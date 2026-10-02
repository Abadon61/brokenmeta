
(function () {
  var searchInput = document.getElementById('counterSearch');
  if (!searchInput) return;
  var resultsEl = document.getElementById('counterSearchResults');
  var outputEl = document.getElementById('counterOutput');
  var emptyEl = document.getElementById('counterEmpty');
  var selectedNameEl = document.getElementById('counterSelectedName');
  var forListEl = document.getElementById('counterForList');
  var againstListEl = document.getElementById('counterAgainstList');
  var root = window.BM_ROOT || '';
  var compIndex = null, matchupData = null;

  Promise.all([
    fetch(root + 'assets/data/comp-index.json').then(function (r) { return r.json(); }),
    fetch(root + 'assets/data/matchup-finder.json').then(function (r) { return r.json(); }),
  ]).then(function (res) {
    compIndex = res[0];
    matchupData = res[1];
  }).catch(function () {});

  function renderResults(query) {
    resultsEl.innerHTML = '';
    if (!query || !compIndex || !matchupData) { resultsEl.hidden = true; return; }
    var q = query.toLowerCase();
    var matches = [];
    for (var key in compIndex) {
      if (!matchupData[key]) continue; // only comps with real matchup data are searchable
      if (compIndex[key].display_label.toLowerCase().indexOf(q) !== -1) {
        matches.push(key);
        if (matches.length >= 8) break;
      }
    }
    if (!matches.length) { resultsEl.hidden = true; return; }
    matches.forEach(function (key) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'counter-result-item';
      btn.textContent = compIndex[key].display_label;
      btn.addEventListener('click', function () { selectComp(key); });
      resultsEl.appendChild(btn);
    });
    resultsEl.hidden = false;
  }

  function matchupRow(m) {
    var side = m.aheadPct >= 50 ? 'ahead' : 'behind';
    var row = document.createElement('div');
    row.className = 'fiche-matchup-row';
    row.dataset.side = side;
    var nameHtml = m.oppSlug
      ? '<a href="' + root + 'compo/' + m.oppSlug + '/" style="color:inherit">' + m.oppLabel + '</a>'
      : m.oppLabel;
    row.innerHTML =
      '<span class="m-name">' + nameHtml + '</span>' +
      '<span class="m-encounters nums">' + m.encounters + '</span>' +
      '<span class="matchup-bar-wrap"><span class="matchup-bar" style="width:' + m.aheadPct + '%"></span></span>' +
      '<span class="m-pct nums">' + m.aheadPct + '%</span>';
    return row;
  }

  function selectComp(key) {
    searchInput.value = compIndex[key].display_label;
    resultsEl.hidden = true;
    resultsEl.innerHTML = '';
    var rows = matchupData[key] || [];
    var against = rows.filter(function (m) { return m.aheadPct < 50; })
                       .sort(function (a, b) { return a.aheadPct - b.aheadPct; });
    var forUs = rows.filter(function (m) { return m.aheadPct >= 50; })
                     .sort(function (a, b) { return b.aheadPct - a.aheadPct; });
    againstListEl.innerHTML = '';
    forListEl.innerHTML = '';
    against.forEach(function (m) { againstListEl.appendChild(matchupRow(m)); });
    forUs.forEach(function (m) { forListEl.appendChild(matchupRow(m)); });
    if (selectedNameEl) selectedNameEl.textContent = compIndex[key].display_label;
    outputEl.hidden = false;
    emptyEl.hidden = true;
    if (window.gtag) gtag('event', 'counter_finder_search', {comp_key: key});
  }

  searchInput.addEventListener('input', function () {
    outputEl.hidden = true;
    renderResults(searchInput.value.trim());
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.counter-search-wrap')) resultsEl.hidden = true;
  });
})();
