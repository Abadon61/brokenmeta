// Thin Riot API client -- Workers-runtime port of src/tft_tracker/riot_client.py.
// No local disk cache (Workers are stateless/ephemeral); relies on Riot's own
// rate limits and the fact that a single profile lookup is a handful of
// requests, not a bulk collection run like the Python pipeline's.

export const REGIONS: Record<string, { platform: string; regional: string }> = {
  EUW: { platform: "euw1", regional: "europe" },
  NA: { platform: "na1", regional: "americas" },
  BR: { platform: "br1", regional: "americas" },
  KR: { platform: "kr", regional: "asia" },
};

export const RANKED_TFT_QUEUE_ID = 1100;

export class RiotAPIError extends Error {
  status: number;
  constructor(status: number, url: string, body: string) {
    super(`Riot API ${status} on ${url}: ${body.slice(0, 300)}`);
    this.status = status;
  }
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
    return this.get<{ puuid: string; gameName: string; tagLine: string }>(url);
  }

  // Verified directly against the live API (2026-09-05) with a real key and
  // a real puuid, one real request, 200 OK -- a reference wrapper library's
  // source code suggested this route didn't exist for TFT (only an older
  // by-summoner one), which was WRONG (that library just hadn't caught up
  // with a real Riot API addition). Lesson: check the live endpoint, not a
  // third party's code, when the two disagree and a real key is on hand.
  getLeagueEntriesByPuuid(platform: string, puuid: string) {
    const url = `https://${platform}.api.riotgames.com/tft/league/v1/by-puuid/${puuid}`;
    return this.get<Array<{ queueType: string; tier: string; rank: string; leaguePoints: number; wins: number; losses: number; hotStreak: boolean }>>(url);
  }

  getMatchIdsByPuuid(regional: string, puuid: string, count = 15) {
    const url = `https://${regional}.api.riotgames.com/tft/match/v1/matches/by-puuid/${puuid}/ids?count=${count}`;
    return this.get<string[]>(url).then((r) => r || []);
  }

  getMatch(regional: string, matchId: string) {
    const url = `https://${regional}.api.riotgames.com/tft/match/v1/matches/${matchId}`;
    return this.get<any>(url);
  }
}
