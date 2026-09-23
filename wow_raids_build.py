"""Build the WoW: Forever raid loot pages data (data/wow_raids/raids.json).

Input (nothing is invented):
  - data/wow_wowhead_raw/raid_<zone>.json      loot (drops + quest rewards) and the NPC list of a raid, read from the Wowhead
                                                 Forever zone page, with the items' real Forever stats and icons
  - data/wow_wowhead_raw/raid_<zone>_fr.json   the same NPCs' French names, read from fr.wowhead.com's copy of the same page
  - data/wow_talents_raw/<build>/...           beta client tables: item type labels (SkillLine)

Bosses: a raid boss is an NPC with classification == 3 ("world boss" tier in Wowhead's own data) -- unlike dungeons, where every
named creature (boss or not) is tagged the same as trash, so this signal only exists for raids. A handful of classification-3
entries are not real encounters (a phase-2 "image" add, a zone-wide placeholder) and are excluded by name below since the data
gives no other way to tell them apart; every exclusion is listed so it can be checked against Wowhead directly.

Per-boss loot: an item is attributed to a boss only when that boss's exact name appears in the item's own `sourcemore` data on
Wowhead. Most Molten Core items have no such attribution yet in Wowhead's Forever database -- presumably because the raid, being
level-60 content, has not really been cleared during this low-level beta. Unattributed items are still listed, just without a
named source, rather than guessed at.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

P = Path(__file__).resolve().parent
BUILD = "1.60.1.69913"
RAW = P / "data" / "wow_talents_raw" / BUILD
WH = P / "data" / "wow_wowhead_raw"
OUT = P / "data" / "wow_raids"

RAIDS = {2717: ("molten-core", "Molten Core")}                      # zone id -> (slug, Wowhead's English zone title, for reference)

# classification-3 NPCs that are not a real encounter (checked by hand against each raid's real boss roster)
NOT_A_BOSS = {"Image of Shazzrah", "The Molten Core"}

# Zone-level facts, read by hand from Wowhead's own zone quick-facts box (Forever zone page for level/players/patch/attunement,
# classic zone page for the fixed real-world location, since Forever's own quick-facts box omits it) -- nothing invented.
RAID_INFO = {
    2717: {
        "level": 60, "players": "20/40", "territory": {"en": "Contested", "fr": "Contesté"}, "patch": "1.60.1",
        "location": {"en": "Blackrock Mountain, beneath Blackrock Depths", "fr": "Mont Rochenoire, sous les Profondeurs de Rochenoire"},
        "attunement": {"quest": "Attunement to the Core", "reqlevel": 55, "questid": 7487},
        "screenshots": [5993, 5995, 81144],
    },
}

# Real, canonical encounter order for each raid, read from Wowhead's own zone page boss list -- Forever's classification-3 signal
# does not preserve encounter order, so this fills that gap from the (identical, decades-old) real raid's own documented order.
BOSS_ORDER = {
    2717: ["Lucifron", "Magmadar", "Gehennas", "Garr", "Baron Geddon", "Shazzrah", "Golemagg the Incinerator",
           "Sulfuron Harbinger", "Majordomo Executus", "Ragnaros"],
}

# Per-boss creature type and known abilities, read by hand from each boss's own Wowhead NPC page (Quick Facts "Type:" field and
# the "Abilities" tab, both pulled from the game's own creature data) -- real spell names/ids, not invented mechanics or strategy.
BOSS_INFO = {
    "Lucifron": {"npc": 12118, "type": "Humanoid",
                 "abilities": [(19460, "Shadow Shock"), (19702, "Impending Doom"), (19703, "Lucifron's Curse"), (20604, "Dominate Mind")]},
    "Magmadar": {"npc": 11982, "type": "Beast",
                 "abilities": [(19408, "Panic"), (19411, "Lava Bomb"), (19428, "Conflagration"), (19450, "Magma Spit"), (19451, "Frenzy")]},
    "Gehennas": {"npc": 12259, "type": "Humanoid",
                 "abilities": [(19716, "Gehennas' Curse"), (19717, "Rain of Fire"), (19728, "Shadow Bolt"), (20277, "Fist of Ragnaros")]},
    "Garr": {"npc": 12057, "type": "Elemental",
             "abilities": [(15732, "Immolate"), (19492, "Antimagic Pulse"), (19496, "Magma Shackles"), (19516, "Enrage")]},
    "Baron Geddon": {"npc": 12056, "type": "Elemental",
                     "abilities": [(19659, "Ignite Mana"), (19695, "Inferno"), (20475, "Living Bomb"), (20478, "Armageddon")]},
    "Shazzrah": {"npc": 12264, "type": "Humanoid",
                 "abilities": [(19712, "Arcane Explosion"), (19713, "Shazzrah's Curse"), (19714, "Deaden Magic"), (23138, "Gate of Shazzrah")]},
    "Golemagg the Incinerator": {"npc": 11988, "type": "Giant",
                                  "abilities": [(13880, "Magma Splash"), (19798, "Earthquake"), (20228, "Pyroblast"), (20553, "Golemagg's Trust")]},
    "Sulfuron Harbinger": {"npc": 12098, "type": "Humanoid",
                           "abilities": [(19775, "Dark Mending"), (19776, "Shadow Word: Pain"), (19778, "Demoralizing Shout"),
                                         (19779, "Inspire"), (19780, "Hand of Ragnaros"), (20294, "Immolate")]},
    "Majordomo Executus": {"npc": 12018, "type": "Humanoid",
                           "abilities": [(20534, "Teleport"), (20619, "Magic Reflection"), (20620, "Aegis of Ragnaros"), (21075, "Damage Shield")]},
    "Ragnaros": {"npc": 11502, "type": "Elemental",
                 "abilities": [(19773, "Elemental Fire"), (20565, "Magma Blast"), (19774, "Summon Ragnaros"), (20566, "Wrath of Ragnaros")]},
}

# Official Blizzard localization of the fixed, small set of WoW creature-type labels (not per-raid data).
CREATURE_TYPE_FR = {"Humanoid": "Humanoïde", "Beast": "Bête", "Elemental": "Élémentaire", "Giant": "Géant",
                     "Undead": "Mort-vivant", "Dragonkin": "Dragon", "Demon": "Démon", "Mechanical": "Mécanique", "Critter": "Créature"}

ARMOR_SKILL = {1: 415, 2: 414, 3: 413, 4: 293, 6: 433}
WEAPON_SKILL = {0: 44, 1: 172, 2: 45, 3: 46, 4: 54, 5: 160, 6: 229, 7: 43, 8: 55, 10: 136, 13: 473, 15: 173, 16: 176, 18: 226, 19: 228}
SLOTS = {1: ("Head", "Tête"), 2: ("Neck", "Cou"), 3: ("Shoulders", "Épaules"), 5: ("Chest", "Torse"), 6: ("Waist", "Taille"), 7: ("Legs", "Jambes"),
         8: ("Feet", "Pieds"), 9: ("Wrists", "Poignets"), 10: ("Hands", "Mains"), 11: ("Finger", "Doigt"), 13: ("One-hand", "Une main"), 14: ("Shield", "Bouclier"),
         15: ("Ranged", "Distance"), 16: ("Back", "Dos"), 17: ("Two-hand", "Deux mains"), 20: ("Chest", "Torse"), 21: ("Main hand", "Main droite"),
         22: ("Off hand", "Main gauche"), 23: ("Held in off-hand", "Tenu en main gauche"), 25: ("Thrown", "Armes de jet"), 26: ("Ranged", "Distance")}
SLOT_ORDER = [1, 2, 3, 16, 5, 20, 9, 10, 6, 7, 8, 11, 17, 13, 21, 22, 14, 23, 15, 26, 25]
KEEP_STATS = ["str", "agi", "int", "spi", "sta", "splpwr", "spldmg", "atkpwr", "manargn", "critstrkrtng", "hastertng", "hitrtng", "defrtng", "armor", "dps", "speed",
              "firres", "frores", "natres", "arcres", "shares", "rgddps"]
PRIMARY_STATS = ["str", "agi", "int"]
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

    raids = []
    for zone, (slug, zonename) in RAIDS.items():
        f = WH / f"raid_{zone}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        fr_names = {}
        ffr = WH / f"raid_{zone}_fr.json"
        if ffr.exists():
            fr_names = {i: n for i, n in json.loads(ffr.read_text(encoding="utf-8"))}

        # ---- bosses: classification-3 NPCs, deduplicated by name (Forever reuses some names on a second, newer NPC id),
        # ordered by the raid's real, documented encounter order when known
        boss_names = []
        for n in d["npcs"]:
            if n["classification"] == 3 and n["name"] not in NOT_A_BOSS and n["name"] not in boss_names:
                boss_names.append(n["name"])
        order = BOSS_ORDER.get(zone)
        if order:
            boss_names.sort(key=lambda bn: order.index(bn) if bn in order else 999)
        bosses = []
        for bn in boss_names:
            info = BOSS_INFO.get(bn, {"npc": None, "type": "", "abilities": []})
            bosses.append({
                "name": {"en": bn, "fr": fr_names.get(next(n["id"] for n in d["npcs"] if n["name"] == bn), bn)},
                "npc": info["npc"], "type": {"en": info["type"], "fr": CREATURE_TYPE_FR.get(info["type"], info["type"])},
                "abilities": [{"id": sid, "name": sname} for sid, sname in info["abilities"]],
                "drops": [],
            })

        # ---- items
        items = []
        for it in d["items"]:
            if it["slot"] not in SLOTS or it["c"] not in (2, 4) or it["q"] < 2:
                continue
            st = {k: v for k, v in it["st"].items() if k in KEEP_STATS}
            if not st:
                continue
            row = {"id": it["id"], "name": it["name"], "q": it["q"], "slot": it["slot"], "type": type_label(it), "req": it["req"], "lvl": it["lvl"],
                   "icon": it["icon"], "st": st, "src": it["src"][:3], "kind": it["kind"]}
            items.append(row)
            for b in bosses:
                if b["name"]["en"] in it["src"]:
                    b["drops"].append(row)
        raids.append({"id": slug, "zone": zone, "name": {"en": zonename, "fr": zonename}, "info": RAID_INFO.get(zone, {}),
                      "bosses": bosses, "items": items})

    # French zone display name, from the client's own Map table when available
    maps_en = {r["ID"]: r["MapName_lang"] for r in read_csv("Map.csv")}
    maps_fr = {r["ID"]: r["MapName_lang"] for r in read_csv("Map.frFR.csv")}
    map_id = {v: k for k, v in maps_en.items()}
    for r in raids:
        if r["name"]["en"] in map_id:
            r["name"]["fr"] = maps_fr[map_id[r["name"]["en"]]]

    OUT.mkdir(parents=True, exist_ok=True)
    data = {"build": BUILD, "generated": "2026-09-22", "slots": {str(k): {"en": v[0], "fr": v[1]} for k, v in SLOTS.items()}, "slot_order": SLOT_ORDER,
            "primary_stats": PRIMARY_STATS, "secondary_stats": SECONDARY_STATS, "raids": raids,
            "source": {"label": "Wowhead — Forever zone pages (drops, quest rewards and NPCs)", "url": "https://www.wowhead.com/forever/zones/dungeons"}}
    (OUT / "raids.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(raids), "raids")
    for r in raids:
        attributed = sum(len(b["drops"]) for b in r["bosses"])
        print(f"  {r['name']['fr']:<20} {len(r['items']):>3} items, {len(r['bosses'])} bosses, {attributed} items with a confirmed boss")
        for b in r["bosses"]:
            print(f"    {b['name']['fr']:<28} {len(b['drops'])} confirmed drop(s)")


if __name__ == "__main__":
    main()
