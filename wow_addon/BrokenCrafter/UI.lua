-- Broken Meta : Crafter, shared interface pieces: profession icons, callouts (empty states and calls
-- to action), drop-down lists and toasts. Loaded before the tabs that use them.
local ADDON = ...
local ns = BrokenMetaNS -- Broken Meta : HUB's namespace, shared by the suite
if not ns.HubTab then return end
local C, HEX = ns.C, ns.HEX
local W = ns.Hub.W

---------------------------------------------------------------------------------------------
-- Profession icons (skill line -> game icon), inline in a text with ns.ProfIcon.
---------------------------------------------------------------------------------------------
local ICONS = {
  [164] = "Trade_BlackSmithing", [165] = "Trade_LeatherWorking", [197] = "Trade_Tailoring", [171] = "Trade_Alchemy",
  [202] = "Trade_Engineering", [333] = "Trade_Engraving", [755] = "INV_Misc_Gem_01",
  [773] = "INV_Inscription_Tradeskill01", [185] = "INV_Misc_Food_15", [129] = "Spell_Holy_SealOfSacrifice",
}

function ns.ProfIconPath(line)
  return ICONS[line] and ("Interface\\Icons\\" .. ICONS[line]) or "Interface\\Icons\\INV_Misc_QuestionMark"
end

-- "|T...|t " to put in front of a profession name; empty for a line without an icon.
function ns.ProfIcon(line, size)
  if not ICONS[line] then return "" end
  size = size or 14
  return "|TInterface\\Icons\\" .. ICONS[line] .. ":" .. size .. ":" .. size .. ":0:0:64:64:5:59:5:59|t "
end

---------------------------------------------------------------------------------------------
-- Callout: a framed box with an icon, a title, a text and an optional button. Used where a list
-- is empty (say why and what to do) and for calls to action.
--   local box = ns.Callout(page, top); box:Set({ icon = path, title = "", text = "", btn = "", onClick = fn, warn = bool })
--   box:Hide()
---------------------------------------------------------------------------------------------
function ns.Callout(page, top, width, x)
  local f = CreateFrame("Frame", nil, page, ns.BACKDROP_TEMPLATE)
  f:SetSize(width or (W - 32), 210)
  f:SetPoint("TOPLEFT", x or 4, top)
  ns.Flat(f, C.row, C.border)
  f.icon = f:CreateTexture(nil, "ARTWORK")
  f.icon:SetSize(48, 48)
  f.icon:SetPoint("TOP", 0, -20)
  f.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)
  f.title = f:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
  f.title:SetPoint("TOP", f.icon, "BOTTOM", 0, -12)
  f.title:SetWidth((width or W) - 100)
  f.text = f:CreateFontString(nil, "OVERLAY", "BrokenMetaFontBody")
  f.text:SetPoint("TOP", f.title, "BOTTOM", 0, -10)
  f.text:SetWidth((width or W) - 140)
  f.text:SetJustifyH("CENTER")
  f.btn = ns.Button(f, nil, "primary")
  f.btn:SetSize(260, 32)
  f.btn:SetPoint("BOTTOM", 0, 18)
  function f:Set(spec)
    self.icon:SetTexture(spec.icon or "Interface\\Icons\\INV_Misc_QuestionMark")
    self.title:SetText("|c" .. HEX.gold .. (spec.title or "") .. "|r")
    self.text:SetText(spec.text or "")
    ns.FlatBorder(self, spec.warn and C.gold or C.border)
    self.btn:SetShown(spec.btn ~= nil)
    if spec.btn then
      self.btn:SetText(spec.btn)
      self.btn:SetScript("OnClick", spec.onClick or function() end)
    end
    self:Show()
  end
  f:Hide()
  return f
end

---------------------------------------------------------------------------------------------
-- Drop-down list under a button (own frame, flat style): ns.DropDown(btn, page, labels, current, pick)
--   labels(): array of strings; current(): index of the chosen one; pick(i): called on a click.
-- A click anywhere else, or hiding the page, closes it.
---------------------------------------------------------------------------------------------
function ns.DropDown(btn, page, labels, current, pick)
  local menu = CreateFrame("Frame", nil, page, ns.BACKDROP_TEMPLATE)
  local catcher = CreateFrame("Button", nil, page)
  local rows = {}
  local function close() menu:Hide(); catcher:Hide() end
  catcher:SetAllPoints(UIParent)
  catcher:SetFrameStrata("DIALOG")
  catcher:SetScript("OnClick", close)
  catcher:Hide()
  menu:SetPoint("TOPLEFT", btn, "BOTTOMLEFT", 0, -2)
  menu:SetFrameStrata("DIALOG")
  menu:SetFrameLevel((catcher:GetFrameLevel() or 0) + 5)
  menu:EnableMouse(true)
  ns.Flat(menu, C.bg, C.teal)
  menu:Hide()
  btn:SetScript("OnClick", function()
    if menu:IsShown() then close(); return end
    local list, now = labels(), current()
    menu:SetSize(math.max(200, btn:GetWidth() or 200), #list * 22 + 8)
    for i, text in ipairs(list) do
      local row = rows[i]
      if not row then
        row = ns.Button(menu)
        row:SetPoint("TOPLEFT", 4, -4 - (i - 1) * 22)
        rows[i] = row
      end
      row:SetSize((menu:GetWidth() or 200) - 8, 22)
      row:SetText(i == now and ("|c" .. HEX.teal .. text .. "|r") or text)
      row:SetScript("OnClick", function() close(); pick(i) end)
      row:Show()
    end
    for i = #list + 1, #rows do rows[i]:Hide() end
    catcher:Show(); menu:Show()
  end)
  page:HookScript("OnHide", close)
  return close
end

---------------------------------------------------------------------------------------------
-- Toast: a short message at the bottom of the hub that fades out; in the chat when the hub is closed.
---------------------------------------------------------------------------------------------
local toast
function ns.Toast(text)
  local hub = _G.BrokenMetaHub
  if not (hub and hub.IsShown and hub:IsShown()) then ns.say(text); return end
  if not toast then
    toast = CreateFrame("Frame", nil, hub, ns.BACKDROP_TEMPLATE)
    toast:SetSize(480, 36)
    toast:SetPoint("BOTTOM", hub, "BOTTOM", 0, 48)
    toast:SetFrameStrata("DIALOG")
    ns.Flat(toast, C.bg, C.teal)
    toast.text = toast:CreateFontString(nil, "OVERLAY", "BrokenMetaFontStrong")
    toast.text:SetPoint("CENTER")
    toast.text:SetWidth(460)
    toast:SetScript("OnUpdate", function(self, dt)
      self.left = (self.left or 0) - dt
      if self.left <= 0 then self:Hide() elseif self.left < 0.6 then self:SetAlpha(self.left / 0.6) end
    end)
  end
  toast.text:SetText("|c" .. HEX.teal .. text:gsub("^%l", string.upper) .. "|r")
  toast.left = 3.4
  toast:SetAlpha(1)
  toast:Show()
end
