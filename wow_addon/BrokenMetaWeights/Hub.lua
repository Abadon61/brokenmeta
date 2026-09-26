-- BrokenMeta hub window (/bmw): Character (spec, weights, equipped gear value), Upgrades (bag
-- items worth more than what's equipped) and Export (a text string to paste on brokenmeta.gg).
local ADDON, ns = ...
local IS_FR = ns.IS_FR

local T = IS_FR and {
  title = "BrokenMeta · Hub DPS",
  tab_char = "Personnage", tab_up = "Améliorations", tab_export = "Export", tab_cmd = "Commandes",
  run = "Lancer", cmd_hint = "Commandes à taper dans le chat (ou clique sur Lancer).",
  cmds = {
    { "", "/bmw", "Ouvre ou ferme cette fenêtre." },
    { "weights", "/bmw weights", "Affiche les poids de ta spé dans le chat." },
    { "export", "/bmw export", "Ouvre l'onglet Export (texte à coller sur brokenmeta.gg)." },
    { "list", "/bmw list", "Liste les spécialisations simulées de ta classe." },
    { nil, "/bmw spec <id>", "Force une spé, ex. /bmw spec %s" },
    { "auto", "/bmw auto", "Revient à la détection automatique par tes talents." },
    { "minimap", "/bmw minimap", "Affiche ou masque le bouton de la minicarte." },
    { "probe", "/bmw probe", "Diagnostic : fonctions du client et points par arbre." },
  },
  spec = "Spécialisation", weights = "Poids (DPS simulé par point)",
  gear = "Équipement porté", total = "Total des stats de l'équipement",
  empty = "vide", no_upgrade = "Aucune amélioration dans tes sacs.",
  up_hint = "Objets de tes sacs qui valent plus que l'équipé pour ta spé. Vérifie que tu peux les porter (type d'armure).",
  export_hint = "Ctrl+C pour copier, puis colle sur brokenmeta.gg. Contient : classe, spé, niveau, race, talents, équipement (ID d'objets), stats de la feuille de personnage. Ni nom ni royaume.",
  approx = "conversion approximative",
  weapon_note = "Le DPS de l'arme n'est pas encore compté.",
  no_spec = "Aucune spécialisation DPS simulée pour ta classe.",
  rating = "cote",
} or {
  title = "BrokenMeta · DPS Hub",
  tab_char = "Character", tab_up = "Upgrades", tab_export = "Export", tab_cmd = "Commands",
  run = "Run", cmd_hint = "Commands to type in chat (or click Run).",
  cmds = {
    { "", "/bmw", "Opens or closes this window." },
    { "weights", "/bmw weights", "Prints your spec's weights in chat." },
    { "export", "/bmw export", "Opens the Export tab (text to paste on brokenmeta.gg)." },
    { "list", "/bmw list", "Lists your class's simulated specs." },
    { nil, "/bmw spec <id>", "Forces a spec, e.g. /bmw spec %s" },
    { "auto", "/bmw auto", "Back to automatic detection from your talents." },
    { "minimap", "/bmw minimap", "Shows or hides the minimap button." },
    { "probe", "/bmw probe", "Diagnostics: client functions and points per tree." },
  },
  spec = "Specialization", weights = "Weights (simulated DPS per point)",
  gear = "Equipped gear", total = "Gear stats total",
  empty = "empty", no_upgrade = "No upgrade in your bags.",
  up_hint = "Bag items worth more than what you wear for your spec. Check that you can wear them (armor type).",
  export_hint = "Ctrl+C to copy, then paste on brokenmeta.gg. Contains: class, spec, level, race, talents, gear (item IDs), character sheet stats. No name, no realm.",
  approx = "approximate conversion",
  weapon_note = "Weapon DPS is not counted yet.",
  no_spec = "No simulated DPS spec for your class.",
  rating = "rating",
}

local SLOT_ORDER = {
  { 1, "HEADSLOT" }, { 2, "NECKSLOT" }, { 3, "SHOULDERSLOT" }, { 15, "BACKSLOT" }, { 5, "CHESTSLOT" },
  { 9, "WRISTSLOT" }, { 10, "HANDSSLOT" }, { 6, "WAISTSLOT" }, { 7, "LEGSSLOT" }, { 8, "FEETSLOT" },
  { 11, "FINGER0SLOT" }, { 12, "FINGER1SLOT" }, { 13, "TRINKET0SLOT" }, { 14, "TRINKET1SLOT" },
  { 16, "MAINHANDSLOT" }, { 17, "SECONDARYHANDSLOT" }, { 18, "RANGEDSLOT" },
}
local function slotLabel(key) return _G[key] or key end

---------------------------------------------------------------------------------------------
-- Frame
---------------------------------------------------------------------------------------------
local W, H = 440, 520
local hub = CreateFrame("Frame", "BrokenMetaHub", UIParent, "BasicFrameTemplateWithInset")
hub:SetSize(W, H)
hub:SetPoint("CENTER")
hub:SetFrameStrata("HIGH")
hub:SetMovable(true)
hub:EnableMouse(true)
hub:RegisterForDrag("LeftButton")
hub:SetScript("OnDragStart", hub.StartMoving)
hub:SetScript("OnDragStop", hub.StopMovingOrSizing)
hub:SetClampedToScreen(true)
hub:Hide()
tinsert(UISpecialFrames, "BrokenMetaHub") -- Escape closes it

hub.title = hub:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
hub.title:SetPoint("TOP", 0, -5)
hub.title:SetText("|TInterface\\AddOns\\BrokenMetaWeights\\Media\\icon:16|t " .. T.title)

local pages, tabs = {}, {}
local function newPage()
  local p = CreateFrame("Frame", nil, hub)
  p:SetPoint("TOPLEFT", 12, -62)
  p:SetPoint("BOTTOMRIGHT", -12, 12)
  p:Hide()
  pages[#pages + 1] = p
  return p
end

local current = 1
local refreshers = {}
local function showPage(i)
  current = i
  for j, p in ipairs(pages) do p:SetShown(j == i) end
  for j, b in ipairs(tabs) do
    if j == i then b:LockHighlight() else b:UnlockHighlight() end
  end
  if refreshers[i] then refreshers[i]() end
end

for i, label in ipairs({ T.tab_char, T.tab_up, T.tab_export, T.tab_cmd }) do
  local b = CreateFrame("Button", nil, hub, "UIPanelButtonTemplate")
  b:SetSize(100, 22)
  b:SetPoint("TOPLEFT", 12 + (i - 1) * 104, -30)
  b:SetText(label)
  b:SetScript("OnClick", function() showPage(i) end)
  tabs[i] = b
end

-- Reusable rows: optional item icon, left/right text, and a hover area that shows the item's
-- real tooltip (equipped slot or item link).
local function rows(page, n, top, lineH, withIcon)
  page.rows = {}
  for i = 1, n do
    local y = top - (i - 1) * lineH
    local icon
    if withIcon then
      icon = page:CreateTexture(nil, "ARTWORK")
      icon:SetSize(lineH - 2, lineH - 2)
      icon:SetPoint("TOPLEFT", 4, y + 1)
      icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    end
    local l = page:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    l:SetPoint("TOPLEFT", withIcon and (lineH + 6) or 4, y)
    l:SetWidth(W - 150)
    l:SetJustifyH("LEFT")
    l:SetWordWrap(false)
    local r = page:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    r:SetPoint("TOPRIGHT", -4, y)
    r:SetJustifyH("RIGHT")
    local row = { l, r, icon = icon }
    local hover = CreateFrame("Button", nil, page)
    hover:SetPoint("TOPLEFT", 0, y + 2)
    hover:SetSize(W - 24, lineH)
    hover:SetScript("OnEnter", function(self)
      if not row.slot and not row.link then return end
      GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
      if row.slot then GameTooltip:SetInventoryItem("player", row.slot) else GameTooltip:SetHyperlink(row.link) end
      GameTooltip:Show()
    end)
    hover:SetScript("OnLeave", function() GameTooltip:Hide() end)
    page.rows[i] = row
  end
end

-- item = { icon = texture, dim = bool, slot = inventory slot } or { icon = texture, link = item link }
local function setRow(page, i, left, right, item)
  local row = page.rows[i]
  if not row then return end
  row[1]:SetText(left or "")
  row[2]:SetText(right or "")
  if row.icon then
    row.icon:SetTexture(item and item.icon or nil)
    row.icon:SetDesaturated(item and item.dim or false)
    row.icon:SetAlpha(item and item.dim and 0.4 or 1)
  end
  row.slot = item and item.slot or nil
  row.link = item and item.link or nil
end

local function clearRows(page, from)
  for i = from, #page.rows do setRow(page, i) end
end

local function fmtDelta(d)
  if d > 0.005 then return string.format("|cff40ff40+%.2f|r", d) end
  if d < -0.005 then return string.format("|cffff5050%.2f|r", d) end
  return "|cffcccccc0.00|r"
end

---------------------------------------------------------------------------------------------
-- Page 1: Character
---------------------------------------------------------------------------------------------
local pChar = newPage()

local specText = pChar:CreateFontString(nil, "OVERLAY", "GameFontNormal")
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
  local b = CreateFrame("Button", nil, pChar, "UIPanelButtonTemplate")
  b:SetSize(28, 20)
  b:SetPoint(def[3], def[4], 0)
  b:SetText(def[1])
  b:SetScript("OnClick", function() cycleSpec(def[2]) end)
end

rows(pChar, 26, -30, 15, true)

refreshers[1] = function()
  local spec = ns.GetSpec()
  if not spec then
    specText:SetText(T.no_spec)
    clearRows(pChar, 1)
    return
  end
  specText:SetText(T.spec .. " : |cffffffff" .. ns.specName(spec) .. "|r")
  local w = ns.WEIGHTS[spec].w
  local rp = ns.GetRatingPerPct()
  local i = 1
  setRow(pChar, i, "|cffffd100" .. T.weights .. "|r"); i = i + 1
  setRow(pChar, i, string.format(IS_FR and "Force %.3f · Agilité %.3f · Intelligence %.3f"
    or "Strength %.3f · Agility %.3f · Intellect %.3f", w.str, w.agi, w.int)); i = i + 1
  setRow(pChar, i, string.format(IS_FR and "Puiss. d'attaque %.3f · Puiss. des sorts %.3f" or "Attack power %.3f · Spell power %.3f", w.ap, w.sp)); i = i + 1
  setRow(pChar, i, string.format(IS_FR and "Critique 1%% %.3f (%.1f %s) · Toucher 1%% %.3f (%.1f %s)"
    or "Crit 1%% %.3f (%.1f %s) · Hit 1%% %.3f (%.1f %s)",
    w.crit, rp.crit, T.rating, w.hit, rp.hit, T.rating),
    rp.crit_approx and ("|cff888888" .. T.approx .. "|r") or nil); i = i + 1
  i = i + 1
  setRow(pChar, i, "|cffffd100" .. T.gear .. "|r", "|cffffd100DPS|r"); i = i + 1
  local total = 0
  for _, s in ipairs(SLOT_ORDER) do
    local link = GetInventoryItemLink("player", s[1])
    local v = link and ns.score(link) or 0
    total = total + v
    local icon, dim = GetInventoryItemTexture("player", s[1]), false
    if not icon then
      -- empty slot: the game's own grey slot silhouette
      local ok, _, tex = pcall(GetInventorySlotInfo, s[2])
      icon, dim = ok and tex or nil, true
    end
    setRow(pChar, i, slotLabel(s[2]) .. " : " .. (link or ("|cff888888" .. T.empty .. "|r")),
      link and string.format("%.2f", v) or "", { icon = icon, dim = dim, slot = link and s[1] or nil }); i = i + 1
  end
  setRow(pChar, i, "|cffffd100" .. T.total .. "|r", string.format("|cffffffff%.2f|r", total)); i = i + 1
  setRow(pChar, i, "|cff888888" .. T.weapon_note .. "|r"); i = i + 1
  clearRows(pChar, i)
end

---------------------------------------------------------------------------------------------
-- Page 2: Upgrades from bags
---------------------------------------------------------------------------------------------
local pUp = newPage()
local upHint = pUp:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
upHint:SetPoint("TOPLEFT", 4, -2)
upHint:SetPoint("TOPRIGHT", -4, -2)
upHint:SetJustifyH("LEFT")
upHint:SetText(T.up_hint)
rows(pUp, 22, -40, 17, true)

local Container = C_Container or {}
local GetNumSlots = Container.GetContainerNumSlots or GetContainerNumSlots
local GetBagLink = Container.GetContainerItemLink or GetContainerItemLink

refreshers[2] = function()
  local found = {}
  if ns.GetSpec() and GetNumSlots and GetBagLink then
    for bag = 0, (NUM_BAG_SLOTS or 4) do
      for slot = 1, (GetNumSlots(bag) or 0) do
        local link = GetBagLink(bag, slot)
        local loc = link and select(9, ns.GetItemInfo(link))
        if loc and ns.SLOTS[loc] then
          local v = ns.score(link)
          local d = v and ns.deltaVsEquipped(link, v)
          if d and d > 0.005 then found[#found + 1] = { link = link, d = d } end
        end
      end
    end
  end
  table.sort(found, function(a, b) return a.d > b.d end)
  if #found == 0 then
    setRow(pUp, 1, "|cff888888" .. T.no_upgrade .. "|r")
    clearRows(pUp, 2)
    return
  end
  for i = 1, #pUp.rows do
    local f = found[i]
    if f then
      setRow(pUp, i, f.link, fmtDelta(f.d) .. " DPS", { icon = select(10, ns.GetItemInfo(f.link)), link = f.link })
    else
      setRow(pUp, i)
    end
  end
end

---------------------------------------------------------------------------------------------
-- Page 3: Export
---------------------------------------------------------------------------------------------
local pExp = newPage()
local expHint = pExp:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
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
box:SetScript("OnEscapePressed", function() hub:Hide() end)
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
  add("addon", (C_AddOns and C_AddOns.GetAddOnMetadata or GetAddOnMetadata or function() end)(ADDON, "Version"))
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
    end
  end
  return table.concat(out, "\n")
end
ns.BuildExport = buildExport

refreshers[3] = function()
  box:SetText(buildExport())
  box:HighlightText()
  box:SetFocus()
end

---------------------------------------------------------------------------------------------
-- Page 4: Commands
---------------------------------------------------------------------------------------------
local pCmd = newPage()
local cmdHint = pCmd:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
cmdHint:SetPoint("TOPLEFT", 4, -2)
cmdHint:SetJustifyH("LEFT")
cmdHint:SetText(T.cmd_hint)
local cmdDesc = {}
for i, c in ipairs(T.cmds) do
  local y = -26 - (i - 1) * 46
  local name = pCmd:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
  name:SetPoint("TOPLEFT", 4, y)
  name:SetText("|cff4fd1c5" .. c[2] .. "|r")
  local desc = pCmd:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
  desc:SetPoint("TOPLEFT", 4, y - 16)
  desc:SetWidth(W - 110)
  desc:SetJustifyH("LEFT")
  desc:SetText(c[3])
  cmdDesc[i] = desc
  if c[1] then
    local b = CreateFrame("Button", nil, pCmd, "UIPanelButtonTemplate")
    b:SetSize(70, 20)
    b:SetPoint("TOPRIGHT", -4, y)
    b:SetText(T.run)
    b:SetScript("OnClick", function() SlashCmdList.BROKENMETAWEIGHTS(c[1]) end)
  end
end

refreshers[4] = function()
  local ids = ns.classSpecs()
  for i, c in ipairs(T.cmds) do
    if c[3]:find("%%s") then
      cmdDesc[i]:SetText(c[3]:format(ids[1] or "warrior_fury") .. "\n|cff888888" .. table.concat(ids, ", ") .. "|r")
    end
  end
end

---------------------------------------------------------------------------------------------
-- Entry points
---------------------------------------------------------------------------------------------
function ns.ToggleHub()
  if hub:IsShown() then hub:Hide() else hub:Show(); showPage(current) end
end

function ns.ShowExport()
  hub:Show(); showPage(3)
end

function ns.OnDataChanged()
  if hub:IsShown() and refreshers[current] then refreshers[current]() end
end
