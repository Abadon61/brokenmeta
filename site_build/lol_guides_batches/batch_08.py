"""Guides rédigés, lot 8. Écrits d'après les textes officiels des capacités (Data Dragon)."""

BATCH = {
    "Rengar": {"fr": {
        "playstyle": (
            "Rengar est un assassin de la jungle qui bondit sur ses cibles depuis les hautes herbes. "
            "Chaque compétence génère de la Férocité, et au maximum la compétence suivante est renforcée. Chasseur-né le camoufle, révèle le champion ennemi le plus proche et réduit l'armure de sa cible."
        ),
        "laning": (
            "Bondis depuis les hautes herbes avec ton attaque de base pour ouvrir l'échange. "
            "Garde ta Férocité : au maximum, ta prochaine compétence est renforcée."
        ),
        "combos": [
            {"name": "L'embuscade", "keys": ["AA", "Q", "AA", "E", "W"], "when": "Tu es dans les hautes herbes près d'un ennemi.",
             "how": "Ton attaque te fait bondir, Esprit sauvage poignarde pour des dégâts bonus, Bolas ralentit (immobilise avec la Férocité), Rugissement te soigne."},
            {"name": "L'ultime de chasse", "keys": ["R", "AA", "Q", "E"], "when": "Tu traques un carry.",
             "how": "Chasseur-né te camoufle, révèle le champion ennemi le plus proche à très longue distance, te donne de la vitesse, te permet de bondir sans hautes herbes et réduit l'armure de la cible."},
            {"name": "La sortie", "keys": ["W", "E"], "when": "Tu es sous contrôle.",
             "how": "Rugissement renforcé par la Férocité brise les effets de contrôle de foule ; Bolas immobilise la cible poursuivante."},
        ],
        "mistakes": [
            "Dépenser ta Férocité trop vite : au maximum, tes compétences sont renforcées.",
            "Engager sans t'être placé dans les hautes herbes.",
            "Lancer l'ultime sans cible prioritaire : il révèle le champion le plus proche.",
        ],
    }},
    "Vi": {"fr": {
        "playstyle": (
            "Vi est une combattante d'engagement : Brise-coffre l'entraîne vers l'avant en repoussant les ennemis touchés, et son ultime fonce sur un ennemi en écartant ceux sur son passage. "
            "Sa passive charge un bouclier activé quand elle frappe un ennemi avec une compétence."
        ),
        "laning": (
            "Coups fracassants brisent l'armure de l'adversaire et augmentent ta vitesse d'attaque : utilise tes attaques pour les cumuler. "
            "Force implacable traverse la cible et blesse ceux derrière."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["Q", "AA", "E", "AA"], "when": "Un ennemi est à portée de Brise-coffre.",
             "how": "Brise-coffre te propulse et repousse les ennemis touchés en appliquant Coups fracassants ; Force implacable traverse la cible."},
            {"name": "La capture", "keys": ["R", "AA", "Q", "E"], "when": "Le carry adverse est isolé.",
             "how": "Mise en demeure fonce sur l'ennemi en écartant ceux sur le passage, puis à l'arrivée le projette, saute par-dessus et le renvoie au sol."},
            {"name": "Le bouclier", "keys": ["Q", "AA"], "when": "Tu entres au corps à corps.",
             "how": "Frapper avec une compétence active le bouclier chargé de ta passive."},
        ],
        "mistakes": [
            "Utiliser Brise-coffre sans cible : il te fait avancer.",
            "Lancer l'ultime sur un ennemi hors de portée de tes alliés.",
            "Oublier de charger ton bouclier avant l'engagement.",
        ],
    }},
    "Hwei": {"fr": {
        "playstyle": (
            "Hwei est un mage-artiste dont les compétences se divisent en trois sujets qui remplacent chacun ses compétences : Désastres (dégâts : Feu dévastateur, Éclair enflammé, Champ de lave), Sérénités (utilité : Ruisseau, Étang, Nuit étoilée) et Tourments (contrôle : Visage effroyable, Œil des abysses, Mâchoires chatoyantes). "
            "Sa passive termine une signature qui explose sous un ennemi touché par deux compétences blessantes."
        ),
        "laning": (
            "Touche un ennemi avec deux compétences blessantes pour terminer la signature : elle explose après un court délai. "
            "Choisis ton sujet selon la situation : dégâts, soutien ou contrôle."
        ),
        "combos": [
            {"name": "Le combo de signature", "keys": ["Q", "Q", "Q"], "when": "Un ennemi est à portée.",
             "how": "Avec Désastres, touche avec deux compétences blessantes : la signature apparaît sous l'ennemi et explose après un court délai."},
            {"name": "Le contrôle", "keys": ["E", "E", "E"], "when": "Un ennemi plonge.",
             "how": "Tourments remplace tes compétences par des contrôles de foule : Visage effroyable, Œil des abysses ou Mâchoires chatoyantes selon la situation."},
            {"name": "L'ultime de peinture", "keys": ["R", "Q", "E"], "when": "Un combat s'engage.",
             "how": "Vision de désespoir fait du premier champion touché le centre d'une peinture grandissante qui ralentit et blesse ; elle explose à sa taille limite ou à la mort du champion."},
        ],
        "mistakes": [
            "Changer de sujet au mauvais moment : chaque sujet remplace tes compétences.",
            "Oublier la signature : deux compétences blessantes sont nécessaires.",
            "Lancer Vision de désespoir sur un ennemi qui peut la fuir.",
        ],
    }},
    "Rakan": {"fr": {
        "playstyle": (
            "Rakan est un support d'engagement mobile : Entrée triomphale le fait foncer et projeter les ennemis, Valse guerrière le fait voler vers un allié en lui donnant un bouclier, et son ultime le rend plus rapide et charme les ennemis touchés. "
            "Sa passive lui donne périodiquement un bouclier."
        ),
        "laning": (
            "Rémige rayonnante soigne tes alliés si elle touche un champion ou un monstre épique. "
            "Valse guerrière est relançable sans coût pendant un court instant : enchaîne pour te repositionner."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["W", "R", "Q"], "when": "Un carry ennemi est à portée.",
             "how": "Entrée triomphale te fait foncer en projetant les ennemis proches, Danse ultime augmente ta vitesse et charme les ennemis touchés, Rémige rayonnante blesse."},
            {"name": "Le sauvetage", "keys": ["E", "E"], "when": "Un allié est en danger.",
             "how": "Valse guerrière t'envole vers un champion allié en lui donnant un bouclier ; relance-la sans coût pour prolonger le mouvement."},
            {"name": "Le harcèlement", "keys": ["Q", "AA"], "when": "Un ennemi est à portée.",
             "how": "Rémige rayonnante inflige des dégâts magiques et soigne tes alliés si elle touche un champion."},
        ],
        "mistakes": [
            "Engager sans allié à proximité pour suivre.",
            "Gaspiller Entrée triomphale sans cible.",
            "Oublier de relancer Valse guerrière.",
        ],
    }},
    "KSante": {"fr": {
        "playstyle": (
            "K'Santé est un tank-combattant à deux temps : ses compétences marquent ses cibles et renforcent sa prochaine attaque, et son ultime lui fait repousser un ennemi au travers de tout mur avant de passer en forme Grand jeu. "
            "En Grand jeu, il inflige plus de dégâts et de soins, ses compétences sont transformées, mais ses défenses baissent."
        ),
        "laning": (
            "Coups de ntofo attire les ennemis à 2 effets cumulés : place-les pour l'attirer. "
            "Pour Nazumah ! réduit les dégâts subis avant de te ruer pour repousser et étourdir."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "Q", "AA", "E"], "when": "Un ennemi est à courte portée.",
             "how": "Deux Coups de ntofo font une onde de choc qui attire les ennemis, Jeu de jambes te donne un bouclier, ton attaque profite de la marque de ta passive."},
            {"name": "L'engagement", "keys": ["W", "AA", "Q"], "when": "Un ennemi est à portée de ruée.",
             "how": "Pour Nazumah ! charge ton attaque et te protège avant de te ruer en repoussant et étourdissant les ennemis."},
            {"name": "L'ultime au mur", "keys": ["R", "Q", "E", "AA"], "when": "Un ennemi est près d'un mur.",
             "how": "Grand jeu repousse l'ennemi au travers du mur puis te rue sur lui : passe en forme Grand jeu pour des dégâts et des soins renforcés."},
        ],
        "mistakes": [
            "Rester en forme Grand jeu sans profiter du burst : tes défenses sont réduites.",
            "Lancer l'ultime sans mur à proximité.",
            "Ignorer la marque de ta passive.",
        ],
    }},
    "Kayn": {"fr": {
        "playstyle": (
            "Kayn est un jungler qui combat Rhaast, le Darkin de son arme : soit Rhaast triomphe (soin selon les dégâts de compétence infligés aux champions), soit Kayn le maîtrise et devient l'Assassin de l'ombre (dégâts supplémentaires en début de combat). "
            "Passe-muraille lui permet de traverser le terrain et son ultime le cache dans un ennemi pour infliger d'énormes dégâts."
        ),
        "laning": (
            "Moisson cruelle te rue puis frappe : les deux infligent des dégâts. "
            "Passe-muraille te permet d'éviter les obstacles et de te repositionner."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "W"], "when": "Un ennemi est à portée.",
             "how": "Moisson cruelle te rue puis frappe, Entaille sombre blesse et ralentit sur une ligne."},
            {"name": "L'assassinat", "keys": ["E", "R", "Q", "W"], "when": "Un carry est isolé derrière un mur.",
             "how": "Passe-muraille te fait traverser le terrain, Intrusion obscure te cache dans le corps de l'ennemi puis inflige d'énormes dégâts quand tu en sors."},
            {"name": "La fuite", "keys": ["E", "W"], "when": "Tu dois t'échapper.",
             "how": "Passe-muraille te permet de traverser le terrain pour couper la poursuite."},
        ],
        "mistakes": [
            "Utiliser l'ultime sans cible qui ne puisse pas se soigner ou fuir.",
            "Ne pas choisir ta forme selon ta situation.",
            "Traverser le terrain sans sortie.",
        ],
    }},
    "MonkeyKing": {"fr": {
        "playstyle": (
            "Wukong est un jungler de combat dont l'armure et la régénération augmentent en combat (effet cumulable). "
            "Écrasement réduit l'armure, Guerrier espiègle le rend invisible avec un clone, Nimbus le rue sur une cible avec des images qui attaquent ses voisins, et Cyclone projette les ennemis en l'air."
        ),
        "laning": (
            "Écrasement a une portée plus longue et réduit l'armure de la cible : ouvre l'échange avec lui. "
            "Ta passive t'apporte de la défense au fil du combat."
        ),
        "combos": [
            {"name": "L'engagement", "keys": ["E", "Q", "AA", "W"], "when": "Un ennemi est à portée de Nimbus.",
             "how": "Nimbus te rue sur l'ennemi en envoyant des images qui attaquent les ennemis proches, Écrasement réduit son armure, Guerrier espiègle te rend invisible avec un clone."},
            {"name": "Le combat d'équipe", "keys": ["W", "R", "Q"], "when": "Plusieurs ennemis sont groupés.",
             "how": "Guerrier espiègle te cache, Cyclone augmente ta vitesse et projette en l'air les ennemis touchés."},
            {"name": "La sortie", "keys": ["W", "E"], "when": "Tu es en danger.",
             "how": "Guerrier espiègle te rend invisible et te fait te ruer en laissant un clone."},
        ],
        "mistakes": [
            "Lancer Cyclone sans cible groupée.",
            "Oublier le clone de Guerrier espiègle.",
            "Utiliser Nimbus sans plan pour la suite.",
        ],
    }},
    "Nocturne": {"fr": {
        "playstyle": (
            "Nocturne est un jungler dont l'attaque frappe régulièrement en zone avec des dégâts supplémentaires et un soin. "
            "Crépuscule laisse une Lueur qui lui donne vitesse, dégâts et traversée des unités, Linceul des ténèbres bloque une compétence, Horreur indicible terrifie et Paranoïa réduit la vision ennemie avant un bond."
        ),
        "laning": (
            "Tes attaques réduisent le délai de ta passive : attaque souvent. "
            "Reste dans la Lueur crépusculaire pour bénéficier du bonus de vitesse et de dégâts."
        ),
        "combos": [
            {"name": "L'échange", "keys": ["Q", "AA", "E"], "when": "Un ennemi est à portée.",
             "how": "Crépuscule blesse et laisse une Lueur ; tes attaques dans la lueur sont renforcées, Horreur indicible inflige des dégâts par seconde et terrifie s'il reste à portée."},
            {"name": "La protection", "keys": ["W", "AA"], "when": "Un ennemi lance une compétence importante.",
             "how": "Linceul des ténèbres crée une barrière capable de bloquer une compétence ennemie et double le bonus de vitesse d'attaque en cas de blocage."},
            {"name": "L'assassinat", "keys": ["R", "Q", "E", "AA"], "when": "Un carry est isolé.",
             "how": "Paranoïa réduit le champ de vision des ennemis et supprime la vision de leurs alliés ; projette-toi sur un champion proche puis enchaîne."},
        ],
        "mistakes": [
            "Utiliser Linceul des ténèbres sans anticiper la compétence à bloquer.",
            "Lancer l'ultime sans cible proche.",
            "Quitter la Lueur crépusculaire : tu perds ton bonus.",
        ],
    }},
    "Soraka": {"fr": {
        "playstyle": (
            "Soraka est une soigneuse : Infusion astrale sacrifie une partie de ses PV pour soigner un allié, Souhait soigne toute l'équipe à distance, et sa passive la fait courir plus vite vers les alliés affaiblis. "
            "Appel de l'étoile ralentit et la soigne si elle touche un champion, Équinoxe réduit au silence puis immobilise ceux qui restent."
        ),
        "laning": (
            "Appel de l'étoile te soigne quand il touche un champion : harcèle avec. "
            "Infusion astrale a un court délai mais te coûte des PV : surveille les tiens."
        ),
        "combos": [
            {"name": "Le harcèlement", "keys": ["Q", "AA", "Q"], "when": "Un ennemi est à portée.",
             "how": "Appel de l'étoile inflige des dégâts magiques, ralentit et te soigne si un champion est touché."},
            {"name": "Le contrôle", "keys": ["E", "Q"], "when": "Un ennemi plonge sur ton carry.",
             "how": "Équinoxe crée une zone qui réduit au silence tous les ennemis, puis immobilise ceux qui s'y trouvent encore quand elle disparaît."},
            {"name": "Le sauvetage global", "keys": ["W", "R"], "when": "Ton équipe est à bas PV.",
             "how": "Infusion astrale soigne un allié en sacrifiant tes PV ; Souhait rend immédiatement des PV à tous les alliés et à toi."},
        ],
        "mistakes": [
            "Spammer Infusion astrale à bas PV.",
            "Lancer l'ultime trop tôt : il soigne au moment de l'utilisation.",
            "Placer Équinoxe sans que les ennemis y restent.",
        ],
    }},
    "Fizz": {"fr": {
        "playstyle": (
            "Fizz est un assassin agile : il traverse les unités et bénéficie d'une réduction de dégâts fixe contre toutes les sources. "
            "Frappe de l'oursin le fait traverser sa cible, Trident marin ajoute un saignement, Joueur/Filou le rend impossible à cibler, et Pêche au gros lance un poisson qui attire un requin."
        ),
        "laning": (
            "Attaque avec Trident marin pour le saignement et les dégâts renforcés. "
            "Garde Joueur/Filou pour éviter une compétence décisive."
        ),
        "combos": [
            {"name": "Le burst", "keys": ["R", "W", "Q", "E"], "when": "Un carry est à portée.",
             "how": "Pêche au gros ralentit la cible et fait surgir un requin qui la projette et repousse les ennemis proches ; enchaîne avec Trident marin, Frappe de l'oursin et Joueur/Filou."},
            {"name": "L'échange", "keys": ["W", "AA", "Q"], "when": "Un ennemi est à portée.",
             "how": "Trident marin fait saigner et renforce tes attaques ; Frappe de l'oursin te fait traverser la cible en infligeant des dégâts magiques."},
            {"name": "L'esquive", "keys": ["E", "E"], "when": "Un ennemi lance une compétence décisive.",
             "how": "Joueur/Filou te rend impossible à cibler ; depuis cette position, tu peux frapper le sol ou sauter à nouveau."},
        ],
        "mistakes": [
            "Lancer l'ultime sans avoir vérifié la trajectoire du poisson.",
            "Utiliser Joueur/Filou hors du besoin : son délai est long au début.",
            "Ne pas profiter de la traversée des unités pour te repositionner.",
        ],
    }},
}
