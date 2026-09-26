(function () {
  'use strict';
  var table = document.getElementById('dgTable');
  var filters = document.getElementById('dgFilters');
  if (!table || !filters) return;
  var tbody = table.querySelector('tbody');
  var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
  var originalOrder = rows.slice();
  var stats = rows.map(function (r) { try { return JSON.parse(r.getAttribute('data-stats') || '{}'); } catch (e) { return {}; } });
  var none = document.getElementById('dgNone');
  var count = document.getElementById('dgCount');
  var reset = document.getElementById('dgReset');
  var levelMin = document.getElementById('dgLevelMin');
  var levelMax = document.getElementById('dgLevelMax');
  var sortHeader = document.getElementById('dgSortReq');
  var reqSort = null; // null = original order, true = ascending, false = descending

  function checked(facet) {
    return Array.prototype.slice.call(filters.querySelectorAll('input[data-facet="' + facet + '"]:checked')).map(function (i) { return i.value; });
  }

  function apply() {
    var types = checked('type'), primary = checked('primary'), secondary = checked('secondary');
    var minL = levelMin.value !== '' ? +levelMin.value : null;
    var maxL = levelMax.value !== '' ? +levelMax.value : null;
    var shown = 0;
    rows.forEach(function (r, i) {
      var st = stats[i];
      var req = +r.getAttribute('data-req');
      var typeOk = types.length === 0 || types.indexOf(r.getAttribute('data-type')) !== -1;
      var primaryOk = primary.length === 0 || primary.some(function (k) { return st[k] > 0; });
      var secondaryOk = secondary.every(function (k) { return st[k] > 0; });
      var levelOk = (minL === null || req >= minL) && (maxL === null || req <= maxL);
      var ok = typeOk && primaryOk && secondaryOk && levelOk;
      r.hidden = !ok;
      if (ok) shown++;
    });
    none.hidden = shown > 0;
    count.textContent = (window.dgCountTpl || '{shown}/{total}').replace('{shown}', shown).replace('{total}', rows.length);
    if (window.history && history.replaceState) {
      var parts = [];
      if (types.length) parts.push('type=' + types.join(','));
      if (primary.length) parts.push('primary=' + primary.join(','));
      if (secondary.length) parts.push('secondary=' + secondary.join(','));
      if (minL !== null || maxL !== null) parts.push('level=' + (minL === null ? '' : minL) + '-' + (maxL === null ? '' : maxL));
      if (reqSort !== null) parts.push('sort=' + (reqSort ? 'asc' : 'desc'));
      history.replaceState(null, '', parts.length ? '#' + parts.join('&') : location.pathname + location.search);
    }
  }

  function sortByReq(asc) {
    var order = asc === null ? originalOrder : rows.slice().sort(function (a, b) {
      var av = +a.getAttribute('data-req'), bv = +b.getAttribute('data-req');
      return asc ? av - bv : bv - av;
    });
    order.forEach(function (r) { tbody.appendChild(r); });
    reqSort = asc;
    sortHeader.classList.toggle('is-asc', asc === true);
    sortHeader.classList.toggle('is-desc', asc === false);
    apply();
  }

  function toggleSort() {
    sortByReq(reqSort === true ? false : true);
  }
  sortHeader.addEventListener('click', toggleSort);
  sortHeader.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleSort(); }
  });

  filters.addEventListener('change', apply);
  filters.addEventListener('input', apply);
  reset.addEventListener('click', function () {
    filters.querySelectorAll('input[type="checkbox"]').forEach(function (i) { i.checked = false; });
    levelMin.value = '';
    levelMax.value = '';
    sortByReq(null);
  });

  // restore from the URL hash, e.g. #type=Mail&primary=agi&secondary=critstrkrtng,hastertng&level=20-40&sort=asc
  var hash = (location.hash || '').replace(/^#/, '');
  var startSort = null;
  if (hash) {
    hash.split('&').forEach(function (part) {
      var eq = part.indexOf('=');
      if (eq < 0) return;
      var facet = part.slice(0, eq), raw = decodeURIComponent(part.slice(eq + 1));
      if (facet === 'level') {
        var m = /^(-?\d*)-(-?\d*)$/.exec(raw);
        if (m) { levelMin.value = m[1]; levelMax.value = m[2]; }
        return;
      }
      if (facet === 'sort') { startSort = raw === 'asc' ? true : raw === 'desc' ? false : null; return; }
      raw.split(',').forEach(function (v) {
        var box = filters.querySelector('input[data-facet="' + facet + '"][value="' + v + '"]');
        if (box) box.checked = true;
      });
    });
  }
  if (startSort !== null) { sortByReq(startSort); } else { apply(); }
})();
