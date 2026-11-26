"""Detail of the ranked WoWSims build of each spec, for the spec's page on the site (/wow-forever/classement/<slug>/) and the
guide's gear table: talents (mapped onto our talent trees), gear with enchantments and where each item comes from, race,
professions, consumables, raid buffs and boss debuffs (all as the WoWSims preset sets them), the character sheet the engine
computes (computeStats) and the damage by ability, auras and pets from a run of the engine (github.com/wowsims/forever, MIT).

Nothing is chosen here: the build is the preset WoWSims publishes (requests/page_*.json, best preset per spec from
data/wow_ranking_wowsims_by_spec.json). usage: py details.py [--iterations 5000]   -> data/wow_ranking_wowsims_detail.json"""
import argparse, json, os, subprocess, tempfile
from pathlib import Path

HERE = Path(__file__).parent
PROJECT = HERE.parents[1]
CLONE = Path(os.environ.get("WOWSIMS_DIR", PROJECT.parent / "wowsims-forever"))
CLI = CLONE / "bin" / ("wowsimcli.exe" if os.name == "nt" else "wowsimcli")
WASM = CLONE / "dist_bm" / "lib_db.wasm"
EXEC = PROJECT / "site_build" / "wowsims_web" / "wasm_exec.js"

ap = argparse.ArgumentParser()
ap.add_argument("--iterations", type=int, default=5000)
a = ap.parse_args()

SLOTS = ["head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet", "ring1", "ring2", "trinket1", "trinket2", "mh", "oh", "rng"]
PROF = {1: "alchemy", 2: "blacksmithing", 3: "enchanting", 4: "engineering", 5: "herbalism", 8: "leatherworking", 9: "mining", 10: "skinning", 11: "tailoring"}
PROF_NAME = {"Alchemy": ("Alchimie", "Alchemy"), "Blacksmithing": ("Forge", "Blacksmithing"), "Enchanting": ("Enchantement", "Enchanting"),
             "Engineering": ("Ingénierie", "Engineering"), "Herbalism": ("Herboristerie", "Herbalism"), "Leatherworking": ("Travail du cuir", "Leatherworking"),
             "Mining": ("Minage", "Mining"), "Skinning": ("Dépeçage", "Skinning"), "Tailoring": ("Couture", "Tailoring")}
CLASS_ID = {"ClassWarrior": "warrior", "ClassRogue": "rogue", "ClassHunter": "hunter", "ClassMage": "mage", "ClassWarlock": "warlock",
            "ClassShaman": "shaman", "ClassDruid": "druid", "ClassPriest": "priest", "ClassPaladin": "paladin"}
# raid / party / player buffs and boss debuffs of the presets: proto field -> (our setup id for the French name, spell id, English name)
BUFFS = {
    "arcaneIntellect": ("arcane_intellect", 23028, "Arcane Brilliance (Mage)"), "battleShout": ("battle_shout", 25289, "Battle Shout (Warrior)"),
    "graceOfAirTotem": ("grace_of_air", 25359, "Grace of Air Totem (Shaman)"), "leaderOfThePack": ("leader_of_the_pack", 24932, "Leader of the Pack (Feral Druid)"),
    "markOfTheWild": ("mark_of_the_wild", 21850, "Gift of the Wild (Druid)"), "moonkinAura": ("moonkin_aura", 24907, "Moonkin Aura (Balance Druid)"),
    "powerWordFortitude": ("power_word_fortitude", 21564, "Prayer of Fortitude (Priest)"), "prayerOfSpirit": ("divine_spirit", 27681, "Prayer of Spirit (Priest)"),
    "strengthOfEarthTotem": ("strength_of_earth", 25361, "Strength of Earth Totem (Shaman)"), "windfuryTotem": ("windfury_totem", 10614, "Windfury Totem (Shaman)"),
    "greaterBlessingOfKings": ("blessing_of_kings", 25898, "Greater Blessing of Kings (Paladin)"), "greaterBlessingOfMight": ("blessing_of_might", 25916, "Greater Blessing of Might (Paladin)"),
    "greaterBlessingOfWisdom": ("blessing_of_wisdom", 25918, "Greater Blessing of Wisdom (Paladin)"), "innervates": ("innervate", 29166, "Innervate (Druid)"),
    "manaSpringTotem": ("mana_spring_totem", 10497, "Mana Spring Totem (Shaman)"), "manaTideTotems": ("mana_tide_totem", 17359, "Mana Tide Totem (Shaman)"),
    "darkInspiration": ("dark_inspiration", None, "Dark Inspiration"),
}
DEBUFFS = {
    "curseOfElements": ("curse_of_elements", 11722, "Curse of the Elements"), "curseOfRecklessness": ("curse_of_recklessness", 11717, "Curse of Recklessness"),
    "curseOfWeakness": ("curse_of_weakness", 11708, "Curse of Weakness"), "exposeArmor": ("expose_armor", 11198, "Expose Armor"), "faerieFire": ("faerie_fire", 9907, "Faerie Fire"),
    "giftOfArthas": ("gift_of_arthas", 11374, "Gift of Arthas"), "huntersMark": ("hunters_mark", 14325, "Hunter's Mark"), "insectSwarm": ("insect_swarm", 24977, "Insect Swarm"),
    "judgementOfLight": ("judgement_of_light", 20346, "Judgement of Light"), "judgementOfTheCrusader": ("judgement_of_the_crusader", 20303, "Judgement of the Crusader"),
    "judgementOfWisdom": ("judgement_of_wisdom", 20355, "Judgement of Wisdom"), "sunderArmor": ("sunder_armor_5", 11597, "Sunder Armor x5"), "vindication": ("vindication", 26021, "Vindication"),
}
CONS = [("flaskId", "flask"), ("elixirIds", "elixir"), ("foodId", "food"), ("mhImbueId", "imbue_mh"), ("ohImbueId", "imbue_oh"), ("mhWeaponImbueId", "imbue_mh"),
        ("ohWeaponImbueId", "imbue_oh"), ("offensivePotId", "potion"), ("resourcePotId", "potion"), ("conjuredId", "conjured"), ("explosiveId", "explosive"), ("extraIds", "extra")]

db = json.loads((CLONE / "assets" / "database" / "db.json").read_text(encoding="utf-8"))
ITEMS = {i["id"]: i for i in db["items"]}
ENCH = {}
for _e in db["enchants"]:
    ENCH.setdefault(_e["effectId"], []).append(_e)
SLOT_TYPE = {"head": 1, "neck": 2, "shoulder": 3, "back": 4, "chest": 5, "wrist": 6, "hands": 7, "waist": 8, "legs": 9, "feet": 10, "ring1": 11, "ring2": 11, "mh": 13, "oh": 13, "rng": 14}
CONSUMABLES = {c["id"]: c for c in db["consumables"]}
SPELL = {s["id"]: s for s in db["spellIcons"]}
ZONES = {z["id"]: z["name"] for z in db["zones"]}
NPCS = {n["id"]: n for n in db["npcs"]}
TREES = {c: json.loads((CLONE / "ui" / "sim" / "talents" / "trees" / f"{CLASS_ID[c]}.json").read_text(encoding="utf-8")) for c in CLASS_ID}
OUR = {c: json.loads((PROJECT / "data" / "wow_talents" / f"{CLASS_ID[c]}.json").read_text(encoding="utf-8")) for c in CLASS_ID}
OUR_ENCH = {e["id"]: e for e in json.loads((PROJECT / "site_build" / "sim60" / "data" / "enchants60.json").read_text(encoding="utf-8"))["enchants"]}
FR_SPELL = {}           # English spell name -> French, from our class glossaries and talent trees
for gp in (PROJECT / "data" / "wow_spells").glob("*.json"):
    for ab in json.loads(gp.read_text(encoding="utf-8")).get("abilities", []):
        nm = ab.get("name") or {}
        if nm.get("en") and nm.get("fr"):
            FR_SPELL.setdefault(nm["en"], nm["fr"])
for cls in OUR.values():
    for sp in cls["specs"]:
        for t in sp["talents"]:
            FR_SPELL.setdefault(t["name"]["en"], t["name"]["fr"])


# French names read from Wowhead's Forever tooltips (spell and item ids of these builds, locale fr), see wh_fr_names_2026-11-26.json
_WHFR = json.loads((HERE / "wh_fr_names_2026-11-26.json").read_text(encoding="utf-8"))
FR_BY_SPELL = {int(k): v for k, v in _WHFR["spell"].items() if not v.startswith("[")}      # "[Name]" = no French text on Wowhead yet
FR_BY_ITEM = {int(k): v for k, v in _WHFR["item"].items() if not v.startswith("[")}
FR_SPELL.update({"Imp": "Diablotin", "Succubus": "Succube", "Hawk 1": "Faucon 1", "Hawk 2": "Faucon 2", "Raptor": "Raptor (familier)", "Corruption": "Corruption", "Rupture": "Rupture",
                 "Auto attack (main hand)": "Attaque auto (main droite)", "Auto attack (off hand)": "Attaque auto (main gauche)", "Auto attack": "Attaque auto",
                 "Auto Shot": "Tir automatique", "Extra attacks": "Attaques supplémentaires"})


def talents(cls, s):
    """WoWSims talent string (one digit per talent of each tree, in their tree order) -> the three trees with the build's points.
    The trees are WoWSims' own (ui/sim/talents/trees), checked identical to Wowhead's Forever talent calculator on 2026-11-26
    (our data/wow_talents comes from an older client build and differs: Flurry 3 ranks, Reckless Swings, Improved Whirlwind...).
    French names come from our trees when the talent kept its English name; descriptions are left to the Wowhead tooltip."""
    trees, digits3 = [], (s.split("-") + ["", "", ""])[:3]
    our = OUR[cls]
    for ti, digits in enumerate(digits3):
        wt = TREES[cls][ti]
        sp = our["specs"][ti]
        fr = {t["name"]["en"].lower(): t["name"]["fr"] for t in sp["talents"]}
        cells = []
        for k, w in enumerate(wt["talents"]):
            pts = int(digits[k]) if k < len(digits) else 0
            ic = (SPELL.get(w["spellId"]) or {}).get("icon")
            pre = w.get("prereqLocation")
            cells.append({"name": {"en": w["fancyName"], "fr": FR_BY_SPELL.get(w["spellId"]) or fr.get(w["fancyName"].lower(), w["fancyName"])}, "sid": w["spellId"], "icon": ic,
                          "row": w["location"]["rowIdx"], "col": w["location"]["colIdx"], "max": w["maxPoints"], "points": pts,
                          "pre": [pre["rowIdx"], pre["colIdx"]] if pre else None})
        trees.append({"id": sp["id"], "name": sp["name"], "points": sum(c["points"] for c in cells), "cells": cells})
    return trees


def source(it):
    """Where an item comes from, from the WoWSims database: dungeon + boss, profession, vendor, quest, reputation or PvP."""
    for s in it.get("sources") or []:
        if "drop" in s:
            d = s["drop"]
            npc = NPCS.get(d.get("npcId"), {})
            return {"from": "drop", "zone": ZONES.get(d.get("zoneId") or npc.get("zoneId"), ""), "src": npc.get("name", d.get("otherName", ""))}
        if "crafted" in s:
            return {"from": "craft", "zone": PROF.get(s["crafted"].get("profession"), ""), "src": "", "spell": s["crafted"].get("spellId")}
        if "quest" in s:
            return {"from": "quest", "zone": ZONES.get(s["quest"].get("zoneId"), ""), "src": s["quest"].get("name", ""), "quest": s["quest"].get("id")}
        if "soldBy" in s:
            v = s["soldBy"]
            return {"from": "vendor", "zone": ZONES.get(v.get("zoneId"), ""), "src": v.get("npcName", "")}
        if "rep" in s:
            return {"from": "rep", "zone": "", "src": ""}
        if "pvp" in s:
            return {"from": "pvp", "zone": "", "src": ""}
    return {"from": "", "zone": "", "src": ""}


STAT_KEYS = {0: "str", 1: "agi", 2: "sta", 3: "int", 13: "spi", 14: "ap", 5: "sp", 4: "heal", 17: "hit_r", 18: "crit_r", 19: "haste_r", 27: "armor", 31: "mp5"}


def stat_dict(arr):
    return {k: arr[i] for i, k in STAT_KEYS.items() if i < len(arr) and arr[i]}


def enchant(eid, slot):
    """An enchant id is shared by several slots (Strength +5 on a bracer or, in Forever, a necklace): the slot picks the record."""
    cands = ENCH.get(eid) or []
    if not cands:
        return None
    t = SLOT_TYPE.get(slot)
    e = next((c for c in cands if c.get("type") == t or t in (c.get("extraTypes") or [])), None) or (next((c for c in cands if c.get("type") == 2), None) if slot == "oh" else None) or cands[0]
    ours = OUR_ENCH.get(e.get("spellId"))
    # an enchant's spell is named after its effect only ("Force"): our enchant table first, then the scroll / arcanum item
    it_fr = (FR_BY_ITEM.get(e.get("itemId")) or "").replace("Formule : ", "").replace("Formule : ", "")
    fr = (ours["name"]["fr"] if ours else None) or (it_fr if it_fr and not it_fr.startswith(("Manuscrit", "Patron", "Plans", "Schéma")) else None) or e["name"]
    st = stat_dict(e.get("stats") or [])
    return {"id": e.get("spellId") or e.get("itemId"), "item": e.get("itemId"), "kind": "enchant", "name": {"en": e["name"], "fr": fr},
            "stats": {k: v for k, v in st.items() if k in ("str", "agi", "sta", "int", "spi", "ap", "sp")}, "effect": ours.get("effect") if ours else ""}


def consumable(cid):
    c = CONSUMABLES.get(cid) or ITEMS.get(cid)
    if not c:
        return None
    return {"id": cid, "name": {"en": c["name"], "fr": FR_BY_ITEM.get(cid, c["name"])}}


import re as _re
# every spell of the engine's spell table (its names for procs the UI database has no icon for: Instant Poison VI, Dragonbreath Chili...)
SPELLDATA = {int(m.group(1)): m.group(2) for m in _re.finditer(r'\{ID: (\d+), Name: "([^"]+)"', (CLONE / "sim" / "core" / "spelldata" / "spells_auto_gen.go").read_text(encoding="utf-8"))}
_DUMPS = {}


def proc_owner(sid, gear_ids, enchant_ids):
    """Item or enchantment of the build whose database record names this proc spell (Heart of Wyrmthalak -> 27655)."""
    for kind, ids, table in (("item", gear_ids, ITEMS), ("enchant", enchant_ids, None)):
        for i in ids:
            rec = ITEMS.get(i) if table else next((e for e in ENCH.get(i, [])), None)
            if not rec:
                continue
            k = (kind, i)
            if k not in _DUMPS:
                _DUMPS[k] = json.dumps(rec)
            if f": {sid}" in _DUMPS[k] or f"[{sid}" in _DUMPS[k] or f" {sid}," in _DUMPS[k] or f" {sid}]" in _DUMPS[k]:
                return rec["name"]
    return None


GEAR_CTX = {"items": [], "enchants": []}


def name_of(aid):
    if "spellId" in aid:
        s = SPELL.get(aid["spellId"])
        if s:
            return s["name"]
        owner = proc_owner(aid["spellId"], GEAR_CTX["items"], GEAR_CTX["enchants"])
        return owner or SPELLDATA.get(aid["spellId"]) or f"#{aid['spellId']}"
    if "itemId" in aid:
        i = ITEMS.get(aid["itemId"]) or CONSUMABLES.get(aid["itemId"])
        return i["name"] if i else f"#{aid['itemId']}"
    return aid.get("otherId", "?")


best = {r["spec"]: r for r in json.loads((PROJECT / "data" / "wow_ranking_wowsims_by_spec.json").read_text(encoding="utf-8"))["specs"]}
reqs = {}
for page in sorted((HERE / "requests").glob("page_*.json")):
    for label, req in json.loads(page.read_text(encoding="utf-8")).items():
        reqs[label] = req

# character sheets, all presets in one Node run of the engine
tmp = Path(tempfile.mkdtemp())
(tmp / "in.json").write_text(json.dumps({best[s]["label"]: reqs[best[s]["label"]] for s in best}), encoding="utf-8")
subprocess.run(["node", str(HERE / "stats.mjs"), str(EXEC), str(WASM), str(tmp / "in.json"), str(tmp / "st.json")], check=True, capture_output=True)
SHEETS = json.loads((tmp / "st.json").read_text(encoding="utf-8"))

out = {}
for spec, b in best.items():
    req = json.loads(json.dumps(reqs[b["label"]]))
    meta = req.pop("_bm", {})
    req.pop("requestId", None)
    req["simOptions"] = {"iterations": a.iterations, "randomSeed": "101"}
    (tmp / "r.json").write_text(json.dumps(req), encoding="utf-8")
    res = json.loads(subprocess.run([str(CLI), "sim", "--infile", str(tmp / "r.json")], capture_output=True, text=True, cwd=CLONE).stdout)
    pm = res["raidMetrics"]["parties"][0]["players"][0]
    p = req["raid"]["parties"][0]["players"][0]
    GEAR_CTX["items"] = [i.get("id") for i in p["equipment"]["items"] if i.get("id")]
    GEAR_CTX["enchants"] = [i.get("enchant") for i in p["equipment"]["items"] if i.get("enchant")]
    n = a.iterations
    dur = req["encounter"]["duration"]
    total_dps = pm["dps"]["avg"]
    # damage by ability: merged over tags except the auto attacks (main hand / off hand / ranged)
    rows = {}
    for act in pm.get("actions") or []:
        tg = act.get("targets") or []
        dmg = sum(t.get("damage", 0) for t in tg)
        if dmg <= 0:
            continue
        aid = act["id"]
        if aid.get("itemId") in (12662, 20520):          # Demonic / Dark Rune: the damage is the player's own health, not the boss's
            continue
        key = (aid.get("spellId"), aid.get("itemId"), aid.get("otherId"), aid.get("tag") if aid.get("otherId") == "OtherActionAttack" or aid.get("spellId") in (75,) else 0)
        r = rows.setdefault(key, {"id": aid, "dmg": 0, "casts": 0, "hits": 0, "crits": 0, "melee": act.get("isMelee", False)})
        r["dmg"] += dmg
        r["casts"] += sum(t.get("casts", 0) for t in tg)
        r["hits"] += sum(t.get("hits", 0) + t.get("ticks", 0) + t.get("crits", 0) + t.get("critTicks", 0) + t.get("glances", 0) + t.get("blocks", 0) for t in tg)
        r["crits"] += sum(t.get("crits", 0) + t.get("critTicks", 0) for t in tg)
    for pet in pm.get("pets") or []:
        dmg = sum(t.get("damage", 0) for act in pet.get("actions") or [] for t in act.get("targets") or [])
        if dmg > 0:
            rows[("pet", pet["name"])] = {"id": {"pet": pet["name"]}, "dmg": dmg, "casts": 0, "hits": 0, "crits": 0, "melee": False}
    tot = sum(r["dmg"] for r in rows.values()) or 1
    abilities = []
    for r in sorted(rows.values(), key=lambda r: -r["dmg"]):
        aid = r["id"]
        if "pet" in aid:
            en = aid["pet"]
            kind = "pet"
        elif aid.get("otherId") == "OtherActionAttack":
            tg = aid.get("tag")
            en = {14: "Auto attack (main hand)", 15: "Auto attack (off hand)", 16: "Auto Shot"}.get(tg) or ((SPELL.get(tg) or {}).get("name") or "Extra attacks")
            kind = "auto"
        elif aid.get("otherId") == "OtherActionShoot":
            en, kind = "Auto Shot", "auto"
        else:
            en, kind = name_of(aid), ("item" if "itemId" in aid else "spell")
        abilities.append({"name": {"en": en, "fr": FR_BY_SPELL.get(aid.get("spellId")) or FR_BY_ITEM.get(aid.get("itemId")) or FR_SPELL.get(en, en)}, "kind": kind, "sid": aid.get("spellId"), "iid": aid.get("itemId"),
                          "dps": round(total_dps * r["dmg"] / tot, 1), "share": round(100 * r["dmg"] / tot, 1),
                          "casts": round(r["casts"] / n, 1) if kind not in ("auto", "pet") else 0,
                          "crit": round(r["crits"] / r["hits"], 3) if r["hits"] else None})
    # auras that come and go during the fight (procs and cooldowns), not the permanent buffs
    uptimes = []
    for au in pm.get("auras") or []:
        up = au.get("uptimeSecondsAvg", 0) / dur
        sid = au["id"].get("spellId")
        if sid and 0.02 <= up <= 0.97 and au.get("procsAvg", 0) >= 1 and SPELL.get(sid):
            en = SPELL[sid]["name"]
            uptimes.append({"name": {"en": en, "fr": FR_BY_SPELL.get(sid) or FR_SPELL.get(en, en)}, "sid": sid, "uptime": round(min(up, 1), 3), "procs": round(au["procsAvg"], 1)})
    # an aura named like one of the build's attacks is its queue / proc window (Heroic Strike queued, Overpower usable), not an effect
    dmg_names = {x["name"]["en"] for x in abilities}
    seen = set()
    uptimes = [u for u in sorted(uptimes, key=lambda u: -u["uptime"]) if u["name"]["en"] not in dmg_names and "Stance" not in u["name"]["en"]
               and not (u["name"]["en"] in seen or seen.add(u["name"]["en"]))]
    # gear
    items, enchants = [], {}
    for slot, it in zip(SLOTS, p["equipment"]["items"]):
        if not it.get("id"):
            continue
        rec = ITEMS.get(it["id"], {})
        sc = (rec.get("scalingOptions") or {}).get("0", {})
        items.append({"slot": slot, "id": it["id"], "name": {"en": rec.get("name", f"#{it['id']}"), "fr": FR_BY_ITEM.get(it["id"]) or rec.get("name", f"#{it['id']}")}, "q": rec.get("quality", 1), "ilvl": sc.get("ilvl"), "icon": rec.get("icon"), **source(rec)})
        e = enchant(it.get("enchant"), slot) if it.get("enchant") else None
        if e:
            enchants[slot] = e
    # set bonuses and character sheet
    sh = SHEETS.get(b["label"], {})
    fs, ps = (sh.get("finalStats") or {}).get("stats") or [], (sh.get("finalStats") or {}).get("pseudoStats") or []
    g = lambda arr, i: arr[i] if i < len(arr) else 0
    stats = {"prim": {"str": g(fs, 0), "agi": g(fs, 1), "sta": g(fs, 2), "int": g(fs, 3), "spi": g(fs, 13)}, "ap": g(fs, 14), "rap": g(fs, 15),
             "sp": g(fs, 5), "armor": g(fs, 27), "health": g(fs, 29), "mana": g(fs, 30), "mp5": g(fs, 31),
             "hit_r": g(fs, 17), "crit_r": g(fs, 18), "haste_r": g(fs, 19),
             "melee_hit": g(ps, 12), "melee_crit": g(ps, 14), "spell_hit": g(ps, 13), "spell_crit": g(ps, 15), "ranged_crit": g(ps, 25), "ranged_hit": g(ps, 24)}
    # consumables, buffs, debuffs
    cons = []
    c = p.get("consumables") or {}
    for key, kind in CONS:
        v = c.get(key)
        for cid in (v if isinstance(v, list) else [v] if v else []):
            x = consumable(cid)
            if x and not any(y["id"] == cid for y in cons):
                cons.append(dict(x, kind=kind))
    buffs = []
    for src in (req["raid"].get("buffs") or {}, req["raid"]["parties"][0].get("buffs") or {}, p.get("buffs") or {}):
        for k, v in src.items():
            if v and k in BUFFS:
                bid, sid, en = BUFFS[k]
                buffs.append({"id": bid, "sid": sid, "name": {"en": en, "fr": FR_BY_SPELL.get(sid) or en}, "count": v if isinstance(v, int) and not isinstance(v, bool) and v > 1 else None})
    debuffs = [{"id": DEBUFFS[k][0], "sid": DEBUFFS[k][1], "name": {"en": DEBUFFS[k][2], "fr": FR_BY_SPELL.get(DEBUFFS[k][1]) or DEBUFFS[k][2]}} for k, v in (req["raid"].get("debuffs") or {}).items() if v and k in DEBUFFS]
    rot = (p.get("rotation") or {})
    out[spec] = {
        "label": b["label"], "preset": meta.get("preset"), "dps": round(total_dps, 1), "stdev": round(pm["dps"]["stdev"], 1), "iterations": n,
        "race": p["race"].replace("Race", ""), "class": CLASS_ID[p["class"]], "professions": [x for x in (p.get("profession1"), p.get("profession2")) if x and x in PROF_NAME],
        "talents_string": p.get("talentsString", ""), "talents": talents(p["class"], p.get("talentsString", "")),
        "items": items, "enchants": enchants, "sets": sh.get("sets") or [], "stats": stats,
        "abilities": abilities, "uptimes": uptimes[:10], "consumables": cons, "buffs": buffs, "debuffs": debuffs,
        "rotation_type": rot.get("type"), "duration": dur, "duration_variation": req["encounter"].get("durationVariation", 0),
        "target_level": req["encounter"]["targets"][0].get("level"),
    }
    print(f"{spec:24} {total_dps:8.1f}  {len(items)} items  {len(out[spec]['talents'])} talents  {len(abilities)} sources  sets={out[spec]['sets']}", flush=True)

commit = subprocess.run(["git", "log", "-1", "--format=%h %cs"], cwd=CLONE, capture_output=True, text=True).stdout.strip()
(PROJECT / "data" / "wow_ranking_wowsims_detail.json").write_text(json.dumps({"engine_commit": commit, "iterations": a.iterations, "specs": out}, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out), "specs -> data/wow_ranking_wowsims_detail.json")
