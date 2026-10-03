import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runBatch } from '../run.js';
import { warlockKit } from '../warlock.js';
import { buildCharacter } from '../character.js';
import { SAMPLE_WARLOCK } from '../samples.js';
import { ranksToBuild, ranksFromNames, PRESETS } from '../talents.js';

const spells = JSON.parse(readFileSync(new URL('../data/spells60.json', import.meta.url)));
const tal = JSON.parse(readFileSync(new URL('../data/talents.json', import.meta.url))).warlock;
const preset = (k, over = {}) => Object.assign(ranksToBuild('warlock', tal, ranksFromNames(tal, PRESETS[k])), { rotation: k.endsWith('affliction') ? 'affliction' : 'destruction' }, k.endsWith('demonology') ? { sacrifice: 'imp' } : {}, over);
const cfg = (build, sample = SAMPLE_WARLOCK, len = 180) => { const ch = buildCharacter(sample); return { fightLen: len, player: ch.player, target: ch.target, kitFactory: () => warlockKit(build, spells) }; };

test('warlock stat block uses the caster path with Warlock crit and mana', () => {
  const c = buildCharacter({ class: 'warlock', race: 'human', gear: [], weapons: [], buffs: [], consumables: [], debuffs: [] });
  assert.ok(Math.abs(c.summary.crit - 115 / 60.6 / 100) < 1e-9);
  assert.equal(c.summary.mana, 1200 + 15 * (115 - 20));
});

test('Affliction keeps its damage-over-time effects up and Life Tap pays for the mana', () => {
  const r = runBatch(cfg(preset('warlock_affliction')), 400, 1);
  assert.ok(r.breakdown['Corruption'].dps > 20 && r.breakdown['Bane of Doom'] || r.breakdown['Bane of Agony']);
  assert.ok(r.breakdown['Shadow Bolt'].casts > 20 && r.breakdown['Life Tap'].casts > 3, JSON.stringify(Object.keys(r.breakdown)));
  assert.ok(r.breakdown['Imp Firebolt'].dps > 0);
  assert.ok(r.mean > 300 && r.mean < 3000, 'dps ' + r.mean);
});

test('Destruction uses Immolate, Conflagrate and Incinerate; the capstone needs the talent', () => {
  const r = runBatch(cfg(preset('warlock_destruction')), 400, 1);
  assert.ok(r.breakdown['Immolate'] && r.breakdown['Conflagrate'].casts > 5 && (r.breakdown['Incinerate'] || r.breakdown['Shadow Bolt']));
  assert.ok(!runBatch(cfg(preset('warlock_destruction', { conflagrate: 0 })), 100, 1).breakdown['Conflagrate']);
  const s = runBatch(cfg(preset('warlock_demonology')), 400, 1);
  assert.ok(!s.breakdown['Imp Firebolt'], 'a sacrificed Imp does not attack');
});

test('talents and spell power move the DPS; Demonic Sacrifice adds shadow damage', () => {
  const aff = preset('warlock_affliction'), base = runBatch(cfg(aff), 1500, 1).mean;
  assert.ok(base > runBatch(cfg({ ...aff, shadowMastery: 0 }), 1500, 1).mean * 1.02, 'Shadow Mastery');
  assert.ok(base > runBatch(cfg({ ...aff, malediction: 0 }), 1500, 1).mean, 'Malediction');
  const more = { ...SAMPLE_WARLOCK, gear: SAMPLE_WARLOCK.gear.concat([{ slot: 'neck', name: 'x', st: { splpwr: 100 } }]) };
  assert.ok(runBatch(cfg(aff, more), 1500, 1).mean > base * 1.05, 'spell power');
  const sac = { ...aff, demonicSacrifice: 1, sacrifice: 'imp' };
  assert.ok(runBatch(cfg(sac), 1500, 1).mean > runBatch(cfg({ ...aff, pet: 'none' }), 1500, 1).mean * 1.05, 'sacrifice');
});
