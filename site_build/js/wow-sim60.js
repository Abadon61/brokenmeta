(function () {
  'use strict';
  var app = document.getElementById('s60App');
  if (!app || !window.Sim60) return;
  var S = window.Sim60;
  var T = JSON.parse(document.getElementById('s60I18n').textContent);
  var base = app.dataset.base, dv = app.dataset.v;
  var SLOT_LABEL = { head: 'Head', neck: 'Neck', shoulder: 'Shoulders', back: 'Back', chest: 'Chest', wrist: 'Wrists', hands: 'Hands', waist: 'Waist', legs: 'Legs', feet: 'Feet', ring1: 'Ring 1', ring2: 'Ring 2', trinket1: 'Trinket 1', trinket2: 'Trinket 2' };
  var SLOT_LABEL_FR = { head: 'Tête', neck: 'Cou', shoulder: 'Épaules', back: 'Dos', chest: 'Torse', wrist: 'Poignets', hands: 'Mains', waist: 'Taille', legs: 'Jambes', feet: 'Pieds', ring1: 'Anneau 1', ring2: 'Anneau 2', trinket1: 'Bijou 1', trinket2: 'Bijou 2' };
  var fr = app.dataset.lang === 'fr';
  var RACES = [['human', 'Human', 'Humain'], ['dwarf', 'Dwarf', 'Nain'], ['nightelf', 'Night Elf', 'Elfe de la nuit'], ['gnome', 'Gnome', 'Gnome'],
    ['orc', 'Orc', 'Orc'], ['undead', 'Undead', 'Mort-vivant'], ['tauren', 'Tauren', 'Tauren'], ['troll', 'Troll', 'Troll']];
  var $ = function (id) { return document.getElementById(id); };
  function el(tag, attrs) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { if (k === 'text') e.textContent = attrs[k]; else if (k === 'html') e.innerHTML = attrs[k]; else e.setAttribute(k, attrs[k]); });
    for (var i = 2; i < arguments.length; i++) { var c = arguments[i]; if (c) e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); }
    return e;
  }
  function fmt(s, o) { return s.replace(/\{(\w+)\}/g, function (_, k) { return o[k]; }); }

  var state = { pool: null, data: null, items: null, prof: null, simPool: null, lastOpt: null, tdata: null, ranks: {} };

  // ---------- workers ----------
  function getPool() {
    if (!state.simPool) {
      var n = Math.max(1, Math.min(8, (navigator.hardwareConcurrency || 4) - 1));
      var workers = [], pending = {}, id = 1;
      for (var i = 0; i < n; i++) {
        var w = new Worker(app.dataset.worker);
        w.onmessage = function (ev) { var p = pending[ev.data.id]; if (p) { if (ev.data.progress && p.onProgress) p.onProgress(ev.data.progress); if (!ev.data.progress) { delete pending[ev.data.id]; p.resolve(ev.data); } } };
        workers.push(w);
      }
      function call(w, msg, onProgress) { return new Promise(function (resolve) { msg.id = id++; pending[msg.id] = { resolve: resolve, onProgress: onProgress }; w.postMessage(msg); }); }
      var ready = Promise.all(workers.map(function (w) { return call(w, { kind: 'init', data: state.data }); }));
      state.simPool = {
        size: n,
        run: function (job, iterations, seedBase, onProgress) {
          return ready.then(function () {
            var chunk = 250, chunks = [], parts = [], idx = 0, done = 0;
            for (var off = 0; off < iterations; off += chunk) chunks.push([off, Math.min(chunk, iterations - off)]);
            return Promise.all(workers.map(function (w) {
              function next() {
                if (idx >= chunks.length) return Promise.resolve();
                var c = chunks[idx++];
                return call(w, { kind: 'run', job: job, iterations: c[1], seedBase: seedBase + c[0] }).then(function (r) { parts.push(r.raw); done += c[1]; if (onProgress) onProgress(done / iterations); return next(); });
              }
              return next();
            })).then(function () { return S.finalize(S.mergeRaw(parts), job.fightLen); });
          });
        },
        one: function (msg, onProgress) { return ready.then(function () { return call(workers[0], msg, onProgress); }); },
      };
    }
    return state.simPool;
  }

  // ---------- form ----------
  function itemLabel(it) { return it.name + ' (' + (it.zone || '') + (it.req ? ', ' + it.req : '') + ')'; }
  function itemScore(it) {
    var s = it.st || {};
    return (s.str || 0) * 2 + (s.agi || 0) * 0.6 + (s.atkpwr || 0) + (s.critstrkrtng || 0) * 1.4 + (s.hitrtng || 0) * 2.6 + (s.dps || 0) * 6;
  }
  function fillSelect(sel, items, emptyLabel) {
    sel.innerHTML = '';
    sel.appendChild(el('option', { value: '', text: emptyLabel }));
    items.forEach(function (it) { sel.appendChild(el('option', { value: String(it.id), text: itemLabel(it) })); });
  }
  function sortedFor(slot) {
    return state.pool.forSlot(slot, 'warrior', 60).slice().sort(function (a, b) { return itemScore(b) - itemScore(a); });
  }
  function weaponLists(spec) {
    var w = state.pool.weapons('warrior', 60);
    var by = function (a, b) { return itemScore(b) - itemScore(a); };
    var oneH = w.oneHand.concat(w.mainHand).sort(by), off = w.oneHand.concat(w.offHand).sort(by), two = w.twoHand.sort(by);
    return { mh: oneH, oh: off, th: two };
  }

  function buildForm() {
    var gearBox = $('s60Gear'); gearBox.innerHTML = '';
    var labels = fr ? SLOT_LABEL_FR : SLOT_LABEL;
    S.EQUIP_SLOTS.forEach(function (slot) {
      var sel = el('select', { id: 's60g_' + slot });
      fillSelect(sel, sortedFor(slot), T.empty);
      gearBox.appendChild(el('label', { class: 's60-row' }, el('span', { text: labels[slot] }), sel));
    });
    ['mh', 'oh', 'th'].forEach(function (k) {
      var sel = el('select', { id: 's60w_' + k });
      gearBox.appendChild(el('label', { class: 's60-row', id: 's60rw_' + k }, el('span', { text: T[k] }), sel));
    });
    refreshWeapons();
    var rs = $('s60Race'); RACES.forEach(function (r) { rs.appendChild(el('option', { value: r[0], text: fr ? r[2] : r[1] })); });
    var addGroup = function (box, defs, preset, group) {
      Object.keys(defs).forEach(function (k) {
        var d = defs[k], id = 's60b_' + group + '_' + k;
        var cb = el('input', { type: 'checkbox', id: id }); if (preset.indexOf(k) >= 0) cb.checked = true;
        box.appendChild(el('label', { class: 's60-check' }, cb, ' ' + d.name, d.assumed ? el('em', { class: 's60-assumed', text: ' · ' + T.assumed }) : null));
      });
    };
    addGroup($('s60Buffs'), S.BUFFS, S.PRESET_RAID.buffs, 'buff');
    addGroup($('s60Cons'), S.CONSUMABLES, S.PRESET_RAID.consumables, 'cons');
    addGroup($('s60Debuffs'), S.DEBUFFS, S.PRESET_RAID.debuffs, 'debuff');
    // sensible defaults: best-scoring gear per slot and weapons
    S.EQUIP_SLOTS.forEach(function (slot) {
      var list = sortedFor(slot); var used = {};
      S.EQUIP_SLOTS.forEach(function (s2) { var v = $('s60g_' + s2).value; if (v) used[v] = 1; });
      for (var i = 0; i < list.length; i++) if (!used[list[i].id]) { $('s60g_' + slot).value = String(list[i].id); break; }
    });
    pickDefaultWeapons();
  }
  function curSpec() { return $('s60Spec').value; }
  function refreshWeapons() {
    var L = weaponLists(curSpec()), arms = curSpec() === 'warrior_arms';
    fillSelect($('s60w_mh'), L.mh, T.empty); fillSelect($('s60w_oh'), L.oh, T.empty); fillSelect($('s60w_th'), L.th, T.empty);
    $('s60rw_mh').hidden = arms; $('s60rw_oh').hidden = arms; $('s60rw_th').hidden = !arms;
  }
  function pickDefaultWeapons() {
    var L = weaponLists(curSpec());
    if (curSpec() === 'warrior_arms') { if (L.th[0]) $('s60w_th').value = String(L.th[0].id); }
    else {
      if (L.mh[0]) $('s60w_mh').value = String(L.mh[0].id);
      var o = L.oh.filter(function (i) { return String(i.id) !== $('s60w_mh').value; })[0]; if (o) $('s60w_oh').value = String(o.id);
    }
  }

  function checked(group, defs) { return Object.keys(defs).filter(function (k) { var c = $('s60b_' + group + '_' + k); return c && c.checked; }); }
  function num(id) { var v = parseFloat($(id).value); return isFinite(v) ? v : null; }

  function collect() {
    var gear = [];
    S.EQUIP_SLOTS.forEach(function (slot) {
      var v = $('s60g_' + slot).value; if (!v) return;
      var it = state.pool.byId.get(parseInt(v, 10)); if (it) gear.push({ slot: slot, id: it.id, name: it.name, st: it.st });
    });
    var weapons = [], arms = curSpec() === 'warrior_arms';
    function wp(k, off) { var v = $('s60w_' + k).value; if (!v) return; weapons.push(S.toWeapon(state.pool.byId.get(parseInt(v, 10)), off)); }
    if (arms) wp('th', false); else { wp('mh', false); wp('oh', true); }
    var spec = { class: 'warrior', race: $('s60Race').value, gear: gear, weapons: weapons,
      buffs: checked('buff', S.BUFFS), consumables: checked('cons', S.CONSUMABLES), debuffs: checked('debuff', S.DEBUFFS),
      targetArmor: num('s60Armor') == null ? 3731 : num('s60Armor'), executeFrac: $('s60Exec').checked ? 0.2 : 0 };
    var ap = num('s60Ap'), cr = num('s60Crit'), hi = num('s60Hit');
    if (ap != null && cr != null && hi != null) spec.totals = { ap: ap, crit: cr / 100, hit: hi / 100 };
    var build = Object.assign(S.ranksToBuild('warrior', state.tdata, state.ranks), { executePhase: $('s60Exec').checked, useDeathWish: $('s60DW').checked, useRecklessness: $('s60Reck').checked, enrageUptime: num('s60Enrage') || 0 });
    return { spec: spec, build: build };
  }
  function makeJob(c) {
    var ch = S.buildCharacter(c.spec);
    return { job: { player: ch.player, target: ch.target, fightLen: num('s60Len') || 180, kitName: curSpec(), kitBuild: c.build }, ch: ch };
  }

  // ---------- results ----------
  function status(msg) { $('s60Status').textContent = msg || ''; }
  function bar(p) { var b = $('s60Bar'); b.hidden = p == null; if (p != null) b.firstChild.style.width = Math.round(p * 100) + '%'; }
  function renderRun(r, ch, ms) {
    var box = $('s60Result'); box.hidden = false;
    var rows = Object.keys(r.breakdown).map(function (k) { return [k, r.breakdown[k]]; }).filter(function (x) { return x[1].dps > 0; }).sort(function (a, b) { return b[1].dps - a[1].dps; });
    var tr = rows.map(function (x) {
      return '<tr><td data-first>' + x[0] + '</td><td class="nums">' + x[1].dps.toFixed(1) + '</td><td class="nums">' + (100 * x[1].dps / r.mean).toFixed(1) + ' %</td><td class="nums">' + x[1].casts.toFixed(1) +
        '</td><td class="nums">' + x[1].crits.toFixed(1) + '</td><td class="nums">' + x[1].misses.toFixed(1) + '</td><td class="nums">' + x[1].dodges.toFixed(1) + '</td></tr>';
    }).join('');
    var up = Object.keys(r.uptimes).filter(function (k) { return r.uptimes[k] > 0; }).map(function (k) { return k + ' ' + (r.uptimes[k] * 100).toFixed(0) + ' %'; }).join(' · ');
    var sm = ch.summary;
    box.innerHTML = '<p class="s60-dps"><b>' + r.mean.toFixed(1) + '</b> ' + T.dps + ' <span>± ' + r.sem.toFixed(2) + ' (' + r.iterations + ')</span></p>' +
      '<p class="wow-note">AP ' + Math.round(sm.ap) + ' · ' + T.crit + ' ' + (sm.crit * 100).toFixed(1) + ' · ' + T.hit + ' ' + (sm.hit * 100).toFixed(1) + ' · ' + T.armor + ' ' + Math.round(sm.armor) + '</p>' +
      '<div class="wow-table-wrap"><table class="wow-table"><thead><tr><th>' + T.ability + '</th><th>DPS</th><th>' + T.share + '</th><th>' + T.casts + '</th><th>' + T.crits + '</th><th>' + T.misses + '</th><th>' + T.dodges + '</th></tr></thead><tbody>' + tr + '</tbody></table></div>' +
      (up ? '<p class="wow-note">' + T.uptime + ' : ' + up + '</p>' : '');
    status(fmt(T.js.done, { s: (ms / 1000).toFixed(1), rate: Math.round(r.iterations / (ms / 1000)) }) + ' · ' + fmt(T.js.workers, { n: getPool().size }));
  }

  function setBusy(b) { ['s60Run', 's60Weights', 's60Opt'].forEach(function (id) { $(id).disabled = b; }); }

  function doRun() {
    var c = collect(), j = makeJob(c), iters = Math.max(100, num('s60Iters') || 5000), t0 = performance.now();
    setBusy(true); status(T.running); bar(0);
    getPool().run(j.job, iters, 1, bar).then(function (r) { renderRun(r, j.ch, performance.now() - t0); }).catch(function (e) { status(String(e)); }).then(function () { setBusy(false); bar(null); });
  }
  function withStats(job, delta) {
    var stats = Object.assign({}, job.player.stats);
    Object.keys(delta).forEach(function (k) { stats[k] = (stats[k] || 0) + delta[k]; });
    return Object.assign({}, job, { player: Object.assign({}, job.player, { stats: stats }) });
  }
  function doWeights() {
    var c = collect(), j = makeJob(c), iters = Math.max(500, Math.min(30000, num('s60Iters') || 4000)), t0 = performance.now();
    setBusy(true); status(T.js.weightsRunning); bar(0);
    var probes = [['ap', { ap: 40 }], ['crit', { crit: 0.01 }], ['hit', { hit: 0.01 }], ['haste', { haste: 0.01 }]], res = {}, step = 0;
    function neg(d) { var o = {}; Object.keys(d).forEach(function (k) { o[k] = -d[k]; }); return o; }
    var p = Promise.resolve();
    probes.forEach(function (pr) {
      p = p.then(function () { return getPool().run(withStats(j.job, pr[1]), iters, 1); })
        .then(function (hi) { bar((++step) / 8); return getPool().run(withStats(j.job, neg(pr[1])), iters, 1).then(function (lo) { bar((++step) / 8); res[pr[0]] = (hi.mean - lo.mean) / 2; }); });
    });
    p.then(function () {
      var apPer = res.ap / 40, box = $('s60Weights2'); box.hidden = false;
      box.innerHTML = '<h3 class="ad-h3">' + T.w_title + '</h3><ul class="ms-limits"><li>' + T.w_crit + ' = <b>' + (res.crit / apPer).toFixed(1) + '</b> AP</li><li>' + T.w_hit + ' = <b>' + (res.hit / apPer).toFixed(1) + '</b> AP</li><li>' + T.w_haste + ' = <b>' + (res.haste / apPer).toFixed(1) + '</b> AP</li></ul>';
      var ms = performance.now() - t0; status(fmt(T.js.done, { s: (ms / 1000).toFixed(1), rate: Math.round(iters * 8 / (ms / 1000)) }));
    }).catch(function (e) { status(String(e)); }).then(function () { setBusy(false); bar(null); });
  }
  function doOptimize() {
    var c = collect(), jj = makeJob(c), iters = Math.max(200, Math.min(2000, Math.round((num('s60Iters') || 5000) / 10))), t0 = performance.now();
    setBusy(true); status(fmt(T.js.optProgress, { slot: '…' })); bar(null);
    var chara = Object.assign({}, c.spec, { gear: [] }), wmode = curSpec() === 'warrior_arms' ? '2h' : 'dw';
    function jobFor(spec) { var ch = S.buildCharacter(spec); return Object.assign({}, jj.job, { player: ch.player, target: ch.target }); }
    function evaluate(spec) { return getPool().run(jobFor(spec), iters, 11).then(function (r) { return r.mean; }); }
    function getWeights(spec) {
      var job = jobFor(spec), n = 1200;
      function diff(d) { return Promise.all([getPool().run(withStats(job, d.up), n, 11), getPool().run(withStats(job, d.dn), n, 11)]).then(function (r) { return (r[0].mean - r[1].mean) / 2; }); }
      return Promise.all([diff({ up: { ap: 40 }, dn: { ap: -40 } }), diff({ up: { crit: 0.01 }, dn: { crit: -0.01 } }), diff({ up: { hit: 0.01 }, dn: { hit: -0.01 } }), diff({ up: { haste: 0.01 }, dn: { haste: -0.01 } })])
        .then(function (r) { var apPer = r[0] / 40; return { agi: 0.05 * r[1] / apPer, crit: r[1] / apPer, hit: r[2] / apPer, haste: r[3] / apPer }; });
    }
    S.optimizeGearAsync({ pool: state.pool, character: chara, weaponMode: wmode, evaluate: evaluate, getWeights: getWeights, prefilter: 4, maxPasses: 3,
      onProgress: function (p) { status(fmt(T.js.optProgress, { slot: p.slot }) + ' ' + p.dps.toFixed(1) + ' DPS'); } }).then(function (res) {
      state.lastOpt = res;
      var box = $('s60Opt2'); box.hidden = false;
      var list = res.weapons.concat(res.gear).map(function (g) { return '<li>' + g.slot + ' : ' + g.name + '</li>'; }).join('');
      box.innerHTML = '<h3 class="ad-h3">' + T.o_title + ' : ' + res.dps.toFixed(1) + ' DPS</h3><ul class="ms-limits">' + list + '</ul><button type="button" class="ms-btn" id="s60Apply">' + T.apply + '</button><p class="wow-note">' + T.o_note + '</p>';
      $('s60Apply').addEventListener('click', function () {
        S.EQUIP_SLOTS.forEach(function (s) { $('s60g_' + s).value = ''; });
        res.gear.forEach(function (g) { var sel = $('s60g_' + g.slot); if (sel) sel.value = String(g.id); });
        ['mh', 'oh', 'th'].forEach(function (k) { $('s60w_' + k).value = ''; });
        res.weapons.forEach(function (g) { var sel = $('s60w_' + g.slot); if (sel) sel.value = String(g.id); });
      });
      status(fmt(T.js.optDone, { s: ((performance.now() - t0) / 1000).toFixed(1) }));
    }).catch(function (e) { status(String(e)); }).then(function () { setBusy(false); });
  }

  // ---------- talents ----------
  var TREE_NAMES = { arms: fr ? 'Armes' : 'Arms', fury: fr ? 'Fureur' : 'Fury', protection: fr ? 'Protection' : 'Protection' };
  function talentStatus() {
    var v = S.validateRanks(state.tdata, state.ranks), st = $('s60TalentStatus');
    st.textContent = (v.ok ? fmt(T.t_ok, { pts: v.total, a: v.bySpec[0], b: v.bySpec[1], c: v.bySpec[2] }) : fmt(T.t_bad, { err: v.errors.slice(0, 2).join(' · ') }));
    st.className = 'wow-note' + (v.ok ? '' : ' s60-warn');
  }
  function renderTalents() {
    var box = $('s60Talents'); box.innerHTML = '';
    var names = S.NAME_TO_KEY.warrior;
    state.tdata.specs.forEach(function (sp) {
      var rows = sp.talents.filter(function (t) { return names[t.name.en]; }).sort(function (a, b) { return a.row - b.row || a.col - b.col; });
      if (!rows.length) return;
      var col = el('div', { class: 's60-checks' }, el('b', { text: TREE_NAMES[sp.id] || sp.id }));
      rows.forEach(function (t) {
        var inp = el('input', { type: 'number', min: '0', max: String(t.max_rank), step: '1', value: String(state.ranks[t.id] || 0), class: 's60-rank' });
        inp.addEventListener('change', function () {
          var v = Math.max(0, Math.min(t.max_rank, parseInt(inp.value, 10) || 0)); inp.value = String(v);
          if (v) state.ranks[t.id] = v; else delete state.ranks[t.id]; talentStatus();
        });
        col.appendChild(el('label', { class: 's60-check s60-talent', title: (t.desc[fr ? 'fr' : 'en'] || [''])[0] }, inp, ' ' + t.name[fr ? 'fr' : 'en'] + ' / ' + t.max_rank));
      });
      box.appendChild(col);
    });
    talentStatus();
  }
  function loadPreset() { state.ranks = S.ranksFromNames(state.tdata, S.PRESETS[curSpec()]); renderTalents(); }
  function importLink() {
    var r = S.parseShareHash(state.tdata, $('s60TalentLink').value);
    var st = $('s60TalentStatus');
    if (r.error) { st.textContent = T.t_link_bad; st.className = 'wow-note s60-warn'; return; }
    state.ranks = r.ranks; renderTalents();
    if (!r.revMatches) { st.textContent = T.t_rev + ' ' + st.textContent; }
  }

  // ---------- boot ----------
  Promise.all(['items.json', 'proficiency.json', 'spells60.json', 'talents.json'].map(function (f) { return fetch(base + f + '?v=' + dv).then(function (r) { return r.json(); }); })).then(function (all) {
    state.items = all[0]; state.prof = all[1]; state.data = all[2]; state.tdata = all[3].warrior;
    state.pool = new S.ItemPool(all[0], all[1]);
    buildForm(); loadPreset();
    $('s60Spec').addEventListener('change', function () { refreshWeapons(); pickDefaultWeapons(); loadPreset(); });
    $('s60Preset').addEventListener('click', loadPreset);
    $('s60TalentLink').addEventListener('change', importLink);
    $('s60Run').addEventListener('click', doRun);
    $('s60Weights').addEventListener('click', doWeights);
    $('s60Opt').addEventListener('click', doOptimize);
    app.classList.add('ready'); $('s60Loading').hidden = true; $('s60Form').hidden = false;
  }).catch(function (e) { $('s60Loading').textContent = 'Error: ' + e; });
})();
