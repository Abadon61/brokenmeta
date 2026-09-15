// Real summoner spell / rune icon + name lookups from CommunityDragon and
// Data Dragon. Replaces lolData.ts's old static SUMMONER_SPELLS/KEYSTONES/
// RUNE_TREES tables and their icon-URL builders: those were hand-typed
// from memory (see that file's own comment admitting as much) and turned
// out to be wrong for several real spells/runes once actually checked --
// e.g. Ignite's real file is "SummonerIgnite.png", not the guessed
// "summonerdot.png"; Aftershock's real folder is "VeteranAftershock", not
// "aftershock". Same fetch-then-cache shape as itemData.ts/championData.ts
// (edge-cached via the Cache API, isolate-local memory cache on top).
const SUMMONER_SPELLS_URL = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/summoner-spells.json";
const PERKS_URL = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json";
const CACHE_TTL_SECONDS = 21600; // 6h -- these barely change between patches

export interface IconRef { name: string; iconUrl: string | null; }

interface CDragonSpell { id: number; name: string; iconPath?: string; }
interface CDragonPerk { id: number; name: string; iconPath?: string; }

function cdragonUrl(iconPath: string | undefined): string | null {
  if (!iconPath) return null;
  const rel = iconPath.replace(/^\/lol-game-data\/assets\//i, "").toLowerCase();
  return `https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/${rel}`;
}

async function fetchJsonCached<T>(url: string): Promise<T | null> {
  const cache = caches.default;
  const cacheKey = new Request(url);
  const cached = await cache.match(cacheKey);
  if (cached) return (await cached.json()) as T;
  const resp = await fetch(url);
  if (!resp.ok) return null;
  const cloned = resp.clone();
  const data = (await resp.json()) as T;
  const withTtl = new Response(cloned.body, cloned);
  withTtl.headers.set("Cache-Control", `public, max-age=${CACHE_TTL_SECONDS}`);
  cache.put(cacheKey, withTtl).catch(() => {});
  return data;
}

let spellMemo: { map: Record<number, IconRef>; expires: number } | null = null;
export async function getSpellMap(): Promise<Record<number, IconRef>> {
  const now = Date.now();
  if (spellMemo && spellMemo.expires > now) return spellMemo.map;
  const spells = await fetchJsonCached<CDragonSpell[]>(SUMMONER_SPELLS_URL);
  const map: Record<number, IconRef> = {};
  for (const s of spells || []) map[s.id] = { name: s.name, iconUrl: cdragonUrl(s.iconPath) };
  spellMemo = { map, expires: now + CACHE_TTL_SECONDS * 1000 };
  return map;
}

let perkMemo: { map: Record<number, IconRef>; expires: number } | null = null;
export async function getPerkMap(): Promise<Record<number, IconRef>> {
  const now = Date.now();
  if (perkMemo && perkMemo.expires > now) return perkMemo.map;
  const perks = await fetchJsonCached<CDragonPerk[]>(PERKS_URL);
  const map: Record<number, IconRef> = {};
  for (const p of perks || []) map[p.id] = { name: p.name, iconUrl: cdragonUrl(p.iconPath) };
  perkMemo = { map, expires: now + CACHE_TTL_SECONDS * 1000 };
  return map;
}

// The 5 rune TREE icons (Precision/Domination/.../ id 8000-8400) aren't in
// perks.json at all (that file only has individual runes/keystones) --
// Data Dragon's runesReforged.json is the real source for those, keyed by
// the same tree ids. Needs a ddragon version, resolved the same way
// championData.ts does (kept independent on purpose: this file has no
// dependency on champion data, and the tiny extra versions.json fetch is
// itself Cache-API'd so it's shared/free across both once either warms it).
async function getLatestDdragonVersion(): Promise<string | null> {
  const cache = caches.default;
  const url = "https://ddragon.leagueoflegends.com/api/versions.json";
  const cacheKey = new Request(url);
  const cached = await cache.match(cacheKey);
  if (cached) return (await cached.text()) || null;
  const resp = await fetch(url);
  if (!resp.ok) return null;
  const versions = (await resp.json()) as string[];
  const version = versions[0] || null;
  if (version) {
    cache.put(cacheKey, new Response(version, { headers: { "Cache-Control": `public, max-age=${CACHE_TTL_SECONDS}` } })).catch(() => {});
  }
  return version;
}

let treeMemo: { map: Record<number, IconRef>; expires: number } | null = null;
export async function getRuneTreeMap(): Promise<Record<number, IconRef>> {
  const now = Date.now();
  if (treeMemo && treeMemo.expires > now) return treeMemo.map;
  const version = await getLatestDdragonVersion();
  const map: Record<number, IconRef> = {};
  if (version) {
    const trees = await fetchJsonCached<{ id: number; name: string; icon: string }[]>(
      `https://ddragon.leagueoflegends.com/cdn/${version}/data/en_US/runesReforged.json`
    );
    for (const t of trees || []) map[t.id] = { name: t.name, iconUrl: `https://ddragon.leagueoflegends.com/cdn/img/${t.icon}` };
  }
  treeMemo = { map, expires: now + CACHE_TTL_SECONDS * 1000 };
  return map;
}
