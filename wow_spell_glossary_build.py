"""Public spell glossary: EVERY class ability up to level 60, read from the WoW: Forever client tables.

For each class, lists every spell of the class's skill lines (the three spec lines) first learned at level 1-60, with
its ranks, the highest rank available at level 60 and that rank's cost, cooldown, cast time and tooltip text in French
and English. Tooltip variables ($s1, $d, ...) are computed from the spell tables by wow_talents_import.Renderer (the
same resolver as the talent calculator); a text the resolver cannot fully compute is NOT shown (flagged "desc_ok": false,
the page then relies on the Wowhead tooltip on hover). Nothing is typed by hand.

Writes data/wow_spells_all/<class>.json. Raw tables are read from the cache data/wow_talents_raw/<build>/ (git-ignored).
Two builds are mixed on purpose (both cached): STRUCTURE_BUILD gives the skill lines, levels, costs, cooldowns and cast
times; TEXT_BUILD gives the localized names/tooltips and the effect tables the text variables need.

Usage: py wow_spell_glossary_build.py [--structure-build 1.60.1.70291] [--text-build 1.60.1.70170]
"""
import argparse
import csv
import io
import json
import re
from collections import defaultdict
from pathlib import Path

import wow_spell_ranks_build as rb
import wow_talents_import as imp

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "data" / "wow_spells_all"
RAW = ROOT / "data" / "wow_talents_raw"
MAX_LEVEL = 60
# ChrClasses ClassMask bit of each class we publish (death knights do not exist in WoW: Forever).
CLASS_MASK = {"warrior": 1, "paladin": 2, "hunter": 4, "rogue": 8, "priest": 16, "shaman": 64, "mage": 128, "warlock": 256, "druid": 1024}
# Skill lines that are not the class's own spell book: engraving recipes, racial and defensive states, professions.
SKIP_LINES = ("Engraving", "Defense", "Racial", "Language", "Riding")
SKIP_NAME = re.compile(r"\((?:DND|NYI)\)|^Engrave |Passive$|^None$", re.I)
RESOURCE = {"mana": "mana", "rage": "rage", "energy": "energy"}
# SpellMisc.SchoolMask bits -> school of the spell (single-school spells only; a multi-school mask stays null).
SCHOOLS = {1: "physical", 2: "holy", 4: "fire", 8: "nature", 16: "frost", 32: "shadow", 64: "arcane"}


def rd(build, table, locale=None):
    p = RAW / build / f"{table}{'.' + locale if locale else ''}.csv"
    with io.open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class TextTables:
    """The attributes wow_talents_import.Spells reads."""

    def __init__(self, build):
        for t in ("SpellEffect", "SpellDuration", "SpellMisc", "SpellAuraOptions", "SpellRadius", "CurvePoint"):
            setattr(self, t, rd(build, t))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--structure-build", default="1.60.1.70291")
    ap.add_argument("--text-build", default="1.60.1.70170")
    args = ap.parse_args()
    S = rb.load(args.structure_build, False)                     # skill lines, levels, costs, cooldowns, cast times
    tt = TextTables(args.text_build)
    sp = imp.Spells(tt)
    names = {lang: {r["ID"]: r["Name_lang"] for r in rd(args.text_build, "SpellName", code)} for lang, code in imp.LOCALES.items()}
    spell_rows = {lang: rd(args.text_build, "Spell", code) for lang, code in imp.LOCALES.items()}
    descs = {lang: {r["ID"]: r["Description_lang"] for r in rows} for lang, rows in spell_rows.items()}
    auras = {lang: {r["ID"]: r["AuraDescription_lang"] for r in rows} for lang, rows in spell_rows.items()}
    subtext = {r["ID"]: r["NameSubtext_lang"] for r in spell_rows["en"]}
    skill_names = {lang: {r["ID"]: r["DisplayName_lang"] for r in rd("1.60.1.69913", "SkillLine", code)} for lang, code in imp.LOCALES.items()}
    renderers = {lang: imp.Renderer(sp, names[lang], lang, descs[lang]) for lang in imp.LOCALES}
    icon_names = {r["ID"]: r["FileName"].rsplit(".", 1)[0].lower() for r in rd(args.text_build, "ManifestInterfaceData") if r["FilePath"].lower().startswith("interface\icons")}
    misc = {}
    for r in tt.SpellMisc:
        if r.get("DifficultyID", "0") in ("0", ""):
            misc.setdefault(r["SpellID"], r)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for cls, mask in CLASS_MASK.items():
        rows = [r for r in S["sla"] if rb.num(r.get("ClassMask"), int) == mask]
        lines = {r["SkillLine"] for r in rows if not skill_names["en"].get(r["SkillLine"], "").startswith(SKIP_LINES)}
        by_name = defaultdict(list)
        for r in rows:
            sid = r["Spell"]
            name = S["names"].get(sid)
            if r["SkillLine"] not in lines or not name or SKIP_NAME.search(name):
                continue
            by_name[(name, r["SkillLine"])].append(sid)
        # Spells granted by a talent (Mortal Strike, Bloodthirst, ...): flagged, they are learned from the tree, not at a level.
        talents = {}
        tf = ROOT / "data" / "wow_talents" / f"{cls}.json"
        if tf.exists():
            for spec in json.loads(tf.read_text(encoding="utf-8")).get("specs", []):
                for t in spec.get("talents", []):
                    talents[t["name"]["en"]] = spec["name"]
        out, problems = [], []
        for (name, line), ids in by_name.items():
            recs = sorted((rb.rank_record(s, S) for s in set(ids)), key=lambda x: (x["level"], x["spell_id"]))
            learned = [x for x in recs if 0 < x["level"] <= MAX_LEVEL]
            engraved = [x for x in recs if x["level"] == 0]
            if not learned and not engraved:
                continue
            top = (learned or engraved)[-1]
            sid = str(top["spell_id"])
            if not (descs["en"].get(sid) or auras["en"].get(sid)):
                continue                                         # no text at all: an internal / passive helper spell
            entry = {"id": top["spell_id"], "name": {"en": names["en"].get(sid, name), "fr": names["fr"].get(sid) or names["en"].get(sid, name)},
                     "line": {"en": skill_names["en"].get(line), "fr": skill_names["fr"].get(line) or skill_names["en"].get(line)},
                     "level": learned[0]["level"] if learned else None, "max_rank_level": top["level"] or None,
                     "ranks": len(learned) or 1, "engraved": not learned,
                     "cost": ({"type": top["cost"]["type"], "amount": (top["cost"]["amount"] // 10 if top["cost"]["type"] == "rage" else top["cost"]["amount"])}
                              if top["cost"] and top["cost"]["amount"] else None),
                     "cast_s": top["cast_ms"] / 1000 if top["cast_ms"] > 0 else 0,      # a negative base is a placeholder row: instant
                     "cooldown_s": top["cooldown_ms"] / 1000 if top["cooldown_ms"] > 0 else None,
                     "duration_s": top["duration_ms"] / 1000 if top["duration_ms"] > 0 else None,   # -1 = until cancelled: not shown
                     "icon": icon_names.get((misc.get(sid) or {}).get("SpellIconFileDataID", "0")),
                     "school": SCHOOLS.get(rb.num((misc.get(sid) or {}).get("SchoolMask"), int)),
                     "talent": talents.get(names["en"].get(sid, name)),
                     # SPELL_ATTR1_CHANNELED_1 / _2: a channelled spell has no cast time, it channels for its duration.
                     "channeled": bool(rb.num((misc.get(sid) or {}).get("Attributes_1"), int) & 0x44)}
            ok_all = True
            for lang in imp.LOCALES:
                text = descs[lang].get(sid) or ""
                if not text:
                    entry.setdefault("desc", {})[lang] = None
                    continue
                rendered, ok = renderers[lang].render(text, sid, {})
                ok_all = ok_all and ok
                entry.setdefault("desc", {})[lang] = rendered if ok else None
            entry["desc_ok"] = ok_all and bool(entry["desc"]["en"])
            if not entry["desc_ok"]:
                problems.append(entry["name"]["en"])
            out.append(entry)
        out.sort(key=lambda e: (e["level"] if e["level"] is not None else 99, e["name"]["en"]))
        (OUT_DIR / f"{cls}.json").write_text(json.dumps({
            "_source": f"WoW: Forever client tables (via wago.tools): structure from build {args.structure_build}, "
                       f"texts from build {args.text_build}. Every ability of the class's spec skill lines learned at levels 1-{MAX_LEVEL}, "
                       "highest rank available at level 60.",
            "class": cls, "abilities": out}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{cls:8s} {len(out):3d} abilities, {len(out) - len(problems):3d} with a fully resolved text; unresolved: {', '.join(problems[:6])}{'…' if len(problems) > 6 else ''}")


if __name__ == "__main__":
    main()
