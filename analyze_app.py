"""CoreMeta — Analyse de partie. Standalone local Flask app (see
src/tft_tracker/analysis.py for why this isn't part of the static Outrun
artifact: it needs a live Riot API call triggered by user input, which a
published Artifact's CSP cannot do).

Run: py analyze_app.py, then open http://127.0.0.1:5055
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "src")

from flask import Flask, jsonify, render_template, request

from tft_tracker import config
from tft_tracker.analysis import build_report, load_benchmarks, load_matchups
from tft_tracker.champion_images import build_champion_image_map, build_item_image_map, classify_item_offense
from tft_tracker.riot_client import RiotAPIError, RiotClient

app = Flask(__name__)
client = RiotClient()

_tierlist = json.loads(Path("data/output/tierlist.json").read_text(encoding="utf-8"))
SET_NAME = _tierlist["set"]
benchmarks = load_benchmarks()
matchup_lookup = load_matchups()

_raw_champ_map = build_champion_image_map(SET_NAME)
name_map = {cid: info["name"] for cid, info in _raw_champ_map.items()}
champ_icon_by_name = {info["name"]: info["icon"] for info in _raw_champ_map.values()}
item_offense = classify_item_offense(SET_NAME)

_needed_items = set()
for _c in benchmarks.values():
    for _u in _c.get("core_units", []):
        _needed_items.update(_u.get("items", []))
item_icon_map = build_item_image_map(_needed_items)


@app.route("/")
def index():
    return render_template("analyze.html", regions=list(config.REGIONS.keys()))


@app.route("/api/matches", methods=["POST"])
def api_matches():
    data = request.get_json(silent=True) or {}
    riot_id = (data.get("riotId") or "").strip()
    region = (data.get("region") or "").upper()
    game_name, sep, tag_line = riot_id.partition("#")
    if region not in config.REGIONS or not sep or not game_name.strip() or not tag_line.strip():
        return jsonify({"error": "Riot ID invalide (format Pseudo#TAG) ou région inconnue."}), 400

    regional = config.REGIONS[region]["regional"]
    try:
        account = client.get_account_by_riot_id(regional, game_name.strip(), tag_line.strip())
    except RiotAPIError as e:
        if e.status == 404:
            return jsonify({"error": "Joueur introuvable avec ce Riot ID sur cette région."}), 404
        return jsonify({"error": f"Erreur API Riot ({e.status})."}), 502
    if not account:
        return jsonify({"error": "Joueur introuvable avec ce Riot ID sur cette région."}), 404

    puuid = account["puuid"]
    match_ids = client.get_match_ids_by_puuid(regional, puuid, count=10)
    matches = []
    for mid in match_ids:
        m = client.get_match(regional, mid)
        if not m:
            continue
        info = m.get("info", {})
        if info.get("queueId") != config.RANKED_TFT_QUEUE_ID:
            continue
        participant = next((p for p in info.get("participants", []) if p.get("puuid") == puuid), None)
        if not participant or not participant.get("placement"):
            continue
        matches.append({
            "matchId": mid,
            "placement": participant["placement"],
            "level": participant.get("level"),
        })
    return jsonify({
        "puuid": puuid,
        "region": region,
        "riotId": f"{account.get('gameName', game_name)}#{account.get('tagLine', tag_line)}",
        "matches": matches,
    })


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(silent=True) or {}
    region = (data.get("region") or "").upper()
    match_id = data.get("matchId")
    puuid = data.get("puuid")
    if region not in config.REGIONS or not match_id or not puuid:
        return jsonify({"error": "Requête invalide."}), 400

    regional = config.REGIONS[region]["regional"]
    match = client.get_match(regional, match_id)
    if not match:
        return jsonify({"error": "Partie introuvable."}), 404
    participant = next((p for p in match.get("info", {}).get("participants", []) if p.get("puuid") == puuid), None)
    if not participant:
        return jsonify({"error": "Joueur non trouvé dans cette partie."}), 404

    report = build_report(participant, name_map, benchmarks, match=match, puuid=puuid,
                           matchup_lookup=matchup_lookup, item_offense=item_offense)
    report["carryIcon"] = champ_icon_by_name.get(report["carry"], "")
    for u in report["units"]:
        u["icon"] = champ_icon_by_name.get(u["champion"], "")
        u["itemIcons"] = [item_icon_map.get(i, "") for i in u["items"]]
    for l in report["lobby"]:
        l["carryIcon"] = champ_icon_by_name.get(l["carry"], "")
    return jsonify(report)


if __name__ == "__main__":
    print(f"Set détecté : {SET_NAME} · {len(benchmarks)} comps avec benchmarks")
    app.run(debug=True, port=5055)
