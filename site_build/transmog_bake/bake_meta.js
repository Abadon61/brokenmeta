/* Copy the data files the page needs next to the baked assets (transmog_assets/):
 *   meta/character/<id>.json, meta/charactercustomization/<id>.json   (the 18 models)
 *   catalog.json   (the item catalogue, data/wow_transmog_catalog.json)
 *   proficiency.json (armor / weapon types per class, data/wow_items/proficiency.json)
 * Customization files keep only the fields the viewer reads. */
const fs = require('fs'), path = require('path');
const RAW = path.join(__dirname, '..', 'transmog_proto', 'modelviewer', 'classicplus', 'meta');
const OUT = path.join(__dirname, '..', 'transmog_assets');
const DATA = path.join(__dirname, '..', '..', 'data');
const IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 218, 219];
const FOREVER = 1 | 2 | 4 | 8 | 16 | 64 | 128 | 256 | 1024;
const ok = ch => ch.ReqType !== 2 && ch.ReqType !== 4 && (ch.ClassMask === undefined || ch.ClassMask === -1 || (ch.ClassMask & FOREVER) !== 0);
for (const d of ['meta/character', 'meta/charactercustomization']) fs.mkdirSync(path.join(OUT, d), { recursive: true });
let before = 0, after = 0;
for (const id of IDS) {
  const c = JSON.parse(fs.readFileSync(path.join(RAW, 'character', id + '.json'), 'utf8'));
  fs.writeFileSync(path.join(OUT, 'meta/character', id + '.json'), JSON.stringify({ Model: c.Model, Character: c.Character }));
  const raw = fs.readFileSync(path.join(RAW, 'charactercustomization', id + '.json'), 'utf8'); before += raw.length;
  const j = JSON.parse(raw);
  // keep only the choices available in the game, and the fields the viewer uses
  const slim = {
    Options: j.Options.map(o => ({
      Id: o.Id, Name: o.Name, Choices: o.Choices.filter(ok).map(ch => ({
        Id: ch.Id, Name: ch.Name, ReqType: ch.ReqType, ClassMask: ch.ClassMask,
        Elements: ch.Elements.filter(e => e.Geoset || e.Material).map(e => ({ VariationChoiceID: e.VariationChoiceID, VariationIndex: e.VariationIndex, Geoset: e.Geoset ? { GeosetType: e.Geoset.GeosetType, GeosetID: e.Geoset.GeosetID } : null, Material: e.Material ? { TextureTarget: e.Material.TextureTarget, MaterialResourcesID: e.Material.MaterialResourcesID } : null })),
      })),
    })).filter(o => o.Choices.length),
    TextureFiles: j.TextureFiles, Materials: j.Materials, TextureLayers: j.TextureLayers, TextureSections: j.TextureSections,
  };
  const txt = JSON.stringify(slim); after += txt.length;
  fs.writeFileSync(path.join(OUT, 'meta/charactercustomization', id + '.json'), txt);
}
fs.copyFileSync(path.join(DATA, 'wow_transmog_catalog.json'), path.join(OUT, 'catalog.json'));
fs.copyFileSync(path.join(DATA, 'wow_items', 'proficiency.json'), path.join(OUT, 'proficiency.json'));
console.log(`customization: ${(before / 1e6).toFixed(1)} MB -> ${(after / 1e6).toFixed(1)} MB; catalog and proficiency copied`);
