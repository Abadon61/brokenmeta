"""One-off: rewrites TALENT_NOTES in wow_rank_texts.py from data/wow_ranking60.json (measured talent values, tree split) + the written notes below.
Run after a ranking recompute:  py -3 site_build/_regen_talent_notes.py
The first two strings of each spec are generated (tree split, talents that weigh the most, talents measured at about zero); the following strings are the
hand-written commentary kept in KEEP (history that is still true) or NEW (what the notes of 3 Nov 2026 change)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RANK = json.loads((ROOT / "data" / "wow_ranking60.json").read_text(encoding="utf-8"))
SRC = ROOT / "site_build" / "wow_rank_texts.py"
import sys
sys.path.insert(0, str(ROOT / "site_build"))
import importlib
rt = importlib.import_module("wow_rank_texts")
OLD = rt.TALENT_NOTES

TOP_MIN = 14        # a talent is listed as "weighing the most" from this DPS loss
PCT_MIN = 10.0      # the share of the DPS is shown from this value


def split_text(spec, lang):
    d = spec["detail"]
    names = {}
    for t in d["talents"]:
        names[t["tree"]] = t["tree_name"][lang]
    parts = sorted(d["trees"].items(), key=lambda kv: -kv[1])
    word = " et " if lang == "fr" else " and "
    inn = "dans" if lang == "fr" else "in"
    return word.join(f"{n} {inn} {names.get(k, k)}" for k, n in parts)


def measured(spec, lang):
    tv = spec["detail"]["talentValues"]
    top = sorted(((n, v) for n, v in tv.items() if v and v["gain"] >= TOP_MIN), key=lambda x: -x[1]["gain"])[:8]
    low = [n for n, v in tv.items() if not v or v["gain"] < TOP_MIN]
    sp = " %" if lang == "fr" else "%"
    items = ", ".join(n + (f" (−{v['gain']:.0f}, {v['pct']:.0f}{sp})" if v["pct"] >= PCT_MIN else f" (−{v['gain']:.0f})") for n, v in top)
    if lang == "fr":
        a = f"{split_text(spec, 'fr')}. Talents qui pèsent le plus (perte de DPS sans eux, mesurée dans le simulateur) : {items}." if top else f"{split_text(spec, 'fr')}."
        b = f"Mesurés à près de zéro ou non simulés (points de passage, remplissage ou effets hors DPS) : {', '.join(low)}." if low else None
    else:
        a = f"{split_text(spec, 'en')}. The talents that weigh the most (DPS lost without them, measured in the simulator): {items}." if top else f"{split_text(spec, 'en')}."
        b = f"Measured at about zero or not simulated (gate points, filler or non-damage effects): {', '.join(low)}." if low else None
    return [a] + ([b] if b else [])


def dps_of(spec_id, ability):
    s = next(x for x in RANK["specs"] if x["spec"] == spec_id)
    a = next((x for x in s["detail"]["abilities"] if x["name"] == ability), None)
    return None if a is None else a["dps"]


# History that is still true (third string of the previous TALENT_NOTES) -> kept as is. Everything else is replaced by NEW.
KEEP = {"warrior_fury", "warlock_affliction", "hunter_melee", "priest_shadow"}

NEW = {}
shank = lambda sid: dps_of(sid, "Shank")
for sid, extra_fr, extra_en in [
    ("rogue_combat", "", ""),
    ("rogue_assassination", " Venom (désormais lié à Shank : +30 % de dégâts des poisons et +20 % de chances de les appliquer pendant 6 s) est simulé.", " Venom (now tied to Shank: +30% poison damage and +20% chance to apply poisons for 6 s) is simulated."),
    ("rogue_subtlety", " Quietus, Cutthroat et Improved Distract ont disparu ; Opportunity passe à 5 rangs (+4 % par rang).", " Quietus, Cutthroat and Improved Distract are gone; Opportunity goes to 5 ranks (+4% per rank)."),
]:
    d = shank(sid)
    NEW[sid] = (
        [f"Les notes du 3 novembre sont appliquées : le nouveau sort Shank (niveau 24, 5 énergie, 10 s de recharge, 25 énergie rendus au rang 2) est lancé dès qu'il ne fait pas dépasser le plafond d'énergie ({d:.0f} DPS directs, et surtout l'énergie qu'il rend aux constructeurs ; hypothèse : il utilise le délai global de 1 s). Lethality n'a plus que 2 rangs (+10 / 20 %), Relentless Strikes passe à 5 rangs, Dual Wield Specialization à 2 rangs (+25 / 50 %), Seal Fate à 3 rangs, Aggression donne 5 / 10 / 15 % à Sinister Strike et Eviscerate (plus à Backstab), Mutilate fait 90 % des dégâts d'arme et les poisons ont leur coefficient de puissance d'attaque doublé.{extra_fr} Non simulés (positions non publiées) : Blood Splatter, Boot Knife, Flash of Steel, Composure, Poised et Death Mark."],
        [f"The notes of November 3 are applied: the new Shank spell (level 24, 5 energy, 10 s cooldown, 25 energy returned at rank 2) is cast whenever it does not push the energy past the cap ({d:.0f} direct DPS, and above all the energy it gives back to the builders; assumption: it uses the 1 s global cooldown). Lethality has only 2 ranks (+10 / 20%), Relentless Strikes goes to 5 ranks, Dual Wield Specialization to 2 ranks (+25 / 50%), Seal Fate to 3 ranks, Aggression gives 5 / 10 / 15% to Sinister Strike and Eviscerate (no longer Backstab), Mutilate deals 90% weapon damage and the poisons' attack power coefficient is doubled.{extra_en} Not simulated (positions not published): Blood Splatter, Boot Knife, Flash of Steel, Composure, Poised and Death Mark."],
    )
NEW["warrior_fury"] = (
    ["Les notes du 3 novembre : Flurry passe à 3 rangs de +10 % de vitesse d'attaque (5 rangs de +5 % avant) et ne demande plus Death Wish, Improved Tactical Mastery n'a plus que 3 rangs. Reckless Swings et Improved Whirlwind, nouveaux talents de Fureur, ne sont pas simulés (leur position n'est pas publiée). Les points libérés vont dans Improved Berserker Rage (+2 % de DPS mesurés) et Blood Craze."],
    ["The notes of November 3: Flurry goes to 3 ranks of +10% attack speed (5 ranks of +5% before) and no longer requires Death Wish, Improved Tactical Mastery has only 3 ranks. Reckless Swings and Improved Whirlwind, new Fury talents, are not simulated (their position is not published). The freed points go to Improved Berserker Rage (+2% DPS measured) and Blood Craze."],
)
NEW["warrior_arms"] = (
    ["Slam a 15 s de recharge depuis les notes du 3 novembre (18 s avant) et Improved Slam la réduit de 2,5 s au rang 1 et de 5 s au rang 2, en plus de supprimer le délai d'attaque. Bloodthrill n'a plus que 2 rangs (10 / 20 % de chances d'activer Overpower) et Two-Handed Weapon Specialization donne 2 / 4 / 6 %. Mortal Strike reste le coup principal du build. Unbridled Wrath ne donne plus 2 rages avec une arme à deux mains depuis le patch du 15 octobre."],
    ["Slam has a 15 s cooldown since the notes of November 3 (18 s before) and Improved Slam shortens it by 2.5 s at rank 1 and 5 s at rank 2, on top of removing the swing delay. Bloodthrill has only 2 ranks (10 / 20% chance to enable Overpower) and Two-Handed Weapon Specialization gives 2 / 4 / 6%. Mortal Strike stays the main strike of the build. Unbridled Wrath no longer gives 2 rage with a two-hander since the October 15 patch."],
)
NEW["mage_fire"] = (
    ["Notes du 3 novembre : Critical Mass revient à 3 rangs (+6 % de critique, 10 % avant) et Incineration passe à 5 rangs (+10 %). Accelerant (ex-Improved Fireball) raccourcit aussi Arcane Wrath, Elemental Precision devient Precision (3 rangs, +6 % de toucher avec tous les sorts) et Piercing Ice a disparu. Fire Power compte les effets de feu sur la cible (Ignite, Improved Scorch, dégâts sur la durée de Fireball et de Pyroblast : +1 % par rang et par effet, 4 effets au plus) et Fire Blast ajoute une charge de Heating Up à chaque lancer."],
    ["Notes of November 3: Critical Mass goes back to 3 ranks (+6% crit, 10% before) and Incineration to 5 ranks (+10%). Accelerant (formerly Improved Fireball) also shortens Arcane Wrath, Elemental Precision becomes Precision (3 ranks, +6% hit with all spells) and Piercing Ice is gone. Fire Power counts the fire effects on the target (Ignite, Improved Scorch, the damage over time of Fireball and Pyroblast: +1% per rank and per effect, 4 effects at most) and Fire Blast adds a Heating Up charge on every cast."],
)
NEW["mage_frost"] = (
    ["Notes du 3 novembre : Ice Lance refait +300 % contre une cible gelée mais a 8 s de recharge partagée avec Fire Blast. Ice Barrier (talent de palier 7, il exige Cold Snap) donne +15 % de dégâts de givre pendant 1 minute : le simulateur le compte comme actif en permanence. Piercing Ice a disparu et Elemental Precision devient Precision (3 rangs). Winter's Chill ne renforce que Cone of Cold : ses 5 points ne servent ici qu'à atteindre Ice Barrier."],
    ["Notes of November 3: Ice Lance does +300% against a Frozen target again but has an 8 s cooldown shared with Fire Blast. Ice Barrier (a row-7 talent, it requires Cold Snap) gives +15% Frost damage for 1 minute: the simulator counts it as always active. Piercing Ice is gone and Elemental Precision becomes Precision (3 ranks). Winter's Chill only strengthens Cone of Cold: its 5 points are here only to reach Ice Barrier."],
)
NEW["mage_arcane"] = (
    ["Notes du 3 novembre : Arcane Blast coûte +100 % de mana par charge (175 % avant), donne 12 % de l'Intelligence en puissance des sorts par charge (15 % avant) et dure 18 s (15 s avant). Le simulateur compare à chaque combat « Arcane Blast puis Wrath et Missiles » à « Wrath et Missiles seuls » et reste sur ce dernier ; ce choix repose sur un calcul de dégâts par seconde avec le coût en mana, pas sur une mesure combat contre combat. Arcane Focus a disparu, absorbé par Precision (3 rangs, +6 % de toucher), et Arcane Wrath a 3,5 s d'incantation, raccourcie par Accelerant."],
    ["Notes of November 3: Arcane Blast costs +100% mana per stack (175% before), gives 12% of the Intellect as spell damage per stack (15% before) and lasts 18 s (15 s before). The simulator compares \"Arcane Blast, then Wrath and Missiles\" with \"Wrath and Missiles alone\" on every fight and stays on the latter; that choice rests on a damage-per-second estimate with the mana cost folded in, not on a fight-against-fight measurement. Arcane Focus is gone, absorbed by Precision (3 ranks, +6% hit), and Arcane Wrath has a 3.5 s cast, shortened by Accelerant."],
)
d = dps_of("warlock_affliction", "Wrack")
NEW["warlock_affliction"] = (
    ["Notes du 3 novembre : Wrack double son coefficient de puissance des sorts et passe à 86 dégâts de base par seconde au niveau 60 (36 avant), ce qui relève nettement la spécialisation. Improved Drains ne renforce plus Wrack."],
    ["Notes of November 3: Wrack doubles its spell power coefficient and goes to 86 base damage per second at level 60 (36 before), which lifts the specialization clearly. Improved Drains no longer strengthens Wrack."],
)
NEW["warlock_destruction"] = (
    ["Notes du 3 novembre : Shadow and Flame donne 4 / 8 / 12 / 16 / 20 % de dégâts d'ombre ou de feu (2 / 4 / 6 / 8 / 10 % avant)."],
    ["Notes of November 3: Shadow and Flame gives 4 / 8 / 12 / 16 / 20% Shadow or Fire damage (2 / 4 / 6 / 8 / 10% before)."],
)
hunter_fr = "Notes du 3 novembre : Aimed Shot gagne environ +110 % de dégâts bonus, Arcane Shot +30 % (coefficient de puissance d'attaque 0,15 au lieu de 0,1), Serpent Sting +20 % (5 % de puissance d'attaque par tick au lieu de 3 %), Barrage donne 5 / 10 / 15 % et Sniper Shot +100 % ; Aspect of the Hawk plafonne à 110 de puissance d'attaque à distance (rang 6). Les pièges partagent une recharge de 30 s (non simulée)."
hunter_en = "Notes of November 3: Aimed Shot gains about +110% bonus damage, Arcane Shot +30% (attack power coefficient 0.15 instead of 0.1), Serpent Sting +20% (5% attack power per tick instead of 3%), Barrage gives 5 / 10 / 15% and Sniper Shot +100%; Aspect of the Hawk tops out at 110 ranged attack power (rank 6). Traps share a 30 s cooldown (not simulated)."
NEW["hunter_marksmanship"] = ([hunter_fr], [hunter_en])
NEW["hunter_beastmastery"] = ([hunter_fr], [hunter_en])
NEW["shaman_elemental"] = (
    ["Notes du 3 novembre : Lava Burst est supprimé et remplacé par Call of Thunder (+5 % de critique pour Lightning Bolt et Chain Lightning), Lightning Bolt gagne environ +80 % de dégâts de base au rang maximal, Lightning Overload déclenche 10 / 20 / 30 % du temps (3 / 7 / 10 % avant). Chain Lightning passe à 2,5 s d'incantation, environ 145 % des dégâts de base d'un Lightning Bolt et environ 225 % de son coût en mana ; le simulateur ne le lance pas et ce choix n'a pas été re-mesuré avec ces valeurs. Les dégâts des chocs « reviennent aux valeurs de Classic Era » sans chiffre publié : non simulé."],
    ["Notes of November 3: Lava Burst is removed and replaced by Call of Thunder (+5% crit for Lightning Bolt and Chain Lightning), Lightning Bolt gains about +80% base damage at max rank, Lightning Overload triggers 10 / 20 / 30% of the time (3 / 7 / 10% before). Chain Lightning goes to a 2.5 s cast, about 145% of a Lightning Bolt's base damage and about 225% of its mana cost; the simulator does not cast it and that choice was not re-measured with these values. Shock damage \"reverts to Classic Era values\" with no published number: not simulated."],
)
NEW["shaman_enhancement"] = (
    ["Notes du 3 novembre : Stormstrike fait 150 % des dégâts d'arme normalisés (100 % avant) avec 6 s de recharge (8 s), Maelstrom Weapon se déclenche deux fois plus souvent, Flurry donne 6 % par rang (5 % avant), Mental Dexterity 50 / 100 / 150 % de l'Intelligence et Lightning Bolt gagne environ +80 % de dégâts de base."],
    ["Notes of November 3: Stormstrike deals 150% normalized weapon damage (100% before) with a 6 s cooldown (8 s), Maelstrom Weapon triggers twice as often, Flurry gives 6% per rank (5% before), Mental Dexterity 50 / 100 / 150% of Intellect and Lightning Bolt gains about +80% base damage."],
)
NEW["druid_balance"] = (
    ["Notes du 3 novembre : Genesis donne 2 / 4 / 6 / 8 / 10 % de dégâts périodiques (1 % par rang avant) et Naturalist 2 % de tous les dégâts par rang (1 % avant). Furor est passé dans l'arbre Féral : les 5 points de Restauration vont dans Nature's Focus."],
    ["Notes of November 3: Genesis gives 2 / 4 / 6 / 8 / 10% periodic damage (1% per rank before) and Naturalist 2% of all damage per rank (1% before). Furor moved to the Feral tree: the 5 Restoration points go into Nature's Focus."],
)
NEW["druid_feral"] = (
    ["Notes du 3 novembre : Shred passe à 200 % des dégâts d'arme (155 % avant) et Claw à 140 % (110 %) ; Rip, Rake et Ferocious Bite gagnent environ 25 % de dégâts de base et de puissance d'attaque (le simulateur applique 25 % : la formulation des notes est « environ »). Rend and Tear donne 3 % par rang (2 % avant), Berserk disparaît et Shifting Power demande désormais Predatory Discipline. Heart of the Wild est passé dans l'arbre Restauration."],
    ["Notes of November 3: Shred goes to 200% weapon damage (155% before) and Claw to 140% (110%); Rip, Rake and Ferocious Bite gain about 25% base damage and attack power scaling (the simulator applies 25%: the notes say \"about\"). Rend and Tear gives 3% per rank (2% before), Berserk is gone and Shifting Power now requires Predatory Discipline. Heart of the Wild moved to the Restoration tree."],
)
NEW["paladin_retribution"] = (
    ["Notes du 3 novembre : Champion of the Light donne 12 % de l'Intelligence en puissance des sorts par rang sur 5 rangs et raccourcit Hammer of Wrath de 0,2 s par rang, Conviction donne 2 % de critique par rang à tous les sorts et attaques, Two-Handed Weapon Specialization augmente aussi les dégâts sacrés, Improved Seals donne 3 % par rang sur 5 rangs, Vindication n'augmente plus la puissance d'attaque, Vengeance cumule 5 fois ; Instrument of Law et Twist of Light disparaissent. Unsealed Wrath (nouveau talent de palier 7) n'est pas simulé."],
    ["Notes of November 3: Champion of the Light gives 12% of the Intellect as spell power per rank over 5 ranks and shortens Hammer of Wrath by 0.2 s per rank, Conviction gives 2% crit per rank to all spells and attacks, Two-Handed Weapon Specialization also raises Holy damage, Improved Seals gives 3% per rank over 5 ranks, Vindication no longer raises attack power, Vengeance stacks 5 times; Instrument of Law and Twist of Light are gone. Unsealed Wrath (a new row-7 talent) is not simulated."],
)
NEW["warrior_protection"] = (
    ["Notes du 3 novembre : la posture défensive donne 80 % de menace en plus (30 % avant) et Defiance 7 / 13 / 20 % (5 / 10 / 15 %)."],
    ["Notes of November 3: Defensive Stance gives 80% extra threat (30% before) and Defiance 7 / 13 / 20% (5 / 10 / 15%)."],
)
NEW["paladin_protection"] = (
    ["Notes du 3 novembre : Righteous Fury donne +33 % de menace sur tout et +90 % de plus sur les dégâts sacrés (le simulateur les additionne), Improved Righteous Fury réduit les dégâts subis de 3 / 6 / 9 %, Iron Creed n'a plus que 3 rangs (+10 % de menace de Holy Strike par rang), One-Handed Weapon Specialization disparaît et Holy Shield inflige moins de dégâts."],
    ["Notes of November 3: Righteous Fury gives +33% threat on everything and +90% more on Holy damage (the simulator adds them), Improved Righteous Fury cuts damage taken by 3 / 6 / 9%, Iron Creed has only 3 ranks (+10% Holy Strike threat per rank), One-Handed Weapon Specialization is gone and Holy Shield deals less damage."],
)
NEW["druid_bear"] = (
    ["Notes du 3 novembre : le bonus de menace des formes d'ours passe à 115 % (50 % avant), pour remplacer la Bénédiction de salut supprimée. Berserk disparaît de l'arbre."],
    ["Notes of November 3: the bear forms' threat bonus goes to 115% (50% before), to replace the removed Blessing of Salvation. Berserk is gone from the tree."],
)

out = {}
for sid in OLD:
    spec = next(x for x in RANK["specs"] if x["spec"] == sid)
    entry = {}
    for lang in ("fr", "en"):
        strings = measured(spec, lang)
        if sid in KEEP and len(OLD[sid][lang]) > 2:
            strings += OLD[sid][lang][2:]
        if sid in NEW:
            strings += NEW[sid][0 if lang == "fr" else 1]
        entry[lang] = strings
    out[sid] = entry

lines = ["TALENT_NOTES = {"]
for sid, e in out.items():
    lines.append(f'    "{sid}": {{')
    for lang in ("fr", "en"):
        lines.append(f'        "{lang}": [' + ", ".join(json.dumps(s, ensure_ascii=False) for s in e[lang]) + "],")
    lines.append("    },")
lines.append("}")
text = SRC.read_text(encoding="utf-8")
m = re.search(r"^TALENT_NOTES = \{.*?^\}\n", text, re.S | re.M)
assert m, "TALENT_NOTES block not found"
SRC.write_text(text[:m.start()] + "\n".join(lines) + "\n" + text[m.end():], encoding="utf-8")
print("rewrote", len(out), "specs")
