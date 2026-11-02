/* BrokenMeta transmog viewer: character + customization + three.js scene (own code). */
(function (G) {
  'use strict';
  const THREE = G.THREE, TM = G.TM;

  // ---- data access -------------------------------------------------------------------------
  const cache = {};
  function getJSON(base, p) { return cache[p] || (cache[p] = fetch(base + p).then(r => { if (!r.ok) throw new Error(p + ' ' + r.status); return r.json(); })); }
  function getBuf(base, p) { return fetch(base + p).then(r => { if (!r.ok) throw new Error(p + ' ' + r.status); return r.arrayBuffer(); }); }
  function getImage(base, id) {
    const k = 'img' + id;
    return cache[k] || (cache[k] = new Promise((res, rej) => {
      const im = new Image(); im.onload = () => res(im); im.onerror = () => rej(new Error('texture ' + id)); im.src = base + 'textures/' + id + '.webp';
    }));
  }

  // item appearance metadata: packed per slot (items/armor-<inv>.json, items/weapon.json), raw per-file metadata as a fallback (dev)
  async function itemMeta(base, weapon, inv, display) {
    const key = weapon ? 'weapon' : 'armor-' + inv;
    const pack = await (cache['pack' + key] || (cache['pack' + key] = fetch(base + 'items/' + key + '.json').then(r => r.ok ? r.json() : null).catch(() => null)));
    if (pack && pack[display]) return pack[display];
    return getJSON(base, weapon ? 'meta/item/' + display + '.json' : 'meta/armor/' + inv + '/' + display + '.json');
  }
  // item / helmet / shoulder model: the compact baked file (models/<id>.tmc.gz), the raw m2 + skin when it is not baked
  async function loadModel(base, id) {
    try { return await TM.loadSlim(base + 'models/' + id + '.tmc.gz'); } catch (e) { /* not baked: dev fallback */ }
    const m2 = TM.parseM2(await getBuf(base, 'm2/' + id + '.m2'));
    return { m2, skin: TM.parseSkin(await getBuf(base, 'skin/' + m2.skinFileIds[0] + '.skin')) };
  }

  // WoW (x fwd, y left, z up) -> three (x = left, y = up, z = fwd): right-handed, character faces +z
  function toThree(pos) {
    const out = new Float32Array(pos.length);
    for (let i = 0; i < pos.length; i += 3) { out[i] = pos[i + 1]; out[i + 1] = pos[i + 2]; out[i + 2] = pos[i]; }
    return out;
  }

  // rest pose: bone matrices (WoW axes) from the first key of the Stand animation, then CPU skinning of the vertices
  // altSeq: bone index -> animation id whose pose replaces Stand for that bone (the fingers of a hand that holds a weapon)
  function poseModel(m2, altSeq, extra) {
    altSeq = altSeq || {}; extra = extra || {};
    const B = m2.bones, M = new Array(B.length), done = new Array(B.length);
    const world = (i) => {
      if (done[i]) return M[i];
      const b0 = B[i], al = altSeq[i] && b0.alt && b0.alt[altSeq[i]];
      const b = al ? { pivot: b0.pivot, parent: b0.parent, t: al.t || b0.t, r: al.r || b0.r, s: al.s || b0.s } : b0;
      const l = new THREE.Matrix4(), pv = b.pivot;
      let q = b.r ? new THREE.Quaternion(b.r[0], b.r[1], b.r[2], b.r[3]).normalize() : new THREE.Quaternion();
      if (extra[i]) q = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), extra[i]).multiply(q);      // extra bend about the lateral axis (wow y)
      const t = b.t || [0, 0, 0], s = b.s || [1, 1, 1];
      l.makeTranslation(pv[0], pv[1], pv[2])
        .multiply(new THREE.Matrix4().compose(new THREE.Vector3(t[0], t[1], t[2]), q, new THREE.Vector3(s[0], s[1], s[2])))
        .multiply(new THREE.Matrix4().makeTranslation(-pv[0], -pv[1], -pv[2]));
      M[i] = b.parent >= 0 && b.parent < B.length ? world(b.parent).clone().multiply(l) : l;
      done[i] = true; return M[i];
    };
    for (let i = 0; i < B.length; i++) world(i);
    const n = m2.vertCount, pos = new Float32Array(n * 3), nrm = new Float32Array(n * 3), v = new THREE.Vector3(), nv = new THREE.Vector3(), acc = new THREE.Vector3(), accN = new THREE.Vector3();
    for (let i = 0; i < n; i++) {
      acc.set(0, 0, 0); accN.set(0, 0, 0); let ws = 0;
      for (let k = 0; k < 4; k++) {
        const w = m2.bw[i * 4 + k] / 255; if (!w) continue;
        const mm = M[m2.bi[i * 4 + k]]; if (!mm) continue;
        v.set(m2.pos[i * 3], m2.pos[i * 3 + 1], m2.pos[i * 3 + 2]).applyMatrix4(mm); acc.addScaledVector(v, w);
        nv.set(m2.nrm[i * 3], m2.nrm[i * 3 + 1], m2.nrm[i * 3 + 2]).transformDirection(mm); accN.addScaledVector(nv, w); ws += w;
      }
      if (ws < 0.01) { acc.set(m2.pos[i * 3], m2.pos[i * 3 + 1], m2.pos[i * 3 + 2]); accN.set(m2.nrm[i * 3], m2.nrm[i * 3 + 1], m2.nrm[i * 3 + 2]); }
      pos[i * 3] = acc.x; pos[i * 3 + 1] = acc.y; pos[i * 3 + 2] = acc.z; nrm[i * 3] = accN.x; nrm[i * 3 + 1] = accN.y; nrm[i * 3 + 2] = accN.z;
    }
    // an attachment point follows the body mesh: skin it like its nearest vertex (the bone chain of the attachment bone itself
    // can carry no data for the Stand animation); the linear part (rotation/scale) comes from the vertex's dominant bone
    const skinPoint = (pt) => {
      let best = 0, bd = 1e9;
      for (let i = 0; i < n; i++) { const dx = m2.pos[i * 3] - pt[0], dy = m2.pos[i * 3 + 1] - pt[1], dz = m2.pos[i * 3 + 2] - pt[2], d = dx * dx + dy * dy + dz * dz; if (d < bd) { bd = d; best = i; } }
      const out = new THREE.Vector3(), p = new THREE.Vector3(); let top = -1, tw = -1;
      for (let k = 0; k < 4; k++) {
        const w = m2.bw[best * 4 + k] / 255, mm = M[m2.bi[best * 4 + k]]; if (!w || !mm) continue;
        out.addScaledVector(p.set(pt[0], pt[1], pt[2]).applyMatrix4(mm), w); if (w > tw) { tw = w; top = m2.bi[best * 4 + k]; }
      }
      return { pos: out, M: M[top] };
    };
    return { pos, nrm, M, skinPoint };
  }

  // chr model id -> {s, up, out, fwd, tilt}: shoulder pad calibration; models not listed use the raw attachment
  const ELBOW = 0;                // rad: elbow bend of the weapon arm (Wowhead's pose: the hand is at the waist, not at the thigh)
  const WRIST = 0;                // rad: wrist straightening (kept small: more makes a visible kink at the bracelet); the rest is taken by tilting the weapon
  const WEAPON_TILT = ELBOW - WRIST;
  const BOW_TILT = -Math.PI / 2;  // rad: a bow model lies along the forward axis: stand it up (limbs vertical)
  const WEAPON_PITCH = 0.08;      // rad: how far above horizontal the blade points (every race is levelled to this)       // rad: from "forward through the fist" to "blade up" (tuned by eye, Wowhead not reachable to compare)
  const WEAPON_ROLL = 0;  // rad: spin of the weapon about its own axis
  const WEAPON_LEAN = 0;       // rad: outward lean of the upright weapon (in-game screenshot: about 25 degrees)
  const WEAPON_POMMEL = 0;        // 0..1: how far the pommel is slid into the palm (0 = as modelled, like Wowhead)
  const EQUIP_ORDER = ['shirt', 'legs', 'waist', 'chest', 'tabard', 'wrist', 'hands', 'feet'];
  const SLOT_OF_INV = { 4: 'shirt', 5: 'chest', 20: 'chest', 6: 'waist', 7: 'legs', 8: 'feet', 9: 'wrist', 10: 'hands', 16: 'back', 19: 'tabard' };
  const TUNE = {
    // fitted against Wowhead's own render of the same item (pad box measured as a fraction of the body height); tilt = pads fan outward
    5: { s: 0.80, up: 0.025, out: 0.061, fwd: 0.05, tilt: 0.25 },    // dwarf male
    10: { s: 0.56, up: -0.006, out: 0.008, fwd: 0.02, tilt: 0.25 }, // undead female
    11: { s: 1.78, up: -0.092, out: 0.087, fwd: 0.1, tilt: 0.25 },   // tauren male
    12: { s: 1.11, up: 0.114, out: 0.132, fwd: 0.05, tilt: 0.25 },   // tauren female
    15: { s: 1.10, up: 0.022, out: 0.052, fwd: 0.05, tilt: 0.3 },    // troll male
  };

  // set the rotation of a transform so the model's +z axis points along dir (keeps the translation); roll spins about that axis
  function aimBase(m, dir, roll) {
    const e = m.elements, z = dir.clone().normalize(), up = new THREE.Vector3(0, 1, 0);
    let x = new THREE.Vector3().crossVectors(up, z); if (x.lengthSq() < 1e-6) x.set(1, 0, 0); x.normalize();
    const y = new THREE.Vector3().crossVectors(z, x);
    const R = new THREE.Matrix4().makeBasis(x, y, z); R.setPosition(e[12], e[13], e[14]);
    if (roll) R.multiply(new THREE.Matrix4().makeRotationZ(roll));
    m.copy(R);
  }

  // ---- character ---------------------------------------------------------------------------
  class Character {
    constructor(base, chrModelId) { this.base = base; this.id = chrModelId; this.choice = {}; this.group = new THREE.Group(); this.meshes = []; }

    async load() {
      const b = this.base;
      const meta = await getJSON(b, 'meta/character/' + this.id + '.json');
      this.raceId = meta.Character ? meta.Character.Race : 0;
      this.gender = meta.Character ? meta.Character.Gender : 0;     // 0 male / 1 female: picks the armour texture variant
      this.equip = this.equip || {};
      this.cust = await getJSON(b, 'meta/charactercustomization/' + this.id + '.json');
      let slim = null;
      try { slim = await TM.loadSlim(b + 'chars/' + this.id + '.tmc.gz'); } catch (e) { /* no compact file: use the raw model (dev) */ }
      if (slim) { this.m2 = slim.m2; this.skin = slim.skin; }
      else {
        this.m2 = TM.parseM2(await getBuf(b, 'm2/' + meta.Model + '.m2'));
        this.skin = TM.parseSkin(await getBuf(b, 'skin/' + this.m2.skinFileIds[0] + '.skin'));
      }
      for (const o of this.cust.Options) if (this.choice[o.Id] === undefined) this.choice[o.Id] = 0;

      // shared geometry; one index range per submesh
      this.pose = poseModel(this.m2);
      const pos = toThree(this.pose.pos), nrm = toThree(this.pose.nrm);
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      geo.setAttribute('normal', new THREE.BufferAttribute(nrm, 3));
      geo.setAttribute('uv', new THREE.BufferAttribute(this.m2.uv, 2));
      // WoW triangles are clockwise once mirrored into three's axes: flip the winding
      const tri = this.skin.tri, idx = new Uint32Array(tri.length);
      for (let i = 0; i < tri.length; i += 3) { idx[i] = tri[i]; idx[i + 1] = tri[i + 2]; idx[i + 2] = tri[i + 1]; }
      geo.setIndex(new THREE.BufferAttribute(idx, 1));
      this.geo = geo;

      // one mesh per submesh that has a batch; texture slot comes from the batch's texture combo
      this.parts = [];
      for (const bt of this.skin.batches) {
        const sub = this.skin.subs[bt.sub];
        const slot = this.m2.texLookup[bt.texCombo];
        const tx = this.m2.textures[slot];
        const mat = this.m2.materials[bt.material] || { blend: 0, flags: 0 };
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', geo.getAttribute('position')); g.setAttribute('normal', geo.getAttribute('normal')); g.setAttribute('uv', geo.getAttribute('uv'));
        g.setIndex(new THREE.BufferAttribute(idx.subarray(sub.iStart, sub.iStart + sub.iCount), 1));
        const m = new THREE.MeshLambertMaterial({ side: THREE.DoubleSide, alphaTest: 0.5 });
        const mesh = new THREE.Mesh(g, m); mesh.visible = false;
        this.group.add(mesh);
        this.parts.push({ id: sub.id, tx, blend: mat.blend, mesh, mat: m });
      }
      await this.refresh();
      return this;
    }

    setChoice(optionId, index) { this.choice[optionId] = index; return this.refresh(); }
    setChoices(map) { Object.assign(this.choice, map); return this.refresh(); }     // several options at once, one refresh

    // chosen customization elements -> geoset ids + texture targets
    selection() {
      const geosets = {}, targets = {};
      // an element with a VariationChoiceID (face / eyebrow textures) only applies when that choice id is picked elsewhere
      // (face <- skin colour, eyebrows <- hair colour)
      const picked = new Set();
      for (const o of this.cust.Options) { const c = o.Choices[this.choice[o.Id]]; if (c) picked.add(c.Id); }
      for (const o of this.cust.Options) {
        const c = o.Choices[this.choice[o.Id]]; if (!c) continue;
        for (const e of c.Elements) {
          if (e.VariationChoiceID && !picked.has(e.VariationChoiceID)) continue;
          if (e.Geoset) geosets[e.Geoset.GeosetType] = e.Geoset.GeosetID;
          if (e.Material) targets[e.Material.TextureTarget] = e.Material.MaterialResourcesID;
        }
      }
      return { geosets, targets };
    }

    async composite(sel) {
      const b = this.base, out = {};
      const files = this.cust.TextureFiles;
      const fid = (resId) => { const f = files[resId]; return f && f[0] && f[0].FileDataId; };
      for (const mt of this.cust.Materials) {
        const cv = document.createElement('canvas'); cv.width = mt.Width; cv.height = mt.Height; out[mt.TextureType] = { cv, ctx: cv.getContext('2d') };
      }
      const layers = this.cust.TextureLayers.slice().sort((a, b) => a.Layer - b.Layer);
      for (const L of layers) {
        const res = sel.targets[L.ChrModelTextureTargetID]; const id = res && fid(res); const dst = out[L.TextureType];
        if (!id || !dst) continue;
        const im = await getImage(b, id);
        const sec = L.TextureSection >= 0 ? this.cust.TextureSections.find(s => s.SectionType === L.TextureSection) : null;
        const W = dst.cv.width, H = dst.cv.height;
        if (sec) dst.ctx.drawImage(im, sec.X * W, sec.Y * H, sec.Width * W, sec.Height * H);
        else dst.ctx.drawImage(im, 0, 0, W, H);
      }
      // worn armour: component textures (arm / torso / leg / hand / foot regions) are painted over the skin; later = on top
      const body = out[1];
      if (body) for (const slot of EQUIP_ORDER) {
        const e = this.equip[slot]; if (!e || !e.meta.ComponentTextures) continue;
        for (const region in e.meta.ComponentTextures) {
          const list = (e.meta.TextureFiles || {})[e.meta.ComponentTextures[region]] || [];
          const f = list.find(x => x.Gender === this.gender) || list.find(x => x.Gender === 3) || list[0];
          const sec = f && this.cust.TextureSections.find(s => s.SectionType === +region && s.Width < 0.6);     // sections 9 / 10 are the face halves
          if (!sec) continue;
          const im = await getImage(b, f.FileDataId), W = body.cv.width, H = body.cv.height;
          body.ctx.drawImage(im, sec.X * W, sec.Y * H, sec.Width * W, sec.Height * H);
        }
      }
      return out;
    }

    // geoset groups an armour piece switches (value = group * 100 + 1 + item's GeosetGroup[i]); see the ItemDisplayInfo geoset fields
    equipGeosets() {
      const o = {};
      for (const slot of EQUIP_ORDER.concat(['back'])) {
        const e = this.equip[slot]; if (!e) continue;
        const g = e.meta.Item.GeosetGroup || [];
        if (slot === 'hands') o[4] = 1 + g[0];
        else if (slot === 'feet') o[5] = 1 + g[0];
        else if (slot === 'chest') { o[8] = 1 + g[0]; o[10] = 1 + g[1]; if (e.meta.Item.InventoryType === 20 || g[2] > 0) o[13] = 1 + g[2]; }
        else if (slot === 'legs') { o[9] = 1 + g[0]; o[11] = 1 + g[1]; if (g[2] > 0) o[13] = 1 + g[2]; }
        else if (slot === 'tabard') o[12] = 1 + g[0];
        else if (slot === 'back') o[15] = 1 + g[0];
        else if (slot === 'waist') o[18] = 1 + g[0];
      }
      return o;
    }

    // dress / undress a slot with an appearance (display id); shoulders ride the attachment point, everything else paints or swaps geosets
    async setEquip(inv, displayId) {
      if (inv === 3) return this.setItem(3, displayId);
      if (inv === 1) { await this.setItem(1, displayId); return this.refresh(); }
      const slot = SLOT_OF_INV[inv]; if (!slot) throw new Error('slot ' + inv + ' not supported yet');
      const tk = this._tick('e' + slot);
      if (!displayId) delete this.equip[slot];
      else {
        const meta = await itemMeta(this.base, false, inv, displayId);
        if (this._stale('e' + slot, tk)) return;
        this.equip[slot] = { inv, meta };
      }
      return this.refresh();
    }

    // the hand that carries a weapon closes around it: its finger bones take the Ready1H / Ready2H pose, then the skin is rebuilt
    repose() {
      const B = this.m2.bones, alt = {}, extra = {};
      for (const attId in (this.hand || {})) {
        const att = this.m2.attachments[attId]; if (!att) continue;
        // only the fingers of that hand take the Ready pose (closed fist); the arm keeps its Stand pose, as in Wowhead's viewer (the Ready arm is raised)
        let root = att.bone;
        for (let i = 0; i < 2 && B[root].parent >= 0; i++) root = B[root].parent;
        const kids = new Set([root]);
        for (let grew = true; grew;) { grew = false; B.forEach((b, i) => { if (!kids.has(i) && kids.has(b.parent)) { kids.add(i); grew = true; } }); }
        // the pose that really closes THIS hand: some models animate the off hand only in another Ready animation (ReadyUnarmed...)
        const score = (seq) => { let s = 0; kids.forEach(i => { if (i === root) return; const a = B[i].alt && B[i].alt[seq], r0 = B[i].r; if (a && a.r) { const q1 = new THREE.Quaternion(a.r[0], a.r[1], a.r[2], a.r[3]).normalize(), q0 = r0 ? new THREE.Quaternion(r0[0], r0[1], r0[2], r0[3]).normalize() : new THREE.Quaternion(); s += q1.angleTo(q0); } }); return s; };
        const pref = this.hand[attId], cands = [pref, 26, 27, 25, 28];
        let best = pref, bs = score(pref);
        for (const sq of cands) { const sc = score(sq); if (sc > bs * 1.5) { best = sq; bs = sc; } }
        kids.forEach(i => { if (i !== root) alt[i] = best; });
        // elbow bent a little (the hand comes up in front of the hip) while the wrist straightens so the weapon keeps pointing forward
        let fore = root; if (B[fore].parent >= 0) fore = B[fore].parent;
        if (ELBOW) { extra[fore] = -ELBOW; extra[root] = WRIST; }
      }
      this.pose = poseModel(this.m2, alt, extra);
      const pa = this.geo.getAttribute('position'), na = this.geo.getAttribute('normal');
      pa.array.set(toThree(this.pose.pos)); na.array.set(toThree(this.pose.nrm)); pa.needsUpdate = true; na.needsUpdate = true;
    }

    // every slot keeps a ticket: when two requests for the same slot overlap (hover preview then click), only the last one is shown
    _tick(k) { this._tv = this._tv || {}; return (this._tv[k] = (this._tv[k] || 0) + 1); }
    _stale(k, tk) { return this._tv[k] !== tk; }

    // ---- held items: weapons, shields, off-hand frills, bows. They ride the hand / shield attachment bones ----
    // key: 'mh' | 'oh' | 'rng'; inv = inventory type (decides which hand); displayId 0 clears
    // mode: 'hand' (drawn) | 'back' | 'hip' (sheathed). Two-handers, shields and ranged weapons can only go on the back; 1H weapons choose back or hip.
    async setWeapon(key, inv, displayId, mode) {
      mode = mode || 'hand';
      this.items = this.items || {};
      const tk = this._tick('w' + key);
      if (this.items[key]) { this.group.remove(this.items[key]); delete this.items[key]; }
      this.hand = this.hand || {}; this.heldAtt = this.heldAtt || {};
      if (this.heldAtt[key] !== undefined) { delete this.hand[this.heldAtt[key]]; delete this.heldAtt[key]; this.repose(); }
      if (!displayId) return;
      const a = await itemMeta(this.base, true, inv, displayId);
      const comp = a.ComponentModels && Object.values(a.ComponentModels)[0];
      const f = a.ModelFiles && a.ModelFiles[comp] && a.ModelFiles[comp][0];
      if (!f) return;
      // attachment ids: 0 shield (left forearm), 1 right hand, 2 left hand. Bows are drawn in the left hand, everything else one-handed in the hand of its slot.
      // sheathed: 26 / 27 main / off hand on the back, 28 shield, 30 / 31 large weapon on the back, 32 / 33 left / right hip
      let attId = key === 'mh' ? 1 : key === 'oh' ? (inv === 14 ? 0 : 2) : (inv === 15 ? 2 : 1);
      const sheathed = mode !== 'hand' && inv !== 23;
      if (sheathed) {
        const oneHand = [13, 21, 22].includes(inv);
        if (inv === 14) attId = 28;
        else if (inv === 17 || inv === 15 || inv === 26 || inv === 25) attId = (inv === 15 || key === 'rng') ? 30 : 31;
        else if (mode === 'hip' && oneHand) attId = key === 'oh' ? 32 : 33;
        else attId = key === 'oh' ? 27 : 26;
      }
      const att = this.m2.attachments[attId]; if (!att) return;
      const mesh = await this.itemMesh(f.FileDataId, a);        // a THREE.Group
      if (this._stale('w' + key, tk)) return;                  // a newer weapon was asked for meanwhile
      if (!sheathed && [13, 17, 21, 22, 26, 25, 15, 23].includes(inv)) { this.hand[attId] = inv === 17 ? 27 : 26; this.heldAtt[key] = attId; this.repose(); }     // closed fist around a melee weapon
      const bone = this.m2.bones[att.bone], pv = bone.pivot;
      const hasPos = Math.abs(att.pos[0]) + Math.abs(att.pos[1]) + Math.abs(att.pos[2]) > 1e-6, P = hasPos ? att.pos : pv;       // hand attachments sit on their bone pivot, sheath ones carry an absolute position
      const W = this.pose.M[att.bone].clone().multiply(new THREE.Matrix4().makeTranslation(P[0], P[1], P[2]));
      const C = new THREE.Matrix4().set(0, 1, 0, 0,  0, 0, 1, 0,  1, 0, 0, 0,  0, 0, 0, 1);
      mesh.matrixAutoUpdate = false;
      const base = new THREE.Matrix4().copy(C).multiply(W).multiply(new THREE.Matrix4().copy(C).transpose());
      // the closed hand (Ready pose) points the weapon forward through the fist; the game shows it upright (blade up) in the stand pose; the off-hand one is mirrored
      if (!sheathed && inv === 23) base.multiply(new THREE.Matrix4().makeRotationX(-1.35));          // held in the off hand (torch, orb, book): upright, flame / glow on top       // a bow is held with its limbs up and down
      if (!sheathed && [13, 17, 21, 22, 26, 25, 15].includes(inv)) {      // a drawn bow is held level like every other weapon
        base.multiply(new THREE.Matrix4().makeRotationZ(attId === 2 ? -WEAPON_LEAN : WEAPON_LEAN));     // applied last (in the hand frame): the blade leans away from the body
        base.multiply(new THREE.Matrix4().makeRotationX(WEAPON_TILT));
        base.multiply(new THREE.Matrix4().makeRotationZ(WEAPON_ROLL));
        // level the blade: whatever the race's arm / hand bones give, the weapon rises a few degrees above horizontal like in Wowhead's pose
        for (let it = 0; it < 3; it++) {
          const d = new THREE.Vector3(0, 0, 1).transformDirection(base), up = new THREE.Vector3(0, 1, 0).transformDirection(base);
          const err = WEAPON_PITCH - Math.asin(Math.max(-1, Math.min(1, d.y)));
          base.multiply(new THREE.Matrix4().makeRotationX(-err / Math.max(0.4, up.y)));
        }
        // the pommel (handle end, lowest point along the blade axis) sits in the palm: slide the weapon along its axis, at most 15 cm
        const pz = mesh.userData.geo.getAttribute('position'); let minZ = 0; for (let i = 0; i < pz.count; i++) minZ = Math.min(minZ, pz.getZ(i));
        base.multiply(new THREE.Matrix4().makeTranslation(0, 0, Math.min(0.15, Math.max(0, -minZ - 0.03)) * WEAPON_POMMEL));                                // spin about the handle: the flat of the blade faces forward
        if (attId === 2) base.multiply(new THREE.Matrix4().makeScale(-1, 1, 1));
      }
      if (sheathed && inv !== 14) {
        // stored weapons are aimed explicitly (the sheath attachments' own axes differ from side to side): blade direction in character space
        // (three: x = character's left, y up, z forward), handle up for back stowage, blade back-and-down for the hip
        const left = (attId === 27 || attId === 32) ? 1 : -1;           // which side of the body the weapon sits on
        const aim = attId === 30 || attId === 31 ? new THREE.Vector3(attId === 31 ? 0.5 : -0.5, -0.85, -0.15)
          : (attId === 32 || attId === 33) ? new THREE.Vector3(left * -0.1, -0.55, -0.82)
          : new THREE.Vector3(-left * 0.45, -0.85, -0.2);
        if (inv === 15) aim.set(0.6, 1, -0.05);                         // a bow is slung diagonally across the back (not standing above the head)
        // the heavy side of the model (blade / head: where most vertices are) must point along aim; models do not all have the same orientation
        const gp = mesh.userData.geo.getAttribute('position'); let zs = 0; for (let i = 0; i < gp.count; i++) zs += gp.getZ(i);
        if (zs < 0) aim.negate();                       // most of the geometry (the head / blade) is on the -z side
        aimBase(base, aim.normalize(), 0);
        if (inv === 15) base.elements[13] -= 0.25;                      // and lower than its attachment point (the bow is long)
      }
      mesh.userData.base = base; mesh.matrix.copy(base);
      const holder = new THREE.Group(); holder.add(mesh);
      if (this.items[key]) { this.group.remove(this.items[key]); delete this.items[key]; }
      this.items[key] = holder; this.group.add(holder);
    }

    async setWeapons(list) {                       // list = [[key, inventory type, display id], ...]; the keys not listed are emptied
      for (const k of ['mh', 'oh', 'rng']) { if (!list.some(e => e[0] === k)) await this.setWeapon(k, 0, 0); }
      for (const [k, inv, d, mode] of list) await this.setWeapon(k, inv, d, mode);
    }

    // one item model (m2 + first skin profile) as a group: one mesh per batch with its own texture / blend mode
    // (torches have a flame layer, orbs a glow...). Texture of a slot: the file in the model itself (type 0) or the item's Textures table.
    async itemMesh(fileId, a) {
      const { m2, skin: sk } = await loadModel(this.base, fileId);
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(toThree(m2.pos), 3));
      geo.setAttribute('normal', new THREE.BufferAttribute(toThree(m2.nrm), 3));
      geo.setAttribute('uv', new THREE.BufferAttribute(m2.uv, 2));
      const idx = new Uint32Array(sk.tri.length);
      for (let i = 0; i < idx.length; i += 3) { idx[i] = sk.tri[i]; idx[i + 1] = sk.tri[i + 2]; idx[i + 2] = sk.tri[i + 1]; }
      const group = new THREE.Group(); group.userData.geo = geo;
      const T = a.Textures || {};
      const batches = sk.batches.length ? sk.batches : [{ sub: 0, texCombo: 0, material: 0 }];
      for (const bt of batches) {
        const sub = sk.subs[bt.sub]; if (!sub) continue;
        const tx = m2.textures[m2.texLookup[bt.texCombo]] || m2.textures[0] || { type: 2, fileId: 0 };
        const file = tx.type === 0 ? tx.fileId : (T[tx.type] || T[2]);
        const blend = (m2.materials[bt.material] || { blend: 0 }).blend;
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', geo.getAttribute('position')); g.setAttribute('normal', geo.getAttribute('normal')); g.setAttribute('uv', geo.getAttribute('uv'));
        g.setIndex(new THREE.BufferAttribute(idx.subarray(sub.iStart, sub.iStart + sub.iCount), 1));
        const mat = new THREE.MeshLambertMaterial({ side: THREE.DoubleSide, map: file ? this.fileTexture(file) : null, alphaTest: blend <= 1 ? 0.5 : 0.01, transparent: blend >= 2 });
        if (blend >= 2) mat.depthWrite = false;
        if ([3, 4, 6, 7].includes(blend)) { mat.blending = THREE.AdditiveBlending; mat.emissive = new THREE.Color(0xffffff); mat.emissiveMap = mat.map; }
        group.add(new THREE.Mesh(g, mat));
      }
      return group;
    }

        // several slots at once (after a race / sex change): one refresh. entries = [[inventory type, display id], ...]
    async setEquips(entries) {
      this.equip = {};
      for (const [inv, d] of entries) {
        if (inv === 3 || inv === 1) { await this.setItem(inv, d); continue; }
        const slot = SLOT_OF_INV[inv]; if (slot && d) this.equip[slot] = { inv, meta: await itemMeta(this.base, false, inv, d) };
      }
      if (!entries.some(e => e[0] === 3)) await this.setItem(3, 0);
      if (!entries.some(e => e[0] === 1)) await this.setItem(1, 0);
      return this.refresh();
    }

    async refresh() {
      const rt = this._tick('refresh');
      const sel = this.selection();
      const comp = await this.composite(sel);
      if (this._stale('refresh', rt)) return;                           // a newer refresh already started: it carries the latest state
      const texOf = {};
      if (this._texOf) for (const k in this._texOf) this._texOf[k].dispose();
      for (const t in comp) { const T = new THREE.CanvasTexture(comp[t].cv); T.flipY = false; T.encoding = THREE.sRGBEncoding; texOf[t] = T; }
      this._texOf = texOf;
      // which geoset variant is shown per group: customization choice, else the "01" (bare / default) one
      const want = new Set();
      for (const g in sel.geosets) want.add(g * 100 + sel.geosets[g]);
      for (let g = 4; g <= 33; g++) if (!(g in sel.geosets) && g !== 7 && g !== 17) want.add(g * 100 + 1);
      if (!(32 in sel.geosets)) { want.delete(3201); want.add(3202); }   // the head itself is geoset 3202 when the race has no "Face Shape" option (orcs)
      if (!(7 in sel.geosets)) want.add(702);   // no "Ears" option for this race (orcs): default ear geoset, else the head has a hole
      const eg = this.equipGeosets();
      for (const g in eg) { for (const w of [...want]) if (Math.floor(w / 100) === +g) want.delete(w); want.add(g * 100 + eg[g]); }
      if (this.helm) {          // a helmet hides hair (group 0 minus the body), ears, facial hair... depending on race and sex
        const hide = (this.gender ? this.helm.Item.HideGeosetFemale : this.helm.Item.HideGeosetMale) || [];
        for (const h of hide) if (h.RaceId === this.raceId) for (const w of [...want]) if (w !== 0 && Math.floor(w / 100) === h.GeosetGroup) want.delete(w);
      }
      want.add(0);
      for (const p of this.parts) {
        const show = want.has(p.id);
        let tex = null;
        if (p.tx) tex = p.tx.type === 0 ? this.fileTexture(p.tx.fileId) : texOf[p.tx.type];
        if (p.tx && p.tx.type === 2) { const bk = this.equip.back; let f = bk && bk.meta.Textures && bk.meta.Textures[2]; if (!f && bk && bk.meta.ComponentTextures) { const l = (bk.meta.TextureFiles || {})[bk.meta.ComponentTextures[12]] || []; f = l[0] && l[0].FileDataId; } tex = f ? this.fileTexture(f) : null; }     // cape texture (region 12)
        p.mesh.visible = show && !!tex;
        if (tex && p.mat.map !== tex) { p.mat.map = tex; p.mat.needsUpdate = true; }
      }
    }

    // ---- equipment ---------------------------------------------------------------------------
    // slot = inventory type (3 = shoulders ...), displayId = item appearance. Returns once the item is on the character.
    async setItem(slot, displayId) {
      this.items = this.items || {};
      const tk = this._tick('i' + slot);
      if (this.items[slot]) { this.group.remove(this.items[slot]); delete this.items[slot]; }
      if (slot === 1) this.helm = null;
      if (!displayId) return;
      const a = await itemMeta(this.base, false, slot, displayId);
      if (this._stale('i' + slot, tk)) return;
      const holder = new THREE.Group();
      const comp = a.ComponentModels && Object.values(a.ComponentModels)[0];
      let files = (a.ModelFiles && a.ModelFiles[comp]) || [];
      if (slot === 1) {                    // helmets: one model per race and sex, worn on the head anchor (attachment 11); hides hair / ears / beards
        const mine = files.find(f => f.Race === this.raceId && f.Gender === this.gender) || files.find(f => f.Race === this.raceId) || files[0];
        files = mine ? [mine] : [];
        this._helmNext = a;
      }
      const ATT = { 3: [6, 5] };          // inventory slot -> attachment ids for [ExtraData 0, ExtraData 1]
      for (const f of files) {
        const att = slot === 1 ? this.m2.attachments[11] : ATT[slot] && this.m2.attachments[ATT[slot][f.ExtraData || 0]];
        if (!att) continue;
        const { m2, skin: sk } = await loadModel(this.base, f.FileDataId);
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.BufferAttribute(toThree(m2.pos), 3));
        g.setAttribute('normal', new THREE.BufferAttribute(toThree(m2.nrm), 3));
        g.setAttribute('uv', new THREE.BufferAttribute(m2.uv, 2));
        const idx = new Uint32Array(sk.tri.length);
        for (let i = 0; i < idx.length; i += 3) { idx[i] = sk.tri[i]; idx[i + 1] = sk.tri[i + 2]; idx[i + 2] = sk.tri[i + 1]; }
        g.setIndex(new THREE.BufferAttribute(idx, 1));
        const texId = a.Textures && (a.Textures[(m2.textures[0] || {}).type] || a.Textures[2]);
        const mat = new THREE.MeshLambertMaterial({ side: THREE.DoubleSide, alphaTest: 0.5, map: texId ? this.fileTexture(texId) : null });
        const mesh = new THREE.Mesh(g, mat);
        // the item rides its attachment bone: posed position AND the bone's rotation/scale (orc shoulder bones are scaled 0.9)
        const ap = this.pose.skinPoint(att.pos);
        const W = ap.M.clone(); W.setPosition(ap.pos);
        const C = new THREE.Matrix4().set(0, 1, 0, 0,  0, 0, 1, 0,  1, 0, 0, 0,  0, 0, 0, 1);   // wow (x,y,z) -> three (y,z,x)
        mesh.matrixAutoUpdate = false;
        mesh.userData.base = new THREE.Matrix4().copy(C).multiply(W).multiply(new THREE.Matrix4().copy(C).transpose());
        mesh.matrix.copy(mesh.userData.base);                // shoulders get their per-race calibration on top in tuneItems()
        mesh.userData.side = att.pos[1] > 0 ? 1 : -1;       // +1 = character's left (three +x)
        holder.add(mesh);
      }
      if (this._stale('i' + slot, tk)) return;                          // a newer item was asked for while the models loaded
      if (this.items[slot]) { this.group.remove(this.items[slot]); delete this.items[slot]; }
      if (slot === 1) this.helm = this._helmNext;
      this.items[slot] = holder; this.group.add(holder);
      this.tuneItems();
    }

    // per-model calibration of shoulder pads (the game scales/places them per race; ours is fitted by eye)
    //   s = scale, up/out/fwd = metres in character space (out moves each pad away from the body centre)
    tuneItems(t) {
      const k = Object.assign({ s: 1, up: 0, out: 0, fwd: 0, tilt: 0 }, TUNE[this.id], t);
      this.tune = k;
      const h = this.items && this.items[3]; if (!h) return;
      for (const m of h.children) {
        const side = m.userData.side;
        m.matrix.copy(new THREE.Matrix4().makeTranslation(side * k.out, k.up, k.fwd)).multiply(m.userData.base)
          .multiply(new THREE.Matrix4().makeRotationZ(-side * k.tilt)).multiply(new THREE.Matrix4().makeScale(k.s, k.s, k.s));   // tilt = top of the pad leaning outward (rad)
      }
    }

    fileTexture(id) {
      this._ft = this._ft || {};
      if (this._ft[id]) return this._ft[id];
      const t = new THREE.Texture(); t.flipY = false; t.encoding = THREE.sRGBEncoding;
      getImage(this.base, id).then(im => { t.image = im; t.needsUpdate = true; });
      return (this._ft[id] = t);
    }
  }

  // ---- scene -------------------------------------------------------------------------------
  class Viewer {
    constructor(container, base) {
      this.base = base;
      const w = container.clientWidth, h = container.clientHeight;
      this.r = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      this.r.setPixelRatio(Math.min(2, G.devicePixelRatio || 1)); this.r.setSize(w, h); this.r.outputEncoding = THREE.sRGBEncoding;
      container.appendChild(this.r.domElement);
      // follow the container size (responsive layout)
      new ResizeObserver(() => { const w2 = container.clientWidth, h2 = container.clientHeight; if (!w2 || !h2) return; this.r.setSize(w2, h2, false); this.cam.aspect = w2 / h2; this.cam.updateProjectionMatrix(); }).observe(container);
      this.scene = new THREE.Scene();
      this.cam = new THREE.PerspectiveCamera(30, w / h, 0.1, 50);
      this.scene.add(new THREE.AmbientLight(0xffffff, 0.75));
      const d = new THREE.DirectionalLight(0xffffff, 0.8); d.position.set(1, 2, 3); this.scene.add(d);
      this.yaw = 0.35; this.pitch = 0.05; this.dist = 4.2; this.target = new THREE.Vector3(0, 1.0, 0);
      const el = this.r.domElement; let drag = null;
      el.addEventListener('pointerdown', e => { drag = [e.clientX, e.clientY]; el.setPointerCapture(e.pointerId); });
      el.addEventListener('pointerup', () => drag = null);
      el.addEventListener('pointermove', e => { if (!drag) return; this.yaw += (e.clientX - drag[0]) * 0.01; this.pitch = Math.max(-0.6, Math.min(0.9, this.pitch + (e.clientY - drag[1]) * 0.005)); drag = [e.clientX, e.clientY]; });
      el.addEventListener('wheel', e => { e.preventDefault(); this.dist = Math.max(1.5, Math.min(9, this.dist * (1 + e.deltaY * 0.001))); }, { passive: false });
      const loop = () => { this.frame(); requestAnimationFrame(loop); }; loop();
    }
    frame() {
      const c = this.cam, t = this.target;
      c.position.set(t.x + Math.sin(this.yaw) * Math.cos(this.pitch) * this.dist, t.y + Math.sin(this.pitch) * this.dist, t.z + Math.cos(this.yaw) * Math.cos(this.pitch) * this.dist);
      c.lookAt(t); this.r.render(this.scene, c);
    }
    async setCharacter(chrModelId) {
      const ticket = this._t = (this._t || 0) + 1;      // clicking races quickly: only the latest request is shown
      const ch = await new Character(this.base, chrModelId).load();
      if (ticket !== this._t) return ch;
      if (this.char) this.scene.remove(this.char.group);
      this.char = ch;
      this.scene.add(this.char.group);
      // frame the character: height = top of the visible body parts (orcs/tauren are much taller than humans)
      const P = this.char.pose.pos, S = this.char.skin; let top = 0;
      for (const p of this.char.parts) if (p.mesh.visible) {
        const sub = S.subs.find(s => s.id === p.id);
        for (let i = sub.iStart; i < sub.iStart + sub.iCount; i++) top = Math.max(top, P[S.tri[i] * 3 + 2]);
      }
      this.target.set(0, top * 0.5, 0); this.dist = Math.max(2.6, top * 2.15);
      return this.char;
    }
  }

  TM.Viewer = Viewer; TM.Character = Character; TM.TUNE = TUNE;
})(window);
