
(function () {
  var rows = Array.prototype.slice.call(document.querySelectorAll('.comp-row'));
  if (!rows.length) return;
  var groups = Array.prototype.slice.call(document.querySelectorAll('[data-tier-group]'));
  var bar = document.getElementById('typeFilterBar');
  var searchInput = document.getElementById('compSearch');
  var emptyState = document.getElementById('emptyState');
  var activeType = 'ALL';

  // Homepage only (see macros.html's comp_summary_row): a row past the
  // top-15-per-tier default view ships its unit/item board as a JSON blob
  // instead of real <img> markup -- real icon markup for ~90% of the
  // comps most visitors never scroll to was most of the homepage's DOM
  // weight (SEO/perf audit, 2026-09-16). Built for real the first time
  // this row is actually about to be shown (search match or a rank-filter
  // recombination puts it back in view), then never touched again.
  var STAR_SVG_UNIT = '<svg viewBox="0 0 24 24"><path d="M12 2.5l2.97 6.28 6.93.7-5.13 4.75 1.4 6.87L12 17.9l-6.17 3.2 1.4-6.87-5.13-4.75 6.93-.7z"/></svg>';
  function hydrateRow(row) {
    var el = row.querySelector('.units-row[data-units-lazy]');
    if (!el) return;
    var units;
    try { units = JSON.parse(el.dataset.unitsLazy); } catch (e) { units = null; }
    el.removeAttribute('data-units-lazy');
    if (!units) return;
    var root = window.BM_ROOT || '';
    el.innerHTML = units.map(function (u) {
      var corners = u.is_top ? '<span class="unit-corner tl"></span><span class="unit-corner tr"></span><span class="unit-corner bl"></span><span class="unit-corner br"></span>' : '';
      var stars = u.three_star ? '<span class="star-row">' + STAR_SVG_UNIT + STAR_SVG_UNIT + STAR_SVG_UNIT + '</span>' : '';
      var itemsHtml = (u.shown_items || []).map(function (item) {
        return '<img class="item-icon" src="' + root + 'assets/items/' + item.slug + '.png" alt="' + item.name + '" title="' + item.name + '" loading="lazy">';
      }).join('');
      return '<div class="unit-cell"><div class="unit-icon-wrap">' + corners
        + '<img class="unit-icon champ-link-icon" src="' + root + 'assets/champions/' + u.slug + '.png" alt="' + u.champion + '" loading="lazy" style="border-color:var(--cost-' + (u.cost || 1) + ')" data-champ-slug="' + u.slug + '" data-champ-href="' + root + 'champions/' + u.slug + '/">'
        + stars + '</div><div class="unit-items">' + itemsHtml + '</div></div>';
    }).join('');
  }

  function applyFilters() {
    var q = (searchInput ? searchInput.value.trim().toLowerCase() : '');
    var visible = 0;
    rows.forEach(function (row) {
      var typeOk = activeType === 'ALL' || row.dataset.playstyleCat === activeType;
      var searchOk = !q || (row.dataset.search || '').indexOf(q) !== -1;
      // rankHidden is owned by assets/js/rank-filter.js (homepage only) --
      // it's how the 15-per-tier preview cap AND the rank checkbox filter
      // both hide rows, so a comp-row's real visibility is normally the AND
      // of all three, computed in this one place. EXCEPT while actively
      // searching: a real bug report caught this -- typing an exact comp
      // name (e.g. "greenfather tristana", ranked #80 of 95 in its tier,
      // so outside the top-15 preview) matched searchOk fine but still
      // never appeared, because the preview cap's rankHidden=true silently
      // won the AND. A text search is an explicit "find this specific
      // comp" intent, so it should surface any real match regardless of
      // the preview cap -- bypass rankHidden entirely whenever there's a
      // query, instead of only defeating it for the (rare) case of a
      // comp disqualified by an actively-selected rank bracket.
      var rankOk = q ? true : row.dataset.rankHidden !== 'true';
      var show = typeOk && searchOk && rankOk;
      if (show) hydrateRow(row);
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
