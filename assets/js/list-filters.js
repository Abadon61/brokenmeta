
(function () {
  var rows = Array.prototype.slice.call(document.querySelectorAll('.comp-row'));
  if (!rows.length) return;
  var groups = Array.prototype.slice.call(document.querySelectorAll('[data-tier-group]'));
  var bar = document.getElementById('typeFilterBar');
  var searchInput = document.getElementById('compSearch');
  var emptyState = document.getElementById('emptyState');
  var activeType = 'ALL';

  function applyFilters() {
    var q = (searchInput ? searchInput.value.trim().toLowerCase() : '');
    var visible = 0;
    rows.forEach(function (row) {
      var typeOk = activeType === 'ALL' || row.dataset.playstyleCat === activeType;
      var searchOk = !q || (row.dataset.search || '').indexOf(q) !== -1;
      // rankHidden is owned by assets/js/rank-filter.js (homepage only) --
      // it's how the 15-per-tier preview cap AND the rank checkbox filter
      // both hide rows, so a comp-row's real visibility is always the AND
      // of all three, computed in this one place.
      var rankOk = row.dataset.rankHidden !== 'true';
      var show = typeOk && searchOk && rankOk;
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    groups.forEach(function (group) {
      var groupVisible = group.querySelectorAll('.comp-row').length
        && Array.prototype.some.call(group.querySelectorAll('.comp-row'), function (r) { return r.style.display !== 'none'; });
      group.style.display = groupVisible ? '' : 'none';
    });
    if (emptyState) {
      emptyState.hidden = visible !== 0;
      if (visible === 0) {
        emptyState.textContent = q
          ? (window.BM_I18N_EMPTY_SEARCH || '').replace('__Q__', searchInput.value.trim())
          : (window.BM_I18N_EMPTY_FILTER || '');
      }
    }
  }

  if (bar) {
    bar.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-filter-type]');
      if (!btn) return;
      [].forEach.call(bar.querySelectorAll('[data-filter-type]'), function (b) { b.dataset.active = String(b === btn); });
      activeType = btn.dataset.filterType;
      applyFilters();
    });
  }
  if (searchInput) searchInput.addEventListener('input', applyFilters);
  window.BM_applyListFilters = applyFilters;
})();
