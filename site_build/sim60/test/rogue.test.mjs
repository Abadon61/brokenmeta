import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runBatch } from '../run.js';
import { rogueKit } from '../rogue.js';
import { buildCharacter } from '../character.js';
import { SAMPLE_ROGUE } from '../samples.js';
import { ranksToBuild, ranksFromNames, PRESETS } from '../talents.js';

const spells = JSON.parse(readFileSync(new URL('../data/spells60.json', import.meta.url)));
const tal = JSON.parse(readFileSync(new URL('../data/talents.json', import.meta.url))).rogue;
const cfg = (build = {}, sample = SAMPLE_ROGUE, len = 180) => { const ch = buildCharacter(sample); return { fightLen: len, player: ch.player, target: ch.target, kitFactory: () => rogueKit(build, spells) }; };
const daggers = { ...SAMPLE_ROGUE, weapons: [{ min: 55, max: 100, speed: 1.8, type: 'dagger' }, { min: 50, max: 90, speed: 1.6, type: 'dagger', offHand: true }] };

test('rogue base: AP = 2*level - 20 + Str + Agi, crit = Agi / 29', () => {
  const c = buildCharacter({ class: 'rogue', race: 'human', gear: [], weapons: [], buffs: [], consumables: [], debuffs: [] });
  assert.equal(c.summary.ap, 100 + 85 + 120);
  assert.ok(Math.abs(c.summary.crit - 120 / 29 / 100) < 1e-9);
});

test('the rotation keeps Slice and Dice up, builds with Sinister Strike and spends at 5 combo points', () => {
  const r = runBatch(cfg(), 400, 1);
  assert.ok(r.uptimes['Slice and Dice'] > 0.9, 'SnD uptime ' + r.uptimes['Slice and Dice']);
  assert.ok(r.breakdown['Sinister Strike'].casts > 25);
  assert.ok(r.breakdown['Eviscerate'].casts > 2);
  assert.ok(r.breakdown['Adrenaline Rush'].casts === 1 && r.breakdown['Blade Flurry'].casts >= 1);
  assert.ok(r.mean > 200 && r.mean < 1500);
});

test('daggers switch the builder to Backstab; Mutilate needs the talent and two daggers', () => {
  assert.ok(runBatch(cfg({}, daggers), 100, 1).breakdown['Backstab']);
  assert.ok(runBatch(cfg({ mutilate: 1 }, daggers), 100, 1).breakdown['Mutilate']);
  assert.ok(!runBatch(cfg({ mutilate: 1 }), 100, 1).breakdown['Mutilate']);
});

test('talents and cooldowns move the DPS', () => {
  const base = runBatch(cfg(), 1500, 1).mean;
  assert.ok(base > runBatch(cfg({ malice: 0 }), 1500, 1).mean, 'Malice');
  assert.ok(base > runBatch(cfg({ dualWieldSpec: 0 }), 1500, 1).mean, 'Dual Wield Specialization');
  assert.ok(base > runBatch(cfg({ useCooldowns: false }), 1500, 1).mean, 'cooldowns');
  assert.ok(base > runBatch(cfg({ aggression: 0 }), 1500, 1).mean, 'Aggression');
});

test('the preset builds convert to kit builds', () => {
  const b = ranksToBuild('rogue', tal, ranksFromNames(tal, PRESETS.rogue_assassination));
  assert.equal(b.mutilate, 1); assert.equal(b.lethality, 5); assert.equal(b.bladeFlurry, 0);
  assert.ok(runBatch(cfg(b), 300, 1).mean > 150);
});

test('poisons (Classic values, assumed) add damage and the poison talents scale them', () => {
  const none = runBatch(cfg({ mhPoison: 'none', ohPoison: 'none' }), 1500, 1);
  const base = runBatch(cfg(), 1500, 1);
  assert.ok(base.breakdown['Instant Poison'].dps > 0 && base.breakdown['Deadly Poison'].dps > 0);
  assert.ok(!none.breakdown['Instant Poison'] && !none.breakdown['Deadly Poison']);
  assert.ok(base.mean > none.mean * 1.03, 'poisons add >3%: ' + base.mean + ' vs ' + none.mean);
  assert.ok(runBatch(cfg({ vilePoisons: 5, improvedPoisons: 5 }), 1500, 1).mean > base.mean, 'poison talents');
});
