
(function () {
  // Straight port of the BrokenMeta League concept Artifact's rendering
  // (same HTML structure/CSS classes as league_profile's <style>, see
  // build_site.py), but every function here reads from the REAL worker
  // payload instead of a seeded mock generator -- no MATCH_HISTORY, no
  // fabricated duo data. Only the comms section stays illustrative (see
  // devSectionsHtml): Riot's API exposes no ping/chat data at any endpoint.
  var API = window.BM_LEAGUE_API;
  var I = window.BM_I18N_LEAGUE || {};
  var form = document.getElementById('leagueForm');
  var riotIdInput = document.getElementById('leagueRiotId');
  var regionSelect = document.getElementById('leagueRegion');
  var statusEl = document.getElementById('leagueStatus');
  var results = document.getElementById('leagueResults');
  if (!form || !API) return;

  // Favorited League profiles + recently searched ones -- same localStorage
  // pattern as FAVORITES_JS (TFT comps), separate keys so the two never mix,
  // rendered back out on /favoris/ by FAVORITES_JS itself.
  var LOL_FAV_KEY = 'bm_lol_favorites';
  var LOL_RECENT_KEY = 'bm_lol_recent';
  var LOL_RECENT_MAX = 8;
  var STAR_SVG = '<svg viewBox="0 0 24 24"><path d="M12 2.5l2.97 6.28 6.93.7-5.13 4.75 1.4 6.87L12 17.9l-6.17 3.2 1.4-6.87-5.13-4.75 6.93-.7z"/></svg>';

  function lolFavKey(riotId, region) { return region + '|' + riotId; }
  function loadLolFavorites() {
    try { return JSON.parse(localStorage.getItem(LOL_FAV_KEY)) || []; } catch (e) { return []; }
  }
  function saveLolFavorites(list) {
    try { localStorage.setItem(LOL_FAV_KEY, JSON.stringify(list)); } catch (e) {}
  }
  function isLolFavorite(riotId, region) {
    return loadLolFavorites().some(function (f) { return f.key === lolFavKey(riotId, region); });
  }
  function toggleLolFavorite(riotId, region) {
    var list = loadLolFavorites();
    var key = lolFavKey(riotId, region);
    var idx = list.findIndex(function (f) { return f.key === key; });
    if (idx === -1) {
      list.unshift({ key: key, riotId: riotId, region: region });
      if (window.gtag) gtag('event', 'favorite_add', { kind: 'league_profile' });
    } else {
      list.splice(idx, 1);
    }
    saveLolFavorites(list);
    return idx === -1; // now saved
  }
  function recordLolRecentSearch(riotId, region) {
    try {
      var key = lolFavKey(riotId, region);
      var list = JSON.parse(localStorage.getItem(LOL_RECENT_KEY)) || [];
      list = list.filter(function (f) { return f.key !== key; });
      list.unshift({ key: key, riotId: riotId, region: region });
      localStorage.setItem(LOL_RECENT_KEY, JSON.stringify(list.slice(0, LOL_RECENT_MAX)));
    } catch (e) {}
  }

  var ROLE_ICON = {
    top: '<path opacity="0.5" fill="#785a28" fill-rule="evenodd" d="M21,14H14v7h7V14Zm5-3V26L11.014,26l-4,4H30V7.016Z"/><polygon fill="#c8aa6e" points="4 4 4.003 28.045 9 23 9 9 23 9 28.045 4.003 4 4"/>',
    jungle: '<path fill="#c8aa6e" fill-rule="evenodd" d="M25,3c-2.128,3.3-5.147,6.851-6.966,11.469A42.373,42.373,0,0,1,20,20a27.7,27.7,0,0,1,1-3C21,12.023,22.856,8.277,25,3ZM13,20c-1.488-4.487-4.76-6.966-9-9,3.868,3.136,4.422,7.52,5,12l3.743,3.312C14.215,27.917,16.527,30.451,17,31c4.555-9.445-3.366-20.8-8-28C11.67,9.573,13.717,13.342,13,20Zm8,5a15.271,15.271,0,0,1,0,2l4-4c0.578-4.48,1.132-8.864,5-12C24.712,13.537,22.134,18.854,21,25Z"/>',
    mid: '<path opacity="0.5" fill="#785a28" fill-rule="evenodd" d="M30,12.968l-4.008,4L26,26H17l-4,4H30ZM16.979,8L21,4H4V20.977L8,17,8,8h8.981Z"/><polygon fill="#c8aa6e" points="25 4 4 25 4 30 9 30 30 9 30 4 25 4"/>',
    adc: '<path opacity="0.5" fill="#785a28" fill-rule="evenodd" d="M13,20h7V13H13v7ZM4,4V26.984l3.955-4L8,8,22.986,8l4-4H4Z"/><polygon fill="#c8aa6e" points="29.997 5.955 25 11 25 25 11 25 5.955 29.997 30 30 29.997 5.955"/>',
    support: '<path fill="#c8aa6e" fill-rule="evenodd" d="M26,13c3.535,0,8-4,8-4H23l-3,3,2,7,5-2-3-4h2ZM22,5L20.827,3H13.062L12,5l5,6Zm-5,9-1-1L13,28l4,3,4-3L18,13ZM11,9H0s4.465,4,8,4h2L7,17l5,2,2-7Z"/>',
  };
  var ROLE_LABEL = { top: 'Top', jungle: 'Jungle', mid: 'Mid', adc: 'ADC', support: 'Support' };
  var QUEUE_LABEL = { solo: I.queueSolo, flex: I.queueFlex, aram: I.queueAram };
  // Toutes les files existantes ne sont pas listées (URF, Nexus Blitz,
  // événements temporaires...) -- fallback générique plutôt que de
  // deviner un libellé pour une file absente de cette table.
  var QUEUE_ID_LABEL = { 400: I.queueNormalDraft, 420: I.queueSolo, 430: I.queueNormalBlind, 440: I.queueFlex, 450: I.queueAram, 700: I.queueClash };
  function liveGameQueueLabel(id) { return QUEUE_ID_LABEL[id] || I.queueCustom; }

  // Bandeau "en partie" -- Spectator-V5, vérifié à chaque recherche de
  // profil (voir index.ts). Même style de ligne que le scoreboard d'une
  // partie terminée (.scoreboard-row/-team) : équipe du joueur cherché
  // d'abord, classée "ally" même si Riot lui a attribué teamId 200 cette
  // partie-ci (le bleu/rouge alterne, ce qui compte c'est "son équipe").
  function buildLiveGameHtml(lg) {
    var selfP = lg.participants.filter(function (p) { return p.isSelf; })[0];
    var selfTeam = selfP ? selfP.teamId : 100;
    var otherP = lg.participants.filter(function (p) { return p.teamId !== selfTeam; })[0];
    var enemyTeam = otherP ? otherP.teamId : (selfTeam === 100 ? 200 : 100);
    var mins = Math.floor(lg.gameLengthSeconds / 60), secs = lg.gameLengthSeconds % 60;
    function teamRows(list) {
      return list.map(function (p) {
        var spellsHtml = p.spells.map(function (s) {
          return s.iconUrl ? '<img class="spell-icon league-icon-fallback" style="width:18px;height:18px" src="' + s.iconUrl + '" alt="" title="' + esc(s.name) + '" loading="lazy">' : '';
        }).join('');
        var runeHtml = p.runes.keystoneIconUrl ? '<img class="rune-icon small league-icon-fallback" src="' + p.runes.keystoneIconUrl + '" alt="" title="' + esc(p.runes.keystoneName) + '" loading="lazy">' : '';
        return '<div class="scoreboard-row' + (p.isSelf ? ' is-self' : '') + '">'
          + '<span class="champ-portrait">' + (p.championName ? champPortraitInner(p.championName) : '?') + '</span>'
          + '<span class="scoreboard-name">' + (p.isSelf ? esc(p.riotId || '') + ' ' + I.you : esc(p.riotId || '?')) + (p.bot ? ' <span class="profile-section-note">' + I.bot + '</span>' : '') + '</span>'
          + '<span class="scoreboard-items" style="gap:2px">' + spellsHtml + runeHtml + '</span>'
          + '</div>';
      }).join('');
    }
    function bansHtml(teamId) {
      var bans = (lg.bannedChampions || []).filter(function (b) { return b.teamId === teamId && b.championName; });
      if (!bans.length) return '<span class="live-game-bans-empty">' + I.noBans + '</span>';
      return bans.map(function (b) {
        return '<span class="champ-portrait live-game-ban"><span class="champ-portrait">' + champPortraitInner(b.championName) + '</span></span>';
      }).join('');
    }
    var hasBans = (lg.bannedChampions || []).some(function (b) { return b.championName; });
    return '<div class="live-game-header"><span class="live-dot"></span>' + esc(I.liveGameLabel) + ' — ' + esc(liveGameQueueLabel(lg.gameQueueConfigId)) + ' — ' + mins + ':' + (secs < 10 ? '0' : '') + secs + '</div>'
      + '<div class="scoreboard-grid">'
      + '<div class="scoreboard-team ally">' + teamRows(lg.participants.filter(function (p) { return p.teamId === selfTeam; })) + '</div>'
      + '<div class="scoreboard-team enemy">' + teamRows(lg.participants.filter(function (p) { return p.teamId !== selfTeam; })) + '</div>'
      + '</div>'
      + (hasBans ? '<div class="live-game-bans"><span class="live-game-bans-label">' + esc(I.bannedChampionsTitle) + '</span>'
        + '<div class="live-game-bans-row">' + bansHtml(selfTeam) + '</div>'
        + '<div class="live-game-bans-row">' + bansHtml(enemyTeam) + '</div>'
        + '</div>' : '');
  }

  function roleIcon(role, cls) { return '<svg class="' + (cls || 'champ-role-icon') + '" viewBox="0 0 34 34" xmlns="http://www.w3.org/2000/svg">' + (ROLE_ICON[role] || '') + '</svg>'; }
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }
  function initials(name) { return (name || '?').replace(/[^A-Za-z]/g, '').slice(0, 2).toUpperCase() || '?'; }
  function tierLabel(tier) { return tier ? tier.charAt(0) + tier.slice(1).toLowerCase() : ''; }

  // Real LP-over-time chart (see recordLpSnapshot in lol-worker/src/index.ts)
  // -- each point is a REAL rank recorded on a real lookup, no fabricated
  // history. A promotion resets the raw leaguePoints counter back near 0
  // even though it's a real gain, so points are scored on a continuous
  // tier+division ladder (100 "LP" per division, matching the real
  // promotion threshold) instead of plotting raw leaguePoints, which would
  // otherwise draw a promotion as a misleading drop.
  var LP_TIER_ORDER = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER'];
  var LP_DIV_ORDER = { IV: 0, III: 1, II: 2, I: 3 };
  function lpScore(p) {
    var tierIdx = LP_TIER_ORDER.indexOf((p.tier || '').toUpperCase());
    if (tierIdx < 0) tierIdx = 0;
    return tierIdx * 400 + (LP_DIV_ORDER[p.rank] || 0) * 100 + (p.leaguePoints || 0);
  }
  // Serialises a Bklit chart payload (see charts-ui/src/embed.tsx) into an
  // HTML attribute value; the markup around it stays as the fallback.
  function bmAttr(payload) { return JSON.stringify(payload).replace(/&/g, '&amp;').replace(/"/g, '&quot;'); }
  function buildRealLpChartSvg(points) {
    var w = 740, h = 170, padX = 10, padTop = 14, padBottom = 14;
    var scores = points.map(lpScore);
    var min = Math.min.apply(null, scores), max = Math.max.apply(null, scores);
    var range = (max - min) || 1;
    var n = points.length;
    var coords = scores.map(function (s, i) {
      var x = padX + (n === 1 ? 0 : (i / (n - 1)) * (w - 2 * padX));
      var y = h - padBottom - ((s - min) / range) * (h - padTop - padBottom);
      return [x, y];
    });
    var lineStr = coords.map(function (c) { return c[0].toFixed(1) + ',' + c[1].toFixed(1); }).join(' ');
    var last = coords[coords.length - 1];
    var svg = '<svg viewBox="0 0 740 170" class="lp-chart-svg"><line x1="8" y1="' + (h - padBottom) + '" x2="732" y2="' + (h - padBottom) + '" class="lp-chart-zero"/>'
      + '<polygon points="' + lineStr + ' ' + last[0].toFixed(1) + ',156 ' + coords[0][0].toFixed(1) + ',156" class="lp-chart-area"/>'
      + '<polyline points="' + lineStr + '" class="lp-chart-line" pathLength="1"/><circle cx="' + last[0].toFixed(1) + '" cy="' + last[1].toFixed(1) + '" r="4.5" class="lp-chart-dot"/></svg>';
    // Bklit AreaChart island (assets/js/bm-charts.js, loaded on demand below)
    // replaces this SVG once ready; the SVG stays as the no-JS / load-failure fallback.
    var payload = {
      aspectRatio: '3.4 / 1',
      series: [{ key: 'lp', label: 'LP', color: 'var(--magenta)' }],
      data: points.map(function (p, i) {
        var tier = (p.tier || '').charAt(0) + (p.tier || '').slice(1).toLowerCase();
        return { date: p.ts, lp: scores[i], tip: tier + ' ' + (p.rank || '') + ' - ' + (p.leaguePoints || 0) + ' LP' };
      })
    };
    return '<div class="bm-chart-mount" data-bm-chart="' + bmAttr(payload) + '">' + svg + '</div>';
  }

  // Loads the Bklit chart bundle once, on the first profile that has an LP
  // curve, then mounts every pending [data-bm-chart]. A MutationObserver
  // covers tab switches / re-renders, which rebuild this markup from scratch.
  var bmChartsState = 0;
  function hydrateBmCharts() {
    if (!document.querySelector('[data-bm-chart]:not([data-bm-mounted])')) return;
    if (window.bmCharts && window.bmCharts.mountAll) { window.bmCharts.mountAll(); return; }
    if (bmChartsState) return;
    bmChartsState = 1;
    var sc = document.createElement('script');
    sc.src = (window.BM_ROOT || '/') + 'assets/js/bm-charts.js?v=88e4bfd697';
    sc.async = true;
    document.head.appendChild(sc);
  }
  new MutationObserver(hydrateBmCharts).observe(document.body, { childList: true, subtree: true });

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
    if (!res.ok) {
      var err = new Error(data.error || ('HTTP ' + res.status));
      err.rateLimited = !!data.rateLimited || res.status === 429;
      err.retryAfter = data.retryAfter;
      throw err;
    }
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
    if (mins < 60) return mins + ' ' + I.minAbbr;
    var hours = Math.round(mins / 60);
    if (hours < 24) return hours + ' ' + I.hourAbbr;
    return Math.round(hours / 24) + ' ' + I.dayAbbr;
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
      + '<div class="match-result">' + (m.win ? I.win : I.loss) + '</div>'
      + '<div class="match-champ-block">' + roleIcon(m.role, 'champ-role-icon')
      + '<span class="champ-portrait-wrap"><span class="champ-portrait">' + champPortraitInner(m.champion) + '</span>'
      + (m.runes.keystoneIconUrl ? '<img class="champ-rune-badge league-icon-fallback" src="' + m.runes.keystoneIconUrl + '" alt="" title="' + esc(m.runes.keystoneName) + '" loading="lazy">' : '') + '</span>'
      + '<div><div class="match-champ-name">' + esc(m.champion) + '</div><div class="match-queue">' + QUEUE_LABEL[currentQueue] + '</div></div></div>'
      + buildLoadoutHtml(m)
      + '<div class="match-kda"><div class="match-kda-v mono">' + m.kills + '/' + m.deaths + '/' + m.assists + '</div><div class="match-kda-ratio">' + kdaRatio + ' KDA</div></div>'
      + '<div class="match-cs"><div class="mono">' + m.cs + ' CS</div><div class="match-cs-l">' + csPerMin + '/min</div></div>'
      + (m.dmgPerMin != null ? '<div class="match-cs match-dpm"><div class="mono">' + fmtInt(m.dmgPerMin) + '</div><div class="match-cs-l">' + esc(I.dpmLabel) + '</div></div>' : '')
      + '<div class="match-meta">' + m.durationMin.toFixed(0) + ' min<br>' + timeAgo(m.startedAt) + '</div>'
      + '<button type="button" class="match-expand-btn" id="matchExpandBtn' + idx + '" aria-expanded="false" aria-label="' + esc(I.viewMatchAria) + '">'
      + '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg></button>'
      + '</div>'
      + '<div class="match-detail" id="matchDetail' + idx + '" hidden></div>'
      + '</div>';
  }

  function renderScoreboardTeam(players, label, sideClass, durationMin) {
    return '<div class="scoreboard-team ' + sideClass + '"><div class="scoreboard-team-label">' + label + '</div>'
      + players.map(function (p) {
        var kdaText = p.isSelf ? '' : '<span class="scoreboard-kda mono">' + p.kills + '/' + p.deaths + '/' + p.assists + '</span>';
        var itemsHtml = p.items.map(function (it) {
          return it.iconUrl ? '<img class="item-slot league-icon-fallback" src="' + it.iconUrl + '" data-item-id="' + it.id + '" alt="" loading="lazy">' : '<span class="item-slot"></span>';
        }).join('');
        return '<div class="scoreboard-row' + (p.isSelf ? ' is-self' : '') + '">'
          + roleIcon(p.role, 'champ-role-icon') + '<span class="champ-portrait">' + champPortraitInner(p.champion) + '</span>'
          + '<span class="scoreboard-name">' + (p.isSelf ? esc(p.champion) + ' ' + I.you : esc(p.name)) + '</span>'
          + kdaText
          + '<span class="scoreboard-cs mono">' + p.cs + ' CS</span>'
          + (p.dmg != null && durationMin ? '<span class="scoreboard-cs scoreboard-dpm mono">' + fmtInt(p.dmg / durationMin) + ' ' + esc(I.dpmLabel) + '</span>' : '')
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
    if (m.deaths === 0) badges.push(I.badgeDeathless);
    if (m.kills >= 7) badges.push(I.badgeTripleKill);
    else if (m.kills >= 5) badges.push(I.badgeDoubleKill);
    if (m.assists >= 10) badges.push(I.badgeGoodSupport);

    function score(p) { return p.kills * 2 + p.assists - p.deaths * 1.5; }
    var mySelf = m.scoreboard.filter(function (p) { return p.isSelf; })[0];
    var ranked = m.scoreboard.slice().sort(function (a, b) { return score(b) - score(a); });
    var rank = ranked.indexOf(mySelf) + 1;
    var medal = rank <= 3 ? I.medalGold : rank <= 6 ? I.medalSilver : I.medalBronze;
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
        + renderScoreboardTeam(allies, I.allies, 'ally', m.durationMin)
        + renderScoreboardTeam(enemies, I.enemies, 'enemy', m.durationMin)
        + '</div>';
      detail.dataset.built = '1';
      bindIconFallback(detail);
    }
  }

  function renderMatchList(matches) {
    var list = document.getElementById('matchHistoryList');
    if (!matches.length) { list.innerHTML = '<div class="matchup-empty">' + esc(I.noRecentMatches) + '</div>'; return; }
    list.innerHTML = matches.map(matchRowHtml).join('');
    bindIconFallback(list);
    matches.forEach(function (m, idx) {
      document.getElementById('matchExpandBtn' + idx).addEventListener('click', function () { toggleMatchDetail(idx, m); });
    });
  }

  function champKda(c) { return c.kda.toFixed(1); }

  function renderChampionsTable(champions) {
    var wrap = document.getElementById('championsTableWrap');
    if (!champions.length) { wrap.innerHTML = '<div class="matchup-empty" style="padding:16px">' + esc(I.noChampionsPlayed) + '</div>'; return; }
    var hasDpm = champions.some(function (c) { return c.dpm != null; });
    var rows = champions.map(function (c) {
      return '<tr><td><div class="champ-cell"><span class="champ-portrait">' + champPortraitInner(c.champ) + '</span>' + esc(c.champ) + '</div></td>'
        + '<td class="num mono">' + c.games + '</td>'
        + '<td class="num"><span class="' + (c.wr >= 50 ? 'good' : 'warn') + '">' + c.wr + '%</span></td>'
        + '<td class="num mono">' + c.avgKills.toFixed(1) + ' / ' + c.avgDeaths.toFixed(1) + ' / ' + c.avgAssists.toFixed(1) + '</td>'
        + '<td class="num mono">' + champKda(c) + '</td>'
        + (hasDpm ? '<td class="num mono">' + (c.dpm != null ? fmtInt(c.dpm) : '-') + '</td>' : '') + '</tr>';
    }).join('');
    wrap.innerHTML = '<div class="champions-table-scroll"><table class="champions-table"><thead><tr><th>' + esc(I.thChampion) + '</th><th class="num">' + esc(I.thGames) + '</th><th class="num">' + esc(I.thWinrate) + '</th><th class="num">' + esc(I.thAvgKda) + '</th><th class="num">' + esc(I.thRatio) + '</th>' + (hasDpm ? '<th class="num">' + esc(I.thDpm) + '</th>' : '') + '</tr></thead><tbody>' + rows + '</tbody></table></div>';
    bindIconFallback(wrap);
  }

  // LP progress is now real (see recordLpSnapshot in lol-worker/src/
  // index.ts): every lookup appends one real point to that player's own
  // history in KV, so the chart grows as real visits happen. Comms stays a
  // clearly-labeled illustrative example below -- Riot's API doesn't
  // expose pings or chat messages at any endpoint, so there's no real data
  // to fall back to there at all.
  function lpSectionHtml() {
    var lpQueue = currentQueue === 'flex' ? 'flex' : 'solo';
    var points = (currentData.lpHistory && currentData.lpHistory[lpQueue]) || [];
    var queueLabel = lpQueue === 'flex' ? I.queueFlex : I.queueSolo;
    var inner;
    if (points.length >= 2) {
      inner = '<p class="profile-section-note" style="display:block;margin-bottom:10px">' + esc(I.lpRealNote).replace('{queue}', queueLabel).replace('{n}', points.length) + '</p>'
        + buildRealLpChartSvg(points);
    } else {
      var badge = '<div class="league-dev-badge"><span class="dot"></span>' + esc(points.length === 1 ? I.lpTrackingBadge : I.devBadge) + '</div>';
      inner = badge + '<p class="profile-section-note" style="display:block;margin-bottom:10px">' + esc(points.length === 1 ? I.lpOnePointNote : I.lpProgressNote) + '</p>';
    }
    return '<div class="stats-section"><div class="lp-chart-card">'
      + '<div class="stats-block-title" style="margin-bottom:8px">' + esc(I.lpProgressTitle) + '</div>' + inner + '</div></div>';
  }

  function fmtInt(n) {
    var s = String(Math.round(n)), out = '';
    for (var i = s.length; i > 0; i -= 3) out = s.slice(Math.max(0, i - 3), i) + (out ? String.fromCharCode(160) + out : '');
    return out;
  }
  // Measured rank averages (worker: rankExpected). Set at the start of each
  // stats-tab render; null when unranked / not sampled / ARAM.
  var currentRankMetrics = null, currentRankInfo = null;
  function cmpSub(you, key, mode) {
    var m = currentRankMetrics;
    if (!m || m[key] == null || !(m[key] > 0)) return '';
    var pct = ((you - m[key]) / m[key]) * 100;
    var tone = mode === 'neutral' ? 'dim' : ((mode === 'low' ? pct <= 0 : pct >= 0) ? 'good' : 'warn');
    return '<span class="' + tone + '">' + (pct >= 0 ? '+' : '') + Math.round(pct) + '%</span> ' + esc(I.kpiVsRank);
  }
  function joinSub(a, b) { return [a, b].filter(Boolean).join(' &middot; '); }
  function rankNoteHtml() {
    var r = currentRankInfo;
    if (!r) return '';
    var txt = r.approximate
      ? I.rankNoteApprox.replace('{tier}', tierLabel(r.tier)).replace('{used}', tierLabel(r.comparedTo))
      : I.rankNote.replace('{tier}', tierLabel(r.tier)).replace('{n}', fmtInt(r.sample));
    return '<p class="profile-section-note" style="display:block;margin:0 0 10px">' + esc(txt) + '</p>';
  }
  function kpiTile(label, value, sub, tone) {
    return '<div class="kpi-tile"><div class="kpi-label">' + esc(label) + '</div>'
      + '<div class="kpi-value mono' + (tone ? ' ' + tone : '') + '">' + value + '</div>'
      + (sub ? '<div class="kpi-sub">' + sub + '</div>' : '') + '</div>';
  }
  function kpiSection(title, note, tiles) {
    return '<div class="stats-section"><div class="stats-block-title">' + esc(title)
      + (note ? ' <span class="profile-section-note">' + esc(note) + '</span>' : '') + '</div>'
      + '<div class="kpi-grid">' + tiles.join('') + '</div></div>';
  }

  // Real pings (Match-V5 exposes every ping type; only chat text is missing).
  function realCommsHtml(q) {
    var pg = q && q.pings;
    if (!pg || !q.matches.length || !(pg.perGame > 0)) return null;
    var types = Object.keys(pg.byType).filter(function (k) { return pg.byType[k] > 0; })
      .sort(function (a, b) { return pg.byType[b] - pg.byType[a]; }).slice(0, 8);
    var top = pg.byType[types[0]] || 1;
    var rows = types.map(function (k) {
      return '<div class="comms-ping-row"><span class="comms-ping-label">' + esc((I.pingLabels && I.pingLabels[k]) || k) + '</span>'
        + '<div class="comms-ping-bar-track"><div class="comms-ping-bar-fill" style="width:' + Math.round((pg.byType[k] / top) * 100) + '%"></div></div>'
        + '<span class="comms-ping-value mono">' + pg.byType[k].toFixed(1) + '</span></div>';
    }).join('');
    return '<div class="stats-section"><div class="lp-chart-card">'
      + '<div class="stats-block-title" style="margin-bottom:8px">' + esc(I.commsRealTitle) + '</div>'
      + '<p class="profile-section-note" style="display:block;margin-bottom:10px">' + esc(I.commsRealNote).replace('{n}', q.matches.length) + '</p>'
      + '<div class="stats-comms-grid"><div class="stats-comms-msg"><div class="stats-comms-msg-value mono">' + pg.perGame.toFixed(1) + '</div>'
      + '<div class="stats-comms-msg-label">' + esc(I.pingsPerGame) + '</div>'
      + (cmpSub(pg.perGame, 'pingsPerGame', 'neutral') ? '<div class="stats-comms-msg-label" style="margin-top:4px">' + cmpSub(pg.perGame, 'pingsPerGame', 'neutral') + '</div>' : '')
      + '</div><div class="comms-ping-list">' + rows + '</div></div></div></div>';
  }

  function combatSectionHtml(q) {
    var c = q.combat;
    if (!c || !q.matches.length) return '';
    var per = '<span class="dim">' + esc(I.perGameUnit) + '</span>';
    return kpiSection(I.combatTitle, I.perGameNote, [
      kpiTile(I.kpiDpm, fmtInt(c.dpm), cmpSub(c.dpm, 'dpm', 'high'), 'accent'),
      kpiTile(I.kpiDmgTaken, fmtInt(c.damageTakenPerMin), cmpSub(c.damageTakenPerMin, 'damageTakenPerMin', 'neutral')),
      kpiTile(I.kpiMitigated, fmtInt(c.mitigatedPerMin), cmpSub(c.mitigatedPerMin, 'mitigatedPerMin', 'neutral')),
      kpiTile(I.kpiCc, c.ccTime.toFixed(0) + ' s', joinSub(per, cmpSub(c.ccTime, 'ccTime', 'high'))),
      kpiTile(I.kpiDead, c.deadPct.toFixed(1) + '%', cmpSub(c.deadPct, 'deadPct', 'low')),
      kpiTile(I.kpiHeal, fmtInt(c.healPerMin), cmpSub(c.healPerMin, 'healPerMin', 'neutral'))
    ]);
  }

  function visionSectionHtml(q) {
    if (currentQueue === 'aram' || !q.vision || !q.objectives || !q.matches.length) return '';
    var v = q.vision, o = q.objectives, per = '<span class="dim">' + esc(I.perGameUnit) + '</span>';
    return kpiSection(I.visionTitle, I.perGameNote, [
      kpiTile(I.kpiVisionMin, v.scorePerMin.toFixed(1), cmpSub(v.scorePerMin, 'visionPerMin', 'high'), 'accent'),
      kpiTile(I.kpiWardsPlaced, v.wardsPlaced.toFixed(1), joinSub(per, cmpSub(v.wardsPlaced, 'wardsPlaced', 'high'))),
      kpiTile(I.kpiWardsKilled, v.wardsKilled.toFixed(1), joinSub(per, cmpSub(v.wardsKilled, 'wardsKilled', 'high'))),
      kpiTile(I.kpiControlWards, v.controlWards.toFixed(1), joinSub(per, cmpSub(v.controlWards, 'controlWards', 'high'))),
      kpiTile(I.kpiTurrets, o.turrets.toFixed(1), joinSub(per, cmpSub(o.turrets, 'turrets', 'high'))),
      kpiTile(I.kpiPlates, o.plates.toFixed(1), joinSub(per, cmpSub(o.plates, 'plates', 'high'))),
      kpiTile(I.kpiDragons, o.dragons.toFixed(1), joinSub(per, cmpSub(o.dragons, 'dragons', 'high'))),
      kpiTile(I.kpiBarons, o.barons.toFixed(1), joinSub(per, cmpSub(o.barons, 'barons', 'high'))),
      kpiTile(I.kpiHeralds, o.heralds.toFixed(1), joinSub(per, cmpSub(o.heralds, 'heralds', 'high'))),
      kpiTile(I.kpiObjDmg, fmtInt(o.objDamagePerMin), cmpSub(o.objDamagePerMin, 'objDmgPerMin', 'high'))
    ]);
  }

  function recordsSectionHtml(q) {
    var r = q.records, f = q.form;
    if (!r || !q.matches.length) return '';
    var tiles = [];
    if (r.bestKda) tiles.push(kpiTile(I.kpiBestKda, r.bestKda.kills + '/' + r.bestKda.deaths + '/' + r.bestKda.assists, esc(r.bestKda.champion) + ' &middot; ' + r.bestKda.kda.toFixed(1) + ' KDA', r.bestKda.win ? 'good' : ''));
    if (r.mostKills) tiles.push(kpiTile(I.kpiMostKills, r.mostKills.kills, esc(r.mostKills.champion)));
    if (r.bestDpm) tiles.push(kpiTile(I.kpiBestDpm, fmtInt(r.bestDpm.dpm), esc(r.bestDpm.champion), 'accent'));
    tiles.push(kpiTile(I.kpiPentas, r.pentas, r.quadras + ' ' + esc(I.quadrasLabel)));
    tiles.push(kpiTile(I.kpiSpree, r.longestSpree));
    tiles.push(kpiTile(I.kpiFirstBlood, r.firstBloodPct + '%'));
    tiles.push(kpiTile(I.kpiSoloKills, r.soloKills));
    if (f) {
      tiles.push(kpiTile(f.streak.type === 'win' ? I.kpiStreakWin : I.kpiStreakLoss, f.streak.length, null, f.streak.type === 'win' ? 'good' : 'warn'));
      if (f.afterLoss) tiles.push(kpiTile(I.kpiAfterLoss, f.afterLoss.wr + '%', f.afterLoss.games + ' ' + esc(I.gamesUnitShort), f.afterLoss.wr >= 50 ? 'good' : 'warn'));
    }
    var bucketLabel = { short: I.kpiShort, mid: I.kpiMid, long: I.kpiLong };
    (q.durationStats || []).forEach(function (b) {
      tiles.push(kpiTile(bucketLabel[b.bucket], b.wr + '%', b.games + ' ' + esc(I.gamesUnitShort), b.wr >= 50 ? 'good' : 'warn'));
    });
    return kpiSection(I.recordsTitle, null, tiles);
  }

  function masterySectionHtml() {
    var list = currentData && currentData.mastery;
    if (!list || !list.length) return '';
    var top = list[0].points || 1;
    var rows = list.map(function (m) {
      return '<div class="mastery-row"><span class="champ-portrait">' + champPortraitInner(m.champ) + '</span>'
        + '<span class="mastery-name">' + esc(m.champ) + '</span>'
        + '<span class="mastery-level mono">' + esc(I.masteryLevel) + ' ' + m.level + '</span>'
        + '<div class="mastery-bar-track"><div class="mastery-bar-fill" style="width:' + Math.round((m.points / top) * 100) + '%"></div></div>'
        + '<span class="mastery-pts mono">' + fmtInt(m.points) + ' ' + esc(I.masteryPts) + '</span></div>';
    }).join('');
    return '<div class="stats-section"><div class="stats-block-title">' + esc(I.masteryTitle) + '</div><div class="mastery-list">' + rows + '</div></div>';
  }

  function devSectionsHtml() {
    var badge = '<div class="league-dev-badge"><span class="dot"></span>' + esc(I.devBadge) + '</div>';
    var perGame = I.lang === 'fr' ? ' / partie' : ' / game';
    var realComms = realCommsHtml(currentData.queues[currentQueue]);
    if (realComms) return lpSectionHtml() + realComms;
    return lpSectionHtml()
      + '<div class="stats-section"><div class="lp-chart-card">' + badge
      + '<div class="stats-block-title" style="margin-bottom:8px">' + esc(I.commsTitle) + '</div>'
      + '<p class="profile-section-note" style="display:block;margin-bottom:10px">' + esc(I.commsNote) + '</p>'
      + '<div class="stats-comms-grid"><div class="stats-comms-msg"><div class="stats-comms-msg-value mono">6.4</div><div class="stats-comms-msg-label">' + esc(I.messagesPerGame) + '</div></div>'
      + '<div class="comms-ping-list">'
      + '<div class="comms-ping-row"><span class="comms-ping-label">' + esc(I.pingOnMyWay) + '</span><div class="comms-ping-bar-track"><div class="comms-ping-bar-fill" style="width:70%"></div></div><span class="comms-ping-value mono">2.1' + perGame + '</span></div>'
      + '<div class="comms-ping-row"><span class="comms-ping-label">' + esc(I.pingMissing) + '</span><div class="comms-ping-bar-track"><div class="comms-ping-bar-fill" style="width:60%"></div></div><span class="comms-ping-value mono">1.8' + perGame + '</span></div>'
      + '<div class="comms-ping-row"><span class="comms-ping-label">' + esc(I.pingDanger) + '</span><div class="comms-ping-bar-track"><div class="comms-ping-bar-fill" style="width:40%"></div></div><span class="comms-ping-value mono">1.2' + perGame + '</span></div>'
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
    }).join('') : '<div class="matchup-empty">' + esc(I.notEnoughSameChamp) + '</div>';

    var maxRoleGames = Math.max.apply(null, q.roleStats.map(function (r) { return r.games; })) || 1;
    var roleHtml = q.roleStats.length ? q.roleStats.map(function (r) {
      var pct = Math.round((r.games / maxRoleGames) * 100);
      return '<div class="role-stat-row"><div class="role-stat-role">' + roleIcon(r.role) + (ROLE_LABEL[r.role] || r.role) + '</div>'
        + '<div class="role-stat-bar-track"><div class="role-stat-bar-fill" style="width:' + pct + '%"></div></div>'
        + '<div class="role-stat-games mono">' + r.games + ' ' + esc(I.partiesUnit) + '</div>'
        + '<div class="role-stat-wr ' + (r.wr >= 50 ? 'good' : 'warn') + '">' + r.wr + '%</div></div>';
    }).join('') : '<div class="matchup-empty">' + esc(I.noMatchesInQueue) + '</div>';

    function compareCard(label, you, rankAvg, unit, decimals) {
      var scale = Math.max(you, rankAvg) * 1.15 || 1;
      var diff = you - rankAvg;
      return '<div class="stats-compare-card"><div class="stats-compare-label">' + label + '</div>'
        + '<div class="stats-compare-row"><span class="stats-compare-name">' + esc(I.youLabel) + '</span><div class="stats-compare-track"><div class="stats-compare-fill you" style="width:' + Math.round((you / scale) * 100) + '%"></div></div><span class="stats-compare-value mono">' + you.toFixed(decimals) + unit + '</span></div>'
        + '<div class="stats-compare-row"><span class="stats-compare-name">' + esc(I.rankAvgLabel) + '</span><div class="stats-compare-track"><div class="stats-compare-fill rank" style="width:' + Math.round((rankAvg / scale) * 100) + '%"></div></div><span class="stats-compare-value mono">' + rankAvg.toFixed(decimals) + unit + '</span></div>'
        + '<div class="stats-compare-diff ' + (diff >= 0 ? 'good' : 'warn') + '">' + (diff >= 0 ? '+' : '') + diff.toFixed(decimals) + unit + ' ' + esc(I.vsAvg) + '</div></div>';
    }
    var sa = q.statsAvg;
    var rx = q.rankExpected ? q.rankExpected.metrics : null;
    var ra = rx ? { csPerMin: rx.csPerMin, goldPerMin: rx.goldPerMin, dmgPerMin: rx.dpm, killParticipation: rx.killParticipation } : rankAverages;
    currentRankInfo = q.rankExpected || null;
    currentRankMetrics = rx;
    var compareHtml = !q.matches.length ? '<div class="matchup-empty">' + esc(I.notEnoughToCompare) + '</div>'
      : !ra ? '<div class="matchup-empty">' + esc(I.noRankData) + '</div>'
      : [
      compareCard(I.csPerMin, sa.csPerMin, ra.csPerMin, '', 1),
      compareCard(I.goldPerMin, sa.goldPerMin, ra.goldPerMin, '', 0),
      compareCard(I.dmgPerMin, sa.dmgPerMin, ra.dmgPerMin, '', 0),
      compareCard(I.killParticipation, sa.killParticipation, ra.killParticipation, '%', 0),
    ].join('');

    // Radar (Bklit): shape of the profile vs the rank average at a glance.
    // Each metric is normalised to its own max(you, rank avg) so the axes are
    // comparable; the exact numbers stay in the four cards below.
    var radarHtml = '';
    if (q.matches.length && ra) {
      var radarMetrics = [
        { key: 'cs', label: 'CS/min', you: sa.csPerMin, avg: ra.csPerMin },
        { key: 'gold', label: '\u00a0\u00a0Gold/min', you: sa.goldPerMin, avg: ra.goldPerMin },
        { key: 'dmg', label: 'Dmg/min', you: sa.dmgPerMin, avg: ra.dmgPerMin },
        { key: 'kp', label: 'KP', you: sa.killParticipation, avg: ra.killParticipation }
      ];
      if (rx && q.vision && currentQueue !== 'aram') radarMetrics.push({ key: 'vision', label: 'Vision/min', you: q.vision.scorePerMin, avg: rx.visionPerMin });
      var youVals = {}, avgVals = {};
      radarMetrics.forEach(function (m) {
        var top = Math.max(m.you, m.avg) || 1;
        youVals[m.key] = Math.round((m.you / top) * 100);
        avgVals[m.key] = Math.round((m.avg / top) * 100);
      });
      radarHtml = '<div class="stats-radar" data-bm-chart="' + bmAttr({
        type: 'radar', size: 320,
        metrics: radarMetrics.map(function (m) { return { key: m.key, label: m.label }; }),
        radar: [{ label: I.youLabel, color: 'var(--magenta)', values: youVals }, { label: I.rankAvgLabel, color: 'var(--cream)', values: avgVals }]
      }) + '"></div>';
    }

    var maxWeekday = Math.max.apply(null, q.weekdayStats.map(function (d) { return d.games; })) || 1;
    var weekdayHtml = q.weekdayStats.map(function (d) {
      var pct = Math.round((d.games / maxWeekday) * 100);
      var labelClass = d.idx === 5 ? ' sam' : d.idx === 6 ? ' dim' : '';
      // d.label vient du worker, toujours en français (WEEKDAY_LABELS y est
      // codé en dur) -- recalculé ici depuis l'index numérique plutôt que
      // d'ajouter un paramètre de langue à l'API pour un simple libellé.
      return '<div class="weekday-bar-col"><div class="weekday-bar-value mono">' + d.games + '</div>'
        + '<div class="weekday-bar-track"><div class="weekday-bar-fill ' + (d.games === 0 ? '' : (d.wr >= 50 ? 'good' : 'warn')) + '" style="height:' + pct + '%"></div></div>'
        + '<div class="weekday-bar-label' + labelClass + '">' + esc(I.weekdayLabels[d.idx]) + '</div></div>';
    }).join('');
    var weekdayPayload = {
      type: 'bar', aspectRatio: '2.6 / 1',
      series: [{ key: 'good', label: 'WR >= 50%', color: 'var(--good)' }, { key: 'warn', label: 'WR < 50%', color: 'var(--warn)' }],
      data: q.weekdayStats.map(function (d) {
        return { name: I.weekdayLabels[d.idx], good: d.wr >= 50 ? d.games : 0, warn: d.wr >= 50 ? 0 : d.games, tip: d.games + ' ' + I.gamesUnit + ' - ' + d.wr + '%' };
      })
    };
    var hourlyHtml = q.hourlyStats.filter(function (h) { return h.games > 0; }).map(function (h) {
      return '<div class="hourly-row"><span class="hourly-time mono">' + (h.hour < 10 ? '0' : '') + h.hour + ':00</span>'
        + '<span class="hourly-badge ' + (h.wr >= 50 ? 'good' : 'warn') + '">' + h.games + ' ' + esc(I.gamesUnit) + '</span>'
        + '<span class="hourly-wr mono">' + h.wr + '%</span></div>';
    }).join('') || '<div class="matchup-empty">' + esc(I.notEnoughHourly) + '</div>';

    wrap.innerHTML =
      '<div class="stats-section"><div class="stats-block-title">' + esc(I.seasonBestTitle) + ' <span class="profile-section-note">' + esc(I.seasonBestSub) + '</span></div><div class="stats-top-champs">' + topChampsHtml + '</div></div>'
      + masterySectionHtml()
      + '<div class="stats-section"><div class="stats-block-title">' + esc(I.roleDistTitle) + ' <span class="profile-section-note">' + q.matches.length + ' ' + esc(I.partiesUnit) + '</span></div><div class="role-stats-list">' + roleHtml + '</div></div>'
      + '<div class="stats-section"><div class="stats-block-title">' + esc(I.youVsRankTitle) + '</div>' + rankNoteHtml() + radarHtml + '<div class="stats-compare-grid">' + compareHtml + '</div></div>'
      + combatSectionHtml(q) + visionSectionHtml(q) + recordsSectionHtml(q)
      + '<div class="stats-section"><div class="stats-block-title-row"><div class="stats-block-title" style="margin-bottom:0">' + esc(I.activityTitle) + '</div></div>'
      + '<div class="activity-subtitle">' + esc(I.weekdaysLabel) + '</div><div class="weekday-chart" data-bm-chart="' + bmAttr(weekdayPayload) + '">' + weekdayHtml + '</div>'
      + '<div class="activity-subtitle" style="margin-top:18px">' + esc(I.hourlyLabel) + '</div><div class="hourly-list">' + hourlyHtml + '</div></div>'
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
    }).join('') : '<div class="matchup-empty">' + esc(I.noRecentGame) + '</div>';
    bindIconFallback(document.getElementById('mostPlayedGrid'));

    var hasPlayedWith = q.playedWith.length > 0;
    document.getElementById('duoPartnerDivider').hidden = !hasPlayedWith;
    document.getElementById('duoPartnerTitle').hidden = !hasPlayedWith;
    document.getElementById('duoPartnerList').innerHTML = q.playedWith.map(function (p) {
      return '<div class="duo-partner-row"><div class="duo-partner-info"><div class="duo-partner-name">' + esc(p.riotId) + '</div>'
        + '<div class="duo-partner-meta">' + p.games + ' ' + esc(I.gamesTogether) + '</div></div>'
        + '<div class="duo-partner-stats"><div class="duo-partner-wr ' + (p.wr >= 50 ? 'good' : 'warn') + '">' + p.wr + '%</div>'
        + '<div class="duo-partner-record">' + p.wins + I.winAbbr + ' ' + (p.games - p.wins) + I.lossAbbr + '</div></div></div>';
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
        + '<div class="rank-ring-wrap" data-bm-chart="' + bmAttr({ type: 'gauge', value: wr, suffix: '%', label: primary.wins + I.winAbbr, color: wr >= 50 ? 'var(--good)' : 'var(--warn)', size: 112 }) + '">' + rankRingSvg(wr, wr >= 50) + '<div class="rank-ring-label"><div class="rank-ring-pct">' + wr + '%</div><div class="rank-ring-sub">' + primary.wins + I.winAbbr + '</div></div></div>'
        + '<div class="rank-record">' + primary.wins + I.winAbbr + ' ' + primary.losses + I.lossAbbr + '</div>'
        : '<div class="rank-tier-name" style="color:var(--text-faint)">' + esc(I.unranked) + '</div>')
      + '<div class="sidebar-divider"></div>'
      + (secondary
        ? '<div class="flex-rank-row"><span class="sidebar-subtitle" style="margin-bottom:0">' + esc(I.queueFlex) + '</span><span class="flex-rank-value">' + tierLabel(secondary.tier) + ' ' + secondary.rank + ' <span class="mono">' + secondary.leaguePoints + ' LP</span></span></div>'
        : '<div class="flex-rank-row"><span class="sidebar-subtitle" style="margin-bottom:0">' + esc(I.queueFlex) + '</span><span class="flex-rank-value" style="color:var(--text-faint)">' + esc(I.unranked) + '</span></div>')
      + '<div class="sidebar-divider"></div>'
      + '<div class="sidebar-subtitle">' + esc(I.mostPlayed) + ' <span class="profile-section-note">' + QUEUE_LABEL[currentQueue] + '</span></div>'
      + '<div class="most-played-list" id="mostPlayedGrid"></div>'
      + '<button type="button" class="see-all-champs-btn" id="seeAllChampsBtn">' + esc(I.seeAllChamps) + '</button>'
      + '<div class="sidebar-divider" id="duoPartnerDivider" hidden></div>'
      + '<div class="sidebar-subtitle" id="duoPartnerTitle" hidden>' + esc(I.playedWith) + ' <span class="profile-section-note">' + esc(I.recentMatches) + '</span></div>'
      + '<div class="duo-partner-list" id="duoPartnerList"></div>';

    var card = el('div', 'profile-card', '');
    card.style.setProperty('--tc', 'var(--gold)');
    card.innerHTML =
      '<span class="corner tl"></span><span class="corner tr"></span><span class="corner bl"></span><span class="corner br"></span>'
      + '<div class="profile-sidebar">' + sidebarHtml + '</div>'
      + '<div class="profile-main">'
      + '<div class="profile-main-tabs">'
      + '<button type="button" class="profile-main-tab" id="tabHistory" data-active="true">' + esc(I.tabHistory) + '</button>'
      + '<button type="button" class="profile-main-tab" id="tabChampions">' + esc(I.tabChampions) + '</button>'
      + '<button type="button" class="profile-main-tab" id="tabStats">' + esc(I.tabStats) + '</button>'
      + '</div>'
      + '<div id="queueFilterBar" class="queue-filter-bar">'
      + '<button type="button" class="queue-filter-btn" data-queue="solo" data-active="' + (currentQueue === 'solo' ? 'true' : 'false') + '">' + esc(I.queueSolo) + '</button>'
      + '<button type="button" class="queue-filter-btn" data-queue="flex" data-active="' + (currentQueue === 'flex' ? 'true' : 'false') + '">' + esc(I.queueFlex) + '</button>'
      + '<button type="button" class="queue-filter-btn" data-queue="aram" data-active="' + (currentQueue === 'aram' ? 'true' : 'false') + '">' + esc(I.queueAram) + '</button>'
      + '</div>'
      + '<div class="match-history-list" id="matchHistoryList"></div>'
      + '<div id="championsTableWrap" hidden></div>'
      + '<div id="statsTabWrap" hidden></div>'
      + '</div>';

    var isFav = isLolFavorite(data.riotId, data.region);
    var header = el('div', 'player-header',
      '<div class="player-avatar">' + avatarHtml + '</div>'
      + '<div><div class="player-name-row"><span class="player-name">' + esc(data.riotId) + '</span>'
      + '<button type="button" class="fav-btn inline" id="lolFavBtn" aria-pressed="' + (isFav ? 'true' : 'false') + '" '
      + 'title="' + esc(isFav ? I.favRemove : I.favAdd) + '" aria-label="' + esc(isFav ? I.favRemove : I.favAdd) + '">' + STAR_SVG + '</button></div>'
      + '<div class="lol-fav-hint" id="lolFavHint"' + (isFav ? ' hidden' : '') + '>' + esc(I.favHint) + '</div>'
      + '<div class="player-meta">' + esc(data.region) + (data.summonerLevel ? ' &middot; ' + esc(I.level) + ' ' + data.summonerLevel : '') + '</div></div>');

    results.innerHTML = '';
    results.appendChild(header);
    bindIconFallback(header);
    var lolFavBtn = document.getElementById('lolFavBtn');
    if (lolFavBtn) {
      lolFavBtn.addEventListener('click', function () {
        var nowSaved = toggleLolFavorite(data.riotId, data.region);
        lolFavBtn.setAttribute('aria-pressed', nowSaved ? 'true' : 'false');
        var label = nowSaved ? I.favRemove : I.favAdd;
        lolFavBtn.title = label;
        lolFavBtn.setAttribute('aria-label', label);
        var hint = document.getElementById('lolFavHint');
        if (hint) hint.hidden = nowSaved;
      });
    }
    if (data.liveGame) {
      var liveEl = el('div', 'live-game-banner', buildLiveGameHtml(data.liveGame));
      results.appendChild(liveEl);
      bindIconFallback(liveEl);
    }
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

  // The Riot dev key allows 100 requests / 2 min for ALL visitors combined
  // (one profile costs ~36), so the worker caches profiles for 2 min and this
  // cooldown only stops double-clicks (short) or backs off after a rate-limit
  // answer (long). Kept in localStorage so a page refresh doesn't skip it.
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
      submitBtn.textContent = I.cooldownLabel.replace('{s}', left);
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

  // Skeleton shaped like the profile card, shown while the worker answers
  // (2-10 s, longer when Riot is rate-limited).
  function skeletonProfileHtml() {
    var rows = '';
    for (var i = 0; i < 6; i++) {
      rows += '<div class="skel-row"><span class="skel" style="width:58px;height:14px"></span><span class="skel skel-circle" style="width:38px;height:38px"></span>'
        + '<span class="skel" style="flex:1;height:12px"></span><span class="skel" style="width:64px;height:12px"></span></div>';
    }
    return '<div class="profile-card skel-card" aria-hidden="true">'
      + '<div class="profile-sidebar"><span class="skel" style="width:120px;height:16px;align-self:flex-start;margin-bottom:14px"></span>'
      + '<span class="skel skel-circle" style="width:88px;height:88px;margin-bottom:12px"></span>'
      + '<span class="skel" style="width:110px;height:14px;margin-bottom:8px"></span><span class="skel" style="width:70px;height:12px;margin-bottom:16px"></span>'
      + '<span class="skel skel-circle" style="width:80px;height:80px"></span></div>'
      + '<div class="profile-main"><div class="skel-tabs"><span class="skel" style="width:90px;height:28px"></span><span class="skel" style="width:90px;height:28px"></span><span class="skel" style="width:90px;height:28px"></span></div>' + rows + '</div></div>';
  }

  async function runProfile(riotId, region) {
    setStatus(I.loading, false);
    results.innerHTML = skeletonProfileHtml();
    try {
      await ddragonReady;
      var data = await fetchJson(API + '/profile?riotId=' + encodeURIComponent(riotId) + '&region=' + encodeURIComponent(region));
      setStatus(null);
      results.innerHTML = '';
      setUrl({ riotId: riotId, region: region });
      renderProfile(data);
      recordLolRecentSearch(data.riotId, data.region);
      var ageMin = data.generatedAt ? Math.round((Date.now() - data.generatedAt) / 60000) : 0;
      if (ageMin >= 3) setStatus(I.staleNote.replace('{min}', ageMin), false);
      startCooldown(8);
      if (window.gtag) gtag('event', 'league_lookup', { region: region, success: true });
    } catch (e) {
      results.innerHTML = '';
      setStatus(e.message || String(e), true);
      if (e && e.rateLimited) startCooldown(e.retryAfter || 75);
      if (window.gtag) gtag('event', 'league_lookup', { region: region, success: false });
    }
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (cooldownLeft() > 0) return;
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
