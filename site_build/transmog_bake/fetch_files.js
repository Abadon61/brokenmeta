/* Download game-data files into the dev cache (../transmog_proto/modelviewer/classicplus/), politely and resumably.
 *
 *   node fetch_files.js <kind> <idsFile.json> [pauseMs]
 *     kind = textures (.webp) | m2 | skin | paths (the list holds relative paths such as "meta/armor/5/34698.json") | any path prefix
 *   examples:  node fetch_files.js textures ids.json 120      -> textures/<id>.webp
 *              node fetch_files.js "meta/item" ids.json 120   -> meta/item/<id>.json
 *
 * Files already present are skipped. The CDN accepts plain requests (no Origin header); it refuses browsers from other sites. */
'use strict';
const fs = require('fs'), path = require('path');
const RAW = path.join(__dirname, '..', 'transmog_proto', 'modelviewer', 'classicplus');
const CDN = 'https://wow.zamimg.com/modelviewer/classicplus/';
const [kind, listFile, pauseArg] = process.argv.slice(2);
const pause = +(pauseArg || 120);
const ext = kind === 'paths' ? '' : kind === 'textures' ? 'webp' : kind === 'm2' ? 'm2' : kind === 'skin' ? 'skin' : 'json';
const ids = JSON.parse(fs.readFileSync(listFile, 'utf8'));
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  let got = 0, have = 0, miss = 0, bytes = 0, blocked = 0;
  for (let i = 0; i < ids.length; i++) {
    const rel = kind === 'paths' ? ids[i] : `${kind}/${ids[i]}.${ext}`, f = path.join(RAW, rel);
    if (fs.existsSync(f)) { have++; continue; }
    try {
      const r = await fetch(CDN + rel, { headers: { 'User-Agent': 'brokenmeta.gg transmog asset baker' } });
      if (r.status === 200) { const b = Buffer.from(await r.arrayBuffer()); fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, b); got++; bytes += b.length; blocked = 0; }
      else if (r.status === 403 || r.status === 429) { blocked++; if (blocked >= 10) { console.log(`blocked (HTTP ${r.status}) after ${got} files: stopping, run again later`); break; } await sleep(2000); i--; continue; }
      else { miss++; }
    } catch (e) { await sleep(1500); i--; continue; }
    if ((i + 1) % 200 === 0) console.log(`  ${i + 1}/${ids.length}  new ${got}  (${(bytes / 1e6).toFixed(1)} MB)`);
    await sleep(pause);
  }
  console.log(`${kind}: ${got} downloaded (${(bytes / 1e6).toFixed(1)} MB), ${have} already there, ${miss} not found`);
})();
