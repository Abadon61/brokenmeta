/* List every texture a character customization can use (skin, face, hair, eyes, markings...): only the choices available in the game
 * (same filter as the page: no unlockables, no class-locked ones). Writes the ids to the file given as argument. */
const fs = require('fs'), path = require('path');
const RAW = path.join(__dirname, '..', 'transmog_proto', 'modelviewer', 'classicplus', 'meta');
const IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 218, 219];
const FOREVER = 1 | 2 | 4 | 8 | 16 | 64 | 128 | 256 | 1024;
const ok = ch => ch.ReqType !== 2 && ch.ReqType !== 4 && (ch.ClassMask === undefined || ch.ClassMask === -1 || (ch.ClassMask & FOREVER) !== 0);
const all = new Set();
for (const id of IDS) {
  const j = JSON.parse(fs.readFileSync(path.join(RAW, 'charactercustomization', id + '.json')));
  for (const o of j.Options) for (const ch of o.Choices) { if (!ok(ch)) continue; for (const e of ch.Elements) if (e.Material) (j.TextureFiles[e.Material.MaterialResourcesID] || []).forEach(x => all.add(x.FileDataId)); }
}
fs.writeFileSync(process.argv[2], JSON.stringify([...all].sort((a, b) => a - b)));
console.log(all.size, 'textures');
