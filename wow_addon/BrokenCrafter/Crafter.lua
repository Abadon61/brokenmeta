-- Broken Meta : Profession. A directory of the crafters who run the addon: crafters announce their
-- professions, skill levels and availability with one click, every player of the realm with the
-- addon sees them (see "How the directory travels" below), and the whisper button opens a /w.
--
-- Messages (prefix BMCraft):
--   Q1                              a newcomer asks everyone for their profile (answered by whisper)
--   P3;avail;level;class;faction;race;sex;favs;line:rank:max,...;short message   a profile
--      (favs: how many players have this crafter in their favourites; 0.12 and older sent P2, no favs)
--   F1 / F0                          I added you to / removed you from my favourites (whisper)
--   D1;faction;itemID[;age] / D0 / DQ   craft requests (see Requests.lua)
local ADDON = ...
local ns = BrokenMetaNS -- Broken Meta : HUB's namespace, shared by the suite
ns.Modules.BrokenCrafter = true
local IS_FR = ns.IS_FR
local LOCALE = ns.LOCALE

local T = ns.Localize("craft", {
  tab_dir = "Artisans", tab_me = "Mon profil", sec_find = "Trouver", sec_craft = "Artisan",
  all = "Tous les métiers", only_avail = "Dispo seulement", everyone = "Tout le monde", favorites = "Favoris",
  fav_add = "Ajouter aux favoris", fav_del = "Retirer des favoris", not_announced = "Pas annoncé en ce moment · vu il y a %s",
  minutes = "%d min", hours = "%d h", days = "%d j",
  count = "%d artisan(s) connecté(s), %d disponible(s)",
  none = "Aucun artisan annoncé pour l'instant. Clique sur Actualiser : les artisans disponibles qui ont l'addon, sur ton royaume et ta faction, apparaîtront ici.",
  search = "Chercher un objet…", rec_count = "%d recettes enregistrées", rec_none = "recettes : ouvre ta fenêtre de métier",
  site_opt = "Apparaître sur brokenmeta.gg (annuaire public des artisans)", site_copy = "Copier ma fiche pour le site",
  site_title = "Ma fiche d'artisan pour brokenmeta.gg",
  site_hint = "Ctrl+C, puis colle-la sur brokenmeta.gg/wow-forever/artisans/ (bouton « Publier ma fiche »). Elle contient : nom du personnage, royaume, faction, classe, race, niveau, métiers, recettes, message et nombre de favoris.",
  refresh = "Actualiser", renew = "Renouveler l'annonce", renewed = "ton annonce d'artisan a été renouvelée.",
  announced = "Annoncé il y a %d min : visible par tous pendant 1 h. Clique sur Renouveler pour prolonger.",
  renew_hint = "ton annonce d'artisan expire dans 5 min : ouvre Broken Meta : Profession > Mon profil et clique sur Renouveler pour rester visible.",
  whisper = "MP", you = "toi", page = "Page %d/%d",
  avail_on = "Disponible", avail_off = "Indisponible",
  avail_hint_on = "Tu apparais en vert dans l'annuaire : les joueurs peuvent te chuchoter pour un craft. Clique pour te rendre indisponible.",
  avail_hint_off = "Tu apparais en gris dans l'annuaire. Clique pour te rendre disponible et recevoir des demandes de craft.",
  my_profs = "Tes métiers", no_prof = "Tu n'as aucun métier d'artisanat : tu peux quand même chercher des artisans.",
  net_ok = "Connecté au réseau Broken Meta (%d joueur(s) avec l'addon vus).",
  net_wait = "Connexion au réseau Broken Meta en cours…",
  diag = "Diagnostic : canal %d · envoyés %d · reçus d'autres joueurs %d · tes échos %d · dernier : %s · envoi : %s",
  net_fail = "Impossible de rejoindre le canal Broken Meta : trop de canaux ouverts ? Quitte-en un puis tape /reload.",
  intro = "Broken Meta : Profession montre les artisans qui ont l'addon. Inscris-toi comme artisan pour recevoir des demandes, ou cherche un artisan dans l'onglet Artisans et clique sur MP pour lui écrire.",
  msg_label = "Message court, affiché sur ta carte d'artisan (60 caractères max) :", msg_save = "Enregistrer",
  msg_saved = "ton message d'artisan est enregistré.", preview = "Aperçu de ta carte",
  avail_now = "tu es maintenant disponible dans l'annuaire des artisans.",
  avail_gone = "tu n'es plus disponible dans l'annuaire des artisans.",
  reg_btn = "S'inscrire comme artisan", reg_off = "Se désinscrire",
  reg_hint = "Une seule fois : tu seras annoncé à chaque connexion, renouvelé automatiquement quand tu cliques en jeu, et listé même hors ligne.",
  reg_hint_on = "Inscrit : tu es annoncé automatiquement à chaque connexion et listé même hors ligne. Clique pour passer indisponible.",
  reg_hint_off = "Inscrit mais indisponible pour cette session. Clique pour redevenir disponible.",
  reg_now = "tu es inscrit comme artisan : annonce automatique à chaque connexion.",
  reg_gone = "tu n'es plus inscrit comme artisan.",
  gate_title = "Inscris-toi pour accéder à l'annuaire",
  gate_text = "L'annuaire des artisans de ton royaume est réservé aux artisans inscrits : c'est ce qui garantit qu'il y a toujours quelqu'un à qui écrire.",
  gate_1 = "Une seule inscription : valable à chaque connexion",
  gate_2 = "Les acheteurs te trouvent, même quand tu es hors ligne",
  gate_3 = "Tu peux te désinscrire quand tu veux (onglet Artisan > Mon profil)",
  banner_btn = "S'inscrire comme artisan",
  mode_all = "Tous", mode_avail = "En ligne", mode_fav = "Favoris", whisper_full = "Chuchoter", lvl_short = "niv. %d",
  pick_crafter = "Sélectionne un artisan dans la liste pour voir sa fiche.",
  empty_dir = "Aucun artisan annoncé", empty_dir_btn = "Publier une demande",
  ob_title = "Ta fiche : %d/3", ob_reg = "Inscrit", ob_rec = "Recettes enregistrées", ob_msg = "Message ajouté",
}, {
  tab_dir = "Crafters", tab_me = "My profile", sec_find = "Find", sec_craft = "Crafter",
  all = "All professions", only_avail = "Available only", everyone = "Everyone", favorites = "Favourites",
  fav_add = "Add to favourites", fav_del = "Remove from favourites", not_announced = "Not announced right now · seen %s ago",
  minutes = "%d min", hours = "%dh", days = "%dd",
  count = "%d crafter(s) online, %d available",
  none = "No crafter announced yet. Click Refresh: available crafters who run the addon, on your realm and faction, will show up here.",
  search = "Search an item…", rec_count = "%d recipes recorded", rec_none = "recipes: open your profession window",
  site_opt = "Show me on brokenmeta.gg (public crafters directory)", site_copy = "Copy my card for the site",
  site_title = "My crafter card for brokenmeta.gg",
  site_hint = "Ctrl+C, then paste it on brokenmeta.gg/en/wow-forever/artisans/ (\"Publish my card\" button). It holds: character name, realm, faction, class, race, level, professions, recipes, message and favourite count.",
  refresh = "Refresh", renew = "Renew the announce", renewed = "your crafter announce is renewed.",
  announced = "Announced %d min ago: visible to everyone for 1 hour. Click Renew to extend it.",
  renew_hint = "your crafter announce expires in 5 min: open Broken Meta : Professions > My profile and click Renew to stay visible.",
  whisper = "Whisper", you = "you", page = "Page %d/%d",
  avail_on = "Available", avail_off = "Unavailable",
  avail_hint_on = "You show up in green in the directory: players can whisper you for a craft. Click to become unavailable.",
  avail_hint_off = "You show up in grey in the directory. Click to become available and get craft requests.",
  my_profs = "Your professions", no_prof = "You have no crafting profession: you can still search for crafters.",
  net_ok = "Connected to the Broken Meta network (%d player(s) with the addon seen).",
  net_wait = "Connecting to the Broken Meta network…",
  diag = "Diagnostics: channel %d · sent %d · received from others %d · own echoes %d · last: %s · send: %s",
  net_fail = "Could not join the Broken Meta channel: too many channels open? Leave one, then type /reload.",
  intro = "Broken Meta : Professions shows the crafters who run the addon. Register as a crafter to get requests, or look for a crafter in the Crafters tab and click Whisper to message them.",
  msg_label = "Short message shown on your crafter card (60 characters max):", msg_save = "Save",
  msg_saved = "your crafter message is saved.", preview = "Your card preview",
  avail_now = "you are now available in the crafters directory.",
  avail_gone = "you are no longer available in the crafters directory.",
  reg_btn = "Register as a crafter", reg_off = "Unregister",
  reg_hint = "Once only: you are announced at every login, renewed automatically when you click in game, and listed even when offline.",
  reg_hint_on = "Registered: you are announced automatically at every login and listed even when offline. Click to go unavailable.",
  reg_hint_off = "Registered but unavailable this session. Click to become available again.",
  reg_now = "you are registered as a crafter: announced automatically at every login.",
  reg_gone = "you are no longer registered as a crafter.",
  gate_title = "Register to open the directory",
  gate_text = "The crafters directory of your realm is for registered crafters: that is what makes sure there is always someone to whisper.",
  gate_1 = "Register once: valid at every login",
  gate_2 = "Buyers find you, even when you are offline",
  gate_3 = "Unregister whenever you want (Crafter tab > My profile)",
  banner_btn = "Register as a crafter",
  mode_all = "All", mode_avail = "Online", mode_fav = "Favourites", whisper_full = "Whisper", lvl_short = "lvl %d",
  pick_crafter = "Select a crafter in the list to see their card.",
  empty_dir = "No crafter announced", empty_dir_btn = "Post a request",
  ob_title = "Your card: %d/3", ob_reg = "Registered", ob_rec = "Recipes recorded", ob_msg = "Message added",
})

local PREFIX, CHANNEL = "BMCraft", "BrokenMetaCraft"
local EXPIRE = 3720 -- seconds: a crafter's announce is shown for 1 hour (+2 min of margin)

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
ns.CraftProfName = profName

-- "3 min", "2 h", "4 j" since a time() value.
function ns.Ago(t)
  local sec = math.max(0, time() - (t or 0))
  if sec >= 86400 then return string.format(T.days, math.floor(sec / 86400)) end
  if sec >= 3600 then return string.format(T.hours, math.floor(sec / 3600)) end
  return string.format(T.minutes, math.floor(sec / 60))
end

-- Skill line of a profession from its name in any of the four languages (Classic windows give names).
function ns.CraftLineFromName(name)
  for line, n in pairs(NAMES) do
    for _, loc in ipairs(n) do if loc == name then return line end end
  end
  return nil
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
  if sender:find("-", 1, true) then return sender end
  -- "Name Realm" (seen on Forever) -> "Name-Realm", the form /w expects.
  local name, rest = sender:match("^(%S+)%s+(.+)$")
  if name then return name .. "-" .. rest:gsub("%s", "") end
  return sender .. "-" .. realm
end

-- Character name without the realm. Seen in game: Forever gives the sender as "Name Realm" (a
-- space, not the usual dash); a character name has neither, so both are cut.
local function short(name)
  return (name:gsub("[%-%s].*$", ""))
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
  local fans = 0
  for _ in pairs(db().favBy or {}) do fans = fans + 1 end
  return "P3;" .. (db().avail and 1 or 0) .. ";" .. (UnitLevel("player") or 0) .. ";" .. (class or "")
    .. ";" .. (UnitFactionGroup("player") or "") .. ";" .. (race or "") .. ";" .. (sex or 2) .. ";" .. fans
    .. ";" .. table.concat(parts, ",") .. ";" .. cleanMessage(db().msg), #parts
end

local function parseProfile(msg)
  local avail, level, class, faction, race, sex, fans, profs, text =
    msg:match("^P3;([01]);(%d+);(%u*);(%a*);(%a*);(%d);(%d+);([%d:,]*);(.*)$")
  if not avail then
    avail, level, class, faction, race, sex, profs, text = msg:match("^P2;([01]);(%d+);(%u*);(%a*);(%a*);(%d);([%d:,]*);(.*)$")
    fans = "0"
  end
  if not avail then return nil end
  local list = {}
  for line, rank, max in profs:gmatch("(%d+):(%d+):(%d+)") do
    list[#list + 1] = { line = tonumber(line), rank = tonumber(rank), max = tonumber(max) }
  end
  return { avail = avail == "1", level = tonumber(level), class = class, faction = faction, race = race,
    sex = tonumber(sex), favs = tonumber(fans) or 0, profs = list, msg = cleanMessage(text) }
end

---------------------------------------------------------------------------------------------
-- Network
---------------------------------------------------------------------------------------------
-- How the directory travels. Classic (and so Forever) blocks ADDON messages on custom chat channels
-- (patch 1.13.3: in game, the hidden channel only echoed our own). What stays allowed: ordinary
-- chat lines in a custom channel, sent from a real click, which every addon can read. So:
--   * the crafter's clicks (Available / Unavailable / Renew / Save message) post one chat line
--     "BM1 P2;..." in the hidden channel: every player of the realm with the addon, in any zone,
--     reads it and updates the directory. The channel is kept out of the chat windows.
--   * opening the Crafters tab (a click) posts "BM1 Q1": crafters who are available answer with
--     their profile through an invisible addon whisper, so late arrivals see them too.
--   * guild and group also get the profile through invisible addon messages.
-- No click, no chat line: an announce is valid for ANNOUNCE_TTL, then the addon asks the crafter
-- to renew it with one click.
local peers = {} -- ["Name-Realm"] = profile + seen
local channelId = 0
local joinFailed = false
local TAG = "BM1 "
local ANNOUNCE_TTL = 3600
local lastRequest = -60
local pruneKnown, hookClicks

-- Counters for the diagnostics line of My profile.
local stats = { sent = 0, recv = 0, echo = 0, last = nil, result = nil }
ns.CraftStats = stats

local function send(msg, kind, target)
  if not (C_ChatInfo and C_ChatInfo.SendAddonMessage) then return end
  local ok, res = pcall(C_ChatInfo.SendAddonMessage, PREFIX, msg, kind, target)
  stats.sent = stats.sent + 1
  stats.result = kind .. " " .. (ok and tostring(res) or ("error " .. tostring(res)))
end

ns.CraftSend = send

local function sendOthers(msg)
  if IsInGuild and IsInGuild() then send(msg, "GUILD") end
  if IsInRaid and IsInRaid() then send(msg, "RAID")
  elseif IsInGroup and IsInGroup() then send(msg, "PARTY") end
end

-- A chat line in the hidden channel. Only call from a click: the game refuses channel messages
-- that no hardware event started.
local function chat(line)
  if channelId == 0 or not SendChatMessage then return false end
  SendChatMessage(TAG .. line, "CHANNEL", nil, channelId)
  stats.sent = stats.sent + 1
  stats.result = "CHANNEL chat"
  return true
end

local function announce()
  local msg, n = profileMessage()
  if n == 0 then return end
  chat(msg)
  sendOthers(msg)
  db().announced = time()
  db().reminded = nil
end
ns.CraftAnnounce = announce
ns.CraftChat = chat -- craft requests (Requests.lua) post the same way, from a click
ns.CraftShortName = short

-- Ask who is available (from a click: opening the Crafters tab, the Refresh button).
function ns.CraftRequest(force)
  if not force and GetTime() - lastRequest < 60 then return end
  lastRequest = GetTime()
  chat("Q1")
  sendOthers("Q1")
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
  elseif attempt < 5 then
    C_Timer.After(3, function() join(attempt + 1) end)
  else
    joinFailed = true
  end
  if ns.OnCraftChanged then ns.OnCraftChanged() end
end

local function isOurChannel(name, base)
  return base == CHANNEL or (type(name) == "string" and name:find(CHANNEL, 1, true) ~= nil)
end

-- The channel's notices and lines stay out of the chat windows, wherever it got added.
if ChatFrame_AddMessageEventFilter then
  ChatFrame_AddMessageEventFilter("CHAT_MSG_CHANNEL_NOTICE", function(_, _, _, _, _, name, _, _, _, _, base)
    return isOurChannel(name, base)
  end)
  ChatFrame_AddMessageEventFilter("CHAT_MSG_CHANNEL", function(_, _, _, _, _, name, _, _, _, _, base)
    return isOurChannel(name, base)
  end)
end

function ns.SetCraftAvailable(on, quiet)
  db().avail = on and true or false
  if not quiet then ns.Toast(on and T.avail_now or T.avail_gone) end
  announce() -- from the button's click: also tells everyone when we stop being available
  if ns.OnCraftChanged then ns.OnCraftChanged() end
end

function ns.CraftPeers() return peers end

-- Registered crafter: kept across sessions, available at login, announced on the first click.
function ns.RegisterCrafter(on)
  db().registered = on and true or nil
  ns.Toast(on and T.reg_now or T.reg_gone)
  ns.SetCraftAvailable(on, true)
end

-- The channel announce needs a click. A registered, available crafter's first click in the game
-- world (or on the minimap button) posts it, and a click renews it before it expires: nobody has
-- to open the addon to stay visible.
local lastTry = -60
local function autoAnnounce()
  local d = db()
  if not (d.registered and d.avail) or channelId == 0 then return end
  if d.announced and time() - d.announced < ANNOUNCE_TTL - 600 then return end
  if GetTime() - lastTry < 30 then return end
  lastTry = GetTime()
  announce()
end
ns.CraftAutoAnnounce = autoAnnounce

local clicksHooked = false
hookClicks = function()
  if clicksHooked then return end
  clicksHooked = true
  if type(WorldFrame) == "table" and WorldFrame.HookScript then WorldFrame:HookScript("OnMouseDown", autoAnnounce) end
  local mini = _G.BrokenMetaMinimapButton
  if mini and mini.HookScript then mini:HookScript("OnClick", autoAnnounce) end
end

-- Crafters seen announcing, per realm, kept across sessions so the directory is never empty:
-- { ["Name-Realm"] = { p = profile, t = time() } }, dropped after KNOWN_DAYS without a sign.
local KNOWN_DAYS = 14
local function known()
  BrokenMetaWeightsDB = BrokenMetaWeightsDB or {}
  BrokenMetaWeightsDB.craftKnown = BrokenMetaWeightsDB.craftKnown or {}
  local k = BrokenMetaWeightsDB.craftKnown[realm]
  if not k then k = {}; BrokenMetaWeightsDB.craftKnown[realm] = k end
  return k
end
ns.CraftKnown = known

pruneKnown = function()
  local limit = time() - KNOWN_DAYS * 86400
  for name, k in pairs(known()) do if (k.t or 0) < limit then known()[name] = nil end end
end

-- Favourite crafters, per realm, kept across sessions with their last known profile so they stay
-- listed (greyed) while they are not announced: { ["Name-Realm"] = { p = profile, t = time() } }.
local function favs()
  BrokenMetaWeightsDB = BrokenMetaWeightsDB or {}
  BrokenMetaWeightsDB.craftFavs = BrokenMetaWeightsDB.craftFavs or {}
  local f = BrokenMetaWeightsDB.craftFavs[realm]
  if not f then f = {}; BrokenMetaWeightsDB.craftFavs[realm] = f end
  return f
end
ns.CraftFavs = favs

local function snapshot(p)
  return { level = p.level, class = p.class, faction = p.faction, race = p.race, sex = p.sex, profs = p.profs, msg = p.msg,
    favs = p.favs }
end

-- Removals still to tell (the crafter was not online): { ["Name-Realm"] = true }, per realm.
local function unfavs()
  BrokenMetaWeightsDB.craftUnfavs = BrokenMetaWeightsDB.craftUnfavs or {}
  local u = BrokenMetaWeightsDB.craftUnfavs[realm]
  if not u then u = {}; BrokenMetaWeightsDB.craftUnfavs[realm] = u end
  return u
end

-- The crafter counts who favours them (F1 / F0 by invisible whisper); sent when they are online.
local function tellFav(name)
  local f = favs()[name]
  if f and not f.sent then send("F1", "WHISPER", name); f.sent = true end
  if not f and unfavs()[name] then send("F0", "WHISPER", name); unfavs()[name] = nil end
end

function ns.ToggleCraftFav(name, p)
  if favs()[name] then
    favs()[name] = nil
    if not favs()[name] then unfavs()[name] = true end
  else
    favs()[name] = { p = snapshot(p), t = time() }
    unfavs()[name] = nil
  end
  if peers[name] then tellFav(name) end
  if ns.OnCraftChanged then ns.OnCraftChanged() end
end

-- A message from another player (chat line in the channel, or addon message).
local function receive(body, sender, kind)
  local who = full(sender)
  if not who then return end
  if who == myFull or short(who) == myName then stats.echo = stats.echo + 1; return end
  stats.recv = stats.recv + 1
  stats.last = short(who) .. " (" .. tostring(kind) .. ")"
  if body == "DQ" or body == "D0" or body:sub(1, 3) == "D1;" then -- craft requests (Requests.lua)
    if ns.OnRequestMessage then ns.OnRequestMessage(body, who) end
    return
  end
  if body:sub(1, 2) == "R1" then -- recipes (Recipes.lua)
    if ns.OnRecipeMessage then ns.OnRecipeMessage(body, who) end
    return
  end
  if body == "F1" or body == "F0" then
    db().favBy = db().favBy or {}
    db().favBy[who] = body == "F1" or nil
    if ns.OnCraftChanged then ns.OnCraftChanged() end
    return
  end
  if body == "Q1" then
    -- Available crafters answer, invisibly, a little later so answers don't all arrive at once.
    local reply, n = profileMessage()
    if n > 0 and db().avail then C_Timer.After(1 + math.random() * 4, function() send(reply, "WHISPER", who) end) end
    return
  end
  local p = parseProfile(body)
  if p and (p.faction == "" or p.faction == (UnitFactionGroup("player") or p.faction)) then
    p.seen = GetTime()
    peers[who] = p
    if #p.profs > 0 then
      -- An available crafter is remembered; one who says they are not is no longer listed offline.
      known()[who] = p.avail and { p = snapshot(p), t = time() } or nil
    end
    if favs()[who] then favs()[who].p = snapshot(p); favs()[who].t = time() end
    tellFav(who)
    if ns.OnCraftChanged then ns.OnCraftChanged() end
  end
end
ns.CraftReceive = receive

local f = CreateFrame("Frame")
for _, ev in ipairs({ "PLAYER_LOGIN", "CHAT_MSG_ADDON", "CHAT_MSG_CHANNEL", "CHAT_MSG_SYSTEM", "SKILL_LINES_CHANGED",
    "GROUP_ROSTER_UPDATE" }) do
  pcall(f.RegisterEvent, f, ev)
end
f:SetScript("OnEvent", function(_, event, a1, a2, a3, a4, a5, a6, a7, a8, a9)
  if event == "PLAYER_LOGIN" then
    if C_ChatInfo and C_ChatInfo.RegisterAddonMessagePrefix then pcall(C_ChatInfo.RegisterAddonMessagePrefix, PREFIX) end
    readNames()
    -- 0.8.0 could save this character as "Unknown-<realm>".
    if BrokenMetaWeightsDB and BrokenMetaWeightsDB.craft then
      local old = BrokenMetaWeightsDB.craft["Unknown-" .. (GetRealmName() or "")]
      if old and not BrokenMetaWeightsDB.craft[charKey] then BrokenMetaWeightsDB.craft[charKey] = old end
      BrokenMetaWeightsDB.craft["Unknown-" .. (GetRealmName() or "")] = nil
    end
    -- Nobody has our announce any more, but a registered crafter is available again right away
    -- (answers Q1 invisibly); the channel announce follows on the first click (see autoAnnounce).
    db().announced = nil
    db().avail = db().registered == true
    pruneKnown()
    hookClicks()
    C_Timer.After(6, function() join(1) end)
  elseif event == "CHAT_MSG_CHANNEL" then
    -- text, author, language, channel name, target, flags, zone id, channel number, base name
    if isOurChannel(a4, a9) and type(a1) == "string" and a1:sub(1, #TAG) == TAG then receive(a1:sub(#TAG + 1), a2, "CHANNEL") end
  elseif event == "CHAT_MSG_ADDON" then
    if a1 == PREFIX and type(a2) == "string" then receive(a2, a4, a3) end
  elseif event == "CHAT_MSG_SYSTEM" then
    -- "No player named X is currently playing" (after a whisper to them): X logged off, drop them.
    if type(a1) ~= "string" or not ERR_CHAT_PLAYER_NOT_FOUND_S then return end
    local pattern = "^" .. ERR_CHAT_PLAYER_NOT_FOUND_S:gsub("([%^%$%(%)%.%[%]%*%+%-%?])", "%%%1"):gsub("%%s", "(.+)") .. "$"
    local gone = a1:match(pattern)
    if gone then
      for name in pairs(peers) do
        if name == gone or name == full(gone) or short(name) == gone then peers[name] = nil end
      end
      if ns.OnCraftChanged then ns.OnCraftChanged() end
    end
  elseif event == "GROUP_ROSTER_UPDATE" then
    local m, n = profileMessage()
    if IsInGroup and IsInGroup() and n > 0 then
      if IsInRaid and IsInRaid() then send(m, "RAID") else send(m, "PARTY") end
    end
  elseif event == "SKILL_LINES_CHANGED" then
    local m, n = profileMessage()
    if n > 0 then sendOthers(m) end
  end
end)

-- Expiry, and the reminder to renew an announce that others are about to drop.
local elapsed = 0
f:SetScript("OnUpdate", function(_, dt)
  elapsed = elapsed + dt
  if elapsed < 10 then return end
  elapsed = 0
  local now = GetTime()
  local changed = false
  for name, p in pairs(peers) do
    if now - p.seen > EXPIRE then peers[name] = nil; changed = true end
  end
  if changed and ns.OnCraftChanged then ns.OnCraftChanged() end
  local d = db()
  if d.avail and not d.registered and d.announced and time() - d.announced > ANNOUNCE_TTL - 300 and not d.reminded
      and (not ns.Option or ns.Option("announce_reminder")) then
    d.reminded = true
    ns.say(T.renew_hint)
  end
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

-- Race portrait, first source this client has: the achievement portraits (square, fit the card's
-- frame), the modern race atlases, the Classic race sheet, then the class icon. The source used is
-- kept in ns.RaceIconSource for /bmw probe.
local ACH_RACE = { Scourge = "Undead", NightElf = "Nightelf", BloodElf = "Bloodelf" }
local function fileExists(path)
  if not GetFileIDFromPath then return nil end
  return GetFileIDFromPath(path) ~= nil
end
local function setRaceIcon(tex, race, sex, class)
  local male = sex ~= 3
  local g = male and "male" or "female"
  local r = race and race ~= "" and race or nil
  tex:SetTexCoord(0, 1, 0, 1)
  if r then
    local ach = "Interface\\Icons\\Achievement_Character_" .. (ACH_RACE[r] or r) .. "_" .. (male and "Male" or "Female")
    if fileExists(ach) then
      tex:SetTexture(ach)
      tex:SetTexCoord(0.08, 0.92, 0.08, 0.92)
      ns.RaceIconSource = "achievement"
      return
    end
    local low = r == "Scourge" and "undead" or r:lower()
    if tex.SetAtlas and C_Texture and C_Texture.GetAtlasInfo then
      for _, fmt in ipairs({ "raceicon128-%s-%s", "raceicon-%s-%s" }) do
        local name = fmt:format(low, g)
        if C_Texture.GetAtlasInfo(name) then tex:SetAtlas(name); ns.RaceIconSource = "atlas " .. name; return end
      end
    end
    local coords = RACE_ICON_TCOORDS and (RACE_ICON_TCOORDS[r:upper() .. "_" .. g:upper()] or RACE_ICON_TCOORDS[low:upper() .. "_" .. g:upper()])
    if coords then
      tex:SetTexture("Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races")
      tex:SetTexCoord(unpack(coords))
      ns.RaceIconSource = "race sheet"
      return
    end
  end
  if class and CLASS_ICON_TCOORDS and CLASS_ICON_TCOORDS[class] then
    tex:SetTexture("Interface\\TargetingFrame\\UI-Classes-Circles")
    tex:SetTexCoord(unpack(CLASS_ICON_TCOORDS[class]))
    ns.RaceIconSource = "class icon (no race art found)"
    return
  end
  tex:SetTexture("Interface\\Icons\\INV_Misc_QuestionMark")
  ns.RaceIconSource = "none"
end

local function profText(p, only)
  local parts = {}
  for _, pr in ipairs(p.profs) do
    if not only or pr.line == only then
      parts[#parts + 1] = ns.ProfIcon(pr.line, 14) .. "|c" .. HEX.gold .. profName(pr.line) .. "|r |c" .. HEX.cream .. pr.rank .. "|r|c" .. HEX.faint .. "/" .. pr.max .. "|r"
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
  -- Portrait in its own frame (1-pixel border, class colour on hover-free cards).
  c.frame = CreateFrame("Frame", nil, c, ns.BACKDROP_TEMPLATE)
  c.frame:SetSize(44, 44)
  c.frame:SetPoint("LEFT", 7, 0)
  ns.Flat(c.frame, ns.C.bg, ns.C.borderBright)
  c.icon = c.frame:CreateTexture(nil, "ARTWORK")
  c.icon:SetPoint("TOPLEFT", 1, -1)
  c.icon:SetPoint("BOTTOMRIGHT", -1, 1)
  c.light = c.frame:CreateTexture(nil, "OVERLAY") -- on the portrait frame, else drawn under it
  c.light:SetSize(14, 14)
  c.light:SetPoint("BOTTOMRIGHT", c.frame, "BOTTOMRIGHT", 5, -5)
  c.name = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
  c.name:SetPoint("TOPLEFT", c.frame, "TOPRIGHT", 10, 1)
  c.profs = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  c.profs:SetPoint("TOPLEFT", c.name, "BOTTOMLEFT", 0, -3)
  c.profs:SetWidth(width - 160)
  c.profs:SetJustifyH("LEFT")
  c.profs:SetWordWrap(false)
  c.msg = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  c.msg:SetPoint("TOPLEFT", c.profs, "BOTTOMLEFT", 0, -3)
  c.msg:SetWidth(width - 160)
  c.msg:SetJustifyH("LEFT")
  c.msg:SetWordWrap(false)
  -- Skill bar along the bottom edge: the card's main profession (rank / max).
  c.barBg = c:CreateTexture(nil, "ARTWORK")
  c.barBg:SetColorTexture(unpack(C.border))
  c.barBg:SetHeight(3)
  c.barBg:SetPoint("BOTTOMLEFT", 1, 1)
  c.barBg:SetPoint("BOTTOMRIGHT", -1, 1)
  c.barFill = c:CreateTexture(nil, "OVERLAY")
  c.barFill:SetHeight(3)
  c.barFill:SetPoint("BOTTOMLEFT", 1, 1)
  c.btn = ns.Button(c, nil, "primary")
  c.btn:SetSize(80, 22)
  c.btn:SetPoint("RIGHT", -10, 0)
  c.btn:SetText(T.whisper)
  -- Favourite star (the raid-marker star: no star glyph in the fonts), grey when not a favourite.
  c.star = CreateFrame("Button", nil, c)
  c.star:SetSize(16, 16)
  c.star:SetPoint("LEFT", c.name, "RIGHT", 6, 0)
  c.star.tex = c.star:CreateTexture(nil, "ARTWORK")
  c.star.tex:SetAllPoints()
  c.star.tex:SetTexture("Interface\\TargetingFrame\\UI-RaidTargetingIcon_1")
  c.star:SetScript("OnEnter", function(self)
    GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
    GameTooltip:SetText(self.on and T.fav_del or T.fav_add)
    GameTooltip:Show()
  end)
  c.star:SetScript("OnLeave", function() GameTooltip:Hide() end)
  c.rec = ns.Button(c)
  c.rec:SetSize(80, 22)
  c.rec:SetPoint("RIGHT", c.btn, "LEFT", -6, 0)
  c.rec:SetText(ns.RecipeTexts and ns.RecipeTexts.button or "Recettes")
  function c:Set(e, only)
    local p = e.p
    setRaceIcon(self.icon, p.race, p.sex, p.class)
    self.light:SetTexture(p.avail and "Interface\\FriendsFrame\\StatusIcon-Online" or "Interface\\FriendsFrame\\StatusIcon-Offline")
    local label = "|c" .. classColor(p.class) .. short(e.name) .. "|r  |c" .. HEX.faint .. (p.level or "?") .. "|r"
    if (p.favs or 0) > 0 then
      label = label .. "  |TInterface\\TargetingFrame\\UI-RaidTargetingIcon_1:12:12:0:0|t|c" .. HEX.gold .. p.favs .. "|r"
    end
    if e.me then label = label .. "  |c" .. HEX.gold .. "(" .. T.you .. ")|r" end
    self.name:SetText(label)
    self.profs:SetText(profText(p, only))
    local top
    for _, pr in ipairs(p.profs) do
      if (not only or pr.line == only) and (not top or pr.rank > top.rank) then top = pr end
    end
    if top and top.max > 0 then
      self.barFill:SetWidth(math.max(1, math.floor((width - 2) * math.min(1, top.rank / top.max))))
      self.barFill:SetColorTexture(unpack(p.avail and C.teal or C.faint))
      self.barBg:Show(); self.barFill:Show()
    else
      self.barBg:Hide(); self.barFill:Hide()
    end
    local fav = not e.me and favs()[e.name] ~= nil
    self.star:SetShown(not e.me)
    self.star.on = fav
    self.star.tex:SetDesaturated(not fav)
    self.star.tex:SetAlpha(fav and 1 or 0.35)
    self.star:SetScript("OnClick", function() ns.ToggleCraftFav(e.name, p) end)
    if e.offline then
      self.msg:SetText("|c" .. HEX.faint .. string.format(T.not_announced, e.ago or "?") .. "|r")
    elseif e.match and #e.match > 0 then
      self.msg:SetText("|c" .. HEX.teal .. string.format(ns.RecipeTexts.knows, table.concat(e.match, ", ")) .. "|r")
    else
      self.msg:SetText(p.msg and p.msg ~= "" and ("|c" .. HEX.dim .. "« " .. p.msg .. " »|r") or "")
    end
    ns.FlatBorder(self, e.me and C.gold or (p.avail and C.teal or C.border))
    self.btn:SetShown(not e.me)
    self.btn:SetScript("OnClick", function() whisper(e.name) end)
    self.rec:ClearAllPoints()
    if e.me then self.rec:SetPoint("RIGHT", -10, 0) else self.rec:SetPoint("RIGHT", self.btn, "LEFT", -6, 0) end
    self.rec:SetShown(ns.ShowRecipes ~= nil)
    if ns.RecipeTexts then self.rec:SetText(ns.RecipeTexts.button) end -- Recipes.lua loads after the cards
    self.rec:SetScript("OnClick", function() ns.ShowRecipes(e.name, e.me) end)
    self:Show()
  end
  return c
end

---------------------------------------------------------------------------------------------
-- Page: directory
---------------------------------------------------------------------------------------------
local CARDS, TOP, GAP = 6, -52, 64
local filterIdx, mode, pageNo = 0, 0, 1 -- mode: 0 everyone, 1 available only, 2 favourites
local refreshDir
-- Two sections, one per intention: "prof" (looking for a crafted item) and "craft" (being a crafter).
ns.HubSection("prof", T.sec_find, 20, "BrokenCrafter")
ns.HubSection("craft", T.sec_craft, 25, "BrokenCrafter")
local pDir, dirIndex = ns.HubTab("prof", T.tab_dir, function() refreshDir() end)

-- Three columns like the window: filters (search, who, professions with how many crafters), the
-- crafters as compact rows, and the card of the selected crafter (skills, message, actions).
local MID_W, LIST_W = 262, 306
local DETAIL_W = W - 24 - MID_W - 12 - LIST_W - 12
local ROW_H, ROWS = 62, 9
local selName

-- Left column.
local searchText = ""
local searchBox = ns.Input(pDir)
searchBox:SetSize(MID_W, 24)
searchBox:SetPoint("TOPLEFT", 0, -2)
local searchHint = pDir:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
searchHint:SetPoint("LEFT", searchBox, "LEFT", 8, 0)
searchBox:SetScript("OnTextChanged", function(self)
  searchText = (self:GetText() or ""):gsub("^%s+", ""):gsub("%s+$", "")
  searchHint:SetShown(searchText == "" and not self:HasFocus())
  pageNo = 1
  if searchText ~= "" and ns.RequestRecipes then
    for name, p in pairs(peers) do if p.avail then ns.RequestRecipes(name) end end
  end
  refreshDir()
end)
searchBox:SetScript("OnEditFocusGained", function() searchHint:Hide() end)
searchBox:SetScript("OnEditFocusLost", function() searchHint:SetShown(searchText == "") end)
searchBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)

local modeBtns = {}
for k, key in ipairs({ "mode_all", "mode_avail", "mode_fav" }) do
  local b = ns.Button(pDir, nil, "pill")
  b:SetSize(math.floor((MID_W - 8) / 3), 24)
  b:SetPoint("TOPLEFT", (k - 1) * (math.floor((MID_W - 8) / 3) + 4), -34)
  b:SetText(T[key])
  b:SetScript("OnClick", function() mode = k - 1; pageNo = 1; refreshDir() end)
  modeBtns[k] = b
end

local filterRows = {}
for i = 0, #CRAFTS do
  local b = ns.Button(pDir, nil, "pill")
  b:SetSize(MID_W, 28)
  b:SetPoint("TOPLEFT", 0, -66 - i * 30)
  local fs = b.GetFontString and b:GetFontString()
  if fs then fs:ClearAllPoints(); fs:SetPoint("LEFT", 12, 0); fs:SetWidth(MID_W - 70); fs:SetJustifyH("LEFT") end
  b.count = b:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  b.count:SetPoint("RIGHT", -10, 0)
  b:SetScript("OnClick", function() filterIdx = i; pageNo = 1; refreshDir() end)
  filterRows[i] = b
end

local refreshBtn = ns.Button(pDir, nil, "primary")
refreshBtn:SetSize(MID_W, 26)
refreshBtn:SetPoint("BOTTOMLEFT", 0, 4)
refreshBtn:SetText(T.refresh)
refreshBtn:SetScript("OnClick", function() ns.CraftRequest(true) end)
local dirCount = pDir:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
dirCount:SetPoint("BOTTOMLEFT", 2, 36)
dirCount:SetWidth(MID_W - 4)
dirCount:SetJustifyH("LEFT")
-- Opening the tab is a click too: ask who is available (at most once a minute).
if ns.HubTabButton and ns.HubTabButton(dirIndex) then
  ns.HubTabButton(dirIndex):HookScript("OnClick", function() ns.CraftRequest(false) end)
end

-- The crafters: compact rows.
local function makeRow(parent, w)
  local r = CreateFrame("Button", nil, parent, ns.BACKDROP_TEMPLATE)
  r:SetSize(w, ROW_H - 4)
  ns.Flat(r)
  r.frame = CreateFrame("Frame", nil, r, ns.BACKDROP_TEMPLATE)
  r.frame:SetSize(44, 44)
  r.frame:SetPoint("LEFT", 8, 0)
  ns.Flat(r.frame, ns.C.bg, ns.C.borderBright)
  r.icon = r.frame:CreateTexture(nil, "ARTWORK")
  r.icon:SetPoint("TOPLEFT", 1, -1)
  r.icon:SetPoint("BOTTOMRIGHT", -1, 1)
  r.light = r.frame:CreateTexture(nil, "OVERLAY")
  r.light:SetSize(14, 14)
  r.light:SetPoint("BOTTOMRIGHT", r.frame, "BOTTOMRIGHT", 5, -5)
  r.name = r:CreateFontString(nil, "OVERLAY", "BrokenMetaFontName")
  r.name:SetPoint("TOPLEFT", r.frame, "TOPRIGHT", 10, 1)
  r.name:SetWidth(w - 130)
  r.name:SetJustifyH("LEFT")
  r.name:SetWordWrap(false)
  r.profs = r:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  r.profs:SetPoint("TOPLEFT", r.name, "BOTTOMLEFT", 0, -3)
  r.profs:SetWidth(w - 130)
  r.profs:SetJustifyH("LEFT")
  r.profs:SetWordWrap(false)
  r.msg = r:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  r.msg:SetPoint("TOPLEFT", r.profs, "BOTTOMLEFT", 0, -2)
  r.msg:SetWidth(w - 130)
  r.msg:SetJustifyH("LEFT")
  r.msg:SetWordWrap(false)
  r.btn = ns.Button(r, nil, "primary")
  r.btn:SetSize(58, 22)
  r.btn:SetPoint("RIGHT", -8, 0)
  r.btn:SetText(T.whisper)
  r:SetScript("OnEnter", function(self) if self.SetBackdropColor then self:SetBackdropColor(unpack(C.rowHover)) end end)
  r:SetScript("OnLeave", function(self) if self.SetBackdropColor then self:SetBackdropColor(unpack(C.row)) end end)
  function r:Set(e, only, selected)
    local p = e.p
    self.entry = e
    setRaceIcon(self.icon, p.race, p.sex, p.class)
    self.light:SetTexture(p.avail and "Interface\\FriendsFrame\\StatusIcon-Online" or "Interface\\FriendsFrame\\StatusIcon-Offline")
    local label = "|c" .. classColor(p.class) .. short(e.name) .. "|r  |c" .. HEX.faint .. (p.level or "?") .. "|r"
    if (p.favs or 0) > 0 then label = label .. "  |TInterface\\TargetingFrame\\UI-RaidTargetingIcon_1:11:11:0:0|t|c" .. HEX.gold .. p.favs .. "|r" end
    if e.me then label = label .. "  |c" .. HEX.gold .. "(" .. T.you .. ")|r" end
    self.name:SetText(label)
    local parts = {}
    for _, pr in ipairs(p.profs) do
      if not only or pr.line == only then
        parts[#parts + 1] = ns.ProfIcon(pr.line, 14) .. "|c" .. HEX.cream .. pr.rank .. "|r|c" .. HEX.faint .. "/" .. pr.max .. "|r"
      end
    end
    self.profs:SetText(table.concat(parts, "   "))
    if e.offline then
      self.msg:SetText("|c" .. HEX.faint .. string.format(T.not_announced, e.ago or "?") .. "|r")
    elseif e.match and #e.match > 0 then
      self.msg:SetText("|c" .. HEX.teal .. string.format(ns.RecipeTexts.knows, table.concat(e.match, ", ")) .. "|r")
    else
      self.msg:SetText(p.msg and p.msg ~= "" and ("|c" .. HEX.dim .. "« " .. p.msg .. " »|r") or "")
    end
    ns.FlatBorder(self, selected and C.teal or (e.me and C.gold or C.border))
    self.btn:SetShown(not e.me)
    self.btn:SetScript("OnClick", function() whisper(e.name) end)
    self:SetScript("OnClick", function() selName = e.name; refreshDir() end)
    self:Show()
  end
  return r
end
local dirRows = {}
for i = 1, ROWS do
  dirRows[i] = makeRow(pDir, LIST_W)
  dirRows[i]:SetPoint("TOPLEFT", MID_W + 12, -2 - (i - 1) * ROW_H)
  dirRows[i]:Hide()
end
local prevBtn = ns.Button(pDir)
prevBtn:SetSize(28, 22)
prevBtn:SetPoint("BOTTOMLEFT", MID_W + 12, 4)
prevBtn:SetText("<")
prevBtn:SetScript("OnClick", function() pageNo = pageNo - 1; refreshDir() end)
local nextBtn = ns.Button(pDir)
nextBtn:SetSize(28, 22)
nextBtn:SetPoint("LEFT", prevBtn, "RIGHT", 70, 0)
nextBtn:SetText(">")
nextBtn:SetScript("OnClick", function() pageNo = pageNo + 1; refreshDir() end)
local pageText = pDir:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
pageText:SetPoint("LEFT", prevBtn, "RIGHT", 6, 0)

-- The card of the selected crafter.
local card = CreateFrame("Frame", nil, pDir, ns.BACKDROP_TEMPLATE)
card:SetPoint("TOPLEFT", MID_W + 12 + LIST_W + 12, -2)
card:SetPoint("BOTTOMRIGHT", 0, 4)
ns.Flat(card, C.row, C.border)
card.name = card:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
if ns.MEDIA then pcall(card.name.SetFont, card.name, ns.MEDIA .. "Fonts/CalSans-Regular.ttf", 24, "") end
card.name:SetPoint("TOPLEFT", 14, -14)
card.name:SetWidth(DETAIL_W - 28)
card.name:SetJustifyH("LEFT")
card.name:SetWordWrap(false)
card.sub = card:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
card.sub:SetPoint("TOPLEFT", card.name, "BOTTOMLEFT", 0, -6)
card.sub:SetWidth(DETAIL_W - 28)
card.sub:SetJustifyH("LEFT")
card.sub:SetWordWrap(false)
card.status = card:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
card.status:SetPoint("TOPLEFT", card.sub, "BOTTOMLEFT", 0, -4)
card.status:SetWidth(DETAIL_W - 28)
card.status:SetJustifyH("LEFT")
card.bars = {}
for k = 1, 3 do
  local b = {}
  b.icon = card:CreateTexture(nil, "ARTWORK")
  b.icon:SetSize(20, 20)
  b.icon:SetPoint("TOPLEFT", 14, -108 - (k - 1) * 46)
  b.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
  b.label = card:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  b.label:SetPoint("LEFT", b.icon, "RIGHT", 8, 0)
  b.label:SetWidth(DETAIL_W - 100)
  b.label:SetJustifyH("LEFT")
  b.rank = card:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  b.rank:SetPoint("TOPRIGHT", -14, -112 - (k - 1) * 46)
  b.bg = card:CreateTexture(nil, "ARTWORK")
  b.bg:SetColorTexture(unpack(C.border))
  b.bg:SetHeight(6)
  b.bg:SetPoint("TOPLEFT", 14, -134 - (k - 1) * 46)
  b.bg:SetWidth(DETAIL_W - 28)
  b.fill = card:CreateTexture(nil, "OVERLAY")
  b.fill:SetHeight(6)
  b.fill:SetPoint("TOPLEFT", 14, -134 - (k - 1) * 46)
  card.bars[k] = b
end
card.msg = card:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
card.msg:SetPoint("TOPLEFT", 14, -262)
card.msg:SetWidth(DETAIL_W - 28)
card.msg:SetHeight(60)
card.msg:SetJustifyH("LEFT")
card.msg:SetJustifyV("TOP")
card.empty = card:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
card.empty:SetPoint("TOPLEFT", 14, -16)
card.empty:SetWidth(DETAIL_W - 28)
card.empty:SetJustifyH("LEFT")
card.whisper = ns.Button(card, nil, "primary")
card.whisper:SetSize(DETAIL_W - 28, 32)
card.whisper:SetPoint("BOTTOMLEFT", 14, 76)
card.whisper:SetText(T.whisper_full)
card.fav = ns.Button(card)
card.fav:SetSize(DETAIL_W - 28, 24)
card.fav:SetPoint("BOTTOMLEFT", 14, 44)
card.rec = ns.Button(card)
card.rec:SetSize(DETAIL_W - 28, 24)
card.rec:SetPoint("BOTTOMLEFT", 14, 14)

local function showCard(e)
  local shown = e ~= nil
  for _, f in ipairs({ card.name, card.sub, card.status, card.msg, card.whisper, card.fav, card.rec }) do f:SetShown(shown) end
  card.empty:SetShown(not shown)
  card.empty:SetText("|c" .. HEX.faint .. T.pick_crafter .. "|r")
  for _, b in ipairs(card.bars) do b.icon:Hide(); b.label:Hide(); b.rank:Hide(); b.bg:Hide(); b.fill:Hide() end
  if not e then return end
  local p = e.p
  card.name:SetText("|c" .. classColor(p.class) .. short(e.name) .. "|r")
  local className = LOCALIZED_CLASS_NAMES_MALE and LOCALIZED_CLASS_NAMES_MALE[p.class] or p.class or ""
  card.sub:SetText("|c" .. HEX.dim .. className .. "  ·  " .. string.format(T.lvl_short, p.level or 0) .. "|r")
  card.status:SetText(p.avail and ("|c" .. HEX.teal .. T.avail_on .. "|r")
    or ("|c" .. HEX.faint .. (e.offline and string.format(T.not_announced, e.ago or "?") or T.avail_off) .. "|r"))
  for k, pr in ipairs(p.profs) do
    local b = card.bars[k]
    if b then
      b.icon:SetTexture(ns.ProfIconPath(pr.line))
      b.label:SetText("|c" .. HEX.gold .. profName(pr.line) .. "|r")
      b.rank:SetText("|c" .. HEX.cream .. pr.rank .. "|r|c" .. HEX.faint .. "/" .. pr.max .. "|r")
      b.fill:SetWidth(math.max(1, math.floor((DETAIL_W - 28) * math.min(1, pr.rank / math.max(pr.max, 1)))))
      b.fill:SetColorTexture(unpack(p.avail and C.teal or C.faint))
      b.icon:Show(); b.label:Show(); b.rank:Show(); b.bg:Show(); b.fill:Show()
    end
  end
  card.msg:SetText((p.msg and p.msg ~= "") and ("|c" .. HEX.dim .. "« " .. p.msg .. " »|r") or "")
  card.whisper:SetShown(not e.me)
  card.whisper:SetScript("OnClick", function() whisper(e.name) end)
  card.fav:SetShown(not e.me)
  local isFav = favs()[e.name] ~= nil
  card.fav:SetText((isFav and T.fav_del or T.fav_add))
  card.fav:SetScript("OnClick", function() ns.ToggleCraftFav(e.name, p) end)
  card.rec:SetShown(ns.ShowRecipes ~= nil)
  card.rec:SetText(ns.RecipeTexts and ns.RecipeTexts.button or "Recettes")
  card.rec:SetScript("OnClick", function() ns.ShowRecipes(e.name, e.me) end)
end

local dirEmpty = ns.Callout(pDir, -64, LIST_W + 12 + DETAIL_W, MID_W + 12)

-- Gate: a crafter who has not registered yet sees a frame over the whole directory (filters and
-- list) until they register. A player without any crafting profession is a buyer, not a crafter:
-- no gate for them, they can browse and whisper.
local gate = CreateFrame("Frame", nil, pDir, ns.BACKDROP_TEMPLATE)
gate:SetAllPoints()
gate:SetFrameLevel((pDir:GetFrameLevel() or 0) + 50)
gate:EnableMouse(true) -- swallows the clicks meant for the list below
ns.Flat(gate, C.bg, C.teal)
local gateTitle = gate:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
if ns.MEDIA then pcall(gateTitle.SetFont, gateTitle, ns.MEDIA .. "Fonts/CalSans-Regular.ttf", 24, "") end
gateTitle:SetPoint("TOP", 0, -64)
gateTitle:SetText("|c" .. HEX.gold .. T.gate_title .. "|r")
local gateText = gate:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
gateText:SetPoint("TOP", gateTitle, "BOTTOM", 0, -16)
gateText:SetWidth(W - 160)
gateText:SetJustifyH("CENTER")
gateText:SetText(T.gate_text)
local gateLast = gateText
for i, key in ipairs({ "gate_1", "gate_2", "gate_3" }) do
  local l = gate:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
  l:SetPoint("TOP", gateLast, "BOTTOM", 0, i == 1 and -30 or -16)
  l:SetWidth(W - 160)
  l:SetJustifyH("CENTER")
  l:SetText("|c" .. HEX.teal .. "+|r  " .. T[key])
  gateLast = l
end
local gateBtn = ns.Button(gate, nil, "primary")
gateBtn:SetSize(300, 40)
gateBtn:SetPoint("TOP", gateLast, "BOTTOM", 0, -36)
gateBtn:SetText(T.banner_btn)
gateBtn:SetScript("OnClick", function() ns.RegisterCrafter(true) end)
local function showGate()
  gate:SetShown(not db().registered and #myProfessions() > 0)
end

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
  local function keep(p, name)
    if mode == 1 and not p.avail then return false end
    if mode == 2 and not favs()[name] then return false end
    if not only then return #p.profs > 0 end
    for _, pr in ipairs(p.profs) do if pr.line == only then return true end end
    return false
  end
  local function matches(name, mine)
    if searchText == "" or not ns.RecipeMatches then return nil, true end
    local found, n = ns.RecipeMatches(name, searchText, mine)
    return found, n > 0
  end
  for name, p in pairs(peers) do
    if keep(p, name) then
      local found, ok = matches(name, false)
      if ok then list[#list + 1] = { name = name, p = p, r = rank(p), match = found, fav = favs()[name] ~= nil } end
    end
  end
  -- Favourites not announced right now: their last known profile, greyed.
  for name, f in pairs(favs()) do
    if not peers[name] then
      local fp = snapshot(f.p)
      fp.avail = false
      if keep(fp, name) then
        local found, ok = matches(name, false)
        if ok then list[#list + 1] = { name = name, p = fp, r = rank(fp), match = found, fav = true, offline = true, ago = ns.Ago(f.t) } end
      end
    end
  end
  -- Crafters seen earlier who are not announced right now (not favourites, not me): greyed.
  for name, k in pairs(known()) do
    if not peers[name] and not favs()[name] and name ~= myFull then
      local kp = snapshot(k.p)
      kp.avail = false
      if keep(kp, name) then
        local found, ok = matches(name, false)
        if ok then list[#list + 1] = { name = name, p = kp, r = rank(kp), match = found, fav = false, offline = true, ago = ns.Ago(k.t) } end
      end
    end
  end
  table.sort(list, function(a, b)
    if a.p.avail ~= b.p.avail then return a.p.avail end
    if a.fav ~= b.fav then return a.fav end
    if (a.p.favs or 0) ~= (b.p.favs or 0) then return (a.p.favs or 0) > (b.p.favs or 0) end
    if a.r ~= b.r then return a.r > b.r end
    return a.name < b.name
  end)
  local mine = myEntry()
  if mine and mode ~= 2 and keep(mine.p, myFull) then
    local found, ok = matches(myFull, true)
    mine.match = found
    if ok then table.insert(list, 1, mine) end
  end
  return list, only
end

refreshDir = function()
  -- Crafters per profession (everyone known, whatever the filters), and who is online.
  local counts, seen, total, avail = {}, {}, 0, 0
  local function count(p)
    total = total + 1
    for _, pr in ipairs(p.profs) do counts[pr.line] = (counts[pr.line] or 0) + 1 end
  end
  local online = 0
  for name, p in pairs(peers) do
    if #p.profs > 0 then seen[name] = true; count(p); online = online + 1; if p.avail then avail = avail + 1 end end
  end
  for name, f in pairs(favs()) do if not seen[name] and #f.p.profs > 0 then seen[name] = true; count(f.p) end end
  for name, k in pairs(known()) do if not seen[name] and name ~= myFull and #k.p.profs > 0 then seen[name] = true; count(k.p) end end
  local mine = myEntry()
  if mine and #mine.p.profs > 0 then count(mine.p) end
  for i = 0, #CRAFTS do
    local b = filterRows[i]
    b:SetText(i == 0 and T.all or (ns.ProfIcon(CRAFTS[i], 16) .. profName(CRAFTS[i])))
    b.count:SetText("|c" .. HEX.faint .. (i == 0 and total or (counts[CRAFTS[i]] or 0)) .. "|r")
    if i == filterIdx then b:LockHighlight() else b:UnlockHighlight() end
  end
  for k, b in ipairs(modeBtns) do if mode == k - 1 then b:LockHighlight() else b:UnlockHighlight() end end
  dirCount:SetText(string.format(T.count, online, avail))
  searchHint:SetText("|c" .. HEX.faint .. T.search .. "|r")
  local list, only = ns.CraftList()
  showGate()
  local pages = math.max(1, math.ceil(#list / ROWS))
  pageNo = math.min(math.max(pageNo, 1), pages)
  pageText:SetText(string.format(T.page, pageNo, pages))
  if pageNo > 1 then prevBtn:Enable() else prevBtn:Disable() end
  if pageNo < pages then nextBtn:Enable() else nextBtn:Disable() end
  -- The selected crafter: the one clicked if still listed, else the first.
  local sel
  for _, e in ipairs(list) do if e.name == selName then sel = e end end
  sel = sel or list[1]
  selName = sel and sel.name or nil
  for i = 1, ROWS do
    local e = list[(pageNo - 1) * ROWS + i]
    if e then dirRows[i]:Set(e, only, e == sel) else dirRows[i]:Hide() end
  end
  showCard(sel)
  if #list == 0 then
    dirEmpty:Set({ icon = ns.ProfIconPath(CRAFTS[filterIdx > 0 and filterIdx or 4]), title = T.empty_dir, text = T.none,
      btn = ns.ShowRequests and T.empty_dir_btn or nil, onClick = function() if ns.ShowRequests then ns.ShowRequests() end end })
  else
    dirEmpty:Hide()
  end
end

---------------------------------------------------------------------------------------------
-- Onboarding: the three steps that make a complete crafter card.
---------------------------------------------------------------------------------------------
function ns.CraftOnboarding()
  local profs = myProfessions()
  local recorded = #profs > 0
  for _, p in ipairs(profs) do
    local rec = ns.MyRecipes and ns.MyRecipes()[p.line]
    if not (rec and #rec > 0) then recorded = false end
  end
  local steps = {
    { key = "reg", done = db().registered == true },
    { key = "rec", done = recorded },
    { key = "msg", done = (db().msg or "") ~= "" },
  }
  local n = 0
  for _, st in ipairs(steps) do if st.done then n = n + 1 end end
  return steps, n
end

---------------------------------------------------------------------------------------------
-- Page: my profile
---------------------------------------------------------------------------------------------
local refreshMe
local pMe, meIndex = ns.HubTab("craft", T.tab_me, function() refreshMe() end)
local meIntro = pMe:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
meIntro:SetPoint("TOPLEFT", 4, -2)
meIntro:SetWidth(W - 40)
meIntro:SetJustifyH("LEFT")
meIntro:SetText(T.intro)
local toggle = ns.Button(pMe, nil, "primary")
toggle:SetSize(220, 30)
toggle:SetPoint("TOPLEFT", 4, -48)
toggle:SetScript("OnClick", function()
  if db().registered then ns.SetCraftAvailable(not db().avail) else ns.RegisterCrafter(true) end
end)
local unreg = ns.Button(pMe)
unreg:SetSize(150, 22)
unreg:SetPoint("BOTTOMRIGHT", -4, 34)
unreg:SetText(T.reg_off)
unreg:SetScript("OnClick", function() ns.RegisterCrafter(false) end)
local toggleHint = pMe:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
toggleHint:SetPoint("LEFT", toggle, "RIGHT", 10, 0)
toggleHint:SetWidth(W - 430)
toggleHint:SetJustifyH("LEFT")

local renewBtn = ns.Button(pMe)
renewBtn:SetSize(150, 22)
renewBtn:SetPoint("TOPRIGHT", -4, -52)
renewBtn:SetText(T.renew)
renewBtn:SetScript("OnClick", function() ns.CraftAnnounce(); ns.Toast(T.renewed); if ns.OnCraftChanged then ns.OnCraftChanged() end end)
local msgLabel = pMe:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
msgLabel:SetPoint("TOPLEFT", 4, -92)
msgLabel:SetText(T.msg_label)
local msgBox = ns.Input(pMe)
msgBox:SetSize(W - 150, 22)
msgBox:SetPoint("TOPLEFT", 4, -110)
msgBox:SetAutoFocus(false)
msgBox:SetMaxLetters(MSG_MAX)
local msgSave = ns.Button(pMe)
msgSave:SetSize(100, 22)
msgSave:SetPoint("LEFT", msgBox, "RIGHT", 8, 0)
msgSave:SetText(T.msg_save)

function ns.SetCraftMessage(text)
  db().msg = cleanMessage(text)
  ns.Toast(T.msg_saved)
  if db().avail then ns.CraftAnnounce() end -- from the Save click / Enter key
  if ns.OnCraftChanged then ns.OnCraftChanged() end
end
msgSave:SetScript("OnClick", function() msgBox:ClearFocus(); ns.SetCraftMessage(msgBox:GetText()) end)
msgBox:SetScript("OnEnterPressed", function(self) self:ClearFocus(); ns.SetCraftMessage(self:GetText()) end)
msgBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)

local prevLabel = pMe:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
prevLabel:SetPoint("TOPLEFT", 4, -144)
prevLabel:SetText(T.preview)
local preview = makeCard(pMe, W - 32)
preview:SetPoint("TOPLEFT", 4, -160)

-- Progress of the card (3 steps): a line of ticks and a three-segment bar under the card preview.
local obLabel = pMe:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
obLabel:SetPoint("TOPLEFT", 4, -226)
local obSegs = {}
local segW = math.floor((W - 32 - 8) / 3)
for i = 1, 3 do
  obSegs[i] = pMe:CreateTexture(nil, "ARTWORK")
  obSegs[i]:SetSize(segW, 6)
  obSegs[i]:SetPoint("TOPLEFT", 4 + (i - 1) * (segW + 4), -244)
end
local function showProgress()
  local steps, n = ns.CraftOnboarding()
  local chips = {}
  for i, st in ipairs(steps) do
    local text = T["ob_" .. st.key]
    chips[i] = st.done and ("|c" .. HEX.teal .. "|TInterface\\Buttons\\UI-CheckBox-Check:14:14:0:0|t " .. text .. "|r")
      or ("|c" .. HEX.faint .. "-  " .. text .. "|r")
    obSegs[i]:SetColorTexture(unpack(st.done and C.teal or C.border))
  end
  obLabel:SetText("|c" .. HEX.gold .. string.format(T.ob_title, n) .. "|r      " .. table.concat(chips, "     "))
end

ns.Hub.rows(pMe, 8, -268, 18)

-- brokenmeta.gg crafters page (opt-in): a check box, then a card to copy and paste on the site.
local SITE_KEY_LEN = 32
local function siteKey()
  local d = db()
  if not d.siteKey or #d.siteKey ~= SITE_KEY_LEN then
    local hex = {}
    for i = 1, SITE_KEY_LEN do hex[i] = string.format("%x", math.random(0, 15)) end
    d.siteKey = table.concat(hex) -- proves on the site that later updates come from this character
  end
  return d.siteKey
end

-- "BMC1;k=key;n=Name;r=Realm;f=Horde;c=WARRIOR;ra=Orc;s=2;l=20;fv=3;p=164:150:225,...;m=message;rc=164:1001,1002/197:-2"
function ns.CrafterCard()
  local _, class = UnitClass("player")
  local _, race = UnitRace("player")
  local parts, fans = {}, 0
  for _, pr in ipairs(myProfessions()) do parts[#parts + 1] = pr.line .. ":" .. pr.rank .. ":" .. pr.max end
  for _ in pairs(db().favBy or {}) do fans = fans + 1 end
  local rec = {}
  for line, list in pairs(ns.MyRecipes and ns.MyRecipes() or {}) do
    if #list > 0 then rec[#rec + 1] = line .. ":" .. table.concat(list, ",") end
  end
  local f = {
    "BMC1", "k=" .. siteKey(), "n=" .. myName, "r=" .. (GetRealmName() or ""), "f=" .. (UnitFactionGroup("player") or ""),
    "c=" .. (class or ""), "ra=" .. (race or ""), "s=" .. ((UnitSex and UnitSex("player")) or 2), "l=" .. (UnitLevel("player") or 0),
    "fv=" .. fans, "p=" .. table.concat(parts, ","), "m=" .. cleanMessage(db().msg), "rc=" .. table.concat(rec, "/"),
  }
  return table.concat(f, ";")
end

-- Off until the site's /wow-forever/artisans/ page and its wow-worker routes are live.
local SITE_DIRECTORY = true
local siteCheck = ns.Button(pMe)
siteCheck:SetSize(18, 18)
siteCheck:SetPoint("BOTTOMLEFT", 4, 8)
siteCheck.mark = siteCheck:CreateTexture(nil, "OVERLAY")
siteCheck.mark:SetAllPoints()
siteCheck.mark:SetTexture("Interface\\Buttons\\UI-CheckBox-Check")
local siteLabel = pMe:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
siteLabel:SetPoint("LEFT", siteCheck, "RIGHT", 8, 0)
siteLabel:SetText(T.site_opt)
local siteBtn = ns.Button(pMe, nil, "primary")
siteBtn:SetSize(200, 22)
siteBtn:SetPoint("BOTTOMRIGHT", -4, 6)
siteBtn:SetText(T.site_copy)
siteCheck:SetScript("OnClick", function()
  db().public = not db().public or nil
  if ns.OnCraftChanged then ns.OnCraftChanged() end
end)
siteBtn:SetScript("OnClick", function()
  ns.ShowCopyText(T.site_title, T.site_hint, ns.CrafterCard())
end)
-- The last rows (network status, diagnostics) are long: let them wrap over the free space below.
for _, row in ipairs(pMe.rows) do row[1]:SetWidth(W - 40); row[1]:SetWordWrap(true) end

refreshMe = function()
  local on, reg = db().avail, db().registered
  if not reg then
    toggle:SetText(T.reg_btn)
    toggleHint:SetText("|c" .. HEX.faint .. T.reg_hint .. "|r")
  else
    toggle:SetText(on and ("|c" .. HEX.teal .. T.avail_on .. "|r") or ("|cffff5a6b" .. T.avail_off .. "|r"))
    local age = db().announced and math.floor((time() - db().announced) / 60)
    toggleHint:SetText(on and (age and string.format(T.announced, age) or T.reg_hint_on) or T.reg_hint_off)
  end
  unreg:SetShown(reg == true)
  renewBtn:SetShown(on)
  if not msgBox:HasFocus() then msgBox:SetText(db().msg or "") end
  local mine = myEntry()
  if mine then preview:Set(mine) end
  showProgress()
  local i = 1
  ns.Hub.setRow(pMe, i, "|c" .. HEX.gold .. T.my_profs .. "|r"); i = i + 1
  local profs = myProfessions()
  for _, p in ipairs(profs) do
    local rec = ns.MyRecipes and ns.MyRecipes()[p.line]
    ns.Hub.setRow(pMe, i, ns.ProfIcon(p.line, 14) .. profName(p.line) .. "  |c" .. HEX.faint .. (rec and string.format(T.rec_count, #rec) or T.rec_none) .. "|r",
      "|cffffffff" .. p.rank .. "|r/" .. p.max); i = i + 1
  end
  if #profs == 0 then ns.Hub.setRow(pMe, i, "|c" .. HEX.faint .. T.no_prof .. "|r"); i = i + 1 end
  i = i + 1
  local seen = 0
  for _ in pairs(peers) do seen = seen + 1 end
  ns.Hub.setRow(pMe, i, channelId > 0 and ("|c" .. HEX.teal .. string.format(T.net_ok, seen) .. "|r")
    or (joinFailed and ("|cffff5a6b" .. T.net_fail .. "|r") or ("|c" .. HEX.faint .. T.net_wait .. "|r"))); i = i + 1
  ns.Hub.setRow(pMe, i, "|c" .. HEX.faint .. string.format(T.diag, channelId, stats.sent, stats.recv, stats.echo,
    stats.last or "-", stats.result or "-") .. "|r"); i = i + 1
  ns.Hub.clearRows(pMe, i)
  siteCheck.mark:SetShown(db().public == true)
  if db().public then siteBtn:Enable() else siteBtn:Disable() end
  siteCheck:SetShown(SITE_DIRECTORY); siteLabel:SetShown(SITE_DIRECTORY); siteBtn:SetShown(SITE_DIRECTORY)
end

function ns.OnCraftChanged()
  ns.HubRefresh(dirIndex)
  ns.HubRefresh(meIndex)
end

function ns.ShowCrafters() ns.HubShow(dirIndex) end
