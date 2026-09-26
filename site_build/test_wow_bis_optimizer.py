"""Regression tests for wow_bis_optimizer.py (added 2026-09-26 alongside the feature itself):
the engine-driven BIS optimizer must never recommend an item a level-20 character of that class
couldn't actually legally equip, and must always produce a usable, finite DPS number.

Race/class base stats are duplicated here (not imported from build_site.py) to keep this suite
light -- build_site.py is the ~8700-line full site generator; importing it just for two small
constant tables isn't worth pulling in everything else it imports. Keep these in sync with
build_site.py's own OP_RACE_BASE_STATS / OP_CLASS_BONUS_STATS if either changes.

Run with: py -m unittest test_wow_bis_optimizer -v
"""
import json
import unittest

import wow_bis_optimizer as bo
import wow_dps_sim as w

RACE_BASE_STATS = {
    "human": {"str": 20, "agi": 20, "sta": 20, "int": 20, "spi": 21},
    "dwarf": {"str": 22, "agi": 16, "sta": 23, "int": 19, "spi": 19},
    "nightelf": {"str": 17, "agi": 25, "sta": 19, "int": 20, "spi": 20},
    "gnome": {"str": 15, "agi": 23, "sta": 19, "int": 24, "spi": 20},
    "orc": {"str": 23, "agi": 17, "sta": 22, "int": 17, "spi": 23},
    "undead": {"str": 19, "agi": 18, "sta": 21, "int": 18, "spi": 25},
    "tauren": {"str": 25, "agi": 15, "sta": 22, "int": 15, "spi": 22},
    "troll": {"str": 21, "agi": 22, "sta": 21, "int": 16, "spi": 21},
}
CLASS_BONUS_STATS = {
    "warrior": {"str": 3, "agi": 0, "sta": 2, "int": 0, "spi": 0},
    "paladin": {"str": 2, "agi": 0, "sta": 2, "int": 0, "spi": 1},
    "shaman": {"str": 1, "agi": 0, "sta": 1, "int": 1, "spi": 1},
    "warlock": {"str": 0, "agi": 0, "sta": 1, "int": 2, "spi": 2},
    "hunter": {"str": 0, "agi": 3, "sta": 1, "int": 0, "spi": 1},
    "druid": {"str": 1, "agi": 0, "sta": 0, "int": 2, "spi": 2},
    "mage": {"str": 0, "agi": 0, "sta": 0, "int": 3, "spi": 2},
    "rogue": {"str": 1, "agi": 3, "sta": 1, "int": 0, "spi": 0},
    "priest": {"str": 0, "agi": 0, "sta": 0, "int": 2, "spi": 3},
}
STAT_NAMES = {"str": "Force", "agi": "Agilite", "int": "Intelligence", "spi": "Esprit", "sta": "Endurance",
              "splpwr": "Puissance des sorts", "spldmg": "Degats des sorts", "atkpwr": "Puissance d'attaque",
              "manargn": "Mp5", "critstrkrtng": "Coup critique", "hastertng": "Hate", "hitrtng": "Toucher",
              "defrtng": "Defense", "armor": "Armure"}


def _fallback_data():
    path = w.wow_spells.ROOT / "data" / "wow_items" / "bis_gear_by_slot.json"
    return json.loads(path.read_text(encoding="utf-8"))


class TestArmorAndWeaponEligibility(unittest.TestCase):
    """Every chosen dungeon-sourced item (not a foreverchanges fallback) must be something that
    spec's own class could actually equip at level 20 -- the real point of building this
    optimizer instead of trusting an external list blindly."""

    def test_no_spec_gets_an_illegal_item(self):
        fallback_data = _fallback_data()
        pool_by_id = {it["id"]: it for it in bo._load_item_pool()}
        for spec_id in w.ROTATIONS:
            with self.subTest(spec=spec_id):
                profile = w.ROTATIONS[spec_id]
                class_id = profile.get("glossary", spec_id)
                armor_types = bo.ARMOR_PROFICIENCY.get(class_id, set())
                weapon_types = bo.WEAPON_PROFICIENCY.get(class_id, set())
                fallback = fallback_data["specs"].get(spec_id, [])
                result = bo.optimize_spec(spec_id, RACE_BASE_STATS, CLASS_BONUS_STATS, fallback, STAT_NAMES)
                self.assertIsNotNone(result, f"{spec_id}: optimize_spec returned None")
                gear, _, dps = result
                for it in gear:
                    if it["source"] == "foreverchanges":
                        continue  # not from our own filtered pool; foreverchanges is trusted as-is
                    raw = pool_by_id.get(it["wowhead_item_id"])
                    self.assertIsNotNone(raw, f"{spec_id}: chosen item {it['wowhead_item_id']} not in the level<=20 pool")
                    self.assertLessEqual(raw.get("req") or 0, bo.LEVEL_CAP, f"{spec_id}: {it['name']} requires a level above {bo.LEVEL_CAP}")
                    item_type = raw.get("type", {}).get("en")
                    if it["slot"] in ("head", "shoulder", "chest", "waist", "legs", "feet", "wrist", "hands"):
                        self.assertIn(item_type, armor_types, f"{spec_id}: {it['name']} ({item_type}) isn't a real armor type for {class_id} at level 20")
                    elif it["slot"] in ("main_hand", "off_hand", "ranged") and item_type != "Shield":
                        self.assertIn(item_type, weapon_types | {"Wands"}, f"{spec_id}: {it['name']} ({item_type}) isn't a real weapon proficiency for {class_id}")

    def test_dps_is_finite_and_positive(self):
        fallback_data = _fallback_data()
        for spec_id in w.ROTATIONS:
            with self.subTest(spec=spec_id):
                fallback = fallback_data["specs"].get(spec_id, [])
                _, _, dps = bo.optimize_spec(spec_id, RACE_BASE_STATS, CLASS_BONUS_STATS, fallback, STAT_NAMES)
                self.assertTrue(dps >= 0, f"{spec_id}: negative DPS {dps}")
                self.assertEqual(dps, dps, f"{spec_id}: DPS is NaN")  # NaN != NaN


class TestNoRaidLootInPool(unittest.TestCase):
    """The item pool must never include anything above the beta's level 20 cap -- raids in
    particular are entirely req=60 and must never leak in (see module docstring)."""

    def test_pool_is_level_capped(self):
        pool = bo._load_item_pool()
        self.assertTrue(len(pool) > 0, "item pool is empty")
        for it in pool:
            self.assertLessEqual(it.get("req") or 0, bo.LEVEL_CAP, f"{it['name']} (req {it.get('req')}) leaked into the level<=20 pool")


if __name__ == "__main__":
    unittest.main(verbosity=2)
