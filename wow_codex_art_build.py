"""Build the art/boss table of the dungeon pages of BrokenCodex (data/wow_dungeons/art.json).

For every dungeon of data/wow_dungeons/dungeons.json:
  - image    a FileDataID of the game's own loading screen of that instance (client tables Map + LoadingScreens,
             read from wago.tools for the Forever client build): the addon shows it with SetTexture(fileID), so
             no Blizzard art is shipped inside the addon;
  - bosses   the encounters of the instance in the game's order (client table DungeonEncounter, English + French
             names) with the NPC id of the boss (Wowhead's NPC list of the zone, exact name match; None when the
             encounter is an event such as the Ring of Law), used to show the boss' head with a PlayerModel.

Run: python wow_codex_art_build.py   (needs the network; the result is committed, the addon build only reads it)
"""
from __future__ import annotations

import csv
import io
import json
import re
import time
import urllib.request
from pathlib import Path

P = Path(__file__).resolve().parent
OUT = P / "data" / "wow_dungeons" / "art.json"
BUILD = "1.60.1.70094"
UA = {"User-Agent": "Mozilla/5.0"}

# dungeon slug -> client map id
MAP_ID = {
    "ragefire-chasm": 389, "deadmines": 36, "wailing-caverns": 43, "shadowfang-keep": 33, "blackfathom-deeps": 48,
    "stockade": 34, "gnomeregan": 90, "scarlet-monastery": 189, "razorfen-kraul": 47, "razorfen-downs": 129,
    "uldaman": 70, "zulfarrak": 209, "maraudon": 349, "sunken-temple": 109, "blackrock-depths": 230, "dire-maul": 429,
    "stratholme": 329, "scholomance": 289, "ruins-of-lordaeron": 2999, "hall-of-thanes": 3065,
}


# raid slug -> client map id (loading screen only: the bosses of a raid come from data/wow_raids)
RAID_MAP = {"molten-core": 409}


CACHE = P / "data" / "wow_wowhead_raw" / "codex_cache"


def get(url):
    """A page, from the disk cache when already fetched (the run can be resumed, Wowhead is spared)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (re.sub(r"[^A-Za-z0-9]+", "_", url) + ".txt")
    if f.exists():
        return f.read_text(encoding="utf-8")
    time.sleep(3.0)
    req = urllib.request.Request(url, headers=UA)
    text = urllib.request.urlopen(req, timeout=90).read().decode("utf-8")
    f.write_text(text, encoding="utf-8")
    return text


def wago(table, locale=None):
    url = f"https://wago.tools/db2/{table}/csv?build={BUILD}" + (f"&locale={locale}" if locale else "")
    return list(csv.DictReader(io.StringIO(get(url))))


def listview(html, template):
    """The data of a Wowhead listview (npc, quest...) as a list of dicts."""
    i = html.index(f"template: '{template}'")
    j = html.index("data: [", i) + len("data: ")
    depth, k = 0, j
    while True:
        c = html[k]
        depth += c == "["
        depth -= c == "]"
        k += 1
        if depth == 0:
            break
    return json.loads(html[j:k])


_cache = {}


def page(host, kind, id_):
    key = (host, kind, id_)
    if key not in _cache:
        _cache[key] = get(f"https://{host}.wowhead.com/classic/{kind}={id_}")
    return _cache[key]


def where(host, kind, id_):
    """(zone name, x, y) of an NPC or object from its Wowhead map data, or None."""
    m = re.search(r"g_mapperData = (\{.*?\});", page(host, kind, id_))
    if not m:
        return None
    data = json.loads(m.group(1))
    for zone in data.values():
        for spot in zone:
            if spot.get("coords"):
                x, y = spot["coords"][0]
                return spot.get("uiMapName", ""), x, y
    return None


def quest_info(qid):
    """Who gives a quest: {npc|object|item id, name {en, fr}, zone {en, fr}, x, y}."""
    html = page("www", "quest", qid)
    m = re.search(r"Start: \[url=\\/classic\\/(npc|object|item)=(\d+)[^\]]*\]([^\[]+)\[", html)
    if not m:
        return None
    kind, id_, name = m.group(1), int(m.group(2)), m.group(3)
    info = {"kind": kind, "id": id_, "name": {"en": name, "fr": name}}
    if kind != "item":
        en = where("www", kind, id_)
        fr = where("fr", kind, id_)
        if en:
            info.update({"zone": {"en": en[0], "fr": (fr or en)[0]}, "x": en[1], "y": en[2]})
        fm = re.search(r"<title>([^<]+?) - ", page("fr", kind, id_))
        if fm:
            info["name"]["fr"] = fm.group(1).strip()
    return info


def wowhead_npcs(zone, host="www"):
    """NPCs of a zone: [{id, name, classification}], bosses (classification 3) first."""
    html = get(f"https://{host}.wowhead.com/classic/zone={zone}")
    i = html.index("template: 'npc'")
    j = html.index("data: [", i) + len("data: ")
    depth, k = 0, j
    while True:
        c = html[k]
        depth += c == "["
        depth -= c == "]"
        k += 1
        if depth == 0:
            break
    npcs = json.loads(html[j:k])
    return sorted(({"id": n["id"], "name": n["name"], "c": n.get("classification") or 0} for n in npcs), key=lambda n: -n["c"])


def main():
    dungeons = json.loads((P / "data" / "wow_dungeons" / "dungeons.json").read_text(encoding="utf-8"))["dungeons"]
    maps = {r["ID"]: r for r in wago("Map")}
    screens = {r["ID"]: r for r in wago("LoadingScreens")}
    enc_en = wago("DungeonEncounter")
    enc_fr = {e["ID"]: e["Name_lang"] for e in wago("DungeonEncounter", "frFR")}
    out = {}
    failures = 0
    for dg in dungeons:
        slug, mid = dg["id"], str(MAP_ID[dg["id"]])
        scr = screens.get(maps[mid]["LoadingScreenID"], {})
        image = int(scr.get("NarrowScreenFileDataID") or 0) or int(scr.get("MainImageFileDataID") or 0)
        try:
            npcs = wowhead_npcs(dg["zone"])
            fr_npcs = {n["id"]: n["name"] for n in wowhead_npcs(dg["zone"], "fr")}
        except Exception as exc:  # a Forever-only zone has no classic page
            failures += "HTTP Error 403" in str(exc) or "429" in str(exc)
            print(f"  {slug}: no NPC list ({exc})")
            npcs, fr_npcs = [], {}
        by_name = {}
        for n in npcs:
            by_name.setdefault(n["name"], n)
        bosses, seen = [], set()
        for e in sorted((e for e in enc_en if e["MapID"] == mid), key=lambda e: int(e["OrderIndex"])):
            name = e["Name_lang"]
            if name in seen:
                continue
            seen.add(name)
            n = by_name.get(name)
            bosses.append({"name": {"en": name, "fr": enc_fr.get(e["ID"]) or name}, "npc": n and n["id"]})
        # Rare or boss mobs that drop loot without being an encounter (Ras Frostwhisper, Kirtonos...).
        for it in dg["items"]:
            for src in it.get("src", []):
                n = by_name.get(src)
                if it.get("kind") == "drop" and src not in seen and n and n["c"] in (2, 3, 4):
                    seen.add(src)
                    bosses.append({"name": {"en": src, "fr": fr_npcs.get(n["id"], src)}, "npc": n["id"], "extra": True})
        quests = {}
        names = sorted({src for it in dg["items"] if it.get("kind") == "quest" for src in it.get("src", [])})
        try:
            by_q = {q["name"]: q["id"] for q in listview(page("www", "zone", dg["zone"]), "quest")}
            fr_q = {q["id"]: q["name"] for q in listview(page("fr", "zone", dg["zone"]), "quest")}
        except Exception as exc:
            failures += "HTTP Error 403" in str(exc) or "429" in str(exc)
            print(f"  {slug}: no quest list ({exc})")
            by_q, fr_q = {}, {}
        for qn in names:
            qid = by_q.get(qn)
            row = {"name": {"en": qn, "fr": fr_q.get(qid, qn)}}
            if qid:
                row["id"] = qid
                try:
                    giver = quest_info(qid)
                except Exception as exc:
                    failures += "HTTP Error 403" in str(exc) or "429" in str(exc)
                    print(f"  quest {qn}: {exc}")
                    giver = None
                if giver:
                    row["giver"] = giver
            quests[qn] = row
        print(f"  {slug}: {len(quests)} quests, {sum(1 for q in quests.values() if q.get('giver', {}).get('x'))} with coordinates")
        out[slug] = {"image": image, "map": int(mid), "bosses": bosses, "quests": quests}
        print(f"{slug:20} image {image} bosses {len(bosses)} with npc {sum(1 for b in bosses if b['npc'])}")
    raids = {}
    for slug, mid in RAID_MAP.items():
        scr = screens.get(maps[str(mid)]["LoadingScreenID"], {})
        raids[slug] = {"image": int(scr.get("NarrowScreenFileDataID") or 0) or int(scr.get("MainImageFileDataID") or 0), "map": mid}
        print(f"{slug:20} image {raids[slug]['image']}")
    if failures:
        raise SystemExit(f"{failures} Wowhead page(s) failed: art.json NOT written (rerun later, the cache keeps what was fetched)")
    OUT.write_text(json.dumps({"build": BUILD, "dungeons": out, "raids": raids}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
