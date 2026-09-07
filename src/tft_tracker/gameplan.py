"""Reroll/leveling gameplan generator -- Python port of gameplan.js (the
user's own validated reference implementation, JS). Ported line-for-line,
not reinvented: same LEVEL_ODDS/BAG_SIZE/UNIQUE_CHAMPS/XP_STEP tables, same
simulation-based best-level search (a shortcut without simulation gave a
wrong answer on the Eclipse Kayle case per the original's own comment), same
percentile-based gold estimate. See gameplan.js at the project root for the
original this was ported from -- keep the two in sync if the reference ever
changes.

Runs a real Monte Carlo simulation (up to ~1500 trials x 150 reroll-rounds
x 5 shop slots for the biggest calls) -- multiple hundreds of ms per comp.
NEVER call this per-request; it is meant to be invoked once per comp at
site-build time and its output (a list of {"title","description"} steps)
baked into the static page. See build_site.py's gameplan precompute step.
"""
from __future__ import annotations

import random

LEVEL_ODDS = {
    1: [100, 0, 0, 0, 0], 2: [100, 0, 0, 0, 0], 3: [75, 25, 0, 0, 0],
    4: [55, 30, 15, 0, 0], 5: [45, 33, 20, 2, 0], 6: [30, 40, 25, 5, 0],
    7: [16, 30, 43, 10, 1], 8: [15, 20, 32, 30, 3], 9: [10, 17, 25, 33, 15],
    10: [5, 10, 20, 40, 25], 11: [1, 2, 12, 50, 35],
}
BAG_SIZE = {1: 30, 2: 25, 3: 18, 4: 10, 5: 9}
UNIQUE_CHAMPS = {1: 14, 2: 13, 3: 14, 4: 14, 5: 10}
TOTAL_IN_POOL = {c: BAG_SIZE[c] * UNIQUE_CHAMPS[c] for c in BAG_SIZE}
XP_STEP = {1: 2, 2: 2, 3: 6, 4: 10, 5: 20, 6: 36, 7: 60, 8: 68, 9: 68, 10: 84}


def level_up_cost(a: int, b: int) -> int:
    if b <= a:
        return 0
    return sum(XP_STEP.get(lvl, 0) for lvl in range(a, b))


def star_to_copies(star: int) -> int:
    return 1 if star == 1 else 3 if star == 2 else 9


def _sample_cost(level: int) -> int:
    odds = LEVEL_ODDS[level]
    r = random.random() * 100
    cum = 0.0
    for i in range(5):
        cum += odds[i]
        if r < cum:
            return i + 1
    return 5


def estimate_gold_for_target(group: list[dict], level: int, trials: int = 1500, max_rerolls: int = 150) -> dict:
    """{"p25", "median", "p75"} reroll gold needed to complete `group` at
    `level` -- percentiles over `trials` simulated single-player (no
    contestation) climbs to the target copy counts."""
    if not group:
        return {"p25": 0, "median": 0, "p75": 0}
    needed = {t["id"]: star_to_copies(t["star"]) for t in group}
    rerolls_to_complete = []
    for _ in range(trials):
        owned = {t["id"]: 0 for t in group}
        r = 0
        while r < max_rerolls:
            done = all(owned[t["id"]] >= needed[t["id"]] for t in group)
            if done:
                break
            for _s in range(5):
                cost = _sample_cost(level)
                cand = [t for t in group if t["cost"] == cost and owned[t["id"]] < needed[t["id"]]]
                if not cand:
                    continue
                sub = sum(owned[t["id"]] for t in group if t["cost"] == cost)
                tot = TOTAL_IN_POOL[cost] - sub
                if tot <= 0:
                    continue
                roll = random.random() * tot
                picked = None
                for c in cand:
                    rem = BAG_SIZE[c["cost"]] - owned[c["id"]]
                    if roll < rem:
                        picked = c
                        break
                    roll -= rem
                if picked is not None:
                    owned[picked["id"]] += 1
            r += 1
        rerolls_to_complete.append(r)
    rerolls_to_complete.sort()

    def pct(p: float) -> int:
        idx = int(p * (trials - 1))
        return rerolls_to_complete[idx] * 2

    return {"p25": pct(0.25), "median": pct(0.5), "p75": pct(0.75)}


def best_level_for_group(group: list[dict], level_candidates: list[int], trials: int = 400) -> int:
    """The level minimizing median reroll gold for `group` -- found by
    simulating every candidate level, not a closed-form shortcut (see
    module docstring: a shortcut gave a wrong answer on a real case)."""
    best_level = level_candidates[0]
    best_median = float("inf")
    for level in level_candidates:
        result = estimate_gold_for_target(group, level, trials)
        if result["median"] < best_median:
            best_level, best_median = level, result["median"]
    return best_level


def generate_gameplan(targets: list[dict]) -> list[dict]:
    """targets: [{"id", "name", "cost", "star"}, ...] (star: 1, 2, or 3).
    Returns [{"tab", "title", "description"}, ...] -- "tab" is a short,
    stable KEY (not part of the original JS reference's output; not a
    display string itself), one of "reroll"/"level_up"/"complete_board"/
    "end_game", added purely to drive a tabbed UI since "title" here is a
    full sentence, not tab-length. It's assigned by construction (which
    branch produced the step), never parsed back out of the text, so it
    can't drift from what the step actually is. build_site.py maps this key
    to a real per-language label (French "title"/"description" text stays
    French either way -- see gameplan_fr_only)."""
    priority = [t for t in targets if t["star"] >= 2]  # needs a real dedicated reroll (3 or 9 copies)
    flex = [t for t in targets if t["star"] == 1]       # picked up along the way

    steps: list[dict] = []

    if priority:
        reroll_level = best_level_for_group(priority, [3, 4, 5, 6, 7, 8, 9])
        gold = estimate_gold_for_target(priority, reroll_level)
        costs_str = "/".join(str(c) for c in sorted({t["cost"] for t in priority}))
        names_str = ", ".join(t.get("name") or t["id"] for t in priority)
        steps.append({
            "tab": "reroll",
            "title": f"Se poser au niveau {reroll_level} pour rerolls {names_str}",
            "description": (
                f"Niveau qui minimise l'or nécessaire pour {costs_str}-coût(s) en même temps. "
                f"Compter environ {gold['p25']}-{gold['p75']} or pour une chance de 25% à 75% "
                f"d'obtenir toutes les copies visées (médiane ~{gold['median']} or)."
            ),
        })

        if flex:
            candidates = [lvl for lvl in [reroll_level, reroll_level + 1, reroll_level + 2, 7, 8, 9, 10, 11]
                          if lvl >= reroll_level]
            final_level = best_level_for_group(flex, candidates)
        else:
            final_level = reroll_level

        if final_level > reroll_level and flex:
            lvl_cost = level_up_cost(reroll_level, final_level)
            steps.append({
                "tab": "level_up",
                "title": f"Une fois les carries obtenus, monter au niveau {final_level} ({lvl_cost} or)",
                "description": (
                    f"Passage direct sans s'arrêter aux niveaux intermédiaires : ils n'apportent rien "
                    f"de plus une fois qu'on a fini de rerolls les coûts {costs_str}."
                ),
            })

        if flex:
            gold_flex = estimate_gold_for_target(flex, final_level)
            flex_names = ", ".join(t.get("name") or t["id"] for t in flex)
            steps.append({
                "tab": "complete_board",
                "title": f"Compléter {flex_names} (1★ chacun)",
                "description": f"Peu de regards nécessaires : médiane ~{gold_flex['median']} or pour tout obtenir à ce niveau.",
            })
    elif flex:
        level = best_level_for_group(flex, [4, 5, 6, 7, 8, 9])
        gold = estimate_gold_for_target(flex, level)
        steps.append({
            "tab": "reroll",
            "title": f"Niveau {level}, quelques rerolls suffisent",
            "description": f"Aucun carry à 2-3★ dans cette compo : médiane ~{gold['median']} or pour compléter le board.",
        })

    steps.append({
        "tab": "end_game",
        "title": "Garder le reste de l'or pour les objets et la vie",
        "description": "Une fois la compo posée, prioriser la sécurité du board plutôt que le sur-reroll.",
    })

    return steps
