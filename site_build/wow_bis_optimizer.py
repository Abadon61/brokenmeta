"""Engine-driven Best-in-Slot optimizer for WoW: Forever at level 20 (2026-09-26, user request:
"notre propre optimiseur BIS ... en utilisant le moteur lui-meme" -- point 4 of the original
DPS-sim improvement list, building our own gear picks with wow_dps_sim.py's own engine instead of
trusting foreverchanges.pro's external item choices wholesale).

Candidate pool: data/wow_dungeons/dungeons.json ONLY. data/wow_raids/raids.json was checked and
every single item in it requires level 60 (`req: 60`), i.e. none of it is legally equippable by a
level-20 character in this beta -- raid loot is simply out of scope right now, not omitted by
oversight. Dungeon items are filtered to `req <= 20` for the same reason (the file spans up to
`req: 58`, well past our own level cap).

Two real, disclosed limitations this optimizer inherits rather than papers over:

1. Base (no-gear) character stats: there is no independently-sourced level-20 base-stat table
   (Strength/Agility/etc. with zero items) for this project to build from. foreverchanges.pro's
   own aggregate (data/wow_items/bis_level20_stats.json) bundles a real level-20 base into its
   totals, but doesn't expose it separately, so it can't be cleanly subtracted back out and
   reused here. The one time this project used an AI-supplied stat table (a Gemini conversation),
   it was narrowly scoped to a single Shaman/Orc exception (see that file's own sourcing note),
   not a general race/class table. Per explicit user decision (2026-09-26), this optimizer uses
   the already-disclosed LEVEL 1 base (OP_RACE_BASE_STATS/OP_CLASS_BONUS_STATS in build_site.py,
   sourced from rankedboost.com/world-of-warcraft/classic-stats/) plus real gear on top. This
   means the final DPS number is a genuine under-count relative to a true level-20 character (it
   is missing 19 levels' worth of raw stat growth), which is disclosed on the guide page itself
   rather than silently produced as if it were the more complete number.
2. Per-slot fallback: Head, Neck and Trinket have ZERO real dungeon-drop candidates at req<=20 in
   this dataset (checked directly, not assumed -- these slots are apparently only itemized via
   quest rewards/vendors in this level range, which isn't data this project has). For any slot
   with no real candidate, this optimizer falls back to foreverchanges.pro's own existing pick
   for that exact slot (data/wow_items/bis_gear_by_slot.json) rather than leaving it empty, and
   the per-item source is disclosed on the guide page (dungeon boss name, or "ForeverChanges.pro").

Armor and weapon proficiency (which real armor/weapon TYPES a class can equip at level 20, before
the level-40 Mail/Plate unlock) are sourced from
https://vanilla-wow-archive.fandom.com/wiki/Class_proficiencies (checked 2026-09-26; corroborated
independently by a second search on Warrior/Paladin Mail-before-40 and Hunter/Shaman
Leather-before-40). This is Classic-era data assumed, not independently confirmed, to still hold
in WoW: Forever -- the same disclosed-approximation pattern already used for Hunter pet DPS
(PET_AP_RATIO_OF_HUNTER_RANGED_AP in wow_dps_sim.py).

Weapon SLOT STRUCTURE per spec (how many weapon slots, 1H/2H/ranged/caster) is NOT re-derived here
-- it mirrors exactly what wow_dps_sim.ROTATIONS already encodes and discloses per spec (e.g.
Protection Warrior/Paladin's own comments state "single one-handed weapon + shield, no
off-hand"). This optimizer only chooses which REAL item fills each of those already-established
slots; it does not decide whether a spec dual-wields, uses a shield, or goes two-handed.
"""
import json

import wow_dps_sim
import wow_spells

ROOT = wow_spells.ROOT
LEVEL_CAP = 20

# ---- proficiency tables, sourced from vanilla-wow-archive.fandom.com/wiki/Class_proficiencies
# (see module docstring). Armor types match this project's own item data's `type.en` strings
# exactly (checked directly: dungeons.json uses "Plate Mail" for plate, "Mail" for mail).
ARMOR_PROFICIENCY = {
    "warrior": {"Cloth", "Leather", "Mail"},   # Plate at level 40, not yet
    "paladin": {"Cloth", "Leather", "Mail"},   # Plate at level 40, not yet
    "hunter": {"Cloth", "Leather"},            # Mail at level 40, not yet
    "shaman": {"Cloth", "Leather"},            # Mail at level 40, not yet
    "rogue": {"Cloth", "Leather"},
    "druid": {"Cloth", "Leather"},
    "mage": {"Cloth"},
    "priest": {"Cloth"},
    "warlock": {"Cloth"},
}
SHIELD_CLASSES = {"warrior", "paladin", "shaman"}

WEAPON_PROFICIENCY = {
    "warrior": {"Axes", "Two-Handed Axes", "Swords", "Two-Handed Swords", "Maces", "Two-Handed Maces",
                "Polearms", "Staves", "Daggers", "Fist Weapons", "Bows", "Crossbows", "Guns", "Thrown"},
    "paladin": {"Axes", "Two-Handed Axes", "Swords", "Two-Handed Swords", "Maces", "Two-Handed Maces", "Polearms"},
    "hunter": {"Axes", "Two-Handed Axes", "Swords", "Two-Handed Swords", "Polearms", "Staves",
               "Daggers", "Fist Weapons", "Bows", "Crossbows", "Guns"},  # no Maces
    "rogue": {"Axes", "Swords", "Maces", "Daggers", "Fist Weapons", "Bows", "Crossbows", "Guns", "Thrown"},  # one-handed only
    "shaman": {"Axes", "Two-Handed Axes", "Maces", "Two-Handed Maces", "Polearms", "Staves", "Daggers", "Fist Weapons"},  # no Swords
    "mage": {"Swords", "Daggers", "Staves", "Wands"},
    "priest": {"Maces", "Daggers", "Staves", "Wands"},  # one-handed maces only
    "warlock": {"Swords", "Daggers", "Staves", "Wands"},
    "druid": {"Maces", "Two-Handed Maces", "Polearms", "Staves", "Daggers", "Fist Weapons"},
}

# Raw inventory slot codes used by data/wow_dungeons/dungeons.json (Blizzard's own INVTYPE
# numbering, printed straight from the file's own "slots" dict).
SLOT_HEAD, SLOT_NECK, SLOT_SHOULDER, SLOT_CHEST, SLOT_WAIST = 1, 2, 3, 5, 6
SLOT_LEGS, SLOT_FEET, SLOT_WRIST, SLOT_HANDS, SLOT_FINGER, SLOT_TRINKET = 7, 8, 9, 10, 11, 12
SLOT_ONE_HAND, SLOT_SHIELD, SLOT_RANGED, SLOT_BACK, SLOT_TWO_HAND, SLOT_MAIN_HAND = 13, 14, 15, 16, 17, 21

ARMOR_SLOTS = [
    ("head", SLOT_HEAD, True), ("shoulder", SLOT_SHOULDER, True), ("chest", SLOT_CHEST, True),
    ("waist", SLOT_WAIST, True), ("legs", SLOT_LEGS, True), ("feet", SLOT_FEET, True),
    ("wrist", SLOT_WRIST, True), ("hands", SLOT_HANDS, True),
    ("neck", SLOT_NECK, False), ("back", SLOT_BACK, False),
]

# Per-spec weapon slot structure, mirroring wow_dps_sim.ROTATIONS's own already-disclosed weapon
# choices exactly (see module docstring) -- "main" is always searched; "off" is "shield" (search
# real Shield-type items), "1h" (search a second one-handed weapon of the same proficiency, dual
# wield), or None (no off-hand weapon search). "ranged" adds a Wand search for pure casters (real
# Classic casters carry a wand in the ranged slot purely for its own flat stats -- wand AUTO-
# ATTACK damage itself stays a disclosed, unmodeled gap, same as noted at the top of
# wow_dps_sim.py) or reuses "main" for Hunters (their ranged weapon IS their "weapons" sim entry).
WEAPON_STRUCTURE = {
    "warrior_fury": {"main": "1h", "off": "1h"},
    "warrior_arms": {"main": "2h", "off": None},
    "warrior_protection": {"main": "1h", "off": "shield"},
    "rogue_combat": {"main": "1h", "off": "1h"},
    "rogue_assassination": {"main": "1h", "off": "1h"},
    "rogue_subtlety": {"main": "1h", "off": "1h"},
    "paladin_retribution": {"main": "2h", "off": None},
    "paladin_protection": {"main": "1h", "off": "shield"},
    "shaman_enhancement": {"main": "1h", "off": None},  # real dual-wield not modeled by the sim (see ROTATIONS); matched here, not "fixed"
    "shaman_elemental": {"main": "caster", "off": None},  # Shaman has no Wand proficiency
    "mage_fire": {"main": "caster", "off": None, "wand": True},
    "mage_arcane": {"main": "caster", "off": None, "wand": True},
    "mage_frost": {"main": "caster", "off": None, "wand": True},
    "priest_shadow": {"main": "caster", "off": None, "wand": True},
    "druid_balance": {"main": "caster", "off": None},  # Druid has no Wand proficiency
    "druid_feral": {"main": "1h", "off": None},
    "druid_feral_tank": {"main": "1h", "off": None},
    "warlock_affliction": {"main": "caster", "off": None, "wand": True},
    "warlock_demonology": {"main": "caster", "off": None, "wand": True},
    "warlock_destruction": {"main": "caster", "off": None, "wand": True},
    "hunter_marksmanship": {"main": "ranged", "off": None},
    "hunter_beast_mastery": {"main": "ranged", "off": None},
    "hunter_survival": {"main": "ranged", "off": None},
}

STAT_KEY_ORDER = ["str", "agi", "int", "spi", "sta", "splpwr", "spldmg", "atkpwr", "manargn",
                   "critstrkrtng", "hastertng", "hitrtng", "defrtng", "armor"]

_ITEM_POOL = None


def _load_item_pool():
    """Every data/wow_dungeons/dungeons.json item with req<=20, tagged with its dropping
    dungeon/boss for display credit. Cached module-wide (read-only data, built once per run)."""
    global _ITEM_POOL
    if _ITEM_POOL is not None:
        return _ITEM_POOL
    path = ROOT / "data" / "wow_dungeons" / "dungeons.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"dungeons": []}
    pool = []
    for dg in data.get("dungeons", []):
        for it in dg.get("items", []):
            if (it.get("req") or 0) > LEVEL_CAP:
                continue
            pool.append({**it, "dungeon_name": dg["name"]})
    _ITEM_POOL = pool
    return pool


def _item_stat_contribution(spec_id, item):
    """One item's own {ap, sp, crit_pct, hit_pct} contribution, using the exact same conversion
    ratios as a full character (wow_dps_sim.stat_deltas_from_raw)."""
    st = item.get("st", {})
    flat_ap = st.get("atkpwr", 0)
    flat_sp = st.get("splpwr", 0) + st.get("spldmg", 0)
    d = wow_dps_sim.stat_deltas_from_raw(spec_id, str_=st.get("str", 0), agi=st.get("agi", 0),
                                          int_=st.get("int", 0), flat_ap=flat_ap, flat_sp=flat_sp)
    return d


def _stat_weights(spec_id, baseline_stats, iterations=80, fight_len=120.0):
    """DPS gained per +1 unit of ap/sp and per +0.05 (5 percentage points) of hit/crit, at
    baseline_stats, via numeric differentiation against the real sim -- the standard
    theorycrafting "stat weight" technique (what Pawn/SimC-style tools compute), not a shortcut
    invented for this feature. Used only to RANK candidate items per slot; the final displayed
    DPS always comes from one real full sim run on the final combined stats (see optimize_spec),
    never from summing these linear weights, so weight approximation error can't compound."""
    dps0, _ = wow_dps_sim.run_class(spec_id, iterations=iterations, fight_len=fight_len, stats=baseline_stats)
    weights = {}
    for key, delta in (("ap", 50.0), ("sp", 50.0), ("hit", 0.05), ("crit", 0.05)):
        perturbed = dict(baseline_stats)
        perturbed[key] = perturbed[key] + delta
        dps1, _ = wow_dps_sim.run_class(spec_id, iterations=iterations, fight_len=fight_len, stats=perturbed)
        weights[key] = (dps1 - dps0) / delta
    return weights, dps0


def _score(weights, contribution):
    return (contribution["ap"] * weights["ap"] + contribution["sp"] * weights["sp"]
            + contribution["hit_pct"] / 100.0 * weights["hit"] + contribution["crit_pct"] / 100.0 * weights["crit"])


def _candidates_for_armor_slot(pool, slot_code, allowed_types):
    return [it for it in pool if it["slot"] == slot_code and it.get("type", {}).get("en") in allowed_types]


def _candidates_unrestricted(pool, slot_code):
    return [it for it in pool if it["slot"] == slot_code]


def _candidates_for_weapon(pool, slot_codes, allowed_types):
    return [it for it in pool if it["slot"] in slot_codes and it.get("type", {}).get("en") in allowed_types]


def _fallback_item(fallback_by_slot, slot_key):
    it = fallback_by_slot.get(slot_key)
    if not it or not it.get("wowhead_item_id"):
        return None
    return {
        "slot": slot_key, "name": it["name"], "icon": it["icon"], "wowhead_item_id": it["wowhead_item_id"],
        "stat_text": it.get("stat") or "", "source": "foreverchanges",
    }


def _stat_text(st, stat_names):
    parts = []
    for k in STAT_KEY_ORDER:
        if st.get(k):
            parts.append(f"+{st[k]} {stat_names[k]}")
    if st.get("dps"):
        speed = f" ({st['speed']} s)" if st.get("speed") else ""
        parts.append(f"{st['dps']} DPS{speed}")
    return " · ".join(parts)


def _pick_best(pool, spec_id, weights, candidates, exclude_ids=()):
    best, best_score = None, float("-inf")
    for it in candidates:
        if it["id"] in exclude_ids:
            continue
        score = _score(weights, _item_stat_contribution(spec_id, it))
        if score > best_score:
            best, best_score = it, score
    return best


def optimize_spec(spec_id, race_base_stats, class_bonus_stats, fallback_gear, stat_names):
    """Computes this spec's own engine-driven BIS loadout. Returns (gear_list, final_stats_block,
    dps) where gear_list matches the shape wow_guide_spec.html already renders (slot/name/icon/
    wowhead_item_id/stat text), each item additionally tagged with its real source (a dungeon
    boss name, or "foreverchanges" for a slot with no real dungeon candidate -- see module
    docstring's fallback disclosure)."""
    profile = wow_dps_sim.ROTATIONS.get(spec_id)
    if not profile:
        return None
    class_id = profile.get("glossary", spec_id)
    armor_types = ARMOR_PROFICIENCY.get(class_id, set())
    weapon_types = WEAPON_PROFICIENCY.get(class_id, set())
    pool = _load_item_pool()
    fallback_by_slot = {it["slot"]: it for it in (fallback_gear or [])}

    race = wow_dps_sim._load_bis_data()["specs"].get(spec_id, {}).get("race", "").lower().replace(" ", "")
    race_key = {"nightelf": "nightelf", "human": "human", "dwarf": "dwarf", "gnome": "gnome",
                "orc": "orc", "undead": "undead", "tauren": "tauren", "troll": "troll"}.get(race, "human")
    base = dict(race_base_stats.get(race_key, {}))
    for k, v in class_bonus_stats.get(class_id, {}).items():
        base[k] = base.get(k, 0) + v
    baseline_stats = wow_dps_sim.stats_from_raw(spec_id, str_=base.get("str", 0), agi=base.get("agi", 0), int_=base.get("int", 0))
    weights, _ = _stat_weights(spec_id, baseline_stats)

    gear = []
    totals = dict(base)
    totals_flat_ap, totals_flat_sp = 0.0, 0.0

    weapon_dmg_speed = {}  # "main"/"off" -> {"dmg", "speed"}, only set for actual weapon picks

    def add_item(slot_key, it, source_label):
        nonlocal totals_flat_ap, totals_flat_sp
        st = it.get("st", {})
        for k in ("str", "agi", "int", "sta", "spi"):
            totals[k] = totals.get(k, 0) + st.get(k, 0)
        totals_flat_ap += st.get("atkpwr", 0)
        totals_flat_sp += st.get("splpwr", 0) + st.get("spldmg", 0)
        gear.append({
            "slot": slot_key, "name": it["name"], "icon": f"https://wow.zamimg.com/images/wow/icons/large/{it['icon']}.jpg",
            "wowhead_item_id": it["id"], "stat_text": _stat_text(st, stat_names), "source": source_label,
        })
        if st.get("dps") and st.get("speed"):
            weapon_dmg_speed[slot_key] = {"dmg": round(st["dps"] * st["speed"], 2), "speed": st["speed"]}

    chosen_ids = set()
    for slot_key, slot_code, restricted in ARMOR_SLOTS:
        candidates = _candidates_for_armor_slot(pool, slot_code, armor_types) if restricted else _candidates_unrestricted(pool, slot_code)
        best = _pick_best(pool, spec_id, weights, candidates, chosen_ids)
        if best:
            chosen_ids.add(best["id"])
            add_item(slot_key, best, best["dungeon_name"])
        else:
            fb = _fallback_item(fallback_by_slot, slot_key)
            if fb:
                gear.append(fb)

    for slot_key in ("finger", "finger2", "trinket", "trinket2"):
        slot_code = SLOT_FINGER if slot_key.startswith("finger") else SLOT_TRINKET
        candidates = _candidates_unrestricted(pool, slot_code)
        best = _pick_best(pool, spec_id, weights, candidates, chosen_ids)
        if best:
            chosen_ids.add(best["id"])
            add_item(slot_key, best, best["dungeon_name"])
        else:
            fb = _fallback_item(fallback_by_slot, slot_key)
            if fb:
                gear.append(fb)

    wstruct = WEAPON_STRUCTURE.get(spec_id, {"main": "1h", "off": None})
    main_kind = wstruct["main"]
    if main_kind == "ranged":
        candidates = _candidates_for_weapon(pool, {SLOT_RANGED}, weapon_types & {"Bows", "Crossbows", "Guns"})
        slot_key = "ranged"
    elif main_kind == "2h":
        candidates = _candidates_for_weapon(pool, {SLOT_TWO_HAND}, weapon_types)
        slot_key = "main_hand"
    elif main_kind == "caster":
        candidates = _candidates_for_weapon(pool, {SLOT_ONE_HAND, SLOT_MAIN_HAND}, weapon_types - {"Wands"})
        slot_key = "main_hand"
    else:  # "1h"
        candidates = _candidates_for_weapon(pool, {SLOT_ONE_HAND, SLOT_MAIN_HAND}, weapon_types)
        slot_key = "main_hand"
    best = _pick_best(pool, spec_id, weights, candidates, chosen_ids)
    if best:
        chosen_ids.add(best["id"])
        add_item(slot_key, best, best["dungeon_name"])
    else:
        fb = _fallback_item(fallback_by_slot, slot_key)
        if fb:
            gear.append(fb)

    if wstruct.get("off") == "shield":
        candidates = _candidates_for_weapon(pool, {SLOT_SHIELD}, {"Shield"})
        best = _pick_best(pool, spec_id, weights, candidates, chosen_ids)
        if best:
            chosen_ids.add(best["id"])
            add_item("off_hand", best, best["dungeon_name"])
        else:
            fb = _fallback_item(fallback_by_slot, "off_hand")
            if fb:
                gear.append(fb)
    elif wstruct.get("off") == "1h":
        candidates = _candidates_for_weapon(pool, {SLOT_ONE_HAND, SLOT_MAIN_HAND}, weapon_types)
        best = _pick_best(pool, spec_id, weights, candidates, chosen_ids)
        if best:
            chosen_ids.add(best["id"])
            add_item("off_hand", best, best["dungeon_name"])
        else:
            fb = _fallback_item(fallback_by_slot, "off_hand")
            if fb:
                gear.append(fb)

    if wstruct.get("wand"):
        candidates = _candidates_for_weapon(pool, {SLOT_RANGED}, {"Wands"})
        best = _pick_best(pool, spec_id, weights, candidates, chosen_ids)
        if best:
            chosen_ids.add(best["id"])
            add_item("ranged", best, best["dungeon_name"])
        else:
            fb = _fallback_item(fallback_by_slot, "ranged")
            if fb:
                gear.append(fb)

    # Real weapon(s) chosen above must also drive the DPS number, not just the displayed gear
    # list -- run_class()'s own "weapons" (dmg/speed feeding avg_hit()) otherwise stays whatever
    # ROTATIONS hardcoded, silently decoupling the shown item from the shown DPS. Casters
    # (main_kind == "caster") are exempt: their profile["weapons"] is deliberately [] (no
    # auto-attack modeled at all, see wow_dps_sim.py's own top-of-file disclosure), so a caster's
    # own weapon pick only ever contributes raw stats, never dmg/speed.
    profile_override = None
    if main_kind != "caster":
        original_weapons = profile.get("weapons", [])
        new_weapons = [dict(w) for w in original_weapons]
        if "main_hand" in weapon_dmg_speed and len(new_weapons) > 0:
            new_weapons[0]["dmg"] = weapon_dmg_speed["main_hand"]["dmg"]
            new_weapons[0]["speed"] = weapon_dmg_speed["main_hand"]["speed"]
        elif "ranged" in weapon_dmg_speed and len(new_weapons) > 0:
            new_weapons[0]["dmg"] = weapon_dmg_speed["ranged"]["dmg"]
            new_weapons[0]["speed"] = weapon_dmg_speed["ranged"]["speed"]
        if "off_hand" in weapon_dmg_speed and len(new_weapons) > 1:
            new_weapons[1]["dmg"] = weapon_dmg_speed["off_hand"]["dmg"]
            new_weapons[1]["speed"] = weapon_dmg_speed["off_hand"]["speed"]
        if new_weapons != original_weapons:
            profile_override = {**profile, "weapons": new_weapons}

    final_stats = wow_dps_sim.stats_from_raw(spec_id, str_=totals.get("str", 0), agi=totals.get("agi", 0),
                                              int_=totals.get("int", 0), flat_ap=totals_flat_ap, flat_sp=totals_flat_sp)
    dps, _ = wow_dps_sim.run_class(spec_id, iterations=200, fight_len=300.0, stats=final_stats, profile_override=profile_override)
    stats_block = {
        "stats": {"str": round(totals.get("str", 0)), "agi": round(totals.get("agi", 0)), "int": round(totals.get("int", 0)),
                  "sta": round(totals.get("sta", 0)), "spirit": round(totals.get("spi", 0))},
        "flat_ap": round(totals_flat_ap), "flat_sp": round(totals_flat_sp),
    }
    return gear, stats_block, dps
