
(function () {
  var ROOT = window.BM_ROOT || '';
  var I = window.BM_BUILDER_I18N || {};
  var ROWS = 4, COLS = 7, BENCH_SIZE = 9;

  var picker = document.getElementById('champPicker');
  var boardEl = document.getElementById('hexBoard');
  var benchEl = document.getElementById('benchRow');
  var traitPanel = document.getElementById('traitPanel');
  var searchInput = document.getElementById('builderSearch');
  var costFilters = document.getElementById('builderCostFilters');
  var emptyHint = document.getElementById('builderEmptyHint');
  var resetBtn = document.getElementById('builderReset');
  var shareBtn = document.getElementById('builderShare');
  var shareStatus = document.getElementById('builderShareStatus');
  if (!picker || !boardEl) return;

  var champions = [];
  var champBySlug = {};
  var traitDefs = [];
  var board = new Array(ROWS * COLS).fill(null);
  var bench = new Array(BENCH_SIZE).fill(null);
  var armedSlug = null;
  var activeCostFilter = 'ALL';

  function champImg(slug) {
    return ROOT + 'assets/champions/' + slug + '.png';
  }
  function traitImg(slug) {
    return ROOT + 'assets/traits/' + slug + '.png';
  }

  // ---- Board / bench DOM (built once; only their filled state changes) ----
  function buildBoard() {
    boardEl.innerHTML = '';
    for (var r = 0; r < ROWS; r++) {
      var rowEl = document.createElement('div');
      rowEl.className = 'hex-row';
      if (r % 2 === 1) rowEl.dataset.offset = 'true';
      for (var c = 0; c < COLS; c++) {
        var idx = r * COLS + c;
        var cell = document.createElement('div');
        cell.className = 'hex-cell';
        cell.dataset.idx = String(idx);
        cell.addEventListener('click', function (e) {
          onCellClick(parseInt(e.currentTarget.dataset.idx, 10), 'board');
        });
        rowEl.appendChild(cell);
      }
      boardEl.appendChild(rowEl);
    }
  }
  function buildBench() {
    benchEl.innerHTML = '';
    for (var i = 0; i < BENCH_SIZE; i++) {
      var cell = document.createElement('div');
      cell.className = 'bench-cell';
      cell.dataset.idx = String(i);
      cell.addEventListener('click', function (e) {
        onCellClick(parseInt(e.currentTarget.dataset.idx, 10), 'bench');
      });
      benchEl.appendChild(cell);
    }
  }

  function onCellClick(idx, zone) {
    var arr = zone === 'board' ? board : bench;
    if (armedSlug) {
      arr[idx] = armedSlug;
      setArmed(null);
    } else if (arr[idx]) {
      arr[idx] = null;
    } else {
      return;
    }
    renderCells();
    renderTraitPanel();
    syncUrl();
  }

  function renderCells() {
    var boardCells = boardEl.querySelectorAll('.hex-cell');
    board.forEach(function (slug, i) { paintCell(boardCells[i], slug); });
    var benchCells = benchEl.querySelectorAll('.bench-cell');
    bench.forEach(function (slug, i) { paintCell(benchCells[i], slug); });
    var anyFilled = board.some(Boolean) || bench.some(Boolean);
    if (emptyHint) emptyHint.hidden = anyFilled;
  }
  function paintCell(el, slug) {
    if (!el) return;
    if (slug && champBySlug[slug]) {
      el.dataset.filled = 'true';
      el.innerHTML = '<img src="' + champImg(slug) + '" alt="' + champBySlug[slug].name + '" loading="lazy">';
    } else {
      el.dataset.filled = 'false';
      el.innerHTML = '';
    }
  }

  // ---- Champion picker ----
  function buildPicker() {
    picker.innerHTML = '';
    if (!champions.length) {
      picker.innerHTML = '<div class="champ-picker-empty"></div>';
      return;
    }
    champions.forEach(function (c) {
      var item = document.createElement('div');
      item.className = 'champ-picker-item';
      item.dataset.slug = c.slug;
      item.dataset.cost = String(c.cost || 1);
      item.dataset.name = c.name.toLowerCase();
      item.style.borderColor = 'var(--cost-' + (c.cost || 1) + ')';
      item.title = c.name;
      item.innerHTML = '<img src="' + champImg(c.slug) + '" alt="' + c.name + '" loading="lazy">';
      item.addEventListener('click', function () {
        setArmed(armedSlug === c.slug ? null : c.slug);
      });
      picker.appendChild(item);
    });
  }
  function setArmed(slug) {
    armedSlug = slug;
    picker.querySelectorAll('.champ-picker-item').forEach(function (el) {
      el.dataset.armed = el.dataset.slug === slug ? 'true' : 'false';
    });
  }
  function applyPickerFilters() {
    var q = (searchInput && searchInput.value.trim().toLowerCase()) || '';
    picker.querySelectorAll('.champ-picker-item').forEach(function (el) {
      var costOk = activeCostFilter === 'ALL' || el.dataset.cost === activeCostFilter;
      var searchOk = !q || el.dataset.name.indexOf(q) !== -1;
      el.dataset.hidden = (costOk && searchOk) ? 'false' : 'true';
    });
  }
  if (searchInput) searchInput.addEventListener('input', applyPickerFilters);
  if (costFilters) {
    costFilters.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-cost-filter]');
      if (!btn) return;
      costFilters.querySelectorAll('[data-cost-filter]').forEach(function (b) { b.dataset.active = String(b === btn); });
      activeCostFilter = btn.dataset.costFilter;
      applyPickerFilters();
    });
  }

  // ---- Trait synergy panel (board only, matches real TFT rules) ----
  function renderTraitPanel() {
    if (!traitPanel) return;
    var counts = {};
    board.forEach(function (slug) {
      var c = slug && champBySlug[slug];
      if (!c) return;
      (c.traits || []).forEach(function (t) { counts[t] = (counts[t] || 0) + 1; });
    });
    var rows = [];
    traitDefs.forEach(function (t) {
      var count = counts[t.name] || 0;
      if (!count) return;
      var effects = t.effects; // ascending by min_units
      var activeIdx = -1;
      for (var i = 0; i < effects.length; i++) {
        if (count >= effects[i].min_units) activeIdx = i;
      }
      var next = effects[activeIdx + 1];
      rows.push({ t: t, count: count, activeIdx: activeIdx, nextMin: next ? next.min_units : null });
    });
    rows.sort(function (a, b) {
      if ((a.activeIdx >= 0) !== (b.activeIdx >= 0)) return (a.activeIdx >= 0) ? -1 : 1;
      return b.count - a.count;
    });
    if (!rows.length) {
      traitPanel.innerHTML = '<div class="champ-picker-empty">' + (I.noTraits || '') + '</div>';
      return;
    }
    traitPanel.innerHTML = rows.map(function (r) {
      var label = r.nextMin ? (r.count + '/' + r.nextMin) : String(r.count);
      return '<div class="trait-row" data-active="' + (r.activeIdx >= 0) + '"' +
        (r.activeIdx >= 0 ? ' data-tier="' + r.activeIdx + '"' : '') + '>' +
        '<img src="' + traitImg(r.t.slug) + '" alt="' + r.t.name + '" loading="lazy">' +
        '<span class="trait-row-name">' + r.t.name + '</span>' +
        '<span class="trait-row-count">' + label + '</span></div>';
    }).join('');
  }

  // ---- Shareable URL state ----
  function syncUrl() {
    var b = [];
    board.forEach(function (slug, i) { if (slug) b.push(i + ':' + slug); });
    var e = [];
    bench.forEach(function (slug, i) { if (slug) e.push(i + ':' + slug); });
    var params = new URLSearchParams();
    if (b.length) params.set('b', b.join(','));
    if (e.length) params.set('e', e.join(','));
    var qs = params.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
  }
  function loadFromUrl() {
    var params = new URLSearchParams(location.search);
    (params.get('b') || '').split(',').forEach(function (pair) {
      var m = pair.split(':');
      var idx = parseInt(m[0], 10), slug = m[1];
      if (slug && champBySlug[slug] && idx >= 0 && idx < board.length) board[idx] = slug;
    });
    (params.get('e') || '').split(',').forEach(function (pair) {
      var m = pair.split(':');
      var idx = parseInt(m[0], 10), slug = m[1];
      if (slug && champBySlug[slug] && idx >= 0 && idx < bench.length) bench[idx] = slug;
    });
  }

  async function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      board = new Array(ROWS * COLS).fill(null);
      bench = new Array(BENCH_SIZE).fill(null);
      setArmed(null);
      renderCells();
      renderTraitPanel();
      history.replaceState(null, '', location.pathname);
    });
  }
  if (shareBtn) {
    shareBtn.addEventListener('click', function () {
      copyToClipboard(location.href).then(function () {
        if (!shareStatus) return;
        shareStatus.hidden = false;
        shareStatus.textContent = I.shareCopied || '';
        shareStatus.dataset.error = 'false';
        setTimeout(function () { shareStatus.hidden = true; }, 2200);
      });
    });
  }

  fetch(ROOT + 'assets/data/builder.json').then(function (r) { return r.json(); }).then(function (data) {
    champions = data.champions || [];
    traitDefs = data.traits || [];
    champions.forEach(function (c) { champBySlug[c.slug] = c; });
    buildPicker();
    buildBoard();
    buildBench();
    loadFromUrl();
    renderCells();
    renderTraitPanel();
  }).catch(function () {});
})();
