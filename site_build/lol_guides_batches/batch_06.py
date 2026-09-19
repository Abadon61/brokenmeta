"""Guides rédigés, lot 6. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Aatrox": {"fr": {
        "playstyle": (
            "Aatrox est un combattant de mêlée qui gagne les échanges longs : sa passive lui permet, régulièrement, d'infliger des dégâts magiques bonus et de se soigner selon un pourcentage des PV max de la cible. "
            "Épée des Darkin frappe jusqu'à trois fois avec des zones différentes, Chaînes infernales ramène de force ceux qui ne quittent pas la zone, et son ultime augmente dégâts, soins et vitesse."
        ),
        "laning": (
            "Épée des Darkin a trois frappes de zones différentes : varie ton placement pour toucher à chaque fois. "
            "Ruée obscure te soigne passivement quand tu blesses des champions et te fait te ruer à l'activation."
        ),
        "combos": [
            {"name": "L'échange en lane", "keys": ["W", "Q", "AA", "E"], "when": "Un ennemi est à portée de chaînes.",
             "how": "Chaînes infernales blesse le premier ennemi touché et le ramène s'il ne sort pas de la zone, Épée des Darkin frappe ensuite, ton attaque bénéficie de ta passive, Ruée obscure te repositionne."},
            {"name": "Les trois frappes", "keys": ["Q", "Q", "Q"], "when": "L'ennemi est acculé.",
             "how": "Chaque coup d'Épée des Darkin a une zone d'effet différente : enchaîne les trois en te déplaçant pour toucher la cible."},
            {"name": "Le combat d'équipe", "keys": ["R", "W", "E", "Q"], "when": "Un combat s'engage.",
             "how": "Fossoyeur des mondes te donne dégâts, soins et vitesse et effraie les sbires proches ; sa durée est prolongée si tu participes à l'élimination d'un champion."},
        ],
        "mistakes": [
            "Lancer Épée des Darkin trois fois au même endroit : chaque coup a une zone différente.",
            "Utiliser Chaînes infernales sans laisser le temps à l'ennemi de rester dans la zone.",
            "Oublier ta passive : elle se déclenche régulièrement et soigne.",
        ],
    }},
    "Galio": {"fr": {
        "playstyle": (
            "Galio est un tank-mage qui protège ses alliés à distance : son ultime désigne la position d'un allié, donne un bouclier anti-magie à tous les alliés de la zone puis s'abat pour projeter les ennemis. "
            "Bouclier de Durand provoque après canalisation, Horion de la justice projette le premier champion touché, et Vents de guerre crée une tornade de dégâts sur la durée."
        ),
        "laning": (
            "Ta passive inflige des dégâts magiques en zone toutes les quelques secondes : cale une attaque de base sur les sbires et le champion. "
            "Bouclier de Durand te ralentit pendant la canalisation ; ne l'utilise que face à des dégâts magiques."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée de tornade.",
             "how": "Vents de guerre lance deux rafales qui convergent en tornade, Horion de la justice projette en l'air le premier champion touché, et ta passive inflige des dégâts en zone."},
            {"name": "L'engagement d'équipe", "keys": ["R", "E", "W"], "when": "Un allié est en danger loin de toi.",
             "how": "Entrée héroïque désigne la zone d'un allié, donne à tous les alliés un bouclier anti-magie, puis Galio s'abat après un délai en projetant les ennemis proches."},
            {"name": "La provocation", "keys": ["W"], "when": "Les ennemis visent ton équipe.",
             "how": "Bouclier de Durand est une posture défensive canalisée ; au relâchement, tu provoques et blesses les ennemis proches."},
        ],
        "mistakes": [
            "Lancer Entrée héroïque sans avoir prévenu ton allié : le délai est long.",
            "Utiliser Bouclier de Durand contre des dégâts physiques.",
            "Manquer Horion de la justice : il projette le premier champion touché.",
        ],
    }},
    "Blitzcrank": {"fr": {
        "playstyle": (
            "Blitzcrank est un support-tank qui gagne par le pick : Grappin propulsé attrape un ennemi et l'attire vers lui, puis Poing d'acier double les dégâts de sa prochaine attaque et projette la cible. "
            "Sa passive lui donne un bouclier à bas PV selon son mana, Surcharge augmente ses vitesses d'attaque et de déplacement, et son ultime blesse et réduit au silence."
        ),
        "laning": (
            "Le grappin est ta compétence de lane : chaque réussite décide de l'échange. "
            "Garde du mana : ta Barrière de mana en dépend."
        ),
        "combos": [
            {"name": "Le pick", "keys": ["Q", "E", "AA"], "when": "Un ennemi est isolé sur la trajectoire.",
             "how": "Grappin propulsé l'attire vers toi en le blessant, Poing d'acier double les dégâts de ton attaque et le projette dans les airs."},
            {"name": "La poursuite", "keys": ["W", "AA", "E"], "when": "Tu dois rattraper une cible.",
             "how": "Surcharge augmente considérablement tes vitesses d'attaque et de déplacement, mais te ralentit à la fin : ne l'utilise que si la poursuite est décisive."},
            {"name": "L'ultime de zone", "keys": ["R", "Q"], "when": "Les ennemis sont au corps à corps.",
             "how": "Champ de stase marque les ennemis attaqués (éclairs après 1 seconde) ; active-le pour détruire les boucliers proches, blesser et réduire au silence."},
        ],
        "mistakes": [
            "Lancer le grappin à l'aveugle : le délai de récupération est long.",
            "Utiliser Surcharge sans pouvoir profiter de la vitesse, car tu es ralenti ensuite.",
            "Oublier ta barrière : reste avec du mana quand tu es à bas PV.",
        ],
    }},
    "Khazix": {"fr": {
        "playstyle": (
            "Kha'Zix est un assassin de la jungle qui exploite les cibles isolées : elles sont marquées, et ses compétences profitent d'interactions avec elles. "
            "Il invisibilise avec l'ultime, ce qui déclenche sa passive (dégâts magiques bonus et ralentissement), et son ultime fait évoluer ses compétences avec de nouveaux effets."
        ),
        "laning": (
            "Cherche les cibles isolées : Goût de la peur y inflige plus de dégâts. "
            "Bond te permet d'engager ou de fuir ; certaines évolutions améliorent sa portée et son délai."
        ),
        "combos": [
            {"name": "L'assassinat isolé", "keys": ["R", "Q", "AA", "W"], "when": "Un ennemi est isolé.",
             "how": "Assaut du Néant te rend invisible et déclenche Menace invisible : ta prochaine attaque inflige des dégâts magiques bonus et ralentit ; Goût de la peur inflige plus de dégâts sur une cible isolée."},
            {"name": "L'engagement par bond", "keys": ["E", "Q", "W", "AA"], "when": "La cible est éloignée.",
             "how": "Bond blesse autour du point de chute ; enchaîne avec Goût de la peur et Pique du Néant, qui te soigne si tu es dans le rayon de l'explosion."},
            {"name": "La fuite invisible", "keys": ["R", "E"], "when": "Tu dois t'échapper.",
             "how": "Assaut du Néant augmente ta vitesse de déplacement et te rend invisible ; l'évolution Occultation adaptative allonge la durée et permet une utilisation supplémentaire."},
        ],
        "mistakes": [
            "Engager un ennemi accompagné : tes bonus dépendent de l'isolement.",
            "Ne pas choisir tes évolutions selon la situation.",
            "Rester visible avant l'engagement : tu perds Menace invisible.",
        ],
    }},
    "TwistedFate": {"fr": {
        "playstyle": (
            "Twisted Fate est un mage à cartes : Atouts tire trois cartes qui transpercent, Bonne pioche choisit une carte avec des effets supplémentaires pour l'attaque suivante, et Destinée révèle les champions ennemis et permet d'utiliser Portail pour se téléporter. "
            "Sa passive lui donne de l'or supplémentaire à chaque élimination."
        ),
        "laning": (
            "Bonne pioche prépare ton attaque suivante : choisis la carte selon le besoin (dégâts, contrôle, mana). "
            "Paquet donne de la vitesse d'attaque et des dégâts supplémentaires toutes les 4 attaques."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["W", "AA", "Q"], "when": "Un ennemi est à portée.",
             "how": "Bonne pioche choisit la carte pour ton attaque suivante, l'attaque profite de l'effet supplémentaire, puis Atouts tire trois cartes qui transpercent."},
            {"name": "Le portail", "keys": ["R", "R"], "when": "Un combat éloigné s'engage.",
             "how": "Destinée révèle les champions ennemis et permet d'utiliser Portail, qui te téléporte en 1,5 seconde à l'endroit choisi sur la carte."},
            {"name": "Le farm", "keys": ["Q", "AA", "AA", "AA"], "when": "Tu veux de l'or.",
             "how": "Dé pipé donne 1 à 6 PO supplémentaires à chaque unité tuée ; Paquet inflige des dégâts supplémentaires toutes les 4 attaques."},
        ],
        "mistakes": [
            "Utiliser Portail sans regarder les ennemis autour de ta destination.",
            "Gaspiller Bonne pioche sans cible.",
            "Négliger le farm : ta passive te donne de l'or.",
        ],
    }},
    "Janna": {"fr": {
        "playstyle": (
            "Janna est une enchanteresse de contrôle et de protection : ses alliés gagnent de la vitesse en se dirigeant vers elle, et Œil du cyclone protège un allié ou une tourelle en augmentant ses dégâts d'attaque. "
            "Vent hurlant projette les ennemis, Alizé réduit la vitesse d'un ennemi, et Mousson repousse les ennemis puis soigne les alliés."
        ),
        "laning": (
            "Vent hurlant peut se charger pour croître en taille : réactive-le pour libérer la tornade. "
            "Alizé te donne passivement de la vitesse de déplacement et de traverser les unités."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["W", "AA", "Q"], "when": "Un ennemi est à portée d'Alizé.",
             "how": "Alizé inflige des dégâts et réduit la vitesse de l'ennemi, ta passive ajoute des dégâts liés à ta vitesse de déplacement bonus, Vent hurlant relance."},
            {"name": "La protection", "keys": ["E", "W"], "when": "Ton carry est menacé.",
             "how": "Œil du cyclone protège un champion allié ou une tourelle contre les dégâts et augmente ses dégâts d'attaque."},
            {"name": "L'ultime défensif", "keys": ["R", "Q", "E"], "when": "Les ennemis plongent sur ton équipe.",
             "how": "Mousson repousse les ennemis au loin ; les dernières brises soignent les alliés proches tant que la compétence est active."},
        ],
        "mistakes": [
            "Lancer Vent hurlant sans le charger quand tu peux.",
            "Utiliser l'ultime trop tôt : ses soins dépendent de sa durée.",
            "Placer Œil du cyclone sur une cible qui ne se bat pas.",
        ],
    }},
    "Shaco": {"fr": {
        "playstyle": (
            "Shaco est un assassin de ruse : Tromperie le rend invisible et le téléporte, et sa première attaque invisible inflige des dégâts supplémentaires, avec un coup critique s'il frappe dans le dos. "
            "Boîte surprise effraie, Poison double ralentit et son ultime crée un double qui explose en mini-boîtes."
        ),
        "laning": (
            "Frappe dans le dos : tes attaques et Poison double infligent plus de dégâts. "
            "Pose des boîtes surprises aux endroits stratégiques : elles effraient puis attaquent."
        ),
        "combos": [
            {"name": "L'assassinat par derrière", "keys": ["Q", "AA", "E", "W"], "when": "Un carry est isolé.",
             "how": "Tromperie te rend invisible et te téléporte ; la première attaque est renforcée, critique dans le dos. Poison double ralentit et le poignard lancé inflige des dégâts supplémentaires sous 30 % de PV."},
            {"name": "Le piège", "keys": ["W", "E", "AA"], "when": "Un ennemi te poursuit.",
             "how": "Boîte surprise effraie puis attaque les ennemis proches quand elle est déclenchée ; Poison double ralentit sa poursuite."},
            {"name": "Le duel avec double", "keys": ["R", "Q", "AA"], "when": "Un combat rapproché s'engage.",
             "how": "Hallucination crée un double qui attaque (dégâts réduits aux tourelles) ; en mourant il explose, faisant apparaître trois mini-boîtes surprises."},
        ],
        "mistakes": [
            "Attaquer de face : tu perds tes bonus de dos.",
            "Poser des boîtes sans réfléchir à leur visibilité.",
            "Utiliser Tromperie sans plan pour la suite.",
        ],
    }},
    "Ryze": {"fr": {
        "playstyle": (
            "Ryze est un mage dont les compétences infligent des dégâts supplémentaires selon son mana supplémentaire. "
            "Flux envoûtant marque les cibles ; Court-circuit rebondit sur les ennemis marqués, Prison runique les immobilise, et Portail transdimensionnel transporte tes alliés vers un endroit proche."
        ),
        "laning": (
            "Enchaîne les compétences pour charger des runes : deux runes chargées donnent une brève vitesse de déplacement à Court-circuit. "
            "Marque avec Flux envoûtant avant d'utiliser tes autres compétences."
        ),
        "combos": [
            {"name": "Le combo de base", "keys": ["E", "Q", "W", "Q"], "when": "Un ennemi est à portée.",
             "how": "Flux envoûtant marque la cible et les ennemis proches, Court-circuit inflige des dégâts supplémentaires sur cible marquée et rebondit, Prison runique l'immobilise au lieu de la ralentir."},
            {"name": "La zone", "keys": ["E", "W", "Q"], "when": "Plusieurs ennemis sont groupés.",
             "how": "Flux marque les ennemis proches de la cible ; Court-circuit rebondit vers eux, et leurs dégâts profitent de la marque."},
            {"name": "Le portail d'équipe", "keys": ["R"], "when": "Tu veux repositionner ton équipe.",
             "how": "Portail transdimensionnel ouvre un portail vers un endroit proche : quelques secondes plus tard, tous les alliés près du portail y sont transportés."},
        ],
        "mistakes": [
            "Lancer Prison runique sans marque : l'immobilisation dépend de Flux.",
            "Négliger ton mana : tes dégâts en dépendent.",
            "Ouvrir le portail sans prévenir ton équipe.",
        ],
    }},
    "Garen": {"fr": {
        "playstyle": (
            "Garen est un combattant simple et robuste : il régénère un pourcentage de ses PV s'il n'a pas subi de dégâts récemment, et gagne de l'armure et de la résistance magique en tuant. "
            "Coup décisif le rend plus rapide et réduit au silence, Courage donne bouclier et ténacité, Jugement inflige des dégâts en zone, et Justice de Demacia tente d'exécuter un champion."
        ),
        "laning": (
            "Coup décisif purge les ralentissements et te donne de la vitesse : utilise-le pour ouvrir l'échange. "
            "Ta régénération ne se déclenche que sans dégâts : sors de portée pour te soigner."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Coup décisif te donne de la vitesse, ton attaque suivante inflige des dégâts supplémentaires et réduit au silence, Jugement tourbillonne autour de toi."},
            {"name": "La défense", "keys": ["W", "E"], "when": "Tu subis des dégâts importants.",
             "how": "Courage donne un bouclier et une grande ténacité pendant un bref instant, puis une réduction de dégâts moindre plus longtemps."},
            {"name": "L'exécution", "keys": ["Q", "E", "R"], "when": "Un champion est à basse vie.",
             "how": "Justice de Demacia tente d'exécuter un champion ennemi : lance-la quand ses PV sont bas."},
        ],
        "mistakes": [
            "Lancer l'ultime sur un ennemi en pleine santé.",
            "Rester en lane sans jamais te retirer : ta régénération demande un répit.",
            "Oublier Courage avant de tomber sous un contrôle.",
        ],
    }},
    "Leblanc": {"fr": {
        "playstyle": (
            "LeBlanc est une assassine de burst et de mobilité : Sceau de malveillance marque la cible et explose quand une compétence la blesse. "
            "Distorsion la fait foncer puis revenir, Chaînes éthérées immobilise après 1,5 seconde, et Imitation copie l'une de ses compétences de base."
        ),
        "laning": (
            "Marque avec Sceau de malveillance puis déclenche l'explosion avec une compétence pendant les 3,5 secondes. "
            "Si le sceau tue la cible, tu récupères le coût en mana et réduis le délai restant."
        ),
        "combos": [
            {"name": "Le burst", "keys": ["Q", "R", "W", "E"], "when": "Un ennemi est à portée.",
             "how": "Sceau de malveillance marque la cible, Imitation relance l'explosion en copiant ton sort, Distorsion fonce en blessant les ennemis proches, Chaînes éthérées immobilisent après 1,5 seconde."},
            {"name": "L'engagement et la sortie", "keys": ["W", "Q", "W"], "when": "Tu veux frapper puis fuir.",
             "how": "Distorsion te fait foncer ; dans les 4 secondes, réactive-la pour retourner à ton point de départ."},
            {"name": "La sécurité", "keys": ["E", "Q"], "when": "Un ennemi te poursuit.",
             "how": "Chaînes éthérées lancent une chaîne : si elle reste 1,5 seconde, l'ennemi est immobilisé. Ta passive te rend invisible sous 40 % de PV."},
        ],
        "mistakes": [
            "Lancer des compétences avant d'avoir marqué : le sceau doit exploser.",
            "Oublier que Distorsion peut se réactiver 4 secondes après.",
            "Utiliser l'ultime sur une compétence dont le délai de récupération est trop long.",
        ],
    }},
}
