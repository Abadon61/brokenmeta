// Compares a looked-up player with MEASURED rank averages (see
// src/tft_tracker/lol_pipeline.py: build_rank_averages), replacing the
// hand-written approximate table this worker used to ship. Averages are per
// tier AND role, so the expected value for a player is the mean of the value
// for the role of each game they actually played (a support isn't compared
// with the all-role vision average).
import { RANK_AVERAGES, RANK_AVERAGES_GENERATED_AT } from "./rankAveragesData";

const TIER_ORDER = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"];

export interface RankExpected {
  tier: string;          // the player's real tier
  comparedTo: string;    // the tier whose measured data was used
  approximate: boolean;  // true when the player's tier isn't sampled (compared with the closest sampled one)
  sample: number;        // participant rows behind the averages
  generatedAt: string;
  metrics: Record<string, number>;
}

export function expectedForRoles(tier: string | null | undefined, roles: string[]): RankExpected | null {
  if (!tier || !roles.length) return null;
  const upper = tier.toUpperCase();
  const collected = TIER_ORDER.filter((t) => RANK_AVERAGES[t]);
  if (!collected.length) return null;
  let used = upper;
  if (!RANK_AVERAGES[used]) {
    // Not sampled (Iron/Bronze/Silver): fall back to the closest sampled tier and say so.
    const idx = TIER_ORDER.indexOf(upper);
    used = collected.reduce((best, t) => (Math.abs(TIER_ORDER.indexOf(t) - idx) < Math.abs(TIER_ORDER.indexOf(best) - idx) ? t : best), collected[0]);
  }
  const entry = RANK_AVERAGES[used];
  const sums: Record<string, number> = {};
  for (const role of roles) {
    const row = entry[role] || entry.all;
    for (const [k, v] of Object.entries(row.metrics)) sums[k] = (sums[k] || 0) + v;
  }
  const metrics: Record<string, number> = {};
  for (const [k, v] of Object.entries(sums)) metrics[k] = Math.round((v / roles.length) * 100) / 100;
  return {
    tier: upper, comparedTo: used, approximate: used !== upper, sample: entry.all.n,
    generatedAt: RANK_AVERAGES_GENERATED_AT, metrics,
  };
}
