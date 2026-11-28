"""Tree layout of the launch build, applied on top of wow_talents_announced.

The client tables we read (1.60.1.70753 / 70755) still hold the old trees. The open-source WoWSims Forever simulator (MIT) ships the trees of the
launch build: positions, maximum ranks and prerequisites (wowsims_talent_layout.json, copied from ui/sim/talents/trees/<class>.json at commit 48c77eb).
They give the cell of every moved or new talent, which Blizzard's notes do not. Each spec listed in that file is laid out as WoWSims draws it; the
talents the notes rename keep their icon, new talents have no icon yet. The descriptions of new talents are written from the spell rows of the same
simulator (values per rank); the French names of the new talents are not known, the English name is kept.

Remove this module (and wowsims_talent_layout.json) once a client build carries the trees and has been re-imported.
"""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = {"label": "WoWSims Forever talent trees (open source, MIT)", "url": "https://github.com/wowsims/forever/tree/master/ui/sim/talents/trees"}
_LAYOUT = json.loads((Path(__file__).with_name("wowsims_talent_layout.json")).read_text(encoding="utf-8"))["classes"]
QUESTION_MARK = "https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg"


def _t(en, fr):
    return {"en": en, "fr": fr}


def _fmt(x: float) -> str:
    return f"{x:g}"


# talents of the notes that take the cell of an old one (same spec): (class, spec, old EN name) -> (new EN name, EN rank texts, FR rank texts)
RENAME = {
    ("rogue", "combat", "Improved Eviscerate"): ("Coup de Grace",
        ["Increases the damage of your Eviscerate ability by 7%, and the damage Death Mark stores and its maximum by 7%.",
         "Increases the damage of your Eviscerate ability by 13%, and the damage Death Mark stores and its maximum by 13%.",
         "Increases the damage of your Eviscerate ability by 20%, and the damage Death Mark stores and its maximum by 20%."],
        ["Augmente de 7 % les dégâts de votre technique Éviscération, ainsi que les dégâts stockés par Death Mark et son maximum.",
         "Augmente de 13 % les dégâts de votre technique Éviscération, ainsi que les dégâts stockés par Death Mark et son maximum.",
         "Augmente de 20 % les dégâts de votre technique Éviscération, ainsi que les dégâts stockés par Death Mark et son maximum."]),
    ("rogue", "combat", "Improved Sinister Strike"): ("Efficient Strikes",
        ["Reduces the energy cost of your Sinister Strike ability by 3.", "Reduces the energy cost of your Sinister Strike ability by 5."],
        ["Réduit de 3 le coût en énergie de votre technique Attaque pernicieuse.", "Réduit de 5 le coût en énergie de votre technique Attaque pernicieuse."]),
    ("warrior", "fury", "Raging Blows"): ("Reckless Swings",
        ["Active, 15 sec cooldown, costs 25% of your base health. For 8 sec, your next 4 melee attacks each give you 5 additional Rage."],
        ["Actif, 15 s de recharge, coûte 25 % de votre santé de base. Pendant 8 s, vos 4 prochaines attaques en mêlée vous donnent chacune 5 points de rage supplémentaires."]),
    ("shaman", "elemental", "Elemental Mastery"): ("Lightning Mastery",
        ["Active, 3 min cooldown. For 15 sec, the cast time of your Lightning Bolt is reduced by 0.5 sec and your Chain Lightning has no cooldown."],
        ["Actif, 3 min de recharge. Pendant 15 s, le temps d’incantation de votre Éclair est réduit de 0,5 s et votre Chaîne d’éclairs n’a plus de temps de recharge."]),
}
# talents with no old cell to take over: (class, spec, EN name) -> (EN rank texts, FR rank texts)
NEW = {
    ("rogue", "assassination", "Blood Splatter"): (["Increases the duration of your Rupture by 6 sec and of your Garrote by 9 sec."],
        ["Augmente de 6 s la durée de votre Rupture et de 9 s celle de votre Garrot."]),
    ("rogue", "combat", "Composure"): (["Poised reduces the energy cost of your next ability by 5 more.", "Poised reduces the energy cost of your next ability by 10 more."],
        ["Posé réduit de 5 points d’énergie supplémentaires le coût de votre prochaine technique.", "Posé réduit de 10 points d’énergie supplémentaires le coût de votre prochaine technique."]),
    ("rogue", "combat", "Flash of Steel"): (
        [f"Shank returns {3 * r} more energy and its cooldown is reduced by {_fmt(0.4 * r)} sec." for r in range(1, 6)],
        [f"Shank rend {3 * r} points d’énergie de plus et son temps de recharge est réduit de {_fmt(0.4 * r).replace('.', ',')} s." for r in range(1, 6)]),
    ("rogue", "subtlety", "Quick Getaway"): (["Grants a burst of movement speed of 15% for 3 sec.", "Grants a burst of movement speed of 30% for 3 sec."],
        ["Procure un regain de vitesse de déplacement de 15 % pendant 3 s.", "Procure un regain de vitesse de déplacement de 30 % pendant 3 s."]),
    ("rogue", "subtlety", "Boot Knife"): (
        [f"Your Shank has a {20 * r}% chance to give you 2 combo points." for r in range(1, 6)],
        [f"Votre Shank a {20 * r} % de chances de vous donner 2 points de combo." for r in range(1, 6)]),
    ("warrior", "fury", "Improved Whirlwind"): (["Reduces the cooldown of your Whirlwind ability by 1 sec.", "Reduces the cooldown of your Whirlwind ability by 2 sec."],
        ["Réduit de 1 s le temps de recharge de votre technique Tourbillon.", "Réduit de 2 s le temps de recharge de votre technique Tourbillon."]),
}


def apply_layout(cls: dict) -> list[str]:
    log: list[str] = []
    cid = cls["id"]
    for spec in cls["specs"]:
        tree = _LAYOUT.get(cid, {}).get(spec["id"])
        if not tree:
            continue
        by_name = {t["name"]["en"]: t for t in spec["talents"]}
        for (c, sp, old), (new, en, fr) in RENAME.items():
            if c == cid and sp == spec["id"] and old in by_name:
                t = by_name.pop(old)
                t["name"] = _t(new, new)
                t["desc"] = {"en": list(en), "fr": list(fr)}
                t["max_rank"] = len(en)
                t["announced"] = True
                by_name[new] = t
                log.append(f"{cid}/{old}: renamed {new}")
        keep: list[dict] = []
        placed: dict[tuple[int, int], dict] = {}
        for node in tree:
            t = by_name.get(node["name"])
            if t is None:
                key = (cid, spec["id"], node["name"])
                if key not in NEW:
                    raise ValueError(f"layout: no description for new talent {key}")
                en, fr = NEW[key]
                t = {"id": f"w{node['spell']}", "name": _t(node["name"], node["name"]), "row": node["row"], "col": node["col"], "max_rank": len(en),
                     "desc": {"en": list(en), "fr": list(fr)}, "icon": QUESTION_MARK, "announced": True}
                log.append(f"{cid}/{node['name']}: added")
            else:
                if (t["row"], t["col"]) != (node["row"], node["col"]):
                    log.append(f"{cid}/{node['name']}: moved to row {node['row']} col {node['col']}")
                    t["announced"] = True
                t["row"], t["col"] = node["row"], node["col"]
                if node["max"] < t["max_rank"]:
                    for lang in ("en", "fr"):
                        t["desc"][lang] = t["desc"][lang][: node["max"]]
                    t["max_rank"] = node["max"]
                    t["announced"] = True
                elif node["max"] > t["max_rank"]:
                    raise ValueError(f"layout: {cid}/{node['name']} has more ranks in the tree than text we can show")
            t.pop("gates", None)
            if t["row"] > 1:
                t["gates"] = [{"through_row": t["row"] - 1, "points": 5 * (t["row"] - 1)}]
            keep.append(t)
            placed[(node["row"], node["col"])] = t
        for t, node in zip(keep, tree):
            t.pop("requires", None)
            t.pop("requires_any", None)
            if node["prereq"]:
                src = placed[tuple(node["prereq"])]
                t["requires"] = [{"id": src["id"], "rank": src["max_rank"]}]
        names = {x["name"] for x in tree}
        for n in by_name:
            if n not in names:
                log.append(f"{cid}/{n}: removed")
        spec["talents"] = keep
    return log
