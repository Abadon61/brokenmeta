
(function () {
  var API = window.BM_LEAGUE_API;
  var I = window.BM_I18N_LEAGUE || {};
  var form = document.getElementById('lolCompareForm');
  var statusEl = document.getElementById('lolCompareStatus');
  var results = document.getElementById('lolCompareResults');
  if (!form || !API) return;

  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }
  function tierLabel(tier) { return tier ? tier.charAt(0) + tier.slice(1).toLowerCase() : ''; }
  function setStatus(text, isError) {
    if (!text) { statusEl.hidden = true; statusEl.textContent = ''; return; }
    statusEl.hidden = false;
    statusEl.textContent = text;
    statusEl.dataset.error = isError ? 'true' : 'false';
  }
  async function fetchProfile(riotId, region) {
    var res = await fetch(API + '/profile?riotId=' + encodeURIComponent(riotId) + '&region=' + encodeURIComponent(region));
    var data = await res.json().catch(function () { return {}; });
    if (!res.ok) throw new Error((data && data.error) || ('HTTP ' + res.status));
    return data;
  }

  function playerHeaderHtml(data) {
    var primary = data.ranks.solo || data.ranks.flex;
    var avatarHtml = data.profileIconId
      ? '<img class="league-icon-fallback" src="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/' + data.profileIconId + '.jpg" alt="">'
      : '';
    return '<div class="lol-compare-player-header">'
      + '<div class="player-avatar">' + avatarHtml + '</div>'
      + '<div><div class="player-name">' + esc(data.riotId) + '</div>'
      + '<div class="player-meta">' + esc(data.region) + '</div>'
      + (primary
        ? '<div class="rank-tier-name">' + tierLabel(primary.tier) + ' ' + primary.rank + ' <span class="mono">' + primary.leaguePoints + ' LP</span></div>'
        : '<div class="rank-tier-name" style="color:var(--text-faint)">' + esc(I.unranked) + '</div>') + '</div></div>';
  }

  function compareCard(label, a, b, unit, decimals, aName, bName) {
    var scale = Math.max(a, b) * 1.15 || 1;
    return '<div class="stats-compare-card"><div class="stats-compare-label">' + esc(label) + '</div>'
      + '<div class="stats-compare-row"><span class="stats-compare-name">' + esc(aName) + '</span><div class="stats-compare-track"><div class="stats-compare-fill you" style="width:' + Math.round((a / scale) * 100) + '%"></div></div><span class="stats-compare-value mono">' + a.toFixed(decimals) + unit + '</span></div>'
      + '<div class="stats-compare-row"><span class="stats-compare-name">' + esc(bName) + '</span><div class="stats-compare-track"><div class="stats-compare-fill rank" style="width:' + Math.round((b / scale) * 100) + '%"></div></div><span class="stats-compare-value mono">' + b.toFixed(decimals) + unit + '</span></div>'
      + '</div>';
  }

  function soloOrFlex(data) {
    return data.ranks.solo ? data.queues.solo : (data.ranks.flex ? data.queues.flex : data.queues.solo);
  }

  function renderCompare(dataA, dataB) {
    var nameA = dataA.riotId.split('#')[0], nameB = dataB.riotId.split('#')[0];
    var qa = soloOrFlex(dataA), qb = soloOrFlex(dataB);
    var wrA = qa.matches.length ? Math.round(qa.matches.filter(function (m) { return m.win; }).length / qa.matches.length * 100) : 0;
    var wrB = qb.matches.length ? Math.round(qb.matches.filter(function (m) { return m.win; }).length / qb.matches.length * 100) : 0;
    var topA = qa.champions[0], topB = qb.champions[0];

    var cardsHtml = (qa.matches.length && qb.matches.length) ? [
      compareCard(I.thWinrate, wrA, wrB, '%', 0, nameA, nameB),
      compareCard(I.csPerMin, qa.statsAvg.csPerMin, qb.statsAvg.csPerMin, '', 1, nameA, nameB),
      compareCard(I.goldPerMin, qa.statsAvg.goldPerMin, qb.statsAvg.goldPerMin, '', 0, nameA, nameB),
      compareCard(I.dmgPerMin, qa.statsAvg.dmgPerMin, qb.statsAvg.dmgPerMin, '', 0, nameA, nameB),
      compareCard(I.killParticipation, qa.statsAvg.killParticipation, qb.statsAvg.killParticipation, '%', 0, nameA, nameB),
    ].join('') : '<div class="matchup-empty">' + esc(I.notEnoughToCompare) + '</div>';

    var mostPlayedHtml = '<div class="lol-compare-most-played">'
      + '<div>' + (topA ? esc(topA.champ) + ' <span class="mono">' + topA.kda.toFixed(1) + ' KDA</span>' : '') + '</div>'
      + '<div class="stats-compare-label">' + esc(I.mostPlayed) + '</div>'
      + '<div>' + (topB ? esc(topB.champ) + ' <span class="mono">' + topB.kda.toFixed(1) + ' KDA</span>' : '') + '</div>'
      + '</div>';

    results.innerHTML =
      '<div class="lol-compare-headers">' + playerHeaderHtml(dataA) + '<div class="lol-compare-form-vs">' + esc(I.compareVs || 'VS') + '</div>' + playerHeaderHtml(dataB) + '</div>'
      + mostPlayedHtml
      + '<div class="stats-compare-grid">' + cardsHtml + '</div>';
    results.querySelectorAll('.league-icon-fallback').forEach(function (img) {
      img.addEventListener('error', function () { img.style.visibility = 'hidden'; });
    });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var riotIdA = document.getElementById('lolCompareRiotIdA').value.trim();
    var riotIdB = document.getElementById('lolCompareRiotIdB').value.trim();
    var regionA = document.getElementById('lolCompareRegionA').value;
    var regionB = document.getElementById('lolCompareRegionB').value;
    if (!riotIdA || !riotIdB) return;
    setStatus(I.loading, false);
    results.innerHTML = '';
    Promise.all([fetchProfile(riotIdA, regionA), fetchProfile(riotIdB, regionB)]).then(function (r) {
      setStatus(null);
      renderCompare(r[0], r[1]);
    }).catch(function (err) {
      setStatus(err.message || String(err), true);
    });
  });
})();
