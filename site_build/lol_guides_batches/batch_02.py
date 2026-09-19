"""Guides rédigés, lot 2. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Viktor": {"fr": {
        "playstyle": (
            "Viktor est un mage qui devient plus fort au fil de la partie : chaque élimination lui rapporte des fragments Hextech, et tous les 100 fragments il améliore définitivement une compétence. "
            "Une fois les quatre compétences de base améliorées, il peut améliorer son ultime. Sa force vient du contrôle de zone : ralentissements, étourdissements sur le Champ gravitationnel et Tempête arcanique qu'il redirige."
        ),
        "laning": (
            "Siphonnage te donne un bouclier et renforce ta prochaine attaque : utilise-le pour trader en sécurité. "
            "Chaque élimination compte double pour toi, car elle te rapproche d'une amélioration : priorise les derniers coups."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "AA", "E"], "when": "Un ennemi est à portée du Rayon Hextech.",
             "how": "Siphonnage inflige des dégâts, te protège et renforce ton attaque ; enchaîne avec l'attaque renforcée puis Rayon Hextech, qui touche tous les ennemis sur sa ligne."},
            {"name": "Le contrôle de zone", "keys": ["W", "E", "Q"], "when": "Les ennemis se regroupent autour d'un objectif ou d'une porte de tour.",
             "how": "Pose Champ gravitationnel : les ennemis qui y restent trop longtemps sont étourdis. Rayon Hextech et Siphonnage complètent pendant qu'ils tentent de sortir."},
            {"name": "L'ultime en combat d'équipe", "keys": ["W", "R", "E"], "when": "Un combat d'équipe est engagé.",
             "how": "Tempête arcanique inflige des dégâts périodiques et interrompt les canalisations ennemies ; tu peux la rediriger pour suivre les cibles. Si un champion meurt après avoir été blessé par elle, elle grandit et dure plus longtemps (version améliorée)."},
        ],
        "mistakes": [
            "Négliger les derniers coups : tes fragments Hextech, donc tes améliorations, dépendent des éliminations.",
            "Lancer Tempête arcanique sans la rediriger : elle peut suivre les ennemis qui fuient.",
            "Placer Champ gravitationnel sans piéger de cible : il ne rapporte qu'en gardant les ennemis dans sa zone.",
        ],
    }},
    "Syndra": {"fr": {
        "playstyle": (
            "Syndra est une mage de burst qui joue avec ses sphères noires : elles restent quelques secondes et peuvent être manipulées par ses autres compétences. "
            "Sa passive collecte des éclats de courroux qui améliorent ses compétences en plusieurs paliers. Elle finit ses cibles en les bombardant avec toutes ses sphères."
        ),
        "laning": (
            "Pose des sphères noires pour harceler à distance et les garder en réserve pour ton ultime : plus tu en as, plus l'ultime frappe fort. "
            "Force de la volonté peut lancer une sphère ou un sbire ennemi, et ralentit ceux qu'il touche."
        ),
        "combos": [
            {"name": "Le combo d'étourdissement", "keys": ["Q", "E", "W"], "when": "Un ennemi est à portée d'une sphère noire.",
             "how": "Pose une sphère, puis Dispersion des faibles la repousse avec les ennemis : ceux frappés par les sphères sont étourdis. Force de la volonté lance une sphère ou un sbire pour ajouter des dégâts et un ralentissement."},
            {"name": "Le burst complet", "keys": ["Q", "Q", "E", "W", "R"], "when": "Un carry est à portée de toutes tes sphères.",
             "how": "Accumule des sphères noires, étourdis avec Dispersion des faibles, puis Déchaînement de puissance bombarde le champion avec toutes tes sphères. Plus tu en as, plus il frappe fort."},
            {"name": "Le nettoyage", "keys": ["R"], "when": "Un champion ennemi affaibli tente de fuir.",
             "how": "Avec les paliers de passive débloqués, Déchaînement de puissance exécute les cibles dont les PV sont bas."},
        ],
        "mistakes": [
            "Lancer l'ultime avec peu de sphères noires : il est bien plus fort avec un stock complet.",
            "Utiliser Dispersion des faibles sans sphère à repousser : c'est le cœur de l'étourdissement.",
            "Négliger les éclats de courroux : ils améliorent tes compétences par paliers, joue-les à ton avantage.",
        ],
    }},
    "Caitlyn": {"fr": {
        "playstyle": (
            "Caitlyn est une tireuse de zone et de portée : ses pièges immobilisent les ennemis et lui octroient un Tir dans la tête renforcé, dont la portée est doublée contre les cibles prises au piège ou dans le filet. "
            "Elle domine sa lane par la distance et le contrôle, et son ultime achève une cible unique à très longue portée."
        ),
        "laning": (
            "Pose des pièges-yordle derrière toi et sur les passages : ils révèlent et immobilisent 1,5 seconde le champion qui les déclenche. "
            "Enchaîne l'immobilisation avec Pacificateur de Piltover et un Tir dans la tête renforcé pour un échange très rentable."
        ),
        "combos": [
            {"name": "Le piège et le tir", "keys": ["W", "AA", "Q"], "when": "Un ennemi marche sur ton piège.",
             "how": "Le piège immobilise, ton attaque suivante est un Tir dans la tête renforcé (portée doublée sur cible piégée), puis Pacificateur de Piltover inflige des dégâts en ligne."},
            {"name": "La défense", "keys": ["E", "W", "Q"], "when": "Un ennemi se rapproche de toi.",
             "how": "Filet de calibre 90 ralentit la cible et te projette en arrière pour reprendre de la distance ; pose un piège à ton arrivée et finis avec le tir perforant."},
            {"name": "L'exécution à distance", "keys": ["R"], "when": "Un ennemi est à très basse vie et visible.",
             "how": "Tir chirurgical prend son temps pour infliger de gros dégâts à une cible unique à très longue portée. Les champions ennemis peuvent intercepter la balle à la place de leur allié : vérifie qu'aucun ne s'interpose."},
        ],
        "mistakes": [
            "Utiliser l'ultime avec un ennemi proche de la cible : il peut intercepter la balle.",
            "Poser tous tes pièges d'un coup : ils ont peu de délai de récupération, mais un bon placement vaut mieux que la quantité.",
            "Oublier que Filet de calibre 90 te projette en arrière : ne l'utilise pas contre un mur derrière toi.",
        ],
    }},
    "Lulu": {"fr": {
        "playstyle": (
            "Lulu est une enchanteresse-mage qui protège et contrôle. Pix, son compagnon, tire des projectiles magiques guidés quand le champion qu'il suit attaque. "
            "Sa force est de transformer un ennemi en petite bête inoffensive avec Fantaisie ou de propulser un allié avec la même compétence, puis de faire grandir un allié avec son ultime."
        ),
        "laning": (
            "Duo éclatant ralentit grandement : pose-le pour contrôler la distance et harceler. "
            "Pix à la rescousse ! permet de protéger un allié en le suivant, ou de blesser un ennemi et d'obtenir sa vision : place-le au bon endroit avant l'échange."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée du Duo éclatant.",
             "how": "Duo éclatant tire deux projectiles qui blessent et ralentissent. Pix à la rescousse ! sur l'ennemi le blesse et te donne sa vision, puis tes attaques déclenchent les tirs de Pix."},
            {"name": "La protection du carry", "keys": ["W", "E", "R"], "when": "Ton carry est plongé par un ennemi.",
             "how": "Fantaisie sur l'agresseur l'empêche d'attaquer et de lancer des sorts ; sur ton allié, elle augmente ses vitesses de déplacement et d'attaque. Croissance prodigieuse projette en l'air les ennemis proches et donne des PV à l'allié."},
            {"name": "L'engagement d'équipe", "keys": ["W", "Q", "R"], "when": "Ton équipe engage.",
             "how": "Ralentis avec Duo éclatant, neutralise la principale menace avec Fantaisie, puis fais grandir ton tank ou ton carry avec l'ultime : il ralentit ensuite les ennemis proches avec son halo."},
        ],
        "mistakes": [
            "Utiliser Fantaisie sur le mauvais champion : son délai de récupération est long.",
            "Lancer l'ultime en oubliant qu'il projette les ennemis proches : place-toi au bon moment pour interrompre leur plongée.",
            "Négliger Pix : ses tirs dépendent des attaques de l'allié qu'il suit.",
        ],
    }},
    "Jayce": {"fr": {
        "playstyle": (
            "Jayce alterne entre deux formes : Marteau (mêlée) et Canon (distance), en gagnant de la vitesse de déplacement à chaque changement. "
            "Chaque forme possède ses propres compétences : en Marteau il bondit, blesse et repousse ; en Canon il tire un orbe à longue portée et accélère ses attaques. "
            "Sa force vient de la maîtrise du changement d'arme au bon moment."
        ),
        "laning": (
            "Le Canon te permet de harceler en sécurité avec Orbe électrique ; passe en Marteau pour plonger avec Direction le ciel ! quand l'ennemi est à portée d'un burst. "
            "Le changement d'arme donne une vitesse de déplacement brève : utilise-le pour te dégager ou te rapprocher."
        ),
        "combos": [
            {"name": "Le harcèlement en Canon", "keys": ["E", "Q", "W", "AA"], "when": "Tu es à distance et l'ennemi est dans l'axe.",
             "how": "Le Portail d'accélération augmente la vitesse, la portée et les dégâts de l'Orbe électrique qui le traverse. Hypercharge porte ta vitesse d'attaque au maximum pour plusieurs attaques."},
            {"name": "Le plongeon en Marteau", "keys": ["R", "Q", "W", "E", "AA"], "when": "Un ennemi est à portée de bond.",
             "how": "Après l'ultime, Direction le ciel ! te fait bondir sur l'ennemi, le blesse et le ralentit ; Champ électrique et Coup foudroyant (dégâts magiques, repousse) complètent."},
            {"name": "L'engagement et le retrait", "keys": ["R", "Q", "R"], "when": "Un ennemi est à portée et tu veux le harceler puis te dégager.",
             "how": "Le premier passage en Canon réduit l'armure et la résistance magique de l'ennemi, le retour en Marteau inflige des dégâts magiques supplémentaires : alterne pour tirer parti de ces bonus."},
        ],
        "mistakes": [
            "Rester trop longtemps dans une seule forme : la force de Jayce vient du changement.",
            "Bondir en Marteau sans avoir de sortie : tu te retrouves au cœur des ennemis.",
            "Oublier que l'ultime a un délai de récupération très court (6 s) : change d'arme dès que le moment est bon.",
        ],
    }},
    "Qiyana": {"fr": {
        "playstyle": (
            "Qiyana est une assassine à éléments : Terraforce enchante son arme avec un élément, et ses attaques et compétences infligent des dégâts supplémentaires tant qu'elle reste enchantée. "
            "Sa passive donne des dégâts bonus à la première compétence ou attaque contre un ennemi. Son ultime provoque une explosion en touchant un élément du terrain et étourdit les ennemis proches."
        ),
        "laning": (
            "Prépare toujours Terraforce avant d'engager, car l'enchantement dépend du terrain traversé. "
            "Audace te permet de te ruer sur un ennemi : utilise-la à bon escient, car elle est ton principal moyen d'engager comme de fuir."
        ),
        "combos": [
            {"name": "Le combo de base", "keys": ["W", "E", "Q", "AA"], "when": "Un ennemi est à portée d'Audace.",
             "how": "Terraforce enchante ton arme, Audace te rue sur la cible (et déclenche les dégâts bonus de ta passive), Courroux élémentaire applique l'effet de l'élément puis tes attaques enchantées finissent."},
            {"name": "L'ultime contre un mur", "keys": ["W", "R", "Q"], "when": "Un ennemi est près d'un mur ou d'un élément de terrain.",
             "how": "Tour de force suprême envoie une onde de choc qui explose en touchant un élément, ce qui étourdit et blesse les ennemis proches. Positionne la cible contre l'élément avant de lancer."},
            {"name": "La sortie", "keys": ["W", "E"], "when": "Tu dois te dégager.",
             "how": "Terraforce te rue vers une zone, puis Audace te rue sur un ennemi ou une cible proche pour prolonger ton déplacement."},
        ],
        "mistakes": [
            "Lancer l'ultime en plein milieu de la zone sans élément du terrain à proximité : il faut qu'il explose.",
            "Engager sans Terraforce : tes attaques n'infligent pas les dégâts supplémentaires de l'enchantement.",
            "Dépenser Audace sans plan de sortie : elle est ton principal outil de mobilité.",
        ],
    }},
    "Thresh": {"fr": {
        "playstyle": (
            "Thresh est un support d'engagement et de protection. Peine capitale attire un ennemi vers toi (ou toi vers lui), Lien des ténèbres protège les alliés proches avec une lanterne qu'ils peuvent utiliser pour se ruer vers lui, et La cage emprisonne les ennemis avec des murs qui ralentissent et blessent. "
            "Sa passive collecte des âmes qui augmentent définitivement son armure et sa puissance."
        ),
        "laning": (
            "Peine capitale est ta compétence principale : place-la avec soin, car elle décide de ta lane. "
            "Pose la lanterne entre ton carry et le danger, puis utilise Fauchage pour repousser un ennemi ou le ramener sous ta tour."
        ),
        "combos": [
            {"name": "Le crochet et le fauchage", "keys": ["Q", "E", "AA"], "when": "Un ennemi est touché par Peine capitale.",
             "how": "Peine capitale ligote et attire l'ennemi ; Fauchage l'envoie dans la direction du coup (vers tes alliés ou la tour). Tes attaques chargées infligent plus de dégâts si tu attends entre elles."},
            {"name": "L'engagement de combat d'équipe", "keys": ["Q", "Q", "R"], "when": "Le carry adverse est isolé.",
             "how": "Une deuxième activation de Peine capitale t'attire vers l'ennemi, ce qui te place pour poser La cage autour de lui et de ses alliés. Ses murs ralentissent et blessent ceux qui les brisent."},
            {"name": "Le sauvetage", "keys": ["W", "E"], "when": "Ton carry est plongé.",
             "how": "Lien des ténèbres protège les alliés proches contre les dégâts, et ils peuvent cliquer sur la lanterne pour se ruer vers toi ; Fauchage repousse les agresseurs."},
        ],
        "mistakes": [
            "Utiliser Peine capitale sans regarder les sbires : ils bloquent la trajectoire.",
            "Poser la lanterne trop loin de tes alliés : ils ne peuvent l'utiliser que s'ils l'atteignent.",
            "Lancer La cage sans que ton équipe soit prête à en profiter.",
        ],
    }},
    "Locke": {"fr": {
        "playstyle": (
            "Locke est un assassin-mage dont les attaques infligent des dégâts magiques bonus à l'impact, augmentés selon les PV manquants de l'ennemi. "
            "Ses Clous rituels marquent les ennemis, et il peut consommer ces marques pour infliger des dégâts bonus avec ses attaques. Son ultime exécute les ennemis touchés et le renforce en scellant des champions."
        ),
        "laning": (
            "Marque avec Clous rituels puis frappe : la marque est ce qui décuple tes dégâts d'attaque. "
            "Brûlure d'âme te rend plus rapide mais te blesse : n'active-la que quand tu peux gagner l'échange, car tu te soignes d'une portion des dégâts subis à la fin."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "W", "AA"], "when": "Un ennemi est à portée des clous.",
             "how": "Clous rituels marquent la cible, tes attaques consomment les marques pour des dégâts bonus, Brûlure d'âme augmente ta vitesse d'attaque et de déplacement."},
            {"name": "L'engagement par la traque", "keys": ["E", "Q", "AA", "W"], "when": "Un ennemi est hors de portée.",
             "how": "Traque cendrée te téléporte puis te rue sur la prochaine cible en blessant les ennemis traversés. Marque et attaque dès l'arrivée."},
            {"name": "L'exécution", "keys": ["R"], "when": "Un ennemi est à basse vie.",
             "how": "Purgatoire inflige des dégâts et peut exécuter les ennemis touchés ; en scellant des champions, Locke gagne de la puissance supplémentaire."},
        ],
        "mistakes": [
            "Activer Brûlure d'âme sans cible à frapper : elle t'inflige des dégâts sans contrepartie.",
            "Lancer Purgatoire sur des ennemis en pleine santé : il sert surtout à finir.",
            "Oublier de consommer tes marques avec les attaques.",
        ],
    }},
    "Lux": {"fr": {
        "playstyle": (
            "Lux est une mage à longue portée qui contrôle avec Entrave de lumière et Anomalie radieuse, protège avec Barrière prismatique et finit avec Éclat final. "
            "Ses compétences chargent la cible en énergie, et sa prochaine attaque embrase cette énergie pour des dégâts magiques supplémentaires."
        ),
        "laning": (
            "Entrave de lumière immobilise jusqu'à deux ennemis : lance-la à longue portée et enchaîne. "
            "Barrière prismatique protège les alliés touchés à l'aller comme au retour : place-la pour toucher ton carry."
        ),
        "combos": [
            {"name": "Le combo d'immobilisation", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée de l'Entrave.",
             "how": "Entrave de lumière immobilise et blesse, Anomalie radieuse ralentit puis explose, et l'attaque de base embrase l'énergie de Illumination."},
            {"name": "L'ultime de finition", "keys": ["Q", "R", "AA"], "when": "Des ennemis sont alignés ou affaiblis.",
             "how": "Éclat final tire un rayon qui inflige des dégâts dans sa zone et déclenche ta passive : Illumination est rafraîchie sur les cibles touchées. Termine avec une attaque."},
            {"name": "La protection", "keys": ["W", "E"], "when": "Ton équipe est engagée.",
             "how": "Barrière prismatique protège les alliés touchés contre les dégâts, Anomalie radieuse ralentit les poursuivants."},
        ],
        "mistakes": [
            "Lancer Entrave de lumière sans regarder les sbires : elle s'arrête après deux unités.",
            "Déclencher l'Anomalie radieuse trop tôt : l'explosion inflige les dégâts, laisse-la ralentir avant.",
            "Utiliser l'ultime sans avoir vérifié la trajectoire.",
        ],
    }},
    "Zed": {"fr": {
        "playstyle": (
            "Zed est un assassin d'énergie qui joue avec ses ombres : Shuriken-rasoir et Taillade des ombres sont lancés par lui et par ses ombres à la fois. "
            "Il regagne de l'énergie quand ses ombres et lui frappent le même ennemi avec la même compétence. Son ultime le rend impossible à cibler, le téléporte sur un champion et marque la cible pour une explosion différée."
        ),
        "laning": (
            "Ombre vivante te permet de harceler avec deux sources de dégâts : positionne l'ombre avant Shuriken-rasoir pour toucher deux fois. "
            "L'énergie est ta ressource : ne la gaspille pas, car chaque compétence en coûte."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["W", "Q", "AA"], "when": "Un ennemi est à portée de shuriken.",
             "how": "Ombre vivante envoie l'ombre vers l'avant, Shuriken-rasoir est lancé par toi et ton ombre, et tes attaques exploitent le bonus de ta passive contre les cibles à faibles PV."},
            {"name": "Le burst d'assassinat", "keys": ["R", "W", "E", "Q", "AA"], "when": "Un carry est à portée de l'ultime.",
             "how": "Marque de la mort te rend impossible à cibler et te téléporte ; frappe avec tes ombres et tes compétences. Au bout de 3 secondes la marque explose et inflige de nouveau un pourcentage de tous les dégâts que tu as infligés pendant la marque."},
            {"name": "La sortie", "keys": ["W", "W"], "when": "Tu dois t'échapper.",
             "how": "Réactiver Ombre vivante te fait changer de position avec l'ombre : place-la loin avant, puis échange."},
        ],
        "mistakes": [
            "Attaquer avec l'ultime sans finir dans les 3 secondes : la marque explose et son explosion dépend des dégâts que tu as infligés.",
            "Dépenser toute ton énergie sans avoir touché : ta passive ne la rend que si la compétence touche.",
            "Utiliser Ombre vivante sans prévoir l'échange de position.",
        ],
    }},
}
