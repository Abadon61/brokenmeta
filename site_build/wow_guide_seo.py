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
