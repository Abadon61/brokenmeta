// Turns "base stats + gear + enchants + buffs + consumables + talents" into the player object the
// engine consumes. Also accepts a pre-computed stat block (addon export) via `totals`.
import { RATING_PER_PCT, PLAYER_LEVEL, BASE_WEAPON_SKILL, BOSS_DEFENSE } from './constants.js';
import { BUFFS, CONSUMABLES, DEBUFFS, RACIAL_SKILL } from './presets.js';
import { racialsFor } from './racials.js';
import { resolveEffects } from './effects.js';

// Level-63 boss vs level-60 caster (WoWSims, sim/core/target.go and spell_resistances.go): 17% base spell miss, 2.1% spell crit suppression, average partial-resist loss
// 0.02 per level of difference x 4/3 x 3 levels / ... = 6% for a spell with a direct hit (a pure damage-over-time spell loses a tenth of it: 0.6%).
export const TARGET_SPELL_MISS = 0.17, TARGET_SPELL_MITIGATION = 0.06, SPELL_CRIT_SUPPRESSION = 0;      // Forever core/spell_result.go SpellCritChance has no level suppression (was 2.1 %)

// Level-60 Human base stats per class (str/agi/sta/int/spi) and race offsets: the Classic values of WoWSims (sim/core/base_stats.go, ClassBaseStats and RaceOffsets,
// MIT licence, github.com/wowsims/classic), adopted 2026-10-16 in place of the earlier estimates (level-30 planner data pushed to level 60). Forever has not published its own
// level-60 base stats: the page lets the user override them, and the addon import replaces them with the real in-game totals. The Skyborne have no offsets (human stats).
export const BASE_L60_HUMAN = {
  warrior: { str: 120, agi: 80, sta: 110, int: 30, spi: 45 },
  rogue: { str: 80, agi: 130, sta: 75, int: 35, spi: 50 },
  hunter: { str: 55, agi: 125, sta: 90, int: 65, spi: 70 },
  mage: { str: 30, agi: 35, sta: 45, int: 125, spi: 120 },
  priest: { str: 35, agi: 40, sta: 50, int: 120, spi: 125 },
  warlock: { str: 45, agi: 50, sta: 65, int: 110, spi: 115 },
  paladin: { str: 105, agi: 65, sta: 100, int: 70, spi: 75 },
  druid: { str: 65, agi: 60, sta: 70, int: 100, spi: 110 },
  shaman: { str: 85, agi: 55, sta: 95, int: 90, spi: 100 },
};
export const RACE_MODS = {
  human: { str: 0, agi: 0, sta: 0, int: 0, spi: 0 },
  dwarf: { str: 2, agi: -4, sta: 3, int: -1, spi: -1 },
  nightelf: { str: -3, agi: 5, sta: -1, int: 0, spi: 0 },
  orc: { str: 3, agi: -3, sta: 2, int: -3, spi: 3 },
  tauren: { str: 5, agi: -5, sta: 2, int: -5, spi: 2 },
  undead: { str: -1, agi: -2, sta: 1, int: -2, spi: 5 },
  gnome: { str: -5, agi: 3, sta: -1, int: 3, spi: 0 },
  troll: { str: 1, agi: 2, sta: 1, int: -4, spi: 1 },
};

const PRIMARY = ['str', 'agi', 'sta', 'int', 'spi'];

// Class formulas (Classic): AP from Strength/Agility, crit from Agility.
const CLASS_RULES = {
  warrior: { apPerStr: 2, apPerAgi: 0, apBase: PLAYER_LEVEL * 3 - 20, agiPerCrit: 20, baseCrit: 0, resource: 'rage' },
  rogue: { apPerStr: 1, apPerAgi: 1, apBase: PLAYER_LEVEL * 2 - 20, agiPerCrit: 29, baseCrit: 0, resource: 'energy' },
  // Casters (Classic): spell crit from Intellect, mana from Intellect. baseMana/intPerCrit are ASSUMED Classic values.
  // Hunter: ranged attack power = 2*level - 10 + Agility, crit from Agility (1 per 53), mana from Intellect (ASSUMED Classic values)
  hunter: { ranged: true, apPerStr: 0, apPerAgi: 2, apBase: PLAYER_LEVEL * 2 - 20, agiPerCrit: 52.9, baseCrit: 0, resource: 'mana', baseMana: 1720, manaPerInt: 15 },   // WoWSims: 2 ranged attack power per Agility, base 100
  // Tanks: attack power like the DPS version, plus the defensive block (ASSUMED Classic-style values: base health 1500 + 10 per Stamina, 5% parry/block with a
  // shield, dodge from Agility, block value 40 + Strength / 20 when a shield is worn).
  warrior_protection: { tank: { parry: 0.05, block: 0.05, dodgeBase: 0.0075, agiPerDodge: 20, baseHealth: 1500, bvBase: 40 }, apPerStr: 2, apPerAgi: 0, apBase: PLAYER_LEVEL * 3 - 20, agiPerCrit: 20, baseCrit: 0, resource: 'rage' },
  paladin_protection: { tank: { parry: 0.05, block: 0.05, dodgeBase: 0.0075, agiPerDodge: 20, baseHealth: 1500, bvBase: 40 }, manaUser: true, apPerStr: 2, apPerAgi: 0, apBase: PLAYER_LEVEL * 3 - 20, agiPerCrit: 19.8, baseCrit: 0.007, resource: 'mana', baseMana: 1512, manaPerInt: 15 },
  druid_bear: { tank: { parry: 0, block: 0, dodgeBase: 0, agiPerDodge: 14.7, baseHealth: 1500, bvBase: 0 }, stick: true, apPerStr: 2, apPerAgi: 0, apBase: PLAYER_LEVEL * 3 - 20, agiPerCrit: 20, baseCrit: 0, resource: 'rage' },
  // Melee classes with mana (Paladin, Enhancement) and the cat: attack power 2 per Strength (+3 per level for the Paladin), crit from Agility 1/20
  paladin: { manaUser: true, apPerStr: 2, apPerAgi: 0, apBase: PLAYER_LEVEL * 3 - 20, agiPerCrit: 19.8, baseCrit: 0.007, resource: 'mana', baseMana: 1512, manaPerInt: 15 },
  shaman_enhancement: { manaUser: true, apPerStr: 2, apPerAgi: 0, apBase: PLAYER_LEVEL * 2 - 20, agiPerCrit: 19.7, baseCrit: 0.017, resource: 'mana', baseMana: 1520, manaPerInt: 15 },
  druid_feral: { stick: true, manaUser: true, baseMana: 1244, manaPerInt: 15, apPerStr: 2, apPerAgi: 1, apBase: PLAYER_LEVEL * 2 - 20, agiPerCrit: 20, baseCrit: 0.009, resource: 'energy' },
  // Caster values (WoWSims: ClassBaseStats mana, ClassBaseCrit spell crit, CritPerIntAtLevel)
  priest: { caster: true, intPerCrit: 59.5, baseCrit: 0.008, baseMana: 1376, manaPerInt: 15, resource: 'mana' },
  shaman: { caster: true, intPerCrit: 59.2, baseCrit: 0.023, baseMana: 1520, manaPerInt: 15, resource: 'mana' },
  druid: { caster: true, intPerCrit: 59.9, baseCrit: 0.018, baseMana: 1244, manaPerInt: 15, resource: 'mana' },
  hunter_melee: { manaUser: true, apPerStr: 1, apPerAgi: 1, apBase: PLAYER_LEVEL * 2 - 20, agiPerCrit: 52.9, baseCrit: 0, resource: 'mana', baseMana: 1720, manaPerInt: 15 },
  warlock: { caster: true, intPerCrit: 60.6, baseCrit: 0.017, baseMana: 1373, manaPerInt: 15, resource: 'mana' },
  mage: { caster: true, intPerCrit: 59.5, baseCrit: 0.002, baseMana: 1213, manaPerInt: 15, resource: 'mana' },
};

function sumGear(gear) {
  const t = { defRating: 0, dodgePct: 0, shield: false, sp: 0, mp5: 0, str: 0, agi: 0, sta: 0, int: 0, spi: 0, ap: 0, critRating: 0, hitRating: 0, hasteRating: 0, armor: 0, weaponDmg: 0, skill: 0 };
  for (const it of gear) {
    const s = it.st || {};
    for (const k of PRIMARY) t[k] += s[k] || 0;
    t.ap += s.atkpwr || 0;
    t.critRating += s.critstrkrtng || 0;
    t.hitRating += s.hitrtng || 0;
    t.hasteRating += s.hastertng || 0;
    t.armor += (s.armor || 0) + (s.armorbonus || 0);
    t.bv = (t.bv || 0) + (s.blockvalue || 0); t.exp = (t.exp || 0) + (s.exprtng || 0); t.catMin = (t.catMin || 0) + (s.catMin || 0); t.catMax = (t.catMax || 0) + (s.catMax || 0); t.defRating += s.defrtng || 0; t.dodgePct += s.dodgepct || 0;
    if (it.slot === 'shield') t.shield = true;
    t.skill += s.skill || 0;
    t.sp += (s.splpwr || 0) + (s.spldmg || 0);
    t.mp5 += s.manargn || 0;
  }
  return t;
}

/**
 * spec: { class:'warrior', race:'human', base?:{...}, gear:[item...], weapons:[{min,max,speed,offHand?,twoHand?,type?}],
 *         buffs:[ids], consumables:[ids], debuffs:[ids], flatCrit?, flatHit?, talentCrit?, talentHit?, totals? }
 */
export function buildCharacter(spec) {
  const cls = spec.class || 'warrior', race = spec.race || 'human';
  // The racials are the ones read from the beta client (racials.js), which replace the Classic weapon-skill bonus (Forever's weapon specializations give
  // critical strike chance instead); spec.racialModel === 'classic' brings the old Classic model back (tests, comparisons). spec.weaponTypes lists the equipped weapon types.
  const rm = spec.racialModel !== 'classic' ? racialsFor(race, spec.weaponTypes || (spec.weapons || []).map((w) => w.type)) : null;
  if (rm) spec = Object.assign({}, spec, { flatCrit: (spec.flatCrit || 0) + rm.crit, flatHit: (spec.flatHit || 0) + rm.hit, racialManaMult: rm.manaMult, racialUse: rm.use, racialCritDmg: rm.critDmg });
  const rules = CLASS_RULES[spec.variant ? cls + '_' + spec.variant : cls] || CLASS_RULES[cls];
  const base = spec.base || (() => {
    const h = BASE_L60_HUMAN[cls], m = RACE_MODS[race] || RACE_MODS.human, o = {};
    for (const k of PRIMARY) o[k] = h[k] + m[k];
    return o;
  })();
  // the stats of the weapons (Strength, Agility, crit, hit...) count like any other item; they were left out when the weapons were passed apart from the gear
  const gear = sumGear([...(spec.gear || []), ...(spec.weapons || []).filter((w) => w.st).map((w) => ({ slot: 'weapon', st: w.st }))]);
  // item effects (spec.effects = data/effects.json): passive stats now, on-use buffs and procs handed to the engine
  const fxIds = [...(spec.gear || []).map((g) => g.id), ...(spec.weapons || []).map((w) => w.itemId)].filter(Boolean);
  const weaponOf = {};
  (spec.weapons || []).forEach((w, i) => { if (w.itemId) weaponOf[w.itemId] = rules.ranged ? 'ranged' : (w.offHand || i > 0 ? 'oh' : 'mh'); });
  const fxr = spec.effects ? resolveEffects(spec.effects, fxIds, rules.caster ? {} : weaponOf, !!rules.caster) : null;
  if (fxr) {
    const p = fxr.passive;
    gear.ap += p.ap; gear.sp += p.sp; gear.mp5 += p.mp5;
    for (const k of ['str', 'agi', 'sta', 'int', 'spi']) gear[k] += p[k];
  }
  const allBuffs = [...(spec.buffs || []).map((id) => BUFFS[id]), ...(spec.consumables || []).map((id) => CONSUMABLES[id])].filter(Boolean);

  let statMult = 1, flatAp = gear.ap, buffCrit = fxr ? fxr.passive.crit : 0, buffHit = fxr ? fxr.passive.hit : 0, buffHaste = 1, apMult = 1, buffSp = 0, buffSpCrit = 0, buffMp5 = 0, buffSpHit = 0;
  const prim = {};
  for (const k of PRIMARY) prim[k] = base[k] + gear[k];
  for (const b of allBuffs) {
    for (const k of PRIMARY) if (b[k]) prim[k] += b[k];
    if (b.statMult) statMult *= b.statMult;
    if (b.ap) flatAp += b.ap;
    if (b.crit && !(rules.caster && b.meleeOnly)) buffCrit += b.crit;
    if (b.sp) buffSp += b.sp;
    if (b.spCrit) buffSpCrit += b.spCrit;
    if (b.spHit) buffSpHit += b.spHit;
    if (b.mp5) buffMp5 += b.mp5;
    if (b.hit) buffHit += b.hit;
    if (b.haste) buffHaste *= b.haste;
    if (b.apMult) apMult *= b.apMult;
  }
  for (const k of PRIMARY) prim[k] = Math.floor(prim[k] * statMult);
  if (rm) { prim.spi = Math.floor(prim.spi * rm.spiritMult); buffHaste *= rm.haste; }

  let ap, crit, hit, haste;
  if (spec.totals) {                      // pre-computed in game (addon export): trust it
    ({ ap, crit, hit } = spec.totals); haste = spec.totals.haste || 1;
  } else {
    ap = (rules.apBase + prim.str * rules.apPerStr + prim.agi * rules.apPerAgi + flatAp) * apMult;
    crit = prim.agi / rules.agiPerCrit / 100 + rules.baseCrit + gear.critRating / RATING_PER_PCT.crit / 100 + buffCrit + (spec.flatCrit || 0);
    hit = gear.hitRating / RATING_PER_PCT.hit / 100 + buffHit + (spec.flatHit || 0);
    haste = buffHaste * (1 + gear.hasteRating / RATING_PER_PCT.haste / 100);
  }

  if (rules.caster) return buildCaster(spec, rules, prim, gear, fxr, { buffCrit, buffHit, buffHaste, buffSp, buffSpCrit, buffSpHit, buffMp5 });

  const weapons = (spec.weapons || []).map((w) => Object.assign({}, w));
  for (const w of weapons) if (spec.weaponDmgBonus) { w.min += spec.weaponDmgBonus; w.max += spec.weaponDmgBonus; }
  const consDmg = allBuffs.reduce((a, b) => a + (b.weaponDmg || 0), 0);
  for (const w of weapons) { w.min += consDmg; w.max += consDmg; }

  // Weapon skill for the attack table: 300 + racial bonus for the main-hand weapon type + gear skill.
  const mh = weapons[0];
  const racial = !rm && (RACIAL_SKILL[race] || []).includes((mh && mh.type) || '') ? 5 : 0;
  const weaponSkill = BASE_WEAPON_SKILL + racial + gear.skill;

  let armor = spec.targetArmor !== undefined ? spec.targetArmor : 3731;
  // armor debuffs of one family do not stack (measured on WoWSims Forever: Sunder + Faerie Fire + Curse of Recklessness = -2250 - 505, not -3260):
  // the strongest of Sunder Armor / Expose Armor, plus the strongest of Faerie Fire / Curse of Recklessness
  { const fam = { sunder_armor_5: 'major', expose_armor: 'major', faerie_fire: 'minor', curse_of_recklessness: 'minor' }, best = {};
    for (const id of spec.debuffs || []) { const d = DEBUFFS[id]; if (!d || !d.armor) continue; const f = fam[id] || id; if (!best[f] || d.armor < best[f]) best[f] = d.armor; }
    for (const v of Object.values(best)) armor += v;
    var majorArmorDebuff = !!best.major; }
  armor = Math.max(0, armor);

  const tank = rules.tank ? {
    armor: gear.armor, health: rules.tank.baseHealth + 10 * prim.sta, defense: 300 + Math.floor(gear.defRating / RATING_PER_PCT.defense),
    dodge: rules.tank.dodgeBase + prim.agi / rules.tank.agiPerDodge / 100 + gear.dodgePct / 100, parry: rules.tank.parry, block: rules.tank.block,
    blockValue: gear.shield ? rules.tank.bvBase + prim.str / 20 + (gear.bv || 0) : 0, shield: gear.shield, stamina: prim.sta,
  } : undefined;
  const extra = rules.ranged || rules.manaUser ? { int: prim.int, spi: prim.spi, mana: (rules.baseMana + rules.manaPerInt * (prim.int - 20)) * (spec.racialManaMult || 1), mp5: gear.mp5 + buffMp5, sp: gear.sp + buffSp } : {};
  return {
    player: {
      level: PLAYER_LEVEL, resource: rules.resource, dualWield: rules.ranged || rules.stick ? false : weapons.length > 1,
      stats: { catMin: gear.catMin || 0, catMax: gear.catMax || 0, racialCrit: spec.flatCrit || 0, expertise: gear.exp || 0, ap, crit, critAura: Math.max(0, crit - prim.agi / rules.agiPerCrit / 100 - rules.baseCrit), hit, haste, weaponSkill, str: prim.str, agi: prim.agi, ...extra },
      weapons: rules.ranged || rules.stick ? [] : weapons, ranged: rules.ranged ? weapons[0] : undefined,
      effects: effectsOf(fxr, spec), tank, racialCritDmg: spec.racialCritDmg || 0,
    },
    target: { majorArmorDebuff: typeof majorArmorDebuff === 'undefined' ? false : majorArmorDebuff, boss: tank ? Object.assign({ speed: 2.0, dmg: 9000, var: 0.15, level: 63 }, spec.boss || {}) : undefined, armor, defense: spec.targetDefense || BOSS_DEFENSE, executeFrac: spec.executeFrac ?? 0.2, spellMiss: TARGET_SPELL_MISS, spellMitigation: TARGET_SPELL_MITIGATION, spellCritSuppression: SPELL_CRIT_SUPPRESSION, spellTaken: 1 },
    summary: { prim, ap, crit, hit, haste, weaponSkill, armor, gearArmor: gear.armor, mana: extra.mana, mp5: extra.mp5, int: prim.int, effects: fxr ? fxr.applied : [], tank },
  };
}

// item effects plus the on-use racial of the Forever racial model (Blood Fury, Elune's Light, Berserking), as the engine's list of on-use effects
function effectsOf(fxr, spec) {
  const u = spec.racialUse ? [{ source: 'race', name: spec.racialUse.name, payload: Object.assign({ kind: 'racial' }, spec.racialUse), cd: spec.racialUse.cd, start: spec.racialUse.start }] : [];
  return fxr || u.length ? { uses: (fxr ? fxr.uses : []).concat(u), procs: fxr ? fxr.procs : [] } : undefined;
}

// Caster stat block. Spell hit is a separate table from melee hit (Classic: 83% base against a level-63 boss,
// +1% per 1% hit up to 99%), applied by the kit; here `hit` is only the bonus from gear/buffs.
function buildCaster(spec, rules, prim, gear, fxr, b) {
  const totals = spec.totals;
  const sp = totals ? totals.sp : gear.sp + b.buffSp;
  const crit = totals ? totals.crit : prim.int / rules.intPerCrit / 100 + rules.baseCrit + gear.critRating / RATING_PER_PCT.crit / 100 + b.buffCrit + b.buffSpCrit + (spec.flatCrit || 0);
  const hit = totals ? totals.hit : gear.hitRating / RATING_PER_PCT.hit / 100 + b.buffHit + b.buffSpHit + (spec.flatHit || 0);
  const haste = totals ? (totals.haste || 1) : b.buffHaste * (1 + gear.hasteRating / RATING_PER_PCT.haste / 100);
  const mp5 = totals && totals.mp5 !== undefined ? totals.mp5 : gear.mp5 + b.buffMp5;
  const mana = totals && totals.mana ? totals.mana : (rules.baseMana + rules.manaPerInt * (prim.int - 20)) * (spec.racialManaMult || 1);
  let resist = spec.targetSpellMitigation !== undefined ? spec.targetSpellMitigation : TARGET_SPELL_MITIGATION;
  let taken = 1;
  for (const id of spec.debuffs || []) { const d = DEBUFFS[id]; if (d && d.spellTaken) taken *= d.spellTaken; }
  return {
    player: { level: PLAYER_LEVEL, resource: 'mana', dualWield: false, stats: { sp, crit, hit, haste, int: prim.int, spi: prim.spi, mana, mp5, weaponSkill: BASE_WEAPON_SKILL, ap: 0 }, weapons: [], effects: effectsOf(fxr, spec), racialCritDmg: spec.racialCritDmg || 0 },
    target: { armor: 0, defense: BOSS_DEFENSE, executeFrac: spec.executeFrac ?? 0.2, spellMitigation: Math.max(0, resist), spellMiss: TARGET_SPELL_MISS, spellCritSuppression: SPELL_CRIT_SUPPRESSION, spellTaken: taken },
    summary: { prim, sp, crit, hit, haste, mana, mp5, spirit: prim.spi, int: prim.int, spellMitigation: Math.max(0, resist), effects: fxr ? fxr.applied : [] },
  };
}
