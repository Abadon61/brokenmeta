
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
    if (!res.ok) {
      var err = new Error((data && data.error) || ('HTTP ' + res.status));
      err.rateLimited = !!(data && data.rateLimited) || res.status === 429;
      err.retryAfter = data && data.retryAfter;
      throw err;
    }
    return data;
  }

  // Same shared back-off as the profile page (one localStorage key): a
  // comparison costs TWO profile lookups against the shared Riot dev-key
  // quota, so a short debounce after success and a long one after a 429.
  var submitBtn = form.querySelector('button[type="submit"]');
  var submitLabel = submitBtn ? submitBtn.textContent : '';
  var COOLDOWN_KEY = 'bmLolCooldownUntil';
  var cooldownTimer = null;
  function cooldownLeft() {
    var until = 0;
    try { until = Number(localStorage.getItem(COOLDOWN_KEY)) || 0; } catch (e) {}
    return Math.ceil((until - Date.now()) / 1000);
  }
  function tickCooldown() {
    clearTimeout(cooldownTimer);
    if (!submitBtn) return;
    var left = cooldownLeft();
    if (left > 0) {
      submitBtn.disabled = true;
      submitBtn.textContent = (I.cooldownLabel || 'Retry in {s}s').replace('{s}', left);
      cooldownTimer = setTimeout(tickCooldown, 1000);
    } else {
      submitBtn.disabled = false;
      submitBtn.textContent = submitLabel;
    }
  }
  function startCooldown(seconds) {
    try { localStorage.setItem(COOLDOWN_KEY, String(Date.now() + seconds * 1000)); } catch (e) {}
    tickCooldown();
  }
  tickCooldown();

  // Bklit charts (assets/js/bm-charts.js) load on demand, like on the profile page.
  var bmChartsState = 0;
  function bmAttr(payload) { return JSON.stringify(payload).replace(/&/g, '&amp;').replace(/"/g, '&quot;'); }
  function hydrateBmCharts() {
    if (!document.querySelector('[data-bm-chart]:not([data-bm-mounted])')) return;
    if (window.bmCharts && window.bmCharts.mountAll) { window.bmCharts.mountAll(); return; }
    if (bmChartsState) return;
    bmChartsState = 1;
    var sc = document.createElement('script');
    sc.src = (window.BM_ROOT || '/') + 'assets/js/bm-charts.js?v=f6f19b706b';
    sc.async = true;
    document.head.appendChild(sc);
  }
  new MutationObserver(hydrateBmCharts).observe(document.body, { childList: true, subtree: true });

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

  // Left value | label | right value, the better side highlighted.
  function duelRow(label, aVal, bVal, aText, bText, lowerIsBetter) {
    var win = aVal === bVal ? 0 : ((lowerIsBetter ? aVal < bVal : aVal > bVal) ? 1 : 2);
    return '<div class="lol-compare-most-played">'
      + '<div class="' + (win === 1 ? 'lol-duel-win' : '') + '">' + aText + '</div>'
      + '<div class="stats-compare-label">' + esc(label) + '</div>'
      + '<div class="' + (win === 2 ? 'lol-duel-win' : '') + '">' + bText + '</div></div>';
  }
  function section(title, inner) {
    return '<div class="stats-section"><div class="stats-block-title">' + esc(title) + '</div>' + inner + '</div>';
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

    var both = qa.matches.length && qb.matches.length;
    var sections = '';
    if (both) {
      // Radar: each axis normalised to the larger of the two players.
      var axes = [
        { key: 'cs', label: 'CS/min', a: qa.statsAvg.csPerMin, b: qb.statsAvg.csPerMin },
        { key: 'gold', label: '\u00a0\u00a0Gold/min', a: qa.statsAvg.goldPerMin, b: qb.statsAvg.goldPerMin },
        { key: 'dpm', label: 'DPM', a: qa.statsAvg.dmgPerMin, b: qb.statsAvg.dmgPerMin },
        { key: 'kp', label: 'KP', a: qa.statsAvg.killParticipation, b: qb.statsAvg.killParticipation }
      ];
      if (qa.vision && qb.vision) axes.push({ key: 'vision', label: 'Vision/min', a: qa.vision.scorePerMin, b: qb.vision.scorePerMin });
      var va = {}, vb = {};
      axes.forEach(function (ax) { var top = Math.max(ax.a, ax.b) || 1; va[ax.key] = Math.round((ax.a / top) * 100); vb[ax.key] = Math.round((ax.b / top) * 100); });
      sections += '<div class="stats-radar" data-bm-chart="' + bmAttr({
        type: 'radar', size: 320,
        metrics: axes.map(function (ax) { return { key: ax.key, label: ax.label }; }),
        radar: [{ label: nameA, color: 'var(--magenta)', values: va }, { label: nameB, color: 'var(--cream)', values: vb }]
      }) + '"></div>'
        + '<div class="lol-compare-legend"><span style="color:var(--magenta)">&#9632; ' + esc(nameA) + '</span><span style="color:var(--cream)">&#9632; ' + esc(nameB) + '</span></div>';

      if (qa.combat && qb.combat) {
        sections += section(I.combatTitle, '<div class="stats-compare-grid">'
          + compareCard(I.kpiDmgTaken, qa.combat.damageTakenPerMin, qb.combat.damageTakenPerMin, '', 0, nameA, nameB)
          + compareCard(I.kpiDead, qa.combat.deadPct, qb.combat.deadPct, '%', 1, nameA, nameB)
          + compareCard(I.kpiCc, qa.combat.ccTime, qb.combat.ccTime, ' s', 0, nameA, nameB) + '</div>');
      }
      if (qa.vision && qb.vision && qa.objectives && qb.objectives) {
        sections += section(I.visionTitle, '<div class="stats-compare-grid">'
          + compareCard(I.kpiVisionMin, qa.vision.scorePerMin, qb.vision.scorePerMin, '', 1, nameA, nameB)
          + compareCard(I.kpiControlWards, qa.vision.controlWards, qb.vision.controlWards, '', 1, nameA, nameB)
          + compareCard(I.kpiTurrets, qa.objectives.turrets, qb.objectives.turrets, '', 1, nameA, nameB)
          + compareCard(I.kpiDragons, qa.objectives.dragons, qb.objectives.dragons, '', 1, nameA, nameB) + '</div>');
      }
      if (qa.records && qb.records) {
        var ra = qa.records, rb = qb.records;
        var rows = '';
        if (ra.bestKda && rb.bestKda) rows += duelRow(I.kpiBestKda, ra.bestKda.kda, rb.bestKda.kda, ra.bestKda.kills + '/' + ra.bestKda.deaths + '/' + ra.bestKda.assists + ' <span class="mono">' + ra.bestKda.kda.toFixed(1) + '</span>', rb.bestKda.kills + '/' + rb.bestKda.deaths + '/' + rb.bestKda.assists + ' <span class="mono">' + rb.bestKda.kda.toFixed(1) + '</span>');
        if (ra.bestDpm && rb.bestDpm) rows += duelRow(I.kpiBestDpm, ra.bestDpm.dpm, rb.bestDpm.dpm, '<span class="mono">' + ra.bestDpm.dpm + '</span>', '<span class="mono">' + rb.bestDpm.dpm + '</span>');
        rows += duelRow(I.kpiSpree, ra.longestSpree, rb.longestSpree, '<span class="mono">' + ra.longestSpree + '</span>', '<span class="mono">' + rb.longestSpree + '</span>');
        rows += duelRow(I.kpiPentas, ra.pentas, rb.pentas, '<span class="mono">' + ra.pentas + '</span>', '<span class="mono">' + rb.pentas + '</span>');
        rows += duelRow(I.kpiSoloKills, ra.soloKills, rb.soloKills, '<span class="mono">' + ra.soloKills + '</span>', '<span class="mono">' + rb.soloKills + '</span>');
        if (qa.pings && qb.pings) rows += duelRow(I.pingsPerGame, qa.pings.perGame, qb.pings.perGame, '<span class="mono">' + qa.pings.perGame.toFixed(1) + '</span>', '<span class="mono">' + qb.pings.perGame.toFixed(1) + '</span>');
        sections += section(I.recordsTitle, '<div class="lol-duel-list">' + rows + '</div>');
      }
    }

    var mostPlayedHtml = '<div class="lol-compare-most-played">'
      + '<div>' + (topA ? esc(topA.champ) + ' <span class="mono">' + topA.kda.toFixed(1) + ' KDA</span>' : '') + '</div>'
      + '<div class="stats-compare-label">' + esc(I.mostPlayed) + '</div>'
      + '<div>' + (topB ? esc(topB.champ) + ' <span class="mono">' + topB.kda.toFixed(1) + ' KDA</span>' : '') + '</div>'
      + '</div>';

    results.innerHTML =
      '<div class="lol-compare-headers">' + playerHeaderHtml(dataA) + '<div class="lol-compare-form-vs">' + esc(I.compareVs || 'VS') + '</div>' + playerHeaderHtml(dataB) + '</div>'
      + mostPlayedHtml
      + '<div class="stats-compare-grid">' + cardsHtml + '</div>'
      + sections;
    results.querySelectorAll('.league-icon-fallback').forEach(function (img) {
      img.addEventListener('error', function () { img.style.visibility = 'hidden'; });
    });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (cooldownLeft() > 0) return;
    var riotIdA = document.getElementById('lolCompareRiotIdA').value.trim();
    var riotIdB = document.getElementById('lolCompareRiotIdB').value.trim();
    var regionA = document.getElementById('lolCompareRegionA').value;
    var regionB = document.getElementById('lolCompareRegionB').value;
    if (!riotIdA || !riotIdB) return;
    setStatus(I.loading, false);
    var skelCards = '';
    for (var i = 0; i < 4; i++) skelCards += '<span class="skel" style="height:96px"></span>';
    results.innerHTML = '<div class="skel-stack" aria-hidden="true"><div class="skel-duo"><span class="skel" style="height:64px"></span><span class="skel" style="height:64px"></span></div>'
      + '<span class="skel skel-circle" style="width:200px;height:200px;margin:8px auto"></span><div class="stats-compare-grid">' + skelCards + '</div></div>';
    Promise.all([fetchProfile(riotIdA, regionA), fetchProfile(riotIdB, regionB)]).then(function (r) {
      setStatus(null);
      renderCompare(r[0], r[1]);
      startCooldown(20);
    }).catch(function (err) {
      results.innerHTML = '';
      setStatus(err.message || String(err), true);
      if (err && err.rateLimited) startCooldown(err.retryAfter || 75);
    });
  });
})();
