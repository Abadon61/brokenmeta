(function () {
  'use strict';
  // BrokenLogs page: drop a WoWCombatLog.txt, a worker parses it (wow-logs-core.js), this script draws the report. Nothing leaves the browser.
  var root = document.getElementById('lgApp');
  if (!root) return;
  var T = JSON.parse(document.getElementById('lgI18n').textContent);
  var lang = root.getAttribute('data-lang') || 'fr';
  var $ = function (id) { return document.getElementById(id); };
  var COLORS = { warrior: '#C69B6D', rogue: '#FFF468', mage: '#3FC7EB', hunter: '#AAD372', priest: '#FFFFFF', warlock: '#8788EE', shaman: '#0070DD', druid: '#FF7C0A', paladin: '#F48CBA',
    deathknight: '#C41E3A', demonhunter: '#A330C9', monk: '#00FF98', evoker: '#33937F' };
  var NEUTRAL = '#9aa3d6';
  var state = { res: null, fight: 0, tab: 'over', sel: 0, hide: false };

  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function f(n) { return Math.round(n).toLocaleString(lang === 'fr' ? 'fr-FR' : 'en-US').replace(/ /g, ' '); }
  function pct(a, b) { return b ? Math.round(a / b * 100) : 0; }
  function tm(sec) { sec = Math.max(0, Math.round(sec)); return Math.floor(sec / 60) + ':' + ('0' + (sec % 60)).slice(-2); }
  function fmt(s, o) { return String(s).replace(/\{(\w+)\}/g, function (m, k) { return o[k] !== undefined ? o[k] : m; }); }
  function color(p) { return COLORS[p.cls] || NEUTRAL; }
  function who(p, i) { return state.hide ? (lang === 'fr' ? 'Joueur ' : 'Player ') + (i + 1) : p.name; }
  function stamp(ms) { var d = new Date(ms); return ('0' + d.getUTCHours()).slice(-2) + ':' + ('0' + d.getUTCMinutes()).slice(-2); }

  // ---------------------------------------------------------------- read the file
  var worker = null;
  function start(file) {
    $('lgError').hidden = true; $('lgReport').hidden = true; $('lgProgress').hidden = false;
    $('lgBar').style.width = '0%'; $('lgProgTxt').textContent = T.reading;
    if (worker) worker.terminate();
    worker = new Worker(root.getAttribute('data-worker'));
    worker.onmessage = function (e) {
      var m = e.data;
      if (m.type === 'progress') {
        $('lgBar').style.width = Math.min(99, m.read / m.total * 100).toFixed(1) + '%';
        $('lgProgTxt').textContent = T.reading + ' ' + fmt(T.lines, { n: f(m.lines) });
      } else if (m.type === 'done') { finish(m.result); worker.terminate(); worker = null; }
      else if (m.type === 'error') fail(m.message);
    };
    worker.onerror = function (e) { fail(e.message || 'worker'); };
    worker.postMessage({ file: file, core: new URL(root.getAttribute('data-core'), location.href).href });
  }
  function fail(msg) {
    $('lgProgress').hidden = true;
    var box = $('lgError'); box.hidden = false; box.textContent = msg;
  }
  function finish(res) {
    $('lgProgress').hidden = true;
    if (!res.meta.sawCombat && !res.fights.length) return fail(T.bad);
    if (!res.fights.length) return fail(T.nofight);
    state.res = res; state.fight = 0; state.tab = 'over'; state.sel = 0;
    // a boss fight first when there is one
    for (var i = 0; i < res.fights.length; i++) if (res.fights[i].kind === 'boss') { state.fight = i; break; }
    draw();
    $('lgReport').hidden = false;
    $('lgDrop').hidden = true;
    $('lgNoteTxt').textContent = fmt(T.done, { s: res.meta.seconds, f: res.fights.length }) + (res.meta.advanced === false ? ' ' + T.noadv : '');
    $('lgNote').hidden = false;
  }

  // ---------------------------------------------------------------- drawing helpers
  function line(svg, pts, col, w, h, dur) {
    var mx = Math.max.apply(null, pts.concat([1])) * 1.08, n = pts.length, d = [], i;
    for (i = 0; i < n; i++) d.push((n > 1 ? i / (n - 1) * w : 0).toFixed(1) + ',' + (h - pts[i] / mx * h).toFixed(1));
    svg.innerHTML = '<polyline fill="' + col + '" fill-opacity=".12" stroke="none" points="0,' + h + ' ' + d.join(' ') + ' ' + w + ',' + h + '"/><polyline fill="none" stroke="' + col + '" stroke-width="2.2" points="' + d.join(' ') + '"/>' +
      '<text x="4" y="' + (h - 4) + '" fill="#9aa3d6" font-size="11">0:00</text><text x="' + (w / 2) + '" y="' + (h - 4) + '" fill="#9aa3d6" font-size="11" text-anchor="middle">' + tm(dur / 2) + '</text><text x="' + (w - 4) + '" y="' + (h - 4) + '" fill="#9aa3d6" font-size="11" text-anchor="end">' + tm(dur) + '</text>';
  }
  function bars(rows, key, mx, onClickIdx) {
    return rows.map(function (p, i) {
      return '<button type="button" class="lg-row' + (onClickIdx === i ? ' is-on' : '') + '" data-i="' + i + '"><span class="lg-rk">' + (i + 1) + '</span><span class="lg-dot" style="background:' + color(p) + '"></span>' +
        '<span><b style="color:' + color(p) + '">' + esc(who(p, i)) + '</b><br><small>' + esc(p.spec || T.unknown) + (p.ilvl ? ' · ' + T.ilvl + ' ' + Math.round(p.ilvl) : '') + '</small></span>' +
        '<span class="lg-bar"><i style="width:' + (mx ? p[key] / mx * 100 : 0).toFixed(1) + '%;background:' + color(p) + '"></i></span><span class="lg-n">' + f(key === 'dmg' ? p.dps : p.hps) + '</span></button>';
    }).join('');
  }

  // ---------------------------------------------------------------- insights (every sentence comes from a measured number)
  function playerInsights(fi, p, idx) {
    var out = [], players = fi.players, best = players.filter(function (x) { return x.role !== 'heal'; })[0] || players[0];
    if (p.role === 'heal') {
      var h = players.filter(function (x) { return x.heal > 0; }).sort(function (a, b) { return b.heal - a.heal; })[0];
      if (p.heal + p.over > 0) { var op = pct(p.over, p.heal + p.over); out.push({ k: op > 40 ? 'warn' : 'ok', t: T.heal_h, x: fmt(T.i_overheal, { p: op }) }); }
      if (h && h !== p) out.push({ k: 'ok', t: T.best, x: fmt(T.i_hps_best, { p: pct(p.heal, h.heal) }) });
    } else {
      var idle = Math.max(0, Math.round(fi.dur - p.active));
      out.push({ k: p.activePct >= 85 ? 'ok' : 'warn', t: T.idle, x: p.activePct >= 85 ? fmt(T.i_active_ok, { p: p.activePct }) : fmt(T.i_active_low, { p: p.activePct, s: idle }) });
      if (p.spells.length && p.dmg) out.push({ k: 'ok', t: T.ab_h, x: fmt(T.i_top_spell, { n: p.spells[0].n, p: pct(p.spells[0].d, p.dmg) }) });
      if (best && best !== p && best.dps) out.push({ k: 'ok', t: T.best, x: fmt(T.i_vs_best, { p: pct(p.dps, best.dps) }) });
      var pd = p.pets.reduce(function (s, x) { return s + x[1]; }, 0);
      if (pd > 0 && p.dmg) out.push({ k: 'ok', t: T.pet, x: fmt(T.i_pets, { p: pct(pd, p.dmg) }) });
    }
    if (p.deaths.length) {
      var last = p.deaths[p.deaths.length - 1].recap, hit = last.filter(function (r) { return r.k === 'd'; }).pop();
      out.push({ k: 'warn', t: T.t_death, x: fmt(T.i_death, { n: p.deaths.length, w: hit ? hit.who : '?', sp: hit ? hit.sp : '?' }) });
    } else out.push({ k: 'ok', t: T.t_death, x: T.i_nodeath });
    return out.slice(0, 4);
  }
  function groupInsights(fi) {
    var out = [], dd = fi.players.filter(function (p) { return p.role !== 'heal' && p.dmg > 0; });
    if (fi.deaths) out.push({ k: 'warn', t: T.k_deaths, x: fmt(T.g_dead, { n: fi.deaths }) }); else out.push({ k: 'ok', t: T.k_deaths, x: T.no_deaths });
    if (dd.length) out.push({ k: 'ok', t: T.dmg_h, x: fmt(T.g_best, { who: state.hide ? (lang === 'fr' ? 'Joueur 1' : 'Player 1') : dd[0].name, v: f(dd[0].dps) }) });
    if (dd.length) { var avg = Math.round(dd.reduce(function (s, p) { return s + p.activePct; }, 0) / dd.length); out.push({ k: avg >= 85 ? 'ok' : 'warn', t: T.idle, x: fmt(T.g_idle, { p: avg }) }); }
    return out;
  }
  function cards(list) { return list.map(function (i) { return '<div class="lg-in ' + i.k + '"><b>' + esc(i.t) + '</b><p>' + esc(i.x) + '</p></div>'; }).join(''); }

  // ---------------------------------------------------------------- panes
  function overview(fi) {
    var dps = Math.round(fi.totalDmg / Math.max(1, fi.dur)), il = fi.players.filter(function (p) { return p.ilvl; }), avg = il.length ? il.reduce(function (s, p) { return s + p.ilvl; }, 0) / il.length : 0;
    var n = Math.ceil(fi.dur / 5), tl = [], i, j;
    for (i = 0; i < n; i++) { var v = 0; for (j = 0; j < fi.players.length; j++) v += fi.players[j].tl[i] || 0; tl.push(v); }
    return '<div class="lg-kpis"><div class="lg-kpi"><b>' + f(dps) + '</b><span>' + T.k_dps + '</span></div><div class="lg-kpi"><b>' + tm(fi.dur) + '</b><span>' + T.k_dur + '</span></div>' +
      '<div class="lg-kpi"><b>' + fi.deaths + '</b><span>' + T.k_deaths + '</span></div><div class="lg-kpi"><b>' + (avg ? avg.toFixed(1) : '–') + '</b><span>' + T.k_ilvl + '</span></div></div>' +
      '<section class="gs-tile" style="margin-top:14px"><div class="gs-th"><h2 class="gs-h2">' + T.ins_h + '</h2><span class="gs-meta">' + T.ins_sub + '</span></div><div class="lg-ins">' + cards(groupInsights(fi)) + '</div></section>' +
      '<section class="gs-tile" style="margin-top:14px"><div class="gs-th"><h2 class="gs-h2">' + T.chart_h + '</h2></div><svg class="lg-chart" id="lgChartRaid" viewBox="0 0 800 150" preserveAspectRatio="none"></svg></section>';
  }
  function damagePane(fi) {
    var rows = fi.players.filter(function (p) { return p.dmg > 0; });
    if (state.sel >= rows.length) state.sel = 0;
    var mx = rows.length ? rows[0].dmg : 1;
    return '<div class="lg-split"><section class="gs-tile"><div class="gs-th"><h2 class="gs-h2">' + T.dmg_h + '</h2><span class="gs-meta">' + T.dmg_sub + '</span></div><div class="lg-rows" id="lgRows">' + bars(rows, 'dmg', mx, state.sel) + '</div></section><aside class="lg-side" id="lgSide"></aside></div>';
  }
  function side(fi) {
    var rows = fi.players.filter(function (p) { return p.dmg > 0; }), p = rows[state.sel], box = $('lgSide');
    if (!p || !box) return;
    var best = rows[0], ab = p.spells.slice(0, 12).map(function (s) {
      return '<tr><td>' + esc(s.n) + '</td><td>' + f(s.d / Math.max(1, fi.dur)) + '</td><td>' + pct(s.d, p.dmg) + ' %</td><td>' + f(s.h) + '</td><td>' + (s.h ? pct(s.c, s.h) : 0) + ' %</td></tr>';
    }).join('');
    box.innerHTML = '<section class="gs-tile"><div class="gs-th"><h2 class="gs-h2" style="color:' + color(p) + '">' + esc(who(p, state.sel)) + '</h2><span class="lg-n">' + f(p.dps) + ' DPS</span></div>' +
      '<div class="lg-meta">' + esc(p.spec || T.unknown) + (p.ilvl ? ' · ' + T.ilvl + ' ' + Math.round(p.ilvl) : '') + ' · ' + f(p.dmg) + ' ' + T.overall.toLowerCase() + '</div>' +
      '<div class="lg-sim"><div><span>' + T.your_dps + '</span><span class="lg-bar"><i style="width:' + pct(p.dps, best.dps) + '%;background:' + color(p) + '"></i></span><b class="lg-n">' + f(p.dps) + '</b></div>' +
      '<div><span>' + T.best + '</span><span class="lg-bar"><i style="width:100%;background:#2de6c4"></i></span><b class="lg-n">' + f(best.dps) + '</b></div></div>' +
      '<div class="lg-meta">' + p.activePct + ' % ' + T.active + ' · ' + f(p.adps) + ' DPS</div><svg class="lg-chart" id="lgChartP" viewBox="0 0 800 150" preserveAspectRatio="none"></svg></section>' +
      '<section class="gs-tile"><div class="gs-th"><h2 class="gs-h2">' + T.imp_h + '</h2></div><div style="display:flex;flex-direction:column;gap:8px">' + cards(playerInsights(fi, p, state.sel)) + '</div></section>' +
      '<section class="gs-tile"><div class="gs-th"><h2 class="gs-h2">' + T.ab_h + '</h2></div><table class="lg-ab"><thead><tr><th>' + T.col_spell + '</th><th>' + T.col_dps + '</th><th>%</th><th>' + T.col_hits + '</th><th>' + T.col_crit + '</th></tr></thead><tbody>' + ab + '</tbody></table></section>';
    line($('lgChartP'), p.tl, color(p), 800, 150, fi.dur);
  }
  function healPane(fi) {
    var rows = fi.players.filter(function (p) { return p.heal > 0; }).sort(function (a, b) { return b.heal - a.heal; });
    if (!rows.length) return '<section class="gs-tile" style="margin-top:12px"><p class="lg-meta">–</p></section>';
    var mx = rows[0].heal;
    var list = rows.map(function (p, i) {
      return '<div class="lg-row" style="cursor:default"><span class="lg-rk">' + (i + 1) + '</span><span class="lg-dot" style="background:' + color(p) + '"></span><span><b style="color:' + color(p) + '">' + esc(who(p, fi.players.indexOf(p))) + '</b><br><small>' +
        esc(p.spec || T.unknown) + ' · ' + T.col_over + ' ' + pct(p.over, p.heal + p.over) + ' %</small></span><span class="lg-bar"><i style="width:' + (p.heal / mx * 100).toFixed(1) + '%;background:' + color(p) + '"></i></span><span class="lg-n">' + f(p.hps) + ' HPS</span></div>';
    }).join('');
    return '<section class="gs-tile" style="margin-top:12px"><div class="gs-th"><h2 class="gs-h2">' + T.heal_h + '</h2></div><div class="lg-rows">' + list + '</div><p class="lg-meta" style="margin-top:10px">' + T.heal_note + '</p></section>';
  }
  function deathPane(fi) {
    var ds = [];
    fi.players.forEach(function (p, i) { p.deaths.forEach(function (d) { ds.push({ p: p, i: i, d: d }); }); });
    ds.sort(function (a, b) { return a.d.t - b.d.t; });
    if (!ds.length) return '<section class="gs-tile" style="margin-top:12px"><p class="lg-meta">' + T.no_deaths + '</p></section>';
    return '<div style="margin-top:12px">' + ds.map(function (x) {
      return '<div class="lg-death"><b style="color:' + color(x.p) + '">' + esc(who(x.p, x.i)) + '</b> · ' + fmt(T.death_at, { t: tm(x.d.t / 1000) }) + '<ol>' + x.d.recap.map(function (r) {
        return '<li><b>' + (r.dt / 1000).toFixed(1) + ' s</b> ' + esc(r.who) + ' : ' + esc(r.sp) + '<em class="' + (r.k === 'h' ? 'heal' : '') + '">' + (r.k === 'h' ? '+' : '-') + f(r.v) + '</em></li>';
      }).join('') + '</ol></div>';
    }).join('') + '</div>';
  }
  function takenPane(fi) {
    var rows = fi.players.slice().sort(function (a, b) { return b.taken - a.taken; }).filter(function (p) { return p.taken > 0; });
    if (!rows.length) return '<section class="gs-tile" style="margin-top:12px"><p class="lg-meta">–</p></section>';
    var mx = rows[0].taken;
    return '<section class="gs-tile" style="margin-top:12px"><div class="gs-th"><h2 class="gs-h2">' + T.taken_h + '</h2></div><div class="lg-rows">' + rows.map(function (p, i) {
      return '<div class="lg-row" style="cursor:default"><span class="lg-rk">' + (i + 1) + '</span><span class="lg-dot" style="background:' + color(p) + '"></span><span><b style="color:' + color(p) + '">' + esc(who(p, fi.players.indexOf(p))) + '</b><br><small>' +
        esc(p.taken_by.slice(0, 2).map(function (s) { return s.n; }).join(', ')) + '</small></span><span class="lg-bar"><i style="width:' + (p.taken / mx * 100).toFixed(1) + '%;background:' + color(p) + '"></i></span><span class="lg-n">' + f(p.taken) + '</span></div>';
    }).join('') + '</div></section>';
  }

  // ---------------------------------------------------------------- page
  function draw() {
    var res = state.res, fi = res.fights[state.fight];
    var encs = res.fights.map(function (x, i) {
      var status = x.kind === 'boss' ? (x.success ? '<span class="kill">' + T.kill + '</span>' : '<span class="wipe">' + T.wipe + '</span>') : '<span>' + T.combat + '</span>';
      return '<button type="button" data-f="' + i + '" class="' + (i === state.fight ? 'is-on' : '') + '"><b>' + esc(x.name) + '</b><span>' + status + ' · ' + tm(x.dur) + ' · ' + stamp(x.start) + ' · ' + x.players.length + ' ' + T.players + '</span></button>';
    }).join('');
    var tabs = [['over', T.t_over], ['dmg', T.t_dmg], ['heal', T.t_heal], ['death', T.t_death], ['taken', T.t_taken]].map(function (t) {
      return '<button type="button" class="lg-tab' + (state.tab === t[0] ? ' is-on' : '') + '" data-t="' + t[0] + '">' + t[1] + '</button>';
    }).join('');
    var body = state.tab === 'over' ? overview(fi) : state.tab === 'dmg' ? damagePane(fi) : state.tab === 'heal' ? healPane(fi) : state.tab === 'death' ? deathPane(fi) : takenPane(fi);
    $('lgReport').innerHTML = '<section class="gs-tile" style="margin-top:14px"><div class="gs-th"><h2 class="gs-h2">' + T.fights + '</h2><span class="gs-meta">' + T.hint_fight + '</span></div><div class="lg-enc" id="lgEnc">' + encs + '</div></section>' +
      '<nav class="lg-tabs" aria-label="' + esc(fi.name) + '">' + tabs + '<label class="lg-names"><input type="checkbox" id="lgHide"' + (state.hide ? ' checked' : '') + '> ' + T.hide + '</label></nav>' + body;
    if (state.tab === 'over') {
      var n = Math.ceil(fi.dur / 5), tl = [], i, j;
      for (i = 0; i < n; i++) { var v = 0; for (j = 0; j < fi.players.length; j++) v += fi.players[j].tl[i] || 0; tl.push(v); }
      line($('lgChartRaid'), tl, '#8a6cff', 800, 150, fi.dur);
    }
    if (state.tab === 'dmg') side(fi);
  }

  // ---------------------------------------------------------------- events
  var input = $('lgFile'), drop = $('lgDrop');
  input.addEventListener('change', function () { if (input.files[0]) start(input.files[0]); });
  ['dragenter', 'dragover'].forEach(function (n) { drop.addEventListener(n, function (e) { e.preventDefault(); drop.classList.add('is-over'); }); });
  ['dragleave', 'drop'].forEach(function (n) { drop.addEventListener(n, function (e) { e.preventDefault(); drop.classList.remove('is-over'); }); });
  drop.addEventListener('drop', function (e) { var fl = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]; if (fl) start(fl); });
  $('lgAgain').addEventListener('click', function () { $('lgReport').hidden = true; $('lgNote').hidden = true; $('lgDrop').hidden = false; input.value = ''; state.res = null; });
  $('lgReport').addEventListener('click', function (e) {
    var b = e.target.closest('#lgEnc button');
    if (b) { state.fight = +b.getAttribute('data-f'); state.sel = 0; draw(); return; }
    b = e.target.closest('.lg-tab');
    if (b) { state.tab = b.getAttribute('data-t'); draw(); return; }
    b = e.target.closest('#lgRows .lg-row');
    if (b) { state.sel = +b.getAttribute('data-i'); draw(); }
  });
  $('lgReport').addEventListener('change', function (e) { if (e.target.id === 'lgHide') { state.hide = e.target.checked; draw(); } });
})();
