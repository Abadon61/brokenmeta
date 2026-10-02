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
