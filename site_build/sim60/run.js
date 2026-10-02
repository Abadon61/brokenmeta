// Batch runner: many fights with seeds base+i (common random numbers across configs).
import { Sim } from './engine.js';

export function runBatch(cfg, iterations, seedBase = 1) {
  let sum = 0, sumSq = 0;
  const by = Object.create(null), up = Object.create(null);
  let rageWasted = 0, rageGained = 0;
  for (let i = 0; i < iterations; i++) {
    const sim = new Sim(Object.assign({}, cfg, { seed: seedBase + i, spec: cfg.kitFactory() }));
    sim.run();
    const dps = sim.total / cfg.fightLen;
    sum += dps; sumSq += dps * dps;
    for (const k in sim.dmg) {
      const e = sim.dmg[k], t = by[k] || (by[k] = { dmg: 0, hits: 0, crits: 0, misses: 0, dodges: 0, glances: 0, casts: 0 });
      t.dmg += e.dmg; t.hits += e.hits; t.crits += e.crits; t.misses += e.misses; t.dodges += e.dodges; t.glances += e.glances; t.casts += e.casts;
    }
    for (const a of sim.auras) up[a.name] = (up[a.name] || 0) + a.uptime / cfg.fightLen;
    rageWasted += sim.rageWasted; rageGained += sim.rageGained;
  }
  const mean = sum / iterations, variance = Math.max(0, sumSq / iterations - mean * mean);
  const stdev = Math.sqrt(variance), sem = stdev / Math.sqrt(iterations);
  const breakdown = {};
  for (const k in by) { const t = by[k]; breakdown[k] = { dps: t.dmg / iterations / cfg.fightLen, hits: t.hits / iterations, crits: t.crits / iterations, misses: t.misses / iterations, dodges: t.dodges / iterations, glances: t.glances / iterations, casts: t.casts / iterations }; }
  for (const k in up) up[k] /= iterations;
  return { mean, stdev, sem, iterations, breakdown, uptimes: up, rageWastedPerFight: rageWasted / iterations, rageGainedPerFight: rageGained / iterations };
}
