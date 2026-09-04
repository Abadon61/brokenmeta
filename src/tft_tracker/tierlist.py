"""Aggregate raw (comp, placement) observations into a tier list, and split
each comp's observed ("real") performance from its contest-free ("brute
force") strength.

Core idea (product-validated): a comp that's played a lot gets contested —
copies of its key units/items are split between more players in the same
lobby — so its real average placement drifts worse than its raw power level
would predict. We proxy "how contested" with play_rate (we don't have
per-round shop/roll data), fit a trend of avg_placement vs play_rate across
the whole sampled meta, and use the slope to back out a contest-free
estimate per comp:

    brute_force_placement = avg_placement - slope * play_rate

`slope` is >0 when, across the meta, more-played comps really do place worse
on average (i.e. contest is a real, measurable drag this patch). A comp
whose brute_force_placement is a lot better than its avg_placement is a
"contested" pick: strong in theory, hard to actually hit. A comp where the
two are close is "uncontested": you get what you see.

The front-and-center, human-facing metric is simpler than that regression
output, though: `contestation_index`/`contestation_level`, a plain
percentile rank of play_rate against the rest of the sampled meta — i.e.
"how present is this comp in games right now". brute_force_placement /
contest_drag stay in the output as the underlying math for anyone who wants
it, but the UI should lead with contestation, not the regression numbers.
"""
from __future__ import annotations

import bisect
from collections import Counter
from dataclasses import dataclass, field

from . import config
from .comp_signature import clean_id, derive_comp, display_name, is_complete_item as _is_complete_item


@dataclass
class CompStats:
    key: str
    label: str
    traits: list[str]
    carry: str | None
    placements: list[int] = field(default_factory=list)
    units: Counter = field(default_factory=Counter)  # champion_id -> occurrence count
    unit_cost: dict = field(default_factory=dict)  # champion_id -> cost (1-5), last value seen
    levels: list[int] = field(default_factory=list)  # final board level per game
    gold_lefts: list[int] = field(default_factory=list)  # unspent gold at game end, per game
    last_rounds: list[int] = field(default_factory=list)  # last round reached (elimination/finish), per game
    unit_three_star: Counter = field(default_factory=Counter)  # champion_id -> # of games seen at 3-star
    unit_items: dict = field(default_factory=dict)  # champion_id -> Counter of item names
    item_game_placements: dict = field(default_factory=dict)  # item_name -> [placement, ...], one per game it appeared in (any unit, deduped per game)
    unit_item_combo: dict = field(default_factory=dict)  # champion_id -> dict[(item1,item2,item3) sorted -> [placement, ...]]
    board_variant: dict = field(default_factory=dict)  # tuple(sorted unit set for one game) -> [placement, ...]

    @property
    def play_count(self) -> int:
        return len(self.placements)

    @property
    def avg_level(self) -> float:
        return sum(self.levels) / len(self.levels) if self.levels else 0.0

    @property
    def avg_gold_left(self) -> float:
        return sum(self.gold_lefts) / len(self.gold_lefts) if self.gold_lefts else 0.0

    @property
    def avg_last_round(self) -> float:
        return sum(self.last_rounds) / len(self.last_rounds) if self.last_rounds else 0.0

    # Cost/3-star-rate thresholds calibrated against real sampled data (see
    # the calibration run in project notes): 1-2 cost carries clear 90%+
    # three-star rate almost universally once they're identified as the
    # carry at all (a cheap unit only gets the most items on it through
    # active rerolling -- it's not an accident), so the threshold barely
    # needs to do any filtering there. 3-cost carries are the real
    # dividing line: comps built around one genuinely split roughly into a
    # ~20-55% cluster (leveled into the unit normally) and a ~90%+ cluster
    # (actively rerolled for it) -- 0.65 sits cleanly between them.
    PLAYSTYLE_REROLL_MAX_COST = 3
    PLAYSTYLE_REROLL_MIN_THREE_STAR_RATE = 0.65

    # "Fast N": not about how quickly any one player leveled (unknowable --
    # see docstring below), but about whether THIS ARCHETYPE's placement
    # actually improves once its board reaches N units -- i.e. reaching
    # that board size is this comp's real win condition, not incidental.
    # TFT placement is close to uniform over 1-8, so its standard deviation
    # is already ~2.3 -- at 5 games per side a 1.0 swing is within one
    # standard error and mostly noise (confirmed empirically: at 5 games
    # this flagged comps whose "improvement" came from as few as 2-3 games
    # on the bonus-slot side). 15 games per side pushes the same swing to
    # roughly 1.5 standard errors, which is where the flagged examples
    # started looking like real, repeatable patterns rather than outliers.
    PLAYSTYLE_FAST_MIN_GAMES = 15
    PLAYSTYLE_FAST_MIN_IMPROVEMENT = 1.0  # placement improvement vs the core-only baseline

    # "Slow N": several units at the cost tier that peaks around level N
    # all sitting at an elevated star level -- only reachable by rerolling
    # at that level for a while, not by leveling straight through it.
    PLAYSTYLE_SLOW_LEVELS = [
        (3, "Slow 7", 0.40),  # 3-cost odds peak around level 7
        (4, "Slow 8", 0.15),  # 4-cost odds peak around level 8; 3-starring a 4-cost is rare
        # enough overall that a much lower bar than the 3-cost one still means something.
    ]
    PLAYSTYLE_SLOW_MIN_UNITS = 2  # need at least this many elevated units at the cost tier, not just one

    def _slot_placements(self, core: set, extra_count: int) -> list[int]:
        """Every placement from a game whose exact board was `core` plus
        exactly `extra_count` other units (any others, pooled) -- the same
        board_variant data bonus_slots()/board_variants() use, just grouped
        by how many units were added rather than by which ones."""
        if not core:
            return []
        placements = []
        for units, pls in self.board_variant.items():
            unit_set = set(units)
            if core <= unit_set and len(unit_set - core) == extra_count:
                placements.extend(pls)
        return placements

    def playstyle_tag(self) -> str | None:
        """Real, derivable playstyle signal -- "Reroll", "Fast N", "Slow N"
        or None. Deliberately NOT attempting to infer leveling PACE
        (how quickly any one player went up) -- Riot's Match-V1 only ever
        returns the final board, never a round-by-round level history, so
        that's not observable. What IS observable: whether a cheap carry
        got actively 3-starred (Reroll), whether THIS ARCHETYPE's own
        placement improves once it fields more units (Fast N -- the
        archetype's win condition really is reaching that board size), and
        whether several same-cost-tier units sit at an elevated star level
        (Slow N -- only reachable by rerolling at the level where that
        cost tier's odds peak). At most one tag, checked in that order."""
        if not self.carry or not self.play_count:
            return None

        cost = self.unit_cost.get(self.carry)
        occurrences = self.units.get(self.carry, 0)
        if cost is not None and cost <= self.PLAYSTYLE_REROLL_MAX_COST and occurrences:
            three_star_rate = self.unit_three_star.get(self.carry, 0) / occurrences
            if three_star_rate >= self.PLAYSTYLE_REROLL_MIN_THREE_STAR_RATE:
                return "Reroll"

        core_list = self.core_units()
        core = {u["champion"] for u in core_list}
        if core:
            core_size = len(core)
            core_placements = self._slot_placements(core, 0)
            if len(core_placements) >= self.PLAYSTYLE_FAST_MIN_GAMES:
                core_avg = sum(core_placements) / len(core_placements)
                for extra, label in ((2, f"Fast {core_size + 2}"), (1, f"Fast {core_size + 1}")):
                    slot_placements = self._slot_placements(core, extra)
                    if len(slot_placements) < self.PLAYSTYLE_FAST_MIN_GAMES:
                        continue
                    slot_avg = sum(slot_placements) / len(slot_placements)
                    if core_avg - slot_avg >= self.PLAYSTYLE_FAST_MIN_IMPROVEMENT:
                        return label

            by_cost: dict[int, list[dict]] = {}
            for u in core_list:
                if u["cost"] is not None:
                    by_cost.setdefault(u["cost"], []).append(u)
            for cost_tier, slow_label, min_rate in self.PLAYSTYLE_SLOW_LEVELS:
                elevated = [u for u in by_cost.get(cost_tier, []) if u["threeStarRate"] >= min_rate]
                if len(elevated) >= self.PLAYSTYLE_SLOW_MIN_UNITS:
                    return slow_label

        return None

    def core_units(self, max_units: int = 9, min_frequency: float = 0.25) -> list[dict]:
        """The board a human would actually recognize for this comp: the
        champions that show up often enough across its sampled games
        (ranked by consistency to decide who makes the cut), returned
        sorted by cost ascending (1-cost first) -- how a player reads a
        board left to right, not by how often each piece shows up.

        Capped at 9, not 10: reaching a 10th board slot requires level 10,
        which by itself already strongly correlates with a good placement
        (you only get there in a long, successful game) -- folding a
        marginal 10th unit into the "core" board would credit that unit for
        a correlation that's really about game length. See bonus_slots()
        for that 9th/10th-unit signal shown honestly, as a labeled add-on
        rather than baked into the board everyone sees first."""
        if not self.play_count:
            return []
        ranked = sorted(self.units.items(), key=lambda kv: kv[1], reverse=True)
        picked = []
        for champ_id, count in ranked[:max_units]:
            freq = count / self.play_count
            if freq < min_frequency:
                break
            picked.append((champ_id, freq))
        picked.sort(key=lambda cf: (self.unit_cost.get(cf[0], 99), -cf[1]))

        result = []
        for c, f in picked:
            occurrences = self.units[c]
            three_star_rate = self.unit_three_star.get(c, 0) / occurrences if occurrences else 0.0
            items = self.unit_items.get(c)
            # Keep more than the 3 we'll actually display: raw components
            # get filtered out client-side, so this leaves enough headroom
            # for 3 real combined items to still surface after that filter.
            top_items = [name for name, _ in items.most_common(6)] if items else []
            result.append({
                "champion": c,
                "frequency": round(f, 3),
                "cost": self.unit_cost.get(c),
                "threeStarRate": round(three_star_rate, 3),
                "items": top_items,
            })
        return result

    def board_variants(self, min_games: int = 2, top_n: int = 3) -> list[dict]:
        """Real, no-guessing alternative to a per-stage "path to this comp"
        (Riot's Match-V1 only ever returns the FINAL board, never a
        round-by-round history, so there's no way to know what a player had
        at 2-1/3-2/4-2 -- see comp_signature.py). This instead compares
        actual VERSIONS of this comp's final board: which exact set of units
        showed up together, how often, and how those games went. Not a
        timeline, but a real signal about "what this comp's build actually
        looks like in practice" that doesn't require data we don't have."""
        rows = []
        for units, placements in self.board_variant.items():
            n = len(placements)
            if n < min_games:
                continue
            rows.append({
                "units": list(units),
                "games": n,
                "share": round(n / self.play_count, 3) if self.play_count else 0.0,
                "avgPlacement": round(sum(placements) / n, 3),
            })
        rows.sort(key=lambda r: -r["games"])
        return rows[:top_n]

    def bonus_slots(self, min_games: int = 2) -> dict:
        """Honest version of "does a bonus 9th/10th unit help": among games
        that included the full core board (see core_units(), capped at 9)
        plus exactly one or two extra units, what were those extras and how
        did those specific games place -- shown as an explicit add-on
        rather than folded into the core board itself. Reaching a bigger
        board is itself a strong proxy for a long, already-successful game
        (you need level 10 to even field 10 units), so this is presented as
        "here's what placement looked like when this extra unit was also
        on board", not a causal claim that the extra unit caused it."""
        core = {u["champion"] for u in self.core_units()}
        if not core:
            return {"coreSize": 0, "coreAvgPlacement": None, "coreGames": 0, "plusOne": [], "plusTwo": []}

        core_key = tuple(sorted(core))
        core_placements = self.board_variant.get(core_key, [])

        plus_one: dict[str, list[int]] = {}
        plus_two: dict[tuple[str, str], list[int]] = {}
        for units, placements in self.board_variant.items():
            unit_set = set(units)
            if not core <= unit_set:
                continue
            extra = tuple(sorted(unit_set - core))
            if len(extra) == 1:
                plus_one.setdefault(extra[0], []).extend(placements)
            elif len(extra) == 2:
                plus_two.setdefault(extra, []).extend(placements)

        def rows_from(bucket: dict, to_champs) -> list[dict]:
            out = []
            for key, placements in bucket.items():
                n = len(placements)
                if n < min_games:
                    continue
                out.append({
                    "champions": to_champs(key),
                    "games": n,
                    "avgPlacement": round(sum(placements) / n, 3),
                })
            out.sort(key=lambda r: -r["games"])
            return out

        return {
            "coreSize": len(core),
            "coreAvgPlacement": round(sum(core_placements) / len(core_placements), 3) if len(core_placements) >= min_games else None,
            "coreGames": len(core_placements),
            "plusOne": rows_from(plus_one, lambda k: [k])[:5],
            "plusTwo": rows_from(plus_two, lambda k: list(k))[:3],
        }

    def item_stats(self, min_games: int = 3) -> list[dict]:
        """Real win-rate-by-item for this comp: across every game, which
        items showed up anywhere on the board (deduped per game, so 2 copies
        of the same item in one game only count once), and how that game
        went. Not "this item on this unit" -- just "this item was part of
        the build" -- since Riot's data doesn't let us attribute an item's
        specific impact more precisely than that."""
        rows = []
        for item, placements in self.item_game_placements.items():
            n = len(placements)
            if n < min_games:
                continue
            rows.append({
                "item": item,
                "games": n,
                "pickRate": round(n / self.play_count, 3) if self.play_count else 0.0,
                "avgPlacement": round(sum(placements) / n, 3),
                "top4Rate": round(sum(1 for p in placements if p <= 4) / n, 3),
            })
        rows.sort(key=lambda r: -r["games"])
        return rows

    def item_combo_stats(self, min_games: int = 1, top_n: int = 45) -> list[dict]:
        """Real win-rate-by-3-item-combo, per champion: which exact set of
        3 finished items a unit held together, and how those games went.
        Which champions are worth showing this for (the comp's "main"
        pieces) is a display-layer decision made from `frequency`/item
        count, same as `core_units` -- this returns everything observed,
        unfiltered by champion, ranked by how often each combo occurred.
        Capped at `top_n` (the display layer only ever shows the top 10 per
        champion, across up to 3 focus champions) -- a well-sampled comp can
        otherwise surface dozens of rarely-seen combos that never get shown
        but still bloat every payload that carries this comp."""
        rows = []
        for champ, combos in self.unit_item_combo.items():
            for combo, placements in combos.items():
                n = len(placements)
                if n < min_games:
                    continue
                rows.append({
                    "champion": champ,
                    "items": list(combo),
                    "games": n,
                    "avgPlacement": round(sum(placements) / n, 3),
                    "top4Rate": round(sum(1 for p in placements if p <= 4) / n, 3),
                })
        rows.sort(key=lambda r: -r["games"])
        return rows[:top_n]

    @property
    def avg_placement(self) -> float:
        return sum(self.placements) / len(self.placements) if self.placements else 0.0

    @property
    def top4_rate(self) -> float:
        if not self.placements:
            return 0.0
        return sum(1 for p in self.placements if p <= 4) / len(self.placements)

    @property
    def win_rate(self) -> float:
        if not self.placements:
            return 0.0
        return sum(1 for p in self.placements if p == 1) / len(self.placements)


def collect_participant_observations(matches: list[dict], name_map: dict[str, str] | None = None,
                                      item_offense: dict[str, str] | None = None
                                      ) -> tuple[list[tuple[str, int]], dict[str, CompStats]]:
    """Returns (observations, comp_stats_by_key). `observations` is a flat
    list of (comp_key, placement) — one per participant per match — used
    later by the matchup proxy module without re-parsing matches.

    `name_map` corrects Riot's leftover dev-codename apiNames (e.g. "Sentry"
    -> "Pebbles") to the champion's real released name -- see
    comp_signature.display_name. Applied consistently to every champion
    identity in the output (core units, carry, comp label) so they all stay
    in the same name space and keep cross-referencing correctly.

    `item_offense` (see champion_images.classify_item_offense) is what lets
    derive_comp() tell an itemized tank from the real carry -- must be the
    same map passed everywhere else derive_comp() runs on this same match
    pool (matchup_proxy, leaderboard), same reason as name_map: the derived
    comp `key` has to agree everywhere or cross-references break."""
    comps: dict[str, CompStats] = {}
    observations: list[tuple[str, int]] = []

    for match in matches:
        for p in match.get("info", {}).get("participants", []):
            placement = p.get("placement")
            if not placement:
                continue
            sig = derive_comp(p, name_map=name_map, item_offense=item_offense)
            stats = comps.get(sig.key)
            if stats is None:
                stats = CompStats(key=sig.key, label=sig.label, traits=sig.traits, carry=sig.carry)
                comps[sig.key] = stats
            stats.placements.append(placement)
            level = p.get("level")
            if level:
                stats.levels.append(level)
            gold_left = p.get("gold_left")
            if gold_left is not None:
                stats.gold_lefts.append(gold_left)
            last_round = p.get("last_round")
            if last_round is not None:
                stats.last_rounds.append(last_round)
            game_items = set()
            game_units = set()
            for u in p.get("units") or []:
                champ_id = display_name(clean_id(u.get("character_id", "")), name_map)
                if champ_id:
                    stats.units[champ_id] += 1
                    game_units.add(champ_id)
                    rarity = u.get("rarity")
                    if rarity is not None:
                        stats.unit_cost[champ_id] = rarity + 1  # API rarity is 0-indexed cost
                    if u.get("tier", 0) >= 3:
                        stats.unit_three_star[champ_id] += 1
                    item_names = u.get("itemNames") or []
                    if item_names:
                        counter = stats.unit_items.setdefault(champ_id, Counter())
                        cleaned_items = []
                        for item in item_names:
                            cleaned = clean_id(item)
                            counter[cleaned] += 1
                            game_items.add(cleaned)
                            cleaned_items.append(cleaned)
                        complete = sorted(i for i in cleaned_items if _is_complete_item(i))
                        if len(complete) >= 3:
                            combo = tuple(complete[:3])
                            combo_map = stats.unit_item_combo.setdefault(champ_id, {})
                            combo_map.setdefault(combo, []).append(placement)
            for item in game_items:
                stats.item_game_placements.setdefault(item, []).append(placement)
            if game_units:
                stats.board_variant.setdefault(tuple(sorted(game_units)), []).append(placement)
            observations.append((sig.key, placement))

    return observations, comps


def _weighted_linear_regression(xs: list[float], ys: list[float], weights: list[float]) -> tuple[float, float]:
    """Closed-form weighted least squares for y = intercept + slope * x.
    Pure-python (no numpy dependency) since it's just 2 unknowns."""
    sw = sum(weights)
    if sw == 0:
        return 0.0, 0.0
    x_bar = sum(w * x for w, x in zip(weights, xs)) / sw
    y_bar = sum(w * y for w, y in zip(weights, ys)) / sw
    num = sum(w * (x - x_bar) * (y - y_bar) for w, x, y in zip(weights, xs, ys))
    den = sum(w * (x - x_bar) ** 2 for w, x in zip(weights, xs))
    if den == 0:
        return y_bar, 0.0
    slope = num / den
    intercept = y_bar - slope * x_bar
    return intercept, slope


def compute_contest_adjustment(comps: dict[str, CompStats], min_sample: int) -> tuple[float, float]:
    eligible = [c for c in comps.values() if c.play_count >= min_sample]
    if len(eligible) < 3:
        return 0.0, 0.0  # not enough distinct comps to fit a trend safely
    xs = [c.play_count for c in eligible]  # play_rate needs total; use raw count as weight-proportional x
    total = sum(xs)
    play_rates = [x / total for x in xs]
    ys = [c.avg_placement for c in eligible]
    weights = [float(c.play_count) for c in eligible]
    intercept, slope = _weighted_linear_regression(play_rates, ys, weights)
    return intercept, slope


# Cumulative fraction of ranked comps (best-performing first) that falls in
# each tier: top 12% -> S, next 28% (cumulative 40%) -> A, next 35%
# (cumulative 75%) -> B, remaining 25% -> C.
TIER_BUCKETS = [
    ("S", 0.12),
    ("A", 0.40),
    ("B", 0.75),
    ("C", 1.01),
]

MERGE_MIN_RATIO = 0.7  # smaller comp must retain at least this fraction of the parent's unit count
MERGE_MIN_PLAY_COUNT = 2  # candidates below this aren't worth comparing (pure noise)

# A real final board in this set runs 7-9 units. Anything derive_comp() built
# around fewer than that isn't a deliberate archetype -- it's almost always
# an early elimination (a handful of units at time of death, sometimes just
# one, e.g. "Generic Gnar": no traits active yet, one unit on board) getting
# swept up as if it were a comp because it technically has a carry and a
# key. Filtered out entirely rather than tiered/displayed at all -- unlike
# the has_enough_data ("?") cut in the export step, this isn't about sample
# size, it's that these were never a real composition to begin with.
MIN_CORE_BOARD_SIZE = 7

# A board where every single unit is a 5-cost isn't a strategy -- nobody
# builds TOWARD that (you can't economize or level for a specific 5-cost the
# way you can plan around a cheap carry, see derive_comp()'s carry
# exclusion). It's what a very long, very lucky game looks like once it's
# over: whatever 5-costs got found along the way, kept because nothing
# better came up. Real archetypes always anchor on a 1-4 cost unit that was
# actually built around; an all-5-cost board is that outcome, not a plan,
# so it's dropped the same way an under-sized board is.


def _is_all_five_cost(core_units: list[dict]) -> bool:
    return bool(core_units) and all(u.get("cost") == 5 for u in core_units)


def _near_miss_ratio(parent_units: set, other_units: set) -> float | None:
    """None unless `other` looks like an incomplete attempt at `parent`:
    every one of its units is also in parent (a STRICT subset, not just
    high overlap) -- so this only catches "missing a unit or two", never
    two same-size boards that differ by carry choice (e.g. a shared shell
    that can be finished with either of two different carries -- a real,
    separate signal worth keeping as its own comp, not a near-miss of the
    other). Returns how much of parent's board `other` actually has."""
    if not other_units or not (other_units < parent_units):
        return None
    return len(other_units) / len(parent_units)


def _merge_similar_comps(rows: list[dict], min_ratio: float = MERGE_MIN_RATIO) -> list[dict]:
    """Folds near-miss comps into the more-played one instead of listing
    them as separate archetypes. This happens more than it looks: losing
    just one unit can shift which trait reads as "most active" (derive_comp()
    picks the single dominant one by a threshold), so someone who meant to
    build a comp but came up a unit or two short can get tagged with a
    different key entirely, even though their board is a strict subset of
    the real thing. Left alone, that fragments the sample across
    near-duplicate rows instead of pooling it into one.

    The absorbed comp's own real numbers are never blended into the
    parent's (that would quietly change the parent's avg_placement etc.
    based on a merge heuristic) -- they're attached as `similar_variants`,
    shown as their own honest data point, same spirit as bonus_slots."""
    candidates = [r for r in rows if r["play_count"] >= MERGE_MIN_PLAY_COUNT and r["core_units"]]
    unit_sets = {r["key"]: {u["champion"] for u in r["core_units"]} for r in candidates}
    # Most-played first: whichever comp has the deeper sample becomes the
    # parent any smaller, sufficiently-similar comp gets folded into.
    candidates.sort(key=lambda r: -r["play_count"])

    absorbed: set[str] = set()
    similar_variants: dict[str, list[dict]] = {}

    for i, parent in enumerate(candidates):
        if parent["key"] in absorbed:
            continue
        parent_units = unit_sets[parent["key"]]
        for other in candidates[i + 1:]:
            if other["key"] in absorbed:
                continue
            ratio = _near_miss_ratio(parent_units, unit_sets[other["key"]])
            if ratio is not None and ratio >= min_ratio:
                absorbed.add(other["key"])
                similar_variants.setdefault(parent["key"], []).append({
                    "key": other["key"],
                    "label": other["label"],
                    "carry": other["carry"],
                    "playCount": other["play_count"],
                    "avgPlacement": other["avg_placement"],
                    "top4Rate": other["top4_rate"],
                    "boardSize": len(unit_sets[other["key"]]),
                })

    result = []
    for r in rows:
        if r["key"] in absorbed:
            continue
        variants = similar_variants.get(r["key"], [])
        variants.sort(key=lambda v: -v["playCount"])
        r["similar_variants"] = variants
        result.append(r)
    return result


def _contestation_level(percentile: float) -> str:
    if percentile >= 66.0:
        return "High"
    if percentile >= 33.0:
        return "Medium"
    return "Low"


def build_tier_list(comps: dict[str, CompStats], total_participants: int) -> tuple[list[dict], dict]:
    intercept, slope = compute_contest_adjustment(comps, config.MIN_SAMPLE_FOR_TIER)

    # Percentile rank of play_rate, but only against other comps that actually
    # made the cut (>= MIN_SAMPLE_FOR_TIER observations) — i.e. the real
    # sampled meta shown on the tier list. Ranking against the huge long tail
    # of one-off boards would make every tiered comp read as "High" contest,
    # since they already sit above thousands of singletons by construction.
    meta_play_rates = sorted(
        (c.play_count / total_participants if total_participants else 0.0)
        for c in comps.values() if c.play_count >= config.MIN_SAMPLE_FOR_TIER
    )

    rows = []
    for c in comps.values():
        play_rate = c.play_count / total_participants if total_participants else 0.0
        contest_drag = slope * play_rate
        brute_force_placement = c.avg_placement - contest_drag
        percentile = (
            (bisect.bisect_right(meta_play_rates, play_rate) / len(meta_play_rates)) * 100
            if meta_play_rates else 0.0
        )
        rows.append({
            "key": c.key,
            "label": c.label,
            "playstyle_tag": c.playstyle_tag(),
            "traits": c.traits,
            "carry": c.carry,
            "core_units": c.core_units(),
            "item_stats": c.item_stats(),
            "item_combo_stats": c.item_combo_stats(),
            "board_variants": c.board_variants(),
            "bonus_slots": c.bonus_slots(),
            "avg_level": round(c.avg_level, 2),
            "level_badge": f"Niveau {round(c.avg_level)}" if c.levels else "",
            "avg_gold_left": round(c.avg_gold_left, 2),
            "avg_last_round": round(c.avg_last_round, 2),
            "play_count": c.play_count,
            "play_rate": round(play_rate, 4),
            "contestation_index": round(percentile, 1),
            "contestation_level": _contestation_level(percentile),
            "avg_placement": round(c.avg_placement, 3),
            "top4_rate": round(c.top4_rate, 4),
            "win_rate": round(c.win_rate, 4),
            "brute_force_placement": round(brute_force_placement, 3),
            "contest_drag": round(contest_drag, 3),
            "tier": None,  # filled in below
            "has_enough_data": c.play_count >= config.MIN_SAMPLE_FOR_TIER,
        })

    rows = [r for r in rows if len(r["core_units"]) >= MIN_CORE_BOARD_SIZE
            and not _is_all_five_cost(r["core_units"])]
    rows = _merge_similar_comps(rows)

    ranked = sorted(
        (r for r in rows if r["has_enough_data"]),
        key=lambda r: (-r["top4_rate"], r["avg_placement"]),
    )
    n = len(ranked)
    cursor = 0
    for tier_name, cutoff_fraction in TIER_BUCKETS:
        end = min(n, round(n * cutoff_fraction)) if tier_name != "C" else n
        for r in ranked[cursor:max(end, cursor)]:
            r["tier"] = tier_name
        cursor = max(end, cursor)

    unranked = [r for r in rows if not r["has_enough_data"]]
    for r in unranked:
        r["tier"] = "?"

    all_rows = ranked + unranked
    all_rows.sort(key=lambda r: (r["tier"] == "?", {"S": 0, "A": 1, "B": 2, "C": 3, "?": 4}[r["tier"]], r["avg_placement"]))
    return all_rows, {"regression_intercept": round(intercept, 3), "regression_slope": round(slope, 3)}
