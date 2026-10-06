// node guide_builds.mjs  ->  data/wow_guides/builds60.json
// The level-60 talent build (51 points) of every specialization guide. DPS and tank specs use the simulator's own presets (PRESETS in talents.js);
// the five healing specs have no simulator kit, so their builds are composed here from the talent tooltips (flagged `simulated: false`) and checked
// against the same tree rules.
import { readFileSync, writeFileSync } from 'node:fs';
import { validateRanks, ranksFromNames, PRESETS } from './talents.js';

const all = JSON.parse(readFileSync(new URL('data/talents.json', import.meta.url)));

// guide spec id (data/wow_guides/content.json) -> preset key
const FROM_PRESET = {
  warrior: { fury: 'warrior_fury', arms: 'warrior_arms', protection: 'warrior_protection' },
  rogue: { combat: 'rogue_combat', assassination: 'rogue_assassination', subtlety: 'rogue_subtlety' },
  mage: { fire: 'mage_fire', frost: 'mage_frost', arcane: 'mage_arcane' },
  warlock: { affliction: 'warlock_affliction', destruction: 'warlock_destruction', demonology: 'warlock_demonology' },
  hunter: { marksmanship: 'hunter_marksmanship', 'beast-mastery': 'hunter_beastmastery', survival: 'hunter_survival' },
  priest: { shadow: 'priest_shadow' },
  shaman: { elemental: 'shaman_elemental', enhancement: 'shaman_enhancement' },
  druid: { balance: 'druid_balance', 'feral-combat': 'druid_feral' },
  paladin: { retribution: 'paladin_retribution', protection: 'paladin_protection' },
};

// Healing builds: composed from the tooltips, not simulated. Mana efficiency and throughput first (cast time, mana cost, regeneration while casting, critical heals).
const HEALERS = {
  priest: {
    holy: {
      'Improved Renew': 3, 'Holy Specialization': 5, 'Divine Fury': 5, 'Inspiration': 3, 'Improved Healing': 3, 'Binding Heal': 1, 'Spiritual Guidance': 5, 'Spiritual Healing': 3, 'Litany of Light': 1, 'Spirit of Redemption': 1, 'Prayer of Mending': 1,
      'Twin Disciplines': 5, 'Improved Power Word: Shield': 3, 'Martyrdom': 2, 'Meditation': 3, 'Mental Agility': 3, 'Inner Focus': 1, 'Mental Strength': 3,
    },
    discipline: {
      'Twin Disciplines': 5, 'Improved Power Word: Shield': 3, 'Martyrdom': 2, 'Mental Agility': 3, 'Inner Focus': 1, 'Meditation': 3, 'Mental Strength': 5, 'Soul Warding': 1, 'Penance': 1, 'Renewed Hope': 3, 'Divine Aegis': 3, 'Power Infusion': 1,
      'Improved Renew': 3, 'Holy Specialization': 5, 'Divine Fury': 5, 'Inspiration': 3, 'Improved Healing': 3, 'Binding Heal': 1,
    },
  },
  shaman: {
    restoration: {
      'Improved Healing Wave': 5, 'Totemic Focus': 5, 'Mindfulness': 3, 'Tidal Focus': 5, 'Healing Focus': 3, 'Water Shield': 1, 'Tidal Mastery': 5, 'Restorative Totems': 5, 'Mana Tide Totem': 1, 'Healing Way': 3, "Nature's Swiftness": 1, 'Purification': 5, 'Riptide': 1,
      'Ancestral Knowledge': 5, 'Thundering Strikes': 3,
    },
  },
  druid: {
    restoration: {
      "Nature's Focus": 5, 'Furor': 5, 'Naturalist': 5, 'Subtlety': 3, 'Natural Shapeshifter': 3, 'Reflection': 3, 'Gift of Nature': 5, 'Gift of the Earthmother': 1, 'Tranquil Spirit': 5, 'Improved Rejuvenation': 3, 'Swiftmend': 1,
      "Nature's Swiftness": 1, 'Living Spirit': 3, 'Improved Tranquility': 2, 'Improved Regrowth': 5, 'Wild Growth': 1,
    },
  },
  paladin: {
    holy: {
      'Divine Intellect': 5, 'Healing Light': 3, 'Spiritual Focus': 2, 'Voice of Truth': 1, 'Reverence': 3, 'Purifying Power': 2, 'Infusion of Light': 2, 'Illumination': 5, 'Divine Favor': 1, 'Divine Precision': 3, 'Holy Shock': 1,
      'Consecrated Ground': 2, 'Holy Power': 5, "Light's Vigil": 1,
      'Benediction': 5, 'Improved Judgement': 2, 'Holy Conduit': 2, 'Deflection': 1, 'Toughness': 5,
    },
  },
};

const out = { generated: new Date().toISOString().slice(0, 10), level: 60, builds: {} };
let bad = 0;
const emit = (cls, spec, byName, simulated, preset) => {
  const data = all[cls], ranks = ranksFromNames(data, byName), v = validateRanks(data, ranks);
  if (!v.ok || v.total !== 51) { bad++; console.log('INVALID', cls, spec, v.total, v.errors.join(' ; ')); }
  const talents = [];
  for (const sp of data.specs) {
    for (const t of sp.talents) {
      const rk = ranks[t.id];
      if (!rk) continue;
      talents.push({ id: t.id, points: rk, max: t.max_rank, tree: sp.id, row: t.row, desc: { en: t.desc.en[Math.min(rk, t.desc.en.length) - 1], fr: (t.desc.fr || t.desc.en)[Math.min(rk, (t.desc.fr || t.desc.en).length) - 1] } });
    }
  }
  (out.builds[cls] = out.builds[cls] || {})[spec] = { simulated, preset: preset || null, total: v.total, trees: v.bySpec, talents };
};
for (const [cls, specs] of Object.entries(FROM_PRESET)) for (const [spec, key] of Object.entries(specs)) emit(cls, spec, PRESETS[key], true, key);
for (const [cls, specs] of Object.entries(HEALERS)) for (const [spec, byName] of Object.entries(specs)) emit(cls, spec, byName, false);
const n = Object.values(out.builds).reduce((a, s) => a + Object.keys(s).length, 0);
console.log(n, 'builds,', bad, 'invalid');
if (!bad) writeFileSync(new URL('../../data/wow_guides/builds60.json', import.meta.url), JSON.stringify(out, null, 1));
