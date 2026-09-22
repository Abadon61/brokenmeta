(function () {
  'use strict';
  var table = document.getElementById('dgTable');
  var filters = document.getElementById('dgFilters');
  if (!table || !filters) return;
  var rows = Array.prototype.slice.call(table.querySelectorAll('tbody tr'));
  var stats = rows.map(function (r) { try { return JSON.parse(r.getAttribute('data-stats') || '{}'); } catch (e) { return {}; } });
  var none = document.getElementById('dgNone');
  var count = document.getElementById('dgCount');
  var reset = document.getElementById('dgReset');

  function checked(facet) {
    return Array.prototype.slice.call(filters.querySelectorAll('input[data-facet="' + facet + '"]:checked')).map(function (i) { return i.value; });
  }

  function apply() {
    var types = checked('type'), primary = checked('primary'), secondary = checked('secondary');
    var shown = 0;
    rows.forEach(function (r, i) {
      var st = stats[i];
      var typeOk = types.length === 0 || types.indexOf(r.getAttribute('data-type')) !== -1;
      var primaryOk = primary.length === 0 || primary.some(function (k) { return st[k] > 0; });
      var secondaryOk = secondary.every(function (k) { return st[k] > 0; });
      var ok = typeOk && primaryOk && secondaryOk;
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
      history.replaceState(null, '', parts.length ? '#' + parts.join('&') : location.pathname + location.search);
    }
  }

  filters.addEventListener('change', apply);
  reset.addEventListener('click', function () {
    filters.querySelectorAll('input[type="checkbox"]').forEach(function (i) { i.checked = false; });
    apply();
  });

  // restore from the URL hash, e.g. #type=Mail&primary=agi&secondary=critstrkrtng,hastertng
  var hash = (location.hash || '').replace(/^#/, '');
  if (hash) {
    hash.split('&').forEach(function (part) {
      var eq = part.indexOf('=');
      if (eq < 0) return;
      var facet = part.slice(0, eq), values = decodeURIComponent(part.slice(eq + 1)).split(',');
      values.forEach(function (v) {
        var box = filters.querySelector('input[data-facet="' + facet + '"][value="' + v + '"]');
        if (box) box.checked = true;
      });
    });
  }
  apply();
})();
