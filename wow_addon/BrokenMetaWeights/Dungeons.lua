-- Broken Meta : Dungeons.
--   Loot     the dungeon you are in (detected), or the one you pick: its bosses and quests, each item
--            with its DPS value for your spec, the gain if it is an upgrade, and a check when you own it;
--   History  what you looted in dungeons (green quality and above), with the date and the dungeon.
-- Data: ns.LOOT / ns.DUNGEONS (Data.lua, from the site's dungeon pages).
local ADDON, ns = ...
local IS_FR = ns.IS_FR

local T = ns.Localize("dungeons", {
  tab_loot = "Butin", tab_log = "Historique",
  pick = "Donjon : %s", here = "tu y es", quests = "Récompenses de quête : %s",
  none = "Pas de données de butin pour ce donjon.", owned = "possédé", level = "niv. %d",
  log_none = "Rien encore : le butin que tu ramasses en donjon (vert et mieux) s'affichera ici.",
  page = "Page %d/%d", summary = "%d objet(s), %d amélioration(s) pour ta spé.",
}, {
  tab_loot = "Loot", tab_log = "History",
  pick = "Dungeon: %s", here = "you are here", quests = "Quest rewards: %s",
  none = "No loot data for this dungeon.", owned = "owned", level = "lvl %d",
  log_none = "Nothing yet: the loot you pick up in dungeons (green and better) will show up here.",
  page = "Page %d/%d", summary = "%d item(s), %d upgrade(s) for your spec.",
})

if not ns.HubTab or not ns.DUNGEONS or not ns.LOOT then return end
local W, C, HEX = ns.Hub.W, ns.C, ns.HEX
local LOC = IS_FR and "frFR" or "enUS"
local CHECK = "|TInterface\\RaidFrame\\ReadyCheck-Ready:14:14:0:0|t"
local QUALITY = { [2] = "1eff00", [3] = "0070dd", [4] = "a335ee", [5] = "ff8000" }

local function dungeonName(i)
  local dg = ns.DUNGEONS[i]
  if not dg then return "?" end
  return (dg.name[LOC] or dg.name.enUS) .. (dg.levels ~= "" and (" (" .. dg.levels .. ")") or "")
end

-- The dungeon the player is in, matched on its name (French or English data), or nil.
function ns.CurrentDungeon()
  if not GetInstanceInfo then return nil end
  local name, kind = GetInstanceInfo()
  if kind ~= "party" or not name then return nil end
  for i, dg in ipairs(ns.DUNGEONS) do
    if dg.name.frFR == name or dg.name.enUS == name then return i end
  end
  return nil
end

local function owned(id)
  local n = (C_Item and C_Item.GetItemCount and C_Item.GetItemCount(id, true)) or (GetItemCount and GetItemCount(id, true)) or 0
  if n > 0 then return true end
  for slot = 1, 19 do
    local link = GetInventoryItemLink("player", slot)
    if link and tonumber(link:match("item:(%d+)")) == id then return true end
  end
  return false
end

local function itemLink(it)
  local name = (ns.GetItemInfo and select(1, ns.GetItemInfo(it.id))) or it.n
  return "|cff" .. (QUALITY[it.q] or "ffffff") .. "|Hitem:" .. it.id .. "::::::::|h[" .. name .. "]|h|r"
end

-- One dungeon's loot, grouped by boss (bosses in data order, quest rewards last):
-- { { header = text } or { it, value, gain, owned } }.
function ns.DungeonLoot(d)
  local groups, order, quests = {}, {}, {}
  for _, it in ipairs(ns.LOOT) do
    if it.d == d then
      local key = it.quest and ("Q:" .. (it.src or "?")) or (it.src or "?")
      if not groups[key] then
        groups[key] = {}
        if it.quest then quests[#quests + 1] = key else order[#order + 1] = key end
      end
      local e = { it = it, owned = owned(it.id) }
      local slots = it.slot and ns.SLOTS[it.slot]
      if slots and ns.scoreStats and ns.CanWearType(it.t) then
        e.value = ns.scoreStats(it.st, it.slot) or 0
        local worst
        for _, slot in ipairs(slots) do
          local eq = GetInventoryItemLink("player", slot)
          local ev = eq and ns.score(eq) or 0
          if not worst or ev < worst then worst = ev end
        end
        if e.value > 0 then e.gain = e.value - (worst or 0) end
      end
      table.insert(groups[key], e)
    end
  end
  local out, n, ups = {}, 0, 0
  for _, key in ipairs(order) do
    out[#out + 1] = { header = key }
    for _, e in ipairs(groups[key]) do out[#out + 1] = e; n = n + 1; if e.gain and e.gain > 0.005 then ups = ups + 1 end end
  end
  for _, key in ipairs(quests) do
    out[#out + 1] = { header = string.format(T.quests, key:sub(3)) }
    for _, e in ipairs(groups[key]) do out[#out + 1] = e; n = n + 1; if e.gain and e.gain > 0.005 then ups = ups + 1 end end
  end
  return out, n, ups
end

---------------------------------------------------------------------------------------------
-- Loot tab
---------------------------------------------------------------------------------------------
local ROWS = 16
do
  local refresh
  local page = ns.HubTab("dg", T.tab_loot, function() refresh() end)
  local selected, pageNo = nil, 1
  local pickBtn = ns.Button(page)
  pickBtn:SetSize(W - 32, 22)
  pickBtn:SetPoint("TOPLEFT", 4, -2)
  local summary = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  summary:SetPoint("TOPLEFT", 4, -30)
  summary:SetWidth(W - 40)
  summary:SetJustifyH("LEFT")
  ns.Hub.rows(page, ROWS, -52, 24, true)

  local picker = CreateFrame("Frame", nil, page, ns.BACKDROP_TEMPLATE)
  picker:SetPoint("TOPLEFT", pickBtn, "BOTTOMLEFT", 0, -4)
  picker:SetPoint("RIGHT", page, "RIGHT", -4, 0)
  picker:SetHeight(300)
  ns.Flat(picker, ns.C.bg, ns.C.borderBright)
  picker:SetFrameLevel((page:GetFrameLevel() or 1) + 20)
  picker:Hide()
  local pickRows = {}
  for k = 1, 24 do
    local b = ns.Button(picker, nil, "pill")
    b:SetSize((W - 50) / 2, 22)
    b:SetPoint("TOPLEFT", 6 + ((k - 1) % 2) * ((W - 50) / 2 + 6), -6 - math.floor((k - 1) / 2) * 24)
    b:Hide()
    pickRows[k] = b
  end
  pickBtn:SetScript("OnClick", function() picker:SetShown(not picker:IsShown()) end)

  local prev = ns.Button(page)
  prev:SetSize(28, 20)
  prev:SetPoint("BOTTOMLEFT", 4, 4)
  prev:SetText("<")
  prev:SetScript("OnClick", function() pageNo = pageNo - 1; refresh() end)
  local nxt = ns.Button(page)
  nxt:SetSize(28, 20)
  nxt:SetPoint("LEFT", prev, "RIGHT", 70, 0)
  nxt:SetText(">")
  nxt:SetScript("OnClick", function() pageNo = pageNo + 1; refresh() end)
  local pageText = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  pageText:SetPoint("LEFT", prev, "RIGHT", 8, 0)

  refresh = function()
    local here = ns.CurrentDungeon()
    local d = selected or here
    if not d then
      -- Nothing picked and not in a dungeon: the most rewarding one for this character.
      local by = ns.UpgradesByDungeon and ns.UpgradesByDungeon() or {}
      local best
      for i in ipairs(ns.DUNGEONS) do
        if by[i] and (not best or by[i].gain > by[best].gain) then best = i end
      end
      d = best or 1
    end
    pickBtn:SetText(string.format(T.pick, dungeonName(d)) .. (d == here and ("  · " .. T.here) or "") .. "  ↓")
    for k, b in ipairs(pickRows) do
      if ns.DUNGEONS[k] then
        b:SetText(dungeonName(k))
        if k == d then b:LockHighlight() else b:UnlockHighlight() end
        b:SetScript("OnClick", function() selected = k; pageNo = 1; picker:Hide(); refresh() end)
        b:Show()
      else
        b:Hide()
      end
    end
    local list, n, ups = ns.DungeonLoot(d)
    summary:SetText(#list > 0 and string.format(T.summary, n, ups) or ("|c" .. HEX.faint .. T.none .. "|r"))
    local pages = math.max(1, math.ceil(#list / ROWS))
    pageNo = math.min(math.max(pageNo, 1), pages)
    pageText:SetText(string.format(T.page, pageNo, pages))
    if pageNo > 1 then prev:Enable() else prev:Disable() end
    if pageNo < pages then nxt:Enable() else nxt:Disable() end
    local level = UnitLevel("player") or 1
    for i = 1, ROWS do
      local e = list[(pageNo - 1) * ROWS + i]
      if e and e.header then
        ns.Hub.setRow(page, i, "|c" .. HEX.gold .. e.header .. "|r")
      elseif e then
        local it = e.it
        local icon = (C_Item and C_Item.GetItemIconByID and C_Item.GetItemIconByID(it.id)) or (GetItemIcon and GetItemIcon(it.id))
        local left = itemLink(it) .. ((it.req or 0) > level and ("  |c" .. HEX.faint .. string.format(T.level, it.req) .. "|r") or "")
          .. (e.owned and ("  " .. CHECK .. "|c" .. HEX.faint .. T.owned .. "|r") or "")
        local right = ""
        if e.gain and e.gain > 0.005 then right = "|c" .. HEX.teal .. string.format("+%.2f DPS", e.gain) .. "|r"
        elseif e.value and e.value > 0 then right = "|c" .. HEX.faint .. string.format("%.2f DPS", e.value) .. "|r" end
        ns.Hub.setRow(page, i, left, right, { icon = icon, link = "item:" .. it.id })
      else
        ns.Hub.setRow(page, i)
      end
    end
  end
  -- Entering or leaving a dungeon: show that dungeon next time.
  local ev = CreateFrame("Frame")
  pcall(ev.RegisterEvent, ev, "PLAYER_ENTERING_WORLD")
  ev:SetScript("OnEvent", function() selected = nil; pageNo = 1 end)
end

---------------------------------------------------------------------------------------------
-- History tab: loot picked up in dungeons
---------------------------------------------------------------------------------------------
local LOG_MAX = 200
local function lootLog()
  BrokenMetaWeightsDB = BrokenMetaWeightsDB or {}
  BrokenMetaWeightsDB.lootLog = BrokenMetaWeightsDB.lootLog or {}
  return BrokenMetaWeightsDB.lootLog
end
ns.LootLog = lootLog

-- "You receive loot: %s." / "...: %sx%d." -> Lua patterns.
local function toPattern(fmt)
  if not fmt then return nil end
  return "^" .. fmt:gsub("([%^%$%(%)%.%[%]%*%+%-%?])", "%%%1"):gsub("%%s", "(.+)"):gsub("%%d", "(%%d+)") .. "$"
end
local SELF_MULTI, SELF_ONE -- built on first use, from the game's own loot message formats

function ns.RecordLoot(msg)
  if type(msg) ~= "string" then return end
  local d = ns.CurrentDungeon()
  if not d then return end
  SELF_MULTI = SELF_MULTI or toPattern(LOOT_ITEM_SELF_MULTIPLE)
  SELF_ONE = SELF_ONE or toPattern(LOOT_ITEM_SELF)
  local link, count = nil, 1
  if SELF_MULTI then link, count = msg:match(SELF_MULTI) end
  if not link and SELF_ONE then link = msg:match(SELF_ONE) end
  if not link or not link:find("item:", 1, true) then return end
  local quality = ns.GetItemInfo and select(3, ns.GetItemInfo(link))
  if quality and quality < 2 then return end
  local log = lootLog()
  table.insert(log, 1, { t = time(), d = d, link = link, n = tonumber(count) or 1 })
  while #log > LOG_MAX do table.remove(log) end
end

do
  local refresh
  local page, logIndex = ns.HubTab("dg", T.tab_log, function() refresh() end)
  local pageNo = 1
  local none = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  none:SetPoint("TOPLEFT", 4, -4)
  none:SetWidth(W - 40)
  none:SetJustifyH("LEFT")
  ns.Hub.rows(page, 18, -4, 24, true)
  local prev = ns.Button(page)
  prev:SetSize(28, 20)
  prev:SetPoint("BOTTOMLEFT", 4, 4)
  prev:SetText("<")
  prev:SetScript("OnClick", function() pageNo = pageNo - 1; refresh() end)
  local nxt = ns.Button(page)
  nxt:SetSize(28, 20)
  nxt:SetPoint("LEFT", prev, "RIGHT", 70, 0)
  nxt:SetText(">")
  nxt:SetScript("OnClick", function() pageNo = pageNo + 1; refresh() end)
  local pageText = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  pageText:SetPoint("LEFT", prev, "RIGHT", 8, 0)
  refresh = function()
    local log = lootLog()
    none:SetText(#log == 0 and ("|c" .. HEX.faint .. T.log_none .. "|r") or "")
    local pages = math.max(1, math.ceil(#log / 18))
    pageNo = math.min(math.max(pageNo, 1), pages)
    pageText:SetText(string.format(T.page, pageNo, pages))
    if pageNo > 1 then prev:Enable() else prev:Disable() end
    if pageNo < pages then nxt:Enable() else nxt:Disable() end
    for i = 1, 18 do
      local e = log[(pageNo - 1) * 18 + i]
      if e then
        local id = tonumber(e.link:match("item:(%d+)"))
        local icon = id and ((C_Item and C_Item.GetItemIconByID and C_Item.GetItemIconByID(id)) or (GetItemIcon and GetItemIcon(id)))
        ns.Hub.setRow(page, i, (e.n > 1 and (e.n .. "× ") or "") .. e.link .. "  |c" .. HEX.faint .. dungeonName(e.d) .. "|r",
          "|c" .. HEX.faint .. date("%d/%m %H:%M", e.t) .. "|r", { icon = icon, link = e.link })
      else
        ns.Hub.setRow(page, i)
      end
    end
  end
  local ev = CreateFrame("Frame")
  pcall(ev.RegisterEvent, ev, "CHAT_MSG_LOOT")
  ev:SetScript("OnEvent", function(_, _, msg) ns.RecordLoot(msg); ns.HubRefresh(logIndex) end)
end
