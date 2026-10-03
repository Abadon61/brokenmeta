-- First-login welcome, and "a newer version exists" notices: addons of the same group/guild tell
-- each other their version through hidden addon messages (the addon itself has no internet).
local ADDON, ns = ...
local PREFIX = "BrokenMeta"
local THROTTLE = 60 -- seconds between broadcasts on the same channel

local function version(addon)
  return (C_AddOns and C_AddOns.GetAddOnMetadata or GetAddOnMetadata or function() end)(addon or ADDON, "Version") or "0"
end
local CHILDREN = { "BrokenDPS", "BrokenCrafter", "BrokenCodex" }

-- "M:BrokenDPS=1.0.0,BrokenCodex=1.0.0": the versions of the suite's addons loaded here (the HUB's
-- own version keeps its "V:" message, which older versions understand).
local function modulesMessage()
  local parts = {}
  for _, a in ipairs(CHILDREN) do
    if ns.Modules[a] then parts[#parts + 1] = a .. "=" .. version(a) end
  end
  return #parts > 0 and "M:" .. table.concat(parts, ",") or nil
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

local lastSent, notified = {}, {}

local function send(channel)
  if not (C_ChatInfo and C_ChatInfo.SendAddonMessage) then return end
  local now = GetTime()
  if lastSent[channel] and now - lastSent[channel] < THROTTLE then return end
  lastSent[channel] = now
  pcall(C_ChatInfo.SendAddonMessage, PREFIX, "V:" .. version(), channel)
  local m = modulesMessage()
  if m then pcall(C_ChatInfo.SendAddonMessage, PREFIX, m, channel) end
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
  elseif event == "CHAT_MSG_ADDON" and prefix == PREFIX and type(msg) == "string" then
    local other = msg:match("^V:([%d%.]+)$")
    if other and not notified[ADDON] and newer(other, version()) then
      notified[ADDON] = true
      ns.say(string.format(ns.L.update_available, other, version()))
    end
    for name, v in (msg:match("^M:(.+)$") or ""):gmatch("(%w+)=([%d%.]+)") do
      if ns.Modules[name] and not notified[name] and newer(v, version(name)) then
        notified[name] = true
        ns.say(name .. " — " .. string.format(ns.L.update_available, v, version(name)))
      end
    end
  end
end)
