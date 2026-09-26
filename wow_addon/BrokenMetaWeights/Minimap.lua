-- Minimap button (drag it around the minimap edge) + the modern addon-compartment entry.
-- Left click: open/close the hub. Right click: open the Export tab.
local ADDON, ns = ...
local IS_FR = ns.IS_FR
local ICON = "Interface\\AddOns\\BrokenMetaWeights\\Media\\icon"
ns.ICON = ICON

local TIP = IS_FR and {
  left = "|cffffffffClic gauche|r : ouvrir le hub",
  right = "|cffffffffClic droit|r : export pour brokenmeta.gg",
  drag = "|cffffffffGlisser|r : déplacer le bouton",
  hidden = "bouton de la minicarte masqué. /bmw minimap pour le réafficher.",
  shown = "bouton de la minicarte affiché.",
} or {
  left = "|cffffffffLeft click|r: open the hub",
  right = "|cffffffffRight click|r: export for brokenmeta.gg",
  drag = "|cffffffffDrag|r: move the button",
  hidden = "minimap button hidden. /bmw minimap to show it again.",
  shown = "minimap button shown.",
}

local btn = CreateFrame("Button", "BrokenMetaMinimapButton", Minimap)
btn:SetSize(31, 31)
btn:SetFrameStrata("MEDIUM")
btn:SetFrameLevel(8)
btn:RegisterForClicks("LeftButtonUp", "RightButtonUp")
btn:RegisterForDrag("LeftButton")
btn:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight")

local bg = btn:CreateTexture(nil, "BACKGROUND")
bg:SetSize(20, 20)
bg:SetTexture("Interface\\Minimap\\UI-Minimap-Background")
bg:SetPoint("TOPLEFT", 7, -5)

local icon = btn:CreateTexture(nil, "ARTWORK")
icon:SetSize(20, 20)
icon:SetTexture(ICON)
icon:SetPoint("TOPLEFT", 6, -5)

local border = btn:CreateTexture(nil, "OVERLAY")
border:SetSize(53, 53)
border:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
border:SetPoint("TOPLEFT")

-- Position on the minimap's edge from a saved angle (degrees).
local function place(angle)
  local rad = math.rad(angle)
  local r = (Minimap:GetWidth() / 2) + 5
  btn:ClearAllPoints()
  btn:SetPoint("CENTER", Minimap, "CENTER", math.cos(rad) * r, math.sin(rad) * r)
end

local function dragUpdate()
  local mx, my = Minimap:GetCenter()
  local scale = Minimap:GetEffectiveScale()
  local cx, cy = GetCursorPosition()
  local angle = math.deg(math.atan2(cy / scale - my, cx / scale - mx))
  BrokenMetaWeightsDB.minimapAngle = angle
  place(angle)
end

btn:SetScript("OnDragStart", function(self) self:SetScript("OnUpdate", dragUpdate) end)
btn:SetScript("OnDragStop", function(self) self:SetScript("OnUpdate", nil) end)

btn:SetScript("OnClick", function(_, button)
  if button == "RightButton" then
    if ns.ShowExport then ns.ShowExport() end
  elseif ns.ToggleHub then
    ns.ToggleHub()
  end
end)

btn:SetScript("OnEnter", function(self)
  GameTooltip:SetOwner(self, "ANCHOR_LEFT")
  GameTooltip:AddLine("|T" .. ICON .. ":16|t BrokenMeta", 0.31, 0.82, 0.77)
  if ns.GetSpec and ns.GetSpec() then GameTooltip:AddLine(ns.specName(ns.GetSpec()), 1, 1, 1) end
  GameTooltip:AddLine(TIP.left)
  GameTooltip:AddLine(TIP.right)
  GameTooltip:AddLine(TIP.drag)
  GameTooltip:Show()
end)
btn:SetScript("OnLeave", function() GameTooltip:Hide() end)

function ns.ApplyMinimap()
  BrokenMetaWeightsDB = BrokenMetaWeightsDB or {}
  place(BrokenMetaWeightsDB.minimapAngle or 215)
  btn:SetShown(not BrokenMetaWeightsDB.minimapHidden)
end

function ns.ToggleMinimap()
  BrokenMetaWeightsDB.minimapHidden = not BrokenMetaWeightsDB.minimapHidden
  ns.ApplyMinimap()
  ns.say(BrokenMetaWeightsDB.minimapHidden and TIP.hidden or TIP.shown)
end

-- Addon compartment (the modern minimap dropdown listing addons), named in the .toc.
function BrokenMeta_OnCompartmentClick(_, button)
  if button == "RightButton" then
    if ns.ShowExport then ns.ShowExport() end
  elseif ns.ToggleHub then
    ns.ToggleHub()
  end
end

btn:Hide()
local f = CreateFrame("Frame")
f:RegisterEvent("PLAYER_LOGIN")
f:SetScript("OnEvent", function() ns.ApplyMinimap() end)
