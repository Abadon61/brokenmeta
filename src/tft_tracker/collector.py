"""Sampling layer: turns (region, tier) brackets into a deduplicated pool of
real match data, respecting the small quotas set in config.py so a dev key
(20 req/1s, 100 req/120s, 24h TTL) doesn't get burned in one run.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import config
from .riot_client import RiotClient


@dataclass
class BracketSample:
    region: str
    tier: str
    used_fallback: bool = False
    fallback_note: str | None = None
    seed_puuids: list[str] = field(default_factory=list)
    match_ids: set[str] = field(default_factory=set)
    matches: list[dict] = field(default_factory=list)


def _seed_puuids_for_bracket(client: RiotClient, platform: str, tier: str) -> tuple[list[str], bool, str | None]:
    """Returns (puuids, used_fallback, note)."""
    if tier in config.APEX_TIERS:
        data = client.get_apex_league(platform, tier)
        entries = data.get("entries") or []
        puuids = [e["puuid"] for e in entries if e.get("puuid")]
        if puuids:
            # Apex ladders can be large; take the top ones by league points.
            entries_sorted = sorted(entries, key=lambda e: e.get("leaguePoints", 0), reverse=True)
            puuids = [e["puuid"] for e in entries_sorted if e.get("puuid")][: config.PLAYERS_PER_BRACKET]
            return puuids, False, None
        # Known-flaky endpoint (Riot returns 200 + empty entries for
        # MASTER/GRANDMASTER/CHALLENGER as of this writing). Fall back to a
        # high sub-apex division as the nearest available high-elo proxy.
        fb_tier, fb_div = config.APEX_FALLBACK_TIER, config.APEX_FALLBACK_DIVISION
        note = (f"{tier} ladder came back empty from Riot's API (known-flaky apex "
                f"endpoint); used {fb_tier} {fb_div} as a high-elo proxy instead.")
        fb_entries = client.get_league_entries(platform, fb_tier, fb_div, page=1)
        puuids = [e["puuid"] for e in fb_entries if e.get("puuid")][: config.PLAYERS_PER_BRACKET]
        return puuids, True, note

    puuids: list[str] = []
    for division in config.DIVISIONS_SAMPLED:
        if len(puuids) >= config.PLAYERS_PER_BRACKET:
            break
        entries = client.get_league_entries(platform, tier, division, page=1)
        puuids.extend(e["puuid"] for e in entries if e.get("puuid"))
    return puuids[: config.PLAYERS_PER_BRACKET], False, None


def collect_bracket(client: RiotClient, region: str, tier: str) -> BracketSample:
    platform = config.REGIONS[region]["platform"]
    regional = config.REGIONS[region]["regional"]

    sample = BracketSample(region=region, tier=tier)
    puuids, used_fallback, note = _seed_puuids_for_bracket(client, platform, tier)
    sample.seed_puuids = puuids
    sample.used_fallback = used_fallback
    sample.fallback_note = note

    for puuid in puuids:
        if len(sample.match_ids) >= config.MAX_MATCHES_PER_BRACKET:
            break
        ids = client.get_match_ids_by_puuid(regional, puuid, count=config.MATCH_IDS_PER_PLAYER)
        for mid in ids:
            if len(sample.match_ids) >= config.MAX_MATCHES_PER_BRACKET:
                break
            sample.match_ids.add(mid)

    for mid in sample.match_ids:
        match = client.get_match(regional, mid)
        if not match:
            continue
        info = match.get("info", {})
        if info.get("queueId") != config.RANKED_TFT_QUEUE_ID:
            continue  # skip non-ranked (e.g. hyper roll / double up) matches
        sample.matches.append(match)

    return sample
