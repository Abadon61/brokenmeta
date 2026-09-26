"""Pass/fail tests for the BrokenMeta addon, run in a mocked WoW API (see harness.py).

Run: py -3.11 -m unittest discover -s wow_addon/tests -p "test_units.py"
"""
import unittest

from harness import run

SWORD_EQ = "|cff1eff00|Hitem:1234:0:0:0:0:0:0:0:20|h[Sword]|h|r"
ITEMS = {
    "sword": {"loc": "INVTYPE_2HWEAPON", "classID": 2, "subID": 8,
              "stats": {"ITEM_MOD_STRENGTH_SHORT": 10, "ITEM_MOD_DAMAGE_PER_SECOND_SHORT": 10}},
    SWORD_EQ: {"loc": "INVTYPE_2HWEAPON", "classID": 2, "subID": 8, "stats": {"ITEM_MOD_STRENGTH_SHORT": 6}},
    "ring_crit": {"loc": "INVTYPE_FINGER", "stats": {"ITEM_MOD_CRIT_RATING_SHORT": 14}},
    "plate_chest": {"loc": "INVTYPE_CHEST", "classID": 4, "subID": 4, "stats": {"ITEM_MOD_STRENGTH_SHORT": 8, "ITEM_MOD_INTELLECT_SHORT": 8}},
    "mail_chest": {"loc": "INVTYPE_CHEST", "classID": 4, "subID": 3, "stats": {"ITEM_MOD_STRENGTH_SHORT": 8, "ITEM_MOD_INTELLECT_SHORT": 8}},
    "cloth_sp": {"loc": "INVTYPE_CHEST", "classID": 4, "subID": 1,
                 "text": ["Equip: Increases damage and healing done by magical spells and effects by up to 10."]},
    "food": {"loc": ""},
}


def lua_list(t):
    return [t[i] for i in range(1, len(t) + 1)] if t is not None else []


class TooltipTests(unittest.TestCase):
    def test_upgrade_line_and_equipped_marker(self):
        out, _, _, _ = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {16: SWORD_EQ}, ["sword", SWORD_EQ, "food"])
        self.assertIn("vs equipped", out[0])
        self.assertIn("+", out[0])
        self.assertIn("(equipped)", out[1])
        self.assertIsNone(out[2], "non-equippable items get no line")

    def test_weapon_dps_counts_for_melee_not_casters(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        with_dps = g.NS.scoreStats(g.LUA_EVAL("{str = 10, wdps = 10}"), "INVTYPE_2HWEAPON")
        without = g.NS.scoreStats(g.LUA_EVAL("{str = 10}"), "INVTYPE_2HWEAPON")
        self.assertGreater(with_dps, without)
        self.assertEqual(g.NS.scoreStats(g.LUA_EVAL("{wdps = 10}"), "INVTYPE_FINGER"), 0)
        _, _, _, g = run("enUS", "MAGE", [0, 0, 12], ITEMS, {}, [])
        self.assertEqual(g.NS.scoreStats(g.LUA_EVAL("{wdps = 10}"), "INVTYPE_2HWEAPON"), 0)

    def test_class_cannot_wear_plate_and_mail_needs_level_40(self):
        out, _, _, g = run("enUS", "SHAMAN", [0, 11, 0], ITEMS, {}, ["plate_chest", "mail_chest"])
        self.assertFalse(g.NS.CanWearType("Plate Mail")[0])
        can, need = g.NS.CanWearType("Mail")
        self.assertFalse(can)
        self.assertEqual(need, 40)
        self.assertTrue(g.NS.CanWearType("Leather")[0])
        self.assertTrue(g.NS.CanWearType(None)[0])
        self.assertIn("level 40", out[1] or "")

    def test_rating_fallback_is_flat(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        rp = g.NS.GetRatingPerPct()
        # The harness's client exposes GetCombatRatingBonusForCombatRatingValue (100/3.2 per 100).
        self.assertAlmostEqual(rp.crit, 3.2, places=2)


class HubTests(unittest.TestCase):
    def test_dungeon_upgrades_listed_for_naked_warrior(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [], [""])
        g.LUA_EVAL('function(label) for _, f in ipairs(frames) do if rawget(f, "text") == label and f.scripts.OnClick then f.scripts.OnClick() end end end')("Upgrades")
        texts = lua_list(g.LUA_EVAL('function() local o = {} for _, fs in ipairs(fontstrings) do local t = rawget(fs, "text") if t then o[#o+1] = t end end return o end')())
        self.assertTrue(any("Most rewarding dungeon" in t for t in texts))

    def test_bag_upgrades_skip_unwearable(self):
        _, _, _, g = run("enUS", "SHAMAN", [0, 11, 0], ITEMS, {}, [], [""], bags=["plate_chest", "cloth_sp"])
        g.LUA_EVAL('function(label) for _, f in ipairs(frames) do if rawget(f, "text") == label and f.scripts.OnClick then f.scripts.OnClick() end end end')("Upgrades")
        texts = lua_list(g.LUA_EVAL('function() local o = {} for _, fs in ipairs(fontstrings) do local t = rawget(fs, "text") if t then o[#o+1] = t end end return o end')())
        self.assertNotIn("plate_chest", texts)

    def test_localized_titles(self):
        for loc, expected in (("frFR", "Hub DPS"), ("deDE", "DPS-Hub"), ("esES", "Hub DPS"), ("enUS", "DPS Hub"), ("ruRU", "DPS Hub")):
            _, _, texts, _ = run(loc, "WARRIOR", [0, 11, 0], ITEMS, {}, [])
            self.assertTrue(any(expected in t for t in texts), (loc, expected))

    def test_guide_link_is_tagged_and_localized(self):
        _, _, _, g = run("frFR", "SHAMAN", [0, 11, 0], ITEMS, {}, [])
        url = g.NS.SiteURL("wow-forever/guides/shaman/elemental/", "guide")
        self.assertEqual(url, "https://brokenmeta.gg/wow-forever/guides/shaman/elemental/?utm_source=addon&utm_medium=ingame&utm_campaign=guide")
        _, _, _, g = run("deDE", "SHAMAN", [0, 11, 0], ITEMS, {}, [])
        self.assertIn("brokenmeta.gg/en/wow-forever/", g.NS.SiteURL("wow-forever/", "x"))


class ExportAndShareTests(unittest.TestCase):
    def test_export_has_class_spec_and_no_name(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {16: SWORD_EQ}, [])
        text = g.NS.BuildExport()
        self.assertTrue(text.startswith("format=BMW1"))
        self.assertIn("class=WARRIOR", text)
        self.assertIn("slot16=1234", text)
        self.assertNotIn("Test", text, "character name must never be exported")

    def test_share_string_format(self):
        _, _, _, g = run("enUS", "HUNTER", [0, 5, 0], ITEMS, {}, [])
        g.flush()
        text, n_meas, n_scans = g.NS.BuildShareString()
        self.assertTrue(text.startswith("BMD1 "))
        self.assertGreater(n_meas, 0)
        self.assertNotIn("|", text, "'|' is an escape character in WoW edit boxes")
        self.assertTrue(all(line[:2] in ("BM", "M ", "A ", "P ") for line in text.split("\n")))


class AuctionTests(unittest.TestCase):
    def test_modern_scan_keeps_min_price_and_no_seller(self):
        _, _, _, g = run("enUS", "MAGE", [0, 0, 0], ITEMS, {}, [])
        L = g.LUA_EVAL
        L('''function()
          LISTINGS = { {2, 500, 2589}, {1, 200, 2589}, {3, 900, 2592} }
          C_AuctionHouse = {
            ReplicateItems = function() for _, f in ipairs(frames) do if f.events.REPLICATE_ITEM_LIST_UPDATE then f.scripts.OnEvent(f, "REPLICATE_ITEM_LIST_UPDATE") end end end,
            GetNumReplicateItems = function() return #LISTINGS end,
            GetReplicateItemInfo = function(i) local l = LISTINGS[i + 1]; return "n", 1, l[1], 1, true, 1, 0, 0, 0, l[2], 0, false, nil, "SELLER", "SELLER-X", 0, l[3], true end,
          }
          AuctionHouseFrame = CreateFrame("Frame", "AuctionHouseFrame")
          for _, f in ipairs(frames) do if f.events and f.events.AUCTION_HOUSE_SHOW then f.scripts.OnEvent(f, "AUCTION_HOUSE_SHOW") end end
        end''')()
        g.flush()
        g.NS.StartAuctionScan()
        g.flush()
        scans = g.NS.Data().ah
        scan = scans[len(scans)]
        self.assertEqual(lua_list(scan.prices[2589]), [200, 3, 2])
        self.assertEqual(lua_list(scan.prices[2592]), [300, 3, 1])
        self.assertNotIn("SELLER", repr({k: lua_list(v) for k, v in scan.prices.items()}))

    def test_scan_refused_when_closed(self):
        _, _, _, g = run("enUS", "MAGE", [0, 0, 0], ITEMS, {}, [], ["ah"])
        self.assertIn("open the auction house first", g.chat[len(g.chat)])


class ImportWeightsTests(unittest.TestCase):
    CODE = "BMW-W1;spec=warrior_arms;level=34;date=2026-09-26;str=0.5;agi=0.1;int=0;ap=0.25;sp=0;crit=0.4;hit=0.6;wdps_mh=1.2;wdps_oh=0;wdps_r=0"

    def test_import_replaces_generic_weights_and_clear_restores(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        before = g.NS.scoreStats(g.LUA_EVAL("{str = 10}"), "INVTYPE_CHEST")
        ok = g.NS.ImportWeights(self.CODE)
        self.assertTrue(ok)
        self.assertEqual(g.NS.GetSpec(), "warrior_arms")
        self.assertAlmostEqual(g.NS.scoreStats(g.LUA_EVAL("{str = 10}"), "INVTYPE_CHEST"), 5.0)
        g.SlashCmdList.BROKENMETAWEIGHTS("import clear")
        self.assertNotAlmostEqual(g.NS.scoreStats(g.LUA_EVAL("{str = 10}"), "INVTYPE_CHEST"), 5.0)
        self.assertIsNotNone(before)

    def test_import_rejects_other_class_and_garbage(self):
        _, _, _, g = run("enUS", "MAGE", [0, 0, 12], ITEMS, {}, [])
        ok, err = g.NS.ImportWeights(self.CODE)
        self.assertFalse(ok)
        self.assertEqual(err, "import_class")
        ok, err = g.NS.ImportWeights("hello")
        self.assertEqual(err, "import_bad")


class VersionTests(unittest.TestCase):
    def test_update_notice_only_for_newer(self):
        _, _, _, g = run("enUS", "MAGE", [0, 0, 0], ITEMS, {}, [])
        frames = g.LUA_EVAL("function() return frames end")().values()
        for f in frames:
            if f.events and f.events["CHAT_MSG_ADDON"]:
                before = len(g.chat)
                f.scripts.OnEvent(f, "CHAT_MSG_ADDON", "BrokenMeta", "V:0")
                self.assertEqual(len(g.chat), before, "same/older version: no notice")
                f.scripts.OnEvent(f, "CHAT_MSG_ADDON", "BrokenMeta", "V:99.0.0")
                self.assertIn("newer version", g.chat[len(g.chat)])


if __name__ == "__main__":
    unittest.main()
