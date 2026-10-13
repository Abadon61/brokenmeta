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
            "generated": meta["generated"], "build": meta["build"], "fight": meta["fightLen"], "iters": meta["iterations"],
            "thresholds": THRESHOLDS}


TX = {
    "fr": {
        "title": "Tier list WoW Forever niveau 60 : meilleures classes",
        "desc": "Tier list des classes et spécialisations de WoW: Forever au niveau 60, classées par DPS simulé. Méthode, données et build du jeu affichés.",
        "kicker": "TIER LIST NIVEAU 60", "h1": "Tier list WoW: Forever niveau 60 : quelle est la meilleure classe ?",
        "intro": "Chaque spécialisation est simulée au niveau 60 avec le meilleur équipement connu de la bêta, ses talents optimisés et les buffs d'un raid. Les paliers S à D viennent de l'écart avec la meilleure spécialisation de son rôle : rien n'est placé à la main.",
        "chips": ["Données du simulateur", "Build du jeu {build}", "Mise à jour le {date}"],
        "best": "Le meilleur DPS simulé aujourd'hui est {name} avec {dps} DPS ; les paliers se calculent à partir de cette valeur.",
        "h_dps": "Tier list DPS", "h_tank": "Tier list tanks", "h_class": "Les classes de WoW: Forever, du mieux au moins bien placé",
        "tier_word": "Palier", "tier_rule": "{lo} % ou plus du meilleur", "tier_rule_d": "moins de {hi} % du meilleur",
        "unit_dps": "DPS", "unit_tps": "TPS", "of_top": "du meilleur", "best_spec": "Meilleure spécialisation",
        "open_rank": "Détail du build", "open_guide": "Guide",
        "tank_note": "Les tanks sont classés à la menace par seconde (TPS), sans palier : la survie n'est pas encore simulée, donc ce classement ne dit pas quel tank encaisse le mieux.",
        "heal_h": "Et les soigneurs ?", "heal_p": "Les soigneurs ne sont pas classés : le simulateur ne modélise pas encore les soins sur un combat complet, et nous refusons d'afficher un chiffre inventé. Leurs guides restent disponibles dans la section des classes.",
        "heal_link": "Voir les guides de spécialisation",
        "meth_h": "Comment est calculée cette tier list", "meth": [
            "Simulateur : le moteur niveau 60 de BrokenMeta.gg ({url}), le même que celui de la page « Simulateur DPS niveau 60 ». Les tables de sorts et de statistiques viennent du client de la bêta (build {build}).",
            "Combat : {fight} secondes contre un boss immobile de niveau 63, {iters} répétitions par spécialisation ; le DPS affiché est la moyenne, l'incertitude (± erreur standard) est donnée sur la page de détail.",
            "Équipement : le meilleur ensemble que l'optimiseur trouve parmi les objets connus de la bêta (donjons, raid, équipement fabriqué). Aucun objet n'est ajouté à la main.",
            "Paliers : S = au moins {S} % du DPS de la meilleure spécialisation, A = {A} %, B = {B} %, C = {C} %, D = en dessous. Les tanks sont comparés entre eux, sur la menace par seconde.",
            "Limites : un combat sur cible unique, sans déplacements ni mécaniques de boss ; certaines valeurs de WoW Classic servent d'estimation quand Forever ne les donne pas encore (signalées dans le simulateur). Le classement bougera avec les correctifs.",
        ],
        "faq_h": "Questions fréquentes", "faq": [
            ("Quelle est la meilleure classe de WoW: Forever au niveau 60 ?", "Dans notre simulation, la spécialisation DPS la plus haute est {name} ({dps} DPS, build {build}). Le classement complet des {n} spécialisations DPS est sur cette page, avec la méthode."),
            ("Comment sont construits les paliers de la tier list ?", "Chaque spécialisation est comparée à la meilleure de son rôle : S à partir de {S} % de son DPS, A à partir de {A} %, B à partir de {B} %, C à partir de {C} %, D en dessous. Aucun placement manuel."),
            ("La tier list va-t-elle changer ?", "Oui : le jeu est encore en bêta et les valeurs bougent avec les correctifs. La date de mise à jour et le build du jeu sont affichés en haut de page, et le simulateur est relancé à chaque changement important."),
            ("Pourquoi les soigneurs ne sont-ils pas classés ?", "Le simulateur ne modélise pas encore les soins sur un combat complet. Plutôt que d'afficher un chiffre inventé, nous les laissons hors classement pour l'instant."),
        ],
        "links_h": "Aller plus loin", "l_sim": "Simulateur DPS niveau 60", "l_calc": "Calculateur de talents", "l_dung": "Donjons", "l_mysim": "Simuler mon personnage",
        "art_credit": "Illustrations : © Blizzard Entertainment",
    },
    "en": {
        "title": "WoW Forever tier list: best classes at level 60",
        "desc": "Tier list of WoW: Forever classes and specs at level 60, ranked by simulated DPS. Method, data and game build shown on the page.",
        "kicker": "LEVEL 60 TIER LIST", "h1": "WoW: Forever level 60 tier list: which class is the best?",
        "intro": "Each spec is simulated at level 60 with the best gear known from the beta, optimized talents and raid buffs. Tiers S to D come from the gap to the best spec of the same role: nothing is placed by hand.",
        "chips": ["Simulator data", "Game build {build}", "Updated {date}"],
        "best": "The highest simulated DPS today is {name} with {dps} DPS; the tiers are computed from that value.",
        "h_dps": "DPS tier list", "h_tank": "Tank tier list", "h_class": "WoW: Forever classes, from best to least well placed",
        "tier_word": "Tier", "tier_rule": "{lo}% or more of the best", "tier_rule_d": "under {hi}% of the best",
        "unit_dps": "DPS", "unit_tps": "TPS", "of_top": "of the best", "best_spec": "Best spec",
        "open_rank": "Build details", "open_guide": "Guide",
        "tank_note": "Tanks are ranked by threat per second (TPS), with no tier letter: survivability is not simulated yet, so this ranking does not say which tank takes damage best.",
        "heal_h": "What about healers?", "heal_p": "Healers are not ranked: the simulator does not model healing over a full fight yet, and we will not show an invented number. Their guides remain available in the classes section.",
        "heal_link": "See the spec guides",
        "meth_h": "How this tier list is computed", "meth": [
            "Simulator: BrokenMeta.gg's level 60 engine ({url}), the same as the \"Level 60 DPS simulator\" page. Spell and stat tables come from the beta client (build {build}).",
            "Fight: {fight} seconds against a stationary level 63 boss, {iters} runs per spec; the DPS shown is the mean, with its standard error on the detail page.",
            "Gear: the best set the optimizer finds among the items known from the beta (dungeons, raid, crafted gear). No item is added by hand.",
            "Tiers: S = at least {S}% of the best spec's DPS, A = {A}%, B = {B}%, C = {C}%, D = below. Tanks are compared with each other, on threat per second.",
            "Limits: a single-target fight with no movement or boss mechanics; some WoW Classic values stand in when Forever does not give them yet (flagged in the simulator). The ranking will move with patches.",
        ],
        "faq_h": "Frequently asked questions", "faq": [
            ("What is the best class in WoW: Forever at level 60?", "In our simulation the highest DPS spec is {name} ({dps} DPS, build {build}). The full ranking of the {n} DPS specs is on this page, with the method."),
            ("How are the tiers of this tier list built?", "Each spec is compared with the best one of its role: S from {S}% of its DPS, A from {A}%, B from {B}%, C from {C}%, D below. Nothing is placed by hand."),
            ("Will the tier list change?", "Yes: the game is still in beta and values move with patches. The update date and the game build are shown at the top of the page, and the simulator is rerun after every major change."),
            ("Why are healers not ranked?", "The simulator does not model healing over a full fight yet. Rather than show an invented number, we leave them out for now."),
        ],
        "links_h": "Go further", "l_sim": "Level 60 DPS simulator", "l_calc": "Talent calculator", "l_dung": "Dungeons", "l_mysim": "Simulate my character",
        "art_credit": "Artwork: © Blizzard Entertainment",
    },
}
