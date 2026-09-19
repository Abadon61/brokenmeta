"""Guides rédigés, lot 16. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Nunu": {"fr": {
        "playstyle": (
            "Nunu et Willump forment un duo tank-mage : Nunu augmente les vitesses d'attaque et de déplacement de Willump et d'un allié proche, et les attaques de Willump blessent les ennemis proches de la cible. "
            "Voracité soigne, Boule de neige géante ! grossit en roulant et projette, Rafale de boules de neige immobilise ceux qui sont touchés, et Zéro absolu crée un blizzard."
        ),
        "laning": (
            "Voracité mord un sbire, un monstre ou un champion et te soigne. "
            "Boule de neige géante ! grossit et accélère : plus elle roule, plus elle est efficace."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["W", "E", "Q"], "when": "Un ennemi est éloigné.",
             "how": "Boule de neige géante ! blesse et projette, Rafale de boules de neige blesse et Willump immobilise les champions touchés, Voracité mord en te soignant."},
            {"name": "L'ultime de zone", "keys": ["R", "E"], "when": "Les ennemis sont regroupés.",
             "how": "Zéro absolu crée un blizzard qui ralentit et inflige d'importants dégâts à la fin du sort : reste sur place pour le canaliser."},
            {"name": "La sustain", "keys": ["Q", "AA"], "when": "Tu es en jungle.",
             "how": "Voracité inflige d'importants dégâts et te rend des PV en mordant."},
        ],
        "mistakes": [
            "Lancer l'ultime sans protection pendant sa durée.",
            "Ne pas faire rouler la boule de neige assez longtemps.",
            "Oublier ton allié : Nunu augmente ses vitesses.",
        ],
    }},
    "Belveth": {"fr": {
        "playstyle": (
            "Bel'Veth est une jungler de vitesse d'attaque : sa passive lui donne des bonus définitifs après avoir tué grands monstres, grands sbires et champions, et un bonus temporaire après chaque compétence. "
            "Charge du Néant la rue, Projection cinglante projette et ralentit, Maelström impérial canalise des coups sur l'ennemi qui a le moins de PV, et Banquet infini la fait passer à sa véritable forme."
        ),
        "laning": (
            "Tue les grands monstres et grands sbires pour cumuler des bonus définitifs de vitesse d'attaque. "
            "Charge du Néant blesse tous les ennemis traversés."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "W", "AA"], "when": "Un ennemi est à portée.",
             "how": "Charge du Néant te rue en blessant ; chaque compétence te donne un bonus temporaire de vitesse d'attaque ; Projection cinglante projette et ralentit."},
            {"name": "La tempête", "keys": ["E", "AA"], "when": "Les ennemis sont proches.",
             "how": "Maelström impérial t'immobilise et canalise une tempête de coups qui cible l'ennemi ayant le moins de PV, avec vol de vie et réduction des dégâts."},
            {"name": "La forme finale", "keys": ["R", "Q", "W", "AA"], "when": "Tu as du corail du Néant.",
             "how": "Banquet infini consomme du corail du Néant : PV max, portée d'attaque et vitesse d'attaque augmentent ; le corail d'un monstre épique du Néant permet d'invoquer des rémoras."},
        ],
        "mistakes": [
            "Négliger les grands monstres : ils donnent des bonus définitifs.",
            "Lancer Maelström impérial sans protection : tu es immobile.",
            "Ne pas récolter le corail du Néant.",
        ],
    }},
    "Skarner": {"fr": {
        "playstyle": (
            "Skarner est un jungler-tank de tectonique : ses attaques, Terre brisée, Soulèvement et Empalement appliquent Tectonique, et au maximum les ennemis subissent des dégâts magiques selon leurs PV max. "
            "Bastion sismique donne un bouclier et ralentit, Impact d'Ixtal écrase contre un mur, et Empalement neutralise puis traîne les ennemis."
        ),
        "laning": (
            "Arrache un rocher avec Terre brisée pour renforcer tes attaques, puis lance-le avec Soulèvement. "
            "Cumule la Tectonique pour déclencher les dégâts sur PV max."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "Q", "W"], "when": "Un ennemi est à portée.",
             "how": "Terre brisée renforce tes attaques, Soulèvement lance le rocher, Bastion sismique te donne un bouclier et ralentit par une onde de choc."},
            {"name": "L'écrasement", "keys": ["E", "Q", "AA"], "when": "Un ennemi est près d'un mur.",
             "how": "Impact d'Ixtal charge en traversant les obstacles ; s'il percute un champion, il l'écrase contre le prochain mur, lui infligeant des dégâts et l'étourdissant."},
            {"name": "L'ultime de capture", "keys": ["R", "E", "Q"], "when": "Un carry est visible.",
             "how": "Empalement neutralise les champions ennemis frappés par tes queues et te permet de te déplacer en les traînant : place-les dans ton équipe."},
        ],
        "mistakes": [
            "Traîner les ennemis vers leurs alliés.",
            "Oublier la Tectonique : elle est ta source de dégâts sur PV max.",
            "Lancer Impact d'Ixtal sans mur.",
        ],
    }},
    "Azir": {"fr": {
        "playstyle": (
            "Azir est un mage à soldats de sable : Dresse-toi ! invoque un soldat qui attaque à sa place, et les attaques du soldat infligent des dégâts magiques sur une ligne. "
            "Sables conquérants envoie tous les soldats, Sables mouvants le fait foncer vers un soldat, et Partition impériale repousse les ennemis. Sa passive lui permet d'invoquer le Disque solaire depuis les ruines de tourelles."
        ),
        "laning": (
            "Place tes soldats de manière à ce qu'ils touchent ta cible ; ils remplacent ton attaque contre les cibles à leur portée. "
            "Sables mouvants te fait foncer vers un soldat."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["W", "AA", "Q"], "when": "Un ennemi est à portée.",
             "how": "Dresse-toi ! invoque un soldat qui attaque à ta place ; Sables conquérants envoie tous les soldats en zone : ils blessent et ralentissent 1 seconde."},
            {"name": "L'engagement", "keys": ["W", "E", "Q", "R"], "when": "Un carry est à portée.",
             "how": "Sables mouvants te donne un bouclier et te fait foncer vers un soldat ; s'il touche un champion, un nouveau soldat est préparé et la ruée s'arrête ; Partition impériale repousse."},
            {"name": "La défense", "keys": ["R", "E"], "when": "Un ennemi plonge.",
             "how": "Partition impériale invoque un mur de soldats qui chargent vers l'avant, repoussant et blessant les ennemis."},
        ],
        "mistakes": [
            "Ne pas placer de soldats avant d'attaquer.",
            "Lancer Sables mouvants sans soldat proche.",
            "Utiliser l'ultime sans direction.",
        ],
    }},
    "Ivern": {"fr": {
        "playstyle": (
            "Ivern est un jungler-support d'enchantement : il ne peut pas attaquer ni être attaqué par les monstres non épiques, et crée des bosquets magiques qui, une fois développés, libèrent les monstres pour des PO et de l'expérience. "
            "Enracinement immobilise, Main verte crée de l'herbe haute, Graine à retardement protège, et Marguerite ! invoque une sentinelle."
        ),
        "laning": (
            "Développe tes bosquets, puis libère les monstres pour des PO et de l'expérience. "
            "Tes alliés peuvent foncer vers la cible immobilisée par Enracinement."
        ),
        "combos": [
            {"name": "Le pick", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée d'enracinement.",
             "how": "Enracinement immobilise la cible et tes alliés peuvent foncer dessus ; Graine à retardement donne un bouclier à un allié qui explose et ralentit."},
            {"name": "La zone d'herbes", "keys": ["W", "AA"], "when": "Un combat approche.",
             "how": "Main verte crée une parcelle d'herbes hautes où tes attaques et celles de tes alliés proches infligent des dégâts magiques supplémentaires."},
            {"name": "Le compagnon", "keys": ["R", "R"], "when": "Un combat d'équipe s'engage.",
             "how": "Marguerite ! invoque une sentinelle qui combat à tes côtés ; relance la compétence pour lui ordonner d'attaquer ou de se déplacer."},
        ],
        "mistakes": [
            "Négliger tes bosquets.",
            "Utiliser Graine à retardement sur un allié sans ennemi proche : le bouclier se réinitialise.",
            "Ne pas contrôler Marguerite.",
        ],
    }},
    "Kled": {"fr": {
        "playstyle": (
            "Kled est un combattant monté : Skaarl subit les dégâts à sa place, et quand ses PV tombent à zéro, Kled est désarçonné avec des compétences modifiées et moins de dégâts aux champions. "
            "Il restaure le courage de Skaarl en combattant, et Piège à ours en laisse accroche et tire les ennemis vers lui."
        ),
        "laning": (
            "Protège Skaarl : tant qu'il est monté, tu infliges plus de dégâts. "
            "Désarçonné, combats pour restaurer le courage et te remettre en selle."
        ),
        "combos": [
            {"name": "L'accroche", "keys": ["Q", "E", "AA", "AA"], "when": "Un ennemi est à portée du piège.",
             "how": "Piège à ours en laisse accroche un champion ; s'il reste accroché, il subit des dégâts supplémentaires et est tiré vers toi ; Joute te fait foncer."},
            {"name": "Le combat de vitesse", "keys": ["W", "AA", "AA", "AA", "AA"], "when": "Tu es au corps à corps.",
             "how": "Penchant pour la violence augmente grandement ta vitesse d'attaque pendant quatre attaques ; la quatrième inflige plus de dégâts."},
            {"name": "La charge d'équipe", "keys": ["R", "E"], "when": "Ton équipe engage.",
             "how": "Chaaaaaaaargez !!! te fait charger avec un bouclier et laisse une traînée qui augmente la vitesse des alliés ; Skaarl fonce sur le premier champion ennemi rencontré."},
        ],
        "mistakes": [
            "Laisser Skaarl tomber à zéro sans nécessité.",
            "Oublier que désarçonné tu changes de compétences.",
            "Utiliser Joute sans réactivation quand elle est utile.",
        ],
    }},
    "Trundle": {"fr": {
        "playstyle": (
            "Trundle est un combattant de duel : quand une unité ennemie meurt près de lui, il récupère un pourcentage de ses PV max. "
            "Morsure ralentit et draine les dégâts d'attaque, Royaume gelé augmente ses vitesses et ses soins, Montagne de glace bloque le passage, et Soumission vole PV, armure et résistance magique."
        ),
        "laning": (
            "Morsure réduit les dégâts d'attaque de ton adversaire : utilise-la en début d'échange. "
            "Combats dans ton Royaume gelé pour bénéficier de bonus."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["W", "Q", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Royaume gelé augmente vitesses et soins, Morsure inflige des dégâts, ralentit et draine ses dégâts d'attaque, Montagne de glace bloque le passage."},
            {"name": "Le duel", "keys": ["R", "Q", "AA"], "when": "Un carry est isolé.",
             "how": "Soumission vole immédiatement un pourcentage des PV, de l'armure et de la résistance magique de la cible, puis le montant double en 4 secondes."},
            {"name": "Le piège", "keys": ["E", "W", "Q"], "when": "Un ennemi te poursuit.",
             "how": "Montagne de glace bloque le passage et ralentit les ennemis proches."},
        ],
        "mistakes": [
            "Utiliser Soumission sur un carry trop faible : elle vole un pourcentage des stats.",
            "Combattre hors de ton Royaume gelé.",
            "Oublier de drainer les dégâts avec Morsure.",
        ],
    }},
    "Sejuani": {"fr": {
        "playstyle": (
            "Sejuani est une jungler-tank de glace : hors combat elle gagne Armure de glace (armure, résistance magique, immunité aux ralentissements), et elle peut fracasser un ennemi étourdi pour d'énormes dégâts magiques. "
            "Assaut arctique projette, Colère de l'hiver applique des effets Givre, Permafrost étourdit un champion au maximum de Givre, et Prison de glace gèle le premier champion touché."
        ),
        "laning": (
            "Empile les effets Givre avec Colère de l'hiver puis gèle avec Permafrost. "
            "Profite de l'Armure de glace hors combat pour engager."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["Q", "W", "E", "AA"], "when": "Un ennemi est à portée.",
             "how": "Assaut arctique projette en l'air et s'arrête sur un champion ; Colère de l'hiver blesse, ralentit et applique Givre ; Permafrost étourdit un champion au maximum d'effets ; ton attaque fracasse l'étourdi."},
            {"name": "L'ultime de capture", "keys": ["R", "W", "E"], "when": "Un carry est visible.",
             "how": "Prison de glace gèle et étourdit le premier champion touché avec des bolas et crée une tempête de glace qui ralentit les autres ennemis."},
            {"name": "L'approche", "keys": ["Q", "W"], "when": "Tu veux ouvrir un combat.",
             "how": "Assaut arctique projette dans les airs, Colère de l'hiver ralentit les ennemis avec deux coups de masse."},
        ],
        "mistakes": [
            "Utiliser Permafrost sans le maximum de Givre.",
            "Lancer l'ultime sans allié pour profiter du gel.",
            "Oublier de fracasser l'ennemi étourdi.",
        ],
    }},
    "Rammus": {"fr": {
        "playstyle": (
            "Rammus est un jungler-tank qui gagne des dégâts d'attaque selon son armure et sa résistance magique. "
            "Démolisseur roule sur les ennemis, Boule défensive augmente ses défenses et renvoie des dégâts, Provocation frénétique force un ennemi à l'attaquer, et Frappe ascendante bondit et retombe avec des dégâts et un ralentissement."
        ),
        "laning": (
            "Provoque le carry adverse pour le forcer à t'attaquer. "
            "Boule défensive te rend très résistant et renvoie des dégâts aux attaquants."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["Q", "E", "R"], "when": "Un ennemi est à portée de roulade.",
             "how": "Démolisseur roule vers les ennemis en infligeant des dégâts et ralentissant ; Provocation frénétique force la cible à t'attaquer ; Frappe ascendante retombe en zone."},
            {"name": "La défense", "keys": ["W", "E"], "when": "Un carry attaque ton équipe.",
             "how": "Boule défensive augmente grandement armure et résistance magique et renvoie des dégâts ; Provocation frénétique force un champion à s'acharner sur toi."},
            {"name": "Le combo projeté", "keys": ["Q", "R", "W"], "when": "Plusieurs ennemis sont groupés.",
             "how": "Si Frappe ascendante est lancée pendant Démolisseur, les ennemis près du centre sont projetés dans les airs."},
        ],
        "mistakes": [
            "Lancer Boule défensive sur un ennemi qui n'attaque pas par des dégâts physiques.",
            "Utiliser Frappe ascendante sans Démolisseur actif quand tu peux l'associer.",
            "Provoquer le mauvais champion.",
        ],
    }},
    "RekSai": {"fr": {
        "playstyle": (
            "Rek'Sai est une jungler à deux modes : en surface, elle génère de la Fureur avec ses attaques et compétences, et enfouie elle consomme la Fureur pour se soigner. "
            "Enfouissement lui donne de nouvelles compétences (Jaillissement, Tunnel), et Rush du Néant marque puis la fait bondir sur une cible marquée."
        ),
        "laning": (
            "Génère de la Fureur pour te soigner enfouie et pour renforcer Morsure féroce. "
            "Enfouie, tu ne peux plus attaquer et ta vision est réduite."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "AA", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Courroux de la reine renforce tes 3 prochaines attaques ; Morsure féroce inflige des dégâts bruts bonus si ta jauge de Fureur est pleine."},
            {"name": "L'embuscade souterraine", "keys": ["W", "E", "W"], "when": "Un ennemi est isolé.",
             "how": "Enfouissement te donne de la vitesse ; Jaillissement, enfouie, projette en l'air et blesse les ennemis proches ; Tunnel crée un passage réutilisable."},
            {"name": "L'ultime de traque", "keys": ["R", "R", "Q"], "when": "Un ennemi est marqué.",
             "how": "Rush du Néant marque passivement tes cibles ; active-le pour devenir impossible à cibler et bondir sur une cible marquée avec d'importants dégâts selon ses PV max."},
        ],
        "mistakes": [
            "Rester enfouie face à un ennemi qui te détruit le tunnel.",
            "Ne pas utiliser ta Fureur pour te soigner.",
            "Bondir sans avoir marqué.",
        ],
    }},
    "Annie": {"fr": {
        "playstyle": (
            "Annie est une mage de burst : après 4 compétences utilisées, sa prochaine compétence offensive étourdit sa cible, et elle commence la partie et réapparaît avec Pyromanie disponible. "
            "Désintégration rend son mana si elle tue, Incinération inflige des dégâts en cône, Bouclier en fusion protège, et Invocation : Tibbers fait apparaître son ours."
        ),
        "laning": (
            "Utilise tes compétences pour charger ta passive : 4 compétences puis étourdissement. "
            "Désintégration te rend son mana si elle tue la cible."
        ),
        "combos": [
            {"name": "L'étourdissement", "keys": ["W", "Q", "W", "Q", "R"], "when": "Un ennemi est à portée.",
             "how": "Enchaîne quatre compétences ; ta prochaine compétence offensive étourdit ta cible : lance Tibbers, qui inflige des dégâts en zone et brûle les ennemis proches."},
            {"name": "L'engagement d'équipe", "keys": ["E", "W", "R", "Q"], "when": "Un combat s'engage.",
             "how": "Bouclier en fusion donne vitesse de déplacement et bouclier (blessant les attaquants) ; Tibbers attaque et brûle les ennemis proches."},
            {"name": "Le farm", "keys": ["Q", "AA"], "when": "Tu es en lane.",
             "how": "Désintégration détruit la cible et te rend son coût en mana."},
        ],
        "mistakes": [
            "Gaspiller ta passive avant l'engagement.",
            "Lancer Tibbers sans étourdissement prêt.",
            "Négliger Bouclier en fusion pour un allié.",
        ],
    }},
    "Amumu": {"fr": {
        "playstyle": (
            "Amumu est un jungler-tank de contrôle : ses attaques maudissent les ennemis, qui subissent des dégâts bruts supplémentaires à chaque dégât magique. "
            "Jet de bandelette étourdit, Désespoir retire un pourcentage des PV max chaque seconde, Colère réduit les dégâts physiques et blesse, et Malédiction d'Amumu emmêle et étourdit les ennemis proches."
        ),
        "laning": (
            "Jet de bandelette a un délai très court : utilise-le pour approcher et étourdir. "
            "Désespoir consomme du mana à chaque seconde : ne le laisse pas actif sans cible."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["Q", "R", "W", "E"], "when": "Plusieurs ennemis sont groupés.",
             "how": "Jet de bandelette étourdit et te rapproche, Malédiction d'Amumu emmêle les ennemis proches et les étourdit, Désespoir retire un pourcentage de leurs PV max chaque seconde."},
            {"name": "Le combat prolongé", "keys": ["W", "AA", "E"], "when": "Tu es au milieu des ennemis.",
             "how": "Ta passive maudit ; Colère réduit les dégâts physiques subis et blesse ; son délai diminue chaque fois que tu es touché."},
            {"name": "Le pick", "keys": ["Q", "AA", "Q"], "when": "Un ennemi est isolé.",
             "how": "Jet de bandelette étourdit et blesse pendant que tu approches, puis attaque pour appliquer la malédiction."},
        ],
        "mistakes": [
            "Lancer l'ultime sur un seul ennemi.",
            "Laisser Désespoir actif sans cible.",
            "Oublier ta malédiction : les dégâts magiques deviennent plus forts contre les maudits.",
        ],
    }},
}
