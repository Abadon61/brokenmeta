"""Generates the stat weights used by the BrokenMetaWeights WoW: Forever addon.

For every spec in site_build/wow_dps_sim.py's ROTATIONS, measures how much simulated DPS one
extra point of each stat adds on top of that spec's real level-20 BiS gear, then writes the
result as a Lua table to wow_addon/BrokenMetaWeights/Weights.lua.

Method: finite differences with common random numbers -- the baseline and every perturbed run
replay the SAME seeded fights, so the tiny DPS gain from +20 Strength isn't drowned in
fight-to-fight RNG noise. Primary stats (Str/Agi/Int) are perturbed on the raw gear totals and
go through the sim's own bis_stats_for_spec() conversion, so the addon's weights always agree
with whatever conversion ratios the site's simulator uses. Direct stats (AP, SP, Crit %, Hit %)
are perturbed on the final {ap, sp, crit, hit} sheet.

Also writes wow_addon/BrokenMetaWeights/Data.lua (no simulation needed, `--data-only`): dungeon
loot with stats, class armor/weapon proficiency, recommended talent builds and profession routes,
all from the site's own data files.

Usage: py -3.11 wow_addon_build.py [--iterations 400] [--fight-len 300] [--data-only]
"""
import argparse
import copy
import json
import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "site_build"))
import wow_dps_sim as sim  # noqa: E402

OUT = ROOT / "wow_addon" / "BrokenMetaWeights" / "Weights.lua"
DATA_OUT = ROOT / "wow_addon" / "BrokenMetaWeights" / "Data.lua"
WEAPON_STEP = 2.0  # +2 weapon DPS (dmg per swing += 2 x speed)

# Step sizes: large enough to rise above the residual noise, small enough to stay linear.
RAW_STEPS = {"str": 20, "agi": 20, "int": 30}
SHEET_STEPS = {"ap": 40, "sp": 40, "crit": 0.03, "hit": 0.02}


def mean_dps(spec_id, stats, iterations, fight_len, profile=None):
    profile = profile or sim.ROTATIONS[spec_id]
    glossary = sim.wow_spells.load_class(profile.get("glossary", spec_id))
    total = 0.0
    for i in range(iterations):
        random.seed(i)
        dmg, _ = sim.Sim(spec_id, profile, glossary, stats, fight_len).run()
        total += dmg
    return total / iterations / fight_len


def sheet_with_raw(spec_id, stat, delta):
    """bis_stats_for_spec() after adding `delta` to one raw gear stat (Str/Agi/Int)."""
    data = sim._load_bis_data()
    saved = copy.deepcopy(data["specs"][spec_id])
    try:
        data["specs"][spec_id]["stats"][stat] = data["specs"][spec_id]["stats"].get(stat, 0) + delta
        return sim.bis_stats_for_spec(spec_id)
    finally:
        data["specs"][spec_id] = saved


def weights_for(spec_id, iterations, fight_len):
    base = sim.bis_stats_for_spec(spec_id)
    if base is None:
        return None
    base_dps = mean_dps(spec_id, base, iterations, fight_len)
    w = {}
    for stat, step in SHEET_STEPS.items():
        s = dict(base)
        s[stat] = s[stat] + step
        if stat == "hit":
            s[stat] = min(1.0, s[stat])
            step = s[stat] - base[stat]
            if step <= 0:
                w[stat] = 0.0
                continue
        gain = (mean_dps(spec_id, s, iterations, fight_len) - base_dps) / step
        # crit/hit are fractions in the sim; the addon wants DPS per 1 percentage point.
        w[stat] = gain / 100 if stat in ("crit", "hit") else gain
    for stat, step in RAW_STEPS.items():
        s = sheet_with_raw(spec_id, stat, step)
        w[stat] = 0.0 if s == base else (mean_dps(spec_id, s, iterations, fight_len) - base_dps) / step
    # Weapon DPS: +WEAPON_STEP DPS on each simulated weapon. Hunters' only simulated weapon is the
    # ranged one (Auto Shot), so their weight goes to ranged slots; melee specs get main/off hand.
    ranged = sim.SPEC_STAT_PROFILE.get(spec_id, {}).get("agi_ap") == "ranged"
    w.update(wdps_mh=0.0, wdps_oh=0.0, wdps_r=0.0)
    for idx, wpn in enumerate(sim.ROTATIONS[spec_id].get("weapons", [])):
        prof = copy.deepcopy(sim.ROTATIONS[spec_id])
        prof["weapons"][idx]["dmg"] += WEAPON_STEP * wpn["speed"]
        gain = (mean_dps(spec_id, base, iterations, fight_len, prof) - base_dps) / WEAPON_STEP
        w["wdps_r" if ranged else ("wdps_oh" if wpn.get("offhand") else "wdps_mh")] = gain
    # Negative values are pure noise on stats the rotation barely uses; clamp them.
    w = {k: max(0.0, round(v, 4)) for k, v in w.items()}
    return base_dps, base, w


def talent_specs(cls):
    """Real spec ids, FR/EN names and talent-tab order from the beta client tables."""
    d = json.loads((ROOT / "data" / "wow_talents" / f"{cls}.json").read_text(encoding="utf-8"))
    return {s["id"]: (i + 1, s["name"]) for i, s in enumerate(d["specs"])}


def talent_nodes_lua():
    """Every class's talent node ids mapped to their talent tree index, so the addon can count
    the points spent per tree in game and export talents the site's calculator understands."""
    lines = ["ns.TALENT_TAB = {"]
    for f in sorted((ROOT / "data" / "wow_talents").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        pairs = [f"[{t['id'].lstrip('n')}] = {i + 1}" for i, s in enumerate(d["specs"]) for t in s["talents"]]
        lines.append(f"  {d['id'].upper()} = {{ " + ", ".join(pairs) + " },")
    lines.append("}")
    return "\n".join(lines)


def lua_str(v):
    return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'


def lua_table(rows):
    lines = []
    for spec_id, (dps, base, w) in rows.items():
        prof = sim.ROTATIONS[spec_id]
        cls = prof.get("glossary", spec_id)
        tab, names = talent_specs(cls)[sim.SPEC_ID_MAP[spec_id]]
        caster = "true" if sim.SPEC_STAT_PROFILE.get(spec_id, {}).get("crit") == "spell" else "false"
        stats = ", ".join(f"{k} = {w[k]}" for k in ("str", "agi", "int", "ap", "sp", "crit", "hit", "wdps_mh", "wdps_oh", "wdps_r"))
        ranged = "true" if sim.SPEC_STAT_PROFILE.get(spec_id, {}).get("agi_ap") == "ranged" else "false"
        lines.append(
            f'  {spec_id} = {{ class = "{cls.upper()}", spec = "{sim.SPEC_ID_MAP.get(spec_id, spec_id)}", '
            f'role = "{prof.get("role", "dps")}", tab = {tab}, ranged = {ranged}, caster = {caster}, dps = {dps:.2f},\n'
            f"    name = {{ frFR = {lua_str(names['fr'])}, enUS = {lua_str(names['en'])} }},\n"
            f"    w = {{ {stats} }} }},"
        )
    return "\n".join(lines)


# ------------------------------------------------------------------------------------ Data.lua
DUNGEON_SLOTS = {1: "INVTYPE_HEAD", 2: "INVTYPE_NECK", 3: "INVTYPE_SHOULDER", 5: "INVTYPE_CHEST", 20: "INVTYPE_ROBE",
                 6: "INVTYPE_WAIST", 7: "INVTYPE_LEGS", 8: "INVTYPE_FEET", 9: "INVTYPE_WRIST", 10: "INVTYPE_HAND",
                 11: "INVTYPE_FINGER", 12: "INVTYPE_TRINKET", 13: "INVTYPE_WEAPON", 14: "INVTYPE_SHIELD",
                 15: "INVTYPE_RANGED", 16: "INVTYPE_CLOAK", 17: "INVTYPE_2HWEAPON", 21: "INVTYPE_WEAPONMAINHAND",
                 22: "INVTYPE_WEAPONOFFHAND", 23: "INVTYPE_HOLDABLE", 25: "INVTYPE_THROWN", 26: "INVTYPE_RANGEDRIGHT"}
PROF_SKILL_LINES = {"alchemy": 171, "blacksmithing": 164, "enchanting": 333, "engineering": 202,
                    "leatherworking": 165, "tailoring": 197, "cooking": 185, "first-aid": 129}


def lua(v):
    """Python value -> Lua literal (dicts with str keys become records, lists become arrays)."""
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(round(v, 4)) if isinstance(v, float) else str(v)
    if isinstance(v, str):
        return lua_str(v)
    if isinstance(v, list):
        return "{" + ", ".join(lua(x) for x in v) + "}"
    if isinstance(v, dict):
        parts = []
        for k, x in v.items():
            key = k if isinstance(k, str) and k.isidentifier() else f"[{lua(k)}]"
            parts.append(f"{key} = {lua(x)}")
        return "{" + ", ".join(parts) + "}"
    raise TypeError(type(v))


def loot_data():
    d = json.loads((ROOT / "data" / "wow_dungeons" / "dungeons.json").read_text(encoding="utf-8"))
    dungeons, loot = [], []
    for i, dg in enumerate(d["dungeons"], 1):
        dungeons.append({"id": dg["id"], "name": {"frFR": dg["name"]["fr"], "enUS": dg["name"]["en"]}, "levels": dg["levels"]})
        for it in dg["items"]:
            st = it["st"]
            stats = {k: v for k, v in {
                "str": st.get("str"), "agi": st.get("agi"), "int": st.get("int"), "ap": st.get("atkpwr"),
                "sp": (st.get("splpwr") or 0) + (st.get("spldmg") or 0) or None,
                "critR": st.get("critstrkrtng"), "hitR": st.get("hitrtng"),
                "wdps": st.get("rgddps") or st.get("dps"),
            }.items() if v}
            loot.append({"id": it["id"], "d": i, "slot": DUNGEON_SLOTS.get(it["slot"]), "t": it["type"]["en"] or None,
                         "req": it.get("req", 0), "q": it.get("q", 2), "n": it["name"],
                         "src": (it.get("src") or [None])[0], "quest": it.get("kind") == "quest", "st": stats})
    return dungeons, loot


def talent_builds():
    """Recommended talent nodes per spec (Icy Veins level-20 templates, data/wow_guides/content.json)
    and the site guide path. Only node ids: the addon shows how many the player follows and links
    to the guide for the details (user decision: keep the full guide on the site, 2026-09-26)."""
    content = json.loads((ROOT / "data" / "wow_guides" / "content.json").read_text(encoding="utf-8"))
    out = {}
    for spec_id, prof in sim.ROTATIONS.items():
        cls, spec = prof.get("glossary", spec_id), sim.SPEC_ID_MAP.get(spec_id)
        build = content.get(cls, {}).get(spec, {}).get("build") or {}
        out[spec_id] = {
            "guide": f"wow-forever/guides/{cls}/{spec}/",
            "level": build.get("level"),
            "core": [int(t["id"].lstrip("n")) for t in build.get("talents", []) if not t.get("option")],
            "optional": [int(t["id"].lstrip("n")) for t in build.get("talents", []) if t.get("option")],
        }
    return out


def profession_routes():
    out = {}
    for f in sorted((ROOT / "data" / "wow_professions").glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        line = PROF_SKILL_LINES.get(p["id"])
        if not line:
            continue
        out[line] = {"id": p["id"], "name": {"frFR": p["name"]["fr"], "enUS": p["name"]["en"]}, "cap": p["cap"], "steps": [
            {"f": s["from"], "t": s["to"], "c": s["crafts"], "recipe": s["recipe"],
             "name": {"frFR": s["name"]["fr"], "enUS": s["name"]["en"]},
             "reag": [{"id": g["id"], "n": g["count"], "name": {"frFR": g["name"]["fr"], "enUS": g["name"]["en"]}}
                      for g in s["reagents"]]}
            for s in p["route"]]}
    return out


def write_data_lua():
    dungeons, loot = loot_data()
    prof = json.loads((ROOT / "data" / "wow_items" / "proficiency.json").read_text(encoding="utf-8"))["classes"]
    nl = chr(10)
    parts = [
        "-- GENERATED by wow_addon_build.py (--data-only) from the site's data files -- do not edit by hand.",
        f"-- {date.today().isoformat()}. Sources: data/wow_dungeons, data/wow_items/proficiency.json (beta client",
        "-- tables), data/wow_guides/content.json (Icy Veins level-20 talent templates), data/wow_professions.",
        "local _, ns = ...",
        "ns.DUNGEONS = {" + nl + ("," + nl).join("  " + lua(x) for x in dungeons) + nl + "}",
        "ns.LOOT = {" + nl + ("," + nl).join("  " + lua(x) for x in loot) + nl + "}",
        "ns.PROFICIENCY = " + lua(prof),
        "ns.TALENT_BUILDS = {" + nl + ("," + nl).join(f"  {k} = {lua(v)}" for k, v in talent_builds().items()) + nl + "}",
        "ns.PROFESSIONS = {" + nl + ("," + nl).join(f"  [{k}] = {lua(v)}" for k, v in profession_routes().items()) + nl + "}",
    ]
    DATA_OUT.write_text(nl.join(parts) + nl, encoding="utf-8")
    print(f"wrote {DATA_OUT.relative_to(ROOT)} ({len(loot)} loot items, {len(dungeons)} dungeons)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--iterations", type=int, default=400)
    parser.add_argument("--fight-len", type=float, default=300.0)
    parser.add_argument("--data-only", action="store_true", help="only rewrite Data.lua (no simulation)")
    args = parser.parse_args()
    write_data_lua()
    if args.data_only:
        return

    rows = {}
    for spec_id in sim.ROTATIONS:
        r = weights_for(spec_id, args.iterations, args.fight_len)
        if r is None:
            print(f"{spec_id}: no BiS data, skipped")
            continue
        rows[spec_id] = r
        w = r[2]
        print(f"{spec_id:22s} {r[0]:7.2f} DPS  " + "  ".join(f"{k}={w[k]:.3f}" for k in w))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "-- GENERATED by wow_addon_build.py -- do not edit by hand, re-run the script instead.\n"
        f"-- {date.today().isoformat()}, {args.iterations} fights x {args.fight_len:.0f}s per point, level-20 BiS gear.\n"
        "-- w = simulated DPS gained per +1 of: str/agi/int/ap/sp (points), crit/hit (percentage points).\n"
        "local _, ns = ...\n"
        "ns.WEIGHTS = {\n" + lua_table(rows) + "\n}\n\n"
        "-- Talent tree index per talent node id (the client's TraitNode ids), from data/wow_talents.\n"
        + talent_nodes_lua() + "\n",
        encoding="utf-8",
    )
    print(f"\nwrote {OUT.relative_to(ROOT)} ({len(rows)} specs)")


if __name__ == "__main__":
    main()
