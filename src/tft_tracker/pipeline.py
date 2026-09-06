"""CLI entry point: region/tier brackets -> real matches -> tier list JSON.

Examples:
    py run.py                                   # EUW,NA,BR,KR / PLATINUM only
    py run.py --tiers PLATINUM,DIAMOND
    py run.py --all-tiers --regions EUW
    py run.py --regions EUW,KR --matchups
    py run.py --matchups --by-region            # also compute one tier list per region
    py run.py --all-tiers --matchups --by-region --by-rank-bracket
                                                 # full Iron-Challenger sample, sliced by
                                                 # region AND by rank bracket (2 independent axes)
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import requests

from . import config
from .analysis import build_report, load_benchmarks, load_matchups
from .champion_images import build_champion_image_map, classify_item_offense
from .champion_stats import build_champion_stats
from .collector import collect_bracket
from .comp_signature import derive_comp
from .leaderboard import collect_leaderboard
from .matchup_proxy import build_matchup_table
from .riot_client import RiotClient
from .tierlist import build_tier_list, collect_participant_observations


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect real TFT matches and compute a data-driven tier list.")
    p.add_argument("--regions", default=",".join(config.DEFAULT_REGIONS),
                    help=f"Comma-separated region codes among {list(config.REGIONS)}")
    p.add_argument("--tiers", default=",".join(config.DEFAULT_TIERS),
                    help=f"Comma-separated ranks among {config.ALL_TIERS}")
    p.add_argument("--all-tiers", action="store_true",
                    help="Sample every rank from IRON to CHALLENGER (overrides --tiers).")
    p.add_argument("--matchups", action="store_true", help="Also compute the co-occurrence matchup proxy.")
    p.add_argument("--by-region", action="store_true",
                    help="Also compute one full tier list (comps + matchups + champions) per region, "
                         "written to --by-region-out, in addition to the combined one.")
    p.add_argument("--by-rank-bracket", action="store_true",
                    help="Also compute one full tier list per individual rank bracket "
                         f"({', '.join(config.RANK_BRACKET_ORDER)}), across all sampled regions, "
                         "written to --by-rank-bracket-out. Only meaningful with --all-tiers (or --tiers "
                         "spanning more than one bracket) -- with the Diamond+-only default there's "
                         "nothing to split.")
    p.add_argument("--leaderboard", action="store_true",
                    help="Also collect the real per-region top-100 player leaderboard (League-v1 apex "
                         "tiers + Account-v1 name resolution + last-5-games form).")
    p.add_argument("--leaderboard-only", action="store_true",
                    help="Collect ONLY the leaderboard -- skips the match/tier-list collection entirely "
                         "(implies --leaderboard). Use this to refresh the leaderboard without re-running "
                         "the much longer match collection.")
    p.add_argument("--leaderboard-size", type=int, default=100,
                    help="Players per region in the leaderboard (default 100).")
    p.add_argument("--leaderboard-out", default=f"{config.OUTPUT_DIR}/leaderboard.json")
    p.add_argument("--leaderboard-history-out", default=f"{config.OUTPUT_DIR}/leaderboard_history.json",
                    help="Where the append-only avg-LP-per-region snapshot history is kept "
                         "(one row per day the leaderboard was refreshed) -- backs the World Stat elo chart.")
    p.add_argument("--no-champions", action="store_true",
                    help="Skip per-champion hover stats (computed by default, no extra API calls).")
    p.add_argument("--no-images", action="store_true",
                    help="Skip fetching champion icon/splash URLs from Community Dragon.")
    p.add_argument("--refresh-images", action="store_true",
                    help="Re-download the Community Dragon TFT data cache instead of reusing it.")
    p.add_argument("--no-cache", action="store_true", help="Ignore the local raw-match cache.")
    p.add_argument("--from-cache", action="store_true",
                    help="Recompute combined + by-region output from already-cached matches on disk, "
                         "with no live API calls at all (skips seeding/collection entirely). Ignores "
                         "--tiers/--all-tiers and --by-rank-bracket (rank-bracket membership isn't "
                         "recoverable from a cached match alone -- only known at live collection time).")
    p.add_argument("--out", default=f"{config.OUTPUT_DIR}/tierlist.json")
    p.add_argument("--matchups-out", default=f"{config.OUTPUT_DIR}/matchups.json")
    p.add_argument("--champions-out", default=f"{config.OUTPUT_DIR}/champion_stats.json")
    p.add_argument("--by-region-out", default=f"{config.OUTPUT_DIR}/tierlist_by_region.json")
    p.add_argument("--by-rank-bracket-out", default=f"{config.OUTPUT_DIR}/tierlist_by_rank.json")
    p.add_argument("--comp-history-out", default=f"{config.OUTPUT_DIR}/comp_history.json",
                    help="Append-only daily snapshot of each ranked comp's placement/play count/tier -- "
                         "backs a real placement-over-time chart on the comp fiche (one point per day "
                         "this has actually run, no interpolation/fabrication).")
    return p.parse_args(argv)


MAJORITY_SET_MIN_SHARE = 0.9


def _detect_set(matches: list[dict]):
    set_names = {m.get("info", {}).get("tft_set_core_name") for m in matches}
    return next(iter(set_names)) if len(set_names) == 1 else sorted(n for n in set_names if n)


def _filter_to_current_set(matches: list[dict]) -> tuple[list[dict], str | None, dict[str, int]]:
    """The raw-match disk cache accumulates over the project's whole
    lifetime and is never pruned, so a sample pulled today can still contain
    a handful of matches left over from an older set (a seed player's own
    match history can reach back that far even when their RECENT games are
    all current-set). Mixing sets in one tier list is meaningless -- units,
    traits and items don't carry over -- so this drops anything that isn't
    the dominant set in this batch, rather than either blending them
    silently or (the old behavior) refusing to resolve champion names/icons
    at all the moment more than one set_core_name shows up even once.
    Returns (filtered_matches, majority_set_name, {set_name: dropped_count})."""
    counts = Counter(m.get("info", {}).get("tft_set_core_name") for m in matches)
    if not counts:
        return matches, None, {}
    majority_set, majority_count = counts.most_common(1)[0]
    if majority_count / len(matches) < MAJORITY_SET_MIN_SHARE:
        # No clear current set -- something more unusual than routine cache
        # cruft (e.g. a genuine live set transition mid-collection). Don't
        # guess; let the old all-or-nothing behavior (no image/name map)
        # apply so this is visible rather than silently wrong.
        return matches, None, {}
    filtered = [m for m in matches if m.get("info", {}).get("tft_set_core_name") == majority_set]
    dropped = {name: n for name, n in counts.items() if name != majority_set}
    return filtered, majority_set, dropped


def compute_full_payload(matches: list[dict], *, want_matchups: bool, want_champions: bool,
                          image_map: dict | None, name_map: dict[str, str] | None = None,
                          item_offense: dict[str, str] | None = None, want_item_stats: bool = False) -> dict:
    """Everything derivable from one pool of matches: comps (tier list),
    matchup proxy, and champion hover stats. Used both for the combined
    ("ALL") view and for each individual region's view -- same math, just a
    different slice of matches.

    `name_map` corrects champion identities from Riot's raw (often
    leftover-codename) apiName to the real released name; `image_map` must
    already be keyed the same way (by display name) -- see main(). `
    item_offense` (see champion_images.classify_item_offense) is what lets
    derive_comp() pick the unit actually built to deal damage as the carry,
    instead of just whichever unit is holding the most items (a well-
    itemized tank -- Warmog's/Gargoyle/Sunfire is a completed 3-item build
    same as any carry's -- would otherwise win that on raw count alone).
    `want_item_stats` adds the Item Glossary's per-item champion win rates
    (see champion_stats.build_item_champion_stats) -- off by default and
    only turned on for the combined ("ALL") view: a per-region/per-rank
    slice is too thin for a single-item win rate to mean anything, and
    computing it on every slice would just be wasted work."""
    observations, comps = collect_participant_observations(matches, name_map=name_map,
                                                             item_offense=item_offense)
    total_participants = len(observations)
    result: dict = {"total_matches": len(matches), "total_participants": total_participants}
    if total_participants == 0:
        result["comps"] = []
        result["regression"] = {"regression_intercept": 0.0, "regression_slope": 0.0}
        if want_matchups:
            result["matchups"] = []
        if want_champions:
            result["champions"] = []
            result["item_champion_stats"] = {}
        return result

    rows, regression = build_tier_list(comps, total_participants)
    result["comps"] = rows
    result["regression"] = regression

    if want_matchups:
        result["matchups"] = build_matchup_table(matches, name_map=name_map, item_offense=item_offense)

    if want_champions:
        champion_rows, item_champion_stats = build_champion_stats(matches, total_participants, name_map=name_map)
        if image_map:
            for row in champion_rows:
                images = image_map.get(row["id"], {})
                row["icon_url"] = images.get("icon", "")
                row["splash_url"] = images.get("splash", "")
        result["champions"] = champion_rows
        result["item_champion_stats"] = item_champion_stats if want_item_stats else {}

    return result


def _top_comps_from_games(comp_games: list[tuple[dict, str | None, dict]], name_map: dict[str, str] | None,
                           top_k: int = 3, item_offense: dict[str, str] | None = None) -> list[dict]:
    """Aggregates the raw (participant, set_name, match) triples behind a
    region's top-N players' recent games into "the comps those players
    actually play" -- count, average placement, real champion names via
    name_map. Sample here is small by construction (top_n_for_comps players
    x up to RECENT_GAMES each), which is inherent to "what do the very best
    players do right now", not a bug -- the front end should treat this as
    a signal, not a tier-list-grade sample."""
    counts: Counter[str] = Counter()
    label_for_key: dict[str, str] = {}
    carry_for_key: dict[str, str] = {}
    placement_sum: dict[str, int] = {}
    for participant, _set_name, _match in comp_games:
        sig = derive_comp(participant, name_map=name_map, item_offense=item_offense)
        counts[sig.key] += 1
        label_for_key[sig.key] = sig.label
        carry_for_key[sig.key] = sig.carry or ""
        placement_sum[sig.key] = placement_sum.get(sig.key, 0) + participant.get("placement", 0)
    return [
        {
            "key": key,
            "label": label_for_key[key],
            "carry": carry_for_key[key],
            "count": count,
            "avgPlacement": round(placement_sum[key] / count, 2),
        }
        for key, count in counts.most_common(top_k)
    ]


def _append_leaderboard_history(regions_data: dict[str, list[dict]], history_path: Path) -> None:
    """Appends today's average-LP-per-region snapshot to a persistent
    history file -- this is what lets the World Stat elo chart actually
    show a curve over time instead of a single point. Re-running on the
    same day overwrites that day's snapshot rather than duplicating it."""
    today = datetime.now(timezone.utc).date().isoformat()
    avg_lp = {}
    sample_size = {}
    for region, rows in regions_data.items():
        if rows:
            avg_lp[region] = round(sum(r["leaguePoints"] for r in rows) / len(rows), 1)
            sample_size[region] = len(rows)

    history: dict = {"snapshots": []}
    if history_path.exists():
        try:
            history = json.loads(history_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    snapshots = [s for s in history.get("snapshots", []) if s.get("date") != today]
    snapshots.append({"date": today, "avgLp": avg_lp, "sampleSize": sample_size})
    snapshots.sort(key=lambda s: s["date"])

    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps({"snapshots": snapshots}, indent=2), encoding="utf-8")
    print(f"Leaderboard history: {len(snapshots)} snapshot(s) in {history_path}.")


def _append_comp_history(rows: list[dict], history_path: Path) -> None:
    """Appends today's per-comp (avg placement, play count, tier) snapshot
    to a persistent history file -- same pattern as
    _append_leaderboard_history, so a comp's fiche can eventually show a
    real placement trend instead of one static number. Starts empty: the
    first run only writes one point, a real trend only exists once this
    has run on multiple different days. Only comps that actually earned a
    tier (has_enough_data) get snapshotted -- the long tail of thin-sample
    comps changes key too often between runs to track meaningfully, and
    would just bloat the file with one-off entries."""
    today = datetime.now(timezone.utc).date().isoformat()
    by_comp = {
        r["key"]: {"avgPlacement": r["avg_placement"], "playCount": r["play_count"], "tier": r["tier"]}
        for r in rows if r["has_enough_data"]
    }

    history: dict = {"snapshots": []}
    if history_path.exists():
        try:
            history = json.loads(history_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    snapshots = [s for s in history.get("snapshots", []) if s.get("date") != today]
    snapshots.append({"date": today, "comps": by_comp})
    snapshots.sort(key=lambda s: s["date"])

    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps({"snapshots": snapshots}), encoding="utf-8")
    print(f"Comp placement history: {len(snapshots)} snapshot(s) in {history_path}.")


def _run_leaderboard(client: RiotClient, regions: list[str], size: int, out_path: Path,
                      history_path: Path) -> None:
    print(f"== Leaderboard: top {size} per region ({', '.join(regions)}) ==")
    rows_by_region, comp_games_by_region = collect_leaderboard(client, regions, size=size)
    for region, rows in rows_by_region.items():
        print(f"[leaderboard] {region}: {len(rows)} players resolved")

    # Detect the current set from whichever match we actually fetched, to
    # correct champion names the same way the main pipeline does (Riot's
    # apiName is sometimes a leftover dev codename -- see champion_images.py).
    detected_set = None
    for games in comp_games_by_region.values():
        for _participant, set_name, _match in games:
            if set_name:
                detected_set = set_name
                break
        if detected_set:
            break

    name_map: dict[str, str] = {}
    item_offense: dict[str, str] = {}
    if detected_set:
        try:
            raw_image_map = build_champion_image_map(detected_set)
            name_map = {cid: info["name"] for cid, info in raw_image_map.items()}
            item_offense = classify_item_offense(detected_set)
        except requests.RequestException as e:
            print(f"[warn] couldn't fetch champion images for leaderboard comp names: {e}")

    top_comps_by_region = {
        region: _top_comps_from_games(games, name_map, item_offense=item_offense)
        for region, games in comp_games_by_region.items()
    }

    # Real per-game analysis report for every player's recent games -- same
    # engine the local analyze_app.py tool uses (build_report: compares this
    # exact game against the comp's real benchmarks, checks the carry's item
    # build, flags opponents that historically counter this comp), just run
    # here at collection time instead of live, since the full match (all 8
    # participants) is already fetched for free. Backs the site's
    # "Analyser la partie" pages -- MetaScope's first phase, pre-computed
    # for the ~top-100-per-region players we already track; a live lookup
    # for an arbitrary Riot ID is a separate, later phase (needs a real
    # public backend to keep the Riot key server-side, not just this static
    # pipeline). Loaded from whatever the last full pipeline run left on
    # disk -- may be one refresh cycle stale on a --leaderboard-only run,
    # same tradeoff World Stat's top-comps comparison already accepts.
    benchmarks: dict[str, dict] = {}
    matchup_lookup: dict[tuple[str, str], dict] = {}
    try:
        benchmarks = load_benchmarks()
        matchup_lookup = load_matchups()
    except (OSError, json.JSONDecodeError) as e:
        print(f"[warn] no existing tierlist/matchups on disk yet -- per-game analysis will skip benchmarks: {e}")

    # Derive each player's own recent-games comp signatures now that
    # name_map is known -- same derive_comp() call as everywhere else, so a
    # player's "recentComps" keys line up with the regular comps dataset.
    for rows in rows_by_region.values():
        for row in rows:
            games = row.pop("_games", [])
            puuid = row["puuid"]
            recent_comps = []
            for participant, _set_name, match in games:
                sig = derive_comp(participant, name_map=name_map, item_offense=item_offense)
                report = build_report(participant, name_map, benchmarks, match=match, puuid=puuid,
                                       matchup_lookup=matchup_lookup, item_offense=item_offense)
                recent_comps.append({
                    "matchId": match.get("metadata", {}).get("match_id"),
                    "placement": participant.get("placement"),
                    "compKey": sig.key,
                    "compLabel": sig.label,
                    "carry": sig.carry,
                    # Compact per-game analysis -- everything build_report()
                    # doesn't already duplicate from data the static site
                    # builds separately (comp's own aggregate benchmark is
                    # looked up client-side via compKey, not repeated here).
                    "analysis": {
                        "level": report["level"], "goldLeft": report["goldLeft"], "lastRound": report["lastRound"],
                        "units": report["units"], "insights": report["insights"], "lobby": report["lobby"],
                    },
                })
            row["recentComps"] = recent_comps

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "Real League-v1 apex standings (Challenger, falling back to Grandmaster/Master to fill "
                "out smaller servers), LP-sorted. TFT has no literal win/loss -- recentPlacements is the "
                "last 5 ranked games' actual 1-8 finish; the app's W/L convention (top4 = W) is a "
                "display-layer choice, not something Riot defines. top_comps is derived from the top 10 "
                "players' own recent games only -- a small, real sample, not a tier-list-grade one.",
        "size": size,
        "regions": rows_by_region,
        "top_comps": top_comps_by_region,
    }, indent=2), encoding="utf-8")
    print(f"Leaderboard written to {out_path} ({client.request_count} API requests).")

    _append_leaderboard_history(rows_by_region, history_path)


def _load_matches_from_cache(regions: list[str]) -> dict[str, list[dict]]:
    """Loads every already-cached ranked match for the given regions
    straight off disk, no API calls. Region is recovered from the match id
    prefix Riot itself encodes into the filename (e.g. "EUW1_..." /
    "KR_..."), which is the same prefix as the platform routing value --
    this is reliable because Riot assigns it, not something we guessed.
    Used by --from-cache to recompute the combined + by-region views
    without re-running the (rate-limited, hours-long) live collection --
    e.g. after a code fix like _filter_to_current_set that only needed a
    recompute, not new data. Cannot reconstruct rank-bracket membership
    (that's a property of the seed player at collection time, not of the
    match itself), so by-rank-bracket stays empty in this mode."""
    prefixes = {config.REGIONS[r]["platform"].upper(): r for r in regions}
    by_region: dict[str, list[dict]] = {r: [] for r in regions}
    cache_dir = Path(config.RAW_CACHE_DIR)
    for path in cache_dir.glob("*.json"):
        if path.name.startswith("_"):
            continue  # not a match file (e.g. _cdragon_tft.json asset cache)
        matched_region = next((r for prefix, r in prefixes.items() if path.stem.startswith(prefix)), None)
        if not matched_region:
            continue
        try:
            match = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        info = match.get("info", {})
        if info.get("queueId") != config.RANKED_TFT_QUEUE_ID:
            continue
        by_region[matched_region].append(match)
    return by_region


def main(argv=None) -> None:
    args = parse_args(argv)
    regions = [r.strip().upper() for r in args.regions.split(",") if r.strip()]
    tiers = config.ALL_TIERS if args.all_tiers else [t.strip().upper() for t in args.tiers.split(",") if t.strip()]

    for r in regions:
        if r not in config.REGIONS:
            raise SystemExit(f"Unknown region '{r}'. Known: {list(config.REGIONS)}")
    for t in tiers:
        if t not in config.ALL_TIERS:
            raise SystemExit(f"Unknown tier '{t}'. Known: {config.ALL_TIERS}")

    client = RiotClient(use_cache=not args.no_cache)

    if args.leaderboard_only:
        _run_leaderboard(client, regions, args.leaderboard_size, Path(args.leaderboard_out),
                          Path(args.leaderboard_history_out))
        return

    all_matches: list[dict] = []
    matches_by_region: dict[str, list[dict]] = {r: [] for r in regions}
    matches_by_tier: dict[str, list[dict]] = {t: [] for t in tiers}
    bracket_meta = []
    started = time.monotonic()

    if args.from_cache:
        print(f"[from-cache] loading cached ranked matches for {regions} -- no API calls.")
        matches_by_region = _load_matches_from_cache(regions)
        for region, matches in matches_by_region.items():
            all_matches.extend(matches)
            print(f"   {region}: {len(matches)} cached ranked matches")
        args.by_rank_bracket = False  # not recoverable from cache alone -- see _load_matches_from_cache
    else:
        for region in regions:
            for tier in tiers:
                print(f"== {region} / {tier} ==")
                sample = collect_bracket(client, region, tier)
                print(f"   seed players: {len(sample.seed_puuids)} | unique matches: {len(sample.match_ids)} "
                      f"| ranked matches kept: {len(sample.matches)}")
                if sample.fallback_note:
                    print(f"   NOTE: {sample.fallback_note}")
                all_matches.extend(sample.matches)
                matches_by_region[region].extend(sample.matches)
                matches_by_tier[tier].extend(sample.matches)
                bracket_meta.append({
                    "region": region,
                    "tier": tier,
                    "seed_players": len(sample.seed_puuids),
                    "matches_collected": len(sample.matches),
                    "used_apex_fallback": sample.used_fallback,
                    "fallback_note": sample.fallback_note,
                })

    elapsed = time.monotonic() - started
    print(f"\nCollected {len(all_matches)} ranked matches across {len(regions)} region(s) / "
          f"{len(tiers)} tier(s) in {elapsed:.1f}s ({client.request_count} API requests).")

    if not all_matches:
        raise SystemExit("No participant data collected — nothing to compute a tier list from.")

    all_matches, majority_set, dropped_by_set = _filter_to_current_set(all_matches)
    if dropped_by_set:
        dropped_desc = ", ".join(f"{n} {name}" for name, n in sorted(dropped_by_set.items(), key=lambda kv: -kv[1]))
        print(f"[note] dropped {sum(dropped_by_set.values())} match(es) from an older set ({dropped_desc}) "
              f"-- kept only {majority_set}, the current set, so comps/matchups/champion stats aren't "
              "blended across sets with different champions/traits/items.")
        for region in matches_by_region:
            matches_by_region[region] = [m for m in matches_by_region[region]
                                          if m.get("info", {}).get("tft_set_core_name") == majority_set]
        for tier in matches_by_tier:
            matches_by_tier[tier] = [m for m in matches_by_tier[tier]
                                      if m.get("info", {}).get("tft_set_core_name") == majority_set]

    generated_at = datetime.now(timezone.utc).isoformat()
    set_name = _detect_set(all_matches)

    image_map = {}
    name_map: dict[str, str] = {}
    item_offense: dict[str, str] = {}
    if not args.no_images and not args.no_champions and isinstance(set_name, str) and set_name:
        try:
            raw_image_map = build_champion_image_map(set_name, refresh=args.refresh_images)
            # Re-key icon/splash lookups by the corrected display name so
            # they line up with every other output field (comps' carry/core
            # units, champions[].id), which all get translated the same way.
            name_map = {cid: info["name"] for cid, info in raw_image_map.items()}
            image_map = {info["name"]: info for info in raw_image_map.values()}
            item_offense = classify_item_offense(set_name, refresh=args.refresh_images)
        except requests.RequestException as e:
            print(f"[warn] couldn't fetch champion images from Community Dragon: {e}")

    # ---- Combined ("ALL") view: same file shapes as before, for Wix sync ----
    combined = compute_full_payload(all_matches, want_matchups=args.matchups,
                                     want_champions=not args.no_champions, image_map=image_map,
                                     name_map=name_map, item_offense=item_offense, want_item_stats=True)

    output = {
        "generated_at": generated_at,
        "set": set_name,
        "sample": {
            "regions": regions,
            "tiers": tiers,
            "total_matches": combined["total_matches"],
            "total_participants": combined["total_participants"],
            "brackets": bracket_meta,
        },
        "methodology": {
            "comp_signature": "top active traits (by style/tier) + carry = most offensive-item unit "
                               "among 1-4 cost units only (a 5-cost is never what a comp is built "
                               "around -- it's whatever the game handed you at 8-9, on top of a comp "
                               "that already worked), AD/AP/AS/Crit-built items beat raw item count "
                               "(an itemized tank doesn't get picked over the real damage dealer), "
                               "ties broken by star level then item count",
            "contest_adjustment": "brute_force_placement = avg_placement - regression_slope * play_rate, "
                                   "fit via weighted least-squares of avg_placement on play_rate across comps "
                                   f"with >= {config.MIN_SAMPLE_FOR_TIER} observations",
            "regression": combined["regression"],
            "min_sample_for_tier": config.MIN_SAMPLE_FOR_TIER,
        },
        "comps": combined["comps"],
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nTier list written to {out_path} ({len(combined['comps'])} comps).")

    _append_comp_history(combined["comps"], Path(args.comp_history_out))

    if args.matchups:
        mout_path = Path(args.matchups_out)
        mout_path.parent.mkdir(parents=True, exist_ok=True)
        mout_path.write_text(json.dumps({
            "generated_at": generated_at,
            "note": "Proxy signal: within shared lobbies, which comp placed ahead of which — "
                    "not literal round-by-round combat data (not exposed by Riot's public API).",
            "matchups": combined["matchups"],
        }, indent=2), encoding="utf-8")
        print(f"Matchup proxy table written to {mout_path} ({len(combined['matchups'])} pairs).")

    if not args.no_champions:
        missing = sum(1 for r in combined["champions"] if not r.get("icon_url"))
        if missing:
            print(f"[note] {missing}/{len(combined['champions'])} champions had no matching image in Community Dragon.")
        cout_path = Path(args.champions_out)
        cout_path.parent.mkdir(parents=True, exist_ok=True)
        cout_path.write_text(json.dumps({
            "generated_at": generated_at,
            "note": "Per-champion aggregates for a hover tooltip: pick rate, average star level, "
                    "most common items, and how games featuring this champion tend to go.",
            "champions": combined["champions"],
            "item_champion_stats": combined.get("item_champion_stats", {}),
        }, indent=2), encoding="utf-8")
        print(f"Champion hover stats written to {cout_path} ({len(combined['champions'])} champions).")

    # ---- Per-region views ----
    if args.by_region:
        by_region = {}
        for region in regions:
            region_matches = matches_by_region[region]
            payload = compute_full_payload(region_matches, want_matchups=args.matchups,
                                            want_champions=not args.no_champions, image_map=image_map,
                                            name_map=name_map, item_offense=item_offense)
            ranked = sum(1 for c in payload["comps"] if c["has_enough_data"])
            print(f"[by-region] {region}: {payload['total_matches']} matches, "
                  f"{len(payload['comps'])} comps ({ranked} ranked)")
            by_region[region] = {
                "total_matches": payload["total_matches"],
                "total_participants": payload["total_participants"],
                "comps": payload["comps"],
                "matchups": payload.get("matchups", []),
                "champions": payload.get("champions", []),
            }

        by_region_path = Path(args.by_region_out)
        by_region_path.parent.mkdir(parents=True, exist_ok=True)
        by_region_path.write_text(json.dumps({
            "generated_at": generated_at,
            "set": set_name,
            "regions": by_region,
        }, indent=2), encoding="utf-8")
        print(f"Per-region tier lists written to {by_region_path}.")

    # ---- Per-rank-bracket views: a second, independent slicing axis from
    # region -- see config.RANK_BRACKETS. A bracket only has matches to show
    # if --tiers/--all-tiers actually reached it; brackets outside the
    # collected tiers come back empty rather than erroring, so this is safe
    # to pass even when the run only covered e.g. Diamond+. ----
    if args.by_rank_bracket:
        by_rank = {}
        for bracket, bracket_tiers in config.RANK_BRACKETS.items():
            bracket_matches = [m for t in bracket_tiers for m in matches_by_tier.get(t, [])]
            payload = compute_full_payload(bracket_matches, want_matchups=args.matchups,
                                            want_champions=not args.no_champions, image_map=image_map,
                                            name_map=name_map, item_offense=item_offense)
            ranked = sum(1 for c in payload["comps"] if c["has_enough_data"])
            print(f"[by-rank-bracket] {bracket}: {payload['total_matches']} matches, "
                  f"{len(payload['comps'])} comps ({ranked} ranked)")
            by_rank[bracket] = {
                "total_matches": payload["total_matches"],
                "total_participants": payload["total_participants"],
                "comps": payload["comps"],
                "matchups": payload.get("matchups", []),
                "champions": payload.get("champions", []),
            }

        by_rank_path = Path(args.by_rank_bracket_out)
        by_rank_path.parent.mkdir(parents=True, exist_ok=True)
        by_rank_path.write_text(json.dumps({
            "generated_at": generated_at,
            "set": set_name,
            "bracket_definitions": config.RANK_BRACKETS,
            "ranks": by_rank,
        }, indent=2), encoding="utf-8")
        print(f"Per-rank-bracket tier lists written to {by_rank_path}.")

    # ---- Leaderboard (independent of match collection above) ----
    if args.leaderboard:
        _run_leaderboard(client, regions, args.leaderboard_size, Path(args.leaderboard_out),
                          Path(args.leaderboard_history_out))


if __name__ == "__main__":
    main()
