"""Guides rédigés, lot 10. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Poppy": {"fr": {
        "playstyle": (
            "Poppy est une tank anti-mobilité : Présence immuable arrête les ruées ennemies autour d'elle (l'ennemi est ralenti et inerte), Charge héroïque repousse et étourdit contre un mur, et Verdict de la gardienne projette les ennemis très loin. "
            "Sa passive lance son écu, qu'elle ramasse pour un bouclier temporaire."
        ),
        "laning": (
            "Ramasse ton écu après ta passive pour obtenir un bouclier temporaire. "
            "Commotion crée une zone qui ralentit puis explose après un délai."
        ),
        "combos": [
            {"name": "L'étourdissement au mur", "keys": ["E", "Q", "AA"], "when": "Un ennemi est près d'un mur.",
             "how": "Charge héroïque repousse la cible ; contre un mur elle est étourdie. Commotion ralentit puis explose."},
            {"name": "L'anti-plongée", "keys": ["W", "R"], "when": "Un ennemi effectue une ruée vers ton carry.",
             "how": "Présence immuable arrête les ruées autour de toi : l'ennemi est ralenti et inerte. Verdict de la gardienne projette ensuite l'ennemi très loin."},
            {"name": "Le harcèlement", "keys": ["Q", "AA", "AA"], "when": "Un ennemi est en lane.",
             "how": "Commotion inflige des dégâts et crée une zone qui explose ; ton attaque lance ensuite l'écu."},
        ],
        "mistakes": [
            "Ne pas ramasser ton écu.",
            "Utiliser Présence immuable sans ruée à arrêter.",
            "Lancer Charge héroïque loin d'un mur alors que tu peux attendre.",
        ],
    }},
    "Karthus": {"fr": {
        "playstyle": (
            "Karthus est un mage de zone qui continue de lancer des sorts en mourant : sa passive lui donne une forme spirituelle. "
            "Dévastation explose après un délai (plus fort sur cible isolée), Mur de douleur réduit vitesse et résistance magique, Souillure lui rend du mana aux éliminations, et Requiem inflige des dégâts à tous les champions ennemis après 3 secondes."
        ),
        "laning": (
            "Dévastation n'a pas de délai de récupération : lance-la sans arrêt sur les sbires et les ennemis. "
            "Souillure te rend du mana à chaque élimination."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "Q", "W"], "when": "Un ennemi est isolé.",
             "how": "Dévastation explose à retardement avec plus de dégâts sur cible isolée ; Mur de douleur réduit la vitesse et la résistance magique de ceux qui le franchissent."},
            {"name": "L'ultime à distance", "keys": ["R"], "when": "Des ennemis sont affaiblis partout.",
             "how": "Requiem canalise 3 secondes puis inflige des dégâts à tous les champions ennemis : utilise-le pour finir plusieurs cibles à distance."},
            {"name": "La forme spirituelle", "keys": ["Q", "W", "R"], "when": "Tu meurs en plein combat.",
             "how": "Déni de mort te donne une forme spirituelle qui te permet de continuer à lancer des sorts : profites-en pour lancer Requiem ou Dévastation."},
        ],
        "mistakes": [
            "Lancer Requiem sans que les ennemis soient à portée de tuer.",
            "Utiliser Souillure hors de tes besoins : elle coûte beaucoup de mana.",
            "Oublier ta forme spirituelle.",
        ],
    }},
    "Gnar": {"fr": {
        "playstyle": (
            "Gnar est un combattant qui alterne entre petit et Méga Gnar : sa Rage se remplit en combattant, et quand elle est pleine, sa prochaine compétence le transforme en Méga Gnar avec de meilleures défenses et de nouvelles compétences. "
            "Petit, il lance un boomerang et rebondit ; en Méga, il lance des rochers, étourdit avec Beigne et projette tous les ennemis avec GNAR !."
        ),
        "laning": (
            "Rattrape ton boomerang pour réduire son délai. "
            "Agitation te donne dégâts et vitesse en attaquant et en lançant des compétences."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "AA", "W", "E"], "when": "Un ennemi est à portée du boomerang.",
             "how": "Jet de boomerang blesse et ralentit ; rattrape-le pour réduire son délai ; Agitation ajoute dégâts et vitesse ; Rebond te repositionne."},
            {"name": "La transformation", "keys": ["W", "E", "Q", "R"], "when": "Ta jauge de Rage est pleine.",
             "how": "Ta prochaine compétence te transforme en Méga Gnar : Beigne étourdit, Aplatissement inflige des dégâts de zone."},
            {"name": "L'engagement d'équipe", "keys": ["R"], "when": "Les ennemis sont près d'un mur.",
             "how": "GNAR ! projette tous les ennemis proches dans la direction ciblée avec dégâts et ralentissement ; s'ils percutent un mur, ils sont étourdis et subissent des dégâts supplémentaires."},
        ],
        "mistakes": [
            "Utiliser GNAR ! sans mur ni alliés derrière.",
            "Oublier de rattraper le boomerang ou le rocher.",
            "Se transformer au mauvais moment : la Rage se dépense.",
        ],
    }},
    "Taliyah": {"fr": {
        "playstyle": (
            "Taliyah est une mage de terrain : sa passive augmente sa vitesse près des murs, et Rafale filée crée un sol ouvragé qu'elle consomme pour lancer un rocher plus puissant qui ralentit. "
            "Poussée sismique projette les ennemis, Défilage tellurique piège avec des mines qui étourdissent, et Mur de la tisseuse crée un très long mur sur lequel elle surfe."
        ),
        "laning": (
            "Lance Rafale filée en te déplaçant librement : le sol ouvragé donne une version renforcée. "
            "Utilise Défilage tellurique pour piéger les ruées."
        ),
        "combos": [
            {"name": "Le combo de rocher", "keys": ["Q", "Q", "W", "E"], "when": "Un ennemi est à portée.",
             "how": "Rafale filée crée un sol ouvragé, la seconde le consomme pour un rocher qui ralentit ; Poussée sismique projette la cible vers tes mines."},
            {"name": "Le piège", "keys": ["E", "W"], "when": "Un ennemi pourrait faire une ruée.",
             "how": "Défilage tellurique crée un champ de mines ralentissant ; si un ennemi effectue une ruée ou est projeté par-dessus, elles explosent et l'étourdissent."},
            {"name": "L'ultime de mur", "keys": ["R", "Q"], "when": "Tu veux bloquer un passage ou te déplacer vite.",
             "how": "Mur de la tisseuse crée un très long mur et te fait surfer dessus."},
        ],
        "mistakes": [
            "Lancer Poussée sismique sans direction utile.",
            "Utiliser l'ultime sans savoir qui il bloque ou piège.",
            "Négliger les murs : ils augmentent ta vitesse.",
        ],
    }},
    "Vayne": {"fr": {
        "playstyle": (
            "Vayne est une tireuse-assassin : sa troisième attaque ou compétence consécutive sur la même cible inflige un pourcentage des PV max en dégâts bruts. "
            "Roulade la fait se repositionner avec des dégâts bonus, Condamnation projette et empale contre le décor, et Combat ultime augmente ses dégâts et la rend invisible pendant Roulade."
        ),
        "laning": (
            "Roulade entre tes attaques pour te repositionner et infliger des dégâts. "
            "Attaque la même cible pour déclencher Carreaux d'argent à la troisième."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["AA", "Q", "AA", "AA"], "when": "Un ennemi est à portée.",
             "how": "Roulade te repositionne avec des dégâts bonus, la troisième attaque consécutive déclenche Carreaux d'argent avec des dégâts bruts selon les PV max."},
            {"name": "L'empalement", "keys": ["E", "AA"], "when": "Un ennemi est près d'un mur.",
             "how": "Condamnation tire un carreau gigantesque qui projette la cible en arrière ; si elle percute le décor, elle est empalée, subit des dégâts supplémentaires et est étourdie."},
            {"name": "Le combat ultime", "keys": ["R", "Q", "AA", "AA"], "when": "Un combat d'équipe s'engage.",
             "how": "Combat ultime augmente tes dégâts d'attaque, te rend invisible pendant Roulade et réduit son délai de récupération."},
        ],
        "mistakes": [
            "Changer de cible : tu perds la progression des Carreaux d'argent.",
            "Utiliser Condamnation sans mur derrière la cible alors qu'il y en a un.",
            "Rouler en direction des ennemis sans plan.",
        ],
    }},
    "Quinn": {"fr": {
        "playstyle": (
            "Quinn est une tireuse-assassin qui combat avec Valor, son aigle : Busard marque périodiquement des ennemis, et sa première attaque sur cible marquée inflige des dégâts bonus. "
            "Assaut aveuglant limite la vision, Salto la projette en arrière après un impact, et En territoire ennemi la fait voler à grande vitesse avec Valor."
        ),
        "laning": (
            "Attaque la cible marquée par Busard en premier : ta première attaque inflige des dégâts bonus. "
            "Œil d'aigle te donne des vitesses d'attaque et de déplacement après avoir attaqué une cible marquée."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "E"], "when": "Un ennemi est marqué par Busard.",
             "how": "Assaut aveuglant marque et limite la vision avant de blesser les ennemis proches ; ton attaque sur cible marquée inflige des dégâts bonus ; Salto blesse, ralentit et te renvoie en arrière."},
            {"name": "La reconnaissance", "keys": ["W"], "when": "Tu veux de la vision.",
             "how": "Activer Œil d'aigle fait révéler une grande zone par Valor."},
            {"name": "L'ultime de mobilité", "keys": ["R", "Q", "AA"], "when": "Tu veux traverser la carte.",
             "how": "En territoire ennemi vous fait voler à grande vitesse, Valor et toi ; mettre fin à la compétence lance Volée fatale qui blesse les ennemis proches et marque les champions avec Busard."},
        ],
        "mistakes": [
            "Oublier la marque de Busard.",
            "Utiliser Salto sans avoir prévu ta position d'arrivée.",
            "Lancer l'ultime en te plaçant au milieu des ennemis.",
        ],
    }},
    "DrMundo": {"fr": {
        "playstyle": (
            "Dr. Mundo est un tank qui résiste au premier effet immobilisant, au prix de PV et d'une bonbonne qu'il ramasse pour se soigner. "
            "Scie souillée blesse selon les PV actuels, Défibrillateur stocke des dégâts et les rend en soins, Contusion inflige des dégâts selon ses PV manquants, et Dosage maximal le soigne instantanément."
        ),
        "laning": (
            "Scie souillée inflige des dégâts selon les PV actuels de la cible : utilise-la souvent pour harceler. "
            "Ta régénération de PV est très élevée : joue avec."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Scie souillée ralentit et inflige des dégâts selon les PV actuels ; Contusion frappe avec des dégâts supplémentaires selon tes PV manquants."},
            {"name": "Le combat prolongé", "keys": ["W", "AA", "Q"], "when": "Tu es entouré d'ennemis.",
             "how": "Défibrillateur inflige des dégâts continus et stocke une partie des dégâts subis, puis les rend en soins à la fin ou à la réactivation."},
            {"name": "L'ultime de survie", "keys": ["R", "E"], "when": "Tu es à bas PV.",
             "how": "Dosage maximal récupère instantanément un pourcentage de tes PV manquants, te donne de la vitesse et régénère sur une longue durée."},
        ],
        "mistakes": [
            "Ne pas ramasser la bonbonne de ta passive.",
            "Utiliser Dosage maximal à pleine santé.",
            "Oublier que le premier effet immobilisant te coûte des PV.",
        ],
    }},
    "Xayah": {"fr": {
        "playstyle": (
            "Xayah est une tireuse de plumes : ses compétences laissent des plumes, et Appel des lames les rappelle pour infliger des dégâts et immobiliser. "
            "Après une compétence, ses prochaines attaques frappent toutes les cibles sur leur passage et laissent une plume. Rafale de plumes la rend impossible à cibler."
        ),
        "laning": (
            "Enchaîne compétence puis attaque pour que tes attaques frappent tout sur leur passage. "
            "Place des plumes sur les ennemis pour ton immobilisation."
        ),
        "combos": [
            {"name": "L'immobilisation", "keys": ["Q", "AA", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Dagues jumelles laissent des plumes, tes attaques en laissent aussi, Appel des lames rappelle toutes les plumes pour blesser et immobiliser."},
            {"name": "Le combat d'équipe", "keys": ["W", "AA", "AA"], "when": "Un combat s'engage.",
             "how": "Plumage mortel augmente ta vitesse d'attaque et tes dégâts, et ta vitesse de déplacement si tu attaques un champion."},
            {"name": "L'ultime", "keys": ["R", "E"], "when": "Tu es menacée.",
             "how": "Rafale de plumes te fait bondir dans les airs, impossible à cibler, en lançant des dagues qui laissent des plumes ; rappelle-les ensuite."},
        ],
        "mistakes": [
            "Rappeler tes plumes sans ennemis à immobiliser.",
            "Utiliser l'ultime sans vérifier où retomber.",
            "Négliger la portée de tes attaques : elles frappent tout sur leur passage.",
        ],
    }},
    "Draven": {"fr": {
        "playstyle": (
            "Draven est un tireur qui vit de son style : rattraper la Hache tournoyante, tuer des sbires ou détruire des tourelles lui donne de l'Adoration, qui se convertit en or supplémentaire quand il tue un champion. "
            "Pulsion sanguinaire augmente ses vitesses, Division repousse et ralentit, et Volée mortelle exécute les ennemis dont les PV sont inférieurs à son Adoration."
        ),
        "laning": (
            "Rattrape tes haches : c'est ta source d'Adoration et de dégâts. "
            "Tu peux avoir deux Haches tournoyantes en même temps."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "AA", "W"], "when": "Un ennemi est à portée.",
             "how": "Hache tournoyante inflige des dégâts supplémentaires et ricoche ; rattrape-la pour en préparer une autre ; Pulsion sanguinaire termine son délai en attrapant."},
            {"name": "La séparation", "keys": ["E", "Q", "AA"], "when": "Un ennemi te plonge.",
             "how": "Division repousse sur le côté les cibles touchées et les ralentit."},
            {"name": "L'exécution", "keys": ["R", "R"], "when": "Un ennemi est à bas PV.",
             "how": "Volée mortelle exécute les ennemis dont les PV sont inférieurs à ton Adoration cumulée ; réactive-la pour faire revenir les haches plus tôt."},
        ],
        "mistakes": [
            "Rater une hache : tu perds Adoration et dégâts.",
            "Utiliser l'ultime sans réactivation quand elle est utile.",
            "Négliger l'Adoration : elle décide de l'exécution.",
        ],
    }},
    "Teemo": {"fr": {
        "playstyle": (
            "Teemo est un tireur-mage de harcèlement : sa passive le rend invisible indéfiniment s'il reste immobile, et dans les hautes herbes il peut se déplacer en restant invisible. "
            "Fléchette aveuglante aveugle, Vélocité l'accélère, Tir toxique empoisonne pendant 4 secondes, et Piège nocif pose des champignons qui ralentissent et blessent."
        ),
        "laning": (
            "Aveugle avec Fléchette aveuglante pour empêcher ton adversaire de t'attaquer. "
            "Quand tu quittes l'invisibilité, ton Effet de surprise augmente ta vitesse d'attaque."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "AA", "AA"], "when": "Un ennemi est à portée.",
             "how": "Fléchette aveuglante inflige des dégâts et aveugle ; tes attaques empoisonnent la cible pendant 4 secondes."},
            {"name": "L'embuscade", "keys": ["W", "AA", "Q"], "when": "Tu sors des hautes herbes.",
             "how": "Sors de ton invisibilité pour profiter de l'Effet de surprise (vitesse d'attaque augmentée quelques secondes), puis aveugle et attaque."},
            {"name": "Le contrôle de zone", "keys": ["R", "R"], "when": "Les ennemis approchent d'un passage.",
             "how": "Piège nocif lance un champignon : si un ennemi marche dessus, un nuage empoisonné le ralentit et le blesse ; lancé sur un autre champignon, il rebondit avec plus de portée."},
        ],
        "mistakes": [
            "Rester visible quand tu peux te cacher.",
            "Placer des champignons sans les cacher.",
            "Ignorer l'Effet de surprise : c'est ta fenêtre de dégâts.",
        ],
    }},
}
