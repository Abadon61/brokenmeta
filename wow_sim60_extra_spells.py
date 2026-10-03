"""Looks up spells by NAME in the beta client tables for the simulator: the spells a talent grants (Mind Flay, Lava Burst, Starfire...)
are not in the spell glossary, so their rank ladder is rebuilt here with the same tables and rules as wow_spell_ranks_build.py
(spells of the same name inside the class's skill lines, ranked by learn level, highest rank learnable by level 60 kept).

    py -3.11 wow_sim60_extra_spells.py            # prints what it finds
Imported by wow_sim60_export.py (function `extra_spells`).
"""
import json
from collections import defaultdict

import wow_spell_ranks_build as R
import wow_talents_import as imp

EXTRA = {
    "priest": ["Mind Flay", "Shadow Word: Death", "Devouring Plague", "Holy Fire", "Penance", "Shadowform", "Vampiric Embrace", "Power Infusion", "Inner Focus", "Smite", "Shadow Word: Pain", "Mind Blast"],
    "shaman": ["Chain Lightning", "Lava Burst", "Stormstrike", "Windfury Weapon", "Flametongue Weapon", "Fire Nova", "Lightning Shield", "Earth Shock", "Flame Shock", "Lightning Bolt", "Searing Totem", "Magma Totem", "Rockbiter Weapon"],
    "paladin": ["Seal of Command", "Seal of Righteousness", "Holy Shock", "Hammer of Wrath", "Exorcism", "Holy Strike", "Judgement", "Consecration", "Crusader Strike", "Holy Wrath", "Judgement of Command", "Judgement of Righteousness"],
    "druid": ["Starfire", "Insect Swarm", "Wrath", "Moonfire", "Shred", "Rake", "Ferocious Bite", "Ravage", "Claw", "Rip", "Primal Bite", "Berserk", "Tiger's Fury", "Swipe", "Maul", "Lacerate"],
}


def extra_spells(build=None, refresh=False):
    build = build or imp.latest_beta_build()
    T = R.load(build, refresh)
    # class skill lines: the lines of every glossary ability of the class (rank ladders already known)
    out = {}
    for cls, names in EXTRA.items():
        gloss = json.loads((R.GLOSSARY_DIR / f"{cls}.json").read_text(encoding="utf-8"))
        lines = set()
        for ab in gloss.get("abilities", []):
            sid = str(ab.get("wowhead_spell_id") or "")
            lines |= {r["SkillLine"] for r in T["sla"] if r["Spell"] == sid}
        by_name = defaultdict(set)
        for r in T["sla"]:
            if r["SkillLine"] in lines:
                n = T["names"].get(r["Spell"])
                if n in names:
                    by_name[n].add(r["Spell"])
        found = {}
        for n in names:
            ids = sorted(by_name.get(n, []), key=lambda s: (R.num(T["levels"].get(s, {}).get("BaseLevel"), int), R.num(s, int)))
            recs = [R.rank_record(s, T) for s in ids]
            ok = [r for r in recs if r["spell_level"] <= 60 and r["level"] <= 60]
            if ok:
                withcost = [r for r in ok if r.get("cost")]
                found[n] = (withcost or ok)[-1]
        out[cls] = found
    return out


if __name__ == "__main__":
    res = extra_spells()
    for cls, d in res.items():
        print("==", cls)
        for n, r in d.items():
            e = " ".join(f"{x['effect']}/{x['aura']}/{x['base']:g}v{x['variance']:.2f}pl{x['per_level']:.1f}p{x['period_ms']}sp{x['sp_coeff']}ap{x['ap_coeff']}" for x in r["effects"])
            print(f"  {n:24s} L{r['spell_level']:<3d} cost {r['cost'] and r['cost']['amount']} cast {r['cast_ms']} cd {r['cooldown_ms']} dur {r['duration_ms']} | {e}")
