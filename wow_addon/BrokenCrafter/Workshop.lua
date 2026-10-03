-- Broken Meta : Profession > Workshop, and the shopping list of the Leveling tab.
--   Profitable crafts: the recipes you know whose item sells on the auction house for more than its
--     reagents cost (after the house's 5% cut), priced like the Leveling tab (ns.ReagentPrice).
--   Recipes to learn: the recipes of your profession you don't know yet, up to 25 points above your
--     skill, with where to get them (trainer, vendor, drop) from the site's profession data.
--   Shopping list: every reagent the rest of your leveling route needs, minus what you already carry.
local ADDON = ...
local ns = BrokenMetaNS -- Broken Meta : HUB's namespace, shared by the suite
ns.Modules.BrokenCrafter = true
local IS_FR = ns.IS_FR

local T = ns.Localize("workshop", {
  tab = "Atelier", mode_profit = "Crafts rentables", mode_learn = "Recettes à apprendre",
  profit_info = "Tes recettes qui se revendent plus cher qu'elles ne coûtent (prix HV moins 5 % de commission).",
  profit_none = "Aucun craft rentable avec tes prix actuels.",
  learn_info = "Recettes de %s jusqu'au niveau %d que tu ne connais pas encore.",
  learn_none = "Tu connais déjà toutes les recettes accessibles à ton niveau.",
  no_recipes = "Ouvre une fois ta fenêtre de métier pour que l'addon connaisse tes recettes.",
  empty_rec_t = "Recettes pas encore enregistrées", empty_scan_t = "Prix de l'hôtel des ventes manquants",
  empty_none_t = "Rien à afficher", go_leveling = "Aller à l'onglet Montée",
  no_scan = "Scanne l'hôtel des ventes (onglet Montée) pour voir les crafts rentables.",
  no_prof = "Tu n'as aucun métier d'artisanat avec des données de recettes.",
  cost = "coût %s", ah = "HV %s", margin = "+%s",
  src_t = "Entraîneur", src_v = "Marchand", src_d = "Butin ou quête", src_s = "De base",
  src_vn = "Marchand : %s", lvl = "niv. %d", useful = "utile pour monter",
  page = "Page %d/%d",
  shop_btn = "Liste de courses", shop_title = "Liste de courses : %s",
  shop_info = "Composants du reste du parcours, moins ce que tu as dans tes sacs (et ta banque si tu l'as ouverte). Clique sur un composant, hôtel des ventes ouvert, pour le chercher.",
  shop_total = "À acheter : %s", shop_have = "tu as %d", shop_done = "Tu as déjà tout ce qu'il faut.",
}, {
  tab = "Workshop", mode_profit = "Profitable crafts", mode_learn = "Recipes to learn",
  profit_info = "Your recipes that sell for more than they cost (AH price minus the 5% cut).",
  profit_none = "No profitable craft with your current prices.",
  learn_info = "%s recipes up to skill %d that you don't know yet.",
  learn_none = "You already know every recipe available at your skill.",
  no_recipes = "Open your profession window once so the addon knows your recipes.",
  empty_rec_t = "Recipes not recorded yet", empty_scan_t = "Auction house prices missing",
  empty_none_t = "Nothing to show", go_leveling = "Go to the Leveling tab",
  no_scan = "Scan the auction house (Leveling tab) to see profitable crafts.",
  no_prof = "You have no crafting profession with recipe data.",
  cost = "cost %s", ah = "AH %s", margin = "+%s",
  src_t = "Trainer", src_v = "Vendor", src_d = "Drop or quest", src_s = "Starting recipe",
  src_vn = "Vendor: %s", lvl = "lvl %d", useful = "good for leveling",
  page = "Page %d/%d",
  shop_btn = "Shopping list", shop_title = "Shopping list: %s",
  shop_info = "Reagents for the rest of the route, minus what you carry (and your bank once opened). Click a reagent, auction house open, to search for it.",
  shop_total = "To buy: %s", shop_have = "you have %d", shop_done = "You already have everything you need.",
})
ns.WorkshopTexts = T

if not ns.HubTab or not ns.RECIPES then return end
local W, C, HEX = ns.Hub.W, ns.C, ns.HEX
local LOC = IS_FR and 1 or 2
local AH_CUT = 0.95

local function itemName(id)
  local n = ns.ITEM_NAMES and ns.ITEM_NAMES[id]
  return n and (n[LOC] or n[2]) or (ns.GetItemInfo and select(1, ns.GetItemInfo(id))) or ("#" .. id)
end
ns.ItemName = itemName

local function itemIcon(key)
  if key > 0 then
    return (C_Item and C_Item.GetItemIconByID and C_Item.GetItemIconByID(key)) or (GetItemIcon and GetItemIcon(key))
      or "Interface\\Icons\\INV_Misc_QuestionMark"
  end
  return (C_Spell and C_Spell.GetSpellTexture and C_Spell.GetSpellTexture(-key)) or (GetSpellTexture and GetSpellTexture(-key))
    or "Interface\\Icons\\INV_Misc_QuestionMark"
end

-- "id:n:k[:v],..." -> { { id, n, k, v } } (cached).
local decoded = {}
local function reagents(str)
  if decoded[str] then return decoded[str] end
  local list = {}
  for id, n, k, v in (str or ""):gmatch("(%d+):(%d+):(%a)%:?(%d*)") do
    list[#list + 1] = { id = tonumber(id), n = tonumber(n), k = k, v = tonumber(v) }
  end
  decoded[str] = list
  return list
end
ns.DecodeReagents = reagents

-- Pricing view of a profession for ns.ReagentPrice: "made" = the recipes of crafted reagents.
local views = {}
local function view(line)
  if views[line] then return views[line] end
  local made = setmetatable({}, { __index = function(t, id)
    local r = ns.RECIPES[line] and ns.RECIPES[line][id]
    if not r then return nil end
    local v = { n = r.q or 1, reag = reagents(r.r) }
    rawset(t, id, v)
    return v
  end })
  views[line] = { made = made }
  return views[line]
end

-- Cost of ONE crafted item of a recipe (copper), or nil when a reagent has no price.
function ns.CraftCost(line, key, prices)
  local r = ns.RECIPES[line] and ns.RECIPES[line][key]
  if not r then return nil end
  local total = 0
  for _, g in ipairs(reagents(r.r)) do
    local u = ns.ReagentPrice(view(line), g, prices, 0)
    if not u then return nil end
    total = total + u * g.n
  end
  return total / (r.q or 1)
end

local function skillIn(line)
  if GetProfessions and GetProfessionInfo then
    for _, idx in ipairs({ GetProfessions() }) do
      local ok, _, _, rank, max, _, _, l = pcall(GetProfessionInfo, idx)
      if ok and l == line then return rank or 0, max or 0 end
    end
  end
  return nil
end

local function myLines()
  local out = {}
  for line in pairs(ns.RECIPES) do if skillIn(line) then out[#out + 1] = line end end
  table.sort(out)
  if #out == 0 then
    for line in pairs(ns.RECIPES) do out[#out + 1] = line end
    table.sort(out)
  end
  return out
end

-- Profitable crafts of a profession: { key, cost, ah, qty, margin } sorted by margin.
function ns.ProfitableCrafts(line, prices)
  local known = ns.MyRecipes and ns.MyRecipes()[line] or {}
  local out = {}
  for _, key in ipairs(known) do
    local seen = key > 0 and prices and prices[key]
    if seen then
      local cost = ns.CraftCost(line, key, prices)
      if cost then
        local margin = seen[1] * AH_CUT - cost
        if margin > 0 then out[#out + 1] = { key = key, cost = cost, ah = seen[1], qty = seen[2], margin = margin } end
      end
    end
  end
  table.sort(out, function(a, b) return a.margin > b.margin end)
  return out
end

-- Recipes not known yet, up to rank + 25: { key, r } sorted by learn level.
function ns.RecipesToLearn(line, rank)
  local known = {}
  for _, key in ipairs(ns.MyRecipes and ns.MyRecipes()[line] or {}) do known[key] = true end
  local out = {}
  for key, r in pairs(ns.RECIPES[line] or {}) do
    if not known[key] and (r.l or 1) <= rank + 25 then out[#out + 1] = { key = key, r = r } end
  end
  table.sort(out, function(a, b)
    if a.r.l ~= b.r.l then return a.r.l < b.r.l end
    return a.key < b.key
  end)
  return out
end

local function sourceText(r)
  if r.a == "t" then return T.src_t .. (r.ac and (" " .. ns.Money(r.ac)) or "") end
  if r.a == "v" then return (r.np and string.format(T.src_vn, r.np) or T.src_v) .. (r.ac and (" " .. ns.Money(r.ac)) or "") end
  if r.a == "s" then return T.src_s end
  return T.src_d
end

-- A recipe still gives skill points while the rank is below its green threshold.
local function useful(r, rank)
  return r.c and r.c[3] and rank < r.c[3]
end

---------------------------------------------------------------------------------------------
-- Workshop tab
---------------------------------------------------------------------------------------------
local ROWS, LINE, TOP = 16, 23, -54
local refresh
local page, index = ns.HubTab("craft", T.tab, function() refresh() end)
local lineIdx, mode, pageNo = nil, "profit", 1

local profBtn = ns.Button(page)
profBtn:SetSize(200, 22)
profBtn:SetPoint("TOPLEFT", 4, -2)
ns.DropDown(profBtn, page, function()
  local list = {}
  for i, line in ipairs(myLines()) do list[i] = ns.ProfIcon(line, 14) .. (ns.CraftProfName and ns.CraftProfName(line) or tostring(line)) end
  return list
end, function() return lineIdx or 1 end, function(i) lineIdx = i; pageNo = 1; refresh() end)
local modeBtn = ns.Button(page, nil, "pill")
modeBtn:SetSize(170, 22)
modeBtn:SetPoint("LEFT", profBtn, "RIGHT", 8, 0)
modeBtn:SetText(T.mode_profit)
modeBtn:SetScript("OnClick", function() mode = "profit"; pageNo = 1; refresh() end)
local learnBtn = ns.Button(page, nil, "pill")
learnBtn:SetSize(170, 22)
learnBtn:SetPoint("LEFT", modeBtn, "RIGHT", 6, 0)
learnBtn:SetText(T.mode_learn)
learnBtn:SetScript("OnClick", function() mode = "learn"; pageNo = 1; refresh() end)
local info = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
info:SetPoint("TOPLEFT", 4, -30)
info:SetWidth(W - 40)
info:SetJustifyH("LEFT")
ns.Hub.rows(page, ROWS, TOP, LINE, true)
local emptyBox = ns.Callout(page, TOP - 10)

local prevBtn = ns.Button(page)
prevBtn:SetSize(28, 22)
prevBtn:SetPoint("BOTTOMLEFT", 4, 4)
prevBtn:SetText("<")
prevBtn:SetScript("OnClick", function() pageNo = pageNo - 1; refresh() end)
local nextBtn = ns.Button(page)
nextBtn:SetSize(28, 22)
nextBtn:SetPoint("LEFT", prevBtn, "RIGHT", 70, 0)
nextBtn:SetText(">")
nextBtn:SetScript("OnClick", function() pageNo = pageNo + 1; refresh() end)
local pageText = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
pageText:SetPoint("LEFT", prevBtn, "RIGHT", 8, 0)

local function linkOf(key) return key > 0 and ("item:" .. key) or ("spell:" .. -key) end

refresh = function()
  local lines = myLines()
  if #lines == 0 then info:SetText("|c" .. HEX.faint .. T.no_prof .. "|r"); ns.Hub.clearRows(page, 1); return end
  lineIdx = math.min(lineIdx or 1, #lines)
  local line = lines[lineIdx]
  profBtn:SetText(ns.ProfIcon(line, 14) .. (ns.CraftProfName and ns.CraftProfName(line) or tostring(line)) .. "  v")
  if mode == "profit" then modeBtn:LockHighlight(); learnBtn:UnlockHighlight() else learnBtn:LockHighlight(); modeBtn:UnlockHighlight() end
  local rank = skillIn(line) or 0
  local known = ns.MyRecipes and ns.MyRecipes()[line]
  local list, rowsOut = {}, {}
  local empty -- callout shown instead of the (empty) list
  if mode == "profit" then
    local scan = ns.Market and ns.Market()
    if not known then
      empty = { title = T.empty_rec_t, text = T.no_recipes, warn = true }
    elseif not scan then
      empty = { title = T.empty_scan_t, text = T.no_scan, warn = true,
        btn = ns.ShowLeveling and T.go_leveling or nil, onClick = function() if ns.ShowLeveling then ns.ShowLeveling() end end }
    else
      list = ns.ProfitableCrafts(line, scan.prices)
      if #list == 0 then empty = { title = T.empty_none_t, text = T.profit_none } end
    end
    info:SetText(empty and "" or T.profit_info)
    for _, e in ipairs(list) do
      rowsOut[#rowsOut + 1] = { key = e.key,
        left = itemName(e.key) .. "  |c" .. HEX.faint .. string.format(T.cost, ns.Money(e.cost)) .. " · " .. string.format(T.ah, ns.Money(e.ah)) .. "|r",
        right = "|c" .. HEX.teal .. string.format(T.margin, ns.Money(e.margin)) .. "|r" }
    end
  else
    list = ns.RecipesToLearn(line, rank)
    if not known then
      empty = { title = T.empty_rec_t, text = T.no_recipes, warn = true }
    elseif #list == 0 then
      empty = { title = T.empty_none_t, text = T.learn_none }
    end
    info:SetText(empty and "" or string.format(T.learn_info, ns.CraftProfName(line), rank + 25))
    for _, e in ipairs(list) do
      local tag = useful(e.r, rank) and ("  |c" .. HEX.teal .. T.useful .. "|r") or ""
      rowsOut[#rowsOut + 1] = { key = e.key,
        left = "|c" .. HEX.faint .. string.format(T.lvl, e.r.l) .. "|r  " .. itemName(e.key) .. tag,
        right = "|c" .. HEX.dim .. sourceText(e.r) .. "|r" }
    end
    if not known then rowsOut = {} end
  end
  if empty then
    empty.icon = ns.ProfIconPath(line)
    emptyBox:Set(empty)
  else
    emptyBox:Hide()
  end
  local pages = math.max(1, math.ceil(#rowsOut / ROWS))
  pageNo = math.min(math.max(pageNo, 1), pages)
  pageText:SetText(string.format(T.page, pageNo, pages))
  if pageNo > 1 then prevBtn:Enable() else prevBtn:Disable() end
  if pageNo < pages then nextBtn:Enable() else nextBtn:Disable() end
  for i = 1, ROWS do
    local r = rowsOut[(pageNo - 1) * ROWS + i]
    if r then
      ns.Hub.setRow(page, i, r.left, r.right, { icon = itemIcon(r.key), link = linkOf(r.key) })
    else
      ns.Hub.setRow(page, i)
    end
  end
end

---------------------------------------------------------------------------------------------
-- Shopping list (opened from the Leveling tab)
---------------------------------------------------------------------------------------------
local shop, shopRows = nil, {}
local SHOP_ROWS = 16

local function itemCount(id)
  if C_Item and C_Item.GetItemCount then return C_Item.GetItemCount(id, true) or 0 end
  return GetItemCount and GetItemCount(id, true) or 0
end

-- Types the name in the auction house search and starts it (from a click).
local function searchAH(name)
  if AuctionHouseFrame and AuctionHouseFrame:IsShown() and AuctionHouseFrame.SearchBar then
    pcall(function()
      AuctionHouseFrame.SearchBar.SearchBox:SetText(name)
      AuctionHouseFrame.SearchBar:StartSearch()
    end)
  elseif BrowseName and AuctionFrameBrowse_Search then
    pcall(function() BrowseName:SetText(name); AuctionFrameBrowse_Search() end)
  end
end

-- { { id, name, need, have, buy, unit, src } } for the rest of a route, and the total to spend.
function ns.ShoppingList(line, rank)
  local plan = ns.LevelingPlan(line, rank)
  local byId, order = {}, {}
  for _, e in ipairs(plan) do
    for _, r in ipairs(e.reag) do
      local x = byId[r.g.id]
      if not x then
        x = { id = r.g.id, name = r.g.name and (r.g.name[IS_FR and "frFR" or "enUS"] or r.g.name.enUS) or itemName(r.g.id),
          need = 0, unit = r.unit, src = r.src }
        byId[r.g.id] = x
        order[#order + 1] = x
      end
      x.need = x.need + r.qty
    end
  end
  local total = 0
  for _, x in ipairs(order) do
    x.have = itemCount(x.id)
    x.buy = math.max(0, x.need - x.have)
    if x.unit then total = total + x.unit * x.buy end
  end
  table.sort(order, function(a, b) return (a.unit or 0) * a.buy > (b.unit or 0) * b.buy end)
  return order, total
end

local function buildShop()
  shop = ns.Window("BrokenMetaShopping", 460, 520, "", "DIALOG")
  shop:ClearAllPoints()
  shop:SetPoint("CENTER", 320, 0)
  shop.info = shop:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  shop.info:SetPoint("TOPLEFT", 12, -42)
  shop.info:SetWidth(436)
  shop.info:SetJustifyH("LEFT")
  shop.total = shop:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  shop.total:SetPoint("TOPLEFT", 12, -92)
  for i = 1, SHOP_ROWS do
    local b = CreateFrame("Button", nil, shop)
    b:SetSize(436, 22)
    b:SetPoint("TOPLEFT", 12, -114 - (i - 1) * 24)
    b.icon = b:CreateTexture(nil, "ARTWORK")
    b.icon:SetSize(18, 18)
    b.icon:SetPoint("LEFT", 0, 0)
    b.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    b.text = b:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
    b.text:SetPoint("LEFT", b.icon, "RIGHT", 8, 0)
    b.text:SetWidth(260)
    b.text:SetJustifyH("LEFT")
    b.text:SetWordWrap(false)
    b.price = b:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
    b.price:SetPoint("RIGHT", -4, 0)
    b:SetScript("OnEnter", function(self)
      if not self.id then return end
      GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
      if GameTooltip.SetItemByID then GameTooltip:SetItemByID(self.id) else GameTooltip:SetHyperlink("item:" .. self.id) end
      GameTooltip:Show()
    end)
    b:SetScript("OnLeave", function() GameTooltip:Hide() end)
    b:SetScript("OnClick", function(self) if self.name then searchAH(self.name) end end)
    b:Hide()
    shopRows[i] = b
  end
end

function ns.ShowShoppingList(line, rank)
  if not shop then buildShop() end
  local list, total = ns.ShoppingList(line, rank)
  shop.title:SetText(string.format(T.shop_title, ns.CraftProfName and ns.CraftProfName(line) or ""))
  shop.info:SetText(T.shop_info)
  local todo = {}
  for _, x in ipairs(list) do if x.buy > 0 then todo[#todo + 1] = x end end
  shop.total:SetText(#todo > 0 and string.format(T.shop_total, "|c" .. HEX.gold .. ns.Money(total) .. "|r")
    or ("|c" .. HEX.teal .. T.shop_done .. "|r"))
  for i = 1, SHOP_ROWS do
    local x, b = todo[i], shopRows[i]
    if x then
      b.id, b.name = x.id, x.name
      b.icon:SetTexture(itemIcon(x.id))
      b.text:SetText("|c" .. HEX.cream .. x.buy .. "×|r " .. x.name .. (x.have > 0 and ("  |c" .. HEX.faint .. string.format(T.shop_have, x.have) .. "|r") or ""))
      b.price:SetText(x.unit and ns.Money(x.unit * x.buy) or "|cffff5a6b?|r")
      b:Show()
    else
      b:Hide()
    end
  end
  shop:Show()
end
