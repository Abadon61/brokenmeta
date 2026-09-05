
(function () {
  var API = window.BM_METASCOPE_API;
  var ROOT = window.BM_ROOT || '';
  var I = window.BM_I18N_MS || {};
  var form = document.getElementById('metascopeForm');
  var riotIdInput = document.getElementById('metascopeRiotId');
  var regionSelect = document.getElementById('metascopeRegion');
  var statusEl = document.getElementById('metascopeStatus');
  var results = document.getElementById('metascopeResults');
  if (!form || !API) return;

  var currentProfile = null; // cached so "back" from an analysis doesn't refetch

  function el(tag, className, html) {
    var e = document.createElement(tag);
    if (className) e.className = className;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  function champIcon(slug, alt, cls, style) {
    if (!slug) return '';
    return '<img class="champ-link-icon' + (cls ? ' ' + cls : '') + '" src="' + ROOT + 'assets/champions/' + slug + '.png" alt="' + alt + '" loading="lazy"'
      + (style ? ' style="' + style + '"' : '') + ' data-champ-slug="' + slug + '" data-champ-href="' + ROOT + 'champions/' + slug + '/">';
  }
  function pill(label, value) {
    return '<div class="pill"><div class="p-label">' + label + '</div><div class="p-value nums">' + value + '</div></div>';
  }
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }
  function initials(riotId) { var name = (riotId || '').split('#')[0].trim(); return (name.slice(0, 2) || '?').toUpperCase(); }

  function setStatus(text, isError) {
    if (!text) { statusEl.hidden = true; statusEl.textContent = ''; return; }
    statusEl.hidden = false;
    statusEl.textContent = text;
    statusEl.dataset.error = isError ? 'true' : 'false';
  }

  function setUrl(params) {
    var qs = new URLSearchParams(params).toString();
    var url = location.pathname + (qs ? '?' + qs : '');
    history.pushState(params, '', url);
  }

  async function fetchJson(url) {
    var res = await fetch(url);
    var data = await res.json().catch(function () { return {}; });
    if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));
    return data;
  }

  function renderProfile(data) {
    currentProfile = data;
    var total = (data.wins || 0) + (data.losses || 0);
    var wr = total ? Math.round((data.wins / total) * 100) + '%' : null;

    var header = el('div', 'player-header',
      '<div class="player-avatar">' + esc(initials(data.riotId)) + '</div>'
      + '<div><div class="player-name-row"><span class="player-name">' + esc(data.riotId) + '</span>'
      + (data.tier ? '<span class="lb-tier-tag" data-tier="' + data.tier + '">' + data.tier + '</span>' : '')
      + (data.hotStreak ? '<span class="lb-hot" title="' + esc(I.hotStreakTitle) + '">\ud83d\udd25</span>' : '')
      + '</div><div class="player-meta">' + esc(data.region) + '</div></div>'
      + '<div class="player-stats pill-row">'
      + pill('LP', data.leaguePoints != null ? data.leaguePoints : '—')
      + pill(I.recordLabel, total ? (data.wins + 'W / ' + data.losses + 'L') : '—')
      + pill(I.winrateLabel, wr || I.winrateUnavailable)
      + '</div>');

    var statsBox = el('div', 'metascope-box',
      '<div class="metascope-box-title">' + esc(I.statsTitle) + '</div>'
      + '<div class="metascope-stat-row"><span>LP</span><b class="nums">' + (data.leaguePoints != null ? data.leaguePoints : '—') + '</b></div>'
      + (data.avgPlacement != null ? '<div class="metascope-stat-row"><span>' + esc(I.placementLabel) + '</span><b class="nums">' + data.avgPlacement.toFixed(2) + '</b></div>' : ''));

    var habitsInner = '<div class="metascope-box-title">' + esc(I.habitsTitle) + '</div>';
    if (data.isRerollLover) habitsInner += '<div class="metascope-habit-badge">\ud83c\udfb2 ' + esc(I.rerollLover) + '</div>';
    if (data.topPlayed && data.topPlayed.length) {
      habitsInner += '<div class="metascope-top-played-label">' + esc(I.topPlayed) + '</div>';
      data.topPlayed.forEach(function (tp) {
        habitsInner += '<div class="metascope-top-played-row">' + champIcon(tp.carrySlug, tp.label)
          + (tp.compSlug ? '<a class="metascope-top-played-name" href="' + ROOT + 'compo/' + tp.compSlug + '/">' + esc(tp.label) + '</a>'
                          : '<span class="metascope-top-played-name">' + esc(tp.label) + '</span>')
          + '<span class="metascope-top-played-count nums">\u00d7' + tp.count + '</span></div>';
      });
    } else if (!data.isRerollLover) {
      habitsInner += '<div class="matchup-empty">' + esc(I.noHabits) + '</div>';
    }
    var habitsBox = el('div', 'metascope-box', habitsInner);

    var sidebar = el('div', 'metascope-sidebar');
    sidebar.appendChild(statsBox);
    sidebar.appendChild(habitsBox);

    var gamesHtml = '';
    (data.recentGames || []).forEach(function (g) {
      gamesHtml += '<div class="profile-comp-row" style="cursor:default">'
        + '<span class="lb-square ' + (g.placement <= 4 ? 'win' : 'loss') + '">' + g.placement + '</span>'
        + champIcon(g.carrySlug, g.carry, null, 'width:26px;height:26px;object-fit:cover;border:1px solid var(--border-bright)')
        + (g.compSlug ? '<a class="profile-comp-name" href="' + ROOT + 'compo/' + g.compSlug + '/">' + esc(g.compLabel) + '</a>'
                       : '<span class="profile-comp-name">' + esc(g.compLabel) + '</span>')
        + '<a class="metascope-analyze-link" href="javascript:;" data-match-id="' + g.matchId + '">' + esc(I.analyzeButton) + ' \u2192</a>'
        + '</div>';
    });
    var main = el('div', 'metascope-main',
      '<h2 class="fiche-section-title" style="margin-top:0">' + esc(I.last10GamesTitle) + '</h2>'
      + (data.recentGames && data.recentGames.length ? '<p class="metascope-hint">' + esc(I.analyzeHint) + '</p>' : '')
      + '<div class="profile-comp-list">' + (gamesHtml || '<div class="matchup-empty">' + esc(I.noRecentGames) + '</div>') + '</div>');

    var layout = el('div', 'metascope-layout');
    layout.appendChild(sidebar);
    layout.appendChild(main);

    results.innerHTML = '';
    results.appendChild(header);
    results.appendChild(layout);

    main.querySelectorAll('[data-match-id]').forEach(function (btn) {
      btn.addEventListener('click', function () { runAnalyze(btn.dataset.matchId); });
    });
  }

  function renderAnalysis(data) {
    var insightsHtml = (data.insights || []).map(function (ins) {
      var icon = ins.type === 'good' ? '\u2713' : ins.type === 'warning' ? '\u26a0' : '\u2139';
      return '<div class="metascope-insight-row" data-type="' + ins.type + '">'
        + '<span class="metascope-insight-icon">' + icon + '</span>'
        + '<div><span class="metascope-insight-category">' + esc(ins.category) + '</span>'
        + '<span class="metascope-insight-text">' + esc(ins.text) + '</span></div></div>';
    }).join('');

    var unitsHtml = (data.units || []).map(function (u) {
      var itemsHtml = (u.items || []).map(function (it) {
        return '<img class="item-icon" src="' + ROOT + 'assets/items/' + it.slug + '.png" alt="' + esc(it.name) + '" title="' + esc(it.name) + '" loading="lazy">';
      }).join('');
      var stars = u.star >= 3 ? '\u2605\u2605\u2605' : u.star === 2 ? '\u2605\u2605' : '';
      return '<div class="unit-cell"><div class="unit-icon-wrap">'
        + champIcon(u.slug, u.champion, 'unit-icon', 'border-color:var(--cost-' + (u.cost || 1) + ')')
        + (stars ? '<span class="star-row">' + stars + '</span>' : '')
        + '</div><div class="unit-items">' + itemsHtml + '</div></div>';
    }).join('');

    var lobbyHtml = '<div class="profile-comp-row" style="cursor:default;background:transparent;border-color:transparent">'
      + '<span class="lb-square" style="background:transparent;border:none;color:var(--text-faint)">\u2014</span>'
      + champIcon(data.carrySlug, data.carry, null, 'width:26px;height:26px;object-fit:cover;border:1px solid var(--cyan)')
      + '<span class="profile-comp-name"><b>' + esc(currentProfile ? currentProfile.riotId : '') + '</b> \u2014 ' + esc(data.compLabel) + '</span>'
      + '<span class="lb-square ' + (data.placement <= 4 ? 'win' : 'loss') + '">' + data.placement + '</span></div>';
    (data.lobby || []).forEach(function (l) {
      lobbyHtml += '<div class="profile-comp-row" style="cursor:default" data-counter="' + (l.isCounter ? 'true' : 'false') + '">'
        + '<span class="lb-square ' + (l.placement <= 4 ? 'win' : 'loss') + '">' + l.placement + '</span>'
        + champIcon(l.carrySlug, l.carry, null, 'width:26px;height:26px;object-fit:cover;border:1px solid var(--border-bright)')
        + (l.compSlug ? '<a class="profile-comp-name" href="' + ROOT + 'compo/' + l.compSlug + '/">' + esc(l.riotId) + ' \u2014 ' + esc(l.compLabel) + '</a>'
                       : '<span class="profile-comp-name">' + esc(l.riotId) + ' \u2014 ' + esc(l.compLabel) + '</span>')
        + (l.isCounter ? '<span class="metascope-counter-tag">' + esc(I.counterTag) + '</span>' : '')
        + '</div>';
    });

    var container = el('div', '',
      '<a class="back-link" href="javascript:;" id="msBackLink">' + esc(I.backButton) + '</a>'
      + '<div class="fiche-header">' + champIcon(data.carrySlug, data.carry, 'champ-fiche-icon')
      + '<div><h1 class="fiche-title">' + (data.compSlug ? '<a href="' + ROOT + 'compo/' + data.compSlug + '/" style="color:inherit">' + esc(data.compLabel) + '</a>' : esc(data.compLabel)) + '</h1></div>'
      + '<div class="fiche-stats pill-row">' + pill(I.placementLabel, data.placement)
      + (data.level ? pill(I.levelLabel, data.level) : '') + (data.goldLeft != null ? pill(I.goldLeftLabel, data.goldLeft) : '') + '</div></div>'
      + (unitsHtml ? '<h2 class="fiche-section-title">' + esc(I.yourBoardTitle) + '</h2><div class="fiche-board-wrap"><div class="fiche-board">' + unitsHtml + '</div></div>' : '')
      + '<h2 class="fiche-section-title">' + esc(I.insightsTitle) + '</h2>'
      + (I.lang === 'en' ? '<div class="metascope-lang-note">' + esc(I.insightsFrOnly) + '</div>' : '')
      + (insightsHtml ? '<div class="metascope-insight-list">' + insightsHtml + '</div>' : '<div class="matchup-empty">' + esc(I.noInsights) + '</div>')
      + '<h2 class="fiche-section-title">' + esc(I.lobbyTitle) + '</h2>'
      + (data.lobby && data.lobby.length ? '<div class="profile-comp-list">' + lobbyHtml + '</div>' : '<div class="matchup-empty">' + esc(I.noLobby) + '</div>'));

    results.innerHTML = '';
    results.appendChild(container);
    document.getElementById('msBackLink').addEventListener('click', function () {
      setUrl({ riotId: currentProfile.riotId, region: currentProfile.region });
      if (currentProfile) renderProfile(currentProfile);
    });
    window.scrollTo(0, 0);
  }

  async function runProfile(riotId, region) {
    setStatus(I.loading, false);
    results.innerHTML = '';
    try {
      var data = await fetchJson(API + '/profile?riotId=' + encodeURIComponent(riotId) + '&region=' + encodeURIComponent(region));
      setStatus(null);
      setUrl({ riotId: riotId, region: region });
      renderProfile(data);
    } catch (e) {
      setStatus(e.message || String(e), true);
    }
  }

  async function runAnalyze(matchId) {
    if (!currentProfile) return;
    setStatus(I.loading, false);
    try {
      var data = await fetchJson(API + '/analyze?region=' + encodeURIComponent(currentProfile.region) + '&matchId=' + encodeURIComponent(matchId) + '&puuid=' + encodeURIComponent(currentProfile.puuid));
      setStatus(null);
      setUrl({ riotId: currentProfile.riotId, region: currentProfile.region, match: matchId });
      renderAnalysis(data);
    } catch (e) {
      setStatus(e.message || String(e), true);
    }
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var riotId = riotIdInput.value.trim();
    var region = regionSelect.value;
    if (riotId) runProfile(riotId, region);
  });

  window.addEventListener('popstate', function (e) {
    var p = new URLSearchParams(location.search);
    var riotId = p.get('riotId');
    if (!riotId) { results.innerHTML = ''; setStatus(null); return; }
    riotIdInput.value = riotId;
    regionSelect.value = p.get('region') || 'EUW';
    runProfile(riotId, regionSelect.value).then(function () {
      var matchId = p.get('match');
      if (matchId) runAnalyze(matchId);
    });
  });

  // Auto-run on load if the URL already carries a lookup (shared link, or a
  // refresh/back-navigation onto a result).
  var initial = new URLSearchParams(location.search);
  var initialRiotId = initial.get('riotId');
  if (initialRiotId) {
    riotIdInput.value = initialRiotId;
    regionSelect.value = initial.get('region') || 'EUW';
    runProfile(initialRiotId, regionSelect.value).then(function () {
      var matchId = initial.get('match');
      if (matchId) runAnalyze(matchId);
    });
  }
})();
