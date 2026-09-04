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
from pathlib import Path

import requests
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
sys.path.insert(0, str(PROJECT / "src"))
from tft_tracker.champion_images import (  # noqa: E402
    build_champion_image_map, build_item_image_map,
)

OUT = PROJECT / "data" / "output"
DIST = ROOT / "dist"
SET_MUTATOR = "TFTSet18"
BASE_URL = "https://brokenmeta.gg/"

# Same quality filter as the Artifact's export_data.py -- keeps both
# versions showing the same ~500 real, well-sampled comps.
MIN_PLAY_COUNT = 10
MAX_AVG_PLACEMENT = 6.00
MIN_CORE_BOARD_SIZE = 7

TIER_VAR = {"S": "var(--red)", "A": "var(--gold)", "B": "var(--teal)", "C": "var(--gray)", "?": "var(--gray)"}

# Progressive enhancement only -- every comp is already in the static HTML
# (crawlable, works with JS off); Région/Rang are real separate pages, but
# Type (Reroll/Fast/Slow) doesn't need its own data slice, just show/hide
# among rows already rendered on the current tier page.
TYPE_FILTER_JS = """
(function () {
  var bar = document.getElementById('typeFilterBar');
  if (!bar) return;
  var rows = document.querySelectorAll('#rows .comp-row');
  bar.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-filter-type]');
    if (!btn) return;
    [].forEach.call(bar.querySelectorAll('[data-filter-type]'), function (b) { b.dataset.active = String(b === btn); });
    var cat = btn.dataset.filterType;
    rows.forEach(function (row) {
      row.style.display = (cat === 'ALL' || row.dataset.playstyleCat === cat) ? '' : 'none';
    });
  });
})();
"""
STAR_SVG = '<svg viewBox="0 0 24 24"><path d="M12 2.5l2.97 6.28 6.93.7-5.13 4.75 1.4 6.87L12 17.9l-6.17 3.2 1.4-6.87-5.13-4.75 6.93-.7z"/></svg>'


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "x"


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
        "overlay_cta_title": "L'overlay Overwolf est en cours de développement, pas encore disponible au téléchargement.",
        "overlay_cta_soon": "Bientôt",
        "footer_generated": lambda date, s: f"Généré le {date} · Set {s}",
        "lbl_region": "Région", "lbl_rank": "Rang", "lbl_tier": "Tier", "lbl_type": "Type",
        "region_all": "Toutes", "rank_all": "Tous rangs", "tier_all": "Tout",
        "placement_label": "Placement", "top4_label": "Top 4", "contest_label": "Contest.",
        "level_badge": lambda n: f"Niveau {n}",
        "home_intro": lambda n, m: f"{n} compositions calculées à partir de {m} parties classées réelles, collectées via l'API officielle de Riot (Match-V1). Aucune donnée inventée ou estimée : chaque statistique vient d'un vrai match.",
        "scope_intro": lambda n, suffix: f"{n} compositions{suffix} classées, triées par taux de top 4 puis placement moyen. Données réelles issues de l'API Riot Match-V1.",
        "tier_scope_intro": lambda n, tier, suffix: f"{n} compositions classées Tier {tier}{suffix}, triées par taux de top 4 puis placement moyen.",
        "see_full_tier": lambda n, tier: f"Voir les {n} compos Tier {tier} →",
        "tier_word": "Tier",
        "type_all": "Tout type",
        "view_full_sheet": "Voir la fiche complète →",
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
        "champ_unranked_note": 'Les champions marqués <b style="color:var(--cream)">?</b> n\'ont pas encore assez de parties observées dans cet échantillon pour un rang fiable — ils restent affichés avec leurs stats brutes.',
        "best_items_title": "Meilleurs objets",
        "no_combo_data": "Pas assez de données de combinaisons pour ce champion dans cet échantillon.",
        "games_col": "Parties", "winrate_col": "Winrate",
        "compositions_title": "Compositions",
        "champ_not_in_comp": "Ce champion n'apparaît dans aucune comp classée de cet échantillon.",
        "back_to_leaderboard": "← Retour au leaderboard",
        "leaderboard_title": "Leaderboard — Teamfight Tactics Set 18",
        "th_player": "Joueur", "th_tier": "Palier", "th_form": "Forme (5 dernières)",
        "hot_streak_title": "Série en cours",
        "lb_note": 'Classement réel (League-v1, Challenger complété par Grandmaster/Master si le serveur en a moins de 100), trié par LP. TFT n\'a pas de victoire/défaite au sens strict : <b style="color:var(--good)">W</b> = top 4 sur la partie, <b style="color:var(--warn)">L</b> = 5ᵉ-8ᵉ — une convention d\'affichage, pas une donnée Riot.',
        "see_worldstat": "Voir World Stat →",
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
        "patch_banner": 'Riot ne publie pas les patch notes TFT via une API — seulement en articles sur son site officiel. Voici une sélection résumée à la main des derniers patchs ; chaque carte renvoie vers l\'article complet (tous les chiffres d\'équilibrage) sur <a href="https://teamfighttactics.leagueoflegends.com/en-us/news/" target="_blank" rel="noopener">teamfighttactics.leagueoflegends.com</a>.',
        "patch_word": "Patch", "read_full_article": "Lire l'article complet →",
    },
    "en": {
        "nav_comps": "Comp List", "nav_champions": "Champion List", "nav_patchnotes": "Patch Notes", "nav_leaderboard": "Leaderboard",
        "overlay_cta_title": "The Overwolf overlay is in development, not yet available for download.",
        "overlay_cta_soon": "Soon",
        "footer_generated": lambda date, s: f"Generated on {date} · Set {s}",
        "lbl_region": "Region", "lbl_rank": "Rank", "lbl_tier": "Tier", "lbl_type": "Type",
        "region_all": "All", "rank_all": "All ranks", "tier_all": "All",
        "placement_label": "Placement", "top4_label": "Top 4", "contest_label": "Contest.",
        "level_badge": lambda n: f"Level {n}",
        "home_intro": lambda n, m: f"{n} comps calculated from {m} real ranked games, collected via Riot's official API (Match-V1). No invented or estimated data: every stat comes from a real match.",
        "scope_intro": lambda n, suffix: f"{n} ranked comps{suffix}, sorted by top 4 rate then average placement. Real data from the Riot Match-V1 API.",
        "tier_scope_intro": lambda n, tier, suffix: f"{n} comps ranked Tier {tier}{suffix}, sorted by top 4 rate then average placement.",
        "see_full_tier": lambda n, tier: f"See all {n} Tier {tier} comps →",
        "tier_word": "Tier",
        "type_all": "All types",
        "view_full_sheet": "View full sheet →",
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
        "champ_unranked_note": 'Champions marked <b style="color:var(--cream)">?</b> don\'t have enough observed games in this sample yet for a reliable rank — they\'re still shown with their raw stats.',
        "best_items_title": "Best items",
        "no_combo_data": "Not enough item-combo data for this champion in this sample.",
        "games_col": "Games", "winrate_col": "Winrate",
        "compositions_title": "Comps",
        "champ_not_in_comp": "This champion doesn't appear in any ranked comp in this sample.",
        "back_to_leaderboard": "← Back to leaderboard",
        "leaderboard_title": "Leaderboard — Teamfight Tactics Set 18",
        "th_player": "Player", "th_tier": "Tier", "th_form": "Form (last 5)",
        "hot_streak_title": "On a streak",
        "lb_note": 'Real standings (League-v1, Challenger topped up with Grandmaster/Master if the server has fewer than 100), sorted by LP. TFT doesn\'t have a strict win/loss: <b style="color:var(--good)">W</b> = top 4 that game, <b style="color:var(--warn)">L</b> = 5th-8th — a display convention, not a Riot-provided stat.',
        "see_worldstat": "View World Stat →",
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
        "patch_banner": 'Riot doesn\'t publish TFT patch notes through an API — only as articles on its official site. Here\'s a hand-written summary of the latest patches; each card links to the full article (all the real balance numbers) on <a href="https://teamfighttactics.leagueoflegends.com/en-us/news/" target="_blank" rel="noopener">teamfighttactics.leagueoflegends.com</a>.',
        "patch_word": "Patch", "read_full_article": "Read full article →",
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
        self.champ_dir.mkdir(parents=True, exist_ok=True)
        self.item_dir.mkdir(parents=True, exist_ok=True)
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
            "avg_placement": c["avg_placement"], "top4_pct": pct(c["top4_rate"]),
            "play_count": c["play_count"], "play_rate": c.get("play_rate", 0),
            "contestation_index": c.get("contestation_index", 0), "contestation_level": c.get("contestation_level", "Low"),
            "level_badge_n": (re.search(r"\d+", c["level_badge"]).group() if c.get("level_badge") else None),
            "trend": trend_for(c["key"]),
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

    # ---- Leaderboard view-model (region display name filled in per-language
    # just before rendering -- everything else here is language-independent) ----
    REGION_NAMES = {
        "fr": {"EUW": "Europe Ouest (EUW)", "NA": "Amérique du Nord (NA)", "BR": "Brésil (BR)", "KR": "Corée (KR)"},
        "en": {"EUW": "West Europe (EUW)", "NA": "North America (NA)", "BR": "Brazil (BR)", "KR": "Korea (KR)"},
    }
    lb_regions_raw = []
    for region, rows in leaderboard_json["regions"].items():
        if not rows:
            continue
        vm_rows = []
        for p in rows[:100]:
            form = []
            for placement in (p.get("recentPlacements") or [])[:5]:
                win = placement <= 4
                form.append({"cls": "win" if win else "loss", "label": "W" if win else "L", "placement": placement})
            while len(form) < 5:
                form.append({"cls": "empty", "label": "–", "placement": None})
            vm_rows.append({"rank": p["rank"], "riot_id": p["riotId"], "tier": p["tier"], "lp": p["leaguePoints"],
                             "hot_streak": p.get("hotStreak", False), "form": form})
        lb_regions_raw.append({"code": region, "rows": vm_rows})

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

    # ---- Render: every page renders twice, once per language. French stays
    # at the URL root (default, matches the site's existing audience); English
    # gets a real /en/ prefix -- its own crawlable pages with their own
    # hreflang-linked URL, not a client-side toggle over one page. ----
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=True)
    env.globals["star_svg"] = STAR_SVG
    env.globals["t"] = translate

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

        lb_regions = [{"name": REGION_NAMES[lang].get(r["code"], r["code"]),
                       "rows": [{**row, "form": [{**sq, "title": (translate(lang, "placement_colon", sq["placement"]) if sq["placement"] is not None else "")} for sq in row["form"]]}
                                for row in r["rows"]]}
                      for r in lb_regions_raw]
        render("leaderboard.html", "/leaderboard/", lang, active_nav="leaderboard", regions=lb_regions)
        render("world_stat.html", "/leaderboard/world-stat/", lang, active_nav="leaderboard",
               elo_chart_svg=build_elo_chart_svg(ws_snapshots, ws_regions_present, lang), legend=legend, single_point=len(ws_snapshots) == 1,
               region_cols=region_cols, comp_cols=comp_cols)
        render("patch_notes.html", "/patch-notes/", lang, active_nav="patchnotes", patches=PATCHES[lang])

        for c in comp_vms:
            render("comp.html", f"/compo/{c['slug']}/", lang, active_nav="comps", c=c)
        for d in champion_vms:
            render("champion.html", f"/champions/{d['slug']}/", lang, active_nav="champions", d=d)

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
            render("overview.html", root_path, _lang,
                   active_nav="comps",
                   page_title=f"Tier List{title_suffix} — {len(rows)} compositions | BrokenMeta.gg" if _lang == "fr"
                              else f"Tier List{title_suffix} — {len(rows)} comps | BrokenMeta.gg",
                   page_description=f"Tier list Teamfight Tactics Set 18{title_suffix} : {len(rows)} compositions, données réelles Riot Match-V1." if _lang == "fr"
                                     else f"Teamfight Tactics Set 18 tier list{title_suffix}: {len(rows)} real ranked comps, real Riot Match-V1 data.",
                   h1=f"Tier List{title_suffix} — Teamfight Tactics Set 18",
                   intro=translate(_lang, "home_intro", len(rows), f"{total_matches:,}" if _lang == "en" else f"{total_matches:,}".replace(",", " ")) if kind == "all"
                         else translate(_lang, "scope_intro", len(rows), suffix),
                   tier_groups=tier_groups, region_chips=region_chips, rank_chips=rank_chips,
                   tier_href=lambda t, _root=root_path: _root + f"tier/{t.lower()}/")

            for group in tier_groups:
                tier = group["tier"]
                tier_rows = [c for c in rows if c["tier"] == tier]
                cats = sorted({c["playstyle_cat"] for c in tier_rows if c["playstyle_cat"]},
                              key=lambda x: ["Reroll", "Fast", "Slow"].index(x) if x in ["Reroll", "Fast", "Slow"] else 9)
                region_chips_t, rank_chips_t = scope_chip_lists(kind, key, tier)
                tier_url = root_path + f"tier/{tier.lower()}/"
                render("list_page.html", tier_url, _lang,
                       active_nav="comps",
                       page_title=f"Tier {tier}{title_suffix} — {len(tier_rows)} compositions | TFT Set 18 | BrokenMeta.gg" if _lang == "fr"
                                  else f"Tier {tier}{title_suffix} — {len(tier_rows)} comps | TFT Set 18 | BrokenMeta.gg",
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
     inert on purpose, no download link exists yet. */
  .navbar-right { display: flex; align-items: center; gap: 18px; flex-wrap: wrap; }
  .overlay-cta { display: flex; align-items: center; gap: 6px; background: var(--cyan); color: #0b0221; padding: 6px 8px 6px 10px; }
  .overlay-cta svg { width: 13px; height: 13px; stroke: #0b0221; fill: none; stroke-width: 2.2; }
  .overlay-cta .cta-label { font-family: 'Cal Sans', sans-serif; font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase; }
  .overlay-cta .cta-soon { font-family: 'Space Mono', monospace; font-size: 9px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; background: rgba(11,2,33,0.15); padding: 2px 6px; margin-left: 2px; }

  /* FR/EN toggle -- real separate pages (hreflang-linked), this just jumps
     between the current page's two language URLs. */
  .lang-toggle { display: flex; border: 1px solid var(--border-bright); flex: none; }
  .lang-btn { display: block; background: var(--row); border: none; color: var(--text-faint); font-family: 'Space Mono', monospace; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; padding: 6px 10px; text-decoration: none; }
  .lang-btn + .lang-btn { border-left: 1px solid var(--border-bright); }
  .lang-btn[data-active="true"] { background: var(--cyan); color: #0b0221; }
  .lang-btn:not([data-active="true"]):hover { color: var(--cream); }
"""
    (DIST / "assets" / "css" / "style.css").write_text(css, encoding="utf-8")

    (DIST / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<text y=".9em" font-size="90">\U0001F306</text></svg>', encoding="utf-8")

    (DIST / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (DIST / "assets" / "js" / "type-filter.js").write_text(TYPE_FILTER_JS, encoding="utf-8")

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
