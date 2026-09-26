-- First-login welcome, and "a newer version exists" notices: addons of the same group/guild tell
-- each other their version through hidden addon messages (the addon itself has no internet).
local ADDON, ns = ...
local PREFIX = "BrokenMeta"
local THROTTLE = 60 -- seconds between broadcasts on the same channel

local function version()
  return (C_AddOns and C_AddOns.GetAddOnMetadata or GetAddOnMetadata or function() end)(ADDON, "Version") or "0"
end

-- "0.5.2" < "0.6.0"
local function newer(a, b)
  local x, y = { strsplit(".", a or "0") }, { strsplit(".", b or "0") }
  for i = 1, math.max(#x, #y) do
    local d = (tonumber(x[i]) or 0) - (tonumber(y[i]) or 0)
    if d ~= 0 then return d > 0 end
  end
  return false
end

local lastSent, notified = {}, false

local function send(channel)
  if not (C_ChatInfo and C_ChatInfo.SendAddonMessage) then return end
  local now = GetTime()
  if lastSent[channel] and now - lastSent[channel] < THROTTLE then return end
  lastSent[channel] = now
  pcall(C_ChatInfo.SendAddonMessage, PREFIX, "V:" .. version(), channel)
end

local function broadcast()
  if IsInGuild and IsInGuild() then send("GUILD") end
  if IsInRaid and IsInRaid() then send("RAID")
  elseif IsInGroup and IsInGroup() then send("PARTY") end
end

local f = CreateFrame("Frame")
for _, ev in ipairs({ "PLAYER_LOGIN", "GROUP_ROSTER_UPDATE", "CHAT_MSG_ADDON" }) do pcall(f.RegisterEvent, f, ev) end
f:SetScript("OnEvent", function(_, event, prefix, msg)
  if event == "PLAYER_LOGIN" then
    if C_ChatInfo and C_ChatInfo.RegisterAddonMessagePrefix then pcall(C_ChatInfo.RegisterAddonMessagePrefix, PREFIX) end
    C_Timer.After(15, broadcast)
    BrokenMetaWeightsDB = BrokenMetaWeightsDB or {}
    if not BrokenMetaWeightsDB.welcomed then
      BrokenMetaWeightsDB.welcomed = version()
      C_Timer.After(8, function()
        for _, line in ipairs(ns.L.welcome) do ns.say(line) end
      end)
    end
  elseif event == "GROUP_ROSTER_UPDATE" then
    C_Timer.After(5, broadcast)
  elseif event == "CHAT_MSG_ADDON" and prefix == PREFIX and not notified then
    local other = type(msg) == "string" and msg:match("^V:([%d%.]+)$")
    if other and newer(other, version()) then
      notified = true
      ns.say(string.format(ns.L.update_available, other, version()))
    end
  end
end)
