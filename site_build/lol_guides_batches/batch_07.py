"""Guides rédigés, lot 7. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Olaf": {"fr": {
        "playstyle": (
            "Olaf est un combattant qui devient plus dangereux à mesure qu'il perd des PV : sa passive lui donne de la vitesse d'attaque et du vol de vie selon ses PV manquants. "
            "Déchireuse lance sa hache pour blesser et réduire armure et vitesse de déplacement, Frappe sauvage inflige des dégâts bruts (y compris à lui-même), et Ragnarok l'immunise aux entraves tant qu'il attaque."
        ),
        "laning": (
            "Ramasse ta hache après Déchireuse : ça réduit son délai de récupération. "
            "Frappe sauvage te coûte des PV mais te les rend si elle tue sa cible."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "E", "W"], "when": "Un ennemi est à portée de hache.",
             "how": "Déchireuse blesse et réduit l'armure et la vitesse, ramasse la hache pour réduire son délai, Frappe sauvage inflige des dégâts bruts et Force décuplée donne vitesse d'attaque et bouclier."},
            {"name": "L'engagement d'équipe", "keys": ["R", "Q", "W", "AA"], "when": "Un combat s'engage.",
             "how": "Ragnarok te rend immunisé aux entraves aussi longtemps que tu attaques ; enchaîne avec Déchireuse et Force décuplée."},
            {"name": "La sortie de combat", "keys": ["W", "R"], "when": "Un contrôle te menace.",
             "how": "Ragnarok annule les entraves si tu continues d'attaquer, et Force décuplée te donne un bouclier."},
        ],
        "mistakes": [
            "Ne pas ramasser la hache après Déchireuse.",
            "Lancer Frappe sauvage à bas PV sans garantie de tuer.",
            "Cesser d'attaquer pendant Ragnarok : l'immunité dépend de tes attaques.",
        ],
    }},
    "Zoe": {"fr": {
        "playstyle": (
            "Zoé est une mage de burst qui joue avec la distance : les dégâts d'Astro-pong ! augmentent avec la distance parcourue en ligne droite, et Bulle soporifique endort la cible. "
            "Sa passive ajoute des dégâts après chaque compétence, Voleuse de sorts lui permet de ramasser les sorts d'invocateur et objets actifs adverses, et Bond dimensionnel la téléporte brièvement avant de la ramener."
        ),
        "laning": (
            "Envoie Astro-pong ! de loin et redirige-le en vol : plus il voyage, plus il blesse. "
            "Enchaîne compétence puis attaque pour profiter de ta passive."
        ),
        "combos": [
            {"name": "Le burst de base", "keys": ["E", "Q", "AA"], "when": "Un ennemi est à portée de Bulle.",
             "how": "Bulle soporifique endort la cible et réduit sa résistance magique ; les dégâts qui la réveillent sont doublés (jusqu'à un maximum) : frappe avec Astro-pong ! puis une attaque de passive."},
            {"name": "Le vol de sorts", "keys": ["W", "AA"], "when": "Un ennemi vient d'utiliser un sort d'invocateur.",
             "how": "Voleuse de sorts ramasse les vestiges des sorts d'invocateur et objets actifs adverses pour les utiliser toi-même ; quand tu utilises un sort d'invocateur, tu tires trois projectiles sur l'ennemi le plus proche."},
            {"name": "L'ultime de placement", "keys": ["R", "E", "Q", "R"], "when": "Tu veux frapper en sécurité.",
             "how": "Bond dimensionnel te téléporte à un endroit proche pendant 1 seconde avant de te ramener à ton point de départ : lance tes compétences depuis la position avancée."},
        ],
        "mistakes": [
            "Lancer Astro-pong ! à bout portant : il perd la majorité de ses dégâts.",
            "Réveiller la cible avec un petit dégât : les dégâts qui la réveillent sont doublés, garde le gros pour ça.",
            "Oublier que Bond dimensionnel te ramène au point de départ.",
        ],
    }},
    "Milio": {"fr": {
        "playstyle": (
            "Milio est un support-mage qui enchante ses alliés : ses compétences donnent aux alliés touchés des dégâts supplémentaires et une brûlure sur leur prochaine attaque. "
            "Chaud devant ! donne un bouclier et de la vitesse (2 charges), Feu de camp soigne et augmente la portée d'attaque, et son ultime soigne et retire les effets de contrôle."
        ),
        "laning": (
            "Ultra méga boule de feu repousse un ennemi puis retombe en cloche pour ralentir. "
            "Chaud devant ! a deux charges : utilise-en une pour ton carry et garde l'autre pour toi."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée.",
             "how": "La boule de feu repousse puis retombe pour blesser et ralentir ; Chaud devant ! sur ton carry enchante ses prochaines attaques."},
            {"name": "Le soutien", "keys": ["W", "E"], "when": "Ton équipe se bat autour d'un point.",
             "how": "Feu de camp soigne les alliés qui y entrent et augmente leur portée d'attaque ; la zone suit l'allié le plus proche du point de départ."},
            {"name": "L'ultime de soin", "keys": ["R"], "when": "Ton équipe est sous contrôle de foule.",
             "how": "Flammes vitales soignent les alliés à portée et suppriment les effets de contrôle qui les affectent."},
        ],
        "mistakes": [
            "Utiliser les deux charges de Chaud devant ! d'un coup.",
            "Lancer Feu de camp loin de tes alliés.",
            "Garder l'ultime trop longtemps quand ton équipe est déjà contrôlée.",
        ],
    }},
    "Shen": {"fr": {
        "playstyle": (
            "Shen est un tank de soutien à distance : sa passive lui donne un bouclier après chaque compétence, et son ultime offre un bouclier à un allié avant de te téléporter jusqu'à lui. "
            "Refuge spirituel bloque les attaques qui ciblent ses alliés ou lui près de sa lame, et Rush des ombres provoque les ennemis."
        ),
        "laning": (
            "Assaut crépusculaire inflige des dégâts basés sur les PV max de la cible : utilise-le pour harceler. "
            "Place la lame spirituelle pour que Refuge spirituel protège quand tu es proche."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["E", "Q", "AA", "W"], "when": "Un ennemi est à portée de provocation.",
             "how": "Rush des ombres te rue et provoque les ennemis traversés ; Assaut crépusculaire rappelle ta lame pour des dégâts basés sur les PV max ; Refuge spirituel bloque les attaques ciblées."},
            {"name": "L'ultime de sauvetage", "keys": ["R", "W"], "when": "Un allié est en danger loin de toi.",
             "how": "Soutien indéfectible offre un bouclier absorbant à un champion allié puis te téléporte jusqu'à lui : garde-le pour un allié menacé."},
            {"name": "Le harcèlement", "keys": ["Q", "AA"], "when": "Un ennemi est éloigné de ses alliés.",
             "how": "La lame ralentit les ennemis touchés quand ils s'éloignent de toi ; les attaques sont grandement renforcées si elle touche un champion."},
        ],
        "mistakes": [
            "Utiliser l'ultime sans allié à protéger.",
            "Oublier ta passive : chaque compétence te donne un bouclier.",
            "Placer Refuge spirituel loin de ta lame.",
        ],
    }},
    "Renekton": {"fr": {
        "playstyle": (
            "Renekton est un combattant de mêlée dont les attaques génèrent de la Fureur, davantage quand il lui reste peu de PV. "
            "Au-delà de 50 points de Fureur, chaque compétence est renforcée : Destruction des faibles soigne plus, Prédateur impitoyable frappe trois fois et détruit les boucliers, Tranche et coupe réduit l'armure. Dominus le rend plus résistant."
        ),
        "laning": (
            "Attaque pour générer de la Fureur, et garde 50 points pour renforcer tes compétences avant un échange. "
            "Prédateur impitoyable étourdit 0,75 seconde (1,5 s si renforcé)."
        ),
        "combos": [
            {"name": "L'échange renforcé", "keys": ["AA", "AA", "W", "Q", "E"], "when": "Tu as plus de 50 points de Fureur.",
             "how": "Prédateur impitoyable frappe trois fois, détruit les boucliers et étourdit 1,5 seconde ; Destruction des faibles et Tranche et coupe sont renforcées."},
            {"name": "L'engagement", "keys": ["E", "W", "Q", "AA"], "when": "Un ennemi est éloigné.",
             "how": "Tranche et coupe charge et blesse toutes les unités sur le chemin ; enchaîne avec l'étourdissement puis l'attaque circulaire."},
            {"name": "La forme de tyran", "keys": ["R", "W", "Q", "E"], "when": "Un combat d'équipe s'engage.",
             "how": "Dominus te donne des PV supplémentaires, blesse les ennemis autour de toi et te fait gagner périodiquement de la Fureur."},
        ],
        "mistakes": [
            "Dépenser tes compétences avant 50 points de Fureur.",
            "Utiliser Tranche et coupe sans plan de sortie.",
            "Lancer Prédateur impitoyable sur une cible sans bouclier alors que tu peux garder ta version renforcée pour une cible protégée.",
        ],
    }},
    "Kalista": {"fr": {
        "playstyle": (
            "Kalista est une tireuse qui bondit en se déplaçant pendant ses attaques : donne un ordre de déplacement pendant l'animation de l'attaque ou de Perforation pour avancer légèrement. "
            "Ses attaques plantent des lances dans les cibles, qu'elle extirpe pour ralentir et infliger des dégâts augmentés. Son ultime téléporte son pactisant auprès d'elle."
        ),
        "laning": (
            "Attaque et bondis en même temps : c'est la base de ta mobilité. "
            "Extirpation n'a pas de délai de récupération : utilise-la quand les lances plantées suffisent à tuer ou à ralentir."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["AA", "Q", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Tes attaques plantent des lances, Perforation traverse les ennemis tués, puis Extirpation extirpe les lances pour ralentir et infliger des dégâts augmentés."},
            {"name": "La reconnaissance", "keys": ["W"], "when": "Tu veux de la vision.",
             "how": "Sentinelle envoie une âme patrouiller le long d'une route en révélant la zone devant elle ; elle inflige aussi des dégâts supplémentaires quand toi et ton pactisant frappez la même cible."},
            {"name": "L'ultime", "keys": ["R"], "when": "Ton pactisant est en danger ou doit engager.",
             "how": "Appel du destin téléporte le pactisant auprès de toi ; il peut ensuite charger pour repousser les champions ennemis proches."},
        ],
        "mistakes": [
            "Attaquer sans bondir : tu perds ta mobilité.",
            "Utiliser l'ultime sans coordination avec ton pactisant.",
            "Extirper les lances sans effet décisif.",
        ],
    }},
    "Gangplank": {"fr": {
        "playstyle": (
            "Gangplank est un combattant dont les attaques mettent le feu à la cible toutes les quelques secondes. "
            "Pourparlers lui rapporte de l'or s'il tue, Guérison du scorbut dissipe les contrôles et le soigne, Baril de poudre étend les dégâts de ses attaques dans la zone et ralentit, et Tir de barrage bombarde une zone."
        ),
        "laning": (
            "Attaque un baril pour étendre tes dégâts et ralentir les ennemis autour. "
            "Prends les derniers coups avec Pourparlers pour gagner de l'or supplémentaire."
        ),
        "combos": [
            {"name": "Le baril", "keys": ["E", "AA", "Q"], "when": "Un ennemi est près d'un baril.",
             "how": "Baril de poudre explose quand tu l'attaques, étend les dégâts dans la zone et ralentit ; Pourparlers achève."},
            {"name": "La dissipation", "keys": ["W", "AA"], "when": "Tu es sous contrôle.",
             "how": "Guérison du scorbut dissipe les effets de contrôle qui t'affectent et te rend des PV."},
            {"name": "L'ultime de zone", "keys": ["R", "E", "AA"], "when": "Un combat est en cours à distance.",
             "how": "Tir de barrage bombarde une zone en ralentissant et blessant les ennemis ; combine-le avec des barils pour piéger."},
        ],
        "mistakes": [
            "Poser des barils sans plan d'explosion.",
            "Utiliser Guérison du scorbut sans contrôle à dissiper.",
            "Lancer l'ultime sans annoncer la zone à tes alliés.",
        ],
    }},
    "Nidalee": {"fr": {
        "playstyle": (
            "Nidalee alterne entre forme humaine (Javelot, Guérilla, Charge primale) et forme de Couguar (Mise à terre, Bond, Taillade). "
            "Dans les herbes hautes, sa vitesse de déplacement augmente, et toucher des champions avec Javelot ou Guérilla la met à leur chasse : vision pure et Bond/Mise à terre renforcés."
        ),
        "laning": (
            "Le Javelot inflige plus de dégâts selon la distance : c'est ta compétence de harcèlement. "
            "Guérilla place un piège qui blesse et révèle : utilise-le pour marquer et chasser."
        ),
        "combos": [
            {"name": "La chasse", "keys": ["Q", "R", "W", "Q", "E"], "when": "Tu as touché avec Javelot ou Guérilla.",
             "how": "Après avoir touché avec Javelot, passe en Couguar avec Aspect du Couguar : Bond te fait atterrir en zone (renforcé contre la cible chassée), Mise à terre égorge (plus de dégâts si la cible a perdu des PV), Taillade griffe."},
            {"name": "Le harcèlement en humaine", "keys": ["W", "Q", "E"], "when": "Un ennemi est à portée de Javelot.",
             "how": "Guérilla marque et révèle, le Javelot inflige plus de dégâts selon la distance, Charge primale soigne les alliés et leur donne de la vitesse d'attaque."},
            {"name": "La poursuite", "keys": ["R", "W", "W"], "when": "Un ennemi est en fuite.",
             "how": "En Couguar, Bond te propulse et blesse en zone à l'atterrissage."},
        ],
        "mistakes": [
            "Lancer Javelot à courte portée : il inflige moins de dégâts.",
            "Changer de forme sans avoir marqué : tu perds la chasse.",
            "Ignorer les herbes hautes : elles augmentent ta vitesse.",
        ],
    }},
    "Naafiri": {"fr": {
        "playstyle": (
            "Naafiri est une assassine qui combat avec sa meute : des membres de meute apparaissent et attaquent les cibles de ses attaques et compétences. "
            "Dagues des Darkin applique des saignements, Appel de la meute la rend impossible à cibler et invoque des membres supplémentaires, Éviscération rappelle et soigne la meute, et Hallali frappe un champion avec toute la meute."
        ),
        "laning": (
            "Ta meute attaque avec toi : reste proche de ton adversaire pour qu'elle inflige ses dégâts. "
            "Les dagues appliquent un saignement ; la seconde inflige des dégâts supplémentaires si la cible saigne déjà."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "Q", "AA", "E"], "when": "Un ennemi est à portée de dagues.",
             "how": "Deux Dagues des Darkin appliquent un saignement puis des dégâts bonus ; la meute bondit sur le premier champion touché ; Éviscération te rue et inflige des dégâts autour de toi."},
            {"name": "L'exécution", "keys": ["R", "R", "Q"], "when": "Un champion est à basse vie.",
             "how": "Hallali te fait, toi et ta meute, vous ruer sur un champion ; tu révèles les ennemis proches et relances si tu réalises une élimination (sans bouclier la deuxième fois)."},
            {"name": "La meute renforcée", "keys": ["W", "AA", "E"], "when": "Un combat s'engage.",
             "how": "Appel de la meute te rend impossible à cibler, invoque des membres supplémentaires et te donne de la vitesse et des dégâts d'attaque ; Éviscération rappelle et soigne entièrement la meute."},
        ],
        "mistakes": [
            "Engager seule : ta puissance dépend de ta meute.",
            "Utiliser Éviscération sans regarder l'état de ta meute.",
            "Relancer l'ultime sans élimination.",
        ],
    }},
    "Sona": {"fr": {
        "playstyle": (
            "Sona est une enchanteresse dont chaque compétence a un effet direct et un halo pour les alliés touchés : Hymne à la bravoure blesse et donne des dégâts bonus, Aria de persévérance soigne et protège, Mélodie de vélocité accélère. "
            "Sa passive réduit ses délais de récupération quand elle utilise bien ses compétences, et son ultime étourdit et force à danser."
        ),
        "laning": (
            "Enchaîne les compétences pour bénéficier de l'accélération de compétence de ta passive. "
            "Ta prochaine attaque après quelques compétences inflige des dégâts bonus et un effet selon la dernière compétence lancée."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "E", "AA"], "when": "Un ennemi est proche de toi et de ton carry.",
             "how": "Hymne à la bravoure inflige des dégâts à deux ennemis et donne un halo à tes alliés ; enchaîne pour déclencher l'Accord de puissance sur ton attaque."},
            {"name": "La protection", "keys": ["W", "E"], "when": "Un allié est menacé.",
             "how": "Aria de persévérance te soigne et soigne un allié blessé proche, avec bouclier pour les alliés touchés par le halo ; Mélodie de vélocité accélère ton équipe."},
            {"name": "L'ultime d'engagement", "keys": ["R", "Q"], "when": "Ton équipe est prête à engager.",
             "how": "Crescendo étourdit les champions ennemis, les force à danser et leur inflige des dégâts magiques."},
        ],
        "mistakes": [
            "Lancer l'ultime sans allié prêt.",
            "Ne pas utiliser tes compétences quand tu peux : ta passive réduit les délais.",
            "Négliger le mana : chaque compétence en coûte.",
        ],
    }},
}
