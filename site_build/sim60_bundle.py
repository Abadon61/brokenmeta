"""Bundles the ES modules of site_build/sim60 into one classic script (global `Sim60`) + a Web Worker
script, with content hashes in the file names (the site's service worker serves same-origin assets
cache-first, so every change must change the URL). Used by build_site.py."""
import hashlib
import re
import shutil
from pathlib import Path

SIM = Path(__file__).parent / "sim60"
ORDER = ["rng", "constants", "engine", "run", "presets", "character", "items", "talents", "warrior", "kits", "weights", "optimizer"]
EXPORTS = ("Sim, Aura, runBatchRaw, mergeRaw, finalize, runBatch, buildCharacter, ItemPool, toWeapon, EQUIP_SLOTS, "
           "BUFFS, CONSUMABLES, DEBUFFS, PRESET_RAID, RACIAL_SKILL, RACE_MODS, furyKit, armsKit, makeKit, KITS, "
           "statWeights, optimizeGear, optimizeGearAsync, validateRanks, parseShareHash, ranksToBuild, ranksFromNames, PRESETS, NAME_TO_KEY, FURY_DEFAULT_BUILD, ARMS_DEFAULT_BUILD, WARRIOR, warriorFromData, meleeTable, armorDR")


def _strip(src: str) -> str:
    src = re.sub(r"^import[\s\S]*?from\s+['\"][^'\"]+['\"];?[ \t]*\n", "", src, flags=re.M)
    src = re.sub(r"^export\s+(const|let|async function|function|class)\b", r"\1", src, flags=re.M)
    return src


def build(dist_dir: Path):
    parts = ["(function (root) {", "'use strict';"]
    for name in ORDER:
        parts.append(f"// ---- {name}.js ----")
        parts.append(_strip((SIM / f"{name}.js").read_text(encoding="utf-8")))
    parts.append(f"root.Sim60 = {{ {EXPORTS} }};")
    parts.append("})(typeof self !== 'undefined' ? self : this);")
    lib = "\n".join(parts) + "\n"
    h = hashlib.sha256(lib.encode("utf-8")).hexdigest()[:10]
    out = Path(dist_dir) / "assets" / "sim60"
    out.mkdir(parents=True, exist_ok=True)
    lib_name = f"sim60.{h}.js"
    (out / lib_name).write_text(lib, encoding="utf-8")
    worker = (
        f"importScripts('{lib_name}');\n"
        "let data = null;\n"
        "self.onmessage = (ev) => {\n"
        "  const m = ev.data, S = self.Sim60;\n"
        "  if (m.kind === 'init') { data = m.data; self.postMessage({ id: m.id, ok: true }); return; }\n"
        "  if (m.kind === 'run') {\n"
        "    const j = m.job;\n"
        "    const cfg = { fightLen: j.fightLen, player: j.player, target: j.target, kitFactory: () => S.makeKit(j.kitName, j.kitBuild, data) };\n"
        "    self.postMessage({ id: m.id, raw: S.runBatchRaw(cfg, m.iterations, m.seedBase) });\n"
        "  } else if (m.kind === 'weights') {\n"
        "    const j = m.job;\n"
        "    const cfg = { fightLen: j.fightLen, player: j.player, target: j.target, kitFactory: () => S.makeKit(j.kitName, j.kitBuild, data) };\n"
        "    self.postMessage({ id: m.id, result: S.statWeights(cfg, m.iterations, m.seedBase) });\n"
        "  } else if (m.kind === 'optimize') {\n"
        "    const j = m.job, pool = new S.ItemPool(m.items, m.proficiency);\n"
        "    const res = S.optimizeGear({ pool, character: m.character, kit: () => S.makeKit(j.kitName, j.kitBuild, data), fightLen: j.fightLen, iterations: m.iterations,\n"
        "      prefilter: m.prefilter, maxPasses: m.maxPasses, seed: m.seedBase, onProgress: (p) => self.postMessage({ id: m.id, progress: p }) });\n"
        "    self.postMessage({ id: m.id, result: res });\n"
        "  }\n"
        "};\n"
    )
    wh = hashlib.sha256(worker.encode("utf-8")).hexdigest()[:10]
    worker_name = f"worker.{wh}.js"
    (out / worker_name).write_text(worker, encoding="utf-8")
    for f in ("items.json", "proficiency.json", "spells60.json", "talents.json"):
        shutil.copy(SIM / "data" / f, out / f)
    data_v = hashlib.sha256(b"".join((SIM / "data" / f).read_bytes() for f in ("items.json", "proficiency.json", "spells60.json", "talents.json"))).hexdigest()[:10]
    return {"lib": lib_name, "worker": worker_name, "data_v": data_v}
