-- Broken Meta : HUB core. Shared by the addons of the suite (BrokenDPS, BrokenCrafter,
-- BrokenCodex), which all use this namespace (BrokenMetaNS, see Locales.lua):
--   texts shared by the suite (ns.L), chat output (ns.say), the item slots table (ns.SLOTS);
--   the /bmw command: the HUB's own subcommands, and ns.RegisterCommand for the others;
--   one item tooltip hook: each addon adds its line with ns.AddTooltipHandler(fn, order).
local ADDON, ns = ...
local IS_FR = ns.IS_FR

local L = ns.Localize("core", {
  header = "Broken Meta",
  vs_equipped = "vs équipé", vs_two = "vs tes deux armes", vs_other = "%s vs l'autre",
  replaces_2h = "remplace ton arme à deux mains",
  same = "équipé",
  no_spec = "aucune spécialisation DPS simulée pour cette classe.",
  spec_set = "spécialisation : %s",
  spec_auto = "détection automatique (arbre de talents le plus rempli).",
  spec_unknown = "spécialisation inconnue : %s. Liste : /bmw list",
  help = "/bmw : fenêtre · /bmw weights · /bmw export · /bmw list · /bmw spec <id> · /bmw auto · /bmw minimap · /bmw share · /bmw ah · /bmw import · /bmw craft · /bmw options · /bmw lang · /bmw tour · /bmw probe",
  weights = "Poids (DPS par point) pour %s :",
  approx = "approximation",
  share_state = "partage des données avec brokenmeta.gg : ",
  import_ok = "tes poids personnels sont importés : ils remplacent les poids génériques pour ce personnage.", import_bad = "ce texte n'est pas un export de poids Broken Meta (il commence par BMW-W1).", import_class = "ces poids sont pour une autre classe que ce personnage.", import_cleared = "retour aux poids génériques (niveau 20).",
  lang_set = "langue enregistrée : tape /reload pour l'appliquer.", lang_help = "/bmw lang fr, en, de, es ou auto (langue du jeu).",
  refresh_weights = "tes poids personnels datent du niveau %d : refais-les sur brokenmeta.gg (Simuler mon personnage), à faire tous les %d niveaux.",
  loot_drop = "Butin de donjon : %s (%s)", loot_quest = "Récompense de quête : %s",
  welcome = {
    "merci d'avoir installé l'addon ! Clique sur le bouton à l'épée autour de la minicarte (ou tape /bmw) pour ouvrir le hub.",
    "Survole un objet : sa valeur en DPS pour ta spé s'affiche dans l'infobulle. Guides et simulateur : brokenmeta.gg",
  },
  update_available = "une nouvelle version de l'addon existe (%s, tu as la %s) : mets-la à jour avec l\'application CurseForge.",
  cant_wear = "ta classe ne peut pas le porter", wear_at = "portable au niveau %d",
  snap_done = "%d nouvelle(s) mesure(s) enregistrée(s).",
}, {
  header = "Broken Meta",
  vs_equipped = "vs equipped", vs_two = "vs both your weapons", vs_other = "%s vs the other",
  replaces_2h = "replaces your two-hander",
  same = "equipped",
  no_spec = "no simulated DPS spec for this class.",
  spec_set = "spec: %s",
  spec_auto = "automatic detection (talent tree with the most points).",
  spec_unknown = "unknown spec: %s. List: /bmw list",
  help = "/bmw: window · /bmw weights · /bmw export · /bmw list · /bmw spec <id> · /bmw auto · /bmw minimap · /bmw share · /bmw ah · /bmw import · /bmw craft · /bmw options · /bmw lang · /bmw tour · /bmw probe",
  weights = "Weights (DPS per point) for %s:",
  approx = "approximation",
  share_state = "data sharing with brokenmeta.gg: ",
  import_ok = "your personal weights are imported: they replace the generic weights for this character.", import_bad = "this text isn't a Broken Meta weights export (it starts with BMW-W1).", import_class = "these weights are for another class than this character.", import_cleared = "back to the generic (level 20) weights.",
  lang_set = "language saved: type /reload to apply it.", lang_help = "/bmw lang fr, en, de, es or auto (the game's language).",
  refresh_weights = "your personal weights are from level %d: redo them on brokenmeta.gg (Simulate my character), every %d levels.",
  loot_drop = "Dungeon loot: %s (%s)", loot_quest = "Quest reward: %s",
  welcome = {
    "thanks for installing the addon! Click the sword button around the minimap (or type /bmw) to open the hub.",
    "Hover an item: its DPS value for your spec shows in the tooltip. Guides and simulator: brokenmeta.gg",
  },
  update_available = "a newer version of the addon exists (%s, you have %s): update it with the CurseForge app.",
  cant_wear = "your class can't wear it", wear_at = "wearable at level %d",
  snap_done = "%d new measurement(s) recorded.",
})

local function say(msg) DEFAULT_CHAT_FRAME:AddMessage("|cff2de6c4Broken Meta|r " .. msg) end
ns.L, ns.say = L, say
-- Forever runs the modern (Mainline) UI, where these globals moved into C_Item.
ns.GetItemInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo

-- Item equip location -> inventory slot(s).
local SLOTS = {
  INVTYPE_HEAD = { 1 }, INVTYPE_NECK = { 2 }, INVTYPE_SHOULDER = { 3 }, INVTYPE_CHEST = { 5 },
  INVTYPE_ROBE = { 5 }, INVTYPE_WAIST = { 6 }, INVTYPE_LEGS = { 7 }, INVTYPE_FEET = { 8 },
  INVTYPE_WRIST = { 9 }, INVTYPE_HAND = { 10 }, INVTYPE_FINGER = { 11, 12 },
  INVTYPE_TRINKET = { 13, 14 }, INVTYPE_CLOAK = { 15 }, INVTYPE_WEAPON = { 16, 17 },
  INVTYPE_2HWEAPON = { 16 }, INVTYPE_WEAPONMAINHAND = { 16 }, INVTYPE_WEAPONOFFHAND = { 17 },
  INVTYPE_SHIELD = { 17 }, INVTYPE_HOLDABLE = { 17 }, INVTYPE_RANGED = { 18 },
  INVTYPE_RANGEDRIGHT = { 18 }, INVTYPE_THROWN = { 18 }, INVTYPE_RELIC = { 18 },
}
ns.SLOTS = SLOTS

---------------------------------------------------------------------------------------------
-- /bmw
---------------------------------------------------------------------------------------------
local commands = {}
function ns.RegisterCommand(name, fn) commands[name] = fn end

SLASH_BROKENMETAWEIGHTS1 = "/bmw"
SlashCmdList.BROKENMETAWEIGHTS = function(msg)
  local cmd, arg = (msg or ""):lower():match("^(%S*)%s*(.-)$")
  if commands[cmd] then return commands[cmd](arg) end
  if cmd == "share" then
    if arg == "on" or arg == "off" then BrokenMetaWeightsDB.share = (arg == "on") end
    say(L.share_state .. (BrokenMetaWeightsDB.share and "|cff40ff40ON|r" or "off"))
    if ns.OnDataChanged then ns.OnDataChanged() end
  elseif cmd == "copy" and ns.ShowShareCopy then
    ns.ShowShareCopy()
  elseif cmd == "snap" and ns.SnapshotAll then
    say(string.format(L.snap_done, ns.SnapshotAll()))
  elseif cmd == "minimap" and ns.ToggleMinimap then
    ns.ToggleMinimap()
  elseif cmd == "lang" and ns.SetLanguage then
    -- /bmw lang fr|en|de|es|auto: saved now, applied at the next /reload.
    local code = ({ fr = "frFR", en = "enUS", de = "deDE", es = "esES", auto = "auto" })[arg]
    if code then ns.SetLanguage(code); say(L.lang_set) else say(L.lang_help) end
  elseif cmd == "options" and ns.ShowOptions then
    ns.ShowOptions()
  elseif cmd == "tour" and ns.StartTour then
    ns.StartTour()
  elseif cmd == "" and ns.ToggleHub then
    ns.ToggleHub()
  else
    say(L.help)
  end
end

---------------------------------------------------------------------------------------------
-- Item tooltips: one hook, the lines of every addon of the suite, in their order
---------------------------------------------------------------------------------------------
local handlers = {}
function ns.AddTooltipHandler(fn, order)
  handlers[#handlers + 1] = { fn = fn, order = order or 10 }
  table.sort(handlers, function(a, b) return a.order < b.order end)
end

local function onTooltipItem(tt)
  if not tt.GetItem then return end
  local _, link = tt:GetItem()
  if not link then return end
  local added = false
  for _, h in ipairs(handlers) do
    local ok, did = pcall(h.fn, tt, link)
    if ok and did then added = true end
  end
  if added then tt:Show() end
end

if TooltipDataProcessor and Enum and Enum.TooltipDataType and Enum.TooltipDataType.Item then
  TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Item, onTooltipItem)
else
  for _, name in ipairs({ "GameTooltip", "ItemRefTooltip", "ShoppingTooltip1", "ShoppingTooltip2" }) do
    local tt = _G[name]
    if tt then tt:HookScript("OnTooltipSetItem", onTooltipItem) end
  end
end

-- Saved data shared by the suite.
local ev = CreateFrame("Frame")
ev:RegisterEvent("PLAYER_LOGIN")
ev:SetScript("OnEvent", function()
  BrokenMetaWeightsDB = BrokenMetaWeightsDB or {}
  BrokenMetaWeightsDB.chars = BrokenMetaWeightsDB.chars or {}
end)
