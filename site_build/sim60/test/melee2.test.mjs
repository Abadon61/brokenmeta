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

test('Enhancement: Windfury Weapon gives the client\'s 2 extra attacks, Searing Totem is dropped, Maelstrom Weapon needs full stacks at 5 ranks', () => {
  const r = run('shaman_enhancement', {}, null, 180, 300);
  assert.ok(r.breakdown['Searing Bolt'] && r.breakdown['Searing Bolt'].dps > 5);
  const noTotem = run('shaman_enhancement', { fireTotem: 'none' }, null, 180, 300);
  assert.ok(!noTotem.breakdown['Searing Bolt']);
  assert.ok(r.breakdown['Windfury'].casts > 5);
  const weak = run('shaman_enhancement', { maelstromWeapon: 1 }, null, 180, 300);
  assert.ok(weak.mean < r.mean + 5, 'a single rank is no better than five');
});

test('Enhancement: the Windfury extra attacks show their own damage line', () => {
  const r = run('shaman_enhancement', {}, null, 180, 300);
  assert.ok(r.breakdown['Windfury'].dps > 15, 'Windfury dps ' + r.breakdown['Windfury'].dps);
});

test('Enhancement: Earth Shock is cast on its cooldown and adds damage', () => {
  const r = run('shaman_enhancement', {}, null, 180, 400);
  assert.ok(r.breakdown['Earth Shock'] && r.breakdown['Earth Shock'].casts > 5, 'Earth Shock ' + JSON.stringify(r.breakdown['Earth Shock']));
  assert.ok(r.mean > run('shaman_enhancement', { earthShock: false }, null, 180, 400).mean, 'Earth Shock adds DPS');
});

test('Enhancement: Stormstrike comes first, Lightning Bolt is cast from one Maelstrom stack, Improved Stormstrike and Convection pay for it, swings go on while casting', () => {
  const base = run('shaman_enhancement', {}, null, 180, 500);
  assert.ok(base.breakdown['Lightning Bolt'].casts > 5, 'LB casts ' + base.breakdown['Lightning Bolt'].casts);
  assert.ok(base.mean > run('shaman_enhancement', { improvedStormstrike: 0 }, null, 180, 500).mean, 'Improved Stormstrike mana');
  assert.ok(base.mean > run('shaman_enhancement', { convection: 0, elementalFocus: 0 }, null, 180, 500).mean, 'Convection and Elemental Focus');
  const swings = (r) => { const w = r.breakdown['White (main hand)']; return w.hits + w.misses + w.dodges + w.glances; };
  const none = run('shaman_enhancement', { earthShock: false, flameShock: false, maelstromMin: 9, fireTotem: 'none' }, null, 180, 300), spam = run('shaman_enhancement', { maelstromMin: 0 }, null, 180, 300);
  assert.ok(spam.breakdown['Lightning Bolt'].casts > 20 && Math.abs(swings(spam) - swings(none)) < 3, 'casting does not interrupt the swings: ' + swings(spam) + ' vs ' + swings(none));
});

test('Enhancement: the Stormstrike bonus is worth more on a Lightning Bolt than on the Earth Shock, and Frost Shock is no better than Earth Shock', () => {
  const twoHand = { ...SAMPLE_ENH, weapons: [{ min: 200, max: 300, speed: 3.2, type: 'two-handed axe', twoHand: true }] };       // what the ranking plays (two-hand weapon)
  const bolt = run('shaman_enhancement', {}, twoHand, 180, 1500), shock = run('shaman_enhancement', { ssBuffOn: 'shock' }, twoHand, 180, 1500);
  assert.ok(bolt.mean > shock.mean, 'bolt first ' + bolt.mean + ' vs shock first ' + shock.mean);
  assert.ok(run('shaman_enhancement', { shockSpell: 'frost' }, twoHand, 180, 1500).mean < bolt.mean * 1.01, 'Frost Shock does not beat Earth Shock');
});
