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


-- Texts of the Upgrades, Best in slot, Guide and Export pages (new in the wide layout).
local PT = ns.Localize("dpspages", {
  up_bags_entry = "Dans tes sacs", up_vs = "face à ton équipement", up_total = "%d objet(s) utile(s) : +%.2f DPS au total",
  bis_hint = "Meilleur équipement niveau 20 de ta spécialisation, objet par objet.", bis_worn = "✓ équipé", bis_owned = "dans tes sacs",
  bis_none = "pas encore obtenu", bis_wearing = "%d sur %d équipés",
  page = "Page %d/%d", prof_done_short = "Parcours terminé jusqu'à %d/%d.", prof_next_short = "Prochaine étape : %s (%d-%d), environ %d crafts.",
  export_keys = "Contient : stats de la fiche personnage, talents, équipement (identifiants d'objets), armes. Aucun nom de personnage.",
}, {
  up_bags_entry = "In your bags", up_vs = "vs. your equipment", up_total = "%d useful item(s): +%.2f DPS in total",
  bis_hint = "Level-20 best in slot gear for your spec, item by item.", bis_worn = "✓ worn", bis_owned = "in your bags",
  bis_none = "not obtained yet", bis_wearing = "%d of %d worn",
  page = "Page %d/%d", prof_done_short = "Route finished up to %d/%d.", prof_next_short = "Next step: %s (%d-%d), about %d crafts.",
  export_keys = "Holds: character sheet stats, talents, gear (item ids), weapons. No character name.",
})
for k, v in pairs(PT) do if rawget(T, k) == nil then T[k] = v end end

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
-- Shared by the pages below: item cards (icon in a quality frame, name, a line of detail, what the item
-- adds over what is worn with a meter) and the two-column layout of a list on the left, a panel on the right.
---------------------------------------------------------------------------------------------
local QUALITY = { [2] = "1eff00", [3] = "0070dd", [4] = "a335ee", [5] = "ff8000" }
local function rgbOf(hex)
  return { tonumber(hex:sub(1, 2), 16) / 255, tonumber(hex:sub(3, 4), 16) / 255, tonumber(hex:sub(5, 6), 16) / 255, 1 }
end
local function lootLink(it)
  local name = select(1, ns.GetItemInfo(it.id)) or it.n
  return "|cff" .. (QUALITY[it.q] or "ffffff") .. "|Hitem:" .. it.id .. "::::::::|h[" .. name .. "]|h|r"
end

local LIST_W = 262
local PANEL_W = W - 24 - LIST_W - 12
local CARD_W, CARD_H = math.floor((PANEL_W - 8) / 2), 64

-- spec: { id or link, name, quality (number or hex), icon, sub, gain, maxGain, tag }
local function newItemCard(parent, w)
  w = w or CARD_W
  local c = CreateFrame("Button", nil, parent, ns.BACKDROP_TEMPLATE)
  c:SetSize(w, CARD_H - 6)
  ns.Flat(c)
  c.frame = CreateFrame("Frame", nil, c, ns.BACKDROP_TEMPLATE)
  c.frame:SetSize(46, 46)
  c.frame:SetPoint("LEFT", 8, 0)
  ns.Flat(c.frame, ns.C.bg, ns.C.border)
  c.icon = c.frame:CreateTexture(nil, "ARTWORK")
  c.icon:SetPoint("TOPLEFT", 1, -1)
  c.icon:SetPoint("BOTTOMRIGHT", -1, 1)
  c.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
  c.name = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  c.name:SetPoint("TOPLEFT", 64, -7)
  c.name:SetWidth(w - 76)
  c.name:SetJustifyH("LEFT")
  c.name:SetWordWrap(false)
  c.sub = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  c.sub:SetPoint("TOPLEFT", 64, -25)
  c.sub:SetWidth(w - 76)
  c.sub:SetJustifyH("LEFT")
  c.sub:SetWordWrap(false)
  c.delta = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  c.delta:SetPoint("TOPLEFT", 64, -40)
  c.delta:SetWidth(w - 76)
  c.delta:SetJustifyH("LEFT")
  c.delta:SetWordWrap(false)
  c.meterBg = c:CreateTexture(nil, "ARTWORK")
  c.meterBg:SetColorTexture(unpack(ns.C.border))
  c.meterBg:SetHeight(3)
  c.meterBg:SetPoint("BOTTOMLEFT", 64, 5)
  c.meterBg:SetWidth(w - 76)
  c.meterFill = c:CreateTexture(nil, "OVERLAY")
  c.meterFill:SetHeight(3)
  c.meterFill:SetPoint("BOTTOMLEFT", 64, 5)
  c:SetScript("OnEnter", function(self)
    if self.SetBackdropColor then self:SetBackdropColor(unpack(ns.C.rowHover)) end
    if self.ref then
      GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
      GameTooltip:SetHyperlink(self.ref)
      GameTooltip:Show()
    end
  end)
  c:SetScript("OnLeave", function(self)
    if self.SetBackdropColor then self:SetBackdropColor(unpack(ns.C.row)) end
    GameTooltip:Hide()
  end)
  c:SetScript("OnClick", function(self) if self.ref and HandleModifiedItemClick then HandleModifiedItemClick(self.link or self.ref) end end)
  function c:Set(spec)
    self.ref, self.link = spec.ref, spec.link
    local hex = type(spec.quality) == "string" and spec.quality or QUALITY[spec.quality or 1] or "ffffff"
    local q = rgbOf(hex)
    self.name:SetText("|cff" .. hex .. (spec.name or "?") .. "|r" .. (spec.mark and ("  " .. spec.mark) or ""))
    self.icon:SetTexture(spec.icon or "Interface\\Icons\\INV_Misc_QuestionMark")
    ns.FlatBorder(self.frame, q)
    self.sub:SetText("|c" .. ns.HEX.faint .. (spec.sub or "") .. "|r")
    local gain = spec.gain
    if gain and gain > 0.005 then
      self.delta:SetText("|c" .. ns.HEX.teal .. string.format("+%.2f DPS", gain) .. "|r |c" .. ns.HEX.faint .. (spec.vs or "") .. "|r")
      self.meterFill:SetColorTexture(unpack(ns.C.teal))
      self.meterFill:SetWidth(math.max(2, math.floor((w - 76) * math.min(1, gain / math.max(spec.maxGain or gain, 0.01)))))
      self.meterFill:Show()
    else
      self.delta:SetText(spec.note and ("|c" .. ns.HEX.faint .. spec.note .. "|r") or "")
      self.meterFill:Hide()
    end
    self:Show()
  end
  return c
end

-- A column of selectable rows (pill buttons) with a tag on the right and a pager under it.
local function newList(page, rowsN, rowH, top)
  local list = { rows = {}, page = 1 }
  for k = 1, rowsN do
    local b = ns.Button(page, nil, "pill")
    b:SetSize(LIST_W, rowH - 2)
    b:SetPoint("TOPLEFT", 0, top - (k - 1) * rowH)
    local fs = b.GetFontString and b:GetFontString()
    if fs then fs:ClearAllPoints(); fs:SetPoint("LEFT", 12, 0); fs:SetWidth(LIST_W - 90); fs:SetJustifyH("LEFT"); fs:SetWordWrap(false) end
    b.tag = b:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
    b.tag:SetPoint("RIGHT", -10, 0)
    b:Hide()
    list.rows[k] = b
  end
  local prev = ns.Button(page)
  prev:SetSize(28, 22)
  prev:SetPoint("BOTTOMLEFT", 0, 4)
  prev:SetText("<")
  local nxt = ns.Button(page)
  nxt:SetSize(28, 22)
  nxt:SetPoint("LEFT", prev, "RIGHT", 70, 0)
  nxt:SetText(">")
  local text = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  text:SetPoint("LEFT", prev, "RIGHT", 8, 0)
  -- entries: { label, tag, selected, onClick }
  function list:Fill(entries, refresh)
    local pages = math.max(1, math.ceil(#entries / #self.rows))
    self.page = math.min(math.max(self.page, 1), pages)
    for k, b in ipairs(self.rows) do
      local e = entries[(self.page - 1) * #self.rows + k]
      if e then
        b:SetText(e.label)
        b.tag:SetText(e.tag or "")
        if e.selected then b:LockHighlight() else b:UnlockHighlight() end
        b:SetScript("OnClick", e.onClick)
        b:Show()
      else
        b:Hide()
      end
    end
    text:SetText(string.format(T.page, self.page, pages))
    if self.page > 1 then prev:Enable() else prev:Disable() end
    if self.page < pages then nxt:Enable() else nxt:Disable() end
    prev:SetScript("OnClick", function() self.page = self.page - 1; refresh() end)
    nxt:SetScript("OnClick", function() self.page = self.page + 1; refresh() end)
  end
  return list
end

-- A title and a summary at the top of a panel.
local function newPanelHead(parent)
  local h = {}
  h.title = parent:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
  if ns.MEDIA then pcall(h.title.SetFont, h.title, ns.MEDIA .. "Fonts/CalSans-Regular.ttf", 24, "") end
  h.title:SetPoint("TOPLEFT", LIST_W + 12 + 2, -2)
  h.title:SetWidth(PANEL_W - 4)
  h.title:SetJustifyH("LEFT")
  h.title:SetWordWrap(false)
  h.sub = parent:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  h.sub:SetPoint("TOPLEFT", h.title, "BOTTOMLEFT", 0, -6)
  h.sub:SetWidth(PANEL_W - 4)
  h.sub:SetJustifyH("LEFT")
  h.sub:SetWordWrap(false)
  return h
end

local function cardPos(k, top) -- card k (1-based) of a two-column grid under the panel head
  return LIST_W + 12 + ((k - 1) % 2) * (CARD_W + 8), top - math.floor((k - 1) / 2) * CARD_H
end

---------------------------------------------------------------------------------------------
-- Page 2: Upgrades: the sources on the left (bags, then dungeons by what a run is worth), the upgrades
-- of the chosen source as cards on the right.
---------------------------------------------------------------------------------------------
local pUp, upIndex = newPage(T.tab_up, 2)
ns.DPSTabs.upgrades = upIndex

local Container = C_Container or {}
local GetNumSlots = Container.GetContainerNumSlots or GetContainerNumSlots
local GetBagLink = Container.GetContainerItemLink or GetContainerItemLink

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

-- Dungeons in the list: most rewarding first, then the others by name.
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

local UP_ROWS, UP_ROW_H = 15, 34
local upSel -- nil: bags if it has upgrades, else the most rewarding dungeon; "bags"; or a dungeon index
local upList = newList(pUp, UP_ROWS, UP_ROW_H, -2)
local upHead = newPanelHead(pUp)
local upCards = {}
for k = 1, 12 do
  upCards[k] = newItemCard(pUp)
  upCards[k]:SetPoint("TOPLEFT", cardPos(k, -70))
  upCards[k]:Hide()
end
local upEmpty = pUp:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
upEmpty:SetPoint("TOPLEFT", LIST_W + 12 + 4, -80)
upEmpty:SetWidth(PANEL_W - 8)
upEmpty:SetJustifyH("LEFT")
local upHint = pUp:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
upHint:SetPoint("BOTTOMLEFT", LIST_W + 12 + 4, 8)
upHint:SetWidth(PANEL_W - 8)
upHint:SetJustifyH("LEFT")
upHint:SetText(T.up_hint)

refreshers[2] = function()
  -- Upgrades in the bags.
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
  local bagsTotal = 0
  for _, f in ipairs(found) do bagsTotal = bagsTotal + f.d end

  local by = upgradesByDungeon()
  local order = dungeonOrder(by)
  local top = order[1] and by[order[1]] and order[1] or nil
  local sel = upSel
  if sel == nil then sel = (#found > 0) and "bags" or top or order[1] end

  local entries = { { label = "|c" .. ns.HEX.gold .. T.up_bags_entry .. "|r", tag = #found > 0 and string.format("|c%s+%.1f|r", ns.HEX.teal, bagsTotal) or "",
    selected = sel == "bags", onClick = function() upSel = "bags"; refreshers[2]() end } }
  for _, idx in ipairs(order) do
    local x = by[idx]
    entries[#entries + 1] = { label = dungeonName(idx), tag = x and string.format("|c%s+%.1f|r", ns.HEX.teal, x.gain) or "",
      selected = sel == idx, onClick = function() upSel = idx; refreshers[2]() end }
  end
  upList:Fill(entries, refreshers[2])

  -- The cards of the selected source.
  local cards = {}
  local summary
  if sel == "bags" then
    upHead.title:SetText("|c" .. ns.HEX.gold .. T.up_bags_entry .. "|r")
    for _, f in ipairs(found) do
      local name, _, quality, _, _, _, _, _, loc, icon = ns.GetItemInfo(f.link)
      cards[#cards + 1] = { ref = f.link, link = f.link, name = name, quality = quality, icon = icon, sub = loc and _G[loc] or "", gain = f.d, vs = T.up_vs }
    end
    summary = #found > 0 and string.format(T.up_total, #found, bagsTotal) or T.no_upgrade
  else
    local dd = by[sel]
    upHead.title:SetText("|c" .. ns.HEX.cream .. (sel and dungeonName(sel) or "") .. "|r" .. ((sel == top and dd) and ("  |c" .. ns.HEX.teal .. T.up_top .. "|r") or ""))
    local level = UnitLevel("player") or 1
    for _, b in ipairs(dd and dd.items or {}) do
      local it = b.it
      local icon = (C_Item and C_Item.GetItemIconByID and C_Item.GetItemIconByID(it.id)) or (GetItemIcon and GetItemIcon(it.id))
      local src = it.quest and T.up_quest or (it.src or "")
      if (it.req or 0) > level then src = src .. "  ·  " .. string.format(T.up_level, it.req) end
      cards[#cards + 1] = { ref = "item:" .. it.id, link = lootLink(it), name = (select(1, ns.GetItemInfo(it.id))) or it.n, quality = it.q, icon = icon,
        sub = src, gain = b.gain, vs = T.up_vs }
    end
    summary = dd and string.format(T.up_summary, dd.n, dd.gain) or T.up_none_in
  end
  upHead.sub:SetText("|c" .. ns.HEX.dim .. summary .. "|r")
  local maxGain = 0
  for _, c in ipairs(cards) do maxGain = math.max(maxGain, c.gain or 0) end
  for k, card in ipairs(upCards) do
    local spec = cards[k]
    if spec then spec.maxGain = maxGain; card:Set(spec) else card:Hide() end
  end
  upEmpty:SetText(#cards == 0 and ("|c" .. ns.HEX.faint .. (sel == "bags" and T.no_upgrade or T.up_none_in) .. "|r") or "")
end

---------------------------------------------------------------------------------------------
-- Page 5: Best in slot (level-20 gear per spec; data/wow_items/bis_gear_by_slot.json): one card per
-- slot, saying whether you wear it and what it would add over what you wear.
---------------------------------------------------------------------------------------------
local pBis, bisIndex = newPage(T.tab_bis, 5)
ns.DPSTabs.bis = bisIndex

local BIS_SLOT_LABEL = {
  head = "HEADSLOT", neck = "NECKSLOT", shoulder = "SHOULDERSLOT", back = "BACKSLOT", chest = "CHESTSLOT",
  wrist = "WRISTSLOT", hands = "HANDSSLOT", waist = "WAISTSLOT", legs = "LEGSSLOT", feet = "FEETSLOT",
  finger = "FINGER0SLOT", finger2 = "FINGER1SLOT", trinket = "TRINKET0SLOT", trinket2 = "TRINKET1SLOT",
  main_hand = "MAINHANDSLOT", off_hand = "SECONDARYHANDSLOT", ranged = "RANGEDSLOT",
}
local BIS_SLOT_ID = {
  head = 1, neck = 2, shoulder = 3, back = 15, chest = 5, wrist = 9, hands = 10, waist = 6, legs = 7, feet = 8,
  finger = 11, finger2 = 12, trinket = 13, trinket2 = 14, main_hand = 16, off_hand = 17, ranged = 18,
}

local BIS_W = math.floor((W - 24 - 8) / 2)
local bisHeadTitle = pBis:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
if ns.MEDIA then pcall(bisHeadTitle.SetFont, bisHeadTitle, ns.MEDIA .. "Fonts/CalSans-Regular.ttf", 24, "") end
bisHeadTitle:SetPoint("TOPLEFT", 2, -2)
bisHeadTitle:SetWidth(W - 40)
bisHeadTitle:SetJustifyH("LEFT")
local bisHeadSub = pBis:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
bisHeadSub:SetPoint("TOPLEFT", bisHeadTitle, "BOTTOMLEFT", 0, -6)
bisHeadSub:SetWidth(W - 40)
bisHeadSub:SetJustifyH("LEFT")
local bisCards = {}
for k = 1, 18 do
  local c = newItemCard(pBis, BIS_W)
  c:SetPoint("TOPLEFT", ((k - 1) % 2) * (BIS_W + 8), -66 - math.floor((k - 1) / 2) * CARD_H)
  c:Hide()
  bisCards[k] = c
end
local bisEmpty = pBis:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
bisEmpty:SetPoint("TOPLEFT", 4, -70)
bisEmpty:SetWidth(W - 40)
bisEmpty:SetJustifyH("LEFT")

-- Ask the client for every item of the spec's list so names, icons and stats are known (the gain needs
-- them); the page redraws as the answers come back.
local bisRequested = {}
local function preloadBis()
  local spec = ns.GetSpec and ns.GetSpec()
  local rows = spec and ns.BIS and ns.BIS[spec]
  if not rows then return end
  local request = (C_Item and C_Item.RequestLoadItemDataByID) or _G.RequestLoadItemDataByID
  for _, r in ipairs(rows) do
    if r.id and not bisRequested[r.id] and not ns.GetItemInfo(r.id) then
      bisRequested[r.id] = true
      if request then pcall(request, r.id) end
    end
  end
end
ns.PreloadBis = preloadBis

local bisEvents, bisRedraw = CreateFrame("Frame"), false
for _, e in ipairs({ "PLAYER_ENTERING_WORLD", "GET_ITEM_INFO_RECEIVED", "PLAYER_TALENT_UPDATE" }) do
  pcall(bisEvents.RegisterEvent, bisEvents, e)
end
bisEvents:SetScript("OnEvent", function(_, event, itemID)
  if event ~= "GET_ITEM_INFO_RECEIVED" then
    bisRequested = {}
    preloadBis()
    return
  end
  if not bisRequested[itemID] or bisRedraw or not pBis:IsShown() then return end
  bisRedraw = true -- several items arrive together: redraw once
  C_Timer.After(0.2, function()
    bisRedraw = false
    if pBis:IsShown() then refreshers[5]() end
  end)
end)

refreshers[5] = function()
  preloadBis()
  local spec = ns.GetSpec and ns.GetSpec()
  local rows = spec and ns.BIS and ns.BIS[spec]
  if not rows then
    bisHeadTitle:SetText("")
    bisHeadSub:SetText("")
    for _, c in ipairs(bisCards) do c:Hide() end
    bisEmpty:SetText("|c" .. ns.HEX.faint .. T.no_spec .. "|r")
    return
  end
  bisEmpty:SetText("")
  bisHeadTitle:SetText("|c" .. ns.HEX.cream .. T.tab_bis .. "|r  |c" .. ns.HEX.teal .. ns.specName(spec) .. "|r")
  bisHeadSub:SetText("|c" .. ns.HEX.dim .. T.bis_hint .. "|r")
  local items, maxGain, wearing = {}, 0, 0
  for k, r in ipairs(rows) do
    local link = r.id and ("item:" .. r.id) or nil
    local name, _, quality, _, _, _, _, _, _, tex = ns.GetItemInfo(r.id or 0)
    local slotId = BIS_SLOT_ID[r.slot]
    local worn = slotId and GetInventoryItemLink("player", slotId)
    local isWorn = worn and r.id and tonumber(worn:match("item:(%d+)")) == r.id
    local gain
    if link and not isWorn and name then
      local v = ns.score(link)
      local d = v and ns.deltaVsEquipped(link, v)
      if d and d > 0.005 then gain = d; maxGain = math.max(maxGain, d) end
    end
    if isWorn then wearing = wearing + 1 end
    items[k] = { ref = link, link = link, name = name or r.n or "?", quality = quality or 3,
      icon = r.icon and ("Interface\\Icons\\" .. r.icon) or tex, sub = slotLabel(BIS_SLOT_LABEL[r.slot] or r.slot),
      gain = gain, vs = T.up_vs,
      note = isWorn and ("|c" .. ns.HEX.teal .. T.bis_worn .. "|r") or ((r.id and GetItemCount and GetItemCount(r.id, true) or 0) > 0 and T.bis_owned or T.bis_none) }
  end
  bisHeadSub:SetText("|c" .. ns.HEX.dim .. T.bis_hint .. "  ·  " .. string.format(T.bis_wearing, wearing, #rows) .. "|r")
  for k, c in ipairs(bisCards) do
    local it = items[k]
    if it then it.maxGain = maxGain; c:Set(it) else c:Hide() end
  end
end

---------------------------------------------------------------------------------------------
-- Page 6: Guide: your build against the guide's talents, and your professions with their route (the
-- full guide stays on brokenmeta.gg; the buttons give the links).
---------------------------------------------------------------------------------------------
local pGuide, guideIndex = newPage(T.tab_guide, 6)
ns.DPSTabs.guide = guideIndex
local GL_W = 380
local GR_X = GL_W + 14
local GR_W = W - 24 - GR_X

local function newPanel(parent, x, w, h)
  local f = CreateFrame("Frame", nil, parent, ns.BACKDROP_TEMPLATE)
  f:SetSize(w, h)
  f:SetPoint("TOPLEFT", x, -2)
  ns.Flat(f, ns.C.row, ns.C.border)
  return f
end

local gl = newPanel(pGuide, 0, GL_W, 330)
local gTitle = gl:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
gTitle:SetPoint("TOPLEFT", 14, -14)
gTitle:SetText(T.guide_h)
local gSpec = gl:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
if ns.MEDIA then pcall(gSpec.SetFont, gSpec, ns.MEDIA .. "Fonts/CalSans-Regular.ttf", 26, "") end
gSpec:SetPoint("TOPLEFT", 14, -40)
gSpec:SetWidth(GL_W - 28)
gSpec:SetJustifyH("LEFT")
local gText = gl:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
gText:SetPoint("TOPLEFT", gSpec, "BOTTOMLEFT", 0, -10)
gText:SetWidth(GL_W - 28)
gText:SetJustifyH("LEFT")
local gBarBg = gl:CreateTexture(nil, "ARTWORK")
gBarBg:SetColorTexture(unpack(ns.C.border))
gBarBg:SetHeight(10)
gBarBg:SetWidth(GL_W - 28)
gBarBg:SetPoint("TOPLEFT", 14, -150)
local gBarFill = gl:CreateTexture(nil, "OVERLAY")
gBarFill:SetHeight(10)
gBarFill:SetPoint("TOPLEFT", 14, -150)
local gMore = gl:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
gMore:SetPoint("TOPLEFT", 14, -176)
gMore:SetWidth(GL_W - 28)
gMore:SetJustifyH("LEFT")
local gBtn = ns.Button(gl, nil, "primary")
gBtn:SetSize(GL_W - 28, 30)
gBtn:SetPoint("BOTTOMLEFT", 14, 16)
gBtn:SetText(T.guide_copy)

local gr = newPanel(pGuide, GR_X, GR_W, 330)
local pTitle = gr:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
pTitle:SetPoint("TOPLEFT", 14, -14)
pTitle:SetText(T.prof_h)
local profRows = {}
for k = 1, 4 do
  local y = -44 - (k - 1) * 70
  local r = {}
  r.icon = gr:CreateTexture(nil, "ARTWORK")
  r.icon:SetSize(32, 32)
  r.icon:SetPoint("TOPLEFT", 14, y)
  r.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
  r.name = gr:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  r.name:SetPoint("TOPLEFT", 54, y)
  r.name:SetWidth(GR_W - 54 - 130)
  r.name:SetJustifyH("LEFT")
  r.name:SetWordWrap(false)
  r.rank = gr:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  r.rank:SetPoint("TOPRIGHT", -140, y - 2)
  r.bg = gr:CreateTexture(nil, "ARTWORK")
  r.bg:SetColorTexture(unpack(ns.C.border))
  r.bg:SetHeight(6)
  r.bg:SetWidth(GR_W - 54 - 130)
  r.bg:SetPoint("TOPLEFT", 54, y - 20)
  r.fill = gr:CreateTexture(nil, "OVERLAY")
  r.fill:SetHeight(6)
  r.fill:SetPoint("TOPLEFT", 54, y - 20)
  r.next = gr:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  r.next:SetPoint("TOPLEFT", 54, y - 30)
  r.next:SetWidth(GR_W - 54 - 130)
  r.next:SetHeight(28)
  r.next:SetJustifyH("LEFT")
  r.next:SetJustifyV("TOP")
  r.btn = ns.Button(gr)
  r.btn:SetSize(112, 22)
  r.btn:SetPoint("TOPRIGHT", -14, y - 4)
  r.btn:SetText(T.prof_copy)
  profRows[k] = r
end
local profNone = gr:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
profNone:SetPoint("TOPLEFT", 14, -46)
profNone:SetWidth(GR_W - 28)
profNone:SetJustifyH("LEFT")

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
  gSpec:SetText(spec and ("|c" .. ns.HEX.cream .. ns.specName(spec) .. "|r") or "")
  if spec and tb and #tb.core > 0 and ranks then
    local have = 0
    for _, node in ipairs(tb.core) do if (ranks[node] or 0) > 0 then have = have + 1 end end
    gText:SetText(string.format(T.guide_follow, have, #tb.core, tb.level or 20))
    gBarBg:Show()
    gBarFill:SetColorTexture(unpack(have == #tb.core and ns.C.teal or ns.C.gold))
    gBarFill:SetWidth(math.max(2, math.floor((GL_W - 28) * have / #tb.core)))
    gBarFill:Show()
    gMore:SetText(T.guide_more)
  else
    gText:SetText("")
    gBarBg:Hide(); gBarFill:Hide()
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
      local r = profRows[k]
      local pname = route.name[IS_FR and "frFR" or "enUS"] or route.name.enUS
      local nextText = string.format(T.prof_done_short, pr.rank, pr.max)
      for _, st in ipairs(route.steps) do
        if pr.rank < st.t then
          local left = st.c
          if pr.rank > st.f then left = math.ceil(st.c * (st.t - pr.rank) / math.max(1, st.t - st.f)) end
          nextText = string.format(T.prof_next_short, st.name[IS_FR and "frFR" or "enUS"] or st.name.enUS, st.f, st.t, left)
          break
        end
      end
      r.icon:SetTexture(ns.ProfIconPath and ns.ProfIconPath(pr.line) or "Interface\\Icons\\INV_Misc_QuestionMark")
      r.name:SetText("|c" .. ns.HEX.gold .. pname .. "|r")
      r.rank:SetText("|c" .. ns.HEX.cream .. pr.rank .. "|r|c" .. ns.HEX.faint .. "/" .. pr.max .. "|r")
      r.fill:SetColorTexture(unpack(ns.C.teal))
      r.fill:SetWidth(math.max(2, math.floor((GR_W - 54 - 130) * math.min(1, pr.rank / math.max(pr.max, 1)))))
      r.next:SetText("|c" .. ns.HEX.dim .. nextText .. "|r")
      for _, f in ipairs({ r.icon, r.name, r.rank, r.bg, r.fill, r.next, r.btn }) do f:Show() end
      r.btn:SetScript("OnClick", function()
        ns.ShowCopyText(T.link_title, T.link_hint, ns.SiteURL("wow-forever/professions/" .. route.id .. "/", "profession"))
      end)
    end
  end
  profNone:SetText(k == 0 and ("|c" .. ns.HEX.faint .. T.prof_none .. "|r") or "")
  for j = k + 1, #profRows do
    local r = profRows[j]
    for _, f in ipairs({ r.icon, r.name, r.rank, r.bg, r.fill, r.next, r.btn }) do f:Hide() end
  end
end

---------------------------------------------------------------------------------------------
-- Page 3: Export
---------------------------------------------------------------------------------------------
local pExp, iExport = newPage(T.tab_export, 3)
ns.DPSTabs.export = iExport
-- Left: what this is and how to use it. Right: the text to copy, in a framed panel.
local EX_W = 300
local exInfo = CreateFrame("Frame", nil, pExp, ns.BACKDROP_TEMPLATE)
exInfo:SetSize(EX_W, 330)
exInfo:SetPoint("TOPLEFT", 0, -2)
ns.Flat(exInfo, ns.C.row, ns.C.border)
local exTitle = exInfo:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
exTitle:SetPoint("TOPLEFT", 14, -14)
exTitle:SetText(T.tab_export)
local expHint = exInfo:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
expHint:SetPoint("TOPLEFT", 14, -42)
expHint:SetWidth(EX_W - 28)
expHint:SetJustifyH("LEFT")
expHint:SetJustifyV("TOP")
expHint:SetText(T.export_hint)
local exKeys = exInfo:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
exKeys:SetPoint("BOTTOMLEFT", 14, 14)
exKeys:SetWidth(EX_W - 28)
exKeys:SetJustifyH("LEFT")
exKeys:SetText(T.export_keys)

local exPanel = CreateFrame("Frame", nil, pExp, ns.BACKDROP_TEMPLATE)
exPanel:SetPoint("TOPLEFT", EX_W + 14, -2)
exPanel:SetPoint("BOTTOMRIGHT", 0, 4)
ns.Flat(exPanel, ns.C.bg, ns.C.borderBright)
local scroll = CreateFrame("ScrollFrame", "BrokenMetaHubExportScroll", exPanel, "UIPanelScrollFrameTemplate")
scroll:SetPoint("TOPLEFT", 10, -10)
scroll:SetPoint("BOTTOMRIGHT", -30, 10)
local box = CreateFrame("EditBox", nil, scroll)
box:SetMultiLine(true)
box:SetAutoFocus(false)
box:SetFontObject(ChatFontNormal)
box:SetWidth(W - 24 - EX_W - 14 - 50)
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
