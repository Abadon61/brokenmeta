import test from 'node:test';
import assert from 'node:assert/strict';
import { buildCharacter } from '../character.js';
import { SAMPLE_FURY } from '../samples.js';

test('Strength gives 2 AP, 20 Agility give 1% crit, ratings convert at 14/10 per 1%', () => {
  const none = buildCharacter({ class: 'warrior', race: 'human', gear: [], weapons: [], buffs: [], consumables: [], debuffs: [] });
  // Human warrior L60: str 120 -> AP = 3*60 - 20 + 2*120 = 400
  assert.equal(none.summary.ap, 400);
  assert.ok(Math.abs(none.summary.crit - 80 / 20 / 100) < 1e-9);
  const plus = buildCharacter({ class: 'warrior', race: 'human', gear: [{ st: { str: 10, agi: 20, critstrkrtng: 14, hitrtng: 10, atkpwr: 50 } }], weapons: [], buffs: [], consumables: [], debuffs: [] });
  assert.equal(plus.summary.ap, 400 + 20 + 50);
  assert.ok(Math.abs(plus.summary.crit - (100 / 20 + 1) / 100) < 1e-9);
  assert.ok(Math.abs(plus.summary.hit - 0.01) < 1e-9);
});

test('Blessing of Kings multiplies primary stats; racial modifiers apply', () => {
  const k = buildCharacter({ class: 'warrior', race: 'orc', gear: [], weapons: [], buffs: ['blessing_of_kings'], consumables: [], debuffs: [] });
  assert.equal(k.summary.prim.str, Math.floor((120 + 3) * 1.1));
});

test('debuffs lower the boss armor (floored at 0) and the racial weapon skill is added', () => {
  const c = buildCharacter({ ...SAMPLE_FURY });
  assert.equal(c.target.armor, 3731 - 2250 - 505);
  assert.equal(c.player.stats.weaponSkill, 305);        // human + sword
  const o = buildCharacter({ ...SAMPLE_FURY, race: 'orc' });
  assert.equal(o.player.stats.weaponSkill, 300);        // orc + sword: no bonus
});

test('the addon-export path trusts the pre-computed totals', () => {
  const c = buildCharacter({ class: 'warrior', race: 'human', totals: { ap: 1900, crit: 0.25, hit: 0.08 }, weapons: [{ min: 1, max: 2, speed: 2 }] });
  assert.equal(c.player.stats.ap, 1900);
});
