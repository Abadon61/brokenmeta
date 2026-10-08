// Shadow Priest kit. Spell numbers come from the client tables (rank ladders in data/spells60.json: top / extra): Shadow Word: Pain,
// Mind Blast, Mind Flay, Shadow Word: Death, Devouring Plague. Talent numbers come from the Forever tooltips. ASSUMED (Classic
// style): Power Infusion and Inner Focus cooldowns, Smite as the filler of a build without Mind Flay, mana items, base mana.
// Periodic effects use the client's per-tick coefficient and can crit. Not simulated: Vampiric Embrace healing, Spirit Tap,
// Silence, the Holy and Discipline spells other than the ones listed.
import { makeCaster, fromRank, pickRank } from './caster.js';
import { dotActive, dotLeft } from './spells.js';

export const PRIEST = {
  shadowFocus: { hit: 0.01 }, improvedSwp: { ticks: 1 }, improvedMindBlast: { cd: 0.5 }, improvedMindFlay: { dmg: 0.10 }, shadowWeaving: { dmg: 0.02, max: 5, dur: 15 },
  darkness: { dmg: 0.02 }, shadowform: { dmg: 0.10, cost: 0.5, critBonus: 1 }, devouringContagion: { cost: 0.25 }, twinDisciplines: { dmg: 0.01 }, mentalAgility: { cost: 1 / 30 },
  mentalStrength: { int: 0.03 }, meditation: { keep: 1 / 6 }, powerInfusion: { dmg: 1.2, dur: 15, cd: 180 }, innerFocus: { crit: 0.25, cd: 180 },   // cooldowns ASSUMED
  manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

export const PRIEST_DEFAULT_BUILD = {
  shadowFocus: 0, improvedSwp: 0, improvedMindBlast: 0, mindFlay: 0, improvedMindFlay: 0, shadowWeaving: 0, darkness: 0, shadowform: 0, devouringContagion: 0,
  twinDisciplines: 0, mentalAgility: 0, mentalStrength: 0, meditation: 0, powerInfusion: 0, innerFocus: 0,
  useCooldowns: true, usePotion: true, useGem: true, devouringPlague: true, shadowWordDeath: true,
};

export function priestKit(build = {}, data = null) {
  const b = Object.assign({}, PRIEST_DEFAULT_BUILD, build), P = PRIEST;
  const sh = ['shadow'];
  const swp = pickRank(data, 'priest', 'priest_shadow_word_pain', 'Shadow Word: Pain'), mb = pickRank(data, 'priest', 'priest_mind_blast', 'Mind Blast');
  const mf = pickRank(data, 'priest', null, 'Mind Flay'), swd = pickRank(data, 'priest', null, 'Shadow Word: Death'), dp = pickRank(data, 'priest', null, 'Devouring Plague');
  const sm = pickRank(data, 'priest', 'priest_smite', 'Smite');
  const S = {};
  if (swp) S.swp = fromRank(swp, { name: 'Shadow Word: Pain', schools: sh, instant: true });
  if (mb) S.mb = fromRank(mb, { name: 'Mind Blast', schools: sh });
  if (mf) { const t = fromRank(mf); S.mf = { name: 'Mind Flay', schools: sh, cost: t.cost, cast: 0, channel: { perTick: t.dot.perTick, ticks: t.dot.ticks, interval: t.dot.interval, coeff: t.dot.coeff } }; }
  if (swd) S.swd = fromRank(swd, { name: 'Shadow Word: Death', schools: sh, instant: true });
  if (dp) S.dp = fromRank(dp, { name: 'Devouring Plague', schools: sh, instant: true });
  if (sm) S.smite = fromRank(sm, { name: 'Smite', schools: ['holy'] });
  const def = {
    name: 'priest', build: b, S,
    items: { potion: P.manaPotion, gem: P.manaGem },
    baseMana: (sim) => sim.stats.mana + Math.floor((sim.stats.int || 0) * P.mentalStrength.int * b.mentalStrength) * 15,
    keep: () => P.meditation.keep * b.meditation,
    setup(sim) {
      const extraInt = Math.floor((sim.stats.int || 0) * P.mentalStrength.int * b.mentalStrength);
      sim.critBase = extraInt / 59.2 / 100;
      sim.aWeave = sim.addAura({ name: 'Shadow Weaving', duration: P.shadowWeaving.dur, maxStacks: P.shadowWeaving.max });
      sim.aPI = sim.addAura({ name: 'Power Infusion', duration: P.powerInfusion.dur });
      sim.innerFocus = false;
      sim.est = (s) => 0;
    },
    mods(sim, s, kind) {
      let hit = 0, crit = sim.critBase, dmg = 1, critBonus = 0;
      if (s.schools[0] === 'shadow') {
        hit += P.shadowFocus.hit * b.shadowFocus;
        dmg *= (1 + P.darkness.dmg * b.darkness) * (b.shadowform ? 1 + P.shadowform.dmg : 1) * (1 + P.shadowWeaving.dmg * sim.aWeave.stacks);
        if (b.shadowform) critBonus += P.shadowform.critBonus;
      }
      if (s.instant) dmg *= 1 + P.twinDisciplines.dmg * b.twinDisciplines;
      if (s === def.S.mf) dmg *= 1 + P.improvedMindFlay.dmg * b.improvedMindFlay;
      if (sim.aPI.active) dmg *= P.powerInfusion.dmg;
      if (sim.innerFocus && s.direct) crit += P.innerFocus.crit;
      return { hit, crit, dmg, critBonus };
    },
    castTime: (sim, s) => s.cast,
    cost(sim, s) {
      if (sim.innerFocus) return 0;
      let c = s.cost;
      if (b.shadowform && s.schools[0] === 'shadow') c *= 1 - P.shadowform.cost;
      if (s.instant) c *= 1 - P.mentalAgility.cost * b.mentalAgility;
      if (s === def.S.dp) c *= 1 - P.devouringContagion.cost * b.devouringContagion;
      return Math.round(c);
    },
    beforeCast(sim, s) { if (sim.innerFocus) sim.innerFocus = false; },
    afterHit(sim, s, outcome) { if (outcome !== 'miss' && s.schools[0] === 'shadow' && !s.dot && b.shadowWeaving && sim.rng() < Math.min(1, b.shadowWeaving / 3)) sim.aWeave.apply(1); },
    offGcd(sim) {
      if (!b.useCooldowns) return;
      if (b.powerInfusion && sim.now >= (sim.cdAt.pi || 0)) { sim.cdAt.pi = sim.now + P.powerInfusion.cd; sim.entry('Power Infusion').casts++; sim.aPI.apply(); }
      if (b.innerFocus && sim.now >= (sim.cdAt.focus || 0) && !sim.innerFocus) { sim.cdAt.focus = sim.now + P.innerFocus.cd; sim.entry('Inner Focus').casts++; sim.innerFocus = true; }
    },
    choose(sim) {
      const now = sim.now, ready = (s) => now >= (sim.cdAt[s.name] || 0) - 1e-9, rem = sim.fightLen - now;
      if (S.swp && rem > 6 && dotLeft(sim, S.swp.name) < 0.6) return S.swp;
      if (S.dp && b.devouringPlague && ready(S.dp) && rem > 12 && !dotActive(sim, S.dp.name)) return S.dp;
      if (S.mb && ready(S.mb)) return S.mb;
      if (S.swd && b.shadowWordDeath && ready(S.swd)) return S.swd;
      if (S.mf && b.mindFlay) return S.mf;
      return b.shadowform ? null : S.smite || S.mb;                // Shadowform forbids holy spells: without Mind Flay the priest just waits for the next cooldown
    },
  };
  if (S.mb) S.mb.cdBase = S.mb.cd;
  const kit = makeCaster(def);
  const baseSetup = kit.setup;
  kit.setup = (sim) => { if (S.mb) S.mb.cd = S.mb.cdBase - P.improvedMindBlast.cd * b.improvedMindBlast; if (S.swp) S.swp.dotTicks = () => S.swp.dot.ticks + P.improvedSwp.ticks * b.improvedSwp; baseSetup(sim); };
  return kit;
}
