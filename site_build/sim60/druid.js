// Druid kits. Balance: Wrath, Starfire, Moonfire and Insect Swarm from the client's rank ladders (data/spells60.json: top / extra) and the
// Forever talent tooltips (Eclipse, Nature's Grace, Moonfury...). ASSUMED (Classic style): base mana, mana items, the Moonkin Aura crit
// applied to the druid itself. Not simulated: Omen of Clarity, Hurricane, Starfall-style effects.
import { makeCaster, fromRank, pickRank } from './caster.js';
import { dotActive, dotLeft } from './spells.js';

export const DRUID = {
  improvedWrath: { cast: 0.1, cost: 0.10 }, genesis: { dmg: 0.01 }, moonglow: { cost: 0.25 / 3 }, improvedMoonfire: { dmg: 0.05, crit: 0.05 }, naturesMajesty: { crit: 0.02 },
  naturesReach: { hit: 0.02 }, naturesSplendor: { moonfire: 1, swarm: 1 }, vengeance: { critBonus: 0.2 }, improvedStarfire: { cast: 0.1 }, naturesGrace: { haste: 1.1, dur: 3 },
  naturalist: { dmg: 0.01 }, eclipse: { cast: 0.5, charges: 2, max: 4, dur: 15 }, moonfury: { dmg: 0.02 }, moonkinAura: { crit: 0.03 },
  manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

export const DRUID_BAL_DEFAULT_BUILD = {
  improvedWrath: 0, genesis: 0, moonglow: 0, improvedMoonfire: 0, naturesMajesty: 0, naturesReach: 0, naturesSplendor: 0, insectSwarm: 0, vengeance: 0, improvedStarfire: 0,
  naturesGrace: 0, eclipse: 0, moonfury: 0, moonkinForm: 0, naturalist: 0,
  useCooldowns: true, usePotion: true, useGem: true,
};

export function druidBalanceKit(build = {}, data = null) {
  const b = Object.assign({}, DRUID_BAL_DEFAULT_BUILD, build), D = DRUID;
  const wr = pickRank(data, 'druid', 'druid_wrath', 'Wrath'), sf = pickRank(data, 'druid', null, 'Starfire'), mf = pickRank(data, 'druid', 'druid_moonfire', 'Moonfire'), isw = pickRank(data, 'druid', null, 'Insect Swarm');
  const S = {};
  if (wr) S.wrath = fromRank(wr, { name: 'Wrath', schools: ['nature'], wrath: true });
  if (sf) S.starfire = fromRank(sf, { name: 'Starfire', schools: ['arcane'], starfire: true });
  if (mf) S.moonfire = fromRank(mf, { name: 'Moonfire', schools: ['arcane'], instant: true, moonfire: true });
  if (isw) S.swarm = fromRank(isw, { name: 'Insect Swarm', schools: ['nature'], instant: true, swarm: true });
  const def = {
    name: 'druid_balance', build: b, S,
    items: { potion: D.manaPotion, gem: D.manaGem },
    baseMana: (sim) => sim.stats.mana,
    keep: () => 0,
    setup(sim) {
      sim.aGrace = sim.addAura({ name: "Nature's Grace", duration: D.naturesGrace.dur, mods: { hasteMult: D.naturesGrace.haste } });
      sim.aEclipse = sim.addAura({ name: 'Eclipse', duration: D.eclipse.dur, maxStacks: D.eclipse.max });
      sim.critBase = D.naturesMajesty.crit * b.naturesMajesty + (b.moonkinForm ? D.moonkinAura.crit : 0);
      sim.spBonus = 0;
    },
    mods(sim, s, kind) {
      let hit = D.naturesReach.hit * b.naturesReach, crit = sim.critBase, dmg = 1, critBonus = D.vengeance.critBonus * b.vengeance;
      dmg *= (1 + D.moonfury.dmg * b.moonfury) * (1 + D.naturalist.dmg * b.naturalist);
      if (kind === 'dot') dmg *= 1 + D.genesis.dmg * b.genesis;
      if (s.moonfire) { dmg *= 1 + D.improvedMoonfire.dmg * b.improvedMoonfire; crit += D.improvedMoonfire.crit * b.improvedMoonfire; }
      return { hit, crit, dmg, critBonus };
    },
    castTime(sim, s) {
      let t = s.cast;
      if (s.wrath) t -= D.improvedWrath.cast * b.improvedWrath;
      if (s.starfire) { t -= D.improvedStarfire.cast * b.improvedStarfire; if (sim.aEclipse.active) t -= D.eclipse.cast; }
      return Math.max(0.5, t);
    },
    cost(sim, s) {
      let c = s.cost;
      if (s.wrath) c *= 1 - D.improvedWrath.cost * b.improvedWrath;
      c *= 1 - D.moonglow.cost * b.moonglow;
      return Math.round(c);
    },
    beforeCast(sim, s) { if (s.starfire && sim.aEclipse.active) sim.aEclipse.consumeStack(); },
    afterHit(sim, s, outcome) {
      if (outcome === 'miss') return;
      if (s.wrath && b.eclipse) sim.aEclipse.apply(D.eclipse.charges);
      if (outcome === 'crit' && !s.dot && b.naturesGrace) sim.aGrace.apply();
    },
    choose(sim) {
      const now = sim.now, rem = sim.fightLen - now;
      if (S.swarm && b.insectSwarm && rem > 6 && dotLeft(sim, S.swarm.name) < 0.8) return S.swarm;
      if (S.moonfire && rem > 6 && dotLeft(sim, S.moonfire.name) < 0.8) return S.moonfire;
      if (sim.aEclipse.active && S.starfire) return S.starfire;
      return S.wrath;
    },
  };
  if (S.moonfire) S.moonfire.dotTicks = () => S.moonfire.dot.ticks + D.naturesSplendor.moonfire * b.naturesSplendor * 1;
  if (S.swarm) S.swarm.dotTicks = () => S.swarm.dot.ticks + b.naturesSplendor;
  return makeCaster(def);
}

// ---------------------------------------------------------------------------------------------------------------------------
// Feral (cat): energy and combo points like the Rogue, Claw / Shred / Rake as builders, Rip and Ferocious Bite as finishers. Numbers from
// the client's rank ladders (Claw, Shred, Rake, Rip, Ferocious Bite) and the Forever talent tooltips. ASSUMED (Classic style): the cat's
// natural weapon (speed 1.0, 17-25 damage), attack power from Strength and Agility (2 per Strength, 1 per Agility), 20 energy per 2 s,
// being behind the target for Shred. Not simulated: Berserk, Tiger's Fury, Primal Bite, Swipe, Ravage, feral weapon attack power.
import { yellowAttack, castGcd } from './shared.js';

export const DRUID_FERAL = {
  energy: { cap: 100, tick: 2, perTick: 20 }, natural: { min: 17, max: 25, speed: 1.0 },
  claw: { cost: 45, flat: 115, pct: 1.10 }, shred: { cost: 60, flat: 80, pct: 1.55 }, rake: { cost: 40, direct: 61, tick: 34, ticks: 3, interval: 3 },
  rip: { cost: 30, base: 15, perCp: 25.5, ticks: 6, interval: 2 }, bite: { cost: 35, base: 82, var: 0.73, perCp: 147 },
  ferocity: { cost: 1 }, shreddingAttacks: { cost: 6 }, savageFury: { dmg: 0.05 }, sharpenedClaws: { crit: 0.03 }, predatoryStrikes: { ap: 30 }, predatoryInstincts: { critDmg: 0.1 },
  rendAndTear: { dmg: 0.02 }, heartOfTheWild: { str: 0.02 }, leaderOfThePack: { crit: 0.03 }, naturesMajesty: { crit: 0.02 },
};

export const DRUID_FERAL_DEFAULT_BUILD = {
  ferocity: 0, shreddingAttacks: 0, savageFury: 0, sharpenedClaws: 0, predatoryStrikes: 0, predatoryInstincts: 0, rendAndTear: 0, heartOfTheWild: 0, leaderOfThePack: 0, naturesMajesty: 0,
  behind: true,
};

export function druidFeralKit(build = {}, data = null) {
  const b = Object.assign({}, DRUID_FERAL_DEFAULT_BUILD, build), F = JSON.parse(JSON.stringify(DRUID_FERAL));
  const cl = pickRank(data, 'druid', 'druid_claw', 'Claw'), sh = pickRank(data, 'druid', null, 'Shred'), rk = pickRank(data, 'druid', null, 'Rake'), rp = pickRank(data, 'druid', 'druid_rip', 'Rip'), fb = pickRank(data, 'druid', null, 'Ferocious Bite');
  const eff = (r, e, a) => r && r.effects.find((x) => x.effect === e && (a === undefined || x.aura === a));
  if (cl) { F.claw.cost = cl.cost.amount; F.claw.flat = eff(cl, 58).base; F.claw.pct = eff(cl, 31).base / 100; }
  if (sh) { F.shred.cost = sh.cost.amount; F.shred.flat = eff(sh, 58).base; F.shred.pct = eff(sh, 31).base / 100; }
  if (rk) { F.rake.cost = rk.cost.amount; F.rake.direct = eff(rk, 2).base; const d = eff(rk, 6, 3); F.rake.tick = d.base; F.rake.interval = d.period_ms / 1000; F.rake.ticks = Math.round(rk.duration_ms / d.period_ms); }
  if (rp) { F.rip.cost = rp.cost.amount; const d = eff(rp, 6, 3); F.rip.base = d.base; F.rip.perCp = d.per_resource; F.rip.interval = d.period_ms / 1000; F.rip.ticks = Math.round(rp.duration_ms / d.period_ms); }
  if (fb) { F.bite.cost = fb.cost.amount; const d = eff(fb, 2); F.bite.base = d.base; F.bite.var = d.variance; F.bite.perCp = d.per_resource; }
  return {
    name: 'druid_feral', build: b, F,
    setup(sim) {
      sim.player.resource = 'energy'; sim.kitBuild = b;
      const mods = sim.mods;
      sim.player = Object.assign({}, sim.player, { weapons: [{ min: F.natural.min, max: F.natural.max, speed: F.natural.speed, type: '' }], dualWield: false });
      mods.apBonus += F.predatoryStrikes.ap * b.predatoryStrikes + Math.floor((sim.stats.str || 0) * F.heartOfTheWild.str * b.heartOfTheWild) * 2;
      mods.critBonus += F.sharpenedClaws.crit * b.sharpenedClaws + F.leaderOfThePack.crit * b.leaderOfThePack + F.naturesMajesty.crit * b.naturesMajesty;
      mods.critDmgBonus = F.predatoryInstincts.critDmg * b.predatoryInstincts;
      sim.rageCap = F.energy.cap; sim.cp = 0; sim.ripUntil = 0; sim.rakeUntil = 0;
      const tick = () => { sim.gainRage(F.energy.perTick); sim.nextTick = sim.now + F.energy.tick; sim.schedule(F.energy.tick, tick); };
      sim.nextTick = F.energy.tick; sim.schedule(F.energy.tick, tick);
      sim.bleeding = () => sim.now < sim.ripUntil || sim.now < sim.rakeUntil;
    },
    start(sim) { sim.rage = sim.rageCap; },
    rotate(sim) {
      const now = sim.now, rem = sim.fightLen - now, energy = sim.rage, gcd = 1.0;
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      const wait = Math.max(0.05, sim.nextTick - now);
      const dmg = (isBuilder) => (1 + (isBuilder ? F.savageFury.dmg * b.savageFury : 0)) * (1 + (sim.bleeding() ? F.rendAndTear.dmg * b.rendAndTear : 0));
      const spell = (name) => ({ name, cd: 0, readyAt: 0, casts: 0 });
      const addCp = (o) => { if (o !== 'miss' && o !== 'dodge') sim.cp = Math.min(5, sim.cp + 1); };
      const mh = sim.player.weapons[0];
      const nearEnd = rem < 4;
      // finishers at five combo points (or a few at the very end)
      if ((sim.cp >= 5 || (nearEnd && sim.cp >= 3)) && energy >= Math.min(F.rip.cost, F.bite.cost)) {
        const ripDown = now >= sim.ripUntil - 1.0;
        if (ripDown && rem > 8 && energy >= F.rip.cost) {
          return castGcd(sim, spell('Rip'), () => {
            const cp = sim.cp; sim.spendRage(F.rip.cost); sim.cp = 0;
            const e = sim.entry('Rip'), out = sim.resolveYellow(0, true);
            if (out === 'miss' || out === 'dodge') { e.misses++; return; }
            const per = F.rip.base + F.rip.perCp * cp;
            sim.ripUntil = now + F.rip.ticks * F.rip.interval;
            const my = (sim.ripToken = (sim.ripToken || 0) + 1); let n = 0;
            const critP = sim.critChance(0), cm = sim.critMult(sim.mods.critDmgBonus);
            const step = () => { if (sim.ripToken !== my) return; const c = sim.rng() < critP; sim.record('Rip', per * sim.mods.dmgMult * (c ? cm : 1) * (1 - sim.dr), c ? 'crit' : 'hit'); if (++n < F.rip.ticks) sim.schedule(F.rip.interval, step); };
            sim.schedule(F.rip.interval, step);
          }, gcd);
        }
        if (energy >= F.bite.cost) {
          return castGcd(sim, spell('Ferocious Bite'), () => {
            const cp = sim.cp; sim.spendRage(F.bite.cost); sim.cp = 0;
            yellowAttack(sim, 'Ferocious Bite', () => (F.bite.base * (1 + F.bite.var * (sim.rng() - 0.5)) + F.bite.perCp * cp) * dmg(false), { critDmgBonus: sim.mods.critDmgBonus });
          }, gcd);
        }
      }
      if (sim.cp >= 5) return wait;
      // builders: Rake when it is down, then Shred (behind the target) or Claw
      const rakeCost = Math.max(10, F.rake.cost - F.ferocity.cost * b.ferocity), clawCost = Math.max(10, F.claw.cost - F.ferocity.cost * b.ferocity), shredCost = Math.max(10, F.shred.cost - F.shreddingAttacks.cost * b.shreddingAttacks);
      if (now >= sim.rakeUntil - 0.5 && rem > 6 && energy >= rakeCost) {
        return castGcd(sim, spell('Rake'), () => {
          sim.spendRage(rakeCost);
          const o = yellowAttack(sim, 'Rake', () => F.rake.direct * dmg(true), { critDmgBonus: sim.mods.critDmgBonus });
          addCp(o);
          if (o !== 'miss' && o !== 'dodge') {
            sim.rakeUntil = now + F.rake.ticks * F.rake.interval;
            const my = (sim.rakeToken = (sim.rakeToken || 0) + 1); let n = 0;
            const step = () => { if (sim.rakeToken !== my) return; sim.record('Rake (bleed)', F.rake.tick * sim.mods.dmgMult * (1 - sim.dr) * (1 + F.savageFury.dmg * b.savageFury), 'hit'); if (++n < F.rake.ticks) sim.schedule(F.rake.interval, step); };
            sim.schedule(F.rake.interval, step);
          }
        }, gcd);
      }
      if (b.behind && energy >= shredCost) return castGcd(sim, spell('Shred'), () => { sim.spendRage(shredCost); addCp(yellowAttack(sim, 'Shred', () => (sim.weaponRoll(mh) + sim.ap() / 14 * F.natural.speed + F.shred.flat) * F.shred.pct * dmg(true), { critDmgBonus: sim.mods.critDmgBonus })); }, gcd);
      if (!b.behind && energy >= clawCost) return castGcd(sim, spell('Claw'), () => { sim.spendRage(clawCost); addCp(yellowAttack(sim, 'Claw', () => (sim.weaponRoll(mh) + sim.ap() / 14 * F.natural.speed + F.claw.flat) * F.claw.pct * dmg(true), { critDmgBonus: sim.mods.critDmgBonus })); }, gcd);
      return wait;
    },
  };
}
