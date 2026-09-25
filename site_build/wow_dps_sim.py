"""Internal, generic level-20 DPS simulator driven by data/wow_spells/<class>.json.

NOT wired into the public site (2026-09-25, user request): built to eventually feed a
cross-spec DPS ranking (a la WarcraftLogs), not to be shown as a public interactive tool.
Run directly: `py site_build/wow_dps_sim.py` (from the project root) prints a DPS ranking
across every class that has a glossary file.

Reuses the same architecture already validated for the Fury Warrior engine
(site_build/js/wow-warrior-sim.js) -- event queue, per-swing hit/crit RNG, non-stacking
DoT/buff refresh, per-source damage breakdown -- but generalized to read ability cost,
cooldown, cast time and damage formulas straight from each class's own glossary instead of
hardcoding class-specific numbers. Only the ROTATION PRIORITY per class stays hand-written
below (ROTATIONS), because it's real game knowledge that isn't part of the glossary schema
-- exactly like the Warrior engine's own rotation choice. Every entry cites the sourced
priority note (in that class's own data/wow_spells/<class>.json) that justifies it.

Deliberately not modeled, matching what each class's own glossary already discloses as a
gap: pet damage (Hunter, Warlock), Hunter's Auto Shot itself (no sourced ranged-weapon
damage), wand damage (Mage/Priest/Warlock), Mana regeneration or depletion (no sourced
regen rate for any class -- Mana is treated as unconstrained: this measures "is the
rotation's damage output," not "for how long it can be sustained"), long-duration
low-maintenance self-buffs that aren't really part of the active rotation (Battle Shout,
Rockbiter Weapon -- their stat bonus belongs in your own stat input, not a scripted cast),
and the extra talent-rank sliders the bespoke Warrior tool exposes (Cruelty, Precision,
Flurry, Unbridled Wrath, Dual Wield Specialization, Boundless Rage) -- those aren't sourced
for the other 8 classes yet, so this generic pass compares base rotations on equal stats,
not fully talented character sheets.
"""
import argparse
import heapq
import random

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


def rage_conversion_value(level):
    """Real classic-WoW formula (see wow-warrior-sim.js for the full citation and derivation)."""
    return 0.0091107836 * level * level + 3.225598133 * level + 4.2652911


RAGE_CONVERSION_L20 = rage_conversion_value(20)


def roll(chance):
    return random.random() < chance


def parse_cast_time(raw):
    """"instant" -> 0.0, "3 sec" -> 3.0. Anything else (e.g. Heroic Strike's "on next melee
    swing", unused by any class modeled here) -> 0.0, since no glossary ability used here
    needs it."""
    if not raw or raw == "instant":
        return 0.0
    if raw.endswith(" sec"):
        try:
            return float(raw.split(" ")[0])
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
    """avg_hit is one full white-swing's worth of damage (weapon + AP/14), consistent with
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
        self.buff_ends = {}
        self.once_used = set()
        self.dodge_window_until = -1.0
        self.active_seal = None
        self.swing_speed_mult = 1.0
        self.dmg_by = {}
        self.total_dmg = 0.0

    def push(self, time, kind, data=None):
        if time > self.fight_len:
            return
        self.seq += 1
        heapq.heappush(self.events, (time, self.seq, kind, data))

    def add_dmg(self, amount, tag):
        self.total_dmg += amount
        self.dmg_by[tag] = self.dmg_by.get(tag, 0.0) + amount

    def avg_hit(self, idx=0):
        weapons = self.profile.get("weapons", [])
        if not weapons:
            return 0.0
        return weapons[idx]["dmg"] + self.stats["ap"] / 14

    def off_cooldown(self, aid, t):
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

    def lockout(self, aid):
        ab = self.abilities[aid]
        return max(parse_cast_time(ab.get("cast_time")), ab.get("gcd_sec", 1.5) or 0)

    def apply_effects(self, aid, t, combo_points_used=None):
        ab = self.abilities[aid]
        sp, crit_frac = self.stats["sp"], self.stats["crit"]
        for eff in ab.get("effects", []):
            kind = eff["kind"]
            if kind == "direct_damage":
                dmg, _ = resolve_direct_damage(eff, self.stats["ap"], sp, crit_frac)
                self.add_dmg(dmg, aid)
            elif kind == "normalized_weapon_damage":
                dmg, _ = resolve_normalized_weapon_damage(eff, self.avg_hit(0), sp, crit_frac)
                self.add_dmg(dmg, aid)
            elif kind == "periodic_damage":
                duration, interval, per_tick, _ = resolve_periodic_setup(eff, sp)
                was_active = t <= self.dot_ends.get(aid, -1.0)
                self.dot_ends[aid] = t + duration
                if not was_active:
                    self.push(t + interval, "dot_tick", {"aid": aid, "interval": interval, "per_tick": per_tick})
            elif kind == "resource_generation" and eff.get("resource") == "combo_points":
                self.combo_points = min(5, self.combo_points + eff.get("immediate", 0))
            elif kind == "combo_point_scaling":
                cp = max(1, min(5, combo_points_used or self.combo_points))
                if "table" in eff:
                    dmg, _ = resolve_combo_point_table(eff, cp, crit_frac)
                    self.add_dmg(dmg, aid)
                elif "base" in eff:
                    self.buff_ends[aid] = t + eff["base"] + eff["per_point"] * cp
                    self.swing_speed_mult = SND_HASTE_MULT
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
            pass  # miss
        elif roll(DODGE_CHANCE):
            self.dodge_window_until = t + OVERPOWER_WINDOW
        else:
            is_glance = roll(GLANCE_CHANCE)
            is_crit = (not is_glance) and roll(self.stats["crit"])
            base = wpn["dmg"] + self.stats["ap"] / 14
            if is_oh:
                base *= 0.5
            seal_id = self.profile.get("seal_ability")
            if seal_id and t <= self.buff_ends.get(seal_id, -1.0) and not is_oh:
                seal = self.abilities.get(seal_id, {})
                for eff in seal.get("effects", []):
                    if eff.get("kind") == "self_buff" and "per_swing_bonus_dmg_range" in eff:
                        base += random.uniform(*eff["per_swing_bonus_dmg_range"])
            mult = GLANCE_DAMAGE_MULT if is_glance else (2.0 if is_crit else 1.0)
            dmg = base * mult
            self.add_dmg(dmg, "white")
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
        hit = roll(self.stats["hit"])
        cp_used = self.combo_points if kind in ("finisher_damage", "finisher_buff") else None
        if hit:
            if kind == "judgement_release":
                self.handle_judgement(aid, t)
            else:
                self.apply_effects(aid, t, combo_points_used=cp_used)
            if kind == "maintain_buff":
                self.active_seal = aid
        if kind in ("finisher_damage", "finisher_buff"):
            self.combo_points = 0
        lock = self.lockout(aid)
        if lock > 0:
            self.gcd_ready = t + lock
        cd = self.abilities[aid].get("cooldown_sec")
        if cd:
            self.cooldowns[aid] = t + cd

    def run(self):
        weapons = self.profile.get("weapons", [])
        for i, wpn in enumerate(weapons):
            self.push(wpn["speed"], "swing", {"idx": i})
        self.push(0.0, "decision")
        last_t = 0.0
        while self.events:
            t, _, kind, data = heapq.heappop(self.events)
            if t > self.fight_len:
                continue
            if self.profile["resource"] == "energy":
                self.gain_energy(t - last_t)
            last_t = t
            if kind == "swing":
                self.do_swing(t, data["idx"])
            elif kind == "dot_tick":
                aid = data["aid"]
                if t <= self.dot_ends.get(aid, -1.0):
                    is_crit = roll(self.stats["crit"])
                    self.add_dmg(data["per_tick"] * (2.0 if is_crit else 1.0), aid)
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
        next_swing = min(self._next_swing_times(), default=None)
        if next_swing and next_swing > t:
            return next_swing
        return t + 0.5

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
    "shaman_enhancement": {
        "glossary": "shaman", "resource": "mana", "role": "dps",
        "weapons": [{"dmg": 28, "speed": 2.6}],
        "rotation": [
            {"ability": "shaman_earth_shock", "kind": "on_cooldown"},  # the only rotational damage spell this glossary sources
        ],
    },
    "mage_fire": {
        "glossary": "mage", "resource": "mana", "role": "dps",
        "weapons": [],
        "rotation": [
            {"ability": "mage_pyroblast", "kind": "once"},        # notes: "Single-Target Rotation opener"
            {"ability": "mage_fire_blast", "kind": "on_cooldown"},
            {"ability": "mage_fireball", "kind": "filler"},
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
    "warlock_affliction": {
        "glossary": "warlock", "resource": "mana", "role": "dps",
        "weapons": [],
        "rotation": [
            {"ability": "warlock_immolate", "kind": "maintain_dot"},   # notes: "the first DoT applied, before Corruption"
            {"ability": "warlock_corruption", "kind": "maintain_dot"},
        ],
    },
    "hunter_marksmanship": {
        "glossary": "hunter", "resource": "mana", "role": "dps",
        "weapons": [],  # Auto Shot itself isn't sourced (see the docstring) -- excluded, not zeroed by accident
        "rotation": [
            {"ability": "hunter_serpent_sting", "kind": "maintain_dot"},  # notes: "cast once the pet has engaged, before Aimed Shot"
            {"ability": "hunter_aimed_shot", "kind": "on_cooldown"},
            {"ability": "hunter_arcane_shot", "kind": "on_cooldown"},
        ],
    },
}

# Illustrative placeholder stats, identical across every class so the ranking compares
# rotations on equal footing -- NOT real level-20 gear (no sourced level-20 stat baseline
# exists yet for any class). Spell Power stays 0 for the melee/hybrid classes, since none of
# their sourced abilities have an sp_coeff that would use it meaningfully at this stat level.
DEFAULT_STATS = {"ap": 150, "sp": 90, "hit": 0.90, "crit": 0.15}


def run_class(cls_id, iterations=300, fight_len=300.0, stats=None):
    profile = ROTATIONS.get(cls_id)
    if not profile:
        return None
    glossary = wow_spells.load_class(profile.get("glossary", cls_id))
    if not glossary:
        return None
    stats = stats or DEFAULT_STATS
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
    print(f"\nLevel 20 DPS ranking ({args.iterations} fights x {args.fight_len:.0f}s, illustrative stats: {DEFAULT_STATS})\n")
    for spec_id, role, dps, breakdown in results:
        bar = "#" * max(1, round(40 * dps / max_dps))
        tag = f"[{role}]" if role != "dps" else ""
        print(f"{spec_id:22s} {tag:6s} {dps:6.2f} DPS  {bar}")
        for src, src_dps in sorted(breakdown.items(), key=lambda kv: -kv[1]):
            print(f"                              {src:28s} {src_dps:6.2f} ({100*src_dps/dps:4.1f}%)")
        print()


if __name__ == "__main__":
    main()
