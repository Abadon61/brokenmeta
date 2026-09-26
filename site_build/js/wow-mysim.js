(function () {
  'use strict';
  // "Simulate my character": paste the BrokenMeta addon's /bmw export, the simulation runs in a
  // Web Worker (Pyodide + the site's own wow_dps_sim.py). Nothing is sent to any server.
  var root = document.getElementById('msApp');
  if (!root) return;
  var T = JSON.parse(document.getElementById('msI18n').textContent);
  var SPECS = JSON.parse(document.getElementById('msSpecs').textContent);
  var base = root.getAttribute('data-base');
  var lang = root.getAttribute('data-lang');
  var $ = function (id) { return document.getElementById(id); };
  var input = $('msExport'), btn = $('msRun'), status = $('msStatus'), out = $('msResult'), specSel = $('msSpec');
  var STORE_KEY = 'bm-mysim-export';
  var worker = null, busy = false, lastText = '';

  try { var saved = localStorage.getItem(STORE_KEY); if (saved && !input.value) input.value = saved; } catch (e) {}

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function fmt(n, d) {
    return Number(n).toLocaleString(lang === 'fr' ? 'fr-FR' : 'en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function setStatus(key, isError) {
    status.textContent = key ? (T['st_' + key] || key) : '';
    status.className = 'ms-status' + (isError ? ' is-error' : '') + (key && !isError ? ' is-busy' : '');
  }

  function getWorker() {
    if (worker) return worker;
    worker = new Worker(root.getAttribute('data-worker'));
    worker.onmessage = function (e) {
      var m = e.data;
      if (m.type === 'status') return setStatus(m.step);
      busy = false; btn.disabled = false;
      if (m.type === 'error') { setStatus('crash', true); console.error(m.message); return; }
      var r = m.result;
      if (!r.ok) { setStatus('err_' + r.error, true); out.hidden = true; return; }
      setStatus('');
      render(r);
    };
    worker.onerror = function (e) { busy = false; btn.disabled = false; setStatus('crash', true); console.error(e); };
    return worker;
  }

  function run(spec) {
    var text = input.value.trim();
    if (!text) { setStatus('err_empty', true); return; }
    if (busy) return;
    busy = true; btn.disabled = true; lastText = text;
    try { localStorage.setItem(STORE_KEY, text); } catch (e) {}
    setStatus('engine');
    getWorker().postMessage({ base: base, manifest: root.getAttribute('data-manifest'), text: text, spec: spec || null, lang: lang });
  }

  // "0.3.0" < "0.4.0"; an empty/missing version (addon older than 0.2) counts as older.
  function olderThan(a, b) {
    if (!a) return true;
    var x = String(a).split('.'), y = String(b).split('.');
    for (var i = 0; i < Math.max(x.length, y.length); i++) {
      var d = (parseInt(x[i], 10) || 0) - (parseInt(y[i], 10) || 0);
      if (d) return d < 0;
    }
    return false;
  }

  function specLabel(id) {
    var s = SPECS[id];
    return s ? s.class_name + ' ' + s.spec_name + (s.role === 'tank' ? ' (' + T.tank + ')' : '') : id;
  }

  function statRows(r) {
    var mine = r.stats, bis = r.bis_stats;
    var rows = [
      [T.stat_ap, fmt(mine.ap, 0), fmt(bis.ap, 0)],
      [T.stat_sp, fmt(mine.sp, 0), fmt(bis.sp, 0)],
      [T.stat_crit, fmt(mine.crit * 100, 2) + ' %', fmt(bis.crit * 100, 2) + ' %'],
      [T.stat_hit, fmt(mine.hit * 100, 2) + ' %', fmt(bis.hit * 100, 2) + ' %']
    ];
    (r.bis_weapons || []).forEach(function (bw, i) {
      var w = (r.weapons || [])[i];
      var label = bw.offhand ? T.stat_oh : T.stat_mh;
      rows.push([label, w ? fmt(w.dmg, 1) + ' · ' + fmt(w.speed, 2) + ' s' : '—', fmt(bw.dmg, 1) + ' · ' + fmt(bw.speed, 2) + ' s']);
    });
    if ((r.weapons || []).length > (r.bis_weapons || []).length) {
      var extra = r.weapons[r.weapons.length - 1];
      rows.push([T.stat_oh, fmt(extra.dmg, 1) + ' · ' + fmt(extra.speed, 2) + ' s', '—']);
    }
    return rows.map(function (row) {
      return '<tr><th scope="row">' + esc(row[0]) + '</th><td class="nums">' + row[1] + '</td><td class="nums">' + row[2] + '</td></tr>';
    }).join('');
  }

  function render(r) {
    specSel.innerHTML = r.specs.map(function (id) {
      return '<option value="' + esc(id) + '"' + (id === r.spec ? ' selected' : '') + '>' + esc(specLabel(id)) + '</option>';
    }).join('');
    specSel.parentNode.hidden = r.specs.length < 2;

    var s = SPECS[r.spec] || {};
    var diff = r.bis_dps ? (r.dps / r.bis_dps - 1) * 100 : 0;
    var max = Math.max(r.dps, r.bis_dps) || 1;
    var bmax = r.breakdown.length ? r.breakdown[0].dps : 1;
    var latest = root.getAttribute('data-addon');
    var dlLink = document.querySelector('.ms-dl');
    var update = (latest && dlLink && olderThan(r.addon, latest))
      ? '<p class="wow-note">' + esc(T.update.replace('{old}', r.addon || '?').replace('{new}', latest)) +
        ' <a href="' + esc(dlLink.getAttribute('href')) + '" download>' + esc(dlLink.textContent) + '</a></p>'
      : '';
    var warn = update + r.warnings.map(function (w) { return '<p class="wow-note">' + esc(T['warn_' + w] || w) + '</p>'; }).join('');

    out.innerHTML =
      '<div class="ms-head" style="--rc:' + esc(s.class_color || 'var(--magenta)') + '">' +
        (s.class_icon ? '<img src="' + esc(s.class_icon) + '" alt="" width="40" height="40" loading="lazy">' : '') +
        '<div><div class="ms-spec">' + esc(specLabel(r.spec)) + '</div>' +
        '<div class="ms-sub">' + esc(T.level) + ' ' + r.level + (r.race ? ' · ' + esc(r.race) : '') + '</div></div>' +
      '</div>' +
      warn +
      '<div class="ms-compare">' +
        '<div class="ms-bar-row"><span>' + esc(T.you) + '</span><span class="wow-rank-bar-wrap"><span class="wow-rank-bar" style="width:' + (100 * r.dps / max).toFixed(1) + '%;--rc:var(--cyan)"></span></span><span class="nums ms-big">' + fmt(r.dps, 1) + ' DPS</span></div>' +
        '<div class="ms-bar-row"><span>' + esc(T.bis) + '</span><span class="wow-rank-bar-wrap"><span class="wow-rank-bar" style="width:' + (100 * r.bis_dps / max).toFixed(1) + '%"></span></span><span class="nums">' + fmt(r.bis_dps, 1) + ' DPS</span></div>' +
        '<p class="ms-diff ' + (diff >= 0 ? 'is-up' : 'is-down') + '">' + esc(diff >= 0 ? T.diff_up : T.diff_down).replace('{pct}', fmt(Math.abs(diff), 1)) + '</p>' +
      '</div>' +
      '<h2 class="fiche-section-title">' + esc(T.breakdown_h2) + '</h2>' +
      '<div class="tc-dps-breakdown">' + r.breakdown.map(function (b) {
        return '<div class="tc-dps-row ms-src"><span>' + esc(b.name) + '</span><span class="wow-rank-bar-wrap"><span class="wow-rank-bar" style="width:' + (100 * b.dps / bmax).toFixed(1) + '%"></span></span><span class="nums">' + fmt(b.dps, 2) + ' (' + fmt(100 * b.dps / r.dps, 0) + ' %)</span></div>';
      }).join('') +
      '<div class="tc-dps-row tc-dps-total"><span>' + esc(T.total) + '</span><span class="nums">' + fmt(r.dps, 2) + '</span></div></div>' +
      '<h2 class="fiche-section-title">' + esc(T.stats_h2) + '</h2>' +
      '<div class="table-scroll"><table class="ms-stats"><thead><tr><th></th><th>' + esc(T.you) + '</th><th>' + esc(T.bis) + '</th></tr></thead><tbody>' + statRows(r) + '</tbody></table></div>' +
      '<p class="wow-note">' + esc(T.method_note).replace('{n}', r.iterations).replace('{s}', Math.round(r.fight_len)) + '</p>';
    out.hidden = false;
    out.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  btn.addEventListener('click', function () { run(null); });
  specSel.addEventListener('change', function () { if (lastText) run(specSel.value); });
})();
