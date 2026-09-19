"""Guides rédigés, lot 1 (champions les plus joués). Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Yone": {"fr": {
        "playstyle": (
            "Yone est un combattant-assassin qui alterne coups physiques et magiques : une attaque sur deux inflige des dégâts magiques, ce qui rend ses dégâts difficiles à contrer avec un seul type de résistance. "
            "Il gagne ses parties en empilant Acier mortel pour projeter les ennemis dans les airs, puis en fermant le combat avec Destin scellé, qui rassemble les ennemis touchés. "
            "Libération spirituelle est la clé de son jeu : les dégâts infligés sous forme d'esprit sont répétés au retour dans le corps."
        ),
        "laning": (
            "Enchaîne attaques de base et Acier mortel pour empiler l'effet Tempête menaçante ; deux cumuls te permettent de te ruer et de projeter la cible. "
            "Fendoir spirituel te donne un bouclier proportionnel au nombre de champions touchés : garde-le pour un échange, pas pour les sbires."
        ),
        "combos": [
            {"name": "L'échange en lane", "keys": ["Q", "AA", "Q", "W"], "when": "Tu veux trader sans dépenser Libération spirituelle.",
             "how": "Deux Acier mortel rapprochés déclenchent la ruée et la projection ; glisse une attaque entre les deux pour profiter du bonus de sa passive, puis Fendoir spirituel pour le bouclier."},
            {"name": "L'engagement par l'esprit", "keys": ["E", "Q", "AA", "W", "E"], "when": "Un ennemi est à portée et tu veux maximiser les dégâts répétés.",
             "how": "Sors de ton corps avec Libération spirituelle, inflige un maximum de dégâts pendant que tu es en esprit, puis réactive-la : une partie de ces dégâts est répétée. Le combo tient sur sa durée limitée, donc lance-le à portée."},
            {"name": "Le combo de combat d'équipe", "keys": ["Q", "Q", "R", "Q", "W"], "when": "Plusieurs ennemis sont alignés.",
             "how": "Projette une cible avec la tornade, puis Destin scellé te téléporte derrière le dernier champion touché sur la ligne et attire tous les ennemis vers toi. Termine avec Acier mortel et Fendoir spirituel pour profiter du regroupement."},
        ],
        "mistakes": [
            "Utiliser Destin scellé sans avoir un allié qui suit : l'ultime te place au cœur de l'équipe adverse.",
            "Lancer Libération spirituelle sans cible à frapper : les dégâts répétés dépendent de ce que tu infliges pendant l'esprit.",
            "Gaspiller Fendoir spirituel sur des sbires : son bouclier grandit avec les champions touchés.",
        ],
    }},
    "LeeSin": {"fr": {
        "playstyle": (
            "Lee Sin est un jungler de mobilité et d'initiative. Il enchaîne des capacités à deux temps (Onde sonore / Coup résonant, Rempart / Force d'âme, Trombe / Fracture) pour poursuivre, protéger ou s'échapper. "
            "Sa passive accélère ses deux attaques après chaque compétence, ce qui récompense les enchaînements rapides. Son ultime projette la cible en arrière et blesse ceux qu'elle percute."
        ),
        "laning": (
            "Dans la jungle, garde de l'énergie : chaque capacité à deux temps en coûte. Utilise Trombe pour révéler les ennemis et Onde sonore pour engager. "
            "Rempart te permet de te ruer vers un allié, ce qui sert aussi bien à le protéger qu'à rejoindre un combat."
        ),
        "combos": [
            {"name": "Le pick classique", "keys": ["Q", "Q", "AA", "E", "AA"], "when": "Un ennemi est isolé à portée d'Onde sonore.",
             "how": "Onde sonore touche, Coup résonant te propulse dessus (dégâts selon ses PV manquants). Enchaîne avec les attaques rapides de ta passive et Trombe pour révéler et ralentir."},
            {"name": "L'engagement avec ultime", "keys": ["Q", "Q", "R"], "when": "Tu veux éjecter un carry de sa position.",
             "how": "Après Coup résonant, Rage du dragon envoie la cible en arrière : elle inflige des dégâts aux ennemis qu'elle percute et les projette en l'air un court instant. Vise une cible qui traverse leur ligne."},
            {"name": "La fuite ou le renfort", "keys": ["W", "W", "E"], "when": "Un allié est en danger ou tu dois te dégager.",
             "how": "Rempart te rue vers un allié (il est aussi protégé s'il est champion), puis Force d'âme t'apporte de l'omnivampirisme. Trombe et Fracture ralentissent les poursuivants."},
        ],
        "mistakes": [
            "Réactiver Coup résonant trop tard : tu as 3 secondes après l'impact d'Onde sonore.",
            "Lancer Onde sonore sans énergie de reste pour le second temps.",
            "Utiliser Rage du dragon sans regarder derrière la cible : les ennemis qu'elle percute sont blessés et projetés, donc vise une cible qui traverse leur ligne plutôt que la tienne.",
        ],
    }},
    "Jhin": {"fr": {
        "playstyle": (
            "Jhin est un tireur de précision à la cadence fixe : il tire quatre balles avant de recharger, et la quatrième inflige toujours un coup critique avec des dégâts supplémentaires. "
            "Il joue autour de l'immobilisation (Floraison mortelle) et des pièges-lotus pour verrouiller une cible, avant de la finir à très longue portée avec son ultime."
        ),
        "laning": (
            "Ta quatrième balle est la plus forte : vise-la sur un champion. Grenade dansante gagne en dégâts à chaque coup fatal, donc prends les derniers coups sur les sbires avec elle. "
            "Pose des pièges-lotus sur les passages, ils ralentissent et blessent quand un ennemi marche dessus."
        ),
        "combos": [
            {"name": "Le verrouillage de lane", "keys": ["E", "W", "Q", "AA"], "when": "Un ennemi est bloqué par ses sbires ou a déjà été touché.",
             "how": "Piège-lotus pour ralentir, puis Floraison mortelle : si la cible a été récemment blessée par toi ou un allié, elle est immobilisée. Grenade dansante et la quatrième balle terminent."},
            {"name": "Le combat d'équipe", "keys": ["W", "AA", "AA", "AA", "AA"], "when": "Ton équipe engage et tu es protégé.",
             "how": "Immobilise avec Floraison mortelle après un premier coup allié, puis enchaîne tes quatre balles : la dernière est un coup critique garanti. N'oublie pas la vitesse de déplacement gagnée sur chaque critique."},
            {"name": "La finition à distance", "keys": ["R", "R", "R", "R"], "when": "Un ennemi affaibli est dans ton axe de tir.",
             "how": "Rappel de rideau te permet quatre tirs à très longue portée qui s'arrêtent au premier champion touché et l'estropient. Le quatrième tir inflige toujours un coup critique : garde-le pour la finition."},
        ],
        "mistakes": [
            "Recharger au mauvais moment : le rechargement te laisse sans dégâts pendant un moment, surtout au contact.",
            "Lancer l'ultime sans repérer l'ennemi qui s'interpose : le tir s'arrête au premier champion touché.",
            "Poser les pièges-lotus au hasard : ils ne se déclenchent que quand un ennemi marche dessus, place-les sur ses trajets probables.",
        ],
    }},
    "Sylas": {"fr": {
        "playstyle": (
            "Sylas est un mage combattant qui gagne les échanges longs. Après chaque compétence, sa passive stocke une charge qui rend sa prochaine attaque plus rapide et plus dangereuse. "
            "Régicide le soigne contre les champions, et son ultime lui permet de voler la compétence ultime d'un ennemi : son potentiel dépend donc autant de ses cibles que de lui-même."
        ),
        "laning": (
            "Lance Croix du forçat sur la trajectoire de ton adversaire pour ralentir et faire exploser le croisement des chaînes. "
            "Garde Régicide pour un échange rentable, car il te soigne quand il touche un champion. Ta passive rend chaque enchaînement plus fort : évite de lancer une seule compétence isolée."
        ),
        "combos": [
            {"name": "Le combo de lane", "keys": ["Q", "AA", "W", "AA"], "when": "Tu veux un échange court et rentable.",
             "how": "Croix du forçat pour ralentir, une attaque avec la charge de passive, puis Régicide pour te soigner et infliger des dégâts."},
            {"name": "L'engagement par les chaînes", "keys": ["E", "E", "W", "Q", "AA"], "when": "La cible est trop loin pour Régicide.",
             "how": "Évasion te rue dans une direction, réactive pour lancer tes chaînes et te rapprocher de l'ennemi touché. Enchaîne avec Régicide et Croix du forçat."},
            {"name": "Le vol d'ultime", "keys": ["R"], "when": "Un ennemi vient d'utiliser une ultime utile ou que tu peux réutiliser.",
             "how": "Détournement te permet de lancer librement l'ultime d'un ennemi. Vise le bon moment : une ultime volée qui ne touche personne est un tour d'avance pour l'adversaire."},
        ],
        "mistakes": [
            "Voler une ultime sans savoir comment elle fonctionne : lis-la avant, car chaque ultime se joue différemment.",
            "Lancer Croix du forçat sans laisser le temps à l'intersection d'exploser : le second effet a un délai.",
            "Utiliser Régicide sans cible champion : le soin n'apparaît que contre des champions.",
        ],
    }},
    "Yunara": {"fr": {
        "playstyle": (
            "Yunara est une tireuse dont les coups critiques infligent des dégâts magiques bonus. Sa capacité Déchaînement spirituel lui donne de la vitesse d'attaque et fait rebondir ses attaques sur les ennemis proches, ce qui la rend forte dans les combats d'équipe. "
            "Sa Transe améliore ses compétences de base et remplace certaines par des versions plus dangereuses."
        ),
        "laning": (
            "Garde Célérité des kanmei pour te repositionner ou te dégager. Arc du jugement ralentit à distance : utilise-le pour poursuivre ou pour garder un ennemi à bonne portée. "
            "Attends ta Transe pour engager pleinement : ses versions améliorées changent la nature de ses compétences."
        ),
        "combos": [
            {"name": "Le combat d'équipe", "keys": ["R", "Q", "W", "AA"], "when": "Un combat d'équipe s'engage et tu es protégée.",
             "how": "Entre en Transe pour améliorer tes compétences, puis lance Déchaînement spirituel : vitesse d'attaque, dégâts bonus à l'impact et rebonds sur les ennemis proches. Ralentis avec le rayon de Transe."},
            {"name": "Le harcèlement", "keys": ["W", "AA", "AA"], "when": "Tu veux ralentir et frapper à distance.",
             "how": "Arc du jugement inflige des dégâts et ralentit ; enchaîne avec des attaques de base tant que l'ennemi reste à ta portée."},
            {"name": "La sortie de danger", "keys": ["E", "W"], "when": "Un ennemi te tombe dessus.",
             "how": "Célérité des kanmei te donne de la vitesse et te rend fantomatique ; en Transe, elle devient une ruée. Ralentis ensuite le poursuivant avec Arc du jugement."},
        ],
        "mistakes": [
            "Déclencher la Transe trop tôt : elle est ta principale fenêtre de puissance, avec un délai de récupération long.",
            "Utiliser Célérité des kanmei par réflexe plutôt que pour un positionnement précis.",
            "Rester à courte portée : ton avantage vient de la distance et du ralentissement.",
        ],
    }},
    "Kaisa": {"fr": {
        "playstyle": (
            "Kai'Sa est une tireuse-mage qui enchaîne les effets Plasma : chaque attaque applique des marques, et les immobilisations de ses alliés en ajoutent aussi. "
            "Ses objets améliorent ses compétences de base (Arme vivante), ce qui change son style de jeu selon son build. Son ultime la propulse sur un champion, idéal pour une exécution."
        ),
        "laning": (
            "Marque avec Rayon du Néant à longue portée pour empiler du Plasma, puis attaque pour finir les marques. Pluie d'Icathia inflige des dégâts en zone autour de toi : utilise-la à bout portant. "
            "Surpresseur t'aide à te repositionner ; améliorée, elle te donne une brève invisibilité."
        ),
        "combos": [
            {"name": "Le harcèlement en lane", "keys": ["W", "AA", "AA", "Q"], "when": "Un ennemi est à portée du Rayon.",
             "how": "Rayon du Néant marque avec ta passive, tes attaques de base complètent les marques, puis Pluie d'Icathia inflige ses dégâts sur les cibles proches."},
            {"name": "L'exécution", "keys": ["R", "Q", "AA", "AA"], "when": "Un carry est isolé ou affaibli.",
             "how": "Instinct meurtrier te propulse sur un champion ennemi ; enchaîne immédiatement avec Pluie d'Icathia et tes attaques. Assure-toi d'avoir une sortie avant de plonger."},
            {"name": "Le combat d'équipe", "keys": ["E", "AA", "AA", "W"], "when": "Ton équipe engage et tu es à distance.",
             "how": "Surpresseur augmente ta vitesse de déplacement puis d'attaque. Reste en périphérie et utilise Rayon du Néant pour marquer, tes alliés en immobilisant ajoutent du Plasma."},
        ],
        "mistakes": [
            "Utiliser l'ultime en entrée de combat sans sortie : elle te place au contact des ennemis.",
            "Négliger l'amélioration des compétences par tes objets : l'objet choisi change l'usage de chaque compétence.",
            "Lancer Surpresseur sans en tirer profit : c'est ton outil de repositionnement, pas de dégâts.",
        ],
    }},
    "Yasuo": {"fr": {
        "playstyle": (
            "Yasuo est un combattant de mêlée à mobilité constante. Sa passive lui donne des chances de coup critique accrues et un bouclier qui se remplit en se déplaçant. "
            "Il empile Tempête menaçante pour projeter les ennemis dans les airs, ce qui active son ultime, et Mur de vent bloque les projectiles ennemis, une capacité décisive contre les tireurs et les mages."
        ),
        "laning": (
            "Utilise Cercle tranchant sur les sbires pour te rapprocher de l'ennemi, et empile Tempête d'acier pour déclencher la tornade. "
            "Garde Mur de vent pour bloquer une compétence importante plutôt que pour la lancer par habitude : son délai de récupération est long."
        ),
        "combos": [
            {"name": "Le combo de tornade", "keys": ["E", "Q", "Q"], "when": "Un ennemi est à portée d'une ruée.",
             "how": "Cercle tranchant te rue à travers une cible, Tempête d'acier lancée pendant la ruée donne un coup circulaire ; deux cumuls de Tempête menaçante font ensuite une tornade qui projette la cible."},
            {"name": "L'ultime après projection", "keys": ["Q", "Q", "R"], "when": "Un ennemi est projeté dans les airs.",
             "how": "Dernier soupir ne peut viser qu'un champion déjà projeté : lance-le au moment où la tornade touche, et profite de la pénétration d'armure bonus sur tes coups critiques."},
            {"name": "La défense de tireurs", "keys": ["W"], "when": "Les tireurs adverses visent ton équipe.",
             "how": "Mur de vent bloque les projectiles ennemis pendant 4 secondes. Place-le entre ton équipe et leurs sources de dégâts à distance, avant qu'ils ne tirent."},
        ],
        "mistakes": [
            "Utiliser l'ultime sans avoir de cible projetée : il ne peut pas être lancé seul.",
            "Gaspiller Mur de vent hors des combats importants.",
            "Ruer sur des sbires qui te placent sous une tour ou dans la ligne de tirs ennemis.",
        ],
    }},
    "Ezreal": {"fr": {
        "playstyle": (
            "Ezreal est un tireur qui joue avec ses compétences plus qu'avec ses attaques. Chaque compétence qui touche lui donne de la vitesse d'attaque (jusqu'à 5 cumuls), et Tir mystique réduit ses délais de récupération quand il touche. "
            "Il harcèle à distance et se repositionne avec Transfert arcanique, sans jamais s'exposer."
        ),
        "laning": (
            "Tir mystique est ton outil principal : chaque impact réduit tes délais de récupération, donc vise des cibles réelles, champions ou sbires. "
            "Marque avec Flux essentiel pour préparer un échange : l'orbe explose si tu frappes la cible marquée."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["W", "Q", "AA"], "when": "Un ennemi est à portée de Flux essentiel.",
             "how": "Pose l'orbe sur la cible, frappe-la avec Tir mystique ou une attaque pour le faire exploser ; chaque impact réduit tes délais de récupération et ajoute de la vitesse d'attaque."},
            {"name": "L'esquive et la riposte", "keys": ["E", "Q", "W"], "when": "Un ennemi te tombe dessus.",
             "how": "Transfert arcanique te téléporte et tire sur l'ennemi le plus proche, en priorité celui marqué par Flux essentiel. Profite de la distance pour riposter avec tes autres compétences."},
            {"name": "L'ultime en combat", "keys": ["R"], "when": "Un combat d'équipe s'engage et plusieurs ennemis sont dans ton axe.",
             "how": "Arc térébrant traverse chaque unité sur sa ligne avec de gros dégâts (réduits contre les sbires et monstres non épiques). Lance-le en visant l'alignement des ennemis."},
        ],
        "mistakes": [
            "Lancer Transfert arcanique sans savoir où te placer : c'est ta sortie, pas ton engagement.",
            "Gaspiller Tir mystique dans le vide : chaque impact réduit tes délais de récupération.",
            "Oublier que l'ultime traverse toute la carte : vérifie les lignes avant de tirer.",
        ],
    }},
    "Nautilus": {"fr": {
        "playstyle": (
            "Nautilus est un tank de contrôle qui gagne ses parties en attrapant un ennemi : Abordage tire les deux protagonistes l'un vers l'autre, puis ses attaques immobilisent brièvement grâce à sa passive. "
            "Son ultime poursuit un ennemi choisi, le projette en l'air et l'étourdit, ce qui en fait l'un des meilleurs outils d'engagement du jeu."
        ),
        "laning": (
            "Lance Abordage à l'aveugle uniquement si la trajectoire est dégagée : il s'arrête au premier ennemi ou obstacle touché. "
            "Colère du titan te donne un bouclier et inflige des dégâts sur la durée avec tes attaques : place-la avant un échange."
        ),
        "combos": [
            {"name": "Le crochet de base", "keys": ["Q", "AA", "E"], "when": "Un ennemi est à portée du crochet.",
             "how": "Abordage tire les deux vers l'autre, ta première attaque inflige des dégâts bonus et immobilise brièvement. Répliques ralentit et blesse pour finir."},
            {"name": "L'engagement de combat d'équipe", "keys": ["R", "W", "E"], "when": "Le carry adverse est visible.",
             "how": "Grenade ASM poursuit un ennemi et le projette en l'air avec un étourdissement, ce qui permet à ton équipe de l'attaquer. Active Colère du titan pour tenir face aux dégâts ennemis."},
            {"name": "La protection d'un allié", "keys": ["Q", "W"], "when": "Un ennemi plonge sur ton carry.",
             "how": "Abordage attrape l'agresseur et le coupe de sa cible ; Colère du titan te protège et blesse ceux qui s'approchent."},
        ],
        "mistakes": [
            "Lancer Abordage sans trajectoire dégagée : un sbire peut l'arrêter.",
            "Utiliser l'ultime sur une cible non prioritaire : préviens ton équipe avant.",
            "Oublier le bouclier de Colère du titan avant un échange.",
        ],
    }},
    "Tristana": {"fr": {
        "playstyle": (
            "Tristana est une tireuse d'exécution : sa portée d'attaque augmente avec ses niveaux, et Saut roquette lui permet de plonger ou de fuir. "
            "Charge explosive place une bombe sur une cible ou explose à chaque élimination, ce qui lui permet d'enchaîner les kills en combat d'équipe. Son ultime repousse la cible et double le rayon de la charge."
        ),
        "laning": (
            "Ta portée augmente avec tes niveaux : joue tôt avec précaution, puis punis à distance dès que tu la dépasses. "
            "Garde Saut roquette pour t'échapper ou pour finir, car son délai de récupération est long."
        ),
        "combos": [
            {"name": "L'exécution", "keys": ["W", "E", "Q", "AA"], "when": "Un ennemi est isolé ou affaibli.",
             "how": "Saut roquette te rapproche et ralentit, Charge explosive pose une bombe sur la cible, Tir rapide augmente ta vitesse d'attaque pour finir."},
            {"name": "L'ultime défensif", "keys": ["R"], "when": "Un ennemi plonge sur toi.",
             "how": "Tir à impact inflige des dégâts magiques et repousse la cible ; si elle porte une Charge explosive, le rayon de déflagration est doublé, ce qui blesse aussi ses alliés proches."},
            {"name": "L'enchaînement de kills", "keys": ["E", "AA", "AA", "Q"], "when": "Un combat d'équipe est engagé.",
             "how": "Chaque élimination fait exploser tes projectiles autour de la victime : positionne-toi pour toucher plusieurs ennemis à la fois."},
        ],
        "mistakes": [
            "Plonger avec Saut roquette sans avoir de sortie : son délai de récupération est long.",
            "Utiliser l'ultime en attaque alors qu'il repousse la cible : il sert aussi de défense.",
            "Oublier que ta portée augmente avec les niveaux : ne joue pas comme au niveau 1.",
        ],
    }},
}
