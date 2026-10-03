-- Look of the addon: a dark palette and the site's fonts (Cal Sans for titles and buttons, Afacad
-- Flux for text, Space Mono for numbers) on flat frames (a 1-pixel border and a solid fill, drawn
-- with the plain white texture).
local ADDON, ns = ...

local function rgb(hex, a)
  return { tonumber(hex:sub(1, 2), 16) / 255, tonumber(hex:sub(3, 4), 16) / 255, tonumber(hex:sub(5, 6), 16) / 255, a or 1 }
end

-- Palette: near-black blue panels, a teal accent, soft white texts (the "grand tableau" mock-up).
-- "magenta" is kept as a name but is the accent of primary buttons and of the active tab.
ns.C = {
  bg = rgb("0b0c13", 0.97), row = rgb("12141f", 0.95), rowHover = rgb("1b1e2f", 0.97),
  border = rgb("262a3d"), borderBright = rgb("3a3f66"),
  magenta = rgb("2de6c4"), teal = rgb("2de6c4"), gold = rgb("ffc23c"),
  cream = rgb("e9e9f1"), dim = rgb("a2a6bd"), faint = rgb("7a7e96"), none = { 0, 0, 0, 0 },
}
-- Same colours for |c escapes in texts.
ns.HEX = { teal = "ff2de6c4", gold = "ffffc23c", cream = "ffe9e9f1", dim = "ffa2a6bd", faint = "ff7a7e96", magenta = "ff2de6c4" }

local FLAT = "Interface\\Buttons\\WHITE8x8"
local FONTS = "Interface\\AddOns\\" .. ADDON .. "\\Media\\Fonts\\"
ns.MEDIA = "Interface\\AddOns\\" .. ADDON .. "\\Media\\"

-- Font objects, used by name in CreateFontString(nil, layer, "BrokenMetaFont...").
local function font(name, file, size, color)
  local f = CreateFont(name)
  if f and f.SetFont then
    f:SetFont(FONTS .. file, size, "")
    f:SetTextColor(unpack(color))
    f:SetShadowOffset(1, -1)
    f:SetShadowColor(0, 0, 0, 0.6)
  end
  return f
end
if CreateFont then
  font("BrokenMetaFontTitle", "CalSans-Regular.ttf", 17, ns.C.cream)
  font("BrokenMetaFontHeading", "CalSans-Regular.ttf", 14, ns.C.gold)
  font("BrokenMetaFontButton", "CalSans-Regular.ttf", 12, ns.C.cream)
  font("BrokenMetaFontButtonDim", "CalSans-Regular.ttf", 12, ns.C.faint)
  font("BrokenMetaFontSection", "CalSans-Regular.ttf", 15, ns.C.cream)
  font("BrokenMetaFontSectionDim", "CalSans-Regular.ttf", 15, ns.C.faint)
  font("BrokenMetaFontName", "CalSans-Regular.ttf", 14, ns.C.cream)
  font("BrokenMetaFontBody", "AfacadFlux-Regular.ttf", 14, ns.C.cream)
  font("BrokenMetaFontBodySmall", "AfacadFlux-Regular.ttf", 12, ns.C.cream)
  font("BrokenMetaFontHint", "AfacadFlux-Regular.ttf", 12, ns.C.dim)
  font("BrokenMetaFontStrong", "AfacadFlux-Medium.ttf", 14, ns.C.cream)
  font("BrokenMetaFontMono", "SpaceMono-Regular.ttf", 11, ns.C.cream)
end

-- Frame template that carries SetBackdrop on modern clients (nil on clients that have it built in).
ns.BACKDROP_TEMPLATE = BackdropTemplateMixin and "BackdropTemplate" or nil

function ns.Flat(frame, fill, edge)
  if not frame.SetBackdrop then return end
  frame:SetBackdrop({ bgFile = FLAT, edgeFile = FLAT, edgeSize = 1 })
  frame:SetBackdropColor(unpack(fill or ns.C.row))
  frame:SetBackdropBorderColor(unpack(edge or ns.C.border))
end

function ns.FlatBorder(frame, edge)
  if frame.SetBackdropBorderColor then frame:SetBackdropBorderColor(unpack(edge)) end
end

local function line(parent, layer)
  local t = parent:CreateTexture(nil, layer or "ARTWORK")
  t:SetTexture(FLAT)
  return t
end
ns.Line = line

---------------------------------------------------------------------------------------------
-- Buttons. kind: "button" (outlined), "primary" (magenta outline), "tab" (text with a magenta
-- underline when active), "pill" (sub-tab: filled when active).
-- LockHighlight / UnlockHighlight mark the active tab, like on the Blizzard buttons they replace.
---------------------------------------------------------------------------------------------
-- solid: filled background (for a button that sits over the game world).
function ns.Button(parent, name, kind, solid)
  kind = kind or "button"
  local b = CreateFrame("Button", name, parent, ns.BACKDROP_TEMPLATE)
  b.kind = kind
  local label = b:CreateFontString(nil, "OVERLAY", "BrokenMetaFontButton")
  label:SetPoint("CENTER", 0, 0)
  if b.SetFontString then b:SetFontString(label) end
  local framed = kind == "button" or kind == "primary" or kind == "pill"
  if framed then ns.Flat(b, ns.C.none, ns.C.none) end
  if b.SetNormalFontObject then
    b:SetNormalFontObject(kind == "tab" and "BrokenMetaFontSectionDim" or "BrokenMetaFontButton")
    b:SetHighlightFontObject(kind == "tab" and "BrokenMetaFontSection" or "BrokenMetaFontButton")
    b:SetDisabledFontObject("BrokenMetaFontButtonDim")
  end
  if kind == "tab" then
    b.under = line(b, "OVERLAY")
    b.under:SetColorTexture(unpack(ns.C.magenta))
    b.under:SetHeight(2)
    b.under:SetPoint("BOTTOMLEFT", 0, 0)
    b.under:SetPoint("BOTTOMRIGHT", 0, 0)
    b.under:Hide()
  end

  local function paint(self)
    local hover = self.hover and self:IsEnabled()
    if kind == "tab" then
      if self.under then self.under:SetShown(self.active) end
      if self.SetNormalFontObject then self:SetNormalFontObject(self.active and "BrokenMetaFontSection" or "BrokenMetaFontSectionDim") end
    elseif kind == "pill" then
      self:SetBackdropColor(unpack(self.active and ns.C.row or (hover and ns.C.rowHover or ns.C.none)))
      ns.FlatBorder(self, self.active and ns.C.borderBright or (hover and ns.C.border or ns.C.none))
      if self.SetNormalFontObject then self:SetNormalFontObject(self.active and "BrokenMetaFontButton" or "BrokenMetaFontButtonDim") end
    elseif self.SetBackdropColor then
      local edge = kind == "primary" and ns.C.magenta or ns.C.borderBright
      if not self:IsEnabled() then edge = ns.C.border end
      self:SetBackdropColor(unpack(hover and ns.C.rowHover or (solid and ns.C.bg or ns.C.none)))
      ns.FlatBorder(self, (hover or self.active) and (kind == "primary" and ns.C.magenta or ns.C.teal) or edge)
    end
  end
  b.Paint = paint
  b:HookScript("OnEnter", function(self) self.hover = true; paint(self) end)
  b:HookScript("OnLeave", function(self) self.hover = false; paint(self) end)
  function b:LockHighlight() self.active = true; paint(self) end
  function b:UnlockHighlight() self.active = false; paint(self) end
  local enable, disable = b.Enable, b.Disable
  function b:Enable() enable(self); paint(self) end
  function b:Disable() disable(self); paint(self) end
  paint(b)
  return b
end

---------------------------------------------------------------------------------------------
-- Window: flat panel, header with the logo and the title, a close cross, drag to move, Escape
-- closes it. Returns the frame; frame.title is the title font string.
---------------------------------------------------------------------------------------------
ns.HEADER_H = 34
function ns.Window(name, width, height, title, strata)
  local w = CreateFrame("Frame", name, UIParent, ns.BACKDROP_TEMPLATE)
  w:SetSize(width, height)
  w:SetPoint("CENTER")
  w:SetFrameStrata(strata or "HIGH")
  ns.Flat(w, ns.C.bg, ns.C.border)
  w:SetMovable(true)
  w:EnableMouse(true)
  w:RegisterForDrag("LeftButton")
  w:SetScript("OnDragStart", w.StartMoving)
  w:SetScript("OnDragStop", w.StopMovingOrSizing)
  w:SetClampedToScreen(true)
  w:Hide()
  if name then tinsert(UISpecialFrames, name) end

  local logo = w:CreateTexture(nil, "ARTWORK")
  logo:SetTexture(ns.MEDIA .. "icon")
  logo:SetSize(20, 20)
  logo:SetPoint("TOPLEFT", 12, -7)
  w.title = w:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
  w.title:SetPoint("LEFT", logo, "RIGHT", 8, 0)
  w.title:SetText(title or "")
  local sep = line(w)
  sep:SetColorTexture(unpack(ns.C.border))
  sep:SetHeight(1)
  sep:SetPoint("TOPLEFT", 1, -ns.HEADER_H)
  sep:SetPoint("TOPRIGHT", -1, -ns.HEADER_H)

  local close = CreateFrame("Button", nil, w)
  close:SetSize(26, 26)
  close:SetPoint("TOPRIGHT", -6, -4)
  local x = close:CreateFontString(nil, "OVERLAY", "BrokenMetaFontTitle")
  x:SetPoint("CENTER", 0, 1)
  x:SetText("×")
  x:SetTextColor(unpack(ns.C.faint))
  close:SetScript("OnEnter", function() x:SetTextColor(unpack(ns.C.magenta)) end)
  close:SetScript("OnLeave", function() x:SetTextColor(unpack(ns.C.faint)) end)
  close:SetScript("OnClick", function() w:Hide() end)
  return w
end

-- Single-line text field.
function ns.Input(parent)
  local e = CreateFrame("EditBox", nil, parent, ns.BACKDROP_TEMPLATE)
  ns.Flat(e, ns.C.row, ns.C.borderBright)
  e:SetFontObject("BrokenMetaFontBody")
  e:SetTextInsets(8, 8, 0, 0)
  e:SetAutoFocus(false)
  e:HookScript("OnEditFocusGained", function(self) ns.FlatBorder(self, ns.C.teal) end)
  e:HookScript("OnEditFocusLost", function(self) ns.FlatBorder(self, ns.C.borderBright) end)
  return e
end
