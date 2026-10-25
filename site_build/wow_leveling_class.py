"""'Which class levels fast?' (/wow-forever/leveling/meilleure-classe/, 2026-10-25, user decision: a page of its own, measured and opinion kept apart).
What we measure: the level-60 simulator's best DPS spec of each class (data/wow_ranking60.json), which says nothing about leveling speed, and the roles each class can play
(data/wow_guides/roles.json). What we do NOT measure: how fast a class levels. The page says so, and cites other sites' views with a link instead of making a ranking up.
No beta wording: the page needs no switch at the launch."""

# One fact per source, read on the page itself on 2026-10-25 (ConquestCapped: "Updated 22 Oct 2026").
SOURCES = [
    {"key": "cc", "name": "ConquestCapped", "url": "https://conquestcapped.com/guides/wow-forever/wow-forever-best-leveling-class/", "date": "2026-10-22"},
    {"key": "mob", "name": "Mobalytics", "url": "https://mobalytics.gg/wow-forever/tier-list", "date": None},
]

TX = {
    "fr": {
        "title": "Meilleure classe pour leveler dans WoW Forever",
        "desc": "Quelle classe pour leveler vite dans WoW Forever ? Ce que nous mesurons, ce qui est un avis, les rôles de chaque classe et les avis cités.",
        "kicker": "LEVELING", "h1": "Quelle classe pour leveler vite dans WoW: Forever ?",
        "intro": "C'est la question la plus posée avant le lancement. Nous ne mesurons pas la vitesse de leveling : notre simulateur mesure le niveau 60. Cette page sépare ce que nous savons de ce qui est un avis, et renvoie vers les avis des autres sites.",
        "chips": ["Pas de mesure de vitesse de leveling", "Niveau 60 : simulateur", "Avis cités avec leur lien", "Mis à jour le {date}"],
        "know_h": "Ce que nous mesurons, ce que nous ne mesurons pas",
        "know": [
            "<b>Mesuré</b> : le classement DPS de niveau 60 de notre simulateur (boss immobile, buffs de raid, meilleur équipement connu). Il dit quelle spécialisation fait le plus de dégâts au niveau 60 ; il ne dit rien de la vitesse à laquelle une classe monte de 1 à 60.",
            "<b>Connu</b> : les rôles que chaque classe peut jouer (tank, soigneur, DPS), lus dans les guides de spécialisation.",
            "<b>Pas mesuré</b> : le temps pour monter, les dégâts en combat de monde, la survie sur plusieurs monstres, la dépendance aux donjons. Nous n'avons ni partie jouée ni simulation de leveling, et nous n'inventons pas de classement.",
        ],
        "tbl_h": "Les neuf classes", "tbl_p": "Une ligne par classe : les rôles possibles et la meilleure spécialisation DPS du classement niveau 60. La dernière colonne n'est pas une mesure de leveling.",
        "col_cls": "Classe", "col_roles": "Rôles possibles", "col_best": "Meilleur DPS au niveau 60 (simulateur)", "col_lvl": "Leveling",
        "best_cell": "{spec} · {val} DPS · n°{pos}", "no_dps": "pas de spécialisation DPS simulée", "lvl_link": "Monter {cls} de 1 à 60",
        "views_h": "Les avis que nous citons", "views_p": "Ce sont les avis des autres sites, pas les nôtres. Les liens ouvrent leurs pages : lis-les avec ce que nous venons de dire des mesures.",
        "views": {"cc": "{name} (page mise à jour le {date}) classe le chasseur en tête (palier S) pour le leveling et le guerrier et le prêtre en bas (palier C).",
                  "mob": "{name} publie sa propre tier list de leveling par spécialisation."},
        "go_h": "Pour choisir", "go": [("Les guides de leveling par spécialisation", "wow-forever/leveling/#lvg-classes"), ("Quelle race choisir", "wow-forever/races/"), ("Tier list niveau 60", "wow-forever/tier-list/"), ("Donjons par niveau", "wow-forever/dungeons/")],
        "faq_h": "Questions fréquentes", "faq": [
            ("Quelle est la classe la plus rapide pour leveler dans WoW Forever ?", "Nous ne le savons pas : nous n'avons pas de mesure de la vitesse de leveling. Les autres sites donnent des avis, que nous citons sur cette page avec leur lien. Le classement de notre simulateur concerne le niveau 60."),
            ("Le classement niveau 60 donne-t-il la meilleure classe pour leveler ?", "Pas forcément : il mesure les dégâts d'une spécialisation équipée au niveau 60 sur un boss immobile, pas la vitesse à laquelle une classe tue des monstres en monde ouvert."),
            ("Ce classement changera-t-il après le lancement ?", "Les avis des autres sites sont susceptibles de changer avec le jeu sorti. Nous ne publions pas de classement de leveling tant que nous n'avons pas de mesure."),
        ],
        "src_h": "Sources et méthode", "src": ["Classement niveau 60 : simulateur de la page Classement (méthode affichée sur chaque page de spécialisation).", "Rôles : guides de spécialisation (data/wow_guides/roles.json).", "Avis : pages citées, lues le 25 octobre 2026."],
    },
    "en": {
        "title": "Best class to level in WoW Forever",
        "desc": "Which class levels fastest in WoW Forever? What we measure, what is an opinion, each class's roles and the views we cite.",
        "kicker": "LEVELING", "h1": "Which class levels fast in WoW: Forever?",
        "intro": "It is the most asked question before the launch. We do not measure leveling speed: our simulator measures level 60. This page keeps what we know apart from what is an opinion, and points to other sites' views.",
        "chips": ["No leveling speed measure", "Level 60: simulator", "Views cited with their link", "Updated {date}"],
        "know_h": "What we measure and what we do not",
        "know": [
            "<b>Measured</b>: our simulator's level-60 DPS ranking (stationary boss, raid buffs, best known gear). It says which specialization does the most damage at level 60; it says nothing about how fast a class goes from 1 to 60.",
            "<b>Known</b>: the roles each class can play (tank, healer, DPS), read from the specialization guides.",
            "<b>Not measured</b>: the time to level, open-world damage, survival against several monsters, dependence on dungeons. We have no played game and no leveling simulation, and we do not make up a ranking.",
        ],
        "tbl_h": "The nine classes", "tbl_p": "One row per class: the roles it can play and the best DPS specialization of the level-60 ranking. The last column is not a leveling measure.",
        "col_cls": "Class", "col_roles": "Possible roles", "col_best": "Best DPS at level 60 (simulator)", "col_lvl": "Leveling",
        "best_cell": "{spec} · {val} DPS · #{pos}", "no_dps": "no simulated DPS specialization", "lvl_link": "Leveling {cls} from 1 to 60",
        "views_h": "The views we cite", "views_p": "These are other sites' views, not ours. The links open their pages: read them with what we just said about measures.",
        "views": {"cc": "{name} (page updated {date}) ranks the hunter first (tier S) for leveling and the warrior and the priest last (tier C).",
                  "mob": "{name} publishes its own leveling tier list by specialization."},
        "go_h": "To choose", "go": [("Leveling guides by specialization", "wow-forever/leveling/#lvg-classes"), ("Which race to pick", "wow-forever/races/"), ("Level 60 tier list", "wow-forever/tier-list/"), ("Dungeons by level", "wow-forever/dungeons/")],
        "faq_h": "Frequently asked questions", "faq": [
            ("Which class levels fastest in WoW Forever?", "We do not know: we have no measure of leveling speed. Other sites give opinions, which we cite on this page with their link. Our simulator's ranking is about level 60."),
            ("Does the level-60 ranking give the best class to level?", "Not necessarily: it measures the damage of an equipped specialization at level 60 against a stationary boss, not how fast a class kills monsters in the open world."),
            ("Will this change after the launch?", "Other sites' views are likely to change with the released game. We publish no leveling ranking until we have a measure."),
        ],
        "src_h": "Sources and method", "src": ["Level-60 ranking: the simulator of the Ranking page (method shown on each specialization page).", "Roles: specialization guides (data/wow_guides/roles.json).", "Views: the cited pages, read on October 25, 2026."],
    },
}
