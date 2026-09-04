"""Matchup "counter" proxy.

Riot's Match-V1 does not expose who fought whom each round (no fight-pairing
data is public), so a literal round-by-round matchup analysis isn't possible
from official data. This is the agreed proxy instead: within each real lobby
(8 players), for every pair of distinct comps present together, whichever one
placed better counts as "ahead" of the other that game. Aggregated across
many lobbies this surfaces comps that consistently out-place another comp
when they land in the same game — a genuine signal about the meta, just not
literal combat log data.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from . import config
from .comp_signature import derive_comp


def build_matchup_table(matches: list[dict], min_encounters: int = 5,
                         name_map: dict[str, str] | None = None,
                         item_offense: dict[str, str] | None = None) -> list[dict]:
    """`name_map` (Riot apiName -> real released name, see
    comp_signature.display_name) and `item_offense` (see
    champion_images.classify_item_offense, used for carry detection) must
    be the same maps passed to collect_participant_observations() for a
    given payload -- comp `key`s are derived the same way in both places
    and need to agree for matchup rows to line up with the tier list's
    comps by key."""
    pair_ahead: dict[tuple[str, str], int] = defaultdict(int)
    pair_total: dict[tuple[str, str], int] = defaultdict(int)
    labels: dict[str, str] = {}

    for match in matches:
        participants = match.get("info", {}).get("participants", [])
        lobby = []
        for p in participants:
            placement = p.get("placement")
            if not placement:
                continue
            sig = derive_comp(p, name_map=name_map, item_offense=item_offense)
            labels[sig.key] = sig.label
            lobby.append((sig.key, placement))

        for (key_a, place_a), (key_b, place_b) in combinations(lobby, 2):
            if key_a == key_b:
                continue
            pair = tuple(sorted((key_a, key_b)))
            pair_total[pair] += 1
            better = key_a if place_a < place_b else key_b
            pair_ahead[(pair, better)] += 1  # type: ignore[index]

    rows = []
    for pair, total in pair_total.items():
        if total < min_encounters:
            continue
        a, b = pair
        a_ahead = pair_ahead.get((pair, a), 0)
        b_ahead = pair_ahead.get((pair, b), 0)
        rows.append({
            "comp_a": a,
            "comp_a_label": labels.get(a, a),
            "comp_b": b,
            "comp_b_label": labels.get(b, b),
            "encounters": total,
            "a_ahead_rate": round(a_ahead / total, 4),
            "b_ahead_rate": round(b_ahead / total, 4),
        })

    rows.sort(key=lambda r: -r["encounters"])
    return rows
