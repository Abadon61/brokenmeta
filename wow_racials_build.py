"""Racial abilities of every playable race of WoW: Forever, read from the beta client tables (nothing typed by hand).

For each race: its classes (CharBaseInfo, fetched from wago.tools into the raw cache) and the spells of its racial skill line
(SkillLineAbility), with the English / French tooltip resolved by the same renderer as the spell glossary (a text it cannot fully
compute is left null: the page then only shows the name), cast cooldown and duration. Writes data/wow_racials.json.

Usage: py wow_racials_build.py [--structure-build 1.60.1.70291] [--text-build 1.60.1.70170]
"""
import argparse
import csv
import io
import json
import re
from collections import defaultdict
from pathlib import Path

import wow_spell_glossary_build as gb
import wow_spell_ranks_build as rb
import wow_talents_import as imp

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "wow_talents_raw"
CLASS_BY_ID = {1: "warrior", 2: "paladin", 3: "hunter", 4: "rogue", 5: "priest", 7: "shaman", 8: "mage", 9: "warlock", 11: "druid"}
# ChrRaces.ID -> key used by the site (data/wow_races.json); the two Skyborne races share the key "skyborne" and are told apart by faction
RACE_KEY = {1: "human", 2: "orc", 3: "dwarf", 4: "nightelf", 5: "undead", 6: "tauren", 7: "gnome", 8: "troll", 95: "skyborne-alliance", 96: "skyborne-horde"}


def mask_has(row, race_id):
    """RaceMasks_0 holds the bit (race id - 1) of the original races; the Skyborne races (ids 95 and 96) are bits 0 and 1 of RaceMasks_1 (checked on the Skyborne racial skill line)."""
    if race_id >= 95:
        return bool((int(row.get("RaceMasks_1") or 0) >> (race_id - 95)) & 1)
    return bool((int(row.get("RaceMasks_0") or 0) >> (race_id - 1)) & 1)


def _duration_text(spell_id, lang, S):
    ms = rb.rank_record(spell_id, S)["duration_ms"]
    if ms <= 0:
        return f"${spell_id}d"            # no duration in the tables: the text stays unresolved (the page then shows the name only)
    return f"{ms / 1000:g} {'sec' if lang == 'en' else 's'}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--structure-build", default="1.60.1.70291")
    ap.add_argument("--text-build", default="1.60.1.70170")
    args = ap.parse_args()
    S = rb.load(args.structure_build, False)
    tt = gb.TextTables(args.text_build)
    sp = imp.Spells(tt)
    names = {lang: {r["ID"]: r["Name_lang"] for r in gb.rd(args.text_build, "SpellName", code)} for lang, code in imp.LOCALES.items()}
    spell_rows = {lang: gb.rd(args.text_build, "Spell", code) for lang, code in imp.LOCALES.items()}
    descs = {lang: {r["ID"]: r["Description_lang"] for r in rows} for lang, rows in spell_rows.items()}
    auras = {lang: {r["ID"]: r["AuraDescription_lang"] for r in rows} for lang, rows in spell_rows.items()}
    skill_names = {r["ID"]: r["DisplayName_lang"] for r in gb.rd("1.60.1.69913", "SkillLine")}
    racial_lines = {i for i, n in skill_names.items() if re.search(r"Racial", n)}
    xvars = defaultdict(list)
    for r in gb.rd("1.60.1.69913", "SpellXDescriptionVariables"):
        xvars[r["SpellID"]].append(r["SpellDescriptionVariablesID"])
    vtext = {r["ID"]: r["Variables"] for r in gb.rd("1.60.1.69913", "SpellDescriptionVariables")}
    var_defs = {}
    for sid_, ids_ in xvars.items():
        d_ = {}
        for vid in ids_:
            for line in vtext.get(vid, "").splitlines():
                m_ = re.match(r"\$(\w+)=(.*)", line.strip())
                if m_:
                    d_[m_.group(1)] = m_.group(2)
        var_defs[sid_] = d_
    renderers = {lang: gb.GlossaryRenderer(sp, names[lang], lang, descs[lang], var_defs) for lang in imp.LOCALES}
    icon_names = {r["ID"]: r["FileName"].rsplit(".", 1)[0].lower() for r in gb.rd(args.text_build, "ManifestInterfaceData") if r["FilePath"].lower().startswith("interface\icons")}
    misc = {}
    for r in tt.SpellMisc:
        if r.get("DifficultyID", "0") in ("0", ""):
            misc.setdefault(r["SpellID"], r)
    cls_rows = list(csv.DictReader(io.open(RAW / args.structure_build / "CharBaseInfo.csv", encoding="utf-8-sig")))
    out = {}
    for race_id, key in RACE_KEY.items():
        classes = sorted(CLASS_BY_ID[int(r["ClassID"])] for r in cls_rows if int(r["RaceID"]) == race_id and int(r["ClassID"]) in CLASS_BY_ID)
        spells, seen = [], set()
        for r in S["sla"]:
            if r["SkillLine"] not in racial_lines or not mask_has(r, race_id):
                continue
            sid = r["Spell"]
            nm = names["en"].get(sid)
            if not nm or sid in seen or not (descs["en"].get(sid) or auras["en"].get(sid)):
                continue
            seen.add(sid)
            rec = rb.rank_record(sid, S)
            ent = {"id": int(sid), "name": {"en": nm, "fr": names["fr"].get(sid) or nm}, "icon": icon_names.get((misc.get(sid) or {}).get("SpellIconFileDataID", "0")),
                   "cooldown_s": rec["cooldown_ms"] / 1000 if rec["cooldown_ms"] > 0 else None, "duration_s": rec["duration_ms"] / 1000 if rec["duration_ms"] > 0 else None,
                   "class_mask": rb.num(r.get("ClassMask"), int) or 0, "desc": {}}
            ok = True
            for lang in imp.LOCALES:
                text = descs[lang].get(sid) or auras[lang].get(sid) or ""
                text = re.sub(r"\$(\d+)d", lambda m_, lang=lang: _duration_text(m_.group(1), lang, S), text)       # "$26635d": duration of another spell (Berserking's aura)
                rendered, good = renderers[lang].render(text, sid, {}) if text else (None, False)
                ent["desc"][lang] = rendered if good else None
                ok = ok and good
            ent["desc_ok"] = ok
            spells.append(ent)
        out[key] = {"race_id": race_id, "classes": classes, "spells": spells}
    (ROOT / "data" / "wow_racials.json").write_text(json.dumps({"_source": f"WoW: Forever client tables (via wago.tools): structure build {args.structure_build}, texts build {args.text_build}", "races": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in out.items():
        print(k, v["classes"], [f"{s['name']['en']}{'' if s['desc_ok'] else '?'}" for s in v["spells"]])


if __name__ == "__main__":
    main()
