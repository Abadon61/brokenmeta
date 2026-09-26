-- Auction house price scan. A "BrokenMeta" button appears on the auction house window; one click
-- (a real click is required by the game for full scans) reads every listing and keeps, per item,
-- the lowest unit buyout and the quantity listed. No seller names are read or stored.
-- Forever mixes a Classic game with the modern UI, so both APIs are supported:
--   modern:  C_AuctionHouse.ReplicateItems() + GetReplicateItemInfo(0-based index)
--   classic: QueryAuctionItems(..., getAll = true) + GetAuctionItemInfo("list", i)
local ADDON, ns = ...
local IS_FR = ns.IS_FR
local MAX_SCANS = 5
local CHUNK = 400 -- listings processed per frame, so a big auction house doesn't freeze the game

local T = IS_FR and {
  button = "BrokenMeta : scanner les prix", scanning = "Scan en cours… %d / %d",
  done = "scan de l'hôtel des ventes terminé : %d annonces, %d objets différents.",
  wait = "le jeu n'autorise un scan complet que toutes les 15 minutes environ. Réessaie plus tard.",
  noapi = "aucune fonction de scan de l'hôtel des ventes n'est disponible dans ce client.",
  empty = "le scan n'a renvoyé aucune annonce.",
  closed = "ouvre d'abord l'hôtel des ventes (parle à un commissaire-priseur), puis relance le scan.",
} or {
  button = "BrokenMeta: scan prices", scanning = "Scanning… %d / %d",
  done = "auction house scan done: %d listings, %d distinct items.",
  wait = "the game only allows a full scan about every 15 minutes. Try again later.",
  noapi = "no auction house scan function is available in this client.",
  empty = "the scan returned no listings.",
  closed = "open the auction house first (talk to an auctioneer), then start the scan again.",
}

local function mode()
  if C_AuctionHouse and C_AuctionHouse.ReplicateItems and C_AuctionHouse.GetReplicateItemInfo then return "replicate" end
  if QueryAuctionItems and GetAuctionItemInfo then return "getall" end
  return nil
end
ns.AuctionMode = mode

local btn, scanning, ahOpen = nil, false, false
local events = CreateFrame("Frame")

local function finish(prices, listings)
  scanning = false
  events:UnregisterAllEvents()
  events:RegisterEvent("AUCTION_HOUSE_SHOW")
  events:RegisterEvent("AUCTION_HOUSE_CLOSED")
  if btn then btn:SetText(T.button); btn:Enable() end
  local distinct = 0
  for _ in pairs(prices) do distinct = distinct + 1 end
  if listings == 0 then return ns.say(T.empty) end
  local d = ns.Data()
  table.insert(d.ah, {
    t = time(), realm = GetRealmName(), faction = UnitFactionGroup("player"),
    mode = mode(), listings = listings, prices = prices,
  })
  while #d.ah > MAX_SCANS do table.remove(d.ah, 1) end
  ns.say(string.format(T.done, listings, distinct))
  if ns.OnDataChanged then ns.OnDataChanged() end
end

-- Walks listings [first..last] in chunks; read(i) returns count, buyout, itemID.
local function collect(first, last, read)
  local prices, listings, i = {}, 0, first
  local function step()
    local stop = math.min(i + CHUNK - 1, last)
    for idx = i, stop do
      local count, buyout, itemID = read(idx)
      if itemID and buyout and buyout > 0 and count and count > 0 then
        local unit = math.floor(buyout / count)
        local p = prices[itemID]
        if not p then prices[itemID] = { unit, count, 1 }
        else
          if unit < p[1] then p[1] = unit end
          p[2] = p[2] + count
          p[3] = p[3] + 1
        end
        listings = listings + 1
      end
    end
    if btn then btn:SetText(string.format(T.scanning, stop - first + 1, last - first + 1)) end
    i = stop + 1
    if i <= last then C_Timer.After(0, step) else finish(prices, listings) end
  end
  if last < first then return finish(prices, 0) end
  step()
end

events:SetScript("OnEvent", function(_, event)
  if event == "AUCTION_HOUSE_SHOW" then
    ahOpen = true
    -- The auction frame is load-on-demand: let Blizzard's own handler create it first.
    C_Timer.After(0, ns.ShowAuctionButton)
    C_Timer.After(0.5, ns.ShowAuctionButton)
    if ns.OnDataChanged then ns.OnDataChanged() end
  elseif event == "AUCTION_HOUSE_CLOSED" then
    ahOpen = false
    if btn then btn:Hide() end
    if ns.OnDataChanged then ns.OnDataChanged() end
    if scanning then finish({}, 0) end
  elseif event == "REPLICATE_ITEM_LIST_UPDATE" and scanning then
    events:UnregisterEvent("REPLICATE_ITEM_LIST_UPDATE")
    local n = C_AuctionHouse.GetNumReplicateItems() or 0
    collect(0, n - 1, function(i)
      -- name, texture, count, quality, usable, level, levelType, minBid, minIncrement, buyout, bid,
      -- highBidder, bidder, owner, ownerFull, saleStatus, itemID, hasAllInfo
      local _, _, count, _, _, _, _, _, _, buyout, _, _, _, _, _, _, itemID = C_AuctionHouse.GetReplicateItemInfo(i)
      return count, buyout, itemID
    end)
  elseif event == "AUCTION_ITEM_LIST_UPDATE" and scanning then
    events:UnregisterEvent("AUCTION_ITEM_LIST_UPDATE")
    local n = GetNumAuctionItems("list") or 0
    collect(1, n, function(i)
      local _, _, count, _, _, _, _, _, _, buyout, _, _, _, _, _, _, itemID = GetAuctionItemInfo("list", i)
      return count, buyout, itemID
    end)
  end
end)
events:RegisterEvent("AUCTION_HOUSE_SHOW")
events:RegisterEvent("AUCTION_HOUSE_CLOSED")

-- Must run from a click (hardware event): full-scan APIs refuse otherwise.
function ns.IsAuctionOpen() return ahOpen end

function ns.StartAuctionScan()
  if scanning then return end
  if not ahOpen then return ns.say(T.closed) end
  local m = mode()
  if m == "replicate" then
    scanning = true
    pcall(events.RegisterEvent, events, "REPLICATE_ITEM_LIST_UPDATE")
    C_AuctionHouse.ReplicateItems()
  elseif m == "getall" then
    local _, canAll = CanSendAuctionQuery()
    if not canAll then return ns.say(T.wait) end
    scanning = true
    events:RegisterEvent("AUCTION_ITEM_LIST_UPDATE")
    QueryAuctionItems("", nil, nil, 0, false, 0, true, false, nil)
  else
    return ns.say(T.noapi)
  end
  if btn then btn:Disable(); btn:SetText(string.format(T.scanning, 0, 0)) end
end

-- Parented to UIParent and anchored just under the auction window: inside Forever's (modern)
-- auction frame the first version was hidden behind its own layers (0.5.1 fix, seen in game).
function ns.ShowAuctionButton()
  if not ahOpen then return end
  local anchor = AuctionHouseFrame or AuctionFrame
  if not anchor then return end
  if not btn then
    btn = CreateFrame("Button", "BrokenMetaAuctionScanButton", UIParent, "UIPanelButtonTemplate")
    btn:SetSize(240, 24)
    btn:SetFrameStrata("DIALOG")
    btn:SetScript("OnClick", ns.StartAuctionScan)
    local icon = btn:CreateTexture(nil, "ARTWORK")
    icon:SetSize(16, 16)
    icon:SetPoint("LEFT", 6, 0)
    icon:SetTexture(ns.ICON)
  end
  btn:ClearAllPoints()
  btn:SetPoint("TOPRIGHT", anchor, "BOTTOMRIGHT", 0, -4)
  if not scanning then btn:SetText(T.button); btn:Enable() end
  btn:Show()
end
