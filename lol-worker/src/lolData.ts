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

