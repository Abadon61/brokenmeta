
(function () {
  var dropdown = document.getElementById('rankFilterDropdown');
  if (!dropdown) return;
  var summaryEl = document.getElementById('rankFilterSummary');
  var applyBtn = document.getElementById('rankFilterApply');
  var checks = Array.prototype.slice.call(dropdown.querySelectorAll('.rank-option-check'));
  var rows = Array.prototype.slice.call(document.querySelectorAll('.comp-row[data-key]'));
  if (!rows.length) return;
  var groups = {};
  Array.prototype.slice.call(document.querySelectorAll('[data-tier-group]')).forEach(function (g) {
    groups[g.dataset.tierGroup] = g.querySelector('.tier-rows');
  });
  var seeFullLinks = Array.prototype.slice.call(document.querySelectorAll('.see-full-tier-link'));
  var summaryChip = dropdown.querySelector('summary');
  var I18N = window.BM_RANK_FILTER_I18N || {};

  // Snapshot the server-rendered ("all ranks", full real dataset) truth --
  // restored verbatim whenever every bracket ends up checked again, so
  // re-checking everything never leaves the page showing the smaller
  // live-collected per-bracket sample instead of the site's real numbers.
  var original = {};
  rows.forEach(function (row) {
    var pills = row.querySelectorAll('.p-value');
    original[row.dataset.key] = {
      tier: row.dataset.tier,
      rankHidden: row.dataset.previewHidden === 'true',
      placementText: pills[0] ? pills[0].textContent : '',
      top4Text: pills[1] ? pills[1].textContent : '',
      contestText: pills[2] ? pills[2].textContent : '',
      contestLevel: pills[2] ? pills[2].getAttribute('data-level') : '',
    };
    row.dataset.rankHidden = original[row.dataset.key].rankHidden ? 'true' : 'false';
  });
  if (window.BM_applyListFilters) window.BM_applyListFilters();

  var data = null;
  fetch((window.BM_ROOT || '') + 'assets/data/rank-filter.json').then(function (r) { return r.json(); }).then(function (d) { data = d; }).catch(function () {});

  function updateSummary(selected) {
    if (!summaryEl) return;
    if (selected.length === checks.length) { summaryEl.textContent = I18N.allLabel || ''; return; }
    if (selected.length === 1) {
      var opt = dropdown.querySelector('.rank-option-check[value="' + selected[0] + '"]');
      var nameEl = opt && opt.closest('.rank-option').querySelector('.rank-option-name');
      summaryEl.textContent = nameEl ? nameEl.textContent : selected[0];
      return;
    }
    summaryEl.textContent = (I18N.nSelectedTpl || '__N__').replace('__N__', String(selected.length));
  }

  function reappend(tierOf) {
    ['S', 'A', 'B', 'C'].forEach(function (tierName) {
      var rowsEl = groups[tierName];
      if (!rowsEl) return;
      rows.filter(function (row) { return tierOf(row) === tierName; })
          .forEach(function (row) { rowsEl.appendChild(row); });
    });
  }

  function resetToDefault() {
    rows.forEach(function (row) {
      var o = original[row.dataset.key];
      if (!o) return;
      row.dataset.tier = o.tier;
      row.dataset.rankHidden = o.rankHidden ? 'true' : 'false';
      var badge = row.querySelector('.tier-badge');
      if (badge) badge.textContent = o.tier;
      var pills = row.querySelectorAll('.p-value');
      if (pills[0]) pills[0].textContent = o.placementText;
      if (pills[1]) pills[1].textContent = o.top4Text;
      if (pills[2]) { pills[2].textContent = o.contestText; pills[2].setAttribute('data-level', o.contestLevel || 'Low'); }
    });
    reappend(function (row) { return original[row.dataset.key] ? original[row.dataset.key].tier : null; });
    seeFullLinks.forEach(function (a) { a.style.display = ''; });
    if (summaryChip) summaryChip.dataset.active = 'false';
    updateSummary(checks.map(function (c) { return c.value; }));
    if (window.BM_applyListFilters) window.BM_applyListFilters();
  }

  function recompute(selectedKeys) {
    if (!data) return;
    var selectedSet = {};
    selectedKeys.forEach(function (k) { selectedSet[k] = true; });

    // Sum play_count, weight-average the three rates -- correct because
    // each bracket is a disjoint slice of the same real matches (a match
    // is played at exactly one rank), same reasoning as tierlist.py
    // computing everything from one flat match list.
    var combined = {};
    Object.keys(data.comps).forEach(function (key) {
      var perBracket = data.comps[key];
      var playCount = 0, placementSum = 0, top4Sum = 0, winSum = 0;
      selectedKeys.forEach(function (b) {
        var v = perBracket[b];
        if (!v) return;
        playCount += v[0];
        placementSum += v[1] * v[0];
        top4Sum += v[2] * v[0];
        winSum += v[3] * v[0];
      });
      if (playCount > 0) {
        combined[key] = { playCount: playCount, avgPlacement: placementSum / playCount, top4Rate: top4Sum / playCount, winRate: winSum / playCount };
      }
    });

    // Same "does it get a real page" gate as build_site.py's
    // filter_quality() (board-size/all-5-cost are structural and already
    // guaranteed -- every key here already has a real /compo/ page).
    var quality = Object.keys(combined).filter(function (key) {
      var c = combined[key];
      return c.playCount >= data.min_play_count && c.avgPlacement <= data.max_avg_placement;
    });
    // Same S/A/B/C assignment as tierlist.py's build_tier_list(): rank by
    // (-top4Rate, avgPlacement) among comps with enough sample, bucket by
    // cumulative fraction.
    var ranked = quality.filter(function (key) { return combined[key].playCount >= data.min_sample_for_tier; });
    ranked.sort(function (a, b) {
      var ca = combined[a], cb = combined[b];
      return cb.top4Rate - ca.top4Rate || ca.avgPlacement - cb.avgPlacement;
    });
    var tierOf = {};
    var n = ranked.length, cursor = 0;
    data.tier_buckets.forEach(function (bucket) {
      var tierName = bucket[0], end = tierName === 'C' ? n : Math.min(n, Math.round(n * bucket[1]));
      for (var i = cursor; i < Math.max(end, cursor); i++) tierOf[ranked[i]] = tierName;
      cursor = Math.max(end, cursor);
    });

    // Contestation pill: same play-rate-percentile idea as tierlist.py,
    // over this filtered scope's own ranked comps (the broader pre-
    // quality-filter pool Python uses isn't shipped to the client) --
    // a reasonable approximation for a display-only pill, not the tier.
    var totalParticipants = 0;
    data.brackets.forEach(function (b) { if (selectedSet[b.key]) totalParticipants += b.total_participants; });
    var playRates = ranked.map(function (key) { return totalParticipants ? combined[key].playCount / totalParticipants : 0; }).sort(function (a, b) { return a - b; });
    function percentileOf(rate) {
      if (!playRates.length) return 0;
      var idx = 0;
      while (idx < playRates.length && playRates[idx] <= rate) idx++;
      return (idx / playRates.length) * 100;
    }
    function levelOf(p) { return p >= 66 ? 'High' : (p >= 33 ? 'Medium' : 'Low'); }

    rows.forEach(function (row) {
      var key = row.dataset.key, tier = tierOf[key];
      if (!tier) { row.dataset.rankHidden = 'true'; return; }
      row.dataset.rankHidden = 'false';
      row.dataset.tier = tier;
      var badge = row.querySelector('.tier-badge');
      if (badge) badge.textContent = tier;
      var c = combined[key];
      var pills = row.querySelectorAll('.p-value');
      if (pills[0]) pills[0].textContent = c.avgPlacement.toFixed(2);
      if (pills[1]) pills[1].textContent = Math.round(c.top4Rate * 100) + '%';
      if (pills[2]) {
        var p = percentileOf(totalParticipants ? c.playCount / totalParticipants : 0);
        pills[2].textContent = String(Math.round(p));
        pills[2].setAttribute('data-level', levelOf(p));
      }
    });
    reappend(function (row) { return tierOf[row.dataset.key] || null; });
    // Within each now-settled group, order by the recombined placement --
    // reappending in this sorted order both re-sorts and re-parents.
    ['S', 'A', 'B', 'C'].forEach(function (tierName) {
      var rowsEl = groups[tierName];
      if (!rowsEl) return;
      rows.filter(function (row) { return tierOf[row.dataset.key] === tierName; })
          .sort(function (a, b) { return combined[a.dataset.key].avgPlacement - combined[b.dataset.key].avgPlacement; })
          .forEach(function (row) { rowsEl.appendChild(row); });
    });
    seeFullLinks.forEach(function (a) { a.style.display = 'none'; });
    if (summaryChip) summaryChip.dataset.active = 'true';
    updateSummary(selectedKeys);
    if (window.BM_applyListFilters) window.BM_applyListFilters();
  }

  if (applyBtn) {
    applyBtn.addEventListener('click', function () {
      var selected = checks.filter(function (c) { return c.checked; }).map(function (c) { return c.value; });
      if (!selected.length) { if (summaryEl) summaryEl.textContent = I18N.noneLabel || ''; return; }
      if (selected.length === checks.length) resetToDefault();
      else recompute(selected);
      dropdown.removeAttribute('open');
    });
  }
})();
