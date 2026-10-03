// Batch runner: many fights with seeds base+i (common random numbers across configs).
// Split in two so Web Workers can each run a slice and the main thread merges the raw sums.
import { Sim } from './engine.js';

export function runBatchRaw(cfg, iterations, seedBase = 1) {
  const acc = { n: 0, sum: 0, sumSq: 0, by: Object.create(null), up: Object.create(null), rageWasted: 0, rageGained: 0 };
  for (let i = 0; i < iterations; i++) {
    const sim = new Sim(Object.assign({}, cfg, { seed: seedBase + i, spec: cfg.kitFactory() }));
    sim.run();
    const dps = sim.total / cfg.fightLen;
    acc.n++; acc.sum += dps; acc.sumSq += dps * dps;
    for (const k in sim.dmg) {
      const e = sim.dmg[k], t = acc.by[k] || (acc.by[k] = { dmg: 0, hits: 0, crits: 0, misses: 0, dodges: 0, glances: 0, casts: 0 });
      t.dmg += e.dmg; t.hits += e.hits; t.crits += e.crits; t.misses += e.misses; t.dodges += e.dodges; t.glances += e.glances; t.casts += e.casts;
    }
    for (const a of sim.auras) acc.up[a.name] = (acc.up[a.name] || 0) + a.uptime / cfg.fightLen;
    acc.rageWasted += sim.rageWasted; acc.rageGained += sim.rageGained;
  }
  return acc;
}

export function mergeRaw(parts) {
  const out = { n: 0, sum: 0, sumSq: 0, by: Object.create(null), up: Object.create(null), rageWasted: 0, rageGained: 0 };
  for (const p of parts) {
    out.n += p.n; out.sum += p.sum; out.sumSq += p.sumSq; out.rageWasted += p.rageWasted; out.rageGained += p.rageGained;
    for (const k in p.by) { const t = out.by[k] || (out.by[k] = { dmg: 0, hits: 0, crits: 0, misses: 0, dodges: 0, glances: 0, casts: 0 }); for (const f in p.by[k]) t[f] += p.by[k][f]; }
    for (const k in p.up) out.up[k] = (out.up[k] || 0) + p.up[k];
  }
  return out;
}

export function finalize(raw, fightLen) {
  const n = raw.n, mean = raw.sum / n, variance = Math.max(0, raw.sumSq / n - mean * mean);
  const stdev = Math.sqrt(variance), sem = stdev / Math.sqrt(n);
  const breakdown = {};
  for (const k in raw.by) { const t = raw.by[k]; breakdown[k] = { dps: t.dmg / n / fightLen, hits: t.hits / n, crits: t.crits / n, misses: t.misses / n, dodges: t.dodges / n, glances: t.glances / n, casts: t.casts / n }; }
  const uptimes = {}; for (const k in raw.up) uptimes[k] = raw.up[k] / n;
  return { mean, stdev, sem, iterations: n, breakdown, uptimes, rageWastedPerFight: raw.rageWasted / n, rageGainedPerFight: raw.rageGained / n };
}

export function runBatch(cfg, iterations, seedBase = 1) {
  return finalize(runBatchRaw(cfg, iterations, seedBase), cfg.fightLen);
}
