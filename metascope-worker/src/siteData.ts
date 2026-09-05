// Fetches the small data files build_site.py publishes specifically for
// this worker (see build_site.py's "MetaScope worker data" section) --
// keeps this worker's comp knowledge in lockstep with the static site's own
// numbers instead of a copy that can silently drift. Cached at Cloudflare's
// edge (Cache API) for a short TTL so a burst of lookups doesn't refetch
// ~2MB of JSON per request; a stale cache just means a few minutes' lag
// behind the last site rebuild, never wrong data.
import type { Benchmark } from "./analysis";

const CACHE_TTL_SECONDS = 600;

export interface SiteData {
  nameMap: Record<string, string>;
  itemOffense: Record<string, string>;
  benchmarks: Record<string, Benchmark>;
  compIndex: Record<string, { slug: string; display_label: string }>;
  matchupLookup: Map<string, { aheadRate: number; encounters: number }>;
}

async function fetchJson<T>(base: string, path: string): Promise<T> {
  const url = `${base}/assets/data/${path}`;
  const cache = caches.default;
  const cacheKey = new Request(url);
  const cached = await cache.match(cacheKey);
  if (cached) return cached.json();

  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`Failed to fetch ${url}: ${resp.status}`);
  const cloned = resp.clone();
  const withTtl = new Response(cloned.body, cloned);
  withTtl.headers.set("Cache-Control", `public, max-age=${CACHE_TTL_SECONDS}`);
  // Not awaited on purpose -- caching is best-effort, the response itself
  // must not wait on it.
  cache.put(cacheKey, withTtl).catch(() => {});
  return resp.json();
}

export async function loadSiteData(base: string): Promise<SiteData> {
  const [nameMap, itemOffense, benchmarks, compIndex, matchupsRaw] = await Promise.all([
    fetchJson<Record<string, string>>(base, "name-map.json"),
    fetchJson<Record<string, string>>(base, "item-offense.json"),
    fetchJson<Record<string, Benchmark>>(base, "benchmarks.json"),
    fetchJson<Record<string, { slug: string; display_label: string }>>(base, "comp-index.json"),
    fetchJson<Array<{ comp_a: string; comp_b: string; a_ahead_rate: number; b_ahead_rate: number; encounters: number }>>(base, "matchups.json"),
  ]);
  const matchupLookup = new Map<string, { aheadRate: number; encounters: number }>();
  for (const m of matchupsRaw) {
    matchupLookup.set(`${m.comp_a}|${m.comp_b}`, { aheadRate: m.a_ahead_rate, encounters: m.encounters });
    matchupLookup.set(`${m.comp_b}|${m.comp_a}`, { aheadRate: m.b_ahead_rate, encounters: m.encounters });
  }
  return { nameMap, itemOffense, benchmarks, compIndex, matchupLookup };
}
