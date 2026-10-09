"""Crafted equipment (Leatherworking, Blacksmithing, Tailoring, Engineering, Enchanting) for the simulator's item pool and the guides.

Inputs (nothing is invented):
  - data/wow_professions/<profession>.json   the recipes (skill needed, what they make, French names)
  - data/wow_wowhead_raw/crafted_candidates.json   the made items of those recipes up to the skill cap (written by this script's first run, see `candidates()`)
  - data/wow_wowhead_raw/crafted_chunk*.json   the items' real Forever stats read from their Wowhead Forever pages: [id, quality, required level, slot, stats]
  - the beta client table `Item` (wago.tools)  armor class / weapon class of each item

Writes data/wow_crafted/items.json in the shape of the dungeon / raid items, plus the profession and skill needed.

    py -3.11 wow_crafted_build.py
"""
import json
import re
from pathlib import Path

import wow_talents_import as imp

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "wow_wowhead_raw"
OUT = ROOT / "data" / "wow_crafted"
PROFS = ["leatherworking", "blacksmithing", "tailoring", "engineering", "enchanting"]
SKIP_NAME = re.compile(r"^Enchant |Kit$|Scope|Stone$|Bolt of|Bar$|Ingot|Potion|Elixir|Oil|Flask|Bandage|Bomb|Shot|Arrow|Cog|Gizmo|Rod|Dust|Essence|Mote|Mask|Dye|Pattern|Leather$|Scale$|Bag$|Pouch|Quiver|Ammo|Torch|Repeater|Charge|Dynamite|Grenade|Goblin Land|Wormhole|Teleport|Trap|Spark|Fuse|Pylon|Flare|Target|Dummy|Rocket Fuel|Mining Pick|Skinning Knife|Rune", re.I)
KEEP = ["str", "agi", "int", "spi", "sta", "splpwr", "spldmg", "atkpwr", "manargn", "critstrkrtng", "hastertng", "hitrtng", "defrtng", "armor", "dps", "speed", "firres", "frores", "natres", "arcres", "shares"]
ARMOR_TYPE = {1: "Cloth", 2: "Leather", 3: "Mail", 4: "Plate Mail", 6: "Shield"}
ARMOR_FR = {"Cloth": "Tissu", "Leather": "Cuir", "Mail": "Mailles", "Plate Mail": "Plaques", "Shield": "Bouclier"}
WEAPON_TYPE = {0: "Axes", 1: "Two-Handed Axes", 2: "Bows", 3: "Guns", 4: "Maces", 5: "Two-Handed Maces", 6: "Polearms", 7: "Swords", 8: "Two-Handed Swords", 10: "Staves",
               13: "Fist Weapons", 15: "Daggers", 18: "Crossbows", 19: "Wands"}
SLOT_OK = {1, 3, 5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 20, 21, 22, 23, 26}              # no shirts, bags, tabards, thrown


def candidates():
    """The items the recipes make (skill 200 up to the cap), without the obvious consumables / reagents."""
    out, seen = [], set()
    for prof in PROFS:
        data = json.loads((ROOT / "data" / "wow_professions" / f"{prof}.json").read_text(encoding="utf-8"))
        for r in data["recipes"]:
            c = r.get("creates")
            if not c or r["learn_at"] < 200 or r["learn_at"] > (data.get("cap") or 300) or SKIP_NAME.search(c["name"]["en"]) or c["id"] in seen:
                continue
            seen.add(c["id"])
            out.append({"id": c["id"], "name": c["name"], "icon": c.get("icon"), "prof": prof, "skill": r["learn_at"], "recipe": r["id"], "recipe_name": r["name"]})
    return out


def main():
    cands = candidates()
    (RAW / "crafted_candidates.json").write_text(json.dumps(cands, ensure_ascii=False), encoding="utf-8")
    stats = {}
    for f in sorted(RAW.glob("crafted_chunk*.json")):
        for iid, q, req, slot, st in json.loads(f.read_text(encoding="utf-8")):
            stats[iid] = (q, req, slot, st)
    build = imp.latest_beta_build()
    item_tab = {r["ID"]: r for r in imp.read(imp.fetch("Item", build, None, False))}
    items, missing = [], 0
    for c in cands:
        s = stats.get(c["id"])
        if not s:
            missing += 1
            continue
        q, req, slot, st = s
        row = item_tab.get(str(c["id"]))
        if not row or slot not in SLOT_OK or req > 60:
            continue
        cls, sub = int(row["ClassID"]), int(row["SubclassID"])
        if cls == 4:
            typ = ARMOR_TYPE.get(sub, "")
        elif cls == 2:
            typ = WEAPON_TYPE.get(sub, "")
            if not typ:
                continue
        else:
            continue
        keep = {k: v for k, v in st.items() if k in KEEP}
        if not keep:
            continue
        items.append({"id": c["id"], "name": c["name"], "q": q, "slot": slot, "type": {"en": typ, "fr": ARMOR_FR.get(typ, typ)}, "req": req, "icon": c.get("icon"), "st": keep,
                      "prof": c["prof"], "skill": c["skill"], "recipe": c["recipe"], "recipe_name": c["recipe_name"]})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "items.json").write_text(json.dumps({"build": build, "items": items}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    by = {}
    for i in items:
        by[i["prof"]] = by.get(i["prof"], 0) + 1
    print(f"{len(items)} crafted items ({by}); {missing} candidates without stats yet")


if __name__ == "__main__":
    main()
