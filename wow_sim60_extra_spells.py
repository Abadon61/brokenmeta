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
    "hunter": ["Raptor Strike", "Mongoose Bite", "Wing Clip", "Strider Kick", "Counterattack", "Multi-Shot", "Steady Shot", "Hunter's Mark", "Serpent Sting", "Arcane Shot", "Aimed Shot"],
    "mage": ["Arcane Missiles", "Arcane Blast", "Ice Lance", "Frostfire Bolt", "Scorch"],
    "warrior": ["Shield Slam", "Revenge", "Shield Block", "Thunder Clap", "Sunder Armor", "Heroic Strike", "Shield Bash", "Concussion Blow", "Taunt", "Devastate", "Last Stand", "Shield Wall"],
    "priest": ["Mind Flay", "Shadow Word: Death", "Devouring Plague", "Holy Fire", "Penance", "Shadowform", "Vampiric Embrace", "Power Infusion", "Inner Focus", "Smite", "Shadow Word: Pain", "Mind Blast"],
    "shaman": ["Chain Lightning", "Lava Burst", "Stormstrike", "Windfury Weapon", "Flametongue Weapon", "Fire Nova", "Lightning Shield", "Earth Shock", "Flame Shock", "Lightning Bolt", "Searing Totem", "Magma Totem", "Rockbiter Weapon", "Frost Shock"],
    "paladin": ["Seal of Command", "Seal of Righteousness", "Holy Shock", "Hammer of Wrath", "Exorcism", "Holy Strike", "Judgement", "Consecration", "Crusader Strike", "Holy Wrath", "Judgement of Command", "Judgement of Righteousness", "Holy Shield", "Righteous Fury", "Seal of Fury", "Judgement of Light", "Judgement of Wisdom", "Hammer of the Righteous", "Avenger's Shield", "Blessing of Sanctuary"],
    "druid": ["Starfire", "Insect Swarm", "Wrath", "Moonfire", "Shred", "Rake", "Ferocious Bite", "Ravage", "Claw", "Rip", "Primal Bite", "Berserk", "Tiger's Fury", "Swipe", "Maul", "Lacerate", "Growl", "Savage Bite", "Demoralizing Roar", "Bash", "Enrage"],
}
# spells that are not on a class skill line of the glossary (talent / passive spells): explicit client spell ids, highest rank at level 60
SEEDS = {
    "shaman": {"Searing Bolt": 10436, "Magma Totem Pulse": 10581, "Fire Nova Damage": 408428, "Windfury Weapon Proc": 16361, "Frostbrand Attack": 16353, "Lightning Shield Damage": 432149},
    "paladin": {"Holy Shield": 20928, "Righteous Fury": 25780, "Hammer of the Righteous": 407632},
    "mage": {"Arcane Blast": 1239700, "Arcane Blast Stacks": 400573, "Arcane Missiles": 25345, "Arcane Missiles Tick": 25346},
    "druid": {"Savage Roar": 407988, "Tiger's Fury": 5217, "Tiger's Fury Energy": 417045, "Tiger's Fury Damage": 1289238, "Shifting Power": 1322605},
}


# spells missing from the class skill lines: highest rank (learn level <= 60) among ALL client spells of that name
GLOBAL = {"hunter": ["Raptor Strike", "Mongoose Bite", "Wing Clip", "Strider Kick"]}


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
        for n in GLOBAL.get(cls, []):
            ids = [sid for sid, nm in T["names"].items() if nm == n and R.num(T["levels"].get(sid, {}).get("BaseLevel"), int) > 0]
            ids.sort(key=lambda x: (R.num(T["levels"].get(x, {}).get("BaseLevel"), int), R.num(x, int)))
            recs = [R.rank_record(x, T) for x in ids]
            recs = [r for r in recs if r["level"] <= 60]
            if recs:
                found[n] = ([r for r in recs if r.get("cost")] or recs)[-1]
        for n, sid in SEEDS.get(cls, {}).items():
            found[n] = R.rank_record(str(sid), T)
        for n, rec in found.items():           # percent-of-base-mana costs live in a separate column
            pct = T["power"].get(str(rec["spell_id"]), {}).get("PowerCostPct")
            if pct not in (None, "", "0"):
                rec["cost_pct"] = R.num(pct, int)
        out[cls] = found
    return out


if __name__ == "__main__":
    res = extra_spells()
    for cls, d in res.items():
        print("==", cls)
        for n, r in d.items():
            e = " ".join(f"{x['effect']}/{x['aura']}/{x['base']:g}v{x['variance']:.2f}pl{x['per_level']:.1f}p{x['period_ms']}sp{x['sp_coeff']}ap{x['ap_coeff']}" for x in r["effects"])
            print(f"  {n:24s} L{r['spell_level']:<3d} cost {r['cost'] and r['cost']['amount']} cast {r['cast_ms']} cd {r['cooldown_ms']} dur {r['duration_ms']} | {e}")
