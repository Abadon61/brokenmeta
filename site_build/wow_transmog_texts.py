"""Texts of the transmog simulator page (/wow-forever/transmogrification/), FR + EN. The page script's strings live under `js` (served as JSON in #tmI18n)."""

_OPTIONS_FR = {
    'Skin Color': 'Couleur de peau', 'Face': 'Visage', 'Hair Style': 'Coiffure', 'Hair Color': 'Couleur des cheveux', 'Facial Hair': 'Pilosité faciale',
    'Face Shape': 'Forme du visage', 'Eyebrows': 'Sourcils', 'Eye Color': 'Couleur des yeux', 'Eye Style': 'Style des yeux', 'Beard': 'Barbe', 'Mustache': 'Moustache',
    'Piercings': 'Piercings', 'Earrings': 'Boucles d’oreilles', 'Earring Color': 'Couleur des boucles', 'Makeup': 'Maquillage', 'Ears': 'Oreilles', 'Grime': 'Crasse',
    'Tusks': 'Défenses', 'Horns': 'Cornes', 'Markings': 'Marques', 'Markings Color': 'Couleur des marques', 'Face Paint': 'Peinture de guerre', 'Face Paint Color': 'Couleur de la peinture',
    'Jaw Features': 'Mâchoire', 'Face Features': 'Traits du visage', 'Eye Glow': 'Lueur des yeux', 'Hair': 'Cheveux', 'Foremane': 'Crinière avant', 'Blindfold': 'Bandeau',
    'Body Tattoo': 'Tatouage du corps', 'Body Tattoo Color': 'Couleur du tatouage', 'Face Tattoo': 'Tatouage du visage', 'Face Tattoo Color': 'Couleur du tatouage de visage',
    'Feather Color': 'Couleur des plumes', 'Feathers': 'Plumes', 'Eyebrow Style': 'Style des sourcils', 'Eyesight': 'Regard', 'Jewelry Color': 'Couleur des bijoux', 'Skin': 'Peau',
}

TXT = {
    "fr": {
        "kicker": "World of Warcraft: Forever · Transmogrification",
        "title": "Transmogrification WoW Forever : simulateur 3D",
        "desc": "Essayez les apparences d'armure et d'arme de WoW: Forever sur votre personnage en 3D : race, coiffure, couleurs, classe, armes dégainées ou rangées.",
        "h1": "Simulateur de transmogrification",
        "intro": "Choisissez une race, personnalisez votre personnage, puis essayez n'importe quelle pièce d'équipement du niveau 1 à 60 : le rendu est en 3D, directement dans votre navigateur.",
        "chip1": "9 races · 18 modèles", "chip2": "Environ 10 000 objets", "chip3": "Armes dégainées ou rangées",
        "h_how": "Comment l'utiliser",
        "how": [
            "Choisissez la race et le modèle (1 ou 2), puis réglez le visage, les cheveux et les couleurs.",
            "Choisissez votre classe pour ne voir que les objets qu'elle peut porter (ou laissez « Toutes »).",
            "Cliquez sur un emplacement, cherchez un objet : en passant la souris dessus vous l'essayez sur le personnage, en cliquant vous le gardez.",
            "Pour les armes, choisissez dégainée, rangée sur le dos ou à la taille (les armes à deux mains vont toujours sur le dos). Faites tourner le personnage à la souris.",
        ],
        "h_limits": "Ce que la page ne fait pas encore",
        "limits": [
            "Le personnage est en pose fixe : pas d'animation, les vêtements ne bougent pas.",
            "Pas de pièces de classe spéciales ni d'effets d'enchantement.",
            "Les apparences viennent des données du jeu WoW: Forever (niveau 60 maximum) ; l'essayage montre l'apparence, pas les statistiques de l'objet.",
            "Certains objets rares (capes à plusieurs textures, pièces d'armure très particulières) peuvent s'afficher imparfaitement.",
        ],
        "source": "Modèles, textures et apparences : données du client WoW: Forever, publiées par wago.tools. World of Warcraft et ses données appartiennent à Blizzard Entertainment.",
        "noscript": "Le simulateur a besoin de JavaScript et du WebGL de votre navigateur.",
        "js": {
            "loading": "Chargement…", "error": "Erreur :",
            "races": {"human": "Humain", "dwarf": "Nain", "nightelf": "Elfe de la nuit", "gnome": "Gnome", "orc": "Orc", "undead": "Mort-vivant", "tauren": "Tauren", "troll": "Troll", "skyborne": "Éolide"},
            "classes": {"WARRIOR": "Guerrier", "PALADIN": "Paladin", "HUNTER": "Chasseur", "ROGUE": "Voleur", "PRIEST": "Prêtre", "SHAMAN": "Chaman", "MAGE": "Mage", "WARLOCK": "Démoniste", "DRUID": "Druide"},
            "all": "Toutes", "no_filter": "Aucun filtre", "class_hint": "Seuls les objets que {cls} peut porter sont proposés.",
            "slots": {"head": "Tête", "shoulder": "Épaules", "back": "Dos", "chest": "Torse", "shirt": "Chemise", "tabard": "Tabard", "wrist": "Poignets", "hands": "Mains", "waist": "Taille",
                      "legs": "Jambes", "feet": "Pieds", "mainhand": "Main droite", "offhand": "Main gauche", "ranged": "À distance"},
            "armor": {"0": "Divers", "1": "Tissu", "2": "Cuir", "3": "Mailles", "4": "Plaques", "5": "Cosmétique", "6": "Boucliers"},
            "weapon": {"0": "Haches", "1": "Haches 2M", "2": "Arcs", "3": "Armes à feu", "4": "Masses", "5": "Masses 2M", "6": "Armes d’hast", "7": "Épées", "8": "Épées 2M", "10": "Bâtons",
                       "13": "Armes de pugilat", "14": "Divers", "15": "Dagues", "16": "Armes de jet", "18": "Arbalètes", "19": "Baguettes", "20": "Cannes à pêche"},
            "weapon_other": "Arme", "held": "Tenu en main gauche",
            "stance_title": "Armes : dégainées ou rangées", "stance_hand": "Dégainée", "stance_back": "Dos", "stance_hip": "Taille", "draw_all": "Tout dégainer", "stow_all": "Tout ranger",
            "search": "Rechercher dans {slot}…", "remove": "Retirer", "close": "Fermer", "lvl": "niv.", "count": "{n} objets", "count_more": "{n} sur {total} : affinez la recherche",
            "appearance": "Apparence", "colors": "Couleurs", "style": "Style", "prev": "Précédent", "next": "Suivant", "options": _OPTIONS_FR,
        },
        "labels": {"race": "Race", "model1": "Modèle 1", "model2": "Modèle 2", "random": "Aléatoire", "reset": "Réinitialiser", "cls": "Classe (filtre les objets)", "equip": "Équipement"},
    },
    "en": {
        "kicker": "World of Warcraft: Forever · Transmog",
        "title": "WoW Forever transmog simulator in 3D",
        "desc": "Try WoW: Forever armor and weapon looks on your character in 3D: race, hair, colors, class, weapons drawn or sheathed. Free, in your browser.",
        "h1": "Transmog simulator",
        "intro": "Pick a race, customize your character, then try any piece of gear from level 1 to 60: it renders in 3D, right in your browser.",
        "chip1": "9 races · 18 models", "chip2": "About 10,000 items", "chip3": "Weapons drawn or sheathed",
        "h_how": "How to use it",
        "how": [
            "Pick the race and model (1 or 2), then set the face, hair and colors.",
            "Pick your class to see only the items it can wear (or leave \"All\").",
            "Click a slot and search for an item: hovering tries it on the character, clicking keeps it.",
            "For weapons, choose drawn, sheathed on the back or at the hip (two-handers always go on the back). Drag to rotate the character.",
        ],
        "h_limits": "What the page does not do yet",
        "limits": [
            "The character is in a fixed pose: no animation, clothes do not move.",
            "No special class pieces and no enchant glow effects.",
            "Looks come from the WoW: Forever game data (level 60 maximum); trying an item shows its look, not its stats.",
            "Some rare items (cloaks with several textures, unusual armor pieces) may render imperfectly.",
        ],
        "source": "Models, textures and appearances: WoW: Forever client data, published by wago.tools. World of Warcraft and its data belong to Blizzard Entertainment.",
        "noscript": "The simulator needs JavaScript and your browser's WebGL.",
        "js": {
            "loading": "Loading…", "error": "Error:",
            "races": {"human": "Human", "dwarf": "Dwarf", "nightelf": "Night Elf", "gnome": "Gnome", "orc": "Orc", "undead": "Undead", "tauren": "Tauren", "troll": "Troll", "skyborne": "Skyborne"},
            "classes": {"WARRIOR": "Warrior", "PALADIN": "Paladin", "HUNTER": "Hunter", "ROGUE": "Rogue", "PRIEST": "Priest", "SHAMAN": "Shaman", "MAGE": "Mage", "WARLOCK": "Warlock", "DRUID": "Druid"},
            "all": "All", "no_filter": "No filter", "class_hint": "Only items a {cls} can wear are listed.",
            "slots": {"head": "Head", "shoulder": "Shoulders", "back": "Back", "chest": "Chest", "shirt": "Shirt", "tabard": "Tabard", "wrist": "Wrists", "hands": "Hands", "waist": "Waist",
                      "legs": "Legs", "feet": "Feet", "mainhand": "Main hand", "offhand": "Off hand", "ranged": "Ranged"},
            "armor": {"0": "Misc", "1": "Cloth", "2": "Leather", "3": "Mail", "4": "Plate", "5": "Cosmetic", "6": "Shields"},
            "weapon": {"0": "Axes", "1": "2H Axes", "2": "Bows", "3": "Guns", "4": "Maces", "5": "2H Maces", "6": "Polearms", "7": "Swords", "8": "2H Swords", "10": "Staves",
                       "13": "Fist weapons", "14": "Misc", "15": "Daggers", "16": "Thrown", "18": "Crossbows", "19": "Wands", "20": "Fishing poles"},
            "weapon_other": "Weapon", "held": "Held in off hand",
            "stance_title": "Weapons: drawn or sheathed", "stance_hand": "Drawn", "stance_back": "Back", "stance_hip": "Hip", "draw_all": "Draw all", "stow_all": "Sheathe all",
            "search": "Search {slot}…", "remove": "Remove", "close": "Close", "lvl": "lvl", "count": "{n} items", "count_more": "{n} of {total}: narrow the search",
            "appearance": "Appearance", "colors": "Colors", "style": "Style", "prev": "Previous", "next": "Next", "options": {},
        },
        "labels": {"race": "Race", "model1": "Model 1", "model2": "Model 2", "random": "Random", "reset": "Reset", "cls": "Class (filters items)", "equip": "Equipment"},
    },
}

if __name__ == "__main__":
    for lang, t in TXT.items():
        print(lang, len(t["title"]), len(t["desc"]))
