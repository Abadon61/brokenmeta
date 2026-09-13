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

export class RiotClient {
  constructor(private apiKey: string) {}

  private async get<T>(url: string): Promise<T | null> {
    const resp = await fetch(url, { headers: { "X-Riot-Token": this.apiKey } });
    if (resp.status === 200) return (await resp.json()) as T;
    if (resp.status === 404) return null;
    const body = await resp.text().catch(() => "");
    throw new RiotAPIError(resp.status, url, body);
  }

  getAccountByRiotId(regional: string, gameName: string, tagLine: string) {
    const url = `https://${regional}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}`;
    return this.get<RiotAccount>(url);
  }

  getSummonerByPuuid(platform: string, puuid: string) {
    const url = `https://${platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/${puuid}`;
    return this.get<RiotSummoner>(url);
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
}
