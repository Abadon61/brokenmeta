// Rogue kit (Combat / Assassination / Subtlety share one single-target rotation; the specs differ by
// talents and by the builder they use). Numbers are WoW: Forever's own where we have them (glossary at
// level 60 in data/spells60.json, talent tooltips in data/talents.json); ASSUMED = Classic value kept
// until Forever's table is sourced. Poisons: Forever has no poison table yet, so the damage, proc chances
// and the spell-hit roll are Classic 1.12 values (ASSUMED); only the talent effects come from Forever
// (Improved Poisons, Vile Poisons, Malice on poisons, Mutilate vs poisoned). Not modeled: poison charges,
// Venom, Improved Kidney Shot.
import { yellowAttack, castGcd } from './shared.js';

export const ROGUE = {
  sinisterStrike: { cost: 45, flat: 68, pct: 1.0 },
  backstab: { cost: 60, flat: 150, pct: 1.5 },
  eviscerate: { cost: 35, table: { 1: [224, 332], 2: [394, 502], 3: [564, 672], 4: [734, 842], 5: [904, 1012] } },
  sliceAndDice: { cost: 25, base: 6, perPoint: 3, haste: 1.2 },
  hemorrhage: { cost: 35, pct: 1.0, pctDagger: 1.45 },          // cost ASSUMED (Classic); damage from the Forever talent tooltip
  mutilate: { cost: 60, pct: 0.75, flat: 17.2, cp: 2 },         // client table + talent tooltip
  bladeFlurry: { cost: 25, cd: 120, duration: 15, haste: 1.2 },  // cost/cooldown ASSUMED (Classic)
  adrenalineRush: { cd: 300, duration: 15, regenMult: 2 },      // cooldown ASSUMED (Classic)
  coldBlood: { cd: 180 },                                       // cooldown ASSUMED (Classic)
  energy: { cap: 100, tick: 2, perTick: 20 },
  normSpeed: { other: 2.4, dagger: 1.7 },                       // Classic weapon-speed normalization (ASSUMED)
  // talents (per rank, from the Forever tooltips)
  improvedSinisterStrike: { costPerRank: 3 }, improvedEviscerate: { perRank: 0.07 }, flawlessExecution: { cost: 10 },
  aggression: { perRank: 0.02 }, malice: { critPerRank: 0.01 }, lethality: { critDmgPerRank: 0.04 },
  precision: { hitPerRank: 0.01 }, dualWieldSpec: { ohPerRank: 0.05 }, relentlessStrikes: { chancePerCp: 0.2, energy: 25 },
  ruthlessness: { perRank: 0.2 }, sealFate: { perRank: 0.2 }, vigor: { perRank: 5 }, improvedSliceAndDice: { perRank: 0.15 },
  hackAndSlash: { perRank: 0.01, armorPerRank: 0.03 }, weaponExpertise: { dodgePerRank: 0.01 },
  opportunity: { perRank: 0.05 }, quietus: { perRank: 0.02, below: 0.35 }, serratedBlades: { armorPerRank: 0.03 },
  puncturingWounds: { bsCritPerRank: 0.10, mutCritPerRank: 0.05 },
  // poisons: Classic 1.12 rank VII / V (ASSUMED). Nature damage: no armor, no AP scaling, 1.5x on crit, resisted like a spell.
  poison: { resist: 0.17, critMult: 1.5, mutilateBonus: 1.2 },
  instantPoison: { min: 146, max: 194, chance: 0.20 },
  deadlyPoison: { total: 136, duration: 12, tick: 3, maxStacks: 5, chance: 0.30 },
  improvedPoisons: { chancePerRank: 0.02 }, vilePoisons: { dmgPerRank: 0.04 },
};

export const ROGUE_DEFAULT_BUILD = {
  improvedSinisterStrike: 2, improvedEviscerate: 3, precision: 3, dualWieldSpec: 5, flawlessExecution: 1, bladeFlurry: 1, hackAndSlash: 5,
  weaponExpertise: 2, aggression: 3, adrenalineRush: 1, malice: 5, lethality: 5, ruthlessness: 3, relentlessStrikes: 1, improvedSliceAndDice: 3,
  sealFate: 0, vigor: 0, coldBlood: 0, mutilate: 0, hemorrhage: 0, opportunity: 0, quietus: 0, serratedBlades: 0, puncturingWounds: 0,
  improvedPoisons: 0, vilePoisons: 0, mhPoison: 'instant', ohPoison: 'deadly',   // 'instant' | 'deadly' | 'none'
  builder: 'auto', useCooldowns: true,
};

export function rogueKit(build = {}, data = null) {
  const b = Object.assign({}, ROGUE_DEFAULT_BUILD, build), R = JSON.parse(JSON.stringify(ROGUE));
  const a = data && data.rogue && data.rogue.abilities;
  if (a) {
    const ss = a.rogue_sinister_strike, bs = a.rogue_backstab, ev = a.rogue_eviscerate, sd = a.rogue_slice_and_dice;
    const nw = (x) => (x && x.effects || []).find((e) => e.kind === 'normalized_weapon_damage');
    if (nw(ss)) { R.sinisterStrike.flat = nw(ss).flat; R.sinisterStrike.pct = nw(ss).pct; R.sinisterStrike.cost = ss.resource_cost.energy; }
    if (nw(bs)) { R.backstab.flat = nw(bs).flat; R.backstab.pct = nw(bs).pct; R.backstab.cost = bs.resource_cost.energy; }
    const et = ev && ev.effects.find((e) => e.table); if (et) { R.eviscerate.table = et.table; R.eviscerate.cost = ev.resource_cost.energy; }
    const st = sd && sd.effects.find((e) => e.base !== undefined); if (st) { R.sliceAndDice.base = st.base; R.sliceAndDice.perPoint = st.per_point; R.sliceAndDice.cost = sd.resource_cost.energy; }
    const mu = (data.rogue.future || []).find((f) => f.name === 'Mutilate'); if (mu) R.mutilate.cost = mu.rank.cost.amount;
  }
  return {
    name: 'rogue', build: b, R,
    setup(sim) {
      sim.player.resource = 'energy'; sim.kitBuild = b;
      const mods = sim.mods, mh = sim.player.weapons[0] || {}, oh = sim.player.weapons[1];
      sim.rageCap = R.energy.cap + R.vigor.perRank * (b.vigor || 0);
      mods.critBonus += R.malice.critPerRank * b.malice;
      mods.hitBonus += R.precision.hitPerRank * b.precision;
      mods.ohDmgBonus = R.dualWieldSpec.ohPerRank * b.dualWieldSpec;
      sim.table.dodge = Math.max(0, sim.table.dodge - R.weaponExpertise.dodgePerRank * b.weaponExpertise);
      const type = mh.type || '';
      sim.dagger = /dagger/.test(type);
      if (b.hackAndSlash) {
        if (/dagger|fist/.test(type)) mods.critBonus += R.hackAndSlash.perRank * b.hackAndSlash;
        if (/mace/.test(type)) sim.dr *= 1 - R.hackAndSlash.armorPerRank * b.hackAndSlash;
      }
      if (b.serratedBlades) sim.dr *= 1 - R.serratedBlades.armorPerRank * b.serratedBlades;
      sim.extraAttack = (/sword|axe/.test(type) ? R.hackAndSlash.perRank * b.hackAndSlash : 0);
      sim.cp = 0; sim.cbReady = false; sim.arUntil = -1;
      sim.sndAura = sim.addAura({ name: 'Slice and Dice', duration: 30, mods: { hasteMult: R.sliceAndDice.haste } });
      sim.bfAura = sim.addAura({ name: 'Blade Flurry', duration: R.bladeFlurry.duration, mods: { hasteMult: R.bladeFlurry.haste } });
      sim.arAura = sim.addAura({ name: 'Adrenaline Rush', duration: R.adrenalineRush.duration });
      sim.sBF = sim.addSpell({ name: 'Blade Flurry', cost: () => R.bladeFlurry.cost, cd: R.bladeFlurry.cd });
      sim.sAR = sim.addSpell({ name: 'Adrenaline Rush', cost: () => 0, cd: R.adrenalineRush.cd });
      sim.sCB = sim.addSpell({ name: 'Cold Blood', cost: () => 0, cd: R.coldBlood.cd });
      sim.cost = {
        ss: () => Math.max(0, R.sinisterStrike.cost - R.improvedSinisterStrike.costPerRank * b.improvedSinisterStrike),
        bs: () => R.backstab.cost, hemo: () => R.hemorrhage.cost, mut: () => R.mutilate.cost,
        ev: () => Math.max(0, R.eviscerate.cost - (b.flawlessExecution ? R.flawlessExecution.cost : 0)), snd: () => R.sliceAndDice.cost,
      };
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (isWhite && sim.extraAttack && outcome !== 'glance' && s.rng() < sim.extraAttack) s.whiteAttack(s.swings[0]);
      });
      // poisons: each landed weapon hit may apply the poison on that weapon
      const dk = sim.deadly = { stacks: 0, endsAt: 0, ticking: false };
      const pmult = () => (1 + R.vilePoisons.dmgPerRank * b.vilePoisons) * sim.mods.spellDmgMult;
      const pcrit = () => Math.min(1, Math.max(0, sim.stats.crit + sim.mods.critBonus));
      const pdmg = (name, base) => {
        const crit = sim.rng() < pcrit();
        const d = base * pmult() * (crit ? R.poison.critMult : 1);
        sim.record(name, d, crit ? 'crit' : 'hit');
      };
      const dkTick = () => {
        if (sim.now > dk.endsAt + 1e-9) { dk.stacks = 0; dk.ticking = false; return; }
        pdmg('Deadly Poison', dk.stacks * R.deadlyPoison.total / (R.deadlyPoison.duration / R.deadlyPoison.tick));
        sim.schedule(R.deadlyPoison.tick, dkTick);
      };
      const applyPoison = (kind) => {
        const p = kind === 'deadly' ? R.deadlyPoison : R.instantPoison;
        if (sim.rng() >= p.chance + R.improvedPoisons.chancePerRank * b.improvedPoisons) return;
        const name = kind === 'deadly' ? 'Deadly Poison' : 'Instant Poison';
        sim.entry(name).casts++;
        if (sim.rng() < R.poison.resist) { sim.entry(name).misses++; return; }
        if (kind === 'instant') { pdmg(name, p.min + (p.max - p.min) * sim.rng()); return; }
        dk.stacks = Math.min(p.maxStacks, dk.stacks + 1); dk.endsAt = sim.now + p.duration;
        if (!dk.ticking) { dk.ticking = true; sim.schedule(p.tick, dkTick); }
      };
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (source === 'Eviscerate') return;
        const kind = isOH ? b.ohPoison : b.mhPoison;
        if (kind === 'instant' || kind === 'deadly') applyPoison(kind);
        if (source === 'Mutilate' && b.ohPoison !== 'none' && b.ohPoison !== undefined) applyPoison(b.ohPoison);   // Mutilate hits both weapons
      });
      // energy: +20 every 2 s, doubled by Adrenaline Rush
      const tick = () => { sim.gainRage(R.energy.perTick * (sim.arAura.active ? R.adrenalineRush.regenMult : 1)); sim.nextTick = sim.now + R.energy.tick; sim.schedule(R.energy.tick, tick); };
      sim.nextTick = R.energy.tick; sim.schedule(R.energy.tick, tick);
    },
    start(sim) { sim.rage = sim.rageCap; },
    rotate(sim) {
      const now = sim.now, mh = sim.player.weapons[0], oh = sim.player.weapons[1];
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      const GCD = 1.0, energy = sim.rage;
      const nextTickWait = Math.max(0.05, sim.nextTick - now);
      // choose the builder
      const builder = (() => {
        if (b.builder && b.builder !== 'auto') return b.builder;
        if (b.mutilate && sim.dagger && oh && /dagger/.test(oh.type || '')) return 'mutilate';
        if (sim.dagger) return 'backstab';
        if (b.hemorrhage) return 'hemorrhage';
        return 'ss';
      })();
      const norm = sim.dagger ? R.normSpeed.dagger : R.normSpeed.other;
      const ohMult = () => 0.5 + (sim.mods.ohDmgBonus || 0);
      const nearEnd = (sim.fightLen - now) < 3;
      const qm = () => (sim.targetHealthPct() <= R.quietus.below ? 1 + R.quietus.perRank * (b.quietus || 0) : 1);
      const cbBonus = () => (sim.cbReady ? 1.0 : 0);
      const spendCb = () => { sim.cbReady = false; };
      const addCp = (n, crit, isBuilder) => {
        sim.cp = Math.min(5, sim.cp + n);
        if (crit && isBuilder && b.sealFate && sim.rng() < R.sealFate.perRank * b.sealFate) sim.cp = Math.min(5, sim.cp + 1);
      };
      const lethal = () => 1.0 * R.lethality.critDmgPerRank * b.lethality;

      // cooldowns that cost no GCD
      if (b.useCooldowns) {
        if (b.adrenalineRush && now >= sim.sAR.readyAt) { sim.sAR.readyAt = now + R.adrenalineRush.cd; sim.entry('Adrenaline Rush').casts++; sim.arAura.apply(); }
        if (b.coldBlood && now >= sim.sCB.readyAt && sim.cp >= 4) { sim.sCB.readyAt = now + R.coldBlood.cd; sim.entry('Cold Blood').casts++; sim.cbReady = true; }
      }
      if (gcdLeft > 0) return gcdLeft;
      if (b.useCooldowns && b.bladeFlurry && now >= sim.sBF.readyAt && energy >= R.bladeFlurry.cost) {
        return castGcd(sim, sim.sBF, () => { sim.spendRage(R.bladeFlurry.cost); sim.bfAura.apply(); }, GCD);
      }
      const sndLeft = sim.sndAura.active ? sim.sndAura.endsAt - now : 0;
      // Slice and Dice: keep it up (1+ combo points when down, 2+ to refresh early)
      if (!nearEnd && energy >= sim.cost.snd() && ((sndLeft <= 0 && sim.cp >= 1) || (sndLeft < 2 && sim.cp >= 2))) {
        return castGcd(sim, { name: 'Slice and Dice', cd: 0, readyAt: 0, casts: 0 }, () => {
          sim.spendRage(sim.cost.snd());
          const dur = (R.sliceAndDice.base + R.sliceAndDice.perPoint * sim.cp) * (1 + R.improvedSliceAndDice.perRank * b.improvedSliceAndDice);
          sim.sndAura.apply(1, dur); sim.cp = 0;
        }, GCD);
      }
      // Eviscerate at 5 combo points (or earlier at the very end of the fight)
      if ((sim.cp >= 5 || (nearEnd && sim.cp >= 2)) && energy >= sim.cost.ev()) {
        return castGcd(sim, { name: 'Eviscerate', cd: 0, readyAt: 0, casts: 0 }, () => {
          const cp = sim.cp; sim.spendRage(sim.cost.ev()); sim.cp = 0;
          const tb = R.eviscerate.table[cp];
          const bonus = cbBonus(); spendCb();
          yellowAttack(sim, 'Eviscerate', () => (tb[0] + (tb[1] - tb[0]) * sim.rng()) * (1 + R.improvedEviscerate.perRank * b.improvedEviscerate) * (1 + R.aggression.perRank * b.aggression), { bonusCrit: bonus });
          if (b.ruthlessness && sim.rng() < R.ruthlessness.perRank * b.ruthlessness) sim.cp = Math.min(5, sim.cp + 1);
          if (b.relentlessStrikes) for (let i = 0; i < cp; i++) if (sim.rng() < R.relentlessStrikes.chancePerCp) { sim.gainRage(R.relentlessStrikes.energy); break; }
        }, GCD);
      }
      // never build past 5 combo points, and never starve Slice and Dice: wait for the energy instead
      if (sim.cp >= 5 || (!nearEnd && ((sndLeft <= 0 && sim.cp >= 1) || (sndLeft < 2 && sim.cp >= 2)))) return nextTickWait;
      // builders
      const doBuilder = (name, cost, fn) => {
        if (energy < cost) return null;
        return castGcd(sim, { name, cd: 0, readyAt: 0, casts: 0 }, () => { sim.spendRage(cost); fn(); }, GCD);
      };
      let w = null;
      if (builder === 'ss') w = doBuilder('Sinister Strike', sim.cost.ss(), () => {
        const bonus = cbBonus(); spendCb();
        const o = yellowAttack(sim, 'Sinister Strike', () => (sim.weaponRoll(mh) + sim.ap() / 14 * norm + R.sinisterStrike.flat) * R.sinisterStrike.pct * (1 + R.aggression.perRank * b.aggression) * qm(),
          { bonusCrit: bonus, critDmgBonus: lethal() });
        if (o !== 'miss' && o !== 'dodge') addCp(1, o === 'crit', true);
      });
      else if (builder === 'backstab') w = doBuilder('Backstab', sim.cost.bs(), () => {
        const bonus = cbBonus() + R.puncturingWounds.bsCritPerRank * b.puncturingWounds; spendCb();
        const o = yellowAttack(sim, 'Backstab', () => ((sim.weaponRoll(mh) + sim.ap() / 14 * norm) * R.backstab.pct + R.backstab.flat) * (1 + R.aggression.perRank * b.aggression) * (1 + R.opportunity.perRank * b.opportunity),
          { bonusCrit: bonus, critDmgBonus: lethal() });
        if (o !== 'miss' && o !== 'dodge') addCp(1, o === 'crit', true);
      });
      else if (builder === 'hemorrhage') w = doBuilder('Hemorrhage', sim.cost.hemo(), () => {
        const bonus = cbBonus(); spendCb();
        const o = yellowAttack(sim, 'Hemorrhage', () => (sim.weaponRoll(mh) + sim.ap() / 14 * norm) * (sim.dagger ? R.hemorrhage.pctDagger : R.hemorrhage.pct) * qm(), { bonusCrit: bonus, critDmgBonus: lethal() });
        if (o !== 'miss' && o !== 'dodge') addCp(1, o === 'crit', true);
      });
      else if (builder === 'mutilate') w = doBuilder('Mutilate', sim.cost.mut(), () => {
        const bonus = cbBonus() + R.puncturingWounds.mutCritPerRank * b.puncturingWounds; spendCb();
        const o = yellowAttack(sim, 'Mutilate', () => {
          const mhPart = (sim.weaponRoll(mh) + sim.ap() / 14 * norm) * R.mutilate.pct + R.mutilate.flat;
          const ohPart = ((sim.weaponRoll(oh) + sim.ap() / 14 * norm) * R.mutilate.pct + R.mutilate.flat) * ohMult();
          return (mhPart + ohPart) * (1 + R.opportunity.perRank * b.opportunity) * (sim.deadly.stacks > 0 ? R.poison.mutilateBonus : 1);
        }, { bonusCrit: bonus, critDmgBonus: lethal() });
        if (o !== 'miss' && o !== 'dodge') addCp(R.mutilate.cp, o === 'crit', true);
      });
      if (w !== null) return w;
      // wait for energy: the next tick (or the global cooldown, whichever comes later)
      return nextTickWait;
    },
  };
}
