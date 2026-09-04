"""Thin, rate-limited client for the Riot Games TFT API.

The API key is read from the environment (`.env` -> RIOT_API_KEY) and never
appears in source. Every outbound request carries it only as a header.
"""
from __future__ import annotations

import json
import os
import time
import collections
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from . import config

load_dotenv()  # populates os.environ from a local .env file, if present


class RiotAPIError(RuntimeError):
    def __init__(self, status: int, url: str, body: str):
        super().__init__(f"Riot API {status} on {url}: {body[:300]}")
        self.status = status
        self.url = url
        self.body = body


class RateLimiter:
    """Sliding-window limiter for the multiple windows Riot enforces at once
    (e.g. 20 req/1s AND 100 req/120s for a dev key)."""

    def __init__(self, windows: list[tuple[int, float]]):
        self.windows = windows
        self._hits: dict[float, collections.deque] = {
            w: collections.deque() for _, w in windows
        }

    def wait_slot(self) -> None:
        while True:
            now = time.monotonic()
            soonest_wait = 0.0
            for max_requests, window in self.windows:
                dq = self._hits[window]
                while dq and now - dq[0] > window:
                    dq.popleft()
                if len(dq) >= max_requests:
                    wait = window - (now - dq[0]) + 0.05
                    soonest_wait = max(soonest_wait, wait)
            if soonest_wait <= 0:
                for _, window in self.windows:
                    self._hits[window].append(now)
                return
            time.sleep(soonest_wait)


class RiotClient:
    def __init__(self, api_key: str | None = None, cache_dir: str = config.RAW_CACHE_DIR,
                 use_cache: bool = True, verbose: bool = True):
        self.api_key = api_key or os.environ.get("RIOT_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "RIOT_API_KEY is not set. Put it in a .env file at the project "
                "root: RIOT_API_KEY=RGAPI-...  (never hardcode it in source)."
            )
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
            print(f"[riot] {msg}")

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

    # -- League-v1 ------------------------------------------------------
    def get_league_entries(self, platform: str, tier: str, division: str, page: int = 1) -> list[dict]:
        url = f"https://{platform}.api.riotgames.com/tft/league/v1/entries/{tier}/{division}"
        data = self._get(url, params={"page": page})
        return data or []

    def get_apex_league(self, platform: str, tier: str) -> dict:
        """tier one of MASTER, GRANDMASTER, CHALLENGER."""
        path = tier.lower()
        url = f"https://{platform}.api.riotgames.com/tft/league/v1/{path}"
        data = self._get(url)
        return data or {"tier": tier, "entries": []}

    # -- Account-v1 (Riot ID -> puuid; the reverse of the lookup below) -----
    def get_account_by_riot_id(self, regional: str, game_name: str, tag_line: str) -> dict | None:
        # Riot ID components can contain characters (spaces, accents) that
        # need URL-encoding in the path.
        from urllib.parse import quote
        url = (f"https://{regional}.api.riotgames.com/riot/account/v1/accounts/"
               f"by-riot-id/{quote(game_name)}/{quote(tag_line)}")
        return self._get(url)

    # -- Account-v1 (puuid -> Riot ID; league-v1 stopped returning names) --
    def get_account_by_puuid(self, regional: str, puuid: str) -> dict | None:
        if self.use_cache:
            cached = self._read_account_cache(puuid)
            if cached is not None:
                return cached
        url = f"https://{regional}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
        data = self._get(url)
        if data is not None and self.use_cache:
            self._write_account_cache(puuid, data)
        return data

    # -- Match-v1 ---------------------------------------------------------
    def get_match_ids_by_puuid(self, regional: str, puuid: str, count: int = 5) -> list[str]:
        url = f"https://{regional}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids"
        data = self._get(url, params={"count": count})
        return data or []

    def get_match(self, regional: str, match_id: str) -> dict | None:
        if self.use_cache:
            cached = self._read_cache(match_id)
            if cached is not None:
                return cached
        url = f"https://{regional}.api.riotgames.com/tft/match/v1/matches/{match_id}"
        data = self._get(url)
        if data is not None and self.use_cache:
            self._write_cache(match_id, data)
        return data

    # -- Local disk cache (matches are immutable once played) -------------
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

    # -- Account cache (puuid -> Riot ID; names change rarely, and re-fetching
    # 100s of them on every leaderboard refresh would be wasteful) -----------
    def _account_cache_path(self, puuid: str) -> Path:
        return self.cache_dir / "_accounts" / f"{puuid}.json"

    def _read_account_cache(self, puuid: str) -> dict | None:
        p = self._account_cache_path(puuid)
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return None
        return None

    def _write_account_cache(self, puuid: str, data: dict) -> None:
        try:
            p = self._account_cache_path(puuid)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(data), encoding="utf-8")
        except OSError:
            pass
