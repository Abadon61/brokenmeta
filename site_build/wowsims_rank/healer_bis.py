"""Healing power of each healer spec's Best in Slot set on Wowhead's Forever class guides (bis-gear pages, read 2026-11-28 in the browser),
summed from the WoWSims Forever item database (stat 4 = healing power; items only, no enchantment, talent or buff).
The guides' healing-spell table is computed at this healing power (theoretical HPS, unlimited mana, no crit, no talents).
usage: py healer_bis.py -> data/wow_healer_bis_power.json"""
import json, os
from pathlib import Path

HERE = Path(__file__).parent
PROJECT = HERE.parents[1]
CLONE = Path(os.environ.get("WOWSIMS_DIR", PROJECT.parent / "wowsims-forever"))
# Wowhead's BiS list per spec: the guide's summary table when it has one (one item per slot), else the "BiS" row of each slot section.
# Weapons: either a main hand + off hand or a two-hander; the set with more healing power is kept. Two BiS chests (shaman): the higher one.
BIS = {
    ("paladin", "holy"): {"url": "https://www.wowhead.com/forever/guide/classes/paladin/holy/bis-gear",
                          "items": [260212, 18723, 272855, 272413, 280027, 13969, 273363, 18327, 18386, 13954, 22334, 16058, 272439, 11819, 272436], "weapons": [[276404, 19312]]},
    ("druid", "restoration"): {"url": "https://www.wowhead.com/forever/guide/classes/druid/restoration/bis-gear",
                               "items": [252561, 18723, 226785, 18510, 12462, 13208, 226784, 14553, 226787, 226781, 22334, 272407, 272439, 18470, 272429], "weapons": [[13360, 19312], [812]]},
    ("priest", "holy"): {"url": "https://www.wowhead.com/forever/guide/classes/priest/holy/bis-gear",
                         "items": [260212, 1443, 14139, 18510, 14154, 13958, 12554, 19047, 18386, 13282, 16058, 22334, 272439, 18469, 22254], "weapons": [[13360, 15805]]},
    ("priest", "discipline"): {"url": "https://www.wowhead.com/forever/guide/classes/priest/discipline/bis-gear",
                               "items": [226947, 226951, 18510, 14154, 226949, 226950, 272394, 226946, 226952, 18723, 272407, 16058, 18469, 272439, 22254], "weapons": [[13360, 15805], [812]]},
    ("shaman", "restoration"): {"url": "https://www.wowhead.com/forever/guide/classes/shaman/restoration/bis-gear",
                                "items": [252561, 274222, 18510, 13969, 12554, 14553, 18386, 274217, 18723, 16058, 272439, 249398], "chest": [13346, 15047], "weapons": [[13360, 19312], [812]]},
}

db = json.loads((CLONE / "assets" / "database" / "db.json").read_text(encoding="utf-8"))
I = {i["id"]: i for i in db["items"]}
hp = lambda i: (((I.get(i) or {}).get("scalingOptions") or {}).get("0") or {}).get("stats", {}).get("4", 0)
out, missing = {}, []
for (c, s), b in BIS.items():
    ids = list(b["items"])
    if b.get("chest"):
        ids.append(max(b["chest"], key=hp))
    ids += max(b["weapons"], key=lambda w: sum(hp(x) for x in w))
    missing += [i for i in ids if i not in I]
    out[f"{c}/{s}"] = {"healing_power": sum(hp(i) for i in ids), "items": ids, "n_items": len(ids), "source": b["url"]}
    print(c, s, out[f"{c}/{s}"]["healing_power"], len(ids), "missing:", [i for i in ids if i not in I])
(PROJECT / "data" / "wow_healer_bis_power.json").write_text(json.dumps({"read": "2026-11-28", "specs": out}, indent=1), encoding="utf-8")
