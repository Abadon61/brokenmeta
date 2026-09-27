-- Broken Meta : Profession > Leveling. The site's optimal route to max out a profession, from the
-- player's current skill, with each reagent priced from the player's latest auction house scan
-- (same rules as the site's profession guides, site_build/wow_ah.py):
--   vendor reagent: the vendor price, unless the auction house is cheaper;
--   farmed / disenchanted: the auction house price, else unknown (never guessed);
--   crafted by the same profession: the cheaper of its auction price and its crafting cost.
-- The auction house scan button lives here too.
local ADDON, ns = ...
local IS_FR = ns.IS_FR

local T = ns.Localize("leveling", {
  tab = "Montée", scan = "Scanner l'hôtel des ventes",
  scan_closed = "Ouvre l'hôtel des ventes pour scanner",
  no_scan = "Aucun scan de ton royaume : ouvre l'hôtel des ventes et clique sur « Scanner » pour avoir les prix du moment.",
  scan_info = "Prix : médiane de %d scan(s) récents, dernier le %s (%s, %s), il y a %s.", stale = "Scan ancien : rescanne pour des prix à jour.",
  skill = "Ton niveau : %d / %d", not_learned = "Tu n'as pas ce métier : parcours complet depuis 1.",
  total = "Reste %d fabrications · composants : %s", unknown = " (%d composant(s) sans prix)",
  done = "Parcours terminé : ton métier est au niveau maximum du guide.",
  step = "%d-%d · %s ×%d", free = "gratuit",
  guide = "Guide complet sur le site", page = "Page %d/%d",
  link_title = "Lien brokenmeta.gg", link_hint = "Le lien est déjà sélectionné : Ctrl+C, puis colle-le dans ton navigateur.",
  hours = "%d h", days = "%d j", minutes = "%d min",
  src_v = "marchand", src_a = "HV", src_c = "fabriqué",
  tip_price = "%d × %s = %s (%s)", tip_noprice = "Pas de prix : absent de ton dernier scan de l'hôtel des ventes.",
  step_total = "Étape", craft_cost = "Coût du craft", ah_price = "Prix HV", ah_none = "absent de ton dernier scan",
}, {
  tab = "Leveling", scan = "Scan the auction house",
  scan_closed = "Open the auction house to scan",
  no_scan = "No scan from your realm: open the auction house and click \"Scan\" to get current prices.",
  scan_info = "Prices: median of %d recent scan(s), latest on %s (%s, %s), %s ago.", stale = "Old scan: scan again for current prices.",
  skill = "Your skill: %d / %d", not_learned = "You don't have this profession: full route from 1.",
  total = "%d crafts left · reagents: %s", unknown = " (%d reagent(s) without a price)",
  done = "Route complete: your profession is at the guide's maximum.",
  step = "%d-%d · %s ×%d", free = "free",
  guide = "Full guide on the site", page = "Page %d/%d",
  link_title = "brokenmeta.gg link", link_hint = "The link is already selected: Ctrl+C, then paste it in your browser.",
  hours = "%dh", days = "%dd", minutes = "%dmin",
  src_v = "vendor", src_a = "AH", src_c = "crafted",
  tip_price = "%d × %s = %s (%s)", tip_noprice = "No price: not in your latest auction house scan.",
  step_total = "Step", craft_cost = "Craft cost", ah_price = "AH price", ah_none = "not in your latest scan",
})

if not ns.HubTab or not ns.PROFESSIONS then return end
local W, C, HEX = ns.Hub.W, ns.C, ns.HEX
local LOC = IS_FR and "frFR" or "enUS"

-- Routes in a fixed order (the ones the player has first, see refresh).
local ORDER = {}
for line in pairs(ns.PROFESSIONS) do ORDER[#ORDER + 1] = line end
table.sort(ORDER, function(a, b) return ns.PROFESSIONS[a].id < ns.PROFESSIONS[b].id end)

-- Gold / silver / copper with the game's coin icons (drawn here: Forever's client has no
-- GetCoinTextureString). Zero parts are left out, except a lone 0 copper.
local COIN = "|TInterface\\MoneyFrame\\UI-%sIcon:12:12:2:0|t"
local function money(copper)
  copper = math.floor(copper + 0.5)
  local g, s, c = math.floor(copper / 10000), math.floor(copper / 100) % 100, copper % 100
  local parts = {}
  if g > 0 then parts[#parts + 1] = g .. COIN:format("Gold") end
  if s > 0 then parts[#parts + 1] = s .. COIN:format("Silver") end
  if c > 0 or #parts == 0 then parts[#parts + 1] = c .. COIN:format("Copper") end
  return table.concat(parts, " ")
end
ns.Money = money

-- Prices of this realm and faction from the scans of the last MARKET_DAYS (the addon keeps 5): per
-- item, the MEDIAN of the lowest unit price seen in each scan (one cheap or overpriced listing in
-- a single scan no longer sets the price), with the quantity of the latest scan holding it.
-- Returns { t = latest scan time, realm, faction, n = scans used, prices = { [itemID] = { unit, qty, scans } } }.
local MARKET_DAYS, STALE_DAYS = 7, 3
local function market()
  local d = ns.Data and ns.Data()
  if not d or not d.ah then return nil end
  local realm, faction, now = GetRealmName(), UnitFactionGroup("player"), time()
  local scans = {}
  for i = #d.ah, 1, -1 do
    local s = d.ah[i]
    if s.realm == realm and s.faction == faction and (now - (s.t or 0)) <= MARKET_DAYS * 86400 then scans[#scans + 1] = s end
  end
  if #scans == 0 then
    -- Nothing recent: the latest scan anyway, flagged as stale by its date.
    for i = #d.ah, 1, -1 do
      local s = d.ah[i]
      if s.realm == realm and s.faction == faction then scans[1] = s; break end
    end
    if #scans == 0 then return nil end
  end
  local seen = {}
  for _, s in ipairs(scans) do -- newest first
    for id, p in pairs(s.prices or {}) do
      local e = seen[id]
      if not e then e = { units = {}, qty = p[2] }; seen[id] = e end
      e.units[#e.units + 1] = p[1]
    end
  end
  local prices = {}
  for id, e in pairs(seen) do
    table.sort(e.units)
    local n = #e.units
    local median = n % 2 == 1 and e.units[(n + 1) / 2] or math.floor((e.units[n / 2] + e.units[n / 2 + 1]) / 2)
    prices[id] = { median, e.qty, n }
  end
  return { t = scans[1].t, realm = scans[1].realm, faction = scans[1].faction, n = #scans, prices = prices,
    stale = (now - (scans[1].t or 0)) > STALE_DAYS * 86400 }
end
ns.Market = market

-- Unit price of a reagent (copper) and where it comes from ("v", "a", "c"), or nil.
local function unitPrice(prof, g, prices, depth)
  local seen = prices and prices[g.id]
  local ah = seen and seen[1] or nil
  if g.k == "v" then
    if ah and ah < (g.v or 0) then return ah, "a" end
    return g.v or 0, "v"
  end
  local best, src = ah, ah and "a" or nil
  local recipe = prof.made and prof.made[g.id]
  if recipe and depth < 3 then
    local total = 0
    for _, sub in ipairs(recipe.reag) do
      local u = unitPrice(prof, sub, prices, depth + 1)
      if not u then total = nil; break end
      total = total + u * sub.n
    end
    if total then
      total = total / math.max(1, recipe.n)
      if not best or total < best then best, src = total, "c" end
    end
  end
  return best, src
end
ns.ReagentPrice = unitPrice

-- The player's skill in a profession line (rank, max) or nil when not learned.
local function skillIn(line)
  if GetProfessions and GetProfessionInfo then
    for _, idx in ipairs({ GetProfessions() }) do
      local ok, _, _, rank, max, _, _, l = pcall(GetProfessionInfo, idx)
      if ok and l == line then return rank or 0, max or 0 end
    end
  end
  return nil
end

-- Remaining steps from a skill: { step, crafts, cost (copper or nil), missing, reag = {...} }.
function ns.LevelingPlan(line, rank)
  local prof = ns.PROFESSIONS[line]
  local scan = market()
  local prices = scan and scan.prices
  local plan, total, missing, crafts = {}, 0, 0, 0
  for _, st in ipairs(prof.steps) do
    if rank < st.t then
      local n = st.c
      if rank > st.f then n = math.ceil(st.c * (st.t - rank) / math.max(1, st.t - st.f)) end
      local cost, priced, lines = 0, true, {}
      for _, g in ipairs(st.reag) do
        local u, src = unitPrice(prof, g, prices, 0)
        local qty = g.n * n
        lines[#lines + 1] = { g = g, qty = qty, unit = u, src = src }
        if u then cost = cost + u * qty else missing = missing + 1; priced = false end
      end
      total = total + cost -- the known part; the unknown reagents are counted in `missing`
      crafts = crafts + n
      -- One crafted item: the reagents of one craft over the items it makes; and its AH price.
      local perCraft = 0
      for _, r in ipairs(lines) do perCraft = r.unit and perCraft + r.unit * r.g.n or nil; if not perCraft then break end end
      local sold = st.item and prices and prices[st.item]
      plan[#plan + 1] = { step = st, crafts = n, cost = priced and cost or nil, reag = lines,
        unitCost = perCraft and perCraft / math.max(1, st.q or 1) or nil, ah = sold and sold[1] or nil }
    end
  end
  return plan, total, missing, crafts, scan
end

---------------------------------------------------------------------------------------------
-- Page
---------------------------------------------------------------------------------------------
local refresh
local page, index = ns.HubTab("prof", T.tab, function() refresh() end)
local profIdx, pageNo = nil, 1

local profBtn = ns.Button(page)
profBtn:SetSize(200, 22)
profBtn:SetPoint("TOPLEFT", 4, -2)
if profBtn.RegisterForClicks then profBtn:RegisterForClicks("LeftButtonUp", "RightButtonUp") end
profBtn:SetScript("OnClick", function(_, button)
  profIdx = ((profIdx or 1) - 1 + (button == "RightButton" and -1 or 1)) % #ORDER + 1
  pageNo = 1
  refresh()
end)
-- A click here counts as the hardware event full scans require.
local scanBtn = ns.Button(page, nil, "primary")
scanBtn:SetSize(220, 22)
scanBtn:SetPoint("TOPRIGHT", -4, -2)
scanBtn:SetScript("OnClick", function() if ns.StartAuctionScan then ns.StartAuctionScan() end end)
local guideBtn = ns.Button(page)
guideBtn:SetSize(170, 20)
guideBtn:SetPoint("BOTTOMRIGHT", -4, 4)
-- Shopping list (Workshop.lua): the reagents the rest of the route needs, minus what you carry.
local shopBtn = ns.Button(page)
shopBtn:SetSize(150, 20)
shopBtn:SetPoint("RIGHT", guideBtn, "LEFT", -8, 0)
guideBtn:SetText(T.guide)

local info = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
info:SetPoint("TOPLEFT", 4, -30)
info:SetWidth(W - 40)
info:SetJustifyH("LEFT")
local summary = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
summary:SetPoint("TOPLEFT", 4, -50)
summary:SetWidth(W - 40)
summary:SetJustifyH("LEFT")
local summary2 = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
summary2:SetPoint("TOPLEFT", 4, -68)
summary2:SetWidth(W - 40)
summary2:SetJustifyH("LEFT")

-- Item tooltips (the game's own, like bags and chat links) on the result icon and on each reagent;
-- shift-click puts the item link in the chat box. extra: lines added under the tooltip.
local function itemTooltip(owner, id, extra)
  if not id then return end
  GameTooltip:SetOwner(owner, "ANCHOR_RIGHT")
  if GameTooltip.SetItemByID then GameTooltip:SetItemByID(id) else GameTooltip:SetHyperlink("item:" .. id) end
  if extra then
    GameTooltip:AddLine(" ")
    for _, l in ipairs(extra) do GameTooltip:AddLine(l) end
  end
  GameTooltip:Show()
end

local function linkToChat(id)
  if not id or not IsModifiedClick or not IsModifiedClick("CHATLINK") then return end
  local link = select(2, ns.GetItemInfo(id))
  if link then
    if ChatEdit_InsertLink then ChatEdit_InsertLink(link) elseif HandleModifiedItemClick then HandleModifiedItemClick(link) end
  end
end

-- A reagent chip: icon, quantity, price (price only in the tooltip when the step has many reagents).
local MAX_CHIPS = 7
local function makeChip(parent)
  local b = CreateFrame("Button", nil, parent)
  b:SetHeight(18)
  b.icon = b:CreateTexture(nil, "ARTWORK")
  b.icon:SetSize(16, 16)
  b.icon:SetPoint("LEFT", 0, 0)
  b.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
  b.text = b:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  b.text:SetPoint("LEFT", b.icon, "RIGHT", 4, 0)
  b:SetScript("OnEnter", function(self) itemTooltip(self, self.id, self.extra) end)
  b:SetScript("OnLeave", function() GameTooltip:Hide() end)
  b:SetScript("OnClick", function(self) linkToChat(self.id) end)
  return b
end

local function setChip(b, r, compact)
  b.id = r.g.id
  b.icon:SetTexture("Interface\\Icons\\" .. (r.g.icon or "INV_Misc_QuestionMark"))
  local price = r.unit and money(r.unit * r.qty) or "|cffff5a6b?|r"
  b.text:SetText("|c" .. HEX.cream .. r.qty .. "×|r" .. (compact and "" or (" |c" .. HEX.dim .. price .. "|r")))
  local line = r.unit and string.format(T.tip_price, r.qty, money(r.unit), money(r.unit * r.qty), T["src_" .. r.src])
    or ("|cffff5a6b" .. T.tip_noprice .. "|r")
  b.extra = { "|c" .. HEX.teal .. "Broken Meta|r  " .. line }
  b:SetWidth(20 + ((b.text.GetStringWidth and b.text:GetStringWidth()) or 60))
  b:Show()
end

-- Step cards: result icon, "from-to · recipe ×crafts", the reagents with their prices, step cost.
local CARDS, TOP, GAP, CARD_H = 6, -90, 60, 54
local cards = {}
for i = 1, CARDS do
  local c = CreateFrame("Frame", nil, page, ns.BACKDROP_TEMPLATE)
  c:SetSize(W - 32, CARD_H)
  c:SetPoint("TOPLEFT", 4, TOP - (i - 1) * GAP)
  ns.Flat(c)
  c.icon = c:CreateTexture(nil, "ARTWORK")
  c.icon:SetSize(34, 34)
  c.icon:SetPoint("LEFT", 8, 0)
  c.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
  c.title = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontName")
  c.title:SetPoint("TOPLEFT", c.icon, "TOPRIGHT", 10, 1)
  c.title:SetWidth(W - 280) -- leaves room for the price column
  c.title:SetJustifyH("LEFT")
  c.title:SetWordWrap(false)
  c.iconBtn = CreateFrame("Button", nil, c)
  c.iconBtn:SetAllPoints(c.icon)
  c.iconBtn:SetScript("OnEnter", function(self) itemTooltip(self, self.id, self.extra) end)
  c.iconBtn:SetScript("OnLeave", function() GameTooltip:Hide() end)
  c.iconBtn:SetScript("OnClick", function(self) linkToChat(self.id) end)
  c.free = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  c.free:SetPoint("TOPLEFT", c.title, "BOTTOMLEFT", 0, -5)
  c.chips = {}
  for j = 1, MAX_CHIPS do
    local chip = makeChip(c)
    if j == 1 then chip:SetPoint("TOPLEFT", c.title, "BOTTOMLEFT", 0, -4)
    else chip:SetPoint("LEFT", c.chips[j - 1], "RIGHT", 7, 0) end
    chip:Hide()
    c.chips[j] = chip
  end
  -- Right column: step total, then one item's crafting cost and its auction house price.
  c.cost = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  c.cost:SetPoint("TOPRIGHT", -10, -6)
  c.cost:SetJustifyH("RIGHT")
  c.unit = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  c.unit:SetPoint("TOPRIGHT", c.cost, "BOTTOMRIGHT", 0, -3)
  c.unit:SetJustifyH("RIGHT")
  c.sell = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  c.sell:SetPoint("TOPRIGHT", c.unit, "BOTTOMRIGHT", 0, -1)
  c.sell:SetJustifyH("RIGHT")
  c:Hide()
  cards[i] = c
end

local prevBtn = ns.Button(page)
prevBtn:SetSize(28, 20)
prevBtn:SetPoint("BOTTOMLEFT", 4, 4)
prevBtn:SetText("<")
prevBtn:SetScript("OnClick", function() pageNo = pageNo - 1; refresh() end)
local nextBtn = ns.Button(page)
nextBtn:SetSize(28, 20)
nextBtn:SetPoint("LEFT", prevBtn, "RIGHT", 70, 0)
nextBtn:SetText(">")
nextBtn:SetScript("OnClick", function() pageNo = pageNo + 1; refresh() end)
local pageText = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
pageText:SetPoint("LEFT", prevBtn, "RIGHT", 8, 0)

local function ago(t)
  local s = math.max(0, time() - (t or 0))
  if s >= 86400 then return string.format(T.days, math.floor(s / 86400)) end
  if s >= 3600 then return string.format(T.hours, math.floor(s / 3600)) end
  return string.format(T.minutes, math.floor(s / 60))
end

refresh = function()
  if not profIdx then
    -- Start on the first route the player has learned.
    profIdx = 1
    for i, line in ipairs(ORDER) do if skillIn(line) then profIdx = i; break end end
  end
  local line = ORDER[profIdx]
  local prof = ns.PROFESSIONS[line]
  profBtn:SetText(prof.name[LOC] or prof.name.enUS)
  local open = ns.IsAuctionOpen and ns.IsAuctionOpen()
  scanBtn:SetText(open and T.scan or T.scan_closed)
  if open then scanBtn:Enable() else scanBtn:Disable() end
  guideBtn:SetScript("OnClick", function()
    ns.ShowCopyText(T.link_title, T.link_hint,
      ns.SiteURL("wow-forever/professions/" .. prof.id .. "/", "leveling"))
  end)

  local rank, max = skillIn(line)
  shopBtn:SetShown(ns.ShowShoppingList ~= nil)
  if ns.WorkshopTexts then shopBtn:SetText(ns.WorkshopTexts.shop_btn) end
  shopBtn:SetScript("OnClick", function() if ns.ShowShoppingList then ns.ShowShoppingList(line, rank or 0) end end)
  local plan, total, missing, crafts, scan = ns.LevelingPlan(line, rank or 0)
  info:SetText(scan and (string.format(T.scan_info, scan.n, date("%d/%m %H:%M", scan.t), scan.realm or "?", scan.faction or "?", ago(scan.t))
      .. (scan.stale and ("  |cffff9900" .. T.stale .. "|r") or ""))
    or ("|c" .. HEX.faint .. T.no_scan .. "|r"))
  summary:SetText(rank and string.format(T.skill, rank, max) or ("|c" .. HEX.faint .. T.not_learned .. "|r"))
  if #plan == 0 then
    summary2:SetText("|c" .. HEX.teal .. T.done .. "|r")
  else
    summary2:SetText(string.format(T.total, crafts, "|c" .. HEX.gold .. money(total) .. "|r")
      .. (missing > 0 and ("|cffff5a6b" .. string.format(T.unknown, missing) .. "|r") or ""))
  end

  local pages = math.max(1, math.ceil(#plan / CARDS))
  pageNo = math.min(math.max(pageNo, 1), pages)
  pageText:SetText(string.format(T.page, pageNo, pages))
  if pageNo > 1 then prevBtn:Enable() else prevBtn:Disable() end
  if pageNo < pages then nextBtn:Enable() else nextBtn:Disable() end
  for i = 1, CARDS do
    local k = (pageNo - 1) * CARDS + i
    local e, c = plan[k], cards[i]
    if e then
      local st = e.step
      c.icon:SetTexture(st.icon and ("Interface\\Icons\\" .. st.icon) or "Interface\\Icons\\INV_Misc_QuestionMark")
      c.title:SetText(string.format(T.step, st.f, st.t, st.name[LOC] or st.name.enUS, e.crafts))
      c.iconBtn.id = st.item
      local compact = #e.reag > 3
      for j = 1, MAX_CHIPS do
        if e.reag[j] then setChip(c.chips[j], e.reag[j], compact) else c.chips[j]:Hide() end
      end
      c.free:SetText(#e.reag == 0 and ("|c" .. HEX.faint .. T.free .. "|r") or "")
      c.cost:SetText(T.step_total .. " " .. (e.cost and money(e.cost) or "|cffff5a6b?|r"))
      c.unit:SetText(T.craft_cost .. " " .. (e.unitCost and money(e.unitCost) or "|cffff5a6b?|r"))
      -- AH price in teal when selling the item is worth more than crafting it.
      local gain = e.ah and e.unitCost and e.ah > e.unitCost
      c.sell:SetText(T.ah_price .. " " .. (e.ah and ((gain and ("|c" .. HEX.teal) or "") .. money(e.ah) .. (gain and "|r" or ""))
        or ("|c" .. HEX.faint .. "—|r")))
      c.iconBtn.extra = {
        "|c" .. HEX.teal .. "Broken Meta|r  " .. T.craft_cost .. " " .. (e.unitCost and money(e.unitCost) or "?"),
        "|c" .. HEX.teal .. "Broken Meta|r  " .. T.ah_price .. " " .. (e.ah and money(e.ah) or T.ah_none),
      }
      ns.FlatBorder(c, k == 1 and C.teal or C.border) -- the step to do now
      c:Show()
    else
      c:Hide()
    end
  end
end

-- Skill-up: refresh if this tab is open (a new scan goes through ns.OnDataChanged, which refreshes
-- the open tab).
local ev = CreateFrame("Frame")
pcall(ev.RegisterEvent, ev, "SKILL_LINES_CHANGED")
ev:SetScript("OnEvent", function() ns.HubRefresh(index) end)
