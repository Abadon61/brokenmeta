"""Enchantments of the beta (Enchanting recipes up to the skill cap) with the stats they give, for the simulator and the guides.
Source: the Enchanting recipes (data/wow_professions/enchanting.json) + the client tables SpellEffect / SpellItemEnchantment (wago.tools, same build as the
other pipelines). Writes data/wow_enchants60.json and a copy under site_build/sim60/data/.

    py -3.11 wow_enchants_build.py

Only the enchantments whose effect is a flat stat (or a flat weapon damage) are valued; enchantments that proc a spell (Crusader, Fiery Weapon...) are listed
with `"proc": true` and no stats: the simulator does not value them.
"""
import json
import re
from pathlib import Path

import wow_spell_ranks_build as R
import wow_talents_import as imp

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "wow_enchants60.json"
OUT_SIM = ROOT / "site_build" / "sim60" / "data" / "enchants60.json"

# recipe name prefix -> slots of the simulator it can go on
SLOT_OF = {"Chest": ["chest"], "Bracer": ["wrist"], "Cloak": ["back"], "Gloves": ["hands"], "Boots": ["feet"], "Shield": ["shield"], "Necklace": ["neck"],
           "Weapon": ["mh", "oh"], "2H Weapon": ["th"], "Off-Hand": ["held"], "Ring": ["ring1", "ring2"]}
ARG_STAT = {3: "agi", 4: "str", 5: "int", 6: "spi", 7: "sta", 38: "atkpwr", 45: "splpwr"}              # EffectArg of an "item stat" effect
NAME_STAT = [(re.compile(r"\bStrength \+(\d+)"), "str"), (re.compile(r"\bAgility \+(\d+)"), "agi"), (re.compile(r"\bIntellect \+(\d+)"), "int"),
             (re.compile(r"\bSpirit \+(\d+)"), "spi"), (re.compile(r"\bStamina \+(\d+)"), "sta"), (re.compile(r"\bSpell Power \+(\d+)"), "splpwr"),
             (re.compile(r"Damage Spells \+(\d+)"), "splpwr"), (re.compile(r"Mana Regen (\d+) per 5"), "mp5"), (re.compile(r"Weapon Damage \+(\d+)"), "wdmg")]


def stats_of(ench):
    """Flat stats of one SpellItemEnchantment row, {} when it only procs / gives resistances / defense."""
    name = ench.get("Name_lang", "")
    st = {}
    for i in range(3):
        eff = R.num(ench.get(f"Effect_{i}"), int)
        arg, pts = R.num(ench.get(f"EffectArg_{i}"), int), R.num(ench.get(f"EffectPointsMin_{i}"), int)
        if eff == 5 and arg in ARG_STAT and pts:
            st[ARG_STAT[arg]] = st.get(ARG_STAT[arg], 0) + pts
        elif eff == 2 and pts:
            st["wdmg"] = st.get("wdmg", 0) + pts
    if not st:
        m = re.search(r"All Stats \+(\d+)", name)
        if m:
            st = {k: int(m.group(1)) for k in ("str", "agi", "sta", "int", "spi")}
        for rx, key in NAME_STAT:
            m = rx.search(name)
            if m:
                st[key] = st.get(key, 0) + int(m.group(1))
    return st


INV_SLOT = {1: "head", 3: "shoulder", 5: "chest", 20: "chest", 6: "waist", 7: "legs", 8: "feet", 9: "wrist", 10: "hands", 16: "back"}
KIT_RX = re.compile(r"Armor Kit|Scope$|Accurascope|Buckle|Shield Spike", re.I)


def enhancement_stats(ench):
    """Flat stats of an armor kit / scope: armor (effect 4), item stats (effect 5), named bonuses like '+3% Hit' or 'Scope (+7 Damage)'."""
    st = {}
    for i in range(3):
        eff = R.num(ench.get(f"Effect_{i}"), int)
        arg, pts = R.num(ench.get(f"EffectArg_{i}"), int), R.num(ench.get(f"EffectPointsMin_{i}"), int)
        if eff == 4 and pts:
            st["armor"] = st.get("armor", 0) + pts
        elif eff == 5 and arg in ARG_STAT and pts:
            st[ARG_STAT[arg]] = st.get(ARG_STAT[arg], 0) + pts
        elif eff == 2 and pts:
            st["wdmg"] = st.get("wdmg", 0) + pts
    name = ench.get("Name_lang", "")
    m = re.search(r"\+(\d+)% Hit", name)
    if m:
        st["hitrtng"] = int(m.group(1)) * 10                    # 10 rating per 1% hit at level 60
    m = re.search(r"Scope \(\+(\d+) Damage\)", name)
    if m:
        st["wdmg"] = int(m.group(1))
    return st


def enhancements(T, byid, build):
    """Armor kits (leather-working) and scopes (engineering) through the item -> use spell -> permanent enchantment chain of the client tables."""
    ie = {r["ID"]: r for r in imp.read(imp.fetch("ItemEffect", build, None, False))}
    item_spell = {}
    for r in imp.read(imp.fetch("ItemXItemEffect", build, None, False)):
        if r["ItemEffectID"] in ie:
            item_spell.setdefault(r["ItemID"], ie[r["ItemEffectID"]]["SpellID"])
    equipped = {}
    for r in imp.read(imp.fetch("SpellEquippedItems", build, None, False)):
        equipped[r["SpellID"]] = r
    out = []
    for prof in ("leatherworking", "engineering"):
        data = json.loads((ROOT / "data" / "wow_professions" / f"{prof}.json").read_text(encoding="utf-8"))
        cap = data.get("cap") or 300
        for r in data["recipes"]:
            c = r.get("creates")
            if not c or not KIT_RX.search(c["name"]["en"]) or r["learn_at"] > cap:
                continue
            spell = item_spell.get(str(c["id"]))
            ench = None
            for e in T["effects"].get(spell, []) if spell else []:
                if R.num(e["Effect"], int) == 53:
                    ench = byid.get(e.get("EffectMiscValue_0", e.get("EffectMiscValue")))
            if not ench:
                continue
            st = enhancement_stats(ench)
            if not st:
                continue
            mask = R.num((equipped.get(spell) or {}).get("EquippedItemInvTypes"), int)
            slots = sorted({INV_SLOT[b] for b in INV_SLOT if mask >> b & 1})
            if prof == "engineering":
                slots = ["rng"]
            out.append({"id": c["id"], "recipe": r["id"], "name": c["name"], "slots": slots, "skill": r["learn_at"], "effect": ench.get("Name_lang"), "stats": st,
                        "kind": "kit" if prof == "leatherworking" else "scope", "profession": prof})
    return out


def main():
    build = imp.latest_beta_build()
    byid = {r["ID"]: r for r in imp.read(imp.fetch("SpellItemEnchantment", build, None, False))}
    T = R.load(build, False)
    prof = json.loads((ROOT / "data" / "wow_professions" / "enchanting.json").read_text(encoding="utf-8"))
    cap = prof.get("cap") or 300
    out = []
    for r in prof["recipes"]:
        n = r["name"]["en"]
        m = re.match(r"Enchant (2H Weapon|Weapon|Off-Hand|Chest|Bracer|Cloak|Gloves|Boots|Shield|Necklace|Ring) - (.+)$", n)
        if not m or r["learn_at"] > cap:
            continue
        ench = None
        for e in T["effects"].get(str(r["id"]), []):
            if R.num(e["Effect"], int) == 53:
                ench = byid.get(e.get("EffectMiscValue_0", e.get("EffectMiscValue")))
        if not ench:
            continue
        st = stats_of(ench)
        proc = not st and R.num(ench.get("Effect_0"), int) == 1
        out.append({"id": r["id"], "name": r["name"], "slots": SLOT_OF[m.group(1)], "skill": r["learn_at"], "effect": ench.get("Name_lang"), "stats": st, "proc": proc, "kind": "enchant"})
    for e in out:
        e["kind"] = "enchant"
    out += enhancements(T, byid, build)
    data = {"build": build, "skill_cap": cap, "enchants": out}
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    OUT.write_text(text, encoding="utf-8")
    OUT_SIM.write_text(text, encoding="utf-8")
    valued = [e for e in out if e["stats"]]
    print(f"{len(out)} enchantments and enhancements up to skill {cap}: {len(valued)} with flat stats, {sum(e.get('proc', False) for e in out)} procs")
    for e in valued:
        if e["kind"] != "enchant":
            print(f"  {e['kind']:6} {','.join(e['slots']):22} {e['name']['en']:36} L{e['skill']} {e['stats']}")


if __name__ == "__main__":
    main()
