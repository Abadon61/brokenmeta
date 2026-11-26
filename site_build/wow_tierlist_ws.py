"""DPS ranking from the WoWSims Forever engine (2026-11-26, user decision): github.com/wowsims/forever, MIT license, credited
with a visible link. data/wow_ranking_wowsims_by_spec.json comes from site_build/wowsims_rank/ (run_requests.py + compare.py):
the presets of wowsims.com/forever (Export > CLI) simulated with their CLI. Only the DPS specs switch: tanks keep our own
simulator until their presets are exported. A spec WoWSims has no complete build for (feral cat) is left out, not guessed."""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SRC = PROJECT / "data" / "wow_ranking_wowsims_by_spec.json"
REPO = "https://github.com/wowsims/forever"
SITE = "https://www.wowsims.com/forever/"
NOT_RANKED = {"druid_feral"}     # WoWSims has no feral build preset yet: its page default (Tauren, pre-raid) is not a build


def load():
    return json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else None


def apply(rows, ws):
    """DPS rows with WoWSims' DPS and margin (stdev / sqrt(iterations)); the row's page becomes the spec guide."""
    by = {r["spec"]: r for r in ws["specs"]}
    out = []
    for r in rows:
        w = by.get(r["spec_id"])
        if not w or r["spec_id"] in NOT_RANKED:
            continue
        out.append(dict(r, dps=w["dps"], sem=round(w["stdev"] / w["iterations"] ** 0.5, 1), ws=w, page_path=r["guide_path"]))
    out.sort(key=lambda x: x["dps"], reverse=True)
    return out


def meta(ws):
    commit = (ws.get("engine_commit") or "").split()
    return {"generated": ws["generated"][:10], "fight": 180, "iters": ws["iterations"], "build": "WoWSims " + (commit[0] if commit else "")}


CREDIT = {"fr": f'Moteur de simulation : <a href="{REPO}" rel="noopener" target="_blank">WoWSims Forever</a> (licence MIT), préréglages de <a href="{SITE}" rel="noopener" target="_blank">wowsims.com</a>.',
          "en": f'Simulation engine: <a href="{REPO}" rel="noopener" target="_blank">WoWSims Forever</a> (MIT license), presets from <a href="{SITE}" rel="noopener" target="_blank">wowsims.com</a>.'}

# text overrides of wow_tierlist.TX (same placeholders); everything not listed keeps the TX text
TX = {
    "fr": {
        "desc": "Tier list DPS WoW Forever niveau 60, simulée avec le moteur WoWSims le {date} : spécialisations classées, tanks et méthode.",
        "intro": "Chaque spécialisation DPS est simulée avec le moteur open source WoWSims Forever, sur le build Pre-BiS que WoWSims propose pour elle (équipement de donjons, de quêtes et de fabrication, sans objet de raid : les raids ouvrent le 9 décembre). Les paliers S à D viennent de l'écart avec la meilleure spécialisation : rien n'est placé à la main.",
        "chips": ["Moteur WoWSims Forever", "Builds Pre-BiS", "Mise à jour le {date}"],
        "best": "Le meilleur DPS simulé aujourd'hui est {name} avec {dps} DPS ; les paliers se calculent à partir de cette valeur.",
        "quick_top": "{top_name} est la spécialisation DPS la plus forte avec le moteur WoWSims ({top_dps} DPS).",
        "choose_intro": "Ces simulations mesurent la puissance sur une cible, pas le plaisir de jeu. Voici la meilleure spécialisation de chaque style, et ce que nous ne pouvons pas encore dire.",
        "open_rank": "Guide",
        "choose_dung_p": "ces simulations portent sur une cible unique, sans dégâts de zone ; le butin et les boss sont dans les",
        "tank_note": "Les tanks sont classés à la menace par seconde (TPS) par notre propre simulateur, sans palier : WoWSims ne fournit pas encore ces chiffres ici, et la survie n'est pas simulée.",
        "meth": [
            "Moteur : <a href=\"" + REPO + "\" rel=\"noopener\" target=\"_blank\">WoWSims Forever</a> (licence MIT), le simulateur open source de la communauté, lancé chez nous avec son outil en ligne de commande ({build}).",
            "Builds : pour chaque spécialisation, le préréglage « Pre-BiS » de <a href=\"" + SITE + "\" rel=\"noopener\" target=\"_blank\">wowsims.com</a> (équipement, talents, rotation, consommables et buffs de raid), tel que leur site l'exporte. Quand une spécialisation a plusieurs préréglages, le plus fort est retenu.",
            "Combat : {fight} secondes (à 5 s près) contre un boss de niveau 63, {iters} combats par spécialisation ; le DPS affiché est la moyenne.",
            "Paliers : S = au moins {S} % du DPS de la meilleure spécialisation, A = {A} %, B = {B} %, C = {C} %, D = en dessous. Les tanks sont comparés entre eux, sur la menace par seconde.",
            "Non classé : le Druide farouche, pour lequel WoWSims ne propose pas encore de build complet. Nous ne publions pas un chiffre tiré de réglages par défaut.",
            "Limites : pas d'objet de raid (les builds sont Pre-BiS), combat sur une cible sans déplacements. Le classement bougera avec les raids du 9 décembre et les mises à jour de WoWSims.",
        ],
        "faq0": ("Quelle est la meilleure classe de WoW Forever au niveau 60 ?", "Avec le moteur WoWSims et les builds Pre-BiS, la spécialisation DPS la plus haute est {name} ({dps} DPS). Le palier S compte : {s_list}. Le classement complet des {n} spécialisations DPS est sur cette page, avec la méthode."),
        "chg_h": "Ce qui a changé avec le moteur WoWSims",
        "chg_p": "{reason}. Les écarts ci-dessous comparent les chiffres WoWSims à ceux de notre ancien simulateur, qui incluait des objets de raid.",
        "chg_reason": "Le classement DPS est désormais calculé avec le moteur WoWSims Forever, sur les builds Pre-BiS de WoWSims",
        "chg_note": "Les tanks restent sur notre simulateur pour le moment.",
        "cond_h": "Conditions de simulation et marge d'erreur",
        "cond_p": "Chaque chiffre DPS de cette page est la moyenne de {iters} combats simulés de {fight} secondes contre un boss de niveau 63, avec le moteur WoWSims et le build Pre-BiS de chaque spécialisation.",
        "cond": ["Buffs, affaiblissements du boss et consommables : ceux du préréglage WoWSims de chaque spécialisation.",
                 "Équipement : le préréglage « Pre-BiS » de WoWSims (donjons, quêtes, fabrication), sans objet de raid.",
                 "Marge d'erreur : chaque ligne affiche l'erreur standard de la moyenne (±). La plus grande est de ± {sem_max} DPS ; l'écart le plus serré entre deux voisines est de {gap_min} DPS ({gap_pair}). {tie}"],
        "cmp_h": "D'où viennent ces chiffres",
        "cmp_p": "Le classement DPS utilise le moteur de WoWSims Forever, le simulateur de référence de la communauté, avec les builds qu'il propose. Notre ancien moteur incluait des objets de raid et donnait d'autres valeurs : les chiffres ne se comparent pas d'une version à l'autre.",
    },
    "en": {
        "desc": "WoW Forever level 60 DPS tier list, simulated with the WoWSims engine on {date}: every spec ranked, tanks and method shown.",
        "intro": "Each DPS spec is simulated with the open-source WoWSims Forever engine, on the Pre-BiS build WoWSims offers for it (dungeon, quest and crafted gear, no raid items: raids open on December 9). Tiers S to D come from the gap to the best spec: nothing is placed by hand.",
        "chips": ["WoWSims Forever engine", "Pre-BiS builds", "Updated {date}"],
        "best": "The highest simulated DPS today is {name} with {dps} DPS; the tiers are computed from that value.",
        "quick_top": "{top_name} is the strongest DPS spec with the WoWSims engine ({top_dps} DPS).",
        "choose_intro": "These simulations measure single-target power, not how fun a class is. Here is the best spec of each style, and what we cannot say yet.",
        "open_rank": "Guide",
        "choose_dung_p": "these simulations are single target, with no area damage; loot and bosses are in the",
        "tank_note": "Tanks are ranked by threat per second (TPS) by our own simulator, with no tier letter: WoWSims numbers are not available here yet, and survivability is not simulated.",
        "meth": [
            "Engine: <a href=\"" + REPO + "\" rel=\"noopener\" target=\"_blank\">WoWSims Forever</a> (MIT license), the community's open-source simulator, run on our side with its command-line tool ({build}).",
            "Builds: for each spec, the \"Pre-BiS\" preset of <a href=\"" + SITE + "\" rel=\"noopener\" target=\"_blank\">wowsims.com</a> (gear, talents, rotation, consumables and raid buffs), as their site exports it. When a spec has several presets, the strongest one is kept.",
            "Fight: {fight} seconds (give or take 5 s) against a level 63 boss, {iters} fights per spec; the DPS shown is the mean.",
            "Tiers: S = at least {S}% of the best spec's DPS, A = {A}%, B = {B}%, C = {C}%, D = below. Tanks are compared with each other, on threat per second.",
            "Not ranked: Feral Druid, which WoWSims does not offer a complete build for yet. We do not publish a number taken from default settings.",
            "Limits: no raid items (the builds are Pre-BiS), a single-target fight with no movement. The ranking will move with the December 9 raids and WoWSims updates.",
        ],
        "faq0": ("What is the best class in WoW: Forever at level 60?", "With the WoWSims engine and Pre-BiS builds, the highest DPS spec is {name} ({dps} DPS). The full ranking of the {n} DPS specs is on this page, with the method."),
        "chg_h": "What changed with the WoWSims engine",
        "chg_p": "{reason}. The gaps below compare the WoWSims numbers with those of our former simulator, which included raid items.",
        "chg_reason": "The DPS ranking is now computed with the WoWSims Forever engine, on WoWSims' Pre-BiS builds",
        "chg_note": "Tanks stay on our simulator for now.",
        "cond_h": "Simulation conditions and margin of error",
        "cond_p": "Every DPS number on this page is the mean of {iters} simulated {fight}-second fights against a level 63 boss, with the WoWSims engine and each spec's Pre-BiS build.",
        "cond": ["Buffs, boss debuffs and consumables: those of each spec's WoWSims preset.",
                 "Gear: WoWSims' \"Pre-BiS\" preset (dungeons, quests, crafting), no raid items.",
                 "Margin of error: each row shows the standard error of the mean (±). The largest is ± {sem_max} DPS; the tightest gap between two neighbours is {gap_min} DPS ({gap_pair}). {tie}"],
        "cmp_h": "Where these numbers come from",
        "cmp_p": "The DPS ranking uses the engine of WoWSims Forever, the community's reference simulator, with the builds it offers. Our former engine included raid items and gave other values: the numbers do not compare from one version to the other.",
    },
}


def hub_tx(hx, lang):
    """The tier-list hub's texts with the DPS ranking credited to the WoWSims engine (tanks stay on our simulator)."""
    fr = lang == "fr"
    sw = (("Dans notre simulation", "Avec le moteur WoWSims"), ("dans notre simulation", "avec le moteur WoWSims")) if fr else          (("In our simulation", "With the WoWSims engine"), ("in our simulation", "with the WoWSims engine"))
    def fix(t):
        for a, b in sw:
            t = t.replace(a, b)
        return t
    return {"chips": ["Moteur WoWSims Forever (DPS)", "Recalculé le {date}"] if fr else ["WoWSims Forever engine (DPS)", "Recomputed {date}"],
            "faq": [(q, fix(a)) for q, a in hx["faq"]], "intro": fix(hx["intro"])}
