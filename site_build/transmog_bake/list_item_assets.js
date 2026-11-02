/* From the item catalogue: every (slot, appearance) the page can show -> the metadata files to fetch.
 *   node list_item_assets.js <out.json>     writes ["meta/armor/5/34698.json", "meta/item/8474.json", ...] */
const fs = require('fs'), path = require('path');
const cat = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', 'data', 'wow_transmog_catalog.json'), 'utf8'));
const paths = new Set();
for (const r of cat.items) {
  const inv = r[5], disp = r[8], cls = r[6];
  const weapon = [13, 17, 21, 22, 15, 26, 25, 14, 23].includes(inv);
  paths.add(weapon ? `meta/item/${disp}.json` : `meta/armor/${inv}/${disp}.json`);
}
fs.writeFileSync(process.argv[2], JSON.stringify([...paths]));
console.log(paths.size, 'metadata files');
