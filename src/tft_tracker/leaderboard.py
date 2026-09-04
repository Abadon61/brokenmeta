"""Real per-region player leaderboard: top players by League Points (LP),
their current rank, their last 5 ranked placements, and (for the top N of
those, by default 10) the raw match participants behind those games -- reused
by pipeline.py to build the World Stat comp comparison without any extra
API calls.

League-v1's apex endpoints (challenger/grandmaster/master) give real,
public ranked standings -- LP, wins, losses, hot streak -- but no longer
include a display name (Riot removed `summonerName` from these responses),
only a `puuid`. Resolving that to an actual Riot ID (the `Pseudo#TAG` shown
in-client) takes one extra call per player to account-v1
(`/riot/account/v1/accounts/by-puuid/{puuid}`), which IS how public
trackers get names shown for a real leaderboard, since Riot doesn't publish
one as a ready-made feed.

TFT doesn't have a literal win/loss the way a 1v1 queue does -- placement is
1-8. For "recent form" we adopt the same convention public trackers use:
top 4 = W (green), bottom 4 = L (red). That convention is documented in the
output so it isn't mistaken for anything Riot itself defines.
"""
from __future__ import annotations

from . import config
from .riot_client import RiotClient

LEADERBOARD_SIZE = 100
# 10 so the player profile page ("10 dernières compositions") has what it
# needs; the compact leaderboard row only ever shows the first 5 of these
# as W/L squares (display-layer slice, not a separate fetch).
RECENT_GAMES = 10
TOP_N_FOR_COMPS = 10
# Tiers merged (in this order) to fill out to LEADERBOARD_SIZE even on a
# smaller server where Challenger alone doesn't have 100 players.
FILL_TIERS = ("CHALLENGER", "GRANDMASTER", "MASTER")


def _apex_pool(client: RiotClient, platform: str) -> list[dict]:
    pool: list[dict] = []
    for tier in FILL_TIERS:
        data = client.get_apex_league(platform, tier)
        for e in data.get("entries") or []:
            if e.get("puuid"):
                pool.append({**e, "_tier": tier})
    return pool


def _recent_games(client: RiotClient, regional: str, puuid: str) -> list[tuple[dict, str | None]]:
    """Returns [(participant_dict, tft_set_core_name), ...] for this
    player's last RECENT_GAMES ranked matches, most-recent-first. Keeping
    the raw participant (not just its placement) lets a caller re-derive
    the comp signature later -- e.g. for the World Stat "most-played by the
    top 10" comparison -- without a second round of API calls."""
    match_ids = client.get_match_ids_by_puuid(regional, puuid, count=RECENT_GAMES)
    games = []
    for mid in match_ids:
        match = client.get_match(regional, mid)
        if not match:
            continue
        info = match.get("info", {})
        if info.get("queueId") != config.RANKED_TFT_QUEUE_ID:
            continue
        participant = next(
            (p for p in info.get("participants", []) if p.get("puuid") == puuid), None
        )
        if participant and participant.get("placement"):
            games.append((participant, info.get("tft_set_core_name")))
    return games


def collect_region_leaderboard(client: RiotClient, region: str, size: int = LEADERBOARD_SIZE,
                                top_n_for_comps: int = TOP_N_FOR_COMPS,
                                verbose: bool = True) -> tuple[list[dict], list[tuple[dict, str | None]]]:
    """Returns (rows, comp_source_games). `comp_source_games` is the raw
    (participant, set_name) pairs behind the top `top_n_for_comps` players'
    recent games -- not part of `rows`, kept separate since it's only
    consumed by the World Stat comp comparison, not the leaderboard table."""
    platform = config.REGIONS[region]["platform"]
    regional = config.REGIONS[region]["regional"]

    pool = _apex_pool(client, platform)
    pool.sort(key=lambda e: e.get("leaguePoints", 0), reverse=True)
    top = pool[:size]

    rows = []
    comp_source_games: list[tuple[dict, str | None]] = []
    for rank, e in enumerate(top, start=1):
        puuid = e["puuid"]
        account = client.get_account_by_puuid(regional, puuid) or {}
        game_name = account.get("gameName") or "?"
        tag_line = account.get("tagLine") or ""
        games = _recent_games(client, regional, puuid)
        if rank <= top_n_for_comps:
            comp_source_games.extend(games)

        rows.append({
            "rank": rank,
            "tier": e["_tier"],
            "riotId": f"{game_name}#{tag_line}" if tag_line else game_name,
            "leaguePoints": e.get("leaguePoints", 0),
            "wins": e.get("wins", 0),
            "losses": e.get("losses", 0),
            "hotStreak": bool(e.get("hotStreak")),
            "recentPlacements": [p.get("placement") for p, _ in games],  # most-recent-first, 1-8
            # Internal only -- consumed by pipeline.py to derive each game's
            # comp signature once a name_map exists, then replaced with
            # "recentComps" and stripped before the JSON is written.
            "_games": games,
        })
        if verbose and rank % 20 == 0:
            print(f"   [{region}] {rank}/{len(top)} players resolved "
                  f"({client.request_count} total requests so far)", flush=True)
    return rows, comp_source_games


def collect_leaderboard(client: RiotClient, regions: list[str], size: int = LEADERBOARD_SIZE,
                         top_n_for_comps: int = TOP_N_FOR_COMPS
                         ) -> tuple[dict[str, list[dict]], dict[str, list[tuple[dict, str | None]]]]:
    rows_by_region: dict[str, list[dict]] = {}
    comp_games_by_region: dict[str, list[tuple[dict, str | None]]] = {}
    for region in regions:
        rows, comp_games = collect_region_leaderboard(client, region, size=size, top_n_for_comps=top_n_for_comps)
        rows_by_region[region] = rows
        comp_games_by_region[region] = comp_games
    return rows_by_region, comp_games_by_region
