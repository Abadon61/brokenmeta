"""Compléments rédigés pour les guides les plus courts : forces, faiblesses, rôle en combat d'équipe, combos en plus.
Toujours d'après les textes officiels des capacités (Data Dragon)."""

EXTRA = {
    "Nilah": {
        "strengths": [
            "Gagne plus d'expérience sur les sbires (passive) et partage les soins et boucliers des alliés proches.",
            "Voile de liesse lui fait esquiver toutes les attaques et donne le même effet aux alliés qu'elle touche.",
            "Apothéose regroupe les ennemis autour d'elle, ce qui aide les dégâts de zone de son équipe.",
        ],
        "weaknesses": [
            "Doit être au contact pour exprimer sa puissance : Lame fluide n'augmente sa portée que brièvement.",
            "Voile de liesse a un délai de récupération long (22 à 26 s) : impossible de l'utiliser en boucle.",
            "Dépend de la présence d'alliés qui soignent ou protègent pour profiter de sa passive.",
        ],
        "teamfight": (
            "Nilah est une tireuse de mêlée : elle rejoint le combat avec Torrent, place Voile de liesse pour rendre son équipe insensible aux attaques pendant la brume, "
            "puis Apothéose attire les ennemis vers elle. Elle est meilleure quand ses alliés la soignent ou la protègent, car elle renforce et partage ces effets."
        ),
        "combos": [
            {"name": "L'engagement avec le voile", "keys": ["W", "E", "Q", "AA"], "when": "Ton équipe s'engage sur des attaques de base ennemies.",
             "how": "Voile de liesse augmente ta vitesse de déplacement et t'évite toutes les attaques ; Torrent te rue sur la cible en blessant sur ton chemin ; Lame fluide augmente ta portée d'attaque."},
        ],
    },
    "Fiddlesticks": {
        "strengths": [
            "Terreur fait fuir un ennemi quand tu le blesses sans être visible : un engagement très surprenant.",
            "Rafale de corbeaux inflige des dégâts par seconde à toutes les unités ennemies dans la zone.",
            "Fauchaison ralentit tous les ennemis touchés et réduit au silence ceux du centre.",
        ],
        "weaknesses": [
            "Dépend de l'invisibilité : un ennemi qui révèle ta position te fait perdre l'effet de Terreur.",
            "Moisson fructueuse et Rafale de corbeaux demandent de rester dans la zone pendant qu'ils agissent.",
            "Peu de mobilité une fois engagé : sans effet de surprise, tu es exposé.",
        ],
        "teamfight": (
            "Fiddlesticks entre dans le combat par surprise, depuis un buisson ou une zone sans vision, puis enchaîne Terreur, Fauchaison et Rafale de corbeaux au milieu des ennemis. "
            "Son ultime fait de lui une source de dégâts constante tant qu'il n'est pas interrompu : son équipe doit protéger sa canalisation."
        ),
        "combos": [
            {"name": "L'engagement de combat d'équipe", "keys": ["R", "E", "Q", "W"], "when": "Ton équipe est prête et les ennemis sont regroupés.",
             "how": "Rafale de corbeaux crée une zone de dégâts par seconde, Fauchaison ralentit et réduit au silence au centre, Terreur et Moisson fructueuse ajoutent contrôle et dégâts d'exécution."},
        ],
    },
    "Renata": {
        "strengths": [
            "Ses attaques marquent les ennemis et ses alliés leur infligent des dégâts supplémentaires.",
            "Patronage retarde la mort d'un allié et lui permet de survivre s'il participe à une élimination.",
            "Prise de contrôle hostile retourne les ennemis les uns contre les autres.",
        ],
        "weaknesses": [
            "Dépend de la présence d'alliés pour bénéficier de ses marques.",
            "Poignée de main a un délai de récupération long (16 s) et se lance à l'aveugle.",
            "Patronage a un délai de récupération de 24 à 28 s : choisis bien l'allié.",
        ],
        "teamfight": (
            "Renata contrôle l'engagement : elle immobilise un ennemi ou l'envoie vers ses alliés, protège son carry avec Patronage et Programme de fidélité, "
            "puis déclenche Prise de contrôle hostile quand les ennemis sont regroupés. Ses marques font grimper les dégâts de ses alliés sur la cible."
        ),
        "combos": [
            {"name": "Le combat d'équipe", "keys": ["R", "E", "W", "Q"], "when": "Les ennemis se regroupent sur ton carry.",
             "how": "Prise de contrôle hostile rend fous furieux les ennemis touchés, Programme de fidélité protège et ralentit, Patronage prolonge la vie d'un allié clé, Poignée de main immobilise une menace."},
        ],
    },
    "Neeko": {
        "strengths": [
            "Son déguisement lui permet d'approcher sans être identifiée, et la préparation de son ultime est invisible tant qu'elle est déguisée.",
            "Spirale épineuse immobilise plusieurs ennemis et grossit si elle traverse un champion ou tue.",
            "Floraison renversante projette puis étourdit tous les ennemis proches.",
        ],
        "weaknesses": [
            "Le déguisement se rompt si elle est immobilisée, lance une compétence offensive ou subit assez de dégâts.",
            "Ses compétences ont des délais de récupération longs (Métaclonage 16 s, Floraison 120 s).",
            "Fragile : sans son engagement, elle n'a pas d'échappatoire.",
        ],
        "teamfight": (
            "Neeko approche déguisée, lance son ultime pour projeter et étourdir tous les ennemis proches, puis immobilise les fuyards avec Spirale épineuse. "
            "Un seul engagement réussi peut décider le combat, mais elle n'a pas de seconde chance si l'ultime est raté."
        ),
        "combos": [
            {"name": "Le piège déguisé", "keys": ["R", "E", "Q", "AA"], "when": "Tu es déguisée en allié et les ennemis sont regroupés.",
             "how": "Floraison renversante : sa préparation ne se voit pas déguisée ; les ennemis proches sont projetés en l'air puis blessés et étourdis à l'atterrissage ; enchaîne Spirale épineuse et Explosion florale."},
        ],
    },
    "Lillia": {
        "strengths": [
            "Ses compétences infligent des dégâts sur la durée selon les PV max des cibles touchées.",
            "Frappe fleurie lui donne de la vitesse de déplacement cumulable pour poursuivre ou fuir.",
            "Douce berceuse endort les ennemis affectés par Poussière de rêve, avec des dégâts supplémentaires s'ils sont réveillés de force.",
        ],
        "weaknesses": [
            "Doit toucher avec ses compétences pour cumuler sa vitesse et sa Poussière de rêve.",
            "Attention, désolée ! inflige ses gros dégâts au centre : un mauvais placement les réduit.",
            "Son ultime est inutile sans ennemis affectés par sa passive.",
        ],
        "teamfight": (
            "Lillia entre en combat en courant, applique sa Poussière de rêve avec ses compétences, puis lance Douce berceuse pour endormir tous les ennemis marqués. "
            "Son équipe doit éviter de réveiller trop tôt les cibles endormies, sauf pour profiter des dégâts supplémentaires."
        ),
        "combos": [
            {"name": "La course de zone", "keys": ["Q", "E", "W", "Q"], "when": "Tu veux courir vers un groupe d'ennemis.",
             "how": "Frappe fleurie cumule de la vitesse quand tes compétences touchent, Graine tournoyante ralentit, Attention, désolée ! frappe au centre, puis Frappe fleurie active blesse en zone."},
        ],
    },
    "Trundle": {
        "strengths": [
            "Récupère des PV quand un ennemi meurt près de lui, et se soigne beaucoup dans son Royaume gelé.",
            "Morsure ralentit et draine les dégâts d'attaque de sa cible : très efficace contre un carry en mêlée.",
            "Soumission vole immédiatement des PV, de l'armure et de la résistance magique, puis double le montant en 4 secondes.",
        ],
        "weaknesses": [
            "Dépend de rester dans son Royaume gelé pour ses bonus.",
            "Peu d'engagement à distance : il doit rejoindre sa cible.",
            "Montagne de glace ne sert que si le terrain s'y prête.",
        ],
        "teamfight": (
            "Trundle choisit une cible, la neutralise avec Morsure et Soumission, et utilise Montagne de glace pour bloquer un passage ou séparer les ennemis. "
            "Il se bat mieux dans son Royaume gelé, où ses vitesses et ses soins augmentent."
        ),
        "combos": [
            {"name": "Le duel d'attrition", "keys": ["W", "Q", "AA", "R"], "when": "Un carry en mêlée est à portée.",
             "how": "Royaume gelé augmente tes vitesses et soins, Morsure draine ses dégâts d'attaque, Soumission vole une partie de ses PV, de son armure et de sa résistance magique, doublée en 4 secondes."},
        ],
    },
    "Belveth": {
        "strengths": [
            "Sa vitesse d'attaque augmente définitivement avec les grands monstres, grands sbires et champions tués.",
            "Maelström impérial lui donne du vol de vie et de la réduction de dégâts tout en frappant l'ennemi qui a le moins de PV.",
            "Sa forme finale (Banquet infini) augmente ses PV max, sa portée et sa vitesse d'attaque.",
        ],
        "weaknesses": [
            "Maelström impérial l'immobilise pendant sa canalisation.",
            "Sa puissance dépend d'une bonne progression de jungle.",
            "Son ultime dépend du corail du Néant à collecter.",
        ],
        "teamfight": (
            "Bel'Veth entre en combat avec Charge du Néant, projette avec Projection cinglante, puis canalise Maelström impérial au milieu des ennemis pour profiter du vol de vie et de la réduction de dégâts. "
            "Elle est la plus dangereuse quand elle a pris sa forme finale."
        ),
        "combos": [
            {"name": "L'entrée en combat", "keys": ["Q", "W", "E", "AA"], "when": "Les ennemis sont regroupés.",
             "how": "Charge du Néant te rue en blessant tous les ennemis traversés, Projection cinglante projette et ralentit, Maelström impérial canalise une tempête de coups autour de toi."},
        ],
    },
    "Kennen": {
        "strengths": [
            "Étourdit les ennemis touchés trois fois avec ses compétences (Marque de tempête).",
            "Rush foudroyant lui donne de la vitesse et lui permet de traverser les unités en appliquant des marques.",
            "Maelström frappe tous les champions ennemis proches avec des dégâts magiques.",
        ],
        "weaknesses": [
            "Limité par son énergie : ses compétences se répètent moins vite qu'un mage à mana.",
            "Doit s'approcher pour utiliser Maelström.",
            "Fragile quand il n'a pas d'étourdissement prêt.",
        ],
        "teamfight": (
            "Kennen entre avec Rush foudroyant pour appliquer des marques sur plusieurs ennemis à la fois, complète avec Shuriken et Surtension pour déclencher les étourdissements, "
            "puis lance Maelström pour finir. Son rôle est de contrôler plusieurs cibles avec une seule série de marques."
        ),
        "combos": [
            {"name": "La série de marques", "keys": ["E", "W", "Q", "R"], "when": "Plusieurs ennemis sont proches.",
             "how": "Rush foudroyant applique une marque à chaque ennemi traversé, Surtension et Shuriken foudroyant en ajoutent : à trois marques, ils sont étourdis ; Maelström frappe ensuite les champions proches."},
        ],
    },
    "Vex": {
        "strengths": [
            "Sa passive effraie et interrompt les ruées : c'est une réponse directe aux assassins et aux engagements.",
            "Chaque ruée ennemie lui donne une marque qui inflige des dégâts supplémentaires et réduit le délai de son renforcement.",
            "Déferlement d'Ombre marque à distance et se réactive pour se ruer sur la cible.",
        ],
        "weaknesses": [
            "Contre les champions sans ruée, elle profite moins de ses marques.",
            "Son renforcement est périodique : le gaspiller a un coût.",
            "Fragile face aux burst rapides si son bouclier n'est pas prêt.",
        ],
        "teamfight": (
            "Vex protège son équipe des engagements : sa compétence renforcée effraie l'ennemi qui plonge, Lâchez-moi ! lui donne un bouclier, et Déferlement d'Ombre lui permet de finir un carry marqué. "
            "Elle est très efficace face aux compositions qui reposent sur des ruées."
        ),
        "combos": [
            {"name": "La riposte à l'engagement", "keys": ["W", "Q", "E", "R"], "when": "Un ennemi plonge sur toi ou ton carry.",
             "how": "Lâchez-moi ! te donne un bouclier et blesse les ennemis proches, ta compétence renforcée effraie et interrompt la ruée, Ténèbres imminentes ralentit et applique Désespoir."},
        ],
    },
    "Annie": {
        "strengths": [
            "Étourdit après 4 compétences utilisées, et commence chaque vie avec sa passive prête.",
            "Tibbers inflige des dégâts en zone et continue de brûler les ennemis proches.",
            "Bouclier en fusion protège un allié et blesse ceux qui l'attaquent.",
        ],
        "weaknesses": [
            "Doit lancer 4 compétences pour rendre l'étourdissement disponible.",
            "Courte portée de la plupart de ses compétences : elle doit s'approcher.",
            "Tibbers est son ultime : sans lui, le burst diminue.",
        ],
        "teamfight": (
            "Annie prépare son étourdissement avec 4 compétences avant le combat, puis lance Tibbers sur le groupe ennemi pour le faire suivre d'un étourdissement. "
            "Elle protège aussi son carry avec Bouclier en fusion, qui blesse les attaquants."
        ),
        "combos": [
            {"name": "L'ouverture de combat d'équipe", "keys": ["E", "W", "R", "Q"], "when": "Ta passive est prête (4 compétences déjà utilisées).",
             "how": "Bouclier en fusion te protège, Incinération blesse en cône, Tibbers (avec l'étourdissement de ta passive) atterrit sur le groupe, Désintégration finit."},
        ],
    },
    "Aurora": {
        "strengths": [
            "Se soigne grâce aux esprits exorcisés des ennemis qu'elle blesse.",
            "Derrière le voile la rend invisible et accélère un bref instant.",
            "Entre les mondes blesse et ralentit, puis crée une zone où elle peut se téléporter d'un bord à l'autre.",
        ],
        "weaknesses": [
            "Sortilège la fait bondir en arrière : sa position finale est moins agressive.",
            "Maléfice demande une relance pour être pleinement efficace.",
            "Beaucoup de délais de récupération longs : ses combos sont espacés.",
        ],
        "teamfight": (
            "Aurora joue à distance, place Maléfice sur plusieurs cibles, puis relance pour attirer les maléfices. "
            "Son ultime crée une zone de ralentissement dans laquelle elle se téléporte librement : elle se repositionne dans le combat sans jamais s'exposer inutilement."
        ),
        "combos": [
            {"name": "Le combo de zone", "keys": ["R", "Q", "E", "Q"], "when": "Un groupe d'ennemis approche.",
             "how": "Entre les mondes libère une onde de choc et crée une zone qui ralentit ; Maléfice maudit les ennemis, Sortilège ralentit puis te met à l'abri, relance Maléfice pour attirer les maléfices actifs."},
        ],
    },
    "Gangplank": {
        "strengths": [
            "Les barils étendent les dégâts de ses attaques et ralentissent les ennemis autour.",
            "Guérison du scorbut dissipe les effets de contrôle et le soigne.",
            "Tir de barrage bombarde une zone à grande distance en ralentissant et blessant.",
        ],
        "weaknesses": [
            "Sa puissance dépend de poser et faire exploser des barils au bon moment.",
            "Guérison du scorbut a un délai de récupération long (14 à 22 s).",
            "Peu de mobilité pour se dégager quand ses barils sont détruits.",
        ],
        "teamfight": (
            "Gangplank prépare le terrain avec des barils, lance Tir de barrage pour ralentir et blesser une zone entière, "
            "puis fait exploser les barils autour des ennemis. Il utilise Guérison du scorbut pour survivre à un contrôle décisif."
        ),
        "combos": [
            {"name": "Le baril sous barrage", "keys": ["E", "R", "AA", "Q"], "when": "Les ennemis sont dans une zone étroite.",
             "how": "Pose un baril, Tir de barrage ralentit et blesse la zone, une attaque sur le baril étend les dégâts et ralentit, Pourparlers achève en gagnant de l'or."},
        ],
    },
    "MonkeyKing": {
        "strengths": [
            "Gagne de l'armure et de la régénération en combat avec des champions ou des monstres.",
            "Guerrier espiègle le rend invisible et laisse un clone qui attaque à sa place.",
            "Cyclone augmente sa vitesse de déplacement et projette les ennemis touchés en l'air.",
        ],
        "weaknesses": [
            "Doit s'approcher : Nimbus est son principal engagement.",
            "Guerrier espiègle a un délai de récupération long (18 à 22 s).",
            "Son ultime ne sert que si les ennemis restent à portée du bâton.",
        ],
        "teamfight": (
            "Wukong entre en combat par surprise avec Guerrier espiègle (invisible, clone laissé derrière lui), se rue avec Nimbus sur la cible qu'il a choisie et lance Cyclone pour projeter les ennemis en l'air. "
            "Il est particulièrement efficace pour isoler un carry."
        ),
        "combos": [
            {"name": "L'entrée invisible", "keys": ["W", "E", "R", "Q"], "when": "Un carry est dans la mêlée adverse.",
             "how": "Guerrier espiègle te rend invisible et laisse un clone, Nimbus te rue sur la cible avec des images qui attaquent ses voisins, Cyclone augmente ta vitesse et projette en l'air, Écrasement réduit l'armure."},
        ],
    },
    "Heimerdinger": {
        "strengths": [
            "Ses tourelles infligent des dégâts continus et aident à contrôler une zone ou une lane.",
            "Grenade électro-tempête CH-2 étourdit les unités touchées directement et ralentit celles proches.",
            "AMÉLIORATION ! augmente les effets de son prochain sort.",
        ],
        "weaknesses": [
            "Sa puissance dépend de ses tourelles : loin d'elles, il est vulnérable.",
            "Peu mobile en dehors de sa vitesse près des tourelles.",
            "Grenade et Micro-roquettes ont des délais de récupération longs.",
        ],
        "teamfight": (
            "Heimerdinger transforme un couloir ou un objectif en zone défendue : tourelles posées à l'avance, Grenade électro-tempête pour étourdir, Micro-roquettes pour la portée. "
            "AMÉLIORATION ! sur la compétence adaptée décide souvent le combat."
        ),
        "combos": [
            {"name": "La défense d'objectif", "keys": ["Q", "Q", "R", "E", "W"], "when": "Ton équipe défend un point.",
             "how": "Déploie deux tourelles, AMÉLIORATION ! renforce ta prochaine compétence, Grenade électro-tempête étourdit et ralentit, Micro-roquettes convergent vers ton curseur."},
        ],
    },
    "TahmKench": {
        "strengths": [
            "Ses dégâts augmentent avec ses PV totaux, ce qui le rend efficace en tank.",
            "Coup de langue applique Goût acquis : à 3 effets, il étourdit.",
            "Dévoration protège un allié en le mettant à l'abri ou avale un ennemi affecté.",
        ],
        "weaknesses": [
            "Dévoration exige 3 effets de Goût acquis pour un ennemi.",
            "Peu de dégâts sans PV.",
            "Peau épaisse ne protège vraiment qu'avec des dégâts stockés à consommer.",
        ],
        "teamfight": (
            "Tahm Kench choisit entre protéger et attaquer : avaler un allié le sort d'un contrôle, avaler un ennemi le sépare de son équipe. "
            "Plongée abyssale l'aide à rejoindre la mêlée ou à en sortir."
        ),
        "combos": [
            {"name": "Le sauvetage d'allié", "keys": ["W", "R", "E"], "when": "Un allié est ciblé par un engagement.",
             "how": "Plongée abyssale te fait rejoindre l'allié, Dévoration lui octroie un bouclier pendant quelques secondes, Peau épaisse convertit tes dégâts stockés en bouclier temporaire."},
        ],
    },
    "Taric": {
        "strengths": [
            "Bénédiction stellaire soigne ses alliés selon le nombre de charges stockées.",
            "Bastion donne de l'armure et permet de lancer ses compétences depuis l'allié affecté.",
            "Lumière cosmique rend les alliés proches invulnérables un court instant.",
        ],
        "weaknesses": [
            "Lumière cosmique a un délai avant de s'activer : il faut l'anticiper.",
            "Éblouissement met du temps à agir.",
            "Ses dégâts restent faibles sans ses attaques renforcées.",
        ],
        "teamfight": (
            "Taric déclenche Lumière cosmique au bon moment pour rendre son équipe invulnérable pendant l'engagement adverse, puis enchaîne Éblouissement et attaques renforcées. "
            "Il protège surtout un allié précis grâce à Bastion."
        ),
        "combos": [
            {"name": "La fenêtre d'invulnérabilité", "keys": ["R", "E", "AA", "AA", "Q"], "when": "Un engagement adverse est prévisible.",
             "how": "Lumière cosmique se déclenche après un délai : lance-la avant le pic de dégâts ; Éblouissement étourdit après un bref délai, tes attaques renforcées chargent Bénédiction stellaire."},
        ],
    },
    "Amumu": {
        "strengths": [
            "Malédiction d'Amumu étourdit tous les ennemis proches et applique sa passive.",
            "Désespoir réduit les PV max de tous les ennemis autour de lui chaque seconde.",
            "Jet de bandelette a un très court délai de récupération pour se rapprocher.",
        ],
        "weaknesses": [
            "Désespoir consomme du mana tant qu'il est actif.",
            "A besoin d'un allié pour convertir ses étourdissements en éliminations.",
            "Peu de dégâts hors de ses effets de zone.",
        ],
        "teamfight": (
            "Amumu est un engagement de zone : Malédiction d'Amumu étourdit tous les ennemis proches, puis Désespoir retire un pourcentage de leurs PV max chaque seconde pendant que ses alliés attaquent. "
            "Sa passive fait subir des dégâts bruts supplémentaires aux ennemis maudits à chaque dégât magique."
        ),
        "combos": [
            {"name": "L'engagement de zone", "keys": ["Q", "R", "W", "E"], "when": "Plusieurs ennemis sont groupés.",
             "how": "Jet de bandelette étourdit et te rapproche, Malédiction d'Amumu emmêle les ennemis proches, Désespoir retire un pourcentage de leurs PV max, Colère réduit les dégâts physiques subis."},
        ],
    },
    "Volibear": {
        "strengths": [
            "Sa vitesse d'attaque augmente avec ses attaques et compétences, avec des dégâts magiques de zone après un moment.",
            "Tempête incarnée désactive temporairement les tourelles ennemies proches et lui donne des PV supplémentaires.",
            "Folie mutilatrice se relance pour infliger plus de dégâts et le soigner.",
        ],
        "weaknesses": [
            "Doit s'approcher pour exprimer ses dégâts.",
            "Tempête incarnée a un délai de récupération long (110 à 160 s).",
            "Ses engagements peuvent être contrôlés avant qu'il n'atteigne sa cible.",
        ],
        "teamfight": (
            "Volibear bondit sur les ennemis avec Tempête incarnée, gagne des PV supplémentaires et ralentit ceux sous lui, puis frappe avec Coup fulgurant et Folie mutilatrice. "
            "Près d'une tourelle ennemie, l'ultime la désactive, ce qui permet de plonger."
        ),
        "combos": [
            {"name": "Le plongeon sous tourelle", "keys": ["R", "Q", "W", "W", "E"], "when": "Un ennemi est protégé par une tourelle.",
             "how": "Tempête incarnée désactive temporairement les tourelles proches de son point d'atterrissage, ralentit et blesse les ennemis sous toi ; Coup fulgurant étourdit, Folie mutilatrice se relance pour soigner, Foudroiement te donne un bouclier."},
        ],
    },
}
