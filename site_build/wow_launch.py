"""'At launch' tile of the specialization guides: the short answer (talents, opening rotation, pre-raid gear, consumables) built only from
data/wow_prebis60.json (simulator run without raid drops, see sim60/ranking.mjs RANK_NORAID), data/wow_ranking60.json and data/wow_guides/builds60.json."""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent


def patch_of(build):
    """'1.60.1.69913' -> '1.60.1'"""
    return ".".join(str(build).split(".")[:3])


def load_meta():
    p = PROJECT / "data" / "wow_prebis60.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    return {"generated": d["generated"], "build": d["build"], "fight": d["fightLen"], "iters": d["iterations"]}


def title(lang, cls, spec, patch):
    """Longest title (<= 60 characters) among the candidates; the patch number stays in all of them."""
    cands = TITLES[lang]
    for c in cands:
        t = c.format(cls=cls, spec=spec, patch=patch)
        if len(t) <= 60:
            return t
    raise AssertionError(("title too long", cls, spec))


TITLES = {
    "fr": ["{cls} {spec} WoW: Forever {patch} : guide, talents, BiS", "{cls} {spec} Forever {patch} : guide, talents, BiS", "{cls} {spec} Forever {patch} : talents, BiS", "{cls} {spec} Forever {patch} : talents"],
    "en": ["{spec} {cls} WoW: Forever {patch}: guide, talents, BiS", "{spec} {cls} Forever {patch}: guide, talents, BiS", "{spec} {cls} Forever {patch}: talents, BiS", "{spec} {cls} Forever {patch}: talents"],
}


def build(lang, cls, rows, pre_rows, lvl60, pre60, builds_entry, meta):
    """Data of the tile. rows / pre_rows: ranking rows of the spec (with details) from the full and the pre-raid run; lvl60 / pre60: their _guide_level60 views."""
    out = {"patch": patch_of(meta["build"]), "build": meta["build"], "meta": meta}
    # talents: points per tree (builds60.json lists them in the class's tree order) and the talents the simulator values most
    split = []
    if builds_entry:
        names = [s["name"][lang] for s in cls["specs"]]
        split = [(names[i], n) for i, n in enumerate(builds_entry["trees"]) if n and i < len(names)]
        out["total"] = builds_entry["total"]
    top = []
    det = next((r["detail"] for r in rows if r.get("detail")), None)
    if det:
        fr = {t["name"]["en"]: t["name"][lang] for t in det["talents"]}
        vals = [(k, v["pct"]) for k, v in det["talentValues"].items() if v and v.get("pct", 0) > 0 and k in fr]
        vals.sort(key=lambda x: -x[1])
        top = [(fr[k], p) for k, p in vals[:3]]
    out["split"], out["top"] = split, top
    out["split_txt"] = " / ".join(f"{n} {p}" for n, p in split)
    # opening rotation: first lines of the written rotation
    rot = (lvl60.get("rot") or {}).get("sim") or []
    out["rot"] = (rot[0]["steps"][:3] if rot else [])
    out["has_rot"] = bool(lvl60.get("rot"))
    out["healer"] = bool((lvl60.get("rot") or {}).get("heal"))
    # pre-raid gear and consumables per simulated variant, with the DPS cost of leaving the raid items out
    full = {r["spec_id"]: r for r in rows}
    blocks = []
    cons_by_label = {c["label"]: c["cats"] for c in pre60.get("cons") or []}
    for blk_gear, r in zip(pre60.get("gear") or [], [x for x in pre_rows if x.get("detail")]):
        f = full.get(r["spec_id"])
        d = None
        if f and f.get("dps"):
            d = round(100.0 * (r["dps"] - f["dps"]) / f["dps"], 1)
        delta_txt = None if d is None else (f"{d:+.1f}".replace("-", "−").replace(".", ",") if lang == "fr" else f"{d:+.1f}".replace("-", "−"))
        blocks.append({"label": blk_gear["label"], "items": blk_gear["items"], "cats": cons_by_label.get(blk_gear["label"], []), "unit": "TPS" if r.get("tps") else "DPS",
                       "value": r["dps"], "full": f["dps"] if f else None, "delta_txt": delta_txt})
    out["blocks"] = blocks
    out["cons_heal"] = lvl60.get("cons_heal")
    return out


TX = {
    "fr": {
        "h2": "Au lancement : niveau 60, build {patch}", "kicker": "RÉSUMÉ",
        "meta": "Mis à jour le {date} · build des données du simulateur {build} · simulation de {fight} secondes, {iters} répétitions",
        "talents": "Talents conseillés", "t_points": "{total} points : {split}", "t_top": "Les talents qui pèsent le plus dans la simulation : {top}.", "t_link": "Voir l'arbre complet",
        "rot": "Ordre des sorts", "rot_link": "Rotation complète",
        "gear": "Équipement de pré-raid (sans objets de raid)", "gear_link": "Équipement complet, enchantements compris",
        "gear_p": "Le meilleur ensemble que le simulateur trouve parmi les objets de donjons et de métiers de la bêta, raid exclu : {value} {unit}, soit {delta} % par rapport à l'ensemble qui inclut les objets du raid ({full} {unit}).",
        "gear_p_nodelta": "Le meilleur ensemble que le simulateur trouve parmi les objets de donjons et de métiers de la bêta, raid exclu : {value} {unit}.",
        "gear_none": "Pas de liste d'équipement simulée pour les soigneurs : le simulateur ne modélise pas encore les soins sur un combat complet. Les objets conseillés ne sont donc pas affichés ici.",
        "cons": "Consommables", "cons_link": "Tous les consommables", "cons_heal": "Consommables conseillés",
        "gain": "+{g} {u}", "source_note": "Chiffres issus de notre simulateur, sans valeur de joueur : ils bougent avec les correctifs de la bêta.",
    },
    "en": {
        "h2": "At launch: level 60, build {patch}", "kicker": "SUMMARY",
        "meta": "Updated {date} · simulator data build {build} · {fight}-second simulation, {iters} runs",
        "talents": "Recommended talents", "t_points": "{total} points: {split}", "t_top": "The talents that weigh the most in the simulation: {top}.", "t_link": "See the full tree",
        "rot": "Spell order", "rot_link": "Full rotation",
        "gear": "Pre-raid gear (no raid items)", "gear_link": "Full gear, enchantments included",
        "gear_p": "The best set the simulator finds among the beta's dungeon and profession items, raid excluded: {value} {unit}, {delta}% against the set that includes raid items ({full} {unit}).",
        "gear_p_nodelta": "The best set the simulator finds among the beta's dungeon and profession items, raid excluded: {value} {unit}.",
        "gear_none": "No simulated gear list for healers: the simulator does not model healing over a full fight yet, so recommended items are not shown here.",
        "cons": "Consumables", "cons_link": "All consumables", "cons_heal": "Recommended consumables",
        "gain": "+{g} {u}", "source_note": "Figures come from our simulator, not from players: they move with beta patches.",
    },
}
