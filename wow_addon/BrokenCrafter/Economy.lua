-- Broken Meta : Economy. Everything built on the player's own auction house scans (Auction.lua,
-- prices = ns.Market(), the median of the recent scans of this realm and faction):
--   Inventory   what the bags are worth: auction price vs vendor price, the better one, the total;
--   Prices      one item's price now and in every stored scan (name, or shift-click the item);
--   Deals       items listed well under their usual price in the latest scan, and the resale margin.
-- Also an "AH price" line in item tooltips (Core.lua calls ns.TooltipAHLine).
local ADDON = ...
local ns = BrokenMetaNS -- Broken Meta : HUB's namespace, shared by the suite
ns.Modules.BrokenCrafter = true
local IS_FR = ns.IS_FR

local T = ns.Localize("economy", {
  tab_inv = "Inventaire", tab_price = "Prix", tab_deals = "Bonnes affaires",
  scan = "Scanner l'hôtel des ventes", scan_closed = "Ouvre l'hôtel des ventes pour scanner",
  no_scan = "Aucun scan de ton royaume : ouvre l'hôtel des ventes et scanne-le pour voir les prix.",
  inv_total = "Tes sacs valent %s à l'hôtel des ventes (%s chez le marchand).",
  inv_none = "Rien à vendre dans tes sacs.", ah = "HV %s", vendor = "marchand %s", best_ah = "vends à l'HV", best_vendor = "vends au marchand",
  price_box = "Objet : nom ou Maj+clic", price_now = "Prix actuel (médiane) : %s · %d en vente dans le dernier scan",
  price_none = "Cet objet n'apparaît dans aucun de tes scans.", price_pick = "Tape le nom d'un objet ou fais Maj+clic dessus.",
  price_scan = "Scan du %s", price_absent = "absent",
  deals_info = "Objets vendus au moins 30 % sous leur prix habituel (médiane de tes scans précédents). Marge après la commission de 5 %.",
  deals_none = "Aucune bonne affaire dans ton dernier scan (il faut au moins 3 scans).", deals_t = "Aucune bonne affaire pour l'instant", deal = "%s au lieu de %s", margin = "+%s",
  tooltip = "Prix HV", tooltip_n = "médiane de %d scan(s)", page = "Page %d/%d",
}, {
  tab_inv = "Inventory", tab_price = "Prices", tab_deals = "Deals",
  scan = "Scan the auction house", scan_closed = "Open the auction house to scan",
  no_scan = "No scan from your realm: open the auction house and scan it to see prices.",
  inv_total = "Your bags are worth %s at the auction house (%s at a vendor).",
  inv_none = "Nothing to sell in your bags.", ah = "AH %s", vendor = "vendor %s", best_ah = "sell at the AH", best_vendor = "sell to a vendor",
  price_box = "Item: name or shift-click", price_now = "Current price (median): %s · %d listed in the latest scan",
  price_none = "This item is in none of your scans.", price_pick = "Type an item name or shift-click it.",
  price_scan = "Scan of %s", price_absent = "not listed",
  deals_info = "Items listed at least 30% under their usual price (median of your previous scans). Margin after the 5% cut.",
  deals_none = "No deal in your latest scan (it takes at least 3 scans).", deals_t = "No deal for now", deal = "%s instead of %s", margin = "+%s",
  tooltip = "AH price", tooltip_n = "median of %d scan(s)", page = "Page %d/%d",
})

local AH_CUT = 0.95
local function money(c) return ns.Money and ns.Money(c) or tostring(c) end

-- "AH price" tooltip line for an item ID, or nil (no scan / not in the scans).
function ns.TooltipAHLine(itemID)
  local m = itemID and ns.Market and ns.Market()
  local p = m and m.prices[itemID]
  if not p then return nil end
  return "|cff2de6c4Broken Meta|r  " .. T.tooltip .. " : |cffffffff" .. money(p[1]) .. "|r  |cff7a7e96(" .. string.format(T.tooltip_n, p[3] or 1) .. ")|r"
end

-- Registered with the HUB's single tooltip hook (order 3: after BrokenDPS's DPS line and
-- BrokenCodex's loot-source line).
ns.AddTooltipHandler(function(tt, link)
  if ns.Option and not ns.Option("tooltip_ah") then return false end
  local itemID = link and tonumber(link:match("item:(%d+)"))
  local line = ns.TooltipAHLine(itemID)
  if not line then return false end
  tt:AddLine(line)
  return true
end, 3)

-- /bmw ah and /bmw craft: scan the auction house, open the crafter directory.
ns.RegisterCommand("ah", function() if ns.StartAuctionScan then ns.StartAuctionScan() end end)
ns.RegisterCommand("craft", function() if ns.ShowCrafters then ns.ShowCrafters() end end)

if not ns.HubTab then return end
local W, C, HEX = ns.Hub.W, ns.C, ns.HEX

local Container = C_Container or {}
local GetNumSlots = Container.GetContainerNumSlots or GetContainerNumSlots
local GetBagLink = Container.GetContainerItemLink or GetContainerItemLink

local function stackCount(bag, slot)
  if Container.GetContainerItemInfo then
    local info = Container.GetContainerItemInfo(bag, slot)
    if type(info) == "table" then return info.stackCount or 1 end
  end
  if GetContainerItemInfo then return select(2, GetContainerItemInfo(bag, slot)) or 1 end
  return 1
end

local function itemIcon(id)
  return (C_Item and C_Item.GetItemIconByID and C_Item.GetItemIconByID(id)) or (GetItemIcon and GetItemIcon(id))
    or "Interface\\Icons\\INV_Misc_QuestionMark"
end

-- Bag contents grouped by item: { id, link, count, ah (unit or nil), vendor (unit), value }.
function ns.BagValues()
  local scan = ns.Market and ns.Market()
  local prices = scan and scan.prices or {}
  local byId, out = {}, {}
  for bag = 0, (NUM_BAG_SLOTS or 4) do
    for slot = 1, (GetNumSlots and GetNumSlots(bag) or 0) do
      local link = GetBagLink and GetBagLink(bag, slot)
      local id = link and tonumber(link:match("item:(%d+)"))
      if id then
        local x = byId[id]
        if not x then
          x = { id = id, link = link, count = 0, ah = prices[id] and prices[id][1] or nil,
            vendor = (ns.GetItemInfo and select(11, ns.GetItemInfo(link))) or 0 }
          byId[id] = x
          out[#out + 1] = x
        end
        x.count = x.count + stackCount(bag, slot)
      end
    end
  end
  local totalAH, totalVendor = 0, 0
  for _, x in ipairs(out) do
    local ahNet = x.ah and x.ah * AH_CUT or 0
    x.value = math.max(ahNet, x.vendor or 0) * x.count
    x.bestAH = ahNet > (x.vendor or 0)
    totalAH = totalAH + (x.bestAH and ahNet or (x.vendor or 0)) * x.count
    totalVendor = totalVendor + (x.vendor or 0) * x.count
  end
  table.sort(out, function(a, b) return a.value > b.value end)
  return out, totalAH, totalVendor, scan
end

-- Every stored scan of this realm and faction, newest first: { t, unit or nil, qty }.
function ns.PriceHistory(id)
  local d = ns.Data and ns.Data()
  local realm, faction = GetRealmName(), UnitFactionGroup("player")
  local out = {}
  for i = #(d and d.ah or {}), 1, -1 do
    local s = d.ah[i]
    if s.realm == realm and s.faction == faction then
      local p = s.prices and s.prices[id]
      out[#out + 1] = { t = s.t, unit = p and p[1], qty = p and p[2] or 0 }
    end
  end
  return out
end

-- Deals of the latest scan: listed under 70% of the median of the previous scans (3 scans at least).
function ns.AuctionDeals()
  local d = ns.Data and ns.Data()
  local realm, faction = GetRealmName(), UnitFactionGroup("player")
  local scans = {}
  for i = #(d and d.ah or {}), 1, -1 do
    local s = d.ah[i]
    if s.realm == realm and s.faction == faction then scans[#scans + 1] = s end
  end
  if #scans < 3 then return {} end
  local latest, out = scans[1], {}
  for id, p in pairs(latest.prices or {}) do
    local units = {}
    for k = 2, #scans do
      local q = scans[k].prices and scans[k].prices[id]
      if q then units[#units + 1] = q[1] end
    end
    if #units >= 2 then
      table.sort(units)
      local n = #units
      local usual = n % 2 == 1 and units[(n + 1) / 2] or (units[n / 2] + units[n / 2 + 1]) / 2
      if usual >= 100 and p[1] < usual * 0.7 then
        out[#out + 1] = { id = id, now = p[1], usual = usual, qty = p[2], margin = usual * AH_CUT - p[1] }
      end
    end
  end
  table.sort(out, function(a, b) return a.margin > b.margin end)
  return out
end

-- Scan button + status line shared by the tabs.
local function scanHeader(page, refresh)
  local b = ns.Button(page, nil, "primary")
  b:SetSize(230, 22)
  b:SetPoint("TOPRIGHT", -4, -2)
  b:SetScript("OnClick", function() if ns.StartAuctionScan then ns.StartAuctionScan() end end)
  local info = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  info:SetPoint("TOPLEFT", 4, -30)
  info:SetWidth(W - 40)
  info:SetJustifyH("LEFT")
  return function()
    local open = ns.IsAuctionOpen and ns.IsAuctionOpen()
    b:SetText(open and T.scan or T.scan_closed)
    if open then b:Enable() else b:Disable() end
  end, info
end

local function pager(page, refresh, state)
  local prev = ns.Button(page)
  prev:SetSize(28, 22)
  prev:SetPoint("BOTTOMLEFT", 4, 4)
  prev:SetText("<")
  prev:SetScript("OnClick", function() state.page = state.page - 1; refresh() end)
  local nxt = ns.Button(page)
  nxt:SetSize(28, 22)
  nxt:SetPoint("LEFT", prev, "RIGHT", 70, 0)
  nxt:SetText(">")
  nxt:SetScript("OnClick", function() state.page = state.page + 1; refresh() end)
  local text = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  text:SetPoint("LEFT", prev, "RIGHT", 8, 0)
  return function(total, per)
    local pages = math.max(1, math.ceil(total / per))
    state.page = math.min(math.max(state.page, 1), pages)
    text:SetText(string.format(T.page, state.page, pages))
    if state.page > 1 then prev:Enable() else prev:Disable() end
    if state.page < pages then nxt:Enable() else nxt:Disable() end
    return (state.page - 1) * per
  end
end

---------------------------------------------------------------------------------------------
-- Inventory
---------------------------------------------------------------------------------------------
local ROWS = 17
do
  local refresh
  ns.HubSection("eco", ns.HubTexts.sec_eco, 30, "BrokenCrafter")
  local page = ns.HubTab("eco", T.tab_inv, function() refresh() end)
  local state = { page = 1 }
  local updScan, info = scanHeader(page)
  local total = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  total:SetPoint("TOPLEFT", 4, -48)
  total:SetWidth(W - 40)
  total:SetJustifyH("LEFT")
  ns.Hub.rows(page, ROWS, -72, 22, true)
  local paging = pager(page, function() refresh() end, state)
  refresh = function()
    updScan()
    local list, totalAH, totalVendor, scan = ns.BagValues()
    info:SetText(scan and "" or ("|c" .. HEX.gold .. T.no_scan .. "|r"))
    local shown = {}
    for _, x in ipairs(list) do if x.value > 0 then shown[#shown + 1] = x end end
    total:SetText(#shown > 0 and string.format(T.inv_total, "|c" .. HEX.gold .. money(totalAH) .. "|r", money(totalVendor))
      or ("|c" .. HEX.faint .. T.inv_none .. "|r"))
    local first = paging(#shown, ROWS)
    for i = 1, ROWS do
      local x = shown[first + i]
      if x then
        local detail = {}
        if x.ah then detail[#detail + 1] = string.format(T.ah, money(x.ah)) end
        if (x.vendor or 0) > 0 then detail[#detail + 1] = string.format(T.vendor, money(x.vendor)) end
        ns.Hub.setRow(page, i, x.count .. "× " .. x.link .. "  |c" .. HEX.faint .. table.concat(detail, " · ") .. "|r",
          "|c" .. (x.bestAH and HEX.teal or HEX.dim) .. money(x.value) .. "|r", { icon = itemIcon(x.id), link = x.link })
      else
        ns.Hub.setRow(page, i)
      end
    end
  end
end

---------------------------------------------------------------------------------------------
-- Prices
---------------------------------------------------------------------------------------------
do
  local refresh
  local page = ns.HubTab("eco", T.tab_price, function() refresh() end)
  local updScan = scanHeader(page)
  local box = ns.Input(page)
  box:SetSize(W - 290, 22)
  box:SetPoint("TOPLEFT", 4, -2)
  local hint = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  hint:SetPoint("LEFT", box, "LEFT", 8, 0)
  hint:SetText("|c" .. HEX.faint .. T.price_box .. "|r")
  local head = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  head:SetPoint("TOPLEFT", 4, -34)
  head:SetWidth(W - 40)
  head:SetJustifyH("LEFT")
  ns.Hub.rows(page, 8, -60, 20)
  local picked

  -- Name typed -> item ID: known names (crafting data), then the bags and the latest scan's cached items.
  local function lowerAscii(s) return (s:gsub("[A-Z]", string.lower)) end
  local function resolve(text)
    local linked = tonumber((text or ""):match("item:(%d+)"))
    if linked then return linked end
    local q = lowerAscii((text or ""):gsub("^%s+", ""):gsub("%s+$", ""))
    if #q < 3 then return nil end
    local loc = IS_FR and 1 or 2
    for id, n in pairs(ns.ITEM_NAMES or {}) do
      if id > 0 and lowerAscii(n[loc] or n[2]) == q then return id end
    end
    local m = ns.Market and ns.Market()
    for id in pairs(m and m.prices or {}) do
      local n = ns.GetItemInfo and ns.GetItemInfo(id)
      if n and lowerAscii(n):find(q, 1, true) then return id end
    end
    return nil
  end

  box:SetScript("OnTextChanged", function(self)
    hint:SetShown((self:GetText() or "") == "" and not self:HasFocus())
    picked = resolve(self:GetText())
    refresh()
  end)
  box:SetScript("OnEditFocusGained", function() hint:Hide() end)
  box:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
  if hooksecurefunc and ChatEdit_InsertLink then
    hooksecurefunc("ChatEdit_InsertLink", function(link)
      if box:HasFocus() and type(link) == "string" then box:SetText(link) end
    end)
  end

  refresh = function()
    updScan()
    if not picked then
      head:SetText("|c" .. HEX.faint .. T.price_pick .. "|r")
      ns.Hub.clearRows(page, 1)
      return
    end
    local m = ns.Market and ns.Market()
    local p = m and m.prices[picked]
    local name = (ns.GetItemInfo and ns.GetItemInfo(picked)) or (ns.ItemName and ns.ItemName(picked)) or ("#" .. picked)
    head:SetText(p and ("|cffffffff" .. name .. "|r   " .. string.format(T.price_now, "|c" .. HEX.gold .. money(p[1]) .. "|r", p[2]))
      or ("|cffffffff" .. name .. "|r   |c" .. HEX.faint .. T.price_none .. "|r"))
    local hist = ns.PriceHistory(picked)
    for i = 1, 8 do
      local h = hist[i]
      if h then
        ns.Hub.setRow(page, i, string.format(T.price_scan, date("%d/%m %H:%M", h.t)),
          h.unit and (money(h.unit) .. "  |c" .. HEX.faint .. "×" .. h.qty .. "|r") or ("|c" .. HEX.faint .. T.price_absent .. "|r"))
      else
        ns.Hub.setRow(page, i)
      end
    end
  end
end

---------------------------------------------------------------------------------------------
-- Deals
---------------------------------------------------------------------------------------------
do
  local refresh
  local page = ns.HubTab("eco", T.tab_deals, function() refresh() end)
  local state = { page = 1 }
  local updScan, info = scanHeader(page)
  local emptyBox = ns.Callout(page, -64)
  ns.Hub.rows(page, ROWS, -56, 22, true)
  local paging = pager(page, function() refresh() end, state)
  refresh = function()
    updScan()
    local list = ns.AuctionDeals()
    info:SetText(#list > 0 and T.deals_info or "")
    if #list == 0 then
      emptyBox:Set({ icon = "Interface\\Icons\\INV_Misc_Coin_01", title = T.deals_t, text = T.deals_none })
    else
      emptyBox:Hide()
    end
    local first = paging(#list, ROWS)
    for i = 1, ROWS do
      local x = list[first + i]
      if x then
        local name = (ns.GetItemInfo and ns.GetItemInfo(x.id)) or (ns.ItemName and ns.ItemName(x.id)) or ("#" .. x.id)
        ns.Hub.setRow(page, i, name .. "  |c" .. HEX.faint .. string.format(T.deal, money(x.now), money(x.usual)) .. " · ×" .. x.qty .. "|r",
          "|c" .. HEX.teal .. string.format(T.margin, money(x.margin)) .. "|r", { icon = itemIcon(x.id), link = "item:" .. x.id })
      else
        ns.Hub.setRow(page, i)
      end
    end
  end
end
