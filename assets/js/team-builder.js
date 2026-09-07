
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
  var itemPicker = document.getElementById('itemPicker');
  var itemSearchInput = document.getElementById('builderItemSearch');
  if (!picker || !boardEl) return;

  var MAX_ITEMS_PER_UNIT = 3;
  var champions = [];
  var champBySlug = {};
  var traitDefs = [];
  var items = [];
  var itemBySlug = {};
  var plannerHeader = '02';
  var setMutator = '';
  // Each board cell is null (empty) or {slug, items: [itemSlug, ...]} (up
  // to MAX_ITEMS_PER_UNIT) -- items travel with a champion when it's moved
  // or swapped, same object reference, never resynthesized.
  var board = new Array(ROWS * COLS).fill(null);
  var activeCostFilter = 'ALL';
  var armedItemSlug = null, armedItemEl = null;

  function champImg(slug) {
    return ROOT + 'assets/champions/' + slug + '.png';
  }
  function traitImg(slug) {
    return ROOT + 'assets/traits/' + slug + '.png';
  }
  function itemImg(slug) {
    return ROOT + 'assets/items/' + slug + '.png';
  }
  function itemLabel(it) {
    return (I.lang === 'fr' && it.name_fr) ? it.name_fr : it.name;
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
  var dragGhost = null, dragSlug = null, dragItems = [], dragOrigin = null, dragOverEl = null;
  var dragSourcePickerEl = null, dragStartX = 0, dragStartY = 0, dragMoved = false;
  var armedSlug = null, armedPickerEl = null;
  var TAP_THRESHOLD = 6; // px of movement below which a press counts as a tap, not a drag

  function setArmed(slug, pickerEl) {
    if (armedPickerEl) armedPickerEl.dataset.armed = 'false';
    armedSlug = slug;
    armedPickerEl = pickerEl || null;
    if (armedPickerEl) armedPickerEl.dataset.armed = 'true';
    if (slug) setArmedItem(null, null); // mutually exclusive with an armed item
  }
  function setArmedItem(slug, el) {
    if (armedItemEl) armedItemEl.dataset.armed = 'false';
    armedItemSlug = slug;
    armedItemEl = el || null;
    if (armedItemEl) armedItemEl.dataset.armed = 'true';
    if (slug) setArmed(null, null); // mutually exclusive with an armed champion
  }
  function clearDragSourceHighlight() {
    if (dragSourcePickerEl) { dragSourcePickerEl.dataset.dragging = 'false'; dragSourcePickerEl = null; }
  }

  function beginDrag(slug, origin, x, y, pickerEl, sourceItems) {
    dragSlug = slug;
    dragItems = sourceItems || [];
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
    board[idx] = { slug: armedSlug, items: [] };
    setArmed(null, null);
    renderCells();
    renderTraitPanel();
    syncUrl();
  }
  function attachArmedItemOn(idx) {
    var cellData = board[idx];
    if (!cellData) return; // items only attach to an already-placed champion, leave it armed
    if (cellData.items.length >= MAX_ITEMS_PER_UNIT) {
      showStatus(I.itemSlotsFull, true);
      return;
    }
    cellData.items.push(armedItemSlug);
    setArmedItem(null, null);
    renderCells();
    syncUrl();
  }
  function removeItemFrom(idx, itemSlug) {
    var cellData = board[idx];
    if (!cellData) return;
    var pos = cellData.items.indexOf(itemSlug);
    if (pos === -1) return;
    cellData.items.splice(pos, 1);
    renderCells();
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
      board[hit.idx] = { slug: dragSlug, items: dragItems };
      if (dragOrigin !== null && displaced) {
        // swap instead of losing the champion that was already there
        board[dragOrigin] = displaced;
      }
    }
    // hit === null (dropped outside the board): already removed from its
    // origin below on pickup, so this is how a unit (and its items) gets discarded.
    renderCells();
    renderTraitPanel();
    syncUrl();
    dragSlug = null; dragItems = []; dragOrigin = null;
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
      board[dragOrigin] = { slug: dragSlug, items: dragItems };
      renderCells();
    }
    dragSlug = null; dragItems = []; dragOrigin = null;
  });

  // ---- Board DOM (built once; only its filled state changes) ----
  function wireCellDrag(cell) {
    cell.addEventListener('pointerdown', function (e) {
      var idx = parseInt(cell.dataset.idx, 10);
      // Tapping directly on an already-equipped item icon, with nothing
      // armed, removes just that item -- checked first so it never falls
      // through to "pick up the whole champion to move it".
      var iconHit = e.target.closest('.hex-item-icon');
      if (iconHit && !armedSlug && !armedItemSlug) {
        e.preventDefault();
        e.stopPropagation();
        removeItemFrom(idx, iconHit.dataset.itemSlug);
        return;
      }
      if (armedSlug) {
        e.preventDefault();
        placeArmedOn(idx);
        return;
      }
      if (armedItemSlug) {
        e.preventDefault();
        attachArmedItemOn(idx);
        return;
      }
      var cellData = board[idx];
      if (!cellData) return;
      e.preventDefault();
      board[idx] = null;
      renderCells();
      renderTraitPanel();
      beginDrag(cellData.slug, idx, e.clientX, e.clientY, null, cellData.items);
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
    board.forEach(function (cellData, i) { paintCell(boardCells[i], cellData); });
    if (emptyHint) emptyHint.hidden = board.some(Boolean);
  }
  function paintCell(el, cellData) {
    if (!el) return;
    var slug = cellData && cellData.slug;
    if (slug && champBySlug[slug]) {
      el.dataset.filled = 'true';
      var itemsHtml = (cellData.items || []).map(function (itSlug) {
        var it = itemBySlug[itSlug];
        var label = it ? itemLabel(it) : '';
        return '<img class="hex-item-icon" data-item-slug="' + itSlug + '" src="' + itemImg(itSlug) + '" alt="' + label + '" title="' + label + '" loading="lazy">';
      }).join('');
      el.innerHTML = '<img class="hex-champ-icon" src="' + champImg(slug) + '" alt="' + champBySlug[slug].name + '" loading="lazy">' +
        (itemsHtml ? '<div class="hex-item-row">' + itemsHtml + '</div>' : '');
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

  // ---- Item picker: tap an item to arm it (same persistent-highlight
  // convention as an armed champion, see setArmed), then tap an
  // already-placed champion's hex to equip it there. Deliberately no
  // drag-and-drop for items -- they attach to an existing unit, not to a
  // hex coordinate, so "tap the target" reads clearer than dragging a small
  // icon onto an even smaller part of the board. ----
  function buildItemPicker() {
    if (!itemPicker) return;
    itemPicker.innerHTML = '';
    items.forEach(function (it) {
      var el = document.createElement('div');
      el.className = 'item-picker-item';
      el.dataset.slug = it.slug;
      el.dataset.name = it.name.toLowerCase();
      var label = itemLabel(it);
      el.title = label;
      el.innerHTML = '<img src="' + itemImg(it.slug) + '" alt="' + label + '" loading="lazy">';
      el.addEventListener('click', function () {
        var wasArmed = armedItemSlug === it.slug;
        setArmedItem(wasArmed ? null : it.slug, wasArmed ? null : el);
      });
      itemPicker.appendChild(el);
    });
  }
  if (itemSearchInput) {
    itemSearchInput.addEventListener('input', function () {
      var q = itemSearchInput.value.trim().toLowerCase();
      itemPicker.querySelectorAll('.item-picker-item').forEach(function (el) {
        el.dataset.hidden = (!q || el.dataset.name.indexOf(q) !== -1) ? 'false' : 'true';
      });
    });
  }

  // ---- Trait synergy panel (board only, matches real TFT rules) ----
  function renderTraitPanel() {
    if (!traitPanel) return;
    var counts = {};
    board.forEach(function (cellData) {
      var c = cellData && champBySlug[cellData.slug];
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
      var traitName = I.lang === 'fr' && r.t.name_fr ? r.t.name_fr : r.t.name;
      return '<div class="trait-row" data-active="' + (r.activeIdx >= 0) + '"' +
        (r.activeIdx >= 0 ? ' data-tier="' + r.activeIdx + '"' : '') + '>' +
        '<img src="' + traitImg(r.t.slug) + '" alt="' + traitName + '" loading="lazy">' +
        '<span class="trait-row-name">' + traitName + '</span>' +
        '<span class="trait-row-count">' + label + '</span></div>';
    }).join('');
  }

  // ---- Shareable URL state ----
  function syncUrl() {
    var b = [];
    board.forEach(function (cellData, i) {
      if (!cellData) return;
      // "." can't appear inside a slug (kebab-case: letters/digits/hyphens
      // only), so it's a safe separator for the item list appended after
      // the champion slug -- old share links with no items still parse
      // fine (rest.slice(1) is just empty).
      var entry = i + ':' + cellData.slug;
      if (cellData.items && cellData.items.length) entry += '.' + cellData.items.join('.');
      b.push(entry);
    });
    var qs = b.length ? ('b=' + b.join(',')) : '';
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
  }
  function loadFromUrl() {
    var params = new URLSearchParams(location.search);
    (params.get('b') || '').split(',').forEach(function (pair) {
      if (!pair) return;
      var m = pair.split(':');
      var idx = parseInt(m[0], 10);
      var rest = (m[1] || '').split('.');
      var slug = rest[0];
      var itemSlugs = rest.slice(1).filter(function (s) { return itemBySlug[s]; });
      if (slug && champBySlug[slug] && idx >= 0 && idx < board.length) {
        board[idx] = { slug: slug, items: itemSlugs.slice(0, MAX_ITEMS_PER_UNIT) };
      }
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
      setArmedItem(null, null);
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
      // Items aren't part of this format at all -- the real in-game Team
      // Planner paste is champions only, confirmed against a live test
      // (see team_planner_code()'s docstring in build_site.py).
      var slots = placed.slice(0, 10).map(function (cellData) {
        var c = champBySlug[cellData.slug];
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
    items = data.items || [];
    plannerHeader = data.plannerHeader || plannerHeader;
    setMutator = data.setMutator || '';
    champions.forEach(function (c) { champBySlug[c.slug] = c; });
    items.forEach(function (it) { itemBySlug[it.slug] = it; });
    buildPicker();
    buildItemPicker();
    buildBoard();
    loadFromUrl();
    renderCells();
    renderTraitPanel();
  }).catch(function () {});
})();
