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


RANK_WORD_FR = {
    "IRON": "Fer", "BRONZE": "Bronze", "SILVER": "Argent", "GOLD": "Or", "PLATINUM": "Platine",
    "EMERALD": "Émeraude", "DIAMOND": "Diamant", "MASTER": "Maître", "GRANDMASTER": "Grand Maître",
    "CHALLENGER": "Challenger",
}


def rank_bracket_label(key: str) -> str:
    """Turns a rank-bracket key (whatever config.RANK_BRACKETS currently
    produces -- broad merged buckets like "IRON_SILVER" today, or individual
    tiers like "PLATINUM" if the pipeline is re-run with the newer 8-bucket
    config) into a readable French label, without hardcoding which shape is
    current."""
    if key == "MASTER_PLUS":
        return "Maître+"
    words = [RANK_WORD_FR.get(p, p.title()) for p in key.split("_")]
    return "-".join(words)


REGION_SHORT = {"EUW": "EUW", "NA": "NA", "BR": "BR", "KR": "KR"}


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
            "level_badge": c.get("level_badge"),
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
                    "title": f"+1 unité ({bs['coreSize'] + 1} au total)",
                    "rows": [{"icons": [(champ_slug_and_download(ch), ch) for ch in row["champions"]],
                              "names": " + ".join(row["champions"]), "avg_placement": row["avgPlacement"], "games": row["games"]}
                             for row in bs["plusOne"]],
                })
            if bs.get("plusTwo"):
                bonus_groups.append({
                    "title": f"+2 unités ({bs['coreSize'] + 2} au total)",
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

    # ---- Leaderboard view-model ----
    REGION_NAMES = {"EUW": "Europe Ouest (EUW)", "NA": "Amérique du Nord (NA)", "BR": "Brésil (BR)", "KR": "Corée (KR)"}
    lb_regions = []
    for region, rows in leaderboard_json["regions"].items():
        if not rows:
            continue
        vm_rows = []
        for p in rows[:100]:
            form = []
            for placement in (p.get("recentPlacements") or [])[:5]:
                win = placement <= 4
                form.append({"cls": "win" if win else "loss", "label": "W" if win else "L", "title": f"Placement : {placement}"})
            while len(form) < 5:
                form.append({"cls": "empty", "label": "–", "title": ""})
            vm_rows.append({"rank": p["rank"], "riot_id": p["riotId"], "tier": p["tier"], "lp": p["leaguePoints"],
                             "hot_streak": p.get("hotStreak", False), "form": form})
        lb_regions.append({"name": REGION_NAMES.get(region, region), "rows": vm_rows})

    # ---- Patch notes (same hand-written content as the Artifact's FR list) ----
    patches = [
        {"version": "18.1", "tag": "Set 18", "date": "25 août 2026", "title": "Enchanted Wilds arrive sur le jeu en direct",
         "summary": "Lancement du Set 18 « Enchanted Wilds » (Riftbeasts, Elderwood, la nouvelle mécanique Wisps) et bascule du moteur du jeu de Hextech vers Unreal Engine. Le Set 17 « Space Gods » reste jouable en parallèle quelques patchs de plus. Plusieurs correctifs ont suivi les 27 et 28 août : fuites mémoire, temps de chargement, et une réactivation de la file Double Up après un bug l'ayant fait désactiver temporairement.",
         "url": "https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1/"},
        {"version": "17.9", "tag": "Équilibrage", "date": "11 août 2026", "title": "Dernier patch dédié à Space Gods",
         "summary": "Dernier patch d'équilibrage propre au Set 17 avant l'arrivée d'Enchanted Wilds le 26 août. Refonte du trait Shepherd (mana, bouclier, dégâts d'échelle), gros changement de courbe risque/récompense sur Twisted Fate, et buffs sur Gwen et Milio.",
         "url": "https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-17-9/"},
        {"version": "17.8", "tag": "Contenu", "date": "28 juillet 2026", "title": "Choncc's Classic Treasure",
         "summary": "Le mode « Choncc's Lore & Legends » devient « Choncc's Classic Treasure » avec des éléments classiques de League (monstres PvE, tribunal de Kayle, anciens objets comme Heart of Gold). Petits ajustements d'équilibrage sur Space Gods, et Enchanted Wilds (Set 18) arrive en PBE le même jour.",
         "url": "https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-17-8/"},
    ]

    # ---- Render ----
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=True)
    env.globals["star_svg"] = STAR_SVG

    def render(template_name: str, out_path: Path, root: str, **ctx) -> None:
        tpl = env.get_template(template_name)
        html = tpl.render(root=root, canonical=BASE_URL + str(out_path.relative_to(DIST)).replace("\\", "/").removesuffix("index.html"),
                           generated_at=combined["generated_at"][:10], set_name=combined["set"], **ctx)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")

    total_matches = combined["sample"]["total_matches"]

    render("champions_list.html", DIST / "champions" / "index.html", "../", active_nav="champions", champions=champion_vms)
    render("leaderboard.html", DIST / "leaderboard" / "index.html", "../", active_nav="leaderboard", regions=lb_regions)
    render("patch_notes.html", DIST / "patch-notes" / "index.html", "../", active_nav="patchnotes", patches=patches)

    for c in comp_vms:
        render("comp.html", DIST / "compo" / c["slug"] / "index.html", "../../", active_nav="comps", c=c)
    for d in champion_vms:
        render("champion.html", DIST / "champions" / d["slug"] / "index.html", "../../", active_nav="champions", d=d)

    # ---- Région / Rang: real pages per slice (not a JS data blob) --------
    # Region and rank are two ALTERNATE ways to slice the same dataset
    # (mirrors the Artifact: picking one is mutually exclusive with the
    # other), so a scope is (kind, key) with kind in {'all','region','rank'}.
    # Every scope gets the same shape: one light overview page (tier
    # previews, like the homepage) + one full list page per tier that
    # actually has comps.
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

    def scope_chip_lists(kind: str, key: str | None, tier: str | None):
        def with_tier(base: str) -> str:
            return base if tier is None else base + f"tier/{tier.lower()}/"

        region_chips = [{"label": "Toutes", "href": with_tier("/"), "active": kind != "region"}]
        for r in available_regions:
            region_chips.append({"label": REGION_SHORT.get(r, r), "href": with_tier(region_root(r)), "active": kind == "region" and key == r})

        rank_chips = [{"label": "Tous rangs", "href": with_tier("/"), "active": kind != "rank"}]
        for b in available_ranks:
            rank_chips.append({"label": rank_bracket_label(b), "href": with_tier(rank_root(b)), "active": kind == "rank" and key == b})

        return region_chips, rank_chips

    def dist_path_for(url_path: str) -> Path:
        """'/', '/region/euw/', '/region/euw/tier/s/' -> a dist/.../index.html Path."""
        parts = [p for p in url_path.strip("/").split("/") if p]
        return Path(DIST, *parts, "index.html") if parts else DIST / "index.html"

    def rel_prefix_for(url_path: str) -> str:
        depth = len([p for p in url_path.strip("/").split("/") if p])
        return "../" * depth

    def render_scope(kind: str, key: str | None, rows: list[dict], scope_label: str) -> None:
        root_path = scope_root(kind, key)
        HOMEPAGE_PREVIEW_PER_TIER = 15
        tier_groups = []
        for tier in ["S", "A", "B", "C"]:
            tier_rows = [c for c in rows if c["tier"] == tier]
            if tier_rows:
                tier_groups.append({"tier": tier, "total": len(tier_rows), "preview": tier_rows[:HOMEPAGE_PREVIEW_PER_TIER]})

        region_chips, rank_chips = scope_chip_lists(kind, key, None)
        suffix = f" — {scope_label}" if scope_label else ""
        render("overview.html", dist_path_for(root_path), rel_prefix_for(root_path),
               active_nav="comps",
               page_title=f"Tier List{suffix} — {len(rows)} compositions | BrokenMeta.gg",
               page_description=f"Tier list Teamfight Tactics Set 18{suffix} : {len(rows)} compositions, données réelles Riot Match-V1.",
               h1=f"Tier List{suffix} — Teamfight Tactics Set 18",
               intro=f"{len(rows)} compositions{suffix} classées, triées par taux de top 4 puis placement moyen. Données réelles issues de l'API Riot Match-V1.",
               tier_groups=tier_groups, region_chips=region_chips, rank_chips=rank_chips,
               tier_href=lambda t, _root=root_path: _root + f"tier/{t.lower()}/")

        for group in tier_groups:
            tier = group["tier"]
            tier_rows = [c for c in rows if c["tier"] == tier]
            cats = sorted({c["playstyle_cat"] for c in tier_rows if c["playstyle_cat"]},
                          key=lambda x: ["Reroll", "Fast", "Slow"].index(x) if x in ["Reroll", "Fast", "Slow"] else 9)
            region_chips_t, rank_chips_t = scope_chip_lists(kind, key, tier)
            tier_url = root_path + f"tier/{tier.lower()}/"
            render("list_page.html", dist_path_for(tier_url), rel_prefix_for(tier_url),
                   active_nav="comps",
                   page_title=f"Tier {tier}{suffix} — {len(tier_rows)} compositions | TFT Set 18 | BrokenMeta.gg",
                   page_description=f"Compositions Tier {tier}{suffix} sur Teamfight Tactics Set 18 ({len(tier_rows)} compos), données réelles.",
                   h1=f"Tier {tier}{suffix} — Teamfight Tactics Set 18",
                   intro=f"{len(tier_rows)} compositions classées Tier {tier}{suffix}, triées par taux de top 4 puis placement moyen.",
                   comps=tier_rows, type_cats=cats,
                   region_chips=region_chips_t, rank_chips=rank_chips_t)

    print("Building région/rang pages...")
    render_scope("all", None, comp_vms, "")
    for r in available_regions:
        render_scope("region", r, region_rows[r], REGION_SHORT.get(r, r))
    for b in available_ranks:
        render_scope("rank", b, rank_rows[b], rank_bracket_label(b))

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
"""
    (DIST / "assets" / "css" / "style.css").write_text(css, encoding="utf-8")

    (DIST / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<text y=".9em" font-size="90">\U0001F306</text></svg>', encoding="utf-8")

    (DIST / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (DIST / "assets" / "js" / "type-filter.js").write_text(TYPE_FILTER_JS, encoding="utf-8")

    # ---- robots.txt + sitemap.xml ----
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")

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
