// Raid buffs, consumables and boss debuffs. Values are Classic 1.12 numbers (ASSUMED: WoW: Forever
// is Classic-derived and its level-60 tooltips are not available yet); the public page flags this.
// Each entry adds to the character through these keys (all optional):
//   str/agi/sta/int/spi  flat primary stats (before multipliers)
//   statMult             multiplies every primary stat (Blessing of Kings: 1.10)
//   ap                   flat attack power         apMult   multiplies final AP
//   crit                 flat crit chance (0.03 = 3%)   hit  flat hit chance
//   haste                haste multiplier (1.0x)        dmgMult  damage multiplier
export const BUFFS = {
  battle_shout: { name: 'Battle Shout (rank 7)', ap: 232, assumed: true },
  blessing_of_might: { name: 'Blessing of Might', ap: 185, assumed: true },
  blessing_of_kings: { name: 'Blessing of Kings', statMult: 1.10, assumed: true },
  mark_of_the_wild: { name: 'Mark of the Wild', str: 12, agi: 12, sta: 12, int: 12, spi: 12, assumed: true },
  strength_of_earth: { name: 'Strength of Earth Totem', str: 53 },          // Forever client value (rank at level 60)
  grace_of_air: { name: 'Grace of Air Totem', agi: 89 },                    // Forever client value (rank at level 60)
  leader_of_the_pack: { name: 'Leader of the Pack', crit: 0.03, meleeOnly: true, assumed: true },
  blessing_of_wisdom: { name: 'Greater Blessing of Wisdom', mp5: 40 },        // 40 mana per 5 s: Forever client value
  mana_spring_totem: { name: 'Mana Spring Totem', mp5: 25 },                                    // Forever client: 10 mana per 2 s at the top rank (level 56)
  arcane_intellect: { name: 'Arcane Brilliance (Arcane Intellect)', int: 31, assumed: true },
  moonkin_aura: { name: 'Moonkin Aura', spCrit: 0.03, assumed: true },
  trueshot_aura: { name: 'Trueshot Aura', ap: 100, assumed: true },
  dragonslayer: { name: 'Rallying Cry of the Dragonslayer', crit: 0.05, ap: 140, assumed: true },
  songflower: { name: 'Songflower Serenade', crit: 0.05, str: 15, agi: 15, assumed: true },
  dire_maul_tribute: { name: 'Fengus\' Ferocity', ap: 200, assumed: true },
};

export const CONSUMABLES = {
  elixir_mongoose: { name: 'Elixir of the Mongoose', agi: 25, crit: 0.02, meleeOnly: true, assumed: true },
  greater_arcane_elixir: { name: 'Greater Arcane Elixir', sp: 35, assumed: true },
  flask_supreme_power: { name: 'Flask of Supreme Power', sp: 150, assumed: true },
  brilliant_wizard_oil: { name: 'Brilliant Wizard Oil', sp: 36, spCrit: 0.01, assumed: true },
  brilliant_mana_oil: { name: 'Brilliant Mana Oil', sp: 25, mp5: 12, assumed: true },
  mageblood_potion: { name: 'Mageblood Potion', mp5: 12, assumed: true },
  juju_power: { name: 'Juju Power', str: 30, assumed: true },
  juju_might: { name: 'Juju Might', ap: 40, assumed: true },
  roids: { name: 'R.O.I.D.S.', str: 25, assumed: true },
  ground_scorpok: { name: 'Ground Scorpok Assay', agi: 25, assumed: true },
  winterfall_firewater: { name: 'Winterfall Firewater', str: 35, assumed: true },
  smoked_dumplings: { name: 'Smoked Desert Dumplings', str: 20, assumed: true },
  dense_stone: { name: 'Dense Sharpening Stone', weaponDmg: 8, critMelee: 0, assumed: true },
};

// Boss debuffs: armor reductions (additive on the boss's armor, floor 0) and the ones that matter for damage.
export const DEBUFFS = {
  sunder_armor_5: { name: 'Sunder Armor x5', armor: -2250, assumed: true },
  faerie_fire: { name: 'Faerie Fire', armor: -505, assumed: true },
  curse_of_recklessness: { name: 'Curse of Recklessness', armor: -640, assumed: true },
  curse_of_elements: { name: 'Curse of the Elements', spellTaken: 1.10, assumed: true },
  expose_armor: { name: 'Expose Armor (5 pts)', armor: -1700, assumed: true },
};

export const PRESET_CASTER = {
  buffs: ['arcane_intellect', 'blessing_of_kings', 'blessing_of_wisdom', 'mana_spring_totem', 'mark_of_the_wild', 'moonkin_aura', 'dragonslayer', 'songflower'],
  consumables: ['flask_supreme_power', 'greater_arcane_elixir', 'brilliant_wizard_oil', 'mageblood_potion'],
  debuffs: ['curse_of_elements'],
};

export const PRESET_HUNTER = {
  buffs: ['battle_shout', 'blessing_of_might', 'blessing_of_kings', 'mark_of_the_wild', 'grace_of_air', 'trueshot_aura', 'dragonslayer', 'songflower'],
  consumables: ['elixir_mongoose', 'ground_scorpok', 'brilliant_mana_oil'],
  debuffs: ['sunder_armor_5', 'faerie_fire'],
};

export const PRESET_RAID = {
  buffs: ['battle_shout', 'blessing_of_might', 'blessing_of_kings', 'mark_of_the_wild', 'strength_of_earth', 'grace_of_air', 'mana_spring_totem', 'blessing_of_wisdom', 'leader_of_the_pack'],
  consumables: ['elixir_mongoose', 'juju_power', 'juju_might', 'roids'],
  debuffs: ['sunder_armor_5', 'faerie_fire'],
};

// Racial weapon-skill bonuses (+5 skill with the listed weapon types, Classic).
export const RACIAL_SKILL = {
  human: ['sword', 'mace', 'two-handed sword', 'two-handed mace'],
  dwarf: ['mace', 'two-handed mace', 'gun'],
  orc: ['axe', 'two-handed axe', 'fist'],
  troll: ['bow', 'thrown'],
  gnome: ['dagger', 'sword'],
  nightelf: [],
  tauren: [],
  undead: [],
};
