"""Dungeon pages and the 'Dungeons by level' hub (2026-10-13): what is added on top of the loot / boss / quest guide of wow_dungeon.html.
  - SCARLET_WINGS: the four wings of the Scarlet Monastery (WoW Classic layout, flagged on the page: Forever has not confirmed it)
  - thin loot note: dungeons whose drop list is still partial in the beta data (the beta is capped at level 30) say that it will be completed at launch
  - level 40 armor: dungeons that straddle level 40 show the plate / mail picks of warriors, paladins, hunters and shamans from level 40
  - hub texts and the level finder's data (js/wow-dungeon-finder.js)"""

# slug -> [(wing id, {lang: name}, [boss names, English])]; the order of the bosses inside a wing is the game's (data/wow_dungeons/art.json)
WINGS = {
    "scarlet-monastery": [
        ("graveyard", {"en": "Graveyard", "fr": "Cimetière"}, ["Interrogator Vishas", "Bloodmage Thalnos", "Ironspine", "Azshir the Sleepless", "Fallen Champion"]),
        ("library", {"en": "Library", "fr": "Bibliothèque"}, ["Houndmaster Loksey", "Arcanist Doan"]),
        ("armory", {"en": "Armory", "fr": "Armurerie"}, ["Herod"]),
        ("cathedral", {"en": "Cathedral", "fr": "Cathédrale"}, ["Scarlet Commander Mograine", "High Inquisitor Fairbanks", "High Inquisitor Whitemane"]),
    ],
}
THIN_DROPS = 10          # fewer boss / creature drops than this: the loot list is flagged as partial
HEAVY_ARMOR_CLASSES = ("warrior", "paladin", "hunter", "shaman")     # plate (warrior, paladin) and mail (hunter, shaman) from level 40


def wing_of(slug, boss_en):
    for i, (_, _, bosses) in enumerate(WINGS.get(slug, [])):
        if boss_en in bosses:
            return i
    return None


def group_by_wing(slug, bosses, lang):
    """bosses: [{'name', 'en', 'items'}] in game order. Adds 'wing' (the wing's name on its first boss) and orders the bosses wing by wing; unknown bosses go last."""
    wings = WINGS.get(slug)
    if not wings:
        return bosses, False
    order = sorted(range(len(bosses)), key=lambda i: (wing_of(slug, bosses[i]["en"]) if wing_of(slug, bosses[i]["en"]) is not None else 99, i))
    out, last = [], object()
    for i in order:
        w = wing_of(slug, bosses[i]["en"])
        name = wings[w][1][lang] if w is not None else None
        out.append(dict(bosses[i], wing=name if name != last else None, wing_id=w))
        last = name
    return out, True


TX = {
    "fr": {
        "thin": "Le butin de {name} est encore partiel dans les données de la bêta, limitée au niveau 30 : la liste sera complétée au lancement, quand les données de Forever seront disponibles. Les boss et les quêtes affichés viennent du client de la bêta.",
        "thin_faq_q": "Le butin de {name} est-il complet ?", "thin_faq_a": "Pas encore : {n} objets lâchés par les boss et les créatures sont connus dans les données de la bêta, limitée au niveau 30. Nous complétons la liste au lancement.",
        "desc_nodrop": "Guide de {name}{abbr} dans WoW: Forever : les boss dans l'ordre, les quêtes et leurs récompenses ; le butin sera complété au lancement.",
        "thin_short": "Butin partiel", "wings_note": "Les ailes sont celles de WoW Classic : Forever ne les a pas confirmées.", "wings_meta": "PAR AILE",
        "from40": "À partir du niveau 40 :", "bands_h": "Quel donjon à quel niveau",
        "hub_title": "Donjons WoW Forever par niveau : lequel faire ?", "hub_desc": "Quel donjon faire dans WoW: Forever selon votre niveau : de 15 à 60, avec le meilleur objet à y chercher pour votre spécialisation.",
        "hub_h1": "Donjons de WoW: Forever par niveau : lequel faire ?",
        "hub_intro": "Indiquez votre niveau et votre spécialisation : la page vous dit quels donjons faire maintenant, et quel est le meilleur objet à y chercher pour vous. Les niveaux viennent des données de la bêta ; le meilleur objet vient de notre simulateur.",
        "f_h": "Je suis niveau…", "f_level": "Niveau", "f_spec": "Spécialisation", "f_any": "— toutes —", "f_now": "À faire maintenant", "f_soon": "Bientôt (dans les 5 niveaux)", "f_none": "Aucun donjon à ce niveau dans nos données.",
        "f_best": "Meilleur objet", "f_nobest": "pas d'objet conseillé", "f_where": "Où", "f_see": "Voir le donjon",
        "bands_p": "Les donjons classés par tranche de niveau (premier niveau de la plage).", "band": "Niveaux {lo} à {hi}",
        "note": "Le meilleur objet est calculé par notre simulateur avec les statistiques réelles de Forever (donnée de la bêta). Pour le Temple englouti, Dire Maul, Uldaman et Razorfen Downs, le butin est encore partiel : il sera complété au lancement.",
    },
    "en": {
        "thin": "{name}'s loot is still partial in the beta data, which is capped at level 30: the list will be completed at launch, when Forever's data is available. The bosses and quests shown come from the beta client.",
        "thin_faq_q": "Is the loot of {name} complete?", "thin_faq_a": "Not yet: {n} items dropped by bosses and creatures are known in the beta data, capped at level 30. We complete the list at launch.",
        "desc_nodrop": "{name}{abbr} guide for WoW: Forever: the bosses in order, the quests and their rewards; the loot will be completed at launch.",
        "thin_short": "Partial loot", "wings_note": "The wings are WoW Classic's: Forever has not confirmed them.", "wings_meta": "BY WING",
        "from40": "From level 40:", "bands_h": "Which dungeon at which level",
        "hub_title": "WoW Forever dungeons by level: which one to run?", "hub_desc": "Which dungeon to run in WoW: Forever at your level: from 15 to 60, with the best item to look for there for your spec.",
        "hub_h1": "WoW: Forever dungeons by level: which one to run?",
        "hub_intro": "Enter your level and your spec: the page tells you which dungeons to run now and the best item to look for in each. Levels come from the beta data; the best item comes from our simulator.",
        "f_h": "I am level…", "f_level": "Level", "f_spec": "Spec", "f_any": "— all —", "f_now": "Run now", "f_soon": "Soon (within 5 levels)", "f_none": "No dungeon at this level in our data.",
        "f_best": "Best item", "f_nobest": "no recommended item", "f_where": "Where", "f_see": "See the dungeon",
        "bands_p": "Dungeons listed by level band (the first level of their range).", "band": "Levels {lo} to {hi}",
        "note": "The best item is computed by our simulator with Forever's real stats (beta data). For Sunken Temple, Dire Maul, Uldaman and Razorfen Downs the loot is still partial: it will be completed at launch.",
    },
}

# After the launch (wow_content.launched()) nothing on the dungeon pages talks about the beta. The data is still the one of the client until the
# post-launch collection, so the texts say "being completed" rather than "complete": no claim the data cannot back.
_AFTER_LAUNCH = {
    "fr": {
        "thin": "Le butin de {name} est encore partiel dans nos données : la liste est en cours de complétion avec les données du jeu sorti. Les boss et les quêtes affichés viennent du client de Forever.",
        "thin_faq_a": "Pas encore : {n} objets lâchés par les boss et les créatures sont connus à ce jour. Nous complétons la liste avec les données du jeu sorti.",
        "desc_nodrop": "Guide de {name}{abbr} dans WoW: Forever : les boss dans l'ordre, les quêtes et leurs récompenses ; le butin est en cours de complétion.",
        "hub_intro": "Indiquez votre niveau et votre spécialisation : la page vous dit quels donjons faire maintenant, et quel est le meilleur objet à y chercher pour vous. Les niveaux viennent des données du client de Forever ; le meilleur objet vient de notre simulateur.",
        "note": "Le meilleur objet est calculé par notre simulateur avec les statistiques réelles de Forever. Pour le Temple englouti, Dire Maul, Uldaman et Razorfen Downs, le butin est encore partiel : il est en cours de complétion.",
    },
    "en": {
        "thin": "{name}'s loot is still partial in our data: the list is being completed with the data of the released game. The bosses and quests shown come from Forever's client.",
        "thin_faq_a": "Not yet: {n} items dropped by bosses and creatures are known so far. We are completing the list with the data of the released game.",
        "desc_nodrop": "{name}{abbr} guide for WoW: Forever: the bosses in order, the quests and their rewards; the loot is being completed.",
        "hub_intro": "Enter your level and your spec: the page tells you which dungeons to run now and the best item to look for in each. Levels come from Forever's client data; the best item comes from our simulator.",
        "note": "The best item is computed by our simulator with Forever's real stats. For Sunken Temple, Dire Maul, Uldaman and Razorfen Downs the loot is still partial: it is being completed.",
    },
}
import wow_content as _wc  # noqa: E402
if _wc.launched():
    for _l, _tx in _AFTER_LAUNCH.items():
        TX[_l].update(_tx)

BANDS = [(10, 20), (20, 30), (30, 40), (40, 50), (50, 60)]


def band_of(lo):
    for i, (a, b) in enumerate(BANDS):
        if a <= lo < b:
            return i
    return 0 if lo < BANDS[0][0] else len(BANDS) - 1
