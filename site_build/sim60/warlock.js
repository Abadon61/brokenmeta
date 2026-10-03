// Warlock kit (Affliction / Destruction / Demonology-with-sacrifice share one priority list; the specs differ by
// talents). Numbers are WoW: Forever's own where the client tables have them (Corruption, Immolate, Shadow Bolt,
// Conflagrate, Incinerate, Soul Fire, Wrack, Siphon Life, Bane of Doom) and the talent tooltips; ASSUMED = Classic
// 1.12 value kept until Forever's table is sourced: Bane of Agony, Shadowburn, Life Tap, the Imp's Firebolt, Demonic Rune
// style mana items, spell hit/crit/mana formulas (character.js), Soul Shards (not limited: shards are assumed available).
// Periodic effects use the client's per-tick spell coefficient (sp_coeff x number of ticks) and can crit (can_crit).
import { setupMana, gainMana, spendMana, spiritRegenPerSec, beginCast, resolveSpell, applyDotCrit, dotActive, dotLeft, cancelDot, SPELL_GCD, SPELL_CRIT_MULT } from './spells.js';

export const WARLOCK = {
  shadowBolt: { name: 'Shadow Bolt', schools: ['shadow'], destruction: true, cast: 3, cost: 380, min: 253.3, max: 282.7, coeff: 0.857 },
  incinerate: { name: 'Incinerate', schools: ['fire'], destruction: true, cast: 2.5, cost: 325, min: 190, max: 245, coeff: 0.714, immolateBonus: 1.25 },
  immolate: { name: 'Immolate', schools: ['fire'], destruction: true, cast: 2, cost: 380, flat: 158, coeff: 0.2, dot: { total: 275, ticks: 5, interval: 3, coeff: 0.13 } },
  conflagrate: { name: 'Conflagrate', schools: ['fire'], destruction: true, cast: 0, cost: 255, min: 220, max: 344, coeff: 0.429, cd: 10 },
  soulFire: { name: 'Soul Fire', schools: ['fire'], destruction: true, cast: 6, cost: 335, min: 334, max: 528, coeff: 1, cd: 60 },
  shadowburn: { name: 'Shadowburn', schools: ['shadow'], destruction: true, cast: 0, cost: 365, min: 450, max: 502, coeff: 0.429, cd: 15 },   // ASSUMED (Classic)
  corruption: { name: 'Corruption', schools: ['shadow'], cast: 2, cost: 340, dot: { total: 438, ticks: 6, interval: 3, coeff: 0.2 } },
  agony: { name: 'Bane of Agony', schools: ['shadow'], cast: 0, cost: 265, dot: { total: 1044, ticks: 12, interval: 2, coeff: 0.1 } },        // ASSUMED (Classic rank 6, coeff 1.2 over 12 ticks)
  doom: { name: 'Bane of Doom', schools: ['shadow'], cast: 0, cost: 300, cd: 60, dot: { total: 1742, ticks: 1, interval: 60, coeff: 4 } },
  siphonLife: { name: 'Siphon Life', schools: ['shadow'], cast: 0, cost: 365, dot: { total: 410, ticks: 10, interval: 3, coeff: 0.05 } },
  wrack: { name: 'Wrack', schools: ['shadow'], cast: 0, cost: 200, dot: { total: 216, ticks: 6, interval: 1, coeff: 0.143 }, vuln: 0.10, dur: 6 },
  lifeTap: { restore: 424 },                                                                                  // ASSUMED (Classic rank 6), health is assumed to be healed back
  manaPotion: { cd: 120, min: 1350, max: 2250 },                                                              // ASSUMED (Major Mana Potion)
  manaGem: { cd: 120, min: 1073, max: 1127 },
  imp: { cast: 2, min: 105, max: 115, spCoeff: 0.15, crit: 0.05, miss: 0.06 },                                  // ASSUMED (Classic Firebolt rank 7, pet scaling)
  sacrifice: 0.15,
  // talents, per rank (Forever tooltips; per-rank = last rank / max rank)
  suppression: { hit: 0.01 }, improvedCorruption: { cast: 0.4, dmg: 0.02 }, malediction: { dmg: 0.01 }, improvedLifeTap: { restore: 0.10 },
  pandemic: { critBonus: 1 / 3 }, malevolence: { crit: 0.01 }, nightfall: { chance: 0.02 }, shadowMastery: { dmg: 0.01 }, improvedBaneOfAgony: { dmg: 0.05 },
  improvedShadowBolt: { dmg: 0.04, dur: 12 }, bane: { cast: 0.1, soulFire: 0.4 }, cataclysm: { cost: 0.10 / 3 }, aftermath: { dmg: 0.10 }, ruin: { critBonus: 0.2 },
  agonizingFlames: { dmg: 0.10 / 3 }, fireAndBrimstone: { crit: 0.25 / 3 }, shadowAndFlame: { dmg: 0.02, dur: 20 }, decimation: { cd: 0.45 },
  demonicKnowledge: { sp: 20 }, masterDemonologist: { dmg: 0.02 }, unholyPower: { pet: 0.02 }, improvedImp: { pet: 0.10 }, felVitality: { mana: 0.05 },
  soulSiphon: { dmg: 0.12 },
};

export const WARLOCK_DEFAULT_BUILD = {
  suppression: 0, improvedCorruption: 0, malediction: 0, improvedLifeTap: 0, pandemic: 0, malevolence: 0, nightfall: 0, shadowMastery: 0, improvedBaneOfAgony: 0,
  siphonLife: 0, wrack: 0, soulSiphon: 0,
  improvedShadowBolt: 0, bane: 0, cataclysm: 0, aftermath: 0, ruin: 0, shadowburn: 0, agonizingFlames: 0, conflagrate: 0, fireAndBrimstone: 0, shadowAndFlame: 0, incinerate: 0,
  decimation: 0, demonicKnowledge: 0, masterDemonologist: 0, unholyPower: 0, improvedImp: 0, felVitality: 0, demonicSacrifice: 0,
  rotation: 'affliction', curse: 'auto', filler: 'auto', pet: 'imp', sacrifice: 'none', useCooldowns: true, usePotion: true, useGem: true, immolate: 'auto',
};

const warlockParseCast = (c) => (typeof c === 'string' ? (c === 'instant' ? 0 : parseFloat(c)) : c);

export function warlockKit(build = {}, data = null) {
  const b = Object.assign({}, WARLOCK_DEFAULT_BUILD, build), W = JSON.parse(JSON.stringify(WARLOCK));
  const a = data && data.warlock && data.warlock.abilities;
  if (a) {
    const pull = (key, id) => {
      const x = a[id]; if (!x) return;
      const d = (x.effects || []).find((e) => e.kind === 'direct_damage'), p = (x.effects || []).find((e) => e.kind === 'periodic_damage'), s = W[key];
      if (d && d.dmg_range) { s.min = d.dmg_range[0]; s.max = d.dmg_range[1]; s.coeff = d.sp_coeff; }
      if (d && d.flat !== undefined) { s.flat = d.flat; s.coeff = d.sp_coeff; }
      if (p && s.dot) { s.dot.total = p.total_damage; s.dot.interval = p.tick_interval_sec; s.dot.ticks = Math.round(p.duration_sec / p.tick_interval_sec); s.dot.coeff = p.sp_coeff || 0; }
      if (x.resource_cost && x.resource_cost.mana) s.cost = x.resource_cost.mana;
      s.cast = warlockParseCast(x.cast_time);
    };
    pull('shadowBolt', 'warlock_shadow_bolt'); pull('immolate', 'warlock_immolate'); pull('corruption', 'warlock_corruption');
    const fut = (n) => (data.warlock.future || []).find((f) => f.name === n);
    const range = (r) => { const e = r.effects.find((x) => x.effect === 2); const mid = e.base + e.per_level * Math.max(0, 60 - r.spell_level) + 1; return [mid * (1 - e.variance / 2), mid * (1 + e.variance / 2), e.sp_coeff]; };
    const direct = (key, name) => { const f = fut(name); if (!f) return; const [lo, hi, co] = range(f.rank); Object.assign(W[key], { min: lo, max: hi, coeff: co, cost: f.rank.cost.amount, cast: f.rank.cast_ms / 1000 }); if (f.rank.cooldown_ms) W[key].cd = f.rank.cooldown_ms / 1000; };
    direct('conflagrate', 'Conflagrate'); direct('incinerate', 'Incinerate'); direct('soulFire', 'Soul Fire');
    const dotOf = (key, name, aura) => { const f = fut(name); if (!f) return; const e = f.rank.effects.find((x) => x.aura === aura); if (!e) return; const ticks = Math.max(1, Math.round(f.rank.duration_ms / e.period_ms)); Object.assign(W[key].dot, { total: e.base * ticks, ticks, interval: e.period_ms / 1000, coeff: e.sp_coeff }); W[key].cost = f.rank.cost.amount; if (f.rank.cooldown_ms) W[key].cd = f.rank.cooldown_ms / 1000; };
    dotOf('siphonLife', 'Siphon Life', 53); dotOf('wrack', 'Wrack', 3); dotOf('doom', 'Bane of Doom', 3);
  }

  return {
    name: 'warlock', build: b, W,
    setup(sim) {
      sim.player.resource = 'mana'; sim.kitBuild = b;
      const st = sim.stats;
      sim.manaMaxExtra = Math.floor(st.mana * W.felVitality.mana * b.felVitality);
      setupMana(sim, { manaMax: st.mana + sim.manaMaxExtra, mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int: st.int, spi: st.spi }), castingFraction: 0 });
      sim.critBase = 0; sim.regenMult = 1;
      sim.cd = { gem: 0, potion: 0, conflagrate: 0, soulFire: 0, shadowburn: 0, doom: 0 };
      sim.trance = false;
      const petOn = b.pet === 'imp' && !(b.sacrifice !== 'none' && b.demonicSacrifice);
      sim.petOn = petOn;
      sim.spBonus = petOn ? W.demonicKnowledge.sp * b.demonicKnowledge : 0;           // Demonic Knowledge: +33% of level per rank while a demon is out
      sim.sacrificed = b.sacrifice !== 'none' && b.demonicSacrifice ? b.sacrifice : null;
      sim.aISB = sim.addAura({ name: 'Shadow Vulnerability', duration: W.improvedShadowBolt.dur });
      sim.aSF = sim.addAura({ name: 'Shadow and Flame', duration: W.shadowAndFlame.dur });
      sim.aWrack = sim.addAura({ name: 'Wrack', duration: W.wrack.dur });
      sim.aTrance = sim.addAura({ name: 'Shadow Trance', duration: Infinity });
      sim.aDecim = sim.addAura({ name: 'Decimation', duration: 10 });
      // the Imp's Firebolt: independent cast loop, uses the warlock's spell power
      if (petOn) {
        const bolt = () => {
          const I = W.imp, e = sim.entry('Imp Firebolt'); e.casts++;
          if (sim.rng() < I.miss) { e.misses++; } else {
            const sp = ((st.sp || 0) + sim.spBonus) * I.spCoeff;
            let d = I.min + (I.max - I.min) * sim.rng() + sp;
            d *= (1 + W.improvedImp.pet * b.improvedImp) * (1 + W.unholyPower.pet * b.unholyPower) * (1 + W.masterDemonologist.dmg * b.masterDemonologist);
            const crit = sim.rng() < I.crit; if (crit) d *= SPELL_CRIT_MULT;
            sim.record('Imp Firebolt', d * (1 - sim.target.spellMitigation) * sim.target.spellTaken, crit ? 'crit' : 'hit');
          }
          sim.schedule(I.cast, bolt);
        };
        sim.schedule(0.5, bolt);
      }
      sim.est = (s) => {
        const sp = (st.sp || 0), m = mods(sim, s, true);
        const mid = s.min !== undefined ? (s.min + s.max) / 2 : s.flat;
        const bonus = s === W.incinerate && dotActive(sim, 'Immolate') ? W.incinerate.immolateBonus : 1;
        const hit = Math.min(0.99, 1 - sim.target.spellMiss + st.hit + m.hit), crit = Math.min(1, st.crit + m.crit);
        return ((mid + (sp + sim.spBonus) * s.coeff) * bonus * (1 + crit * 0.5 * (1 + m.critBonus)) * hit) * m.dmg / Math.max(warlockCastTime(sim, s), SPELL_GCD);
      };
    },
    start() {},
    rotate(sim) { return warlockRotate(sim, b, W); },
  };
}

// ---- modifiers ----
function has(s, x) { return s.schools.indexOf(x) >= 0; }
function mods(sim, s, noAuras, periodic) {
  const b = sim.kitBuild, W = sim.spec.W;
  let hit = W.suppression.hit * b.suppression, crit = 0, dmg = 1, critBonus = 0;
  const shadow = has(s, 'shadow'), fire = has(s, 'fire');
  if (shadow) { crit += W.malevolence.crit * b.malevolence; dmg *= 1 + W.shadowMastery.dmg * b.shadowMastery; if (sim.sacrificed === 'imp') dmg *= 1 + W.sacrifice; }
  if (fire && sim.sacrificed === 'succubus') dmg *= 1 + W.sacrifice;
  if (s.destruction) { critBonus += W.ruin.critBonus * b.ruin; dmg *= 1 + W.agonizingFlames.dmg * b.agonizingFlames; }
  if (periodic) { dmg *= 1 + W.malediction.dmg * b.malediction; if (shadow) critBonus += W.pandemic.critBonus * b.pandemic; }
  if (s === W.conflagrate) crit += W.fireAndBrimstone.crit * b.fireAndBrimstone;
  if (!noAuras) {
    if (shadow) {
      if (sim.aISB.active) dmg *= 1 + W.improvedShadowBolt.dmg * b.improvedShadowBolt;
      if (sim.aSF.active) dmg *= 1 + W.shadowAndFlame.dmg * b.shadowAndFlame;
      if (periodic && sim.aWrack.active && s !== W.wrack) dmg *= 1 + W.wrack.vuln;
    }
  }
  return { hit, crit, dmg, critBonus };
}
function warlockCastTime(sim, s) {
  const b = sim.kitBuild, W = sim.spec.W;
  let t = s.cast;
  if (s === W.shadowBolt || s === W.immolate || s === W.incinerate) t -= W.bane.cast * b.bane;
  if (s === W.soulFire) { t -= W.bane.soulFire * b.bane; if (sim.aDecim.active) t *= 1 - 0.2 * b.decimation; }
  if (s === W.corruption) t -= W.improvedCorruption.cast * b.improvedCorruption;
  if (s === W.shadowBolt && sim.aTrance.active) t = 0;
  return Math.max(0, t);
}
function warlockManaCost(sim, s) {
  const b = sim.kitBuild, W = sim.spec.W;
  let c = s.cost;
  if (s.destruction) c *= 1 - W.cataclysm.cost * b.cataclysm;
  if (s === W.soulFire && sim.aDecim.active) return 0;
  return Math.round(c);
}

// ---- cast a spell (direct part, then the periodic part when it landed) ----
function warlockCast(sim, s) {
  const b = sim.kitBuild, W = sim.spec.W, st = sim.stats;
  const cost = warlockManaCost(sim, s);
  const tranced = s === W.shadowBolt && sim.aTrance.active; if (tranced) sim.aTrance.expire();
  const ct = tranced ? 0 : warlockCastTime(sim, s);
  return beginCast(sim, s, ct, cost, () => {
    let landed = true;
    if (s.min !== undefined || s.flat !== undefined) {
      const m = mods(sim, s, false);
      let raw = (s.min !== undefined ? s.min + (s.max - s.min) * sim.rng() : s.flat * (s === W.immolate ? 1 + W.aftermath.dmg * b.aftermath : 1)) + (st.sp + sim.spBonus) * s.coeff;
      if (s === W.incinerate && dotActive(sim, 'Immolate')) raw *= W.incinerate.immolateBonus;
      const r = resolveSpell(sim, s.name, raw, m);
      landed = r.outcome !== 'miss';
      if (landed) afterDirect(sim, s, r);
    } else {
      // pure damage-over-time spells need a hit roll
      const m = mods(sim, s, false, true);
      const hit = Math.min(0.99, 1 - sim.target.spellMiss + st.hit + m.hit);
      const e = sim.entry(s.name);
      if (sim.rng() >= hit) { e.misses++; landed = false; }
    }
    if (landed && s.dot) startDot(sim, s);
  });
}
function afterDirect(sim, s, r) {
  const b = sim.kitBuild, W = sim.spec.W;
  if (s === W.shadowBolt && r.outcome === 'crit' && b.improvedShadowBolt) sim.aISB.apply();
  if (s === W.conflagrate) { if (b.shadowAndFlame) sim.aSF.apply(); if (!(b.shadowAndFlame && sim.rng() < 0.2 * b.shadowAndFlame)) cancelDot(sim, 'Immolate'); }
  if (s === W.shadowburn && b.shadowAndFlame) { /* fire bonus not tracked separately: Shadowburn's fire window is folded into Conflagrate's shadow window */ }
  if ((s === W.shadowBolt || s === W.incinerate) && b.decimation && sim.targetHealthPct() < 0.35) sim.aDecim.apply();
}
function startDot(sim, s) {
  const b = sim.kitBuild, W = sim.spec.W, st = sim.stats, d = s.dot;
  const m = mods(sim, s, false, true);
  let per = (d.total / d.ticks + (st.sp + sim.spBonus) * d.coeff) * m.dmg * (1 - sim.target.spellMitigation) * sim.target.spellTaken;
  if (s === W.corruption) per *= 1 + W.improvedCorruption.dmg * b.improvedCorruption;
  if (s === W.agony) per *= 1 + W.improvedBaneOfAgony.dmg * b.improvedBaneOfAgony;
  if (s === W.wrack) { sim.aWrack.apply(); if (b.soulSiphon) per *= 1 + Math.min(3, activeAfflictions(sim)) * W.soulSiphon.dmg * b.soulSiphon; }
  const critChance = Math.max(0, Math.min(1, st.crit + m.crit));
  const critMult = 1 + (SPELL_CRIT_MULT - 1) * (1 + m.critBonus);
  const onTick = (s === W.corruption || s === W.wrack) && b.nightfall ? () => { if (sim.rng() < W.nightfall.chance * b.nightfall) sim.aTrance.apply(); } : null;
  applyDotCrit(sim, s.name, per, d.ticks, d.interval, () => { const c = sim.rng() < critChance; return { crit: c, mult: c ? critMult : 1 }; }, onTick);
}
function activeAfflictions(sim) { return ['Corruption', 'Bane of Agony', 'Bane of Doom', 'Siphon Life'].filter((n) => dotActive(sim, n)).length; }

// ---- rotation ----
function warlockRotate(sim, b, W) {
  const now = sim.now, rem = sim.fightLen - now;
  if (sim.casting) return sim.casting.endsAt - now;
  if (b.usePotion && now >= sim.cd.potion && sim.mana <= sim.manaMax - (W.manaPotion.min + W.manaPotion.max) / 2 && rem > 20) {
    sim.cd.potion = now + W.manaPotion.cd; sim.entry('Mana Potion').casts++;
    gainMana(sim, W.manaPotion.min + (W.manaPotion.max - W.manaPotion.min) * sim.rng());
  }
  if (b.useGem && now >= sim.cd.gem && sim.mana <= sim.manaMax - (W.manaGem.min + W.manaGem.max) / 2 && rem > 15) {
    sim.cd.gem = now + W.manaGem.cd; sim.entry('Mana Gem').casts++;
    gainMana(sim, W.manaGem.min + (W.manaGem.max - W.manaGem.min) * sim.rng());
  }
  const gcdLeft = sim.gcdReadyAt - now;
  if (gcdLeft > 1e-9) return gcdLeft;
  const destro = b.rotation === 'destruction';
  const useDoom = b.curse === 'doom' || (b.curse === 'auto' && sim.fightLen >= 80);
  const filler = (() => {
    const cands = [W.shadowBolt];
    if (b.incinerate) cands.push(W.incinerate);
    if (b.filler === 'shadowBolt') return W.shadowBolt;
    if (b.filler === 'incinerate' && b.incinerate) return W.incinerate;
    return cands.sort((x, y) => sim.est(y) - sim.est(x))[0];
  })();
  const refresh = (s, margin) => dotLeft(sim, s.name) <= margin + warlockCastTime(sim, s) && (rem > 6);
  const wantImmolate = b.immolate === true || (b.immolate === 'auto' && (destro || b.conflagrate));
  let s = null;
  // the damage-over-time effects first
  {
    if (wantImmolate && refresh(W.immolate, 1.5) && rem > 8) s = W.immolate;
    else if (refresh(W.corruption, 1.0) && rem > 8) s = W.corruption;
    else if (useDoom ? (now >= sim.cd.doom && refresh(W.doom, 0) && rem > 62) : (refresh(W.agony, 1.5) && rem > 8)) s = useDoom ? W.doom : W.agony;
    else if (b.siphonLife && refresh(W.siphonLife, 1.5) && rem > 8) s = W.siphonLife;
    else if (b.wrack && refresh(W.wrack, 0.5)) s = W.wrack;
  }
  if (!s && b.conflagrate && now >= sim.cd.conflagrate && dotActive(sim, 'Immolate')) s = W.conflagrate;
  if (!s && b.shadowburn && now >= sim.cd.shadowburn && destro) s = W.shadowburn;
  if (!s && now >= sim.cd.soulFire && destro && sim.est(W.soulFire) > sim.est(filler) * 0.95) s = W.soulFire;
  if (!s) s = filler;
  // Life Tap when the next cast is not affordable (or the pool is nearly dry)
  const need = warlockManaCost(sim, s);
  if (need > sim.mana || sim.mana < 0.12 * sim.manaMax) {
    sim.gcdReadyAt = now + SPELL_GCD; sim.entry('Life Tap').casts++;
    gainMana(sim, W.lifeTap.restore * (1 + W.improvedLifeTap.restore * b.improvedLifeTap));
    return SPELL_GCD;
  }
  if (s === W.conflagrate) sim.cd.conflagrate = now + W.conflagrate.cd;
  if (s === W.shadowburn) sim.cd.shadowburn = now + W.shadowburn.cd;
  if (s === W.soulFire) sim.cd.soulFire = now + W.soulFire.cd * (1 - W.decimation.cd * b.decimation);
  if (s === W.doom) sim.cd.doom = now + W.doom.cd;
  return warlockCast(sim, s);
}
