"""Exports the level-60 simulator's item pool (dungeons + raids from the beta client tables) to
site_build/sim60/data/items.json, plus the class proficiency table, so the JavaScript engine and
optimizer read the same sourced data as the site.   py -3.11 wow_sim60_export.py"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "site_build" / "sim60" / "data"
OUT.mkdir(parents=True, exist_ok=True)

items = []
seen = set()
d = json.loads((ROOT / "data" / "wow_dungeons" / "dungeons.json").read_text(encoding="utf-8"))
r = json.loads((ROOT / "data" / "wow_raids" / "raids.json").read_text(encoding="utf-8"))
for src_kind, groups in (("dungeon", d["dungeons"]), ("raid", r["raids"])):
    for g in groups:
        for it in g["items"]:
            if it["id"] in seen:
                continue
            seen.add(it["id"])
            items.append({
                "id": it["id"], "name": it["name"], "q": it.get("q"), "slot": it["slot"], "type": it["type"]["en"],
                "req": it.get("req") or 0, "ilvl": it.get("lvl"), "st": it["st"], "src": it.get("src", []),
                "from": src_kind, "zone": g["name"]["en"] if isinstance(g["name"], dict) else g["name"],
            })
payload = {"build": d.get("build"), "slots": d["slots"], "items": items}
(OUT / "items.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
prof = ROOT / "data" / "wow_items" / "proficiency.json"
if prof.exists():
    (OUT / "proficiency.json").write_text(prof.read_text(encoding="utf-8"), encoding="utf-8")
print(len(items), "items,", sum(1 for i in items if i["req"] >= 50), "with req >= 50,", sum(1 for i in items if i["from"] == "raid"), "raid")


# ---- spells at level 60 (ranks resolved by the same code as the site's Python engine) ----
import sys
sys.path.insert(0, str(ROOT / "site_build"))
import wow_dps_sim  # noqa: E402

classes = ["warrior", "paladin", "hunter", "rogue", "priest", "shaman", "mage", "warlock", "druid"]
spells = {}
for cls in classes:
    g = wow_dps_sim.load_glossary(cls, 60)
    if not g:
        continue
    abil = {}
    for a in g["abilities"]:
        abil[a["id"]] = {k: a.get(k) for k in ("name", "wowhead_spell_id", "resource_cost", "cooldown_sec", "gcd_sec", "cast_time", "school", "flags", "effects", "min_level", "notes") if k in a}
    fut = []
    fp = ROOT / "data" / "wow_spells_future" / f"{cls}.json"
    if fp.exists():
        for a in json.loads(fp.read_text(encoding="utf-8"))["abilities"]:
            known = [r for r in a["ranks"] if r["level"] <= 60]
            if known:
                fut.append({"name": a["name"], "first_level": a["first_level"], "rank": known[-1]})
    spells[cls] = {"abilities": abil, "future": fut}
(OUT / "spells60.json").write_text(json.dumps(spells, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
w = spells["warrior"]["abilities"]
for k in ("warrior_bloodthirst", "warrior_whirlwind", "warrior_heroic_strike", "warrior_death_wish", "warrior_slam", "warrior_overpower", "warrior_rend"):
    print(k, w[k].get("resource_cost"), w[k].get("cooldown_sec"), json.dumps(w[k]["effects"])[:260])
print([ (f["name"], f["rank"]["cost"], f["rank"]["cooldown_ms"]) for f in spells["warrior"]["future"]])


# ---- talent trees (same data and ordering as the site's talent calculator) ----
import wow_talents  # noqa: E402

_classes, _ = wow_talents.load()
talents = {}
KIT_CLASSES = {"warrior"}   # classes that have a simulator kit (keeps the page download small)
for c in _classes:
    if c["id"] not in KIT_CLASSES:
        continue
    p_en, p_fr = wow_talents.payload(c, "en"), wow_talents.payload(c, "fr")
    specs = []
    for se, sf in zip(p_en["specs"], p_fr["specs"]):
        ts = []
        for te, tf in zip(se["talents"], sf["talents"]):
            t = {"id": te["id"], "name": {"en": te["name"], "fr": tf["name"]}, "row": te["row"], "col": te["col"],
                 "max_rank": te["max_rank"], "desc": {"en": te["desc"], "fr": tf["desc"]}}
            for k in ("requires", "requires_any", "gates"):
                if te.get(k):
                    t[k] = te[k]
            ts.append(t)
        specs.append({"id": se["id"], "name": {"en": se["name"], "fr": sf["name"]}, "talents": ts})
    talents[c["id"]] = {"rev": c["rev"], "rules": p_en["rules"], "specs": specs}
(OUT / "talents.json").write_text(json.dumps(talents, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("talents:", {k: sum(len(s["talents"]) for s in v["specs"]) for k, v in talents.items()})
