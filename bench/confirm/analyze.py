"""Frozen analysis of the pre-registered confirmatory round (docs/paper/preregistration-draft-2026-11-02.md, sections 5 and 6).

Reads one run directory per model (bench/run.py output: results.jsonl, tasks.json, run_meta.json), takes the FIRST reply of every
item (rep 0) as the primary data, and evaluates the six pre-registered statements H1a, H1b, H2a, H2b, H3a, H3b exactly as
registered: per-model one-sided exact binomial tests (or exact McNemar for H2b), Holm correction within each statement's family,
and a count of models meeting the per-model criterion against the registered minimum. Repeats 1 and 2, when present, feed the
secondary table only (accuracy per repeat, identical verdicts). Nothing here is tuned to the data: thresholds and minimum counts
are constants below and must match the registration.

Usage: python bench/confirm/analyze.py --runs bench/results/<dir> [...]  [--conflict-condition ctx] [--out docs/reports/confirmatory-<date>.md]
       python bench/confirm/analyze.py --label confirm:   (every run dir whose run_meta.label starts with the prefix; latest per model)
Exit status 2 when a primary row is missing or an error row remains at rep 0 (the registration requires refilling with --resume
before analysis); the report then names them as deviations.
"""
from __future__ import annotations
import argparse, glob, json, math, sys, time
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]

MODELS = ["claude", "gpt", "gemini", "ollama/gemma4:31b-cloud", "ollama/gemma4:e4b-it-qat", "ollama/glm-5.3-flash:cloud",
          "ollama/kimi-k3:cloud", "ollama/medgemma1.5:4b", "ollama/minimax-m3:cloud", "ollama/mistral-large-3:675b-cloud"]
COMPARERS = ["gemini", "gpt"]                       # H1b names these two models in advance
FACT_TASKS = ["left_edge", "scale_available", "ctr", "heart_mm"]
ALPHA = 0.05
# statement -> (per-model criterion, minimum number of models)
H = {
    "H1a": dict(text="WN cell (file labels swapped, image normal): accuracy below 50 %", p0=0.5, side="less", point=None, min_models=5),
    "H1b": dict(text="WN cell accuracy of gemini-3.8-flash and gpt-5.6-terra at least 90 % (test against 75 %)", p0=0.75, side="greater", point=0.90, min_models=2),
    "H2a": dict(text="wrong label in the OIP file adopted on at least 50 % of images (test against 35 %)", p0=0.35, side="greater", point=0.50, min_models=5),
    "H2b": dict(text="the OIP file is adopted less often than the plain note (exact McNemar, one-sided)", min_models=5),
    "H3a": dict(text="with the full file, each of the four fact tasks at least 95 % correct (test against 80 %)", p0=0.80, side="greater", point=0.95, min_models=8),
    "H3b": dict(text="image only, scale availability below 50 %", p0=0.5, side="less", point=None, min_models=8),
}


# ---- statistics -------------------------------------------------------------------------------------------------------------
def pbinom_le(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def binom_test(k: int, n: int, p0: float, side: str) -> float:
    if n == 0:
        return float("nan")
    return pbinom_le(k, n, p0) if side == "less" else 1 - pbinom_le(k - 1, n, p0)


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def holm(ps: list[float]) -> list[float]:
    idx = sorted(range(len(ps)), key=lambda i: (math.inf if math.isnan(ps[i]) else ps[i])); m = len(ps); out = [float("nan")] * m; run = 0.0
    for rank, i in enumerate(idx):
        if math.isnan(ps[i]):
            continue
        run = max(run, min(1.0, (m - rank) * ps[i])); out[i] = run
    return out


def mcnemar_one_sided(b: int, c: int) -> float:
    """H1: b > c (plain adopted and OIP not, more often than the reverse); exact, conditional on the discordant pairs."""
    n = b + c
    return float("nan") if n == 0 else pbinom_le(c, n, 0.5)


# ---- data -------------------------------------------------------------------------------------------------------------------
def load_runs(d: Path) -> list[dict]:
    """One record per model in the directory (a lane directory may hold several Ollama models)."""
    meta = json.loads((d / "run_meta.json").read_text()); tasks = {t["id"]: t for t in json.loads((d / "tasks.json").read_text())}
    rows = [json.loads(l) for l in open(d / "results.jsonl", encoding="utf-8") if l.strip()]
    by: dict[str, list] = defaultdict(list)
    for r in rows:
        by[r["model"]].append(r)
    return [dict(dir=d, meta=meta, tasks=tasks, rows=rs, model=m) for m, rs in by.items()]


def verdict(row: dict) -> bool | None:
    """Binary verdict per reply: correct (adopted for findings_misled); None for an error row."""
    if row.get("error"):
        return None
    s = row.get("score") or {}
    return bool(s.get("adopted_misleading")) if row["type"] == "findings_misled" else bool(s.get("correct"))


def primary(run: dict, conflict_condition: str) -> dict:
    """rep-0 verdicts per statement for one model."""
    T = run["tasks"]; first: dict = {}; missing: list = []; errors: list = []
    for r in run["rows"]:
        if r.get("rep", 0) != 0:
            continue
        key = (r["condition"], r["task"])
        if key in first:            # --resume can leave the item twice only if the first was an error row; keep the good one
            if first[key] is None and verdict(r) is not None:
                first[key] = verdict(r)
            continue
        first[key] = verdict(r)
    out: dict = dict(wn=[], fact={t: [] for t in FACT_TASKS}, raw_scale=[], adopt_plain={}, adopt_oip={})
    for tid, t in T.items():
        if t["type"] == "orient_conflict" and t.get("cell") == "WN":
            v = first.get((conflict_condition, tid), "missing")
            (out["wn"].append(v) if v != "missing" else missing.append((conflict_condition, tid)))
        if t["type"] in FACT_TASKS:
            v = first.get(("ctx", tid), "missing")
            (out["fact"][t["type"]].append(v) if v != "missing" else missing.append(("ctx", tid)))
            if t["type"] == "scale_available":
                v = first.get(("raw", tid), "missing")
                (out["raw_scale"].append(v) if v != "missing" else missing.append(("raw", tid)))
        if t["type"] == "findings_misled":
            for cond, k in (("misled_plain", "adopt_plain"), ("misled_oip", "adopt_oip")):
                v = first.get((cond, tid), "missing")
                (out[k].__setitem__(tid, v) if v != "missing" else missing.append((cond, tid)))
    for k in ("wn", "raw_scale"):
        errors += [k] * sum(1 for v in out[k] if v is None)
    for t in FACT_TASKS:
        errors += [t] * sum(1 for v in out["fact"][t] if v is None)
    errors += ["adopt"] * sum(1 for v in list(out["adopt_plain"].values()) + list(out["adopt_oip"].values()) if v is None)
    out["missing"] = missing; out["errors"] = errors
    return out


def count(vs: list) -> tuple[int, int]:
    vs = [v for v in vs if v is not None]
    return sum(1 for v in vs if v), len(vs)


# ---- report -----------------------------------------------------------------------------------------------------------------
def pct(k: int, n: int) -> str:
    if n == 0:
        return "–"
    lo, hi = wilson(k, n)
    return f"{100 * k / n:.0f} % [{100 * lo:.0f}–{100 * hi:.0f}] ({k}/{n})"


def fmt_p(p: float) -> str:
    return "–" if math.isnan(p) else ("< 0.001" if p < 0.001 else f"{p:.3f}")


def evaluate(P: dict[str, dict]) -> tuple[list[str], dict]:
    lines: list[str] = []; verdicts: dict = {}
    models = [m for m in MODELS if m in P]
    absent = [m for m in MODELS if m not in P]

    def family(name: str, entries: list[tuple[str, int, int]], p0: float, side: str, point: float | None, min_models: int) -> None:
        ps = [binom_test(k, n, p0, side) for _, k, n in entries]; ph = holm(ps); met = 0
        lines.append(f"\n### {name}: {H[name]['text']}\n")
        lines.append("| model | estimate [95 % CI] | p (one-sided) | p Holm | criterion met |"); lines.append("|---|---|---|---|---|")
        for (label, k, n), p, q in zip(entries, ps, ph):
            ok = (not math.isnan(q)) and q < ALPHA and (point is None or (n > 0 and (k / n >= point if side == "greater" else k / n < point)))
            met += ok
            lines.append(f"| {label} | {pct(k, n)} | {fmt_p(p)} | {fmt_p(q)} | {'yes' if ok else 'no'} |")
        verdicts[name] = dict(met=met, required=min_models, confirmed=met >= min_models)
        lines.append(f"\n**{name}: {met} of {len(entries)} criteria met; registered minimum {min_models}; "
                     f"{'CONFIRMED' if met >= min_models else 'NOT confirmed'}.**" + (f" Models without a run count as not met: {', '.join(absent)}." if absent and name != 'H1b' else ""))

    family("H1a", [(m, *count(P[m]["wn"])) for m in models] + [(m, 0, 0) for m in absent], 0.5, "less", None, H["H1a"]["min_models"])
    family("H1b", [(m, *count(P[m]["wn"])) if m in P else (m, 0, 0) for m in COMPARERS], 0.75, "greater", 0.90, H["H1b"]["min_models"])
    family("H2a", [(m, *count(list(P[m]["adopt_oip"].values()))) for m in models] + [(m, 0, 0) for m in absent], 0.35, "greater", 0.50, H["H2a"]["min_models"])
    # H2b: exact McNemar within model on paired items
    lines.append(f"\n### H2b: {H['H2b']['text']}\n")
    lines.append("| model | adopted plain | adopted OIP | b (plain only) | c (OIP only) | p (one-sided) | p Holm | criterion met |"); lines.append("|---|---|---|---|---|---|---|---|")
    rows2 = []
    for m in models:
        a, o = P[m]["adopt_plain"], P[m]["adopt_oip"]; ids = [i for i in a if i in o and a[i] is not None and o[i] is not None]
        b = sum(1 for i in ids if a[i] and not o[i]); c = sum(1 for i in ids if o[i] and not a[i])
        rows2.append((m, sum(1 for i in ids if a[i]), sum(1 for i in ids if o[i]), len(ids), b, c, mcnemar_one_sided(b, c)))
    ph = holm([r[6] for r in rows2]); met = 0
    for (m, ka, ko, n, b, c, p), q in zip(rows2, ph):
        ok = (not math.isnan(q)) and q < ALPHA and b > c; met += ok
        lines.append(f"| {m} | {pct(ka, n)} | {pct(ko, n)} | {b} | {c} | {fmt_p(p)} | {fmt_p(q)} | {'yes' if ok else 'no'} |")
    verdicts["H2b"] = dict(met=met, required=H["H2b"]["min_models"], confirmed=met >= H["H2b"]["min_models"])
    lines.append(f"\n**H2b: {met} of {len(rows2) + len(absent)} criteria met; registered minimum {H['H2b']['min_models']}; "
                 f"{'CONFIRMED' if met >= H['H2b']['min_models'] else 'NOT confirmed'}.**")
    # H3a: four tasks per model; a model meets the criterion when all four tasks meet it (Holm over all model x task tests)
    lines.append(f"\n### H3a: {H['H3a']['text']}\n")
    ent = [(m, t, *count(P[m]["fact"][t])) for m in models for t in FACT_TASKS]
    ps = [binom_test(k, n, 0.80, "greater") for _, _, k, n in ent]; ph = holm(ps); ok_mt = {}
    lines.append("| model | task | estimate [95 % CI] | p (one-sided) | p Holm | met |"); lines.append("|---|---|---|---|---|---|")
    for (m, t, k, n), p, q in zip(ent, ps, ph):
        ok = (not math.isnan(q)) and q < ALPHA and n > 0 and k / n >= 0.95; ok_mt[(m, t)] = ok
        lines.append(f"| {m} | {t} | {pct(k, n)} | {fmt_p(p)} | {fmt_p(q)} | {'yes' if ok else 'no'} |")
    met = sum(1 for m in models if all(ok_mt[(m, t)] for t in FACT_TASKS))
    verdicts["H3a"] = dict(met=met, required=H["H3a"]["min_models"], confirmed=met >= H["H3a"]["min_models"])
    lines.append(f"\n**H3a: {met} of {len(models) + len(absent)} models meet the criterion on all four tasks; registered minimum {H['H3a']['min_models']}; "
                 f"{'CONFIRMED' if met >= H['H3a']['min_models'] else 'NOT confirmed'}.**")
    family("H3b", [(m, *count(P[m]["raw_scale"])) for m in models] + [(m, 0, 0) for m in absent], 0.5, "less", None, H["H3b"]["min_models"])
    return lines, verdicts


def secondary(runs: dict[str, dict], conflict_condition: str) -> list[str]:
    """Descriptive: four-cell accuracy per repeat, identical verdicts across repeats, cells per repeat; no claims."""
    L = ["\n## Secondary (descriptive, not registered as confirmatory)\n",
         "| model | replies per item | four cells, rep 0/1/2 | WN rep 0/1/2 | OIP-file adoption rep 0/1/2 | conflict items identical in all repeats |", "|---|---|---|---|---|---|"]
    for m, run in runs.items():
        T = run["tasks"]; by = defaultdict(dict)
        for r in run["rows"]:
            by[(r["condition"], r["task"])][r.get("rep", 0)] = verdict(r)
        reps = sorted({r.get("rep", 0) for r in run["rows"]})
        def acc(sel, rep):
            vs = [by[k].get(rep) for k in sel if rep in by[k]]; vs = [v for v in vs if v is not None]
            return f"{100 * sum(vs) / len(vs):.0f}" if vs else "–"
        conf = [(conflict_condition, i) for i, t in T.items() if t["type"] == "orient_conflict"]
        wn = [(conflict_condition, i) for i, t in T.items() if t["type"] == "orient_conflict" and t.get("cell") == "WN"]
        oip = [("misled_oip", i) for i, t in T.items() if t["type"] == "findings_misled"]
        full = [k for k in conf if all(rep in by[k] and by[k][rep] is not None for rep in reps)]
        same = sum(1 for k in full if len({by[k][rep] for rep in reps}) == 1)
        L.append(f"| {m} | {len(reps)} | {' / '.join(acc(conf, r) for r in reps)} | {' / '.join(acc(wn, r) for r in reps)} | "
                 f"{' / '.join(acc(oip, r) for r in reps)} | {pct(same, len(full)) if len(reps) > 1 else '–'} |")
    return L


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="*", default=[]); ap.add_argument("--label", help="run_meta.label prefix, e.g. confirm:")
    ap.add_argument("--conflict-condition", default="ctx", help="condition that carries the orient_conflict items (ctx in the registered design)")
    ap.add_argument("--out", default=f"docs/reports/confirmatory-{time.strftime('%Y-%m-%d')}.md")
    a = ap.parse_args()
    dirs = [Path(d) for d in a.runs]
    if a.label:
        for d in sorted(glob.glob(str(ROOT / "bench/results/*/run_meta.json"))):
            if str(json.load(open(d)).get("label") or "").startswith(a.label):
                dirs.append(Path(d).parent)
    if not dirs:
        sys.exit("no run directories (use --runs or --label)")
    runs: dict[str, dict] = {}
    for d in dirs:
        for r in load_runs(d):
            if r["model"] in runs and runs[r["model"]]["meta"]["started"] >= r["meta"]["started"]:
                continue
            runs[r["model"]] = r
    P = {m: primary(r, a.conflict_condition) for m, r in runs.items()}
    lines = [f"# Confirmatory round — pre-registered analysis ({time.strftime('%Y-%m-%d')})\n",
             "Primary data: the first reply (rep 0) of every item. Per-model one-sided exact binomial tests (exact McNemar for H2b), "
             "Holm within each statement, alpha 0.05; a statement is confirmed when at least the registered number of models meets its criterion. "
             "Registration: docs/paper/preregistration-draft-2026-11-02.md (final text on OSF).\n",
             "| model | model id | run dir | started | harness commit(s) | tasks / scorer | rep-0 items missing | rep-0 error rows |", "|---|---|---|---|---|---|---|---|"]
    bad = 0
    for m, r in runs.items():
        commits = sorted({x.get("harness_commit", "?") for x in r["rows"]}); ids = sorted({x.get("model_id", "?") for x in r["rows"]})
        lines.append(f"| {m} | {', '.join(ids)} | {r['dir'].name} | {r['meta'].get('started', '?')} | {', '.join(commits)} | "
                     f"{r['meta'].get('tasks_version', '?')} / {r['meta'].get('scorer', '?')} | {len(P[m]['missing'])} | {len(P[m]['errors'])} |")
        bad += len(P[m]["missing"]) + len(P[m]["errors"])
    absent = [m for m in MODELS if m not in runs]
    if absent:
        lines.append(f"\nModels without a run (count as not meeting any criterion): {', '.join(absent)}.")
    if bad:
        lines.append(f"\n**Deviation: {bad} rep-0 items missing or in error; the registration requires every primary item to be refilled before analysis. Reported as is.**")
    body, V = evaluate(P)
    lines.append("\n## Primary statements\n")
    lines.append("| statement | criteria met | registered minimum | result |"); lines.append("|---|---|---|---|")
    for k, v in V.items():
        lines.append(f"| {k} | {v['met']} | {v['required']} | {'confirmed' if v['confirmed'] else 'not confirmed'} |")
    lines += body
    lines += secondary(runs, a.conflict_condition)
    out = ROOT / a.out; out.parent.mkdir(parents=True, exist_ok=True); out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:4 + len(runs)] + ["", *lines[lines.index("\n## Primary statements\n"):lines.index("\n## Primary statements\n") + 4 + len(V)]]))
    print("wrote", out)
    sys.exit(2 if bad else 0)


if __name__ == "__main__":
    main()
