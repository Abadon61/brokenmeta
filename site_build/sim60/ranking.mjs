// node ranking.mjs [fightLen] [finalIterations]
// Builds data/wow_ranking60.json, the public DPS ranking of the hub page: every simulated specialization with the same rules:
// raid buffs of its family, the best gear the optimizer finds in the known beta item pool (dungeons + the few raid items), a standard
// race, item effects on, a single target for `fightLen` seconds. Tanks are listed apart with their threat per second.
import { readFileSync, writeFileSync } from 'node:fs';
import { ItemPool, toWeapon } from './items.js';
import { optimizeGear } from './optimizer.js';
import { runBatch } from './run.js';
import { Sim } from './engine.js';
import { buildCharacter } from './character.js';
import { makeKit, KITS } from './kits.js';
import { ranksToBuild, ranksFromNames, PRESETS } from './talents.js';
import { PRESET_RAID, PRESET_CASTER, PRESET_HUNTER, CONSUMABLES, BUFFS, DEBUFFS } from './presets.js';

const FIGHT = +process.argv[2] || 180, FINAL = +process.argv[3] || 6000;
const here = new URL('.', import.meta.url);
const rd = (f) => JSON.parse(readFileSync(new URL('data/' + f, here)));
const pool = new ItemPool(rd('items.json'), rd('proficiency.json'));
const data = rd('spells60.json'), fx = rd('effects.json'), tal = rd('talents.json');

// spec -> { class, variant, mode, family, race, role }  (mode follows the page: dw / 2h / caster / ranged / stick / tank)
const SPECS = {
  warrior_fury: { cls: 'warrior', mode: 'dw' }, warrior_arms: { cls: 'warrior', mode: '2h' },
  rogue_combat: { cls: 'rogue', mode: 'dw' }, rogue_assassination: { cls: 'rogue', mode: 'dw' }, rogue_subtlety: { cls: 'rogue', mode: 'dw' },
  mage_fire: { cls: 'mage', mode: 'caster', family: 'caster' }, mage_frost: { cls: 'mage', mode: 'caster', family: 'caster' }, mage_arcane: { cls: 'mage', mode: 'caster', family: 'caster' },
  warlock_affliction: { cls: 'warlock', mode: 'caster', family: 'caster' }, warlock_destruction: { cls: 'warlock', mode: 'caster', family: 'caster' }, warlock_demonology: { cls: 'warlock', mode: 'caster', family: 'caster' },
  hunter_marksmanship: { cls: 'hunter', mode: 'ranged', family: 'hunter', build: { pet: 'none' } }, hunter_beastmastery: { cls: 'hunter', mode: 'ranged', family: 'hunter' },
  hunter_survival: { cls: 'hunter', mode: 'ranged', family: 'hunter' }, hunter_melee: { cls: 'hunter', variant: 'melee', mode: 'dw' },
  priest_shadow: { cls: 'priest', mode: 'caster', family: 'caster' }, shaman_elemental: { cls: 'shaman', mode: 'caster', family: 'caster', race: 'orc' },
  shaman_enhancement: { cls: 'shaman', variant: 'enhancement', mode: '2h', race: 'orc' }, druid_balance: { cls: 'druid', mode: 'caster', family: 'caster' },
  druid_feral: { cls: 'druid', variant: 'feral', mode: 'stick' }, paladin_retribution: { cls: 'paladin', mode: '2h' },
  warrior_protection: { cls: 'warrior', variant: 'protection', mode: 'tank', tank: true }, paladin_protection: { cls: 'paladin', variant: 'protection', mode: 'tank', tank: true },
  druid_bear: { cls: 'druid', variant: 'bear', mode: 'stick', tank: true },
};
const FAMILY = { caster: PRESET_CASTER, hunter: PRESET_HUNTER };

const out = { generated: new Date().toISOString().slice(0, 10), fightLen: FIGHT, iterations: FINAL, build: rd('items.json').build, specs: [] };
const objectiveTank = (r, ch) => { const len = FIGHT, thr = r.counters.threat / len, dt = r.counters.dmgTaken / len, raw = ch.target.boss.dmg / ch.target.boss.speed; return Math.sqrt(Math.max(0, thr) * Math.max(0, raw - dt)); };

const stat = (d) => { const o = {}; for (const k of ['str', 'agi', 'sta', 'int', 'spi', 'ap', 'sp', 'crit', 'spCrit', 'mp5', 'statMult', 'armor', 'spellTaken']) if (d[k]) o[k] = d[k]; if (d.meleeOnly) o.meleeOnly = true; return o; };
// procs shown on a spec's page: talent / effect procs with the number of times they fire per minute. kind 'aura' = applications of the aura, 'entry' = hits + misses of the damage entry (div: attacks per proc)
const PROCS = {
  warrior_fury: [['Flurry', 'aura']],
  rogue_combat: [['Instant Poison', 'entry'], ['Deadly Poison', 'entry']], rogue_assassination: [['Instant Poison', 'entry'], ['Deadly Poison', 'entry']], rogue_subtlety: [['Instant Poison', 'entry'], ['Deadly Poison', 'entry']],
  mage_fire: [['Heating Up', 'aura'], ['Combustion', 'aura']], mage_frost: [['Fingers of Frost', 'aura'], ['Clearcasting', 'aura']], mage_arcane: [['Clearcasting', 'aura']],
  warlock_affliction: [['Shadow Trance', 'aura']], warlock_destruction: [['Shadow and Flame', 'aura']],
  shaman_elemental: [['Lightning Bolt (Overload)', 'entry'], ['Clearcasting', 'aura']],
  shaman_enhancement: [['Windfury', 'entry', 2], ['Maelstrom Weapon', 'aura'], ['Elemental Devastation', 'aura'], ['Flurry', 'aura'], ['Clearcasting', 'aura']],
  druid_balance: [["Nature's Grace", 'aura'], ['Eclipse', 'aura']],
  paladin_retribution: [['Seal of Command', 'entry'], ['Vengeance', 'aura'], ['Vindication', 'aura']],
  hunter_beastmastery: [['Frenzy', 'aura']],
};
// stat curves: DPS as a function of one stat (a probe item adds it on top of the final gear). range = the largest amount tried, in the probe's own unit
const CURVE_RANGE = { hitrtng: 180, critstrkrtng: 280, hastertng: 200, atkpwr: 400, splpwr: 300, int: 150, spi: 150, str: 120, agi: 120 };
const RATING_PCT = { hitrtng: 10, critstrkrtng: 14, hastertng: 10 };
// specs whose page also shows the build with a spell the ranking build does not take (the ranking keeps the one with more DPS)
const ALTS = {
  warrior_arms: { spell: 'Mortal Strike', names: { 'Improved Execute': 0, 'Mortal Strike': 1 } },
  hunter_marksmanship: { spell: 'Sniper Shot', names: { 'Focused Fire': 0, 'Sniper Shot': 1 } },
  warlock_demonology: { spell: 'Conflagrate', names: { 'Ruin': 0, 'Conflagrate': 1 } },
};
// RANK_ONLY=spec_a,spec_b recomputes only those specs and keeps the other rows of the existing file
const ONLY = process.env.RANK_ONLY ? process.env.RANK_ONLY.split(',') : null;
for (const [id, S] of Object.entries(SPECS)) {
  if (ONLY && !ONLY.includes(id)) continue;
  const t0 = Date.now();
  const family = FAMILY[S.family] || PRESET_RAID;
  const build = Object.assign(ranksToBuild(S.cls, tal[S.cls], ranksFromNames(tal[S.cls], PRESETS[id])), S.build || {});
  const kit = () => makeKit(id, build, data);
  const character = { class: S.cls, variant: S.variant, race: S.race || 'human', gear: [], weapons: [], buffs: family.buffs, consumables: family.consumables, debuffs: family.debuffs, effects: fx };
  // a spec can be played with several weapon setups (Enhancement: dual wield or two-hand): the ranking keeps the best one, as a player would
  const tryMode = async (mode) => {
    const done = await optimizeGear({
      pool, character, kit, fightLen: FIGHT, iterations: 500, prefilter: 4, maxPasses: 2, weaponMode: mode,
      caster: mode === 'caster', ranged: mode === 'ranged', stick: mode === 'stick', tank: !!S.tank, objective: S.tank ? objectiveTank : undefined,
    });
    // rebuild the final character the way the page applies an optimizer result
    const gear = done.gear.slice(), weapons = [];
    for (const w of done.weapons) {
      const it = pool.byId.get(w.id);
      if (w.slot === 'rng') weapons.push(toWeapon(it, false));
      else if (w.slot === 'th' && (mode === 'caster' || mode === 'ranged' || mode === 'stick')) gear.push({ slot: 'th', id: it.id, name: it.name, st: it.st });
      else weapons.push(toWeapon(it, w.slot === 'oh'));
    }
    const ch = buildCharacter({ ...character, gear, weapons });
    const r = runBatch({ fightLen: FIGHT, player: ch.player, target: ch.target, kitFactory: kit }, FINAL, 7);
    return { done, gear, weapons, ch, r, mode };
  };
  let best = null;
  for (const m of S.modes || [S.mode]) { const x = await tryMode(m); if (!best || x.r.mean > best.r.mean) best = x; }
  const { done, gear, weapons, ch, r } = best;
  // ---- stat weights at level 60 (DPS specs): DPS gained by one more point of each stat on the final character, same random draws on both sides ----
  let weights = null;
  if (!S.tank) {
    const caster = S.mode === 'caster', main = caster ? 'splpwr' : 'atkpwr';
    const probes = [[main, caster ? 30 : 40, 'pt'], ['str', 20, 'pt'], ['agi', 20, 'pt'], ['int', 20, 'pt'], ['spi', 20, 'pt'], ['critstrkrtng', 14, 'pct'], ['hitrtng', 10, 'pct'], ['hastertng', 10, 'pct']];
    const runOf = (c) => runBatch({ fightLen: FIGHT, player: c.player, target: c.target, kitFactory: kit }, 3000, 3).mean;
    const baseMean = runOf(ch);
    const list = [];
    for (const [key, amount, unit] of probes) {
      const c2 = buildCharacter({ ...character, gear: gear.concat([{ slot: 'trinket3', id: -1, name: 'probe', st: { [key]: amount } }]), weapons });
      const per = (runOf(c2) - baseMean) / (unit === 'pct' ? 1 : amount);
      list.push({ stat: key, per: +per.toFixed(3), unit });
    }
    const ref = list.find((x) => x.stat === main).per || 1;
    weights = list.map((x) => ({ ...x, rel: +(x.per / ref).toFixed(2) })).sort((a, b) => b.per - a.per);
  }
  // ---- stat curves (DPS specs): where more of a stat stops paying ----
  let curves = [];
  if (!S.tank && weights) {
    const sm0 = ch.summary || {}, baseOf = { hitrtng: (sm0.hit || 0) * 100, critstrkrtng: (sm0.crit || 0) * 100, hastertng: 0 };
    const picks = weights.filter((w) => CURVE_RANGE[w.stat] && w.per > 0 && w.rel >= 0.05).slice(0, 4);
    for (const w of picks) {
      const key = w.stat, steps = 8, pts = [];
      for (let i = 0; i <= steps; i++) {
        const add = Math.round((CURVE_RANGE[key] * i) / steps), c2 = buildCharacter({ ...character, gear: add ? gear.concat([{ slot: 'trinket3', id: -1, name: 'probe', st: { [key]: add } }]) : gear, weapons });
        pts.push([add, +runBatch({ fightLen: FIGHT, player: c2.player, target: c2.target, kitFactory: kit }, 1200, 3).mean.toFixed(2)]);
      }
      const rp = RATING_PCT[key], x = (a) => +(rp ? baseOf[key] + a / rp : a).toFixed(2);
      // cap: the first step after which each further step gives less than a fifth of the first step's gain (and keeps giving little)
      const sl = pts.slice(1).map((p, i) => p[1] - pts[i][1]), s0 = Math.max(sl[0], sl[1] || 0);
      let cap = null;
      if (s0 > 0.4) for (let i = 1; i < sl.length; i++) if (sl[i] < 0.2 * s0 && sl.slice(i).every((v) => v < 0.35 * s0)) { cap = x(pts[i][0]); break; }
      curves.push({ stat: key, unit: rp ? 'pct' : 'pt', base: rp ? +baseOf[key].toFixed(2) : 0, points: pts.map((p) => [x(p[0]), p[1]]), cap });
    }
  }
  // ---- procs per minute ----
  const procs = [];
  for (const [pn, kind, div] of PROCS[id] || []) {
    const e = r.breakdown[pn], n = kind === 'aura' ? (r.applications || {})[pn] : e ? (e.hits + e.misses) / (div || 1) : 0;
    if (n > 0.2) procs.push({ name: pn, perMin: +(n / (FIGHT / 60)).toFixed(1) });
  }
  // ---- consumables: what each one is worth to this spec. Those of the simulated set are removed one by one (loss), the others are added one by one (gain) ----
  const metric = (c, rr) => (S.tank ? objectiveTank(rr, c) : rr.mean);
  const withCons = (list) => { const c = buildCharacter({ ...character, consumables: list, gear, weapons }); return metric(c, runBatch({ fightLen: FIGHT, player: c.player, target: c.target, kitFactory: kit }, 2500, 3)); };
  const baseCons = withCons(family.consumables), consumables = [];
  for (const [cid, cdef] of Object.entries(CONSUMABLES)) {
    if (cdef.weaponDmg) continue;
    const inSet = family.consumables.includes(cid);
    const v = withCons(inSet ? family.consumables.filter((x) => x !== cid) : family.consumables.concat([cid]));
    consumables.push({ id: cid, name: cdef.name, inSet, gain: +((inSet ? baseCons - v : v - baseCons)).toFixed(2), pct: +(100 * (inSet ? baseCons - v : v - baseCons) / baseCons).toFixed(2) });
  }
  consumables.sort((a, b) => b.gain - a.gain);
  // ---- value of each chosen talent: what the spec loses when it is taken out (null = the simulator has no effect for it: a gate / utility point) ----
  const talentValues = {};
  {
    const base1 = metric(ch, runBatch({ fightLen: FIGHT, player: ch.player, target: ch.target, kitFactory: kit }, 1500, 3));
    for (const tn of Object.keys(PRESETS[id])) {
      const names2 = { ...PRESETS[id] }; delete names2[tn];
      const b2 = Object.assign(ranksToBuild(S.cls, tal[S.cls], ranksFromNames(tal[S.cls], names2)), S.build || {});
      if (JSON.stringify(b2) === JSON.stringify(build)) { talentValues[tn] = null; continue; }
      const rr = runBatch({ fightLen: FIGHT, player: ch.player, target: ch.target, kitFactory: () => makeKit(id, b2, data) }, 1500, 3);
      talentValues[tn] = { gain: +(base1 - metric(ch, rr)).toFixed(2), pct: +(100 * (base1 - metric(ch, rr)) / base1).toFixed(2) };
    }
  }
  // ---- data of the spec's detail page: talents, gear, stats, damage by ability, the opening ----
  const talents = [];
  for (const [tn, rk] of Object.entries(PRESETS[id])) {
    for (const sp of tal[S.cls].specs) {
      const t = sp.talents.find((x) => x.name.en === tn);
      if (!t) continue;
      const pick = (arr) => arr[Math.min(rk, arr.length) - 1];
      talents.push({ tree: sp.id, tree_name: sp.name, name: t.name, rank: rk, max: t.max_rank, row: t.row, desc: { en: pick(t.desc.en), fr: pick(t.desc.fr || t.desc.en) } });
      break;
    }
  }
  const trees = {};
  for (const t of talents) trees[t.tree] = (trees[t.tree] || 0) + t.rank;
  const weaponSlot = (w) => (w.offHand ? 'oh' : w.twoHand ? 'th' : /bow|gun|crossbow/.test(w.type) ? 'rng' : 'mh');
  const items = gear.map((g) => ({ slot: g.slot, id: g.id })).concat(weapons.map((w) => ({ slot: weaponSlot(w), id: w.itemId })));
  for (const it of items) { const p = pool.byId.get(it.id) || {}; it.name = p.name; it.zone = p.zone; it.src = (p.src || [])[0]; it.ilvl = p.ilvl; it.q = p.q; }
  const sim = new Sim({ fightLen: FIGHT, player: ch.player, target: ch.target, spec: kit(), seed: 11, log: true });
  sim.run();
  const opening = [];
  for (const [t, n, , tick] of sim.log) {
    if (tick) continue;                                   // damage-over-time ticks are not casts
    if (t > 14 || /^White|Pet|Imp Firebolt|Searing Bolt|Deep Wounds|Ignite|Ignition|\(bleed\)|\(DoT\)|Windfury|Overload|Poison|Mana|Smokey|Ephemeral|Hawk/.test(n)) continue;
    const last = opening[opening.length - 1];
    if (last && last.n === n && t - last.t < 0.4) { last.x++; continue; }
    if (opening.length < 14 && !opening.some((o) => o.n === n && t - o.t < 0.2)) opening.push({ t, n, x: 1 });
  }
  // ---- the alternative build (with the spell), on the same gear ----
  let alt = null;
  if (ALTS[id]) {
    const names = { ...PRESETS[id] };
    for (const [k, v] of Object.entries(ALTS[id].names)) { if (v) names[k] = v; else delete names[k]; }
    const bAlt = Object.assign(ranksToBuild(S.cls, tal[S.cls], ranksFromNames(tal[S.cls], names)), S.build || {});
    const kitAlt = () => makeKit(id, bAlt, data);
    const rA = runBatch({ fightLen: FIGHT, player: ch.player, target: ch.target, kitFactory: kitAlt }, FINAL, 7);
    const tA = [];
    for (const [tn, rk] of Object.entries(names)) {
      for (const sp of tal[S.cls].specs) {
        const t = sp.talents.find((x) => x.name.en === tn);
        if (!t) continue;
        const pick = (arr) => arr[Math.min(rk, arr.length) - 1];
        tA.push({ tree: sp.id, tree_name: sp.name, name: t.name, rank: rk, max: t.max_rank, row: t.row, desc: { en: pick(t.desc.en), fr: pick(t.desc.fr || t.desc.en) } });
        break;
      }
    }
    const trA = {}; for (const t of tA) trA[t.tree] = (trA[t.tree] || 0) + t.rank;
    const tvA = {}, baseA = metric(ch, runBatch({ fightLen: FIGHT, player: ch.player, target: ch.target, kitFactory: kitAlt }, 1500, 3));
    for (const tn of Object.keys(names)) {
      const n2 = { ...names }; delete n2[tn];
      const b2 = Object.assign(ranksToBuild(S.cls, tal[S.cls], ranksFromNames(tal[S.cls], n2)), S.build || {});
      if (JSON.stringify(b2) === JSON.stringify(bAlt)) { tvA[tn] = null; continue; }
      const rr = runBatch({ fightLen: FIGHT, player: ch.player, target: ch.target, kitFactory: () => makeKit(id, b2, data) }, 1500, 3);
      tvA[tn] = { gain: +(baseA - metric(ch, rr)).toFixed(2), pct: +(100 * (baseA - metric(ch, rr)) / baseA).toFixed(2) };
    }
    const simA = new Sim({ fightLen: FIGHT, player: ch.player, target: ch.target, spec: kitAlt(), seed: 11, log: true });
    simA.run();
    const opA = [];
    for (const [t, n, , tick] of simA.log) {
      if (tick) continue;
      if (t > 14 || /^White|Pet|Imp Firebolt|Searing Bolt|Deep Wounds|Ignite|Ignition|(bleed)|(DoT)|Windfury|Overload|Poison|Mana|Smokey|Ephemeral|Hawk/.test(n)) continue;
      const last = opA[opA.length - 1];
      if (last && last.n === n && t - last.t < 0.4) { last.x++; continue; }
      if (opA.length < 14 && !opA.some((o) => o.n === n && t - o.t < 0.2)) opA.push({ t, n, x: 1 });
    }
    alt = { spell: ALTS[id].spell, dps: +rA.mean.toFixed(1), sem: +rA.sem.toFixed(2), talents: tA, trees: trA, talentValues: tvA, opening: opA,
      abilities: Object.entries(rA.breakdown).filter(([, v]) => (v.dps || 0) > 0.05).sort((a, b) => b[1].dps - a[1].dps).map(([n, v]) => ({ name: n, dps: +v.dps.toFixed(1), casts: +(v.casts || 0).toFixed(1), hits: +v.hits.toFixed(1), crit: v.hits ? +(v.crits / v.hits).toFixed(3) : 0 })) };
  }
  const sm = ch.summary || {};
  const detail = {
    talents, trees, items, weights, consumables, curves, procs, talentValues, alt,
    // what the raid gives during the simulation (ids and values come from presets.js; the page translates the names)
    setup: { buffs: family.buffs.map((x) => ({ id: x, name: BUFFS[x].name, ...stat(BUFFS[x]) })), consumables: family.consumables.map((x) => ({ id: x, name: CONSUMABLES[x].name, ...stat(CONSUMABLES[x]) })), debuffs: family.debuffs.map((x) => ({ id: x, name: DEBUFFS[x].name, ...stat(DEBUFFS[x]) })) },
    stats: { prim: sm.prim, ap: sm.ap, sp: sm.sp, crit: sm.crit, hit: sm.hit, haste: sm.haste, mana: sm.mana, armor: sm.armor, tank: sm.tank },
    effects: (sm.effects || []).map((e) => (e && (e.name || e.id)) || String(e)).slice(0, 12),
    uptimes: Object.entries(r.uptimes || {}).filter(([n, v]) => v > 0.05 && v < 0.999 && !/Ephemeral|Smokey/.test(n)).map(([n, v]) => [n, +v.toFixed(2)]),
    abilities: Object.entries(r.breakdown).filter(([, v]) => (v.dps || 0) > 0.05).sort((a, b) => b[1].dps - a[1].dps)
      .map(([n, v]) => ({ name: n, dps: +v.dps.toFixed(1), casts: +(v.casts || 0).toFixed(1), hits: +v.hits.toFixed(1), crit: v.hits ? +(v.crits / v.hits).toFixed(3) : 0 })),
    opening,
  };
  const row = { spec: id, class: S.cls, role: S.tank ? 'tank' : 'dps', dps: +r.mean.toFixed(1), sem: +r.sem.toFixed(2), name: KITS[id] };
  if (S.tank) { row.tps = +(r.counters.threat / FIGHT).toFixed(1); row.dtps = +(r.counters.dmgTaken / FIGHT).toFixed(1); row.health = Math.round(ch.summary.tank.health); }
  row.spells = Object.entries(r.breakdown).filter(([, v]) => (v.dps || 0) > 0).sort((x, y) => y[1].dps - x[1].dps).map(([n, v]) => [n, +v.dps.toFixed(1), +(v.casts || 0).toFixed(1)]);
  row.detail = detail;
  out.specs.push(row);
  console.log(id.padEnd(22), S.tank ? 'TPS ' + row.tps : 'DPS ' + row.dps, '±' + row.sem, ((Date.now() - t0) / 1000).toFixed(0) + 's');
}
if (ONLY) {                                         // merge the recomputed rows into the existing file, in its order
  const prev = JSON.parse(readFileSync(new URL('../../data/wow_ranking60.json', here)));
  const fresh = new Map(out.specs.map((r) => [r.spec, r]));
  out.specs = prev.specs.map((r) => fresh.get(r.spec) || r);
  out.generated = prev.generated; out.iterations = prev.iterations;
}
writeFileSync(new URL(process.env.RANK_OUT || '../../data/wow_ranking60.json', here), JSON.stringify(out, null, 1));
console.log('written', out.specs.length, 'specs');
