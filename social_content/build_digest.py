"""
BrokenMeta Content Studio - data digest
=========================================
Pulls fresh "content-worthy" facts out of the site's own data (no guessing,
no external scraping) so the ideation step always starts from real numbers:

- data/output/comp_history.json  -> top comps this week
- data/output/trends_digest.json -> biggest riser/faller (same canonical data
                                     as the live /tendances/ page -- see
                                     build_site.py's build_trend_rows)
- data/output/champion_stats.json -> best performer, most picked, best item combo
- social_content/patches.json     -> latest patch notes (buffs/nerfs), extracted
                                      from site_build/build_site.py's PATCHES dict
                                      (re-run the extraction snippet in the tool's
                                      README if a newer patch has been added there)

Run it whenever you want fresh talking points:
    py social_content/build_digest.py

Writes social_content/digest.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent

MIN_GAMES_COMP = 15
MIN_PICKS_CHAMP = 300


def load(p):
    return json.load(open(p, encoding="utf-8"))


def _builder():
    return load(ROOT / "site_build/dist/assets/data/builder.json")


def _comp_index():
    """The curated set of comps that actually have a published page on the
    site (site_build/dist/compo/<slug>/) -- a small fraction of every
    Trait_Champion combo comp_history.json tracks from raw match data.
    A comp NOT in here has no page to link to and must never be featured
    as content (confirmed the hard way: "Elderwood_Yunara" passed the old
    trait-name validity check but has no site page at all)."""
    return load(ROOT / "site_build/dist/assets/data/comp-index.json")


def _tierlist_by_key():
    """data/output/tierlist.json is the exact dataset the site's own
    comp-row UI is built from (tier letter, playstyle_tag "Reroll" pill,
    avg_placement/top4_rate/contestation_index -- the PLACEMENT/TOP4/CONTEST
    columns shown on-site). ~20MB / 1456 comps, so load it once per run."""
    comps = load(ROOT / "data/output/tierlist.json")["comps"]
    return {c["key"]: c for c in comps}


TIER_COLOR_VAR = {"S": "red", "A": "gold", "B": "teal", "C": "gray"}


def _trait_champ_split(name, valid_champs):
    """comp_history keys are 'Trait_Champion'. Split on the champion suffix
    rather than the first underscore, since some champion names contain
    apostrophes but not underscores."""
    for champ in valid_champs:
        suffix = "_" + champ
        if name.endswith(suffix):
            return name[: -len(suffix)], champ
    return None, None


def top_comps():
    hist = load(ROOT / "data/output/comp_history.json")["snapshots"]
    hist.sort(key=lambda s: s["date"])
    latest, prev = hist[-1], (hist[-2] if len(hist) > 1 else None)

    builder = _builder()
    comp_index = _comp_index()
    tierlist = _tierlist_by_key()
    valid_champs = {c["name"] for c in builder["champions"]}
    champ_by_name = {c["name"]: c for c in builder["champions"]}
    trait_slug = {t["name"].replace(" ", ""): t["slug"] for t in builder["traits"]}
    champ_slug = {c["name"]: c["slug"] for c in builder["champions"]}

    def enrich(name, stats):
        page = comp_index.get(name)
        if page is None:
            return None  # no published page for this comp -- never feature it
        trait, champ = _trait_champ_split(name, valid_champs)
        if champ is None:
            return None
        tl = tierlist.get(name)  # the same site-row stats: tier, Reroll pill, PLACEMENT/TOP4/CONTEST
        row = {
            "comp": name, "display_label": page["display_label"], "comp_slug": page["slug"],
            "champion": champ,
            # trait icon is best-effort: some published comps are keyed by a
            # champion-unique "trait" (e.g. "LuxUniqueTrait") that has no icon
            # in the trait art set -- fine to omit, the champion art carries it.
            "trait_slug": trait_slug.get(trait.replace(" ", "")) if trait else None,
            "champion_slug": champ_slug[champ],
            "cost": champ_by_name[champ]["cost"],
            **stats,
        }
        if tl:
            row.update({
                "tier": tl["tier"], "tier_color": TIER_COLOR_VAR.get(tl["tier"], "gray"),
                "playstyle_tag": tl["playstyle_tag"],  # e.g. "Reroll", "Fast 8", "Standard"
                "top4_rate": tl["top4_rate"], "contestation_index": tl["contestation_index"],
            })
        return row

    ranked = [r for name, stats in latest["comps"].items()
              if stats["playCount"] >= MIN_GAMES_COMP and (r := enrich(name, stats))]
    ranked.sort(key=lambda c: c["avgPlacement"])
    top5 = ranked[:5]

    return {
        "latest_date": latest["date"],
        "prev_date": prev["date"] if prev else None,
        "top5": top5,
        **_biggest_movers(trait_slug),
    }


def _biggest_movers(trait_slug):
    """The #1 riser/faller, straight from site_build/build_site.py's own
    /tendances/ page data (data/output/trends_digest.json) instead of a
    second, separately-derived copy of the same computation -- that page's
    version already excludes Hors Meta comps and filters out noise-level
    swings (min_delta), neither of which this tool used to do, so a
    "biggest riser" here could previously have been a comp visitors can't
    even see live on /tendances/. trend_risers[0]/trend_fallers[0] are
    already sorted best-first by build_trend_rows()."""
    path = ROOT / "data/output/trends_digest.json"
    if not path.exists():
        return {"biggest_riser": None, "biggest_faller": None}
    data = load(path)

    def convert(row):
        if not row:
            return None
        trait = row.get("identity_trait")
        return {
            "comp": row["slug"], "display_label": row["display_label"], "comp_slug": row["slug"],
            "champion": row.get("carry"), "champion_slug": row.get("carry_slug"),
            "trait_slug": trait_slug.get(trait.replace(" ", "")) if trait else None,
            "tier": row["tier"], "tier_color": TIER_COLOR_VAR.get(row["tier"], "gray"),
            "avgPlacement": row["latest_placement"], "prevAvgPlacement": row["prev_placement"],
            "delta": row["delta"],
        }

    return {
        "biggest_riser": convert(data["risers"][0] if data.get("risers") else None),
        "biggest_faller": convert(data["fallers"][0] if data.get("fallers") else None),
    }


def champion_highlights():
    d = load(ROOT / "data/output/champion_stats.json")
    builder = _builder()
    champ_by_name = {c["name"]: c for c in builder["champions"]}
    item_slug = {i["name"].replace(" ", "").replace("'", ""): i["slug"] for i in builder.get("items", [])}

    def champ_meta(champ_id):
        c = champ_by_name.get(champ_id)
        return {"cost": c["cost"], "champion_slug": c["slug"]} if c else {}

    champs = [c for c in d["champions"] if c["pick_count"] >= MIN_PICKS_CHAMP]

    best_placement = sorted(champs, key=lambda c: c["avg_placement"])[:5]
    most_picked = sorted(champs, key=lambda c: c["pick_count"], reverse=True)[:5]
    best_top4 = sorted(champs, key=lambda c: c["top4_rate"], reverse=True)[:5]

    # a champion with a standout item combo (highest winRate combo among
    # combos with a decent sample size)
    best_combo = None
    for c in champs:
        for combo in c.get("item_combo_stats", []):
            if combo.get("games", 0) < 100:
                continue
            if best_combo is None or combo["winRate"] > best_combo["winRate"]:
                best_combo = {"champion": c["id"], **champ_meta(c["id"]), **combo}
    if best_combo:
        best_combo["item_slugs"] = [item_slug.get(i.replace(" ", "").replace("'", ""), i.lower()) for i in best_combo["items"]]

    return {
        "best_placement": [{"id": c["id"], "avg_placement": c["avg_placement"], "top4_rate": c["top4_rate"],
                             "pick_count": c["pick_count"], **champ_meta(c["id"])} for c in best_placement],
        "most_picked": [{"id": c["id"], "pick_count": c["pick_count"], "pick_rate": c["pick_rate"],
                          "avg_placement": c["avg_placement"], **champ_meta(c["id"])} for c in most_picked],
        "best_top4_rate": [{"id": c["id"], "top4_rate": c["top4_rate"], "avg_placement": c["avg_placement"],
                             **champ_meta(c["id"])} for c in best_top4],
        "best_item_combo": best_combo,
    }


def latest_patch():
    patches = load(OUT / "patches.json")
    return {lang: patches[lang][0] for lang in patches}


def main():
    digest = {
        "comps": top_comps(),
        "champions": champion_highlights(),
        "patch": latest_patch(),
    }
    json.dump(digest, open(OUT / "digest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("digest.json written")


if __name__ == "__main__":
    main()
