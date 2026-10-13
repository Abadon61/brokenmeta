"""Texts of the 'Which race?' pages (see wow_racepick.py)."""


def finish(lang, cls, rp, guides):
    """Texts that depend on the numbers: method, FAQ, links."""
    tx = TX[lang]
    s = rp["meta"]
    rp["method"] = [m.format(fight=s["fight"], iters=s["iters"], build=s["build"]) for m in tx["method"]]
    faq = []
    for sp in rp["specs"]:
        if sp["tank"]:
            continue
        eq = [l["name"] for l in sp["lines"] if l["equiv"]]
        worst = sp["lines"][-1]
        gap = f"{abs(worst['delta']):.1f}".replace(".", ",") if lang == "fr" else f"{abs(worst['delta']):.1f}"
        if len(eq) == len(sp["lines"]):
            ans = tx["faq_equal"].format(spec=sp["name"], cls=cls["name"][lang])
        else:
            ans = tx["faq_best"].format(spec=sp["name"], cls=cls["name"][lang], best=", ".join(eq), worst=worst["name"], gap=gap)
        faq.append((tx["faq_q"].format(spec=sp["name"], cls=cls["name"][lang]), ans))
    faq.append((tx["faq_q2"], tx["faq_a2"]))
    rp["faq"] = faq
    rp["guides"] = guides
    return rp


TX = {
    "fr": {
        "title": "Meilleure race {cls} WoW Forever : racials et DPS", "desc": "Quelle race jouer pour un {cls} dans WoW: Forever : racials lus dans le client bêta et écart de DPS simulé entre les {n} races possibles.",
        "kicker": "QUELLE RACE CHOISIR", "h1": "Quelle race choisir pour un {cls} dans WoW: Forever ?",
        "intro": "Le {cls} peut être joué par {n} races. Pour chacune, voici ses capacités raciales telles que le client de la bêta les décrit et, pour les spécialisations simulées, l'écart de DPS que ces racials entraînent par rapport à la meilleure race.",
        "chips": ["{n} races possibles", "Racials : client bêta", "Simulateur niveau 60", "Mis à jour le {date}"],
        "verdict_h": "Quelle race fait le plus de dégâts ?", "verdict_p": "Pour chaque spécialisation simulée : l'écart de DPS avec la meilleure race. Seuls les racials lus dans le client comptent : les bonus de caractéristiques de base de chaque race ne sont pas publiés dans les tables et ne sont pas pris en compte (toutes les races partent des mêmes caractéristiques).",
        "col_race": "Race", "col_racials": "Écart de DPS (± erreur)", "best_tag": "Meilleure", "equiv_tag": "Équivalente", "tank_hint": "menace par seconde", "never_hint": "racial actif sans gain, non utilisé",
        "table_note": "« Équivalente » : l'écart avec la meilleure race est dans la marge d'erreur de la simulation. Seuls les racials qui modifient les dégâts sont simulés ; les autres (résistances, évasions, déplacement, métiers) sont listés plus bas.",
        "method_h": "Méthode et limites", "method": [
            "Pour chaque spécialisation, le même personnage (équipement, talents, consommables du classement niveau 60) est simulé avec chaque race possible : {fight} secondes contre un boss immobile de niveau 63, {iters} répétitions par race et par variante (en 5 lots pour l'erreur).",
            "Les racials viennent des tables du client bêta (build {build}) : Forever a refondu ceux de WoW Classic. Les spécialisations d'armes donnent maintenant de la chance de coup critique au lieu de la maîtrise d'arme, et plusieurs racials sont nouveaux (Lumière d'Élune, Vent porteur…).",
            "Simulés : critique des spécialisations d'armes (épée, hache, masse), Fureur sanguinaire et Berserker (bonus de dégâts temporaires), Lumière d'Élune, Endurance (+1 % toucher), Vent porteur (+1 % hâte), L'esprit humain, Esprit étendu (mana).",
            "Non simulés : Eureka ! des gnomes, Toucher de la tombe des morts-vivants, bonus contre les bêtes et les élémentaires (le combat simulé est contre un seul boss), et la santé en plus des taurens.",
            "Les bonus de caractéristiques de base de chaque race (force, agilité, etc.) ne figurent pas dans les tables lues : toutes les races partent des caractéristiques humaines, pour ne mesurer que l'effet des racials. Un racial à utiliser (Fureur sanguinaire, Lumière d'Élune, Berserker) est lancé au meilleur moment parmi quatre départs possibles (0,2 s, 20 s, 60 s, 120 s), comme un joueur l'alignerait avec ses autres cooldowns.",
        ],
        "races_h": "Les races du {cls} et leurs racials", "races_p": "Les descriptions viennent du client de la bêta. L'étiquette indique si la simulation en tient compte.",
        "tags": {"sim": "simulé", "dmg": "dégâts, non simulé", "util": "utilité, sans effet sur le DPS"}, "dur": "Durée", "cd": "Recharge",
        "fac": {"alliance": "Alliance", "horde": "Horde"},
        "faq_h": "Questions fréquentes", "faq_q": "Quelle est la meilleure race pour un {cls} {spec} dans WoW: Forever ?",
        "faq_best": "Dans notre simulation, {best} donne le plus de DPS au {cls} {spec} avec ses racials ; la race la moins bien placée, {worst}, est environ {gap} % derrière. Ces écarts sont petits : jouez plutôt la race que vous préférez si vous ne visez pas le dernier pourcent.",
        "faq_equal": "Dans notre simulation, aucune race ne se détache nettement pour le {cls} {spec} : les écarts sont dans la marge d'erreur.",
        "faq_q2": "Peut-on choisir n'importe quelle race ?", "faq_a2": "Non : les combinaisons race et classe viennent du client de la bêta. Les races Alliance et Horde ne se mélangent pas, et les skyborne ont leurs propres classes.",
        "links_h": "Pour aller plus loin", "l_tier": "Tier list niveau 60", "l_talents": "Talents du {cls}", "l_sim": "Simulateur DPS niveau 60", "l_hub": "Toutes les classes",
        "hub_title": "Quelle race choisir dans WoW Forever : toutes les classes", "hub_desc": "Quelle race jouer dans WoW: Forever : classes possibles, racials du client bêta et écart de DPS simulé pour chaque classe.",
        "hub_classes": "Choisissez votre classe", "hub_n": "{n} races possibles", "hub_note": "Pour chaque spécialisation simulée, les races à égalité en tête du classement de DPS (écart dans la marge d'erreur) sont listées. Les écarts sont petits : consultez la page de la classe pour le détail et les limites.", "hub_h1": "Quelle race choisir dans WoW: Forever ?", "hub_intro": "Choisissez votre classe pour voir ses races possibles, leurs capacités raciales et l'écart de DPS simulé.",
    },
    "en": {
        "title": "Best {cls} race in WoW Forever: racials and DPS", "desc": "Which race to play as a {cls} in WoW: Forever: racials read from the beta client and the simulated DPS gap between the {n} possible races.",
        "kicker": "WHICH RACE TO PICK", "h1": "Which race should a {cls} pick in WoW: Forever?",
        "intro": "The {cls} can be played by {n} races. For each one, here are its racial abilities as the beta client describes them and, for the simulated specs, the DPS gap these racials create against the best race.",
        "chips": ["{n} possible races", "Racials: beta client", "Level 60 simulator", "Updated {date}"],
        "verdict_h": "Which race deals the most damage?", "verdict_p": "For each simulated spec: the DPS gap against the best race. Only the racials read from the client count: each race's base stat bonuses are not published in the tables and are not accounted for (all races start from the same stats).",
        "col_race": "Race", "col_racials": "DPS gap (± error)", "best_tag": "Best", "equiv_tag": "Equivalent", "tank_hint": "threat per second", "never_hint": "active racial adds nothing, not used",
        "table_note": "\"Equivalent\": the gap with the best race is within the simulation's error margin. Only racials that change damage are simulated; the others (resistances, escapes, movement, professions) are listed below.",
        "method_h": "Method and limits", "method": [
            "For each spec, the same character (gear, talents, consumables from the level 60 ranking) is simulated with every possible race: {fight} seconds against a stationary level 63 boss, {iters} runs per race and per variant (in 5 batches for the error).",
            "Racials come from the beta client tables (build {build}): Forever reworked those of WoW Classic. Weapon specializations now give critical strike chance instead of weapon skill, and several racials are new (Elune's Light, Wind Blessed...).",
            "Simulated: weapon specialization crit (sword, axe, mace), Blood Fury and Berserking (temporary damage bonuses), Elune's Light, Endurance (+1% hit), Wind Blessed (+1% haste), The Human Spirit, Expansive Mind (mana).",
            "Not simulated: Gnome Eureka!, Undead Touch of the Grave, bonuses against Beasts and Elementals (the simulated fight is against a single boss), and the Tauren's extra health.",
            "Each race's base stat bonuses (strength, agility, etc.) are not in the tables read: all races start from the human stats, so that only the racials' effect is measured. A racial you press (Blood Fury, Elune's Light, Berserking) is used at the best moment among four possible starts (0.2 s, 20 s, 60 s, 120 s), as a player would line it up with their other cooldowns.",
        ],
        "races_h": "{cls} races and their racials", "races_p": "The descriptions come from the beta client. The label says whether the simulation accounts for them.",
        "tags": {"sim": "simulated", "dmg": "damage, not simulated", "util": "utility, no effect on DPS"}, "dur": "Duration", "cd": "Cooldown",
        "fac": {"alliance": "Alliance", "horde": "Horde"},
        "faq_h": "Frequently asked questions", "faq_q": "What is the best race for a {spec} {cls} in WoW: Forever?",
        "faq_best": "In our simulation, {best} deals the most DPS as a {spec} {cls} with its racials; the lowest-placed race, {worst}, is about {gap}% behind. These gaps are small: play the race you prefer unless you chase the last percent.",
        "faq_equal": "In our simulation no race stands out for the {spec} {cls}: the gaps are within the error margin.",
        "faq_q2": "Can I pick any race?", "faq_a2": "No: the race and class combinations come from the beta client. Alliance and Horde races do not mix, and the Skyborne have their own classes.",
        "links_h": "Go further", "l_tier": "Level 60 tier list", "l_talents": "{cls} talents", "l_sim": "Level 60 DPS simulator", "l_hub": "All classes",
        "hub_title": "Which race to pick in WoW Forever: all classes", "hub_desc": "Which race to play in WoW: Forever: possible classes, beta client racials and the simulated DPS gap for each class.",
        "hub_classes": "Pick your class", "hub_n": "{n} possible races", "hub_note": "For each simulated spec, the races tied at the top of the DPS ranking (gap within the error margin) are listed. The gaps are small: see the class page for the detail and the limits.", "hub_h1": "Which race should you pick in WoW: Forever?", "hub_intro": "Pick your class to see its possible races, their racial abilities and the simulated DPS gap.",
    },
}
