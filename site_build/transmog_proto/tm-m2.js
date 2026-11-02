/* BrokenMeta transmog viewer: M2 / SKIN parser (own code, format documented on wowdev.wiki).
   Only what a static dress-up needs: vertices, submeshes, texture units, texture slots, attachments. */
(function (G) {
  'use strict';

  function chunks(buf) {
    const dv = new DataView(buf), out = {};
    let o = 0;
    while (o + 8 <= buf.byteLength) {
      const id = String.fromCharCode(dv.getUint8(o), dv.getUint8(o + 1), dv.getUint8(o + 2), dv.getUint8(o + 3));
      const sz = dv.getUint32(o + 4, true);
      out[id] = { ofs: o + 8, size: sz };
      o += 8 + sz;
    }
    return out;
  }

  // buf: whole .m2 file (chunked "MD21" container, version >= 264)
  function parseM2(buf) {
    const ch = chunks(buf);
    if (!ch.MD21) throw new Error('not a chunked M2');
    const base = ch.MD21.ofs, dv = new DataView(buf);
    const u32 = (o) => dv.getUint32(base + o, true);
    const arr = (o) => ({ n: u32(o), ofs: u32(o + 4) });

    const m = { version: u32(4) };
    const vtx = arr(0x3c);       // layout: name@8 flags@0x10 loops@0x14 seq@0x1c seqLookup@0x24 bones@0x2c keyBone@0x34 verts@0x3c
    const nV = vtx.n;
    m.vertCount = nV;
    m.pos = new Float32Array(nV * 3);
    m.nrm = new Float32Array(nV * 3);
    m.uv = new Float32Array(nV * 2);
    m.bi = new Uint8Array(nV * 4);
    m.bw = new Uint8Array(nV * 4);
    for (let i = 0; i < nV; i++) {
      const p = base + vtx.ofs + i * 48;
      m.pos[i * 3] = dv.getFloat32(p, true); m.pos[i * 3 + 1] = dv.getFloat32(p + 4, true); m.pos[i * 3 + 2] = dv.getFloat32(p + 8, true);
      for (let k = 0; k < 4; k++) { m.bw[i * 4 + k] = dv.getUint8(p + 12 + k); m.bi[i * 4 + k] = dv.getUint8(p + 16 + k); }
      m.nrm[i * 3] = dv.getFloat32(p + 20, true); m.nrm[i * 3 + 1] = dv.getFloat32(p + 24, true); m.nrm[i * 3 + 2] = dv.getFloat32(p + 28, true);
      m.uv[i * 2] = dv.getFloat32(p + 32, true); m.uv[i * 2 + 1] = dv.getFloat32(p + 36, true);
    }

    // sequences by animation id (variation 0): its index differs per model (night elf males list Walk first). Stand = rest pose,
    // 26 / 27 = Ready1H / Ready2H: the hand holds a weapon (fingers closed), used for the hand that carries one
    const seqs = arr(0x1c);
    const seqIndex = (animId) => { for (let i = 0; i < seqs.n; i++) { const p = base + seqs.ofs + i * 64; if (dv.getUint16(p, true) === animId && dv.getUint16(p + 2, true) === 0) return i; } return -1; };
    const stand = Math.max(0, seqIndex(0));
    m.standSeq = stand;
    const ALT = [26, 27, 25, 28];      // Ready1H, Ready2H, ReadyUnarmed, Ready2HL: the closed-fist candidates (some models only animate one hand in some of them)
    const altIdx = {}; for (const id of ALT) altIdx[id] = seqIndex(id);

    // bones (pivot = bind position, parent, key bone id); size 88 in this version
    const bones = arr(0x2c);
    m.bones = [];
    const BS = (m.version >= 264) ? 88 : 0;
    for (let i = 0; i < bones.n; i++) {
      const p = base + bones.ofs + i * BS;
      // first key of a sequence for each track (translation / rotation / scale) = that animation's pose
      const key0 = (t, seq, rd) => {
        if (seq < 0) return null;
        const interp = dv.getUint16(p + t, true), cnt = dv.getUint32(p + t + 12, true), vo = dv.getUint32(p + t + 16, true);
        if (!interp && !cnt) return null;
        if (cnt < 1 || seq >= cnt) return null;
        const sn = dv.getUint32(base + vo + seq * 8, true), so = dv.getUint32(base + vo + seq * 8 + 4, true);
        if (!sn || !so || base + so + 4 > buf.byteLength) return null;
        return rd(base + so);
      };
      const pose = (seq) => ({
        t: key0(16, seq, (q) => [dv.getFloat32(q, true), dv.getFloat32(q + 4, true), dv.getFloat32(q + 8, true)]),
        r: key0(36, seq, (q) => { if (!dv.getInt16(q, true) && !dv.getInt16(q + 2, true) && !dv.getInt16(q + 4, true) && !dv.getInt16(q + 6, true)) return null;   // zeroed = no data in this file
          const c = (k) => { const v = dv.getInt16(q + k * 2, true); return (v < 0 ? v + 32768 : v - 32768) / 32767; }; return [c(0), c(1), c(2), c(3)]; }),
        s: key0(56, seq, (q) => { const s = [dv.getFloat32(q, true), dv.getFloat32(q + 4, true), dv.getFloat32(q + 8, true)]; return s.every(x => Math.abs(x) < 1e-6) ? null : s; }),
      });
      const alt = {}; for (const id of ALT) alt[id] = pose(altIdx[id]);
      m.bones.push(Object.assign({
        keyBone: dv.getInt32(p, true), flags: dv.getUint32(p + 4, true), parent: dv.getInt16(p + 8, true),
        pivot: [dv.getFloat32(p + 76, true), dv.getFloat32(p + 80, true), dv.getFloat32(p + 84, true)], alt,
      }, pose(stand)));
    }

    // texture slots: type, flags, filename(array); file ids come from the TXID chunk
    const tex = arr(0x50);
    m.textures = [];
    let txid = null;
    if (ch.TXID) { txid = new Uint32Array(buf.slice(ch.TXID.ofs, ch.TXID.ofs + ch.TXID.size)); }
    for (let i = 0; i < tex.n; i++) {
      const p = base + tex.ofs + i * 16;
      m.textures.push({ type: dv.getUint32(p, true), flags: dv.getUint32(p + 4, true), fileId: txid ? txid[i] : 0 });
    }
    // render flags (materials): flags u16, blend u16
    const mat = arr(0x70);
    m.materials = [];
    for (let i = 0; i < mat.n; i++) { const p = base + mat.ofs + i * 4; m.materials.push({ flags: dv.getUint16(p, true), blend: dv.getUint16(p + 2, true) }); }
    const rd16 = (a) => { const r = new Uint16Array(a.n); for (let i = 0; i < a.n; i++) r[i] = dv.getUint16(base + a.ofs + i * 2, true); return r; };
    m.texLookup = rd16(arr(0x80));

    // attachment points (id, bone, position in model space): shoulders 5/6, helmet 11, hands 1/2, back 0/10...
    const att = arr(0xf0);
    m.attachments = {};
    for (let i = 0; i < att.n; i++) {
      const p = base + att.ofs + i * 40, id = dv.getUint32(p, true);
      m.attachments[id] = { bone: dv.getUint16(p + 4, true), pos: [dv.getFloat32(p + 8, true), dv.getFloat32(p + 12, true), dv.getFloat32(p + 16, true)] };
    }

    m.skinFileIds = [];
    if (ch.SFID) { const n = u32(0x44); for (let i = 0; i < n; i++) m.skinFileIds.push(dv.getUint32(ch.SFID.ofs + i * 4, true)); }
    return m;
  }

  // buf: .skin file ("SKIN"); returns triangles (as indices into the M2 vertex array), submeshes and batches
  function parseSkin(buf) {
    const dv = new DataView(buf);
    if (dv.getUint32(0, true) !== 0x4e494b53) throw new Error('not a SKIN');
    const A = (o) => ({ n: dv.getUint32(o, true), ofs: dv.getUint32(o + 4, true) });
    const vl = A(4), ix = A(12), sm = A(28), bt = A(36);
    const lookup = new Uint16Array(vl.n);
    for (let i = 0; i < vl.n; i++) lookup[i] = dv.getUint16(vl.ofs + i * 2, true);
    const tri = new Uint32Array(ix.n);
    for (let i = 0; i < ix.n; i++) tri[i] = lookup[dv.getUint16(ix.ofs + i * 2, true)];
    const subs = [];
    for (let i = 0; i < sm.n; i++) {
      const p = sm.ofs + i * 48;
      subs.push({ id: dv.getUint16(p, true), vStart: dv.getUint16(p + 4, true), vCount: dv.getUint16(p + 6, true),
        iStart: dv.getUint16(p + 8, true) | (dv.getUint16(p + 2, true) << 16), iCount: dv.getUint16(p + 10, true) });
    }
    const batches = [];
    for (let i = 0; i < bt.n; i++) {
      const p = bt.ofs + i * 24;
      batches.push({ flags: dv.getUint8(p), prio: dv.getInt8(p + 1), shader: dv.getUint16(p + 2, true), sub: dv.getUint16(p + 4, true),
        color: dv.getUint16(p + 8, true), material: dv.getUint16(p + 10, true), layer: dv.getUint16(p + 12, true),
        texCount: dv.getUint16(p + 14, true), texCombo: dv.getUint16(p + 16, true) });
    }
    return { tri, subs, batches };
  }


  // ---- compact character files (".tmc.gz", made by site_build/transmog_bake/bake_characters.js) ----
  async function loadSlim(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(url + ' ' + res.status);
    const buf = await new Response(res.body.pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
    return parseSlim(buf);
  }
  function parseSlim(buf) {
    const dv = new DataView(buf), jl = dv.getUint32(0, true);
    const J = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 4, jl)));
    const base = 4 + ((jl + 3) & ~3), n = J.n;
    const at = (i) => J.offs[i][0] + base;
    const u16 = (i, len) => new Uint16Array(buf, at(i), len);
    const dq = (q, lo, hi) => lo + q / 65535 * (hi - lo);
    const m = { version: 'slim', vertCount: n, pos: new Float32Array(n * 3), nrm: new Float32Array(n * 3), uv: new Float32Array(n * 2) };
    const P = u16(0, n * 3), U = u16(1, n * 2), N = new Int8Array(buf, at(2), n * 4);
    for (let i = 0; i < n; i++) {
      for (let k = 0; k < 3; k++) { m.pos[i * 3 + k] = dq(P[i * 3 + k], J.pr[k][0], J.pr[k][1]); m.nrm[i * 3 + k] = N[i * 4 + k] / 127; }
      for (let k = 0; k < 2; k++) m.uv[i * 2 + k] = dq(U[i * 2 + k], J.ur[k][0], J.ur[k][1]);
    }
    m.bi = new Uint8Array(buf, at(3), n * 4); m.bw = new Uint8Array(buf, at(4), n * 4);
    const pose = (p) => p ? { t: p[0], r: p[1], s: p[2] } : { t: null, r: null, s: null };
    m.bones = J.bones.map(b => { const alt = {}; for (const k in (b[4] || {})) alt[k] = pose(b[4][k]); return Object.assign({ keyBone: b[0], parent: b[1], pivot: b[2], alt }, pose(b[3])); });
    m.textures = J.textures.map(t => ({ type: t[0], flags: 0, fileId: t[1] }));
    m.materials = J.materials.map(b => ({ flags: 0, blend: b }));
    m.texLookup = J.texLookup;
    m.attachments = {}; for (const k in J.attachments) { const a = J.attachments[k]; m.attachments[k] = { bone: a[0], pos: [a[1], a[2], a[3]] }; }
    m.standSeq = J.standSeq; m.skinFileIds = [];
    const skin = { tri: new Uint32Array(buf, at(5), J.tris), subs: J.subs.map(s => ({ id: s[0], iStart: s[1], iCount: s[2] })), batches: J.batches.map(b => ({ sub: b[0], texCombo: b[1], material: b[2] })) };
    return { m2: m, skin, model: J.model };
  }

  G.TM = G.TM || {};
  G.TM.parseM2 = parseM2;
  G.TM.parseSkin = parseSkin;
  G.TM.loadSlim = loadSlim;
})(window);
