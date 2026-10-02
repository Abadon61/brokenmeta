// SYNTHETIC test characters (not real items): realistic magnitudes for exercising the pipeline.
import { PRESET_RAID } from './presets.js';

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
