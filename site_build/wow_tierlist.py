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


# latest beta client build whose spell, talent and racial tables were compared with the imported ones (identical to 1.60.1.70425)
CLIENT_BUILD = "1.60.1.70450"


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
    return {"dps": dps_t, "tank": tank_t, "classes": classes, "top": top, "n_dps": len(dps_rows), "n_tank": len(tank_rows),
            "generated": meta["generated"], "build": CLIENT_BUILD, "fight": meta["fightLen"], "iters": meta["iterations"],
            "thresholds": THRESHOLDS}


TX = {
    "fr": {
        "title": "Tier list WoW Forever : meilleures classes et spés",
        "desc": "Quelle est la meilleure classe de WoW Forever ? Tier list DPS et tanks simulée au niveau 60, mise à jour le {date} (build {build}).",
        "kicker": "TIER LIST WOW FOREVER", "h1": "Tier list WoW Forever niveau 60 : quelle est la meilleure classe ?",
        "intro": "Chaque spécialisation est simulée au niveau 60 avec le meilleur équipement connu de la bêta, ses talents optimisés et les buffs d'un raid. Les paliers S à D viennent de l'écart avec la meilleure spécialisation de son rôle : rien n'est placé à la main. Ce classement ne tient compte que des objets déjà datamined : beaucoup d'objets restent à découvrir, et il peut donc changer.",
        "chips": ["Données du simulateur", "Build du jeu {build}", "Mise à jour le {date}"],
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
            "Simulateur : le moteur niveau 60 de BrokenMeta.gg ({url}), le même que celui de la page « Simulateur DPS ». Les tables de sorts et de statistiques viennent du client de la bêta (build {build}). Les objets (butin des donjons, du raid et équipement fabriqué) viennent des pages Wowhead Forever lues le 17 octobre 2026.",
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
    },
    "en": {
        "title": "WoW Forever tier list: best classes at level 60",
        "desc": "Tier list of WoW: Forever classes and specs at level 60, ranked by simulated DPS. Method, data and game build shown on the page.",
        "kicker": "LEVEL 60 TIER LIST", "h1": "WoW: Forever level 60 tier list: which class is the best?",
        "intro": "Each spec is simulated at level 60 with the best gear known from the beta, optimized talents and raid buffs. Tiers S to D come from the gap to the best spec of the same role: nothing is placed by hand. This ranking only counts the items that have already been datamined: many items are still undiscovered, so it can change.",
        "chips": ["Simulator data", "Game build {build}", "Updated {date}"],
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
            "Simulator: BrokenMeta.gg's level 60 engine ({url}), the same as the \"DPS simulator\" page. Spell and stat tables come from the beta client (build {build}). Items (dungeon, raid and crafted gear) come from the Wowhead Forever pages read on October 17, 2026.",
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
    return tl
