"""Hand-written parts of the League champion guides (/league/guide/<champion>/).

Everything here is EDITORIAL advice, not measured data: the guide pages label
it "Guide rédigé" and keep it visually separate from the measured sections
(win rates, builds, matchups). Each combo is written from the champion's
official spell descriptions (Data Dragon) and Riot's own ally/enemy tips, so
it only claims what those texts support; the `key` fields (Q/W/E/R/AA) drive
the ability-icon sequence shown on the page.

Schema per champion (French for now, English to follow once the layout is validated):
    "playstyle":  short paragraph -- how the champion wins games
    "laning":     short paragraph -- early game plan
    "combos":     [{"name", "keys": ["E", "Q", "W"], "when", "how"}]
    "mistakes":   [str] -- common errors to avoid
"""

EDITORIAL = {
    "Ahri": {
        "fr": {
            "playstyle": (
                "Ahri est une mage mobile qui gagne ses parties en attrapant un adversaire isolé avec Charme puis en le brûlant "
                "avant qu'il ne réagisse. Son Orbe d'illusion inflige des dégâts magiques à l'aller et des dégâts bruts au retour, "
                "ce qui la rend efficace même contre des cibles qui empilent de la résistance magique. Son ultime lui donne trois "
                "déplacements et se réactive quand elle participe à une élimination : elle est à son meilleur quand elle enchaîne les kills "
                "et à son pire quand elle se trompe d'engagement, car sans ultime ses capacités de survie sont très réduites."
            ),
            "laning": (
                "Au début de partie, harcèle avec l'Orbe d'illusion à sa portée maximale et ne dépense Lucioles que pour finir ou pour te dégager. "
                "Le coût en mana de l'Orbe augmente à chaque niveau : surveille ta barre de mana avant de trader. Ton passif te soigne "
                "après 9 sbires tués, donc farmer proprement compense une partie du harcèlement adverse."
            ),
            "combos": [
                {
                    "name": "Le combo de base (pick)",
                    "keys": ["E", "Q", "W"],
                    "when": "Un ennemi est à portée de Charme et aucun sbire ne bloque la trajectoire.",
                    "how": (
                        "Lance Charme en premier : il interrompt les compétences de déplacement de la cible et la fait marcher vers toi, "
                        "ce qui t'assure de toucher le reste. Enchaîne avec l'Orbe d'illusion, puis Lucioles, qui verrouillent et attaquent "
                        "les ennemis proches pendant que tu te repositionnes."
                    ),
                },
                {
                    "name": "L'engagement avec l'ultime",
                    "keys": ["R", "E", "Q", "W"],
                    "when": "La cible est trop loin pour un Charme direct ou tu veux fermer la distance d'un coup.",
                    "how": (
                        "Assaut spirituel ouvre la voie : il te rapproche, permet d'activer Charme, aide à toucher deux fois avec l'Orbe d'illusion "
                        "et te met à portée de Lucioles. Garde une réactivation en réserve, car l'ultime peut être lancé jusqu'à trois fois."
                    ),
                },
                {
                    "name": "Le nettoyage de combat d'équipe",
                    "keys": ["E", "R", "R", "R"],
                    "when": "Le combat tourne à ton avantage et tu poursuis les derniers ennemis.",
                    "how": (
                        "Charme sur le premier fuyard, puis enchaîne les réactivations d'Assaut spirituel : Ahri en gagne en participant à "
                        "l'élimination de champions ennemis. Garde la dernière pour repartir vers ton équipe si le combat se retourne."
                    ),
                },
            ],
            "mistakes": [
                "Lancer Charme sans regarder les sbires : le premier ennemi touché l'est, et c'est rarement le bon.",
                "Utiliser l'ultime en entrée de combat sans savoir si tu pourras le réactiver : sans lui, tu n'as presque plus de survie.",
                "Oublier que l'Orbe d'illusion frappe aussi au retour : place-toi pour que la cible soit sur son trajet des deux côtés.",
            ],
        },
    },
    "Jinx": {
        "fr": {
            "playstyle": (
                "Jinx est une tireuse qui devient dominante dès qu'elle est bien protégée. Son passif lui donne un énorme bonus de vitesse "
                "de déplacement et d'attaque à chaque élimination, ce qui lui permet d'enchaîner les kills dans un combat déjà bien engagé. "
                "Elle alterne entre le minigun, qui monte en vitesse d'attaque, et le lance-roquettes, qui frappe en zone à plus longue portée "
                "mais consomme du mana. Sa faiblesse est son manque de défense : si ses grenades ratent leur cible, elle est vulnérable."
            ),
            "laning": (
                "Utilise les roquettes sur les sbires pour toucher les champions adverses proches sans attirer leur attention, et passe au minigun "
                "dès qu'un ennemi s'approche trop. Garde tes grenades pour te défendre : leur long délai de récupération en fait ta principale "
                "protection. Zap ! ralentit et révèle la cible à très longue portée, idéal pour préparer un échange."
            ),
            "combos": [
                {
                    "name": "Le combat d'équipe en périphérie",
                    "keys": ["W", "AA", "AA"],
                    "when": "Un combat éclate et tu es protégée par ton équipe.",
                    "how": (
                        "Reste en marge du combat, utilise Zap ! puis tes roquettes, et ne sors le minigun que quand c'est sans danger. "
                        "Chaque élimination déclenche ton passif : la vitesse gagnée te permet d'enchaîner sur la cible suivante."
                    ),
                },
                {
                    "name": "La défense contre un plongeur",
                    "keys": ["E", "W", "Q", "AA"],
                    "when": "Un ennemi se jette sur toi.",
                    "how": (
                        "Place Pyromâcheurs sur sa trajectoire : ils l'immobilisent quand il marche dessus. Ralentis-le avec Zap !, "
                        "puis repasse au minigun avec Flip flap ! pour le finir à courte portée."
                    ),
                },
                {
                    "name": "L'ultime pour finir une cible",
                    "keys": ["R"],
                    "when": "Un ennemi affaibli fuit ou se trouve loin de toi.",
                    "how": (
                        "La super roquette traverse la carte et ses dégâts augmentent pendant le trajet, en fonction des PV manquants de la cible : "
                        "plus tu es loin de la cible, plus l'ultime frappe fort. Tire-la de loin pour sécuriser un kill ou une poursuite."
                    ),
                },
            ],
            "mistakes": [
                "Tirer les roquettes en boucle quand un ennemi est à côté de toi : le minigun met du temps à monter en vitesse d'attaque.",
                "Gaspiller les grenades en début de combat : sans elles, tu n'as aucune défense.",
                "Utiliser l'ultime de près : plus la cible est proche, moins il inflige de dégâts.",
            ],
        },
    },
    "Darius": {
        "fr": {
            "playstyle": (
                "Darius est un combattant qui devient plus fort plus le combat dure. Ses attaques et ses compétences font saigner (Plaie béante, "
                "jusqu'à 5 cumuls) ; à cinq cumuls, il enrage et gagne un énorme bonus en dégâts d'attaque. Sa Décimation le soigne en fonction "
                "des champions touchés par la lame, et Crampon attire les ennemis à lui. Sa capacité à fuir est limitée : il cherche donc "
                "le combat prolongé au corps à corps, pas la poursuite."
            ),
            "laning": (
                "Frappe avec la lame de Décimation, sur le bord extérieur de la hache, pour profiter au maximum des dégâts et du soin, en restant "
                "à la limite de ta portée. Empile Plaie béante avec tes attaques entre les compétences. Pendant le délai de récupération de Crampon, "
                "tu es vulnérable au harcèlement : évite de t'exposer quand il n'est pas disponible."
            ),
            "combos": [
                {
                    "name": "L'échange en lane",
                    "keys": ["Q", "AA", "W", "AA"],
                    "when": "Tu veux trader sans engager complètement.",
                    "how": (
                        "Décimation à la limite de la portée pour que la lame touche, une attaque pour empiler Plaie béante, puis Estropiaison "
                        "sur la prochaine attaque : le saignement ralentit la cible et l'empêche de partir."
                    ),
                },
                {
                    "name": "L'engagement complet (kill)",
                    "keys": ["E", "W", "AA", "Q", "AA", "R"],
                    "when": "Un ennemi est à portée de Crampon et tu veux le tuer.",
                    "how": (
                        "Crampon l'attire à toi, Estropiaison le ralentit, tes attaques et Décimation empilent Plaie béante (jusqu'à 5 cumuls) "
                        "et te soignent. Termine avec Guillotine noxienne : ses dégâts bruts augmentent avec le nombre de cumuls sur la cible, "
                        "donc ne la lance pas trop tôt."
                    ),
                },
                {
                    "name": "L'enchaînement de combat d'équipe",
                    "keys": ["R", "R"],
                    "when": "Un ennemi affaibli est à portée de Guillotine dans un combat d'équipe.",
                    "how": (
                        "Si Guillotine noxienne tue sa cible, son délai de récupération est annulé pendant un court moment : "
                        "relance-la aussitôt sur le prochain ennemi affaibli. Garde une cible à cumuls pour la deuxième."
                    ),
                },
            ],
            "mistakes": [
                "Lancer Guillotine noxienne sans cumuls de Plaie béante : ses dégâts en dépendent.",
                "S'engager sans Crampon quand l'adversaire peut te harceler : tu es fragile pendant son délai de récupération.",
                "Chercher à poursuivre : ta capacité à fuir ou à rattraper est limitée, force plutôt le combat proche.",
            ],
        },
    },
}


# Batches of hand-written guides (site_build/lol_guides_batches/batch_NN.py, each defining BATCH = {...}).
def _load_batches() -> None:
    import importlib.util
    from pathlib import Path
    for path in sorted((Path(__file__).parent / "lol_guides_batches").glob("batch_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        EDITORIAL.update(mod.BATCH)
    for path in sorted((Path(__file__).parent / "lol_guides_batches").glob("extra_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for champ, extra in mod.EXTRA.items():
            fr = EDITORIAL[champ]["fr"]
            fr["combos"] = fr["combos"] + extra.get("combos", [])
            for key in ("teamfight", "strengths", "weaknesses"):
                if key in extra:
                    fr[key] = extra[key]
    # English versions (en_*.py define EN = {champion_id: {...same schema as "fr"...}}, incl. any strengths/weaknesses/teamfight)
    for path in sorted((Path(__file__).parent / "lol_guides_batches").glob("en_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for champ, entry in mod.EN.items():
            fr_combos = EDITORIAL[champ]["fr"]["combos"]
            assert len(entry["combos"]) == len(fr_combos), f"{champ}: EN has {len(entry['combos'])} combos, FR has {len(fr_combos)}"
            for cb, fr_cb in zip(entry["combos"], fr_combos):
                cb.setdefault("keys", fr_cb["keys"])
            EDITORIAL[champ]["en"] = entry


_load_batches()
