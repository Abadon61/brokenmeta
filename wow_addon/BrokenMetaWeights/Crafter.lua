-- BrokenMeta : Profession. A live directory of the crafters who run the addon: each client joins a
-- hidden chat channel and announces its professions, skill levels and a "available" flag through
-- addon messages (the addon has no internet). Searching lists who is online right now, and the
-- whisper button opens a /w to them.
--
-- Messages (prefix BMCraft):
--   Q1                              a newcomer asks everyone for their profile (answered by whisper)
--   P2;avail;level;class;faction;race;sex;line:rank:max,...;short message   a profile
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
  msg_label = "Message court, affiché sur ta carte d'artisan (60 caractères max) :", msg_save = "Enregistrer",
  msg_saved = "ton message d'artisan est enregistré.", preview = "Aperçu de ta carte",
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
  msg_label = "Short message shown on your crafter card (60 characters max):", msg_save = "Save",
  msg_saved = "your crafter message is saved.", preview = "Your card preview",
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

-- Set at PLAYER_LOGIN: while addons load on a fresh login, UnitName("player") is still "Unknown".
local realm, myName, myFull, charKey = "", "", "", ""
local function readNames()
  realm = (GetNormalizedRealmName and GetNormalizedRealmName()) or (GetRealmName() or ""):gsub("[%s%-]", "")
  myName = UnitName("player") or "?"
  myFull = myName .. "-" .. realm
  charKey = myName .. "-" .. (GetRealmName() or "")
end
readNames()

local function full(sender)
  if not sender or sender == "" then return nil end
  if not sender:find("-", 1, true) then return sender .. "-" .. realm end
  return sender
end

local function short(name)
  return (name:gsub("%-.*$", ""))
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

-- Short message: no chat escapes (|), no field separator (;), at most MSG_MAX characters (UTF-8).
local MSG_MAX = 60
local function cleanMessage(text)
  text = (text or ""):gsub("[|;%c]", ""):gsub("^%s+", ""):gsub("%s+$", "")
  local out, n = {}, 0
  for ch in text:gmatch("[\1-\127\194-\244][\128-\191]*") do
    n = n + 1
    if n > MSG_MAX then break end
    out[n] = ch
  end
  return table.concat(out)
end
ns.CleanCraftMessage = cleanMessage

local function profileMessage()
  local parts = {}
  for _, p in ipairs(myProfessions()) do parts[#parts + 1] = p.line .. ":" .. p.rank .. ":" .. p.max end
  local _, class = UnitClass("player")
  local _, race = UnitRace("player")
  local sex = UnitSex and UnitSex("player") or 2
  return "P2;" .. (db().avail and 1 or 0) .. ";" .. (UnitLevel("player") or 0) .. ";" .. (class or "")
    .. ";" .. (UnitFactionGroup("player") or "") .. ";" .. (race or "") .. ";" .. (sex or 2)
    .. ";" .. table.concat(parts, ",") .. ";" .. cleanMessage(db().msg), #parts
end

local function parseProfile(msg)
  local avail, level, class, faction, race, sex, profs, text =
    msg:match("^P2;([01]);(%d+);(%u*);(%a*);(%a*);(%d);([%d:,]*);(.*)$")
  if not avail then return nil end
  local list = {}
  for line, rank, max in profs:gmatch("(%d+):(%d+):(%d+)") do
    list[#list + 1] = { line = tonumber(line), rank = tonumber(rank), max = tonumber(max) }
  end
  return { avail = avail == "1", level = tonumber(level), class = class, faction = faction, race = race,
    sex = tonumber(sex), profs = list, msg = cleanMessage(text) }
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
    readNames()
    -- 0.8.0 could save this character as "Unknown-<realm>".
    if BrokenMetaWeightsDB and BrokenMetaWeightsDB.craft then
      local old = BrokenMetaWeightsDB.craft["Unknown-" .. (GetRealmName() or "")]
      if old and not BrokenMetaWeightsDB.craft[charKey] then BrokenMetaWeightsDB.craft[charKey] = old end
      BrokenMetaWeightsDB.craft["Unknown-" .. (GetRealmName() or "")] = nil
    end
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
    if channelId > 0 and n > 0 then send((msg:gsub("^P2;[01];", "P2;0;")), "CHANNEL", channelId) end
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
local W = ns.Hub.W
local C, HEX = ns.C, ns.HEX

local function classColor(class)
  local c = RAID_CLASS_COLORS and RAID_CLASS_COLORS[class]
  return c and c.colorStr or "ffffffff"
end

-- Race portrait: modern atlas, then the Classic race sheet, then the class icon.
local function setRaceIcon(tex, race, sex, class)
  local g = sex == 3 and "female" or "male"
  local r = race and race ~= "" and (race == "Scourge" and "undead" or race:lower()) or nil
  if r and tex.SetAtlas and C_Texture and C_Texture.GetAtlasInfo then
    for _, fmt in ipairs({ "raceicon128-%s-%s", "raceicon-%s-%s" }) do
      local name = fmt:format(r, g)
      if C_Texture.GetAtlasInfo(name) then tex:SetAtlas(name); return end
    end
  end
  if r and RACE_ICON_TCOORDS then
    local coords = RACE_ICON_TCOORDS[race:upper() .. "_" .. g:upper()] or RACE_ICON_TCOORDS[r:upper() .. "_" .. g:upper()]
    if coords then
      tex:SetTexture("Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races")
      tex:SetTexCoord(unpack(coords))
      return
    end
  end
  if class and CLASS_ICON_TCOORDS and CLASS_ICON_TCOORDS[class] then
    tex:SetTexture("Interface\\TargetingFrame\\UI-Classes-Circles")
    tex:SetTexCoord(unpack(CLASS_ICON_TCOORDS[class]))
    return
  end
  tex:SetTexture("Interface\\Icons\\INV_Misc_QuestionMark")
  tex:SetTexCoord(0, 1, 0, 1)
end

local function profText(p, only)
  local parts = {}
  for _, pr in ipairs(p.profs) do
    if not only or pr.line == only then
      parts[#parts + 1] = "|c" .. HEX.gold .. profName(pr.line) .. "|r |c" .. HEX.cream .. pr.rank .. "|r|c" .. HEX.faint .. "/" .. pr.max .. "|r"
    end
  end
  return table.concat(parts, "   ")
end

local function whisper(name)
  if ChatFrame_SendTell then
    ChatFrame_SendTell(name)
  elseif ChatFrame_OpenChat then
    ChatFrame_OpenChat("/w " .. name .. " ")
  end
end
ns.CraftWhisper = whisper

-- A crafter card: framed box, race portrait, status light, name / level, professions, message,
-- whisper button. Border: teal when available, gold for your own card.
local CARD_H = 58
local function makeCard(parent, width)
  local c = CreateFrame("Frame", nil, parent, ns.BACKDROP_TEMPLATE)
  c:SetSize(width, CARD_H)
  ns.Flat(c)
  c:EnableMouse(true)
  c:SetScript("OnEnter", function(self) if self.SetBackdropColor then self:SetBackdropColor(unpack(C.rowHover)) end end)
  c:SetScript("OnLeave", function(self) if self.SetBackdropColor then self:SetBackdropColor(unpack(C.row)) end end)
  c.icon = c:CreateTexture(nil, "ARTWORK")
  c.icon:SetSize(42, 42)
  c.icon:SetPoint("LEFT", 8, 0)
  c.light = c:CreateTexture(nil, "OVERLAY")
  c.light:SetSize(14, 14)
  c.light:SetPoint("BOTTOMRIGHT", c.icon, "BOTTOMRIGHT", 4, -4)
  c.name = c:CreateFontString(nil, "OVERLAY", "GameFontNormal")
  c.name:SetPoint("TOPLEFT", c.icon, "TOPRIGHT", 10, 0)
  c.profs = c:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
  c.profs:SetPoint("TOPLEFT", c.name, "BOTTOMLEFT", 0, -3)
  c.profs:SetWidth(width - 160)
  c.profs:SetJustifyH("LEFT")
  c.profs:SetWordWrap(false)
  c.msg = c:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
  c.msg:SetPoint("TOPLEFT", c.profs, "BOTTOMLEFT", 0, -3)
  c.msg:SetWidth(width - 160)
  c.msg:SetJustifyH("LEFT")
  c.msg:SetWordWrap(false)
  c.btn = CreateFrame("Button", nil, c, "UIPanelButtonTemplate")
  c.btn:SetSize(80, 22)
  c.btn:SetPoint("RIGHT", -10, 0)
  c.btn:SetText(T.whisper)
  function c:Set(e, only)
    local p = e.p
    setRaceIcon(self.icon, p.race, p.sex, p.class)
    self.light:SetTexture(p.avail and "Interface\\FriendsFrame\\StatusIcon-Online" or "Interface\\FriendsFrame\\StatusIcon-Offline")
    local label = "|c" .. classColor(p.class) .. short(e.name) .. "|r  |c" .. HEX.faint .. (p.level or "?") .. "|r"
    if e.me then label = label .. "  |c" .. HEX.gold .. "(" .. T.you .. ")|r" end
    self.name:SetText(label)
    self.profs:SetText(profText(p, only))
    self.msg:SetText(p.msg and p.msg ~= "" and ("|c" .. HEX.dim .. "« " .. p.msg .. " »|r") or "")
    ns.FlatBorder(self, e.me and C.gold or (p.avail and C.teal or C.border))
    self.btn:SetShown(not e.me)
    self.btn:SetScript("OnClick", function() whisper(e.name) end)
    self:Show()
  end
  return c
end

---------------------------------------------------------------------------------------------
-- Page: directory
---------------------------------------------------------------------------------------------
local CARDS, TOP, GAP = 6, -52, 64
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
local dirNone = pDir:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
dirNone:SetPoint("TOPLEFT", 4, TOP - 4)
dirNone:SetWidth(W - 40)
dirNone:SetJustifyH("LEFT")

local cards = {}
for i = 1, CARDS do
  cards[i] = makeCard(pDir, W - 32)
  cards[i]:SetPoint("TOPLEFT", 4, TOP - (i - 1) * GAP)
  cards[i]:Hide()
end

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

local function myEntry()
  local mine = parseProfile((profileMessage()))
  return mine and { name = myFull, p = mine, me = true }
end

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
  local mine = myEntry()
  if mine and keep(mine.p) then table.insert(list, 1, mine) end
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
  local pages = math.max(1, math.ceil(#list / CARDS))
  pageNo = math.min(math.max(pageNo, 1), pages)
  pageText:SetText(string.format(T.page, pageNo, pages))
  if pageNo > 1 then prevBtn:Enable() else prevBtn:Disable() end
  if pageNo < pages then nextBtn:Enable() else nextBtn:Disable() end
  for i = 1, CARDS do
    local e = list[(pageNo - 1) * CARDS + i]
    if e then cards[i]:Set(e, only) else cards[i]:Hide() end
  end
  dirNone:SetText(#list == 0 and ("|c" .. HEX.faint .. T.none .. "|r") or "")
end

---------------------------------------------------------------------------------------------
-- Page: my profile
---------------------------------------------------------------------------------------------
local refreshMe
local pMe, meIndex = ns.HubTab("prof", T.tab_me, function() refreshMe() end)
local meIntro = pMe:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
meIntro:SetPoint("TOPLEFT", 4, -2)
meIntro:SetWidth(W - 40)
meIntro:SetJustifyH("LEFT")
meIntro:SetText(T.intro)
local toggle = CreateFrame("Button", nil, pMe, "UIPanelButtonTemplate")
toggle:SetSize(220, 30)
toggle:SetPoint("TOPLEFT", 4, -48)
toggle:SetScript("OnClick", function() ns.SetCraftAvailable(not db().avail) end)
local toggleHint = pMe:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
toggleHint:SetPoint("LEFT", toggle, "RIGHT", 10, 0)
toggleHint:SetWidth(W - 270)
toggleHint:SetJustifyH("LEFT")

local msgLabel = pMe:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
msgLabel:SetPoint("TOPLEFT", 4, -92)
msgLabel:SetText(T.msg_label)
local msgBox = CreateFrame("EditBox", nil, pMe, "InputBoxTemplate")
msgBox:SetSize(W - 150, 22)
msgBox:SetPoint("TOPLEFT", 10, -108)
msgBox:SetAutoFocus(false)
msgBox:SetMaxLetters(MSG_MAX)
local msgSave = CreateFrame("Button", nil, pMe, "UIPanelButtonTemplate")
msgSave:SetSize(100, 22)
msgSave:SetPoint("LEFT", msgBox, "RIGHT", 8, 0)
msgSave:SetText(T.msg_save)

function ns.SetCraftMessage(text)
  db().msg = cleanMessage(text)
  ns.say(T.msg_saved)
  broadcastSoon()
  if ns.OnCraftChanged then ns.OnCraftChanged() end
end
msgSave:SetScript("OnClick", function() msgBox:ClearFocus(); ns.SetCraftMessage(msgBox:GetText()) end)
msgBox:SetScript("OnEnterPressed", function(self) self:ClearFocus(); ns.SetCraftMessage(self:GetText()) end)
msgBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)

local prevLabel = pMe:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
prevLabel:SetPoint("TOPLEFT", 4, -144)
prevLabel:SetText(T.preview)
local preview = makeCard(pMe, W - 32)
preview:SetPoint("TOPLEFT", 4, -160)

ns.Hub.rows(pMe, 10, -236, 18)

refreshMe = function()
  local on = db().avail
  toggle:SetText(on and ("|c" .. HEX.teal .. T.avail_on .. "|r") or ("|cffff5050" .. T.avail_off .. "|r"))
  toggleHint:SetText(on and T.avail_hint_on or T.avail_hint_off)
  if not msgBox:HasFocus() then msgBox:SetText(db().msg or "") end
  local mine = myEntry()
  if mine then preview:Set(mine) end
  local i = 1
  ns.Hub.setRow(pMe, i, "|c" .. HEX.gold .. T.my_profs .. "|r"); i = i + 1
  local profs = myProfessions()
  for _, p in ipairs(profs) do
    ns.Hub.setRow(pMe, i, profName(p.line), "|cffffffff" .. p.rank .. "|r/" .. p.max); i = i + 1
  end
  if #profs == 0 then ns.Hub.setRow(pMe, i, "|c" .. HEX.faint .. T.no_prof .. "|r"); i = i + 1 end
  i = i + 1
  local seen = 0
  for _ in pairs(peers) do seen = seen + 1 end
  ns.Hub.setRow(pMe, i, channelId > 0 and ("|c" .. HEX.teal .. string.format(T.net_ok, seen) .. "|r")
    or (joinFailed and ("|cffff5050" .. T.net_fail .. "|r") or ("|c" .. HEX.faint .. T.net_wait .. "|r"))); i = i + 1
  ns.Hub.clearRows(pMe, i)
end

function ns.OnCraftChanged()
  ns.HubRefresh(dirIndex)
  ns.HubRefresh(meIndex)
end

function ns.ShowCrafters() ns.HubShow(dirIndex) end
