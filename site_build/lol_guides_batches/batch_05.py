"""Guides rédigés, lot 5. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Malphite": {"fr": {
        "playstyle": (
            "Malphite est un tank-mage dont le bouclier de roche absorbe 10 % de ses PV max et se recharge s'il n'est pas touché pendant quelques secondes. "
            "Éclat sismique lui vole de la vitesse de déplacement, Choc au sol inflige des dégâts magiques selon son armure, et Force indomptable le fait foncer à grande vitesse et projette les ennemis dans les airs : c'est un engagement de combat d'équipe."
        ),
        "laning": (
            "Éclat sismique te rapproche de ton adversaire en lui volant sa vitesse de déplacement pendant 3 secondes. "
            "Tes dégâts de Choc au sol augmentent avec ton armure : empile de l'armure pour renforcer autant ta défense que tes dégâts."
        ),
        "combos": [
            {"name": "L'échange en lane", "keys": ["Q", "W", "AA", "E"], "when": "Un ennemi est à portée d'éclat.",
             "how": "Éclat sismique lui vole sa vitesse pendant 3 secondes et te rapproche, Coup de tonnerre fait produire des ondes de choc à tes attaques, Choc au sol réduit sa vitesse d'attaque."},
            {"name": "L'engagement d'équipe", "keys": ["R", "E", "W", "AA"], "when": "Plusieurs ennemis sont groupés.",
             "how": "Force indomptable te fait foncer à grande vitesse, blesser les ennemis et les projeter en l'air ; enchaîne avec Choc au sol et tes attaques renforcées."},
            {"name": "Le harcèlement", "keys": ["Q", "E"], "when": "Tu veux gêner un carry.",
             "how": "Éclat sismique ralentit en volant la vitesse ; Choc au sol réduit brièvement la vitesse d'attaque : tu réduis fortement son efficacité."},
        ],
        "mistakes": [
            "Lancer Force indomptable sans cible à toucher en zone.",
            "Se faire toucher inutilement : ton bouclier se recharge si tu ne prends pas de dégâts.",
            "Négliger l'armure : elle renforce tes dégâts de Choc au sol.",
        ],
    }},
    "Katarina": {"fr": {
        "playstyle": (
            "Katarina est une assassine de burst dont les délais de récupération sont grandement réduits quand un champion qu'elle a blessé récemment meurt. "
            "Elle ramasse ses dagues pour blesser tous les ennemis proches, se téléporte avec Shunpo, et son ultime frappe les trois champions ennemis les plus proches pendant sa canalisation."
        ),
        "laning": (
            "Lame rebondissante rebondit sur les ennemis proches avant de tomber au sol : ramasse ensuite la dague pour infliger des dégâts en zone. "
            "Garde Shunpo pour te rapprocher ou fuir."
        ),
        "combos": [
            {"name": "Le combo de base", "keys": ["Q", "E", "W", "AA"], "when": "Un ennemi est à portée.",
             "how": "Lame rebondissante lance une dague, Shunpo te téléporte près de la cible, Préparation lance une dague dans les airs et te donne de la vitesse ; ramasse les dagues pour frapper les ennemis proches."},
            {"name": "L'ultime en canalisation", "keys": ["E", "R"], "when": "Plusieurs ennemis sont proches.",
             "how": "Lotus mortel projette des couteaux sur les trois champions ennemis les plus proches pendant la canalisation : place-toi avec Shunpo puis lance-le."},
            {"name": "La remise à zéro", "keys": ["Q", "E", "R"], "when": "Un champion blessé va mourir.",
             "how": "Quand un champion que tu as blessé meurt, tes délais sont fortement réduits : relance tes compétences pour enchaîner le suivant."},
        ],
        "mistakes": [
            "Lancer l'ultime en étant interrompue : il se canalise.",
            "Oublier de ramasser les dagues : ta passive en dépend.",
            "Utiliser Shunpo sans cible ni sortie.",
        ],
    }},
    "Rell": {"fr": {
        "playstyle": (
            "Rell est une tank d'engagement à deux formes : à cheval elle descend en piqué en projetant les ennemis dans les airs et gagne un bouclier, à pied elle gagne défenses, vitesse et portée d'attaque mais est ralentie. "
            "Sa passive vole de l'armure et de la résistance magique, et son ultime attire violemment les ennemis proches."
        ),
        "laning": (
            "Frappe dislocatrice brise les boucliers et étourdit sur une ligne. "
            "Ta passive te donne des dégâts magiques bonus et vole des résistances : engage-toi au corps à corps."
        ),
        "combos": [
            {"name": "L'engagement classique", "keys": ["W", "Q", "AA"], "when": "Ton équipe est prête à suivre.",
             "how": "Ferromancie te fait descendre du cheval, projette les ennemis proches dans les airs et te donne un bouclier ; Frappe dislocatrice étourdit sur la ligne."},
            {"name": "La joute avec un allié", "keys": ["E", "AA", "Q"], "when": "Un allié est à proximité.",
             "how": "Joute endiablée donne de la vitesse croissante à Rell et à l'allié, doublée vers les ennemis ; ta prochaine attaque provoque une explosion de dégâts magiques."},
            {"name": "L'ultime d'équipe", "keys": ["R", "W", "Q"], "when": "Les ennemis sont dispersés autour de toi.",
             "how": "Tempête magnétique les attire violemment vers toi puis continue de les attirer un bref instant en les blessant : ton équipe peut alors les cibler."},
        ],
        "mistakes": [
            "Rester à pied en oubliant que tu es ralentie.",
            "Lancer l'ultime sans allié pour profiter du regroupement.",
            "Utiliser Frappe dislocatrice sans vérifier la ligne de tir.",
        ],
    }},
    "Senna": {"fr": {
        "playstyle": (
            "Senna est une tireuse-support de portée : sa passive lui permet de libérer les âmes prises au piège dans la Brume noire, ce qui renforce ses dégâts, sa portée et ses chances de critique. "
            "Ombre perforante soigne les alliés et blesse les ennemis sur sa ligne, Dernière étreinte immobilise, et son ultime a une portée illimitée avec un bouclier pour les alliés touchés."
        ),
        "laning": (
            "Attaque les âmes libérées quand des unités meurent près de toi. "
            "Ton canon tire plus lentement mais inflige des dégâts supplémentaires et te donne une partie de la vitesse de déplacement de la cible."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "AA", "W"], "when": "Un allié est aligné avec l'ennemi.",
             "how": "Ombre perforante soigne les alliés et blesse les ennemis touchés ; tes attaques du canon profitent du bonus de vitesse de déplacement."},
            {"name": "L'immobilisation", "keys": ["W", "Q", "AA"], "when": "Un ennemi est à portée de Brume.",
             "how": "Dernière étreinte projette une vague de Brume : si elle touche un ennemi, il est immobilisé avec les ennemis proches après un court délai."},
            {"name": "L'ultime globale", "keys": ["R"], "when": "Tes alliés se battent loin de toi.",
             "how": "Ténèbres aveuglantes tire un rayon à portée illimitée : bouclier pour les alliés touchés, dégâts pour les ennemis au centre."},
        ],
        "mistakes": [
            "Ne pas récupérer les âmes : elles renforcent ton canon.",
            "Lancer Dernière étreinte sans que ton équipe puisse profiter de l'immobilisation.",
            "Utiliser l'ultime sans viser les alliés ou le centre ennemi.",
        ],
    }},
    "Hecarim": {"fr": {
        "playstyle": (
            "Hecarim est un jungler de vitesse : ses dégâts d'attaque augmentent d'un pourcentage de sa vitesse de déplacement bonus. "
            "Carnage augmente ses dégâts et réduit son délai à chaque coup, Charge dévastatrice repousse et inflige des dégâts selon la distance parcourue, et Légion des ombres charge en ligne avant d'effrayer à l'arrivée."
        ),
        "laning": (
            "Carnage blesse les ennemis proches ; s'il en touche au moins un, les suivants deviennent plus rapides et plus forts. "
            "Essence de la peur te soigne d'un pourcentage des dégâts subis par les ennemis proches."
        ),
        "combos": [
            {"name": "L'engagement de charge", "keys": ["E", "AA", "Q", "W"], "when": "Un ennemi est éloigné.",
             "how": "Charge dévastatrice augmente ta vitesse et te fait traverser les unités ; ta prochaine attaque repousse et inflige d'autant plus de dégâts que la distance parcourue est grande."},
            {"name": "Le combat d'équipe", "keys": ["R", "Q", "W"], "when": "Les ennemis sont regroupés.",
             "how": "Légion des ombres charge en ligne et effraie les ennemis proches à l'arrivée ; enchaîne avec Carnage et Essence de la peur."},
            {"name": "Le combat prolongé", "keys": ["Q", "Q", "W", "AA"], "when": "Tu es au corps à corps.",
             "how": "Carnage devient plus fort à chaque coup ; Essence de la peur t'apporte armure, résistance magique et des PV."},
        ],
        "mistakes": [
            "Attaquer sans vitesse de déplacement bonus : tes dégâts en dépendent.",
            "Utiliser Charge dévastatrice à trop courte distance : ses dégâts dépendent de la distance parcourue.",
            "Lancer l'ultime en oubliant qu'il charge devant toi.",
        ],
    }},
    "Zeri": {"fr": {
        "playstyle": (
            "Zeri est une tireuse dont les attaques infligent des dégâts magiques et sont traitées comme des compétences. "
            "Se déplacer et lancer Rafale stocke de l'énergie dans son paquetage ionique ; chargée à bloc, sa prochaine attaque inflige des dégâts supplémentaires. Son ultime la surcharge : elle gagne de la vitesse d'attaque et Rafale devient un triple tir."
        ),
        "laning": (
            "Rafale n'a pas de délai de récupération : tire-la souvent en te déplaçant pour charger ton paquetage. "
            "Laser électrocuteur ralentit et blesse ; s'il touche un mur, il devient un laser à longue portée."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "Q"], "when": "Un ennemi est à portée.",
             "how": "Rafale tire 7 balles qui infligent tes dégâts d'attaque au premier ennemi touché ; Laser électrocuteur ralentit, puis relance Rafale."},
            {"name": "La ruée perforante", "keys": ["E", "Q", "Q"], "when": "Tu veux engager ou fuir.",
             "how": "Charge ionique te fait ruer, renforce Rafale qui devient perforante et te fait bondir par-dessus les obstacles."},
            {"name": "La surcharge", "keys": ["R", "Q", "Q"], "when": "Un combat d'équipe s'engage.",
             "how": "Éruption électrique provoque une nova et te surcharge : bonus cumulable de vitesse d'attaque à chaque champion touché et Rafale en triple tir avec chaîne d'éclairs."},
        ],
        "mistakes": [
            "Ne pas te déplacer pendant tes tirs : ton paquetage se charge en mouvement.",
            "Utiliser l'ultime seule : tu dois toucher des champions pour cumuler la vitesse d'attaque.",
            "Lancer Charge ionique sans plan de sortie.",
        ],
    }},
    "Pyke": {"fr": {
        "playstyle": (
            "Pyke est un support-assassin qui régénère les dégâts récents quand il n'est pas vu, et dont les PV supplémentaires sont convertis en dégâts d'attaque. "
            "Harponnage attire un ennemi, Ressac fantôme étourdit sur son passage, Plongée spectrale le camoufle, et son ultime exécute les ennemis à peu de PV et octroie de l'or supplémentaire à l'allié qui l'assiste."
        ),
        "laning": (
            "Harponnage peut poignarder un ennemi devant toi ou l'attirer : choisis selon la distance. "
            "Reste hors de vue pour régénérer les dégâts récents."
        ),
        "combos": [
            {"name": "Le crochet", "keys": ["Q", "E", "AA"], "when": "Un ennemi est à portée de harpon.",
             "how": "Harponnage attire l'ennemi, Ressac fantôme laisse un fantôme qui étourdit les champions sur son passage à son retour."},
            {"name": "L'exécution", "keys": ["R", "R"], "when": "Plusieurs ennemis ont peu de PV.",
             "how": "Exécution abyssale fonce sur les ennemis à peu de PV pour les exécuter, ce qui te permet de relancer le sort et d'octroyer de l'or supplémentaire à un allié assistant."},
            {"name": "L'approche discrète", "keys": ["W", "Q"], "when": "Tu veux surprendre.",
             "how": "Plongée spectrale te camoufle avec un important bonus de vitesse qui diminue : approche puis harponne."},
        ],
        "mistakes": [
            "Chercher à augmenter tes PV max : ils sont convertis en dégâts d'attaque.",
            "Lancer l'ultime sur des ennemis avec beaucoup de PV.",
            "Utiliser Harponnage sans regarder les sbires.",
        ],
    }},
    "Ashe": {"fr": {
        "playstyle": (
            "Ashe est une tireuse de contrôle : ses attaques ralentissent leurs cibles et infligent des dégâts supplémentaires aux cibles affectées, et ses coups critiques appliquent un ralentissement renforcé. "
            "Rapace envoie son faucon en reconnaissance n'importe où sur la carte, et Flèche de cristal enchantée étourdit avec une durée qui augmente avec la distance."
        ),
        "laning": (
            "Attaque pour générer de la Concentration ; au maximum, Concentration du ranger augmente ta vitesse d'attaque. "
            "Salve inflige plus de dégâts en cône et applique Tir givrant."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["W", "AA", "AA"], "when": "Un ennemi est à portée.",
             "how": "Salve applique Tir givrant : tes attaques suivantes infligent des dégâts supplémentaires aux cibles affectées."},
            {"name": "Le combat d'équipe", "keys": ["Q", "AA", "AA", "W"], "when": "Un combat d'équipe est engagé.",
             "how": "Concentration du ranger consomme tes effets pour augmenter temporairement ta vitesse d'attaque et transformer tes attaques en volées de flèches."},
            {"name": "L'ultime longue distance", "keys": ["R"], "when": "Un engagement ou une fuite est en cours.",
             "how": "Flèche de cristal enchantée étourdit le premier champion touché : plus elle voyage loin, plus l'étourdissement est long, et les unités proches subissent dégâts et ralentissement."},
        ],
        "mistakes": [
            "Utiliser l'ultime à trop courte distance : l'étourdissement est plus court.",
            "Oublier Rapace : la vision qu'il donne est sa vraie valeur.",
            "Gaspiller Concentration du ranger avant un combat.",
        ],
    }},
    "Irelia": {"fr": {
        "playstyle": (
            "Irelia est une combattante de mobilité dont les compétences lui donnent de la vitesse d'attaque cumulable. "
            "Rush fatal annule son délai s'il tue sa cible ou touche une cible marquée, Duo parfait blesse, étourdit et marque entre deux lames, et Pointe de l'avant-garde crée un mur qui blesse et ralentit."
        ),
        "laning": (
            "Enchaîne Rush fatal sur les sbires pour te rapprocher : il annule son délai de récupération s'il tue. "
            "Danse de défi te protège des dégâts physiques pendant la charge."
        ),
        "combos": [
            {"name": "Le combo d'engagement", "keys": ["E", "Q", "AA", "W"], "when": "Un ennemi est à portée.",
             "how": "Duo parfait blesse, étourdit et marque ; Rush fatal sur une cible marquée annule son délai : tu peux enchaîner et empiler la Ferveur ionienne."},
            {"name": "L'ultime de mur", "keys": ["R", "Q", "E", "W"], "when": "Un combat d'équipe s'engage.",
             "how": "Pointe de l'avant-garde blesse et marque les champions touchés puis forme un mur qui ralentit ; profite des marques pour relancer Rush fatal."},
            {"name": "La défense physique", "keys": ["W", "AA"], "when": "Un ennemi attaque avec des dégâts physiques.",
             "how": "Danse de défi charge une attaque et te fait subir moins de dégâts physiques ; plus la charge dure, plus les dégâts augmentent."},
        ],
        "mistakes": [
            "Utiliser Rush fatal sans sbire ou marque pour revenir.",
            "Charger Danse de défi sans protection contre les dégâts magiques.",
            "Négliger la vitesse d'attaque de ta passive : elle nécessite de toucher avec tes compétences.",
        ],
    }},
    "Xerath": {"fr": {
        "playstyle": (
            "Xerath est un mage de longue portée : Rayon arcanique, Œil de la destruction et Orbe d'électrocution harcèlent depuis très loin. "
            "Ses attaques restaurent du mana et l'ultime le fait s'immobiliser pour tirer plusieurs barrages à longue portée."
        ),
        "laning": (
            "Rayon arcanique inflige des dégâts à toutes les cibles touchées : lance-le pour toucher ennemis et sbires. "
            "Œil de la destruction ralentit dans la zone, avec plus d'effet au centre."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "W", "E"], "when": "Un ennemi est à portée.",
             "how": "Rayon arcanique inflige des dégâts en ligne, Œil de la destruction ralentit (davantage au centre), Orbe d'électrocution étourdit et blesse."},
            {"name": "L'étourdissement de contrôle", "keys": ["E", "W", "Q"], "when": "Un ennemi plonge sur toi.",
             "how": "Orbe d'électrocution étourdit d'abord, puis Œil de la destruction et Rayon arcanique font les dégâts."},
            {"name": "L'ultime de siège", "keys": ["R", "R", "R"], "when": "Les ennemis sont visibles à longue portée.",
             "how": "Rite arcanique t'immobilise pour tirer plusieurs barrages : lance-le quand tu es protégé."},
        ],
        "mistakes": [
            "Lancer l'ultime sans protection : tu es immobilisé pendant les tirs.",
            "Gaspiller Orbe d'électrocution : c'est ton seul étourdissement.",
            "Négliger le mana : tes attaques le restaurent régulièrement.",
        ],
    }},
}
