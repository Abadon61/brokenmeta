// Mechanics constants for a level-60 character against a level-63 raid boss.
// WoW: Forever is Classic-derived (confirmed on every mechanic checked so far: Rage formula, 1.12
// attack table, +hit/+crit as ratings like TBC). Each value below says where it comes from;
// "ASSUMED" = Classic 1.12 value kept until a Forever source exists (flagged on the public page).

export const PLAYER_LEVEL = 60;
export const BOSS_LEVEL = 63;
export const BOSS_DEFENSE = BOSS_LEVEL * 5;          // 315
export const BASE_WEAPON_SKILL = PLAYER_LEVEL * 5;   // 300

// Rating conversions at level 60 (Forever items carry critstrkrtng/hitrtng/hastertng/defrtng;
// 14 crit rating = 1% and 10 hit rating = 1% match the beta's own level-20..60 items, e.g. "Quick
// Strike Ring: +14 crit rating", "Blackstone Ring: +10 hit rating"). Haste rating: ASSUMED 10 per 1%.
export const RATING_PER_PCT = { crit: 14, hit: 10, haste: 10, defense: 4 };

// Rage conversion value c(level) (community-derived formula, lands on the known 230.6 at level 60).
export function rageConversion(level) {
  return 0.0091107836 * level * level + 3.225598133 * level + 4.2652911;
}
export const RAGE_CAP = 100;
export const HIT_FACTOR = { mh: { normal: 3.5, crit: 7.0 }, oh: { normal: 1.75, crit: 3.5 } };

// Crit damage: Classic melee/ranged 200%, spells 150% (Wowhead "Stats and Attributes", Classic).
export const CRIT_MULT_PHYSICAL = 2.0;
export const CRIT_MULT_SPELL = 1.5;

// Armor mitigation: DR = armor / (armor + 400 + 85 * attackerLevel), 75% cap (Classic).
export function armorDR(armor, attackerLevel = PLAYER_LEVEL) {
  const dr = armor / (armor + 400 + 85 * attackerLevel);
  return Math.max(0, Math.min(0.75, dr));
}

// Melee attack table vs a boss, Classic 1.12 (the formulas the previous level-60 engine of this
// site already used and sourced): with D = defense - weaponSkill (15 at skill 300 vs a lvl-63 boss):
//   miss  = 5% + D*0.1%   if D <= 10,  else 7% + (D-10)*0.4%      -> 9% at D = 15
//   dodge = 5% + D*0.1%                                           -> 6.5%
//   glance chance = 10% + D*2%                                    -> 40% (white swings only)
//   glance damage multiplier ~ U(low, high), low = min(0.91, 1.3-0.05D), high = min(0.99, 1.2-0.03D)
//   crit suppression = 0.2% * D + 1.8%  (ASSUMED Classic: 4.8% at D = 15)
// Dual-wield adds a flat 19% miss to WHITE swings only (specials are unaffected).
export function meleeTable(weaponSkill, targetDefense = BOSS_DEFENSE) {
  const D = Math.max(0, targetDefense - weaponSkill);
  const miss = D <= 10 ? 0.05 + D * 0.001 : 0.07 + (D - 10) * 0.004;
  const dodge = 0.05 + D * 0.001;
  const glance = Math.max(0, 0.10 + D * 0.02);
  const low = Math.max(0.01, Math.min(0.91, 1.3 - 0.05 * D));
  const high = Math.max(low, Math.min(0.99, 1.2 - 0.03 * D));
  const critSuppression = D > 0 ? 0.002 * D + 0.018 : 0;
  return { miss, dodge, glance, glanceLow: low, glanceHigh: high, critSuppression };
}
export const DUAL_WIELD_MISS_PENALTY = 0.19;
export const OVERPOWER_WINDOW = 5.0;
export const GCD = 1.5;
