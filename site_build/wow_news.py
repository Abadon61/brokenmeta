"""WoW: Forever news feed (/wow-forever/actualites/).

Aggregates the headlines of public RSS feeds (Wowhead's Forever news, MMO-Champion, the Wowhead Blue Tracker of Blizzard's own posts)
and keeps them in data/wow_news/news.json so the page grows into an archive. Only the title, source, date and a link to the original
are stored and shown (no article text, no images): a headline index that sends the reader to the source.

    py wow_news.py          # refresh the feeds and print what changed
Imported by build_site.py (`refresh`, `load`, `latest`, `TAGS`).
"""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "data" / "wow_news" / "news.json"
KEEP = 400          # newest items kept in the archive
FEEDS = [
    # (source id, label, url, title filter or None)
    ("wowhead", "Wowhead", "https://www.wowhead.com/news/rss/forever", None),
    ("mmochampion", "MMO-Champion", "https://www.mmo-champion.com/external.php?do=rss&type=newcontent&sectionid=1&days=120&count=15", re.compile(r"forever|\bbeta\b", re.I)),
    ("blizzard", "Blizzard (Wowhead Blue Tracker)", "https://www.wowhead.com/blue-tracker?rss", re.compile(r"forever|\bbeta\b", re.I)),
]
SOURCES = {f[0]: f[1] for f in FEEDS}

# tag id -> (FR label, EN label); the first matching rule wins, "news" is the default
TAGS = {
    "release": ("Sortie et bêta", "Release & beta"),
    "tuning": ("Changements de la bêta", "Beta changes"),
    "dev": ("Blizzard", "Blizzard posts"),
    "guide": ("Guides", "Guides"),
    "news": ("Actualités", "News"),
}
RULES = [
    ("tuning", re.compile(r"hotfix|tuning|nerf|buff|rebalanc|changes?|updates? in|rework|adjust|patch notes|build|no longer|removed|reduced|increased|temporary", re.I)),
    ("dev", re.compile(r"development notes|dev notes|developer|q&a|interview|blizzard (says|working|confirms|warns|addresses)|blue post|wow weekly|from the dev", re.I)),
    ("release", re.compile(r"release date|pre-?purchase|edition|launch|servers? (open|down|live)|beta (phase|now live|ends?|start|invite)|early access|character name|reservation|open beta|invite", re.I)),
    ("guide", re.compile(r"guide|every quest|walkthrough|how to|where to|best |tier list|story of|locations?|rewards?|walk-?through", re.I)),
]


def classify(title):
    for tag, rx in RULES:
        if rx.search(title):
            return tag
    return "news"


def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; BrokenMetaNews/1.0; +https://brokenmeta.gg)"})
    return ET.fromstring(urllib.request.urlopen(req, timeout=25).read())


def _norm(title):
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def load():
    if PATH.exists():
        return json.loads(PATH.read_text(encoding="utf-8"))
    return {"updated": None, "items": []}


def refresh(verbose=False):
    """Fetches every feed (a feed that fails is skipped), merges with the stored archive by URL, writes the file. Returns the data."""
    data = load()
    known = {i["url"]: i for i in data["items"]}
    seen_titles = {(_norm(i["title"]), i["date"][:10]) for i in data["items"]}
    added = 0
    for sid, label, url, rx in FEEDS:
        try:
            root = _fetch(url)
        except Exception as e:                       # network, 403, XML: keep what we have
            print(f"[wow_news] {sid}: {e}", file=sys.stderr)
            continue
        for it in root.findall(".//item"):
            title = (it.findtext("title") or "").replace("�", "'").strip()
            link = (it.findtext("link") or "").strip()
            if not title or not link or link in known or (rx and not rx.search(title)):
                continue
            try:
                dt = parsedate_to_datetime(it.findtext("pubDate")).astimezone(timezone.utc)
            except Exception:
                continue
            key = (_norm(title), dt.strftime("%Y-%m-%d"))
            if key in seen_titles:                   # the Blue Tracker lists the EU and US copy of one post
                continue
            seen_titles.add(key)
            known[link] = {"source": sid, "title": title, "url": link, "date": dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "tag": classify(title)}
            added += 1
    items = sorted(known.values(), key=lambda i: i["date"], reverse=True)[:KEEP]
    data = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "items": items}
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    if verbose:
        print(f"[wow_news] {added} new item(s), {len(items)} kept")
    return data


def latest(data, n=6):
    return data["items"][:n]


if __name__ == "__main__":
    d = refresh(verbose=True)
    for i in d["items"][:12]:
        print(i["date"][:10], f"{i['source']:<12} {i['tag']:<8}", i["title"][:90])
