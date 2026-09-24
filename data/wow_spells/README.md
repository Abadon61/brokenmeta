# WoW: Forever spell glossary — schema

One file per class: `data/wow_spells/<class>.json`. This is the combat-mechanics glossary (costs,
cooldowns, damage formulas) that a simulator reads from — it is deliberately separate from
`data/wow_talents/<class>.json`, which describes the talent *tree layout* (rows, columns, point
gates) for the talent calculator. The two are cross-referenced by `wowhead_talent_id` where a talent
also has real combat mechanics worth simulating (e.g. Death Wish, Bloodthirst).

**Never invent a value.** Every number comes from that ability's own live WoW: Forever Wowhead
tooltip (`wowhead.com/forever/spell=<id>`) unless `notes` says otherwise. Anything not yet looked up
goes in the top-level `gaps` array, not a guessed placeholder.

## Top-level shape

```json
{
  "class": "warrior",
  "resource_system": "rage",
  "schema_version": 2,
  "source_note": "free text: where these values generally come from",
  "gaps": ["plain-English description of what's not sourced yet, and why it matters"],
  "abilities": [ ... ],
  "talents": { "<tree_name>": [ ... ], "<tree_name>": [ ... ] }
}
```

- `resource_system`: the class's primary resource (`"rage"`, `"mana"`, `"energy"`, ...). A spec that
  uses a secondary resource (e.g. Rogue combo points) notes it in that ability's own `resource_cost`
  instead of a second top-level field.
- `talents`: one array per talent tree the class has (all of them, not just the "DPS" one — a Fury
  Warrior can still spend points in Arms; a build's spec name comes from wherever it puts the most
  points, which the relevant Icy Veins guide already tells us for each recommended build).

## Ability entry (`abilities[]`)

| Field | Type | Notes |
|---|---|---|
| `id` | string | Our own stable slug, e.g. `"warrior_bloodthirst"`. Primary key within this project. |
| `wowhead_spell_id` | number | The *real* Wowhead spell ID. Never omit this — it's what lets us link to or render the actual Wowhead tooltip (the site already loads Wowhead's own tooltip widget elsewhere), even though `id` is our own. |
| `name` | `{en, fr}` | Real localized name. |
| `category` | string | `"core_ability"` or `"talent_capstone"` (a talent that grants/is a real spell, not just a passive modifier — cross-reference via the talent's own `see_ability_id`). |
| `trees` | string[] | Which talent tree(s) gate this, if any; `[]` for a baseline class ability nobody needs to spec into. |
| `rank` | number \| `"max"` \| null | Which rank these values are for. |
| `max_rank_total` | number \| null | How many ranks the ability has in total. |
| `min_level` | number | Level this rank is first trainable/reachable at. |
| `resource_cost` | object | Numeric only, one key per resource type actually spent, e.g. `{"rage": 30}` or `{"health_pct": 20}`. Never a formatted string. |
| `cooldown_sec` | number \| null | `null` = no cooldown (may still share the GCD). |
| `gcd_sec` | number | 0 if it doesn't use the GCD. |
| `cast_time` | string | `"instant"`, `"on next melee swing"`, or a cast time description. |
| `school` | string | `"physical"`, `"fire"`, etc. |
| `mechanic` | string \| null | e.g. `"bleeding"`, matching the tooltip's own "Mechanic" field. |
| `effects` | object[] | **Always an array**, even for a single effect — found necessary validating the schema on Fire Mage: Fireball and Pyroblast each deal one direct hit *and* apply their own DoT in the same cast, which doesn't fit a single `effect` object. See **effect kinds** below. |
| `flags` | string[] | Free-form but reuse existing ones across classes where the mechanic is the same (e.g. `"no_dual_wield_miss_penalty"`, `"no_glancing_blow"`, `"discount_power_on_miss"`). |
| `notes` | string | Anything a simulator author needs to know that isn't captured structurally — assumptions, ambiguities, cross-era discrepancies. |
| `source_url` | string | Direct link to the tooltip this was read from. |

### Effect kinds (`effect.kind`)

Fixed vocabulary — add a new one here (not an ad hoc string) if a class needs something not listed:

- `direct_damage` — one instant or cast-time hit. Fields: any of `ap_coeff`, `sp_coeff`, `flat`, `weapon_pct`, `dmg_range` (`[low, high]` if the tooltip shows a range rather than one number). `sp_coeff` should come from the tooltip's own shown "SP mod: X" value when present — real, precise, don't derive it yourself.
- `periodic_damage` — a DoT/bleed, standalone (e.g. Rend) or attached to a direct-damage spell (e.g. Fireball's built-in burn — put both a `direct_damage` and a `periodic_damage` entry in that ability's `effects` array). Fields: `total_damage`, `duration_sec`, `tick_interval_sec`, `damage_per_tick`, `sp_coeff` if shown, `can_crit` (bool — check the tooltip's own flags, don't assume).
- `normalized_weapon_damage` — hits for weapon damage, optionally to multiple targets. Fields: `pct`, `max_targets`, optional `flat` bonus.
- `flat_bonus_on_next_swing` — e.g. Heroic Strike. Fields: `flat`.
- `self_buff` / `party_buff` — a buff, not damage. Fields: whatever stats it changes, `duration_sec`, `radius_yd` if relevant.
- `target_debuff_stacking` — e.g. Sunder Armor. Fields: `per_stack` value, `max_stacks`, `duration_sec`.
- `resource_generation` — e.g. Bloodrage. Fields: `immediate`, `over_time`, `over_time_duration_sec`.
- `heal` / `periodic_heal` — for healing specs, mirrors `direct_damage` / `periodic_damage`.
- `proc_trigger` — grants a chance-based buff/effect on some condition; describe the condition and result in `notes` until a common shape emerges from real use.
- `combo_point_scaling` — a finisher whose effect depends on how many combo points (or an equivalent secondary resource) are spent, found validating the schema on Rogue. Fields: `resource` (e.g. `"combo_points"`), and either `table` (an object keyed `"1"`..`"5"` when the tooltip gives exact per-count values, e.g. Eviscerate's real damage at each combo point count — prefer this over reverse-engineering a formula) or, only when the tooltip states one explicitly, `base` + `per_point` for a genuinely linear stat like a buff's duration (e.g. Slice and Dice: `duration_sec = base + per_point × combo_points`).

### Non-stacking effects (buffs, debuffs, DoTs)

**Default rule, confirmed by the user from real gameplay knowledge: re-applying a buff/debuff/DoT from a *different cast of the same ability* refreshes it — the new application replaces the old one outright, it does not stack or add.** This is the default for every `self_buff`, `party_buff`, `target_debuff_stacking` (within one "stack slot" — `max_stacks` governs genuinely-cumulative stacks like Sunder Armor, not repeated casts beyond that cap) and `periodic_damage` entry unless a `stacks: true`-style field says otherwise. A simulator should refresh-not-stack by default; only add explicit stacking logic where a tooltip clearly says multiple instances coexist.

## Talent entry (`talents.<tree>[]`)

| Field | Type | Notes |
|---|---|---|
| `id` | string | Our own stable slug. |
| `wowhead_talent_id` | string | The real ID from `data/wow_talents/<class>.json` (e.g. `"n105933"`) — keeps the two files cross-referenceable. |
| `name` | `{en, fr}` | Real localized name. |
| `row` / `col` | number | Position in the tree, matching `wow_talents.py`'s layout. |
| `max_rank_total` | number | |
| `effect_per_rank` | string | Plain-English real tooltip text summary — not a full mechanical breakdown unless it's DPS-relevant. |
| `see_ability_id` | string \| null | If this talent grants/is a real spell with its own mechanical entry, point to that `abilities[].id` instead of duplicating its numbers here. |
| `dps_relevant` | bool | Whether this talent affects sustained single-target DPS at all — lets a simulator builder filter noise (utility/defensive talents) at a glance. |

## Adding a class

1. Copy this shape, not another class's file verbatim — resource system and available trees differ.
2. Look up every ability's own tooltip; never carry a number over from another class or another WoW
   version without flagging it in `notes`.
3. List anything not yet looked up in `gaps` rather than guessing or leaving a silent 0.
