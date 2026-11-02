/* Bake the character models of the transmog simulator into a compact file (".tmc.gz") the page loads instead of Wowhead's 30 MB .m2.
 *
 *   node bake_characters.js [chrModelId ...]        (default: all 18 models)
 *
 * Reads the raw files from ../transmog_proto/modelviewer/classicplus/ (the dev server fills that cache from the game-data CDN),
 * parses them with the page's own parser (tm-m2.js) and keeps only what the viewer uses:
 *   vertices (positions / normals / uv / bone indices + weights, quantised), the triangles, the submeshes and batches,
 *   the bones with their rest pose and the weapon-ready poses, the attachment points, the texture slots.
 * Everything else in the M2 (animations of every kind, particles, ribbons, cameras, collision...) is dropped.
 *
 * File layout (little endian): uint32 jsonLength | json (padded to 4) | binary blob; the whole file is gzip-compressed.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
global.window = global;
require('../transmog_proto/tm-m2.js');

const RAW = path.join(__dirname, '..', 'transmog_proto', 'modelviewer', 'classicplus');
const OUT = path.join(__dirname, '..', 'transmog_assets');
const IDS = process.argv.length > 2 ? process.argv.slice(2).map(Number) : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 218, 219];

const ab = (f) => { const b = fs.readFileSync(f); return b.buffer.slice(b.byteOffset, b.byteOffset + b.length); };

function bake(id) {
  const meta = JSON.parse(fs.readFileSync(path.join(RAW, 'meta/character', id + '.json'), 'utf8'));
  const m = TM.parseM2(ab(path.join(RAW, 'm2', meta.Model + '.m2')));
  const sk = TM.parseSkin(ab(path.join(RAW, 'skin', m.skinFileIds[0] + '.skin')));
  const n = m.vertCount;

  // keep only the triangles of submeshes that a batch draws (the rest is never shown)
  const used = new Set(sk.batches.map(b => b.sub));
  const subs = [], tris = [];
  sk.subs.forEach((s, i) => {
    if (!used.has(i)) return;
    subs.push([s.id, tris.length / 3 * 3, s.iCount]);
    for (let k = 0; k < s.iCount; k++) tris.push(sk.tri[s.iStart + k]);
  });
  const subIndex = new Map(); let j = 0; sk.subs.forEach((s, i) => { if (used.has(i)) subIndex.set(i, j++); });

  // quantisation ranges
  const rng = (arr, stride, k) => { let lo = 1e9, hi = -1e9; for (let i = k; i < arr.length; i += stride) { lo = Math.min(lo, arr[i]); hi = Math.max(hi, arr[i]); } return [lo, hi]; };
  const pr = [0, 1, 2].map(k => rng(m.pos, 3, k)), ur = [0, 1].map(k => rng(m.uv, 2, k));
  const q16 = (x, lo, hi) => Math.max(0, Math.min(65535, Math.round((x - lo) / ((hi - lo) || 1) * 65535)));

  const pos = new Uint16Array(n * 3), uv = new Uint16Array(n * 2), nrm = new Int8Array(n * 4);
  for (let i = 0; i < n; i++) {
    for (let k = 0; k < 3; k++) pos[i * 3 + k] = q16(m.pos[i * 3 + k], pr[k][0], pr[k][1]);
    for (let k = 0; k < 2; k++) uv[i * 2 + k] = q16(m.uv[i * 2 + k], ur[k][0], ur[k][1]);
    for (let k = 0; k < 3; k++) nrm[i * 4 + k] = Math.max(-127, Math.min(127, Math.round(m.nrm[i * 3 + k] * 127)));
  }
  const parts = [pos, uv, nrm, m.bi, m.bw, Uint32Array.from(tris)];
  const offs = []; let o = 0;
  for (const p of parts) { o = (o + 3) & ~3; offs.push([o, p.byteLength]); o += p.byteLength; }
  const blob = Buffer.alloc((o + 3) & ~3);
  parts.forEach((p, i) => Buffer.from(p.buffer, p.byteOffset, p.byteLength).copy(blob, offs[i][0]));

  const rnd = (a) => a && a.map(x => +x.toFixed(5));
  const poseOf = (p) => (p.t || p.r || p.s) ? [rnd(p.t), rnd(p.r), rnd(p.s)] : 0;
  const json = {
    v: 1, chr: id, model: meta.Model, n, pr, ur, tris: tris.length, offs,
    bones: m.bones.map(b => {
      const alt = {}; for (const k in b.alt) { const p = poseOf(b.alt[k]); if (p) alt[k] = p; }
      return [b.keyBone, b.parent, rnd(b.pivot), poseOf(b), Object.keys(alt).length ? alt : 0];
    }),
    textures: m.textures.map(t => [t.type, t.fileId]), materials: m.materials.map(x => x.blend), texLookup: Array.from(m.texLookup),
    attachments: Object.fromEntries(Object.entries(m.attachments).map(([k, a]) => [k, [a.bone, ...rnd(a.pos)]])),
    standSeq: m.standSeq, subs, batches: sk.batches.map(b => [subIndex.get(b.sub), b.texCombo, b.material]),
  };
  const js = Buffer.from(JSON.stringify(json), 'utf8');
  const head = Buffer.alloc(4); head.writeUInt32LE(js.length, 0);
  const pad = Buffer.alloc((4 - (js.length % 4)) % 4);
  const raw = Buffer.concat([head, js, pad, blob]);
  const gz = zlib.gzipSync(raw, { level: 9 });
  fs.mkdirSync(path.join(OUT, 'chars'), { recursive: true });
  fs.writeFileSync(path.join(OUT, 'chars', id + '.tmc.gz'), gz);
  return { id, vertices: n, raw: raw.length, gz: gz.length, src: fs.statSync(path.join(RAW, 'm2', meta.Model + '.m2')).size };
}

let tot = 0, src = 0;
for (const id of IDS) {
  try { const r = bake(id); tot += r.gz; src += r.src; console.log(`model ${id}: ${r.vertices} vertices, ${(r.src / 1e6).toFixed(1)} MB -> ${(r.raw / 1e6).toFixed(2)} MB raw, ${(r.gz / 1e6).toFixed(2)} MB gz`); }
  catch (e) { console.log(`model ${id}: FAILED ${e.message}`); }
}
console.log(`total: ${(src / 1e6).toFixed(0)} MB source -> ${(tot / 1e6).toFixed(1)} MB gz`);
