
(function () {
  var API = window.BM_LEAGUE_API;
  var I = window.BM_I18N_LOL_LB || {};
  var bar = document.getElementById('lolLbRegionBar');
  var statusEl = document.getElementById('lolLbStatus');
  var tableWrap = document.getElementById('lolLbTableWrap');
  var tbody = document.getElementById('lolLbTableBody');
  if (!bar || !API) return;
  var currentRegion = 'EUW';
  var cache = {};

  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }

  function setStatus(text, isError) {
    if (!text) { statusEl.hidden = true; statusEl.textContent = ''; return; }
    statusEl.hidden = false;
    statusEl.textContent = text;
    statusEl.dataset.error = isError ? 'true' : 'false';
  }

  function rowHtml(e) {
    var name = e.riotId ? esc(e.riotId) : '<i>' + esc(I.anonymous) + '</i>';
    var href = e.riotId ? I.root + 'league/?riotId=' + encodeURIComponent(e.riotId) + '&region=' + currentRegion : null;
    var total = e.wins + e.losses;
    var wr = total ? Math.round((e.wins / total) * 100) : 0;
    return '<tr' + (href ? " onclick=\"location.href='" + href + "'\" style=\"cursor:pointer\"" : '') + '>'
      + '<td class="num"><span class="lb-rank" data-top="' + (e.rank <= 3) + '">#' + e.rank + '</span></td>'
      + '<td><span class="lb-player-cell"><span class="lb-riotid">' + name + '</span>'
      + (e.hotStreak ? '<span class="lb-hot" title="' + esc(I.hotStreakTitle) + '">\ud83d\udd25</span>' : '') + '</span></td>'
      + '<td><span class="lb-tier-tag" data-tier="' + e.tier + '">' + e.tier + '</span></td>'
      + '<td class="num mono">' + e.leaguePoints + ' LP</td>'
      + '<td class="num mono">' + e.wins + I.wins + ' ' + e.losses + I.losses + ' <span class="' + (wr >= 50 ? 'good' : 'warn') + '">(' + wr + '%)</span></td>'
      + '</tr>';
  }

  function render(entries) {
    tbody.innerHTML = entries.map(rowHtml).join('');
    tableWrap.hidden = false;
  }

  function load(region) {
    currentRegion = region;
    setStatus(I.loading, false);
    tableWrap.hidden = true;
    if (cache[region]) { setStatus(null); render(cache[region]); return; }
    fetch(API + '/leaderboard?region=' + region)
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
      .then(function (res) {
        if (!res.ok || res.data.error) throw new Error(res.data.error || 'error');
        cache[region] = res.data.entries;
        setStatus(null);
        render(res.data.entries);
      })
      .catch(function () { setStatus(I.error, true); });
  }

  bar.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-region]');
    if (!btn) return;
    [].forEach.call(bar.querySelectorAll('[data-region]'), function (b) { b.dataset.active = String(b === btn); });
    load(btn.dataset.region);
  });

  load(currentRegion);
})();
