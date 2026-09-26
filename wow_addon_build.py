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

Usage: py -3.11 wow_addon_build.py [--iterations 400] [--fight-len 300]
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

# Step sizes: large enough to rise above the residual noise, small enough to stay linear.
RAW_STEPS = {"str": 20, "agi": 20, "int": 30}
SHEET_STEPS = {"ap": 40, "sp": 40, "crit": 0.03, "hit": 0.02}


def mean_dps(spec_id, stats, iterations, fight_len):
    profile = sim.ROTATIONS[spec_id]
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
        stats = ", ".join(f"{k} = {w[k]}" for k in ("str", "agi", "int", "ap", "sp", "crit", "hit"))
        ranged = "true" if sim.SPEC_STAT_PROFILE.get(spec_id, {}).get("agi_ap") == "ranged" else "false"
        lines.append(
            f'  {spec_id} = {{ class = "{cls.upper()}", spec = "{sim.SPEC_ID_MAP.get(spec_id, spec_id)}", '
            f'role = "{prof.get("role", "dps")}", tab = {tab}, ranged = {ranged}, caster = {caster}, dps = {dps:.2f},\n'
            f"    name = {{ frFR = {lua_str(names['fr'])}, enUS = {lua_str(names['en'])} }},\n"
            f"    w = {{ {stats} }} }},"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--iterations", type=int, default=400)
    parser.add_argument("--fight-len", type=float, default=300.0)
    args = parser.parse_args()

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
