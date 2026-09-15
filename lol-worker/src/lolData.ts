// Summoner spell / rune name+icon lookups moved to spellsAndRunes.ts --
// this file's old static SUMMONER_SPELLS/RUNE_TREES/KEYSTONES tables were
// hand-typed from memory and turned out wrong for several real spells/
// runes once actually checked against CommunityDragon (e.g. Ignite's
// real file is "SummonerIgnite.png", not the guessed "summonerdot.png";
// Aftershock's real folder is "VeteranAftershock", not "aftershock").
// Same lesson as items below: a numeric id alone doesn't reliably predict
// CommunityDragon's filename, a real id -> iconPath lookup does.
export const LANE_TO_ROLE: Record<string, string> = {
  TOP: "top", JUNGLE: "jungle", MIDDLE: "mid", BOTTOM: "adc", UTILITY: "support",
};

// Item icons moved to itemData.ts -- a numeric id alone 404s (CommunityDragon
// needs the item's own filename, e.g. "3071_fighter_t3_blackcleaver.png"),
// so building the URL needs a real id -> iconPath lookup, not a guess here.

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
