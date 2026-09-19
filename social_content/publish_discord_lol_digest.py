"""
League of Legends digest for the Discord subscribers who follow League (see
the game checkboxes on /discord/): biggest win-rate risers/fallers and the
champion+role tier changes between the last two collections -- the same data
as /league/tendances/ and /league/changements/.

Run by hand after a League collection and a site rebuild (the whole pipeline
stays manual -- see the project's notes on the Riot dev key's 24h TTL):
    py lol_run.py                                  # collect
    py site_build/build_site.py                    # writes data/output/lol_trends_digest.json
    py social_content/publish_discord_lol_digest.py [--dry-run]

Requires DISCORD_BROADCAST_SECRET in .env, matching the secret set with
    npx wrangler secret put BROADCAST_SECRET
in discord-notify-worker/. --dry-run prints the embed and sends nothing.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

DIGEST_PATH = Path(__file__).resolve().parent.parent / "data" / "output" / "lol_trends_digest.json"
WORKER_URL = "https://discord-notify-worker.brokenmeta.workers.dev"
BRAND_COLOR = 0xD72638  # brand red
MAX_LINES = 5
FIELD_LIMIT = 1000     # Discord caps an embed field value at 1024 characters


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def mover_line(m: dict) -> str:
    delta = (m["latest_win_rate"] - m["prev_win_rate"]) * 100
    return f"**{m['name']}** ({m['role_label']}) {pct(m['prev_win_rate'])} → {pct(m['latest_win_rate'])} ({delta:+.1f})"


def tier_line(t: dict) -> str:
    return f"**{t['name']}** ({t['role_label']}) {t['prev_tier']} → {t['latest_tier']}"


def field(name: str, lines: list[str]) -> dict | None:
    if not lines:
        return None
    value = "\n".join(lines[:MAX_LINES])
    return {"name": name, "value": value[:FIELD_LIMIT], "inline": False}


def build_embed(d: dict) -> dict | None:
    fields = [f for f in (
        field("📈 Plus fortes hausses de winrate", [mover_line(m) for m in d["risers"]]),
        field("📉 Plus grosses chutes de winrate", [mover_line(m) for m in d["fallers"]]),
        field("⬆️ Montées de tier", [tier_line(t) for t in d["promotions"]]),
        field("⬇️ Descentes de tier", [tier_line(t) for t in d["demotions"]]),
    ) if f]
    if not fields:
        return None
    return {
        "title": "⚔️ League of Legends -- Tendances",
        "url": "https://brokenmeta.gg/league/tendances/",
        "description": f"Entre les collectes du {d['prev_date']} et du {d['latest_date']} (champions avec au moins 100 parties dans les deux).",
        "color": BRAND_COLOR,
        "fields": fields,
        "footer": {"text": "BrokenMeta.gg -- parties classées réelles, aucune donnée inventée"},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print the embed, send nothing")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252 and choke on the emojis
    except Exception:
        pass

    if not DIGEST_PATH.exists():
        raise SystemExit("lol_trends_digest.json not found -- run `py site_build/build_site.py` first.")
    digest = json.load(open(DIGEST_PATH, encoding="utf-8"))
    if not digest.get("prev_date"):
        raise SystemExit("Only one League snapshot so far: no trends to publish yet.")
    embed = build_embed(digest)
    if not embed:
        raise SystemExit("No significant movement between the last two snapshots: nothing to publish.")

    if args.dry_run:
        print(json.dumps(embed, ensure_ascii=False, indent=2))
        return

    secret = os.environ.get("DISCORD_BROADCAST_SECRET")
    if not secret:
        raise SystemExit("DISCORD_BROADCAST_SECRET is not set in .env.")
    resp = requests.post(f"{WORKER_URL}/broadcast", json={"secret": secret, "embed": embed, "game": "lol"}, timeout=30)
    resp.raise_for_status()
    r = resp.json()
    print(f"Sent to {r['sent']} subscriber(s), {r['failed']} failed, {r['removed']} removed (dead webhook), {r.get('skipped', 0)} skipped (not following League).")


if __name__ == "__main__":
    main()
