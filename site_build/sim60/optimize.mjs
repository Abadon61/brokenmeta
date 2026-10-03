// node optimize.mjs [fury|arms] -- demo: optimise a synthetic warrior (gear AND weapons) from the exported item pool
import { readFileSync } from 'node:fs';
import { ItemPool, toWeapon } from './items.js';
import { optimizeGear } from './optimizer.js';
import { furyKit, armsKit } from './warrior.js';
import { SAMPLE_FURY } from './samples.js';

const spec = process.argv[2] === 'arms' ? 'arms' : 'fury';
const here = new URL('.', import.meta.url);
const pool = new ItemPool(JSON.parse(readFileSync(new URL('data/items.json', here))), JSON.parse(readFileSync(new URL('data/proficiency.json', here))));
const data = JSON.parse(readFileSync(new URL('data/spells60.json', here)));
const t0 = Date.now();
const res = await optimizeGear({
  pool, character: { ...SAMPLE_FURY, gear: [], weapons: [] }, weaponMode: spec === 'arms' ? '2h' : 'dw',
  kit: () => (spec === 'arms' ? armsKit({}, data) : furyKit({}, data)), iterations: 400, prefilter: 4, maxPasses: 2,
  onProgress: (p) => process.stdout.write(`\rpass ${p.pass} ${String(p.slot).padEnd(9)} ${p.dps.toFixed(1)} DPS   `),
});
console.log(`\n${spec}: best ${res.dps.toFixed(1)} DPS in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
for (const w of res.weapons) console.log(w.slot.padEnd(9), w.name, JSON.stringify({ dps: w.st.dps, speed: w.st.speed }));
for (const g of res.gear) console.log(g.slot.padEnd(9), g.name);
