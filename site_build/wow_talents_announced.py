"""Talent changes announced by Blizzard (class tuning notes relayed by Wowhead, 3 Nov 2026) that the client tables we read do NOT carry yet.

Source: https://www.wowhead.com/forever/news/wow-forever-official-development-notes-and-class-tuning-383704
Client tables read: build 1.60.1.70753 (2 Nov 2026). The Druid, Paladin, Mage and part of the Priest / Shaman changes are already in them
(see data/wow_talents/); Warrior, Rogue, Hunter and Warlock are not, and neither are the Shaman's Flurry, Mental Dexterity and Lava Burst.

What is applied here: ONLY changes that do not need a position the notes do not give. The notes say "moved to Row 5" without a column and name
new talents without a cell, so moves and new talents are left out (the calculator pages say so). What is applied: new rank values, new rank
counts (a smaller maximum), a prerequisite change on an existing talent, a talent removed, and a talent replaced in its own cell.

Each entry is applied only while the client still shows the OLD rank count (`old_max`): the day the tables carry the new values the entry is skipped
and the client's own data is used. Remove this module once the build that holds the notes has been re-imported (wow_talents_import.py).
"""
from __future__ import annotations

import copy
import re

SOURCE = {"label": "Blizzard class tuning notes of 3 Nov 2026 (via Wowhead)",
          "url": "https://www.wowhead.com/forever/news/wow-forever-official-development-notes-and-class-tuning-383704"}

# (class, spec, talent name EN, old_max, new_max, EN pattern, FR pattern, EN values, FR values)
# The pattern's first group is the text replaced, once per rank, by the value of that rank.
VALUES = [
    ("warrior", "arms", "Improved Tactical Mastery", 5, 3, r"additional (\d+) Rage", r"jusqu’à (\d+) points de rage", [5, 10, 15], None),
    ("warrior", "arms", "Two-Handed Weapon Specialization", 3, 3, r"by (\d+)%", r"de (\d+) ?%", [2, 4, 6], None),
    ("warrior", "arms", "Bloodthrill", 5, 2, r"a (\d+)% chance", r"ont (\d+) % de chances", [10, 20], None),
    ("warrior", "arms", "Improved Slam", 2, 2, r"reduced by (-3\.0) sec", r"réduit de (-3,0) s", ["-2.5", "-5.0"], ["-2,5", "-5,0"]),
    ("warrior", "fury", "Flurry", 5, 3, r"by (\d+)%", r"de (\d+) ?%", [10, 20, 30], None),
    ("warrior", "protection", "Defiance", 3, 3, r"additional (\d+)%", r"de (\d+) % supplémentaires", [7, 13, 20], None),
    ("rogue", "assassination", "Lethality", 5, 2, r"abilities by (\d+)%", r"de (\d+) ?% le bonus", [10, 20], None),
    ("rogue", "assassination", "Seal Fate", 5, 3, r"have a (\d+)% chance", r"ont (\d+) % de chances", [33, 66, 100], None),
    ("rogue", "assassination", "Relentless Strikes", 1, 5, r"have a (\d+)% chance", r"ont (\d+) % de chances", [4, 8, 12, 16, 20], None),
    ("rogue", "combat", "Flawless Execution", 1, 1, r"by (\d+)\.", r"Réduit de (\d+) le", [15], None),
    ("rogue", "combat", "Dual Wield Specialization", 5, 2, r"by (\d+)%", r"de (\d+) ?%", [25, 50], None),
    ("rogue", "subtlety", "Opportunity", 2, 5, r"by (\d+)%", r"de (\d+) ?%", [4, 8, 12, 16, 20], None),
    ("shaman", "enhancement", "Mental Dexterity", 3, 3, r"equal to (\d+)%", r"égal à (\d+) %", [50, 100, 150], None),
    ("shaman", "enhancement", "Flurry", 5, 5, r"by (\d+)%", r"de (\d+) %", [6, 12, 18, 24, 30], None),
    ("hunter", "marksmanship", "Barrage", 3, 3, r"by (\d+)%", r"de (\d+) ?%", [5, 10, 15], None),
    ("hunter", "survival", "Lightning Reflexes", 5, 5, r"by (\d+)%", r"de (\d+) ?%", [3, 6, 9, 12, 15], None),
]
# Shadow and Flame carries two numbers per text (Shadow and Fire): replaced together.
VALUES_ALL = [
    ("warlock", "destruction", "Shadow and Flame", 5, 5, r"by (\d+)%", r"de (\d+) ?%", [4, 8, 12, 16, 20], None),
]
# Literal rewrites on every rank text: (class, spec, name, EN old, EN new, FR old, FR new)
TEXT = [
    ("rogue", "combat", "Aggression", "Sinister Strike, Backstab, and Eviscerate abilities", "Sinister Strike and Eviscerate abilities",
     "Attaque pernicieuse, Attaque sournoise et Eviscération", "Attaque pernicieuse et Éviscération"),
    ("rogue", "subtlety", "Hemorrhage", "increased Rupture damage", "increased Rupture and Garrote damage", "dégâts de Rupture", "dégâts de Rupture et de Garrot"),
]
# Aggression keeps its old maximum (3) but its values become 5/10/15
VALUES_EXTRA = [
    ("rogue", "combat", "Aggression", 3, 3, r"by (\d+)%", r"de (\d+) ?%", [5, 10, 15], None),
]
# Lava Burst is removed and replaced, in its own cell, by Call of Thunder (the French name is not known: the English name is kept)
REPLACE = [
    ("shaman", "elemental", "Lava Burst", {"en": "Call of Thunder", "fr": "Call of Thunder"},
     {"en": "Increases the critical strike chance of your Lightning Bolt and Chain Lightning spells by 5%.",
      "fr": "Augmente de 5 % les chances d’infliger un coup critique avec vos sorts Éclair et Chaîne d’éclairs."}),
    # Venom keeps its cell and name but becomes a passive tied to Shank; Thousand Cuts is replaced by Death Mark (English name kept: no French name known)
    ("rogue", "assassination", "Venom", None,
     {"en": "Passive. Your Shank ability increases your Poison damage by 30% and your chance to apply Poisons by 20% for 6 sec.",
      "fr": "Passif. Votre technique Shank augmente de 30 % les dégâts de vos poisons et de 20 % vos chances d’appliquer des poisons pendant 6 s."}),
    ("rogue", "subtlety", "Thousand Cuts", {"en": "Death Mark", "fr": "Death Mark"},
     {"en": "Finishing move that marks the target, storing a portion of the damage dealt by your attacks per Combo Point. Garrote and Rupture damage is stored at twice the rate. After 6 sec, the stored damage is dealt, up to a maximum increased by Attack Power and Critical Strike chance.",
      "fr": "Coup de grâce qui marque la cible et stocke une partie des dégâts que vos attaques infligent, par point de combo. Les dégâts de Garrot et de Rupture sont stockés deux fois plus vite. Après 6 s, les dégâts stockés sont infligés, jusqu’à un maximum augmenté par la puissance d’attaque et le taux de critique."}),
]
REMOVE = [("rogue", "assassination", "Murder", 2), ("rogue", "subtlety", "Quietus", 5), ("rogue", "subtlety", "Cutthroat", 5),
          ("rogue", "subtlety", "Improved Distract", 2)]            # (class, spec, name, old_max): gone in the notes of 3 Nov 2026
REQUIRES = [                                                       # (class, spec, name, old requires id name or None -> new requirement name)
    ("warrior", "fury", "Flurry", "Death Wish", None),             # Flurry no longer needs Death Wish
    ("warrior", "fury", "Bloodthirst", None, "Death Wish"),        # Bloodthirst now does
]


def _sub(text: str, pattern: str, value, every: bool) -> str:
    pattern = pattern.replace(' ?', '<SP?>').replace(' ', '<SP>').replace('<SP?>', '[ \u00a0\u202f]?').replace('<SP>', '[ \u00a0\u202f]')      # the French texts use no-break spaces before % and between words
    n = 0

    def f(m):
        nonlocal n
        n += 1
        return m.group(0).replace(m.group(1), str(value), 1)
    out = re.sub(pattern, f, text) if every else re.sub(pattern, f, text, count=1)
    return out


def _find(cls: dict, spec_id: str, name: str):
    for s in cls["specs"]:
        if s["id"] == spec_id:
            for t in s["talents"]:
                if t["name"]["en"] == name:
                    return s, t
    return None, None


def _rank_texts(t: dict, old_max: int, new_max: int, lang: str, pattern: str, values, every: bool) -> list[str]:
    old = t["desc"][lang]
    out = []
    for i in range(1, new_max + 1):
        base = old[min(i, old_max) - 1]
        out.append(_sub(base, pattern, values[i - 1], every))
    return out


def apply(cls: dict) -> list[str]:
    """Patch one class (dict from data/wow_talents/<id>.json) in place; returns what was applied (for the build log)."""
    cid = cls["id"]
    log: list[str] = []
    for table, every in ((VALUES, False), (VALUES_ALL, True), (VALUES_EXTRA, False)):
        for c, sp, name, old_max, new_max, pen, pfr, ven, vfr in table:
            if c != cid:
                continue
            s, t = _find(cls, sp, name)
            if not t or t["max_rank"] != old_max:
                continue                                           # not there, or the client already carries the new rank count
            en = _rank_texts(t, old_max, new_max, "en", pen, ven, every)
            fr = _rank_texts(t, old_max, new_max, "fr", pfr, vfr or ven, every)
            if t["desc"]["en"] == en and t["desc"]["fr"] == fr:
                continue
            t["desc"] = {"en": en, "fr": fr}
            if new_max != old_max:
                t["max_rank"] = new_max
            t["announced"] = True
            log.append(f"{cid}/{name}: {old_max}->{new_max} ranks")
    for c, sp, name, en_old, en_new, fr_old, fr_new in TEXT:
        if c != cid:
            continue
        s, t = _find(cls, sp, name)
        if t and any(en_old in x for x in t["desc"]["en"]):
            t["desc"]["en"] = [x.replace(en_old, en_new) for x in t["desc"]["en"]]
            t["desc"]["fr"] = [x.replace(fr_old, fr_new) for x in t["desc"]["fr"]]
            t["announced"] = True
            log.append(f"{cid}/{name}: text")
    for c, sp, name, new_name, new_desc in REPLACE:
        if c != cid:
            continue
        s, t = _find(cls, sp, name)
        if t:
            if new_name:
                t["name"] = dict(new_name)
            t["desc"] = {"en": [new_desc["en"]], "fr": [new_desc["fr"]]}
            t["announced"] = True
            log.append(f"{cid}/{name}: replaced" + (f" by {new_name['en']}" if new_name else " (text)"))
    for c, sp, name, old_max in REMOVE:
        if c != cid:
            continue
        s, t = _find(cls, sp, name)
        if t and t["max_rank"] == old_max:
            gone = t["id"]
            s["talents"] = [x for x in s["talents"] if x["id"] != gone]
            for x in s["talents"]:                                   # nothing may point at a removed talent
                for key in ("requires", "requires_any"):
                    v = x.get(key)
                    if v:
                        keep = [q for q in (v if isinstance(v, list) else [v]) if q["id"] != gone]
                        if keep:
                            x[key] = keep
                        else:
                            x.pop(key)
            log.append(f"{cid}/{name}: removed")
    for c, sp, name, drop, add in REQUIRES:
        if c != cid:
            continue
        s, t = _find(cls, sp, name)
        if not t:
            continue
        ids = {x["name"]["en"]: x["id"] for x in s["talents"]}
        cur = t.get("requires")
        cur = cur if isinstance(cur, list) else ([cur] if cur else [])
        if drop and any(q["id"] == ids.get(drop) for q in cur):
            cur = [q for q in cur if q["id"] != ids[drop]]
            t["announced"] = True
            log.append(f"{cid}/{name}: no longer requires {drop}")
        if add and not any(q["id"] == ids.get(add) for q in cur):
            cur = cur + [{"id": ids[add], "rank": 1}]
            t["announced"] = True
            log.append(f"{cid}/{name}: now requires {add}")
        if cur:
            t["requires"] = cur
        else:
            t.pop("requires", None)
    byid = {x["id"]: x for sp in cls["specs"] for x in sp["talents"]}      # a prerequisite is the source talent at its MAXIMUM rank: follow a lowered maximum
    for x in byid.values():
        for key in ("requires", "requires_any"):
            v = x.get(key)
            for q in ([] if not v else (v if isinstance(v, list) else [v])):
                tgt = byid.get(q["id"])
                if tgt and q["rank"] > tgt["max_rank"]:
                    q["rank"] = tgt["max_rank"]
    return log


def apply_all(classes: list[dict]) -> dict[str, list[str]]:
    return {c["id"]: apply(c) for c in classes}
