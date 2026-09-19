"""Guides rédigés, lot 4. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Alistar": {"fr": {
        "playstyle": (
            "Alistar est un tank d'engagement : Atomisation et Coup de tête projettent ou font tomber les ennemis, Piétinement ignore les collisions et prépare un étourdissement sur sa prochaine attaque, et son ultime dissipe les contrôles subis tout en réduisant les dégâts reçus. "
            "Sa passive charge un cri qui soigne toute l'équipe proche quand il étourdit ou déplace des ennemis."
        ),
        "laning": (
            "Étourdir ou déplacer des ennemis charge ton cri : chaque contrôle compte, même en lane. "
            "Piétinement se cumule quand il blesse un champion : au maximum, ta prochaine attaque étourdit."
        ),
        "combos": [
            {"name": "Le combo d'engagement", "keys": ["W", "Q"], "when": "Un ennemi est à portée de Coup de tête.",
             "how": "Coup de tête charge la cible et la fait tomber à la renverse, Atomisation projette dans les airs les ennemis proches : l'enchaînement place toute l'équipe ennemie sous contrôle."},
            {"name": "L'étourdissement par piétinement", "keys": ["E", "AA", "Q"], "when": "Un ennemi est au corps à corps.",
             "how": "Piétine plusieurs fois pour atteindre le maximum d'effets ; ta prochaine attaque contre un champion inflige des dégâts magiques supplémentaires et l'étourdit."},
            {"name": "L'ultime défensif", "keys": ["R", "W", "Q"], "when": "Tu es pris dans un contrôle de foule.",
             "how": "Volonté de fer dissipe tous les effets de contrôle qui t'affectent et réduit les dégâts subis : engage pendant sa durée sans crainte des contrôles."},
        ],
        "mistakes": [
            "Utiliser Atomisation et Coup de tête en même temps sans coordination.",
            "Oublier ton cri : soigne-toi et ton équipe en enchaînant les contrôles.",
            "Lancer l'ultime trop tôt : c'est ta meilleure protection contre un contrôle décisif.",
        ],
    }},
    "Nasus": {"fr": {
        "playstyle": (
            "Nasus est un combattant qui gagne en puissance grâce à Buveuse d'âmes : chaque cible tuée augmente les dégâts de ses prochaines frappes. "
            "Flétrissement ralentit fortement un champion en réduisant ses vitesses d'attaque et de déplacement, Esprit enflammé réduit l'armure, et Fureur des sables lui donne PV, portée et résistances."
        ),
        "laning": (
            "Prends les derniers coups avec Buveuse d'âmes : c'est ta principale source de puissance. "
            "Ta passive te donne un bonus de vol de vie contre ton adversaire, ce qui rend ta lane plus endurante."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["W", "E", "Q", "AA"], "when": "Un ennemi est à portée.",
             "how": "Flétrissement ralentit l'ennemi (vitesses d'attaque et de déplacement), Esprit enflammé réduit son armure, Buveuse d'âmes frappe pour infliger de gros dégâts."},
            {"name": "Le combat d'équipe", "keys": ["R", "W", "E", "Q"], "when": "Un combat d'équipe est engagé.",
             "how": "Fureur des sables te donne plus de PV, de portée d'attaque, d'armure et de résistance magique et réduit le délai de récupération de Buveuse d'âmes : lance-la avant d'entrer dans la mêlée."},
            {"name": "Le farm", "keys": ["Q", "AA"], "when": "Tu veux monter en puissance.",
             "how": "Buveuse d'âmes augmente la puissance des prochaines frappes si elle tue sa cible : prends chaque sbire avec elle."},
        ],
        "mistakes": [
            "Rater des derniers coups avec Buveuse d'âmes : c'est ton scaling.",
            "Oublier Flétrissement sur le carry ennemi.",
            "Entrer en combat sans ton ultime.",
        ],
    }},
    "Pantheon": {"fr": {
        "playstyle": (
            "Pantheon est un combattant-assassin agressif : après plusieurs compétences ou attaques, sa prochaine compétence est renforcée. "
            "Assaut martial étourdit, Égide impénétrable le rend invulnérable aux attaques auxquelles il fait face, et Météore lui permet de sauter à l'endroit choisi pour atterrir en zone."
        ),
        "laning": (
            "Fais monter ta passive avec des attaques et des compétences pour obtenir une compétence renforcée. "
            "Assaut martial étourdit : place-le pour un échange, mais garde Égide impénétrable pour bloquer une attaque importante."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["W", "AA", "Q", "AA"], "when": "Un ennemi est à portée.",
             "how": "Assaut martial te rue sur la cible en l'étourdissant, tes attaques accumulent ta passive, Lance astrale (coup ou lancé) profite de la version renforcée."},
            {"name": "Le blocage", "keys": ["E", "AA"], "when": "Un ennemi lance des attaques dans ta direction.",
             "how": "Égide impénétrable te rend invulnérable aux attaques auxquelles tu fais face, tout en donnant des coups de lance en succession rapide. Oriente le bouclier vers la source."},
            {"name": "L'ultime d'engagement", "keys": ["R", "W", "Q"], "when": "Tu veux surprendre ta cible.",
             "how": "Météore te fait sauter puis atterrir à l'endroit choisi ; enchaîne avec Assaut martial et Lance astrale à l'arrivée."},
        ],
        "mistakes": [
            "Utiliser Égide impénétrable sans cible qui attaque de face.",
            "Oublier la compétence renforcée de ta passive.",
            "Lancer Météore sans plan pour la suite : tu atterris au milieu des ennemis.",
        ],
    }},
    "Lucian": {"fr": {
        "playstyle": (
            "Lucian est un tireur mobile qui enchaîne compétences et attaques : chaque compétence transforme ta prochaine attaque en double-tir. "
            "Poursuite inlassable le fait foncer sur une courte distance (et Pistolero réduit son délai de récupération), Flamboiement marque et révèle brièvement les ennemis avec un bonus de vitesse de déplacement quand il les attaque, et son ultime tire un déluge de balles."
        ),
        "laning": (
            "Enchaîne toujours compétence puis attaque pour profiter du double-tir. "
            "Quand un allié te soigne ou te protège, ou qu'un ennemi est immobilisé, tes 2 prochaines attaques infligent des dégâts magiques supplémentaires."
        ),
        "combos": [
            {"name": "Le combo de base", "keys": ["Q", "AA", "E", "AA"], "when": "Un ennemi est à portée de Lumière perforante.",
             "how": "Lumière perforante transperce la cible, ton attaque devient un double-tir, Poursuite inlassable te repositionne (délai réduit par Pistolero) et relance l'attaque suivante."},
            {"name": "Le harcèlement de zone", "keys": ["W", "AA", "E", "AA"], "when": "Plusieurs ennemis sont proches.",
             "how": "Flamboiement explose en étoile, marque et révèle les ennemis ; attaque-les pour bénéficier de la vitesse de déplacement bonus."},
            {"name": "L'ultime", "keys": ["R"], "when": "Un ennemi est bloqué ou immobilisé.",
             "how": "Déluge de balles tire un déluge avec tes armes : tire-le sur un ennemi contrôlé par ton équipe pour tout toucher."},
        ],
        "mistakes": [
            "Attaquer sans compétence préalable : tu perds le double-tir.",
            "Utiliser Poursuite inlassable sans regarder ta position après.",
            "Gaspiller l'ultime sur une cible qui bouge sans contrôle.",
        ],
    }},
    "Karma": {"fr": {
        "playstyle": (
            "Karma est une mage-support dont l'ultime Mantra renforce sa prochaine compétence : chacune reçoit un bonus (cataclysme, lien renforcé qui la soigne, bouclier étendu aux alliés proches). "
            "Ses compétences de dégâts réduisent le délai de récupération de Mantra, ce qui te permet de l'utiliser souvent."
        ),
        "laning": (
            "Flamme intérieure harcèle et réduit le délai de Mantra en infligeant des dégâts. "
            "Volonté concentrée révèle l'ennemi, l'immobilise s'il ne brise pas le lien, puis inflige de nouveau des dégâts."
        ),
        "combos": [
            {"name": "Le harcèlement Mantra", "keys": ["R", "Q", "W"], "when": "Un ennemi est à portée.",
             "how": "Mantra renforce la prochaine compétence : Flamme intérieure crée en plus un cataclysme qui inflige des dégâts après un court délai."},
            {"name": "L'immobilisation", "keys": ["R", "W", "Q"], "when": "Un ennemi peut être bloqué.",
             "how": "Volonté concentrée renforcée soigne Karma et prolonge l'immobilisation : le lien immobilise l'ennemi s'il n'est pas brisé."},
            {"name": "La protection", "keys": ["R", "E"], "when": "Ton équipe engage.",
             "how": "Exaltation donne un bouclier et de la vitesse de déplacement à l'allié ; avec Mantra, l'énergie se diffuse et étend Exaltation aux champions alliés proches."},
        ],
        "mistakes": [
            "Utiliser Mantra sans savoir quelle compétence renforcer.",
            "Ne pas utiliser tes compétences pour réduire son délai de récupération.",
            "Lancer Volonté concentrée en te laissant briser le lien trop facilement.",
        ],
    }},
    "Chogath": {"fr": {
        "playstyle": (
            "Cho'Gath est un tank-mage qui grossit : il regagne des PV et du mana à chaque unité éliminée et Festin le fait grandir en augmentant ses PV max s'il tue sa cible. "
            "Rupture envoie les ennemis dans les airs, Cri sauvage réduit au silence dans un cône et Piques vorpales ralentissent."
        ),
        "laning": (
            "Prends les éliminations pour te soigner et regagner du mana. "
            "Rupture est ton principal outil de contrôle : place-la là où ton ennemi va."
        ),
        "combos": [
            {"name": "Le combo de contrôle", "keys": ["Q", "W", "AA"], "when": "Un ennemi est à portée de Rupture.",
             "how": "Rupture projette et ralentit, Cri sauvage réduit au silence dans le cône, tes attaques lancent des piques qui ralentissent."},
            {"name": "L'exécution", "keys": ["Q", "R"], "when": "Un ennemi est à basse vie.",
             "how": "Festin dévore une unité ennemie pour d'importants dégâts bruts ; si la cible est tuée, tu grandis et gagnes des PV max."},
            {"name": "La zone de contrôle", "keys": ["E", "AA", "Q"], "when": "Plusieurs ennemis sont devant toi.",
             "how": "Tes attaques avec Piques vorpales blessent et ralentissent tous les ennemis devant toi."},
        ],
        "mistakes": [
            "Utiliser Festin sans cible tuable : son bonus dépend de l'élimination.",
            "Manquer Rupture : c'est ton point d'entrée.",
            "Négliger le farm : ta puissance dépend des éliminations.",
        ],
    }},
    "Leona": {"fr": {
        "playstyle": (
            "Leona est un tank d'engagement : ses sorts marquent les ennemis d'un Rayon de soleil que tes alliés dissipent pour des dégâts magiques supplémentaires. "
            "Bouclier de l'aube étourdit sur ta prochaine attaque, Lame du zénith immobilise le dernier champion touché et te fait foncer sur lui, et Éruption solaire étourdit au centre et ralentit en bordure."
        ),
        "laning": (
            "Bouclier de l'aube a un court délai de récupération : utilise-le pour étourdir dès que tu peux attaquer. "
            "Marque les ennemis pour que ton équipe dissipe le Rayon de soleil."
        ),
        "combos": [
            {"name": "L'engagement de lane", "keys": ["E", "Q", "AA"], "when": "Un ennemi est à portée de Lame du zénith.",
             "how": "Lame du zénith touche tous les ennemis sur une ligne, immobilise le dernier champion touché et te fait foncer sur lui ; Bouclier de l'aube l'étourdit sur ton attaque."},
            {"name": "L'ultime d'équipe", "keys": ["E", "R", "Q"], "when": "Plusieurs ennemis se regroupent.",
             "how": "Éruption solaire étourdit ceux au centre et ralentit ceux en bordure : centre la zone sur les carries."},
            {"name": "La défense", "keys": ["W", "Q"], "when": "Tu es en position avancée.",
             "how": "Éclipse augmente armure et résistance magique et réduit les dégâts subis ; à la fin, elle blesse les ennemis proches et l'effet de protection est prolongé."},
        ],
        "mistakes": [
            "Engager sans allié pour profiter du Rayon de soleil.",
            "Lancer Éruption solaire de façon à ne toucher que la bordure.",
            "Utiliser Éclipse trop tôt : sa protection est courte.",
        ],
    }},
    "Jax": {"fr": {
        "playstyle": (
            "Jax est un combattant dont la vitesse d'attaque augmente avec les attaques successives. "
            "Frappe bondissante lui permet de bondir sur une unité, Contre-attaque esquive toutes les attaques puis étourdit les ennemis proches, et Maître d'armes ajoute des dégâts magiques toutes les trois attaques consécutives."
        ),
        "laning": (
            "Bondis sur des sbires ou des alliés pour te repositionner. "
            "Garde Contre-attaque pour esquiver une attaque importante et étourdir les ennemis proches."
        ),
        "combos": [
            {"name": "Le combo de base", "keys": ["Q", "W", "AA"], "when": "Un ennemi est à portée de bond.",
             "how": "Frappe bondissante frappe la cible, Élargissement charge ta prochaine attaque pour des dégâts supplémentaires, puis tes attaques consécutives augmentent ta vitesse d'attaque."},
            {"name": "L'esquive et l'étourdissement", "keys": ["E", "AA", "E"], "when": "Plusieurs ennemis attaquent ensemble.",
             "how": "Contre-attaque esquive toutes les attaques pendant un bref instant puis étourdit les ennemis proches : lance-la pendant leurs attaques, et réactive-la quand le moment est bon."},
            {"name": "Le combat d'équipe", "keys": ["R", "Q", "W", "AA"], "when": "Un combat d'équipe s'engage.",
             "how": "Maître d'armes inflige des dégâts magiques toutes les trois attaques et peut être activé pour des dégâts autour de toi et de la résistance supplémentaire."},
        ],
        "mistakes": [
            "Utiliser Contre-attaque sans attaque à esquiver.",
            "Bondir dans le vide sans cible ni sortie.",
            "Interrompre tes attaques successives : elles font monter ta vitesse d'attaque.",
        ],
    }},
    "Vladimir": {"fr": {
        "playstyle": (
            "Vladimir est un mage qui puise sa force dans les PV : il gagne 1 point de puissance tous les 30 PV bonus, et Transfusion vole les PV de l'ennemi ciblé. "
            "Bain de sang le rend impossible à cibler 2 secondes, Vagues de sang dépense ses PV pour des dégâts de zone, et Peste sanguine renforce les dégâts subis par les ennemis infectés avant de les blesser et de le soigner."
        ),
        "laning": (
            "Transfusion est ta principale source de dégâts et de soin. Quand ta jauge est pleine, ses dégâts et son soin augmentent beaucoup. "
            "Vagues de sang coûte des PV : ne l'utilise que si tu peux te soigner ensuite."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée de Transfusion.",
             "how": "Transfusion vole des PV, Vagues de sang inflige des dégâts de zone (peut être bloquée par les unités ennemies), tes attaques finissent."},
            {"name": "Le combo de combat d'équipe", "keys": ["R", "E", "Q", "W"], "when": "Plusieurs ennemis sont groupés.",
             "how": "Peste sanguine infecte la zone : les ennemis subissent plus de dégâts, puis subissent des dégâts magiques et te rendent des PV pour chaque champion touché. Bain de sang te rend intouchable 2 secondes."},
            {"name": "La sortie", "keys": ["W", "Q"], "when": "Tu es engagé par plusieurs ennemis.",
             "how": "Bain de sang te rend impossible à cibler et ralentit les ennemis dans la flaque ; tu peux aspirer leur vie."},
        ],
        "mistakes": [
            "Lancer Vagues de sang à bas PV : elle te coûte de la vie.",
            "Utiliser Bain de sang trop tôt : son délai est long.",
            "Lancer Peste sanguine sur des ennemis qui peuvent sortir facilement de la zone.",
        ],
    }},
    "JarvanIV": {"fr": {
        "playstyle": (
            "Jarvan IV est un combattant-tank d'engagement : sa première attaque inflige un pourcentage des PV actuels de la cible. "
            "Étendard demacien augmente sa vitesse d'attaque et celle des alliés proches, Frappe du dragon réduit l'armure et peut ramener Jarvan à son Étendard en projetant les ennemis, et Cataclysme crée une arène autour de lui."
        ),
        "laning": (
            "Ta première attaque sur un ennemi inflige un pourcentage de ses PV actuels : ouvre l'échange avec elle. "
            "Plante ton Étendard demacien pour préparer ta Frappe du dragon et un engagement."
        ),
        "combos": [
            {"name": "Le combo d'engagement", "keys": ["E", "Q", "AA"], "when": "Un ennemi est à portée de Frappe du dragon.",
             "how": "Étendard demacien plante un drapeau qui inflige des dégâts magiques ; Frappe du dragon te ramène à l'étendard en projetant dans les airs les ennemis sur le chemin, puis ta première attaque inflige les dégâts de passive."},
            {"name": "L'arène", "keys": ["R", "Q", "W", "AA"], "when": "Un carry est isolé.",
             "how": "Cataclysme te fait bondir sur une cible en transformant la zone en arène ; enchaîne avec Frappe du dragon et Égide dorée pour ralentir."},
            {"name": "La défense", "keys": ["W", "AA"], "when": "Tu es en plein combat.",
             "how": "Égide dorée implore les anciens rois pour te protéger et ralentir les ennemis proches."},
        ],
        "mistakes": [
            "Lancer Frappe du dragon sans l'Étendard : tu perds la projection dans les airs.",
            "Utiliser Cataclysme sans allié pour le suivre.",
            "Attaquer plusieurs fois la même cible : la passive ne s'active qu'une fois par période.",
        ],
    }},
}
