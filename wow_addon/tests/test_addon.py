"""Eyeball demo: prints tooltips, hub pages, export, measurements and scans. Assertions live in
test_units.py. Run: `py -3.11 wow_addon/tests/test_addon.py`."""
import lupa
from harness import *  # noqa: F401,F403

items = {
    "sword": {"loc": "INVTYPE_2HWEAPON", "stats": {"ITEM_MOD_STRENGTH_SHORT": 10, "ITEM_MOD_AGILITY_SHORT": 5}},
    "|cff1eff00|Hitem:1234:0:0:0:0:0:0:0:20|h[Sword]|h|r": {"loc": "INVTYPE_2HWEAPON", "stats": {"ITEM_MOD_STRENGTH_SHORT": 6}},
    "ring_crit": {"loc": "INVTYPE_FINGER", "stats": {"ITEM_MOD_CRIT_RATING_SHORT": 14}},
    "ring_old": {"loc": "INVTYPE_FINGER", "text": ["Equip: Improves your chance to get a critical strike by 1%."]},
    "cloth_sp": {"loc": "INVTYPE_CHEST", "text": ["Equip: Increases damage and healing done by magical spells and effects by up to 10."]},
    "cloth_fr": {"loc": "INVTYPE_CHEST", "text": ["Équipé : Augmente les dégâts et les soins produits par les sorts et effets magiques de 10 au maximum."]},
    "food": {"loc": ""},
}
SW = "|cff1eff00|Hitem:1234:0:0:0:0:0:0:0:20|h[Sword]|h|r"
out, chat, texts, g = run("enUS", "WARRIOR", [0, 11, 0], items, {16: SW, 11: "ring_old"},
                ["sword", SW, "ring_crit", "ring_old", "cloth_sp", "food"], ["", "list", "spec warrior_arms", "spec nope", "weights", "probe"],
                bags=["food", "sword", "ring_crit", "cloth_sp"])
for o in out: print("TT:", o)
for c in chat: print("CHAT:", c)
print("HUB shown:", g.BrokenMetaHub.shown)
for t in texts: print("UI:", t)
print("---- upgrades page")
g.fontstrings  # noqa
g.SlashCmdList.BROKENMETAWEIGHTS("")  # close
g.SlashCmdList.BROKENMETAWEIGHTS("")  # reopen on page 1
print("EXPORT:"); print(g.BrokenMetaHub and __import__("sys").stdout.write(""))
print(g.eval if False else "")
print()
out, chat, texts, g = run("frFR", "MAGE", [0, 0, 12], items, {}, ["cloth_sp", "cloth_fr", "ring_old", "sword"], ["weights", ""])
for o in out: print("TT:", o)
for c in chat: print("CHAT:", c)
for t in texts: print("UI:", t)

print("==== upgrades + export (warrior)")
out, chat, texts, g = run("enUS", "WARRIOR", [0, 11, 0], items, {16: SW, 11: "ring_old"}, [], [], bags=["food", "sword", "ring_crit", "cloth_sp"])
g.SlashCmdList.BROKENMETAWEIGHTS("")
g.NS.OnDataChanged()
tabs_click = None
print(g.NS.BuildExport())
print("==== upgrades page")
g.fontstrings_before = None
lua_click = g.eval if hasattr(g, "eval") else None
import lupa as _l
g.LUA_EVAL('function(label) for _, f in ipairs(frames) do if rawget(f, "text") == label and f.scripts.OnClick then f.scripts.OnClick() end end end')("Upgrades")
for t in g.LUA_EVAL('function() local o = {} for _, fs in ipairs(fontstrings) do local t = rawget(fs, "text") if t and t ~= "" then o[#o+1] = t end end return o end')().values():
    if "DPS" in t or "upgrade" in t.lower() or t in ("sword","ring_crit","cloth_sp","food"): print("UI:", t)
print("==== shaman talents + commands + export")
out, chat, texts, g = run("frFR", "SHAMAN", [0, 0, 0], items, {16: SW}, [], ["probe"], bags=[])
for c in chat[-2:]: print("CHAT:", c)
click = g.LUA_EVAL('function(label) for _, f in ipairs(frames) do if rawget(f, "text") == label and f.scripts.OnClick then f.scripts.OnClick() end end end')
click("Commandes")
for t in g.LUA_EVAL('function() local o = {} for _, fs in ipairs(fontstrings) do local t = rawget(fs, "text") if t and t:find("bmw") then o[#o+1] = t end end return o end')().values(): print("CMD:", t)
click("Personnage")
print("icons:", list(g.LUA_EVAL('function() local o = {} for _, t in ipairs(textures) do if rawget(t, "tex") then o[#o+1] = tostring(t.tex) end end return o end')().values())[:6])
print([l for l in g.NS.BuildExport().split("\n") if l.startswith(("spec","talent"))])
print("==== minimap")
out, chat, texts, g = run("frFR", "SHAMAN", [0, 0, 0], items, {}, [], ["minimap", "minimap"], bags=[])
print("CHAT:", chat[-2:])
btn = g.BrokenMetaMinimapButton
print("shown:", btn.shown, "DB:", dict(g.BrokenMetaWeightsDB.items()).keys())
btn.scripts.OnClick(btn, "LeftButton"); print("hub after left click:", g.BrokenMetaHub.shown)
btn.scripts.OnClick(btn, "RightButton"); print("hub after right click:", g.BrokenMetaHub.shown)
btn.scripts.OnDragStart(btn); btn.scripts.OnUpdate(btn); print("angle:", g.BrokenMetaWeightsDB.minimapAngle)
g.BrokenMeta_OnCompartmentClick(None, "LeftButton"); print("compartment toggle:", g.BrokenMetaHub.shown)

print("==== collect + auction (modern API)")
out, chat, texts, g = run("frFR", "HUNTER", [0, 5, 0], items, {}, [], [], bags=[])
L = g.LUA_EVAL
L('function() HAS_PET = true end')()
g.flush()
d = g.NS.Data()
print("meas:", [ (r.k, r.level, r.crit_melee, r.regen_base, r.pet_level if r.k == "pet" else None) for r in d.meas.values()])
g.NS.SnapshotAll(); g.flush()
print("after re-snapshot (dedup) count:", len(d.meas))
# modern auction house
L('''function()
  LISTINGS = { {2, 500, 2589}, {1, 200, 2589}, {5, 0, 2592}, {3, 900, 2592}, {1, 50, 765} }
  C_AuctionHouse = {
    ReplicateItems = function() for _, f in ipairs(frames) do if f.events.REPLICATE_ITEM_LIST_UPDATE then f.scripts.OnEvent(f, "REPLICATE_ITEM_LIST_UPDATE") end end end,
    GetNumReplicateItems = function() return #LISTINGS end,
    GetReplicateItemInfo = function(i) local l = LISTINGS[i + 1]; return "n", 1, l[1], 1, true, 1, 0, 0, 0, l[2], 0, false, nil, "SELLER", "SELLER-X", 0, l[3], true end,
  }
  AuctionHouseFrame = CreateFrame("Frame", "AuctionHouseFrame")
end''')()
for f in L('function() return frames end')().values():
    if f.events and f.events["AUCTION_HOUSE_SHOW"]:
        f.scripts.OnEvent(f, "AUCTION_HOUSE_SHOW")
g.flush()
btn = g.BrokenMetaAuctionScanButton
print("button:", btn.text, btn.shown)
btn.scripts.OnClick(btn); g.flush()
print("chat:", g.chat[len(g.chat)])
scan = d.ah[len(d.ah)]
print("scan:", scan.realm, scan.faction, scan.mode, scan.listings, {k: list(v.values()) for k, v in scan.prices.items()})
print("seller stored anywhere?", "SELLER" in repr([list(v.values()) for v in scan.prices.values()]))

print("==== auction (classic getAll API)")
out, chat, texts, g = run("enUS", "MAGE", [0, 0, 0], items, {}, [], [], bags=[])
L = g.LUA_EVAL
L('''function()
  CL = { {1, 1000, 100}, {4, 400, 100} }
  function CanSendAuctionQuery() return true, true end
  function QueryAuctionItems(...) QARGS = {...}; for _, f in ipairs(frames) do if f.events.AUCTION_ITEM_LIST_UPDATE then f.scripts.OnEvent(f, "AUCTION_ITEM_LIST_UPDATE") end end end
  function GetNumAuctionItems() return #CL end
  function GetAuctionItemInfo(_, i) local l = CL[i]; return "n", 1, l[1], 1, true, 1, "", 0, 0, l[2], 0, false, nil, "S", "S", 0, l[3], true end
  AuctionFrame = CreateFrame("Frame", "AuctionFrame")
end''')()
print("mode:", g.NS.AuctionMode())
for f in L("function() return frames end")().values():
    if f.events and f.events["AUCTION_HOUSE_SHOW"]:
        f.scripts.OnEvent(f, "AUCTION_HOUSE_SHOW")
g.flush(); g.BrokenMetaAuctionScanButton.scripts.OnClick(); g.flush()
d = g.NS.Data(); s = d.ah[len(d.ah)]
print("getAll flag:", L('function() return QARGS[7] end')(), "prices:", {k: list(v.values()) for k, v in s.prices.items()})
print("==== share + data tab")
g.SlashCmdList.BROKENMETAWEIGHTS("share on"); print(g.chat[len(g.chat)], g.BrokenMetaWeightsDB.share)
g.SlashCmdList.BROKENMETAWEIGHTS("share off"); print(g.BrokenMetaWeightsDB.share)
g.SlashCmdList.BROKENMETAWEIGHTS("")
L('function(label) for _, f in ipairs(frames) do if rawget(f, "text") == label and f.scripts.OnClick then f.scripts.OnClick() end end end')("Data")
for t in L('function() local o = {} for _, fs in ipairs(fontstrings) do local t = rawget(fs, "text") if t and (t:find("scan") or t:find("measure") or t:find("Scan")) then o[#o+1] = t end end return o end')().values():
    print("UI:", t)
print("==== scan refused when auction house closed + /bmw ah")
for f in L("function() return frames end")().values():
    if f.events and f.events["AUCTION_HOUSE_CLOSED"]:
        f.scripts.OnEvent(f, "AUCTION_HOUSE_CLOSED")
g.SlashCmdList.BROKENMETAWEIGHTS("ah"); print(g.chat[len(g.chat)])
for f in L("function() return frames end")().values():
    if f.events and f.events["AUCTION_HOUSE_SHOW"]:
        f.scripts.OnEvent(f, "AUCTION_HOUSE_SHOW")
g.flush()
n = len(g.NS.Data().ah)
g.SlashCmdList.BROKENMETAWEIGHTS("ah"); g.flush()
print("scans before/after /bmw ah:", n, len(g.NS.Data().ah), "| button shown:", g.BrokenMetaAuctionScanButton.shown)
print("==== guide tab + german client")
for loc in ("frFR", "deDE", "esES"):
    out, chat, texts, g = run(loc, "SHAMAN", [0, 11, 0], items, {}, [], [""], bags=[])
    L = g.LUA_EVAL
    L('function(label) for _, f in ipairs(frames) do if rawget(f, "text") == label and f.scripts.OnClick then f.scripts.OnClick() end end end')("Guide")
    ui = [t for t in L('function() local o = {} for _, fs in ipairs(fontstrings) do local t = rawget(fs, "text") if t and t ~= "" then o[#o+1] = t end end return o end')().values()]
    print(loc, "| title:", [t for t in ui if "Hub" in t][:1], "| guide:", [t for t in ui if "%" not in t and ("guide" in t.lower() or "guía" in t.lower() or "talent" in t.lower())][:2], "| prof:", [t for t in ui if "75" in t][:1])
    L('function() for _, f in ipairs(frames) do if rawget(f, "text") and f.scripts.OnClick and (rawget(f, "text"):find("guide") or rawget(f, "text"):find("Guide") or rawget(f, "text"):find("guía")) and not rawget(f, "text"):find("^Guide$") and not rawget(f, "text"):find("^Guía$") then f.scripts.OnClick(); return end end end')()
    print("   copy box:", [rawget for rawget in []] or L('function() return BrokenMetaShareCopy and BrokenMetaShareCopy.shown end')(), L('function() for _, f in ipairs(frames) do local t = rawget(f, "text") if t and t:find("^https://") then return t end end end')())
print("welcome + version sent:", list(g.SENT.values()) if hasattr(g, "SENT") else None)
