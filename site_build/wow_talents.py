"""World of Warcraft: Forever talent calculator -- data loading and validation.

The calculator itself (templates/wow_talents_*.html + js/wow-talents.js) is generic and data-driven: it knows the rules
below and nothing about any actual talent. Talent data is read from data/wow_talents/<class>.json and is NEVER invented
here. Until real data exists no talent page is generated at all.

Local testing only: WOW_TALENTS_FIXTURE=1 uses site_build/wow_talents_fixture/*.json (obviously fake talents), stamps
every page with a test banner + noindex and keeps them out of the sitemap. Never deploy a build made with it (the
build prints a warning and the pages carry the marker WOW-TALENTS-FIXTURE, which the deploy check greps for).

Class file schema (one file per class):
{
  "id": "mage",
  "name": {"fr": "Mage", "en": "Mage"},
  "specs": [                                   # exactly 3 in the game
    {"id": "arcane",
     "name": {"fr": "Arcanes", "en": "Arcane"},
     "talents": [
       {"id": "arcane-focus",                  # unique inside the class
        "name": {"fr": "...", "en": "..."},
        "row": 1,                              # 1..RULES["rows"]
        "col": 1,                              # 1..RULES["cols"]
        "max_rank": 5,                         # 1..9
        "desc": {"fr": ["text rank 1", "..."], "en": [...]},   # one text per rank
        "gates": [{"through_row": 2, "points": 10}],           # optional: needs >= points spent in rows 1..through_row of this spec
        "requires": [{"id": "other-talent", "rank": 3}],       # optional: ALL of these prerequisite talents (a lone dict is accepted too)
        "requires_any": [{"id": "x", "rank": 1}],              # optional: AT LEAST ONE of these
        "icon": "path/or/url"}                                 # optional, none until we have permitted images
     ]}
  ],
  "source": {"label": "...", "url": "..."},   # optional: where the data comes from (shown on the page)
  "icons_source": {"label": "...", "url": "..."}   # optional: where the "icon" images are served from (credited on the page)
}
Without "gates" a talent in row r falls back to the generic rule below. Importer output always carries explicit gates.

Rules modelled: 51 points to spend across the three trees, seven rows, the next row unlocks for every 5 points invested.
Fallback when a talent has no explicit "gates": row r needs (r-1)*5 points spent in the rows strictly below it (same spec).
The level needed for N points spent is first_level - 1 + N (first point at level 10). wow_talents_import.py READS the real
gates, the point cap and the level schedule from the game tables and reports any difference with these defaults.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

RULES = {"total_points": 51, "rows": 7, "cols": 4, "points_per_row": 5, "first_level": 10, "specs_per_class": 3}

HERE = Path(__file__).parent
DATA_DIR = HERE.parent / "data" / "wow_talents"
FIXTURE_DIR = HERE / "wow_talents_fixture"
STAGING_DIR = HERE.parent / "data" / "wow_talents_staging"
FIXTURE_MARKER = "WOW-TALENTS-FIXTURE"

# Display order of the nine classes (ids must match the file ids).
CLASS_ORDER = ["druid", "hunter", "mage", "paladin", "priest", "rogue", "shaman", "warlock", "warrior"]


def _as_list(v) -> list:
    return [] if not v else (v if isinstance(v, list) else [v])


def _check_text(obj, where: str) -> None:
    if not isinstance(obj, dict) or set(obj) != {"fr", "en"} or not all(isinstance(v, str) and v.strip() for v in obj.values()):
        raise ValueError(f"{where}: needs non-empty 'fr' and 'en' strings, got {obj!r}")


def validate(cls: dict, source: str = "") -> None:
    where = f"{source or cls.get('id', '?')}"
    if not isinstance(cls.get("id"), str) or not cls["id"]:
        raise ValueError(f"{where}: missing class id")
    _check_text(cls.get("name"), f"{where} name")
    specs = cls.get("specs")
    if not isinstance(specs, list) or len(specs) != RULES["specs_per_class"]:
        raise ValueError(f"{where}: exactly {RULES['specs_per_class']} specs required")
    seen_ids: set[str] = set()
    all_talents: dict[str, dict] = {}
    for spec in specs:
        sw = f"{where}/{spec.get('id', '?')}"
        _check_text(spec.get("name"), f"{sw} name")
        cells: set[tuple[int, int]] = set()
        for t in spec.get("talents", []):
            tw = f"{sw}/{t.get('id', '?')}"
            if not t.get("id") or t["id"] in seen_ids:
                raise ValueError(f"{tw}: missing or duplicate talent id")
            seen_ids.add(t["id"])
            all_talents[t["id"]] = {**t, "_spec": spec["id"]}
            _check_text(t.get("name"), f"{tw} name")
            if not (isinstance(t.get("row"), int) and 1 <= t["row"] <= RULES["rows"]):
                raise ValueError(f"{tw}: row must be 1..{RULES['rows']}")
            if not (isinstance(t.get("col"), int) and 1 <= t["col"] <= RULES["cols"]):
                raise ValueError(f"{tw}: col must be 1..{RULES['cols']}")
            if (t["row"], t["col"]) in cells:
                raise ValueError(f"{tw}: two talents share row {t['row']} col {t['col']}")
            cells.add((t["row"], t["col"]))
            if not (isinstance(t.get("max_rank"), int) and 1 <= t["max_rank"] <= 9):
                raise ValueError(f"{tw}: max_rank must be 1..9")
            for lang in ("fr", "en"):
                d = (t.get("desc") or {}).get(lang)
                if not (isinstance(d, list) and len(d) == t["max_rank"] and all(isinstance(x, str) and x.strip() for x in d)):
                    raise ValueError(f"{tw}: desc.{lang} must list exactly {t['max_rank']} non-empty rank texts")
    for tid, t in all_talents.items():
        for key in ("requires", "requires_any"):
            for req in _as_list(t.get(key)):
                target = all_talents.get(req.get("id"))
                if not target or target["_spec"] != t["_spec"]:
                    raise ValueError(f"{where}/{tid}: '{key}' must point to a talent of the same spec")
                if not (isinstance(req.get("rank"), int) and 1 <= req["rank"] <= target["max_rank"]) or target["row"] > t["row"] or target["id"] == tid:
                    raise ValueError(f"{where}/{tid}: invalid prerequisite rank or row order in '{key}'")
        for g in t.get("gates") or []:
            if not (isinstance(g.get("through_row"), int) and 1 <= g["through_row"] <= RULES["rows"] and isinstance(g.get("points"), int) and g["points"] > 0):
                raise ValueError(f"{where}/{tid}: invalid gate {g!r}")


def revision(cls: dict) -> str:
    """Short hash of the tree STRUCTURE (ids, cells, ranks): a shared link built on other data is rejected, not misread."""
    parts = [[s["id"], [[t["id"], t["row"], t["col"], t["max_rank"]] for t in sorted(s["talents"], key=lambda t: (t["row"], t["col"]))]] for s in cls["specs"]]
    return hashlib.sha1(json.dumps(parts, separators=(",", ":")).encode()).hexdigest()[:6]


def load() -> tuple[list[dict], bool]:
    """(classes in display order, is_fixture). Empty list = no calculator pages."""
    real = sorted(DATA_DIR.glob("*.json")) if DATA_DIR.is_dir() else []
    preview = not real and os.environ.get("WOW_TALENTS_PREVIEW") == "1"          # importer output, not approved for publication
    use_fixture = not real and (preview or os.environ.get("WOW_TALENTS_FIXTURE") == "1")
    files = real or (sorted(STAGING_DIR.glob("*.json")) if preview else sorted(FIXTURE_DIR.glob("*.json")) if use_fixture else [])
    classes = []
    for f in files:
        cls = json.loads(f.read_text(encoding="utf-8"))
        validate(cls, f.name)
        cls["rev"] = revision(cls)
        classes.append(cls)
    order = {cid: i for i, cid in enumerate(CLASS_ORDER)}
    classes.sort(key=lambda c: order.get(c["id"], 99))
    if use_fixture:
        print("!! talent pages are built from TEST or UNAPPROVED PREVIEW data (WOW_TALENTS_FIXTURE / WOW_TALENTS_PREVIEW) -- do NOT deploy this build.")
    return classes, use_fixture


# ---------------------------------------------------------------------------------------------------- UI strings
UI = {
    "fr": {
        "points": "Points : {n} / {max}", "pointsLeft": "Restants : {n}", "level": "Niveau requis : {n}", "levelNone": "Niveau requis : —",
        "reset": "Tout réinitialiser", "resetTree": "Réinitialiser", "share": "Copier le lien", "copied": "Lien copié !",
        "removeMode": "Mode retrait", "removeModeOn": "Mode retrait activé", "rankOf": "Rang {r} sur {max}", "nextRank": "Rang suivant",
        "needPoints": "Nécessite {n} points dans les rangées 1 à {rows} de « {tree} » (actuellement {have}).",
        "needTalent": "Nécessite « {name} » au rang {r}.", "needAny": "Nécessite l'un de ces talents : {names}.", "treePoints": "{n} pts",
        "hint": "Clic pour ajouter un point, clic droit ou Maj + clic pour en retirer. Sur téléphone, activez le mode retrait.",
        "linkOld": "Ce lien a été créé avec d'anciennes données de talents : il ne peut pas être chargé.",
        "linkBad": "Ce lien de build n'est pas valide.",
        "incomplete": "Certaines valeurs de ce talent dépendent de vos statistiques ou ne peuvent pas être déterminées de façon fiable à partir des données du jeu : elles sont affichées « … ».",
    },
    "en": {
        "points": "Points: {n} / {max}", "pointsLeft": "Left: {n}", "level": "Required level: {n}", "levelNone": "Required level: —",
        "reset": "Reset all", "resetTree": "Reset", "share": "Copy link", "copied": "Link copied!",
        "removeMode": "Remove mode", "removeModeOn": "Remove mode on", "rankOf": "Rank {r} of {max}", "nextRank": "Next rank",
        "needPoints": "Requires {n} points in rows 1 to {rows} of \"{tree}\" (currently {have}).",
        "needTalent": "Requires \"{name}\" at rank {r}.", "needAny": "Requires one of these talents: {names}.", "treePoints": "{n} pts",
        "hint": "Click to add a point, right-click or Shift + click to remove one. On a phone, turn on remove mode.",
        "linkOld": "This link was made with older talent data and cannot be loaded.",
        "linkBad": "This build link is not valid.",
        "incomplete": "Some values of this talent depend on your stats or cannot be determined reliably from the game data: they are shown as \"…\".",
    },
}

TXT = {
    "fr": {
        "kicker": "World of Warcraft: Forever · Talents",
        "hub_title": "Calculateur de talents WoW: Forever par classe",
        "hub_desc": "Calculateur de talents pour les neuf classes de WoW: Forever : trois arbres, 51 points, build partageable par lien.",
        "hub_h1": "Calculateur de talents de WoW: Forever",
        "hub_intro": "Choisissez une classe, répartissez vos points dans ses trois arbres de spécialisation et partagez votre build par un simple lien.",
        "rules_h2": "Comment fonctionnent les talents",
        "rules": ["Vous disposez de 51 points à répartir entre les trois arbres de spécialisation de votre classe.",
                  "Chaque arbre compte sept rangées. Pour chaque tranche de 5 points investis dans un arbre, la rangée suivante se débloque.",
                  "Certains talents se prennent en plusieurs rangs, et certains exigent un autre talent."],
        "classes_h2": "Choisir une classe",
        "class_title": "Talents {name} WoW: Forever : calculateur",
        "class_desc": "Calculateur de talents {name} pour WoW: Forever : arbres {specs}, 51 points, build partageable par lien.",
        "class_desc_short": "Calculateur de talents {name} pour WoW: Forever : trois arbres, 51 points, build partageable par lien.",
        "class_h1": "Talents {name} : calculateur WoW: Forever",
        "class_intro": "Répartissez vos 51 points entre les arbres {specs}. Le lien de partage encode votre build : envoyez-le tel quel.",
        "specs": "spécialisations", "talents": "talents", "back": "Toutes les classes", "classes_count": "classes", "talents_kicker": "Talents",
        "sources": "Sources et règles", "rules_src": "Règles (51 points, sept rangées, une rangée débloquée tous les 5 points) : ",
        "data_pending": "Le calculateur sera disponible quand les données de talents du jeu seront publiées.",
        "fixture": "PRÉVISUALISATION : cette page utilise des données de test ou non validées et ne doit pas être publiée.",
    },
    "en": {
        "kicker": "World of Warcraft: Forever · Talents",
        "hub_title": "WoW: Forever talent calculator by class",
        "hub_desc": "Talent calculator for the nine WoW: Forever classes: three trees, 51 points, build shareable by link.",
        "hub_h1": "WoW: Forever talent calculator",
        "hub_intro": "Pick a class, spread your points across its three specialization trees and share your build with a simple link.",
        "rules_h2": "How talents work",
        "rules": ["You have 51 points to spend across your class's three specialization trees.",
                  "Each tree has seven rows. For every 5 points invested in a tree, the next row unlocks.",
                  "Some talents take several ranks, and some require another talent."],
        "classes_h2": "Pick a class",
        "class_title": "{name} talents WoW: Forever: calculator",
        "class_desc": "{name} talent calculator for WoW: Forever: {specs} trees, 51 points, build shareable by link.",
        "class_desc_short": "{name} talent calculator for WoW: Forever: three trees, 51 points, build shareable by link.",
        "class_h1": "{name} talents: WoW: Forever calculator",
        "class_intro": "Spend your 51 points across the {specs} trees. The share link encodes your build: send it as is.",
        "specs": "specializations", "talents": "talents", "back": "All classes", "classes_count": "classes", "talents_kicker": "Talents",
        "sources": "Sources and rules", "rules_src": "Rules (51 points, seven rows, a row unlocked every 5 points): ",
        "data_pending": "The calculator will be available once the game's talent data is published.",
        "fixture": "PREVIEW: this page uses test or unapproved data and must not be published.",
    },
}


def payload(cls: dict, lang: str) -> dict:
    """The language-resolved data the calculator script reads (embedded in the page as JSON)."""
    specs = []
    for s in cls["specs"]:
        talents = []
        for t in s["talents"]:
            item = {"id": t["id"], "name": t["name"][lang], "row": t["row"], "col": t["col"], "max_rank": t["max_rank"], "desc": t["desc"][lang]}
            if t.get("requires"):
                item["requires"] = _as_list(t["requires"])
            if t.get("requires_any"):
                item["requires_any"] = t["requires_any"]
            if t.get("gates"):
                item["gates"] = t["gates"]
            if t.get("incomplete"):
                item["incomplete"] = True
            if t.get("icon"):
                item["icon"] = t["icon"]
            talents.append(item)
        specs.append({"id": s["id"], "name": s["name"][lang], "talents": talents})
    return {"rev": cls["rev"], "rules": RULES, "ui": UI[lang], "lang": lang, "specs": specs}
