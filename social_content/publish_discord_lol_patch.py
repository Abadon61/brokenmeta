"""
Fan the latest League of Legends patch out to every visitor who subscribed
their own Discord webhook via /discord/ -- same subscriber list and same
discord-notify-worker /broadcast endpoint as publish_discord_digest.py
(the TFT digest), just a League-flavored embed instead.

Run by hand whenever a new League patch has been added to PATCHES_LOL in
site_build/build_site.py (this stays manual, same as the rest of the LoL
pipeline -- see the project's own notes on the Riot dev key's 24h TTL):
    1. Re-run the extraction snippet below against the new PATCHES_LOL
       entry to refresh social_content/lol_patches.json:

        py -c "
        import json
        src = open('site_build/build_site.py', encoding='utf-8').read()
        start = src.index('PATCHES_LOL = {')
        i = src.index('{', start)
        depth = 0
        for j in range(i, len(src)):
            if src[j] == '{': depth += 1
            elif src[j] == '}':
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break
        ns = {}
        exec('PATCHES_LOL = ' + src[i:end], ns)
        p = ns['PATCHES_LOL']

        def summarize(entry):
            return {
                'version': entry['version'], 'date': entry['date'], 'title': entry['title'],
                'summary': entry['summary'], 'url': entry['url'],
                'buffs': [c['name_en'] for c in entry['changes'] if c['status'] == 'buff'],
                'nerfs': [c['name_en'] for c in entry['changes'] if c['status'] == 'nerf'],
            }

        out = {lang: [summarize(p[lang][0])] for lang in p}
        json.dump(out, open('social_content/lol_patches.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        "
    2. py social_content/publish_discord_lol_patch.py

Requires DISCORD_BROADCAST_SECRET in .env, matching whatever was set with
    npx wrangler secret put BROADCAST_SECRET
in discord-notify-worker/ (same secret as publish_discord_digest.py).
"""
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

PATCHES_PATH = Path(__file__).resolve().parent / "lol_patches.json"
WORKER_URL = "https://discord-notify-worker.brokenmeta.workers.dev"
BRAND_COLOR = 0x00D9FF  # var(--cyan) -- League section's accent, distinct from the TFT digest's magenta


def load_latest_patch() -> dict:
    if not PATCHES_PATH.exists():
        raise SystemExit("lol_patches.json not found -- see this script's docstring to extract it from PATCHES_LOL.")
    patches = json.load(open(PATCHES_PATH, encoding="utf-8"))
    return patches["fr"][0]


def build_embed(patch: dict) -> dict:
    fields = []
    if patch["buffs"]:
        fields.append({"name": "🔼 Renforcés", "value": ", ".join(f"**{n}**" for n in patch["buffs"]), "inline": False})
    if patch["nerfs"]:
        fields.append({"name": "🔽 Affaiblis", "value": ", ".join(f"**{n}**" for n in patch["nerfs"]), "inline": False})

    return {
        "title": f"⚔️ League of Legends -- Patch {patch['version']}",
        "url": "https://brokenmeta.gg/league/patch-notes/",
        "description": patch["summary"],
        "color": BRAND_COLOR,
        "fields": fields,
        "footer": {"text": f"Notes complètes sur leagueoflegends.com -- {patch['date']}"},
    }


def main():
    secret = os.environ.get("DISCORD_BROADCAST_SECRET")
    if not secret:
        raise SystemExit("DISCORD_BROADCAST_SECRET is not set in .env.")

    patch = load_latest_patch()
    embed = build_embed(patch)

    resp = requests.post(f"{WORKER_URL}/broadcast", json={"secret": secret, "embed": embed}, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    print(f"Sent patch {patch['version']} to {result['sent']} subscriber(s), {result['failed']} failed, {result['removed']} removed (dead webhook).")


if __name__ == "__main__":
    main()
