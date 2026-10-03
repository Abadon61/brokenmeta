// node optimize-mage.mjs [fire|frost|arcane] -- demo: optimise a synthetic mage (gear + staff) from the exported item pool
import { readFileSync } from 'node:fs';
import { ItemPool } from './items.js';
import { optimizeGear } from './optimizer.js';
import { mageKit } from './mage.js';
import { statWeights } from './weights.js';
import { buildCharacter } from './character.js';
import { SAMPLE_MAGE } from './samples.js';
import { ranksToBuild, ranksFromNames, PRESETS } from './talents.js';

const rot = ['fire', 'frost', 'arcane'].includes(process.argv[2]) ? process.argv[2] : 'fire';
const here = new URL('.', import.meta.url);
const pool = new ItemPool(JSON.parse(readFileSync(new URL('data/items.json', here))), JSON.parse(readFileSync(new URL('data/proficiency.json', here))));
const data = JSON.parse(readFileSync(new URL('data/spells60.json', here)));
const tal = JSON.parse(readFileSync(new URL('data/talents.json', here))).mage;
const build = Object.assign(ranksToBuild('mage', tal, ranksFromNames(tal, PRESETS['mage_' + rot])), { rotation: rot });
const kit = () => mageKit(build, data);
const t0 = Date.now();
const res = await optimizeGear({
  pool, character: { ...SAMPLE_MAGE, gear: [], weapons: [] }, caster: true, kit, iterations: 400, prefilter: 4, maxPasses: 2,
  onProgress: (p) => process.stdout.write(`\rpass ${p.pass} ${String(p.slot).padEnd(9)} ${p.dps.toFixed(1)} DPS   `),
});
console.log(`\n${rot}: best ${res.dps.toFixed(1)} DPS in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
for (const w of res.weapons) console.log(w.slot.padEnd(9), w.name);
for (const g of res.gear) console.log(g.slot.padEnd(9), g.name, JSON.stringify(g.st));
const ch = buildCharacter({ ...SAMPLE_MAGE, gear: res.gear, weapons: [] });
const sw = statWeights({ fightLen: 180, player: ch.player, target: ch.target, kitFactory: kit }, 2000, 1);
console.log('weights (SP-equivalent):', JSON.stringify(sw.normalizedToAp));
