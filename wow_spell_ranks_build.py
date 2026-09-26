"""Every rank of every ability the DPS simulator uses, read from the WoW: Forever beta client tables.

For each ability in data/wow_spells/<class>.json (the level-20 glossary, sourced from Wowhead
tooltips), finds all its ranks in the client (same spell name in the same class skill line),
with the level each rank is learned and its raw numbers, and writes
data/wow_spells_ranks/<class>.json. site_build/wow_dps_sim.py uses these files to simulate any
character level (the glossary stays the source of the ability's structure and rotation role).

Client formulas (checked against the glossary's Wowhead values, see --check):
  points(level) = EffectBasePointsF + EffectRealPointsPerLevel x (min(level, MaxLevel) - SpellLevel)
  damage range  = points +/- EffectBasePointsF x Variance / 2
Tables come from wago.tools (same source and download helper as wow_talents_import.py).

Usage: py -3.11 wow_spell_ranks_build.py [--build 1.60.1.xxxxx] [--refresh]
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import wow_talents_import as imp

ROOT = Path(__file__).resolve().parent
GLOSSARY_DIR = ROOT / "data" / "wow_spells"
OUT_DIR = ROOT / "data" / "wow_spells_ranks"
TABLES = ["SkillLineAbility", "SpellLevels", "SpellEffect", "SpellName", "SpellMisc", "SpellPower",
          "SpellCastTimes", "SpellCooldowns", "SpellDuration"]
POWER_TYPES = {0: "mana", 1: "rage", 3: "energy"}


def num(v, cast=float):
    try:
        return cast(float(v))
    except (TypeError, ValueError):
        return cast(0)


def load(build, refresh):
    t = {name: imp.read(imp.fetch(name, build, None, refresh)) for name in TABLES}
    effects = defaultdict(list)
    for e in t["SpellEffect"]:
        if num(e.get("DifficultyID"), int) == 0:
            effects[e["SpellID"]].append(e)
    return {
        "sla": t["SkillLineAbility"],
        "levels": {r["SpellID"]: r for r in t["SpellLevels"] if num(r.get("DifficultyID"), int) == 0},
        "effects": effects,
        "names": {r["ID"]: r.get("Name_lang", "") for r in t["SpellName"]},
        "misc": {r["SpellID"]: r for r in t["SpellMisc"] if num(r.get("DifficultyID"), int) == 0},
        # A spell can have several costs (Eviscerate: Energy + combo points): keep the main resource.
        "power": {r["SpellID"]: r for r in sorted(t["SpellPower"], key=lambda r: num(r.get("PowerType"), int) in POWER_TYPES)},
        "cast": {r["ID"]: r for r in t["SpellCastTimes"]},
        "cooldown": {r["SpellID"]: r for r in t["SpellCooldowns"] if num(r.get("DifficultyID"), int) == 0},
        "duration": {r["ID"]: r for r in t["SpellDuration"]},
    }


def ranks_of(spell_id, T):
    """All spells sharing this spell's name within its class skill line(s), by learn level."""
    lines = {r["SkillLine"] for r in T["sla"] if r["Spell"] == spell_id}
    name = T["names"].get(spell_id)
    ids = {r["Spell"] for r in T["sla"] if r["SkillLine"] in lines and T["names"].get(r["Spell"]) == name}
    ids.add(spell_id)
    return sorted(ids, key=lambda s: (num(T["levels"].get(s, {}).get("BaseLevel"), int), num(s, int)))


def rank_record(sid, T):
    lv = T["levels"].get(sid, {})
    misc = T["misc"].get(sid, {})
    pw = T["power"].get(sid, {})
    cd = T["cooldown"].get(sid, {})
    cast = T["cast"].get(misc.get("CastingTimeIndex", ""), {})
    dur = T["duration"].get(misc.get("DurationIndex", ""), {})
    return {
        "spell_id": num(sid, int),
        "level": num(lv.get("BaseLevel"), int),
        "spell_level": num(lv.get("SpellLevel"), int),
        "max_level": num(lv.get("MaxLevel"), int),
        "cost": {"type": POWER_TYPES.get(num(pw.get("PowerType"), int), pw.get("PowerType")),
                 "amount": num(pw.get("ManaCost"), int)} if pw else None,
        "cast_ms": num(cast.get("Base"), int),
        "cooldown_ms": max(num(cd.get("RecoveryTime"), int), num(cd.get("CategoryRecoveryTime"), int)),
        "duration_ms": num(dur.get("Duration"), int),
        "effects": [{
            "index": num(e["EffectIndex"], int), "effect": num(e["Effect"], int), "aura": num(e["EffectAura"], int),
            "base": num(e["EffectBasePointsF"]), "variance": num(e["Variance"]),
            "per_level": num(e["EffectRealPointsPerLevel"]), "period_ms": num(e["EffectAuraPeriod"], int),
            "per_resource": num(e["EffectPointsPerResource"]),
            "sp_coeff": round(num(e["EffectBonusCoefficient"]), 4), "ap_coeff": round(num(e["BonusCoefficientFromAP"]), 4),
        } for e in sorted(T["effects"].get(sid, []), key=lambda e: num(e["EffectIndex"], int))],
    }


def points(eff, rank, level):
    lvl = min(level, rank["max_level"]) if rank["max_level"] else level
    return eff["base"] + eff["per_level"] * max(0, lvl - rank["spell_level"])


def check(cls, glossary, ranks_by_ability):
    """Prints the client-formula value at level 20 next to each glossary (Wowhead) value."""
    for ab in glossary["abilities"]:
        ranks = ranks_by_ability.get(ab["id"])
        if not ranks:
            continue
        rank = next((r for r in ranks if r["spell_id"] == ab.get("wowhead_spell_id")), None)
        if not rank:
            continue
        for g_eff, c_eff in zip([e for e in ab["effects"] if "dmg_range" in e or "damage_per_tick" in e],
                                [e for e in rank["effects"] if e["effect"] in (2, 6)]):
            p = points(c_eff, rank, 20)
            half = c_eff["base"] * c_eff["variance"] / 2
            client = f"{p - half:.0f}-{p + half:.0f}" if half else f"{p:.0f}"
            gloss = g_eff.get("dmg_range") or g_eff.get("damage_per_tick")
            print(f"  {cls:8s} {ab['id']:30s} glossary {gloss!s:12s} client@20 {client}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", default=None)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--check", action="store_true", help="print level-20 client values next to the glossary")
    args = ap.parse_args()
    build = args.build or imp.latest_beta_build()
    print(f"build {build}")
    T = load(build, args.refresh)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for f in sorted(GLOSSARY_DIR.glob("*.json")):
        glossary = json.loads(f.read_text(encoding="utf-8"))
        out = {}
        for ab in glossary.get("abilities", []):
            sid = str(ab.get("wowhead_spell_id") or "")
            if not sid or sid not in T["names"]:
                continue
            out[ab["id"]] = [rank_record(s, T) for s in ranks_of(sid, T)]
        (OUT_DIR / f.name).write_text(json.dumps({
            "_source": f"WoW: Forever beta client tables, build {build} (via wago.tools): SkillLineAbility, "
                       "SpellLevels, SpellEffect, SpellPower, SpellCastTimes, SpellCooldowns, SpellDuration.",
            "build": build, "abilities": out,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        n_ranks = sum(len(v) for v in out.values())
        print(f"{f.stem:8s} {len(out)} abilities, {n_ranks} ranks")
        if args.check:
            check(f.stem, glossary, out)


if __name__ == "__main__":
    main()
