"""Runs the BrokenMetaWeights addon inside a mocked WoW API (Lua via lupa: `py -3.11 -m pip install lupa`).

Not a pass/fail suite yet: prints tooltips, hub pages, export, measurements and auction scans
for eyeballing after a change. Run: `py -3.11 wow_addon/tests/test_addon.py`.
"""
import sys
from pathlib import Path
import lupa

ADDON = Path(__file__).resolve().parent.parent / "BrokenMetaWeights"
MOCK = r'''
chat = {}
DEFAULT_CHAT_FRAME = { AddMessage = function(_, m) chat[#chat+1] = m end }
function GetLocale() return LOCALE end
function UnitClass() return "Guerrier", CLASS end
function UnitName() return "Test" end
function GetRealmName() return "Realm" end
function UnitLevel() return 20 end
function wipe(t) for k in pairs(t) do t[k] = nil end return t end
function GetNumTalentTabs() return 3 end
function GetTalentTabInfo(i) return "Tab"..i, "icon", TALENTS[i], "bg" end
Enum = nil; TooltipDataProcessor = nil
C_Item = { GetItemInfo = function(l) return _GII(l) end, GetItemStats = function(l) return _GIS(l) end }
ITEM_SPELL_TRIGGER_ONEQUIP = (LOCALE == "frFR") and "Équipé :" or "Equip:"
ITEMS = {}
function _GIS(link) return ITEMS[link].stats end
function _GII(link) local it = ITEMS[link]; return it.name,link,nil,nil,nil,nil,nil,nil,it.loc end
EQUIPPED = {}
function GetInventoryItemLink(_, slot) return EQUIPPED[slot] end
frames = {}
local function obj(name)
  local f = { lines = {}, scripts = {}, events = {}, added = {}, text = nil, shown = false }
  setmetatable(f, { __index = function(t, k) return function() end end })
  function f:RegisterEvent(e) self.events[e] = true end
  function f:SetScript(s, fn) self.scripts[s] = fn end
  function f:HookScript(s, fn) self.scripts[s] = fn end
  function f:ClearLines() self.lines = {} end
  function f:SetHyperlink(link) self.lines = { "name" } for _, l in ipairs(ITEMS[link].text or {}) do self.lines[#self.lines+1] = l end
    for i, l in ipairs(self.lines) do _G[name.."TextLeft"..i] = { GetText = function() return l end } end end
  function f:NumLines() return #self.lines end
  function f:AddLine(l) self.added[#self.added+1] = l end
  function f:SetText(t) self.text = t end
  function f:GetText() return self.text end
  function f:Show() self.shown = true end
  function f:Hide() self.shown = false end
  function f:IsShown() return self.shown end
  function f:SetShown(v) self.shown = v end
  function f:CreateFontString() local fs = obj(); fontstrings[#fontstrings+1] = fs; return fs end
  function f:CreateTexture() local t = obj(); function t:SetTexture(x) self.tex = x end; textures[#textures+1] = t; return t end
  return f
end
fontstrings = {}; textures = {}
C_ClassTalents = { GetActiveConfigID = function() return 7 end }
C_Traits = { GetNodeInfo = function(cfg, node) if node == 104773 then return { ranksPurchased = 5 } end if node == 104772 then return { ranksPurchased = 3 } end return { ranksPurchased = 0 } end }
function GetInventoryItemTexture(_, slot) return EQUIPPED[slot] and 135274 or nil end
function GetInventorySlotInfo(n) return 1, "slot-"..n end
function CreateFrame(kind, name)
  local f = obj(name)
  if name then _G[name] = f end
  frames[#frames+1] = f
  return f
end
math.atan2 = math.atan
TIMERS = {}
C_Timer = { After = function(d, f) TIMERS[#TIMERS + 1] = f end }
function flush() local n = 0 while #TIMERS > 0 and n < 1000 do local f = table.remove(TIMERS, 1) f() n = n + 1 end end
function time() return 1790000000 end
function GetManaRegen() return 0.8, 0.2 end
function UnitPowerMax() return 500 end
function GetDodgeChance() return 4.5 end
function UnitExists(u) return u == "pet" and HAS_PET end
function UnitCreatureFamily() return "Wolf" end
function UnitFactionGroup() return "Alliance" end
function GetCombatRatingBonusForCombatRatingValue(cr, v) return v / 3.2 end
function GetCursorPosition() return 500, 500 end
UIParent = {}; UISpecialFrames = {}; tinsert = table.insert; unpack = table.unpack; ChatFontNormal = {}
NUM_BAG_SLOTS = 4; date = os.date
BAGS = { [0] = {} }
C_Container = { GetContainerNumSlots = function(b) return BAGS[b] and #BAGS[b] or 0 end,
                GetContainerItemLink = function(b, s) return BAGS[b][s] end }
function GetBuildInfo() return "1.60.1", "70009", "Sep 2026", 16001 end
function UnitRace() return "Orc", "Orc" end
function UnitStat(_, i) return 20, 20 + i end
function UnitAttackPower() return 80, 12, 0 end
function GetSpellBonusDamage(s) return s == 3 and 25 or 10 end
function GetCritChance() return 5.1234 end
function GetSpellCritChance() return 3 end
function GetHitModifier() return 0 end
function UnitAttackSpeed() return 2.6, nil end
function UnitDamage() return 40, 55, nil, nil, 0, 0, 1 end
function GetCombatRating() return 0 end
C_UnitAuras = { GetAuraDataByIndex = function(u, i) if i <= 2 then return {} end end }
function strsplit(sep, s) local t = {} for part in (s..sep):gmatch("(.-)"..sep) do t[#t+1] = part end return table.unpack(t) end
GameTooltip = CreateFrame("GameTooltip", "GameTooltip")
Minimap = CreateFrame("Frame", "Minimap"); function Minimap:GetWidth() return 140 end; function Minimap:GetCenter() return 400, 400 end; function Minimap:GetEffectiveScale() return 1 end
function GameTooltip:GetItem() return "x", self.link end
SlashCmdList = {}
WorldFrame = {}
function fire(ev) for _, f in ipairs(frames) do if f.events[ev] then f.scripts.OnEvent(f, ev) end end end
function hover(link) GameTooltip.link = link; GameTooltip.added = {}; GameTooltip.scripts.OnTooltipSetItem(GameTooltip); return GameTooltip.added[1] end
'''


def run(locale, cls, talents, items, equipped, hovers, slash=(), bags=()):
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    g = lua.globals()
    g.LOCALE, g.CLASS = locale, cls
    lua.execute(MOCK)
    g.TALENTS = lua.table_from(talents)
    for link, it in items.items():
        g.ITEMS[link] = lua.table_from({"name": link, "loc": it["loc"],
                                        "stats": lua.table_from(it.get("stats", {})),
                                        "text": lua.table_from(it.get("text", []))})
    for slot, link in equipped.items():
        g.EQUIPPED[slot] = link
    ns = lua.table()
    for f in ("Weights.lua", "Core.lua", "Hub.lua", "Minimap.lua", "Collect.lua", "Auction.lua"):
        lua.execute((ADDON / f).read_text(encoding="utf-8"), "BrokenMetaWeights", ns) if False else \
            lua.eval("function(src, name, ns) return assert(load(src, name))('BrokenMetaWeights', ns) end")(
                (ADDON / f).read_text(encoding="utf-8"), f, ns)
    for i, l in enumerate(bags, 1):
        g.BAGS[0][i] = l
    g.fire("PLAYER_LOGIN")
    out = [g.hover(h) for h in hovers]
    for cmd in slash:
        g.SlashCmdList.BROKENMETAWEIGHTS(cmd)
    chat = [g.chat[i] for i in range(1, len(g.chat) + 1)]
    texts = list(lua.eval('function() local o = {} for _, fs in ipairs(fontstrings) do local t = rawget(fs, "text") if t and t ~= "" then o[#o+1] = t end end return o end')().values())
    g.NS = ns
    g.LUA_EVAL = lua.eval
    return out, chat, texts, g


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
