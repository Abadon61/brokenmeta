-- Measurements: snapshots of what the game itself reports (crit, mana regen, pet stats, rating
-- conversion), stored in the SavedVariables file on the player's own disk. They let the site
-- replace the simulator's unverified / Classic-approximation values with real Forever numbers.
-- Nothing leaves the computer from here: an uploader only sends BrokenMetaWeightsDB.data, and
-- only when the player turned sharing on (/bmw share on). No character name, no realm, except
-- realm + faction on auction prices (prices only make sense per realm).
local ADDON, ns = ...
local MAX_RECORDS = 400
local DATA_VERSION = 1

local function safe(fn, ...)
  if type(fn) ~= "function" then return nil end
  return (function(ok, ...) if ok then return ... end end)(pcall(fn, ...))
end

local function round(v, d)
  if type(v) ~= "number" then return nil end
  local m = 10 ^ (d or 2)
  return math.floor(v * m + 0.5) / m
end

function ns.Data()
  BrokenMetaWeightsDB = BrokenMetaWeightsDB or {}
  local d = BrokenMetaWeightsDB.data
  if type(d) ~= "table" or d.v ~= DATA_VERSION then
    d = { v = DATA_VERSION, meas = {}, sigs = {}, ah = {} }
    BrokenMetaWeightsDB.data = d
  end
  d.client = select(1, GetBuildInfo()) .. "." .. select(2, GetBuildInfo())
  d.addon = (C_AddOns and C_AddOns.GetAddOnMetadata or GetAddOnMetadata or function() end)(ADDON, "Version")
  return d
end

local function buffCount()
  local n = 0
  if C_UnitAuras and C_UnitAuras.GetAuraDataByIndex then
    while safe(C_UnitAuras.GetAuraDataByIndex, "player", n + 1, "HELPFUL") do n = n + 1 end
  elseif UnitBuff then
    while safe(UnitBuff, "player", n + 1) do n = n + 1 end
  end
  return n
end

-- Stores a record unless an identical one (same values, ignoring the timestamp) already exists.
local function store(rec)
  local d = ns.Data()
  local keys = {}
  for k in pairs(rec) do keys[#keys + 1] = k end
  table.sort(keys)
  local parts = {}
  for _, k in ipairs(keys) do parts[#parts + 1] = k .. "=" .. tostring(rec[k]) end
  local sig = table.concat(parts, ";")
  if d.sigs[sig] then return false end
  d.sigs[sig] = true
  rec.t = time()
  table.insert(d.meas, rec)
  while #d.meas > MAX_RECORDS do table.remove(d.meas, 1) end
  return true
end

local function talentString()
  local _, perTab = ns.readTalents and ns.readTalents()
  return perTab and table.concat(perTab, "/") or nil
end

-- Character sheet: base crit per class/level/Agility/Intellect, mana regen per Spirit, dodge...
local function snapStats()
  local _, class = UnitClass("player")
  local stat = {}
  for i = 1, 5 do stat[i] = select(2, safe(UnitStat, "player", i)) end
  local base, pos, neg = safe(UnitAttackPower, "player")
  local rbase, rpos, rneg = safe(UnitRangedAttackPower, "player")
  local regenBase, regenCast = safe(GetManaRegen)
  -- Defense and weapon skill rise while leveling and move crit/dodge/block by ~0.04% per point:
  -- recorded so the site can separate that from Agility (seen in the first real uploads).
  local defBase, defMod = safe(UnitDefense, "player")
  local mhSkill, mhMod, ohSkill, ohMod = safe(UnitAttackBothHands, "player")
  local spellCrit = 0
  for school = 2, 7 do spellCrit = math.max(spellCrit, safe(GetSpellCritChance, school) or 0) end
  return store({
    k = "stats", class = class, race = select(2, UnitRace("player")), level = UnitLevel("player"),
    str = stat[1], agi = stat[2], sta = stat[3], int = stat[4], spi = stat[5],
    ap = base and (base + (pos or 0) + (neg or 0)), rap = rbase and (rbase + (rpos or 0) + (rneg or 0)),
    crit_melee = round(safe(GetCritChance)), crit_ranged = round(safe(GetRangedCritChance)), crit_spell = round(spellCrit),
    dodge = round(safe(GetDodgeChance)), parry = round(safe(GetParryChance)), block = round(safe(GetBlockChance)),
    regen_base = round(regenBase, 3), regen_cast = round(regenCast, 3), mana_max = safe(UnitPowerMax, "player", 0),
    def_skill = defBase and (defBase + (defMod or 0)) or nil,
    wpn_skill_mh = mhSkill and (mhSkill + (mhMod or 0)) or nil,
    wpn_skill_oh = (ohSkill and ohSkill > 0) and (ohSkill + (ohMod or 0)) or nil,
    buffs = buffCount(), talents = talentString(), spec = ns.GetSpec and ns.GetSpec() or nil,
  })
end

-- Hunter/Warlock pet: its own stats next to the player's, to measure the real pet AP ratio.
local function snapPet()
  if not UnitExists("pet") then return false end
  local _, class = UnitClass("player")
  local stat = {}
  for i = 1, 5 do stat[i] = select(2, safe(UnitStat, "pet", i)) end
  local pb, pp, pn = safe(UnitAttackPower, "pet")
  local lo, hi = safe(UnitDamage, "pet")
  local rbase, rpos, rneg = safe(UnitRangedAttackPower, "player")
  local base, pos, neg = safe(UnitAttackPower, "player")
  return store({
    k = "pet", class = class, level = UnitLevel("player"), pet_level = UnitLevel("pet"),
    family = safe(UnitCreatureFamily, "pet"), pet_str = stat[1], pet_agi = stat[2], pet_sta = stat[3],
    pet_int = stat[4], pet_spi = stat[5], pet_ap = pb and (pb + (pp or 0) + (pn or 0)),
    pet_min = round(lo), pet_max = round(hi), pet_speed = round(safe(UnitAttackSpeed, "pet")),
    pet_armor = select(2, safe(UnitArmor, "pet")),
    player_ap = base and (base + (pos or 0) + (neg or 0)), player_rap = rbase and (rbase + (rpos or 0) + (rneg or 0)),
    buffs = buffCount(),
  })
end

-- Rating -> % at this level, straight from the client (percent given by 100 rating).
local CR_NAMES = { [6] = "hit_melee", [7] = "hit_ranged", [8] = "hit_spell", [9] = "crit_melee",
  [10] = "crit_ranged", [11] = "crit_spell", [18] = "haste_melee", [19] = "haste_ranged", [20] = "haste_spell" }
local function snapRatings()
  if not GetCombatRatingBonusForCombatRatingValue then return false end
  local rec = { k = "rating", level = UnitLevel("player") }
  for cr, name in pairs(CR_NAMES) do
    rec[name] = round(safe(GetCombatRatingBonusForCombatRatingValue, cr, 100), 4)
  end
  return store(rec)
end

-- Text version of BrokenMetaWeightsDB.data to copy-paste on the site's "share my data" page
-- (same content the page extracts from the SavedVariables file). One record per line:
--   BMD1 addon=..;client=..
--   M k=stats;class=SHAMAN;level=6;agi=19;...        one measurement
--   A t=..;realm=..;faction=..;mode=..;listings=..   one auction scan...
--   P itemID,unit,qty,auctions;itemID,...            ...and its prices
-- Values are percent-encoded for ";=,% " and newlines. "|" never appears: WoW edit boxes treat it
-- as an escape character, so it is encoded too.
local function enc(v)
  return (tostring(v):gsub("[%%;=,|\n\r ]", function(c) return string.format("%%%02X", c:byte()) end))
end

local function fields(t, skip)
  local keys = {}
  for k, v in pairs(t) do
    if not (skip and skip[k]) and (type(v) == "number" or type(v) == "string" or type(v) == "boolean") then
      keys[#keys + 1] = k
    end
  end
  table.sort(keys)
  local parts = {}
  for _, k in ipairs(keys) do parts[#parts + 1] = enc(k) .. "=" .. enc(t[k]) end
  return table.concat(parts, ";")
end

function ns.BuildShareString()
  local d = ns.Data()
  local lines = { "BMD1 " .. fields({ addon = d.addon or "", client = d.client or "" }) }
  for _, m in ipairs(d.meas) do lines[#lines + 1] = "M " .. fields(m) end
  for _, scan in ipairs(d.ah) do
    lines[#lines + 1] = "A " .. fields(scan, { prices = true })
    local items = {}
    for itemID in pairs(scan.prices) do items[#items + 1] = itemID end
    table.sort(items)
    local parts = {}
    for _, itemID in ipairs(items) do
      local p = scan.prices[itemID]
      parts[#parts + 1] = itemID .. "," .. p[1] .. "," .. p[2] .. "," .. p[3]
    end
    lines[#lines + 1] = "P " .. table.concat(parts, ";")
  end
  return table.concat(lines, "\n"), #d.meas, #d.ah
end

function ns.SnapshotAll()
  local n = 0
  for _, fn in ipairs({ snapStats, snapPet, snapRatings }) do
    local ok, added = pcall(fn)
    if ok and added then n = n + 1 end
  end
  if n > 0 and ns.OnDataChanged then ns.OnDataChanged() end
  return n
end

-- Debounced: equipment swaps and pet summons fire several events in a row.
local pending = false
local function schedule(delay)
  if pending then return end
  pending = true
  C_Timer.After(delay, function() pending = false; ns.SnapshotAll() end)
end

local f = CreateFrame("Frame")
-- No snapshot after every fight any more (0.6): it only produced near-duplicates.
for _, ev in ipairs({ "PLAYER_LOGIN", "PLAYER_LEVEL_UP", "PLAYER_EQUIPMENT_CHANGED", "UNIT_PET",
    "TRAIT_CONFIG_UPDATED" }) do
  pcall(f.RegisterEvent, f, ev)
end
f:SetScript("OnEvent", function(_, event, unit)
  if event == "PLAYER_LOGIN" then
    ns.Data()
    schedule(5)
  elseif event == "UNIT_PET" and unit ~= "player" then
    return
  else
    schedule(2)
  end
end)
