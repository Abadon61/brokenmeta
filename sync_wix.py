#!/usr/bin/env python
"""Push already-generated data/output/*.json into Wix Data Collections.

Usage:
    py sync_wix.py                 # syncs all three (skips missing files)
    py sync_wix.py --only comps
    py sync_wix.py --only matchups,champions
    py sync_wix.py --prune         # also deletes stale items no longer in
                                    # the JSON (e.g. after a naming-scheme
                                    # change) -- irreversible on Wix's side

Requires WIX_API_KEY and WIX_SITE_ID in .env (see src/tft_tracker/wix_sync.py
docstring for where to get them and what collections/fields to create first).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from tft_tracker import config  # noqa: E402
from tft_tracker.wix_sync import sync_champions, sync_matchups, sync_tierlist  # noqa: E402

TARGETS = {
    "comps": (f"{config.OUTPUT_DIR}/tierlist.json", sync_tierlist, "Comp"),
    "matchups": (f"{config.OUTPUT_DIR}/matchups.json", sync_matchups, "Matchups"),
    "champions": (f"{config.OUTPUT_DIR}/champion_stats.json", sync_champions, "Champions"),
}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--only", default=None, help="Comma-separated subset of: comps,matchups,champions")
    p.add_argument("--prune", action="store_true",
                    help="Delete stale items no longer produced by the current JSON. Irreversible.")
    args = p.parse_args()

    names = [n.strip() for n in args.only.split(",")] if args.only else list(TARGETS)

    for name in names:
        if name not in TARGETS:
            raise SystemExit(f"Unknown target '{name}'. Known: {list(TARGETS)}")
        path, sync_fn, collection_id = TARGETS[name]
        if not Path(path).exists():
            print(f"[skip] {name}: {path} not found (run the pipeline first)")
            continue
        print(f"[sync] {name} -> Wix collection '{collection_id}' ...")
        try:
            result = sync_fn(path, prune=args.prune)
        except RuntimeError as e:
            raise SystemExit(f"error: {e}")
        print(f"        inserted={result['inserted']} updated={result['updated']} "
              f"failures={result['failures']}" + (f" pruned={result['pruned']}" if args.prune else ""))
        if result["errors"]:
            print(f"        first error: {result['errors'][0]}")


if __name__ == "__main__":
    main()
