// Numeric champion id -> real Data Dragon champion id (e.g. 103 -> "Ahri",
// 62 -> "MonkeyKing") -- needed only for Spectator-V5, which gives
// numeric championId (unlike Match-V5's extractMatch(), which already
// gets the human-readable championName string directly and never needed
// this table). Same cache-then-fetch shape as itemData.ts's
// getItemIconMap(): edge-cached via the Cache API, isolate-local memory
// cache on top for warm requests.
const VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json";
// Longer than itemData.ts's 1h -- the champion roster/ddragon version
// changes at most every couple of weeks (a patch), so a longer TTL
// mostly just means fewer cold-cache misses (each one costs 2 extra
// subrequests on whatever profile lookup triggers it -- see index.ts).
const CACHE_TTL_SECONDS = 21600; // 6h

interface DDragonChampion { id: string; key: string; }

let memoryMap: { map: Record<number, string>; expires: number } | null = null;

async function getLatestVersion(): Promise<string | null> {
  const cache = caches.default;
  const cacheKey = new Request(VERSIONS_URL);
  const cached = await cache.match(cacheKey);
  if (cached) return (await cached.text()) || null;
  const resp = await fetch(VERSIONS_URL);
  if (!resp.ok) return null;
  const versions = (await resp.json()) as string[];
  const version = versions[0] || null;
  if (version) {
    const cacheable = new Response(version, { headers: { "Cache-Control": `public, max-age=${CACHE_TTL_SECONDS}` } });
    cache.put(cacheKey, cacheable).catch(() => {});
  }
  return version;
}

export async function getChampionIdMap(): Promise<Record<number, string>> {
  const now = Date.now();
  if (memoryMap && memoryMap.expires > now) return memoryMap.map;

  const version = await getLatestVersion();
  const map: Record<number, string> = {};
  if (version) {
    const url = `https://ddragon.leagueoflegends.com/cdn/${version}/data/en_US/champion.json`;
    const cache = caches.default;
    const cacheKey = new Request(url);
    let champions: Record<string, DDragonChampion> | null = null;
    const cached = await cache.match(cacheKey);
    if (cached) {
      const parsed = (await cached.json()) as { data?: Record<string, DDragonChampion> };
      champions = parsed?.data ?? null;
    } else {
      const resp = await fetch(url);
      if (resp.ok) {
        const cloned = resp.clone();
        const parsed = (await resp.json()) as { data?: Record<string, DDragonChampion> };
        champions = parsed?.data ?? null;
        const withTtl = new Response(cloned.body, cloned);
        withTtl.headers.set("Cache-Control", `public, max-age=${CACHE_TTL_SECONDS}`);
        cache.put(cacheKey, withTtl).catch(() => {});
      }
    }
    if (champions) {
      for (const champ of Object.values(champions)) map[Number(champ.key)] = champ.id;
    }
  }
  memoryMap = { map, expires: now + CACHE_TTL_SECONDS * 1000 };
  return map;
}
