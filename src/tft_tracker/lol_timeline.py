"""Skill order / starting items / item order for the champion guides, from Match-V5 *timelines*.

Unlike everything else in lol_guide.py this needs one extra Riot API call per
match (GET /lol/match/v5/matches/{id}/timeline), so it is a separate, opt-in,
resumable collection (lol_timeline_run.py): the guides simply omit these
sections until timeline summaries exist.

A timeline covers all 10 participants, so `select_matches` picks the smallest
set of already-cached matches that gives every (champion, role) section at
least K games (greedy set cover). Only a compact per-participant summary is
stored (data/raw_lol/_timelines/<matchId>.json), never the raw timeline.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from .lol_riot_client import LANE_TO_ROLE

TIMELINE_DIR = Path("data/raw_lol/_timelines")
MIN_GAME_SECONDS = 300
START_WINDOW_MS = 90_000
TRINKETS = {3340, 3363, 3364, 2055}          # warding trinkets + control ward: noise in a "starting items" list
SLOT_LETTER = {1: "Q", 2: "W", 3: "E", 4: "R"}
MIN_TL_GAMES = 15                             # a skill order / item path needs this many timelines to be shown
REGIONAL = {"BR1": "americas", "NA1": "americas", "LA1": "americas", "LA2": "americas", "OC1": "sea",
            "EUW1": "europe", "EUN1": "europe", "TR1": "europe", "RU": "europe", "KR": "asia", "JP1": "asia"}


def regional_for(match_id: str) -> str:
    return REGIONAL.get(match_id.split("_")[0], "europe")


def select_matches(matches: list[tuple[str, list[tuple[str, str]]]], targets: set[tuple[str, str]], k: int,
                   already: set[str] | None = None) -> list[str]:
    """matches: [(matchId, [(champion_lower, role), ...10])]. Greedy set cover: returns the match ids still to fetch so
    that every reachable target gets >= k timelines, counting the ids in `already` (fetched on a previous run) first."""
    counts: Counter = Counter()
    already = already or set()
    by_id = dict(matches)
    for mid in already:
        for key in by_id.get(mid, []):
            if key in targets:
                counts[key] += 1
    avail: Counter = Counter(key for _, keys in matches for key in keys if key in targets)
    unfilled = {t for t in targets if avail[t] >= k and counts[t] < k}
    pool = [(mid, [key for key in keys if key in targets]) for mid, keys in matches if mid not in already]
    chosen: list[str] = []
    while unfilled and pool:
        best_i, best_score = -1, 0
        for i, (_, keys) in enumerate(pool):
            score = sum(1 for key in keys if key in unfilled and counts[key] < k)
            if score > best_score:
                best_i, best_score = i, score
        if best_score == 0:
            break
        mid, keys = pool.pop(best_i)
        chosen.append(mid)
        for key in keys:
            counts[key] += 1
            if counts[key] >= k:
                unfilled.discard(key)
    return chosen


def summarize_timeline(match: dict, timeline: dict, core_ids: set[int], boot_ids: set[int]) -> dict:
    """Compact per-participant summary of one match + its timeline."""
    info = match["info"]
    who = {p["participantId"]: p for p in info["participants"]}
    skills: dict[int, list[str]] = defaultdict(list)
    buys: dict[int, list[tuple[int, int]]] = defaultdict(list)      # (timestamp, itemId), undo-aware
    frames = (timeline.get("info") or {}).get("frames") or []
    for frame in frames:
        for ev in frame.get("events") or []:
            pid = ev.get("participantId")
            typ = ev.get("type")
            if typ == "SKILL_LEVEL_UP" and ev.get("levelUpType", "NORMAL") == "NORMAL" and ev.get("skillSlot") in SLOT_LETTER:
                skills[pid].append(SLOT_LETTER[ev["skillSlot"]])
            elif typ == "ITEM_PURCHASED":
                buys[pid].append((ev.get("timestamp", 0), ev["itemId"]))
            elif typ == "ITEM_UNDO" and buys[pid] and buys[pid][-1][1] == ev.get("beforeId"):
                buys[pid].pop()

    def frame_stats(idx: int, pid: int) -> dict | None:
        if idx >= len(frames):
            return None
        pf = (frames[idx].get("participantFrames") or {}).get(str(pid))
        if not pf:
            return None
        return {"gold": pf.get("totalGold"), "xp": pf.get("xp"), "cs": (pf.get("minionsKilled") or 0) + (pf.get("jungleMinionsKilled") or 0)}

    out = {}
    for pid, p in who.items():
        role = LANE_TO_ROLE.get(p.get("individualPosition"))
        if not role:
            continue
        seq = buys.get(pid, [])
        start = sorted(i for t, i in seq if t <= START_WINDOW_MS and i not in TRINKETS)
        completed, seen = [], set()
        for _, iid in seq:
            if iid in core_ids and iid not in seen:
                seen.add(iid)
                completed.append(iid)
        boots = next((iid for _, iid in seq if iid in boot_ids), None)
        out[str(pid)] = {
            "champion": p.get("championName"), "role": role, "win": bool(p.get("win")),
            "skills": skills.get(pid, [])[:18], "start": start, "core": completed[:4], "boots": boots,
            "at10": frame_stats(10, pid), "at15": frame_stats(15, pid),
        }
    return {"matchId": match["metadata"]["matchId"], "duration": info.get("gameDuration"), "participants": out}


def load_summaries(directory: Path = TIMELINE_DIR) -> list[dict]:
    out = []
    if directory.exists():
        for path in directory.glob("*.json"):
            try:
                out.append(json.loads(path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue
    return out


def _rate(w: int, g: int) -> float:
    return round(w / g, 4) if g else 0.0


def aggregate_timelines(summaries: list[dict]) -> dict[tuple[str, str], dict]:
    """(championName, role) -> {"games", "skills": [...], "start_items": [...], "item_paths": [...], "lane": {...}}.
    Only groups reaching MIN_TL_GAMES are kept; everything else is simply absent."""
    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for s in summaries:
        for part in s.get("participants", {}).values():
            cells[(part["champion"], part["role"])].append(part)
    result = {}
    for key, parts in cells.items():
        if len(parts) < MIN_TL_GAMES:
            continue
        out: dict = {"games": len(parts)}

        # skill order: which of Q/W/E is maxed first, second, third (order in which they reach rank 5)
        groups: dict[str, list[dict]] = defaultdict(list)
        for p in parts:
            counts: Counter = Counter()
            order = []
            for letter in p["skills"]:
                if letter == "R":
                    continue
                counts[letter] += 1
                if counts[letter] == 5:
                    order.append(letter)
            if len(order) >= 2:
                groups[">".join(order)].append(p)
        skill_rows = []
        for order, ps in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:3]:
            if len(ps) < MIN_TL_GAMES:
                continue
            modal = Counter(tuple(p["skills"][:15]) for p in ps if len(p["skills"]) >= 15).most_common(1)
            skill_rows.append({"order": order, "games": len(ps), "win_rate": _rate(sum(p["win"] for p in ps), len(ps)),
                               "levels": list(modal[0][0]) if modal else []})
        if skill_rows:
            out["skills"] = skill_rows

        start = Counter(tuple(p["start"]) for p in parts if p["start"])
        out["start_items"] = [{"items": list(items), "games": n, "win_rate": _rate(sum(p["win"] for p in parts if tuple(p["start"]) == items), n)}
                              for items, n in start.most_common(3) if n >= MIN_TL_GAMES]
        paths = Counter(tuple(p["core"][:3]) for p in parts if len(p["core"]) >= 3)
        out["item_paths"] = [{"items": list(items), "games": n, "win_rate": _rate(sum(p["win"] for p in parts if tuple(p["core"][:3]) == items), n)}
                             for items, n in paths.most_common(3) if n >= MIN_TL_GAMES]

        def avg(field: str, sub: str) -> float | None:
            vals = [p[field][sub] for p in parts if p.get(field) and p[field].get(sub) is not None]
            return round(sum(vals) / len(vals), 1) if len(vals) >= MIN_TL_GAMES else None

        lane = {f"{sub}_{field}": avg(field, sub) for field in ("at10", "at15") for sub in ("gold", "xp", "cs")}
        if any(v is not None for v in lane.values()):
            out["lane"] = lane
        result[key] = out
    return result
