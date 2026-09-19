"""Guides rédigés, lot 17 (dernier). Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Illaoi": {"fr": {
        "playstyle": (
            "Illaoi est une combattante à tentacules : elle et les réceptacles qu'elle crée font apparaître des tentacules sur les éléments de décor infranchissables proches ; ils infligent des dégâts physiques et la soignent s'ils blessent un champion. "
            "Épreuve de l'esprit arrache l'esprit d'un ennemi et le rend réceptacle, et Acte de foi fait apparaître un tentacule par champion touché."
        ),
        "laning": (
            "Joue près d'éléments de décor : c'est là que tes tentacules apparaissent. "
            "Coup de tentacule augmente les dégâts des tentacules et en fait s'abattre un à l'activation."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["E", "Q", "W", "AA"], "when": "Un ennemi est près d'éléments de décor.",
             "how": "Épreuve de l'esprit arrache l'esprit de l'ennemi : s'il s'éloigne trop ou si l'esprit est détruit, il devient réceptacle et fait apparaître des tentacules ; Âpre leçon te fait bondir et pousse les tentacules proches à frapper la cible."},
            {"name": "L'ultime de zone", "keys": ["R", "Q", "W"], "when": "Plusieurs ennemis sont proches.",
             "how": "Acte de foi écrase ton idole, inflige des dégâts physiques et fait apparaître un tentacule par champion ennemi touché."},
            {"name": "Le harcèlement", "keys": ["Q", "AA"], "when": "Un ennemi est en lane.",
             "how": "Coup de tentacule inflige des dégâts physiques et amplifie les tentacules ; ils te soignent s'ils blessent un champion."},
        ],
        "mistakes": [
            "Te battre loin d'éléments de décor infranchissables.",
            "Lancer l'ultime sans plusieurs cibles.",
            "Oublier que l'esprit transmet une partie des dégâts à la cible originale.",
        ],
    }},
    "Evelynn": {"fr": {
        "playstyle": (
            "Evelynn est une jungler-assassine d'ombre : hors combat elle est plongée dans l'Ombre démoniaque, qui la soigne à bas PV et la camoufle à partir du niveau 6. "
            "Piques de haine frappe puis tire des piques, Séduction charme sa cible, Coup de fouet la fait avancer, et Faiseuse de veuves la rend impossible à cibler avant de la téléporter en arrière."
        ),
        "laning": (
            "Reste cachée : le camouflage arrive au niveau 6. "
            "Séduction maudit la cible : ta prochaine attaque ou sort la charme et réduit sa résistance magique."
        ),
        "combos": [
            {"name": "Le combo d'assassinat", "keys": ["W", "AA", "Q", "E", "R"], "when": "Un carry est à portée.",
             "how": "Séduction maudit la cible, ta prochaine attaque ou sort la charme et réduit sa résistance magique ; Piques de haine et Coup de fouet infligent des dégâts ; Faiseuse de veuves ravage la zone puis te téléporte en arrière."},
            {"name": "L'approche", "keys": ["Q", "E", "W"], "when": "Un ennemi est éloigné.",
             "how": "Piques de haine frappe la première unité touchée puis tire une ligne de piques vers les ennemis proches à plusieurs reprises ; Coup de fouet augmente ta vitesse de déplacement."},
            {"name": "La sortie", "keys": ["R", "E"], "when": "Tu es en danger.",
             "how": "Faiseuse de veuves te rend impossible à cibler, blesse devant toi et te téléporte loin en arrière."},
        ],
        "mistakes": [
            "Te faire voir avant de charmer.",
            "Utiliser l'ultime sans plan : elle te téléporte en arrière.",
            "Négliger l'Ombre démoniaque : elle te soigne à bas PV.",
        ],
    }},
    "Taric": {"fr": {
        "playstyle": (
            "Taric est un support-tank de protection : sa passive renforce ses 2 prochaines attaques après une compétence (dégâts magiques, délais réduits, attaques rapides). "
            "Bénédiction stellaire soigne les alliés proches selon ses charges, Bastion donne un bouclier et de l'armure, Éblouissement étourdit, et Lumière cosmique rend les alliés invulnérables."
        ),
        "laning": (
            "Enchaîne compétence puis attaques pour tirer parti de Plastronneur : chaque attaque renforcée donne une charge de Bénédiction stellaire. "
            "Bastion : tes compétences se lancent aussi depuis l'allié affecté."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["E", "AA", "AA", "Q"], "when": "Un ennemi est à portée.",
             "how": "Éblouissement prépare un rayon qui étourdit après un bref délai ; tes attaques renforcées infligent des dégâts magiques supplémentaires et chargent Bénédiction stellaire."},
            {"name": "La protection", "keys": ["W", "Q", "E"], "when": "Ton carry est menacé.",
             "how": "Bastion donne un bouclier à l'allié et lui donne de l'armure tant qu'il reste près de toi ; Bénédiction stellaire soigne selon tes charges."},
            {"name": "L'ultime d'équipe", "keys": ["R", "E", "Q"], "when": "Un combat décisif s'engage.",
             "how": "Lumière cosmique, après un délai, nimbe les alliés proches d'énergie cosmique et les rend invulnérables un court instant : prévois le délai."},
        ],
        "mistakes": [
            "Déclencher l'ultime trop tard : elle a un délai.",
            "Oublier les attaques renforcées de ta passive.",
            "Placer Éblouissement sans anticiper le délai.",
        ],
    }},
    "Heimerdinger": {"fr": {
        "playstyle": (
            "Heimerdinger est un mage de tourelles : sa passive lui donne de la vitesse près des tourelles alliées ou déployées. "
            "Tourelle H-28G Évolution pose une tourelle avec un laser perforant, Micro-roquettes Hextech converge vers son curseur, Grenade électro-tempête CH-2 étourdit et ralentit, et AMÉLIORATION ! augmente les effets de son prochain sort."
        ),
        "laning": (
            "Déploie des tourelles pour contrôler la lane. "
            "La tourelle inflige 50 % de dégâts aux tourelles ennemies."
        ),
        "combos": [
            {"name": "Le siège", "keys": ["Q", "Q", "W"], "when": "Tu veux pousser ou défendre.",
             "how": "Tourelle H-28G Évolution déploie une tourelle à laser perforant ; les Micro-roquettes convergent vers ton curseur à longue portée."},
            {"name": "L'étourdissement", "keys": ["Q", "E", "W"], "when": "Un ennemi approche de tes tourelles.",
             "how": "Grenade électro-tempête CH-2 étourdit les unités touchées directement et ralentit celles proches ; tes tourelles infligent des dégâts."},
            {"name": "La compétence améliorée", "keys": ["R", "E"], "when": "Un combat décisif s'engage.",
             "how": "AMÉLIORATION ! te permet d'avoir des effets augmentés sur ton prochain sort : choisis-le selon la situation."},
        ],
        "mistakes": [
            "Combattre loin de tes tourelles.",
            "Lancer l'amélioration sans sort clair à renforcer.",
            "Placer les tourelles sans protection.",
        ],
    }},
    "Nilah": {"fr": {
        "playstyle": (
            "Nilah est une combattante-tireuse de soutien : sa passive lui donne plus d'expérience sur les sbires et renforce et partage les soins et boucliers des alliés proches. "
            "Lame fluide augmente sa portée d'attaque, Voile de liesse l'immunise en esquivant les attaques, Torrent la rue, et Apothéose inflige des dégâts et attire les ennemis."
        ),
        "laning": (
            "Prends les sbires pour gagner plus d'expérience. "
            "Lame fluide augmente ta portée d'attaque un court instant."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "E", "AA"], "when": "Un ennemi est à portée.",
             "how": "Lame fluide inflige des dégâts en ligne droite et augmente ta portée d'attaque ; Torrent te rue avec enthousiasme et blesse sur ton chemin."},
            {"name": "La protection d'équipe", "keys": ["W", "AA"], "when": "Ton équipe est engagée.",
             "how": "Voile de liesse augmente ta vitesse de déplacement et te fait esquiver toutes les attaques ; tout allié que tu touches pendant la brume gagne aussi cet effet."},
            {"name": "L'ultime de regroupement", "keys": ["R", "Q", "E"], "when": "Les ennemis sont autour de toi.",
             "how": "Apothéose fait tournoyer ta lame-fouet, inflige des dégâts aux ennemis qui t'entourent puis les attire vers toi."},
        ],
        "mistakes": [
            "Lancer l'ultime sans être au contact.",
            "Utiliser Voile de liesse sans allié à toucher.",
            "Négliger les soins et boucliers de tes alliés.",
        ],
    }},
}
