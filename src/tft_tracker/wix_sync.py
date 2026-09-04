"""Push pipeline output (tierlist.json / matchups.json / champion_stats.json)
into Wix Data Collections via the Wix REST Data API (bulk upsert).

Requires two env vars alongside RIOT_API_KEY, read from `.env`:
    WIX_API_KEY=...   Wix Dashboard -> Settings -> API Keys
                       (grant it the "Write Data Items" / DC-DATA.WRITE scope)
    WIX_SITE_ID=...   Wix Dashboard -> Settings -> Site ID

The three collections below must already exist in the site's Content
Manager (CMS) with matching Collection IDs and fields — this only writes
items into them, it never creates collections or fields:

    Comps      _id, label, traits(array), carry, tier, playCount, playRate,
               contestationLevel, contestationIndex, avgPlacement, top4Rate,
               winRate, hasEnoughData
    Matchups   _id, compA, compALabel, compB, compBLabel, encounters,
               aAheadRate, bAheadRate
    Champions  _id, pickCount, pickRate, avgPlacement, top4Rate,
               avgStarLevel, threeStarRate, topItems(array of object)

Uses "Bulk Save Data Items" (POST /wix-data/v2/bulk/items/save), which
upserts: existing IDs get updated in place, new IDs get inserted. Re-running
a sync after a fresh collection is safe and idempotent.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

WIX_BULK_SAVE_URL = "https://www.wixapis.com/wix-data/v2/bulk/items/save"
WIX_BULK_REMOVE_URL = "https://www.wixapis.com/wix-data/v2/bulk/items/remove"
WIX_QUERY_URL = "https://www.wixapis.com/wix-data/v2/items/query"
CHUNK_SIZE = 1000  # Wix's own max items per bulk call

_SLUG_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def slugify(raw: str, max_len: int = 128) -> str:
    """Wix Data item IDs are safest as a plain slug — comp keys contain
    '+', an em dash, spaces, etc. so normalize those away."""
    slug = _SLUG_RE.sub("-", raw).strip("-")
    return slug[:max_len] or "item"


def _wix_headers() -> dict:
    api_key = os.environ.get("WIX_API_KEY")
    site_id = os.environ.get("WIX_SITE_ID")
    if not api_key or not site_id:
        raise RuntimeError(
            "WIX_API_KEY and/or WIX_SITE_ID missing from .env. Get them from the "
            "Wix Dashboard: Settings -> API Keys (scope: Write Data Items) and "
            "Settings -> Site ID, then add them to .env next to RIOT_API_KEY."
        )
    return {
        "Content-Type": "application/json",
        "Authorization": api_key,
        "wix-site-id": site_id,
    }


def _bulk_save(collection_id: str, data_items: list[dict]) -> dict:
    if not data_items:
        return {"inserted": 0, "updated": 0, "failures": 0, "errors": []}
    headers = _wix_headers()
    totals = {"inserted": 0, "updated": 0, "failures": 0, "errors": []}
    for i in range(0, len(data_items), CHUNK_SIZE):
        chunk = data_items[i:i + CHUNK_SIZE]
        resp = requests.post(
            WIX_BULK_SAVE_URL,
            headers=headers,
            json={"dataCollectionId": collection_id, "dataItems": chunk, "returnEntity": False},
            timeout=30,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"Wix Data API {resp.status_code} on '{collection_id}': {resp.text[:500]}")
        body = resp.json()
        for r in body.get("results", []):
            meta = r.get("itemMetadata", {})
            if meta.get("success"):
                action = r.get("action")
                if action == "INSERT":
                    totals["inserted"] += 1
                elif action == "UPDATE":
                    totals["updated"] += 1
            else:
                totals["failures"] += 1
                totals["errors"].append(meta.get("error"))
    return totals


def _query_all_ids(collection_id: str, max_pages: int = 50) -> set[str]:
    """All current item IDs in a collection, paginated via cursor.

    Cursor continuation MUST go under `query.cursorPaging.cursor` -- NOT
    `query.paging.cursor`, which isn't a recognized field and gets silently
    ignored, causing every "next page" call to just re-return page 1
    forever. (Learned the hard way: that shape hung in an infinite loop.)
    `max_pages` is a hard safety cap so a future paging bug fails loud
    instead of spinning silently again.
    """
    headers = _wix_headers()
    ids: set[str] = set()
    cursor = None
    for page_num in range(max_pages):
        cursor_paging = {"limit": 1000}
        if cursor:
            cursor_paging["cursor"] = cursor
        resp = requests.post(
            WIX_QUERY_URL,
            headers=headers,
            json={"dataCollectionId": collection_id, "query": {"cursorPaging": cursor_paging}},
            timeout=30,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"Wix Data API {resp.status_code} querying '{collection_id}': {resp.text[:500]}")
        body = resp.json()
        page_items = body.get("dataItems", [])
        for item in page_items:
            ids.add(item["id"])
        print(f"[query] {collection_id}: page {page_num + 1}, +{len(page_items)} items, {len(ids)} total", flush=True)
        cursor = body.get("pagingMetadata", {}).get("cursors", {}).get("next")
        if not cursor or not page_items:
            break
    else:
        raise RuntimeError(f"_query_all_ids hit the {max_pages}-page safety cap on '{collection_id}' "
                            "without exhausting results -- investigate before trusting this set.")
    return ids


def prune_stale_items(collection_id: str, keep_ids: set[str]) -> int:
    """Deletes every item in the collection whose ID isn't in `keep_ids`
    (e.g. left over from a naming-scheme change). Irreversible on Wix's
    side -- call only when `keep_ids` is the authoritative, complete set."""
    existing = _query_all_ids(collection_id)
    stale = list(existing - keep_ids)
    print(f"[prune] {collection_id}: {len(existing)} existing, {len(keep_ids)} to keep, "
          f"{len(stale)} to delete", flush=True)
    if not stale:
        return 0
    headers = _wix_headers()
    removed = 0
    for i in range(0, len(stale), CHUNK_SIZE):
        chunk = stale[i:i + CHUNK_SIZE]
        print(f"[prune] deleting batch {i // CHUNK_SIZE + 1} ({len(chunk)} items)...", flush=True)
        resp = requests.post(
            WIX_BULK_REMOVE_URL,
            headers=headers,
            json={"dataCollectionId": collection_id, "dataItemIds": chunk},
            timeout=30,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"Wix Data API {resp.status_code} pruning '{collection_id}': {resp.text[:500]}")
        body = resp.json()
        removed += body.get("bulkActionMetadata", {}).get("totalSuccesses", 0)
    return removed


def _load_carry_icon_map(champion_stats_path: str) -> dict[str, str]:
    """Best-effort: {champion_id: icon_url}, sourced from a champion_stats.json
    sitting next to the tier list, so a comp card can show its carry's icon
    without a live cross-collection lookup in Velo."""
    p = Path(champion_stats_path)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {c["id"]: c.get("icon_url", "") for c in data.get("champions", [])}


_TIER_RANK = {"S": 1, "A": 2, "B": 3, "C": 4, "?": 5}


def _comp_to_item(row: dict, carry_icons: dict[str, str]) -> dict:
    core_units = [
        {
            "champion": u["champion"],
            "frequency": u["frequency"],
            "cost": u.get("cost"),
            "iconUrl": carry_icons.get(u["champion"], ""),
        }
        for u in row.get("core_units", [])
    ]
    return {
        "id": slugify(row["key"]),
        "data": {
            "label": row["label"],
            "traits": row["traits"],
            "carry": row["carry"],
            "carryIconUrl": carry_icons.get(row["carry"] or "", ""),
            "coreUnits": core_units,
            "avgLevel": row.get("avg_level"),
            "levelBadge": row.get("level_badge", ""),
            "tier": row["tier"],
            "tierRank": _TIER_RANK.get(row["tier"], 99),
            "playCount": row["play_count"],
            "playRate": row["play_rate"],
            "contestationLevel": row["contestation_level"],
            "contestationIndex": row["contestation_index"],
            "avgPlacement": row["avg_placement"],
            "avgPlacementStr": f"{row['avg_placement']:.2f}",
            "top4Rate": row["top4_rate"],
            "top4RatePct": f"{round(row['top4_rate'] * 100)}%",
            "playRatePct": f"{round(row['play_rate'] * 100, 1)}%",
            "winRate": row["win_rate"],
            "hasEnoughData": row["has_enough_data"],
        },
    }


def _matchup_to_item(row: dict) -> dict:
    return {
        "id": slugify(f"{row['comp_a']}__{row['comp_b']}"),
        "data": {
            "compA": row["comp_a"],
            "compALabel": row["comp_a_label"],
            "compB": row["comp_b"],
            "compBLabel": row["comp_b_label"],
            "encounters": row["encounters"],
            "aAheadRate": row["a_ahead_rate"],
            "bAheadRate": row["b_ahead_rate"],
        },
    }


def _champion_to_item(row: dict) -> dict:
    return {
        "id": slugify(row["id"]),
        "data": {
            "pickCount": row["pick_count"],
            "pickRate": row["pick_rate"],
            "avgPlacement": row["avg_placement"],
            "top4Rate": row["top4_rate"],
            "avgStarLevel": row["avg_star_level"],
            "threeStarRate": row["three_star_rate"],
            "topItems": row["top_items"],
            # Community Dragon icon/splash URLs (empty string if unmatched or
            # not computed this run) -- plain Text fields, not Wix Image
            # fields, since these are external URLs, not Wix Media Manager
            # assets. Set them on a Wix Image element's `.src` in Velo.
            "iconUrl": row.get("icon_url", ""),
            "splashUrl": row.get("splash_url", ""),
        },
    }


def sync_tierlist(path: str, collection_id: str = "Comp", champion_stats_path: str | None = None,
                   prune: bool = False) -> dict:
    # NOTE: the Wix collection is displayed as "Comps" in the editor but its
    # actual Collection ID is "Comp" (Wix pluralizes the display label, not
    # the ID) -- verified live via GET /wix-data/v2/collections.
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if champion_stats_path is None:
        champion_stats_path = str(Path(path).parent / "champion_stats.json")
    carry_icons = _load_carry_icon_map(champion_stats_path)
    items = [_comp_to_item(r, carry_icons) for r in data["comps"]]
    result = _bulk_save(collection_id, items)
    if prune:
        result["pruned"] = prune_stale_items(collection_id, {i["id"] for i in items})
    return result


def sync_matchups(path: str, collection_id: str = "Matchups", prune: bool = False) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = [_matchup_to_item(r) for r in data["matchups"]]
    result = _bulk_save(collection_id, items)
    if prune:
        result["pruned"] = prune_stale_items(collection_id, {i["id"] for i in items})
    return result


def sync_champions(path: str, collection_id: str = "Champions", prune: bool = False) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = [_champion_to_item(r) for r in data["champions"]]
    result = _bulk_save(collection_id, items)
    if prune:
        result["pruned"] = prune_stale_items(collection_id, {i["id"] for i in items})
    return result
