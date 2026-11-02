#!/usr/bin/env python
"""Catalogue of the items that can be shown in the transmog simulator (/wow-forever/transmogrification/): item -> appearance -> slot.

    py -3.11 wow_transmog_catalog_build.py                 # tables (wago.tools, build of the Forever product "wowf") -> data/wow_transmog_catalog.json
    py -3.11 wow_transmog_catalog_build.py --names         # first fetch the missing item names/qualities/icons (Wowhead tooltips, resumable), then build
    py -3.11 wow_transmog_catalog_build.py --build 1.60.1.70707 [--refresh]

Where the data comes from:
  * the client tables Item / ItemModifiedAppearance / ItemAppearance (item -> ItemAppearance -> ItemDisplayInfo = the id the 3D viewer loads),
    ItemSparse (names, quality, levels) and ManifestInterfaceData (icon file id -> icon name), published per build by wago.tools;
  * the original (vanilla) items are NOT in the client's name table (ItemSparse), so their name / quality / icon come from Wowhead's tooltip
    endpoint, one request per item with a pause, cached in data/wow_transmog_names.json so an interrupted run resumes where it stopped.
Output rows are arrays (compact): see COLS. Data is Blizzard's / Wowhead's: whether the site may show it is the site owner's decision.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import wow_talents_import as imp

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "wow_transmog_catalog.json"
NAMES = ROOT / "data" / "wow_transmog_names.json"
UA = "brokenmeta.gg transmog catalogue (independent fan site)"
TOOLTIP = "https://nether.wowhead.com/forever/tooltip/item/{id}?dataEnv=14&locale={loc}"
LOCALES = {"en": 0, "fr": 2}

# ItemClass 2 = weapons, 4 = armor; InventoryType -> the slot the simulator dresses (robes dress the chest, one-handers go to either hand...)
SLOT_OF_INV = {1: "head", 3: "shoulder", 4: "shirt", 5: "chest", 20: "chest", 6: "waist", 7: "legs", 8: "feet", 9: "wrist", 10: "hands", 16: "back", 19: "tabard",
               13: "mainhand", 17: "twohand", 21: "mainhand", 22: "offhand", 23: "offhand", 14: "shield", 15: "ranged", 25: "ranged", 26: "ranged"}
# developer leftovers the client still carries: "(Test)", "[PH]", "zz...", "Deprecated", "UNUSED", NPC-only "Monster - ..." gear
JUNK = re.compile(r"\(test\)|\btest\b|\[ph\]|placeholder|^zz|deprecated|unused|^monster\s*-|\bqa\b|\bdebug\b|\bnpc equip", re.I)
SOD_RANGE = (200000, 250000)           # Season of Discovery items (new ids 2xxxxx); WoW: Forever's own new items start at 250000 -- left out on purpose
MAX_LEVEL = 60                         # WoW Classic / Forever: nothing above level 60 is wearable, so nothing above it is listed
MAX_ITEM_LEVEL = 100                   # items with no level requirement (shirts, tabards, test pieces): vanilla's highest item level is ~92
COLS = ["id", "name_en", "name_fr", "quality", "icon", "inventory_type", "item_class", "item_subclass", "display_id", "appearance_id", "required_level"]


def read(name: str, build: str, locale=None, refresh=False) -> list[dict]:
    return imp.read(imp.fetch(name, build, locale, refresh))


TT_RLVL = re.compile(r"<!--rlvl-->(\d+)")
TT_ILVL = re.compile(r"<!--ilvl-->(\d+)")


def http_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None


def latest_forever_build() -> str:
    status, body = imp.http("https://wago.tools/api/builds")
    if status != 200:
        sys.exit(f"cannot list builds (HTTP {status})")
    builds = json.loads(body).get("wowf") or []
    if not builds:
        sys.exit("no wowf (WoW: Forever) builds listed")
    return sorted(builds, key=lambda b: b["created_at"], reverse=True)[0]["version"]


def wanted_items(build: str, refresh: bool):
    """Items with an appearance that the dressing room can show: {item id: row}."""
    item = {r["ID"]: r for r in read("Item", build, None, refresh)}
    appearance = {r["ID"]: r for r in read("ItemAppearance", build, None, refresh)}
    best: dict[str, tuple[int, str]] = {}                               # item -> (modifier, appearance id): the base look (modifier 0) first
    for r in read("ItemModifiedAppearance", build, None, refresh):
        key = (int(r["ItemAppearanceModifierID"] or 0), r["ItemAppearanceID"])
        if r["ItemID"] not in best or key < best[r["ItemID"]]:
            best[r["ItemID"]] = key
    out = {}
    for iid, (_mod, app_id) in best.items():
        it = item.get(iid)
        if not it or it["ClassID"] not in ("2", "4"):
            continue
        if int(it["InventoryType"]) not in SLOT_OF_INV:
            continue
        disp = (appearance.get(app_id) or {}).get("ItemDisplayInfoID", "0")
        if disp in ("", "0"):
            continue
        out[iid] = {"item": it, "appearance": app_id, "display": int(disp)}
    return out


def fetch_names(ids: list[str], pause: float) -> None:
    """Name / quality / icon of the items the client table does not name, from Wowhead's tooltip endpoint. Resumable."""
    cache = json.loads(NAMES.read_text(encoding="utf-8")) if NAMES.exists() else {}
    todo = [i for i in ids if i not in cache or "rl" not in cache[i]]      # entries cached before levels were read are fetched again
    print(f"names: {len(cache)} cached, {len(todo)} to fetch (pause {pause}s)")
    failures = 0
    for n, iid in enumerate(todo, 1):
        status, j = http_json(TOOLTIP.format(id=iid, loc=LOCALES["en"]))
        if status == 200 and j and j.get("name"):
            tt = j.get("tooltip") or ""
            rl, il = TT_RLVL.search(tt), TT_ILVL.search(tt)
            cache[iid] = {"en": j["name"], "q": j.get("quality"), "icon": j.get("icon"), "rl": int(rl.group(1)) if rl else 0, "il": int(il.group(1)) if il else 0}
            failures = 0
        elif status in (403, 429):
            print(f"blocked by the server (HTTP {status}) after {n - 1} requests: stopping, run again later")
            break
        else:
            cache[iid] = {"en": None, "q": None, "icon": None, "rl": 0, "il": 0}          # unknown to Wowhead: remembered so it is not asked again
            failures += 1
            if failures >= 2000:
                print("2000 failures in a row: stopping")
                break
        if n % 100 == 0:
            NAMES.write_text(json.dumps(cache, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            print(f"  {n}/{len(todo)}")
        time.sleep(pause)
    NAMES.write_text(json.dumps(cache, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--names", action="store_true", help="fetch the missing names from Wowhead first (slow, resumable)")
    ap.add_argument("--pause", type=float, default=0.3)
    a = ap.parse_args()
    build = a.build or latest_forever_build()
    print("build", build)
    wanted = wanted_items(build, a.refresh)
    print(f"{len(wanted)} items with an appearance")

    sparse = {r["ID"]: r for r in read("ItemSparse", build, None, a.refresh)}
    sparse_fr = {r["ID"]: r["Display_lang"] for r in read("ItemSparse", build, "frFR", a.refresh)}
    icons = {r["ID"]: r["FileName"].rsplit(".", 1)[0].lower() for r in read("ManifestInterfaceData", build, None, a.refresh) if r["FilePath"].lower().startswith("interface\\icons")}
    missing = [i for i in wanted if i not in sparse and not (SOD_RANGE[0] <= int(i) < SOD_RANGE[1])]       # no need to name what is left out anyway
    if a.names:
        fetch_names(missing, a.pause)
    cache = json.loads(NAMES.read_text(encoding="utf-8")) if NAMES.exists() else {}

    rows, unnamed, junk, too_high, sod = [], 0, 0, 0, 0
    for iid, w in sorted(wanted.items(), key=lambda kv: int(kv[0])):
        it, sp, c = w["item"], sparse.get(iid), cache.get(iid)
        if sp:
            en, q, req, ilvl = sp["Display_lang"], int(sp["OverallQualityID"] or 0), int(sp.get("RequiredLevel") or 0), int(sp.get("ItemLevel") or 0)
            icon = icons.get(it["IconFileDataID"])
        elif c and c.get("en"):
            en, q, req, ilvl, icon = c["en"], c.get("q") or 0, c.get("rl") or 0, c.get("il") or 0, c.get("icon") or icons.get(it["IconFileDataID"])
        else:
            unnamed += 1
            continue                                                       # not named yet: left out until `--names` has run
        if SOD_RANGE[0] <= int(iid) < SOD_RANGE[1]:
            sod += 1
            continue
        if req > MAX_LEVEL or ilvl > MAX_ITEM_LEVEL:
            too_high += 1
            continue
        if JUNK.search(en):
            junk += 1
            continue
        rows.append([int(iid), en, sparse_fr.get(iid) or en, q, icon, int(it["InventoryType"]), int(it["ClassID"]), int(it["SubclassID"]), w["display"], int(w["appearance"]), req])
    OUT.write_text(json.dumps({"build": build, "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "cols": COLS, "slots": SLOT_OF_INV,
                               "items": rows}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(rows)} items written to {OUT.name}; {unnamed} still without a name (run with --names); {junk} test / placeholder items, {too_high} items above level {MAX_LEVEL} and {sod} Season of Discovery items left out")


if __name__ == "__main__":
    main()
