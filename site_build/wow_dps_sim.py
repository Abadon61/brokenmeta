"""Internal, generic level-20 DPS simulator driven by data/wow_spells/<class>.json.

The engine and its interactive sliders stay internal-only (2026-09-25, user request: no public
Monte-Carlo sandbox), but `build_ranking()` below feeds its AGGREGATE numbers into the public
cross-spec DPS ranking on /wow-forever/ (build_site.py imports this module directly at build
time -- no server, no API, just a Python function call baked into the static HTML). Run this
file directly (`py site_build/wow_dps_sim.py`, from the project root) to print the same ranking
as plain text for local debugging.

Reuses the same architecture already validated for the Fury Warrior engine
(site_build/js/wow-warrior-sim.js) -- event queue, per-swing hit/crit RNG, non-stacking
DoT/buff refresh, per-source damage breakdown -- but generalized to read ability cost,
cooldown, cast time and damage formulas straight from each class's own glossary instead of
hardcoding class-specific numbers. Only the ROTATION PRIORITY per class stays hand-written
below (ROTATIONS), because it's real game knowledge that isn't part of the glossary schema
-- exactly like the Warrior engine's own rotation choice. Every entry cites the sourced
priority note (in that class's own data/wow_spells/<class>.json) that justifies it.

Deliberately not modeled, matching what each class's own glossary already discloses as a
gap: Warlock pet damage (Imp/Voidwalker -- no sourced formula found yet, unlike Hunter's
pet below), wand damage (Mage/Priest/Warlock), Mana regeneration or depletion (no sourced
regen rate for any class -- Mana is treated as unconstrained: this measures "is the
rotation's damage output," not "for how long it can be sustained"), long-duration
low-maintenance self-buffs that aren't really part of the active rotation (Battle Shout,
Rockbiter Weapon -- their stat bonus belongs in your own stat input, not a scripted cast),
and the extra talent-rank sliders the bespoke Warrior tool exposes (Cruelty, Precision,
Flurry, Unbridled Wrath, Dual Wield Specialization, Boundless Rage) -- those aren't sourced
for the other 8 classes yet, so this generic pass compares base rotations on equal stats,
not fully talented character sheets.

2026-09-26: Hunter's own Auto Shot and pet are now both modeled (see the pet ratio constant's
comment further down for the pet's sourcing and its disclosed Classic-approximation caveats).

2026-09-26: stats are now real level-20 BiS gear, not an illustrative placeholder. Each
spec's {ap, sp, hit, crit} comes from bis_stats_for_spec(), which converts the raw Str/Agi/
Int/flat-AP/flat-SP totals in data/wow_items/bis_level20_stats.json (sourced from
foreverchanges.pro's BIS lists, cross-checked against Icy Veins/Wowhead for Warrior) through
the real Classic Str->AP / Agi->Crit% / Int->SpellCrit% ratios and base Crit/Hit values also
cited in that file (from Wowhead's own Classic "Stats and Attributes" guide). One weak link
stays disclosed there: Shaman's base character stats (no gear) aren't independently verified
against a primary source. DEFAULT_STATS below is now just a never-should-fire fallback.
"""
import argparse
import heapq
import json
import random
import re

import wow_spells

DODGE_CHANCE = 0.05          # same-level-target baseline -- see wow-warrior-sim.js for the citation
GLANCE_CHANCE = 0.10
GLANCE_DAMAGE_MULT = 0.70
OVERPOWER_WINDOW = 5.0        # Vanilla WoW Wiki -- Overpower: usable within 5s of a target Dodge
ENERGY_CAP = 100.0
ENERGY_REGEN_PER_SEC = 10.0   # Vanilla WoW Wiki -- Energy: fixed 10/sec, not level- or haste-dependent
SND_HASTE_MULT = 1.20         # Slice and Dice's own sourced "+20% melee attack speed" (rogue.json)
HIT_FACTOR_MH = {"normal": 3.5, "crit": 7.0}
HIT_FACTOR_OH = {"normal": 1.75, "crit": 3.5}

# Hunter pet auto-attack, added 2026-09-26 (user request: "integrer le dps de son pet"). WoW
# Forever's own Icy Veins guides (Beast Mastery/Marksmanship/Survival) confirm pets scale with
# the hunter's stats and inherit hit/crit, but give NO exact formula or base pet stats -- and
# explicitly call out that pet mechanics changed from Classic ("pets no longer have an inherent
# damage buff or reduction based on type", "pet now has scaling with your stats like in LATER
# versions of WoW"), so the real Classic numbers below are a disclosed, labeled APPROXIMATION,
# not a confirmed Forever value (per-user decision, since no primary Forever source exists yet):
#   - pet melee AP = 22% of the hunter's own ranged AP (wow-petopia.com/classic_lk/stats_scaling.php,
#     a long-standing Classic pet reference; corroborated by community Classic AP-formula pages)
#   - pet inherits the hunter's own hit and crit chance (same Petopia page, and directly stated in
#     Forever's own Icy Veins BM guide: "pets also inherit your critical strike chance")
#   - pet base attack speed = 2.0s (Petopia's Classic/BC pet-attack-speed pages; BC Classic
#     normalized every pet family to 2.0s -- Forever's own bug tracker suggests some pets may
#     currently have per-family speeds again, but no normalized replacement value is given, so
#     2.0s stays the best-available baseline)
# NOT modeled (undisclosed in every source checked, so left at zero rather than guessed): the
# pet's own base Strength/Agility-derived AP and its own base weapon damage -- real pets have
# stats of their own on top of the inherited 22%, so this UNDER-counts true pet DPS. Uptime is
# idealized at 100% (pet attacking from t=0 for the whole fight), matching how the rest of this
# engine already treats buffs/DoTs, though a real pet can die, get out of range, or be re-summoned.
PET_AP_RATIO_OF_HUNTER_RANGED_AP = 0.22
PET_ATTACK_SPEED_SEC = 2.0


def rage_conversion_value(level):
    """Real classic-WoW formula (see wow-warrior-sim.js for the full citation and derivation)."""
    return 0.0091107836 * level * level + 3.225598133 * level + 4.2652911


RAGE_CONVERSION_L20 = rage_conversion_value(20)


def roll(chance):
    return random.random() < chance


def parse_cast_time(raw):
    """"instant" -> 0.0, "3 sec" -> 3.0, "2 sec (Improved Corruption, ...)" -> 2.0 -- matches a
    leading number+sec even when the field also carries descriptive caveat text (real bug found
    2026-09-26: the old raw.endswith(" sec") check silently read Corruption's caveat-laden
    cast_time as 0.0 instead of 2.0, since the full string doesn't end in " sec"). Anything else
    (e.g. Heroic Strike's "on next melee swing", unused by any class modeled here) -> 0.0, since
    no glossary ability used here needs it."""
    if not raw or raw == "instant":
        return 0.0
    m = re.match(r"([\d.]+)\s*sec\b", raw)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return 0.0
    return 0.0


# ---- generic effect resolution (reads straight off each ability's effects[]) --------------

def resolve_direct_damage(effect, ap, sp, crit_frac):
    if "dmg_range" in effect:
        base = random.uniform(*effect["dmg_range"])
    else:
        base = effect.get("flat", 0)
    base += ap * effect.get("ap_coeff", 0) + sp * effect.get("sp_coeff", 0)
    is_crit = roll(crit_frac)
    return base * (2.0 if is_crit else 1.0), is_crit


def resolve_normalized_weapon_damage(effect, avg_hit, sp, crit_frac):
    """avg_hit is one full white-swing's worth of damage (weapon + AP/14 x speed), consistent with
    how the Warrior engine already treats Sinister-Strike-like "100% weapon dmg" abilities."""
    base = avg_hit * effect.get("pct", 1.0) + effect.get("flat", 0)
    if "dmg_range" in effect:
        base += random.uniform(*effect["dmg_range"])
    base += sp * effect.get("sp_coeff", 0)
    is_crit = roll(crit_frac)
    return base * (2.0 if is_crit else 1.0), is_crit


def resolve_periodic_setup(effect, sp):
    duration = effect["duration_sec"]
    interval = effect["tick_interval_sec"]
    ticks = round(duration / interval)
    per_tick = effect.get("damage_per_tick")
    if per_tick is None:
        per_tick = effect["total_damage"] / ticks
    per_tick += sp * effect.get("sp_coeff", 0)
    return duration, interval, per_tick, effect.get("can_crit", False)


def resolve_combo_point_table(effect, cp, crit_frac):
    lo, hi = effect["table"][str(cp)]
    base = random.uniform(lo, hi)
    is_crit = roll(crit_frac)
    return base * (2.0 if is_crit else 1.0), is_crit


class Sim:
    def __init__(self, cls_id, profile, glossary, stats, fight_len):
        self.cls_id = cls_id
        self.profile = profile
        self.abilities = {a["id"]: a for a in glossary.get("abilities", [])}
        self.stats = stats
        self.fight_len = fight_len
        self.events = []
        self.seq = 0
        self.resource = 0.0
        self.resource_cap = ENERGY_CAP if profile["resource"] == "energy" else 100.0
        self.combo_points = 0
        self.cooldowns = {}
        self.gcd_ready = 0.0
        self.dot_ends = {}
        self.dot_epoch = {}
        self.buff_ends = {}
        self.once_used = set()
        self.dodge_window_until = -1.0
        self.active_seal = None
        self.swing_speed_mult = 1.0
        self.pending_swing_bonus = 0.0
        self.pending_swing_bonus_tag = None
        self.dmg_by = {}
        self.total_dmg = 0.0
        self.trace = None  # set to [] before run() to record a play-by-play (see trace_rotation())
        self._now = 0.0

    def push(self, time, kind, data=None):
        if time > self.fight_len:
            return
        self.seq += 1
        heapq.heappush(self.events, (time, self.seq, kind, data))

    def add_dmg(self, amount, tag, is_tick=False):
        self.total_dmg += amount
        self.dmg_by[tag] = self.dmg_by.get(tag, 0.0) + amount
        if self.trace is not None:
            label = (self.abilities.get(tag, {}).get("name", {}).get("fr") or tag) if tag not in ("white",) else "Attaque de base"
            marker = "  (tick)" if is_tick else ""
            self.trace.append(f"{self._now:6.2f}s  {label:28s} {amount:5.1f} dégâts{marker}")

    def avg_hit(self, idx=0):
        weapons = self.profile.get("weapons", [])
        if not weapons:
            return 0.0
        # Attack Power adds AP/14 damage per second of the weapon's own (base) speed to each hit.
        # Fixed 2026-09-26: this used to add a flat AP/14 per hit regardless of speed, which
        # undervalued AP (and Strength) by a factor of ~2.5-3.3 for every melee/ranged spec.
        # Classic-era special attacks use the weapon's real speed (no TBC-style normalization).
        wpn = weapons[idx]
        return wpn["dmg"] + self.stats["ap"] / 14 * wpn["speed"]

    def off_cooldown(self, aid, t):
        group = self.abilities[aid].get("cooldown_group")
        if group and t < self.cooldowns.get(f"group:{group}", 0):
            return False
        return t >= self.cooldowns.get(aid, 0)

    def has_resource(self, aid):
        ab = self.abilities[aid]
        cost = ab.get("resource_cost", {})
        res = self.profile["resource"]
        return not (res in ("rage", "energy") and res in cost and self.resource < cost[res])

    def pay_cost(self, aid):
        ab = self.abilities[aid]
        cost = ab.get("resource_cost", {})
        res = self.profile["resource"]
        if res in ("rage", "energy") and res in cost:
            self.resource -= cost[res]

    def talent_mod(self, aid):
        """Real, quantified talent-point modifiers for this spec's own build (see ROTATIONS'
        "talent_mods" -- only added where the exact numeric effect is sourced from the real
        talent tooltip AND confirmed to be in that spec's own real 11-point build, not just
        "a talent that exists somewhere in the tree"). Empty dict if this spec has none for aid."""
        return self.profile.get("talent_mods", {}).get(aid, {})

    def lockout(self, aid):
        ab = self.abilities[aid]
        override = self.talent_mod(aid).get("cast_time_override")
        cast_time = override if override is not None else parse_cast_time(ab.get("cast_time"))
        return max(cast_time, ab.get("gcd_sec", 1.5) or 0)

    def apply_effects(self, aid, t, combo_points_used=None):
        ab = self.abilities[aid]
        sp, crit_frac = self.stats["sp"], self.stats["crit"]
        dmg_mult = self.talent_mod(aid).get("damage_mult", 1.0)
        for eff in ab.get("effects", []):
            kind = eff["kind"]
            if kind == "direct_damage":
                dmg, _ = resolve_direct_damage(eff, self.stats["ap"], sp, crit_frac)
                self.add_dmg(dmg * dmg_mult, aid)
            elif kind == "normalized_weapon_damage":
                dmg, _ = resolve_normalized_weapon_damage(eff, self.avg_hit(0), sp, crit_frac)
                self.add_dmg(dmg * dmg_mult, aid)
            elif kind == "periodic_damage":
                duration, interval, per_tick, _ = resolve_periodic_setup(eff, sp)
                per_tick *= dmg_mult
                self.dot_ends[aid] = t + duration
                # Every (re)application starts a fresh epoch and always (re)schedules its own tick
                # chain -- real bug found 2026-09-26: the old "if not was_active: push" logic
                # assumed a refresh always lands before the previous application's tracked expiry,
                # but a refresh landing even slightly AFTER it (was_active reads False) used to
                # leave the ORIGINAL tick chain alive (its own `t <= dot_ends` check still passes,
                # since dot_ends had just been pushed further out by the new application) --
                # spawning a second, permanent, parallel tick chain. Repeated a few times this
                # compounded a DoT's real DPS several-fold. The epoch counter makes a tick chain
                # from an earlier application stop rescheduling itself the moment a newer
                # application exists, regardless of exact timing.
                self.dot_epoch[aid] = self.dot_epoch.get(aid, 0) + 1
                epoch = self.dot_epoch[aid]
                self.push(t + interval, "dot_tick", {"aid": aid, "interval": interval, "per_tick": per_tick, "epoch": epoch})
                if self.trace is not None:
                    name = self.abilities.get(aid, {}).get("name", {}).get("fr") or aid
                    self.trace.append(f"{self._now:6.2f}s  {name:28s} posé (DoT, {duration:.0f}s)")
            elif kind == "resource_generation" and eff.get("resource") == "combo_points":
                self.combo_points = min(5, self.combo_points + eff.get("immediate", 0))
            elif kind == "combo_point_scaling":
                cp = max(1, min(5, combo_points_used or self.combo_points))
                if "table" in eff:
                    dmg, _ = resolve_combo_point_table(eff, cp, crit_frac)
                    self.add_dmg(dmg, aid)
                elif "dot_table" in eff:
                    total = eff["dot_table"][str(cp)]
                    interval = eff.get("tick_interval_sec", 2)
                    duration = eff.get("duration_sec", 12)
                    ticks = round(duration / interval)
                    per_tick = total / ticks
                    self.dot_ends[aid] = t + duration
                    self.dot_epoch[aid] = self.dot_epoch.get(aid, 0) + 1
                    self.push(t + interval, "dot_tick", {"aid": aid, "interval": interval, "per_tick": per_tick, "epoch": self.dot_epoch[aid]})
                elif "base" in eff:
                    self.buff_ends[aid] = t + eff["base"] + eff["per_point"] * cp
                    self.swing_speed_mult = SND_HASTE_MULT
            elif kind == "flat_bonus_on_next_swing":
                self.pending_swing_bonus += eff.get("flat", 0)
                self.pending_swing_bonus_tag = aid
            elif kind == "self_buff":
                self.buff_ends[aid] = t + eff.get("duration_sec", 0)
            # party_buff / heal / proc_trigger: not relevant to a solo DPS total, or handled
            # by a dedicated hook (Judgement's proc_trigger -- see handle_judgement()).

    def handle_judgement(self, aid, t):
        """Judgement deals no damage of its own -- it releases whichever Seal is active
        (paladin.json's own real mechanic). Not generic: this is the one cross-ability
        reference the schema doesn't encode, so it's a named special case."""
        if not self.active_seal:
            return
        seal = self.abilities.get(self.active_seal)
        if not seal:
            return
        for eff in seal.get("effects", []):
            if eff.get("kind") == "proc_trigger" and "dmg_range" in eff:
                dmg, _ = resolve_direct_damage(eff, self.stats["ap"], self.stats["sp"], self.stats["crit"])
                self.add_dmg(dmg, aid)

    def do_swing(self, t, idx):
        weapons = self.profile["weapons"]
        wpn = weapons[idx]
        is_oh = wpn.get("offhand", False)
        hit_frac = self.stats["hit"] - (0.19 if len(weapons) > 1 else 0.0)
        roll_val = random.random()
        if roll_val >= hit_frac:
            if self.trace is not None:
                self.trace.append(f"{t:6.2f}s  {'OH ' if is_oh else 'MH '} attaque de base -- raté")
            pass  # miss
        elif roll(DODGE_CHANCE):
            self.dodge_window_until = t + OVERPOWER_WINDOW
            if self.trace is not None:
                self.trace.append(f"{t:6.2f}s  {'OH ' if is_oh else 'MH '} attaque de base -- esquivée")
        else:
            is_glance = roll(GLANCE_CHANCE)
            is_crit = (not is_glance) and roll(self.stats["crit"])
            base = wpn["dmg"] + self.stats["ap"] / 14 * wpn["speed"]  # see avg_hit()
            if is_oh:
                base *= 0.5
            seal_id = self.profile.get("seal_ability")
            if seal_id and t <= self.buff_ends.get(seal_id, -1.0) and not is_oh:
                seal = self.abilities.get(seal_id, {})
                for eff in seal.get("effects", []):
                    if eff.get("kind") == "self_buff" and "per_swing_bonus_dmg_range" in eff:
                        base += random.uniform(*eff["per_swing_bonus_dmg_range"])
            tag = "white"
            if not is_oh and self.pending_swing_bonus > 0:
                base += self.pending_swing_bonus
                tag = self.pending_swing_bonus_tag or "white"
                self.pending_swing_bonus = 0.0
                self.pending_swing_bonus_tag = None
            mult = GLANCE_DAMAGE_MULT if is_glance else (2.0 if is_crit else 1.0)
            dmg = base * mult
            self.add_dmg(dmg, tag)
            if self.profile["resource"] == "rage":
                self.gain_rage(dmg, is_crit, is_oh)
        speed = wpn["speed"] / self.swing_speed_mult
        self.push(t + speed, "swing", {"idx": idx})

    def gain_rage(self, dealt, is_crit, is_oh):
        f = (HIT_FACTOR_OH if is_oh else HIT_FACTOR_MH)["crit" if is_crit else "normal"]
        speed = self.profile["weapons"][1 if is_oh else 0]["speed"]
        raw = (15 * dealt) / (4 * RAGE_CONVERSION_L20) + (f * speed) / 2
        cap = (15 * dealt) / RAGE_CONVERSION_L20
        self.resource = min(self.resource_cap, self.resource + min(raw, cap))

    def gain_energy(self, dt):
        self.resource = min(self.resource_cap, self.resource + ENERGY_REGEN_PER_SEC * dt)

    def rule_condition(self, aid, kind, t):
        """Whether this rule is the right thing to do next, ignoring resource availability
        (cooldowns and DoT/buff/combo-point state only). Checked in priority order BEFORE
        resource: a rogue should wait for 60 Energy to re-cast Backstab rather than
        immediately downgrading to a cheaper, lower-priority Sinister Strike just because
        it's affordable sooner -- that's a real rotation-priority choice, not a resource-
        starvation fallback, and collapsing the two produced a real bug caught while
        building this engine (Backstab never fired; see git history for the fix)."""
        if not self.off_cooldown(aid, t):
            return False
        if kind == "once":
            return aid not in self.once_used
        if kind == "builder":
            return self.combo_points < 5
        if kind == "finisher_damage":
            return self.combo_points >= 5
        if kind == "finisher_dot":
            # Real, sourced Feral Druid threshold (Wowhead's own level-20 guide): Rip at 4+
            # combo points if the target will live at least ~6s, not a full 5 like Eviscerate.
            return self.combo_points >= 4
        if kind == "swing_enhancer":
            return self.pending_swing_bonus == 0
        if kind == "finisher_buff":
            # Requires a full 5 combo points too (not "whatever's banked"): with only Backstab
            # as a builder, CP income is slow enough that a looser threshold made this refresh
            # trivially true at 1 CP the instant the fight starts (never-applied reads as
            # "expired"), which starved Eviscerate out of ever firing. Real rogues do
            # prioritize Slice and Dice uptime over Eviscerate when Energy-limited, so it's
            # correct that this still wins most contests -- just not for free at 1 CP.
            return self.combo_points >= 5 and t > self.buff_ends.get(aid, -1.0)
        if kind == "maintain_dot":
            return t > self.dot_ends.get(aid, -1.0) - self.lockout(aid)
        if kind == "maintain_buff":
            return t > self.buff_ends.get(aid, -1.0) - self.lockout(aid)
        if kind == "dodge_proc":
            return t <= self.dodge_window_until
        if kind in ("on_cooldown", "filler", "judgement_release"):
            return True
        return False

    def next_action(self, t):
        """The first rotation rule (in priority order) whose condition holds right now,
        or None if nothing applies at all (e.g. every DoT is up and everything else is on
        cooldown) -- that's a real idle moment, not a resource wait."""
        for rule in self.profile["rotation"]:
            if self.rule_condition(rule["ability"], rule["kind"], t):
                return rule["ability"], rule["kind"]
        return None

    def do_cast(self, aid, kind, t):
        if kind == "once":
            self.once_used.add(aid)
        self.pay_cost(aid)
        if kind == "swing_enhancer":
            # No separate hit roll: the enhancement isn't independently resisted, the swing it
            # attaches to (with its own hit/dodge/glance roll) determines whether it lands.
            self.apply_effects(aid, t)
        else:
            hit = roll(self.stats["hit"])
            cp_used = self.combo_points if kind in ("finisher_damage", "finisher_buff", "finisher_dot") else None
            if hit:
                if kind == "judgement_release":
                    self.handle_judgement(aid, t)
                else:
                    self.apply_effects(aid, t, combo_points_used=cp_used)
                if kind == "maintain_buff":
                    self.active_seal = aid
            if kind in ("finisher_damage", "finisher_buff", "finisher_dot"):
                self.combo_points = 0
        lock = self.lockout(aid)
        if lock > 0:
            self.gcd_ready = t + lock
        cd_override = self.talent_mod(aid).get("cooldown_override")
        cd = cd_override if cd_override is not None else self.abilities[aid].get("cooldown_sec")
        if cd:
            self.cooldowns[aid] = t + cd
            group = self.abilities[aid].get("cooldown_group")
            if group:
                self.cooldowns[f"group:{group}"] = t + cd

    def do_pet_swing(self, t):
        """See PET_AP_RATIO_OF_HUNTER_RANGED_AP's comment for the sourcing/approximation this
        relies on. Independent of the hunter's own weapon-swing/dual-wield machinery: a pet has
        its own attack table (own hit/crit rolls, though drawn from the SAME sourced-inherited
        chances) and isn't subject to the hunter's own dual-wield hit penalty."""
        is_crit = False
        if roll(self.stats["hit"]):
            is_crit = roll(self.stats["crit"])
            pet_ap = self.stats["ap"] * PET_AP_RATIO_OF_HUNTER_RANGED_AP
            dmg = (pet_ap / 14) * PET_ATTACK_SPEED_SEC * (2.0 if is_crit else 1.0)
            self.add_dmg(dmg, "hunter_pet")
        self.push(t + PET_ATTACK_SPEED_SEC, "pet_swing")

    def run(self):
        weapons = self.profile.get("weapons", [])
        for i, wpn in enumerate(weapons):
            self.push(wpn["speed"], "swing", {"idx": i})
        if self.profile.get("pet"):
            self.push(0.0, "pet_swing")
        self.push(0.0, "decision")
        last_t = 0.0
        while self.events:
            t, _, kind, data = heapq.heappop(self.events)
            if t > self.fight_len:
                continue
            if self.profile["resource"] == "energy":
                self.gain_energy(t - last_t)
            last_t = t
            self._now = t
            if kind == "swing":
                self.do_swing(t, data["idx"])
            elif kind == "pet_swing":
                self.do_pet_swing(t)
            elif kind == "dot_tick":
                aid = data["aid"]
                # Only the CURRENT epoch's chain keeps ticking -- a chain from a superseded
                # application (see apply_effects' periodic_damage branch) silently stops here
                # instead of continuing to fire in parallel with the new one.
                if data.get("epoch") == self.dot_epoch.get(aid) and t <= self.dot_ends.get(aid, -1.0):
                    is_crit = roll(self.stats["crit"])
                    self.add_dmg(data["per_tick"] * (2.0 if is_crit else 1.0), aid, is_tick=True)
                    self.push(t + data["interval"], "dot_tick", data)
            else:  # decision point
                if t < self.gcd_ready:
                    self.push(self.gcd_ready, "decision")
                    continue
                action = self.next_action(t)
                if action is None:
                    # Nothing in the whole priority list applies right now (every DoT/buff
                    # up, everything else on cooldown): a real idle moment.
                    self.push(self._next_wakeup(t), "decision")
                    continue
                aid, kind = action
                if self.has_resource(aid):
                    self.do_cast(aid, kind, t)
                    self.push(max(t, self.gcd_ready), "decision")
                else:
                    # Top-priority action is valid but not affordable yet: wait for
                    # resource rather than downgrading to a lower-priority rule.
                    self.push(self._next_wakeup(t), "decision")
        return self.total_dmg, self.dmg_by

    def _next_wakeup(self, t):
        """Earliest time anything the priority list cares about could newly become valid: the
        next auto-attack swing, any ability/cooldown-group clearing, or any maintained DoT/buff
        crossing its own refresh threshold (dot_ends/buff_ends minus that ability's own lockout,
        matching rule_condition's maintain_dot/maintain_buff check). Real bug found 2026-09-26
        (user-flagged): this used to only look at the next swing (or a blind t+0.5 poll for
        casters with no weapon), so when nothing was scheduled to swing before a cooldown-group
        actually cleared, idle time silently overshot past the real availability moment -- e.g.
        Enhancement Shaman's Earth Shock/Flame Shock alternation drifting to ~7.8s gaps instead
        of the real 6s Shock-cooldown cadence."""
        candidates = []
        next_swing = min(self._next_swing_times(), default=None)
        if next_swing and next_swing > t:
            candidates.append(next_swing)
        for cd_time in self.cooldowns.values():
            if cd_time > t:
                candidates.append(cd_time)
        for aid, end in self.dot_ends.items():
            if aid in self.abilities:
                wake = end - self.lockout(aid)
                if wake > t:
                    candidates.append(wake)
        for aid, end in self.buff_ends.items():
            if aid in self.abilities:
                wake = end - self.lockout(aid)
                if wake > t:
                    candidates.append(wake)
        return min(candidates) if candidates else t + 0.5

    def _next_swing_times(self):
        return [time for (time, _, kind, _) in self.events if kind == "swing"]


# ---- per-class profiles: resource, weapons, and the sourced rotation priority --------------
# Every "ability" id below is real, sourced weapon/spell data from data/wow_spells/<class>.json.
# Every rotation ORDER is taken from that same ability's own "notes" field (Icy Veins' real
# level-20 single-target priority) -- see the docstring at the top of this file for what's
# deliberately excluded (pets, wands, mana regen, utility buffs, extra talent sliders).

ROTATIONS = {
    "warrior_fury": {
        "glossary": "warrior",  # multiple specs can share one class glossary file
        "resource": "rage",
        "role": "dps",
        "weapons": [{"dmg": 25, "speed": 2.6}, {"dmg": 18, "speed": 1.8, "offhand": True}],
        "rotation": [
            {"ability": "warrior_overpower", "kind": "dodge_proc"},       # notes: "usable for a few seconds after the CURRENT target dodges"
            {"ability": "warrior_rend", "kind": "maintain_dot"},          # notes: real bleed, "Periodic Can Crit"
        ],
    },
    "warrior_arms": {
        "glossary": "warrior",
        "resource": "rage",
        "role": "dps",
        # Real, sourced finding: Icy Veins' Arms guide spends its 11 points identically to Fury
        # (all in the Fury tree -- Arms' own deeper talents aren't reachable at level 20). The
        # two real differences are the weapon (Arms uses one two-handed weapon, no off-hand) and
        # Slam, which only Arms' own rotation text includes (see warrior_slam's notes).
        "weapons": [{"dmg": 42, "speed": 3.3}],
        "rotation": [
            {"ability": "warrior_overpower", "kind": "dodge_proc"},
            {"ability": "warrior_rend", "kind": "maintain_dot"},
            {"ability": "warrior_slam", "kind": "filler"},   # notes: "Slam right after an auto-attack"
        ],
    },
    "warrior_protection": {
        "glossary": "warrior", "resource": "rage", "role": "tank",
        # Real, sourced finding: Protection's own single-target priority (Icy Veins) does NOT
        # include Rend or Overpower at all (Overpower needs Battle Stance, which the guide says
        # Protection only visits briefly to Charge in). The two abilities it DOES name -- Revenge
        # (procs off the player successfully Block/Dodge/Parry-ing an incoming attack) and Sunder
        # Armor (no direct-damage effect of its own) -- aren't simulable here: this engine has no
        # incoming-damage/attack-table-against-the-player model, so a defensive proc can't fire.
        # Left as auto-attack only with a smaller one-handed weapon (paired with a shield, no
        # off-hand) -- an honestly low number, consistent with a tank not being built for damage.
        "weapons": [{"dmg": 18, "speed": 2.6}],
        "rotation": [],
    },
    # All 3 Rogue specs share the exact same real sustained single-target core rotation per
    # their own guides (build combo points with Backstab/Sinister Strike, spend at 5 CP on
    # Eviscerate/Slice and Dice) -- their real differences are talents, a one-time stealth
    # opener (Ambush) and poisons, none of which this engine models yet (see rogue.json's own
    # gaps). All three therefore intentionally produce the same simulated number right now.
    "rogue_combat": {
        "glossary": "rogue", "resource": "energy", "role": "dps",
        "weapons": [{"dmg": 25, "speed": 2.6}, {"dmg": 18, "speed": 1.8, "offhand": True}],
        "rotation": [
            {"ability": "rogue_eviscerate", "kind": "finisher_damage"},     # dumped at 5 combo points
            {"ability": "rogue_slice_and_dice", "kind": "finisher_buff"},   # re-applied only once it's fully dropped, using whatever CP is banked
            {"ability": "rogue_backstab", "kind": "builder"},               # notes: "priority (Icy Veins) uses this over Sinister Strike"
            {"ability": "rogue_sinister_strike", "kind": "builder"},
        ],
    },
    "rogue_assassination": {
        "glossary": "rogue", "resource": "energy", "role": "dps",
        "weapons": [{"dmg": 25, "speed": 2.6}, {"dmg": 18, "speed": 1.8, "offhand": True}],
        "rotation": [
            {"ability": "rogue_eviscerate", "kind": "finisher_damage"},
            {"ability": "rogue_slice_and_dice", "kind": "finisher_buff"},
            {"ability": "rogue_backstab", "kind": "builder"},
            {"ability": "rogue_sinister_strike", "kind": "builder"},
        ],
    },
    "rogue_subtlety": {
        "glossary": "rogue", "resource": "energy", "role": "dps",
        "weapons": [{"dmg": 25, "speed": 2.6}, {"dmg": 18, "speed": 1.8, "offhand": True}],
        "rotation": [
            {"ability": "rogue_eviscerate", "kind": "finisher_damage"},
            {"ability": "rogue_slice_and_dice", "kind": "finisher_buff"},
            {"ability": "rogue_backstab", "kind": "builder"},
            {"ability": "rogue_sinister_strike", "kind": "builder"},
        ],
    },
    "paladin_retribution": {
        "glossary": "paladin", "resource": "mana", "role": "dps",
        "weapons": [{"dmg": 30, "speed": 2.9}],
        "seal_ability": "paladin_seal_of_righteousness",
        "rotation": [
            {"ability": "paladin_seal_of_righteousness", "kind": "maintain_buff"},  # notes: "the default Seal to keep active"
            {"ability": "paladin_holy_strike", "kind": "on_cooldown"},              # notes: "use on cooldown alongside Judgement"
            {"ability": "paladin_judgement", "kind": "judgement_release"},
        ],
    },
    "paladin_protection": {
        "glossary": "paladin", "resource": "mana", "role": "tank",
        # Real, sourced priority: Consecration on cooldown > Seal of Fury > Judgement (taunts,
        # no own damage) > Holy Strike. Seal of Fury's own real damage numbers weren't found this
        # pass (see paladin.json's gaps), so it's omitted rather than invented -- Judgement then
        # has nothing to release and contributes no simulated damage, same as any spec with no
        # damage-dealing Seal active. Single one-handed weapon + shield, no off-hand.
        "weapons": [{"dmg": 18, "speed": 2.6}],
        "rotation": [
            {"ability": "paladin_consecration", "kind": "maintain_dot"},
            {"ability": "paladin_holy_strike", "kind": "on_cooldown"},
        ],
    },
    "shaman_enhancement": {
        "glossary": "shaman", "resource": "mana", "role": "dps",
        "weapons": [{"dmg": 28, "speed": 2.6}],
        # Real-game correction (2026-09-26, user-flagged): a Shaman's spellbook isn't restricted
        # to whichever tree got the talent points -- min_level 10 and untalented ("trees": [])
        # per shaman_flame_shock's own glossary entry, so it's just as real and castable for
        # Enhancement as for Elemental. Icy Veins' own Enhancement guide doesn't mention it (its
        # priority text is Earth Shock-only), but the ability itself is sourced and legitimately
        # available, so it's included per real class mechanics rather than left out. Searing Totem
        # (also user-flagged) is sourced now too -- a real, independent damage source (doesn't
        # share the Shock cooldown group), dropped once and left ticking for its 30s duration.
        # Still missing (real gap, not sourced in this glossary yet): Strength of Earth Totem (the
        # stat-buff totem the user describes dropping at pull) -- a pure stat buff with no damage
        # of its own, so it wouldn't show up as a DPS line even once sourced; needs fresh Wowhead
        # data before it can be folded into the BIS stat calc instead.
        "rotation": [
            {"ability": "shaman_searing_totem", "kind": "maintain_dot"},
            {"ability": "shaman_flame_shock", "kind": "maintain_dot"},
            {"ability": "shaman_earth_shock", "kind": "on_cooldown"},
        ],
    },
    "shaman_elemental": {
        "glossary": "shaman", "resource": "mana", "role": "dps",
        # Real, sourced finding: Elemental's own headline talents (Lava Burst, Elemental
        # Alacrity) aren't reachable at level 20 -- the guide calls them "a preview of sorts for
        # what is to come." The real usable rotation is just Lightning Bolt + maintained Flame
        # Shock. Pure caster, no auto-attack weapon.
        "weapons": [],
        "rotation": [
            {"ability": "shaman_flame_shock", "kind": "maintain_dot"},  # notes: applied right after the Lightning Bolt pull
            {"ability": "shaman_lightning_bolt", "kind": "filler"},
        ],
    },
    "mage_fire": {
        "glossary": "mage", "resource": "mana", "role": "dps",
        "weapons": [],
        # Real, sourced talent (2026-09-26): Wake of Fire 2/2 (Fire-tree only, per
        # data/wow_talents/mage.json) reduces Fire Blast's cooldown by 2s at full rank --
        # confirmed at rank 2/2 in mage_fire_blast's own glossary note ("Base cooldown is 8s;
        # Wake of Fire (talented) reduces this to 6s"). The talent's other effect (+25-50% crit
        # on the next Fire Blast after a kill) is a leveling-only proc that can't fire in a
        # continuous single-boss fight -- same out-of-scope reasoning as Victory Rush -- so it's
        # not modeled.
        "talent_mods": {
            "mage_fire_blast": {"cooldown_override": 6.0},
        },
        "rotation": [
            {"ability": "mage_pyroblast", "kind": "once"},        # notes: "Single-Target Rotation opener"
            {"ability": "mage_fire_blast", "kind": "on_cooldown"},
            {"ability": "mage_fireball", "kind": "filler"},
        ],
    },
    # Real, sourced finding: neither Arcane's nor Frost's own headline level-20 rotation is
    # actually usable at level 20 (Missile Barrage needs level 24; Ice Lance needs level 28
    # despite the guide's own talents already investing toward it) -- see mage.json's gaps.
    # Both specs' real castable kit reduces to Frostbolt (a shared base spell, not tree-locked).
    "mage_arcane": {
        "glossary": "mage", "resource": "mana", "role": "dps",
        "weapons": [],
        "rotation": [
            {"ability": "mage_frostbolt", "kind": "filler"},
        ],
    },
    "mage_frost": {
        "glossary": "mage", "resource": "mana", "role": "dps",
        "weapons": [],
        "rotation": [
            {"ability": "mage_frostbolt", "kind": "filler"},
        ],
    },
    "priest_shadow": {
        "glossary": "priest", "resource": "mana", "role": "dps",
        "weapons": [],
        "rotation": [
            {"ability": "priest_mind_blast", "kind": "on_cooldown"},          # notes: cast right after the opener, before SW:P
            {"ability": "priest_shadow_word_pain", "kind": "maintain_dot"},
            {"ability": "priest_smite", "kind": "filler"},                    # real Holy-school opener/filler at level 20
        ],
    },
    "druid_balance": {
        "glossary": "druid", "resource": "mana", "role": "dps",
        "weapons": [],
        "rotation": [
            {"ability": "druid_moonfire", "kind": "maintain_dot"},  # notes: "keep this active on the target at all times, ahead of Wrath"
            {"ability": "druid_wrath", "kind": "filler"},
        ],
    },
    "druid_feral": {
        "glossary": "druid", "resource": "energy", "role": "dps",
        # Cat Form DPS build. Real, sourced finding: the level-20 kit is genuinely thin (Wowhead's
        # own guide: "only having two damage abilities in Claw and Rip"). Single weapon (fist
        # weapons/daggers in Cat Form don't dual-wield).
        "weapons": [{"dmg": 20, "speed": 1.0}],
        "rotation": [
            {"ability": "druid_rip", "kind": "finisher_dot"},   # Wowhead's own threshold: 4+ combo points
            {"ability": "druid_claw", "kind": "builder"},
        ],
    },
    "druid_feral_tank": {
        "glossary": "druid", "resource": "rage", "role": "tank",
        # Bear Form tank build -- same Feral Combat talents as the Cat DPS build (Icy Veins: "the
        # only spec that buffs both Tanking and DPS"). Real sourced rotation: Maul as the single-
        # target Rage dump (Enrage's own numbers weren't found this pass, see druid.json gaps).
        "weapons": [{"dmg": 22, "speed": 2.5}],
        "rotation": [
            {"ability": "druid_maul", "kind": "swing_enhancer"},
        ],
    },
    "warlock_affliction": {
        "glossary": "warlock", "resource": "mana", "role": "dps",
        "weapons": [],
        # Real, sourced talent (2026-09-26): Improved Corruption 5/5 is confirmed in Affliction's
        # own real build (data/wow_talents/warlock.json), and its exact rank-5 tooltip is "Reduces
        # the casting time of your Corruption spell by 2 sec and increases the damage it deals by
        # 10%" -- i.e. Corruption's 2s base cast becomes instant, +10% damage. NOT applied to
        # Demonology/Destruction below: neither spec's own real build in that same talents file
        # takes this talent (checked directly, not assumed).
        "talent_mods": {
            "warlock_corruption": {"cast_time_override": 0.0, "damage_mult": 1.10},
        },
        "rotation": [
            {"ability": "warlock_immolate", "kind": "maintain_dot"},   # notes: "the first DoT applied, before Corruption"
            {"ability": "warlock_corruption", "kind": "maintain_dot"},
        ],
    },
    # Real, sourced finding: Demonology's own level-20 rotation uses the exact same two DoTs as
    # Affliction (its real difference is talents/demon damage, neither modeled generically here),
    # so it intentionally produces the same number. Destruction's own guide names Shadow Bolt as
    # its primary filler, unlike Affliction -- a genuine per-spec difference, not a duplicate.
    "warlock_demonology": {
        "glossary": "warlock", "resource": "mana", "role": "dps",
        "weapons": [],
        "rotation": [
            {"ability": "warlock_immolate", "kind": "maintain_dot"},
            {"ability": "warlock_corruption", "kind": "maintain_dot"},
        ],
    },
    "warlock_destruction": {
        "glossary": "warlock", "resource": "mana", "role": "dps",
        "weapons": [],
        "rotation": [
            {"ability": "warlock_immolate", "kind": "maintain_dot"},
            {"ability": "warlock_corruption", "kind": "maintain_dot"},
            {"ability": "warlock_shadow_bolt", "kind": "filler"},  # notes: "primary direct-damage filler" (Destruction only)
        ],
    },
    # Real, sourced finding: all 3 Hunter specs converge on the exact same real level-20 ranged
    # rotation (Serpent Sting > Aimed Shot on cooldown > Auto Shot > Arcane Shot filler) --
    # Survival's own guide states outright "regardless of what talents you choose, this is the
    # optimal choice" at level 20. Spec choice is about talents/pet, not the rotation, so all 3
    # intentionally produce the same simulated number here.
    #
    # 2026-09-26 (user-flagged): Auto Shot is now modeled -- real BIS ranged weapon (Venomstrike,
    # data/wow_items/bis_gear_by_slot.json, Wowhead item=6469: 20-38 dmg, 2.40s speed, midpoint 29
    # used) reused as this profile's "weapons" entry. self.stats["ap"] is already the Hunter's
    # RANGED Attack Power (SPEC_STAT_PROFILE sets agi_ap="ranged"), so the existing melee-swing
    # machinery (avg_hit/do_swing) correctly doubles as the ranged auto-attack here -- no new
    # engine code needed, just real weapon data. This also fixes a second, previously-unnoticed
    # gap: Aimed Shot is a normalized_weapon_damage ability (100% weapon dmg + 20 flat) that was
    # silently scoring ZERO on its weapon-damage component this whole time, since avg_hit()
    # returns 0.0 with an empty weapons list -- it was only ever dealing its +20 flat bonus.
    # Venomstrike's own "Chance on hit: Venom Shot for 23-33 Nature damage" proc isn't modeled
    # (same class of omission as other on-hit procs already disclosed elsewhere).
    "hunter_marksmanship": {
        "glossary": "hunter", "resource": "mana", "role": "dps",
        "weapons": [{"dmg": 29, "speed": 2.40}],
        "pet": True,  # see PET_AP_RATIO_OF_HUNTER_RANGED_AP's comment above for sourcing/caveats
        "rotation": [
            {"ability": "hunter_serpent_sting", "kind": "maintain_dot"},  # notes: "cast once the pet has engaged, before Aimed Shot"
            {"ability": "hunter_aimed_shot", "kind": "on_cooldown"},
            {"ability": "hunter_arcane_shot", "kind": "on_cooldown"},
        ],
    },
    "hunter_beast_mastery": {
        "glossary": "hunter", "resource": "mana", "role": "dps",
        "weapons": [{"dmg": 29, "speed": 2.40}],
        "pet": True,
        "rotation": [
            {"ability": "hunter_serpent_sting", "kind": "maintain_dot"},
            {"ability": "hunter_aimed_shot", "kind": "on_cooldown"},
            {"ability": "hunter_arcane_shot", "kind": "on_cooldown"},
        ],
    },
    "hunter_survival": {
        "glossary": "hunter", "resource": "mana", "role": "dps",
        "weapons": [{"dmg": 29, "speed": 2.40}],
        "pet": True,
        "rotation": [
            {"ability": "hunter_serpent_sting", "kind": "maintain_dot"},
            {"ability": "hunter_aimed_shot", "kind": "on_cooldown"},
            {"ability": "hunter_arcane_shot", "kind": "on_cooldown"},
        ],
    },
}

# Fallback only -- used if a spec has no entry in data/wow_items/bis_level20_stats.json.
# Every spec in ROTATIONS has real BIS data now (see bis_stats_for_spec below), so this
# should never actually fire, but stays as a safety net rather than a crash.
DEFAULT_STATS = {"ap": 150, "sp": 90, "hit": 0.90, "crit": 0.15}

_BIS_DATA = None


def _load_bis_data():
    global _BIS_DATA
    if _BIS_DATA is None:
        path = wow_spells.ROOT / "data" / "wow_items" / "bis_level20_stats.json"
        _BIS_DATA = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return _BIS_DATA


# Per-spec metadata the raw bis_level20_stats.json doesn't itself encode: which crit formula
# applies (physical, off Agility -- vs spell, off Intellect), which Agility->AP coefficient to
# use (None for classes with no Agi->AP conversion, "melee" for Rogue/Feral Druid, "ranged" for
# Hunter, whose real damage-relevant AP comes from the 2-per-Agi ranged coefficient, not the
# 1-per-Agi melee one), and which damage school's extra Spell Power (if any was itemized on the
# BIS list) actually matters for that spec's own nukes.
SPEC_STAT_PROFILE = {
    "warrior_fury": {"crit": "physical"}, "warrior_arms": {"crit": "physical"}, "warrior_protection": {"crit": "physical"},
    "rogue_combat": {"crit": "physical", "agi_ap": "melee"}, "rogue_assassination": {"crit": "physical", "agi_ap": "melee"}, "rogue_subtlety": {"crit": "physical", "agi_ap": "melee"},
    "paladin_retribution": {"crit": "physical"}, "paladin_protection": {"crit": "physical"},
    "shaman_enhancement": {"crit": "physical"}, "shaman_elemental": {"crit": "spell"},
    "mage_fire": {"crit": "spell", "school": "fire"}, "mage_arcane": {"crit": "spell", "school": "arcane"}, "mage_frost": {"crit": "spell", "school": "frost"},
    "priest_shadow": {"crit": "spell", "school": "shadow"},
    "druid_balance": {"crit": "spell", "school": "arcane"}, "druid_feral": {"crit": "physical", "agi_ap": "melee"}, "druid_feral_tank": {"crit": "physical", "agi_ap": "melee"},
    "warlock_affliction": {"crit": "spell", "school": "shadow"}, "warlock_demonology": {"crit": "spell", "school": "shadow"}, "warlock_destruction": {"crit": "spell", "school": "shadow"},
    "hunter_marksmanship": {"crit": "physical", "agi_ap": "ranged"}, "hunter_beast_mastery": {"crit": "physical", "agi_ap": "ranged"}, "hunter_survival": {"crit": "physical", "agi_ap": "ranged"},
}


def stat_deltas_from_raw(spec_id, str_=0, agi=0, int_=0, flat_ap=0, flat_sp=0, flat_crit_pct=0, flat_hit_pct=0):
    """The MARGINAL {ap, sp, crit_pct, hit_pct} contribution of a raw stat block -- no base
    character constants (base melee/spell crit%, base hit%) added. Used to convert either one
    item's own stats (wow_bis_optimizer.py, 2026-09-26) or a full aggregate's stats
    (stats_from_raw below) into DPS-relevant terms with the same real Classic conversion ratios
    (data/wow_items/bis_level20_stats.json). Returns None if spec_id/class_id isn't in the
    conversion tables."""
    profile = ROTATIONS.get(spec_id)
    if not profile:
        return None
    bis = _load_bis_data()
    class_id = profile.get("glossary", spec_id)
    ratios = bis["conversion_ratios"]
    meta = SPEC_STAT_PROFILE.get(spec_id, {})

    agi_ap_mode = meta.get("agi_ap")
    # Real Classic mechanic: a Hunter's RANGED Attack Power pool (used for Auto Shot/Aimed Shot,
    # this sim's only Hunter abilities) is base + 2*Agi ONLY -- it does not include a Strength
    # component the way melee AP does. Skipping the str_*ap_per_str term for agi_ap=="ranged"
    # specs (2026-09-26, found while wiring Auto Shot) avoids silently inflating ranged AP with a
    # melee-only conversion that real Hunters don't get on their ranged attacks.
    ap = flat_ap if agi_ap_mode == "ranged" else flat_ap + str_ * ratios["ap_per_str"].get(class_id, 0)
    if agi_ap_mode == "ranged":
        ap += agi * ratios["ap_per_agi_ranged"].get(class_id, 0)
    elif agi_ap_mode == "melee":
        # Druids only get melee AP from Agility in Cat Form, stored under its own "druid_cat" key
        # (fixed 2026-09-26: looking it up as "druid" silently gave Feral 0 AP per Agility).
        agi_key = "druid_cat" if spec_id == "druid_feral" else class_id
        ap += agi * ratios["ap_per_agi_melee"].get(agi_key, 0)

    if meta.get("crit") == "spell":
        crit_pct = int_ / ratios["spell_crit_pct_per_int"].get(class_id, 99999) + flat_crit_pct
    else:
        crit_pct = agi / ratios["crit_pct_per_agi"].get(class_id, 99999) + flat_crit_pct

    return {"ap": ap, "sp": flat_sp, "crit_pct": crit_pct, "hit_pct": flat_hit_pct}


def stats_from_raw(spec_id, str_=0, agi=0, int_=0, flat_ap=0, flat_sp=0, flat_crit_pct=0, flat_hit_pct=0):
    """Turns a raw Str/Agi/Int + flat AP/SP/Crit/Hit stat block into the {ap, sp, hit, crit}
    shape run_class() needs: stat_deltas_from_raw()'s marginal contribution PLUS this spec's
    base (no-gear) Crit%/Hit% constants, also cited in data/wow_items/bis_level20_stats.json.
    This is the shared math bis_stats_for_spec() (the aggregate BIS path) and
    wow_bis_optimizer.py (2026-09-26, the engine-driven BIS optimizer's final-loadout path) both
    call, so the two can never drift apart. Returns None if spec_id/class_id isn't in the
    conversion tables."""
    profile = ROTATIONS.get(spec_id)
    if not profile:
        return None
    bis = _load_bis_data()
    class_id = profile.get("glossary", spec_id)
    base_ch = bis["base_crit_hit"]
    meta = SPEC_STAT_PROFILE.get(spec_id, {})
    deltas = stat_deltas_from_raw(spec_id, str_, agi, int_, flat_ap, flat_sp, flat_crit_pct, flat_hit_pct)

    if meta.get("crit") == "spell":
        base_crit = base_ch["base_spell_crit_pct"].get(class_id, 0)
        base_hit_pct = 97  # equal-level spell miss baseline, Wowhead Classic "Stats and Attributes" guide
    else:
        base_crit = base_ch["base_melee_crit_pct"].get(class_id, 0)
        base_hit_pct = 95  # equal-level melee/ranged miss baseline, same source
    crit_pct = base_crit + deltas["crit_pct"]
    hit_pct = base_hit_pct + deltas["hit_pct"]

    return {"ap": round(deltas["ap"], 1), "sp": round(deltas["sp"], 1), "hit": round(hit_pct / 100.0, 4), "crit": round(crit_pct / 100.0, 4)}


def bis_stats_for_spec(spec_id):
    """Turns the raw sourced gear stats (Str/Agi/Int + flat AP/SP/Crit/Hit from
    data/wow_items/bis_level20_stats.json) into the {ap, sp, hit, crit} shape run_class()
    needs. Returns None if the spec isn't in the BIS data (shouldn't happen -- all 23 are)."""
    bis = _load_bis_data()
    spec_bis = bis.get("specs", {}).get(spec_id)
    if not spec_bis:
        return None
    meta = SPEC_STAT_PROFILE.get(spec_id, {})
    s = spec_bis["stats"]
    sp = spec_bis.get("flat_sp", 0) + spec_bis.get("generic_spell_dmg", 0) + spec_bis.get("school_sp", {}).get(meta.get("school"), 0)
    return stats_from_raw(
        spec_id, str_=s.get("str", 0), agi=s.get("agi", 0), int_=s.get("int", 0),
        flat_ap=spec_bis.get("flat_ap", 0), flat_sp=sp,
        flat_crit_pct=spec_bis.get("flat_crit_pct", 0), flat_hit_pct=spec_bis.get("flat_hit_pct", 0),
    )


def trace_rotation(spec_id, seconds=30.0, stats=None):
    """Runs ONE simulated fight for spec_id with play-by-play tracing on, truncated to the first
    `seconds` of the fight, and returns the list of trace lines (timestamp, ability, damage/miss/
    dodge). For manually eyeballing that the rotation is actually firing what's expected -- not
    used by the site itself."""
    profile = ROTATIONS.get(spec_id)
    if not profile:
        return None
    glossary = wow_spells.load_class(profile.get("glossary", spec_id))
    if not glossary:
        return None
    stats = stats or bis_stats_for_spec(spec_id) or DEFAULT_STATS
    sim = Sim(spec_id, profile, glossary, stats, seconds)
    sim.trace = []
    sim.run()
    return sim.trace


def run_class(cls_id, iterations=300, fight_len=300.0, stats=None, profile_override=None):
    """profile_override lets a caller (wow_bis_optimizer.py) substitute a different "weapons"
    list -- e.g. the real weapon(s) its own search picked -- without touching ROTATIONS itself;
    everything else about the spec (rotation, resource, talent_mods) stays as sourced."""
    profile = profile_override or ROTATIONS.get(cls_id)
    if not profile:
        return None
    glossary = wow_spells.load_class(profile.get("glossary", cls_id))
    if not glossary:
        return None
    stats = stats or bis_stats_for_spec(cls_id) or DEFAULT_STATS
    total = 0.0
    dmg_by_total = {}
    for _ in range(iterations):
        sim = Sim(cls_id, profile, glossary, stats, fight_len)
        dmg, dmg_by = sim.run()
        total += dmg
        for k, v in dmg_by.items():
            dmg_by_total[k] = dmg_by_total.get(k, 0.0) + v
    dps = total / iterations / fight_len
    breakdown = {k: v / iterations / fight_len for k, v in dmg_by_total.items()}
    return dps, breakdown


# Maps each ROTATIONS key to the real spec id used by data/wow_talents/<class>.json's own
# "specs" array and by data/wow_guides/roles.json (both already sourced from Icy Veins/the
# beta client, independent of this file) -- lets build_ranking() below join this engine's
# output onto the site's existing real spec names, icons and guide URLs. Not a 1:1 string
# transform: Druid's Feral tree covers both the cat-DPS and bear-tank builds under a single
# real spec id ("feral-combat"), and Hunter/Druid spec ids use hyphens this file's own keys
# don't.
SPEC_ID_MAP = {
    "warrior_fury": "fury", "warrior_arms": "arms", "warrior_protection": "protection",
    "rogue_combat": "combat", "rogue_assassination": "assassination", "rogue_subtlety": "subtlety",
    "paladin_retribution": "retribution", "paladin_protection": "protection",
    "shaman_enhancement": "enhancement", "shaman_elemental": "elemental",
    "mage_fire": "fire", "mage_arcane": "arcane", "mage_frost": "frost",
    "priest_shadow": "shadow",
    "druid_balance": "balance", "druid_feral": "feral-combat", "druid_feral_tank": "feral-combat",
    "warlock_affliction": "affliction", "warlock_demonology": "demonology", "warlock_destruction": "destruction",
    "hunter_marksmanship": "marksmanship", "hunter_beast_mastery": "beast-mastery", "hunter_survival": "survival",
}


def build_ranking(wt_classes, lang, iterations=300, fight_len=300.0):
    """Runs every spec in ROTATIONS and returns a list of dicts ready for the public ranking
    template, sorted by simulated DPS descending. wt_classes is wow_talents.load()'s class list
    (real class name/icon/color + per-spec real names); data/wow_guides/roles.json supplies each
    spec's real Icy Veins role label and guide URL, both already sourced independently of this
    engine."""
    roles_path = wow_spells.ROOT / "data" / "wow_guides" / "roles.json"
    roles = json.loads(roles_path.read_text(encoding="utf-8")) if roles_path.exists() else {}
    classes_by_id = {c["id"]: c for c in wt_classes}
    rows = []
    for spec_id, profile in ROTATIONS.items():
        result = run_class(spec_id, iterations, fight_len)
        if result is None:
            continue
        dps, breakdown = result
        class_id = profile.get("glossary", spec_id)
        wt_spec_id = SPEC_ID_MAP.get(spec_id)
        cls = classes_by_id.get(class_id)
        spec_name = wt_spec_id
        if cls:
            for s in cls.get("specs", []):
                if s["id"] == wt_spec_id:
                    spec_name = s["name"][lang]
                    break
        role_entry = roles.get(class_id, {}).get(wt_spec_id, {})
        bis_gear = _load_bis_data().get("specs", {}).get(spec_id, {})
        rows.append({
            "spec_id": spec_id,
            "bis_gear": bis_gear,
            "bis_final_stats": bis_stats_for_spec(spec_id),
            "class_id": class_id,
            "class_name": cls["name"][lang] if cls else class_id,
            "class_icon": cls.get("icon") if cls else None,
            "class_color": cls.get("color") if cls else None,
            "spec_name": spec_name,
            "role": profile.get("role", "dps"),
            "dps": dps,
            "breakdown": breakdown,
            # The site's own real per-spec guide page (already built from this same roles.json +
            # wt_classes data) -- link there rather than off-site, since it exists for every spec here.
            "guide_path": f"wow-forever/guides/{class_id}/{wt_spec_id}/" if wt_spec_id else None,
            "icy_veins_url": role_entry.get("url"),
        })
    rows.sort(key=lambda r: r["dps"], reverse=True)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=300)
    parser.add_argument("--fight-len", type=float, default=300.0)
    parser.add_argument("--class", dest="cls", default=None, help="Run one spec only (e.g. warrior_fury)")
    args = parser.parse_args()

    specs = [args.cls] if args.cls else list(ROTATIONS.keys())
    results = []
    for spec_id in specs:
        r = run_class(spec_id, args.iterations, args.fight_len)
        if r is None:
            print(f"{spec_id}: no glossary/rotation profile found, skipped")
            continue
        dps, breakdown = r
        role = ROTATIONS[spec_id].get("role", "dps")
        results.append((spec_id, role, dps, breakdown))

    results.sort(key=lambda r: r[2], reverse=True)
    max_dps = results[0][2] if results else 1.0
    print(f"\nLevel 20 DPS ranking ({args.iterations} fights x {args.fight_len:.0f}s, real level-20 BiS gear per spec)\n")
    for spec_id, role, dps, breakdown in results:
        bar = "#" * max(1, round(40 * dps / max_dps))
        tag = f"[{role}]" if role != "dps" else ""
        print(f"{spec_id:22s} {tag:6s} {dps:6.2f} DPS  {bar}")
        for src, src_dps in sorted(breakdown.items(), key=lambda kv: -kv[1]):
            print(f"                              {src:28s} {src_dps:6.2f} ({100*src_dps/dps:4.1f}%)")
        print()


if __name__ == "__main__":
    main()
