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
import { RiotClient, REGIONS, QUEUE_SOLO, QUEUE_FLEX, QUEUE_ARAM, RiotLeagueItem } from "./riot";
import { SUMMONER_SPELLS, KEYSTONES, RUNE_TREES, LANE_TO_ROLE, RANK_AVERAGES_BY_TIER, spellIconUrl, keystoneIconUrl, treeIconUrl, rankEmblemUrl } from "./lolData";
import { getItemIconMap } from "./itemData";

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
      if (url.pathname === "/leaderboard") return await handleLeaderboard(url, env, origin);
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

  // Chargé une fois, en parallèle du reste -- ne dépend ni du compte ni
  // de la région, et sert à corriger l'URL de CHAQUE objet de CHAQUE
  // partie plus bas (voir itemData.ts pour pourquoi un id seul ne suffit
  // pas à construire l'URL d'icône).
  const [summoner, leagueEntries, itemIconMap] = await Promise.all([
    client.getSummonerByPuuid(platform, puuid),
    client.getLeagueEntriesByPuuid(platform, puuid),
    getItemIconMap(),
  ]);
  const soloEntry = leagueEntries.find((e) => e.queueType === "RANKED_SOLO_5x5") || null;
  const flexEntry = leagueEntries.find((e) => e.queueType === "RANKED_FLEX_SR") || null;

  // Un seul pool de match ids couvrant les trois queues, tirés une fois puis
  // triés par queueId -- moins d'appels que de demander les ids séparément
  // par queue (l'endpoint by-puuid ne filtre pas par queue sur Match-V5).
  // L'ARAM était déjà présent dans ce même pool et silencieusement jeté --
  // aucun appel API supplémentaire pour l'exposer.
  const matchIds = await client.getMatchIdsByPuuid(regional, puuid, MATCHES_PER_QUEUE * 2);
  const matches = await fetchMatchesSequential(client, regional, matchIds, puuid, itemIconMap);

  const soloMatches = matches.filter((m) => m.queueId === QUEUE_SOLO);
  const flexMatches = matches.filter((m) => m.queueId === QUEUE_FLEX);
  const aramMatches = matches.filter((m) => m.queueId === QUEUE_ARAM);

  const tierForAverages = (soloEntry?.tier || flexEntry?.tier || "GOLD").toUpperCase();
  const rankAverages = RANK_AVERAGES_BY_TIER[tierForAverages] || RANK_AVERAGES_BY_TIER.GOLD;

  return json({
    riotId: `${account.gameName}#${account.tagLine}`, region,
    profileIconId: summoner?.profileIconId ?? null, summonerLevel: summoner?.summonerLevel ?? null,
    ranks: {
      solo: soloEntry ? { ...soloEntry, emblemUrl: rankEmblemUrl(soloEntry.tier) } : null,
      flex: flexEntry ? { ...flexEntry, emblemUrl: rankEmblemUrl(flexEntry.tier) } : null,
    },
    rankAverages,
    queues: {
      solo: buildQueueBlock(soloMatches, puuid),
      flex: buildQueueBlock(flexMatches, puuid),
      aram: buildQueueBlock(aramMatches, puuid),
    },
  }, 200, origin);
}

// Real Challenger/Grandmaster/Master ladder -- unlike the TFT tier list
// (built offline by run.py from a large sampled collection), this is
// cheap enough to compute live: the 3 apex-tier endpoints return their
// FULL real ladder in one call each, no sampling needed. The one real
// cost is that they return summonerId, not puuid or a Riot ID (a genuine
// Riot API inconsistency -- the per-player /entries/by-puuid endpoint
// used elsewhere in this file DOES give puuid directly) -- so each of
// the top LEADERBOARD_SIZE entries needs 2 more calls (summoner-by-id
// for its puuid, then account-by-puuid for the real name) to show a
// real name instead of just a rank + LP. Edge-cached
// (LEADERBOARD_CACHE_TTL) so that cost is paid once per region per
// cache window, not once per visitor.
const LEADERBOARD_SIZE = 20;
const LEADERBOARD_CACHE_TTL = 900; // 15 min

async function handleLeaderboard(url: URL, env: Env, origin: string): Promise<Response> {
  const region = parseRegion(url.searchParams.get("region"));
  if (!region) return json({ error: "Région inconnue." }, 400, origin);
  const { platform, regional } = REGIONS[region];

  const cache = caches.default;
  const cacheKey = new Request(`https://lol-worker.internal/leaderboard-cache?region=${region}`);
  const cached = await cache.match(cacheKey);
  if (cached) {
    const fresh = new Response(cached.body, cached);
    Object.entries(corsHeaders(origin)).forEach(([k, v]) => fresh.headers.set(k, v));
    return fresh;
  }

  const client = new RiotClient(env.RIOT_API_KEY_LOL);
  const [challenger, grandmaster, master] = await Promise.all([
    client.getChallengerLeague(platform, "RANKED_SOLO_5x5"),
    client.getGrandmasterLeague(platform, "RANKED_SOLO_5x5"),
    client.getMasterLeague(platform, "RANKED_SOLO_5x5"),
  ]);

  const all: (RiotLeagueItem & { tier: string })[] = [
    ...(challenger?.entries || []).map((e) => ({ ...e, tier: "CHALLENGER" })),
    ...(grandmaster?.entries || []).map((e) => ({ ...e, tier: "GRANDMASTER" })),
    ...(master?.entries || []).map((e) => ({ ...e, tier: "MASTER" })),
  ];
  all.sort((a, b) => b.leaguePoints - a.leaguePoints);
  const top = all.slice(0, LEADERBOARD_SIZE);

  // Sequential, same rate-limit reasoning as fetchMatchesSequential below
  // -- this is already a bounded ~40 calls (2 per entry) for the whole
  // region, comfortably inside one rate-limit window.
  const entries: { rank: number; riotId: string | null; tier: string; leaguePoints: number; wins: number; losses: number; hotStreak: boolean }[] = [];
  let rank = 0;
  for (const item of top) {
    rank++;
    const summoner = await client.getSummonerById(platform, item.summonerId);
    if (!summoner) continue;
    const account = await client.getAccountByPuuid(regional, summoner.puuid);
    entries.push({
      rank, riotId: account ? `${account.gameName}#${account.tagLine}` : null,
      tier: item.tier, leaguePoints: item.leaguePoints, wins: item.wins, losses: item.losses, hotStreak: item.hotStreak,
    });
  }

  const resp = json({ region, updatedAt: Date.now(), entries }, 200, origin);
  const cacheable = new Response(resp.body, resp);
  cacheable.headers.set("Cache-Control", `public, max-age=${LEADERBOARD_CACHE_TTL}`);
  await cache.put(cacheKey, cacheable.clone());
  return cacheable;
}

// Riot's dev-key rate limit (20 req/1s) is tight enough that fetching 40
// match details in parallel risks a 429 mid-burst. Sequential is slower
// (a few seconds for a full lookup) but reliable -- the right trade-off
// for a low-traffic beta page, not a production-scale one.
type ExtractedMatch = NonNullable<ReturnType<typeof extractMatch>>;

async function fetchMatchesSequential(client: RiotClient, regional: string, matchIds: string[], puuid: string, itemIconMap: Record<number, string>): Promise<ExtractedMatch[]> {
  const out: ExtractedMatch[] = [];
  for (const id of matchIds) {
    const match = await client.getMatch(regional, id);
    if (!match) continue;
    const extracted = extractMatch(match, puuid, itemIconMap);
    if (extracted) out.push(extracted);
  }
  return out;
}

function extractMatch(match: any, puuid: string, itemIconMap: Record<number, string>) {
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

  // Les 10 joueurs, pour le volet "voir la partie" -- même info que la
  // ligne repliée mais pour tout le monde, plus l'or et les 6 objets.
  // Généré ici pour chaque partie (coût déjà payé, `participants` est
  // déjà en mémoire) plutôt que recalculé côté client.
  const scoreboard = participants.map((p) => ({
    puuid: p.puuid, isSelf: p.puuid === puuid, team: p.teamId === me.teamId ? "ally" : "enemy",
    name: p.puuid === puuid ? null : (p.riotIdGameName ? `${p.riotIdGameName}#${p.riotIdTagline}` : p.summonerName || "Joueur inconnu"),
    champion: p.championName, role: LANE_TO_ROLE[p.individualPosition] || "mid",
    kills: p.kills, deaths: p.deaths, assists: p.assists,
    cs: (p.totalMinionsKilled || 0) + (p.neutralMinionsKilled || 0), gold: p.goldEarned || 0,
    items: [p.item0, p.item1, p.item2, p.item3, p.item4, p.item5, p.item6].map((id: number) => ({ id, iconUrl: itemIconMap[id] || null })),
  }));

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
    items: [me.item0, me.item1, me.item2, me.item3, me.item4, me.item5, me.item6].map((id) => ({ id, iconUrl: itemIconMap[id] || null })),
    spells: [me.summoner1Id, me.summoner2Id].map((id) => ({ id, name: SUMMONER_SPELLS[id]?.name || "?", iconUrl: spellIconUrl(id) })),
    runes: {
      keystoneId, keystoneName: keystoneId ? KEYSTONES[keystoneId]?.name || "?" : null, keystoneIconUrl: keystoneId ? keystoneIconUrl(keystoneId) : null,
      secondaryStyleId: subStyle?.style ?? null, secondaryStyleName: subStyle ? RUNE_TREES[subStyle.style]?.name || "?" : null, secondaryStyleIconUrl: subStyle ? treeIconUrl(subStyle.style) : null,
    },
    teammates, scoreboard,
    startedAt, weekday, hour: d.getUTCHours(),
  };
}

function buildQueueBlock(matches: ExtractedMatch[], puuid: string) {
  const roleMap: Record<string, { role: string; games: number; wins: number }> = {};
  const weekday = WEEKDAY_LABELS.map((label, idx) => ({ label, idx, games: 0, wins: 0 }));
  const hourly = Array.from({ length: 24 }, (_, hour) => ({ hour, games: 0, wins: 0 }));
  const teammateMap: Record<string, { riotId: string; games: number; wins: number }> = {};
  const champMap: Record<string, { champ: string; games: number; wins: number; kills: number; deaths: number; assists: number }> = {};
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
    if (!champMap[m.champion]) champMap[m.champion] = { champ: m.champion, games: 0, wins: 0, kills: 0, deaths: 0, assists: 0 };
    const c = champMap[m.champion];
    c.games++;
    if (m.win) c.wins++;
    c.kills += m.kills; c.deaths += m.deaths; c.assists += m.assists;
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
  const champions = Object.values(champMap)
    .map((c) => ({
      champ: c.champ, games: c.games, wr: Math.round((c.wins / c.games) * 100),
      avgKills: Math.round((c.kills / c.games) * 10) / 10, avgDeaths: Math.round((c.deaths / c.games) * 10) / 10, avgAssists: Math.round((c.assists / c.games) * 10) / 10,
      kda: Math.round(((c.kills + c.assists) / Math.max(1, c.deaths)) * 10) / 10,
    }))
    .sort((a, b) => b.games - a.games);

  return {
    matches: matches.map(({ teammates, ...rest }) => rest),
    roleStats, weekdayStats, hourlyStats, playedWith, champions,
    statsAvg: { csPerMin: csSum / n, goldPerMin: goldSum / n, dmgPerMin: dmgSum / n, killParticipation: kpSum / n },
  };
}
