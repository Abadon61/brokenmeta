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
    {
        "slug": "pretre-discipline-penitence-nerf-wow-forever",
        "date": "2026-10-09",
        "updated": "2026-10-09",
        "draft": False,
        "tag": "tuning",
        "kind": "nerf",
        "class": "priest",
        "image": "assets/img/spec/priest-discipline.png",
        "sources": [
            ("Wowhead : New Class Changes in Latest WoW: Forever Beta Build (8 Oct. 2026)",
             "https://www.wowhead.com/news=383327/new-class-changes-in-latest-wow-forever-beta-build"),
        ],
        "fr": {
            "title": "Nerf Prêtre Discipline WoW Forever : Pénitence affaiblie",
            "description": "Build bêta WoW Forever : Pénitence (Prêtre Discipline) inflige et soigne moins, avec un coefficient de 0,285 à 0,19 et un coût en mana plus élevé.",
            "h1": "Prêtre Discipline dans WoW Forever : le nerf de Pénitence",
            "lede": "Le dernier build de la bêta de **WoW Forever** est un **nerf de Pénitence** (Penance), le sort signature du **Prêtre Discipline** : la salve fait moins de dégâts, soigne moins, profite moins de la puissance des sorts et coûte plus de mana. D'après la liste de changements de Wowhead, le [nerf]coefficient de puissance des sorts passe de 0,285 à 0,19[/nerf] et le [nerf]coût augmente à tous les rangs[/nerf].",
            "body": [
                ("cards", [("spell_holy_penance", "Pénitence : dégâts", "81 à 45 par tick au rang 1", "nerf"),
                           ("spell_holy_penance", "Pénitence : soins", "184 à 134 par tick au rang 1", "nerf"),
                           ("spell_holy_penance", "Coefficient de sorts", "0,285 à 0,19", "nerf"),
                           ("spell_holy_penance", "Coût en mana", "100 à 150 au rang 1", "nerf")]),
                ("h2", "Pénitence du Prêtre Discipline : tous les changements"),
                ("list", [
                    "{nerf} {i:spell_holy_penance} **Dégâts** du sacré : [nerf]81 à 45[/nerf] au rang 1, [nerf]131 à 92[/nerf] au dernier rang (valeurs de base, par tick).",
                    "{nerf} {i:spell_holy_penance} **Soins** : [nerf]184 à 134[/nerf] au rang 1, [nerf]673 à 425[/nerf] au dernier rang (valeurs de base, par tick).",
                    "{nerf} Le **coefficient de puissance des sorts** tombe de [nerf]0,285 à 0,19[/nerf] : l'équipement de soins ou de dégâts compte moins pour Pénitence.",
                    "{nerf} Le **coût en mana** monte : [nerf]100 à 150[/nerf] (rang 1), [nerf]185 à 220[/nerf], [nerf]355 à 385[/nerf] au dernier rang.",
                    "La rune de gants **Pénitence** reprend les mêmes nouvelles valeurs.",
                ]),
                ("bars", {"unit": "points par tick", "rows": [
                    ("Dégâts rang 1", 81, 45), ("Dégâts dernier rang", 131, 92),
                    ("Soins rang 1", 184, 134), ("Soins dernier rang", 673, 425)]}),
                ("h2", "Ce que ça change pour ton Prêtre Discipline"),
                ("list", [
                    "Pénitence reste un sort puissant, mais il devient **plus cher et moins efficace** : attends-toi à gérer ton mana plus finement, surtout en donjon.",
                    "Le nerf touche aussi bien le **DPS** (Pénitence sur un ennemi) que le **soin** (Pénitence sur un allié).",
                    "Nous ne chiffrons pas l'impact en DPS ou en HPS global : le Prêtre Discipline [eq]n'est pas simulé[/eq] dans notre simulateur niveau 60, donc aucun pourcentage n'est donné.",
                ]),
                ("note", "Méthode : valeurs lues dans la liste de changements de Wowhead du 8 octobre 2026 (ancienne valeur puis nouvelle), réécrites ; aucune simulation. Les valeurs sont des valeurs de base, avant puissance des sorts. La bêta change souvent."),
            ],
            "faq": [
                ("Pénitence est-elle nerf dans WoW Forever ?", "Oui, dans le dernier build de la bêta : moins de dégâts et de soins (par exemple 81 à 45 en dégâts au rang 1), un coefficient de puissance des sorts de 0,285 à 0,19 et un coût en mana plus élevé."),
                ("Le Prêtre Discipline est-il simulé sur BrokenMeta ?", "Pas encore : nous ne donnons donc aucun pourcentage de DPS pour ce nerf, seulement les valeurs publiées."),
            ],
            "links": [
                ("Guide Prêtre Discipline", "wow-forever/guides/priest/discipline/"),
                ("Calculateur de talents Prêtre", "wow-forever/talents/priest/"),
            ],
        },
        "en": {
            "title": "Discipline Priest nerf WoW Forever: Penance weakened",
            "description": "WoW Forever beta build: Penance (Discipline Priest) deals and heals less, with a spell power coefficient cut from 0.285 to 0.19 and a higher mana cost.",
            "h1": "Discipline Priest in WoW Forever: the Penance nerf",
            "lede": "The latest **WoW Forever** beta build is a **nerf to Penance**, the signature spell of the **Discipline Priest**: the volley deals less damage, heals less, scales less with spell power and costs more mana. According to Wowhead's change list, the [nerf]spell power coefficient drops from 0.285 to 0.19[/nerf] and the [nerf]cost goes up at every rank[/nerf].",
            "body": [
                ("cards", [("spell_holy_penance", "Penance: damage", "81 to 45 per tick at rank 1", "nerf"),
                           ("spell_holy_penance", "Penance: healing", "184 to 134 per tick at rank 1", "nerf"),
                           ("spell_holy_penance", "Spell coefficient", "0.285 to 0.19", "nerf"),
                           ("spell_holy_penance", "Mana cost", "100 to 150 at rank 1", "nerf")]),
                ("h2", "Discipline Priest Penance: every change"),
                ("list", [
                    "{nerf} {i:spell_holy_penance} Holy **damage**: [nerf]81 to 45[/nerf] at rank 1, [nerf]131 to 92[/nerf] at the top rank (base values, per tick).",
                    "{nerf} {i:spell_holy_penance} **Healing**: [nerf]184 to 134[/nerf] at rank 1, [nerf]673 to 425[/nerf] at the top rank (base values, per tick).",
                    "{nerf} The **spell power coefficient** falls from [nerf]0.285 to 0.19[/nerf]: healing or damage gear matters less for Penance.",
                    "{nerf} The **mana cost** rises: [nerf]100 to 150[/nerf] (rank 1), [nerf]185 to 220[/nerf], [nerf]355 to 385[/nerf] at the top rank.",
                    "The **Penance** glove rune takes the same new values.",
                ]),
                ("bars", {"unit": "points per tick", "rows": [
                    ("Damage rank 1", 81, 45), ("Damage top rank", 131, 92),
                    ("Healing rank 1", 184, 134), ("Healing top rank", 673, 425)]}),
                ("h2", "What it means for your Discipline Priest"),
                ("list", [
                    "Penance is still a strong spell, but it becomes **more expensive and less efficient**: expect to manage mana more carefully, especially in dungeons.",
                    "The nerf hits both **damage** (Penance on an enemy) and **healing** (Penance on an ally).",
                    "We put no number on the overall DPS or HPS impact: Discipline Priest is [eq]not simulated[/eq] in our level-60 simulator, so no percentage is given.",
                ]),
                ("note", "Method: values read from Wowhead's October 8, 2026 change list (old value then new value), rewritten; no simulation. Values are base values, before spell power. The beta changes often."),
            ],
            "faq": [
                ("Is Penance nerfed in WoW Forever?", "Yes, in the latest beta build: less damage and healing (for example 81 to 45 damage at rank 1), a spell power coefficient cut from 0.285 to 0.19 and a higher mana cost."),
                ("Is the Discipline Priest simulated on BrokenMeta?", "Not yet, so we give no DPS percentage for this nerf, only the published values."),
            ],
            "links": [
                ("Discipline Priest guide", "wow-forever/guides/priest/discipline/"),
                ("Priest talent calculator", "wow-forever/talents/priest/"),
            ],
        },
    },
    {
        "slug": "wolfshead-helm-nerf-druide-wow-forever",
        "date": "2026-10-09",
        "updated": "2026-10-09",
        "draft": False,
        "tag": "tuning",
        "kind": "nerf",
        "class": "druid",
        "image": "assets/img/spec/druid-feral-combat.png",
        "sources": [
            ("Wowhead : Wolfshead Helm Nerfed in Latest WoW: Forever Beta Build (9 Oct. 2026)",
             "https://www.wowhead.com/news=383334/wolfshead-helm-nerfed-in-latest-wow-forever-beta-build"),
        ],
        "fr": {
            "title": "Nerf Wolfshead Helm WoW Forever : 20 à 5 énergie",
            "description": "Build bêta WoW Forever : le Wolfshead Helm du Druide Farouche ne donne plus que 5 énergie avec Shifting Power, contre 20 avant. Ce qui change.",
            "h1": "Druide Farouche : le nerf du Wolfshead Helm dans WoW Forever",
            "lede": "Le dernier build de la bêta de **WoW Forever** est un **nerf du Wolfshead Helm**, le casque de cuir de niveau 40 du **Druide Farouche**. Dans WoW Classic, il donnait de l'énergie à chaque passage en forme de félin, ce qui nourrissait le « powershifting ». Dans Forever, il agit sur **Shifting Power** : le bonus [nerf]passe de 20 à 5 énergie[/nerf], selon Wowhead.",
            "body": [
                ("cards", [("spell_druid_displacement", "Shifting Power", "Bonus du casque : 20 à 5 énergie", "nerf"),
                           ("ability_mount_jungletiger", "Wolfshead Helm", "Casque de cuir niveau 40", "nerf")]),
                ("h2", "Wolfshead Helm : ce qui change"),
                ("list", [
                    "{nerf} **Wolfshead Helm** : le bonus d'énergie obtenu en activant {i:spell_druid_displacement} **Shifting Power** tombe de [nerf]20 à 5[/nerf].",
                    "Le casque ne sert plus de moteur au powershifting : Shifting Power convertit du mana en énergie sans macro, et le casque n'ajoute qu'un petit complément.",
                ]),
                ("bars", {"unit": "énergie", "rows": [("Bonus de Shifting Power", 20, 5)]}),
                ("h2", "Ce que ça change pour ton Druide Farouche"),
                ("list", [
                    "Dans Classic, le Wolfshead Helm était le meilleur objet de son emplacement pendant tout Classic et l'essentiel de Burning Crusade : Wowhead rappelle que beaucoup de joueurs ne voulaient pas le revoir indétrônable. Ce nerf va dans ce sens.",
                    "Le casque reste utile, mais il faudra comparer avec d'autres casques de niveau 40 plutôt que le prendre par défaut.",
                    "Nous ne chiffrons pas ce changement : le build Farouche [eq]n'est pas simulé[/eq] dans notre simulateur niveau 60, donc aucun pourcentage de DPS n'est donné.",
                ]),
                ("note", "Méthode : faits tirés de l'article Wowhead du 9 octobre 2026, réécrits ; aucune simulation ni classement d'objets. La bêta change souvent."),
            ],
            "faq": [
                ("Le Wolfshead Helm est-il nerf dans WoW Forever ?", "Oui : dans le dernier build de la bêta, il ne donne plus que 5 énergie avec Shifting Power, contre 20 auparavant."),
                ("Que fait le Wolfshead Helm dans WoW Forever ?", "Il augmente l'énergie gagnée en activant Shifting Power, le talent qui convertit du mana en énergie et remplace le powershifting d'origine."),
            ],
            "links": [
                ("Guide Druide Farouche", "wow-forever/guides/druid/feral-combat/"),
                ("Calculateur de talents Druide", "wow-forever/talents/druid/"),
                ("Shifting Power : l'article", "wow-forever/actualites/druide-farouche-shifting-power-wow-forever/"),
            ],
        },
        "en": {
            "title": "Wolfshead Helm nerf WoW Forever: 20 to 5 Energy",
            "description": "WoW Forever beta build: the Feral Druid's Wolfshead Helm now gives only 5 Energy with Shifting Power, down from 20. What changes for you.",
            "h1": "Feral Druid: the Wolfshead Helm nerf in WoW Forever",
            "lede": "The latest **WoW Forever** beta build is a **nerf to the Wolfshead Helm**, the level 40 leather helm of the **Feral Druid**. In WoW Classic it granted Energy on every shift into Cat Form, which fuelled \"powershifting\". In Forever it works with **Shifting Power**: the bonus [nerf]drops from 20 to 5 Energy[/nerf], according to Wowhead.",
            "body": [
                ("cards", [("spell_druid_displacement", "Shifting Power", "Helm bonus: 20 to 5 Energy", "nerf"),
                           ("ability_mount_jungletiger", "Wolfshead Helm", "Level 40 leather helm", "nerf")]),
                ("h2", "Wolfshead Helm: what changes"),
                ("list", [
                    "{nerf} **Wolfshead Helm**: the Energy bonus gained when you activate {i:spell_druid_displacement} **Shifting Power** falls from [nerf]20 to 5[/nerf].",
                    "The helm no longer drives powershifting: Shifting Power converts mana into Energy without a macro, and the helm only adds a small extra.",
                ]),
                ("bars", {"unit": "Energy", "rows": [("Shifting Power bonus", 20, 5)]}),
                ("h2", "What it means for your Feral Druid"),
                ("list", [
                    "In Classic, the Wolfshead Helm was the best item in its slot for all of Classic and most of Burning Crusade: Wowhead notes many players did not want it to stay unbeatable. This nerf goes that way.",
                    "The helm is still useful, but you should compare it with other level 40 helms rather than take it by default.",
                    "We put no number on this change: the Feral build is [eq]not simulated[/eq] in our level-60 simulator, so no DPS percentage is given.",
                ]),
                ("note", "Method: facts taken from Wowhead's October 9, 2026 article, rewritten; no simulation or item ranking. The beta changes often."),
            ],
            "faq": [
                ("Is the Wolfshead Helm nerfed in WoW Forever?", "Yes: in the latest beta build it only gives 5 Energy with Shifting Power, down from 20."),
                ("What does the Wolfshead Helm do in WoW Forever?", "It increases the Energy gained when you activate Shifting Power, the talent that converts mana into Energy and replaces original powershifting."),
            ],
            "links": [
                ("Feral Druid guide", "wow-forever/guides/druid/feral-combat/"),
                ("Druid talent calculator", "wow-forever/talents/druid/"),
                ("The Shifting Power article", "wow-forever/actualites/druide-farouche-shifting-power-wow-forever/"),
            ],
        },
    },
    {
        "slug": "truthseekers-bow-niveau-40-nerf-wow-forever",
        "date": "2026-10-13",
        "updated": "2026-10-13",
        "draft": False,
        "tag": "tuning",
        "kind": "nerf",
        "class": "hunter",
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_weapon_bow_08.jpg",
        "sources": [
            ("Wowhead : Truthseeker's Bow is now restricted to Level 40 in WoW: Forever (8 Oct. 2026)",
             "https://www.wowhead.com/news=383326/truthseekers-bow-is-now-restricted-to-level-40-in-wow-forever"),
        ],
        "fr": {
            "title": "Nerf Truthseeker's Bow WoW Forever : niveau 40 requis",
            "description": "Bêta WoW Forever : le Truthseeker's Bow, récompense des livres de bibliothèque, exige désormais le niveau 40 au lieu du 30. Ce qui change.",
            "h1": "Nerf du Truthseeker's Bow dans WoW Forever : l'arc passe au niveau 40",
            "lede": "Dans le dernier build de la bêta de **WoW Forever**, le **Truthseeker's Bow** subit un **nerf** : cet arc, récompense de la quête des livres de bibliothèque au **niveau 30**, demande maintenant le [nerf]niveau 40[/nerf] pour être équipé. Les **Chasseurs** (et les autres porteurs d'arc) ne pourront donc plus s'en servir dès la remise des 25 livres.",
            "body": [
                ("cards", [("inv_weapon_bow_08", "Truthseeker's Bow", "Niveau requis : 30 à 40", "nerf"),
                           ("inv_misc_book_09", "Quête des livres", "25 livres rendus au niveau 30", "eq")]),
                ("h2", "Truthseeker's Bow : ce qui change"),
                ("list", [
                    "{nerf} **Truthseeker's Bow** : l'arc ne peut plus être équipé dès le niveau 30, il exige le [nerf]niveau 40[/nerf].",
                    "{eq} Statistiques inchangées : arc de niveau d'objet 45, 46 - 87 de dégâts, vitesse 2,80 (environ 23,7 DPS), +7 Agilité et +3 Endurance.",
                    "Les deux autres choix de la quête ne s'équipaient déjà qu'au niveau 40 : l'arc était le seul à être utilisable tout de suite, ce qui n'est plus le cas.",
                ]),
                ("bars", {"unit": "niveau requis", "rows": [("Truthseeker's Bow", 30, 40)]}),
                ("h2", "Ce que ça change pour ton Chasseur"),
                ("list", [
                    "Si tu comptais sur cet arc pour passer le niveau 30, oublie-le : prévois une autre arme à distance.",
                    "L'arc reste intéressant plus tard : il garde son niveau d'objet 45 et n'est plus qu'une récompense de milieu de parcours.",
                    "Nous ne chiffrons pas ce changement : aucune simulation ni classement d'objets n'a été fait ici, donc aucun pourcentage de DPS n'est donné.",
                ]),
                ("note", "Méthode : faits tirés de l'article Wowhead du 8 octobre 2026, réécrits ; aucune simulation. La bêta change souvent."),
            ],
            "faq": [
                ("Le Truthseeker's Bow est-il nerfé dans WoW Forever ?", "Oui : dans le dernier build de la bêta, il demande le niveau 40 pour être équipé, alors qu'on pouvait l'utiliser dès le niveau 30."),
                ("Comment obtenir le Truthseeker's Bow dans WoW Forever ?", "C'est l'une des récompenses de la quête de livres de bibliothèque, débloquée au niveau 30 en rendant 25 livres."),
            ],
            "links": [
                ("Guide Chasseur Précision", "wow-forever/guides/hunter/marksmanship/"),
                ("Calculateur de talents Chasseur", "wow-forever/talents/hunter/"),
                ("L'arc des livres de bibliothèque", "wow-forever/actualites/livres-bibliotheque-arc-niveau-30-wow-forever/"),
            ],
        },
        "en": {
            "title": "Truthseeker's Bow nerf WoW Forever: level 40 needed",
            "description": "WoW Forever beta: the Truthseeker's Bow, a library-book reward, now needs level 40 instead of 30. Here is what changes for you.",
            "h1": "Truthseeker's Bow nerf in WoW Forever: the bow moves to level 40",
            "lede": "In the latest **WoW Forever** beta build, the **Truthseeker's Bow** gets a **nerf**: this bow, a reward of the library-book quest at **level 30**, now requires [nerf]level 40[/nerf] to equip. **Hunters** (and other bow users) can no longer use it as soon as the 25 books are handed in.",
            "body": [
                ("cards", [("inv_weapon_bow_08", "Truthseeker's Bow", "Required level: 30 to 40", "nerf"),
                           ("inv_misc_book_09", "Library book quest", "25 books handed in at level 30", "eq")]),
                ("h2", "Truthseeker's Bow: what changes"),
                ("list", [
                    "{nerf} **Truthseeker's Bow**: the bow can no longer be equipped at level 30, it now requires [nerf]level 40[/nerf].",
                    "{eq} Stats unchanged: item level 45 bow, 46 - 87 damage, speed 2.80 (about 23.7 DPS), +7 Agility and +3 Stamina.",
                    "The quest's other two reward choices could already only be equipped at level 40: the bow was the only one usable right away, which is no longer true.",
                ]),
                ("bars", {"unit": "required level", "rows": [("Truthseeker's Bow", 30, 40)]}),
                ("h2", "What it means for your Hunter"),
                ("list", [
                    "If you counted on this bow to get through level 30, forget it: plan on another ranged weapon.",
                    "The bow stays interesting later: it keeps its item level 45 and becomes a mid-journey reward.",
                    "We put no number on this change: no simulation or item ranking was run here, so no DPS percentage is given.",
                ]),
                ("note", "Method: facts taken from Wowhead's October 8, 2026 article, rewritten; no simulation. The beta changes often."),
            ],
            "faq": [
                ("Is the Truthseeker's Bow nerfed in WoW Forever?", "Yes: in the latest beta build it requires level 40 to equip, whereas it could be used from level 30."),
                ("How do you get the Truthseeker's Bow in WoW Forever?", "It is one of the rewards of the library-book quest, unlocked at level 30 by handing in 25 books."),
            ],
            "links": [
                ("Marksmanship Hunter guide", "wow-forever/guides/hunter/marksmanship/"),
                ("Hunter talent calculator", "wow-forever/talents/hunter/"),
                ("The library-book bow", "wow-forever/actualites/livres-bibliotheque-arc-niveau-30-wow-forever/"),
            ],
        },
    },
    {
        "slug": 'penalite-resurrection-durabilite-wow-forever',
        "format": "brief",
        "date": "2026-10-10",
        "updated": "2026-10-10",
        "draft": False,
        "tag": 'tuning',
        "kind": 'up',
        "class": None,
        "image": 'https://wow.zamimg.com/images/wow/icons/large/spell_holy_resurrection.jpg',
        "sources": [
            ('Wowhead : Durability Loss from Resurrection Penalty Reduced in WoW: Forever Beta Build 4 (8 Oct. 2026)',
             'https://www.wowhead.com/news=383325/durability-loss-from-resurrection-penalty-reduced-in-wow-forever-beta-build-4'),
        ],
        "fr": {
            "title": 'WoW Forever : mort moins chère chez le Spirit Healer',
            "description": 'WoW Forever, bêta build 4 : ressusciter chez le Spirit Healer coûte 25 % de durabilité au lieu de 50 %. La maladie de résurrection reste.',
            "h1": 'WoW Forever : la pénalité de durabilité à la résurrection est divisée par deux',
            "lede": "Dans le **build 4** de la bêta de **WoW Forever**, la pénalité pour revenir à la vie chez un **Spirit Healer** (guérisseur des esprits) baisse : la perte de durabilité de l'équipement passe de **50 % à 25 %**. Courir jusqu'à son cadavre reste gratuit et la **maladie de résurrection**, qui affaiblit le personnage un court moment, s'applique toujours à ceux qui préfèrent le Spirit Healer.",
            "body": [
                ("h2", 'Ce que ça change pour toi'),
                ("list", ["**Réparations** : une mort chez le Spirit Healer coûte deux fois moins de durabilité, donc moins d'or chez le réparateur.", '**Maladie de résurrection** : inchangée, tu restes affaibli un court moment.', "**Courir à son corps** reste le choix sans aucune pénalité quand c'est possible, surtout en donjon."]),
            ],
            "faq": [],
            "links": [('Donjons de WoW Forever', 'wow-forever/dungeons/'), ('Bêta de WoW Forever', 'wow-forever/beta/'), ('FAQ WoW Forever', 'wow-forever/faq/')],
        },
        "en": {
            "title": 'WoW Forever: Cheaper Spirit Healer Resurrection',
            "description": 'WoW Forever beta build 4: resurrecting at a Spirit Healer now costs 25% durability instead of 50%. Resurrection Sickness still applies.',
            "h1": 'WoW Forever: the resurrection durability penalty is cut in half',
            "lede": 'In **build 4** of the **WoW Forever** beta, the penalty for coming back at a **Spirit Healer** is lighter: the durability lost on your gear drops from **50% to 25%**. Running back to your corpse remains free, and **Resurrection Sickness**, which weakens your character for a short time, still applies to anyone who picks the Spirit Healer.',
            "body": [
                ("h2", 'What it means for you'),
                ("list", ['**Repairs**: a death at the Spirit Healer costs half the durability, so less gold at the repair vendor.', '**Resurrection Sickness**: unchanged, you stay weakened for a short time.', '**Running to your corpse** is still the penalty-free choice when you can, especially in dungeons.']),
            ],
            "faq": [],
            "links": [('WoW Forever dungeons', 'wow-forever/dungeons/'), ('WoW Forever beta', 'wow-forever/beta/'), ('WoW Forever FAQ', 'wow-forever/faq/')],
        },
    },
    {
        "slug": 'recompenses-quetes-donjon-wetlands-wow-forever',
        "format": "brief",
        "date": "2026-10-10",
        "updated": "2026-10-10",
        "draft": False,
        "tag": 'tuning',
        "kind": 'nerf',
        "class": None,
        "image": 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_map_01.jpg',
        "sources": [
            ('Wowhead : More Dungeon Quest Rewards Reduced in Rarity in Latest WoW: Forever Build (8 Oct. 2026)',
             'https://www.wowhead.com/news=383330/more-dungeon-quest-rewards-reduced-in-rarity-in-latest-wow-forever-build'),
        ],
        "fr": {
            "title": 'WoW Forever : quêtes du donjon Wetlands moins généreuses',
            "description": 'WoW Forever : les récompenses de quêtes du donjon Excavation Site: Wetlands perdent en rareté dans le dernier build de la bêta.',
            "h1": 'WoW Forever : les récompenses du donjon Excavation Site: Wetlands rabaissées',
            "lede": "Le dernier build de la bêta de **WoW Forever** réduit la **rareté des récompenses de quêtes** du nouveau donjon **Excavation Site: Wetlands**. Ce donjon attirait beaucoup de monde depuis le passage au niveau 30 maximum. Les quêtes restent intéressantes à faire, mais l'équipement obtenu est moins attractif qu'avant, avec des statistiques revues à la baisse sur plusieurs pièces. D'autres pièces gardent leur rareté mais changent de statistiques.",
            "body": [
                ("h2", 'Ce que ça change pour toi'),
                ("list", ["**Armes, bijoux et armures** de niveau d'objet 33 à 43 touchés : haches, masses, anneaux, bracelets, ceinture, amulettes.", "**Statistiques en baisse** sur la plupart des pièces, par exemple moins de dégâts d'arme ou moins de bonus aux sorts.", "**Quand même utile** : les quêtes du donjon restent une source d'équipement pour monter au niveau 30.", '**Dos** : deux capes gardent leur rareté mais leurs statistiques changent.']),
            ],
            "faq": [],
            "links": [('Donjons de WoW Forever', 'wow-forever/dungeons/'), ('Bêta de WoW Forever', 'wow-forever/beta/')],
        },
        "en": {
            "title": 'WoW Forever: Wetlands Dungeon Quest Rewards Nerfed',
            "description": 'WoW Forever: quest rewards from the Excavation Site: Wetlands dungeon lose rarity in the latest beta build. Several items also get lower stats.',
            "h1": 'WoW Forever: Excavation Site: Wetlands quest rewards toned down',
            "lede": 'The latest **WoW Forever** beta build lowers the **rarity of quest rewards** from the new **Excavation Site: Wetlands** dungeon, which drew crowds once the level cap rose to 30. The quests are still worth doing, but the gear is less appealing than before, with weaker stats on several pieces. A few other items keep their rarity but get different stats.',
            "body": [
                ("h2", 'What it means for you'),
                ("list", ['**Weapons, jewelry and armor** at item level 33 to 43 are affected: axes, maces, rings, bracers, a belt, necks.', '**Lower stats** on most pieces, for example less weapon damage or smaller spell bonuses.', '**Still useful**: the dungeon quests remain a source of gear on the way to level 30.', '**Cloaks**: two keep their rarity but get different stats.']),
            ],
            "faq": [],
            "links": [('WoW Forever dungeons', 'wow-forever/dungeons/'), ('WoW Forever beta', 'wow-forever/beta/')],
        },
    },
    {
        "slug": 'nouveaux-sets-donjon-defias-violet-kroldok-wow-forever',
        "format": "brief",
        "date": "2026-10-10",
        "updated": "2026-10-10",
        "draft": False,
        "tag": 'news',
        "kind": 'eq',
        "class": None,
        "image": 'https://wow.zamimg.com/images/wow/icons/large/inv_chest_cloth_17.jpg',
        "sources": [
            ('Wowhead : Three New Gear Sets Revealed in Latest WoW: Forever Beta Build (9 Oct. 2026)',
             'https://www.wowhead.com/news=383336/three-new-gear-sets-revealed-in-latest-wow-forever-beta-build'),
        ],
        "fr": {
            "title": 'WoW Forever : 3 nouveaux sets de donjon (Deadmines, Dalaran)',
            "description": "WoW Forever : trois sets découverts, Defias Enforcer's Garb, Violet Sorcerer's Vestments et Krol'dok Battlegear, liés à des donjons.",
            "h1": "WoW Forever : trois nouveaux sets d'équipement liés à des donjons",
            "lede": "Le dernier build de la bêta de **WoW Forever** contient trois **nouveaux sets** : **Defias Enforcer's Garb**, **Violet Sorcerer's Vestments** et **Krol'dok Battlegear**. Leurs noms laissent penser qu'ils viennent des Deadmines, du donjon City of Dalaran et de Krol'dok Stronghold, un donjon de niveau 40 pas encore jouable en bêta. Les bonus de set sont déjà visibles dans les données du jeu.",
            "body": [
                ("h2", 'Ce que ça change pour toi'),
                ("list", ["**Defias Enforcer's Garb** : +10 résistance au feu, +15 endurance, +1 épées, puis une chance d'augmenter les critiques de 2 % (doublé dans les marais).", "**Violet Sorcerer's Vestments** : +5 résistance aux arcanes, +10 esprit, régénération de mana en incantant, et une chance d'invoquer un élémentaire des arcanes.", "**Krol'dok Battlegear** : +100 armure, +5 défense, soin sur blocage et gain d'endurance cumulable quand tu subis des dégâts.", "**À vérifier** : l'origine exacte des pièces reste à confirmer en jouant les donjons."]),
            ],
            "faq": [],
            "links": [('Donjons de WoW Forever', 'wow-forever/dungeons/'), ('Donjon Deadmines', 'wow-forever/dungeons/deadmines/'), ('Bêta de WoW Forever', 'wow-forever/beta/')],
        },
        "en": {
            "title": 'WoW Forever: 3 New Dungeon Gear Sets Found',
            "description": "WoW Forever: three new sets found in the beta, Defias Enforcer's Garb, Violet Sorcerer's Vestments and Krol'dok Battlegear, tied to dungeons.",
            "h1": 'WoW Forever: three new dungeon-themed gear sets',
            "lede": "The latest **WoW Forever** beta build contains three **new gear sets**: **Defias Enforcer's Garb**, **Violet Sorcerer's Vestments** and **Krol'dok Battlegear**. Their names point to the Deadmines, the City of Dalaran dungeon and Krol'dok Stronghold, a level 40 dungeon not yet playable on the beta. The set bonuses are already visible in the game data.",
            "body": [
                ("h2", 'What it means for you'),
                ("list", ["**Defias Enforcer's Garb**: +10 fire resistance, +15 stamina, +1 swords, then a chance to raise crit by 2% (doubled in swamps).", "**Violet Sorcerer's Vestments**: +5 arcane resistance, +10 spirit, mana regeneration while casting, and a chance to summon an Arcane Elemental.", "**Krol'dok Battlegear**: +100 armor, +5 defense, healing on block and a stacking stamina gain when you take damage.", '**To confirm**: the exact source of each piece still has to be checked in the dungeons.']),
            ],
            "faq": [],
            "links": [('WoW Forever dungeons', 'wow-forever/dungeons/'), ('Deadmines dungeon', 'wow-forever/dungeons/deadmines/'), ('WoW Forever beta', 'wow-forever/beta/')],
        },
    },
    {
        "slug": 'gdkp-interdit-na-europe-wow-forever',
        "format": "brief",
        "date": "2026-10-10",
        "updated": "2026-10-10",
        "draft": False,
        "tag": 'news',
        "kind": None,
        "class": None,
        "image": 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_coin_01.jpg',
        "sources": [
            ('Wowhead : GDKP Ban Only Applies to NA and Europe Realms - 4Gamers Interview (9 Oct. 2026)',
             'https://www.wowhead.com/news=383345/gdkp-ban-only-applies-to-na-and-europe-realms-4gamers-interview'),
        ],
        "fr": {
            "title": "WoW Forever : l'interdiction du GDKP ne vise que NA et EU",
            "description": "WoW Forever : selon Blizzard, l'interdiction du GDKP ne s'applique qu'aux royaumes d'Amérique du Nord et d'Europe. Or et économie.",
            "h1": "WoW Forever : le ban du GDKP ne concerne que l'Amérique du Nord et l'Europe",
            "lede": "Dans une interview avec 4Gamers Taiwan, Clay Stone précise que l'**interdiction du GDKP** annoncée pour **WoW Forever** ne s'applique qu'aux régions **Amérique du Nord et Europe**. Blizzard justifie le ban par la protection des joueurs aux moyens limités et par la lutte contre l'achat d'or et le blanchiment. L'équipe dit aussi que les joueurs gagneront nettement plus d'or que dans le Classic d'origine.",
            "body": [
                ("h2", 'Ce que ça change pour toi'),
                ("list", ["**Joueur européen** : le GDKP (enchères d'objets en or dans les raids) sera interdit sur tes royaumes.", '**Autres régions** : pas concernées, selon cette interview.', "**Économie** : acheter à l'hôtel des ventes reste au cœur du jeu, avec plus d'or gagné qu'en Classic."]),
            ],
            "faq": [],
            "links": [('FAQ WoW Forever', 'wow-forever/faq/'), ('Raids de WoW Forever', 'wow-forever/raids/'), ('Date de sortie de WoW Forever', 'wow-forever/sortie/')],
        },
        "en": {
            "title": 'WoW Forever: GDKP Ban Only Covers NA and EU',
            "description": 'WoW Forever: per Blizzard, the GDKP ban only applies to North America and Europe realms. What it means for gold and the economy.',
            "h1": 'WoW Forever: the GDKP ban only applies to North America and Europe',
            "lede": 'In an interview with 4Gamers Taiwan, Clay Stone clarified that the **GDKP ban** announced for **WoW Forever** only applies to **North America and Europe**. Blizzard justifies it by protecting players with fewer resources and by fighting gold buying and laundering. The team also says players will earn noticeably more gold than in the original Classic.',
            "body": [
                ("h2", 'What it means for you'),
                ("list", ['**European player**: GDKP (gold-bid loot auctions in raids) will be banned on your realms.', '**Other regions**: not covered, according to this interview.', '**Economy**: buying from the Auction House stays a core part of the game, with more gold earned than in Classic.']),
            ],
            "faq": [],
            "links": [('WoW Forever FAQ', 'wow-forever/faq/'), ('WoW Forever raids', 'wow-forever/raids/'), ('WoW Forever release date', 'wow-forever/sortie/')],
        },
    },
    {
        "slug": "classes-pas-modernisees-interview-techradar-wow-forever",
        "format": "brief",
        "date": "2026-10-13",
        "updated": "2026-10-13",
        "draft": False,
        "tag": "dev",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_book_09.jpg",
        "sources": [
            ("Wowhead : WoW: Forever Classes Won't Be Modernized - TechRadar Interview with Blizzard (12 Oct. 2026)",
             "https://www.wowhead.com/news=383378/wow-forever-classes-wont-be-modernized-techradar-interview-with-blizzard"),
        ],
        "fr": {
            "title": "WoW Forever : classes non modernisées, respec chère",
            "description": "Interview de Blizzard sur WoW Forever : classes Classic conservées, respec au prix croissant, pas de races Retail, pas de pierres de rencontre.",
            "h1": "WoW Forever : Blizzard ne modernisera pas les classes",
            "lede": "Dans une série d'interviews avec TechRadar, Blizzard détaille sa vision de **WoW Forever**. Les **classes Classic** ne seront pas refondues : elles doivent rester simples, mais avec une vraie profondeur, et le rythme du combat d'origine est conservé. Le changement de spécialisation ne sera pas bon marché : son prix grimpe vite et se réinitialise une fois par semaine. Les races de Retail ne sont pas prévues, et les pierres de rencontre ne sont pas souhaitées, car les téléportations rapides rétrécissent le monde.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Classes** : les talents et les rotations que tu connais de Classic restent la base, pas de refonte à la Retail.",
                    "**Respec** : prévois de l'or, le coût augmente rapidement et retombe une fois par semaine. Choisis ton build avant de payer.",
                    "**Races** : seules les races du lore d'origine, pas de races Retail.",
                    "**Voyage** : pas de pierres de rencontre, ce qui garde son identité de classe au Démoniste.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Calculateur de talents", "wow-forever/talents/"),
                ("FAQ WoW Forever", "wow-forever/faq/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Classes Not Modernized, Pricey Respec",
            "description": "Blizzard interview on WoW Forever: Classic classes kept, rising respec price, no Retail races, no Summoning Stones.",
            "h1": "WoW Forever: Blizzard will not modernize the classes",
            "lede": "In a series of interviews with TechRadar, Blizzard lays out its vision for **WoW Forever**. The **Classic classes** will not be overhauled: they should stay simple but with real depth, and the original combat pacing is kept. Respeccing will not be cheap: the price climbs quickly and resets once a week. Retail races are not planned, and Summoning Stones are not wanted because quick teleports shrink the world.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Classes**: the Classic talents and rotations you know remain the base, no Retail-style overhaul.",
                    "**Respec**: bring gold, the cost rises fast and drops back once a week. Settle on your build before paying.",
                    "**Races**: only the original lore races, no Retail races.",
                    "**Travel**: no Summoning Stones, which keeps part of the Warlock class identity.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Talent calculator", "wow-forever/talents/"),
                ("WoW Forever FAQ", "wow-forever/faq/"),
            ],
        },
    },
    {
        "slug": "interview-jackediq-chaman-tank-collections-wow-forever",
        "format": "brief",
        "date": "2026-10-13",
        "updated": "2026-10-13",
        "draft": False,
        "tag": "dev",
        "kind": None,
        "class": "shaman",
        "image": "assets/img/spec/shaman-enhancement.png",
        "sources": [
            ("Wowhead : Shaman Tanks, Collections and Zones - JackedIQ Interview on WoW: Forever (13 Oct. 2026)",
             "https://www.wowhead.com/news=383381/shaman-tanks-collections-and-zones-jackediq-interview-on-wow-forever"),
        ],
        "fr": {
            "title": "WoW Forever : chaman tank, collections et zones",
            "description": "Interview de Blizzard par JackedIQ : chaman tank discuté mais pas prévu, collections cachées, objets qui changent le style de jeu, nouvelles zones.",
            "h1": "WoW Forever : ce que Blizzard dit du chaman tank et des zones",
            "lede": "Lors d'une interview menée par JackedIQ, des développeurs de **WoW Forever** ont abordé plusieurs sujets chers à la communauté. Le **chaman tank** est beaucoup discuté dans l'équipe, mais ce n'est pas un projet officiel pour l'instant. Le menu des **collections** n'affichera que ce que tu as déjà trouvé, pour garder les secrets du monde. Certains objets cachés, comme une épée qui fait du mage un combattant plus proche du corps à corps, pourraient changer ton style de jeu après la sortie. Côté **nouvelles zones**, rien n'est exclu (Norfendre, Pandarie), mais l'équipe se concentre d'abord sur la meilleure histoire à raconter.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Chaman** : ne compte pas sur un rôle de tank au lancement, il n'est pas officiellement prévu.",
                    "**Collections** : explore, tu ne verras une entrée qu'une fois l'objet obtenu.",
                    "**Objets cachés** : d'autres objets qui modifient ton style de jeu pourraient apparaître après la sortie.",
                    "**Zones** : pas d'annonce de nouveau continent, rien n'est exclu à long terme.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Talents du chaman", "wow-forever/talents/shaman/"),
                ("Date de sortie et éditions", "wow-forever/sortie/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Shaman Tanks, Collections, Zones",
            "description": "Blizzard on JackedIQ's interview: Shaman tanks discussed but not planned, hidden collections, playstyle items, possible new zones.",
            "h1": "WoW Forever: what Blizzard says about Shaman tanks and zones",
            "lede": "In an interview led by JackedIQ, **WoW Forever** developers covered several community favorites. **Shaman tanks** are a popular topic inside the team, but not something officially being pursued for now. The **collections** menu will only show what you have already found, to keep the world's secrets. Some hidden items, like a sword that turns Mages into more of a battle-mage, may change how you play after launch. On **new zones**, nothing is off the table (Northrend, Pandaria), but the team is first asking what the best story to tell is.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Shaman**: do not count on a tank role at launch, it is not officially planned.",
                    "**Collections**: explore, an entry appears only once you have the item.",
                    "**Hidden items**: more playstyle-changing items may turn up after release.",
                    "**Zones**: no new continent announced, nothing ruled out long term.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Shaman talents", "wow-forever/talents/shaman/"),
                ("Release date and editions", "wow-forever/sortie/"),
            ],
        },
    },
    {
        "slug": "double-specialisation-niveau-40-wow-forever",
        "format": "brief",
        "date": "2026-10-13",
        "updated": "2026-10-13",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/ability_dualwield.jpg",
        "sources": [
            ("Wowhead : Blizzard Teases Possible Change to Unlock Level of Dual Spec in WoW: Forever (10 Oct. 2026)",
             "https://www.wowhead.com/news=383320/blizzard-teases-possible-change-to-unlock-level-of-dual-spec-in-wow-forever"),
        ],
        "fr": {
            "title": "WoW Forever : double spécialisation plus tôt ?",
            "description": "Blizzard réfléchit à débloquer la double spécialisation de WoW Forever avant le niveau 40, peut-être au niveau 30. Rien n'est décidé.",
            "h1": "WoW Forever : la double spécialisation pourrait arriver plus tôt",
            "lede": "Dans le troisième épisode du podcast officiel de **WoW Forever**, un développeur a expliqué que la **double spécialisation** se débloque pour l'instant au **niveau 40**. L'équipe se demande quel est le bon niveau et a évoqué, sur le ton de la plaisanterie, un déblocage au **niveau 30**. Rien n'est confirmé : c'est une piste de discussion, pas un changement de la bêta. L'idée vient d'un débat sur les tanks : avec un déblocage plus tôt, on pourrait garder une build dédiée aux donjons sans changer de talents à chaque fois.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Aujourd'hui** : la double spécialisation arrive au niveau 40, donc après les premiers donjons.",
                    "**Piste évoquée** : le niveau 30, mais **rien n'est décidé**.",
                    "**Pour les tanks et les soigneurs** : une build de donjon séparée de la build de quête serait disponible plus tôt.",
                    "**À faire** : prépare tes deux builds avec le calculateur de talents en attendant la décision.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Calculateur de talents", "wow-forever/talents/"),
                ("Donjons par niveau", "wow-forever/dungeons/"),
                ("Bêta de WoW Forever", "wow-forever/beta/"),
                ("FAQ WoW Forever", "wow-forever/faq/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Dual Spec Unlocking Earlier?",
            "description": "Blizzard is considering unlocking dual spec in WoW Forever before level 40, possibly at level 30. Nothing is decided yet.",
            "h1": "WoW Forever: dual spec could unlock earlier",
            "lede": "In episode 3 of the official **WoW Forever** podcast, a developer explained that **dual spec** currently unlocks at **level 40**. The team is discussing what the right level is and jokingly floated **level 30**. Nothing is confirmed: it is a talking point, not a beta change. The idea came up in a talk about tanks: with an earlier unlock, you could keep a dedicated dungeon build without respeccing every time.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Today**: dual spec unlocks at level 40, after the first dungeons.",
                    "**Idea floated**: level 30, but **nothing is decided**.",
                    "**For tanks and healers**: a dungeon build separate from the questing build would be available sooner.",
                    "**To do**: plan your two builds with the talent calculator while waiting.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Talent calculator", "wow-forever/talents/"),
                ("Dungeons by level", "wow-forever/dungeons/"),
                ("WoW Forever beta", "wow-forever/beta/"),
                ("WoW Forever FAQ", "wow-forever/faq/"),
            ],
        },
    },
    {
        "slug": "pelle-fossoyeur-mousse-des-tombes-wow-forever",
        "format": "brief",
        "date": "2026-10-13",
        "updated": "2026-10-13",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/trade_herbalism.jpg",
        "sources": [
            ("Wowhead : New Item Makes Gravemoss Farming Easier in WoW: Forever (12 Oct. 2026)",
             "https://www.wowhead.com/news=383371/new-item-makes-gravemoss-farming-easier-in-wow-forever"),
        ],
        "fr": {
            "title": "WoW Forever : farmer la Mousse des tombes",
            "description": "Dans la bêta de WoW Forever, la Graverobber's Shovel permet de déterrer de la Mousse des tombes dans les cimetières.",
            "h1": "WoW Forever : la Graverobber's Shovel pour farmer la Mousse des tombes",
            "lede": "La bêta de **WoW Forever** ajoute des armes aux effets uniques, dont la **Graverobber's Shovel**. Un joueur l'a utilisée dans les cimetières de Raven Hill (Bois de la Pénombre) et du Monastère écarlate : en dépensant ses **20 charges**, il a fait apparaître plusieurs goules de niveau 30 qui donnent de l'expérience sans rien lâcher, et il a obtenu **9 Mousses des tombes**. C'est un seul essai rapporté par un joueur, donc le rendement moyen reste à confirmer. Cette herbe sert en alchimie, par exemple pour les potions de protection contre l'Ombre, utiles contre certains boss de raid.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Nouveau moyen de farmer** : creuser les tombes d'un cimetière plutôt que chercher l'herbe sur la carte.",
                    "**Attention** : chaque utilisation fait apparaître des goules de **niveau 30**, prévois de quoi les affronter.",
                    "**Alchimie** : la Mousse des tombes sert aux potions de protection contre l'Ombre, utiles en raid.",
                    "**Résultat à confirmer** : 9 herbes pour 20 charges, d'après un seul retour de joueur.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Guide de l'alchimie", "wow-forever/professions/alchemy/"),
                ("Toutes les professions", "wow-forever/professions/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Farming Grave Moss Faster",
            "description": "In the WoW Forever beta, the Graverobber's Shovel lets you dig up Grave Moss in graveyards. One player got 9 from 20 charges.",
            "h1": "WoW Forever: the Graverobber's Shovel for farming Grave Moss",
            "lede": "The **WoW Forever** beta adds weapons with unique effects, including the **Graverobber's Shovel**. One player used it in the Raven Hill Cemetery (Duskwood) and Scarlet Monastery graveyards: spending all **20 charges** spawned several level 30 ghouls that give experience but drop nothing, and yielded **9 Grave Moss**. That is a single run reported by one player, so the average yield is still to be confirmed. The herb is used in Alchemy, for example for Shadow Protection Potions, which help against some raid bosses.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**A new way to farm**: dig up graves in a cemetery instead of searching the map for the herb.",
                    "**Careful**: each use spawns **level 30** ghouls, so be ready to fight them.",
                    "**Alchemy**: Grave Moss goes into Shadow Protection Potions, useful in raids.",
                    "**To be confirmed**: 9 herbs for 20 charges, from one player report.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Alchemy guide", "wow-forever/professions/alchemy/"),
                ("All professions", "wow-forever/professions/"),
            ],
        },
    },
    {
        "slug": "test-de-charge-reporte-21-octobre-wow-forever",
        "format": "brief",
        "date": "2026-10-20",
        "updated": "2026-10-20",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_groupneedmore.jpg",
        "sources": [
            ("Wowhead : Blizzard Moves WoW: Forever Stress Test to October 21 (16 Oct. 2026)",
             "https://www.wowhead.com/news=383474/blizzard-moves-wow-forever-stress-test-to-october-21"),
        ],
        "fr": {
            "title": "WoW Forever : test de charge reporté au 21 octobre",
            "description": "Le test de charge ouvert à tous de WoW Forever n'a pas lieu le 19 octobre mais le 21 octobre. Ce que ça change pour toi.",
            "h1": "WoW Forever : le test de charge est reporté au 21 octobre",
            "lede": "Blizzard corrige la date du **test de charge de WoW Forever** : il aura lieu le **21 octobre** et non le 19 octobre comme annoncé d'abord, soit deux jours plus tard. Le test reste ouvert à tous, sans clé de bêta, sans abonnement et sans invitation. Si tu avais prévu de te connecter le 19, il faut décaler ton créneau.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Nouvelle date** : le 21 octobre, pas le 19. Les anciennes annonces qui parlent du 19 octobre sont dépassées.",
                    "**Même principe** : ouvert à tous, aucun abonnement ni clé de bêta requis.",
                    "**Avant de te connecter** : installe la version de test depuis Battle.net et mets tes pilotes graphiques à jour.",
                    "Le **lancement mondial** reste annoncé pour le 4 novembre.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Test de charge : mode d'emploi", "wow-forever/actualites/test-de-charge-19-octobre-wow-forever/"),
                ("Date de sortie de WoW Forever", "wow-forever/sortie/"),
                ("Tout sur la bêta", "wow-forever/beta/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Stress Test Moved to October 21",
            "description": "The open WoW Forever stress test is on October 21, not October 19. What the new date means for you.",
            "h1": "WoW Forever: the stress test is moved to October 21",
            "lede": "Blizzard has corrected the date of the **WoW Forever stress test**: it will take place on **October 21**, not on October 19 as first announced, so two days later. The test stays open to everyone, with no beta key, no subscription and no invitation. If you had planned to log in on the 19th, move your slot.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**New date**: October 21, not the 19th. Older posts that mention October 19 are out of date.",
                    "**Same idea**: open to all, no subscription or beta key needed.",
                    "**Before you log in**: install the test version from Battle.net and update your graphics drivers.",
                    "The **worldwide launch** is still announced for November 4.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Stress test: how to join", "wow-forever/actualites/test-de-charge-19-octobre-wow-forever/"),
                ("WoW Forever release date", "wow-forever/sortie/"),
                ("Everything about the beta", "wow-forever/beta/"),
            ],
        },
    },
    {
        "slug": "riverglades-hyjal-apres-niveau-30-wow-forever",
        "format": "brief",
        "date": "2026-10-20",
        "updated": "2026-10-20",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_map_01.jpg",
        "sources": [
            ("Wowhead : The Journey Past Level 30 in WoW: Forever - The Riverglades and Hyjal Zones (19 Oct. 2026)",
             "https://www.wowhead.com/news=383495/the-journey-past-level-30-in-wow-forever-the-riverglades-and-hyjal-zones"),
        ],
        "fr": {
            "title": "WoW Forever : Riverglades et Hyjal après le niveau 30",
            "description": "Blizzard présente les zones de leveling après le niveau 30 de WoW Forever : Riverglades, Mont Hyjal et le raid à 10 Barrow Deeps.",
            "h1": "WoW Forever : ce qui t'attend après le niveau 30 (Riverglades, Hyjal)",
            "lede": "La bêta de **WoW Forever** s'arrête au niveau 30, mais Blizzard dévoile dans une vidéo la suite du leveling jusqu'au 60 avec deux nouvelles zones. **Riverglades** reprend des factions du passé de Warcraft : l'Alliance y croise la Brotherhood of the Horse, des chevaliers de Hurlevent, et la Horde les ogres Boulderrock, anciens du Marteau du Crépuscule, avec une arène de combat au cœur de leur territoire. **Mont Hyjal** conclut le leveling, avec une route rouverte pour la première fois depuis la Troisième Guerre et un raid à **10 joueurs, Barrow Deeps**.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Deux zones à prévoir** pour la fin du leveling : Riverglades, puis **Hyjal** comme point d'orgue.",
                    "**Hyjal** met Horde et Alliance au même endroit, aux côtés des Druides du Talon et du Cercle cénarien : les tensions remontent.",
                    "**Nouveau raid à 10** : Barrow Deeps, une prison dans Hyjal, à ajouter à ton suivi de progression.",
                    "Rien de tout cela n'est jouable dans la bêta actuelle, plafonnée au **niveau 30**.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Guide de leveling", "wow-forever/leveling/"),
                ("Raids de WoW Forever", "wow-forever/raids/"),
                ("Progression par niveau", "wow-forever/progression/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Riverglades and Hyjal Past Level 30",
            "description": "Blizzard previews the post-level-30 leveling zones of WoW Forever: Riverglades, Mount Hyjal and the 10-player raid Barrow Deeps.",
            "h1": "WoW Forever: what waits for you past level 30 (Riverglades, Hyjal)",
            "lede": "The **WoW Forever** beta stops at level 30, but Blizzard has shown in a video what comes next on the way to 60, with two new zones. **Riverglades** builds on factions from Warcraft's past: the Alliance meets the Brotherhood of the Horse, knights from Stormwind, while the Horde meets the Boulderrock ogres, former Twilight Hammer members, with a fighting ring deep in their territory. **Mount Hyjal** closes the leveling journey, with a road reopened for the first time since the Third War and a **10-player raid, Barrow Deeps**.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Two zones to plan for** at the end of leveling: Riverglades, then **Hyjal** as the finale.",
                    "**Hyjal** puts Horde and Alliance side by side, with the Druids of the Talon and the Cenarion Circle: tensions are rising again.",
                    "**New 10-player raid**: Barrow Deeps, a prison in Hyjal, to add to your progression plans.",
                    "None of this is playable in the current beta, which is capped at **level 30**.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Leveling guide", "wow-forever/leveling/"),
                ("WoW Forever raids", "wow-forever/raids/"),
                ("Progression by level", "wow-forever/progression/"),
            ],
        },
    },
    {
        "slug": "groupes-premade-champs-de-bataille-wow-forever",
        "format": "brief",
        "date": "2026-10-20",
        "updated": "2026-10-20",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_bannerpvp_01.jpg",
        "sources": [
            ("Wowhead : Premade Groups Will Only Match Against Other Premades in WoW: Forever Battlegrounds (18 Oct. 2026)",
             "https://www.wowhead.com/news=383436/premade-groups-will-only-match-against-other-premades-in-wow-forever-battlegrounds"),
        ],
        "fr": {
            "title": "WoW Forever : les premades jouent entre eux en BG",
            "description": "WoW Forever : un joueur solo en champ de bataille ne tombera pas contre un groupe premade. Ce qu'a dit Blizzard et ce qui reste flou.",
            "h1": "WoW Forever : en champ de bataille, les premades affrontent les premades",
            "lede": "Blizzard a indiqué dans le dernier podcast de **WoW Forever** que si tu t'inscris **seul** en champ de bataille, tu ne seras pas confronté à un groupe premade. Les groupes constitués ne seront opposés qu'à d'autres groupes constitués. Pour les petits groupes d'amis, une option dédiée est prévue, probablement pour **2 à 3 joueurs**, mais ce chiffre n'est pas arrêté. On ne sait pas encore si la règle sera assouplie après une longue attente en file, comme lors de la phase 2 de Season of Discovery.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**En solo** : plus de risque de tomber contre un groupe organisé en champ de bataille.",
                    "**En groupe constitué** : tu affronteras d'autres premades, donc des parties plus disputées.",
                    "**Avec 2 ou 3 amis** : une file pour petits groupes est prévue, la taille exacte reste à confirmer.",
                    "**À surveiller** : l'attente en file pourrait être plus longue, et une exception après un certain temps n'est pas exclue.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Honneur et rangs PvP", "wow-forever/actualites/progression-pvp-honneur-rangs-wow-forever/"),
                ("Champ de bataille des îles Darkspear", "wow-forever/actualites/champ-de-bataille-iles-darkspear-wow-forever/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Premades Only Face Premades in BGs",
            "description": "WoW Forever: a solo queuer will not be matched against a premade group in battlegrounds. What Blizzard said and what is still unclear.",
            "h1": "WoW Forever: in battlegrounds, premades face premades",
            "lede": "Blizzard said on the latest **WoW Forever** podcast that if you queue for a battleground **solo**, you will not be matched against a premade group. Premade groups will only be matched against other premade groups. A dedicated option for small groups of friends is planned, probably for **2 to 3 players**, but that number is not final. It is not known yet whether the rule will be relaxed after a long wait in queue, as it was in Season of Discovery phase 2.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Solo**: no more risk of facing an organized group in a battleground.",
                    "**In a premade**: you will face other premades, so tougher matches.",
                    "**With 2 or 3 friends**: a small-group queue is planned, exact size still to be confirmed.",
                    "**Keep an eye on**: queue times may be longer, and an exception after some waiting is not ruled out.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Honor and PvP ranks", "wow-forever/actualites/progression-pvp-honneur-rangs-wow-forever/"),
                ("Battle for the Darkspear Islands", "wow-forever/actualites/champ-de-bataille-iles-darkspear-wow-forever/"),
            ],
        },
    },
    {
        "slug": "molten-core-nouvelles-mecaniques-wow-forever",
        "format": "brief",
        "date": "2026-10-23",
        "updated": "2026-10-23",
        "draft": False,
        "tag": "dev",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_hammer_unique_sulfuras.jpg",
        "sources": [
            ("Wowhead : Blizzard Confirms Molten Core Will Have New Mechanics in WoW: Forever (22 Oct. 2026)",
             "https://www.wowhead.com/news=383543/blizzard-confirms-molten-core-will-have-new-mechanics-in-wow-forever"),
        ],
        "fr": {
            "title": "WoW Forever : Molten Core aura de nouvelles mécaniques",
            "description": "WoW Forever : Blizzard confirme que Molten Core ne sera pas une copie de Classic, avec de nouvelles mécaniques. Ce qu'on sait et ce qu'on ignore.",
            "h1": "WoW Forever : Molten Core aura de nouvelles mécaniques",
            "lede": "Dans le dernier podcast de **WoW Forever**, le game designer Josh Greenfield a confirmé que **Molten Core** ne sera pas une simple reprise du raid de 2004 ou de Classic. Blizzard veut éviter le contraste entre les nouveaux raids de Hyjal et un Molten Core que tout le monde connaît déjà par cœur. Il a cité Golemagg comme exemple : on ne le tankera plus simplement en restant immobile. Les mécaniques exactes ne sont pas encore connues.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Molten Core** : prévois de redécouvrir les combats au lieu de rejouer des stratégies apprises par cœur.",
                    "**Golemagg** : cité en exemple, son combat devrait demander plus qu'un simple tank and spank.",
                    "**À savoir** : Blizzard parle de raid « revampé » ou « réimaginé », sans détail pour l'instant.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Molten Core", "wow-forever/raids/molten-core/"),
                ("Tous les raids de WoW Forever", "wow-forever/raids/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Molten Core Gets New Mechanics",
            "description": "WoW Forever: Blizzard confirms Molten Core will not be a Classic copy and will have new mechanics. What we know and what is still unknown.",
            "h1": "WoW Forever: Molten Core will have new mechanics",
            "lede": "On the latest **WoW Forever** podcast, game designer Josh Greenfield confirmed that **Molten Core** will not be a simple rerun of the 2004 or Classic raid. Blizzard wants to avoid the gap between the new Hyjal raids and a Molten Core everyone already knows by heart. He named Golemagg as an example: you will no longer just stand still and tank him. The exact mechanics are not known yet.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Molten Core**: expect to rediscover the fights instead of replaying memorized strategies.",
                    "**Golemagg**: named as an example, his fight should ask for more than plain tank and spank.",
                    "**Good to know**: Blizzard talks of a \"revamped\" or \"reimagined\" raid, with no detail so far.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Molten Core", "wow-forever/raids/molten-core/"),
                ("All WoW Forever raids", "wow-forever/raids/"),
            ],
        },
    },
    {
        "slug": "ruleset-rp-pvp-lancement-4-novembre-wow-forever",
        "format": "brief",
        "date": "2026-10-23",
        "updated": "2026-10-23",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_book_09.jpg",
        "sources": [
            ("Wowhead : RP-PvP Ruleset Coming to WoW: Forever (22 Oct. 2026)",
             "https://www.wowhead.com/news=383537/rp-pvp-ruleset-coming-to-wow-forever"),
        ],
        "fr": {
            "title": "WoW Forever : un ruleset RP-PvP au lancement du 4 nov.",
            "description": "WoW Forever : Blizzard ajoute finalement un ruleset Roleplay-PvP pour le lancement du 4 novembre, avec réservation des noms dès le 27 octobre.",
            "h1": "WoW Forever : le ruleset Roleplay-PvP sera disponible au lancement",
            "lede": "Blizzard avait exprimé des réserves sur un ruleset **Roleplay-PvP** dans **WoW Forever**, puis a changé d'avis après avoir étudié ce que cela demandait. Le ruleset sera bien présent **au lancement, le 4 novembre**. L'équipe travaille à ce qu'on puisse le choisir et y réserver ses noms dès l'ouverture de la période de réservation, le **mardi 27 octobre**.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Lancement** : le ruleset Roleplay-PvP sera là dès le **4 novembre**, comme les autres.",
                    "**Noms** : tu pourras viser ce ruleset pendant la réservation qui débute le **27 octobre**.",
                    "**À confirmer** : Blizzard dit « travailler dur » pour que le choix soit possible dès l'ouverture.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Date et heure de sortie", "wow-forever/sortie/"),
                ("FAQ WoW Forever", "wow-forever/faq/"),
            ],
        },
        "en": {
            "title": "WoW Forever: RP-PvP Ruleset at the Nov. 4 Launch",
            "description": "WoW Forever: Blizzard is adding a Roleplay-PvP ruleset for the November 4 launch, with name reservation starting October 27.",
            "h1": "WoW Forever: the Roleplay-PvP ruleset will be available at launch",
            "lede": "Blizzard had voiced concerns about a **Roleplay-PvP** ruleset in **WoW Forever**, then changed course after studying what it would take. The ruleset will be there **at launch, on November 4**. The team is working so you can pick it and reserve names on it when the reservation period opens on **Tuesday, October 27**.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Launch**: the Roleplay-PvP ruleset will be live on **November 4**, like the others.",
                    "**Names**: you should be able to target this ruleset during the reservation starting **October 27**.",
                    "**To confirm**: Blizzard says it is \"working hard\" to make the choice available from the start.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Release date and time", "wow-forever/sortie/"),
                ("WoW Forever FAQ", "wow-forever/faq/"),
            ],
        },
    },
    {
        "slug": "reservation-noms-personnages-27-octobre-wow-forever",
        "format": "brief",
        "date": "2026-10-23",
        "updated": "2026-10-23",
        "draft": False,
        "tag": "release",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_note_01.jpg",
        "sources": [
            ("Wowhead : How to Reserve Your World of Warcraft: Forever Character Name on October 27th (20 Oct. 2026)",
             "https://www.wowhead.com/news=383515/how-to-reserve-your-world-of-warcraft-forever-character-name-on-october-27th"),
        ],
        "fr": {
            "title": "WoW Forever : réserver ton nom le 27 octobre, mode d'emploi",
            "description": "WoW Forever : réservation anticipée des noms du 27 octobre au 3 novembre, horaires par région, 3 personnages maximum et conditions d'accès.",
            "h1": "WoW Forever : comment réserver le nom de ton personnage le 27 octobre",
            "lede": "La **réservation anticipée des noms** de **WoW Forever** se déroule du **27 octobre au 3 novembre**. Elle ouvre le 27 octobre à **18h00 (heure de Paris)** en Europe, et à 13h00 PDT en Amérique du Nord. Chaque joueur éligible peut réserver jusqu'à **trois personnages au total**, tous rulesets confondus. Les noms sont attribués au premier arrivé, sans garantie d'obtenir celui que tu veux.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Horaire Europe** : ouverture le **27 octobre à 18h00 (CET)**, fin le 3 novembre.",
                    "**Limite** : **3 personnages** en tout. Deux sur un ruleset PvP, et il n'en reste qu'un pour les autres.",
                    "**Accès** : réservé aux comptes ayant précommandé l'édition numérique, la Collector ou l'un des packs Skyborne.",
                    "**Préparation** : installe WoW: Forever depuis l'appli Battle.net avant l'ouverture.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Date et heure de sortie", "wow-forever/sortie/"),
                ("Éditions de WoW Forever", "wow-forever/editions/"),
                ("FAQ WoW Forever", "wow-forever/faq/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Reserve Your Name on October 27 (Guide)",
            "description": "WoW Forever: early name reservation runs October 27 to November 3, with start times by region, a 3-character cap and who can take part.",
            "h1": "WoW Forever: how to reserve your character name on October 27",
            "lede": "**Early name reservation** for **WoW Forever** runs from **October 27 to November 3**. It opens on October 27 at **18:00 CET** in Europe and 13:00 PDT in North America. Each eligible player can reserve up to **three characters in total**, across all rulesets. Names are first come, first served, with no guarantee of getting the one you want.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Europe start time**: opens **October 27 at 18:00 CET**, ends November 3.",
                    "**Limit**: **3 characters** in total. Two on a PvP ruleset leaves only one for the others.",
                    "**Access**: for accounts that pre-purchased the Digital Upgrade, the Collector's Edition or a Skyborne pack.",
                    "**Preparation**: install WoW: Forever from the Battle.net app before it opens.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Release date and time", "wow-forever/sortie/"),
                ("WoW Forever editions", "wow-forever/editions/"),
                ("WoW Forever FAQ", "wow-forever/faq/"),
            ],
        },
    },
    {
        "slug": "paladin-sans-armure-mailles-puissance-sorts-wow-forever",
        "format": "brief",
        "date": "2026-10-23",
        "updated": "2026-10-23",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": "paladin",
        "image": "assets/img/spec/paladin-protection.png",
        "sources": [
            ("Wowhead : No Mail Spell Power Dungeon and Quest Armor in WoW: Forever Early Levels (22 Oct. 2026)",
             "https://www.wowhead.com/news=383520/no-mail-spell-power-dungeon-and-quest-armor-in-wow-forever-early-levels"),
        ],
        "fr": {
            "title": "Paladin WoW Forever : pas de mailles à puissance des sorts",
            "description": "WoW Forever, niveaux 1-30 : la bêta ne montre aucune maille à puissance des sorts en donjon ou quête. Seul le Paladin est touché, à vérifier.",
            "h1": "Paladin dans WoW Forever : pas de mailles à puissance des sorts avant le niveau 30",
            "lede": "D'après la base de données de Wowhead sur la bêta de **WoW Forever**, aucune pièce de **maille à puissance des sorts** n'apparaît dans les donjons ni les quêtes entre les niveaux 1 et 30. Seuls des objets verts aléatoires avec un suffixe comme « of Magic » tombent, et deux récompenses de quête, orientées soins. Cela ne touche que le **Paladin**. Ce n'est pas une preuve définitive : les joueurs n'ont simplement rien trouvé pour l'instant, et Blizzard peut encore corriger.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Paladin Sacré** : pour équiper de la maille de soins avant le niveau 30, il faudra surtout **fabriquer** ou passer par l'hôtel des ventes.",
                    "**Quêtes** : seuls les **Garrison Cuffs** et les **Silvered Gauntlets** sont aujourd'hui des mailles à effet de soins.",
                    "**Artisanat** : les patrons viennent de donjons ou des remises de Merchant's Favor.",
                    "**À surveiller** : Blizzard peut ajouter ces objets avant le lancement.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Guide Paladin Sacré", "wow-forever/guides/paladin/holy/"),
                ("Guide Paladin Protection", "wow-forever/guides/paladin/protection/"),
                ("Métiers de WoW Forever", "wow-forever/professions/"),
            ],
        },
        "en": {
            "title": "Paladin in WoW Forever: No Spell Power Mail Early On",
            "description": "WoW Forever levels 1-30: the beta shows no spell power mail from dungeons or quests. Only the Paladin is affected, and it may still change.",
            "h1": "Paladin in WoW Forever: no spell power mail before level 30",
            "lede": "According to Wowhead's database for the **WoW Forever** beta, no piece of **spell power mail** drops from dungeons or quests between levels 1 and 30. Only random green items with a suffix such as \"of Magic\" drop, plus two quest rewards aimed at healing. This affects only the **Paladin**. It is not definitive proof: players simply have not found any so far, and Blizzard may still fix it.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Holy Paladin**: to wear healing mail before level 30, you will mostly need to **craft** it or buy it on the auction house.",
                    "**Quests**: only the **Garrison Cuffs** and **Silvered Gauntlets** are healing-oriented mail today.",
                    "**Crafting**: patterns come from dungeons or Merchant's Favor turn-ins.",
                    "**Keep an eye on**: Blizzard may add these items before launch.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Holy Paladin guide", "wow-forever/guides/paladin/holy/"),
                ("Protection Paladin guide", "wow-forever/guides/paladin/protection/"),
                ("WoW Forever professions", "wow-forever/professions/"),
            ],
        },
    },
    {
        "slug": "feux-de-camp-metiers-bonus-wow-forever",
        "format": "brief",
        "date": "2026-10-23",
        "updated": "2026-10-23",
        "draft": False,
        "tag": "news",
        "kind": None,
        "class": None,
        "image": "https://wow.zamimg.com/images/wow/icons/large/spell_fire_fire.jpg",
        "sources": [
            ("Wowhead : Camping System Breakdown in World of Warcraft: Forever (21 Oct. 2026)",
             "https://www.wowhead.com/news=383522/camping-system-breakdown-in-world-of-warcraft-forever"),
        ],
        "fr": {
            "title": "WoW Forever : feux de camp et bonus de métiers expliqués",
            "description": "WoW Forever : le système de camping donne des bonus de stats selon les métiers autour d'un feu de camp. Fonctionnement, niveaux requis et exclusivités.",
            "h1": "WoW Forever : le système de camping et les bonus de chaque métier",
            "lede": "Blizzard a détaillé le **système de camping** de **WoW Forever**. Le feu de cuisine devient un **feu de camp de base** qui accepte jusqu'à **trois objets** posés par des joueurs proches, un par joueur. Chaque métier apporte un bonus, par exemple de la Force avec la Forge ou de l'Intelligence avec l'Herboristerie. Ces effets sont des variantes de buffs de classe et ne se cumulent pas avec eux. Il faut rester assis ou crafter au moins **1 minute** près du feu pour en profiter.",
            "body": [
                ("h2", "Ce que ça change pour toi"),
                ("list", [
                    "**Niveau requis** : les premiers objets de camp arrivent au niveau **20** du métier, les suivants à partir de 140 via donjons et raids.",
                    "**Exclusivité** : le bonus remplace celui de la classe équivalente, par exemple l'Intelligence de l'Herboristerie et Arcane Intellect.",
                    "**Délai** : toutes les fonctions de camp partagent un **délai de 1 heure**.",
                    "**Cuisine** : les cuisiniers débloqueront des feux plus grands, de 5 à 10 objets.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Cuisine dans WoW Forever", "wow-forever/professions/cooking/"),
                ("Tous les métiers", "wow-forever/professions/"),
            ],
        },
        "en": {
            "title": "WoW Forever: Campfires and Profession Buffs Explained",
            "description": "WoW Forever: the camping system gives stat buffs from professions around a campfire. How it works, required skill levels and exclusivity.",
            "h1": "WoW Forever: the camping system and each profession's buff",
            "lede": "Blizzard has detailed the **camping system** in **WoW Forever**. The cooking fire becomes a **Basic Campfire** that holds up to **three objects** placed by nearby players, one each. Each profession adds a buff, such as Strength from Blacksmithing or Intellect from Herbalism. These effects are variants of class buffs and do not stack with them. You need to sit or craft for at least **1 minute** near the fire to benefit.",
            "body": [
                ("h2", "What it means for you"),
                ("list", [
                    "**Skill needed**: the first camp items arrive at profession skill **20**, later ones from 140 via dungeons and raids.",
                    "**Exclusivity**: the buff replaces the matching class buff, for example Herbalism's Intellect and Arcane Intellect.",
                    "**Cooldown**: all camp features share a **1-hour cooldown**.",
                    "**Cooking**: cooks will unlock bigger fires holding 5 to 10 objects.",
                ]),
            ],
            "faq": [],
            "links": [
                ("Cooking in WoW Forever", "wow-forever/professions/cooking/"),
                ("All professions", "wow-forever/professions/"),
            ],
        },
    },
]

from wow_article_launch import LAUNCH_ARTICLE  # noqa: E402  (launch-day guide, kept in its own file)
ARTICLES.insert(0, LAUNCH_ARTICLE)
from wow_articles_patch1015 import PATCH1015_ARTICLES  # noqa: E402  (full articles from the 15 Oct 2026 beta build)
ARTICLES[1:1] = PATCH1015_ARTICLES
from wow_articles_racials1027 import RACIALS_TUNING  # noqa: E402  (racial tuning pass of 26-27 Oct 2026, a draft until proof-read)
ARTICLES.insert(1, RACIALS_TUNING)
from wow_articles_hunter1028 import HUNTER_HOTFIX  # noqa: E402  (Hunter hotfixes seen on live servers, 28 Oct 2026)
ARTICLES.insert(1, HUNTER_HOTFIX)

KIND_LABEL = {"up": ("UP", "UP"), "nerf": ("NERF", "NERF"), "eq": ("ÉQUILIBRAGE", "BALANCE")}
FORMAT_LABEL = {"article": ("Analyse", "Analysis"), "brief": ("Brève", "Brief"), "guide": ("Guide", "Guide")}


def check():
    for a in ARTICLES:
        assert a.get("format", "article") in FORMAT_LABEL, a["slug"]
        assert a["kind"] in KIND_LABEL or (a.get("format") in ("brief", "guide") and a["kind"] is None), a["slug"]
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

