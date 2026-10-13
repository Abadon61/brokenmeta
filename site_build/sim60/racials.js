// Racial abilities of WoW: Forever as the simulator applies them (spec.racialModel === 'forever').
// Every number is read from the beta client tables (data/wow_racials.json, build 1.60.1.70170; spell ids in the comments): Forever reworked the
// racials of WoW Classic (weapon specializations now give critical strike chance instead of weapon skill, new racials such as Elune's Light).
// Racial effects that do not change damage on a single target (resistances, movement, escapes, stealth detection, gathering) are not listed.
// NOT simulated: Gnome Eureka! (next 3 damaging abilities +10% damage, 120 s) and the Gnome's +5% maximum energy / rage, Undead Touch of the Grave
// (health drain), Tauren +5% health, bonuses against Beasts (Troll Beast Slaying, Dwarf Big Game Hunter) and Elementals (Skyborne Elemental Insight):
// the fight is against a single humanoid-like boss.
export const FOREVER_RACIALS = {
  human: { weaponCrit: { types: ['sword', 'two-handed sword'], crit: 0.02 }, spiritMult: 1.05 },                                    // 20597 Sword Specialization, 20598 The Human Spirit
  orc: { weaponCrit: { types: ['axe', 'two-handed axe'], crit: 0.01 }, use: { name: 'Blood Fury', cd: 120, duration: 15, apMult: 1.10, spMult: 1.10 } },   // 20574, 20572
  dwarf: { weaponCrit: { types: ['mace', 'two-handed mace'], crit: 0.01 } },                                                          // 1259719 Mace Specialization
  nightelf: { use: { name: "Elune's Light", cd: 180, duration: 15, crit: 0.10 } },                                                    // 1259799
  tauren: { hit: 0.01 },                                                                                                              // 20550 Endurance (+1% chance to hit; the +5% health is not simulated)
  gnome: { manaMult: 1.05 },                                                                                                          // 20591 Expansive Mind (maximum mana)
  troll: { use: { name: 'Berserking', cd: 180, duration: 10, haste: 1.10 } },                                                         // 20554 (spellcasting and attack speed +10% for 10 s)
  skyborne: { haste: 1.01 },                                                                                                          // 1259710 Wind Blessed
  undead: {},
};

/** The part of a race's model that applies to this character: flat crit (needs a matching weapon), hit, haste, spirit, mana and the on-use racial. */
export function racialsFor(race, weaponTypes) {
  const r = FOREVER_RACIALS[race] || {};
  const types = weaponTypes || [];
  const crit = r.weaponCrit && types.some((t) => r.weaponCrit.types.includes(t)) ? r.weaponCrit.crit : 0;
  return { crit, hit: r.hit || 0, haste: r.haste || 1, spiritMult: r.spiritMult || 1, manaMult: r.manaMult || 1, use: r.use || null };
}
