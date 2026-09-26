// wow-worker: receives the data players CHOOSE to share from the BrokenMeta WoW addon, through
// the site's /wow-forever/partager-mes-donnees/ page, and serves the aggregates the site is built
// from (auction prices for the profession guides, in-game measurements for the DPS simulator).
//
// Privacy by design (see the site's /confidentialite/ page):
//   - the page only ever sends BrokenMetaWeightsDB.data: no character name, no account;
//     auction scans keep realm + faction because prices only make sense per realm;
//   - every field is whitelisted and type/range-checked here, anything else is dropped;
//   - the raw IP is never stored: rate limiting uses a salted SHA-256 hash, purged after a day;
//   - each upload returns a one-time deletion code; DELETE /v1/submission erases that upload.
//
// Routes:
//   POST   /v1/submit       JSON { format: "BMD1", addon, client, meas: [...], ah: [...] }
//   DELETE /v1/submission   JSON { code }
//   GET    /v1/aggregates   public aggregates (latest price per realm/faction/item, counts)
//   GET    /v1/export?kind= raw measurements for simulator calibration (Bearer ADMIN_TOKEN)
//   cron   daily purge of uploads older than 24 months

export interface Env {
  DB: D1Database;
  CORS_ORIGIN: string;
  IP_SALT: string;
  ADMIN_TOKEN: string;
}

const MAX_BODY = 2_000_000;
const MAX_MEAS = 400;
const MAX_SCANS = 5;
const MAX_ITEMS_PER_SCAN = 30_000;
const UPLOADS_PER_HOUR = 20;
const PRICE_MAX_AGE_DAYS = 14;
const RETENTION_DAYS = 730; // 24 months, as stated on /confidentialite/

const CLASSES = new Set(["WARRIOR", "ROGUE", "PALADIN", "SHAMAN", "MAGE", "PRIEST", "DRUID", "WARLOCK", "HUNTER"]);
const FACTIONS = new Set(["Alliance", "Horde", "Neutral"]);

// Allowed measurement fields per kind: "n" = number in [min, max], "s" = short string.
type Rule = ["n", number, number] | ["s", number];
const NUM = (min: number, max: number): Rule => ["n", min, max];
const STR = (len: number): Rule => ["s", len];
const PCT = NUM(0, 100);
const STAT = NUM(0, 5000);
const COMMON: Record<string, Rule> = { t: NUM(1_700_000_000, 4_000_000_000), level: NUM(1, 80), class: STR(12), buffs: NUM(0, 80) };
const FIELDS: Record<string, Record<string, Rule>> = {
  stats: {
    ...COMMON, race: STR(24), str: STAT, agi: STAT, sta: STAT, int: STAT, spi: STAT, ap: NUM(0, 20000), rap: NUM(0, 20000),
    crit_melee: PCT, crit_ranged: PCT, crit_spell: PCT, dodge: PCT, parry: PCT, block: PCT,
    regen_base: NUM(0, 1000), regen_cast: NUM(0, 1000), mana_max: NUM(0, 100000), talents: STR(16), spec: STR(32),
  },
  pet: {
    ...COMMON, pet_level: NUM(1, 80), family: STR(32), pet_str: STAT, pet_agi: STAT, pet_sta: STAT, pet_int: STAT, pet_spi: STAT,
    pet_ap: NUM(0, 20000), pet_min: NUM(0, 5000), pet_max: NUM(0, 5000), pet_speed: NUM(0, 10), pet_armor: NUM(0, 50000),
    player_ap: NUM(0, 20000), player_rap: NUM(0, 20000),
  },
  rating: {
    ...COMMON, hit_melee: NUM(0, 1000), hit_ranged: NUM(0, 1000), hit_spell: NUM(0, 1000), crit_melee: NUM(0, 1000),
    crit_ranged: NUM(0, 1000), crit_spell: NUM(0, 1000), haste_melee: NUM(0, 1000), haste_ranged: NUM(0, 1000), haste_spell: NUM(0, 1000),
  },
};

class BadRequest extends Error {}

function cors(origin: string): Record<string, string> {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Vary": "Origin",
  };
}

function json(data: unknown, status: number, origin: string, extra: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...cors(origin), ...extra },
  });
}

async function sha256(text: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function randomHex(bytes: number): string {
  return [...crypto.getRandomValues(new Uint8Array(bytes))].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function cleanString(v: unknown, len: number): string | undefined {
  if (typeof v !== "string") return undefined;
  const s = v.trim().slice(0, len);
  return s.length ? s : undefined;
}

// Keeps only whitelisted, well-typed, in-range fields; returns null if the record isn't usable.
function cleanMeasurement(raw: any): Record<string, number | string> | null {
  if (!raw || typeof raw !== "object") return null;
  const rules = FIELDS[raw.k];
  if (!rules) return null;
  const out: Record<string, number | string> = { k: raw.k };
  for (const [key, rule] of Object.entries(rules)) {
    const v = raw[key];
    if (v === undefined || v === null) continue;
    if (rule[0] === "n") {
      if (typeof v === "number" && Number.isFinite(v) && v >= rule[1] && v <= rule[2]) out[key] = v;
    } else {
      const s = cleanString(v, rule[1]);
      if (s !== undefined) out[key] = s;
    }
  }
  if (out.class !== undefined && !CLASSES.has(String(out.class))) return null;
  if (typeof out.level !== "number") return null;
  return out;
}

async function rateLimited(request: Request, env: Env): Promise<boolean> {
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const key = await sha256(`${env.IP_SALT}|${ip}`);
  const window = Math.floor(Date.now() / 3_600_000);
  await env.DB.prepare("DELETE FROM rate WHERE window < ?").bind(window - 24).run();
  const row = await env.DB.prepare(
    "INSERT INTO rate (key, window, count) VALUES (?, ?, 1) ON CONFLICT(key, window) DO UPDATE SET count = count + 1 RETURNING count",
  ).bind(key, window).first<{ count: number }>();
  return (row?.count ?? 0) > UPLOADS_PER_HOUR;
}

async function handleSubmit(request: Request, env: Env, origin: string): Promise<Response> {
  const length = Number(request.headers.get("Content-Length") || 0);
  if (length > MAX_BODY) throw new BadRequest("too_large");
  const text = await request.text();
  if (text.length > MAX_BODY) throw new BadRequest("too_large");
  let body: any;
  try { body = JSON.parse(text); } catch { throw new BadRequest("bad_json"); }
  if (!body || body.format !== "BMD1") throw new BadRequest("bad_format");
  if (await rateLimited(request, env)) return json({ error: "rate_limited" }, 429, origin, { "Retry-After": "3600" });

  const meas = (Array.isArray(body.meas) ? body.meas.slice(0, MAX_MEAS) : []).map(cleanMeasurement).filter(Boolean) as Record<string, number | string>[];
  const scans = (Array.isArray(body.ah) ? body.ah.slice(0, MAX_SCANS) : []).filter((s: any) =>
    s && typeof s === "object" && Number.isFinite(s.t) && cleanString(s.realm, 64) && FACTIONS.has(s.faction) && s.prices && typeof s.prices === "object");
  if (!meas.length && !scans.length) throw new BadRequest("empty");

  const id = randomHex(12);
  const code = randomHex(16);
  const now = Math.floor(Date.now() / 1000);
  const statements: D1PreparedStatement[] = [];

  let nMeas = 0;
  for (const m of meas) {
    const data = JSON.stringify(m);
    statements.push(env.DB.prepare(
      "INSERT OR IGNORE INTO measurements (submission_id, kind, class, level, recorded_at, data, sig) VALUES (?, ?, ?, ?, ?, ?, ?)",
    ).bind(id, m.k, m.class ?? null, m.level, typeof m.t === "number" ? m.t : null, data, await sha256(data)));
    nMeas++;
  }

  let nPrices = 0;
  for (const s of scans) {
    const realm = cleanString(s.realm, 64)!;
    let count = 0;
    for (const [itemKey, p] of Object.entries(s.prices as Record<string, unknown>)) {
      if (count >= MAX_ITEMS_PER_SCAN) break;
      const itemId = Number(itemKey);
      if (!Number.isInteger(itemId) || itemId <= 0 || itemId > 10_000_000 || !Array.isArray(p)) continue;
      const [unit, qty, auctions] = p.map(Number);
      if (!(unit > 0 && unit < 1e10 && qty > 0 && qty < 1e7 && auctions > 0 && auctions < 1e6)) continue;
      statements.push(env.DB.prepare(
        "INSERT OR IGNORE INTO ah_prices (realm, faction, item_id, scanned_at, unit_min, qty, auctions, submission_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
      ).bind(realm, s.faction, itemId, Math.floor(s.t), Math.floor(unit), Math.floor(qty), Math.floor(auctions), id));
      count++;
      nPrices++;
    }
  }

  statements.unshift(env.DB.prepare(
    "INSERT INTO submissions (id, received_at, addon, client, n_meas, n_prices, delete_hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
  ).bind(id, now, cleanString(body.addon, 16) ?? null, cleanString(body.client, 32) ?? null, nMeas, nPrices, await sha256(code)));

  // D1 batches run as one transaction; chunked to stay well under per-batch limits.
  for (let i = 0; i < statements.length; i += 500) await env.DB.batch(statements.slice(i, i + 500));
  return json({ ok: true, measurements: nMeas, prices: nPrices, deletion_code: code }, 200, origin);
}

async function handleDelete(request: Request, env: Env, origin: string): Promise<Response> {
  let body: any;
  try { body = await request.json(); } catch { throw new BadRequest("bad_json"); }
  const code = cleanString(body?.code, 64);
  if (!code || !/^[0-9a-f]{32}$/.test(code)) throw new BadRequest("bad_code");
  const sub = await env.DB.prepare("SELECT id FROM submissions WHERE delete_hash = ?").bind(await sha256(code)).first<{ id: string }>();
  if (!sub) return json({ error: "not_found" }, 404, origin);
  await env.DB.batch([
    env.DB.prepare("DELETE FROM measurements WHERE submission_id = ?").bind(sub.id),
    env.DB.prepare("DELETE FROM ah_prices WHERE submission_id = ?").bind(sub.id),
    env.DB.prepare("DELETE FROM submissions WHERE id = ?").bind(sub.id),
  ]);
  return json({ ok: true }, 200, origin);
}

async function handleAggregates(env: Env, origin: string): Promise<Response> {
  const since = Math.floor(Date.now() / 1000) - PRICE_MAX_AGE_DAYS * 86400;
  // SQLite returns the bare columns of the row holding MAX(scanned_at): the latest scan per item.
  const prices = await env.DB.prepare(
    "SELECT realm, faction, item_id, unit_min, qty, MAX(scanned_at) AS scanned_at FROM ah_prices WHERE scanned_at >= ? GROUP BY realm, faction, item_id",
  ).bind(since).all<{ realm: string; faction: string; item_id: number; unit_min: number; qty: number; scanned_at: number }>();
  const ah: Record<string, Record<string, [number, number, number]>> = {};
  for (const r of prices.results ?? []) {
    const key = `${r.realm}|${r.faction}`;
    (ah[key] ??= {})[r.item_id] = [r.unit_min, r.qty, r.scanned_at];
  }
  const counts = await env.DB.prepare("SELECT kind, class, COUNT(*) AS n FROM measurements GROUP BY kind, class").all();
  const subs = await env.DB.prepare("SELECT COUNT(*) AS n FROM submissions").first<{ n: number }>();
  return json({ generated_at: Date.now(), submissions: subs?.n ?? 0, measurements: counts.results ?? [], ah }, 200, origin,
    { "Cache-Control": "public, max-age=600" });
}

async function handleExport(request: Request, url: URL, env: Env, origin: string): Promise<Response> {
  const auth = request.headers.get("Authorization") || "";
  if (!env.ADMIN_TOKEN || auth !== `Bearer ${env.ADMIN_TOKEN}`) return json({ error: "unauthorized" }, 401, origin);
  const kind = url.searchParams.get("kind") || "stats";
  const rows = await env.DB.prepare("SELECT data FROM measurements WHERE kind = ? ORDER BY id LIMIT 50000").bind(kind).all<{ data: string }>();
  return json({ kind, rows: (rows.results ?? []).map((r) => JSON.parse(r.data)) }, 200, origin);
}

// Daily cron (wrangler.toml [triggers]): enforces the 24-month retention stated on the site's
// privacy page, and clears stale rate-limit rows.
async function purge(env: Env): Promise<void> {
  const cutoff = Math.floor(Date.now() / 1000) - RETENTION_DAYS * 86400;
  await env.DB.batch([
    env.DB.prepare("DELETE FROM measurements WHERE submission_id IN (SELECT id FROM submissions WHERE received_at < ?)").bind(cutoff),
    env.DB.prepare("DELETE FROM ah_prices WHERE submission_id IN (SELECT id FROM submissions WHERE received_at < ?)").bind(cutoff),
    env.DB.prepare("DELETE FROM submissions WHERE received_at < ?").bind(cutoff),
    env.DB.prepare("DELETE FROM rate WHERE window < ?").bind(Math.floor(Date.now() / 3_600_000) - 24),
  ]);
}

export default {
  async scheduled(_event: ScheduledController, env: Env): Promise<void> {
    await purge(env);
  },

  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = env.CORS_ORIGIN;
    if (request.method === "OPTIONS") return new Response(null, { headers: cors(origin) });
    const url = new URL(request.url);
    try {
      if (url.pathname === "/v1/submit" && request.method === "POST") return await handleSubmit(request, env, origin);
      if (url.pathname === "/v1/submission" && request.method === "DELETE") return await handleDelete(request, env, origin);
      if (url.pathname === "/v1/aggregates" && request.method === "GET") return await handleAggregates(env, origin);
      if (url.pathname === "/v1/export" && request.method === "GET") return await handleExport(request, url, env, origin);
      return json({ error: "not_found" }, 404, origin);
    } catch (e: any) {
      if (e instanceof BadRequest) return json({ error: e.message }, 400, origin);
      console.error(e);
      return json({ error: "server_error" }, 500, origin);
    }
  },
};
