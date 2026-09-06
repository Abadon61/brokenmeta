"""Static-site generator for the real brokenmeta.gg production site.

Reads the exact same pipeline output the Claude Artifact prototype uses
(data/output/*.json) and renders real, crawlable, per-page-SEO static HTML
into site_build/dist/ -- one page per comp, one per champion, plus list
pages, sitemap.xml and robots.txt. No fabricated content: every number here
traces back to the same real Riot Match-V1 data as the Artifact version.

Run from anywhere:  py site_build/build_site.py
Output:              site_build/dist/  (upload this folder's CONTENTS to
                      Hostinger's public_html/)
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import requests
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
sys.path.insert(0, str(PROJECT / "src"))
from tft_tracker.champion_images import (  # noqa: E402
    build_augment_data, build_champion_image_map, build_family_docs, build_full_item_catalog, build_item_image_map,
    build_team_planner_codes, build_trait_data, classify_item_offense,
)

OUT = PROJECT / "data" / "output"
DIST = ROOT / "dist"
SET_MUTATOR = "TFTSet18"
# Single source of truth for the human-facing set name used in SEO-critical
# spots (titles, on-page kickers, intro copy): "TFT" is what players actually
# type into Google (confirmed via Google Trends: "tft" outweighs "comp tft"
# ~15:1 in France), so this is deliberately the abbreviation, not "Teamfight
# Tactics Set 18". Same string in FR and EN -- real players use it unchanged
# in both languages. Bump this (and SET_MUTATOR) together when Set 19 ships.
SET_LABEL = "TFT Set 18"
BASE_URL = "https://brokenmeta.gg/"

# Was 10 (matching the Artifact's export_data.py), same as everywhere real
# TFT trackers set a low floor -- but with the raw match cache now spanning
# 20k+ real ranked games instead of ~4-5k, a 10-game comp can cross that bar
# on pure variance (TFT placement has high game-to-game swing). Raised to
# 100 on 2026-09-06 after checking the actual distribution: ~537 comps
# qualify at 10 vs ~158 at 100, and every comp at 100+ games has a real
# statistical base instead of a lucky handful of games. The Artifact
# (export_data.py) still uses 10 -- deliberately diverged, not kept in sync,
# since it doesn't have this site's real match volume to support a higher bar.
MIN_PLAY_COUNT = 100
MAX_AVG_PLACEMENT = 6.00
MIN_CORE_BOARD_SIZE = 7

TIER_VAR = {"S": "var(--red)", "A": "var(--gold)", "B": "var(--teal)", "C": "var(--gray)", "?": "var(--gray)"}

# Progressive enhancement only -- every comp is already in the static HTML
# (crawlable, works with JS off); Région/Rang are real separate pages, but
# Type (Reroll/Fast/Slow) and search don't need their own data slice, just
# combined show/hide among rows already rendered on the current page.
# Ported from the Artifact's matchesSearch()/render() filter chain, with
# each row's search haystack precomputed server-side into data-search
# (see build_row_vm's "search_blob") instead of scraping DOM text.
#
# Two different page shapes use this: list_page.html (a single flat #rows
# list, plus the Type chips) and overview.html (the homepage/scope preview,
# grouped into one [data-tier-group] block per tier, no Type chips there).
# Selecting every ".comp-row" on the page (not scoped to #rows) covers
# both; group visibility is handled separately so an emptied-out preview
# group (e.g. "Tier S" has zero matches) disappears header and all, not
# just its rows. The two empty-state messages ("no comp matches this
# filter" vs "...this search") come from window.BM_I18N_EMPTY_* set by
# each template's own <script>, so this one shared file needs no
# per-language copy, and works whether or not BM_I18N_EMPTY_FILTER is
# defined at all (overview.html only ever needs the search one, since it
# has no Type filter to produce a filter-only empty state).
LIST_FILTERS_JS = """
(function () {
  var rows = Array.prototype.slice.call(document.querySelectorAll('.comp-row'));
  if (!rows.length) return;
  var groups = Array.prototype.slice.call(document.querySelectorAll('[data-tier-group]'));
  var bar = document.getElementById('typeFilterBar');
  var searchInput = document.getElementById('compSearch');
  var emptyState = document.getElementById('emptyState');
  var activeType = 'ALL';

  function applyFilters() {
    var q = (searchInput ? searchInput.value.trim().toLowerCase() : '');
    var visible = 0;
    rows.forEach(function (row) {
      var typeOk = activeType === 'ALL' || row.dataset.playstyleCat === activeType;
      var searchOk = !q || (row.dataset.search || '').indexOf(q) !== -1;
      var show = typeOk && searchOk;
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    groups.forEach(function (group) {
      var groupVisible = group.querySelectorAll('.comp-row').length
        && Array.prototype.some.call(group.querySelectorAll('.comp-row'), function (r) { return r.style.display !== 'none'; });
      group.style.display = groupVisible ? '' : 'none';
    });
    if (emptyState) {
      emptyState.hidden = visible !== 0;
      if (visible === 0) {
        emptyState.textContent = q
          ? (window.BM_I18N_EMPTY_SEARCH || '').replace('__Q__', searchInput.value.trim())
          : (window.BM_I18N_EMPTY_FILTER || '');
      }
    }
  }

  if (bar) {
    bar.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-filter-type]');
      if (!btn) return;
      [].forEach.call(bar.querySelectorAll('[data-filter-type]'), function (b) { b.dataset.active = String(b === btn); });
      activeType = btn.dataset.filterType;
      applyFilters();
    });
  }
  if (searchInput) searchInput.addEventListener('input', applyFilters);
})();
"""
STAR_SVG = '<svg viewBox="0 0 24 24"><path d="M12 2.5l2.97 6.28 6.93.7-5.13 4.75 1.4 6.87L12 17.9l-6.17 3.2 1.4-6.87-5.13-4.75 6.93-.7z"/></svg>'
COPY_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"></rect>'
            '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>')

# Progressive enhancement, same pattern as TYPE_FILTER_JS -- every comp's
# planner_code is already baked into the button's data-code attribute at
# build time (no client-side lookup table needed, unlike the Artifact).
COPY_COMP_JS = """
(function () {
  var CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
  async function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }
  document.querySelectorAll('.copy-comp-btn').forEach(function (btn) {
    var originalHTML = btn.innerHTML;
    var originalTitle = btn.title;
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      copyToClipboard(btn.dataset.code).then(function () {
        btn.dataset.copied = 'true';
        btn.innerHTML = CHECK_SVG;
        btn.title = btn.dataset.copiedTitle;
      }, function () {
        btn.title = btn.dataset.failedTitle;
      });
      setTimeout(function () {
        btn.dataset.copied = 'false';
        btn.innerHTML = originalHTML;
        btn.title = originalTitle;
      }, 2200);
    });
  });
})();
"""

# Progressive enhancement, ported from the Artifact's wireChampionIcons():
# any ".champ-link-icon" (unit portraits, item-combo headers, board-variant
# icons, ...) shows a real stat tooltip on hover and jumps to that
# champion's page on click. Unlike the Artifact (one big embedded data
# object), stats are fetched once from assets/data/champions.json -- see
# main()'s champion_tooltip_data write-out -- and the click target is
# baked into each icon's own data-champ-href at build time, so this file
# needs no per-page templating. FR/EN labels are embedded directly here
# (not routed through the Jinja `t()` system) since this one static file
# is shared, unchanged, across every language's pages.
#
# Event DELEGATION on `document` (not per-icon listeners) on purpose: every
# other page's icons exist at load time, but MetaScope (see metascope.js)
# renders its whole profile/analysis view from a live API response AFTER
# this script has already run -- delegation means those icons get the same
# hover/click behavior for free, no re-init call needed from that script.
CHAMP_ICON_JS = """
(function () {
  var LABELS = {
    fr: {playrate: 'Popularité', avgplacement: 'Placement moyen', avgstar: 'Étoile moyenne',
         items: function (s) { return 'Objets fréquents : ' + s; }},
    en: {playrate: 'Play rate', avgplacement: 'Avg placement', avgstar: 'Avg star',
         items: function (s) { return 'Common items: ' + s; }}
  };
  var L = LABELS[document.documentElement.lang === 'en' ? 'en' : 'fr'];
  var tooltip = document.getElementById('tooltip');
  var champData = null;
  fetch((window.BM_ROOT || '') + 'assets/data/champions.json').then(function (r) { return r.json(); }).then(function (d) { champData = d; }).catch(function () {});

  function showTooltip(icon, e) {
    if (!champData || !tooltip) return;
    var d = champData[icon.dataset.champSlug];
    if (!d) return;
    var traitsHtml = (d.traits || []).map(function (t) {
      return '<span class="tt-trait-chip"><img src="' + (window.BM_ROOT || '') + 'assets/traits/' + t.slug + '.png" alt="">' + t.name + '</span>';
    }).join('');
    tooltip.innerHTML = '<div class="tt-name">' + d.name + '</div>'
      + (traitsHtml ? '<div class="tt-traits">' + traitsHtml + '</div>' : '')
      + '<div class="tt-row"><span>' + L.playrate + '</span><b class="nums">' + d.pick_rate_pct + '</b></div>'
      + '<div class="tt-row"><span>' + L.avgplacement + '</span><b class="nums">' + d.avg_placement.toFixed(2) + '</b></div>'
      + '<div class="tt-row"><span>' + L.avgstar + '</span><b class="nums">' + d.avg_star_level.toFixed(1) + '\\u2605</b></div>'
      + (d.top_items && d.top_items.length ? '<div class="tt-items">' + L.items(d.top_items.join(', ')) + '</div>' : '');
    tooltip.dataset.visible = 'true';
    moveTooltip(e);
  }
  function moveTooltip(e) {
    if (!tooltip) return;
    var pad = 14, x = e.clientX + pad, y = e.clientY + pad;
    if (x + 190 > window.innerWidth) x = e.clientX - 190 - pad;
    if (y + 130 > window.innerHeight) y = e.clientY - 130 - pad;
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }
  function hideTooltip() { if (tooltip) tooltip.dataset.visible = 'false'; }

  document.addEventListener('mouseover', function (e) {
    var icon = e.target.closest('.champ-link-icon');
    if (icon) showTooltip(icon, e);
  });
  document.addEventListener('mousemove', function (e) {
    if (e.target.closest('.champ-link-icon')) moveTooltip(e);
  });
  document.addEventListener('mouseout', function (e) {
    if (e.target.closest('.champ-link-icon')) hideTooltip();
  });
  document.addEventListener('click', function (e) {
    var icon = e.target.closest('.champ-link-icon');
    if (!icon) return;
    e.preventDefault();
    e.stopPropagation();
    var href = icon.dataset.champHref;
    if (href) location.href = href;
  });
})();
"""

# Same tooltip mechanism as CHAMP_ICON_JS above (shared #tooltip div, one
# lazy-fetched static JSON), for the Glossary's item icon grid: hovering an
# item shows its real crafting components (the ".item-icon"/".item-icon-sm"
# used everywhere else on the site already have a native `title` tooltip for
# this, deliberately not reused here so this one richer version -- icons,
# not just names -- doesn't fight the plain-text one on the exact same class).
GLOSSARY_ITEM_JS = """
(function () {
  var tooltip = document.getElementById('tooltip');
  var itemData = null;
  fetch((window.BM_ROOT || '') + 'assets/data/glossary-items.json').then(function (r) { return r.json(); }).then(function (d) { itemData = d; }).catch(function () {});

  function showTooltip(icon, e) {
    if (!itemData || !tooltip) return;
    var d = itemData[icon.dataset.itemSlug];
    if (!d) return;
    var compHtml = (d.composition || []).map(function (c) {
      return '<span class="tt-trait-chip"><img src="' + (window.BM_ROOT || '') + 'assets/items/' + c.slug + '.png" alt="">' + c.name + '</span>';
    }).join('');
    tooltip.innerHTML = '<div class="tt-name">' + d.name + '</div>'
      + (compHtml ? '<div class="tt-traits">' + compHtml + '</div>' : '');
    tooltip.dataset.visible = 'true';
    moveTooltip(e);
  }
  function moveTooltip(e) {
    if (!tooltip) return;
    var pad = 14, x = e.clientX + pad, y = e.clientY + pad;
    if (x + 190 > window.innerWidth) x = e.clientX - 190 - pad;
    if (y + 130 > window.innerHeight) y = e.clientY - 130 - pad;
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }
  function hideTooltip() { if (tooltip) tooltip.dataset.visible = 'false'; }

  document.addEventListener('mouseover', function (e) {
    var icon = e.target.closest('.item-tt-icon');
    if (icon) showTooltip(icon, e);
  });
  document.addEventListener('mousemove', function (e) {
    if (e.target.closest('.item-tt-icon')) moveTooltip(e);
  });
  document.addEventListener('mouseout', function (e) {
    if (e.target.closest('.item-tt-icon')) hideTooltip();
  });
})();
"""

# The one page on the whole site that renders itself: a Riot ID typed by any
# visitor can't be pre-built at deploy time, so this fetches from
# metascope-worker (see metascope-worker/, a separate Cloudflare Worker --
# the only live backend BrokenMeta.gg has) and builds the same markup/CSS
# classes the static player.html/game_analysis.html templates already use,
# by hand, in JS. Two "screens" (profile, then one game's analysis) toggled
# in place, with the URL kept in sync via history.pushState so a result is
# still linkable/shareable and survives a refresh or the back button.
METASCOPE_JS = """
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
      + (data.hotStreak ? '<span class="lb-hot" title="' + esc(I.hotStreakTitle) + '">\\ud83d\\udd25</span>' : '')
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
    if (data.isRerollLover) habitsInner += '<div class="metascope-habit-badge">\\ud83c\\udfb2 ' + esc(I.rerollLover) + '</div>';
    if (data.topPlayed && data.topPlayed.length) {
      habitsInner += '<div class="metascope-top-played-label">' + esc(I.topPlayed) + '</div>';
      data.topPlayed.forEach(function (tp) {
        habitsInner += '<div class="metascope-top-played-row">' + champIcon(tp.carrySlug, tp.label)
          + (tp.compSlug ? '<a class="metascope-top-played-name" href="' + ROOT + 'compo/' + tp.compSlug + '/">' + esc(tp.label) + '</a>'
                          : '<span class="metascope-top-played-name">' + esc(tp.label) + '</span>')
          + '<span class="metascope-top-played-count nums">\\u00d7' + tp.count + '</span></div>';
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
        + '<a class="metascope-analyze-link" href="javascript:;" data-match-id="' + g.matchId + '">' + esc(I.analyzeButton) + ' \\u2192</a>'
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
      var icon = ins.type === 'good' ? '\\u2713' : ins.type === 'warning' ? '\\u26a0' : '\\u2139';
      return '<div class="metascope-insight-row" data-type="' + ins.type + '">'
        + '<span class="metascope-insight-icon">' + icon + '</span>'
        + '<div><span class="metascope-insight-category">' + esc(ins.category) + '</span>'
        + '<span class="metascope-insight-text">' + esc(ins.text) + '</span></div></div>';
    }).join('');

    var unitsHtml = (data.units || []).map(function (u) {
      var itemsHtml = (u.items || []).map(function (it) {
        return '<img class="item-icon" src="' + ROOT + 'assets/items/' + it.slug + '.png" alt="' + esc(it.name) + '" title="' + esc(it.name) + '" loading="lazy">';
      }).join('');
      var stars = u.star >= 3 ? '\\u2605\\u2605\\u2605' : u.star === 2 ? '\\u2605\\u2605' : '';
      return '<div class="unit-cell"><div class="unit-icon-wrap">'
        + champIcon(u.slug, u.champion, 'unit-icon', 'border-color:var(--cost-' + (u.cost || 1) + ')')
        + (stars ? '<span class="star-row">' + stars + '</span>' : '')
        + '</div><div class="unit-items">' + itemsHtml + '</div></div>';
    }).join('');

    var lobbyHtml = '<div class="profile-comp-row" style="cursor:default;background:transparent;border-color:transparent">'
      + '<span class="lb-square" style="background:transparent;border:none;color:var(--text-faint)">\\u2014</span>'
      + champIcon(data.carrySlug, data.carry, null, 'width:26px;height:26px;object-fit:cover;border:1px solid var(--cyan)')
      + '<span class="profile-comp-name"><b>' + esc(currentProfile ? currentProfile.riotId : '') + '</b> \\u2014 ' + esc(data.compLabel) + '</span>'
      + '<span class="lb-square ' + (data.placement <= 4 ? 'win' : 'loss') + '">' + data.placement + '</span></div>';
    (data.lobby || []).forEach(function (l) {
      lobbyHtml += '<div class="profile-comp-row" style="cursor:default" data-counter="' + (l.isCounter ? 'true' : 'false') + '">'
        + '<span class="lb-square ' + (l.placement <= 4 ? 'win' : 'loss') + '">' + l.placement + '</span>'
        + champIcon(l.carrySlug, l.carry, null, 'width:26px;height:26px;object-fit:cover;border:1px solid var(--border-bright)')
        + (l.compSlug ? '<a class="profile-comp-name" href="' + ROOT + 'compo/' + l.compSlug + '/">' + esc(l.riotId) + ' \\u2014 ' + esc(l.compLabel) + '</a>'
                       : '<span class="profile-comp-name">' + esc(l.riotId) + ' \\u2014 ' + esc(l.compLabel) + '</span>')
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
"""


TEAM_BUILDER_JS = """
(function () {
  var ROOT = window.BM_ROOT || '';
  var I = window.BM_BUILDER_I18N || {};
  var ROWS = 4, COLS = 7;

  var picker = document.getElementById('champPicker');
  var boardEl = document.getElementById('hexBoard');
  var traitPanel = document.getElementById('traitPanel');
  var searchInput = document.getElementById('builderSearch');
  var costFilters = document.getElementById('builderCostFilters');
  var emptyHint = document.getElementById('builderEmptyHint');
  var resetBtn = document.getElementById('builderReset');
  var shareBtn = document.getElementById('builderShare');
  var copyGameBtn = document.getElementById('builderCopyGame');
  var shareStatus = document.getElementById('builderShareStatus');
  if (!picker || !boardEl) return;

  var champions = [];
  var champBySlug = {};
  var traitDefs = [];
  var plannerHeader = '02';
  var setMutator = '';
  var board = new Array(ROWS * COLS).fill(null);
  var activeCostFilter = 'ALL';

  function champImg(slug) {
    return ROOT + 'assets/champions/' + slug + '.png';
  }
  function traitImg(slug) {
    return ROOT + 'assets/traits/' + slug + '.png';
  }

  // ---- Placement: two ways in, on purpose --------------------------------
  // 1) Drag and drop (mouse + touch via Pointer Events): pick up a champion
  //    from the picker, or an already-placed one straight off the board,
  //    and drop it on any hex cell. Dropping outside the board removes it.
  //    (No bench -- deliberate: it doesn't count toward traits in the real
  //    game either, so it added a UI section without adding anything a
  //    comp-building tool needs.)
  // 2) Tap-to-arm: a plain click/tap (no real movement) on a picker
  //    champion "arms" it instead -- a persistent border/glow, not a
  //    fleeting mid-drag one -- and the next tap on any cell places it
  //    there. Needed because a real drag's "currently held" highlight
  //    collapses to a few milliseconds for a plain click, invisible in
  //    practice; this is what actually answers "show me what I picked".
  var dragGhost = null, dragSlug = null, dragOrigin = null, dragOverEl = null;
  var dragSourcePickerEl = null, dragStartX = 0, dragStartY = 0, dragMoved = false;
  var armedSlug = null, armedPickerEl = null;
  var TAP_THRESHOLD = 6; // px of movement below which a press counts as a tap, not a drag

  function setArmed(slug, pickerEl) {
    if (armedPickerEl) armedPickerEl.dataset.armed = 'false';
    armedSlug = slug;
    armedPickerEl = pickerEl || null;
    if (armedPickerEl) armedPickerEl.dataset.armed = 'true';
  }
  function clearDragSourceHighlight() {
    if (dragSourcePickerEl) { dragSourcePickerEl.dataset.dragging = 'false'; dragSourcePickerEl = null; }
  }

  function beginDrag(slug, origin, x, y, pickerEl) {
    dragSlug = slug;
    dragOrigin = origin; // null if fresh from the picker, else the board index it came from
    dragStartX = x; dragStartY = y; dragMoved = false;
    dragSourcePickerEl = pickerEl || null;
    if (dragSourcePickerEl) dragSourcePickerEl.dataset.dragging = 'true';
    dragGhost = document.createElement('img');
    dragGhost.src = champImg(slug);
    dragGhost.className = 'builder-drag-ghost';
    document.body.appendChild(dragGhost);
    document.body.classList.add('builder-dragging');
    positionGhost(x, y);
  }
  function positionGhost(x, y) {
    if (dragGhost) { dragGhost.style.left = x + 'px'; dragGhost.style.top = y + 'px'; }
  }
  function cellUnder(x, y) {
    var el = document.elementFromPoint(x, y);
    if (!el) return null;
    var hex = el.closest('.hex-cell');
    if (hex) return { idx: parseInt(hex.dataset.idx, 10), el: hex };
    return null;
  }
  function placeArmedOn(idx) {
    board[idx] = armedSlug;
    setArmed(null, null);
    renderCells();
    renderTraitPanel();
    syncUrl();
  }
  document.addEventListener('pointermove', function (e) {
    if (!dragGhost) return;
    positionGhost(e.clientX, e.clientY);
    if (Math.abs(e.clientX - dragStartX) + Math.abs(e.clientY - dragStartY) > TAP_THRESHOLD) dragMoved = true;
    var hit = cellUnder(e.clientX, e.clientY);
    var el = hit ? hit.el : null;
    if (el !== dragOverEl) {
      if (dragOverEl) dragOverEl.dataset.dragover = 'false';
      if (el) el.dataset.dragover = 'true';
      dragOverEl = el;
    }
  });
  document.addEventListener('pointerup', function (e) {
    if (!dragGhost) return;
    document.body.removeChild(dragGhost);
    dragGhost = null;
    document.body.classList.remove('builder-dragging');
    if (dragOverEl) { dragOverEl.dataset.dragover = 'false'; dragOverEl = null; }

    if (!dragMoved && dragOrigin === null) {
      // A tap (not a drag) on a picker champion: arm it instead of
      // cancelling. Re-tapping the already-armed one toggles it off.
      // (Grab the source element BEFORE clearing it -- clearDragSourceHighlight()
      // nulls out dragSourcePickerEl as a side effect.)
      var tappedEl = dragSourcePickerEl;
      var wasThisOneArmed = armedPickerEl === tappedEl;
      clearDragSourceHighlight();
      setArmed(wasThisOneArmed ? null : dragSlug, wasThisOneArmed ? null : tappedEl);
      dragSlug = null; dragOrigin = null;
      return;
    }
    clearDragSourceHighlight();

    var hit = cellUnder(e.clientX, e.clientY);
    if (hit) {
      var displaced = board[hit.idx];
      board[hit.idx] = dragSlug;
      if (dragOrigin !== null && displaced) {
        // swap instead of losing the champion that was already there
        board[dragOrigin] = displaced;
      }
    }
    // hit === null (dropped outside the board): already removed from its
    // origin below on pickup, so this is how a unit gets discarded.
    renderCells();
    renderTraitPanel();
    syncUrl();
    dragSlug = null; dragOrigin = null;
  });
  document.addEventListener('pointercancel', function () {
    if (!dragGhost) return;
    document.body.removeChild(dragGhost);
    dragGhost = null;
    document.body.classList.remove('builder-dragging');
    if (dragOverEl) { dragOverEl.dataset.dragover = 'false'; dragOverEl = null; }
    clearDragSourceHighlight();
    // Interrupted mid-drag (e.g. OS gesture) -- put it back where it came from.
    if (dragOrigin !== null) {
      board[dragOrigin] = dragSlug;
      renderCells();
    }
    dragSlug = null; dragOrigin = null;
  });

  // ---- Board DOM (built once; only its filled state changes) ----
  function wireCellDrag(cell) {
    cell.addEventListener('pointerdown', function (e) {
      var idx = parseInt(cell.dataset.idx, 10);
      if (armedSlug) {
        e.preventDefault();
        placeArmedOn(idx);
        return;
      }
      var slug = board[idx];
      if (!slug) return;
      e.preventDefault();
      board[idx] = null;
      renderCells();
      renderTraitPanel();
      beginDrag(slug, idx, e.clientX, e.clientY);
    });
  }
  function buildBoard() {
    boardEl.innerHTML = '';
    for (var r = 0; r < ROWS; r++) {
      var rowEl = document.createElement('div');
      rowEl.className = 'hex-row';
      if (r % 2 === 1) rowEl.dataset.offset = 'true';
      for (var c = 0; c < COLS; c++) {
        var idx = r * COLS + c;
        var cell = document.createElement('div');
        cell.className = 'hex-cell';
        cell.dataset.idx = String(idx);
        wireCellDrag(cell);
        rowEl.appendChild(cell);
      }
      boardEl.appendChild(rowEl);
    }
  }

  function renderCells() {
    var boardCells = boardEl.querySelectorAll('.hex-cell');
    board.forEach(function (slug, i) { paintCell(boardCells[i], slug); });
    if (emptyHint) emptyHint.hidden = board.some(Boolean);
  }
  function paintCell(el, slug) {
    if (!el) return;
    if (slug && champBySlug[slug]) {
      el.dataset.filled = 'true';
      el.innerHTML = '<img src="' + champImg(slug) + '" alt="' + champBySlug[slug].name + '" loading="lazy">';
    } else {
      el.dataset.filled = 'false';
      el.innerHTML = '';
    }
  }

  // ---- Champion picker ----
  function buildPicker() {
    picker.innerHTML = '';
    if (!champions.length) {
      picker.innerHTML = '<div class="champ-picker-empty"></div>';
      return;
    }
    champions.forEach(function (c) {
      var item = document.createElement('div');
      item.className = 'champ-picker-item';
      item.dataset.slug = c.slug;
      item.dataset.cost = String(c.cost || 1);
      item.dataset.name = c.name.toLowerCase();
      item.style.setProperty('--picker-cost-color', 'var(--cost-' + (c.cost || 1) + ')');
      item.title = c.name;
      item.innerHTML = '<img src="' + champImg(c.slug) + '" alt="' + c.name + '" loading="lazy">';
      item.addEventListener('pointerdown', function (e) {
        e.preventDefault();
        if (armedPickerEl && armedPickerEl !== item) setArmed(null, null);
        beginDrag(c.slug, null, e.clientX, e.clientY, item);
      });
      picker.appendChild(item);
    });
  }
  function applyPickerFilters() {
    var q = (searchInput && searchInput.value.trim().toLowerCase()) || '';
    picker.querySelectorAll('.champ-picker-item').forEach(function (el) {
      var costOk = activeCostFilter === 'ALL' || el.dataset.cost === activeCostFilter;
      var searchOk = !q || el.dataset.name.indexOf(q) !== -1;
      el.dataset.hidden = (costOk && searchOk) ? 'false' : 'true';
    });
  }
  if (searchInput) searchInput.addEventListener('input', applyPickerFilters);
  if (costFilters) {
    costFilters.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-cost-filter]');
      if (!btn) return;
      costFilters.querySelectorAll('[data-cost-filter]').forEach(function (b) { b.dataset.active = String(b === btn); });
      activeCostFilter = btn.dataset.costFilter;
      applyPickerFilters();
    });
  }

  // ---- Trait synergy panel (board only, matches real TFT rules) ----
  function renderTraitPanel() {
    if (!traitPanel) return;
    var counts = {};
    board.forEach(function (slug) {
      var c = slug && champBySlug[slug];
      if (!c) return;
      (c.traits || []).forEach(function (t) { counts[t] = (counts[t] || 0) + 1; });
    });
    var rows = [];
    traitDefs.forEach(function (t) {
      var count = counts[t.name] || 0;
      if (!count) return;
      var effects = t.effects; // ascending by min_units
      var activeIdx = -1;
      for (var i = 0; i < effects.length; i++) {
        if (count >= effects[i].min_units) activeIdx = i;
      }
      var next = effects[activeIdx + 1];
      rows.push({ t: t, count: count, activeIdx: activeIdx, nextMin: next ? next.min_units : null });
    });
    rows.sort(function (a, b) {
      if ((a.activeIdx >= 0) !== (b.activeIdx >= 0)) return (a.activeIdx >= 0) ? -1 : 1;
      return b.count - a.count;
    });
    if (!rows.length) {
      traitPanel.innerHTML = '<div class="champ-picker-empty">' + (I.noTraits || '') + '</div>';
      return;
    }
    traitPanel.innerHTML = rows.map(function (r) {
      var label = r.nextMin ? (r.count + '/' + r.nextMin) : String(r.count);
      return '<div class="trait-row" data-active="' + (r.activeIdx >= 0) + '"' +
        (r.activeIdx >= 0 ? ' data-tier="' + r.activeIdx + '"' : '') + '>' +
        '<img src="' + traitImg(r.t.slug) + '" alt="' + r.t.name + '" loading="lazy">' +
        '<span class="trait-row-name">' + r.t.name + '</span>' +
        '<span class="trait-row-count">' + label + '</span></div>';
    }).join('');
  }

  // ---- Shareable URL state ----
  function syncUrl() {
    var b = [];
    board.forEach(function (slug, i) { if (slug) b.push(i + ':' + slug); });
    var qs = b.length ? ('b=' + b.join(',')) : '';
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
  }
  function loadFromUrl() {
    var params = new URLSearchParams(location.search);
    (params.get('b') || '').split(',').forEach(function (pair) {
      var m = pair.split(':');
      var idx = parseInt(m[0], 10), slug = m[1];
      if (slug && champBySlug[slug] && idx >= 0 && idx < board.length) board[idx] = slug;
    });
  }

  async function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }
  function showStatus(text, isError) {
    if (!shareStatus) return;
    shareStatus.hidden = false;
    shareStatus.textContent = text || '';
    shareStatus.dataset.error = isError ? 'true' : 'false';
    setTimeout(function () { shareStatus.hidden = true; }, 2200);
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      board = new Array(ROWS * COLS).fill(null);
      setArmed(null, null);
      renderCells();
      renderTraitPanel();
      history.replaceState(null, '', location.pathname);
    });
  }
  if (shareBtn) {
    shareBtn.addEventListener('click', function () {
      copyToClipboard(location.href).then(function () { showStatus(I.shareCopied, false); });
    });
  }
  if (copyGameBtn) {
    // Same encoding the real /compo/ pages' copy button uses (see
    // team_planner_code() in build_site.py): header + 10 slots of
    // 3-hex-digit per-champion codes (blank = "000") + the set mutator.
    // Board order (top-left to bottom-right by hex index) is as good an
    // order as any -- the game's planner doesn't care about slot order,
    // only which champions are in it.
    copyGameBtn.addEventListener('click', function () {
      var placed = board.filter(Boolean);
      if (!placed.length) { showStatus(I.copyGameEmpty, true); return; }
      var slots = placed.slice(0, 10).map(function (slug) {
        var c = champBySlug[slug];
        return (c && c.planner_code) || '000';
      });
      while (slots.length < 10) slots.push('000');
      var code = plannerHeader + slots.join('') + setMutator;
      copyToClipboard(code).then(function () { showStatus(I.copyGameCopied, false); });
    });
  }

  fetch(ROOT + 'assets/data/builder.json').then(function (r) { return r.json(); }).then(function (data) {
    champions = data.champions || [];
    traitDefs = data.traits || [];
    plannerHeader = data.plannerHeader || plannerHeader;
    setMutator = data.setMutator || '';
    champions.forEach(function (c) { champBySlug[c.slug] = c; });
    buildPicker();
    buildBoard();
    loadFromUrl();
    renderCells();
    renderTraitPanel();
  }).catch(function () {});
})();
"""


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "x"


def initials(riot_id: str) -> str:
    """Same convention as the Artifact's initials() -- first two characters
    of the name part (before the #tag), uppercased. A no-op on CJK names,
    same as the Artifact's JS .toUpperCase() on those, so behavior matches."""
    name = (riot_id or "").split("#")[0].strip()
    return (name[:2] or "?").upper()


def player_url_slug(rank: int, riot_id: str) -> str:
    """Rank prefix guarantees uniqueness within a region even when the name
    slugifies to nothing (CJK names collapse to 'x' -- verified on real
    leaderboard data, e.g. dozens of Korean riotIds all slugify to 'x')."""
    name = (riot_id or "").split("#")[0].strip()
    return f"{rank}-{slugify(name)}"


def load(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def pct(x: float) -> str:
    return f"{round((x or 0) * 100)}%"


def is_complete_item(name: str) -> bool:
    return not name.startswith("Component_")


def is_emblem(name: str) -> bool:
    return "Emblem" in name


def filter_quality(raw_comps: list[dict]) -> list[dict]:
    """Same quality bar the Artifact's export applies to every slice
    (combined, per-region, per-rank) -- keeps only comps with a real tier
    and enough of a real sample to trust."""
    return [
        c for c in raw_comps
        if c.get("tier") != "?"
        and c.get("play_count", 0) >= MIN_PLAY_COUNT
        and c.get("avg_placement", 99) <= MAX_AVG_PLACEMENT
        and len(c.get("core_units") or []) >= MIN_CORE_BOARD_SIZE
        and not all(u.get("cost") == 5 for u in (c.get("core_units") or []))
    ]


RANK_WORD = {
    "fr": {"IRON": "Fer", "BRONZE": "Bronze", "SILVER": "Argent", "GOLD": "Or", "PLATINUM": "Platine",
           "EMERALD": "Émeraude", "DIAMOND": "Diamant", "MASTER": "Maître", "GRANDMASTER": "Grand Maître",
           "CHALLENGER": "Challenger"},
    "en": {"IRON": "Iron", "BRONZE": "Bronze", "SILVER": "Silver", "GOLD": "Gold", "PLATINUM": "Platinum",
           "EMERALD": "Emerald", "DIAMOND": "Diamond", "MASTER": "Master", "GRANDMASTER": "Grandmaster",
           "CHALLENGER": "Challenger"},
}


def rank_bracket_label(key: str, lang: str = "fr") -> str:
    """Turns a rank-bracket key (whatever config.RANK_BRACKETS currently
    produces -- broad merged buckets like "IRON_SILVER" today, or individual
    tiers like "PLATINUM" if the pipeline is re-run with the newer 8-bucket
    config) into a readable label, without hardcoding which shape is
    current."""
    if key == "MASTER_PLUS":
        return "Maître+" if lang == "fr" else "Master+"
    words = [RANK_WORD[lang].get(p, p.title()) for p in key.split("_")]
    return "-".join(words)


REGION_SHORT = {"EUW": "EUW", "NA": "NA", "BR": "BR", "KR": "KR"}


REGION_COLOR_VAR = {"EUW": "var(--magenta)", "NA": "var(--cyan)", "BR": "var(--gold)", "KR": "var(--teal)"}
MONTHS = {
    "fr": ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}


def short_date(iso: str, lang: str = "fr") -> str:
    y, m, d = iso.split("-")
    return f"{d} {MONTHS[lang][int(m) - 1]}" if lang == "fr" else f"{MONTHS[lang][int(m) - 1]} {d}"


def build_elo_chart_svg(snapshots: list[dict], regions: list[str], lang: str = "fr") -> str:
    """Ports the Artifact's eloChartSVG()/renderEloChart(): a real avg-LP-
    over-time line per region, from leaderboard_history.json snapshots --
    grows one point every time the leaderboard gets refreshed, never
    interpolated or faked."""
    W, H, padL, padR, padT, padB = 760, 300, 46, 18, 18, 34
    plot_w, plot_h = W - padL - padR, H - padT - padB
    n = len(snapshots)
    if not snapshots or not regions:
        return f'<div class="empty-state">{translate(lang, "no_leaderboard_chart")}</div>'

    all_values = [s["avgLp"][r] for s in snapshots for r in regions if s.get("avgLp", {}).get(r) is not None]
    if not all_values:
        return f'<div class="empty-state">{translate(lang, "no_lp_data")}</div>'
    y_min, y_max = min(all_values), max(all_values)
    if y_min == y_max:
        y_min -= 10
        y_max += 10
    y_pad = (y_max - y_min) * 0.12
    y_min, y_max = max(0, y_min - y_pad), y_max + y_pad

    def x_for(i: int) -> float:
        return padL + plot_w / 2 if n == 1 else padL + (plot_w * i) / (n - 1)

    def y_for(v: float) -> float:
        return padT + plot_h - ((v - y_min) / (y_max - y_min)) * plot_h

    grid = []
    GRID_STEPS = 4
    for g in range(GRID_STEPS + 1):
        v = y_min + (y_max - y_min) * g / GRID_STEPS
        y = y_for(v)
        grid.append(f'<line x1="{padL}" y1="{y:.1f}" x2="{W - padR}" y2="{y:.1f}" stroke="var(--border)" stroke-width="1" />')
        grid.append(f'<text x="{padL - 8}" y="{y + 3:.1f}" text-anchor="end" font-size="10">{round(v)}</text>')

    x_labels = []
    step = -(-n // 6)  # ceil(n/6)
    for i, s in enumerate(snapshots):
        if n > 1 and i % step != 0 and i != n - 1:
            continue
        x_labels.append(f'<text x="{x_for(i):.1f}" y="{H - padB + 18}" text-anchor="middle" font-size="10">{short_date(s["date"], lang)}</text>')

    lines = []
    for region in regions:
        pts = [(i, s["avgLp"][region]) for i, s in enumerate(snapshots) if s.get("avgLp", {}).get(region) is not None]
        if not pts:
            continue
        color = REGION_COLOR_VAR[region]
        if len(pts) == 1:
            i, v = pts[0]
            lines.append(f'<circle cx="{x_for(i):.1f}" cy="{y_for(v):.1f}" r="5" fill="{color}" stroke="var(--bg)" stroke-width="2" />')
        else:
            d = " ".join(f'{"M" if idx == 0 else "L"}{x_for(i):.1f},{y_for(v):.1f}' for idx, (i, v) in enumerate(pts))
            lines.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.5" />')
            for i, v in pts:
                lines.append(f'<circle cx="{x_for(i):.1f}" cy="{y_for(v):.1f}" r="3.5" fill="{color}" />')

    return (f'<svg class="ws-chart-svg" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            + "".join(grid) + "".join(x_labels) + "".join(lines) + "</svg>")


# ---------------------------------------------------------------------------
# i18n: FR (default, root URLs) / EN (/en/ prefix, real separate pages with
# hreflang alternates -- not a client-side toggle, since the whole point of
# this rebuild over the Artifact is real per-page SEO in each language).
# `t` is registered once as a Jinja global (see env.globals below) so every
# template and macro can call it directly as t(lang, 'key', ...args) without
# threading a bound closure through every render() call.
# ---------------------------------------------------------------------------
I18N: dict[str, dict] = {
    "fr": {
        "nav_comps": "Compo List", "nav_champions": "Champion List", "nav_patchnotes": "Patch Notes", "nav_leaderboard": "Leaderboard",
        "nav_metascope": "Analyse ton profil",
        "nav_builder": "Team Builder",
        "builder_title": "Team Builder — Teamfight Tactics Set 18",
        "builder_desc": "Compose librement ta comp TFT Set 18 sur un vrai plateau hexagonal : place tes champions, suis tes synergies de familles en direct, et partage le résultat par lien.",
        "builder_h1": "Team Builder",
        "builder_intro": "Place des champions sur le plateau pour voir tes synergies de familles se calculer en direct.",
        "builder_search_placeholder": "Rechercher un champion…",
        "builder_reset": "Réinitialiser",
        "builder_share": "Copier le lien de partage",
        "builder_share_copied": "Lien copié !",
        "builder_copy_game": "Copier pour le jeu",
        "builder_copy_game_copied": "Copié ! (colle-le dans le Team Planner du jeu)",
        "builder_copy_game_empty": "Place au moins un champion avant de copier.",
        "builder_empty_hint": "Le plateau est vide — clique un champion ci-dessus puis une case pour le placer.",
        "builder_traits_title": "Familles",
        "builder_no_traits": "Aucune synergie active pour l'instant.",
        "builder_next_at": lambda n: f"prochain palier à {n}",
        "overlay_cta_title": "L'overlay Overwolf est en cours de développement, pas encore disponible au téléchargement.",
        "overlay_cta_soon": "Bientôt",
        "footer_generated": lambda date, s: f"Généré le {date} · Set {s}",
        "footer_disclaimer": "BrokenMeta.gg n'est pas approuvé par Riot Games et ne reflète pas les opinions de Riot Games ou de quiconque impliqué officiellement dans la production ou la gestion des propriétés de Riot Games. Riot Games et toutes les propriétés associées sont des marques commerciales ou déposées de Riot Games, Inc.",
        "footer_nav_title": "Navigation", "footer_about_title": "À propos",
        "lbl_region": "Région", "lbl_rank": "Rang", "lbl_tier": "Tier", "lbl_type": "Type",
        "region_all": "Toutes", "rank_all": "Tous rangs", "tier_all": "Tout",
        "placement_label": "Placement", "top4_label": "Top 4", "contest_label": "Contest.",
        "level_badge": lambda n: f"Niveau {n}",
        "home_intro": lambda n, m: f"{n} compositions {SET_LABEL} calculées à partir de {m} parties classées réelles, collectées via l'API officielle de Riot (Match-V1). Aucune donnée inventée ou estimée : chaque statistique vient d'un vrai match.",
        "faq_best_comp_q": f"Quelle est la meilleure comp {SET_LABEL} en ce moment ?",
        "faq_best_comp_a": lambda label, tier, placement, top4, matches: f"D'après {matches} vraies parties classées analysées, la meilleure comp {SET_LABEL} en ce moment est {label} (Tier {tier}), avec un placement moyen de {placement} et {top4} de top 4.",
        "faq_comp_tier_q": lambda label: f"Quel tier a {label} sur {SET_LABEL} ?",
        "faq_comp_tier_a": lambda label, tier, placement, top4, matches: f"{label} est actuellement Tier {tier} sur {SET_LABEL}, avec un placement moyen de {placement} et {top4} de top 4 sur {matches} vraies parties classées analysées.",
        "scope_intro": lambda n, suffix: f"{n} compositions {SET_LABEL}{suffix} classées, triées par taux de top 4 puis placement moyen. Données réelles issues de l'API Riot Match-V1.",
        "tier_scope_intro": lambda n, tier, suffix: f"{n} compositions {SET_LABEL} classées Tier {tier}{suffix}, triées par taux de top 4 puis placement moyen.",
        "see_full_tier": lambda n, tier: f"Voir les {n} compos Tier {tier} →",
        "tier_word": "Tier",
        "type_all": "Tout type",
        "search_placeholder": "Rechercher une comp, un carry, un champion…",
        "empty_no_comp_filter": "Aucune comp ne correspond à ce filtre.",
        "empty_no_comp_search": lambda q: f"Aucune comp ne correspond à « {q} ».",
        "view_full_sheet": "Voir la fiche complète →",
        "copy_comp_title": "Copier la compo pour le Team Planner du jeu — expérimental, champions seulement (pas les objets).",
        "copy_comp_aria": "Copier la compo", "copied_title": "Copié ! (champions seulement, pas les objets)", "copy_failed_title": "Échec de la copie",
        "full_composition_title": "Composition complète",
        "item_combos_title": "Combinaisons d'objets — persos principaux (top 10)",
        "combo_col_header": "Combinaison", "avg_placement_col": "Placement moyen",
        "no_main_carries": "Pas assez de données pour dégager des persos principaux sur cette comp.",
        "top_ladders_title": "Joué dans le TOP ladders",
        "no_ladder_sightings": "Aucun joueur du leaderboard n'a joué cette compo dans les 10 dernières parties observées.",
        "placement_colon": lambda p: f"Placement : {p}",
        "matchups_vs_title": "Match-up vs", "vs_word": "vs",
        "encounters_count": lambda n: f"{n} rencontres",
        "not_enough_shared_lobby_comp": "Pas assez de rencontres en lobby partagée pour cette comp dans cet échantillon.",
        "board_variants_title": "Variantes de board",
        "not_enough_variants": "Pas assez de parties pour dégager des variantes fiables de cette comp.",
        "baseline_tag": "Référence", "share_of_games": lambda p: f"{p} des parties", "avg_placement_inline": "placement moyen",
        "board_variants_note": "Versions réelles du board final de cette comp : quel groupe exact de champions apparaît ensemble, à quelle fréquence, et le placement moyen de ces parties. Pas un historique de partie (Riot n'expose que le board de fin de partie, jamais son évolution) : une comparaison de builds, pas un chemin dans le temps.",
        "board_addons_title": "Compléments de board (9e/10e unité)",
        "no_base_board_data": "Pas assez de données pour dégager un board de base fiable sur cette comp.",
        "base_board_label": lambda n: f"Board de base — {n} unités",
        "not_enough_exact_board": "Pas assez de parties avec exactement ce board, sans ajout",
        "games_count": lambda n: f"{n} partie{'s' if n > 1 else ''}",
        "plus_one_title": lambda n: f"+1 unité ({n} au total)", "plus_two_title": lambda n: f"+2 unités ({n} au total)",
        "not_enough_extra_unit": "Pas assez de parties avec une unité en plus pour dégager un signal fiable.",
        "board_addons_note": 'Le board principal ci-dessus s\'arrête à 9 unités : atteindre un 10e emplacement demande le niveau 10, qui à lui seul corrèle déjà fortement avec un bon placement. Ci-dessous, le placement moyen des parties ayant ce board de base <b style="color:var(--cream)">plus</b> une ou deux unités en plus, présenté comme une corrélation à interpréter, pas une recommandation causale.',
        "incomplete_attempts_title": "Tentatives incomplètes regroupées ici",
        "units_word": lambda n: f"{n} unités",
        "similar_variants_note": "Ces compos partagent un sous-ensemble strict des unités ci-dessus (jamais d'unité en plus) — des tentatives probables de cette même comp, arrêtées en cours de route plutôt que des archétypes distincts.",
        "augments_title": "Chemin d'augments",
        "augments_note": '<b>Donnée indisponible.</b> L\'API Riot ne renseigne pas le champ des augments pour ce set — vérifié directement sur l\'échantillon collecté (le champ "augments" n\'apparaît même pas dans la réponse, sur 23 000+ participants réels examinés). Le champ existe bien dans le schéma officiel et fonctionnait sur d\'anciens sets, donc ce n\'est probablement pas définitif — cette section s\'activera automatiquement dès qu\'il se remplit à nouveau.',
        "champions_title": "Champions — Teamfight Tactics Set 18",
        "champ_list_title": "Liste des champions", "th_rank": "Rang", "th_champion": "Champion",
        "th_playrate": "Popularité", "th_avgplacement": "Placement moyen", "th_top4": "Top 4",
        "th_avgstar": "Étoile moyenne", "th_commonitems": "Objets fréquents",
        "tt_common_items": lambda items: f"Objets fréquents : {items}",
        "champ_unranked_note": 'Les champions marqués <b style="color:var(--cream)">?</b> n\'ont pas encore assez de parties observées dans cet échantillon pour un rang fiable — ils restent affichés avec leurs stats brutes.',
        "best_items_title": "Meilleurs objets",
        "no_combo_data": "Pas assez de données de combinaisons pour ce champion dans cet échantillon.",
        "games_col": "Parties", "winrate_col": "Winrate",
        "compositions_title": "Compositions",
        "champ_not_in_comp": "Ce champion n'apparaît dans aucune comp classée de cet échantillon.",
        "balance_history_title": "Historique d'équilibrage",
        "back_to_leaderboard": "← Retour au leaderboard",
        "leaderboard_title": "Leaderboard — Teamfight Tactics Set 18",
        "th_player": "Joueur", "th_tier": "Palier", "th_form": "Forme (5 dernières)",
        "hot_streak_title": "Série en cours",
        "lb_note": 'Classement réel (League-v1, Challenger complété par Grandmaster/Master si le serveur en a moins de 100), trié par LP. TFT n\'a pas de victoire/défaite au sens strict : <b style="color:var(--good)">W</b> = top 4 sur la partie, <b style="color:var(--warn)">L</b> = 5ᵉ-8ᵉ — une convention d\'affichage, pas une donnée Riot.',
        "player_page_desc": lambda riot_id, region: f"Profil réel de {riot_id} sur le leaderboard {region} de Teamfight Tactics Set 18 : LP, palier, winrate et 10 dernières parties classées, via l'API officielle de Riot.",
        "region_rank_of": lambda region, rank: f"{region} · Rang #{rank}",
        "record_label": "Bilan", "record_wl": lambda w, l: f"{w}W / {l}L", "winrate_label": "Winrate",
        "last10_games_title": "10 dernières parties classées",
        "no_recent_games": "Pas de partie récente enregistrée pour ce joueur.",
        "ms_stats_title": "Statistiques", "ms_regional_rank": "Rang régional",
        "ms_habits_title": "Habitudes de jeu", "ms_reroll_lover": "Adepte du reroll",
        "ms_top_played": "Compos favorites", "ms_no_habits": "Pas assez de parties récentes pour dégager une habitude de jeu.",
        "ms_analyze_hint": "Clique sur « Analyser la partie » pour voir en détail ce qui a bien (ou moins bien) marché dans une de ces parties.",
        "ms_analyze_button": "Analyser la partie",
        "ms_analysis_of": lambda riot_id: f"Analyse de partie — {riot_id}",
        "ms_analysis_desc": lambda riot_id, comp: f"Analyse réelle d'une partie classée de {riot_id} sur {comp} : comparaison aux moyennes de la comp, qualité du build, adversaires rencontrés — MetaScope, via l'API officielle de Riot.",
        "ms_back_to_profile": lambda riot_id: f"← Retour au profil de {riot_id}",
        "ms_level_label": "Niveau", "ms_gold_left_label": "Or restant",
        "ms_your_board_title": "Ton board en fin de partie",
        "ms_insights_title": "Ce qui a marché (ou non)",
        "ms_insights_fr_only": "Ces observations sont pour l'instant générées uniquement en français.",
        "ms_no_insights": "Pas assez de données pour comparer cette partie à des moyennes fiables.",
        "ms_lobby_title": "Classement de la partie",
        "ms_counter_tag": "Contre ta compo",
        "ms_no_lobby": "Détail des adversaires indisponible pour cette partie.",
        "ms_page_intro": "Entre ton Riot ID pour voir ton profil réel — LP, placement moyen, habitudes de jeu — et analyser en détail une de tes parties récentes : ce qui a bien (ou moins bien) marché, et si des adversaires contraient ta compo.",
        "ms_riotid_placeholder": "Pseudo#TAG",
        "ms_search_button": "Voir mon profil",
        "ms_loading": "Recherche en cours…",
        "ms_back_button": "← Retour au profil",
        "ms_winrate_unavailable": "Palier non classé pour l'instant.",
        "ms_profile_of": lambda riot_id: f"Profil de {riot_id}",
        "worldstat_title": "World Stat — Teamfight Tactics Set 18",
        "worldstat_elo_title": "Élo moyen du top 100 par région",
        "no_leaderboard_chart": "Pas encore de relevé de classement pour construire la courbe.",
        "no_lp_data": "Pas encore de donnée de LP moyen.",
        "worldstat_single_point_note": "Premier relevé — un seul point par région pour l'instant. La courbe se construira au fil des prochains rafraîchissements du classement.",
        "worldstat_top10_title": "Top 10 par région — palier & winrate",
        "not_enough_ranked_players": "Pas assez de joueurs classés.",
        "worldstat_topcomps_title": "Compos les plus jouées par le top 10",
        "not_enough_recent_top10": "Pas assez de parties récentes chez le top 10.",
        "patch_notes_title": "Patch Notes — Teamfight Tactics Set 18",
        "patch_banner": 'Riot ne publie pas les patch notes TFT via une API — seulement en articles sur son site officiel, et pas toujours pour les petits correctifs d\'équilibrage entre deux patchs. Voici une sélection résumée à la main des derniers patchs ; chaque carte renvoie vers l\'article complet, sur <a href="https://teamfighttactics.leagueoflegends.com/en-us/news/" target="_blank" rel="noopener">teamfighttactics.leagueoflegends.com</a> quand Riot en a publié un, sinon vers une source communautaire de référence.',
        "patch_word": "Patch", "read_full_article": "Lire l'article complet →",
        "nav_glossary": "Glossaire",
        "nav_glossary_champions": "Champions", "nav_glossary_families": "Familles",
        "nav_glossary_augments": "Augments", "nav_glossary_items": "Objets",
        "glossary_title": f"Glossaire {SET_LABEL}",
        "glossary_desc": f"Glossaire complet {SET_LABEL} : tous les champions, familles, augments et objets, avec leurs effets réels.",
        "glossary_intro": "Référence complète du set : champions, familles, augments et objets, avec leurs vraies fiches (effets, composants, synergies).",
        "glossary_count": lambda n: f"{n} entrées",
        "glossary_champions_hub_desc": "Tous les champions du set, avec accès direct à leur fiche complète.",
        "glossary_families_hub_desc": "Toutes les familles (traits) : comment elles fonctionnent, qui en fait partie, quelles comps s'appuient dessus.",
        "glossary_augments_hub_desc": "Tous les augments du set, triés par rareté (Argent, Or, Prismatique).",
        "glossary_items_hub_desc": "Tous les objets complets du set, leurs composants et les champions qui en tirent le meilleur parti.",
        "glossary_champions_title": f"Champions — Glossaire {SET_LABEL}",
        "glossary_champions_desc": f"Liste illustrée de tous les champions {SET_LABEL} classés, avec accès direct à la fiche de chacun.",
        "glossary_champions_intro": "Clique un champion pour voir sa fiche complète (objets, compositions, historique d'équilibrage).",
        "glossary_families_title": f"Familles — Glossaire {SET_LABEL}",
        "glossary_families_desc": f"Toutes les familles (traits) de {SET_LABEL} : paliers, champions membres, compositions basées dessus.",
        "glossary_families_intro": "Clique une famille pour voir comment elle fonctionne, ses champions membres, et les comps qui s'appuient dessus.",
        "family_detail_desc": lambda name: f"Famille {name} sur {SET_LABEL} : comment elle fonctionne, ses champions membres, et les compositions réelles construites autour d'elle.",
        "family_breakpoints_title": "Paliers de la famille",
        "family_breakpoint_fallback": lambda n: f"({n}) Palier actif.",
        "family_members_title": "Champions de la famille",
        "family_no_members": "Aucun champion trouvé pour cette famille.",
        "family_comps_title": "Compositions basées sur cette famille",
        "family_no_comps": "Aucune comp classée n'est actuellement construite autour de cette famille dans cet échantillon.",
        "glossary_augments_title": f"Augments — Glossaire {SET_LABEL}",
        "glossary_augments_desc": f"Tous les augments {SET_LABEL}, triés par rareté (Argent, Or, Prismatique), avec leur effet réel.",
        "glossary_augments_intro": 'Riot ne publie pas quel augment un joueur a pris via l\'API Match-V1 pour ce set (voir la note sur les fiches de comp) — cette liste est donc une référence statique, sans statistique de pick rate ou de winrate.',
        "augment_tier_silver": "Argent", "augment_tier_gold": "Or", "augment_tier_prismatic": "Prismatique",
        "glossary_items_title": f"Objets — Glossaire {SET_LABEL}",
        "glossary_items_desc": f"Tous les objets complets {SET_LABEL}, leurs composants et les champions qui en tirent le meilleur winrate.",
        "glossary_items_intro": "Survole une icône pour voir ses composants. Clique un objet pour voir sa fiche complète.",
        "item_detail_desc": lambda name: f"{name} sur {SET_LABEL} : effet, composants nécessaires, et les champions avec le meilleur winrate en le portant.",
        "item_composition_title": "Composants nécessaires",
        "item_top_champions_title": "Champions avec un fort winrate sur cet objet",
        "item_no_champion_data": "Pas assez de parties observées avec cet objet pour dégager des champions fiables.",
    },
    "en": {
        "nav_comps": "Comp List", "nav_champions": "Champion List", "nav_patchnotes": "Patch Notes", "nav_leaderboard": "Leaderboard",
        "nav_metascope": "Analyze your profile",
        "nav_builder": "Team Builder",
        "builder_title": "Team Builder — Teamfight Tactics Set 18",
        "builder_desc": "Freely build your TFT Set 18 comp on a real hex board: place champions, track trait synergies live, and share the result with a link.",
        "builder_h1": "Team Builder",
        "builder_intro": "Place champions on the board to see your trait synergies calculated live.",
        "builder_search_placeholder": "Search a champion…",
        "builder_reset": "Reset",
        "builder_share": "Copy share link",
        "builder_share_copied": "Link copied!",
        "builder_copy_game": "Copy for the game",
        "builder_copy_game_copied": "Copied! (paste it into the game's Team Planner)",
        "builder_copy_game_empty": "Place at least one champion before copying.",
        "builder_empty_hint": "The board is empty — click a champion above, then a cell to place it.",
        "builder_traits_title": "Traits",
        "builder_no_traits": "No active synergy yet.",
        "builder_next_at": lambda n: f"next tier at {n}",
        "overlay_cta_title": "The Overwolf overlay is in development, not yet available for download.",
        "overlay_cta_soon": "Soon",
        "footer_generated": lambda date, s: f"Generated on {date} · Set {s}",
        "footer_disclaimer": "BrokenMeta.gg isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc.",
        "footer_nav_title": "Navigation", "footer_about_title": "About",
        "lbl_region": "Region", "lbl_rank": "Rank", "lbl_tier": "Tier", "lbl_type": "Type",
        "region_all": "All", "rank_all": "All ranks", "tier_all": "All",
        "placement_label": "Placement", "top4_label": "Top 4", "contest_label": "Contest.",
        "level_badge": lambda n: f"Level {n}",
        "home_intro": lambda n, m: f"{n} {SET_LABEL} comps calculated from {m} real ranked games, collected via Riot's official API (Match-V1). No invented or estimated data: every stat comes from a real match.",
        "faq_best_comp_q": f"What's the best {SET_LABEL} comp right now?",
        "faq_best_comp_a": lambda label, tier, placement, top4, matches: f"Based on {matches} real ranked games analyzed, the best {SET_LABEL} comp right now is {label} (Tier {tier}), with a {placement} average placement and {top4} top 4 rate.",
        "faq_comp_tier_q": lambda label: f"What tier is {label} on {SET_LABEL}?",
        "faq_comp_tier_a": lambda label, tier, placement, top4, matches: f"{label} is currently Tier {tier} on {SET_LABEL}, with a {placement} average placement and {top4} top 4 rate over {matches} real ranked games analyzed.",
        "scope_intro": lambda n, suffix: f"{n} {SET_LABEL} ranked comps{suffix}, sorted by top 4 rate then average placement. Real data from the Riot Match-V1 API.",
        "tier_scope_intro": lambda n, tier, suffix: f"{n} {SET_LABEL} comps ranked Tier {tier}{suffix}, sorted by top 4 rate then average placement.",
        "see_full_tier": lambda n, tier: f"See all {n} Tier {tier} comps →",
        "tier_word": "Tier",
        "type_all": "All types",
        "search_placeholder": "Search a comp, a carry, a champion…",
        "empty_no_comp_filter": "No comp matches this filter.",
        "empty_no_comp_search": lambda q: f'No comp matches "{q}".',
        "view_full_sheet": "View full sheet →",
        "copy_comp_title": "Copy the comp to the game's Team Planner — experimental, champions only (no items).",
        "copy_comp_aria": "Copy comp", "copied_title": "Copied! (champions only, no items)", "copy_failed_title": "Copy failed",
        "full_composition_title": "Full composition",
        "item_combos_title": "Item combos — main carries (top 10)",
        "combo_col_header": "Combo", "avg_placement_col": "Avg placement",
        "no_main_carries": "Not enough data to identify main carries for this comp.",
        "top_ladders_title": "Seen on the TOP ladders",
        "no_ladder_sightings": "No leaderboard player has played this comp in the last 10 observed games.",
        "placement_colon": lambda p: f"Placement: {p}",
        "matchups_vs_title": "Matchups vs", "vs_word": "vs",
        "encounters_count": lambda n: f"{n} encounters",
        "not_enough_shared_lobby_comp": "Not enough shared-lobby encounters for this comp in this sample.",
        "board_variants_title": "Board variants",
        "not_enough_variants": "Not enough games to identify reliable variants for this comp.",
        "baseline_tag": "Baseline", "share_of_games": lambda p: f"{p} of games", "avg_placement_inline": "avg placement",
        "board_variants_note": "Real versions of this comp's final board: which exact group of champions shows up together, how often, and the average placement of those games. Not a game-by-game history (Riot only exposes the end-of-game board, never how it got there): a comparison of builds, not a timeline.",
        "board_addons_title": "Board add-ons (9th/10th unit)",
        "no_base_board_data": "Not enough data to identify a reliable base board for this comp.",
        "base_board_label": lambda n: f"Base board — {n} units",
        "not_enough_exact_board": "Not enough games with exactly this board, no add-ons",
        "games_count": lambda n: f"{n} game{'s' if n > 1 else ''}",
        "plus_one_title": lambda n: f"+1 unit ({n} total)", "plus_two_title": lambda n: f"+2 units ({n} total)",
        "not_enough_extra_unit": "Not enough games with an extra unit for a reliable signal.",
        "board_addons_note": 'The main board above stops at 9 units: reaching a 10th slot needs level 10, which on its own already correlates strongly with a good placement. Below, the average placement of games with this base board <b style="color:var(--cream)">plus</b> one or two extra units, shown as a correlation to interpret, not a causal recommendation.',
        "incomplete_attempts_title": "Incomplete attempts grouped here",
        "units_word": lambda n: f"{n} units",
        "similar_variants_note": "These comps share a strict subset of the units above (never an extra one) — likely attempts at this same comp, stopped partway rather than distinct archetypes.",
        "augments_title": "Augment path",
        "augments_note": '<b>Data unavailable.</b> Riot\'s API doesn\'t populate the augments field for this set — verified directly on the collected sample (the "augments" field doesn\'t even appear in the response, across 23,000+ real participants checked). The field does exist in the official schema and worked on older sets, so this probably isn\'t permanent — this section will activate automatically as soon as it fills in again.',
        "champions_title": "Champions — Teamfight Tactics Set 18",
        "champ_list_title": "Champion list", "th_rank": "Rank", "th_champion": "Champion",
        "th_playrate": "Play rate", "th_avgplacement": "Avg placement", "th_top4": "Top 4",
        "th_avgstar": "Avg star", "th_commonitems": "Common items",
        "tt_common_items": lambda items: f"Common items: {items}",
        "champ_unranked_note": 'Champions marked <b style="color:var(--cream)">?</b> don\'t have enough observed games in this sample yet for a reliable rank — they\'re still shown with their raw stats.',
        "best_items_title": "Best items",
        "no_combo_data": "Not enough item-combo data for this champion in this sample.",
        "games_col": "Games", "winrate_col": "Winrate",
        "compositions_title": "Comps",
        "champ_not_in_comp": "This champion doesn't appear in any ranked comp in this sample.",
        "balance_history_title": "Balance history",
        "back_to_leaderboard": "← Back to leaderboard",
        "leaderboard_title": "Leaderboard — Teamfight Tactics Set 18",
        "th_player": "Player", "th_tier": "Tier", "th_form": "Form (last 5)",
        "hot_streak_title": "On a streak",
        "lb_note": 'Real standings (League-v1, Challenger topped up with Grandmaster/Master if the server has fewer than 100), sorted by LP. TFT doesn\'t have a strict win/loss: <b style="color:var(--good)">W</b> = top 4 that game, <b style="color:var(--warn)">L</b> = 5th-8th — a display convention, not a Riot-provided stat.',
        "player_page_desc": lambda riot_id, region: f"Real profile for {riot_id} on the {region} Teamfight Tactics Set 18 leaderboard: LP, tier, winrate and the last 10 ranked games, via Riot's official API.",
        "region_rank_of": lambda region, rank: f"{region} · Rank #{rank}",
        "record_label": "Record", "record_wl": lambda w, l: f"{w}W / {l}L", "winrate_label": "Winrate",
        "last10_games_title": "Last 10 ranked games",
        "no_recent_games": "No recent games recorded for this player.",
        "ms_stats_title": "Stats", "ms_regional_rank": "Regional rank",
        "ms_habits_title": "Playstyle habits", "ms_reroll_lover": "Reroll enthusiast",
        "ms_top_played": "Favorite comps", "ms_no_habits": "Not enough recent games to identify a playstyle habit.",
        "ms_analyze_hint": "Click \"Analyze this game\" to see in detail what worked (or didn't) in one of these games.",
        "ms_analyze_button": "Analyze this game",
        "ms_analysis_of": lambda riot_id: f"Game analysis — {riot_id}",
        "ms_analysis_desc": lambda riot_id, comp: f"Real analysis of a ranked game by {riot_id} on {comp}: comparison against the comp's averages, build quality, opponents faced — MetaScope, via Riot's official API.",
        "ms_back_to_profile": lambda riot_id: f"← Back to {riot_id}'s profile",
        "ms_level_label": "Level", "ms_gold_left_label": "Gold left",
        "ms_your_board_title": "Your board at the end of the game",
        "ms_insights_title": "What worked (or didn't)",
        "ms_insights_fr_only": "These insights are currently only generated in French.",
        "ms_no_insights": "Not enough data to compare this game against reliable averages.",
        "ms_lobby_title": "Game standings",
        "ms_counter_tag": "Counters your comp",
        "ms_no_lobby": "Opponent detail unavailable for this game.",
        "ms_page_intro": "Enter your Riot ID to see your real profile — LP, average placement, playstyle habits — and analyze one of your recent games in detail: what worked (or didn't), and whether any opponents countered your comp.",
        "ms_riotid_placeholder": "Name#TAG",
        "ms_search_button": "View my profile",
        "ms_loading": "Searching…",
        "ms_back_button": "← Back to profile",
        "ms_winrate_unavailable": "Not ranked yet.",
        "ms_profile_of": lambda riot_id: f"{riot_id}'s profile",
        "worldstat_title": "World Stat — Teamfight Tactics Set 18",
        "worldstat_elo_title": "Average Elo of the top 100 by region",
        "no_leaderboard_chart": "Not enough leaderboard data yet to build the chart.",
        "no_lp_data": "Not enough average LP data yet.",
        "worldstat_single_point_note": "First reading — a single point per region for now. The chart will build up over future leaderboard refreshes.",
        "worldstat_top10_title": "Top 10 by region — tier & winrate",
        "not_enough_ranked_players": "Not enough ranked players.",
        "worldstat_topcomps_title": "Most played comps by the top 10",
        "not_enough_recent_top10": "Not enough recent games from the top 10.",
        "patch_notes_title": "Patch Notes — Teamfight Tactics Set 18",
        "patch_banner": 'Riot doesn\'t publish TFT patch notes through an API — only as articles on its official site, and not always for smaller mid-patch balance hotfixes. Here\'s a hand-written summary of the latest patches; each card links to the full article, on <a href="https://teamfighttactics.leagueoflegends.com/en-us/news/" target="_blank" rel="noopener">teamfighttactics.leagueoflegends.com</a> when Riot published one, otherwise to a reliable community source.',
        "patch_word": "Patch", "read_full_article": "Read full article →",
        "nav_glossary": "Glossary",
        "nav_glossary_champions": "Champions", "nav_glossary_families": "Families",
        "nav_glossary_augments": "Augments", "nav_glossary_items": "Items",
        "glossary_title": f"{SET_LABEL} Glossary",
        "glossary_desc": f"Complete {SET_LABEL} glossary: every champion, family, augment and item, with their real effects.",
        "glossary_intro": "The set's full reference: champions, families, augments and items, each with a real page (effects, components, synergies).",
        "glossary_count": lambda n: f"{n} entries",
        "glossary_champions_hub_desc": "Every champion in the set, with direct access to their full sheet.",
        "glossary_families_hub_desc": "Every family (trait): how it works, its members, and which comps build around it.",
        "glossary_augments_hub_desc": "Every augment in the set, sorted by rarity (Silver, Gold, Prismatic).",
        "glossary_items_hub_desc": "Every finished item in the set, its components, and the champions who get the most out of it.",
        "glossary_champions_title": f"Champions — {SET_LABEL} Glossary",
        "glossary_champions_desc": f"Illustrated list of every ranked {SET_LABEL} champion, with direct access to each one's sheet.",
        "glossary_champions_intro": "Click a champion to see their full sheet (items, comps, balance history).",
        "glossary_families_title": f"Families — {SET_LABEL} Glossary",
        "glossary_families_desc": f"Every {SET_LABEL} family (trait): breakpoints, member champions, and comps built around it.",
        "glossary_families_intro": "Click a family to see how it works, its member champions, and the comps built around it.",
        "family_detail_desc": lambda name: f"The {name} family on {SET_LABEL}: how it works, its member champions, and the real comps built around it.",
        "family_breakpoints_title": "Family breakpoints",
        "family_breakpoint_fallback": lambda n: f"({n}) Active breakpoint.",
        "family_members_title": "Family champions",
        "family_no_members": "No champion found for this family.",
        "family_comps_title": "Comps built around this family",
        "family_no_comps": "No ranked comp is currently built around this family in this sample.",
        "glossary_augments_title": f"Augments — {SET_LABEL} Glossary",
        "glossary_augments_desc": f"Every {SET_LABEL} augment, sorted by rarity (Silver, Gold, Prismatic), with its real effect.",
        "glossary_augments_intro": "Riot's Match-V1 API doesn't expose which augment a player took for this set (see the note on comp sheets) — this list is a static reference, with no pick rate or win rate stat.",
        "augment_tier_silver": "Silver", "augment_tier_gold": "Gold", "augment_tier_prismatic": "Prismatic",
        "glossary_items_title": f"Items — {SET_LABEL} Glossary",
        "glossary_items_desc": f"Every finished {SET_LABEL} item, its components, and the champions with the best win rate holding it.",
        "glossary_items_intro": "Hover an icon to see its components. Click an item to see its full sheet.",
        "item_detail_desc": lambda name: f"{name} on {SET_LABEL}: effect, required components, and the champions with the best win rate holding it.",
        "item_composition_title": "Required components",
        "item_top_champions_title": "Champions with a high win rate on this item",
        "item_no_champion_data": "Not enough observed games with this item to identify reliable champions.",
    },
}


def translate(lang: str, key: str, *args):
    entry = I18N.get(lang, I18N["fr"]).get(key, key)
    return entry(*args) if callable(entry) else entry


def playstyle_cat(tag: str | None) -> str:
    return (tag or "").split(" ")[0]


def units_worth_itemizing(units: list[dict], carry: str | None) -> set[str]:
    """Mirrors the Artifact's unitsWorthItemizing(): the carry always, plus
    the 2 non-carry units holding the most complete items."""
    with_items = [
        (u["champion"], [i for i in (u.get("items") or []) if is_complete_item(i)])
        for u in units if u["champion"] != carry
    ]
    with_items = [(c, i) for c, i in with_items if i]
    with_items.sort(key=lambda x: -len(x[1]))
    top_n = 2 if carry else 3
    top = {c for c, _ in with_items[:top_n]}
    if carry and any(u["champion"] == carry for u in units):
        top.add(carry)
    return top


class ImageCache:
    """Downloads champion/item images to real files once, dedup by slug."""

    def __init__(self, dist: Path):
        self.champ_dir = dist / "assets" / "champions"
        self.item_dir = dist / "assets" / "items"
        self.trait_dir = dist / "assets" / "traits"
        self.augment_dir = dist / "assets" / "augments"
        self.champ_dir.mkdir(parents=True, exist_ok=True)
        self.item_dir.mkdir(parents=True, exist_ok=True)
        self.trait_dir.mkdir(parents=True, exist_ok=True)
        self.augment_dir.mkdir(parents=True, exist_ok=True)
        self._done: set[str] = set()

    def _fetch(self, url: str, dest: Path) -> None:
        key = str(dest)
        if key in self._done or dest.exists():
            self._done.add(key)
            return
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        self._done.add(key)

    def champion(self, slug: str, url: str) -> None:
        self._fetch(url, self.champ_dir / f"{slug}.png")

    def item(self, slug: str, url: str) -> None:
        self._fetch(url, self.item_dir / f"{slug}.png")

    def trait(self, slug: str, url: str) -> None:
        self._fetch(url, self.trait_dir / f"{slug}.png")

    def augment(self, slug: str, url: str) -> None:
        self._fetch(url, self.augment_dir / f"{slug}.png")


def main() -> None:
    combined = load("tierlist.json")
    champion_stats = load("champion_stats.json")
    leaderboard_json = load("leaderboard.json")
    matchups_json = load("matchups.json")
    comp_history = load("comp_history.json") if (OUT / "comp_history.json").exists() else {"snapshots": []}
    leaderboard_history = load("leaderboard_history.json") if (OUT / "leaderboard_history.json").exists() else {"snapshots": []}

    # ---- Fresh clean output dir ----
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    images = ImageCache(DIST)

    # ---- Real champion + item image URLs (same CDragon source as the Artifact) ----
    raw_image_map = build_champion_image_map(SET_MUTATOR, refresh=False)
    info_by_name = {info["name"]: info for info in raw_image_map.values()}

    # ---- Team Planner copy button (ported from the Artifact) -- format
    # confirmed by extracting metatft.com's own (working) encoder out of its
    # Redux store: header "02" (not "01" -- that's only for TFTSet13/
    # TFTSet4_Act2), each of 10 slots is CDragon's `team_planner_code` field
    # zero-padded to 3 hex digits (not 2, not 4), blank = "000". See
    # build_team_planner_codes()'s docstring in champion_images.py for the
    # two earlier wrong versions this replaced, both rejected by the user's
    # live in-game test. Computed here (ahead of the Team Builder block
    # below, which also needs it per-champion) rather than at its original
    # spot further down. ----
    champ_name_map = {cid: info["name"] for cid, info in raw_image_map.items()}
    planner_codes = build_team_planner_codes(SET_MUTATOR, name_map=champ_name_map, refresh=False)
    PLANNER_HEADER = "01" if SET_MUTATOR in ("TFTSet13", "TFTSet4_Act2") else "02"

    # ---- Team Builder: full static roster + trait breakpoints. Unlike
    # every other page on the site, this doesn't depend on match data at
    # all -- raw_image_map already has every real champion in the set
    # (traits non-empty filters out neutral board hazards like Murk Wolf),
    # so a low-sample-size run still gets a complete picker. ----
    builder_champions = []
    for info in raw_image_map.values():
        if not info.get("traits"):
            continue
        slug = slugify(info["name"])
        images.champion(slug, info["icon"])
        code = planner_codes.get(info["name"])
        builder_champions.append({
            "name": info["name"], "slug": slug, "cost": info["cost"], "traits": info["traits"],
            "planner_code": f"{code:03x}" if code is not None else None,
        })
    builder_champions.sort(key=lambda c: (c["cost"] or 0, c["name"]))

    builder_traits = []
    for trait in build_trait_data(SET_MUTATOR, refresh=False):
        slug = slugify(trait["name"])
        images.trait(slug, trait["icon"])
        builder_traits.append({"name": trait["name"], "slug": slug, "effects": trait["effects"]})
    trait_by_name = {t["name"]: t for t in builder_traits}

    def champion_trait_chips(champ_name: str) -> list[dict]:
        """[{"name","slug"}] for a champion's real traits (same icons as
        the Team Builder) -- used on the champion sheet and its hover
        tooltip, neither of which showed this before."""
        info = info_by_name.get(champ_name, {})
        return [{"name": t, "slug": trait_by_name[t]["slug"]} for t in info.get("traits", []) if t in trait_by_name]

    def compute_comp_traits(core_units: list[dict]) -> list[dict]:
        """Same active/next-threshold math as the Team Builder's client-side
        renderTraitPanel(), run once here instead: how many of this comp's
        core units share each trait, and whether that's enough to be active.
        Only traits with at least one unit are returned (a comp's incidental
        1-of-a-trait units still show, same as the Team Builder)."""
        counts: dict[str, int] = {}
        for u in core_units or []:
            for t in info_by_name.get(u["champion"], {}).get("traits", []):
                counts[t] = counts.get(t, 0) + 1
        rows = []
        for trait in builder_traits:
            count = counts.get(trait["name"], 0)
            if not count:
                continue
            effects = trait["effects"]  # ascending by min_units
            active_idx = -1
            for i, e in enumerate(effects):
                if count >= e["min_units"]:
                    active_idx = i
            next_min = effects[active_idx + 1]["min_units"] if active_idx + 1 < len(effects) else None
            rows.append({
                "name": trait["name"], "slug": trait["slug"], "count": count,
                "active": active_idx >= 0, "tier": active_idx if active_idx >= 0 else None,
                "next_min": next_min,
            })
        rows.sort(key=lambda r: (not r["active"], -r["count"]))
        return rows

    (DIST / "assets" / "data").mkdir(parents=True, exist_ok=True)
    (DIST / "assets" / "data" / "builder.json").write_text(
        json.dumps({
            "champions": builder_champions, "traits": builder_traits,
            "plannerHeader": PLANNER_HEADER, "setMutator": SET_MUTATOR,
        }, ensure_ascii=False), encoding="utf-8")

    # Same classification derive_comp() uses to pick a comp's carry (see
    # comp_signature.py) -- published below as its own data file so
    # MetaScope's worker (a live Riot-ID lookup for players we DON'T
    # already track, running comp derivation itself for an arbitrary game)
    # stays in lockstep with this exact site build, not a copy that can
    # drift out of sync.
    item_offense = classify_item_offense(SET_MUTATOR)

    def team_planner_code(core_units: list[dict]) -> str:
        slots = []
        for u in (core_units or [])[:10]:
            code = planner_codes.get(u["champion"])
            slots.append(f"{code:03x}" if code is not None else "000")
        while len(slots) < 10:
            slots.append("000")
        return PLANNER_HEADER + "".join(slots) + SET_MUTATOR

    by_region = load("tierlist_by_region.json") if (OUT / "tierlist_by_region.json").exists() else {"regions": {}}
    by_rank = load("tierlist_by_rank.json") if (OUT / "tierlist_by_rank.json").exists() else {"ranks": {}}

    all_comps_raw = combined["comps"]
    comps_filtered = filter_quality(all_comps_raw)
    comps_by_key = {c["key"]: c for c in all_comps_raw}

    region_raw_filtered = {r: filter_quality(payload["comps"]) for r, payload in by_region["regions"].items()}
    rank_raw_filtered = {b: filter_quality(payload["comps"]) for b, payload in by_rank["ranks"].items()}

    needed_items: set[str] = set()
    for pool in [comps_filtered, *region_raw_filtered.values(), *rank_raw_filtered.values()]:
        for c in pool:
            for u in c.get("core_units", []):
                needed_items.update(u.get("items") or [])
            for combo in c.get("item_combo_stats", []):
                needed_items.update(combo.get("items") or [])
    for champ in champion_stats["champions"]:
        for ti in champ.get("top_items", []):
            needed_items.add(ti["item"])
        for combo in champ.get("item_combo_stats", []):
            needed_items.update(combo.get("items") or [])
    item_image_map = build_item_image_map(needed_items, id_prefix="DA_")

    def champ_slug_and_download(name: str) -> str:
        slug = slugify(name)
        info = info_by_name.get(name)
        if info and info.get("icon"):
            images.champion(slug, info["icon"])
        return slug

    def item_slug_and_download(name: str) -> str:
        slug = slugify(name)
        url = item_image_map.get(name)
        if url:
            images.item(slug, url)
        return slug

    # ---- Leaderboard: real ladder sightings index (same as the Artifact's compSightings) ----
    comp_sightings: dict[str, list[dict]] = {}
    for region, rows in leaderboard_json["regions"].items():
        for p in rows:
            for g in p.get("recentComps", []):
                comp_sightings.setdefault(g["compKey"], []).append({
                    "region": region, "rank": p["rank"], "riot_id": p["riotId"],
                    "tier": p["tier"], "lp": p["leaguePoints"], "placement": g["placement"],
                })

    matchups_by_comp: dict[str, list[dict]] = {}
    for m in matchups_json["matchups"]:
        matchups_by_comp.setdefault(m["comp_a"], []).append(
            {"opp": m["comp_b"], "opp_label": m["comp_b_label"], "encounters": m["encounters"], "ahead": m["a_ahead_rate"]})
        matchups_by_comp.setdefault(m["comp_b"], []).append(
            {"opp": m["comp_a"], "opp_label": m["comp_a_label"], "encounters": m["encounters"], "ahead": m["b_ahead_rate"]})

    history_by_key: dict[str, list[dict]] = {}
    for snap in comp_history.get("snapshots", []):
        for key, row in snap.get("comps", {}).items():
            history_by_key.setdefault(key, []).append({"date": snap["date"], "avgPlacement": row["avgPlacement"]})
    for rows in history_by_key.values():
        rows.sort(key=lambda r: r["date"])

    def trend_for(key: str) -> dict | None:
        hist = history_by_key.get(key, [])
        if len(hist) < 2:
            return None
        prev, latest = hist[-2], hist[-1]
        delta = prev["avgPlacement"] - latest["avgPlacement"]
        if abs(delta) < 0.3:
            return {"state": "stable", "arrow": "=", "delta": abs(delta)}
        return {"state": "up" if delta > 0 else "down", "arrow": "▲" if delta > 0 else "▼", "delta": abs(delta)}

    # ---- Per-comp derived view-model ----
    def build_core_units_display(units: list[dict], carry: str | None) -> list[dict]:
        top_set = units_worth_itemizing(units, carry)
        out = []
        for u in units:
            is_top = u["champion"] in top_set
            complete = [i for i in (u.get("items") or []) if is_complete_item(i)]
            shown = complete[:3] if is_top else [i for i in complete if is_emblem(i)]
            out.append({
                "champion": u["champion"], "slug": champ_slug_and_download(u["champion"]),
                "cost": u.get("cost"), "three_star": (u.get("threeStarRate") or 0) >= 0.5, "is_top": is_top,
                "shown_items": [{"name": n, "slug": item_slug_and_download(n)} for n in shown],
            })
        return out

    def build_row_vm(c: dict) -> dict:
        """The fields a list row needs -- used directly for region/rank/tier
        list pages, and as the base build_comp_vm() extends with full fiche
        detail for the one canonical /compo/<slug>/ page per comp."""
        tier = c["tier"]
        carry = c.get("carry")
        core_display = build_core_units_display(c.get("core_units") or [], carry)
        return {
            "key": c["key"], "slug": slugify(c["key"]),
            "label": c["label"], "tier": tier, "tier_var": TIER_VAR.get(tier, "var(--gray)"),
            "playstyle_tag": c.get("playstyle_tag"), "playstyle_cat": playstyle_cat(c.get("playstyle_tag")),
            "display_label": f"{c['label']} {c['playstyle_tag']}" if c.get("playstyle_tag") else c["label"],
            "carry": carry, "carry_slug": champ_slug_and_download(carry) if carry else None,
            "core_units_display": core_display,
            # Ranked same as derive_comp() ranks them (most-activated first) --
            # traits[0] is this comp's single IDENTITY trait (same one baked
            # into `key`/`label`), used by the Glossary's family pages to find
            # "comps actually BUILT AROUND this family" rather than every comp
            # that merely has a unit or two carrying it as a minor tag.
            "traits": c.get("traits") or [],
            "avg_placement": c["avg_placement"], "top4_pct": pct(c["top4_rate"]),
            "play_count": c["play_count"], "play_rate": c.get("play_rate", 0),
            "contestation_index": c.get("contestation_index", 0), "contestation_level": c.get("contestation_level", "Low"),
            "level_badge_n": (re.search(r"\d+", c["level_badge"]).group() if c.get("level_badge") else None),
            "trend": trend_for(c["key"]),
            "planner_code": team_planner_code(c.get("core_units")),
            # Matches the Artifact's matchesSearch(): comp name, carry, and
            # every champion on the board -- so searching "renekton" finds
            # every comp featuring him even when he isn't the named carry.
            "search_blob": " ".join(filter(None, [
                c["label"], carry, c.get("playstyle_tag"), *[u["champion"] for u in core_display],
            ])).lower(),
        }

    def build_comp_vm(c: dict) -> dict:
        row = build_row_vm(c)
        core_display = row["core_units_display"]
        top_champs_in_order = [u["champion"] for u in core_display if u["is_top"]]

        combo_blocks = []
        for champ in top_champs_in_order:
            rows = [r for r in c.get("item_combo_stats", []) if r["champion"] == champ][:10]
            if not rows:
                continue
            combo_blocks.append({
                "champion": champ, "slug": champ_slug_and_download(champ),
                "rows": [{"item_icons": [{"name": n, "slug": item_slug_and_download(n)} for n in r["items"]],
                          "avg_placement": r["avgPlacement"]} for r in rows],
            })

        sightings = sorted(comp_sightings.get(c["key"], []), key=lambda s: s["placement"])[:20]

        mu_rows = sorted([m for m in matchups_by_comp.get(c["key"], []) if m["encounters"] >= 4],
                          key=lambda m: -m["encounters"])[:20]
        matchups = []
        for m in mu_rows:
            opp = comps_by_key.get(m["opp"])
            matchups.append({
                "side": "ahead" if m["ahead"] >= 0.5 else "behind",
                "opp_label": opp["label"] if opp else m["opp_label"],
                "opp_url_slug": slugify(m["opp"]),
                "opp_slug": champ_slug_and_download(opp["carry"]) if opp and opp.get("carry") else None,
                "encounters": m["encounters"], "pct": pct(m["ahead"]), "pct_int": round(m["ahead"] * 100),
            })

        variants_raw = c.get("board_variants") or []
        board_variants = []
        base_units = variants_raw[0]["units"] if variants_raw else []
        for v in variants_raw:
            removed = [u for u in base_units if u not in v["units"]]
            added = [u for u in v["units"] if u not in base_units]
            board_variants.append({
                "icons": [(champ_slug_and_download(u), u) for u in v["units"]],
                "removed": [(champ_slug_and_download(u), u) for u in removed],
                "added": [(champ_slug_and_download(u), u) for u in added],
                "share_pct": pct(v["share"]), "avg_placement": v["avgPlacement"],
            })

        bs = c.get("bonus_slots") or {}
        bonus_base = None
        bonus_groups = []
        if bs.get("coreSize"):
            bonus_base = {"core_size": bs["coreSize"], "avg_placement": bs.get("coreAvgPlacement"), "games": bs.get("coreGames")}
            if bs.get("plusOne"):
                bonus_groups.append({
                    "kind": "plus_one_title", "total_units": bs["coreSize"] + 1,
                    "rows": [{"icons": [(champ_slug_and_download(ch), ch) for ch in row["champions"]],
                              "names": " + ".join(row["champions"]), "avg_placement": row["avgPlacement"], "games": row["games"]}
                             for row in bs["plusOne"]],
                })
            if bs.get("plusTwo"):
                bonus_groups.append({
                    "kind": "plus_two_title", "total_units": bs["coreSize"] + 2,
                    "rows": [{"icons": [(champ_slug_and_download(ch), ch) for ch in row["champions"]],
                              "names": " + ".join(row["champions"]), "avg_placement": row["avgPlacement"], "games": row["games"]}
                             for row in bs["plusTwo"]],
                })

        similar = []
        for v in c.get("similar_variants") or []:
            similar.append({
                "label": v["label"], "carry": v.get("carry"),
                "carry_slug": champ_slug_and_download(v["carry"]) if v.get("carry") else None,
                "board_size": v["boardSize"], "play_count": v["playCount"], "avg_placement": v["avgPlacement"],
            })

        row.update({
            "item_combo_blocks": combo_blocks,
            "ladder_sightings": sightings,
            "matchups": matchups,
            "board_variants": board_variants,
            "bonus_base": bonus_base, "bonus_groups": bonus_groups,
            "similar_variants": similar,
            "comp_traits": compute_comp_traits(c.get("core_units")),
        })
        return row

    TIER_SORT = {"S": 0, "A": 1, "B": 2, "C": 3}

    def sorted_rows(raw_comps: list[dict]) -> list[dict]:
        rows = [build_row_vm(c) for c in raw_comps]
        rows.sort(key=lambda c: (TIER_SORT.get(c["tier"], 4), c["avg_placement"]))
        return rows

    print(f"Building {len(comps_filtered)} comp pages...")
    comp_vms = [build_comp_vm(c) for c in comps_filtered]
    comp_vms.sort(key=lambda c: (TIER_SORT.get(c["tier"], 4), c["avg_placement"]))
    # Only comps that passed the quality filter get a real /compo/<slug>/
    # page -- used below to decide whether a player's recent-game row links
    # to a real fiche or shows as plain (unlinked) text.
    comp_vm_by_key = {c["key"]: c for c in comp_vms}

    region_rows = {r: sorted_rows(rows) for r, rows in region_raw_filtered.items()}
    rank_rows = {b: sorted_rows(rows) for b, rows in rank_raw_filtered.items()}

    # ---- Champions ----
    def build_champion_vm(d: dict) -> dict:
        slug = champ_slug_and_download(d["id"])
        combos = (d.get("item_combo_stats") or [])[:10]
        rows_for_champ = [c for c in comp_vms if any(u["champion"] == d["id"] for u in c["core_units_display"])]
        order = {"S": 0, "A": 1, "B": 2, "C": 3}
        rows_for_champ.sort(key=lambda c: (order.get(c["tier"], 4), c["avg_placement"]))
        info = info_by_name.get(d["id"], {})
        return {
            "name": d["id"], "slug": slug, "tier": d.get("tier", "?"), "tier_var": TIER_VAR.get(d.get("tier"), "var(--gray)"),
            "pick_rate_pct": pct(d["pick_rate"]), "avg_placement": d["avg_placement"], "top4_pct": pct(d["top4_rate"]),
            "avg_star_level": d["avg_star_level"],
            "top_items": [{"name": ti["item"], "slug": item_slug_and_download(ti["item"])} for ti in (d.get("top_items") or [])[:3]],
            "ability_name": info.get("ability_name", ""), "ability_desc": info.get("ability_desc", ""),
            "traits": champion_trait_chips(d["id"]),
            "combo_rows": [
                {"item_icons": [{"name": n, "slug": item_slug_and_download(n)} for n in r["items"]],
                 "games": r["games"], "top4_pct": pct(r.get("top4Rate", 0)), "winrate_pct": pct(r.get("winRate", 0))}
                for r in combos
            ],
            "comps": [{"slug": c["slug"], "display_label": c["display_label"], "tier": c["tier"], "tier_var": c["tier_var"],
                       "avg_placement": c["avg_placement"], "top4_pct": c["top4_pct"]} for c in rows_for_champ],
        }

    champion_vms = [build_champion_vm(d) for d in champion_stats["champions"] if d.get("tier") != "?"]
    champion_vms.sort(key=lambda d: ({"S": 0, "A": 1, "B": 2, "C": 3}.get(d["tier"], 4), d["avg_placement"]))
    print(f"Building {len(champion_vms)} champion pages...")

    # ---- Hover-tooltip data for every ".champ-link-icon" on the site (ported
    # from the Artifact's currentChampions lookup) -- one shared static JSON
    # file instead of embedding this per page, fetched once client-side by
    # assets/js/champ-icons.js. Language-independent (numbers + item names
    # aren't translated), keyed by slug to match data-champ-slug. ----
    champion_tooltip_data = {
        d["slug"]: {
            "name": d["name"], "pick_rate_pct": d["pick_rate_pct"],
            "avg_placement": round(d["avg_placement"], 2), "avg_star_level": round(d["avg_star_level"], 1),
            "top_items": [ti["name"] for ti in d["top_items"]],
            "traits": d["traits"],
        }
        for d in champion_vms
    }

    # ==========================================================================
    # ---- Glossaire TFT: a static reference distinct from every tier-list
    # page above -- every real champion/family/item/augment in the set, not
    # just the ones with enough sample to rank. Only "Champions" reuses an
    # existing page set as-is (see below); Familles/Augments/Objets are new.
    # ==========================================================================

    # Only real champions with an actual /champions/<slug>/ fiche (tier != "?",
    # see champion_vms above) get linked to from anywhere in the Glossaire --
    # same page set the site already exposes, nothing new generated here, so
    # every "cliquable" icon the Glossaire promises really does resolve.
    ranked_champion_names = {d["name"] for d in champion_vms}
    glossary_champions = champion_vms

    # ---- Familles: full trait roster, each with a real explanation (see
    # build_family_docs), its real member champions, and the real comps
    # actually BUILT AROUND it (comp["traits"][0] == this trait -- see
    # build_row_vm's "traits" field). ----
    family_docs = build_family_docs(SET_MUTATOR)
    glossary_families = []
    for trait in builder_traits:
        doc = family_docs.get(trait["name"], {})
        member_infos = sorted(
            (info for info in raw_image_map.values() if trait["name"] in (info.get("traits") or [])),
            key=lambda info: (info.get("cost") or 0, info["name"]),
        )
        members = []
        for info in member_infos:
            name = info["name"]
            slug = champ_slug_and_download(name)
            members.append({"name": name, "slug": slug, "has_page": name in ranked_champion_names})
        family_comps = sorted(
            (c for c in comp_vms if c["traits"] and c["traits"][0] == trait["name"]),
            key=lambda c: (TIER_SORT.get(c["tier"], 4), c["avg_placement"]),
        )
        # Riot's own <row> order always matches ascending min_units (checked
        # across every Set 18 trait) -- zipped here, once, rather than in the
        # template, since a plain Jinja2 Environment has no zip() global.
        # Falls back to just the number with no flavor text if the two ever
        # come out different lengths, rather than mis-pairing them.
        bp_texts = doc.get("breakpoint_text", [])
        breakpoints = [
            {"min_units": e["min_units"], "text": bp_texts[i] if i < len(bp_texts) else ""}
            for i, e in enumerate(trait["effects"])
        ]
        glossary_families.append({
            "name": trait["name"], "slug": trait["slug"], "icon_slug": trait["slug"],
            "intro": doc.get("intro", ""), "breakpoints": breakpoints,
            "members": members, "comps": family_comps,
        })
    glossary_families.sort(key=lambda f: f["name"])

    # ---- Augments: one static reference page, grouped Silver -> Gold ->
    # Prismatic (see build_augment_data). No usage stats: Riot's Match-V1
    # doesn't expose which augments a participant took for this set at all
    # (see the existing "augments_note" i18n string) -- a purely static
    # reference is genuinely all real data supports here. ----
    glossary_augments_flat = []
    for a in build_augment_data(SET_MUTATOR):
        a_slug = slugify(a["clean_id"])
        if a["icon"]:
            images.augment(a_slug, a["icon"])
        glossary_augments_flat.append({"name": a["name"], "icon_slug": a_slug, "desc": a["desc"], "tier": a["tier"]})
    # Pre-grouped Silver -> Gold -> Prismatic rather than a template-side
    # {% groupby %}: Jinja2's groupby re-sorts groups alphabetically by key
    # ("Gold, Prismatic, Silver"), which would silently undo this exact
    # ordering build_augment_data() already sorted for.
    glossary_augment_groups = [
        {"tier": tier, "augments": [a for a in glossary_augments_flat if a["tier"] == tier]}
        for tier in ("Silver", "Gold", "Prismatic")
    ]

    # ---- Objets: every FINISHED item in the set (not just ones seen in real
    # matches, unlike item_image_map above), each with its real components
    # (for the hover tooltip) and, on its own fiche, the real champions who
    # get a high win rate holding it alone (see champion_stats.
    # build_item_champion_stats -- computed once, for the WHOLE sample, not
    # per-region/rank: see compute_full_payload's want_item_stats). ----
    item_champion_stats_raw = champion_stats.get("item_champion_stats", {})
    glossary_items = []
    for it in build_full_item_catalog(SET_MUTATOR, id_prefix="DA_"):
        slug = slugify(it["clean_id"])
        if it["icon"]:
            images.item(slug, it["icon"])
        composition = []
        for comp in it["composition"]:
            comp_slug = slugify(comp["clean_id"])
            if comp["icon"]:
                images.item(comp_slug, comp["icon"])
            composition.append({"name": comp["name"], "slug": comp_slug})
        champion_rows = []
        for row in item_champion_stats_raw.get(it["clean_id"], []):
            name = row["champion"]
            champion_rows.append({
                "name": name, "slug": champ_slug_and_download(name), "has_page": name in ranked_champion_names,
                "games": row["games"], "avg_placement": row["avgPlacement"],
                "top4_pct": pct(row["top4Rate"]), "winrate_pct": pct(row["winRate"]),
            })
        glossary_items.append({
            "name": it["name"], "slug": slug, "icon_slug": slug,
            "composition": composition, "desc": it["desc"], "champion_rows": champion_rows,
        })
    glossary_items.sort(key=lambda i: i["name"])

    # Small tooltip data file for item icons across the Glossary (composition
    # on hover) -- same pattern as champions.json above, fetched once by a
    # small addition to champ-icons.js rather than inlined per page.
    glossary_item_tooltip_data = {
        i["slug"]: {"name": i["name"], "composition": i["composition"]} for i in glossary_items
    }

    # ---- Leaderboard view-model (region display name filled in per-language
    # just before rendering -- everything else here is language-independent) ----
    REGION_NAMES = {
        "fr": {"EUW": "Europe Ouest (EUW)", "NA": "Amérique du Nord (NA)", "BR": "Brésil (BR)", "KR": "Corée (KR)"},
        "en": {"EUW": "West Europe (EUW)", "NA": "North America (NA)", "BR": "Brazil (BR)", "KR": "Korea (KR)"},
    }
    lb_regions_raw = []
    player_vms_by_region: dict[str, list[dict]] = {}
    for region, rows in leaderboard_json["regions"].items():
        if not rows:
            continue
        vm_rows = []
        players = []
        for p in rows[:100]:
            slug = player_url_slug(p["rank"], p["riotId"])
            form = []
            for placement in (p.get("recentPlacements") or [])[:5]:
                win = placement <= 4
                form.append({"cls": "win" if win else "loss", "label": "W" if win else "L", "placement": placement})
            while len(form) < 5:
                form.append({"cls": "empty", "label": "–", "placement": None})
            vm_rows.append({"rank": p["rank"], "riot_id": p["riotId"], "tier": p["tier"], "lp": p["leaguePoints"],
                             "hot_streak": p.get("hotStreak", False), "form": form, "slug": slug})

            # ---- Player profile: real /player/<region>/<rank-slug>/ page,
            # opened from clicking this leaderboard row. Header repeats this
            # row's real stats plus a real winrate computed from wins/losses,
            # then the player's last 10 ranked games with the comp each one
            # was actually played -- same convention as every other comp
            # signature in the app. A recent game only links to a real comp
            # fiche when that comp passed the quality filter (has a real
            # /compo/ page); otherwise it's shown as plain text -- avoids
            # generating thin single-game stub pages for one-off comps. ----
            total = p["wins"] + p["losses"]
            wr = (p["wins"] / total) if total else 0
            all_recent = p.get("recentComps") or []
            recent_games = []
            for g in all_recent[:10]:
                cv = comp_vm_by_key.get(g["compKey"])
                carry = g.get("carry")
                match_id = g.get("matchId")
                has_analysis = bool(match_id and g.get("analysis"))
                recent_games.append({
                    "placement": g["placement"], "is_win": g["placement"] <= 4,
                    "label": cv["display_label"] if cv else g.get("compLabel", ""),
                    "carry_slug": champ_slug_and_download(carry) if carry else None,
                    "carry": carry,
                    "comp_slug": cv["slug"] if cv else None,
                    "match_id": match_id, "has_analysis": has_analysis,
                })

            # ---- MetaScope habits: real signal from this same recent-games
            # sample, no separate collection needed. "Reroll lover" needs a
            # real majority, not one lucky reroll comp; "most played" only
            # calls out a comp actually repeated (count >= 2), never pads
            # out to 2 with one-off games. ----
            placements = [g["placement"] for g in all_recent if g.get("placement")]
            avg_placement = round(sum(placements) / len(placements), 2) if placements else None
            reroll_games = sum(1 for g in all_recent if (comp_vm_by_key.get(g["compKey"]) or {}).get("playstyle_cat") == "Reroll"
                                or "Reroll" in (g.get("compLabel") or ""))
            is_reroll_lover = len(all_recent) >= 5 and reroll_games / len(all_recent) >= 0.5
            comp_counts = Counter(g["compKey"] for g in all_recent if g.get("compKey"))
            top_played = []
            for key, count in comp_counts.most_common(2):
                if count < 2:
                    break
                sample = next(g for g in all_recent if g["compKey"] == key)
                cv = comp_vm_by_key.get(key)
                top_played.append({
                    "label": cv["display_label"] if cv else sample.get("compLabel", ""),
                    "count": count, "carry_slug": champ_slug_and_download(sample["carry"]) if sample.get("carry") else None,
                    "comp_slug": cv["slug"] if cv else None,
                })

            players.append({
                "region": region, "rank": p["rank"], "riot_id": p["riotId"], "tier": p["tier"],
                "lp": p["leaguePoints"], "wins": p["wins"], "losses": p["losses"],
                "hot_streak": p.get("hotStreak", False), "winrate_pct": pct(wr),
                "initials": initials(p["riotId"]), "slug": slug, "recent_games": recent_games,
                "avg_placement": avg_placement, "is_reroll_lover": is_reroll_lover, "top_played": top_played,
                # Kept only to build each game's analysis page further down
                # (needs the raw analysis payload, not the trimmed recent_games
                # view-model above) -- never passed to a template directly.
                "_raw_recent": all_recent,
            })
        lb_regions_raw.append({"code": region, "rows": vm_rows})
        player_vms_by_region[region] = players

    # ---- MetaScope: "Analyser la partie" -- one static page per player per
    # recent game that has a real analysis payload (see pipeline.py's
    # _run_leaderboard: build_report() already ran for these at collection
    # time, same engine as the local analyze_app.py tool, so no live API
    # call happens here, just icon/slug resolution). Insight text itself is
    # French-only for now (analysis.py was written before this site went
    # bilingual) -- shown as-is on the EN page too, with a short note, rather
    # than holding the whole feature back on translating every insight
    # sentence into a parameterized i18n entry. ----
    def build_game_analysis_vm(g: dict) -> dict | None:
        analysis = g.get("analysis")
        if not g.get("matchId") or not analysis:
            return None
        cv = comp_vm_by_key.get(g["compKey"])
        lobby_vm = []
        for entry in analysis.get("lobby", []):
            opp_cv = comp_vm_by_key.get(entry["compKey"])
            lobby_vm.append({
                **entry,
                "carry_slug": champ_slug_and_download(entry["carry"]) if entry.get("carry") else None,
                "comp_slug": opp_cv["slug"] if opp_cv else None,
                "comp_label": opp_cv["display_label"] if opp_cv else entry["compLabel"],
                "is_counter": entry.get("counterRate") is not None and entry["counterRate"] >= 0.55 and entry.get("encounters", 0) >= 4,
            })
        units_vm = []
        for u in analysis.get("units", []):
            units_vm.append({
                "champion": u["champion"], "slug": champ_slug_and_download(u["champion"]),
                "cost": u.get("cost"), "star": u.get("star"),
                "items": [{"name": n, "slug": item_slug_and_download(n)} for n in (u.get("items") or [])],
            })
        return {
            "match_id": g["matchId"], "placement": g["placement"],
            "comp_label": cv["display_label"] if cv else g.get("compLabel", ""),
            "comp_slug": cv["slug"] if cv else None,
            "carry": g.get("carry"), "carry_slug": champ_slug_and_download(g["carry"]) if g.get("carry") else None,
            "level": analysis.get("level"), "gold_left": analysis.get("goldLeft"), "last_round": analysis.get("lastRound"),
            "units": units_vm, "insights": analysis.get("insights") or [], "lobby": lobby_vm,
        }

    # ---- World Stat: elo-over-time chart, top 10 by region, top comps by
    # region -- reached from a button on the Leaderboard. All three pieces
    # are derived from data already loaded (leaderboard_history.json,
    # leaderboard.json's top_comps), same as the Artifact's version. ----
    ws_snapshots = leaderboard_history.get("snapshots", [])
    ws_regions_present = [r for r in ["EUW", "NA", "BR", "KR"] if leaderboard_json["regions"].get(r)]
    latest_snapshot = ws_snapshots[-1] if ws_snapshots else None
    legend = [{"name": REGION_SHORT.get(r, r), "color": REGION_COLOR_VAR[r],
               "value": (f"{round(latest_snapshot['avgLp'][r])} LP" if latest_snapshot and latest_snapshot.get("avgLp", {}).get(r) is not None else "—")}
              for r in ws_regions_present]

    region_cols = []
    for r in (ws_regions_present or list(REGION_SHORT.keys())):
        top10 = (leaderboard_json["regions"].get(r) or [])[:10]
        players = []
        for p in top10:
            total = p["wins"] + p["losses"]
            wr = p["wins"] / total if total else 0
            players.append({"rank": p["rank"], "riot_id": p["riotId"], "tier": p["tier"], "wr_pct": pct(wr)})
        region_cols.append({"name": REGION_SHORT.get(r, r), "color": REGION_COLOR_VAR.get(r, "var(--gray)"), "players": players})

    comp_cols = []
    top_comps = leaderboard_json.get("top_comps", {})
    for r in (ws_regions_present or list(REGION_SHORT.keys())):
        rows = top_comps.get(r, [])
        comps = [{"slug": champ_slug_and_download(row["carry"]), "carry": row["carry"], "label": row["label"],
                  "count": row["count"], "avg_placement": row["avgPlacement"]} for row in rows]
        comp_cols.append({"name": REGION_SHORT.get(r, r), "color": REGION_COLOR_VAR.get(r, "var(--gray)"), "comps": comps})

    # ---- Patch notes (same hand-written content as the Artifact's i18n
    # dict -- real hand-translated English, not machine-translated) ----
    PATCHES = {
        "fr": [
            {"version": "18.1d", "tag": "Équilibrage", "date": "31 août 2026", "title": "Premier vrai passage d'équilibrage sur Enchanted Wilds",
             "summary": "Première vraie mise à jour d'équilibrage depuis le lancement du Set 18 (les 18.1a/18.1b des 27-28 août n'avaient touché que des bugs). Cassiopeia, Ahri, Cinderling, Master Yi et Morgana affaiblis ; Draven, Soraka, Amumu, Elder Dragon et Lux renforcés — Lux reçoit les deux à la fois (dégâts du sort en hausse, bonus Lunaire en baisse). Le palier Riftbeast (7) est légèrement réduit. Suivie le 1er septembre d'une série de correctifs : mauvais placement affiché en fin de partie classée pour les 1ers/2èmes, dégâts vrais de l'augment « Soul Awakening » qui ne s'appliquaient qu'aux dégâts d'attaque, un bug de matchmaking pouvant refaire tomber deux joueurs l'un contre l'autre deux manches de suite, et plusieurs autres correctifs mineurs (Adaptor, Alune, icônes Master of All Origins, dette de vie en Double Up).",
             "buffs": [
                 {"champion": "Amumu", "text": "Mana : 30/140 → 30/125 · Soin (% PV max) : 2,2 % → 2,5 %"},
                 {"champion": "Soraka", "text": "Dégâts initiaux à l'étoile : 190/285 → 225/335"},
                 {"champion": "Draven", "text": "Mana : 0/120 → 0/110 · Vitesse d'attaque de base : 0,8 → 0,85"},
                 {"champion": "Elder Dragon", "text": "Dégâts d'attaque de base : 115 → 125"},
                 {"champion": "Lux", "text": "Dégâts du sort : 330/520 → 355/550"},
             ],
             "nerfs": [
                 {"champion": "Cassiopeia", "text": "Dégâts du sort : 440/660/1050 → 400/600/950"},
                 {"champion": "Ahri", "text": "Dégâts du sort : 450/675 → 425/640"},
                 {"champion": "Cinderling", "text": "Dégâts d'attaque de base : 45 → 40 · Dégâts du sort : 340/510/765/1300 → 310/465/700/1200"},
                 {"champion": "Master Yi", "text": "Résistances : 60 → 55"},
                 {"champion": "Morgana", "text": "Mana : 0/60 → 0/65"},
                 {"champion": "Lux", "text": "Bonus de dégâts Lunaire : 10 % → 8 %"},
                 {"trait": "Riftbeast (7)", "text": "Bonus AD/AP/VA : 6 % → 5 %"},
             ],
             "url": "https://tftguide.org/en/patch-notes/18.1d"},
            {"version": "18.1", "tag": "Set 18", "date": "25 août 2026", "title": "Enchanted Wilds arrive sur le jeu en direct",
             "summary": "Lancement du Set 18 « Enchanted Wilds » (Riftbeasts, Elderwood, la nouvelle mécanique Wisps) et bascule du moteur du jeu de Hextech vers Unreal Engine. Le Set 17 « Space Gods » reste jouable en parallèle quelques patchs de plus. Plusieurs correctifs ont suivi les 27 et 28 août : fuites mémoire, temps de chargement, et une réactivation de la file Double Up après un bug l'ayant fait désactiver temporairement.",
             "url": "https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1/"},
            {"version": "17.9", "tag": "Équilibrage", "date": "11 août 2026", "title": "Dernier patch dédié à Space Gods",
             "summary": "Dernier patch d'équilibrage propre au Set 17 avant l'arrivée d'Enchanted Wilds le 26 août. Refonte du trait Shepherd (mana, bouclier, dégâts d'échelle), gros changement de courbe risque/récompense sur Twisted Fate, et buffs sur Gwen et Milio.",
             "url": "https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-17-9/"},
            {"version": "17.8", "tag": "Contenu", "date": "28 juillet 2026", "title": "Choncc's Classic Treasure",
             "summary": "Le mode « Choncc's Lore & Legends » devient « Choncc's Classic Treasure » avec des éléments classiques de League (monstres PvE, tribunal de Kayle, anciens objets comme Heart of Gold). Petits ajustements d'équilibrage sur Space Gods, et Enchanted Wilds (Set 18) arrive en PBE le même jour.",
             "url": "https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-17-8/"},
        ],
        "en": [
            {"version": "18.1d", "tag": "Balance", "date": "August 31, 2026", "title": "First real balance pass on Enchanted Wilds",
             "summary": "The first real balance update since Set 18 launched (18.1a/18.1b on August 27-28 only touched bugs). Cassiopeia, Ahri, Cinderling, Master Yi and Morgana got weaker; Draven, Soraka, Amumu, Elder Dragon and Lux got stronger — Lux gets both at once (spell damage up, Lunar damage amp down). The Riftbeast (7) tier was trimmed slightly. Followed on September 1 by a round of bug fixes: the end-of-game screen showing the wrong final placement for 1st/2nd in Ranked, the “Soul Awakening” augment's true damage only applying to attack damage instead of ability damage too, a matchmaking issue that could pit the same two players against each other two rounds in a row, and several smaller fixes (Adaptor, Alune, Master of All Origins icons, Double Up life debt).",
             "buffs": [
                 {"champion": "Amumu", "text": "Mana: 30/140 → 30/125 · Heal (% max HP): 2.2% → 2.5%"},
                 {"champion": "Soraka", "text": "Initial star damage: 190/285 → 225/335"},
                 {"champion": "Draven", "text": "Mana: 0/120 → 0/110 · Base attack speed: 0.8 → 0.85"},
                 {"champion": "Elder Dragon", "text": "Base AD: 115 → 125"},
                 {"champion": "Lux", "text": "Spell damage: 330/520 → 355/550"},
             ],
             "nerfs": [
                 {"champion": "Cassiopeia", "text": "Spell damage: 440/660/1050 → 400/600/950"},
                 {"champion": "Ahri", "text": "Spell damage: 450/675 → 425/640"},
                 {"champion": "Cinderling", "text": "Base AD: 45 → 40 · Spell damage: 340/510/765/1300 → 310/465/700/1200"},
                 {"champion": "Master Yi", "text": "Resists: 60 → 55"},
                 {"champion": "Morgana", "text": "Mana: 0/60 → 0/65"},
                 {"champion": "Lux", "text": "Lunar damage amp: 10% → 8%"},
                 {"trait": "Riftbeast (7)", "text": "AD/AP/AS bonus: 6% → 5%"},
             ],
             "url": "https://tftguide.org/en/patch-notes/18.1d"},
            {"version": "18.1", "tag": "Set 18", "date": "August 25, 2026", "title": "Enchanted Wilds goes live",
             "summary": "Set 18 “Enchanted Wilds” launches (Riftbeasts, Elderwood, the new Wisps mechanic) alongside the game's engine switch from Hextech to Unreal Engine. Set 17 “Space Gods” stays playable in parallel for a few more patches. Several hotfixes followed on August 27 and 28: memory leaks, load times, and Double Up re-enabled after a bug had temporarily disabled the queue.",
             "url": "https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1/"},
            {"version": "17.9", "tag": "Balance", "date": "August 11, 2026", "title": "Last patch dedicated to Space Gods",
             "summary": "Last Set-17-only balance patch before Enchanted Wilds arrives on August 26. Shepherd trait rework (mana, shield, scaling damage), a big risk/reward curve change on Twisted Fate, and buffs to Gwen and Milio.",
             "url": "https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-17-9/"},
            {"version": "17.8", "tag": "Content", "date": "July 28, 2026", "title": "Choncc's Classic Treasure",
             "summary": "The “Choncc's Lore & Legends” mode becomes “Choncc's Classic Treasure” with classic League elements (PvE monsters, Kayle's court, old items like Heart of Gold). Small balance adjustments to Space Gods, and Enchanted Wilds (Set 18) hits PBE the same day.",
             "url": "https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-17-8/"},
        ],
    }

    # ---- Resolve a champion icon for every buff/nerf line item (trait-only
    # entries like Riftbeast have no icon), and build a per-champion balance
    # history (buffs/nerfs across ALL patches, most-recent-first since
    # PATCHES itself is already ordered that way) for the champion sheet's
    # own "Balance history" section. Champion names are identical between
    # languages (real proper nouns from the game), only each entry's `text`
    # differs, so history has to stay keyed per-language even though the
    # icon/slug resolution below only needs to happen once. ----
    balance_history_by_lang: dict[str, dict[str, list[dict]]] = {lang: {} for lang in PATCHES}
    for lang, patch_list in PATCHES.items():
        for p in patch_list:
            for kind in ("buffs", "nerfs"):
                for item in p.get(kind, []):
                    champ = item.get("champion")
                    item["slug"] = champ_slug_and_download(champ) if champ else None
                    if champ:
                        balance_history_by_lang[lang].setdefault(champ, []).append({
                            "version": p["version"], "date": p["date"], "kind": kind[:-1], "text": item["text"],
                        })

    # ---- Render: every page renders twice, once per language. French stays
    # at the URL root (default, matches the site's existing audience); English
    # gets a real /en/ prefix -- its own crawlable pages with their own
    # hreflang-linked URL, not a client-side toggle over one page. ----
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=True)
    env.globals["star_svg"] = STAR_SVG
    env.globals["copy_svg"] = COPY_SVG
    env.globals["t"] = translate
    env.globals["SET_LABEL"] = SET_LABEL
    # Cache-buster for the one stylesheet URL every page shares: without it,
    # a CSS-only change (like this session's icon-size fix) never reaches a
    # browser that already cached style.css from an earlier visit -- caught
    # live: a rule was correctly in the deployed file but getComputedStyle
    # still showed the pre-fix value because the CSSOM itself was stale.
    # Changes on every build (not tied to data freshness) since template/CSS
    # edits often ship without a backend data refresh.
    env.globals["css_v"] = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    # Not a builtin on a plain jinja2.Environment (only Flask registers this)
    # -- needed to safely embed a translated string inside an inline <script>.
    # Must return Markup (safe), not a plain str: with autoescape=True a
    # plain str would get HTML-escaped a SECOND time after json.dumps already
    # quoted it, turning its `"` into `&quot;` -- which the browser leaves
    # un-decoded inside <script> text (it's not parsed as HTML there),
    # corrupting the string instead of just being redundant.
    env.filters["tojson"] = lambda v: Markup(json.dumps(v))

    LANGS = ["fr", "en"]

    def lang_url(url_path: str, lang: str) -> str:
        parts = [p for p in url_path.strip("/").split("/") if p]
        if lang == "en":
            parts = ["en", *parts]
        return "/" + "/".join(parts) + "/" if parts else "/"

    def dist_path_for(url_path: str, lang: str) -> Path:
        parts = [p for p in lang_url(url_path, lang).strip("/").split("/") if p]
        return Path(DIST, *parts, "index.html") if parts else DIST / "index.html"

    def rel_prefix_for(url_path: str, lang: str) -> str:
        depth = len([p for p in lang_url(url_path, lang).strip("/").split("/") if p])
        return "../" * depth

    def canonical_for(url_path: str, lang: str) -> str:
        u = lang_url(url_path, lang)
        return BASE_URL if u == "/" else BASE_URL + u.strip("/") + "/"

    def render(template_name: str, url_path: str, lang: str, **ctx) -> None:
        tpl = env.get_template(template_name)
        other = "en" if lang == "fr" else "fr"
        html = tpl.render(root=rel_prefix_for(url_path, lang), lang=lang,
                           canonical=canonical_for(url_path, lang), alt_canonical=canonical_for(url_path, other), alt_lang=other,
                           generated_at=combined["generated_at"][:10], set_name=combined["set"], **ctx)
        out_path = dist_path_for(url_path, lang)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")

    total_matches = combined["sample"]["total_matches"]

    CANON_RANK_ORDER = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]

    def rank_sort_key(key: str) -> int:
        idxs = [CANON_RANK_ORDER.index(p) for p in key.split("_") if p in CANON_RANK_ORDER]
        return min(idxs) if idxs else 999

    available_regions = [r for r in ["EUW", "NA", "BR", "KR"] if region_rows.get(r)]
    available_ranks = sorted([b for b in rank_rows if rank_rows.get(b)], key=rank_sort_key)

    def region_root(r: str) -> str:
        return f"/region/{r.lower()}/"

    def rank_root(b: str) -> str:
        return f"/rank/{slugify(b)}/"

    def scope_root(kind: str, key: str | None) -> str:
        if kind == "region":
            return region_root(key)
        if kind == "rank":
            return rank_root(key)
        return "/"

    print("Building comp / champion / list pages (FR + EN)...")
    for lang in LANGS:
        render("champions_list.html", "/champions/", lang, active_nav="champions", champions=champion_vms)

        # ---- Glossaire ----
        render("glossary_index.html", "/glossaire/", lang, active_nav="glossary", counts={
            "champions": len(glossary_champions), "families": len(glossary_families),
            "augments": len(glossary_augments_flat), "items": len(glossary_items),
        })
        render("glossary_champions.html", "/glossaire/champions/", lang, active_nav="glossary", champions=glossary_champions)
        render("glossary_families.html", "/glossaire/familles/", lang, active_nav="glossary", families=glossary_families)
        for f in glossary_families:
            render("glossary_family_detail.html", f"/glossaire/familles/{f['slug']}/", lang, active_nav="glossary", f=f)
        render("glossary_augments.html", "/glossaire/augments/", lang, active_nav="glossary", augment_groups=glossary_augment_groups)
        render("glossary_items.html", "/glossaire/objets/", lang, active_nav="glossary", items=glossary_items)
        for it in glossary_items:
            render("glossary_item_detail.html", f"/glossaire/objets/{it['slug']}/", lang, active_nav="glossary", it=it)

        lb_regions = [{"code": r["code"], "name": REGION_NAMES[lang].get(r["code"], r["code"]),
                       "rows": [{**row, "form": [{**sq, "title": (translate(lang, "placement_colon", sq["placement"]) if sq["placement"] is not None else "")} for sq in row["form"]]}
                                for row in r["rows"]]}
                      for r in lb_regions_raw]
        render("leaderboard.html", "/leaderboard/", lang, active_nav="leaderboard", regions=lb_regions)
        render("world_stat.html", "/leaderboard/world-stat/", lang, active_nav="leaderboard",
               elo_chart_svg=build_elo_chart_svg(ws_snapshots, ws_regions_present, lang), legend=legend, single_point=len(ws_snapshots) == 1,
               region_cols=region_cols, comp_cols=comp_cols)
        render("patch_notes.html", "/patch-notes/", lang, active_nav="patchnotes", patches=PATCHES[lang])
        render("metascope.html", "/metascope/", lang, active_nav="metascope")
        render("team_builder.html", "/team-builder/", lang, active_nav="builder")

        for c in comp_vms:
            comp_url = canonical_for(f"/compo/{c['slug']}/", lang)
            comp_headline = f"{c['display_label']} — Tier {c['tier']} ({SET_LABEL})"
            comp_desc = translate(lang, "faq_comp_tier_a", c["display_label"], c["tier"],
                                   f"{c['avg_placement']:.2f}", c["top4_pct"], c["play_count"])
            article_schema = {
                "@context": "https://schema.org", "@type": "Article",
                "headline": comp_headline, "description": comp_desc,
                "datePublished": combined["generated_at"][:10], "dateModified": combined["generated_at"][:10],
                "mainEntityOfPage": {"@type": "WebPage", "@id": comp_url},
                "author": {"@type": "Organization", "name": "BrokenMeta.gg"},
                "publisher": {"@type": "Organization", "name": "BrokenMeta.gg"},
            }
            if c.get("carry_slug"):
                article_schema["image"] = f"{BASE_URL}assets/champions/{c['carry_slug']}.png"
            faq_schema = {
                "@context": "https://schema.org", "@type": "FAQPage",
                "mainEntity": [{
                    "@type": "Question", "name": translate(lang, "faq_comp_tier_q", c["display_label"]),
                    "acceptedAnswer": {"@type": "Answer", "text": comp_desc},
                }],
            }
            render("comp.html", f"/compo/{c['slug']}/", lang, active_nav="comps", c=c,
                   article_schema=article_schema, faq_schema=faq_schema)

        # ---- Player profile pages: one per leaderboard row, opened from
        # the leaderboard table (see player.html + leaderboard.html link) ----
        for region, players in player_vms_by_region.items():
            region_name = REGION_NAMES[lang].get(region, region)
            for p in players:
                render("player.html", f"/player/{region.lower()}/{p['slug']}/", lang, active_nav="leaderboard",
                       p=p, region_name=region_name)
                for g in p["_raw_recent"]:
                    game_vm = build_game_analysis_vm(g)
                    if game_vm:
                        render("game_analysis.html", f"/player/{region.lower()}/{p['slug']}/match/{game_vm['match_id']}/",
                               lang, active_nav="leaderboard", g=game_vm, player=p, region_name=region_name)
        for d in champion_vms:
            render("champion.html", f"/champions/{d['slug']}/", lang, active_nav="champions", d=d,
                   balance_history=balance_history_by_lang[lang].get(d["name"], []))

        # ---- Région / Rang: real pages per slice (not a JS data blob) ----
        # Region and rank are two ALTERNATE ways to slice the same dataset
        # (mirrors the Artifact: picking one is mutually exclusive with the
        # other), so a scope is (kind, key) with kind in {'all','region','rank'}.
        # Every scope gets the same shape: one light overview page (tier
        # previews, like the homepage) + one full list page per tier that
        # actually has comps.
        def scope_chip_lists(kind: str, key: str | None, tier: str | None, _lang=lang):
            def with_tier(base: str) -> str:
                return base if tier is None else base + f"tier/{tier.lower()}/"

            region_chips = [{"label": translate(_lang, "region_all"), "href": with_tier("/"), "active": kind != "region"}]
            for r in available_regions:
                region_chips.append({"label": REGION_SHORT.get(r, r), "href": with_tier(region_root(r)), "active": kind == "region" and key == r})

            rank_chips = [{"label": translate(_lang, "rank_all"), "href": with_tier("/"), "active": kind != "rank"}]
            for b in available_ranks:
                rank_chips.append({"label": rank_bracket_label(b, _lang), "href": with_tier(rank_root(b)), "active": kind == "rank" and key == b})

            return region_chips, rank_chips

        def render_scope(kind: str, key: str | None, rows: list[dict], scope_label: str, _lang=lang) -> None:
            root_path = scope_root(kind, key)
            HOMEPAGE_PREVIEW_PER_TIER = 15
            tier_groups = []
            for tier in ["S", "A", "B", "C"]:
                tier_rows = [c for c in rows if c["tier"] == tier]
                if tier_rows:
                    tier_groups.append({"tier": tier, "total": len(tier_rows), "preview": tier_rows[:HOMEPAGE_PREVIEW_PER_TIER]})

            region_chips, rank_chips = scope_chip_lists(kind, key, None)
            suffix = f" — {scope_label}" if scope_label else ""
            title_suffix = "" if not scope_label else f" — {scope_label}"
            # Structured data (schema.org ItemList) for the tier list this page
            # actually shows -- gives Google (rich results) and AI answer
            # engines a clean, unambiguous "here are the top TFT Set 18 comps"
            # summary to lift, instead of having to parse the visual layout.
            list_name = f"{SET_LABEL} Tier List{title_suffix}"
            item_list_schema = {
                "@context": "https://schema.org", "@type": "ItemList", "name": list_name,
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": c["display_label"],
                     "url": canonical_for(f"/compo/{c['slug']}/", _lang)}
                    for i, c in enumerate(c for group in tier_groups for c in group["preview"])
                ],
            }
            # A short, real-data FAQ on the true homepage only (not every
            # region/rank scope variant, to avoid near-duplicate FAQ text
            # across dozens of pages): both a classic featured-snippet bait
            # and a clean, quotable answer for AI answer engines (GEO).
            faq = None
            if kind == "all" and rows:
                top = rows[0]
                matches_str = f"{total_matches:,}" if _lang == "en" else f"{total_matches:,}".replace(",", " ")
                faq = {
                    "q": translate(_lang, "faq_best_comp_q"),
                    "a": translate(_lang, "faq_best_comp_a", top["display_label"], top["tier"],
                                   f"{top['avg_placement']:.2f}", top["top4_pct"], matches_str),
                }
            render("overview.html", root_path, _lang,
                   active_nav="comps",
                   page_title=f"BrokenMeta.gg | {SET_LABEL} Tier List{title_suffix} — {len(rows)} compositions" if _lang == "fr"
                              else f"BrokenMeta.gg | {SET_LABEL} Tier List{title_suffix} — {len(rows)} comps",
                   page_description=f"Tier list Teamfight Tactics Set 18{title_suffix} : {len(rows)} compositions, données réelles Riot Match-V1." if _lang == "fr"
                                     else f"Teamfight Tactics Set 18 tier list{title_suffix}: {len(rows)} real ranked comps, real Riot Match-V1 data.",
                   h1=f"Tier List{title_suffix} — Teamfight Tactics Set 18",
                   intro=translate(_lang, "home_intro", len(rows), f"{total_matches:,}" if _lang == "en" else f"{total_matches:,}".replace(",", " ")) if kind == "all"
                         else translate(_lang, "scope_intro", len(rows), suffix),
                   tier_groups=tier_groups, region_chips=region_chips, rank_chips=rank_chips,
                   tier_href=lambda t, _root=root_path: _root + f"tier/{t.lower()}/",
                   item_list_schema=item_list_schema, faq=faq)

            for group in tier_groups:
                tier = group["tier"]
                tier_rows = [c for c in rows if c["tier"] == tier]
                cats = sorted({c["playstyle_cat"] for c in tier_rows if c["playstyle_cat"]},
                              key=lambda x: ["Reroll", "Fast", "Slow"].index(x) if x in ["Reroll", "Fast", "Slow"] else 9)
                region_chips_t, rank_chips_t = scope_chip_lists(kind, key, tier)
                tier_url = root_path + f"tier/{tier.lower()}/"
                render("list_page.html", tier_url, _lang,
                       active_nav="comps",
                       page_title=f"BrokenMeta.gg | Tier {tier}{title_suffix} — {len(tier_rows)} compositions | TFT Set 18" if _lang == "fr"
                                  else f"BrokenMeta.gg | Tier {tier}{title_suffix} — {len(tier_rows)} comps | TFT Set 18",
                       page_description=f"Compositions Tier {tier}{title_suffix} sur Teamfight Tactics Set 18 ({len(tier_rows)} compos), données réelles." if _lang == "fr"
                                         else f"Tier {tier}{title_suffix} comps on Teamfight Tactics Set 18 ({len(tier_rows)} comps), real data.",
                       h1=f"Tier {tier}{title_suffix} — Teamfight Tactics Set 18",
                       intro=translate(_lang, "tier_scope_intro", len(tier_rows), tier, suffix),
                       comps=tier_rows, type_cats=cats,
                       region_chips=region_chips_t, rank_chips=rank_chips_t)

        render_scope("all", None, comp_vms, "")
        for r in available_regions:
            render_scope("region", r, region_rows[r], REGION_SHORT.get(r, r))
        for b in available_ranks:
            render_scope("rank", b, rank_rows[b], rank_bracket_label(b, lang))

    # ---- CSS, favicon ----
    (DIST / "assets" / "css").mkdir(parents=True, exist_ok=True)
    css = (ROOT / "style_base.css").read_text(encoding="utf-8")
    css += """
  .page-h1 { font-family: 'Cal Sans', sans-serif; font-size: 26px; text-transform: uppercase; letter-spacing: 0.01em; margin: 6px 0 10px; }
  .page-intro { font-size: 13.5px; color: var(--text-dim); line-height: 1.6; max-width: 720px; margin: 0 0 22px; }
  a.comp-row, a.champ-comp-row { text-decoration: none; color: inherit; }
  /* .tier-filters never needed to wrap in the Artifact (S/A/B/C, single-word
     rank labels) -- this site's real Région/Rang chips can be two-word
     labels ("Or-Émeraude") that overflow a narrow viewport without this. */
  .tier-filters { flex-wrap: wrap; }

  /* Overlay TFT badge (Overwolf project CTA, ported from the Artifact) --
     inert on purpose, no download link exists yet. (.navbar-right itself
     lives only in style_base.css now -- this exact duplicate used to sit
     here too and silently won the cascade over that file's responsive
     @media rule, since it came later in the concatenated stylesheet and
     wasn't wrapped in a media query. Same class of bug as the .overlay-cta
     cache issue from an earlier session: two copies of one rule, only one
     kept up to date.) */
  .overlay-cta { display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.14); color: rgba(255,255,255,0.45); padding: 6px 8px 6px 10px; cursor: not-allowed; }
  .overlay-cta svg { width: 13px; height: 13px; stroke: rgba(255,255,255,0.45); fill: none; stroke-width: 2.2; }
  .overlay-cta .cta-label { font-family: 'Cal Sans', sans-serif; font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase; }
  .overlay-cta .cta-soon { font-family: 'Space Mono', monospace; font-size: 9px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; background: rgba(255,255,255,0.12); color: rgba(255,255,255,0.6); padding: 2px 6px; margin-left: 2px; }

  /* FR/EN toggle -- real separate pages (hreflang-linked), this just jumps
     between the current page's two language URLs. */
  .lang-toggle { display: flex; border: 1px solid var(--border-bright); flex: none; }
  .lang-btn { display: block; background: var(--row); border: none; color: var(--text-faint); font-family: 'Space Mono', monospace; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; padding: 6px 10px; text-decoration: none; }
  .lang-btn + .lang-btn { border-left: 1px solid var(--border-bright); }
  .lang-btn[data-active="true"] { background: var(--cyan); color: #0b0221; }
  .lang-btn:not([data-active="true"]):hover { color: var(--cream); }

  /* Balance-patch buff/nerf columns on the Patch Notes cards. */
  .patch-balance-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 12px; }
  @media (max-width: 560px) { .patch-balance-grid { grid-template-columns: 1fr; } }
  .patch-balance-label { font-family: 'Space Mono', monospace; font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
  .patch-balance-col[data-kind="buff"] .patch-balance-label { color: var(--good); }
  .patch-balance-col[data-kind="nerf"] .patch-balance-label { color: var(--warn); }
  .patch-balance-col ul { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 6px; }
  .patch-balance-col li { display: flex; align-items: center; gap: 8px; color: var(--text-dim); font-size: 12.5px; line-height: 1.4; }
  .patch-balance-col li b { color: var(--cream); }
  .patch-balance-icon { width: 32px; height: 32px; border: 1px solid var(--border-bright); object-fit: cover; flex: none; }

  /* Champion sheet's "Balance history" list. */
  .balance-history-list { display: flex; flex-direction: column; gap: 8px; }
  .balance-history-row { display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: var(--row); border: 1px solid var(--border); flex-wrap: wrap; }
  .balance-history-kind { flex: none; width: 16px; text-align: center; font-size: 13px; }
  .balance-history-row[data-kind="buff"] .balance-history-kind { color: var(--good); }
  .balance-history-row[data-kind="nerf"] .balance-history-kind { color: var(--warn); }
  .balance-history-patch { flex: none; font-family: 'Space Mono', monospace; font-size: 11px; color: var(--cyan); }
  .balance-history-date { flex: none; font-family: 'Space Mono', monospace; font-size: 11px; color: var(--text-faint); }
  .balance-history-text { flex: 1; min-width: 200px; color: var(--text-dim); font-size: 12.5px; }

  /* ---------- MetaScope: player profile stats/habits sidebar + game
     analysis page ---------- */
  .metascope-layout { display: flex; align-items: flex-start; gap: 20px; }
  .metascope-sidebar { flex: 0 0 240px; display: flex; flex-direction: column; gap: 14px; }
  .metascope-main { flex: 1; min-width: 0; }
  @media (max-width: 720px) { .metascope-layout { flex-direction: column; } .metascope-sidebar { flex: none; width: 100%; } }
  .metascope-box { background: var(--row); border: 1px solid var(--border); padding: 14px 16px; }
  .metascope-box-title { font-family: 'Space Mono', monospace; font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--cyan); margin-bottom: 10px; }
  .metascope-stat-row { display: flex; justify-content: space-between; gap: 10px; padding: 3px 0; font-size: 12.5px; color: var(--text-dim); }
  .metascope-stat-row b { color: var(--cream); }
  .metascope-habit-badge { display: inline-block; background: var(--magenta-dim); border: 1px solid var(--magenta); color: var(--cream); font-size: 12px; font-weight: 600; padding: 5px 10px; margin-bottom: 10px; }
  .metascope-top-played-label { font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-faint); font-family: 'Space Mono', monospace; margin-bottom: 6px; }
  .metascope-top-played-row { display: flex; align-items: center; gap: 8px; padding: 4px 0; }
  .metascope-top-played-name { flex: 1; min-width: 0; font-size: 12.5px; color: inherit; text-decoration: none; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  a.metascope-top-played-name:hover { color: var(--cyan); }
  .metascope-top-played-count { color: var(--text-faint); font-size: 11px; }
  .metascope-hint { color: var(--text-faint); font-size: 12px; margin: -6px 0 14px; }
  .metascope-analyze-link { margin-left: auto; flex: none; color: var(--cyan); font-family: 'Space Mono', monospace; font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; text-decoration: none; white-space: nowrap; }
  .metascope-analyze-link:hover { color: var(--cream); }
  .profile-comp-row .profile-comp-name { text-decoration: none; color: inherit; }
  a.profile-comp-name:hover { color: var(--cyan); }

  .metascope-lang-note { padding: 10px 14px; margin-bottom: 14px; background: rgba(5,217,232,0.06); border: 1px dashed var(--border-bright); color: var(--text-faint); font-size: 12px; }
  .metascope-insight-list { display: flex; flex-direction: column; gap: 8px; }
  .metascope-insight-row { display: flex; align-items: flex-start; gap: 10px; padding: 10px 12px; background: var(--row); border: 1px solid var(--border); border-left: 3px solid var(--border); }
  .metascope-insight-row[data-type="good"] { border-left-color: var(--good); }
  .metascope-insight-row[data-type="warning"] { border-left-color: var(--warn); }
  .metascope-insight-row[data-type="info"] { border-left-color: var(--cyan); }
  .metascope-insight-icon { flex: none; width: 18px; text-align: center; font-size: 13px; }
  .metascope-insight-row[data-type="good"] .metascope-insight-icon { color: var(--good); }
  .metascope-insight-row[data-type="warning"] .metascope-insight-icon { color: var(--warn); }
  .metascope-insight-row[data-type="info"] .metascope-insight-icon { color: var(--cyan); }
  .metascope-insight-category { display: block; font-family: 'Space Mono', monospace; font-size: 9.5px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-faint); margin-bottom: 2px; }
  .metascope-insight-text { color: var(--text-dim); font-size: 13px; line-height: 1.5; }
  .metascope-counter-tag { flex: none; background: rgba(255,56,100,0.14); border: 1px solid var(--warn); color: var(--warn); font-family: 'Space Mono', monospace; font-size: 9.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 2px 7px; margin-left: auto; }
  .profile-comp-row[data-counter="true"] { border-color: var(--warn); }

  /* MetaScope search form + status line (leaderboard.html/list_page.html
     rows above reuse .search-input, but that one's a plain <input
     type=search> with a magnifier icon absolutely positioned via
     .search-row -- this form has a region <select> and a submit button
     alongside it, so it gets its own flex row instead). */
  .metascope-search-form { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; }
  .metascope-search-form .search-input { flex: 1; min-width: 220px; padding: 10px 14px; }
  .metascope-region-select { background: var(--row); border: 1px solid var(--border); color: var(--cream); font-family: 'Space Mono', monospace; font-size: 12px; font-weight: 700; padding: 0 12px; }
  .metascope-search-button { background: var(--magenta); border: none; color: #fff; font-family: 'Space Mono', monospace; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 0 20px; cursor: pointer; transition: background .12s ease; }
  .metascope-search-button:hover { background: var(--cyan); color: #0b0221; }
  .metascope-status { padding: 10px 14px; margin-bottom: 16px; background: var(--row); border: 1px dashed var(--border-bright); color: var(--text-dim); font-size: 12.5px; }
  .metascope-status[data-error="true"] { border-color: var(--warn); color: var(--warn); }
"""
    (DIST / "assets" / "css" / "style.css").write_text(css, encoding="utf-8")

    # Real brand assets (PROJECT/logo/) instead of the old emoji placeholder:
    # - logo-sword.svg (white, transparent) sits in the header next to the
    #   wordmark, on the site's dark top bar.
    # - favicon.svg ("logo google.svg", the circular navy-badge version) is
    #   the browser tab icon -- SVG favicons are supported by every modern
    #   browser. Tried logo_color.svg (dark navy sword, transparent) first,
    #   but a dark mark on a transparent background all but disappears on a
    #   dark-themed browser tab bar; the filled circle badge stays visible
    #   on any tab color.
    # - favicon-google.png (the same circular badge, pre-rendered to a flat
    #   512x512 PNG) is there specifically for Google Search results:
    #   Google does not support SVG favicons, so without a raster fallback
    #   the SERP would show a generic globe icon.
    LOGO_DIR = PROJECT / "logo"
    (DIST / "assets" / "img").mkdir(parents=True, exist_ok=True)
    shutil.copy(LOGO_DIR / "logo_epee_sans_fond.svg", DIST / "assets" / "img" / "logo-sword.svg")
    shutil.copy(LOGO_DIR / "logo google.svg", DIST / "favicon.svg")
    shutil.copy(LOGO_DIR / "logo_google_512.png", DIST / "favicon-google.png")

    (DIST / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (DIST / "assets" / "js" / "list-filters.js").write_text(LIST_FILTERS_JS, encoding="utf-8")
    (DIST / "assets" / "js" / "copy-comp.js").write_text(COPY_COMP_JS, encoding="utf-8")
    (DIST / "assets" / "js" / "champ-icons.js").write_text(CHAMP_ICON_JS, encoding="utf-8")
    (DIST / "assets" / "js" / "glossary-items.js").write_text(GLOSSARY_ITEM_JS, encoding="utf-8")
    (DIST / "assets" / "js" / "metascope.js").write_text(METASCOPE_JS, encoding="utf-8")
    (DIST / "assets" / "js" / "team-builder.js").write_text(TEAM_BUILDER_JS, encoding="utf-8")
    (DIST / "assets" / "data").mkdir(parents=True, exist_ok=True)
    (DIST / "assets" / "data" / "champions.json").write_text(
        json.dumps(champion_tooltip_data, ensure_ascii=False), encoding="utf-8")
    (DIST / "assets" / "data" / "glossary-items.json").write_text(
        json.dumps(glossary_item_tooltip_data, ensure_ascii=False), encoding="utf-8")

    # ---- MetaScope worker data: the same real numbers this build already
    # computed, published as small standalone files so the worker (a
    # separate, tiny Cloudflare Worker -- see metascope-worker/ -- doing a
    # LIVE Riot-ID lookup for a player we don't already track) can derive a
    # comp signature and compare it to real benchmarks without duplicating
    # or drifting from this site's own numbers. Trimmed to only the fields
    # analysis.py's build_report()/derive_comp() actually read -- tierlist.
    # json itself is 8MB+, most of it (item_stats, board_variants, bonus_
    # slots, contestation fields) irrelevant to a live single-game report. ----
    worker_benchmarks = {
        c["key"]: {
            "avg_gold_left": c.get("avg_gold_left"), "avg_level": c.get("avg_level"),
            "avg_last_round": c.get("avg_last_round"), "avg_placement": c["avg_placement"],
            "top4_rate": c["top4_rate"],
            "core_units": [{"champion": u["champion"], "items": u.get("items") or []} for u in c.get("core_units", [])],
            "item_combo_stats": [{"champion": r["champion"], "items": r["items"],
                                   "avgPlacement": r["avgPlacement"], "games": r["games"]}
                                  for r in c.get("item_combo_stats", [])],
        }
        for c in combined["comps"] if c.get("has_enough_data")
    }
    worker_matchups = [
        {"comp_a": m["comp_a"], "comp_b": m["comp_b"],
         "a_ahead_rate": m["a_ahead_rate"], "b_ahead_rate": m["b_ahead_rate"], "encounters": m["encounters"]}
        for m in matchups_json["matchups"]
    ]
    worker_comp_index = {c["key"]: {"slug": c["slug"], "display_label": c["display_label"]} for c in comp_vms}
    for name, payload in [
        ("benchmarks.json", worker_benchmarks), ("matchups.json", worker_matchups),
        ("comp-index.json", worker_comp_index), ("name-map.json", champ_name_map), ("item-offense.json", item_offense),
    ]:
        (DIST / "assets" / "data" / name).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    # ---- robots.txt + sitemap.xml ----
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")

    # Riot domain-ownership verification file (production API key application)
    # -- must be served at the real site root, so copy it through if present.
    riot_txt = PROJECT / "riot.txt"
    if riot_txt.exists():
        shutil.copy(riot_txt, DIST / "riot.txt")

    # Every page that got rendered wrote a real index.html -- walk the
    # finished dist/ instead of re-tracking URLs by hand, so the sitemap
    # can never drift from what was actually built.
    def url_for_index(p: Path) -> str:
        rel = p.parent.relative_to(DIST).as_posix()
        return BASE_URL if rel == "." else f"{BASE_URL}{rel}/"

    urls = sorted(url_for_index(p) for p in DIST.rglob("index.html"))
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{u}</loc></url>" for u in urls]
    sitemap.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")

    n_files = sum(1 for _ in DIST.rglob("*") if _.is_file())
    size_mb = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file()) / 1e6
    print(f"Done: {n_files} files, {size_mb:.1f} MB total, in {DIST}")
    print(f"{len(urls)} URLs in sitemap.xml")


if __name__ == "__main__":
    main()
