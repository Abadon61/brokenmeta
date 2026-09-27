-- BrokenMeta : Profession. A live directory of the crafters who run the addon: each client joins a
-- hidden chat channel and announces its professions, skill levels and a "available" flag through
-- addon messages (the addon has no internet). Searching lists who is online right now, and the
-- whisper button opens a /w to them.
--
-- Messages (prefix BMCraft):
--   Q1                              a newcomer asks everyone for their profile (answered by whisper)
--   P1;avail;level;class;faction;line:rank:max,line:rank:max   a profile
local ADDON, ns = ...
local IS_FR = ns.IS_FR
local LOCALE = GetLocale()

local T = ns.Localize("craft", {
  tab_dir = "Artisans", tab_me = "Mon profil",
  all = "Tous les métiers", only_avail = "Dispo seulement", everyone = "Tout le monde",
  count = "%d artisan(s) connecté(s), %d disponible(s)",
  none = "Aucun artisan connecté pour l'instant. L'annuaire ne montre que les joueurs qui ont l'addon, sur ton royaume et ta faction.",
  whisper = "MP", you = "toi", page = "Page %d/%d",
  avail_on = "Disponible", avail_off = "Indisponible",
  avail_hint_on = "Tu apparais en vert dans l'annuaire : les joueurs peuvent te chuchoter pour un craft. Clique pour te rendre indisponible.",
  avail_hint_off = "Tu apparais en gris dans l'annuaire. Clique pour te rendre disponible et recevoir des demandes de craft.",
  my_profs = "Tes métiers", no_prof = "Tu n'as aucun métier d'artisanat : tu peux quand même chercher des artisans.",
  net_ok = "Connecté au réseau BrokenMeta (%d joueur(s) avec l'addon vus).",
  net_wait = "Connexion au réseau BrokenMeta en cours…",
  net_fail = "Impossible de rejoindre le canal BrokenMeta : trop de canaux ouverts ? Quitte-en un puis tape /reload.",
  intro = "BrokenMeta : Profession montre les artisans connectés qui ont l'addon. Mets-toi disponible pour recevoir des demandes, ou cherche un artisan dans l'onglet Artisans et clique sur MP pour lui écrire.",
  avail_now = "tu es maintenant disponible dans l'annuaire des artisans.",
  avail_gone = "tu n'es plus disponible dans l'annuaire des artisans.",
}, {
  tab_dir = "Crafters", tab_me = "My profile",
  all = "All professions", only_avail = "Available only", everyone = "Everyone",
  count = "%d crafter(s) online, %d available",
  none = "No crafter online right now. The directory only shows players who run the addon, on your realm and faction.",
  whisper = "Whisper", you = "you", page = "Page %d/%d",
  avail_on = "Available", avail_off = "Unavailable",
  avail_hint_on = "You show up in green in the directory: players can whisper you for a craft. Click to become unavailable.",
  avail_hint_off = "You show up in grey in the directory. Click to become available and get craft requests.",
  my_profs = "Your professions", no_prof = "You have no crafting profession: you can still search for crafters.",
  net_ok = "Connected to the BrokenMeta network (%d player(s) with the addon seen).",
  net_wait = "Connecting to the BrokenMeta network…",
  net_fail = "Could not join the BrokenMeta channel: too many channels open? Leave one, then type /reload.",
  intro = "BrokenMeta : Professions shows the online crafters who run the addon. Set yourself available to get requests, or look for a crafter in the Crafters tab and click Whisper to message them.",
  avail_now = "you are now available in the crafters directory.",
  avail_gone = "you are no longer available in the crafters directory.",
})

local PREFIX, CHANNEL = "BMCraft", "BrokenMetaCraft"
local HEARTBEAT, EXPIRE = 300, 720 -- seconds: profile re-sent every 5 min, dropped after 12 min of silence

-- Crafting professions (skill line IDs), in the order of the filter.
local CRAFTS = { 164, 165, 197, 171, 202, 333, 755, 773, 185, 129 }
local NAMES = {
  [164] = { "Forge", "Blacksmithing", "Schmiedekunst", "Herrería" },
  [165] = { "Travail du cuir", "Leatherworking", "Lederverarbeitung", "Peletería" },
  [197] = { "Couture", "Tailoring", "Schneiderei", "Sastrería" },
  [171] = { "Alchimie", "Alchemy", "Alchimie", "Alquimia" },
  [202] = { "Ingénierie", "Engineering", "Ingenieurskunst", "Ingeniería" },
  [333] = { "Enchantement", "Enchanting", "Verzauberkunst", "Encantamiento" },
  [755] = { "Joaillerie", "Jewelcrafting", "Juwelierskunst", "Joyería" },
  [773] = { "Calligraphie", "Inscription", "Inschriftenkunde", "Inscripción" },
  [185] = { "Cuisine", "Cooking", "Kochkunst", "Cocina" },
  [129] = { "Secourisme", "First Aid", "Erste Hilfe", "Primeros auxilios" },
}
local IS_CRAFT = {}
for _, line in ipairs(CRAFTS) do IS_CRAFT[line] = true end
local LANG = (LOCALE == "frFR" and 1) or (LOCALE == "deDE" and 3) or ((LOCALE == "esES" or LOCALE == "esMX") and 4) or 2

local function profName(line)
  local n = NAMES[line]
  return n and n[LANG] or ("#" .. tostring(line))
end

local realm = (GetNormalizedRealmName and GetNormalizedRealmName()) or (GetRealmName() or ""):gsub("[%s%-]", "")
local myName = UnitName("player")
local myFull = myName .. "-" .. realm
local charKey = myName .. "-" .. (GetRealmName() or "")

local function full(sender)
  if not sender or sender == "" then return nil end
  if not sender:find("-", 1, true) then return sender .. "-" .. realm end
  return sender
end

local function short(name)
  if Ambiguate then return Ambiguate(name, "none") end
  return (name:gsub("%-" .. realm .. "$", ""))
end

---------------------------------------------------------------------------------------------
-- My profile
---------------------------------------------------------------------------------------------
local function db()
  BrokenMetaWeightsDB = BrokenMetaWeightsDB or {}
  BrokenMetaWeightsDB.craft = BrokenMetaWeightsDB.craft or {}
  BrokenMetaWeightsDB.craft[charKey] = BrokenMetaWeightsDB.craft[charKey] or { avail = false }
  return BrokenMetaWeightsDB.craft[charKey]
end

-- Crafting professions as { line, rank, max }: modern API first, Classic skill list fallback.
local function myProfessions()
  local out = {}
  if GetProfessions and GetProfessionInfo then
    for _, idx in ipairs({ GetProfessions() }) do
      local ok, _, _, rank, max, _, _, line = pcall(GetProfessionInfo, idx)
      if ok and line and IS_CRAFT[line] then out[#out + 1] = { line = line, rank = rank or 0, max = max or 0 } end
    end
  elseif GetNumSkillLines and GetSkillLineInfo then
    for i = 1, GetNumSkillLines() do
      local name, header, _, rank, _, _, max = GetSkillLineInfo(i)
      if name and not header then
        for line, n in pairs(NAMES) do
          for _, loc in ipairs(n) do
            if loc == name then out[#out + 1] = { line = line, rank = rank or 0, max = max or 0 } end
          end
        end
      end
    end
  end
  return out
end

local function profileMessage()
  local parts = {}
  for _, p in ipairs(myProfessions()) do parts[#parts + 1] = p.line .. ":" .. p.rank .. ":" .. p.max end
  local _, class = UnitClass("player")
  return "P1;" .. (db().avail and 1 or 0) .. ";" .. (UnitLevel("player") or 0) .. ";" .. (class or "")
    .. ";" .. (UnitFactionGroup("player") or "") .. ";" .. table.concat(parts, ","), #parts
end

local function parseProfile(msg)
  local avail, level, class, faction, profs = msg:match("^P1;([01]);(%d+);(%u*);(%a*);(.*)$")
  if not avail then return nil end
  local list = {}
  for line, rank, max in profs:gmatch("(%d+):(%d+):(%d+)") do
    list[#list + 1] = { line = tonumber(line), rank = tonumber(rank), max = tonumber(max) }
  end
  return { avail = avail == "1", level = tonumber(level), class = class, faction = faction, profs = list }
end

---------------------------------------------------------------------------------------------
-- Network
---------------------------------------------------------------------------------------------
local peers = {} -- ["Name-Realm"] = profile + seen
local channelId = 0
local joinFailed = false

local function send(msg, kind, target)
  if not (C_ChatInfo and C_ChatInfo.SendAddonMessage) then return end
  pcall(C_ChatInfo.SendAddonMessage, PREFIX, msg, kind, target)
end

local function broadcast()
  if channelId == 0 then return end
  local msg, n = profileMessage()
  if n > 0 then send(msg, "CHANNEL", channelId) end
end

local lastBroadcast = -HEARTBEAT
local pending = false
-- Several changes in a row (skill-ups, toggles) end up as one message.
local function broadcastSoon()
  if pending then return end
  pending = true
  C_Timer.After(2, function() pending = false; lastBroadcast = GetTime(); broadcast() end)
end

local function hideChannel()
  for i = 1, (NUM_CHAT_WINDOWS or 1) do
    local frame = _G["ChatFrame" .. i] or (i == 1 and DEFAULT_CHAT_FRAME)
    if frame and ChatFrame_RemoveChannel then pcall(ChatFrame_RemoveChannel, frame, CHANNEL) end
  end
end

local function join(attempt)
  if JoinTemporaryChannel then pcall(JoinTemporaryChannel, CHANNEL) end
  local id = GetChannelName and GetChannelName(CHANNEL) or 0
  if id and id > 0 then
    channelId = id
    hideChannel()
    send("Q1", "CHANNEL", channelId)
    broadcastSoon()
  elseif attempt < 5 then
    C_Timer.After(3, function() join(attempt + 1) end)
  else
    joinFailed = true
  end
  if ns.OnCraftChanged then ns.OnCraftChanged() end
end

-- The join / leave notices of the hidden channel stay out of the chat.
if ChatFrame_AddMessageEventFilter then
  ChatFrame_AddMessageEventFilter("CHAT_MSG_CHANNEL_NOTICE", function(_, _, _, _, _, _, _, _, _, _, name)
    return name == CHANNEL
  end)
end

function ns.SetCraftAvailable(on)
  db().avail = on and true or false
  ns.say(on and T.avail_now or T.avail_gone)
  broadcastSoon()
  if ns.OnCraftChanged then ns.OnCraftChanged() end
end

function ns.CraftPeers() return peers end

local f = CreateFrame("Frame")
for _, ev in ipairs({ "PLAYER_LOGIN", "CHAT_MSG_ADDON", "CHAT_MSG_SYSTEM", "SKILL_LINES_CHANGED", "PLAYER_LOGOUT" }) do
  pcall(f.RegisterEvent, f, ev)
end
f:SetScript("OnEvent", function(_, event, prefix, msg, kind, sender)
  if event == "PLAYER_LOGIN" then
    if C_ChatInfo and C_ChatInfo.RegisterAddonMessagePrefix then pcall(C_ChatInfo.RegisterAddonMessagePrefix, PREFIX) end
    db()
    C_Timer.After(6, function() join(1) end)
  elseif event == "CHAT_MSG_ADDON" then
    if prefix ~= PREFIX or type(msg) ~= "string" then return end
    local who = full(sender)
    if not who or who == myFull then return end
    if msg == "Q1" then
      -- Answer the newcomer directly, a little later so answers don't all arrive at once.
      local reply, n = profileMessage()
      if n > 0 then C_Timer.After(1 + math.random() * 6, function() send(reply, "WHISPER", who) end) end
    else
      local p = parseProfile(msg)
      if p and (p.faction == "" or p.faction == (UnitFactionGroup("player") or p.faction)) then
        p.seen = GetTime()
        peers[who] = p
        if ns.OnCraftChanged then ns.OnCraftChanged() end
      end
    end
  elseif event == "CHAT_MSG_SYSTEM" then
    -- "No player named X is currently playing": X logged off, drop them.
    if type(prefix) ~= "string" or not ERR_CHAT_PLAYER_NOT_FOUND_S then return end
    local pattern = "^" .. ERR_CHAT_PLAYER_NOT_FOUND_S:gsub("([%^%$%(%)%.%[%]%*%+%-%?])", "%%%1"):gsub("%%s", "(.+)") .. "$"
    local gone = prefix:match(pattern)
    if gone then
      for name in pairs(peers) do
        if name == gone or name == full(gone) or short(name) == gone then peers[name] = nil end
      end
      if ns.OnCraftChanged then ns.OnCraftChanged() end
    end
  elseif event == "SKILL_LINES_CHANGED" then
    if channelId > 0 then broadcastSoon() end
  elseif event == "PLAYER_LOGOUT" then
    -- Tell the others we left (best effort: the client may not flush it before quitting).
    local msg, n = profileMessage()
    if channelId > 0 and n > 0 then send((msg:gsub("^P1;[01];", "P1;0;")), "CHANNEL", channelId) end
  end
end)

-- Heartbeat and expiry (OnUpdate rather than a repeating timer).
local elapsed = 0
f:SetScript("OnUpdate", function(_, dt)
  elapsed = elapsed + dt
  if elapsed < 10 then return end
  elapsed = 0
  local now = GetTime()
  if channelId > 0 and now - lastBroadcast >= HEARTBEAT then lastBroadcast = now; broadcast() end
  local changed = false
  for name, p in pairs(peers) do
    if now - p.seen > EXPIRE then peers[name] = nil; changed = true end
  end
  if changed and ns.OnCraftChanged then ns.OnCraftChanged() end
end)

---------------------------------------------------------------------------------------------
-- Hub pages
---------------------------------------------------------------------------------------------
if not ns.HubTab then return end
local H = ns.Hub
local W = H.W
local ROWS, LINE, TOP = 17, 22, -58

local function classColor(class)
  local c = RAID_CLASS_COLORS and RAID_CLASS_COLORS[class]
  return c and c.colorStr or "ffffffff"
end

local function profText(p, only)
  local parts = {}
  for _, pr in ipairs(p.profs) do
    if not only or pr.line == only then
      parts[#parts + 1] = profName(pr.line) .. " |cffffffff" .. pr.rank .. "|r/" .. pr.max
    end
  end
  return table.concat(parts, " · ")
end

-- Page: directory
local filterIdx, onlyAvail, pageNo = 0, false, 1
local refreshDir
local pDir, dirIndex = ns.HubTab("prof", T.tab_dir, function() refreshDir() end)

local filterBtn = CreateFrame("Button", nil, pDir, "UIPanelButtonTemplate")
filterBtn:SetSize(200, 22)
filterBtn:SetPoint("TOPLEFT", 4, -2)
filterBtn:SetScript("OnClick", function(_, button)
  local step = button == "RightButton" and -1 or 1
  filterIdx = (filterIdx + step) % (#CRAFTS + 1)
  pageNo = 1
  refreshDir()
end)
if filterBtn.RegisterForClicks then filterBtn:RegisterForClicks("LeftButtonUp", "RightButtonUp") end
local availBtn = CreateFrame("Button", nil, pDir, "UIPanelButtonTemplate")
availBtn:SetSize(140, 22)
availBtn:SetPoint("LEFT", filterBtn, "RIGHT", 8, 0)
availBtn:SetScript("OnClick", function() onlyAvail = not onlyAvail; pageNo = 1; refreshDir() end)
local dirCount = pDir:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
dirCount:SetPoint("TOPLEFT", 4, -32)
dirCount:SetWidth(W - 40)
dirCount:SetJustifyH("LEFT")

H.rows(pDir, ROWS, TOP, LINE)
local whisperBtns = {}
for i = 1, ROWS do
  local b = CreateFrame("Button", nil, pDir, "UIPanelButtonTemplate")
  b:SetSize(70, 20)
  b:SetPoint("TOPRIGHT", -4, TOP - (i - 1) * LINE + 3)
  b:SetText(T.whisper)
  b:SetFrameLevel((pDir:GetFrameLevel() or 1) + 5) -- above the row's tooltip area
  b:Hide()
  whisperBtns[i] = b
end

local function whisper(name)
  if ChatFrame_SendTell then
    ChatFrame_SendTell(name)
  elseif ChatFrame_OpenChat then
    ChatFrame_OpenChat("/w " .. name .. " ")
  end
end
ns.CraftWhisper = whisper

local prevBtn = CreateFrame("Button", nil, pDir, "UIPanelButtonTemplate")
prevBtn:SetSize(28, 20)
prevBtn:SetPoint("BOTTOMLEFT", 4, 4)
prevBtn:SetText("<")
prevBtn:SetScript("OnClick", function() pageNo = pageNo - 1; refreshDir() end)
local nextBtn = CreateFrame("Button", nil, pDir, "UIPanelButtonTemplate")
nextBtn:SetSize(28, 20)
nextBtn:SetPoint("LEFT", prevBtn, "RIGHT", 70, 0)
nextBtn:SetText(">")
nextBtn:SetScript("OnClick", function() pageNo = pageNo + 1; refreshDir() end)
local pageText = pDir:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
pageText:SetPoint("LEFT", prevBtn, "RIGHT", 6, 0)

-- Visible entries: me first (so I can check what I send), then available before unavailable,
-- then highest skill in the filtered profession.
function ns.CraftList()
  local only = filterIdx > 0 and CRAFTS[filterIdx] or nil
  local list = {}
  local function rank(p)
    local best = 0
    for _, pr in ipairs(p.profs) do if not only or pr.line == only then best = math.max(best, pr.rank) end end
    return best
  end
  local function keep(p)
    if onlyAvail and not p.avail then return false end
    if not only then return #p.profs > 0 end
    for _, pr in ipairs(p.profs) do if pr.line == only then return true end end
    return false
  end
  for name, p in pairs(peers) do
    if keep(p) then list[#list + 1] = { name = name, p = p, r = rank(p) } end
  end
  table.sort(list, function(a, b)
    if a.p.avail ~= b.p.avail then return a.p.avail end
    if a.r ~= b.r then return a.r > b.r end
    return a.name < b.name
  end)
  local mine = parseProfile((profileMessage()))
  if mine and keep(mine) then table.insert(list, 1, { name = myFull, p = mine, me = true }) end
  return list, only
end

refreshDir = function()
  filterBtn:SetText(filterIdx > 0 and profName(CRAFTS[filterIdx]) or T.all)
  availBtn:SetText(onlyAvail and T.only_avail or T.everyone)
  local total, avail = 0, 0
  for _, p in pairs(peers) do
    if #p.profs > 0 then total = total + 1; if p.avail then avail = avail + 1 end end
  end
  dirCount:SetText(string.format(T.count, total, avail))
  local list, only = ns.CraftList()
  local pages = math.max(1, math.ceil(#list / ROWS))
  pageNo = math.min(math.max(pageNo, 1), pages)
  pageText:SetText(string.format(T.page, pageNo, pages))
  if pageNo > 1 then prevBtn:Enable() else prevBtn:Disable() end
  if pageNo < pages then nextBtn:Enable() else nextBtn:Disable() end
  for i = 1, ROWS do
    local e = list[(pageNo - 1) * ROWS + i]
    local b = whisperBtns[i]
    if e then
      local dot = e.p.avail and "|cff40ff40●|r " or "|cff777777●|r "
      local label = "|c" .. classColor(e.p.class) .. short(e.name) .. "|r"
      if e.me then label = label .. " |cff888888(" .. T.you .. ")|r" end
      H.setRow(pDir, i, dot .. label .. " |cff888888" .. (e.p.level or "?") .. "|r  " .. profText(e.p, only))
      b:SetShown(not e.me)
      b:SetScript("OnClick", function() whisper(e.name) end)
    else
      H.setRow(pDir, i)
      b:Hide()
    end
  end
  if #list == 0 then H.setRow(pDir, 1, "|cff888888" .. T.none .. "|r") end
end

-- Page: my profile
local refreshMe
local pMe, meIndex = ns.HubTab("prof", T.tab_me, function() refreshMe() end)
local meIntro = pMe:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
meIntro:SetPoint("TOPLEFT", 4, -2)
meIntro:SetWidth(W - 40)
meIntro:SetJustifyH("LEFT")
meIntro:SetText(T.intro)
local toggle = CreateFrame("Button", nil, pMe, "UIPanelButtonTemplate")
toggle:SetSize(220, 30)
toggle:SetPoint("TOPLEFT", 4, -52)
toggle:SetScript("OnClick", function() ns.SetCraftAvailable(not db().avail) end)
local toggleHint = pMe:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
toggleHint:SetPoint("LEFT", toggle, "RIGHT", 10, 0)
toggleHint:SetWidth(W - 270)
toggleHint:SetJustifyH("LEFT")
H.rows(pMe, 14, -100, 18)

refreshMe = function()
  local on = db().avail
  toggle:SetText(on and ("|cff40ff40● " .. T.avail_on .. "|r") or ("|cffff5050● " .. T.avail_off .. "|r"))
  toggleHint:SetText(on and T.avail_hint_on or T.avail_hint_off)
  local i = 1
  H.setRow(pMe, i, "|cffffd100" .. T.my_profs .. "|r"); i = i + 1
  local profs = myProfessions()
  for _, p in ipairs(profs) do
    H.setRow(pMe, i, profName(p.line), "|cffffffff" .. p.rank .. "|r/" .. p.max); i = i + 1
  end
  if #profs == 0 then H.setRow(pMe, i, "|cff888888" .. T.no_prof .. "|r"); i = i + 1 end
  i = i + 1
  local seen = 0
  for _ in pairs(peers) do seen = seen + 1 end
  H.setRow(pMe, i, channelId > 0 and ("|cff40ff40" .. string.format(T.net_ok, seen) .. "|r")
    or (joinFailed and ("|cffff5050" .. T.net_fail .. "|r") or ("|cff888888" .. T.net_wait .. "|r"))); i = i + 1
  H.clearRows(pMe, i)
end

function ns.OnCraftChanged()
  ns.HubRefresh(dirIndex)
  ns.HubRefresh(meIndex)
end

function ns.ShowCrafters() ns.HubShow(dirIndex) end
