// node cli.mjs [iterations] [fury|arms] [weights]  -- quick benchmark / sanity run
import { readFileSync } from 'node:fs';
import { runBatch } from './run.js';
import { furyKit, armsKit } from './warrior.js';
import { buildCharacter } from './character.js';
import { SAMPLE_FURY } from './samples.js';

const iterations = parseInt(process.argv[2] || '2000', 10);
const spec = process.argv[3] === 'arms' ? 'arms' : 'fury';
const data = JSON.parse(readFileSync(new URL('data/spells60.json', import.meta.url)));
const sample = spec === 'arms'
  ? { ...SAMPLE_FURY, weapons: [{ min: 210, max: 330, speed: 3.5, type: 'two-handed sword', twoHand: true }] }
  : SAMPLE_FURY;
const ch = buildCharacter(sample);
const cfg = { fightLen: 180, player: ch.player, target: ch.target, kitFactory: () => (spec === 'arms' ? armsKit({}, data) : furyKit({}, data)) };
console.log(spec, 'character:', JSON.stringify({ ap: Math.round(ch.summary.ap), crit: +(ch.summary.crit * 100).toFixed(1), hit: +(ch.summary.hit * 100).toFixed(1), skill: ch.summary.weaponSkill, bossArmor: ch.summary.armor }));
const t0 = Date.now();
const r = runBatch(cfg, iterations, 1);
const dt = (Date.now() - t0) / 1000;
console.log(`${iterations} fights of ${cfg.fightLen}s in ${dt.toFixed(2)}s -> ${(iterations / dt).toFixed(0)} fights/s`);
console.log(`DPS ${r.mean.toFixed(1)} +/- ${r.sem.toFixed(2)} (sd ${r.stdev.toFixed(1)}), rage wasted/fight ${r.rageWastedPerFight.toFixed(0)}`);
for (const [k, v] of Object.entries(r.breakdown).sort((a, b) => b[1].dps - a[1].dps)) console.log(k.padEnd(28), v.dps.toFixed(1).padStart(7), 'casts', v.casts.toFixed(1), 'crit', v.crits.toFixed(1), 'miss', v.misses.toFixed(1), 'dodge', v.dodges.toFixed(1));
console.log('uptimes', Object.fromEntries(Object.entries(r.uptimes).map(([k, v]) => [k, +v.toFixed(2)])));

if (process.argv[4] === 'weights') {
  const { statWeights } = await import('./weights.js');
  const t1 = Date.now();
  const w = statWeights(cfg, iterations, 1);
  console.log(`stat weights (${iterations} fights per point, 8 runs) in ${((Date.now() - t1) / 1000).toFixed(1)}s`);
  console.log('1% crit =', w.normalizedToAp.crit.toFixed(1), 'AP | 1% hit =', w.normalizedToAp.hit.toFixed(1), 'AP | 1% haste =', w.normalizedToAp.haste.toFixed(1), 'AP');
}
