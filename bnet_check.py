#!/usr/bin/env python
"""Check what the official Battle.net Game Data API serves for World of Warcraft (re-run after the WoW: Forever launch).

    py -3.11 bnet_check.py                        # default namespaces
    py -3.11 bnet_check.py static-forever-us ...  # extra namespaces to probe (see Blizzard's namespaces guide)

Reads BLIZZARD_CLIENT_ID / BLIZZARD_CLIENT_SECRET from .env and never prints them. What to look for: a namespace answering
200 on talent/index or talent-tree/index whose data matches WoW: Forever (7 rows, 51 points). As of 2026-09-20 no Forever
namespace exists (the classic ones have no talent endpoints); see site_build/wow_talents.py for how the data is used.
"""
import base64
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_NAMESPACES = ["static-us", "static-classic-us", "static-classic1x-us"]
PATHS = ["/data/wow/playable-class/index", "/data/wow/playable-specialization/index", "/data/wow/talent/index",
         "/data/wow/talent-tree/index", "/data/wow/playable-race/index"]


def load_env() -> dict:
    env = {}
    for line in (Path(__file__).parent / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def call(url: str, headers=None, data=None):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}, data=data), timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:300]
    except Exception as e:  # noqa: BLE001
        return "ERR", str(e)[:200]


def main() -> None:
    env = load_env()
    cid, secret = env.get("BLIZZARD_CLIENT_ID", ""), env.get("BLIZZARD_CLIENT_SECRET", "")
    if not (cid and secret):
        sys.exit("BLIZZARD_CLIENT_ID / BLIZZARD_CLIENT_SECRET missing in .env")
    basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    status, body = call("https://oauth.battle.net/token", {"Authorization": "Basic " + basic, "Content-Type": "application/x-www-form-urlencoded"},
                        b"grant_type=client_credentials")
    print("token request:", status)
    if status != 200:
        sys.exit("authentication failed -- check the client id/secret in .env")
    token = json.loads(body)["access_token"]
    print("\nnamespace x endpoint -> HTTP status (200 = served, 404 = endpoint absent, 403 = unknown namespace)")
    for ns in DEFAULT_NAMESPACES + sys.argv[1:]:
        row = []
        for p in PATHS:
            q = urllib.parse.urlencode({"namespace": ns, "locale": "en_US"})
            s, b = call(f"https://us.api.blizzard.com{p}?{q}", {"Authorization": "Bearer " + token})
            note = ""
            if s == 200:
                try:
                    d = json.loads(b)
                    keys = [k for k in d if k != "_links"]
                    note = f"({keys[0]}:{len(d[keys[0]])})" if keys and isinstance(d[keys[0]], list) else ""
                except Exception:  # noqa: BLE001
                    pass
            row.append(f"{p.split('/')[-2]}={s}{note}")
        print(f"{ns:24}", " | ".join(row))


if __name__ == "__main__":
    main()
