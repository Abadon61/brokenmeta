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

  // No TFT League-v1 "by puuid" shortcut exists (verified against Riot-
  // Watcher's own endpoint definitions, a well-maintained reference
  // wrapper) -- unlike some LoL v4 endpoints, TFT still needs the classic
  // 2-hop: puuid -> encryptedSummonerId (Summoner-v1), then that id ->
  // league entries (League-v1's by-summoner route).
  async getLeagueEntriesByPuuid(platform: string, puuid: string) {
    const summonerUrl = `https://${platform}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/${puuid}`;
    const summoner = await this.get<{ id: string }>(summonerUrl);
    if (!summoner?.id) return null;
    const leagueUrl = `https://${platform}.api.riotgames.com/tft/league/v1/entries/by-summoner/${summoner.id}`;
    return this.get<Array<{ queueType: string; tier: string; rank: string; leaguePoints: number; wins: number; losses: number; hotStreak: boolean }>>(leagueUrl);
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
