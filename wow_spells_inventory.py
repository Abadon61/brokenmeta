"""Inventory of the class abilities learned AFTER level 20, read from the WoW: Forever client tables.

The DPS simulator only models the level-20 kit (data/wow_spells/<class>.json, every value sourced
from Wowhead's Forever tooltips) plus the higher ranks of those same abilities
(data/wow_spells_ranks/). This lists what the client holds for levels 21-60: every ability of the
class's skill lines first learned in that range, its ranks, and what kind of effect it has, so the
work to simulate higher levels is known and the raw numbers are ready. It does NOT add anything to
the simulator: a new ability needs its rotation role sourced first (see data/wow_spells/README.md).

Writes data/wow_spells_future/<class>.json and prints a summary.
Usage: py -3.11 wow_spells_inventory.py [--build 1.60.1.xxxxx] [--max-level 60]
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import wow_spell_ranks_build as rb
import wow_talents_import as imp

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "data" / "wow_spells_future"

# SpellEffect.Effect codes -> what the simulator would need to model.
DIRECT, WEAPON = {2}, {17, 31, 58, 121}
PERIODIC_DAMAGE_AURAS = {3, 89}  # periodic damage, periodic damage % max health


def kind_of(rank):
    kinds = set()
    for e in rank["effects"]:
        if e["effect"] in DIRECT:
            kinds.add("direct")
        elif e["effect"] in WEAPON:
            kinds.add("weapon")
        elif e["effect"] == 6 and e["aura"] in PERIODIC_DAMAGE_AURAS:
            kinds.add("periodic")
    return "+".join(sorted(kinds)) or "other"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", default=None)
    ap.add_argument("--max-level", type=int, default=60)
    args = ap.parse_args()
    build = args.build or imp.latest_beta_build()
    T = rb.load(build, False)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"build {build}")
    for f in sorted(rb.GLOSSARY_DIR.glob("*.json")):
        glossary = json.loads(f.read_text(encoding="utf-8"))
        known_ids = {str(a.get("wowhead_spell_id")) for a in glossary.get("abilities", []) if a.get("wowhead_spell_id")}
        # The class's skill lines: those holding its level-20 abilities.
        lines = {r["SkillLine"] for r in T["sla"] if r["Spell"] in known_ids}
        known_names = {T["names"].get(s) for s in known_ids}
        by_name = defaultdict(list)
        for r in T["sla"]:
            sid = r["Spell"]
            if r["SkillLine"] not in lines or sid not in T["levels"]:
                continue
            name = T["names"].get(sid)
            if not name or name in known_names:
                continue
            by_name[name].append(sid)
        out = []
        for name, ids in by_name.items():
            ranks = [rb.rank_record(s, T) for s in sorted(set(ids), key=lambda s: rb.num(T["levels"][s].get("BaseLevel"), int))]
            first = ranks[0]["level"]
            if not (20 < first <= args.max_level):
                continue
            out.append({"name": name, "first_level": first, "kind": kind_of(ranks[0]),
                        "ranks": [r for r in ranks if r["level"] <= args.max_level]})
        out.sort(key=lambda a: (a["first_level"], a["name"]))
        (OUT_DIR / f.name).write_text(json.dumps({
            "_source": f"WoW: Forever client tables, build {build} (via wago.tools). Abilities of the class's "
                       f"skill lines first learned between levels 21 and {args.max_level}; not simulated yet.",
            "build": build, "abilities": out,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        counts = defaultdict(int)
        for a in out:
            counts[a["kind"]] += 1
        print(f"{f.stem:8s} {len(out):3d} new abilities 21-{args.max_level}: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
        for a in out:
            if a["kind"] != "other":
                print(f"           {a['first_level']:2d}  {a['kind']:16s} {a['name']}")


if __name__ == "__main__":
    main()
