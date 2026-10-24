// Numbers aligned on the WoWSims Forever engine (2026-10-24): each one was checked against their published engine run on the same character.
import test from 'node:test';
import assert from 'node:assert/strict';
import { Sim } from '../engine.js';
import { spiritRegenPerSec } from '../spells.js';
import { makeDeepWounds } from '../shared.js';

test('spirit mana regeneration is 6.25 + Spirit / 8 for every class (core/mana.go)', () => {
  assert.equal(spiritRegenPerSec({ spi: 80 }), 6.25 + 10);
  assert.equal(spiritRegenPerSec({ spi: 80 }, false), 6.25 + 10);
});

test('a missed special attack refunds 80% of its rage', () => {
  const sim = Object.create(Sim.prototype);
  sim.rage = 50; sim.rageCap = 100; sim.now = 3; sim.mods = {}; sim.counters = {}; sim.stats = {};
  sim.gainRage = (n) => { sim.rage = Math.min(sim.rageCap, sim.rage + n); };
  sim.spendRage(20);
  assert.equal(sim.rage, 30);
  sim.refundRage();
  assert.equal(sim.rage, 46);
  sim.refundRage();                 // only once per spend
  assert.equal(sim.rage, 46);
});

test('Deep Wounds adds the share of the main-hand average to what is unticked and keeps the tick timer', () => {
  const rec = [], sched = [];
  const sim = { mods: { dmgMult: 1 }, schedule: (d, f) => sched.push([d, f]), record: (n, d) => rec.push(d) };
  const apply = makeDeepWounds(sim, 100, 0.6);          // 60 damage over four ticks = 15 each
  apply();
  assert.equal(sched.length, 1);
  sched.shift()[1]();                                   // first tick: 15
  assert.equal(rec[0], 15);
  apply();                                              // a crit with three ticks left (45) + 60 = 105 over four ticks
  sched.shift()[1]();
  assert.equal(rec[1], 105 / 4);
});
