"""Packages the WoWSims Forever engine for the browser (site_build/wowsims_web/, copied to dist/assets/wowsims/ by the build):
lib.wasm.gz (built with the with_db tag, so requests need no item database), Go's wasm_exec.js, the MIT license, and
presets.json: every exported WoWSims preset (requests/page_*.json) with our spec id and names, plus the spell/item names
the result's damage sources need. usage: py package_web.py   (after building the wasm, see README.md)"""
import gzip, json, os, shutil, subprocess
from pathlib import Path

HERE = Path(__file__).parent
PROJECT = HERE.parents[1]
CLONE = Path(os.environ.get("WOWSIMS_DIR", PROJECT.parent / "wowsims-forever"))
OUT = PROJECT / "site_build" / "wowsims_web"
GO = os.environ.get("WOWSIMS_GO") or shutil.which("go") or r"C:\Users\Vincent\tools\go\bin\go.exe"

TREES = {
    "ClassWarrior": ["warrior_arms", "warrior_fury", "warrior_protection"], "ClassRogue": ["rogue_assassination", "rogue_combat", "rogue_subtlety"],
    "ClassHunter": ["hunter_beastmastery", "hunter_marksmanship", "hunter_melee"], "ClassMage": ["mage_arcane", "mage_fire", "mage_frost"],
    "ClassWarlock": ["warlock_affliction", "warlock_demonology", "warlock_destruction"], "ClassShaman": ["shaman_elemental", "shaman_enhancement", "shaman_restoration"],
    "ClassDruid": ["druid_balance", "druid_feral", "druid_restoration"], "ClassPriest": ["priest_discipline", "priest_holy", "priest_shadow"],
    "ClassPaladin": ["paladin_holy", "paladin_protection", "paladin_retribution"],
}
NAMES = {  # spec id -> (fr, en)
    "warrior_arms": ("Guerrier Armes", "Arms Warrior"), "warrior_fury": ("Guerrier Fureur", "Fury Warrior"),
    "rogue_assassination": ("Voleur Assassinat", "Assassination Rogue"), "rogue_combat": ("Voleur Combat", "Combat Rogue"), "rogue_subtlety": ("Voleur Finesse", "Subtlety Rogue"),
    "hunter_beastmastery": ("Chasseur Maîtrise des bêtes", "Beast Mastery Hunter"), "hunter_marksmanship": ("Chasseur Précision", "Marksmanship Hunter"), "hunter_melee": ("Chasseur Survie", "Survival Hunter"),
    "mage_arcane": ("Mage Arcanes", "Arcane Mage"), "mage_fire": ("Mage Feu", "Fire Mage"), "mage_frost": ("Mage Givre", "Frost Mage"),
    "warlock_affliction": ("Démoniste Affliction", "Affliction Warlock"), "warlock_demonology": ("Démoniste Démonologie", "Demonology Warlock"), "warlock_destruction": ("Démoniste Destruction", "Destruction Warlock"),
    "shaman_elemental": ("Chaman Élémentaire", "Elemental Shaman"), "shaman_enhancement": ("Chaman Amélioration", "Enhancement Shaman"),
    "druid_balance": ("Druide Équilibre", "Balance Druid"), "druid_feral": ("Druide Farouche (félin)", "Feral Druid (cat)"),
    "priest_shadow": ("Prêtre Ombre", "Shadow Priest"), "paladin_retribution": ("Paladin Vindicte", "Retribution Paladin"),
}


PRESET = {  # export label -> WoWSims preset name, as their site shows it
    "warrior_fury": "Fury Pre-BiS", "warrior_fury_2h": "Fury 2H Pre-BiS", "warrior_arms": "Arms Pre-BiS",
    "rogue_asn_muti": "Asn Muti", "rogue_combat_ss": "Combat SS", "rogue_combat_bs": "Combat BS", "rogue_sub_hemo": "Subtlety Hemo",
    "rogue_combat_venom": "Combat Venom", "rogue_hemo_seal_fate": "Hemo Seal Fate",
    "hunter_sv_weave": "SV Weave", "hunter_mm": "MM", "hunter_bm": "BM", "hunter_sv": "SV", "hunter_sv_melee": "SV Melee",
    "mage_arcane": "Arcane", "mage_arcane_fire": "Arcane Fire", "mage_ffb": "FFB", "mage_fire": "Fire", "mage_frost_incin": "Frost Incin", "mage_frost_med": "Frost Med",
    "warlock_demo_fire": "Demo (Fire Brand)", "warlock_demo_shadow": "Demo (Shadow Brand)", "warlock_destro": "Destro", "warlock_sm_ruin": "SM/Ruin", "warlock_aff_wrack": "Aff (Wrack)",
    "shaman_elemental": "Default", "shaman_enhancement": "Default", "druid_balance": "Default", "druid_feral": "Default",
    "priest_shadow": "Shadow", "paladin_ret_uw": "Unsealed Wrath", "paladin_ret_holy_shock": "Holy Shock",
}


def spec_of(cls, talents):
    trees = (talents.split("-") + ["", "", ""])[:3]
    pts = [sum(int(c) for c in t if c.isdigit()) for t in trees]
    return TREES[cls][pts.index(max(pts))]


OUT.mkdir(parents=True, exist_ok=True)
wasm = CLONE / "dist_bm" / "lib_db.wasm"
if not wasm.exists():
    raise SystemExit("build it first: GOOS=js GOARCH=wasm go build --tags=with_db -ldflags '-w -s' -o dist_bm/lib_db.wasm ./sim/wasm/")
(OUT / "lib.wasm.gz").write_bytes(gzip.compress(wasm.read_bytes(), 9))
goroot = subprocess.run([GO, "env", "GOROOT"], capture_output=True, text=True).stdout.strip()
shutil.copy(Path(goroot) / "lib" / "wasm" / "wasm_exec.js", OUT / "wasm_exec.js")
shutil.copy(CLONE / "LICENSE", OUT / "LICENSE-wowsims.txt")

presets = []
for page in sorted((HERE / "requests").glob("page_*.json")):
    for label, req in json.loads(page.read_text(encoding="utf-8")).items():
        meta = req.pop("_bm", {})
        req.pop("requestId", None)
        p = req["raid"]["parties"][0]["players"][0]
        sid = spec_of(p["class"], p.get("talentsString", ""))
        if sid not in NAMES:
            continue
        presets.append({"id": label, "spec": sid, "fr": NAMES[sid][0], "en": NAMES[sid][1], "preset": PRESET.get(label) or meta.get("preset", ""),
                        "race": p["race"], "request": req})
best = {r["spec"]: r["label"] for r in json.loads((PROJECT / "data" / "wow_ranking_wowsims_by_spec.json").read_text(encoding="utf-8"))["specs"]}
presets.sort(key=lambda x: (x["fr"], x["id"] != best.get(x["spec"]), x["preset"]))
db = json.loads((CLONE / "assets" / "database" / "db.json").read_text(encoding="utf-8"))
names = {"spell": {s["id"]: s["name"] for s in db.get("spellIcons", [])}, "item": {i["id"]: i["name"] for i in db.get("items", [])}}
commit = subprocess.run(["git", "log", "-1", "--format=%h %cs"], cwd=CLONE, capture_output=True, text=True).stdout.strip()
(OUT / "presets.json").write_text(json.dumps({"engine_commit": commit, "best": best, "presets": presets, "names": names},
                                             ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print({f.name: f.stat().st_size for f in OUT.iterdir()})
