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
        self.assertTrue(any("slot(s) improved" in t for t in texts), "the selected dungeon's summary")
        self.assertTrue(any("most rewarding" in t for t in texts), "the panel defaults to the best dungeon, marked as such")

    def test_upgrades_grouped_by_dungeon(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        by = g.NS.UpgradesByDungeon()
        dungeons = list(by.keys())
        self.assertGreater(len(dungeons), 1)
        for d in dungeons:
            dd = by[d]
            items = lua_list(dd["items"])
            self.assertTrue(all(x.it.d == d for x in items), "only that dungeon's items")
            self.assertEqual([x.gain for x in items], sorted((x.gain for x in items), reverse=True))
            self.assertLessEqual(dd.gain, sum(x.gain for x in items) + 1e-9, "per-run value = best item per slot")

    def test_bag_upgrades_skip_unwearable(self):
        _, _, _, g = run("enUS", "SHAMAN", [0, 11, 0], ITEMS, {}, [], [""], bags=["plate_chest", "cloth_sp"])
        g.LUA_EVAL('function(label) for _, f in ipairs(frames) do if rawget(f, "text") == label and f.scripts.OnClick then f.scripts.OnClick() end end end')("Upgrades")
        texts = lua_list(g.LUA_EVAL('function() local o = {} for _, fs in ipairs(fontstrings) do local t = rawget(fs, "text") if t then o[#o+1] = t end end return o end')())
        self.assertNotIn("plate_chest", texts)

    def test_localized_titles(self):
        for loc, expected in (("frFR", "Profession montre"), ("deDE", "Berufe zeigt"), ("esES", "Profesiones muestra"), ("enUS", "Professions shows"), ("ruRU", "Professions shows")):
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

    def test_refresh_reminder_after_five_levels(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        g.NS.ImportWeights(self.CODE.replace("level=34", "level=20"))
        self.assertIsNone(g.NS.ImportedWeightsStale(), "same level: not stale")
        g.NS.ImportWeights(self.CODE.replace("level=34", "level=15"))
        self.assertEqual(g.NS.ImportedWeightsStale(), 15, "5 levels behind (mock player is 20): stale")
        g.LUA_EVAL('function() for _, f in ipairs(frames) do if f.events and f.events.PLAYER_LEVEL_UP then f.scripts.OnEvent(f, "PLAYER_LEVEL_UP") end end end')()
        g.flush()
        self.assertIn("redo them on brokenmeta.gg", g.chat[len(g.chat)])

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


class CrafterTests(unittest.TestCase):
    ME = "P3;{a};20;WARRIOR;Alliance;Orc;2;{f};171:60:75;{m}"

    def setUp(self):
        _, _, _, self.g = run("frFR", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        self.g.flush()
        self.frame = next(f for f in self.g.LUA_EVAL("function() return frames end")().values()
                          if f.events and f.events["CHAT_MSG_CHANNEL"])

    def event(self, *args):
        self.frame.scripts.OnEvent(self.frame, *args)

    def line(self, text, author):
        # CHAT_MSG_CHANNEL: text, author, language, channel name, target, flags, zone id, number, base name
        self.event("CHAT_MSG_CHANNEL", text, author, "", "5. BrokenMetaCraft", "", "", 0, 5, "BrokenMetaCraft")

    def sent(self):
        return lua_list(self.g.SENT)

    def chat(self):
        return lua_list(self.g.CHAT)

    def test_login_joins_hidden_channel_and_sends_nothing(self):
        self.assertTrue(self.g.JOINED["BrokenMetaCraft"])
        self.assertEqual(self.chat(), [], "no chat line without a click")
        self.assertFalse(self.g.NS.CraftPeers() and len(list(self.g.NS.CraftPeers().keys())))

    def test_available_click_posts_a_chat_line(self):
        self.g.NS.SetCraftAvailable(True)
        self.assertEqual(self.chat()[-1], "CHANNEL:5:BM1 " + self.ME.format(a=1, m="", f=0))
        self.assertEqual(self.sent()[-1], "GUILD:" + self.ME.format(a=1, m="", f=0), "guild gets it invisibly")
        self.assertIn("disponible", self.g.chat[len(self.g.chat)])
        self.g.NS.SetCraftAvailable(False)
        self.assertEqual(self.chat()[-1], "CHANNEL:5:BM1 " + self.ME.format(a=0, m="", f=0), "unavailable is announced too")

    def test_channel_line_lists_crafter_and_whisper(self):
        self.line("BM1 P2;1;18;MAGE;Alliance;Human;3;164:150:225,197:80:150;Tout le cuir, compos fournies", "Bob-Realm")
        peers = self.g.NS.CraftPeers()
        self.assertTrue(peers["Bob-Realm"].avail)
        self.assertEqual(peers["Bob-Realm"].msg, "Tout le cuir, compos fournies")
        names = [e.name for e in lua_list(self.g.NS.CraftList()[0])]
        self.assertIn("Bob-Realm", names)
        self.line("BM1 P2;1;18;MAGE;Alliance;Human;3;164:150:225;", "Kael Storm Strike")
        self.assertIsNotNone(self.g.NS.CraftPeers()["Kael-StormStrike"], "space form stored as Name-Realm")
        self.g.NS.CraftWhisper("Bob-Realm")
        self.assertEqual(self.g.WHISPERED[1], "Bob-Realm")

    def test_ignores_self_other_faction_untagged_and_other_channels(self):
        self.line("BM1 P2;1;18;MAGE;Alliance;Human;2;164:150:225;", "Test-Realm")
        self.line("BM1 P2;1;18;MAGE;Alliance;Human;2;164:150:225;", "Test Stormstrike")
        self.line("BM1 P2;1;18;MAGE;Horde;Orc;2;164:150:225;", "Orc-Realm")
        self.line("P2;1;18;MAGE;Alliance;Human;2;164:150:225;", "Nolabel-Realm")
        self.event("CHAT_MSG_CHANNEL", "BM1 P2;1;18;MAGE;Alliance;Human;2;164:150:225;", "Trader-Realm", "", "2. Trade", "", "", 0, 2, "Trade")
        self.event("CHAT_MSG_ADDON", "BrokenMeta", "V:0.1", "GUILD", "Bob-Realm")
        self.assertEqual(len(list(self.g.NS.CraftPeers().keys())), 0)

    def test_request_click_and_invisible_answer_when_available(self):
        self.g.NS.CraftRequest(True)
        self.assertEqual(self.chat()[-1], "CHANNEL:5:BM1 Q1")
        self.line("BM1 Q1", "New-Realm")
        self.g.flush()
        self.assertFalse(any(s.startswith("WHISPER") for s in self.sent()), "unavailable: no answer")
        self.g.NS.SetCraftAvailable(True)
        self.line("BM1 Q1", "New-Realm")
        self.g.flush()
        sent = self.sent()
        self.assertEqual(sent[-1], "WHISPER:" + self.ME.format(a=1, m="", f=0))
        self.assertEqual(self.g.SENT_TO[len(sent)], "New-Realm")

    def test_message_cleaned_limited_and_announced(self):
        clean = self.g.NS.CleanCraftMessage
        self.assertEqual(clean("  |cffff0000Cuir;épique|r  "), "cffff0000Cuirépiquer")
        self.assertEqual(clean("é" * 80), "é" * 60, "60 characters, UTF-8 kept whole")
        self.g.NS.SetCraftMessage("Tout le cuir")
        self.assertEqual(self.chat(), [], "not available: saved only")
        self.g.NS.SetCraftAvailable(True)
        self.g.NS.SetCraftMessage("Tout le cuir, compos fournies")
        self.assertEqual(self.chat()[-1], "CHANNEL:5:BM1 " + self.ME.format(a=1, m="Tout le cuir, compos fournies", f=0))
        self.line("BM1 P2;1;18;MAGE;Alliance;Human;3;164:150:225;Salut |Hitem:1|h", "Bob-Realm")
        peer = self.g.NS.CraftPeers()["Bob-Realm"]
        self.assertEqual(peer.msg, "Salut Hitem:1h", "no chat escapes from others")
        self.assertEqual(peer.race, "Human")

    def test_group_profile_counts_in_diagnostics(self):
        self.event("CHAT_MSG_ADDON", "BMCraft", "P2;0;6;MAGE;Alliance;Troll;2;197:9:75;tout pour les po", "PARTY", "Polo-Realm")
        self.line("BM1 Q1", "Test-Realm")
        st = self.g.NS.CraftStats
        self.assertEqual((st.recv, st.echo), (1, 1))
        self.assertEqual(st.last, "Polo (PARTY)")
        self.assertIn("Polo-Realm", list(self.g.NS.CraftPeers().keys()))

    def test_favourite_stays_listed_when_not_announced(self):
        self.line("BM1 P2;1;18;MAGE;Alliance;Human;3;164:150:225;Armes", "Bob-Realm")
        self.g.NS.ToggleCraftFav("Bob-Realm", self.g.NS.CraftPeers()["Bob-Realm"])
        self.assertIsNotNone(self.g.NS.CraftFavs()["Bob-Realm"])
        self.event("CHAT_MSG_SYSTEM", "No player named 'Bob' is currently playing.")
        self.assertEqual(len(list(self.g.NS.CraftPeers().keys())), 0)
        bob = [e for e in lua_list(self.g.NS.CraftList()[0]) if e.name == "Bob-Realm"]
        self.assertEqual(len(bob), 1, "favourite kept in the list")
        self.assertTrue(bob[0].offline)
        self.assertFalse(bob[0].p.avail)
        self.assertEqual(bob[0].p.msg, "Armes")
        self.g.NS.ToggleCraftFav("Bob-Realm", bob[0].p)
        left = [e for e in lua_list(self.g.NS.CraftList()[0]) if e.name == "Bob-Realm"]
        self.assertEqual(len(left), 1, "no longer a favourite, still remembered as an announced crafter")
        self.assertFalse(left[0].fav)

    def test_register_is_saved_and_announced(self):
        self.g.NS.RegisterCrafter(True)
        self.assertEqual(self.chat()[-1], "CHANNEL:5:BM1 " + self.ME.format(a=1, m="", f=0))
        self.g.NS.RegisterCrafter(False)
        self.assertEqual(self.chat()[-1], "CHANNEL:5:BM1 " + self.ME.format(a=0, m="", f=0))

    def test_registered_crafter_is_available_at_login_and_announced_on_first_click(self):
        self.g.NS.RegisterCrafter(True)
        self.event("PLAYER_LOGIN")  # next session: the saved registration is kept
        before = len(self.chat())
        self.g.WorldFrame.scripts.OnMouseDown(self.g.WorldFrame)
        self.assertEqual(self.chat()[-1], "CHANNEL:5:BM1 " + self.ME.format(a=1, m="", f=0), "first click announces")
        self.assertEqual(len(self.chat()), before + 1)
        self.g.WorldFrame.scripts.OnMouseDown(self.g.WorldFrame)
        self.assertEqual(len(self.chat()), before + 1, "announce still fresh: nothing more")
        self.line("BM1 Q1", "New-Realm")
        self.g.flush()
        self.assertEqual(self.sent()[-1], "WHISPER:" + self.ME.format(a=1, m="", f=0), "answers Q1 invisibly")

    def test_unregistered_crafter_stays_silent_on_click(self):
        self.event("PLAYER_LOGIN")
        self.g.WorldFrame.scripts.OnMouseDown(self.g.WorldFrame)
        self.assertEqual(self.chat(), [])

    def test_announced_crafter_stays_listed_offline_until_they_leave(self):
        self.line("BM1 P3;1;18;MAGE;Alliance;Human;3;0;164:150:225;Armes", "Bob-Realm")
        self.event("CHAT_MSG_SYSTEM", "No player named 'Bob' is currently playing.")
        bob = [e for e in lua_list(self.g.NS.CraftList()[0]) if e.name == "Bob-Realm"]
        self.assertEqual(len(bob), 1, "remembered while offline")
        self.assertTrue(bob[0].offline)
        self.assertFalse(bob[0].p.avail)
        self.line("BM1 P3;0;18;MAGE;Alliance;Human;3;0;164:150:225;Armes", "Bob-Realm")
        self.event("CHAT_MSG_SYSTEM", "No player named 'Bob' is currently playing.")
        self.assertEqual([e for e in lua_list(self.g.NS.CraftList()[0]) if e.name == "Bob-Realm"], [], "said they are out")

    def test_onboarding_steps_follow_registration_and_message(self):
        steps, n = self.g.NS.CraftOnboarding()
        self.assertEqual(n, 0)
        self.g.NS.RegisterCrafter(True)
        self.g.NS.SetCraftMessage("Tout le cuir")
        steps, n = self.g.NS.CraftOnboarding()
        self.assertEqual(n, 2, "registered + message; recipes not recorded yet")
        self.assertEqual([s.done for s in lua_list(steps)], [True, False, True])

    def test_profession_icons(self):
        self.assertIn("Trade_Alchemy", self.g.NS.ProfIcon(171, 14))
        self.assertEqual(self.g.NS.ProfIcon(1), "", "unknown line: no icon")
        self.assertIn("QuestionMark", self.g.NS.ProfIconPath(1))

    def test_toast_goes_to_the_chat_when_the_hub_is_closed(self):
        before = len(self.g.chat)
        self.g.NS.Toast("tu es inscrit")
        self.assertEqual(len(self.g.chat), before + 1)

    def test_every_crafter_page_opens_without_error(self):
        for show in ("ShowCrafters", "ShowRequests", "ShowLeveling"):
            getattr(self.g.NS, show)()
        self.g.NS.RegisterCrafter(True)
        self.g.NS.ShowCrafters()
        self.line("BM1 P3;1;18;MAGE;Alliance;Human;3;0;164:150:225;Armes", "Bob-Realm")
        self.g.NS.ShowCrafters()

    def test_favourite_count_signals(self):
        # Someone favours me: my profile carries the count.
        self.event("CHAT_MSG_ADDON", "BMCraft", "F1", "WHISPER", "Fan-Realm")
        self.event("CHAT_MSG_ADDON", "BMCraft", "F1", "WHISPER", "Fan2-Realm")
        self.event("CHAT_MSG_ADDON", "BMCraft", "F1", "WHISPER", "Fan-Realm")
        self.g.NS.SetCraftAvailable(True)
        self.assertEqual(self.chat()[-1], "CHANNEL:5:BM1 " + self.ME.format(a=1, m="", f=2))
        self.event("CHAT_MSG_ADDON", "BMCraft", "F0", "WHISPER", "Fan2-Realm")
        self.g.NS.CraftAnnounce()
        self.assertEqual(self.chat()[-1], "CHANNEL:5:BM1 " + self.ME.format(a=1, m="", f=1))
        # I favour an online crafter: told right away; an offline one: told when seen again.
        self.line("BM1 P3;1;18;MAGE;Alliance;Human;3;7;164:150:225;x", "Bob-Realm")
        self.assertEqual(self.g.NS.CraftPeers()["Bob-Realm"].favs, 7)
        self.g.NS.ToggleCraftFav("Bob-Realm", self.g.NS.CraftPeers()["Bob-Realm"])
        self.assertEqual(lua_list(self.g.SENT)[-1], "WHISPER:F1")
        self.g.NS.ToggleCraftFav("Cid-Realm", self.g.NS.CraftPeers()["Bob-Realm"])
        self.assertNotEqual(self.g.SENT_TO[len(lua_list(self.g.SENT))], "Cid-Realm", "offline: not yet")
        self.line("BM1 P2;1;18;MAGE;Alliance;Human;3;164:150:225;", "Cid-Realm")
        self.assertEqual(lua_list(self.g.SENT)[-1], "WHISPER:F1")
        self.assertEqual(self.g.SENT_TO[len(lua_list(self.g.SENT))], "Cid-Realm")
        self.assertEqual(self.g.NS.CraftPeers()["Cid-Realm"].favs, 0, "P2 from older versions still read")

    def test_offline_player_dropped(self):
        self.line("BM1 P2;1;18;MAGE;Alliance;Human;2;164:150:225;", "Bob-Realm")
        self.event("CHAT_MSG_SYSTEM", "No player named 'Bob' is currently playing.")
        self.assertEqual(len(list(self.g.NS.CraftPeers().keys())), 0)


class RecipeTests(unittest.TestCase):
    def setUp(self):
        _, _, _, self.g = run("frFR", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        self.g.flush()
        self.ev = self.g.LUA_EVAL
        # Modern profession window: Tailoring (197) open, recipes 1 and 2 learned (2 makes no item), 3 not.
        self.ev('''function()
          C_TradeSkillUI = {
            GetBaseProfessionInfo = function() return { professionID = 197 } end,
            GetAllRecipeIDs = function() return { 1, 2, 3 } end,
            GetRecipeInfo = function(id) return { learned = id ~= 3 } end,
            GetRecipeSchematic = function(id) if id == 2 then return {} end return { outputItemID = 1000 + id } end,
          }
        end''')()
        self.frame = next(f for f in self.ev("function() return frames end")().values()
                          if f.events and f.events["CHAT_MSG_CHANNEL"])

    def addon_msg(self, body, sender):
        self.frame.scripts.OnEvent(self.frame, "CHAT_MSG_ADDON", "BMCraft", body, "WHISPER", sender)

    def test_capture_from_profession_window(self):
        line, n = self.g.NS.CaptureRecipes()
        self.assertEqual((line, n), (197, 2))
        self.assertEqual(lua_list(self.g.NS.MyRecipes()[197]), [-2, 1001], "item IDs, minus spell ID without item")
        self.assertIn("2 recettes de Couture", self.g.chat[len(self.g.chat)])

    def test_answer_request_in_chunks(self):
        self.g.NS.CaptureRecipes()
        self.addon_msg("R1?", "Bob-Realm")
        self.g.flush()
        sent = lua_list(self.g.SENT)
        self.assertEqual(sent[-1], "WHISPER:R1;197;1;1;-2,1001")
        self.assertEqual(self.g.SENT_TO[len(sent)], "Bob-Realm")
        # nothing recorded: an explicit empty answer
        _, _, _, g2 = run("frFR", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        f2 = next(f for f in g2.LUA_EVAL("function() return frames end")().values() if f.events and f.events["CHAT_MSG_CHANNEL"])
        f2.scripts.OnEvent(f2, "CHAT_MSG_ADDON", "BMCraft", "R1?", "WHISPER", "Bob-Realm")
        g2.flush()
        self.assertEqual(lua_list(g2.SENT)[-1], "WHISPER:R1;0;1;1;")

    def test_receive_chunks_and_search(self):
        self.g.NS.ShowRecipes("Bob-Realm", False)
        self.assertEqual(lua_list(self.g.SENT)[-1], "WHISPER:R1?", "asked by invisible whisper")
        self.addon_msg("R1;164;1;2;10,11", "Bob-Realm")
        self.addon_msg("R1;164;2;2;12", "Bob-Realm")
        cache = self.g.NS.PeerRecipes("Bob-Realm")
        self.assertEqual(lua_list(cache.lines[164]), [10, 11, 12])
        self.addon_msg("R1;164;1;1;13", "Bob-Realm")
        self.assertEqual(lua_list(cache.lines[164]), [13], "a new answer replaces the old list")
        self.ev('function() ITEMS[13] = { name = "Bottes en cuir cousu main" } end')()
        found, n = self.g.NS.RecipeMatches("Bob-Realm", "BOTTES")
        self.assertEqual((lua_list(found), n), (["Bottes en cuir cousu main"], 1))
        self.assertEqual(self.g.NS.RecipeMatches("Bob-Realm", "épée")[1], 0)
        self.g.flush()


class LevelingTests(unittest.TestCase):
    def setUp(self):
        _, _, _, self.g = run("frFR", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        self.ev = self.g.LUA_EVAL

    def test_vendor_farm_and_crafted_prices(self):
        price = self.g.NS.ReagentPrice
        prof = self.ev("{ made = { [99] = { n = 2, reag = { { id = 1, n = 4, k = 'v', v = 50 } } } } }")
        vendor = self.ev("{ id = 1, n = 1, k = 'v', v = 50 }")
        farm = self.ev("{ id = 2, n = 1, k = 'f' }")
        crafted = self.ev("{ id = 99, n = 1, k = 'c' }")
        self.assertEqual(price(prof, vendor, None, 0), (50, "v"))
        self.assertEqual(price(prof, vendor, self.ev("{ [1] = { 30, 20, 1 } }"), 0), (30, "a"), "AH cheaper than vendor")
        self.assertEqual(price(prof, farm, None, 0), (None, None), "farmed, no scan: unknown")
        self.assertEqual(price(prof, farm, self.ev("{ [2] = { 120, 5, 1 } }"), 0), (120, "a"))
        # crafted: 4 x 50 vendor / 2 made = 100 each, cheaper than 150 on the AH
        self.assertEqual(price(prof, crafted, self.ev("{ [99] = { 150, 5, 1 } }"), 0), (100, "c"))
        self.assertEqual(price(prof, crafted, self.ev("{ [99] = { 80, 5, 1 } }"), 0), (80, "a"))

    def test_plan_from_current_skill_uses_latest_scan(self):
        plan, total, missing, crafts, scan = self.g.NS.LevelingPlan(171, 60)
        steps = lua_list(plan)
        self.assertGreater(len(steps), 0)
        self.assertGreaterEqual(steps[0].step.t, 61, "done steps are skipped")
        self.assertIsNone(scan)
        self.assertGreater(missing, 0, "herbs have no price without a scan")
        farm = {r.g.id for st in steps for r in lua_list(st.reag) if r.g.k != "v"}
        d = self.g.NS.Data()
        prices = self.ev("{}")
        for item in farm:
            prices[item] = self.ev("{ 10, 99, 1 }")
        d.ah[len(d.ah) + 1] = self.ev("{ realm = 'Realm', faction = 'Alliance', t = 1790000000 }")
        d.ah[len(d.ah)].prices = prices
        plan2, total2, missing2, _, scan2 = self.g.NS.LevelingPlan(171, 60)
        self.assertIsNotNone(scan2)
        self.assertEqual(missing2, 0)
        self.assertGreater(total2, total)
        first = lua_list(plan2)[0]
        per_craft = sum((r.unit or 0) * r.g.n for r in lua_list(first.reag))
        self.assertAlmostEqual(first.unitCost, per_craft / (first.step.q or 1))
        self.assertIsNone(first.ah, "crafted potion not in the scan")
        prices[first.step.item] = self.ev("{ 777, 3, 1 }")
        self.assertEqual(lua_list(self.g.NS.LevelingPlan(171, 60)[0])[0].ah, 777)


class WorkshopTests(unittest.TestCase):
    def setUp(self):
        _, _, _, self.g = run("frFR", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        self.g.flush()
        self.ev = self.g.LUA_EVAL

    def scan(self, t, prices):
        d = self.g.NS.Data()
        s = self.ev("{ realm = 'Realm', faction = 'Alliance' }")
        s.t = t
        s.prices = self.ev("{}")
        for k, v in prices.items():
            s.prices[k] = self.ev("{ %d, %d, 1 }" % (v, 20))
        d.ah[len(d.ah) + 1] = s

    def test_market_is_the_median_of_recent_scans(self):
        now = 1790000000
        self.scan(now - 3600 * 50, {2589: 100})
        self.scan(now - 3600 * 20, {2589: 900})       # one overpriced scan
        self.scan(now - 3600 * 2, {2589: 120, 2592: 50})
        self.scan(now - 86400 * 20, {2589: 1})        # too old: ignored
        m = self.g.NS.Market()
        self.assertEqual(m.n, 3)
        self.assertEqual(m.prices[2589][0 + 1], 120, "median, not the latest or the extreme")
        self.assertEqual(m.prices[2592][1], 50)
        self.assertFalse(m.stale)

    def test_craft_cost_and_profitable_crafts(self):
        # Tailoring 197, Brown Linen Vest 2568: 1 Bolt of Linen Cloth (2996, crafted from 2 Linen 2589) + 1 Coarse Thread (2320, vendor 10)
        r = self.g.NS.DecodeReagents(self.ev("function() return ns_RECIPES_197_2568 end")() if False else self.g.NS.RECIPES[197][2568].r)
        ids = sorted(x.id for x in lua_list(r))
        self.assertEqual(ids, [2320, 2996])
        prices = self.ev("{ [2589] = { 30, 99, 1 }, [2568] = { 400, 5, 1 } }")
        cost = self.g.NS.CraftCost(197, 2568, prices)
        self.assertAlmostEqual(cost, 2 * 30 + 10, msg="bolt priced as its crafting cost (2 linen), thread at vendor price")
        store = self.g.NS.MyRecipes()
        store[197] = self.ev("{ 2568 }")
        crafts = lua_list(self.g.NS.ProfitableCrafts(197, prices))
        self.assertEqual(len(crafts), 1)
        self.assertAlmostEqual(crafts[0].margin, 400 * 0.95 - 70)

    def test_recipes_to_learn_and_shopping_list(self):
        store = self.g.NS.MyRecipes()
        store[171] = self.ev("{ 118 }")  # knows Minor Healing Potion
        todo = lua_list(self.g.NS.RecipesToLearn(171, 60))
        keys = [e.key for e in todo]
        self.assertNotIn(118, keys, "known recipes left out")
        self.assertTrue(all(e.r.l <= 85 for e in todo), "up to skill + 25")
        self.assertEqual([e.r.l for e in todo], sorted(e.r.l for e in todo))
        route = self.g.NS.PROFESSIONS[171]
        reag = route.steps[len(lua_list(route.steps))].reag[1].id
        self.ev("function(id) BAGCOUNT[id] = 3 end")(reag)
        items, total = self.g.NS.ShoppingList(171, 60)
        x = next(i for i in lua_list(items) if i.id == reag)
        self.assertEqual(x.have, 3)
        self.assertEqual(x.buy, max(0, x.need - 3))


class RequestTests(unittest.TestCase):
    def setUp(self):
        _, _, _, self.g = run("frFR", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        self.g.flush()
        self.ev = self.g.LUA_EVAL
        self.frame = next(f for f in self.ev("function() return frames end")().values()
                          if f.events and f.events["CHAT_MSG_CHANNEL"])

    def line(self, text, author):
        self.frame.scripts.OnEvent(self.frame, "CHAT_MSG_CHANNEL", text, author, "", "5. BrokenMetaCraft", "", "", 0, 5, "BrokenMetaCraft")

    def test_resolve_item_by_name_or_link(self):
        r = self.g.NS.ResolveCraftable
        self.assertEqual(r("Gilet marron en lin"), 2568)
        self.assertEqual(r("  gilet MARRON en lin "), 2568)
        self.assertEqual(r("|cffffffff|Hitem:2568::::|h[x]|h|r"), 2568)
        self.assertIsNone(r("zz"))
        self.assertIsNone(r("item:6948"), "not craftable")

    def test_post_repost_guard_and_cancel(self):
        self.g.NS.PostCraftRequest(2568)
        self.assertEqual(lua_list(self.g.CHAT)[-1], "CHANNEL:5:BM1 D1;Alliance;2568")
        self.g.NS.PostCraftRequest(2568)
        self.assertEqual(len(lua_list(self.g.CHAT)), 1, "no repost within a minute")
        self.g.NS.CancelCraftRequest()
        self.assertEqual(lua_list(self.g.CHAT)[-1], "CHANNEL:5:BM1 D0")

    def test_crafter_is_told_and_late_arrivals_get_answers(self):
        self.g.NS.MyRecipes()[197] = self.ev("{ 2568 }")
        self.line("BM1 D1;Alliance;2568", "Bob-Realm")
        self.assertIn("tu sais le fabriquer", self.g.chat[len(self.g.chat)])
        lst = lua_list(self.g.NS.CraftRequestList())
        self.assertEqual((lst[0].name, lst[0].item, lst[0].can), ("Bob-Realm", 2568, True))
        self.line("BM1 D1;Horde;2568", "Orc-Realm")
        self.assertEqual(len(lua_list(self.g.NS.CraftRequestList())), 1, "other faction ignored")
        self.line("BM1 D0", "Bob-Realm")
        self.assertEqual(len(lua_list(self.g.NS.CraftRequestList())), 0)
        # I have a request: a DQ gets it by invisible whisper
        self.g.NS.PostCraftRequest(2568)
        self.line("BM1 DQ", "New-Realm")
        self.g.flush()
        sent = lua_list(self.g.SENT)
        self.assertEqual(sent[-1], "WHISPER:D1;Alliance;2568;0")
        self.assertEqual(self.g.SENT_TO[len(sent)], "New-Realm")


class OptionsTourTests(unittest.TestCase):
    def test_tooltip_dps_option_and_defaults(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {16: SWORD_EQ}, [])
        self.assertTrue(g.NS.Option("tooltip_dps"))
        self.assertTrue(g.NS.Option("request_alert"))
        self.assertIn("vs equipped", g.hover("sword"))
        g.NS.SetOption("tooltip_dps", False)
        self.assertFalse(g.NS.Option("tooltip_dps"))
        line = g.hover("sword")
        self.assertTrue(line is None or "DPS" not in line, "DPS line off")

    def test_tour_starts_once(self):
        _, _, texts, g = run("frFR", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        g.NS.ToggleHub()
        tour = g.LUA_EVAL("function() return _G.BrokenMetaTour end")()
        self.assertTrue(tour.shown, "first opening shows the tour")
        g.NS.TourStep(5)
        self.assertEqual(tour.count.text, "5 / 5")
        tour.nextBtn.scripts.OnClick(tour.nextBtn)
        self.assertFalse(tour.shown)
        self.assertTrue(g.LUA_EVAL("function() return BrokenMetaWeightsDB.tourDone end")())
        g.NS.ToggleHub(); g.NS.ToggleHub()
        self.assertFalse(tour.shown, "not again once done")


def delta4(g, link):
    r = g.NS.deltaVsEquipped(link, g.NS.score(link))
    r = r if isinstance(r, tuple) else (r,)
    return tuple(r) + (None,) * (4 - len(r))


class DualSlotTests(unittest.TestCase):
    ITEMS2 = dict(ITEMS)
    ITEMS2.update({
        "ring_a": {"loc": "INVTYPE_FINGER", "stats": {"ITEM_MOD_STRENGTH_SHORT": 2}},
        "ring_b": {"loc": "INVTYPE_FINGER", "stats": {"ITEM_MOD_STRENGTH_SHORT": 6}},
        "ring_new": {"loc": "INVTYPE_FINGER", "stats": {"ITEM_MOD_STRENGTH_SHORT": 5}},
        "mh_1h": {"loc": "INVTYPE_WEAPON", "classID": 2, "subID": 7, "stats": {"ITEM_MOD_STRENGTH_SHORT": 4}},
        "oh_1h": {"loc": "INVTYPE_WEAPON", "classID": 2, "subID": 7, "stats": {"ITEM_MOD_STRENGTH_SHORT": 3}},
        "shield": {"loc": "INVTYPE_SHIELD", "classID": 4, "subID": 6, "stats": {"ITEM_MOD_STRENGTH_SHORT": 3}},
    })

    def test_ring_compares_with_weaker_and_shows_the_other(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], self.ITEMS2, {11: "ring_a", 12: "ring_b"}, [])
        s = g.NS.score
        d, same, note, other = delta4(g, "ring_new")
        self.assertAlmostEqual(d, s("ring_new") - s("ring_a"), msg="replaces the weaker ring")
        self.assertAlmostEqual(other, s("ring_new") - s("ring_b"))
        self.assertIn("vs the other", g.hover("ring_new"))

    def test_two_hander_replaces_both_hands(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], self.ITEMS2, {16: "mh_1h", 17: "oh_1h"}, [])
        s = g.NS.score
        d, same, note, other = delta4(g, "sword")
        self.assertAlmostEqual(d, s("sword") - s("mh_1h") - s("oh_1h"))
        self.assertEqual(note, "two")
        self.assertIn("vs both your weapons", g.hover("sword"))

    def test_off_hand_under_a_two_hander(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], self.ITEMS2, {16: SWORD_EQ}, [])
        s = g.NS.score
        d, same, note, other = delta4(g, "shield")
        self.assertEqual(note, "replaces_2h")
        self.assertAlmostEqual(d, s("shield") - s(SWORD_EQ))


class EconomyDungeonTests(unittest.TestCase):
    def setUp(self):
        _, _, _, self.g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [], [], bags=["food", "ring_crit"])
        self.ev = self.g.LUA_EVAL

    def scan(self, t, prices):
        d = self.g.NS.Data()
        s = self.ev("{ realm = 'Realm', faction = 'Alliance' }")
        s.t, s.prices = t, self.ev("{}")
        for k, v in prices.items():
            s.prices[k] = self.ev("{ %d, 7, 1 }" % v)
        d.ah[len(d.ah) + 1] = s

    def test_ah_tooltip_line_on_any_item(self):
        self.ev('function() ITEMS["item:2589"] = { name = "Linen", loc = "" } end')()
        self.assertIsNone(self.g.hover("item:2589"), "no scan, no line")
        self.scan(1790000000 - 60, {2589: 120})
        line = self.g.hover("item:2589")
        self.assertIn("AH price", line)
        self.g.NS.SetOption("tooltip_ah", False)
        self.assertIsNone(self.g.hover("item:2589"))

    def test_price_history_and_deals(self):
        now = 1790000000
        for k, v in enumerate([1000, 1100, 900, 1050]):
            self.scan(now - (5 - k) * 3600, {2589: v, 2592: 500})
        self.scan(now - 60, {2589: 400, 2592: 480})
        hist = lua_list(self.g.NS.PriceHistory(2589))
        self.assertEqual([h.unit for h in hist][:2], [400, 1050], "newest first")
        deals = lua_list(self.g.NS.AuctionDeals())
        self.assertEqual([d.id for d in deals], [2589], "only the item under 70% of its usual price")
        self.assertAlmostEqual(deals[0].margin, deals[0].usual * 0.95 - 400)

    def test_dungeon_loot_grouped_by_boss_and_loot_log(self):
        items, n, ups = self.g.NS.DungeonLoot(2)  # Deadmines
        rows = lua_list(items)
        self.assertTrue(rows[0].header, "starts with a boss header")
        self.assertEqual(n, sum(1 for r in rows if not r.header))
        self.assertTrue(any(r.header and r.header.startswith("Quest rewards") for r in rows))
        self.assertGreater(ups, 0, "a naked warrior has upgrades")
        # loot log: only inside a dungeon
        self.ev('function() LOOT_ITEM_SELF = "You receive loot: %s."; LOOT_ITEM_SELF_MULTIPLE = "You receive loot: %sx%d." end')()
        self.g.NS.RecordLoot("You receive loot: |cff1eff00|Hitem:872::::|h[Rockslicer]|h|r.")
        self.assertEqual(len(lua_list(self.g.NS.LootLog())), 0, "not in a dungeon")
        self.ev('function() GetInstanceInfo = function() return "Deadmines", "party" end end')()
        self.assertEqual(self.g.NS.CurrentDungeon(), 2)
        self.g.NS.RecordLoot("You receive loot: |cff1eff00|Hitem:872::::|h[Rockslicer]|h|r.")
        self.g.NS.RecordLoot("You receive loot: |cff1eff00|Hitem:2589::::|h[Linen]|h|rx3.")
        log = lua_list(self.g.NS.LootLog())
        self.assertEqual([(e.d, e.n) for e in log], [(2, 3), (2, 1)], "newest first, with the count")


class CodexDungeonTests(unittest.TestCase):
    def setUp(self):
        _, _, _, self.g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [], [], bags=["food", "ring_crit"])
        self.ev = self.g.LUA_EVAL

    def test_bosses_in_game_order_with_their_loot_and_an_other_entry(self):
        bosses = lua_list(self.g.NS.DungeonBosses(2))  # Deadmines
        names = [b.name for b in bosses]
        self.assertEqual(names[0], "Rhahk'Zor", "the game's encounter order")
        self.assertIn("Edwin VanCleef", names)
        edwin = next(b for b in bosses if b.name == "Edwin VanCleef")
        self.assertTrue(edwin.npc, "NPC id for the head")
        self.assertGreater(len(lua_list(edwin["items"])), 0)
        self.assertTrue(bosses[-1].other, "monsters and quests come last")
        total = sum(len(lua_list(b["items"])) for b in bosses)
        self.assertEqual(total, sum(1 for it in lua_list(self.g.NS.LOOT) if it.d == 2), "every item is under one entry")

    def test_quests_are_grouped_with_a_header_row_each(self):
        bosses = lua_list(self.g.NS.DungeonBosses(2))  # Deadmines: 5 quests
        quests = next(b for b in bosses if b.quest)
        rows = lua_list(quests["rows"])
        headers = [r for r in rows if r.header]
        self.assertEqual(len(headers), 5)
        self.assertTrue(rows[0].header, "a quest header comes first")
        self.assertTrue(all(r.indent for r in rows if not r.header), "rewards are indented under their quest")
        self.assertEqual(len(lua_list(quests["items"])), len(rows) - len(headers))

    def test_raid_bosses_with_head_abilities_and_loot(self):
        bosses = lua_list(self.g.NS.RaidBosses(1))  # Molten Core
        self.assertEqual(bosses[0].name, "Lucifron")
        self.assertTrue(bosses[0].npc, "NPC id for the head")
        self.assertTrue(bosses[0].abilities, "abilities line")
        self.assertGreater(len(lua_list(bosses[1]["items"])), 0, "Magmadar drops Earthshaker")
        self.assertTrue(bosses[-1].other, "the loot of the raid's other monsters comes last")
        self.assertGreater(self.g.NS.RAID_IMAGES["molten-core"], 0)

    def test_dungeon_and_raid_tabs_open_in_both_views(self):
        tabs = self.g.NS.CodexTabs
        for key in ("dungeons", "raids"):
            self.g.NS.HubShow(tabs[key])  # the cards of the instances (a single raid goes straight to its detail)
        self.ev('function() GetInstanceInfo = function() return "Molten Core", "raid" end end')()
        self.assertEqual(self.g.NS.CurrentRaid(), 1)
        self.g.NS.HubShow(tabs["raids"])
        self.ev('function() GetInstanceInfo = function() return "Deadmines", "party" end end')()
        self.g.NS.HubShow(tabs["dungeons"])

    def test_every_dungeon_has_a_picture(self):
        art = lua_list(self.g.NS.DUNGEON_ART)
        self.assertEqual(len(art), len(lua_list(self.g.NS.DUNGEONS)))
        self.assertTrue(all(a.image and a.image > 0 for a in art))

    def test_the_two_views_open_without_error(self):
        self.g.NS.HubOpenSection("codex")  # list of the dungeons
        self.ev('function() GetInstanceInfo = function() return "Deadmines", "party" end end')()
        self.g.NS.HubOpenSection("codex")  # you are in one: its first boss
        self.g.NS.HubOpenSection("codex")


class TalentWeightsTests(unittest.TestCase):
    """Mental Dexterity turns Intellect into Attack Power: the Intellect weight follows the rank taken."""

    def weights(self, ranks):
        _, _, _, g = run("enUS", "SHAMAN", [0, 11, 0], ITEMS, {}, [], [])
        g.LUA_EVAL("function() BrokenMetaNS.readTalents = function() return %s end end" % ranks)()
        w, _ = g.NS.ActiveWeights("shaman_enhancement")
        return w

    def test_intellect_weight_follows_mental_dexterity(self):
        full = self.weights("{ [104755] = 3 }")
        self.assertGreater(full["ap"], 0)
        self.assertAlmostEqual(full["int"], full["ap"], places=3, msg="3/3: 100% of Intellect becomes Attack Power")
        one = self.weights("{ [104755] = 1 }")
        self.assertAlmostEqual(one["int"], one["ap"] / 3, places=3, msg="1/3: a third")
        none = self.weights("{}")
        self.assertEqual(none["int"], 0, "no talent: Intellect is worth nothing to Enhancement")

    def test_other_specs_are_untouched(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [], [])
        w, _ = g.NS.ActiveWeights("warrior_fury")
        self.assertEqual(w["int"], 0)


class CharacterPageTests(unittest.TestCase):
    def test_character_page_opens_with_gauges_for_every_stat(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [], [], bags=["food", "ring_crit"])
        g.NS.HubShow(g.NS.DPSTabs["character"])  # weights as gauges + equipped gear
        weights, _ = g.NS.ActiveWeights(g.NS.GetSpec())
        self.assertGreater(weights["str"] + weights["ap"] + weights["crit"], 0)

    def test_every_dps_page_opens(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [], [], bags=["food", "ring_crit"])
        for key in ("character", "upgrades", "bis", "guide", "export"):
            g.NS.HubShow(g.NS.DPSTabs[key])
        # again with the first dungeon picked and no spec: the empty states
        g.NS.HubShow(g.NS.DPSTabs["upgrades"])


class LanguageTests(unittest.TestCase):
    def texts(self, g):
        return lua_list(g.LUA_EVAL('function() local o = {} for _, fs in ipairs(fontstrings) do local t = rawget(fs, "text") if t then o[#o+1] = t end end return o end')())

    def test_language_override_and_auto(self):
        _, _, texts, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [], cvars={"brokenMetaLanguage": "frFR"})
        self.assertEqual((g.NS.LOCALE, g.NS.CLIENT_LOCALE, g.NS.IS_FR), ("frFR", "enUS", True))
        self.assertTrue(any("Profession montre" in t for t in texts), "French texts on an English client")
        _, _, texts, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [], cvars={"brokenMetaLanguage": "auto"})
        self.assertEqual(g.NS.LOCALE, "enUS")
        _, _, texts, g = run("frFR", "WARRIOR", [0, 11, 0], ITEMS, {}, [], cvars={"brokenMetaLanguage": "deDE"})
        self.assertEqual(g.NS.LOCALE, "deDE")
        self.assertTrue(any("Berufe zeigt" in t for t in texts))

    def test_lang_command_saves_for_next_reload(self):
        _, chat, _, g = run("frFR", "WARRIOR", [0, 11, 0], ITEMS, {}, [], ["lang en"])
        self.assertEqual(g.CVARS["brokenMetaLanguage"], "enUS")
        self.assertEqual(g.NS.LOCALE, "frFR", "applied only after /reload")
        self.assertIn("/reload", chat[-1])


class SuiteTests(unittest.TestCase):
    """The 4-addon split: the HUB alone, dependency-free child addons, home cards, per-addon data."""

    def test_hub_alone_flags_children_missing(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [], modules=["BrokenMetaWeights"])
        self.assertIsNone(g.NS.Modules.BrokenDPS)
        self.assertEqual(g.LUA_EVAL('function(ns) return ns.AddonState("BrokenDPS") end')(g.NS), "missing")

    def test_each_child_loads_without_its_siblings(self):
        for solo in ("BrokenDPS", "BrokenCrafter", "BrokenCodex"):
            with self.subTest(solo=solo):
                _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [], modules=["BrokenMetaWeights", solo])
                self.assertTrue(g.NS.Modules[solo])

    def test_home_cards_reflect_loaded_and_missing_addons(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [], modules=["BrokenMetaWeights", "BrokenDPS"])
        states = {row.id: g.LUA_EVAL('function(ns, id) return ns.AddonState(id) end')(g.NS, row.id) for row in lua_list(g.NS.SUITE)}
        self.assertEqual(states["BrokenDPS"], "loaded")
        self.assertEqual(states["BrokenCrafter"], "missing")
        self.assertEqual(states["BrokenCodex"], "missing")

    def test_dps_bis_table_has_gear_per_spec(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        fury = lua_list(g.NS.BIS.warrior_fury)
        self.assertTrue(fury)
        self.assertTrue(all(row.slot and row.id for row in fury))

    def test_codex_raids_table_has_molten_core_bosses_and_loot(self):
        _, _, _, g = run("enUS", "WARRIOR", [0, 11, 0], ITEMS, {}, [])
        raids = lua_list(g.NS.RAIDS)
        self.assertTrue(raids)
        mc = next(r for r in raids if r.id == "molten-core")
        bosses = lua_list(mc.bosses)
        self.assertTrue(bosses)
        self.assertTrue(any(lua_list(b.drops) for b in bosses))

    def test_crafter_ah_and_craft_commands_registered(self):
        # /bmw ah and /bmw craft moved from the old Core.lua to BrokenCrafter; they must still exist
        # and run without error (the underlying functions are pcall-wrapped by the /bmw dispatcher).
        _, chat, _, g = run("enUS", "MAGE", [0, 0, 0], ITEMS, {}, [], ["ah", "craft"])
        self.assertFalse(any(m.startswith("options:") for m in chat))


if __name__ == "__main__":
    unittest.main()
