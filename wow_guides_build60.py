"""Merges the level-60 talent builds (data/wow_guides/builds60.json, written by `node site_build/sim60/guide_builds.mjs`) into the specialization
guides' data (data/wow_guides/content.json). Run again after any change to a preset or a healer build:

    cd site_build/sim60 && node guide_builds.mjs && cd ../.. && py -3.11 wow_guides_build60.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "data" / "wow_guides" / "content.json"
BUILDS = ROOT / "data" / "wow_guides" / "builds60.json"

NOTE_SIM = {"fr": "Build de notre simulateur niveau 60 (51 points), celui utilisé pour le classement : talents choisis, équipement et rotation sur la page du classement.",
            "en": "Our level-60 simulator build (51 points), the one used for the ranking: talents, gear and rotation are on the ranking page."}
NOTE_HEAL = {"fr": "Build de soin niveau 60 (51 points) composé par BrokenMeta à partir des descriptions des talents : le simulateur ne gère pas encore les soins, ce build n'est donc pas chiffré.",
             "en": "Level-60 healing build (51 points) put together by BrokenMeta from the talent descriptions: the simulator does not model healing yet, so this build is not simulated."}


def main():
    raw = CONTENT.read_text(encoding="utf-8")
    content = json.loads(raw)
    builds = json.loads(BUILDS.read_text(encoding="utf-8"))
    n = 0
    for cls, specs in builds["builds"].items():
        for spec, b in specs.items():
            order = {t["id"]: (0 if t["tree"] == spec else 1, t["tree"], t["row"]) for t in b["talents"]}       # the guide's own tree first
            talents = [{"id": t["id"], "points": t["points"],
                        "why": {"fr": f"Rang {t['points']}/{t['max']} : {t['desc']['fr']}", "en": f"Rank {t['points']}/{t['max']}: {t['desc']['en']}"}} for t in b["talents"]]
            talents.sort(key=lambda t: order[t["id"]])
            content[cls][spec]["build"] = {"level": 60, "source": "sim60" if b["simulated"] else "theorycraft", "note": NOTE_SIM if b["simulated"] else NOTE_HEAL, "talents": talents}
            n += 1
    CONTENT.write_text(json.dumps(content, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("merged", n, "builds")


if __name__ == "__main__":
    main()
