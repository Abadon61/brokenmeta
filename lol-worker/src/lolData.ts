// Static reference data: Riot's numeric IDs (summoner spells, runes) mapped
// to display names and CommunityDragon icon slugs. These IDs are stable
// Riot constants (unlike the artifact mockup, nothing here is invented),
// but the exact FR names and a few icon slugs are from memory, not a live
// verification pass in this session -- spot-check against the live FR
// client and the CommunityDragon paths before relying on this for the
// production-key submission. A wrong slug just hides one icon (see
// spellIconUrl/runeIconUrl callers' onerror handling) -- it never breaks
// the page.
export const SUMMONER_SPELLS: Record<number, { name: string; slug: string }> = {
  1: { name: "Purification", slug: "summonerboost" },
  3: { name: "Épuisement", slug: "summonerexhaust" },
  4: { name: "Flash", slug: "summonerflash" },
  6: { name: "Hâte", slug: "summonerhaste" },
  7: { name: "Soin", slug: "summonerheal" },
  11: { name: "Châtiment", slug: "summonersmite" },
  12: { name: "Téléportation", slug: "summonerteleport" },
  13: { name: "Clarté", slug: "summonermana" },
  14: { name: "Embrasement", slug: "summonerdot" },
  21: { name: "Barrière", slug: "summonerbarrier" },
  32: { name: "Boule de neige", slug: "summonersnowball" },
};

export const RUNE_TREES: Record<number, { name: string; slug: string }> = {
  8000: { name: "Précision", slug: "precision" },
  8100: { name: "Domination", slug: "domination" },
  8200: { name: "Sorcellerie", slug: "sorcery" },
  8400: { name: "Résolution", slug: "resolve" },
  8300: { name: "Inspiration", slug: "inspiration" },
};

export const KEYSTONES: Record<number, { name: string; slug: string; tree: number }> = {
  8005: { name: "Coup assuré", slug: "presstheattack", tree: 8000 },
  8008: { name: "Tempo fatal", slug: "lethaltempo", tree: 8000 },
  8021: { name: "Pas rapide", slug: "fleetfootwork", tree: 8000 },
  8010: { name: "Conquérant", slug: "conqueror", tree: 8000 },
  8112: { name: "Électrocution", slug: "electrocute", tree: 8100 },
  8124: { name: "Prédateur", slug: "predator", tree: 8100 },
  8128: { name: "Moisson sinistre", slug: "darkharvest", tree: 8100 },
  9923: { name: "Pluie de lames", slug: "hailofblades", tree: 8100 },
  8214: { name: "Convocation d'Aery", slug: "summonaery", tree: 8200 },
  8229: { name: "Comète arcanique", slug: "arcanecomet", tree: 8200 },
  8230: { name: "Accélération", slug: "phaserush", tree: 8200 },
  8437: { name: "Étreinte de l'increvable", slug: "graspoftheundying", tree: 8400 },
  8439: { name: "Choc en retour", slug: "aftershock", tree: 8400 },
  8465: { name: "Gardien", slug: "guardian", tree: 8400 },
  8351: { name: "Renfort glacial", slug: "glacialaugment", tree: 8300 },
  8360: { name: "Grimoire descellé", slug: "unsealedspellbook", tree: 8300 },
  8358: { name: "Initiative", slug: "firststrike", tree: 8300 },
};

export const LANE_TO_ROLE: Record<string, string> = {
  TOP: "top", JUNGLE: "jungle", MIDDLE: "mid", BOTTOM: "adc", UTILITY: "support",
};

export function spellIconUrl(spellId: number): string | null {
  const s = SUMMONER_SPELLS[spellId];
  return s ? `https://raw.communitydragon.org/latest/game/data/spells/icons2d/${s.slug}.png` : null;
}

export function keystoneIconUrl(perkId: number): string | null {
  const k = KEYSTONES[perkId];
  if (!k) return null;
  const tree = RUNE_TREES[k.tree];
  return `https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perk-images/styles/${tree.slug}/${k.slug}/${k.slug}.png`;
}

export function treeIconUrl(styleId: number): string | null {
  // The tree-level icon filenames on CommunityDragon don't follow the
  // {slug}/{slug}.png pattern the keystones use -- only Precision (7201)
  // and Domination (7200) were confirmed live in this project so far.
  // Unconfirmed trees fall back to null (icon hidden, name still shows)
  // rather than guessing a filename that might 404.
  const confirmed: Record<number, string> = { 8000: "7201_precision", 8100: "7200_domination" };
  const file = confirmed[styleId];
  return file ? `https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perk-images/styles/${file}.png` : null;
}

export function itemIconUrl(itemId: number): string | null {
  if (!itemId) return null;
  return `https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/items/icons2d/${itemId}.png`;
}

// Emblème de rang réel (verified pattern, already used by the TFT side of
// the site) -- clé = le tier tel que renvoyé par League-V4, en minuscules.
export function rankEmblemUrl(tier: string | null | undefined): string | null {
  if (!tier) return null;
  return `https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/images/ranked-emblem/emblem-${tier.toLowerCase()}.png`;
}

// Approximate per-tier per-minute benchmarks -- NOT sourced from Riot (they
// don't expose this), and not yet from BrokenMeta's own aggregated match
// data either (that would need the same kind of large-scale collection
// pipeline run.py already does for TFT, not built for LoL yet). These are
// rough, defensible reference points to compare a looked-up player against,
// clearly weaker than the real per-comp benchmarks.json the TFT side has.
// Replace with real aggregated numbers once enough LoL matches are
// collected through this same worker.
export const RANK_AVERAGES_BY_TIER: Record<string, { csPerMin: number; goldPerMin: number; dmgPerMin: number; killParticipation: number }> = {
  IRON: { csPerMin: 4.2, goldPerMin: 320, dmgPerMin: 380, killParticipation: 48 },
  BRONZE: { csPerMin: 4.8, goldPerMin: 345, dmgPerMin: 410, killParticipation: 50 },
  SILVER: { csPerMin: 5.4, goldPerMin: 365, dmgPerMin: 440, killParticipation: 52 },
  GOLD: { csPerMin: 6.0, goldPerMin: 385, dmgPerMin: 470, killParticipation: 54 },
  PLATINUM: { csPerMin: 6.6, goldPerMin: 405, dmgPerMin: 505, killParticipation: 56 },
  EMERALD: { csPerMin: 7.1, goldPerMin: 425, dmgPerMin: 540, killParticipation: 58 },
  DIAMOND: { csPerMin: 7.7, goldPerMin: 445, dmgPerMin: 580, killParticipation: 60 },
  MASTER: { csPerMin: 8.2, goldPerMin: 460, dmgPerMin: 610, killParticipation: 61 },
  GRANDMASTER: { csPerMin: 8.5, goldPerMin: 470, dmgPerMin: 630, killParticipation: 62 },
  CHALLENGER: { csPerMin: 8.6, goldPerMin: 460, dmgPerMin: 640, killParticipation: 62 },
};
