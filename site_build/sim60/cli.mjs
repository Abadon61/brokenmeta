// node site_build/sim60/cli.mjs [iterations]  -- quick benchmark / sanity run
import { runBatch } from './run.js';
import { furyKit } from './warrior.js';

const iterations = parseInt(process.argv[2] || '2000', 10);
const player = {
  level: 60, resource: 'rage', dualWield: true,
  stats: { ap: 1400, crit: 0.20, hit: 0.06, haste: 1, weaponSkill: 300 },
  weapons: [{ min: 85, max: 160, speed: 2.7 }, { min: 70, max: 130, speed: 2.5, offHand: true }],
};
const cfg = { fightLen: 180, player, target: { armor: 3731, defense: 315, executeFrac: 0.2 }, kitFactory: () => furyKit() };
const t0 = Date.now();
const r = runBatch(cfg, iterations, 1);
const dt = (Date.now() - t0) / 1000;
console.log(`${iterations} fights of ${cfg.fightLen}s in ${dt.toFixed(2)}s -> ${(iterations / dt).toFixed(0)} fights/s`);
console.log(`DPS ${r.mean.toFixed(1)} +/- ${r.sem.toFixed(2)} (sd ${r.stdev.toFixed(1)}), rage wasted/fight ${r.rageWastedPerFight.toFixed(0)}`);
for (const [k, v] of Object.entries(r.breakdown).sort((a, b) => b[1].dps - a[1].dps)) console.log(k.padEnd(28), v.dps.toFixed(1).padStart(7), 'casts', v.casts.toFixed(1), 'crit', v.crits.toFixed(1), 'miss', v.misses.toFixed(1), 'dodge', v.dodges.toFixed(1));
console.log('uptimes', Object.fromEntries(Object.entries(r.uptimes).map(([k, v]) => [k, +v.toFixed(2)])));

if (process.argv[3] === 'weights') {
  const { statWeights } = await import('./weights.js');
  const t1 = Date.now();
  const w = statWeights(cfg, iterations, 1);
  console.log(`stat weights (${iterations} fights per point, 8 runs) in ${((Date.now() - t1) / 1000).toFixed(1)}s`);
  console.log('1% crit =', w.normalizedToAp.crit.toFixed(1), 'AP | 1% hit =', w.normalizedToAp.hit.toFixed(1), 'AP | 1% haste =', w.normalizedToAp.haste.toFixed(1), 'AP');
}
