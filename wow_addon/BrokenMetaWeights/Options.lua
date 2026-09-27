-- Options: a panel in the game's Options > AddOns (and /bmw options). Loaded right after Theme.lua
-- so ns.Option() exists for every other file; the panel itself is built at login.
local ADDON, ns = ...

local T = ns.Localize("options", {
  title = "Broken Meta : Hub", intro = "Réglages de l'addon. Ils s'appliquent tout de suite.",
  tooltip_dps = "Afficher la valeur en DPS dans l'infobulle des objets",
  tooltip_loot = "Afficher où l'objet s'obtient (donjon, boss ou quête)",
  weights_reminder = "Me rappeler de refaire mes poids de stats tous les 5 niveaux",
  announce_reminder = "Me prévenir quand mon annonce d'artisan va expirer",
  request_alert = "Me prévenir quand quelqu'un cherche un objet que je sais fabriquer",
  sounds = "Jouer un son avec ces alertes",
  minimap = "Afficher le bouton autour de la minicarte",
  open = "Ouvrir le hub", tour = "Revoir la visite guidée",
}, {
  title = "Broken Meta : Hub", intro = "Addon settings. They apply right away.",
  tooltip_dps = "Show the DPS value in item tooltips",
  tooltip_loot = "Show where the item comes from (dungeon, boss or quest)",
  weights_reminder = "Remind me to redo my stat weights every 5 levels",
  announce_reminder = "Warn me when my crafter announce is about to expire",
  request_alert = "Tell me when someone looks for an item I can make",
  sounds = "Play a sound with these alerts",
  minimap = "Show the minimap button",
  open = "Open the hub", tour = "Replay the guided tour",
})

local DEFAULTS = { tooltip_dps = true, tooltip_loot = true, weights_reminder = true, announce_reminder = true,
  request_alert = true, sounds = true }
local ORDER = { "tooltip_dps", "tooltip_loot", "weights_reminder", "announce_reminder", "request_alert", "sounds", "minimap" }

-- ns.Option("tooltip_dps") -> true / false (defaults above until the player changes it).
function ns.Option(key)
  if key == "minimap" then return not (BrokenMetaWeightsDB and BrokenMetaWeightsDB.minimapHidden) end
  local opt = BrokenMetaWeightsDB and BrokenMetaWeightsDB.opt
  local v = opt and opt[key]
  if v == nil then return DEFAULTS[key] ~= false end
  return v
end

function ns.SetOption(key, value)
  if key == "minimap" then
    if ns.Option("minimap") ~= value and ns.ToggleMinimap then ns.ToggleMinimap() end
    return
  end
  BrokenMetaWeightsDB = BrokenMetaWeightsDB or {}
  BrokenMetaWeightsDB.opt = BrokenMetaWeightsDB.opt or {}
  BrokenMetaWeightsDB.opt[key] = value and true or false
end

local panel, category, checks = nil, nil, {}

local function refresh()
  for key, c in pairs(checks) do c.mark:SetShown(ns.Option(key)) end
end

local function build()
  panel = CreateFrame("Frame", "BrokenMetaOptionsPanel", UIParent)
  panel.name = T.title
  panel:Hide()
  local title = panel:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
  title:SetPoint("TOPLEFT", 16, -16)
  title:SetText(T.title)
  local intro = panel:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHint")
  intro:SetPoint("TOPLEFT", 16, -44)
  intro:SetText(T.intro)
  for i, key in ipairs(ORDER) do
    local c = ns.Button(panel)
    c:SetSize(18, 18)
    c:SetPoint("TOPLEFT", 16, -74 - (i - 1) * 30)
    c.mark = c:CreateTexture(nil, "OVERLAY")
    c.mark:SetAllPoints()
    c.mark:SetTexture("Interface\\Buttons\\UI-CheckBox-Check")
    local label = panel:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
    label:SetPoint("LEFT", c, "RIGHT", 10, 0)
    label:SetText(T[key])
    c:SetScript("OnClick", function() ns.SetOption(key, not ns.Option(key)); refresh() end)
    checks[key] = c
  end
  local open = ns.Button(panel, nil, "primary")
  open:SetSize(160, 24)
  open:SetPoint("TOPLEFT", 16, -74 - #ORDER * 30 - 12)
  open:SetText(T.open)
  open:SetScript("OnClick", function()
    if SettingsPanel and SettingsPanel:IsShown() and HideUIPanel then HideUIPanel(SettingsPanel) end
    if ns.ToggleHub then ns.ToggleHub() end
  end)
  local tour = ns.Button(panel)
  tour:SetSize(200, 24)
  tour:SetPoint("LEFT", open, "RIGHT", 10, 0)
  tour:SetText(T.tour)
  tour:SetScript("OnClick", function()
    if SettingsPanel and SettingsPanel:IsShown() and HideUIPanel then HideUIPanel(SettingsPanel) end
    if ns.StartTour then ns.StartTour() end
  end)
  panel:SetScript("OnShow", refresh)
  -- Modern Settings UI first, the old Interface Options for older clients.
  if Settings and Settings.RegisterCanvasLayoutCategory and Settings.RegisterAddOnCategory then
    category = Settings.RegisterCanvasLayoutCategory(panel, T.title)
    Settings.RegisterAddOnCategory(category)
  elseif InterfaceOptions_AddCategory then
    InterfaceOptions_AddCategory(panel)
  end
end

function ns.ShowOptions()
  if not panel then return end
  if Settings and Settings.OpenToCategory and category then
    Settings.OpenToCategory(category.GetID and category:GetID() or category.ID)
  elseif InterfaceOptionsFrame_OpenToCategory then
    InterfaceOptionsFrame_OpenToCategory(panel)
    InterfaceOptionsFrame_OpenToCategory(panel) -- the old frame needs it twice to scroll to the addon
  end
end

local ev = CreateFrame("Frame")
ev:RegisterEvent("PLAYER_LOGIN")
ev:SetScript("OnEvent", function() pcall(build) end)
ns.OptionsTexts = T
