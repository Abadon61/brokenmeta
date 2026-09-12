"""Per-champion aggregate stats, built from the same match data as the tier
list, meant to back a hover tooltip on a champion card in the future web
page: how often it's picked, what star level it usually reaches, its most
common items, and how games featuring it tend to go.

Riot's Match-V1 does expose this at the unit level (`character_id`,
`itemNames`, `tier` = star level, `rarity` = cost tier) so no extra API
calls are needed — this is derived from matches already fetched for the
tier list.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from .comp_signature import clean_id, display_name, is_complete_item
from .tierlist import TIER_BUCKETS, SHRINKAGE_PRIOR_GAMES

# Champions get picked far more often per match (up to ~9 slots/game) than
# any single comp does, so this can safely sit higher than
# config.MIN_SAMPLE_FOR_TIER without starving thin regions (BR) of ranked
# champions -- checked live against the smallest sampled region.
MIN_SAMPLE_FOR_CHAMPION_TIER = 30


@dataclass
class ChampionAgg:
    id: str
    placements: list[int] = field(default_factory=list)
    star_levels: list[int] = field(default_factory=list)
    items: Counter = field(default_factory=Counter)
    three_star_count: int = 0
    # 3-complete-item combo -> [placement, ...], across EVERY game this
    # champion appeared in (any comp) -- not scoped to one identified comp
    # the way CompStats.unit_item_combo is. Backs the champion sheet's
    # "Best Items" tab: real win rate per build, independent of which
    # archetype it happened to be played in.
    item_combo: dict = field(default_factory=dict)

    @property
    def pick_count(self) -> int:
        return len(self.placements)

    @property
    def avg_placement(self) -> float:
        return sum(self.placements) / len(self.placements) if self.placements else 0.0

    @property
    def top4_rate(self) -> float:
        if not self.placements:
            return 0.0
        return sum(1 for p in self.placements if p <= 4) / len(self.placements)

    @property
    def avg_star_level(self) -> float:
        return sum(self.star_levels) / len(self.star_levels) if self.star_levels else 0.0

    @property
    def three_star_rate(self) -> float:
        return self.three_star_count / self.pick_count if self.pick_count else 0.0

    def item_combo_stats(self, min_games: int = 2) -> list[dict]:
        rows = []
        for combo, placements in self.item_combo.items():
            n = len(placements)
            if n < min_games:
                continue
            rows.append({
                "items": list(combo),
                "games": n,
                "avgPlacement": round(sum(placements) / n, 3),
                "top4Rate": round(sum(1 for p in placements if p <= 4) / n, 4),
                "winRate": round(sum(1 for p in placements if p == 1) / n, 4),
            })
        rows.sort(key=lambda r: -r["games"])
        return rows


def build_item_champion_stats(item_champ_placements: dict[str, dict[str, list[int]]],
                               min_games: int = 5, top_champions: int = 6) -> dict[str, list[dict]]:
    """Turns the raw {item: {champion: [placement, ...]}} collected
    alongside ChampionAgg (see build_champion_stats()) into the Item
    Glossary's "who plays this well" table: for one item, its top
    champions by real win rate WHILE HOLDING IT ALONE -- not inside a
    3-item combo the way ChampionAgg.item_combo_stats() is scoped, so a
    single strong item shows up here even on a build that varies its other
    2 slots. `min_games` keeps thin single-game flukes out (a 1-game 100%
    "win rate" would otherwise top every list)."""
    result: dict[str, list[dict]] = {}
    for item, by_champ in item_champ_placements.items():
        rows = []
        for champ, placements in by_champ.items():
            n = len(placements)
            if n < min_games:
                continue
            rows.append({
                "champion": champ, "games": n,
                "avgPlacement": round(sum(placements) / n, 3),
                "top4Rate": round(sum(1 for x in placements if x <= 4) / n, 4),
                "winRate": round(sum(1 for x in placements if x == 1) / n, 4),
            })
        rows.sort(key=lambda r: (-r["winRate"], -r["top4Rate"], -r["games"]))
        if rows:
            result[item] = rows[:top_champions]
    return result


MIN_SAMPLE_FOR_ITEM_TIER = 100  # same bar as a comp's own MIN_PLAY_COUNT (build_site.py) -- see build_global_item_stats


def build_global_item_stats(item_champ_placements: dict[str, dict[str, list[int]]],
                             total_participants: int) -> list[dict]:
    """The Item Tier List's real numbers: for one item, EVERY placement from
    EVERY champion that held it, flattened -- not scoped to a single
    champion or comp the way item_stats()/item_combo_stats() are elsewhere.
    Reuses item_champ_placements (already collected alongside ChampionAgg
    for build_item_champion_stats' "who plays this well" table) instead of
    a second pass over raw matches -- same underlying observations, just
    grouped by item alone instead of by item-then-champion.

    A single item slot on a unit is one observation, so games where two
    different champions both held e.g. Infinity Edge count it twice --
    intentional: this answers "how do games featuring this item tend to
    go", not "how many unique games". Tiered with the exact same
    percentile-bucket system as champions (assign_champion_tiers) -- checked
    live, item sample sizes run comparable to or larger than champions' (an
    item can sit on any of ~9 champion slots/game), so the same reasoning
    that made small-sample shrinkage unnecessary for champions holds here
    too, not assumed."""
    rows = []
    for item, by_champ in item_champ_placements.items():
        placements = [p for pls in by_champ.values() for p in pls]
        n = len(placements)
        if n < MIN_SAMPLE_FOR_ITEM_TIER:
            continue
        rows.append({
            "item": item,
            # pick_count, not just play_count: assign_champion_tiers() (reused
            # as-is below) reads this exact key name for its own eligibility
            # check and tier sort -- same field, kept under both names since
            # "play_count" is what comps/the rest of the site call it.
            "play_count": n, "pick_count": n,
            "pick_rate": round(n / total_participants, 4) if total_participants else 0.0,
            "avg_placement": round(sum(placements) / n, 3),
            "top4_rate": round(sum(1 for p in placements if p <= 4) / n, 4),
            "win_rate": round(sum(1 for p in placements if p == 1) / n, 4),
        })
    return assign_champion_tiers(rows)


def build_global_combo_stats(champs: dict[str, "ChampionAgg"]) -> list[dict]:
    """The Combo Tier List's real numbers: every real 3-completed-item combo
    ever seen, flattened ACROSS every champion that built it (a champion's
    own ChampionAgg.item_combo already tracks this per-champion, for that
    champion's own "Best Items" tab -- this merges all of those into one
    global view, since a strong combo is often strong on more than one
    carry). Same MIN_SAMPLE_FOR_ITEM_TIER bar and assign_champion_tiers()
    percentile tiering as the Item Tier List, for the same reason: checked,
    combo sample sizes run comparable to single items (any 3-item build a
    unit completes counts once per game), so no extra small-sample handling
    needed beyond the existing 100-game floor."""
    global_combo: dict[tuple, list[int]] = {}
    for agg in champs.values():
        for combo, placements in agg.item_combo.items():
            global_combo.setdefault(combo, []).extend(placements)
    rows = []
    for combo, placements in global_combo.items():
        n = len(placements)
        if n < MIN_SAMPLE_FOR_ITEM_TIER:
            continue
        rows.append({
            "items": list(combo),
            "play_count": n, "pick_count": n,
            "avg_placement": round(sum(placements) / n, 3),
            "top4_rate": round(sum(1 for p in placements if p <= 4) / n, 4),
            "win_rate": round(sum(1 for p in placements if p == 1) / n, 4),
        })
    return assign_champion_tiers(rows)


def build_champion_stats(matches: list[dict], total_participants: int, top_items: int = 5,
                          name_map: dict[str, str] | None = None) -> tuple[list[dict], dict[str, list[dict]], list[dict], list[dict]]:
    champs: dict[str, ChampionAgg] = {}
    # item (clean id) -> champion (display name) -> [placement, ...], across
    # every game that champion held that item at all -- feeds
    # build_item_champion_stats() below. A duplicated item on one unit
    # (2x the same completed item) still only counts once per game here
    # (set(complete), not the list) -- this answers "how do games go when
    # this champion holds this item", not "how many copies".
    item_champ_placements: dict[str, dict[str, list[int]]] = {}

    for match in matches:
        for p in match.get("info", {}).get("participants", []):
            placement = p.get("placement")
            if not placement:
                continue
            for u in p.get("units") or []:
                cid = display_name(clean_id(u.get("character_id", "")), name_map)
                if not cid:
                    continue
                agg = champs.get(cid)
                if agg is None:
                    agg = ChampionAgg(id=cid)
                    champs[cid] = agg
                agg.placements.append(placement)
                star = u.get("tier", 1)
                agg.star_levels.append(star)
                if star >= 3:
                    agg.three_star_count += 1
                item_names = u.get("itemNames") or []
                cleaned_items = [clean_id(item) for item in item_names]
                for item in cleaned_items:
                    agg.items[item] += 1
                complete = sorted(i for i in cleaned_items if is_complete_item(i))
                if len(complete) >= 3:
                    combo = tuple(complete[:3])
                    agg.item_combo.setdefault(combo, []).append(placement)
                for item in set(complete):
                    item_champ_placements.setdefault(item, {}).setdefault(cid, []).append(placement)

    rows = []
    for cid, agg in champs.items():
        common_items = [
            {"item": name, "count": count, "rate": round(count / agg.pick_count, 4)}
            for name, count in agg.items.most_common(top_items)
        ]
        rows.append({
            "id": cid,
            "pick_count": agg.pick_count,
            "pick_rate": round(agg.pick_count / total_participants, 4) if total_participants else 0.0,
            "avg_placement": round(agg.avg_placement, 3),
            "top4_rate": round(agg.top4_rate, 4),
            "avg_star_level": round(agg.avg_star_level, 2),
            "three_star_rate": round(agg.three_star_rate, 4),
            "top_items": common_items,
            "item_combo_stats": agg.item_combo_stats()[:15],
        })

    rows.sort(key=lambda r: -r["pick_count"])
    item_stats = build_global_item_stats(item_champ_placements, total_participants)
    combo_stats = build_global_combo_stats(champs)
    return assign_champion_tiers(rows), build_item_champion_stats(item_champ_placements), item_stats, combo_stats


def assign_champion_tiers(rows: list[dict]) -> list[dict]:
    """Same percentile-bucket tiering as the comp tier list (see
    tierlist.TIER_BUCKETS / build_tier_list) -- top4_rate then avg_placement
    among entries with enough picks to trust, ranked S/A/B/C by where they
    fall in that sorted list. Kept as one shared set of buckets so "S" means
    the same thing (top ~12% of what's actually ranked) whether you're
    looking at a comp, a champion, an item, or a 3-item combo.

    Shared by champions, items (build_global_item_stats), AND combos
    (build_global_combo_stats) -- champions/items were checked live and
    don't need shrinkage (smallest ranked sample seen: ~8,000 picks, miles
    above where it would matter), but combos do: a specific 3-item combo is
    far rarer than any single item, and one real anomaly slipped through
    here uncorrected before this was added (a 106-game combo at 92% top4 --
    the exact same small-sample pattern as the comp tier list's own
    Eclipse_Xayah case). Applying the same empirical-Bayes shrinkage here
    unconditionally is safe either way: it barely moves an already-huge
    sample (the correction shrinks toward 0 as play_count grows) and
    properly restrains a thin one, so one shared function stays correct for
    every caller instead of only combos getting a fix."""
    eligible = [r for r in rows if r["pick_count"] >= MIN_SAMPLE_FOR_CHAMPION_TIER]
    if not eligible:
        for r in rows:
            r.setdefault("tier", "?")
            r["has_enough_data"] = False
        return rows

    total_n = sum(r["pick_count"] for r in eligible)
    global_top4_rate = sum(r["top4_rate"] * r["pick_count"] for r in eligible) / total_n if total_n else 0.5

    def shrunk_top4(r: dict) -> float:
        top4_count = r["top4_rate"] * r["pick_count"]
        return (top4_count + SHRINKAGE_PRIOR_GAMES * global_top4_rate) / (r["pick_count"] + SHRINKAGE_PRIOR_GAMES)

    for r in eligible:
        r["ranking_score_top4"] = round(shrunk_top4(r), 4)

    ranked = sorted(eligible, key=lambda r: (-r["ranking_score_top4"], r["avg_placement"]))
    n = len(ranked)
    cursor = 0
    for tier_name, cutoff_fraction in TIER_BUCKETS:
        end = min(n, round(n * cutoff_fraction)) if tier_name != "C" else n
        for r in ranked[cursor:max(end, cursor)]:
            r["tier"] = tier_name
        cursor = max(end, cursor)
    for r in rows:
        r.setdefault("tier", "?")
        r["has_enough_data"] = r["pick_count"] >= MIN_SAMPLE_FOR_CHAMPION_TIER
    return rows
