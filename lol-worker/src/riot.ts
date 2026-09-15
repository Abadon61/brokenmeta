// Thin Riot LoL API client -- same shape as metascope-worker's riot.ts (TFT),
// separate file because it's a different game's endpoints and a different
// API key. No local disk cache (Workers are stateless/ephemeral); a single
// profile lookup is a bounded handful of requests, not a bulk collection run.

export const REGIONS: Record<string, { platform: string; regional: string }> = {
  EUW: { platform: "euw1", regional: "europe" },
  NA: { platform: "na1", regional: "americas" },
  BR: { platform: "br1", regional: "americas" },
  KR: { platform: "kr", regional: "asia" },
};

// Ranked queue ids (Riot's own constants, stable across seasons):
// https://static.developer.riotgames.com/docs/lol/queues.json
export const QUEUE_SOLO = 420;
export const QUEUE_FLEX = 440;
export const QUEUE_ARAM = 450;

export class RiotAPIError extends Error {
  status: number;
  constructor(status: number, url: string, body: string) {
    super(`Riot API ${status} on ${url}: ${body.slice(0, 300)}`);
    this.status = status;
  }
}

export interface RiotAccount { puuid: string; gameName: string; tagLine: string; }
export interface RiotSummoner { id: string; puuid: string; profileIconId: number; summonerLevel: number; }
export interface RiotLeagueEntry {
  queueType: string; tier: string; rank: string; leaguePoints: number;
  wins: number; losses: number; hotStreak: boolean; veteran: boolean;
}
// Bulk apex-tier endpoints (challenger/grandmaster/master) return this
// shape instead -- one tier for the WHOLE list, entries keyed by
// summonerId (not puuid, unlike RiotLeagueEntry above -- a real API
// inconsistency, not a mistake here) with no queueType per entry either.
export interface RiotLeagueItem {
  // Riot has been migrating summonerId out of its API surface in favor of
  // puuid (confirmed elsewhere, e.g. Spectator-V5) -- these bulk apex-tier
  // endpoints' exact current shape isn't reliably documented, so both are
  // optional here and the caller checks which one it actually got rather
  // than assuming.
  summonerId?: string; puuid?: string; leaguePoints: number; rank: string;
  wins: number; losses: number; hotStreak: boolean; veteran: boolean; freshBlood: boolean;
}
export interface RiotLeagueList { tier: string; name: string; entries: RiotLeagueItem[]; }

export class RiotClient {
  constructor(private apiKey: string) {}

  private async get<T>(url: string, retriesLeft = 2): Promise<T | null> {
    const resp = await fetch(url, { headers: { "X-Riot-Token": this.apiKey } });
    if (resp.status === 200) return (await resp.json()) as T;
    if (resp.status === 404) return null;
    if (resp.status === 429 && retriesLeft > 0) {
      // Riot always sends Retry-After on 429s -- honor it (capped, this is
      // a request-time wait, not a batch job) rather than failing a whole
      // leaderboard/profile lookup on one transient rate-limit hit.
      const retryAfter = Math.min(5, Number(resp.headers.get("Retry-After")) || 1);
      await new Promise((r) => setTimeout(r, retryAfter * 1000));
      return this.get<T>(url, retriesLeft - 1);
    }
    const body = await resp.text().catch(() => "");
    throw new RiotAPIError(resp.status, url, body);
  }

  getAccountByRiotId(regional: string, gameName: string, tagLine: string) {
    const url = `https://${regional}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}`;
    return this.get<RiotAccount>(url);
  }

  getAccountByPuuid(regional: string, puuid: string) {
    const url = `https://${regional}.api.riotgames.com/riot/account/v1/accounts/by-puuid/${puuid}`;
    return this.get<RiotAccount>(url);
  }

  getSummonerByPuuid(platform: string, puuid: string) {
    const url = `https://${platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/${puuid}`;
    return this.get<RiotSummoner>(url);
  }

  getSummonerById(platform: string, summonerId: string) {
    const url = `https://${platform}.api.riotgames.com/lol/summoner/v4/summoners/${summonerId}`;
    return this.get<RiotSummoner>(url);
  }

  getChallengerLeague(platform: string, queue: string) {
    const url = `https://${platform}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/${queue}`;
    return this.get<RiotLeagueList>(url);
  }

  getGrandmasterLeague(platform: string, queue: string) {
    const url = `https://${platform}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/${queue}`;
    return this.get<RiotLeagueList>(url);
  }

  getMasterLeague(platform: string, queue: string) {
    const url = `https://${platform}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/${queue}`;
    return this.get<RiotLeagueList>(url);
  }

  getLeagueEntriesByPuuid(platform: string, puuid: string) {
    const url = `https://${platform}.api.riotgames.com/lol/league/v4/entries/by-puuid/${puuid}`;
    return this.get<RiotLeagueEntry[]>(url).then((r) => r || []);
  }

  getMatchIdsByPuuid(regional: string, puuid: string, count: number) {
    const url = `https://${regional}.api.riotgames.com/lol/match/v5/matches/by-puuid/${puuid}/ids?start=0&count=${count}`;
    return this.get<string[]>(url).then((r) => r || []);
  }

  getMatch(regional: string, matchId: string) {
    const url = `https://${regional}.api.riotgames.com/lol/match/v5/matches/${matchId}`;
    return this.get<any>(url);
  }

  // Spectator-V5 (the "by-summoner" path segment is legacy naming --
  // Riot switched the actual identifier to puuid in V5, confirmed via
  // their own dev-relations announcement). 404 (not in game right now)
  // is the expected, common case -- returns null, not an error.
  getActiveGameByPuuid(platform: string, puuid: string) {
    const url = `https://${platform}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/${puuid}`;
    return this.get<any>(url);
  }
}
