"""BrokenMeta's own WoW: Forever news articles (/wow-forever/actualites/<slug>/).

Why (SEO pass 2026-10-04): the news page is a headline index that sends readers to Wowhead / Blizzard. Our own
articles start from one of those news items and add what only this site has: simulated numbers from our engines,
the dungeon loot data, links to the class guides. The user wants an article for every class or item buff/nerf,
even when Wowhead was first, because tuning is what the site is about.

Rules for every article:
  - facts from the cited source, rewritten (never copied); our own analysis clearly separated and its method stated;
  - `draft: True` until the user has proof-read it: a draft is rendered with noindex, left out of the sitemap,
    the news page and the home page, so it can be previewed at its URL without being published;
  - `updated` moves when the text changes (shown on the page and in NewsArticle.dateModified);
  - `kind` is the overall verdict shown as a coloured badge on the article and its card: "up", "nerf" or "eq"
    (balance change: neither clearly better nor worse);
  - keywords players actually search ("WoW Forever", the class + spec, "build", "patch", "nerf"/"buff", the item
    names) go into the title, the first paragraph, the h2s and the FAQ, written as normal sentences.

Two formats (`format`, default "article"):
  - "article": a full analysis (simulation, data), written for class/item buffs and nerfs;
  - "brief" (brève, 2026-10-04): a short page for any other important headline, so the reader stays on the site:
    a lede of 3-4 sentences rewritten in our own words, then a "Ce que ça change pour toi" / "What it means for
    you" h2 with a few lines and `links` to our own pages (class guide, dungeon page, simulator, talents...).
    A brief WITHOUT links is rendered noindex (a bare summary of someone else's news adds nothing for Google).
    `kind` may be None for a brief (no up/nerf verdict).

Blocks of `body` (per language): ("p", text), ("h2", text), ("list", [text, ...]), ("table", {"head": [...],
"rows": [[...], ...]}), ("note", text). `faq` is a list of (question, answer).

Inline markup (rendered by the `artfmt` filter in build_site.py, after HTML-escaping the text):
  **bold**                      key words
  {up} {nerf} {eq}              coloured badge UP / NERF / ÉQUILIBRAGE (BALANCE in English), at the start of a line
  [up]x[/up] [nerf]x[/nerf] [eq]x[/eq]   text coloured green / red / orange (numbers, verdicts)
  {i:icon_name}                 small game icon (wow.zamimg.com icon name, the CDN the site already uses)

Visual blocks (so an article is not a wall of text): ("cards", [(icon_name, title, subtitle, kind), ...]) tiles with a
big icon and a UP/NERF/ÉQUILIBRAGE badge; ("bars", {"unit": "DPS", "rows": [(label, before, after), ...]}) a
before/after bar chart drawn in CSS.
"""
import os
import re

ARTICLES = [
    {
        "slug": "guerrier-fureur-buff-bloodthirst",
        "date": "2026-10-04",
        "updated": "2026-10-04",
        "draft": False,
        "tag": "tuning",
        "kind": "up",
        "class": "warrior",
        "image": "assets/img/spec/warrior-fury.png",
        "sources": [
            ("Wowhead : Warrior Updates in Today's WoW: Forever Beta Build (2 Oct. 2026)",
             "https://www.wowhead.com/forever/news/warrior-updates-in-todays-wow-forever-beta-build-383230"),
        ],
        "fr": {
            "title": "Buff du Guerrier Fureur dans WoW: Forever : +3,9 % de DPS",
            "description": "Bloodthirst passe de 35 à 45 % de puissance d'attaque, les critiques rendent plus de rage. Simulé au niveau 60 : +3,9 % de DPS en Fureur, +0,9 % en Armes.",
            "h1": "Guerrier Fureur : le buff du 2 octobre dans WoW Forever, simulé",
            "lede": "Le patch de la bêta de **WoW Forever** du 2 octobre 2026 est un **buff pour le Guerrier Fureur** : plus de rage sur les coups critiques, un **Bloodthirst** (Sanguinaire) plus fort et un arbre de talents Fureur réorganisé. Nous avons passé les changements chiffrés dans notre simulateur DPS niveau 60 : [up]+3,9 % de DPS en Fureur[/up], [up]+0,9 % en Armes[/up].",
            "body": [
                ("cards", [("spell_nature_bloodlust", "Sanguinaire (Bloodthirst)", "35 % → 45 % de puissance d'attaque", "up"),
                           ("ability_whirlwind", "Tourbillon (Whirlwind)", "Toujours avec les deux armes", "up"),
                           ("ability_dualwield", "Spécialisation Ambidextrie", "Plus de toucher en main gauche", "nerf"),
                           ("ability_ghoulfrenzy", "Rafale (Flurry)", "Demande Souhait mortel au lieu d'Enrager", "eq")]),
                ("h2", "Patch du Guerrier dans WoW Forever : tous les changements"),
                ("list", [
                    "{up} **Rage des coups critiques** : un critique rapporte maintenant [up]100 % de rage en plus[/up] au lieu de 75 %.",
                    "{up} {i:spell_nature_bloodlust} **Bloodthirst** (Sanguinaire) : son ratio de puissance d'attaque passe de 35 % à [up]45 %[/up].",
                    "{up} {i:ability_whirlwind} **Whirlwind** (Tourbillon) frappe désormais toujours avec les deux armes, sans talent. **Raging Blows** réduit de 3 le coût en rage de Cleave et de Whirlwind.",
                    "{up} Nouveau talent **Furious Precision** (rang 3 de Fureur) : [up]+4/7/10 % de chances de toucher[/up] avec la main gauche.",
                    "{nerf} {i:ability_dualwield} Bug corrigé : **Dual Wield Specialization** donnait son bonus de toucher aux deux armes. Elle [nerf]n'en donne plus du tout à la main gauche[/nerf].",
                    "{nerf} {i:spell_nature_stoneclawtotem} **Unbridled Wrath** ne donne plus deux fois plus de rage avec une arme à deux mains, et {i:spell_shadow_summonimp} **Blood Craze** ne se déclenche plus sur Bloodthirst.",
                    "{eq} Talents supprimés : Improved Cleave et Boundless Rage (Fureur), Toughness (Protection). Nouveaux talents : **Lingering Rage** (rang 2) et **Gore Drinker** (rang 6).",
                    "{eq} {i:ability_ghoulfrenzy} **Flurry** (Rafale) demande maintenant **Death Wish** (Souhait mortel) au lieu d'Enrage. **Berserker Rage** arrive au niveau 30 (au lieu de 32), Improved Berserker Rage passe au rang 5.",
                    "{eq} **Guerrier Protection** : Iron Will et Improved Bloodrage remontent au rang 1, Anticipation et Improved Revenge au rang 2, Improved Disarm au rang 3, Improved Shield Bash au rang 4.",
                ]),
                ("h2", "Combien de DPS en plus pour le Guerrier : la simulation"),
                ("p", "Même personnage **niveau 60**, même équipement, mêmes combats : 20 000 combats de 3 minutes contre un boss, avec les mêmes tirages aléatoires avant et après. Seuls les deux changements chiffrés sont appliqués."),
                ("bars", {"unit": "DPS", "before": "Avant", "after": "Après", "rows": [("Guerrier Fureur", 497.9, 517.4), ("Guerrier Armes", 490.3, 494.8)]}),
                ("table", {"head": ["Spécialisation", "DPS avant", "Bloodthirst à 45 %", "+ rage des critiques", "Écart"],
                           "rows": [["**Guerrier Fureur** (deux armes)", "497,9", "515,2 ([up]+3,5 %[/up])", "517,4", "[up]+3,9 %[/up]"],
                                    ["**Guerrier Armes** (arme à deux mains)", "490,3", "490,3 (inchangé)", "494,8", "[up]+0,9 %[/up]"]]}),
                ("h2", "Ce que ça change pour ton build Guerrier"),
                ("list", [
                    "**Le Guerrier Fureur est le grand gagnant** : Bloodthirst représente environ 13 % de ses dégâts dans notre simulation, donc 10 points de ratio en plus se voient tout de suite.",
                    "**Le Guerrier Armes gagne très peu** sur ces deux lignes : il n'utilise pas Bloodthirst, seule la rage des critiques l'aide un peu.",
                    "En Fureur, pense au nouveau talent **Furious Precision** : sans le bonus de toucher de Dual Wield Specialization, c'est lui qui fait toucher ta main gauche.",
                    "La réorganisation des talents (Flurry, Furious Precision, Whirlwind à deux armes) n'est [eq]pas encore dans le simulateur[/eq] : son effet n'est pas compté ici.",
                ]),
                ("note", "Méthode : simulateur DPS niveau 60 de BrokenMeta, personnage d'exemple Fureur (et la même base avec une épée à deux mains pour Armes), 20 000 combats par scénario. La bêta change souvent : ces chiffres valent pour le build du 2 octobre."),
            ],
            "faq": [
                ("Le Guerrier Fureur a-t-il été buff dans WoW Forever ?", "Oui. Le patch de la bêta du 2 octobre 2026 monte Bloodthirst de 35 à 45 % de puissance d'attaque et la rage des critiques de 75 à 100 %. Notre simulateur niveau 60 mesure +3,9 % de DPS en Fureur."),
                ("Le Guerrier Armes est-il touché par le patch du 2 octobre ?", "Peu : il ne gagne que +0,9 % de DPS dans notre simulation, grâce à la rage des coups critiques. Le buff de Bloodthirst ne le concerne pas."),
            ],
            "links": [
                ("Guide Guerrier Fureur", "wow-forever/guides/warrior/fury/"),
                ("Guide Guerrier Armes", "wow-forever/guides/warrior/arms/"),
                ("Calculateur de talents Guerrier", "wow-forever/talents/warrior/"),
            ],
        },
        "en": {
            "title": "Fury Warrior buff in WoW: Forever: +3.9% DPS, simulated",
            "description": "Bloodthirst goes from 35% to 45% attack power and crits give more rage. Simulated at level 60: +3.9% DPS for Fury, +0.9% for Arms.",
            "h1": "Fury Warrior: the October 2 buff in WoW Forever, simulated",
            "lede": "The October 2, 2026 **WoW Forever** beta patch is a **Fury Warrior buff**: more rage from critical strikes, a stronger **Bloodthirst** and a reorganized Fury talent tree. We ran the numeric changes through our level-60 DPS simulator: [up]+3.9% DPS for Fury[/up], [up]+0.9% for Arms[/up].",
            "body": [
                ("cards", [("spell_nature_bloodlust", "Bloodthirst", "35% → 45% attack power", "up"),
                           ("ability_whirlwind", "Whirlwind", "Always with both weapons", "up"),
                           ("ability_dualwield", "Dual Wield Specialization", "No more off-hand hit", "nerf"),
                           ("ability_ghoulfrenzy", "Flurry", "Requires Death Wish instead of Enrage", "eq")]),
                ("h2", "WoW Forever Warrior patch: every change"),
                ("list", [
                    "{up} **Critical strike rage**: a crit now generates [up]100% more rage[/up] instead of 75%.",
                    "{up} {i:spell_nature_bloodlust} **Bloodthirst**: its attack power ratio goes from 35% to [up]45%[/up].",
                    "{up} {i:ability_whirlwind} **Whirlwind** now always strikes with both weapons, no talent needed. **Raging Blows** reduces the rage cost of Cleave and Whirlwind by 3.",
                    "{up} New talent **Furious Precision** (Fury row 3): [up]+4/7/10% chance to hit[/up] with off-hand attacks.",
                    "{nerf} {i:ability_dualwield} Bug fix: **Dual Wield Specialization** gave its hit bonus to both weapons. It [nerf]no longer gives any hit to the off-hand[/nerf].",
                    "{nerf} {i:spell_nature_stoneclawtotem} **Unbridled Wrath** no longer gives twice as much rage with a two-handed weapon, and {i:spell_shadow_summonimp} **Blood Craze** no longer triggers from Bloodthirst.",
                    "{eq} Removed talents: Improved Cleave and Boundless Rage (Fury), Toughness (Protection). New talents: **Lingering Rage** (row 2) and **Gore Drinker** (row 6).",
                    "{eq} {i:ability_ghoulfrenzy} **Flurry** now requires **Death Wish** instead of Enrage. **Berserker Rage** is available at level 30 (was 32), Improved Berserker Rage moves to row 5.",
                    "{eq} **Protection Warrior**: Iron Will and Improved Bloodrage move up to row 1, Anticipation and Improved Revenge to row 2, Improved Disarm to row 3, Improved Shield Bash to row 4.",
                ]),
                ("h2", "How much DPS the Warrior gains: the simulation"),
                ("p", "Same **level-60** character, same gear, same fights: 20,000 three-minute boss fights with identical random rolls before and after. Only the two numeric changes are applied."),
                ("bars", {"unit": "DPS", "before": "Before", "after": "After", "rows": [("Fury Warrior", 497.9, 517.4), ("Arms Warrior", 490.3, 494.8)]}),
                ("table", {"head": ["Spec", "DPS before", "Bloodthirst at 45%", "+ crit rage", "Change"],
                           "rows": [["**Fury Warrior** (dual wield)", "497.9", "515.2 ([up]+3.5%[/up])", "517.4", "[up]+3.9%[/up]"],
                                    ["**Arms Warrior** (two-hander)", "490.3", "490.3 (unchanged)", "494.8", "[up]+0.9%[/up]"]]}),
                ("h2", "What it means for your Warrior build"),
                ("list", [
                    "**Fury Warrior is the big winner**: Bloodthirst is about 13% of its damage in our simulation, so 10 more ratio points show right away.",
                    "**Arms Warrior gains very little** from these two lines: it does not use Bloodthirst, only the crit rage helps a little.",
                    "As Fury, look at the new **Furious Precision** talent: without Dual Wield Specialization's hit bonus, it is what makes your off-hand connect.",
                    "The talent reorganization (Flurry, Furious Precision, dual-weapon Whirlwind) is [eq]not in the simulator yet[/eq]: its effect is not counted here.",
                ]),
                ("note", "Method: BrokenMeta level-60 DPS simulator, sample Fury character (and the same base with a two-handed sword for Arms), 20,000 fights per scenario. The beta changes often: these numbers are for the October 2 build."),
            ],
            "faq": [
                ("Was Fury Warrior buffed in WoW Forever?", "Yes. The October 2, 2026 beta patch raises Bloodthirst from 35% to 45% attack power and crit rage from 75% to 100%. Our level-60 simulator measures +3.9% DPS for Fury."),
                ("Is Arms Warrior affected by the October 2 patch?", "Barely: it only gains +0.9% DPS in our simulation, from the crit rage. The Bloodthirst buff does not apply to it."),
            ],
            "links": [
                ("Fury Warrior guide", "wow-forever/guides/warrior/fury/"),
                ("Arms Warrior guide", "wow-forever/guides/warrior/arms/"),
                ("Warrior talent calculator", "wow-forever/talents/warrior/"),
            ],
        },
    },
    {
        "slug": "colliers-des-livres-nerf-alternatives",
        "date": "2026-10-04",
        "updated": "2026-10-04",
        "draft": False,
        "tag": "tuning",
        "kind": "nerf",
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_jewelry_necklace_11.jpg",
        "sources": [
            ("Wowhead : Necklace Rewards from Collecting Books Nerfed to Uncommon Quality (3 Oct. 2026)",
             "https://www.wowhead.com/forever/news/necklace-rewards-from-collecting-books-nerfed-to-uncommon-quality-in-wow-forever-383231"),
            ("Wowhead : Erudite's Amulet", "https://www.wowhead.com/forever/item=277204/erudites-amulet"),
            ("Wowhead : Scholarly Pendant", "https://www.wowhead.com/forever/item=277203/scholarly-pendant"),
        ],
        "fr": {
            "title": "Colliers des livres nerfés : quel collier au niveau 30",
            "description": "Erudite's Amulet et Scholarly Pendant passent en qualité inhabituelle. Les colliers de donjon qui les remplacent, spécialisation par spécialisation.",
            "h1": "Nerf des colliers des livres dans WoW Forever : le meilleur collier au niveau 30",
            "lede": "**Nerf** dans la bêta de **WoW Forever** : les deux colliers de la quête **Friend of the Library**, obtenue en rapportant 10 livres au bibliothécaire de sa faction, passent [nerf]de qualité rare à inhabituelle[/nerf]. Nous avons cherché le **meilleur collier** pour chaque spécialisation vers le **niveau 30**, avec les poids de stats de notre simulateur DPS.",
            "body": [
                ("cards", [("inv_jewelry_necklace_01", "Erudite's Amulet", "Rare → inhabituel", "nerf"),
                           ("inv_jewelry_necklace_11", "Scholarly Pendant", "Rare → inhabituel", "nerf"),
                           ("inv_jewelry_necklace_06", "Ghostshard Talisman", "Meilleur collier physique au niveau 30", "up"),
                           ("inv_jewelry_necklace_03", "Scorn's Icy Choker", "Meilleur collier de lanceur de sorts", "up")]),
                ("h2", "Ce qui change sur les colliers des livres"),
                ("list", [
                    "{nerf} {i:inv_jewelry_necklace_01} **Erudite's Amulet** : maintenant [nerf]+2 Agilité et +3 Endurance[/nerf] (niveau d'objet 23).",
                    "{nerf} {i:inv_jewelry_necklace_11} **Scholarly Pendant** : maintenant [nerf]+3 Endurance et +2 Esprit[/nerf] (niveau d'objet 23).",
                    "{eq} La récompense des **20 livres** perd 5 niveaux d'objet (40 vers 35) mais [up]n'est plus réservée à une classe[/up].",
                ]),
                ("h2", "Ce que valent ces colliers après le nerf"),
                ("p", "Pour une spécialisation DPS, [nerf]presque rien[/nerf] : 2 points d'Agilité pèsent très peu face à de la puissance d'attaque ou de sorts, et l'Esprit ne compte pas dans nos simulations de dégâts. Ils restent un **bon collier d'attente** : avant le niveau 28, nos données de donjon n'ont aucun collier meilleur."),
                ("h2", "Le meilleur collier de donjon vers le niveau 30, par spécialisation"),
                ("table", {"head": ["Spécialisations", "Meilleur collier", "Stats", "Où le trouver"],
                           "rows": [["Guerrier, Voleur, Chasseur, Paladin Vindicte, Druide Farouche", "{i:inv_jewelry_necklace_06} **Ghostshard Talisman**", "[up]+14 puissance d'attaque[/up], +9 Endurance (niveau 30 requis)", "Monastère écarlate, Azshir the Sleepless"],
                                    ["Mage, Prêtre Ombre, Démoniste, Chaman Élémentaire, Druide Équilibre", "{i:inv_jewelry_necklace_03} **Scorn's Icy Choker**", "[up]+6 Intelligence, +7 puissance des sorts[/up], +5 Endurance (niveau 30 requis)", "Monastère écarlate, Scorn"],
                                    ["Chaman Amélioration", "**Scorn's Icy Choker**, de peu devant Ghostshard Talisman", "", "Monastère écarlate"]]}),
                ("p", "Le **Chaman Amélioration** est le seul cas serré : ses sorts profitent de la puissance des sorts, si bien que les deux colliers se valent presque dans notre simulation."),
                ("note", "Méthode : chaque collier est classé avec les poids de stats que notre simulateur calcule pour chaque spécialisation DPS (puissance d'attaque, puissance des sorts, toucher, critique). L'Endurance et l'Esprit ne sont pas comptés, et les poids sont calculés sur un personnage de niveau 30. Les tanks et les soigneurs ne sont pas couverts."),
            ],
            "faq": [
                ("Les colliers de la quête des livres ont-ils été nerfés dans WoW Forever ?", "Oui. Erudite's Amulet et Scholarly Pendant, récompenses de Friend of the Library, sont passés de qualité rare à inhabituelle : +2 Agilité et +3 Endurance pour l'un, +3 Endurance et +2 Esprit pour l'autre."),
                ("Quel est le meilleur collier au niveau 30 dans WoW Forever ?", "Dans nos données de donjon : Ghostshard Talisman pour les classes physiques et Scorn's Icy Choker pour les lanceurs de sorts, tous deux au Monastère écarlate."),
            ],
            "links": [
                ("Butin du Monastère écarlate", "wow-forever/dungeons/scarlet-monastery/"),
                ("Tous les objets des donjons", "wow-forever/dungeons/tous-les-objets/"),
            ],
        },
        "en": {
            "title": "Book necklaces nerfed: which necklace to wear at level 30",
            "description": "Erudite's Amulet and Scholarly Pendant drop to uncommon quality. The dungeon necklaces that replace them, spec by spec.",
            "h1": "WoW Forever book necklace nerf: the best necklace at level 30",
            "lede": "A **nerf** in the **WoW Forever** beta: the two necklaces from the **Friend of the Library** quest, earned by handing 10 books to your faction's librarian, go [nerf]from rare to uncommon quality[/nerf]. We looked for the **best necklace** for every spec around **level 30**, using our DPS simulator's stat weights.",
            "body": [
                ("cards", [("inv_jewelry_necklace_01", "Erudite's Amulet", "Rare → uncommon", "nerf"),
                           ("inv_jewelry_necklace_11", "Scholarly Pendant", "Rare → uncommon", "nerf"),
                           ("inv_jewelry_necklace_06", "Ghostshard Talisman", "Best physical necklace at level 30", "up"),
                           ("inv_jewelry_necklace_03", "Scorn's Icy Choker", "Best caster necklace", "up")]),
                ("h2", "What changes on the book necklaces"),
                ("list", [
                    "{nerf} {i:inv_jewelry_necklace_01} **Erudite's Amulet**: now [nerf]+2 Agility and +3 Stamina[/nerf] (item level 23).",
                    "{nerf} {i:inv_jewelry_necklace_11} **Scholarly Pendant**: now [nerf]+3 Stamina and +2 Spirit[/nerf] (item level 23).",
                    "{eq} The **20-book** reward loses 5 item levels (40 to 35) but [up]is no longer class-restricted[/up].",
                ]),
                ("h2", "What the necklaces are worth after the nerf"),
                ("p", "For a DPS spec, [nerf]almost nothing[/nerf]: 2 Agility weighs very little next to attack or spell power, and Spirit does not count in our damage simulations. They are still a **fine placeholder**: before level 28, our dungeon data has no better necklace."),
                ("h2", "Best dungeon necklace around level 30, by spec"),
                ("table", {"head": ["Specs", "Best necklace", "Stats", "Where to get it"],
                           "rows": [["Warrior, Rogue, Hunter, Retribution Paladin, Feral Druid", "{i:inv_jewelry_necklace_06} **Ghostshard Talisman**", "[up]+14 attack power[/up], +9 Stamina (requires level 30)", "Scarlet Monastery, Azshir the Sleepless"],
                                    ["Mage, Shadow Priest, Warlock, Elemental Shaman, Balance Druid", "{i:inv_jewelry_necklace_03} **Scorn's Icy Choker**", "[up]+6 Intellect, +7 spell power[/up], +5 Stamina (requires level 30)", "Scarlet Monastery, Scorn"],
                                    ["Enhancement Shaman", "**Scorn's Icy Choker**, just ahead of Ghostshard Talisman", "", "Scarlet Monastery"]]}),
                ("p", "**Enhancement Shaman** is the only close call: its spells use spell power, so both necklaces come out almost even in our simulation."),
                ("note", "Method: each necklace is ranked with the stat weights our simulator computes for every DPS spec (attack power, spell power, hit, crit). Stamina and Spirit are not counted, and the weights are computed on a level-30 character. Tanks and healers are not covered."),
            ],
            "faq": [
                ("Were the book quest necklaces nerfed in WoW Forever?", "Yes. Erudite's Amulet and Scholarly Pendant, rewards of Friend of the Library, went from rare to uncommon quality: +2 Agility and +3 Stamina for one, +3 Stamina and +2 Spirit for the other."),
                ("What is the best necklace at level 30 in WoW Forever?", "In our dungeon data: Ghostshard Talisman for physical classes and Scorn's Icy Choker for casters, both in Scarlet Monastery."),
            ],
            "links": [
                ("Scarlet Monastery loot", "wow-forever/dungeons/scarlet-monastery/"),
                ("All dungeon items", "wow-forever/dungeons/tous-les-objets/"),
            ],
        },
    },
    {
        "slug": "metiers-equipement-bonus-wow-forever",
        "format": "brief",
        "date": "2026-10-05",
        "updated": "2026-10-05",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/trade_blacksmithing.jpg",
        "sources": [
            ("Wowhead : Professions get Fun Thematic Gear Bonuses in WoW: Forever (4 Oct. 2026)",
             "https://www.wowhead.com/news=383236/professions-get-fun-thematic-gear-bonuses-in-wow-forever"),
        ],
        "fr": {
            "title": "WoW Forever : de l'équipement qui aide vos métiers",
            "description": "WoW Forever ajoute des pièces d'équipement thématiques pour les métiers : vitesse de cuisine, marteau de forgeron lancé. Ce qu'on sait.",
            "h1": "WoW Forever : du matériel de métier qui sert aussi au combat",
            "lede": "La bêta de **WoW Forever** introduit des objets d'équipement liés aux métiers. Dans les Mines de la Mort, on trouve des pièces comme les **Smelting Pants** (utiles aux mineurs de bas niveau) et, depuis la dernière build, la **Cookie's Stirring Rod**, une baguette qui accélère la cuisine. L'**Arcanite Blacksmith Hammer** est une arme de jet qui peut étourdir la cible et remplace aussi le marteau de forgeron qu'on garde en sac. Ce sont des bonus de progression « horizontale » : ils ne rendent pas forcément plus fort.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Cuisine** : la Cookie's Stirring Rod se farme dans les Mines de la Mort et sert à tous les utilisateurs de baguette.",
                    "**Forge** : l'Arcanite Blacksmith Hammer libère un emplacement de sac, en plus de son effet d'étourdissement.",
                    "**Mineurs** : les Smelting Pants aident surtout pendant les premiers niveaux.",
                    "Ces objets sont des **bonus de confort**, pas des gains de puissance : à farmer par intérêt pour le métier.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Mines de la Mort : butin", "wow-forever/dungeons/deadmines/"),
                ("Guide Cuisine", "wow-forever/professions/cooking/"),
                ("Guide Forge", "wow-forever/professions/blacksmithing/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Gear That Boosts Your Professions",
            "description": "WoW Forever adds profession-themed gear: faster cooking, a throwable Blacksmith Hammer. What we know so far from the beta.",
            "h1": "WoW Forever: profession gear that also works in combat",
            "lede": "The **WoW Forever** beta introduces gear tied to professions. The Deadmines drops pieces such as the **Smelting Pants** (handy for low-level miners) and, since the latest build, **Cookie's Stirring Rod**, a wand that speeds up cooking. The **Arcanite Blacksmith Hammer** is a throwing weapon that can stun its target and also counts as the blacksmith hammer you would otherwise carry in your bags. These are \"horizontal progression\" rewards: they do not necessarily make you stronger.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Cooking**: Cookie's Stirring Rod drops in the Deadmines and works for any wand user.",
                    "**Blacksmithing**: the Arcanite Blacksmith Hammer frees a bag slot, on top of its stun chance.",
                    "**Miners**: the Smelting Pants mostly help during the first levels.",
                    "These are **quality-of-life bonuses**, not power upgrades: farm them if you care about the profession.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Deadmines loot", "wow-forever/dungeons/deadmines/"),
                ("Cooking guide", "wow-forever/professions/cooking/"),
                ("Blacksmithing guide", "wow-forever/professions/blacksmithing/"),
            ],
        },
    },
    {
        "slug": "student-fodder-xp-repose-wow-forever",
        "format": "brief",
        "date": "2026-10-05",
        "updated": "2026-10-05",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_food_15.jpg",
        "sources": [
            ("Wowhead : Student Fodder Doesn't Give Rested Experience in WoW: Forever (4 Oct. 2026)",
             "https://www.wowhead.com/news=383243/student-fodder-doesnt-give-rested-experience-in-wow-forever"),
        ],
        "fr": {
            "title": "WoW Forever : Student Fodder sans XP de repos",
            "description": "Dans la bêta de WoW Forever, Student Fodder ne donne plus d'expérience de repos. Les autres moyens d'xp plus vite pendant le leveling.",
            "h1": "WoW Forever : Student Fodder n'accorde plus d'expérience de repos",
            "lede": "La quête du sac de couchage, venue de Season of Discovery, revient dans **WoW Forever**. Sa récompense **Student Fodder** donnait quatre barres d'expérience de repos ; dans la bêta, cet effet est supprimé. Il rend toujours instantanément une partie de la ressource de ta classe, et applique **Trail Snack** : +60 % de vitesse pendant 0,75 seconde et des soins sur la durée (175 par tick).",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "Ne compte plus sur Student Fodder pour **monter plus vite** : il sert désormais de soin et de ressource.",
                    "Le **feu de camp** donne une barre d'expérience de repos, utilisable une fois par heure.",
                    "Presque toutes les **nouvelles nourritures** donnent +5 % d'expérience, et le **Cozy Sleeping Bag** jusqu'à +3 % pendant une heure.",
                    "Les **talents d'héritage** faciliteront aussi le leveling des personnages suivants.",
                ]),
            ],
            "faq": [],
            "links": [
                ("FAQ WoW Forever", "wow-forever/faq/"),
                ("Cuisine : nourritures", "wow-forever/professions/cooking/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Student Fodder Loses Rested XP",
            "description": "In the WoW Forever beta, Student Fodder no longer grants rested experience. The other ways to level faster are still there.",
            "h1": "WoW Forever: Student Fodder no longer gives rested experience",
            "lede": "The Sleeping Bag quest chain from Season of Discovery returns in **WoW Forever**. Its reward **Student Fodder** used to give four bars of rested experience; in the beta that effect is gone. It still restores part of your class resource instantly and now applies **Trail Snack**: a 60% speed boost for 0.75 seconds plus healing over time (175 per tick).",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "Do not count on Student Fodder to **level faster**: it is now a heal and resource item.",
                    "Resting at a **campfire** grants one bar of rested experience, once per hour.",
                    "Almost all **new food buffs** give +5% experience, and the **Cozy Sleeping Bag** up to +3% for an hour.",
                    "**Legacy talents** will also make levelling easier on later characters.",
                ]),
            ],
            "faq": [],
            "links": [
                ("WoW Forever FAQ", "wow-forever/faq/"),
                ("Cooking: food buffs", "wow-forever/professions/cooking/"),
            ],
        },
    },
    {
        "slug": "gnome-eureka-nerf-wow-forever",
        "date": "2026-10-05",
        "updated": "2026-10-05",
        "draft": False,
        "tag": "tuning",
        "kind": "nerf",
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/race_gnome_male.jpg",
        "sources": [
            ("Wowhead : Gnome Racial Nerfed Again In Latest WoW: Forever Build (2 Oct. 2026)",
             "https://www.wowhead.com/news=383222/gnome-racial-nerfed-again-in-latest-wow-forever-build"),
        ],
        "fr": {
            "title": "Nerf du Gnome dans WoW Forever : Eureka! sans les DoT",
            "description": "Eureka!, le racial du Gnome de WoW Forever, ne profite plus du tout aux effets périodiques. Rupture, Garrot et Pourfendre perdent leur bonus.",
            "h1": "Gnome dans WoW Forever : Eureka! nerfé une deuxième fois",
            "lede": "Deuxième **nerf** pour le racial du **Gnome** dans la bêta de **WoW Forever** : dans le build du 2 octobre 2026, **Eureka!** ne fonctionne [nerf]plus du tout sur les effets périodiques[/nerf]. Les sorts canalisés ne comptent pas comme périodiques. Le premier nerf avait déjà réduit, d'un pourcentage fixe, la réduction de coût de ressource.",
            "body": [
                ("cards", [("race_gnome_male", "Eureka! (Gnome)", "Plus d'effet sur les DoT", "nerf"),
                           ("ability_rogue_rupture", "Rupture (Rogue)", "Perd le bonus de 10 %", "nerf"),
                           ("ability_rogue_garrote", "Garrot (Rogue)", "Perd le bonus de 10 %", "nerf"),
                           ("ability_gouge", "Rend (Warrior)", "Perd le bonus de 10 %", "nerf")]),
                ("h2", "Eureka! du Gnome : ce qui change dans WoW Forever"),
                ("list", [
                    "{nerf} **Eureka!** ne profite plus aux dégâts périodiques : l'effet qui augmentait de 10 % les dégâts périodiques est [nerf]supprimé[/nerf].",
                    "{nerf} {i:ability_rogue_rupture} **Rupture** et {i:ability_rogue_garrote} **Garrote** (Garrot) du Voleur perdent ce bonus de dégâts.",
                    "{nerf} {i:ability_gouge} **Rend** (Pourfendre) du Guerrier perd lui aussi ce bonus.",
                    "{eq} Les trois prochaines attaques directes gardent le bonus : **-10 % de coût** (énergie, rage ou mana selon la classe) et **+10 % de dégâts**.",
                ]),
                ("h2", "Que vaut encore le Gnome après ce nerf"),
                ("list", [
                    "**Voleur et Guerrier** sont les plus touchés : leurs saignements (Rupture, Garrot, Pourfendre) étaient les sorts concernés par le bonus.",
                    "**Les classes à mana** perdent moins : le texte du racial reste le même pour leurs sorts directs.",
                    "Nous ne chiffrons pas ce nerf : le racial Eureka! [eq]n'est pas simulé[/eq] dans notre simulateur niveau 60, donc aucun pourcentage de DPS n'est donné ici.",
                ]),
                ("note", "Méthode : faits tirés des notes de build relayées par Wowhead, réécrits ; aucune simulation. La bêta change souvent : ces informations valent pour le build du 2 octobre 2026."),
            ],
            "faq": [
                ("Eureka! du Gnome a-t-il été nerfé dans WoW Forever ?", "Oui, deux fois. Après une première baisse de la réduction de coût, le build du 2 octobre 2026 retire tout effet d'Eureka! sur les dégâts périodiques. Les sorts canalisés ne comptent pas comme périodiques."),
                ("Le Gnome est-il encore un bon choix pour le Voleur ou le Guerrier ?", "Le racial perd son bonus sur Rupture, Garrot et Pourfendre. Nous ne l'avons pas simulé, donc nous ne donnons pas de chiffre : consulte nos guides de spécialisation."),
            ],
            "links": [
                ("Guide Voleur Assassinat", "wow-forever/guides/rogue/assassination/"),
                ("Guide Guerrier Armes", "wow-forever/guides/warrior/arms/"),
                ("Simulateur de DPS niveau 60", "wow-forever/simulateur-dps/"),
            ],
        },
        "en": {
            "title": "Gnome nerf in WoW Forever: Eureka! no longer hits DoTs",
            "description": "Eureka!, the Gnome racial in WoW Forever, no longer applies to periodic effects at all. Rupture, Garrote and Rend lose their bonus.",
            "h1": "Gnome in WoW Forever: Eureka! nerfed a second time",
            "lede": "Second **nerf** to the **Gnome** racial in the **WoW Forever** beta: in the October 2, 2026 build, **Eureka!** [nerf]no longer works at all on periodic effects[/nerf]. Channeled spells do not count as periodic. The first nerf had already cut the resource discount by a flat percentage.",
            "body": [
                ("cards", [("race_gnome_male", "Eureka! (Gnome)", "No more effect on DoTs", "nerf"),
                           ("ability_rogue_rupture", "Rupture (Rogue)", "Loses the 10% bonus", "nerf"),
                           ("ability_rogue_garrote", "Garrote (Rogue)", "Loses the 10% bonus", "nerf"),
                           ("ability_gouge", "Rend (Warrior)", "Loses the 10% bonus", "nerf")]),
                ("h2", "Gnome Eureka! in WoW Forever: what changed"),
                ("list", [
                    "{nerf} **Eureka!** no longer benefits periodic damage: the effect that raised periodic damage by 10% is [nerf]removed[/nerf].",
                    "{nerf} {i:ability_rogue_rupture} **Rupture** and {i:ability_rogue_garrote} **Garrote** for Rogues lose this damage bonus.",
                    "{nerf} {i:ability_gouge} Warrior **Rend** loses it as well.",
                    "{eq} Your next three direct attacks keep the bonus: **10% lower cost** (energy, rage or mana depending on the class) and **10% more damage**.",
                ]),
                ("h2", "How good is the Gnome after this nerf"),
                ("list", [
                    "**Rogue and Warrior** are hit hardest: their bleeds (Rupture, Garrote, Rend) were the spells the bonus applied to.",
                    "**Mana classes** lose less: the racial text is unchanged for their direct spells.",
                    "We do not put a number on this nerf: Eureka! is [eq]not simulated[/eq] in our level-60 simulator, so no DPS percentage is given here.",
                ]),
                ("note", "Method: facts taken from the build notes relayed by Wowhead, rewritten; no simulation. The beta changes often: this is valid for the October 2, 2026 build."),
            ],
            "faq": [
                ("Was the Gnome racial Eureka! nerfed in WoW Forever?", "Yes, twice. After a first cut to the cost discount, the October 2, 2026 build removes all Eureka! effect on periodic damage. Channeled spells do not count as periodic."),
                ("Is Gnome still a good pick for Rogue or Warrior?", "The racial loses its bonus on Rupture, Garrote and Rend. We have not simulated it, so we give no figure: see our spec guides."),
            ],
            "links": [
                ("Assassination Rogue guide", "wow-forever/guides/rogue/assassination/"),
                ("Arms Warrior guide", "wow-forever/guides/warrior/arms/"),
                ("Level-60 DPS simulator", "wow-forever/simulateur-dps/"),
            ],
        },
    },
    {
        "slug": "verigans-fist-buff-paladin-wow-forever",
        "date": "2026-10-05",
        "updated": "2026-10-05",
        "draft": False,
        "tag": "tuning",
        "kind": "up",
        "class": "paladin",
        "image": "https://wow.zamimg.com/images/wow/icons/large/spell_holy_innerfire.jpg",
        "sources": [
            ("Wowhead : New Proc for Verigan's Fist in WoW: Forever (1 Oct. 2026)",
             "https://www.wowhead.com/news=383221/new-proc-for-verigans-fist-in-wow-forever-alliance-paladin-weapon"),
        ],
        "fr": {
            "title": "Verigan's Fist buff dans WoW Forever : nouveau proc",
            "description": "L'arme de niveau 20 du Paladin Alliance gagne le proc Holy Forgefire (39 à 59 dégâts de feu sacré), comme Wolfsbane côté Horde.",
            "h1": "Paladin : Verigan's Fist reçoit un nouveau proc dans WoW Forever",
            "lede": "**Buff** dans le dernier build de **WoW Forever** : **Verigan's Fist**, l'arme de niveau 20 du **Paladin** Alliance (quête Test of Righteousness), gagne un effet de proc, **Holy Forgefire**. Jusque-là, la version Horde, **Wolfsbane**, obtenue par la quête Old Fire-Eye pour les Paladins réprouvés, avait un proc que l'arme Alliance n'avait pas.",
            "body": [
                ("cards", [("spell_holy_innerfire", "Holy Forgefire", "Nouveau proc de Verigan's Fist", "up"),
                           ("spell_fire_fire", "39 à 59 dégâts", "Dégâts de feu sacré", "up"),
                           ("spell_fire_selfdestruct", "x3 sur les élémentaires", "Feu et Terre", "up")]),
                ("h2", "Verigan's Fist : le nouveau proc"),
                ("list", [
                    "{up} {i:spell_holy_innerfire} **Holy Forgefire** : embrase la cible avec les flammes de la Grande Forge pour [up]39 à 59 dégâts de feu sacré[/up].",
                    "{up} Les dégâts sont [up]triplés contre les élémentaires de feu et de terre[/up].",
                    "{eq} Contexte : l'arme Horde, **Wolfsbane**, avait déjà un proc de dégâts fixes, contre les Worgen. Des joueurs Alliance avaient réclamé un rééquilibrage entre factions.",
                ]),
                ("h2", "Ce que ça change pour ton Paladin"),
                ("list", [
                    "Le proc fait des dégâts fixes, donc il pèse peu sur le DPS total d'un Paladin : il corrige surtout un écart entre factions.",
                    "Il est [eq]non simulé[/eq] dans notre simulateur niveau 60 : nous ne donnons pas de pourcentage de DPS.",
                    "Pour comparer avec les autres armes disponibles, consulte les guides Paladin.",
                ]),
                ("note", "Méthode : faits tirés de l'article Wowhead, réécrits ; aucune simulation. Le taux de déclenchement du proc n'est pas précisé dans la source."),
            ],
            "faq": [
                ("Verigan's Fist a-t-il été amélioré dans WoW Forever ?", "Oui. Le dernier build de la bêta lui ajoute le proc Holy Forgefire : 39 à 59 dégâts de feu sacré, triplés contre les élémentaires de feu et de terre."),
                ("Quelle est l'arme équivalente côté Horde ?", "Wolfsbane, obtenue avec la quête Old Fire-Eye par les Paladins réprouvés. Elle a un proc de dégâts fixes contre les Worgen."),
            ],
            "links": [
                ("Guide Paladin Vindicte", "wow-forever/guides/paladin/retribution/"),
                ("Guide Paladin Protection", "wow-forever/guides/paladin/protection/"),
                ("Calculateur de talents Paladin", "wow-forever/talents/paladin/"),
            ],
        },
        "en": {
            "title": "Verigan's Fist buff in WoW Forever: new proc",
            "description": "The level-20 Alliance Paladin weapon gains the Holy Forgefire proc (39 to 59 holyfire damage), like Wolfsbane on the Horde side.",
            "h1": "Paladin: Verigan's Fist gets a new proc in WoW Forever",
            "lede": "**Buff** in the latest **WoW Forever** build: **Verigan's Fist**, the level-20 **Paladin** weapon for the Alliance (Test of Righteousness quest), gains a proc effect, **Holy Forgefire**. Until now the Horde version, **Wolfsbane**, from the Old Fire-Eye quest for Forsaken Paladins, had a proc the Alliance weapon lacked.",
            "body": [
                ("cards", [("spell_holy_innerfire", "Holy Forgefire", "New Verigan's Fist proc", "up"),
                           ("spell_fire_fire", "39 to 59 damage", "Holyfire damage", "up"),
                           ("spell_fire_selfdestruct", "x3 on elementals", "Fire and Earth", "up")]),
                ("h2", "Verigan's Fist: the new proc"),
                ("list", [
                    "{up} {i:spell_holy_innerfire} **Holy Forgefire**: ignites the target in the flames of the Great Forge for [up]39 to 59 holyfire damage[/up].",
                    "{up} Damage is [up]tripled against Fire and Earth Elementals[/up].",
                    "{eq} Background: the Horde weapon, **Wolfsbane**, already had a flat-damage proc, against Worgen. Alliance players had asked for faction balance.",
                ]),
                ("h2", "What it means for your Paladin"),
                ("list", [
                    "The proc deals flat damage, so it weighs little in a Paladin's total DPS: it mostly closes a gap between factions.",
                    "It is [eq]not simulated[/eq] in our level-60 simulator: we give no DPS percentage.",
                    "To compare with the other available weapons, see the Paladin guides.",
                ]),
                ("note", "Method: facts taken from the Wowhead article, rewritten; no simulation. The source does not state the proc rate."),
            ],
            "faq": [
                ("Was Verigan's Fist improved in WoW Forever?", "Yes. The latest beta build adds the Holy Forgefire proc: 39 to 59 holyfire damage, tripled against Fire and Earth Elementals."),
                ("What is the Horde equivalent weapon?", "Wolfsbane, from the Old Fire-Eye quest for Forsaken Paladins. It has a flat-damage proc against Worgen."),
            ],
            "links": [
                ("Retribution Paladin guide", "wow-forever/guides/paladin/retribution/"),
                ("Protection Paladin guide", "wow-forever/guides/paladin/protection/"),
                ("Paladin talent calculator", "wow-forever/talents/paladin/"),
            ],
        },
    },
    {
        "slug": "livres-bibliotheque-arc-niveau-30-wow-forever",
        "format": "brief",
        "date": "2026-10-06",
        "updated": "2026-10-06",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": "hunter",
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_weapon_bow_08.jpg",
        "sources": [
            ("Wowhead : New Library Book Return Quest Unlocked at Level 30 in WoW: Forever (6 Oct. 2026)",
             "https://www.wowhead.com/news=383251/new-reward-for-handing-in-library-books-at-level-30"),
        ],
        "fr": {
            "title": "WoW Forever : quête des 25 livres, un arc au niveau 30",
            "description": "WoW Forever : au niveau 30, rapportez 25 livres de bibliothèque pour choisir entre l'arc Truthseeker's Bow et deux autres récompenses.",
            "h1": "WoW Forever : la quête des 25 livres débloquée au niveau 30",
            "lede": "Dans la bêta de **WoW Forever**, les joueurs de **niveau 30** peuvent désormais rapporter **25 livres de bibliothèque** pour une récompense plus grosse. Il s'agit d'une seconde « Greater Friend of the Library » : on y choisit entre l'arc **Truthseeker's Bow**, le **Crest of Elucidation** et la **Researcher's Night Light**. Les deux dernières récompenses demandent le niveau 40, et l'arc pourrait lui aussi être verrouillé plus tard.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**25 livres** au niveau 30 : un choix unique entre le **Truthseeker's Bow**, le **Crest of Elucidation** et la **Researcher's Night Light**.",
                    "**Chasseurs** : l'arc vaut le détour, mais il se pourrait qu'il reçoive aussi une restriction de niveau 40.",
                    "Les paliers précédents restent : **10 livres** (collier) et **20 livres** (anneau).",
                    "Les livres se rendent au bibliothécaire de ta faction : **Garion Wendell** à Hurlevent (Alliance), **Owen Thadd** à Fossoyeuse (Horde).",
                ]),
            ],
            "faq": [],
            "links": [
                ("Guide Chasseur Précision", "wow-forever/guides/hunter/marksmanship/"),
                ("Calculateur de talents Chasseur", "wow-forever/talents/hunter/"),
            ],
        },
        "en": {
            "title": "WoW Forever: 25-Book Quest Unlocks a Bow at Level 30",
            "description": "WoW Forever: at level 30, hand in 25 library books to pick Truthseeker's Bow or two other rewards. What we know from the beta.",
            "h1": "WoW Forever: the 25-book library quest opens at level 30",
            "lede": "In the **WoW Forever** beta, **level 30** players can now hand in **25 library books** for a bigger reward. It is a second \"Greater Friend of the Library\" quest: you pick between the **Truthseeker's Bow**, the **Crest of Elucidation** and the **Researcher's Night Light**. The last two require level 40, so the bow may also get a level lock later.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**25 books** at level 30: a single choice between the **Truthseeker's Bow**, the **Crest of Elucidation** and the **Researcher's Night Light**.",
                    "**Hunters**: the bow is worth the trip, but it may end up with a level 40 requirement too.",
                    "The earlier tiers stay: **10 books** (necklace) and **20 books** (ring).",
                    "Hand books in to your faction's librarian: **Garion Wendell** in Stormwind (Alliance), **Owen Thadd** in Undercity (Horde).",
                ]),
            ],
            "faq": [],
            "links": [
                ("Marksmanship Hunter guide", "wow-forever/guides/hunter/marksmanship/"),
                ("Hunter talent calculator", "wow-forever/talents/hunter/"),
            ],
        },
    },
    {
        "slug": "lfg-style-de-jeu-obligatoire-wow-forever",
        "format": "brief",
        "date": "2026-10-07",
        "updated": "2026-10-07",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_groupneedmore.jpg",
        "sources": [
            ("Wowhead : New Required \"Playstyle\" Selection Added To LFG In WoW: Forever (7 Oct. 2026)",
             "https://www.wowhead.com/news=383259/new-required-playstyle-selection-added-to-lfg-in-wow-f"),
        ],
        "fr": {
            "title": "WoW Forever : un style de jeu obligatoire dans le LFG",
            "description": "WoW Forever bêta : le LFG demande de choisir Learning, Relaxed, Competitive ou Carry Offered avant de chercher un groupe de donjon.",
            "h1": "WoW Forever : le LFG impose maintenant un style de jeu",
            "lede": "Dans la bêta de **WoW Forever**, l'outil de recherche de groupe (**LFG**) affiche un nouveau menu « Playstyle » à remplir avant de pouvoir chercher un groupe de donjon. Quatre choix : **Learning**, **Relaxed**, **Competitive** et **Carry Offered**. Les deux premiers visent les runs tranquilles et les nouveaux joueurs ; « Competitive » n'a pas encore de vraie raison d'être en donjon, mais pourrait servir en raid.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Choix obligatoire** : impossible de lancer une recherche LFG sans sélectionner un style de jeu.",
                    "**Learning / Relaxed** : pour les groupes qui prennent leur temps, idéal pour découvrir un donjon.",
                    "**Carry Offered** : l'option la plus discutée, car un carry se fait souvent contre paiement ; les **GDKP** restent interdits dans WoW Forever.",
                    "Prépare ton groupe avant de chercher : consulte nos pages de **donjons** pour le loot et les boss.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Tous les donjons de WoW Forever", "wow-forever/dungeons/"),
                ("FAQ WoW Forever", "wow-forever/faq/"),
                ("Bêta de WoW Forever", "wow-forever/beta/"),
            ],
        },
        "en": {
            "title": "WoW Forever: A Required Playstyle Choice in LFG",
            "description": "WoW Forever beta: the LFG tool now asks you to pick Learning, Relaxed, Competitive or Carry Offered before queuing for a dungeon group.",
            "h1": "WoW Forever: LFG now requires a playstyle",
            "lede": "In the **WoW Forever** beta, the group finder (**LFG**) shows a new \"Playstyle\" menu that must be filled in before you can look for a dungeon group. There are four options: **Learning**, **Relaxed**, **Competitive** and **Carry Offered**. The first two target slower runs and newer players; \"Competitive\" has no real purpose in dungeons yet but could matter for raids.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Mandatory choice**: you cannot queue in LFG without picking a playstyle.",
                    "**Learning / Relaxed**: for groups that take their time, ideal to discover a dungeon.",
                    "**Carry Offered**: the most debated option, since carries often come at a price; **GDKPs** remain banned in WoW Forever.",
                    "Prepare your group before queuing: check our **dungeon** pages for loot and bosses.",
                ]),
            ],
            "faq": [],
            "links": [
                ("All WoW Forever dungeons", "wow-forever/dungeons/"),
                ("WoW Forever FAQ", "wow-forever/faq/"),
                ("WoW Forever beta", "wow-forever/beta/"),
            ],
        },
    },
    {
        "slug": "booty-bay-bruiser-buckshot-nerf-wow-forever",
        "format": "brief",
        "date": "2026-10-07",
        "updated": "2026-10-07",
        "draft": False,
        "tag": "tuning",
        "kind": "nerf",
        "class": "hunter",
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_weapon_rifle_05.jpg",
        "sources": [
            ("Wowhead : Booty Bay's Most Entertaining Weapon Just Got Nerfed - WoW Forever (6 Oct. 2026)",
             "https://www.wowhead.com/news=383276/booty-bays-most-entertaining-weapon-just-got-nerfed-wo"),
        ],
        "fr": {
            "title": "WoW Forever : Booty Bay Bruiser's Buckshot nerfé",
            "description": "WoW Forever bêta : le fusil Booty Bay Bruiser's Buckshot, vendu à Honoré chez Baie-du-Butin, perd son effet de projection par hotfix.",
            "h1": "WoW Forever : le Booty Bay Bruiser's Buckshot perd sa projection",
            "lede": "Cette semaine, les joueurs de la bêta de **WoW Forever** ont découvert le fusil **Booty Bay Bruiser's Buckshot**, disponible à **Honoré** auprès de la faction Baie-du-Butin. Son effet à l'utilisation projetait en arrière la cible touchée, joueur ou PNJ, ce qui a provoqué un joyeux chaos. Blizzard a depuis appliqué un **hotfix** qui supprime cette projection.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Plus de projection** : le fusil ne repousse plus la cible, l'effet d'origine est retiré.",
                    "L'arme reste accessible à **Honoré** avec la réputation de **Baie-du-Butin**.",
                    "**Chasseurs** : pense à vérifier les armes à distance de ton niveau dans nos guides.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Guide Chasseur Précision", "wow-forever/guides/hunter/marksmanship/"),
                ("Calculateur de talents Chasseur", "wow-forever/talents/hunter/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Booty Bay Bruiser's Buckshot Nerfed",
            "description": "WoW Forever beta: the Booty Bay Bruiser's Buckshot gun, sold at Honored with Booty Bay, loses its knockback effect in a hotfix.",
            "h1": "WoW Forever: Booty Bay Bruiser's Buckshot loses its knockback",
            "lede": "This week, **WoW Forever** beta players found the **Booty Bay Bruiser's Buckshot** gun, available at **Honored** with the Booty Bay faction. Its on-use effect knocked back whoever you shot, player or NPC, and chaos followed. Blizzard has since applied a **hotfix** that removes the knockback.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**No more knockback**: the gun no longer pushes its target, the original effect is gone.",
                    "The weapon is still available at **Honored** with **Booty Bay** reputation.",
                    "**Hunters**: check the ranged weapons for your level in our guides.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Marksmanship Hunter guide", "wow-forever/guides/hunter/marksmanship/"),
                ("Hunter talent calculator", "wow-forever/talents/hunter/"),
            ],
        },
    },
    {
        "slug": "druide-farouche-shifting-power-wow-forever",
        "date": "2026-10-07",
        "updated": "2026-10-07",
        "draft": False,
        "tag": "tuning",
        "kind": "eq",
        "class": "druid",
        "image": "https://wow.zamimg.com/images/wow/icons/large/spell_druid_displacement.jpg",
        "sources": [
            ("Wowhead : Powershifting is Out, Shifting Power is In: Feral Druid Changes Analysis (6 Oct. 2026)",
             "https://www.wowhead.com/news=383273/powershifting-is-out-shifting-power-is-in-feral-druid-changes-analysis-in-wow-forever"),
        ],
        "fr": {
            "title": "Druide Farouche WoW Forever : Shifting Power et powershift",
            "description": "Le build de la bêta WoW Forever ajoute Shifting Power au Druide Farouche : 40 énergie pour 55 % du mana de base, mais Tiger's Fury disparaît.",
            "h1": "Druide Farouche dans WoW Forever : Shifting Power, le nouveau powershifting",
            "lede": "Le dernier build de la bêta de **WoW Forever** change le **Druide Farouche** : deux nouveaux talents, **Shifting Power** et **Improved Shifting Power**, remplacent le « powershifting » de la version d'origine, tandis que **Tiger's Fury** et **King of the Jungle** disparaissent. Verdict mitigé : c'est un [up]buff pour le DPS en PvE[/up] et un [nerf]nerf pour le burst en PvP[/nerf], selon l'analyse de Wowhead.",
            "body": [
                ("cards", [("spell_druid_displacement", "Shifting Power", "40 énergie pour 55 % du mana de base", "up"),
                           ("ability_hunter_aspectmastery", "Improved Shifting Power", "Recharge de 16 s à 8 s (2 points)", "up"),
                           ("ability_mount_jungletiger", "Tiger's Fury", "Supprimé du Druide Farouche", "nerf"),
                           ("ability_druid_kingofthejungle", "King of the Jungle", "Supprimé : plus de 60 énergie", "nerf")]),
                ("h2", "Shifting Power du Druide Farouche : tous les changements"),
                ("list", [
                    "{up} {i:spell_druid_displacement} **Shifting Power** convertit instantanément [up]55 % du mana de base en 40 énergie[/up]. Son coût baisse avec les effets qui réduisent le coût des changements de forme.",
                    "{up} {i:ability_hunter_aspectmastery} **Improved Shifting Power** : la recharge de 16 secondes passe à [up]8 secondes avec 2 points[/up].",
                    "{up} Plus besoin de macro, et Shifting Power ne retire pas les ralentissements ni les immobilisations, contrairement au powershifting d'origine.",
                    "{nerf} {i:ability_mount_jungletiger} **Tiger's Fury** et {i:ability_druid_kingofthejungle} **King of the Jungle** (60 énergie) disparaissent : on perd aussi [nerf]+15 % de dégâts avec 20 % de présence[/nerf].",
                    "{nerf} {i:spell_holy_blessingofstamina} **Fureur** (Furor) : passer de la forme de chat à la forme d'ours et revenir vide toute l'énergie. Feral Charge pour interrompre ou Bash pour étourdir coûtent donc toute ton énergie, et il faut un Shifting Power (une global et du mana) pour la retrouver.",
                ]),
                ("h2", "Ce que ça change pour ton Druide Farouche"),
                ("list", [
                    "**PvE** : pour l'analyste de Wowhead, c'est positif : plus d'énergie compte plus que les 15 % de dégâts perdus.",
                    "**PvP** : le burst en forme de chat baisse nettement et la consommation de mana grimpe.",
                    "Le texte de Fureur laisse penser qu'on devrait garder son énergie en changeant de forme : Wowhead se demande si c'est un [eq]oubli[/eq] qui sera corrigé.",
                    "Nous ne chiffrons pas ce changement : le build Farouche [eq]n'est pas simulé[/eq] dans notre simulateur niveau 60, donc aucun pourcentage de DPS n'est donné.",
                ]),
                ("note", "Méthode : faits tirés de l'analyse Wowhead du 6 octobre 2026, réécrits ; aucune simulation. Les jugements PvE/PvP sont ceux de l'auteur de la source. La bêta change souvent."),
            ],
            "faq": [
                ("Qu'est-ce que Shifting Power pour le Druide Farouche dans WoW Forever ?", "Un talent qui convertit instantanément 55 % du mana de base en 40 énergie, avec 16 secondes de recharge (8 avec Improved Shifting Power). Il remplace le powershifting d'origine, sans macro."),
                ("Le Druide Farouche est-il buff ou nerf dans cette bêta ?", "Les deux : plus d'énergie utile en PvE, mais Tiger's Fury et King of the Jungle sont supprimés, ce qui réduit le burst en PvP. Nous ne l'avons pas simulé."),
            ],
            "links": [
                ("Guide Druide Farouche", "wow-forever/guides/druid/feral-combat/"),
                ("Calculateur de talents Druide", "wow-forever/talents/druid/"),
                ("Simulateur de DPS niveau 60", "wow-forever/simulateur-dps/"),
            ],
        },
        "en": {
            "title": "Feral Druid WoW Forever: Shifting Power replaces powershift",
            "description": "The WoW Forever beta adds Shifting Power for Feral Druids: 40 Energy for 55% of base mana, but Tiger's Fury is gone.",
            "h1": "Feral Druid in WoW Forever: Shifting Power, the new powershifting",
            "lede": "The latest **WoW Forever** beta build changes the **Feral Druid**: two new talents, **Shifting Power** and **Improved Shifting Power**, replace the original \"powershifting\", while **Tiger's Fury** and **King of the Jungle** are gone. A mixed verdict: a [up]buff for PvE DPS[/up] and a [nerf]nerf for PvP burst[/nerf], according to Wowhead's analysis.",
            "body": [
                ("cards", [("spell_druid_displacement", "Shifting Power", "40 Energy for 55% of base mana", "up"),
                           ("ability_hunter_aspectmastery", "Improved Shifting Power", "Cooldown 16s to 8s (2 points)", "up"),
                           ("ability_mount_jungletiger", "Tiger's Fury", "Removed for Feral Druid", "nerf"),
                           ("ability_druid_kingofthejungle", "King of the Jungle", "Removed: no more 60 Energy", "nerf")]),
                ("h2", "Feral Druid Shifting Power: every change"),
                ("list", [
                    "{up} {i:spell_druid_displacement} **Shifting Power** instantly converts [up]55% of base mana into 40 Energy[/up]. Its cost is reduced by effects that reduce shapeshift cost.",
                    "{up} {i:ability_hunter_aspectmastery} **Improved Shifting Power**: the 16-second cooldown drops to [up]8 seconds with 2 points[/up].",
                    "{up} No macro needed, and Shifting Power does not remove slows or snares, unlike original powershifting.",
                    "{nerf} {i:ability_mount_jungletiger} **Tiger's Fury** and {i:ability_druid_kingofthejungle} **King of the Jungle** (60 Energy) are gone: you also lose [nerf]+15% damage at 20% uptime[/nerf].",
                    "{nerf} {i:spell_holy_blessingofstamina} **Furor**: shifting from Cat to Bear and back empties all your Energy. Feral Charge to interrupt or Bash to stun now cost you all your Energy, and you need a Shifting Power (a global and mana) to get it back.",
                ]),
                ("h2", "What it means for your Feral Druid"),
                ("list", [
                    "**PvE**: Wowhead's analyst finds it positive: more Energy matters more than the 15% damage lost.",
                    "**PvP**: Cat Form burst drops noticeably and mana use goes up.",
                    "Furor's tooltip suggests you should keep your Energy when shifting: Wowhead wonders whether this is an [eq]oversight[/eq] that will be fixed.",
                    "We put no number on this change: the Feral build is [eq]not simulated[/eq] in our level-60 simulator, so no DPS percentage is given.",
                ]),
                ("note", "Method: facts taken from Wowhead's October 6, 2026 analysis, rewritten; no simulation. The PvE/PvP judgments are the source author's. The beta changes often."),
            ],
            "faq": [
                ("What is Shifting Power for Feral Druid in WoW Forever?", "A talent that instantly converts 55% of base mana into 40 Energy, with a 16-second cooldown (8 with Improved Shifting Power). It replaces original powershifting, with no macro."),
                ("Is Feral Druid buffed or nerfed in this beta?", "Both: more useful Energy in PvE, but Tiger's Fury and King of the Jungle are removed, which cuts PvP burst. We have not simulated it."),
            ],
            "links": [
                ("Feral Druid guide", "wow-forever/guides/druid/feral-combat/"),
                ("Druid talent calculator", "wow-forever/talents/druid/"),
                ("Level-60 DPS simulator", "wow-forever/simulateur-dps/"),
            ],
        },
    },
    {
        "slug": "progression-pvp-honneur-rangs-wow-forever",
        "format": "brief",
        "date": "2026-10-08",
        "updated": "2026-10-08",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_tabardpvp_02.jpg",
        "sources": [
            ("Wowhead : How PvP Progression Works in World of Warcraft: Forever (7 Oct. 2026)",
             "https://www.wowhead.com/news=383292/how-pvp-progression-in-world-of-warcraft-forever"),
        ],
        "fr": {
            "title": "WoW Forever : progression PvP, Honneur et rangs",
            "description": "WoW Forever : Honneur, points de rang avec plafond hebdomadaire, équipement PvP bleu puis épique, saisons PvP. Voici comment fonctionne la progression.",
            "h1": "WoW Forever : comment fonctionne la progression PvP",
            "lede": "Blizzard a détaillé le système PvP de **WoW Forever**, qui repose sur deux éléments : l'**Honneur**, une monnaie, et les **points de rang**, qui font monter dans les rangs classiques jusqu'à Grand Maréchal ou Seigneur de guerre. Les gains d'Honneur sont harmonisés entre champs de bataille pour qu'Alterac ne soit plus le choix par défaut. Les rangs ont un **plafond hebdomadaire**, et des saisons PvP avec tâches hebdomadaires s'ajoutent par-dessus.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Équipement PvP** : l'Honneur achète un set **bleu** et un set **épique** ; l'épique demande la pièce bleue plus un Emboldened Seal, bloqué par un **rang minimum**.",
                    "**Rangs** : trinket de PvP au rang 2, armes épiques au rang 14 ; les montures arrivent au rang 11.",
                    "**Toutes les spécialisations servies** : le Chaman aura par exemple des sets soigneur, mêlée et lanceur de sorts.",
                    "**Saisons** : des tâches hebdomadaires donnent Honneur et points de rang, trois d'entre elles rapportent un **point d'héritage** (Legacy Point).",
                ]),
            ],
            "faq": [],
            "links": [
                ("Bêta de WoW Forever", "wow-forever/beta/"),
                ("Progression de personnage", "wow-forever/progression/"),
                ("FAQ WoW Forever", "wow-forever/faq/"),
            ],
        },
        "en": {
            "title": "WoW Forever: PvP Progression, Honor and Ranks",
            "description": "WoW Forever PvP: Honor, rank points with a weekly cap, blue then epic PvP gear and seasonal tasks. Here is how progression works.",
            "h1": "WoW Forever: how PvP progression works",
            "lede": "Blizzard has detailed the **WoW Forever** PvP system, built on two parts: **Honor**, a currency, and **rank points**, which move you up the classic ranks toward High Warlord or Grand Marshal. Honor gains are evened out across battlegrounds so Alterac Valley is no longer the default pick. Ranks have a **weekly cap**, and PvP seasons with weekly tasks sit on top.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**PvP gear**: Honor buys a **blue** set and an **epic** set; the epic needs the blue piece plus an Emboldened Seal, gated by a **minimum rank**.",
                    "**Ranks**: PvP trinket at rank 2, epic weapons at rank 14; mounts come at rank 11.",
                    "**Every spec covered**: Shaman, for example, get healer, melee and caster sets.",
                    "**Seasons**: weekly tasks grant Honor and rank points, and three of them give a **Legacy Point**.",
                ]),
            ],
            "faq": [],
            "links": [
                ("WoW Forever beta", "wow-forever/beta/"),
                ("Character progression", "wow-forever/progression/"),
                ("WoW Forever FAQ", "wow-forever/faq/"),
            ],
        },
    },
    {
        "slug": "champ-de-bataille-iles-darkspear-wow-forever",
        "format": "brief",
        "date": "2026-10-08",
        "updated": "2026-10-08",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_bannerpvp_01.jpg",
        "sources": [
            ("Wowhead : New Battleground Preview in World of Warcraft: Forever - Battle for the Darkspear Islands (7 Oct. 2026)",
             "https://www.wowhead.com/news=383294/new-battleground-preview-in-world-of-warcraft-forever-battle-for-the-darkspear"),
        ],
        "fr": {
            "title": "WoW Forever : champ de bataille des îles Darkspear",
            "description": "WoW Forever : Battle for the Darkspear Islands, nouveau champ de bataille 15v15 niveau 30-60, premier à 2000 points. Accès, récompenses, réputation.",
            "h1": "WoW Forever : le nouveau champ de bataille des îles Darkspear",
            "lede": "Blizzard présente **Battle for the Darkspear Islands**, un nouveau champ de bataille de **WoW Forever** en **15 contre 15**, situé au large du marécage d'Âprefange (Dustwallow Marsh), pour les niveaux 30 à 60. Quatre points de capture et un drapeau central rapportent des points ; la première équipe à **2000 points** gagne. Chaque faction a sa propre réputation avec équipement et consommables à la clé.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Format** : 15v15, capture de points plus drapeau central à ramener dans une base capturée pour marquer davantage.",
                    "**Accès** : par un maître de bataille dans les capitales ou les Tarides, ou via la base des Darkspear Raiders (Horde) ou de la Theramore Expeditionary Force (Alliance).",
                    "**Récompenses** : réputation par faction, avec bijoux, anneaux, capes, armes et pièces d'armure selon le palier.",
                    "**Exalté** : une courte suite de quêtes débloque le tabard exclusif de la faction.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Bêta de WoW Forever", "wow-forever/beta/"),
                ("Progression de personnage", "wow-forever/progression/"),
                ("FAQ WoW Forever", "wow-forever/faq/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Battle for the Darkspear Islands",
            "description": "WoW Forever: Battle for the Darkspear Islands, a new 15v15 battleground for levels 30-60, first to 2000 points. Access, rewards, reputation.",
            "h1": "WoW Forever: the new Battle for the Darkspear Islands battleground",
            "lede": "Blizzard has previewed **Battle for the Darkspear Islands**, a new **WoW Forever** battleground for **15v15**, set off the coast of Dustwallow Marsh for levels 30 to 60. Four capture points and a central flag score points, and the first team to **2000 points** wins. Each faction has its own reputation with gear and consumables as rewards.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Format**: 15v15, point control plus a central flag to carry to a captured base for extra score.",
                    "**Access**: through a battlemaster in the capitals or the Barrens, or via the Darkspear Raiders base (Horde) or Theramore Expeditionary Force base (Alliance).",
                    "**Rewards**: a reputation track per faction, with trinkets, rings, cloaks, weapons and armor by standing.",
                    "**Exalted**: a short questline unlocks the faction's exclusive tabard.",
                ]),
            ],
            "faq": [],
            "links": [
                ("WoW Forever beta", "wow-forever/beta/"),
                ("Character progression", "wow-forever/progression/"),
                ("WoW Forever FAQ", "wow-forever/faq/"),
            ],
        },
    },
    {
        "slug": "skyborne-modeles-sd-formes-druide-2027-wow-forever",
        "format": "brief",
        "date": "2026-10-08",
        "updated": "2026-10-08",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": "druid",
        "image": "https://wow.zamimg.com/images/wow/icons/large/ability_druid_catform.jpg",
        "sources": [
            ("Wowhead : SD Skyborne Models and Druid Forms Arriving in Early 2027 (7 Oct. 2026)",
             "https://www.wowhead.com/news=383298/sd-skyborne-models-and-druid-forms-arriving-in-early-2027"),
        ],
        "fr": {
            "title": "WoW Forever : modèles SD Skyborne et formes de Druide",
            "description": "WoW Forever : Blizzard prépare des modèles SD pour les Skyborne, formes de Druide comprises, pour début 2027, et retouche les formes HD.",
            "h1": "WoW Forever : les Skyborne auront des modèles SD début 2027",
            "lede": "Blizzard annonce que les joueurs **Skyborne** de **WoW Forever** auront bientôt le choix entre modèles HD et **SD**, formes de **Druide** incluses, avec une sortie prévue **début 2027**. Le studio reconnaît que les Skyborne en HD détonnent à côté du monde et des modèles SD. En attendant, les formes de Druide HD sont retouchées : moins de douceur, des textures de fourrure plus détaillées et une saturation ajustée.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Choix SD / HD** : les races d'origine ont déjà ce réglage, les Skyborne l'auront **début 2027**.",
                    "**Druides** : les formes HD sont ajustées en attendant les formes SD.",
                    "**Pas de date précise** : Blizzard promet plus d'informations plus près de la sortie.",
                    "Si tu hésites sur ta classe, nos pages de classes t'aident à choisir.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Calculateur de talents Druide", "wow-forever/talents/druid/"),
                ("Bêta de WoW Forever", "wow-forever/beta/"),
                ("Classes de WoW Forever", "wow-forever/classes/"),
            ],
        },
        "en": {
            "title": "WoW Forever: SD Skyborne Models and Druid Forms",
            "description": "WoW Forever: Blizzard is making SD models for the Skyborne, Druid forms included, for early 2027, and refining the HD Druid forms.",
            "h1": "WoW Forever: Skyborne get SD models in early 2027",
            "lede": "Blizzard says **Skyborne** players in **WoW Forever** will soon be able to choose between HD and **SD** models, **Druid** forms included, with a release planned for **early 2027**. The studio admits the HD Skyborne clash with the SD models and world. Meanwhile the HD Druid forms are being refined: less softness, more detailed fur textures and adjusted saturation.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**SD / HD choice**: the original races already have it, the Skyborne will get it in **early 2027**.",
                    "**Druids**: HD forms are adjusted in the meantime, with SD forms to follow.",
                    "**No exact date**: Blizzard promises more information closer to release.",
                    "Unsure which class to play? Our class pages can help you pick.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Druid talent calculator", "wow-forever/talents/druid/"),
                ("WoW Forever beta", "wow-forever/beta/"),
                ("WoW Forever classes", "wow-forever/classes/"),
            ],
        },
    },
    {
        "slug": "downranking-sorts-nerf-wow-forever",
        "format": "brief",
        "date": "2026-10-09",
        "updated": "2026-10-09",
        "draft": False,
        "tag": "tuning",
        "kind": "nerf",
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/spell_holy_flashheal.jpg",
        "sources": [
            ("Wowhead : Downranking Spells Significantly Nerfed In WoW: Forever (9 Oct. 2026)",
             "https://www.wowhead.com/news=383285/downranking-spells-significantly-nerfed-in-wow-forever"),
        ],
        "fr": {
            "title": "WoW Forever : le downranking fortement nerfé",
            "description": "WoW Forever : lancer un sort de rang très inférieur à ton niveau réduit les dégâts et soins bonus et les chances de proc (Frostbite, Omen of Clarity).",
            "h1": "WoW Forever : le downranking des sorts est fortement nerfé",
            "lede": "Dans une récente build de la bêta de **WoW Forever**, Blizzard a nettement affaibli le **downranking**, cette habitude des lanceurs de sorts et des soigneurs qui consiste à utiliser un rang bas d'un sort. Un sort de rang très inférieur à ton niveau profite moins de tes dégâts et soins bonus, et a moins de chances de déclencher tes talents et capacités de classe. Exemple donné par les développeurs : un **Éclair de givre rang 1** au niveau 60 n'a plus **aucune chance** de déclencher Frostbite.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Soigneurs** : descendre d'un rang pour éviter le surplus de soins et économiser du mana devient moins intéressant, car le soin bonus est réduit.",
                    "**Mages** : il faut choisir entre un ralentissement rapide et un sort capable de déclencher **Frostbite**, plus les deux à la fois.",
                    "**Procs** : les effets comme **Omen of Clarity** sont aussi moins fréquents avec un rang très bas.",
                    "Le texte de la feuille de personnage explique désormais cette réduction.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Guide Mage Givre", "wow-forever/guides/mage/frost/"),
                ("Guide Prêtre Sacré", "wow-forever/guides/priest/holy/"),
                ("Calculateur de talents Mage", "wow-forever/talents/mage/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Downranking Spells Heavily Nerfed",
            "description": "WoW Forever: casting a spell rank far below your level now gets less spell damage and healing and a lower proc chance (Frostbite, Omen of Clarity).",
            "h1": "WoW Forever: spell downranking has been heavily nerfed",
            "lede": "In a recent **WoW Forever** beta build, Blizzard has sharply weakened **downranking**, the habit casters and healers have of using a low rank of a spell. A spell rank far below your level now benefits less from your spell damage and healing, and is less likely to trigger your class abilities and talents. The developers' example: a **rank 1 Frostbolt** at level 60 now has **no chance** to trigger Frostbite.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Healers**: dropping a rank to avoid overhealing and save mana is less attractive, since bonus healing is reduced.",
                    "**Mages**: you must choose between a quick slow and a spell that can trigger **Frostbite**, no longer both at once.",
                    "**Procs**: effects like **Omen of Clarity** also fire less often on a very low rank.",
                    "The character sheet tooltip now explains this reduction.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Frost Mage guide", "wow-forever/guides/mage/frost/"),
                ("Holy Priest guide", "wow-forever/guides/priest/holy/"),
                ("Mage talent calculator", "wow-forever/talents/mage/"),
            ],
        },
    },
    {
        "slug": "dalaran-horde-acces-donjon-wow-forever",
        "format": "brief",
        "date": "2026-10-09",
        "updated": "2026-10-09",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_key_03.jpg",
        "sources": [
            ("Wowhead : Horde are Welcome in Dalaran After Completing the City of Dalaran Dungeon in WoW: Forever (8 Oct. 2026)",
             "https://www.wowhead.com/news=383338/horde-are-welcome-in-dalaran-after-completing-the-city-of-dalaran-dungeon-in-wow"),
        ],
        "fr": {
            "title": "WoW Forever : la Horde peut entrer dans Dalaran",
            "description": "WoW Forever : après le donjon City of Dalaran et la quête Heart of Disruption, les joueurs de la Horde accèdent à Dalaran. Étapes et services.",
            "h1": "WoW Forever : la Horde accède à Dalaran après le donjon",
            "lede": "Dans la bêta de **WoW Forever**, la ville de **Dalaran**, qu'on croyait réservée à l'Alliance, est aussi ouverte à la **Horde**. Il faut terminer le donjon **City of Dalaran** et la suite de quêtes **Heart of Disruption**, qui donne la clé des égouts de Dalaran. Ensuite, on rapporte la Arcane Mote du Shade of the Archmage en ville avec la quête **Shrewd Negotiations**, et les gardes deviennent neutres.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Condition** : donjon City of Dalaran fini, puis quête Shrewd Negotiations rendue à l'archimage Celindra.",
                    "**Gardes** : ils ne sont plus hostiles et laissent passer les joueurs de la Horde.",
                    "**Services** : peu de PNJ proposent des services, mais on y trouve flèches, nourriture, boissons, entraînement de Mage et écuries pour changer de familier.",
                    "**Détail** : on peut aussi pêcher des pièces dans la fontaine.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Donjons de WoW Forever", "wow-forever/dungeons/"),
                ("Bêta de WoW Forever", "wow-forever/beta/"),
                ("Date de sortie de WoW Forever", "wow-forever/sortie/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Horde Can Enter Dalaran",
            "description": "WoW Forever: after the City of Dalaran dungeon and the Heart of Disruption questline, Horde players can enter Dalaran. Steps and services.",
            "h1": "WoW Forever: Horde gains access to Dalaran after the dungeon",
            "lede": "In the **WoW Forever** beta, the city of **Dalaran**, believed to be Alliance-only, is also open to the **Horde**. You must finish the **City of Dalaran** dungeon and the **Heart of Disruption** questline, which gives the Dalaran Sewer Key. You then bring the Arcane Mote from Shade of the Archmage into the city through **Shrewd Negotiations**, and the guards turn neutral.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Requirement**: City of Dalaran dungeon done, then the Shrewd Negotiations quest handed to Archmage Celindra.",
                    "**Guards**: no longer hostile, they let Horde players through.",
                    "**Services**: few NPCs offer services, but you can buy arrows, food and drink, train Mage skills and swap hunter pets at the stables.",
                    "**Bonus**: you can also fish for coins in the fountain.",
                ]),
            ],
            "faq": [],
            "links": [
                ("WoW Forever dungeons", "wow-forever/dungeons/"),
                ("WoW Forever beta", "wow-forever/beta/"),
                ("WoW Forever release date", "wow-forever/sortie/"),
            ],
        },
    },
    {
        "slug": "xp-donjons-plus-20-pourcent-wow-forever",
        "format": "brief",
        "date": "2026-10-09",
        "updated": "2026-10-09",
        "draft": False,
        "tag": "tuning",
        "kind": "up",
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_book_09.jpg",
        "sources": [
            ("Wowhead : Buffs to Dungeon Experience Coming in WoW: Forever (8 Oct. 2026)",
             "https://www.wowhead.com/news=383312/buffs-to-dungeon-experience-coming-in-wow-forever"),
        ],
        "fr": {
            "title": "WoW Forever : +20 % d'XP en donjon",
            "description": "WoW Forever : l'expérience gagnée sur les monstres de donjon augmente de 20 %, pour s'approcher de la vitesse d'xp optimale en quêtes.",
            "h1": "WoW Forever : l'XP des donjons augmente de 20 %",
            "lede": "Blizzard annonce dans le podcast de **WoW Forever** que l'expérience gagnée en tuant des monstres en **donjon** augmente de **20 %**. Un bug d'expérience en donjon a aussi été corrigé. L'objectif : qu'avec un jeu optimal, monter de niveau en donjon aille presque aussi vite que de suivre les meilleures quêtes, sans que les donjons deviennent la seule bonne façon de jouer.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**+20 % d'XP** sur les kills en donjon, de quoi inciter à refaire un donjon plus d'une fois.",
                    "**Correction de bug** : l'expérience en donjon doit être nettement plus agréable.",
                    "**Philosophie** : Blizzard ne veut pas de donjons « une fois et c'est fini », ni de monter uniquement en les enchaînant.",
                    "**Bêta** : ces réglages restent ajustés selon les retours.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Donjons de WoW Forever", "wow-forever/dungeons/"),
                ("Progression de personnage", "wow-forever/progression/"),
                ("FAQ WoW Forever", "wow-forever/faq/"),
            ],
        },
        "en": {
            "title": "WoW Forever: +20% Dungeon XP",
            "description": "WoW Forever: experience from killing dungeon monsters rises by 20%, bringing dungeon leveling close to optimal questing speed.",
            "h1": "WoW Forever: dungeon experience goes up by 20%",
            "lede": "Blizzard announced on the **WoW Forever** podcast that experience from killing monsters in **dungeons** is rising by **20%**. A dungeon experience bug was also fixed. The goal: with optimal play, leveling in dungeons should come close to the speed of the best questing, without dungeons becoming the only good way to play.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**+20% XP** on dungeon kills, giving a reason to run a dungeon more than once.",
                    "**Bug fix**: experience in dungeons should feel significantly better.",
                    "**Philosophy**: Blizzard wants neither one-and-done dungeons nor leveling purely by chaining them.",
                    "**Beta**: these values keep being tuned from feedback.",
                ]),
            ],
            "faq": [],
            "links": [
                ("WoW Forever dungeons", "wow-forever/dungeons/"),
                ("Character progression", "wow-forever/progression/"),
                ("WoW Forever FAQ", "wow-forever/faq/"),
            ],
        },
    },
    {
        "slug": "points-heritage-16-bete-wow-forever",
        "format": "brief",
        "date": "2026-10-09",
        "updated": "2026-10-09",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_book_11.jpg",
        "sources": [
            ("Wowhead : 16 Legacy Points Now Available for Testing on WoW: Forever Beta (8 Oct. 2026)",
             "https://www.wowhead.com/news=383335/16-legacy-points-now-available-for-testing-on-wow-forever-beta"),
        ],
        "fr": {
            "title": "WoW Forever : 16 points d'héritage sur la bêta",
            "description": "WoW Forever : tous les personnages de la bêta ont 16 points d'héritage (Legacy) pour tester l'arbre de talents du compte avant le 4 novembre.",
            "h1": "WoW Forever : 16 points d'héritage à tester sur la bêta",
            "lede": "Dans la dernière build de la bêta de **WoW Forever**, tous les personnages disposent de **16 points d'héritage** (Legacy Points) pour tester le nouvel arbre de talents. Le **système Legacy** est commun à tout le compte : en remplissant certains objectifs, on débloque des points à dépenser dans des bonus pour les métiers, l'aventure ou la débrouillardise. Seize points est le maximum, tous sont ouverts sur la bêta avant la sortie du **4 novembre**.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Test complet** : les 16 points sont déjà débloqués, tu peux essayer toutes les combinaisons.",
                    "**Bonus de compte** : les points améliorent les métiers, l'aventure ou la débrouillardise pour tous tes personnages.",
                    "**En jeu réel** : les points se débloqueront progressivement, via des objectifs.",
                    "**Sortie** : le jeu est prévu le 4 novembre.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Bêta de WoW Forever", "wow-forever/beta/"),
                ("Progression de personnage", "wow-forever/progression/"),
                ("Date de sortie de WoW Forever", "wow-forever/sortie/"),
            ],
        },
        "en": {
            "title": "WoW Forever: 16 Legacy Points on the Beta",
            "description": "WoW Forever: every beta character now has 16 Legacy Points to test the account-wide talent tree before the November 4 release.",
            "h1": "WoW Forever: 16 Legacy Points to test on the beta",
            "lede": "In the latest **WoW Forever** beta build, every character has **16 Legacy Points** to test the new talent tree. The **Legacy System** is account-wide: completing certain objectives unlocks points you spend on bonuses for professions, adventuring or resourcefulness. Sixteen is the maximum, and all of them are open on the beta ahead of the **November 4** launch.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Full test**: all 16 points are already unlocked, so you can try every combination.",
                    "**Account bonuses**: points improve professions, adventuring or resourcefulness for all your characters.",
                    "**On live realms**: points will unlock gradually through objectives.",
                    "**Release**: the game is planned for November 4.",
                ]),
            ],
            "faq": [],
            "links": [
                ("WoW Forever beta", "wow-forever/beta/"),
                ("Character progression", "wow-forever/progression/"),
                ("WoW Forever release date", "wow-forever/sortie/"),
            ],
        },
    },
    {
        "slug": "chaman-quete-niveau-30-armes-wow-forever",
        "format": "brief",
        "date": "2026-10-09",
        "updated": "2026-10-09",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": "shaman",
        "image": "https://wow.zamimg.com/images/wow/icons/large/spell_nature_bloodlust.jpg",
        "sources": [
            ("Wowhead : Unlock Powerful Weapons with Level 30 Shaman Quest in WoW: Forever (9 Oct. 2026)",
             "https://www.wowhead.com/news=383290/unlock-powerful-weapons-with-level-30-shaman-quest-in-wow-forever"),
        ],
        "fr": {
            "title": "WoW Forever : quête Chaman niveau 30, armes puissantes",
            "description": "WoW Forever : la quête Chaman de niveau 30 donne des armes de pugilat ou une masse à deux mains, et devient plus facile depuis la dernière build.",
            "h1": "WoW Forever : la quête d'armes du Chaman niveau 30, simplifiée",
            "lede": "Une suite de quêtes réservée au **Chaman** dans **WoW Forever**, disponible au niveau 30, récompense des armes puissantes : armes de pugilat ou masse à deux mains. Elle enchaîne après la quête du totem de vent : butin de Charlga Razorflank à Razorfen Kraul, collecte de 20 totems à travers Azeroth, puis combat contre des élites de niveau 40 à Thousand Needles. La dernière build la rend nettement plus facile.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Récompenses** : Lightning's Grasp, Tidebringer's Claw ou Rage of the Storm, plus Elementalist's Guard en bonus.",
                    "**Totems** : les créatures réapparaissent plus vite et lâchent plus souvent leurs totems tordus ; de nouveaux monstres en donnent aussi.",
                    "**Eye of the Tempest** (quête Heed My Call) peut maintenant être obtenu par plusieurs joueurs.",
                    "**Remise** : chez Bath'rah le Guetteur de vent, dans les monts d'Alterac.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Guide Chaman Amélioration", "wow-forever/guides/shaman/enhancement/"),
                ("Calculateur de talents Chaman", "wow-forever/talents/shaman/"),
                ("Razorfen Kraul", "wow-forever/dungeons/razorfen-kraul/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Level 30 Shaman Weapon Quest",
            "description": "WoW Forever: the level 30 Shaman quest line rewards fist weapons or a two-handed mace and got easier in the latest beta build.",
            "h1": "WoW Forever: the level 30 Shaman weapon quest is now easier",
            "lede": "A **Shaman**-only quest line in **WoW Forever**, available at level 30, rewards powerful weapons: fist weapons or a two-handed mace. It follows the wind totem quest: loot Charlga Razorflank in Razorfen Kraul, collect 20 totems across Azeroth, then beat level 40 elites in Thousand Needles. The latest build makes it significantly easier.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Rewards**: Lightning's Grasp, Tidebringer's Claw or Rage of the Storm, plus Elementalist's Guard as an extra.",
                    "**Totems**: creatures respawn faster and drop their twisted totems more often, and new monsters drop some too.",
                    "**Eye of the Tempest** (the Heed My Call quest) can now be looted by several players.",
                    "**Turn-in**: Bath'rah the Windwatcher, in the Alterac Mountains.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Enhancement Shaman guide", "wow-forever/guides/shaman/enhancement/"),
                ("Shaman talent calculator", "wow-forever/talents/shaman/"),
                ("Razorfen Kraul", "wow-forever/dungeons/razorfen-kraul/"),
            ],
        },
    },
]

KIND_LABEL = {"up": ("UP", "UP"), "nerf": ("NERF", "NERF"), "eq": ("ÉQUILIBRAGE", "BALANCE")}
FORMAT_LABEL = {"article": ("Analyse", "Analysis"), "brief": ("Brève", "Brief")}


def check():
    for a in ARTICLES:
        assert a.get("format", "article") in FORMAT_LABEL, a["slug"]
        assert a["kind"] in KIND_LABEL or (a.get("format") == "brief" and a["kind"] is None), a["slug"]
        for lang in ("fr", "en"):
            t = a[lang]
            assert len(t["title"]) <= 60, (a["slug"], lang, len(t["title"]))
            assert len(t["description"]) <= 155, (a["slug"], lang, len(t["description"]))


def published():
    """Articles listed on the site. BM_PREVIEW_DRAFTS=1 lists the drafts too, for a local proof-reading build only
    (never deploy a build made with it)."""
    if os.environ.get("BM_PREVIEW_DRAFTS") == "1":
        return list(ARTICLES)
    return [a for a in ARTICLES if not a.get("draft")]


check()


def indexable(a):
    """Drafts never are; a brief only when it links to our own pages (see the module docstring)."""
    if a.get("draft"):
        return False
    if a.get("format") == "brief":
        return bool(a["fr"].get("links")) and bool(a["en"].get("links"))
    return True


def covered_urls():
    """Source urls (and Wowhead news ids) that one of our published pages already covers."""
    urls = {u for a in published() for _, u in a["sources"]}
    ids = {m.group(1) for u in urls for m in [re.search(r"(?:news=|-)(\d{5,})(?:/|$)", u)] if m}
    return urls, ids


def page_for(url):
    """Our published article/brief covering this headline url, or None."""
    m = re.search(r"(?:news=|-)(\d{5,})(?:/|$)", url)
    nid = m.group(1) if m else None
    for a in published():
        for _, u in a["sources"]:
            if u == url or (nid and nid in u):
                return a
    return None

