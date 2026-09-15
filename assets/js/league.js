
(function () {
  // Straight port of the BrokenMeta League concept Artifact's rendering
  // (same HTML structure/CSS classes as league_profile's <style>, see
  // build_site.py), but every function here reads from the REAL worker
  // payload instead of a seeded mock generator -- no MATCH_HISTORY, no
  // fabricated duo/ping/message data. Only two sections stay illustrative
  // (see devSectionsHtml): Riot's API has no LP-history endpoint and
  // exposes no ping/chat data at all, at any endpoint.
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
  var QUEUE_LABEL = { solo: 'Classé en solo/duo', flex: 'Classé flexible', aram: 'ARAM' };

  function roleIcon(role, cls) { return '<svg class="' + (cls || 'champ-role-icon') + '" viewBox="0 0 34 34" xmlns="http://www.w3.org/2000/svg">' + (ROLE_ICON[role] || '') + '</svg>'; }
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }
  function initials(name) { return (name || '?').replace(/[^A-Za-z]/g, '').slice(0, 2).toUpperCase() || '?'; }
  function tierLabel(tier) { return tier ? tier.charAt(0) + tier.slice(1).toLowerCase() : ''; }

  // Portraits de champion réels (Data Dragon, clé = championName renvoyé
  // tel quel par Match-V5 -- garanti identique à la clé ddragon par Riot,
  // aucune table de correspondance à maintenir). Version résolue une fois
  // au chargement plutôt que codée en dur, pour ne pas se périmer à
  // chaque patch.
  var ddragonVersion = null;
  var ddragonReady = fetch('https://ddragon.leagueoflegends.com/api/versions.json')
    .then(function (r) { return r.json(); })
    .then(function (v) { ddragonVersion = v[0]; })
    .catch(function () {});
  function champPortraitInner(championName) {
    if (ddragonVersion) {
      return '<img class="league-icon-fallback" src="https://ddragon.leagueoflegends.com/cdn/' + ddragonVersion + '/img/champion/' + encodeURIComponent(championName) + '.png" alt="' + esc(championName) + '" loading="lazy">';
    }
    return esc(initials(championName));
  }

  // Glossaire des objets (nom réel, description courte, prix) -- source
  // Data Dragon, la même que pour ddragonVersion ci-dessus, en FR ou EN
  // selon la langue de la page. Alimente uniquement l'infobulle au survol
  // d'une icône d'objet (voir wireItemTooltip) ; les icônes elles-mêmes
  // viennent toujours de itemIconMap côté worker (CommunityDragon), ce
  // fichier ne sert qu'à retrouver le nom/texte à partir de l'id Riot.
  var lolItemGlossary = null;
  ddragonReady.then(function () {
    if (!ddragonVersion) return;
    var locale = document.documentElement.lang === 'fr' ? 'fr_FR' : 'en_US';
    return fetch('https://ddragon.leagueoflegends.com/cdn/' + ddragonVersion + '/data/' + locale + '/item.json')
      .then(function (r) { return r.json(); })
      .then(function (d) {
        lolItemGlossary = {};
        Object.keys(d.data || {}).forEach(function (id) {
          var it = d.data[id];
          lolItemGlossary[id] = { name: it.name, plaintext: it.plaintext || '', price: it.gold ? it.gold.total : null };
        });
      });
  }).catch(function () {});

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

  // Infobulle au survol d'une icône d'objet -- même mécanisme (#tooltip
  // partagé, classes .tt-*) que CHAMP_ICON_JS/GLOSSARY_ITEM_JS pour la
  // partie TFT du site. Délégation sur `document` : les lignes de partie
  // sont réinjectées via innerHTML à chaque rendu (renderProfile,
  // renderQueue...), pas la peine de re-brancher un listener par icône.
  var lolTooltip = document.getElementById('tooltip');
  function showItemTooltip(icon, e) {
    if (!lolItemGlossary || !lolTooltip) return;
    var d = lolItemGlossary[icon.dataset.itemId];
    if (!d) return;
    lolTooltip.innerHTML = '<div class="tt-name">' + esc(d.name) + '</div>'
      + (d.price ? '<div class="tt-row"><span>Prix</span><b class="nums">' + d.price + '</b></div>' : '')
      + (d.plaintext ? '<div class="tt-items">' + esc(d.plaintext) + '</div>' : '');
    lolTooltip.dataset.visible = 'true';
    moveItemTooltip(e);
  }
  function moveItemTooltip(e) {
    if (!lolTooltip) return;
    var pad = 14, x = e.clientX + pad, y = e.clientY + pad;
    if (x + 190 > window.innerWidth) x = e.clientX - 190 - pad;
    if (y + 130 > window.innerHeight) y = e.clientY - 130 - pad;
    lolTooltip.style.left = x + 'px';
    lolTooltip.style.top = y + 'px';
  }
  function hideItemTooltip() { if (lolTooltip) lolTooltip.dataset.visible = 'false'; }
  document.addEventListener('mouseover', function (e) {
    var icon = e.target.closest('.item-slot[data-item-id]');
    if (icon) showItemTooltip(icon, e);
  });
  document.addEventListener('mousemove', function (e) {
    if (e.target.closest('.item-slot[data-item-id]')) moveItemTooltip(e);
  });
  document.addEventListener('mouseout', function (e) {
    if (e.target.closest('.item-slot[data-item-id]')) hideItemTooltip();
  });
  function timeAgo(ts) {
    var mins = Math.round((Date.now() - ts) / 60000);
    if (mins < 60) return mins + ' min';
    var hours = Math.round(mins / 60);
    if (hours < 24) return hours + ' h';
    return Math.round(hours / 24) + ' j';
  }
  // Anneau de winrate -- rayon 27 (circonférence ~169.65), même tracé que
  // l'artefact mais avec le pourcentage RÉEL du joueur, pas une valeur
  // figée dans le markup.
  function rankRingSvg(pct, good) {
    var c = 169.65;
    var offset = Math.round((c * (1 - pct / 100)) * 10) / 10;
    return '<svg viewBox="0 0 64 64" class="rank-ring">'
      + '<circle cx="32" cy="32" r="27" fill="none" stroke="var(--border-bright)" stroke-width="6"/>'
      + '<circle cx="32" cy="32" r="27" fill="none" stroke="var(--' + (good ? 'good' : 'warn') + ')" stroke-width="6" stroke-linecap="round" stroke-dasharray="' + c + '" stroke-dashoffset="' + offset + '" transform="rotate(-90 32 32)"/>'
      + '</svg>';
  }

  var currentData = null;
  var currentQueue = 'solo';
  var currentTab = 'history';

  function buildLoadoutHtml(m) {
    var itemsHtml = m.items.map(function (it) {
      return it.iconUrl ? '<img class="item-slot league-icon-fallback" src="' + it.iconUrl + '" data-item-id="' + it.id + '" alt="" loading="lazy">' : '<span class="item-slot"></span>';
    }).join('');
    var spellsHtml = m.spells.map(function (s) {
      return s.iconUrl ? '<img class="spell-icon league-icon-fallback" src="' + s.iconUrl + '" alt="" title="' + esc(s.name) + '" loading="lazy">' : '';
    }).join('');
    var runesHtml = (m.runes.keystoneIconUrl ? '<img class="rune-icon league-icon-fallback" src="' + m.runes.keystoneIconUrl + '" alt="" title="' + esc(m.runes.keystoneName) + '" loading="lazy">' : '')
      + (m.runes.secondaryStyleIconUrl ? '<img class="rune-icon small league-icon-fallback" src="' + m.runes.secondaryStyleIconUrl + '" alt="" title="' + esc(m.runes.secondaryStyleName) + '" loading="lazy">' : '');
    return '<div class="match-loadout">'
      + '<div class="spell-col">' + spellsHtml + '</div>'
      + '<div class="spell-col">' + runesHtml + '</div>'
      + '<div class="match-loadout-items">' + itemsHtml + '</div>'
      + '</div>';
  }

  function matchRowHtml(m, idx) {
    var kdaRatio = ((m.kills + m.assists) / Math.max(1, m.deaths)).toFixed(1);
    var csPerMin = (m.cs / m.durationMin).toFixed(1);
    return '<div class="match-row-wrap">'
      + '<div class="match-row ' + (m.win ? 'win' : 'loss') + '">'
      + '<div class="match-result">' + (m.win ? 'Victoire' : 'Défaite') + '</div>'
      + '<div class="match-champ-block">' + roleIcon(m.role, 'champ-role-icon')
      + '<span class="champ-portrait-wrap"><span class="champ-portrait">' + champPortraitInner(m.champion) + '</span>'
      + (m.runes.keystoneIconUrl ? '<img class="champ-rune-badge league-icon-fallback" src="' + m.runes.keystoneIconUrl + '" alt="" title="' + esc(m.runes.keystoneName) + '" loading="lazy">' : '') + '</span>'
      + '<div><div class="match-champ-name">' + esc(m.champion) + '</div><div class="match-queue">' + QUEUE_LABEL[currentQueue] + '</div></div></div>'
      + buildLoadoutHtml(m)
      + '<div class="match-kda"><div class="match-kda-v mono">' + m.kills + '/' + m.deaths + '/' + m.assists + '</div><div class="match-kda-ratio">' + kdaRatio + ' KDA</div></div>'
      + '<div class="match-cs"><div class="mono">' + m.cs + ' CS</div><div class="match-cs-l">' + csPerMin + '/min</div></div>'
      + '<div class="match-meta">' + m.durationMin.toFixed(0) + ' min<br>' + timeAgo(m.startedAt) + '</div>'
      + '<button type="button" class="match-expand-btn" id="matchExpandBtn' + idx + '" aria-expanded="false" aria-label="Voir la partie">'
      + '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg></button>'
      + '</div>'
      + '<div class="match-detail" id="matchDetail' + idx + '" hidden></div>'
      + '</div>';
  }

  function renderScoreboardTeam(players, label, sideClass) {
    return '<div class="scoreboard-team ' + sideClass + '"><div class="scoreboard-team-label">' + label + '</div>'
      + players.map(function (p) {
        var kdaText = p.isSelf ? '' : '<span class="scoreboard-kda mono">' + p.kills + '/' + p.deaths + '/' + p.assists + '</span>';
        var itemsHtml = p.items.map(function (it) {
          return it.iconUrl ? '<img class="item-slot league-icon-fallback" src="' + it.iconUrl + '" data-item-id="' + it.id + '" alt="" loading="lazy">' : '<span class="item-slot"></span>';
        }).join('');
        return '<div class="scoreboard-row' + (p.isSelf ? ' is-self' : '') + '">'
          + roleIcon(p.role, 'champ-role-icon') + '<span class="champ-portrait">' + champPortraitInner(p.champion) + '</span>'
          + '<span class="scoreboard-name">' + (p.isSelf ? esc(p.champion) + ' (toi)' : esc(p.name)) + '</span>'
          + kdaText
          + '<span class="scoreboard-cs mono">' + p.cs + ' CS</span>'
          + '<span class="scoreboard-gold mono">' + (p.gold / 1000).toFixed(1) + 'k</span>'
          + '<span class="scoreboard-items">' + itemsHtml + '</span>'
          + '</div>';
      }).join('') + '</div>';
  }

  // Badges de perf + classement dans la partie -- calculés sur le K/D/A
  // RÉEL du joueur et comparés aux 9 AUTRES vrais scores du scoreboard
  // (pas de simulation). Pas de ligne "elo moyen" ici : Riot n'expose pas
  // le rang des autres joueurs d'une partie, contrairement au mockup.
  function buildMatchSummary(m) {
    var badges = [];
    if (m.deaths === 0) badges.push('Increvable');
    if (m.kills >= 7) badges.push('Triple Kill');
    else if (m.kills >= 5) badges.push('Double Kill');
    if (m.assists >= 10) badges.push('Soutien exemplaire');

    function score(p) { return p.kills * 2 + p.assists - p.deaths * 1.5; }
    var mySelf = m.scoreboard.filter(function (p) { return p.isSelf; })[0];
    var ranked = m.scoreboard.slice().sort(function (a, b) { return score(b) - score(a); });
    var rank = ranked.indexOf(mySelf) + 1;
    var medal = rank <= 3 ? 'Or' : rank <= 6 ? 'Argent' : 'Bronze';
    badges.unshift(medal + ' ' + rank + '/10');

    var badgesHtml = badges.map(function (b, i) {
      return '<span class="perf-badge' + (i === 0 ? ' medal' : '') + '">' + b + '</span>';
    }).join('');
    return '<div class="match-summary-strip"><div class="summary-badges">' + badgesHtml + '</div></div>';
  }

  function toggleMatchDetail(idx, m) {
    var detail = document.getElementById('matchDetail' + idx);
    var willOpen = detail.hidden;
    detail.hidden = !willOpen;
    document.getElementById('matchExpandBtn' + idx).setAttribute('aria-expanded', willOpen ? 'true' : 'false');
    if (willOpen && !detail.dataset.built) {
      var allies = m.scoreboard.filter(function (p) { return p.team === 'ally'; });
      var enemies = m.scoreboard.filter(function (p) { return p.team === 'enemy'; });
      detail.innerHTML = buildMatchSummary(m) + '<div class="scoreboard-grid">'
        + renderScoreboardTeam(allies, 'Alliés', 'ally')
        + renderScoreboardTeam(enemies, 'Adversaires', 'enemy')
        + '</div>';
      detail.dataset.built = '1';
      bindIconFallback(detail);
    }
  }

  function renderMatchList(matches) {
    var list = document.getElementById('matchHistoryList');
    if (!matches.length) { list.innerHTML = '<div class="matchup-empty">Aucune partie récente dans cette file.</div>'; return; }
    list.innerHTML = matches.map(matchRowHtml).join('');
    bindIconFallback(list);
    matches.forEach(function (m, idx) {
      document.getElementById('matchExpandBtn' + idx).addEventListener('click', function () { toggleMatchDetail(idx, m); });
    });
  }

  function champKda(c) { return c.kda.toFixed(1); }

  function renderChampionsTable(champions) {
    var wrap = document.getElementById('championsTableWrap');
    if (!champions.length) { wrap.innerHTML = '<div class="matchup-empty" style="padding:16px">Aucun champion joué dans cette file.</div>'; return; }
    var rows = champions.map(function (c) {
      return '<tr><td><div class="champ-cell"><span class="champ-portrait">' + champPortraitInner(c.champ) + '</span>' + esc(c.champ) + '</div></td>'
        + '<td class="num mono">' + c.games + '</td>'
        + '<td class="num"><span class="' + (c.wr >= 50 ? 'good' : 'warn') + '">' + c.wr + '%</span></td>'
        + '<td class="num mono">' + c.avgKills.toFixed(1) + ' / ' + c.avgDeaths.toFixed(1) + ' / ' + c.avgAssists.toFixed(1) + '</td>'
        + '<td class="num mono">' + champKda(c) + '</td></tr>';
    }).join('');
    wrap.innerHTML = '<div class="champions-table-scroll"><table class="champions-table"><thead><tr><th>Champion</th><th class="num">Parties</th><th class="num">Winrate</th><th class="num">KDA moyen</th><th class="num">Ratio</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
    bindIconFallback(wrap);
  }

  // Les deux sections que l'API Riot ne peut pas alimenter aujourd'hui --
  // Match-V5 ne donne que le LP ACTUEL (pas d'historique) et n'expose ni
  // pings ni messages, à aucun endpoint. Exemple fixe et clairement
  // étiqueté, jamais présenté comme la donnée du joueur recherché.
  function devSectionsHtml() {
    var badge = '<div class="league-dev-badge"><span class="dot"></span>En développement -- en attente de l\'API de production Riot</div>';
    var lpPoints = '10,150 90,120 170,135 250,90 330,100 410,55 490,65 570,25 650,45 730,10';
    return '<div class="stats-section"><div class="lp-chart-card">' + badge
      + '<div class="stats-block-title" style="margin-bottom:8px">Progression de LP</div>'
      + '<p class="profile-section-note" style="display:block;margin-bottom:10px">Match-V5 ne donne que ton LP du moment, pas son historique -- cette courbe montre à quoi ça ressemblera une fois qu\'on aura commencé à relever ton LP dans le temps. Exemple illustratif :</p>'
      + '<svg viewBox="0 0 740 170" class="lp-chart-svg"><line x1="8" y1="90" x2="732" y2="90" class="lp-chart-zero"/>'
      + '<polygon points="' + lpPoints + ' 730,156 10,156" class="lp-chart-area"/>'
      + '<polyline points="' + lpPoints + '" class="lp-chart-line"/><circle cx="730" cy="10" r="4.5" class="lp-chart-dot"/></svg>'
      + '</div></div>'
      + '<div class="stats-section"><div class="lp-chart-card">' + badge
      + '<div class="stats-block-title" style="margin-bottom:8px">Communication en jeu</div>'
      + '<p class="profile-section-note" style="display:block;margin-bottom:10px">Les pings et les messages de chat ne sont exposés par l\'API Riot à aucun endpoint -- cette section restera un exemple tant que ça n\'aura pas changé. Exemple illustratif :</p>'
      + '<div class="stats-comms-grid"><div class="stats-comms-msg"><div class="stats-comms-msg-value mono">6.4</div><div class="stats-comms-msg-label">Messages / partie</div></div>'
      + '<div class="comms-ping-list">'
      + '<div class="comms-ping-row"><span class="comms-ping-label">En chemin</span><div class="comms-ping-bar-track"><div class="comms-ping-bar-fill" style="width:70%"></div></div><span class="comms-ping-value mono">2.1 / partie</span></div>'
      + '<div class="comms-ping-row"><span class="comms-ping-label">Ennemi manquant</span><div class="comms-ping-bar-track"><div class="comms-ping-bar-fill" style="width:60%"></div></div><span class="comms-ping-value mono">1.8 / partie</span></div>'
      + '<div class="comms-ping-row"><span class="comms-ping-label">Attention</span><div class="comms-ping-bar-track"><div class="comms-ping-bar-fill" style="width:40%"></div></div><span class="comms-ping-value mono">1.2 / partie</span></div>'
      + '</div></div></div></div>';
  }

  function renderStatsTab(q, rankAverages) {
    var wrap = document.getElementById('statsTabWrap');
    var topChamps = q.champions.filter(function (c) { return c.games >= 2; }).slice().sort(function (a, b) { return b.kda - a.kda; }).slice(0, 3);
    var topChampsHtml = topChamps.length ? topChamps.map(function (c, i) {
      return '<div class="stats-top-champ-card"><span class="stats-top-champ-rank">#' + (i + 1) + '</span>'
        + '<span class="champ-portrait">' + champPortraitInner(c.champ) + '</span>'
        + '<div class="stats-top-champ-info"><div class="stats-top-champ-name">' + esc(c.champ) + '</div>'
        + '<div class="stats-top-champ-sub">' + c.games + ' parties &middot; <span class="' + (c.wr >= 50 ? 'good' : 'warn') + '">' + c.wr + '% WR</span></div></div>'
        + '<div class="stats-top-champ-kda mono">' + c.kda.toFixed(1) + ' <span>KDA</span></div></div>';
    }).join('') : '<div class="matchup-empty">Pas assez de parties sur un même champion dans cette file (min. 2).</div>';

    var maxRoleGames = Math.max.apply(null, q.roleStats.map(function (r) { return r.games; })) || 1;
    var roleHtml = q.roleStats.length ? q.roleStats.map(function (r) {
      var pct = Math.round((r.games / maxRoleGames) * 100);
      return '<div class="role-stat-row"><div class="role-stat-role">' + roleIcon(r.role) + (ROLE_LABEL[r.role] || r.role) + '</div>'
        + '<div class="role-stat-bar-track"><div class="role-stat-bar-fill" style="width:' + pct + '%"></div></div>'
        + '<div class="role-stat-games mono">' + r.games + ' parties</div>'
        + '<div class="role-stat-wr ' + (r.wr >= 50 ? 'good' : 'warn') + '">' + r.wr + '%</div></div>';
    }).join('') : '<div class="matchup-empty">Aucune partie dans cette file.</div>';

    function compareCard(label, you, rankAvg, unit, decimals) {
      var scale = Math.max(you, rankAvg) * 1.15 || 1;
      var diff = you - rankAvg;
      return '<div class="stats-compare-card"><div class="stats-compare-label">' + label + '</div>'
        + '<div class="stats-compare-row"><span class="stats-compare-name">Toi</span><div class="stats-compare-track"><div class="stats-compare-fill you" style="width:' + Math.round((you / scale) * 100) + '%"></div></div><span class="stats-compare-value mono">' + you.toFixed(decimals) + unit + '</span></div>'
        + '<div class="stats-compare-row"><span class="stats-compare-name">Rang</span><div class="stats-compare-track"><div class="stats-compare-fill rank" style="width:' + Math.round((rankAvg / scale) * 100) + '%"></div></div><span class="stats-compare-value mono">' + rankAvg.toFixed(decimals) + unit + '</span></div>'
        + '<div class="stats-compare-diff ' + (diff >= 0 ? 'good' : 'warn') + '">' + (diff >= 0 ? '+' : '') + diff.toFixed(decimals) + unit + ' vs moyenne</div></div>';
    }
    var sa = q.statsAvg;
    var compareHtml = q.matches.length ? [
      compareCard('CS / min', sa.csPerMin, rankAverages.csPerMin, '', 1),
      compareCard('Gold / min', sa.goldPerMin, rankAverages.goldPerMin, '', 0),
      compareCard('Dégâts / min', sa.dmgPerMin, rankAverages.dmgPerMin, '', 0),
      compareCard('Participation aux kills', sa.killParticipation, rankAverages.killParticipation, '%', 0),
    ].join('') : '<div class="matchup-empty">Pas assez de parties pour comparer.</div>';

    var maxWeekday = Math.max.apply(null, q.weekdayStats.map(function (d) { return d.games; })) || 1;
    var weekdayHtml = q.weekdayStats.map(function (d) {
      var pct = Math.round((d.games / maxWeekday) * 100);
      var labelClass = d.idx === 5 ? ' sam' : d.idx === 6 ? ' dim' : '';
      return '<div class="weekday-bar-col"><div class="weekday-bar-value mono">' + d.games + '</div>'
        + '<div class="weekday-bar-track"><div class="weekday-bar-fill ' + (d.games === 0 ? '' : (d.wr >= 50 ? 'good' : 'warn')) + '" style="height:' + pct + '%"></div></div>'
        + '<div class="weekday-bar-label' + labelClass + '">' + d.label + '</div></div>';
    }).join('');
    var hourlyHtml = q.hourlyStats.filter(function (h) { return h.games > 0; }).map(function (h) {
      return '<div class="hourly-row"><span class="hourly-time mono">' + (h.hour < 10 ? '0' : '') + h.hour + ':00</span>'
        + '<span class="hourly-badge ' + (h.wr >= 50 ? 'good' : 'warn') + '">' + h.games + ' jeux</span>'
        + '<span class="hourly-wr mono">' + h.wr + '%</span></div>';
    }).join('') || '<div class="matchup-empty">Pas assez de parties pour un historique horaire.</div>';

    wrap.innerHTML =
      '<div class="stats-section"><div class="stats-block-title">Meilleures perfs de la saison <span class="profile-section-note">classé par KDA, min. 2 parties</span></div><div class="stats-top-champs">' + topChampsHtml + '</div></div>'
      + '<div class="stats-section"><div class="stats-block-title">Répartition par rôle <span class="profile-section-note">' + q.matches.length + ' parties</span></div><div class="role-stats-list">' + roleHtml + '</div></div>'
      + '<div class="stats-section"><div class="stats-block-title">Toi vs moyenne du rang</div><div class="stats-compare-grid">' + compareHtml + '</div></div>'
      + '<div class="stats-section"><div class="stats-block-title-row"><div class="stats-block-title" style="margin-bottom:0">Modèles d\'activité</div></div>'
      + '<div class="activity-subtitle">En semaine</div><div class="weekday-chart">' + weekdayHtml + '</div>'
      + '<div class="activity-subtitle" style="margin-top:18px">Par heure</div><div class="hourly-list">' + hourlyHtml + '</div></div>'
      + devSectionsHtml();
    bindIconFallback(wrap);
  }

  function renderSidebarQueueBits(q) {
    var most = q.champions.slice(0, 4);
    document.getElementById('mostPlayedGrid').innerHTML = most.length ? most.map(function (c) {
      return '<div class="most-played-row"><span class="champ-portrait">' + champPortraitInner(c.champ) + '</span>'
        + '<span class="most-played-name">' + esc(c.champ) + '</span>'
        + '<span class="most-played-kda mono">' + c.kda.toFixed(1) + ' KDA</span>'
        + '<span class="most-played-wr ' + (c.wr >= 50 ? 'good' : 'warn') + '">' + c.wr + '%</span></div>';
    }).join('') : '<div class="matchup-empty">Aucune partie.</div>';
    bindIconFallback(document.getElementById('mostPlayedGrid'));

    var hasPlayedWith = q.playedWith.length > 0;
    document.getElementById('duoPartnerDivider').hidden = !hasPlayedWith;
    document.getElementById('duoPartnerTitle').hidden = !hasPlayedWith;
    document.getElementById('duoPartnerList').innerHTML = q.playedWith.map(function (p) {
      return '<div class="duo-partner-row"><div class="duo-partner-info"><div class="duo-partner-name">' + esc(p.riotId) + '</div>'
        + '<div class="duo-partner-meta">' + p.games + ' parties ensemble</div></div>'
        + '<div class="duo-partner-stats"><div class="duo-partner-wr ' + (p.wr >= 50 ? 'good' : 'warn') + '">' + p.wr + '%</div>'
        + '<div class="duo-partner-record">' + p.wins + 'V ' + (p.games - p.wins) + 'D</div></div></div>';
    }).join('');
  }

  function setProfileTab(tab) {
    currentTab = tab;
    document.getElementById('tabHistory').setAttribute('data-active', tab === 'history' ? 'true' : 'false');
    document.getElementById('tabChampions').setAttribute('data-active', tab === 'champions' ? 'true' : 'false');
    document.getElementById('tabStats').setAttribute('data-active', tab === 'stats' ? 'true' : 'false');
    document.getElementById('matchHistoryList').hidden = tab !== 'history';
    document.getElementById('championsTableWrap').hidden = tab !== 'champions';
    document.getElementById('statsTabWrap').hidden = tab !== 'stats';
    renderActiveTab();
  }

  function renderActiveTab() {
    var q = currentData.queues[currentQueue];
    if (currentTab === 'history') renderMatchList(q.matches);
    else if (currentTab === 'champions') renderChampionsTable(q.champions);
    else renderStatsTab(q, currentData.rankAverages);
  }

  function renderQueue(queueKey) {
    currentQueue = queueKey;
    document.querySelectorAll('.queue-filter-btn').forEach(function (btn) {
      btn.setAttribute('data-active', btn.dataset.queue === queueKey ? 'true' : 'false');
    });
    renderSidebarQueueBits(currentData.queues[queueKey]);
    renderActiveTab();
  }

  function renderProfile(data) {
    currentData = data;
    currentQueue = data.ranks.solo || !data.ranks.flex ? 'solo' : 'flex';
    currentTab = 'history';

    var primary = data.ranks.solo || data.ranks.flex;
    var secondary = data.ranks.solo ? data.ranks.flex : null;
    var wr = primary ? Math.round((primary.wins / Math.max(1, primary.wins + primary.losses)) * 100) : 0;

    var avatarHtml = data.profileIconId
      ? '<img class="league-icon-fallback" src="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/' + data.profileIconId + '.jpg" alt="">'
      : esc(initials(data.riotId));

    var sidebarHtml =
      '<div class="profile-id">' + esc(data.riotId.split('#')[0]) + ' <span class="tag">#' + esc(data.riotId.split('#')[1] || '') + '</span></div>'
      + (primary ? '<div class="rank-emblem-wrap"><img class="rank-emblem league-icon-fallback" src="' + primary.emblemUrl + '" alt=""></div>'
        + '<div class="rank-tier-name">' + tierLabel(primary.tier) + ' ' + primary.rank + '</div>'
        + '<div class="rank-lp mono">' + primary.leaguePoints + ' LP</div>'
        + '<div class="rank-ring-wrap">' + rankRingSvg(wr, wr >= 50) + '<div class="rank-ring-label"><div class="rank-ring-pct">' + wr + '%</div><div class="rank-ring-sub">' + primary.wins + 'V</div></div></div>'
        + '<div class="rank-record">' + primary.wins + 'V ' + primary.losses + 'D</div>'
        : '<div class="rank-tier-name" style="color:var(--text-faint)">Non classé</div>')
      + '<div class="sidebar-divider"></div>'
      + (secondary
        ? '<div class="flex-rank-row"><span class="sidebar-subtitle" style="margin-bottom:0">Classé flexible</span><span class="flex-rank-value">' + tierLabel(secondary.tier) + ' ' + secondary.rank + ' <span class="mono">' + secondary.leaguePoints + ' LP</span></span></div>'
        : '<div class="flex-rank-row"><span class="sidebar-subtitle" style="margin-bottom:0">Classé flexible</span><span class="flex-rank-value" style="color:var(--text-faint)">Non classé</span></div>')
      + '<div class="sidebar-divider"></div>'
      + '<div class="sidebar-subtitle">Le plus joué <span class="profile-section-note">' + QUEUE_LABEL[currentQueue] + '</span></div>'
      + '<div class="most-played-list" id="mostPlayedGrid"></div>'
      + '<button type="button" class="see-all-champs-btn" id="seeAllChampsBtn">Voir tous les champions →</button>'
      + '<div class="sidebar-divider" id="duoPartnerDivider" hidden></div>'
      + '<div class="sidebar-subtitle" id="duoPartnerTitle" hidden>Joué avec <span class="profile-section-note">derniers matchs</span></div>'
      + '<div class="duo-partner-list" id="duoPartnerList"></div>';

    var card = el('div', 'profile-card', '');
    card.style.setProperty('--tc', 'var(--gold)');
    card.innerHTML =
      '<span class="corner tl"></span><span class="corner tr"></span><span class="corner bl"></span><span class="corner br"></span>'
      + '<div class="profile-sidebar">' + sidebarHtml + '</div>'
      + '<div class="profile-main">'
      + '<div class="profile-main-tabs">'
      + '<button type="button" class="profile-main-tab" id="tabHistory" data-active="true">Historique</button>'
      + '<button type="button" class="profile-main-tab" id="tabChampions">Champions</button>'
      + '<button type="button" class="profile-main-tab" id="tabStats">Statistiques</button>'
      + '</div>'
      + '<div id="queueFilterBar" class="queue-filter-bar">'
      + '<button type="button" class="queue-filter-btn" data-queue="solo" data-active="' + (currentQueue === 'solo' ? 'true' : 'false') + '">Classé en solo/duo</button>'
      + '<button type="button" class="queue-filter-btn" data-queue="flex" data-active="' + (currentQueue === 'flex' ? 'true' : 'false') + '">Classé flexible</button>'
      + '<button type="button" class="queue-filter-btn" data-queue="aram" data-active="' + (currentQueue === 'aram' ? 'true' : 'false') + '">ARAM</button>'
      + '</div>'
      + '<div class="match-history-list" id="matchHistoryList"></div>'
      + '<div id="championsTableWrap" hidden></div>'
      + '<div id="statsTabWrap" hidden></div>'
      + '</div>';

    var header = el('div', 'player-header',
      '<div class="player-avatar">' + avatarHtml + '</div>'
      + '<div><div class="player-name-row"><span class="player-name">' + esc(data.riotId) + '</span></div>'
      + '<div class="player-meta">' + esc(data.region) + (data.summonerLevel ? ' &middot; Niveau ' + data.summonerLevel : '') + '</div></div>');

    results.innerHTML = '';
    results.appendChild(header);
    bindIconFallback(header);
    results.appendChild(card);
    bindIconFallback(card);

    document.getElementById('tabHistory').addEventListener('click', function () { setProfileTab('history'); });
    document.getElementById('tabChampions').addEventListener('click', function () { setProfileTab('champions'); });
    document.getElementById('tabStats').addEventListener('click', function () { setProfileTab('stats'); });
    document.getElementById('seeAllChampsBtn').addEventListener('click', function () { setProfileTab('champions'); });
    document.querySelectorAll('.queue-filter-btn').forEach(function (btn) {
      btn.addEventListener('click', function () { renderQueue(btn.dataset.queue); });
    });

    renderSidebarQueueBits(data.queues[currentQueue]);
    renderActiveTab();
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
