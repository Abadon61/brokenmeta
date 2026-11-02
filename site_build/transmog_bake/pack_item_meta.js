/* Pack the item appearance metadata by slot: one small JSON per armor slot (items/armor-<inventory type>.json) and one for all held items
 * (items/weapon.json), each {displayId: slimMeta}. The page loads a pack the first time a slot is used.
 * Slim = only what the viewer reads: textures, component textures (+ their files), model files of our 18 character models, geoset groups,
 * and the helmet "hide" lists of our races. Same field names as the raw metadata, so the engine reads both. */
const fs = require('fs'), path = require('path');
const RAW = path.join(__dirname, '..', 'transmog_proto', 'modelviewer', 'classicplus');
const OUT = path.join(__dirname, '..', 'transmog_assets', 'items');
const cat = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', 'data', 'wow_transmog_catalog.json'), 'utf8'));
const RACES = new Set([1, 2, 3, 4, 5, 6, 7, 8, 95, 96]);
const WEAPON_INV = new Set([13, 17, 21, 22, 15, 26, 25, 14, 23]);
fs.mkdirSync(OUT, { recursive: true });
const packs = {};
let kept = 0;
for (const r of cat.items) {
  const inv = r[5], disp = r[8], weapon = WEAPON_INV.has(inv);
  const key = weapon ? 'weapon' : 'armor-' + inv;
  packs[key] = packs[key] || {};
  if (packs[key][disp]) continue;
  const rel = weapon ? `meta/item/${disp}.json` : `meta/armor/${inv}/${disp}.json`;
  let j; try { j = JSON.parse(fs.readFileSync(path.join(RAW, rel), 'utf8')); } catch (e) { continue; }
  const s = {};
  if (j.Textures) s.Textures = j.Textures;
  if (j.Textures2) s.Textures2 = j.Textures2;
  if (j.ComponentTextures) {
    s.ComponentTextures = j.ComponentTextures; s.TextureFiles = {};
    for (const k of Object.values(j.ComponentTextures)) if (j.TextureFiles && j.TextureFiles[k]) s.TextureFiles[k] = j.TextureFiles[k].map(f => ({ FileDataId: f.FileDataId, Gender: f.Gender }));
  }
  if (j.ComponentModels) {
    s.ComponentModels = j.ComponentModels; s.ModelFiles = {};
    for (const c of Object.values(j.ComponentModels)) if (j.ModelFiles && j.ModelFiles[c]) s.ModelFiles[c] = j.ModelFiles[c].filter(f => f.Race === 0 || RACES.has(f.Race)).map(f => ({ FileDataId: f.FileDataId, Gender: f.Gender, Race: f.Race, ExtraData: f.ExtraData }));
  }
  const it = j.Item || {};
  const hide = (a) => a && a.filter(h => RACES.has(h.RaceId)).map(h => ({ RaceId: h.RaceId, GeosetGroup: h.GeosetGroup }));
  s.Item = { GeosetGroup: it.GeosetGroup, InventoryType: it.InventoryType, ItemSubClass: it.ItemSubClass };
  if (it.HideGeosetMale) s.Item.HideGeosetMale = hide(it.HideGeosetMale);
  if (it.HideGeosetFemale) s.Item.HideGeosetFemale = hide(it.HideGeosetFemale);
  packs[key][disp] = s; kept++;
}
let tot = 0;
for (const k in packs) { const f = path.join(OUT, k + '.json'); const txt = JSON.stringify(packs[k]); fs.writeFileSync(f, txt); tot += txt.length; console.log(k.padEnd(10), Object.keys(packs[k]).length, 'appearances', (txt.length / 1e3).toFixed(0), 'KB'); }
console.log(kept, 'appearances,', (tot / 1e6).toFixed(2), 'MB raw');
