#!/usr/bin/env python
"""Precomputes the reroll/leveling "Plan de jeu" (gameplan) text for every
comp that gets a real /compo/<slug>/ page, using gameplan.py's real Monte
Carlo simulation (a faithful Python port of the user's own validated
gameplan.js).

This is slow -- real simulation, ~5-7s per comp in Python (the JS original
is sub-second; V8's JIT vs. interpreted Python on the same tight loops).
Deliberately kept as its OWN script, separate from site_build/build_site.py:
that script needs to stay fast since it gets rerun constantly for routine
template/CSS iteration, so it only READS this script's output
(data/output/gameplans.json), never runs the simulation itself. Re-run this
script after a real match-data refresh (tierlist.json changed); no need to
re-run it for a template/CSS-only site_build.

Star target per champion is derived from the comp's own empirical
threeStarRate (already computed from real match data -- no new data field
needed): star = 3 if threeStarRate >= STAR_THRESHOLD else star = 1. This
rule was picked because it exactly reproduces the star targets the user
specified for "Eclipse Kayle Reroll" (confirmed 2026-09-07), and
generate_gameplan() on those targets correctly recommends leveling to 5
with a ~200g median cost, matching the user's own expectation for that comp.

Usage:
    py compute_gameplans.py [--tierlist data/output/tierlist.json] [--out data/output/gameplans.json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT / "src"))

from tft_tracker.gameplan import generate_gameplan  # noqa: E402

# Reuse build_site.py's own filter_quality() -- must match exactly which
# comps get a real page, or this would waste time on comps nobody sees (or
# skip ones that do). Imported by path (not a package), same technique used
# elsewhere in this project for one-off scripts against build_site.py.
_spec = importlib.util.spec_from_file_location("build_site", PROJECT / "site_build" / "build_site.py")
_build_site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_build_site)

STAR_THRESHOLD = 0.6


def derive_star(three_star_rate: float | None) -> int:
    return 3 if (three_star_rate or 0) >= STAR_THRESHOLD else 1


def build_targets(core_units: list[dict] | None) -> list[dict]:
    return [
        {"id": u["champion"], "name": u["champion"], "cost": u["cost"], "star": derive_star(u.get("threeStarRate"))}
        for u in (core_units or [])
    ]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tierlist", default="data/output/tierlist.json")
    p.add_argument("--out", default="data/output/gameplans.json")
    args = p.parse_args()

    tierlist = json.loads(Path(args.tierlist).read_text(encoding="utf-8"))
    comps = _build_site.filter_quality(tierlist["comps"])
    print(f"Computing gameplans for {len(comps)} comps (real simulation, ~5-7s each -- this takes a while)...")

    results: dict[str, list[dict]] = {}
    started = time.monotonic()
    for i, c in enumerate(comps, 1):
        targets = build_targets(c.get("core_units"))
        results[c["key"]] = generate_gameplan(targets)
        if i % 10 == 0 or i == len(comps):
            elapsed = time.monotonic() - started
            eta = elapsed / i * (len(comps) - i)
            print(f"  {i}/{len(comps)} done ({elapsed:.0f}s elapsed, ~{eta:.0f}s left)")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(results)} gameplans to {out_path} in {time.monotonic() - started:.0f}s total.")


if __name__ == "__main__":
    main()
