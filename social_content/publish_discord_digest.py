"""
Fan the current digest out to every visitor who subscribed their own
Discord webhook via /discord/ (see discord-notify-worker/) -- the
site-owner-side half of that feature. Nothing here posts to a webhook
BrokenMeta itself controls; this only tells discord-notify-worker's
/broadcast to relay one embed to the full subscriber list it already
holds in KV.

Run by hand after refreshing the site's data (the whole pipeline stays
manual -- see the project's own notes on the Riot dev key's 24h TTL):
    py social_content/build_digest.py     # refresh digest.json first
    py social_content/publish_discord_digest.py

Requires DISCORD_BROADCAST_SECRET in .env, matching whatever was set with
    npx wrangler secret put BROADCAST_SECRET
in discord-notify-worker/.
"""
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DIGEST_PATH = Path(__file__).resolve().parent / "digest.json"
WORKER_URL = "https://discord-notify-worker.brokenmeta.workers.dev"
BRAND_COLOR = 0xFF2D95  # var(--magenta)


def load_digest() -> dict:
    if not DIGEST_PATH.exists():
        raise SystemExit("digest.json not found -- run `py social_content/build_digest.py` first.")
    return json.load(open(DIGEST_PATH, encoding="utf-8"))


def build_embed(digest: dict) -> dict:
    patch = digest.get("patch", {}).get("fr")
    comps = digest.get("comps", {})
    top5 = comps.get("top5") or []
    riser = comps.get("biggest_riser")
    faller = comps.get("biggest_faller")

    fields = []
    if top5:
        top = top5[0]
        fields.append({
            "name": "🔥 Top comp du moment",
            "value": f"**{top['display_label']}** (Tier {top['tier']}) -- {top['avgPlacement']:.2f} placement moyen sur {top['playCount']} parties",
            "inline": False,
        })
    if riser:
        fields.append({
            "name": "📈 Plus grosse hausse",
            "value": f"**{riser['display_label']}** -- {riser['prevAvgPlacement']:.2f} → {riser['avgPlacement']:.2f} placement",
            "inline": True,
        })
    if faller:
        fields.append({
            "name": "📉 Plus grosse chute",
            "value": f"**{faller['display_label']}** -- {faller['prevAvgPlacement']:.2f} → {faller['avgPlacement']:.2f} placement",
            "inline": True,
        })

    title = "📊 Digest BrokenMeta.gg"
    description = None
    if patch:
        title = f"📊 Digest BrokenMeta.gg -- Patch {patch['version']}"
        description = patch.get("summary")

    return {
        "title": title,
        "url": "https://brokenmeta.gg/tendances/",
        "description": description,
        "color": BRAND_COLOR,
        "fields": fields,
        "footer": {"text": "BrokenMeta.gg -- TFT Set 18, données réelles uniquement"},
    }


def main():
    secret = os.environ.get("DISCORD_BROADCAST_SECRET")
    if not secret:
        raise SystemExit("DISCORD_BROADCAST_SECRET is not set in .env.")

    digest = load_digest()
    embed = build_embed(digest)

    resp = requests.post(f"{WORKER_URL}/broadcast", json={"secret": secret, "embed": embed}, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    print(f"Sent to {result['sent']} subscriber(s), {result['failed']} failed, {result['removed']} removed (dead webhook).")


if __name__ == "__main__":
    main()
