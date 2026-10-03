"""Generates the stat weights of BrokenDPS and the data files of the Broken Meta addon suite.

For every spec in site_build/wow_dps_sim.py's ROTATIONS, measures how much simulated DPS one
extra point of each stat adds on top of that spec's real level-20 BiS gear, then writes the
result as a Lua table to wow_addon/BrokenMetaWeights/Weights.lua.

Method: site_build/wow_weights.py (shared with the site's "Simulate my character" page):
common random numbers, central differences, Str/Agi/Int derived exactly from the sim's own
conversions. See that module's docstring.

Also writes wow_addon/BrokenMetaWeights/Data.lua (no simulation needed, `--data-only`): dungeon
loot with stats, class armor/weapon proficiency, recommended talent builds and profession routes,
all from the site's own data files.

Usage: py -3.11 wow_addon_build.py [--iterations 800] [--fight-len 300] [--data-only]
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "site_build"))
import wow_dps_sim as sim  # noqa: E402
import wow_weights  # noqa: E402

# The Broken Meta suite: the HUB (folder BrokenMetaWeights, kept so players keep their saved data)
# holds the data several addons share; each addon gets its own Data.lua.
ADDONS_DIR = ROOT / "wow_addon"
OUT = ADDONS_DIR / "BrokenDPS" / "Weights.lua"
DATA_OUT = {
    "hub": ADDONS_DIR / "BrokenMetaWeights" / "Data.lua",
    "dps": ADDONS_DIR / "BrokenDPS" / "Data.lua",
    "crafter": ADDONS_DIR / "BrokenCrafter" / "Data.lua",
    "codex": ADDONS_DIR / "BrokenCodex" / "Data.lua",
}

def weights_for(spec_id, iterations, fight_len):
    """Level-20 BiS sheet weights through the shared wow_weights module (same code as the site)."""
    base = sim.bis_stats_for_spec(spec_id)
    if base is None:
        return None
    dps, w = wow_weights.stat_weights(spec_id, base, None, iterations, fight_len)
    return dps, base, w


def talent_specs(cls):
    """Real spec ids, FR/EN names and talent-tab order from the beta client tables."""
    d = json.loads((ROOT / "data" / "wow_talents" / f"{cls}.json").read_text(encoding="utf-8"))
    return {s["id"]: (i + 1, s["name"]) for i, s in enumerate(d["specs"])}


def talent_nodes_lua():
    """Every class's talent node ids mapped to their talent tree index, so the addon can count
    the points spent per tree in game and export talents the site's calculator understands."""
    lines = ["ns.TALENT_TAB = {"]
    for f in sorted((ROOT / "data" / "wow_talents").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        pairs = [f"[{t['id'].lstrip('n')}] = {i + 1}" for i, s in enumerate(d["specs"]) for t in s["talents"]]
        lines.append(f"  {d['id'].upper()} = {{ " + ", ".join(pairs) + " },")
    lines.append("}")
    return "\n".join(lines)


def lua_str(v):
    return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'


def lua_table(rows):
    lines = []
    for spec_id, (dps, base, w) in rows.items():
        prof = sim.ROTATIONS[spec_id]
        cls = prof.get("glossary", spec_id)
        tab, names = talent_specs(cls)[sim.SPEC_ID_MAP[spec_id]]
        caster = "true" if sim.SPEC_STAT_PROFILE.get(spec_id, {}).get("crit") == "spell" else "false"
        stats = ", ".join(f"{k} = {w[k]}" for k in ("str", "agi", "int", "ap", "sp", "crit", "hit", "wdps_mh", "wdps_oh", "wdps_r"))
        ranged = "true" if sim.SPEC_STAT_PROFILE.get(spec_id, {}).get("agi_ap") == "ranged" else "false"
        # Talent that turns Intellect into Attack Power: lets the addon correct the Intellect weight for
        # the rank the player really has (the weights above assume the guide's build).
        t = sim.INT_AP_TALENTS.get(spec_id)
        intap = (f",\n    intap = {{ node = {t['node']}, assumed = {t['assumed']}, ranks = {{" + ", ".join(f"{r:.4f}" for r in t["ranks"]) + "} }")\
            if t else ""
        lines.append(
            f'  {spec_id} = {{ class = "{cls.upper()}", spec = "{sim.SPEC_ID_MAP.get(spec_id, spec_id)}", '
            f'role = "{prof.get("role", "dps")}", tab = {tab}, ranged = {ranged}, caster = {caster}, dps = {dps:.2f},\n'
            f"    name = {{ frFR = {lua_str(names['fr'])}, enUS = {lua_str(names['en'])} }},\n"
            f"    w = {{ {stats} }}{intap} }},"
        )
    return "\n".join(lines)


# ------------------------------------------------------------------------------------ Data.lua
DUNGEON_SLOTS = {1: "INVTYPE_HEAD", 2: "INVTYPE_NECK", 3: "INVTYPE_SHOULDER", 5: "INVTYPE_CHEST", 20: "INVTYPE_ROBE",
                 6: "INVTYPE_WAIST", 7: "INVTYPE_LEGS", 8: "INVTYPE_FEET", 9: "INVTYPE_WRIST", 10: "INVTYPE_HAND",
                 11: "INVTYPE_FINGER", 12: "INVTYPE_TRINKET", 13: "INVTYPE_WEAPON", 14: "INVTYPE_SHIELD",
                 15: "INVTYPE_RANGED", 16: "INVTYPE_CLOAK", 17: "INVTYPE_2HWEAPON", 21: "INVTYPE_WEAPONMAINHAND",
                 22: "INVTYPE_WEAPONOFFHAND", 23: "INVTYPE_HOLDABLE", 25: "INVTYPE_THROWN", 26: "INVTYPE_RANGEDRIGHT"}
PROF_SKILL_LINES = {"alchemy": 171, "blacksmithing": 164, "enchanting": 333, "engineering": 202,
                    "leatherworking": 165, "tailoring": 197, "cooking": 185, "first-aid": 129}


def lua(v):
    """Python value -> Lua literal (dicts with str keys become records, lists become arrays)."""
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(round(v, 4)) if isinstance(v, float) else str(v)
    if isinstance(v, str):
        return lua_str(v)
    if isinstance(v, list):
        return "{" + ", ".join(lua(x) for x in v) + "}"
    if isinstance(v, dict):
        parts = []
        for k, x in v.items():
            key = k if isinstance(k, str) and k.isidentifier() else f"[{lua(k)}]"
            parts.append(f"{key} = {lua(x)}")
        return "{" + ", ".join(parts) + "}"
    raise TypeError(type(v))


def loot_item(it, **extra):
    """A site loot item (dungeon or raid page) -> the addon's compact loot row."""
    st = it["st"]
    stats = {k: v for k, v in {
        "str": st.get("str"), "agi": st.get("agi"), "int": st.get("int"), "ap": st.get("atkpwr"),
        "sp": (st.get("splpwr") or 0) + (st.get("spldmg") or 0) or None,
        "critR": st.get("critstrkrtng"), "hitR": st.get("hitrtng"),
        "wdps": st.get("rgddps") or st.get("dps"),
    }.items() if v}
    return dict({"id": it["id"], "slot": DUNGEON_SLOTS.get(it["slot"]), "t": it["type"]["en"] or None,
                 "req": it.get("req", 0), "q": it.get("q", 2), "n": it["name"],
                 "src": (it.get("src") or [None])[0], "quest": it.get("kind") == "quest", "st": stats}, **extra)


def loot_data():
    d = json.loads((ROOT / "data" / "wow_dungeons" / "dungeons.json").read_text(encoding="utf-8"))
    dungeons, loot = [], []
    for i, dg in enumerate(d["dungeons"], 1):
        dungeons.append({"id": dg["id"], "name": {"frFR": dg["name"]["fr"], "enUS": dg["name"]["en"]}, "levels": dg["levels"]})
        for it in dg["items"]:
            loot.append(loot_item(it, d=i))
    return dungeons, loot


def dungeon_art():
    """Per dungeon (same order as ns.DUNGEONS): its loading screen FileDataID and its bosses with NPC ids.
    Built by wow_codex_art_build.py (data/wow_dungeons/art.json)."""
    art = json.loads((ROOT / "data" / "wow_dungeons" / "art.json").read_text(encoding="utf-8"))
    dungeons = json.loads((ROOT / "data" / "wow_dungeons" / "dungeons.json").read_text(encoding="utf-8"))["dungeons"]
    out = []
    for dg in dungeons:
        a = art["dungeons"][dg["id"]]
        bosses = []
        for b in a["bosses"]:
            row = {"name": {"frFR": b["name"]["fr"], "enUS": b["name"]["en"]}, "npc": b["npc"]}
            if b.get("extra"):
                row["extra"] = True
            bosses.append(row)
        quests = {}
        for qn, qd in a.get("quests", {}).items():
            row = {"name": {"frFR": qd["name"]["fr"], "enUS": qd["name"]["en"]}}
            g = qd.get("giver")
            if g:
                row["giver"] = {"kind": g["kind"], "name": {"frFR": g["name"]["fr"], "enUS": g["name"]["en"]}}
                if g.get("zone") and g.get("x") is not None:
                    row["giver"].update({"zone": {"frFR": g["zone"]["fr"], "enUS": g["zone"]["en"]}, "x": g["x"], "y": g["y"]})
            quests[qn] = row
        # wide: a 16:9 picture (Forever's own dungeons); the others are the classic 4:3 loading screens
        out.append({"image": a["image"], "wide": a["image"] > 1000000, "bosses": bosses, "quests": quests})
    return out, {k: v["image"] for k, v in art.get("raids", {}).items()}


def fr_en(v):
    return {"frFR": v.get("fr") or v.get("en"), "enUS": v.get("en")} if isinstance(v, dict) else v


def raids_data():
    """Raids for BrokenCodex: info, bosses with their type, abilities (spell IDs) and loot."""
    path = ROOT / "data" / "wow_raids" / "raids.json"
    if not path.exists():
        return []
    out = []
    for rd in json.loads(path.read_text(encoding="utf-8")).get("raids", []):
        info = rd.get("info") or {}
        att = info.get("attunement") or {}
        out.append({
            "id": rd["id"], "name": fr_en(rd["name"]), "level": info.get("level"), "players": info.get("players"),
            "location": fr_en(info.get("location") or {"en": ""}), "attune": att.get("quest"), "attune_req": att.get("reqlevel"),
            "bosses": [{"name": fr_en(b["name"]), "npc": b.get("npc"), "type": fr_en(b.get("type") or {"en": ""}),
                        "abilities": [{"id": a["id"], "n": a["name"]} for a in b.get("abilities", [])],
                        "drops": [loot_item(it) for it in b.get("drops", [])]} for b in rd.get("bosses", [])],
            # loot of the raid whose boss the site doesn't know yet
            "other": [loot_item(it) for it in rd.get("items", []) if not it.get("src")],
        })
    return out


def bis_data():
    """Level-20 best-in-slot gear per spec (data/wow_items/bis_gear_by_slot.json), for BrokenDPS."""
    path = ROOT / "data" / "wow_items" / "bis_gear_by_slot.json"
    if not path.exists():
        return {}
    out = {}
    for spec, rows in json.loads(path.read_text(encoding="utf-8")).get("specs", {}).items():
        out[spec] = [{"slot": r["slot"], "id": r.get("wowhead_item_id"), "n": r.get("name"),
                      "icon": (r.get("icon") or "").rsplit("/", 1)[-1].replace(".jpg", "") or None}
                     for r in rows if r.get("wowhead_item_id")]
    return out


def talent_builds():
    """Recommended talent nodes per spec (Icy Veins level-20 templates, data/wow_guides/content.json)
    and the site guide path. Only node ids: the addon shows how many the player follows and links
    to the guide for the details (user decision: keep the full guide on the site, 2026-09-26)."""
    content = json.loads((ROOT / "data" / "wow_guides" / "content.json").read_text(encoding="utf-8"))
    out = {}
    for spec_id, prof in sim.ROTATIONS.items():
        cls, spec = prof.get("glossary", spec_id), sim.SPEC_ID_MAP.get(spec_id)
        build = content.get(cls, {}).get(spec, {}).get("build") or {}
        out[spec_id] = {
            "guide": f"wow-forever/guides/{cls}/{spec}/",
            "level": build.get("level"),
            "core": [int(t["id"].lstrip("n")) for t in build.get("talents", []) if not t.get("option")],
            "optional": [int(t["id"].lstrip("n")) for t in build.get("talents", []) if t.get("option")],
        }
    return out


def profession_routes():
    out = {}
    for f in sorted((ROOT / "data" / "wow_professions").glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        line = PROF_SKILL_LINES.get(p["id"])
        if not line:
            continue
        out[line] = {"id": p["id"], "name": {"frFR": p["name"]["fr"], "enUS": p["name"]["en"]}, "cap": p["cap"], "steps": [
            {"f": s["from"], "t": s["to"], "c": s["crafts"], "recipe": s["recipe"],
             "name": {"frFR": s["name"]["fr"], "enUS": s["name"]["en"]},
             "icon": (s.get("creates") or {}).get("icon"), "item": (s.get("creates") or {}).get("id"),
             "q": (s.get("creates") or {}).get("count") or 1,
             "reag": [reagent(g) for g in s["reagents"]]}
            for s in p["route"]],
            "made": made_by(p)}
    return out


def reagent(g):
    """Route reagent for the addon's pricing: k = v(endor) / f(arm) / c(rafted) / d(isenchant),
    v = vendor price in copper (vendor reagents only)."""
    price = g.get("price") or {}
    r = {"id": g["id"], "n": g["count"], "k": (price.get("kind") or "farm")[0], "icon": g.get("icon"),
         "name": {"frFR": g["name"]["fr"], "enUS": g["name"]["en"]}}
    if price.get("kind") == "vendor":
        r["v"] = price.get("copper") or 0
    return r


def made_by(p):
    """Recipes of the reagents this profession crafts itself (Cured Heavy Hide...), two levels deep,
    so the addon can price them at the cheaper of the auction house and their crafting cost."""
    recipes = {r["creates"]["id"]: r for r in p.get("recipes", []) if r.get("creates")}
    wanted = [g["id"] for s in p["route"] for g in s["reagents"] if (g.get("price") or {}).get("kind") == "craft"]
    out, depth = {}, 0
    while wanted and depth < 3:
        nxt = []
        for item in wanted:
            r = recipes.get(item)
            if not r or item in out:
                continue
            out[item] = {"n": r["creates"].get("count") or 1, "reag": [reagent(g) for g in r["reagents"]]}
            nxt += [g["id"] for g in r["reagents"] if (g.get("price") or {}).get("kind") == "craft"]
        wanted, depth = nxt, depth + 1
    return out


def all_recipes():
    """Every recipe of every profession, for the addon's workshop (profitable crafts, recipes to learn)
    and the craft requests board. Keyed by the crafted item's ID, or minus the spell ID when the recipe
    makes no item (enchantments), like the addon's recorded recipes. Names go to a shared table.
      s spell, l learn level, c difficulty colours, q items made, a source (t trainer, v vendor,
      d drop / other, s starting recipe), ac source cost (copper), np vendor NPC, r reagents."""
    recipes, names = {}, {}
    for f in sorted((ROOT / "data" / "wow_professions").glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        line = PROF_SKILL_LINES.get(p["id"])
        if not line:
            continue
        out = {}
        for r in p.get("recipes", []):
            cr = r.get("creates")
            key = cr["id"] if cr else -r["id"]
            names[key] = [(cr or r)["name"]["fr"], (cr or r)["name"]["en"]]
            acq = r.get("acquire") or {}
            kind = {"trainer": "t", "vendor": "v", "start": "s"}.get(acq.get("type"), "d")
            # Reagents as one compact string "id:n:kind[:vendor copper],..." (decoded by the addon on use):
            # a table per reagent made Data.lua 1 MB.
            regs = [reagent(g) for g in r.get("reagents", [])]
            e = {"s": r["id"], "l": r.get("learn_at") or 1, "c": r.get("colors") or [], "a": kind,
                 "r": ",".join(f"{g['id']}:{g['n']}:{g['k']}" + (f":{g['v']}" if "v" in g else "") for g in regs)}
            if cr and (cr.get("count") or 1) != 1:
                e["q"] = cr["count"]
            if acq.get("cost"):
                e["ac"] = acq["cost"]
            if acq.get("npc"):
                e["np"] = acq["npc"]
            for g in regs:
                names.setdefault(g["id"], [g["name"]["frFR"], g["name"]["enUS"]])
            out[key] = e
        recipes[line] = out
    return recipes, names


def write_data_lua():
    dungeons, loot = loot_data()
    prof = json.loads((ROOT / "data" / "wow_items" / "proficiency.json").read_text(encoding="utf-8"))["classes"]
    recipes, names = all_recipes()
    raids = raids_data()
    art, raid_images = dungeon_art()
    nl = chr(10)
    head = [
        "-- GENERATED by wow_addon_build.py (--data-only) from the site's data files -- do not edit by hand.",
        f"-- {date.today().isoformat()}.",
    ]
    files = {
        "hub": head + [
            "-- Shared by the suite: dungeons and their loot (BrokenDPS upgrades, BrokenCodex). Source: data/wow_dungeons.",
            "local _, ns = ...",
            "ns.DUNGEONS = {" + nl + ("," + nl).join("  " + lua(x) for x in dungeons) + nl + "}",
            "ns.LOOT = {" + nl + ("," + nl).join("  " + lua(x) for x in loot) + nl + "}",
        ],
        "dps": head + [
            "-- BrokenDPS: armor/weapon proficiency (beta client tables), level-20 talent templates (Icy Veins),",
            "-- level-20 best-in-slot gear per spec (data/wow_items/bis_gear_by_slot.json).",
            "local ns = BrokenMetaNS",
            "ns.PROFICIENCY = " + lua(prof),
            "ns.TALENT_BUILDS = {" + nl + ("," + nl).join(f"  {k} = {lua(v)}" for k, v in talent_builds().items()) + nl + "}",
            "ns.BIS = {" + nl + ("," + nl).join(f"  {k} = {lua(v)}" for k, v in bis_data().items()) + nl + "}",
        ],
        "crafter": head + [
            "-- BrokenCrafter: profession routes and every recipe (data/wow_professions).",
            "local ns = BrokenMetaNS",
            "ns.PROFESSIONS = {" + nl + ("," + nl).join(f"  [{k}] = {lua(v)}" for k, v in profession_routes().items()) + nl + "}",
            "-- Every recipe (workshop, recipes to learn, craft requests): see all_recipes() in wow_addon_build.py.",
            "ns.RECIPES = {" + nl + ("," + nl).join(
                f"  [{line}] = {{" + ", ".join(f"[{k}] = {lua(v)}" for k, v in sorted(rs.items())) + "}"
                for line, rs in recipes.items()) + nl + "}",
            "ns.ITEM_NAMES = {" + ", ".join(f"[{k}] = {lua(v)}" for k, v in sorted(names.items())) + "}",
        ],
        "codex": head + [
            "-- BrokenCodex: raids, their bosses, abilities and loot (data/wow_raids/raids.json).",
            "local ns = BrokenMetaNS",
            "ns.RAIDS = {" + nl + ("," + nl).join("  " + lua(x) for x in raids) + nl + "}",
            "-- Per dungeon (same order as ns.DUNGEONS): its loading screen (FileDataID of the game's own image)",
            "-- and its bosses in the game's order, with the NPC id used for the head (wow_codex_art_build.py).",
            "ns.DUNGEON_ART = {" + nl + ("," + nl).join("  " + lua(x) for x in art) + nl + "}",
            "ns.RAID_IMAGES = " + lua(raid_images),
        ],
    }
    for key, parts in files.items():
        DATA_OUT[key].parent.mkdir(parents=True, exist_ok=True)
        DATA_OUT[key].write_text(nl.join(parts) + nl, encoding="utf-8")
    print(f"wrote 4 Data.lua ({len(loot)} loot items, {len(dungeons)} dungeons, {len(raids)} raid(s))")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--iterations", type=int, default=800)
    parser.add_argument("--fight-len", type=float, default=300.0)
    parser.add_argument("--data-only", action="store_true", help="only rewrite Data.lua (no simulation)")
    args = parser.parse_args()
    write_data_lua()
    if args.data_only:
        return

    rows = {}
    for spec_id in sim.ROTATIONS:
        r = weights_for(spec_id, args.iterations, args.fight_len)
        if r is None:
            print(f"{spec_id}: no BiS data, skipped")
            continue
        rows[spec_id] = r
        w = r[2]
        print(f"{spec_id:22s} {r[0]:7.2f} DPS  " + "  ".join(f"{k}={w[k]:.3f}" for k in w))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "-- GENERATED by wow_addon_build.py -- do not edit by hand, re-run the script instead.\n"
        f"-- {date.today().isoformat()}, {args.iterations} fights x {args.fight_len:.0f}s per point, level-20 BiS gear.\n"
        "-- w = simulated DPS gained per +1 of: str/agi/int/ap/sp (points), crit/hit (percentage points).\n"
        "local ns = BrokenMetaNS -- BrokenDPS, part of the Broken Meta suite\n"
        "ns.WEIGHTS = {\n" + lua_table(rows) + "\n}\n\n"
        "-- Talent tree index per talent node id (the client's TraitNode ids), from data/wow_talents.\n"
        + talent_nodes_lua() + "\n",
        encoding="utf-8",
    )
    print(f"\nwrote {OUT.relative_to(ROOT)} ({len(rows)} specs)")


if __name__ == "__main__":
    main()
