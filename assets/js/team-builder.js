
(function () {
  var ROOT = window.BM_ROOT || '';
  var I = window.BM_BUILDER_I18N || {};
  var ROWS = 4, COLS = 7;

  var picker = document.getElementById('champPicker');
  var boardEl = document.getElementById('hexBoard');
  var traitPanel = document.getElementById('traitPanel');
  var searchInput = document.getElementById('builderSearch');
  var costFilters = document.getElementById('builderCostFilters');
  var emptyHint = document.getElementById('builderEmptyHint');
  var resetBtn = document.getElementById('builderReset');
  var shareBtn = document.getElementById('builderShare');
  var copyGameBtn = document.getElementById('builderCopyGame');
  var shareStatus = document.getElementById('builderShareStatus');
  if (!picker || !boardEl) return;

  var champions = [];
  var champBySlug = {};
  var traitDefs = [];
  var plannerHeader = '02';
  var setMutator = '';
  var board = new Array(ROWS * COLS).fill(null);
  var activeCostFilter = 'ALL';

  function champImg(slug) {
    return ROOT + 'assets/champions/' + slug + '.png';
  }
  function traitImg(slug) {
    return ROOT + 'assets/traits/' + slug + '.png';
  }

  // ---- Placement: two ways in, on purpose --------------------------------
  // 1) Drag and drop (mouse + touch via Pointer Events): pick up a champion
  //    from the picker, or an already-placed one straight off the board,
  //    and drop it on any hex cell. Dropping outside the board removes it.
  //    (No bench -- deliberate: it doesn't count toward traits in the real
  //    game either, so it added a UI section without adding anything a
  //    comp-building tool needs.)
  // 2) Tap-to-arm: a plain click/tap (no real movement) on a picker
  //    champion "arms" it instead -- a persistent border/glow, not a
  //    fleeting mid-drag one -- and the next tap on any cell places it
  //    there. Needed because a real drag's "currently held" highlight
  //    collapses to a few milliseconds for a plain click, invisible in
  //    practice; this is what actually answers "show me what I picked".
  var dragGhost = null, dragSlug = null, dragOrigin = null, dragOverEl = null;
  var dragSourcePickerEl = null, dragStartX = 0, dragStartY = 0, dragMoved = false;
  var armedSlug = null, armedPickerEl = null;
  var TAP_THRESHOLD = 6; // px of movement below which a press counts as a tap, not a drag

  function setArmed(slug, pickerEl) {
    if (armedPickerEl) armedPickerEl.dataset.armed = 'false';
    armedSlug = slug;
    armedPickerEl = pickerEl || null;
    if (armedPickerEl) armedPickerEl.dataset.armed = 'true';
  }
  function clearDragSourceHighlight() {
    if (dragSourcePickerEl) { dragSourcePickerEl.dataset.dragging = 'false'; dragSourcePickerEl = null; }
  }

  function beginDrag(slug, origin, x, y, pickerEl) {
    dragSlug = slug;
    dragOrigin = origin; // null if fresh from the picker, else the board index it came from
    dragStartX = x; dragStartY = y; dragMoved = false;
    dragSourcePickerEl = pickerEl || null;
    if (dragSourcePickerEl) dragSourcePickerEl.dataset.dragging = 'true';
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
    if (hex) return { idx: parseInt(hex.dataset.idx, 10), el: hex };
    return null;
  }
  function placeArmedOn(idx) {
    board[idx] = armedSlug;
    setArmed(null, null);
    renderCells();
    renderTraitPanel();
    syncUrl();
  }
  document.addEventListener('pointermove', function (e) {
    if (!dragGhost) return;
    positionGhost(e.clientX, e.clientY);
    if (Math.abs(e.clientX - dragStartX) + Math.abs(e.clientY - dragStartY) > TAP_THRESHOLD) dragMoved = true;
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

    if (!dragMoved && dragOrigin === null) {
      // A tap (not a drag) on a picker champion: arm it instead of
      // cancelling. Re-tapping the already-armed one toggles it off.
      // (Grab the source element BEFORE clearing it -- clearDragSourceHighlight()
      // nulls out dragSourcePickerEl as a side effect.)
      var tappedEl = dragSourcePickerEl;
      var wasThisOneArmed = armedPickerEl === tappedEl;
      clearDragSourceHighlight();
      setArmed(wasThisOneArmed ? null : dragSlug, wasThisOneArmed ? null : tappedEl);
      dragSlug = null; dragOrigin = null;
      return;
    }
    clearDragSourceHighlight();

    var hit = cellUnder(e.clientX, e.clientY);
    if (hit) {
      var displaced = board[hit.idx];
      board[hit.idx] = dragSlug;
      if (dragOrigin !== null && displaced) {
        // swap instead of losing the champion that was already there
        board[dragOrigin] = displaced;
      }
    }
    // hit === null (dropped outside the board): already removed from its
    // origin below on pickup, so this is how a unit gets discarded.
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
    clearDragSourceHighlight();
    // Interrupted mid-drag (e.g. OS gesture) -- put it back where it came from.
    if (dragOrigin !== null) {
      board[dragOrigin] = dragSlug;
      renderCells();
    }
    dragSlug = null; dragOrigin = null;
  });

  // ---- Board DOM (built once; only its filled state changes) ----
  function wireCellDrag(cell) {
    cell.addEventListener('pointerdown', function (e) {
      var idx = parseInt(cell.dataset.idx, 10);
      if (armedSlug) {
        e.preventDefault();
        placeArmedOn(idx);
        return;
      }
      var slug = board[idx];
      if (!slug) return;
      e.preventDefault();
      board[idx] = null;
      renderCells();
      renderTraitPanel();
      beginDrag(slug, idx, e.clientX, e.clientY);
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
        wireCellDrag(cell);
        rowEl.appendChild(cell);
      }
      boardEl.appendChild(rowEl);
    }
  }

  function renderCells() {
    var boardCells = boardEl.querySelectorAll('.hex-cell');
    board.forEach(function (slug, i) { paintCell(boardCells[i], slug); });
    if (emptyHint) emptyHint.hidden = board.some(Boolean);
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
      item.style.setProperty('--picker-cost-color', 'var(--cost-' + (c.cost || 1) + ')');
      item.title = c.name;
      item.innerHTML = '<img src="' + champImg(c.slug) + '" alt="' + c.name + '" loading="lazy">';
      item.addEventListener('pointerdown', function (e) {
        e.preventDefault();
        if (armedPickerEl && armedPickerEl !== item) setArmed(null, null);
        beginDrag(c.slug, null, e.clientX, e.clientY, item);
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
    var qs = b.length ? ('b=' + b.join(',')) : '';
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
  }
  function loadFromUrl() {
    var params = new URLSearchParams(location.search);
    (params.get('b') || '').split(',').forEach(function (pair) {
      var m = pair.split(':');
      var idx = parseInt(m[0], 10), slug = m[1];
      if (slug && champBySlug[slug] && idx >= 0 && idx < board.length) board[idx] = slug;
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
  function showStatus(text, isError) {
    if (!shareStatus) return;
    shareStatus.hidden = false;
    shareStatus.textContent = text || '';
    shareStatus.dataset.error = isError ? 'true' : 'false';
    setTimeout(function () { shareStatus.hidden = true; }, 2200);
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      board = new Array(ROWS * COLS).fill(null);
      setArmed(null, null);
      renderCells();
      renderTraitPanel();
      history.replaceState(null, '', location.pathname);
    });
  }
  if (shareBtn) {
    shareBtn.addEventListener('click', function () {
      copyToClipboard(location.href).then(function () { showStatus(I.shareCopied, false); });
    });
  }
  if (copyGameBtn) {
    // Same encoding the real /compo/ pages' copy button uses (see
    // team_planner_code() in build_site.py): header + 10 slots of
    // 3-hex-digit per-champion codes (blank = "000") + the set mutator.
    // Board order (top-left to bottom-right by hex index) is as good an
    // order as any -- the game's planner doesn't care about slot order,
    // only which champions are in it.
    copyGameBtn.addEventListener('click', function () {
      var placed = board.filter(Boolean);
      if (!placed.length) { showStatus(I.copyGameEmpty, true); return; }
      var slots = placed.slice(0, 10).map(function (slug) {
        var c = champBySlug[slug];
        return (c && c.planner_code) || '000';
      });
      while (slots.length < 10) slots.push('000');
      var code = plannerHeader + slots.join('') + setMutator;
      copyToClipboard(code).then(function () { showStatus(I.copyGameCopied, false); });
    });
  }

  fetch(ROOT + 'assets/data/builder.json').then(function (r) { return r.json(); }).then(function (data) {
    champions = data.champions || [];
    traitDefs = data.traits || [];
    plannerHeader = data.plannerHeader || plannerHeader;
    setMutator = data.setMutator || '';
    champions.forEach(function (c) { champBySlug[c.slug] = c; });
    buildPicker();
    buildBoard();
    loadFromUrl();
    renderCells();
    renderTraitPanel();
  }).catch(function () {});
})();
