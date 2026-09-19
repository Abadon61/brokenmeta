#!/usr/bin/env python
"""Entry point: `py lol_guide_run.py` -- recomputes the champion-guide aggregates
(data/output/lol_champion_guide.json) from the matches already cached in
data/raw_lol/. Makes NO Riot API call (only one Data Dragon request for item
metadata) and never touches the role-stats history. See src/tft_tracker/lol_guide.py."""
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from tft_tracker import config  # noqa: E402
from tft_tracker.lol_guide import build_guide_output, load_item_meta, write_guide_output  # noqa: E402
from tft_tracker.lol_timeline import aggregate_timelines, load_summaries  # noqa: E402

CACHE_DIR = Path("data/raw_lol")
OUT = Path(f"{config.OUTPUT_DIR}/lol_champion_guide.json")


def main() -> None:
    version = json.load(urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json"))[0]
    items = json.load(urllib.request.urlopen(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"))
    core_ids, boot_ids = load_item_meta(items)
    print(f"Data Dragon {version}: {len(core_ids)} core-eligible items, {len(boot_ids)} boots.")

    matches = []
    for path in CACHE_DIR.glob("*.json"):
        if path.name.startswith("_"):
            continue
        try:
            matches.append(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    print(f"{len(matches)} cached match files read.")

    summaries = load_summaries()
    timeline_stats = aggregate_timelines(summaries) if summaries else None
    print(f"{len(summaries)} timeline summaries -> {len(timeline_stats or {})} champion+role groups with skill/item data.")
    output = build_guide_output(matches, core_ids, boot_ids, timeline_stats)
    write_guide_output(output, OUT)
    n_roles = sum(len(c["roles"]) for c in output["by_champion"].values())
    print(f"{output['unique_matches']} ranked-solo matches -> {len(output['by_champion'])} champions, {n_roles} champion+role sections -> {OUT}")


if __name__ == "__main__":
    main()
