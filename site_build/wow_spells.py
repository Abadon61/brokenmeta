"""Loader for the WoW: Forever spell glossary (data/wow_spells/<class>.json).

The glossary itself is documented in data/wow_spells/README.md. This module just reads the JSON
files and exposes the FR/EN page text for the glossary hub + per-class pages built from it.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "wow_spells"


def load_class(class_id):
    """Returns the parsed data/wow_spells/<class_id>.json, or None if it doesn't exist yet."""
    path = DATA_DIR / f"{class_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_all():
    """Returns {class_id: parsed_json} for every class glossary file that exists."""
    out = {}
    for path in sorted(DATA_DIR.glob("*.json")):
        out[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return out


TXT = {
    "fr": {
        "kicker": "World of Warcraft: Forever · Glossaire",
        "hub_title": "Glossaire des sorts WoW: Forever",
        "hub_desc": "Coûts, temps de recharge et formules de dégâts réels de chaque sort, sourcés directement depuis les infobulles Wowhead de WoW: Forever.",
        "hub_h1": "Glossaire des sorts",
        "hub_intro": "Une capacité par ligne, avec sa vraie valeur et un lien vers son infobulle Wowhead — la base de données qui alimente nos outils de theorycraft. Chaque classe ne couvre pour l'instant que les sorts d'une rotation mono-cible soutenue au niveau 20 (le plafond actuel de la bêta), pas l'intégralité du grimoire.",
        "class_link": "Voir le glossaire {name}",
        "class_title": "Glossaire des sorts {name} WoW: Forever",
        "class_desc": "Coûts, dégâts et temps de recharge réels des sorts {name} dans WoW: Forever, sourcés depuis Wowhead.",
        "class_h1": "Glossaire des sorts : {name}",
        "class_intro": "Les sorts et talents d'une rotation {name} mono-cible soutenue au niveau 20, avec leurs vraies valeurs sourcées depuis les infobulles Wowhead de WoW: Forever.",
        "abilities_h2": "Sorts",
        "talents_h2": "Talents",
        "col_name": "Sort", "col_level": "Niveau requis", "col_cost": "Coût", "col_cooldown": "Recharge",
        "col_cast": "Lancer", "col_effect": "Effet", "col_source": "Source",
        "col_tree": "Arbre", "col_maxrank": "Rang max", "talent_effect": "Effet", "talent_dps": "Pertinent DPS ?",
        "dps_yes": "Oui", "dps_no": "Non", "dps_unknown": "Non vérifié",
        "gaps_h2": "Ce qui manque encore", "gaps_intro": "Cette classe n'est pas encore complète : voici précisément ce qui n'a pas encore été sourcé, plutôt que de le passer sous silence.",
        "no_cooldown": "Aucune", "no_cost": "Aucun", "instant": "Instantané",
        "source_wowhead": "Infobulle Wowhead",
        "back_to_hub": "Retour au glossaire",
        "seealso_optimizer": "Voir aussi : le simulateur de DPS et l'Item builder utilisent ces mêmes données.",
        "talents_no_tooltip_note": "Les noms de talents ci-dessus ne sont pas encore cliquables : leurs identifiants internes (extraits des données client de la bêta) ne correspondent pas à un vrai identifiant de sort Wowhead vérifié, donc aucune infobulle n'est affichée plutôt que de pointer vers une mauvaise page.",
    },
    "en": {
        "kicker": "World of Warcraft: Forever · Glossary",
        "hub_title": "WoW: Forever spell glossary",
        "hub_desc": "Every ability's real cost, cooldown and damage formula, sourced directly from WoW: Forever's own Wowhead tooltips.",
        "hub_h1": "Spell glossary",
        "hub_intro": "One ability per row, with its real value and a link to its own Wowhead tooltip — the database that powers our theorycraft tools. Each class currently only covers a sustained single-target rotation's spells at level 20 (the beta's current cap), not the full spellbook.",
        "class_link": "View the {name} glossary",
        "class_title": "WoW: Forever {name} spell glossary",
        "class_desc": "Real {name} spell costs, damage and cooldowns in WoW: Forever, sourced from Wowhead.",
        "class_h1": "Spell glossary: {name}",
        "class_intro": "The spells and talents of a sustained single-target {name} rotation at level 20, with their real values sourced from WoW: Forever's own Wowhead tooltips.",
        "abilities_h2": "Abilities",
        "talents_h2": "Talents",
        "col_name": "Ability", "col_level": "Required level", "col_cost": "Cost", "col_cooldown": "Cooldown",
        "col_cast": "Cast", "col_effect": "Effect", "col_source": "Source",
        "col_tree": "Tree", "col_maxrank": "Max rank", "talent_effect": "Effect", "talent_dps": "DPS relevant?",
        "dps_yes": "Yes", "dps_no": "No", "dps_unknown": "Not checked",
        "gaps_h2": "What's still missing", "gaps_intro": "This class isn't complete yet: here's precisely what hasn't been sourced yet, rather than leaving it silent.",
        "no_cooldown": "None", "no_cost": "None", "instant": "Instant",
        "source_wowhead": "Wowhead tooltip",
        "back_to_hub": "Back to glossary",
        "seealso_optimizer": "See also: the DPS simulator and the Item builder use this same data.",
        "talents_no_tooltip_note": "Talent names above aren't clickable yet: their internal IDs (pulled from the beta's own client data) don't match a verified real Wowhead spell ID, so no tooltip is shown rather than risk linking to the wrong page.",
    },
}


def ability_view(ability):
    """An ability dict enriched with display-ready cost_text and effects_text for the templates."""
    return {
        **ability,
        "cost_text": format_cost(ability.get("resource_cost")),
        "effects_text": [format_effect(e) for e in ability.get("effects", [])],
    }


def talents_view(talents_by_tree):
    """Flattens {tree: [talent, ...]} into one list, each tagged with its tree id, sorted by tree/row/col."""
    out = []
    for tree, lst in talents_by_tree.items():
        for t in lst:
            out.append({**t, "tree": tree})
    out.sort(key=lambda t: (t["tree"], t.get("row", 0), t.get("col", 0)))
    return out


def format_cost(resource_cost):
    """Turns a resource_cost dict like {"rage": 30} or {"health_pct": 20} into display text."""
    if not resource_cost:
        return None
    parts = []
    for key, val in resource_cost.items():
        if key == "health_pct":
            parts.append(f"{val}% HP")
        elif key == "mana_pct_of_base":
            parts.append(f"{val}% Mana")
        else:
            label = key.replace("_", " ").title()
            parts.append(f"{val} {label}")
    return ", ".join(parts)


def _generic_effect_fields(effect):
    """Best-effort readable text for whatever numeric/flag fields an effect carries, used as a
    fallback when no dedicated formatting exists for its kind (e.g. self_buff/party_buff, whose
    fields vary ability to ability -- a flat "buff" label would hide the real sourced values)."""
    parts = []
    for key, val in effect.items():
        if key in ("kind", "notes"):
            continue
        if key.endswith("_pct") and isinstance(val, (int, float)):
            label = key[: -len("_pct")].replace("_", " ")
            parts.append(f"{'+' if val >= 0 else ''}{val * 100:.0f}% {label}")
        elif key == "duration_sec":
            parts.append(f"{val}s")
        elif key == "radius_yd":
            parts.append(f"{val}yd radius")
        elif key == "attack_power":
            parts.append(f"+{val} AP")
        elif isinstance(val, bool):
            if val:
                parts.append(key.replace("_", " "))
        else:
            parts.append(f"{val} {key.replace('_', ' ')}")
    return ", ".join(parts)


def format_effect(effect):
    """Plain-text summary of one effects[] entry, for display in the glossary table."""
    kind = effect.get("kind")
    if kind == "direct_damage":
        if "dmg_range" in effect:
            base = f"{effect['dmg_range'][0]}-{effect['dmg_range'][1]}"
        elif effect.get("flat") is not None:
            base = str(effect["flat"])
        else:
            base = None
        extra = []
        if effect.get("ap_coeff"):
            extra.append(f"+{effect['ap_coeff']*100:.0f}% AP")
        if effect.get("sp_coeff"):
            extra.append(f"+{effect['sp_coeff']*100:.0f}% SP")
        if base is not None:
            return base + (" (" + ", ".join(extra) + ")" if extra else "")
        return ", ".join(extra) if extra else "?"
    if kind == "periodic_damage":
        return f"{effect.get('total_damage', '?')} / {effect.get('duration_sec', '?')}s ({effect.get('damage_per_tick', '?')}/tick)"
    if kind == "normalized_weapon_damage":
        pct = effect.get("pct", 1.0)
        flat = effect.get("flat")
        base = f"{pct*100:.0f}% weapon dmg" if pct != 1.0 else "100% weapon dmg"
        return base + (f" +{flat}" if flat else "")
    if kind == "flat_bonus_on_next_swing":
        return f"+{effect.get('flat', '?')} on next swing"
    if kind in ("self_buff", "party_buff"):
        return effect.get("notes") or _generic_effect_fields(effect) or "buff"
    if kind == "target_debuff_stacking":
        stat = effect.get("stat", "").replace("_", " ")
        stacks = f" ×{effect['max_stacks']}" if effect.get("max_stacks", 1) > 1 else ""
        return f"-{effect.get('per_stack', '?')} {stat}{stacks}"
    if kind == "resource_generation":
        resource = effect.get("resource", "").replace("_", " ").capitalize()
        parts = []
        if effect.get("immediate"):
            parts.append(f"+{effect['immediate']} {resource} instantly")
        if effect.get("over_time"):
            parts.append(f"{effect['over_time']} {resource} over {effect.get('over_time_duration_sec', '?')}s")
        return " + ".join(parts) if parts else "?"
    if kind == "combo_point_scaling":
        return "scales with combo points (see table)"
    if kind == "proc_trigger":
        return effect.get("description") or "conditional effect"
    return kind or "?"
