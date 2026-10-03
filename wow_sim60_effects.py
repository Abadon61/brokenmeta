"""Exports the item effects (trinket use/proc, "Chance on hit", "Equip:" lines, set bonuses) of the level-60 simulator's
item pool to site_build/sim60/data/effects.json, from the beta client tables (via wago.tools, same helper as wow_talents_import.py).

  ItemXItemEffect -> ItemEffect (trigger type, cooldown) -> Spell / SpellEffect / SpellAuraOptions / SpellDuration / SpellCooldowns
  ItemSet + ItemSetSpell -> set bonuses (piece threshold -> spell)

Nothing is interpreted here: each effect keeps the client's numbers (aura type, base points, period, proc chance, duration,
cooldown) plus the spell's own description, so the JavaScript engine decides what it can simulate and what it flags.
    py -3.11 wow_sim60_effects.py [--refresh]
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import wow_talents_import as imp

ROOT = Path(__file__).parent
OUT = ROOT / "site_build" / "sim60" / "data" / "effects.json"
TABLES = ["ItemXItemEffect", "ItemEffect", "ItemSet", "ItemSetSpell", "Spell", "SpellName", "SpellEffect", "SpellAuraOptions",
          "SpellMisc", "SpellDuration", "SpellCooldowns"]
TRIGGER = {0: "use", 1: "equip", 2: "chance_on_hit", 3: "soulstone", 4: "use_no_delay", 5: "learn"}


def num(v, cast=float):
    try:
        return cast(float(v))
    except (TypeError, ValueError):
        return cast(0)


def main():
    refresh = "--refresh" in sys.argv
    build = imp.latest_beta_build() if refresh else sorted(p.name for p in imp.RAW_DIR.iterdir())[-1]
    T = {t: imp.read(imp.fetch(t, build, None, refresh)) for t in TABLES}
    items = json.loads((ROOT / "site_build" / "sim60" / "data" / "items.json").read_text(encoding="utf-8"))["items"]
    pool = {i["id"] for i in items}

    name = {r["ID"]: r.get("Name_lang", "") for r in T["SpellName"]}
    desc = {r["ID"]: (r.get("Description_lang") or "", r.get("AuraDescription_lang") or "") for r in T["Spell"]}
    effects = defaultdict(list)
    for e in T["SpellEffect"]:
        if num(e.get("DifficultyID"), int) == 0:
            effects[e["SpellID"]].append(e)
    aura = {r["SpellID"]: r for r in T["SpellAuraOptions"] if num(r.get("DifficultyID"), int) == 0}
    misc = {r["SpellID"]: r for r in T["SpellMisc"] if num(r.get("DifficultyID"), int) == 0}
    duration = {r["ID"]: num(r.get("Duration"), int) for r in T["SpellDuration"]}
    cooldown = {r["SpellID"]: r for r in T["SpellCooldowns"] if num(r.get("DifficultyID"), int) == 0}

    def spell(sid):
        sid = str(sid)
        a, m, c = aura.get(sid, {}), misc.get(sid, {}), cooldown.get(sid, {})
        return {
            "spell_id": int(sid), "name": name.get(sid, ""), "desc": desc.get(sid, ("", ""))[0], "aura_desc": desc.get(sid, ("", ""))[1],
            "proc_chance": num(a.get("ProcChance"), int), "proc_charges": num(a.get("ProcCharges"), int),
            "proc_mask": [num(a.get("ProcTypeMask_0"), int), num(a.get("ProcTypeMask_1"), int)], "ppm_id": num(a.get("SpellProcsPerMinuteID"), int),
            "duration_ms": duration.get(m.get("DurationIndex"), 0), "cooldown_ms": num(c.get("RecoveryTime"), int), "category_cd_ms": num(c.get("CategoryRecoveryTime"), int),
            "effects": [{"effect": num(e["Effect"], int), "aura": num(e.get("EffectAura"), int), "base": num(e.get("EffectBasePointsF") or e.get("EffectBasePoints")),
                         "period_ms": num(e.get("EffectAuraPeriod"), int), "misc": [num(e.get("EffectMiscValue_0"), int), num(e.get("EffectMiscValue_1"), int)],
                         "trigger_spell": num(e.get("EffectTriggerSpell"), int), "sp_coeff": num(e.get("EffectBonusCoefficient")), "chain": num(e.get("EffectChainTargets"), int)}
                        for e in effects.get(sid, [])],
        }

    link = defaultdict(list)                       # item id -> ItemEffect ids
    for r in T["ItemXItemEffect"]:
        if num(r["ItemID"], int) in pool:
            link[num(r["ItemID"], int)].append(r["ItemEffectID"])
    ie = {r["ID"]: r for r in T["ItemEffect"]}
    by_item, used = {}, set()
    for item_id, ids in sorted(link.items()):
        lst = []
        for eid in ids:
            r = ie.get(eid)
            if not r:
                continue
            sp = spell(r["SpellID"]); used.add(sp["spell_id"])
            trig = num(r["TriggerType"], int)
            lst.append({"trigger": TRIGGER.get(trig, str(trig)), "charges": num(r.get("Charges"), int), "cooldown_ms": num(r.get("CoolDownMSec"), int),
                        "category_cd_ms": num(r.get("CategoryCoolDownMSec"), int), "spell": sp})
        if lst:
            by_item[str(item_id)] = lst

    # set bonuses for the sets that hold at least one pool item
    sets = []
    spells_by_set = defaultdict(list)
    for r in T["ItemSetSpell"]:
        spells_by_set[r["ItemSetID"]].append(r)
    for r in T["ItemSet"]:
        ids = [num(r.get(f"ItemID_{i}"), int) for i in range(17)]
        mine = [i for i in ids if i in pool]
        if not mine:
            continue
        bonuses = [{"pieces": num(b["Threshold"], int), "spell": spell(b["SpellID"])} for b in sorted(spells_by_set.get(r["ID"], []), key=lambda b: num(b["Threshold"], int))]
        sets.append({"id": num(r["ID"], int), "name": r.get("Name_lang", ""), "items": [i for i in ids if i], "pool_items": mine, "bonuses": bonuses})

    payload = {"build": build, "source": f"WoW: Forever beta client tables, build {build} (via wago.tools)", "items": by_item, "sets": sets}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    kinds = defaultdict(int)
    for lst in by_item.values():
        for e in lst:
            kinds[e["trigger"]] += 1
    print(f"build {build}: {len(by_item)} of {len(pool)} pool items have effects {dict(kinds)}; {len(sets)} sets, {sum(len(s['bonuses']) for s in sets)} set bonuses -> {OUT}")


if __name__ == "__main__":
    main()
