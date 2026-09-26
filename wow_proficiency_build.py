"""Which armor/weapon types each class can equip in WoW: Forever, and from which level.

Read from the beta client's own tables (SkillRaceClassInfo + the armor/weapon SkillLine ids),
the same data_raw folder wow_talents_import.py downloads, and written to
data/wow_items/proficiency.json (committed) for the BrokenMeta addon's upgrade filters.

Usage: py -3.11 wow_proficiency_build.py [path/to/data/wow_talents_raw/<build>]
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "wow_items" / "proficiency.json"

# SkillLine ids of the armor and weapon skills, keyed by the site's item "type" names
# (data/wow_dungeons/dungeons.json uses these English type strings).
SKILLS = {
    415: "Cloth", 414: "Leather", 413: "Mail", 293: "Plate Mail", 433: "Shield",
    43: "Swords", 55: "Two-Handed Swords", 44: "Axes", 172: "Two-Handed Axes", 54: "Maces",
    160: "Two-Handed Maces", 229: "Polearms", 136: "Staves", 173: "Daggers", 473: "Fist Weapons",
    45: "Bows", 46: "Guns", 226: "Crossbows", 176: "Thrown", 228: "Wands",
}
CLASS_BITS = {1: "WARRIOR", 2: "PALADIN", 4: "HUNTER", 8: "ROGUE", 16: "PRIEST", 64: "SHAMAN",
              128: "MAGE", 256: "WARLOCK", 1024: "DRUID"}


def main():
    if len(sys.argv) > 1:
        raw = Path(sys.argv[1])
    else:
        candidates = sorted((ROOT / "data" / "wow_talents_raw").glob("*/SkillRaceClassInfo.csv"))
        if not candidates:
            sys.exit("SkillRaceClassInfo.csv not found: pass the raw client table folder")
        raw = candidates[-1].parent
    out = {c: {} for c in CLASS_BITS.values()}
    with open(raw / "SkillRaceClassInfo.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            skill = SKILLS.get(int(r["SkillID"]))
            if not skill:
                continue
            mask, level = int(r["ClassMask"]), int(r["MinLevel"] or 0)
            for bit, cls in CLASS_BITS.items():
                if mask == -1 or mask & bit:
                    out[cls][skill] = min(level, out[cls].get(skill, level))
    OUT.write_text(json.dumps({
        "_source": f"WoW: Forever beta client tables SkillRaceClassInfo + SkillLine ({raw.name}); "
                   "value = minimum character level to use that armor/weapon type.",
        "classes": {c: dict(sorted(v.items())) for c, v in out.items()},
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
