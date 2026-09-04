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
from .tierlist import TIER_BUCKETS

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


def build_champion_stats(matches: list[dict], total_participants: int, top_items: int = 5,
                          name_map: dict[str, str] | None = None) -> list[dict]:
    champs: dict[str, ChampionAgg] = {}

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
    return assign_champion_tiers(rows)


def assign_champion_tiers(rows: list[dict]) -> list[dict]:
    """Same percentile-bucket tiering as the comp tier list (see
    tierlist.TIER_BUCKETS / build_tier_list) -- top4_rate then avg_placement
    among champions with enough picks to trust, ranked S/A/B/C by where they
    fall in that sorted list. Kept as one shared set of buckets so "S" means
    the same thing (top ~12% of what's actually ranked) whether you're
    looking at a comp or a single champion."""
    eligible = [r for r in rows if r["pick_count"] >= MIN_SAMPLE_FOR_CHAMPION_TIER]
    ranked = sorted(eligible, key=lambda r: (-r["top4_rate"], r["avg_placement"]))
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
