"""View-model for one League champion guide (/league/guide/<champion>/, /en/league/guide/<champion>/).

Pure functions over already-loaded data (see src/tft_tracker/lol_guide.py for
how the measured aggregates are produced, and lol_guides_editorial.py for the
hand-written combos). Nothing here fabricates a number: every sentence is
composed from a measured value or an official Riot text, and every section
returns nothing when its sample is too small -- the template then omits it.

Every user-visible string lives in STR[lang] (fr / en); the template only prints
what this module hands it (g.ui for labels, g.* for prose).
"""
from __future__ import annotations

import re

ROLE_LABEL = {"top": "Top", "jungle": "Jungle", "mid": "Mid", "adc": "ADC", "support": "Support"}
SHARD_NAMES = {   # stat shards are not in Data Dragon's runesReforged: (fr, en)
    5001: ("Vie évolutive", "Health scaling"), 5005: ("Vitesse d'attaque", "Attack speed"),
    5007: ("Accélération de compétence", "Ability haste"), 5008: ("Force adaptative", "Adaptive force"),
    5010: ("Vitesse de déplacement", "Movement speed"), 5011: ("Vie", "Health"),
    5013: ("Ténacité et résistance aux ralentissements", "Tenacity and slow resist"),
}
MIN_MATCHUP_GAMES = 15
MIN_LIFT_GAMES = 25
NOTABLE_LIFT = 0.03

STR = {
    "fr": {
        "role_in": {"top": "en Top", "jungle": "en Jungle", "mid": "en Mid", "adc": "en ADC", "support": "en Support"},
        "bucket": {"short": ("courtes", "moins de 25 min"), "mid": ("moyennes", "25 à 35 min"), "long": ("longues", "plus de 35 min")},
        "enemy": {
            "ap": ("Équipe adverse surtout magique", "au moins 50 % de leurs dégâts sont magiques"),
            "ad": ("Équipe adverse surtout physique", "moins de 35 % de leurs dégâts sont magiques"),
            "mixed": ("Équipe adverse équilibrée", "dégâts physiques et magiques mélangés"),
        },
        "and": " et ", "pctsp": " %", "aa": "Attaque de base",
        "difficulty": ("plutôt simple à prendre en main", "de difficulté moyenne", "exigeant à maîtriser"),
        "stats": ("KDA moyen", "ratio", "Dégâts / min", "CS / min", "Or / min", "Participation aux kills", "Vision / min"),
        "ui": {
            "guide": "Guide", "h1": "Guide {name}", "toc_aria": "Sommaire du guide", "toc_combos": "Aperçu des combos", "toc_build": "Build",
            "toc_adverse": "Objets selon l'ennemi", "toc_contres": "Contres", "toc_abilities": "Capacités", "toc_faq": "FAQ",
            "tier_badge": "Tier {tier} {role}",
            "avg_note": "Moyennes mesurées sur {games} parties {role} jouées avec {name}, issues de notre collecte (file classée Solo/Duo).",
            "combos_title": "Façon de jouer et aperçu des combos", "editorial_tag": "Guide rédigé · d'après les textes officiels des capacités",
            "strengths": "Points forts de {name}", "weaknesses": "Points faibles de {name}", "teamfight": "Rôle en combat d'équipe",
            "when": "Quand :", "laning": "Phase de lane", "mistakes": "Erreurs fréquentes", "riot_play": "Conseils officiels de Riot pour jouer {name}",
            "build_title": "Build, runes et sorts d'invocateur", "top_items_title": "Objets les plus construits",
            "top_items_note": "Les choix d'objets varient trop pour qu'un build de base se répète : voici les objets terminés les plus souvent présents en fin de partie, avec la part des parties où ils sont achetés.",
            "share": "des parties", "games": "parties", "boots": "Bottes", "summoners": "Sorts d'invocateur",
            "runes": "Runes les plus jouées",
            "adverse_title": "Quels objets prendre selon l'équipe adverse ?",
            "adverse_intro": "Nous classons chaque partie selon les dégâts de l'équipe ennemie. Voici les objets terminés de {name} et leur winrate dans chaque situation ; « ▲ » signale un objet qui fait au moins 3 points de mieux que son winrate habituel.",
            "contres_title": "Contres et matchups", "who_counters": "Qui contre {name} {role_in}", "see_guide_of": "Voir le guide de {enemy}",
            "strong_vs": "Contre qui {name} est fort", "play_against": "Comment jouer contre {name}", "riot_src": "Conseils officiels de Riot.",
            "matchup_note": "Winrates mesurés sur des duels directs de même poste ; seuls les affrontements de plus de 15 parties sont listés.",
            "all_matchups": "Voir tous les matchups de {name}", "abilities": "Capacités", "passive": "Passif", "faq_title": "Questions fréquentes",
            "full_sheet": "Fiche complète de {name}", "tier_list": "Tier list League of Legends", "all_guides": "Tous les guides de champions",
            "guide_title_attr": "Guide {name}",
            "runes_primary": "Arbre principal", "runes_secondary": "Arbre secondaire", "runes_shards": "Fragments",
            "runes_note": "Pour chaque rangée, la rune la plus choisie parmi les parties jouées avec cette page (part des parties entre parenthèses).",
            "skills_title": "Ordre des compétences", "skills_maxed": "Maximisation", "skills_level": "Niv.",
            "skills_note": "L'ordre indique quelles compétences atteignent le rang 5 en premier ; la grille montre la montée de niveau la plus jouée avec cet ordre (mesuré sur {tl_games} parties).",
            "start_title": "Objets de départ", "path_title": "Ordre des premiers objets terminés",
            "lane_title": "Phase de lane (moyennes)",
        },
        "lane_text": "À 10 min : {g10} or, {c10} CS, {x10} XP. À 15 min : {g15} or, {c15} CS, {x15} XP.",
        # 2026-10-14 (Search Console: 179 "<champion> combo" queries landed on the guides): no "combos" in a guide's title or description, the combos page owns that
        # query. Longest variant first; the first one that fits in 60 (title) / 155 (description) characters wins. {kw} / {counters}: only what the page really has.
        "seo_title": ("{name} {role} Build & Guide (Patch {patch}) : {kw}", "{name} {role} Build & Guide (Patch {patch}) : {kw2}", "{name} {role} Build & Guide (Patch {patch})",
                      "{name} {role} Build & Guide : {kw2}", "{name} {role} Build & Guide", "{name} Build & Guide"),
        "seo_kw": ("runes, objets, contres", "runes et objets"), "seo_kw2": ("runes, contres", "runes"),
        "seo_desc": ("Guide {name} {role} (patch {patch}) : runes, build et objets selon l'équipe adverse{counters}, mesurés sur {n} parties {role}.",
                     "Guide {name} {role} (patch {patch}) : runes, build et objets{counters}.",
                     "Guide {name} {role} : runes, build et objets{counters}.",
                     "Guide {name} : runes, build et objets."),
        "seo_counters": " et contres",
        "role": {
            "title": "{name} {role} : ce que disent nos parties", "toc": "Poste",
            "lane_h": "Phase de lane face à la moyenne des {role}", "col_measure": "Mesure", "col_avg": "Moyenne {role}", "col_diff": "Écart",
            "lane_labels": {"gold_at10": "Or à 10 min", "cs_at10": "CS à 10 min", "xp_at10": "XP à 10 min", "gold_at15": "Or à 15 min", "cs_at15": "CS à 15 min", "xp_at15": "XP à 15 min"},
            "lane_note": "Mesuré sur {games} parties de {name} avec chronologie ; la moyenne regroupe {champs} champions jouant {role} dans nos parties classées.",
            "spikes_h": "Taux de victoire selon la durée de la partie", "spikes_best": "Meilleur résultat : {name} ({label}).",
            "spikes_note": "Seuls les groupes d'au moins 30 parties sont affichés. Un écart de plusieurs points indique la phase où le champion est le plus fiable.",
            "others_h": "{name} à un autre poste", "col_role": "Poste", "col_games": "Parties", "col_wr": "Victoires", "col_cs": "CS/min", "col_gold": "Or/min", "col_items": "Objets les plus construits",
            "others_note": "Postes où nous avons au moins 40 parties de {name}.",
            "same_h": "Autres {role} à connaître", "same_played": "Les plus joués", "same_strong": "Les plus efficaces (au moins 100 parties)",
        },
    },
    "en": {
        "role_in": {"top": "in Top", "jungle": "in the Jungle", "mid": "in Mid", "adc": "as ADC", "support": "as Support"},
        "bucket": {"short": ("short", "under 25 min"), "mid": ("medium-length", "25 to 35 min"), "long": ("long", "over 35 min")},
        "enemy": {
            "ap": ("Mostly magic-damage enemy team", "at least 50% of their damage is magic"),
            "ad": ("Mostly physical-damage enemy team", "less than 35% of their damage is magic"),
            "mixed": ("Balanced enemy team", "mixed physical and magic damage"),
        },
        "and": " and ", "pctsp": "%", "aa": "Basic attack",
        "difficulty": ("that is easy to pick up", "of medium difficulty", "that is demanding to master"),
        "stats": ("Average KDA", "ratio", "Damage / min", "CS / min", "Gold / min", "Kill participation", "Vision / min"),
        "ui": {
            "guide": "Guide", "h1": "{name} Guide", "toc_aria": "Guide contents", "toc_combos": "Combo preview", "toc_build": "Build",
            "toc_adverse": "Items by enemy team", "toc_contres": "Counters", "toc_abilities": "Abilities", "toc_faq": "FAQ",
            "tier_badge": "Tier {tier} {role}",
            "avg_note": "Averages measured over {games} {role} games played with {name}, from our ranked Solo/Duo data collection.",
            "combos_title": "How to play and combo preview", "editorial_tag": "Written guide · based on the official ability texts",
            "strengths": "{name}'s strengths", "weaknesses": "{name}'s weaknesses", "teamfight": "Role in team fights",
            "when": "When:", "laning": "Laning phase", "mistakes": "Common mistakes", "riot_play": "Riot's official tips for playing {name}",
            "build_title": "Build, runes and summoner spells", "top_items_title": "Most-built items",
            "top_items_note": "Item choices vary too much for a single core build to repeat: these are the finished items most often owned at the end of the game, with the share of games in which they are bought.",
            "share": "of games", "games": "games", "boots": "Boots", "summoners": "Summoner spells",
            "runes": "Most-played runes",
            "adverse_title": "Which items to build against the enemy team?",
            "adverse_intro": "We sort every game by the enemy team's damage. These are {name}'s completed items and their win rate in each situation; \"▲\" marks an item that does at least 3 points better than its usual win rate.",
            "contres_title": "Counters and matchups", "who_counters": "Who counters {name} {role_in}", "see_guide_of": "See the {enemy} guide",
            "strong_vs": "Who {name} is strong against", "play_against": "How to play against {name}", "riot_src": "Riot's official tips.",
            "matchup_note": "Win rates measured over direct same-role duels; only matchups with more than 15 games are listed.",
            "all_matchups": "See all of {name}'s matchups", "abilities": "Abilities", "passive": "Passive", "faq_title": "Frequently asked questions",
            "full_sheet": "Full {name} page", "tier_list": "League of Legends tier list", "all_guides": "All champion guides",
            "guide_title_attr": "{name} guide",
            "runes_primary": "Primary tree", "runes_secondary": "Secondary tree", "runes_shards": "Shards",
            "runes_note": "For each row, the most picked rune among the games played with this page (share of games in brackets).",
            "skills_title": "Skill order", "skills_maxed": "Max order", "skills_level": "Lvl",
            "skills_note": "The order shows which abilities reach rank 5 first; the grid shows the most-played level-up sequence with that order (measured over {tl_games} games).",
            "start_title": "Starting items", "path_title": "First completed items, in order",
            "lane_title": "Laning phase (averages)",
        },
        "lane_text": "At 10 min: {g10} gold, {c10} CS, {x10} XP. At 15 min: {g15} gold, {c15} CS, {x15} XP.",
        "seo_title": ("{name} {role} Build & Guide (Patch {patch}): {kw}", "{name} {role} Build & Guide (Patch {patch}): {kw2}", "{name} {role} Build & Guide (Patch {patch})",
                      "{name} {role} Build & Guide: {kw2}", "{name} {role} Build & Guide", "{name} Build & Guide"),
        "seo_kw": ("runes, items, counters", "runes and items"), "seo_kw2": ("runes, counters", "runes"),
        "seo_desc": ("{name} {role} guide (patch {patch}): runes, build and items by enemy team{counters}, measured over {n} {role} games.",
                     "{name} {role} guide (patch {patch}): runes, build and items{counters}.",
                     "{name} {role} guide: runes, build and items{counters}.",
                     "{name} guide: runes, build and items."),
        "seo_counters": " and counters",
        "role": {
            "title": "{name} {role}: what our games say", "toc": "Role",
            "lane_h": "Laning phase against the {role} average", "col_measure": "Measure", "col_avg": "{role} average", "col_diff": "Gap",
            "lane_labels": {"gold_at10": "Gold at 10 min", "cs_at10": "CS at 10 min", "xp_at10": "XP at 10 min", "gold_at15": "Gold at 15 min", "cs_at15": "CS at 15 min", "xp_at15": "XP at 15 min"},
            "lane_note": "Measured over {games} {name} games with a timeline; the average covers {champs} champions played {role} in our ranked games.",
            "spikes_h": "Win rate by game length", "spikes_best": "Best result: {name} ({label}).",
            "spikes_note": "Only groups of at least 30 games are shown. A gap of several points shows the phase where the champion is the most reliable.",
            "others_h": "{name} in another role", "col_role": "Role", "col_games": "Games", "col_wr": "Win rate", "col_cs": "CS/min", "col_gold": "Gold/min", "col_items": "Most-built items",
            "others_note": "Roles where we have at least 40 {name} games.",
            "same_h": "Other {role} champions to know", "same_played": "Most played", "same_strong": "Strongest (at least 100 games)",
        },
    },
}


def pct(x: float, digits: int = 1) -> str:
    return f"{x * 100:.{digits}f}"


def join_list(items: list[str], lang: str) -> str:
    items = [i for i in items if i]
    if len(items) <= 1:
        return "".join(items)
    if lang == "fr":
        return ", ".join(items[:-1]) + " et " + items[-1]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def resolve_item(item_id: int, lookup: dict, lang: str) -> dict | None:
    ref = lookup.get(str(item_id))
    if not ref:
        return None
    return {"id": item_id, "name": ref["name_fr" if lang == "fr" else "name_en"], "icon_file": ref["icon_file"],
            "slug": ref["slug"], "has_page": ref["has_page"]}



LANE_KEYS = ("gold_at10", "cs_at10", "xp_at10", "gold_at15", "cs_at15", "xp_at15")
MIN_TL_GAMES = 30         # timeline games a champion needs for its lane figures to be compared with the role average
MIN_BASELINE_CHAMPS = 10  # champions a role average is built from
MIN_BUCKET_GAMES = 30     # games a game-length group needs to be shown


def build_role_context(guide_by_champion: dict, champ_by_id: dict, lang: str) -> dict:
    """Role-level context of the guides (2026-10-14, Search Console: "<champion> <role>" queries sit at positions 11-17): the average lane figures of every
    role (weighted by timeline games, champions with at least MIN_TL_GAMES of them) and, per role, the champions that play it, for the "other <role>" links.
    Everything is read from data/output/lol_champion_guide.json (our ranked games)."""
    sums: dict[str, dict] = {}
    lists: dict[str, list] = {}
    for cid, g in guide_by_champion.items():
        c = champ_by_id.get(cid)
        if not c:
            continue
        for role, r in (g.get("roles") or {}).items():
            lists.setdefault(role, []).append({"id": cid, "slug": c["slug"], "name": c["name_fr"] if lang == "fr" else c["name_en"], "icon_file": c["icon_file"],
                                               "games": r["games"], "win_rate": r["win_rate"]})
            tl = r.get("timeline") or {}
            lane = tl.get("lane") or {}
            w = tl.get("games") or 0
            if w >= MIN_TL_GAMES and all(lane.get(k) is not None for k in LANE_KEYS):
                s = sums.setdefault(role, {"w": 0, "n": 0, **{k: 0.0 for k in LANE_KEYS}})
                s["w"] += w
                s["n"] += 1
                for k in LANE_KEYS:
                    s[k] += lane[k] * w
    baseline = {role: {"n": s["n"], **{k: s[k] / s["w"] for k in LANE_KEYS}} for role, s in sums.items() if s["n"] >= MIN_BASELINE_CHAMPS}
    return {"baseline": baseline, "lists": lists}


ITEM_USE_MIN_GAMES = 20      # a champion + role row needs this many games with the item to be listed
ITEM_USE_ROWS = 12

ITEM_USE_STR = {
    "fr": {
        "title": "Qui l'achète, et ce que disent nos parties",
        "intro": "{n} parties classées où {name} figure parmi les 6 objets les plus achetés du champion à son poste.",
        "pill_games": "Parties", "pill_wr": "Taux de victoire", "pill_lift": "Écart avec la moyenne du poste", "pill_champs": "Champions",
        "col_champ": "Champion", "col_role": "Poste", "col_games": "Parties", "col_wr": "Victoires", "col_diff": "Écart au poste",
        "note": "Échantillon : nos parties classées. Seuls les 6 objets les plus achetés de chaque champion à chaque poste sont comptés, "
                "et un objet acheté tard l'est surtout dans des parties longues, donc déjà bien engagées : l'écart est un indice, pas une preuve que l'objet fait gagner.",
        "diff_unit": "pt",
    },
    "en": {
        "title": "Who buys it, and what our games say",
        "intro": "{n} ranked games where {name} is one of the champion's 6 most bought items in their role.",
        "pill_games": "Games", "pill_wr": "Win rate", "pill_lift": "Gap to the role average", "pill_champs": "Champions",
        "col_champ": "Champion", "col_role": "Role", "col_games": "Games", "col_wr": "Win rate", "col_diff": "Gap to role",
        "note": "Sample: our ranked games. Only each champion's 6 most bought items in each role are counted, and an item bought late is mostly bought in "
                "long games that were already going somewhere, so the gap is a hint, not proof that the item wins games.",
        "diff_unit": "pt",
    },
}


def build_item_usage_index(guide_by_champion: dict) -> dict:
    """item id (str) -> [{cid, role, games, wins_rate, role_wr, role_games}] from the "top_items" of every champion + role of the guide data."""
    idx: dict[str, list] = {}
    for cid, g in guide_by_champion.items():
        for role, r in (g.get("roles") or {}).items():
            for t in r.get("top_items") or []:
                idx.setdefault(str(t["item_id"]), []).append({"cid": cid, "role": role, "games": t["games"], "win_rate": t["win_rate"],
                                                                "role_wr": r["win_rate"], "role_games": r["games"]})
    return idx


def item_usage_view(index: dict, item_id: str, item_name: str, champ_by_id: dict, lang: str, guide_slugs: set | None) -> dict | None:
    """The "who buys this item" block of a glossary item page, or None when no champion + role reaches ITEM_USE_MIN_GAMES games with it."""
    S = ITEM_USE_STR[lang]
    rows = [r for r in index.get(str(item_id), []) if r["games"] >= ITEM_USE_MIN_GAMES and r["cid"] in champ_by_id]
    if not rows:
        return None
    total = sum(r["games"] for r in rows)
    wr = sum(r["games"] * r["win_rate"] for r in rows) / total
    base = sum(r["games"] * r["role_wr"] for r in rows) / total
    fr = lang == "fr"

    def pct(x):
        return ("%.1f" % (x * 100)).replace(".", "," if fr else ".")

    def signed(x):
        return ("%+.1f" % (x * 100)).replace(".", "," if fr else ".").replace("-", "−")

    out_rows = []
    for r in sorted(rows, key=lambda r: -r["games"])[:ITEM_USE_ROWS]:
        c = champ_by_id[r["cid"]]
        d = r["win_rate"] - r["role_wr"]
        out_rows.append({"name": c["name_fr"] if fr else c["name_en"], "slug": c["slug"], "icon_file": c["icon_file"], "has_guide": bool(guide_slugs and c["slug"] in guide_slugs),
                         "role": ROLE_LABEL.get(r["role"], r["role"]), "games": r["games"], "wr": pct(r["win_rate"]), "diff": d, "diff_txt": signed(d)})
    champs = len({r["cid"] for r in rows})
    return {"t": S, "intro": S["intro"].format(n=f"{total:,}".replace(",", " " if fr else ","), name=item_name), "rows": out_rows,
            "games": total, "wr": pct(wr), "lift": signed(wr - base), "lift_pos": wr - base > 0, "champs": champs}


def build_role_view(*, S: dict, fr: bool, name: str, roles: dict, main_role: str, main: dict, role_ctx: dict | None, items_lookup: dict, guide_slugs: set | None,
                    champ_id: str, lang: str) -> dict | None:
    """The "what our games say about this role" blocks of a guide: lane against the role average, win rate by game length, the other roles of the champion
    and the other champions of the same role. Returns None when there is nothing to show."""
    R_ = S["role"]
    role_label = ROLE_LABEL.get(main_role, main_role)
    out: dict = {}
    # lane against the role average
    tl = main.get("timeline") or {}
    lane = tl.get("lane") or {}
    base = ((role_ctx or {}).get("baseline") or {}).get(main_role)
    if base and (tl.get("games") or 0) >= MIN_TL_GAMES and all(lane.get(k) is not None for k in LANE_KEYS):
        rows = []
        for k in LANE_KEYS:
            v, a = lane[k], base[k]
            rows.append({"label": R_["lane_labels"][k], "value": f"{v:.0f}", "avg": f"{a:.0f}", "diff": v - a, "diff_txt": f"{v - a:+.0f}".replace("-", "\u2212")})
        out["lane"] = {"rows": rows, "games": tl["games"], "champs": base["n"], "note": R_["lane_note"].format(games=tl["games"], name=name, champs=base["n"], role=role_label)}
    # win rate by game length
    buckets = [dict(x, label=S["bucket"][x["bucket"]][1], name=S["bucket"][x["bucket"]][0], pct=round(x["win_rate"] * 100, 1)) for x in main.get("duration", []) if x["games"] >= MIN_BUCKET_GAMES]
    if len(buckets) >= 2:
        best = max(buckets, key=lambda x: x["win_rate"])
        out["spikes"] = {"rows": buckets, "best": best["bucket"], "best_txt": R_["spikes_best"].format(name=best["name"], label=best["label"])}
    # the other roles of the champion
    others = []
    for role, r in sorted(roles.items(), key=lambda kv: -kv[1]["games"]):
        if role == main_role:
            continue
        its = [resolve_item(x["item_id"], items_lookup, lang) for x in (r.get("top_items") or [])[:3]]
        avg = r.get("avg") or {}
        others.append({"role": ROLE_LABEL.get(role, role), "games": r["games"], "win_rate": r["win_rate"], "cs": avg.get("cs_per_min"), "gold": avg.get("gold_per_min"),
                       "items": [i for i in its if i]})
    if others:
        out["others"] = others
    # the other champions of the same role
    pool = [x for x in ((role_ctx or {}).get("lists") or {}).get(main_role, []) if x["id"] != champ_id and (guide_slugs is None or x["slug"] in guide_slugs)]
    if len(pool) >= 6:
        played = sorted(pool, key=lambda x: -x["games"])[:8]
        seen = {x["id"] for x in played}
        strong = [x for x in sorted(pool, key=lambda x: -x["win_rate"]) if x["games"] >= 100 and x["id"] not in seen][:8]
        out["same_role"] = {"role": role_label, "played": played, "strong": strong}
    if not out:
        return None
    out["role_label"] = role_label
    out["t"] = {k: v.format(name=name, role=role_label) for k, v in R_.items() if isinstance(v, str) and k not in ("lane_note", "spikes_best")}
    out["has_main"] = bool(out.get("lane") or out.get("spikes") or out.get("others"))
    return out



def build_guide_view(*, lang: str, d: dict, champ: dict, guide: dict, editorial: dict | None, items_lookup: dict,
                     spells_by_key: dict, champ_by_slug: dict, tier_info: dict | None,
                     matchups_for_role: list[dict], rune_pages: list[dict],
                     rune_by_id: dict | None = None, tree_by_id: dict | None = None, patch: str = "", role_ctx: dict | None = None, guide_slugs: set | None = None) -> dict | None:
    """d: lol_champion_detail_view(...) output in `lang`. patch: the public patch name ("26.20", see patch_label), shown in the titles. guide: this champion's entry of lol_champion_guide.json.
    tier_info: {"tier", "rank", "of"} or None. matchups_for_role: enemies of the main role (already localized)."""
    S = STR[lang]
    fr = lang == "fr"
    roles = guide.get("roles") or {}
    if not roles:
        return None
    main_role, main = max(roles.items(), key=lambda kv: kv[1]["games"])
    name = d["name"]
    spell_by_key_early = {"Q": d["spells"][0], "W": d["spells"][1], "E": d["spells"][2], "R": d["spells"][3]} if len(d["spells"]) >= 4 else {}
    total_games = sum(r["games"] for r in roles.values())
    role_label = ROLE_LABEL.get(main_role, main_role)
    role_in = S["role_in"]
    main_share = main["games"] / total_games if total_games else 1
    other_roles = [(r, v["games"] / total_games) for r, v in sorted(roles.items(), key=lambda kv: -kv[1]["games"])[1:]
                   if v["games"] / total_games >= 0.10]
    P = S["pctsp"]

    # ---- summary paragraphs (composed from measured values only)
    classes = join_list([c.lower() for c in d["classes"]], lang)
    difficulty = (d.get("info") or {}).get("difficulty")
    diff = ""
    if difficulty:
        diff = S["difficulty"][0 if difficulty <= 3 else 1 if difficulty <= 6 else 2]
    if fr:
        intro = f"{name}, {d['title']}, est un champion de classe {classes}" + (f" {diff}" if diff else "") + ". "
        intro += f"Dans nos {total_games} parties classées analysées, {name} est joué principalement {role_in[main_role]} ({pct(main_share, 0)} % de ses parties)"
        if other_roles:
            intro += ", et plus rarement " + join_list([f"{role_in[r]} ({pct(s, 0)} %)" for r, s in other_roles], lang)
        intro += f", avec {pct(main['win_rate'])} % de victoires à ce poste"
        if tier_info:
            intro += f" : tier {tier_info['tier']} parmi les {role_label} (n°{tier_info['rank']} sur {tier_info['of']}, classés par winrate)"
    else:
        art = "an" if classes[:1] in "aeiou" else "a"
        intro = f"{name}, {d['title']}, is {art} {classes} champion" + (f" {diff}" if diff else "") + ". "
        intro += f"Across our {total_games} analysed ranked games, {name} is mostly played {role_in[main_role]} ({pct(main_share, 0)}% of its games)"
        if other_roles:
            intro += ", and more rarely " + join_list([f"{role_in[r]} ({pct(s, 0)}%)" for r, s in other_roles], lang)
        intro += f", with a {pct(main['win_rate'])}% win rate in that role"
        if tier_info:
            intro += f": tier {tier_info['tier']} among {role_label} champions (#{tier_info['rank']} of {tier_info['of']}, ranked by win rate)"
    intro += "."

    ds = main["damage_split"]
    dominant = max(ds, key=ds.get)
    if fr:
        if dominant == "magic" and ds["magic"] >= 0.6:
            damage = f"Les dégâts de {name} sont surtout magiques ({pct(ds['magic'], 0)} %) : les objets de résistance magique sont donc efficaces face à ce champion."
        elif dominant == "physical" and ds["physical"] >= 0.6:
            damage = f"Les dégâts de {name} sont surtout physiques ({pct(ds['physical'], 0)} %) : l'armure est le meilleur réflexe défensif face à ce champion."
        else:
            damage = (f"Les dégâts de {name} sont mixtes ({pct(ds['physical'], 0)} % physiques, {pct(ds['magic'], 0)} % magiques) : "
                      "empiler un seul type de résistance est moins rentable face à ce champion.")
        if ds["true"] >= 0.10:
            damage += f" {pct(ds['true'], 0)} % de ces dégâts sont bruts et ignorent donc les résistances."
    else:
        if dominant == "magic" and ds["magic"] >= 0.6:
            damage = f"{name}'s damage is mostly magic ({pct(ds['magic'], 0)}%): magic resistance items are therefore effective against this champion."
        elif dominant == "physical" and ds["physical"] >= 0.6:
            damage = f"{name}'s damage is mostly physical ({pct(ds['physical'], 0)}%): armor is the best defensive answer against this champion."
        else:
            damage = (f"{name}'s damage is mixed ({pct(ds['physical'], 0)}% physical, {pct(ds['magic'], 0)}% magic): "
                      "stacking a single type of resistance is less efficient against this champion.")
        if ds["true"] >= 0.10:
            damage += f" {pct(ds['true'], 0)}% of that damage is true damage and therefore ignores resistances."

    durations = [x for x in main["duration"] if x["games"] >= 30]
    timing = ""
    if len(durations) >= 2:
        best = max(durations, key=lambda x: x["win_rate"])
        worst = min(durations, key=lambda x: x["win_rate"])
        bn, br = S["bucket"][best["bucket"]]
        wn, wr = S["bucket"][worst["bucket"]]
        if best["win_rate"] - worst["win_rate"] >= 0.04:
            if fr:
                timing = (f"Le winrate varie avec la durée de la partie : {pct(best['win_rate'])} % de victoires dans les parties "
                          f"{bn} ({br}, {best['games']} parties) contre {pct(worst['win_rate'])} % dans les parties {wn} ({wr}).")
            else:
                timing = (f"Win rate varies with game length: {pct(best['win_rate'])}% in {bn} games "
                          f"({br}, {best['games']} games) versus {pct(worst['win_rate'])}% in {wn} games ({wr}).")
        else:
            if fr:
                timing = (f"Le winrate reste stable quelle que soit la durée de la partie ({pct(worst['win_rate'])} % à {pct(best['win_rate'])} %) : "
                          "le choix est fiable à toutes les phases du jeu.")
            else:
                timing = (f"Win rate stays steady whatever the game length ({pct(worst['win_rate'])}% to {pct(best['win_rate'])}%): "
                          "a reliable pick in every phase of the game.")

    avg = main["avg"]
    kda = (avg["kills"] + avg["assists"]) / max(avg["deaths"], 0.5)
    L = S["stats"]
    stats = [
        {"label": L[0], "value": f"{avg['kills']:.1f} / {avg['deaths']:.1f} / {avg['assists']:.1f}", "sub": f"{L[1]} {kda:.1f}"},
        {"label": L[2], "value": f"{avg['dpm']:.0f}"},
        {"label": L[3], "value": f"{avg['cs_per_min']:.1f}"},
        {"label": L[4], "value": f"{avg['gold_per_min']:.0f}"},
        {"label": L[5], "value": f"{avg['kp']:.0f}{P}"},
        {"label": L[6], "value": f"{avg['vision_per_min']:.2f}"},
    ]

    # ---- builds
    core_builds = []
    for b in main["core_builds"]:
        its = [resolve_item(i, items_lookup, lang) for i in b["items"]]
        if all(its):
            core_builds.append({"items": its, "games": b["games"], "win_rate": b["win_rate"]})
    top_items = []
    if not core_builds:
        for x in main.get("top_items", []):
            it = resolve_item(x["item_id"], items_lookup, lang)
            if it:
                top_items.append({**it, "games": x["games"], "win_rate": x["win_rate"], "share": x["games"] / main["games"]})
        top_items = top_items[:6]
    boots = [{**x, **(resolve_item(x["item_id"], items_lookup, lang) or {})} for x in main["boots"] if resolve_item(x["item_id"], items_lookup, lang)]
    spells = []
    for s in main["spells"]:
        pair = [spells_by_key.get(str(i)) for i in s["ids"]]
        if all(pair):
            spells.append({"spells": pair, "games": s["games"], "win_rate": s["win_rate"]})
    builds_text = ""
    if core_builds:
        top = core_builds[0]
        names = join_list([i["name"] for i in top["items"]], lang)
        if fr:
            builds_text = f"Le build de base le plus joué réunit {names} ({top['games']} parties, {pct(top['win_rate'])} % de victoires)"
            if boots:
                builds_text += f", généralement avec {boots[0]['name']} ({pct(boots[0]['win_rate'])} % sur {boots[0]['games']} parties)"
        else:
            builds_text = f"The most-played core build is {names} ({top['games']} games, {pct(top['win_rate'])}% win rate)"
            if boots:
                builds_text += f", usually with {boots[0]['name']} ({pct(boots[0]['win_rate'])}% over {boots[0]['games']} games)"
        builds_text += "."
    elif len(top_items) >= 3:
        names = join_list([i["name"] for i in top_items[:3]], lang)
        if fr:
            builds_text = f"Les builds varient beaucoup ; les objets terminés les plus construits sont {names} (achetés dans {pct(top_items[0]['share'])} % des parties pour le premier)."
        else:
            builds_text = f"Builds vary a lot; the most-built finished items are {names} (the first is bought in {pct(top_items[0]['share'])}% of games)."

    # ---- skill order / start items / item path (only when lol_timeline_run.py has been run; see lol_timeline.py)
    timeline = None
    tl = main.get("timeline")
    if tl:
        letters = ("Q", "W", "E", "R")
        skill_orders = []
        for row in tl.get("skills", []):
            lv = row["levels"]
            skill_orders.append({
                "order": " > ".join(row["order"].split(">")), "games": row["games"], "win_rate": row["win_rate"],
                "grid": [{"key": k, "icon": (spell_by_key_early.get(k) or {}).get("icon_file"),
                          "cells": [i < len(lv) and lv[i] == k for i in range(15)]} for k in letters],
            })

        def items_of(entries):
            out = []
            for e in entries:
                its = [resolve_item(i, items_lookup, lang) for i in e["items"]]
                if all(its):
                    out.append({"items": its, "games": e["games"], "win_rate": e["win_rate"]})
            return out

        lane = tl.get("lane") or {}
        lane_text = ""
        if all(lane.get(k) is not None for k in ("gold_at10", "cs_at10", "xp_at10", "gold_at15", "cs_at15", "xp_at15")):
            lane_text = S["lane_text"].format(g10=f"{lane['gold_at10']:.0f}", c10=f"{lane['cs_at10']:.0f}", x10=f"{lane['xp_at10']:.0f}",
                                                    g15=f"{lane['gold_at15']:.0f}", c15=f"{lane['cs_at15']:.0f}", x15=f"{lane['xp_at15']:.0f}")
        timeline = {"skills": skill_orders, "start_items": items_of(tl.get("start_items", [])), "item_paths": items_of(tl.get("item_paths", [])),
                    "lane_text": lane_text, "games": tl["games"]}
        if not (skill_orders or timeline["start_items"] or timeline["item_paths"] or lane_text):
            timeline = None

    # ---- items depending on the enemy team
    vs_enemy = []
    for key in ("ap", "ad", "mixed"):
        v = main["vs_enemy"].get(key)
        if not v:
            continue
        items = []
        for it in v["items"][:6]:
            r = resolve_item(it["item_id"], items_lookup, lang)
            if r:
                tag = "up" if it["lift"] >= NOTABLE_LIFT and it["games"] >= MIN_LIFT_GAMES else "down" if it["lift"] <= -NOTABLE_LIFT and it["games"] >= MIN_LIFT_GAMES else ""
                items.append({**r, "games": it["games"], "win_rate": it["win_rate"], "lift": it["lift"], "tag": tag})
        standout = [i for i in items if i["tag"] == "up"]
        if standout:
            best_i = max(standout, key=lambda i: i["lift"])
            if fr:
                note = f"L'objet qui se démarque le plus est {best_i['name']} : {pct(best_i['win_rate'])} % de victoires, soit {best_i['lift'] * 100:+.0f} points par rapport à son winrate habituel."
            else:
                note = f"The item that stands out most is {best_i['name']}: {pct(best_i['win_rate'])}% win rate, {best_i['lift'] * 100:+.0f} points versus its usual win rate."
        else:
            note = ("Aucun objet ne se démarque nettement dans cette situation : le build habituel reste la référence." if fr
                    else "No item clearly stands out in this situation: the usual build remains the reference.")
        title, rule = S["enemy"][key]
        vs_enemy.append({"key": key, "title": title, "rule": rule, "games": v["games"], "win_rate": v["win_rate"], "items": items, "note": note})

    # ---- matchups (main role): hardest / easiest
    pool = [m for m in matchups_for_role if m["games"] >= MIN_MATCHUP_GAMES]
    hardest = sorted(pool, key=lambda m: m["win_rate"])[:5]
    easiest = sorted(pool, key=lambda m: -m["win_rate"])[:5]
    if fr:
        hardest = [{**m, "edge": f"{m['name']} prend l'avantage dans {pct(1 - m['win_rate'], 0)} % des {m['games']} duels {role_label} contre {name}."} for m in hardest]
    else:
        hardest = [{**m, "edge": f"{m['name']} has the edge in {pct(1 - m['win_rate'], 0)}% of the {m['games']} {role_label} duels against {name}."} for m in hardest]
    easiest = [dict(m) for m in easiest]
    # Data Dragon sometimes ships the champion's lore as its only "tip" (Naafiri, 16.19): drop
    # any tip that is a slice of the lore/blurb so a story paragraph never shows up as advice.
    _lore = champ.get(f"lore_{lang}", "") + " " + champ.get(f"blurb_{lang}", "")
    enemy_tips = [t for t in champ.get(f"enemytips_{lang}", []) if t[:80] not in _lore]
    ally_tips = [t for t in champ.get(f"allytips_{lang}", []) if t[:80] not in _lore]
    has_contres = bool(hardest or easiest or enemy_tips)

    # ---- full rune pages (measured from the cached matches; see lol_guide.py)
    name_key = "name_fr" if fr else "name_en"
    rune_builds = []
    for rp in (main.get("runes") or []) if rune_by_id and tree_by_id else []:
        ks, pt, st = rune_by_id.get(rp["keystone"]), tree_by_id.get(rp["primary_tree"]), tree_by_id.get(rp["secondary_tree"])
        if not (ks and pt and st):
            continue

        def rune_ref(entry):
            r = rune_by_id.get(entry["id"])
            return {"name": r[name_key], "icon": r["icon_file"], "share": entry["share"]} if r else None

        rows = [rune_ref(e) for e in rp["primary_rows"]]
        sec = [rune_ref(e) for e in rp["secondary"]]
        if not all(rows) or len(sec) < 2 or not all(sec):
            continue
        shards = [{"name": SHARD_NAMES[e["id"]][0 if fr else 1], "share": e["share"]} for e in rp["shards"] if e and e["id"] in SHARD_NAMES]
        rune_builds.append({
            "keystone": {"name": ks[name_key], "icon": ks["icon_file"]}, "primary_tree": {"name": pt[name_key], "icon": pt["icon_file"]},
            "secondary_tree": {"name": st[name_key], "icon": st["icon_file"]}, "rows": rows, "secondary": sec, "shards": shards,
            "games": rp["games"], "win_rate": rp["win_rate"], "keystone_name": ks[name_key], "tree_name": st[name_key],
        })
    if rune_builds:
        rune_pages = rune_builds

    # ---- FAQ, only from data we have
    faq = []
    if fr:
        if builds_text:
            faq.append({"q": f"Quel est le meilleur build pour {name} ?", "a": builds_text})
        if hardest:
            faq.append({"q": f"Qui contre {name} ?",
                        "a": f"Les matchups les plus difficiles de {name} {role_in[main_role]} sont " + join_list(
                            [f"{m['name']} ({pct(m['win_rate'])} % de victoires sur {m['games']} parties)" for m in hardest[:3]], lang) + "."})
        if easiest:
            faq.append({"q": f"Quels sont les meilleurs matchups de {name} ?",
                        "a": f"{name} affiche ses meilleurs winrates contre " + join_list([f"{m['name']} ({pct(m['win_rate'])} %)" for m in easiest[:3]], lang) + "."})
        if timing:
            faq.append({"q": f"Quelle durée de partie convient le mieux à {name} ?", "a": timing})
        if rune_pages:
            rp = rune_pages[0]
            faq.append({"q": f"Quelles runes jouer avec {name} ?",
                        "a": f"La page de runes la plus jouée utilise {rp['keystone_name']} avec l'arbre secondaire {rp['tree_name']} "
                             f"({rp['games']} parties, {pct(rp['win_rate'])} % de victoires)."})
    else:
        if builds_text:
            faq.append({"q": f"What is the best build for {name}?", "a": builds_text})
        if hardest:
            faq.append({"q": f"Who counters {name}?",
                        "a": f"{name}'s toughest matchups {role_in[main_role]} are " + join_list(
                            [f"{m['name']} ({pct(m['win_rate'])}% win rate over {m['games']} games)" for m in hardest[:3]], lang) + "."})
        if easiest:
            faq.append({"q": f"What are {name}'s best matchups?",
                        "a": f"{name} posts its best win rates against " + join_list([f"{m['name']} ({pct(m['win_rate'])}%)" for m in easiest[:3]], lang) + "."})
        if timing:
            faq.append({"q": f"What game length suits {name} best?", "a": timing})
        if rune_pages:
            rp = rune_pages[0]
            faq.append({"q": f"Which runes should I play on {name}?",
                        "a": f"The most-played rune page uses {rp['keystone_name']} with the {rp['tree_name']} secondary tree "
                             f"({rp['games']} games, {pct(rp['win_rate'])}% win rate)."})

    # ---- editorial (hand-written) -> attach ability icons to each combo key
    spell_by_key = {"Q": d["spells"][0], "W": d["spells"][1], "E": d["spells"][2], "R": d["spells"][3]} if len(d["spells"]) >= 4 else {}
    ed = None
    if editorial:
        ed = {
            "playstyle": editorial.get("playstyle", ""), "laning": editorial.get("laning", ""),
            "mistakes": editorial.get("mistakes", []),
            "teamfight": editorial.get("teamfight", ""), "strengths": editorial.get("strengths", []), "weaknesses": editorial.get("weaknesses", []),
            "combos": [{
                "name": cb["name"], "when": cb["when"], "how": cb["how"],
                "seq": [{"key": k, "icon": (spell_by_key.get(k) or {}).get("icon_file"), "name": (spell_by_key.get(k) or {}).get("name", S["aa"])}
                         for k in cb["keys"]],
            } for cb in editorial.get("combos", [])],
        }

    kwi = 0 if has_contres else 1
    tfmt = dict(name=name, role=role_label, patch=patch, kw=S["seo_kw"][kwi], kw2=S["seo_kw2"][kwi])
    seo_title = next(t for t in (v.format(**tfmt) for v in S["seo_title"] if patch or "{patch}" not in v) if len(t) <= 60)
    seo_title = "BrokenMeta.gg | " + seo_title       # build_site.py's seo_title filter moves the brand to the end, and only when it still fits in 60 characters
    dfmt = dict(name=name, role=role_label, n=main["games"], patch=patch, counters=S["seo_counters"] if has_contres else "")
    seo_description = next(t for t in (v.format(**dfmt) for v in S["seo_desc"] if patch or "{patch}" not in v) if len(t) <= 155)

    ui = {k: v.format(name=name, role=role_label, role_in=role_in[main_role], games=main["games"], tier=(tier_info or {}).get("tier", ""), enemy="{enemy}", tl_games="{tl_games}")
          for k, v in S["ui"].items()}
    return {
        "role_view": build_role_view(S=S, fr=fr, name=name, roles=roles, main_role=main_role, main=main, role_ctx=role_ctx, items_lookup=items_lookup,
                                     guide_slugs=guide_slugs, champ_id=champ["id"], lang=lang),
        "lang": lang, "ui": ui, "id": d["id"], "patch": patch, "seo_title": seo_title, "seo_description": seo_description,
        "name": name, "title": d["title"], "slug": d["slug"], "icon_file": d["icon_file"], "classes": d["classes"],
        "main_role": main_role, "role_label": role_label, "roles": [{"role": r, "label": ROLE_LABEL.get(r, r), "games": v["games"], "win_rate": v["win_rate"]}
                                                                    for r, v in sorted(roles.items(), key=lambda kv: -kv[1]["games"])],
        "games": main["games"], "win_rate": main["win_rate"], "tier": tier_info, "difficulty": difficulty,
        "intro": intro, "damage": damage, "timing": timing, "stats": stats,
        "damage_split": ds, "durations": main["duration"],
        "editorial": ed, "ally_tips": ally_tips, "enemy_tips": enemy_tips,
        "passive": d["passive"], "spells": d["spells"],
        "core_builds": core_builds, "boots": boots, "summoner_spells": spells, "builds_text": builds_text,
        "best_items": d["best_items"][:8], "rune_pages": rune_pages[:3], "rune_builds": rune_builds, "timeline": timeline, "top_items": top_items,
        "vs_enemy": vs_enemy, "hardest": hardest, "easiest": easiest,
        "faq": faq, "has_contres": has_contres,
    }


def patch_label(dd_version: str) -> str:
    """The public patch name read from the Data Dragon version: "16.20.1" -> "26.20". Data Dragon's major is the year minus 2010 while Riot's patch names use
    the year minus 2000 since 2025 (26.18 on 2026-09-09 on the patch notes page, Data Dragon 16.20.1 in October). "" when the version cannot be read."""
    m = re.match(r"(\d+)\.(\d+)", dd_version or "")
    return f"{int(m.group(1)) + 10}.{m.group(2)}" if m else ""


def build_combo_view(g: dict, lang: str, patch: str = "") -> dict | None:
    """Extra bits for /league/combos/<champion>/, built on top of a guide view `g`.

    Search Console (2026-09-26): '<champion> combo' is the League query family the guides
    already rank for (positions 6-10 over ~170 distinct queries) but the snippet says
    "Guide", so almost nobody clicks. This page answers that query directly: the written
    combos first, then each ability's cooldown / cost / range and the measured skill order.
    Every sentence comes from the guide view (editorial combos, Data Dragon, timelines)."""
    ed = g.get("editorial")
    if not ed or not ed.get("combos"):
        return None
    fr = lang == "fr"
    name = g["name"]
    keys = ["Q", "W", "E", "R"]
    abilities = [{"key": keys[i], **sp} for i, sp in enumerate(g["spells"][:4])]
    first = ed["combos"][0]
    seq = " › ".join(k["key"] for k in first["seq"])
    n = len(ed["combos"])
    # 2026-10-14: "<Champion> Combos (Patch X.Y) : touches et temps de recharge" (the page has the key order with the ability icons, when to cast each combo and
    # every ability's cooldown, cost and range; no videos: promise nothing else). Longest first, the first that fits in 60 characters wins; the seo_title filter
    # of build_site.py then appends the brand only if it still fits.
    pp = f" (Patch {patch})" if patch else ""
    ttl = (f"{name} Combos{pp} : touches et temps de recharge", f"{name} Combos{pp} : touches", f"{name} Combos{pp}", f"{name} Combos") if fr else (
           f"{name} Combos{pp}: key order & cooldowns", f"{name} Combos{pp}: key order", f"{name} Combos{pp}", f"{name} Combos")
    title = "BrokenMeta.gg | " + next(t for t in ttl if len(t) <= 60 or t is ttl[-1])
    pd = f" (patch {patch})" if patch else ""
    dsc = (f"Combos {name}{pd} : {n} enchaînements expliqués touche par touche (le principal : {seq}), quand les lancer, et le temps de recharge, le coût et la portée de chaque sort.",
           f"Combos {name}{pd} : {n} enchaînements expliqués touche par touche, et le temps de recharge et le coût de chaque sort.",
           f"Combos {name} : {n} enchaînements expliqués, temps de recharge de chaque sort.") if fr else (
           f"{name} combos{pd}: {n} combos explained key by key (main one: {seq}), when to cast them, plus every ability's cooldown, cost and range.",
           f"{name} combos{pd}: {n} combos explained key by key, plus every ability's cooldown and cost.",
           f"{name} combos: {n} combos explained, with every ability's cooldown.")
    description = next((d for d in dsc if len(d) <= 155), dsc[-1][:155])

    faq = []
    faq.append({"q": f"Quel est le combo principal de {name} ?" if fr else f"What is {name}'s main combo?",
                "a": (f"{first['name']} : {seq}. " if fr else f"{first['name']}: {seq}. ") + f"{first['when']} {first['how']}"})
    so = ((g.get("timeline") or {}).get("skills") or [None])[0]
    if so:
        wr = f"{so['win_rate'] * 100:.1f}"
        faq.append({"q": f"Quelle compétence monter en premier sur {name} ?" if fr else f"Which ability should I max first on {name}?",
                    "a": (f"L'ordre de montée le plus joué est {so['order']} ({so['games']} parties, {wr.replace('.', ',')} % de victoires)."
                          if fr else f"The most-played max order is {so['order']} ({so['games']} games, {wr}% win rate).")})
    ult = abilities[3] if len(abilities) == 4 else None
    if ult and ult.get("cooldown") and ult["cooldown"] != "0":
        faq.append({"q": f"Quel est le temps de recharge de l'ultime de {name} ?" if fr else f"What is the cooldown of {name}'s ultimate?",
                    "a": (f"{ult['name']} a un temps de recharge de {ult['cooldown']} secondes selon son rang."
                          if fr else f"{ult['name']} has a {ult['cooldown']} second cooldown depending on its rank.")})
    return {"seo_title": title, "seo_description": description, "abilities": abilities, "faq": faq, "main_seq": seq, "n": n}
