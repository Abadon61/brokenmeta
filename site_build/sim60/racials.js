// Racial abilities of WoW: Forever as the simulator applies them (spec.racialModel === 'forever').
// Every number is read from the beta client tables (data/wow_racials.json, build 1.60.1.70425 = the beta patch of 2026-10-16, which reworked the racials; spell ids in
// the comments): Forever replaced the Classic weapon-skill bonuses (weapon specializations) by flat critical strike chance or critical damage, and added racials such as Elune's Light.
// Racial effects that do not change damage on a single target (resistances, movement, escapes, stealth detection, gathering) are not listed.
// NOT simulated: the Gnome's +5% maximum energy / rage and the -10% resource cost of Eureka! (only its +10% damage on direct hits is), the Undead Touch of the Grave (it drains
// health: 30% / 20% chance, 25 s internal cooldown, up to 5% of the player's maximum health, so a few DPS at most), Tauren +5% health, bonuses against Beasts (Troll Beast Slaying,
// Dwarf Big Game Hunter) and Elementals (Skyborne Elemental Insight): the fight is against a single humanoid-like boss.
// critDmg = "critical strike bonus to damage increased by X%": scales the bonus part of a critical strike (physical 2.0 -> 2.0 + X, spell 1.5 -> 1.5 + X / 2), like Impale / Ice Shards.
// 2026-10-27: the values below follow Blizzard's racial tuning pass for the launch (posts of 2026-10-26 and 2026-10-27, relayed by Wowhead; data/wow_racials_announced.json), which the
// client tables above (build 1.60.1.70425) do not carry yet: Human Ruthless 1% crit (was 2%) and Spirit +10% (was 5%); Dwarf Earth Fury removed, Artisan's Precision +1% hit added; Tauren
// Endurance only +5% health (no critical damage); Orc Savage removed, Command re-added (+5% damage of Warlock and Hunter pets), Blood Fury cooldown 2 min (was 3); Troll Berserking 15 s
// (was 10); Undead Touch of the Grave internal cooldown 15 s (was 25, still not simulated); Skyborne Wind Blessed 2% haste (was 3%). Read Leyline and Skysight (regeneration, movement) are not simulated.
export const FOREVER_RACIALS = {
  human: { crit: 0.01, spiritMult: 1.10 },                                                                                           // 20597 Ruthless (+1% critical strike chance, any weapon), 20598 The Human Spirit (+10% Spirit)
  orc: { petDmg: 0.05, use: { name: 'Blood Fury', cd: 120, duration: 15, apMult: 1.10, spMult: 1.10 } },                              // Command (+5% Warlock / Hunter pet damage), 20572 Blood Fury (cooldown 2 min since 2026-10-27); 20574 Savage removed
  dwarf: { hit: 0.01 },                                                                                                               // Artisan's Precision (+1% hit chance with spells and attacks); 1259719 Earth Fury removed
  nightelf: { use: { name: "Elune's Light", cd: 180, duration: 15, crit: 0.10 } },                                                    // 1259799
  tauren: {},                                                                                                                         // 20550 Endurance: +5% health only since 2026-10-27 (no more critical damage; the health is not simulated)
  gnome: { manaMult: 1.05, use: { name: 'Eureka!', cd: 120, duration: 8, dmgMult: 1.10 } },                                           // 20591 Expansive Mind (maximum mana), 1259812 Eureka! (8 s, +10% damage, -10% cost)
  troll: { use: { name: 'Berserking', cd: 180, duration: 15, haste: 1.10 } },                                                         // 20554 (spellcasting and attack speed +10% for 15 s since 2026-10-27, was 10 s)
  skyborne: { haste: 1.02 },                                                                                                          // 1259710 Wind Blessed (2% haste since 2026-10-27, was 3%)
  undead: {},
};

/** The part of a race's model that applies to this character: flat crit, critical damage, hit, haste, spirit, mana, pet damage and the on-use racial. `weaponTypes` is kept for callers that still pass it. */
export function racialsFor(race, weaponTypes) {
  const r = FOREVER_RACIALS[race] || {};
  return { crit: r.crit || 0, critDmg: r.critDmg || 0, hit: r.hit || 0, haste: r.haste || 1, spiritMult: r.spiritMult || 1, manaMult: r.manaMult || 1, petDmg: r.petDmg || 0, use: r.use || null };
}
