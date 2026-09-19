"""Guides rédigés, lot 13. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Morgana": {"fr": {
        "playstyle": (
            "Morgana est une mage-support de contrôle : Entrave sombre immobilise, Tourment ténébreux blesse sur la durée avec des dégâts qui augmentent avec les PV manquants, Bouclier noir protège un allié des dégâts magiques et des entraves, et Chaînes spirituelles étourdit ceux qui ne les brisent pas. "
            "Sa passive la soigne quand elle blesse des champions, grands sbires et monstres."
        ),
        "laning": (
            "Entrave sombre est ton principal outil : chaque impact décide de l'échange. "
            "Garde Bouclier noir pour un allié menacé par un contrôle ou des dégâts magiques."
        ),
        "combos": [
            {"name": "Le pick", "keys": ["Q", "W", "AA"], "when": "Un ennemi est à portée d'entrave.",
             "how": "Entrave sombre immobilise et inflige des dégâts ; pose Tourment ténébreux sur lui : ses dégâts augmentent avec ses PV manquants."},
            {"name": "La protection", "keys": ["E", "W"], "when": "Un allié va subir un contrôle.",
             "how": "Bouclier noir absorbe les dégâts magiques et les entraves jusqu'à sa rupture : place-le avant l'engagement ennemi."},
            {"name": "L'ultime d'équipe", "keys": ["R", "W", "Q"], "when": "Les ennemis sont regroupés autour de toi.",
             "how": "Chaînes spirituelles ralentissent et blessent les champions ennemis proches ; après un délai, ceux qui n'ont pas brisé les chaînes sont étourdis."},
        ],
        "mistakes": [
            "Utiliser Bouclier noir sur un allié qui n'est pas la cible de contrôles.",
            "Lancer l'ultime sans être proche des ennemis.",
            "Rater Entrave sombre à cause d'un sbire.",
        ],
    }},
    "Brand": {"fr": {
        "playstyle": (
            "Brand est un mage de burst à flammes : ses compétences enflamment les cibles (cumul de 3), et au maximum les Flammes explosent après 2 secondes. "
            "Brûlure étourdit une cible en flammes, Colonne de flammes inflige 25 % de dégâts en plus aux cibles en flammes, Conflagration double sa portée de dispersion, et Pyrolyse rebondit jusqu'à 5 fois."
        ),
        "laning": (
            "Enflamme d'abord, puis étourdis avec Brûlure. "
            "Ta passive te rend du mana si tu tues un ennemi en flammes."
        ),
        "combos": [
            {"name": "L'étourdissement", "keys": ["E", "Q", "W"], "when": "Un ennemi est à portée.",
             "how": "Conflagration enflamme la cible, Brûlure l'étourdit puisqu'elle est en flammes, Colonne de flammes inflige 25 % de dégâts supplémentaires."},
            {"name": "Le burst complet", "keys": ["W", "E", "Q", "R"], "when": "Un carry est à portée.",
             "how": "Colonne de flammes puis Conflagration et Brûlure ; Pyrolyse rebondit en priorité sur les champions affectés qui n'ont pas atteint le maximum d'effets et les ralentit."},
            {"name": "L'explosion des flammes", "keys": ["Q", "E", "W", "R"], "when": "Un champion approche du cumul maximum.",
             "how": "Au maximum d'effets sur un champion, les Flammes deviennent instables et explosent après 2 secondes en infligeant d'énormes dégâts autour de la victime."},
        ],
        "mistakes": [
            "Lancer Brûlure sans cible en flammes : tu perds l'étourdissement.",
            "Oublier la portée doublée de Conflagration sur cible en flammes.",
            "Lancer l'ultime sans plusieurs cibles à faire rebondir.",
        ],
    }},
    "Mordekaiser": {"fr": {
        "playstyle": (
            "Mordekaiser est un combattant-mage qui joue avec son bouclier : Indestructible stocke une partie des dégâts infligés et subis sous forme de bouclier, consommable pour se soigner. "
            "Sa passive donne un halo de dégâts après 3 attaques ou compétences, Emprise funeste attire les ennemis, et Royaume des morts l'entraîne en duel avec sa victime en volant une partie de ses stats."
        ),
        "laning": (
            "Oblitération inflige plus de dégâts si un seul ennemi est touché : vise un champion seul. "
            "Enchaîne 3 attaques ou compétences pour déclencher le halo de ta passive."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "W", "Q"], "when": "Un ennemi est seul à portée.",
             "how": "Oblitération inflige plus de dégâts sur cible unique, Indestructible convertit les dégâts en bouclier, la troisième attaque ou compétence déclenche le halo."},
            {"name": "L'attraction", "keys": ["E", "Q", "W"], "when": "Plusieurs ennemis sont dispersés.",
             "how": "Emprise funeste attire tous les ennemis d'une zone vers toi ; enchaîne avec Oblitération."},
            {"name": "Le duel", "keys": ["R", "Q", "W", "AA"], "when": "Un carry est identifié.",
             "how": "Royaume des morts t'entraîne avec ta victime dans une autre dimension et lui vole une partie de ses stats ; si tu la tues, tu gardes ces stats jusqu'à sa réapparition."},
        ],
        "mistakes": [
            "Lancer l'ultime sur une cible qui peut te battre en duel.",
            "Utiliser Oblitération quand plusieurs ennemis sont touchés sans nécessité.",
            "Ne pas consommer ton bouclier pour te soigner.",
        ],
    }},
    "Warwick": {"fr": {
        "playstyle": (
            "Warwick est un jungler de chasse : ses attaques infligent des dégâts magiques supplémentaires, et sous 50 % de PV elles le soignent (triplé sous 25 %). "
            "Traque sanguinaire lui donne des vitesses contre les ennemis sous 50 % de PV, Dents de la bête mord selon les PV max, Hurlement bestial fait fuir, et Contrainte infinie neutralise un champion."
        ),
        "laning": (
            "Dents de la bête inflige des dégâts selon les PV max de la cible et te soigne. "
            "Traque sanguinaire te signale les ennemis sous 50 % de PV et te donne de la vitesse contre eux."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Dents de la bête te jette sur la cible en te soignant, tes attaques infligent des dégâts magiques supplémentaires, Hurlement bestial réduit les dégâts subis puis fait fuir."},
            {"name": "La capture", "keys": ["R", "Q", "AA"], "when": "Un carry est isolé.",
             "how": "Contrainte infinie bondit dans une direction (plus loin avec de la vitesse bonus) et neutralise le premier champion touché pendant 1,5 seconde."},
            {"name": "La chasse", "keys": ["W", "Q", "AA"], "when": "Un ennemi est sous 50 % de PV.",
             "how": "Traque sanguinaire te donne des bonus de vitesse de déplacement et d'attaque contre lui, triplés sous 25 %."},
        ],
        "mistakes": [
            "Oublier ta passive à bas PV : c'est ton soin.",
            "Lancer l'ultime sans avoir ajusté ta vitesse de déplacement bonus.",
            "Utiliser Hurlement bestial hors du besoin de fuite.",
        ],
    }},
    "Aurora": {"fr": {
        "playstyle": (
            "Aurora est une mage-assassine des royaumes spirituels : sa passive exorcise les esprits des ennemis blessés, qui la suivent et la soignent. "
            "Maléfice maudit et se relance pour attirer les maléfices, Derrière le voile la rend invisible, Sortilège ralentit avant un bond en arrière, et Entre les mondes crée une zone de téléportation."
        ),
        "laning": (
            "Maléfice : relance-le pour attirer les maléfices actifs et blesser au passage. "
            "Sortilège te fait bondir en arrière pour te mettre à l'abri."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "E", "Q"], "when": "Un ennemi est à portée.",
             "how": "Maléfice maudit la cible, Sortilège inflige des dégâts et ralentit puis te met à l'abri, relance Maléfice pour attirer les maléfices actifs."},
            {"name": "L'engagement", "keys": ["W", "Q", "E", "R"], "when": "Un carry est isolé.",
             "how": "Derrière le voile te fait bondir, te rend invisible et t'accélère ; Entre les mondes libère une onde de choc et crée une zone qui ralentit."},
            {"name": "La zone de téléportation", "keys": ["R", "R"], "when": "Tu veux te repositionner.",
             "how": "Entre les mondes crée une zone qui permet de te téléporter d'un bord à l'autre."},
        ],
        "mistakes": [
            "Oublier la relance de Maléfice.",
            "Utiliser Derrière le voile sans cible.",
            "Ignorer les esprits exorcisés : ils te soignent.",
        ],
    }},
    "Samira": {"fr": {
        "playstyle": (
            "Samira est une tireuse qui combine mêlée et distance : ses combos s'enchaînent avec des attaques ou compétences différentes de la précédente. "
            "Charge sauvage la rue à travers un ennemi et se réinitialise sur un kill, Tourbillon de lame détruit les projectiles ennemis, et Gâchette infernale tire une pluie de balles sur tous les ennemis autour d'elle."
        ),
        "laning": (
            "Enchaîne des actions différentes pour monter ton combo. "
            "En mêlée, tes attaques infligent des dégâts magiques supplémentaires."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["E", "Q", "AA", "W"], "when": "Un ennemi est à portée de ruée.",
             "how": "Charge sauvage te rue à travers un ennemi en tailladant et te donne de la vitesse d'attaque ; Panache lancé pendant la ruée frappe tous les ennemis sur ton chemin."},
            {"name": "L'ultime au corps à corps", "keys": ["E", "R", "AA"], "when": "Tu es entourée d'ennemis.",
             "how": "Gâchette infernale tire une pluie de balles sur tous les ennemis qui t'entourent."},
            {"name": "La défense", "keys": ["W", "AA"], "when": "Des projectiles ennemis arrivent.",
             "how": "Tourbillon de lame blesse les ennemis proches et détruit les projectiles ennemis."},
        ],
        "mistakes": [
            "Répéter la même action : tu perds ton combo.",
            "Lancer l'ultime sans être au contact des ennemis.",
            "Utiliser Charge sauvage sans cible à traverser.",
        ],
    }},
    "Akshan": {"fr": {
        "playstyle": (
            "Akshan est un tireur mobile : tous les trois coups, il inflige des dégâts supplémentaires et gagne un bouclier sur un champion. "
            "Vengerang lance un boomerang qui gagne de la portée à chaque touche, Cavalier seul le camoufle et ressuscite ses alliés en tuant une Crapule, et Envolée héroïque le balance depuis un terrain."
        ),
        "laning": (
            "Tes attaques sont doublées par une attaque supplémentaire moins forte : annule-la pour gagner de la vitesse de déplacement. "
            "Vengerang gagne de la portée à chaque ennemi touché."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "AA", "AA"], "when": "Un ennemi est à portée.",
             "how": "Vengerang inflige des dégâts à l'aller et au retour, sa portée augmente à chaque touche ; la troisième action déclenche les dégâts et le bouclier de ta passive."},
            {"name": "L'embuscade", "keys": ["W", "E", "AA"], "when": "Une Crapule est repérée.",
             "how": "Cavalier seul te camoufle et t'accélère vers les Crapules ; Envolée héroïque te balance et tire à répétition sur l'ennemi le plus proche."},
            {"name": "L'ultime de précision", "keys": ["R"], "when": "Un champion ennemi est visible.",
             "how": "Bien mérité ! se verrouille sur un champion, stocke des balles puis les tire toutes ; les dégâts dépendent des PV manquants du premier champion, sbire ou bâtiment touché."},
        ],
        "mistakes": [
            "Lancer l'ultime sans vérifier qui sera touché en premier.",
            "Rester visible loin des hautes herbes ou des éléments de terrain quand tu es camouflé.",
            "Oublier l'attaque supplémentaire annulable.",
        ],
    }},
    "Briar": {"fr": {
        "playstyle": (
            "Briar est une jungler frénétique : ses attaques et compétences infligent un saignement cumulable qui la soigne, et elle manque de régénération naturelle mais ses soins augmentent quand elle a peu de PV. "
            "À table ! étourdit et brise l'armure, Folie sanguinaire la fait poursuivre l'ennemi le plus proche, Cri sanglant la libère de la frénésie, et Vol mortel la fait voler vers sa proie."
        ),
        "laning": (
            "Ne compte pas sur ta régénération : fais des échanges qui te soignent grâce au saignement. "
            "À table ! étourdit et brise l'armure."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["Q", "AA", "W", "AA"], "when": "Un ennemi est à portée de bond.",
             "how": "À table ! bondit sur une unité, étourdit et brise l'armure ; Folie sanguinaire donne vitesses et dégâts de zone autour de la cible ; réactive-la pour un CROC."},
            {"name": "La sortie de frénésie", "keys": ["E", "Q", "AA"], "when": "Tu dois reprendre le contrôle.",
             "how": "Cri sanglant te libère de la Folie sanguinaire, réduit les dégâts subis en chargeant et te soigne ; un cri chargé repousse et étourdit contre un mur."},
            {"name": "L'ultime de proie", "keys": ["R", "W", "AA"], "when": "Un carry est visible sur la carte.",
             "how": "Vol mortel marque le premier champion touché comme ta proie et te fait voler jusqu'à lui en effrayant les ennemis proches ; tu gagnes armure, résistance magique, vol de vie et vitesse."},
        ],
        "mistakes": [
            "Rester en frénésie sans contrôle : tu poursuis l'ennemi le plus proche.",
            "Oublier la réactivation de Folie sanguinaire.",
            "Lancer l'ultime sur une proie qui peut fuir.",
        ],
    }},
    "Zac": {"fr": {
        "playstyle": (
            "Zac est un tank élastique : chaque compétence qui touche lui fait perdre un bout de lui-même qu'il absorbe pour se soigner, et à sa mort il se divise en 4 blobs qui tentent de se recombiner. "
            "Étirements attrape et cogne deux cibles, Matière instable blesse selon les PV max, Fronde le projette, et Boing ! rebondit quatre fois en projetant."
        ),
        "laning": (
            "Ramasse tes bouts pour te soigner. "
            "Étirements attrape un ennemi puis en attaque un autre pour les cogner l'un contre l'autre."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["E", "Q", "W", "R"], "when": "Un carry ennemi est à portée.",
             "how": "Fronde te projette vers l'avant, Étirements attrape, Matière instable inflige des dégâts selon les PV max, Boing ! projette et ralentit."},
            {"name": "L'échange", "keys": ["Q", "AA", "W"], "when": "Deux ennemis sont proches l'un de l'autre.",
             "how": "Étirements attrape un ennemi puis, si tu en attaques un autre, envoie les deux cibles l'une contre l'autre."},
            {"name": "La deuxième vie", "keys": ["W"], "when": "Tu subis des dégâts mortels.",
             "how": "Division cellulaire te divise en 4 blobs qui tentent de se recombiner ; s'il en reste, tu reviens à la vie. Cette compétence a un délai de 5 minutes."},
        ],
        "mistakes": [
            "Laisser les bouts sur le sol : ils sont ton soin.",
            "Oublier que la deuxième vie est disponible toutes les 5 minutes.",
            "Utiliser Fronde sans direction : c'est un déplacement.",
        ],
    }},
    "Kassadin": {"fr": {
        "playstyle": (
            "Kassadin est un assassin-mage qui subit moins de dégâts magiques et traverse les unités. "
            "Orbe du Néant interrompt les canalisations, Lame éthérée renforce ses attaques, Pulsation utilise l'énergie des sorts lancés près de lui, et Fissure le téléporte : chaque utilisation rapprochée augmente coût et dégâts."
        ),
        "laning": (
            "Garde Orbe du Néant pour interrompre une canalisation ou obtenir un bouclier contre la magie. "
            "Lame éthérée active rend du mana et inflige d'importants dégâts."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "W", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Orbe du Néant inflige des dégâts et te protège de la magie, Lame éthérée renforce ton attaque et rend du mana, Pulsation blesse et ralentit en cône après avoir absorbé assez d'énergie."},
            {"name": "L'engagement", "keys": ["R", "Q", "W", "AA", "R"], "when": "Un carry est éloigné.",
             "how": "Fissure te téléporte en blessant les ennemis proches ; chaque utilisation dans une courte période augmente le coût en mana et les dégâts de la suivante."},
            {"name": "L'anti-magie", "keys": ["Q", "E"], "when": "Un mage ennemi lance des compétences autour de toi.",
             "how": "Pulsation tire de l'énergie des sorts lancés près de toi ; ta passive réduit les dégâts magiques subis."},
        ],
        "mistakes": [
            "Enchaîner les Fissures sans mana.",
            "Utiliser Pulsation sans avoir assez d'énergie.",
            "Engager sans sortie : tes Fissures coûtent de plus en plus.",
        ],
    }},
    "Tryndamere": {"fr": {
        "playstyle": (
            "Tryndamere est un combattant de Fureur : chaque attaque, critique et coup de grâce lui en donne, ce qui augmente ses chances de critique. "
            "Soif de sang consomme la Fureur pour le soigner, Moquerie réduit les dégâts d'attaque des ennemis proches, Balafre le rue, et Rage inépuisable l'empêche de mourir pendant sa durée."
        ),
        "laning": (
            "Génère de la Fureur en attaquant, puis utilise Soif de sang pour te soigner. "
            "Moquerie réduit les dégâts d'attaque des champions proches et le déplacement de ceux qui te tournent le dos."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["E", "AA", "AA", "Q"], "when": "Un ennemi est à portée.",
             "how": "Balafre te rue et blesse les ennemis sur ton chemin, tes attaques génèrent de la Fureur, Soif de sang te soigne."},
            {"name": "La défense", "keys": ["W", "AA"], "when": "Tu affrontes des ennemis à haute attaque.",
             "how": "Moquerie réduit les dégâts d'attaque des champions proches ; ceux qui fuient sont ralentis."},
            {"name": "L'ultime de survie", "keys": ["R", "E", "AA", "Q"], "when": "Tu es à bas PV.",
             "how": "Rage inépuisable t'empêche de mourir, quelles que soient les blessures : continue le combat."},
        ],
        "mistakes": [
            "Lancer Rage inépuisable trop tôt : elle a une durée limitée.",
            "Consommer ta Fureur sans avoir d'attaques à faire.",
            "Oublier Moquerie contre des ennemis à haute attaque.",
        ],
    }},
}
