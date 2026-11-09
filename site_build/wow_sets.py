"""WoW: Forever "Sanctified" class sets (item level 98, sold in Eastern Plaguelands by the Argent Dawn and Scarlet quartermasters).

Data (nothing invented): data/wow_items/sanctified_items.txt (every piece with its Forever stats) and data/wow_items/sanctified_sets.json (the 2/4/6-piece bonuses),
both read from Wowhead's Forever item and item-set pages. The French sentences are our own paraphrase of the bonus texts; ability names stay in English (the Forever
client has no French names for the new abilities yet). What the simulator does with the sets comes from the ranking data (which pieces the best setup equips).
"""
from __future__ import annotations

import json
from pathlib import Path

P = Path(__file__).resolve().parent.parent
ITEMS_TXT = P / "data" / "wow_items" / "sanctified_items.txt"
SETS_JSON = P / "data" / "wow_items" / "sanctified_sets.json"

CLASS_OF_BIT = {1: "warrior", 2: "paladin", 4: "hunter", 8: "rogue", 16: "priest", 64: "shaman", 128: "mage", 256: "warlock", 1024: "druid"}
SLOT_ORDER = [1, 3, 5, 9, 10, 6, 7, 8]
SLOT = {
    "fr": {1: "Tête", 3: "Épaules", 5: "Torse", 9: "Poignets", 10: "Mains", 6: "Taille", 7: "Jambes", 8: "Pieds"},
    "en": {1: "Head", 3: "Shoulders", 5: "Chest", 9: "Wrists", 10: "Hands", 6: "Waist", 7: "Legs", 8: "Feet"},
}
STAT = {
    "fr": {"str": "Force", "agi": "Agilité", "int": "Intelligence", "sta": "Endurance", "spi": "Esprit", "splpwr": "Puissance des sorts", "splheal": "Soins",
           "shasplpwr": "Puissance des sorts d'Ombre", "rgdatkpwr": "Puissance d'attaque à distance", "atkpwr": "Puissance d'attaque", "critstrkrtng": "Critique",
           "hitrtng": "Toucher", "hastertng": "Hâte", "exprtng": "Expertise", "defrtng": "Défense", "blockrtng": "Blocage", "blockamount": "Valeur de blocage", "armorbonus": "Armure bonus"},
    "en": {"str": "Strength", "agi": "Agility", "int": "Intellect", "sta": "Stamina", "spi": "Spirit", "splpwr": "Spell Power", "splheal": "Healing",
           "shasplpwr": "Shadow Spell Power", "rgdatkpwr": "Ranged Attack Power", "atkpwr": "Attack Power", "critstrkrtng": "Crit", "hitrtng": "Hit",
           "hastertng": "Haste", "exprtng": "Expertise", "defrtng": "Defense", "blockrtng": "Block", "blockamount": "Block Value", "armorbonus": "Bonus Armor"},
}
STAT_ORDER = ["str", "agi", "int", "spi", "splpwr", "shasplpwr", "splheal", "atkpwr", "rgdatkpwr", "critstrkrtng", "hitrtng", "hastertng", "exprtng", "defrtng", "blockrtng", "blockamount", "sta"]

# set id -> (French role label, English role label)
SPEC = {
    "1932": ("Guerrier Fureur (dégâts)", "Fury Warrior (damage)"), "1933": ("Guerrier Protection (tank)", "Protection Warrior (tank)"),
    "1934": ("Voleur (dégâts)", "Rogue (damage)"), "1935": ("Voleur (tank)", "Rogue (tank)"),
    "1936": ("Chasseur corps à corps", "Melee Hunter"), "1937": ("Chasseur à distance", "Ranged Hunter"),
    "1938": ("Prêtre Ombre", "Shadow Priest"), "1939": ("Prêtre soigneur", "Healer Priest"),
    "1940": ("Paladin Vindicte", "Retribution Paladin"), "1941": ("Paladin Sacré", "Holy Paladin"), "1942": ("Paladin Protection", "Protection Paladin"),
    "1963": ("Paladin Vindicte à puissance des sorts", "Spell-power Retribution Paladin"),
    "1943": ("Mage (Feu et Givre)", "Mage (Fire and Frost)"), "1944": ("Mage (Arcanes)", "Mage (Arcane)"),
    "1945": ("Druide Farouche", "Feral Druid"), "1946": ("Druide Équilibre", "Balance Druid"), "1947": ("Druide Restauration", "Restoration Druid"), "1948": ("Druide gardien (ours)", "Guardian Druid (bear)"),
    "1949": ("Chaman tank", "Tank Shaman"), "1950": ("Chaman Restauration", "Restoration Shaman"), "1951": ("Chaman Amélioration", "Enhancement Shaman"), "1952": ("Chaman Élémentaire", "Elemental Shaman"),
    "1953": ("Démoniste tank", "Tank Warlock"), "1954": ("Démoniste (dégâts)", "Warlock (damage)"),
}

# French paraphrase of each bonus (pieces -> sentence). Ability names stay in English.
FR = {
    "1932": ["Heroic Strike, Cleave et Quick Strike font 20 % de dégâts en plus en posture de Combat ou Berserker ; Cleave touche une cible de plus et peut déclencher Blood Surge.",
             "Chaque coup de Whirlwind, Heroic Strike, Quick Strike ou Cleave augmente de 20 % les dégâts du prochain Slam, jusqu'à 5 cumuls.",
             "Chaque tick de Deep Wounds réduit de 3 s le temps de recharge de Whirlwind, qui inflige 100 % de dégâts en plus aux cibles saignant sous Deep Wounds."],
    "1933": ["Shockwave inflige 35 % de dégâts en plus, et chaque Heroic Strike ou Cleave qui touche réduit sa recharge de 2 s.",
             "Recklessness, Retaliation et Shield Wall ne partagent plus leur recharge ; Recklessness dure 15 s de plus et convertit 50 % de votre Défense au-delà de 300 en Force.",
             "Plus aucune contrainte de posture ; Revenge, Devastate et Shield Slam augmentent de 20 % le prochain Whirlwind ou Execute, jusqu'à 5 cumuls."],
    "1934": ["Backstab, Sinister Strike, Saber Slash et Mutilate font 20 % de dégâts en plus par poison ou saignement actif sur la cible (maximum 60 %), tant que Just a Flesh Wound n'est pas actif.",
             "Les critiques de poison et d'attaque automatique ont 10 % de chances de donner un point de combo.",
             "Ambush, Eviscerate, Crimson Tempest et Envenom font 50 % de dégâts en plus."],
    "1935": ["Chaque cumul de Rolling with the Punches augmente aussi vos dégâts de 1 %.",
             "Blade Flurry frappe une troisième cible et ajoute 10 % de vitesse d'attaque ; chaque point de combo dépensé réduit sa recharge de 0,5 s.",
             "Rolling with the Punches donne 2 % de vie et 1 % de dégâts de plus par cumul ; à 5 cumuls, chaque esquive ou parade rend 10 d'énergie."],
    "1936": ["Les Strikes et Mongoose Bite font 20 % de dégâts en plus aux cibles touchées par Serpent Sting ou Wyvern Strike.",
             "Vos critiques au corps à corps donnent 20 % de vitesse d'attaque pendant 10 s.",
             "Le bonus de dégâts de Raptor Fury augmente de 10 % de plus par cumul."],
    "1937": ["Vos tirs font 20 % de dégâts en plus aux cibles touchées par Serpent Sting.",
             "Vos critiques à distance donnent 20 % de puissance d'attaque pendant 10 s.",
             "Multi-Shot touche 2 cibles de plus ; chaque touche de Kill Shot ou Chimera Shot augmente de 75 % le prochain Multi-Shot (12 s), jusqu'à 4 cumuls."],
    "1938": ["Mind Flay et Mind Sear ne perdent plus de durée quand vous subissez des dégâts et font 10 % de dégâts en plus par autre effet d'Ombre périodique sur la cible (maximum 30 %).",
             "Mind Blast ne génère plus de menace et gagne 20 % de dégâts par cumul de Mind Spike sur la cible.",
             "Les dégâts de Mind Flay augmentent tout au long de l'incantation et reviennent à zéro à chaque nouvelle incantation (la valeur exacte n'est pas lisible dans les données de Wowhead)."],
    "1939": ["Power Word: Barrier a 30 s de recharge en moins ; Surge of Light rend aussi Prayer of Healing et Greater Heal instantanés.",
             "Power Word: Shield soigne aussitôt la cible de 20 % de son absorption ; les sorts renforcés par Serendipity soignent 10 % de plus par cumul.",
             "Circle of Healing et Penance soignent 25 % de plus ; Spirit of the Redeemer a une recharge réduite et vos soins augmentent de 20 % pendant qu'il est actif."],
    "1940": ["Avec une arme à deux mains, Crusader Strike et Exorcism donnent du Holy Power : +20 % de dégâts Sacré par cumul, jusqu'à 3.",
             "Divine Storm, Holy Shock et Holy Wrath consomment tout le Holy Power et font 100 % de dégâts en plus par cumul (50 % d'efficacité contre les joueurs).",
             "Consommer du Holy Power donne 10 % de puissance d'attaque par cumul consommé pendant 10 s."],
    "1941": ["Lay on Hands donne 20 % de hâte des sorts pendant 30 s et réduit de 0,5 s le temps de recharge global des 5 prochains Divine Light, Holy Light, Flash of Light ou Holy Shock.",
             "Beacon of Light se déclenche aussi quand vous soignez la cible du Beacon, mais avec une efficacité réduite à zéro.",
             "25 % de vos soins sont transférés en plus vers la cible de Beacon of Light."],
    "1942": ["Shield of Righteousness double aussi votre valeur de blocage pendant 6 s.",
             "Shield of Righteousness inflige un pourcentage de dégâts en plus égal à votre chance de blocage.",
             "Avenging Wrath ne déclenche plus Forbearance et augmente votre valeur de blocage de 30 %."],
    "1963": ["Tant que Shock and Awe est actif, Crusader Strike et Exorcism donnent du Holy Power : +20 % de dégâts Sacré par cumul, jusqu'à 3.",
             "Divine Storm, Holy Shock et Holy Wrath consomment tout le Holy Power et font 100 % de dégâts en plus par cumul (50 % d'efficacité contre les joueurs)."],
    "1943": ["Living Bomb inflige ses dégâts plus souvent (la valeur exacte n'est pas lisible dans les données) et explose si la cible meurt ; Glaciate (rune d'Ice Lance) se cumule jusqu'à 4 fois et Spellfrost Bolt en donne 2.",
             "Frozen Orb a 25 s de recharge en moins ; consommer Glaciate réduit la recharge de Deep Freeze de 1 s par cumul ; Fire Blast a 5 s de recharge en moins et rafraîchit Living Bomb sur la cible."],
    "1944": ["Arcane Blast a 10 % de chances de déclencher Arcane Tunneling, qui empêche le prochain autre sort Arcanes de consommer l'effet d'Arcane Blast ; Arcane Power remet à zéro la recharge de Mass Regeneration.",
             "Rewind Time réduit aussi de 20 % les dégâts subis par la cible pendant 8 s.",
             "Arcane Power dure 10 s de plus, la chance d'Arcane Tunneling augmente de 10 % pendant sa durée et chaque Arcane Blast réduit de 1 s la recharge de Mass Regeneration."],
    "1945": ["Chaque tick de Rake ou Rip rend 2 d'énergie.",
             "Le bonus de dégâts de Tiger's Fury est doublé.",
             "Vos finishers ont 20 % de chances par point de combo de déclencher Clearcasting et de prolonger Tiger's Fury de 6 s."],
    "1946": ["Starfire fait 20 % de dégâts en plus sur les cibles sous Moonfire, et Wrath 20 % de plus sur les cibles sous Sunfire.",
             "Starsurge augmente les dégâts de vos 2 prochains Starfire.",
             "Chaque tick de Sunfire donne +10 % au prochain Wrath, chaque tick de Moonfire +10 % au prochain Starfire, jusqu'à 5 cumuls (sans effet sur Starsurge)."],
    "1947": ["Chaque soin de Lifebloom a 5 % de chances de rendre instantané votre prochain Healing Touch, Nourish ou Regrowth (15 s).",
             "Les cibles sous Rejuvenation de rang 10 ou 11 reçoivent 20 % de soins en plus de vos sorts.",
             "Les soins directs de Regrowth de rang 8 ou 9 propagent votre Rejuvenation à tout le groupe à portée."],
    "1948": ["Vos critiques en forme d'ours donnent un bouclier de 10 s qui absorbe des dégâts physiques égaux à 25 % de votre puissance d'attaque, jusqu'à 3 cumuls.",
             "Berserk dure 15 s de plus.",
             "Chaque critique donne 4 % de vitesse d'attaque pendant 10 s."],
    "1949": ["Vos chocs activent Shield Mastery, qui peut se cumuler jusqu'à 7 fois.",
             "Chaque dégât de Lightning Shield vous soigne de 100 % de ces dégâts, au plus une fois toutes les 3 s.",
             "Les cumuls de Shield Mastery réduisent de 20 % chacun le temps d'incantation de Lava Burst, qui ne consomme plus de charges de Maelstrom Weapon."],
    "1950": ["Les soins d'Earth Shield ont 25 % de chances de rendre instantané votre prochain soin à incantation.",
             "Healing Wave et Lesser Healing Wave soignent aussi la cible d'Earth Shield pour 50 % de leur valeur.",
             "Chain Heal rebondit sur une cible de plus et perd 20 % de moins par rebond."],
    "1951": ["Tant que Static Shock est actif, Lava Lash, Lava Burst et Stormstrike ajoutent une charge à Lightning Shield ; au-delà de 9 charges, il frappe immédiatement la cible.",
             "Fire Nova Totem a 60 % de recharge en moins, fait 200 % de dégâts en plus, coûte 60 % de mana en moins et s'active instantanément.",
             "Maelstrom Weapon monte à 10 charges (2 à la fois avec une arme à deux mains) ; au-delà de 5 charges, chaque charge en trop donne 20 % de dégâts ou de soins en plus ; à 10 charges, le sort est lancé deux fois."],
    "1952": ["Quand Lava Burst, Chain Lightning ou Lightning Bolt touche une cible sous Flame Shock de rang 5 ou 6, elle subit aussi une impulsion de Flame Shock.",
             "Overload se déclenche 10 % plus souvent ; Lava Burst gagne un bonus de dégâts égal à votre chance de critique des sorts ; Lightning Bolt et Chain Lightning donnent +10 % au prochain Lava Burst (15 s), jusqu'à 5 cumuls.",
             "Chain Lightning fait 35 % de dégâts en plus par cible manquante sous 3 cibles."],
    "1953": ["Shadow Cleave applique Corruption de rang 7 à chaque cible touchée, pour 12 s.",
             "Vous vous soignez de 10 % des dégâts de Corruption, et de 100 % si la cible subit aussi Drain Life.",
             "Infernal Armor augmente aussi tous vos dégâts magiques de 20 % et dure 10 s de plus."],
    "1954": ["Vos critiques directs d'Ombre et de Feu font brûler la cible pour 25 % des dégâts infligés sur 4 s.",
             "Shadow Bolt, Haunt, Chaos Bolt, Shadow Cleave et Soul Fire font 30 % de dégâts en plus aux cibles sous Corruption.",
             "Vos critiques périodiques donnent 20 % de hâte des sorts pendant 15 s, et Backdraft en ajoute 12 %."],
}


# English bonus texts whose Wowhead wording carries an unresolved placeholder value (e.g. "every 4000 sec"): rewritten without the bogus number
EN_FIX = {
    ("1938", 2): "Damage done by your Mind Flay increases the longer you channel the spell and resets on each new channel (the exact value is not readable in Wowhead's data).",
    ("1939", 2): "Increases the healing of Circle of Healing and Penance by 25%. Your Spirit of the Redeemer has a shorter cooldown (the exact value is not readable in Wowhead's data) and your healing is increased by 20% while it is active.",
    ("1942", 2): "Your Avenging Wrath no longer triggers Forbearance, lasts slightly longer (the exact value is not readable in Wowhead's data) and increases your Block Value by 30%.",
    ("1943", 0): "Your Living Bomb now deals damage more often (the exact interval is not readable in Wowhead's data) and detonates if the target dies. In addition, the effect of Glaciate from the rune of Ice Lance now stacks up to 4 times, and Spellfrost Bolt grants 2 stacks each time it hits.",
    ("1944", 2): "Arcane Power has a shorter cooldown (the exact value is not readable in Wowhead's data) and lasts 10 sec longer. While it is active, your chance to gain Arcane Tunneling is increased by 10% and each cast of Arcane Blast reduces the remaining cooldown on Mass Regeneration by 1.0 sec.",
}


def available() -> bool:
    return ITEMS_TXT.exists() and SETS_JSON.exists()


def _stat_line(st: dict, lang: str, limit: int = 6) -> str:
    out = []
    for k in STAT_ORDER:
        if st.get(k):
            out.append(f"{st[k]} {STAT[lang][k]}")
    return ", ".join(out[:limit])


def build(lang: str, wt_classes: list, ranking_rows: list) -> dict:
    """{'classes': [{id, name, color, sets: [...]}], 'n_sets', 'n_items'}; ranking_rows are build_wow_ranking60 rows (their detail lists the best setup's items)."""
    raw = json.loads(SETS_JSON.read_text(encoding="utf-8"))
    sets_meta = raw["sets"]
    by_set: dict[str, list] = {}
    cbit_of: dict[str, int] = {}
    for line in ITEMS_TXT.read_text(encoding="utf-8").splitlines():
        iid, name, slot, cbit, setid, stats = line.split("|")
        st = {kv.split("=")[0]: int(kv.split("=")[1]) for kv in stats.split(",")}
        by_set.setdefault(setid, []).append({"id": int(iid), "name": name, "slot": int(slot), "st": st})
        cbit_of[setid] = int(cbit)
    # which sets the simulator's best setups equip (how many pieces of the set each spec wears)
    worn: dict[str, list] = {}
    ids_of = {sid: {i["id"] for i in its} for sid, its in by_set.items()}
    for r in ranking_rows:
        its = ((r.get("detail") or {}).get("items")) or []
        for sid, ids in ids_of.items():
            n = sum(1 for it in its if it.get("id") in ids)
            if n >= 2:
                worn.setdefault(sid, []).append({"spec": r["spec_name"], "n": n, "path": r["page_path"]})
    classes = []
    for c in wt_classes:
        sets = []
        for sid in sorted(by_set, key=int):
            if CLASS_OF_BIT[cbit_of[sid]] != c["id"]:
                continue
            pieces = sorted(by_set[sid], key=lambda p: SLOT_ORDER.index(p["slot"]) if p["slot"] in SLOT_ORDER else 99)
            tot: dict[str, int] = {}
            for p in pieces:
                for k, v in p["st"].items():
                    tot[k] = tot.get(k, 0) + v
            meta = sets_meta[sid]
            bonuses = []
            for i, (n, en_text) in enumerate(meta["bonuses"]):
                bonuses.append({"n": n, "text": FR[sid][i] if lang == "fr" else EN_FIX.get((sid, i), en_text)})
            sets.append({
                "id": sid, "title": meta["title"], "spec": SPEC[sid][0 if lang == "fr" else 1], "tank": "tank" in meta["spec"] or meta["spec"] in ("protection", "guardian"),
                "heal": meta["spec"] in ("healer", "holy", "restoration"),
                "pieces": [{"slot": SLOT[lang].get(p["slot"], str(p["slot"])), "name": p["name"], "id": p["id"], "stats": _stat_line(p["st"], lang), "armor": p["st"].get("armor", 0)} for p in pieces],
                "totals": _stat_line(tot, lang, 8), "n_pieces": len(pieces), "bonuses": bonuses, "worn": sorted(worn.get(sid, []), key=lambda w: -w["n"]),
            })
        if sets:
            classes.append({"id": c["id"], "name": c["name"][lang], "color": c.get("color"), "sets": sets})
    return {"classes": classes, "n_sets": sum(len(c["sets"]) for c in classes), "n_items": sum(len(v) for v in by_set.values())}


TX = {
    "fr": {
        "kicker": "WoW Forever · Ensembles Sanctified",
        "title": "Ensembles Sanctified WoW Forever : bonus et stats",
        "desc": "Les {n} ensembles Sanctified (ilvl 98) de WoW Forever : pièces, stats, bonus 2/4/6 pièces et où les obtenir, classe par classe.",
        "h1": "Ensembles Sanctified de WoW Forever, classe par classe",
        "intro": "Les ensembles Sanctified (niveau d'objet 98) sont vendus en Eastern Plaguelands par les quartermasters de l'Argent Dawn et de Scarlet. Chaque classe a un ensemble de 8 pièces par rôle, avec des bonus à 2, 4 et 6 pièces qui changent la façon de jouer. Voici les pièces, leurs stats et les bonus, avec ce que notre simulateur en fait.",
        "hub_n": "{n} ensembles",
        "cls_title": "Ensembles Sanctified du {cls} : pièces et bonus",
        "cls_desc": "Ensembles Sanctified du {cls} dans WoW Forever : pièces, stats, bonus 2/4/6 pièces et ce qu'en fait le simulateur.",
        "cls_h1": "Ensembles Sanctified du {cls}",
        "cls_intro": "Sets de niveau d'objet 98 du {cls} : pièces, stats totales et effets des bonus à 2, 4 et 6 pièces.",
        "pieces": "Pièces", "slot": "Emplacement", "item": "Objet", "stats": "Stats", "total": "Total des 8 pièces", "bonuses": "Bonus d'ensemble", "pieces_n": "{n} pièces",
        "n_pieces": "{n} pièces", "where": "Où l'obtenir",
        "where_txt": "Vendu en Eastern Plaguelands par le quartermaster de l'Argent Dawn (réputation « Revered ») et par le quartermaster de Scarlet. Le prix et la réputation exacte ne sont pas encore relevés : vérifiez-les en jeu.",
        "sim_worn": "Dans notre simulateur, la meilleure configuration porte au moins 2 pièces de cet ensemble pour :",
        "sim_none": "Notre simulateur ne retient pas ces pièces pour un classement de dégâts.",
        "sim_note": "Les statistiques des pièces sont simulées ; les bonus d'ensemble, pas encore (ils demandent des mécaniques propres à chaque classe). Les DPS publiés sont donc plutôt une borne basse pour les classes qui portent l'ensemble.",
        "src_note": "Données lues sur les pages Forever de Wowhead (objets et ensembles). Les phrases françaises sont notre reformulation ; les noms de sorts restent en anglais.",
        "role_tank": "Tank", "role_heal": "Soigneur", "role_dps": "Dégâts",
        "hub_h2": "Choisir une classe", "hub_back": "Tous les ensembles",
    },
    "en": {
        "kicker": "WoW Forever · Sanctified sets",
        "title": "WoW Forever Sanctified sets: bonuses and stats",
        "desc": "All {n} Sanctified sets (ilvl 98) in WoW Forever: pieces, stats, 2/4/6-piece bonuses and where to get them, class by class.",
        "h1": "WoW Forever Sanctified sets, class by class",
        "intro": "Sanctified sets (item level 98) are sold in Eastern Plaguelands by the Argent Dawn and Scarlet quartermasters. Each class has an 8-piece set per role, with 2, 4 and 6-piece bonuses that change how the spec plays. Here are the pieces, their stats and the bonuses, with what our simulator does with them.",
        "hub_n": "{n} sets",
        "cls_title": "{cls} Sanctified sets: pieces and bonuses",
        "cls_desc": "{cls} Sanctified sets in WoW Forever: pieces, stats, 2/4/6-piece bonuses and what the simulator does with them.",
        "cls_h1": "{cls} Sanctified sets",
        "cls_intro": "Item level 98 sets for the {cls}: pieces, total stats and the effects of the 2, 4 and 6-piece bonuses.",
        "pieces": "Pieces", "slot": "Slot", "item": "Item", "stats": "Stats", "total": "Total of the 8 pieces", "bonuses": "Set bonuses", "pieces_n": "{n} pieces",
        "n_pieces": "{n} pieces", "where": "Where to get it",
        "where_txt": "Sold in Eastern Plaguelands by the Argent Dawn quartermaster (Revered) and the Scarlet quartermaster. The exact price and reputation are not recorded yet: check them in game.",
        "sim_worn": "In our simulator the best setup wears at least 2 pieces of this set for:",
        "sim_none": "Our simulator does not pick these pieces for a damage ranking.",
        "sim_note": "The pieces' stats are simulated; the set bonuses are not yet (each needs class-specific mechanics). The published DPS is therefore more of a floor for the classes that wear a set.",
        "src_note": "Data read from Wowhead's Forever item and item-set pages. Bonus texts are the game's own.",
        "role_tank": "Tank", "role_heal": "Healer", "role_dps": "Damage",
        "hub_h2": "Pick a class", "hub_back": "All sets",
    },
}
