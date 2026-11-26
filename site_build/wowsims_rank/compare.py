"""Maps each WoWSims preset (data/wow_ranking_wowsims.json) to one of our specs by the talent tree that holds the most
points, keeps the best preset per spec, and prints it next to our own ranking (data/wow_ranking60.json, sim60).
Writes data/wow_ranking_wowsims_by_spec.json (the per-spec view the site can read)."""
import json
from pathlib import Path

PROJECT = Path(__file__).parents[2]
TREES = {  # class -> our spec ids in talent-tree order
    "ClassWarrior": ["warrior_arms", "warrior_fury", "warrior_protection"],
    "ClassRogue": ["rogue_assassination", "rogue_combat", "rogue_subtlety"],
    "ClassHunter": ["hunter_beastmastery", "hunter_marksmanship", "hunter_melee"],
    "ClassMage": ["mage_arcane", "mage_fire", "mage_frost"],
    "ClassWarlock": ["warlock_affliction", "warlock_demonology", "warlock_destruction"],
    "ClassShaman": ["shaman_elemental", "shaman_enhancement", "shaman_restoration"],
    "ClassDruid": ["druid_balance", "druid_feral", "druid_restoration"],
    "ClassPriest": ["priest_discipline", "priest_holy", "priest_shadow"],
    "ClassPaladin": ["paladin_holy", "paladin_protection", "paladin_retribution"],
}


def spec_of(row):
    trees = (row["talents"].split("-") + ["", "", ""])[:3]
    pts = [sum(int(c) for c in t if c.isdigit()) for t in trees]
    return TREES[row["class"]][pts.index(max(pts))]


ws = json.loads((PROJECT / "data" / "wow_ranking_wowsims.json").read_text(encoding="utf-8"))
ours = {r["spec"]: r for r in json.loads((PROJECT / "data" / "wow_ranking60.json").read_text(encoding="utf-8"))["specs"]}
best = {}
for r in ws["rows"]:
    if "dps" not in r:
        continue
    s = spec_of(r)
    r = dict(r, spec=s)
    if s not in best or r["dps"] > best[s]["dps"]:
        best[s] = r
order = sorted(best.values(), key=lambda r: -r["dps"])
print(f'{"#":>2} {"spec":24} {"WoWSims":>8} {"preset":24} {"ours":>8} {"our #":>5}  gap')
our_rank = {s: i + 1 for i, s in enumerate(sorted((s for s in ours if ours[s].get("role") == "dps"), key=lambda s: -ours[s]["dps"]))}
for i, r in enumerate(order, 1):
    o = ours.get(r["spec"], {})
    gap = f'{(r["dps"] / o["dps"] - 1) * 100:+.0f} %' if o.get("dps") else ""
    print(f'{i:>2} {r["spec"]:24} {r["dps"]:8.1f} {r["label"]:24} {o.get("dps", 0):8.1f} {our_rank.get(r["spec"], "-"):>5}  {gap}')
missing = [s for s in our_rank if s not in best]
print("in our ranking, no WoWSims preset:", missing)
(PROJECT / "data" / "wow_ranking_wowsims_by_spec.json").write_text(json.dumps(
    {k: ws[k] for k in ("engine", "engine_commit", "source", "generated", "iterations")} | {"specs": order}, indent=1, ensure_ascii=False), encoding="utf-8")
