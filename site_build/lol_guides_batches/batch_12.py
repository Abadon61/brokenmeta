"""Guides rédigés, lot 12. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Gwen": {"fr": {
        "playstyle": (
            "Gwen est une combattante dont les attaques infligent des dégâts magiques supplémentaires selon les PV de la cible, et qui se soigne d'une partie des dégâts infligés aux champions. "
            "Tchac, tchac ! coupe jusqu'à 6 fois, Brume sacrée la protège des ennemis hors de la zone, Élan incisif la fait se ruer avec des bonus, et Piqûre ralentit et se réactive deux fois."
        ),
        "laning": (
            "Tchac, tchac ! inflige des dégâts bruts au centre de la zone et applique ta passive à chaque coup : vise avec le centre. "
            "Brume sacrée te rend intouchable des ennemis hors de la brume."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["E", "AA", "Q", "AA"], "when": "Un ennemi est à portée.",
             "how": "Élan incisif te rue puis te donne vitesse d'attaque, portée et dégâts magiques ; Tchac, tchac ! applique ta passive à chaque coup de ciseaux."},
            {"name": "Le duel", "keys": ["W", "Q", "E", "R"], "when": "Tu affrontes un ennemi qui a des alliés à distance.",
             "how": "Brume sacrée te protège des ennemis hors de la zone : seuls ceux qui y entrent peuvent te cibler. Combats à l'intérieur."},
            {"name": "L'ultime en trois temps", "keys": ["R", "R", "R", "Q"], "when": "Un carry est isolé.",
             "how": "Piqûre ralentit, inflige des dégâts magiques et applique Mille coupures ; elle peut être activée deux fois de plus avec plus d'aiguilles et de dégâts."},
        ],
        "mistakes": [
            "Lancer Tchac, tchac ! en visant les bords : les dégâts bruts sont au centre.",
            "Utiliser Brume sacrée sans combattre à l'intérieur.",
            "Oublier les réactivations de l'ultime.",
        ],
    }},
    "Zyra": {"fr": {
        "playstyle": (
            "Zyra est une mage de zone qui combat avec des plantes : des graines apparaissent régulièrement, et lancer Épines funestes ou Racines fixatrices près d'elles les change en plantes qui combattent pour elle. "
            "Racines fixatrices immobilise, et Ronces étrangleuses projette en l'air et enrage les plantes."
        ),
        "laning": (
            "Plante des graines avec Croissance incontrôlée : elles durent jusqu'à 60 secondes et se stockent. "
            "Lance tes compétences près des graines pour faire pousser des plantes."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["W", "Q", "E"], "when": "Un ennemi est à portée d'une graine.",
             "how": "Plante une graine puis Épines funestes près d'elle : une Cracheuse de ronces pousse et tire de loin ; Racines fixatrices près d'une graine fait pousser une Plante flagellante qui ralentit."},
            {"name": "L'immobilisation", "keys": ["E", "Q", "R"], "when": "Un ennemi est isolé.",
             "how": "Racines fixatrices immobilise la cible ; Épines funestes inflige des dégâts en explosion, Ronces étrangleuses projette."},
            {"name": "Le combat d'équipe", "keys": ["W", "W", "R", "E"], "when": "Un combat s'engage à un endroit préparé.",
             "how": "Ronces étrangleuses blesse en s'étendant puis projette les ennemis ; les plantes dans les ronces deviennent enragées."},
        ],
        "mistakes": [
            "Lancer tes compétences loin de tes graines : tu perds les plantes.",
            "Oublier que les graines durent 60 secondes.",
            "Utiliser l'ultime sans plantes à enrager.",
        ],
    }},
    "Malzahar": {"fr": {
        "playstyle": (
            "Malzahar est un mage de contrôle : Appel du Néant réduit au silence, Visions maléfiques inflige des dégâts sur la durée et se propage à la mort, et Poigne du Néant neutralise un champion. "
            "Sa passive lui donne une énorme réduction des dégâts et l'insensibilité aux contrôles s'il ne subit rien pendant un temps."
        ),
        "laning": (
            "Profite de ta passive : ne subis pas de dégâts pour gagner l'insensibilité aux contrôles. "
            "Visions maléfiques est renouvelé par tes autres sorts sur la cible."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["E", "Q", "W"], "when": "Un ennemi est à portée.",
             "how": "Visions maléfiques inflige des dégâts sur la durée et attire les êtres du Néant, Appel du Néant réduit au silence, Nuée du Néant ajoute des attaques."},
            {"name": "La neutralisation", "keys": ["E", "Q", "R"], "when": "Un carry est isolé.",
             "how": "Poigne du Néant neutralise un champion dans une zone d'énergie négative infligeant des dégâts : prépare avec Visions maléfiques."},
            {"name": "La propagation", "keys": ["E", "Q", "W", "E"], "when": "Un ennemi affecté va mourir.",
             "how": "Si la cible meurt sous Visions maléfiques, les visions passent à une unité ennemie proche et tu regagnes du mana."},
        ],
        "mistakes": [
            "Subir des dégâts sans intérêt : tu perds la réduction de ta passive.",
            "Lancer Appel du Néant sans anticiper le délai des portails.",
            "Utiliser l'ultime sur une cible qui peut se dégager.",
        ],
    }},
    "Yuumi": {"fr": {
        "playstyle": (
            "Yuumi est une support qui s'attache à ses alliés : Félin pour l'autre ! la fait se ruer vers un allié, et dans cet état seules les tourelles peuvent la cibler. "
            "Tête chat-sseuse ralentit (davantage si le projectile vole au moins 1,35 seconde), Zouuu ! ne bénéficie qu'à l'allié quand elle est attachée, et Chat-pitre final soigne et blesse."
        ),
        "laning": (
            "Attache-toi à ton carry pour le protéger. "
            "Ta passive te soigne et soigne ton prochain allié quand tu frappes un champion."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "E"], "when": "Un ennemi est à portée du projectile.",
             "how": "Tête chat-sseuse ralentit et blesse (plus fort si le projectile a volé 1,35 s) ; attachée, tu peux le diriger avec le curseur ; Zouuu ! donne bouclier et vitesses à ton allié."},
            {"name": "La protection", "keys": ["W", "E", "R"], "when": "Ton carry est menacé.",
             "how": "Félin pour l'autre ! te met à l'abri sur ton allié, Zouuu ! le protège, et Chat-pitre final soigne tes alliés pendant sa canalisation."},
            {"name": "Le combat d'équipe", "keys": ["R", "W", "E"], "when": "Un combat s'engage.",
             "how": "Chat-pitre final canalise cinq vagues qui blessent les ennemis et soignent les alliés ; pendant, tu peux te déplacer, t'attacher et lancer Zouuu !."},
        ],
        "mistakes": [
            "Te détacher en zone dangereuse : tu es vulnérable hors attache.",
            "Lancer Tête chat-sseuse sans direction.",
            "Oublier de renforcer le lien avec ton meilleur ami.",
        ],
    }},
    "Velkoz": {"fr": {
        "playstyle": (
            "Vel'Koz est un mage-support de longue portée : ses compétences appliquent Décomposition organique, et à 3 effets l'ennemi subit une explosion de dégâts bruts. "
            "Fission du plasma se divise, Ouverture de faille explose après un délai, Dislocation tectonique projette, et son ultime suit le curseur en infligeant des dégâts bruts aux sujets d'étude."
        ),
        "laning": (
            "Applique trois effets pour déclencher l'explosion de dégâts bruts. "
            "Fission du plasma se divise en deux à l'impact ou à la réactivation."
        ),
        "combos": [
            {"name": "L'explosion de décomposition", "keys": ["Q", "W", "E"], "when": "Un ennemi est à portée.",
             "how": "Chaque compétence applique Décomposition organique : à 3 effets cumulés, l'ennemi subit une explosion de dégâts bruts."},
            {"name": "Le projectile divisé", "keys": ["Q", "Q", "W"], "when": "Un ennemi est de côté.",
             "how": "Fission du plasma se divise en deux à l'impact ou à la réactivation ; ralentit et blesse à l'impact."},
            {"name": "L'ultime de dégâts bruts", "keys": ["W", "E", "R"], "when": "Un carry est marqué.",
             "how": "Désintégrateur de formes de vie tire un rayon canalisé de 2,5 secondes qui suit le curseur ; les sujets d'étude subissent des dégâts bruts."},
        ],
        "mistakes": [
            "Lancer l'ultime sans sujet d'étude.",
            "Oublier la réactivation de Fission du plasma.",
            "Négliger la portée : reste loin.",
        ],
    }},
    "Corki": {"fr": {
        "playstyle": (
            "Corki est un tireur-mage à dégâts mixtes : ses attaques infligent des dégâts bruts bonus. "
            "Bombe au phosphore révèle, Valkyrie franchit une courte distance en lâchant des bombes, Gatling réduit armure et résistance magique, et Barrage de projectiles stocke des munitions dont un tir sur 3 est une grosse Bertha."
        ),
        "laning": (
            "Ta passive convertit une part de tes dégâts d'attaque en dégâts bruts. "
            "Gatling réduit l'armure et la résistance magique des ennemis touchés."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée.",
             "how": "Bombe au phosphore blesse et révèle la zone, Gatling tire dans un cône en réduisant armure et résistance magique."},
            {"name": "Le repositionnement", "keys": ["W", "R", "AA"], "when": "Tu veux frapper et te déplacer.",
             "how": "Valkyrie te fait franchir une courte distance en lâchant des bombes et une traînée de feu, puis Barrage de projectiles tire."},
            {"name": "L'ultime de siège", "keys": ["R", "R", "R"], "when": "Les ennemis sont à portée d'un barrage.",
             "how": "Barrage de projectiles tire des projectiles explosifs stockés ; un sur 3 est une grosse Bertha qui inflige plus de dégâts."},
        ],
        "mistakes": [
            "Gaspiller les projectiles de ton ultime.",
            "Utiliser Valkyrie sans regarder sa direction.",
            "Négliger Gatling : la réduction de résistance est importante.",
        ],
    }},
    "Sett": {"fr": {
        "playstyle": (
            "Sett est un combattant qui encaisse : sa passive fait alterner ses directs et augmente sa régénération selon ses PV manquants, et Coup cathartique convertit les dégâts subis en agressivité pour un bouclier et un coup de zone. "
            "Rogne inflige des dégâts selon les PV max, Casse-tête attire des deux côtés, et Le Clou du spectacle écrase un champion."
        ),
        "laning": (
            "Rogne renforce tes deux prochaines attaques selon les PV max de la cible. "
            "Ne gaspille pas Coup cathartique : plus tu as subi de dégâts, plus le bouclier est utile."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Rogne augmente ta vitesse vers les ennemis et tes deux attaques infligent des dégâts selon les PV max ; Casse-tête étourdit s'il y a des ennemis des deux côtés."},
            {"name": "La récupération", "keys": ["W", "AA"], "when": "Tu as subi beaucoup de dégâts.",
             "how": "Coup cathartique dépense toute l'agressivité stockée : bouclier et coup de poing à effet de zone, dégâts bruts au centre."},
            {"name": "L'ultime de clou", "keys": ["R", "E", "Q"], "when": "Un carry est à portée.",
             "how": "Le Clou du spectacle emporte un champion ennemi dans les airs avant de l'écraser, blessant et ralentissant tous les ennemis proches à l'atterrissage."},
        ],
        "mistakes": [
            "Utiliser Casse-tête avec des ennemis d'un seul côté : ils sont seulement ralentis.",
            "Lancer Coup cathartique sans agressivité stockée.",
            "Oublier que tu peux placer l'ultime pour écraser sur tes alliés adverses.",
        ],
    }},
    "Twitch": {"fr": {
        "playstyle": (
            "Twitch est un tireur-assassin de venin : ses attaques contaminent la cible et lui infligent des dégâts bruts chaque seconde. "
            "Embuscade le camoufle avec un bonus de vitesse, Dose de venin ralentit et applique le poison, Contamination l'aggrave, et Panique tire des carreaux qui transpercent tous les ennemis."
        ),
        "laning": (
            "Empoisonne ton adversaire avec des attaques puis utilise Contamination pour l'aggraver. "
            "Quand tu quittes ton camouflage, ta vitesse d'attaque augmente brièvement."
        ),
        "combos": [
            {"name": "L'embuscade", "keys": ["Q", "AA", "AA", "E"], "when": "Un carry est à portée.",
             "how": "Embuscade te camoufle et augmente ta vitesse ; en sortant, ta vitesse d'attaque augmente : frappe puis Contamination aggrave le poison."},
            {"name": "Le harcèlement", "keys": ["W", "AA", "AA"], "when": "Un ennemi est à portée.",
             "how": "Dose de venin explose en zone, ralentit et applique Venin mortel ; tes attaques renforcent le poison."},
            {"name": "L'ultime de ligne", "keys": ["R", "AA", "AA", "AA"], "when": "Les ennemis sont alignés.",
             "how": "Panique tire des carreaux à longue portée qui transpercent tous les ennemis touchés : aligne-les."},
        ],
        "mistakes": [
            "Utiliser Contamination sans poison.",
            "Lancer l'ultime sans aligner les ennemis.",
            "Sortir du camouflage sans cible : tu perds ta fenêtre.",
        ],
    }},
    "Zaahen": {"fr": {
        "playstyle": (
            "Zaahen est un combattant qui gagne en puissance à chaque coup : ses attaques et compétences donnent des effets de Détermination avec des dégâts d'attaque bonus, et au maximum il peut revenir à la vie. "
            "Glaive des Darkin taillade deux fois et se relance pour projeter, Retour redoutable attire, Incursion dorée le rue avec une taillade, et Libération inexorable le fait retomber en piqué."
        ),
        "laning": (
            "Touche des champions pour empiler la Détermination. "
            "Glaive des Darkin te soigne et se relance pour projeter la cible dans les airs."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "Q", "AA"], "when": "Un ennemi est à portée.",
             "how": "Glaive des Darkin taillade deux fois avec des dégâts bonus et un soin ; relance-le pour projeter la cible dans les airs."},
            {"name": "L'engagement", "keys": ["W", "E", "Q", "AA"], "when": "Un ennemi est éloigné.",
             "how": "Retour redoutable attire les ennemis vers toi, Incursion dorée te rue avec une taillade autour de toi."},
            {"name": "L'ultime", "keys": ["R", "Q", "E"], "when": "Un groupe est proche.",
             "how": "Libération inexorable te fait redescendre en piqué en blessant les ennemis et en te soignant d'une partie des dégâts infligés."},
        ],
        "mistakes": [
            "Utiliser l'ultime sans avoir empilé la Détermination.",
            "Lancer Retour redoutable dans le vide.",
            "Oublier la relance de Glaive des Darkin.",
        ],
    }},
    "Ornn": {"fr": {
        "playstyle": (
            "Ornn est un tank de forge : il augmente tous ses bonus d'armure et de résistance magique, et peut forger des objets non consommables n'importe où sur la carte avec de l'or. "
            "Fracture magmatique ralentit, Fournaise rend fragile, Ruée ardente projette contre un terrain, et Appel du dieu de la forge invoque un élémentaire qui charge vers lui."
        ),
        "laning": (
            "Fournaise : la dernière flamme rend les ennemis fragiles. "
            "Tu peux forger des objets sans retourner à la base."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "AA"], "when": "Un ennemi est à portée.",
             "how": "Fracture magmatique ralentit et forme une colonne de lave, Fournaise rend fragile les ennemis touchés par la dernière flamme."},
            {"name": "La projection", "keys": ["E", "Q", "W"], "when": "Un ennemi est près d'un mur.",
             "how": "Ruée ardente blesse ceux que tu traverses et crée une onde de choc qui projette si tu percutes un terrain."},
            {"name": "L'ultime en deux temps", "keys": ["R", "E", "R"], "when": "Plusieurs ennemis sont groupés.",
             "how": "Appel du dieu de la forge invoque un élémentaire qui charge vers toi ; relance l'ultime pour te ruer sur lui et le rediriger, projetant en l'air les ennemis touchés."},
        ],
        "mistakes": [
            "Oublier que tu peux forger des objets.",
            "Utiliser la relance de l'ultime sans direction claire.",
            "Lancer Ruée ardente sans mur.",
        ],
    }},
}
