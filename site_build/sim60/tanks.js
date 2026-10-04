// Tank kits: Protection Warrior, Protection Paladin and Bear Druid. The fight adds a raid boss that swings at the tank (engine.js _bossSwing:
// Classic attack table of a level-63 mob against the tank's defense, dodge, parry and block, armor mitigation, rage from the damage taken).
// The headline numbers are threat per second (TPS), damage taken per second, avoidance and block. Spell numbers come from the client's rank
// ladders (data/spells60.json: extra) and the Forever talent tooltips. ASSUMED (Classic style): Defensive Stance (+30% threat, -10% damage taken
// and dealt), Righteous Fury (+60% holy threat: from the client), Dire Bear Form threat +30%, the flat threat of Shield Slam, the boss swing
// (2.0 s, 9000 damage, +-15%), Seal of Righteousness' per-swing damage, Holy Shield's 8 charges, the bear's natural weapon, block value 40 + Strength / 20.
// Not simulated: Taunt, Concussion Blow, Shield Wall / Last Stand / Templar's Bulwark (emergency cooldowns), threat of Thunder Clap and Consecration (area).
import { yellowAttack, castGcd } from './shared.js';
import { setupMana, gainMana, spendMana, spiritRegenPerSec, SPELL_CRIT_MULT } from './spells.js';
import { pickRank } from './caster.js';

const spell = (name) => ({ name, cd: 0, readyAt: 0, casts: 0 });

// ---------------------------------------------------------------------------------------------------------------------------
// Protection Warrior
export const WARRIOR_PROT = {
  stance: { threat: 1.3, taken: 0.9, dealt: 0.9 },
  shieldSlam: { cost: 20, cd: 6, dmg: 655, var: 0.05, threat: 250 },        // flat threat ASSUMED ("very high threat" in the tooltip)
  revenge: { cost: 5, cd: 5, dmg: 153, var: 0.2, window: 5 },
  sunder: { cost: 15, threat: 206 }, heroicStrike: { cost: 15, flat: 157 }, bloodrage: { immediate: 10, overTime: 10, cd: 60 },
  shieldSpec: { block: 0.01, rage: 5, chance: 0.2 }, anticipation: { def: 4 }, toughness: { armor: 0.02 }, improvedRevenge: { dmg: 0.2 }, defiance: { threat: 0.05 },
  bastion: { dmg: 0.02 }, focusedRage: { cost: 1 }, masterOfDefense: { rage: 5, chance: 0.5 }, improvedSunder: { cost: 1 },
};
export const WARRIOR_PROT_DEFAULT_BUILD = {
  deflection: 0, improvedHeroicStrike: 0, shieldSpec: 0, anticipation: 0, toughness: 0, improvedRevenge: 0, defiance: 0, bastion: 0, focusedRage: 0, masterOfDefense: 0, improvedSunder: 0, shieldSlam: 0, improvedBloodrage: 0,
  useHeroicStrike: true, hsRageReserve: 25,
};

export function warriorProtKit(build = {}, data = null) {
  const b = Object.assign({}, WARRIOR_PROT_DEFAULT_BUILD, build), W = JSON.parse(JSON.stringify(WARRIOR_PROT));
  const ss = pickRank(data, 'warrior', null, 'Shield Slam'), rv = pickRank(data, 'warrior', null, 'Revenge'), su = pickRank(data, 'warrior', null, 'Sunder Armor'), hs = pickRank(data, 'warrior', null, 'Heroic Strike');
  const rg = (r) => (r.cost ? r.cost.amount / 10 : 0);
  if (ss) { W.shieldSlam.cost = rg(ss); W.shieldSlam.cd = ss.cooldown_ms / 1000; const e = ss.effects.find((x) => x.effect === 2); W.shieldSlam.dmg = e.base; W.shieldSlam.var = e.variance; }
  if (rv) { W.revenge.cost = rg(rv); W.revenge.cd = rv.cooldown_ms / 1000; const e = rv.effects.find((x) => x.effect === 2); W.revenge.dmg = e.base; W.revenge.var = e.variance; }
  if (su) { W.sunder.cost = rg(su); const e = su.effects.find((x) => x.effect === 63); if (e) W.sunder.threat = e.base; }
  if (hs) { W.heroicStrike.cost = rg(hs); W.heroicStrike.flat = hs.effects.find((x) => x.effect === 17).base; }
  return {
    name: 'warrior_protection', build: b, W,
    setup(sim) {
      sim.kitBuild = b; sim.player.resource = 'rage';
      const t = sim.tank, mods = sim.mods;
      t.defense += W.anticipation.def * b.anticipation; t.armor *= 1 + W.toughness.armor * b.toughness; t.block += W.shieldSpec.block * b.shieldSpec; t.parry += 0.01 * b.deflection;
      sim.takenMult *= W.stance.taken;
      mods.dmgMult *= W.stance.dealt * (t.shield ? 1 + W.bastion.dmg * b.bastion : 1);
      const tm = W.stance.threat + (t.shield ? W.defiance.threat * b.defiance : 0);
      sim.threatMult = () => tm;
      sim.rageCap = 100;
      sim.sSS = sim.addSpell({ name: 'Shield Slam', cd: W.shieldSlam.cd, cost: () => Math.max(0, W.shieldSlam.cost - W.focusedRage.cost * b.focusedRage) });
      sim.sRV = sim.addSpell({ name: 'Revenge', cd: W.revenge.cd, cost: () => Math.max(0, W.revenge.cost - W.focusedRage.cost * b.focusedRage) });
      sim.sBR = sim.addSpell({ name: 'Bloodrage', cd: W.bloodrage.cd, cost: () => 0 });
      const hsCost = () => Math.max(0, W.heroicStrike.cost - W.focusedRage.cost * b.focusedRage - b.improvedHeroicStrike);
      sim.sHS = sim.addSpell({ name: 'Heroic Strike', cost: hsCost, onSwing(s, sw) {
        s.spendRage(hsCost()); s.entry('Heroic Strike').casts++;
        yellowAttack(s, 'Heroic Strike', () => s.weaponRoll(sw.w) + s.ap() / 14 * sw.w.speed + W.heroicStrike.flat);
      } });
      sim.revengeUntil = -1;
      sim.bossHooks.push((s, out, dmg) => {
        if (dmg > 0) s.gainRage(2.5 * dmg / s.rageC);
        if (out === 'dodge' || out === 'parry' || out === 'block') s.revengeUntil = s.now + W.revenge.window;
        if (out === 'block' && b.shieldSpec && s.rng() < W.shieldSpec.chance * b.shieldSpec) s.gainRage(W.shieldSpec.rage);
        if ((out === 'dodge' || out === 'parry') && b.masterOfDefense && t.shield && s.rng() < W.masterOfDefense.chance * b.masterOfDefense) s.gainRage(W.masterOfDefense.rage);
      });
    },
    rotate(sim) {
      const now = sim.now, W2 = W;
      if (now >= sim.sBR.readyAt) {
        sim.sBR.readyAt = now + W.bloodrage.cd; sim.entry('Bloodrage').casts++;
        const extra = 1 + 0.5 * b.improvedBloodrage / 2;
        sim.gainRage(W.bloodrage.immediate * extra);
        for (let i = 1; i <= 10; i++) sim.schedule(i, () => sim.gainRage(W.bloodrage.overTime * extra / 10));
      }
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      const rage = sim.rage, ssCost = sim.sSS.cost(), rvCost = sim.sRV.cost(), suCost = Math.max(0, W.sunder.cost - W.improvedSunder.cost * b.improvedSunder);
      if (b.shieldSlam && sim.tank.shield && now >= sim.sSS.readyAt && rage >= ssCost) {
        return castGcd(sim, sim.sSS, () => {
          sim.spendRage(ssCost);
          const o = yellowAttack(sim, 'Shield Slam', () => W.shieldSlam.dmg * (1 + W.shieldSlam.var * (sim.rng() - 0.5)) + sim.tank.blockValue);
          if (o !== 'miss' && o !== 'dodge') sim.threat(W.shieldSlam.threat * sim.threatMult());
        });
      }
      if (now < sim.revengeUntil && now >= sim.sRV.readyAt && rage >= rvCost) {
        return castGcd(sim, sim.sRV, () => {
          sim.spendRage(rvCost); sim.revengeUntil = -1;
          yellowAttack(sim, 'Revenge', () => W.revenge.dmg * (1 + W.revenge.var * (sim.rng() - 0.5)) * (1 + W.improvedRevenge.dmg * b.improvedRevenge));
        });
      }
      const reserve = (now >= sim.sSS.readyAt - 1.5 && b.shieldSlam ? ssCost : 0);
      if (b.useHeroicStrike && !sim.mhQueued && rage >= sim.sHS.cost() + b.hsRageReserve && sim.player.weapons.length) sim.mhQueued = sim.sHS;
      if (rage >= suCost + reserve) {
        return castGcd(sim, spell('Sunder Armor'), () => { sim.spendRage(suCost); sim.threat(W.sunder.threat * sim.threatMult()); });
      }
      const next = Math.min(b.shieldSlam ? sim.sSS.readyAt : Infinity, sim.sRV.readyAt, sim.sBR.readyAt);
      return Math.max(0.1, Math.min(0.5, next - now));
    },
  };
}

// ---------------------------------------------------------------------------------------------------------------------------
// Protection Paladin
export const PALADIN_PROT = {
  holyShield: { cost: 240, cd: 10, dur: 10, block: 0.30, dmg: 221, charges: 8 },                 // charges ASSUMED (Classic), the rest from the client
  holyStrike: { cost: 20, cd: 10, wpnPct: 0.5, flat: 93, spCoeff: 0.429 },
  judgement: { cd: 10, costPct: 0.06, baseMana: 1250, dmg: 178, spCoeff: 0.5 },
  sealCost: 200, sealPerSecond: 25, sealDur: 30,                                                // per-swing damage ASSUMED
  rf: { threat: 1.6 }, anticipation: { def: 4 }, toughness: { armor: 0.02 }, precision: { hit: 0.01 }, oneHand: { dmg: 0.10 / 3 }, improvedRf: { taken: 0.02 },
  reckoning: { chance: 0.08 }, redoubt: { chance: 0.02, block: 0.20, blocks: 5, dur: 10 }, ironCreed: { threat: 0.05 }, sacredDuty: { sta: 0.02 },
  manaPotion: { cd: 120, min: 1350, max: 2250 },
};
export const PALADIN_PROT_DEFAULT_BUILD = {
  anticipation: 0, toughness: 0, precision: 0, oneHandWeaponSpecialization: 0, improvedRighteousFury: 0, reckoning: 0, redoubt: 0, ironCreed: 0, sacredDuty: 0, holyShield: 0, swiftJudgement: 0,
  usePotion: true,
};

export function paladinProtKit(build = {}, data = null) {
  const b = Object.assign({}, PALADIN_PROT_DEFAULT_BUILD, build), P = JSON.parse(JSON.stringify(PALADIN_PROT));
  const hsh = pickRank(data, 'paladin', null, 'Holy Shield'), hst = pickRank(data, 'paladin', 'paladin_holy_strike', 'Holy Strike'), jor = pickRank(data, 'paladin', null, 'Judgement of Righteousness'), rf = pickRank(data, 'paladin', null, 'Righteous Fury');
  if (hsh) { P.holyShield.cost = hsh.cost.amount; P.holyShield.cd = hsh.cooldown_ms / 1000; P.holyShield.dur = hsh.duration_ms / 1000; P.holyShield.block = hsh.effects.find((e) => e.aura === 51).base / 100; P.holyShield.dmg = hsh.effects.find((e) => e.aura === 43).base; }
  if (hst) { P.holyStrike.cost = hst.cost.amount; P.holyStrike.cd = hst.cooldown_ms / 1000; const e = hst.effects.find((x) => x.effect === 121); if (e) { P.holyStrike.flat = e.base; P.holyStrike.spCoeff = e.sp_coeff; } }
  if (jor) { const e = jor.effects.find((x) => x.effect === 2); P.judgement.dmg = e.base + e.per_level * Math.max(0, 60 - jor.spell_level); P.judgement.spCoeff = e.sp_coeff; }
  if (rf) P.rf.threat = 1 + rf.effects.find((e) => e.aura === 10).base / 100;
  return {
    name: 'paladin_protection', build: b, P,
    setup(sim) {
      sim.kitBuild = b; sim.player.resource = 'mana';
      const t = sim.tank, mods = sim.mods, st = sim.stats;
      t.defense += P.anticipation.def * b.anticipation; t.armor *= 1 + P.toughness.armor * b.toughness;
      mods.hitBonus += P.precision.hit * b.precision;
      mods.dmgMult *= 1 + P.oneHand.dmg * b.oneHandWeaponSpecialization;
      sim.takenMult *= 1 - P.improvedRf.taken * b.improvedRighteousFury;
      const HOLY = /Holy|Seal|Judgement|Consecration/;
      sim.threatMult = (name) => (HOLY.test(name) ? P.rf.threat * (name === 'Holy Strike' ? 1 + P.ironCreed.threat * b.ironCreed : 1) : 1);
      setupMana(sim, { manaMax: st.mana, mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int: st.int, spi: st.spi }), castingFraction: 0 });
      sim.baseBlock = t.block; sim.hsUntil = -1; sim.hsCharges = 0; sim.redoubtBlocks = 0; sim.redoubtUntil = -1; sim.sealUntil = -1;
      sim.cd = { hs: 0, holyStrike: 0, judgement: 0, potion: 0 };
      const holy = (name, raw) => {
        const c = Math.max(0, Math.min(1, sim.stats.crit + sim.mods.critBonus)), crit = sim.rng() < c;
        sim.record(name, raw * (sim.mods.dmgMult) * (1 - sim.target.spellMitigation) * sim.target.spellTaken * (crit ? SPELL_CRIT_MULT : 1), crit ? 'crit' : 'hit');
      };
      sim.holy = holy;
      sim.bossHooks.push((s, out, dmg) => {
        // active block bonuses
        if (dmg > 0 && b.redoubt && s.now >= s.redoubtUntil && s.rng() < P.redoubt.chance * b.redoubt) { s.redoubtUntil = s.now + P.redoubt.dur; s.redoubtBlocks = P.redoubt.blocks; }
        if (out === 'block') {
          if (s.now < s.hsUntil && s.hsCharges > 0) { s.hsCharges--; s.entry('Holy Shield').hits++; holy('Holy Shield', P.holyShield.dmg + (st.sp || 0) * 0.0); }
          if (s.redoubtBlocks > 0) s.redoubtBlocks--;
          if (b.reckoning && s.rng() < P.reckoning.chance * b.reckoning) s.whiteAttack(s.swings[0]);
        }
        // the block chance for the NEXT swing follows the active effects
        s.tank.block = s.baseBlock + (s.now < s.hsUntil && s.hsCharges > 0 ? P.holyShield.block : 0) + (s.now < s.redoubtUntil && s.redoubtBlocks > 0 ? P.redoubt.block : 0);
      });
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (outcome === 'miss' || outcome === 'dodge' || !isWhite || s.now >= s.sealUntil) return;
        const w = s.player.weapons[0]; s.entry('Seal of Righteousness').casts++; s.holy('Seal of Righteousness', P.sealPerSecond * (w ? w.speed : 2.5));
      });
    },
    rotate(sim) {
      const now = sim.now, st = sim.stats;
      if (b.usePotion && now >= sim.cd.potion && sim.mana <= sim.manaMax - 1800 && sim.fightLen - now > 20) { sim.cd.potion = now + P.manaPotion.cd; sim.entry('Mana Potion').casts++; gainMana(sim, P.manaPotion.min + (P.manaPotion.max - P.manaPotion.min) * sim.rng()); }
      const judgeCost = Math.round(P.judgement.costPct * P.judgement.baseMana);
      if (now >= sim.cd.judgement && now < sim.sealUntil && sim.mana >= judgeCost) {
        sim.cd.judgement = now + P.judgement.cd; spendMana(sim, judgeCost); sim.lastCastAt = now; sim.entry('Judgement of Righteousness').casts++;
        sim.holy('Judgement of Righteousness', P.judgement.dmg + (st.sp || 0) * P.judgement.spCoeff);
        if (b.swiftJudgement && false) sim.cd.judgement = now;
      }
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      if ((now >= sim.sealUntil - 1.5) && sim.mana >= P.sealCost && sim.fightLen - now > 3) {
        spendMana(sim, P.sealCost); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.sealUntil = now + P.sealDur; return 1.5;
      }
      if (b.holyShield && sim.tank.shield && now >= sim.cd.hs && sim.mana >= P.holyShield.cost) {
        sim.cd.hs = now + P.holyShield.cd; spendMana(sim, P.holyShield.cost); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry('Holy Shield').casts++;
        sim.hsUntil = now + P.holyShield.dur; sim.hsCharges = P.holyShield.charges; sim.tank.block = sim.baseBlock + P.holyShield.block;
        sim.schedule(P.holyShield.dur, () => { sim.tank.block = sim.baseBlock + (sim.now < sim.redoubtUntil && sim.redoubtBlocks > 0 ? P.redoubt.block : 0); });
        return 1.5;
      }
      if (now >= sim.cd.holyStrike && sim.mana >= P.holyStrike.cost && sim.player.weapons.length) {
        sim.cd.holyStrike = now + P.holyStrike.cd; spendMana(sim, P.holyStrike.cost); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry('Holy Strike').casts++;
        const w = sim.player.weapons[0], out = sim.resolveYellow(0, true);
        if (out === 'miss' || out === 'dodge') { sim.entry('Holy Strike')[out === 'miss' ? 'misses' : 'dodges']++; return 1.5; }
        sim.holy('Holy Strike', (sim.weaponRoll(w) + sim.ap() / 14 * 2.4) * P.holyStrike.wpnPct + P.holyStrike.flat + (st.sp || 0) * P.holyStrike.spCoeff);
        return 1.5;
      }
      const next = Math.min(sim.cd.holyStrike, sim.cd.judgement, sim.cd.hs, sim.sealUntil - 1.5);
      return Math.max(0.1, Math.min(0.5, next - now));
    },
  };
}

// ---------------------------------------------------------------------------------------------------------------------------
// Bear Druid (Dire Bear Form)
export const DRUID_BEAR = {
  armorMult: 4.6, threat: 1.3, natural: { min: 45, max: 70, speed: 2.5 },                         // armor +360% from the client; the rest ASSUMED
  maul: { cost: 15, flat: 128 }, swipe: { cost: 20, dmg: 83 }, lacerate: { cost: 15, tick: 15, ticks: 5, interval: 3, hit: 10 }, enrage: { rage: 10, cd: 60 },
  naturalReaction: { dodge: 0.01, rage: 5 }, feralSwiftness: { dodge: 0.02 }, thickHide: { armor: 60 }, heartOfTheWild: { sta: 0.04 }, sharpenedClaws: { crit: 0.03 },
  predatoryStrikes: { ap: 30 }, savageFury: { dmg: 0.05 }, feralInstinct: { dmg: 0.10 }, ferocity: { cost: 1 }, shreddingAttacks: { cost: 1 }, bloodFrenzy: { rage: 5, chance: 0.5 },
  leaderOfThePack: { crit: 0.03 },
};
export const DRUID_BEAR_DEFAULT_BUILD = {
  naturalReaction: 0, feralSwiftness: 0, thickHide: 0, heartOfTheWild: 0, sharpenedClaws: 0, predatoryStrikes: 0, savageFury: 0, feralInstinct: 0, ferocity: 0, shreddingAttacks: 0, bloodFrenzy: 0, leaderOfThePack: 0, useSwipe: true,
};

export function druidBearKit(build = {}, data = null) {
  const b = Object.assign({}, DRUID_BEAR_DEFAULT_BUILD, build), B = JSON.parse(JSON.stringify(DRUID_BEAR));
  const mu = pickRank(data, 'druid', null, 'Maul'), sw = pickRank(data, 'druid', null, 'Swipe'), la = pickRank(data, 'druid', null, 'Lacerate'), en = pickRank(data, 'druid', null, 'Enrage');
  if (mu) { B.maul.cost = mu.cost.amount / 10; B.maul.flat = mu.effects.find((e) => e.effect === 58).base; }
  if (sw) { B.swipe.cost = sw.cost.amount / 10; B.swipe.dmg = sw.effects.find((e) => e.effect === 2).base; }
  if (la) { B.lacerate.cost = la.cost.amount / 10; const d = la.effects.find((e) => e.aura === 3); B.lacerate.tick = d.base; B.lacerate.interval = d.period_ms / 1000; B.lacerate.ticks = Math.round(la.duration_ms / d.period_ms); B.lacerate.hit = la.effects.find((e) => e.effect === 3).base; }
  if (en) { B.enrage.cd = en.cooldown_ms / 1000; B.enrage.rage = en.effects.find((e) => e.effect === 30).base / 10; }
  return {
    name: 'druid_bear', build: b, B,
    setup(sim) {
      sim.kitBuild = b; sim.player.resource = 'rage';
      const t = sim.tank, mods = sim.mods;
      sim.player = Object.assign({}, sim.player, { weapons: [{ min: B.natural.min, max: B.natural.max, speed: B.natural.speed, type: '' }], dualWield: false });
      t.armor = t.armor * B.armorMult + B.thickHide.armor * b.thickHide; t.dodge += B.naturalReaction.dodge * b.naturalReaction + B.feralSwiftness.dodge * b.feralSwiftness;
      t.health += 10 * Math.floor((t.stamina || 0) * B.heartOfTheWild.sta * b.heartOfTheWild);
      mods.apBonus += B.predatoryStrikes.ap * b.predatoryStrikes; mods.critBonus += B.sharpenedClaws.crit * b.sharpenedClaws + B.leaderOfThePack.crit * b.leaderOfThePack;
      sim.threatMult = () => B.threat;
      sim.rageCap = 100;
      sim.sEN = sim.addSpell({ name: 'Enrage', cd: B.enrage.cd, cost: () => 0 });
      const maulCost = () => Math.max(0, B.maul.cost - B.ferocity.cost * b.ferocity);
      sim.sMaul = sim.addSpell({ name: 'Maul', cost: maulCost, onSwing(s, sw2) {
        s.spendRage(maulCost()); s.entry('Maul').casts++;
        yellowAttack(s, 'Maul', () => (s.weaponRoll(sw2.w) + s.ap() / 14 * sw2.w.speed + B.maul.flat) * (1 + B.savageFury.dmg * b.savageFury));
      } });
      sim.lacerateUntil = -1; sim.lacerateStacks = 0;
      sim.bossHooks.push((s, out, dmg) => {
        if (dmg > 0) s.gainRage(2.5 * dmg / s.rageC);
        if (out === 'dodge' && b.naturalReaction && s.rng() < b.naturalReaction / 5) s.gainRage(B.naturalReaction.rage);
      });
      sim.procs.push((s, outcome) => { if (outcome === 'crit' && b.bloodFrenzy && s.rng() < B.bloodFrenzy.chance * b.bloodFrenzy) s.gainRage(B.bloodFrenzy.rage); });
    },
    rotate(sim) {
      const now = sim.now, rem = sim.fightLen - now;
      if (now >= sim.sEN.readyAt) { sim.sEN.readyAt = now + B.enrage.cd; sim.entry('Enrage').casts++; sim.gainRage(B.enrage.rage); }
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      const rage = sim.rage, lacCost = Math.max(0, B.lacerate.cost - B.shreddingAttacks.cost * b.shreddingAttacks), swCost = Math.max(0, B.swipe.cost - B.ferocity.cost * b.ferocity);
      if (rage >= lacCost && (now >= sim.lacerateUntil - 2 || sim.lacerateStacks < 5) && rem > 4) {
        return castGcd(sim, spell('Lacerate'), () => {
          sim.spendRage(lacCost);
          const o = yellowAttack(sim, 'Lacerate', () => B.lacerate.hit * (1 + 0));
          if (o === 'miss' || o === 'dodge') return;
          sim.lacerateStacks = Math.min(5, sim.lacerateStacks + 1); sim.lacerateUntil = now + B.lacerate.ticks * B.lacerate.interval;
          const my = (sim.lacToken = (sim.lacToken || 0) + 1); let n = 0;
          const step = () => { if (sim.lacToken !== my) return; sim.record('Lacerate (bleed)', B.lacerate.tick * sim.lacerateStacks * sim.mods.dmgMult, 'hit'); if (++n < B.lacerate.ticks) sim.schedule(B.lacerate.interval, step); else sim.lacerateStacks = 0; };
          sim.schedule(B.lacerate.interval, step);
        }, 1.5);
      }
      if (!sim.mhQueued && rage >= sim.sMaul.cost() + 5) sim.mhQueued = sim.sMaul;
      if (b.useSwipe && rage >= swCost + 10) {
        return castGcd(sim, spell('Swipe'), () => {
          sim.spendRage(swCost);
          yellowAttack(sim, 'Swipe', () => B.swipe.dmg * (1 + B.savageFury.dmg * b.savageFury + B.feralInstinct.dmg * b.feralInstinct));
        }, 1.5);
      }
      return Math.max(0.1, Math.min(0.5, sim.sEN.readyAt - now));
    },
  };
}
