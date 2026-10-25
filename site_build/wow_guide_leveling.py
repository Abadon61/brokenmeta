"""'Monter de 1 à 60' section of the spec guides (2026-10-25, user decision: option A).

What is solid (client data, wow_talents.RULES): the first talent point comes at level 10, then one per level (51 at level 60), a row of a tree opens for
every 5 points spent in that tree, and some talents need other talents. What is derived, and said so on the page: the ORDER of the points. It is
computed from the guide's level-60 build and the tree rules, taking at each point the talent the simulation values most per point among those the rules
allow (a spec the simulator does not rank, the healers, has no values: its order follows the rows of the tree). It was never tested on a character
that levels, and the page says it. Dungeons of each level band and the best item of the spec in each come from the dungeon data and the
simulator's stat weights (wow_bis_optimizer.dungeon_picks), the same source as the dungeon pages.
"""

FIRST_LEVEL = 10
STEPS = (10, 20, 30, 40, 50, 60)
BANDS = {10: (10, 20), 20: (20, 30), 30: (30, 40), 40: (40, 50), 50: (50, 60)}      # first level of a dungeon's range -> band (same as the dungeons hub)

TX = {
    "fr": {
        "h2": "Monter {cls} {spec} de 1 à 60", "kicker": "LEVELING",
        "intro": "Le premier point de talent arrive au niveau 10, puis un par niveau : 1 point au niveau 10, 11 au niveau 20, 21 au niveau 30, 31 au niveau 40, 41 au niveau 50 et 51 au niveau 60. Une rangée d'un arbre s'ouvre tous les 5 points dépensés dans cet arbre.",
        "note_sim": "Ordre déduit : nous l'avons calculé à partir du build niveau 60 de notre simulateur, en respectant les règles des arbres (rangées, prérequis) et en prenant à chaque point le talent que la simulation valorise le plus. Il n'a pas été testé en montant un personnage : c'est une base de départ, pas un build de leveling éprouvé, à revoir avec les données du jeu sorti.",
        "note_rows": "Ordre déduit : le simulateur ne classe pas les soigneurs, l'ordre suit donc les rangées de l'arbre, du haut vers le bas, à partir du build niveau 60. Il n'a pas été testé en montant un personnage : c'est une base de départ, à revoir avec les données du jeu sorti.",
        "none": "Niveaux 1 à 9 : pas encore de point de talent, le premier arrive au niveau 10.",
        "step_h": "Niveau {lv} : {pts} point{s} de talent", "step_h60": "Niveau 60 : {pts} points, build complet", "step_levels": "(niveaux {lo} à {hi})",
        "take": "À prendre : {list}.", "tree": "Voir l'arbre à ce palier", "dung": "Donjons de ces niveaux", "dung_all": "Tous les donjons de ce niveau",
        "best": "meilleur objet", "no_dung": "Pas de donjon de WoW Forever qui commence dans cette tranche de niveau.", "lvl": "niveaux {lo}-{hi}",
        "guide": "Guide de leveling 1-60 (zones, métiers)", "calc_all": "Calculateur de talents",
    },
    "en": {
        "h2": "Leveling {spec} {cls} from 1 to 60", "kicker": "LEVELING",
        "intro": "The first talent point comes at level 10, then one per level: 1 point at level 10, 11 at level 20, 21 at level 30, 31 at level 40, 41 at level 50 and 51 at level 60. A row of a tree opens for every 5 points spent in that tree.",
        "note_sim": "Derived order: we computed it from our simulator's level-60 build, following the tree rules (rows, prerequisites) and taking at each point the talent the simulation values most. It was not tested while leveling a character: it is a starting point, not a proven leveling build, to be revisited with the released game's data.",
        "note_rows": "Derived order: the simulator does not rank healers, so the order follows the rows of the tree, top to bottom, from the level-60 build. It was not tested while leveling a character: it is a starting point, to be revisited with the released game's data.",
        "none": "Levels 1 to 9: no talent point yet, the first one comes at level 10.",
        "step_h": "Level {lv}: {pts} talent point{s}", "step_h60": "Level 60: {pts} points, full build", "step_levels": "(levels {lo} to {hi})",
        "take": "Take: {list}.", "tree": "See the tree at this step", "dung": "Dungeons at these levels", "dung_all": "All dungeons at this level",
        "best": "best item", "no_dung": "No WoW Forever dungeon starts in this level band.", "lvl": "levels {lo}-{hi}",
        "guide": "1-60 leveling guide (zones, professions)", "calc_all": "Talent calculator",
    },
}


def points_at(level):
    return max(0, level - FIRST_LEVEL + 1)


def share_hash(payload, ranks):
    """The calculator's share link (same encoding as wow-talents.js): #b=<rev>.<ranks of tree 1>.<tree 2>.<tree 3>, talents in (row, column) order."""
    return "#b=" + payload["rev"] + "".join("." + "".join(str(ranks.get(t["id"], 0)) for t in sorted(sp["talents"], key=lambda t: (t["row"], t["col"]))) for sp in payload["specs"])


def talent_order(payload, build, values):
    """Legal order of the build's points: one talent id per point (a talent with 3 ranks appears 3 times), or None if the rules block the build.
    payload: wow_talents.payload (specs -> talents with id, row, col, gates, requires, requires_any); build: {talent id: points}; values: {talent id: value per point} (may be empty)."""
    tal = {}
    for si, sp in enumerate(payload["specs"]):
        for t in sp["talents"]:
            tal[t["id"]] = (si, t)
    rank, seq = {}, []

    def tree_points(si, through=None):
        return sum(r for tid, r in rank.items() if tal[tid][0] == si and (through is None or tal[tid][1]["row"] <= through))

    def allowed(tid):
        si, t = tal[tid]
        if rank.get(tid, 0) >= build[tid]:
            return False
        gates = t.get("gates")
        if gates:
            if any(tree_points(si, g["through_row"]) < g["points"] for g in gates):
                return False
        elif tree_points(si, t["row"] - 1) < 5 * (t["row"] - 1):
            return False
        req = t.get("requires") or []
        for q in ([req] if isinstance(req, dict) else req):
            if rank.get(q["id"], 0) < q["rank"]:
                return False
        any_of = t.get("requires_any")
        if any_of and not any(rank.get(q["id"], 0) >= q["rank"] for q in ([any_of] if isinstance(any_of, dict) else any_of)):
            return False
        return True

    total = sum(build.values())
    while len(seq) < total:
        avail = [tid for tid in build if tid in tal and allowed(tid)]
        if not avail:
            return None
        tid = min(avail, key=lambda i: (-values.get(i, 0.0), tal[i][1]["row"], tal[i][1]["col"], i))
        rank[tid] = rank.get(tid, 0) + 1
        seq.append(tid)
    return seq


def steps(lang, payload, build, values):
    """[{level, hi, points, added: [(name, n)], hash}] for levels 10, 20 ... 60, or None when the rules block the build."""
    seq = talent_order(payload, build, values)
    if not seq:
        return None
    names = {t["id"]: t["name"] for sp in payload["specs"] for t in sp["talents"]}
    out, prev, ranks = [], 0, {}
    for lv in STEPS:
        n = min(points_at(lv), len(seq))
        added = {}
        for tid in seq[prev:n]:
            added[tid] = added.get(tid, 0) + 1
            ranks[tid] = ranks.get(tid, 0) + 1
        out.append({"level": lv, "hi": (lv + 9 if lv < 60 else 60), "points": n, "added": [(names[t], c) for t, c in added.items()], "hash": share_hash(payload, ranks)})
        prev = n
    return out


def dungeon_bands(dungeons, lang, level_of, abbr_of, best_of):
    """{band first level: [{name, abbr, range, path, best: {id, name} | None}]} for the dungeons that start in each band.
    dungeons: wow_dungeons['dungeons']; level_of(d) -> 'lo-hi' text; abbr_of(id); best_of(d, min_level) -> item dict or None."""
    out = {lo: [] for lo in BANDS}
    for d in dungeons:
        rng = level_of(d)
        if not rng:
            continue
        lo = int(str(rng).split("-")[0])
        band = next((b for b, (a, z) in BANDS.items() if a <= lo < z), None)
        if band is None:
            continue
        item = best_of(d, max(lo, BANDS[band][0]))
        out[band].append({"name": d["name"][lang], "abbr": abbr_of(d["id"]), "range": rng, "lo": lo, "path": f"wow-forever/dungeons/{d['id']}/",
                          "best": {"id": item["id"], "name": item["name"]} if item else None})
    for lst in out.values():
        lst.sort(key=lambda x: (x["lo"], x["name"]))
    return out
