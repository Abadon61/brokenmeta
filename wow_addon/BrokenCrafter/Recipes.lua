-- Broken Meta : Profession > recipes. A crafter's learned recipes are recorded when they open their
-- profession window; a buyer who clicks "Recipes" on a crafter card (or searches an item) asks for
-- them through an invisible addon whisper, and the crafter's addon answers by itself.
--
-- Recipe entry: the crafted item's ID, or minus the spell ID for recipes that make no item
-- (enchantments). Messages (prefix BMCraft, whisper):
--   R1?                                  send me your recipes
--   R1;line;seq;total;e,e,e              one chunk of one profession's recipes (line 0: none)
local ADDON = ...
local ns = BrokenMetaNS -- Broken Meta : HUB's namespace, shared by the suite
ns.Modules.BrokenCrafter = true
local IS_FR = ns.IS_FR

local T = ns.Localize("recipes", {
  button = "Recettes", title = "Recettes de %s", mine = "Mes recettes",
  loading = "Demande envoyée à %s…",
  none_mine = "Aucune recette enregistrée : ouvre une fois ta fenêtre de métier (touche K ou ton livre de sorts) pour que l'addon les note.",
  none_other = "%s n'a partagé aucune recette : il doit ouvrir une fois sa fenêtre de métier, avec la version 0.12 de l'addon ou plus.",
  no_answer = "Pas de réponse de %s : il est peut-être déconnecté ou a une ancienne version de l'addon.",
  saved = "%d recettes de %s enregistrées : les autres joueurs de l'addon peuvent les consulter dans l'annuaire des artisans.",
  search = "Filtrer…", count = "%d recette(s)", page = "Page %d/%d",
  knows = "Sait faire : %s",
}, {
  button = "Recipes", title = "%s's recipes", mine = "My recipes",
  loading = "Request sent to %s…",
  none_mine = "No recipes recorded: open your profession window once (K key or your spellbook) so the addon notes them.",
  none_other = "%s has shared no recipes: they must open their profession window once, with addon version 0.12 or later.",
  no_answer = "No answer from %s: they may be offline or running an older version of the addon.",
  saved = "%d %s recipes recorded: other addon players can browse them in the crafters directory.",
  search = "Filter…", count = "%d recipe(s)", page = "Page %d/%d",
  knows = "Can make: %s",
})
ns.RecipeTexts = T

local function lowerAscii(s) return (s:gsub("[A-Z]", string.lower)) end

---------------------------------------------------------------------------------------------
-- Names of entries (items load asynchronously: nil until the client has them)
---------------------------------------------------------------------------------------------
local names = {}
local function entryName(e)
  if names[e] then return names[e] end
  local n
  if e > 0 then
    n = ns.GetItemInfo and select(1, ns.GetItemInfo(e)) or nil
    if not n and C_Item and C_Item.RequestLoadItemDataByID then pcall(C_Item.RequestLoadItemDataByID, e) end
  else
    local id = -e
    if C_Spell and C_Spell.GetSpellName then n = C_Spell.GetSpellName(id)
    elseif GetSpellInfo then n = GetSpellInfo(id) end
  end
  names[e] = n
  return n
end
ns.RecipeEntryName = entryName

local function entryIcon(e)
  if e > 0 then
    local icon = (C_Item and C_Item.GetItemIconByID and C_Item.GetItemIconByID(e)) or (GetItemIcon and GetItemIcon(e))
    return icon or "Interface\\Icons\\INV_Misc_QuestionMark"
  end
  local icon = (C_Spell and C_Spell.GetSpellTexture and C_Spell.GetSpellTexture(-e)) or (GetSpellTexture and GetSpellTexture(-e))
  return icon or "Interface\\Icons\\INV_Misc_QuestionMark"
end

---------------------------------------------------------------------------------------------
-- My recipes, recorded from the profession window
---------------------------------------------------------------------------------------------
local function charKey() return (UnitName("player") or "?") .. "-" .. (GetRealmName() or "") end
local function store()
  BrokenMetaWeightsDB = BrokenMetaWeightsDB or {}
  BrokenMetaWeightsDB.recipes = BrokenMetaWeightsDB.recipes or {}
  local k = charKey()
  BrokenMetaWeightsDB.recipes[k] = BrokenMetaWeightsDB.recipes[k] or {}
  return BrokenMetaWeightsDB.recipes[k]
end
ns.MyRecipes = store

local function idFromLink(link, kind)
  return type(link) == "string" and tonumber(link:match(kind .. ":(%d+)")) or nil
end

-- The profession the open window shows, as a skill line ID (164 Blacksmithing...).
local function openLine()
  local ui = C_TradeSkillUI
  if ui and ui.GetBaseProfessionInfo then
    local ok, info = pcall(ui.GetBaseProfessionInfo)
    if ok and info and info.professionID and info.professionID > 0 then return info.professionID end
  end
  if ui and ui.GetTradeSkillLine then
    local ok, id = pcall(ui.GetTradeSkillLine)
    if ok and type(id) == "number" and id > 0 then return id end
  end
  local name = (GetTradeSkillLine and GetTradeSkillLine()) or nil
  if (not name or name == "UNKNOWN") and GetCraftDisplaySkillLine then name = GetCraftDisplaySkillLine() end
  return name and ns.CraftLineFromName and ns.CraftLineFromName(name) or nil
end

local function readModern()
  local ui, list = C_TradeSkillUI, {}
  local ok, ids = pcall(ui.GetAllRecipeIDs)
  if not ok or type(ids) ~= "table" then return list end
  for _, id in ipairs(ids) do
    local okI, info = pcall(ui.GetRecipeInfo, id)
    if okI and info and info.learned then
      local item
      if ui.GetRecipeSchematic then
        local okS, sc = pcall(ui.GetRecipeSchematic, id, false)
        if okS and sc then item = sc.outputItemID end
      end
      if not item and ui.GetRecipeItemLink then item = idFromLink(ui.GetRecipeItemLink(id), "item") end
      list[#list + 1] = item or -id
    end
  end
  return list
end

local function readClassic()
  local list = {}
  if GetNumTradeSkills and GetTradeSkillInfo then
    for i = 1, GetNumTradeSkills() or 0 do
      local _, kind = GetTradeSkillInfo(i)
      if kind and kind ~= "header" and kind ~= "subheader" then
        local item = GetTradeSkillItemLink and idFromLink(GetTradeSkillItemLink(i), "item")
        local spell = GetTradeSkillRecipeLink and idFromLink(GetTradeSkillRecipeLink(i), "enchant")
        list[#list + 1] = item or (spell and -spell) or nil
      end
    end
  end
  if #list == 0 and GetNumCrafts and GetCraftInfo then -- Classic Enchanting used the Craft window
    for i = 1, GetNumCrafts() or 0 do
      local _, _, kind = GetCraftInfo(i)
      if kind and kind ~= "header" then
        local link = GetCraftItemLink and GetCraftItemLink(i)
        local item, spell = idFromLink(link, "item"), idFromLink(link, "enchant")
        list[#list + 1] = item or (spell and -spell) or nil
      end
    end
  end
  return list
end

function ns.CaptureRecipes()
  local line = openLine()
  if not line then return nil end
  local list = (C_TradeSkillUI and C_TradeSkillUI.GetAllRecipeIDs) and readModern() or {}
  if #list == 0 then list = readClassic() end
  if #list == 0 then return nil end
  local seen, clean = {}, {}
  for _, e in ipairs(list) do if not seen[e] then seen[e] = true; clean[#clean + 1] = e end end
  table.sort(clean)
  local before = store()[line]
  store()[line] = clean
  if not before or #before ~= #clean then
    ns.say(string.format(T.saved, #clean, ns.CraftProfName and ns.CraftProfName(line) or tostring(line)))
  end
  ns.LastRecipeCapture = line .. ": " .. #clean
  if ns.OnRecipesChanged then ns.OnRecipesChanged() end
  return line, #clean
end

---------------------------------------------------------------------------------------------
-- Sharing
---------------------------------------------------------------------------------------------
local cache = {}     -- ["Name-Realm"] = { t = GetTime(), lines = { [line] = { entries } }, done = bool }
local answered = {}  -- ["Name-Realm"] = GetTime() of our last answer
local FRESH = 600

function ns.PeerRecipes(name) return cache[name] end

function ns.RequestRecipes(name, force)
  local c = cache[name]
  if c and not force and (c.pending or GetTime() - c.t < FRESH) then return end
  cache[name] = { t = GetTime(), lines = c and c.lines or {}, pending = true, done = c and c.done }
  ns.CraftSend("R1?", "WHISPER", name)
  C_Timer.After(8, function()
    local now = cache[name]
    if now and now.pending then now.pending = false; now.noAnswer = not now.done; if ns.OnRecipesChanged then ns.OnRecipesChanged() end end
  end)
  if ns.OnRecipesChanged then ns.OnRecipesChanged() end
end

local function answer(who)
  if answered[who] and GetTime() - answered[who] < 20 then return end
  answered[who] = GetTime()
  local msgs = {}
  for line, list in pairs(store()) do
    local chunks, cur = {}, {}
    for _, e in ipairs(list) do
      cur[#cur + 1] = e
      if #table.concat(cur, ",") > 200 then chunks[#chunks + 1] = cur; cur = {} end
    end
    if #cur > 0 then chunks[#chunks + 1] = cur end
    for i, ch in ipairs(chunks) do
      msgs[#msgs + 1] = "R1;" .. line .. ";" .. i .. ";" .. #chunks .. ";" .. table.concat(ch, ",")
    end
  end
  if #msgs == 0 then msgs[1] = "R1;0;1;1;" end
  for i, m in ipairs(msgs) do C_Timer.After((i - 1) * 0.2, function() ns.CraftSend(m, "WHISPER", who) end) end
end

function ns.OnRecipeMessage(body, who)
  if body == "R1?" then return answer(who) end
  local line, seq, total, data = body:match("^R1;(%d+);(%d+);(%d+);([%-%d,]*)$")
  if not line then return end
  line, seq, total = tonumber(line), tonumber(seq), tonumber(total)
  local c = cache[who] or { t = GetTime(), lines = {} }
  cache[who] = c
  c.t, c.pending, c.noAnswer, c.done = GetTime(), false, false, true
  if line > 0 then
    if seq == 1 then c.lines[line] = {} end
    local l = c.lines[line] or {}
    c.lines[line] = l
    for e in data:gmatch("[%-%d]+") do l[#l + 1] = tonumber(e) end
  end
  if ns.OnRecipesChanged then ns.OnRecipesChanged() end
end

-- All entries of someone ({ {e, line} }), mine included.
local function entriesOf(name, mine)
  local lines = mine and store() or (cache[name] and cache[name].lines) or {}
  local out = {}
  for line, list in pairs(lines) do for _, e in ipairs(list) do out[#out + 1] = { e = e, line = line } end end
  return out
end
ns.RecipeEntries = entriesOf

-- Names of someone's recipes matching a search (at most 3), and how many match.
function ns.RecipeMatches(name, query, mine)
  local q = lowerAscii(query)
  local found, n = {}, 0
  for _, r in ipairs(entriesOf(name, mine)) do
    local label = entryName(r.e)
    if label and lowerAscii(label):find(q, 1, true) then
      n = n + 1
      if #found < 3 then found[#found + 1] = label end
    end
  end
  return found, n
end

---------------------------------------------------------------------------------------------
-- Recipes window
---------------------------------------------------------------------------------------------
local win, rows, current, filter, pageNo = nil, {}, nil, "", 1
local ROWS, ROW_H = 15, 23
local refreshWin

local function tooltip(owner, e)
  if not e then return end
  GameTooltip:SetOwner(owner, "ANCHOR_RIGHT")
  if e > 0 then
    if GameTooltip.SetItemByID then GameTooltip:SetItemByID(e) else GameTooltip:SetHyperlink("item:" .. e) end
  elseif GameTooltip.SetSpellByID then
    GameTooltip:SetSpellByID(-e)
  end
  GameTooltip:Show()
end

local function linkToChat(e)
  if not e or not IsModifiedClick or not IsModifiedClick("CHATLINK") then return end
  local link
  if e > 0 then link = select(2, ns.GetItemInfo(e)) elseif GetSpellLink then link = GetSpellLink(-e) end
  if link and ChatEdit_InsertLink then ChatEdit_InsertLink(link) end
end

local function build()
  local W = 440
  win = ns.Window("BrokenMetaRecipes", W, 486, "", "DIALOG")
  win:ClearAllPoints()
  win:SetPoint("CENTER", 300, 0)
  local box = ns.Input(win)
  box:SetSize(W - 150, 22)
  box:SetPoint("TOPLEFT", 12, -44)
  box:SetScript("OnTextChanged", function(self) filter = self:GetText() or ""; pageNo = 1; refreshWin() end)
  box:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
  win.box = box
  win.hint = win:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  win.hint:SetPoint("LEFT", box, "RIGHT", 10, 0)
  win.status = win:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  win.status:SetPoint("TOPLEFT", 12, -76)
  win.status:SetWidth(W - 24)
  win.status:SetJustifyH("LEFT")
  for i = 1, ROWS do
    local b = CreateFrame("Button", nil, win)
    b:SetSize(W - 24, ROW_H - 2)
    b:SetPoint("TOPLEFT", 12, -76 - (i - 1) * ROW_H)
    b.icon = b:CreateTexture(nil, "ARTWORK")
    b.icon:SetSize(18, 18)
    b.icon:SetPoint("LEFT", 0, 0)
    b.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    b.text = b:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
    b.text:SetPoint("LEFT", b.icon, "RIGHT", 8, 0)
    b.text:SetWidth(W - 170)
    b.text:SetJustifyH("LEFT")
    b.text:SetWordWrap(false)
    b.prof = b:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
    b.prof:SetPoint("RIGHT", -4, 0)
    b:SetScript("OnEnter", function(self) tooltip(self, self.e) end)
    b:SetScript("OnLeave", function() GameTooltip:Hide() end)
    b:SetScript("OnClick", function(self) linkToChat(self.e) end)
    b:Hide()
    rows[i] = b
  end
  local prev = ns.Button(win)
  prev:SetSize(28, 22)
  prev:SetPoint("BOTTOMLEFT", 12, 10)
  prev:SetText("<")
  prev:SetScript("OnClick", function() pageNo = pageNo - 1; refreshWin() end)
  local nxt = ns.Button(win)
  nxt:SetSize(28, 22)
  nxt:SetPoint("LEFT", prev, "RIGHT", 70, 0)
  nxt:SetText(">")
  nxt:SetScript("OnClick", function() pageNo = pageNo + 1; refreshWin() end)
  local pageText = win:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  pageText:SetPoint("LEFT", prev, "RIGHT", 8, 0)
  win.prev, win.next, win.pageText = prev, nxt, pageText
end

refreshWin = function()
  if not win or not win:IsShown() or not current then return end
  local mine = current.mine
  win.title:SetText(mine and T.mine or string.format(T.title, current.short))
  local all = entriesOf(current.name, mine)
  local q = lowerAscii(filter or "")
  local list = {}
  for _, r in ipairs(all) do
    local label = entryName(r.e)
    if q == "" or (label and lowerAscii(label):find(q, 1, true)) then list[#list + 1] = { e = r.e, line = r.line, label = label } end
  end
  table.sort(list, function(a, b)
    if (a.label ~= nil) ~= (b.label ~= nil) then return a.label ~= nil end
    if a.label and b.label and a.label ~= b.label then return a.label < b.label end
    return a.e < b.e
  end)
  win.hint:SetText(string.format(T.count, #list))
  local c = not mine and cache[current.name] or nil
  local status = ""
  if #all == 0 then
    if mine then status = T.none_mine
    elseif c and c.pending then status = string.format(T.loading, current.short)
    elseif c and c.noAnswer then status = string.format(T.no_answer, current.short)
    else status = string.format(T.none_other, current.short) end
  end
  win.status:SetText(status ~= "" and ("|c" .. ns.HEX.faint .. status .. "|r") or "")
  local pages = math.max(1, math.ceil(#list / ROWS))
  pageNo = math.min(math.max(pageNo, 1), pages)
  win.pageText:SetText(string.format(T.page, pageNo, pages))
  if pageNo > 1 then win.prev:Enable() else win.prev:Disable() end
  if pageNo < pages then win.next:Enable() else win.next:Disable() end
  for i = 1, ROWS do
    local r, b = (#all > 0) and list[(pageNo - 1) * ROWS + i] or nil, rows[i]
    if r then
      b.e = r.e
      b.icon:SetTexture(entryIcon(r.e))
      b.text:SetText(r.label or ("|c" .. ns.HEX.faint .. "…|r"))
      b.prof:SetText(ns.CraftProfName and ns.CraftProfName(r.line) or "")
      b:Show()
    else
      b:Hide()
    end
  end
end

-- Opens the recipes of a crafter (asks for them when needed) or mine.
function ns.ShowRecipes(name, mine)
  if not win then build() end
  current = { name = name, mine = mine, short = (name or ""):gsub("[%-%s].*$", "") }
  filter, pageNo = "", 1
  win.box:SetText("")
  win:Show()
  if mine then ns.CaptureRecipes() else ns.RequestRecipes(name) end
  refreshWin()
end

-- Something changed (answer received, item names loaded, new capture): refresh what is open.
local refreshPending = false
function ns.OnRecipesChanged()
  if refreshPending then return end
  refreshPending = true
  C_Timer.After(0.3, function()
    refreshPending = false
    refreshWin()
    if ns.OnCraftChanged then ns.OnCraftChanged() end
  end)
end

local ev = CreateFrame("Frame")
for _, e in ipairs({ "TRADE_SKILL_SHOW", "TRADE_SKILL_LIST_UPDATE", "TRADE_SKILL_DATA_SOURCE_CHANGED", "CRAFT_SHOW",
    "CRAFT_UPDATE", "GET_ITEM_INFO_RECEIVED" }) do
  pcall(ev.RegisterEvent, ev, e)
end
local capturePending = false
ev:SetScript("OnEvent", function(_, event, itemID)
  if event == "GET_ITEM_INFO_RECEIVED" then
    if itemID and names[itemID] == nil then
      names[itemID] = nil
      ns.OnRecipesChanged()
    end
    return
  end
  -- The window fills over several events: record once it settles.
  if capturePending then return end
  capturePending = true
  C_Timer.After(1, function() capturePending = false; ns.CaptureRecipes() end)
end)
