"""Leveling 1-60 guide (/wow-forever/leveling/).
Sources, by kind of data (the page says which is which):
  - dungeons and their level ranges: data/wow_dungeons/dungeons.json (client / Wowhead Forever); Hall of Thanes and Ruins of Lordaeron: Blizzard's beta announcement
  - professions: data/wow_professions/*.json (rank thresholds and costs read from the beta client tables)
  - zones: WoW Classic level ranges (Warcraft Wiki, "Zones by level (Classic)"): NOT confirmed for Forever, flagged as such on the page."""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
UPDATED = "2026-10-13"
BANDS = [(1, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60)]

# (English name, French name, first level, last level); Classic ranges. A zone sits in the band where its range starts.
ZONES = [
    ("Elwynn Forest", "Forêt d'Elwynn", 1, 10), ("Dun Morogh", "Dun Morogh", 1, 10), ("Teldrassil", "Teldrassil", 1, 10), ("Durotar", "Durotar", 1, 10),
    ("Mulgore", "Mulgore", 1, 10), ("Tirisfal Glades", "Clairières de Tirisfal", 1, 10),
    ("Darkshore", "Sombrivage", 10, 20), ("Loch Modan", "Loch Modan", 10, 20), ("Silverpine Forest", "Forêt des Pins argentés", 10, 20), ("Westfall", "Marche de l'Ouest", 10, 20),
    ("The Barrens", "Les Tarides", 10, 25), ("Redridge Mountains", "Les Carmines", 15, 25), ("Stonetalon Mountains", "Les Serres-Rocheuses", 15, 27),
    ("Ashenvale", "Orneval", 18, 30), ("Duskwood", "Bois de la Pénombre", 18, 30),
    ("Wetlands", "Les Paluns", 20, 30), ("Hillsbrad Foothills", "Contreforts de Hautebrande", 20, 35), ("Thousand Needles", "Mille pointes", 25, 35),
    ("Alterac Mountains", "Montagnes d'Alterac", 30, 40), ("Arathi Highlands", "Hautes-terres d'Arathi", 30, 40), ("Desolace", "Désolace", 30, 40), ("Stranglethorn Vale", "Vallée de Strangleronce", 30, 45),
    ("Dustwallow Marsh", "Marécage d'Âprefange", 35, 45), ("Badlands", "Terres ingrates", 35, 45), ("Swamp of Sorrows", "Marais des Chagrins", 35, 45),
    ("Feralas", "Féralas", 40, 50), ("The Hinterlands", "Les Hinterlands", 40, 50), ("Tanaris", "Tanaris", 40, 50), ("Searing Gorge", "Gorge des Vents brûlants", 45, 50),
    ("Azshara", "Azshara", 45, 55), ("Blasted Lands", "Terres foudroyées", 45, 55), ("Un'Goro Crater", "Cratère d'Un'Goro", 48, 55), ("Felwood", "Gangrebois", 48, 55),
    ("Burning Steppes", "Steppes ardentes", 50, 58), ("Western Plaguelands", "Maleterres de l'ouest", 51, 58), ("Eastern Plaguelands", "Maleterres de l'est", 53, 60),
    ("Winterspring", "Berceau-de-l'Hiver", 53, 60), ("Deadwind Pass", "Défilé de Deuillevent", 55, 60), ("Moonglade", "Reflet-de-Lune", 55, 60), ("Silithus", "Silithus", 55, 60),
]
# Dungeons without a range in the client data: levels announced by Blizzard for the beta week 1
EXTRA_LEVELS = {"hall-of-thanes": "13-18", "ruins-of-lordaeron": "15-20"}


def _band_of(lo):
    for i, (a, b) in enumerate(BANDS):
        if a <= lo < b or (i == len(BANDS) - 1 and lo >= a):
            return i
    return 0


def _gold(copper):
    g, s = divmod(int(round(copper)) // 100, 100)
    return g, s


def build(lang):
    L = 0 if lang == "fr" else 1
    n = lambda e, f: (f if lang == "fr" else e)
    bands = [{"lo": a, "hi": b, "zones": [], "dungeons": [], "ranks": []} for a, b in BANDS]
    for en, fr, lo, hi in ZONES:
        bands[_band_of(lo)]["zones"].append({"name": n(en, fr), "lo": lo, "hi": hi})
    dg = json.loads((PROJECT / "data" / "wow_dungeons" / "dungeons.json").read_text(encoding="utf-8"))["dungeons"]
    for d in dg:
        rng = d.get("levels") or EXTRA_LEVELS.get(d["id"])
        if not rng:
            continue
        lo, hi = (int(x) for x in rng.split("-"))
        bands[_band_of(lo)]["dungeons"].append({"id": d["id"], "name": d["name"][lang], "lo": lo, "hi": hi, "blizz": d["id"] in EXTRA_LEVELS, "path": f"wow-forever/dungeons/{d['id']}/"})
    for b in bands:
        b["dungeons"].sort(key=lambda x: (x["lo"], x["hi"]))
    profs = []
    for p in sorted((PROJECT / "data" / "wow_professions").glob("*.json"), key=lambda f: json.loads(f.read_text(encoding="utf-8"))["order"]):
        d = json.loads(p.read_text(encoding="utf-8"))
        ranks = {r["name"]: r for r in d["ranks"]}
        g, s = _gold(d["totals"]["all_copper"])
        profs.append({"id": d["id"], "name": d["name"][lang], "path": f"wow-forever/professions/{d['id']}/", "journeyman": ranks["Journeyman"]["min_char_level"],
                      "expert": ranks["Expert"].get("min_char_level"), "artisan": ranks["Artisan"]["min_char_level"], "gold": g, "silver": s,
                      "trainer_expert": ranks["Expert"]["trainer"], "trainer_artisan": ranks["Artisan"]["trainer"]})
    # which rank unlocks in which band (identical for every profession but first aid's Expert, which has no level in the client)
    for key, label_idx in (("journeyman", 0), ("expert", 1), ("artisan", 2)):
        lv = {p[key] for p in profs if p[key]}
        assert len(lv) == 1, (key, lv)
        level = lv.pop()
        bands[_band_of(level)]["ranks"].append((label_idx, level))
    lev = {k: next(p[k] for p in profs if p[k]) for k in ("journeyman", "expert", "artisan")}
    return {"bands": bands, "profs": profs, "lev": lev, "n_dungeons": sum(len(b["dungeons"]) for b in bands), "updated": UPDATED}


TX = {
    "fr": {
        "title": "Guide de leveling WoW Forever 1-60 : zones et donjons",
        "desc": "Monter de 1 à 60 dans WoW: Forever : zones par niveau, donjons du client bêta et niveaux des métiers. Ce qui vient de Classic est signalé.",
        "kicker": "LEVELING 1-60", "h1": "Guide de leveling WoW: Forever 1-60 : zones, donjons et métiers par niveau",
        "intro": "Le niveau maximum de WoW: Forever est 60. Voici, par tranche de dix niveaux, les zones où monter, les donjons à faire et les rangs de métiers qui se débloquent. Chaque donnée dit d'où elle vient : le client de la bêta, une annonce de Blizzard, ou WoW Classic quand Forever ne la confirme pas encore.",
        "chips": ["Niveau maximum 60", "Donjons : client bêta", "Zones : Classic, à confirmer", "Mis à jour le {date}"],
        "legend_h": "Ce qui est confirmé, ce qui ne l'est pas",
        "legend": [
            "<b>Donjons</b> : niveaux lus dans les données de la bêta (build 1.60.1.69913) ; le Hall of Thanes (13-18) et les Ruins of Lordaeron (15-20) viennent de l'annonce de Blizzard.",
            "<b>Métiers</b> : niveaux de personnage exigés pour apprendre chaque rang, lus dans le client de la bêta.",
            "<b>Zones</b> : niveaux de WoW Classic (Warcraft Wiki). Rien ne confirme encore qu'ils soient identiques dans Forever, où le monde est étendu avec du contenu nouveau : ils sont donnés à titre indicatif.",
        ],
        "band_h": "Niveaux {lo} à {hi}", "zones": "Zones (Classic, à confirmer)", "dungeons": "Donjons (client bêta)", "profs": "Métiers",
        "no_dungeon": "Aucun donjon de cette tranche dans les données de la bêta.", "lvl": "niv. {lo}-{hi}",
        "rank_text": ["Rang Compagnon (jusqu'à 150) : niveau {lvl}", "Rang Expert (jusqu'à 225) : niveau {lvl}", "Rang Artisan (jusqu'à 300) : niveau {lvl}"],
        "rank_none": "Pas de nouveau rang de métier dans cette tranche.",
        "band_zones_note": "Une zone est rangée dans la tranche où sa plage de niveaux commence.",
        "start_h": "Où commencer : les zones de départ", "start_p": "Chaque race commence dans sa zone de départ (niveaux 1 à 10 dans Classic). Les Skyborne, nouvelle race de Forever, commencent à Zephras Isle, jouable dès la bêta ; son niveau n'est pas annoncé.",
        "new_h": "Les zones nouvelles de Forever", "new_p": "Trois zones nouvelles sont annoncées. Leurs niveaux n'ont pas été publiés : nous ne les plaçons pas dans le tableau.",
        "new": ["Zephras Isle : zone de départ des Skyborne, jouable dès la bêta (Blizzard).", "Mount Hyjal et Riverglades : deux autres zones annoncées (Icy Veins, Wikipedia)."],
        "prof_h": "Métiers : quand chaque rang se débloque et ce qu'il coûte", "prof_p": "Le rang Compagnon s'apprend au niveau {j}, le rang Expert au niveau {e} et le rang Artisan au niveau {a} (niveau de personnage exigé par le client de la bêta). Le coût est celui de la page du métier : composants, recettes et rangs de 1 à 300, calculé avec nos données.",
        "col_prof": "Métier", "col_j": "Compagnon", "col_e": "Expert", "col_a": "Artisan", "col_cost": "Coût 1 → 300", "col_trainer": "Entraîneur", "lvl_short": "niv. {n}",
        "trainer_no": "Les rangs Expert et Artisan ne s'apprennent pas chez un entraîneur : ils s'obtiennent autrement (voir la page du métier).", "fa_e": "pas de niveau exigé dans le client",
        "gold": "{g} po {s} pa",
        "pb_note": "Aucun conseil de métier \"à faire en parallèle\" n'est donné ici : rien dans nos données ne permet de dire quel couple est le meilleur, et nous n'inventons pas de recommandation.",
        "dung_h": "Les donjons, dans l'ordre", "dung_p": "{n} donjons ont une plage de niveaux dans nos données, classés par niveau d'entrée. Chaque donjon a sa page avec son butin.",
        "faq_h": "Questions fréquentes", "faq": [
            ("Quels donjons faire pour monter de 1 à 60 dans WoW: Forever ?", "Dans les données de la bêta, les donjons s'étendent du niveau 13 (Hall of Thanes) au niveau 60 (Scholomance, Temple englouti, Profondeurs de Blackrock). Les plages de niveaux de chacun sont dans ce guide, avec le lien vers sa page de butin."),
            ("À quel niveau apprend-on les rangs de métier ?", "Selon le client de la bêta, le rang Compagnon s'apprend au niveau {j}, le rang Expert au niveau {e} et le rang Artisan au niveau {a}."),
            ("Les zones de leveling de WoW Classic sont-elles les mêmes dans Forever ?", "Ce n'est pas confirmé. Forever étend l'Azeroth d'origine avec du contenu nouveau (Zephras Isle, Mount Hyjal, Riverglades) : les plages de niveaux des zones de ce guide viennent de WoW Classic et seront vérifiées au lancement."),
            ("Peut-on monter jusqu'à 60 pendant la bêta ?", "Non : le plafond de la bêta est le niveau 30. Les données de niveaux 30 à 60 viennent des tables du client, pas de parties jouées."),
        ],
        "links_h": "Pour aller plus loin", "l_prog": "Progression 1-60 et nouveautés", "l_calc": "Calculateur de talents", "l_tier": "Tier list niveau 60", "l_dung": "Tous les donjons", "l_prof": "Guides de métiers",
        "src_h": "Sources et méthode", "src": ["Donjons : data/wow_dungeons, niveaux lus sur Wowhead Forever et dans le client de la bêta ; Hall of Thanes et Ruins of Lordaeron : Blizzard.", "Zones : Warcraft Wiki, « Zones by level (Classic) » : niveaux de WoW Classic.", "Métiers : tables de la bêta (rangs, niveaux exigés, coûts), les mêmes que sur les pages de métiers."],
    },
    "en": {
        "title": "WoW Forever leveling guide 1-60: zones and dungeons",
        "desc": "Level 1 to 60 in WoW: Forever: zones by level, beta client dungeons and profession ranks. What comes from Classic is flagged as such.",
        "kicker": "LEVELING 1-60", "h1": "WoW: Forever leveling guide 1-60: zones, dungeons and professions by level",
        "intro": "WoW: Forever's level cap is 60. Here are, in bands of ten levels, the zones to level in, the dungeons to run and the profession ranks that unlock. Every figure says where it comes from: the beta client, a Blizzard announcement, or WoW Classic when Forever has not confirmed it yet.",
        "chips": ["Level cap 60", "Dungeons: beta client", "Zones: Classic, to be confirmed", "Updated {date}"],
        "legend_h": "What is confirmed and what is not",
        "legend": [
            "<b>Dungeons</b>: levels read from the beta data (build 1.60.1.69913); the Hall of Thanes (13-18) and the Ruins of Lordaeron (15-20) come from Blizzard's announcement.",
            "<b>Professions</b>: character levels required to learn each rank, read from the beta client.",
            "<b>Zones</b>: WoW Classic levels (Warcraft Wiki). Nothing confirms yet that they are the same in Forever, where the world is extended with new content: they are indicative.",
        ],
        "band_h": "Levels {lo} to {hi}", "zones": "Zones (Classic, to be confirmed)", "dungeons": "Dungeons (beta client)", "profs": "Professions",
        "no_dungeon": "No dungeon in this band in the beta data.", "lvl": "lvl {lo}-{hi}",
        "rank_text": ["Journeyman rank (up to 150): level {lvl}", "Expert rank (up to 225): level {lvl}", "Artisan rank (up to 300): level {lvl}"],
        "rank_none": "No new profession rank in this band.",
        "band_zones_note": "A zone is listed in the band where its level range starts.",
        "start_h": "Where to start: the starting zones", "start_p": "Each race starts in its own starting zone (levels 1 to 10 in Classic). The Skyborne, Forever's new race, start on Zephras Isle, playable since the beta; its level has not been announced.",
        "new_h": "Forever's new zones", "new_p": "Three new zones are announced. Their levels have not been published, so we do not place them in the table.",
        "new": ["Zephras Isle: the Skyborne starting zone, playable since the beta (Blizzard).", "Mount Hyjal and Riverglades: two more announced zones (Icy Veins, Wikipedia)."],
        "prof_h": "Professions: when each rank unlocks and what it costs", "prof_p": "The Journeyman rank is learned at level {j}, Expert at level {e} and Artisan at level {a} (character level required by the beta client). The cost is the one on each profession page: reagents, recipes and ranks from 1 to 300, computed from our data.",
        "col_prof": "Profession", "col_j": "Journeyman", "col_e": "Expert", "col_a": "Artisan", "col_cost": "Cost 1 → 300", "col_trainer": "Trainer", "lvl_short": "lvl {n}",
        "trainer_no": "Expert and Artisan ranks are not learned from a trainer: they are obtained another way (see the profession page).", "fa_e": "no level required in the client",
        "gold": "{g}g {s}s",
        "pb_note": "No \"level in parallel\" profession advice is given here: nothing in our data says which pair is best, and we do not make up a recommendation.",
        "dung_h": "The dungeons, in order", "dung_p": "{n} dungeons have a level range in our data, sorted by entry level. Each dungeon has its own page with its loot.",
        "faq_h": "Frequently asked questions", "faq": [
            ("Which dungeons should I run to level from 1 to 60 in WoW: Forever?", "In the beta data, dungeons range from level 13 (Hall of Thanes) to level 60 (Scholomance, Sunken Temple, Blackrock Depths). Each dungeon's level range is in this guide, with a link to its loot page."),
            ("At what level do profession ranks unlock?", "According to the beta client, the Journeyman rank is learned at level {j}, Expert at level {e} and Artisan at level {a}."),
            ("Are WoW Classic's leveling zones the same in Forever?", "That is not confirmed. Forever extends the original Azeroth with new content (Zephras Isle, Mount Hyjal, Riverglades): the zone level ranges in this guide come from WoW Classic and will be checked at launch."),
            ("Can you reach level 60 during the beta?", "No: the beta cap is level 30. The level 30 to 60 data comes from the client tables, not from played games."),
        ],
        "links_h": "Go further", "l_prog": "Leveling 1-60 and news", "l_calc": "Talent calculator", "l_tier": "Level 60 tier list", "l_dung": "All dungeons", "l_prof": "Profession guides",
        "src_h": "Sources and method", "src": ["Dungeons: data/wow_dungeons, levels read from Wowhead Forever and the beta client; Hall of Thanes and Ruins of Lordaeron: Blizzard.", "Zones: Warcraft Wiki, \"Zones by level (Classic)\": WoW Classic levels.", "Professions: beta tables (ranks, required levels, costs), the same as on the profession pages."],
    },
}
