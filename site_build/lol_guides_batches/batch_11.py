"""Guides rédigés, lot 11. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Orianna": {"fr": {
        "playstyle": (
            "Orianna est une mage qui joue avec sa sphère : chaque compétence lui donne un ordre (Attaque, Dissonance, Protection, Onde de choc), et la sphère reste dans la zone ciblée. "
            "Sa passive inflige des dégâts croissants sur la même cible, et son ultime projette les ennemis vers la sphère après un bref délai."
        ),
        "laning": (
            "Ordre : Attaque envoie la sphère sur une zone en blessant les cibles sur son passage. "
            "Place la sphère : Dissonance et Onde de choc partent d'elle, pas de toi."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "AA"], "when": "Un ennemi est à portée.",
             "how": "Ordre : Attaque envoie la sphère qui reste dans la zone, Ordre : Dissonance inflige des dégâts autour d'elle et crée une zone qui ralentit les ennemis et accélère tes alliés, ton attaque profite de ta passive."},
            {"name": "La protection", "keys": ["E", "W"], "when": "Ton carry est plongé.",
             "how": "Ordre : Protection fixe la sphère sur un allié : bouclier, armure et résistance magique, et dégâts aux ennemis sur son passage."},
            {"name": "L'ultime de regroupement", "keys": ["Q", "R", "W"], "when": "Les ennemis sont autour de la sphère.",
             "how": "Onde de choc projette les ennemis proches vers la sphère après un bref délai : place-la au milieu de ton équipe ou sur la cible."},
        ],
        "mistakes": [
            "Oublier où est ta sphère : tes compétences partent d'elle.",
            "Lancer l'ultime sans sphère bien placée.",
            "Utiliser Protection sur un allié qui n'est pas menacé.",
        ],
    }},
    "Shyvana": {"fr": {
        "playstyle": (
            "Shyvana est une jungler qui gagne de la défense en éliminant des champions, grands sbires et grands monstres (Armure d'écailles). "
            "Son ultime la transforme en dragon, ce qui renforce ses compétences : Frappe enflammée gagne une réactivation, Égide de feu la soigne, et Éruption traverse les ennemis en laissant une traînée de feu."
        ),
        "laning": (
            "Frappe enflammée frappe la cible et la zone autour ; réactive-la. "
            "Égide de feu te donne bouclier et vitesse avant d'exploser."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "Q", "W"], "when": "Un ennemi est à portée.",
             "how": "Frappe enflammée frappe la cible et la zone, réactive-la ; Égide de feu te protège et explose après un court délai."},
            {"name": "La forme de dragon", "keys": ["R", "E", "Q", "Q"], "when": "Un combat s'engage.",
             "how": "Vol du dragon te transforme en dragon et fait fuir les ennemis sur ton passage ; Frappe enflammée gagne une réactivation infligeant d'énormes dégâts à une cible unique, Éruption traverse en laissant une traînée de feu."},
            {"name": "Le soin", "keys": ["R", "W"], "when": "Tu es blessée en forme de dragon.",
             "how": "En forme de dragon, l'explosion d'Égide de feu te soigne si elle touche un champion ennemi."},
        ],
        "mistakes": [
            "Utiliser l'ultime trop tôt : la forme de dragon est ta fenêtre.",
            "Oublier la réactivation de Frappe enflammée.",
            "Négliger Armure d'écailles : elle améliore tes résistances aux éliminations.",
        ],
    }},
    "Gragas": {"fr": {
        "playstyle": (
            "Gragas est un combattant-mage qui se soigne à chaque compétence. "
            "Fût roulant ralentit et explose (manuellement ou après 4 secondes, avec plus de puissance au fil du temps), Coup de bidon étourdit, Rage d'ivrogne réduit ses dégâts subis, et Fût explosif repousse les ennemis."
        ),
        "laning": (
            "Chaque compétence te soigne grâce à ta passive. "
            "Rage d'ivrogne te donne une réduction de dégâts et une attaque qui blesse tous les ennemis proches."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "AA"], "when": "Un ennemi est à portée du fût.",
             "how": "Fût roulant explose à la demande, sa puissance augmente avec le temps et ralentit ; Rage d'ivrogne prépare une attaque de zone."},
            {"name": "L'engagement", "keys": ["E", "AA", "Q", "R"], "when": "Plusieurs ennemis sont groupés.",
             "how": "Coup de bidon charge et étourdit tous les ennemis proches du premier percuté ; Fût explosif repousse les ennemis touchés par l'explosion."},
            {"name": "La défense", "keys": ["W", "E"], "when": "Tu es pris à partie.",
             "how": "Rage d'ivrogne réduit les dégâts subis et inflige des dégâts à tous les ennemis proches avec ta prochaine attaque."},
        ],
        "mistakes": [
            "Faire exploser le fût trop tôt : sa puissance grandit avec le temps.",
            "Lancer l'ultime en repoussant les ennemis vers leurs alliés.",
            "Utiliser Coup de bidon sans plan pour la suite.",
        ],
    }},
    "Zilean": {"fr": {
        "playstyle": (
            "Zilean est un support-mage du temps : Bombe à retardement colle sur une unité et explose après 3 secondes, Retour rapide réduit les délais de ses compétences, Distorsion temporelle ralentit un ennemi ou accélère un allié, et Retour temporel renvoie un allié dans le passé s'il subit des dégâts mortels. "
            "Sa passive stocke de l'expérience qu'il peut offrir à un allié."
        ),
        "laning": (
            "Pose des bombes sur les ennemis et les sbires : elles se collent sur la première unité proche, en priorité les champions. "
            "Une bombe qui explose prématurément à cause d'une autre étourdit."
        ),
        "combos": [
            {"name": "L'étourdissement", "keys": ["Q", "Q", "E"], "when": "Un ennemi est à portée de bombes.",
             "how": "Lance une bombe, puis une seconde : si une bombe explose prématurément à cause d'une autre, les ennemis sont étourdis ; Distorsion temporelle ralentit la cible."},
            {"name": "Le tempo", "keys": ["Q", "W", "Q"], "when": "Tu veux relancer tes bombes vite.",
             "how": "Retour rapide réduit le délai de tes autres compétences : relance immédiatement Bombe à retardement."},
            {"name": "La protection", "keys": ["R", "E"], "when": "Ton carry va mourir.",
             "how": "Retour temporel place une rune sur un allié qui le renvoie dans le passé s'il subit des dégâts mortels ; Distorsion temporelle accélère ton équipe."},
        ],
        "mistakes": [
            "Placer l'ultime sur un allié trop tard : il faut le placer avant les dégâts mortels.",
            "Poser une bombe sans cible en approche.",
            "Oublier ta passive : donne de l'expérience à un allié.",
        ],
    }},
    "Aphelios": {"fr": {
        "playstyle": (
            "Aphelios est un tireur à cinq armes de Lunari : il en porte deux à la fois (principale et secondaire), et chaque arme a une attaque et une compétence uniques. "
            "Les attaques et compétences consomment les munitions ; sans munitions, l'arme est jetée et Alune invoque la suivante. Phase échange les deux armes."
        ),
        "laning": (
            "Apprends l'ordre des armes : le troisième emplacement t'indique la prochaine. "
            "Chaque arme a sa compétence active : Calibrum marque, Severum court en frappant, Gravitum immobilise, Infernum frappe en cône, Crescendum déploie une vigie."
        ),
        "combos": [
            {"name": "Le harcèlement à distance", "keys": ["Q", "AA", "W"], "when": "Ton arme principale est Calibrum.",
             "how": "Calibrum tire une balle à longue portée qui marque la cible et permet une seconde attaque à très longue portée ; Phase échange tes armes pour enchaîner."},
            {"name": "Le combat d'équipe", "keys": ["W", "Q", "AA", "R"], "when": "Un combat d'équipe est engagé.",
             "how": "Choisis l'arme dont la compétence sert le mieux : Infernum frappe en cône avec l'arme secondaire, Crescendum déploie une vigie qui attaque, Gravitum immobilise les ennemis ralentis."},
            {"name": "L'ultime d'arme", "keys": ["R"], "when": "Un groupe d'ennemis est aligné.",
             "how": "Veille au clair de lune envoie un rayon qui explose au contact d'un champion ennemi et applique l'effet unique de ton arme principale."},
        ],
        "mistakes": [
            "Ne pas surveiller les munitions : une arme sans munitions est jetée.",
            "Utiliser l'ultime sans regarder ton arme principale : l'effet en dépend.",
            "Oublier Phase : échanger tes armes change attaque et compétence.",
        ],
    }},
    "Lissandra": {"fr": {
        "playstyle": (
            "Lissandra est une mage de glace et de contrôle : Éclat de glace blesse et ralentit, Cercle de givre immobilise les ennemis proches, Chemin glacial la transporte à sa griffe, et son ultime peut geler un ennemi ou l'immobiliser elle-même pour se soigner. "
            "Sa passive transforme les champions morts près d'elle en Serviteurs de glace qui explosent."
        ),
        "laning": (
            "Éclat de glace traverse la cible et blesse les ennemis derrière : lance-le dans l'axe. "
            "Chemin glacial te permet de te repositionner : réactive-le pour te téléporter à ta griffe."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["E", "E", "W", "Q"], "when": "Un ennemi est à portée de griffe.",
             "how": "Chemin glacial lance une griffe et te transporte à elle ; Cercle de givre congèle et immobilise les ennemis proches ; Éclat de glace finit."},
            {"name": "Le contrôle", "keys": ["R", "W", "Q"], "when": "Un carry est isolé.",
             "how": "Tombeau polaire sur un champion ennemi le congèle et l'étourdit ; de la glace obscure émane de la cible et ralentit les ennemis proches."},
            {"name": "La survie", "keys": ["R"], "when": "Tu es en danger.",
             "how": "Lancé sur toi, Tombeau polaire t'immobilise dans la glace : tu te soignes, deviens impossible à cibler et insensible aux dégâts."},
        ],
        "mistakes": [
            "Lancer Chemin glacial dans le vide.",
            "Utiliser l'ultime sur toi trop tôt : tu ne peux pas agir pendant.",
            "Oublier les Serviteurs de glace : ils ralentissent et explosent.",
        ],
    }},
    "Veigar": {"fr": {
        "playstyle": (
            "Veigar est un mage qui gagne en puissance permanente : toucher un champion avec une compétence, tuer un champion ou assister lui donne de la puissance. "
            "Coup malin, sur des unités tuées, en donne aussi. Profanation crée une cage qui étourdit, et Explosion primordiale inflige des dégâts qui augmentent avec les PV manquants de la cible."
        ),
        "laning": (
            "Coup malin touche deux ennemis : tue les sbires avec pour gagner de la puissance. "
            "Matière noire a un délai de récupération réduit par tes cumuls de puissance."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "AA"], "when": "Un ennemi est à portée.",
             "how": "Coup malin blesse les deux premiers ennemis, Matière noire fait tomber de la matière noire pour des dégâts magiques."},
            {"name": "La cage", "keys": ["E", "W", "Q"], "when": "Un ennemi est poursuivi.",
             "how": "Profanation crée une cage qui étourdit les ennemis qui la traversent : place-la autour d'un ennemi ou de ton équipe pour l'engager."},
            {"name": "L'exécution", "keys": ["W", "Q", "R"], "when": "Un champion est à basse vie.",
             "how": "Explosion primordiale inflige d'importants dégâts qui augmentent avec les PV manquants de la cible : enchaîne pour finir."},
        ],
        "mistakes": [
            "Lancer l'ultime sur un ennemi en pleine santé.",
            "Négliger le farm avec Coup malin : c'est ta puissance.",
            "Placer Profanation où les ennemis ne passeront pas.",
        ],
    }},
    "Riven": {"fr": {
        "playstyle": (
            "Riven est une combattante de burst : ses compétences chargent sa lame, ce qui permet à ses attaques de base d'infliger des dégâts supplémentaires en consommant des charges. "
            "Ailes brisées se réactive trois fois (le troisième coup repousse), Décharge de ki étourdit, Bravoure la fait avancer en bloquant des dégâts, et Lame de l'exilée augmente ses dégâts et sa portée avec Taillade du vent."
        ),
        "laning": (
            "Enchaîne compétence et attaque pour consommer les charges de ta lame. "
            "Ailes brisées peut être réactivée deux fois pendant une courte période."
        ),
        "combos": [
            {"name": "Le burst", "keys": ["E", "W", "Q", "AA", "Q", "AA", "Q"], "when": "Un ennemi est à portée.",
             "how": "Bravoure te rapproche en bloquant des dégâts, Décharge de ki étourdit les ennemis proches, trois Ailes brisées avec des attaques entre chaque, le troisième coup repousse."},
            {"name": "L'ultime de finition", "keys": ["R", "W", "Q", "R"], "when": "Un ennemi est à basse vie.",
             "how": "Lame de l'exilée augmente tes dégâts d'attaque et ta portée ; pendant l'effet, tu peux utiliser une fois Taillade du vent, une puissante attaque à distance."},
            {"name": "La sortie", "keys": ["E", "Q", "Q"], "when": "Tu dois te dégager.",
             "how": "Bravoure te déplace et bloque des dégâts, Ailes brisées te fait avancer de nouveau."},
        ],
        "mistakes": [
            "Gaspiller des charges : enchaîne attaque et compétence.",
            "Utiliser Ailes brisées trois fois sans cible.",
            "Lancer Taillade du vent trop tôt : elle est à usage unique par ultime.",
        ],
    }},
    "Mel": {"fr": {
        "playstyle": (
            "Mel est une mage qui accumule des projectiles bonus (jusqu'à neuf) à chaque compétence pour sa prochaine attaque, et applique Accablement, cumulable à l'infini. "
            "S'il y a assez de cumuls sur une cible, ils sont consommés pour l'exécuter. Éclipse dorée frappe tous les ennemis marqués sans limite de distance."
        ),
        "laning": (
            "Enchaîne compétences pour charger ta prochaine attaque de projectiles bonus. "
            "Réfutation renvoie les projectiles ennemis à l'envoyeur : garde-la pour une compétence à distance décisive."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée.",
             "how": "Salve radieuse inflige des dégâts répétés en zone, Piège solaire immobilise au centre et ralentit en périphérie, ton attaque profite des projectiles bonus."},
            {"name": "La protection", "keys": ["W"], "when": "Un ennemi lance des projectiles.",
             "how": "Réfutation crée une barrière qui renvoie les projectiles ennemis à l'envoyeur, te protège et augmente ta vitesse de déplacement."},
            {"name": "L'exécution", "keys": ["Q", "E", "AA", "R"], "when": "Plusieurs ennemis sont marqués.",
             "how": "Éclipse dorée frappe tous les ennemis marqués par Accablement sans tenir compte de la distance, avec des dégâts bonus par cumul."},
        ],
        "mistakes": [
            "Gaspiller Réfutation sur des sbires.",
            "Lancer l'ultime sans avoir empilé Accablement.",
            "Attaquer sans compétence préalable : tu perds tes projectiles bonus.",
        ],
    }},
    "Sion": {"fr": {
        "playstyle": (
            "Sion est un tank qui revient à la vie après sa mort, avec des attaques très rapides qui le soignent et infligent des dégâts selon les PV max de la cible. "
            "Fracas meurtrier se charge pour projeter et étourdir, Feu intérieur donne un bouclier et de la vie max aux éliminations, et Assaut inarrêtable charge en accélérant."
        ),
        "laning": (
            "Fracas meurtrier : charge assez longtemps pour projeter et étourdir. "
            "Feu intérieur te donne un bouclier ; tuer des ennemis augmente passivement tes PV max."
        ),
        "combos": [
            {"name": "L'étourdissement", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée.",
             "how": "Fracas meurtrier chargé assez longtemps projette et étourdit ; Cri du tueur blesse, ralentit et réduit l'armure."},
            {"name": "L'ultime d'engagement", "keys": ["R", "Q", "W"], "when": "Un ennemi est loin.",
             "how": "Assaut inarrêtable charge en accélérant et tu peux légèrement changer de trajectoire ; l'impact projette en l'air selon la distance parcourue."},
            {"name": "Le bouclier", "keys": ["W", "AA", "W"], "when": "Tu es engagé.",
             "how": "Feu intérieur t'entoure d'un bouclier ; réactive-le après 3 secondes pour infliger des dégâts magiques aux ennemis proches."},
        ],
        "mistakes": [
            "Lâcher Fracas meurtrier trop tôt : il ne projette qu'après une charge suffisante.",
            "Lancer l'ultime sans direction : il accélère et ne s'arrête pas.",
            "Oublier ta passive : tu reviens temporairement à la vie.",
        ],
    }},
}
