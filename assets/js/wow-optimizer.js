(function () {
  'use strict';
  var root = window.BM_ROOT || '';
  var I = window.OP_I18N || {};
  var avatar = document.getElementById('opAvatar');
  var filters = document.getElementById('opFilters');
  if (!avatar || !filters) return;

  var slotButtons = Array.prototype.slice.call(avatar.querySelectorAll('.op-slot, .op-weapon-slot'));
  var picker = document.getElementById('opPicker');
  var pickerTitle = document.getElementById('opPickerTitle');
  var pickerClose = document.getElementById('opPickerClose');
  var pickerSearch = document.getElementById('opPickerSearch');
  var pickerList = document.getElementById('opPickerList');
  var pickerCount = document.getElementById('opPickerCount');
  var pickerRemove = document.getElementById('opPickerRemove');
  var pickerNone = document.getElementById('opPickerNone');
  var summaryStats = document.getElementById('opSummaryStats');
  var summaryEmpty = document.getElementById('opSummaryEmpty');
  var resetBtn = document.getElementById('opReset');
  var shareBtn = document.getElementById('opShare');
  var shareStatus = document.getElementById('opShareStatus');
  var raceSlot = document.getElementById('opRaceSlot');
  var racePicker = document.getElementById('opRacePicker');
  var racePickerClose = document.getElementById('opRacePickerClose');
  var raceRemove = document.getElementById('opRaceRemove');
  var raceOptions = racePicker ? Array.prototype.slice.call(racePicker.querySelectorAll('.op-race-option')) : [];
  var classSlot = document.getElementById('opClassSlot');
  var classPicker = document.getElementById('opClassPicker');
  var classPickerClose = document.getElementById('opClassPickerClose');
  var classRemove = document.getElementById('opClassRemove');
  var classOptions = classPicker ? Array.prototype.slice.call(classPicker.querySelectorAll('.op-race-option')) : [];
  var summaryNote = document.getElementById('opSummaryNote');
  var summaryIlvl = document.getElementById('opSummaryIlvl');
  var completionEl = document.getElementById('opCompletion');
  var pickerSort = document.getElementById('opPickerSort');

  var data = null;               // fetched wow-optimizer.json
  var slotByKey = {};             // key -> {key, label, gear}
  var itemById = {};              // item id -> {item, slotKey}
  var loadout = {};               // slotKey -> item
  var activeSlot = null;
  var race = null;                // {key, raceKey, name, icon} or null
  var charClass = null;           // {id, name, icon} or null

  function checked(facet) {
    return Array.prototype.slice.call(filters.querySelectorAll('input[data-facet="' + facet + '"]:checked')).map(function (i) { return i.value; });
  }

  function sourceText(it) {
    return it.sources.map(function (src) {
      if (src.kind === 'dungeon') return I.sourceDungeon.replace('{name}', src.name[I.lang]);
      if (src.boss) return I.sourceRaidBoss.replace('{name}', src.name[I.lang]).replace('{boss}', src.boss[I.lang]);
      return I.sourceRaid.replace('{name}', src.name[I.lang]);
    }).join(', ');
  }

  function iconUrl(it) {
    return 'https://wow.zamimg.com/images/wow/icons/large/' + it.icon + '.jpg';
  }

  function wowheadItemLink(it, innerHtml) {
    // href="#" + onclick="return false" (Wowhead's own documented "Custom URLs" pattern,
    // wowhead.com/tooltips) blocks the page-jump but still lets the click bubble up to
    // whatever ancestor button/row handles the actual pick/equip action. tabindex="-1" keeps
    // it out of the tab order (the ancestor button/row is already the real, single focus stop).
    return '<a href="https://www.wowhead.com/forever/item=' + it.id + '" onclick="return false" tabindex="-1">' + innerHtml + '</a>';
  }

  function refreshWowheadTooltips() {
    // 2026-09-26 (user-flagged: tooltips missing on some WoW: Forever pages): this page's item
    // names are rendered client-side after a fetch, but Wowhead's tooltips.js (loaded in
    // base.html's <head>) only scans the DOM once on its own init -- links added afterwards need
    // this explicit refreshLinks() call (its own public, documented API) or they never get wired.
    if (window.WH && WH.Tooltips && WH.Tooltips.refreshLinks) WH.Tooltips.refreshLinks(true);
  }

  function updateSlotVisual(slotKey) {
    var btn = avatar.querySelector('[data-slot="' + slotKey + '"]');
    if (!btn) return;
    var img = btn.querySelector('.op-item-icon');
    var empty = btn.querySelector('.op-slot-icon-empty');
    var nameEl = btn.querySelector('.op-slot-itemname');
    var ilvlEl = btn.querySelector('.op-slot-ilvl');
    var placeholder = btn.querySelector('.op-slot-placeholder');
    var it = loadout[slotKey];
    if (it) {
      img.src = iconUrl(it);
      img.hidden = false;
      empty.hidden = true;
      nameEl.innerHTML = wowheadItemLink(it, it.name);
      nameEl.className = 'op-slot-itemname dg-q' + it.q;
      nameEl.hidden = false;
      ilvlEl.textContent = (I.itemLevel || 'ilvl {lvl}').replace('{lvl}', it.lvl || it.req || '?');
      ilvlEl.hidden = false;
      placeholder.hidden = true;
      btn.title = it.name + ' — ' + sourceText(it);
      refreshWowheadTooltips();
    } else {
      img.hidden = true;
      empty.hidden = false;
      nameEl.hidden = true;
      nameEl.innerHTML = '';
      ilvlEl.hidden = true;
      placeholder.hidden = false;
      btn.title = '';
    }
  }

  function updateCompletion() {
    if (!completionEl) return;
    var filled = Object.keys(loadout).length;
    completionEl.textContent = (I.completion || '{filled}/{total}').replace('{filled}', filled).replace('{total}', I.totalSlots);
  }

  function renderSummary() {
    var totals = {};
    var order = [];
    function add(stats) {
      Object.keys(stats || {}).forEach(function (k) {
        if (!stats[k]) return;
        if (!(k in totals)) { totals[k] = 0; order.push(k); }
        totals[k] += stats[k];
      });
    }
    Object.keys(loadout).forEach(function (slotKey) {
      var st = {};
      Object.keys(loadout[slotKey].st || {}).forEach(function (k) { if (k !== 'speed') st[k] = loadout[slotKey].st[k]; });
      add(st);
    });
    var hasBaseStats = false;
    if (race && data.race_base_stats && data.race_base_stats[race.raceKey]) { add(data.race_base_stats[race.raceKey]); hasBaseStats = true; }
    if (charClass && data.class_bonus_stats && data.class_bonus_stats[charClass.id]) { add(data.class_bonus_stats[charClass.id]); hasBaseStats = true; }
    var ilvls = Object.keys(loadout).map(function (k) { return loadout[k].lvl; }).filter(function (v) { return v; });
    if (ilvls.length) {
      var avg = Math.round(ilvls.reduce(function (a, b) { return a + b; }, 0) / ilvls.length);
      summaryIlvl.hidden = false;
      summaryIlvl.textContent = (I.avgIlvl || '{lvl}').replace('{lvl}', avg);
    } else {
      summaryIlvl.hidden = true;
    }
    if (!order.length) {
      summaryEmpty.hidden = false;
      summaryStats.hidden = true;
      summaryStats.innerHTML = '';
      summaryNote.hidden = true;
      updateCompletion();
      return;
    }
    summaryEmpty.hidden = true;
    summaryStats.hidden = false;
    summaryNote.hidden = !hasBaseStats;
    var names = (data.stat_names || {})[I.lang] || {};
    summaryStats.innerHTML = order.map(function (k) {
      var v = Math.round(totals[k] * 100) / 100;
      var label = names[k] || k;
      return '<span>+' + v + ' ' + label + '</span>';
    }).join('');
    updateCompletion();
  }

  function syncUrl() {
    var parts = Object.keys(loadout).map(function (k) { return k + '=' + loadout[k].id; });
    if (race) parts.push('race=' + race.key);
    if (charClass) parts.push('class=' + charClass.id);
    if (window.history && history.replaceState) {
      history.replaceState(null, '', parts.length ? '#' + parts.join('&') : location.pathname + location.search);
    }
  }

  function updateRaceVisual() {
    if (!raceSlot) return;
    var img = raceSlot.querySelector('.op-race-icon');
    var placeholder = raceSlot.querySelector('.op-race-placeholder');
    var nameEl = raceSlot.querySelector('.op-race-name');
    if (race) {
      img.src = race.icon;
      img.hidden = false;
      placeholder.hidden = true;
      nameEl.textContent = race.name;
    } else {
      img.hidden = true;
      placeholder.hidden = false;
      nameEl.textContent = '';
    }
  }

  function updateClassVisual() {
    if (!classSlot) return;
    var img = classSlot.querySelector('.op-class-icon');
    var placeholder = classSlot.querySelector('.op-class-placeholder');
    var nameEl = classSlot.querySelector('.op-class-name');
    if (charClass) {
      img.src = charClass.icon;
      img.hidden = false;
      placeholder.hidden = true;
      nameEl.textContent = charClass.name;
    } else {
      img.hidden = true;
      placeholder.hidden = false;
      nameEl.textContent = '';
    }
  }

  function openRacePicker() {
    if (!racePicker) return;
    raceSlot.classList.add('is-active');
    raceRemove.hidden = !race;
    racePicker.hidden = false;
    racePicker.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function closeRacePicker() {
    if (!racePicker) return;
    racePicker.hidden = true;
    raceSlot.classList.remove('is-active');
  }

  function openClassPicker() {
    if (!classPicker) return;
    classSlot.classList.add('is-active');
    classRemove.hidden = !charClass;
    classPicker.hidden = false;
    classPicker.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function closeClassPicker() {
    if (!classPicker) return;
    classPicker.hidden = true;
    classSlot.classList.remove('is-active');
  }

  if (raceSlot) raceSlot.addEventListener('click', openRacePicker);
  if (racePickerClose) racePickerClose.addEventListener('click', closeRacePicker);
  raceOptions.forEach(function (opt) {
    opt.addEventListener('click', function () {
      race = { key: opt.getAttribute('data-race'), raceKey: opt.getAttribute('data-racekey'), name: opt.getAttribute('data-name'), icon: opt.getAttribute('data-icon') };
      updateRaceVisual();
      renderSummary();
      syncUrl();
      closeRacePicker();
    });
  });
  if (raceRemove) {
    raceRemove.addEventListener('click', function () {
      race = null;
      updateRaceVisual();
      renderSummary();
      syncUrl();
      closeRacePicker();
    });
  }

  if (classSlot) classSlot.addEventListener('click', openClassPicker);
  if (classPickerClose) classPickerClose.addEventListener('click', closeClassPicker);
  classOptions.forEach(function (opt) {
    opt.addEventListener('click', function () {
      charClass = { id: opt.getAttribute('data-class'), name: opt.getAttribute('data-name'), icon: opt.getAttribute('data-icon') };
      updateClassVisual();
      renderSummary();
      syncUrl();
      closeClassPicker();
    });
  });
  if (classRemove) {
    classRemove.addEventListener('click', function () {
      charClass = null;
      updateClassVisual();
      renderSummary();
      syncUrl();
      closeClassPicker();
    });
  }

  function matchesFilters(it) {
    var types = checked('type'), primary = checked('primary'), secondary = checked('secondary');
    var q = (pickerSearch.value || '').trim().toLowerCase();
    if (q && it.name.toLowerCase().indexOf(q) === -1) return false;
    var typeOk = types.length === 0 || types.indexOf(it.type.en) !== -1;
    var primaryOk = primary.length === 0 || primary.some(function (k) { return it.st[k] > 0; });
    var secondaryOk = secondary.every(function (k) { return it.st[k] > 0; });
    return typeOk && primaryOk && secondaryOk;
  }

  function statsText(it) {
    var names = (data.stat_names || {})[I.lang] || {};
    var order = ['str', 'agi', 'int', 'spi', 'sta', 'splpwr', 'spldmg', 'atkpwr', 'manargn', 'critstrkrtng', 'hastertng', 'hitrtng', 'defrtng', 'armor'];
    var parts = order.filter(function (k) { return it.st[k]; }).map(function (k) { return '+' + it.st[k] + ' ' + (names[k] || k); });
    if (it.st.dps) parts.push(it.st.dps + ' DPS' + (it.st.speed ? ' (' + it.st.speed + 's)' : ''));
    return parts.join(' · ');
  }

  // Compares a candidate item to whatever is currently in the active slot: real stat-by-stat deltas, plus a
  // fact -- not an opinion -- that it's a strict upgrade only when every shared/only-on-one-side stat is equal
  // or higher and at least one is strictly higher (so an item that trades one stat for another never qualifies).
  function compareToEquipped(it) {
    var current = loadout[activeSlot];
    if (!current || current.id === it.id) return null;
    var keys = {};
    Object.keys(it.st || {}).forEach(function (k) { if (k !== 'speed') keys[k] = 1; });
    Object.keys(current.st || {}).forEach(function (k) { if (k !== 'speed') keys[k] = 1; });
    var diffs = [];
    var isUpgrade = true, hasGain = false;
    Object.keys(keys).forEach(function (k) {
      var a = it.st[k] || 0, b = current.st[k] || 0;
      var d = Math.round((a - b) * 100) / 100;
      if (d !== 0) diffs.push({ k: k, d: d });
      if (d < 0) isUpgrade = false;
      if (d > 0) hasGain = true;
    });
    return { diffs: diffs, isUpgrade: isUpgrade && hasGain };
  }

  function renderPickerList() {
    if (!activeSlot) return;
    var slot = slotByKey[activeSlot];
    var matches = slot.gear.filter(matchesFilters);
    var sortMode = pickerSort ? pickerSort.value : 'name';
    matches = matches.slice().sort(function (a, b) {
      if (sortMode === 'ilvl') return (b.lvl || 0) - (a.lvl || 0);
      return a.name.localeCompare(b.name);
    });
    pickerCount.textContent = (I.pickerCount || '{n}').replace('{n}', matches.length);
    pickerNone.hidden = matches.length > 0;
    pickerList.innerHTML = '';
    var currentId = loadout[activeSlot] ? loadout[activeSlot].id : null;
    var names = (data.stat_names || {})[I.lang] || {};
    matches.forEach(function (it) {
      var row = document.createElement('button');
      row.type = 'button';
      row.className = 'op-picker-row';
      var badge = '';
      var cmp = compareToEquipped(it);
      if (it.id === currentId) badge = '<span class="op-badge op-badge-current">' + I.currentBadge + '</span>';
      else if (cmp && cmp.isUpgrade) badge = '<span class="op-badge op-badge-upgrade">' + I.upgradeBadge + '</span>';
      var diffHtml = '';
      if (cmp && cmp.diffs.length) {
        diffHtml = '<span class="op-picker-row-diff">' + I.vsCurrent + cmp.diffs.map(function (d) {
          var cls = d.d > 0 ? 'op-diff-pos' : 'op-diff-neg';
          var sign = d.d > 0 ? '+' : '';
          return '<span class="' + cls + '">' + sign + d.d + ' ' + (names[d.k] || d.k) + '</span>';
        }).join(' · ') + '</span>';
      }
      row.innerHTML = '<img src="' + iconUrl(it) + '" alt="" loading="lazy">' +
        '<span class="op-picker-row-text">' +
        '<span class="op-picker-row-name dg-q' + it.q + '">' + wowheadItemLink(it, it.name) + badge + '</span>' +
        '<span class="op-picker-row-meta">' + statsText(it) + ' — ' + sourceText(it) + '</span>' +
        diffHtml +
        '</span>';
      row.addEventListener('click', function () {
        loadout[activeSlot] = it;
        updateSlotVisual(activeSlot);
        renderSummary();
        syncUrl();
        closePicker();
      });
      pickerList.appendChild(row);
    });
    refreshWowheadTooltips();
  }

  function openPicker(slotKey) {
    activeSlot = slotKey;
    slotButtons.forEach(function (b) { b.classList.toggle('is-active', b.getAttribute('data-slot') === slotKey); });
    var slot = slotByKey[slotKey];
    pickerTitle.textContent = (I.chooseFor || '{slot}').replace('{slot}', slot.label[I.lang]);
    pickerRemove.hidden = !loadout[slotKey];
    picker.hidden = false;
    pickerSearch.value = '';
    renderPickerList();
    picker.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function closePicker() {
    picker.hidden = true;
    slotButtons.forEach(function (b) { b.classList.remove('is-active'); });
    activeSlot = null;
  }

  slotButtons.forEach(function (btn) {
    btn.addEventListener('click', function () { openPicker(btn.getAttribute('data-slot')); });
  });
  pickerClose.addEventListener('click', closePicker);
  pickerSearch.addEventListener('input', renderPickerList);
  filters.addEventListener('change', renderPickerList);
  if (pickerSort) pickerSort.addEventListener('change', renderPickerList);
  pickerRemove.addEventListener('click', function () {
    if (!activeSlot) return;
    delete loadout[activeSlot];
    updateSlotVisual(activeSlot);
    renderSummary();
    syncUrl();
    closePicker();
  });
  resetBtn.addEventListener('click', function () {
    Object.keys(loadout).forEach(function (k) { delete loadout[k]; updateSlotVisual(k); });
    filters.querySelectorAll('input[type="checkbox"]').forEach(function (i) { i.checked = false; });
    race = null;
    charClass = null;
    updateRaceVisual();
    updateClassVisual();
    renderSummary();
    if (window.history && history.replaceState) history.replaceState(null, '', location.pathname + location.search);
    closePicker();
    closeRacePicker();
    closeClassPicker();
  });
  if (shareBtn) {
    shareBtn.addEventListener('click', function () {
      var done = function () {
        shareStatus.textContent = I.shareCopied || 'Copied';
        shareStatus.hidden = false;
        setTimeout(function () { shareStatus.hidden = true; }, 2500);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(location.href).then(done, done);
      } else {
        done();
      }
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (!picker.hidden) closePicker();
    if (racePicker && !racePicker.hidden) closeRacePicker();
    if (classPicker && !classPicker.hidden) closeClassPicker();
  });

  fetch(root + 'assets/data/wow-optimizer.json').then(function (r) { return r.json(); }).then(function (json) {
    data = json;
    data.slots.forEach(function (s) {
      slotByKey[s.key] = s;
      s.gear.forEach(function (it) { itemById[it.id] = { item: it, slotKey: s.key }; });
    });
    var raceByKey = {};
    (data.races || []).forEach(function (r) { raceByKey[r.faction + '-' + r.key] = r; });
    var classById = {};
    (data.classes || []).forEach(function (c) { classById[c.id] = c; });
    // restore from the URL hash, e.g. #head=1234&chest=5678&race=horde-orc&class=warrior
    var hash = (location.hash || '').replace(/^#/, '');
    if (hash) {
      hash.split('&').forEach(function (part) {
        var eq = part.indexOf('=');
        if (eq < 0) return;
        var key = part.slice(0, eq), val = decodeURIComponent(part.slice(eq + 1));
        if (key === 'race') {
          var r = raceByKey[val];
          if (r) race = { key: val, raceKey: r.key, name: r.name[I.lang], icon: r.icon };
          return;
        }
        if (key === 'class') {
          var c = classById[val];
          if (c) charClass = { id: val, name: c.name[I.lang], icon: c.icon };
          return;
        }
        var id = +val, entry = itemById[id];
        if (entry && entry.slotKey === key) loadout[key] = entry.item;
      });
    }
    slotButtons.forEach(function (b) { updateSlotVisual(b.getAttribute('data-slot')); });
    updateRaceVisual();
    updateClassVisual();
    renderSummary();
  });
})();
