// Stat weights by central finite difference with common random numbers (same seeds on both sides),
// expressed in DPS per point of each stat, then normalised to Attack Power.
import { runBatch } from './run.js';

function withStats(cfg, delta) {
  const stats = Object.assign({}, cfg.player.stats);
  for (const k in delta) stats[k] = (stats[k] || 0) + delta[k];
  return Object.assign({}, cfg, { player: Object.assign({}, cfg.player, { stats }) });
}

export function statWeights(cfg, iterations = 4000, seedBase = 1) {
  const caster = cfg.player.resource === 'mana';
  const probes = {
    ap: caster ? { sp: 40 } : { ap: 40 },       // main power stat: attack power or spell power
    crit: { crit: 0.01 },      // per 1%
    hit: { hit: 0.01 },        // per 1%
    haste: { haste: 0.01 },    // per 1% (multiplier 1 -> 1.01)
  };
  const out = {};
  for (const k in probes) {
    const d = probes[k];
    const up = {}, down = {};
    for (const s in d) { up[s] = d[s]; down[s] = -d[s]; }
    const hi = runBatch(withStats(cfg, up), iterations, seedBase).mean;
    const lo = runBatch(withStats(cfg, down), iterations, seedBase).mean;
    out[k] = (hi - lo) / 2;
  }
  const apPer = out.ap / 40;                      // DPS per AP (spell power for casters)
  return {
    perPoint: { ap: apPer, crit: out.crit, hit: out.hit, haste: out.haste },
    normalizedToAp: { ap: 1, crit: out.crit / apPer, hit: out.hit / apPer, haste: out.haste / apPer },  // "1% crit = X AP"
  };
}
