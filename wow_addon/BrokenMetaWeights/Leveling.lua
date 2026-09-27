-- BrokenMeta : Profession > Leveling. The site's optimal route to max out a profession, from the
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
  scan_info = "Prix du scan du %s (%s, %s), il y a %s.",
  skill = "Ton niveau : %d / %d", not_learned = "Tu n'as pas ce métier : parcours complet depuis 1.",
  total = "Reste %d fabrications · composants : %s", unknown = " (%d composant(s) sans prix)",
  done = "Parcours terminé : ton métier est au niveau maximum du guide.",
  step = "%d-%d · %s ×%d", free = "gratuit",
  guide = "Guide complet sur le site", page = "Page %d/%d",
  link_title = "Lien brokenmeta.gg", link_hint = "Le lien est déjà sélectionné : Ctrl+C, puis colle-le dans ton navigateur.",
  hours = "%d h", days = "%d j", minutes = "%d min",
  src_v = "marchand", src_a = "HV", src_c = "fabriqué",
}, {
  tab = "Leveling", scan = "Scan the auction house",
  scan_closed = "Open the auction house to scan",
  no_scan = "No scan from your realm: open the auction house and click \"Scan\" to get current prices.",
  scan_info = "Prices from the %s scan (%s, %s), %s ago.",
  skill = "Your skill: %d / %d", not_learned = "You don't have this profession: full route from 1.",
  total = "%d crafts left · reagents: %s", unknown = " (%d reagent(s) without a price)",
  done = "Route complete: your profession is at the guide's maximum.",
  step = "%d-%d · %s ×%d", free = "free",
  guide = "Full guide on the site", page = "Page %d/%d",
  link_title = "brokenmeta.gg link", link_hint = "The link is already selected: Ctrl+C, then paste it in your browser.",
  hours = "%dh", days = "%dd", minutes = "%dmin",
  src_v = "vendor", src_a = "AH", src_c = "crafted",
})

if not ns.HubTab or not ns.PROFESSIONS then return end
local W, C, HEX = ns.Hub.W, ns.C, ns.HEX
local LOC = IS_FR and "frFR" or "enUS"

-- Routes in a fixed order (the ones the player has first, see refresh).
local ORDER = {}
for line in pairs(ns.PROFESSIONS) do ORDER[#ORDER + 1] = line end
table.sort(ORDER, function(a, b) return ns.PROFESSIONS[a].id < ns.PROFESSIONS[b].id end)

local function money(copper)
  copper = math.floor(copper + 0.5)
  if GetCoinTextureString then return GetCoinTextureString(copper) end
  local g, s, c = math.floor(copper / 10000), math.floor(copper / 100) % 100, copper % 100
  if g > 0 then return string.format("%dg %ds %dc", g, s, c) end
  if s > 0 then return string.format("%ds %dc", s, c) end
  return string.format("%dc", c)
end
ns.Money = money

-- Latest scan of this realm and faction: { [itemID] = { unit, quantity, listings } }.
local function market()
  local d = ns.Data and ns.Data()
  if not d or not d.ah then return nil end
  local realm, faction = GetRealmName(), UnitFactionGroup("player")
  for i = #d.ah, 1, -1 do
    local s = d.ah[i]
    if s.realm == realm and s.faction == faction then return s end
  end
  return nil
end

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
      plan[#plan + 1] = { step = st, crafts = n, cost = priced and cost or nil, reag = lines }
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
  c.title:SetWidth(W - 210)
  c.title:SetJustifyH("LEFT")
  c.title:SetWordWrap(false)
  c.reag = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  c.reag:SetPoint("TOPLEFT", c.title, "BOTTOMLEFT", 0, -4)
  c.reag:SetWidth(W - 210)
  c.reag:SetJustifyH("LEFT")
  c.reag:SetWordWrap(false)
  c.cost = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  c.cost:SetPoint("RIGHT", -10, 0)
  c.cost:SetJustifyH("RIGHT")
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

local function reagentText(r)
  local name = r.g.name[LOC] or r.g.name.enUS
  local price
  if r.unit then
    price = "|c" .. HEX.dim .. money(r.unit * r.qty) .. " " .. T["src_" .. r.src] .. "|r"
  else
    price = "|cffff5a6b?|r"
  end
  return "|c" .. HEX.cream .. r.qty .. "×|r " .. name .. " " .. price
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
  local plan, total, missing, crafts, scan = ns.LevelingPlan(line, rank or 0)
  info:SetText(scan and string.format(T.scan_info, date("%d/%m %H:%M", scan.t), scan.realm or "?", scan.faction or "?", ago(scan.t))
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
      local parts = {}
      for _, r in ipairs(e.reag) do parts[#parts + 1] = reagentText(r) end
      c.reag:SetText(#parts > 0 and table.concat(parts, "   ") or ("|c" .. HEX.faint .. T.free .. "|r"))
      c.cost:SetText(e.cost and money(e.cost) or "|cffff5a6b?|r")
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
