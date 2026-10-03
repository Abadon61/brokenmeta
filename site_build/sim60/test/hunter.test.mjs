import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runBatch } from '../run.js';
import { hunterKit, hunterMeleeKit } from '../hunter.js';
import { buildCharacter } from '../character.js';
import { SAMPLE_HUNTER, SAMPLE_HUNTER_MELEE } from '../samples.js';
import { ranksToBuild, ranksFromNames, PRESETS } from '../talents.js';

const spells = JSON.parse(readFileSync(new URL('../data/spells60.json', import.meta.url)));
const tal = JSON.parse(readFileSync(new URL('../data/talents.json', import.meta.url))).hunter;
const preset = (k, over = {}) => Object.assign(ranksToBuild('hunter', tal, ranksFromNames(tal, PRESETS[k])), k.endsWith('marksmanship') ? { pet: 'none' } : {}, over);
const cfg = (build, sample = SAMPLE_HUNTER, len = 180) => { const ch = buildCharacter(sample); return { fightLen: len, player: ch.player, target: ch.target, kitFactory: () => hunterKit(build, spells) }; };

test('hunter stat block: ranged attack power from Agility, crit from Agility / 53, ranged weapon kept apart', () => {
  const c = buildCharacter({ class: 'hunter', race: 'human', gear: [], weapons: [{ min: 50, max: 90, speed: 2.5, type: 'bow' }], buffs: [], consumables: [], debuffs: [] });
  assert.equal(c.summary.ap, 2 * 60 - 10 + 126);
  assert.ok(c.player.ranged && c.player.weapons.length === 0 && !c.player.dualWield);
  assert.ok(c.player.stats.mana > 1300);
});

test('Marksmanship rotation: Auto Shot carries it, Arcane / Multi-Shot / Serpent Sting add, Rapid Fire fires once per fight', () => {
  const r = runBatch(cfg(preset('hunter_marksmanship')), 400, 1);
  assert.ok(r.breakdown['Auto Shot'].dps > 100 && r.breakdown['Arcane Shot'].casts > 15 && r.breakdown['Multi-Shot'].casts > 5, JSON.stringify(Object.keys(r.breakdown)));
  assert.ok(r.breakdown['Serpent Sting'].dps > 5 && r.breakdown['Rapid Fire'].casts === 1);
  assert.ok(!r.breakdown['Pet (melee)'], 'Lone Wolf build has no pet');
  assert.ok(r.mean > 250 && r.mean < 3000, 'dps ' + r.mean);
});

test('Beast Mastery adds the pet, Bestial Wrath and the Hawk', () => {
  const r = runBatch(cfg(preset('hunter_beastmastery')), 400, 1);
  assert.ok(r.breakdown['Pet (melee)'].dps > 20 && r.breakdown['Pet (Claw)'].dps > 5);
  assert.ok(r.breakdown['Bestial Wrath'].casts >= 1 && r.breakdown['Summon Hawk'].casts >= 1 && r.breakdown['Hawk'].dps > 0);
  assert.ok(r.uptimes['Bestial Wrath'] > 0.05 && r.uptimes['Frenzy'] > 0.2);
});

test('talents, attack power and haste move the DPS', () => {
  const mm = preset('hunter_marksmanship'), base = runBatch(cfg(mm), 1500, 1).mean;
  assert.ok(base > runBatch(cfg({ ...mm, carefulAim: 0 }), 1500, 1).mean * 1.01, 'Careful Aim');
  assert.ok(base > runBatch(cfg({ ...mm, rangedSpec: 0 }), 1500, 1).mean * 1.02, 'Ranged Weapon Specialization');
  assert.ok(base > runBatch(cfg({ ...mm, quiver: false }), 1500, 1).mean * 1.05, 'quiver haste');
  const more = { ...SAMPLE_HUNTER, gear: SAMPLE_HUNTER.gear.concat([{ slot: 'neck', name: 'x', st: { atkpwr: 120 } }]) };
  assert.ok(runBatch(cfg(mm, more), 1500, 1).mean > base * 1.02, 'attack power');
  assert.ok(runBatch(cfg({ ...mm, useCooldowns: false }), 1500, 1).mean < base, 'Rapid Fire');
});

test('Survival in melee: swings, Raptor Strike, Strider Kick and Mongoose Bite after a dodge, no ranged shots', () => {
  const tal2 = tal, build = Object.assign(ranksToBuild('hunter', tal2, ranksFromNames(tal2, PRESETS.hunter_melee)), {});
  const go = (b, sample = SAMPLE_HUNTER_MELEE) => { const ch = buildCharacter(sample); return runBatch({ fightLen: 180, player: ch.player, target: ch.target, kitFactory: () => hunterMeleeKit(b, spells) }, 800, 1); };
  const r = go(build);
  for (const n of ['White (main hand)', 'White (off-hand)', 'Raptor Strike', 'Strider Kick', 'Mongoose Bite']) assert.ok(r.breakdown[n] && r.breakdown[n].dps > 0, n + ' ' + Object.keys(r.breakdown));
  assert.ok(!r.breakdown['Auto Shot'] && !r.breakdown['Arcane Shot']);
  assert.ok(r.mean > 200 && r.mean < 3000, 'dps ' + r.mean);
  assert.ok(r.mean > go({ ...build, predatorsEdge: 0 }).mean, "Predator's Edge");
  assert.ok(!go({ ...build, striderKick: 0 }).breakdown['Strider Kick'], 'the talent');
});
