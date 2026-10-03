// node check_presets.mjs -- validates the preset talent builds against the tree rules
import { readFileSync } from 'node:fs';
import { validateRanks, ranksFromNames, PRESETS } from './talents.js';
const all = JSON.parse(readFileSync(new URL('data/talents.json', import.meta.url)));
for (const [k, p] of Object.entries(PRESETS)) {
  const data = all[k.split('_')[0]];
  const r = validateRanks(data, ranksFromNames(data, p));
  console.log(k, r.ok, 'total', r.total, 'per tree', r.bySpec.join('/'), r.errors.join(' ; '));
}
