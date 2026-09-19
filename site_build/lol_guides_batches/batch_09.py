"""Guides rédigés, lot 9. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Anivia": {"fr": {
        "playstyle": (
            "Anivia est une mage de contrôle de zone : Lance de glace gèle et blesse sur son passage puis étourdit en explosant, Cristallisation crée un mur de glace impénétrable, et Tempête glaciale blesse et ralentit sur une zone. "
            "Sa passive la fait renaître en œuf avec tous ses PV quand elle subit des dégâts mortels."
        ),
        "laning": (
            "Gelure inflige le double de dégâts si la cible a été touchée récemment par Lance de glace ou une Tempête glaciale à taille maximale. "
            "Utilise Cristallisation pour bloquer le passage ou protéger un allié."
        ),
        "combos": [
            {"name": "Le combo de base", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée de Lance de glace.",
             "how": "Lance de glace gèle et blesse tout sur son passage, puis explose en étourdissant à proximité ; Gelure inflige le double de dégâts sur une cible récemment touchée."},
            {"name": "Le contrôle de zone", "keys": ["W", "R", "E"], "when": "Les ennemis avancent vers ton équipe.",
             "how": "Cristallisation bloque le passage un court moment avant de fondre ; place Tempête glaciale pour blesser et ralentir ceux qui attendent."},
            {"name": "La deuxième vie", "keys": ["R"], "when": "Tu es à bas PV.",
             "how": "Renaissance te transforme en œuf et te ramène à la vie avec tous tes PV : le combat n'est pas fini."},
        ],
        "mistakes": [
            "Lancer Gelure sans avoir touché avant : tu perds le double dégât.",
            "Placer Cristallisation trop tard : sa durée est courte.",
            "Laisser ton œuf sans protection : il peut être détruit.",
        ],
    }},
    "MissFortune": {"fr": {
        "playstyle": (
            "Miss Fortune est une tireuse de zone : sa passive inflige des dégâts supplémentaires quand elle attaque une nouvelle cible, Doublé touche deux ennemis alignés, Pluie de balles ralentit et blesse en vagues, et Barrage de plomb déchaîne un déluge dans un cône. "
            "Chaque vague de l'ultime peut infliger des coups critiques."
        ),
        "laning": (
            "Change de cible pour déclencher Cœur volage à chaque fois. "
            "Doublé blesse la cible puis celle derrière : utilise un sbire pour toucher un champion derrière."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "AA", "E"], "when": "Un ennemi est derrière un sbire.",
             "how": "Doublé tire sur le sbire pour atteindre le champion derrière, les deux coups peuvent appliquer Cœur volage ; Pluie de balles ralentit."},
            {"name": "Le combat d'équipe", "keys": ["E", "R"], "when": "Les ennemis sont regroupés dans ton axe.",
             "how": "Pluie de balles ralentit et blesse par vagues, Barrage de plomb inflige d'importants dégâts dans un cône : place-toi pour que le cône couvre plusieurs ennemis."},
            {"name": "La mobilité", "keys": ["W", "AA", "AA"], "when": "Tu veux frapper vite ou fuir.",
             "how": "Fanfaronne augmente passivement ta vitesse hors attaque et donne de la vitesse d'attaque à l'activation ; Cœur volage réduit son délai."},
        ],
        "mistakes": [
            "Lancer l'ultime sans protection : elle canalise.",
            "Attaquer toujours la même cible : tu perds Cœur volage.",
            "Oublier que Doublé traverse : place-toi pour toucher les deux.",
        ],
    }},
    "Braum": {"fr": {
        "playstyle": (
            "Braum est un support-tank dont les attaques appliquent Coups étourdissants : les attaques de ses alliés les appliquent aussi, et à 4 effets la cible est étourdie et subit des dégâts magiques. "
            "Incassable lève son bouclier pour intercepter les projectiles, Bouclier humain le fait bondir vers un allié, et son ultime projette en l'air puis ralentit sur une ligne."
        ),
        "laning": (
            "Applique Coups étourdissants avec Morsure de l'hiver et tes attaques : tes alliés déclenchent aussi l'effet, coordonne-toi avec ton carry. "
            "Oriente Incassable vers les projectiles ennemis."
        ),
        "combos": [
            {"name": "L'étourdissement", "keys": ["Q", "AA", "AA", "AA"], "when": "Ton carry attaque la même cible.",
             "how": "Morsure de l'hiver applique un effet, chaque attaque de Braum ou d'un allié en ajoute ; à 4 effets, la cible est étourdie et subit des dégâts magiques."},
            {"name": "La protection", "keys": ["W", "E"], "when": "Ton carry est menacé par des projectiles.",
             "how": "Bouclier humain te fait bondir vers lui pour donner armure et résistance magique à vous deux ; Incassable intercepte les projectiles et bloque totalement la première attaque."},
            {"name": "L'ultime d'engagement", "keys": ["R", "Q", "AA"], "when": "Les ennemis se regroupent.",
             "how": "Fissure glaciale projette en l'air les ennemis proches et sur la ligne, puis la fissure les ralentit."},
        ],
        "mistakes": [
            "Oublier que tes alliés déclenchent aussi Coups étourdissants.",
            "Mal orienter Incassable : il ne protège que dans la direction choisie.",
            "Utiliser l'ultime sans coordonner ton équipe.",
        ],
    }},
    "Varus": {"fr": {
        "playstyle": (
            "Varus est un tireur-mage à distance : sa passive lui donne des dégâts d'attaque et de la puissance après un kill ou une assistance, davantage sur un champion. "
            "Flèche perforante se charge pour plus de dégâts et de portée, Carquois meurtri applique Meurtrissure (dégâts selon les PV max), Pluie de flèches souille le sol, et Chaîne corruptrice immobilise et se propage."
        ),
        "laning": (
            "Tes attaques appliquent Meurtrissure : les autres compétences la déclenchent et infligent des dégâts selon les PV max de la cible. "
            "Charge ta Flèche perforante pour plus de portée et de dégâts."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["W", "AA", "AA", "Q"], "when": "Un ennemi est à portée.",
             "how": "Carquois meurtri renforce ta prochaine Flèche perforante et tes attaques appliquent Meurtrissure ; les compétences déclenchent Meurtrissure pour des dégâts selon les PV max."},
            {"name": "La zone empoisonnée", "keys": ["E", "Q", "AA"], "when": "Les ennemis sont près d'un passage.",
             "how": "Pluie de flèches inflige des dégâts physiques et souille le sol : vitesse de déplacement, soins et régénération réduits."},
            {"name": "L'engagement d'équipe", "keys": ["R", "E", "Q", "W"], "when": "Un carry ennemi est visible.",
             "how": "Chaîne corruptrice blesse et immobilise le premier champion touché et se propage aux champions non infectés proches en les immobilisant."},
        ],
        "mistakes": [
            "Lâcher la Flèche perforante sans charge : dégâts et portée augmentent avec la charge.",
            "Ne pas utiliser Meurtrissure : elle fait une part importante de tes dégâts.",
            "Lancer l'ultime sans que ses cibles proches soient prises.",
        ],
    }},
    "Diana": {"fr": {
        "playstyle": (
            "Diana est une combattante-assassine dont la passive frappe en zone tous les trois coups et augmente sa vitesse d'attaque pendant 5 secondes après chaque compétence. "
            "Croissant lunaire révèle avec Clair de lune, Rush lunaire n'a pas de délai sur un ennemi affecté, et Attraction lunaire attire tous les ennemis proches."
        ),
        "laning": (
            "Touche avec Croissant lunaire : Clair de lune permet à Rush lunaire de se réinitialiser. "
            "Corps célestes te donne un bouclier ; renforcé si les trois sphères explosent."
        ),
        "combos": [
            {"name": "Le combo de base", "keys": ["Q", "E", "W", "AA"], "when": "Un ennemi est à portée de Croissant.",
             "how": "Croissant lunaire inflige Clair de lune, Rush lunaire te rue sans délai sur la cible affectée, Corps célestes donne dégâts et bouclier, tes attaques profitent de la vitesse d'attaque."},
            {"name": "L'engagement d'équipe", "keys": ["R", "W", "Q", "E"], "when": "Plusieurs ennemis sont groupés.",
             "how": "Attraction lunaire révèle et attire les ennemis proches puis les ralentit ; si tu attires un champion, la lumière de la lune s'abat sur toi avec des dégâts augmentés par cible secondaire."},
            {"name": "La poursuite", "keys": ["E", "Q", "E"], "when": "Tu poursuis des ennemis marqués.",
             "how": "Rush lunaire n'a pas de délai sur un ennemi affecté par Clair de lune ; tous les autres ennemis perdent l'effet, même s'ils ne sont pas ciblés."},
        ],
        "mistakes": [
            "Lancer Rush lunaire sur une cible sans Clair de lune.",
            "Utiliser l'ultime sans champion à attirer.",
            "Oublier que Rush lunaire retire Clair de lune aux autres ennemis.",
        ],
    }},
    "Swain": {"fr": {
        "playstyle": (
            "Swain est un mage qui grandit : les corbeaux collectent des fragments d'âme qui lui rendent des PV et augmentent définitivement ses PV max. "
            "Poigne mortifère inflige plus de dégâts avec le nombre de projectiles, Œil de l'empire ralentit et révèle, Capture immobilise et attire, et Incarnation démoniaque draine les PV des ennemis proches."
        ),
        "laning": (
            "Œil de l'empire blesse, ralentit et donne un fragment d'âme s'il touche un champion. "
            "Poigne mortifère traverse les ennemis : plus de projectiles touchent, plus les dégâts augmentent."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["W", "Q", "AA"], "when": "Un ennemi est à portée.",
             "how": "Œil de l'empire blesse, ralentit et révèle les champions touchés (fragment d'âme à la clé), Poigne mortifère inflige des dégâts croissants."},
            {"name": "La capture", "keys": ["E", "E", "Q"], "when": "Un ennemi est isolé.",
             "how": "Capture tire une vague qui revient et immobilise les ennemis touchés ; réactive-la pour attirer vers toi tous les champions immobilisés."},
            {"name": "La forme démoniaque", "keys": ["R", "E", "Q", "R"], "when": "Un combat d'équipe s'engage.",
             "how": "Incarnation démoniaque te transforme et draine les PV des ennemis proches ; Éruption démoniaque décime et ralentit, et la forme dure tant que tu draines des champions ennemis."},
        ],
        "mistakes": [
            "Utiliser Capture sans savoir qui attirer.",
            "Lancer l'ultime hors du combat : il draine les ennemis proches.",
            "Négliger les fragments d'âme : ils augmentent tes PV max.",
        ],
    }},
    "Cassiopeia": {"fr": {
        "playstyle": (
            "Cassiopeia est une mage qui profite de la vitesse de déplacement, plus efficace sur elle. "
            "Bombe nocive blesse, augmente sa vitesse et empoisonne, Miasmes ralentit et rend inertes les ennemis qui les traversent, Morsure fatale inflige plus de dégâts aux cibles empoisonnées et la soigne, et Regard de la Méduse étourdit ceux qui lui font face."
        ),
        "laning": (
            "Empoisonne avec Bombe nocive puis Morsure fatale : elle inflige plus de dégâts et te soigne. "
            "Si Morsure fatale tue sa cible, tu regagnes du mana."
        ),
        "combos": [
            {"name": "Le combo poison", "keys": ["Q", "E", "E", "W"], "when": "Un ennemi est à portée.",
             "how": "Bombe nocive empoisonne après un court délai et t'accélère si elle touche un champion, puis Morsure fatale inflige plus de dégâts aux cibles empoisonnées."},
            {"name": "L'ultime face", "keys": ["W", "R", "E"], "when": "Plusieurs ennemis te font face.",
             "how": "Regard de la Méduse étourdit ceux qui te font face et ralentit ceux qui te tournent le dos : place-toi pour qu'ils regardent vers toi."},
            {"name": "L'anti-mobilité", "keys": ["W", "Q"], "when": "Un ennemi utilise des compétences de déplacement.",
             "how": "Miasmes rend inertes ceux qui traversent les nuages : ils ne peuvent pas utiliser de compétence de déplacement."},
        ],
        "mistakes": [
            "Lancer l'ultime dos aux ennemis : ils ne sont que ralentis.",
            "Utiliser Morsure fatale sans poison.",
            "Poser Miasmes sans l'usage de leur effet d'inertie.",
        ],
    }},
    "Sivir": {"fr": {
        "playstyle": (
            "Sivir est une tireuse de rebond et de tempo : Lame boomerang blesse à l'aller et au retour, Ricochet fait rebondir ses attaques avec de la vitesse d'attaque, Bouclier magique bloque une compétence ennemie et son ultime accélère ses alliés. "
            "Ses attaques réduisent ensuite ses délais de récupération."
        ),
        "laning": (
            "Lame boomerang touche à l'aller comme au retour : place-toi pour que les deux passages comptent. "
            "Bouclier magique bloque une compétence ennemie et te soigne si elle est bloquée."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "AA"], "when": "Plusieurs cibles sont proches.",
             "how": "Lame boomerang inflige des dégâts à l'aller et au retour, Ricochet donne de la vitesse d'attaque et fait rebondir tes attaques (dégâts réduits sur les rebonds)."},
            {"name": "La protection", "keys": ["E", "AA"], "when": "Un ennemi va lancer une compétence décisive.",
             "how": "Bouclier magique bloque une compétence ennemie, te soigne et te donne un bref bonus de vitesse si elle est bloquée."},
            {"name": "L'ultime d'équipe", "keys": ["R", "W", "AA"], "when": "Ton équipe s'engage ou poursuit.",
             "how": "En chasse augmente temporairement la vitesse de tes alliés et tes attaques réduisent les délais de tes compétences."},
        ],
        "mistakes": [
            "Utiliser Bouclier magique trop tôt : il faut le garder pour la bonne compétence.",
            "Lancer Lame boomerang sans regarder son retour.",
            "Attaquer en rebond sur des sbires alors que tu peux toucher un champion.",
        ],
    }},
    "Fiora": {"fr": {
        "playstyle": (
            "Fiora est une duelliste qui révèle les points faibles de ses adversaires : les frapper la soigne et lui donne de la vitesse. "
            "Fente la propulse, Riposte pare tous les dégâts et entraves qui la ciblent avant de contre-attaquer, Botte secrète augmente sa vitesse d'attaque avec un critique, et Défi suprême révèle les quatre points faibles."
        ),
        "laning": (
            "Frappe le point faible révélé pour te soigner et gagner de la vitesse. "
            "Garde Riposte pour parer une compétence décisive : elle bloque tous les dégâts et entraves."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "E", "AA", "AA"], "when": "Un ennemi est à portée de Fente.",
             "how": "Fente te propulse sur le point faible, Botte secrète donne vitesse d'attaque avec ralentissement puis coup critique."},
            {"name": "La parade", "keys": ["W", "Q", "E"], "when": "Un ennemi lance une compétence décisive.",
             "how": "Riposte pare tous les dégâts et toutes les entraves qui te ciblent, puis donne un coup d'estoc qui ralentit ; étourdit si tu as paré un effet immobilisant."},
            {"name": "Le duel", "keys": ["R", "Q", "E", "AA"], "when": "Tu affrontes un seul champion.",
             "how": "Défi suprême révèle les quatre points faibles et t'accélère à proximité ; si tu frappes les quatre ou que l'adversaire meurt après que tu en as frappé un, toi et tes alliés dans la zone êtes soignés."},
        ],
        "mistakes": [
            "Utiliser Riposte sans savoir quelle compétence parer.",
            "Ignorer le point faible : c'est ta source de soin.",
            "Lancer Défi suprême sur un ennemi accompagné de nombreux alliés.",
        ],
    }},
    "MasterYi": {"fr": {
        "playstyle": (
            "Maître Yi est un jungler de mêlée qui gagne par la vitesse : Coup double frappe deux fois après plusieurs attaques consécutives, Assaut éclair le rend impossible à cibler, Style Wuju ajoute des dégâts bruts, et Highlander lui donne vitesses et insensibilité aux ralentissements. "
            "Tuer ou assister prolonge Highlander et réduit les délais de ses compétences."
        ),
        "laning": (
            "Attaque avec Assaut éclair : les attaques de base réduisent son délai. "
            "Méditation te soigne chaque seconde et cumule des effets Coup double."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["R", "Q", "E", "AA"], "when": "Un carry est à portée.",
             "how": "Highlander augmente tes vitesses de déplacement et d'attaque et t'insensibilise aux ralentissements ; Assaut éclair te rend impossible à cibler, Style Wuju ajoute des dégâts bruts."},
            {"name": "Le nettoyage", "keys": ["Q", "AA", "Q", "AA"], "when": "Ton équipe gagne le combat.",
             "how": "Chaque élimination ou assistance réduit les délais de tes compétences et prolonge Highlander : enchaîne Assaut éclair de cible en cible."},
            {"name": "La récupération", "keys": ["W", "AA"], "when": "Tu es à bas PV.",
             "how": "Méditation régénère tes PV chaque seconde, réduit un court moment les dégâts subis et met en pause la durée restante de Style Wuju et de Highlander."},
        ],
        "mistakes": [
            "Utiliser Assaut éclair sans cible ou sans plan de sortie.",
            "Lancer Highlander trop tôt : sa durée est limitée.",
            "Ne pas enchaîner les attaques : Coup double en dépend.",
        ],
    }},
}
