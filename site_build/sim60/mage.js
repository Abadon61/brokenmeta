// Mage kit (Fire / Frost / Arcane). Numbers are WoW: Forever's own where the level-60 glossary has them
// (Fireball, Fire Blast, Pyroblast, Frostbolt, Scorch, Frostfire Bolt, Combustion cooldown) and the talent
// tooltips; ASSUMED = Classic 1.12 value kept until Forever's table is sourced (Arcane Missiles and Arcane Blast now come from the client tables):
//   Arcane Missiles / Ice Lance / Arcane Blast damage and costs, Arcane Power and Presence of Mind cooldowns,
//   Evocation, mana potion, spell hit/crit/mana formulas (see spells.js and character.js).
// Simplifications: Arcane Blast is not rotated (the Forever tooltip is ambiguous about which spells its stacks
// boost); Frostfire Bolt takes both the fire and the frost damage modifiers; Ignite stacks are summed;
// no trinkets, set bonuses, Mana Gems, Innervate or movement.
import { useRune, setupMana, gainMana, spendMana, spiritRegenPerSec, beginCast, resolveSpell, applyDot, SPELL_GCD } from './spells.js';

export const MAGE = {
  fireball: { name: 'Fireball', schools: ['fire'], cast: 3.5, cost: 410, min: 424.6, max: 541.4, coeff: 1, dot: { total: 60, ticks: 4, interval: 2, coeff: 0 }, heat: true },
  scorch: { name: 'Scorch', schools: ['fire'], cast: 1.5, cost: 150, min: 152, max: 207, coeff: 0.429, heat: true, incin: true },
  fireBlast: { name: 'Fire Blast', schools: ['fire'], cast: 0, cost: 340, min: 416.7, max: 489.3, coeff: 0.429, cd: 8, heat: true, incin: true },
  pyroblast: { name: 'Pyroblast', schools: ['fire'], cast: 6, cost: 440, min: 519.8, max: 646.2, coeff: 1, dot: { total: 212, ticks: 4, interval: 3, coeff: 0.15 } },
  frostbolt: { name: 'Frostbolt', schools: ['frost'], cast: 3, cost: 290, min: 457.2, max: 492.8, coeff: 0.814 },
  frostfireBolt: { name: 'Frostfire Bolt', schools: ['fire', 'frost'], cast: 3, cost: 370, min: 247, max: 337, coeff: 0.814, dot: { total: 57, ticks: 3, interval: 3, coeff: 0 }, heat: true },
  iceLance: { name: 'Ice Lance', schools: ['frost'], cast: 0, cost: 150, min: 173, max: 200, coeff: 0.143, incin: true },       // ASSUMED (Classic TBC-era value)
  arcaneWrath: { name: 'Arcane Wrath', schools: ['arcane'], cast: 3.5, cost: 395, min: 405.7, max: 496.3, coeff: 1, cd: 6, manaSp: 0.05, incin: false },   // build 70425 (spell 1326082): damage like Fireball plus spell power worth 5% of the maximum mana
  arcaneMissiles: { name: 'Arcane Missiles', schools: ['arcane'], cast: 5, cost: 655, total: 1085, coeff: 0.714, ticks: 5 },     // ASSUMED (Classic rank 8)
  // build 1.60.1.70425: Arcane Blast is a 1.5 s cast (damage and coefficient -40%); each cast gives 15% of the mage's Intellect as spell damage, stacking 4 times for 15 s from the FIRST cast, and raises its own cost
  arcaneBlast: { name: 'Arcane Blast', schools: ['arcane'], cast: 1.5, cost: 195, min: 218.2, max: 253.8, coeff: 0.429, incin: true, spPerInt: 0.15, stackCost: 1.75, maxStacks: 4, dur: 15 },
  combustion: { cd: 180 },
  manaGem: { cd: 120, min: 1073, max: 1127 },                                                                                    // ASSUMED (Mana Ruby)
  innervate: { cd: 360, dur: 20, mult: 5 },                                                                                      // ASSUMED (Classic, cast by a druid)
  movement: { period: 30 },
  arcanePower: { cd: 180, duration: 15, dmg: 1.3, cost: 1.3 },                                                                  // cooldown ASSUMED
  presenceOfMind: { cd: 180 },                                                                                                  // cooldown ASSUMED
  evocation: { cd: 480, restore: 0.6, duration: 8 },                                                                            // ASSUMED (Classic)
  manaPotion: { cd: 120, min: 1350, max: 2250 },                                                                                // ASSUMED (Major Mana Potion)
  // talents, per rank (Forever tooltips)
  arcaneFocus: { hit: 0.01 }, arcaneConcentration: { chance: 0.02 }, arcaneImpact: { crit: 0.02 }, arcaneMeditation: { keep: 1 / 6 },
  arcaneMind: { int: 0.02, critBonus: 0.2 }, arcaneInstability: { dmg: 0.01, crit: 0.01 }, missileBarrage: { ab: 0.2, am: 0.05, other: 0.10 },   // per rank (2 ranks since build 70425): Arcane Blast, each Arcane Missiles hit, Arcane Wrath / Fireball / Frostbolt / Frostfire Bolt
  incineration: { crit: 0.02 }, improvedFireball: { cast: 0.1 }, ignite: { frac: 0.08 }, improvedScorch: { chance: 0.33, perStack: 0.03, max: 5, dur: 30 },
  masterOfElements: { refund: 0.10 }, criticalMass: { crit: 0.02 }, firePower: { perEffect: 0.01, maxEffects: 4 }, wakeOfFire: { cd: 1 },   // Fire Power (3 ranks): +1% per rank for each Fire effect on the target (Ignite, Fire Vulnerability, Fireball and Pyroblast DoTs), up to 4 effects
  improvedFrostbolt: { cast: 0.1 }, elementalPrecision: { hit: 0.01 }, iceShards: { critBonus: 0.2 }, piercingIce: { dmg: 0.02 },
  frostChanneling: { cost: 0.05 }, shatter: { crit: 0.5 / 3 }, fingersOfFrost: { chance: 0.15 }, wintersChill: { chance: 0.2, crit: 0, max: 5 },   // build 70425: Winter's Chill only boosts Cone of Cold now (no crit on Frostbolt / Ice Lance)
  iceLanceFrozen: 3,                                                                    // build 70425: +200% against Frozen targets (was +300%)
};

export const MAGE_DEFAULT_BUILD = {
  arcaneFocus: 0, arcaneConcentration: 0, arcaneImpact: 0, arcaneMeditation: 0, arcaneMind: 0, arcaneInstability: 0, arcanePower: 0, presenceOfMind: 0, missileBarrage: 0,
  incineration: 0, improvedFireball: 0, ignite: 0, improvedScorch: 0, heatingUp: 0, masterOfElements: 0, criticalMass: 0, firePower: 0, combustion: 0, pyroblast: 0, wakeOfFire: 0, arcaneWrath: 0,
  improvedFrostbolt: 0, elementalPrecision: 0, iceShards: 0, piercingIce: 0, frostChanneling: 0, iceLance: 0, shatter: 0, fingersOfFrost: 0, wintersChill: 0,
  rotation: 'fire', filler: 'auto', useCooldowns: true, usePotion: true, useEvocation: true, useGem: true, innervate: false, movement: 0, arcaneBlast: 0,
};

const mageParseCast = (c) => (typeof c === 'string' ? (c === 'instant' ? 0 : parseFloat(c)) : c);

export function mageKit(build = {}, data = null) {
  const b = Object.assign({}, MAGE_DEFAULT_BUILD, build), M = JSON.parse(JSON.stringify(MAGE));
  const a = data && data.mage && data.mage.abilities;
  if (a) {
    const pull = (key, id, dotKey) => {
      const x = a[id]; if (!x) return;
      const d = (x.effects || []).find((e) => e.kind === 'direct_damage'), p = (x.effects || []).find((e) => e.kind === 'periodic_damage');
      const s = M[key];
      if (d) { s.min = d.dmg_range[0]; s.max = d.dmg_range[1]; s.coeff = d.sp_coeff; }
      if (p && s.dot) { s.dot.total = p.total_damage; s.dot.interval = p.tick_interval_sec; s.dot.ticks = Math.round(p.duration_sec / p.tick_interval_sec); if (p.sp_coeff !== undefined) s.dot.coeff = p.sp_coeff; }
      if (x.resource_cost && x.resource_cost.mana) s.cost = x.resource_cost.mana;
      s.cast = mageParseCast(x.cast_time); if (x.cooldown_sec) s.cd = x.cooldown_sec;
    };
    pull('fireball', 'mage_fireball'); pull('fireBlast', 'mage_fire_blast'); pull('pyroblast', 'mage_pyroblast'); pull('frostbolt', 'mage_frostbolt');
    const fut = (n) => (data.mage.future || []).find((f) => f.name === n);
    const range = (r) => { const e = r.effects.find((x) => x.effect === 2); const mid = e.base + e.per_level * Math.max(0, 60 - r.spell_level) + 1; return [mid * (1 - e.variance / 2), mid * (1 + e.variance / 2), e.sp_coeff]; };
    const sc = fut('Scorch'); if (sc) { const [lo, hi, co] = range(sc.rank); Object.assign(M.scorch, { min: lo, max: hi, coeff: co, cost: sc.rank.cost.amount, cast: sc.rank.cast_ms / 1000 }); }
    const ff = fut('Frostfire Bolt'); if (ff) { const [lo, hi, co] = range(ff.rank); Object.assign(M.frostfireBolt, { min: lo, max: hi, coeff: co, cost: ff.rank.cost.amount, cast: ff.rank.cast_ms / 1000 }); const dt = ff.rank.effects.find((x) => x.aura === 3); if (dt) M.frostfireBolt.dot.total = dt.base * 3; }
    const cb = fut('Combustion'); if (cb) M.combustion.cd = cb.rank.cooldown_ms / 1000;
    // Arcane Missiles and Arcane Blast straight from the client's rank ladders (spells60.json: extra): per-missile damage and coefficient, 15% of base mana for Arcane Blast
    const ex = data.mage.extra || {};
    if (ex['Arcane Missiles Tick'] && ex['Arcane Missiles']) {
      const t = ex['Arcane Missiles Tick'], c = ex['Arcane Missiles'], e = t.effects.find((x) => x.effect === 2), ticks = Math.round(c.duration_ms / 1000);
      Object.assign(M.arcaneMissiles, { cost: c.cost.amount, ticks, cast: ticks, total: ticks * (e.base + e.per_level * Math.max(0, 60 - t.spell_level)), coeff: ticks * e.sp_coeff });
    }
    if (ex['Arcane Blast']) {
      const r = ex['Arcane Blast'], e = r.effects.find((x) => x.effect === 2), mid = e.base + e.per_level * Math.max(0, Math.min(60, r.max_level || 60) - r.spell_level);
      Object.assign(M.arcaneBlast, { min: mid * (1 - e.variance / 2), max: mid * (1 + e.variance / 2), coeff: e.sp_coeff, cast: r.cast_ms / 1000, cost: Math.round(r.cost_pct / 100 * 1213) });
      const st = ex['Arcane Blast Stacks']; if (st) { const sp = st.effects.find((x) => x.aura === 174); if (sp) M.arcaneBlast.spPerInt = sp.base / 100; M.arcaneBlast.dur = st.duration_ms / 1000; }
    }
    if (ex['Arcane Wrath']) {
      const r = ex['Arcane Wrath'], e = r.effects.find((x) => x.effect === 2), m = r.effects.find((x) => x.effect === 3), mid = e.base + e.per_level * Math.max(0, Math.min(60, r.max_level || 60) - r.spell_level);
      Object.assign(M.arcaneWrath, { min: mid * (1 - e.variance / 2), max: mid * (1 + e.variance / 2), coeff: e.sp_coeff, cast: r.cast_ms / 1000, cd: r.cooldown_ms / 1000, cost: r.cost.amount || Math.round(r.cost_pct / 100 * 1213), manaSp: m ? m.base / 100 : 0.05 });
    }
    if (ex['Ice Lance']) { const f = ex['Ice Lance'].effects.find((x) => x.effect === 3 && x.base >= 100); if (f) M.iceLanceFrozen = 1 + f.base / 100; }
  }

  return {
    name: 'mage', build: b, M,
    setup(sim) {
      sim.player.resource = 'mana'; sim.kitBuild = b;
      const st = sim.stats, intBonus = M.arcaneMind.int * b.arcaneMind;
      const extraInt = Math.floor((st.int || 0) * intBonus);
      sim.critBase = extraInt / 59.5 / 100;                                         // Arcane Mind's extra Intellect -> crit (ASSUMED Classic ratio)
      sim.manaMaxExtra = 15 * extraInt;
      setupMana(sim, { manaMax: st.mana + sim.manaMaxExtra, mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int: (st.int || 0) + extraInt, spi: st.spi }), castingFraction: M.arcaneMeditation.keep * b.arcaneMeditation });
      sim.cd = { gem: 0, innervate: 0, fireBlast: 0, combustion: 0, arcanePower: 0, presenceOfMind: 0, evocation: 0, potion: 0, arcaneWrath: 0 };
      sim.abInt = (st.int || 0) + extraInt;
      sim.pom = false; sim.cc = false; sim.mb = false; sim.fof = 0; sim.combCrits = 0; sim.heatStacks = 0;
      sim.aScorch = sim.addAura({ name: 'Fire Vulnerability', duration: M.improvedScorch.dur, maxStacks: M.improvedScorch.max });
      sim.aHeat = sim.addAura({ name: 'Heating Up', duration: 20, maxStacks: 3 });
      sim.aComb = sim.addAura({ name: 'Combustion', duration: Infinity, maxStacks: 99 });
      sim.aAP = sim.addAura({ name: 'Arcane Power', duration: M.arcanePower.duration });
      sim.aWC = sim.addAura({ name: "Winter's Chill", duration: 15, maxStacks: M.wintersChill.max });
      sim.aFoF = sim.addAura({ name: 'Fingers of Frost', duration: 15 });
      sim.aCC = sim.addAura({ name: 'Clearcasting', duration: Infinity });
      sim.aAB = sim.addAura({ name: 'Arcane Blast', duration: M.arcaneBlast.dur, maxStacks: M.arcaneBlast.maxStacks });
      sim.aInn = sim.addAura({ name: 'Innervate', duration: M.innervate.dur, onApply: () => { sim.regenMult = M.innervate.mult; }, onExpire: () => { sim.regenMult = 1; } });
      sim.regenMult = 1; sim.moving = false;
      if (b.movement > 0) {
        const per = M.movement.period, len = Math.min(per * 0.9, per * b.movement);
        const go = () => { if (sim.casting) { sim.schedule(0.1, go); return; } sim.moving = true; sim.schedule(len, () => { sim.moving = false; sim.poke(0); }); sim.schedule(per, go); };
        sim.schedule(per / 2, go);
      }
      sim.aMB = sim.addAura({ name: 'Missile Barrage', duration: Infinity });
      const ab = M.arcaneBlast, am = M.arcaneMissiles;
      sim.est = (s) => {
        const mid = s.total !== undefined ? s.total : (s.min + s.max) / 2, sp = (st.sp || 0) * s.coeff;
        const dot = s.dot ? s.dot.total + (st.sp || 0) * (s.dot.coeff || 0) : 0;
        const m = specMods(sim, s, true);
        const hit = Math.min(0.99, 1 - sim.target.spellMiss + st.hit + m.hit), crit = Math.min(1, st.crit + sim.critBase + m.crit);
        return ((mid + sp) * (1 + crit * (0.5 * (1 + m.critBonus))) * hit + dot) * m.dmg / Math.max(mageCastTime(sim, s, true), SPELL_GCD);
      };
    },
    start(sim) { sim.arcaneBurst = arcaneBurstBetter(sim, M, b); sim.awBetter = arcaneWrathBetter(sim, M, b); },
    rotate(sim) { return mageRotate(sim, b, M); },
  };
}

// ---- modifiers ----
function schoolHas(s, x) { return s.schools.indexOf(x) >= 0; }
function specMods(sim, s, noAuras, extra = 1) {
  const b = sim.kitBuild, M = sim.spec.M;
  let hit = 0, crit = 0, dmg = extra, critBonus = 0;
  const fire = schoolHas(s, 'fire'), frost = schoolHas(s, 'frost'), arcane = schoolHas(s, 'arcane');
  if (fire || frost) hit += M.elementalPrecision.hit * b.elementalPrecision;
  if (arcane) { hit += M.arcaneFocus.hit * b.arcaneFocus; crit += M.arcaneImpact.crit * b.arcaneImpact; critBonus += M.arcaneMind.critBonus * b.arcaneMind; }
  if (fire) { crit += M.criticalMass.crit * b.criticalMass; if (!noAuras && b.firePower) dmg *= 1 + M.firePower.perEffect * b.firePower * Math.min(M.firePower.maxEffects, fireEffects(sim)); }
  if (frost) { dmg *= 1 + M.piercingIce.dmg * b.piercingIce; critBonus += M.iceShards.critBonus * b.iceShards; }
  if (s.incin) crit += M.incineration.crit * b.incineration;
  crit += M.arcaneInstability.crit * b.arcaneInstability; dmg *= 1 + M.arcaneInstability.dmg * b.arcaneInstability;
  if (!noAuras) {
    if (sim.aAP.active) dmg *= M.arcanePower.dmg;
    if (fire) { crit += sim.aComb.stacks * 0.10; if (sim.aScorch.active) dmg *= 1 + M.improvedScorch.perStack * sim.aScorch.stacks; }
    if (s === M.frostbolt || s === M.iceLance) crit += sim.aWC.stacks * M.wintersChill.crit;
    if (sim.aFoF.active) { crit += M.shatter.crit * b.shatter; if (s === M.iceLance) dmg *= M.iceLanceFrozen; }
  }
  return { hit, crit: crit + sim.critBase, dmg, critBonus };
}
// Fire effects on the target for Fire Power (build 70425): Ignite, Fire Vulnerability (Improved Scorch), the Fireball and Pyroblast damage over time
function fireEffects(sim) {
  const e = sim.fxEnds || {};
  return (e.Ignite > sim.now ? 1 : 0) + (sim.aScorch.active ? 1 : 0) + (e.Fireball > sim.now ? 1 : 0) + (e.Pyroblast > sim.now ? 1 : 0);
}
const markFx = (sim, name, dur) => { (sim.fxEnds || (sim.fxEnds = {}))[name] = sim.now + dur; };
// Arcane Blast stacks: 15% of the Intellect as spell damage per stack (build 70425)
function abSpell(sim, s) {
  const M = sim.spec.M;
  return M.arcaneBlast.spPerInt * (sim.abInt || 0) * (sim.aAB.active ? sim.aAB.stacks : 0) + (s === M.arcaneWrath ? M.arcaneWrath.manaSp * sim.manaMax : 0);
}
function mageCastTime(sim, s, noAuras) {
  const b = sim.kitBuild, M = sim.spec.M;
  let t = s.cast;
  if (s === M.fireball || s === M.frostfireBolt) t -= M.improvedFireball.cast * b.improvedFireball;
  if (s === M.frostbolt) t -= M.improvedFrostbolt.cast * b.improvedFrostbolt;
  if (s === M.pyroblast && !noAuras && sim.aHeat.active) t *= 1 - 0.25 * sim.aHeat.stacks;
  return t;
}
function mageManaCost(sim, s) {
  const b = sim.kitBuild, M = sim.spec.M;
  if (sim.aCC.active) return 0;
  if (s === M.arcaneBlast) { let c = s.cost * (1 + s.stackCost * sim.aAB.stacks); if (sim.aAP.active) c *= M.arcanePower.cost; return Math.round(c); }
  if (s === M.arcaneMissiles && sim.aMB.active) return 0;
  let c = s.cost;
  if (schoolHas(s, 'frost')) c *= 1 - M.frostChanneling.cost * b.frostChanneling;
  if (sim.aAP.active) c *= M.arcanePower.cost;
  return Math.round(c);
}

// ---- casting a damage spell ----
function mageCast(sim, s, instant) {
  const b = sim.kitBuild, M = sim.spec.M, cost = mageManaCost(sim, s);
  const usedCC = sim.aCC.active; if (usedCC) sim.aCC.expire();
  const pomUsed = sim.pom && s.cast >= 1.5 && s !== M.arcaneMissiles; if (pomUsed) sim.pom = false;
  let ct = instant ? 0 : mageCastTime(sim, s);
  if (pomUsed) ct = 0;
  if (s === M.pyroblast && !pomUsed) sim.aHeat.expire();         // build 70425: Heating Up is not consumed by a Presence of Mind Pyroblast
  const extra = 1;
  if (s === M.arcaneWrath) sim.cd.arcaneWrath = sim.now + M.arcaneWrath.cd;
  if (s === M.arcaneMissiles) return channelMissiles(sim, s, cost, extra);
  const baseCost = s.cost;
  return beginCast(sim, s, ct, cost, () => {
    const m = specMods(sim, s, false, extra);
    const raw = s.min + (s.max - s.min) * sim.rng() + (sim.stats.sp + abSpell(sim, s)) * s.coeff;
    const r = resolveSpell(sim, s.name, raw, m);
    afterHit(sim, s, r, m, baseCost);
    if (s === M.arcaneBlast && r.outcome !== 'miss') sim.aAB.apply(1, sim.aAB.active ? sim.aAB.endsAt - sim.now : undefined);   // the 15 s run from the first cast
    if (r.outcome !== 'miss' && s.dot) {
      const total = s.dot.total + sim.stats.sp * (s.dot.coeff || 0);
      applyDot(sim, s.name + ' (DoT)', total * m.dmg * (1 - sim.target.spellMitigation) * sim.target.spellTaken, s.dot.ticks, s.dot.interval);
      if (s === M.fireball) markFx(sim, 'Fireball', s.dot.ticks * s.dot.interval); else if (s === M.pyroblast) markFx(sim, 'Pyroblast', s.dot.ticks * s.dot.interval);
    }
  });
}
function afterHit(sim, s, r, m, baseCost) {
  const b = sim.kitBuild, M = sim.spec.M;
  if (sim.aFoF.active && s !== M.arcaneMissiles && --sim.fof <= 0) sim.aFoF.expire();   // Fingers of Frost: each spell uses a charge
  if (r.outcome === 'miss') return;
  const crit = r.outcome === 'crit', fire = schoolHas(s, 'fire'), frost = schoolHas(s, 'frost');
  if (b.arcaneConcentration && sim.rng() < M.arcaneConcentration.chance * b.arcaneConcentration) sim.aCC.apply();
  if (crit && (fire || frost) && b.masterOfElements) gainMana(sim, baseCost * M.masterOfElements.refund * b.masterOfElements);
  if (fire) {
    if (sim.aComb.active) { sim.aComb.apply(1); if (crit && ++sim.combCrits >= 3) { sim.aComb.expire(); sim.combCrits = 0; } }
    if (crit && b.ignite) { const total = r.dmg * M.ignite.frac * b.ignite; applyDot(sim, 'Ignite', total, 2, 2); markFx(sim, 'Ignite', 4); }
  }
  if (crit && s.heat && b.heatingUp) sim.aHeat.apply(1);
  if (s === M.fireBlast && b.heatingUp) sim.aHeat.apply(1);      // build 70425: Fire Blast always adds a charge (two on a critical strike)
  if (s === M.scorch && b.improvedScorch && sim.rng() < Math.min(1, M.improvedScorch.chance * b.improvedScorch)) sim.aScorch.apply(1);
  if (frost && b.wintersChill && sim.rng() < M.wintersChill.chance * b.wintersChill) sim.aWC.apply(1);
  if (s === M.frostbolt && b.fingersOfFrost && sim.rng() < M.fingersOfFrost.chance) { sim.fof = b.fingersOfFrost; sim.aFoF.apply(); }
  if (b.missileBarrage) {                                       // build 70425: 2 ranks; Arcane Blast 20% / 40%, each Arcane Missiles hit 5% / 10%, Arcane Wrath / Fireball / Frostbolt / Frostfire Bolt 10% / 20%
    const p = s === M.arcaneBlast ? M.missileBarrage.ab : s === M.arcaneMissiles ? M.missileBarrage.am : (s === M.fireball || s === M.frostbolt || s === M.frostfireBolt || s === M.arcaneWrath) ? M.missileBarrage.other : 0;
    if (p && sim.rng() < p * b.missileBarrage) sim.aMB.apply();
  }
}
function channelMissiles(sim, s, cost, extra = 1) {
  const M = sim.spec.M, barrage = sim.aMB.active; if (barrage) sim.aMB.expire();
  const total = s.total + (sim.stats.sp + abSpell(sim, s)) * s.coeff, per = total / s.ticks, step = barrage ? 0.5 : 1;
  const dur = step * s.ticks / sim.hasteMult();
  const m0 = specMods(sim, s, false, extra);
  sim.gcdReadyAt = sim.now + SPELL_GCD; spendMana(sim, cost); sim.entry(s.name).casts++;
  sim.casting = { name: s.name, endsAt: sim.now + dur };
  for (let i = 1; i <= s.ticks; i++) sim.schedule(dur * i / s.ticks, () => {
    const r = resolveSpell(sim, s.name, per, specMods(sim, s, false, extra));
    afterHit(sim, s, r, m0, s.cost / s.ticks);
  });
  sim.schedule(dur, () => { sim.casting = null; sim.lastCastAt = sim.now; sim.poke(0); });
  return dur;
}

// ---- rotation ----
function mageRotate(sim, b, M) {
  const now = sim.now;
  if (sim.casting) return sim.casting.endsAt - now;
  const rem = sim.fightLen - now;
  // mana potion (off the global cooldown)
  if (b.usePotion && now >= sim.cd.potion && sim.mana <= sim.manaMax - (M.manaPotion.min + M.manaPotion.max) / 2 && rem > 20) {
    sim.cd.potion = now + M.manaPotion.cd; sim.entry('Mana Potion').casts++;
    gainMana(sim, M.manaPotion.min + (M.manaPotion.max - M.manaPotion.min) * sim.rng());
  }
  if (b.useGem && now >= sim.cd.gem && sim.mana <= sim.manaMax - (M.manaGem.min + M.manaGem.max) / 2 && rem > 15) {
    sim.cd.gem = now + M.manaGem.cd; sim.entry('Mana Gem').casts++;
    gainMana(sim, M.manaGem.min + (M.manaGem.max - M.manaGem.min) * sim.rng());
  }
  useRune(sim, b);
  if (b.innervate && now >= sim.cd.innervate && sim.mana < 0.5 * sim.manaMax) { sim.cd.innervate = now + M.innervate.cd; sim.entry('Innervate').casts++; sim.aInn.apply(); }
  if (b.useCooldowns) {
    if (b.combustion && now >= sim.cd.combustion && !sim.aComb.active) { sim.cd.combustion = now + M.combustion.cd; sim.entry('Combustion').casts++; sim.aComb.apply(1); sim.combCrits = 0; }
    if (b.arcanePower && now >= sim.cd.arcanePower) { sim.cd.arcanePower = now + M.arcanePower.cd; sim.entry('Arcane Power').casts++; sim.aAP.apply(); }
    if (b.presenceOfMind && now >= sim.cd.presenceOfMind && !sim.pom && b.rotation !== 'arcane') { sim.cd.presenceOfMind = now + M.presenceOfMind.cd; sim.entry('Presence of Mind').casts++; sim.pom = true; }
  }
  const gcdLeft = sim.gcdReadyAt - now;
  if (gcdLeft > 1e-9) return gcdLeft;
  const rotation = b.rotation;
  const instantOnly = sim.moving;
  const pick = () => {
    if (rotation === 'frost') return (b.iceLance && sim.aFoF.active) ? M.iceLance : M.frostbolt;
    if (rotation === 'arcane') {
      // build 70425: stack Arcane Blast to the cap (15% of the Intellect as spell damage each, 15 s from the first cast), spend the stacks on Arcane Wrath (every 6 s) and Arcane Missiles
      if (b.arcaneBlast && sim.arcaneBurst && sim.aAB.stacks < M.arcaneBlast.maxStacks) return M.arcaneBlast;
      if (b.arcaneWrath && sim.awBetter && now >= sim.cd.arcaneWrath) return M.arcaneWrath;
      return M.arcaneMissiles;
    }
    // fire
    if (b.improvedScorch && !sim.aScorch.active || (b.improvedScorch && sim.aScorch.stacks < M.improvedScorch.max) || (b.improvedScorch && sim.aScorch.endsAt - now < 6)) return M.scorch;
    if (now >= sim.cd.fireBlast) return M.fireBlast;
    if (b.pyroblast && (sim.pom || sim.aHeat.stacks >= 2)) return M.pyroblast;
    if (b.filler === 'fireball') return M.fireball;
    if (b.filler === 'frostfire') return M.frostfireBolt;
    return sim.est(M.frostfireBolt) > sim.est(M.fireball) ? M.frostfireBolt : M.fireball;
  };
  let s = pick();
  if (instantOnly && s.cast > 0 && !sim.pom) {      // moving: only instant spells
    const alt = (b.iceLance && sim.aFoF.active && rotation === 'frost') ? M.iceLance : (b.rotation === 'fire' && now >= sim.cd.fireBlast) ? M.fireBlast : null;
    if (!alt) return 0.25;
    s = alt;
  }
  // out of mana: Evocation, else wait for the regeneration
  if (mageManaCost(sim, s) > sim.mana) {
    if (b.useEvocation && now >= sim.cd.evocation && rem > 10) {
      sim.cd.evocation = now + M.evocation.cd; sim.entry('Evocation').casts++;
      sim.gcdReadyAt = now + SPELL_GCD; sim.casting = { name: 'Evocation', endsAt: now + M.evocation.duration };
      const per = M.evocation.restore * sim.manaMax / 4;
      for (let i = 1; i <= 4; i++) sim.schedule(2 * i, () => gainMana(sim, per));
      sim.schedule(M.evocation.duration, () => { sim.casting = null; sim.lastCastAt = sim.now; sim.poke(0); });
      return M.evocation.duration;
    }
    sim.manaOom += 0.5;
    return 0.5;
  }
  if (s === M.fireBlast) sim.cd.fireBlast = now + M.fireBlast.cd - M.wakeOfFire.cd * b.wakeOfFire;
  return mageCast(sim, s, s.cast === 0);
}

// Arcane Wrath (3.5 s cast, 6 s cooldown) is only cast when it deals more per second than Arcane Missiles (mana folded in the same way as for the burst).
function arcaneWrathBetter(sim, M, b) {
  if (!b.arcaneWrath || b.rotation !== 'arcane') return false;
  const st = sim.stats, aw = M.arcaneWrath, am = M.arcaneMissiles, h = sim.hasteMult();
  const dmgOf = (s, spExtra, mid) => { const m = specMods(sim, s, true); const crit = 1 + Math.min(1, st.crit + m.crit) * 0.5 * (1 + m.critBonus), hit = Math.min(0.99, 1 - sim.target.spellMiss + st.hit + m.hit); return (mid + (st.sp + spExtra) * s.coeff) * crit * hit * m.dmg; };
  const awD = dmgOf(aw, aw.manaSp * sim.manaMax, (aw.min + aw.max) / 2), amD = dmgOf(am, 0, am.total);
  const budget = sim.manaMax / 180 + (st.mp5 || 0) / 5 + 8;
  return awD / Math.max(aw.cast / h, aw.cost / budget) > amD / Math.max(am.cast / h, am.cost / budget);
}

// Arcane (build 1.60.1.70425): is "four Arcane Blasts, then Arcane Wrath and Arcane Missiles with the stacks" better than Arcane Wrath + Arcane Missiles alone?
// Each Arcane Blast stack gives 15% of the Intellect as spell damage for 15 s. Compared on damage per second with the mana cost folded in
// (damage per second of mana-limited play: dmg / max(time, mana / manaRate)).
function arcaneBurstBetter(sim, M, b) {
  if (!b.arcaneBlast || b.rotation !== 'arcane') return false;
  const st = sim.stats, ab = M.arcaneBlast, am = M.arcaneMissiles, aw = b.arcaneWrath ? M.arcaneWrath : null;
  const boost = ab.spPerInt * (sim.abInt || st.int || 0), h = sim.hasteMult();
  const dmgOf = (s, spExtra, mid) => {
    const m = specMods(sim, s, true);
    const crit = 1 + Math.min(1, st.crit + m.crit) * 0.5 * (1 + m.critBonus), hit = Math.min(0.99, 1 - sim.target.spellMiss + st.hit + m.hit);
    return (mid + (st.sp + spExtra) * s.coeff) * crit * hit * m.dmg;
  };
  const abMid = (ab.min + ab.max) / 2, awMid = aw ? (aw.min + aw.max) / 2 : 0, awExtra = aw ? aw.manaSp * sim.manaMax : 0;
  let dmg = 0, mana = 0, time = 0;
  for (let i = 0; i < ab.maxStacks; i++) { dmg += dmgOf(ab, boost * i, abMid); mana += ab.cost * (1 + ab.stackCost * i); time += ab.cast / h; }
  if (aw) { dmg += dmgOf(aw, boost * ab.maxStacks + awExtra, awMid); mana += aw.cost; time += aw.cast / h; }
  dmg += dmgOf(am, boost * ab.maxStacks, am.total); mana += am.cost; time += am.cast / h;
  let pd = dmgOf(am, 0, am.total), pm = am.cost, pt = am.cast / h;
  if (aw) { pd += dmgOf(aw, awExtra, awMid); pm += aw.cost; pt += aw.cast / h; }
  const rate = (st.mp5 || 0) / 5 + 0.0;                       // mana regained per second while casting (gear only)
  const budget = sim.manaMax / 180 + rate + 8;                // rough sustainable mana per second over a 3-minute fight (pool + potions + regen)
  return dmg / Math.max(time, mana / budget) > (pd / Math.max(pt, pm / budget)) * 1.05;
}
