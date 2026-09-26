"""Auction house prices shared by players through the BrokenMeta addon, for the profession guides.

The data comes from wow-worker's public /v1/aggregates (latest lowest unit buyout per item,
per realm/faction, scans younger than 14 days). Fetched at build time; the last good copy is
kept in data/wow_ah/aggregates.json so a build without network still has prices, and the
committed snapshot documents exactly what a deployed page was built from.

Pricing rule per shopping-list reagent:
  - bought from a vendor: the vendor's fixed price, unless the auction house sells it cheaper
    AND lists at least the quantity the route needs;
  - gathered / disenchanted: the auction house price if the item was seen in the chosen market,
    otherwise unknown (never guessed). "thin" flags a market listing fewer units than the route
    needs (the real cost will be higher: the cheapest units run out);
  - crafted by this same profession (Cured Heavy Hide, grinding stones...): the cheaper of its
    auction price and its crafting cost (its own recipe's reagents priced by these same rules).
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

PROJECT = Path(__file__).resolve().parent.parent
SNAPSHOT = PROJECT / "data" / "wow_ah" / "aggregates.json"
AGG_URL = "https://wow-worker.brokenmeta.workers.dev/v1/aggregates"


def load(fetch=True):
    """Latest aggregates (fresh from the worker when reachable, else the saved snapshot)."""
    if fetch:
        try:
            r = requests.get(AGG_URL, timeout=15)
            r.raise_for_status()
            data = r.json()
            if isinstance(data.get("ah"), dict):
                SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
                SNAPSHOT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
                return data
        except (requests.RequestException, ValueError) as e:
            print(f"wow_ah: aggregates fetch failed ({e}); using the saved snapshot")
    if SNAPSHOT.exists():
        return json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    return None


def pick_market(agg):
    """The realm/faction with the most priced items (the best-covered market), or None."""
    if not agg or not agg.get("ah"):
        return None
    key, prices = max(agg["ah"].items(), key=lambda kv: len(kv[1]))
    realm, _, faction = key.partition("|")
    latest = max(p[2] for p in prices.values())
    return {
        "realm": realm, "faction": faction, "items": len(prices),
        "scanned": datetime.fromtimestamp(latest, tz=timezone.utc),
        "prices": {int(item): {"unit": p[0], "qty": p[1], "t": p[2]} for item, p in prices.items()},
    }


def price_profession(prof, market):
    """Adds prof["ah"] (per-material prices + totals) when a market exists. Returns prof."""
    if not market:
        prof["ah"] = None
        return prof
    recipes = {r["creates"]["id"]: r for r in prof.get("recipes", []) if r.get("creates")}

    def reagent_unit(g, depth):
        seen = market["prices"].get(g["id"])
        if g["price"]["kind"] == "vendor":
            vendor = g["price"]["copper"]
            return min(vendor, seen["unit"]) if seen else vendor
        options = [seen["unit"]] if seen else []
        crafted = craft_cost(g["id"], depth + 1)
        if crafted is not None:
            options.append(crafted)
        return min(options) if options else None

    def craft_cost(item_id, depth=0):
        r = recipes.get(item_id)
        if not r or depth > 2:
            return None
        total = 0
        for g in r["reagents"]:
            unit = reagent_unit(g, depth)
            if unit is None:
                return None
            total += unit * g["count"]
        return -(-total // max(1, r["creates"].get("count") or 1))  # ceil

    rows, known, unknown, from_ah = {}, 0, 0, 0
    for m in prof["materials"]:
        seen = market["prices"].get(m["id"])
        ah_unit = seen["unit"] if seen else None
        listed = seen["qty"] if seen else 0
        crafted = craft_cost(m["id"]) if m["price"]["kind"] == "craft" else None
        if m["price"]["kind"] == "vendor":
            unit, source = m["price"]["copper"], "vendor"
            if ah_unit is not None and ah_unit < unit and listed >= m["count"]:
                unit, source = ah_unit, "ah"
                from_ah += 1
        elif crafted is not None and (ah_unit is None or crafted <= ah_unit):
            unit, source = crafted, "craft"
        elif ah_unit is not None:
            unit, source = ah_unit, "ah"
            from_ah += 1
        else:
            unit, source = None, None
        line = unit * m["count"] if unit is not None else None
        if line is None:
            unknown += 1
        else:
            known += line
        rows[m["id"]] = {"ah_unit": ah_unit, "listed": listed, "line": line, "source": source,
                         "thin": source == "ah" and listed < m["count"]}
    prof["materials"] = sorted(prof["materials"], key=lambda m: -(rows[m["id"]]["line"] or -1))
    t = prof["totals"]
    prof["ah"] = {
        "rows": rows, "reagents_copper": known, "unknown": unknown, "from_ah": from_ah,
        "total_copper": known + t.get("recipes_copper", 0) + t.get("ranks_copper", 0),
        "realm": market["realm"], "faction": market["faction"], "scanned": market["scanned"],
    }
    return prof
