-- Guided tour: shown the first time the hub opens (then /bmw tour or the Options panel). A small
-- card next to the hub walks through the sections and opens the matching tabs.
local ADDON, ns = ...

local T = ns.Localize("tour", {
  next = "Suivant", prev = "Précédent", done = "C'est parti !", skip = "Passer",
  steps = {
    { "Bienvenue dans Broken Meta : HUB", "Le HUB réunit les addons Broken Meta pour WoW: Forever. L'accueil liste ceux que tu as ; ceux qui manquent sont grisés et disponibles sur CurseForge. Ouvre cette fenêtre avec le bouton à la spirale autour de la minicarte ou avec /bmw." },
    { "BrokenDPS", "Survole n'importe quel objet : son infobulle affiche sa valeur en DPS pour ta spé. Onglets Personnage, Améliorations (par donjon), BiS et Guide de ta classe sur brokenmeta.gg." },
    { "BrokenCrafter", "Trouve un artisan disponible sur ton royaume et écris-lui, monte tes métiers au meilleur prix, et suis la valeur de tes objets à l'hôtel des ventes (section Économie)." },
    { "BrokenCodex", "Le codex des donjons et des raids : butin de chaque boss, techniques des boss, conditions d'accès et historique de ton butin." },
    { "Réglages", "Tout se règle dans Options > AddOns > Broken Meta : HUB, ou avec /bmw options. Bon jeu !" },
  },
}, {
  next = "Next", prev = "Back", done = "Let's go!", skip = "Skip",
  steps = {
    { "Welcome to Broken Meta : HUB", "The HUB gathers the Broken Meta addons for WoW: Forever. Home lists the ones you have; missing ones are greyed out and available on CurseForge. Open this window with the spiral button around the minimap or with /bmw." },
    { "BrokenDPS", "Hover any item: its tooltip shows its DPS value for your spec. Tabs: Character, Upgrades (per dungeon), BiS and your class Guide on brokenmeta.gg." },
    { "BrokenCrafter", "Find an available crafter on your realm and whisper them, level your professions at the best price, and track what your items are worth at the auction house (Economy section)." },
    { "BrokenCodex", "The dungeon and raid codex: each boss's loot, boss abilities, attunements and your loot history." },
    { "Settings", "Everything is in Options > AddOns > Broken Meta : HUB, or with /bmw options. Have fun!" },
  },
})

-- Which hub page each step opens (nil: leave it as is).
local function openFor(step)
  local key = ({ [1] = "home", [2] = "dps", [3] = "prof", [4] = "codex" })[step]
  if key and ns.HubOpenSection then ns.HubOpenSection(key) end
end

local card, step
local function build()
  card = CreateFrame("Frame", "BrokenMetaTour", UIParent, ns.BACKDROP_TEMPLATE)
  card:SetSize(320, 190)
  card:SetFrameStrata("DIALOG")
  ns.Flat(card, ns.C.bg, ns.C.teal)
  card.title = card:CreateFontString(nil, "OVERLAY", "BrokenMetaFontHeading")
  card.title:SetPoint("TOPLEFT", 14, -12)
  card.title:SetWidth(292)
  card.title:SetJustifyH("LEFT")
  card.text = card:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBodySmall")
  card.text:SetPoint("TOPLEFT", card.title, "BOTTOMLEFT", 0, -8)
  card.text:SetWidth(292)
  card.text:SetJustifyH("LEFT")
  card.count = card:CreateFontString(nil, "OVERLAY", "BrokenMetaFontMono")
  card.count:SetPoint("BOTTOMLEFT", 14, 14)
  card.nextBtn = ns.Button(card, nil, "primary")
  card.nextBtn:SetSize(100, 22)
  card.nextBtn:SetPoint("BOTTOMRIGHT", -12, 10)
  card.prevBtn = ns.Button(card)
  card.prevBtn:SetSize(90, 22)
  card.prevBtn:SetPoint("RIGHT", card.nextBtn, "LEFT", -6, 0)
  card.prevBtn:SetText(T.prev)
  card.skip = ns.Button(card)
  card.skip:SetSize(70, 20)
  card.skip:SetPoint("TOPRIGHT", -8, -8)
  card.skip:SetText(T.skip)
  local function finish()
    card:Hide()
    BrokenMetaWeightsDB = BrokenMetaWeightsDB or {}
    BrokenMetaWeightsDB.tourDone = true
  end
  card.skip:SetScript("OnClick", finish)
  card.prevBtn:SetScript("OnClick", function() ns.TourStep(step - 1) end)
  card.nextBtn:SetScript("OnClick", function()
    if step >= #T.steps then finish() else ns.TourStep(step + 1) end
  end)
end

function ns.TourStep(n)
  if not card then build() end
  step = math.max(1, math.min(n, #T.steps))
  local s = T.steps[step]
  card.title:SetText(s[1])
  card.text:SetText(s[2])
  card.count:SetText(step .. " / " .. #T.steps)
  card.nextBtn:SetText(step >= #T.steps and T.done or T.next)
  card.prevBtn:SetShown(step > 1)
  local hub = _G.BrokenMetaHub
  card:ClearAllPoints()
  if hub and hub:IsShown() then card:SetPoint("BOTTOMRIGHT", hub, "BOTTOMRIGHT", -16, 16) else card:SetPoint("CENTER") end -- inside the wide window
  card:Show()
  openFor(step)
end

function ns.StartTour()
  local hub = _G.BrokenMetaHub
  if hub and not hub:IsShown() and ns.ToggleHub then ns.ToggleHub() end
  ns.TourStep(1)
end

-- The card goes away with the hub.
if _G.BrokenMetaHub then _G.BrokenMetaHub:HookScript("OnHide", function() if card then card:Hide() end end) end

-- First time the hub opens: start the tour.
if ns.ToggleHub then
  local toggle = ns.ToggleHub
  ns.ToggleHub = function(...)
    toggle(...)
    local hub = _G.BrokenMetaHub
    if hub and hub:IsShown() and not (BrokenMetaWeightsDB and BrokenMetaWeightsDB.tourDone) and not (card and card:IsShown()) then
      ns.TourStep(1)
    end
  end
end
