"""TFT and League of Legends news feed (/tft/actualites/, /league/actualites/).

Headline index built from Google News RSS searches (official patch notes and the specialised press), one archive per game in
data/game_news/<game>.json, items tagged with the language of the search. Only the title, source name, date and a link to the original
are stored and shown (no article text, no images), same rule as wow_news.py.

    py game_news.py          # refresh both games and print the newest items
Imported by build_site.py (`refresh`, `load`, `TAGS`).
"""
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent / "data" / "game_news"
KEEP = 200          # newest items kept per language
GAMES = ("tft", "lol")
QUERIES = {
    "tft": ['"teamfight tactics" when:90d', 'TFT (patch OR comps OR meta OR "set 18") when:90d'],
    "lol": ['"league of legends" (patch OR meta OR "tier list" OR ranked OR rework) when:90d'],
}
# the title must name the game, Google's search also returns loosely related stories
MUST = {
    "tft": re.compile(r"TFT|teamfight|team fight tactics", re.I),
    "lol": re.compile(r"LoL|league of legends|PBE|Worlds|patch 2\d\.\d+", re.I),
}
EDITIONS = {"fr": "hl=fr&gl=FR&ceid=FR:fr", "en": "hl=en-US&gl=US&ceid=US:en"}

# tag id -> (FR label, EN label); first matching rule wins, "news" is the default
TAGS = {
    "patch": ("Patchs", "Patches"),
    "meta": ("Méta", "Meta"),
    "guide": ("Guides", "Guides"),
    "news": ("Actualités", "News"),
}
RULES = [
    ("patch", re.compile(r"patch|notes de (mise|patch)|mise à jour|update|hotfix", re.I)),
    ("guide", re.compile(r"guide|how to|comment |best builds?|build |astuces|tips", re.I)),
    ("meta", re.compile(r"meta|tier list|comps?\b|buff|nerf|rework|changes|changements|ranked|classé", re.I)),
]


def classify(title):
    for tag, rx in RULES:
        if rx.search(title):
            return tag
    return "news"


def _path(game):
    return DIR / f"{game}.json"


def _norm(title):
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def _fetch(query, lang):
    url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(query) + "&" + EDITIONS[lang]
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; BrokenMetaNews/1.0; +https://brokenmeta.gg)"})
    return ET.fromstring(urllib.request.urlopen(req, timeout=25).read())


def load(game):
    p = _path(game)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"updated": None, "items": []}


def refresh(game, verbose=False):
    """Fetches the searches (one that fails is skipped), merges with the stored archive by URL, writes the file. Returns the data."""
    data = load(game)
    known = {i["url"]: i for i in data["items"]}
    seen = {(i["lang"], _norm(i["title"])) for i in data["items"]}
    added = 0
    for lang in EDITIONS:
        for q in QUERIES[game]:
            try:
                root = _fetch(q, lang)
            except Exception as e:                   # network, XML: keep what we have
                print(f"[game_news] {game}/{lang}: {e}", file=sys.stderr)
                continue
            for it in root.findall(".//item"):
                raw = (it.findtext("title") or "").strip()
                link = (it.findtext("link") or "").strip()
                src = (it.findtext("source") or "").strip()
                title = raw[: -len(src) - 3].strip() if src and raw.endswith(" - " + src) else raw
                if not title or not link or link in known or (lang, _norm(title)) in seen or not MUST[game].search(title):
                    continue
                try:
                    dt = parsedate_to_datetime(it.findtext("pubDate")).astimezone(timezone.utc)
                except Exception:
                    continue
                seen.add((lang, _norm(title)))
                known[link] = {"lang": lang, "source": src or "Google News", "title": title, "url": link,
                               "date": dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "tag": classify(title)}
                added += 1
    items = []
    for lang in EDITIONS:
        items += sorted((i for i in known.values() if i["lang"] == lang), key=lambda i: i["date"], reverse=True)[:KEEP]
    data = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "items": items}
    DIR.mkdir(parents=True, exist_ok=True)
    _path(game).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    if verbose:
        print(f"[game_news] {game}: {added} new item(s), {len(items)} kept")
    return data


def items_for(data, lang):
    return sorted((i for i in data["items"] if i["lang"] == lang), key=lambda i: i["date"], reverse=True)


if __name__ == "__main__":
    for g in GAMES:
        d = refresh(g, verbose=True)
        for i in items_for(d, "fr")[:6]:
            print(i["date"][:10], f"{i['source'][:18]:<18} {i['tag']:<6}", i["title"][:80])
