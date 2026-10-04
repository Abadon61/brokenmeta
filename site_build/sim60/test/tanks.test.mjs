import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runBatch } from '../run.js';
import { warriorProtKit, paladinProtKit, druidBearKit } from '../tanks.js';
import { buildCharacter } from '../character.js';
import { SAMPLE_PROT_WAR, SAMPLE_PROT_PAL, SAMPLE_BEAR } from '../samples.js';
import { ranksToBuild, ranksFromNames, PRESETS } from '../talents.js';

const rd = (f) => JSON.parse(readFileSync(new URL('../data/' + f, import.meta.url)));
const spells = rd('spells60.json'), tals = rd('talents.json');
const KITS = { warrior_protection: [warriorProtKit, 'warrior', SAMPLE_PROT_WAR], paladin_protection: [paladinProtKit, 'paladin', SAMPLE_PROT_PAL], druid_bear: [druidBearKit, 'druid', SAMPLE_BEAR] };
const run = (k, over = {}, sample, len = 120, n = 500) => {
  const [kit, cls, smp] = KITS[k], tal = tals[cls];
  const build = Object.assign(ranksToBuild(cls, tal, ranksFromNames(tal, PRESETS[k])), over);
  const ch = buildCharacter(sample || smp);
  const r = runBatch({ fightLen: len, player: ch.player, target: ch.target, kitFactory: () => kit(build, spells) }, n, 1);
  return { r, ch, tps: r.counters.threat / len, dtps: r.counters.dmgTaken / len };
};

test('the tank character: armor, health, defense, dodge, parry and block come from the gear', () => {
  const t = buildCharacter(SAMPLE_PROT_WAR).summary.tank;
  assert.equal(t.defense, 300 + Math.floor((8 + 8 + 6 + 5 + 5) / 4));
  assert.ok(t.armor > 3000 && t.health > 4000 && t.shield && t.blockValue > 40 && t.parry === 0.05);
  const noShield = buildCharacter({ ...SAMPLE_PROT_WAR, gear: SAMPLE_PROT_WAR.gear.filter((g) => g.slot !== 'shield') }).summary.tank;
  assert.ok(!noShield.shield && noShield.blockValue === 0 && noShield.armor < t.armor);
});

test('the boss swings at the tank: avoidance, blocks, crits and crushes are counted and armor lowers the damage taken', () => {
  const { r, dtps } = run('warrior_protection');
  const c = r.counters;
  assert.ok(Math.abs(c.swings - 60) < 1, 'swings ' + c.swings);
  assert.ok(c.boss_miss > 0 && c.boss_dodge > 0 && c.boss_parry > 0 && c.boss_block > 0 && c.boss_crush > 0 && c.dmgTaken > 0);
  const heavy = { ...SAMPLE_PROT_WAR, gear: SAMPLE_PROT_WAR.gear.map((g) => ({ ...g, st: { ...g.st, armor: (g.st.armor || 0) * 3 } })) };
  assert.ok(run('warrior_protection', {}, heavy).dtps < dtps * 0.85, 'armor');
  const hard = { ...SAMPLE_PROT_WAR, boss: { dmg: 18000 } };
  assert.ok(run('warrior_protection', {}, hard).dtps > dtps * 1.6, 'boss damage');
});

test('Protection Warrior: Shield Slam, Revenge after an avoided hit, Sunder Armor threat, rage from damage taken', () => {
  const { r, tps } = run('warrior_protection');
  for (const n of ['Shield Slam', 'Revenge', 'Sunder Armor', 'White (main hand)']) assert.ok(r.breakdown[n] && r.breakdown[n].casts + r.breakdown[n].dps > 0, n + ' ' + Object.keys(r.breakdown));
  assert.ok(r.breakdown['Shield Slam'].casts > 12 && r.breakdown['Revenge'].casts > 5);
  assert.ok(tps > 200 && tps < 3000, 'TPS ' + tps);
  assert.ok(!run('warrior_protection', { shieldSlam: 0 }, null, 60, 100).r.breakdown['Shield Slam'], 'the talent');
  assert.ok(run('warrior_protection', { defiance: 3 }, null, 120, 800).tps > run('warrior_protection', { defiance: 0 }, null, 120, 800).tps, 'Defiance');
  assert.ok(run('warrior_protection', { anticipation: 5 }, null, 120, 800).dtps < run('warrior_protection', { anticipation: 0 }, null, 120, 800).dtps, 'Anticipation lowers the damage taken');
});

test('Protection Paladin: Holy Shield adds blocks and holy threat, the seal and Holy Strike keep going', () => {
  const { r, tps } = run('paladin_protection');
  for (const n of ['Seal of Righteousness', 'Holy Strike', 'Judgement of Righteousness']) assert.ok(r.breakdown[n] && r.breakdown[n].dps > 0, n + ' ' + Object.keys(r.breakdown));
  assert.ok(r.breakdown['Holy Shield'] && r.breakdown['Holy Shield'].casts > 8 && r.breakdown['Holy Shield'].dps > 0);
  assert.ok(tps > 150 && tps < 3000, 'TPS ' + tps);
  const without = run('paladin_protection', { holyShield: 0 }, null, 120, 800);
  assert.ok(run('paladin_protection', {}, null, 120, 800).r.counters.boss_block > without.r.counters.boss_block * 1.3, 'Holy Shield raises the blocks');
});

test('Bear Druid: Dire Bear armor, Swipe and Lacerate, rage from damage taken, dodge from Natural Reaction', () => {
  const { r, ch, tps } = run('druid_bear');
  for (const n of ['Swipe', 'Lacerate', 'White (main hand)']) assert.ok(r.breakdown[n] && r.breakdown[n].casts + r.breakdown[n].dps > 0, n + ' ' + Object.keys(r.breakdown));
  assert.ok(tps > 100 && tps < 3000, 'TPS ' + tps);
  const a = run('druid_bear', { naturalReaction: 5 }, null, 120, 800), z = run('druid_bear', { naturalReaction: 0 }, null, 120, 800);
  assert.ok(a.r.counters.boss_dodge > z.r.counters.boss_dodge, 'Natural Reaction dodge');
});

test('Protection Warrior spends spare rage on Heroic Strike before Sunder Armor; the Bear mauls on top of Swipe', () => {
  const w = run('warrior_protection', {}, null, 120, 600);
  assert.ok(w.r.breakdown['Heroic Strike'] && w.r.breakdown['Heroic Strike'].dps > 20, 'Heroic Strike ' + JSON.stringify(w.r.breakdown['Heroic Strike']));
  assert.ok(w.tps > run('warrior_protection', { useHeroicStrike: false }, null, 120, 600).tps, 'Heroic Strike adds threat');
  const bear = run('druid_bear', {}, null, 120, 600);
  assert.ok(bear.r.breakdown['Maul'] && bear.r.breakdown['Maul'].dps > 30, 'Maul ' + JSON.stringify(bear.r.breakdown['Maul']));
  assert.ok(bear.tps > run('druid_bear', { useSwipe: false }, null, 120, 600).tps * 0.95, 'Swipe is no loss');
});
