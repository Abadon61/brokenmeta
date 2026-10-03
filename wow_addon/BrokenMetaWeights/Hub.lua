-- Broken Meta : HUB window (/bmw): Character (spec, weights, equipped gear value), Upgrades (bag
-- items worth more than what's equipped) and Export (a text string to paste on brokenmeta.gg).
local ADDON, ns = ...
local IS_FR = ns.IS_FR

local T = ns.Localize("hub", {
  reload = "Recharger pour appliquer", lang_tip = "Langue de l'addon (AUTO = celle du jeu). Clique pour changer.",
  title = "Broken Meta : HUB", sec_dps = "DPS", sec_prof = "Profession", sec_eco = "Économie", sec_dg = "Donjons",
  sec_home = "Accueil", sec_codex = "Codex", tab_addons = "Addons",
  home_intro = "Broken Meta : HUB v%s réunit les addons Broken Meta pour WoW: Forever. Installe ceux qui t'intéressent : chacun ajoute sa section dans cette fenêtre, et ils fonctionnent les uns sans les autres.",
  mod_dps = "La valeur en DPS de chaque objet pour ta spé, tes poids de stats, tes améliorations, l'équipement idéal et le guide de ta classe.",
  mod_crafter = "L'annuaire des artisans, leurs recettes, les demandes, la montée de métier au meilleur prix et l'économie de l'hôtel des ventes.",
  mod_codex = "Le codex des donjons et des raids : les boss, leurs techniques, le butin de chaque boss et l'historique de ton butin.",
  mod_loaded = "installé · v%s", mod_disabled = "désactivé", mod_missing = "non installé",
  mod_open = "Ouvrir", mod_link = "Lien CurseForge", mod_link_title = "Lien CurseForge",
  mod_enable_hint = "Active-le dans la liste des AddOns (écran de choix du personnage), puis recharge l'interface.",
  mod_curseforge = "Disponible gratuitement sur CurseForge (application CurseForge ou fichier .zip).",
  tab_char = "Personnage", tab_up = "Améliorations", tab_bis = "Meilleur équipement", tab_export = "Export", tab_cmd = "Commandes", tab_data = "Données",
  tab_guide = "Guide",
  up_bags = "Dans tes sacs", up_dungeons = "Dans les donjons (meilleur objet par emplacement)",
  up_best = "Donjon le plus rentable : %s (%d amélioration(s), +%.2f DPS)", up_level = "niv. %d",
  no_dungeon = "Aucune amélioration trouvée dans les donjons pour ton niveau.",
  up_pick = "Donjon : %s", up_top = "le plus rentable", up_none_in = "Aucune amélioration dans ce donjon pour ton niveau et ta spé.",
  up_summary = "%d emplacement(s) amélioré(s), +%.2f DPS au total. Clique sur le donjon pour en choisir un autre.", up_quest = "récompense de quête",
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
  ah_h = "Hôtel des ventes", ah_none = "Aucun scan. Ouvre l'hôtel des ventes, puis Profession > Montée > « Scanner l'hôtel des ventes ».",
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
    { "craft", "/bmw craft", "Ouvre l'annuaire des artisans connectés (Broken Meta : Profession)." },
    { "options", "/bmw options", "Ouvre les réglages de l'addon (aussi dans Options > AddOns)." },
    { "tour", "/bmw tour", "Relance la visite guidée." },
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
  reload = "Reload to apply", lang_tip = "Addon language (AUTO = the game's). Click to change.",
  title = "Broken Meta : HUB", sec_dps = "DPS", sec_prof = "Professions", sec_eco = "Economy", sec_dg = "Dungeons",
  sec_home = "Home", sec_codex = "Codex", tab_addons = "Addons",
  home_intro = "Broken Meta : HUB v%s brings together the Broken Meta addons for WoW: Forever. Install the ones you want: each adds its section to this window, and they work without one another.",
  mod_dps = "Every item's DPS value for your spec, your stat weights, your upgrades, the best-in-slot gear and your class guide.",
  mod_crafter = "The crafters directory, their recipes, requests, profession leveling at the best price and the auction house economy.",
  mod_codex = "The dungeon and raid codex: bosses, their abilities, each boss's loot and your loot history.",
  mod_loaded = "installed · v%s", mod_disabled = "disabled", mod_missing = "not installed",
  mod_open = "Open", mod_link = "CurseForge link", mod_link_title = "CurseForge link",
  mod_enable_hint = "Enable it in the AddOns list (character selection screen), then reload the interface.",
  mod_curseforge = "Free on CurseForge (CurseForge app or .zip file).",
  tab_char = "Character", tab_up = "Upgrades", tab_bis = "Best in slot", tab_export = "Export", tab_cmd = "Commands", tab_data = "Data",
  tab_guide = "Guide",
  up_bags = "In your bags", up_dungeons = "In dungeons (best item per slot)",
  up_best = "Most rewarding dungeon: %s (%d upgrade(s), +%.2f DPS)", up_level = "lvl %d",
  no_dungeon = "No dungeon upgrade found for your level.",
  up_pick = "Dungeon: %s", up_top = "most rewarding", up_none_in = "No upgrade in this dungeon for your level and spec.",
  up_summary = "%d slot(s) improved, +%.2f DPS in total. Click the dungeon to pick another one.", up_quest = "quest reward",
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
  ah_h = "Auction house", ah_none = "No scan yet. Open the auction house, then Professions > Leveling > \"Scan the auction house\".",
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
    { "craft", "/bmw craft", "Opens the directory of online crafters (Broken Meta : Professions)." },
    { "options", "/bmw options", "Opens the addon settings (also in Options > AddOns)." },
    { "tour", "/bmw tour", "Replays the guided tour." },
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


ns.HubTexts = T -- the DPS pages (BrokenDPS) use these texts too

---------------------------------------------------------------------------------------------
-- Frame
---------------------------------------------------------------------------------------------
-- W: width of the area the pages fill (every page lays itself out from ns.Hub.W); the left column adds NAV.
local W, H, NAV = 866, 700, 214
local hub = ns.Window("BrokenMetaHub", W + NAV, H, "Broken Meta : HUB") -- Escape closes it
-- A smaller screen (or UI scale) than the window: scale it down to fit.
hub:HookScript("OnShow", function(self)
  local sw, sh = UIParent:GetWidth() or 0, UIParent:GetHeight() or 0
  local fit = (sw > 0 and sh > 0) and math.min(1, (sw - 40) / (W + NAV), (sh - 40) / H) or 1
  self:SetScale(math.max(fit, 0.5))
end)

-- Addon language, right in the header (also in the Options panel): cycles Auto / FR / EN / DE / ES;
-- the texts are built at load, so the choice applies after the reload button (see Locales.lua).
local LANG_CODES = { "auto", "frFR", "enUS", "deDE", "esES" }
local LANG_SHORT = { auto = "AUTO", frFR = "FR", enUS = "EN", deDE = "DE", esES = "ES" }
local langBtn = ns.Button(hub)
langBtn:SetSize(58, 20)
langBtn:SetPoint("TOPRIGHT", -38, -7)
local reloadBtn = ns.Button(hub, nil, "primary")
reloadBtn:SetSize(150, 20)
reloadBtn:SetPoint("RIGHT", langBtn, "LEFT", -6, 0)
reloadBtn:SetText(T.reload)
reloadBtn:SetScript("OnClick", function() if ReloadUI then ReloadUI() end end)
local function showLang()
  local choice = ns.GetLanguageChoice and ns.GetLanguageChoice() or "auto"
  langBtn:SetText(LANG_SHORT[choice] or choice)
  local wanted = choice == "auto" and ns.CLIENT_LOCALE or choice
  reloadBtn:SetShown(wanted ~= ns.LOCALE)
end
langBtn:SetScript("OnClick", function()
  local choice = ns.GetLanguageChoice and ns.GetLanguageChoice() or "auto"
  local k = 1
  for i, c in ipairs(LANG_CODES) do if c == choice then k = i end end
  if ns.SetLanguage then ns.SetLanguage(LANG_CODES[k % #LANG_CODES + 1]) end
  showLang()
  if ns.ShowLanguageOption then ns.ShowLanguageOption() end
end)
langBtn:HookScript("OnEnter", function(self)
  GameTooltip:SetOwner(self, "ANCHOR_BOTTOM")
  GameTooltip:SetText(T.lang_tip)
  GameTooltip:Show()
end)
langBtn:HookScript("OnLeave", function() GameTooltip:Hide() end)
hub:HookScript("OnShow", showLang)
showLang()

-- Left column (NAV px): the addons of the suite, logo and name; the open addon lists its tabs under
-- it, grouped by section when it has several. The pages fill the rest of the window.
local nav = CreateFrame("Frame", nil, hub)
nav:SetPoint("TOPLEFT", 1, -ns.HEADER_H - 1)
nav:SetPoint("BOTTOMLEFT", 1, 1)
nav:SetWidth(NAV - 1)
local navBg = nav:CreateTexture(nil, "BACKGROUND")
navBg:SetAllPoints()
navBg:SetColorTexture(0.03, 0.035, 0.06, 0.85)
local navLine = ns.Line(hub)
navLine:SetColorTexture(unpack(ns.C.border))
navLine:SetWidth(1)
navLine:SetPoint("TOPLEFT", NAV, -ns.HEADER_H - 1)
navLine:SetPoint("BOTTOMLEFT", NAV, 1)

local PAGE_TOP = ns.HEADER_H + 12
local pages, tabs = {}, {}
local function newPage()
  local p = CreateFrame("Frame", nil, hub)
  p:SetPoint("TOPLEFT", NAV + 12, -PAGE_TOP)
  p:SetPoint("BOTTOMRIGHT", -12, 12)
  p:Hide()
  pages[#pages + 1] = p
  return p
end

local current = 1
local refreshers = {}

-- An addon declares a section with ns.HubSection(key, label, order, addon) and adds tabs to it
-- with ns.HubTab; the tab buttons (ns.HubTabButton) are the rows of the left column.
ns.HUB_ADDONS = {
  HUB = { name = "HUB", order = 0, icon = ns.MEDIA .. "icon" },
  BrokenDPS = { name = "BrokenDPS", order = 10, icon = ns.MEDIA .. "icon_dps" },
  BrokenCrafter = { name = "BrokenCrafter", order = 20, icon = ns.MEDIA .. "icon_crafter" },
  BrokenCodex = { name = "BrokenCodex", order = 40, icon = ns.MEDIA .. "icon_codex" },
}
local sectionOf, sectionLabels, sectionList, sectionAddon, sectionTabs = {}, {}, {}, {}, {}
local addonBtns, addonLast = {}, {}
local lastTab = {} -- last page opened in each section

local function sectionsOf(addon)
  local out = {}
  for _, sec in ipairs(sectionList) do if sectionAddon[sec.key] == addon then out[#out + 1] = sec end end
  return out
end

local function addonIds()
  local ids = {}
  for id in pairs(addonBtns) do ids[#ids + 1] = id end
  table.sort(ids, function(a, b) return ns.HUB_ADDONS[a].order < ns.HUB_ADDONS[b].order end)
  return ids
end

-- Places the rows of the left column: every addon, and under the open one its sections and tabs.
local function layoutNav(active, openIndex)
  for _, b in pairs(tabs) do b:Hide() end
  for _, fs in pairs(sectionLabels) do fs:Hide() end
  local y = -10
  for _, id in ipairs(addonIds()) do
    local b = addonBtns[id]
    b:ClearAllPoints()
    b:SetPoint("TOPLEFT", 8, y)
    y = y - 36
    if id == active then b:LockHighlight() else b:UnlockHighlight() end
    if id == active then
      local secs = sectionsOf(id)
      for _, sec in ipairs(secs) do
        if #secs > 1 and sectionLabels[sec.key] then
          sectionLabels[sec.key]:ClearAllPoints()
          sectionLabels[sec.key]:SetPoint("TOPLEFT", 20, y - 4)
          sectionLabels[sec.key]:Show()
          y = y - 22
        end
        for _, index in ipairs(sectionTabs[sec.key] or {}) do
          local t = tabs[index]
          t:ClearAllPoints()
          t:SetPoint("TOPLEFT", 22, y)
          t:Show()
          if index == openIndex then t:LockHighlight() else t:UnlockHighlight() end
          y = y - 28
        end
      end
      y = y - 6
    end
  end
end

local function showPage(i)
  current = i
  local sec = sectionOf[i]
  local addon = sectionAddon[sec]
  addonLast[addon] = sec
  for j, p in ipairs(pages) do p:SetShown(j == i) end
  layoutNav(addon, i)
  if refreshers[i] then refreshers[i]() end
end

local function addTab(section, label, index)
  sectionOf[index] = section
  sectionTabs[section] = sectionTabs[section] or {}
  table.insert(sectionTabs[section], index)
  lastTab[section] = lastTab[section] or index
  local b = ns.Button(nav, nil, "pill")
  b:SetSize(NAV - 1 - 30, 26)
  b:SetText(label)
  local fs = b.GetFontString and b:GetFontString()
  if fs then fs:ClearAllPoints(); fs:SetPoint("LEFT", 12, 0); fs:SetJustifyH("LEFT") end
  b:SetScript("OnClick", function() lastTab[section] = index; showPage(index) end)
  b:Hide()
  tabs[index] = b
end

local function addonButton(id)
  if addonBtns[id] then return end
  local info = ns.HUB_ADDONS[id] or { name = id, order = 90 }
  ns.HUB_ADDONS[id] = info
  local b = ns.Button(nav, nil, "pill")
  b:SetSize(NAV - 1 - 16, 32)
  b:SetText(info.name)
  local fs = b.GetFontString and b:GetFontString()
  if fs then fs:ClearAllPoints(); fs:SetPoint("LEFT", 40, 0); fs:SetJustifyH("LEFT") end
  b.logo = b:CreateTexture(nil, "ARTWORK")
  b.logo:SetSize(22, 22)
  b.logo:SetPoint("LEFT", 10, 0)
  if info.icon then b.logo:SetTexture(info.icon) end
  b:SetScript("OnClick", function()
    local sec = addonLast[id]
    if not sec then local first = sectionsOf(id)[1]; sec = first and first.key end
    if sec and lastTab[sec] then showPage(lastTab[sec]) end
  end)
  addonBtns[id] = b
end

function ns.HubSection(key, label, order, addon)
  if sectionLabels[key] then return end
  addon = addon or "HUB"
  addonButton(addon)
  local fs = nav:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  fs:SetText(label)
  fs:Hide()
  sectionLabels[key] = fs
  sectionAddon[key] = addon
  sectionList[#sectionList + 1] = { key = key, order = order or 50 }
  table.sort(sectionList, function(a, b2) return a.order < b2.order end)
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
    local l = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
    l:SetPoint("TOPLEFT", withIcon and (lineH + 6) or 4, y)
    l:SetWidth(W - 150)
    l:SetJustifyH("LEFT")
    l:SetWordWrap(false)
    local r = page:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
    r:SetPoint("TOPRIGHT", -4, y)
    r:SetJustifyH("RIGHT")
    local row = { l, r, icon = icon }
    local hover = CreateFrame("Button", nil, page)
    hover:SetPoint("TOPLEFT", 0, y + 2)
    hover:SetSize(W - 24, lineH)
    -- Highlight in the page's own background layer: under the row's texts.
    local hl = page:CreateTexture(nil, "BACKGROUND")
    hl:SetColorTexture(unpack(ns.C.rowHover))
    hl:SetPoint("TOPLEFT", 0, y + 2)
    hl:SetSize(W - 24, lineH)
    hl:Hide()
    hover:SetScript("OnEnter", function(self)
      if not row.slot and not row.link then return end
      hl:Show()
      GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
      if row.slot then GameTooltip:SetInventoryItem("player", row.slot) else GameTooltip:SetHyperlink(row.link) end
      GameTooltip:Show()
    end)
    hover:SetScript("OnLeave", function() hl:Hide(); GameTooltip:Hide() end)
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

-- Building blocks for the pages every addon of the suite adds.
ns.Hub = { W = W, rows = rows, setRow = setRow, clearRows = clearRows }
function ns.HubTab(section, label, refresher)
  local page = newPage()
  addTab(section, label, #pages)
  refreshers[#pages] = refresher
  return page, #pages
end
function ns.HubShow(index) hub:Show(); showPage(index) end
function ns.HubTabButton(index) return tabs[index] end
function ns.HubRefresh(index) if hub:IsShown() and current == index and refreshers[index] then refreshers[index]() end end

-- Home: the addons of the suite, the data shared with the site, the commands.
ns.HubSection("home", T.sec_home, 0, "HUB")
local pHome, iHome = ns.HubTab("home", T.tab_addons)
local pData, iData = ns.HubTab("home", T.tab_data)
local pCmd, iCmd = ns.HubTab("home", T.tab_cmd)
ns.HubHomePage, ns.HubHomeIndex = pHome, iHome

local function fmtDelta(d)
  if d > 0.005 then return string.format("|cff2de6c4+%.2f|r", d) end
  if d < -0.005 then return string.format("|cffff5a6b%.2f|r", d) end
  return "|cffa2a6bd0.00|r"
end

---------------------------------------------------------------------------------------------
-- Page 4: Commands
---------------------------------------------------------------------------------------------
local cmdHint = pCmd:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
cmdHint:SetPoint("TOPLEFT", 4, -2)
cmdHint:SetJustifyH("LEFT")
cmdHint:SetText(T.cmd_hint)
local cmdDesc = {}
for i, c in ipairs(T.cmds) do
  local y = -22 - (i - 1) * 32
  local name = pCmd:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  name:SetPoint("TOPLEFT", 4, y)
  name:SetText("|cff2de6c4" .. c[2] .. "|r")
  local desc = pCmd:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  desc:SetPoint("TOPLEFT", 4, y - 16)
  desc:SetWidth(W - 110)
  desc:SetJustifyH("LEFT")
  desc:SetText(c[3])
  cmdDesc[i] = desc
  if c[1] then
    local b = ns.Button(pCmd)
    b:SetSize(70, 20)
    b:SetPoint("TOPRIGHT", -4, y)
    b:SetText(T.run)
    b:SetScript("OnClick", function() SlashCmdList.BROKENMETAWEIGHTS(c[1]) end)
  end
end

refreshers[iCmd] = function()
  local ids = ns.classSpecs and ns.classSpecs() or {}
  for i, c in ipairs(T.cmds) do
    if c[3]:find("%%s") then
      cmdDesc[i]:SetText(c[3]:format(ids[1] or "warrior_fury") .. "\n|cff7a7e96" .. table.concat(ids, ", ") .. "|r")
    end
  end
end

---------------------------------------------------------------------------------------------
-- Page 5: Data (what is collected for the site, sharing switch)
---------------------------------------------------------------------------------------------
local dataTitle = pData:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
dataTitle:SetPoint("TOPLEFT", 4, -2)
dataTitle:SetText(T.data_h)
local dataIntro = pData:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
dataIntro:SetPoint("TOPLEFT", 4, -22)
dataIntro:SetWidth(W - 40)
dataIntro:SetJustifyH("LEFT")
dataIntro:SetText(T.data_intro)

local shareBtn = ns.Button(pData)
shareBtn:SetSize(150, 22)
shareBtn:SetPoint("TOPLEFT", 4, -96)
shareBtn:SetScript("OnClick", function()
  SlashCmdList.BROKENMETAWEIGHTS(BrokenMetaWeightsDB.share and "share off" or "share on")
end)
local snapBtn = ns.Button(pData)
snapBtn:SetSize(150, 22)
snapBtn:SetPoint("LEFT", shareBtn, "RIGHT", 8, 0)
snapBtn:SetText(T.snap)
snapBtn:SetScript("OnClick", function() SlashCmdList.BROKENMETAWEIGHTS("snap") end)
local copyBtn = ns.Button(pData)
copyBtn:SetSize(150, 22)
copyBtn:SetPoint("LEFT", snapBtn, "RIGHT", 8, 0)
copyBtn:SetText(T.copy)
copyBtn:SetScript("OnClick", function() if ns.ShowShareCopy then ns.ShowShareCopy() end end)

rows(pData, 10, -130, 18)
for _, row in ipairs(pData.rows) do row[1]:SetWidth(W - 40); row[1]:SetWordWrap(true) end

-- The scan button itself is in Profession > Leveling, next to the prices it feeds.

refreshers[iData] = function()
  shareBtn:SetText(BrokenMetaWeightsDB.share and ("|cff2de6c4" .. T.share_on .. "|r") or T.share_off)
  local d = ns.Data()
  local n = { stats = 0, pet = 0, rating = 0 }
  for _, r in ipairs(d.meas) do n[r.k] = (n[r.k] or 0) + 1 end
  local i = 1
  setRow(pData, i, "|cffffc23c" .. T.meas .. "|r", string.format(T.meas_detail, #d.meas, n.stats, n.pet, n.rating)); i = i + 2
  setRow(pData, i, "|cffffc23c" .. T.ah_h .. "|r"); i = i + 1
  setRow(pData, i, string.format(T.ah_mode, tostring(ns.AuctionMode and ns.AuctionMode() or "-"))); i = i + 1
  local last = d.ah[#d.ah]
  if last then
    local distinct = 0
    for _ in pairs(last.prices) do distinct = distinct + 1 end
    setRow(pData, i, string.format(T.ah_last, date("%d/%m %H:%M", last.t), last.realm or "?", last.faction or "?",
      last.listings or 0, distinct)); i = i + 1
    setRow(pData, i, string.format(T.ah_count, #d.ah)); i = i + 1
  else
    setRow(pData, i, "|cff7a7e96" .. T.ah_none .. "|r"); i = i + 1
  end
  clearRows(pData, i)
end

---------------------------------------------------------------------------------------------
-- Copy dialog: the share string, pre-selected for Ctrl+C
---------------------------------------------------------------------------------------------
local copyFrame = ns.Window("BrokenMetaShareCopy", 520, 300, T.copy_title, "DIALOG")
copyFrame:ClearAllPoints()
copyFrame:SetPoint("CENTER", 0, 60)
local copyHint = copyFrame:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
copyHint:SetPoint("TOPLEFT", 14, -42)
copyHint:SetWidth(490)
copyHint:SetJustifyH("LEFT")
local copyScroll = CreateFrame("ScrollFrame", "BrokenMetaShareCopyScroll", copyFrame, "UIPanelScrollFrameTemplate")
copyScroll:SetPoint("TOPLEFT", 14, -80)
copyScroll:SetPoint("BOTTOMRIGHT", -32, 14)
local copyBox = CreateFrame("EditBox", nil, copyScroll)
copyBox:SetMultiLine(true)
copyBox:SetAutoFocus(false)
copyBox:SetMaxLetters(0)
copyBox:SetFontObject("BrokenMetaFontMono")
copyBox:SetWidth(460)
copyBox:SetScript("OnEscapePressed", function() copyFrame:Hide() end)
copyScroll:SetScrollChild(copyBox)

-- Any text to copy (share data, site links): a game addon cannot open a browser.
local importOk = ns.Button(copyFrame, nil, "primary")
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
  local prefix = ns.IS_FR and "" or "en/"
  return "https://brokenmeta.gg/" .. prefix .. path .. "?utm_source=addon&utm_medium=ingame&utm_campaign=" .. campaign
end

function ns.ShowShareCopy()
  if not BrokenMetaWeightsDB.share then return ns.say(T.copy_off) end
  local text, nMeas, nScans = ns.BuildShareString()
  if nMeas == 0 and nScans == 0 then return ns.say(T.copy_empty) end
  ns.ShowCopyText(T.copy_title, T.copy_hint, text)
end

---------------------------------------------------------------------------------------------
-- Entry points
---------------------------------------------------------------------------------------------

function ns.ToggleHub()
  if hub:IsShown() then hub:Hide() else hub:Show(); showPage(current) end
end


function ns.OnDataChanged()
  if hub:IsShown() and refreshers[current] then refreshers[current]() end
end

---------------------------------------------------------------------------------------------
-- Home > Addons: the suite, each addon installed (open it), disabled, or missing (CurseForge)
---------------------------------------------------------------------------------------------
local CURSEFORGE = "https://www.curseforge.com/wow/addons/"
-- Each addon's own logo, shipped in the HUB's own Media folder so the home cards show it whether
-- or not that addon is actually installed (the missing ones advertise what they look like too).
ns.SUITE = {
  { id = "BrokenDPS", section = "dps", slug = "brokendps", desc = T.mod_dps, icon = ns.MEDIA .. "icon_dps" },
  { id = "BrokenCrafter", section = "prof", slug = "brokencrafter", desc = T.mod_crafter, icon = ns.MEDIA .. "icon_crafter" },
  { id = "BrokenCodex", section = "codex", slug = "brokencodex", desc = T.mod_codex, icon = ns.MEDIA .. "icon_codex" },
}

local function metadata(name, field)
  local get = (C_AddOns and C_AddOns.GetAddOnMetadata) or GetAddOnMetadata
  local ok, v = pcall(get or function() end, name, field)
  return ok and v or nil
end

-- "loaded", "disabled" (installed, not enabled) or "missing".
function ns.AddonState(name)
  if ns.Modules[name] then return "loaded" end
  local isLoaded = (C_AddOns and C_AddOns.IsAddOnLoaded) or IsAddOnLoaded
  if isLoaded then
    local ok, loaded = pcall(isLoaded, name)
    if ok and loaded then return "loaded" end
  end
  local info = (C_AddOns and C_AddOns.GetAddOnInfo) or GetAddOnInfo
  if info then
    local ok, _, title, _, _, reason = pcall(info, name)
    if ok and title and reason ~= "MISSING" then return "disabled" end
  end
  return "missing"
end

function ns.HubOpenSection(key)
  if lastTab[key] then hub:Show(); showPage(lastTab[key]) end
end

local homeIntro = pHome:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
homeIntro:SetPoint("TOPLEFT", 4, -2)
homeIntro:SetWidth(W - 40)
homeIntro:SetJustifyH("LEFT")
local homeCards = {}
for k, m in ipairs(ns.SUITE) do
  local c = CreateFrame("Frame", nil, pHome, ns.BACKDROP_TEMPLATE)
  c:SetSize(W - 32, 104)
  c:SetPoint("TOPLEFT", 4, -40 - (k - 1) * 114)
  ns.Flat(c)
  c.icon = c:CreateTexture(nil, "ARTWORK")
  c.icon:SetSize(40, 40)
  c.icon:SetPoint("TOPLEFT", 12, -12)
  c.icon:SetTexture(m.icon)
  c.name = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
  c.name:SetPoint("TOPLEFT", c.icon, "TOPRIGHT", 12, 0)
  c.name:SetText(m.id)
  c.status = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  c.status:SetPoint("LEFT", c.name, "RIGHT", 10, 0)
  c.desc = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  c.desc:SetPoint("TOPLEFT", c.name, "BOTTOMLEFT", 0, -6)
  c.desc:SetWidth(W - 230)
  c.desc:SetJustifyH("LEFT")
  c.desc:SetText(m.desc)
  c.note = c:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  c.note:SetPoint("BOTTOMLEFT", 64, 10)
  c.note:SetWidth(W - 230)
  c.note:SetJustifyH("LEFT")
  c.btn = ns.Button(c, nil, "primary")
  c.btn:SetSize(140, 24)
  c.btn:SetPoint("RIGHT", -12, 0)
  homeCards[k] = c
end

refreshers[iHome] = function()
  homeIntro:SetText(string.format(T.home_intro, metadata(ADDON, "Version") or "?"))
  for k, m in ipairs(ns.SUITE) do
    local c, state = homeCards[k], ns.AddonState(m.id)
    local url = CURSEFORGE .. m.slug
    c:SetAlpha(state == "missing" and 0.55 or 1)
    c.icon:SetDesaturated(state ~= "loaded")
    ns.FlatBorder(c, state == "loaded" and ns.C.teal or ns.C.border)
    if state == "loaded" then
      c.status:SetText("|c" .. ns.HEX.teal .. string.format(T.mod_loaded, metadata(m.id, "Version") or "?") .. "|r")
      c.note:SetText("")
      c.btn:SetText(T.mod_open)
      c.btn:SetScript("OnClick", function() ns.HubOpenSection(m.section) end)
    elseif state == "disabled" then
      c.status:SetText("|c" .. ns.HEX.gold .. T.mod_disabled .. "|r")
      c.note:SetText(T.mod_enable_hint)
      c.btn:SetText(T.mod_link)
      c.btn:SetScript("OnClick", function() ns.ShowCopyText(T.mod_link_title, T.link_hint, url) end)
    else
      c.status:SetText("|c" .. ns.HEX.faint .. T.mod_missing .. "|r")
      c.note:SetText(T.mod_curseforge)
      c.btn:SetText(T.mod_link)
      c.btn:SetScript("OnClick", function() ns.ShowCopyText(T.mod_link_title, T.link_hint, url) end)
    end
  end
end
