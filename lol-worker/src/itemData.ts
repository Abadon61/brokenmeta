// Real item icon URLs -- unlike champion portraits (Data Dragon serves
// those directly by championName) or the summoner-spell/rune slugs we
// hardcoded in lolData.ts, LoL item icons on CommunityDragon are NOT at a
// predictable /items/icons2d/{id}.png path: item {id} 3071 lives at
// .../assets/items/icons2d/3071_fighter_t3_blackcleaver.png -- the numeric
// id plus the item's own name, lowercased. There is no way to build that
// URL from the id alone; it has to come from CommunityDragon's own
// items.json (each entry's iconPath field), which is what this module
// fetches and turns into a plain id -> icon URL map.
//
// Bug found live: the earlier itemIconUrl() in lolData.ts guessed
// {id}.png directly and 404'd for every real item, so every match row's
// item slots stayed empty. This replaces that guess with real data.
const ITEMS_URL = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/items.json";
const CACHE_TTL_SECONDS = 3600;

interface CDragonItem { id: number; iconPath?: string; }

// Warm-isolate memory cache on top of the Cache API below -- a bonus for
// requests that land on an already-warm Worker instance; the Cache API
// entry is what actually makes this reliable across isolates/regions.
let memoryMap: { map: Record<number, string>; expires: number } | null = null;

export async function getItemIconMap(): Promise<Record<number, string>> {
  const now = Date.now();
  if (memoryMap && memoryMap.expires > now) return memoryMap.map;

  const cache = caches.default;
  const cacheKey = new Request(ITEMS_URL);
  let items: CDragonItem[] | null = null;
  const cached = await cache.match(cacheKey);
  if (cached) {
    items = await cached.json();
  } else {
    const resp = await fetch(ITEMS_URL);
    if (resp.ok) {
      const cloned = resp.clone();
      items = await resp.json();
      const withTtl = new Response(cloned.body, cloned);
      withTtl.headers.set("Cache-Control", `public, max-age=${CACHE_TTL_SECONDS}`);
      // Best-effort -- a cache-put failure just means the next request
      // re-fetches, never a broken response for this one.
      cache.put(cacheKey, withTtl).catch(() => {});
    }
  }

  const map: Record<number, string> = {};
  if (items) {
    for (const it of items) {
      if (!it.iconPath) continue;
      const rel = it.iconPath.replace(/^\/lol-game-data\/assets\//i, "").toLowerCase();
      map[it.id] = `https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/${rel}`;
    }
  }
  memoryMap = { map, expires: now + CACHE_TTL_SECONDS * 1000 };
  return map;
}
