-- BrokenDPS pages in the Broken Meta : HUB window: Character (spec, weights, equipped gear value),
-- Upgrades (bags and dungeons), Guide (links to the spec guide on brokenmeta.gg), Export (text for
-- "Simulate my character" on the site).
local ADDON = ...
local ns = BrokenMetaNS
local IS_FR = ns.IS_FR
local T = ns.HubTexts
local H = ns.Hub
local W, rows, setRow, clearRows = H.W, H.rows, H.setRow, H.clearRows
local HUB_ADDON = "BrokenMetaWeights" -- the export reports the HUB's version (the site compares it)

ns.HubSection("dps", T.sec_dps, 10, "BrokenDPS")
local refreshers = {}
local function newPage(label, slot)
  return ns.HubTab("dps", label, function() if refreshers[slot] then refreshers[slot]() end end)
end

local function fmtDelta(d)
  if d > 0.005 then return string.format("|cff2de6c4+%.2f|r", d) end
  if d < -0.005 then return string.format("|cffff5a6b%.2f|r", d) end
  return "|cffa2a6bd0.00|r"
end

local SLOT_ORDER = {
  { 1, "HEADSLOT" }, { 2, "NECKSLOT" }, { 3, "SHOULDERSLOT" }, { 15, "BACKSLOT" }, { 5, "CHESTSLOT" },
  { 9, "WRISTSLOT" }, { 10, "HANDSSLOT" }, { 6, "WAISTSLOT" }, { 7, "LEGSSLOT" }, { 8, "FEETSLOT" },
  { 11, "FINGER0SLOT" }, { 12, "FINGER1SLOT" }, { 13, "TRINKET0SLOT" }, { 14, "TRINKET1SLOT" },
  { 16, "MAINHANDSLOT" }, { 17, "SECONDARYHANDSLOT" }, { 18, "RANGEDSLOT" },
}
local function slotLabel(key) return _G[key] or key end

---------------------------------------------------------------------------------------------
-- Page 1: Character
---------------------------------------------------------------------------------------------
local pChar, charIndex = newPage(T.tab_char, 1)
ns.DPSTabs = { character = charIndex }

local specText = pChar:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
specText:SetPoint("TOP", 0, -4)

local function cycleSpec(step)
  local list = ns.classSpecs()
  if #list == 0 then return end
  local idx = 1
  for i, id in ipairs(list) do if id == ns.GetSpec() then idx = i end end
  idx = (idx - 1 + step) % #list + 1
  ns.ChooseSpec(list[idx])
end

for _, def in ipairs({ { "<", -1, "TOPLEFT", 4 }, { ">", 1, "TOPRIGHT", -4 } }) do
  local b = ns.Button(pChar)
  b:SetSize(28, 20)
  b:SetPoint(def[3], def[4], 0)
  b:SetText(def[1])
  b:SetScript("OnClick", function() cycleSpec(def[2]) end)
end

-- Two panels: the stat weights as gauges (longest = the stat that matters most) and the equipped gear.
local C, HEX = ns.C, ns.HEX
local LEFT_W = 396
local RIGHT_X = LEFT_W + 14
local RIGHT_W = W - 24 - RIGHT_X
local PANEL_H = 482
local BAR_W = LEFT_W - 28

local LABELS = {
  str = IS_FR and "Force" or "Strength", agi = IS_FR and "Agilité" or "Agility", int = IS_FR and "Intelligence" or "Intellect",
  ap = IS_FR and "Puissance d'attaque" or "Attack power", sp = IS_FR and "Puissance des sorts" or "Spell power",
  crit = IS_FR and "Critique (1 %)" or "Crit (1%)", hit = IS_FR and "Toucher (1 %)" or "Hit (1%)",
}
local STAT_ORDER = { "str", "agi", "int", "ap", "sp", "crit", "hit" }

local wp = CreateFrame("Frame", nil, pChar, ns.BACKDROP_TEMPLATE)
wp:SetSize(LEFT_W, PANEL_H)
wp:SetPoint("TOPLEFT", 0, -34)
ns.Flat(wp, C.row, C.border)
local wTitle = wp:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
wTitle:SetPoint("TOPLEFT", 14, -12)
local wTag = wp:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
wTag:SetPoint("TOPLEFT", 14, -32)
wTag:SetWidth(LEFT_W - 28)
wTag:SetJustifyH("LEFT")

local function gauge(parent, y)
  local g = {}
  g.label = parent:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  g.label:SetPoint("TOPLEFT", 14, y)
  g.label:SetWidth(BAR_W - 130)
  g.label:SetJustifyH("LEFT")
  g.label:SetWordWrap(false)
  g.value = parent:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  g.value:SetPoint("TOPRIGHT", -14, y - 2)
  g.value:SetJustifyH("RIGHT")
  g.bg = parent:CreateTexture(nil, "ARTWORK")
  g.bg:SetColorTexture(unpack(C.border))
  g.bg:SetHeight(8)
  g.bg:SetWidth(BAR_W)
  g.bg:SetPoint("TOPLEFT", 14, y - 20)
  g.fill = parent:CreateTexture(nil, "OVERLAY")
  g.fill:SetHeight(8)
  g.fill:SetPoint("TOPLEFT", 14, y - 20)
  function g:Set(label, value, text, fraction, color)
    self.label:SetText(label)
    self.value:SetText(text)
    if fraction and fraction > 0 then
      self.fill:SetColorTexture(unpack(color or C.teal))
      self.fill:SetWidth(math.max(2, math.floor(BAR_W * math.min(1, fraction))))
      self.fill:Show()
    else
      self.fill:Hide()
    end
    for _, f in ipairs({ self.label, self.value, self.bg }) do f:Show() end
  end
  function g:Hide() for _, f in ipairs({ self.label, self.value, self.bg, self.fill }) do f:Hide() end end
  return g
end

local gauges = {}
for k = 1, #STAT_ORDER do gauges[k] = gauge(wp, -58 - (k - 1) * 40) end
local wdpsHead = wp:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
wdpsHead:SetPoint("TOPLEFT", 14, -58 - #STAT_ORDER * 40 - 4)
local wdpsGauges = {}
for k = 1, 3 do wdpsGauges[k] = gauge(wp, -58 - #STAT_ORDER * 40 - 24 - (k - 1) * 40) end
local weightHint = pChar:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
weightHint:SetPoint("TOPLEFT", 4, -34 - PANEL_H - 8)
weightHint:SetWidth(LEFT_W - 8)
weightHint:SetJustifyH("LEFT")

-- Equipped gear: one row per slot (icon, slot : item, DPS value), tooltip of the worn item on hover.
local gp = CreateFrame("Frame", nil, pChar, ns.BACKDROP_TEMPLATE)
gp:SetPoint("TOPLEFT", RIGHT_X, -34)
gp:SetSize(RIGHT_W, PANEL_H)
ns.Flat(gp, C.row, C.border)
local gTitle = gp:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
gTitle:SetPoint("TOPLEFT", 14, -12)
local gDps = gp:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
gDps:SetPoint("TOPRIGHT", -14, -12)
local gearRows = {}
local GEAR_H = 24
for k = 1, #SLOT_ORDER do
  local r = CreateFrame("Button", nil, gp)
  r:SetSize(RIGHT_W - 16, GEAR_H)
  r:SetPoint("TOPLEFT", 8, -38 - (k - 1) * GEAR_H)
  r.hl = r:CreateTexture(nil, "BACKGROUND")
  r.hl:SetAllPoints()
  r.hl:SetColorTexture(unpack(C.rowHover))
  r.hl:Hide()
  r.icon = r:CreateTexture(nil, "ARTWORK")
  r.icon:SetSize(20, 20)
  r.icon:SetPoint("LEFT", 4, 0)
  r.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
  r.label = r:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  r.label:SetPoint("LEFT", r.icon, "RIGHT", 8, 0)
  r.label:SetWidth(RIGHT_W - 130)
  r.label:SetJustifyH("LEFT")
  r.label:SetWordWrap(false)
  r.value = r:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  r.value:SetPoint("RIGHT", -8, 0)
  r.value:SetJustifyH("RIGHT")
  r:SetScript("OnEnter", function(self)
    self.hl:Show()
    if self.slot then
      GameTooltip:SetOwner(self, "ANCHOR_LEFT")
      GameTooltip:SetInventoryItem("player", self.slot)
      GameTooltip:Show()
    end
  end)
  r:SetScript("OnLeave", function(self) self.hl:Hide(); GameTooltip:Hide() end)
  gearRows[k] = r
end
local gTotalLabel = gp:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
gTotalLabel:SetPoint("TOPLEFT", 14, -38 - #SLOT_ORDER * GEAR_H - 10)
local gTotal = gp:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
gTotal:SetPoint("TOPRIGHT", -14, -38 - #SLOT_ORDER * GEAR_H - 10)

local importBtn = ns.Button(pChar)
importBtn:SetSize(180, 22)
importBtn:SetPoint("BOTTOMLEFT", 4, 4)
importBtn:SetText(T.import_btn)
importBtn:SetScript("OnClick", function() if ns.ShowImportDialog then ns.ShowImportDialog() end end)
local resetBtn = ns.Button(pChar)
resetBtn:SetSize(180, 22)
resetBtn:SetPoint("LEFT", importBtn, "RIGHT", 8, 0)
resetBtn:SetText(T.reset_btn)
resetBtn:SetScript("OnClick", function() SlashCmdList.BROKENMETAWEIGHTS("import clear") end)

refreshers[1] = function()
  local spec = ns.GetSpec()
  if not spec then
    specText:SetText(T.no_spec)
    wp:Hide(); gp:Hide(); weightHint:SetText("")
    return
  end
  wp:Show(); gp:Show()
  specText:SetText(T.spec .. " : |cffffffff" .. ns.specName(spec) .. "|r")
  local w, custom = ns.ActiveWeights(spec)
  local rp = ns.GetRatingPerPct()

  -- Stat weights: sorted by importance, each with a gauge relative to the best stat.
  wTitle:SetText(T.weights)
  wTag:SetText(custom and ("|c" .. HEX.teal .. string.format(T.w_custom, custom.level or 0, custom.date or "?") .. "|r")
    or ("|c" .. HEX.faint .. T.w_generic .. "|r"))
  local list = {}
  for i, key in ipairs(STAT_ORDER) do list[i] = { key = key, v = w[key] or 0, order = i } end
  table.sort(list, function(a, b) if a.v ~= b.v then return a.v > b.v end return a.order < b.order end)
  local top = list[1].v
  for i, e in ipairs(list) do
    local label = LABELS[e.key]
    if e.key == "crit" or e.key == "hit" then
      label = label .. "  |c" .. HEX.faint .. string.format("(%.1f %s%s)", rp[e.key] or 0, T.rating,
        (e.key == "crit" and rp.crit_approx) and " ~" or "") .. "|r"
    end
    if e.v > 0 and top > 0 then
      local rel = e.v / top
      gauges[i]:Set("|c" .. (i == 1 and HEX.teal or HEX.cream) .. label .. "|r", e.v,
        string.format("%.3f  |c%s%d%%|r", e.v, HEX.faint, math.floor(rel * 100 + 0.5)), rel, i == 1 and C.teal or { 0.24, 0.62, 0.92, 1 })
    else
      gauges[i]:Set("|c" .. HEX.faint .. label .. "|r", 0, "|c" .. HEX.faint .. "0.000|r", 0)
    end
  end
  local wd = { { _G.MAINHANDSLOT or "Main hand", w.wdps_mh or 0 }, { _G.SECONDARYHANDSLOT or "Off hand", w.wdps_oh or 0 }, { _G.RANGEDSLOT or "Ranged", w.wdps_r or 0 } }
  local wmax = math.max(wd[1][2], wd[2][2], wd[3][2])
  if wmax > 0 then
    wdpsHead:SetText("|c" .. HEX.gold .. (IS_FR and "DPS de l'arme (par point)" or "Weapon DPS (per point)") .. "|r")
    for k, e in ipairs(wd) do
      if e[2] > 0 then
        wdpsGauges[k]:Set("|c" .. HEX.cream .. e[1] .. "|r", e[2], string.format("%.3f", e[2]), e[2] / wmax, { 1, 0.76, 0.24, 1 })
      else
        wdpsGauges[k]:Set("|c" .. HEX.faint .. e[1] .. "|r", 0, "|c" .. HEX.faint .. "0.000|r", 0)
      end
    end
  else
    wdpsHead:SetText("")
    for k = 1, 3 do wdpsGauges[k]:Hide() end
  end

  -- Equipped gear.
  gTitle:SetText(T.gear)
  gDps:SetText("DPS")
  local total = 0
  for k, s in ipairs(SLOT_ORDER) do
    local r = gearRows[k]
    local link = GetInventoryItemLink("player", s[1])
    local v = link and ns.score(link) or 0
    total = total + v
    local icon, dim = GetInventoryItemTexture("player", s[1]), false
    if not icon then
      -- empty slot: the game's own grey slot silhouette
      local ok, _, tex = pcall(GetInventorySlotInfo, s[2])
      icon, dim = ok and tex or nil, true
    end
    r.slot = link and s[1] or nil
    r.icon:SetTexture(icon)
    r.icon:SetDesaturated(dim)
    r.icon:SetAlpha(dim and 0.4 or 1)
    r.label:SetText("|c" .. HEX.faint .. slotLabel(s[2]) .. "|r  " .. (link or ("|c" .. HEX.faint .. T.empty .. "|r")))
    r.value:SetText(link and ((v > 0 and "|c" .. HEX.cream or "|c" .. HEX.faint) .. string.format("%.2f", v) .. "|r") or "")
  end
  gTotalLabel:SetText(T.total)
  gTotal:SetText(string.format("|c" .. HEX.teal .. "%.2f|r", total))

  if not custom and (UnitLevel("player") or 20) ~= 20 then
    weightHint:SetText("|cffff9900" .. T.w_hint_level .. "|r")
  elseif custom and ns.ImportedWeightsStale() then
    weightHint:SetText("|cffff9900" .. string.format(T.w_hint_refresh, custom.level, ns.REFRESH_LEVELS) .. "|r")
  else
    weightHint:SetText("")
  end
end

---------------------------------------------------------------------------------------------
-- Page 2: Upgrades from bags
---------------------------------------------------------------------------------------------
local pUp = newPage(T.tab_up, 2)
local upHint = pUp:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
upHint:SetPoint("TOPLEFT", 4, -2)
upHint:SetPoint("TOPRIGHT", -4, -2)
upHint:SetJustifyH("LEFT")
upHint:SetText(T.up_hint)
rows(pUp, 24, -40, 17, true)

local Container = C_Container or {}
local GetNumSlots = Container.GetContainerNumSlots or GetContainerNumSlots
local GetBagLink = Container.GetContainerItemLink or GetContainerItemLink

local QUALITY = { [2] = "1eff00", [3] = "0070dd", [4] = "a335ee", [5] = "ff8000" }
local function lootLink(it)
  local name = select(1, ns.GetItemInfo(it.id)) or it.n
  return "|cff" .. (QUALITY[it.q] or "ffffff") .. "|Hitem:" .. it.id .. "::::::::|h[" .. name .. "]|h|r"
end

-- Dungeon upgrades, per dungeon: every dungeon item that beats what is worn (wearable by the class,
-- required level at most 3 above the player's), and per dungeon the sum of its best item per slot
-- (what a run is worth). { [d] = { items = { { it, gain } } sorted, n = slots improved, gain } }.
local function upgradesByDungeon()
  local level = UnitLevel("player") or 1
  local out = {}
  for _, it in ipairs(ns.LOOT or {}) do
    local slots = it.slot and ns.SLOTS[it.slot]
    if slots and (it.req or 0) <= level + 3 and ns.CanWearType(it.t) then
      local v = ns.scoreStats(it.st, it.slot) or 0
      if v > 0 then
        local worst
        for _, slot in ipairs(slots) do
          local eq = GetInventoryItemLink("player", slot)
          local ev = eq and ns.score(eq) or 0
          if not worst or ev < worst then worst = ev end
        end
        local gain = v - (worst or 0)
        if gain > 0.005 then
          local dd = out[it.d] or { items = {}, best = {} }
          out[it.d] = dd
          dd.items[#dd.items + 1] = { it = it, gain = gain }
          if not dd.best[it.slot] or gain > dd.best[it.slot] then dd.best[it.slot] = gain end
        end
      end
    end
  end
  for _, dd in pairs(out) do
    table.sort(dd.items, function(x, y) return x.gain > y.gain end)
    dd.n, dd.gain = 0, 0
    for _, g in pairs(dd.best) do dd.n, dd.gain = dd.n + 1, dd.gain + g end
  end
  return out
end
ns.UpgradesByDungeon = upgradesByDungeon

local function dungeonName(i)
  local dg = ns.DUNGEONS and ns.DUNGEONS[i]
  if not dg then return "?" end
  return (dg.name[IS_FR and "frFR" or "enUS"] or dg.name.enUS) .. (dg.levels ~= "" and (" (" .. dg.levels .. ")") or "")
end

-- Dungeons in the picker: most rewarding first, then the others by name.
local function dungeonOrder(by)
  local list = {}
  for i in ipairs(ns.DUNGEONS or {}) do list[#list + 1] = i end
  table.sort(list, function(a, b)
    local ga, gb = by[a] and by[a].gain or 0, by[b] and by[b].gain or 0
    if ga ~= gb then return ga > gb end
    return dungeonName(a) < dungeonName(b)
  end)
  return list
end

local BAG_MAX, PICK_ROW = 4, 7 -- bag upgrades shown, row where the dungeon picker sits
local selectedDungeon -- nil: the most rewarding one

local pickBtn = ns.Button(pUp)
pickBtn:SetSize(W - 32, 22)
pickBtn:SetPoint("TOPLEFT", 4, -40 - (PICK_ROW - 1) * 17 + 3)

-- The picker: a panel over the list with one button per dungeon (upgrades count and DPS gain).
local picker = CreateFrame("Frame", nil, pUp, ns.BACKDROP_TEMPLATE)
picker:SetPoint("TOPLEFT", pickBtn, "BOTTOMLEFT", 0, -4)
picker:SetPoint("RIGHT", pUp, "RIGHT", -4, 0)
picker:SetHeight(318)
ns.Flat(picker, ns.C.bg, ns.C.borderBright)
picker:SetFrameLevel((pUp:GetFrameLevel() or 1) + 20)
picker:Hide()
local pickRows = {}
for k = 1, 24 do
  local b = ns.Button(picker, nil, "pill")
  b:SetSize((W - 50) / 2, 24)
  b:SetPoint("TOPLEFT", 6 + ((k - 1) % 2) * ((W - 50) / 2 + 6), -6 - math.floor((k - 1) / 2) * 26)
  if b.GetFontString and b:GetFontString() then b:GetFontString():SetWidth((W - 50) / 2 - 12) end
  b:Hide()
  pickRows[k] = b
end
pickBtn:SetScript("OnClick", function() picker:SetShown(not picker:IsShown()) end)

refreshers[2] = function()
  local found = {}
  if ns.GetSpec() and GetNumSlots and GetBagLink then
    local level = UnitLevel("player") or 1
    for bag = 0, (NUM_BAG_SLOTS or 4) do
      for slot = 1, (GetNumSlots(bag) or 0) do
        local link = GetBagLink(bag, slot)
        local loc = link and select(9, ns.GetItemInfo(link))
        local minLevel = link and select(5, ns.GetItemInfo(link)) or 0
        if loc and ns.SLOTS[loc] and minLevel <= level and ns.CanWearLink(link) then
          local v = ns.score(link)
          local d = v and ns.deltaVsEquipped(link, v)
          if d and d > 0.005 then found[#found + 1] = { link = link, d = d } end
        end
      end
    end
  end
  table.sort(found, function(a, b) return a.d > b.d end)
  local i = 1
  setRow(pUp, i, "|cffffc23c" .. T.up_bags .. "|r"); i = i + 1
  if #found == 0 then
    setRow(pUp, i, "|cff7a7e96" .. T.no_upgrade .. "|r"); i = i + 1
  end
  for k = 1, math.min(#found, BAG_MAX) do
    local f = found[k]
    setRow(pUp, i, f.link, fmtDelta(f.d) .. " DPS", { icon = select(10, ns.GetItemInfo(f.link)), link = f.link }); i = i + 1
  end
  clearRows(pUp, i)

  -- Dungeon picker and the selected dungeon's upgrades.
  local by = upgradesByDungeon()
  local order = dungeonOrder(by)
  local top = order[1] and by[order[1]] and order[1] or nil
  local d = selectedDungeon or top or order[1]
  if not d then pickBtn:Hide(); return end
  pickBtn:Show()
  local dd = by[d]
  pickBtn:SetText(string.format(T.up_pick, dungeonName(d)) .. (d == top and ("  · " .. T.up_top) or "") .. "  ↓")
  for k, b in ipairs(pickRows) do
    local idx = order[k]
    if idx then
      local x = by[idx]
      b:SetText(dungeonName(idx) .. (x and string.format("  |c%s+%.1f|r", ns.HEX.teal, x.gain) or ""))
      if idx == d then b:LockHighlight() else b:UnlockHighlight() end
      b:SetScript("OnClick", function() selectedDungeon = idx; picker:Hide(); refreshers[2]() end)
      b:Show()
    else
      b:Hide()
    end
  end
  i = PICK_ROW + 1
  if not dd then
    setRow(pUp, i, "|cff7a7e96" .. T.up_none_in .. "|r"); i = i + 1
  else
    setRow(pUp, i, "|cff7a7e96" .. string.format(T.up_summary, dd.n, dd.gain) .. "|r"); i = i + 1
    local level = UnitLevel("player") or 1
    for _, b in ipairs(dd.items) do
      if i > #pUp.rows then break end
      local it = b.it
      local extra = (it.req or 0) > level and (" · " .. string.format(T.up_level, it.req)) or ""
      local icon = (C_Item and C_Item.GetItemIconByID and C_Item.GetItemIconByID(it.id)) or (GetItemIcon and GetItemIcon(it.id))
      local src = it.quest and T.up_quest or (it.src or "")
      setRow(pUp, i, lootLink(it) .. "  |cff7a7e96" .. src .. extra .. "|r", fmtDelta(b.gain) .. " DPS",
        { icon = icon, link = "item:" .. it.id }); i = i + 1
    end
  end
  clearRows(pUp, i)
end

---------------------------------------------------------------------------------------------
-- Page 5: Best in slot (level-20 gear per spec; data/wow_items/bis_gear_by_slot.json)
---------------------------------------------------------------------------------------------
local pBis = newPage(T.tab_bis, 5)

local BIS_SLOT_LABEL = {
  head = "HEADSLOT", neck = "NECKSLOT", shoulder = "SHOULDERSLOT", back = "BACKSLOT", chest = "CHESTSLOT",
  wrist = "WRISTSLOT", hands = "HANDSSLOT", waist = "WAISTSLOT", legs = "LEGSSLOT", feet = "FEETSLOT",
  finger = "FINGER0SLOT", finger2 = "FINGER1SLOT", trinket = "TRINKET0SLOT", trinket2 = "TRINKET1SLOT",
  main_hand = "MAINHANDSLOT", off_hand = "SECONDARYHANDSLOT", ranged = "RANGEDSLOT",
}

refreshers[5] = function()
  local spec = ns.GetSpec and ns.GetSpec()
  local rows = spec and ns.BIS and ns.BIS[spec]
  local i = 1
  if not rows then
    setRow(pBis, i, "|cff7a7e96" .. T.no_spec .. "|r"); i = i + 1
    clearRows(pBis, i)
    return
  end
  for _, r in ipairs(rows) do
    local icon = r.icon and ("Interface\\Icons\\" .. r.icon) or nil
    setRow(pBis, i, slotLabel(BIS_SLOT_LABEL[r.slot] or r.slot) .. "  |cffffffff" .. (r.n or "?") .. "|r", "",
      { icon = icon, link = r.id and ("item:" .. r.id) or nil }); i = i + 1
  end
  clearRows(pBis, i)
end

---------------------------------------------------------------------------------------------
-- Page 6: Guide (teaser + links to the site; the full guide stays on brokenmeta.gg)
---------------------------------------------------------------------------------------------
local pGuide = newPage(T.tab_guide, 6)
local gTitle = pGuide:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
gTitle:SetPoint("TOPLEFT", 4, -2)
gTitle:SetText(T.guide_h)
local gText = pGuide:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
gText:SetPoint("TOPLEFT", 4, -24)
gText:SetWidth(W - 40)
gText:SetJustifyH("LEFT")
local gMore = pGuide:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
gMore:SetPoint("TOPLEFT", gText, "BOTTOMLEFT", 0, -8)
gMore:SetWidth(W - 40)
gMore:SetJustifyH("LEFT")
local gBtn = ns.Button(pGuide)
gBtn:SetSize(220, 24)
gBtn:SetPoint("TOPLEFT", gMore, "BOTTOMLEFT", 0, -10)
gBtn:SetText(T.guide_copy)
local pTitle = pGuide:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
pTitle:SetPoint("TOPLEFT", 4, -190)
pTitle:SetText(T.prof_h)
local profRows = {}
for k = 1, 4 do
  local fs = pGuide:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  fs:SetPoint("TOPLEFT", 4, -190 - k * 34)
  fs:SetWidth(W - 160)
  fs:SetJustifyH("LEFT")
  local b = ns.Button(pGuide)
  b:SetSize(120, 22)
  b:SetPoint("TOPRIGHT", -4, -186 - k * 34)
  b:SetText(T.prof_copy)
  profRows[k] = { fs = fs, btn = b }
end

-- Learned professions as { line = skillLineID, rank, max }: modern API first, Classic fallback
-- (matched on the localized name against the site's profession names).
local function learnedProfessions()
  local out = {}
  if GetProfessions and GetProfessionInfo then
    for _, idx in ipairs({ GetProfessions() }) do
      local ok, _, _, rank, max, _, _, line = pcall(GetProfessionInfo, idx)
      if ok and line then out[#out + 1] = { line = line, rank = rank or 0, max = max or 0 } end
    end
  elseif GetNumSkillLines and GetSkillLineInfo then
    for i = 1, GetNumSkillLines() do
      local name, header, _, rank, _, _, max = GetSkillLineInfo(i)
      if name and not header then
        for line, p in pairs(ns.PROFESSIONS or {}) do
          if p.name.frFR == name or p.name.enUS == name then out[#out + 1] = { line = line, rank = rank or 0, max = max or 0 } end
        end
      end
    end
  end
  return out
end

refreshers[6] = function()
  local spec = ns.GetSpec()
  local tb = spec and ns.TALENT_BUILDS and ns.TALENT_BUILDS[spec]
  local ranks = ns.readTalents and select(1, ns.readTalents())
  if spec and tb and #tb.core > 0 and ranks then
    local have = 0
    for _, node in ipairs(tb.core) do if (ranks[node] or 0) > 0 then have = have + 1 end end
    gText:SetText("|cffffffff" .. ns.specName(spec) .. "|r : " .. string.format(T.guide_follow, have, #tb.core, tb.level or 20))
    gMore:SetText(T.guide_more)
  else
    gText:SetText(spec and ("|cffffffff" .. ns.specName(spec) .. "|r") or "")
    gMore:SetText(T.guide_nobuild)
  end
  gBtn:SetShown(tb ~= nil)
  gBtn:SetScript("OnClick", function()
    if tb then ns.ShowCopyText(T.link_title, T.link_hint, ns.SiteURL(tb.guide, "guide")) end
  end)

  local profs, k = learnedProfessions(), 0
  for _, pr in ipairs(profs) do
    local route = ns.PROFESSIONS and ns.PROFESSIONS[pr.line]
    if route and k < #profRows then
      k = k + 1
      local pname = route.name[IS_FR and "frFR" or "enUS"] or route.name.enUS
      local text = string.format(T.prof_done, pname, pr.rank, pr.max)
      for _, st in ipairs(route.steps) do
        if pr.rank < st.t then
          local left = st.c
          if pr.rank > st.f then left = math.ceil(st.c * (st.t - pr.rank) / math.max(1, st.t - st.f)) end
          text = string.format(T.prof_next, pname, pr.rank, pr.max, st.name[IS_FR and "frFR" or "enUS"] or st.name.enUS, st.f, st.t, left)
          break
        end
      end
      profRows[k].fs:SetText(text)
      profRows[k].btn:Show()
      profRows[k].btn:SetScript("OnClick", function()
        ns.ShowCopyText(T.link_title, T.link_hint, ns.SiteURL("wow-forever/professions/" .. route.id .. "/", "profession"))
      end)
    end
  end
  if k == 0 then
    profRows[1].fs:SetText("|cff7a7e96" .. T.prof_none .. "|r")
    profRows[1].btn:Hide()
    k = 1
  end
  for j = k + 1, #profRows do profRows[j].fs:SetText(""); profRows[j].btn:Hide() end
end

---------------------------------------------------------------------------------------------
-- Page 3: Export
---------------------------------------------------------------------------------------------
local pExp, iExport = newPage(T.tab_export, 3)
local expHint = pExp:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
expHint:SetPoint("TOPLEFT", 4, -2)
expHint:SetPoint("TOPRIGHT", -4, -2)
expHint:SetJustifyH("LEFT")
expHint:SetText(T.export_hint)

local scroll = CreateFrame("ScrollFrame", "BrokenMetaHubExportScroll", pExp, "UIPanelScrollFrameTemplate")
scroll:SetPoint("TOPLEFT", 4, -56)
scroll:SetPoint("BOTTOMRIGHT", -26, 4)
local box = CreateFrame("EditBox", nil, scroll)
box:SetMultiLine(true)
box:SetAutoFocus(false)
box:SetFontObject(ChatFontNormal)
box:SetWidth(W - 60)
box:SetScript("OnEscapePressed", function() if BrokenMetaHub then BrokenMetaHub:Hide() end end)
scroll:SetScrollChild(box)

-- pcall wrapper that keeps every return value, including nils in the middle (UnitDamage returns
-- nil off-hand values without an off-hand, which a table + unpack would silently cut short).
local function safe(fn, ...)
  if type(fn) ~= "function" then return nil end
  return (function(ok, ...) if ok then return ... end end)(pcall(fn, ...))
end

local function num(v) return v and tostring(tonumber(string.format("%.2f", v))) or "" end

-- Plain "key=value" lines, one per line: readable by a human, trivial for the site to parse.
local function buildExport()
  local out = {}
  local function add(k, v) out[#out + 1] = k .. "=" .. tostring(v == nil and "" or v) end
  add("format", "BMW1")
  add("addon", (C_AddOns and C_AddOns.GetAddOnMetadata or GetAddOnMetadata or function() end)(HUB_ADDON, "Version"))
  add("client", select(1, GetBuildInfo()) .. "." .. select(2, GetBuildInfo()))
  add("date", date("!%Y-%m-%dT%H:%M:%SZ"))
  add("class", ns.PlayerClass())
  add("spec", ns.GetSpec())
  add("level", UnitLevel("player"))
  add("race", select(2, UnitRace("player")))
  -- Character sheet: effective primary stats, attack power, spell power, crit/hit as shown in game.
  for i, k in ipairs({ "str", "agi", "sta", "int", "spi" }) do add(k, select(2, safe(UnitStat, "player", i))) end
  local base, pos, neg = safe(UnitAttackPower, "player")
  if base then add("ap", base + (pos or 0) + (neg or 0)) end
  local rbase, rpos, rneg = safe(UnitRangedAttackPower, "player")
  if rbase then add("rap", rbase + (rpos or 0) + (rneg or 0)) end
  -- Spell power per school (2 holy, 3 fire, 4 nature, 5 frost, 6 shadow, 7 arcane) + the best one.
  local sp = 0
  for school, name in pairs({ [2] = "holy", [3] = "fire", [4] = "nature", [5] = "frost", [6] = "shadow", [7] = "arcane" }) do
    local v = safe(GetSpellBonusDamage, school) or 0
    add("sp_" .. name, v)
    sp = math.max(sp, v)
  end
  add("sp", sp)
  local spellCrit = 0
  for school = 2, 7 do spellCrit = math.max(spellCrit, safe(GetSpellCritChance, school) or 0) end
  add("crit_melee", num(safe(GetCritChance)))
  add("crit_ranged", num(safe(GetRangedCritChance)))
  add("crit_spell", num(spellCrit))
  -- Hit: flat modifiers (talents, items) + what hit rating converts to at the current level.
  local function ratingPct(cr)
    local rating = cr and safe(GetCombatRating, cr)
    if not rating or rating <= 0 then return 0 end
    return safe(GetCombatRatingBonusForCombatRatingValue, cr, rating) or safe(GetCombatRatingBonus, cr) or 0
  end
  add("hit_melee", num((safe(GetHitModifier) or 0) + ratingPct(CR_HIT_MELEE or 6)))
  add("hit_ranged", num((safe(GetHitModifier) or 0) + ratingPct(CR_HIT_RANGED or 7)))
  add("hit_spell", num((safe(GetSpellHitModifier) or 0) + ratingPct(CR_HIT_SPELL or 8)))
  -- Weapons as the character sheet shows them (AP bonus and % modifiers included).
  local mh, oh = safe(UnitAttackSpeed, "player")
  add("speed_mh", num(mh)); add("speed_oh", num(oh))
  local mhMin, mhMax, ohMin, ohMax, _, _, pct = safe(UnitDamage, "player")
  add("mh_min", num(mhMin)); add("mh_max", num(mhMax))
  add("oh_min", num(ohMin)); add("oh_max", num(ohMax)); add("dmg_pct", num(pct))
  local rSpeed, rMin, rMax, _, _, rPct = safe(UnitRangedDamage, "player")
  add("r_speed", num(rSpeed)); add("r_min", num(rMin)); add("r_max", num(rMax)); add("r_pct", num(rPct))
  -- Active buffs inflate sheet stats; the site warns when this is above 0.
  local buffs = 0
  if C_UnitAuras and C_UnitAuras.GetAuraDataByIndex then
    while safe(C_UnitAuras.GetAuraDataByIndex, "player", buffs + 1, "HELPFUL") do buffs = buffs + 1 end
  elseif UnitBuff then
    while safe(UnitBuff, "player", buffs + 1) do buffs = buffs + 1 end
  end
  add("buffs", buffs)
  -- Talents: points per tree and node:rank pairs (the site calculator's own node ids).
  local ranks, perTab = ns.readTalents()
  if perTab then add("talent_points", table.concat(perTab, "/")) end
  if ranks then
    local list = {}
    for node, r in pairs(ranks) do list[#list + 1] = node .. ":" .. r end
    table.sort(list)
    add("talents", table.concat(list, ","))
  end
  -- Gear: slot=itemID:enchantID:suffixID (from the item string, no personal data).
  for _, s in ipairs(SLOT_ORDER) do
    local link = GetInventoryItemLink("player", s[1])
    local istr = link and link:match("|H(item:[^|]+)|h")
    if istr then
      local parts = { strsplit(":", istr) }
      add("slot" .. s[1], (parts[2] or "") .. ":" .. (parts[3] or "") .. ":" .. (parts[8] or ""))
      -- The item's own stats and slot type, so the site can compare dungeon items with it
      -- ("Top gear"): st16=str:10,agi:5,wdps:12.4 / loc16=INVTYPE_2HWEAPON.
      local st, list = ns.itemStats(link), {}
      for k, v in pairs(st) do
        if type(v) == "number" and v ~= 0 then list[#list + 1] = k .. ":" .. num(v) end
      end
      table.sort(list)
      add("st" .. s[1], table.concat(list, ","))
      add("loc" .. s[1], select(9, ns.GetItemInfo(link)) or "")
    end
  end
  -- Rating needed for 1% crit / hit on this client, to turn item ratings into percentages.
  local rp = ns.GetRatingPerPct()
  add("rating_crit", num(rp.crit))
  add("rating_hit", num(rp.hit))
  return table.concat(out, "\n")
end
ns.BuildExport = buildExport

refreshers[3] = function()
  box:SetText(buildExport())
  box:HighlightText()
  box:SetFocus()
end


function ns.ShowExport() ns.HubShow(iExport) end
