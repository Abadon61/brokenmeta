"""World of Warcraft: Forever class/spec guides and profession guides -- data loading and page texts.

Nothing here is invented: a specialization page is built from the talent data (data/wow_talents/, itself read from the beta client
tables) plus the role published by Icy Veins (data/wow_guides/roles.json). A class only gets guide pages when every one of its
specializations has a sourced role. Profession guides come from data/wow_professions/<id>.json (see wow_professions_build.py).
"""
from __future__ import annotations

import json
from pathlib import Path

from markupsafe import Markup

ROOT = Path(__file__).resolve().parent.parent
ROLES_FILE = ROOT / "data" / "wow_guides" / "roles.json"
CONTENT_FILE = ROOT / "data" / "wow_guides" / "content.json"
PROF_DIR = ROOT / "data" / "wow_professions"


def load_guides(wt_classes: list[dict]) -> list[dict]:
    """Classes that have complete, sourced guides: [{'cls': class dict, 'roles': {spec_id: {...}}}]."""
    if not ROLES_FILE.exists():
        return []
    roles = json.loads(ROLES_FILE.read_text(encoding="utf-8"))
    content = json.loads(CONTENT_FILE.read_text(encoding="utf-8")) if CONTENT_FILE.exists() else {}
    out = []
    for c in wt_classes:
        r = roles.get(c["id"])
        if r and all(s["id"] in r for s in c["specs"]):
            out.append({"cls": c, "roles": r, "content": content.get(c["id"], {})})
    return out


def load_professions() -> list[dict]:
    if not PROF_DIR.exists():
        return []
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(PROF_DIR.glob("*.json"))]


def spec_facts(spec: dict) -> dict:
    """Facts read from a spec's talent list (all derived from the client data)."""
    ts = spec["talents"]
    top = max(t["row"] for t in ts)
    top_talents = sorted([t for t in ts if t["row"] == top], key=lambda t: t["col"])
    need = 0
    for t in top_talents:
        for g in (t.get("gates") or []):
            need = max(need, g["points"])
    rows = []
    for r in range(1, top + 1):
        rows.append({"row": r, "talents": sorted([t for t in ts if t["row"] == r], key=lambda t: t["col"])})
    return {"count": len(ts), "points": sum(t["max_rank"] for t in ts), "top_row": top, "top_talents": top_talents, "top_need": need,
            "single": [t for t in sorted(ts, key=lambda t: (t["row"], t["col"])) if t["max_rank"] == 1], "rows": rows}


# geometry of the static talent tree (SVG units; the CSS scales everything with one variable)
TW, TH, GX, GY, ICON, RW = 44, 44, 8, 8, 40, 34


def _as_list(v):
    return v if isinstance(v, list) else ([v] if v else [])


def _tree_svg(sp: dict, flags: dict) -> Markup:
    """Background of a tree: tier rail (tier number + points needed), prerequisite links between talents."""
    rows = max(t["row"] for t in sp["talents"])
    w, h = RW + GX + 4 * TW + 3 * GX, rows * TH + (rows - 1) * GY      # the grid gap sits between the tier rail and column 1
    pos = {t["id"]: (RW + GX + (t["col"] - 1) * (TW + GX) + TW / 2, (t["row"] - 1) * (TH + GY) + ICON / 2) for t in sp["talents"]}
    parts = [f'<svg class="wg-svg" viewBox="0 0 {w} {h}" aria-hidden="true" focusable="false">']
    for r in range(1, rows + 1):
        need = max([g["points"] for t in sp["talents"] if t["row"] == r for g in (t.get("gates") or [])] or [0])
        y = (r - 1) * (TH + GY) + ICON / 2
        parts.append(f'<text class="wg-rail-t" x="{RW - 8}" y="{y - 1:.0f}" text-anchor="end">{r}</text>')
        parts.append(f'<text class="wg-rail-p" x="{RW - 8}" y="{y + 9:.0f}" text-anchor="end">{need}</text>')
    for t in sp["talents"]:
        for key in ("requires", "requires_any"):
            for req in _as_list(t.get(key)):
                src = req["id"] if isinstance(req, dict) else req
                if src not in pos:
                    continue
                (x1, y1), (x2, y2) = pos[src], pos[t["id"]]
                hot = " is-hot" if (src in flags and t["id"] in flags) else ""
                dash = " is-any" if key == "requires_any" else ""
                parts.append(f'<line class="wg-link{hot}{dash}" x1="{x1:.0f}" y1="{y1 + ICON / 2 - 2:.0f}" x2="{x2:.0f}" y2="{y2 - ICON / 2 + 2:.0f}"/>')
    parts.append("</svg>")
    return Markup("".join(parts))


def template_tree(cls: dict, spec: dict, build: dict) -> dict:
    """Static, read-only trees with the recommended talents flagged. A build may use talents of several trees of the class
    (e.g. a Holy Priest guide names Discipline and Shadow talents): one tree is returned per spec that holds at least one, the guide's own spec first."""
    flags = {t["id"]: t for t in build["talents"]}
    where = {t["id"]: (sp, t) for sp in cls["specs"] for t in sp["talents"]}
    missing = [i for i in flags if i not in where]
    assert not missing, f"template talents not found in class {cls['id']}: {missing}"
    order = [spec["id"]] + [sp["id"] for sp in cls["specs"] if sp["id"] != spec["id"]]      # all three trees, the guide's own first
    trees = []
    for sid in order:
        sp = next(x for x in cls["specs"] if x["id"] == sid)
        cells = []
        for t in sorted(sp["talents"], key=lambda t: (t["row"], t["col"])):
            f = flags.get(t["id"])
            cells.append({"t": t, "mark": None if not f else ("option" if f.get("option") else "reco"), "points": (f or {}).get("points")})
        trees.append({"spec": sp, "cells": cells, "rows": max(t["row"] for t in sp["talents"]), "svg": _tree_svg(sp, flags), "own": sid == spec["id"]})
    items = []
    for f in build["talents"]:
        sp, t = where[f["id"]]
        items.append({"t": t, "why": f["why"], "option": bool(f.get("option")), "points": f.get("points"), "tree": sp["name"]})
    return {"trees": trees, "items": items}


def money(copper: int, lang: str) -> str:
    c = int(copper)
    g, s, cu = c // 10000, c % 10000 // 100, c % 100
    u = ("po", "pa", "pc") if lang == "fr" else ("g", "s", "c")
    parts = []
    if g:
        parts.append(f"{g:,}".replace(",", " ") + f" {u[0]}")
    if s:
        parts.append(f"{s} {u[1]}")
    if cu or not parts:
        parts.append(f"{cu} {u[2]}")
    return " ".join(parts)


TXT = {
    "fr": {
        "guides": "Guides de classe", "professions": "Métiers", "kicker": "World of Warcraft: Forever · Guide de classe",
        "hub_title": "Guides de classe WoW: Forever par spécialisation", "hub_desc": "Guides par classe et spécialisation de WoW: Forever : rôle, talents clés et arbre complet, lus dans les données du client bêta.",
        "hub_h1": "Guides de classe de WoW: Forever", "hub_intro": "Un guide par spécialisation : son rôle, les talents qui structurent l'arbre et le détail palier par palier, lus dans les tables du client bêta. Chaque page renvoie vers le calculateur de talents.",
        "soon": "Guide à venir", "specs_word": "Spécialisations", "open_class": "Voir la classe",
        "class_title": "Guides {name} WoW: Forever : spécialisations", "class_desc": "Guides {name} de WoW: Forever : {specs}. Rôle, talents clés et arbre complet de chaque spécialisation.",
        "class_h1": "Guides {name} de WoW: Forever", "class_intro": "Les trois spécialisations du {name} dans WoW: Forever : {specs}. Choisissez une spécialisation pour voir son rôle, ses talents clés et son arbre complet.",
        "spec_title": "{cls} {spec} WoW: Forever : guide et talents", "spec_desc": "Guide {cls} {spec} de WoW: Forever : {role}, talents du dernier palier et arbre complet, lus dans les données du client bêta.",
        "spec_desc_short": "Guide {cls} {spec} de WoW: Forever : {role}, talents et arbre complet.",
        "spec_h1": "{cls} {spec} : guide de spécialisation", "spec_intro": "{spec} est la spécialisation « {role} » du {cls} dans WoW: Forever. Cette page résume son arbre de talents tel qu'il figure dans le client bêta (build {build}) ; le rôle est celui indiqué par le guide Icy Veins de la spécialisation.",
        "facts_h2": "En bref", "f_class": "Classe", "f_role": "Rôle", "f_talents": "Talents dans l'arbre", "f_points": "Points maximum dans l'arbre", "f_top": "Palier le plus haut", "f_need": "Points nécessaires pour le dernier palier", "f_build": "Données",
        "top_h2": "Les talents du dernier palier", "top_p": "Ce sont les talents les plus profonds de l'arbre : ils demandent d'avoir déjà investi {need} points dans la spécialisation. Textes officiels du jeu, au rang maximum.",
        "single_h2": "Les talents à rang unique", "single_p": "Talents qui ne se prennent qu'une fois, avec leur palier (textes officiels au rang maximum).",
        "tree_h2": "L'arbre palier par palier", "tree_p": "Chaque ligne est un palier de l'arbre ; entre parenthèses, le nombre de rangs maximum du talent.", "row_word": "Palier",
        "cta": "Ouvrir {cls} dans le calculateur de talents", "cta_p": "Répartissez vos 51 points, comparez les trois spécialisations et partagez votre build par lien.",
        "others_h2": "Les autres spécialisations du {cls}", "sources": "Sources", "src_role": "Rôle : ", "src_data": "Talents : ",
        "note": "Cette page ne donne ni rotation ni priorité de sorts : le client ne les fournit pas et nous ne les inventons pas. Les données changeront avec la sortie du jeu le 4 novembre 2026.",
        "rank_word": "rang", "ranks_word": "rangs",
        "tpl_h2": "Le template de talents (niveau {level})", "tpl_p": "Les trois arbres de la classe, avec les talents que le guide Icy Veins recommande au niveau {level} en couleur et tous les autres en grisé. Le chiffre à gauche de chaque ligne est le nombre de points à avoir dépensé dans l'arbre pour y accéder. Quand le guide indique un nombre de points, il est précisé ; sinon seuls les talents sont cités. Cette section est figée : elle ne bouge pas et ne dépend pas du calculateur.",
        "tpl_reco": "Recommandé", "tpl_option": "Au choix", "tpl_tier": "Palier", "pts_word": "pts", "tree_word": "Arbre", "tree_own": "ce guide",
        "stats_h2": "Priorité de stats", "stats_p": "Dans l'ordre d'importance, d'après Icy Veins.", "stats_spec": "Ordre présenté comme spéculatif par Icy Veins.",
        "cons_h2": "Consommables", "cons_p": "Ce que le guide Icy Veins cite pour cette spécialisation.", "prof_h2": "Métiers conseillés",
        "gear_h2": "Équipement, enchantements et objets de donjon", "gear_p": "Aucune source ne publie encore de liste d'équipement (BiS), d'enchantements ni d'objets de donjon pour cette spécialisation : les guides Icy Veins de Forever se limitent pour l'instant au niveau 20 et ne les détaillent pas. Cette section sera remplie quand une source les publiera, sans invention de notre part.",
        "updated": "Guide Icy Veins daté du {date}, lu le 21 septembre 2026.",
        "p_hub_title": "Guides de métiers WoW: Forever : monter au max", "p_hub_desc": "Guides de métiers de WoW: Forever : parcours de 1 à 300 au moindre coût, liste de courses, recettes et plans.",
        "p_hub_h1": "Guides de métiers de WoW: Forever", "p_hub_intro": "Pour chaque métier : la suite de recettes la moins chère pour monter de 1 à 300, la liste de courses complète, l'origine de chaque plan et la table de toutes les recettes.",
        "p_kicker": "World of Warcraft: Forever · Métier",
        "p_title": "{name} WoW: Forever : monter de 1 à 300 à petit prix", "p_desc": "Guide {name} de WoW: Forever : parcours de 1 à 300 le moins cher, liste de courses, origine des plans et toutes les recettes.",
        "p_h1": "{name} : monter de 1 à 300 au moindre coût", "p_intro": "Le parcours ci-dessous passe de 1 à 300 en {crafts} créations, uniquement avec des recettes qui donnent un point de compétence à coup sûr, pour environ {total}. Il est calculé à partir des recettes, des composants et des prix de la base de données Wowhead Forever et des tables du client bêta.",
        "sum_h2": "Le résumé", "s_total": "Coût total estimé", "s_reag": "Composants", "s_plans": "Recettes et plans", "s_ranks": "Rangs du formateur", "s_crafts": "Créations à faire", "s_vendor": "Achetés chez un vendeur", "s_farm": "À récolter (valeur de revente)",
        "how_h2": "Comment ce parcours est calculé", "how": [
            "On ne garde que les recettes affichées en orange à votre niveau de compétence : une recette orange donne un point de compétence à chaque création.",
            "Une recette est utilisable si un formateur l'enseigne ou si son plan est vendu par un vendeur. Le prix du plan est ajouté une seule fois.",
            "Un composant vendu par un vendeur est compté à son prix d'achat. Un composant à récolter ou à obtenir autrement (herbes, drops) est compté à sa valeur de revente au vendeur : la bêta n'a pas encore de prix à l'hôtel des ventes, c'est donc un plancher, pas un prix de marché.",
            "Les recettes dont un composant n'a pas de prix fiable (composants fabriqués, objets de quête) sont écartées, ainsi que les transmutations, dont un éventuel temps de recharge en Forever n'est pas indiqué dans les données.",
            "Un calcul de plus court chemin de 1 à 300 choisit ensuite la suite la moins chère en payant chaque recette une seule fois.",
        ],
        "route_h2": "Le parcours pas à pas", "route_p": "Faites {n} créations de chaque recette dans l'ordre. Les coûts sont en argent du jeu.",
        "c_skill": "Compétence", "c_recipe": "Recette", "c_crafts": "Créations", "c_reagents": "Composants (par création)", "c_cost": "Coût des composants", "c_get": "Où l'obtenir",
        "get_trainer": "Formateur : {cost}", "get_vendor": "Plan vendu par {npc} : {cost}", "get_vendor_many": "Plan vendu par des vendeurs : {cost}", "get_start": "Connue au départ (à confirmer en bêta)",
        "shop_h2": "La liste de courses complète", "shop_p": "Tous les composants du parcours, du plus cher au moins cher.", "m_item": "Composant", "m_qty": "Quantité", "m_unit": "Prix unitaire", "m_total": "Total", "m_kind": "Origine",
        "kind_vendor": "Vendeur", "kind_farm": "À récolter",
        "ranks_h2": "Les rangs du métier chez le formateur", "ranks_p": "Chaque rang relève le plafond de compétence. Les descriptions viennent du client bêta.", "r_rank": "Rang", "r_cap": "Plafond", "r_at": "À partir de", "r_cost": "Prix",
        "rank_names": {"Apprentice": "Apprenti", "Journeyman": "Compagnon", "Expert": "Expert", "Artisan": "Artisan"},
        "all_h2": "Toutes les recettes", "all_p": "Les recettes de {name} avec leurs paliers de couleur (orange, jaune, vert, gris), leurs composants et leur origine. Les plans obtenus par drop, quête ou pêche ne sont pas dans le parcours faute d'un moyen fiable de les obtenir.",
        "a_recipe": "Recette", "a_colors": "Couleurs", "a_makes": "Crée", "a_get": "Origine",
        "get_other": "Drop, quête ou autre", "kinds": {"drop": "drop", "quest": "quête", "fished": "pêche", "pickpocket": "vol à la tire", "vendor": "vendeur"},
        "limits_h2": "Ce que les données ne disent pas", "limits": [
            "Aucun prix de l'hôtel des ventes n'existe encore en bêta : le coût des composants à récolter est sa valeur de revente, pas le prix de marché. Le vrai coût sera souvent différent.",
            "Les recettes dont l'origine est un drop, une quête ou la pêche ne sont pas prises en compte, même si elles pourraient raccourcir le parcours.",
            "Deux recettes de départ n'ont aucune source indiquée : elles sont comptées comme connues dès le début, à confirmer en bêta.",
            "Les valeurs peuvent changer avec le jeu final, le 4 novembre 2026.",
        ],
        "sources_wh": "Wowhead — base de données Forever : {name}", "sources_client": "Tables du client bêta (build {build}), publiées par wago.tools",
        "prof_soon": "Guide à venir", "name_col": "Nom",
    },
    "en": {
        "guides": "Class guides", "professions": "Professions", "kicker": "World of Warcraft: Forever · Class guide",
        "hub_title": "WoW: Forever class guides by specialization", "hub_desc": "WoW: Forever guides for every class and specialization: role, key talents and the full tree, read from the beta client data.",
        "hub_h1": "WoW: Forever class guides", "hub_intro": "One guide per specialization: its role, the talents that shape the tree and the full tier-by-tier breakdown, read from the beta client tables. Every page links to the talent calculator.",
        "soon": "Guide coming soon", "specs_word": "Specializations", "open_class": "View class",
        "class_title": "{name} guides WoW: Forever: specializations", "class_desc": "WoW: Forever {name} guides: {specs}. Role, key talents and the full tree of each specialization.",
        "class_h1": "WoW: Forever {name} guides", "class_intro": "The three {name} specializations in WoW: Forever: {specs}. Pick one to see its role, key talents and full tree.",
        "spec_title": "{spec} {cls} WoW: Forever: guide and talents", "spec_desc": "WoW: Forever {spec} {cls} guide: {role}, last-tier talents and the full tree, read from the beta client data.",
        "spec_desc_short": "WoW: Forever {spec} {cls} guide: {role}, talents and the full tree.",
        "spec_h1": "{spec} {cls}: specialization guide", "spec_intro": "{spec} is the {role} specialization of the {cls} in WoW: Forever. This page summarizes its talent tree as it appears in the beta client (build {build}); the role is the one stated by the Icy Veins guide for the specialization.",
        "facts_h2": "At a glance", "f_class": "Class", "f_role": "Role", "f_talents": "Talents in the tree", "f_points": "Maximum points in the tree", "f_top": "Highest tier", "f_need": "Points needed for the last tier", "f_build": "Data",
        "top_h2": "The last-tier talents", "top_p": "These are the deepest talents in the tree: they require {need} points already spent in the specialization. Official game text, at maximum rank.",
        "single_h2": "Single-rank talents", "single_p": "Talents you take only once, with their tier (official text at maximum rank).",
        "tree_h2": "The tree tier by tier", "tree_p": "Each line is a tier of the tree; in brackets, the talent's maximum rank.", "row_word": "Tier",
        "cta": "Open {cls} in the talent calculator", "cta_p": "Spend your 51 points, compare the three specializations and share your build by link.",
        "others_h2": "Other {cls} specializations", "sources": "Sources", "src_role": "Role: ", "src_data": "Talents: ",
        "note": "This page gives no rotation or spell priority: the client does not provide them and we do not invent them. The data will change when the game launches on November 4, 2026.",
        "rank_word": "rank", "ranks_word": "ranks",
        "tpl_h2": "Talent template (level {level})", "tpl_p": "The class's three trees, with the talents the Icy Veins guide recommends at level {level} in colour and all the others in grey. The small number on the left of each row is the points you must have spent in the tree to reach it. Point counts are shown when the guide states them; otherwise only the talents are named. This section is fixed: it does not move and does not depend on the calculator.",
        "tpl_reco": "Recommended", "tpl_option": "Optional", "tpl_tier": "Tier", "pts_word": "pts", "tree_word": "Tree", "tree_own": "this guide",
        "stats_h2": "Stat priority", "stats_p": "In order of importance, according to Icy Veins.", "stats_spec": "Order presented as speculative by Icy Veins.",
        "cons_h2": "Consumables", "cons_p": "What the Icy Veins guide lists for this specialization.", "prof_h2": "Suggested professions",
        "gear_h2": "Gear, enchants and dungeon items", "gear_p": "No source publishes a best-in-slot list, enchants or dungeon items for this specialization yet: the Icy Veins Forever guides only cover level 20 for now and do not detail them. This section will be filled when a source publishes them, with nothing invented on our side.",
        "updated": "Icy Veins guide dated {date}, read on September 21, 2026.",
        "p_hub_title": "WoW: Forever profession guides: level fast", "p_hub_desc": "WoW: Forever profession guides: the cheapest 1-300 route, a full shopping list, recipes and plans.",
        "p_hub_h1": "WoW: Forever profession guides", "p_hub_intro": "For each profession: the cheapest recipe sequence from 1 to 300, the full shopping list, where each plan comes from and a table of every recipe.",
        "p_kicker": "World of Warcraft: Forever · Profession",
        "p_title": "{name} WoW: Forever: 1 to 300 on the cheap", "p_desc": "WoW: Forever {name} guide: the cheapest 1-300 route, shopping list, where the plans come from and every recipe.",
        "p_h1": "{name}: 1 to 300 at the lowest cost", "p_intro": "The route below goes from 1 to 300 in {crafts} crafts, using only recipes that are guaranteed to give a skill point, for about {total}. It is computed from the recipes, reagents and prices of the Wowhead Forever database and the beta client tables.",
        "sum_h2": "Summary", "s_total": "Estimated total cost", "s_reag": "Reagents", "s_plans": "Recipes and plans", "s_ranks": "Trainer ranks", "s_crafts": "Crafts to make", "s_vendor": "Bought from a vendor", "s_farm": "To gather (resale value)",
        "how_h2": "How this route is computed", "how": [
            "Only recipes shown in orange at your skill level are kept: an orange recipe gives a skill point on every craft.",
            "A recipe is usable if a trainer teaches it or if its plan is sold by a vendor. The plan's price is added once.",
            "A reagent sold by a vendor is counted at its purchase price. A reagent you gather or obtain otherwise (herbs, drops) is counted at its vendor resale value: the beta has no auction house prices yet, so this is a floor, not a market price.",
            "Recipes with a reagent that has no reliable price (crafted reagents, quest items) are left out, and so are transmutes, whose possible cooldown in Forever is not shown in the data.",
            "A shortest-path calculation from 1 to 300 then picks the cheapest sequence, paying for each recipe once.",
        ],
        "route_h2": "The route, step by step", "route_p": "Make {n} crafts of each recipe, in order. Costs are in in-game money.",
        "c_skill": "Skill", "c_recipe": "Recipe", "c_crafts": "Crafts", "c_reagents": "Reagents (per craft)", "c_cost": "Reagent cost", "c_get": "Where to get it",
        "get_trainer": "Trainer: {cost}", "get_vendor": "Plan sold by {npc}: {cost}", "get_vendor_many": "Plan sold by vendors: {cost}", "get_start": "Known from the start (to confirm in beta)",
        "shop_h2": "The full shopping list", "shop_p": "Every reagent of the route, most expensive first.", "m_item": "Reagent", "m_qty": "Quantity", "m_unit": "Unit price", "m_total": "Total", "m_kind": "Source",
        "kind_vendor": "Vendor", "kind_farm": "Gather",
        "ranks_h2": "Profession ranks at the trainer", "ranks_p": "Each rank raises the skill cap. Descriptions come from the beta client.", "r_rank": "Rank", "r_cap": "Cap", "r_at": "From skill", "r_cost": "Price",
        "rank_names": {"Apprentice": "Apprentice", "Journeyman": "Journeyman", "Expert": "Expert", "Artisan": "Artisan"},
        "all_h2": "Every recipe", "all_p": "All {name} recipes with their colour thresholds (orange, yellow, green, grey), reagents and origin. Plans that drop, come from quests or fishing are not in the route because there is no reliable way to get them.",
        "a_recipe": "Recipe", "a_colors": "Colours", "a_makes": "Creates", "a_get": "Origin",
        "get_other": "Drop, quest or other", "kinds": {"drop": "drop", "quest": "quest", "fished": "fishing", "pickpocket": "pickpocket", "vendor": "vendor"},
        "limits_h2": "What the data does not say", "limits": [
            "No auction house prices exist in the beta yet: the cost of gathered reagents is their resale value, not a market price. The real cost will often differ.",
            "Recipes that come from drops, quests or fishing are not considered, even if they could shorten the route.",
            "Two starting recipes have no source listed: they are counted as known from the start, to confirm in beta.",
            "Values may change with the final game on November 4, 2026.",
        ],
        "sources_wh": "Wowhead — Forever database: {name}", "sources_client": "Beta client tables (build {build}), published by wago.tools",
        "prof_soon": "Guide coming soon", "name_col": "Name",
    },
}
