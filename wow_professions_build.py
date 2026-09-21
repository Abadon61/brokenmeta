"""Build the WoW: Forever profession guide data (data/wow_professions/<profession>.json).

Inputs (all local, nothing is invented):
  - data/wow_wowhead_raw/<prof>_spells.json        recipe list of the Wowhead Forever database (skill colours, reagents, source, trainer cost)
  - data/wow_wowhead_raw/<prof>_recipe_items.json  recipe items (plans) of the same database: source, vendor NPC
  - data/wow_wowhead_raw/tradegoods.json           trade goods with their sources (5 = sold by a vendor)
  - data/wow_talents_raw/<build>/*.csv             beta client tables (item names, vendor buy price, vendor sell price, icons, rank texts)

Method for the levelling route (documented on the page):
  * only recipes shown ORANGE at the current skill are used (orange = guaranteed skill point), one craft = one point
  * a recipe is usable if a trainer teaches it, or if its plan is sold by a vendor (plan price = the plan's vendor price)
  * a reagent sold by a vendor costs its vendor price; any other reagent (herbs, drops...) is valued at its vendor SELL price,
    the floor value of an item you farm yourself - the beta has no auction house prices yet
  * recipes whose reagents cannot all be priced (crafted intermediates, quest items...) are left out of the route
  * dynamic programming over skill 1 -> 300 picks the cheapest way, paying each recipe's learning cost once
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

P = Path(__file__).resolve().parent
BUILD = "1.60.1.69913"
RAW = P / "data" / "wow_talents_raw" / BUILD
WH = P / "data" / "wow_wowhead_raw"
OUT = P / "data" / "wow_professions"
ICON_BASE = "https://wow.zamimg.com/images/wow/icons/large/"
CAP = 300      # default; each profession's real cap is read from its rank spells
RANK_CAP = {"Apprentice": 75, "Journeyman": 150, "Expert": 225, "Artisan": 300}     # read from the rank spells' descriptions in the client

# id = URL slug; wh_key = prefix of the raw Wowhead files; wh_path = where the recipe list lives on Wowhead
PROFESSIONS = {
    "alchemy":        {"order": 1, "skill_line": "171", "name": {"en": "Alchemy", "fr": "Alchimie"}, "wh_key": "alchemy", "wh_path": "professions/alchemy"},
    "blacksmithing":  {"order": 2, "skill_line": "164", "name": {"en": "Blacksmithing", "fr": "Forge"}, "wh_key": "blacksmithing", "wh_path": "professions/blacksmithing"},
    "enchanting":     {"order": 3, "skill_line": "333", "name": {"en": "Enchanting", "fr": "Enchantement"}, "wh_key": "enchanting", "wh_path": "professions/enchanting"},
    "engineering":    {"order": 4, "skill_line": "202", "name": {"en": "Engineering", "fr": "Ingénierie"}, "wh_key": "engineering", "wh_path": "professions/engineering"},
    "leatherworking": {"order": 5, "skill_line": "165", "name": {"en": "Leatherworking", "fr": "Travail du cuir"}, "wh_key": "leatherworking", "wh_path": "professions/leatherworking"},
    "tailoring":      {"order": 6, "skill_line": "197", "name": {"en": "Tailoring", "fr": "Couture"}, "wh_key": "tailoring", "wh_path": "professions/tailoring"},
    "cooking":        {"order": 7, "skill_line": "185", "name": {"en": "Cooking", "fr": "Cuisine"}, "wh_key": "cooking", "wh_path": "secondary-skills/cooking"},
    "first-aid":      {"order": 8, "skill_line": "129", "name": {"en": "First Aid", "fr": "Secourisme"}, "wh_key": "firstaid", "wh_path": "secondary-skills/first-aid"},
}


def read_csv(name: str):
    with open(RAW / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main(prof: str = "alchemy") -> None:
    cfg = PROFESSIONS[prof]
    spells = json.loads((WH / f"{cfg['wh_key']}_spells.json").read_text(encoding="utf-8"))
    plans_file = WH / f"{cfg['wh_key']}_recipe_items.json"
    plans = json.loads(plans_file.read_text(encoding="utf-8")) if plans_file.exists() else []
    tradegoods = {r[0]: r for r in json.loads((WH / "tradegoods.json").read_text(encoding="utf-8"))}

    # ---- client tables
    icons = {r["ID"]: r["FileName"].rsplit(".", 1)[0].lower() for r in read_csv("ManifestInterfaceData.csv") if r["FilePath"].lower().startswith("interface\\icons")}
    item_icon = {r["ID"]: r["IconFileDataID"] for r in read_csv("Item.csv")}
    items: dict[int, dict] = {}
    for r in read_csv("ItemSparse.csv"):
        items[int(r["ID"])] = {"en": r["Display_lang"], "buy": int(r["BuyPrice"] or 0), "sell": int(r["SellPrice"] or 0), "icon": icons.get(item_icon.get(r["ID"], ""))}
    for r in read_csv("ItemSparse.frFR.csv"):
        if int(r["ID"]) in items:
            items[int(r["ID"])]["fr"] = r["Display_lang"]
    spell_fr = {r["ID"]: r["Name_lang"] for r in read_csv("SpellName.frFR.csv")}

    def item_name(iid: int) -> dict:
        it = items.get(iid)
        return {"en": it["en"], "fr": it.get("fr") or it["en"]} if it else {"en": f"Item #{iid}", "fr": f"Objet #{iid}"}     # newer beta items are missing from the client table

    # ---- reagent pricing
    unknown_items: set[int] = set()

    def price_of(iid: int):
        it = items.get(iid)
        if not it:
            return None
        row = tradegoods.get(iid)
        if row is None:
            unknown_items.add(iid)           # not a trade good on Wowhead: source unknown, so no reliable price
            return None
        src = row[2] or []
        if 5 in src and it["buy"] > 0:
            return {"copper": it["buy"], "kind": "vendor"}
        if it["sell"] <= 0:
            return None
        if 15 in src and not ({16, 17, 19} & set(src)):
            return {"copper": it["sell"], "kind": "disenchant"}  # from disenchanting: the vendor value in the tables is a token amount
        if 1 in src and not ({2, 16, 17, 19} & set(src)):
            return {"copper": it["sell"], "kind": "craft"}      # made by another craft: resale value as a floor
        return {"copper": it["sell"], "kind": "farm"}

    sl = next((r for r in read_csv("SkillLine.csv") if r["ID"] == cfg["skill_line"]), None)
    prof_icon = icons.get(sl["SpellIconFileID"]) if sl else None
    prof_icon = (ICON_BASE + prof_icon + ".jpg") if prof_icon else None

    # ---- ranks: the trainer's rank spells (cost > 0); the cap is read from the spell text of the beta client
    import re
    spell_desc = {r["ID"]: r["Description_lang"] for r in read_csv("Spell.csv")}
    ranks = []
    LEARN_AT = {"Apprentice": 1, "Journeyman": 50, "Expert": 125, "Artisan": 200}
    for s_ in spells:
        rname = (s_[8] or "").strip()
        if rname in RANK_CAP and not any(r["name"] == rname for r in ranks):
            m = re.search(r"skill of (\d+)", spell_desc.get(str(s_[0]), ""))
            ranks.append({"name": rname, "cap": int(m.group(1)) if m else RANK_CAP[rname], "learn_at": s_[2] if s_[2] < 9000 else LEARN_AT[rname],
                          "cost": s_[7], "cap_from_client": bool(m), "trainer": bool(s_[7])})
    ranks.sort(key=lambda r: r["cap"])
    assert len(ranks) == 4, (prof, ranks)
    cap_total = ranks[-1]["cap"]

    # ---- plans (recipe items) matched to the spell they teach by name ("Recipe: X" -> X)
    plan_by_spell_name: dict[str, list] = {}
    for p in plans:
        name = p[1]
        for pre in ("Recipe: ", "Formula: ", "Pattern: ", "Plans: ", "Schematic: ", "Manual: ", "Blueprint: "):
            if name.startswith(pre):
                name = name[len(pre):]
                break
        plan_by_spell_name.setdefault(name, []).append(p)

    recipes = []
    for s in spells:
        sid, name, learnedat, colors, creates, reagents, source, tcost, rank = s
        if rank or not colors:
            continue
        rag = []
        total = 0
        ok = True
        for iid, cnt in (reagents or []):
            pr = price_of(iid)
            if pr is None:
                ok = False
            else:
                total += pr["copper"] * cnt
            rag.append({"id": iid, "count": cnt, "name": item_name(iid), "icon": (items.get(iid) or {}).get("icon"), "price": pr})
        source = source or []
        acquire = None
        fixed = None
        if 6 in source and tcost:
            acquire = {"type": "trainer", "cost": tcost}
            fixed = tcost
        pl = [p for p in plan_by_spell_name.get(name, [])]
        vend = None
        for p in pl:
            if 5 not in (p[3] or []):
                continue
            npcs = [m for m in (p[5] or []) if m.get("t") == 1 and m.get("n")]
            vend = {"npc": npcs[0]["n"] if len(npcs) == 1 else None, "npc_id": npcs[0]["ti"] if len(npcs) == 1 else None,
                    "item_id": p[0], "cost": items.get(p[0], {}).get("buy", 0)}
        if vend and vend["cost"] > 0 and (fixed is None or vend["cost"] < fixed):
            acquire = {"type": "vendor", "npc": vend["npc"], "npc_id": vend["npc_id"], "item_id": vend["item_id"], "cost": vend["cost"]}
            fixed = vend["cost"]
        if acquire is None and not source and learnedat <= 1:
            acquire = {"type": "start", "cost": 0}       # no source listed for a skill-1 recipe: treated as known from the start (to confirm in beta)
            fixed = 0
        if acquire is None:
            kinds = []
            for code, label in ((2, "drop"), (4, "quest"), (16, "fished"), (21, "pickpocket"), (5, "vendor")):
                if code in source:
                    kinds.append(label)
            acquire = {"type": "other", "kinds": kinds}
        cr = None
        if creates:
            cr = {"id": creates[0], "count": creates[1], "name": item_name(creates[0]), "icon": (items.get(creates[0]) or {}).get("icon")}
        recipes.append({
            "id": sid, "name": {"en": name, "fr": spell_fr.get(str(sid)) or name}, "learn_at": learnedat, "colors": colors,
            "creates": cr, "reagents": rag, "unit_cost": total if ok else None, "acquire": acquire, "fixed": fixed,
        })
    recipes.sort(key=lambda r: (r["learn_at"], r["name"]["en"]))

    # ---- dynamic programming over skill 1 -> cap. One recipe covers a stretch [a, b) of skill points.
    #   orange points are guaranteed; yellow points are not (a lower bound of crafts is used) and carry a penalty so they are only
    #   used to bridge stretches no orange recipe covers. A recipe whose plan cannot be bought (drop, quest...) is a last resort:
    #   it carries a huge penalty, its price is unknown and it is flagged on the page.
    # transmutations are left out: whether they carry a cooldown in Forever is not shown by the data, and a route repeats a recipe many times
    YELLOW_PENALTY, GREEN_PENALTY, UNKNOWN_PLAN_PENALTY = 10 ** 6, 3 * 10 ** 6, 10 ** 10
    usable = []
    for r in recipes:
        if r["unit_cost"] is None or r["name"]["en"].startswith("Transmute"):
            continue
        if r["fixed"] is not None:
            usable.append((r, r["fixed"]))
        elif r["acquire"]["type"] == "other":
            usable.append((r, UNKNOWN_PLAN_PENALTY))
    INF = float("inf")
    best = [INF] * (cap_total + 1)
    back = [None] * (cap_total + 1)
    best[1] = 0
    for b in range(2, cap_total + 1):
        for r, fixed in usable:
            o, y, g, gr = r["colors"]
            if b > gr:
                continue
            first = max(r["learn_at"], o if o > 0 else y, 1)         # first skill at which this recipe still gives points
            for a in range(first, b):
                if best[a] == INF:
                    continue
                yellow_pts = max(0, min(b, g) - max(a, y))
                green_pts = max(0, min(b, gr) - max(a, g))
                c = best[a] + fixed + (b - a) * r["unit_cost"] + yellow_pts * YELLOW_PENALTY + green_pts * GREEN_PENALTY
                if c < best[b]:
                    best[b] = c
                    back[b] = (a, r, fixed)
    steps = []
    gaps = []
    if best[cap_total] == INF:
        reach = max(i for i in range(1, cap_total + 1) if best[i] < INF)
        gaps.append({"reachable_to": reach})
        end = reach
    else:
        end = cap_total
    b = end
    while b > 1:
        a, r, fixed = back[b]
        steps.append((a, b, r, fixed))
        b = a
    steps.reverse()

    route = []
    mats: dict[int, dict] = {}
    plan_cost = 0
    unknown_plans = 0
    for a, b, r, fixed in steps:
        n = b - a
        _o, y, g, gr = r["colors"]
        yellow_pts = max(0, min(b, g) - max(a, y))
        green_pts = max(0, min(b, gr) - max(a, g))
        for g in r["reagents"]:
            m = mats.setdefault(g["id"], {"id": g["id"], "name": g["name"], "icon": g["icon"], "count": 0, "price": g["price"]})
            m["count"] += g["count"] * n
        if fixed >= UNKNOWN_PLAN_PENALTY:
            unknown_plans += 1
        else:
            plan_cost += fixed
        route.append({"from": a, "to": b, "crafts": n, "yellow_points": yellow_pts, "green_points": green_pts, "recipe": r["id"], "name": r["name"], "creates": r["creates"], "reagents": r["reagents"],
                      "unit_cost": r["unit_cost"], "step_cost": n * r["unit_cost"], "acquire": r["acquire"], "colors": r["colors"]})
    materials = sorted(mats.values(), key=lambda m: -(m["count"] * m["price"]["copper"]))
    rank_cost = sum(rk["cost"] for rk in ranks)
    reagent_cost = sum(s["step_cost"] for s in route)
    totals = {"reagents_copper": reagent_cost, "recipes_copper": plan_cost, "ranks_copper": rank_cost,
              "all_copper": reagent_cost + plan_cost + rank_cost, "crafts": sum(s["crafts"] for s in route),
              "yellow_points": sum(s["yellow_points"] for s in route), "green_points": sum(s["green_points"] for s in route), "unknown_plans": unknown_plans,
              "vendor_copper": sum(m["count"] * m["price"]["copper"] for m in materials if m["price"]["kind"] == "vendor"),
              "farm_copper": sum(m["count"] * m["price"]["copper"] for m in materials if m["price"]["kind"] == "farm"),
              "craft_copper": sum(m["count"] * m["price"]["copper"] for m in materials if m["price"]["kind"] == "craft"),
              "disenchant_copper": sum(m["count"] * m["price"]["copper"] for m in materials if m["price"]["kind"] == "disenchant"),
              "has_disenchant": any(m["price"]["kind"] == "disenchant" for m in materials)}

    data = {
        "id": prof, "name": cfg["name"], "icon": prof_icon, "cap": cap_total, "order": cfg["order"], "build": BUILD, "ranks": ranks, "route": route, "gaps": gaps, "materials": materials,
        "totals": totals, "recipes": recipes,
        "method": {"orange_first": True, "farm_valued_at": "vendor sell price", "start_recipes_assumed": [r["id"] for r in recipes if r["acquire"]["type"] == "start"]},
        "sources": {"wowhead": "https://www.wowhead.com/forever/spells/" + cfg["wh_path"], "client": "https://wago.tools/"},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{prof}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(prof, "cap", cap_total, "recipes", len(recipes), "usable", len(usable), "route steps", len(route), "reach", end, "gaps", gaps, "| yellow pts", totals["yellow_points"], "green pts", totals["green_points"], "| unknown plans", unknown_plans, "| unpriced reagent items:", len(unknown_items))
    print("totals copper:", totals)
    for s in route:
        print(f"  {s['from']:>3}->{s['to']:>3} x{s['crafts']:<3} {s['name']['en']:<34} unit {s['unit_cost']:>6}  {s['acquire']['type']} {s['acquire'].get('cost')}")


if __name__ == "__main__":
    for name in (sys.argv[1:] or list(PROFESSIONS)):
        main(name)
