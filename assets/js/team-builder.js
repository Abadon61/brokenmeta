
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
  var activeCostFilter = 'ALL';

  function champImg(slug) {
    return ROOT + 'assets/champions/' + slug + '.png';
  }
  function traitImg(slug) {
    return ROOT + 'assets/traits/' + slug + '.png';
  }

  // ---- Drag and drop (mouse + touch via Pointer Events): pick up a
  // champion from the picker, or an already-placed one straight off the
  // board/bench, and drop it on any hex/bench cell. Dropping outside the
  // board/bench removes it -- the only other way to clear a cell, since
  // this replaces the old click-to-arm-then-click-to-place flow entirely. --
  var dragGhost = null, dragSlug = null, dragOrigin = null, dragOverEl = null;

  function beginDrag(slug, origin, x, y) {
    dragSlug = slug;
    dragOrigin = origin; // null if fresh from the picker, else {zone, idx}
    dragGhost = document.createElement('img');
    dragGhost.src = champImg(slug);
    dragGhost.className = 'builder-drag-ghost';
    document.body.appendChild(dragGhost);
    document.body.classList.add('builder-dragging');
    positionGhost(x, y);
  }
  function positionGhost(x, y) {
    if (dragGhost) { dragGhost.style.left = x + 'px'; dragGhost.style.top = y + 'px'; }
  }
  function cellUnder(x, y) {
    var el = document.elementFromPoint(x, y);
    if (!el) return null;
    var hex = el.closest('.hex-cell');
    if (hex) return { zone: 'board', idx: parseInt(hex.dataset.idx, 10), el: hex };
    var bc = el.closest('.bench-cell');
    if (bc) return { zone: 'bench', idx: parseInt(bc.dataset.idx, 10), el: bc };
    return null;
  }
  document.addEventListener('pointermove', function (e) {
    if (!dragGhost) return;
    positionGhost(e.clientX, e.clientY);
    var hit = cellUnder(e.clientX, e.clientY);
    var el = hit ? hit.el : null;
    if (el !== dragOverEl) {
      if (dragOverEl) dragOverEl.dataset.dragover = 'false';
      if (el) el.dataset.dragover = 'true';
      dragOverEl = el;
    }
  });
  document.addEventListener('pointerup', function (e) {
    if (!dragGhost) return;
    document.body.removeChild(dragGhost);
    dragGhost = null;
    document.body.classList.remove('builder-dragging');
    if (dragOverEl) { dragOverEl.dataset.dragover = 'false'; dragOverEl = null; }

    var hit = cellUnder(e.clientX, e.clientY);
    if (hit) {
      var destArr = hit.zone === 'board' ? board : bench;
      var displaced = destArr[hit.idx];
      destArr[hit.idx] = dragSlug;
      if (dragOrigin && displaced) {
        // swap instead of losing the champion that was already there
        var originArr = dragOrigin.zone === 'board' ? board : bench;
        originArr[dragOrigin.idx] = displaced;
      }
    }
    // hit === null (dropped outside board/bench): already removed from
    // its origin below on pickup, so this is how a unit gets discarded.
    renderCells();
    renderTraitPanel();
    syncUrl();
    dragSlug = null; dragOrigin = null;
  });
  document.addEventListener('pointercancel', function () {
    if (!dragGhost) return;
    document.body.removeChild(dragGhost);
    dragGhost = null;
    document.body.classList.remove('builder-dragging');
    if (dragOverEl) { dragOverEl.dataset.dragover = 'false'; dragOverEl = null; }
    // Interrupted mid-drag (e.g. OS gesture) -- put it back where it came from.
    if (dragOrigin) {
      var arr = dragOrigin.zone === 'board' ? board : bench;
      arr[dragOrigin.idx] = dragSlug;
      renderCells();
    }
    dragSlug = null; dragOrigin = null;
  });

  // ---- Board / bench DOM (built once; only their filled state changes) ----
  function wireCellDrag(cell, zone) {
    cell.addEventListener('pointerdown', function (e) {
      var idx = parseInt(cell.dataset.idx, 10);
      var arr = zone === 'board' ? board : bench;
      var slug = arr[idx];
      if (!slug) return;
      e.preventDefault();
      arr[idx] = null;
      renderCells();
      renderTraitPanel();
      beginDrag(slug, { zone: zone, idx: idx }, e.clientX, e.clientY);
    });
  }
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
        wireCellDrag(cell, 'board');
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
      wireCellDrag(cell, 'bench');
      benchEl.appendChild(cell);
    }
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
      item.addEventListener('pointerdown', function (e) {
        e.preventDefault();
        beginDrag(c.slug, null, e.clientX, e.clientY);
      });
      picker.appendChild(item);
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
