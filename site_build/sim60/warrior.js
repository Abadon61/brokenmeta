// Warrior spec kits (Fury first). Numbers come from WoW: Forever's own tooltips where we have them
// (data/wow_spells/warrior.json, data/wow_talents/warrior.json) and are marked ASSUMED where a
// Classic 1.12 value is kept until Forever's level-60 table is sourced.
import { GCD } from './constants.js';

// ---- Forever-sourced / assumed ability numbers (level 60, max rank) ----
export const WARRIOR = {
  bloodthirst: { cost: 30, cd: 6, apCoeff: 0.35, flat: 30 },          // talent text: "35% of your Attack Power plus 30"
  whirlwind: { cost: 25, cd: 10, normSpeed1H: 2.4, normSpeed2H: 3.3 }, // glossary: 100% normalized weapon damage (Classic normalization speeds, ASSUMED)
  heroicStrike: { cost: 15, flat: 157 },                              // glossary: flat bonus on next swing, rank 9
  execute: { cost: 15, base: 600, perRage: 15, cd: 0 },               // ASSUMED Classic rank 5 (600 + 15 per excess Rage); Forever value not sourced yet
  deathWish: { cost: 10, cd: 180, duration: 30, dmgMult: 1.2 },       // Forever tooltip: +20% Physical damage, 30 s, 3 min cooldown
  recklessness: { cost: 0, cd: 1800, duration: 15, crit: 1.0 },       // ASSUMED Classic (+100% crit 15 s, 30 min); future table has the spell at level 50
  bloodrage: { cd: 60, immediate: 10, overTime: 10, overTimeSec: 10 },// Forever tooltip (spell 2687)
  berserkerRage: { cd: 30 },
  flurry: { perRank: 0.05, charges: 3, expire: 15 },                  // Forever: +25% attack speed at 5/5 for 3 swings after a melee crit
  unbridledWrath: { chancePerRank: 0.12 },                            // Forever: 60% at 5/5, +1 Rage (2 with a two-hander)
  dualWieldSpec: { ohDmgPerRank: 0.05, ohHitPerRank: 0.02 },          // Forever: +25% OH damage and +10% OH hit at 5/5 (off-hand base 50%)
  cruelty: { critPerRank: 0.01 },
  precision: { hitPerRank: 0.01 },
  improvedHeroicStrike: { costPerRank: 1 },
  improvedExecute: { costPerRank: 2.5 },                              // Forever: -5 Rage over 2 ranks
  boundlessRage: { capPerRank: 10 },
  angerManagement: { interval: 3, amount: 1 },
};

// Rotation options & talent ranks arrive in cfg.build. Defaults model a typical raiding Fury build.
export const FURY_DEFAULT_BUILD = {
  cruelty: 5, unbridledWrath: 5, dualWieldSpec: 5, flurry: 5, precision: 3, improvedHeroicStrike: 3,
  improvedExecute: 2, boundlessRage: 3, ragingBlows: 1, bloodthirst: 1, deathWish: 1, angerManagement: 0,
  enrageUptime: 0.0,            // Enrage needs incoming damage; 0 = off unless the user enters an expected uptime
  hsRageReserve: 0,             // extra Rage kept back before queueing Heroic Strike (rotation knob)
  useRecklessness: true, useDeathWish: true, executePhase: true,
};

export function furyKit(build = {}) {
  const b = Object.assign({}, FURY_DEFAULT_BUILD, build);
  const W = WARRIOR;
  return {
    name: 'warrior_fury', build: b,
    setup(sim) {
      const mods = sim.mods;
      sim.player.resource = 'rage';
      sim.rageCap = 100 + W.boundlessRage.capPerRank * b.boundlessRage;
      mods.critBonus += W.cruelty.critPerRank * b.cruelty;
      mods.hitBonus += W.precision.hitPerRank * b.precision;
      if (sim.player.dualWield) {
        mods.ohDmgBonus = W.dualWieldSpec.ohDmgPerRank * b.dualWieldSpec;
        mods.ohHitBonus = W.dualWieldSpec.ohHitPerRank * b.dualWieldSpec;
      }
      if (b.enrageUptime > 0) mods.dmgMult *= 1 + 0.10 * b.enrageUptime;   // flat average, Enrage's "10% for 12 s"

      const twoHanded = !sim.player.dualWield && sim.player.weapons[0] && sim.player.weapons[0].twoHand;
      const norm = twoHanded ? W.whirlwind.normSpeed2H : W.whirlwind.normSpeed1H;

      // ---- auras ----
      sim.deathWishAura = sim.addAura({ name: 'Death Wish', duration: W.deathWish.duration, mods: { dmgMult: W.deathWish.dmgMult } });
      sim.reckAura = sim.addAura({ name: 'Recklessness', duration: W.recklessness.duration, mods: { critBonus: W.recklessness.crit } });
      sim.flurryAura = sim.addAura({ name: 'Flurry', duration: W.flurry.expire,
        mods: { hasteMult: 1 + W.flurry.perRank * b.flurry } });
      // Flurry is a haste aura with 3 "charges": one is consumed per swing, a fresh crit refills all 3.
      sim.flurryAura.charges = 0;

      // ---- spells ----
      const hsCost = () => Math.max(0, W.heroicStrike.cost - W.improvedHeroicStrike.costPerRank * b.improvedHeroicStrike);
      const execCost = () => Math.max(0, W.execute.cost - W.improvedExecute.costPerRank * b.improvedExecute);

      sim.sBT = sim.addSpell({ name: 'Bloodthirst', cost: () => W.bloodthirst.cost, cd: W.bloodthirst.cd });
      sim.sWW = sim.addSpell({ name: 'Whirlwind', cost: () => W.whirlwind.cost, cd: W.whirlwind.cd });
      sim.sEX = sim.addSpell({ name: 'Execute', cost: execCost, cd: 0 });
      sim.sDW = sim.addSpell({ name: 'Death Wish', cost: () => W.deathWish.cost, cd: W.deathWish.cd });
      sim.sRK = sim.addSpell({ name: 'Recklessness', cost: () => 0, cd: W.recklessness.cd });
      sim.sBR = sim.addSpell({ name: 'Bloodrage', cost: () => 0, cd: W.bloodrage.cd });
      sim.sHS = sim.addSpell({
        name: 'Heroic Strike', cost: hsCost,
        onSwing(s, sw) {            // replaces the main-hand white swing
          s.spendRage(hsCost());
          const w = sw.w, out = s.resolveYellow();
          const e = s.entry('Heroic Strike'); e.casts++;
          if (out === 'miss') { e.misses++; s.onMeleeHit('miss', 'Heroic Strike', false, false); return; }
          if (out === 'dodge') { e.dodges++; s.overpowerUntil = s.now + 5; s.onMeleeHit('dodge', 'Heroic Strike', false, false); return; }
          let raw = s.weaponRoll(w) + s.ap() / 14 * w.speed + W.heroicStrike.flat;
          if (out === 'crit') raw *= s.critMult();
          const dmg = s.mitigate(raw * s.mods.dmgMult, true);
          s.record('Heroic Strike', dmg, out);
          s.onMeleeHit(out, 'Heroic Strike', false, false);
        },
      });

      // ---- procs ----
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (outcome === 'miss' || outcome === 'dodge') {
          if (isWhite) flurryConsume(s);
          return;
        }
        if (isWhite) flurryConsume(s);
        if (outcome === 'crit' && b.flurry > 0) { s.flurryAura.charges = W.flurry.charges; s.flurryAura.apply(1); }
        if (isWhite && b.unbridledWrath > 0 && s.rng() < W.unbridledWrath.chancePerRank * b.unbridledWrath) {
          s.gainRage(twoHanded ? 2 : 1);
        }
      });
      function flurryConsume(s) {
        const a = s.flurryAura;
        if (!a.active) return;
        a.charges--;
        if (a.charges <= 0) a.expire();
      }

      sim.executeDamage = function (rageLeft) {
        return W.execute.base + W.execute.perRage * rageLeft;
      };
      sim._norm = norm;
    },

    start(sim) {
      // Pre-pull: Bloodrage on cooldown from t=0 (off the GCD).
      sim.bloodrageTick = null;
    },

    // Priority list. Returns seconds until the next useful re-check (or null to wait for an event).
    rotate(sim) {
      const W2 = WARRIOR, now = sim.now;
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      // Off-GCD: Bloodrage.
      if (now >= sim.sBR.readyAt) {
        sim.sBR.readyAt = now + W2.bloodrage.cd; sim.entry('Bloodrage').casts++;
        sim.gainRage(W2.bloodrage.immediate);
        const ticks = W2.bloodrage.overTimeSec;
        for (let i = 1; i <= ticks; i++) sim.schedule(i, () => sim.gainRage(W2.bloodrage.overTime / ticks));
      }
      if (gcdLeft > 0) return gcdLeft;

      const cast = (spell, fn) => { sim.startGcd(); spell.readyAt = now + spell.cd; spell.casts++; sim.entry(spell.name).casts++; fn(); return sim.gcdReadyAt - now; };
      const yellow = (name, rawFn, opts = {}) => {
        const out = sim.resolveYellow(0, opts.canDodge !== false);
        const e = sim.entry(name);
        if (out === 'miss') { e.misses++; sim.onMeleeHit('miss', name, false, false); return out; }
        if (out === 'dodge') { e.dodges++; sim.overpowerUntil = now + 5; sim.onMeleeHit('dodge', name, false, false); return out; }
        let raw = rawFn(); if (out === 'crit') raw *= sim.critMult();
        const dmg = sim.mitigate(raw * sim.mods.dmgMult, true);
        sim.record(name, dmg, out); sim.onMeleeHit(out, name, false, false);
        return out;
      };

      // Cooldowns first.
      if (b.useDeathWish && sim.canCast(sim.sDW)) {
        return cast(sim.sDW, () => { sim.spendRage(W2.deathWish.cost); sim.deathWishAura.apply(); });
      }
      if (b.useRecklessness && sim.now >= sim.sRK.readyAt && now >= sim.gcdReadyAt) {
        return cast(sim.sRK, () => { sim.reckAura.apply(); });
      }
      const exec = b.executePhase && sim.inExecute();
      // Execute phase: Execute is the main button.
      if (exec && sim.rage >= sim.sEX.cost()) {
        return cast(sim.sEX, () => {
          const cost = sim.sEX.cost(); sim.spendRage(cost);
          const extra = Math.max(0, sim.rage - 0); sim.rage = 0;
          yellow('Execute', () => sim.executeDamage(extra));
        });
      }
      // Bloodthirst, then Whirlwind.
      if (sim.canCast(sim.sBT)) {
        return cast(sim.sBT, () => {
          sim.spendRage(W2.bloodthirst.cost);
          yellow('Bloodthirst', () => sim.ap() * W2.bloodthirst.apCoeff + W2.bloodthirst.flat);
        });
      }
      if (sim.canCast(sim.sWW)) {
        return cast(sim.sWW, () => {
          sim.spendRage(W2.whirlwind.cost);
          const mh = sim.player.weapons[0];
          yellow('Whirlwind', () => sim.weaponRoll(mh) + sim.ap() / 14 * sim._norm);
          if (b.ragingBlows && sim.player.dualWield) {
            const oh = sim.player.weapons[1];
            yellow('Whirlwind (Raging Blows)', () => (sim.weaponRoll(oh) + sim.ap() / 14 * sim._norm) * (0.5 + (sim.mods.ohDmgBonus || 0)));
          }
        });
      }
      // Heroic Strike: queue only on spare Rage (keep BT/WW affordable when they are about to come off cooldown).
      const reserve = ((sim.sBT.readyAt - now) < 1.5 ? W2.bloodthirst.cost : 0) + ((sim.sWW.readyAt - now) < 1.5 ? W2.whirlwind.cost : 0) + b.hsRageReserve;
      if (!sim.mhQueued && sim.rage >= sim.sHS.cost() + reserve && sim.player.weapons.length) sim.mhQueued = sim.sHS;
      // Wait for the next event that can change the decision.
      const t = Math.min(sim.sBT.readyAt, sim.sWW.readyAt, sim.sDW.readyAt, sim.sBR.readyAt);
      return Math.max(0.05, t - now);
    },
  };
}
