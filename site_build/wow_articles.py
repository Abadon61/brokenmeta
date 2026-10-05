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

