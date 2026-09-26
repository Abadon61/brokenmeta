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
        # Same equal-level baselines bis_stats_for_spec() uses (97% spells, 95% melee/ranged).
        hit = 97 + num(data, "hit_spell")
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


def run(spec_id, stats, weapons, iterations, fight_len):
    """Seeded fights (seed = fight index) so two runs compare the same luck, not noise."""
    profile = copy.deepcopy(sim.ROTATIONS[spec_id])
    if weapons is not None:
        profile["weapons"] = weapons
    glossary = sim.wow_spells.load_class(profile.get("glossary", spec_id))
    total, by = 0.0, {}
    for i in range(iterations):
        random.seed(i)
        dmg, dmg_by = sim.Sim(spec_id, profile, glossary, stats, fight_len).run()
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
        glossary = sim.wow_spells.load_class(sim.ROTATIONS[spec_id].get("glossary", spec_id))
        dps, by = run(spec_id, stats, weapons, iterations, fight_len)
        bis_stats = sim.bis_stats_for_spec(spec_id) or sim.DEFAULT_STATS
        bis_dps, _ = run(spec_id, bis_stats, None, iterations, fight_len)
        breakdown = sorted(({"name": label(glossary, k, lang), "dps": round(v, 2)} for k, v in by.items() if v > 0),
                           key=lambda r: -r["dps"])
        return json.dumps({
            "ok": True, "spec": spec_id, "specs": specs, "role": sim.ROTATIONS[spec_id].get("role", "dps"),
            "addon": data.get("addon", ""), "class": data["class"], "level": int(num(data, "level", SIM_LEVEL)), "race": data.get("race", ""),
            "dps": round(dps, 2), "bis_dps": round(bis_dps, 2), "breakdown": breakdown,
            "stats": stats, "bis_stats": bis_stats, "weapons": weapons,
            "bis_weapons": sim.ROTATIONS[spec_id].get("weapons", []),
            "warnings": warnings, "iterations": iterations, "fight_len": fight_len,
        })
    except ExportError as e:
        return json.dumps({"ok": False, "error": e.code, **e.info})


if __name__ == "__main__":
    src = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    print(json.dumps(json.loads(simulate(src, sys.argv[2] if len(sys.argv) > 2 else None)), indent=1, ensure_ascii=False))
