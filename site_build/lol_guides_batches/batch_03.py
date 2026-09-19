"""Guides rédigés, lot 3. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Camille": {"fr": {
        "playstyle": (
            "Camille est une combattante de mobilité qui gagne un bouclier en attaquant des champions, adapté au type de dégâts de l'ennemi (physique ou magique). "
            "Grappin lui permet de bondir depuis un mur et de projeter les champions à l'atterrissage, et son ultime enferme une cible dans une zone où ses attaques infligent des dégâts magiques supplémentaires."
        ),
        "laning": (
            "Protocole de précision inflige beaucoup plus de dégâts si tu attends entre les deux activations : ne le relance pas trop vite. "
            "Ta passive te protège selon le type de dégâts de ton adversaire, ce qui rend les échanges au corps à corps favorables."
        ),
        "combos": [
            {"name": "L'échange en lane", "keys": ["Q", "AA", "Q", "W"], "when": "Un ennemi est à portée d'attaque.",
             "how": "Protocole de précision renforce ta prochaine attaque et te donne de la vitesse ; relance-le après une courte attente pour infliger beaucoup plus de dégâts. Balayage tactique touche avec la moitié extérieure du cône pour ralentir et te soigner."},
            {"name": "L'engagement avec Grappin", "keys": ["E", "E", "Q", "W", "AA"], "when": "Un mur est proche de la cible.",
             "how": "Grappin te propulse vers un mur puis te fait bondir ; les champions ennemis touchés à l'atterrissage sont projetés en l'air. Enchaîne avec tes compétences pendant qu'ils sont vulnérables."},
            {"name": "L'exécution en zone", "keys": ["R", "Q", "W", "AA"], "when": "Un carry est isolé.",
             "how": "Ultimatum Hextech te fait foncer sur un champion et l'emprisonne dans une zone ; profite des dégâts magiques bonus de tes attaques de base sur lui."},
        ],
        "mistakes": [
            "Relancer Protocole de précision trop vite : l'attente entre les deux attaques augmente beaucoup les dégâts.",
            "Lancer Balayage tactique en visant la moitié intérieure du cône : c'est la moitié extérieure qui ralentit et te soigne.",
            "Utiliser Grappin sans mur proche : il en a besoin pour se propulser.",
        ],
    }},
    "Ekko": {"fr": {
        "playstyle": (
            "Ekko est un assassin-mage qui manipule le temps. Sa passive inflige des dégâts magiques bonus toutes les trois attaques ou compétences sur la même cible. "
            "Rétrobang ralentit et blesse deux fois, Convergence parallèle crée une anomalie qui ralentit puis étourdit, et son ultime le rend impossible à cibler en le ramenant à sa position d'il y a quelques secondes."
        ),
        "laning": (
            "Utilise Rétrobang à distance : la grenade revient vers toi et blesse sur son chemin. "
            "Ne garde pas Chronofracture pour rien : son ultime est aussi bien un outil de survie qu'un engagement."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "E", "AA", "AA"], "when": "Un ennemi est à portée de la grenade.",
             "how": "Rétrobang inflige des dégâts et ralentit, Rush déphasé te téléporte près de la cible avec des dégâts bonus, puis tes attaques déclenchent la passive toutes les trois touches."},
            {"name": "L'étourdissement", "keys": ["W", "Q", "E"], "when": "Les ennemis se regroupent.",
             "how": "Convergence parallèle crée après quelques secondes une anomalie qui ralentit ; si tu y entres, tu obtiens un bouclier et étourdis ceux qui s'y trouvent. Place-la là où ils iront."},
            {"name": "L'ultime de secours", "keys": ["R"], "when": "Tu es en danger ou tu veux blesser plusieurs ennemis.",
             "how": "Chronofracture te rend impossible à cibler et te ramène là où tu étais quelques secondes plus tôt, en récupérant un pourcentage des PV perdus ; les ennemis proches de ton arrivée subissent d'importants dégâts."},
        ],
        "mistakes": [
            "Utiliser l'ultime sans se souvenir que tu retournes à ta position d'il y a quelques secondes : évalue-la avant.",
            "Poser Convergence parallèle au hasard : elle a un délai avant de créer l'anomalie.",
            "Gaspiller Rush déphasé : c'est ton esquive, sa prochaine attaque te téléporte près de la cible.",
        ],
    }},
    "Seraphine": {"fr": {
        "playstyle": (
            "Séraphine est une mage de soutien dont la passive lui fait lancer deux fois la compétence de base choisie toutes les trois compétences. "
            "Elle protège et soigne avec Son ambiophonique, inflige des dégâts en zone avec Note aiguë et Battement, et son ultime charme les ennemis touchés avec une portée qui s'étend à chaque champion touché."
        ),
        "laning": (
            "Lance des compétences près de tes alliés : ta prochaine attaque de base gagne en portée et en dégâts magiques. "
            "Note aiguë est ton harcèlement principal, Battement restreint les déplacements en ligne."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée de zone.",
             "how": "Note aiguë inflige des dégâts en zone, Battement touche sur une ligne et restreint leurs déplacements, puis ton attaque bénéficie de la portée bonus de ta passive."},
            {"name": "La protection", "keys": ["W", "Q", "E"], "when": "Tes alliés sont menacés.",
             "how": "Son ambiophonique donne hâte et bouclier aux alliés proches ; si tu as déjà un bouclier, il soigne aussi les alliés. Place-le en plein combat."},
            {"name": "L'ultime en chaîne", "keys": ["R", "Q", "E"], "when": "Des ennemis et des alliés sont alignés.",
             "how": "Bis inflige des dégâts et charme les ennemis touchés ; sa portée s'étend à chaque champion, allié ou ennemi, touché. Vise pour en toucher un maximum."},
        ],
        "mistakes": [
            "Lancer l'ultime sans allié ou ennemi pour étendre sa portée.",
            "Négliger la passive : la compétence lancée deux fois est ta meilleure occasion de dégâts.",
            "Utiliser Son ambiophonique trop tôt : son délai de récupération est long.",
        ],
    }},
    "Akali": {"fr": {
        "playstyle": (
            "Akali est une assassine d'énergie qui joue avec le cercle d'énergie créé autour de la cible blessée : le quitter renforce sa prochaine attaque en portée et en dégâts. "
            "Linceul nébuleux la rend invisible et impossible à cibler, Lancer acrobatique la rue sur une cible marquée, et son ultime peut exécuter les ennemis touchés à la réactivation."
        ),
        "laning": (
            "Vague de kunais ralentit et frappe à courte portée : enchaîne avec ta passive en sortant du cercle pour renforcer ton attaque. "
            "Linceul nébuleux te protège brièvement mais tu es révélée si tu attaques ou utilises des compétences."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "E"], "when": "Un ennemi est à portée de kunais.",
             "how": "Vague de kunais blesse et ralentit, crée le cercle d'énergie ; sors du cercle pour renforcer ton attaque, puis Lancer acrobatique."},
            {"name": "L'engagement complet", "keys": ["E", "E", "R", "R", "Q"], "when": "Un carry est à portée d'engagement.",
             "how": "Lancer acrobatique marque le premier ennemi ou nuage touché, réactive-le pour te ruer sur la cible marquée. Maîtrise absolue te fait bondir puis, à la réactivation, exécuter tous les ennemis que tu frappes."},
            {"name": "La fuite", "keys": ["W", "E"], "when": "Tu dois te dégager.",
             "how": "Linceul nébuleux te donne de la vitesse de déplacement et t'invisibilise ; Lancer acrobatique sur un nuage de fumée touché te permet de te ruer dessus."},
        ],
        "mistakes": [
            "Lancer l'ultime sans avoir de cible à portée : il est ton principal outil d'exécution.",
            "Attaquer depuis le Linceul en oubliant que cela te révèle temporairement.",
            "Dépenser trop d'énergie sur des sbires : chaque compétence en coûte.",
        ],
    }},
    "Nami": {"fr": {
        "playstyle": (
            "Nami est une enchanteresse d'eau : Prison aqueuse étourdit, Flux et reflux soigne les alliés et blesse les ennemis en rebondissant, et Bénédiction de l'Aquamancienne renforce les attaques d'un allié (dégâts magiques et ralentissement). "
            "Ses compétences sur les alliés leur donnent de la vitesse de déplacement, et son ultime projette les ennemis touchés en l'air."
        ),
        "laning": (
            "Prison aqueuse est ton engagement : sa bulle étourdit à l'impact, vise bien. "
            "Bénédiction de l'Aquamancienne sur ton carry lui donne ralentissement et dégâts bonus : c'est l'essentiel de ton harcèlement."
        ),
        "combos": [
            {"name": "L'engagement de lane", "keys": ["Q", "E", "W"], "when": "Ton carry est prêt à frapper.",
             "how": "Prison aqueuse étourdit à l'impact, Bénédiction de l'Aquamancienne renforce ton allié, Flux et reflux soigne ton équipe et blesse la cible en rebondissant."},
            {"name": "La protection", "keys": ["W", "E"], "when": "Un allié est en difficulté.",
             "how": "Flux et reflux rebondit sur les champions alliés et ennemis : soigne les alliés et blesse les ennemis. Bénédiction de l'Aquamancienne ralentit les agresseurs."},
            {"name": "L'ultime d'engagement", "keys": ["R", "Q", "W"], "when": "Un combat d'équipe s'engage.",
             "how": "Raz-de-marée projette les ennemis touchés en l'air, les ralentit et les blesse ; tes alliés touchés gagnent le double de l'effet de Déferlantes."},
        ],
        "mistakes": [
            "Lancer Prison aqueuse sans laisser le temps de la bulle : elle étourdit à l'impact, prévois la trajectoire.",
            "Oublier de soigner : Flux et reflux est aussi ton outil de sustain.",
            "Utiliser l'ultime sans allié à proximité : son effet de vitesse profite à ton équipe.",
        ],
    }},
    "Graves": {"fr": {
        "playstyle": (
            "Graves est un tireur-jungler au fusil unique : chaque attaque tire quatre balles qui ne traversent pas les unités, et il doit recharger quand il n'a plus de munitions. "
            "Ruée vers l'or lui donne de l'armure et de la résistance magique, Écran de fumée réduit la vision des ennemis, et Dégâts collatéraux inflige de lourds dégâts au premier champion touché."
        ),
        "laning": (
            "Tes balles ne traversent pas les unités : place-toi à courte distance pour toucher avec toutes. "
            "Ruée vers l'or se recharge quand tu touches avec tes attaques de base et te donne un bonus de défense."
        ),
        "combos": [
            {"name": "Le combo de mêlée", "keys": ["E", "AA", "Q", "AA"], "when": "Un ennemi est proche.",
             "how": "Ruée vers l'or te rapproche et te donne de l'armure ; tes attaques réduisent son délai de récupération, Terminus explose après 1 seconde ou au contact d'un obstacle."},
            {"name": "La zone de contrôle", "keys": ["W", "Q", "E", "AA"], "when": "Tu veux réduire la vision ennemie.",
             "how": "Écran de fumée blesse et ralentit brièvement et réduit le champ de vision ; enchaîne avec Terminus et Ruée."},
            {"name": "L'ultime en cône", "keys": ["R"], "when": "Des ennemis sont en ligne.",
             "how": "Dégâts collatéraux inflige de lourds dégâts au premier champion touché puis explose en cône : vise un ennemi de ligne de front avec d'autres derrière."},
        ],
        "mistakes": [
            "Attaquer de loin : tes balles ne touchent pas toutes à longue portée.",
            "Ignorer ton chargeur : recharger au mauvais moment te coûte des dégâts.",
            "Lancer l'ultime sans regarder ce que le cône touchera.",
        ],
    }},
    "Ambessa": {"fr": {
        "playstyle": (
            "Ambessa est une combattante d'énergie dont la passive déclenche une ruée courte après une compétence lancée en se déplaçant ou en attaquant, avec une portée, des dégâts et une vitesse d'attaque bonus sur la prochaine attaque. "
            "Ses doubles chiens-dragons lui donnent des variantes de compétences, et son ultime la téléporte sur l'ennemi le plus éloigné pour l'étourdir."
        ),
        "laning": (
            "Lance une compétence en te déplaçant ou en attaquant pour déclencher ta ruée : elle est la base de ton enchaînement. "
            "Égide dévastatrice te donne un bouclier et inflige des dégâts bonus si tu bloques des dégâts d'unités autres que des sbires."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "Q", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Frappe fourbe inflige des dégâts bonus, et si elle touche, la suivante devient une Frappe fracassante en ligne droite. Lacération ralentit et blesse."},
            {"name": "La ruée par Lacération", "keys": ["E", "AA", "W"], "when": "Tu veux amplifier ta ruée.",
             "how": "Utiliser Ruée des chiens-dragons à partir de Lacération déclenche une frappe supplémentaire à la fin. Égide dévastatrice te protège pendant l'enchaînement."},
            {"name": "L'exécution", "keys": ["R", "Q", "E"], "when": "Un carry isolé est en ligne droite.",
             "how": "Exécution publique te téléporte sur l'ennemi le plus éloigné sur une ligne, le neutralise, puis le projette au sol pour dégâts et étourdissement."},
        ],
        "mistakes": [
            "Lancer l'ultime sans vérifier qui est l'ennemi le plus éloigné sur la ligne.",
            "Ne pas déclencher ta ruée : elle fait une grande part de tes dégâts.",
            "Utiliser Égide dévastatrice sans rien à bloquer : ses dégâts bonus dépendent de ce que tu bloques.",
        ],
    }},
    "Talon": {"fr": {
        "playstyle": (
            "Talon est un assassin mobile : ses compétences blessent champions et grands monstres (jusqu'à 3 cumuls), et une attaque sur un champion à 3 blessures le fait saigner pour de gros dégâts sur la durée. "
            "Voie de l'assassin lui permet de sauter par-dessus les murs, et Assaut ténébreux le rend invisible avec un bonus de vitesse."
        ),
        "laning": (
            "Empile 3 blessures avec Diplomatie noxienne et Ratissage, puis attaque pour déclencher le saignement. "
            "Voie de l'assassin a un court délai de récupération mais le terrain franchi en a un long : n'en abuse pas."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["W", "Q", "AA"], "when": "Un ennemi est à portée de lames.",
             "how": "Ratissage blesse à l'aller et au retour et ralentit, Diplomatie noxienne poignarde (critique en mêlée) et cumule, l'attaque déclenche le saignement à 3 cumuls."},
            {"name": "L'assassinat", "keys": ["E", "Q", "W", "AA", "R"], "when": "Un carry est isolé derrière un mur.",
             "how": "Voie de l'assassin franchit le terrain, Diplomatie noxienne saute sur la cible à distance, puis Assaut ténébreux te rend invisible et blesse les ennemis touchés par les lames."},
            {"name": "La sortie", "keys": ["R", "E"], "when": "Tu dois t'échapper.",
             "how": "Assaut ténébreux te rend invisible avec un bonus de vitesse de déplacement ; Voie de l'assassin franchit un mur pour couper la poursuite."},
        ],
        "mistakes": [
            "Attaquer sans les 3 blessures : le saignement dépend des cumuls.",
            "Utiliser Voie de l'assassin sans réfléchir : le terrain franchi a un long délai de récupération.",
            "Lancer l'ultime trop tôt : les lames reviennent vers toi quand tu redeviens visible.",
        ],
    }},
    "Bard": {"fr": {
        "playstyle": (
            "Bard est un support voyageur qui collecte des carillons pour gagner de l'expérience, du mana et de la vitesse de déplacement hors combat. "
            "Ses Meeps ajoutent des dégâts à ses attaques et, avec assez de carillons, blessent en zone et ralentissent. Lien cosmique ralentit et peut étourdir, Route magique ouvre un portail, et son ultime met en stase toutes les unités et les tourelles."
        ),
        "laning": (
            "Collecte les carillons pour rester en avance en expérience et en mana. "
            "Lien cosmique étourdit s'il touche un mur ou un deuxième ennemi : place-toi pour ça."
        ),
        "combos": [
            {"name": "L'étourdissement", "keys": ["Q", "AA"], "when": "Un ennemi est près d'un mur ou d'un autre ennemi.",
             "how": "Lien cosmique ralentit le premier ennemi touché ; s'il touche un mur il étourdit la cible initiale, et un deuxième ennemi étourdit les deux. Les Meeps ajoutent leurs dégâts à tes attaques."},
            {"name": "Le sauvetage", "keys": ["W", "E"], "when": "Un allié est à basse vie ou a besoin de vitesse.",
             "how": "Don du gardien révèle un sanctuaire qui soigne et accélère le premier allié qui le touche. Route magique crée un portail à sens unique utilisable par tous, alliés et ennemis."},
            {"name": "L'ultime de contrôle", "keys": ["R", "Q"], "when": "Un combat est en cours.",
             "how": "Destin tempéré met brièvement en stase toutes les unités et les tourelles : utilise-le pour sauver un allié, stopper une poursuite ou rendre un engagement inutile."},
        ],
        "mistakes": [
            "Négliger les carillons : ils te donnent expérience, mana et vitesse.",
            "Utiliser l'ultime sans réfléchir : il met aussi tes alliés et les tourelles en stase.",
            "Ouvrir Route magique sans y penser : les ennemis peuvent aussi l'emprunter.",
        ],
    }},
    "Viego": {"fr": {
        "playstyle": (
            "Viego est un jungler dont la passive transforme les ennemis morts devant lui en spectres : il en prend le contrôle en les attaquant, récupère un pourcentage de leurs PV et accède à leurs compétences de base et à leurs objets. "
            "Il n'a pas leur ultime mais peut lancer le sien gratuitement. Sa lame inflige un pourcentage des PV actuels en dégâts supplémentaires."
        ),
        "laning": (
            "Ta lame inflige un pourcentage des PV actuels de la cible : elle est efficace contre les cibles à haute vie. "
            "Chemin tourmenté te permet de te cacher dans la Brume noire sous forme de spectre : camoufle-toi et gagne de la vitesse."
        ),
        "combos": [
            {"name": "Le combo de base", "keys": ["W", "Q", "AA", "Q"], "when": "Un ennemi est à portée de charge.",
             "how": "Gueule spectrale charge puis te rue vers l'avant avec une boule qui étourdit le premier ennemi touché ; Lame du roi déchu frappe deux fois les ennemis récemment touchés et te soigne."},
            {"name": "L'exécution", "keys": ["E", "Q", "R"], "when": "Un carry est affaibli.",
             "how": "Cœur brisé te téléporte près d'un champion et l'exécute à l'arrivée en repoussant ses alliés proches. Garde-le pour un ennemi à basse vie."},
            {"name": "Le cycle de possession", "keys": ["AA", "Q", "W", "E"], "when": "Un ennemi meurt devant toi.",
             "how": "Attaque le spectre pour prendre le contrôle du corps de l'ennemi mort : tu récupères des PV et disposes de ses compétences de base et de ses objets, tu peux lancer ton ultime gratuitement."},
        ],
        "mistakes": [
            "Ne pas exploiter les spectres : ta passive est ta meilleure source de puissance.",
            "Lancer Cœur brisé sur un ennemi en pleine santé.",
            "Se cacher dans la Brume sans plan : sortir en plein milieu d'ennemis est dangereux.",
        ],
    }},
}
