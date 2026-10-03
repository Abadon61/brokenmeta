// SYNTHETIC test characters (not real items): realistic magnitudes for exercising the pipeline.
import { PRESET_RAID, PRESET_CASTER, PRESET_HUNTER } from './presets.js';

export const SAMPLE_FURY = {
  class: 'warrior', race: 'human',
  gear: [
    { slot: 'head', name: 'Sample helm', st: { str: 28, agi: 14, sta: 30, critstrkrtng: 28 } },
    { slot: 'chest', name: 'Sample chest', st: { str: 30, sta: 28, atkpwr: 40 } },
    { slot: 'legs', name: 'Sample legs', st: { str: 26, agi: 18, sta: 26 } },
    { slot: 'hands', name: 'Sample gloves', st: { str: 24, sta: 14, hitrtng: 10 } },
    { slot: 'trinket', name: 'Sample trinket', st: { atkpwr: 76 } },
    { slot: 'ring1', name: 'Sample ring', st: { str: 8, critstrkrtng: 14, hitrtng: 10 } },
    { slot: 'ring2', name: 'Sample ring 2', st: { atkpwr: 36, hitrtng: 10 } },
  ],
  weapons: [
    { min: 100, max: 190, speed: 2.7, type: 'sword' },
    { min: 80, max: 150, speed: 2.5, type: 'sword', offHand: true },
  ],
  ...PRESET_RAID,
};

export const SAMPLE_ROGUE = {
  class: 'rogue', race: 'human',
  gear: [
    { slot: 'head', name: 'Sample helm', st: { agi: 26, str: 10, sta: 24, critstrkrtng: 28 } },
    { slot: 'chest', name: 'Sample chest', st: { agi: 24, str: 12, sta: 26, atkpwr: 40 } },
    { slot: 'legs', name: 'Sample legs', st: { agi: 24, str: 10, sta: 24 } },
    { slot: 'hands', name: 'Sample gloves', st: { agi: 18, sta: 14, hitrtng: 10 } },
    { slot: 'trinket', name: 'Sample trinket', st: { atkpwr: 76 } },
    { slot: 'ring1', name: 'Sample ring', st: { agi: 12, critstrkrtng: 14, hitrtng: 10 } },
    { slot: 'ring2', name: 'Sample ring 2', st: { atkpwr: 36, hitrtng: 10 } },
  ],
  weapons: [
    { min: 70, max: 130, speed: 2.6, type: 'sword' },
    { min: 60, max: 110, speed: 2.4, type: 'sword', offHand: true },
  ],
  buffs: ['battle_shout', 'blessing_of_might', 'blessing_of_kings', 'mark_of_the_wild', 'strength_of_earth', 'grace_of_air', 'leader_of_the_pack'],
  consumables: ['elixir_mongoose', 'juju_power', 'juju_might', 'roids'],
  debuffs: ['sunder_armor_5', 'faerie_fire'],
};

export const SAMPLE_MAGE = {
  class: 'mage', race: 'human',
  gear: [
    { slot: 'head', name: 'Sample hood', st: { int: 30, sta: 22, splpwr: 40, critstrkrtng: 14, hitrtng: 10 } },
    { slot: 'chest', name: 'Sample robe', st: { int: 28, sta: 24, splpwr: 45, manargn: 6 } },
    { slot: 'legs', name: 'Sample legs', st: { int: 26, sta: 22, splpwr: 40, critstrkrtng: 14 } },
    { slot: 'hands', name: 'Sample gloves', st: { int: 18, sta: 14, splpwr: 24, hitrtng: 10 } },
    { slot: 'trinket', name: 'Sample trinket', st: { splpwr: 50 } },
    { slot: 'ring1', name: 'Sample ring', st: { int: 10, splpwr: 20, critstrkrtng: 14 } },
    { slot: 'ring2', name: 'Sample ring 2', st: { splpwr: 25, hitrtng: 10 } },
  ],
  weapons: [],
  ...PRESET_CASTER,
};

export const SAMPLE_WARLOCK = { ...SAMPLE_MAGE, class: 'warlock', race: 'human' };

export const SAMPLE_HUNTER = {
  class: 'hunter', race: 'dwarf',
  gear: [
    { slot: 'head', name: 'Sample helm', st: { agi: 26, int: 10, sta: 24, critstrkrtng: 28 } },
    { slot: 'chest', name: 'Sample chest', st: { agi: 24, int: 12, sta: 26, atkpwr: 40 } },
    { slot: 'legs', name: 'Sample legs', st: { agi: 24, int: 10, sta: 24 } },
    { slot: 'hands', name: 'Sample gloves', st: { agi: 18, sta: 14, hitrtng: 10 } },
    { slot: 'trinket', name: 'Sample trinket', st: { atkpwr: 76 } },
    { slot: 'ring1', name: 'Sample ring', st: { agi: 12, critstrkrtng: 14, hitrtng: 10 } },
    { slot: 'ring2', name: 'Sample ring 2', st: { atkpwr: 36, hitrtng: 10 } },
  ],
  weapons: [{ min: 85, max: 165, speed: 2.8, type: 'gun' }],
  ...PRESET_HUNTER,
};
