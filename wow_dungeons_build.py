"""Build the WoW: Forever dungeon loot pages data (data/wow_dungeons/dungeons.json).

Input (nothing is invented):
  - data/wow_wowhead_raw/dungeon_<zone>.json   loot of a dungeon (drops + quest rewards) read from the Wowhead Forever zone page, with the
                                                 items' real Forever stats (Wowhead's own item data) and icons
  - data/wow_talents_raw/<build>/...            beta client tables: item type labels (SkillLine), dungeon names (Map)

This page does NOT rank items by class or specialization: an earlier version tried to (matching a spec's stat-priority order,
armor-type preference, level thresholds) and kept surfacing new edge cases a rule-based system cannot fully capture (item sets,
trinket effects, weapon speed, real stat weights, a level-20 priority list applied to level-60 gear...). Recommending a precise
ranking would be false precision. Instead the page is a plain filter: item type (armor/weapon), primary stat (Strength/Agility/
Intellect), and a checklist of secondary stats -- the player, who knows their own class and spec, picks what they need.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

P = Path(__file__).resolve().parent
BUILD = "1.60.1.69913"
RAW = P / "data" / "wow_talents_raw" / BUILD
WH = P / "data" / "wow_wowhead_raw"
OUT = P / "data" / "wow_dungeons"

# zone id -> (client map name, level range shown by Wowhead; "" = no range listed, e.g. a Forever-specific zone)
DUNGEONS = {
    2437: ("Ragefire Chasm", "15-25"), 1581: ("Deadmines", "15-25"), 718: ("Wailing Caverns", "17-27"), 209: ("Shadowfang Keep", "22-30"),
    719: ("Blackfathom Deeps", "22-32"), 717: ("Stormwind Stockade", "22-32"), 721: ("Gnomeregan", "26-36"), 796: ("Scarlet Monastery", "26-45"),
    491: ("Razorfen Kraul", "32-42"), 722: ("Razorfen Downs", "37-47"), 1337: ("Uldaman", "42-52"), 1176: ("Zul'Farrak", "46-56"),
    2100: ("Maraudon", "42-52"), 1477: ("Sunken Temple", "50-60"), 1584: ("Blackrock Depths", "52-60"), 2557: ("Dire Maul", "44-54"),
    2017: ("Stratholme", "48-58"), 2057: ("Scholomance", "55-60"), 16611: ("Ruins of Lordaeron", ""), 16919: ("The Hall of Thanes", ""),
}
SLUG = {2437: "ragefire-chasm", 1581: "deadmines", 718: "wailing-caverns", 209: "shadowfang-keep", 719: "blackfathom-deeps", 717: "stockade",
        721: "gnomeregan", 796: "scarlet-monastery", 491: "razorfen-kraul", 722: "razorfen-downs", 1337: "uldaman", 1176: "zulfarrak",
        2100: "maraudon", 1477: "sunken-temple", 1584: "blackrock-depths", 2557: "dire-maul", 2017: "stratholme", 2057: "scholomance",
        16611: "ruins-of-lordaeron", 16919: "hall-of-thanes"}

ARMOR_SKILL = {1: 415, 2: 414, 3: 413, 4: 293, 6: 433}                                    # cloth, leather, mail, plate, shield
WEAPON_SKILL = {0: 44, 1: 172, 2: 45, 3: 46, 4: 54, 5: 160, 6: 229, 7: 43, 8: 55, 10: 136, 13: 473, 15: 173, 16: 176, 18: 226, 19: 228}
SLOTS = {1: ("Head", "Tête"), 2: ("Neck", "Cou"), 3: ("Shoulders", "Épaules"), 5: ("Chest", "Torse"), 6: ("Waist", "Taille"), 7: ("Legs", "Jambes"),
         8: ("Feet", "Pieds"), 9: ("Wrists", "Poignets"), 10: ("Hands", "Mains"), 11: ("Finger", "Doigt"), 13: ("One-hand", "Une main"), 14: ("Shield", "Bouclier"),
         15: ("Ranged", "Distance"), 16: ("Back", "Dos"), 17: ("Two-hand", "Deux mains"), 20: ("Chest", "Torse"), 21: ("Main hand", "Main droite"),
         22: ("Off hand", "Main gauche"), 23: ("Held in off-hand", "Tenu en main gauche"), 25: ("Thrown", "Armes de jet"), 26: ("Ranged", "Distance")}
SLOT_ORDER = [1, 2, 3, 16, 5, 20, 9, 10, 6, 7, 8, 11, 17, 13, 21, 22, 14, 23, 15, 26, 25]

# numeric fields kept per item (everything else Wowhead's item data carries is dropped)
KEEP_STATS = ["str", "agi", "int", "spi", "sta", "splpwr", "spldmg", "atkpwr", "manargn", "critstrkrtng", "hastertng", "hitrtng", "defrtng", "armor", "dps", "speed",
              "firres", "frores", "natres", "arcres", "shares", "rgddps"]
PRIMARY_STATS = ["str", "agi", "int"]                                                     # Strength / Agility / Intellect: the filter's "primary stat"
SECONDARY_STATS = ["sta", "spi", "armor", "critstrkrtng", "hastertng", "hitrtng", "defrtng", "manargn", "atkpwr", "splpwr", "spldmg"]


def read_csv(name):
    with open(RAW / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    skills_en = {r["ID"]: r["DisplayName_lang"] for r in read_csv("SkillLine.csv")}
    fr_file = RAW / "SkillLine.frFR.csv"
    skills_fr = {r["ID"]: r["DisplayName_lang"] for r in csv.DictReader(open(fr_file, encoding="utf-8"))} if fr_file.exists() else skills_en

    def type_label(it):
        sk = WEAPON_SKILL.get(it["sc"]) if it["c"] == 2 else ARMOR_SKILL.get(it["sc"]) if it["c"] == 4 else None
        if sk:
            return {"en": skills_en.get(str(sk), ""), "fr": skills_fr.get(str(sk), "")}
        return {"en": "", "fr": ""}

    maps_en = {r["ID"]: r["MapName_lang"] for r in read_csv("Map.csv")}
    maps_fr = {r["ID"]: r["MapName_lang"] for r in read_csv("Map.frFR.csv")}
    map_id = {v: k for k, v in maps_en.items()}

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
            st = {k: v for k, v in it["st"].items() if k in KEEP_STATS}
            if not st:
                continue
            items.append({"id": it["id"], "name": it["name"], "q": it["q"], "slot": it["slot"], "type": type_label(it), "req": it["req"], "lvl": it["lvl"],
                           "icon": it["icon"], "st": st, "src": it["src"][:3], "kind": it["kind"]})
        dungeons.append({"id": SLUG[zone], "zone": zone, "name": {"en": maps_en[map_id[mapname]], "fr": maps_fr[map_id[mapname]]}, "levels": levels, "items": items})
    OUT.mkdir(parents=True, exist_ok=True)
    data = {"build": BUILD, "generated": "2026-09-23", "slots": {str(k): {"en": v[0], "fr": v[1]} for k, v in SLOTS.items()}, "slot_order": SLOT_ORDER,
            "primary_stats": PRIMARY_STATS, "secondary_stats": SECONDARY_STATS, "dungeons": dungeons,
            "source": {"label": "Wowhead — Forever zone pages (drops and quest rewards)", "url": "https://www.wowhead.com/forever/zones/dungeons"}}
    (OUT / "dungeons.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(dungeons), "dungeons,", sum(len(d["items"]) for d in dungeons), "equippable items with stats")
    for dgn in dungeons:
        print(f"  {dgn['name']['fr']:<28} {dgn['levels']:<6} {len(dgn['items']):>3} items")


if __name__ == "__main__":
    main()
