/* BrokenMeta transmog simulator page (/wow-forever/transmogrification/): race + sex, customization, equipment, class filter, weapon stance.
   Needs three.js (assets/js/three.min.js), wow-transmog-m2.js and wow-transmog-viewer.js (the engine), and the baked assets under data-base
   (chars/, models/, items/, textures/, meta/, catalog.json, proficiency.json: see site_build/transmog_bake/). Texts come from #tmI18n. */
(function () {
  'use strict';
  const app = document.getElementById('tmApp');
  if (!app || !window.THREE || !window.TM) return;
  const BASE = app.dataset.base;
  const I = JSON.parse(document.getElementById('tmI18n').textContent);
  const FR = app.dataset.lang === 'fr';
  const $ = (id) => document.getElementById(id);
  const log = $('tmLog');
  const v = new TM.Viewer($('tmView'), BASE);
  window.tmViewer = v;                      // handy for debugging in the console

  // ---- race / sex ----------------------------------------------------------------------------------------------
  // [key, male chr model id, female chr model id] (both Skyborne races share models 218 / 219)
  const RACES = [['human', 1, 2], ['dwarf', 5, 6], ['nightelf', 7, 8], ['gnome', 13, 14], ['orc', 3, 4], ['undead', 9, 10], ['tauren', 11, 12], ['troll', 15, 16], ['skyborne', 218, 219]];
  let race = 'human', sex = 0;
  const chrId = () => RACES.find(r => r[0] === race)[1 + sex];
  const ICON = { undead: 'scourge' };       // the Scourge icon is the undead one
  const raceIcon = (key) => 'https://wow.zamimg.com/images/wow/icons/large/race_' + (ICON[key] || key) + '_' + (sex ? 'female' : 'male') + '.jpg';
  for (const [key] of RACES) {
    const b = document.createElement('button'), im = document.createElement('img');
    b.type = 'button'; b.dataset.race = key; b.title = I.races[key]; b.setAttribute('aria-label', I.races[key]); im.alt = I.races[key]; im.loading = 'lazy'; b.appendChild(im); $('tmRaces').appendChild(b);
  }
  function mark() {
    app.querySelectorAll('[data-race]').forEach(b => { b.classList.toggle('on', b.dataset.race === race); b.firstChild.src = raceIcon(b.dataset.race); });
    app.querySelectorAll('[data-sex]').forEach(b => b.classList.toggle('on', +b.dataset.sex === sex));
  }
  function pick(id) {
    log.textContent = I.loading;
    return v.setCharacter(id).then(async c => { if (c === v.char) { await c.setEquips(wornEntries()); await c.setWeapons(weaponEntries()); } return c; })
      .then(c => { if (c !== v.char) return; log.textContent = ''; buildOptions(c); })
      .catch(e => { log.textContent = I.error + ' ' + e.message; console.error(e); });
  }

  // ---- equipment: slot cards + searchable picker (catalogue = assets/transmog/catalog.json) ----------------------------
  // [key, inventory types, weapon slot?]
  const SLOTS = [['head', [1]], ['shoulder', [3]], ['back', [16]], ['chest', [5, 20]], ['shirt', [4]], ['tabard', [19]], ['wrist', [9]], ['hands', [10]], ['waist', [6]], ['legs', [7]], ['feet', [8]],
    ['mainhand', [13, 21, 17], true], ['offhand', [13, 22, 14, 23], true], ['ranged', [15, 26, 25], true]];
  const WKEY = { mainhand: 'mh', offhand: 'oh', ranged: 'rng' };
  const typeLabel = (r) => r[6] === 2 ? (I.weapon[r[7]] || (I.weapon_other + ' ' + r[7])) : (r[5] === 23 ? I.held : (I.armor[r[7]] || ('#' + r[7])));

  // ---- class filter: only the armor / weapon types the class can wear (Forever client data) -------------------------
  const CLASSES = [['WARRIOR', 'warrior'], ['PALADIN', 'paladin'], ['HUNTER', 'hunter'], ['ROGUE', 'rogue'], ['PRIEST', 'priest'], ['SHAMAN', 'shaman'], ['MAGE', 'mage'], ['WARLOCK', 'warlock'], ['DRUID', 'druid']];
  const DUAL_WIELD = new Set(['WARRIOR', 'ROGUE', 'HUNTER', 'SHAMAN']);
  const ARMOR_TYPE = { 1: 'Cloth', 2: 'Leather', 3: 'Mail', 4: 'Plate Mail', 6: 'Shield' };
  const WEAPON_TYPE = { 0: 'Axes', 1: 'Two-Handed Axes', 2: 'Bows', 3: 'Guns', 4: 'Maces', 5: 'Two-Handed Maces', 6: 'Polearms', 7: 'Swords', 8: 'Two-Handed Swords', 10: 'Staves', 13: 'Fist Weapons', 15: 'Daggers', 16: 'Thrown', 18: 'Crossbows', 19: 'Wands' };
  let PROF = null, myClass = null;
  function allowedFor(r, slotKey) {         // r = [id, name_en, name_fr, quality, icon, inv, class, subclass, display, appearance, required level]
    if (!myClass || !PROF) return true;
    const can = PROF.classes[myClass] || {}, inv = r[5], cls = r[6], sub = r[7];
    if (cls === 4) {
      if (inv === 16 || inv === 4 || inv === 19 || inv === 23 || sub === 0 || sub === 5) return true;     // cloaks, shirts, tabards, held items, cosmetic pieces: everyone
      const t = ARMOR_TYPE[sub]; return !t || t in can;
    }
    if (cls === 2) {
      if (slotKey === 'offhand' && [13, 22].includes(inv) && !DUAL_WIELD.has(myClass)) return false;     // no dual wield
      const t = WEAPON_TYPE[sub]; return t ? t in can : false;
    }
    return true;
  }
  function drawClasses() {
    const box = $('tmClasses'); box.innerHTML = '';
    const all = document.createElement('button'); all.type = 'button'; all.className = 'all'; all.textContent = I.all; all.title = I.no_filter; all.classList.toggle('on', !myClass); all.onclick = () => setClass(null); box.appendChild(all);
    for (const [key, icon] of CLASSES) {
      const b = document.createElement('button'), im = document.createElement('img');
      b.type = 'button'; im.src = 'https://wow.zamimg.com/images/wow/icons/large/classicon_' + icon + '.jpg'; im.alt = I.classes[key]; im.loading = 'lazy'; b.title = I.classes[key]; b.setAttribute('aria-label', I.classes[key]);
      b.classList.toggle('on', myClass === key); b.onclick = () => setClass(key); b.appendChild(im); box.appendChild(b);
    }
    $('tmClassHint').textContent = myClass ? I.class_hint.replace('{cls}', I.classes[myClass]) : '';
  }
  function setClass(k) { myClass = k; drawClasses(); const open = app.querySelector('.slot.open'); if (open) openPicker(open.dataset.slot); }
  fetch(BASE + 'proficiency.json').then(r => r.json()).then(j => { PROF = j; }).catch(() => { PROF = null; });

  // ---- worn items + weapon stance (drawn / back / hip) ---------------------------------------------------------------------
  const worn = {};                                                                  // slot key -> catalogue row
  const stance = { mainhand: 'hand', offhand: 'hand', ranged: 'hand' };
  const canHip = (k) => !!worn[k] && [13, 21, 22].includes(worn[k][5]);             // only one-handers sit at the hip
  const modeOf = (k) => (stance[k] === 'hip' && !canHip(k)) ? 'back' : stance[k];
  const wornEntries = () => SLOTS.filter(s => worn[s[0]] && !WKEY[s[0]]).map(s => [worn[s[0]][5], worn[s[0]][8]]);
  const weaponEntries = () => Object.keys(WKEY).filter(k => worn[k]).map(k => [WKEY[k], worn[k][5], worn[k][8], modeOf(k)]);
  const iconSrc = (n) => 'https://wow.zamimg.com/images/wow/icons/large/' + n + '.jpg';
  const itemName = (r) => FR ? (r[2] || r[1]) : r[1];
  const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const slotsBox = $('tmSlots'), picker = $('tmPicker');
  let CAT = null;
  async function loadCatalog() { if (CAT) return CAT; CAT = (await (await fetch(BASE + 'catalog.json')).json()).items; return CAT; }

  function drawSlots() {
    slotsBox.innerHTML = '';
    for (const [key] of SLOTS) {
      const r = worn[key], b = document.createElement('button'); b.type = 'button'; b.className = 'slot'; b.dataset.slot = key;
      b.innerHTML = (r ? '<img src="' + iconSrc(r[4]) + '" alt="">' : '<div class="ph"></div>') + '<div class="t"><b>' + esc(I.slots[key]) + '</b><span class="' + (r ? 'q' + r[3] : '') + '">' + (r ? esc(itemName(r)) : '—') + '</span></div>';
      b.onclick = () => openPicker(key); slotsBox.appendChild(b);
    }
  }
  const STANCES = [['hand', I.stance_hand], ['back', I.stance_back], ['hip', I.stance_hip]];
  function drawStance() {
    const box = $('tmStance'); box.innerHTML = '';
    const title = document.createElement('h3'); title.textContent = I.stance_title; box.appendChild(title);
    for (const k of ['mainhand', 'offhand', 'ranged']) {
      const row = document.createElement('div'), nm = document.createElement('span'), opts = document.createElement('div');
      row.className = 'srow'; opts.className = 'opts'; nm.textContent = I.slots[k];
      for (const [m, txt] of STANCES) {
        const b = document.createElement('button'); b.type = 'button'; b.textContent = txt;
        b.disabled = !worn[k] || (m === 'hip' && !canHip(k));
        b.classList.toggle('on', modeOf(k) === m && !!worn[k]);
        b.onclick = () => setStance(k, m); opts.appendChild(b);
      }
      row.append(nm, opts); box.appendChild(row);
    }
    const all = document.createElement('div'); all.className = 'all';
    const draw = document.createElement('button'), stow = document.createElement('button');
    draw.type = stow.type = 'button'; draw.textContent = I.draw_all; stow.textContent = I.stow_all;
    draw.onclick = () => { for (const k in stance) stance[k] = 'hand'; applyStance(); };
    stow.onclick = () => { for (const k in stance) stance[k] = canHip(k) ? 'hip' : 'back'; applyStance(); };
    all.append(draw, stow); box.appendChild(all);
  }
  async function applyStance() {
    drawStance();
    const c = v.char; if (!c) return;
    try { await c.setWeapons(weaponEntries()); } catch (e) { log.textContent = I.error + ' ' + e.message; console.error(e); }
  }
  function setStance(k, m) { stance[k] = m; applyStance(); }

  let pickTicket = 0;
  async function openPicker(key) {
    const ticket = ++pickTicket;
    const invs = SLOTS.find(s => s[0] === key)[1];
    app.querySelectorAll('.slot').forEach(b => b.classList.toggle('open', b.dataset.slot === key));
    picker.className = 'show';
    picker.innerHTML = '<div class="top"><input type="search" placeholder="' + esc(I.search.replace('{slot}', I.slots[key].toLowerCase())) + '"><button type="button" class="pclear">' + esc(I.remove) + '</button><button type="button" class="pclose" aria-label="' + esc(I.close) + '">✕</button></div><div class="chips"></div><div class="plist"></div><div class="pcount"></div>';
    const all = await loadCatalog();
    if (ticket !== pickTicket) return;                         // a newer picker was opened meanwhile
    const cat = all.filter(r => invs.includes(r[5]) && (WKEY[key] || r[6] === 4) && allowedFor(r, key));
    const input = picker.querySelector('input'), chips = picker.querySelector('.chips'), list = picker.querySelector('.plist');
    let type = null;
    const types = [...new Set(cat.map(typeLabel))].sort((a, b) => a.localeCompare(b));
    const mk = (txt, val) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = txt; b.onclick = () => { type = val; [...chips.children].forEach(c => c.classList.toggle('on', c === b)); render(); }; if (val === null) b.className = 'on'; chips.appendChild(b); };
    if (types.length > 1) { mk(I.all, null); types.forEach(t => mk(t, t)); }
    const render = () => {
      const q = input.value.trim().toLowerCase();
      const rows = cat.filter(r => (type === null || typeLabel(r) === type) && (!q || r[1].toLowerCase().includes(q) || (r[2] || '').toLowerCase().includes(q)))
        .sort((a, b) => b[3] - a[3] || itemName(a).localeCompare(itemName(b)));
      list.innerHTML = '';
      for (const r of rows.slice(0, 120)) {
        const d = document.createElement('div'); d.className = 'row' + (worn[key] && worn[key][0] === r[0] ? ' on' : '');
        d.innerHTML = '<img src="' + iconSrc(r[4]) + '" alt="" loading="lazy"><span class="q' + r[3] + '">' + esc(itemName(r)) + '</span><small>' + (r[10] ? esc(I.lvl) + ' ' + r[10] : '') + '</small>';
        d.onclick = () => wear(key, r); d.onmouseenter = () => tryOn(key, r); list.appendChild(d);
      }
      picker.querySelector('.pcount').textContent = rows.length > 120 ? I.count_more.replace('{n}', 120).replace('{total}', rows.length) : I.count.replace('{n}', rows.length);
    };
    list.onmouseleave = () => tryOn(key, worn[key] || null);   // leaving the list puts the worn item (or nothing) back
    input.oninput = render; render(); input.focus();
    picker.querySelector('.pclear').onclick = () => wear(key, null);
    picker.querySelector('.pclose').onclick = () => { picker.className = ''; app.querySelectorAll('.slot').forEach(b => b.classList.remove('open')); };
  }
  // try-on on hover: the item is shown on the character without being worn (debounced; only the last hover counts)
  let tryTimer = 0, tryTicket = 0;
  function tryOn(key, r) {
    clearTimeout(tryTimer);
    const ticket = ++tryTicket;
    tryTimer = setTimeout(async () => {
      const c = v.char; if (!c || ticket !== tryTicket) return;
      const inv = r ? r[5] : SLOTS.find(s => s[0] === key)[1][0];
      try {
        if (WKEY[key]) await c.setWeapon(WKEY[key], inv, r ? r[8] : 0, r ? (stance[key] === 'hip' && ![13, 21, 22].includes(r[5]) ? 'back' : stance[key]) : 'hand');
        else await c.setEquip(inv, r ? r[8] : 0);
      } catch (e) { console.error(e); }
    }, 140);
  }
  async function wear(key, r) {
    tryTicket++; clearTimeout(tryTimer);
    if (r && WKEY[key] && stance[key] === 'hip' && ![13, 21, 22].includes(r[5])) stance[key] = 'back';
    if (r) worn[key] = r; else delete worn[key];
    drawSlots();
    const c = v.char; if (!c) return;
    const inv = r ? r[5] : SLOTS.find(s => s[0] === key)[1][0];
    try {
      if (WKEY[key]) {
        if (r && r[5] === 17) { delete worn.offhand; drawSlots(); await c.setWeapon('oh', 0, 0); }       // a two-hander leaves no off hand
        await c.setWeapon(WKEY[key], inv, r ? r[8] : 0, r ? modeOf(key) : 'hand');
      } else await c.setEquip(inv, r ? r[8] : 0);
    } catch (e) { log.textContent = I.error + ' ' + e.message; console.error(e); }
    picker.querySelectorAll('.row').forEach(x => x.classList.remove('on'));
    drawStance();
  }

  // ---- customization panel --------------------------------------------------------------------------------------------------
  const optName = (n) => (FR && I.options[n]) || n;
  const isColor = (o) => /Color/.test(o.Name) && o.Choices.length > 1;
  const colorCache = {};
  function avgColor(id, iris) {      // average colour of a texture for the swatches (ignores transparent / near-black / near-white pixels)
    const key = id + (iris ? 'i' : '');
    return colorCache[key] || (colorCache[key] = new Promise((res) => {
      const im = new Image(); im.crossOrigin = 'anonymous';
      im.onload = () => {
        const W = iris ? 24 : 32, H = iris ? 24 : 16, cv = document.createElement('canvas'); cv.width = W; cv.height = H; const x = cv.getContext('2d');
        if (iris) x.drawImage(im, im.width * 0.205, im.height * 0.40, im.width * 0.06, im.width * 0.06, 0, 0, W, H); else x.drawImage(im, 0, 0, W, H);
        const d = x.getImageData(0, 0, W, H).data; let r = 0, g = 0, b = 0, n = 0;
        for (let i = 0; i < d.length; i += 4) { const l = (d[i] + d[i + 1] + d[i + 2]) / 3; if (d[i + 3] > 200 && l > 28 && l < 245) { r += d[i]; g += d[i + 1]; b += d[i + 2]; n++; } }
        res(n ? 'rgb(' + Math.round(r / n) + ',' + Math.round(g / n) + ',' + Math.round(b / n) + ')' : '#555');
      };
      im.onerror = () => res('#555'); im.src = BASE + 'textures/' + id + '.webp';
    }));
  }
  function swatchFile(c, choice) {
    const e = choice.Elements.find(e => e.Material && !e.VariationChoiceID) || choice.Elements.find(e => e.Material);
    const f = e && c.cust.TextureFiles[e.Material.MaterialResourcesID];
    return f && f[0] && f[0].FileDataId;
  }
  // choices that exist in the game for a Forever player (the baked metadata already drops the unlockable / class-locked ones; kept as a safety net)
  const FOREVER_CLASSES = 1 | 2 | 4 | 8 | 16 | 64 | 128 | 256 | 1024;
  const available = (ch) => ch.ReqType !== 2 && ch.ReqType !== 4 && (ch.ClassMask === undefined || ch.ClassMask === -1 || (ch.ClassMask & FOREVER_CLASSES) !== 0);

  function buildOptions(c) {
    const box = $('tmOpts'); box.innerHTML = '';
    const refreshers = [], AL = {}, fix = {};
    for (const o of c.cust.Options) {
      AL[o.Id] = o.Choices.map((ch, i) => i).filter(i => available(o.Choices[i]));
      if (!AL[o.Id].length) AL[o.Id] = [0];
      if (!AL[o.Id].includes(c.choice[o.Id])) fix[o.Id] = AL[o.Id][0];
    }
    if (Object.keys(fix).length) c.setChoices(fix);
    const apply = (o, i) => { if (c !== v.char) return; return c.setChoice(o.Id, i).then(() => refreshers.forEach(f => f())); };
    const colors = c.cust.Options.filter(o => isColor(o) && AL[o.Id].length > 1), others = c.cust.Options.filter(o => !isColor(o) && AL[o.Id].length > 1);
    if (others.length) {
      const h = document.createElement('h3'); h.textContent = I.appearance; box.appendChild(h);
      const grid = document.createElement('div'); grid.className = 'grid'; box.appendChild(grid);
      for (const o of others) {
        const n = AL[o.Id].length, card = document.createElement('div'), nm = document.createElement('div'), row = document.createElement('div');
        const prev = document.createElement('button'), next = document.createElement('button'), val = document.createElement('div'), bar = document.createElement('div'), fill = document.createElement('i');
        card.className = 'card'; nm.className = 'nm'; nm.textContent = optName(o.Name); row.className = 'crow'; val.className = 'val'; bar.className = 'bar'; bar.appendChild(fill);
        prev.type = next.type = 'button'; prev.textContent = '◀'; next.textContent = '▶'; prev.setAttribute('aria-label', I.prev); next.setAttribute('aria-label', I.next);
        const show = () => { const i = c.choice[o.Id], p = AL[o.Id].indexOf(i); val.textContent = o.Choices[i].Name || (I.style + ' ' + (p + 1)); fill.style.width = ((p + 1) / n * 100) + '%'; };
        let busy = false;
        const go = (d) => { if (busy) return; busy = true; apply(o, AL[o.Id][(AL[o.Id].indexOf(c.choice[o.Id]) + d + n) % n]).finally(() => { busy = false; }); };
        prev.onclick = () => go(-1); next.onclick = () => go(1);
        refreshers.push(show); show(); row.append(prev, val, next); card.append(nm, row, bar); grid.appendChild(card);
      }
    }
    if (colors.length) {
      const h = document.createElement('h3'); h.textContent = I.colors; box.appendChild(h);
      for (const o of colors) {
        const wrap = document.createElement('div'), nm = document.createElement('div'), sw = document.createElement('div'), name = document.createElement('b');
        wrap.className = 'opt'; nm.className = 'nm'; sw.className = 'sw';
        const lab = document.createElement('span'); lab.textContent = optName(o.Name); nm.append(lab, name);
        const btns = AL[o.Id].map((i, k) => {
          const ch = o.Choices[i], b = document.createElement('button'); b.type = 'button'; b.title = ch.Name || ('#' + (k + 1)); b.setAttribute('aria-label', b.title); b.onclick = () => apply(o, i); sw.appendChild(b);
          const f = swatchFile(c, ch); if (f) avgColor(f, /Eye Color/.test(o.Name)).then(col => { b.style.background = col; });
          return b;
        });
        const show = () => { const p = AL[o.Id].indexOf(c.choice[o.Id]); btns.forEach((b, k) => b.classList.toggle('on', k === p)); name.textContent = o.Choices[c.choice[o.Id]].Name || ('#' + (p + 1)); };
        refreshers.push(show); show(); wrap.append(nm, sw); box.appendChild(wrap);
      }
    }
    const all = c.cust.Options.filter(o => AL[o.Id].length > 1);        // random / reset act on every option at once (one texture rebuild)
    const setAll = (fn) => { const m = {}; all.forEach(o => { m[o.Id] = fn(o); }); c.setChoices(m).then(() => refreshers.forEach(f => f())); };
    $('tmRnd').onclick = () => setAll(o => AL[o.Id][Math.floor(Math.random() * AL[o.Id].length)]);
    $('tmRst').onclick = () => setAll(o => AL[o.Id][0]);
  }

  app.querySelectorAll('[data-race]').forEach(b => b.onclick = () => { race = b.dataset.race; mark(); pick(chrId()); });
  app.querySelectorAll('[data-sex]').forEach(b => b.onclick = () => { sex = +b.dataset.sex; mark(); pick(chrId()); });
  window.tmPick = (id) => { const r = RACES.find(r => r[1] === id || r[2] === id); race = r[0]; sex = r[2] === id ? 1 : 0; mark(); return pick(id); };
  drawClasses(); drawSlots(); drawStance(); mark(); pick(chrId());
})();
