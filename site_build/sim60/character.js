// Turns "base stats + gear + enchants + buffs + consumables + talents" into the player object the
// engine consumes. Also accepts a pre-computed stat block (addon export) via `totals`.
import { RATING_PER_PCT, PLAYER_LEVEL, BASE_WEAPON_SKILL, BOSS_DEFENSE } from './constants.js';
import { BUFFS, CONSUMABLES, DEBUFFS, RACIAL_SKILL } from './presets.js';

// Level-60 Human base stats per class + racial modifiers (Classic 1.12 values, UNVERIFIED against a
// primary source: the figures come from a community summary of the 1.12 database and match the
// racial deltas of the level-1 table already used by the site). The sim page lets the user override
// them and the addon import replaces them with the real in-game totals.
export const BASE_L60_HUMAN = {
  warrior: { str: 120, agi: 80, sta: 110, int: 30, spi: 50 },
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
  warrior: { apPerStr: 2, apPerAgi: 0, apBase: PLAYER_LEVEL * 3 - 20, agiPerCrit: 20, baseCrit: 0 },
};

function sumGear(gear) {
  const t = { str: 0, agi: 0, sta: 0, int: 0, spi: 0, ap: 0, critRating: 0, hitRating: 0, hasteRating: 0, armor: 0, weaponDmg: 0, skill: 0 };
  for (const it of gear) {
    const s = it.st || {};
    for (const k of PRIMARY) t[k] += s[k] || 0;
    t.ap += s.atkpwr || 0;
    t.critRating += s.critstrkrtng || 0;
    t.hitRating += s.hitrtng || 0;
    t.hasteRating += s.hastertng || 0;
    t.armor += s.armor || 0;
    t.skill += s.skill || 0;
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

  let statMult = 1, flatAp = gear.ap, buffCrit = 0, buffHit = 0, buffHaste = 1, apMult = 1;
  const prim = {};
  for (const k of PRIMARY) prim[k] = base[k] + gear[k];
  for (const b of allBuffs) {
    for (const k of PRIMARY) if (b[k]) prim[k] += b[k];
    if (b.statMult) statMult *= b.statMult;
    if (b.ap) flatAp += b.ap;
    if (b.crit) buffCrit += b.crit;
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

  return {
    player: {
      level: PLAYER_LEVEL, resource: 'rage', dualWield: weapons.length > 1,
      stats: { ap, crit, hit, haste, weaponSkill, str: prim.str, agi: prim.agi },
      weapons,
    },
    target: { armor, defense: spec.targetDefense || BOSS_DEFENSE, executeFrac: spec.executeFrac ?? 0.2 },
    summary: { prim, ap, crit, hit, haste, weaponSkill, armor, gearArmor: gear.armor },
  };
}
