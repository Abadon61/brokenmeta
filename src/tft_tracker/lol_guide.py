"""Champion-guide aggregates for /league/guide/<champion>/ -- everything here is
measured from ranked-solo matches already sitting in the local cache
(data/raw_lol/), so producing it costs NO Riot API call (unlike a collection
run, which is why it lives in its own entry point, lol_guide_run.py, and
never touches the role-stats history snapshots).

Per champion + role it computes, from every participant of every cached match:
  * average per-game stats and the champion's own damage split
    (physical / magic / true),
  * win rate by game length (short / mid / long),
  * summoner-spell pairs, boots, and the most frequent 3-item cores
    (final inventories; "core-eligible" = completed, non-boots items),
  * full rune pages: for each keystone + secondary tree, the most picked rune
    of every row (share of that page's games), the 2 secondary runes and the stat shards,
  * how the champion's final items perform against an enemy team that is
    mostly physical damage, mostly magic damage, or mixed -- the data behind
    "what to build against a given kind of counter".

Nothing is invented: every list is filtered by a minimum number of games, and
a section with too little data simply isn't produced.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from .lol_riot_client import LANE_TO_ROLE

MIN_GAME_SECONDS = 300           # remakes / early surrenders distort every per-minute number
MIN_ROLE_GAMES = 40              # a (champion, role) needs this many games to get a guide section at all
MIN_SPELL_GAMES = 15
MIN_BOOT_GAMES = 15
MIN_CORE_GAMES = 8
MIN_VS_ITEM_GAMES = 10
MIN_VS_BUCKET_GAMES = 40         # an enemy-comp bucket needs this many games to be shown
AP_HEAVY_MAGIC_SHARE = 0.50      # enemy team magic-damage share >= this  -> "ap" (~29% of teams)
AD_HEAVY_MAGIC_SHARE = 0.35      # enemy team magic-damage share <  this  -> "ad" (~29% of teams)
MIN_RUNE_PAGE_GAMES = 25         # a keystone + secondary-tree combination needs this many games to be listed
DURATION_BUCKETS = (("short", 0, 25), ("mid", 25, 35), ("long", 35, 10_000))


def load_item_meta(items_json: dict) -> tuple[set[int], set[int]]:
    """(core_ids, boot_ids) from Data Dragon's item.json ("data" mapping):
    core = purchasable on Summoner's Rift, completed (builds into nothing),
    >= 2000 gold, not boots; boots = tagged Boots and completed."""
    core: set[int] = set()
    boots: set[int] = set()
    for sid, it in items_json.get("data", {}).items():
        gold = it.get("gold") or {}
        if not gold.get("purchasable") or not (it.get("maps") or {}).get("11") or it.get("into"):
            continue
        tags = it.get("tags") or []
        if "Boots" in tags:
            boots.add(int(sid))
        elif (gold.get("total") or 0) >= 2000 and "Consumable" not in tags and "Trinket" not in tags:
            core.add(int(sid))
    return core, boots


def _enemy_bucket(magic_share: float) -> str:
    if magic_share >= AP_HEAVY_MAGIC_SHARE:
        return "ap"
    if magic_share < AD_HEAVY_MAGIC_SHARE:
        return "ad"
    return "mixed"


def _team_damage(participants: list[dict], team_id: int) -> tuple[int, int, int]:
    ps = [p for p in participants if p.get("teamId") == team_id]
    return (sum(p.get("physicalDamageDealtToChampions") or 0 for p in ps),
            sum(p.get("magicDamageDealtToChampions") or 0 for p in ps),
            sum(p.get("trueDamageDealtToChampions") or 0 for p in ps))


def _new_cell() -> dict:
    return {
        "games": 0, "wins": 0,
        "sums": Counter(),                              # kills, deaths, ... (per-game sums)
        "dmg": [0, 0, 0],                               # phys, magic, true (champion's own)
        "duration": {b[0]: [0, 0] for b in DURATION_BUCKETS},   # bucket -> [games, wins]
        "spells": defaultdict(lambda: [0, 0]),          # (a, b) -> [games, wins]
        "boots": defaultdict(lambda: [0, 0]),           # item -> [games, wins]
        "core": defaultdict(lambda: [0, 0]),            # (a, b, c) -> [games, wins]
        "items": defaultdict(lambda: [0, 0]),           # core-eligible item -> [games, wins]
        "runes": {},                                    # (primary tree, keystone, secondary tree) -> aggregate
        "vs": {k: {"games": 0, "wins": 0, "items": defaultdict(lambda: [0, 0])} for k in ("ap", "ad", "mixed")},
    }


def _tally_runes(store: dict, perks: dict, win: bool) -> None:
    styles = {st.get("description"): st for st in perks.get("styles") or []}
    prim, sub = styles.get("primaryStyle"), styles.get("subStyle")
    if not prim or not sub or len(prim.get("selections") or []) < 4 or len(sub.get("selections") or []) < 2:
        return
    ids = [sel["perk"] for sel in prim["selections"]]
    key = (prim["style"], ids[0], sub["style"])
    agg = store.get(key)
    if agg is None:
        agg = store[key] = {"games": 0, "wins": 0, "primary": [Counter() for _ in range(3)], "secondary": Counter(), "shards": [Counter() for _ in range(3)]}
    agg["games"] += 1
    agg["wins"] += win
    for row, rune in enumerate(ids[1:4]):
        agg["primary"][row][rune] += 1
    for sel in sub["selections"][:2]:
        agg["secondary"][sel["perk"]] += 1
    stat = perks.get("statPerks") or {}
    for row, name in enumerate(("offense", "flex", "defense")):
        if stat.get(name):
            agg["shards"][row][stat[name]] += 1


def _rune_pages(store: dict) -> list[dict]:
    pages = []
    for (prim_tree, keystone, sub_tree), a in sorted(store.items(), key=lambda kv: -kv[1]["games"]):
        g = a["games"]
        if g < MIN_RUNE_PAGE_GAMES or len(pages) >= 3:
            continue
        top = lambda c: [{"id": rid, "share": round(n / g, 3)} for rid, n in c.most_common(1)]
        pages.append({
            "primary_tree": prim_tree, "keystone": keystone, "secondary_tree": sub_tree,
            "games": g, "win_rate": round(a["wins"] / g, 4),
            "primary_rows": [top(c)[0] for c in a["primary"]],
            "secondary": [{"id": rid, "share": round(n / g, 3)} for rid, n in a["secondary"].most_common(2)],
            "shards": [top(c)[0] if c else None for c in a["shards"]],
        })
    return pages


def build_guide_output(matches: list[dict], core_ids: set[int], boot_ids: set[int]) -> dict:
    cells: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(_new_cell))
    seen: set[str] = set()
    used = 0
    for match in matches:
        mid = match.get("metadata", {}).get("matchId")
        info = match.get("info", {})
        if not mid or mid in seen or info.get("queueId") != 420 or (info.get("gameDuration") or 0) < MIN_GAME_SECONDS:
            continue
        seen.add(mid)
        used += 1
        duration_min = info["gameDuration"] / 60
        participants = info.get("participants", [])
        team_kills = defaultdict(int)
        for p in participants:
            team_kills[p.get("teamId")] += p.get("kills") or 0
        enemy_bucket = {}
        for team in (100, 200):
            phys, magic, true = _team_damage(participants, 300 - team)   # damage dealt BY the other team
            total = phys + magic + true
            enemy_bucket[team] = _enemy_bucket(magic / total) if total else "mixed"

        for p in participants:
            role = LANE_TO_ROLE.get(p.get("individualPosition"))
            champ = p.get("championName")
            if not role or not champ:
                continue
            win = bool(p.get("win"))
            cell = cells[champ][role]
            cell["games"] += 1
            cell["wins"] += win
            s = cell["sums"]
            s["kills"] += p.get("kills") or 0
            s["deaths"] += p.get("deaths") or 0
            s["assists"] += p.get("assists") or 0
            s["cs_per_min"] += ((p.get("totalMinionsKilled") or 0) + (p.get("neutralMinionsKilled") or 0)) / duration_min
            s["gold_per_min"] += (p.get("goldEarned") or 0) / duration_min
            s["dpm"] += (p.get("totalDamageDealtToChampions") or 0) / duration_min
            s["kp"] += ((p.get("kills") or 0) + (p.get("assists") or 0)) / max(1, team_kills[p.get("teamId")]) * 100
            s["cc_time"] += p.get("timeCCingOthers") or 0
            s["vision_per_min"] += (p.get("visionScore") or 0) / duration_min
            cell["dmg"][0] += p.get("physicalDamageDealtToChampions") or 0
            cell["dmg"][1] += p.get("magicDamageDealtToChampions") or 0
            cell["dmg"][2] += p.get("trueDamageDealtToChampions") or 0
            for name, lo, hi in DURATION_BUCKETS:
                if lo <= duration_min < hi:
                    cell["duration"][name][0] += 1
                    cell["duration"][name][1] += win
                    break
            _tally_runes(cell["runes"], p.get("perks") or {}, win)
            spells = tuple(sorted((p.get("summoner1Id") or 0, p.get("summoner2Id") or 0)))
            cell["spells"][spells][0] += 1
            cell["spells"][spells][1] += win

            final = {p.get(f"item{i}") for i in range(6)} - {0, None}
            for it in final & boot_ids:
                cell["boots"][it][0] += 1
                cell["boots"][it][1] += win
            cores = sorted(final & core_ids)
            for it in cores:
                cell["items"][it][0] += 1
                cell["items"][it][1] += win
            for trio in combinations(cores, 3):
                cell["core"][trio][0] += 1
                cell["core"][trio][1] += win
            vs = cell["vs"][enemy_bucket[p.get("teamId")]]
            vs["games"] += 1
            vs["wins"] += win
            for it in cores:
                vs["items"][it][0] += 1
                vs["items"][it][1] += win

    def rate(w: int, g: int) -> float:
        return round(w / g, 4) if g else 0.0

    by_champion: dict[str, dict] = {}
    for champ, roles in cells.items():
        out_roles: dict[str, dict] = {}
        for role, c in roles.items():
            g = c["games"]
            if g < MIN_ROLE_GAMES:
                continue
            dmg_total = sum(c["dmg"]) or 1
            item_rate = {it: rate(w, n) for it, (n, w) in c["items"].items()}
            vs_out = {}
            for bucket, v in c["vs"].items():
                if v["games"] < MIN_VS_BUCKET_GAMES:
                    continue
                items = [
                    {"item_id": it, "games": n, "win_rate": rate(w, n), "lift": round(rate(w, n) - item_rate.get(it, rate(w, n)), 4)}
                    for it, (n, w) in sorted(v["items"].items(), key=lambda kv: -kv[1][0]) if n >= MIN_VS_ITEM_GAMES
                ][:8]
                vs_out[bucket] = {"games": v["games"], "win_rate": rate(v["wins"], v["games"]), "items": items}
            out_roles[role] = {
                "games": g, "win_rate": rate(c["wins"], g),
                "avg": {k: round(v / g, 2) for k, v in c["sums"].items()},
                "damage_split": {"physical": round(c["dmg"][0] / dmg_total, 3), "magic": round(c["dmg"][1] / dmg_total, 3), "true": round(c["dmg"][2] / dmg_total, 3)},
                "duration": [{"bucket": b, "games": n, "win_rate": rate(w, n)} for b, (n, w) in c["duration"].items() if n],
                "spells": [{"ids": list(ids), "games": n, "win_rate": rate(w, n)}
                           for ids, (n, w) in sorted(c["spells"].items(), key=lambda kv: -kv[1][0]) if n >= MIN_SPELL_GAMES][:4],
                "boots": [{"item_id": it, "games": n, "win_rate": rate(w, n)}
                          for it, (n, w) in sorted(c["boots"].items(), key=lambda kv: -kv[1][0]) if n >= MIN_BOOT_GAMES][:3],
                "core_builds": [{"items": list(trio), "games": n, "win_rate": rate(w, n)}
                                for trio, (n, w) in sorted(c["core"].items(), key=lambda kv: -kv[1][0]) if n >= MIN_CORE_GAMES][:5],
                "vs_enemy": vs_out,
                "runes": _rune_pages(c["runes"]),
            }
        if out_roles:
            by_champion[champ] = {"roles": out_roles}
    return {"unique_matches": used, "by_champion": by_champion}


def write_guide_output(output: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=1), encoding="utf-8")
