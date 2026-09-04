"""Single-match analysis: compare one real, live-fetched game against the
meta benchmarks already computed in tierlist.json for that comp archetype.

This is the engine behind the standalone match-analysis tool (analyze_app.py)
-- deliberately NOT part of the static CoreMeta Outrun artifact, since it
needs a live Riot API call triggered by user input at view time, which a
published Artifact's CSP can't do (see project notes). Runs as a small local
Flask app instead, reusing the same RiotClient/comp_signature/tierlist
machinery as everything else in this project.
"""
from __future__ import annotations

import json
from pathlib import Path

from .comp_signature import clean_id, derive_comp, display_name, is_complete_item

GOLD_DIFF_THRESHOLD = 10  # gold left, above/below benchmark, worth flagging
LEVEL_DIFF_THRESHOLD = 1.0
ROUND_DIFF_THRESHOLD = 3
PLACEMENT_UNDERPERFORM_THRESHOLD = 1.0  # placement worse than comp avg, by this much, before blaming the lobby
COUNTER_RATE_THRESHOLD = 0.55  # opponent comp's historical ahead-rate vs the player's comp, to call it a "counter"
COUNTER_MIN_ENCOUNTERS = 4


def load_benchmarks(tierlist_path: str = "data/output/tierlist.json") -> dict[str, dict]:
    """Real per-comp averages (placement, top4 rate, gold left, level, last
    round) already computed from the full sample -- what a live-fetched game
    gets compared against. Keyed by the same comp `key` derive_comp() uses
    everywhere else, so lookups line up automatically."""
    data = json.loads(Path(tierlist_path).read_text(encoding="utf-8"))
    return {c["key"]: c for c in data["comps"] if c["has_enough_data"]}


def load_matchups(matchups_path: str = "data/output/matchups.json") -> dict[tuple[str, str], dict]:
    """Directional lookup: matchups[(compA, compB)] -> how often compA placed
    ahead of compB within shared lobbies, across the full sample. Same proxy
    signal used everywhere else in this project (Riot's API has no
    round-by-round combat data, so this is the closest real substitute --
    see matchup_proxy.py)."""
    data = json.loads(Path(matchups_path).read_text(encoding="utf-8"))
    lookup: dict[tuple[str, str], dict] = {}
    for m in data["matchups"]:
        a, b = m["comp_a"], m["comp_b"]
        lookup[(a, b)] = {"aheadRate": m["a_ahead_rate"], "encounters": m["encounters"]}
        lookup[(b, a)] = {"aheadRate": m["b_ahead_rate"], "encounters": m["encounters"]}
    return lookup


def _extract_units(participant: dict, name_map: dict[str, str] | None) -> list[dict]:
    units = []
    for u in participant.get("units") or []:
        champ = display_name(clean_id(u.get("character_id", "")), name_map)
        if not champ:
            continue
        items = [clean_id(i) for i in (u.get("itemNames") or [])]
        units.append({
            "champion": champ,
            "cost": (u.get("rarity") or 0) + 1,
            "star": u.get("tier", 1),
            "items": [i for i in items if is_complete_item(i)],
        })
    units.sort(key=lambda u: u["cost"])
    return units


def _analyze_items(units: list[dict], bench: dict | None, expected_carry: str | None) -> list[dict]:
    """Real check, not a guess: is the build on the champion this comp
    actually relies on? Uses core_units()'s per-champion item history (does
    THIS champion typically hold items at all, in THIS comp) and
    item_combo_stats (has this exact 3-item build shown up before, and how
    did it go) -- both already computed from the full sample, nothing
    invented here."""
    if not bench:
        return []
    insights = []
    core_by_champ = {u["champion"]: u for u in bench.get("core_units", [])}
    expected_item_holders = {
        champ for champ, u in core_by_champ.items()
        if any(is_complete_item(i) for i in u.get("items", []))
    }
    actual_by_champ = {u["champion"]: u for u in units}

    if expected_carry:
        carry_unit = actual_by_champ.get(expected_carry)
        carry_items = carry_unit["items"] if carry_unit else []
        if not carry_items:
            insights.append({"type": "warning", "category": "Objets",
                "text": f"Ton carry principal ({expected_carry}) n'a reçu aucun objet complet cette partie — un carry non stuff perd l'essentiel de son impact."})
        elif len(carry_items) < 3:
            insights.append({"type": "warning", "category": "Objets",
                "text": f"Ton carry principal ({expected_carry}) n'a que {len(carry_items)} objet(s) complet(s) — en dessous d'un build complet à 3 objets."})
        else:
            insights.append({"type": "good", "category": "Objets",
                "text": f"Ton carry principal ({expected_carry}) est bien stuff ({len(carry_items)} objets complets)."})
            combos = bench.get("item_combo_stats", [])
            carry_combos = [c for c in combos if c["champion"] == expected_carry]
            actual_set = set(carry_items[:3])
            match = next((c for c in carry_combos if set(c["items"]) == actual_set), None)
            if match:
                insights.append({"type": "good", "category": "Objets",
                    "text": f"Cette combinaison précise sur {expected_carry} fait partie des builds déjà observés sur cette comp (placement moyen {match['avgPlacement']:.2f} sur {match['games']} parties)."})
            elif carry_combos:
                insights.append({"type": "info", "category": "Objets",
                    "text": f"La combinaison construite sur {expected_carry} diffère des builds les plus fréquents observés pour cette comp — pas forcément une erreur, mais à comparer aux combinaisons connues sur sa fiche."})

    for champ, u in actual_by_champ.items():
        if champ == expected_carry or not u["items"]:
            continue
        if champ not in expected_item_holders:
            insights.append({"type": "info", "category": "Objets",
                "text": f"{len(u['items'])} objet(s) complet(s) sur {champ}, qui n'est généralement pas un porteur d'objets dans cette comp — vérifie que c'était voulu (flex, adaptation à la partie) plutôt qu'un objet gâché."})
        else:
            insights.append({"type": "good", "category": "Objets",
                "text": f"{len(u['items'])} objet(s) complet(s) sur {champ} — c'est bien un porteur d'objets habituel de cette comp."})

    return insights


def build_lobby(match: dict, puuid: str, name_map: dict[str, str] | None,
                 matchup_lookup: dict[tuple[str, str], dict], player_key: str,
                 item_offense: dict[str, str] | None = None) -> list[dict]:
    """The other 7 players in this exact lobby, their comp (Riot ID and
    comp are both right there on the raw participant object, no extra API
    calls needed), and -- when the sample has enough shared-lobby
    encounters -- how often THAT comp has historically placed ahead of the
    player's comp. This is the same co-occurrence proxy the rest of the app
    uses for match-ups, just applied to one real, specific lobby instead of
    the aggregate."""
    lobby = []
    for p in match.get("info", {}).get("participants", []):
        if p.get("puuid") == puuid or not p.get("placement"):
            continue
        sig = derive_comp(p, name_map=name_map, item_offense=item_offense)
        game_name = p.get("riotIdGameName") or "?"
        tag_line = p.get("riotIdTagline") or ""
        m = matchup_lookup.get((sig.key, player_key))
        lobby.append({
            "riotId": f"{game_name}#{tag_line}" if tag_line else game_name,
            "compLabel": sig.label,
            "compKey": sig.key,
            "carry": sig.carry,
            "placement": p.get("placement"),
            "counterRate": m["aheadRate"] if m else None,
            "encounters": m["encounters"] if m else 0,
        })
    lobby.sort(key=lambda x: x["placement"])
    return lobby


def _analyze_lobby_insight(lobby: list[dict], bench: dict | None, placement: int | None) -> list[dict]:
    strong_counters = [
        l for l in lobby
        if l["counterRate"] is not None and l["counterRate"] >= COUNTER_RATE_THRESHOLD
        and l["encounters"] >= COUNTER_MIN_ENCOUNTERS
    ]
    if not strong_counters:
        return []
    names = ", ".join(f"{l['compLabel']} ({round(l['counterRate']*100)}% des rencontres)" for l in strong_counters[:3])
    underperformed = bool(bench and placement and placement - bench["avg_placement"] >= PLACEMENT_UNDERPERFORM_THRESHOLD)
    if underperformed:
        return [{"type": "warning", "category": "Adversaires",
            "text": f"Ton lobby comptait {len(strong_counters)} compo(s) qui prennent historiquement l'avantage sur la tienne dans les lobbies partagés : {names} — un facteur possible dans ce placement en dessous de la moyenne de ta comp."}]
    return [{"type": "info", "category": "Adversaires",
        "text": f"Présentes dans ton lobby malgré tout : {names}, qui contrent historiquement ta comp dans les lobbies partagés."}]


def build_report(participant: dict, name_map: dict[str, str] | None, benchmarks: dict[str, dict],
                  match: dict | None = None, puuid: str | None = None,
                  matchup_lookup: dict[tuple[str, str], dict] | None = None,
                  item_offense: dict[str, str] | None = None) -> dict:
    sig = derive_comp(participant, name_map=name_map, item_offense=item_offense)
    bench = benchmarks.get(sig.key)

    placement = participant.get("placement")
    level = participant.get("level")
    gold_left = participant.get("gold_left")
    last_round = participant.get("last_round")

    insights = []

    if bench:
        if gold_left is not None:
            diff = gold_left - bench["avg_gold_left"]
            if diff >= GOLD_DIFF_THRESHOLD:
                insights.append({"type": "warning", "category": "Économie",
                    "text": f"{gold_left} or non dépensé en fin de partie, contre {bench['avg_gold_left']:.1f} en moyenne sur cette comp — cet or aurait pu financer des niveaux ou des rerolls supplémentaires."})
            elif diff <= -GOLD_DIFF_THRESHOLD:
                insights.append({"type": "info", "category": "Économie",
                    "text": f"Seulement {gold_left} or restant, nettement moins que la moyenne ({bench['avg_gold_left']:.1f}) — dépense agressive, cohérent si ça a soutenu le placement."})
            else:
                insights.append({"type": "good", "category": "Économie",
                    "text": f"Gestion de l'or dans la moyenne de cette comp ({gold_left} vs {bench['avg_gold_left']:.1f})."})

        if level is not None:
            ldiff = level - bench["avg_level"]
            if ldiff <= -LEVEL_DIFF_THRESHOLD:
                insights.append({"type": "warning", "category": "Niveau",
                    "text": f"Niveau {level} en fin de partie, en retard sur la moyenne ({bench['avg_level']:.1f}) pour cette comp — un retard de niveau limite souvent la taille du board en fin de partie."})
            elif ldiff >= LEVEL_DIFF_THRESHOLD:
                insights.append({"type": "good", "category": "Niveau",
                    "text": f"Niveau {level} en fin de partie, au-dessus de la moyenne ({bench['avg_level']:.1f}) — bonne courbe de leveling."})
            else:
                insights.append({"type": "good", "category": "Niveau",
                    "text": f"Niveau dans la moyenne de cette comp ({level} vs {bench['avg_level']:.1f})."})

        if last_round is not None:
            rdiff = last_round - bench["avg_last_round"]
            if rdiff <= -ROUND_DIFF_THRESHOLD:
                insights.append({"type": "warning", "category": "Survie",
                    "text": f"Sortie au round {last_round}, contre {bench['avg_last_round']:.1f} en moyenne sur cette comp — une élimination plus précoce qu'attendu."})

        insights.append({"type": "good" if placement and placement <= 4 else "warning", "category": "Résultat",
            "text": f"Placement {placement} — la moyenne pour cette comp est {bench['avg_placement']:.2f} (top 4 dans {round(bench['top4_rate']*100)}% des cas)."})
    else:
        insights.append({"type": "info", "category": "Échantillon",
            "text": "Pas assez de données collectées sur cette comp précise pour établir des benchmarks fiables — voici les faits bruts de la partie, sans comparaison."})

    units = _extract_units(participant, name_map)
    insights.extend(_analyze_items(units, bench, sig.carry))

    lobby = []
    if match is not None and puuid is not None and matchup_lookup is not None:
        lobby = build_lobby(match, puuid, name_map, matchup_lookup, sig.key, item_offense=item_offense)
        insights.extend(_analyze_lobby_insight(lobby, bench, placement))

    return {
        "compLabel": sig.label,
        "compKey": sig.key,
        "carry": sig.carry,
        "placement": placement,
        "level": level,
        "goldLeft": gold_left,
        "lastRound": last_round,
        "units": units,
        "benchmark": bench,
        "insights": insights,
        "lobby": lobby,
    }
