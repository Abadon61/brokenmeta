#!/usr/bin/env python
"""Opt-in, resumable collection of match timelines for the champion guides (skill order, starting items, item order).

    py -3.11 lol_timeline_run.py --dry-run          # plan only: how many calls, no API request
    py -3.11 lol_timeline_run.py                    # collect (needs a valid key in .env)
    py -3.11 lol_timeline_run.py --k 40 --limit 500

Costs ONE Riot call per selected match (matches already sit in data/raw_lol/, so nothing else is fetched). The
selection is the smallest set of cached matches giving every champion+role section at least --k timelines.
Already-fetched matches are skipped, so an interrupted or expired-key run simply resumes. Throughput is capped
at --budget requests per 2 minutes (default 50 of the 100 allowed) so the live site's profile lookups keep
headroom on the shared key. Afterwards run `py -3.11 lol_guide_run.py` then the site build.
"""
import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from tft_tracker import config  # noqa: E402
from tft_tracker.lol_guide import load_item_meta  # noqa: E402
from tft_tracker.lol_riot_client import LANE_TO_ROLE, LolRiotClient  # noqa: E402
from tft_tracker.riot_client import RiotAPIError  # noqa: E402
from tft_tracker.lol_timeline import (MIN_GAME_SECONDS, TIMELINE_DIR, regional_for, select_matches,  # noqa: E402
                                      summarize_timeline)

CACHE_DIR = Path("data/raw_lol")


def load_matches() -> tuple[dict[str, Path], list[tuple[str, list[tuple[str, str]]]]]:
    paths, meta = {}, []
    for path in CACHE_DIR.glob("*.json"):
        if path.name.startswith("_"):
            continue
        try:
            m = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        info = m.get("info", {})
        if info.get("queueId") != 420 or (info.get("gameDuration") or 0) < MIN_GAME_SECONDS:
            continue
        mid = m["metadata"]["matchId"]
        paths[mid] = path
        meta.append((mid, [(p["championName"].lower(), LANE_TO_ROLE.get(p.get("individualPosition"))) for p in info["participants"]]))
    return paths, meta


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=30, help="timelines wanted per champion+role section (default 30)")
    ap.add_argument("--limit", type=int, default=0, help="stop after this many timelines this run (0 = no limit)")
    ap.add_argument("--budget", type=int, default=50, help="max requests per 2 minutes (Riot allows 100; default 50)")
    ap.add_argument("--dry-run", action="store_true", help="only print the plan, make no API request")
    args = ap.parse_args()

    guide = json.loads(Path(f"{config.OUTPUT_DIR}/lol_champion_guide.json").read_text(encoding="utf-8"))["by_champion"]
    targets = {(champ.lower(), role) for champ, v in guide.items() for role in v["roles"]}
    paths, meta = load_matches()
    TIMELINE_DIR.mkdir(parents=True, exist_ok=True)
    done = {p.stem for p in TIMELINE_DIR.glob("*.json")}
    todo = select_matches(meta, targets, args.k, already=done)
    if args.limit:
        todo = todo[:args.limit]
    per_min = args.budget / 2
    print(f"{len(meta)} cached ranked matches, {len(targets)} champion+role sections, target {args.k} timelines each.")
    print(f"{len(done)} timelines already collected; {len(todo)} more needed -> ~{len(todo) / per_min:.0f} min at {args.budget} requests/2 min.")
    if args.dry_run or not todo:
        return

    version = json.load(urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json"))[0]
    items = json.load(urllib.request.urlopen(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"))
    core_ids, boot_ids = load_item_meta(items)

    client = LolRiotClient(use_cache=False, verbose=False)
    min_gap = 120.0 / args.budget
    started, last = time.time(), 0.0
    for n, mid in enumerate(todo, 1):
        wait = min_gap - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        last = time.time()
        try:
            timeline = client.get_timeline(regional_for(mid), mid)
        except RiotAPIError as exc:
            if exc.status in (401, 403):
                print(f"\nStopped: Riot rejected the key (HTTP {exc.status}). Renew it in .env and re-run: progress is kept.")
                return
            print(f"skip {mid}: HTTP {exc.status}")
            continue
        if not timeline:
            print(f"skip {mid}: no timeline")
            continue
        match = json.loads(paths[mid].read_text(encoding="utf-8"))
        summary = summarize_timeline(match, timeline, core_ids, boot_ids)
        (TIMELINE_DIR / f"{mid}.json").write_text(json.dumps(summary, separators=(",", ":")), encoding="utf-8")
        if n % 25 == 0 or n == len(todo):
            elapsed = time.time() - started
            print(f"{n}/{len(todo)} timelines ({elapsed / 60:.1f} min elapsed, ~{(len(todo) - n) * elapsed / n / 60:.0f} min left)")
    print("Done. Now run: py -3.11 lol_guide_run.py   then rebuild the site.")


if __name__ == "__main__":
    main()
