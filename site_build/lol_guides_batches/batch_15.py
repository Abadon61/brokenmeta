"""Guides rédigés, lot 15. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "XinZhao": {"fr": {
        "playstyle": (
            "Xin Zhao est un jungler de duel : toutes les 3 attaques il inflige des dégâts supplémentaires et se soigne. "
            "Frappe des trois serres projette à la 3e attaque, Vent et foudre ralentit et marque comme défié, Charge audacieuse a plus de portée contre les défiés, et Garde circulaire le protège des champions hors du cercle."
        ),
        "laning": (
            "Enchaîne les attaques par trois pour profiter de ta passive et de Frappe des trois serres. "
            "Un ennemi défié est plus facile à atteindre avec Charge audacieuse."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["W", "E", "Q", "AA", "AA", "AA"], "when": "Un ennemi est à portée de charge.",
             "how": "Vent et foudre marque comme défié en ralentissant, Charge audacieuse charge avec plus de portée, Frappe des trois serres : la 3e attaque projette dans les airs."},
            {"name": "Le duel", "keys": ["R", "Q", "AA", "AA", "AA"], "when": "Tu affrontes un seul champion.",
             "how": "Garde circulaire inflige des dégâts selon les PV actuels des ennemis proches, repousse les non-défiés et t'immunise contre les dégâts des champions hors du cercle."},
            {"name": "La poursuite", "keys": ["E", "Q", "AA"], "when": "Un ennemi défié fuit.",
             "how": "Charge audacieuse a une portée augmentée contre les ennemis défiés et augmente ta vitesse d'attaque."},
        ],
        "mistakes": [
            "Utiliser l'ultime en pleine mêlée d'équipe : ses effets défensifs sont contre les champions hors du cercle.",
            "Ne pas compter tes attaques : ta passive est tous les 3 coups.",
            "Charger sans avoir marqué avec Vent et foudre.",
        ],
    }},
    "Fiddlesticks": {"fr": {
        "playstyle": (
            "Fiddlesticks est un jungler de terreur : Terreur fait fuir un ennemi s'il le blesse en n'étant pas visible, Moisson fructueuse draine avec des dégâts d'exécution, Fauchaison ralentit et réduit au silence au centre, et Rafale de corbeaux inflige des dégâts par seconde dans la zone. "
            "Sa passive remplace sa relique par des Effigies d'épouvantail."
        ),
        "laning": (
            "Cache-toi avant d'attaquer : Terreur fonctionne si tu blesses en n'étant pas visible. "
            "Les Effigies d'épouvantail te permettent d'apparaître par surprise."
        ),
        "combos": [
            {"name": "L'embuscade", "keys": ["Q", "E", "W"], "when": "Tu es caché près d'un ennemi.",
             "how": "Terreur fait fuir l'ennemi, Fauchaison ralentit et réduit au silence les ennemis au centre, Moisson fructueuse draine avec des dégâts d'exécution."},
            {"name": "L'ultime de zone", "keys": ["R", "W", "E"], "when": "Les ennemis sont regroupés.",
             "how": "Rafale de corbeaux tourbillonne autour de toi en infligeant des dégâts par seconde à toutes les unités ennemies dans la zone."},
            {"name": "Le drain", "keys": ["W", "E", "Q"], "when": "Un ennemi est isolé.",
             "how": "Moisson fructueuse draine l'essence vitale et inflige des dégâts d'exécution supplémentaires à la fin de l'effet."},
        ],
        "mistakes": [
            "Te montrer avant Terreur.",
            "Lancer l'ultime sans préparation.",
            "Utiliser Moisson fructueuse sans pouvoir la finir.",
        ],
    }},
    "TahmKench": {"fr": {
        "playstyle": (
            "Tahm Kench est un support-tank dont les dégâts augmentent avec ses PV totaux. "
            "Coup de langue ralentit et applique Goût acquis (à 3 effets, il étourdit et peut être suivi de Dévoration), Plongée abyssale projette, Peau épaisse stocke des dégâts pour un bouclier, et Dévoration avale un champion : dégâts magiques ou bouclier pour un allié."
        ),
        "laning": (
            "Applique 3 effets de Goût acquis pour étourdir avec Coup de langue. "
            "Peau épaisse : active-la pour convertir les dégâts stockés en bouclier temporaire."
        ),
        "combos": [
            {"name": "L'étourdissement", "keys": ["Q", "AA", "Q", "Q"], "when": "Un ennemi est à portée.",
             "how": "Coup de langue applique un effet Goût acquis ; à 3 effets, le champion est étourdi et les effets sont consommés."},
            {"name": "L'engagement", "keys": ["W", "Q", "R"], "when": "Un ennemi est éloigné.",
             "how": "Plongée abyssale te fait plonger puis réapparaître à l'endroit ciblé, blessant et projetant les ennemis ; Dévoration avale un champion ennemi (3 effets requis)."},
            {"name": "La protection d'un allié", "keys": ["R", "E"], "when": "Un allié est menacé.",
             "how": "Dévoration sur un allié lui octroie un bouclier pendant quelques secondes ; Peau épaisse te protège aussi."},
        ],
        "mistakes": [
            "Utiliser Dévoration sur un ennemi sans avoir les 3 effets.",
            "Ne pas convertir tes dégâts stockés en bouclier.",
            "Utiliser Plongée abyssale sans direction.",
        ],
    }},
    "Kennen": {"fr": {
        "playstyle": (
            "Kennen est un mage d'énergie dont la passive étourdit les ennemis touchés 3 fois avec ses compétences. "
            "Shuriken foudroyant ajoute une Marque de tempête, Surtension en ajoute passivement, Rush foudroyant le transforme en boule d'électricité, et Maelström frappe les champions ennemis proches."
        ),
        "laning": (
            "Touche trois fois pour étourdir : Shuriken, Surtension, Rush foudroyant appliquent des marques. "
            "Ton énergie limite tes compétences : n'abuse pas."
        ),
        "combos": [
            {"name": "L'étourdissement", "keys": ["Q", "W", "E"], "when": "Un ennemi est à portée.",
             "how": "Shuriken foudroyant ajoute une marque, Surtension une autre, Rush foudroyant une troisième : à 3 marques, l'ennemi est étourdi."},
            {"name": "L'engagement d'équipe", "keys": ["E", "R", "Q", "W"], "when": "Plusieurs ennemis sont proches.",
             "how": "Rush foudroyant te fait traverser les unités en appliquant des marques ; Maelström invoque une tempête qui frappe les champions ennemis proches."},
            {"name": "Le harcèlement", "keys": ["Q", "AA", "W"], "when": "Un ennemi est en lane.",
             "how": "Surtension ajoute passivement des marques toutes les quelques attaques."},
        ],
        "mistakes": [
            "Utiliser tes compétences sans compter les marques.",
            "Lancer l'ultime sans plusieurs ennemis proches.",
            "Négliger ton énergie.",
        ],
    }},
    "Urgot": {"fr": {
        "playstyle": (
            "Urgot est un combattant de mêlée à distance : ses attaques et Géhenne font jaillir des flammes qui infligent des dégâts physiques. "
            "Torpille corrosive ralentit, Géhenne vise en priorité les champions récemment frappés, Mépris le fait foncer avec un bouclier, et Règne de la terreur empale puis exécute sous un certain seuil de PV."
        ),
        "laning": (
            "Géhenne vise en priorité les champions ennemis que tu as récemment frappés avec d'autres compétences. "
            "Torpille corrosive ralentit dans la zone."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "W", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Torpille corrosive ralentit, Géhenne décharge sur l'ennemi marqué, tes attaques déclenchent Flammes purificatrices, Mépris te donne un bouclier."},
            {"name": "L'exécution", "keys": ["R", "R", "W"], "when": "Un champion est à bas PV.",
             "how": "Règne de la terreur tire un trépan qui empale le premier champion touché : sous un certain seuil de PV, tu peux l'exécuter."},
            {"name": "La charge", "keys": ["E", "W", "Q"], "when": "Tu veux te rapprocher.",
             "how": "Mépris te fait foncer en te donnant un bouclier et piétine les ennemis sur ton passage (hors champions) ; s'il percute un champion, il le projette hors de ton chemin."},
        ],
        "mistakes": [
            "Utiliser l'ultime sans seuil d'exécution atteint.",
            "Lancer Géhenne sans ralentissement préalable.",
            "Oublier que Mépris s'arrête sur un champion.",
        ],
    }},
    "Maokai": {"fr": {
        "playstyle": (
            "Maokai est un tank-support de contrôle : son attaque de base rend des PV et inflige des dégâts supplémentaires, avec un délai réduit à chaque compétence lancée ou subie. "
            "Coup de ronces repousse et ralentit, Croissance torturée l'immobilise à l'arrivée, Jet d'arbrisseau surveille une zone, et Emprise de la nature avance lentement en immobilisant."
        ),
        "laning": (
            "Lance des compétences pour recharger ta passive. "
            "Jet d'arbrisseau est plus efficace dans les hautes herbes."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["W", "AA", "Q"], "when": "Un carry est à portée.",
             "how": "Croissance torturée te rend impossible à cibler et te fait foncer sur la cible, qu'elle immobilise à l'arrivée ; Coup de ronces repousse et ralentit."},
            {"name": "Le contrôle de zone", "keys": ["E", "R", "Q"], "when": "Tu défends un objectif.",
             "how": "Jet d'arbrisseau surveille une zone ; Emprise de la nature invoque un mur de ronces qui avance lentement, blessant et immobilisant les ennemis."},
            {"name": "La sustain", "keys": ["Q", "AA", "W"], "when": "Tu es engagé.",
             "how": "Ta passive rend des PV avec ton attaque de base ; chaque compétence réduit son délai de récupération."},
        ],
        "mistakes": [
            "Lancer l'ultime sans direction.",
            "Oublier l'attaque de ta passive.",
            "Utiliser Croissance torturée sans cible.",
        ],
    }},
    "Neeko": {"fr": {
        "playstyle": (
            "Neeko est une mage-support caméléon : sa passive lui permet de prendre l'apparence d'un allié ou d'une unité, jusqu'à ce qu'elle soit immobilisée, lance une compétence offensive ou subisse des dégâts. "
            "Explosion florale éclot deux fois, Métaclonage envoie un clone, Spirale épineuse immobilise, et Floraison renversante projette puis étourdit."
        ),
        "laning": (
            "Déguisée, tu peux surprendre : la préparation de ton ultime ne se voit pas si tu es déguisée. "
            "Explosion florale éclot une nouvelle fois si elle touche un champion ou tue."
        ),
        "combos": [
            {"name": "L'embuscade déguisée", "keys": ["R", "E", "Q", "W"], "when": "Tu es déguisée près des ennemis.",
             "how": "Floraison renversante : la préparation est invisible si tu es déguisée, tu bondis en projetant et à l'atterrissage tu blesses et étourdis ; Spirale épineuse immobilise ensuite."},
            {"name": "Le harcèlement", "keys": ["Q", "W", "AA"], "when": "Un ennemi est à portée.",
             "how": "Explosion florale blesse et éclot une deuxième fois ; toutes les 3 attaques, Métaclonage inflige des dégâts supplémentaires et t'accélère."},
            {"name": "L'immobilisation", "keys": ["E", "Q"], "when": "Un ennemi est isolé.",
             "how": "Spirale épineuse immobilise tous les ennemis traversés ; si elle tue ou traverse un champion, elle grossit et l'immobilisation est plus longue."},
        ],
        "mistakes": [
            "Rompre ton déguisement avant l'engagement.",
            "Lancer Spirale épineuse sans trajectoire.",
            "Oublier la réactivation du clone.",
        ],
    }},
    "Vex": {"fr": {
        "playstyle": (
            "Vex est une mage de contre-mobilité : sa passive la renforce régulièrement pour que sa prochaine compétence de base effraie et interrompe les ruées. "
            "Chaque ruée d'un ennemi proche lui donne une marque consommable pour des dégâts supplémentaires et un délai réduit. Déferlement d'Ombre marque puis la fait se ruer sur l'ennemi."
        ),
        "laning": (
            "Attends que ton renforcement soit prêt pour effrayer. "
            "Ténèbres imminentes ralentit et applique Désespoir."
        ),
        "combos": [
            {"name": "L'anti-ruée", "keys": ["Q", "E", "W"], "when": "Un ennemi fait une ruée.",
             "how": "Ta compétence renforcée effraie et interrompt la ruée ; la marque appliquée inflige des dégâts supplémentaires si elle est consommée."},
            {"name": "L'ultime de traque", "keys": ["R", "R", "Q", "E"], "when": "Un carry est visible.",
             "how": "Déferlement d'Ombre marque un champion puis se réactive pour te ruer sur lui et lui infliger des dégâts."},
            {"name": "La défense", "keys": ["W", "E"], "when": "Un ennemi plonge.",
             "how": "Lâchez-moi ! te donne un bouclier et blesse les ennemis proches ; Ténèbres imminentes ralentit et applique Désespoir."},
        ],
        "mistakes": [
            "Gaspiller ton renforcement de passive.",
            "Lancer l'ultime sur une cible qui peut fuir.",
            "Négliger les marques : elles réduisent le délai de renforcement.",
        ],
    }},
    "Kayle": {"fr": {
        "playstyle": (
            "Kayle est une combattante qui monte en puissance : ses ailes s'enflamment avec ses niveaux et ses points de compétence, lui donnant vitesse d'attaque, vitesse de déplacement, portée et vagues de feu. "
            "Incandescence traverse et réduit les résistances, Bénédiction céleste soigne, Lame de feu stellaire la renforce, et Jugement divin rend un allié invulnérable."
        ),
        "laning": (
            "Survis à la phase de lane : ta puissance vient de tes niveaux. "
            "Lame de feu stellaire inflige des dégâts supplémentaires selon les PV manquants de la cible."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "E", "AA", "AA"], "when": "Un ennemi est à portée.",
             "how": "Incandescence ralentit, blesse et réduit les résistances ; Lame de feu stellaire déchaîne le feu céleste sur ta prochaine attaque."},
            {"name": "La protection", "keys": ["W", "R"], "when": "Un allié est menacé.",
             "how": "Bénédiction céleste te soigne et soigne l'allié le plus proche avec un bonus de vitesse ; Jugement divin rend un allié invulnérable."},
            {"name": "Le combat d'équipe", "keys": ["R", "Q", "E", "AA"], "when": "Un combat décisif s'engage.",
             "how": "Jugement divin fait tomber une pluie d'épées purificatrices autour de sa cible pendant que l'allié est invulnérable."},
        ],
        "mistakes": [
            "Chercher à tuer avant d'avoir tes niveaux clés.",
            "Utiliser l'ultime sur un allié qui n'est pas la cible.",
            "Négliger Lame de feu stellaire : elle ajoute des dégâts selon les PV manquants.",
        ],
    }},
    "Renata": {"fr": {
        "playstyle": (
            "Renata Glasc est une support de contrôle : ses attaques marquent les ennemis, et ses alliés infligent des dégâts supplémentaires aux ennemis marqués. "
            "Poignée de main immobilise et lance, Patronage retarde la mort d'un allié, Programme de fidélité protège et ralentit, et Prise de contrôle hostile rend fous furieux les ennemis touchés."
        ),
        "laning": (
            "Marque l'ennemi avec tes attaques pour que ton carry inflige plus de dégâts. "
            "Poignée de main se réactive pour lancer l'ennemi."
        ),
        "combos": [
            {"name": "Le pick", "keys": ["Q", "Q", "E"], "when": "Un ennemi est isolé.",
             "how": "Poignée de main immobilise le premier ennemi touché, réactive pour le lancer dans une direction ; Programme de fidélité ralentit et protège."},
            {"name": "La protection", "keys": ["W", "E"], "when": "Un allié va mourir.",
             "how": "Patronage retarde la mort de l'allié et lui permet de survivre s'il participe à l'élimination d'un champion."},
            {"name": "L'ultime de chaos", "keys": ["R", "Q", "E"], "when": "Les ennemis sont regroupés.",
             "how": "Prise de contrôle hostile envoie un nuage qui rend fous furieux tous les ennemis touchés."},
        ],
        "mistakes": [
            "Utiliser Patronage sur un allié qui ne peut pas participer à l'élimination.",
            "Lancer l'ultime sans cibles groupées.",
            "Oublier de marquer les ennemis.",
        ],
    }},
    "Lillia": {"fr": {
        "playstyle": (
            "Lillia est une jungler qui court : toucher un champion ou un monstre avec une compétence lui inflige des dégâts sur la durée selon ses PV max. "
            "Frappe fleurie lui donne de la vitesse de déplacement cumulable, Attention, désolée ! frappe fort au centre, Graine tournoyante ralentit, et Douce berceuse endort les ennemis affectés par Poussière de rêve."
        ),
        "laning": (
            "Touche avec tes compétences pour cumuler de la vitesse de déplacement avec Frappe fleurie. "
            "Attention, désolée ! inflige d'importants dégâts au centre de la zone."
        ),
        "combos": [
            {"name": "Le combo de base", "keys": ["E", "W", "Q", "AA"], "when": "Un ennemi est à portée.",
             "how": "Graine tournoyante blesse et ralentit, Attention, désolée ! frappe au centre, Frappe fleurie inflige des dégâts en zone (bruts en bordure) ; ta passive inflige des dégâts sur la durée."},
            {"name": "L'ultime d'endormissement", "keys": ["W", "E", "R"], "when": "Plusieurs ennemis sont marqués.",
             "how": "Douce berceuse provoque une somnolence chez tous les ennemis affectés par Poussière de rêve, qui finissent par s'endormir ; ils subissent des dégâts supplémentaires s'ils sont réveillés de force."},
            {"name": "La poursuite", "keys": ["Q", "E", "AA"], "when": "Tu veux courir vers une cible.",
             "how": "Frappe fleurie te donne des bonus cumulables de vitesse quand tes compétences touchent."},
        ],
        "mistakes": [
            "Lancer l'ultime sans avoir touché de Poussière de rêve.",
            "Ne pas viser le centre avec Attention, désolée !",
            "Rester immobile : ta force vient de ta vitesse.",
        ],
    }},
}
