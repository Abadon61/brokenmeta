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


def aggregate(matches: list[dict]) -> dict:
    """champion -> role -> {games, wins}, reading all 10 participants of
    every match (not just a seed player) -- see module docstring."""
    stats: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: {"games": 0, "wins": 0}))
    seen_match_ids: set[str] = set()
    total_rows = 0
    for match in matches:
        mid = match.get("metadata", {}).get("matchId")
        if not mid or mid in seen_match_ids:
            continue  # a match can be re-fetched across brackets/regions sharing a seed player
        seen_match_ids.add(mid)
        for p in match.get("info", {}).get("participants", []):
            champ = p.get("championName")
            role = LANE_TO_ROLE.get(p.get("individualPosition"))
            if not champ or not role:
                continue
            row = stats[champ][role]
            row["games"] += 1
            if p.get("win"):
                row["wins"] += 1
            total_rows += 1
    return {"stats": stats, "unique_matches": len(seen_match_ids), "total_rows": total_rows}


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


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect real LoL ranked matches and compute real champion pick/win rate by role.")
    p.add_argument("--regions", default=",".join(LOL_REGIONS.keys()))
    p.add_argument("--tiers", default=",".join(DEFAULT_TIERS), help=f"Comma-separated ranks among {ALL_TIERS}")
    p.add_argument("--all-tiers", action="store_true", help="Sample every rank from IRON to CHALLENGER (overrides --tiers).")
    p.add_argument("--no-cache", action="store_true", help="Ignore the local raw-match cache.")
    p.add_argument("--out", default=OUTPUT_PATH)
    return p.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    regions = [r.strip().upper() for r in args.regions.split(",") if r.strip()]
    tiers = ALL_TIERS if args.all_tiers else [t.strip().upper() for t in args.tiers.split(",") if t.strip()]

    client = LolRiotClient(use_cache=not args.no_cache)
    all_matches: list[dict] = []
    for region in regions:
        for tier in tiers:
            print(f"== {region} / {tier} ==")
            sample = collect_bracket(client, region, tier)
            print(f"   seed players: {len(sample.seed_puuids)} | unique matches: {len(sample.match_ids)} | ranked matches kept: {len(sample.matches)}")
            all_matches.extend(sample.matches)

    agg = aggregate(all_matches)
    print(f"\nCollected {agg['unique_matches']} unique ranked matches, {agg['total_rows']} champion+role rows "
          f"across {len(regions)} region(s) / {len(tiers)} tier(s) ({client.request_count} API requests).")

    output = build_output(agg["stats"], regions, tiers, agg["unique_matches"], agg["total_rows"])
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Champion role stats written to {out_path} ({len(output['by_champion'])} champions with at least one qualifying role).")


if __name__ == "__main__":
    main()
