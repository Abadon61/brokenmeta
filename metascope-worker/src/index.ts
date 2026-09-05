// MetaScope worker: the only live, per-request piece of BrokenMeta.gg.
// Everything else on the site is pre-built static HTML; this exists purely
// because looking up an ARBITRARY Riot ID typed by a visitor needs a live
// Riot API call, which a static site can't safely do (the key would have
// to live in the page's own JS, visible to anyone -- see the project's own
// notes on why analyze_app.py stayed a local-only tool for so long).
//
// Two endpoints, both real data, nothing fabricated:
//   GET /profile?riotId=Name%23TAG&region=EUW
//   GET /analyze?region=EUW&matchId=...&puuid=...
import { RiotClient, RANKED_TFT_QUEUE_ID, REGIONS } from "./riot";
import { deriveComp } from "./compSignature";
import { buildReport } from "./analysis";
import { loadSiteData } from "./siteData";

export interface Env {
  RIOT_API_KEY: string;
  CORS_ORIGIN: string;
  SITE_BASE: string;
}

const RECENT_GAMES = 10;

function slugify(name: string): string {
  const s = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  return s || "x";
}

function corsHeaders(origin: string): Record<string, string> {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

function json(data: unknown, status: number, origin: string): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders(origin) },
  });
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = env.CORS_ORIGIN;
    if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders(origin) });

    const url = new URL(request.url);
    try {
      if (url.pathname === "/profile") return await handleProfile(url, env, origin);
      if (url.pathname === "/analyze") return await handleAnalyze(url, env, origin);
      return json({ error: "Route inconnue." }, 404, origin);
    } catch (e: any) {
      const status = e?.status && Number.isInteger(e.status) ? 502 : 500;
      return json({ error: "Erreur interne. Réessaie dans un instant.", detail: String(e?.message || e) }, status, origin);
    }
  },
};

function parseRegion(raw: string | null): keyof typeof REGIONS | null {
  const region = (raw || "").toUpperCase();
  return region in REGIONS ? (region as keyof typeof REGIONS) : null;
}

async function handleProfile(url: URL, env: Env, origin: string): Promise<Response> {
  const riotId = (url.searchParams.get("riotId") || "").trim();
  const region = parseRegion(url.searchParams.get("region"));
  const [gameName, tagLine] = riotId.includes("#") ? riotId.split(/#(.*)/s) : [riotId, ""];
  if (!region || !gameName.trim() || !tagLine.trim()) {
    return json({ error: "Riot ID invalide (format Pseudo#TAG) ou région inconnue." }, 400, origin);
  }

  const { platform, regional } = REGIONS[region];
  const client = new RiotClient(env.RIOT_API_KEY);
  const account = await client.getAccountByRiotId(regional, gameName.trim(), tagLine.trim());
  if (!account) return json({ error: "Joueur introuvable avec ce Riot ID sur cette région." }, 404, origin);
  const puuid = account.puuid;

  const [leagueEntries, matchIds, siteData] = await Promise.all([
    client.getLeagueEntriesByPuuid(platform, puuid),
    client.getMatchIdsByPuuid(regional, puuid, RECENT_GAMES),
    loadSiteData(env.SITE_BASE),
  ]);
  const rankedEntry = (leagueEntries || []).find((e) => e.queueType === "RANKED_TFT") || null;

  const recentGames: any[] = [];
  const placements: number[] = [];
  for (const matchId of matchIds) {
    const match = await client.getMatch(regional, matchId);
    if (!match || match.info?.queueId !== RANKED_TFT_QUEUE_ID) continue;
    const participant = (match.info?.participants || []).find((p: any) => p.puuid === puuid);
    if (!participant?.placement) continue;
    const sig = deriveComp(participant, siteData.nameMap, siteData.itemOffense);
    placements.push(participant.placement);
    const indexed = siteData.compIndex[sig.key];
    recentGames.push({
      matchId, placement: participant.placement,
      compKey: sig.key, compLabel: indexed?.display_label || sig.label,
      compSlug: indexed?.slug || null, carry: sig.carry, carrySlug: sig.carry ? slugify(sig.carry) : null,
      isReroll: /reroll/i.test(sig.label),
    });
  }

  const avgPlacement = placements.length ? Math.round((placements.reduce((a, b) => a + b, 0) / placements.length) * 100) / 100 : null;
  const rerollGames = recentGames.filter((g) => g.isReroll).length;
  const isRerollLover = recentGames.length >= 5 && rerollGames / recentGames.length >= 0.5;
  const counts = new Map<string, number>();
  for (const g of recentGames) counts.set(g.compKey, (counts.get(g.compKey) || 0) + 1);
  const topPlayed = [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .filter(([, c]) => c >= 2)
    .slice(0, 2)
    .map(([key, count]) => {
      const sample = recentGames.find((g) => g.compKey === key);
      return { label: sample.compLabel, count, compSlug: sample.compSlug, carrySlug: sample.carrySlug };
    });

  return json({
    riotId: `${account.gameName}#${account.tagLine}`, region, puuid,
    tier: rankedEntry?.tier || null, leaguePoints: rankedEntry?.leaguePoints ?? null,
    wins: rankedEntry?.wins ?? null, losses: rankedEntry?.losses ?? null, hotStreak: !!rankedEntry?.hotStreak,
    avgPlacement, isRerollLover, topPlayed, recentGames,
  }, 200, origin);
}

async function handleAnalyze(url: URL, env: Env, origin: string): Promise<Response> {
  const region = parseRegion(url.searchParams.get("region"));
  const matchId = url.searchParams.get("matchId");
  const puuid = url.searchParams.get("puuid");
  if (!region || !matchId || !puuid) return json({ error: "Requête invalide." }, 400, origin);

  const { regional } = REGIONS[region];
  const client = new RiotClient(env.RIOT_API_KEY);
  const [match, siteData] = await Promise.all([client.getMatch(regional, matchId), loadSiteData(env.SITE_BASE)]);
  if (!match) return json({ error: "Partie introuvable." }, 404, origin);
  const participant = (match.info?.participants || []).find((p: any) => p.puuid === puuid);
  if (!participant) return json({ error: "Joueur non trouvé dans cette partie." }, 404, origin);

  const report = buildReport(participant, siteData.nameMap, siteData.benchmarks, match, puuid, siteData.matchupLookup, siteData.itemOffense);
  const indexed = siteData.compIndex[report.compKey];
  const units = report.units.map((u) => ({ ...u, slug: slugify(u.champion), items: u.items.map((n) => ({ name: n, slug: slugify(n) })) }));
  const lobby = report.lobby.map((l) => {
    const li = siteData.compIndex[l.compKey];
    return {
      ...l, compLabel: li?.display_label || l.compLabel, compSlug: li?.slug || null,
      carrySlug: l.carry ? slugify(l.carry) : null,
      isCounter: l.counterRate !== null && l.counterRate >= 0.55 && l.encounters >= 4,
    };
  });

  return json({
    compLabel: indexed?.display_label || report.compLabel, compSlug: indexed?.slug || null,
    carry: report.carry, carrySlug: report.carry ? slugify(report.carry) : null,
    placement: report.placement, level: report.level, goldLeft: report.goldLeft, lastRound: report.lastRound,
    units, insights: report.insights, lobby,
  }, 200, origin);
}
