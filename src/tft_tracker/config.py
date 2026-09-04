"""Static configuration: regions, tiers, sampling knobs.

Nothing secret lives here. The API key is loaded separately from `.env`
(see riot_client.py) and never hardcoded.
"""
from __future__ import annotations

# --- Region routing -------------------------------------------------------
# Riot splits routing in two: a "platform" host (per-server, used by
# league-v1/summoner-v1) and a "regional" host (a cluster, used by match-v1).
# CN is not reachable through the public Riot API (Tencent-operated shard),
# so per the product decision it's replaced by BR in the default sample.
REGIONS: dict[str, dict[str, str]] = {
    "EUW": {"platform": "euw1", "regional": "europe"},
    "NA": {"platform": "na1", "regional": "americas"},
    "BR": {"platform": "br1", "regional": "americas"},
    "KR": {"platform": "kr", "regional": "asia"},
}

# Order matters only for default CLI ordering / display.
DEFAULT_REGIONS = ["EUW", "NA", "BR", "KR"]

# --- Ranks ------------------------------------------------------------------
SUB_APEX_TIERS = [
    "IRON",
    "BRONZE",
    "SILVER",
    "GOLD",
    "PLATINUM",
    "EMERALD",
    "DIAMOND",
]
APEX_TIERS = ["MASTER", "GRANDMASTER", "CHALLENGER"]
ALL_TIERS = SUB_APEX_TIERS + APEX_TIERS

DIVISIONS = ["I", "II", "III", "IV"]

# Per-individual-tier grouping for the "trier par rang" filter -- an axis
# independent of region (see --by-rank-bracket in pipeline.py). One bucket
# per sub-apex tier so the front end can offer real per-tier checkboxes
# (pick any combination, e.g. Platinum+Emerald+Diamond) instead of 4 fixed
# groups; apex tiers stay merged into one MASTER_PLUS bucket since
# Grandmaster/Challenger populations are too small on their own to be a
# useful standalone checkbox (see PLAYERS_PER_BRACKET/apex fallback above).
RANK_BRACKETS: dict[str, list[str]] = {
    "IRON": ["IRON"],
    "BRONZE": ["BRONZE"],
    "SILVER": ["SILVER"],
    "GOLD": ["GOLD"],
    "PLATINUM": ["PLATINUM"],
    "EMERALD": ["EMERALD"],
    "DIAMOND": ["DIAMOND"],
    "MASTER_PLUS": ["MASTER", "GRANDMASTER", "CHALLENGER"],
}
RANK_BRACKET_ORDER = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND", "MASTER_PLUS"]

# "Default selector" per product spec: Diamond and up (the ranks where the
# meta is closest to "optimal", least diluted by low-elo experimentation),
# until --tiers/--all-tiers is passed explicitly.
DEFAULT_TIERS = ["DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]

# Rank used as a stand-in sample when an apex ladder (MASTER/GRANDMASTER/
# CHALLENGER) comes back empty from Riot's API (observed live: as of this
# writing the apex league-v1 endpoints return `entries: []` on EUW/NA/KR —
# a known-flaky endpoint on Riot's side, not a request-shape issue).
APEX_FALLBACK_TIER = "DIAMOND"
APEX_FALLBACK_DIVISION = "I"

# --- Sampling knobs (kept small: dev key = 20 req/1s, 100 req/120s, 24h TTL)
DIVISIONS_SAMPLED = ["I", "II", "III"]  # which sub-apex divisions to pull entries from
PLAYERS_PER_BRACKET = 150        # seed players per (region, tier[, division])
MATCH_IDS_PER_PLAYER = 8         # recent ranked match ids requested per seed player
MAX_MATCHES_PER_BRACKET = 400    # hard cap on unique matches fetched per bracket
MIN_SAMPLE_FOR_TIER = 5          # min play_count before a comp gets an S/A/B/C tier

RANKED_TFT_QUEUE_ID = 1100

# --- Rate limiting (matches the dev-key limits echoed back in response
# headers: X-App-Rate-Limit: 100:120,20:1) -----------------------------------
RATE_LIMIT_WINDOWS = [(20, 1.0), (100, 120.0)]  # (max_requests, window_seconds)

# --- Paths --------------------------------------------------------------
RAW_CACHE_DIR = "data/raw"
OUTPUT_DIR = "data/output"
