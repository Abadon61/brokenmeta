// node --test site_build/sim60/test
import test from 'node:test';
import assert from 'node:assert/strict';
import { meleeTable, rageConversion, armorDR, RATING_PER_PCT } from '../constants.js';
import { runBatch } from '../run.js';
import { furyKit } from '../warrior.js';

const player = (over = {}) => ({
  level: 60, resource: 'rage', dualWield: true,
  stats: Object.assign({ ap: 1400, crit: 0.20, hit: 0.06, haste: 1, weaponSkill: 300 }, over.stats || {}),
  weapons: [{ min: 85, max: 160, speed: 2.7 }, { min: 70, max: 130, speed: 2.5, offHand: true }],
});
const cfgFor = (p, build = {}, len = 180) => ({ fightLen: len, player: p, target: { armor: 3731, defense: 315, executeFrac: 0.2 }, kitFactory: () => furyKit(build) });

test('attack table vs a level-63 boss matches the Classic 1.12 values', () => {
  const t = meleeTable(300, 315);
  assert.ok(Math.abs(t.miss - 0.09) < 1e-9, 'miss 9%');
  assert.ok(Math.abs(t.dodge - 0.065) < 1e-9, 'dodge 6.5%');
  assert.ok(Math.abs(t.glance - 0.40) < 1e-9, 'glance 40%');
  assert.ok(Math.abs(t.glanceLow - 0.55) < 1e-9 && Math.abs(t.glanceHigh - 0.75) < 1e-9, 'glance damage 55-75%');
  assert.ok(Math.abs(t.critSuppression - 0.048) < 1e-9, 'crit suppression 4.8%');
  // 5 extra weapon skill shrinks every term
  const t5 = meleeTable(305, 315);
  assert.ok(t5.miss < t.miss && t5.dodge < t.dodge && t5.glance < t.glance);
});

test('rage conversion value is 230.6 at level 60 and armor DR is armor/(armor+5500)', () => {
  assert.ok(Math.abs(rageConversion(60) - 230.6) < 0.1);
  assert.ok(Math.abs(armorDR(3731) - 3731 / (3731 + 5500)) < 1e-9);
  assert.equal(armorDR(1e9), 0.75);
  assert.equal(RATING_PER_PCT.crit, 14);
});

test('same seed gives the exact same result (common random numbers)', () => {
  const a = runBatch(cfgFor(player()), 200, 7), b = runBatch(cfgFor(player()), 200, 7);
  assert.equal(a.mean, b.mean);
});

test('stats move DPS the right way', () => {
  const base = runBatch(cfgFor(player()), 1500, 1).mean;
  const moreAp = runBatch(cfgFor(player({ stats: { ap: 1800 } })), 1500, 1).mean;
  const moreHit = runBatch(cfgFor(player({ stats: { hit: 0.09 } })), 1500, 1).mean;
  const moreCrit = runBatch(cfgFor(player({ stats: { crit: 0.30 } })), 1500, 1).mean;
  assert.ok(moreAp > base * 1.1, 'AP helps');
  assert.ok(moreHit > base, 'hit helps below the cap');
  assert.ok(moreCrit > base, 'crit helps');
});

test('hit above the cap is wasted (yellow cap 9%, white DW cap 28%)', () => {
  const a = runBatch(cfgFor(player({ stats: { hit: 0.28 } })), 1500, 1);
  const b = runBatch(cfgFor(player({ stats: { hit: 0.40 } })), 1500, 1);
  assert.ok(Math.abs(a.mean - b.mean) / a.mean < 0.005, 'no gain past the white cap');
  assert.equal(b.breakdown['White (main hand)'].misses, 0);
});

test('rage never exceeds the cap and Boundless Rage raises it', () => {
  const r = runBatch(cfgFor(player()), 300, 3);
  assert.ok(r.rageGainedPerFight > 100);
});

test('Death Wish and Recklessness are used once in a 3 minute fight; Execute only in the last 20%', () => {
  const r = runBatch(cfgFor(player()), 200, 3);
  assert.ok(Math.abs(r.breakdown['Death Wish'].casts - 1) < 0.01);
  assert.ok(Math.abs(r.breakdown['Recklessness'].casts - 1) < 0.01);
  assert.ok(r.breakdown['Execute'].casts > 3 && r.breakdown['Execute'].casts < 25);
  const noExec = runBatch(cfgFor(player(), { executePhase: false }), 200, 3);
  assert.ok(!noExec.breakdown['Execute']);
});

test('Flurry raises uptime-weighted attack speed: more white swings than without it', () => {
  const withF = runBatch(cfgFor(player()), 800, 5);
  const noF = runBatch(cfgFor(player(), { flurry: 0 }), 800, 5);
  const swings = (r) => r.breakdown['White (main hand)'].hits + r.breakdown['White (main hand)'].misses + r.breakdown['White (main hand)'].dodges;
  assert.ok(swings(withF) > swings(noF) * 1.05);
});

test('speed: at least 800 fights/second of 180 s', () => {
  const t0 = Date.now(); runBatch(cfgFor(player()), 1000, 1);
  const rate = 1000 / ((Date.now() - t0) / 1000);
  assert.ok(rate > 800, `only ${rate.toFixed(0)} fights/s`);
});
