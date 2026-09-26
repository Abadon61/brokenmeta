
(function () {
  var toggle = document.getElementById('siteSearchToggle');
  var panel = document.getElementById('siteSearchPanel');
  var input = document.getElementById('siteSearchInput');
  var resultsEl = document.getElementById('siteSearchResults');
  if (!toggle || !panel || !input || !resultsEl) return;
  var root = window.BM_ROOT || '';
  var lang = document.documentElement.lang === 'fr' ? 'fr' : 'en';
  var TYPE_LABELS = {
    fr: {champion: 'Champion', item: 'Objet', comp: 'Compo'},
    en: {champion: 'Champion', item: 'Item', comp: 'Comp'},
  }[lang];
  var EMPTY_TEXT = lang === 'fr' ? 'Aucun r\u00e9sultat.' : 'No results.';
  var index = null, indexPromise = null;

  function loadIndex() {
    if (indexPromise) return indexPromise;
    var file = lang === 'fr' ? 'site-search_fr.json' : 'site-search.json';
    indexPromise = fetch(root + 'assets/data/' + file).then(function (r) { return r.json(); })
      .then(function (d) { index = d; return d; });
    return indexPromise;
  }

  function iconSrc(entry) {
    if (entry.type === 'champion') return root + 'assets/champions/' + entry.slug + '.png';
    if (entry.type === 'item') return root + 'assets/items/' + entry.slug + '.png';
    return null;
  }

  function renderResults(q) {
    if (!q || !index) { resultsEl.innerHTML = ''; return; }
    var needle = q.toLowerCase();
    var matches = index.filter(function (e) { return e.name.toLowerCase().indexOf(needle) !== -1; }).slice(0, 12);
    resultsEl.innerHTML = '';
    if (!matches.length) {
      var empty = document.createElement('div');
      empty.className = 'site-search-empty';
      empty.textContent = EMPTY_TEXT;
      resultsEl.appendChild(empty);
      return;
    }
    matches.forEach(function (entry) {
      var a = document.createElement('a');
      a.className = 'site-search-result-item';
      a.href = root + entry.href;
      var icon = iconSrc(entry);
      a.innerHTML =
        (icon ? '<img class="site-search-result-icon" src="' + icon + '" alt="" loading="lazy">'
              : '<span class="site-search-result-icon"></span>') +
        '<span class="site-search-result-type">' + TYPE_LABELS[entry.type] + '</span>' +
        '<span class="site-search-result-name">' + entry.name + '</span>';
      resultsEl.appendChild(a);
    });
  }

  function openPanel() {
    panel.hidden = false;
    toggle.setAttribute('aria-expanded', 'true');
    loadIndex().then(function () { renderResults(input.value.trim()); });
    setTimeout(function () { input.focus(); }, 0);
  }
  function closePanel() {
    panel.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
    input.value = '';
    resultsEl.innerHTML = '';
  }

  toggle.addEventListener('click', function (e) {
    e.stopPropagation();
    if (panel.hidden) openPanel(); else closePanel();
  });
  input.addEventListener('input', function () { renderResults(input.value.trim()); });
  document.addEventListener('click', function (e) {
    if (!panel.hidden && !e.target.closest('.site-search-wrap')) closePanel();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !panel.hidden) closePanel();
  });
})();
