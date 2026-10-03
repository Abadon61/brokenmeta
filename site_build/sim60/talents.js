// Talent trees (data/talents.json, same data and ordering as the site's calculator) <-> simulator build.
// Only talents with a simulated effect appear in NAME_TO_KEY; everything else is ignored by the engine.

export const NAME_TO_KEY = {
  warrior: {
    // Fury
    'Cruelty': 'cruelty', 'Unbridled Wrath': 'unbridledWrath', 'Boundless Rage': 'boundlessRage', 'Dual Wield Specialization': 'dualWieldSpec',
    'Raging Blows': 'ragingBlows', 'Enrage': 'enrage', 'Improved Execute': 'improvedExecute', 'Precision': 'precision', 'Death Wish': 'deathWish',
    'Improved Berserker Rage': 'improvedBerserkerRage', 'Flurry': 'flurry', 'Bloodthirst': 'bloodthirst',
    // Arms
    'Improved Heroic Strike': 'improvedHeroicStrike', 'Improved Rend': 'improvedRend', 'Improved Overpower': 'improvedOverpower',
    'Anger Management': 'angerManagement', 'Deep Wounds': 'deepWounds',
    'Two-Handed Weapon Specialization': 'twoHandSpec', 'Impale': 'impale', 'Weaponmaster': 'weaponmaster', 'Improved Slam': 'improvedSlam',
    'Mortal Strike': 'mortalStrike',
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
  warrior_fury: {
    'Cruelty': 5, 'Unbridled Wrath': 5, 'Improved Cleave': 3, 'Boundless Rage': 3, 'Dual Wield Specialization': 5, 'Raging Blows': 1, 'Enrage': 5,
    'Improved Execute': 2, 'Precision': 3, 'Death Wish': 1, 'Improved Berserker Rage': 2, 'Flurry': 5, 'Bloodthirst': 1,
    'Improved Heroic Strike': 3, 'Improved Rend': 3, 'Improved Tactical Mastery': 4,
  },
  warrior_arms: {
    'Improved Heroic Strike': 3, 'Improved Rend': 3, 'Improved Overpower': 2, 'Improved Tactical Mastery': 5, 'Anger Management': 1, 'Deep Wounds': 3,
    'Two-Handed Weapon Specialization': 3, 'Impale': 2, 'Sweeping Strikes': 1, 'Weaponmaster': 5, 'Improved Slam': 2, 'Mortal Strike': 1,
    'Cruelty': 5, 'Unbridled Wrath': 5, 'Improved Cleave': 3, 'Boundless Rage': 3,
  },
};
