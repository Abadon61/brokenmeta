// Raid buffs, consumables and boss debuffs. Values are Classic 1.12 numbers (ASSUMED: WoW: Forever
// is Classic-derived and its level-60 tooltips are not available yet); the public page flags this.
// Each entry adds to the character through these keys (all optional):
//   str/agi/sta/int/spi  flat primary stats (before multipliers)
//   statMult             multiplies every primary stat (Blessing of Kings: 1.10)
//   ap                   flat attack power         apMult   multiplies final AP
//   crit                 flat crit chance (0.03 = 3%)   hit  flat hit chance
//   haste                haste multiplier (1.0x)        dmgMult  damage multiplier
export const BUFFS = {
  // ---- ally buffs of the 20-player raid: every class brings the ones it can cast (values from the Forever client tables, level 60 ranks) ----
  // Warrior
  battle_shout: { name: 'Battle Shout (Warrior)', ap: 139 },
  // Paladin
  blessing_of_might: { name: 'Greater Blessing of Might (Paladin)', ap: 133 },
  blessing_of_kings: { name: 'Greater Blessing of Kings (Paladin)', statMult: 1.10 },
  blessing_of_wisdom: { name: 'Greater Blessing of Wisdom (Paladin)', mp5: 40 },
  // Druid
  mark_of_the_wild: { name: 'Gift of the Wild (Druid)', str: 16, agi: 16, sta: 16, int: 16, spi: 16 },
  leader_of_the_pack: { name: 'Leader of the Pack (Feral Druid)', crit: 0.03, meleeOnly: true },
  moonkin_aura: { name: 'Moonkin Aura (Balance Druid)', spCrit: 0.03 },
  // Shaman totems
  strength_of_earth: { name: 'Strength of Earth Totem (Shaman)', str: 53 },
  grace_of_air: { name: 'Grace of Air Totem (Shaman)', agi: 89 },
  mana_spring_totem: { name: 'Mana Spring Totem (Shaman)', mp5: 25 },       // 10 mana per 2 s
  // Priest
  divine_spirit: { name: 'Prayer of Spirit (Priest)', spi: 40 },
  power_word_fortitude: { name: 'Prayer of Fortitude (Priest)', sta: 70 },
  // Mage
  arcane_intellect: { name: 'Arcane Brilliance (Mage)', int: 31 },
  // Hunter
  hunters_mark: { name: "Hunter's Mark (Hunter)", ap: 110 },                // ranged attack power on the target (ranged Hunters only)
  trueshot_aura: { name: 'Trueshot Aura (Hunter)', ap: 50 },
};

// Consumables: the stat scrolls, flasks, elixirs, juju and foods that exist in the Forever client (level-60 ranks). Weapon oils are Classic numbers (ASSUMED).
export const CONSUMABLES = {
  scroll_strength: { name: 'Scroll of Strength', str: 17 },
  scroll_agility: { name: 'Scroll of Agility', agi: 17 },
  scroll_intellect: { name: 'Scroll of Intellect', int: 16 },
  scroll_spirit: { name: 'Scroll of Spirit', spi: 15 },
  scroll_stamina: { name: 'Scroll of Stamina', sta: 16 },
  flask_ancient_knowledge: { name: 'Flask of Ancient Knowledge', sp: 180 },
  flask_madness: { name: 'Flask of Madness', ap: 50 },
  elixir_mongoose: { name: 'Elixir of the Mongoose', agi: 25, crit: 0.02 },
  elixir_grizzly: { name: 'Elixir of the Grizzly', str: 25, crit: 0.02 },
  elixir_honey_badger: { name: 'Elixir of the Honey Badger', agi: 30, crit: 0.02 },
  elixir_mage_lord: { name: 'Elixir of the Mage-Lord', sp: 40 },
  elixir_owl: { name: 'Elixir of the Owl', int: 25, crit: 0.02 },
  greater_arcane_elixir: { name: 'Greater Arcane Elixir', sp: 35 },
  mageblood_potion: { name: 'Mageblood Potion', mp5: 12 },
  juju_power: { name: 'Juju Power', str: 30 },
  juju_might: { name: 'Juju Might', ap: 40 },
  juju_guile: { name: 'Juju Guile', int: 30 },
  spirit_of_zanza: { name: 'Spirit of Zanza', spi: 50, sta: 50 },
  food_spell_power: { name: 'Well Fed (spell power food)', sp: 25, sta: 10 },
  food_strength: { name: 'Well Fed (strength food)', str: 25, sta: 10 },
  food_agility: { name: 'Well Fed (agility food)', agi: 25, sta: 10 },
  nightfin_soup: { name: 'Nightfin Soup', mp5: 8 },
  brilliant_wizard_oil: { name: 'Brilliant Wizard Oil', sp: 36, spCrit: 0.01, assumed: true },
  brilliant_mana_oil: { name: 'Brilliant Mana Oil', sp: 25, mp5: 12, assumed: true },
  dense_stone: { name: 'Dense Sharpening Stone', weaponDmg: 8, critMelee: 0, assumed: true },
};

// Boss debuffs: armor reductions (additive on the boss's armor, floor 0) and the ones that matter for damage.
export const DEBUFFS = {
  sunder_armor_5: { name: 'Sunder Armor x5', armor: -2250 },
  faerie_fire: { name: 'Faerie Fire', armor: -505 },
  curse_of_recklessness: { name: 'Curse of Recklessness', armor: -505 },
  curse_of_elements: { name: 'Curse of the Elements', spellTaken: 1.10 },
  expose_armor: { name: 'Expose Armor (5 pts)', armor: -1700, assumed: true },
};

// What a 20-player raid gives one player: every ally buff its classes can cast + the consumables of that role (scrolls, flask/elixirs, juju, food).
// Not simulated: Windfury Totem, Power Infusion, Innervate, Judgements (they proc or are cooldowns, not flat stats) and the Demonic Rune's health cost.
const ALLY = ['arcane_intellect', 'blessing_of_kings', 'blessing_of_wisdom', 'blessing_of_might', 'mark_of_the_wild', 'divine_spirit', 'power_word_fortitude', 'mana_spring_totem'];
export const PRESET_CASTER = {
  buffs: [...ALLY, 'moonkin_aura'],
  consumables: ['scroll_intellect', 'scroll_spirit', 'scroll_stamina', 'flask_ancient_knowledge', 'juju_guile', 'spirit_of_zanza', 'mageblood_potion', 'brilliant_wizard_oil', 'food_spell_power'],
  debuffs: ['curse_of_elements'],
};

export const PRESET_HUNTER = {
  buffs: [...ALLY, 'battle_shout', 'grace_of_air', 'strength_of_earth', 'trueshot_aura', 'hunters_mark', 'leader_of_the_pack'],
  consumables: ['scroll_agility', 'scroll_strength', 'scroll_stamina', 'elixir_mongoose', 'elixir_honey_badger', 'juju_might', 'brilliant_mana_oil', 'nightfin_soup', 'food_agility'],
  debuffs: ['sunder_armor_5', 'faerie_fire', 'curse_of_recklessness'],
};

export const PRESET_RAID = {
  buffs: [...ALLY, 'battle_shout', 'grace_of_air', 'strength_of_earth', 'leader_of_the_pack'],
  consumables: ['scroll_strength', 'scroll_agility', 'scroll_stamina', 'elixir_mongoose', 'elixir_grizzly', 'juju_power', 'juju_might', 'nightfin_soup', 'food_strength'],
  debuffs: ['sunder_armor_5', 'faerie_fire', 'curse_of_recklessness'],
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
