-- Guided tour: shown the first time the hub opens (then /bmw tour or the Options panel). A small
-- card next to the hub walks through the sections and opens the matching tabs.
local ADDON, ns = ...

local T = ns.Localize("tour", {
  next = "Suivant", prev = "Précédent", done = "C'est parti !", skip = "Passer",
  steps = {
    { "Bienvenue dans Broken Meta : Hub", "Quatre outils dans une seule fenêtre : DPS pour ton équipement, Profession pour l'artisanat, Économie pour la valeur de tes objets et les bonnes affaires, Donjons pour le butin de chaque boss. Tu peux ouvrir cette fenêtre avec le bouton à la spirale autour de la minicarte ou avec /bmw." },
    { "Broken Meta : DPS", "Survole n'importe quel objet : son infobulle affiche sa valeur en DPS pour ta spé, comparée à ce que tu portes. L'onglet Améliorations liste les meilleurs objets de tes sacs et des donjons de ton niveau." },
    { "Broken Meta : Profession", "Trouve un artisan disponible sur tout ton royaume, consulte ses recettes et écris-lui. Tu cherches un objet ? Publie une demande. Tu es artisan ? Mets-toi disponible dans Mon profil." },
    { "Monter tes métiers", "L'onglet Montée donne le parcours le moins cher depuis ton niveau, aux prix de l'hôtel des ventes (scanne-le une fois). L'Atelier montre tes crafts rentables et les recettes à apprendre." },
    { "Réglages", "Tout se règle dans Options > AddOns > Broken Meta : Hub, ou avec /bmw options. Bon jeu !" },
  },
}, {
  next = "Next", prev = "Back", done = "Let's go!", skip = "Skip",
  steps = {
    { "Welcome to Broken Meta : Hub", "Four tools in one window: DPS for your gear, Professions for crafting, Economy for what your items are worth and good deals, Dungeons for each boss's loot. Open this window with the spiral button around the minimap or with /bmw." },
    { "Broken Meta : DPS", "Hover any item: its tooltip shows its DPS value for your spec, compared with what you wear. The Upgrades tab lists the best items in your bags and in the dungeons of your level." },
    { "Broken Meta : Professions", "Find an available crafter anywhere on your realm, browse their recipes and whisper them. Looking for an item? Post a request. You craft? Set yourself available in My profile." },
    { "Level your professions", "The Leveling tab gives the cheapest route from your skill, at auction house prices (scan it once). The Workshop shows your profitable crafts and the recipes to learn." },
    { "Settings", "Everything is in Options > AddOns > Broken Meta : Hub, or with /bmw options. Have fun!" },
  },
})

-- Which hub page each step opens (nil: leave it as is).
local function openFor(step)
  if step == 2 and ns.HubShow then ns.HubShow(1)
  elseif step == 3 and ns.ShowCrafters then ns.ShowCrafters()
  end
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
  if hub and hub:IsShown() then card:SetPoint("TOPLEFT", hub, "TOPRIGHT", 10, 0) else card:SetPoint("CENTER") end
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
