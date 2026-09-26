"""Stat weights -- simulated DPS gained per point of each stat -- for one spec and one stat sheet.

One implementation shared by the addon's generator (level-20 BiS sheet, wow_addon_build.py) and
the "Simulate my character" page (the player's own sheet, run in the browser through Pyodide),
so the two can never disagree.

Method (audited 2026-09-26):
  - common random numbers: every run replays the same seeded fights, so a +30 AP difference is
    not drowned in fight-to-fight luck;
  - central differences, (DPS(x+h) - DPS(x-h)) / 2h, for AP, SP, crit, hit and weapon DPS: less
    bias than a one-sided step where DPS is not linear (hit and Rage for Warriors, for example);
  - Strength, Agility and Intellect are not simulated: they are derived exactly from the AP /
    crit / SP weights through the simulator's own linear conversion (stat_deltas_from_raw), which
    removes their noise entirely.
"""
import copy
import random

import wow_dps_sim as sim

STEPS = {"ap": 30, "sp": 30, "crit": 0.02, "hit": 0.015}
WEAPON_STEP = 2.0  # weapon DPS
KEYS = ("str", "agi", "int", "ap", "sp", "crit", "hit", "wdps_mh", "wdps_oh", "wdps_r")


def mean_dps(spec_id, profile, glossary, stats, iterations, fight_len):
    total = 0.0
    for i in range(iterations):
        random.seed(i)
        dmg, _ = sim.Sim(spec_id, profile, glossary, stats, fight_len).run()
        total += dmg
    return total / iterations / fight_len


def stat_weights(spec_id, stats, weapons=None, iterations=800, fight_len=300.0, progress=None):
    """Returns (dps_at_stats, {stat: DPS per point}). crit/hit are per percentage point, wdps_*
    per point of weapon DPS. `weapons` overrides the spec profile's weapons (the player's own);
    `progress(done, total)` is called after each simulated batch."""
    profile = copy.deepcopy(sim.ROTATIONS[spec_id])
    if weapons is not None:
        profile["weapons"] = copy.deepcopy(weapons)
    glossary = sim.wow_spells.load_class(profile.get("glossary", spec_id))
    meta = sim.SPEC_STAT_PROFILE.get(spec_id, {})
    caster = meta.get("crit") == "spell"
    ranged = meta.get("agi_ap") == "ranged"
    plan = ["sp", "crit", "hit"] if caster else ["ap", "sp", "crit", "hit"]
    weapon_idx = [] if caster else list(range(len(profile.get("weapons", []))))
    total_runs = 1 + 2 * len(plan) + 2 * len(weapon_idx)
    done = [0]

    def run(st, prof=profile):
        value = mean_dps(spec_id, prof, glossary, st, iterations, fight_len)
        done[0] += 1
        if progress:
            progress(done[0], total_runs)
        return value

    base = run(stats)
    w = {k: 0.0 for k in KEYS}
    caps = {"hit": sim.SPELL_HIT_CAP if caster else 1.0, "crit": 1.0}
    for stat in plan:
        up, down = dict(stats), dict(stats)
        up[stat] = min(caps.get(stat, float("inf")), up[stat] + STEPS[stat])
        down[stat] = max(0.0, down[stat] - STEPS[stat])
        span = up[stat] - down[stat]
        if span <= 0:
            continue
        slope = (run(up) - run(down)) / span
        w[stat] = slope / 100 if stat in ("crit", "hit") else slope
    for idx in weapon_idx:
        wpn = profile["weapons"][idx]
        up, down = copy.deepcopy(profile), copy.deepcopy(profile)
        up["weapons"][idx]["dmg"] = wpn["dmg"] + WEAPON_STEP * wpn["speed"]
        down["weapons"][idx]["dmg"] = max(0.0, wpn["dmg"] - WEAPON_STEP * wpn["speed"])
        span_dps = (up["weapons"][idx]["dmg"] - down["weapons"][idx]["dmg"]) / wpn["speed"]
        slope = (run(stats, up) - run(stats, down)) / span_dps
        w["wdps_r" if ranged else ("wdps_oh" if wpn.get("offhand") else "wdps_mh")] = slope
    for raw, kwarg in (("str", "str_"), ("agi", "agi"), ("int", "int_")):
        d = sim.stat_deltas_from_raw(spec_id, **{kwarg: 1}) or {}
        w[raw] = (d.get("ap", 0) * w["ap"] + d.get("sp", 0) * w["sp"]
                  + d.get("crit_pct", 0) * w["crit"] + d.get("hit_pct", 0) * w["hit"])
    # A negative weight can only be residual noise on a stat the rotation barely uses.
    return base, {k: round(max(0.0, v), 4) for k, v in w.items()}
