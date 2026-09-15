"""Thin, rate-limited client for the Riot Games LEAGUE OF LEGENDS API --
sibling of riot_client.py (TFT), same dev-key constraints, different game's
endpoints. Reuses the same RateLimiter/RiotAPIError and .env-loading
convention. The Development key is account-wide across LoL/TFT/LoR (verified
this session against Riot's own dev-relations docs), so this reads the SAME
RIOT_API_KEY from .env as the TFT pipeline -- no separate key needed for
this offline collection script (the lol-worker Cloudflare Worker is a
different deployment with its own RIOT_API_KEY_LOL secret; unrelated here).
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from dotenv import load_dotenv

from .riot_client import RateLimiter, RiotAPIError
from . import config

load_dotenv()

LOL_REGIONS: dict[str, dict[str, str]] = {
    "EUW": {"platform": "euw1", "regional": "europe"},
    "NA": {"platform": "na1", "regional": "americas"},
    "BR": {"platform": "br1", "regional": "americas"},
    "KR": {"platform": "kr", "regional": "asia"},
}

QUEUE_SOLO = 420
LANE_TO_ROLE = {"TOP": "top", "JUNGLE": "jungle", "MIDDLE": "mid", "BOTTOM": "adc", "UTILITY": "support"}


class LolRiotClient:
    def __init__(self, api_key: str | None = None, cache_dir: str = "data/raw_lol",
                 use_cache: bool = True, verbose: bool = True):
        self.api_key = api_key or os.environ.get("RIOT_API_KEY")
        if not self.api_key:
            raise RuntimeError("RIOT_API_KEY is not set in .env (same key already used by the TFT pipeline).")
        self.session = requests.Session()
        self.session.headers["X-Riot-Token"] = self.api_key
        self.limiter = RateLimiter(config.RATE_LIMIT_WINDOWS)
        self.cache_dir = Path(cache_dir)
        self.use_cache = use_cache
        self.verbose = verbose
        self.request_count = 0
        if self.use_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(f"[riot-lol] {msg}")

    def _get(self, url: str, params: dict | None = None, max_retries: int = 4) -> Any:
        for attempt in range(max_retries + 1):
            self.limiter.wait_slot()
            self.request_count += 1
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", "2"))
                self._log(f"429 rate-limited, sleeping {retry_after}s ({url})")
                time.sleep(retry_after + 0.25)
                continue
            if resp.status_code in (500, 502, 503, 504) and attempt < max_retries:
                backoff = 1.5 ** attempt
                self._log(f"{resp.status_code} on {url}, retrying in {backoff:.1f}s")
                time.sleep(backoff)
                continue
            if resp.status_code == 404:
                return None
            raise RiotAPIError(resp.status_code, url, resp.text)
        raise RiotAPIError(resp.status_code, url, resp.text)

    # -- League-v4 --------------------------------------------------------
    def get_league_entries(self, platform: str, tier: str, division: str, page: int = 1) -> list[dict]:
        url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}"
        data = self._get(url, params={"page": page})
        return data or []

    def get_apex_league(self, platform: str, tier: str) -> dict:
        """tier one of MASTER, GRANDMASTER, CHALLENGER."""
        path = {"MASTER": "masterleagues", "GRANDMASTER": "grandmasterleagues", "CHALLENGER": "challengerleagues"}[tier]
        url = f"https://{platform}.api.riotgames.com/lol/league/v4/{path}/by-queue/RANKED_SOLO_5x5"
        data = self._get(url)
        return data or {"tier": tier, "entries": []}

    def get_summoner_by_id(self, platform: str, summoner_id: str) -> dict | None:
        url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}"
        return self._get(url)

    # -- Match-v5 -----------------------------------------------------------
    def get_match_ids_by_puuid(self, regional: str, puuid: str, count: int = 5) -> list[str]:
        url = f"https://{regional}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        data = self._get(url, params={"count": count, "queue": QUEUE_SOLO})
        return data or []

    def get_match(self, regional: str, match_id: str) -> dict | None:
        if self.use_cache:
            cached = self._read_cache(match_id)
            if cached is not None:
                return cached
        url = f"https://{regional}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        data = self._get(url)
        if data is not None and self.use_cache:
            self._write_cache(match_id, data)
        return data

    # -- Local disk cache (matches are immutable once played) ---------------
    def _cache_path(self, match_id: str) -> Path:
        return self.cache_dir / f"{match_id}.json"

    def _read_cache(self, match_id: str) -> dict | None:
        p = self._cache_path(match_id)
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return None
        return None

    def _write_cache(self, match_id: str, data: dict) -> None:
        try:
            self._cache_path(match_id).write_text(json.dumps(data), encoding="utf-8")
        except OSError:
            pass
