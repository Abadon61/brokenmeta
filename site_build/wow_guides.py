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
DUNGEON_FILE = ROOT / "data" / "wow_dungeons" / "dungeons.json"
RAID_FILE = ROOT / "data" / "wow_raids" / "raids.json"


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
    return sorted((json.loads(p.read_text(encoding="utf-8")) for p in PROF_DIR.glob("*.json")), key=lambda d: d.get("order", 99))


def load_dungeons() -> dict | None:
    return json.loads(DUNGEON_FILE.read_text(encoding="utf-8")) if DUNGEON_FILE.exists() else None


def load_raids() -> dict | None:
    return json.loads(RAID_FILE.read_text(encoding="utf-8")) if RAID_FILE.exists() else None


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
        "gear_h2": "Équipement complet et enchantements", "gear_p": "Aucune source ne publie encore de liste d'équipement (BiS) ni d'enchantements pour cette spécialisation : les guides Icy Veins de Forever se limitent pour l'instant au niveau 20 et ne les détaillent pas. Les pages de donjons permettent de parcourir le butin par type d'objet et par stats, sans classement par spécialisation : c'est à vous de choisir ce qui compte pour votre classe.",
        "updated": "Guide Icy Veins daté du {date}, lu le 21 septembre 2026.",
        "p_hub_title": "Guides de métiers WoW: Forever : monter au max", "p_hub_desc": "Guides de métiers de WoW: Forever : parcours de 1 à 300 au moindre coût, liste de courses, recettes et plans.",
        "p_hub_h1": "Guides de métiers de WoW: Forever", "p_hub_intro": "Pour chaque métier : la suite de recettes la moins chère pour monter de 1 à 300, la liste de courses complète, l'origine de chaque plan et la table de toutes les recettes.",
        "p_kicker": "World of Warcraft: Forever · Métier",
        "p_title": "{name} WoW: Forever : monter de 1 à 300 à petit prix", "p_desc": "Guide {name} de WoW: Forever : parcours de 1 à 300 le moins cher, liste de courses, origine des plans et toutes les recettes.",
        "p_h1": "{name} : monter de 1 à 300 au moindre coût", "p_title_short": "{name} WoW: Forever : de 1 à 300 à petit prix",
        "p_intro": "Le parcours ci-dessous passe de 1 à {cap} en au moins {crafts} créations. Il est calculé à partir des recettes, des composants et des prix de la base de données Wowhead Forever et des tables du client bêta. Les coûts en or des composants ne sont pas affichés : ils dépendront des prix de l'hôtel des ventes, qui n'existent pas encore en bêta. {risk}",
        "risk_none": "Tous les points viennent de recettes orange : ils sont garantis.",
        "risk_some": "{n} de ces points viennent de recettes jaunes ou vertes, sans garantie de gain : il faudra probablement plus de créations que le minimum indiqué.",
        "risk_note": "* Étape avec des points non garantis (recette jaune ou verte) : le nombre de créations est un minimum.",
        "s_risky": "Points non garantis", "s_cost": "Coût en or des composants", "s_cost_wait": "À venir (prix de l'hôtel des ventes)", "m_vprice": "Prix chez le vendeur", "m_none": "—", "s_unknown": "Plans à trouver (prix inconnu)", "rank_quest": "Quête ou livre (prix non indiqué)",
        "kinds_price": {"vendor": "Vendeur", "farm": "À récolter", "craft": "À fabriquer", "disenchant": "Désenchantement"},
        "sum_h2": "Le résumé", "s_total": "Coût total estimé", "s_reag": "Composants", "s_plans": "Recettes et plans", "s_ranks": "Rangs du formateur", "s_crafts": "Créations à faire", "s_vendor": "Achetés chez un vendeur", "s_farm": "À récolter (valeur de revente)",
        "how_h2": "Comment ce parcours est calculé", "how": [
            "On privilégie les recettes affichées en orange à votre niveau de compétence : une recette orange donne un point de compétence à chaque création. Les recettes jaunes ou vertes ne servent qu'à combler un trou quand aucune recette orange ne couvre le niveau, et sont signalées par un astérisque.",
            "Une recette est utilisable si un formateur l'enseigne ou si son plan est vendu par un vendeur ; le prix du plan est ajouté une seule fois. Un plan obtenu par drop ou quête n'est retenu qu'en dernier recours, marqué « plan à trouver ».",
            "Pour choisir la suite la moins chère, un composant vendu par un vendeur est compté à son prix d'achat, et un composant à récolter, fabriquer ou désenchanter à sa valeur de revente au vendeur : c'est un repère provisoire, la bêta n'a pas de prix à l'hôtel des ventes. Ces montants ne sont pas affichés.",
            "Les recettes dont un composant n'a pas de prix fiable (objets de quête, objets absents de la liste des matériaux) sont écartées, ainsi que les transmutations, dont un éventuel temps de recharge en Forever n'est pas indiqué dans les données.",
            "Un calcul de plus court chemin de 1 au plafond choisit ensuite la suite la moins chère en payant chaque recette une seule fois.",
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
            "Aucun prix de l'hôtel des ventes n'existe encore en bêta : la suite de recettes est choisie avec un repère provisoire et aucun coût en or n'est affiché. Elle sera recalculée avec les vrais prix.",
            "Le nombre de créations est un minimum : les points issus de recettes jaunes ou vertes ne sont pas garantis, et la chance de gain n'est pas indiquée par les données.",
            "Les outils requis par certaines recettes (marteau, canne d'enchanteur, etc.) ne sont pas comptés dans le coût.",
            "Les recettes de départ sans source indiquée sont comptées comme connues dès le début, à confirmer en bêta.",
            "Les valeurs peuvent changer avec le jeu final, le 4 novembre 2026.",
        ],
        "limit_disenchant": "Les matériaux d'enchantement (poussières, essences, éclats) viennent du désenchantement d'objets : leur valeur de revente dans les tables est symbolique, donc le parcours ne peut pas en tenir compte fidèlement.",
        "sources_wh": "Wowhead — base de données Forever : {name}", "sources_client": "Tables du client bêta (build {build}), publiées par wago.tools",
        "prof_soon": "Guide à venir", "name_col": "Nom",
        "stat_names": {"str": "Force", "agi": "Agilité", "int": "Intelligence", "spi": "Esprit", "sta": "Endurance", "splpwr": "Puissance des sorts", "spldmg": "Dégâts des sorts",
                       "atkpwr": "Puissance d'attaque", "manargn": "Mp5", "critstrkrtng": "Coup critique", "hastertng": "Hâte", "hitrtng": "Toucher", "defrtng": "Défense", "armor": "Armure"},
        "dg_title_hub": "Objets de donjon WoW: Forever : type et stats", "dg_desc_hub": "Le butin de chaque donjon de WoW: Forever, filtrable par type d'objet, stat principale et stats secondaires.",
        "dg_h1_hub": "Objets de donjon de WoW: Forever", "dg_intro_hub": "Le butin de chaque donjon, avec les vraies stats de Forever. Filtrez par type d'objet et par stats pour retrouver ce qui compte pour votre classe : le site ne devine pas à votre place ce qui est bon pour votre spécialisation.",
        "dg_kicker": "World of Warcraft: Forever · Donjons", "dg_levels": "Niveaux", "dg_items_n": "objets", "dg_title": "{name} WoW: Forever : objets et butin", "dg_desc": "Butin de {name} dans WoW: Forever : objets équipables avec leurs stats, filtrables par type et par stats.",
        "dg_h1": "{name} : objets et stats", "dg_intro": "Les objets équipables de {name} ({levels}), avec leurs stats réelles dans Forever. Filtrez par type d'objet, stat principale et stats secondaires.", "dg_intro_nolvl": "Les objets équipables de {name}, avec leurs stats réelles dans Forever. Filtrez par type d'objet, stat principale et stats secondaires.",
        "dg_filter_type": "Type d'objet", "dg_filter_primary": "Stat principale", "dg_filter_secondary": "Stats secondaires (l'objet doit avoir toutes celles cochées)",
        "dg_filter_level": "Niveau requis", "dg_level_min": "Min", "dg_level_max": "Max",
        "dg_reset": "Réinitialiser", "dg_none": "Aucun objet ne correspond aux filtres choisis.", "dg_count": "{shown} objet(s) affiché(s) sur {total}",
        "dg_slot": "Emplacement", "dg_item": "Objet", "dg_type": "Type", "dg_req": "Niveau requis", "dg_stats": "Stats", "dg_from": "Butin", "dg_quest": "Récompense de quête", "dg_dungeon": "Donjon",
        "dg_all_title": "Tous les objets des donjons WoW: Forever", "dg_all_desc": "Tous les objets équipables des donjons de WoW: Forever réunis sur une page, filtrables par type d'objet, stat principale et stats secondaires.",
        "dg_all_h1": "Tous les objets des donjons", "dg_all_intro": "Le butin des {n} donjons répertoriés, réuni sur une seule page. Filtrez par type d'objet, stat principale et stats secondaires ; chaque objet indique le donjon d'où il vient.",
        "dg_all_card": "Tous les objets des donjons", "dg_all_card_n": "objets, tous donjons",
        "dg_method_h2": "Comment utiliser cette page", "dg_method": [
            "Cette page ne classe pas les objets par classe ni par spécialisation : elle affiche les stats réelles de chaque objet, lues dans les données de Forever, et vous laisse choisir ce qui compte pour vous.",
            "Cochez le ou les types d'objets qui correspondent à ce que votre classe peut équiper (par exemple Mailles), une stat principale (Force, Agilité ou Intelligence) et les stats secondaires recherchées.",
            "Un classement automatique par spécialisation donnerait une fausse impression de précision : il ignore les bonus de set, les effets des trinkets, la vitesse des armes et le poids réel de chaque stat, qui varient d'une spécialisation à l'autre et ne sont pas dans les données publiques.",
            "Les noms d'objets sont en anglais : leur traduction française n'est pas dans les données récupérées.",
        ],
        "dg_src": "Butin et stats des objets : ", "dg_src2": "Types d'armure et d'arme : ",
        "rd_kicker": "World of Warcraft: Forever · Raids", "rd_title_hub": "Raids WoW: Forever : boss et butin", "rd_desc_hub": "Le butin et les boss de chaque raid de WoW: Forever, avec le même filtre par type et par stats que les donjons.",
        "rd_h1_hub": "Raids de WoW: Forever", "rd_intro_hub": "Le butin et les boss de chaque raid répertorié. Ce contenu de fin de partie n'a probablement pas encore été terminé en bêta : l'attribution du butin par boss reste souvent incomplète chez Wowhead.",
        "rd_bosses_n": "boss", "rd_title": "{name} WoW: Forever : boss et butin", "rd_desc": "Boss et butin de {name} dans WoW: Forever, filtrables par type d'objet et par stats.",
        "rd_h1": "{name} : boss et butin", "rd_intro": "Les boss de {name} et leur butin confirmé, plus l'ensemble des objets du raid filtrables par type et par stats.",
        "rd_gallery_h2": "Le lieu", "rd_gallery_p": "Captures d'écran réelles du raid, prises en jeu.",
        "rd_access_h2": "Accès", "rd_level": "Niveau requis", "rd_players": "Joueurs", "rd_territory": "Territoire", "rd_location": "Emplacement",
        "rd_patch": "Ajouté en patch", "rd_attunement": "Quête d'accès", "rd_attunement_lvl": "dès le niveau {lvl}", "rd_no_attunement": "Aucune quête d'accès connue : le raid s'ouvre à l'entrée.",
        "rd_bosses_h2": "Les boss", "rd_bosses_p": "La liste et l'ordre des boss viennent de la fiche du raid sur Wowhead (le classement « boss », une valeur distincte des simples ennemis d'élite, n'existe que pour les raids). Le butin affiché sous chaque boss est celui que Wowhead attribue nommément à ce boss.",
        "rd_boss_none": "Aucun objet attribué nommément à ce boss dans les données actuelles.",
        "rd_boss_type": "Type", "rd_boss_abilities": "Capacités connues", "rd_boss_no_abilities": "Aucune capacité recensée pour le moment dans les données récupérées.",
        "rd_attribution_note": "Ce raid est du contenu de niveau 60 : il n'a probablement pas encore été terminé pendant cette bêta de bas niveau, donc l'attribution du butin par boss reste incomplète chez Wowhead. Le reste du butin du raid est listé plus bas, filtrable comme pour un donjon.",
        "rd_all_h2": "Tout le butin du raid", "rd_all_p": "Tous les objets équipables du raid, y compris ceux sans boss d'origine confirmé, avec leurs vraies stats dans Forever.",
        "rd_unattributed": "Boss non confirmé",
        "rd_method": [
            "Un boss est une créature classée « boss » par Wowhead (une catégorie distincte des ennemis d'élite ordinaires), et non une créature nommée au hasard.",
            "L'ordre des boss et leurs capacités connues viennent de la fiche de chaque boss sur Wowhead (données du jeu réel : ce raid existe depuis WoW Classic et partage la même zone et les mêmes créatures que Forever).",
            "Le butin d'un boss est celui que Wowhead lui attribue nommément. Beaucoup d'objets de raid n'ont pas encore cette attribution dans les données de la bêta.",
            "Comme pour les donjons, cette page ne classe pas les objets par classe ni par spécialisation et ne propose ni carte ni stratégie détaillée : aucune source fiable ne les documente pour Forever.",
            "Les noms d'objets, de capacités et de la quête d'accès sont en anglais : leur traduction française n'est pas dans les données récupérées.",
        ],
        "op_kicker": "World of Warcraft: Forever · Optimisation", "op_title": "Optimisation de personnage WoW: Forever", "op_desc": "Choisissez votre type d'armure et vos stats, puis retrouvez les meilleurs objets par emplacement parmi les donjons et raids de WoW: Forever.",
        "op_h1": "Optimisation de personnage", "op_intro": "Cliquez un emplacement d'équipement pour choisir un objet parmi ceux des donjons et raids catalogués, filtrable par type et par stats. Construisez votre équipement complet et suivez le total de vos stats, sans classement caché par spécialisation.",
        "op_reset_build": "Réinitialiser l'équipement", "op_share": "Partager", "op_share_copied": "Lien copié !",
        "op_summary_h2": "Total des stats", "op_summary_empty": "Choisissez des objets pour voir le total de vos stats.",
        "op_close": "Fermer", "op_search_placeholder": "Rechercher un objet...", "op_remove_item": "Retirer l'objet",
        "op_choose_for": "Choisir : {slot}", "op_picker_count": "{n} objet(s)",
        "op_slot_empty": "Aucun objet connu pour cet emplacement dans les donjons et raids catalogués.",
        "op_slot_none": "Aucun objet ne correspond à ces filtres.",
        "op_source_dungeon": "Donjon : {name}", "op_source_raid": "Raid : {name}", "op_source_raid_boss": "Raid : {name} (boss : {boss})",
        "op_item_level": "Niv. objet {lvl}",
        "op_choose_race": "Choisir une race", "op_alliance": "Alliance", "op_horde": "Horde", "op_remove_race": "Retirer la race",
        "op_race_credit": "Icônes de race : ",
        "op_choose_class": "Choisir une classe", "op_remove_class": "Retirer la classe",
        "op_level1_note": "Inclut les stats de départ (niveau 1) de la race et de la classe choisies : la vraie race + classe, mais sans les courbes de progression jusqu'au niveau 60, absentes des données publiques.",
        "op_stats_credit": "Stats de base par race et par classe : ",
        "op_completion": "{filled}/{total} emplacements équipés",
        "op_avg_ilvl": "Niveau d'objet moyen : {lvl}",
        "op_sort_by": "Trier par", "op_sort_name": "Nom", "op_sort_ilvl": "Niveau d'objet",
        "op_upgrade_badge": "Amélioration", "op_current_badge": "Déjà équipé",
        "op_vs_current": "vs objet équipé : ",
        "op_method_h2": "Comment utiliser cette page",
        "op_method": [
            "Cliquez un emplacement pour ouvrir la liste des objets de donjon et de raid qui peuvent s'y placer, avec les mêmes filtres que sur les pages donjon et raid : type d'objet, stat principale, stats secondaires et niveau requis.",
            "Cette page ne choisit pas d'objet à votre place et ne classe rien par spécialisation : elle affiche les vraies stats de chaque objet et vous laisse comparer et construire votre équipement.",
            "Le total de stats en bas de page est la somme brute des objets choisis : il ne tient pas compte des bonus de set ni des effets spéciaux, absents des données publiques.",
            "Un objet qui existe à la fois en donjon et en raid n'apparaît qu'une fois, avec toutes ses sources listées.",
            "Le bouton Partager encode votre équipement dans le lien de la page : envoyez-le tel quel pour le montrer à quelqu'un d'autre.",
        ],
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
        "gear_h2": "Full gear and enchants", "gear_p": "No source publishes a best-in-slot list or enchants for this specialization yet: the Icy Veins Forever guides only cover level 20 for now and do not detail them. The dungeon pages let you browse loot by item type and stats, with no per-specialization ranking: it's up to you to pick what matters for your class.",
        "updated": "Icy Veins guide dated {date}, read on September 21, 2026.",
        "p_hub_title": "WoW: Forever profession guides: level fast", "p_hub_desc": "WoW: Forever profession guides: the cheapest 1-300 route, a full shopping list, recipes and plans.",
        "p_hub_h1": "WoW: Forever profession guides", "p_hub_intro": "For each profession: the cheapest recipe sequence from 1 to 300, the full shopping list, where each plan comes from and a table of every recipe.",
        "p_kicker": "World of Warcraft: Forever · Profession",
        "p_title": "{name} WoW: Forever: 1 to 300 on the cheap", "p_desc": "WoW: Forever {name} guide: the cheapest 1-300 route, shopping list, where the plans come from and every recipe.",
        "p_h1": "{name}: 1 to 300 at the lowest cost", "p_title_short": "{name} WoW: Forever: 1 to 300 cheaply",
        "p_intro": "The route below goes from 1 to {cap} in at least {crafts} crafts. It is computed from the recipes, reagents and prices of the Wowhead Forever database and the beta client tables. The gold cost of the reagents is not shown: it will depend on auction house prices, which do not exist in the beta yet. {risk}",
        "risk_none": "Every point comes from an orange recipe, so all are guaranteed.",
        "risk_some": "{n} of these points come from yellow or green recipes, which do not guarantee a gain: you will probably need more crafts than the minimum shown.",
        "risk_note": "* Step with non-guaranteed points (yellow or green recipe): the number of crafts is a minimum.",
        "s_risky": "Non-guaranteed points", "s_cost": "Gold cost of reagents", "s_cost_wait": "Coming (auction house prices)", "m_vprice": "Vendor price", "m_none": "—", "s_unknown": "Plans to find (unknown price)", "rank_quest": "Quest or book (price not listed)",
        "kinds_price": {"vendor": "Vendor", "farm": "Gather", "craft": "Craft", "disenchant": "Disenchanting"},
        "sum_h2": "Summary", "s_total": "Estimated total cost", "s_reag": "Reagents", "s_plans": "Recipes and plans", "s_ranks": "Trainer ranks", "s_crafts": "Crafts to make", "s_vendor": "Bought from a vendor", "s_farm": "To gather (resale value)",
        "how_h2": "How this route is computed", "how": [
            "Recipes shown in orange at your skill level are preferred: an orange recipe gives a skill point on every craft. Yellow or green recipes are only used to bridge a stretch that no orange recipe covers, and are marked with an asterisk.",
            "A recipe is usable if a trainer teaches it or if its plan is sold by a vendor; the plan's price is added once. A plan that drops or comes from a quest is only kept as a last resort, marked 'plan to find'.",
            "To pick the cheapest sequence, a reagent sold by a vendor is counted at its purchase price, and one you gather, craft or disenchant at its vendor resale value: this is a provisional yardstick, since the beta has no auction house prices. These amounts are not shown.",
            "Recipes with a reagent that has no reliable price (quest items, items missing from the trade goods list) are left out, and so are transmutes, whose possible cooldown in Forever is not shown in the data.",
            "A shortest-path calculation from 1 to the cap then picks the cheapest sequence, paying for each recipe once.",
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
            "No auction house prices exist in the beta yet: the sequence of recipes is chosen with a provisional yardstick and no gold cost is shown. It will be recomputed with real prices.",
            "The number of crafts is a minimum: points from yellow or green recipes are not guaranteed, and the data does not give the chance of a gain.",
            "Tools required by some recipes (hammer, enchanter's rod, etc.) are not counted in the cost.",
            "Starting recipes with no source listed are counted as known from the start, to confirm in beta.",
            "Values may change with the final game on November 4, 2026.",
        ],
        "limit_disenchant": "Enchanting materials (dusts, essences, shards) come from disenchanting items: their vendor value in the tables is a token amount, so the route cannot account for them faithfully.",
        "sources_wh": "Wowhead — Forever database: {name}", "sources_client": "Beta client tables (build {build}), published by wago.tools",
        "prof_soon": "Guide coming soon", "name_col": "Name",
        "stat_names": {"str": "Strength", "agi": "Agility", "int": "Intellect", "spi": "Spirit", "sta": "Stamina", "splpwr": "Spell Power", "spldmg": "Spell damage",
                       "atkpwr": "Attack Power", "manargn": "Mp5", "critstrkrtng": "Critical Strike", "hastertng": "Haste", "hitrtng": "Hit", "defrtng": "Defense", "armor": "Armor"},
        "dg_title_hub": "WoW: Forever dungeon items: type and stats", "dg_desc_hub": "The loot of every WoW: Forever dungeon, filterable by item type, primary stat and secondary stats.",
        "dg_h1_hub": "WoW: Forever dungeon items", "dg_intro_hub": "The loot of every dungeon, with the real Forever stats. Filter by item type and stats to find what matters for your class: the site does not guess what is good for your specialization.",
        "dg_kicker": "World of Warcraft: Forever · Dungeons", "dg_levels": "Levels", "dg_items_n": "items", "dg_title": "{name} WoW: Forever: items and loot", "dg_desc": "{name} loot in WoW: Forever: equippable items with their stats, filterable by type and stats.",
        "dg_h1": "{name}: items and stats", "dg_intro": "The equippable items of {name} ({levels}), with their real stats in Forever. Filter by item type, primary stat and secondary stats.", "dg_intro_nolvl": "The equippable items of {name}, with their real stats in Forever. Filter by item type, primary stat and secondary stats.",
        "dg_filter_type": "Item type", "dg_filter_primary": "Primary stat", "dg_filter_secondary": "Secondary stats (the item must have all checked ones)",
        "dg_filter_level": "Required level", "dg_level_min": "Min", "dg_level_max": "Max",
        "dg_reset": "Reset", "dg_none": "No item matches the chosen filters.", "dg_count": "{shown} item(s) shown out of {total}",
        "dg_slot": "Slot", "dg_item": "Item", "dg_type": "Type", "dg_req": "Required level", "dg_stats": "Stats", "dg_from": "Drops from", "dg_quest": "Quest reward", "dg_dungeon": "Dungeon",
        "dg_all_title": "All WoW: Forever dungeon items", "dg_all_desc": "Every equippable WoW: Forever dungeon item on one page, filterable by item type, primary stat and secondary stats.",
        "dg_all_h1": "All dungeon items", "dg_all_intro": "The loot of the {n} dungeons catalogued so far, on one page. Filter by item type, primary stat and secondary stats; each item names the dungeon it comes from.",
        "dg_all_card": "All dungeon items", "dg_all_card_n": "items, all dungeons",
        "dg_method_h2": "How to use this page", "dg_method": [
            "This page does not rank items by class or specialization: it shows each item's real stats, read from the Forever data, and lets you pick what matters to you.",
            "Check the item type(s) your class can equip (e.g. Mail), a primary stat (Strength, Agility or Intellect), and the secondary stats you're after.",
            "An automatic per-specialization ranking would give a false sense of precision: it ignores set bonuses, trinket effects, weapon speed, and the real weight of each stat, which vary by specialization and aren't in the public data.",
            "Item names are in English: their French translation is not in the data we retrieved.",
        ],
        "dg_src": "Loot and item stats: ", "dg_src2": "Armor and weapon types: ",
        "rd_kicker": "World of Warcraft: Forever · Raids", "rd_title_hub": "WoW: Forever raids: bosses and loot", "rd_desc_hub": "The loot and bosses of every WoW: Forever raid, with the same type/stat filter as dungeons.",
        "rd_h1_hub": "WoW: Forever raids", "rd_intro_hub": "The loot and bosses of every raid catalogued so far. This end-game content has likely not really been cleared during the beta yet: Wowhead's boss-by-boss loot attribution is often still incomplete.",
        "rd_bosses_n": "bosses", "rd_title": "{name} WoW: Forever: bosses and loot", "rd_desc": "{name} bosses and loot in WoW: Forever, filterable by item type and stats.",
        "rd_h1": "{name}: bosses and loot", "rd_intro": "The bosses of {name} and their confirmed loot, plus every raid item filterable by type and stats.",
        "rd_gallery_h2": "The place", "rd_gallery_p": "Real in-game screenshots of the raid.",
        "rd_access_h2": "Access", "rd_level": "Required level", "rd_players": "Players", "rd_territory": "Territory", "rd_location": "Location",
        "rd_patch": "Added in patch", "rd_attunement": "Attunement quest", "rd_attunement_lvl": "from level {lvl}", "rd_no_attunement": "No known attunement quest: the raid is open at the entrance.",
        "rd_bosses_h2": "The bosses", "rd_bosses_p": "The boss list and order come from the raid's own Wowhead page (the \"boss\" classification, distinct from ordinary elite enemies, only exists for raids). The loot shown under each boss is what Wowhead names as coming from that boss.",
        "rd_boss_none": "No item is named as coming from this boss in the current data.",
        "rd_boss_type": "Type", "rd_boss_abilities": "Known abilities", "rd_boss_no_abilities": "No ability recorded yet in the data we retrieved.",
        "rd_attribution_note": "This raid is level-60 content: it has likely not really been cleared during this low-level beta, so boss-by-boss loot attribution stays incomplete on Wowhead. The rest of the raid's loot is listed below, filterable like a dungeon.",
        "rd_all_h2": "All raid loot", "rd_all_p": "Every equippable item of the raid, including those with no confirmed boss source, with their real Forever stats.",
        "rd_unattributed": "Boss not confirmed",
        "rd_method": [
            "A boss is a creature Wowhead itself classifies as a boss (a category distinct from ordinary elite enemies), not just any named creature.",
            "Boss order and known abilities come from each boss's own Wowhead page (real game data: this raid has existed since WoW Classic and shares the same zone and creatures with Forever).",
            "A boss's loot is whatever Wowhead names as coming from it. Many raid items don't have that attribution yet in the beta data.",
            "Like the dungeon pages, this page does not rank items by class or specialization and offers no map or detailed strategy: no reliable source documents them for Forever.",
            "Item names, ability names and the attunement quest are in English: their French translation is not in the data we retrieved.",
        ],
        "op_kicker": "World of Warcraft: Forever · Optimizer", "op_title": "WoW: Forever character optimizer", "op_desc": "Pick your armor type and stats, then find the best items per slot across every WoW: Forever dungeon and raid.",
        "op_h1": "Character optimizer", "op_intro": "Click a gear slot to pick an item from every catalogued dungeon and raid, filterable by type and stats. Build out your full loadout and track your total stats, with no hidden per-specialization ranking.",
        "op_reset_build": "Reset loadout", "op_share": "Share", "op_share_copied": "Link copied!",
        "op_summary_h2": "Total stats", "op_summary_empty": "Pick items to see your total stats.",
        "op_close": "Close", "op_search_placeholder": "Search an item...", "op_remove_item": "Remove item",
        "op_choose_for": "Choose: {slot}", "op_picker_count": "{n} item(s)",
        "op_slot_empty": "No item known for this slot in the dungeons and raids catalogued so far.",
        "op_slot_none": "No item matches these filters.",
        "op_source_dungeon": "Dungeon: {name}", "op_source_raid": "Raid: {name}", "op_source_raid_boss": "Raid: {name} (boss: {boss})",
        "op_item_level": "Item level {lvl}",
        "op_choose_race": "Choose a race", "op_alliance": "Alliance", "op_horde": "Horde", "op_remove_race": "Remove race",
        "op_race_credit": "Race icons: ",
        "op_choose_class": "Choose a class", "op_remove_class": "Remove class",
        "op_level1_note": "Includes the starting (level 1) stats of the chosen race and class: the real race + class values, but without the level 1-60 growth curves, which aren't in public data.",
        "op_stats_credit": "Base stats by race and class: ",
        "op_completion": "{filled}/{total} slots equipped",
        "op_avg_ilvl": "Average item level: {lvl}",
        "op_sort_by": "Sort by", "op_sort_name": "Name", "op_sort_ilvl": "Item level",
        "op_upgrade_badge": "Upgrade", "op_current_badge": "Currently equipped",
        "op_vs_current": "vs equipped item: ",
        "op_method_h2": "How to use this page",
        "op_method": [
            "Click a slot to open the list of dungeon and raid items that can go there, with the same filters as the dungeon and raid pages: item type, primary stat, secondary stats and required level.",
            "This page does not pick an item for you and does not rank anything by specialization: it shows each item's real stats and lets you compare and build your loadout.",
            "The stat total at the bottom of the page is the raw sum of the items you picked: it does not account for set bonuses or special effects, which aren't in the public data.",
            "An item that exists in both a dungeon and a raid only appears once, with every source listed.",
            "The Share button encodes your loadout into the page's link: send it as-is to show it to someone else.",
        ],
    },
}
