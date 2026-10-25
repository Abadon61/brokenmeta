"""Titles and descriptions of the spec guides (/wow-forever/guides/<class>/<spec>/), 2026-10-25.

Search Console (2026-10-24, 28 days): the guides sit at position 9-11 for "<spec> <class> wow forever" and the most frequent queries are
"<class> <spec> talents / build / guide". The title therefore carries those words (the patch number moves to the description), and the
description carries a real figure of the level-60 simulator (rank and simulated DPS / TPS, the same number as the guide's ranking chip),
the patch and the update date. A spec the simulator does not rank (healers) gets a description without a figure, never an invented one.
The first variant that fits is kept (titles <= 60 characters, descriptions <= 155).
"""

TITLES = {
    "fr": ["{cls} {spec} WoW Forever : build, talents, BiS, rotation", "{cls} {spec} WoW Forever : build, talents et BiS", "{cls} {spec} Forever : build, talents et BiS",
           "{cls} {spec} Forever : build et talents", "{cls} {spec} Forever : build"],
    "en": ["{spec} {cls} Guide WoW Forever: Build, Talents, BiS, Rotation", "{spec} {cls} Guide WoW Forever: Build, Talents, BiS", "{spec} {cls} Guide WoW Forever: Build & Talents",
           "{spec} {cls} Forever: Build, Talents, BiS", "{spec} {cls} Forever Guide"],
}

# {rank_txt} = "n°3 du classement DPS (706 DPS simulés)"; {rank} variants only apply when the simulator ranks the spec
DESCRIPTIONS = {
    "fr": {
        "ranked": ["{cls} {spec} dans WoW Forever : {rank_txt}. Build, talents 51 points, équipement et rotation. Patch {patch}, mis à jour le {date}.",
                   "{cls} {spec} dans WoW Forever : {rank_txt}. Build, talents, équipement et rotation. Mis à jour le {date}.",
                   "{cls} {spec} dans WoW Forever : {rank_txt}. Build, talents, BiS et rotation."],
        "unranked": ["{cls} {spec} dans WoW Forever : build, talents 51 points, équipement, rotation de soin et priorités de stats d'après les données du client. Patch {patch}, mis à jour le {date}.",
                     "{cls} {spec} dans WoW Forever : build, talents 51 points, équipement, rotation et priorités de stats. Mis à jour le {date}.",
                     "{cls} {spec} dans WoW Forever : build, talents, équipement et rotation."],
        "dps": "n°{pos} du classement DPS ({val} DPS simulés)", "tps": "n°{pos} du classement des tanks ({val} TPS simulés)",
    },
    "en": {
        "ranked": ["{spec} {cls} in WoW Forever: {rank_txt}. Build, 51-point talents, gear and rotation. Patch {patch}, updated {date}.",
                   "{spec} {cls} in WoW Forever: {rank_txt}. Build, talents, gear and rotation. Updated {date}.",
                   "{spec} {cls} in WoW Forever: {rank_txt}. Build, talents, BiS and rotation."],
        "unranked": ["{spec} {cls} in WoW Forever: build, 51-point talents, gear, healing rotation and stat priorities from the client data. Patch {patch}, updated {date}.",
                     "{spec} {cls} in WoW Forever: build, 51-point talents, gear, rotation and stat priorities. Updated {date}.",
                     "{spec} {cls} in WoW Forever: build, talents, gear and rotation."],
        "dps": "#{pos} in our DPS ranking ({val} simulated DPS)", "tps": "#{pos} in our tank ranking ({val} simulated TPS)",
    },
}
_MONTHS_SHORT = {"fr": ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."],
                 "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}


def short_date(iso, lang):
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return f"{d} {_MONTHS_SHORT['fr'][m - 1]} {y}" if lang == "fr" else f"{_MONTHS_SHORT['en'][m - 1]} {d}, {y}"


def title(lang, cls, spec):
    for c in TITLES[lang]:
        t = c.format(cls=cls, spec=spec)
        if len(t) <= 60:
            return t
    raise AssertionError(("guide title too long", cls, spec))


def description(lang, cls, spec, rank, patch, iso_date):
    """rank = {"pos", "val", "unit": "DPS" | "TPS"} (the guide's ranking chip) or None when the simulator does not rank the spec."""
    tx = DESCRIPTIONS[lang]
    date = short_date(iso_date, lang)
    sep = " " if lang == "fr" else ","
    if rank:
        val = f"{int(round(rank['val'])):,}".replace(",", sep)
        rank_txt = tx["tps" if rank["unit"] == "TPS" else "dps"].format(pos=rank["pos"], val=val)
        variants = tx["ranked"]
    else:
        rank_txt, variants = "", tx["unranked"]
    for v in variants:
        d = v.format(cls=cls, spec=spec, rank_txt=rank_txt, patch=patch, date=date)
        if len(d) <= 155:
            return d
    raise AssertionError(("guide description too long", cls, spec))


# ---------------------------------------------------------------------------------------------------------------------------------
# "En bref" block (2026-10-25): the questions players type about a spec, answered with the guide's own figures, at the top of the page.
# The text of each answer is also the text of the FAQPage data (same wording on screen and in the data). Nothing here is invented: every
# number comes from the level-60 ranking, the pre-raid simulator run, the guide's build or the race simulation, and a spec the simulator
# does not rank (healers) says so instead of showing a figure.
# ---------------------------------------------------------------------------------------------------------------------------------
QA = {
    "fr": {
        "h2": "En bref : {cls} {spec}",
        "q_good": "{cls} {spec} est-il une bonne spécialisation dans WoW Forever ?",
        "a_good_dps": "Dans notre simulation de niveau 60 ({fight} secondes sur un boss immobile, buffs de raid, meilleur équipement connu), {cls} {spec} est n°{pos} sur {n} spécialisations DPS avec {val} DPS. Le n°1 est {leader} ({lval} DPS). Un boss immobile ne dit pas tout : l'utilité en groupe et le jeu en déplacement comptent aussi.",
        "a_good_tank": "Dans notre simulation de niveau 60, {cls} {spec} est n°{pos} sur {n} tanks avec {val} TPS (menace par seconde). Le n°1 est {leader} ({lval} TPS). La menace n'est qu'une partie du travail d'un tank : la survie et l'utilité comptent aussi.",
        "a_good_none": "Le simulateur ne classe pas encore les soigneurs : nous n'affichons donc aucun chiffre pour {cls} {spec}. Le guide donne le build de talents, la rotation tirée des chiffres du client et les priorités de stats.",
        "q_talents": "Quels talents prendre pour {cls} {spec} ?",
        "a_talents": "Le build de notre simulateur utilise {total} points, répartis {split}.", "a_talents_top": " Les talents qui pèsent le plus dans la simulation : {top}.",
        "a_talents_none": "Le guide affiche l'arbre complet avec les talents conseillés.", "l_talents": "Ouvrir ce build dans le calculateur de talents",
        "q_gear": "Quel équipement pour {cls} {spec} ?",
        "a_gear": "Sans objet de raid, le meilleur ensemble que le simulateur trouve donne {value} {unit}{delta}.", "a_gear_delta": ", soit {delta} % par rapport à l'ensemble qui inclut les objets de raid",
        "a_gear_none": "Pas de liste d'équipement simulée pour les soigneurs : le simulateur ne modélise pas encore les soins sur un combat complet.",
        "a_stats": " Priorité de stats : {stats}.", "l_gear": "Équipement complet et enchantements",
        "q_rot": "Quelle rotation jouer avec {cls} {spec} ?", "a_rot": "Ouverture : {steps}.",
        "a_rot_none": "Le guide détaille l'ordre des sorts d'après les chiffres du client.", "l_rot": "Rotation complète",
        "q_race": "Quelle race choisir pour {cls} {spec} ?", "a_race_one": "La race en tête dans notre simulation : {races}.",
        "a_race_many": "Les races en tête dans notre simulation : {races} (à égalité statistique).", "l_race": "Toutes les races de la classe",
        "q_dung": "Où trouver l'équipement de {cls} {spec} avant le niveau 60 ?",
        "a_dung": "Notre sélecteur de donjons indique, pour chaque donjon, le meilleur objet de cette spécialisation d'après les poids de stats du simulateur.", "l_dung": "Meilleurs objets de donjon",
        "and": " et ",
    },
    "en": {
        "h2": "Quick answers: {spec} {cls}",
        "q_good": "Is {spec} {cls} a good spec in WoW Forever?",
        "a_good_dps": "In our level-60 simulation ({fight} seconds on a stationary boss, raid buffs, best known gear), {spec} {cls} ranks #{pos} of {n} DPS specs with {val} DPS. #1 is {leader} ({lval} DPS). A stationary boss does not tell everything: group utility and moving fights matter too.",
        "a_good_tank": "In our level-60 simulation, {spec} {cls} ranks #{pos} of {n} tanks with {val} TPS (threat per second). #1 is {leader} ({lval} TPS). Threat is only part of a tank's job: survival and utility matter too.",
        "a_good_none": "The simulator does not rank healers yet, so we show no figure for {spec} {cls}. The guide gives the talent build, the rotation read from the client's numbers and the stat priorities.",
        "q_talents": "Which talents should {spec} {cls} take?",
        "a_talents": "Our simulator's build uses {total} points, split {split}.", "a_talents_top": " The talents that weigh the most in the simulation: {top}.",
        "a_talents_none": "The guide shows the full tree with the recommended talents.", "l_talents": "Open this build in the talent calculator",
        "q_gear": "What gear should {spec} {cls} wear?",
        "a_gear": "Without raid items, the best set the simulator finds gives {value} {unit}{delta}.", "a_gear_delta": ", {delta}% against the set that includes raid items",
        "a_gear_none": "There is no simulated gear list for healers: the simulator does not model healing over a full fight yet.",
        "a_stats": " Stat priority: {stats}.", "l_gear": "Full gear and enchantments",
        "q_rot": "What rotation does {spec} {cls} play?", "a_rot": "Opening: {steps}.",
        "a_rot_none": "The guide details the spell order from the client's numbers.", "l_rot": "Full rotation",
        "q_race": "Which race should {spec} {cls} pick?", "a_race_one": "The top race in our simulation: {races}.",
        "a_race_many": "The top races in our simulation: {races} (statistically tied).", "l_race": "All races of the class",
        "q_dung": "Where can {spec} {cls} find gear before level 60?",
        "a_dung": "Our dungeon finder shows, for every dungeon, the best item for this spec according to the simulator's stat weights.", "l_dung": "Best dungeon items",
        "and": " and ",
    },
}


def _num(v, lang):
    return f"{int(round(v)):,}".replace(",", " " if lang == "fr" else ",")


def _join(items, lang):
    items = [i for i in items if i]
    if len(items) <= 1:
        return items[0] if items else ""
    return ", ".join(items[:-1]) + QA[lang]["and"] + items[-1]


def quick_answers(lang, cls, spec, rank, leader, n_ranked, fight, launch, stats, races, links):
    """[{q, a, link: {href, label} | None}]: the top-of-page block and the FAQPage data.
    rank = {pos, val, unit} | None; leader = {name, val} of the first spec of the same ranking list; launch = the guide's 'at launch' data or None;
    stats = stat names in priority order; races = names of the best races (statistically tied) or []; links = hrefs (no site root) for talents, gear, rot, race, dung."""
    t = QA[lang]
    f = dict(cls=cls, spec=spec)
    out = []
    if rank and leader:
        key = "a_good_tank" if rank["unit"] == "TPS" else "a_good_dps"
        a = t[key].format(pos=rank["pos"], n=n_ranked, val=_num(rank["val"], lang), leader=leader["name"], lval=_num(leader["val"], lang), fight=fight, **f)
    else:
        a = t["a_good_none"].format(**f)
    out.append({"q": t["q_good"].format(**f), "a": a, "link": None})
    if launch and launch.get("split") and launch.get("total"):
        a = t["a_talents"].format(total=launch["total"], split=launch["split_txt"])
        if launch.get("top"):
            a += t["a_talents_top"].format(top=", ".join(x[0] for x in launch["top"]))
    else:
        a = t["a_talents_none"]
    out.append({"q": t["q_talents"].format(**f), "a": a, "link": {"href": links["talents"], "label": t["l_talents"]} if links.get("talents") else None})
    blocks = (launch or {}).get("blocks") or []
    if blocks:
        b = blocks[0]
        delta = t["a_gear_delta"].format(delta=b["delta_txt"]) if b.get("delta_txt") else ""
        a = t["a_gear"].format(value=_num(b["value"], lang), unit=b["unit"], delta=delta)
    else:
        a = t["a_gear_none"]
    if stats:
        a += t["a_stats"].format(stats=" > ".join(stats[:3]))
    out.append({"q": t["q_gear"].format(**f), "a": a, "link": {"href": links["gear"], "label": t["l_gear"]} if links.get("gear") else None})
    rot = (launch or {}).get("rot") or []
    out.append({"q": t["q_rot"].format(**f), "a": t["a_rot"].format(steps=" ; ".join(s.strip().rstrip(".;") for s in rot)) if rot else t["a_rot_none"],
                "link": {"href": links["rot"], "label": t["l_rot"]} if links.get("rot") else None})
    if races:
        top3 = races[:3]
        out.append({"q": t["q_race"].format(**f), "a": t["a_race_one" if len(top3) == 1 else "a_race_many"].format(races=_join(top3, lang)),
                    "link": {"href": links["race"], "label": t["l_race"]} if links.get("race") else None})
    if links.get("dung"):
        out.append({"q": t["q_dung"].format(**f), "a": t["a_dung"], "link": {"href": links["dung"], "label": t["l_dung"]}})
    return out
