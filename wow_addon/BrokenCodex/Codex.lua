-- Broken Meta : Dungeons.
--   Loot     the dungeon you are in (detected), or the one you pick: its bosses and quests, each item
--            with its DPS value for your spec, the gain if it is an upgrade, and a check when you own it;
--   History  what you looted in dungeons (green quality and above), with the date and the dungeon.
-- Data: ns.LOOT / ns.DUNGEONS (Data.lua, from the site's dungeon pages).
local ADDON = ...
local ns = BrokenMetaNS -- Broken Meta : HUB's namespace, shared by the suite
ns.Modules.BrokenCodex = true
local IS_FR = ns.IS_FR

local T = ns.Localize("dungeons", {
  tab_loot = "Donjons", tab_log = "Historique", tab_raids = "Raids",
  back = "Tous les donjons", boss_pick = "Boss : %s", boss_other = "Autres sources (monstres, quêtes)", boss_n = "Boss %d sur %d",
  vs_equipped = "face à ton équipement", obj_short = "%d obj.", sum_useful = "en prenant les %d objet(s) utile(s)",
  sum_none = "aucune amélioration ici", quest_reward = "récompense de quête", level_range = "Niv. %s", boss_quests = "Quêtes", n_quests = "%d quête(s)",
  quest_giver = "Donné par %s", quest_item = "Débute avec %s", quest_at = "%s (%.1f, %.1f)",
  none_boss = "Aucun objet d'équipement dans les données pour cette source.",
  pick = "Donjon : %s", here = "tu y es", quests = "Récompenses de quête : %s",
  none = "Pas de données de butin pour ce donjon.", owned = "possédé", level = "niv. %d",
  log_none = "Rien encore : le butin que tu ramasses en donjon (vert et mieux) s'affichera ici.",
  page = "Page %d/%d", summary = "%d objet(s), %d amélioration(s) pour ta spé.",
  back_raids = "Tous les raids", raid_pick = "Raid : %s", raid_info = "Niv. %s · %s joueurs · %s",
  raid_attune = "Accès : %s (niv. requis %s)", other_loot = "Autre butin du raid",
  raid_none = "Pas encore de données de raid.",
}, {
  tab_loot = "Dungeons", tab_log = "History", tab_raids = "Raids",
  back = "All dungeons", boss_pick = "Boss: %s", boss_other = "Other sources (monsters, quests)", boss_n = "Boss %d of %d",
  vs_equipped = "vs. your equipment", obj_short = "%d items", sum_useful = "taking the %d useful item(s)",
  sum_none = "no upgrade here", quest_reward = "quest reward", level_range = "Lvl %s", boss_quests = "Quests", n_quests = "%d quest(s)",
  quest_giver = "Given by %s", quest_item = "Starts with %s", quest_at = "%s (%.1f, %.1f)",
  none_boss = "No gear in the data for this source.",
  pick = "Dungeon: %s", here = "you are here", quests = "Quest rewards: %s",
  none = "No loot data for this dungeon.", owned = "owned", level = "lvl %d",
  log_none = "Nothing yet: the loot you pick up in dungeons (green and better) will show up here.",
  page = "Page %d/%d", summary = "%d item(s), %d upgrade(s) for your spec.",
  back_raids = "All raids", raid_pick = "Raid: %s", raid_info = "Lvl %s · %s players · %s",
  raid_attune = "Attunement: %s (requires lvl %s)", other_loot = "Other raid loot",
  raid_none = "No raid data yet.",
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
ns.HubSection("codex", ns.HubTexts.sec_codex, 40, "BrokenCodex")

---------------------------------------------------------------------------------------------
-- Dungeons tab: the dungeons as picture cards, then one dungeon (dungeon picker, boss picker),
-- then one boss: its head, its name and its loot with big icons.
---------------------------------------------------------------------------------------------
local function colorOf(hex)
  return tonumber(hex:sub(1, 2), 16) / 255, tonumber(hex:sub(3, 4), 16) / 255, tonumber(hex:sub(5, 6), 16) / 255, 1
end

-- A loot row of the data with what the character makes of it: DPS value for the spec, gain over
-- what is worn, and whether it is owned.
local function entryFor(it)
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
  return e
end

-- Upgrades first (biggest gain first), then the best quality, then the name.
local function byGain(a, b)
  local ga, gb = (a.gain and a.gain > 0.005) and a.gain or 0, (b.gain and b.gain > 0.005) and b.gain or 0
  if ga ~= gb then return ga > gb end
  if (a.it.q or 0) ~= (b.it.q or 0) then return (a.it.q or 0) > (b.it.q or 0) end
  return a.it.n < b.it.n
end

-- The bosses of a dungeon (the game's encounters in order, then rare mobs that drop loot) with
-- their items, then "Quests" (one group per quest: a header row with the giver, then its rewards) and
-- the loot of other monsters: { { name, npc, items = { entry }, rows = { header or entry } }, ... }.
function ns.DungeonBosses(d)
  local art = ns.DUNGEON_ART and ns.DUNGEON_ART[d]
  local list, byName = {}, {}
  for _, b in ipairs(art and art.bosses or {}) do
    local e = { name = b.name[LOC] or b.name.enUS, npc = b.npc, items = {} }
    list[#list + 1] = e
    byName[b.name.enUS] = e
  end
  local others = { name = T.boss_other, other = true, items = {} }
  local questEntry = { name = T.boss_quests, quest = true, items = {} }
  local byQuest, questOrder = {}, {}
  for _, it in ipairs(ns.LOOT) do
    if it.d == d then
      local entry = entryFor(it)
      if it.quest then
        local key = it.src or "?"
        if not byQuest[key] then byQuest[key] = {}; questOrder[#questOrder + 1] = key end
        table.insert(byQuest[key], entry)
        table.insert(questEntry.items, entry)
      else
        local e = byName[it.src or ""]
        if not e then entry.from = it.src end
        table.insert((e or others).items, entry)
      end
    end
  end
  for _, e in ipairs(list) do table.sort(e.items, byGain); e.rows = e.items end
  table.sort(others.items, byGain)
  others.rows = others.items
  -- Quests: a header row (name, giver, where), then the rewards indented under it.
  table.sort(questOrder)
  questEntry.rows = {}
  for _, key in ipairs(questOrder) do
    local info = art and art.quests and art.quests[key]
    table.sort(byQuest[key], byGain)
    local h = { header = true, name = info and (info.name[LOC] or info.name.enUS) or key }
    local g = info and info.giver
    if g then
      local who = g.name[LOC] or g.name.enUS
      if g.kind == "item" then
        h.detail = string.format(T.quest_item, who)
      else
        h.detail = string.format(T.quest_giver, who)
        if g.zone and g.x then h.detail = h.detail .. "  ·  " .. string.format(T.quest_at, g.zone[LOC] or g.zone.enUS, g.x, g.y) end
      end
    end
    table.insert(questEntry.rows, h)
    for _, e in ipairs(byQuest[key]) do e.indent = true; table.insert(questEntry.rows, e) end
  end
  if #questEntry.items > 0 then list[#list + 1] = questEntry; questEntry.n = #questOrder end
  if #others.items > 0 then list[#list + 1] = others end
  return list
end

-- The dungeon's picture: the game's own loading screen (a FileDataID of the client).
local function dungeonImage(d)
  local art = ns.DUNGEON_ART and ns.DUNGEON_ART[d]
  return art and art.image ~= 0 and art.image or nil
end

-- A list of choices in a framed grid under a button (closes on a click anywhere else):
-- picker:Fill(labels, current, pick); picker:Toggle().
local function newPicker(page, anchor, cols, width)
  local f = CreateFrame("Frame", nil, page, ns.BACKDROP_TEMPLATE)
  local catcher = CreateFrame("Button", nil, page)
  local btns = {}
  local colW = math.floor((width - 16) / cols)
  catcher:SetAllPoints(UIParent)
  catcher:SetFrameStrata("DIALOG")
  catcher:SetScript("OnClick", function() f:Hide(); catcher:Hide() end)
  catcher:Hide()
  f:SetPoint("TOPLEFT", anchor, "BOTTOMLEFT", 0, -4)
  f:SetWidth(width)
  f:SetFrameStrata("DIALOG")
  f:SetFrameLevel((catcher:GetFrameLevel() or 0) + 5)
  f:EnableMouse(true)
  ns.Flat(f, ns.C.bg, ns.C.borderBright)
  f:Hide()
  page:HookScript("OnHide", function() f:Hide(); catcher:Hide() end)
  function f:Fill(labels, current, pick)
    for k, text in ipairs(labels) do
      local b = btns[k]
      if not b then
        b = ns.Button(f, nil, "pill")
        b:SetSize(colW - 4, 22)
        b:SetPoint("TOPLEFT", 6 + ((k - 1) % cols) * colW, -6 - math.floor((k - 1) / cols) * 24)
        btns[k] = b
      end
      b:SetText(text)
      if k == current then b:LockHighlight() else b:UnlockHighlight() end
      b:SetScript("OnClick", function() f:Hide(); catcher:Hide(); pick(k) end)
      b:Show()
    end
    for k = #labels + 1, #btns do btns[k]:Hide() end
    f:SetHeight(math.ceil(#labels / cols) * 24 + 12)
  end
  function f:Toggle()
    if f:IsShown() then f:Hide(); catcher:Hide() else catcher:Show(); f:Show() end
  end
  return f
end

-- A button whose label sits on the left (list rows of the boss list).
local function leftLabel(b, x, width)
  local fs = b.GetFontString and b:GetFontString()
  if fs then
    fs:ClearAllPoints()
    fs:SetPoint("LEFT", x, 0)
    fs:SetWidth(width)
    fs:SetJustifyH("LEFT")
    if fs.SetWordWrap then fs:SetWordWrap(false) end
  end
end

-- Cell of the loot grid: an item (icon in a quality frame, name, slot and type, what it adds over what
-- is worn with a meter) or a quest header (yellow exclamation mark, name, who gives it and where).
local function makeCell(parent, w, h)
  local c = CreateFrame("Button", nil, parent, ns.BACKDROP_TEMPLATE)
  c:SetSize(w, h)
  ns.Flat(c)
  c.frame = CreateFrame("Frame", nil, c, ns.BACKDROP_TEMPLATE)
  c.frame:SetSize(54, 54)
  c.frame:SetPoint("TOPLEFT", 10, -10)
  ns.Flat(c.frame, ns.C.bg, ns.C.border)
  c.icon = c.frame:CreateTexture(nil, "ARTWORK")
  c.icon:SetPoint("TOPLEFT", 1, -1)
  c.icon:SetPoint("BOTTOMRIGHT", -1, 1)
  c.name = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  c.name:SetPoint("TOPLEFT", 76, -9)
  c.name:SetJustifyH("LEFT")
  c.name:SetWordWrap(false)
  c.sub = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  c.sub:SetPoint("TOPLEFT", 76, -29)
  c.sub:SetJustifyH("LEFT")
  c.sub:SetWordWrap(false)
  c.delta = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  c.delta:SetPoint("TOPLEFT", 76, -47)
  c.delta:SetJustifyH("LEFT")
  c.delta:SetWordWrap(false)
  c.meterBg = c:CreateTexture(nil, "ARTWORK")
  c.meterBg:SetColorTexture(unpack(ns.C.border))
  c.meterBg:SetHeight(5)
  c.meterBg:SetPoint("BOTTOMLEFT", 76, 7)
  c.meterFill = c:CreateTexture(nil, "OVERLAY")
  c.meterFill:SetHeight(5)
  c.meterFill:SetPoint("BOTTOMLEFT", 76, 7)
  c.accent = c:CreateTexture(nil, "OVERLAY")
  c.accent:SetHeight(2)
  c.accent:SetPoint("BOTTOMLEFT", 1, 1)
  c.accent:SetPoint("BOTTOMRIGHT", -1, 1)
  c:SetScript("OnEnter", function(self)
    if self.SetBackdropColor then self:SetBackdropColor(unpack(ns.C.rowHover)) end
    if self.id then
      GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
      GameTooltip:SetHyperlink("item:" .. self.id)
      GameTooltip:Show()
    end
  end)
  c:SetScript("OnLeave", function(self)
    if self.SetBackdropColor then self:SetBackdropColor(unpack(ns.C.row)) end
    GameTooltip:Hide()
  end)
  c:SetScript("OnClick", function(self)
    if self.id and HandleModifiedItemClick then HandleModifiedItemClick(self.link) end
  end)
  function c:SetItem(e, level, maxGain)
    local it = e.it
    self.id = it.id
    self:SetWidth(self.cellW)
    self.name:SetWidth(self.cellW - 90)
    self.sub:SetWidth(self.cellW - 90)
    self.delta:SetWidth(self.cellW - 90)
    self.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    local name = (ns.GetItemInfo and select(1, ns.GetItemInfo(it.id))) or it.n
    local hex = QUALITY[it.q] or "ffffff"
    self.link = "|cff" .. hex .. "|Hitem:" .. it.id .. "::::::::|h[" .. name .. "]|h|r"
    self.name:SetText("|cff" .. hex .. name .. "|r" .. (e.owned and ("  " .. CHECK) or ""))
    local icon = (C_Item and C_Item.GetItemIconByID and C_Item.GetItemIconByID(it.id)) or (GetItemIcon and GetItemIcon(it.id))
    self.icon:SetTexture(icon or "Interface\\Icons\\INV_Misc_QuestionMark")
    local q = { colorOf(hex) }
    ns.FlatBorder(self.frame, q)
    self.accent:SetColorTexture(q[1], q[2], q[3], 0.85)
    self.accent:Show()
    local parts = {}
    local slot = it.slot and _G[it.slot]
    if slot then parts[#parts + 1] = slot end
    local kind = (ns.GetItemInfo and select(7, ns.GetItemInfo(it.id))) or it.t
    if kind and kind ~= slot then parts[#parts + 1] = kind end
    if (it.req or 0) > level then parts[#parts + 1] = "|cffff9900" .. string.format(T.level, it.req) .. "|r|c" .. HEX.faint end
    if e.owned then parts[#parts + 1] = T.owned end
    if e.from then parts[#parts + 1] = e.from end
    if e.indent then parts[#parts + 1] = T.quest_reward end
    self.sub:SetText("|c" .. HEX.faint .. table.concat(parts, "  ·  ") .. "|r")
    local fill, color = 0, nil
    if e.gain and e.gain > 0.005 then
      self.delta:SetText("|c" .. HEX.teal .. string.format("+%.2f DPS", e.gain) .. "|r |c" .. HEX.faint .. T.vs_equipped .. "|r")
      fill, color = math.min(1, e.gain / math.max(maxGain, 0.01)), ns.C.teal
    elseif e.gain and e.gain < -0.005 then
      self.delta:SetText("|cffff6b6b" .. string.format("%.2f DPS", e.gain) .. "|r |c" .. HEX.faint .. T.vs_equipped .. "|r")
      fill, color = math.min(1, -e.gain / math.max(maxGain, 0.01)), { 1, 0.42, 0.42, 1 }
    elseif e.value and e.value > 0 then
      self.delta:SetText("|c" .. HEX.faint .. string.format("%.2f DPS", e.value) .. "  " .. T.vs_equipped .. "|r")
    else
      self.delta:SetText("")
    end
    self.meterBg:SetWidth(self.cellW - 90)
    self.meterBg:Show()
    if color then
      self.meterFill:SetColorTexture(unpack(color))
      self.meterFill:SetWidth(math.max(3, math.floor((self.cellW - 90) * fill)))
      self.meterFill:Show()
    else
      self.meterFill:Hide()
    end
    self:Show()
  end
  function c:SetHeader(e, width)
    self.id = nil
    self:SetWidth(width)
    self.name:SetWidth(width - 90)
    self.sub:SetWidth(width - 90)
    self.icon:SetTexture("Interface\\GossipFrame\\AvailableQuestIcon")
    self.icon:SetTexCoord(0, 1, 0, 1)
    ns.FlatBorder(self.frame, { colorOf("ffd100") })
    self.name:SetText("|cffffd100" .. e.name .. "|r")
    self.sub:SetText("|c" .. HEX.faint .. (e.detail or "") .. "|r")
    self.delta:SetText("")
    self.meterBg:Hide(); self.meterFill:Hide()
    self.accent:SetColorTexture(1, 0.82, 0, 0.85)
    self.accent:Show()
    self:Show()
  end
  return c
end

-- The browser of an instance family (dungeons, raids), in three columns like the window itself:
--   all the instances as picture cards; then one instance: its boss list on the left, the boss on the
--   right (picture banner with the head of the boss, then its loot as cards with what each adds).
-- cfg gives the data:
--   list, name(i), label(i), levels(i), image(i), wide(i), bosses(i), here(), pickText, best() (optional),
--   tip(i) (optional: lines of the instance button's tooltip), empty (text when the list is empty).
-- Returns the refresh function of the page.
local function buildBrowser(page, cfg)
  local refresh
  local selected, bossIdx, gridPage, bossPage, itemPage = nil, nil, 1, 1, 1 -- selected: nil auto, false list, or an index
  local single = #cfg.list == 1
  local MID_W = 262
  local RIGHT_W = W - 24 - MID_W - 12
  local CARD_W, CARD_H, GRID_PER = math.floor((W - 32 - 16) / 3), 108, 15
  local CELL_W, CELL_H, CELL_ROWS = math.floor((RIGHT_W - 8) / 2), 84, 5
  local BOSS_H, BOSS_ROWS = 34, 14
  local BANNER_H = 150

  local function newPager(parent, x, y)
    local prev = ns.Button(parent)
    prev:SetSize(28, 22)
    prev:SetPoint("BOTTOMLEFT", x, y)
    prev:SetText("<")
    local nxt = ns.Button(parent)
    nxt:SetSize(28, 22)
    nxt:SetPoint("LEFT", prev, "RIGHT", 70, 0)
    nxt:SetText(">")
    local text = parent:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
    text:SetPoint("LEFT", prev, "RIGHT", 8, 0)
    return function(n, pages, step)
      text:SetText(string.format(T.page, n, pages))
      if n > 1 then prev:Enable() else prev:Disable() end
      if n < pages then nxt:Enable() else nxt:Disable() end
      prev:SetScript("OnClick", function() step(-1) end)
      nxt:SetScript("OnClick", function() step(1) end)
    end
  end

  ---------------------------------------------------------------- the instances
  local grid = CreateFrame("Frame", nil, page)
  grid:SetAllPoints()
  local gridPager = newPager(grid, 4, 4)
  local cards = {}
  for k = 1, GRID_PER do
    local c = CreateFrame("Button", nil, grid, ns.BACKDROP_TEMPLATE)
    c:SetSize(CARD_W, CARD_H)
    c:SetPoint("TOPLEFT", 4 + ((k - 1) % 3) * (CARD_W + 8), -4 - math.floor((k - 1) / 3) * (CARD_H + 8))
    ns.Flat(c)
    c.img = c:CreateTexture(nil, "ARTWORK")
    c.img:SetPoint("TOPLEFT", 1, -1)
    c.img:SetPoint("BOTTOMRIGHT", -1, 1)
    c.strip = c:CreateTexture(nil, "OVERLAY")
    c.strip:SetColorTexture(0, 0, 0, 0.72)
    c.strip:SetHeight(32)
    c.strip:SetPoint("BOTTOMLEFT", 1, 1)
    c.strip:SetPoint("BOTTOMRIGHT", -1, 1)
    c.name = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
    c.name:SetPoint("BOTTOMLEFT", 10, 8)
    c.name:SetWidth(CARD_W - 100)
    c.name:SetJustifyH("LEFT")
    c.name:SetWordWrap(false)
    c.levels = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
    c.levels:SetPoint("BOTTOMRIGHT", -10, 9)
    c.levels:SetJustifyH("RIGHT")
    c:SetScript("OnEnter", function(self) if self.SetBackdropColor then self:SetBackdropColor(unpack(ns.C.rowHover)) end end)
    c:SetScript("OnLeave", function(self) if self.SetBackdropColor then self:SetBackdropColor(unpack(ns.C.row)) end end)
    c:Hide()
    cards[k] = c
  end
  local noData = grid:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  noData:SetPoint("TOPLEFT", 8, -8)
  noData:SetWidth(W - 48)
  noData:SetJustifyH("LEFT")

  -- A classic loading screen is a square 2048 file: wood frame, the game's logo (down to 23% of the
  -- height) over the picture (18% to 80%), wood frame. Keep a band just under the logo, in the
  -- proportions of the frame it fills (aspect = width / height). Forever's own two are 16:9 with the
  -- picture between grey bars.
  local function crop(tex, i, aspect)
    local img = cfg.image(i)
    tex:SetTexture(img or "Interface\\Icons\\INV_Misc_Map_01")
    if not img then tex:SetTexCoord(0, 1, 0, 1); return end
    if cfg.wide(i) then
      local f = math.min(0.66, 1.78 / aspect)
      local mid = 0.5
      tex:SetTexCoord(0, 1, mid - f / 2, mid + f / 2)
    else
      local f = 1 / aspect
      local top = 0.265
      tex:SetTexCoord(0, 1, top, top + f)
    end
  end

  local function showGrid()
    grid:Show(); page.detail:Hide()
    local here, best = cfg.here(), cfg.best and cfg.best() or nil
    local total = #cfg.list
    local pages = math.max(1, math.ceil(total / GRID_PER))
    gridPage = math.min(math.max(gridPage, 1), pages)
    for k, c in ipairs(cards) do
      local i = (gridPage - 1) * GRID_PER + k
      if cfg.list[i] then
        crop(c.img, i, CARD_W / CARD_H)
        c.name:SetText(cfg.name(i))
        local lv = cfg.levels(i)
        c.levels:SetText("|c" .. HEX.gold .. (lv ~= "" and string.format(T.level_range, lv) or "") .. "|r")
        ns.FlatBorder(c, i == here and ns.C.teal or (i == best and ns.C.gold or ns.C.border))
        c:SetScript("OnClick", function() selected = i; bossIdx = nil; bossPage = 1; itemPage = 1; refresh() end)
        c:Show()
      else
        c:Hide()
      end
    end
    noData:SetText(total == 0 and ("|c" .. HEX.faint .. (cfg.empty or "") .. "|r") or "")
    gridPager(gridPage, pages, function(s) gridPage = gridPage + s; refresh() end)
  end

  ---------------------------------------------------------------- one instance / one boss
  local detail = CreateFrame("Frame", nil, page)
  detail:SetAllPoints()
  page.detail = detail

  -- Left column: back to the instances, the instance picker, the boss list.
  local backBtn = ns.Button(detail)
  backBtn:SetSize(MID_W, 24)
  backBtn:SetPoint("TOPLEFT", 0, -2)
  backBtn:SetText("<  " .. (cfg.back or T.back))
  backBtn:SetScript("OnClick", function() selected = false; refresh() end)
  backBtn:SetShown(not single)
  local pickTop = single and -2 or -32
  local pickBtn = ns.Button(detail)
  pickBtn:SetSize(MID_W, 28)
  pickBtn:SetPoint("TOPLEFT", 0, pickTop)
  pickBtn:HookScript("OnEnter", function(self)
    local lines = cfg.tip and selected ~= false and cfg.tip(selected or cfg.here() or 1)
    if lines and #lines > 0 then
      GameTooltip:SetOwner(self, "ANCHOR_BOTTOM")
      GameTooltip:SetText(lines[1])
      for k = 2, #lines do GameTooltip:AddLine(lines[k], 1, 1, 1, true) end
      GameTooltip:Show()
    end
  end)
  pickBtn:HookScript("OnLeave", function() GameTooltip:Hide() end)
  local bossTop = pickTop - 38
  local bossBtns = {}
  for k = 1, BOSS_ROWS do
    local b = ns.Button(detail, nil, "pill")
    b:SetSize(MID_W, BOSS_H - 2)
    b:SetPoint("TOPLEFT", 0, bossTop - (k - 1) * BOSS_H)
    leftLabel(b, 40, MID_W - 100)
    b.num = b:CreateFontString(nil, "OVERLAY", "BrokenMetaFontButton")
    b.num:SetPoint("LEFT", 10, 0)
    b.num:SetWidth(22)
    b.tag = b:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
    b.tag:SetPoint("RIGHT", -10, 0)
    b.tag:SetJustifyH("RIGHT")
    b:Hide()
    bossBtns[k] = b
  end
  local bossPager = newPager(detail, 0, 4)

  -- Right column.
  local right = CreateFrame("Frame", nil, detail)
  right:SetPoint("TOPLEFT", MID_W + 12, 0)
  right:SetPoint("BOTTOMRIGHT", 0, 0)
  local banner = CreateFrame("Frame", nil, right, ns.BACKDROP_TEMPLATE)
  banner:SetSize(RIGHT_W, BANNER_H)
  banner:SetPoint("TOPLEFT", 0, -2)
  ns.Flat(banner, ns.C.bg, ns.C.border)
  local bannerImg = banner:CreateTexture(nil, "ARTWORK")
  bannerImg:SetPoint("TOPLEFT", 1, -1)
  bannerImg:SetPoint("BOTTOMRIGHT", -1, 1)
  local bannerShade = banner:CreateTexture(nil, "OVERLAY")
  bannerShade:SetColorTexture(0, 0, 0, 0.55)
  bannerShade:SetPoint("TOPLEFT", 1, -1)
  bannerShade:SetPoint("BOTTOMRIGHT", -1, 1)
  local portrait = CreateFrame("Frame", nil, banner, ns.BACKDROP_TEMPLATE)
  portrait:SetSize(98, 98)
  portrait:SetPoint("BOTTOMLEFT", 16, -34)
  ns.Flat(portrait, ns.C.bg, ns.C.borderBright)
  local skull = portrait:CreateTexture(nil, "ARTWORK")
  skull:SetPoint("TOPLEFT", 14, -14)
  skull:SetPoint("BOTTOMRIGHT", -14, 14)
  skull:SetTexture("Interface\\TargetingFrame\\UI-TargetingFrame-Skull")
  local questMark = portrait:CreateTexture(nil, "OVERLAY")
  questMark:SetPoint("TOPLEFT", 14, -14)
  questMark:SetPoint("BOTTOMRIGHT", -14, 14)
  questMark:SetTexture("Interface\\GossipFrame\\AvailableQuestIcon")
  questMark:Hide()
  local model = CreateFrame("PlayerModel", nil, portrait)
  model:SetPoint("TOPLEFT", 2, -2)
  model:SetPoint("BOTTOMRIGHT", -2, 2)
  local TEXT_X = 16 + 98 + 16
  local bossName = banner:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
  if ns.MEDIA then pcall(bossName.SetFont, bossName, ns.MEDIA .. "Fonts/CalSans-Regular.ttf", 26, "") end
  bossName:SetPoint("BOTTOMLEFT", TEXT_X, 76)
  bossName:SetWidth(RIGHT_W - TEXT_X - 190)
  bossName:SetJustifyH("LEFT")
  bossName:SetWordWrap(false)
  local bossSub = banner:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  bossSub:SetPoint("BOTTOMLEFT", TEXT_X, 54)
  bossSub:SetWidth(RIGHT_W - TEXT_X - 190)
  bossSub:SetJustifyH("LEFT")
  bossSub:SetWordWrap(false)
  local bossAbil = banner:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  bossAbil:SetPoint("BOTTOMLEFT", TEXT_X, 14)
  bossAbil:SetWidth(RIGHT_W - TEXT_X - 24)
  bossAbil:SetHeight(34)
  bossAbil:SetJustifyH("LEFT")
  bossAbil:SetJustifyV("TOP")
  local sumBig = banner:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
  if ns.MEDIA then pcall(sumBig.SetFont, sumBig, ns.MEDIA .. "Fonts/CalSans-Regular.ttf", 26, "") end
  sumBig:SetPoint("TOPRIGHT", -16, -18)
  sumBig:SetJustifyH("RIGHT")
  local sumSmall = banner:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  sumSmall:SetPoint("TOPRIGHT", -16, -52)
  sumSmall:SetWidth(170)
  sumSmall:SetJustifyH("RIGHT")
  local prevBoss = ns.Button(banner)
  prevBoss:SetSize(30, 22)
  prevBoss:SetPoint("TOPLEFT", 12, -10)
  prevBoss:SetText("<")
  local nextBoss = ns.Button(banner)
  nextBoss:SetSize(30, 22)
  nextBoss:SetPoint("LEFT", prevBoss, "RIGHT", 4, 0)
  nextBoss:SetText(">")

  local GRID_TOP = -(2 + BANNER_H + 46)
  local cells = {}
  for k = 1, CELL_ROWS * 2 do
    local c = makeCell(right, CELL_W, CELL_H - 8)
    c.cellW = CELL_W
    c:Hide()
    cells[k] = c
  end
  local noLoot = right:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  noLoot:SetPoint("TOPLEFT", 8, GRID_TOP - 10)
  noLoot:SetWidth(RIGHT_W - 16)
  noLoot:SetJustifyH("LEFT")
  local itemPager = newPager(right, 0, 4)

  local dungeonPicker = newPicker(detail, pickBtn, 2, 520)

  -- The cells of the loot grid: items in two columns, a quest header across both; paged by rows.
  local function layoutCells(rowsList)
    local out, row, col = {}, 0, 0
    for _, e in ipairs(rowsList) do
      if e.header then
        if col ~= 0 then row = row + 1; col = 0 end
        out[#out + 1] = { e = e, row = row, col = 0, span = 2 }
        row = row + 1
      else
        out[#out + 1] = { e = e, row = row, col = col, span = 1 }
        col = col + 1
        if col == 2 then col = 0; row = row + 1 end
      end
    end
    return out, (col ~= 0) and (row + 1) or row
  end

  local function showDetail(d)
    grid:Hide(); detail:Show()
    local here = cfg.here()
    pickBtn:SetText(cfg.label(d) .. "  v")
    local names = {}
    for i = 1, #cfg.list do names[i] = cfg.label(i) end
    dungeonPicker:Fill(names, d, function(k) selected = k; bossIdx = nil; bossPage = 1; itemPage = 1; refresh() end)

    local bosses = cfg.bosses(d)
    if not bossIdx then
      bossIdx = 1
      for k, b in ipairs(bosses) do if #b.items > 0 then bossIdx = k; break end end
      bossPage = math.floor((bossIdx - 1) / BOSS_ROWS) + 1
    end
    bossIdx = math.min(math.max(bossIdx, 1), math.max(#bosses, 1))
    local boss = bosses[bossIdx]

    -- Boss list (paged).
    local bossPages = math.max(1, math.ceil(#bosses / BOSS_ROWS))
    bossPage = math.min(math.max(bossPage, 1), bossPages)
    for k, b in ipairs(bossBtns) do
      local idx = (bossPage - 1) * BOSS_ROWS + k
      local e = bosses[idx]
      if e then
        local ups = 0
        for _, it in ipairs(e.items) do if it.gain and it.gain > 0.005 then ups = ups + 1 end end
        b:SetText((e.other and "|c" .. HEX.faint or "") .. e.name .. (e.other and "|r" or ""))
        b.num:SetText(e.quest and "|cffffd100!|r" or (e.other and "|c" .. HEX.faint .. "·|r" or ("|c" .. HEX.faint .. idx .. "|r")))
        b.tag:SetText(#e.items == 0 and "" or ("|c" .. (ups > 0 and HEX.teal or HEX.faint) .. string.format(T.obj_short, #e.items) .. "|r"))
        if idx == bossIdx then b:LockHighlight() else b:UnlockHighlight() end
        b:SetScript("OnClick", function() bossIdx = idx; itemPage = 1; refresh() end)
        b:Show()
      else
        b:Hide()
      end
    end
    bossPager(bossPage, bossPages, function(s) bossPage = bossPage + s; refresh() end)

    -- Banner: the picture of the instance, the head of the boss, its name, where it is, abilities, what it brings.
    crop(bannerImg, d, RIGHT_W / BANNER_H)
    questMark:SetShown(boss and boss.quest or false)
    if boss and boss.quest then
      skull:Hide(); model:Hide()
    else
      skull:Show()
      if boss and boss.npc then
        skull:SetAlpha(0.18)
        pcall(model.ClearModel, model)
        local ok = pcall(model.SetCreature, model, boss.npc)
        if ok then pcall(model.SetPortraitZoom, model, 1) else skull:SetAlpha(1) end
        model:Show()
      else
        skull:SetAlpha(1)
        model:Hide()
      end
    end
    local items = boss and boss.items or {}
    local ups, bestBySlot, maxGain = 0, {}, 0
    for _, e in ipairs(items) do
      if e.gain and e.gain > 0.005 then
        ups = ups + 1
        local key = e.it.slot or ("id" .. e.it.id)
        if not bestBySlot[key] or e.gain > bestBySlot[key] then bestBySlot[key] = e.gain end
      end
      if e.gain and math.abs(e.gain) > maxGain then maxGain = math.abs(e.gain) end
    end
    local total = 0
    for _, g in pairs(bestBySlot) do total = total + g end
    bossName:SetText(boss and ("|c" .. (boss.quest and "ffffd100" or (boss.other and HEX.faint or HEX.cream)) .. boss.name .. "|r") or "")
    bossSub:SetText("|c" .. HEX.dim .. ((boss and boss.quest) and (string.format(T.n_quests, boss.n or 0) .. "  ·  ")
      or ((boss and not boss.other) and (string.format(T.boss_n, bossIdx, #bosses) .. "  ·  ") or "")) .. cfg.name(d) .. "|r")
    bossAbil:SetText(boss and boss.abilities and ("|c" .. HEX.faint .. boss.abilities .. "|r") or "")
    if total > 0.005 then
      sumBig:SetText("|c" .. HEX.teal .. string.format("+%.2f DPS", total) .. "|r")
      sumSmall:SetText("|c" .. HEX.faint .. string.format(T.sum_useful, ups) .. "|r")
    else
      sumBig:SetText("")
      sumSmall:SetText(#items > 0 and ("|c" .. HEX.faint .. T.sum_none .. "|r") or "")
    end
    if bossIdx > 1 then prevBoss:Enable() else prevBoss:Disable() end
    if bossIdx < #bosses then nextBoss:Enable() else nextBoss:Disable() end
    local function gotoBoss(i) bossIdx = i; bossPage = math.floor((i - 1) / BOSS_ROWS) + 1; itemPage = 1; refresh() end
    prevBoss:SetScript("OnClick", function() gotoBoss(bossIdx - 1) end)
    nextBoss:SetScript("OnClick", function() gotoBoss(bossIdx + 1) end)

    -- Loot of the boss.
    local placed, nRows = layoutCells(boss and boss.rows or {})
    local pages = math.max(1, math.ceil(nRows / CELL_ROWS))
    itemPage = math.min(math.max(itemPage, 1), pages)
    local first = (itemPage - 1) * CELL_ROWS
    local level = UnitLevel("player") or 1
    local used = 0
    for _, p in ipairs(placed) do
      if p.row >= first and p.row < first + CELL_ROWS then
        used = used + 1
        local c = cells[used]
        c:ClearAllPoints()
        c:SetPoint("TOPLEFT", p.col * (CELL_W + 8), GRID_TOP - (p.row - first) * CELL_H)
        if p.e.header then c:SetHeader(p.e, RIGHT_W) else c:SetItem(p.e, level, maxGain) end
      end
    end
    for k = used + 1, #cells do cells[k]:Hide() end
    noLoot:SetText(#placed == 0 and ("|c" .. HEX.faint .. T.none_boss .. "|r") or "")
    itemPager(itemPage, pages, function(s) itemPage = itemPage + s; refresh() end)
  end

  refresh = function()
    local here = cfg.here()
    local d
    if selected ~= false then d = selected or here end
    if not d and single then d = 1 end
    if d then showDetail(d) else showGrid() end
  end
  -- Entering or leaving an instance: show that one next time.
  local ev = CreateFrame("Frame")
  pcall(ev.RegisterEvent, ev, "PLAYER_ENTERING_WORLD")
  ev:SetScript("OnEvent", function() selected = nil; bossIdx = nil; bossPage = 1; itemPage = 1 end)
  return function() refresh() end
end

-- Dungeons tab.
do
  local refresh
  local page, index = ns.HubTab("codex", T.tab_loot, function() refresh() end)
  ns.CodexTabs = ns.CodexTabs or {}
  ns.CodexTabs.dungeons = index
  refresh = buildBrowser(page, {
    list = ns.DUNGEONS,
    name = function(i) local dg = ns.DUNGEONS[i]; return dg.name[LOC] or dg.name.enUS end,
    label = dungeonName,
    levels = function(i) return ns.DUNGEONS[i].levels end,
    image = dungeonImage,
    wide = function(i) local art = ns.DUNGEON_ART and ns.DUNGEON_ART[i]; return art and art.wide end,
    bosses = ns.DungeonBosses,
    here = ns.CurrentDungeon,
    pickText = T.pick,
    -- The dungeon that would improve this character the most.
    best = function()
      local by = ns.UpgradesByDungeon and ns.UpgradesByDungeon() or {}
      local best
      for i in ipairs(ns.DUNGEONS) do
        if by[i] and (not best or by[i].gain > by[best].gain) then best = i end
      end
      return best
    end,
  })
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
  local page, logIndex = ns.HubTab("codex", T.tab_log, function() refresh() end)
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

---------------------------------------------------------------------------------------------
-- Raids tab: the same browser, over data/wow_raids/raids.json (bosses with NPC, abilities and loot)
---------------------------------------------------------------------------------------------
if ns.RAIDS then
  local function raidName(i)
    local raid = ns.RAIDS[i]
    return raid.name[LOC] or raid.name.enUS
  end

  -- The raid the player is in, matched on its name, or nil.
  function ns.CurrentRaid()
    if not GetInstanceInfo then return nil end
    local name, kind = GetInstanceInfo()
    if kind ~= "raid" or not name then return nil end
    for i, raid in ipairs(ns.RAIDS) do
      if raid.name.frFR == name or raid.name.enUS == name then return i end
    end
    return nil
  end

  -- The bosses of a raid, in order, with their abilities and their loot, then the other loot of the raid.
  function ns.RaidBosses(ri)
    local raid = ns.RAIDS[ri]
    local list = {}
    if not raid then return list end
    for _, b in ipairs(raid.bosses) do
      local e = { name = b.name[LOC] or b.name.enUS, npc = b.npc, items = {} }
      for _, it in ipairs(b.drops or {}) do e.items[#e.items + 1] = entryFor(it) end
      table.sort(e.items, byGain)
      e.rows = e.items
      if b.abilities and #b.abilities > 0 then
        local names = {}
        for _, ab in ipairs(b.abilities) do names[#names + 1] = ab.n end
        e.abilities = table.concat(names, "  ·  ")
      end
      list[#list + 1] = e
    end
    if raid.other and #raid.other > 0 then
      local e = { name = T.other_loot, other = true, items = {} }
      for _, it in ipairs(raid.other) do e.items[#e.items + 1] = entryFor(it) end
      table.sort(e.items, byGain)
      e.rows = e.items
      list[#list + 1] = e
    end
    return list
  end

  local refresh
  local page, index = ns.HubTab("codex", T.tab_raids, function() refresh() end)
  ns.CodexTabs = ns.CodexTabs or {}
  ns.CodexTabs.raids = index
  refresh = buildBrowser(page, {
    list = ns.RAIDS,
    name = raidName,
    label = raidName,
    levels = function(i) return tostring(ns.RAIDS[i].level or "") end,
    image = function(i) return ns.RAID_IMAGES and ns.RAID_IMAGES[ns.RAIDS[i].id] end,
    wide = function() return false end,
    bosses = ns.RaidBosses,
    here = ns.CurrentRaid,
    pickText = T.raid_pick,
    back = T.back_raids,
    empty = T.raid_none,
    tip = function(i)
      local raid = ns.RAIDS[i]
      local lines = { raidName(i), string.format(T.raid_info, tostring(raid.level or "?"), tostring(raid.players or "?"),
        raid.location and (raid.location[LOC] or raid.location.enUS) or "") }
      if raid.attune then lines[#lines + 1] = string.format(T.raid_attune, raid.attune, tostring(raid.attune_req or "?")) end
      return lines
    end,
  })
end
