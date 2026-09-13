
(function () {
  var API = window.BM_LEAGUE_API;
  var I = window.BM_I18N_LEAGUE || {};
  var form = document.getElementById('leagueForm');
  var riotIdInput = document.getElementById('leagueRiotId');
  var regionSelect = document.getElementById('leagueRegion');
  var statusEl = document.getElementById('leagueStatus');
  var results = document.getElementById('leagueResults');
  if (!form || !API) return;

  var ROLE_ICON = {
    top: '<path opacity="0.5" fill="#785a28" fill-rule="evenodd" d="M21,14H14v7h7V14Zm5-3V26L11.014,26l-4,4H30V7.016Z"/><polygon fill="#c8aa6e" points="4 4 4.003 28.045 9 23 9 9 23 9 28.045 4.003 4 4"/>',
    jungle: '<path fill="#c8aa6e" fill-rule="evenodd" d="M25,3c-2.128,3.3-5.147,6.851-6.966,11.469A42.373,42.373,0,0,1,20,20a27.7,27.7,0,0,1,1-3C21,12.023,22.856,8.277,25,3ZM13,20c-1.488-4.487-4.76-6.966-9-9,3.868,3.136,4.422,7.52,5,12l3.743,3.312C14.215,27.917,16.527,30.451,17,31c4.555-9.445-3.366-20.8-8-28C11.67,9.573,13.717,13.342,13,20Zm8,5a15.271,15.271,0,0,1,0,2l4-4c0.578-4.48,1.132-8.864,5-12C24.712,13.537,22.134,18.854,21,25Z"/>',
    mid: '<path opacity="0.5" fill="#785a28" fill-rule="evenodd" d="M30,12.968l-4.008,4L26,26H17l-4,4H30ZM16.979,8L21,4H4V20.977L8,17,8,8h8.981Z"/><polygon fill="#c8aa6e" points="25 4 4 25 4 30 9 30 30 9 30 4 25 4"/>',
    adc: '<path opacity="0.5" fill="#785a28" fill-rule="evenodd" d="M13,20h7V13H13v7ZM4,4V26.984l3.955-4L8,8,22.986,8l4-4H4Z"/><polygon fill="#c8aa6e" points="29.997 5.955 25 11 25 25 11 25 5.955 29.997 30 30 29.997 5.955"/>',
    support: '<path fill="#c8aa6e" fill-rule="evenodd" d="M26,13c3.535,0,8-4,8-4H23l-3,3,2,7,5-2-3-4h2ZM22,5L20.827,3H13.062L12,5l5,6Zm-5,9-1-1L13,28l4,3,4-3L18,13ZM11,9H0s4.465,4,8,4h2L7,17l5,2,2-7Z"/>',
  };
  var ROLE_LABEL = { top: 'Top', jungle: 'Jungle', mid: 'Mid', adc: 'ADC', support: 'Support' };
  var WEEKDAY_LABELS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

  function roleIcon(role) { return '<svg class="league-champ-role-icon" viewBox="0 0 34 34" xmlns="http://www.w3.org/2000/svg">' + (ROLE_ICON[role] || '') + '</svg>'; }
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }
  function initials(name) { return (name || '?').replace(/[^A-Za-z]/g, '').slice(0, 2).toUpperCase() || '?'; }

  // Portraits de champion réels (Data Dragon, clé = championName renvoyé
  // tel quel par Match-V5 -- garanti identique à la clé ddragon par Riot,
  // aucune table de correspondance à maintenir). La version est résolue
  // une fois au chargement plutôt que codée en dur, pour ne pas se
  // périmer à chaque patch.
  var ddragonVersion = null;
  var ddragonReady = fetch('https://ddragon.leagueoflegends.com/api/versions.json')
    .then(function (r) { return r.json(); })
    .then(function (v) { ddragonVersion = v[0]; })
    .catch(function () {});
  function champIconHtml(championName) {
    if (ddragonVersion) {
      return '<img class="league-icon-fallback" src="https://ddragon.leagueoflegends.com/cdn/' + ddragonVersion + '/img/champion/' + encodeURIComponent(championName) + '.png" alt="' + esc(championName) + '" style="width:32px;height:32px;object-fit:cover;border:1px solid var(--border-bright);flex:none" loading="lazy">';
    }
    return '<span class="player-avatar" style="width:32px;height:32px;font-size:11px">' + esc(initials(championName)) + '</span>';
  }

  function el(tag, className, html) {
    var e = document.createElement(tag);
    if (className) e.className = className;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  function setStatus(text, isError) {
    if (!text) { statusEl.hidden = true; statusEl.textContent = ''; return; }
    statusEl.hidden = false;
    statusEl.textContent = text;
    statusEl.dataset.error = isError ? 'true' : 'false';
  }
  function setUrl(params) {
    var qs = new URLSearchParams(params).toString();
    history.pushState(params, '', location.pathname + (qs ? '?' + qs : ''));
  }
  async function fetchJson(url) {
    var res = await fetch(url);
    var data = await res.json().catch(function () { return {}; });
    if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));
    return data;
  }
  function bindIconFallback(container) {
    container.querySelectorAll('.league-icon-fallback').forEach(function (img) {
      img.addEventListener('error', function () { img.style.visibility = 'hidden'; });
    });
  }
  function timeAgo(ts) {
    var mins = Math.round((Date.now() - ts) / 60000);
    if (mins < 60) return mins + ' min';
    var hours = Math.round(mins / 60);
    if (hours < 24) return hours + ' h';
    return Math.round(hours / 24) + ' j';
  }

  var currentData = null;
  var currentQueue = 'solo';

  function rankCard(label, entry) {
    if (!entry) return '<div class="league-rank-card"><span class="league-rank-queue">' + label + '</span><span class="league-rank-tier" style="color:var(--text-faint)">Non classé</span></div>';
    return '<div class="league-rank-card"><span class="league-rank-queue">' + label + '</span>'
      + '<span class="lb-tier-tag" data-tier="' + entry.tier + '">' + entry.tier + ' ' + entry.rank + '</span>'
      + '<span class="league-rank-lp">' + entry.leaguePoints + ' LP</span>'
      + '<span class="player-meta" style="margin:0">' + entry.wins + 'V ' + entry.losses + 'D</span></div>';
  }

  function matchRowHtml(m) {
    var kda = ((m.kills + m.assists) / Math.max(1, m.deaths)).toFixed(1);
    var itemsHtml = m.items.map(function (it) {
      return it.iconUrl ? '<img class="league-item-slot league-icon-fallback" src="' + it.iconUrl + '" alt="" loading="lazy">' : '<span class="league-item-slot"></span>';
    }).join('');
    var spellsHtml = m.spells.map(function (s) {
      return s.iconUrl ? '<img class="league-spell-icon league-icon-fallback" src="' + s.iconUrl + '" alt="' + esc(s.name) + '" title="' + esc(s.name) + '" loading="lazy">' : '';
    }).join('');
    var runesHtml = (m.runes.keystoneIconUrl ? '<img class="league-rune-icon league-icon-fallback" src="' + m.runes.keystoneIconUrl + '" alt="" title="' + esc(m.runes.keystoneName) + '" loading="lazy">' : '')
      + (m.runes.secondaryStyleIconUrl ? '<img class="league-rune-icon league-icon-fallback" src="' + m.runes.secondaryStyleIconUrl + '" alt="" title="' + esc(m.runes.secondaryStyleName) + '" style="width:14px;height:14px" loading="lazy">' : '');
    return '<div class="league-match-row" data-win="' + m.win + '">'
      + '<span class="league-match-result">' + (m.win ? 'Victoire' : 'Défaite') + '</span>'
      + '<span class="league-match-champ">' + roleIcon(m.role) + champIconHtml(m.champion) + esc(m.champion) + '</span>'
      + '<span class="league-loadout"><span class="league-loadout-col">' + spellsHtml + '</span><span class="league-loadout-col">' + runesHtml + '</span><span class="league-items">' + itemsHtml + '</span></span>'
      + '<span class="league-match-kda mono">' + m.kills + '/' + m.deaths + '/' + m.assists + '<br><span style="color:var(--text-faint);font-size:10px">' + kda + ' KDA</span></span>'
      + '<span class="league-match-cs">' + m.cs + ' CS<br>' + (m.cs / m.durationMin).toFixed(1) + '/min</span>'
      + '<span class="league-match-meta">' + m.durationMin.toFixed(0) + ' min<br>' + timeAgo(m.startedAt) + '</span>'
      + '</div>';
  }

  // Les deux sections que l'API Riot ne peut pas alimenter aujourd'hui --
  // Match-V5 ne donne que le LP ACTUEL (pas d'historique) et n'expose ni
  // pings ni messages, à aucun endpoint. Rendues avec un exemple fixe et
  // clairement étiqueté, pas des chiffres qui feraient croire à de la
  // vraie donnée du joueur recherché.
  function devSectionsHtml() {
    var badge = '<div class="league-dev-badge"><span class="dot"></span>En développement -- en attente de l\'API de production Riot</div>';
    var lpPoints = '0,60 20,52 40,58 60,40 80,44 100,26 120,30 140,14 160,20 180,6';
    return '<div class="metascope-box" style="margin-top:16px">'
      + badge
      + '<div class="metascope-box-title">Progression de LP</div>'
      + '<p class="metascope-hint" style="margin:0 0 10px">Match-V5 ne donne que ton LP du moment, pas son historique -- cette courbe montre à quoi ça ressemblera une fois qu\'on aura commencé à relever ton LP dans le temps. Exemple illustratif :</p>'
      + '<svg viewBox="0 0 180 70" style="width:100%;height:80px;display:block"><polyline points="' + lpPoints + '" fill="none" stroke="var(--cyan)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
      + '</div>'
      + '<div class="metascope-box" style="margin-top:16px">'
      + badge
      + '<div class="metascope-box-title">Communication en jeu</div>'
      + '<p class="metascope-hint" style="margin:0 0 10px">Les pings et les messages de chat ne sont pas exposés par l\'API Riot, à aucun endpoint -- cette section restera un exemple tant que ça n\'aura pas changé. Exemple illustratif :</p>'
      + '<div class="metascope-stat-row"><span>Messages / partie</span><b class="nums">6.4</b></div>'
      + '<div class="metascope-stat-row"><span>En chemin</span><b class="nums">2.1 / partie</b></div>'
      + '<div class="metascope-stat-row"><span>Ennemi manquant</span><b class="nums">1.8 / partie</b></div>'
      + '<div class="metascope-stat-row"><span>Attention</span><b class="nums">1.2 / partie</b></div>'
      + '</div>';
  }

  function renderQueue(queueKey) {
    currentQueue = queueKey;
    var q = currentData.queues[queueKey];
    document.querySelectorAll('.league-queue-tab').forEach(function (btn) {
      btn.setAttribute('data-active', btn.dataset.queue === queueKey ? 'true' : 'false');
    });

    var matchListHtml = q.matches.length
      ? q.matches.map(matchRowHtml).join('')
      : '<div class="matchup-empty">Aucune partie récente dans cette file (sur les ' + (q.matches.length || 0) + ' dernières parties toutes files confondues).</div>';

    var maxRoleGames = Math.max.apply(null, q.roleStats.map(function (r) { return r.games; })) || 1;
    var roleHtml = q.roleStats.length ? q.roleStats.map(function (r) {
      var pct = Math.round((r.games / maxRoleGames) * 100);
      return '<div class="league-role-row"><span class="league-role-name">' + roleIcon(r.role) + (ROLE_LABEL[r.role] || r.role) + '</span>'
        + '<div class="league-role-bar-track"><div class="league-role-bar-fill" style="width:' + pct + '%"></div></div>'
        + '<span class="league-role-wr" style="color:' + (r.wr >= 50 ? 'var(--good)' : 'var(--warn)') + '">' + r.wr + '%</span></div>';
    }).join('') : '<div class="matchup-empty">Pas de partie dans cette file.</div>';

    function compareLine(label, you, rank, unit, decimals) {
      var scale = Math.max(you, rank) * 1.15 || 1;
      return '<div class="league-compare-line"><span>' + label + '</span><div class="league-compare-track"><div class="league-compare-fill you" style="width:' + Math.round((you / scale) * 100) + '%"></div></div><span class="league-compare-val mono">' + you.toFixed(decimals) + unit + '</span></div>'
        + '<div class="league-compare-line"><span>Rang</span><div class="league-compare-track"><div class="league-compare-fill rank" style="width:' + Math.round((rank / scale) * 100) + '%"></div></div><span class="league-compare-val mono">' + rank.toFixed(decimals) + unit + '</span></div>';
    }
    var ra = currentData.rankAverages;
    var sa = q.statsAvg;
    var compareHtml = (q.matches.length ? [
      '<div class="league-compare-card"><div class="league-compare-label">CS / min</div>' + compareLine('Toi', sa.csPerMin, ra.csPerMin, '', 1) + '</div>',
      '<div class="league-compare-card"><div class="league-compare-label">Gold / min</div>' + compareLine('Toi', sa.goldPerMin, ra.goldPerMin, '', 0) + '</div>',
      '<div class="league-compare-card"><div class="league-compare-label">Dégâts / min</div>' + compareLine('Toi', sa.dmgPerMin, ra.dmgPerMin, '', 0) + '</div>',
      '<div class="league-compare-card"><div class="league-compare-label">Participation aux kills</div>' + compareLine('Toi', sa.killParticipation, ra.killParticipation, '%', 0) + '</div>',
    ].join('') : '<div class="matchup-empty">Pas assez de parties pour comparer.</div>');

    var maxWeekday = Math.max.apply(null, q.weekdayStats.map(function (d) { return d.games; })) || 1;
    var weekdayHtml = q.weekdayStats.map(function (d) {
      var pct = Math.round((d.games / maxWeekday) * 100);
      return '<div class="league-weekday-col"><div class="league-weekday-val mono">' + d.games + '</div>'
        + '<div class="league-weekday-track"><div class="league-weekday-fill ' + (d.games === 0 ? '' : (d.wr >= 50 ? 'good' : 'warn')) + '" style="height:' + pct + '%"></div></div>'
        + '<div class="league-weekday-label">' + d.label + '</div></div>';
    }).join('');

    var hourlyHtml = q.hourlyStats.filter(function (h) { return h.games > 0; }).map(function (h) {
      return '<div class="league-hourly-row"><span class="league-hourly-time">' + (h.hour < 10 ? '0' : '') + h.hour + ':00</span>'
        + '<span class="league-hourly-badge ' + (h.wr >= 50 ? 'good' : 'warn') + '">' + h.games + ' parties</span>'
        + '<span class="league-hourly-wr mono">' + h.wr + '%</span></div>';
    }).join('') || '<div class="matchup-empty">Pas assez de parties pour un historique horaire.</div>';

    var playedWithHtml = q.playedWith.length ? q.playedWith.map(function (p) {
      return '<div class="league-playedwith-row"><span class="league-playedwith-name">' + esc(p.riotId) + '</span>'
        + '<span class="player-meta" style="margin:0">' + p.games + ' parties</span>'
        + '<span class="league-playedwith-wr" style="color:' + (p.wr >= 50 ? 'var(--good)' : 'var(--warn)') + '">' + p.wr + '%</span></div>';
    }).join('') : '<div class="matchup-empty">Pas de coéquipier récurrent détecté sur cet échantillon.</div>';

    var main = document.getElementById('leagueQueuePanel');
    main.innerHTML =
      '<div class="metascope-layout">'
      + '<div class="metascope-sidebar">'
      + '<div class="metascope-box"><div class="metascope-box-title">Répartition par rôle</div><div class="league-role-list">' + roleHtml + '</div></div>'
      + '<div class="metascope-box"><div class="metascope-box-title">Joué avec</div>' + playedWithHtml + '</div>'
      + '</div>'
      + '<div class="metascope-main">'
      + '<h2 class="fiche-section-title" style="margin-top:0">Historique (' + q.matches.length + ' parties)</h2>'
      + '<div class="league-match-list">' + matchListHtml + '</div>'
      + '</div>'
      + '</div>'
      + '<div class="metascope-box" style="margin-top:20px"><div class="metascope-box-title">Toi vs moyenne du rang</div><div class="league-compare-grid">' + compareHtml + '</div></div>'
      + '<div class="metascope-box" style="margin-top:16px"><div class="metascope-box-title">Modèles d\'activité</div>'
      + '<div class="league-weekday-chart">' + weekdayHtml + '</div>'
      + '<div class="league-hourly-list">' + hourlyHtml + '</div></div>'
      + devSectionsHtml();
    bindIconFallback(main);
  }

  function renderProfile(data) {
    currentData = data;
    var avatarHtml = data.profileIconId
      ? '<img class="league-icon-fallback" src="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/' + data.profileIconId + '.jpg" alt="">'
      : esc(initials(data.riotId));
    var header = el('div', 'player-header',
      '<div class="player-avatar">' + avatarHtml + '</div>'
      + '<div><div class="player-name-row"><span class="player-name">' + esc(data.riotId) + '</span></div>'
      + '<div class="player-meta">' + esc(data.region) + (data.summonerLevel ? ' &middot; Niveau ' + data.summonerLevel : '') + '</div></div>');

    var rankRow = el('div', 'league-rank-row', rankCard('Solo/Duo', data.ranks.solo) + rankCard('Flex', data.ranks.flex));

    var queueTabs = el('div', 'league-queue-tabs',
      '<button type="button" class="league-queue-tab" data-queue="solo" data-active="true">Classé en solo/duo</button>'
      + '<button type="button" class="league-queue-tab" data-queue="flex">Classé flexible</button>');

    var panel = el('div', '');
    panel.id = 'leagueQueuePanel';

    results.innerHTML = '';
    results.appendChild(header);
    bindIconFallback(header);
    results.appendChild(rankRow);
    results.appendChild(queueTabs);
    results.appendChild(panel);

    queueTabs.querySelectorAll('.league-queue-tab').forEach(function (btn) {
      btn.addEventListener('click', function () { renderQueue(btn.dataset.queue); });
    });

    renderQueue('solo');
    window.scrollTo(0, 0);
  }

  async function runProfile(riotId, region) {
    setStatus(I.loading || 'Recherche en cours…', false);
    results.innerHTML = '';
    try {
      await ddragonReady;
      var data = await fetchJson(API + '/profile?riotId=' + encodeURIComponent(riotId) + '&region=' + encodeURIComponent(region));
      setStatus(null);
      setUrl({ riotId: riotId, region: region });
      renderProfile(data);
      if (window.gtag) gtag('event', 'league_lookup', { region: region, success: true });
    } catch (e) {
      setStatus(e.message || String(e), true);
      if (window.gtag) gtag('event', 'league_lookup', { region: region, success: false });
    }
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var riotId = riotIdInput.value.trim();
    if (riotId) runProfile(riotId, regionSelect.value);
  });

  window.addEventListener('popstate', function () {
    var p = new URLSearchParams(location.search);
    var riotId = p.get('riotId');
    if (!riotId) { results.innerHTML = ''; setStatus(null); return; }
    riotIdInput.value = riotId;
    regionSelect.value = p.get('region') || 'EUW';
    runProfile(riotId, regionSelect.value);
  });

  var initial = new URLSearchParams(location.search);
  var initialRiotId = initial.get('riotId');
  if (initialRiotId) {
    riotIdInput.value = initialRiotId;
    regionSelect.value = initial.get('region') || 'EUW';
    runProfile(initialRiotId, regionSelect.value);
  }
})();
