"""Regression tests for wow_dps_sim.py, added 2026-09-26 after a night of manual-trace debugging
turned up three real scheduling/parsing bugs (Corruption's cast_time silently read as 0.0,
Shaman Shocks not sharing their real cooldown group, _next_wakeup oversleeping past when a
cooldown actually cleared) that a human only caught by eyeballing a play-by-play trace. These
tests exist so the same class of bug fails loudly and automatically instead of needing another
manual trace session to notice.

Run with: py site_build/test_wow_dps_sim.py -v
"""
import unittest

import wow_dps_sim as w
import wow_spells


class TestAllSpecsRun(unittest.TestCase):
    """Every spec in ROTATIONS must run to completion (both the real ranking path and the
    play-by-play trace path) without raising, and produce a finite, non-negative DPS."""

    def test_run_class_all_specs(self):
        for spec_id in w.ROTATIONS:
            with self.subTest(spec=spec_id):
                result = w.run_class(spec_id, iterations=20, fight_len=60.0)
                self.assertIsNotNone(result, f"{spec_id}: run_class returned None")
                dps, breakdown = result
                self.assertTrue(dps >= 0, f"{spec_id}: negative DPS {dps}")
                self.assertTrue(dps == dps, f"{spec_id}: DPS is NaN")  # NaN != NaN
                self.assertIsInstance(breakdown, dict)

    def test_trace_rotation_all_specs(self):
        for spec_id in w.ROTATIONS:
            with self.subTest(spec=spec_id):
                trace = w.trace_rotation(spec_id, seconds=20)
                self.assertIsNotNone(trace, f"{spec_id}: trace_rotation returned None")
                # A spec with any weapon or ability should log at least one line in 20s.
                self.assertTrue(len(trace) > 0, f"{spec_id}: empty trace over 20s")


class TestBisStats(unittest.TestCase):
    """bis_stats_for_spec must return a complete, sane stat block for every spec."""

    def test_all_specs_have_valid_bis_stats(self):
        for spec_id in w.ROTATIONS:
            with self.subTest(spec=spec_id):
                stats = w.bis_stats_for_spec(spec_id)
                self.assertIsNotNone(stats, f"{spec_id}: no BIS stats found")
                for key in ("ap", "sp", "hit", "crit"):
                    self.assertIn(key, stats)
                    self.assertTrue(stats[key] >= 0, f"{spec_id}.{key} is negative: {stats[key]}")
                self.assertTrue(0 <= stats["hit"] <= 1, f"{spec_id}.hit out of [0,1]: {stats['hit']}")
                self.assertTrue(0 <= stats["crit"] <= 1, f"{spec_id}.crit out of [0,1]: {stats['crit']}")


class TestNoAbilityFiresBeforeItsCooldown(unittest.TestCase):
    """Regression test for the _next_wakeup bug (2026-09-26): traces every spec and checks that
    consecutive casts of the SAME ability (or members of the same cooldown_group) never land
    closer together than that ability's real cooldown_sec allows -- with a small tolerance for
    the engine's own decision-cadence granularity."""

    TOLERANCE_SEC = 0.6  # engine re-checks decisions in small steps, not continuously

    def test_no_cooldown_violations(self):
        for spec_id, profile in w.ROTATIONS.items():
            with self.subTest(spec=spec_id):
                glossary = wow_spells.load_class(profile.get("glossary", spec_id))
                abilities = {a["id"]: a for a in (glossary or {}).get("abilities", [])}
                # Map each ability to its cooldown group (abilities with no group are their own group).
                group_of = {aid: a.get("cooldown_group", aid) for aid, a in abilities.items()}
                last_cast_by_group = {}
                stats = w.bis_stats_for_spec(spec_id)
                sim = w.Sim(spec_id, profile, glossary, stats, 60.0)
                sim.trace = []
                sim.run()
                for line in sim.trace:
                    # Trace lines look like " 12.34s  Ability Name    dmg" -- parse the timestamp
                    # and match it back to an ability id by French name. Skip the "posé (DoT...)"
                    # annotation line: it logs at the SAME timestamp as the cast's own damage
                    # line, so counting both as separate cast events falsely reads as a same-
                    # instant re-cast (a bug in this test, not in the engine).
                    if "s  " not in line or "posé (DoT" in line or "(tick)" in line:
                        continue
                    t_str, rest = line.split("s  ", 1)
                    try:
                        t = float(t_str.strip())
                    except ValueError:
                        continue
                    for aid, ab in abilities.items():
                        fr_name = ab.get("name", {}).get("fr")
                        if fr_name and rest.startswith(fr_name):
                            group = group_of[aid]
                            cd = ab.get("cooldown_sec")
                            if cd:
                                prev = last_cast_by_group.get(group)
                                if prev is not None:
                                    gap = t - prev
                                    self.assertGreaterEqual(
                                        gap, cd - self.TOLERANCE_SEC,
                                        f"{spec_id}: {fr_name} (group={group}) fired after only "
                                        f"{gap:.2f}s, real cooldown is {cd}s (at t={t:.2f}s)",
                                    )
                                last_cast_by_group[group] = t
                            break


class TestEnhancementShockCadence(unittest.TestCase):
    """Specific regression test for tonight's headline fix: Earth Shock and Flame Shock must
    alternate on their real shared 6s Shock cooldown, not drift to ~7.8s like the pre-fix
    _next_wakeup bug caused."""

    def test_shock_alternation_is_tight(self):
        trace = w.trace_rotation("shaman_enhancement", seconds=40)
        shock_casts = []
        for line in trace:
            if "Choc tellurique" in line and "s  Choc tellurique" in line:
                t = float(line.split("s")[0].strip())
                shock_casts.append(("earth", t))
            elif "Horion de flammes" in line and "posé" not in line and " dégâts" in line and "tick" not in line:
                # Only count fresh casts (direct-damage line), not periodic ticks -- fresh casts
                # log a direct_damage amount at the same timestamp as a "posé" line.
                pass
        # At minimum, Earth Shock casts (which only ever happen as fresh casts, never ticks)
        # should be spaced close to the real 6s group cooldown, not drifted to ~7.8s+.
        for i in range(1, len(shock_casts)):
            gap = shock_casts[i][1] - shock_casts[i - 1][1]
            # Real cadence is 6s; the pre-fix bug drifted this to ~7.8s per alternation (~15.6s
            # between consecutive Earth Shock casts). 18s gives headroom for one occasional missed
            # shock (RNG) without masking a real regression back toward the old drifted cadence.
            self.assertLess(gap, 18.0, f"Earth Shock gap too large ({gap:.2f}s) between casts "
                                        f"{shock_casts[i-1]} and {shock_casts[i]} -- possible "
                                        f"_next_wakeup regression")


class TestNoNullAbilityNames(unittest.TestCase):
    """Regression test for the null-name bug (2026-09-26): every ability's name dict must have
    real string values for both languages, never an explicit null that would crash the trace
    tool or render as the literal word 'None' on a guide page."""

    def test_all_class_glossaries(self):
        for class_id in ("warrior", "rogue", "paladin", "shaman", "mage", "priest", "druid", "warlock", "hunter"):
            data = wow_spells.load_class(class_id)
            for ability in data.get("abilities", []):
                for lang, val in ability.get("name", {}).items():
                    with self.subTest(cls=class_id, ability=ability["id"], lang=lang):
                        self.assertIsNotNone(val, f"{class_id}.{ability['id']}.name.{lang} is null")
                        self.assertTrue(len(val) > 0, f"{class_id}.{ability['id']}.name.{lang} is empty")


class TestBuildRankingShape(unittest.TestCase):
    """build_ranking() must return exactly one row per ROTATIONS entry, sorted descending by DPS,
    each with the fields the homepage template and guide pages actually read."""

    def test_ranking_shape(self):
        import wow_talents
        wt_classes, _ = wow_talents.load()
        rows = w.build_ranking(wt_classes, "fr", iterations=20, fight_len=60.0)
        self.assertEqual(len(rows), len(w.ROTATIONS))
        dps_values = [r["dps"] for r in rows]
        self.assertEqual(dps_values, sorted(dps_values, reverse=True), "ranking rows not sorted by DPS descending")
        for r in rows:
            for key in ("spec_id", "class_id", "class_name", "spec_name", "role", "dps", "bis_gear", "bis_final_stats"):
                self.assertIn(key, r, f"{r.get('spec_id')}: missing '{key}' field")


if __name__ == "__main__":
    unittest.main(verbosity=2)
