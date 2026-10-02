"""Simulates a real character from the BrokenMeta addon's export (/bmw export).

Runs in the visitor's browser through Pyodide (see js/wow-mysim-worker.js) -- the exact same
wow_dps_sim.py engine as the public DPS ranking and the addon's stat weights, so the three never
disagree. Also runnable locally: `py -3.11 site_build/wow_mysim.py export.txt`.

The export is plain `key=value` lines (format=BMW1). Stats come from the in-game character
sheet (so they already include gear, talents' passive stat bonuses and any active buffs); weapon
damage is converted back from the sheet's min/max to the sim's own per-swing convention.
"""
import copy
import json
import random
import sys

import wow_dps_sim as sim
import wow_weights

FORMAT = "BMW1"
# Spell school whose Spell Power matters for a caster spec, when SPEC_STAT_PROFILE doesn't say.
DEFAULT_SCHOOL = {"shaman": "nature", "paladin": "holy", "druid": "arcane"}
SIM_LEVEL = 20

LABELS = {
    "fr": {"white": "Attaque de base", "hunter_pet": "Familier"},
    "en": {"white": "Auto attack", "hunter_pet": "Pet"},
}


class ExportError(ValueError):
    """The pasted text isn't a usable export; `code` is a key the page translates."""

    def __init__(self, code, **info):
        super().__init__(code)
        self.code, self.info = code, info


def parse_export(text):
    data = {}
    for line in (text or "").splitlines():
        line = line.strip()
        if "=" in line:
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip()
    if data.get("format") != FORMAT:
        raise ExportError("bad_format")
    if not data.get("class"):
        raise ExportError("no_class")
    return data


def num(data, key, default=0.0):
    try:
        return float(data.get(key, ""))
    except ValueError:
        return default


def specs_for_class(class_token):
    cls = class_token.lower()
    return [sid for sid, p in sim.ROTATIONS.items() if p.get("glossary", sid) == cls]


def character_stats(data, spec_id):
    """Export -> (stats {ap, sp, hit, crit}, weapons list, warnings)."""
    meta = sim.SPEC_STAT_PROFILE.get(spec_id, {})
    class_id = sim.ROTATIONS[spec_id].get("glossary", spec_id)
    warnings = []
    ranged = meta.get("agi_ap") == "ranged"

    if meta.get("crit") == "spell":
        school = meta.get("school") or DEFAULT_SCHOOL.get(class_id)
        sp = num(data, f"sp_{school}") if school and f"sp_{school}" in data else num(data, "sp")
        crit = num(data, "crit_spell")
        # Same equal-level baselines bis_stats_for_spec() uses (96% spells capped at 99%, 95% melee/ranged).
        hit = min(sim.SPELL_HIT_BASE_PCT + num(data, "hit_spell"), sim.SPELL_HIT_CAP * 100)
        ap = num(data, "ap")
    else:
        sp = num(data, "sp")
        ap = num(data, "rap") if ranged else num(data, "ap")
        crit = num(data, "crit_ranged") if ranged else num(data, "crit_melee")
        hit = 95 + num(data, "hit_melee")
    stats = {"ap": round(ap, 1), "sp": round(sp, 1), "hit": round(min(hit, 100) / 100, 4), "crit": round(crit / 100, 4)}

    # Weapons: the sheet's min/max already include the AP bonus (AP/14 per second of weapon
    # speed) and any % damage modifier; strip both to get the weapon's own average damage,
    # which is what the sim's profile "dmg" holds.
    weapons = []
    profile_weapons = sim.ROTATIONS[spec_id].get("weapons", [])
    if profile_weapons:
        if ranged:
            speed, lo, hi, pct = num(data, "r_speed"), num(data, "r_min"), num(data, "r_max"), num(data, "r_pct", 1.0) or 1.0
            if speed > 0 and hi > 0:
                weapons.append({"dmg": round(max(0.0, (lo + hi) / 2 / pct - ap / 14 * speed), 2), "speed": speed})
        else:
            pct = num(data, "dmg_pct", 1.0) or 1.0
            mh_speed, oh_speed = num(data, "speed_mh"), num(data, "speed_oh")
            if mh_speed > 0 and num(data, "mh_max") > 0:
                avg = (num(data, "mh_min") + num(data, "mh_max")) / 2
                weapons.append({"dmg": round(max(0.0, avg / pct - ap / 14 * mh_speed), 2), "speed": mh_speed})
            if oh_speed > 0 and num(data, "oh_max") > 0:
                avg = (num(data, "oh_min") + num(data, "oh_max")) / 2
                weapons.append({"dmg": round(max(0.0, avg / pct / 0.5 - ap / 14 * oh_speed), 2),
                                "speed": oh_speed, "offhand": True})
        if not weapons:
            warnings.append("no_weapon_data")
            weapons = copy.deepcopy(profile_weapons)

    level = int(num(data, "level", SIM_LEVEL))
    if level != SIM_LEVEL:
        warnings.append("level")
    if num(data, "buffs") > 0:
        warnings.append("buffs")
    return stats, weapons, warnings


def sim_level(data):
    """The character's level, clamped to what the simulator supports (spell ranks 1-60)."""
    return max(1, min(sim.MAX_LEVEL, int(num(data, "level", SIM_LEVEL))))


def run(spec_id, stats, weapons, iterations, fight_len, level=SIM_LEVEL):
    """Seeded fights (seed = fight index) so two runs compare the same luck, not noise."""
    profile = copy.deepcopy(sim.ROTATIONS[spec_id])
    if weapons is not None:
        profile["weapons"] = weapons
    glossary = sim.load_glossary(profile.get("glossary", spec_id), level)
    total, by = 0.0, {}
    for i in range(iterations):
        random.seed(i)
        dmg, dmg_by = sim.Sim(spec_id, profile, glossary, stats, fight_len, level).run()
        total += dmg
        for k, v in dmg_by.items():
            by[k] = by.get(k, 0.0) + v
    n = iterations * fight_len
    return total / n, {k: v / n for k, v in by.items()}


def label(glossary, tag, lang):
    for ab in glossary.get("abilities", []):
        if ab.get("id") == tag:
            return (ab.get("name") or {}).get(lang) or tag
    return LABELS[lang].get(tag, tag)


def simulate(text, spec_id=None, lang="fr", iterations=300, fight_len=300.0):
    """Entry point for the page. Returns a JSON string (easy to pass out of Pyodide)."""
    try:
        data = parse_export(text)
        specs = specs_for_class(data["class"])
        if not specs:
            raise ExportError("class_not_simulated", cls=data["class"])
        spec_id = spec_id or data.get("spec")
        if spec_id not in specs:
            spec_id = specs[0]
        stats, weapons, warnings = character_stats(data, spec_id)
        level = sim_level(data)
        glossary = sim.load_glossary(sim.ROTATIONS[spec_id].get("glossary", spec_id), level)
        dps, by = run(spec_id, stats, weapons, iterations, fight_len, level)
        # The BiS reference is a level-20 gear set: only compared at level 20.
        bis_stats = sim.bis_stats_for_spec(spec_id) or sim.DEFAULT_STATS
        bis_dps = run(spec_id, bis_stats, None, iterations, fight_len)[0] if level == SIM_LEVEL else None
        breakdown = sorted(({"name": label(glossary, k, lang), "dps": round(v, 2)} for k, v in by.items() if v > 0),
                           key=lambda r: -r["dps"])
        return json.dumps({
            "ok": True, "spec": spec_id, "specs": specs, "role": sim.ROTATIONS[spec_id].get("role", "dps"),
            "addon": data.get("addon", ""), "class": data["class"], "level": int(num(data, "level", SIM_LEVEL)), "race": data.get("race", ""),
            "dps": round(dps, 2), "bis_dps": round(bis_dps, 2) if bis_dps is not None else None, "breakdown": breakdown,
            "stats": stats, "bis_stats": bis_stats, "weapons": weapons,
            "bis_weapons": sim.ROTATIONS[spec_id].get("weapons", []),
            "warnings": warnings, "iterations": iterations, "fight_len": fight_len,
        })
    except ExportError as e:
        return json.dumps({"ok": False, "error": e.code, **e.info})



# ------------------------------------------------------------------ personal weights + Top gear
# (2026-09-26) Replaces the old manual-input calculator: the player's own sheet and weapons from
# the addon export go through wow_weights.stat_weights(), then every dungeon item they can wear
# is valued with those weights and compared with what they wear (addon 0.6.1+ exports each
# equipped item's stats as stN / locN).
DUNGEON_FILE = sim.wow_spells.ROOT / "data" / "wow_dungeons" / "dungeons.json"
PROFICIENCY_FILE = sim.wow_spells.ROOT / "data" / "wow_items" / "proficiency.json"
# Dungeon item slot code -> (equipLoc, inventory slots it can go in)
DUNGEON_SLOTS = {
    1: ("INVTYPE_HEAD", [1]), 2: ("INVTYPE_NECK", [2]), 3: ("INVTYPE_SHOULDER", [3]), 5: ("INVTYPE_CHEST", [5]),
    20: ("INVTYPE_ROBE", [5]), 6: ("INVTYPE_WAIST", [6]), 7: ("INVTYPE_LEGS", [7]), 8: ("INVTYPE_FEET", [8]),
    9: ("INVTYPE_WRIST", [9]), 10: ("INVTYPE_HAND", [10]), 11: ("INVTYPE_FINGER", [11, 12]),
    12: ("INVTYPE_TRINKET", [13, 14]), 13: ("INVTYPE_WEAPON", [16, 17]), 14: ("INVTYPE_SHIELD", [17]),
    15: ("INVTYPE_RANGED", [18]), 16: ("INVTYPE_CLOAK", [15]), 17: ("INVTYPE_2HWEAPON", [16]),
    21: ("INVTYPE_WEAPONMAINHAND", [16]), 22: ("INVTYPE_WEAPONOFFHAND", [17]), 23: ("INVTYPE_HOLDABLE", [17]),
    25: ("INVTYPE_THROWN", [18]), 26: ("INVTYPE_RANGEDRIGHT", [18]),
}
RANGED_LOCS = {"INVTYPE_RANGED", "INVTYPE_RANGEDRIGHT", "INVTYPE_THROWN"}
MAIN_LOCS = {"INVTYPE_WEAPON", "INVTYPE_WEAPONMAINHAND", "INVTYPE_2HWEAPON"}
TOP_PER_SLOT = 3
_cache = {}


def _json(path):
    if path not in _cache:
        _cache[path] = json.loads(path.read_text(encoding="utf-8"))
    return _cache[path]


def item_value(st, loc, w, spec_id, rating_crit, rating_hit):
    """Simulated DPS an item's stats are worth -- the same formula as the addon's scoreStats()."""
    meta = sim.SPEC_STAT_PROFILE.get(spec_id, {})
    own = "spell" if meta.get("crit") == "spell" else "phys"
    ranged = meta.get("agi_ap") == "ranged"
    crit_r = st.get("critR", 0) + st.get("critR_" + own, 0)
    hit_r = st.get("hitR", 0) + st.get("hitR_" + own, 0)
    crit_p = st.get("critP_" + own, 0) + crit_r / rating_crit
    hit_p = st.get("hitP_" + own, 0) + hit_r / rating_hit
    ap = st.get("ap", 0) + (st.get("rap", 0) if ranged else 0)
    if loc in RANGED_LOCS:
        wdps_w = w["wdps_r"]
    elif loc == "INVTYPE_WEAPONOFFHAND":
        wdps_w = w["wdps_oh"]
    elif loc in MAIN_LOCS:
        wdps_w = w["wdps_mh"]
    else:
        wdps_w = 0
    return (st.get("str", 0) * w["str"] + st.get("agi", 0) * w["agi"] + st.get("int", 0) * w["int"]
            + ap * w["ap"] + st.get("sp", 0) * w["sp"] + crit_p * w["crit"] + hit_p * w["hit"]
            + st.get("wdps", 0) * wdps_w)


def equipped_stats(data):
    """{inventory slot: (stats dict, equipLoc)} from the export's stN / locN lines."""
    out = {}
    for key, value in data.items():
        if key.startswith("st") and key[2:].isdigit():
            slot = int(key[2:])
            st = {}
            for pair in value.split(","):
                k, _, v = pair.partition(":")
                try:
                    st[k] = float(v)
                except ValueError:
                    pass
            out[slot] = (st, data.get(f"loc{slot}", ""))
    return out


def dungeon_item_stats(it):
    s = it["st"]
    return {"str": s.get("str", 0), "agi": s.get("agi", 0), "int": s.get("int", 0), "ap": s.get("atkpwr", 0),
            "sp": (s.get("splpwr") or 0) + (s.get("spldmg") or 0), "critR": s.get("critstrkrtng", 0),
            "hitR": s.get("hitrtng", 0), "wdps": s.get("rgddps") or s.get("dps") or 0}


def top_gear(data, spec_id, w, lang):
    dungeons = _json(DUNGEON_FILE)
    prof = _json(PROFICIENCY_FILE)["classes"].get(data["class"], {})
    known_types = set().union(*(set(v) for v in _json(PROFICIENCY_FILE)["classes"].values()))
    level = int(num(data, "level", SIM_LEVEL))
    rating_crit = num(data, "rating_crit", 14) or 14
    rating_hit = num(data, "rating_hit", 10) or 10
    worn = equipped_stats(data)
    worn_value = {slot: item_value(st, loc, w, spec_id, rating_crit, rating_hit) for slot, (st, loc) in worn.items()}
    # Weapons: a two-hander replaces both hands; a one-hander only goes in the off hand for a spec
    # the simulator dual-wields (or a player already holding an off-hand weapon); off-hand items
    # are skipped while a two-hander is worn (they would need a one-hander too).
    dual = any(wp.get("offhand") for wp in sim.ROTATIONS[spec_id].get("weapons", [])) or num(data, "oh_max") > 0
    two_hander_worn = worn.get(16, ({}, ""))[1] == "INVTYPE_2HWEAPON"
    best = {}
    for dg in dungeons["dungeons"]:
        for it in dg["items"]:
            slot_def = DUNGEON_SLOTS.get(it["slot"])
            if not slot_def or it.get("req", 0) > level + 3:
                continue
            type_en = it["type"]["en"]
            if type_en in known_types and (type_en not in prof or prof[type_en] > level):
                continue
            loc, inv = slot_def
            if loc in ("INVTYPE_WEAPONOFFHAND", "INVTYPE_SHIELD", "INVTYPE_HOLDABLE") and two_hander_worn:
                continue
            value = item_value(dungeon_item_stats(it), loc, w, spec_id, rating_crit, rating_hit)
            if loc == "INVTYPE_2HWEAPON":
                baseline = worn_value.get(16, 0) + worn_value.get(17, 0)
            elif loc == "INVTYPE_WEAPON":
                baseline = min(worn_value.get(s, 0) for s in ([16, 17] if dual and not two_hander_worn else [16]))
            else:
                baseline = min(worn_value.get(s, 0) for s in inv)
            gain = value - baseline
            if gain <= 0.005:
                continue
            row = {"id": it["id"], "name": it["name"], "icon": it.get("icon"), "q": it.get("q", 2),
                   "slot": dungeons["slots"].get(str(it["slot"]), {}).get(lang, ""), "req": it.get("req", 0),
                   "dungeon": dg["name"].get(lang) or dg["name"]["en"], "levels": dg.get("levels", ""),
                   "boss": (it.get("src") or [""])[0], "quest": it.get("kind") == "quest",
                   "gain": round(gain, 2), "value": round(value, 2)}
            best.setdefault(row["slot"], []).append(row)
    out = []
    for rows in best.values():
        rows.sort(key=lambda r: -r["gain"])
        out.extend(rows[:TOP_PER_SLOT])
    out.sort(key=lambda r: -r["gain"])
    return out, bool(worn)


def personal(text, spec_id=None, lang="fr", progress=None, iterations=300, fight_len=180.0):
    """Personal stat weights (player's own sheet and weapons) + Top gear. JSON string."""
    try:
        data = parse_export(text)
        specs = specs_for_class(data["class"])
        if not specs:
            raise ExportError("class_not_simulated", cls=data["class"])
        spec_id = spec_id or data.get("spec")
        if spec_id not in specs:
            spec_id = specs[0]
        stats, weapons, warnings = character_stats(data, spec_id)
        dps, w = wow_weights.stat_weights(spec_id, stats, weapons or None, iterations, fight_len, progress, sim_level(data))
        gear, has_worn = top_gear(data, spec_id, w, lang)
        meta = sim.SPEC_STAT_PROFILE.get(spec_id, {})
        return json.dumps({
            "ok": True, "spec": spec_id, "level": sim_level(data), "weights": w, "dps": round(dps, 2), "warnings": warnings,
            "caster": meta.get("crit") == "spell", "ranged": meta.get("agi_ap") == "ranged",
            "top": gear, "has_worn_stats": has_worn, "iterations": iterations, "fight_len": fight_len,
        })
    except ExportError as e:
        return json.dumps({"ok": False, "error": e.code, **e.info})


if __name__ == "__main__":
    src = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    print(json.dumps(json.loads(simulate(src, sys.argv[2] if len(sys.argv) > 2 else None)), indent=1, ensure_ascii=False))
