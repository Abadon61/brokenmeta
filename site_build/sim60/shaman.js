// Shaman kits. Elemental: Lightning Bolt, Chain Lightning, Lava Burst, Flame Shock and Earth Shock from the client's rank ladders
// (data/spells60.json: top / extra) and the Forever talent tooltips. ASSUMED (Classic style): base mana, mana items; the Searing Totem
// (a few damage per second) and the elemental melee crit from Elemental Devastation are not simulated.
import { makeCaster, fromRank, pickRank, spellHit, tickDamage } from './caster.js';
import { dotActive, dotLeft } from './spells.js';

// ---- fire totems (shared by the Elemental and Enhancement kits) ----
// Searing Totem: its "Attack" spell (47 fire damage + 0.017 spell power every 2.2 s, 55 s) and Magma Totem's pulse (73 + 0.033 spell
// power every 2 s, 20 s, area: one target here) come from the client rank tables. Totem attacks crit like spells; Call of Flame and
// Elemental Fury (Elemental) raise them.
export function fireTotems(data) {
  const out = {}, mk = (key, castName, boltName, interval, dmgName) => {
    const c = pickRank(data, 'shaman', null, castName), bolt = pickRank(data, 'shaman', null, boltName);
    if (!c || !bolt) return;
    const d = bolt.effects.find((e) => e.effect === 2 && e.base > 0), mid = d.base;
    out[key] = { name: castName, dmgName, cost: c.cost ? c.cost.amount : 0, dur: c.duration_ms / 1000, interval, min: mid * (1 - d.variance / 2), max: mid * (1 + d.variance / 2), coeff: d.sp_coeff };
  };
  mk('searing', 'Searing Totem', 'Searing Bolt', 2.2, 'Searing Bolt');
  mk('magma', 'Magma Totem', 'Magma Totem Pulse', 2.0, 'Magma Totem');
  return out;
}
// puts the totem down now: one attack every interval until it expires (a new totem replaces the old one)
export function dropTotem(sim, T, mods) {
  const id = (sim.totemId = (sim.totemId || 0) + 1), end = sim.now + T.dur;
  sim.totemUntil = end;
  const tick = () => {
    if (sim.totemId !== id || sim.now > end + 1e-9) return;
    const m = mods(sim);
    if (spellHit(sim, m)) tickDamage(sim, T.dmgName, T.min + (T.max - T.min) * sim.rng() + ((sim.stats.sp || 0) + (sim.spBonus || 0)) * T.coeff, m);
    else sim.entry(T.dmgName).misses++;
    sim.schedule(T.interval, tick);
  };
  sim.schedule(T.interval, tick);
}

export const SHAMAN = {
  convection: { cost: 0.02 }, concussion: { dmg: 0.01 }, reverberation: { cd: 0.2 }, callOfFlame: { dmg: 0.05 }, elementalFocus: { chance: 0.10 }, elementalAlacrity: { cast: 1 / 6 },
  thunderingStrikes: { crit: 0.01 }, ancestralKnowledge: { int: 0.02 }, callOfThunder: { crit: 0.03 }, lightningOverload: { chance: 0.10 / 3, dmg: 0.5 }, elementalFury: { critBonus: 0.2 }, lavaBurstFs: 1.2,
  improvedFireNova: { dmg: 0.1, cd: 2 }, mentalQuickness: { sp: 0.15 }, manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

export const SHAMAN_ELE_DEFAULT_BUILD = {
  convection: 0, concussion: 0, reverberation: 0, callOfFlame: 0, elementalFocus: 0, elementalAlacrity: 0, callOfThunder: 0, lightningOverload: 0, elementalFury: 0, lavaBurst: 0, thunderingStrikes: 0, ancestralKnowledge: 0,
  improvedFireNova: 0, mentalQuickness: 0, mindfulness: 0, totemicFocus: 0, tidalFocus: 0, useCooldowns: true, usePotion: true, useGem: true, earthShock: false, chainLightning: false, fireTotem: 'searing', fireNova: false,   // Chain Lightning costs 485 mana for one target's worth of damage: off by default
};

export function shamanElementalKit(build = {}, data = null) {
  const b = Object.assign({}, SHAMAN_ELE_DEFAULT_BUILD, build), H = SHAMAN;
  const na = ['nature'], fi = ['fire'];
  const lb = pickRank(data, 'shaman', 'shaman_lightning_bolt', 'Lightning Bolt'), cl = pickRank(data, 'shaman', null, 'Chain Lightning'), lv = pickRank(data, 'shaman', null, 'Lava Burst');
  const fs = pickRank(data, 'shaman', 'shaman_flame_shock', 'Flame Shock'), es = pickRank(data, 'shaman', 'shaman_earth_shock', 'Earth Shock');
  const S = {}, TT = fireTotems(data), T = b.fireTotem && TT[b.fireTotem] ? TT[b.fireTotem] : null;
  const fnCast = pickRank(data, 'shaman', null, 'Fire Nova'), fnDmg = pickRank(data, 'shaman', null, 'Fire Nova Damage');
  if (T) S.totem = { name: T.name, cost: T.cost, cast: 0, cd: 0, totem: true, schools: fi };
  if (fnCast && fnDmg) S.fn = fromRank(fnDmg, { name: 'Fire Nova', schools: fi, cost: fnCast.cost.amount, cast: 0, cd: Math.max(2, fnCast.cooldown_ms / 1000 - H.improvedFireNova.cd * b.improvedFireNova), instant: true, nova: true });
  if (lb) S.lb = fromRank(lb, { name: 'Lightning Bolt', schools: na, bolt: true });
  if (cl) S.cl = fromRank(cl, { name: 'Chain Lightning', schools: na, bolt: true });
  if (lv) S.lvb = fromRank(lv, { name: 'Lava Burst', schools: fi, bolt: true });
  if (fs) S.fs = fromRank(fs, { name: 'Flame Shock', schools: fi, shock: true, instant: true });
  if (es) S.es = fromRank(es, { name: 'Earth Shock', schools: na, shock: true, instant: true });
  const def = {
    name: 'shaman_elemental', build: b, S,
    items: { potion: H.manaPotion, gem: H.manaGem },
    baseMana: (sim) => sim.stats.mana + 15 * Math.floor((sim.stats.int || 0) * H.ancestralKnowledge.int * b.ancestralKnowledge),
    keep: () => b.mindfulness / 6,                          // Mindfulness: 17 / 33 / 50 % of the regeneration continues while casting
    setup(sim) {
      sim.aClear = sim.addAura({ name: 'Clearcasting', duration: Infinity });
      sim.spBonus = Math.floor(((sim.stats.int || 0) * (1 + H.ancestralKnowledge.int * b.ancestralKnowledge)) * H.mentalQuickness.sp * b.mentalQuickness);   // Mental Quickness: spell power from Intellect
      sim.critBase = H.thunderingStrikes.crit * b.thunderingStrikes + Math.floor((sim.stats.int || 0) * H.ancestralKnowledge.int * b.ancestralKnowledge) / 59.5 / 100;
    },
    mods(sim, s, kind) {
      let hit = 0.01 * b.tidalFocus, crit = sim.critBase, dmg = 1, critBonus = H.elementalFury.critBonus * b.elementalFury;
      if (s === S.lb || s === S.cl) { dmg *= 1 + H.concussion.dmg * b.concussion; crit += H.callOfThunder.crit * b.callOfThunder; }
      if (s === S.es) dmg *= 1 + H.concussion.dmg * b.concussion;
      if (s.schools[0] === 'fire' && (s === S.fs || s === S.lvb || s === S.fn)) dmg *= 1 + H.callOfFlame.dmg * b.callOfFlame;
      if (s === S.fn) dmg *= 1 + H.improvedFireNova.dmg * b.improvedFireNova;
      if (s === S.lvb && dotActive(sim, S.fs ? S.fs.name : '')) dmg *= H.lavaBurstFs;
      return { hit, crit, dmg, critBonus };
    },
    castTime: (sim, s) => (s.bolt ? Math.max(0.5, s.cast - H.elementalAlacrity.cast * b.elementalAlacrity) : s.cast),
    cost(sim, s) {
      if (s.totem) return Math.round(s.cost * (1 - 0.05 * b.totemicFocus));
      if (sim.aClear.active) return 0;
      return Math.round(s.cost * (s.bolt || s.shock ? 1 - H.convection.cost * b.convection : 1));
    },
    beforeCast(sim, s) { if (s.totem) return; if (sim.aClear.active) sim.aClear.expire(); if (s.shock) sim.cdAt.shock = sim.now + Math.max(1.5, 6 - H.reverberation.cd * b.reverberation * 5); },
    afterHit(sim, s, outcome) {
      if (s.totem) { dropTotem(sim, T, () => ({ hit: 0, crit: sim.critBase, dmg: 1 + H.callOfFlame.dmg * b.callOfFlame, critBonus: H.elementalFury.critBonus * b.elementalFury })); return; }
      if (outcome === 'miss') return;
      if (b.elementalFocus && !s.dot && sim.rng() < H.elementalFocus.chance) sim.aClear.apply();
      if (b.lightningOverload && (s === S.lb || s === S.cl) && sim.rng() < H.lightningOverload.chance * b.lightningOverload) {
        const e = sim.entry(s.name + ' (Overload)'), m = def.mods(sim, s, 'direct');
        const raw = (s.direct.min + (s.direct.max - s.direct.min) * sim.rng() + sim.stats.sp * s.direct.coeff) * H.lightningOverload.dmg;
        const c = sim.rng() < Math.max(0, Math.min(1, sim.stats.crit + m.crit));
        const d = raw * m.dmg * (1 - sim.target.spellMitigation) * sim.target.spellTaken * (c ? 1 + 0.5 * (1 + m.critBonus) : 1);
        e.casts++; sim.record(s.name + ' (Overload)', d, c ? 'crit' : 'hit');
      }
    },
    choose(sim) {
      const now = sim.now, ready = (s) => now >= (sim.cdAt[s.name] || 0) - 1e-9, rem = sim.fightLen - now;
      const shockReady = now >= (sim.cdAt.shock || 0) - 1e-9;
      if (S.totem && rem > 8 && now >= (sim.totemUntil || 0) - 1.0) return S.totem;
      if (S.fs && shockReady && rem > 6 && dotLeft(sim, S.fs.name) < 1.0) return S.fs;
      if (S.lvb && b.lavaBurst && ready(S.lvb)) return S.lvb;
      if (S.es && b.earthShock && shockReady) return S.es;
      if (S.fn && b.fireNova && ready(S.fn)) return S.fn;
      if (S.cl && b.chainLightning && ready(S.cl)) return S.cl;
      return S.lb;
    },
  };
  return makeCaster(def);
}

// ---------------------------------------------------------------------------------------------------------------------------
// Enhancement: melee (dual wield or two-hand) with Stormstrike, Flurry, Maelstrom Weapon (instant Lightning Bolts) and Windfury Weapon.
// Numbers: Stormstrike and Lightning Bolt from the client's rank ladders, talents from the Forever tooltips. ASSUMED (Classic style):
// Windfury Weapon (20% per main-hand hit, one extra attack with +315 attack power), Rockbiter's +118 attack power kept on, Maelstrom
// Weapon's proc chance (3% per rank per melee hit), Rage of the Farseer's cooldown, melee crit used for the Lightning Bolt crit.
import { yellowAttack } from './shared.js';
import { useRune, setupMana, gainMana, spendMana, spiritRegenPerSec, resolveSpell, applyDot } from './spells.js';

export const SHAMAN_ENH = {
  stormstrike: { cost: 125, cd: 8, nature: 1.2, dur: 12 }, rockbiter: { ap: 118 }, windfury: { chance: 0.20, ap: 333, extra: 2 },
  flurry: { perRank: 0.05, charges: 3, expire: 15 }, maelstrom: { chance: 0.10, perRank: 0.04, max: 5, dur: 30 }, improvedStormstrike: { keep: 0.5, dur: 15 }, convection: { cost: 0.02 }, elementalFocus: { chance: 0.10 }, elementalAlacrity: { cast: 1 / 6 }, farseer: { haste: 1.3, dur: 25, cd: 180 },
  thunderingStrikes: { crit: 0.01 }, ancestralKnowledge: { int: 0.02 }, mentalDexterity: { ap: 1 / 3 }, mentalQuickness: { sp: 0.15 }, elementalWeapons: { rock: 0.2 / 3, wf: 0.4 / 3 },
  shamanisticFocus: { cost: 0.45 }, concussion: { dmg: 0.01 }, callOfFlame: { dmg: 0.05 }, improvedFireNova: { dmg: 0.1, cd: 2 }, manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

export const SHAMAN_ENH_DEFAULT_BUILD = {
  thunderingStrikes: 0, ancestralKnowledge: 0, mentalDexterity: 0, mentalQuickness: 0, elementalWeapons: 0, flurry: 0, stormstrike: 0, maelstromWeapon: 0, rageOfTheFarseer: 0,
  windfuryWeapon: true, rockbiter: true, fireTotem: 'searing', shamanisticFocus: 0, earthShock: true, flameShock: true, fireNova: false, shockSpell: 'earth', ssBuffOn: 'bolt', fsFirst: true, fsRefresh: 3, maelstromMin: 3, improvedStormstrike: 0, convection: 0, elementalFocus: 0, elementalAlacrity: 0, improvedFireNova: 0, elementalDevastation: 0, shockReserve: 300, useCooldowns: true, usePotion: true, useGem: true,
};

export function shamanEnhancementKit(build = {}, data = null) {
  const b = Object.assign({}, SHAMAN_ENH_DEFAULT_BUILD, build), E = JSON.parse(JSON.stringify(SHAMAN_ENH));
  const lb = pickRank(data, 'shaman', 'shaman_lightning_bolt', 'Lightning Bolt'), ss = pickRank(data, 'shaman', null, 'Stormstrike'), rb = pickRank(data, 'shaman', 'shaman_rockbiter_weapon', 'Rockbiter Weapon');
  const L = lb ? fromRank(lb) : null;
  const esr = pickRank(data, 'shaman', 'shaman_earth_shock', 'Earth Shock'), ES = esr ? fromRank(esr, { name: 'Earth Shock', cd: 6 }) : null;
  const frr = pickRank(data, 'shaman', null, 'Frost Shock'), FRS = frr ? fromRank(frr, { name: 'Frost Shock', cd: 6 }) : null;
  const fsr = pickRank(data, 'shaman', 'shaman_flame_shock', 'Flame Shock'), FS = fsr ? fromRank(fsr, { name: 'Flame Shock', cd: 6 }) : null;
  const fnc = pickRank(data, 'shaman', null, 'Fire Nova'), fnd = pickRank(data, 'shaman', null, 'Fire Nova Damage');
  const FN = fnc && fnd ? fromRank(fnd, { name: 'Fire Nova', cost: fnc.cost.amount, cd: fnc.cooldown_ms / 1000 }) : null;
  const TT = fireTotems(data), T = b.fireTotem && TT[b.fireTotem] ? TT[b.fireTotem] : null;
  const wf = pickRank(data, 'shaman', null, 'Windfury Weapon Proc');
  if (wf) { const p = wf.effects.find((e) => e.aura === 99), x = wf.effects.find((e) => e.effect === 19); if (p) E.windfury.ap = p.base; if (x) E.windfury.extra = Math.round(x.base); }
  if (ss) { E.stormstrike.cost = ss.cost.amount; E.stormstrike.cd = ss.cooldown_ms / 1000; }
  return {
    name: 'shaman_enhancement', build: b, E,
    setup(sim) {
      sim.player.resource = 'mana'; sim.kitBuild = b;
      const st = sim.stats, mods = sim.mods, mh = sim.player.weapons[0] || {};
      const extraInt = Math.floor((st.int || 0) * E.ancestralKnowledge.int * b.ancestralKnowledge), int = (st.int || 0) + extraInt;
      mods.apBonus += Math.floor(int * E.mentalDexterity.ap * b.mentalDexterity) + (b.rockbiter ? E.rockbiter.ap * (1 + E.elementalWeapons.rock * b.elementalWeapons) : 0);
      mods.critBonus += E.thunderingStrikes.crit * b.thunderingStrikes;
      sim.spBonus = Math.floor(int * E.mentalQuickness.sp * b.mentalQuickness);
      sim.istUntil = -1;
      setupMana(sim, { manaMax: st.mana + 15 * extraInt, mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int, spi: st.spi }), castingFraction: (s) => (s.now < s.istUntil ? E.improvedStormstrike.keep : 0) });
      sim.cd = { ss: 0, farseer: 0, potion: 0, gem: 0 }; sim.totemUntil = 0; sim.fsUntil = -1;
      sim.aClear = sim.addAura({ name: 'Clearcasting', duration: Infinity });
      // Elemental Devastation: an offensive spell crit (not the totem's bolts nor a damage-over-time tick) gives +3% melee crit per rank for 10 s
      if (b.elementalDevastation) {
        sim.aED = sim.addAura({ name: 'Elemental Devastation', duration: 10, mods: { meleeCritBonus: 0.03 * b.elementalDevastation } });
        sim.spellProcs.push((s, name, kind) => { if (kind === 'crit' && !/Searing|DoT/.test(name)) s.aED.apply(); });
      }
      sim.flurryAura = sim.addAura({ name: 'Flurry', duration: E.flurry.expire, mods: { hasteMult: 1 + E.flurry.perRank * b.flurry } });
      sim.flurryAura.charges = 0;
      sim.aMW = sim.addAura({ name: 'Maelstrom Weapon', duration: E.maelstrom.dur, maxStacks: E.maelstrom.max });
      sim.aSS = sim.addAura({ name: 'Stormstrike', duration: E.stormstrike.dur });
      sim.aFar = sim.addAura({ name: 'Rage of the Farseer', duration: E.farseer.dur, mods: { hasteMult: E.farseer.haste } });
      const consume = (s) => { const a = s.flurryAura; if (a.active && --a.charges <= 0) a.expire(); };
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (isWhite) consume(s);
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (outcome === 'crit' && b.flurry > 0) { s.flurryAura.charges = E.flurry.charges; s.flurryAura.apply(1); }
        if (b.maelstromWeapon && s.rng() < E.maelstrom.chance) s.aMW.apply(1);
        if (b.windfuryWeapon && !s.inWindfury && !isOH && (isWhite || source === 'Stormstrike') && s.rng() < E.windfury.chance) {
          const bonus = E.windfury.ap * (1 + E.elementalWeapons.wf * b.elementalWeapons);
          s.entry('Windfury').casts++;
          s.inWindfury = true; s.mods.apBonus += bonus; s.whiteLabel = 'Windfury'; for (let i = 0; i < E.windfury.extra; i++) s.whiteAttack(s.swings[0]); s.whiteLabel = null; s.mods.apBonus -= bonus; s.inWindfury = false;
        }
      });
    },
    rotate(sim) {
      const now = sim.now, rem = sim.fightLen - now;
      if (b.usePotion && now >= sim.cd.potion && sim.mana <= sim.manaMax - 1800 && rem > 20) { sim.cd.potion = now + E.manaPotion.cd; sim.entry('Mana Potion').casts++; gainMana(sim, E.manaPotion.min + (E.manaPotion.max - E.manaPotion.min) * sim.rng()); }
      if (b.useGem && now >= sim.cd.gem && sim.mana <= sim.manaMax - 1100 && rem > 15) { sim.cd.gem = now + E.manaGem.cd; sim.entry('Mana Gem').casts++; gainMana(sim, E.manaGem.min + (E.manaGem.max - E.manaGem.min) * sim.rng()); }
      useRune(sim, b);
      if (b.useCooldowns && b.rageOfTheFarseer && now >= sim.cd.farseer) { sim.cd.farseer = now + E.farseer.cd; sim.entry('Rage of the Farseer').casts++; sim.aFar.apply(); }
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      // fire totem (Searing): one global cooldown every 55 s
      if (T && rem > 8 && now >= sim.totemUntil - 1.0 && sim.mana >= T.cost) {
        spendMana(sim, T.cost); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry(T.name).casts++;
        dropTotem(sim, T, (x) => ({ hit: 0, crit: x.mods.critBonus, dmg: 1 + E.callOfFlame.dmg * (b.callOfFlame || 0), critBonus: 0 }));
        return 1.5;
      }
      const spPow = (sim.stats.sp || 0) + sim.spBonus, focus = 1 - E.shamanisticFocus.cost * b.shamanisticFocus, conv = 1 - E.convection.cost * b.convection;
      const cof = 1 + E.callOfFlame.dmg * (b.callOfFlame || 0), conc = 1 + E.concussion.dmg * (b.concussion || 0);
      // mana cost of a damage spell: Clearcasting makes it free, Convection and Shamanistic Focus lower it
      const price = (base, k) => (sim.aClear.active ? 0 : Math.round(base * k));
      // after a Fire/Frost/Nature damage spell: the Clearcasting that paid for it is gone, Elemental Focus may give a new one
      const afterSpell = (paid) => { if (paid === 0 && sim.aClear.active) sim.aClear.expire(); if (b.elementalFocus && sim.rng() < E.elementalFocus.chance) sim.aClear.apply(); };
      // The shock slot (Earth Shock, Frost Shock or Flame Shock share one cooldown). Flame Shock goes up whenever its damage over time is about to end
      // (while Earth Shock still wanted the Stormstrike bonus, it was skipped during that window)
      const fsNeeded = () => b.flameShock && FS && sim.fsUntil - now < b.fsRefresh && rem > 8 && (b.ssBuffOn === 'bolt' || !sim.aSS.active);
      const castShock = () => {
        if (!(b.earthShock && ES && now >= (sim.cd.shock || 0) && rem > 4)) return null;
        const wantFS = fsNeeded();
        const sp0 = wantFS ? FS : (b.shockSpell === 'frost' && FRS ? FRS : ES), cost = price(sp0.cost, focus * conv);
        if (sim.mana < cost + (cost ? b.shockReserve : 0)) return null;
        sim.cd.shock = now + Math.max(1.5, sp0.cd - 0.2 * (b.reverberation || 0)); spendMana(sim, cost); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry(sp0.name).casts++;
        if (wantFS) {
          const raw = FS.direct.min + (FS.direct.max - FS.direct.min) * sim.rng() + spPow * FS.direct.coeff;
          const r = resolveSpell(sim, 'Flame Shock', raw, { hit: 0, crit: sim.mods.critBonus, dmg: cof, critBonus: 0 });
          if (r.outcome !== 'miss' && FS.dot) { sim.fsUntil = now + FS.dot.ticks * FS.dot.interval; applyDot(sim, 'Flame Shock (DoT)', FS.dot.ticks * (FS.dot.perTick + spPow * FS.dot.coeff) * cof * (1 - sim.target.spellMitigation) * sim.target.spellTaken, FS.dot.ticks, FS.dot.interval); }
        } else if (sp0 === FRS) {                                   // frost: neither Stormstrike nor Concussion apply
          const raw = FRS.direct.min + (FRS.direct.max - FRS.direct.min) * sim.rng() + spPow * FRS.direct.coeff;
          resolveSpell(sim, 'Frost Shock', raw, { hit: 0, crit: sim.mods.critBonus, dmg: 1, critBonus: 0 });
        } else {
          const ssBonus = sim.aSS.active ? E.stormstrike.nature : 1; if (sim.aSS.active) sim.aSS.expire();
          const raw = ES.direct.min + (ES.direct.max - ES.direct.min) * sim.rng() + spPow * ES.direct.coeff;
          resolveSpell(sim, 'Earth Shock', raw, { hit: 0, crit: sim.mods.critBonus, dmg: ssBonus * conc, critBonus: 0 });
        }
        afterSpell(cost);
        return 1.5;
      };
      // opening: Flame Shock right after the totem, so the shock cooldown is already running when Stormstrike and its Lightning Bolt come
      if (b.fsFirst && fsNeeded()) { const w = castShock(); if (w) return w; }
      // Stormstrike: its +20% nature damage goes to the next Lightning Bolt (or Earth Shock), and Improved Stormstrike keeps half of the mana regeneration while casting
      if (b.stormstrike && now >= sim.cd.ss && sim.mana >= E.stormstrike.cost && sim.player.weapons.length) {
        sim.cd.ss = now + E.stormstrike.cd; spendMana(sim, E.stormstrike.cost); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry('Stormstrike').casts++;
        const norm = sim.player.dualWield ? 2.4 : 3.3, mh = sim.player.weapons[0], oh = sim.player.weapons[1];
        yellowAttack(sim, 'Stormstrike', () => sim.weaponRoll(mh) + sim.ap() / 14 * norm);
        if (oh) yellowAttack(sim, 'Stormstrike (off-hand)', () => (sim.weaponRoll(oh) + sim.ap() / 14 * norm) * 0.5);
        sim.aSS.apply();
        if (b.improvedStormstrike && sim.rng() < 0.5 * b.improvedStormstrike) sim.istUntil = now + E.improvedStormstrike.dur;
        return 1.5;
      }
      const boltFirst = b.ssBuffOn === 'bolt' && L && sim.aSS.active && price(L.cost, conv) <= sim.mana;     // the Stormstrike bonus goes to a Lightning Bolt
      if (!boltFirst) { const w = castShock(); if (w) return w; }
      // Fire Nova on its own cooldown (Improved Fire Nova shortens it)
      if (b.fireNova && FN && now >= (sim.cd.fn || 0) && rem > 4) {
        const cost = price(FN.cost, 1), cd = Math.max(2, FN.cd - E.improvedFireNova.cd * (b.improvedFireNova || 0));
        if (sim.mana >= cost + (cost ? b.shockReserve : 0)) {
          sim.cd.fn = now + cd; spendMana(sim, cost); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry('Fire Nova').casts++;
          const raw = FN.direct.min + (FN.direct.max - FN.direct.min) * sim.rng() + spPow * FN.direct.coeff;
          resolveSpell(sim, 'Fire Nova', raw, { hit: 0, crit: sim.mods.critBonus, dmg: cof * (1 + E.improvedFireNova.dmg * (b.improvedFireNova || 0)), critBonus: 0 });
          afterSpell(cost);
          return 1.5;
        }
      }
      // Lightning Bolt from Maelstrom Weapon stacks, squeezed in between the cooldowns. Each stack takes 4% per talent rank off its cast time and mana cost
      // (five ranks and five stacks: instant and free). `maelstromMin` is the fewest stacks worth spending. The swings go on while it is cast.
      const mwStacks = b.maelstromWeapon && sim.aMW.active ? sim.aMW.stacks : 0;
      if (L && (mwStacks >= b.maelstromMin || (b.ssBuffOn === 'bolt' && sim.aSS.active))) {
        const red = Math.min(1, E.maelstrom.perRank * b.maelstromWeapon * mwStacks);
        const lbCost = price(L.cost, (1 - red) * conv), castT = Math.max(1.5, (L.cast - E.elementalAlacrity.cast * (b.elementalAlacrity || 0)) * (1 - red));
        if (lbCost <= sim.mana) {
          if (mwStacks) sim.aMW.expire(); spendMana(sim, lbCost); sim.lastCastAt = now; sim.gcdReadyAt = now + castT; sim.entry('Lightning Bolt').casts++;
          const ssBonus = sim.aSS.active ? E.stormstrike.nature : 1; if (sim.aSS.active) sim.aSS.expire();
          const raw = L.direct.min + (L.direct.max - L.direct.min) * sim.rng() + spPow * L.direct.coeff;
          resolveSpell(sim, 'Lightning Bolt', raw, { hit: 0, crit: sim.mods.critBonus, dmg: ssBonus * conc, critBonus: 0 });
          afterSpell(lbCost);
          return castT;
        }
      }
      const next = Math.min(b.stormstrike ? sim.cd.ss : Infinity, b.rageOfTheFarseer ? sim.cd.farseer : Infinity);
      return Math.max(0.1, Math.min(0.5, next - now));
    },
  };
}
