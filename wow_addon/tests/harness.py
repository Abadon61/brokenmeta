"""Mocked WoW API + addon loader shared by the addon tests (Lua via lupa: `py -3.11 -m pip install lupa`).

run() loads every addon file in .toc order into a fresh Lua state with the mocks below, fires
PLAYER_LOGIN, hovers the given items and runs the given slash commands. Used by test_units.py
(assertions) and test_addon.py (printed demo).
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
function _GIS(link) return ITEMS[link] and ITEMS[link].stats end
function _GII(link) local it = ITEMS[link]; if not it then return nil end; return it.name,link,nil,nil,it.minLevel or 0,nil,nil,nil,it.loc,nil,nil,it.classID,it.subID end
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
function GetTime() return 100 end
function IsInGuild() return true end
SENT = {}
C_ChatInfo = { RegisterAddonMessagePrefix = function() return true end, SendAddonMessage = function(p, m, c) SENT[#SENT+1] = c .. ":" .. m end }
function GetProfessions() return 1, nil end
function GetProfessionInfo(i) return "Alchemy", 1, 60, 75, 0, 0, 171 end
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
function strsplit(sep, s) local t = {} local esc = sep:gsub("%p", "%%%0") for part in (s..sep):gmatch("(.-)"..esc) do t[#t+1] = part end return table.unpack(t) end
GameTooltip = CreateFrame("GameTooltip", "GameTooltip")
Minimap = CreateFrame("Frame", "Minimap"); function Minimap:GetWidth() return 140 end; function Minimap:GetCenter() return 400, 400 end; function Minimap:GetEffectiveScale() return 1 end
function GameTooltip:GetItem() return "x", self.link end
SlashCmdList = {}
WorldFrame = {}
function fire(ev) for _, f in ipairs(frames) do if f.events[ev] then f.scripts.OnEvent(f, ev) end end end
function hover(link) GameTooltip.link = link; GameTooltip.added = {}; GameTooltip.scripts.OnTooltipSetItem(GameTooltip); return GameTooltip.added[1] end
'''


def toc_files():
    """The .lua files listed in the addon's .toc, in load order."""
    toc = (ADDON / "BrokenMetaWeights.toc").read_text(encoding="utf-8")
    return [l.strip() for l in toc.splitlines() if l.strip().endswith(".lua") and not l.startswith("#")]


def run(locale, cls, talents, items, equipped, hovers, slash=(), bags=()):
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    g = lua.globals()
    g.LOCALE, g.CLASS = locale, cls
    lua.execute(MOCK)
    g.TALENTS = lua.table_from(talents)
    for link, it in items.items():
        g.ITEMS[link] = lua.table_from({"name": link, "loc": it["loc"], "minLevel": it.get("minLevel", 0),
                                        "classID": it.get("classID"), "subID": it.get("subID"),
                                        "stats": lua.table_from(it.get("stats", {})),
                                        "text": lua.table_from(it.get("text", []))})
    for slot, link in equipped.items():
        g.EQUIPPED[slot] = link
    ns = lua.table()
    loader = lua.eval("function(src, name, ns) return assert(load(src, name))('BrokenMetaWeights', ns) end")
    for f in toc_files():
        loader((ADDON / f).read_text(encoding="utf-8"), f, ns)
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


