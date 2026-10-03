import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runBatch } from '../run.js';
import { paladinRetKit } from '../paladin.js';
import { shamanEnhancementKit } from '../shaman.js';
import { druidFeralKit } from '../druid.js';
import { buildCharacter } from '../character.js';
import { SAMPLE_RET, SAMPLE_ENH, SAMPLE_FERAL } from '../samples.js';
import { ranksToBuild, ranksFromNames, PRESETS } from '../talents.js';

const rd = (f) => JSON.parse(readFileSync(new URL('../data/' + f, import.meta.url)));
const spells = rd('spells60.json'), tals = rd('talents.json');
const KITS = { paladin_retribution: [paladinRetKit, 'paladin', SAMPLE_RET], shaman_enhancement: [shamanEnhancementKit, 'shaman', SAMPLE_ENH], druid_feral: [druidFeralKit, 'druid', SAMPLE_FERAL] };
const run = (k, over = {}, sample, len = 180, n = 600) => {
  const [kit, cls, smp] = KITS[k], tal = tals[cls];
  const build = Object.assign(ranksToBuild(cls, tal, ranksFromNames(tal, PRESETS[k])), over);
  const ch = buildCharacter(sample || smp);
  return runBatch({ fightLen: len, player: ch.player, target: ch.target, kitFactory: () => kit(build, spells) }, n, 1);
};

test('Retribution: white swings plus Seal of Command procs, Judgement and Holy Strike on cooldown, Hammer of Wrath at the end', () => {
  const r = run('paladin_retribution');
  for (const n of ['White (main hand)', 'Seal of Command', 'Judgement of Command', 'Holy Strike', 'Hammer of Wrath']) assert.ok(r.breakdown[n] && r.breakdown[n].dps > 0, n + ' ' + Object.keys(r.breakdown));
  assert.ok(r.breakdown['Holy Strike'].casts > 12 && r.breakdown['Judgement of Command'].casts > 12);
  assert.ok(r.mean > 200 && r.mean < 3000, 'dps ' + r.mean);
  assert.ok(!run('paladin_retribution', { sealOfCommand: 0 }, null, 60, 100).breakdown['Seal of Command'], 'the Seal needs the talent');
});

test('Enhancement: Stormstrike, Windfury and Maelstrom Weapon Lightning Bolts on top of the swings, Flurry up', () => {
  const r = run('shaman_enhancement');
  for (const n of ['White (main hand)', 'White (off-hand)', 'Stormstrike', 'Lightning Bolt']) assert.ok(r.breakdown[n] && r.breakdown[n].dps > 0, n + ' ' + Object.keys(r.breakdown));
  assert.ok(r.breakdown['Windfury'] && r.uptimes['Flurry'] > 0.2, 'Flurry ' + r.uptimes['Flurry']);
  assert.ok(r.mean > 200 && r.mean < 3000, 'dps ' + r.mean);
});

test('Feral cat: Rake and Rip up, Shred builds, Ferocious Bite at five points', () => {
  const r = run('druid_feral');
  for (const n of ['White (main hand)', 'Shred', 'Rake', 'Rip', 'Ferocious Bite']) assert.ok(r.breakdown[n] && (r.breakdown[n].dps > 0 || r.breakdown[n].casts > 0), n + ' ' + Object.keys(r.breakdown));
  assert.ok(r.breakdown['Rip'].dps > 20, 'Rip ' + r.breakdown['Rip'].dps);
  assert.ok(r.mean > 200 && r.mean < 3000, 'dps ' + r.mean);
});

test('talents and attack power move the DPS of the new melee specs', () => {
  for (const [k, talent] of [['paladin_retribution', 'conviction'], ['shaman_enhancement', 'flurry'], ['druid_feral', 'savageFury']]) {
    const base = run(k, {}, null, 180, 1500).mean;
    assert.ok(base > run(k, { [talent]: 0 }, null, 180, 1500).mean * 1.003, k + ' ' + talent);
    const [, , smp] = KITS[k], more = { ...smp, gear: smp.gear.concat([{ slot: 'neck', name: 'x', st: { atkpwr: 150 } }]) };
    assert.ok(run(k, {}, more, 180, 1500).mean > base * 1.02, k + ' attack power');
  }
});

test('Feral cat uses the Forever finishers and cooldowns: Savage Roar, Tiger Fury, Shifting Power, Berserk', () => {
  const r = run('druid_feral', {}, null, 180, 500);
  assert.ok(r.uptimes['Savage Roar'] > 0.7, 'Savage Roar ' + r.uptimes['Savage Roar']);
  assert.ok(r.breakdown["Tiger's Fury"].casts >= 5 && r.breakdown['Shifting Power'].casts > 5 && r.breakdown['Berserk'].casts >= 1);
  assert.ok(r.mean > 300, 'dps ' + r.mean);
  assert.ok(r.mean > run('druid_feral', { shiftingPower: 0, improvedShiftingPower: 0, berserk: 0 }, null, 180, 500).mean, 'the talents add DPS');
});
