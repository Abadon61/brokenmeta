// Warrior spec kits: Fury (dual wield) and Arms (two-hander). Numbers come from WoW: Forever's own
// tables/tooltips (data/spells60.json, exported by wow_sim60_export.py) when `data` is passed, and from
// the constants below otherwise. Values marked ASSUMED are Classic 1.12 numbers kept until Forever's
// level-60 table for that spell is sourced.
import { yellowAttack, castGcd } from './shared.js';

export const WARRIOR = {
  bloodthirst: { cost: 30, cd: 6, apCoeff: 0.35, flat: 48 },           // glossary at L60: 35% AP + 48
  whirlwind: { cost: 25, cd: 10, flat: 0, normSpeed1H: 2.4, normSpeed2H: 3.3 }, // 100% normalized weapon damage (normalization speeds ASSUMED Classic)
  heroicStrike: { cost: 15, flat: 157 },
  slam: { cost: 15, cd: 0, flat: 87, cast: 1.5 },
  overpower: { cost: 5, cd: 5, flat: 35 },
  rend: { cost: 10, total: 147, duration: 21, tick: 3 },
  mortalStrike: { cost: 30, cd: 6, flat: 160, normSpeed2H: 3.3 },      // client table (spell 21553 at L60): weapon damage + 160
  execute: { cost: 15, base: 600, perRage: 15 },                       // ASSUMED Classic rank 5 (600 + 15 per excess Rage)
  deathWish: { cost: 10, cd: 180, duration: 30, dmgMult: 1.2 },
  recklessness: { cd: 1800, duration: 15, crit: 1.0 },                 // ASSUMED Classic effect; cooldown from the client table
  bloodrage: { cd: 60, immediate: 10, overTime: 10, overTimeSec: 10 },
  flurry: { perRank: 0.05, charges: 3, expire: 15 },
  unbridledWrath: { chancePerRank: 0.12 },
  dualWieldSpec: { ohDmgPerRank: 0.05, ohHitPerRank: 0.02 },
  cruelty: { critPerRank: 0.01 },
  precision: { hitPerRank: 0.01 },
  improvedHeroicStrike: { costPerRank: 1 },
  improvedExecute: { cost: [0, 3, 5] },                                // Forever: -3 Rage at rank 1, -5 at rank 2
  improvedOverpower: { critPerRank: 0.25 },                            // Forever: +25% Overpower crit chance per rank
  improvedSlam: { castReductionPerRank: 0.25 },                        // Forever: -0.25 s cast time per rank; no swing delay at rank 2
  boundlessRage: { capPerRank: 10 },
  angerManagement: { interval: 3, amount: 1 },
  deepWounds: { pctPerRank: 0.20, duration: 12, tick: 3 },             // 3 ranks, 60% of average weapon damage over 12 s
  twoHandSpec: { dmgPerRank: 0.01 },
  impale: { critDmgPerRank: 0.10 },
  enrage: { dmgPerRank: 0.02 },                                        // Forever: 30% chance on being hit, +2% Physical damage per rank for 12 s
  weaponmaster: { axeCritPerRank: 0.01, maceArmorPerRank: 0.03, swordExtraAttackPerRank: 0.01 },
  improvedBerserkerRage: { ragePerRank: 5 },                           // Forever: Berserker Rage instantly generates 5 Rage per rank
  berserkerRage: { cd: 30 },
  improvedRend: { bleedPerRank: 0.12 },
};

// Overrides from the exported client data (spells60.json -> warrior.abilities), when available.
export function warriorFromData(spells60) {
  const W = JSON.parse(JSON.stringify(WARRIOR));
  const a = spells60 && spells60.warrior && spells60.warrior.abilities;
  if (!a) return W;
  const eff = (id, kind) => (a[id] && a[id].effects || []).find((e) => e.kind === kind);
  const cost = (id) => a[id] && a[id].resource_cost && a[id].resource_cost.rage;
  const bt = eff('warrior_bloodthirst', 'direct_damage');
  if (bt) { W.bloodthirst.apCoeff = bt.ap_coeff; W.bloodthirst.flat = bt.flat || 0; }
  if (cost('warrior_bloodthirst')) W.bloodthirst.cost = cost('warrior_bloodthirst');
  const hs = eff('warrior_heroic_strike', 'flat_bonus_on_next_swing'); if (hs) W.heroicStrike.flat = hs.flat;
  const sl = eff('warrior_slam', 'normalized_weapon_damage'); if (sl) W.slam.flat = sl.flat;
  const op = eff('warrior_overpower', 'normalized_weapon_damage'); if (op) W.overpower.flat = op.flat;
  const rd = eff('warrior_rend', 'periodic_damage'); if (rd) { W.rend.total = rd.total_damage; W.rend.duration = rd.duration_sec; W.rend.tick = rd.tick_interval_sec; }
  const dw = eff('warrior_death_wish', 'self_buff'); if (dw) { W.deathWish.dmgMult = 1 + dw.physical_damage_done_pct; W.deathWish.duration = dw.duration_sec; }
  const fut = (spells60.warrior.future || []).find((f) => f.name === 'Mortal Strike');
  if (fut) {
    const e = fut.rank.effects.find((x) => x.effect === 121);
    if (e) W.mortalStrike.flat = e.base;
    W.mortalStrike.cost = fut.rank.cost.amount / 10; W.mortalStrike.cd = fut.rank.cooldown_ms / 1000;
  }
  const rk = (spells60.warrior.future || []).find((f) => f.name === 'Recklessness');
  if (rk) W.recklessness.cd = rk.rank.cooldown_ms / 1000;
  return W;
}

export const FURY_DEFAULT_BUILD = {
  cruelty: 5, unbridledWrath: 5, dualWieldSpec: 5, flurry: 5, precision: 3, improvedHeroicStrike: 0,
  improvedExecute: 2, boundlessRage: 3, ragingBlows: 1, deathWish: 1, bloodthirst: 1, enrage: 5, improvedBerserkerRage: 2,
  enrageUptime: 0.0,            // Enrage needs incoming damage; 0 = off unless the user enters an expected uptime
  hsRageReserve: 0, useRecklessness: true, useDeathWish: true, executePhase: true,
};
export const ARMS_DEFAULT_BUILD = {
  cruelty: 5, unbridledWrath: 5, improvedHeroicStrike: 3, improvedOverpower: 2, angerManagement: 1, deepWounds: 3,
  twoHandSpec: 3, impale: 2, weaponmaster: 5, improvedSlam: 2, improvedExecute: 0, boundlessRage: 0, precision: 0,
  mortalStrike: 1, useSlam: true, useRend: false, hsRageReserve: 20, useRecklessness: true, executePhase: true, flurry: 0,
};

// ---- shared helpers ----
function commonSetup(sim, b, W) {
  const mods = sim.mods;
  sim.kitBuild = b;
  sim.player.resource = 'rage';
  sim.rageCap = 100 + W.boundlessRage.capPerRank * (b.boundlessRage || 0);
  mods.critBonus += W.cruelty.critPerRank * (b.cruelty || 0);
  mods.hitBonus += W.precision.hitPerRank * (b.precision || 0);
  sim.reckAura = sim.addAura({ name: 'Recklessness', duration: W.recklessness.duration, mods: { critBonus: W.recklessness.crit } });
  sim.sRK = sim.addSpell({ name: 'Recklessness', cost: () => 0, cd: W.recklessness.cd });
  sim.sBR = sim.addSpell({ name: 'Bloodrage', cost: () => 0, cd: W.bloodrage.cd });
  sim.sEX = sim.addSpell({ name: 'Execute', cost: () => Math.max(0, W.execute.cost - W.improvedExecute.cost[b.improvedExecute || 0]), cd: 0 });
  sim.hsCost = () => Math.max(0, W.heroicStrike.cost - W.improvedHeroicStrike.costPerRank * (b.improvedHeroicStrike || 0));
  sim.sHS = sim.addSpell({
    name: 'Heroic Strike', cost: sim.hsCost,
    onSwing(s, sw) {            // replaces the main-hand white swing
      s.spendRage(s.hsCost()); s.entry('Heroic Strike').casts++;
      yellowAttack(s, 'Heroic Strike', () => s.weaponRoll(sw.w) + s.ap() / 14 * sw.w.speed + W.heroicStrike.flat);
    },
  });
}

// Bloodrage + Execute + Recklessness handled the same way in both kits.
function offGcd(sim, W) {
  const now = sim.now;
  const b = sim.kitBuild;
  if (b && b.improvedBerserkerRage > 0) {
    sim.sBZ = sim.sBZ || sim.addSpell({ name: 'Berserker Rage', cost: () => 0, cd: W.berserkerRage.cd });
    if (now >= sim.sBZ.readyAt) { sim.sBZ.readyAt = now + W.berserkerRage.cd; sim.entry('Berserker Rage').casts++; sim.gainRage(W.improvedBerserkerRage.ragePerRank * b.improvedBerserkerRage); }
  }
  if (now >= sim.sBR.readyAt) {
    sim.sBR.readyAt = now + W.bloodrage.cd; sim.entry('Bloodrage').casts++;
    sim.gainRage(W.bloodrage.immediate);
    const ticks = W.bloodrage.overTimeSec;
    for (let i = 1; i <= ticks; i++) sim.schedule(i, () => sim.gainRage(W.bloodrage.overTime / ticks));
  }
}

function executePhase(sim, W) {
  if (!sim.canCast(sim.sEX)) return null;
  return castGcd(sim, sim.sEX, () => {
    sim.spendRage(sim.sEX.cost());
    const extra = sim.rage; sim.rage = 0;
    yellowAttack(sim, 'Execute', () => W.execute.base + W.execute.perRage * extra);
  });
}

// =============================== FURY ===============================
export function furyKit(build = {}, data = null) {
  const b = Object.assign({}, FURY_DEFAULT_BUILD, build), W = warriorFromData(data);
  return {
    name: 'warrior_fury', build: b, W,
    setup(sim) {
      commonSetup(sim, b, W);
      const mods = sim.mods;
      if (sim.player.dualWield) {
        mods.ohDmgBonus = W.dualWieldSpec.ohDmgPerRank * b.dualWieldSpec;
        mods.ohHitBonus = W.dualWieldSpec.ohHitPerRank * b.dualWieldSpec;
      }
      if (b.enrage > 0 && b.enrageUptime > 0) mods.dmgMult *= 1 + W.enrage.dmgPerRank * b.enrage * b.enrageUptime;
      const twoHanded = !sim.player.dualWield && sim.player.weapons[0] && sim.player.weapons[0].twoHand;
      sim._norm = twoHanded ? W.whirlwind.normSpeed2H : W.whirlwind.normSpeed1H;
      sim.twoHanded = twoHanded;

      sim.deathWishAura = sim.addAura({ name: 'Death Wish', duration: W.deathWish.duration, mods: { dmgMult: W.deathWish.dmgMult } });
      sim.flurryAura = sim.addAura({ name: 'Flurry', duration: W.flurry.expire, mods: { hasteMult: 1 + W.flurry.perRank * b.flurry } });
      sim.flurryAura.charges = 0;
      sim.sBT = sim.addSpell({ name: 'Bloodthirst', cost: () => W.bloodthirst.cost, cd: W.bloodthirst.cd });
      sim.sWW = sim.addSpell({ name: 'Whirlwind', cost: () => W.whirlwind.cost, cd: W.whirlwind.cd });
      sim.sDW = sim.addSpell({ name: 'Death Wish', cost: () => W.deathWish.cost, cd: W.deathWish.cd });

      const consume = (s) => { const a = s.flurryAura; if (a.active && --a.charges <= 0) a.expire(); };
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (isWhite) consume(s);
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (outcome === 'crit' && b.flurry > 0) { s.flurryAura.charges = W.flurry.charges; s.flurryAura.apply(1); }
        if (isWhite && b.unbridledWrath > 0 && s.rng() < W.unbridledWrath.chancePerRank * b.unbridledWrath) s.gainRage(twoHanded ? 2 : 1);
      });
    },
    rotate(sim) {
      const now = sim.now;
      offGcd(sim, W);
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      if (b.useDeathWish && b.deathWish && sim.canCast(sim.sDW)) return castGcd(sim, sim.sDW, () => { sim.spendRage(W.deathWish.cost); sim.deathWishAura.apply(); });
      if (b.useRecklessness && now >= sim.sRK.readyAt) return castGcd(sim, sim.sRK, () => sim.reckAura.apply());
      if (b.executePhase && sim.inExecute()) { const w = executePhase(sim, W); if (w !== null) return w; }
      if (b.bloodthirst && sim.canCast(sim.sBT)) return castGcd(sim, sim.sBT, () => {
        sim.spendRage(W.bloodthirst.cost);
        yellowAttack(sim, 'Bloodthirst', () => sim.ap() * W.bloodthirst.apCoeff + W.bloodthirst.flat);
      });
      if (sim.canCast(sim.sWW)) return castGcd(sim, sim.sWW, () => {
        sim.spendRage(W.whirlwind.cost);
        const mh = sim.player.weapons[0];
        yellowAttack(sim, 'Whirlwind', () => sim.weaponRoll(mh) + sim.ap() / 14 * sim._norm + W.whirlwind.flat);
        if (b.ragingBlows && sim.player.dualWield) {
          const oh = sim.player.weapons[1];
          yellowAttack(sim, 'Whirlwind (Raging Blows)', () => (sim.weaponRoll(oh) + sim.ap() / 14 * sim._norm) * (0.5 + (sim.mods.ohDmgBonus || 0)));
        }
      });
      const reserve = ((sim.sBT.readyAt - now) < 1.5 ? W.bloodthirst.cost : 0) + ((sim.sWW.readyAt - now) < 1.5 ? W.whirlwind.cost : 0) + b.hsRageReserve;
      if (!sim.mhQueued && sim.rage >= sim.sHS.cost() + reserve && sim.player.weapons.length) sim.mhQueued = sim.sHS;
      return Math.max(0.05, Math.min(sim.sBT.readyAt, sim.sWW.readyAt, sim.sDW.readyAt, sim.sBR.readyAt) - now);
    },
  };
}

// =============================== ARMS ===============================
export function armsKit(build = {}, data = null) {
  const b = Object.assign({}, ARMS_DEFAULT_BUILD, build), W = warriorFromData(data);
  return {
    name: 'warrior_arms', build: b, W,
    setup(sim) {
      commonSetup(sim, b, W);
      const mods = sim.mods, mh = sim.player.weapons[0] || {};
      sim.twoHanded = !!mh.twoHand;
      if (sim.twoHanded) mods.dmgMult *= 1 + W.twoHandSpec.dmgPerRank * b.twoHandSpec;
      mods.critDmgBonus += W.impale.critDmgPerRank * b.impale;
      // Weaponmaster (Forever): axe/polearm +5% crit; mace/staff ignore 15% armor; sword 5% extra attack.
      if (b.weaponmaster) {
        const t = mh.type || '', r = b.weaponmaster, wm = W.weaponmaster;
        if (/axe|polearm/.test(t)) mods.critBonus += wm.axeCritPerRank * r;
        if (/mace|staff/.test(t)) sim.dr = sim.dr * (1 - wm.maceArmorPerRank * r);   // approximation: x% less armor mitigation
        sim.swordExtraAttack = /sword/.test(t) ? wm.swordExtraAttackPerRank * r : 0;
      }
      if (b.enrage > 0 && b.enrageUptime > 0) mods.dmgMult *= 1 + W.enrage.dmgPerRank * b.enrage * b.enrageUptime;
      sim.sMS = sim.addSpell({ name: 'Mortal Strike', cost: () => W.mortalStrike.cost, cd: W.mortalStrike.cd });
      sim.sOP = sim.addSpell({ name: 'Overpower', cost: () => W.overpower.cost, cd: W.overpower.cd });
      sim.sSL = sim.addSpell({ name: 'Slam', cost: () => W.slam.cost, cd: 0 });
      sim.sRD = sim.addSpell({ name: 'Rend', cost: () => W.rend.cost, cd: 0 });
      sim.rendEndsAt = -1;
      sim.slamUntil = -1;
      // Deep Wounds: a crit applies a bleed worth (20% x ranks) of the average weapon damage over 12 s (refreshes, no stacking).
      sim.deepWoundsAt = -1; sim.deepWoundsTick = 0;
      const applyDeepWounds = (s) => {
        const total = (mh.min + mh.max) / 2 * W.deepWounds.pctPerRank * b.deepWounds * 1.0;
        const ticks = Math.round(W.deepWounds.duration / W.deepWounds.tick);
        const per = total / ticks; s.deepWoundsAt = s.now + W.deepWounds.duration;
        const my = ++s.deepWoundsTick;
        for (let i = 1; i <= ticks; i++) s.schedule(i * W.deepWounds.tick, () => { if (s.deepWoundsTick === my && s.now <= s.deepWoundsAt + 1e-9) s.record('Deep Wounds', per * s.mods.dmgMult, 'hit'); });
      };
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (outcome === 'crit' && b.deepWounds > 0) applyDeepWounds(s);
        if (isWhite && b.unbridledWrath > 0 && s.rng() < W.unbridledWrath.chancePerRank * b.unbridledWrath) s.gainRage(sim.twoHanded ? 2 : 1);
        if (isWhite && s.swordExtraAttack && outcome !== 'glance' && s.rng() < s.swordExtraAttack) s.whiteAttack(s.swings[0]);
      });
      if (b.angerManagement) {
        const tick = () => { sim.gainRage(W.angerManagement.amount); sim.schedule(W.angerManagement.interval, tick); };
        sim.schedule(W.angerManagement.interval, tick);
      }
    },
    rotate(sim) {
      const now = sim.now, mh = sim.player.weapons[0], norm = sim.twoHanded ? W.whirlwind.normSpeed2H : 2.4;
      offGcd(sim, W);
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      if (b.useRecklessness && now >= sim.sRK.readyAt) return castGcd(sim, sim.sRK, () => sim.reckAura.apply());
      if (b.executePhase && sim.inExecute()) { const w = executePhase(sim, W); if (w !== null) return w; }
      if (b.mortalStrike && sim.canCast(sim.sMS)) return castGcd(sim, sim.sMS, () => {
        sim.spendRage(W.mortalStrike.cost);
        yellowAttack(sim, 'Mortal Strike', () => sim.weaponRoll(mh) + sim.ap() / 14 * W.mortalStrike.normSpeed2H + W.mortalStrike.flat);
      });
      if (now <= sim.overpowerUntil && sim.canCast(sim.sOP)) return castGcd(sim, sim.sOP, () => {
        sim.spendRage(W.overpower.cost); sim.overpowerUntil = -1;
        yellowAttack(sim, 'Overpower', () => sim.weaponRoll(mh) + sim.ap() / 14 * norm + W.overpower.flat,
          { canDodge: false, bonusCrit: W.improvedOverpower.critPerRank * (b.improvedOverpower || 0) });
      });
      if (b.useRend && now >= sim.rendEndsAt && sim.canCast(sim.sRD)) return castGcd(sim, sim.sRD, () => {
        sim.spendRage(W.rend.cost); sim.rendEndsAt = now + W.rend.duration;
        const ticks = Math.round(W.rend.duration / W.rend.tick), per = W.rend.total * (1 + W.improvedRend.bleedPerRank * (b.improvedRend || 0)) / ticks, my = sim.rendEndsAt;
        for (let i = 1; i <= ticks; i++) sim.schedule(i * W.rend.tick, () => { if (sim.rendEndsAt === my) sim.record('Rend', per * sim.mods.dmgMult, 'hit'); });
      });
      // Slam: a cast that resets the swing timer; only worth it right after the main-hand swing (weaving).
      if (b.useSlam && sim.canCast(sim.sSL) && sim.swings[0] && sim.swings[0].next - now > mh.speed * 0.55) {
        const cast = Math.max(0.1, W.slam.cast - W.improvedSlam.castReductionPerRank * (b.improvedSlam || 0));
        return castGcd(sim, sim.sSL, () => {
          sim.spendRage(W.slam.cost);
          yellowAttack(sim, 'Slam', () => sim.weaponRoll(mh) + sim.ap() / 14 * norm + W.slam.flat);
          // the swing timer restarts after the cast (Improved Slam removes this penalty)
          if (!(b.improvedSlam >= 2)) sim._scheduleSwing(sim.swings[0], cast + mh.speed / sim.hasteMult());
        });
      }
      const reserve = ((sim.sMS.readyAt - now) < 1.5 ? W.mortalStrike.cost : 0) + b.hsRageReserve;
      if (!sim.mhQueued && sim.rage >= sim.sHS.cost() + reserve && mh) sim.mhQueued = sim.sHS;
      return Math.max(0.05, Math.min(sim.sMS.readyAt, sim.sBR.readyAt, sim.overpowerUntil > now ? sim.sOP.readyAt : Infinity) - now);
    },
  };
}
