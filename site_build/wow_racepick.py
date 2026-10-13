"""'Which race?' pages of each class (/wow-forever/races/<class>/) and their hub (/wow-forever/races/).
Sources (nothing typed by hand except the labels):
  - data/wow_racials.json    racial abilities and the classes each race can play, from the beta client tables (wow_racials_build.py)
  - data/wow_races.json      race names, factions, icons
  - data/wow_races60.json    DPS of each simulated spec played by every race its class allows (sim60/ranking.mjs, RANK_RACES=1)"""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CLASS_BIT = {"warrior": 1, "paladin": 2, "hunter": 4, "rogue": 8, "priest": 16, "shaman": 64, "mage": 128, "warlock": 256, "druid": 1024}
# racial spell id -> how the simulator treats it
SIMULATED = {20597, 20598, 20574, 20572, 1259719, 1259799, 20550, 20591, 20554, 1259710}
DAMAGE_NOT_SIMULATED = {1259812, 1259821, 1259823, 1259817, 1259813, 1260189, 1260201, 20557, 1259721, 1259707, 1259803, 1259802}
EQUIV_SIGMA = 2.0      # a race within 2 error bars of the best one is called equivalent


def _load(name):
    return json.loads((PROJECT / "data" / name).read_text(encoding="utf-8"))


def tag_of(spell_id):
    if spell_id in SIMULATED:
        return "sim"
    if spell_id in DAMAGE_NOT_SIMULATED:
        return "dmg"
    return "util"


def available():
    return (PROJECT / "data" / "wow_races60.json").exists() and (PROJECT / "data" / "wow_racials.json").exists()


def build(lang, cls, ranking_rows):
    """Data of one class page. cls: wt_classes entry; ranking_rows: the DPS + tank rows of the hub ranking (spec names and links)."""
    racials = _load("wow_racials.json")["races"]
    sim = _load("wow_races60.json")
    meta = {"build": sim["build"], "generated": sim["generated"], "fight": sim["fightLen"], "iters": sim["iterations"]}
    names = {}
    for r in _load("wow_races.json")["races"]:
        k = "skyborne-" + r["faction"] if r["key"] == "skyborne" else r["key"]
        names[k] = {"name": r["name"][lang], "faction": r["faction"], "icon": r["icon"]}
    bit = CLASS_BIT[cls["id"]]
    races = []
    for key, rec in racials.items():
        if cls["id"] not in rec["classes"]:
            continue
        spells = []
        for s in rec["spells"]:
            if s["class_mask"] and not (s["class_mask"] & bit):
                continue
            spells.append({"id": s["id"], "name": s["name"][lang], "desc": s["desc"][lang], "cd": s["cooldown_s"], "dur": s["duration_s"], "tag": tag_of(s["id"]),
                           "icon": s["icon"]})
        races.append(dict(names[key], key=key, spells=spells))
    # one table per simulated spec of the class
    specs = []
    by_id = {r["spec_id"]: r for r in ranking_rows if r["class_id"] == cls["id"]}
    for sid, row in by_id.items():
        simrow = sim["specs"].get(sid)
        if not simrow or not simrow["rows"]:
            continue
        top = max(r["racials"]["mean"] for r in simrow["rows"])
        best = max(simrow["rows"], key=lambda r: r["racials"]["mean"])
        lines = []
        for r in simrow["rows"]:
            if r["race"] == "skyborne":           # both Skyborne races when the class can be played by both
                nm = dict(names["skyborne-" + r["factions"][0]], name=" / ".join(names["skyborne-" + f]["name"] for f in r["factions"]))
            else:
                nm = names[r["race"]]
            delta = 100.0 * (r["racials"]["mean"] - top) / top
            err = 100.0 * (r["racials"]["sem"] ** 2 + best["racials"]["sem"] ** 2) ** 0.5 / top
            lines.append({"race": r["race"], "name": nm["name"], "icon": nm["icon"], "factions": r["factions"] or [nm["faction"]], "delta": delta, "err": err,
                          "equiv": delta >= -EQUIV_SIGMA * err, "start": r.get("useStart"), "never": r.get("useStart") == "never"})
        lines.sort(key=lambda x: -x["delta"])
        specs.append({"id": row["spec_id"], "name": row["spec_name"], "tank": simrow["tank"], "lines": lines, "path": row["guide_path"],
                      "best": [l["name"] for l in lines if l["equiv"]]})
    specs.sort(key=lambda s: s["tank"])
    return {"races": races, "specs": specs, "meta": meta}
