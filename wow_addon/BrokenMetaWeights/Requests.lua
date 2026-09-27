-- Broken Meta : Profession > Requests: "I'm looking for [item]". A buyer posts a request with one
-- click (a chat line in the hidden channel, like crafter announces, so Blizzard's click rule is kept);
-- every addon player of the realm sees it, crafters who know the recipe are told, and anyone can
-- whisper the buyer. No message is ever sent in anyone's name.
--   BM1 D1;faction;itemID        my request (one per player, replaces the previous one)
--   BM1 D0                       I cancel my request
--   BM1 DQ                       who is looking for something? (opening the tab, a click)
--   whisper D1;faction;itemID;age   answer to DQ from players with an active request (invisible)
local ADDON, ns = ...
local IS_FR = ns.IS_FR

local T = ns.Localize("requests", {
  tab = "Demandes", box = "Objet recherché : nom ou Maj+clic sur l'objet", publish = "Publier ma demande",
  cancel = "Annuler ma demande", refresh = "Actualiser",
  match = "Objet : %s (%s)", no_match = "Aucune recette connue ne fabrique « %s ».", pick = "Tape le nom d'un objet fabricable.",
  mine = "Ta demande : %s, publiée il y a %s. Elle reste visible 30 min.",
  posted = "ta demande pour %s est publiée : les artisans qui ont l'addon la voient.",
  cancelled = "ta demande est retirée.", wait = "patiente un peu avant de republier une demande.",
  none = "Aucune demande en cours. Publie la tienne, ou clique sur Actualiser.",
  you_can = "tu sais le faire", whisper = "MP", ago = "il y a %s",
  alert = "%s cherche %s, et tu sais le fabriquer : Broken Meta : Profession > Demandes.",
  intro = "Tu cherches un objet fabriqué ? Publie une demande : les artisans qui ont la recette sont prévenus et peuvent te contacter. Tu peux aussi écrire toi-même à un joueur ci-dessous.",
}, {
  tab = "Requests", box = "Item wanted: name or shift-click the item", publish = "Post my request",
  cancel = "Cancel my request", refresh = "Refresh",
  match = "Item: %s (%s)", no_match = "No known recipe makes \"%s\".", pick = "Type the name of a craftable item.",
  mine = "Your request: %s, posted %s ago. It stays visible for 30 min.",
  posted = "your request for %s is posted: crafters with the addon can see it.",
  cancelled = "your request is withdrawn.", wait = "wait a little before posting a request again.",
  none = "No request right now. Post yours, or click Refresh.",
  you_can = "you can make it", whisper = "Whisper", ago = "%s ago",
  alert = "%s is looking for %s, and you can make it: Broken Meta : Professions > Requests.",
  intro = "Looking for a crafted item? Post a request: crafters who know the recipe are told and can contact you. You can also whisper a player below yourself.",
})

if not ns.HubTab or not ns.RECIPES then return end
local W, C, HEX = ns.Hub.W, ns.C, ns.HEX
local LOC = IS_FR and 1 or 2
local TTL, REPOST = 1800, 60

local function lowerAscii(s) return (s:gsub("[A-Z]", string.lower)) end

-- Craftable items: itemID -> profession line (every recipe that makes an item).
local craftable
local function craftables()
  if craftable then return craftable end
  craftable = {}
  for line, list in pairs(ns.RECIPES) do
    for key in pairs(list) do if key > 0 then craftable[key] = line end end
  end
  return craftable
end

-- Text typed or an item link -> itemID of a craftable item (exact name first, then "contains").
function ns.ResolveCraftable(text)
  text = text or ""
  local linked = tonumber(text:match("item:(%d+)"))
  if linked then return craftables()[linked] and linked or nil end
  local q = lowerAscii(text:gsub("^%s+", ""):gsub("%s+$", ""))
  if #q < 3 then return nil end
  local best
  for id in pairs(craftables()) do
    local n = ns.ITEM_NAMES[id] and lowerAscii(ns.ITEM_NAMES[id][LOC] or ns.ITEM_NAMES[id][2])
    if n == q then return id end
    if n and not best and n:find(q, 1, true) then best = id end
  end
  return best
end

local requests = {} -- ["Name-Realm"] = { item, t = GetTime() posted, alerted }
local mine = nil    -- { item, t }
local lastPost, lastAsk = -REPOST, -60
function ns.CraftRequests() return requests end

local function knowsRecipe(item)
  local line = craftables()[item]
  for _, key in ipairs(line and ns.MyRecipes and ns.MyRecipes()[line] or {}) do
    if key == item then return true end
  end
  return false
end

local function itemLabel(id)
  local n = ns.ITEM_NAMES[id]
  return "|cffffffff[" .. (n and (n[LOC] or n[2]) or ("#" .. id)) .. "]|r"
end

-- Chat lines (a click): post / cancel / ask.
function ns.PostCraftRequest(item)
  if GetTime() - lastPost < REPOST then return ns.say(T.wait) end
  lastPost = GetTime()
  ns.CraftChat("D1;" .. (UnitFactionGroup("player") or "") .. ";" .. item)
  mine = { item = item, t = GetTime() }
  ns.say(string.format(T.posted, itemLabel(item)))
  if ns.OnRequestsChanged then ns.OnRequestsChanged() end
end

function ns.CancelCraftRequest()
  if not mine then return end
  ns.CraftChat("D0")
  mine = nil
  ns.say(T.cancelled)
  if ns.OnRequestsChanged then ns.OnRequestsChanged() end
end

function ns.AskCraftRequests(force)
  if not force and GetTime() - lastAsk < 60 then return end
  lastAsk = GetTime()
  ns.CraftChat("DQ")
end

function ns.OnRequestMessage(body, who)
  if body == "DQ" then
    -- Our active request, by invisible whisper, with its age so it expires at the same time.
    if mine and GetTime() - mine.t < TTL then
      local age = math.floor(GetTime() - mine.t)
      C_Timer.After(1 + math.random() * 3, function()
        ns.CraftSend("D1;" .. (UnitFactionGroup("player") or "") .. ";" .. mine.item .. ";" .. age, "WHISPER", who)
      end)
    end
    return
  end
  if body == "D0" then
    requests[who] = nil
  else
    local faction, item, age = body:match("^D1;(%a*);(%d+);?(%d*)$")
    item = tonumber(item)
    if not item or not craftables()[item] then return end
    if faction ~= "" and faction ~= UnitFactionGroup("player") then return end
    local r = { item = item, t = GetTime() - (tonumber(age) or 0) }
    local old = requests[who]
    requests[who] = r
    -- A crafter who can make it is told once per request.
    if knowsRecipe(item) and not (old and old.item == item) then
      r.alerted = true
      if not ns.Option or ns.Option("request_alert") then
        ns.say(string.format(T.alert, ns.CraftShortName and ns.CraftShortName(who) or who, itemLabel(item)))
        if PlaySound and SOUNDKIT and SOUNDKIT.TELL_MESSAGE and (not ns.Option or ns.Option("sounds")) then pcall(PlaySound, SOUNDKIT.TELL_MESSAGE) end
      end
    end
  end
  if ns.OnRequestsChanged then ns.OnRequestsChanged() end
end

-- Active requests, newest first: { name, item, age, can }.
function ns.CraftRequestList()
  local out, now = {}, GetTime()
  for name, r in pairs(requests) do
    if now - r.t > TTL then requests[name] = nil
    else out[#out + 1] = { name = name, item = r.item, age = now - r.t, can = knowsRecipe(r.item) } end
  end
  table.sort(out, function(a, b)
    if a.can ~= b.can then return a.can end
    return a.age < b.age
  end)
  return out
end

---------------------------------------------------------------------------------------------
-- Tab
---------------------------------------------------------------------------------------------
local ROWS, TOP, GAP = 12, -118, 28
local refresh
local page, index = ns.HubTab("prof", T.tab, function() refresh() end)
if ns.HubTabButton and ns.HubTabButton(index) then
  ns.HubTabButton(index):HookScript("OnClick", function() ns.AskCraftRequests(false) end)
end

local intro = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
intro:SetPoint("TOPLEFT", 4, -2)
intro:SetWidth(W - 40)
intro:SetJustifyH("LEFT")
intro:SetText(T.intro)
local box = ns.Input(page)
box:SetSize(300, 22)
box:SetPoint("TOPLEFT", 4, -40)
local boxHint = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
boxHint:SetPoint("LEFT", box, "LEFT", 8, 0)
boxHint:SetText("|c" .. HEX.faint .. T.box .. "|r")
local postBtn = ns.Button(page, nil, "primary")
postBtn:SetSize(150, 22)
postBtn:SetPoint("LEFT", box, "RIGHT", 8, 0)
postBtn:SetText(T.publish)
local refreshBtn = ns.Button(page)
refreshBtn:SetSize(96, 22)
refreshBtn:SetPoint("TOPRIGHT", -4, -40)
refreshBtn:SetText(T.refresh)
refreshBtn:SetScript("OnClick", function() ns.AskCraftRequests(true) end)
local preview = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
preview:SetPoint("TOPLEFT", 4, -68)
preview:SetWidth(W - 40)
preview:SetJustifyH("LEFT")
local mineText = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
mineText:SetPoint("TOPLEFT", 4, -90)
mineText:SetWidth(W - 190)
mineText:SetJustifyH("LEFT")
local cancelBtn = ns.Button(page)
cancelBtn:SetSize(150, 20)
cancelBtn:SetPoint("TOPRIGHT", -4, -88)
cancelBtn:SetText(T.cancel)
cancelBtn:SetScript("OnClick", function() ns.CancelCraftRequest() end)

local picked
local function updatePreview()
  local text = box:GetText() or ""
  boxHint:SetShown(text == "" and not box:HasFocus())
  picked = ns.ResolveCraftable(text)
  if text == "" then preview:SetText("|c" .. HEX.faint .. T.pick .. "|r")
  elseif picked then preview:SetText(string.format(T.match, itemLabel(picked), ns.CraftProfName(craftables()[picked])))
  else preview:SetText("|cffff5a6b" .. string.format(T.no_match, text:gsub("|", "")) .. "|r") end
  if picked then postBtn:Enable() else postBtn:Disable() end
end
box:SetScript("OnTextChanged", updatePreview)
box:SetScript("OnEditFocusGained", function() boxHint:Hide() end)
box:SetScript("OnEditFocusLost", function() updatePreview() end)
box:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
box:SetScript("OnEnterPressed", function(self) self:ClearFocus(); if picked then ns.PostCraftRequest(picked) end end)
postBtn:SetScript("OnClick", function() if picked then ns.PostCraftRequest(picked) end end)
-- Shift-click on an item while the box has the focus puts its link here.
if hooksecurefunc and ChatEdit_InsertLink then
  hooksecurefunc("ChatEdit_InsertLink", function(link)
    if box:HasFocus() and type(link) == "string" then box:SetText(link) end
  end)
end

local rows = {}
for i = 1, ROWS do
  local r = CreateFrame("Button", nil, page)
  r:SetSize(W - 32, GAP - 4)
  r:SetPoint("TOPLEFT", 4, TOP - (i - 1) * GAP)
  r.icon = r:CreateTexture(nil, "ARTWORK")
  r.icon:SetSize(20, 20)
  r.icon:SetPoint("LEFT", 0, 0)
  r.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
  r.text = r:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  r.text:SetPoint("LEFT", r.icon, "RIGHT", 8, 0)
  r.text:SetWidth(W - 170)
  r.text:SetJustifyH("LEFT")
  r.text:SetWordWrap(false)
  r.btn = ns.Button(r, nil, "primary")
  r.btn:SetSize(80, 20)
  r.btn:SetPoint("RIGHT", 0, 0)
  r.btn:SetText(T.whisper)
  r:SetScript("OnEnter", function(self)
    if not self.item then return end
    GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
    if GameTooltip.SetItemByID then GameTooltip:SetItemByID(self.item) else GameTooltip:SetHyperlink("item:" .. self.item) end
    GameTooltip:Show()
  end)
  r:SetScript("OnLeave", function() GameTooltip:Hide() end)
  r:Hide()
  rows[i] = r
end
local none = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
none:SetPoint("TOPLEFT", 4, TOP)
none:SetWidth(W - 40)
none:SetJustifyH("LEFT")

refresh = function()
  updatePreview()
  if mine and GetTime() - mine.t < TTL then
    mineText:SetText(string.format(T.mine, itemLabel(mine.item), ns.Ago and ns.Ago(time() - (GetTime() - mine.t)) or ""))
    cancelBtn:Show()
  else
    mine = nil
    mineText:SetText("")
    cancelBtn:Hide()
  end
  local list = ns.CraftRequestList()
  none:SetText(#list == 0 and ("|c" .. HEX.faint .. T.none .. "|r") or "")
  for i = 1, ROWS do
    local e, r = list[i], rows[i]
    if e then
      local icon = (C_Item and C_Item.GetItemIconByID and C_Item.GetItemIconByID(e.item)) or (GetItemIcon and GetItemIcon(e.item))
      r.item = e.item
      r.icon:SetTexture(icon or "Interface\\Icons\\INV_Misc_QuestionMark")
      r.text:SetText("|c" .. HEX.cream .. (ns.CraftShortName and ns.CraftShortName(e.name) or e.name) .. "|r  " .. itemLabel(e.item)
        .. "  |c" .. HEX.faint .. string.format(T.ago, ns.Ago and ns.Ago(time() - e.age) or "") .. "|r"
        .. (e.can and ("  |c" .. HEX.teal .. T.you_can .. "|r") or ""))
      r.btn:SetScript("OnClick", function() if ns.CraftWhisper then ns.CraftWhisper(e.name) end end)
      r:Show()
    else
      r:Hide()
    end
  end
end

function ns.OnRequestsChanged() ns.HubRefresh(index) end
