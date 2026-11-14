"""Tier list of the level-60 classes and specs (/wow-forever/tier-list/), derived only from data/wow_ranking60.json.
A spec's tier depends on its share of the best spec of the same role (DPS or tank); nothing here is hand-placed."""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

# (tier, minimum share of the best spec of the role, in %); the last one catches the rest
THRESHOLDS = [("S", 95.0), ("A", 88.0), ("B", 80.0), ("C", 72.0), ("D", 0.0)]


def tier_of(pct):
    for t, lo in THRESHOLDS:
        if pct >= lo:
            return t
    return THRESHOLDS[-1][0]


def _tiers(rows, key):
    top = max(r[key] for r in rows)
    out = {t: [] for t, _ in THRESHOLDS}
    for r in rows:
        pct = 100.0 * r[key] / top
        out[tier_of(pct)].append(dict(r, value=r[key], pct=round(pct, 1), tier=tier_of(pct)))
    for t in out:
        out[t].sort(key=lambda x: x["value"], reverse=True)
    return [{"tier": t, "min": lo, "rows": out[t]} for t, lo in THRESHOLDS if out[t]]


# client build whose spell and talent tables were imported on 2026-11-03 (launch build; the notes of 3 Nov 2026 are applied on top where the tables lack them)
CLIENT_BUILD = "1.60.1.70753"


def build(dps_rows, tank_rows, wt_classes, lang):
    """Everything the template needs; ([] rows -> None) when the simulator has no data."""
    if not dps_rows:
        return None
    meta = json.loads((PROJECT / "data" / "wow_ranking60.json").read_text(encoding="utf-8"))
    dps_t = _tiers(dps_rows, "dps")
    tank_t = []
    if tank_rows:      # tanks: threat per second only, so no letter tier (a low TPS says nothing about survival)
        ttop = max(r["dps"] for r in tank_rows)
        tank_t = [dict(r, value=r["dps"], pct=round(100.0 * r["dps"] / ttop, 1), tier="T") for r in sorted(tank_rows, key=lambda x: x["dps"], reverse=True)]
    by_spec = {r["spec_id"]: r for g in dps_t for r in g["rows"]}
    by_spec.update({r["spec_id"]: r for r in tank_t})
    classes = []
    for c in wt_classes:
        specs = [r for r in by_spec.values() if r["class_id"] == c["id"]]
        if not specs:
            continue
        order = ("S", "A", "B", "C", "D", "T")
        specs.sort(key=lambda r: order.index(r["tier"]) * 10000 - r["pct"])
        best = next((r for r in specs if r["tier"] != "T"), specs[0])
        classes.append({"id": c["id"], "name": c["name"][lang], "color": c.get("color"), "specs": specs, "best": best})
    classes.sort(key=lambda c: (("S", "A", "B", "C", "D", "T").index(c["best"]["tier"]), -c["best"]["pct"]))
    top = dps_t[0]["rows"][0]
    setup = (next((x for x in meta["specs"] if x["spec"] == top["spec_id"]), meta["specs"][0]).get("detail") or {}).get("setup") or {}
    strip = lambda n: n.split(" (")[0]
    allr = [r for g in dps_t for r in g["rows"]]
    gaps = sorted(((allr[i]["value"] - allr[i + 1]["value"], allr[i], allr[i + 1]) for i in range(len(allr) - 1)), key=lambda x: x[0])
    ties = [(a, b) for g, a, b in gaps if g < 2 * ((a.get("sem") or 0) ** 2 + (b.get("sem") or 0) ** 2) ** 0.5]
    from collections import Counter
    dps_ids = {r["spec_id"] for r in allr}
    bc, dc = Counter(), Counter()
    for x in meta["specs"]:
        if x["spec"] in dps_ids:
            su = (x.get("detail") or {}).get("setup") or {}
            bc.update({strip(b["name"]) for b in su.get("buffs", [])})
            dc.update({strip(b["name"]) for b in su.get("debuffs", [])})
    cond = {"buffs": [n for n, _ in bc.most_common()], "debuffs": [n for n, _ in dc.most_common()],
            "sem_max": max((r.get("sem") or 0) for r in allr), "gap": gaps[0] if gaps else None, "ties": ties}
    return {"cond": cond, "dps": dps_t, "tank": tank_t, "classes": classes, "top": top, "n_dps": len(dps_rows), "n_tank": len(tank_rows),
            "generated": meta["generated"], "build": CLIENT_BUILD, "fight": meta["fightLen"], "iters": meta["iterations"],
            "thresholds": THRESHOLDS}


TX = {
    "fr": {
        "title": "Tier list DPS WoW Forever niveau 60 – maj {short}",
        "desc": "Tier list DPS WoW Forever niveau 60 simulée, recalculée le {date} après le correctif du {hotfix} : spécialisations, tanks, méthode.",
        "kicker": "TIER LIST WOW FOREVER", "h1": "Tier list WoW Forever niveau 60 : quelle est la meilleure classe ?",
        "intro": "Chaque spécialisation est simulée au niveau 60 avec le meilleur équipement connu de la bêta, ses talents optimisés et les buffs d'un raid. Les paliers S à D viennent de l'écart avec la meilleure spécialisation de son rôle : rien n'est placé à la main. Ce classement ne tient compte que des objets déjà datamined : beaucoup d'objets restent à découvrir, et il peut donc changer.",
        "chips": ["Données du simulateur", "Build du jeu {build}", "Mise à jour le {date}", "Après le correctif du {hotfix}"],
        "best": "Le meilleur DPS simulé aujourd'hui est {name} avec {dps} DPS ; les paliers se calculent à partir de cette valeur.",
        "quick_h": "En bref : quelle est la meilleure classe ?",
        "quick_top": "{top_name} est la spécialisation DPS la plus forte de notre simulation ({top_dps} DPS).",
        "quick_s": "Palier S : {s_list}.", "quick_a": "Palier A : {a_list}.",
        "quick_tank": "En tank, {tank_name} arrive en tête ({tank_val} TPS).",
        "choose_h": "Quelle classe choisir selon votre style de jeu ?",
        "choose_intro": "Notre simulation mesure la puissance sur une cible, pas le plaisir de jeu. Voici la meilleure spécialisation de chaque style d'après nos mesures, et ce que nous ne pouvons pas encore dire.",
        "style_labels": {"melee": "Au corps à corps", "ranged": "À distance", "caster": "Lanceur de sorts"},
        "choose_tank": "Tank", "choose_tank_p": "classé à la menace par seconde : la survie n'est pas encore simulée.",
        "choose_versa": "Polyvalence", "choose_versa_p": "{versatile} proposent à la fois une spécialisation DPS et une spécialisation tank dans nos mesures (les soins ne sont pas simulés).",
        "choose_solo": "Solo et montée de niveau", "choose_solo_p": "nous ne simulons pas le jeu en solo ; voyez le", "choose_solo_link": "guide de leveling 1-60",
        "choose_dung": "Donjons", "choose_dung_p": "notre simulation porte sur une cible unique, sans dégâts de zone ; le butin et les boss sont dans les", "choose_dung_link": "pages des donjons",
        "choose_begin": "Débutant", "choose_begin_p": "nous ne classons pas la difficulté de jeu, faute de donnée fiable. Partez d'une classe des paliers S ou A qui vous plaît, puis lisez le guide de sa spécialisation.",
        "open_guide": "Guide", "guides_h": "Les guides de chaque spécialisation",
        "h_dps": "Tier list DPS", "h_tank": "Tier list tanks", "h_class": "Les classes de WoW Forever, de la mieux à la moins bien placée",
        "tier_word": "Palier", "tier_rule": "{lo} % ou plus du meilleur", "tier_rule_d": "moins de {hi} % du meilleur",
        "unit_dps": "DPS", "unit_tps": "TPS", "of_top": "du meilleur", "best_spec": "Meilleure spécialisation",
        "open_rank": "Détail du build", "open_guide": "Guide",
        "tank_note": "Les tanks sont classés à la menace par seconde (TPS), sans palier : la survie n'est pas encore simulée, donc ce classement ne dit pas quel tank encaisse le mieux.",
        "heal_h": "Et les soigneurs ?", "heal_p": "Les soigneurs ne sont pas classés : le simulateur ne modélise pas encore les soins sur un combat complet, et nous refusons d'afficher un chiffre inventé. Leurs guides restent disponibles dans la section des classes.",
        "heal_link": "Voir les guides de spécialisation",
        "meth_h": "Comment est calculée cette tier list", "meth": [
            "Simulateur : le moteur niveau 60 de BrokenMeta.gg ({url}), le même que celui de la page « Simulateur DPS ». Les tables de sorts et de statistiques viennent du client du jeu (build {build}) ; les changements de classes des notes de développement officielles du 3 novembre qui n'y figurent pas encore (valeurs de sorts, rangs de talents) sont appliqués par-dessus, avec la liste dans notre article sur ces notes. Les objets (butin des donjons, du raid et équipement fabriqué) viennent des pages Wowhead Forever lues le 17 octobre 2026.",
            "Combat : {fight} secondes contre un boss immobile de niveau 63, {iters} répétitions par spécialisation ; le DPS affiché est la moyenne, l'incertitude (± erreur standard) est donnée sur la page de détail.",
            "Équipement : le meilleur ensemble que l'optimiseur trouve parmi les objets connus de la bêta (donjons, raid, équipement fabriqué). Aucun objet n'est ajouté à la main. Seuls les objets déjà datamined sont pris en compte : beaucoup restent à découvrir, et les nouveaux objets feront bouger le classement.",
            "Paliers : S = au moins {S} % du DPS de la meilleure spécialisation, A = {A} %, B = {B} %, C = {C} %, D = en dessous. Les tanks sont comparés entre eux, sur la menace par seconde.",
            "Race : humain (orc pour le chaman), avec les racials lus dans le client bêta (refonte du 15 octobre, build 1.60.1.70425) ; la maîtrise d'arme de WoW Classic n'existe plus dans Forever, où les spécialisations d'armes ont été remplacées par du critique. Pour la mêlée, la table d'attaque de Classic (maîtrise 300 contre une défense de 315 pour un boss de niveau 63) est supposée valable : Forever ne le confirme pas, et si elle diffère, les spécialisations de mêlée bougeront.",
            "Limites : un combat sur cible unique, sans déplacements ni mécaniques de boss ; certaines valeurs de WoW Classic servent d'estimation quand Forever ne les donne pas encore (signalées dans le simulateur). Le classement bougera avec les correctifs.",
        ],
        "faq_h": "Questions fréquentes", "faq": [
            ("Quelle est la meilleure classe de WoW Forever au niveau 60 ?", "Dans notre simulation, la spécialisation DPS la plus haute est {name} ({dps} DPS, build {build}). Le palier S compte : {s_list}. Le classement complet des {n} spécialisations DPS est sur cette page, avec la méthode."),
            ("Quelle classe choisir pour débuter dans WoW Forever ?", "Nous ne classons pas la difficulté de jeu, faute de donnée fiable : notre tier list mesure la puissance. Choisissez une classe qui vous plaît parmi les paliers S et A ({s_list}), lisez le guide de sa spécialisation, puis comparez les races sur la page « Quelle race choisir »."),
            ("Quelle est la classe la plus forte, en DPS et en tank ?", "En DPS, {name} ({dps} DPS) ; en tank, {tank_name} ({tank_val} TPS, menace par seconde). Ces valeurs viennent de combats simulés sur une cible avec le meilleur équipement connu de la bêta ; la survie des tanks n'est pas encore simulée."),
            ("Quelle est la classe la plus polyvalente ?", "{versatile} proposent à la fois une spécialisation DPS et une spécialisation tank dans nos mesures. Les soigneurs ne sont pas simulés, nous ne pouvons donc pas comparer la polyvalence complète (DPS, tank et soins)."),
            ("La tier list de WoW Forever va-t-elle changer ?", "Oui : le classement ne tient compte que des objets déjà datamined, beaucoup d'objets restent à découvrir, et les valeurs bougent avec les correctifs. La date de mise à jour et le build du jeu sont affichés en haut de page, et le simulateur est relancé à chaque changement important."),
            ("Pourquoi les soigneurs ne sont-ils pas classés ?", "Le simulateur ne modélise pas encore les soins sur un combat complet. Plutôt que d'afficher un chiffre inventé, nous les laissons hors classement pour l'instant."),
        ],
        "links_h": "Aller plus loin", "l_sim": "Simulateur DPS", "l_calc": "Calculateur de talents", "l_dung": "Donjons", "l_races": "Quelle race choisir", "l_level": "Guide de leveling 1-60",
        "art_credit": "Illustrations : © Blizzard Entertainment",
        "chg_h": "Ce qui a changé depuis la version du {since}",
        "chg_p": "Ce qui a été recalculé : {reason}. Seuls les chiffres du simulateur ont bougé ; rien n'est retouché à la main.",
        "chg_up": "rang", "chg_same": "Sans changement de DPS : {names}.",
        "chg_tier": "palier {a} → {b}", "chg_rank": "rang {a} → {b}", "chg_rank_same": "rang {a}",
        "chg_note": "Ce calcul ne tient pas encore compte des correctifs publiés après le {hotfix} ; ils seront intégrés au prochain recalcul, et cette liste sera mise à jour.",
        "jump": [("#dps", "DPS"), ("#tanks", "Tanks"), ("#healers", "Soigneurs"), ("#changes", "Ce qui a changé"), ("#conditions", "Méthode")],
        "cta_sim": "Simuler ma spécialisation", "open_sim": "Simuler", "err": "erreur ±",
        "cond_h": "Conditions de simulation et marge d'erreur",
        "cond_p": "Chaque chiffre de cette page est une moyenne de {iters} combats simulés de {fight} secondes contre un boss de niveau 63, avec la même méthode pour toutes les spécialisations.",
        "cond": [
            "Raid : jusqu'à {nb} buffs selon la spécialisation ({buffs}) et {nd} affaiblissements du boss ({debuffs}) ; les consommables sont choisis pour chaque spécialisation (noms anglais du jeu).",
            "Équipement : le meilleur ensemble que l'optimiseur trouve parmi les objets déjà datamined (donjons, raid, fabrication, ensembles Sanctified), avec leurs bonus d'ensemble simulés. Talents : optimisés pour chaque spécialisation. Race : humain (orc pour le chaman).",
            "Marge d'erreur : chaque ligne affiche l'erreur standard de la moyenne (±). La plus grande est de ± {sem_max} DPS ; l'écart le plus faible entre deux spécialisations voisines est de {gap_min} DPS ({gap_pair}). {tie}",
        ],
        "tie_none": "Aucune paire voisine n'est dans la marge d'erreur : l'ordre affiché est celui de la simulation, pas du hasard.",
        "tie_some": "Dans la marge d'erreur (écart inférieur à deux fois l'erreur combinée) : {pairs}. Ces paires sont à égalité statistique.",
        "cmp_h": "Pourquoi nos chiffres diffèrent d'autres simulateurs",
        "cmp_p": "MythicSim ou WoWSims Forever publient d'autres valeurs de DPS. Les écarts viennent surtout de choix de simulation : l'équipement autorisé (ici, le meilleur ensemble connu, Sanctified compris), la durée et le niveau du boss, le nombre de combats, et la modélisation de certaines mécaniques. Nous avons comparé notre moteur à WoWSims Forever sur une configuration alignée ; il reste des écarts sur certaines mécaniques (le modèle de rage, par exemple), que nous réduisons version après version. Comparez donc les ordres de classement plutôt que les valeurs brutes, et utilisez le simulateur pour tester votre propre équipement.",
    },
    "en": {
        "title": "WoW Forever DPS Tier List (Level 60), updated {short}",
        "desc": "WoW Forever DPS tier list at level 60, simulated and rerun on {date} after the {hotfix} hotfix. Every spec ranked, tanks and method shown.",
        "kicker": "LEVEL 60 TIER LIST", "h1": "WoW: Forever level 60 tier list: which class is the best?",
        "intro": "Each spec is simulated at level 60 with the best gear known from the beta, optimized talents and raid buffs. Tiers S to D come from the gap to the best spec of the same role: nothing is placed by hand. This ranking only counts the items that have already been datamined: many items are still undiscovered, so it can change.",
        "chips": ["Simulator data", "Game build {build}", "Updated {date}", "After the {hotfix} hotfix"],
        "best": "The highest simulated DPS today is {name} with {dps} DPS; the tiers are computed from that value.",
        "quick_h": "In short: which class is the best?",
        "quick_top": "{top_name} is the strongest DPS spec in our simulation ({top_dps} DPS).",
        "quick_s": "S tier: {s_list}.", "quick_a": "A tier: {a_list}.",
        "quick_tank": "For tanking, {tank_name} comes first ({tank_val} TPS).",
        "choose_h": "Which class should you pick for your playstyle?",
        "choose_intro": "Our simulation measures single-target power, not how fun a class is. Here is the best spec of each style according to our measures, and what we cannot say yet.",
        "style_labels": {"melee": "Melee", "ranged": "Ranged", "caster": "Spellcaster"},
        "choose_tank": "Tank", "choose_tank_p": "ranked by threat per second: survival is not simulated yet.",
        "choose_versa": "Versatility", "choose_versa_p": "{versatile} offer both a DPS spec and a tank spec in our measures (healing is not simulated).",
        "choose_solo": "Solo and leveling", "choose_solo_p": "we do not simulate solo play; see the", "choose_solo_link": "1-60 leveling guide",
        "choose_dung": "Dungeons", "choose_dung_p": "our simulation is single target, with no area damage; loot and bosses are in the", "choose_dung_link": "dungeon pages",
        "choose_begin": "Beginner", "choose_begin_p": "we do not rank how hard a class is to play, for lack of reliable data. Start from an S or A tier class you like, then read its spec guide.",
        "open_guide": "Guide", "guides_h": "Guides for every spec",
        "h_dps": "DPS tier list", "h_tank": "Tank tier list", "h_class": "WoW: Forever classes, from best to least well placed",
        "tier_word": "Tier", "tier_rule": "{lo}% or more of the best", "tier_rule_d": "under {hi}% of the best",
        "unit_dps": "DPS", "unit_tps": "TPS", "of_top": "of the best", "best_spec": "Best spec",
        "open_rank": "Build details", "open_guide": "Guide",
        "tank_note": "Tanks are ranked by threat per second (TPS), with no tier letter: survivability is not simulated yet, so this ranking does not say which tank takes damage best.",
        "heal_h": "What about healers?", "heal_p": "Healers are not ranked: the simulator does not model healing over a full fight yet, and we will not show an invented number. Their guides remain available in the classes section.",
        "heal_link": "See the spec guides",
        "meth_h": "How this tier list is computed", "meth": [
            "Simulator: BrokenMeta.gg's level 60 engine ({url}), the same as the \"DPS simulator\" page. Spell and stat tables come from the game client (build {build}); the class changes of Blizzard's official development notes of November 3 that are not in it yet (spell values, talent ranks) are applied on top, and the list is in our article on those notes. Items (dungeon, raid and crafted gear) come from the Wowhead Forever pages read on October 17, 2026.",
            "Fight: {fight} seconds against a stationary level 63 boss, {iters} runs per spec; the DPS shown is the mean, with its standard error on the detail page.",
            "Gear: the best set the optimizer finds among the items known from the beta (dungeons, raid, crafted gear). No item is added by hand. Only items that have already been datamined are counted: many are still to be discovered, and new items will move the ranking.",
            "Tiers: S = at least {S}% of the best spec's DPS, A = {A}%, B = {B}%, C = {C}%, D = below. Tanks are compared with each other, on threat per second.",
            "Race: Human (Orc for Shaman), with the racials read from the beta client (October 15 rework, build 1.60.1.70425); WoW Classic's weapon skill no longer exists in Forever, where weapon specializations were replaced by critical strike chance. For melee, Classic's attack table (skill 300 against a defense of 315 for a level 63 boss) is assumed to apply: Forever does not confirm it, and if it differs, the melee specs will move.",
            "Limits: a single-target fight with no movement or boss mechanics; some WoW Classic values stand in when Forever does not give them yet (flagged in the simulator). The ranking will move with patches.",
        ],
        "faq_h": "Frequently asked questions", "faq": [
            ("What is the best class in WoW: Forever at level 60?", "In our simulation the highest DPS spec is {name} ({dps} DPS, build {build}). The full ranking of the {n} DPS specs is on this page, with the method."),
            ("How are the tiers of this tier list built?", "Each spec is compared with the best one of its role: S from {S}% of its DPS, A from {A}%, B from {B}%, C from {C}%, D below. Nothing is placed by hand."),
            ("Will the tier list change?", "Yes: the ranking only counts items that have already been datamined, many items are still undiscovered, and values move with patches. The update date and the game build are shown at the top of the page, and the simulator is rerun after every major change."),
            ("Why are healers not ranked?", "The simulator does not model healing over a full fight yet. Rather than show an invented number, we leave them out for now."),
        ],
        "links_h": "Go further", "l_sim": "DPS simulator", "l_calc": "Talent calculator", "l_dung": "Dungeons", "l_races": "Which race to pick", "l_level": "1-60 leveling guide",
        "art_credit": "Artwork: © Blizzard Entertainment",
        "chg_h": "What changed since the {since} version",
        "chg_p": "What was recomputed: {reason}. Only the simulator's numbers moved; nothing is edited by hand.",
        "chg_up": "rank", "chg_same": "No DPS change: {names}.",
        "chg_tier": "tier {a} → {b}", "chg_rank": "rank {a} → {b}", "chg_rank_same": "rank {a}",
        "chg_note": "This run does not include patches published after {hotfix} yet; they will go into the next recompute, and this list will be updated.",
        "jump": [("#dps", "DPS"), ("#tanks", "Tanks"), ("#healers", "Healers"), ("#changes", "What changed"), ("#conditions", "Method")],
        "cta_sim": "Simulate my spec", "open_sim": "Simulate", "err": "error ±",
        "cond_h": "Simulation conditions and margin of error",
        "cond_p": "Every number on this page is the mean of {iters} simulated {fight}-second fights against a level 63 boss, with the same method for every spec.",
        "cond": [
            "Raid: up to {nb} buffs depending on the spec ({buffs}) and {nd} boss debuffs ({debuffs}); consumables are chosen for each spec.",
            "Gear: the best set the optimizer finds among the items already datamined (dungeons, raid, crafting, Sanctified sets), with their set bonuses simulated. Talents: optimized for each spec. Race: Human (Orc for Shaman).",
            "Margin of error: every row shows the standard error of the mean (±). The largest is ± {sem_max} DPS; the smallest gap between two neighbouring specs is {gap_min} DPS ({gap_pair}). {tie}",
        ],
        "tie_none": "No neighbouring pair is within the margin of error: the order shown comes from the simulation, not from chance.",
        "tie_some": "Within the margin of error (gap under twice the combined error): {pairs}. These pairs are statistically tied.",
        "cmp_h": "Why our numbers differ from other simulators",
        "cmp_p": "MythicSim and WoWSims Forever publish other DPS values. The gaps mostly come from simulation choices: the gear allowed (here, the best known set, Sanctified included), the boss level and fight length, the number of fights, and how some mechanics are modelled. We compared our engine with WoWSims Forever on an aligned setup; some gaps remain on certain mechanics (the rage model, for example), and we narrow them version after version. So compare the order of the rankings rather than the raw values, and use the simulator to test your own gear.",
    },
}


# How a spec fights: a game fact, not a measure (used only to group the measured DPS by style)
STYLE = {
    "warrior_fury": "melee", "warrior_arms": "melee", "rogue_combat": "melee", "rogue_assassination": "melee", "rogue_subtlety": "melee",
    "hunter_melee": "melee", "shaman_enhancement": "melee", "druid_feral": "melee", "paladin_retribution": "melee",
    "hunter_marksmanship": "ranged", "hunter_beastmastery": "ranged",
    "mage_fire": "caster", "mage_frost": "caster", "mage_arcane": "caster", "warlock_affliction": "caster", "warlock_destruction": "caster",
    "warlock_demonology": "caster", "priest_shadow": "caster", "shaman_elemental": "caster", "druid_balance": "caster",
}


def _join(names, lang):
    names = list(names)
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + (" et " if lang == "fr" else " and ") + names[-1]


def _num(v, lang):
    return "{:,.0f}".format(v).replace(",", " " if lang == "fr" else ",")


def add_content(tl, lang):
    """Summary, "which class for your playstyle" list and the values the FAQ texts need, all computed from the tiers (nothing hand-written)."""
    tx = TX[lang]
    nm = lambda r: r["class_name"] + " " + r["spec_name"]
    tiers = {g["tier"]: g["rows"] for g in tl["dps"]}
    dps_rows = [r for g in tl["dps"] for r in g["rows"]]
    s_list = _join([nm(r) for r in tiers.get("S", [])], lang)
    a_list = _join([nm(r) for r in tiers.get("A", [])], lang)
    tank = tl["tank"][0] if tl["tank"] else None
    versatile = [c["name"] for c in tl["classes"] if any(r["tier"] == "T" for r in c["specs"]) and any(r["tier"] != "T" for r in c["specs"])]
    fmt = {"s_list": s_list, "a_list": a_list, "versatile": _join(versatile, lang), "tank_name": nm(tank) if tank else "", "tank_val": _num(tank["value"], lang) if tank else ""}
    top = tl["top"]
    quick = [tx["quick_top"].format(top_name=nm(top), top_dps=_num(top["value"], lang))]
    if s_list:
        quick.append(tx["quick_s"].format(**fmt))
    if a_list:
        quick.append(tx["quick_a"].format(**fmt))
    if tank:
        quick.append(tx["quick_tank"].format(**fmt))
    tl["quick"] = " ".join(quick)
    choose = []
    for style in ("melee", "ranged", "caster"):
        rows = [r for r in dps_rows if STYLE.get(r["spec_id"]) == style]
        if rows:
            r = rows[0]
            choose.append({"h": tx["style_labels"][style], "row": r, "val": _num(r["value"], lang), "unit": tx["unit_dps"], "p": "", "link": None})
    if tank:
        choose.append({"h": tx["choose_tank"], "row": tank, "val": _num(tank["value"], lang), "unit": tx["unit_tps"], "p": tx["choose_tank_p"], "link": None})
    if versatile:
        choose.append({"h": tx["choose_versa"], "row": None, "p": tx["choose_versa_p"].format(**fmt), "link": None})
    choose.append({"h": tx["choose_solo"], "row": None, "p": tx["choose_solo_p"], "link": ("wow-forever/leveling/", tx["choose_solo_link"])})
    choose.append({"h": tx["choose_dung"], "row": None, "p": tx["choose_dung_p"], "link": ("wow-forever/dungeons/", tx["choose_dung_link"])})
    choose.append({"h": tx["choose_begin"], "row": None, "p": tx["choose_begin_p"], "link": None})
    tl["choose"] = choose
    tl["fmt"] = fmt
    c = tl["cond"]
    nmr = lambda r: r["class_name"] + " " + r["spec_name"]
    dec = lambda v: ("%.1f" % v).replace(".", "," if lang == "fr" else ".")
    gap = c["gap"]
    tie = tx["tie_some"].format(pairs=_join([nmr(a) + " / " + nmr(b) for a, b in c["ties"]], lang)) if c["ties"] else tx["tie_none"]
    tl["cond_p"] = tx["cond_p"].format(iters=_num(tl["iters"], lang), fight=tl["fight"])
    tl["cond_items"] = [t.format(nb=len(c["buffs"]), buffs=", ".join(c["buffs"]), nd=len(c["debuffs"]), debuffs=", ".join(c["debuffs"]), sem_max=dec(c["sem_max"]),
                                 gap_min=dec(gap[0]) if gap else "", gap_pair=(nmr(gap[1]) + " / " + nmr(gap[2])) if gap else "", tie=tie) for t in tx["cond"]]
    return tl


# ---------------------------------------------------------------------------
# Hub "tier list WoW Forever" (/wow-forever/tier-lists/): one entry point to the DPS and tank rankings (this module),
# healers (not simulated), leveling, races and sets. Every number comes from build(); nothing is hand-placed.
# ---------------------------------------------------------------------------
HUB_PATH = "/wow-forever/tier-lists/"
HUB_TX = {
    "fr": {
        "title": "Tier list WoW Forever : DPS, tanks, soins, leveling",
        "desc": "Toutes les tier lists WoW Forever : DPS et tanks simulés au niveau 60, soins, leveling, races et ensembles. Mise à jour le {date}.",
        "kicker": "TIER LISTS WOW FOREVER", "h1": "Tier list WoW Forever : DPS, tanks, soigneurs et leveling",
        "intro": "Une seule page pour choisir la tier list dont vous avez besoin. Le classement DPS et tanks est simulé au niveau 60 avec la même méthode pour toutes les spécialisations ; pour le reste, nous disons clairement ce qui est mesuré et ce qui ne l'est pas encore.",
        "chips": ["Données du simulateur", "Build du jeu {build}", "Recalculé le {date}"],
        "cards_h": "Choisissez votre tier list",
        "c_dps": "DPS niveau 60", "c_dps_p": "{n} spécialisations simulées, de {top_name} ({top_dps} DPS) à {low_name} ({low_dps} DPS), en paliers S à D.", "c_dps_a": "Tier list DPS",
        "c_tank": "Tanks", "c_tank_p": "{n_tank} spécialisations classées à la menace par seconde : {tank_name} arrive en tête ({tank_val} TPS). La survie n'est pas simulée.", "c_tank_a": "Voir les tanks",
        "c_heal": "Soigneurs", "c_heal_p": "Pas de classement : le simulateur ne modélise pas encore les soins sur un combat complet, et nous n'affichons pas de chiffre inventé. Leurs guides existent.", "c_heal_a": "Guides des classes",
        "c_lvl": "Leveling 1-60", "c_lvl_p": "Le parcours de montée de niveau, zone par zone. Nous ne simulons pas le jeu en solo, il n'y a donc pas de classement de vitesse de leveling.", "c_lvl_a": "Guide de leveling",
        "c_race": "Quelle race choisir", "c_race_p": "Pour chaque classe, les races classées d'après leurs racials lus dans le client et le DPS simulé.", "c_race_a": "Choisir sa race",
        "c_set": "Ensembles Sanctified", "c_set_p": "Les ensembles de classe et leurs bonus, avec l'effet simulé sur le DPS de chaque spécialisation.", "c_set_a": "Voir les ensembles",
        "top_h": "Le haut du classement DPS aujourd'hui", "top_all": "Classement DPS complet et méthode",
        "tier_s": "Palier S",
        "why_h": "Pourquoi une tier list simulée ?",
        "why": [
            "Chaque spécialisation passe par le même moteur, avec le meilleur équipement connu, ses talents optimisés et les buffs d'un raid : l'écart entre deux lignes vient du jeu, pas d'un avis.",
            "Les paliers dépendent de l'écart avec la meilleure spécialisation de son rôle. Rien n'est placé à la main, et le classement est recalculé quand les correctifs ou les nouveaux objets le justifient.",
            "Les limites sont affichées : combat sur une cible, sans déplacements ni mécaniques de boss, et seulement les objets déjà datamined. La méthode complète est en bas de la tier list DPS.",
        ],
        "faq_h": "Questions fréquentes", "faq": [
            ("Où trouver la tier list de WoW Forever ?", "Sur cette page, qui renvoie vers chaque classement : DPS niveau 60 (simulé), tanks (menace par seconde), races, ensembles et guide de leveling. Les soigneurs ne sont pas encore classés."),
            ("Quelle est la meilleure classe de WoW Forever ?", "Dans notre simulation, la spécialisation DPS la plus haute est {top_name} avec {top_dps} DPS (build {build}). Le palier S compte : {s_list}. Le classement complet est sur la tier list DPS."),
            ("Votre tier list est-elle à jour ?", "Elle a été recalculée le {date} avec le build {build} du jeu. Cette date vient du dernier recalcul du simulateur, pas de la date de la page : elle change quand les chiffres changent."),
            ("Y a-t-il une tier list pour les soigneurs ou le PvP ?", "Pas encore. Le simulateur ne modélise ni les soins ni le PvP, et nous préférons ne rien afficher plutôt qu'un chiffre inventé."),
        ],
    },
    "en": {
        "title": "WoW Forever tier list: DPS, tanks, healers, leveling",
        "desc": "Every WoW Forever tier list in one place: simulated level 60 DPS and tanks, healers, leveling, races and sets. Recomputed {date}.",
        "kicker": "WOW FOREVER TIER LISTS", "h1": "WoW Forever tier list: DPS, tanks, healers and leveling",
        "intro": "One page to pick the tier list you need. The DPS and tank ranking is simulated at level 60 with the same method for every spec; for the rest, we say plainly what is measured and what is not yet.",
        "chips": ["Simulator data", "Game build {build}", "Recomputed {date}"],
        "cards_h": "Pick your tier list",
        "c_dps": "Level 60 DPS", "c_dps_p": "{n} specs simulated, from {top_name} ({top_dps} DPS) to {low_name} ({low_dps} DPS), in S to D tiers.", "c_dps_a": "DPS tier list",
        "c_tank": "Tanks", "c_tank_p": "{n_tank} specs ranked by threat per second: {tank_name} comes first ({tank_val} TPS). Survivability is not simulated.", "c_tank_a": "See the tanks",
        "c_heal": "Healers", "c_heal_p": "Not ranked: the simulator does not model healing over a full fight yet, and we will not show an invented number. Their guides are available.", "c_heal_a": "Class guides",
        "c_lvl": "Leveling 1-60", "c_lvl_p": "The leveling route, zone by zone. We do not simulate solo play, so there is no leveling speed ranking.", "c_lvl_a": "Leveling guide",
        "c_race": "Which race to pick", "c_race_p": "For each class, races ranked from the racials read in the client and the simulated DPS.", "c_race_a": "Pick a race",
        "c_set": "Sanctified sets", "c_set_p": "Class sets and their bonuses, with the simulated effect on each spec's DPS.", "c_set_a": "See the sets",
        "top_h": "Top of the DPS ranking today", "top_all": "Full DPS ranking and method",
        "tier_s": "S tier",
        "why_h": "Why a simulated tier list?",
        "why": [
            "Every spec goes through the same engine, with the best known gear, optimized talents and raid buffs: the gap between two lines comes from the game, not from an opinion.",
            "Tiers depend on the gap to the best spec of the same role. Nothing is placed by hand, and the ranking is recomputed when patches or new items justify it.",
            "Limits are shown: a single-target fight with no movement or boss mechanics, and only items that have already been datamined. The full method is at the bottom of the DPS tier list.",
        ],
        "faq_h": "Frequently asked questions", "faq": [
            ("Where is the WoW Forever tier list?", "On this page, which links to every ranking: level 60 DPS (simulated), tanks (threat per second), races, sets and the leveling guide. Healers are not ranked yet."),
            ("What is the best class in WoW Forever?", "In our simulation the highest DPS spec is {top_name} with {top_dps} DPS (build {build}). S tier holds: {s_list}. The full ranking is on the DPS tier list."),
            ("Is your tier list up to date?", "It was recomputed on {date} with game build {build}. That date comes from the last simulator run, not from the page date: it changes when the numbers change."),
            ("Is there a healer or PvP tier list?", "Not yet. The simulator models neither healing nor PvP, and we would rather show nothing than an invented number."),
        ],
    },
}


def hub_build(tl, lang):
    """Values of the hub, taken from the already-built tier list `tl` (build() + add_content())."""
    nm = lambda r: r["class_name"] + " " + r["spec_name"]
    dps_rows = [r for g in tl["dps"] for r in g["rows"]]
    tank = tl["tank"][0] if tl["tank"] else None
    s_rows = next((g["rows"] for g in tl["dps"] if g["tier"] == "S"), [])
    fmt = {
        "n": tl["n_dps"], "n_tank": tl["n_tank"], "top_name": nm(dps_rows[0]), "top_dps": _num(dps_rows[0]["value"], lang),
        "low_name": nm(dps_rows[-1]), "low_dps": _num(dps_rows[-1]["value"], lang),
        "tank_name": nm(tank) if tank else "", "tank_val": _num(tank["value"], lang) if tank else "",
        "s_list": _join([nm(r) for r in s_rows], lang), "build": tl["build"], "date": tl["date_txt"],
    }
    return {"top5": dps_rows[:5], "fmt": fmt, "has_tank": bool(tank)}


# ---------------------------------------------------------------------------
# Freshness (2026-11-14): date of the last real recompute, the hotfix it includes, and what moved since the previous snapshot.
# data/wow_ranking_changelog.json says which hotfix the recompute integrates (written by hand AFTER the recompute, so the page never claims a patch the numbers lack);
# data/wow_ranking60_prev.json is the ranking of the previous published version (copy the current compact ranking there before the next recompute).
# ---------------------------------------------------------------------------
_MONTHS = {"fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
           "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]}
_SHORT = {"fr": ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."],
          "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}


def date_txt(iso, lang, short=False, year=True):
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    if short:
        return f"{d} {_SHORT['fr'][m - 1]}" if lang == "fr" else f"{_SHORT['en'][m - 1]} {d}"
    return (f"{d} {_MONTHS['fr'][m - 1]}" + (f" {y}" if year else "")) if lang == "fr" else (f"{_MONTHS['en'][m - 1]} {d}" + (f", {y}" if year else ""))


def _load(name):
    f = PROJECT / "data" / name
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def freshness(tl, lang):
    """Adds hotfix_txt / short_txt (and the "what changed" rows) to tl; the hotfix is the one named in the changelog file."""
    log = _load("wow_ranking_changelog.json") or {}
    tl["short_txt"] = date_txt(tl["generated"], lang, short=True)
    tl["hotfix_txt"] = date_txt(log["hotfix_date"], lang, year=False) if log.get("hotfix_date") else tl["date_txt"]
    prev = _load("wow_ranking60_prev.json")
    tl["changes"] = None
    if not prev or not log:
        return tl
    tx = TX[lang]
    old = {r["spec"]: r["dps"] for r in prev["specs"] if r["role"] == "dps"}
    otop = max(old.values())
    oorder = sorted(old, key=lambda k: -old[k])
    rows = [r for g in tl["dps"] for r in g["rows"]]
    moved, same = [], []
    for i, r in enumerate(rows):
        o = old.get(r["spec_id"])
        if o is None:
            continue
        delta = 100.0 * (r["value"] / o - 1)
        if abs(delta) < 0.5:
            same.append(r["class_name"] + " " + r["spec_name"])
            continue
        a, b = oorder.index(r["spec_id"]) + 1, i + 1
        ta, tb = tier_of(100.0 * o / otop), r["tier"]
        bits = [tx["chg_rank"].format(a=a, b=b) if a != b else tx["chg_rank_same"].format(a=b)]
        if ta != tb:
            bits.append(tx["chg_tier"].format(a=ta, b=tb))
        moved.append({"row": r, "old": o, "new": r["value"], "delta": delta, "txt": ", ".join(bits), "better": a > b or (a == b and ta != tb and ta > tb)})
    tl["changes"] = {"since": date_txt(prev["generated"], lang), "reason": log.get(lang, ""), "moved": moved, "same": _join(same, lang),
                     "n_same": len(same)}
    return tl
