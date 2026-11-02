/* Bake the item models (shoulders, helmets, weapons, shields...) into compact files, the same format as the characters.
 *
 *   node bake_models.js <m2ids.json> [skinsOut.json]
 *
 * For every model id of the list: reads m2/<id>.m2 and its first skin profile (skin/<skinId>.skin) from the dev cache and writes
 * ../transmog_assets/models/<id>.tmc.gz. Models whose skin is not downloaded yet are written to skinsOut.json (one id each) so that
 * `node fetch_files.js skin skinsOut.json` can fetch them; run this script again afterwards. */
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib');
global.window = global;
require('../transmog_proto/tm-m2.js');
const RAW = path.join(__dirname, '..', 'transmog_proto', 'modelviewer', 'classicplus');
const OUT = path.join(__dirname, '..', 'transmog_assets', 'models');
const ids = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const ab = (f) => { const b = fs.readFileSync(f); return b.buffer.slice(b.byteOffset, b.byteOffset + b.length); };
fs.mkdirSync(OUT, { recursive: true });

function bakeOne(id) {
  const mp = path.join(RAW, 'm2', id + '.m2');
  if (!fs.existsSync(mp)) return { skip: 'no m2' };
  const m = TM.parseM2(ab(mp));
  const sid = m.skinFileIds[0];
  const sp = path.join(RAW, 'skin', sid + '.skin');
  if (!fs.existsSync(sp)) return { needSkin: sid };
  const sk = TM.parseSkin(ab(sp));
  const n = m.vertCount;
  const used = new Set(sk.batches.map(b => b.sub));
  const subs = [], tris = [], subIndex = new Map();
  sk.subs.forEach((s, i) => { if (!used.has(i)) return; subIndex.set(i, subs.length); subs.push([s.id, tris.length, s.iCount]); for (let k = 0; k < s.iCount; k++) tris.push(sk.tri[s.iStart + k]); });
  const rng = (arr, stride, k) => { let lo = 1e9, hi = -1e9; for (let i = k; i < arr.length; i += stride) { lo = Math.min(lo, arr[i]); hi = Math.max(hi, arr[i]); } return [lo, hi]; };
  const pr = [0, 1, 2].map(k => rng(m.pos, 3, k)), ur = [0, 1].map(k => rng(m.uv, 2, k));
  const q16 = (x, lo, hi) => Math.max(0, Math.min(65535, Math.round((x - lo) / ((hi - lo) || 1) * 65535)));
  const pos = new Uint16Array(n * 3), uv = new Uint16Array(n * 2), nrm = new Int8Array(n * 4);
  for (let i = 0; i < n; i++) {
    for (let k = 0; k < 3; k++) pos[i * 3 + k] = q16(m.pos[i * 3 + k], pr[k][0], pr[k][1]);
    for (let k = 0; k < 2; k++) uv[i * 2 + k] = q16(m.uv[i * 2 + k], ur[k][0], ur[k][1]);
    for (let k = 0; k < 3; k++) nrm[i * 4 + k] = Math.max(-127, Math.min(127, Math.round(m.nrm[i * 3 + k] * 127)));
  }
  // items are rigid: no bone data is kept (the viewer attaches the whole model to a bone of the character)
  const parts = [pos, uv, nrm, new Uint8Array(0), new Uint8Array(0), Uint32Array.from(tris)];
  const offs = []; let o = 0;
  for (const p of parts) { o = (o + 3) & ~3; offs.push([o, p.byteLength]); o += p.byteLength; }
  const blob = Buffer.alloc((o + 3) & ~3);
  parts.forEach((p, i) => Buffer.from(p.buffer, p.byteOffset, p.byteLength).copy(blob, offs[i][0]));
  const json = {
    v: 1, model: id, n, pr, ur, tris: tris.length, offs, bones: [],
    textures: m.textures.map(t => [t.type, t.fileId]), materials: m.materials.map(x => x.blend), texLookup: Array.from(m.texLookup), attachments: {}, standSeq: 0,
    subs, batches: sk.batches.map(b => [subIndex.get(b.sub), b.texCombo, b.material]),
  };
  const js = Buffer.from(JSON.stringify(json), 'utf8'), head = Buffer.alloc(4); head.writeUInt32LE(js.length, 0);
  const raw = Buffer.concat([head, js, Buffer.alloc((4 - (js.length % 4)) % 4), blob]);
  const gz = zlib.gzipSync(raw, { level: 9 });
  fs.writeFileSync(path.join(OUT, id + '.tmc.gz'), gz);
  return { gz: gz.length, src: fs.statSync(mp).size + fs.statSync(sp).size };
}

let done = 0, gz = 0, src = 0; const needSkin = [], skipped = [];
for (const id of ids) {
  try {
    const r = bakeOne(id);
    if (r.needSkin) needSkin.push(r.needSkin); else if (r.skip) skipped.push(id); else { done++; gz += r.gz; src += r.src; }
  } catch (e) { skipped.push(id); console.log('model', id, 'failed:', e.message); }
}
if (process.argv[3]) fs.writeFileSync(process.argv[3], JSON.stringify([...new Set(needSkin)]));
console.log(`${done} models baked: ${(src / 1e6).toFixed(1)} MB -> ${(gz / 1e6).toFixed(1)} MB gz; ${needSkin.length} need a skin file; ${skipped.length} skipped`);
