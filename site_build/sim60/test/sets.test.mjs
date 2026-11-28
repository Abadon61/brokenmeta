import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runBatch } from '../run.js';
import { buildCharacter } from '../character.js';
import { makeKit } from '../kits.js';
import * as S from '../samples.js';
import { ranksToBuild, ranksFromNames, PRESETS } from '../talents.js';

const data = JSON.parse(readFileSync(new URL('../data/spells60.json', import.meta.url)));
const tal = JSON.parse(readFileSync(new URL('../data/talents.json', import.meta.url)));
const dps = (id, cls, sample, sets, n = 600) => {
  const ch = buildCharacter(sample); ch.player.sets = sets;
  const build = ranksToBuild(cls, tal[cls], ranksFromNames(tal[cls], PRESETS[id]));
  return runBatch({ fightLen: 180, player: ch.player, target: ch.target, kitFactory: () => makeKit(id, build, data) }, n, 5).mean;
};

test('buildCharacter counts the worn pieces of each class set from the gear `set` ids', () => {
  const c = buildCharacter({ class: 'rogue', race: 'human', gear: [{ slot: 'head', st: {}, set: 1934 }, { slot: 'chest', st: {}, set: 1934 }, { slot: 'feet', st: {} }], weapons: [], buffs: [], consumables: [], debuffs: [] });
  assert.deepEqual(c.player.sets, { 1934: 2 });
});

test('Sanctified set bonuses raise the DPS of the specs whose spells they touch (and do nothing below the piece count)', () => {
  const rogue = dps('rogue_assassination', 'rogue', S.SAMPLE_ROGUE, {});
  assert.ok(dps('rogue_assassination', 'rogue', S.SAMPLE_ROGUE, { 1934: 6 }) > rogue * 1.03, 'Duskwraith Armor');
  assert.ok(Math.abs(dps('rogue_assassination', 'rogue', S.SAMPLE_ROGUE, { 1934: 1 }) - rogue) < 1e-9, 'one piece changes nothing');
  assert.ok(dps('rogue_assassination', 'rogue', S.SAMPLE_ROGUE, { 1933: 8 }) === rogue, 'another set does not count');
});
