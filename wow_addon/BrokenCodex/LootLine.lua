-- BrokenCodex: where an item drops (dungeon and boss, or the quest that rewards it), in its tooltip.
local ADDON = ...
local ns = BrokenMetaNS
local IS_FR = ns.IS_FR
local L = ns.L

local LOOT_BY_ID = {}
for _, it in ipairs(ns.LOOT or {}) do LOOT_BY_ID[it.id] = it end

local function lootLine(link)
  local id = tonumber(link:match("item:(%d+)"))
  local it = id and LOOT_BY_ID[id]
  if not it then return nil end
  local dg = ns.DUNGEONS and ns.DUNGEONS[it.d]
  local dname = dg and (dg.name[IS_FR and "frFR" or "enUS"] or dg.name.enUS) or "?"
  if it.quest then return string.format(L.loot_quest, dname) end
  return string.format(L.loot_drop, dname, it.src or "?")
end

ns.AddTooltipHandler(function(tt, link)
  if ns.Option and not ns.Option("tooltip_loot") then return false end
  local src = lootLine(link)
  if not src then return false end
  tt:AddLine("|cff888888" .. src .. "|r")
  return true
end, 2)
