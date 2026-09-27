-- brokenmeta.gg look for the addon's own widgets: the site's palette (style_base.css) on flat
-- frames (a 1-pixel border and a solid fill, drawn with the plain white texture).
local _, ns = ...

local function rgb(hex, a)
  return { tonumber(hex:sub(1, 2), 16) / 255, tonumber(hex:sub(3, 4), 16) / 255, tonumber(hex:sub(5, 6), 16) / 255, a or 1 }
end

ns.C = {
  bg = rgb("100b26"), row = rgb("1a1440", 0.92), rowHover = rgb("251c58", 0.95),
  border = rgb("2f2760"), borderBright = rgb("4d4192"),
  magenta = rgb("d72638"), teal = rgb("2de6c4"), gold = rgb("ffc23c"),
  cream = rgb("f0e7d8"), dim = rgb("bdb4cf"), faint = rgb("8a81ab"),
}
-- Same colours for |c escapes in texts.
ns.HEX = { teal = "ff2de6c4", gold = "ffffc23c", cream = "fff0e7d8", dim = "ffbdb4cf", faint = "ff8a81ab", magenta = "ffd72638" }

local FLAT = "Interface\\Buttons\\WHITE8x8"

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
