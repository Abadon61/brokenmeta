"""Threat per second of the tank presets WoWSims publishes (requests/page_*protection*.json, page_druid_feralbear.json), same CLI and settings as
run_requests.py. 2026-11-28: only Protection Warrior has published presets (Pre-BiS Offensive / Balanced); Protection Paladin and Bear Druid gear
is a dev-only placeholder on wowsims.com, so their exports carry no gear and are skipped (not simulated, not shown).
The tank ranking stays on our own simulator (user decision 2026-11-28); this figure is shown next to it on the Protection Warrior pages.
usage: py run_tanks.py -> data/wow_tanks_wowsims.json"""
import json, os, subprocess, tempfile, time
from pathlib import Path

HERE = Path(__file__).parent
PROJECT = HERE.parents[1]
CLONE = Path(os.environ.get("WOWSIMS_DIR", PROJECT.parent / "wowsims-forever"))
CLI = CLONE / "bin" / ("wowsimcli.exe" if os.name == "nt" else "wowsimcli")
SPEC = {"page_warrior_protection": "warrior_protection", "page_paladin_protection": "paladin_protection", "page_druid_feralbear": "druid_bear"}
ITER = 12500
rows = []
for page, spec in SPEC.items():
    f = HERE / "requests" / (page + ".json")
    if not f.exists():
        continue
    for label, req in json.loads(f.read_text(encoding="utf-8")).items():
        meta = req.pop("_bm", {})
        req.pop("requestId", None)
        p = req["raid"]["parties"][0]["players"][0]
        if not any(i.get("id") for i in p["equipment"]["items"]):
            print("skip (no gear in the published preset):", label)
            continue
        req["simOptions"] = {"iterations": ITER, "randomSeed": "101"}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as t:
            json.dump(req, t)
        res = json.loads(subprocess.run([str(CLI), "sim", "--infile", t.name], capture_output=True, text=True, cwd=CLONE).stdout)
        os.unlink(t.name)
        m = res["raidMetrics"]["parties"][0]["players"][0]
        rows.append({"spec": spec, "label": label, "preset": meta.get("preset"), "race": p["race"], "talents": p.get("talentsString", ""),
                     "tps": round(m["threat"]["avg"], 1), "tps_sem": round(m["threat"]["stdev"] / ITER ** 0.5, 1), "dps": round(m["dps"]["avg"], 1), "dtps": round(m["dtps"]["avg"], 1)})
        print(rows[-1])
commit = subprocess.run(["git", "log", "-1", "--format=%h %cs"], cwd=CLONE, capture_output=True, text=True).stdout.strip()
(PROJECT / "data" / "wow_tanks_wowsims.json").write_text(json.dumps({"engine_commit": commit, "generated": time.strftime("%Y-%m-%d %H:%M"), "iterations": ITER, "rows": rows}, indent=1), encoding="utf-8")
