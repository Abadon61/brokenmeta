(function () {
  'use strict';
  var app = document.getElementById('s60App');
  if (!app || !window.Sim60) return;
  var S = window.Sim60;
  var T = JSON.parse(document.getElementById('s60I18n').textContent);
  var base = app.dataset.base, dv = app.dataset.v;
  var SLOT_LABEL = { shield: 'Shield', held: 'Held in off-hand', head: 'Head', neck: 'Neck', shoulder: 'Shoulders', back: 'Back', chest: 'Chest', wrist: 'Wrists', hands: 'Hands', waist: 'Waist', legs: 'Legs', feet: 'Feet', ring1: 'Ring 1', ring2: 'Ring 2', trinket1: 'Trinket 1', trinket2: 'Trinket 2' };
  var SLOT_LABEL_FR = { shield: 'Bouclier', held: 'Tenu en main gauche', head: 'Tête', neck: 'Cou', shoulder: 'Épaules', back: 'Dos', chest: 'Torse', wrist: 'Poignets', hands: 'Mains', waist: 'Taille', legs: 'Jambes', feet: 'Pieds', ring1: 'Anneau 1', ring2: 'Anneau 2', trinket1: 'Bijou 1', trinket2: 'Bijou 2' };
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

  var SPECS = { warrior_fury: { cls: 'warrior', mode: 'dw' }, warrior_arms: { cls: 'warrior', mode: '2h' }, rogue_combat: { cls: 'rogue', mode: 'dw' }, rogue_assassination: { cls: 'rogue', mode: 'dw' }, rogue_subtlety: { cls: 'rogue', mode: 'dw' },
    warrior_protection: { cls: 'warrior', mode: 'tank', variant: 'protection' }, paladin_protection: { cls: 'paladin', mode: 'tank', variant: 'protection' }, druid_bear: { cls: 'druid', mode: 'stick', variant: 'bear' },
    paladin_retribution: { cls: 'paladin', mode: '2h' }, shaman_enhancement: { cls: 'shaman', mode: '2h', variant: 'enhancement' }, druid_feral: { cls: 'druid', mode: 'stick', variant: 'feral' },
    priest_shadow: { cls: 'priest', mode: 'caster' }, shaman_elemental: { cls: 'shaman', mode: 'caster' }, druid_balance: { cls: 'druid', mode: 'caster' },
    hunter_melee: { cls: 'hunter', mode: 'dw', variant: 'melee' },
    hunter_marksmanship: { cls: 'hunter', mode: 'ranged' }, hunter_beastmastery: { cls: 'hunter', mode: 'ranged' },
    warlock_affliction: { cls: 'warlock', mode: 'caster' }, warlock_destruction: { cls: 'warlock', mode: 'caster' }, warlock_demonology: { cls: 'warlock', mode: 'caster' },
    mage_fire: { cls: 'mage', mode: 'caster' }, mage_frost: { cls: 'mage', mode: 'caster' }, mage_arcane: { cls: 'mage', mode: 'caster' } };
  var CASTERS = { mage: 1, warlock: 1 };
  function isCaster() { return curMode() === 'caster'; }
  function isRanged() { return curMode() === 'ranged'; }
  function isStick() { return curMode() === 'stick'; }
  function isTank() { return curSpec() === 'warrior_protection' || curSpec() === 'paladin_protection' || curSpec() === 'druid_bear'; }
  function slots() { return S.slotsFor(curMode()); }
  // tank objective: threat per second, damage taken, or both (the optimizer and the stat weights use it instead of the DPS)
  function objective(r) {
    if (!isTank() || !r.counters) return r.mean;
    var len = num('s60Len') || 180, thr = (r.counters.threat || 0) / len, dt = (r.counters.dmgTaken || 0) / len, raw = (num('s60BossDmg') || 9000) / (num('s60BossSpeed') || 2), o = $('s60Obj').value;
    return o === 'threat' ? thr : o === 'survival' ? raw - dt : Math.sqrt(Math.max(0, thr) * Math.max(0, raw - dt));
  }
  function curVariant() { return SPECS[curSpec()].variant; }
  function unit() { return isCaster() ? (fr ? 'PS' : 'SP') : (fr ? 'PA' : 'AP'); }
  function curSpec() { return $('s60Spec').value; }
  function curCls() { return SPECS[curSpec()].cls; }
  function curMode() { return SPECS[curSpec()].mode; }
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
    if (isTank()) return ((s.armor || 0) + (s.armorbonus || 0)) * 0.02 + (s.sta || 0) * 0.8 + (s.defrtng || 0) * 2 + (s.str || 0) * 0.6 + (s.agi || 0) * 0.6 + (s.atkpwr || 0) * 0.3 + (s.hitrtng || 0) * 0.8 + (s.critstrkrtng || 0) * 0.4 + (s.dps || 0) * 6;
    if (isRanged()) return (s.agi || 0) * 1.6 + (s.atkpwr || 0) + (s.int || 0) * 0.2 + (s.critstrkrtng || 0) * 1.4 + (s.hitrtng || 0) * 2.6 + (s.dps || 0) * 6;
    if (isCaster()) return (s.splpwr || 0) + (s.spldmg || 0) + (s.int || 0) * 0.5 + (s.critstrkrtng || 0) * 0.9 + (s.hitrtng || 0) * 1.5 + (s.manargn || 0) * 1.5 + (s.spi || 0) * 0.15;
    return (s.str || 0) * 2 + (s.agi || 0) * 0.6 + (s.atkpwr || 0) + (s.critstrkrtng || 0) * 1.4 + (s.hitrtng || 0) * 2.6 + (s.dps || 0) * 6;
  }
  function fillSelect(sel, items, emptyLabel) {
    sel.innerHTML = '';
    sel.appendChild(el('option', { value: '', text: emptyLabel }));
    items.forEach(function (it) { sel.appendChild(el('option', { value: String(it.id), text: itemLabel(it) })); });
  }
  function sortedFor(slot) {
    return state.pool.forSlot(slot, curCls(), 60).slice().sort(function (a, b) { return itemScore(b) - itemScore(a); });
  }
  function weaponLists(spec) {
    var w = state.pool.weapons(curCls(), 60);
    var by = function (a, b) { return itemScore(b) - itemScore(a); };
    var oneH = w.oneHand.concat(w.mainHand).sort(by), off = w.oneHand.concat(w.offHand).sort(by), two = w.twoHand.sort(by);
    return { mh: oneH, oh: off, th: isRanged() || isStick() ? two.concat(oneH) : two, rng: w.ranged.slice().sort(by) };
  }

  function buildGearSelects() {
    var gearBox = $('s60Gear'); gearBox.innerHTML = '';
    var labels = fr ? SLOT_LABEL_FR : SLOT_LABEL;
    slots().forEach(function (slot) {
      var sel = el('select', { id: 's60g_' + slot });
      fillSelect(sel, sortedFor(slot), T.empty);
      gearBox.appendChild(el('label', { class: 's60-row' }, el('span', { text: labels[slot] }), sel));
    });
    ['mh', 'oh', 'th', 'rng'].forEach(function (k) {
      var sel = el('select', { id: 's60w_' + k });
      gearBox.appendChild(el('label', { class: 's60-row', id: 's60rw_' + k }, el('span', { text: T[k] }), sel));
    });
    refreshWeapons();
    // sensible defaults: best-scoring gear per slot and weapons
    slots().forEach(function (slot) {
      var list = sortedFor(slot); var used = {};
      slots().forEach(function (s2) { var v = $('s60g_' + s2).value; if (v) used[v] = 1; });
      for (var i = 0; i < list.length; i++) if (!used[list[i].id]) { $('s60g_' + slot).value = String(list[i].id); break; }
    });
    pickDefaultWeapons();
  }

  function buildForm() {
    buildGearSelects();
    var rs = $('s60Race'); RACES.forEach(function (r) { rs.appendChild(el('option', { value: r[0], text: fr ? r[2] : r[1] })); });
    var addGroup = function (box, defs, preset, group) {
      Object.keys(defs).forEach(function (k) {
        var d = defs[k], id = 's60b_' + group + '_' + k;
        var cb = el('input', { type: 'checkbox', id: id }); if (preset.indexOf(k) >= 0) cb.checked = true;
        box.appendChild(el('label', { class: 's60-check' }, cb, ' ' + d.name, d.assumed ? el('em', { class: 's60-assumed', text: ' · ' + T.assumed }) : null));
      });
    };
    addGroup($('s60Buffs'), S.BUFFS, [], 'buff');
    addGroup($('s60Cons'), S.CONSUMABLES, [], 'cons');
    addGroup($('s60Debuffs'), S.DEBUFFS, [], 'debuff');
    applyRaidPreset();
  }
  // default raid buffs follow the class family (melee vs caster)
  function applyRaidPreset() {
    var p = isCaster() ? S.PRESET_CASTER : isRanged() ? S.PRESET_HUNTER : S.PRESET_RAID;
    [['buff', S.BUFFS, p.buffs], ['cons', S.CONSUMABLES, p.consumables], ['debuff', S.DEBUFFS, p.debuffs]].forEach(function (g) {
      Object.keys(g[1]).forEach(function (k) { var c = $('s60b_' + g[0] + '_' + k); if (c) c.checked = g[2].indexOf(k) >= 0; });
    });
  }
  function refreshWeapons() {
    var L = weaponLists(curSpec()), arms = curMode() === '2h', cast = curMode() === 'caster';
    fillSelect($('s60w_mh'), L.mh, T.empty); fillSelect($('s60w_oh'), L.oh, T.empty); fillSelect($('s60w_th'), L.th, T.empty); fillSelect($('s60w_rng'), L.rng, T.empty);
    $('s60rw_mh').hidden = arms || cast || isRanged() || isStick(); $('s60rw_oh').hidden = arms || cast || isRanged() || isStick() || curMode() === 'tank'; $('s60rw_th').hidden = !(arms || cast || isRanged() || isStick()); $('s60rw_rng').hidden = !isRanged();
  }
  function pickDefaultWeapons() {
    var L = weaponLists(curSpec());
    if (isRanged()) { if (L.rng[0]) $('s60w_rng').value = String(L.rng[0].id); if (L.th[0]) $('s60w_th').value = String(L.th[0].id); }
    else if (curMode() === 'tank') { if (L.mh[0]) $('s60w_mh').value = String(L.mh[0].id); }
    else if (curMode() === '2h' || curMode() === 'caster' || isStick()) { if (L.th[0]) $('s60w_th').value = String(L.th[0].id); }
    else {
      if (L.mh[0]) $('s60w_mh').value = String(L.mh[0].id);
      var o = L.oh.filter(function (i) { return String(i.id) !== $('s60w_mh').value; })[0]; if (o) $('s60w_oh').value = String(o.id);
    }
  }

  function checked(group, defs) { return Object.keys(defs).filter(function (k) { var c = $('s60b_' + group + '_' + k); return c && c.checked; }); }
  function num(id) { var v = parseFloat($(id).value); return isFinite(v) ? v : null; }

  function collect() {
    var gear = [];
    slots().forEach(function (slot) {
      var v = $('s60g_' + slot).value; if (!v) return;
      var it = state.pool.byId.get(parseInt(v, 10)); if (it) gear.push({ slot: slot, id: it.id, name: it.name, st: it.st });
    });
    var weapons = [], arms = curMode() === '2h';
    function wp(k, off) { var v = $('s60w_' + k).value; if (!v) return; weapons.push(S.toWeapon(state.pool.byId.get(parseInt(v, 10)), off)); }
    if (isCaster()) {
      var wv = $('s60w_th').value; if (wv) { var wi = state.pool.byId.get(parseInt(wv, 10)); if (wi) gear.push({ slot: 'th', id: wi.id, name: wi.name, st: wi.st }); }
    } else if (isRanged() || isStick()) {
      var tv = $('s60w_th').value; if (tv) { var ti = state.pool.byId.get(parseInt(tv, 10)); if (ti) gear.push({ slot: 'th', id: ti.id, name: ti.name, st: ti.st }); }
      if (isRanged()) wp('rng', false);
    } else if (curMode() === 'tank') { wp('mh', false);
    } else if (arms) wp('th', false); else { wp('mh', false); wp('oh', true); }
    var spec = { class: curCls(), variant: curVariant(), base: readBase(), effects: $('s60Fx') && $('s60Fx').checked ? state.effects : null, race: $('s60Race').value, gear: gear, weapons: weapons,
      buffs: checked('buff', S.BUFFS), consumables: checked('cons', S.CONSUMABLES), debuffs: checked('debuff', S.DEBUFFS),
      boss: { dmg: num('s60BossDmg') || 9000, speed: num('s60BossSpeed') || 2 }, targetArmor: num('s60Armor') == null ? 3731 : num('s60Armor'), executeFrac: $('s60Exec').checked ? 0.2 : 0 };
    var ap = num('s60Ap'), cr = num('s60Crit'), hi = num('s60Hit');
    if (ap != null && cr != null && hi != null) spec.totals = isCaster() ? { sp: ap, crit: cr / 100, hit: hi / 100 } : { ap: ap, crit: cr / 100, hit: hi / 100 };
    if (state.impWeapons) spec.weapons = state.impWeapons;
    var build = Object.assign(S.ranksToBuild(curCls(), state.tdata, state.ranks), { useCooldowns: $('s60CD').checked, useGem: $('s60Gem').checked, pet: isRanged() ? $('s60HPet').value : $('s60Pet').value, shots: $('s60Shots').value, aspect: $('s60Aspect').checked, quiver: $('s60Quiver').checked, sacrifice: $('s60Sac').value, curse: $('s60Curse').value, innervate: $('s60Inn').checked, movement: (num('s60Move') || 0) / 100, executePhase: $('s60Exec').checked, useDeathWish: $('s60DW').checked, useRecklessness: $('s60Reck').checked, enrageUptime: num('s60Enrage') || 0 });
    return { spec: spec, build: build };
  }
  function makeJob(c) {
    var ch = S.buildCharacter(c.spec);
    return { job: { player: ch.player, target: ch.target, fightLen: num('s60Len') || 180, kitName: curSpec(), kitBuild: c.build }, ch: ch };
  }

  // ---------- base stats (editable) ----------
  var BASE_KEYS = [['str', 'Str'], ['agi', 'Agi'], ['sta', 'Sta'], ['int', 'Int'], ['spi', 'Spi']];
  function fillBase() {
    var h = S.BASE_L60_HUMAN[curCls()] || {}, m = S.RACE_MODS[$('s60Race').value] || {};
    BASE_KEYS.forEach(function (k) { $('s60base_' + k[0]).value = String((h[k[0]] || 0) + (m[k[0]] || 0)); });
  }
  function readBase() {
    var o = {}; BASE_KEYS.forEach(function (k) { o[k[0]] = parseFloat($('s60base_' + k[0]).value) || 0; }); return o;
  }
  function showClassOptions() {
    var cls = curCls();
    Array.prototype.forEach.call(document.querySelectorAll('[data-cls]'), function (e) { e.hidden = e.dataset.cls.split(' ').indexOf(cls) < 0; });
    Array.prototype.forEach.call(document.querySelectorAll('[data-tank]'), function (e) { e.hidden = !isTank(); });
    var lab = $('s60ApLabel'); if (lab) lab.textContent = isCaster() ? T.sp : T.ap;
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
    var tk = isTank() && r.counters ? tankBlock(r, ch) : '';
    box.innerHTML = tk + '<p class="s60-dps"><b>' + r.mean.toFixed(1) + '</b> ' + T.dps + ' <span>± ' + r.sem.toFixed(2) + ' (' + r.iterations + ')</span></p>' +
      (isCaster() ? '<p class="wow-note">' + unit() + ' ' + Math.round(sm.sp) + ' · ' + T.crit + ' ' + (sm.crit * 100).toFixed(1) + ' · ' + T.hit + ' ' + (sm.hit * 100).toFixed(1) + ' · Mana ' + Math.round(sm.mana) + ' · MP5 ' + Math.round(sm.mp5) + '</p>' : '<p class="wow-note">AP ' + Math.round(sm.ap) + ' · ' + T.crit + ' ' + (sm.crit * 100).toFixed(1) + ' · ' + T.hit + ' ' + (sm.hit * 100).toFixed(1) + ' · ' + T.armor + ' ' + Math.round(sm.armor) + '</p>') +
      '<div class="wow-table-wrap"><table class="wow-table"><thead><tr><th>' + T.ability + '</th><th>DPS</th><th>' + T.share + '</th><th>' + T.casts + '</th><th>' + T.crits + '</th><th>' + T.misses + '</th><th>' + T.dodges + '</th></tr></thead><tbody>' + tr + '</tbody></table></div>' +
      (up ? '<p class="wow-note">' + T.uptime + ' : ' + up + '</p>' : '') + fxList(sm);
    status(fmt(T.js.done, { s: (ms / 1000).toFixed(1), rate: Math.round(r.iterations / (ms / 1000)) }) + ' · ' + fmt(T.js.workers, { n: getPool().size }));
  }

  function tankBlock(r, ch) {
    var c = r.counters, len = num('s60Len') || 180, t = ch.summary.tank, sw = c.swings || 1, pc = function (k) { return ((c['boss_' + k] || 0) / sw * 100).toFixed(1); }, thr = (c.threat || 0) / len, dt = (c.dmgTaken || 0) / len;
    var raw = (num('s60BossDmg') || 9000) / (num('s60BossSpeed') || 2), avoid = (+pc('miss') + +pc('dodge') + +pc('parry')).toFixed(1);
    return '<p class="s60-dps"><b>' + thr.toFixed(0) + '</b> ' + T.tps + '</p>' +
      '<div class="wow-table-wrap"><table class="wow-table"><tbody>' +
      '<tr><td data-first>' + T.tk_taken + '</td><td class="nums">' + dt.toFixed(0) + ' / ' + raw.toFixed(0) + '</td></tr>' +
      '<tr><td data-first>' + T.tk_avoid + '</td><td class="nums">' + avoid + ' % (' + pc('miss') + ' / ' + pc('dodge') + ' / ' + pc('parry') + ')</td></tr>' +
      '<tr><td data-first>' + T.tk_block + '</td><td class="nums">' + pc('block') + ' %</td></tr>' +
      '<tr><td data-first>' + T.tk_crit + '</td><td class="nums">' + pc('crit') + ' % / ' + pc('crush') + ' %</td></tr>' +
      '<tr><td data-first>' + T.tk_health + '</td><td class="nums">' + Math.round(t.health) + ' · ' + T.tk_def + ' ' + t.defense + ' · ' + T.tk_armor + ' ' + Math.round(t.armor) + '</td></tr>' +
      '<tr><td data-first>' + T.tk_ttd + '</td><td class="nums">' + (dt > 0 ? (t.health / dt).toFixed(1) : '—') + ' s</td></tr>' +
      '</tbody></table></div>';
  }
  function fxList(sm) {
    var list = sm.effects || [];
    if (!list.length) return '';
    var sim = list.filter(function (e) { return e.status === 'simulated'; }), other = list.length - sim.length;
    var names = sim.map(function (e) { return e.name; }).filter(function (n, i, a) { return a.indexOf(n) === i; }).join(' · ');
    return '<p class="wow-note"><b>' + T.fx_title + '</b> : ' + (names || '—') + (other ? ' (' + fmt(T.fx_ignored, { n: other }) + ')' : '') + ' ' + T.fx_note + '</p>';
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
    var probes = [['ap', isCaster() ? { sp: 40 } : { ap: 40 }], ['crit', { crit: 0.01 }], ['hit', { hit: 0.01 }], ['haste', { haste: 0.01 }]], res = {}, step = 0;
    function neg(d) { var o = {}; Object.keys(d).forEach(function (k) { o[k] = -d[k]; }); return o; }
    var p = Promise.resolve();
    probes.forEach(function (pr) {
      p = p.then(function () { return getPool().run(withStats(j.job, pr[1]), iters, 1); })
        .then(function (hi) { bar((++step) / 8); return getPool().run(withStats(j.job, neg(pr[1])), iters, 1).then(function (lo) { bar((++step) / 8); res[pr[0]] = (objective(hi) - objective(lo)) / 2; }); });
    });
    p.then(function () {
      var apPer = res.ap / 40, box = $('s60Weights2'); box.hidden = false;
      box.innerHTML = '<h3 class="ad-h3">' + T.w_title + '</h3><ul class="ms-limits"><li>' + T.w_crit + ' = <b>' + (res.crit / apPer).toFixed(1) + '</b> ' + unit() + '</li><li>' + T.w_hit + ' = <b>' + (res.hit / apPer).toFixed(1) + '</b> ' + unit() + '</li><li>' + T.w_haste + ' = <b>' + (res.haste / apPer).toFixed(1) + '</b> ' + unit() + '</li></ul>';
      var ms = performance.now() - t0; status(fmt(T.js.done, { s: (ms / 1000).toFixed(1), rate: Math.round(iters * 8 / (ms / 1000)) }));
    }).catch(function (e) { status(String(e)); }).then(function () { setBusy(false); bar(null); });
  }
  function doOptimize() {
    var c = collect(), jj = makeJob(c), iters = Math.max(200, Math.min(2000, Math.round((num('s60Iters') || 5000) / 10))), t0 = performance.now();
    setBusy(true); status(fmt(T.js.optProgress, { slot: '…' })); bar(null);
    var chara = Object.assign({}, c.spec, { gear: [] }), wmode = curMode();
    function jobFor(spec) { var ch = S.buildCharacter(spec); return Object.assign({}, jj.job, { player: ch.player, target: ch.target }); }
    function evaluate(spec) { return getPool().run(jobFor(spec), iters, 11).then(function (r) { return objective(r); }); }
    function getWeights(spec) {
      var job = jobFor(spec), n = 1200;
      function diff(d) { return Promise.all([getPool().run(withStats(job, d.up), n, 11), getPool().run(withStats(job, d.dn), n, 11)]).then(function (r) { return (objective(r[0]) - objective(r[1])) / 2; }); }
      var mainUp = isCaster() ? { sp: 40 } : { ap: 40 }, mainDn = isCaster() ? { sp: -40 } : { ap: -40 };
      return Promise.all([diff({ up: mainUp, dn: mainDn }), diff({ up: { crit: 0.01 }, dn: { crit: -0.01 } }), diff({ up: { hit: 0.01 }, dn: { hit: -0.01 } }), diff({ up: { haste: 0.01 }, dn: { haste: -0.01 } })])
        .then(function (r) { var apPer = r[0] / 40; return { agi: 0.05 * r[1] / apPer, crit: r[1] / apPer, hit: r[2] / apPer, haste: r[3] / apPer }; });
    }
    S.optimizeGearAsync({ pool: state.pool, character: chara, weaponMode: wmode, caster: isCaster(), ranged: isRanged(), stick: isStick(), tank: isTank(), evaluate: evaluate, getWeights: getWeights, prefilter: 4, maxPasses: 3,
      onProgress: function (p) { status(fmt(T.js.optProgress, { slot: p.slot }) + ' ' + p.dps.toFixed(1) + (isTank() ? ' ' + T.tk_score : ' DPS')); } }).then(function (res) {
      state.lastOpt = res;
      var box = $('s60Opt2'); box.hidden = false;
      var list = res.weapons.concat(res.gear).map(function (g) { return '<li>' + g.slot + ' : ' + g.name + '</li>'; }).join('');
      box.innerHTML = '<h3 class="ad-h3">' + T.o_title + ' : ' + res.dps.toFixed(1) + (isTank() ? ' ' + T.tk_score : ' DPS') + '</h3><ul class="ms-limits">' + list + '</ul><button type="button" class="ms-btn" id="s60Apply">' + T.apply + '</button><p class="wow-note">' + T.o_note + '</p>';
      $('s60Apply').addEventListener('click', function () {
        slots().forEach(function (s) { $('s60g_' + s).value = ''; });
        res.gear.forEach(function (g) { var sel = $('s60g_' + g.slot); if (sel) sel.value = String(g.id); });
        ['mh', 'oh', 'th', 'rng'].forEach(function (k) { $('s60w_' + k).value = ''; });
        res.weapons.forEach(function (g) { var sel = $('s60w_' + g.slot); if (sel) sel.value = String(g.id); });
      });
      status(fmt(T.js.optDone, { s: ((performance.now() - t0) / 1000).toFixed(1) }));
    }).catch(function (e) { status(String(e)); }).then(function () { setBusy(false); });
  }

  // ---------- talents ----------
  var TREE_NAMES = { discipline: fr ? 'Discipline' : 'Discipline', holy: fr ? 'Sacré' : 'Holy', shadow: fr ? 'Ombre' : 'Shadow', elemental: fr ? 'Élémentaire' : 'Elemental', enhancement: fr ? 'Amélioration' : 'Enhancement', restoration: fr ? 'Restauration' : 'Restoration', balance: fr ? 'Équilibre' : 'Balance', 'feral-combat': fr ? 'Combat farouche' : 'Feral Combat', retribution: fr ? 'Vindicte' : 'Retribution', protection: 'Protection', 'beast-mastery': fr ? 'Maîtrise des bêtes' : 'Beast Mastery', marksmanship: fr ? 'Précision' : 'Marksmanship', survival: fr ? 'Survie' : 'Survival', affliction: fr ? 'Affliction' : 'Affliction', demonology: fr ? 'Démonologie' : 'Demonology', destruction: 'Destruction', arcane: fr ? 'Arcanes' : 'Arcane', fire: fr ? 'Feu' : 'Fire', frost: fr ? 'Givre' : 'Frost', arms: fr ? 'Armes' : 'Arms', fury: fr ? 'Fureur' : 'Fury', protection: 'Protection', assassination: fr ? 'Assassinat' : 'Assassination', combat: 'Combat', subtlety: fr ? 'Finesse' : 'Subtlety' };
  function talentStatus() {
    var v = S.validateRanks(state.tdata, state.ranks), st = $('s60TalentStatus');
    st.textContent = (v.ok ? fmt(T.t_ok, { pts: v.total, a: v.bySpec[0], b: v.bySpec[1], c: v.bySpec[2] }) : fmt(T.t_bad, { err: v.errors.slice(0, 2).join(' · ') }));
    st.className = 'wow-note' + (v.ok ? '' : ' s60-warn');
  }
  function renderTalents() {
    var box = $('s60Talents'); box.innerHTML = '';
    var names = S.NAME_TO_KEY[curCls()];
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
  function loadPreset() { if ($('s60HPet')) $('s60HPet').value = curSpec() === 'hunter_marksmanship' ? 'none' : 'cat'; if ($('s60Sac')) $('s60Sac').value = curSpec() === 'warlock_demonology' ? 'imp' : 'none'; state.tdata = state.talentsAll[curCls()]; state.ranks = S.ranksFromNames(state.tdata, S.PRESETS[curSpec()]); renderTalents(); }
  function importLink() {
    var r = S.parseShareHash(state.tdata, $('s60TalentLink').value);
    var st = $('s60TalentStatus');
    if (r.error) { st.textContent = T.t_link_bad; st.className = 'wow-note s60-warn'; return; }
    state.ranks = r.ranks; renderTalents();
    if (!r.revMatches) { st.textContent = T.t_rev + ' ' + st.textContent; }
  }

  // ---------- import of the addon export (/bmw export, format BMW1) ----------
  var EXPORT_SLOTS = { 1: 'head', 2: 'neck', 3: 'shoulder', 15: 'back', 5: 'chest', 9: 'wrist', 10: 'hands', 6: 'waist', 7: 'legs', 8: 'feet', 11: 'ring1', 12: 'ring2', 13: 'trinket1', 14: 'trinket2' };
  var EXPORT_RACES = { human: 'human', dwarf: 'dwarf', nightelf: 'nightelf', gnome: 'gnome', orc: 'orc', scourge: 'undead', undead: 'undead', tauren: 'tauren', troll: 'troll' };
  var PRIMARY_KEYS = ['str', 'agi', 'sta', 'int', 'spi'];
  function parseExport(text) {
    var d = {};
    String(text || '').split(/\r?\n/).forEach(function (line) { var i = line.indexOf('='); if (i > 0) d[line.slice(0, i).trim()] = line.slice(i + 1).trim(); });
    return d;
  }
  function nm(d, k, def) { var v = parseFloat(d[k]); return isFinite(v) ? v : (def === undefined ? 0 : def); }
  function idOf(d, slot) { var v = d['slot' + slot]; return v ? (parseInt(v.split(':')[0], 10) || 0) : 0; }
  // weapon rebuilt from the character sheet: the sheet's min/max include the attack-power bonus (AP / 14 per second of speed) and the % damage modifier
  function sheetWeapon(d, which, off) {
    var ranged = which === 'r', ap = ranged ? nm(d, 'rap') : nm(d, 'ap'), pct = (ranged ? nm(d, 'r_pct', 1) : nm(d, 'dmg_pct', 1)) || 1, speed, lo, hi;
    if (ranged) { speed = nm(d, 'r_speed'); lo = nm(d, 'r_min'); hi = nm(d, 'r_max'); }
    else if (which === 'mh') { speed = nm(d, 'speed_mh'); lo = nm(d, 'mh_min'); hi = nm(d, 'mh_max'); }
    else { speed = nm(d, 'speed_oh'); lo = nm(d, 'oh_min'); hi = nm(d, 'oh_max'); }
    if (!(speed > 0 && hi > 0)) return null;
    var avg = (lo + hi) / 2 / pct; if (which === 'oh') avg /= 0.5;
    avg = Math.max(0, avg - ap / 14 * speed);
    return { min: avg * 0.75, max: avg * 1.25, speed: speed, type: '', offHand: !!off, twoHand: false, itemId: 0, st: {} };
  }
  function dropImport() {
    if (!state.imported || state.importing) return;
    state.imported = false; state.impWeapons = null;
    ['s60Ap', 's60Crit', 's60Hit'].forEach(function (id) { $(id).value = ''; });
    fillBase();
    var st = $('s60ImportStatus'); st.className = 'wow-note'; st.textContent = T.imp_off;
  }
  function importCharacter() {
    var st = $('s60ImportStatus'), notes = [], d = parseExport($('s60Export').value);
    function fail(msg) { st.className = 'wow-note s60-warn'; st.textContent = msg; }
    if (d.format !== 'BMW1') return fail(T.imp_bad_format);
    var cls = (d['class'] || '').toLowerCase();
    if (!cls) return fail(T.imp_no_class);
    var cands = Object.keys(SPECS).filter(function (k) { return SPECS[k].cls === cls; });
    if (!cands.length) return fail(fmt(T.imp_class_bad, { cls: d['class'] }));
    var sid = d.spec === 'hunter_survival' ? 'hunter_melee' : d.spec, guessed = false;
    if (!SPECS[sid] || SPECS[sid].cls !== cls) { sid = cands[0]; guessed = true; }
    state.importing = true;
    $('s60Spec').value = sid; $('s60Spec').dispatchEvent(new Event('change'));
    var specName = $('s60Spec').options[$('s60Spec').selectedIndex].textContent;
    if (guessed) notes.push(fmt(T.imp_spec_guess, { spec: specName }));
    var race = EXPORT_RACES[(d.race || '').toLowerCase()];
    if (race) { $('s60Race').value = race; fillBase(); } else notes.push(T.imp_race_bad);
    var lvl = nm(d, 'level', 60);
    if (lvl !== 60) notes.push(fmt(T.imp_level, { lvl: lvl }));
    // talents: "node:rank" pairs with the talent calculator's own node ids
    if (d.talents) {
      var ranks = {};
      d.talents.split(',').forEach(function (p) { var a = p.split(':'), n = String(a[0]).replace(/^n/, ''), r = parseInt(a[1], 10); if (/^\d+$/.test(n) && r) ranks['n' + n] = r; });
      var v = S.validateRanks(state.tdata, ranks);
      if (v.ok) { state.ranks = ranks; renderTalents(); notes.push(fmt(T.imp_talents, { pts: v.total })); }
      else notes.push(fmt(T.imp_talents_bad, { err: v.errors.slice(0, 2).join(' · ') }));
    }
    // raid buffs and consumables are already inside the sheet's stats: uncheck them so they are not counted twice (the boss debuffs stay)
    var nbuffs = nm(d, 'buffs');
    ['buff', 'cons'].forEach(function (g) { var defs = g === 'buff' ? S.BUFFS : S.CONSUMABLES; Object.keys(defs).forEach(function (k) { var c = $('s60b_' + g + '_' + k); if (c) c.checked = false; }); });
    if (nbuffs > 0) notes.push(fmt(T.imp_buffs, { n: nbuffs }));
    // gear: every item the simulator knows is selected (its effects are simulated); the others are already in the sheet's totals
    slots().forEach(function (slot) { var sel = $('s60g_' + slot); if (sel) sel.value = ''; });
    ['s60w_mh', 's60w_oh', 's60w_th', 's60w_rng'].forEach(function (id) { if ($(id)) $(id).value = ''; });
    var known = 0, unknown = 0;
    Object.keys(EXPORT_SLOTS).forEach(function (n) {
      var id = idOf(d, n); if (!id) return;
      var sel = $('s60g_' + EXPORT_SLOTS[n]); if (!sel) return;
      if (state.pool.byId.get(id)) sel.value = String(id);
      if (sel.value === String(id)) known++; else unknown++;
    });
    var mode = curMode(), id16 = idOf(d, 16), id17 = idOf(d, 17), id18 = idOf(d, 18), W = [];
    function pick(id, which, off) { var it = id && state.pool.byId.get(id); if (id) { if (it) known++; else unknown++; } return it ? S.toWeapon(it, off) : sheetWeapon(d, which, off); }
    if (mode === 'dw') W.push(pick(id16, 'mh', false), pick(id17, 'oh', true));
    else if (mode === '2h') { var w2 = pick(id16, 'mh', false); if (w2) w2.twoHand = true; W.push(w2); }
    else if (mode === 'tank') W.push(pick(id16, 'mh', false));
    else if (mode === 'ranged') W.push(pick(id18, 'r', false));
    if ((mode === 'caster' || mode === 'stick' || mode === 'ranged') && id16 && state.pool.byId.get(id16)) { var th = $('s60w_th'); th.value = String(id16); }
    state.impWeapons = W.filter(Boolean);
    // sheet totals (power, critical strike, hit): trusted as they are by the engine
    var caster = mode === 'caster', ranged = mode === 'ranged';
    $('s60Ap').value = String(caster ? nm(d, 'sp') : ranged ? nm(d, 'rap') : nm(d, 'ap'));
    $('s60Crit').value = String(caster ? nm(d, 'crit_spell') : ranged ? nm(d, 'crit_ranged') : nm(d, 'crit_melee'));
    $('s60Hit').value = String(caster ? nm(d, 'hit_spell') : ranged ? nm(d, 'hit_ranged') : nm(d, 'hit_melee'));
    // base stats = sheet stats minus what the recognized items bring, so that mana and regeneration (Intellect, Spirit) match the sheet
    var c0 = collect(), sum = {};
    PRIMARY_KEYS.forEach(function (k) { sum[k] = 0; });
    (c0.spec.gear || []).concat(c0.spec.weapons || []).forEach(function (g) { PRIMARY_KEYS.forEach(function (k) { sum[k] += (g.st && g.st[k]) || 0; }); });
    PRIMARY_KEYS.forEach(function (k) { if (d[k] !== undefined && d[k] !== '') $('s60base_' + k).value = String(Math.max(0, Math.round(nm(d, k) - sum[k]))); });
    state.importing = false; state.imported = true;
    notes.unshift(fmt(T.imp_gear, { k: known, u: unknown }));
    var race_label = $('s60Race').options[$('s60Race').selectedIndex].textContent;
    st.className = 'wow-note';
    st.innerHTML = '';
    st.appendChild(document.createTextNode(fmt(T.imp_ok, { spec: specName, race: race_label, lvl: lvl })));
    var ul = el('ul'); notes.forEach(function (n) { ul.appendChild(el('li', { text: n })); }); st.appendChild(ul);
    doRun();
  }

  // ---------- boot ----------
  Promise.all(['items.json', 'proficiency.json', 'spells60.json', 'talents.json', 'effects.json'].map(function (f) { return fetch(base + f + '?v=' + dv).then(function (r) { return r.json(); }); })).then(function (all) {
    state.items = all[0]; state.prof = all[1]; state.data = all[2]; state.talentsAll = all[3]; state.effects = all[4];
    state.pool = new S.ItemPool(all[0], all[1]);
    buildForm(); loadPreset();
    BASE_KEYS.forEach(function (k) { $('s60Base').appendChild(el('label', { class: 's60-row' }, el('span', { text: k[1] }), el('input', { id: 's60base_' + k[0], type: 'number', step: '1' }))); });
    fillBase(); showClassOptions();
    $('s60Race').addEventListener('change', fillBase);
    $('s60Spec').addEventListener('change', function () { buildGearSelects(); refreshWeapons(); pickDefaultWeapons(); loadPreset(); fillBase(); showClassOptions(); applyRaidPreset(); });
    $('s60Preset').addEventListener('click', loadPreset);
    $('s60TalentLink').addEventListener('change', importLink);
    $('s60Import').addEventListener('click', importCharacter);
    $('s60ImportClear').addEventListener('click', function () { $('s60Export').value = ''; $('s60ImportStatus').textContent = ''; });
    $('s60Gear').addEventListener('change', dropImport);
    ['s60w_mh', 's60w_oh', 's60w_th', 's60w_rng', 's60Race'].forEach(function (id) { if ($(id)) $(id).addEventListener('change', dropImport); });
    $('s60Spec').addEventListener('change', function () { if (!state.importing) dropImport(); });
    $('s60Run').addEventListener('click', doRun);
    $('s60Weights').addEventListener('click', doWeights);
    $('s60Opt').addEventListener('click', doOptimize);
    try {      // ?spec=<simulator spec id> (the spec guides link here with their own spec, e.g. ?spec=priest_shadow)
      var qSpec = new URLSearchParams(location.search).get('spec'), selSpec = $('s60Spec');
      if (qSpec && Array.prototype.some.call(selSpec.options, function (o) { return o.value === qSpec; })) { selSpec.value = qSpec; selSpec.dispatchEvent(new Event('change')); }
    } catch (e) { /* no query string */ }
    app.classList.add('ready'); $('s60Loading').hidden = true; $('s60Form').hidden = false;
  }).catch(function (e) { $('s60Loading').textContent = 'Error: ' + e; });
})();
