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
        "tc_kicker": "World of Warcraft: Forever · Simulateur", "tc_title": "Simulateur DPS Guerrier Fureur niveau 20",
        "tc_desc": "Guerrier Fureur niveau 20 : simulateur de DPS à événements sur le vrai kit du plafond actuel de la bêta (Déchirure, Surpuissance), pas le kit niveau 60.",
        "tc_h1": "Simulateur DPS : Guerrier Fureur niveau 20", "tc_intro": "Un vrai moteur à événements pour le kit Fureur réellement disponible au niveau 20 (le plafond actuel de la bêta) — pas Bloodthirst, Whirlwind ni Heroic Strike, qui demandent tous le niveau 60 et n'existent pas encore dans ce personnage. Entrez vos statistiques et lancez la simulation pour voir un DPS moyen et sa répartition par source.",
        "tc_only_spec_note": "Seule spécialisation disponible pour l'instant. Icy Veins n'a publié qu'un guide niveau 20 par classe pour WoW: Forever ; les autres spécialisations suivront au fur et à mesure qu'elles seront glossées (voir le glossaire des sorts).",
        "tc_spec_fury": "Guerrier Fureur",
        "tc_inputs_h2": "Vos statistiques",
        "tc_input_ap": "Puissance d'attaque totale", "tc_input_agi": "Agilité totale", "tc_input_sp": "Puissance des sorts totale",
        "tc_input_hit": "Chance de toucher (%)", "tc_input_crit": "Chance de coup critique (%)",
        "tc_input_weapon_dmg": "Dégâts moyens de l'arme (par coup)", "tc_input_weapon_speed": "Vitesse de l'arme (secondes)",
        "tabs_weights": "Poids de stats",
        "tc_calc_h2": "DPS estimé (une cible, en continu)",
        "tc_calc_white": "Attaques normales", "tc_calc_rend": "Déchirure (entretenue)", "tc_calc_op": "Surpuissance (taux estimé)",
        "tc_calc_total": "Total estimé",
        "tc_weights_h2": "Poids de stats (DPS gagné par point)",
        "tc_weight_str": "+1 Force", "tc_weight_agi": "+1 Agilité", "tc_weight_ap": "+1 Puissance d'attaque",
        "tc_weight_hit": "+1% de chance de toucher", "tc_weight_crit": "+1% de critique",
        "tc_weight_crit_rating": "+1 Cote de critique", "tc_weight_hit_rating": "+1 Cote de toucher",
        "tc_method_h2": "Comment c'est calculé, et ce qui manque",
        "tc_method": [
            "Ce calcul par formule utilise le vrai kit niveau 20 (Déchirure, Surpuissance), pas Bloodthirst/Whirlwind du niveau 60 : Déchirure inflige 45 dégâts sur 15 secondes (rang 3, le plafond niveau 20), Surpuissance inflige 100% des dégâts d'arme + 5 fixe. Ces valeurs viennent directement des vraies infobulles Wowhead de WoW: Forever, pas d'une estimation.",
            "Déchirure est supposée entretenue en continu (100% de temps actif) : une approximation raisonnable puisqu'elle ne coûte que 10 Rage et se rafraîchit sans jamais s'additionner à elle-même.",
            "Surpuissance ne peut être lancée que dans les 5 secondes suivant une esquive de la cible contre l'un de vos coups normaux : son taux d'utilisation est donc estimé à partir de votre chance d'esquive supposée (5%, une cible de niveau proche) multipliée par votre nombre de coups normaux par seconde, plafonné par sa propre recharge de 5 secondes. C'est une approximation en régime permanent, pas un calcul exact seconde par seconde.",
            "La Cote de critique (14 = 1% à niveau 60) et la Cote de toucher (10 = 1%) viennent directement des infobulles d'objets réels de WoW: Forever, qui affichent l'équivalence en pourcentage entre parenthèses.",
            "Un coup critique inflige 200% des dégâts normaux (mécanique standard de World of Warcraft).",
            "Ce calcul par formule ignore volontairement les talents à effet aléatoire (Rafale, Colère déchaînée) et Rage sanguinaire : c'est un ordre de grandeur rapide, pas une simulation complète.",
        ],
        "tc_src_spells": "Valeurs des sorts (Déchirure, Surpuissance) : ", "tc_src_stats": "Conversions de stats (Force → Puissance d'attaque, Agilité → Critique) : ",
        "sim_h2": "Simulateur",
        "sim_intro": "Un vrai moteur à événements plutôt qu'une formule : rejoue le combat coup par coup, avec un tirage aléatoire de touché/critique à chaque attaque, et fait la moyenne sur plusieurs milliers de combats simulés.",
        "sim_fight_len": "Durée du combat (secondes)", "sim_iterations": "Nombre de combats simulés", "sim_run": "Lancer la simulation",
        "sim_dps": "DPS simulé (moyenne)", "sim_ci": "Intervalle de confiance", "sim_casts": "Déchirure / Surpuissance / Rage sanguinaire / Coups normaux par combat",
        "sim_rend_uptime": "Déchirure : % du temps actif sur la cible",
        "sim_breakdown_h3": "Répartition des dégâts par source",
        "sim_dmg_white": "Coups d'arme normaux", "sim_dmg_rend": "Déchirure", "sim_dmg_op": "Surpuissance",
        "sim_dmg_proc": "Proc d'arme générique", "sim_dmg_bleed": "Saignement générique",
        "tc_input_oh_dmg": "Dégâts moyens de l'arme de main gauche (par coup)",
        "tc_input_oh_speed": "Vitesse de l'arme de main gauche (secondes)",
        "tc_input_dws": "Rang de Spécialisation Ambidextrie (0-5)",
        "tc_input_oh_note": "Mettez les dégâts de main gauche à 0 pour simuler une seule arme, sans double maniement.",
        "tc_input_flurry": "Rang de Rafale (0-5)",
        "tc_input_unbridled": "Rang de Colère déchaînée (0-5)",
        "tc_input_cruelty": "Rang de Cruauté (0-5, +1% critique par rang)",
        "tc_input_precision": "Rang de Précision (0-3, +1% de toucher par rang)",
        "tc_input_bloodrage": "Utiliser Rage sanguinaire dès que disponible",
        "tc_input_boundless": "Rang de Rage infinie (0-3, +10 Rage max par rang)",
        "tc_proc_h3": "Effets d'objet génériques (optionnel)",
        "tc_proc_note": "Aucun objet précis de WoW: Forever n'est encore confirmé meilleur-en-son-genre pour cette spécialisation : ces champs restent à 0 par défaut. Si votre arme a un vrai effet « chance au toucher » ou applique un saignement, entrez ses vraies valeurs (infobulle de l'objet) ici plutôt que d'utiliser un exemple inventé.",
        "tc_input_proc_chance": "Chance de proc à chaque coup d'arme touché (%)",
        "tc_input_proc_dmg": "Dégâts moyens du proc (fixe, par déclenchement)",
        "tc_input_bleed_chance": "Chance d'appliquer un saignement par coup touché (%)",
        "tc_input_bleed_tick": "Dégâts du saignement par tic",
        "tc_input_bleed_interval": "Intervalle entre les tics (secondes)",
        "tc_input_bleed_duration": "Durée du saignement (secondes)",
        "sim_method_h2": "Comment c'est calculé, et ce qui manque",
        "sim_method": [
            "Ce simulateur modélise le vrai kit Fureur du niveau 20 (le plafond actuel de la bêta), pas celui du niveau 60 : Bloodthirst (niveau 60), Whirlwind (niveau 36) et Heroic Strike (rang max niveau 60) sont retirés, puisqu'aucun des trois n'est réellement entraînable à ce niveau. Le kit modélisé ici vient de data/wow_spells/warrior.json, sourcé depuis les vraies infobulles Wowhead de WoW: Forever : Déchirure (rang 3, exactement le plafond niveau 20, 45 dégâts sur 15s en 5 tics de 9, peut critiquer par tic), Surpuissance (5 Rage, 5 secondes de recharge, 100% des dégâts d'arme + 5) et Rage sanguinaire (60 secondes de recharge, +20 Rage au total).",
            "Priorité de rotation modélisée : Surpuissance dès qu'elle est disponible (la cible vient d'esquiver un de vos coups normaux), sinon maintenir Déchirure (rafraîchie sans jamais s'additionner à elle-même — un nouveau lancer remplace la durée restante, ne s'y ajoute pas), sinon attendre. Au niveau 20, il n'existe aucune vraie capacité de « dépense » de Rage supplémentaire : Heroic Strike est explicitement déconseillé par le guide Icy Veins niveau 20 lui-même (trop coûteux en Rage à ce stade) et n'est de toute façon pas trainable avant 60. La Rage s'accumule donc souvent jusqu'à son plafond entre deux Surpuissance/Déchirure : c'est un vrai résultat de ce niveau, pas un bug du simulateur.",
            "Surpuissance n'est utilisable que dans les 5 secondes suivant une esquive de la cible contre l'un de vos coups d'arme normaux (mécanique réelle du WoW classique, Vanilla WoW Wiki — Overpower) ; elle ne peut elle-même être ni esquivée, ni parée, ni bloquée (vraie mention sur son infobulle Wowhead), mais peut toujours être ratée.",
            "La génération de Rage utilise la vraie formule du WoW classique historique (R = 15 × dégâts / (4 × c) + f × vitesse d'arme / 2, plafonnée à 15 × dégâts / c) : seuls les coups d'arme normaux qui touchent en génèrent, jamais Déchirure ou Surpuissance. La valeur de conversion de Rage « c » dépend du niveau du personnage (c ≈ 0,0091 × niveau² + 3,226 × niveau + 4,265, une formule communautaire qui retombe exactement sur la valeur connue de 230,6 au niveau 60) : ce simulateur utilise donc c ≈ 72,4 pour le niveau 20, pas la constante de niveau 60 utilisée par erreur dans une version précédente de cet outil — à ce niveau, un même montant de dégâts génère proportionnellement plus de Rage qu'au niveau 60.",
            "Le double maniement d'armes est modélisé avec deux armes indépendantes (main droite et main gauche), chacune avec son propre timer de coup et sa propre génération de Rage. Mécaniques réelles du WoW classique : l'arme de main gauche inflige 50% de ses dégâts habituels, et le double maniement ajoute une pénalité de 19% de chance de rater sur les coups normaux des deux armes ; cette pénalité ne s'applique ni à Déchirure ni à Surpuissance, qui sont des attaques spéciales. D'après les notes du glossaire, le double maniement lui-même ne devient disponible qu'exactement au niveau 20.",
            "Spécialisation Ambidextrie (talent réel de l'arbre Fureur, 5 rangs) réduit ce malus : chaque rang donne +5% de dégâts de main gauche, +20% de génération de Rage de main gauche et +2% de chance de toucher de main gauche.",
            "Cruauté (5 rangs, +1% critique par rang) et Précision (3 rangs, +1% de toucher par rang) s'ajoutent directement à vos pourcentages de critique/toucher saisis ci-dessus. Rafale (5 rangs) donne +5% de vitesse d'attaque par rang sur vos 3 prochains coups après un coup critique au corps à corps (auto-attaque, Déchirure ou Surpuissance), les charges expirant après 15 secondes ; simplification disclosée : les tics de Déchirure qui critiquent ne déclenchent pas Rafale ici, un tic de DoT n'étant généralement pas traité comme un « coup critique au corps à corps » dans les mécaniques classiques. Colère déchaînée (5 rangs) donne +12% de chance par rang de générer 1 Rage supplémentaire sur un coup d'arme normal touché.",
            "Rage infinie (3 rangs) augmente votre réserve maximale de Rage de 10/20/30. Avec seulement 11 points disponibles au niveau 20 au total, tous les rangs affichés ici ne sont pas forcément atteignables simultanément dans un seul arbre : ces champs restent un bac à sable pour comparer des rangs, pas une reconstitution garantie d'un build exact à 11 points.",
            "Rage sanguinaire (60 secondes de recharge, sans temps de recharge global) ajoute 10 Rage immédiatement puis 10 de plus sur 10 secondes, pour un coût réel de 20% des points de vie maximum du personnage — ce coût en vie n'est pas modélisé ici (aucun dégât subi n'est simulé), donc la case suppose implicitement que ce coût est toujours soutenable.",
            "Vos coups d'arme normaux utilisent une vraie table de résolution des attaques : en plus de rater, ils peuvent être esquivés (5%, sans dégâts, et c'est ce qui ouvre la fenêtre de Surpuissance) ou partiellement ratés en coup indirect (« Glancing Blow », 10% de chance, 70% des dégâts habituels). Contrairement à une version précédente de cet outil qui modélisait un boss de raid niveau 63, ces pourcentages sont maintenant les valeurs de base du WoW classique à différentiel de compétence nul, un choix plus honnête pour une cible de niveau proche du personnage plutôt qu'un boss de fin de jeu ; ni l'esquive ni le coup indirect ne s'appliquent à Déchirure ou Surpuissance, qui utilisent une table de résolution distincte (« attaques jaunes »). La parade et le blocage sont supposés à 0%.",
            "Les champs « effets d'objet génériques » couvrent un vrai proc « chance au toucher » et un vrai saignement (DoT à tics, non cumulable : un nouveau déclenchement rafraîchit sa durée plutôt que de s'ajouter). Comme aucun objet précis n'est confirmé meilleur-en-son-genre pour Forever à ce niveau, ils restent à 0 par défaut.",
            "Cet outil ne couvre pas tout le sort-book du Guerrier, seulement une rotation Fureur soutenue mono-cible au niveau 20. Volontairement laissés de côté, avec leur raison réelle (voir le glossaire des sorts pour le détail) : Charge (utilisable une seule fois en début de combat, hors combat uniquement), Fragmentation d'armure (aucune formule de mitigation d'armure encore sourcée), Ruée victorieuse (ne se déclenche qu'après un kill, jamais en combat continu), Cri démoralisant (réduit la Puissance d'attaque de la CIBLE, sans effet sur les dégâts du joueur), et Cri de bataille (buff de longue durée à faible entretien : ajoutez ses +12 Puissance d'attaque directement à votre statistique ci-dessus plutôt que de le faire lancer par le simulateur).",
            "La répartition des dégâts par source montre le DPS et la part (%) de chaque source réellement modélisée : coups normaux (main droite + main gauche), Déchirure, Surpuissance, et vos éventuels proc/saignement génériques.",
            "Chaque coup ici tire réellement un jet de touché puis de critique au hasard : le DPS affiché est une vraie moyenne statistique, pas un calcul déterministe.",
        ],
        "sim_src_rage": "Formule de génération de Rage et sa constante dépendante du niveau (WoW classique) : ",
        "sim_src_dw": "Dégâts et pénalité de toucher du double maniement (WoW classique) : ",
        "sim_src_dws": "Rangs de Spécialisation Ambidextrie, Rafale, Colère déchaînée, Cruauté, Précision et Rage infinie (WoW: Forever) : ",
        "sim_src_flurry": "Mécanique de Rafale : charges, expiration (WoW Classic) : ",
        "sim_src_rend": "Coût, dégâts et durée de Déchirure (WoW: Forever) : ",
        "sim_src_overpower": "Coût, recharge et fenêtre d'utilisation de Surpuissance après une esquive (WoW classique) : ",
        "sim_src_bloodrage": "Coût, recharge et effet de Rage sanguinaire (WoW: Forever) : ",
        "sim_src_atktable": "Table de résolution des attaques, attaques spéciales (WoW classique) : ",
        "sim_src_glance": "Chance et réduction de dégâts des coups indirects (WoW classique) : ",
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
        "tc_kicker": "World of Warcraft: Forever · Simulator", "tc_title": "Level 20 Fury Warrior DPS simulator",
        "tc_desc": "Level 20 Fury Warrior: event-driven DPS simulator built on the real kit at the beta's current cap (Rend, Overpower), not the level-60 kit.",
        "tc_h1": "DPS simulator: level 20 Fury Warrior", "tc_intro": "A real event-driven engine for the Fury kit actually available at level 20 (the beta's current cap) — not Bloodthirst, Whirlwind or Heroic Strike, which all require level 60 and don't exist yet on this character. Enter your stats and run the simulation to see an average DPS and its breakdown by source.",
        "tc_only_spec_note": "Only specialization available for now. Icy Veins has only published a level-20 guide per class for WoW: Forever so far; other specializations will follow as they get glossed (see the spell glossary).",
        "tc_spec_fury": "Fury Warrior",
        "tc_inputs_h2": "Your stats",
        "tc_input_ap": "Total Attack Power", "tc_input_agi": "Total Agility", "tc_input_sp": "Total Spell Power",
        "tc_input_hit": "Hit chance (%)", "tc_input_crit": "Critical strike chance (%)",
        "tc_input_weapon_dmg": "Average weapon damage (per hit)", "tc_input_weapon_speed": "Weapon speed (seconds)",
        "tabs_weights": "Stat weights",
        "tc_calc_h2": "Estimated DPS (single target, sustained)",
        "tc_calc_white": "Normal attacks", "tc_calc_rend": "Rend (maintained)", "tc_calc_op": "Overpower (estimated rate)",
        "tc_calc_total": "Estimated total",
        "tc_weights_h2": "Stat weights (DPS gained per point)",
        "tc_weight_str": "+1 Strength", "tc_weight_agi": "+1 Agility", "tc_weight_ap": "+1 Attack Power",
        "tc_weight_hit": "+1% hit chance", "tc_weight_crit": "+1% critical strike",
        "tc_weight_crit_rating": "+1 Critical Strike Rating", "tc_weight_hit_rating": "+1 Hit Rating",
        "tc_method_h2": "How this is calculated, and what's missing",
        "tc_method": [
            "This formula-based calculation uses the real level-20 kit (Rend, Overpower), not level-60's Bloodthirst/Whirlwind: Rend deals 45 damage over 15 seconds (rank 3, the level-20 cap), Overpower deals 100% weapon damage + 5 flat. Both values come directly from WoW: Forever's real Wowhead tooltips, not an estimate.",
            "Rend is assumed maintained continuously (100% uptime): a reasonable approximation since it only costs 10 Rage and refreshes outright, never stacking.",
            "Overpower can only be cast within 5 seconds of the target dodging one of your normal swings: its usage rate is therefore estimated from your assumed Dodge chance (5%, a target close to your own level) times your normal-hit rate per second, capped by its own 5-second cooldown. This is a steady-state approximation, not an exact second-by-second calculation.",
            "Critical Strike Rating (14 = 1% at level 60) and Hit Rating (10 = 1%) come directly from real WoW: Forever item tooltips, which show the percentage equivalent in parentheses.",
            "A critical strike deals 200% of normal damage (standard World of Warcraft mechanic).",
            "This formula-based calculation deliberately ignores randomly-triggered talents (Flurry, Unbridled Wrath) and Bloodrage: it's a quick order-of-magnitude estimate, not a full simulation.",
        ],
        "tc_src_spells": "Spell values (Rend, Overpower): ", "tc_src_stats": "Stat conversions (Strength → Attack Power, Agility → Critical Strike): ",
        "sim_h2": "Simulator",
        "sim_intro": "A real event-driven engine instead of a formula: replays the fight swing by swing, rolling a real hit/crit chance on every attack, and averages the result over thousands of simulated fights.",
        "sim_fight_len": "Fight length (seconds)", "sim_iterations": "Simulated fights", "sim_run": "Run simulation",
        "sim_dps": "Simulated DPS (average)", "sim_ci": "Confidence interval", "sim_casts": "Rend / Overpower / Bloodrage / normal hits per fight",
        "sim_rend_uptime": "Rend: % uptime on target",
        "sim_breakdown_h3": "Damage breakdown by source",
        "sim_dmg_white": "Normal weapon swings", "sim_dmg_rend": "Rend", "sim_dmg_op": "Overpower",
        "sim_dmg_proc": "Generic weapon proc", "sim_dmg_bleed": "Generic bleed",
        "tc_input_oh_dmg": "Off-hand weapon average damage (per hit)",
        "tc_input_oh_speed": "Off-hand weapon speed (seconds)",
        "tc_input_dws": "Dual Wield Specialization rank (0-5)",
        "tc_input_oh_note": "Set off-hand damage to 0 to simulate a single weapon, with no dual-wielding.",
        "tc_input_flurry": "Flurry rank (0-5)",
        "tc_input_unbridled": "Unbridled Wrath rank (0-5)",
        "tc_input_cruelty": "Cruelty rank (0-5, +1% crit per rank)",
        "tc_input_precision": "Precision rank (0-3, +1% hit per rank)",
        "tc_input_bloodrage": "Use Bloodrage as soon as it's available",
        "tc_input_boundless": "Boundless Rage rank (0-3, +10 max Rage per rank)",
        "tc_proc_h3": "Generic item effects (optional)",
        "tc_proc_note": "No specific WoW: Forever item is confirmed best-in-slot for this spec yet, so these fields default to 0. If your weapon has a real \"chance on hit\" effect or applies a bleed, enter its real values (from the item's own tooltip) here instead of using a made-up example.",
        "tc_input_proc_chance": "Proc chance on each landed weapon hit (%)",
        "tc_input_proc_dmg": "Average proc damage (flat, per trigger)",
        "tc_input_bleed_chance": "Chance to apply a bleed per landed hit (%)",
        "tc_input_bleed_tick": "Bleed damage per tick",
        "tc_input_bleed_interval": "Time between ticks (seconds)",
        "tc_input_bleed_duration": "Bleed duration (seconds)",
        "sim_method_h2": "How this is calculated, and what's missing",
        "sim_method": [
            "This simulator models the real level-20 Fury kit (the beta's current cap), not the level-60 one: Bloodthirst (level 60), Whirlwind (level 36) and Heroic Strike (max rank, level 60) are removed, since none of the three is actually trainable at this level. The kit modeled here comes from data/wow_spells/warrior.json, sourced from WoW: Forever's real Wowhead tooltips: Rend (rank 3, exactly the level-20 cap, 45 damage over 15s in 5 ticks of 9, can crit per tick), Overpower (5 Rage, 5-second cooldown, 100% weapon damage + 5) and Bloodrage (60-second cooldown, +20 Rage total).",
            "Modeled rotation priority: Overpower whenever it's available (the target just dodged one of your normal swings), otherwise maintain Rend (refreshed outright rather than stacking — a new cast replaces the remaining duration, never adds to it), otherwise wait. At level 20 there's no real extra Rage \"spender\": Heroic Strike is explicitly discouraged by the level-20 Icy Veins guide itself (too Rage-inefficient at this stage) and isn't trainable before 60 anyway. Rage therefore often sits at its cap between Overpower/Rend casts: that's a genuine finding about this level, not a simulator bug.",
            "Overpower is only usable within 5 seconds of the target dodging one of your normal weapon swings (real WoW classic mechanic, Vanilla WoW Wiki — Overpower); it can never itself be dodged, parried or blocked (a real flag on its own Wowhead tooltip), but it can still miss.",
            "Rage generation uses the real historical WoW classic formula (R = 15 × damage / (4 × c) + f × weapon speed / 2, capped at 15 × damage / c): only landed normal weapon swings generate Rage, never Rend or Overpower. The Rage conversion value \"c\" depends on character level (c ≈ 0.0091 × level² + 3.226 × level + 4.265, a community-derived formula that lands exactly on the known level-60 value of 230.6): this simulator therefore uses c ≈ 72.4 for level 20, not the level-60 constant an earlier version of this tool used by mistake — at this level, the same amount of damage generates proportionally more Rage than it would at level 60.",
            "Dual-wielding is modeled with two independent weapons (main hand and off hand), each with its own swing timer and its own Rage generation. Real classic-WoW mechanics: the off-hand weapon deals 50% of its usual damage, and dual-wielding adds a 19% miss-chance penalty to both weapons' normal swings; this penalty doesn't apply to Rend or Overpower, which are special attacks. Per the glossary's own notes, dual-wielding itself only becomes available exactly at level 20.",
            "Dual Wield Specialization (a real Fury-tree talent, 5 ranks) reduces that penalty: each rank gives +5% off-hand damage, +20% off-hand Rage generation and +2% off-hand hit chance.",
            "Cruelty (5 ranks, +1% crit per rank) and Precision (3 ranks, +1% hit per rank) add directly to the crit/hit percentages you enter above. Flurry (5 ranks) gives +5% attack speed per rank for your next 3 swings after a melee critical strike (auto-attack, Rend or Overpower), with charges expiring after 15 seconds; disclosed simplification: a critical Rend tick doesn't trigger Flurry here, since a DoT tick generally isn't treated as a \"melee critical strike\" under classic-era mechanics. Unbridled Wrath (5 ranks) gives +12% chance per rank to generate 1 extra Rage on a landed normal weapon swing.",
            "Boundless Rage (3 ranks) raises your maximum Rage pool by 10/20/30. With only 11 points available at level 20 in total, every rank shown here isn't necessarily reachable at the same time in a single tree: these fields stay a sandbox for comparing ranks, not a guaranteed reconstruction of one exact 11-point build.",
            "Bloodrage (60-second cooldown, no global cooldown) adds 10 Rage immediately plus 10 more over 10 seconds, for a real cost of 20% of the character's maximum health — that health cost isn't modeled here (no incoming damage is simulated), so the checkbox implicitly assumes that cost is always affordable.",
            "Your normal weapon swings use a real attack-resolution table: on top of missing, they can be Dodged (5%, no damage, and this is what opens the Overpower window) or land as a Glancing Blow (10% chance, 70% of normal damage). Unlike an earlier version of this tool, which modeled a level-63 raid boss, these are now the classic-WoW base values at zero skill differential — a more honest choice for a target close to the character's own level rather than an end-game boss; neither Dodge nor Glancing applies to Rend or Overpower, which use a separate \"yellow attack\" resolution table. Parry and Block are assumed to be 0%.",
            "The \"generic item effects\" fields cover a real \"chance on hit\" proc and a real bleed (a ticking DoT, non-stacking: a new trigger refreshes its duration rather than adding a second one). Since no specific item is confirmed best-in-slot for Forever at this level yet, they default to 0.",
            "This tool doesn't cover the Warrior's whole spellbook, only a sustained single-target Fury rotation at level 20. Deliberately left out, with the real reason (see the spell glossary for detail): Charge (usable once, out of combat only, at the very start of a fight), Sunder Armor (no sourced armor-mitigation formula yet), Victory Rush (only triggers after a kill, never in a continuous fight), Demoralizing Shout (reduces the TARGET's Attack Power, no effect on the player's own damage), and Battle Shout (a long, low-maintenance buff: add its +12 Attack Power directly to your stat above instead of having the simulator cast it).",
            "The damage breakdown by source shows the DPS and share (%) of each source actually modeled: normal swings (main hand + off hand), Rend, Overpower, and your generic proc/bleed if enabled.",
            "Every hit here actually rolls a real hit chance and then a crit chance: the DPS shown is a genuine statistical average, not a deterministic calculation.",
        ],
        "sim_src_rage": "Rage-generation formula and its level-dependent constant (WoW classic): ",
        "sim_src_dw": "Dual-wield damage and miss-chance penalty (WoW classic): ",
        "sim_src_dws": "Dual Wield Specialization, Flurry, Unbridled Wrath, Cruelty, Precision and Boundless Rage ranks (WoW: Forever): ",
        "sim_src_flurry": "Flurry mechanics: charges, expiry (WoW Classic): ",
        "sim_src_rend": "Rend's cost, damage and duration (WoW: Forever): ",
        "sim_src_overpower": "Overpower's cost, cooldown and post-dodge usage window (WoW classic): ",
        "sim_src_bloodrage": "Bloodrage's cost, cooldown and effect (WoW: Forever): ",
        "sim_src_atktable": "Attack resolution table, special attacks (WoW classic): ",
        "sim_src_glance": "Glancing Blow chance and damage reduction (WoW classic): ",
    },
}
