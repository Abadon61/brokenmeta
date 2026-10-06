"""Level-60 healing spells from the beta client tables (highest rank learnable by level 60) -> data/wow_guides/healing60.json.
Used by the healing specs' guide pages: the spell efficiency table (healing per cast, per second and per mana, computed at build time at a stated
healing power) and the data-based priority. Spells without a clean number in the client (talent spells whose heal is a dummy effect) are listed
with `numbers: false`.

    py -3.11 wow_healing_build.py
"""
import json
import sys
from pathlib import Path

import wow_spell_ranks_build as R
import wow_talents_import as imp

OUT = Path(__file__).parent / "data" / "wow_guides" / "healing60.json"

# class -> [(spell name, targets, multi-target note key or None, group)]  targets: how many targets the full amount reaches (1 = single target)
SPELLS = {
    "priest": [("Greater Heal", 1, None), ("Flash Heal", 1, None), ("Heal", 1, None), ("Renew", 1, None), ("Prayer of Healing", 5, "party"), ("Binding Heal", 2, "self"), ("Power Word: Shield", 1, "absorb")],
    "paladin": [("Flash of Light", 1, None), ("Holy Light", 1, None)],
    "shaman": [("Healing Wave", 1, None), ("Lesser Healing Wave", 1, None), ("Chain Heal", 1, "chain"), ("Riptide", 1, None)],
    "druid": [("Healing Touch", 1, None), ("Regrowth", 1, None), ("Rejuvenation", 1, None), ("Wild Growth", 5, "party")],
}
# talent / special spells shown without numbers (their client heal is a dummy effect or a bounce count we do not have)
SPECIAL = {
    "priest": ["Prayer of Mending", "Penance", "Holy Nova", "Power Infusion"],
    "paladin": ["Holy Shock", "Light's Vigil", "Divine Favor", "Lay on Hands"],
    "shaman": ["Water Shield", "Mana Tide Totem", "Healing Stream Totem", "Nature's Swiftness"],
    "druid": ["Swiftmend", "Tranquility", "Nature's Swiftness", "Thorns"],
}


def main():
    T = R.load(imp.latest_beta_build(), False)
    out = {"build": imp.latest_beta_build(), "classes": {}}
    for cls, spells in SPELLS.items():
        rows = []
        for name, targets, note in spells:
            ids = [s for s, nm in T["names"].items() if nm == name]
            recs = [R.rank_record(s, T) for s in ids]
            ok = [r for r in recs if r["spell_level"] <= 60 and r.get("cost")]
            if not ok:
                print("missing", cls, name, file=sys.stderr)
                continue
            ok.sort(key=lambda r: (r["spell_level"], r["spell_id"]))
            r = ok[-1]
            lvl_pts = lambda e: e["base"] + e["per_level"] * max(0, min(60, r["max_level"] or 60) - r["spell_level"])
            direct = next((e for e in r["effects"] if e["effect"] == 10), None)
            hot = next((e for e in r["effects"] if e["effect"] == 6 and e["aura"] == 8 and e["period_ms"] > 0), None)
            absorb = next((e for e in r["effects"] if e["effect"] == 6 and e["aura"] == 69), None)
            row = {"name": name, "spell_id": r["spell_id"], "cast": r["cast_ms"] / 1000, "cost": r["cost"]["amount"], "targets": targets, "note": note, "cd": r["cooldown_ms"] / 1000}
            if direct:
                row["direct"] = {"base": round(lvl_pts(direct), 1), "coeff": direct["sp_coeff"]}
            if hot:
                row["hot"] = {"tick": round(lvl_pts(hot), 1), "coeff": hot["sp_coeff"], "ticks": max(1, round(r["duration_ms"] / hot["period_ms"])), "interval": hot["period_ms"] / 1000}
            if absorb:
                row["absorb"] = {"base": round(lvl_pts(absorb), 1), "coeff": absorb["sp_coeff"]}
            if not (direct or hot or absorb):
                print("no heal effect", cls, name, file=sys.stderr)
                continue
            rows.append(row)
        out["classes"][cls] = {"spells": rows, "special": SPECIAL[cls]}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for cls, d in out["classes"].items():
        print(cls, [x["name"] for x in d["spells"]])


if __name__ == "__main__":
    main()
