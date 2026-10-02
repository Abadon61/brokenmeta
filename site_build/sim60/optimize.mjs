// node optimize.mjs  -- demo: optimise a synthetic Fury Warrior from the exported item pool
import { readFileSync } from 'node:fs';
import { ItemPool } from './items.js';
import { optimizeGear } from './optimizer.js';
import { furyKit } from './warrior.js';
import { SAMPLE_FURY } from './samples.js';

const here = new URL('.', import.meta.url);
const pool = new ItemPool(JSON.parse(readFileSync(new URL('data/items.json', here))), JSON.parse(readFileSync(new URL('data/proficiency.json', here))));
console.log('pool', pool.items.length, 'items; head candidates for a warrior:', pool.forSlot('head', 'warrior').length);
const t0 = Date.now();
const res = optimizeGear({ pool, character: { ...SAMPLE_FURY, gear: [] }, kit: () => furyKit(), iterations: 400, prefilter: 4, maxPasses: 2,
  onProgress: (p) => process.stdout.write(`\rpass ${p.pass} ${p.slot.padEnd(9)} ${p.dps.toFixed(1)} DPS   `) });
console.log(`\nbest ${res.dps.toFixed(1)} DPS in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
for (const g of res.gear) console.log(g.slot.padEnd(9), g.name);
