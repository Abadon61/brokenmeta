// Talent trees (data/talents.json, same data and ordering as the site's calculator) <-> simulator build.
// Only talents with a simulated effect appear in NAME_TO_KEY; everything else is ignored by the engine.

export const NAME_TO_KEY = {
  warrior: {
    // Fury
    'Cruelty': 'cruelty', 'Unbridled Wrath': 'unbridledWrath', 'Boundless Rage': 'boundlessRage', 'Dual Wield Specialization': 'dualWieldSpec',
    'Raging Blows': 'ragingBlows', 'Enrage': 'enrage', 'Improved Execute': 'improvedExecute', 'Precision': 'precision', 'Death Wish': 'deathWish',
    'Improved Berserker Rage': 'improvedBerserkerRage', 'Flurry': 'flurry', 'Bloodthirst': 'bloodthirst',
    // Arms
    'Improved Heroic Strike': 'improvedHeroicStrike', 'Improved Rend': 'improvedRend', 'Bloodthrill': 'bloodthrill', 'Improved Overpower': 'improvedOverpower',
    'Anger Management': 'angerManagement', 'Deep Wounds': 'deepWounds',
    'Two-Handed Weapon Specialization': 'twoHandSpec', 'Impale': 'impale', 'Weaponmaster': 'weaponmaster', 'Improved Slam': 'improvedSlam',
    'Mortal Strike': 'mortalStrike',
    'Shield Specialization': 'shieldSpec', 'Anticipation': 'anticipation', 'Toughness': 'toughness', 'Improved Revenge': 'improvedRevenge', 'Defiance': 'defiance', 'Bastion': 'bastion',
    'Focused Rage': 'focusedRage', 'Master of Defense': 'masterOfDefense', 'Improved Sunder Armor': 'improvedSunder', 'Shield Slam': 'shieldSlam', 'Improved Bloodrage': 'improvedBloodrage', 'Deflection': 'deflection',
  },
  rogue: {
    'Malice': 'malice', 'Lethality': 'lethality', 'Precision': 'precision', 'Dual Wield Specialization': 'dualWieldSpec',
    'Improved Sinister Strike': 'improvedSinisterStrike', 'Improved Eviscerate': 'improvedEviscerate', 'Flawless Execution': 'flawlessExecution',
    'Blade Flurry': 'bladeFlurry', 'Hack and Slash': 'hackAndSlash', 'Weapon Expertise': 'weaponExpertise', 'Aggression': 'aggression',
    'Adrenaline Rush': 'adrenalineRush', 'Ruthlessness': 'ruthlessness', 'Relentless Strikes': 'relentlessStrikes',
    'Improved Slice and Dice': 'improvedSliceAndDice', 'Seal Fate': 'sealFate', 'Vigor': 'vigor', 'Cold Blood': 'coldBlood', 'Mutilate': 'mutilate',
    'Hemorrhage': 'hemorrhage', 'Opportunity': 'opportunity', 'Quietus': 'quietus', 'Serrated Blades': 'serratedBlades', 'Puncturing Wounds': 'puncturingWounds',
    'Improved Poisons': 'improvedPoisons', 'Vile Poisons': 'vilePoisons',
  },
  paladin: {
    'Conviction': 'conviction', 'Improved Judgement': 'improvedJudgement', 'Sanctified Judgement': 'sanctifiedJudgement', 'Two-Handed Weapon Specialization': 'twoHandSpec', 'Vindication': 'vindication',
    'Anticipation': 'anticipation', 'Toughness': 'toughness', 'Precision': 'precision', 'One-Handed Weapon Specialization': 'oneHandWeaponSpecialization', 'Improved Righteous Fury': 'improvedRighteousFury',
    'Reckoning': 'reckoning', 'Redoubt': 'redoubt', 'Iron Creed': 'ironCreed', 'Sacred Duty': 'sacredDuty', 'Holy Shield': 'holyShield', 'Swift Judgement': 'swiftJudgement',
    'Vengeance': 'vengeance', 'Seal of Command': 'sealOfCommand', 'Sacred Arbiter': 'sacredArbiter', 'Champion of the Light': 'championOfLight', 'Divine Strength': 'divineStrength',
    'Divine Intellect': 'divineIntellect', 'Benediction': 'benediction', 'Holy Power': 'holyPower', 'Improved Seals': 'improvedSeals', 'Instrument of Law': 'instrumentOfLaw', 'Twist of Light': 'twistOfLight',
  },
  priest: {
    'Shadow Focus': 'shadowFocus', 'Improved Shadow Word: Pain': 'improvedSwp', 'Improved Mind Blast': 'improvedMindBlast', 'Mind Flay': 'mindFlay', 'Improved Mind Flay': 'improvedMindFlay',
    'Shadow Weaving': 'shadowWeaving', 'Darkness': 'darkness', 'Shadowform': 'shadowform', 'Devouring Contagion': 'devouringContagion', 'Twin Disciplines': 'twinDisciplines',
    'Mental Agility': 'mentalAgility', 'Mental Strength': 'mentalStrength', 'Meditation': 'meditation', 'Power Infusion': 'powerInfusion', 'Inner Focus': 'innerFocus',
  },
  shaman: {
    'Convection': 'convection', 'Concussion': 'concussion', 'Reverberation': 'reverberation', 'Call of Flame': 'callOfFlame', 'Elemental Focus': 'elementalFocus',
    'Elemental Alacrity': 'elementalAlacrity', 'Call of Thunder': 'callOfThunder', 'Lightning Overload': 'lightningOverload', 'Elemental Fury': 'elementalFury', 'Lava Burst': 'lavaBurst',
    'Thundering Strikes': 'thunderingStrikes', 'Ancestral Knowledge': 'ancestralKnowledge', 'Flurry': 'flurry', 'Stormstrike': 'stormstrike', 'Maelstrom Weapon': 'maelstromWeapon',
    'Rage of the Farseer': 'rageOfTheFarseer', 'Improved Fire Nova': 'improvedFireNova', 'Shamanistic Focus': 'shamanisticFocus', 'Improved Stormstrike': 'improvedStormstrike', 'Mental Dexterity': 'mentalDexterity', 'Mental Quickness': 'mentalQuickness', 'Elemental Weapons': 'elementalWeapons',
  },
  druid: {
    'Improved Wrath': 'improvedWrath', 'Genesis': 'genesis', 'Moonglow': 'moonglow', 'Improved Moonfire': 'improvedMoonfire', "Nature's Majesty": 'naturesMajesty', "Nature's Reach": 'naturesReach',
    "Nature's Splendor": 'naturesSplendor', 'Insect Swarm': 'insectSwarm', 'Vengeance': 'vengeance', 'Improved Starfire': 'improvedStarfire', "Nature's Grace": 'naturesGrace', 'Eclipse': 'eclipse',
    'Moonfury': 'moonfury', 'Moonkin Form': 'moonkinForm', 'Naturalist': 'naturalist', 'Ferocity': 'ferocity', 'Shredding Attacks': 'shreddingAttacks', 'Savage Fury': 'savageFury',
    'Sharpened Claws': 'sharpenedClaws', 'Predatory Strikes': 'predatoryStrikes', 'Predatory Instincts': 'predatoryInstincts', 'Rend and Tear': 'rendAndTear', 'Heart of the Wild': 'heartOfTheWild',
    'Leader of the Pack': 'leaderOfThePack', 'Shifting Power': 'shiftingPower', 'Improved Shifting Power': 'improvedShiftingPower', 'Berserk': 'berserk', 'Natural Reaction': 'naturalReaction', 'Feral Swiftness': 'feralSwiftness', 'Thick Hide': 'thickHide', 'Feral Instinct': 'feralInstinct', 'Blood Frenzy': 'bloodFrenzy',
  },
  hunter: {
    'Lethal Attacks': 'lethalAttacks', 'Efficiency': 'efficiency', 'Careful Aim': 'carefulAim', 'Rapid Killing': 'rapidKilling', 'Improved Arcane Shot': 'improvedArcane', 'Lone Wolf': 'loneWolf',
    'Mortal Shots': 'mortalShots', 'Barrage': 'barrage', 'Ranged Weapon Specialization': 'rangedSpec', 'Improved Stings': 'improvedStings', 'Sniper Shot': 'sniperShot',
    'Surefooted': 'surefooted', 'Lightning Reflexes': 'lightningReflexes', 'Unleashed Fury': 'unleashedFury', 'Ferocity': 'ferocity', 'Frenzy': 'frenzy', 'Bestial Wrath': 'bestialWrath',
    'Strider Kick': 'striderKick', 'Savage Strikes': 'savageStrikes', "Predator's Edge": 'predatorsEdge', 'Expose Prey': 'exposePrey', 'Lacerating Strikes': 'lacerationStrikes', 'Resourcefulness': 'resourcefulness',
    'Focused Fire': 'focusedFire', 'Deadly Aspects': 'deadlyAspects', 'Summon Hawk': 'summonHawk', 'Bestial Discipline': 'bestialDiscipline',
  },
  warlock: {
    'Suppression': 'suppression', 'Improved Corruption': 'improvedCorruption', 'Malediction': 'malediction', 'Improved Life Tap': 'improvedLifeTap', 'Pandemic': 'pandemic',
    'Malevolence': 'malevolence', 'Nightfall': 'nightfall', 'Shadow Mastery': 'shadowMastery', 'Improved Bane of Agony': 'improvedBaneOfAgony', 'Siphon Life': 'siphonLife', 'Wrack': 'wrack',
    'Soul Siphon': 'soulSiphon', 'Improved Shadow Bolt': 'improvedShadowBolt', 'Bane': 'bane', 'Cataclysm': 'cataclysm', 'Aftermath': 'aftermath', 'Ruin': 'ruin', 'Shadowburn': 'shadowburn',
    'Agonizing Flames': 'agonizingFlames', 'Conflagrate': 'conflagrate', 'Fire and Brimstone': 'fireAndBrimstone', 'Shadow and Flame': 'shadowAndFlame', 'Incinerate': 'incinerate',
    'Decimation': 'decimation', 'Demonic Knowledge': 'demonicKnowledge', 'Master Demonologist': 'masterDemonologist', 'Unholy Power': 'unholyPower', 'Improved Imp': 'improvedImp',
    'Fel Vitality': 'felVitality', 'Demonic Sacrifice': 'demonicSacrifice',
  },
  mage: {
    'Arcane Focus': 'arcaneFocus', 'Arcane Concentration': 'arcaneConcentration', 'Arcane Impact': 'arcaneImpact', 'Arcane Meditation': 'arcaneMeditation',
    'Arcane Mind': 'arcaneMind', 'Arcane Instability': 'arcaneInstability', 'Arcane Power': 'arcanePower', 'Presence of Mind': 'presenceOfMind', 'Missile Barrage': 'missileBarrage',
    'Incineration': 'incineration', 'Improved Fireball': 'improvedFireball', 'Ignite': 'ignite', 'Improved Scorch': 'improvedScorch', 'Heating Up': 'heatingUp',
    'Master of Elements': 'masterOfElements', 'Critical Mass': 'criticalMass', 'Fire Power': 'firePower', 'Combustion': 'combustion', 'Pyroblast': 'pyroblast', 'Wake of Fire': 'wakeOfFire',
    'Improved Frostbolt': 'improvedFrostbolt', 'Elemental Precision': 'elementalPrecision', 'Ice Shards': 'iceShards', 'Piercing Ice': 'piercingIce', 'Frost Channeling': 'frostChanneling',
    'Ice Lance': 'iceLance', 'Shatter': 'shatter', 'Fingers of Frost': 'fingersOfFrost', "Winter's Chill": 'wintersChill',
  },
};
// Keys that default to "on" in a hand-made build only through the presets below; a talent absent from the ranks means rank 0.
export const ALL_KEYS = (cls) => Object.values(NAME_TO_KEY[cls] || {});

const order = (spec) => spec.talents.slice().sort((a, b) => a.row - b.row || a.col - b.col);

// Same rules as the calculator (js/wow-talents.js): shared points, row gates, prerequisites.
export function validateRanks(data, ranks) {
  const byId = {}, bySpec = [];
  data.specs.forEach((s, si) => s.talents.forEach((t) => { byId[t.id] = t; t._spec = si; }));
  const rank = (t) => ranks[t.id] || 0;
  const spentIn = (si, belowRow) => data.specs[si].talents.reduce((n, t) => n + (t.row < belowRow ? rank(t) : 0), 0);
  const gatesOf = (t) => (t.gates && t.gates.length ? t.gates : (t.row > 1 ? [{ through_row: t.row - 1, points: (t.row - 1) * data.rules.points_per_row }] : []));
  const asList = (v) => (!v ? [] : Array.isArray(v) ? v : [v]);
  let total = 0, ok = true; const errors = [];
  for (const id in ranks) {
    const t = byId[id];
    if (!t) { ok = false; errors.push('unknown talent ' + id); continue; }
    if (ranks[id] > t.max_rank) { ok = false; errors.push(t.name.en + ': above max rank'); }
    total += ranks[id];
  }
  data.specs.forEach((s, si) => { bySpec[si] = spentIn(si, 99); });
  for (const id in ranks) {
    const t = byId[id]; if (!t || !ranks[id]) continue;
    if (!gatesOf(t).every((g) => spentIn(t._spec, g.through_row + 1) >= g.points)) { ok = false; errors.push(t.name.en + ': row locked'); }
    const all = asList(t.requires), any = asList(t.requires_any);
    const met = (q) => (ranks[q.id] || 0) >= q.rank;
    if (!all.every(met) || (any.length && !any.some(met))) { ok = false; errors.push(t.name.en + ': prerequisite missing'); }
  }
  if (total > data.rules.total_points) { ok = false; errors.push('more than ' + data.rules.total_points + ' points'); }
  return { ok, total, bySpec, errors };
}

// Calculator share link "#b=<rev>.<tree1 ranks>.<tree2 ranks>.<tree3 ranks>" (one digit per talent, row-major order).
export function parseShareHash(data, hash) {
  const m = /^#?b=([0-9a-f]{6})((?:\.[0-9]*)+)$/.exec((hash || '').trim().replace(/^.*#/, '#'));
  if (!m) return { error: 'format' };
  const parts = m[2].slice(1).split('.');
  if (parts.length !== data.specs.length) return { error: 'format' };
  const ranks = {};
  for (let i = 0; i < data.specs.length; i++) {
    const ord = order(data.specs[i]);
    if (parts[i].length !== ord.length) return { error: 'format' };
    for (let j = 0; j < ord.length; j++) { const r = +parts[i][j]; if (r > ord[j].max_rank) return { error: 'format' }; if (r) ranks[ord[j].id] = r; }
  }
  return { ranks, revMatches: m[1] === data.rev };
}

export function ranksToBuild(cls, data, ranks) {
  const map = NAME_TO_KEY[cls] || {}, build = {};
  for (const k of Object.values(map)) build[k] = 0;
  data.specs.forEach((s) => s.talents.forEach((t) => { const k = map[t.name.en]; if (k) build[k] = ranks[t.id] || 0; }));
  return build;
}

export function ranksFromNames(data, byName) {
  const ranks = {};
  data.specs.forEach((s) => s.talents.forEach((t) => { if (byName[t.name.en]) ranks[t.id] = byName[t.name.en]; }));
  return ranks;
}

// Typical raiding builds (51 points), by talent name. Checked against the tree rules in the tests.
export const PRESETS = {
  rogue_combat: {
    'Improved Eviscerate': 3, 'Improved Sinister Strike': 2, 'Lightning Reflexes': 4, 'Precision': 3, 'Puncturing Wounds': 3, 'Flawless Execution': 1,
    'Dual Wield Specialization': 5, 'Blade Flurry': 1, 'Hack and Slash': 5, 'Weapon Expertise': 2, 'Aggression': 3, 'Adrenaline Rush': 1,
    'Malice': 5, 'Ruthlessness': 3, 'Improved Slice and Dice': 3, 'Murder': 2, 'Lethality': 5,
  },
  rogue_assassination: {
    'Malice': 5, 'Ruthlessness': 3, 'Improved Slice and Dice': 3, 'Murder': 2, 'Relentless Strikes': 1, 'Lethality': 5, 'Vile Poisons': 5, 'Cold Blood': 1,
    'Mutilate': 1, 'Vigor': 2, 'Seal Fate': 3,
    'Improved Eviscerate': 3, 'Improved Sinister Strike': 2, 'Lightning Reflexes': 4, 'Precision': 3, 'Puncturing Wounds': 3, 'Dual Wield Specialization': 5,
  },
  rogue_subtlety: {
    'Camouflage': 5, 'Opportunity': 2, 'Setup': 3, 'Improved Ambush': 3, 'Ghostly Strike': 1, 'Initiative': 3, 'Improved Distract': 2, 'Serrated Blades': 3,
    'Premeditation': 1, 'Hemorrhage': 1, 'Dirty Deeds': 2, 'Quietus': 5,
    'Improved Eviscerate': 3, 'Improved Sinister Strike': 2, 'Lightning Reflexes': 4, 'Precision': 3, 'Puncturing Wounds': 3, 'Dual Wield Specialization': 5,
  },
  mage_fire: {
    'Wake of Fire': 2, 'Incineration': 3, 'Improved Fireball': 5, 'Ignite': 5, 'Pyroblast': 1, 'Improved Scorch': 3, 'Heating Up': 1, 'Master of Elements': 3,
    'Critical Mass': 3, 'Fire Power': 5, 'Combustion': 1,
    'Elemental Precision': 5, 'Ice Shards': 5, 'Frost Channeling': 3, 'Piercing Ice': 3, 'Improved Frostbolt': 3,
  },
  mage_frost: {
    'Improved Frostbolt': 5, 'Elemental Precision': 5, 'Ice Shards': 5, 'Piercing Ice': 3, 'Frost Channeling': 3, 'Ice Lance': 1, 'Shatter': 3, 'Fingers of Frost': 2, "Winter's Chill": 5,
    'Wand Specialization': 1, 'Arcane Focus': 5, 'Arcane Subtlety': 2, 'Arcane Concentration': 5, 'Arcane Impact': 3, 'Arcane Meditation': 3,
  },
  mage_arcane: {
    'Arcane Focus': 5, 'Improved Channeling': 1, 'Arcane Concentration': 5, 'Arcane Subtlety': 2, 'Arcane Impact': 3, 'Arcane Blast': 1, 'Arcane Meditation': 3, 'Missile Barrage': 1,
    'Presence of Mind': 1, 'Arcane Mind': 5, 'Arcane Instability': 3, 'Arcane Power': 1,
    'Wake of Fire': 2, 'Incineration': 3, 'Improved Fireball': 5, 'Ignite': 5, 'Master of Elements': 3, 'Improved Scorch': 2,
  },
  warlock_affliction: {
    'Suppression': 5, 'Improved Corruption': 5, 'Malediction': 5, 'Pandemic': 3, 'Malevolence': 5, 'Nightfall': 2, 'Siphon Life': 1, 'Shadow Mastery': 5, 'Wrack': 1,
    'Improved Shadow Bolt': 5, 'Bane': 5, 'Cataclysm': 3, 'Ruin': 5, 'Shadowburn': 1,
  },
  warlock_destruction: {
    'Improved Shadow Bolt': 5, 'Bane': 5, 'Cataclysm': 3, 'Aftermath': 5, 'Ruin': 5, 'Shadowburn': 1, 'Agonizing Flames': 3, 'Conflagrate': 1, 'Fire and Brimstone': 3,
    'Shadow and Flame': 5, 'Bane of Havoc': 1, 'Incinerate': 1, 'Suppression': 5, 'Improved Corruption': 5, 'Malediction': 3,
  },
  warlock_demonology: {
    'Demonic Embrace': 5, 'Improved Imp': 3, 'Improved Health Funnel': 2, 'Unholy Power': 5, 'Fel Vitality': 3, 'Demonic Aegis': 2, 'Master Summoner': 2, 'Demonic Knowledge': 3, 'Master Demonologist': 3,
    'Improved Shadow Bolt': 5, 'Bane': 5, 'Cataclysm': 3, 'Aftermath': 5, 'Shadowburn': 1, 'Conflagrate': 1, 'Agonizing Flames': 3,
  },
  hunter_marksmanship: {
    'Lethal Attacks': 5, 'Improved Stings': 3, 'Efficiency': 5, 'Careful Aim': 5, 'Rapid Killing': 2, 'Improved Arcane Shot': 5, 'Lone Wolf': 1, 'Trueshot Aura': 1, 'Mortal Shots': 5,
    'Barrage': 3, 'Ranged Weapon Specialization': 5, 'Sniper Shot': 1, 'Deadly Aspects': 5, 'Endurance Training': 5,
  },
  hunter_beastmastery: {
    'Deadly Aspects': 5, 'Endurance Training': 5, 'Focused Fire': 2, 'Bestial Swiftness': 1, 'Unleashed Fury': 5, 'Ferocity': 5, 'Summon Hawk': 1, 'Intimidation': 1,
    'Bestial Discipline': 2, 'Frenzy': 5, 'Bestial Wrath': 1, 'Lethal Attacks': 5, 'Efficiency': 5, 'Careful Aim': 5, 'Improved Stings': 3,
  },
  hunter_melee: {
    'Improved Tracking': 5, 'Savage Strikes': 2, 'Survivalist': 5, 'Surefooted': 3, "Predator's Edge": 5, 'Resourcefulness': 2, 'Expose Prey': 2, 'Strider Kick': 1, 'Lightning Reflexes': 5, 'Lacerating Strikes': 1,
    'Lethal Attacks': 5, 'Efficiency': 5, 'Careful Aim': 5, 'Hawk Eye': 3, 'Improved Concussive Shot': 2,
  },
  hunter_survival: {
    'Improved Tracking': 5, 'Savage Strikes': 2, 'Survivalist': 5, 'Surefooted': 3, 'Clever Traps': 2, "Predator's Edge": 5, 'Resourcefulness': 2, 'Expose Prey': 2,
    'Lightning Reflexes': 5, 'Lacerating Strikes': 1, 'Lethal Attacks': 5, 'Efficiency': 5, 'Careful Aim': 5, 'Improved Stings': 3, 'Hawk Eye': 1,
  },
  priest_shadow: {
    'Shadow Focus': 5, 'Spirit Tap': 5, 'Improved Shadow Word: Pain': 2, 'Improved Mind Blast': 5, 'Mind Flay': 1, 'Improved Mind Flay': 2, 'Vampiric Embrace': 1, 'Shadow Weaving': 3,
    'Devouring Contagion': 2, 'Darkness': 5, 'Shadowform': 1,
    'Twin Disciplines': 5, 'Power in Light': 5, 'Mental Agility': 3, 'Inner Focus': 1, 'Meditation': 3, 'Mental Strength': 2,
  },
  shaman_elemental: {
    'Convection': 5, 'Concussion': 5, 'Reverberation': 5, 'Call of Flame': 3, 'Elemental Focus': 1, 'Elemental Alacrity': 3, 'Call of Thunder': 1, 'Lightning Overload': 3,
    'Elemental Fury': 5, 'Lava Burst': 1, 'Thundering Strikes': 5, 'Ancestral Knowledge': 5, 'Mental Dexterity': 3, 'Guardian Totems': 2, 'Improved Ghost Wolf': 2, 'Improved Lightning Shield': 2,
  },
  druid_balance: {
    'Improved Wrath': 5, 'Genesis': 5, 'Moonglow': 3, 'Improved Moonfire': 2, "Nature's Majesty": 2, "Nature's Reach": 2, "Nature's Splendor": 1, 'Insect Swarm': 1, 'Vengeance': 5,
    'Improved Starfire': 5, "Nature's Grace": 1, 'Eclipse': 3, 'Moonfury': 5, 'Moonkin Form': 1, 'Furor': 5, 'Naturalist': 5,
  },
  paladin_retribution: {
    'Benediction': 5, 'Improved Judgement': 2, 'Conviction': 5, 'Vindication': 3, 'Sanctified Judgement': 3, 'Seal of Command': 1, 'Sacred Arbiter': 1, 'Two-Handed Weapon Specialization': 3,
    'Vengeance': 3, 'Champion of the Light': 3, 'Instrument of Law': 2, 'Twist of Light': 1,
    'Divine Strength': 5, 'Divine Intellect': 5, 'Improved Seals': 3, 'Healing Light': 3, 'Reverence': 3,
  },
  shaman_enhancement: {
    'Thundering Strikes': 5, 'Ancestral Knowledge': 5, 'Mental Dexterity': 3, 'Elemental Weapons': 3, 'Flurry': 5, 'Stormstrike': 1, 'Mental Quickness': 2, 'Improved Stormstrike': 2,
    'Maelstrom Weapon': 5, 'Rage of the Farseer': 1,
    'Convection': 5, 'Concussion': 5, 'Call of Flame': 3, 'Shamanistic Focus': 1, 'Reverberation': 1, 'Elemental Focus': 1, 'Elemental Alacrity': 3,
  },
  druid_feral: {
    'Ferocity': 5, 'Heart of the Wild': 5, 'Thick Hide': 3, 'Shredding Attacks': 3, 'Savage Fury': 2, 'Sharpened Claws': 2, 'Predatory Strikes': 3, 'Blood Frenzy': 2, 'Shifting Power': 1,
    'Leader of the Pack': 1, 'Predatory Instincts': 2, 'Improved Shifting Power': 2, 'Rend and Tear': 5, 'Berserk': 1,
    'Improved Wrath': 5, 'Genesis': 5, "Nature's Majesty": 2, "Nature's Reach": 2,
  },
  warrior_protection: {
    'Shield Specialization': 5, 'Anticipation': 5, 'Toughness': 5, 'Improved Bloodrage': 2, 'Master of Defense': 2, 'Improved Revenge': 3, 'Defiance': 3, 'Last Stand': 1, 'Improved Sunder Armor': 3,
    'Vanguard': 1, 'Bastion': 5, 'Focused Rage': 3, 'Shield Slam': 1,
    'Deflection': 5, 'Improved Heroic Strike': 3, 'Improved Charge': 2, 'Improved Tactical Mastery': 1, 'Concussion Blow': 1,
  },
  paladin_protection: {
    'Toughness': 5, 'Redoubt': 5, 'Precision': 3, 'Anticipation': 5, 'Improved Righteous Fury': 3, 'Shield Specialization': 3, 'Sacred Duty': 2, 'Improved Seal of Fury': 1, 'Swift Judgement': 1,
    'One-Handed Weapon Specialization': 3, 'Reckoning': 5, "Templar's Bulwark": 1, 'Iron Creed': 5, 'Holy Shield': 1,
    'Divine Strength': 5, 'Divine Intellect': 3,
  },
  druid_bear: {
    'Ferocity': 5, 'Heart of the Wild': 5, 'Feral Swiftness': 2, 'Thick Hide': 3, 'Feral Instinct': 3, 'Shredding Attacks': 3, 'Savage Fury': 2, 'Sharpened Claws': 2,
    'Predatory Strikes': 3, 'Blood Frenzy': 2, 'Leader of the Pack': 1, 'Predatory Instincts': 2, 'Natural Reaction': 5, 'Berserk': 1,
    'Furor': 5, 'Naturalist': 5, 'Subtlety': 2,
  },
  warrior_fury: {
    'Cruelty': 5, 'Unbridled Wrath': 5, 'Improved Cleave': 3, 'Boundless Rage': 3, 'Dual Wield Specialization': 5, 'Raging Blows': 1, 'Enrage': 5,
    'Improved Execute': 2, 'Precision': 3, 'Death Wish': 1, 'Improved Berserker Rage': 2, 'Flurry': 5, 'Bloodthirst': 1,
    'Improved Heroic Strike': 3, 'Improved Rend': 3, 'Improved Tactical Mastery': 4,
  },
  warrior_arms: {
    'Improved Heroic Strike': 3, 'Improved Rend': 3, 'Improved Overpower': 2, 'Improved Tactical Mastery': 5, 'Anger Management': 1, 'Deep Wounds': 3,
    'Two-Handed Weapon Specialization': 3, 'Impale': 2, 'Sweeping Strikes': 1, 'Weaponmaster': 5, 'Improved Slam': 2, 'Mortal Strike': 1,
    'Cruelty': 5, 'Unbridled Wrath': 5, 'Bloodthrill': 5, 'Boundless Rage': 3, 'Improved Cleave': 2,
  },
};
