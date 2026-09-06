"""Champion icon/splash URLs, sourced from Community Dragon.

Riot's Match-V1 API is text-only (character_id, no image). Community Dragon
mirrors Riot's raw game files and serves them transcoded to .png over a CDN
with permissive CORS (`Access-Control-Allow-Origin: *`) — verified live —
so these URLs can be used directly in an <img src> or set as a Wix element's
`.src` in Velo, no need to re-upload anything into Wix's Media Manager.

Not an official Riot API; this is the same asset source public TFT trackers
(tactics.tools, MetaTFT, etc.) commonly use, since Riot doesn't publish one.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import requests

from .comp_signature import clean_id, display_name

CDRAGON_TFT_DATA_URL = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"
CDRAGON_ASSET_BASE = "https://raw.communitydragon.org/latest/game/"
CACHE_PATH = Path("data/raw/_cdragon_tft.json")

# Community Dragon publishes the same TFT data file per Riot locale (verified
# live: .../cdragon/tft/fr_fr.json exists, same schema as en_us.json, real
# official French text -- not a machine translation). Every OTHER locale
# gets its own cache file; en_us keeps its original (pre-existing) cache
# path so this doesn't force a re-download of data every build already has.
def _cdragon_url(locale: str) -> str:
    return f"https://raw.communitydragon.org/latest/cdragon/tft/{locale}.json"


def _cdragon_cache_path(locale: str) -> Path:
    return CACHE_PATH if locale == "en_us" else Path(f"data/raw/_cdragon_tft_{locale}.json")

# Riot's own "paste into the in-game Team Planner" feature (added patch
# 14.22). This file is the authoritative source for the numeric code each
# champion pastes as -- no guessing needed for THAT part. What's still
# unknown (no public spec found anywhere, only two outdated community gists
# describing an older, smaller-set version of the code string) is the exact
# byte layout of the pasted code itself for the CURRENT set -- see
# build_team_planner_codes()'s docstring.
TEAMPLANNER_DATA_URL = ("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/"
                         "global/default/v1/tftchampions-teamplanner.json")
TEAMPLANNER_CACHE_PATH = Path("data/raw/_cdragon_teamplanner.json")

_TEX_RE = re.compile(r"\.(tex|dds)$", re.IGNORECASE)

# Ability text cleanup: Riot's raw tooltip strings carry HTML-ish formatting
# tags (<magicDamage>, <spellPassive>, ...), an "&nbsp;" here and there, icon
# markers ("%i:scaleAP%"), and "@VarName@" placeholders that only resolve to
# real numbers with per-rank scaling data this API doesn't expose. Rather
# than show broken markup or fabricate numbers, this strips the former and
# turns the latter into a plainly-labeled, honestly-not-a-number stand-in
# (e.g. "@PercentManaPerSecond@" -> "<em>Percent Mana Per Second</em>").
_NBSP_RE = re.compile(r"&nbsp;")
_ICON_MARKER_RE = re.compile(r"%i:[^%]*%")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
# Some placeholders carry a "*<number>" multiplier before the closing "@"
# (e.g. "@Durability*100@%" -- a 0-1 ratio the tooltip displays as a
# percentage) -- the bare \w+ variable-name group didn't match these at all
# (asterisk isn't a word character), so they leaked through completely raw
# instead of getting the same humanized-stand-in treatment as every other
# placeholder. The multiplier itself carries no information worth keeping
# (it's a display-scale factor, not a real value), so it's simply dropped.
_VAR_RE = re.compile(r"@(\w+?)(?:\*\d+)?@")
# A chunk of these placeholder names carry a Riot-internal computation suffix
# ("MagicDamageCalc1", "PhysicalDamageCalc2", "HexPercentDamageFalloffTooltip")
# rather than being a plain stat name -- checked against every @Var@ token
# across the whole current champion roster (153 distinct names): the only
# recurring "junk" suffixes are "Calc" (optionally numbered, for abilities
# with several scaling values) and "Tooltip". Left in, they turned the
# humanized fallback into something that reads like a raw API artifact
# ("Magic Damage Calc1") instead of a plain label ("Magic Damage"). Stripped
# before the camelCase split below so both read the same way.
_JUNK_SUFFIX_RE = re.compile(r"(?:Calc\d*|Tooltip)$")
# Split "PercentManaPerSecond" -> "Percent Mana Per Second" but keep runs of
# capitals together (e.g. "MRReduction" -> "MR Reduction", not "M R
# Reduction"): only break lower->upper, or upper->upper-then-lower.
_CAMEL_SPLIT_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_WHITESPACE_RE = re.compile(r"\s{2,}")


def _humanize_var(match: re.Match) -> str:
    name = _JUNK_SUFFIX_RE.sub("", match.group(1)) or match.group(1)
    spaced = _CAMEL_SPLIT_RE.sub(" ", name)
    return f"<em>{spaced}</em>"


def clean_ability_text(desc: str | None) -> str:
    if not desc:
        return ""
    text = _NBSP_RE.sub(" ", desc)
    text = _ICON_MARKER_RE.sub("", text)
    text = _HTML_TAG_RE.sub("", text)
    text = _VAR_RE.sub(_humanize_var, text)
    # Riot's source text sometimes has real control chars, sometimes the
    # literal two-character escape sequence -- normalize both.
    for token in ("\\r\\n", "\\n", "\\r", "\r\n", "\n", "\r"):
        text = text.replace(token, " ")
    return _WHITESPACE_RE.sub(" ", text).strip()


def _asset_url(tex_path: str | None) -> str:
    # Community Dragon uses the literal string "None" (not JSON null) as a
    # placeholder for some missing assets -- observed live on a few units.
    if not tex_path or tex_path == "None":
        return ""
    return CDRAGON_ASSET_BASE + _TEX_RE.sub(".png", tex_path)


def _load_cdragon_data(refresh: bool = False, locale: str = "en_us") -> dict:
    cache_path = _cdragon_cache_path(locale)
    if not refresh and cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    resp = requests.get(_cdragon_url(locale), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data), encoding="utf-8")
    return data


def build_locale_champion_text_map(set_mutator: str, locale: str, refresh: bool = False) -> dict[str, dict]:
    """Returns {clean_champion_id: {"name", "ability_name", "ability_desc"}}
    for one CDragon locale -- a lightweight, non-deduped companion to
    build_champion_image_map() used ONLY to translate display text on an
    already-built (English-keyed) champion, joined back by the same
    clean_id -- icons/slugs/cost/traits stay sourced from the English map
    everywhere else, only these three strings ever get swapped per language."""
    data = _load_cdragon_data(refresh=refresh, locale=locale)
    set_entry = next((s for s in data.get("setData", []) if s.get("mutator") == set_mutator), None)
    if not set_entry:
        return {}
    out: dict[str, dict] = {}
    for champ in set_entry.get("champions", []):
        cid = clean_id(champ.get("apiName", ""))
        if not cid:
            continue
        ability = champ.get("ability") or {}
        out[cid] = {
            "name": champ.get("name") or cid,
            "ability_name": ability.get("name") or "",
            "ability_desc": clean_ability_text(ability.get("desc")),
        }
    return out


def build_locale_trait_name_map(set_mutator: str, locale: str, refresh: bool = False) -> dict[str, str]:
    """Returns {trait_apiName: display_name} for one set/locale -- traits
    are keyed by their (English) display NAME everywhere else in this
    codebase (no stable id was ever threaded through), so this is used to
    build a {english_name: french_name} translation table by joining two
    locales' calls of this same function on apiName, not to replace that
    existing keying anywhere."""
    data = _load_cdragon_data(refresh=refresh, locale=locale)
    set_entry = next((s for s in data.get("setData", []) if s.get("mutator") == set_mutator), None)
    if not set_entry:
        return {}
    return {t["apiName"]: t["name"] for t in set_entry.get("traits", []) if t.get("apiName") and t.get("name")}


def build_locale_item_text_map(locale: str, refresh: bool = False) -> dict[str, dict]:
    """Returns {apiName: {"name", "desc"}} for EVERY item/augment record
    (augments live in the same flat `items` array, `isAugment: True`) in one
    CDragon locale -- no dedup/filtering, unlike build_full_item_catalog()/
    build_augment_data(). Those two already pick one representative apiName
    per (English) display name; this is just a flat translation lookup
    joined back onto that choice by apiName, which is identical across
    locales (only `name`/`desc` text differs)."""
    data = _load_cdragon_data(refresh=refresh, locale=locale)
    out: dict[str, dict] = {}
    for it in data.get("items", []):
        api = it.get("apiName")
        if api:
            out[api] = {"name": it.get("name"), "desc": _clean_item_desc(it.get("desc"))}
    return out


def build_champion_image_map(set_mutator: str, refresh: bool = False) -> dict[str, dict[str, str]]:
    """Returns {clean_champion_id: {"icon": url, "splash": url}} for one set
    (e.g. "TFTSet18", matching `info.tft_set_core_name` from a match). Empty
    dict if that set isn't found in Community Dragon's data yet."""
    data = _load_cdragon_data(refresh=refresh)
    set_entry = next((s for s in data.get("setData", []) if s.get("mutator") == set_mutator), None)
    if not set_entry:
        return {}

    images: dict[str, dict[str, str]] = {}
    for champ in set_entry.get("champions", []):
        cid = clean_id(champ.get("apiName", ""))
        if not cid:
            continue
        ability = champ.get("ability") or {}
        images[cid] = {
            "icon": _asset_url(champ.get("tileIcon")),
            "splash": _asset_url(champ.get("icon")),
            # Riot's apiName/characterName is frequently a leftover dev
            # codename that never gets renamed once a champion ships (e.g.
            # apiName "DA_18_Sentry" for the champion actually called
            # "Pebbles" everywhere in-game and on every other tracker) --
            # `name` is the one field on this same record carrying the real,
            # released name, so it comes along for free here.
            "name": champ.get("name") or cid,
            "cost": champ.get("cost"),
            "ability_name": ability.get("name") or "",
            "ability_desc": clean_ability_text(ability.get("desc")),
            # Empty for neutral board hazards (Murk Wolf, Rift Herald, ...) --
            # every real playable champion has at least one. Used as the
            # roster filter for the Team Builder (see build_trait_data()),
            # since match data alone never covers every champion in the set.
            "traits": champ.get("traits") or [],
        }
    return images


def build_trait_data(set_mutator: str, refresh: bool = False) -> list[dict]:
    """Returns [{"name", "icon", "effects": [{"min_units", "style"}, ...]}]
    for one set's traits (breakpoints only, ascending by min_units) -- the
    synergy thresholds a Team Builder needs to tell a visitor "3/5 active,
    next at 5". Deliberately drops CDragon's `desc`/`maxUnits`: the tooltip
    text has the same unresolvable @Placeholder@/opaque-hash-variable issue
    already documented on clean_ability_text() above, and isn't needed just
    to show numeric breakpoints -- rendering trait flavor text is left for
    a later pass rather than guessing at those values."""
    data = _load_cdragon_data(refresh=refresh)
    set_entry = next((s for s in data.get("setData", []) if s.get("mutator") == set_mutator), None)
    if not set_entry:
        return []

    traits = []
    for trait in set_entry.get("traits", []):
        name = trait.get("name")
        if not name:
            continue
        effects = sorted(
            ({"min_units": e["minUnits"], "style": e.get("style", 1)}
             for e in trait.get("effects", []) if e.get("minUnits") is not None),
            key=lambda e: e["min_units"],
        )
        if not effects:
            continue
        traits.append({"name": name, "api_name": trait.get("apiName"), "icon": _asset_url(trait.get("icon")), "effects": effects})
    return traits


_ROW_RE = re.compile(r"<row>(.*?)</row>", re.IGNORECASE | re.DOTALL)
# clean_ability_text()'s generic tag-stripper deletes <br> with no
# replacement, which is fine for champion abilities (barely ever used
# there) but wrong for item/augment desc text, where "<br><br>" is a real
# paragraph break Riot relies on to separate role-conditional clauses (e.g.
# Adaptive Helm's "...based on their Role:<br><br>Tanks and Fighters: ..."
# -- deleting it outright glues "Role:Tanks" into one word). Turned into a
# space here, before the shared cleaner runs, rather than changing that
# shared regex and risking a champion-ability regression elsewhere.
_BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


def _clean_item_desc(desc: str | None) -> str:
    if not desc:
        return ""
    return clean_ability_text(_BR_RE.sub(" ", desc))


def build_family_docs(set_mutator: str, refresh: bool = False, locale: str = "en_us") -> dict[str, dict]:
    """Returns {trait_name: {"intro": str, "breakpoint_text": [str, ...]}}
    for the Glossary's "how does this family work" section -- the flavor
    text build_trait_data() deliberately drops. `breakpoint_text` is ordered
    the same as build_trait_data()'s `effects` (ascending min_units), one
    entry per <row> Riot's own desc wraps each breakpoint in.

    Every "@MinUnits@" token is substituted with the REAL threshold number
    for its row (we already know it from `effects[].minUnits`, no guessing
    involved) before the generic clean_ability_text() humanization runs on
    the rest -- so "(@MinUnits@) A Stonebark Tree" becomes "(3) A Stonebark
    Tree", not a placeholder. Every OTHER "@Var@" token (e.g.
    "@StonebarkTreeBonusHealth@") stays a humanized stand-in exactly like
    clean_ability_text() does for champion abilities: those numbers live
    behind opaque hashed variable names CDragon doesn't resolve, so showing
    them would mean fabricating a value, not reporting one."""
    data = _load_cdragon_data(refresh=refresh, locale=locale)
    set_entry = next((s for s in data.get("setData", []) if s.get("mutator") == set_mutator), None)
    if not set_entry:
        return {}

    docs: dict[str, dict] = {}
    for trait in set_entry.get("traits", []):
        name = trait.get("name")
        desc_raw = trait.get("desc") or ""
        if not name or not desc_raw:
            continue
        min_units_by_row = [e["minUnits"] for e in sorted(
            (e for e in trait.get("effects", []) if e.get("minUnits") is not None),
            key=lambda e: e["minUnits"])]
        row_matches = _ROW_RE.findall(desc_raw)
        first_row_pos = desc_raw.lower().find("<row>")
        intro = clean_ability_text(desc_raw[:first_row_pos] if first_row_pos != -1 else desc_raw)
        breakpoint_text = []
        for i, row_raw in enumerate(row_matches):
            row = row_raw.replace("@MinUnits@", str(min_units_by_row[i])) if i < len(min_units_by_row) else row_raw
            breakpoint_text.append(clean_ability_text(row))
        docs[name] = {"intro": intro, "breakpoint_text": breakpoint_text}
    return docs


def _load_teamplanner_data(refresh: bool = False) -> dict:
    if not refresh and TEAMPLANNER_CACHE_PATH.exists():
        try:
            return json.loads(TEAMPLANNER_CACHE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    resp = requests.get(TEAMPLANNER_DATA_URL, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    TEAMPLANNER_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEAMPLANNER_CACHE_PATH.write_text(json.dumps(data), encoding="utf-8")
    return data


# The 8 base components have carried the same stat since Set 1 (this is
# stable Riot game design, not a per-set guess): B.F. Sword/Recurve Bow/
# Needlessly Large Rod/Sparring Gloves are pure AD/AS/AP/Crit, Chain Vest/
# Negatron Cloak/Giant's Belt are pure Armor/MR/Health. Tear of the Goddess
# (Mana) is deliberately left out: it shows up in genuine carry items (Spear
# of Shojin, Hextech Gunblade) and in pure support/tank items (Redemption)
# in equal measure, so the component alone doesn't say which side of the
# line it belongs on.
OFFENSE_COMPONENT_KEYWORDS = ("BFSword", "RecurveBow", "NeedlesslyLargeRod", "SparringGloves")
DEFENSE_COMPONENT_KEYWORDS = ("ChainVest", "NegatronCloak", "GiantsBelt")

# Trait emblems are built from a "wildcard" base component (the classic
# Spatula, or this set's second one, "Frying Pan") + one real component --
# but that second component only flavors which trait it visually pairs
# with, it's not a stat the emblem actually grants (an emblem's only real
# effect is "this unit counts toward trait X"). Confirmed live: e.g.
# EmblemExecutioner = FryingPan + SparringGloves reads as "offensive" by
# component alone, which would credit a unit for holding a trait item as if
# it were a damage item -- exactly the same failure mode as Thief's Gloves
# (see derive_comp()), just via item CLASSIFICATION instead of candidacy.
# Excluded before the offense/defense check runs at all, not folded into
# either keyword list, so an emblem is always "neutral" regardless of its
# other component.
WILDCARD_COMPONENT_KEYWORDS = ("Spatula", "FryingPan")


def classify_item_offense(set_mutator: str, id_prefix: str = "DA_", refresh: bool = False) -> dict[str, str]:
    """Returns {clean_item_id: "offensive" | "defensive" | "neutral"} for
    every finished item in this set, classified by its two base components
    (see the keyword lists above) rather than a hand-guessed tier list.
    "neutral" covers items mixing one offensive and one defensive component
    (Bloodthirster, Redemption...), trait emblems (see
    WILDCARD_COMPONENT_KEYWORDS), and anything unparseable -- not guessed
    either way. Backs derive_comp()'s carry detection: raw item COUNT alone
    can't tell a tank stacked with 3 defensive items from a real carry with
    3 damage items, this can."""
    data = _load_cdragon_data(refresh=refresh)
    result: dict[str, str] = {}
    for item in data.get("items", []):
        api_name = item.get("apiName") or ""
        if not api_name.startswith(id_prefix):
            continue
        cid = clean_id(api_name)
        if not cid:
            continue
        composition = item.get("composition") or []
        if any(any(k in c for k in WILDCARD_COMPONENT_KEYWORDS) for c in composition):
            result[cid] = "neutral"
            continue
        has_off = any(any(k in c for k in OFFENSE_COMPONENT_KEYWORDS) for c in composition)
        has_def = any(any(k in c for k in DEFENSE_COMPONENT_KEYWORDS) for c in composition)
        if has_off and not has_def:
            result[cid] = "offensive"
        elif has_def and not has_off:
            result[cid] = "defensive"
        else:
            result[cid] = "neutral"
    return result


def build_team_planner_codes(set_mutator: str, name_map: dict[str, str] | None = None,
                              refresh: bool = False) -> dict[str, int]:
    """Returns {display_champion_name: team_planner_code} for one set --
    CDragon's own `team_planner_code` field IS the right per-slot value
    after all. Real history of getting here (2026-09-04): a first version
    used this exact field, formatted as 4 hex digits/slot with a "01"
    header -- the user tested it in-game and the Team Planner rejected it
    ("Code invalide"). A second version, following a community gist for an
    OLDER, smaller set (TFTSet13), switched to a totally different scheme
    (1-indexed alphabetical rank, 2 hex digits/slot) -- also rejected by
    the user's live test. The real fix came from extracting the actual
    algorithm out of metatft.com's own Team Builder (a site whose Copy
    Team Code button is confirmed working): its Redux store's
    `lookups.unit_lookup[champ].code` is this exact `team_planner_code`
    field, zero-padded to 3 HEX DIGITS (not 2, not 4) -- verified by
    cross-checking 51 of 52 sampled champions' codes byte-for-byte against
    MetaTFT's live values (read directly out of its browser state, not
    guessed); the one mismatch (Ivern, off by 1) is most likely CDragon
    "latest" being one small data revision out of sync with whatever
    MetaTFT's own snapshot uses, not a flaw in this formula. The other
    piece MetaTFT's own encoder revealed: sets other than TFTSet13 and
    TFTSet4_Act2 use header "02", not "01" -- the format apparently changed
    at some point after the older gists were written. See
    site_build/build_site.py's team_planner_code() for where the header
    and 3-hex-digit/blank="000" formatting happens."""
    data = _load_teamplanner_data(refresh=refresh)
    entries = data.get(set_mutator, [])
    codes: dict[str, int] = {}
    for champ in entries:
        cid = clean_id(champ.get("character_id", ""))
        code = champ.get("team_planner_code")
        if not cid or code is None:
            continue
        codes[display_name(cid, name_map)] = code
    return codes


def build_item_image_map(needed_names: set[str], id_prefix: str = "DA_", refresh: bool = False) -> dict[str, str]:
    """Returns {clean_item_name: icon_url} for the given set of item names
    (as produced by `comp_signature.clean_id` on a match's raw itemNames,
    e.g. "GiantSlayer"). Community Dragon's `items` array isn't scoped per
    set the way champions are, and has multiple entries across sets/skins
    that can clean down to the same short name -- so this only resolves
    exactly the names asked for, taking the current set's `id_prefix`
    (matches the champion prefix, e.g. "DA_" for Set 18) as the first match,
    which is what our own match data's itemNames are cleaned from anyway."""
    if not needed_names:
        return {}
    data = _load_cdragon_data(refresh=refresh)
    remaining = set(needed_names)
    images: dict[str, str] = {}
    for item in data.get("items", []):
        if not remaining:
            break
        api_name = item.get("apiName") or ""
        if not api_name.startswith(id_prefix):
            continue
        cid = clean_id(api_name)
        if cid in remaining:
            images[cid] = _asset_url(item.get("icon"))
            remaining.discard(cid)
    return images


def build_full_item_catalog(set_mutator: str, id_prefix: str = "DA_", refresh: bool = False) -> list[dict]:
    """Returns every FINISHED item of one set (2-component combines and
    trait emblems; raw components excluded) for the Glossary's item list --
    unlike build_item_image_map(), not scoped to names seen in real matches,
    so a never-built item still gets a page.

    Each entry: {"api_name", "name", "icon", "composition": [{"name",
    "icon"}, ...], "desc"}.

    `desc` is the honest part: Community Dragon's per-set item records (the
    ones with this set's own `id_prefix`, e.g. "DA_RedBuff") carry a real
    icon and composition, but an EMPTY `desc`/`effects` -- checked live
    against all 55 Set 18 finished items, zero exceptions. The actual effect
    text lives instead on that same item's older, unprefixed "canonical"
    record (item mechanics are shared game-wide; only the icon/skin is
    reskinned per set) -- e.g. "DA_RedBuff" has no text, but
    "TFT_Item_RapidFireCannon" (an old internal name for the same item) has
    the real one. This only trusts that fallback when every candidate
    record sharing this item's name agrees on `effects` (byte-for-byte) --
    32 of 55 items clear that bar; the rest get an empty `desc` rather than
    a guessed or possibly-stale one."""
    data = _load_cdragon_data(refresh=refresh)
    all_items = data.get("items", [])
    component_by_api = {it["apiName"]: it for it in all_items if it.get("apiName")}

    desc_candidates: dict[str, list[dict]] = {}
    for it in all_items:
        if it.get("desc") and not it.get("isAugment"):
            desc_candidates.setdefault(it["name"], []).append(it)

    items = []
    for it in all_items:
        api_name = it.get("apiName") or ""
        if not api_name.startswith(id_prefix) or it.get("isAugment"):
            continue
        composition = it.get("composition") or []
        if len(composition) < 2:
            continue  # raw component or a non-combinable item, not "complete"
        comp_display = []
        for comp_api in composition:
            comp_item = component_by_api.get(comp_api)
            comp_display.append({
                "name": (comp_item or {}).get("name") or clean_id(comp_api),
                "clean_id": clean_id(comp_api), "api_name": comp_api,
                "icon": _asset_url((comp_item or {}).get("icon")) if comp_item else "",
            })

        desc = ""
        candidates = desc_candidates.get(it.get("name") or "") or []
        distinct_effects = {json.dumps(c.get("effects"), sort_keys=True) for c in candidates}
        if len(distinct_effects) == 1:
            desc = _clean_item_desc(candidates[0]["desc"])

        items.append({
            # `clean_id` matches the exact same convention build_item_image_map()
            # and every match-derived itemName already use (comp_signature.clean_id
            # on the raw apiName, e.g. "GiantSlayer") -- the slug this becomes
            # (site_build's slugify()) must line up with existing per-item icon
            # files/URLs elsewhere on the site, which `name` (CDragon's spaced
            # display form, "Giant Slayer") would NOT produce the same slug for.
            "api_name": api_name, "clean_id": clean_id(api_name), "name": it.get("name") or api_name,
            "icon": _asset_url(it.get("icon")), "composition": comp_display, "desc": desc,
        })
    items.sort(key=lambda i: i["name"])
    return items


# Augment rarity ("tags") is one of the fields CDragon hashes into an opaque
# "{hex}" placeholder instead of the real string -- but every single one of
# Set 18's 596 augments carries EXACTLY one of these 3 hashes with zero
# overlap, which is already strong evidence they're 3 mutually-exclusive
# buckets (rarity has exactly 3 values). Matched to an actual tier name via
# Riot's own "Destiny" augment family -- literal augments named "Silver
# Destiny" / "Gold Destiny" / "Prismatic Destiny" (their names spell out
# their own rarity) map 1:1 onto these 3 hashes with no exceptions across
# every "Destiny"/"DestinyPlus"/"DestinyPlusPlus" variant checked -- then
# cross-confirmed against two more independent named pairs: "Glass Cannon
# I"/"Glass Cannon II" (Silver/Gold) and "Cybernetic Uplink"/"Cybernetic
# Implants" (both apiName-suffixed "_Gold"). Three independent anchors
# agreeing, not one coincidental name match.
_SILVER_TAG_HASH = "{d11fd6d5}"
_GOLD_TAG_HASH = "{ce1fd21c}"
_PRISMATIC_TAG_HASH = "{cf1fd3af}"
_AUGMENT_TIER_BY_HASH = {_SILVER_TAG_HASH: "Silver", _GOLD_TAG_HASH: "Gold", _PRISMATIC_TAG_HASH: "Prismatic"}
_AUGMENT_TIER_SORT = {"Silver": 0, "Gold": 1, "Prismatic": 2}


def build_augment_data(set_mutator: str, refresh: bool = False) -> list[dict]:
    """Returns every augment in one set's pool, sorted Silver -> Gold ->
    Prismatic (then name): [{"api_name", "name", "icon", "desc", "tier"}].

    A set's augment pool (`setData[].augments`) is a flat list of apiNames
    that legitimately spans OLDER sets too (Set 18 reuses plenty of
    "standard" augments introduced years earlier, under their original
    apiName prefix, e.g. "TFT6_Augment_...") -- unlike champions/items,
    this is intentionally NOT filtered to one id_prefix.

    That same pool lists the same augment under more than one apiName for
    ~45% of entries (596 raw -> 409 distinct names: a years-old base
    apiName plus this set's own reskinned one, both mechanically identical
    -- confirmed: only 1 of 185 duplicate-name groups disagreed on tier,
    and every single one had a "DA_"-prefixed variant available), so
    duplicates are collapsed to that Set 18 variant, which also has the
    correct current-set icon art."""
    data = _load_cdragon_data(refresh=refresh)
    set_entry = next((s for s in data.get("setData", []) if s.get("mutator") == set_mutator), None)
    if not set_entry:
        return []
    augment_api_names = set(set_entry.get("augments") or [])
    by_api = {it["apiName"]: it for it in data.get("items", []) if it.get("apiName")}

    by_name: dict[str, dict] = {}
    for api_name in augment_api_names:
        it = by_api.get(api_name)
        if not it or not it.get("name"):
            continue
        name = it["name"]
        # Prefer this set's own "DA_"-prefixed variant over an older base
        # apiName sharing the same name (see docstring) -- first DA_ variant
        # seen wins if somehow more than one exists.
        existing = by_name.get(name)
        if existing is not None and existing["apiName"].startswith("DA_") and not api_name.startswith("DA_"):
            continue
        by_name[name] = it

    augments = []
    for name, it in by_name.items():
        tags = set(it.get("tags") or [])
        tier = next((label for h, label in _AUGMENT_TIER_BY_HASH.items() if h in tags), None)
        if not tier:
            continue  # unrecognized tag combo -- skipped, not guessed
        augments.append({
            "api_name": it["apiName"], "clean_id": clean_id(it["apiName"]), "name": name,
            "icon": _asset_url(it.get("icon")), "desc": _clean_item_desc(it.get("desc")),
            "tier": tier,
        })
    augments.sort(key=lambda a: (_AUGMENT_TIER_SORT.get(a["tier"], 9), a["name"]))
    return augments
