#!/usr/bin/env python
"""Build the WoW: Forever talent data files from the game's own tables (published per build by wago.tools).

    py -3.11 wow_talents_import.py                    # latest Forever beta build -> data/wow_talents_staging/  (NOT published)
    py -3.11 wow_talents_import.py --build 1.60.1.69913 [--refresh]
    py -3.11 wow_talents_import.py --publish          # staging -> data/wow_talents/ (what the site builds from), only if clean

What it reads (all from the client tables, nothing typed by hand): the class trees (TraitTree/TraitNode/TraitNodeEntry),
positions (row/column), max ranks, the unlock gates (TraitCond via node groups), prerequisites (TraitEdge), the point cap and
level schedule (TraitCurrency/TraitCurrencySource), spec names (TalentTab), spell names and tooltip texts in enUS and frFR, and
the per-rank values (TraitDefinitionEffectPoints curves). Tooltip variables ($s1, $d, ...) are computed from the spell tables.

Anything it cannot resolve is REPORTED, never guessed: a talent text that still contains an unresolved variable is flagged and
`--publish` refuses to go on. Raw tables are cached in data/wow_talents_raw/<build>/ (git-ignored) so a build is downloaded once;
downloads are sequential with a pause. Data is Blizzard's: whether the site may show it is the site owner's decision.
"""
from __future__ import annotations

import argparse
import ast
import collections
import csv
import datetime as dt
import json
import operator
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "wow_talents_raw"
STAGING_DIR = ROOT / "data" / "wow_talents_staging"
FINAL_DIR = ROOT / "data" / "wow_talents"
UA = "brokenmeta.gg talent importer (independent fan site)"
PAUSE = 1.5
LOCALES = {"en": None, "fr": "frFR"}
ROWS, COLS = 7, 4

# tables read once (language independent) and tables read per language
PLAIN = ["TraitTree", "TraitNode", "TraitNodeEntry", "TraitNodeXTraitNodeEntry", "TraitDefinition", "TraitDefinitionEffectPoints",
         "TraitEdge", "TraitNodeGroupXTraitNode", "TraitNodeGroupXTraitCond", "TraitCond", "TraitCurrency", "TraitCurrencySource",
         "TraitTreeXTraitCurrency", "SpellEffect", "SpellMisc", "SpellDuration", "SpellAuraOptions", "SpellRadius", "Curve", "CurvePoint"]
LOCALIZED = ["ChrClasses", "TalentTab", "SpellName", "Spell"]


# ------------------------------------------------------------------------------------------------------- download
def http(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def latest_beta_build() -> str:
    status, body = http("https://wago.tools/api/builds")
    if status != 200:
        sys.exit(f"cannot list builds (HTTP {status})")
    builds = json.loads(body).get("wow_classic_beta") or []
    if not builds:
        sys.exit("no wow_classic_beta builds listed")
    return sorted(builds, key=lambda b: b["created_at"], reverse=True)[0]["version"]


def fetch(table: str, build: str, locale: str | None, refresh: bool) -> Path:
    path = RAW_DIR / build / f"{table}{'.' + locale if locale else ''}.csv"
    if path.exists() and not refresh:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://wago.tools/db2/{table}/csv?build={build}" + (f"&locale={locale}" if locale else "")
    status, body = http(url)
    if status != 200 or body.lstrip().startswith(b'{"errors"'):
        sys.exit(f"table {table} not available for build {build} (HTTP {status}): {body[:80]!r}")
    path.write_bytes(body)
    print(f"  downloaded {table}{' ' + locale if locale else ''}: {len(body) / 1024:.0f} KB")
    time.sleep(PAUSE)
    return path


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class Tables:
    def __init__(self, build: str, refresh: bool):
        self.build = build
        for t in PLAIN:
            setattr(self, t, read(fetch(t, build, None, refresh)))
        self.loc = {lang: {t: read(fetch(t, build, code, refresh)) for t in LOCALIZED} for lang, code in LOCALES.items()}


# ------------------------------------------------------------------------------------------------------- tooltips
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.USub: operator.neg, ast.UAdd: operator.pos}


def safe_eval(expr: str) -> float:
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.operand))
        raise ValueError(f"unsupported expression {expr!r}")
    return ev(ast.parse(expr.strip(), mode="eval"))


class Spells:
    """Everything a tooltip needs, indexed once."""

    def __init__(self, T: Tables):
        self.effects = collections.defaultdict(dict)                     # spell -> {effect index: row}
        for e in T.SpellEffect:
            if e.get("DifficultyID", "0") in ("0", ""):
                self.effects[e["SpellID"]].setdefault(int(e["EffectIndex"]), e)
        self.dur_ms = {r["ID"]: int(r["Duration"]) for r in T.SpellDuration}
        self.misc_dur = {}
        for r in T.SpellMisc:
            self.misc_dur.setdefault(r["SpellID"], r.get("DurationIndex", "0"))
        self.aura = {r["SpellID"]: r for r in T.SpellAuraOptions}
        self.radius = {r["ID"]: float(r["Radius"]) for r in T.SpellRadius}
        pts = collections.defaultdict(list)
        for c in T.CurvePoint:
            pts[c["CurveID"]].append((int(c["OrderIndex"]), float(c["Pos_0"]), float(c["Pos_1"])))
        self.curve = {k: [(x, y) for _, x, y in sorted(v)] for k, v in pts.items()}

    def duration_ms(self, sid: str) -> int | None:
        d = self.dur_ms.get(self.misc_dur.get(sid, "0"), 0)
        return d if d and d > 0 else None

    def curve_at(self, curve_id: str, rank: int) -> float | None:
        pts = self.curve.get(curve_id)
        if not pts:
            return None
        for x, y in pts:
            if x == rank:
                return y
        lower = [p for p in pts if p[0] < rank]
        return lower[-1][1] if lower else pts[0][1]


DECIMAL = {"en": ".", "fr": ","}


def fmt_num(v: float, decimals: int | None = None, lang: str = "en") -> str:
    if decimals is not None:
        s = f"{v:.{decimals}f}"
    elif abs(v - round(v)) < 1e-6:
        s = str(int(round(v)))
    else:
        s = f"{v:.1f}".rstrip("0").rstrip(".")
    return s.replace(".", DECIMAL[lang])


UNITS = {"en": ("sec", "min"), "fr": ("s", "min")}
SIMPLE = re.compile(r"\$(\d{2,})?([sSmMoOtTaAxXuUdDhH])(\d)?")
SCALED = re.compile(r"\$([/*])(-?\d+);(\d{2,})?([sSmMoOtTaAxXuUdDhH])(\d)?")       # $/1000;S1 = effect 1 divided by 1000
CHARGES = re.compile(r"\$(\d{2,})?n(?![A-Za-z])")                                   # $n / $12345n = proc charges
PROC_CD = re.compile(r"\$proccooldown")


class Renderer:
    def __init__(self, sp: Spells, names: dict[str, str], lang: str):
        self.sp, self.names, self.lang = sp, names, lang
        self.problems: list[str] = []

    def _value(self, letter: str, sid: str, idx: int, overrides: dict, decimals=None, numeric=False):
        """Returns a float, or None when it cannot be computed."""
        L = letter.lower()
        if L in "sm":
            base = overrides.get((sid, idx - 1))
            if base is None:
                e = self.sp.effects.get(sid, {}).get(idx - 1)
                if not e:
                    return None
                base = float(e["EffectBasePointsF"])
            return abs(base)
        e = self.sp.effects.get(sid, {}).get(idx - 1)
        if L == "o":
            dur = self.sp.duration_ms(sid)
            per = int(e["EffectAuraPeriod"]) if e else 0
            base = self._value("s", sid, idx, overrides)
            return None if not (dur and per and base is not None) else base * (dur / per)
        if L == "t":
            return None if not e or not int(e["EffectAuraPeriod"]) else int(e["EffectAuraPeriod"]) / 1000
        if L == "x":
            return None if not e else float(e["EffectChainTargets"] or 0)
        if L == "a":
            return None if not e else self.sp.radius.get(e["EffectRadiusIndex_0"])
        if L == "u":
            a = self.sp.aura.get(sid)
            return None if not a else float(a.get("CumulativeAura", 0)) or None
        if L == "h":
            a = self.sp.aura.get(sid)
            return None if not a else float(a.get("ProcChance", 0)) or None
        if L == "n":
            a = self.sp.aura.get(sid)
            return None if not a else float(a.get("ProcCharges", 0)) or None
        if L == "c":                                                        # proc cooldown (ms -> s)
            a = self.sp.aura.get(sid)
            return None if not a else (float(a.get("ProcCategoryRecovery", 0)) / 1000) or None
        if L == "d":
            d = self.sp.duration_ms(sid)
            return None if d is None else d / 1000
        return None

    def render(self, template: str, sid: str, overrides: dict) -> tuple[str, bool]:
        text = template.replace("\r\n", " ").replace("\n", " ")
        text = re.sub(r"\|[cC][0-9a-fA-F]{8}|\|[rR]", "", text)
        ok = True
        out, i, last_num = [], 0, None

        def num_token(m: re.Match) -> str | None:
            nonlocal last_num
            other, letter, idx = m.group(1), m.group(2), m.group(3)
            ssid = other or sid
            if letter in "dD":
                v = self._value("d", ssid, 1, overrides)
                if v is None:
                    return None
                unit_s, unit_m = UNITS[self.lang]
                last_num = v
                return f"{fmt_num(v / 60, None, self.lang)} {unit_m}" if v >= 60 and abs(v % 60) < 1e-6 else f"{fmt_num(v, None, self.lang)} {unit_s}"
            v = self._value(letter, ssid, int(idx or 1), overrides)
            if v is None:
                return None
            last_num = v
            return fmt_num(v, None, self.lang)

        while i < len(text):
            ch = text[i]
            if ch != "$":
                out.append(ch)
                i += 1
                continue
            sm = SCALED.match(text, i)
            if sm:
                op, factor, other, letter, idx = sm.groups()
                v = self._value(letter, other or sid, int(idx or 1), overrides)
                if v is None:
                    ok = False
                    self.problems.append(sm.group(0))
                    out.append("…")
                else:
                    v = v / float(factor) if op == "/" else v * float(factor)
                    last_num = v
                    out.append(fmt_num(v, None, self.lang))
                i = sm.end()
                continue
            cm = CHARGES.match(text, i) or PROC_CD.match(text, i)
            if cm:
                v = self._value("n" if cm.re is CHARGES else "c", (cm.group(1) if cm.re is CHARGES and cm.group(1) else sid), 1, overrides)
                if v is None:
                    ok = False
                    self.problems.append(cm.group(0))
                    out.append("…")
                else:
                    last_num = v
                    out.append(fmt_num(v, None, self.lang))
                i = cm.end()
                continue
            m = SIMPLE.match(text, i)
            if m:
                r = num_token(m)
                if r is None:
                    ok = False
                    self.problems.append(m.group(0))
                    out.append("…")
                else:
                    out.append(r)
                i = m.end()
                continue
            if text.startswith("${", i):                                   # ${expression}.decimals
                depth, j = 0, i + 1
                while j < len(text):
                    depth += text[j] == "{"
                    depth -= text[j] == "}"
                    if depth == 0:
                        break
                    j += 1
                expr = text[i + 2:j]
                dm = re.match(r"\.(\d)", text[j + 1:])
                decimals = int(dm.group(1)) if dm else None
                try:
                    def sub(mm):
                        v = self._value(mm.group(2), mm.group(1) or sid, int(mm.group(3) or 1), overrides)
                        if v is None:
                            raise ValueError
                        return repr(v)
                    value = safe_eval(SIMPLE.sub(sub, expr))
                    last_num = value
                    out.append(fmt_num(value, decimals, self.lang))
                except Exception:      # noqa: BLE001
                    ok = False
                    self.problems.append(text[i:j + 1])
                    out.append("…")
                i = j + 1 + (len(dm.group(0)) if dm else 0)
                continue
            pm = re.match(r"\$[lL]([^:;]*):([^;]*);", text[i:])           # $lsingular:plural;
            if pm:
                singular, plural = pm.group(1), pm.group(2)
                out.append(singular if last_num is not None and abs(last_num) <= 1 else plural)
                i += pm.end()
                continue
            nm = re.match(r"\$@spellname(\d+)", text[i:])
            if nm and nm.group(1) in self.names:
                out.append(self.names[nm.group(1)])
                i += nm.end()
                continue
            if text.startswith("$?", i):                                      # $?condition[branch A][branch B]
                head = re.match(r"\$\?[^\[]*", text[i:]).group(0)
                pos, branches = i + len(head), []
                while pos < len(text) and text[pos] == "[" and len(branches) < 2:
                    depth, end = 0, pos
                    while end < len(text):
                        depth += text[end] == "["
                        depth -= text[end] == "]"
                        if depth == 0:
                            break
                        end += 1
                    branches.append(text[pos + 1:end])
                    pos = end + 1
                if len(branches) == 2 and branches[0].strip() == branches[1].strip() and "$" not in branches[0]:
                    out.append(branches[0].strip())          # both outcomes read the same: the condition does not matter
                else:
                    ok = False
                    self.problems.append(head)
                    out.append("…")
                i = pos
                continue
            tok = re.match(r"\$[^\s.,;:)\]]{1,14}", text[i:])
            ok = False
            self.problems.append(tok.group(0) if tok else "$")
            out.append("…")
            i += len(tok.group(0)) if tok else 1
        return re.sub(r"\s{2,}", " ", "".join(out)).strip(), ok


# ------------------------------------------------------------------------------------------------------- structure
def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def build(T: Tables, out_dir: Path) -> dict:
    rep: dict = {"build": T.build, "warnings": [], "classes": {}, "unresolved": collections.Counter(), "texts": 0, "texts_ok": 0}
    warn = rep["warnings"].append
    sp = Spells(T)
    nodes = {n["ID"]: n for n in T.TraitNode}
    entries = {e["ID"]: e for e in T.TraitNodeEntry}
    defs = {d["ID"]: d for d in T.TraitDefinition}
    node_entries = collections.defaultdict(list)
    for r in T.TraitNodeXTraitNodeEntry:
        node_entries[r["TraitNodeID"]].append(r["TraitNodeEntryID"])
    eff_points = collections.defaultdict(dict)                              # TraitDefinition -> {effect index: curve id}
    for r in T.TraitDefinitionEffectPoints:
        eff_points[r["TraitDefinitionID"]][int(r["EffectIndex"])] = r["CurveID"]

    # --- points cap and level schedule, read from the data
    trees_currency = {r["TraitTreeID"]: r["TraitCurrencyID"] for r in T.TraitTreeXTraitCurrency}
    cur_max = {c["ID"]: int(c["SourcedMax"]) for c in T.TraitCurrency}
    src_by_cur = collections.defaultdict(list)
    for s in T.TraitCurrencySource:
        if s["TraitNodeEntryID"] == "0" and s["QuestID"] == "0" and s["AchievementID"] == "0" and s["PlayerLevel"] != "0":
            src_by_cur[s["TraitCurrencyID"]].append((int(s["PlayerLevel"]), int(s["Amount"])))

    # --- classes (spell class set -> class), spec tab names
    fam_to_class = {}
    for c in T.loc["en"]["ChrClasses"]:
        fam_to_class[c["SpellClassSet"]] = c
    class_names = {lang: {c["ID"]: c["Name_lang"] for c in T.loc[lang]["ChrClasses"]} for lang in LOCALES}
    spell_class_set = {}
    # class of a spell comes from SpellClassOptions in the client; we only need it to attach trees to classes
    from_sco = ROOT / "data" / "wow_talents_raw" / T.build / "SpellClassOptions.csv"
    if not from_sco.exists():
        fetch("SpellClassOptions", T.build, None, False)
    for r in read(from_sco):
        spell_class_set[r["SpellID"]] = r["SpellClassSet"]
    spell_names = {lang: {r["ID"]: r["Name_lang"] for r in T.loc[lang]["SpellName"]} for lang in LOCALES}
    spell_desc = {lang: {r["ID"]: r["Description_lang"] for r in T.loc[lang]["Spell"]} for lang in LOCALES}

    by_tree = collections.defaultdict(list)
    for n in T.TraitNode:
        by_tree[n["TraitTreeID"]].append(n)

    def clusters(xs):
        xs = sorted(xs)
        cl = [[xs[0]]]
        for v in xs[1:]:
            (cl[-1].append(v) if v - cl[-1][-1] < 1000 else cl.append([v]))
        # a spec cluster holds a real number of talents; lone nodes parked far away are stray (reported later)
        return [sorted(set(c)) for c in cl if len(c) >= 5]

    # a class tree = 3 spec clusters and a real number of talents
    class_trees = {}
    ignored = []
    for tid, ns in by_tree.items():
        cl = clusters([int(n["PosX"]) for n in ns])
        if len(cl) == 3 and len(ns) >= 45:
            fams = collections.Counter()
            for n in ns:
                for eid in node_entries[n["ID"]]:
                    fams[spell_class_set.get(defs[entries[eid]["TraitDefinitionID"]]["SpellID"], "?")] += 1
            fam, cnt = fams.most_common(1)[0]
            klass = fam_to_class.get(fam)
            if not klass or cnt < 0.6 * len(ns):
                warn(f"tree {tid}: class not identifiable ({fams.most_common(3)})")
                continue
            if klass["ID"] in class_trees:
                warn(f"class {klass['Name_lang']} has two full trees ({class_trees[klass['ID']]} and {tid})")
                continue
            class_trees[klass["ID"]] = tid
        else:
            ignored.append((tid, len(ns), len(cl)))
    rep["ignored_trees"] = ignored
    anchors_x = collections.Counter()
    anchors_y = collections.Counter()
    for tid in class_trees.values():
        for k, c in enumerate(clusters([int(n["PosX"]) for n in by_tree[tid]])):
            anchors_x[(k, c[0])] += 1
        anchors_y[min(int(n["PosY"]) for n in by_tree[tid])] += 1
    base_x = {k: max((v, x) for (kk, x), v in anchors_x.items() if kk == k)[1] for k in range(3)}
    base_y = anchors_y.most_common(1)[0][0]

    # --- gates: node -> group -> condition (counts points spent in another group)
    group_nodes = collections.defaultdict(set)
    node_groups = collections.defaultdict(set)
    for r in T.TraitNodeGroupXTraitNode:
        group_nodes[r["TraitNodeGroupID"]].add(r["TraitNodeID"])
        node_groups[r["TraitNodeID"]].add(r["TraitNodeGroupID"])
    conds = {c["ID"]: c for c in T.TraitCond}
    group_conds = collections.defaultdict(list)
    for r in T.TraitNodeGroupXTraitCond:
        if r["TraitCondID"] in conds:
            group_conds[r["TraitNodeGroupID"]].append(conds[r["TraitCondID"]])

    edges_in = collections.defaultdict(list)
    for e in T.TraitEdge:
        edges_in[e["RightTraitNodeID"]].append(e)

    # --- points/level rule check (one currency for all class trees)
    cur_ids = {trees_currency.get(t) for t in class_trees.values()}
    rules = {"total_points": None, "first_level": None}
    if len(cur_ids) == 1:
        cid = cur_ids.pop()
        srcs = src_by_cur.get(cid, [])
        rules["total_points"] = cur_max.get(cid)
        rules["first_level"] = min(l for l, a in srcs) if srcs else None
        got = sum(a for _, a in srcs)
        rep["rules_from_data"] = {"currency": cid, "max": cur_max.get(cid), "first_level": rules["first_level"], "sum_of_sources": got,
                                  "levels": [min(l for l, _ in srcs), max(l for l, _ in srcs)] if srcs else None}
    else:
        warn(f"class trees use several currencies: {cur_ids}")

    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        for old in out_dir.glob("*.json"):
            old.unlink()

    renderers = {lang: Renderer(sp, spell_names[lang], lang) for lang in LOCALES}
    assumptions = ["A prerequisite arrow requires the source talent at its MAXIMUM rank (Classic behaviour); the client tables only store the link."]
    for cid, tid in sorted(class_trees.items(), key=lambda kv: int(kv[0])):
        cls_row = next(c for c in T.loc["en"]["ChrClasses"] if c["ID"] == cid)
        cslug = cls_row["Filename"].lower()
        mask = 1 << (int(cid) - 1)
        tabs = {lang: sorted((t for t in T.loc[lang]["TalentTab"] if int(t["ClassMask"]) == mask), key=lambda t: int(t["OrderIndex"])) for lang in LOCALES}
        cl = clusters([int(n["PosX"]) for n in by_tree[tid]])
        if len(tabs["en"]) != 3:
            warn(f"{cslug}: {len(tabs['en'])} talent tabs (expected 3)")
            continue
        node_pos = {}
        for n in by_tree[tid]:
            k = next((i for i, c in enumerate(cl) if int(n["PosX"]) in c), None)
            row = round((int(n["PosY"]) - base_y) / 600) + 1
            col = None if k is None else round((int(n["PosX"]) - base_x[k]) / 600) + 1
            if k is None or not (1 <= row <= ROWS and 1 <= col <= COLS):
                eid = node_entries[n["ID"]][0] if node_entries[n["ID"]] else None
                sid_ = defs[entries[eid]["TraitDefinitionID"]]["SpellID"] if eid else "?"
                rep.setdefault("offgrid", []).append(f"{cslug}: '{spell_names['en'].get(sid_, sid_)}' (node {n['ID']}, x {n['PosX']}, y {n['PosY']}) -- placed outside the 7x4 grid, excluded")
                continue
            node_pos[n["ID"]] = (k, row, col)
        max_rank = {}
        for nid in node_pos:
            eids = node_entries[nid]
            if len(eids) != 1:
                warn(f"{cslug}: node {nid} has {len(eids)} entries (choice node?) -- skipped")
                continue
            max_rank[nid] = int(entries[eids[0]]["MaxRanks"])

        specs_out = []
        for k in range(3):
            talents = []
            for nid, (kk, row, col) in sorted(node_pos.items(), key=lambda kv: (kv[1][1], kv[1][2])):
                if kk != k or nid not in max_rank:
                    continue
                d = defs[entries[node_entries[nid][0]]["TraitDefinitionID"]]
                sid = d["SpellID"]
                mr = max_rank[nid]
                overrides_by_rank = []
                for r in range(1, mr + 1):
                    ov = {}
                    for eidx, curve in eff_points[d["ID"]].items():
                        v = sp.curve_at(curve, r)
                        if v is not None:
                            ov[(sid, eidx)] = v
                    overrides_by_rank.append(ov)
                name, desc = {}, {}
                for lang in LOCALES:
                    name[lang] = d["OverrideName_lang"] if lang == "en" and d["OverrideName_lang"] else spell_names[lang].get(sid, "")
                    texts = []
                    for r in range(mr):
                        text, ok = renderers[lang].render(spell_desc[lang].get(sid, ""), sid, overrides_by_rank[r])
                        rep["texts"] += 1
                        rep["texts_ok"] += bool(ok and text)
                        texts.append(text or name[lang])
                        if not (ok and text):
                            rep["unresolved"][f"{cslug}/{name['en']}"] += 1
                    desc[lang] = texts
                item = {"id": f"n{nid}", "name": name, "row": row, "col": col, "max_rank": mr, "desc": desc}
                if any("…" in x for lang in LOCALES for x in desc[lang]):
                    item["incomplete"] = True
                # gates
                gates = set()
                for g in node_groups.get(nid, ()):
                    for c in group_conds.get(g, ()):
                        counted = group_nodes.get(c["TraitNodeGroupID"], set())
                        rows_counted = [node_pos[x][1] for x in counted if x in node_pos and node_pos[x][0] == k]
                        need = int(c["SpentAmountRequired"])
                        if rows_counted and need > 0:
                            gates.add((max(rows_counted), need))
                if gates:
                    item["gates"] = [{"through_row": r_, "points": p_} for r_, p_ in sorted(gates)]
                talents.append((nid, item))
            specs_out.append(talents)

        # prerequisites (edges): type 3 = required, type 2 = sufficient (any one), type 0 = drawing only
        id_of = {nid: item["id"] for talents in specs_out for nid, item in talents}
        rank_of = {nid: item["max_rank"] for talents in specs_out for nid, item in talents}
        for talents in specs_out:
            for nid, item in talents:
                allr, anyr = [], []
                for e in edges_in.get(nid, ()):
                    left = e["LeftTraitNodeID"]
                    if left not in id_of or e["Type"] not in ("2", "3"):          # type 0 = drawing only
                        continue
                    if node_pos[left][1] > node_pos[nid][1]:
                        if any(x["LeftTraitNodeID"] == nid and x["Type"] in ("2", "3") for x in edges_in.get(left, ())):
                            continue                                              # the same link is also stored downwards
                        warn(f"{cslug}: prerequisite edge {left}->{nid} goes upwards (rows {node_pos[left][1]} -> {node_pos[nid][1]}), ignored")
                        continue
                    ref = {"id": id_of[left], "rank": rank_of[left]}
                    if e["Type"] == "3":
                        allr.append(ref)
                    elif e["Type"] == "2":
                        anyr.append(ref)
                if allr:
                    item["requires"] = allr
                if len(anyr) == 1 and not allr:
                    item["requires"] = anyr
                elif anyr:
                    item["requires_any"] = anyr

        specs_json = []
        for k, talents in enumerate(specs_out):
            specs_json.append({"id": slug(tabs["en"][k]["Name_lang"]), "name": {lang: tabs[lang][k]["Name_lang"] for lang in LOCALES},
                               "talents": [item for _, item in talents]})
        cls_json = {"id": cslug, "name": {lang: class_names[lang][cid] for lang in LOCALES}, "specs": specs_json,
                    "source": {"label": f"WoW: Forever beta client data, build {T.build} (tables via wago.tools)", "url": "https://wago.tools/"},
                    "meta": {"build": T.build, "generated": dt.date.today().isoformat(), "assumptions": assumptions}}
        if out_dir:
            (out_dir / f"{cslug}.json").write_text(json.dumps(cls_json, ensure_ascii=False, indent=1), encoding="utf-8")
        rep["classes"][cslug] = {"specs": [(s["name"]["en"], len(s["talents"])) for s in specs_json],
                                 "sample": [[t["name"]["en"] for t in s["talents"][:2]] for s in specs_json],
                                 "gates_default_mismatch": sum(1 for s in specs_json for t in s["talents"]
                                                               if t["row"] > 1 and t.get("gates") != [{"through_row": t["row"] - 1, "points": (t["row"] - 1) * 5}]),
                                 "no_gate_rows_above_1": sum(1 for s in specs_json for t in s["talents"] if t["row"] > 1 and not t.get("gates")),
                                 "prereq_talents": sum(1 for s in specs_json for t in s["talents"] if t.get("requires") or t.get("requires_any")),
                                 "any_of": sum(1 for s in specs_json for t in s["talents"] if t.get("requires_any"))}
    rep["problems_by_token"] = collections.Counter(p for r in renderers.values() for p in r.problems)
    rep["missing_classes"] = sorted({c["Filename"].lower() for c in T.loc["en"]["ChrClasses"]} - set(rep["classes"]))
    return rep


def report(rep: dict) -> None:
    print(f"\n=== WoW: Forever talent import, build {rep['build']}")
    print("rules read from the data:", rep.get("rules_from_data"))
    for k, v in rep["classes"].items():
        print(f"- {k:8} specs {v['specs']}  prerequisites {v['prereq_talents']} (any-of {v['any_of']}) | gates differing from (row-1)*5: {v['gates_default_mismatch']} | rows>1 without gate: {v['no_gate_rows_above_1']}")
        print(f"          first talents per spec: {v['sample']}")
    print(f"tooltip texts: {rep['texts_ok']} / {rep['texts']} fully resolved ({100 * rep['texts_ok'] / max(1, rep['texts']):.1f} %)")
    if rep["problems_by_token"]:
        print("unresolved tokens (top):", rep["problems_by_token"].most_common(12))
    print("ignored trees (id, nodes, clusters):", rep["ignored_trees"])
    for line in rep.get("offgrid", []):
        print("OFF-GRID:", line)
    if rep["missing_classes"]:
        print("classes without a calculator tree:", rep["missing_classes"])
    for w in rep["warnings"]:
        print("WARNING:", w)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", help="client build (default: newest wow_classic_beta build)")
    ap.add_argument("--refresh", action="store_true", help="download the tables again")
    ap.add_argument("--publish", action="store_true", help="copy the staging files to data/wow_talents/ (refuses if anything is unresolved)")
    ap.add_argument("--allow-unresolved", action="store_true", help="with --publish: publish even if some texts are unresolved")
    args = ap.parse_args()

    if args.publish:
        files = sorted(STAGING_DIR.glob("*.json"))
        if not files:
            sys.exit("nothing in staging: run the importer first")
        bad = []
        for f in files:
            for spec in json.loads(f.read_text(encoding="utf-8"))["specs"]:
                for t in spec["talents"]:
                    if t.get("incomplete"):
                        bad.append((f.stem, t["name"]["en"]))
        if bad and not args.allow_unresolved:
            sys.exit(f"{len(bad)} talents have an incomplete text (e.g. {bad[:3]}); refusing to publish (use --allow-unresolved to accept the flagged ones)")
        FINAL_DIR.mkdir(parents=True, exist_ok=True)
        for f in files:
            (FINAL_DIR / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"published {len(files)} class files to {FINAL_DIR}")
        return

    build_id = args.build or latest_beta_build()
    print(f"build {build_id}: reading tables (cache: {RAW_DIR / build_id})")
    T = Tables(build_id, args.refresh)
    rep = build(T, STAGING_DIR)
    report(rep)
    print(f"\nwritten to {STAGING_DIR} (staging: not used by the site build unless WOW_TALENTS_PREVIEW=1)")


if __name__ == "__main__":
    main()
