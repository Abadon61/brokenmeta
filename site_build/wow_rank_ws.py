"""Spec pages of the DPS ranking on the WoWSims Forever engine (2026-11-26): /wow-forever/classement/<slug>/.
One page per ranked spec, built from data/wow_ranking_wowsims_detail.json (site_build/wowsims_rank/details.py): the WoWSims
preset that gives the spec its rank (talents, gear, enchantments, race, professions, consumables, raid buffs, boss debuffs),
the character sheet and the damage by source the engine computes, and the cross-check of that build against the Wowhead
Forever class guides (wowsims_rank/wowhead_check_2026-11-26.json). Nothing here is chosen by us: the build is WoWSims'."""
import json
from pathlib import Path

from markupsafe import Markup, escape

import wow_guides
import wow_rank_texts

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
DETAIL = PROJECT / "data" / "wow_ranking_wowsims_detail.json"
CHECK = ROOT / "wowsims_rank" / "wowhead_check_2026-11-26.json"
REPO = "https://github.com/wowsims/forever"
SITE = "https://www.wowsims.com/forever/"
ICON = "https://wow.zamimg.com/images/wow/icons/medium/{}.jpg"
WH_CLASS = {"warrior": "warrior", "rogue": "rogue", "hunter": "hunter", "mage": "mage", "warlock": "warlock", "shaman": "shaman", "druid": "druid", "priest": "priest", "paladin": "paladin"}
RACES = {"Orc": ("Orc", "Orc"), "Human": ("Humain", "Human"), "Dwarf": ("Nain", "Dwarf"), "NightElf": ("Elfe de la nuit", "Night Elf"), "Gnome": ("Gnome", "Gnome"),
         "Troll": ("Troll", "Troll"), "Undead": ("Mort-vivant", "Undead"), "Tauren": ("Tauren", "Tauren"),
         "WindshaperSkyborne": ("Skyborne (Windshaper)", "Skyborne (Windshaper)"), "SkyborneHorde": ("Skyborne", "Skyborne"), "SkyborneAlliance": ("Skyborne", "Skyborne")}
PROFS = {"Alchemy": ("Alchimie", "Alchemy"), "Blacksmithing": ("Forge", "Blacksmithing"), "Enchanting": ("Enchantement", "Enchanting"), "Engineering": ("Ingénierie", "Engineering"),
         "Herbalism": ("Herboristerie", "Herbalism"), "Leatherworking": ("Travail du cuir", "Leatherworking"), "Mining": ("Minage", "Mining"), "Skinning": ("Dépeçage", "Skinning"), "Tailoring": ("Couture", "Tailoring")}
CONS_KIND = {"fr": {"flask": "Flacon", "elixir": "Élixir", "food": "Nourriture", "imbue_mh": "Arme (main droite)", "imbue_oh": "Arme (main gauche)", "potion": "Potion",
                    "conjured": "Rune", "explosive": "Explosif", "extra": "Autre"},
             "en": {"flask": "Flask", "elixir": "Elixir", "food": "Food", "imbue_mh": "Weapon (main hand)", "imbue_oh": "Weapon (off hand)", "potion": "Potion",
                    "conjured": "Rune", "explosive": "Explosive", "extra": "Other"}}

TX = {
    "fr": {
        "title": "{cls} {spec} WoW Forever : build WoWSims et DPS",
        "desc": "{cls} {spec} niveau 60 dans WoW Forever : talents, équipement Pre-BiS, enchantements et dégâts simulés avec le moteur WoWSims ({dps} DPS).",
        "kicker": "WoW: Forever · Classement DPS · Fiche",
        "h1": "{cls} {spec} : le build simulé",
        "intro": "Le build exact qui donne à {cls} {spec} sa place dans le classement : talents, équipement, enchantements, consommables et buffs du préréglage « Pre-BiS » de WoWSims, simulé avec leur moteur sur {iters} combats de {fight} secondes contre un boss de niveau 63.",
        "dps": "DPS", "rank": "du classement", "of": "sur {n}", "race": "Race", "preset": "Préréglage",
        "sim_btn": "Simuler ce build", "guide_btn": "Guide de la spécialisation",
        "check_h": "Vérifié avec les guides Wowhead",
        "chk_same": "Talents identiques au build « {b} » du guide Wowhead.",
        "chk_diff": "Talents à {n} point(s) près du build « {b} » du guide Wowhead.",
        "chk_far": "Talents différents du build « {b} » du guide Wowhead ({n} points d'écart) : WoWSims retient une autre variante.",
        "chk_gear": "{a} objets sur {b} figurent dans la liste « Best in Slot » du guide Wowhead.",
        "chk_gear_none": "L'équipement n'a pas pu être comparé (la liste Wowhead n'est que dans un planificateur d'équipement).",
        "chk_trees": "Les arbres de talents sont ceux de Wowhead, vérifiés talent par talent.",
        "sec_talents": "Talents", "points": "points", "wh_calc": "Ouvrir ce build dans le calculateur Wowhead", "legend": "Talent pris par le build",
        "sec_dmg": "Dégâts par source", "dmg_p": "Part des dégâts de chaque technique, effet ou familier, moyenne de {iters} combats.",
        "col_src": "Source", "col_share": "Part", "col_dps": "DPS", "col_casts": "Par combat", "col_crit": "Critique",
        "sec_up": "Effets et temps actif", "up_p": "Part du combat pendant laquelle chaque effet temporaire est actif.",
        "sec_stats": "Fiche du personnage", "stats_p": "Caractéristiques finales calculées par le moteur, avec l'équipement, les talents, les buffs et les consommables.",
        "st_ap": "Puissance d'attaque", "st_rap": "Puissance d'attaque à distance", "st_sp": "Puissance des sorts", "st_hit": "Toucher (mêlée)", "st_crit": "Critique (mêlée)",
        "st_shit": "Toucher (sorts)", "st_scrit": "Critique (sorts)", "st_rcrit": "Critique (distance)", "st_mana": "Mana", "st_hp": "Points de vie", "st_mp5": "Mana / 5 s", "st_armor": "Armure",
        "sec_gear": "Équipement", "gear_p": "Les objets du préréglage, avec leur provenance et leur enchantement. Le lien ouvre l'objet sur Wowhead.",
        "src_craft": "Fabrication", "src_vendor": "Marchand", "src_quest": "Quête", "src_rep": "Réputation", "src_pvp": "JcJ", "src_drop": "Butin",
        "sets": "Bonus d'ensemble actifs",
        "sec_setup": "Consommables, buffs et affaiblissements", "cons": "Consommables", "buffs": "Buffs de raid", "debuffs": "Affaiblissements du boss", "profs": "Métiers",
        "sec_method": "Méthode", "method": [
            "Build : le préréglage de WoWSims pour cette spécialisation, exporté tel quel depuis wowsims.com (Export > CLI). Quand la spécialisation a plusieurs préréglages, celui qui donne le DPS le plus haut est retenu. Nous n'avons rien changé.",
            "Moteur : WoWSims Forever (licence MIT), lancé chez nous. Le DPS du classement vient de {iters_rank} combats ; le détail des dégâts de cette page, de {iters} combats (les parts sont les mêmes à quelques dixièmes près).",
            "Limites : combat sur une cible, sans déplacements, pas d'objet de raid (les raids ouvrent le 9 décembre)."],
        "credit": "Moteur et builds : <a href=\"" + REPO + "\" rel=\"noopener\" target=\"_blank\">WoWSims Forever</a> (licence MIT), préréglages de <a href=\"" + SITE + "\" rel=\"noopener\" target=\"_blank\">wowsims.com</a>. Vérification : guides de classe de <a href=\"https://www.wowhead.com/forever/guides/classes\" rel=\"noopener nofollow\" target=\"_blank\">Wowhead</a>.",
        "l_rank": "Tier list DPS", "l_sim": "Simulateur DPS", "l_calc": "Calculateur de talents",
        "auto": "attaque automatique", "pet": "familier", "proc": "effet", "others": "Autres",
        "p_tal": "Talents", "p_same": "Identiques", "p_pts": "{n} pts d'écart", "p_gear": "Objets dans la liste BiS", "p_trees": "Arbres de talents", "p_trees_v": "Conformes",
        "p_vs": "comparé au build « {b} » du guide Wowhead", "p_prim": "Caractéristiques", "p_combat": "Combat", "comp_h": "Répartition des dégâts",
    },
    "en": {
        "title": "{spec} {cls} WoW Forever: WoWSims build and DPS",
        "desc": "Level 60 {spec} {cls} in WoW Forever: talents, Pre-BiS gear, enchantments and damage simulated with the WoWSims engine ({dps} DPS).",
        "kicker": "WoW: Forever · DPS ranking · Spec page",
        "h1": "{spec} {cls}: the simulated build",
        "intro": "The exact build that gives {spec} {cls} its place in the ranking: talents, gear, enchantments, consumables and buffs of WoWSims' \"Pre-BiS\" preset, simulated with their engine over {iters} fights of {fight} seconds against a level 63 boss.",
        "dps": "DPS", "rank": "in the ranking", "of": "of {n}", "race": "Race", "preset": "Preset",
        "sim_btn": "Simulate this build", "guide_btn": "Spec guide",
        "check_h": "Checked against the Wowhead guides",
        "chk_same": "Talents identical to the \"{b}\" build of the Wowhead guide.",
        "chk_diff": "Talents within {n} point(s) of the \"{b}\" build of the Wowhead guide.",
        "chk_far": "Talents differ from the \"{b}\" build of the Wowhead guide ({n} points apart): WoWSims uses another variant.",
        "chk_gear": "{a} of {b} items are on the Wowhead guide's Best in Slot list.",
        "chk_gear_none": "The gear could not be compared (the Wowhead list is only in a gear planner).",
        "chk_trees": "The talent trees are Wowhead's, checked talent by talent.",
        "sec_talents": "Talents", "points": "points", "wh_calc": "Open this build in the Wowhead talent calculator", "legend": "Talent taken by the build",
        "sec_dmg": "Damage by source", "dmg_p": "Share of the damage of each ability, effect or pet, mean of {iters} fights.",
        "col_src": "Source", "col_share": "Share", "col_dps": "DPS", "col_casts": "Per fight", "col_crit": "Crit",
        "sec_up": "Effects and uptime", "up_p": "Share of the fight each temporary effect is active.",
        "sec_stats": "Character sheet", "stats_p": "Final stats computed by the engine, with gear, talents, buffs and consumables.",
        "st_ap": "Attack power", "st_rap": "Ranged attack power", "st_sp": "Spell power", "st_hit": "Hit (melee)", "st_crit": "Crit (melee)",
        "st_shit": "Hit (spells)", "st_scrit": "Crit (spells)", "st_rcrit": "Crit (ranged)", "st_mana": "Mana", "st_hp": "Health", "st_mp5": "Mana / 5 s", "st_armor": "Armor",
        "sec_gear": "Gear", "gear_p": "The preset's items, where they come from and their enchantment. The link opens the item on Wowhead.",
        "src_craft": "Crafted", "src_vendor": "Vendor", "src_quest": "Quest", "src_rep": "Reputation", "src_pvp": "PvP", "src_drop": "Drop",
        "sets": "Active set bonuses",
        "sec_setup": "Consumables, buffs and debuffs", "cons": "Consumables", "buffs": "Raid buffs", "debuffs": "Boss debuffs", "profs": "Professions",
        "sec_method": "Method", "method": [
            "Build: WoWSims' preset for this spec, exported as is from wowsims.com (Export > CLI). When the spec has several presets, the one with the highest DPS is used. We changed nothing.",
            "Engine: WoWSims Forever (MIT license), run on our side. The ranking DPS comes from {iters_rank} fights; the damage detail of this page from {iters} fights (shares agree within a few tenths).",
            "Limits: single target, no movement, no raid items (raids open on December 9)."],
        "credit": "Engine and builds: <a href=\"" + REPO + "\" rel=\"noopener\" target=\"_blank\">WoWSims Forever</a> (MIT license), presets from <a href=\"" + SITE + "\" rel=\"noopener\" target=\"_blank\">wowsims.com</a>. Check: <a href=\"https://www.wowhead.com/forever/guides/classes\" rel=\"noopener nofollow\" target=\"_blank\">Wowhead</a> class guides.",
        "l_rank": "DPS tier list", "l_sim": "DPS simulator", "l_calc": "Talent calculator",
        "auto": "auto attack", "pet": "pet", "proc": "effect", "others": "Others",
        "p_tal": "Talents", "p_same": "Identical", "p_pts": "{n} pts apart", "p_gear": "Items on the BiS list", "p_trees": "Talent trees", "p_trees_v": "Match",
        "p_vs": "compared with the \"{b}\" build of the Wowhead guide", "p_prim": "Attributes", "p_combat": "Combat", "comp_h": "Damage breakdown",
    },
}

_CACHE = {}


def load():
    if "d" not in _CACHE:
        pj = ROOT / "wowsims_web" / "presets.json"           # the preset names as wowsims.com shows them ("Fury Pre-BiS")
        _CACHE["names"] = {p["id"]: p["preset"] for p in json.loads(pj.read_text(encoding="utf-8"))["presets"]} if pj.exists() else {}
        _CACHE["d"] = json.loads(DETAIL.read_text(encoding="utf-8"))["specs"] if DETAIL.exists() else {}
        _CACHE["c"] = json.loads(CHECK.read_text(encoding="utf-8"))["specs"] if CHECK.exists() else {}
    return _CACHE["d"], _CACHE["c"]


def num(v, lang, d=1):
    s = f"{v:,.{d}f}"
    return s.replace(",", " ").replace(".", ",") if lang == "fr" else s


def pct(v, lang, d=1):
    return num(v, lang, d) + (" %" if lang == "fr" else "%")


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def sets_view(sets, lang):
    """'Sorcerer's Regalia (2pc)' ... '(6pc)' -> one chip per set with its highest active bonus."""
    import re
    top = {}
    for x in sets:
        m = re.match(r"(.+) \((\d+)pc\)$", x)
        name, n = (m.group(1), int(m.group(2))) if m else (x, 0)
        top[name] = max(top.get(name, 0), n)
    return [f"{k} · {v} " + ("pièces" if lang == "fr" else "pieces") if v else k for k, v in top.items()]


def talent_view(lang, d, cls_name):
    """WoWSims trees in the shape of wow_talent_macros.trees (the guides' read-only tree)."""
    trees, points = [], {}
    for tr in d["talents"]:
        name = tr["name"][lang]
        flags, talents, cells = {}, [], []
        ids = {(c["row"], c["col"]): f"r{c['row']}c{c['col']}" for c in tr["cells"]}
        for c in tr["cells"]:
            tid = ids[(c["row"], c["col"])]
            t = {"id": tid, "row": c["row"] + 1, "col": c["col"] + 1, "name": c["name"], "max_rank": c["max"], "icon": ICON.format(c["icon"]) if c.get("icon") else None,
                 "gates": [{"points": 5 * c["row"]}], "requires": ids.get(tuple(c["pre"])) if c.get("pre") else None}
            talents.append(t)
            if c["points"]:
                flags[tid] = True
            cells.append({"t": t, "mark": "reco" if c["points"] else None, "points": c["points"] or None})
        sp = {"talents": talents}
        trees.append({"spec": {"name": tr["name"]}, "cells": sorted(cells, key=lambda x: (x["t"]["row"], x["t"]["col"])), "rows": max(t["row"] for t in talents),
                      "svg": wow_guides._tree_svg(sp, flags), "pts": tr["points"]})
        points[name] = tr["points"]
    trees.sort(key=lambda t: -t["pts"])
    return {"tpl": {"trees": trees}, "points": points, "tx": {"legend": TX[lang]["legend"], "points": TX[lang]["points"]}}


def page(lang, r, i, rlist, zone_path, prof_info, zone_fr):
    """Everything the template needs for one spec, or None when the spec has no WoWSims detail."""
    det, chk = load()
    d = det.get(r["spec_id"])
    if not d:
        return None
    t = TX[lang]
    fr = lang == "fr"
    L = 0 if fr else 1
    cls, spec = r["class_name"], r["spec_name"]
    ws = r.get("ws") or {}
    # damage by source
    rows = []
    for a in d["abilities"]:
        href = f"https://www.wowhead.com/forever/spell={a['sid']}" if a.get("sid") else (f"https://www.wowhead.com/forever/item={a['iid']}" if a.get("iid") else None)
        note = t["auto"] if a["kind"] == "auto" else (t["pet"] if a["kind"] == "pet" else None)
        rows.append({"name": a["name"][lang], "href": href, "note": note, "share": a["share"], "share_txt": pct(a["share"], lang), "dps": num(a["dps"], lang), "kind": a["kind"],
                     "bar": round(100 * a["share"] / max(x["share"] for x in d["abilities"]), 1),
                     "casts": num(a["casts"], lang) if a["casts"] else "—", "crit": pct(100 * a["crit"], lang, 0) if a.get("crit") else "—"})
    ups = [{"name": u["name"][lang], "sid": u["sid"], "v": pct(100 * u["uptime"], lang, 0), "w": round(100 * u["uptime"], 1)} for u in d["uptimes"]]
    # damage composition: the six biggest sources, the rest grouped
    top = d["abilities"][:6]
    comp = [{"name": a["name"][lang], "share": a["share"], "txt": pct(a["share"], lang, 0)} for a in top]
    rest = round(100 - sum(a["share"] for a in top), 1)
    if rest > 0.5:
        comp.append({"name": t["others"], "share": rest, "txt": pct(rest, lang, 0), "rest": True})
    # character sheet
    st, cid = d["stats"], r["class_id"]
    caster = cid in ("mage", "warlock", "priest") or r["spec_id"] in ("shaman_elemental", "druid_balance") or (r["spec_id"] == "paladin_retribution" and False)
    prim = [(wow_rank_texts.STAT_LABELS[lang][k], num(v, lang, 0)) for k, v in st["prim"].items() if v]
    sheet = []
    if caster:
        sheet += [(t["st_sp"], num(st["sp"], lang, 0)), (t["st_shit"], pct(st["spell_hit"], lang)), (t["st_scrit"], pct(st["spell_crit"], lang)),
                  (t["st_mana"], num(st["mana"], lang, 0)), (t["st_mp5"], num(st["mp5"], lang, 0))]
    else:
        sheet += [(t["st_ap"], num(st["ap"], lang, 0))]
        if cid == "hunter":
            sheet += [(t["st_rap"], num(st["rap"], lang, 0)), (t["st_rcrit"], pct(st["ranged_crit"], lang))]
        sheet += [(t["st_hit"], pct(st["melee_hit"], lang)), (t["st_crit"], pct(st["melee_crit"], lang))]
        if st.get("sp"):
            sheet.append((t["st_sp"], num(st["sp"], lang, 0)))
        if st.get("mana"):
            sheet.append((t["st_mana"], num(st["mana"], lang, 0)))
    sheet += [(t["st_hp"], num(st["health"], lang, 0)), (t["st_armor"], num(st["armor"], lang, 0))]
    # gear
    labels, order = wow_rank_texts.SLOTS[lang], {k: n for n, k in enumerate(wow_rank_texts.SLOT_ORDER)}
    gear = []
    for it in sorted(d["items"], key=lambda x: order.get(x["slot"], 99)):
        src, path, extra = "", None, ""
        if it["from"] == "drop":
            src, path, extra = zone_fr(it["zone"], lang), zone_path(it["zone"]), it["src"]
        elif it["from"] == "craft":
            p = prof_info(it["zone"])
            src, path = (p["name"][lang], p["path"]) if p else (t["src_craft"], None)
        elif it["from"] == "quest":
            src, extra = t["src_quest"], it["src"]
        elif it["from"] == "vendor":
            src, extra = t["src_vendor"], (it["src"] + (" (" + it["zone"] + ")" if it["zone"] else ""))
        elif it["from"] in ("rep", "pvp"):
            src = t["src_" + it["from"]]
        e = d["enchants"].get(it["slot"])
        gear.append({"slot": labels.get(it["slot"], it["slot"]), "id": it["id"], "name": it["name"][lang], "q": it.get("q") or 1, "icon": ICON.format(it["icon"]) if it.get("icon") else None, "src": src, "path": path, "extra": extra,
                     "ench": {"name": cap(e["name"][lang]), "href": f"https://www.wowhead.com/forever/spell={e['id']}"} if e else None})
    # setup
    nm = lambda x: x["name"][lang] if isinstance(x["name"], dict) else x["name"]
    cons = [{"name": nm(c), "href": f"https://www.wowhead.com/forever/item={c['id']}", "kind": CONS_KIND[lang].get(c["kind"], "")} for c in d["consumables"]]
    buffs = [{"name": cap(nm(b)), "href": f"https://www.wowhead.com/forever/spell={b['sid']}" if b.get("sid") else None} for b in d["buffs"]]
    debuffs = [{"name": cap(nm(b)), "href": f"https://www.wowhead.com/forever/spell={b['sid']}" if b.get("sid") else None} for b in d["debuffs"]]
    profs = [PROFS[p][L] for p in d["professions"] if p in PROFS]
    # Wowhead cross-check
    c = chk.get(r["spec_id"]) or {}
    checks = []
    proof = None
    if c:
        tv, g = c.get("talents"), c.get("gear")
        proof = {"build": c["wh_build"],
                 "tal": t["p_same"] if tv == "same" else t["p_pts"].format(n=tv), "tal_ok": "ok" if tv == "same" else ("near" if isinstance(tv, int) and tv <= 8 else "far"),
                 "gear": f"{g[0]}/{g[1]}" if g else "—", "gear_w": round(100 * g[0] / g[1]) if g else 0, "gear_ok": ("ok" if g and g[0] == g[1] else "near") if g else "na"}
    if c:
        tv = c.get("talents")
        if tv == "same":
            checks.append(t["chk_same"].format(b=c["wh_build"]))
        elif isinstance(tv, int):
            checks.append((t["chk_diff"] if tv <= 8 else t["chk_far"]).format(n=tv, b=c["wh_build"]))
        g = c.get("gear")
        checks.append(t["chk_gear"].format(a=g[0], b=g[1]) if g else t["chk_gear_none"])
        checks.append(t["chk_trees"])
    dps_rank = r["dps"]
    iters, iters_rank = d["iterations"], ws.get("iterations") or d["iterations"]
    pg = {
        "title": t["title"].format(cls=cls, spec=spec), "desc": t["desc"].format(cls=cls, spec=spec, dps=num(dps_rank, lang)),
        "h1": t["h1"].format(cls=cls, spec=spec), "intro": t["intro"].format(cls=cls, spec=spec, iters=num(iters_rank, lang, 0), fight=d["duration"]),
        "dps": num(dps_rank, lang), "sem": num(r.get("sem") or 0, lang), "rank": i + 1, "of": t["of"].format(n=len(rlist)),
        "race": RACES.get(d["race"], (d["race"], d["race"]))[L], "preset": _CACHE["names"].get(d["label"]) or ws.get("preset") or d.get("preset") or "Pre-BiS",
        "sim_href": f"wow-forever/simulateur-dps/?ws={d['label']}#wsSim", "calc_href": f"https://www.wowhead.com/forever/talent-calc/{WH_CLASS[cid]}/v2{d['talents_string']}",
        "tl": talent_view(lang, d, cls), "dmg": rows, "dmg_p": t["dmg_p"].format(iters=num(iters, lang, 0)), "ups": ups, "sheet": sheet, "gear": gear,
        "sets": sets_view(d.get("sets") or [], lang), "cons": cons, "buffs": buffs, "debuffs": debuffs, "profs": profs, "checks": checks, "proof": proof, "prim": prim, "comp": comp,
        "method": [m.format(iters=num(iters, lang, 0), iters_rank=num(iters_rank, lang, 0)) for m in t["method"]],
        "prev": rlist[i - 1] if i > 0 else None, "next": rlist[i + 1] if i + 1 < len(rlist) else None,
    }
    if len(pg["title"]) > 60:
        pg["title"] = pg["title"].replace(" WoW Forever", "")
    if len(pg["title"]) > 60:
        pg["title"] = pg["title"].replace(" et DPS", "").replace(" and DPS", "")
    if len(pg["desc"]) > 155:
        pg["desc"] = pg["desc"].replace(" niveau 60", "").replace("Level 60 ", "")
    if len(pg["desc"]) > 155:
        pg["desc"] = pg["desc"].replace(", enchantements", "").replace(", enchantments", "")
    return pg
