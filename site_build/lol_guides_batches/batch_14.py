"""Guides rédigés, lot 14. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "KogMaw": {"fr": {
        "playstyle": (
            "Kog'Maw est un tireur de dégâts sur PV max : Barrage bio-arcanique augmente sa portée et lui fait infliger des dégâts magiques équivalents à un pourcentage des PV max de la cible. "
            "Bave caustique ronge l'armure et la résistance magique, Limon du Néant ralentit, et Artillerie vivante inflige des dégâts grandement augmentés contre les ennemis à faible PV. Sa passive le fait exploser 4 secondes après sa mort."
        ),
        "laning": (
            "Bave caustique te donne aussi de la vitesse d'attaque. "
            "Active Barrage bio-arcanique quand tu peux attaquer sans danger : il augmente ta portée."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "AA", "AA"], "when": "Un ennemi est à portée.",
             "how": "Bave caustique ronge l'armure et la résistance magique et te donne de la vitesse d'attaque ; Barrage bio-arcanique augmente ta portée et tes dégâts sur PV max."},
            {"name": "Le contrôle de zone", "keys": ["E", "R"], "when": "Un ennemi approche.",
             "how": "Limon du Néant blesse et laisse une traînée qui ralentit ; Artillerie vivante tire à longue portée avec des dégâts très augmentés sur les ennemis à faible PV."},
            {"name": "La mort explosive", "keys": ["R", "AA"], "when": "Tu es sur le point de mourir.",
             "how": "Surprise d'Icathia te fait exploser 4 secondes après ta mort en infligeant des dégâts bruts aux ennemis proches : continue de tirer."},
        ],
        "mistakes": [
            "Utiliser Artillerie vivante à répétition : le coût en mana augmente.",
            "Être à portée du contact sans plan de défense.",
            "Oublier ta portée accrue avec Barrage bio-arcanique.",
        ],
    }},
    "Smolder": {"fr": {
        "playstyle": (
            "Smolder est un tireur-mage draconique : toucher des champions avec une compétence et éliminer des ennemis avec Boule de feu draconique lui donne des effets de Dragon en herbe qui augmentent les dégâts de ses compétences de base. "
            "Atchoum ! explose sur les champions, Flap, flap, flap ! le fait voler en bombardant l'ennemi qui a le moins de PV, et MAMAAAN ! appelle sa mère pour un feu ralentissant."
        ),
        "laning": (
            "Prends les éliminations avec Boule de feu draconique : elles te font gagner des effets. "
            "Atchoum ! explose s'il touche des champions ennemis."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "AA"], "when": "Un ennemi est à portée.",
             "how": "Boule de feu draconique devient plus puissante au fil des effets cumulés ; Atchoum ! explose sur les champions touchés."},
            {"name": "Le vol de bombardement", "keys": ["E", "Q", "AA"], "when": "Tu veux passer les obstacles.",
             "how": "Flap, flap, flap ! te fait voler en ignorant les obstacles et bombarder l'ennemi qui a le moins de PV."},
            {"name": "L'ultime d'équipe", "keys": ["R", "W", "Q"], "when": "Un combat s'engage.",
             "how": "MAMAAAN ! fait cracher du feu depuis les airs : dégâts supplémentaires et ralentissement au centre du feu."},
        ],
        "mistakes": [
            "Négliger les éliminations : elles font grandir tes compétences.",
            "Utiliser Flap, flap, flap ! sans savoir qui sera bombardé.",
            "Lancer l'ultime sur des ennemis qui sortent de la zone.",
        ],
    }},
    "Elise": {"fr": {
        "playstyle": (
            "Elise est une jungler à deux formes : en forme humaine, ses compétences génèrent des araignées en sommeil et elle étourdit avec Cocon ; en forme arachnéenne, elle gagne vitesse de déplacement et de nouvelles compétences avec une horde d'araignées. "
            "Ses attaques en forme arachnéenne infligent des dégâts magiques supplémentaires et la soignent."
        ),
        "laning": (
            "En forme humaine, touche pour générer des araignées. "
            "Cocon étourdit la première unité touchée et la révèle si elle n'est pas furtive."
        ),
        "combos": [
            {"name": "Le combo d'engagement", "keys": ["E", "Q", "W", "R", "Q", "W", "E"], "when": "Un ennemi est à portée de Cocon.",
             "how": "Cocon étourdit, Neurotoxine (PV actuels) et Araignée explosive blessent, puis Forme arachnéenne te transforme : Morsure venimeuse (PV manquants), Frénésie symbiotique, Suspension."},
            {"name": "Le harcèlement en humaine", "keys": ["Q", "W", "E"], "when": "Tu veux harceler en forme humaine.",
             "how": "Neurotoxine inflige des dégâts selon les PV actuels ; chaque compétence qui touche génère une araignée en sommeil."},
            {"name": "Le plongeon", "keys": ["R", "E", "Q", "W"], "when": "Un carry est éloigné.",
             "how": "Suspension te suspend dans les airs avec tes araignées puis te fait tomber sur l'ennemi ciblé ; après la chute, les dégâts supplémentaires et soins de ta passive sont augmentés."},
        ],
        "mistakes": [
            "Te transformer sans avoir touché de compétence en humaine.",
            "Utiliser Cocon sans plan pour la forme arachnéenne.",
            "Oublier que ta portée d'attaque est réduite en araignée.",
        ],
    }},
    "Volibear": {"fr": {
        "playstyle": (
            "Volibear est un combattant dont les attaques et compétences augmentent sa vitesse d'attaque, avec des dégâts magiques bonus aux ennemis proches après un moment. "
            "Coup fulgurant étourdit, Folie mutilatrice marque et se relance pour soigner, Foudroiement ralentit et donne un bouclier, et Tempête incarnée le fait bondir en désactivant les tourelles proches."
        ),
        "laning": (
            "Coup fulgurant te donne de la vitesse vers les ennemis et étourdit le premier attaqué. "
            "Folie mutilatrice relancée sur la même cible inflige plus de dégâts et te soigne."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "W", "W", "E"], "when": "Un ennemi est à portée.",
             "how": "Coup fulgurant étourdit, Folie mutilatrice marque puis se relance pour dégâts et soin, Foudroiement ralentit et te donne un bouclier."},
            {"name": "Le plongeon de tourelle", "keys": ["R", "E", "Q"], "when": "Un ennemi est protégé par une tourelle.",
             "how": "Tempête incarnée te fait bondir en ralentissant et blessant les ennemis sous toi ; les tourelles ennemies proches sont désactivées temporairement."},
            {"name": "Le combat d'équipe", "keys": ["Q", "R", "W", "E"], "when": "Un combat s'engage.",
             "how": "Tes attaques cumulent la vitesse d'attaque et, après un moment, infligent des dégâts magiques supplémentaires aux ennemis proches."},
        ],
        "mistakes": [
            "Lancer Tempête incarnée sans profiter de la tourelle désactivée.",
            "Oublier de relancer Folie mutilatrice.",
            "Utiliser Foudroiement hors de portée pour le bouclier.",
        ],
    }},
    "Ziggs": {"fr": {
        "playstyle": (
            "Ziggs est un mage-tireur de siège : ses attaques infligent régulièrement des dégâts magiques supplémentaires, et ses compétences réduisent ce délai. "
            "Bombe rebondissante blesse, Charge explosive repousse (et détruit les tourelles vulnérables), Mines Hexplosives ralentissent, et Méga bombe infernale se lance de très loin."
        ),
        "laning": (
            "Enchaîne compétence puis attaque pour profiter de ta passive. "
            "Charge explosive te repousse sans dégâts : utilise-la pour te repositionner."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Bombe rebondissante inflige des dégâts, ton attaque profite du bonus de passive, Mines Hexplosives ralentissent."},
            {"name": "La sortie", "keys": ["W", "E"], "when": "Un ennemi te plonge.",
             "how": "Charge explosive repousse les ennemis et toi (sans dégâts pour toi) ; pose des mines derrière pour ralentir."},
            {"name": "L'ultime de siège", "keys": ["R", "Q", "W"], "when": "Les ennemis sont regroupés ou une tourelle est vulnérable.",
             "how": "Méga bombe infernale se lance de très loin : plus de dégâts dans la zone d'impact principale ; utilise Charge explosive pour détruire les tourelles vulnérables."},
        ],
        "mistakes": [
            "Lancer l'ultime sans viser la zone d'impact principale.",
            "Gaspiller Charge explosive sans plan.",
            "Poser des mines sans placement stratégique.",
        ],
    }},
    "AurelionSol": {"fr": {
        "playstyle": (
            "Aurelion Sol est un mage qui grandit en poussière d'étoile : ses compétences qui blessent des ennemis lui en donnent, ce qui améliore définitivement chacune de ses compétences. "
            "Souffle de lumière canalise, Vol astral le fait voler, Trou noir attire et exécute au centre, et Étoile finale peut devenir Apocalypse avec assez de poussière."
        ),
        "laning": (
            "Touche des champions avec Souffle de lumière pour collecter de la poussière d'étoile. "
            "Chaque seconde de canalisation sur un ennemi ajoute des dégâts."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "Q"], "when": "Un ennemi est à portée.",
             "how": "Souffle de lumière canalise et inflige des dégâts croissants ; Vol astral t'élève et Souffle de lumière n'a plus de délai ni de durée de canalisation maximale."},
            {"name": "La zone d'exécution", "keys": ["E", "R", "Q"], "when": "Plusieurs ennemis sont groupés.",
             "how": "Trou noir attire lentement les ennemis vers son centre, qui exécute ceux sous un certain pourcentage de PV max ; Étoile finale étourdit."},
            {"name": "L'Apocalypse", "keys": ["W", "R", "E"], "when": "Tu as assez de poussière d'étoile.",
             "how": "Collecter assez de poussière transforme la prochaine Étoile finale en Apocalypse : zone plus grande, dégâts accrus, projection en l'air et onde de choc."},
        ],
        "mistakes": [
            "Canaliser sans cible : Souffle de lumière n'ajoute des dégâts que sur un ennemi.",
            "Négliger la poussière d'étoile.",
            "Utiliser Vol astral sans préparer ta prochaine compétence.",
        ],
    }},
    "Singed": {"fr": {
        "playstyle": (
            "Singed est un tank-mage qui laisse une piste empoisonnée derrière lui et gagne de la vitesse en dépassant les champions. "
            "Attrape-mouche ralentit et rend inertes, Projection projette l'ennemi derrière lui (immobilisé s'il atterrit dans l'adhésif), et Potion de démence améliore ses statistiques et fait appliquer Hémorragie à sa piste."
        ),
        "laning": (
            "Ta piste empoisonnée inflige des dégâts aux ennemis qui la suivent. "
            "Projection sur une cible qui atterrit dans Attrape-mouche l'immobilise."
        ),
        "combos": [
            {"name": "La capture", "keys": ["W", "E"], "when": "Un ennemi est à portée de Projection.",
             "how": "Attrape-mouche ralentit et rend inertes les ennemis dans la zone ; Projection projette l'ennemi derrière toi : s'il atterrit dans l'adhésif, il est immobilisé."},
            {"name": "La poursuite", "keys": ["R", "Q", "AA"], "when": "Tu poursuis un carry.",
             "how": "Potion de démence améliore tes statistiques et ta piste applique Hémorragie."},
            {"name": "La fuite", "keys": ["Q", "W"], "when": "Un ennemi te poursuit.",
             "how": "Ta piste empoisonnée blesse ceux qui te suivent et Attrape-mouche les ralentit."},
        ],
        "mistakes": [
            "Poursuivre sans utiliser ta piste.",
            "Lancer Attrape-mouche sans trajectoire d'ennemi.",
            "Utiliser Potion de démence trop tôt : elle a une durée limitée.",
        ],
    }},
    "Rumble": {"fr": {
        "playstyle": (
            "Rumble est un combattant-mage à Vapeur : chaque compétence augmente sa Vapeur. À 50 % il entre dans la Zone rouge (effets bonus), à 100 % il surchauffe (vitesse d'attaque et dégâts bonus mais compétences impossibles pendant quelques secondes). "
            "Lance-flammes enflamme, Bouclier recyclé protège, Harpon électrique ralentit et réduit la résistance magique, et Éradication crée un mur de flammes."
        ),
        "laning": (
            "Garde ta Vapeur au niveau de la Zone rouge sans surchauffer. "
            "Tu peux porter 2 harpons en même temps."
        ),
        "combos": [
            {"name": "L'échange en Zone rouge", "keys": ["E", "Q", "AA", "W"], "when": "Tu as plus de 50 % de Vapeur.",
             "how": "Harpon électrique ralentit et réduit la résistance magique, Lance-flammes inflige plus de dégâts en Zone rouge, Bouclier recyclé te protège avec plus de PV."},
            {"name": "L'ultime de zone", "keys": ["R", "E", "Q"], "when": "Les ennemis sont dans un couloir.",
             "how": "Éradication tire une bordée de roquettes qui crée un mur de flammes blessant et ralentissant."},
            {"name": "La surchauffe", "keys": ["Q", "E", "W", "AA"], "when": "Tu veux finir en attaquant.",
             "how": "À 100 % de Vapeur, tu surchauffes : vitesse d'attaque et dégâts d'attaque bonus, mais aucune compétence pendant quelques secondes."},
        ],
        "mistakes": [
            "Surchauffer sans avoir placé tes compétences décisives.",
            "Ne pas utiliser les deux harpons.",
            "Rester à faible Vapeur : la Zone rouge renforce toutes tes compétences.",
        ],
    }},
    "Udyr": {"fr": {
        "playstyle": (
            "Udyr est un jungler à postures : quatre compétences qu'il peut activer pour changer de posture, et réactiver pour renouveler leurs effets et en ajouter d'autres. "
            "Après une compétence, ses deux prochaines attaques gagnent de la vitesse d'attaque. Griffe sauvage frappe, Cape de fer protège, Piétinement flamboyant étourdit, Tempête spirituelle ralentit."
        ),
        "laning": (
            "Choisis ta posture selon ce dont tu as besoin : dégâts, défense, mobilité ou zone. "
            "Réactiver une compétence renouvelle ses effets et en ajoute."
        ),
        "combos": [
            {"name": "La posture de dégâts", "keys": ["Q", "AA", "AA", "Q"], "when": "Tu veux maximiser tes dégâts.",
             "how": "Griffe sauvage donne de la vitesse d'attaque et des dégâts physiques sur tes deux attaques ; réactive-la pour que tes attaques fassent tomber la foudre."},
            {"name": "La posture de tank", "keys": ["W", "AA", "AA", "W"], "when": "Tu es engagé.",
             "how": "Cape de fer donne un bouclier et des soins sur tes deux attaques ; réactivée, un bouclier plus puissant et un soin selon tes PV max."},
            {"name": "L'engagement", "keys": ["E", "AA", "R"], "when": "Un ennemi est à portée.",
             "how": "Piétinement flamboyant t'accélère et étourdit la première attaque contre chaque cible ; Tempête spirituelle blesse et ralentit les ennemis proches."},
        ],
        "mistakes": [
            "Rester dans une posture unique alors que la situation change.",
            "Oublier les réactivations.",
            "Utiliser Piétinement flamboyant sans cible à étourdir.",
        ],
    }},
    "Kindred": {"fr": {
        "playstyle": (
            "Kindred est une tireuse-jungler qui chasse : Marque de Kindred marque des cibles, et chaque chasse fructueuse renforce définitivement ses compétences de base, avec plus de portée toutes les 4 chasses. "
            "Danse des flèches tire sur trois cibles, Frénésie de Loup attaque les ennemis proches, Terreur mortelle envoie Loup sur la cible, et Repos d'Agneau empêche quiconque de mourir dans la zone."
        ),
        "laning": (
            "Marque et chasse pour renforcer tes compétences définitivement. "
            "Agneau cumule des effets en se déplaçant et en attaquant : au maximum, sa prochaine attaque te soigne."
        ),
        "combos": [
            {"name": "La chasse", "keys": ["Q", "AA", "E", "AA"], "when": "Une cible marquée est à portée.",
             "how": "Danse des flèches te repositionne et tire sur jusqu'à trois cibles proches ; Terreur mortelle ralentit et, après deux attaques de plus, la troisième envoie Loup pour d'énormes dégâts."},
            {"name": "Le combat de zone", "keys": ["W", "AA", "Q"], "when": "Plusieurs ennemis sont proches.",
             "how": "Frénésie de Loup fait attaquer Loup autour de lui ; ton attaque, à effets maximaux, te soigne."},
            {"name": "La zone de vie", "keys": ["R"], "when": "Un combat décisif autour d'un objectif.",
             "how": "Repos d'Agneau offre un refuge contre la mort à toutes les créatures de la zone : nul ne peut y mourir jusqu'à la fin de l'effet, puis les unités sont soignées. Il protège aussi les ennemis."},
        ],
        "mistakes": [
            "Utiliser l'ultime sans réaliser qu'il protège aussi les ennemis.",
            "Négliger les chasses : elles renforcent tes compétences.",
            "Lancer Danse des flèches sans repositionnement voulu.",
        ],
    }},
    "Yorick": {"fr": {
        "playstyle": (
            "Yorick est un combattant qui invoque : sa passive lui permet de faire apparaître des Goules de Brume qui attaquent les ennemis proches, et ses Derniers sacrements créent une tombe sur un champion, un grand monstre ou une cible qui meurt. "
            "Sombre cortège crée un mur destructible, Brume endeuillée marque et ralentit, et Élégie des Îles invoque la Vierge de la Brume."
        ),
        "laning": (
            "Derniers sacrements inflige des dégâts supplémentaires et te soigne : prends des derniers coups avec. "
            "Utilise le mur pour isoler ta cible."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Derniers sacrements inflige des dégâts supplémentaires et te soigne, créant une tombe s'il touche un champion ; Brume endeuillée réduit l'armure, blesse, ralentit et marque."},
            {"name": "L'isolement", "keys": ["W", "E", "Q"], "when": "Un carry est proche de ses alliés.",
             "how": "Sombre cortège invoque un mur destructible qui bloque les déplacements des ennemis et sépare la cible."},
            {"name": "L'ultime de la Vierge", "keys": ["R", "E", "Q", "AA"], "when": "Un carry est identifié.",
             "how": "Élégie des Îles invoque la Vierge sur la cible : tes attaques contre elle infligent des dégâts supplémentaires ; la Vierge transforme les morts en Goules de Brume."},
        ],
        "mistakes": [
            "Ne pas utiliser les tombes créées par Derniers sacrements.",
            "Placer le mur sans plan.",
            "Lancer l'ultime sur la mauvaise cible : la Vierge suit sa cible.",
        ],
    }},
}
