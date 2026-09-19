"""View-model for one League champion guide (/league/guide/<champion>/).

Pure functions over already-loaded data (see src/tft_tracker/lol_guide.py for
how the measured aggregates are produced, and lol_guides_editorial.py for the
hand-written combos). Nothing here fabricates a number: every sentence is
composed from a measured value or an official Riot text, and every section
returns nothing when its sample is too small -- the template then omits it.

French only for now: the English version follows once the layout is validated.
"""
from __future__ import annotations

ROLE_LABEL = {"top": "Top", "jungle": "Jungle", "mid": "Mid", "adc": "ADC", "support": "Support"}
ROLE_IN_FR = {"top": "en Top", "jungle": "en Jungle", "mid": "en Mid", "adc": "en ADC", "support": "en Support"}
BUCKET_TEXT = {
    "short": ("courtes", "moins de 25 min"),
    "mid": ("moyennes", "25 à 35 min"),
    "long": ("longues", "plus de 35 min"),
}
ENEMY_BUCKET = {
    "ap": {"title": "Équipe adverse surtout magique", "rule": "au moins 50 % de leurs dégâts sont magiques",
           "short": "une équipe adverse surtout magique"},
    "ad": {"title": "Équipe adverse surtout physique", "rule": "moins de 35 % de leurs dégâts sont magiques",
           "short": "une équipe adverse surtout physique"},
    "mixed": {"title": "Équipe adverse équilibrée", "rule": "dégâts physiques et magiques mélangés",
              "short": "une équipe adverse équilibrée"},
}
MIN_MATCHUP_GAMES = 15
MIN_LIFT_GAMES = 25
NOTABLE_LIFT = 0.03


def pct(x: float, digits: int = 1) -> str:
    return f"{x * 100:.{digits}f}"


def difficulty_text(v: int | None) -> str:
    if not v:
        return ""
    if v <= 3:
        return "plutôt simple à prendre en main"
    if v <= 6:
        return "de difficulté moyenne"
    return "exigeant à maîtriser"


def join_fr(items: list[str]) -> str:
    items = [i for i in items if i]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " et " + items[-1]


def resolve_item(item_id: int, lookup: dict) -> dict | None:
    ref = lookup.get(str(item_id))
    if not ref:
        return None
    return {"id": item_id, "name": ref["name_fr"], "icon_file": ref["icon_file"], "slug": ref["slug"], "has_page": ref["has_page"]}


def build_guide_view(*, d: dict, champ: dict, guide: dict, editorial: dict | None, items_lookup: dict,
                     spells_by_key: dict, champ_by_slug: dict, tier_info: dict | None,
                     matchups_for_role: list[dict], rune_pages: list[dict]) -> dict | None:
    """d: lol_champion_detail_view(...) output (fr). guide: this champion's entry of lol_champion_guide.json.
    tier_info: {"tier", "rank", "of"} or None. matchups_for_role: enemies of the main role."""
    roles = guide.get("roles") or {}
    if not roles:
        return None
    main_role, main = max(roles.items(), key=lambda kv: kv[1]["games"])
    name = d["name"]
    total_games = sum(r["games"] for r in roles.values())
    role_label = ROLE_LABEL.get(main_role, main_role)
    main_share = main["games"] / total_games if total_games else 1
    other_roles = [(r, v["games"] / total_games) for r, v in sorted(roles.items(), key=lambda kv: -kv[1]["games"])[1:]
                   if v["games"] / total_games >= 0.10]

    # ---- summary paragraphs (composed from measured values only)
    classes = join_fr([c.lower() for c in d["classes"]])
    diff = difficulty_text((d.get("info") or {}).get("difficulty"))
    intro = f"{name}, {d['title']}, est un champion de classe {classes}" + (f" {diff}" if diff else "") + ". "
    intro += f"Dans nos {total_games} parties classées analysées, {name} est joué principalement {ROLE_IN_FR[main_role]} ({pct(main_share, 0)} % de ses parties)"
    if other_roles:
        intro += ", et plus rarement " + join_fr([f"{ROLE_IN_FR[r]} ({pct(s, 0)} %)" for r, s in other_roles])
    intro += f", avec {pct(main['win_rate'])} % de victoires à ce poste"
    if tier_info:
        intro += f" : tier {tier_info['tier']} parmi les {role_label} (n°{tier_info['rank']} sur {tier_info['of']}, classés par winrate)"
    intro += "."

    ds = main["damage_split"]
    dominant = max(ds, key=ds.get)
    if dominant == "magic" and ds["magic"] >= 0.6:
        damage = (f"Les dégâts de {name} sont surtout magiques ({pct(ds['magic'], 0)} %) : les objets de résistance magique sont donc efficaces face à ce champion.")
    elif dominant == "physical" and ds["physical"] >= 0.6:
        damage = (f"Les dégâts de {name} sont surtout physiques ({pct(ds['physical'], 0)} %) : l'armure est le meilleur réflexe défensif face à ce champion.")
    else:
        damage = (f"Les dégâts de {name} sont mixtes ({pct(ds['physical'], 0)} % physiques, {pct(ds['magic'], 0)} % magiques) : "
                  "empiler un seul type de résistance est moins rentable face à ce champion.")
    if ds["true"] >= 0.10:
        damage += f" {pct(ds['true'], 0)} % de ces dégâts sont bruts et ignorent donc les résistances."

    durations = [x for x in main["duration"] if x["games"] >= 30]
    timing = ""
    if len(durations) >= 2:
        best = max(durations, key=lambda x: x["win_rate"])
        worst = min(durations, key=lambda x: x["win_rate"])
        if best["win_rate"] - worst["win_rate"] >= 0.04:
            timing = (f"Le winrate varie avec la durée de la partie : {pct(best['win_rate'])} % de victoires dans les parties "
                      f"{BUCKET_TEXT[best['bucket']][0]} ({BUCKET_TEXT[best['bucket']][1]}, {best['games']} parties) contre "
                      f"{pct(worst['win_rate'])} % dans les parties {BUCKET_TEXT[worst['bucket']][0]} ({BUCKET_TEXT[worst['bucket']][1]}).")
        else:
            timing = (f"Le winrate reste stable quelle que soit la durée de la partie ({pct(worst['win_rate'])} % à {pct(best['win_rate'])} %) : "
                      "le choix est fiable à toutes les phases du jeu.")

    avg = main["avg"]
    kda = (avg["kills"] + avg["assists"]) / max(avg["deaths"], 0.5)
    stats = [
        {"label": "KDA moyen", "value": f"{avg['kills']:.1f} / {avg['deaths']:.1f} / {avg['assists']:.1f}", "sub": f"ratio {kda:.1f}"},
        {"label": "Dégâts / min", "value": f"{avg['dpm']:.0f}"},
        {"label": "CS / min", "value": f"{avg['cs_per_min']:.1f}"},
        {"label": "Or / min", "value": f"{avg['gold_per_min']:.0f}"},
        {"label": "Participation aux kills", "value": f"{avg['kp']:.0f} %"},
        {"label": "Vision / min", "value": f"{avg['vision_per_min']:.2f}"},
    ]

    # ---- builds
    core_builds = []
    for b in main["core_builds"]:
        its = [resolve_item(i, items_lookup) for i in b["items"]]
        if all(its):
            core_builds.append({"items": its, "games": b["games"], "win_rate": b["win_rate"]})
    boots = [{**x, **(resolve_item(x["item_id"], items_lookup) or {})} for x in main["boots"] if resolve_item(x["item_id"], items_lookup)]
    spells = []
    for s in main["spells"]:
        pair = [spells_by_key.get(str(i)) for i in s["ids"]]
        if all(pair):
            spells.append({"spells": pair, "games": s["games"], "win_rate": s["win_rate"]})
    builds_text = ""
    if core_builds:
        top = core_builds[0]
        builds_text = (f"Le build de base le plus joué réunit {join_fr([i['name'] for i in top['items']])} "
                       f"({top['games']} parties, {pct(top['win_rate'])} % de victoires)")
        if boots:
            builds_text += f", généralement avec {boots[0]['name']} ({pct(boots[0]['win_rate'])} % sur {boots[0]['games']} parties)"
        builds_text += "."

    # ---- items depending on the enemy team
    vs_enemy = []
    for key in ("ap", "ad", "mixed"):
        v = main["vs_enemy"].get(key)
        if not v:
            continue
        items = []
        for it in v["items"][:6]:
            r = resolve_item(it["item_id"], items_lookup)
            if r:
                tag = "up" if it["lift"] >= NOTABLE_LIFT and it["games"] >= MIN_LIFT_GAMES else "down" if it["lift"] <= -NOTABLE_LIFT and it["games"] >= MIN_LIFT_GAMES else ""
                items.append({**r, "games": it["games"], "win_rate": it["win_rate"], "lift": it["lift"], "tag": tag})
        standout = [i for i in items if i["tag"] == "up"]
        if standout:
            best = max(standout, key=lambda i: i["lift"])
            note = f"L'objet qui se démarque le plus est {best['name']} : {pct(best['win_rate'])} % de victoires, soit {best['lift'] * 100:+.0f} points par rapport à son winrate habituel."
        else:
            note = "Aucun objet ne se démarque nettement dans cette situation : le build habituel reste la référence."
        vs_enemy.append({"key": key, **ENEMY_BUCKET[key], "games": v["games"], "win_rate": v["win_rate"], "items": items, "note": note})

    # ---- matchups (main role): hardest / easiest, with Riot's own tips against each hardest counter
    pool = [m for m in matchups_for_role if m["games"] >= MIN_MATCHUP_GAMES]
    hardest = sorted(pool, key=lambda m: m["win_rate"])[:5]
    easiest = sorted(pool, key=lambda m: -m["win_rate"])[:5]

    hardest = [{**m, "edge": f"{m['name']} prend l'avantage dans {pct(1 - m['win_rate'], 0)} % des {m['games']} duels {ROLE_LABEL.get(main_role, main_role)} contre {name}."}
               for m in hardest]
    easiest = [dict(m) for m in easiest]
    has_contres = bool(hardest or easiest or champ.get("enemytips_fr"))

    # ---- FAQ, only from data we have
    faq = []
    if core_builds:
        faq.append({"q": f"Quel est le meilleur build pour {name} ?", "a": builds_text})
    if hardest:
        faq.append({"q": f"Qui contre {name} ?",
                    "a": f"Les matchups les plus difficiles de {name} {ROLE_IN_FR[main_role]} sont " + join_fr(
                        [f"{m['name']} ({pct(m['win_rate'])} % de victoires sur {m['games']} parties)" for m in hardest[:3]]) + "."})
    if easiest:
        faq.append({"q": f"Quels sont les meilleurs matchups de {name} ?",
                    "a": f"{name} affiche ses meilleurs winrates contre " + join_fr(
                        [f"{m['name']} ({pct(m['win_rate'])} %)" for m in easiest[:3]]) + "."})
    if timing:
        faq.append({"q": f"Quelle durée de partie convient le mieux à {name} ?", "a": timing})
    if rune_pages:
        rp = rune_pages[0]
        faq.append({"q": f"Quelles runes jouer avec {name} ?",
                    "a": f"La page de runes la plus jouée utilise {rp['keystone_name']} avec l'arbre secondaire {rp['tree_name']} "
                         f"({rp['games']} parties, {pct(rp['win_rate'])} % de victoires)."})

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
                "seq": [{"key": k, "icon": (spell_by_key.get(k) or {}).get("icon_file"), "name": (spell_by_key.get(k) or {}).get("name", "Attaque de base")}
                         for k in cb["keys"]],
            } for cb in editorial.get("combos", [])],
        }

    kw = "combos, build, contres" if has_contres else "combos et build"
    seo_title = next(t for t in (
        f"Guide {name} {role_label} : {kw} | BrokenMeta.gg",
        f"Guide {name} : {kw} | BrokenMeta.gg",
        f"Guide {name} : combos et build | BrokenMeta.gg",
        f"Guide {name} | BrokenMeta.gg",
    ) if len(t) <= 60)
    seo_description = next(t for t in (
        f"Guide {name} {role_label} : combos, build, runes, contres et objets selon l'équipe adverse, mesurés sur {main['games']} parties {role_label}.",
        f"Guide {name} {role_label} : combos, build, runes, contres et objets selon l'équipe adverse.",
        f"Guide {name} : combos, build, runes et contres.",
    ) if len(t) <= 155)
    return {
        "id": d["id"], "seo_title": seo_title, "seo_description": seo_description,
        "name": name, "title": d["title"], "slug": d["slug"], "icon_file": d["icon_file"], "classes": d["classes"],
        "main_role": main_role, "role_label": role_label, "roles": [{"role": r, "label": ROLE_LABEL.get(r, r), "games": v["games"], "win_rate": v["win_rate"]}
                                                                    for r, v in sorted(roles.items(), key=lambda kv: -kv[1]["games"])],
        "games": main["games"], "win_rate": main["win_rate"], "tier": tier_info, "difficulty": (d.get("info") or {}).get("difficulty"),
        "intro": intro, "damage": damage, "timing": timing, "stats": stats,
        "damage_split": ds, "durations": main["duration"],
        "editorial": ed, "ally_tips": champ.get("allytips_fr", []), "enemy_tips": champ.get("enemytips_fr", []),
        "passive": d["passive"], "spells": d["spells"],
        "core_builds": core_builds, "boots": boots, "summoner_spells": spells, "builds_text": builds_text,
        "best_items": d["best_items"][:8], "rune_pages": rune_pages[:3],
        "vs_enemy": vs_enemy, "hardest": hardest, "easiest": easiest,
        "faq": faq, "has_contres": has_contres,
    }
