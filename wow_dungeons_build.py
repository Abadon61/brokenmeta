"""Build the WoW: Forever dungeon loot pages data (data/wow_dungeons/dungeons.json).

Inputs (nothing is invented):
  - data/wow_wowhead_raw/dungeon_<zone>.json   loot of a dungeon (drops + quest rewards) read from the Wowhead Forever zone page, with the
                                                 items' real Forever stats (Wowhead's own item data) and icons
  - data/wow_talents_raw/<build>/...            beta client tables: who may equip which armor / weapon type (SkillRaceClassInfo), dungeon names
  - data/wow_guides/content.json                the stat priority of every specialization (Icy Veins, restated)

Importance of an item for a specialization (rule, documented on the pages):
  * the item must be usable by the class (armor / weapon proficiency from the client tables) and give at least one of the
    specialization's four highest-priority stats
  * tier 1 = its best matching stat is priority 1 or 2, tier 2 = priority 3 or 4; inside a tier: better priority, more matching stats,
    higher quality, higher value of the matching stat
  * "item level" entries of a priority list cannot tell items apart, so they are skipped
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

P = Path(__file__).resolve().parent
BUILD = "1.60.1.69913"
RAW = P / "data" / "wow_talents_raw" / BUILD
WH = P / "data" / "wow_wowhead_raw"
OUT = P / "data" / "wow_dungeons"

# zone id -> (client map name, level range shown by Wowhead)
DUNGEONS = {
    2437: ("Ragefire Chasm", "15-25"), 1581: ("Deadmines", "15-25"), 718: ("Wailing Caverns", "17-27"), 209: ("Shadowfang Keep", "22-30"),
    719: ("Blackfathom Deeps", "22-32"), 717: ("Stormwind Stockade", "22-32"), 721: ("Gnomeregan", "26-36"), 796: ("Scarlet Monastery", "26-45"),
    491: ("Razorfen Kraul", "32-42"),
}
SLUG = {2437: "ragefire-chasm", 1581: "deadmines", 718: "wailing-caverns", 209: "shadowfang-keep", 719: "blackfathom-deeps", 717: "stockade",
        721: "gnomeregan", 796: "scarlet-monastery", 491: "razorfen-kraul"}

CLASS_BIT = {"warrior": 1, "paladin": 2, "hunter": 4, "rogue": 8, "priest": 16, "shaman": 64, "mage": 128, "warlock": 256, "druid": 1024}
ARMOR_SKILL = {1: 415, 2: 414, 3: 413, 4: 293, 6: 433}                                    # cloth, leather, mail, plate, shield
WEAPON_SKILL = {0: 44, 1: 172, 2: 45, 3: 46, 4: 54, 5: 160, 6: 229, 7: 43, 8: 55, 10: 136, 13: 473, 15: 173, 16: 176, 18: 226, 19: 228}
SLOTS = {1: ("Head", "Tête"), 2: ("Neck", "Cou"), 3: ("Shoulders", "Épaules"), 5: ("Chest", "Torse"), 6: ("Waist", "Taille"), 7: ("Legs", "Jambes"),
         8: ("Feet", "Pieds"), 9: ("Wrists", "Poignets"), 10: ("Hands", "Mains"), 11: ("Finger", "Doigt"), 13: ("One-hand", "Une main"), 14: ("Shield", "Bouclier"),
         15: ("Ranged", "Distance"), 16: ("Back", "Dos"), 17: ("Two-hand", "Deux mains"), 20: ("Chest", "Torse"), 21: ("Main hand", "Main droite"),
         22: ("Off hand", "Main gauche"), 23: ("Held in off-hand", "Tenu en main gauche"), 25: ("Thrown", "Armes de jet"), 26: ("Ranged", "Distance")}
SLOT_ORDER = [1, 2, 3, 16, 5, 20, 9, 10, 6, 7, 8, 11, 17, 13, 21, 22, 14, 23, 15, 26, 25]

# Icy Veins stat name -> item stat keys (Wowhead item data). None = cannot discriminate items.
STAT_KEYS = {
    "Spell Power": ["splpwr", "spldmg"], "Healing Power": ["splpwr", "splheal"],       # no separate healing stat exists in the data: assumed to follow spell power
    "Hit Chance": ["hitrtng"], "Haste": ["hastertng"], "Critical Strike": ["critstrkrtng"], "Intellect": ["int"], "Spirit": ["spi"], "Stamina": ["sta"],
    "Agility": ["agi"], "Strength": ["str"], "Mp5": ["manargn"], "Expertise": ["exprtng"], "Armor": ["armor"],
    "Weapon Damage": ["dps"], "Ranged Weapon Damage": ["dps"],
    "Item Level / Weapon DPS": None, "Highest item level": None,
}
KEEP_STATS = ["str", "agi", "int", "spi", "sta", "splpwr", "spldmg", "atkpwr", "manargn", "critstrkrtng", "hastertng", "hitrtng", "defrtng", "armor", "dps", "speed",
              "firres", "frores", "natres", "arcres", "shares", "rgddps"]


def read_csv(name):
    with open(RAW / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    # ---- who can use what (client tables)
    skills_en = {r["ID"]: r["DisplayName_lang"] for r in read_csv("SkillLine.csv")}
    fr_file = RAW / "SkillLine.frFR.csv"
    skills_fr = {r["ID"]: r["DisplayName_lang"] for r in csv.DictReader(open(fr_file, encoding="utf-8"))} if fr_file.exists() else skills_en
    rows = read_csv("SkillRaceClassInfo.csv")

    def min_level(class_id: str, skill: int):
        """Lowest player level at which the class may use the skill's items, or None if it never can."""
        bit = CLASS_BIT[class_id]
        lv = [int(r["MinLevel"] or 0) for r in rows if r["SkillID"] == str(skill) and int(r["ClassMask"]) & bit]
        return min(lv) if lv else None

    def usable(class_id: str, it: dict):
        """(can use, level from which)"""
        if it["st"].get("classes") and not (int(it["st"]["classes"]) & CLASS_BIT[class_id]):
            return False, 0
        if it["c"] == 2:
            sk = WEAPON_SKILL.get(it["sc"])
            if sk is None:
                return False, 0
            m = min_level(class_id, sk)
            return (m is not None), (m or 0)
        if it["c"] == 4:
            sk = ARMOR_SKILL.get(it["sc"])
            if sk is None:                                   # rings, necklaces, cloaks, trinkets, held items: anyone
                return True, 0
            m = min_level(class_id, sk)
            return (m is not None), (m or 0)
        return False, 0

    def type_label(it):
        sk = WEAPON_SKILL.get(it["sc"]) if it["c"] == 2 else ARMOR_SKILL.get(it["sc"]) if it["c"] == 4 else None
        if sk:
            return {"en": skills_en.get(str(sk), ""), "fr": skills_fr.get(str(sk), "")}
        return {"en": "", "fr": ""}

    # ---- specializations and their priority
    content = json.loads((P / "data" / "wow_guides" / "content.json").read_text(encoding="utf-8"))
    specs = []
    for f in sorted((P / "data" / "wow_talents").glob("*.json")):
        c = json.loads(f.read_text(encoding="utf-8"))
        for s in c["specs"]:
            ct = content.get(c["id"], {}).get(s["id"])
            if ct:
                specs.append({"key": f"{c['id']}/{s['id']}", "class": c["id"], "spec": s["id"], "name": {"en": f"{s['name']['en']} {c['name']['en']}", "fr": f"{c['name']['fr']} {s['name']['fr']}"},
                              "order": [x["en"] for x in ct["stats"]["order"]]})

    maps_en = {r["ID"]: r["MapName_lang"] for r in read_csv("Map.csv")}
    maps_fr = {r["ID"]: r["MapName_lang"] for r in read_csv("Map.frFR.csv")}
    map_id = {v: k for k, v in maps_en.items()}

    def value(it, stat):
        keys = STAT_KEYS.get(stat)
        if not keys:
            return 0
        if stat in ("Weapon Damage", "Ranged Weapon Damage") and it["c"] != 2:
            return 0
        if stat == "Weapon Damage" and it["slot"] in (15, 25, 26):          # melee damage: not on bows, guns, wands or thrown weapons
            return 0
        if stat == "Ranged Weapon Damage" and it["slot"] not in (15, 25, 26):
            return 0
        if stat == "Armor" and it["c"] != 4:
            return 0
        return sum(it["st"].get(k, 0) for k in keys)

    dungeons = []
    for zone, (mapname, levels) in DUNGEONS.items():
        f = WH / f"dungeon_{zone}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        items = []
        for it in d["items"]:
            if it["slot"] not in SLOTS or it["c"] not in (2, 4) or it["q"] < 2:
                continue
            st = {k: v for k, v in it["st"].items() if k in KEEP_STATS or k == "classes"}
            if not st:
                continue
            row = {"id": it["id"], "name": it["name"], "q": it["q"], "slot": it["slot"], "type": type_label(it), "req": it["req"], "lvl": it["lvl"], "icon": it["icon"],
                   "st": {k: v for k, v in st.items() if k != "classes"}, "src": it["src"][:3], "kind": it["kind"], "rel": {}}
            for sp in specs:
                ok, from_lvl = usable(sp["class"], {**it, "st": st})
                if not ok:
                    continue
                best = None
                matched = []
                prio = [s_ for s_ in sp["order"] if STAT_KEYS.get(s_)]           # skip the "item level" entries
                for idx, name in enumerate(prio[:4]):
                    v = value({**it, "st": st}, name)
                    if v > 0:
                        matched.append((idx, name, v))
                if not matched:
                    continue
                idx0, name0, v0 = matched[0]
                tier = 1 if idx0 <= 1 else 2
                row["rel"][sp["key"]] = [tier, idx0, -len(matched), -it["q"], -round(v0, 2), from_lvl, name0]
            items.append(row)
        # rank inside each spec: order the keys so the page can sort; keep compact
        dungeons.append({"id": SLUG[zone], "zone": zone, "name": {"en": maps_en[map_id[mapname]], "fr": maps_fr[map_id[mapname]]}, "levels": levels, "items": items})
    OUT.mkdir(parents=True, exist_ok=True)
    data = {"build": BUILD, "generated": "2026-09-22", "slots": {str(k): {"en": v[0], "fr": v[1]} for k, v in SLOTS.items()}, "slot_order": SLOT_ORDER,
            "specs": [{k: v for k, v in s.items() if k != "order"} | {"priority": s["order"]} for s in specs], "dungeons": dungeons,
            "assumptions": ["Healing Power is matched with spell power: no separate healing stat exists in the item data."],
            "source": {"label": "Wowhead — Forever zone pages (drops and quest rewards)", "url": "https://www.wowhead.com/forever/zones/dungeons"}}
    (OUT / "dungeons.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(dungeons), "dungeons,", sum(len(d["items"]) for d in dungeons), "equippable items with stats;", len(specs), "specs")
    for d in dungeons:
        rel = sum(1 for i in d["items"] if i["rel"])
        print(f"  {d['name']['fr']:<28} {d['levels']:<6} {len(d['items']):>3} items, {rel} relevant to at least one spec")


if __name__ == "__main__":
    main()
