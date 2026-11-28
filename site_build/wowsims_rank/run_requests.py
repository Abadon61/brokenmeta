"""Simulates every preset exported from wowsims.com/forever ('Export > CLI', saved by browser_export.js + sink.py into
requests/page_*.json) with the WoWSims Forever engine (github.com/wowsims/forever, MIT) and writes data/wow_ranking_wowsims.json.

The request is the site's own one (gear, talents, rotation, consumables, buffs, 180 s fight against one boss); only the
number of iterations and the seed are set here, so a rerun gives the same numbers.
usage: py run_requests.py [--iterations 12500]"""
import argparse, json, os, subprocess, tempfile, time
from pathlib import Path

HERE = Path(__file__).parent
PROJECT = HERE.parents[1]
CLONE = Path(os.environ.get("WOWSIMS_DIR", PROJECT.parent / "wowsims-forever"))
CLI = CLONE / "bin" / ("wowsimcli.exe" if os.name == "nt" else "wowsimcli")

ap = argparse.ArgumentParser()
ap.add_argument("--iterations", type=int, default=12500)
ap.add_argument("--out", default=str(PROJECT / "data" / "wow_ranking_wowsims.json"))
a = ap.parse_args()

rows = []
t0 = time.time()
for page in sorted((HERE / "requests").glob("page_*.json")):
    for label, req in json.loads(page.read_text(encoding="utf-8")).items():
        meta = req.pop("_bm", {})
        req.pop("requestId", None)
        req["simOptions"] = {"iterations": a.iterations, "randomSeed": "101"}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(req, f)
        r = subprocess.run([str(CLI), "sim", "--infile", f.name], capture_output=True, text=True, cwd=CLONE)
        os.unlink(f.name)
        p = req["raid"]["parties"][0]["players"][0]
        row = {"label": label, "preset": meta.get("preset"), "class": p["class"], "race": p["race"],
               "talents": p.get("talentsString", ""), "duration": req["encounter"].get("duration"),
               "duration_variation": req["encounter"].get("durationVariation", 0), "iterations": a.iterations}
        try:
            res = json.loads(r.stdout)
            row["dps"] = round(res["raidMetrics"]["dps"]["avg"], 1)
            row["stdev"] = round(res["raidMetrics"]["dps"]["stdev"], 1)
        except Exception:
            row["error"] = (r.stderr or r.stdout)[-400:]
        rows.append(row)
        print(f'{label:26} {row.get("dps", 0):8.1f} +-{row.get("stdev", 0):6.1f}  {p["race"]:26} {row.get("error", "")[:80]}', flush=True)

commit = subprocess.run(["git", "log", "-1", "--format=%h %cs"], cwd=CLONE, capture_output=True, text=True).stdout.strip()
out = {"engine": "WoWSims Forever (github.com/wowsims/forever, MIT license)", "engine_commit": commit,
       "source": "presets of wowsims.com/forever, Export > CLI", "generated": time.strftime("%Y-%m-%d %H:%M"),
       "iterations": a.iterations, "rows": sorted(rows, key=lambda x: -(x.get("dps") or 0))}
Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"{len(rows)} presets in {time.time() - t0:.0f}s -> {a.out}")
