
(function () {
  var KEY = 'bm_favorites';
  var RECENT_KEY = 'bm_recently_viewed';
  var RECENT_MAX = 12;
  var STAR_SVG = '<svg viewBox="0 0 24 24"><path d="M12 2.5l2.97 6.28 6.93.7-5.13 4.75 1.4 6.87L12 17.9l-6.17 3.2 1.4-6.87-5.13-4.75 6.93-.7z"/></svg>';

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; }
  }
  function save(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {}
  }
  function loadRecent() {
    try { return JSON.parse(localStorage.getItem(RECENT_KEY)) || []; } catch (e) { return []; }
  }
  function saveRecent(list) {
    try { localStorage.setItem(RECENT_KEY, JSON.stringify(list)); } catch (e) {}
  }
  function isSaved(list, key) {
    return list.some(function (f) { return f.key === key; });
  }
  function toggle(btn) {
    var list = load();
    var key = btn.dataset.favKey;
    var idx = list.findIndex(function (f) { return f.key === key; });
    if (idx === -1) {
      list.push({
        key: key, slug: btn.dataset.favSlug, label: btn.dataset.favLabel,
        tier: btn.dataset.favTier, carrySlug: btn.dataset.favCarrySlug || null,
      });
      if (window.gtag) gtag('event', 'favorite_add');
    } else {
      list.splice(idx, 1);
    }
    save(list);
    return idx === -1; // now saved
  }
  function applyState(btn, saved) {
    btn.setAttribute('aria-pressed', saved ? 'true' : 'false');
    var addTitle = btn.dataset.addTitle, removeTitle = btn.dataset.removeTitle;
    if (addTitle && removeTitle) btn.title = saved ? removeTitle : addTitle;
  }

  // Re-reads localStorage and re-applies every button's pressed state --
  // not just run once at load, because a plain "read once at script start"
  // goes stale the moment a visitor un-favorites a comp on /favoris/ then
  // hits the browser's Back button: bfcache restores the tier-list page's
  // DOM exactly as it was (including that comp's stale aria-pressed=true)
  // WITHOUT re-running this script, so the star never got a chance to
  // notice the localStorage change made on the other page.
  function syncButtonStates() {
    var favorites = load();
    document.querySelectorAll('.fav-btn[data-fav-key]').forEach(function (btn) {
      applyState(btn, isSaved(favorites, btn.dataset.favKey));
    });
  }
  syncButtonStates();
  // fires on the normal first load too (persisted: false, a harmless
  // no-op re-sync) and, critically, on a bfcache restore (persisted: true).
  window.addEventListener('pageshow', function (e) { if (e.persisted) syncButtonStates(); });

  // Passive "Vus récemment" tracking: every real /compo/<slug>/ visit
  // records itself (see comp.html's window.BM_CURRENT_COMP), no ★ click
  // needed. De-duped by moving an already-seen comp back to the front
  // instead of listing it twice; capped so the list stays a quick
  // "what was I just looking at", not an unbounded history dump.
  if (window.BM_CURRENT_COMP && window.BM_CURRENT_COMP.key) {
    var recent = loadRecent().filter(function (f) { return f.key !== window.BM_CURRENT_COMP.key; });
    recent.unshift(window.BM_CURRENT_COMP);
    saveRecent(recent.slice(0, RECENT_MAX));
  }

  document.querySelectorAll('.fav-btn[data-fav-key]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var nowSaved = toggle(btn);
      applyState(btn, nowSaved);
      // A remove click on the favorites page itself should drop that row
      // immediately rather than wait for a reload.
      if (!nowSaved) {
        var row = btn.closest('.fav-row');
        if (row) { row.remove(); maybeShowEmptyState(); }
      }
    });
  });

  var list = document.getElementById('favoritesList');
  if (!list) return;

  var root = window.BM_ROOT || '';
  var emptyText = list.dataset.emptyText || '';
  var addTitle = list.dataset.addTitle || '';
  var removeTitle = list.dataset.removeTitle || '';

  function maybeShowEmptyState() {
    if (!list.querySelector('.fav-row')) {
      list.innerHTML = '<p class="favorites-empty">' + emptyText + '</p>';
    }
  }

  function renderRow(f) {
    var a = document.createElement('a');
    a.className = 'comp-row fav-row';
    a.setAttribute('data-tier', f.tier || '');
    a.href = root + 'compo/' + f.slug + '/';
    var carryImg = f.carrySlug
      ? '<img class="carry-portrait" src="' + root + 'assets/champions/' + f.carrySlug + '.png" alt="" loading="lazy">'
      : '';
    a.innerHTML =
      '<span class="corner tl"></span><span class="corner tr"></span><span class="corner bl"></span><span class="corner br"></span>' +
      '<div class="tier-badge">' + (f.tier || '') + '</div>' +
      '<div class="row-body"><div class="row-top"><div class="row-name-block">' + carryImg +
      '<div class="row-name">' + f.label + '</div></div></div></div>' +
      '<button type="button" class="fav-btn" data-fav-key="' + f.key + '" data-add-title="' + addTitle + '" ' +
      'data-remove-title="' + removeTitle + '" title="' + removeTitle + '" aria-label="' + removeTitle + '" aria-pressed="true">' + STAR_SVG + '</button>';
    var removeBtn = a.querySelector('.fav-btn');
    removeBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      toggle(removeBtn);
      a.remove();
      maybeShowEmptyState();
    });
    list.appendChild(a);
  }

  var favorites = load();
  if (!favorites.length) {
    maybeShowEmptyState();
  } else {
    favorites.forEach(renderRow);
  }

  // "Vus récemment" -- same page, separate container, separate storage key.
  // Each row gets its own ★ (reusing toggle()/applyState() as-is) so a
  // comp you just glanced at can be favorited straight from here too,
  // without hunting it back down on a list page.
  var recentList = document.getElementById('recentlyViewedList');
  var clearBtn = document.getElementById('recentlyViewedClear');
  if (!recentList) return;

  var recentEmptyText = recentList.dataset.emptyText || '';

  function maybeShowRecentEmptyState() {
    if (!recentList.querySelector('.recent-row')) {
      recentList.innerHTML = '<p class="favorites-empty">' + recentEmptyText + '</p>';
      if (clearBtn) clearBtn.hidden = true;
    }
  }

  function renderRecentRow(f) {
    var a = document.createElement('a');
    a.className = 'comp-row recent-row';
    a.setAttribute('data-tier', f.tier || '');
    a.href = root + 'compo/' + f.slug + '/';
    var carryImg = f.carrySlug
      ? '<img class="carry-portrait" src="' + root + 'assets/champions/' + f.carrySlug + '.png" alt="" loading="lazy">'
      : '';
    var isFav = isSaved(load(), f.key);
    a.innerHTML =
      '<span class="corner tl"></span><span class="corner tr"></span><span class="corner bl"></span><span class="corner br"></span>' +
      '<div class="tier-badge">' + (f.tier || '') + '</div>' +
      '<div class="row-body"><div class="row-top"><div class="row-name-block">' + carryImg +
      '<div class="row-name">' + f.label + '</div></div></div></div>' +
      '<button type="button" class="fav-btn" data-fav-key="' + f.key + '" data-fav-slug="' + f.slug + '" data-fav-label="' + f.label +
      '" data-fav-tier="' + (f.tier || '') + '" data-fav-carry-slug="' + (f.carrySlug || '') + '" data-add-title="' + addTitle +
      '" data-remove-title="' + removeTitle + '" title="' + (isFav ? removeTitle : addTitle) + '" aria-pressed="' + (isFav ? 'true' : 'false') + '">' + STAR_SVG + '</button>';
    var favBtn = a.querySelector('.fav-btn');
    favBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      applyState(favBtn, toggle(favBtn));
    });
    recentList.appendChild(a);
  }

  var recent = loadRecent();
  if (!recent.length) {
    maybeShowRecentEmptyState();
  } else {
    if (clearBtn) clearBtn.hidden = false;
    recent.forEach(renderRecentRow);
  }
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      saveRecent([]);
      recentList.innerHTML = '';
      maybeShowRecentEmptyState();
    });
  }

  // League profiles favorited/recently searched -- separate localStorage
  // keys from the comp favorites above (see LEAGUE_JS), only ever rendered
  // here on /favoris/ (this script loads on every page, but these two
  // containers only exist on that one).
  var lolFavList = document.getElementById('leagueFavoritesList');
  var lolRecentList = document.getElementById('leagueRecentList');
  if (!lolFavList && !lolRecentList) return;

  function loadLol(key) {
    try { return JSON.parse(localStorage.getItem(key)) || []; } catch (e) { return []; }
  }
  function saveLol(key, list) {
    try { localStorage.setItem(key, JSON.stringify(list)); } catch (e) {}
  }
  function lolProfileHref(f) {
    return root + 'league/?riotId=' + encodeURIComponent(f.riotId) + '&region=' + encodeURIComponent(f.region);
  }
  function renderLolRow(container, f, isFav) {
    var a = document.createElement('a');
    a.className = 'comp-row fav-row';
    a.href = lolProfileHref(f);
    var parts = f.riotId.split('#');
    a.innerHTML =
      '<div class="duo-partner-row" style="padding:14px 16px;align-items:center">'
      + '<div class="duo-partner-info"><div class="duo-partner-name">' + parts[0] + (parts[1] ? ' <span class="tag">#' + parts[1] + '</span>' : '') + '</div>'
      + '<div class="duo-partner-meta">' + f.region + '</div></div>'
      + '<button type="button" class="fav-btn inline" data-fav-key="' + f.key + '" aria-pressed="true">' + STAR_SVG + '</button></div>';
    var btn = a.querySelector('.fav-btn');
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var key = isFav ? LOL_FAV_KEY : LOL_RECENT_KEY;
      saveLol(key, loadLol(key).filter(function (x) { return x.key !== f.key; }));
      a.remove();
      maybeShowLolEmptyState();
    });
    (isFav ? lolFavList : lolRecentList).appendChild(a);
  }
  function maybeShowLolEmptyState() {
    if (lolFavList && !lolFavList.querySelector('.fav-row')) {
      lolFavList.innerHTML = '<p class="favorites-empty">' + (lolFavList.dataset.emptyText || '') + '</p>';
    }
    if (lolRecentList && !lolRecentList.querySelector('.fav-row')) {
      lolRecentList.innerHTML = '<p class="favorites-empty">' + (lolRecentList.dataset.emptyText || '') + '</p>';
      if (lolRecentClear) lolRecentClear.hidden = true;
    }
  }
  var LOL_FAV_KEY = 'bm_lol_favorites';
  var LOL_RECENT_KEY = 'bm_lol_recent';
  var lolRecentClear = document.getElementById('leagueRecentClear');
  var lolFavorites = loadLol(LOL_FAV_KEY);
  var lolRecent = loadLol(LOL_RECENT_KEY);
  if (lolFavList) lolFavorites.forEach(function (f) { renderLolRow(lolFavList, f, true); });
  if (lolRecentList) lolRecent.forEach(function (f) { renderLolRow(lolRecentList, f, false); });
  maybeShowLolEmptyState();
  if (lolRecentClear) {
    lolRecentClear.hidden = !lolRecent.length;
    lolRecentClear.addEventListener('click', function () {
      saveLol(LOL_RECENT_KEY, []);
      lolRecentList.innerHTML = '';
      maybeShowLolEmptyState();
    });
  }
})();
