-- BrokenMeta hub window (/bmw): Character (spec, weights, equipped gear value), Upgrades (bag
-- items worth more than what's equipped) and Export (a text string to paste on brokenmeta.gg).
local ADDON, ns = ...
local IS_FR = ns.IS_FR

local T = ns.Localize("hub", {
  title = "BrokenMeta · Hub DPS",
  tab_char = "Personnage", tab_up = "Améliorations", tab_export = "Export", tab_cmd = "Commandes", tab_data = "Données",
  tab_guide = "Guide",
  up_bags = "Dans tes sacs", up_dungeons = "Dans les donjons (meilleur objet par emplacement)",
  up_best = "Donjon le plus rentable : %s (%d amélioration(s), +%.2f DPS)", up_level = "niv. %d",
  no_dungeon = "Aucune amélioration trouvée dans les donjons pour ton niveau.",
  guide_h = "Guide de ta spécialisation", guide_follow = "Tu suis %d des %d talents conseillés par le guide (modèle niveau %d).",
  guide_nobuild = "Le guide complet de ta spécialisation (talents, priorité de stats, consommables, métiers) est sur brokenmeta.gg.",
  guide_more = "Talents détaillés, priorité de stats, consommables et métiers : tout est dans le guide sur brokenmeta.gg.",
  guide_copy = "Copier le lien du guide", prof_h = "Tes métiers",
  prof_next = "%s %d/%d : prochaine recette %s (%d-%d), environ %d fois",
  prof_done = "%s %d/%d : itinéraire terminé", prof_none = "Aucun de tes métiers n'a encore de guide sur le site.",
  prof_copy = "Lien du guide", link_title = "Lien brokenmeta.gg",
  link_hint = "Le lien est déjà sélectionné : Ctrl+C, puis colle-le dans ton navigateur.",
  data_h = "Données pour brokenmeta.gg",
  data_intro = "L'addon enregistre ce que le jeu affiche réellement (critique, régénération de mana, familier, conversion des cotes) et les prix de l'hôtel des ventes que tu scannes. Tout reste sur ton ordinateur : rien n'est envoyé tant que le partage est désactivé. Aucun nom de personnage n'est collecté ; les prix gardent le royaume et la faction. Pour partager : active le partage, clique sur « Copier pour le site », puis colle le texte sur brokenmeta.gg/wow-forever/partager-mes-donnees/",
  share_on = "Partage : ACTIVÉ", share_off = "Partage : désactivé",
  snap = "Enregistrer maintenant",
  w_generic = "génériques niv. 20", w_custom = "tes poids (niv. %d, %s)", w_hint_level = "Tu n'es pas niveau 20 : calcule tes poids à ton niveau sur brokenmeta.gg (Simuler mon personnage), puis importe-les. À refaire tous les 5 niveaux.", w_hint_refresh = "Tes poids datent du niveau %d : refais-les sur brokenmeta.gg (tous les %d niveaux).", import_btn = "Importer mes poids", reset_btn = "Poids génériques", import_do = "Importer", import_title = "Importer mes poids de stats", import_hint = "Colle ici (Ctrl+V) le texte « BMW-W1… » copié sur brokenmeta.gg (Simuler mon personnage > Calculer mes poids > Copier pour l'addon), puis clique sur Importer.", scan = "Scanner l'hôtel des ventes", copy = "Copier pour le site",
  copy_title = "Données à coller sur brokenmeta.gg",
  copy_hint = "Le texte est déjà sélectionné : Ctrl+C, puis colle-le sur brokenmeta.gg/wow-forever/partager-mes-donnees/ (case « Coller le texte de l'addon »).",
  copy_off = "Active d'abord le partage (bouton Partage), le texte ne sort de l'addon que si tu le choisis.",
  copy_empty = "Aucune donnée pour l'instant : joue un peu ou scanne l'hôtel des ventes.",
  scan_hint = "Ouvre l'hôtel des ventes (parle à un commissaire-priseur) pour activer le scan.",
  meas = "Mesures enregistrées", meas_detail = "%d (feuille de perso %d · familier %d · cotes %d)",
  ah_h = "Hôtel des ventes", ah_none = "Aucun scan. Ouvre l'hôtel des ventes et clique sur « BrokenMeta : scanner les prix ».",
  ah_last = "Dernier scan : %s · %s (%s) · %d annonces · %d objets", ah_mode = "Mode de scan du client : %s",
  ah_count = "Scans conservés : %d",
  run = "Lancer", cmd_hint = "Commandes à taper dans le chat (ou clique sur Lancer).",
  cmds = {
    { "", "/bmw", "Ouvre ou ferme cette fenêtre." },
    { "weights", "/bmw weights", "Affiche les poids de ta spé dans le chat." },
    { "export", "/bmw export", "Ouvre l'onglet Export (texte à coller sur brokenmeta.gg)." },
    { "list", "/bmw list", "Liste les spécialisations simulées de ta classe." },
    { nil, "/bmw spec <id>", "Force une spé, ex. /bmw spec %s" },
    { "auto", "/bmw auto", "Revient à la détection automatique par tes talents." },
    { "minimap", "/bmw minimap", "Affiche ou masque le bouton de la minicarte." },
    { "share", "/bmw share on|off", "Active ou coupe le partage des données avec brokenmeta.gg." },
    { "ah", "/bmw ah", "Scanne l'hôtel des ventes (il doit être ouvert)." },
    { "import", "/bmw import", "Importe tes poids personnels calculés sur brokenmeta.gg (/bmw import clear pour revenir aux poids génériques)." },
    { "probe", "/bmw probe", "Diagnostic : fonctions du client et points par arbre." },
  },
  spec = "Spécialisation", weights = "Poids (DPS simulé par point)",
  gear = "Équipement porté", total = "Total des stats de l'équipement",
  empty = "vide", no_upgrade = "Aucune amélioration dans tes sacs.",
  up_hint = "Objets de tes sacs et des donjons qui valent plus que ton équipement pour ta spé. Seuls les objets que ta classe peut porter sont listés.",
  export_hint = "Ctrl+C pour copier, puis colle sur brokenmeta.gg. Contient : classe, spé, niveau, race, talents, équipement (ID d'objets), stats de la feuille de personnage. Ni nom ni royaume.",
  approx = "conversion approximative",
  wdps_line = "DPS d'arme (par point) : main droite %.3f · main gauche %.3f · distance %.3f",
  no_spec = "Aucune spécialisation DPS simulée pour ta classe.",
  rating = "cote",
}, {
  title = "BrokenMeta · DPS Hub",
  tab_char = "Character", tab_up = "Upgrades", tab_export = "Export", tab_cmd = "Commands", tab_data = "Data",
  tab_guide = "Guide",
  up_bags = "In your bags", up_dungeons = "In dungeons (best item per slot)",
  up_best = "Most rewarding dungeon: %s (%d upgrade(s), +%.2f DPS)", up_level = "lvl %d",
  no_dungeon = "No dungeon upgrade found for your level.",
  guide_h = "Your specialization guide", guide_follow = "You follow %d of the %d talents the guide recommends (level %d template).",
  guide_nobuild = "Your specialization's full guide (talents, stat priority, consumables, professions) is on brokenmeta.gg.",
  guide_more = "Detailed talents, stat priority, consumables and professions: it's all in the guide on brokenmeta.gg.",
  guide_copy = "Copy the guide link", prof_h = "Your professions",
  prof_next = "%s %d/%d: next recipe %s (%d-%d), about %d crafts",
  prof_done = "%s %d/%d: route completed", prof_none = "None of your professions has a guide on the site yet.",
  prof_copy = "Guide link", link_title = "brokenmeta.gg link",
  link_hint = "The link is already selected: Ctrl+C, then paste it in your browser.",
  data_h = "Data for brokenmeta.gg",
  data_intro = "The addon records what the game really reports (crit, mana regen, pet, rating conversion) and the auction prices you scan. Everything stays on your computer: nothing is sent while sharing is off. No character name is collected; prices keep the realm and faction. To share: turn sharing on, click \"Copy for the site\", then paste the text on brokenmeta.gg/wow-forever/partager-mes-donnees/",
  share_on = "Sharing: ON", share_off = "Sharing: off",
  snap = "Record now",
  w_generic = "generic lvl 20", w_custom = "your weights (lvl %d, %s)", w_hint_level = "You're not level 20: compute your weights at your level on brokenmeta.gg (Simulate my character), then import them. Redo it every 5 levels.", w_hint_refresh = "Your weights are from level %d: redo them on brokenmeta.gg (every %d levels).", import_btn = "Import my weights", reset_btn = "Generic weights", import_do = "Import", import_title = "Import my stat weights", import_hint = "Paste here (Ctrl+V) the 'BMW-W1...' text copied on brokenmeta.gg (Simulate my character > Compute my weights > Copy for the addon), then click Import.", scan = "Scan the auction house", copy = "Copy for the site",
  copy_title = "Data to paste on brokenmeta.gg",
  copy_hint = "The text is already selected: Ctrl+C, then paste it on brokenmeta.gg/wow-forever/partager-mes-donnees/ (\"Paste the addon text\" box).",
  copy_off = "Turn sharing on first (Sharing button): the text only leaves the addon if you choose so.",
  copy_empty = "No data yet: play a bit or scan the auction house.",
  scan_hint = "Open the auction house (talk to an auctioneer) to enable the scan.",
  meas = "Recorded measurements", meas_detail = "%d (character sheet %d · pet %d · ratings %d)",
  ah_h = "Auction house", ah_none = "No scan yet. Open the auction house and click \"BrokenMeta: scan prices\".",
  ah_last = "Last scan: %s · %s (%s) · %d listings · %d items", ah_mode = "Client scan mode: %s",
  ah_count = "Scans kept: %d",
  run = "Run", cmd_hint = "Commands to type in chat (or click Run).",
  cmds = {
    { "", "/bmw", "Opens or closes this window." },
    { "weights", "/bmw weights", "Prints your spec's weights in chat." },
    { "export", "/bmw export", "Opens the Export tab (text to paste on brokenmeta.gg)." },
    { "list", "/bmw list", "Lists your class's simulated specs." },
    { nil, "/bmw spec <id>", "Forces a spec, e.g. /bmw spec %s" },
    { "auto", "/bmw auto", "Back to automatic detection from your talents." },
    { "minimap", "/bmw minimap", "Shows or hides the minimap button." },
    { "share", "/bmw share on|off", "Turns data sharing with brokenmeta.gg on or off." },
    { "ah", "/bmw ah", "Scans the auction house (it must be open)." },
    { "import", "/bmw import", "Imports your personal weights computed on brokenmeta.gg (/bmw import clear to go back to generic weights)." },
    { "probe", "/bmw probe", "Diagnostics: client functions and points per tree." },
  },
  spec = "Specialization", weights = "Weights (simulated DPS per point)",
  gear = "Equipped gear", total = "Gear stats total",
  empty = "empty", no_upgrade = "No upgrade in your bags.",
  up_hint = "Items from your bags and from dungeons worth more than your gear for your spec. Only items your class can wear are listed.",
  export_hint = "Ctrl+C to copy, then paste on brokenmeta.gg. Contains: class, spec, level, race, talents, gear (item IDs), character sheet stats. No name, no realm.",
  approx = "approximate conversion",
  wdps_line = "Weapon DPS (per point): main hand %.3f · off hand %.3f · ranged %.3f",
  no_spec = "No simulated DPS spec for your class.",
  rating = "rating",
})

local SLOT_ORDER = {
  { 1, "HEADSLOT" }, { 2, "NECKSLOT" }, { 3, "SHOULDERSLOT" }, { 15, "BACKSLOT" }, { 5, "CHESTSLOT" },
  { 9, "WRISTSLOT" }, { 10, "HANDSSLOT" }, { 6, "WAISTSLOT" }, { 7, "LEGSSLOT" }, { 8, "FEETSLOT" },
  { 11, "FINGER0SLOT" }, { 12, "FINGER1SLOT" }, { 13, "TRINKET0SLOT" }, { 14, "TRINKET1SLOT" },
  { 16, "MAINHANDSLOT" }, { 17, "SECONDARYHANDSLOT" }, { 18, "RANGEDSLOT" },
}
local function slotLabel(key) return _G[key] or key end

---------------------------------------------------------------------------------------------
-- Frame
---------------------------------------------------------------------------------------------
local W, H = 590, 560
local hub = CreateFrame("Frame", "BrokenMetaHub", UIParent, "BasicFrameTemplateWithInset")
hub:SetSize(W, H)
hub:SetPoint("CENTER")
hub:SetFrameStrata("HIGH")
hub:SetMovable(true)
hub:EnableMouse(true)
hub:RegisterForDrag("LeftButton")
hub:SetScript("OnDragStart", hub.StartMoving)
hub:SetScript("OnDragStop", hub.StopMovingOrSizing)
hub:SetClampedToScreen(true)
hub:Hide()
tinsert(UISpecialFrames, "BrokenMetaHub") -- Escape closes it

hub.title = hub:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
hub.title:SetPoint("TOP", 0, -5)
hub.title:SetText("|TInterface\\AddOns\\BrokenMetaWeights\\Media\\icon:16|t " .. T.title)

local pages, tabs = {}, {}
local function newPage()
  local p = CreateFrame("Frame", nil, hub)
  p:SetPoint("TOPLEFT", 12, -62)
  p:SetPoint("BOTTOMRIGHT", -12, 12)
  p:Hide()
  pages[#pages + 1] = p
  return p
end

local current = 1
local refreshers = {}
local function showPage(i)
  current = i
  for j, p in ipairs(pages) do p:SetShown(j == i) end
  for j, b in ipairs(tabs) do
    if j == i then b:LockHighlight() else b:UnlockHighlight() end
  end
  if refreshers[i] then refreshers[i]() end
end

-- Tab buttons in display order; each opens the page created with that index below.
for pos, def in ipairs({ { T.tab_char, 1 }, { T.tab_up, 2 }, { T.tab_guide, 6 }, { T.tab_data, 5 },
    { T.tab_export, 3 }, { T.tab_cmd, 4 } }) do
  local b = CreateFrame("Button", nil, hub, "UIPanelButtonTemplate")
  b:SetSize(91, 22)
  b:SetPoint("TOPLEFT", 12 + (pos - 1) * 94, -30)
  b:SetText(def[1])
  b:SetScript("OnClick", function() showPage(def[2]) end)
  tabs[def[2]] = b
end

-- Reusable rows: optional item icon, left/right text, and a hover area that shows the item's
-- real tooltip (equipped slot or item link).
local function rows(page, n, top, lineH, withIcon)
  page.rows = {}
  for i = 1, n do
    local y = top - (i - 1) * lineH
    local icon
    if withIcon then
      icon = page:CreateTexture(nil, "ARTWORK")
      icon:SetSize(lineH - 2, lineH - 2)
      icon:SetPoint("TOPLEFT", 4, y + 1)
      icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    end
    local l = page:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    l:SetPoint("TOPLEFT", withIcon and (lineH + 6) or 4, y)
    l:SetWidth(W - 150)
    l:SetJustifyH("LEFT")
    l:SetWordWrap(false)
    local r = page:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    r:SetPoint("TOPRIGHT", -4, y)
    r:SetJustifyH("RIGHT")
    local row = { l, r, icon = icon }
    local hover = CreateFrame("Button", nil, page)
    hover:SetPoint("TOPLEFT", 0, y + 2)
    hover:SetSize(W - 24, lineH)
    hover:SetScript("OnEnter", function(self)
      if not row.slot and not row.link then return end
      GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
      if row.slot then GameTooltip:SetInventoryItem("player", row.slot) else GameTooltip:SetHyperlink(row.link) end
      GameTooltip:Show()
    end)
    hover:SetScript("OnLeave", function() GameTooltip:Hide() end)
    page.rows[i] = row
  end
end

-- item = { icon = texture, dim = bool, slot = inventory slot } or { icon = texture, link = item link }
local function setRow(page, i, left, right, item)
  local row = page.rows[i]
  if not row then return end
  row[1]:SetText(left or "")
  row[2]:SetText(right or "")
  if row.icon then
    row.icon:SetTexture(item and item.icon or nil)
    row.icon:SetDesaturated(item and item.dim or false)
    row.icon:SetAlpha(item and item.dim and 0.4 or 1)
  end
  row.slot = item and item.slot or nil
  row.link = item and item.link or nil
end

local function clearRows(page, from)
  for i = from, #page.rows do setRow(page, i) end
end

local function fmtDelta(d)
  if d > 0.005 then return string.format("|cff40ff40+%.2f|r", d) end
  if d < -0.005 then return string.format("|cffff5050%.2f|r", d) end
  return "|cffcccccc0.00|r"
end

---------------------------------------------------------------------------------------------
-- Page 1: Character
---------------------------------------------------------------------------------------------
local pChar = newPage()

local specText = pChar:CreateFontString(nil, "OVERLAY", "GameFontNormal")
specText:SetPoint("TOP", 0, -4)

local function cycleSpec(step)
  local list = ns.classSpecs()
  if #list == 0 then return end
  local idx = 1
  for i, id in ipairs(list) do if id == ns.GetSpec() then idx = i end end
  idx = (idx - 1 + step) % #list + 1
  ns.ChooseSpec(list[idx])
end

for _, def in ipairs({ { "<", -1, "TOPLEFT", 4 }, { ">", 1, "TOPRIGHT", -4 } }) do
  local b = CreateFrame("Button", nil, pChar, "UIPanelButtonTemplate")
  b:SetSize(28, 20)
  b:SetPoint(def[3], def[4], 0)
  b:SetText(def[1])
  b:SetScript("OnClick", function() cycleSpec(def[2]) end)
end

rows(pChar, 26, -30, 15, true)

local importBtn = CreateFrame("Button", nil, pChar, "UIPanelButtonTemplate")
importBtn:SetSize(180, 22)
importBtn:SetPoint("BOTTOMLEFT", 4, 4)
importBtn:SetText(T.import_btn)
importBtn:SetScript("OnClick", function() if ns.ShowImportDialog then ns.ShowImportDialog() end end)
local resetBtn = CreateFrame("Button", nil, pChar, "UIPanelButtonTemplate")
resetBtn:SetSize(180, 22)
resetBtn:SetPoint("LEFT", importBtn, "RIGHT", 8, 0)
resetBtn:SetText(T.reset_btn)
resetBtn:SetScript("OnClick", function() SlashCmdList.BROKENMETAWEIGHTS("import clear") end)

refreshers[1] = function()
  local spec = ns.GetSpec()
  if not spec then
    specText:SetText(T.no_spec)
    clearRows(pChar, 1)
    return
  end
  specText:SetText(T.spec .. " : |cffffffff" .. ns.specName(spec) .. "|r")
  local w, custom = ns.ActiveWeights(spec)
  local rp = ns.GetRatingPerPct()
  local i = 1
  setRow(pChar, i, "|cffffd100" .. T.weights .. "|r", custom
    and string.format("|cff40ff40" .. T.w_custom .. "|r", custom.level or 0, custom.date or "?")
    or ("|cff888888" .. T.w_generic .. "|r")); i = i + 1
  setRow(pChar, i, string.format(IS_FR and "Force %.3f · Agilité %.3f · Intelligence %.3f"
    or "Strength %.3f · Agility %.3f · Intellect %.3f", w.str, w.agi, w.int)); i = i + 1
  setRow(pChar, i, string.format(IS_FR and "Puiss. d'attaque %.3f · Puiss. des sorts %.3f" or "Attack power %.3f · Spell power %.3f", w.ap, w.sp)); i = i + 1
  setRow(pChar, i, string.format(IS_FR and "Critique 1%% %.3f (%.1f %s) · Toucher 1%% %.3f (%.1f %s)"
    or "Crit 1%% %.3f (%.1f %s) · Hit 1%% %.3f (%.1f %s)",
    w.crit, rp.crit, T.rating, w.hit, rp.hit, T.rating),
    rp.crit_approx and ("|cff888888" .. T.approx .. "|r") or nil); i = i + 1
  if (w.wdps_mh or 0) + (w.wdps_oh or 0) + (w.wdps_r or 0) > 0 then
    setRow(pChar, i, string.format(T.wdps_line, w.wdps_mh or 0, w.wdps_oh or 0, w.wdps_r or 0)); i = i + 1
  end
  i = i + 1
  setRow(pChar, i, "|cffffd100" .. T.gear .. "|r", "|cffffd100DPS|r"); i = i + 1
  local total = 0
  for _, s in ipairs(SLOT_ORDER) do
    local link = GetInventoryItemLink("player", s[1])
    local v = link and ns.score(link) or 0
    total = total + v
    local icon, dim = GetInventoryItemTexture("player", s[1]), false
    if not icon then
      -- empty slot: the game's own grey slot silhouette
      local ok, _, tex = pcall(GetInventorySlotInfo, s[2])
      icon, dim = ok and tex or nil, true
    end
    setRow(pChar, i, slotLabel(s[2]) .. " : " .. (link or ("|cff888888" .. T.empty .. "|r")),
      link and string.format("%.2f", v) or "", { icon = icon, dim = dim, slot = link and s[1] or nil }); i = i + 1
  end
  setRow(pChar, i, "|cffffd100" .. T.total .. "|r", string.format("|cffffffff%.2f|r", total)); i = i + 1
  if not custom and (UnitLevel("player") or 20) ~= 20 then
    setRow(pChar, i, "|cffff9900" .. T.w_hint_level .. "|r"); i = i + 1
  elseif custom and ns.ImportedWeightsStale() then
    setRow(pChar, i, "|cffff9900" .. string.format(T.w_hint_refresh, custom.level, ns.REFRESH_LEVELS) .. "|r"); i = i + 1
  end
  clearRows(pChar, i)
end

---------------------------------------------------------------------------------------------
-- Page 2: Upgrades from bags
---------------------------------------------------------------------------------------------
local pUp = newPage()
local upHint = pUp:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
upHint:SetPoint("TOPLEFT", 4, -2)
upHint:SetPoint("TOPRIGHT", -4, -2)
upHint:SetJustifyH("LEFT")
upHint:SetText(T.up_hint)
rows(pUp, 24, -40, 17, true)

local Container = C_Container or {}
local GetNumSlots = Container.GetContainerNumSlots or GetContainerNumSlots
local GetBagLink = Container.GetContainerItemLink or GetContainerItemLink

local QUALITY = { [2] = "1eff00", [3] = "0070dd", [4] = "a335ee", [5] = "ff8000" }
local function lootLink(it)
  local name = select(1, ns.GetItemInfo(it.id)) or it.n
  return "|cff" .. (QUALITY[it.q] or "ffffff") .. "|Hitem:" .. it.id .. "::::::::|h[" .. name .. "]|h|r"
end

-- Best dungeon item per equipment slot that beats what is worn (wearable by the class, required
-- level at most 3 above the player's), plus the dungeon whose best items add up to the most DPS.
local function dungeonUpgrades()
  local level = UnitLevel("player") or 1
  local best = {}
  for _, it in ipairs(ns.LOOT or {}) do
    local slots = it.slot and ns.SLOTS[it.slot]
    if slots and (it.req or 0) <= level + 3 and ns.CanWearType(it.t) then
      local v = ns.scoreStats(it.st, it.slot) or 0
      if v > 0 then
        local worst
        for _, slot in ipairs(slots) do
          local eq = GetInventoryItemLink("player", slot)
          local ev = eq and ns.score(eq) or 0
          if not worst or ev < worst then worst = ev end
        end
        local gain = v - (worst or 0)
        if gain > 0.005 and (not best[it.slot] or gain > best[it.slot].gain) then
          best[it.slot] = { it = it, gain = gain }
        end
      end
    end
  end
  local list, perDungeon = {}, {}
  for _, b in pairs(best) do
    list[#list + 1] = b
    local pd = perDungeon[b.it.d] or { n = 0, gain = 0 }
    pd.n, pd.gain = pd.n + 1, pd.gain + b.gain
    perDungeon[b.it.d] = pd
  end
  table.sort(list, function(x, y) return x.gain > y.gain end)
  local top
  for d, pd in pairs(perDungeon) do
    if not top or pd.gain > top.gain then top = { d = d, n = pd.n, gain = pd.gain } end
  end
  return list, top
end

local function dungeonName(i)
  local dg = ns.DUNGEONS and ns.DUNGEONS[i]
  if not dg then return "?" end
  return (dg.name[IS_FR and "frFR" or "enUS"] or dg.name.enUS) .. (dg.levels ~= "" and (" (" .. dg.levels .. ")") or "")
end

refreshers[2] = function()
  local found = {}
  if ns.GetSpec() and GetNumSlots and GetBagLink then
    local level = UnitLevel("player") or 1
    for bag = 0, (NUM_BAG_SLOTS or 4) do
      for slot = 1, (GetNumSlots(bag) or 0) do
        local link = GetBagLink(bag, slot)
        local loc = link and select(9, ns.GetItemInfo(link))
        local minLevel = link and select(5, ns.GetItemInfo(link)) or 0
        if loc and ns.SLOTS[loc] and minLevel <= level and ns.CanWearLink(link) then
          local v = ns.score(link)
          local d = v and ns.deltaVsEquipped(link, v)
          if d and d > 0.005 then found[#found + 1] = { link = link, d = d } end
        end
      end
    end
  end
  table.sort(found, function(a, b) return a.d > b.d end)
  local i = 1
  setRow(pUp, i, "|cffffd100" .. T.up_bags .. "|r"); i = i + 1
  if #found == 0 then
    setRow(pUp, i, "|cff888888" .. T.no_upgrade .. "|r"); i = i + 1
  end
  for k = 1, math.min(#found, 6) do
    local f = found[k]
    setRow(pUp, i, f.link, fmtDelta(f.d) .. " DPS", { icon = select(10, ns.GetItemInfo(f.link)), link = f.link }); i = i + 1
  end
  i = i + 1
  setRow(pUp, i, "|cffffd100" .. T.up_dungeons .. "|r"); i = i + 1
  local list, top = dungeonUpgrades()
  if top then
    setRow(pUp, i, string.format(T.up_best, dungeonName(top.d), top.n, top.gain)); i = i + 1
  else
    setRow(pUp, i, "|cff888888" .. T.no_dungeon .. "|r"); i = i + 1
  end
  local level = UnitLevel("player") or 1
  for _, b in ipairs(list) do
    if i > #pUp.rows then break end
    local it = b.it
    local extra = (it.req or 0) > level and (" · " .. string.format(T.up_level, it.req)) or ""
    local icon = (C_Item and C_Item.GetItemIconByID and C_Item.GetItemIconByID(it.id)) or (GetItemIcon and GetItemIcon(it.id))
    setRow(pUp, i, lootLink(it) .. "  |cff888888" .. dungeonName(it.d) .. extra .. "|r", fmtDelta(b.gain) .. " DPS",
      { icon = icon, link = "item:" .. it.id }); i = i + 1
  end
  clearRows(pUp, i)
end

---------------------------------------------------------------------------------------------
-- Page 3: Export
---------------------------------------------------------------------------------------------
local pExp = newPage()
local expHint = pExp:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
expHint:SetPoint("TOPLEFT", 4, -2)
expHint:SetPoint("TOPRIGHT", -4, -2)
expHint:SetJustifyH("LEFT")
expHint:SetText(T.export_hint)

local scroll = CreateFrame("ScrollFrame", "BrokenMetaHubExportScroll", pExp, "UIPanelScrollFrameTemplate")
scroll:SetPoint("TOPLEFT", 4, -56)
scroll:SetPoint("BOTTOMRIGHT", -26, 4)
local box = CreateFrame("EditBox", nil, scroll)
box:SetMultiLine(true)
box:SetAutoFocus(false)
box:SetFontObject(ChatFontNormal)
box:SetWidth(W - 60)
box:SetScript("OnEscapePressed", function() hub:Hide() end)
scroll:SetScrollChild(box)

-- pcall wrapper that keeps every return value, including nils in the middle (UnitDamage returns
-- nil off-hand values without an off-hand, which a table + unpack would silently cut short).
local function safe(fn, ...)
  if type(fn) ~= "function" then return nil end
  return (function(ok, ...) if ok then return ... end end)(pcall(fn, ...))
end

local function num(v) return v and tostring(tonumber(string.format("%.2f", v))) or "" end

-- Plain "key=value" lines, one per line: readable by a human, trivial for the site to parse.
local function buildExport()
  local out = {}
  local function add(k, v) out[#out + 1] = k .. "=" .. tostring(v == nil and "" or v) end
  add("format", "BMW1")
  add("addon", (C_AddOns and C_AddOns.GetAddOnMetadata or GetAddOnMetadata or function() end)(ADDON, "Version"))
  add("client", select(1, GetBuildInfo()) .. "." .. select(2, GetBuildInfo()))
  add("date", date("!%Y-%m-%dT%H:%M:%SZ"))
  add("class", ns.PlayerClass())
  add("spec", ns.GetSpec())
  add("level", UnitLevel("player"))
  add("race", select(2, UnitRace("player")))
  -- Character sheet: effective primary stats, attack power, spell power, crit/hit as shown in game.
  for i, k in ipairs({ "str", "agi", "sta", "int", "spi" }) do add(k, select(2, safe(UnitStat, "player", i))) end
  local base, pos, neg = safe(UnitAttackPower, "player")
  if base then add("ap", base + (pos or 0) + (neg or 0)) end
  local rbase, rpos, rneg = safe(UnitRangedAttackPower, "player")
  if rbase then add("rap", rbase + (rpos or 0) + (rneg or 0)) end
  -- Spell power per school (2 holy, 3 fire, 4 nature, 5 frost, 6 shadow, 7 arcane) + the best one.
  local sp = 0
  for school, name in pairs({ [2] = "holy", [3] = "fire", [4] = "nature", [5] = "frost", [6] = "shadow", [7] = "arcane" }) do
    local v = safe(GetSpellBonusDamage, school) or 0
    add("sp_" .. name, v)
    sp = math.max(sp, v)
  end
  add("sp", sp)
  local spellCrit = 0
  for school = 2, 7 do spellCrit = math.max(spellCrit, safe(GetSpellCritChance, school) or 0) end
  add("crit_melee", num(safe(GetCritChance)))
  add("crit_ranged", num(safe(GetRangedCritChance)))
  add("crit_spell", num(spellCrit))
  -- Hit: flat modifiers (talents, items) + what hit rating converts to at the current level.
  local function ratingPct(cr)
    local rating = cr and safe(GetCombatRating, cr)
    if not rating or rating <= 0 then return 0 end
    return safe(GetCombatRatingBonusForCombatRatingValue, cr, rating) or safe(GetCombatRatingBonus, cr) or 0
  end
  add("hit_melee", num((safe(GetHitModifier) or 0) + ratingPct(CR_HIT_MELEE or 6)))
  add("hit_ranged", num((safe(GetHitModifier) or 0) + ratingPct(CR_HIT_RANGED or 7)))
  add("hit_spell", num((safe(GetSpellHitModifier) or 0) + ratingPct(CR_HIT_SPELL or 8)))
  -- Weapons as the character sheet shows them (AP bonus and % modifiers included).
  local mh, oh = safe(UnitAttackSpeed, "player")
  add("speed_mh", num(mh)); add("speed_oh", num(oh))
  local mhMin, mhMax, ohMin, ohMax, _, _, pct = safe(UnitDamage, "player")
  add("mh_min", num(mhMin)); add("mh_max", num(mhMax))
  add("oh_min", num(ohMin)); add("oh_max", num(ohMax)); add("dmg_pct", num(pct))
  local rSpeed, rMin, rMax, _, _, rPct = safe(UnitRangedDamage, "player")
  add("r_speed", num(rSpeed)); add("r_min", num(rMin)); add("r_max", num(rMax)); add("r_pct", num(rPct))
  -- Active buffs inflate sheet stats; the site warns when this is above 0.
  local buffs = 0
  if C_UnitAuras and C_UnitAuras.GetAuraDataByIndex then
    while safe(C_UnitAuras.GetAuraDataByIndex, "player", buffs + 1, "HELPFUL") do buffs = buffs + 1 end
  elseif UnitBuff then
    while safe(UnitBuff, "player", buffs + 1) do buffs = buffs + 1 end
  end
  add("buffs", buffs)
  -- Talents: points per tree and node:rank pairs (the site calculator's own node ids).
  local ranks, perTab = ns.readTalents()
  if perTab then add("talent_points", table.concat(perTab, "/")) end
  if ranks then
    local list = {}
    for node, r in pairs(ranks) do list[#list + 1] = node .. ":" .. r end
    table.sort(list)
    add("talents", table.concat(list, ","))
  end
  -- Gear: slot=itemID:enchantID:suffixID (from the item string, no personal data).
  for _, s in ipairs(SLOT_ORDER) do
    local link = GetInventoryItemLink("player", s[1])
    local istr = link and link:match("|H(item:[^|]+)|h")
    if istr then
      local parts = { strsplit(":", istr) }
      add("slot" .. s[1], (parts[2] or "") .. ":" .. (parts[3] or "") .. ":" .. (parts[8] or ""))
      -- The item's own stats and slot type, so the site can compare dungeon items with it
      -- ("Top gear"): st16=str:10,agi:5,wdps:12.4 / loc16=INVTYPE_2HWEAPON.
      local st, list = ns.itemStats(link), {}
      for k, v in pairs(st) do
        if type(v) == "number" and v ~= 0 then list[#list + 1] = k .. ":" .. num(v) end
      end
      table.sort(list)
      add("st" .. s[1], table.concat(list, ","))
      add("loc" .. s[1], select(9, ns.GetItemInfo(link)) or "")
    end
  end
  -- Rating needed for 1% crit / hit on this client, to turn item ratings into percentages.
  local rp = ns.GetRatingPerPct()
  add("rating_crit", num(rp.crit))
  add("rating_hit", num(rp.hit))
  return table.concat(out, "\n")
end
ns.BuildExport = buildExport

refreshers[3] = function()
  box:SetText(buildExport())
  box:HighlightText()
  box:SetFocus()
end

---------------------------------------------------------------------------------------------
-- Page 4: Commands
---------------------------------------------------------------------------------------------
local pCmd = newPage()
local cmdHint = pCmd:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
cmdHint:SetPoint("TOPLEFT", 4, -2)
cmdHint:SetJustifyH("LEFT")
cmdHint:SetText(T.cmd_hint)
local cmdDesc = {}
for i, c in ipairs(T.cmds) do
  local y = -22 - (i - 1) * 35
  local name = pCmd:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
  name:SetPoint("TOPLEFT", 4, y)
  name:SetText("|cff4fd1c5" .. c[2] .. "|r")
  local desc = pCmd:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
  desc:SetPoint("TOPLEFT", 4, y - 16)
  desc:SetWidth(W - 110)
  desc:SetJustifyH("LEFT")
  desc:SetText(c[3])
  cmdDesc[i] = desc
  if c[1] then
    local b = CreateFrame("Button", nil, pCmd, "UIPanelButtonTemplate")
    b:SetSize(70, 20)
    b:SetPoint("TOPRIGHT", -4, y)
    b:SetText(T.run)
    b:SetScript("OnClick", function() SlashCmdList.BROKENMETAWEIGHTS(c[1]) end)
  end
end

refreshers[4] = function()
  local ids = ns.classSpecs()
  for i, c in ipairs(T.cmds) do
    if c[3]:find("%%s") then
      cmdDesc[i]:SetText(c[3]:format(ids[1] or "warrior_fury") .. "\n|cff888888" .. table.concat(ids, ", ") .. "|r")
    end
  end
end

---------------------------------------------------------------------------------------------
-- Page 5: Data (what is collected for the site, sharing switch)
---------------------------------------------------------------------------------------------
local pData = newPage()
local dataTitle = pData:CreateFontString(nil, "OVERLAY", "GameFontNormal")
dataTitle:SetPoint("TOPLEFT", 4, -2)
dataTitle:SetText(T.data_h)
local dataIntro = pData:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
dataIntro:SetPoint("TOPLEFT", 4, -22)
dataIntro:SetWidth(W - 40)
dataIntro:SetJustifyH("LEFT")
dataIntro:SetText(T.data_intro)

local shareBtn = CreateFrame("Button", nil, pData, "UIPanelButtonTemplate")
shareBtn:SetSize(150, 22)
shareBtn:SetPoint("TOPLEFT", 4, -96)
shareBtn:SetScript("OnClick", function()
  SlashCmdList.BROKENMETAWEIGHTS(BrokenMetaWeightsDB.share and "share off" or "share on")
end)
local snapBtn = CreateFrame("Button", nil, pData, "UIPanelButtonTemplate")
snapBtn:SetSize(150, 22)
snapBtn:SetPoint("LEFT", shareBtn, "RIGHT", 8, 0)
snapBtn:SetText(T.snap)
snapBtn:SetScript("OnClick", function() SlashCmdList.BROKENMETAWEIGHTS("snap") end)
local copyBtn = CreateFrame("Button", nil, pData, "UIPanelButtonTemplate")
copyBtn:SetSize(150, 22)
copyBtn:SetPoint("LEFT", snapBtn, "RIGHT", 8, 0)
copyBtn:SetText(T.copy)
copyBtn:SetScript("OnClick", function() if ns.ShowShareCopy then ns.ShowShareCopy() end end)

rows(pData, 10, -130, 18)
for _, row in ipairs(pData.rows) do row[1]:SetWidth(W - 40); row[1]:SetWordWrap(true) end

-- A click here counts as the hardware event full scans require, same as the auction window button.
local scanBtn = CreateFrame("Button", nil, pData, "UIPanelButtonTemplate")
scanBtn:SetSize(370, 22)
scanBtn:SetPoint("TOPLEFT", 4, -330)
scanBtn:SetText(T.scan)
scanBtn:SetScript("OnClick", function() if ns.StartAuctionScan then ns.StartAuctionScan() end end)
local scanHint = pData:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
scanHint:SetPoint("TOPLEFT", scanBtn, "BOTTOMLEFT", 0, -6)
scanHint:SetWidth(W - 40)
scanHint:SetJustifyH("LEFT")

refreshers[5] = function()
  shareBtn:SetText(BrokenMetaWeightsDB.share and ("|cff40ff40" .. T.share_on .. "|r") or T.share_off)
  local open = ns.IsAuctionOpen and ns.IsAuctionOpen()
  if open then scanBtn:Enable() else scanBtn:Disable() end
  scanHint:SetText(open and "" or ("|cff888888" .. T.scan_hint .. "|r"))
  local d = ns.Data()
  local n = { stats = 0, pet = 0, rating = 0 }
  for _, r in ipairs(d.meas) do n[r.k] = (n[r.k] or 0) + 1 end
  local i = 1
  setRow(pData, i, "|cffffd100" .. T.meas .. "|r", string.format(T.meas_detail, #d.meas, n.stats, n.pet, n.rating)); i = i + 2
  setRow(pData, i, "|cffffd100" .. T.ah_h .. "|r"); i = i + 1
  setRow(pData, i, string.format(T.ah_mode, tostring(ns.AuctionMode and ns.AuctionMode() or "-"))); i = i + 1
  local last = d.ah[#d.ah]
  if last then
    local distinct = 0
    for _ in pairs(last.prices) do distinct = distinct + 1 end
    setRow(pData, i, string.format(T.ah_last, date("%d/%m %H:%M", last.t), last.realm or "?", last.faction or "?",
      last.listings or 0, distinct)); i = i + 1
    setRow(pData, i, string.format(T.ah_count, #d.ah)); i = i + 1
  else
    setRow(pData, i, "|cff888888" .. T.ah_none .. "|r"); i = i + 1
  end
  clearRows(pData, i)
end

---------------------------------------------------------------------------------------------
-- Copy dialog: the share string, pre-selected for Ctrl+C
---------------------------------------------------------------------------------------------
local copyFrame = CreateFrame("Frame", "BrokenMetaShareCopy", UIParent, "BasicFrameTemplateWithInset")
copyFrame:SetSize(520, 300)
copyFrame:SetPoint("CENTER", 0, 60)
copyFrame:SetFrameStrata("DIALOG")
copyFrame:SetMovable(true)
copyFrame:EnableMouse(true)
copyFrame:RegisterForDrag("LeftButton")
copyFrame:SetScript("OnDragStart", copyFrame.StartMoving)
copyFrame:SetScript("OnDragStop", copyFrame.StopMovingOrSizing)
copyFrame:Hide()
tinsert(UISpecialFrames, "BrokenMetaShareCopy")
copyFrame.title = copyFrame:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
copyFrame.title:SetPoint("TOP", 0, -5)
copyFrame.title:SetText(T.copy_title)
local copyHint = copyFrame:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
copyHint:SetPoint("TOPLEFT", 14, -32)
copyHint:SetWidth(490)
copyHint:SetJustifyH("LEFT")
local copyScroll = CreateFrame("ScrollFrame", "BrokenMetaShareCopyScroll", copyFrame, "UIPanelScrollFrameTemplate")
copyScroll:SetPoint("TOPLEFT", 14, -70)
copyScroll:SetPoint("BOTTOMRIGHT", -32, 14)
local copyBox = CreateFrame("EditBox", nil, copyScroll)
copyBox:SetMultiLine(true)
copyBox:SetAutoFocus(false)
copyBox:SetMaxLetters(0)
copyBox:SetFontObject(ChatFontNormal)
copyBox:SetWidth(460)
copyBox:SetScript("OnEscapePressed", function() copyFrame:Hide() end)
copyScroll:SetScrollChild(copyBox)

-- Any text to copy (share data, site links): a game addon cannot open a browser.
local importOk = CreateFrame("Button", nil, copyFrame, "UIPanelButtonTemplate")
importOk:SetSize(140, 22)
importOk:SetPoint("BOTTOMRIGHT", -30, 16)
importOk:SetText(T.import_do)
importOk:Hide()
importOk:SetScript("OnClick", function()
  local ok, err = ns.ImportWeights(copyBox:GetText())
  ns.say(ok and ns.L.import_ok or ns.L[err])
  if ok then copyFrame:Hide() end
end)
copyFrame:HookScript("OnHide", function() importOk:Hide() end)

function ns.ShowImportDialog()
  ns.ShowCopyText(T.import_title, T.import_hint, "")
  importOk:Show()
end

function ns.ShowCopyText(title, hint, text)
  importOk:Hide()
  copyFrame.title:SetText(title)
  copyHint:SetText(hint)
  copyBox:SetText(text)
  copyFrame:Show()
  copyBox:SetFocus()
  copyBox:HighlightText()
end

-- Site URL in the player's language (French pages for frFR, English pages otherwise), tagged so
-- Google Analytics shows the traffic the addon brings.
function ns.SiteURL(path, campaign)
  local prefix = GetLocale() == "frFR" and "" or "en/"
  return "https://brokenmeta.gg/" .. prefix .. path .. "?utm_source=addon&utm_medium=ingame&utm_campaign=" .. campaign
end

function ns.ShowShareCopy()
  if not BrokenMetaWeightsDB.share then return ns.say(T.copy_off) end
  local text, nMeas, nScans = ns.BuildShareString()
  if nMeas == 0 and nScans == 0 then return ns.say(T.copy_empty) end
  ns.ShowCopyText(T.copy_title, T.copy_hint, text)
end

---------------------------------------------------------------------------------------------
-- Page 6: Guide (teaser + links to the site; the full guide stays on brokenmeta.gg)
---------------------------------------------------------------------------------------------
local pGuide = newPage()
local gTitle = pGuide:CreateFontString(nil, "OVERLAY", "GameFontNormal")
gTitle:SetPoint("TOPLEFT", 4, -2)
gTitle:SetText(T.guide_h)
local gText = pGuide:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
gText:SetPoint("TOPLEFT", 4, -24)
gText:SetWidth(W - 40)
gText:SetJustifyH("LEFT")
local gMore = pGuide:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
gMore:SetPoint("TOPLEFT", gText, "BOTTOMLEFT", 0, -8)
gMore:SetWidth(W - 40)
gMore:SetJustifyH("LEFT")
local gBtn = CreateFrame("Button", nil, pGuide, "UIPanelButtonTemplate")
gBtn:SetSize(220, 24)
gBtn:SetPoint("TOPLEFT", gMore, "BOTTOMLEFT", 0, -10)
gBtn:SetText(T.guide_copy)
local pTitle = pGuide:CreateFontString(nil, "OVERLAY", "GameFontNormal")
pTitle:SetPoint("TOPLEFT", 4, -190)
pTitle:SetText(T.prof_h)
local profRows = {}
for k = 1, 4 do
  local fs = pGuide:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
  fs:SetPoint("TOPLEFT", 4, -190 - k * 34)
  fs:SetWidth(W - 160)
  fs:SetJustifyH("LEFT")
  local b = CreateFrame("Button", nil, pGuide, "UIPanelButtonTemplate")
  b:SetSize(120, 22)
  b:SetPoint("TOPRIGHT", -4, -186 - k * 34)
  b:SetText(T.prof_copy)
  profRows[k] = { fs = fs, btn = b }
end

-- Learned professions as { line = skillLineID, rank, max }: modern API first, Classic fallback
-- (matched on the localized name against the site's profession names).
local function learnedProfessions()
  local out = {}
  if GetProfessions and GetProfessionInfo then
    for _, idx in ipairs({ GetProfessions() }) do
      local ok, _, _, rank, max, _, _, line = pcall(GetProfessionInfo, idx)
      if ok and line then out[#out + 1] = { line = line, rank = rank or 0, max = max or 0 } end
    end
  elseif GetNumSkillLines and GetSkillLineInfo then
    for i = 1, GetNumSkillLines() do
      local name, header, _, rank, _, _, max = GetSkillLineInfo(i)
      if name and not header then
        for line, p in pairs(ns.PROFESSIONS or {}) do
          if p.name.frFR == name or p.name.enUS == name then out[#out + 1] = { line = line, rank = rank or 0, max = max or 0 } end
        end
      end
    end
  end
  return out
end

refreshers[6] = function()
  local spec = ns.GetSpec()
  local tb = spec and ns.TALENT_BUILDS and ns.TALENT_BUILDS[spec]
  local ranks = ns.readTalents and select(1, ns.readTalents())
  if spec and tb and #tb.core > 0 and ranks then
    local have = 0
    for _, node in ipairs(tb.core) do if (ranks[node] or 0) > 0 then have = have + 1 end end
    gText:SetText("|cffffffff" .. ns.specName(spec) .. "|r : " .. string.format(T.guide_follow, have, #tb.core, tb.level or 20))
    gMore:SetText(T.guide_more)
  else
    gText:SetText(spec and ("|cffffffff" .. ns.specName(spec) .. "|r") or "")
    gMore:SetText(T.guide_nobuild)
  end
  gBtn:SetShown(tb ~= nil)
  gBtn:SetScript("OnClick", function()
    if tb then ns.ShowCopyText(T.link_title, T.link_hint, ns.SiteURL(tb.guide, "guide")) end
  end)

  local profs, k = learnedProfessions(), 0
  for _, pr in ipairs(profs) do
    local route = ns.PROFESSIONS and ns.PROFESSIONS[pr.line]
    if route and k < #profRows then
      k = k + 1
      local pname = route.name[IS_FR and "frFR" or "enUS"] or route.name.enUS
      local text = string.format(T.prof_done, pname, pr.rank, pr.max)
      for _, st in ipairs(route.steps) do
        if pr.rank < st.t then
          local left = st.c
          if pr.rank > st.f then left = math.ceil(st.c * (st.t - pr.rank) / math.max(1, st.t - st.f)) end
          text = string.format(T.prof_next, pname, pr.rank, pr.max, st.name[IS_FR and "frFR" or "enUS"] or st.name.enUS, st.f, st.t, left)
          break
        end
      end
      profRows[k].fs:SetText(text)
      profRows[k].btn:Show()
      profRows[k].btn:SetScript("OnClick", function()
        ns.ShowCopyText(T.link_title, T.link_hint, ns.SiteURL("wow-forever/professions/" .. route.id .. "/", "profession"))
      end)
    end
  end
  if k == 0 then
    profRows[1].fs:SetText("|cff888888" .. T.prof_none .. "|r")
    profRows[1].btn:Hide()
    k = 1
  end
  for j = k + 1, #profRows do profRows[j].fs:SetText(""); profRows[j].btn:Hide() end
end

---------------------------------------------------------------------------------------------
-- Entry points
---------------------------------------------------------------------------------------------
function ns.ToggleHub()
  if hub:IsShown() then hub:Hide() else hub:Show(); showPage(current) end
end

function ns.ShowExport()
  hub:Show(); showPage(3)
end

function ns.OnDataChanged()
  if hub:IsShown() and refreshers[current] then refreshers[current]() end
end
