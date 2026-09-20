"""World of Warcraft: Forever section (/wow-forever/, FR + EN).

Everything here comes from the sources listed in SOURCES -- nothing is invented, and every claim that rests on a
single source or on a community wiki says so on the page. Facts checked 2026-09-20; update the constants below when
Blizzard publishes more. The launch instant is the one Blizzard states (2026-11-04 15:00 PST = 23:00 UTC).

Page model: PAGES[lang][slug] = {title, description, kicker, h1, intro, sections:[{h2, blocks}], sources:[keys], faq?}
Block types: p (text) / list (items) / table (head, rows) / facts (items: [(label, value)]) / note (text).
"""

LAUNCH_UTC = "2026-11-04T23:00:00Z"   # 15:00 PST, as stated by Blizzard

SOURCES = {
    "blizz_beta": ("Blizzard — The World of Warcraft: Forever Beta Now Live",
                   "https://news.blizzard.com/en-us/article/24304160/the-world-of-warcraft-forever-beta-now-live"),
    "blizz_pre": ("Blizzard — Pre-Purchase World of Warcraft: Forever Upgrades",
                  "https://news.blizzard.com/en-us/article/24301508/pre-purchase-world-of-warcraft-forever-upgrades-and-begin-your-next-journey-in-azeroth"),
    "wikipedia": ("Wikipedia — World of Warcraft: Forever", "https://en.wikipedia.org/wiki/World_of_Warcraft:_Forever"),
    "warcraftwiki": ("Warcraft Wiki — World of Warcraft: Forever (community wiki)", "https://warcraft.wiki.gg/wiki/World_of_Warcraft:_Forever"),
    "icyveins": ("Icy Veins — Warcraft Forever releases November 4, beta starts September 17",
                 "https://www.icy-veins.com/wow-forever/news/warcraft-forever-releases-november-4-beta-starts-september-17/"),
    "pcgamer": ("PC Gamer — World of Warcraft: Forever beta launch times",
                "https://www.pcgamer.com/games/world-of-warcraft/world-of-warcraft-forever-beta-launch-times-how-to-sign-up-and-play-blizzards-twist-on-wow-classic/"),
    "official": ("Blizzard — World of Warcraft: Forever (official page)", "http://worldofwarcraft.blizzard.com/en-us/forever"),
}

# slug -> (nav label FR, nav label EN); "" is the hub. Order = menu order.
NAV = [
    ("", "Aperçu", "Overview"),
    ("sortie", "Sortie", "Release"),
    ("beta", "Bêta", "Beta"),
    ("editions", "Éditions et prix", "Editions & prices"),
    ("classes", "Classes et races", "Classes & races"),
    ("progression", "Progression 1-60", "Leveling 1-60"),
    ("faq", "FAQ", "FAQ"),
]

DISCLAIMER = {
    "fr": "World of Warcraft, Warcraft et Blizzard Entertainment sont des marques de Blizzard Entertainment, Inc. BrokenMeta.gg est un site indépendant : il n'est ni affilié à Blizzard, ni approuvé ou sponsorisé par elle.",
    "en": "World of Warcraft, Warcraft and Blizzard Entertainment are trademarks of Blizzard Entertainment, Inc. BrokenMeta.gg is an independent site: it is not affiliated with, endorsed or sponsored by Blizzard.",
}

# ---------------------------------------------------------------------------------------------------- FRENCH
FR_DATES = [
    ["12 septembre 2026", "Annonce du jeu lors de la BlizzCon 2026", "Wikipedia"],
    ["17 septembre 2026", "Début de la bêta", "Wikipedia, Icy Veins"],
    ["20 octobre 2026", "Envoi par e-mail des codes Invite-A-Friend (heure du Pacifique)", "Blizzard"],
    ["21 octobre 2026", "Fin de la bêta (dernier jour complet de test)", "Blizzard"],
    ["27 octobre - 3 novembre 2026", "Réservation anticipée des noms (3 personnages maximum) avec le Skyborne Heroic Pack", "Blizzard"],
    ["4 novembre 2026, 15 h (heure du Pacifique)", "Sortie mondiale", "Blizzard"],
    ["4 - 11 novembre 2026", "Période de validité des codes Invite-A-Friend", "Blizzard"],
    ["9 décembre 2026", "Déblocage annoncé des raids (source unique)", "Icy Veins"],
    ["11 janvier 2027", "Fin de la disponibilité du Warcraft Forever Collection (offre limitée)", "Blizzard"],
]

FR_DUNGEONS = [
    ["Hall of Thanes", "Forgefer (Ironforge)", "13-18", "Blizzard"],
    ["Ruins of Lordaeron", "Fossoyeuse (Undercity)", "15-20", "Blizzard"],
    ["Wetlands Dig Site", "Les Paluns (Wetlands)", "24-29", "Warcraft Wiki"],
    ["Dalaran", "Montagnes d'Alterac", "28-33", "Warcraft Wiki"],
    ["The Drowned City", "Vallée de Strangleronce", "35-40", "Warcraft Wiki"],
    ["Krol'dok Stronghold", "Riverglades", "40-45", "Warcraft Wiki"],
    ["Alcaz Prison", "Marécage d'Âprefange (Dustwallow Marsh)", "48-53", "Warcraft Wiki"],
    ["Blackmaw Hold", "Azshara", "55-60", "Warcraft Wiki"],
    ["Shaper's Terrace", "Cratère d'Un'Goro", "58-60", "Warcraft Wiki"],
]

PAGES_FR = {
    "": {
        "title": "WoW: Forever : sortie, bêta, éditions | BrokenMeta.gg",
        "description": "World of Warcraft: Forever sort le 4 novembre 2026. Bêta, éditions, classes, donjons et calendrier, avec les sources officielles citées.",
        "kicker": "World of Warcraft: Forever",
        "h1": "World of Warcraft: Forever : tout savoir avant la sortie",
        "intro": "Le nouveau WoW de Blizzard sort le 4 novembre 2026 et sa bêta est ouverte. Cette section réunit ce qui est confirmé : dates, accès à la bêta, éditions, classes, donjons et calendrier. Chaque information renvoie à sa source, et ce qui vient d'un wiki communautaire ou d'une source unique est signalé comme tel.",
        "sections": [
            {"h2": "L'essentiel en quelques lignes", "blocks": [
                {"type": "facts", "items": [
                    ("Sortie", "4 novembre 2026, 15 h (heure du Pacifique)"),
                    ("Bêta", "du 17 septembre au 21 octobre 2026"),
                    ("Niveau maximum", "60"),
                    ("Contenu annoncé", "plus de 1 000 quêtes, neuf donjons, deux raids"),
                    ("Nouvelle race", "les Skyborne"),
                    ("Accès", "inclus avec un abonnement ou du temps de jeu WoW"),
                ]},
                {"type": "p", "text": "World of Warcraft: Forever est une branche distincte du jeu, qui vit à côté de WoW moderne et de WoW Classic. Elle se déroule pendant la première année de WoW, dans une continuité séparée de la version moderne, et garde le niveau maximum à 60. Là où Classic recrée le jeu d'origine, Forever développe l'Azeroth d'origine avec du contenu nouveau (source : Wikipedia)."},
            ]},
            {"h2": "Les dates clés", "blocks": [
                {"type": "table", "head": ["Date", "Événement", "Source"], "rows": FR_DATES},
                {"type": "note", "text": "Les dates de la bêta et de la sortie viennent des annonces de Blizzard ; l'ouverture de la bêta au 17 septembre est reprise par Wikipedia et Icy Veins. Icy Veins indique une fin de bêta au 22 octobre : nous retenons le 21 octobre, la date donnée par Blizzard."},
            ]},
            {"h2": "Ce qui est annoncé", "blocks": [
                {"type": "list", "items": [
                    "Une nouvelle race, les Skyborne, avec la zone de départ Zephras Isle (Blizzard).",
                    "Trois nouvelles zones : Mount Hyjal, Zephras Isle et Riverglades (Icy Veins, Wikipedia).",
                    "Plus de 1 000 nouvelles quêtes, neuf donjons et deux raids (Wikipedia).",
                    "De nouvelles combinaisons race-classe, dont des Paladins Réprouvés et des Chamans Nains (Wikipedia).",
                    "Un champ de bataille inédit, les Darkspear Islands (Icy Veins, Warcraft Wiki).",
                    "Un système de transmogrification optionnel et une bascule d'affichage des modèles de personnages SD/HD (Icy Veins).",
                ]},
            ]},
            {"h2": "Aller plus loin", "blocks": [
                {"type": "cards", "items": [
                    ("sortie", "Date de sortie", "Le jour et l'heure du lancement, avec la conversion en heure de Paris."),
                    ("beta", "La bêta", "Comment y accéder, ce qu'on peut y faire et jusqu'à quel niveau."),
                    ("editions", "Éditions et prix", "Le contenu de chaque pack, et ce qui est inclus dans l'abonnement."),
                    ("classes", "Classes et races", "Les classes, les races et les nouvelles combinaisons."),
                    ("progression", "Progression 1-60", "Les donjons par tranche de niveau, les zones et les raids."),
                    ("faq", "FAQ", "Les réponses aux questions les plus fréquentes."),
                ]},
            ]},
        ],
        "sources": ["blizz_beta", "blizz_pre", "wikipedia", "icyveins", "warcraftwiki"],
    },
    "sortie": {
        "title": "Date de sortie de WoW: Forever : 4 novembre 2026",
        "description": "WoW: Forever sort le 4 novembre 2026 à 15 h (heure du Pacifique), soit minuit à Paris. Heure du lancement, accès anticipé et calendrier.",
        "kicker": "World of Warcraft: Forever · Sortie",
        "h1": "Date de sortie de WoW: Forever",
        "intro": "Blizzard a fixé la sortie mondiale de World of Warcraft: Forever au 4 novembre 2026 à 15 h, heure du Pacifique.",
        "sections": [
            {"h2": "Heure du lancement chez vous", "blocks": [
                {"type": "table", "head": ["Fuseau", "Date et heure de sortie"], "rows": [
                    ["Heure du Pacifique (PST, États-Unis)", "mercredi 4 novembre 2026, 15 h 00 (donnée Blizzard)"],
                    ["UTC / heure de Londres", "mercredi 4 novembre 2026, 23 h 00"],
                    ["Heure de Paris (CET)", "jeudi 5 novembre 2026, 0 h 00 (dans la nuit du 4 au 5)"],
                ]},
                {"type": "note", "text": "Seule l'heure du Pacifique vient de Blizzard. Les deux autres lignes sont notre conversion : le passage à l'heure d'hiver a lieu le 25 octobre en France et le 1er novembre aux États-Unis, donc l'écart entre Paris et la côte ouest est de 9 heures à cette date."},
            ]},
            {"h2": "Faut-il acheter le jeu ?", "blocks": [
                {"type": "p", "text": "Non. Selon Blizzard, World of Warcraft: Forever est accessible avec un abonnement WoW ou du temps de jeu existant, sans achat séparé. Les packs Skyborne sont des achats optionnels : ils donnent accès à la nouvelle race, à des cosmétiques et, pour certains, à la bêta. Le détail est sur la page Éditions et prix."},
            ]},
            {"h2": "Avant la sortie", "blocks": [
                {"type": "list", "items": [
                    "Du 17 septembre au 21 octobre : la bêta, avec un niveau maximum de 20 la première semaine puis 30.",
                    "Du 27 octobre au 3 novembre : réservation anticipée des noms de personnages (3 maximum) pour les détenteurs du Skyborne Heroic Pack ou d'un pack supérieur.",
                    "À partir du 20 octobre : envoi par e-mail des codes Invite-A-Friend, valables du 4 au 11 novembre.",
                ]},
            ]},
            {"h2": "Après la sortie : le calendrier annoncé", "blocks": [
                {"type": "list", "items": [
                    "9 décembre 2026 : déblocage des raids Barrow Deeps (10 joueurs), Hyjal Summit (20 joueurs) et Onyxia's Lair (40 joueurs).",
                    "Printemps 2027 : deux raids supplémentaires, l'un à 10 et l'autre à 20 joueurs.",
                    "Été 2027 : un raid emblématique remanié et un nouveau raid.",
                    "Le mode Hardcore est annoncé pour « entre 2026 et 2027 », sans date précise.",
                ]},
                {"type": "note", "text": "Ce calendrier ne provient que d'Icy Veins. Blizzard ne l'a pas repris dans les annonces que nous avons consultées : à considérer comme provisoire."},
            ]},
        ],
        "sources": ["blizz_pre", "blizz_beta", "icyveins", "wikipedia"],
    },
    "beta": {
        "title": "Bêta de WoW: Forever : accès, dates et niveau max",
        "description": "Bêta de WoW: Forever du 17 septembre au 21 octobre 2026 : comment y accéder, niveau 20 puis 30, contenu jouable et vérification de la licence.",
        "kicker": "World of Warcraft: Forever · Bêta",
        "h1": "La bêta de WoW: Forever",
        "intro": "La bêta de World of Warcraft: Forever a commencé le 17 septembre 2026 et se termine le 21 octobre. Voici comment y accéder et ce qu'on peut y faire.",
        "sections": [
            {"h2": "En bref", "blocks": [
                {"type": "facts", "items": [
                    ("Ouverture", "17 septembre 2026"),
                    ("Fin", "21 octobre 2026"),
                    ("Niveau maximum, semaine 1", "20"),
                    ("Niveau maximum, ensuite", "30"),
                    ("Personnage", "un nouveau personnage de test à créer"),
                ]},
            ]},
            {"h2": "Comment accéder à la bêta", "blocks": [
                {"type": "list", "items": [
                    "S'inscrire sur la page officielle du jeu, avec son compte Battle.net. L'inscription donne une chance d'être sélectionné, pas la certitude : des invitations sont envoyées régulièrement pendant le test.",
                    "Acheter le Skyborne Epic Pack ou le Warcraft Forever Collection, qui incluent l'accès à la bêta. Le Skyborne Heroic Pack ne l'inclut pas.",
                    "Faire partie des invités de Blizzard : anciens de la communauté, presse, sites de fans, amis et famille.",
                ]},
                {"type": "p", "text": "Pour vérifier votre accès, regardez dans votre compte Battle.net si la licence « World of Warcraft: Forever beta license » est présente. Les acheteurs d'un pack peuvent attendre jusqu'à 30 minutes avant qu'elle apparaisse."},
            ]},
            {"h2": "Ce qu'on peut faire en bêta", "blocks": [
                {"type": "list", "items": [
                    "Créer un nouveau personnage de test : les personnages existants ne sont pas repris.",
                    "Semaine 1 : niveau maximum 20, avec la nouvelle race Skyborne et la zone Zephras Isle, ainsi que les donjons Hall of Thanes (niveaux 13 à 18) et Ruins of Lordaeron (niveaux 15 à 20).",
                    "Ensuite : niveau maximum 30, avec le contenu adapté à ces niveaux.",
                    "Plus tard pendant la bêta : un « Server Slam » est annoncé, sans date précise à ce jour.",
                ]},
                {"type": "note", "text": "Dans les annonces Blizzard consultées, les régions de serveurs et ce qui est conservé au lancement ne sont pas précisés."},
            ]},
        ],
        "sources": ["blizz_beta", "blizz_pre", "pcgamer", "wikipedia"],
    },
    "editions": {
        "title": "Éditions et prix de WoW: Forever : packs Skyborne",
        "description": "Skyborne Heroic Pack, Epic Pack et Warcraft Forever Collection : contenu de chaque édition, accès bêta, prix relevés par la presse et offre limitée.",
        "kicker": "World of Warcraft: Forever · Éditions",
        "h1": "Éditions et prix de WoW: Forever",
        "intro": "Le jeu est inclus dans l'abonnement WoW. Trois packs optionnels ajoutent la race Skyborne, des cosmétiques et, pour deux d'entre eux, l'accès à la bêta.",
        "sections": [
            {"h2": "Le jeu de base", "blocks": [
                {"type": "p", "text": "World of Warcraft: Forever est accessible avec un abonnement WoW ou du temps de jeu existant, sans achat séparé (Blizzard). Les packs ci-dessous sont optionnels."},
            ]},
            {"h2": "Comparer les trois packs", "blocks": [
                {"type": "table", "head": ["", "Skyborne Heroic Pack", "Skyborne Epic Pack", "Warcraft Forever Collection"], "rows": [
                    ["Race Skyborne et départ à Zephras Isle", "Oui", "Oui", "Oui"],
                    ["Accès à la bêta dès le 17 septembre", "Non", "Oui", "Oui"],
                    ["30 jours de temps de jeu à partir du 4 novembre", "Non", "Oui", "Oui"],
                    ["Réservation anticipée des noms (27 oct. - 3 nov.)", "Oui, 3 personnages", "Oui", "Oui"],
                    ["Codes Invite-A-Friend", "1", "3", "3"],
                    ["Warcraft III: Reforged et campagne Forsaken Kingdom", "Non", "Non", "Oui"],
                    ["Prix relevé par la presse (États-Unis)", "non relevé", "59,99 $", "79,99 $"],
                ]},
                {"type": "note", "text": "Les prix ne figurent pas dans les annonces de Blizzard que nous avons consultées, qui renvoient à la boutique Battle.net. Les montants en dollars viennent de la presse (PC Gamer) : vérifiez-les dans la boutique avant d'acheter. Les prix en euros ne sont pas connus ici."},
            ]},
            {"h2": "Ce que contient le Skyborne Heroic Pack", "blocks": [
                {"type": "list", "items": [
                    "L'accès à la race Skyborne et à son expérience de départ à Zephras Isle.",
                    "La réservation anticipée des noms, pour 3 personnages, du 27 octobre au 3 novembre.",
                    "Une monture terrestre, la Cerulean Prideclaw.",
                    "Un cosmétique, le Shen'dorei Skyseer's Garb, un sac à dos Veteran Adventurer's Rucksack et un jouet Shen'dorei Windwell.",
                    "Des éléments de décor de logement Skyborne.",
                    "Un code Invite-A-Friend pour le lancement.",
                ]},
            ]},
            {"h2": "Ce que les packs supérieurs ajoutent", "blocks": [
                {"type": "list", "items": [
                    "Skyborne Epic Pack : tout le Heroic Pack, plus l'accès à la bêta dès le 17 septembre, 30 jours de temps de jeu ajoutés à partir du 4 novembre, d'autres cosmétiques, des tabards et des mascottes, et deux codes Invite-A-Friend en plus (3 au total).",
                    "Warcraft Forever Collection : tout l'Epic Pack, plus Warcraft III: Reforged, la campagne Warcraft III Reforged: Forsaken Kingdom et une figurine de décor Réprouvés et Humains. Offre limitée dans le temps, disponible jusqu'au 11 janvier 2027.",
                ]},
                {"type": "p", "text": "Les codes Invite-A-Friend sont envoyés par e-mail à partir du 20 octobre 2026 et valables du 4 au 11 novembre. Ils ne donnent pas accès à la bêta."},
            ]},
        ],
        "sources": ["blizz_pre", "blizz_beta", "pcgamer"],
    },
    "classes": {
        "title": "Classes et races de WoW: Forever : combinaisons",
        "description": "Les neuf classes, les races et la nouvelle race Skyborne de WoW: Forever, avec les nouvelles combinaisons race-classe annoncées et leurs sources.",
        "kicker": "World of Warcraft: Forever · Classes et races",
        "h1": "Classes et races de WoW: Forever",
        "intro": "Voici ce que l'on sait des classes et des races de World of Warcraft: Forever. Blizzard n'a pas encore détaillé les classes une par une : cette page s'en tient à ce qui est sourcé.",
        "sections": [
            {"h2": "Les classes", "blocks": [
                {"type": "p", "text": "Selon la Warcraft Wiki (source communautaire), le jeu compte neuf classes : Druide, Chasseur, Mage, Paladin, Prêtre, Voleur, Chaman, Démoniste et Guerrier. Les talents des classes sont rééquilibrés pour que davantage de choix soient viables (même source)."},
                {"type": "note", "text": "Icy Veins ne mentionne que « des combinaisons race-classe supplémentaires » sans nommer les classes. Aucune source officielle consultée ne détaille les classes une à une : nous n'écrivons donc pas de guide de spécialisation à ce stade."},
            ]},
            {"h2": "Les races", "blocks": [
                {"type": "list", "items": [
                    "Les races d'origine de WoW : Humain, Nain, Elfe de la nuit et Gnome pour l'Alliance ; Orc, Mort-vivant (Réprouvé), Tauren et Troll pour la Horde (Warcraft Wiki).",
                    "Une nouvelle race, les Skyborne, accessible avec les packs Skyborne (Blizzard, Wikipedia). Leur zone de départ est Zephras Isle.",
                ]},
                {"type": "note", "text": "La Warcraft Wiki ne dit pas clairement à quelle faction appartiennent les Skyborne, et Blizzard ne le précise pas dans les annonces consultées : nous ne l'affirmons donc pas."},
            ]},
            {"h2": "Les nouvelles combinaisons race-classe", "blocks": [
                {"type": "p", "text": "Wikipedia cite des Paladins Réprouvés et des Chamans Nains, deux combinaisons absentes du jeu d'origine. La Warcraft Wiki en liste davantage, mais sa liste mélange des combinaisons déjà présentes dans WoW Classic : nous ne la reprenons pas tant qu'elle n'est pas confirmée."},
            ]},
        ],
        "sources": ["wikipedia", "warcraftwiki", "icyveins", "blizz_pre"],
    },
    "progression": {
        "title": "Progression 1-60 dans WoW: Forever : donjons et zones",
        "description": "Les donjons de WoW: Forever par tranche de niveau, les nouvelles zones, les raids et le calendrier. Ce qui est sourcé pour monter de 1 à 60.",
        "kicker": "World of Warcraft: Forever · Progression",
        "h1": "Monter de 1 à 60 dans WoW: Forever",
        "intro": "Le niveau maximum reste 60. Cette page rassemble ce qui est connu pour planifier la montée en niveau : donjons par tranche de niveau, nouvelles zones et raids. Un itinéraire de quêtes complet viendra après la sortie, quand il sera possible de le vérifier.",
        "sections": [
            {"h2": "Les neuf donjons, par niveau", "blocks": [
                {"type": "table", "head": ["Donjon", "Lieu", "Niveaux", "Source"], "rows": FR_DUNGEONS},
                {"type": "note", "text": "Blizzard confirme les deux premiers donjons et leurs niveaux. Les sept autres viennent de la Warcraft Wiki (source communautaire) : les noms de lieux sont ceux d'origine ou de la wiki, à confirmer au lancement."},
            ]},
            {"h2": "Les nouvelles zones", "blocks": [
                {"type": "list", "items": [
                    "Zephras Isle : la zone de départ des Skyborne, jouable dès la bêta (Blizzard).",
                    "Mount Hyjal et Riverglades : deux autres nouvelles zones annoncées (Icy Veins, Wikipedia).",
                ]},
            ]},
            {"h2": "Les raids", "blocks": [
                {"type": "list", "items": [
                    "The Barrow Deeps : raid à 10 joueurs (Warcraft Wiki, Icy Veins).",
                    "Hyjal Summit : raid à 20 joueurs (Warcraft Wiki, Icy Veins).",
                    "Onyxia's Lair : raid à 40 joueurs, cité dans le déblocage du 9 décembre 2026 (Icy Veins).",
                ]},
                {"type": "p", "text": "Le calendrier des raids suivants, du printemps et de l'été 2027, est sur la page Sortie."},
            ]},
            {"h2": "Pendant la bêta", "blocks": [
                {"type": "p", "text": "La bêta plafonne au niveau 20 la première semaine, puis au niveau 30. Elle permet donc de tester Zephras Isle et les deux premiers donjons, mais pas la montée jusqu'à 60."},
            ]},
        ],
        "sources": ["blizz_beta", "warcraftwiki", "icyveins", "wikipedia"],
    },
    "faq": {
        "title": "FAQ WoW: Forever : sortie, bêta, prix, différences",
        "description": "Réponses aux questions sur WoW: Forever : date de sortie, accès à la bêta, achat, niveau maximum, différences avec WoW Classic. Sources citées.",
        "kicker": "World of Warcraft: Forever · FAQ",
        "h1": "FAQ : World of Warcraft: Forever",
        "intro": "Les questions les plus fréquentes sur World of Warcraft: Forever, avec des réponses basées sur les annonces officielles et des sources citées.",
        "faq": [
            ("Qu'est-ce que World of Warcraft: Forever ?",
             "Une branche distincte de World of Warcraft, qui vit à côté de WoW moderne et de WoW Classic. Elle se déroule pendant la première année du jeu, dans une continuité séparée, et développe l'Azeroth d'origine avec du contenu nouveau, en gardant le niveau maximum à 60."),
            ("Quand sort WoW: Forever ?",
             "Le 4 novembre 2026 à 15 h, heure du Pacifique, selon Blizzard. Cela correspond à minuit à Paris, dans la nuit du 4 au 5 novembre."),
            ("Faut-il acheter le jeu ?",
             "Non. Il est accessible avec un abonnement WoW ou du temps de jeu existant. Les packs Skyborne sont optionnels."),
            ("Comment accéder à la bêta ?",
             "En s'inscrivant sur la page officielle avec son compte Battle.net, ce qui donne une chance d'être sélectionné, ou en achetant le Skyborne Epic Pack ou le Warcraft Forever Collection. La bêta dure du 17 septembre au 21 octobre 2026."),
            ("Jusqu'à quel niveau peut-on jouer en bêta ?",
             "Niveau 20 la première semaine, puis niveau 30 plus tard dans la bêta."),
            ("Les personnages de la bêta sont-ils conservés ?",
             "Blizzard demande de créer un nouveau personnage de test : les personnages existants ne sont pas repris. Les annonces consultées ne précisent pas ce qui est conservé au lancement."),
            ("Quel est le niveau maximum ?",
             "60, maintenu de façon durable : la progression passe par de nouvelles activités, histoires, capacités et systèmes plutôt que par des niveaux supplémentaires."),
            ("Quelle différence avec WoW Classic ?",
             "Classic recrée le jeu d'origine. Forever le prolonge : plus de 1 000 nouvelles quêtes, neuf donjons, deux raids, une nouvelle race et de nouvelles combinaisons race-classe."),
            ("Le mode Hardcore est-il prévu ?",
             "Icy Veins l'annonce « entre 2026 et 2027 », sans date précise."),
            ("BrokenMeta.gg est-il affilié à Blizzard ?",
             "Non. C'est un site indépendant, qui cite ses sources et signale ce qui n'est pas confirmé."),
        ],
        "sections": [],
        "sources": ["blizz_pre", "blizz_beta", "wikipedia", "icyveins", "pcgamer"],
    },
}

# ---------------------------------------------------------------------------------------------------- ENGLISH
EN_DATES = [
    ["September 12, 2026", "Game announced at BlizzCon 2026", "Wikipedia"],
    ["September 17, 2026", "Beta begins", "Wikipedia, Icy Veins"],
    ["October 20, 2026", "Invite-A-Friend codes emailed (Pacific time)", "Blizzard"],
    ["October 21, 2026", "Beta ends (last full day of testing)", "Blizzard"],
    ["October 27 - November 3, 2026", "Early name reservation (up to 3 characters) with the Skyborne Heroic Pack", "Blizzard"],
    ["November 4, 2026, 3:00 p.m. (Pacific time)", "Worldwide launch", "Blizzard"],
    ["November 4 - 11, 2026", "Invite-A-Friend codes valid", "Blizzard"],
    ["December 9, 2026", "Announced raid unlock (single source)", "Icy Veins"],
    ["January 11, 2027", "Warcraft Forever Collection availability ends (limited-time bundle)", "Blizzard"],
]

EN_DUNGEONS = [
    ["Hall of Thanes", "Ironforge", "13-18", "Blizzard"],
    ["Ruins of Lordaeron", "Undercity", "15-20", "Blizzard"],
    ["Wetlands Dig Site", "Wetlands", "24-29", "Warcraft Wiki"],
    ["Dalaran", "Alterac Mountains", "28-33", "Warcraft Wiki"],
    ["The Drowned City", "Stranglethorn Vale", "35-40", "Warcraft Wiki"],
    ["Krol'dok Stronghold", "Riverglades", "40-45", "Warcraft Wiki"],
    ["Alcaz Prison", "Dustwallow Marsh", "48-53", "Warcraft Wiki"],
    ["Blackmaw Hold", "Azshara", "55-60", "Warcraft Wiki"],
    ["Shaper's Terrace", "Un'Goro Crater", "58-60", "Warcraft Wiki"],
]

PAGES_EN = {
    "": {
        "title": "WoW: Forever: release, beta, editions | BrokenMeta.gg",
        "description": "World of Warcraft: Forever launches November 4, 2026. Beta, editions, classes, dungeons and schedule, with official sources cited.",
        "kicker": "World of Warcraft: Forever",
        "h1": "World of Warcraft: Forever: everything to know before launch",
        "intro": "Blizzard's new WoW launches on November 4, 2026 and its beta is open. This section gathers what is confirmed: dates, beta access, editions, classes, dungeons and schedule. Every fact points to its source, and anything from a community wiki or a single source is flagged as such.",
        "sections": [
            {"h2": "The essentials", "blocks": [
                {"type": "facts", "items": [
                    ("Launch", "November 4, 2026, 3:00 p.m. (Pacific time)"),
                    ("Beta", "September 17 to October 21, 2026"),
                    ("Level cap", "60"),
                    ("Announced content", "over 1,000 quests, nine dungeons, two raids"),
                    ("New race", "the Skyborne"),
                    ("Access", "included with a WoW subscription or game time"),
                ]},
                {"type": "p", "text": "World of Warcraft: Forever is a separate branch of the game that runs alongside modern WoW and WoW Classic. It is set during WoW's first year, in a continuity separate from the modern version, and keeps the level cap at 60. Where Classic recreates the original game, Forever expands the original Azeroth with new content (source: Wikipedia)."},
            ]},
            {"h2": "Key dates", "blocks": [
                {"type": "table", "head": ["Date", "Event", "Source"], "rows": EN_DATES},
                {"type": "note", "text": "The beta and launch dates come from Blizzard's announcements; the September 17 beta opening is also given by Wikipedia and Icy Veins. Icy Veins lists the beta ending on October 22: we use October 21, the date Blizzard gives."},
            ]},
            {"h2": "What has been announced", "blocks": [
                {"type": "list", "items": [
                    "A new race, the Skyborne, with the Zephras Isle starting zone (Blizzard).",
                    "Three new zones: Mount Hyjal, Zephras Isle and Riverglades (Icy Veins, Wikipedia).",
                    "Over 1,000 new quests, nine dungeons and two raids (Wikipedia).",
                    "New race-class combinations, including Forsaken Paladins and Dwarf Shamans (Wikipedia).",
                    "A new battleground, the Darkspear Islands (Icy Veins, Warcraft Wiki).",
                    "An opt-in transmog system and an SD/HD character-model toggle (Icy Veins).",
                ]},
            ]},
            {"h2": "Go further", "blocks": [
                {"type": "cards", "items": [
                    ("sortie", "Release date", "Launch day and time, converted to your time zone."),
                    ("beta", "The beta", "How to get in, what you can do and up to which level."),
                    ("editions", "Editions & prices", "What each pack contains, and what the subscription includes."),
                    ("classes", "Classes & races", "Classes, races and the new combinations."),
                    ("progression", "Leveling 1-60", "Dungeons by level range, zones and raids."),
                    ("faq", "FAQ", "Answers to the most common questions."),
                ]},
            ]},
        ],
        "sources": ["blizz_beta", "blizz_pre", "wikipedia", "icyveins", "warcraftwiki"],
    },
    "sortie": {
        "title": "WoW: Forever release date: November 4, 2026",
        "description": "WoW: Forever launches November 4, 2026 at 3 p.m. Pacific time, midnight in Paris. Launch time, early access and announced schedule.",
        "kicker": "World of Warcraft: Forever · Release",
        "h1": "WoW: Forever release date",
        "intro": "Blizzard has set the worldwide launch of World of Warcraft: Forever for November 4, 2026 at 3:00 p.m. Pacific time.",
        "sections": [
            {"h2": "Launch time in your time zone", "blocks": [
                {"type": "table", "head": ["Time zone", "Launch date and time"], "rows": [
                    ["Pacific time (PST, US)", "Wednesday, November 4, 2026, 3:00 p.m. (Blizzard's figure)"],
                    ["UTC / London time", "Wednesday, November 4, 2026, 11:00 p.m."],
                    ["Paris time (CET)", "Thursday, November 5, 2026, 12:00 a.m. (overnight from the 4th to the 5th)"],
                ]},
                {"type": "note", "text": "Only the Pacific time comes from Blizzard. The other two rows are our conversion: daylight saving ends on October 25 in France and November 1 in the US, so Paris is 9 hours ahead of the US west coast on that date."},
            ]},
            {"h2": "Do you need to buy the game?", "blocks": [
                {"type": "p", "text": "No. According to Blizzard, World of Warcraft: Forever is available with an existing WoW subscription or game time, with no separate purchase. The Skyborne packs are optional: they unlock the new race, cosmetics and, for some, the beta. Details are on the Editions & prices page."},
            ]},
            {"h2": "Before launch", "blocks": [
                {"type": "list", "items": [
                    "September 17 to October 21: the beta, with a level cap of 20 in week one and 30 afterwards.",
                    "October 27 to November 3: early character name reservation (up to 3) for holders of the Skyborne Heroic Pack or higher.",
                    "From October 20: Invite-A-Friend codes emailed, valid November 4 to 11.",
                ]},
            ]},
            {"h2": "After launch: the announced schedule", "blocks": [
                {"type": "list", "items": [
                    "December 9, 2026: raid unlock for Barrow Deeps (10-player), Hyjal Summit (20-player) and Onyxia's Lair (40-player).",
                    "Spring 2027: two more raids, one 10-player and one 20-player.",
                    "Summer 2027: a revamped iconic raid and a new raid.",
                    "Hardcore mode is announced for \"sometime between 2026 and 2027\", with no exact date.",
                ]},
                {"type": "note", "text": "This schedule comes only from Icy Veins. Blizzard did not repeat it in the announcements we consulted: treat it as provisional."},
            ]},
        ],
        "sources": ["blizz_pre", "blizz_beta", "icyveins", "wikipedia"],
    },
    "beta": {
        "title": "WoW: Forever beta: access, dates and level cap",
        "description": "WoW: Forever beta from September 17 to October 21, 2026: how to get access, level 20 then 30, playable content and how to check your license.",
        "kicker": "World of Warcraft: Forever · Beta",
        "h1": "The WoW: Forever beta",
        "intro": "The World of Warcraft: Forever beta began on September 17, 2026 and ends on October 21. Here is how to get in and what you can do.",
        "sections": [
            {"h2": "At a glance", "blocks": [
                {"type": "facts", "items": [
                    ("Opens", "September 17, 2026"),
                    ("Ends", "October 21, 2026"),
                    ("Level cap, week 1", "20"),
                    ("Level cap, afterwards", "30"),
                    ("Character", "a new test character is required"),
                ]},
            ]},
            {"h2": "How to get beta access", "blocks": [
                {"type": "list", "items": [
                    "Sign up on the game's official page with your Battle.net account. Signing up gives you a chance to be picked, not a guarantee: invitations go out regularly throughout the test.",
                    "Buy the Skyborne Epic Pack or the Warcraft Forever Collection, which include beta access. The Skyborne Heroic Pack does not.",
                    "Be among Blizzard's invitees: community veterans, press, fansites, friends and family.",
                ]},
                {"type": "p", "text": "To check your access, look in your Battle.net account for the \"World of Warcraft: Forever beta license\". Pack buyers may wait up to 30 minutes for it to appear."},
            ]},
            {"h2": "What you can do in the beta", "blocks": [
                {"type": "list", "items": [
                    "Create a new test character: existing characters do not carry over.",
                    "Week 1: level cap 20, with the new Skyborne race and the Zephras Isle zone, plus the Hall of Thanes (levels 13 to 18) and Ruins of Lordaeron (levels 15 to 20) dungeons.",
                    "Afterwards: level cap 30, with content suited to those levels.",
                    "Later in the beta: a \"Server Slam\" is announced, with no exact date yet.",
                ]},
                {"type": "note", "text": "In the Blizzard announcements we consulted, server regions and what carries over at launch are not specified."},
            ]},
        ],
        "sources": ["blizz_beta", "blizz_pre", "pcgamer", "wikipedia"],
    },
    "editions": {
        "title": "WoW: Forever editions and prices: Skyborne packs",
        "description": "Skyborne Heroic Pack, Epic Pack and Warcraft Forever Collection: what each edition contains, beta access, prices reported by the press, limited offer.",
        "kicker": "World of Warcraft: Forever · Editions",
        "h1": "WoW: Forever editions and prices",
        "intro": "The game is included with a WoW subscription. Three optional packs add the Skyborne race, cosmetics and, for two of them, beta access.",
        "sections": [
            {"h2": "The base game", "blocks": [
                {"type": "p", "text": "World of Warcraft: Forever is available with an existing WoW subscription or game time, with no separate purchase (Blizzard). The packs below are optional."},
            ]},
            {"h2": "Comparing the three packs", "blocks": [
                {"type": "table", "head": ["", "Skyborne Heroic Pack", "Skyborne Epic Pack", "Warcraft Forever Collection"], "rows": [
                    ["Skyborne race and Zephras Isle start", "Yes", "Yes", "Yes"],
                    ["Beta access from September 17", "No", "Yes", "Yes"],
                    ["30 days of game time from November 4", "No", "Yes", "Yes"],
                    ["Early name reservation (Oct 27 - Nov 3)", "Yes, 3 characters", "Yes", "Yes"],
                    ["Invite-A-Friend codes", "1", "3", "3"],
                    ["Warcraft III: Reforged and Forsaken Kingdom campaign", "No", "No", "Yes"],
                    ["Price reported by the press (US)", "not reported", "$59.99", "$79.99"],
                ]},
                {"type": "note", "text": "Prices do not appear in the Blizzard announcements we consulted, which point to the Battle.net shop. The dollar amounts come from the press (PC Gamer): check them in the shop before buying. Euro prices are not known here."},
            ]},
            {"h2": "What the Skyborne Heroic Pack contains", "blocks": [
                {"type": "list", "items": [
                    "Access to the Skyborne race and its Zephras Isle starting experience.",
                    "Early name reservation for 3 characters, October 27 to November 3.",
                    "A ground mount, the Cerulean Prideclaw.",
                    "A cosmetic, the Shen'dorei Skyseer's Garb, a Veteran Adventurer's Rucksack and a Shen'dorei Windwell toy.",
                    "Skyborne housing decor items.",
                    "One Invite-A-Friend launch code.",
                ]},
            ]},
            {"h2": "What the higher packs add", "blocks": [
                {"type": "list", "items": [
                    "Skyborne Epic Pack: everything in the Heroic Pack, plus beta access from September 17, 30 days of game time added from November 4, more cosmetics, tabards and pets, and two more Invite-A-Friend codes (3 in total).",
                    "Warcraft Forever Collection: everything in the Epic Pack, plus Warcraft III: Reforged, the Warcraft III Reforged: Forsaken Kingdom campaign and a Forsaken and Human figurine decor item. A limited-time bundle, available through January 11, 2027.",
                ]},
                {"type": "p", "text": "Invite-A-Friend codes are emailed from October 20, 2026 and are valid from November 4 to 11. They do not include beta access."},
            ]},
        ],
        "sources": ["blizz_pre", "blizz_beta", "pcgamer"],
    },
    "classes": {
        "title": "WoW: Forever classes and races: combinations",
        "description": "The nine classes, the races and the new Skyborne race in WoW: Forever, with the announced new race-class combinations and their sources.",
        "kicker": "World of Warcraft: Forever · Classes & races",
        "h1": "WoW: Forever classes and races",
        "intro": "Here is what is known about the classes and races of World of Warcraft: Forever. Blizzard has not yet detailed the classes one by one: this page sticks to what is sourced.",
        "sections": [
            {"h2": "The classes", "blocks": [
                {"type": "p", "text": "According to the Warcraft Wiki (a community source), the game has nine classes: Druid, Hunter, Mage, Paladin, Priest, Rogue, Shaman, Warlock and Warrior. Class talents are rebalanced so that more choices are viable (same source)."},
                {"type": "note", "text": "Icy Veins only mentions \"additional race/class combinations\" without naming classes. No official source we consulted details the classes one by one, so we are not writing specialization guides at this stage."},
            ]},
            {"h2": "The races", "blocks": [
                {"type": "list", "items": [
                    "The original WoW races: Human, Dwarf, Night Elf and Gnome for the Alliance; Orc, Undead (Forsaken), Tauren and Troll for the Horde (Warcraft Wiki).",
                    "A new race, the Skyborne, available with the Skyborne packs (Blizzard, Wikipedia). Their starting zone is Zephras Isle.",
                ]},
                {"type": "note", "text": "The Warcraft Wiki does not clearly say which faction the Skyborne belong to, and Blizzard does not specify it in the announcements we consulted: we do not claim it."},
            ]},
            {"h2": "New race-class combinations", "blocks": [
                {"type": "p", "text": "Wikipedia cites Forsaken Paladins and Dwarf Shamans, two combinations absent from the original game. The Warcraft Wiki lists more, but its list mixes in combinations already present in WoW Classic, so we are not repeating it until it is confirmed."},
            ]},
        ],
        "sources": ["wikipedia", "warcraftwiki", "icyveins", "blizz_pre"],
    },
    "progression": {
        "title": "Leveling 1-60 in WoW: Forever: dungeons and zones",
        "description": "WoW: Forever dungeons by level range, the new zones, raids and schedule. What is sourced for leveling from 1 to 60.",
        "kicker": "World of Warcraft: Forever · Leveling",
        "h1": "Leveling from 1 to 60 in WoW: Forever",
        "intro": "The level cap stays at 60. This page gathers what is known to plan your leveling: dungeons by level range, new zones and raids. A full quest route will follow after launch, once it can be verified.",
        "sections": [
            {"h2": "The nine dungeons, by level", "blocks": [
                {"type": "table", "head": ["Dungeon", "Location", "Levels", "Source"], "rows": EN_DUNGEONS},
                {"type": "note", "text": "Blizzard confirms the first two dungeons and their levels. The other seven come from the Warcraft Wiki (a community source): to be confirmed at launch."},
            ]},
            {"h2": "The new zones", "blocks": [
                {"type": "list", "items": [
                    "Zephras Isle: the Skyborne starting zone, playable from the beta (Blizzard).",
                    "Mount Hyjal and Riverglades: two more announced new zones (Icy Veins, Wikipedia).",
                ]},
            ]},
            {"h2": "The raids", "blocks": [
                {"type": "list", "items": [
                    "The Barrow Deeps: a 10-player raid (Warcraft Wiki, Icy Veins).",
                    "Hyjal Summit: a 20-player raid (Warcraft Wiki, Icy Veins).",
                    "Onyxia's Lair: a 40-player raid, named in the December 9, 2026 unlock (Icy Veins).",
                ]},
                {"type": "p", "text": "The schedule for the later raids, in spring and summer 2027, is on the Release page."},
            ]},
            {"h2": "During the beta", "blocks": [
                {"type": "p", "text": "The beta caps at level 20 in the first week, then level 30. It lets you test Zephras Isle and the first two dungeons, but not the climb to 60."},
            ]},
        ],
        "sources": ["blizz_beta", "warcraftwiki", "icyveins", "wikipedia"],
    },
    "faq": {
        "title": "WoW: Forever FAQ: release, beta, price, differences",
        "description": "Answers about WoW: Forever: release date, beta access, buying, level cap, differences from WoW Classic. Sources cited.",
        "kicker": "World of Warcraft: Forever · FAQ",
        "h1": "FAQ: World of Warcraft: Forever",
        "intro": "The most common questions about World of Warcraft: Forever, answered from official announcements and cited sources.",
        "faq": [
            ("What is World of Warcraft: Forever?",
             "A separate branch of World of Warcraft that runs alongside modern WoW and WoW Classic. It is set during the game's first year, in a separate continuity, and expands the original Azeroth with new content while keeping the level cap at 60."),
            ("When does WoW: Forever launch?",
             "On November 4, 2026 at 3:00 p.m. Pacific time, according to Blizzard. That is midnight in Paris, overnight from November 4 to 5."),
            ("Do I need to buy the game?",
             "No. It is available with an existing WoW subscription or game time. The Skyborne packs are optional."),
            ("How do I get into the beta?",
             "By signing up on the official page with your Battle.net account, which gives you a chance to be picked, or by buying the Skyborne Epic Pack or the Warcraft Forever Collection. The beta runs from September 17 to October 21, 2026."),
            ("Up to what level can I play in the beta?",
             "Level 20 in the first week, then level 30 later in the beta."),
            ("Do beta characters carry over?",
             "Blizzard asks you to create a new test character: existing characters do not carry over. The announcements we consulted do not say what carries over at launch."),
            ("What is the level cap?",
             "60, kept long-term: progression comes through new activities, stories, abilities and systems rather than extra levels."),
            ("How does it differ from WoW Classic?",
             "Classic recreates the original game. Forever extends it: over 1,000 new quests, nine dungeons, two raids, a new race and new race-class combinations."),
            ("Is Hardcore mode planned?",
             "Icy Veins announces it \"sometime between 2026 and 2027\", with no exact date."),
            ("Is BrokenMeta.gg affiliated with Blizzard?",
             "No. It is an independent site that cites its sources and flags what is not confirmed."),
        ],
        "sections": [],
        "sources": ["blizz_pre", "blizz_beta", "wikipedia", "icyveins", "pcgamer"],
    },
}

PAGES = {"fr": PAGES_FR, "en": PAGES_EN}

UI = {
    "fr": {"sources": "Sources", "sources_note": "Informations vérifiées le 20 septembre 2026. Les points qui ne viennent que d'un wiki communautaire ou d'une seule source sont signalés dans le texte.",
           "countdown": "Sortie dans", "days": "jours", "hours": "heures", "minutes": "minutes", "seconds": "secondes", "live": "Le jeu est sorti !",
           "launch_line": "Lancement le 4 novembre 2026, 15 h (heure du Pacifique) — minuit à Paris",
           "breadcrumb_home": "Accueil", "section": "World of Warcraft: Forever", "beta_cta": "Accéder à la bêta"},
    "en": {"sources": "Sources", "sources_note": "Information checked on September 20, 2026. Points that only come from a community wiki or a single source are flagged in the text.",
           "countdown": "Launch in", "days": "days", "hours": "hours", "minutes": "minutes", "seconds": "seconds", "live": "The game is out!",
           "launch_line": "Launching November 4, 2026, 3:00 p.m. Pacific time — midnight in Paris",
           "breadcrumb_home": "Home", "section": "World of Warcraft: Forever", "beta_cta": "Get beta access"},
}


def check() -> None:
    """Fail loudly on SEO length limits and structural slips (run by the build)."""
    for lang, pages in PAGES.items():
        assert set(pages) == {slug for slug, _, _ in NAV}, lang
        for slug, p in pages.items():
            assert len(p["title"]) <= 60, (lang, slug, len(p["title"]))
            assert len(p["description"]) <= 155, (lang, slug, len(p["description"]))
            for key in p["sources"]:
                assert key in SOURCES, key
            for sec in p["sections"]:
                for b in sec["blocks"]:
                    assert b["type"] in {"p", "list", "table", "facts", "note", "cards"}, b["type"]
    assert len(PAGES["fr"]["faq"]["faq"]) == len(PAGES["en"]["faq"]["faq"])
