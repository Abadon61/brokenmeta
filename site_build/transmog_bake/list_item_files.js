/* From the item catalogue + the downloaded item metadata: every model and texture file the page needs for items.
 *   node list_item_files.js <outDir>      writes m2.json, textures.json, summary to outDir
 * Helmets exist once per race and sex: only the races of our 18 character models are kept (1-8, Skyborne 95/96, and race 0 = any). */
const fs = require('fs'), path = require('path');
const RAW = path.join(__dirname, '..', 'transmog_proto', 'modelviewer', 'classicplus');
const cat = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', 'data', 'wow_transmog_catalog.json'), 'utf8'));
const RACES = new Set([0, 1, 2, 3, 4, 5, 6, 7, 8, 95, 96]);
const m2 = new Set(), tex = new Set(); let missingMeta = 0, items = 0;
const seen = new Set();
for (const r of cat.items) {
  const inv = r[5], disp = r[8];
  const weapon = [13, 17, 21, 22, 15, 26, 25, 14, 23].includes(inv);
  const rel = weapon ? `meta/item/${disp}.json` : `meta/armor/${inv}/${disp}.json`;
  if (seen.has(rel)) continue; seen.add(rel);
  let j; try { j = JSON.parse(fs.readFileSync(path.join(RAW, rel), 'utf8')); } catch (e) { missingMeta++; continue; }
  items++;
  for (const k in (j.Textures || {})) if (j.Textures[k]) tex.add(j.Textures[k]);
  for (const k in (j.Textures2 || {})) if (j.Textures2[k]) tex.add(j.Textures2[k]);
  for (const k in (j.TextureFiles || {})) for (const f of j.TextureFiles[k]) tex.add(f.FileDataId);
  for (const k in (j.ModelFiles || {})) for (const f of j.ModelFiles[k]) if (RACES.has(f.Race)) m2.add(f.FileDataId);
}
const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(path.join(out, 'm2.json'), JSON.stringify([...m2].sort((a, b) => a - b)));
fs.writeFileSync(path.join(out, 'textures.json'), JSON.stringify([...tex].sort((a, b) => a - b)));
console.log({ appearances: items, missingMeta, models: m2.size, textures: tex.size });
