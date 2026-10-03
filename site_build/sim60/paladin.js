// Retribution Paladin kit (two-handed melee with Seal of Command, Judgement, Holy Strike and Hammer of Wrath). Numbers: Holy Strike,
// Hammer of Wrath and the Seal costs come from the client's rank ladders (data/spells60.json: top / extra); talent numbers from the
// Forever tooltips. ASSUMED (Classic style): Seal of Command's 7 procs per minute, Judgement of Command's damage (the client only
// points at another spell), Vindication's proc chance, mana items, base mana, two-handed weapon speed normalisation (3.3).
// Not simulated: Exorcism and Consecration (low value on one target), blessings, Divine Favor, Holy Shock.
import { yellowAttack } from './shared.js';
import { setupMana, gainMana, spendMana, spiritRegenPerSec, SPELL_CRIT_MULT } from './spells.js';
import { pickRank } from './caster.js';

export const PALADIN = {
  sealOfCommand: { cost: 210, ppm: 7, wpn: 0.7, duration: 30 },                                    // PPM ASSUMED (Classic)
  judgement: { cd: 10, costPct: 0.06, dmg: 72, spCoeff: 0.43, baseMana: 1250 },                    // damage and coefficient ASSUMED (Judgement of Command)
  holyStrike: { cost: 20, cd: 10, wpnPct: 0.5, flat: 93, spCoeff: 0.429, norm: 3.3 },
  hammerOfWrath: { cost: 425, cd: 6, cast: 1, dmg: 498, spCoeff: 0.429 },
  conviction: { crit: 0.01 }, improvedJudgement: { cd: 1 }, sanctifiedJudgement: { mana: 0.2 }, twoHandSpec: { dmg: 0.02 }, vengeance: { dmg: 0.01, stacks: 3, dur: 30 },
  vindication: { ap: 0.01, chance: 0.10, dur: 30 }, sacredArbiter: { dmg: 0.2 }, championOfLight: { sp: 0.2 }, divineStrength: { str: 0.02 }, divineIntellect: { int: 0.02 },
  benediction: { cost: 0.02 }, holyPower: { hs: 0.03 }, improvedSeals: { dmg: 0.05 }, instrumentOfLaw: { cast: 0.5 }, twistOfLight: { cost: 0.2 },
  manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

export const PALADIN_RET_DEFAULT_BUILD = {
  conviction: 0, improvedJudgement: 0, sanctifiedJudgement: 0, twoHandSpec: 0, vengeance: 0, vindication: 0, sealOfCommand: 0, sacredArbiter: 0, championOfLight: 0,
  divineStrength: 0, divineIntellect: 0, benediction: 0, holyPower: 0, improvedSeals: 0, instrumentOfLaw: 0, twistOfLight: 0,
  useCooldowns: true, usePotion: true, useGem: true, executePhase: true,
};

export function paladinRetKit(build = {}, data = null) {
  const b = Object.assign({}, PALADIN_RET_DEFAULT_BUILD, build), P = JSON.parse(JSON.stringify(PALADIN));
  const hs = pickRank(data, 'paladin', 'paladin_holy_strike', 'Holy Strike'), how = pickRank(data, 'paladin', null, 'Hammer of Wrath'), soc = pickRank(data, 'paladin', null, 'Seal of Command'), sor = pickRank(data, 'paladin', 'paladin_seal_of_righteousness', 'Seal of Righteousness');
  if (hs) { P.holyStrike.cost = hs.cost.amount; P.holyStrike.cd = hs.cooldown_ms / 1000; const e = hs.effects.find((x) => x.effect === 121); if (e) { P.holyStrike.flat = e.base; P.holyStrike.var = e.variance; P.holyStrike.spCoeff = e.sp_coeff; } }
  if (how) { P.hammerOfWrath.cost = how.cost.amount; P.hammerOfWrath.cd = how.cooldown_ms / 1000; P.hammerOfWrath.cast = how.cast_ms / 1000; const e = how.effects.find((x) => x.effect === 2); if (e) { P.hammerOfWrath.dmg = e.base; P.hammerOfWrath.spCoeff = e.sp_coeff; } }
  if (soc) P.sealOfCommand.cost = soc.cost.amount;
  return {
    name: 'paladin_retribution', build: b, P,
    setup(sim) {
      sim.player.resource = 'mana'; sim.kitBuild = b;
      const st = sim.stats, mods = sim.mods;
      const extraStr = Math.floor((st.str || 0) * P.divineStrength.str * b.divineStrength), extraInt = Math.floor((st.int || 0) * P.divineIntellect.int * b.divineIntellect);
      mods.apBonus += 2 * extraStr;
      mods.critBonus += P.conviction.crit * b.conviction + extraInt / 54 / 100 * 0;
      mods.dmgMult *= 1 + P.twoHandSpec.dmg * b.twoHandSpec;
      sim.spBonus = Math.floor((st.int || 0) * P.championOfLight.sp * b.championOfLight);
      setupMana(sim, { manaMax: st.mana + 15 * extraInt, mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int: st.int, spi: st.spi }), castingFraction: 0.1 * 0 });
      sim.cd = { judgement: 0, holyStrike: 0, how: 0, potion: 0, gem: 0 };
      sim.sealUntil = -1; sim.sealCommand = false;
      sim.aVeng = sim.addAura({ name: 'Vengeance', duration: P.vengeance.dur, maxStacks: P.vengeance.stacks, mods: { dmgMult: 1 + P.vengeance.dmg * b.vengeance } });
      sim.aVind = sim.addAura({ name: 'Vindication', duration: P.vindication.dur, mods: { apMult: 1 + P.vindication.ap * b.vindication } });
      const holyMult = () => (1 + P.improvedSeals.dmg * b.improvedSeals) * sim.mods.dmgMult / (1 + P.twoHandSpec.dmg * b.twoHandSpec) * (1 - sim.target.spellMitigation) * sim.target.spellTaken;
      sim.holyHit = (name, raw, bonusCrit = 0, critBonus = 0) => {
        const c = Math.max(0, Math.min(1, sim.stats.crit + sim.mods.critBonus + bonusCrit)), crit = sim.rng() < c;
        const d = raw * holyMult() * (crit ? 1 + (SPELL_CRIT_MULT - 1) * (1 + critBonus) : 1);
        sim.record(name, d, crit ? 'crit' : 'hit');
        return crit;
      };
      const twoH = sim.player.weapons[0] && sim.player.weapons[0].twoHand;
      sim.norm = twoH ? P.holyStrike.norm : 2.4;
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (outcome === 'crit' && b.vengeance) s.aVeng.apply(1);
        if (b.vindication && s.rng() < P.vindication.chance) s.aVind.apply();
        if (isWhite && s.sealCommand && s.now < s.sealUntil) {
          const w = s.player.weapons[0], chance = P.sealOfCommand.ppm * w.speed / 60;
          if (s.rng() < chance) { s.entry('Seal of Command').casts++; s.holyHit('Seal of Command', (s.weaponRoll(w) + s.ap() / 14 * w.speed) * P.sealOfCommand.wpn); }
        }
      });
    },
    rotate(sim) {
      const now = sim.now, rem = sim.fightLen - now;
      const st = sim.stats;
      if (b.usePotion && now >= sim.cd.potion && sim.mana <= sim.manaMax - 1800 && rem > 20) { sim.cd.potion = now + P.manaPotion.cd; sim.entry('Mana Potion').casts++; gainMana(sim, P.manaPotion.min + (P.manaPotion.max - P.manaPotion.min) * sim.rng()); }
      if (b.useGem && now >= sim.cd.gem && sim.mana <= sim.manaMax - 1100 && rem > 15) { sim.cd.gem = now + P.manaGem.cd; sim.entry('Mana Gem').casts++; gainMana(sim, P.manaGem.min + (P.manaGem.max - P.manaGem.min) * sim.rng()); }
      const cost = (c) => Math.round(c * (1 - P.benediction.cost * b.benediction));
      const judgeCost = Math.round(P.judgement.costPct * P.judgement.baseMana);
      // Judgement (no global cooldown): unleash the Seal of Command
      if (now >= sim.cd.judgement && sim.sealCommand && now < sim.sealUntil && sim.mana >= judgeCost) {
        sim.cd.judgement = now + P.judgement.cd - P.improvedJudgement.cd * b.improvedJudgement; spendMana(sim, judgeCost); sim.lastCastAt = now;
        sim.entry('Judgement of Command').casts++;
        const e = sim.entry('Judgement of Command');
        sim.holyHit('Judgement of Command', P.judgement.dmg + (st.sp + sim.spBonus) * P.judgement.spCoeff);
        if (b.sanctifiedJudgement) gainMana(sim, P.sealOfCommand.cost * P.sanctifiedJudgement.mana * b.sanctifiedJudgement);
      }
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      // keep the Seal up
      if (b.sealOfCommand && (!sim.sealCommand || sim.sealUntil - now < 1.5) && sim.mana >= cost(P.sealOfCommand.cost) && rem > 3) {
        spendMana(sim, cost(P.sealOfCommand.cost)); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry('Seal of Command').casts += 0;
        sim.sealCommand = true; sim.sealUntil = now + P.sealOfCommand.duration;
        return 1.5;
      }
      // Hammer of Wrath in the execute phase
      if (b.executePhase && sim.inExecute() && now >= sim.cd.how && sim.mana >= cost(P.hammerOfWrath.cost)) {
        sim.cd.how = now + P.hammerOfWrath.cd; spendMana(sim, cost(P.hammerOfWrath.cost)); sim.lastCastAt = now; sim.entry('Hammer of Wrath').casts++;
        sim.gcdReadyAt = now + 1.5;
        const t = Math.max(0.1, P.hammerOfWrath.cast - P.instrumentOfLaw.cast * b.instrumentOfLaw);
        sim.schedule(t, () => { sim.holyHit('Hammer of Wrath', P.hammerOfWrath.dmg + (sim.stats.sp + sim.spBonus) * P.hammerOfWrath.spCoeff); });
        return 1.5;
      }
      // Holy Strike on cooldown
      if (now >= sim.cd.holyStrike && sim.mana >= cost(P.holyStrike.cost) && sim.player.weapons.length) {
        sim.cd.holyStrike = now + P.holyStrike.cd; spendMana(sim, cost(P.holyStrike.cost)); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry('Holy Strike').casts++;
        const w = sim.player.weapons[0], v = P.holyStrike.var || 0;
        const out = sim.resolveYellow(P.holyStrike.holy ? 0 : 0, true);
        const e = sim.entry('Holy Strike');
        if (out === 'miss') { e.misses++; sim.onMeleeHit('miss', 'Holy Strike', false, false); }
        else if (out === 'dodge') { e.dodges++; sim.onMeleeHit('dodge', 'Holy Strike', false, false); }
        else {
          const flat = P.holyStrike.flat * (1 + v * (sim.rng() - 0.5));
          const raw = ((sim.weaponRoll(w) + sim.ap() / 14 * sim.norm) * P.holyStrike.wpnPct + flat + (sim.stats.sp + sim.spBonus) * P.holyStrike.spCoeff) * (1 + P.sacredArbiter.dmg * b.sacredArbiter);
          const crit = sim.holyHit('Holy Strike', raw, P.holyPower.hs * 0, 0);
          sim.onMeleeHit(crit ? 'crit' : 'hit', 'Holy Strike', false, false);
        }
        return 1.5;
      }
      const next = Math.min(sim.cd.holyStrike, sim.cd.how, sim.sealUntil - 1.4, sim.cd.judgement);
      return Math.max(0.1, Math.min(1.0, next - now));
    },
  };
}
