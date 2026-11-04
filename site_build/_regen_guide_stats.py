"""One-off: reorders the stat priority list of the DPS spec guides (data/wow_guides/content.json) from the simulator's stat weights
(data/wow_ranking60.json, detail.weights), run after a ranking recompute:  py -3 site_build/_regen_guide_stats.py

Rules (stated on the page): only the stats the simulator measures are reordered, and only among the places they already hold in the list.
The hit chance is left where it is (it is worth zero once the cap is reached, the guide says to reach the cap first), and so are the stats
the simulator does not weigh (weapon damage, expertise, stamina, armor, Mp5). Value of a stat = DPS gained per point of rating or of the
stat itself (a critical strike, hit or haste probe is 14 / 10 / 10 rating points for 1 %)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "data" / "wow_guides" / "content.json"
RANK = json.loads((ROOT / "data" / "wow_ranking60.json").read_text(encoding="utf-8"))
SPEC_OF = {
    ("warrior", "fury"): "warrior_fury", ("warrior", "arms"): "warrior_arms",
    ("rogue", "combat"): "rogue_combat", ("rogue", "assassination"): "rogue_assassination", ("rogue", "subtlety"): "rogue_subtlety",
    ("mage", "fire"): "mage_fire", ("mage", "frost"): "mage_frost", ("mage", "arcane"): "mage_arcane",
    ("warlock", "affliction"): "warlock_affliction", ("warlock", "destruction"): "warlock_destruction", ("warlock", "demonology"): "warlock_demonology",
    ("hunter", "marksmanship"): "hunter_marksmanship", ("hunter", "beast-mastery"): "hunter_beastmastery", ("hunter", "survival"): "hunter_melee",
    ("priest", "shadow"): "priest_shadow", ("shaman", "elemental"): "shaman_elemental", ("shaman", "enhancement"): "shaman_enhancement",
    ("druid", "balance"): "druid_balance", ("druid", "feral-combat"): "druid_feral", ("paladin", "retribution"): "paladin_retribution",
}
LABEL_KEY = {"Coup critique": "critstrkrtng", "Hâte": "hastertng", "Agilité": "agi", "Force": "str", "Intelligence": "int", "Esprit": "spi", "Puissance des sorts": "splpwr"}
PER_POINT = {"critstrkrtng": 14, "hastertng": 10}       # the probe of these stats is one percent worth of rating points
NOTE = {
    "fr": "Ordre des statistiques mesurées recalculé le 3 novembre 2026 par notre simulateur niveau 60 (DPS gagné par point, notes de Blizzard du 3 novembre comprises) : seules les statistiques que le simulateur pèse (critique, hâte, agilité, force, intelligence, esprit, puissance des sorts) changent de place entre elles ; le toucher, qui ne vaut plus rien une fois le plafond atteint, les dégâts d'arme, l'endurance et le reste restent où ils étaient.",
    "en": "Order of the measured stats recomputed on November 3, 2026 by our level-60 simulator (DPS gained per point, including Blizzard's November 3 notes): only the stats the simulator weighs (critical strike, haste, agility, strength, intellect, spirit, spell power) swap places with each other; hit chance, which is worth nothing once the cap is reached, weapon damage, stamina and the rest stay where they were.",
}

content = json.loads(CONTENT.read_text(encoding="utf-8"))
changed = 0
for (cls, spec), rid in SPEC_OF.items():
    row = next(s for s in RANK["specs"] if s["spec"] == rid)
    w = {x["stat"]: x["per"] / PER_POINT.get(x["stat"], 10 if x["stat"] == "hitrtng" else 1) for x in row["detail"]["weights"]}
    order = content[cls][spec]["stats"]["order"]
    slots = [i for i, o in enumerate(order) if o["fr"] in LABEL_KEY]
    items = sorted((order[i] for i in slots), key=lambda o: -w.get(LABEL_KEY[o["fr"]], 0))
    new = list(order)
    for i, o in zip(slots, items):
        new[i] = o
    if [o["fr"] for o in new] != [o["fr"] for o in order]:
        changed += 1
    st = content[cls][spec]["stats"]
    st["order"] = new
    old = st.get("note")
    if not (old and "recalculé le 3 novembre 2026" in old.get("fr", "")):
        st["note"] = {l: ((old[l] + " ") if old and old.get(l) else "") + NOTE[l] for l in ("fr", "en")}
    content[cls][spec]["updated"] = "2026-11-03"
    print(f"{cls}/{spec}:", " > ".join(o["fr"] for o in new))
CONTENT.write_text(json.dumps(content, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(changed, "guides reordered")
