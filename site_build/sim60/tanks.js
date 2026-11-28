// Tank kits: Protection Warrior, Protection Paladin and Bear Druid. The fight adds a raid boss that swings at the tank (engine.js _bossSwing:
// Classic attack table of a level-63 mob against the tank's defense, dodge, parry and block, armor mitigation, rage from the damage taken).
// The headline numbers are threat per second (TPS), damage taken per second, avoidance and block. Spell numbers come from the client's rank
// ladders (data/spells60.json: extra) and the Forever talent tooltips. ASSUMED (Classic style): Defensive Stance (+30% threat, -10% damage taken
// and dealt), Righteous Fury (+60% holy threat: from the client), Dire Bear Form threat +30%, the flat threat of Shield Slam, the boss swing
// (2.0 s, 9000 damage, +-15%), Seal of Righteousness' per-swing damage, Holy Shield's 8 charges, the bear's natural weapon, block value 40 + Strength / 20.
// Not simulated: Taunt, Concussion Blow, Shield Wall / Last Stand / Templar's Bulwark (emergency cooldowns), the attack-speed slow of Thunder Clap and the attack power cut of
// Demoralizing Shout / Roar on the mobs.
// Several enemies (sim.nT > 1, the 1 vs 5 targets section of the tank pages): the area abilities hit the first mobs, the single-target ones the main mob; the numbers of the
// area abilities are the game files' read by WoWSims Forever (sim/core/spelldata/spells_auto_gen.go, MIT): Thunder Clap rank 6 (4 mobs, 103 + 7 % AP, spell hit table, threat x1),
// Cleave rank 5 (2 mobs, weapon + 50, 96 flat threat shared by the mobs hit), Consecration rank 5 (8 ticks, 12 Holy on every mob + 27 + 4.2 % SP on the first 4), Swipe rank 5
// (3 mobs, 83 + 3 % AP, threat x1.75 as WoWSims), Demoralizing Shout rank 5 / Roar rank 5 (47.8 / 48.4 threat on every mob at level 60).
import { yellowAttack, castGcd, makeDeepWounds } from './shared.js';
import { setupMana, gainMana, spendMana, spiritRegenPerSec, spellCritMult } from './spells.js';
import { pickRank } from './caster.js';
import { armorDR } from './constants.js';

const spell = (name) => ({ name, cd: 0, readyAt: 0, casts: 0 });

// ---------------------------------------------------------------------------------------------------------------------------
// Protection Warrior
export const WARRIOR_PROT = {
  stance: { threat: 1.8, taken: 0.9, dealt: 0.9 },       // Defensive Stance threat 80% since the notes of 3 Nov 2026 (30% before)
  shieldSlam: { cost: 20, cd: 6, dmg: 655, var: 0.05, threat: 0 },          // no flat threat (Forever: 0 until measured in game)
  revenge: { cost: 5, cd: 5, dmg: 153, var: 0.2, window: 5, threatMult: 2.25, apCoeff: 0.28 },   // threat = 2.25 x damage (Forever, measured in game on rank 2)
  sunder: { cost: 15, threat: 206, apCoeff: 0.05, armor: 450, maxStacks: 5, dur: 30 }, shieldBlock: { cost: 10, cd: 5, dur: 7, charges: 2, block: 0.75 }, heroicStrike: { cost: 15, flat: 157, threat: 152.4 }, bloodrage: { immediate: 10, overTime: 10, cd: 60 },
  shieldSpec: { block: 0.01, rage: 5, chance: 0.2 }, anticipation: { def: 4 }, toughness: { armor: 0.02 }, improvedRevenge: { dmg: 0.2 }, defiance: { threat: 0.2 / 3 },
  bastion: { dmg: 0.02 }, focusedRage: { cost: 1 }, masterOfDefense: { rage: 5, chance: 0.5 }, improvedSunder: { cost: 1 },
  thunderClap: { cost: 20, cd: 6, dmg: 103, apCoeff: 0.07, targets: 4 }, cleave: { cost: 20, flat: 50, targets: 2, threat: 96 }, demoShout: { cost: 10, dur: 45, threat: 47.8 },      // area (several mobs only)
};
export const WARRIOR_PROT_DEFAULT_BUILD = {
  deflection: 0, improvedHeroicStrike: 0, shieldSpec: 0, anticipation: 0, toughness: 0, improvedRevenge: 0, defiance: 0, bastion: 0, focusedRage: 0, masterOfDefense: 0, improvedSunder: 0, shieldSlam: 0, improvedBloodrage: 0,
  useHeroicStrike: true, hsRageReserve: 25, useSunder: true, useRevenge: true, useShieldBlock: true,
};

export function warriorProtKit(build = {}, data = null) {
  const b = Object.assign({}, WARRIOR_PROT_DEFAULT_BUILD, build), W = JSON.parse(JSON.stringify(WARRIOR_PROT));
  const ss = pickRank(data, 'warrior', null, 'Shield Slam'), rv = pickRank(data, 'warrior', null, 'Revenge'), su = pickRank(data, 'warrior', null, 'Sunder Armor'), hs = pickRank(data, 'warrior', null, 'Heroic Strike');
  const rg = (r) => (r.cost ? r.cost.amount / 10 : 0);
  if (ss) { W.shieldSlam.cost = rg(ss); W.shieldSlam.cd = ss.cooldown_ms / 1000; const e = ss.effects.find((x) => x.effect === 2); W.shieldSlam.dmg = e.base; W.shieldSlam.var = e.variance; }
  if (rv) { W.revenge.cost = rg(rv); W.revenge.cd = rv.cooldown_ms / 1000; const e = rv.effects.find((x) => x.effect === 2); W.revenge.dmg = e.base; W.revenge.var = e.variance; }
  if (su) { W.sunder.cost = rg(su); const e = su.effects.find((x) => x.effect === 63); if (e) W.sunder.threat = e.base; }
  if (hs) { W.heroicStrike.cost = rg(hs); W.heroicStrike.flat = hs.effects.find((x) => x.effect === 17).base; }
  const tc = pickRank(data, 'warrior', null, 'Thunder Clap');
  if (tc) { W.thunderClap.cost = rg(tc); W.thunderClap.cd = tc.cooldown_ms / 1000; W.thunderClap.dmg = tc.effects.find((x) => x.effect === 2).base; }
  return {
    name: 'warrior_protection', build: b, W,
    setup(sim) {
      sim.kitBuild = b; sim.player.resource = 'rage';
      const t = sim.tank, mods = sim.mods;
      t.defense += W.anticipation.def * b.anticipation; t.armor *= 1 + W.toughness.armor * b.toughness; t.block += W.shieldSpec.block * b.shieldSpec; t.parry += 0.01 * b.deflection;
      sim.takenMult *= W.stance.taken;
      mods.dmgMult *= W.stance.dealt * (t.shield ? 1 + W.bastion.dmg * b.bastion : 1);
      const tm = W.stance.threat * (1 + (t.shield ? W.defiance.threat * b.defiance : 0));   // Defiance multiplies the stance threat (Forever: 1.3 x 1.15 = 1.494 measured on white hits)
      sim.threatMult = (name) => (name === 'Revenge' ? tm * W.revenge.threatMult : tm);
      sim.rageCap = 100;
      mods.critBonus += 0.01 * (b.cruelty || 0);
      // Deep Wounds (Forever rolling bleed, see shared.js)
      if (b.deepWounds > 0 && sim.player.weapons[0]) {
        const mh0 = sim.player.weapons[0], dw = makeDeepWounds(sim, (mh0.min + mh0.max) / 2, 0.2 * b.deepWounds);
        sim.procs.push((s, outcome) => { if (outcome === 'crit') dw(); });
      }
      sim.sSS = sim.addSpell({ name: 'Shield Slam', cd: W.shieldSlam.cd, cost: () => Math.max(0, W.shieldSlam.cost - W.focusedRage.cost * b.focusedRage) });
      sim.sRV = sim.addSpell({ name: 'Revenge', cd: W.revenge.cd, cost: () => Math.max(0, W.revenge.cost - W.focusedRage.cost * b.focusedRage) });
      sim.sBR = sim.addSpell({ name: 'Bloodrage', cd: W.bloodrage.cd, cost: () => 0 });
      const hsCost = () => Math.max(0, W.heroicStrike.cost - W.focusedRage.cost * b.focusedRage - b.improvedHeroicStrike);
      sim.sHS = sim.addSpell({ name: 'Heroic Strike', cost: hsCost, onSwing(s, sw) {
        s.spendRage(hsCost()); s.entry('Heroic Strike').casts++;
        const o = yellowAttack(s, 'Heroic Strike', () => s.weaponRoll(sw.w) + s.ap() / 14 * sw.w.speed + W.heroicStrike.flat);
        if (o !== 'miss' && o !== 'dodge') s.threat(W.heroicStrike.threat * s.threatMult());      // flat threat of the client row (Forever)
      } });
      // Cleave (several mobs): the next swing hits 2 mobs for weapon + 50; the 96 flat threat is shared by the mobs it lands on (WoWSims heroic_strike_cleave.go)
      const clCost = () => Math.max(0, W.cleave.cost - W.focusedRage.cost * b.focusedRage);
      sim.sCL = sim.addSpell({ name: 'Cleave', cost: clCost, onSwing(s, sw) {
        s.spendRage(clCost()); s.entry('Cleave').casts++;
        const landed = [];
        s.onTargets(W.cleave.targets, (i) => { const o = yellowAttack(s, 'Cleave', () => s.weaponRoll(sw.w) + s.ap() / 14 * sw.w.speed + W.cleave.flat, { refund: i === 0 }); if (o !== 'miss' && o !== 'dodge') landed.push(i); });
        for (const i of landed) { s.tgt = i; s.threat(W.cleave.threat / landed.length * s.threatMult()); }
        s.tgt = 0;
      } });
      sim.rageThreat = (x) => { sim.gainRage(x); sim.threatSplit(5 * x * sim.threatMult()); };      // rage not made by hitting or being hit makes 5 threat each (Forever ThreatPerRageGained), shared by the mobs
      sim.demoUntil = -1;
      sim.revengeUntil = -1;
      // Shield Block (client row 2565): off the global cooldown, +75 % block chance for 7 s or 2 blocks
      sim.sSB = sim.addSpell({ name: 'Shield Block', cd: W.shieldBlock.cd, cost: () => W.shieldBlock.cost });
      sim.sbUntil = -1; sim.sbCharges = 0;
      sim.blockBonus = () => (sim.sbCharges > 0 && sim.now < sim.sbUntil ? W.shieldBlock.block : 0);
      // Sunder Armor stacks (-450 armor each, 30 s, refreshed by every cast); the armor is recomputed on the target when no major armor debuff is already assumed
      sim.sunderStacks = 0; sim.sunderUntil = -1; sim.sunderBaseArmor = sim.target.armor;
      sim.setSunder = (stacks) => { sim.sunderStacks = stacks; if (!sim.target.majorArmorDebuff) sim.dr = armorDR(Math.max(0, sim.sunderBaseArmor - W.sunder.armor * stacks)); };
      sim.bossHooks.push((s, out, dmg) => {
        if (out === 'block' && s.sbCharges > 0 && s.now < s.sbUntil) s.sbCharges--;
        if (dmg > 0) s.gainRage(2.5 * dmg / s.rageC);
        if (out === 'dodge' || out === 'parry' || out === 'block') s.revengeUntil = s.now + W.revenge.window;
        if (out === 'block' && b.shieldSpec && s.rng() < W.shieldSpec.chance * b.shieldSpec) s.rageThreat(W.shieldSpec.rage);
        if ((out === 'dodge' || out === 'parry') && b.masterOfDefense && t.shield && s.rng() < W.masterOfDefense.chance * b.masterOfDefense) s.rageThreat(W.masterOfDefense.rage);
      });
    },
    rotate(sim) {
      const now = sim.now, W2 = W;
      if (now >= sim.sBR.readyAt && sim.rage < 90) {      // Forever: Bloodrage whenever the rage is under 90
        sim.sBR.readyAt = now + W.bloodrage.cd; sim.entry('Bloodrage').casts++;
        const extra = 1 + 0.5 * b.improvedBloodrage / 2;
        sim.rageThreat(W.bloodrage.immediate * extra);
        for (let i = 1; i <= 10; i++) sim.schedule(i, () => sim.rageThreat(W.bloodrage.overTime * extra / 10));
      }
      if (sim.sunderStacks && now >= sim.sunderUntil) sim.setSunder(0);
      if (b.useShieldBlock && sim.tank.shield && now >= sim.sSB.readyAt && sim.rage >= W.shieldBlock.cost
        && (sim.rage >= 40 || (!(now < sim.revengeUntil) && sim.sRV.readyAt - now <= 1.5))) {      // Forever APL: at 40 rage, or to open the Revenge window
        sim.spendRage(W.shieldBlock.cost); sim.sSB.readyAt = now + W.shieldBlock.cd; sim.entry('Shield Block').casts++;
        sim.sbUntil = now + W.shieldBlock.dur; sim.sbCharges = W.shieldBlock.charges;
      }
      const aoe = sim.nT > 1, swingSpell = aoe ? sim.sCL : sim.sHS;
      if (b.useHeroicStrike && !sim.mhQueued && sim.rage >= swingSpell.cost() + b.hsRageReserve && sim.player.weapons.length) sim.mhQueued = swingSpell;
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      const rage = sim.rage, ssCost = sim.sSS.cost(), rvCost = sim.sRV.cost(), suCost = Math.max(0, W.sunder.cost - W.improvedSunder.cost * b.improvedSunder);
      if (aoe) {
        // Thunder Clap on every cooldown: 4 mobs, spell hit table (no melee hit, no crit for a warrior), physical damage through armor, threat 1 x damage
        if (!sim.sTC) sim.sTC = sim.addSpell({ name: 'Thunder Clap', cd: W.thunderClap.cd, cost: () => W.thunderClap.cost });
        if (now >= sim.sTC.readyAt && rage >= W.thunderClap.cost) {
          return castGcd(sim, sim.sTC, () => {
            sim.spendRage(W.thunderClap.cost);
            sim.onTargets(W.thunderClap.targets, () => {
              const e = sim.entry('Thunder Clap');
              if (sim.rng() < sim.target.spellMiss) { e.misses++; return; }
              sim.record('Thunder Clap', sim.mitigate((W.thunderClap.dmg + W.thunderClap.apCoeff * sim.ap()) * sim.mods.dmgMult, true), 'hit');
            });
          });
        }
        if (now >= sim.demoUntil && rage >= W.demoShout.cost) {
          return castGcd(sim, spell('Demoralizing Shout'), () => { sim.spendRage(W.demoShout.cost); sim.demoUntil = now + W.demoShout.dur; sim.onTargets(sim.nT, () => sim.threat(W.demoShout.threat * sim.threatMult())); });
        }
      }
      if (b.shieldSlam && sim.tank.shield && now >= sim.sSS.readyAt && rage >= ssCost) {
        return castGcd(sim, sim.sSS, () => {
          sim.spendRage(ssCost);
          const o = yellowAttack(sim, 'Shield Slam', () => W.shieldSlam.dmg * (1 + W.shieldSlam.var * (sim.rng() - 0.5)) + sim.tank.blockValue, { bonusCrit: -0.01 * (b.cruelty || 0) });   // Cruelty is a weapon crit mod: the shield attack does not get it (Forever)
          if (o !== 'miss' && o !== 'dodge') sim.threat(W.shieldSlam.threat * sim.threatMult());
        });
      }
      if (b.useRevenge && now < sim.revengeUntil && now >= sim.sRV.readyAt && rage >= rvCost) {
        return castGcd(sim, sim.sRV, () => {
          sim.spendRage(rvCost); sim.revengeUntil = -1;
          yellowAttack(sim, 'Revenge', () => (W.revenge.dmg * (1 + W.revenge.var * (sim.rng() - 0.5)) + W.revenge.apCoeff * sim.ap()) * (1 + W.improvedRevenge.dmg * b.improvedRevenge));
        });
      }
      // Sunder Armor: until five stacks, then refreshed in the last 10 s when Shield Slam is not within 1.5 s (Forever APL "Delay Check")
      const sunderDue = sim.sunderStacks < W.sunder.maxStacks || (sim.sSS.readyAt - now >= 1.5 && sim.sunderUntil - now <= 10);
      if (b.useSunder && sunderDue && rage >= suCost) {
        return castGcd(sim, spell('Sunder Armor'), () => {
          sim.spendRage(suCost);
          const o = sim.resolveYellow(0, true);
          if (o === 'miss' || o === 'dodge') { sim.gainRage(suCost); return; }      // a missed Sunder is refunded
          sim.sunderUntil = now + W.sunder.dur; sim.setSunder(Math.min(W.sunder.maxStacks, sim.sunderStacks + 1));
          sim.threat((W.sunder.threat + W.sunder.apCoeff * sim.ap()) * sim.threatMult());
        });
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
  rf: { threat: 1.33, holy: 2.23 }, anticipation: { def: 4 }, toughness: { armor: 0.02 }, precision: { hit: 0.01 }, oneHand: { dmg: 0 }, improvedRf: { taken: 0.03 },
  reckoning: { chance: 0.08 }, redoubt: { chance: 0.02, block: 0.20, blocks: 5, dur: 10 }, ironCreed: { threat: 0.10 }, sacredDuty: { sta: 0.02 },
  manaPotion: { cd: 120, min: 1350, max: 2250 },
  consecration: { cost: 565, cd: 8, ticks: 8, tick: 12, bonus: 27, bonusCoeff: 0.042, bonusTargets: 4 },      // rank 5 (several mobs only)
};
export const PALADIN_PROT_DEFAULT_BUILD = {
  anticipation: 0, toughness: 0, deflection: 0, precision: 0, oneHandWeaponSpecialization: 0, improvedRighteousFury: 0, reckoning: 0, redoubt: 0, ironCreed: 0, sacredDuty: 0, holyShield: 0, swiftJudgement: 0,
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
      t.defense += P.anticipation.def * b.anticipation; t.armor *= 1 + P.toughness.armor * b.toughness; t.parry += 0.01 * b.deflection;
      mods.hitBonus += P.precision.hit * b.precision;
      mods.dmgMult *= 1 + P.oneHand.dmg * b.oneHandWeaponSpecialization;
      sim.takenMult *= 1 - P.improvedRf.taken * b.improvedRighteousFury;
      const HOLY = /Holy|Seal|Judgement|Consecration/;
      sim.threatMult = (name) => (HOLY.test(name) ? P.rf.holy * (name === 'Holy Strike' ? 1 + P.ironCreed.threat * b.ironCreed : 1) : P.rf.threat);      // Righteous Fury (notes, 3 Nov 2026): +33% threat on everything and +90% more on Holy damage (additive)
      setupMana(sim, { manaMax: st.mana, mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int: st.int, spi: st.spi }), castingFraction: 0 });
      sim.baseBlock = t.block; sim.hsUntil = -1; sim.hsCharges = 0; sim.redoubtBlocks = 0; sim.redoubtUntil = -1; sim.sealUntil = -1;
      sim.cd = { hs: 0, holyStrike: 0, judgement: 0, potion: 0 };
      const holy = (name, raw) => {
        const c = Math.max(0, Math.min(1, sim.stats.crit + sim.mods.critBonus - (sim.target.spellCritSuppression || 0))), crit = sim.rng() < c;
        sim.record(name, raw * (sim.mods.dmgMult) * (1 - sim.target.spellMitigation) * sim.target.spellTaken * (crit ? spellCritMult(sim) : 1), crit ? 'crit' : 'hit');
      };
      sim.holy = holy;
      sim.bossHooks.push((s, out, dmg) => {
        // active block bonuses
        if (dmg > 0 && b.redoubt && s.now >= s.redoubtUntil && s.rng() < P.redoubt.chance * b.redoubt) { s.redoubtUntil = s.now + P.redoubt.dur; s.redoubtBlocks = P.redoubt.blocks; }
        if (out === 'block') {
          if (s.now < s.hsUntil && s.hsCharges > 0) { s.hsCharges--; s.entry('Holy Shield').hits++; s.tgt = s.swinger; holy('Holy Shield', P.holyShield.dmg + (st.sp || 0) * 0.0); s.tgt = 0; }      // the blocked mob takes the hit
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
      // Consecration (several mobs): 8 ticks of 1 s, every mob takes 12 Holy, the first 4 also 27 + 4.2 % of the spell power (WoWSims consecration.go)
      if (sim.nT > 1 && now >= (sim.cd.cons || 0) && sim.mana >= P.consecration.cost) {
        const C = P.consecration; sim.cd.cons = now + C.cd; spendMana(sim, C.cost); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry('Consecration').casts++;
        for (let k = 1; k <= C.ticks; k++) sim.schedule(k, () => sim.onTargets(sim.nT, (i) => sim.holy('Consecration', C.tick + (i < C.bonusTargets ? C.bonus + (st.sp || 0) * C.bonusCoeff : 0))));
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
  armorMult: 4.6, threat: 2.15, natural: { min: 45, max: 70, speed: 2.5 },      // threat 1.5: Forever druid.go bearFormThreatMultiplier (was 1.3 ASSUMED)                         // armor +360% from the client; the rest ASSUMED
  maul: { cost: 15, flat: 128 }, swipe: { cost: 20, dmg: 83, apCoeff: 0.03, targets: 3, threat: 1.75 }, demoRoar: { cost: 10, dur: 30, threat: 48.4 }, lacerate: { cost: 15, tick: 15, ticks: 5, interval: 3, hit: 10 }, enrage: { rage: 10, cd: 60 },
  naturalReaction: { dodge: 0.01, rage: 5 }, feralSwiftness: { dodge: 0.02 }, thickHide: { armor: 60 }, heartOfTheWild: { sta: 0.04 }, sharpenedClaws: { crit: 0.03 },
  predatoryStrikes: { ap: 30 }, savageFury: { dmg: 0.05 }, feralInstinct: { dmg: 0.10 }, ferocity: { cost: 1 }, shreddingAttacks: { cost: 1 }, bloodFrenzy: { rage: 5, chance: 0.5 },
  leaderOfThePack: { crit: 0.03 },
};
export const DRUID_BEAR_DEFAULT_BUILD = {
  rendAndTear: 0, naturalReaction: 0, feralSwiftness: 0, thickHide: 0, heartOfTheWild: 0, sharpenedClaws: 0, predatoryStrikes: 0, savageFury: 0, feralInstinct: 0, ferocity: 0, shreddingAttacks: 0, bloodFrenzy: 0, leaderOfThePack: 0, useSwipe: true, usePrimalBite: true, primalBiteThreat: 1,
};

export function druidBearKit(build = {}, data = null) {
  const b = Object.assign({}, DRUID_BEAR_DEFAULT_BUILD, build), B = JSON.parse(JSON.stringify(DRUID_BEAR));
  const pbr = pickRank(data, 'druid', null, 'Primal Bite');
  if (pbr) { B.primalBite = { cost: pbr.cost.amount / 10, cd: pbr.cooldown_ms / 1000, flat: pbr.effects.find((e) => e.effect === 58).base }; }
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
      sim.player = Object.assign({}, sim.player, { weapons: [{ min: sim.stats.catMax ? sim.stats.catMin * B.natural.speed : B.natural.min, max: sim.stats.catMax ? sim.stats.catMax * B.natural.speed : B.natural.max, speed: B.natural.speed, type: '' }], dualWield: false });      // the paw swings the equipped weapon's damage per second at the form's speed
      t.armor = t.armor * B.armorMult + B.thickHide.armor * b.thickHide; t.dodge += B.naturalReaction.dodge * b.naturalReaction + B.feralSwiftness.dodge * b.feralSwiftness;
      t.health += 10 * Math.floor((t.stamina || 0) * B.heartOfTheWild.sta * b.heartOfTheWild);
      mods.apBonus += B.predatoryStrikes.ap * b.predatoryStrikes; mods.critBonus += B.sharpenedClaws.crit * b.sharpenedClaws + B.leaderOfThePack.crit * b.leaderOfThePack;
      sim.threatMult = (name) => B.threat * (name === 'Swipe' ? B.swipe.threat : 1);      // Swipe x1.75 (WoWSims Forever swipe.go)
      sim.rageThreat = (x) => { sim.gainRage(x); sim.threatSplit(5 * x * B.threat); };      // rage not made by hitting or being hit: 5 threat each (Forever), shared by the mobs
      sim.demoUntil = -1;
      sim.rageCap = 100;
      sim.sEN = sim.addSpell({ name: 'Enrage', cd: B.enrage.cd, cost: () => 0 });
      const maulCost = () => Math.max(0, B.maul.cost - B.ferocity.cost * b.ferocity);
      sim.sMaul = sim.addSpell({ name: 'Maul', cost: maulCost, onSwing(s, sw2) {
        s.spendRage(maulCost()); s.entry('Maul').casts++;
        yellowAttack(s, 'Maul', () => (s.weaponRoll(sw2.w) + s.ap() / 14 * sw2.w.speed + B.maul.flat) * (1 + B.savageFury.dmg * b.savageFury) * s.rt());
      } });
      sim.lacerateUntil = -1; sim.lacerateStacks = 0;
      sim.rt = () => (b.rendAndTear && sim.lacerateStacks > 0 && sim.now < sim.lacerateUntil ? 1 + 0.04 * b.rendAndTear : 1);      // Rend and Tear: +4 %/rank on specials and bleed ticks against a bleeding target (Forever feral.go)
      sim.bossHooks.push((s, out, dmg) => {
        if (dmg > 0) s.gainRage(2.5 * dmg / s.rageC);
        if (out === 'dodge' && b.naturalReaction && s.rng() < b.naturalReaction / 5) s.rageThreat(B.naturalReaction.rage);
      });
      sim.procs.push((s, outcome) => { if (outcome === 'crit' && b.bloodFrenzy && s.rng() < B.bloodFrenzy.chance * b.bloodFrenzy) s.gainRage(B.bloodFrenzy.rage); });
    },
    rotate(sim) {
      const now = sim.now, rem = sim.fightLen - now;
      if (now >= sim.sEN.readyAt) { sim.sEN.readyAt = now + B.enrage.cd; sim.entry('Enrage').casts++; sim.rageThreat(B.enrage.rage); }
      if (b.alwaysLacerate && !sim.mhQueued && sim.rage >= sim.sMaul.cost() + 5) sim.mhQueued = sim.sMaul;      // Forever APL: Maul queues (off the global cooldown) at 20 rage
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      const rage = sim.rage, lacCost = Math.max(0, B.lacerate.cost - B.shreddingAttacks.cost * b.shreddingAttacks), swCost = Math.max(0, B.swipe.cost - B.ferocity.cost * b.ferocity);
      const swipeHit = () => sim.onTargets(B.swipe.targets, (i) => yellowAttack(sim, 'Swipe', () => (B.swipe.dmg + B.swipe.apCoeff * sim.ap()) * (1 + B.savageFury.dmg * b.savageFury + B.feralInstinct.dmg * b.feralInstinct), { refund: i === 0 }));
      if (sim.nT > 1) {
        // several mobs: Demoralizing Roar kept up, Swipe (3 mobs) before Lacerate; Primal Bite and Maul stay on the main mob
        if (now >= sim.demoUntil && rage >= B.demoRoar.cost) return castGcd(sim, spell('Demoralizing Roar'), () => { sim.spendRage(B.demoRoar.cost); sim.demoUntil = now + B.demoRoar.dur; sim.onTargets(sim.nT, () => sim.threat(B.demoRoar.threat * B.threat)); }, 1.5);
        if (!(b.usePrimalBite && B.primalBite && now >= (sim.pbAt || 0) && rage >= B.primalBite.cost + 2) && rage >= swCost) {
          if (!sim.mhQueued && rage >= sim.sMaul.cost() + swCost + 5) sim.mhQueued = sim.sMaul;
          return castGcd(sim, spell('Swipe'), () => { sim.spendRage(swCost); swipeHit(); }, 1.5);
        }
      }
      if (b.alwaysLacerate && rage >= lacCost && !(b.usePrimalBite && B.primalBite && now >= (sim.pbAt || 0) && rage >= B.primalBite.cost + 2)) {      // Forever APL: Lacerate whenever the rage allows (the stacks refresh the bleed)
        const w0 = sim.player.weapons[0];
        return castGcd(sim, spell('Lacerate'), () => {
          sim.spendRage(lacCost);
          const ex = sim.lacerateStacks;
          const o = yellowAttack(sim, 'Lacerate', () => (sim.weaponRoll(w0) + sim.ap() / 14 * w0.speed) * (B.lacerate.hit / 100) * ex * sim.rt());
          if (o === 'miss' || o === 'dodge') return;
          sim.lacerateStacks = Math.min(5, sim.lacerateStacks + 1); sim.lacerateUntil = now + B.lacerate.ticks * B.lacerate.interval;
          const my = (sim.lacToken = (sim.lacToken || 0) + 1); let n = 0;
          const step = () => { if (sim.lacToken !== my) return; sim.record('Lacerate (bleed)', B.lacerate.tick * sim.lacerateStacks * sim.mods.dmgMult * sim.rt(), 'hit'); if (++n < B.lacerate.ticks) sim.schedule(B.lacerate.interval, step); else sim.lacerateStacks = 0; };
          sim.schedule(B.lacerate.interval, step);
        }, 1.5);
      }
      if (!b.alwaysLacerate && rage >= lacCost && (now >= sim.lacerateUntil - 2 || sim.lacerateStacks < 5) && rem > 4) {
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
      // Primal Bite (Feral talent): the rage spender on a 6 s cooldown, instant, high threat (the client does not quantify it: primalBiteThreat)
      if (b.usePrimalBite && B.primalBite && now >= (sim.pbAt || 0) && rage >= B.primalBite.cost + 2) {
        return castGcd(sim, spell('Primal Bite'), () => {
          sim.spendRage(B.primalBite.cost); sim.pbAt = now + B.primalBite.cd;
          const w = sim.player.weapons[0];
          const o = yellowAttack(sim, 'Primal Bite', () => ((w ? sim.weaponRoll(w) + sim.ap() / 14 * w.speed : 0) + B.primalBite.flat) * sim.rt());
          if (o !== 'miss' && o !== 'dodge' && b.primalBiteThreat > 1) sim.threat(B.primalBite.flat * (b.primalBiteThreat - 1) * sim.threatMult());
        }, 1.5);
      }
      if (!sim.mhQueued && rage >= sim.sMaul.cost() + 5) sim.mhQueued = sim.sMaul;
      if (b.useSwipe && rage >= swCost + 10) {
        return castGcd(sim, spell('Swipe'), () => {
          sim.spendRage(swCost);
          swipeHit();
        }, 1.5);
      }
      return Math.max(0.1, Math.min(0.5, sim.sEN.readyAt - now));
    },
  };
}
