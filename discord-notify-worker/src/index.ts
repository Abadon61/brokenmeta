// discord-notify-worker: lets any visitor paste their OWN Discord webhook
// URL to get automatic BrokenMeta.gg digest updates in their own server --
// this is deliberately NOT "post to BrokenMeta's own Discord", it's a
// public subscriber list anyone can join or leave.
//
// Three endpoints:
//   POST /subscribe   { webhookUrl } -- validated, sent a welcome ping,
//                       then stored (browser-facing, needs CORS)
//   POST /unsubscribe { webhookUrl } -- removed from the list
//                       (browser-facing, needs CORS)
//   POST /broadcast    { secret, embed } -- fans the embed out to every
//                       stored webhook; owner-only (BROADCAST_SECRET),
//                       called from the site owner's own publish script,
//                       never from the browser
//
// Security note: a worker that POSTs to a URL taken from user input is a
// classic SSRF shape. DISCORD_WEBHOOK_RE closes that off completely --
// only a URL matching Discord's own webhook path is ever accepted or
// fetched, so this can never become an open POST-to-anywhere relay.
export interface Env {
  BROADCAST_SECRET: string;
  CORS_ORIGIN: string;
  WEBHOOKS: KVNamespace;
}

const DISCORD_WEBHOOK_RE = /^https:\/\/(discord|discordapp)\.com\/api\/webhooks\/\d+\/[\w-]+$/;

function corsHeaders(origin: string): Record<string, string> {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
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

async function readBody(request: Request): Promise<any> {
  try {
    return await request.json();
  } catch {
    return {};
  }
}

// One subscribe attempt per IP per THROTTLE_SECONDS -- cheap deterrent
// against a script hammering /subscribe with junk URLs. Real subscribers
// only ever call this once. 60 is also Cloudflare KV's own minimum TTL.
const THROTTLE_SECONDS = 60;

async function sha256Hex(input: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(input));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Hashed, not raw -- the site's own privacy copy for this page promises
// nothing but the webhook URL itself is stored, so even this short-lived
// (60s) anti-spam key must never hold a plain IP address.
async function throttled(env: Env, request: Request): Promise<boolean> {
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const key = `throttle:${await sha256Hex(ip)}`;
  if (await env.WEBHOOKS.get(key)) return true;
  await env.WEBHOOKS.put(key, "1", { expirationTtl: THROTTLE_SECONDS });
  return false;
}

async function handleSubscribe(request: Request, env: Env, origin: string): Promise<Response> {
  if (await throttled(env, request)) {
    return json({ error: "Trop de tentatives, réessaie dans quelques secondes." }, 429, origin);
  }
  const body = await readBody(request);
  const webhookUrl = typeof body.webhookUrl === "string" ? body.webhookUrl.trim() : "";
  if (!DISCORD_WEBHOOK_RE.test(webhookUrl)) {
    return json({ error: "URL de webhook Discord invalide." }, 400, origin);
  }

  // A real ping doubles as validation: a webhook Discord already deleted,
  // or one missing send permission, fails here instead of silently
  // collecting dead subscribers that /broadcast would fail on forever.
  const ping = await fetch(webhookUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: "🎉 Abonné aux mises à jour BrokenMeta.gg ! Tu recevras ici les prochains digests (tendances, patch notes, top comps)." }),
  });
  if (!ping.ok) {
    return json({ error: "Ce webhook n'a pas répondu correctement -- vérifie l'URL." }, 400, origin);
  }

  await env.WEBHOOKS.put(webhookUrl, new Date().toISOString());
  return json({ ok: true }, 200, origin);
}

async function handleUnsubscribe(request: Request, env: Env, origin: string): Promise<Response> {
  const body = await readBody(request);
  const webhookUrl = typeof body.webhookUrl === "string" ? body.webhookUrl.trim() : "";
  if (!DISCORD_WEBHOOK_RE.test(webhookUrl)) {
    return json({ error: "URL de webhook Discord invalide." }, 400, origin);
  }
  await env.WEBHOOKS.delete(webhookUrl);
  return json({ ok: true }, 200, origin);
}

// Owner-only: called from the site's own publish script (server-to-server,
// no browser involved, so no CORS concern) whenever a fresh digest is
// ready. Self-cleaning: a webhook Discord reports as gone (401/404 -- the
// server or the webhook itself was deleted) is dropped from the list
// instead of being retried forever.
async function handleBroadcast(request: Request, env: Env, origin: string): Promise<Response> {
  const body = await readBody(request);
  // Explicit truthiness + type checks, not just `!==`: if BROADCAST_SECRET
  // were ever left unset (secret never provisioned via `wrangler secret
  // put`), env.BROADCAST_SECRET and a missing body.secret would both be
  // undefined and a bare `!==` comparison would treat that as a match --
  // silently authorizing every unauthenticated caller. Requiring both to
  // be non-empty strings first closes that off.
  if (typeof env.BROADCAST_SECRET !== "string" || env.BROADCAST_SECRET.length === 0
      || typeof body.secret !== "string" || body.secret !== env.BROADCAST_SECRET) {
    return json({ error: "Non autorisé." }, 401, origin);
  }
  const embed = body.embed;
  if (!embed || typeof embed !== "object") {
    return json({ error: "Il manque 'embed'." }, 400, origin);
  }

  let sent = 0, removed = 0, failed = 0;
  let cursor: string | undefined;
  do {
    const page = await env.WEBHOOKS.list({ cursor, limit: 1000 });
    for (const { name: webhookUrl } of page.keys) {
      if (webhookUrl.startsWith("throttle:")) continue;
      try {
        const res = await fetch(webhookUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ embeds: [embed] }),
        });
        if (res.status === 401 || res.status === 404) {
          await env.WEBHOOKS.delete(webhookUrl);
          removed++;
        } else if (res.ok) {
          sent++;
        } else {
          failed++;
        }
      } catch {
        failed++;
      }
    }
    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor);

  return json({ sent, removed, failed }, 200, origin);
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = env.CORS_ORIGIN;
    if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders(origin) });
    if (request.method !== "POST") return json({ error: "Méthode non supportée." }, 405, origin);

    const url = new URL(request.url);
    try {
      if (url.pathname === "/subscribe") return await handleSubscribe(request, env, origin);
      if (url.pathname === "/unsubscribe") return await handleUnsubscribe(request, env, origin);
      if (url.pathname === "/broadcast") return await handleBroadcast(request, env, origin);
      return json({ error: "Route inconnue." }, 404, origin);
    } catch (e: any) {
      return json({ error: "Erreur interne. Réessaie dans un instant.", detail: String(e?.message || e) }, 500, origin);
    }
  },
};
