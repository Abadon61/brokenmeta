"""Turn one match participant into a "comp signature": a dominant trait +
carry, the way a player would actually say the comp's name out loud (e.g.
"Riftbeast Krug18"), not a full technical description of the board.

Riot doesn't publish a comp id or comp names -- that's 100% manual curation
on public trackers (tactics.tools, MetaTFT, ...), not something derivable
from the API. This heuristic gets closer to that naming convention without
hand-maintaining an archetype list: the SINGLE most-activated trait (ranked
by style/tier, i.e. how "activated" it is) plus the unit holding the most
items (the apparent carry) is what identifies the comp. A couple more
traits are kept separately in `traits` purely for display (tags on a card),
without affecting the comp's identity/grouping -- that stays on the
single dominant trait, both because that's closer to how comps actually get
named colloquially, and because it groups more real games under fewer
buckets, which matters a lot given how thin the sample is at this scale.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_PREFIX_RE = re.compile(r"^[A-Za-z]+_?\d*_")  # e.g. "DA_18_" / "TFT18_" -> strip
_DIGITS_RE = re.compile(r"\d+")  # e.g. embedded set number: "Riftbeast18" -> "Riftbeast"
# Known junk variant markers Riot leaves on some champion IDs -- not a
# meaningful part of the name, just noise (e.g. "MasterYi_AD" -> "MasterYi",
# "Lux18_Base" -> "Lux"). Deliberately NOT a blanket "strip after first
# underscore": some trait ids carry a real, distinct suffix that changes
# their meaning (e.g. "Maokai_UniqueTrait"), so only known junk tokens are
# removed, not every underscore-separated tail.
_JUNK_SUFFIX_RE = re.compile(r"_(AD|AP|Base)$", re.IGNORECASE)


def clean_id(character_id: str) -> str:
    name = _PREFIX_RE.sub("", character_id) or character_id
    name = _DIGITS_RE.sub("", name)
    name = _JUNK_SUFFIX_RE.sub("", name)
    return name or character_id


def is_complete_item(name: str) -> bool:
    """Raw components ("Component_BFSword" etc.) are never a finished
    build -- combos and item stats should only ever reflect combined items.
    Shared by tierlist.py (per-comp) and champion_stats.py (per-champion,
    across every comp it shows up in)."""
    return not name.startswith("Component_")


def display_name(clean_champ_id: str, name_map: dict[str, str] | None) -> str:
    """`clean_id()` only strips API-id noise (prefixes/digits/suffixes) --
    it does NOT recover a champion's real name when Riot's apiName is
    itself a leftover dev codename (e.g. "Sentry" for a champion actually
    called "Pebbles"). `name_map` (built from Community Dragon's `name`
    field, see champion_images.py) is the correction for that; falls back
    to the cleaned id unchanged when no map is supplied or the id isn't in
    it, so every caller stays backward compatible without one."""
    return (name_map or {}).get(clean_champ_id, clean_champ_id)


@dataclass
class CompSignature:
    key: str
    label: str
    traits: list[str] = field(default_factory=list)
    carry: str | None = None


def _active_traits(traits: list[dict]) -> list[dict]:
    return [t for t in traits if t.get("tier_current", 0) > 0]


def derive_comp(participant: dict, identity_trait_count: int = 1, display_trait_count: int = 3,
                 name_map: dict[str, str] | None = None,
                 item_offense: dict[str, str] | None = None) -> CompSignature:
    active = _active_traits(participant.get("traits") or [])
    # Rank by how "activated" a trait is: style (bronze/silver/gold/chromatic)
    # first, then how many breakpoints it has cleared, then unit count.
    active.sort(key=lambda t: (t.get("style", 0), t.get("tier_current", 0), t.get("num_units", 0)),
                reverse=True)
    identity_traits = [clean_id(t["name"]) for t in active[:identity_trait_count]]
    display_traits = [clean_id(t["name"]) for t in active[:display_trait_count]]

    units = participant.get("units") or []
    carry = None
    if units:
        # A 5-cost is never the comp's identity, even fully itemized: you
        # can't build a board AROUND acquiring one (shop odds for it are
        # near-zero until very late, so nobody levels or economizes
        # specifically to find it) -- it's whatever the game happened to
        # hand you at 8-9, on top of a comp that was already built and
        # already working. The unit that comp was actually built around,
        # the one worth investing in early enough to star up, is by
        # necessity 1-4 cost -- rarity 4 (API's 0-indexed cost) excluded
        # from candidacy entirely rather than just deprioritized.
        not_five_cost = [u for u in units if u.get("rarity", 0) != 4] or units

        # Thief's Gloves grants 2 RANDOM completed items' effects -- Riot's
        # API reports those as real itemNames entries right alongside it
        # (confirmed live: e.g. a Leona -- a tank -- holding
        # ["ThiefsGloves", "InfinityEdge", "Bloodthirster"]), completely
        # indistinguishable from deliberately-built items by that field
        # alone. A unit wearing it can look like the best-itemized damage
        # dealer on the board purely by RNG, with zero actual investment
        # behind it -- so it's excluded from carry candidacy entirely,
        # same as a 5-cost.
        candidates = [u for u in not_five_cost
                      if not any(clean_id(n) == "ThiefsGloves" for n in (u.get("itemNames") or []))
                      ] or not_five_cost

        def carry_score(u: dict) -> tuple:
            item_names = [clean_id(n) for n in (u.get("itemNames") or [])]
            # Raw item COUNT alone picks the tank half the time -- a
            # frontline unit stacked with Warmog's/Gargoyle/Sunfire reads as
            # "3 items" exactly like a real carry with 3 damage items does.
            # `item_offense` (see champion_images.classify_item_offense)
            # tells offensive items (built from AD/AP/AS/Crit components)
            # apart from defensive ones (Armor/MR/Health components), so the
            # unit doing the most actual damage-building wins first. Star
            # level comes right after: a deliberately-built cheap carry gets
            # 2-3-starred (that's the whole point of building around it,
            # not just leveling past it), which raw item count alone won't
            # always reflect -- ranked ahead of total item count for that
            # reason.
            offensive = (sum(1 for n in item_names if item_offense.get(n) == "offensive")
                         if item_offense else 0)
            star = u.get("tier", 0)
            items = len(item_names)
            rarity = u.get("rarity", 0)
            return (offensive, star, items, rarity)

        carry_unit = max(candidates, key=carry_score)
        carry = display_name(clean_id(carry_unit.get("character_id", "")), name_map)

    trait_part = "+".join(identity_traits) if identity_traits else "Generic"
    # `key` keeps the carry suffix -- two comps sharing the same dominant
    # trait but a different carry are genuinely different comps for
    # tier-list purposes (identity hinges on ONE dominant trait, not two,
    # which also pools more games per comp). `label` shows both the trait
    # and the carry name (e.g. "Summoner Sett") -- the product wants the
    # carry back in the visible name, not just as a separate icon/field.
    # `traits` carries a couple more traits purely for display tags.
    key = trait_part + (f"_{carry}" if carry else "")
    trait_label = trait_part.replace("+", " ")
    label = f"{trait_label} {carry}" if carry else trait_label
    return CompSignature(key=key, label=label, traits=display_traits, carry=carry)
