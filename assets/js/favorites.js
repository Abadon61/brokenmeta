
(function () {
  var KEY = 'bm_favorites';
  var STAR_SVG = '<svg viewBox="0 0 24 24"><path d="M12 2.5l2.97 6.28 6.93.7-5.13 4.75 1.4 6.87L12 17.9l-6.17 3.2 1.4-6.87-5.13-4.75 6.93-.7z"/></svg>';

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; }
  }
  function save(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {}
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

  var favorites = load();
  document.querySelectorAll('.fav-btn[data-fav-key]').forEach(function (btn) {
    applyState(btn, isSaved(favorites, btn.dataset.favKey));
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

  if (!favorites.length) {
    maybeShowEmptyState();
  } else {
    favorites.forEach(renderRow);
  }
})();
