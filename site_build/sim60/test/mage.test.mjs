import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runBatch } from '../run.js';
import { mageKit } from '../mage.js';
import { buildCharacter } from '../character.js';
import { SAMPLE_MAGE } from '../samples.js';
import { ranksToBuild, ranksFromNames, PRESETS } from '../talents.js';

const spells = JSON.parse(readFileSync(new URL('../data/spells60.json', import.meta.url)));
const tal = JSON.parse(readFileSync(new URL('../data/talents.json', import.meta.url))).mage;
const preset = (k, over = {}) => Object.assign(ranksToBuild('mage', tal, ranksFromNames(tal, PRESETS[k])), { rotation: k.split('_')[1] }, over);
const cfg = (build, sample = SAMPLE_MAGE, len = 180) => { const ch = buildCharacter(sample); return { fightLen: len, player: ch.player, target: ch.target, kitFactory: () => mageKit(build, spells) }; };

test('caster stat block: spell power, spell crit from Intellect, mana from Intellect', () => {
  const c = buildCharacter({ class: 'mage', race: 'human', gear: [], weapons: [], buffs: [], consumables: [], debuffs: [] });
  assert.equal(c.summary.sp, 0);
  assert.ok(Math.abs(c.summary.crit - (126 / 59.5 / 100 + 0.002)) < 1e-9);
  assert.equal(c.summary.mana, 1213 + 15 * (126 - 20));
  assert.ok(c.target.spellMiss > 0.1 && c.target.spellMitigation > 0);
});

test('Fire rotation: Scorch keeps Fire Vulnerability up, Fire Blast on cooldown, mana stays bounded', () => {
  const r = runBatch(cfg(preset('mage_fire')), 400, 1);
  assert.ok(r.uptimes['Fire Vulnerability'] > 0.8, 'vuln ' + r.uptimes['Fire Vulnerability']);
  assert.ok(r.breakdown['Fire Blast'].casts > 15);
  assert.ok(r.breakdown['Fireball'] || r.breakdown['Frostfire Bolt']);
  assert.ok(r.breakdown['Ignite'].dps > 0);
  assert.ok(r.mean > 300 && r.mean < 3000, 'dps ' + r.mean);
});

test('Frost and Arcane rotations run and are driven by their talents', () => {
  const f = runBatch(cfg(preset('mage_frost')), 400, 1);
  assert.ok(f.breakdown['Frostbolt'].casts > 20 && f.breakdown['Ice Lance'].casts > 0 && f.mean > 300);
  const a = runBatch(cfg(preset('mage_arcane')), 400, 1);
  assert.ok(a.breakdown['Arcane Missiles'].casts > 10 && a.breakdown['Arcane Power'].casts >= 1 && a.mean > 200);
});

test('talents and spell power move the DPS', () => {
  const fire = preset('mage_fire'), base = runBatch(cfg(fire), 1500, 1).mean;
  assert.ok(base > runBatch(cfg({ ...fire, firePower: 0 }), 1500, 1).mean * 1.03, 'Fire Power');
  assert.ok(base > runBatch(cfg({ ...fire, criticalMass: 0 }), 1500, 1).mean, 'Critical Mass');
  assert.ok(base > runBatch(cfg({ ...fire, ignite: 0 }), 1500, 1).mean * 1.02, 'Ignite');
  const more = { ...SAMPLE_MAGE, gear: SAMPLE_MAGE.gear.concat([{ slot: 'neck', name: 'x', st: { splpwr: 100 } }]) };
  assert.ok(runBatch(cfg(fire, more), 1500, 1).mean > base * 1.05, 'spell power');
});

test('the mana pool limits a long fight', () => {
  const short = runBatch(cfg(preset('mage_frost'), SAMPLE_MAGE, 40), 300, 1).mean, long = runBatch(cfg(preset('mage_frost'), SAMPLE_MAGE, 300), 300, 1).mean;
  assert.ok(long < short, 'oom: ' + short + ' vs ' + long);
});
