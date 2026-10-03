// Turns "base stats + gear + enchants + buffs + consumables + talents" into the player object the
// engine consumes. Also accepts a pre-computed stat block (addon export) via `totals`.
import { RATING_PER_PCT, PLAYER_LEVEL, BASE_WEAPON_SKILL, BOSS_DEFENSE } from './constants.js';
import { BUFFS, CONSUMABLES, DEBUFFS, RACIAL_SKILL } from './presets.js';

// Level-63 boss vs level-60 caster (Classic, ASSUMED): 17% base spell miss; average partial-resist loss 3.75%.
export const TARGET_SPELL_MISS = 0.17, TARGET_SPELL_MITIGATION = 0.0375;

// Level-60 Human base stats per class (str/agi/sta/int/spi) + racial modifiers.
// warrior: Classic 1.12 values, kept as is. Every other class is an ESTIMATE (Classic-style, flagged
// assumed): the Forever planner's sourced LEVEL-30 base (data/wow_items/base_stats_level30.json, race
// removed to Human) pushed to level 60 with L60 = L30 + 1.5 * (L30 - L1). The 1.5 factor is calibrated on
// the Classic warrior (120/80/110/30/46 vs 120/80/110/30/50 known). Shaman has no L30 source: mean growth
// of paladin and druid. The sim page lets the user override them, and the addon import replaces them with
// the real in-game totals.
export const BASE_L60_HUMAN = {
  warrior: { str: 120, agi: 80, sta: 110, int: 30, spi: 50 },
  rogue: { str: 79, agi: 131, sta: 74, int: 35, spi: 51 },
  hunter: { str: 55, agi: 126, sta: 89, int: 65, spi: 70 },
  mage: { str: 30, agi: 35, sta: 45, int: 126, spi: 126 },
  priest: { str: 35, agi: 40, sta: 50, int: 120, spi: 127 },
  warlock: { str: 45, agi: 50, sta: 64, int: 115, spi: 116 },
  paladin: { str: 105, agi: 65, sta: 100, int: 70, spi: 77 },
  druid: { str: 64, agi: 60, sta: 70, int: 100, spi: 111 },
  shaman: { str: 84, agi: 63, sta: 85, int: 85, spi: 94 },
};
export const RACE_MODS = {
  human: { str: 0, agi: 0, sta: 0, int: 0, spi: 0 },
  dwarf: { str: 5, agi: -4, sta: 1, int: -1, spi: -1 },
  nightelf: { str: -4, agi: 4, sta: 0, int: 0, spi: 0 },
  orc: { str: 3, agi: -3, sta: 1, int: -3, spi: 2 },
  tauren: { str: 5, agi: -4, sta: 1, int: -4, spi: 2 },
  undead: { str: -1, agi: -2, sta: 0, int: -2, spi: 5 },
  gnome: { str: -5, agi: 2, sta: 0, int: 3, spi: 0 },
  troll: { str: 1, agi: 2, sta: 0, int: -4, spi: 1 },
};

const PRIMARY = ['str', 'agi', 'sta', 'int', 'spi'];

// Class formulas (Classic): AP from Strength/Agility, crit from Agility.
const CLASS_RULES = {
  warrior: { apPerStr: 2, apPerAgi: 0, apBase: PLAYER_LEVEL * 3 - 20, agiPerCrit: 20, baseCrit: 0, resource: 'rage' },
  rogue: { apPerStr: 1, apPerAgi: 1, apBase: PLAYER_LEVEL * 2 - 20, agiPerCrit: 29, baseCrit: 0, resource: 'energy' },
  // Casters (Classic): spell crit from Intellect, mana from Intellect. baseMana/intPerCrit are ASSUMED Classic values.
  // Hunter: ranged attack power = 2*level - 10 + Agility, crit from Agility (1 per 53), mana from Intellect (ASSUMED Classic values)
  hunter: { ranged: true, apPerStr: 0, apPerAgi: 1, apBase: PLAYER_LEVEL * 2 - 10, agiPerCrit: 53, baseCrit: 0, resource: 'mana', baseMana: 1300, manaPerInt: 15 },
  warlock: { caster: true, intPerCrit: 60.6, baseCrit: 0, baseMana: 1200, manaPerInt: 15, resource: 'mana' },   // ASSUMED Classic values
  mage: { caster: true, intPerCrit: 59.5, baseCrit: 0.002, baseMana: 1213, manaPerInt: 15, resource: 'mana' },
};

function sumGear(gear) {
  const t = { sp: 0, mp5: 0, str: 0, agi: 0, sta: 0, int: 0, spi: 0, ap: 0, critRating: 0, hitRating: 0, hasteRating: 0, armor: 0, weaponDmg: 0, skill: 0 };
  for (const it of gear) {
    const s = it.st || {};
    for (const k of PRIMARY) t[k] += s[k] || 0;
    t.ap += s.atkpwr || 0;
    t.critRating += s.critstrkrtng || 0;
    t.hitRating += s.hitrtng || 0;
    t.hasteRating += s.hastertng || 0;
    t.armor += s.armor || 0;
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
  const rules = CLASS_RULES[cls];
  const base = spec.base || (() => {
    const h = BASE_L60_HUMAN[cls], m = RACE_MODS[race] || RACE_MODS.human, o = {};
    for (const k of PRIMARY) o[k] = h[k] + m[k];
    return o;
  })();
  const gear = sumGear(spec.gear || []);
  const allBuffs = [...(spec.buffs || []).map((id) => BUFFS[id]), ...(spec.consumables || []).map((id) => CONSUMABLES[id])].filter(Boolean);

  let statMult = 1, flatAp = gear.ap, buffCrit = 0, buffHit = 0, buffHaste = 1, apMult = 1, buffSp = 0, buffSpCrit = 0, buffMp5 = 0, buffSpHit = 0;
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

  let ap, crit, hit, haste;
  if (spec.totals) {                      // pre-computed in game (addon export): trust it
    ({ ap, crit, hit } = spec.totals); haste = spec.totals.haste || 1;
  } else {
    ap = (rules.apBase + prim.str * rules.apPerStr + prim.agi * rules.apPerAgi + flatAp) * apMult;
    crit = prim.agi / rules.agiPerCrit / 100 + rules.baseCrit + gear.critRating / RATING_PER_PCT.crit / 100 + buffCrit + (spec.flatCrit || 0);
    hit = gear.hitRating / RATING_PER_PCT.hit / 100 + buffHit + (spec.flatHit || 0);
    haste = buffHaste * (1 + gear.hasteRating / RATING_PER_PCT.haste / 100);
  }

  if (rules.caster) return buildCaster(spec, rules, prim, gear, { buffCrit, buffHit, buffHaste, buffSp, buffSpCrit, buffSpHit, buffMp5 });

  const weapons = (spec.weapons || []).map((w) => Object.assign({}, w));
  for (const w of weapons) if (spec.weaponDmgBonus) { w.min += spec.weaponDmgBonus; w.max += spec.weaponDmgBonus; }
  const consDmg = allBuffs.reduce((a, b) => a + (b.weaponDmg || 0), 0);
  for (const w of weapons) { w.min += consDmg; w.max += consDmg; }

  // Weapon skill for the attack table: 300 + racial bonus for the main-hand weapon type + gear skill.
  const mh = weapons[0];
  const racial = (RACIAL_SKILL[race] || []).includes((mh && mh.type) || '') ? 5 : 0;
  const weaponSkill = BASE_WEAPON_SKILL + racial + gear.skill;

  let armor = spec.targetArmor !== undefined ? spec.targetArmor : 3731;
  for (const id of spec.debuffs || []) { const d = DEBUFFS[id]; if (d && d.armor) armor += d.armor; }
  armor = Math.max(0, armor);

  const extra = rules.ranged ? { int: prim.int, spi: prim.spi, mana: rules.baseMana + rules.manaPerInt * (prim.int - 20), mp5: gear.mp5 + buffMp5 } : {};
  return {
    player: {
      level: PLAYER_LEVEL, resource: rules.resource, dualWield: rules.ranged ? false : weapons.length > 1,
      stats: { ap, crit, hit, haste, weaponSkill, str: prim.str, agi: prim.agi, ...extra },
      weapons: rules.ranged ? [] : weapons, ranged: rules.ranged ? weapons[0] : undefined,
    },
    target: { armor, defense: spec.targetDefense || BOSS_DEFENSE, executeFrac: spec.executeFrac ?? 0.2 },
    summary: { prim, ap, crit, hit, haste, weaponSkill, armor, gearArmor: gear.armor, mana: extra.mana, mp5: extra.mp5, int: prim.int },
  };
}

// Caster stat block. Spell hit is a separate table from melee hit (Classic: 83% base against a level-63 boss,
// +1% per 1% hit up to 99%), applied by the kit; here `hit` is only the bonus from gear/buffs.
function buildCaster(spec, rules, prim, gear, b) {
  const totals = spec.totals;
  const sp = totals ? totals.sp : gear.sp + b.buffSp;
  const crit = totals ? totals.crit : prim.int / rules.intPerCrit / 100 + rules.baseCrit + gear.critRating / RATING_PER_PCT.crit / 100 + b.buffCrit + b.buffSpCrit + (spec.flatCrit || 0);
  const hit = totals ? totals.hit : gear.hitRating / RATING_PER_PCT.hit / 100 + b.buffHit + b.buffSpHit + (spec.flatHit || 0);
  const haste = totals ? (totals.haste || 1) : b.buffHaste * (1 + gear.hasteRating / RATING_PER_PCT.haste / 100);
  const mp5 = totals && totals.mp5 !== undefined ? totals.mp5 : gear.mp5 + b.buffMp5;
  const mana = totals && totals.mana ? totals.mana : rules.baseMana + rules.manaPerInt * (prim.int - 20);
  let resist = spec.targetSpellMitigation !== undefined ? spec.targetSpellMitigation : TARGET_SPELL_MITIGATION;
  let taken = 1;
  for (const id of spec.debuffs || []) { const d = DEBUFFS[id]; if (d && d.spellTaken) taken *= d.spellTaken; }
  return {
    player: { level: PLAYER_LEVEL, resource: 'mana', dualWield: false, stats: { sp, crit, hit, haste, int: prim.int, spi: prim.spi, mana, mp5, weaponSkill: BASE_WEAPON_SKILL, ap: 0 }, weapons: [] },
    target: { armor: 0, defense: BOSS_DEFENSE, executeFrac: spec.executeFrac ?? 0.2, spellMitigation: Math.max(0, resist), spellMiss: TARGET_SPELL_MISS, spellTaken: taken },
    summary: { prim, sp, crit, hit, haste, mana, mp5, spirit: prim.spi, int: prim.int, spellMitigation: Math.max(0, resist) },
  };
}
