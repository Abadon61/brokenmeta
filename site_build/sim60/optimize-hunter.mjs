// node optimize-hunter.mjs [marksmanship|beastmastery] -- demo: optimise a synthetic hunter (gear, ranged weapon, melee stat stick)
import { readFileSync } from 'node:fs';
import { ItemPool } from './items.js';
import { optimizeGear } from './optimizer.js';
import { hunterKit } from './hunter.js';
import { SAMPLE_HUNTER } from './samples.js';
import { ranksToBuild, ranksFromNames, PRESETS } from './talents.js';

const spec = ['marksmanship', 'beastmastery'].includes(process.argv[2]) ? process.argv[2] : 'marksmanship';
const here = new URL('.', import.meta.url);
const pool = new ItemPool(JSON.parse(readFileSync(new URL('data/items.json', here))), JSON.parse(readFileSync(new URL('data/proficiency.json', here))));
const data = JSON.parse(readFileSync(new URL('data/spells60.json', here)));
const tal = JSON.parse(readFileSync(new URL('data/talents.json', here))).hunter;
const build = Object.assign(ranksToBuild('hunter', tal, ranksFromNames(tal, PRESETS['hunter_' + spec])), spec === 'marksmanship' ? { pet: 'none' } : {});
const t0 = Date.now();
const res = await optimizeGear({
  pool, character: { ...SAMPLE_HUNTER, gear: [], weapons: [] }, ranged: true, kit: () => hunterKit(build, data), iterations: 300, prefilter: 3, maxPasses: 2,
  onProgress: (p) => process.stdout.write(`\rpass ${p.pass} ${String(p.slot).padEnd(9)} ${p.dps.toFixed(1)} DPS   `),
});
console.log(`\n${spec}: best ${res.dps.toFixed(1)} DPS in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
for (const w of res.weapons) console.log(w.slot.padEnd(9), w.name, JSON.stringify({ dps: w.st.dps, speed: w.st.speed }));
for (const g of res.gear) console.log(g.slot.padEnd(9), g.name);
