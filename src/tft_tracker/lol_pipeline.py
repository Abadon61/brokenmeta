"""CLI entry point: region/tier brackets -> real LoL matches -> real
champion pick-rate/win-rate by role. Sibling of pipeline.py (TFT), same
sampling philosophy (seed players from real ladders, pull their recent
ranked matches, dedupe, aggregate) but reads ALL 10 participants of every
fetched match (not just the seed player) -- a LoL match already gives a
free, real role tag per participant (individualPosition), so there is no
reason to throw away 9/10 of the signal the way a single-comp TFT match
would (TFT's own tierlist.py already does the analogous "read every
participant" thing for build_tier_list, this mirrors that logic for LoL).

Output: data/output/lol_champion_role_stats.json, consumed by
site_build/build_site.py to replace the honest "en développement" badge on
/league/glossaire/champions/<slug>/ with real pick rate / win rate by role,
for every champion+role combination that clears MIN_SAMPLE_PER_ROLE.

Example:
    py lol_run.py                                   # EUW,NA,BR,KR / GOLD,PLATINUM,DIAMOND,MASTER+
    py lol_run.py --regions EUW,KR --tiers DIAMOND
    py lol_run.py --all-tiers
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .lol_riot_client import LOL_REGIONS, LANE_TO_ROLE, QUEUE_SOLO, LolRiotClient

SUB_APEX_TIERS = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND"]
APEX_TIERS = ["MASTER", "GRANDMASTER", "CHALLENGER"]
ALL_TIERS = SUB_APEX_TIERS + APEX_TIERS
DEFAULT_TIERS = ["GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
DIVISIONS_SAMPLED = ["I", "II", "III"]

PLAYERS_PER_BRACKET = 150
MATCH_IDS_PER_PLAYER = 4     # kept low: 10 usable rows/match already multiplies this 10x downstream
MAX_MATCHES_PER_BRACKET = 300
MIN_SAMPLE_PER_ROLE = 20     # min games on a champion+role before it gets a real pick/win rate
MIN_SAMPLE_PER_ITEM = 15     # min games with an item on a champion before it gets a real pick/win rate
MAX_ITEMS_PER_CHAMPION = 15  # keep the JSON (and the site's "best items" table) to a real top slice
MIN_SAMPLE_PER_MATCHUP = 10  # min games in a specific lane matchup before it gets a real win rate
MAX_MATCHUPS_PER_CHAMPION = 15
MIN_SAMPLE_PER_RUNE_PAGE = 15  # min games on a keystone+secondary-tree combo before it gets a real pick/win rate
MAX_RUNE_PAGES_PER_CHAMPION = 8  # a champion realistically only has a handful of real rune page identities

OUTPUT_PATH = f"{config.OUTPUT_DIR}/lol_champion_role_stats.json"


@dataclass
class BracketSample:
    region: str
    tier: str
    seed_puuids: list[str] = field(default_factory=list)
    match_ids: set[str] = field(default_factory=set)
    matches: list[dict] = field(default_factory=list)


def _seed_puuids_for_bracket(client: LolRiotClient, platform: str, tier: str) -> list[str]:
    if tier in APEX_TIERS:
        data = client.get_apex_league(platform, tier)
        entries = data.get("entries") or []
        entries_sorted = sorted(entries, key=lambda e: e.get("leaguePoints", 0), reverse=True)
        return _resolve_puuids(client, platform, entries_sorted[:PLAYERS_PER_BRACKET])

    entries: list[dict] = []
    for division in DIVISIONS_SAMPLED:
        if len(entries) >= PLAYERS_PER_BRACKET:
            break
        entries.extend(client.get_league_entries(platform, tier, division, page=1))
    return _resolve_puuids(client, platform, entries[:PLAYERS_PER_BRACKET])


def _resolve_puuids(client: LolRiotClient, platform: str, entries: list[dict]) -> list[str]:
    """Riot's League-V4 entries now include puuid directly on most of these
    endpoints (verified live this session) -- fall back to the
    summonerId -> summoner-by-id -> puuid hop only for the rare entry that
    doesn't have one, rather than assuming either shape."""
    puuids: list[str] = []
    for e in entries:
        if e.get("puuid"):
            puuids.append(e["puuid"])
        elif e.get("summonerId"):
            summoner = client.get_summoner_by_id(platform, e["summonerId"])
            if summoner and summoner.get("puuid"):
                puuids.append(summoner["puuid"])
    return puuids


def collect_bracket(client: LolRiotClient, region: str, tier: str) -> BracketSample:
    platform = LOL_REGIONS[region]["platform"]
    regional = LOL_REGIONS[region]["regional"]

    sample = BracketSample(region=region, tier=tier)
    sample.seed_puuids = _seed_puuids_for_bracket(client, platform, tier)

    for puuid in sample.seed_puuids:
        if len(sample.match_ids) >= MAX_MATCHES_PER_BRACKET:
            break
        ids = client.get_match_ids_by_puuid(regional, puuid, count=MATCH_IDS_PER_PLAYER)
        for mid in ids:
            if len(sample.match_ids) >= MAX_MATCHES_PER_BRACKET:
                break
            sample.match_ids.add(mid)

    for mid in sample.match_ids:
        match = client.get_match(regional, mid)
        if not match:
            continue
        info = match.get("info", {})
        if info.get("queueId") != QUEUE_SOLO:
            continue
        sample.matches.append(match)

    return sample


def load_matches_from_cache(cache_dir: str = "data/raw_lol") -> list[dict]:
    """Every ranked-solo match already sitting in the local disk cache
    (each API-collection run writes one file per match id, immutable once
    played) -- lets item/matchup aggregation be added and recomputed for
    free against everything already fetched, no new Riot API calls. Same
    idea as pipeline.py's --from-cache for TFT; region/tier bracket
    membership isn't recoverable this way (that's a property of the seed
    player at collection time, not of the match itself), so a from-cache
    run's `regions`/`tiers` output fields just say so."""
    matches = []
    for path in Path(cache_dir).glob("*.json"):
        try:
            match = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if match.get("info", {}).get("queueId") == QUEUE_SOLO:
            matches.append(match)
    return matches


def aggregate(matches: list[dict]) -> dict:
    """champion -> role -> {games, wins}, reading all 10 participants of
    every match (not just a seed player) -- see module docstring. Also
    tallies item picks, lane matchups and rune pages off the exact same
    participant rows, at no extra API cost (the items/opposing laner/perks
    are already sitting right there in each match already fetched for the
    role stats)."""
    stats: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: {"games": 0, "wins": 0}))
    item_stats: dict[str, dict[int, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: {"games": 0, "wins": 0}))
    matchup_stats: dict[str, dict[str, dict[str, dict[str, int]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"games": 0, "wins": 0})))
    # Keyed by (keystone_perk_id, secondary_tree_style_id) -- that pair is
    # a rune page's real identity (e.g. "Electrocute + Precision secondary"),
    # not just the keystone alone.
    rune_stats: dict[str, dict[tuple[int, int], dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: {"games": 0, "wins": 0}))
    seen_match_ids: set[str] = set()
    total_rows = 0
    for match in matches:
        mid = match.get("metadata", {}).get("matchId")
        if not mid or mid in seen_match_ids:
            continue  # a match can be re-fetched across brackets/regions sharing a seed player
        seen_match_ids.add(mid)
        participants = match.get("info", {}).get("participants", [])

        by_role_team: dict[tuple[str, int], dict] = {}
        for p in participants:
            champ = p.get("championName")
            role = LANE_TO_ROLE.get(p.get("individualPosition"))
            if not champ or not role:
                continue
            win = bool(p.get("win"))
            row = stats[champ][role]
            row["games"] += 1
            if win:
                row["wins"] += 1
            total_rows += 1

            for item_id in (p.get(f"item{i}") for i in range(7)):
                if not item_id:
                    continue  # 0 = empty slot
                irow = item_stats[champ][item_id]
                irow["games"] += 1
                if win:
                    irow["wins"] += 1

            styles = (p.get("perks") or {}).get("styles") or []
            if len(styles) == 2 and styles[0].get("selections") and styles[1].get("style"):
                keystone = styles[0]["selections"][0].get("perk")
                secondary_tree = styles[1]["style"]
                if keystone and secondary_tree:
                    rrow = rune_stats[champ][(keystone, secondary_tree)]
                    rrow["games"] += 1
                    if win:
                        rrow["wins"] += 1

            by_role_team[(role, p.get("teamId"))] = {"champion": champ, "win": win}

        # Pair each role's two occupants (one per team) into a real lane
        # matchup -- both directions recorded (A-vs-B and B-vs-A), since
        # each is its own useful "how does X fare into Y" lookup.
        roles_seen = {role for role, _ in by_role_team}
        for role in roles_seen:
            sides = [v for (r, _team), v in by_role_team.items() if r == role]
            if len(sides) != 2:
                continue  # a role missing on one side (e.g. no jungler logged) -- skip, not a real 1v1
            a, b = sides
            if a["champion"] == b["champion"]:
                continue  # mirror matchup: not a meaningful counter signal
            row_a = matchup_stats[role][a["champion"]][b["champion"]]
            row_a["games"] += 1
            if a["win"]:
                row_a["wins"] += 1
            row_b = matchup_stats[role][b["champion"]][a["champion"]]
            row_b["games"] += 1
            if b["win"]:
                row_b["wins"] += 1

    return {
        "stats": stats, "item_stats": item_stats, "matchup_stats": matchup_stats, "rune_stats": rune_stats,
        "unique_matches": len(seen_match_ids), "total_rows": total_rows,
    }


def build_output(stats: dict[str, dict[str, dict[str, int]]], regions: list[str], tiers: list[str],
                  unique_matches: int, total_rows: int) -> dict:
    role_totals: dict[str, int] = defaultdict(int)
    for champ_roles in stats.values():
        for role, row in champ_roles.items():
            role_totals[role] += row["games"]

    by_champion: dict[str, dict] = {}
    for champ, roles in stats.items():
        champ_roles_out = {}
        total_games = 0
        for role, row in roles.items():
            total_games += row["games"]
            if row["games"] < MIN_SAMPLE_PER_ROLE:
                continue
            champ_roles_out[role] = {
                "games": row["games"],
                "wins": row["wins"],
                "win_rate": round(row["wins"] / row["games"], 4),
                "pick_rate": round(row["games"] / role_totals[role], 4) if role_totals[role] else 0,
            }
        if champ_roles_out:
            by_champion[champ] = {"roles": champ_roles_out, "total_games": total_games}

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "regions": regions, "tiers": tiers,
        "unique_matches": unique_matches, "total_participant_rows": total_rows,
        "min_sample_per_role": MIN_SAMPLE_PER_ROLE,
        "role_totals": dict(role_totals),
        "by_champion": by_champion,
    }


def build_item_output(item_stats: dict[str, dict[int, dict[str, int]]], champ_total_games: dict[str, int],
                       regions: list[str], tiers: list[str]) -> dict:
    """Per champion, its real most-built items (own win rate holding that
    item, own pick rate = games with it / champion's own total games --
    NOT normalized against other champions, since an item's baseline pick
    rate is a champion-specific question: 'how often do Ahri players buy
    this', not 'how often does anyone in the game')."""
    by_champion: dict[str, list[dict]] = {}
    for champ, items in item_stats.items():
        total = champ_total_games.get(champ, 0)
        if not total:
            continue
        rows = []
        for item_id, row in items.items():
            if row["games"] < MIN_SAMPLE_PER_ITEM:
                continue
            rows.append({
                "item_id": item_id, "games": row["games"], "wins": row["wins"],
                "win_rate": round(row["wins"] / row["games"], 4),
                "pick_rate": round(row["games"] / total, 4),
            })
        rows.sort(key=lambda r: -r["games"])
        if rows:
            by_champion[champ] = rows[:MAX_ITEMS_PER_CHAMPION]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "regions": regions, "tiers": tiers,
        "min_sample_per_item": MIN_SAMPLE_PER_ITEM,
        "by_champion": by_champion,
    }


def build_matchup_output(matchup_stats: dict[str, dict[str, dict[str, dict[str, int]]]],
                          regions: list[str], tiers: list[str]) -> dict:
    """role -> champion -> real lane opponents it has faced, each with its
    real win rate specifically against that opponent (not its overall
    win rate) -- a real counter-pick signal, from the exact same matches
    already collected for the role stats (see aggregate())."""
    by_role: dict[str, dict[str, list[dict]]] = {}
    for role, champs in matchup_stats.items():
        role_out: dict[str, list[dict]] = {}
        for champ, enemies in champs.items():
            rows = []
            for enemy, row in enemies.items():
                if row["games"] < MIN_SAMPLE_PER_MATCHUP:
                    continue
                rows.append({
                    "enemy": enemy, "games": row["games"], "wins": row["wins"],
                    "win_rate": round(row["wins"] / row["games"], 4),
                })
            rows.sort(key=lambda r: -r["games"])
            if rows:
                role_out[champ] = rows[:MAX_MATCHUPS_PER_CHAMPION]
        if role_out:
            by_role[role] = role_out
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "regions": regions, "tiers": tiers,
        "min_sample_per_matchup": MIN_SAMPLE_PER_MATCHUP,
        "by_role": by_role,
    }


def build_rune_output(rune_stats: dict[str, dict[tuple[int, int], dict[str, int]]], champ_total_games: dict[str, int],
                       regions: list[str], tiers: list[str]) -> dict:
    """Per champion, its real most-played rune pages (keystone + secondary
    tree combo), same pick/win-rate philosophy as build_item_output: pick
    rate is against the champion's own total games, not the whole field."""
    by_champion: dict[str, list[dict]] = {}
    for champ, pages in rune_stats.items():
        total = champ_total_games.get(champ, 0)
        if not total:
            continue
        rows = []
        for (keystone, secondary_tree), row in pages.items():
            if row["games"] < MIN_SAMPLE_PER_RUNE_PAGE:
                continue
            rows.append({
                "keystone_id": keystone, "secondary_tree_id": secondary_tree,
                "games": row["games"], "wins": row["wins"],
                "win_rate": round(row["wins"] / row["games"], 4),
                "pick_rate": round(row["games"] / total, 4),
            })
        rows.sort(key=lambda r: -r["games"])
        if rows:
            by_champion[champ] = rows[:MAX_RUNE_PAGES_PER_CHAMPION]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "regions": regions, "tiers": tiers,
        "min_sample_per_rune_page": MIN_SAMPLE_PER_RUNE_PAGE,
        "by_champion": by_champion,
    }


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect real LoL ranked matches and compute real champion pick/win rate by role.")
    p.add_argument("--regions", default=",".join(LOL_REGIONS.keys()))
    p.add_argument("--tiers", default=",".join(DEFAULT_TIERS), help=f"Comma-separated ranks among {ALL_TIERS}")
    p.add_argument("--all-tiers", action="store_true", help="Sample every rank from IRON to CHALLENGER (overrides --tiers).")
    p.add_argument("--no-cache", action="store_true", help="Ignore the local raw-match cache.")
    p.add_argument("--from-cache", action="store_true",
                    help="Recompute role/item/matchup stats from every ranked match already sitting in "
                         "data/raw_lol/, with NO live API calls at all. Ignores --regions/--tiers (a cached "
                         "match's bracket isn't recoverable) -- output says 'from-cache' instead.")
    p.add_argument("--out", default=OUTPUT_PATH)
    p.add_argument("--items-out", default=f"{config.OUTPUT_DIR}/lol_champion_items.json")
    p.add_argument("--matchups-out", default=f"{config.OUTPUT_DIR}/lol_matchups.json")
    p.add_argument("--runes-out", default=f"{config.OUTPUT_DIR}/lol_champion_runes.json")
    return p.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    regions = [r.strip().upper() for r in args.regions.split(",") if r.strip()]
    tiers = ALL_TIERS if args.all_tiers else [t.strip().upper() for t in args.tiers.split(",") if t.strip()]

    if args.from_cache:
        print("Loading every ranked match already in data/raw_lol/ (no live API calls)...")
        all_matches = load_matches_from_cache()
        regions, tiers = ["from-cache"], ["from-cache"]
        request_count = 0
    else:
        client = LolRiotClient(use_cache=not args.no_cache)
        all_matches = []
        for region in regions:
            for tier in tiers:
                print(f"== {region} / {tier} ==")
                sample = collect_bracket(client, region, tier)
                print(f"   seed players: {len(sample.seed_puuids)} | unique matches: {len(sample.match_ids)} | ranked matches kept: {len(sample.matches)}")
                all_matches.extend(sample.matches)
        request_count = client.request_count

    agg = aggregate(all_matches)
    print(f"\nCollected {agg['unique_matches']} unique ranked matches, {agg['total_rows']} champion+role rows "
          f"across {len(regions)} region(s) / {len(tiers)} tier(s) ({request_count} API requests).")

    output = build_output(agg["stats"], regions, tiers, agg["unique_matches"], agg["total_rows"])
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Champion role stats written to {out_path} ({len(output['by_champion'])} champions with at least one qualifying role).")

    champ_total_games = {champ: sum(r["games"] for r in roles.values()) for champ, roles in agg["stats"].items()}
    item_output = build_item_output(agg["item_stats"], champ_total_games, regions, tiers)
    items_path = Path(args.items_out)
    items_path.parent.mkdir(parents=True, exist_ok=True)
    items_path.write_text(json.dumps(item_output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Champion item stats written to {items_path} ({len(item_output['by_champion'])} champions with at least one qualifying item).")

    matchup_output = build_matchup_output(agg["matchup_stats"], regions, tiers)
    matchups_path = Path(args.matchups_out)
    matchups_path.parent.mkdir(parents=True, exist_ok=True)
    matchups_path.write_text(json.dumps(matchup_output, indent=2, ensure_ascii=False), encoding="utf-8")
    total_matchup_champs = sum(len(v) for v in matchup_output["by_role"].values())
    print(f"Lane matchups written to {matchups_path} ({total_matchup_champs} role+champion combos with at least one qualifying matchup).")

    rune_output = build_rune_output(agg["rune_stats"], champ_total_games, regions, tiers)
    runes_path = Path(args.runes_out)
    runes_path.parent.mkdir(parents=True, exist_ok=True)
    runes_path.write_text(json.dumps(rune_output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Champion rune pages written to {runes_path} ({len(rune_output['by_champion'])} champions with at least one qualifying rune page).")


if __name__ == "__main__":
    main()
