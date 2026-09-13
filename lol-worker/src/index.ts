// LoL worker: the real-data backend for BrokenMeta.gg's League of Legends
// profile page. Looks up a Riot ID live via the Riot LoL API and returns
// rank + a real match history + role/queue/activity stats computed
// server-side, ready for the page to render -- same shape of contract as
// metascope-worker's /profile for TFT.
//
// Two things this endpoint deliberately does NOT return, because Riot does
// not expose them at all: per-game ping counts and chat messages. The
// front-end keeps its illustrative mock for those two sections, clearly
// labeled "en développement" -- see league_profile.html.
//
// Uses a Riot DEVELOPMENT key (RIOT_API_KEY_LOL secret) while waiting on a
// Production key application -- which is the whole point of getting this
// live. Two consequences of that while it lasts:
//   1. The key expires every 24h and needs manual rotation (same gap the
//      TFT worker already has -- see the project's own notes on that).
//   2. Rate limits are tight (20 req/1s, 100 req/2min) -- one profile
//      lookup fetches MATCHES_PER_QUEUE * 2 queues + ~4 setup calls, done
//      SEQUENTIALLY on purpose (see fetchMatchesSequential) rather than in
//      parallel, to stay under the per-second cap. That makes a lookup
//      take a few seconds; there is no way around that on a dev key.
import { RiotClient, REGIONS, QUEUE_SOLO, QUEUE_FLEX } from "./riot";
import { SUMMONER_SPELLS, KEYSTONES, RUNE_TREES, LANE_TO_ROLE, RANK_AVERAGES_BY_TIER, spellIconUrl, keystoneIconUrl, treeIconUrl, itemIconUrl } from "./lolData";

export interface Env {
  RIOT_API_KEY_LOL: string;
  CORS_ORIGIN: string;
}

// Kept low deliberately -- see the rate-limit note above. 20 matches is
// already ~20 sequential calls per queue; bumping this multiplies lookup
// time and risk of a 429 linearly.
const MATCHES_PER_QUEUE = 20;
const WEEKDAY_LABELS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];

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
  const client = new RiotClient(env.RIOT_API_KEY_LOL);

  const account = await client.getAccountByRiotId(regional, gameName.trim(), tagLine.trim());
  if (!account) return json({ error: "Joueur introuvable avec ce Riot ID sur cette région." }, 404, origin);
  const puuid = account.puuid;

  const [summoner, leagueEntries] = await Promise.all([
    client.getSummonerByPuuid(platform, puuid),
    client.getLeagueEntriesByPuuid(platform, puuid),
  ]);
  const soloEntry = leagueEntries.find((e) => e.queueType === "RANKED_SOLO_5x5") || null;
  const flexEntry = leagueEntries.find((e) => e.queueType === "RANKED_FLEX_SR") || null;

  // Un seul pool de match ids couvrant les deux queues, tirés une fois puis
  // triés par queueId -- moins d'appels que de demander les ids séparément
  // par queue (l'endpoint by-puuid ne filtre pas par queue sur Match-V5).
  const matchIds = await client.getMatchIdsByPuuid(regional, puuid, MATCHES_PER_QUEUE * 2);
  const matches = await fetchMatchesSequential(client, regional, matchIds, puuid);

  const soloMatches = matches.filter((m) => m.queueId === QUEUE_SOLO);
  const flexMatches = matches.filter((m) => m.queueId === QUEUE_FLEX);

  const tierForAverages = (soloEntry?.tier || flexEntry?.tier || "GOLD").toUpperCase();
  const rankAverages = RANK_AVERAGES_BY_TIER[tierForAverages] || RANK_AVERAGES_BY_TIER.GOLD;

  return json({
    riotId: `${account.gameName}#${account.tagLine}`, region,
    profileIconId: summoner?.profileIconId ?? null, summonerLevel: summoner?.summonerLevel ?? null,
    ranks: { solo: soloEntry, flex: flexEntry },
    rankAverages,
    queues: {
      solo: buildQueueBlock(soloMatches, puuid),
      flex: buildQueueBlock(flexMatches, puuid),
    },
  }, 200, origin);
}

// Riot's dev-key rate limit (20 req/1s) is tight enough that fetching 40
// match details in parallel risks a 429 mid-burst. Sequential is slower
// (a few seconds for a full lookup) but reliable -- the right trade-off
// for a low-traffic beta page, not a production-scale one.
type ExtractedMatch = NonNullable<ReturnType<typeof extractMatch>>;

async function fetchMatchesSequential(client: RiotClient, regional: string, matchIds: string[], puuid: string): Promise<ExtractedMatch[]> {
  const out: ExtractedMatch[] = [];
  for (const id of matchIds) {
    const match = await client.getMatch(regional, id);
    if (!match) continue;
    const extracted = extractMatch(match, puuid);
    if (extracted) out.push(extracted);
  }
  return out;
}

function extractMatch(match: any, puuid: string) {
  const info = match.info;
  if (!info) return null;
  const participants: any[] = info.participants || [];
  const me = participants.find((p) => p.puuid === puuid);
  if (!me) return null;

  const durationMin = Math.max(1, info.gameDuration / 60);
  const teamKills = participants.filter((p) => p.teamId === me.teamId).reduce((s, p) => s + p.kills, 0) || 1;
  const cs = (me.totalMinionsKilled || 0) + (me.neutralMinionsKilled || 0);
  const primaryStyle = me.perks?.styles?.[0];
  const subStyle = me.perks?.styles?.[1];
  const keystoneId = primaryStyle?.selections?.[0]?.perk ?? null;

  const teammates = participants
    .filter((p) => p.teamId === me.teamId && p.puuid !== puuid)
    .map((p) => ({ puuid: p.puuid, riotId: p.riotIdGameName ? `${p.riotIdGameName}#${p.riotIdTagline}` : p.summonerName || "Joueur inconnu" }));

  const startedAt = info.gameStartTimestamp || match.info.gameCreation;
  const d = new Date(startedAt);
  // getDay(): 0=Dim..6=Sam -- décalé pour retomber sur l'ordre Lun..Dim
  // utilisé partout ailleurs sur le site (WEEKDAY_LABELS).
  const weekday = (d.getUTCDay() + 6) % 7;

  return {
    matchId: match.metadata.matchId, queueId: info.queueId, win: !!me.win,
    champion: me.championName, role: LANE_TO_ROLE[me.individualPosition] || "mid",
    kills: me.kills, deaths: me.deaths, assists: me.assists, cs,
    durationMin: Math.round(durationMin * 10) / 10,
    goldPerMin: Math.round((me.goldEarned || 0) / durationMin),
    dmgPerMin: Math.round((me.totalDamageDealtToChampions || 0) / durationMin),
    killParticipation: Math.round(((me.kills + me.assists) / teamKills) * 100),
    items: [me.item0, me.item1, me.item2, me.item3, me.item4, me.item5, me.item6].map((id) => ({ id, iconUrl: itemIconUrl(id) })),
    spells: [me.summoner1Id, me.summoner2Id].map((id) => ({ id, name: SUMMONER_SPELLS[id]?.name || "?", iconUrl: spellIconUrl(id) })),
    runes: {
      keystoneId, keystoneName: keystoneId ? KEYSTONES[keystoneId]?.name || "?" : null, keystoneIconUrl: keystoneId ? keystoneIconUrl(keystoneId) : null,
      secondaryStyleId: subStyle?.style ?? null, secondaryStyleName: subStyle ? RUNE_TREES[subStyle.style]?.name || "?" : null, secondaryStyleIconUrl: subStyle ? treeIconUrl(subStyle.style) : null,
    },
    teammates,
    startedAt, weekday, hour: d.getUTCHours(),
  };
}

function buildQueueBlock(matches: ExtractedMatch[], puuid: string) {
  const roleMap: Record<string, { role: string; games: number; wins: number }> = {};
  const weekday = WEEKDAY_LABELS.map((label, idx) => ({ label, idx, games: 0, wins: 0 }));
  const hourly = Array.from({ length: 24 }, (_, hour) => ({ hour, games: 0, wins: 0 }));
  const teammateMap: Record<string, { riotId: string; games: number; wins: number }> = {};
  let csSum = 0, goldSum = 0, dmgSum = 0, kpSum = 0;

  for (const m of matches) {
    if (!roleMap[m.role]) roleMap[m.role] = { role: m.role, games: 0, wins: 0 };
    roleMap[m.role].games++;
    if (m.win) roleMap[m.role].wins++;
    weekday[m.weekday].games++;
    if (m.win) weekday[m.weekday].wins++;
    hourly[m.hour].games++;
    if (m.win) hourly[m.hour].wins++;
    csSum += m.cs / m.durationMin;
    goldSum += m.goldPerMin;
    dmgSum += m.dmgPerMin;
    kpSum += m.killParticipation;
    for (const t of m.teammates) {
      if (!teammateMap[t.puuid]) teammateMap[t.puuid] = { riotId: t.riotId, games: 0, wins: 0 };
      teammateMap[t.puuid].games++;
      if (m.win) teammateMap[t.puuid].wins++;
    }
  }

  const n = matches.length || 1;
  const roleStats = Object.values(roleMap)
    .map((r) => ({ ...r, wr: Math.round((r.wins / r.games) * 100) }))
    .sort((a, b) => b.games - a.games);
  const weekdayStats = weekday.map((d) => ({ ...d, wr: d.games ? Math.round((d.wins / d.games) * 100) : 0 }));
  const hourlyStats = hourly.map((h) => ({ ...h, wr: h.games ? Math.round((h.wins / h.games) * 100) : 0 }));
  const playedWith = Object.values(teammateMap)
    .map((t) => ({ ...t, wr: Math.round((t.wins / t.games) * 100) }))
    .sort((a, b) => b.games - a.games)
    .slice(0, 3);

  return {
    matches: matches.map(({ teammates, ...rest }) => rest),
    roleStats, weekdayStats, hourlyStats, playedWith,
    statsAvg: { csPerMin: csSum / n, goldPerMin: goldSum / n, dmgPerMin: dmgSum / n, killParticipation: kpSum / n },
  };
}
