import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateRanks, parseShareHash, ranksToBuild, ranksFromNames, PRESETS, NAME_TO_KEY } from '../talents.js';
import { runBatch } from '../run.js';
import { furyKit, armsKit } from '../warrior.js';
import { buildCharacter } from '../character.js';
import { SAMPLE_FURY } from '../samples.js';

const all = JSON.parse(readFileSync(new URL('../data/talents.json', import.meta.url)));
const data = all.warrior;
const spells = JSON.parse(readFileSync(new URL('../data/spells60.json', import.meta.url)));

test('the preset builds follow the tree rules (gates, prerequisites, 51 points)', () => {
  for (const [k, p] of Object.entries(PRESETS)) {
    const d = all[k.split('_')[0]];
    const r = validateRanks(d, ranksFromNames(d, p));
    assert.ok(r.ok, k + ': ' + r.errors.join('; '));
    assert.ok(r.total <= 51);
  }
});

test('the rules reject a locked row, a missing prerequisite and too many points', () => {
  assert.ok(!validateRanks(data, ranksFromNames(data, { 'Bloodthirst': 1 })).ok);
  assert.ok(!validateRanks(data, ranksFromNames(data, { 'Flurry': 5 })).ok);
  const big = {}; data.specs.forEach((s) => s.talents.forEach((t) => { big[t.id] = t.max_rank; }));
  assert.ok(!validateRanks(data, big).ok);
});

test('a calculator share link round-trips into talent ranks', () => {
  const ranks = ranksFromNames(data, PRESETS.warrior_fury);
  const hash = '#b=' + data.rev + data.specs.map((s) => '.' + s.talents.slice().sort((a, b) => a.row - b.row || a.col - b.col).map((t) => ranks[t.id] || 0).join('')).join('');
  const back = parseShareHash(data, 'https://brokenmeta.gg/wow-forever/talents/warrior/' + hash);
  assert.ok(back.revMatches);
  assert.deepEqual(back.ranks, ranks);
  assert.equal(parseShareHash(data, '#nonsense').error, 'format');
});

test('ranksToBuild exposes only the simulated talents', () => {
  const b = ranksToBuild('warrior', data, ranksFromNames(data, PRESETS.warrior_fury));
  assert.equal(b.cruelty, 5); assert.equal(b.flurry, 5); assert.equal(b.mortalStrike, 0);
  assert.ok(Object.keys(b).every((k) => Object.values(NAME_TO_KEY.warrior).includes(k)));
});

const cfg = (kit, build, sample = SAMPLE_FURY) => { const ch = buildCharacter(sample); return { fightLen: 180, player: ch.player, target: ch.target, kitFactory: () => kit(build, spells) }; };
const fury = (over) => Object.assign(ranksToBuild('warrior', data, ranksFromNames(data, PRESETS.warrior_fury)), over);
const arms = (over) => Object.assign(ranksToBuild('warrior', data, ranksFromNames(data, PRESETS.warrior_arms)), over);
const twoHand = { ...SAMPLE_FURY, weapons: [{ min: 210, max: 330, speed: 3.5, type: 'two-handed sword', twoHand: true }] };

test('talents move the simulated DPS: Flurry, Cruelty, Dual Wield Specialization', () => {
  const base = runBatch(cfg(furyKit, fury()), 1500, 1).mean;
  assert.ok(base > runBatch(cfg(furyKit, fury({ flurry: 0 })), 1500, 1).mean * 1.02, 'Flurry');
  assert.ok(base > runBatch(cfg(furyKit, fury({ cruelty: 0 })), 1500, 1).mean * 1.02, 'Cruelty');
  assert.ok(base > runBatch(cfg(furyKit, fury({ dualWieldSpec: 0 })), 1500, 1).mean * 1.005, 'Dual Wield Specialization');
});

test('a build without the capstone cannot cast it', () => {
  assert.ok(!runBatch(cfg(furyKit, fury({ bloodthirst: 0 })), 100, 1).breakdown['Bloodthirst']);
  assert.ok(!runBatch(cfg(armsKit, arms({ mortalStrike: 0 }), twoHand), 100, 1).breakdown['Mortal Strike']);
  assert.ok(runBatch(cfg(armsKit, arms(), twoHand), 100, 1).breakdown['Mortal Strike']);
});

test('Arms talents: Two-Handed Specialization and Impale add damage', () => {
  const base = runBatch(cfg(armsKit, arms(), twoHand), 1500, 1).mean;
  assert.ok(base > runBatch(cfg(armsKit, arms({ twoHandSpec: 0 }), twoHand), 1500, 1).mean);
  assert.ok(base > runBatch(cfg(armsKit, arms({ impale: 0 }), twoHand), 1500, 1).mean);
});

test('Arms: Bloodthrill lets Rend open Overpower without a dodge', () => {
  const withB = runBatch(cfg(armsKit, arms(), twoHand), 800, 1), without = runBatch(cfg(armsKit, arms({ bloodthrill: 0 }), twoHand), 800, 1);
  assert.ok(withB.breakdown['Rend'] && withB.breakdown['Overpower'].casts > without.breakdown['Overpower'].casts * 1.5, 'Overpower casts');
  assert.ok(withB.mean > without.mean, 'Bloodthrill adds DPS');
});
