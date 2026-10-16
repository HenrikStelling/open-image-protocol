"""Runtime experiment readout (PLAN Phase 3b, 2026-10-16): the same local models and items under different daemon settings.

Usage: python bench/runtime_report.py [--out docs/reports/runtime-<date>.md]
Picks every bench/results run whose run_meta.json label starts with "runtime:"; the part after the colon is the runtime
condition (e.g. metal_tensor_disabled, metal_default). Per model: accuracy per task × condition under each runtime (repeat 0 and
pooled over repeats), paired exact McNemar between runtimes on repeat-0 items, stability within each runtime (identical score
across repeats), latency, and reply hygiene (empty replies, output-cap cuts)."""
from __future__ import annotations
import argparse, json, statistics, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "bench"))
from paper_stats import wilson, mcnemar_exact   # noqa: E402


def pct(k, n):
    if not n: return "–"
    lo, hi = wilson(k, n); return f"{100 * k / n:.0f} % [{100 * lo:.0f}–{100 * hi:.0f}]"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out"); a = ap.parse_args()
    runs = []
    for d in sorted((ROOT / "bench/results").glob("2026*")):
        mf = d / "run_meta.json"
        if mf.exists() and (d / "results.jsonl").exists():
            m = json.loads(mf.read_text())
            if (m.get("label") or "").startswith("runtime:"): runs.append((d, m))
    rows = []
    for d, m in runs:
        rt = m["label"].split(":", 1)[1]
        for r in (json.loads(l) for l in (d / "results.jsonl").read_text().splitlines() if l.strip()):
            if not r.get("error"): r["runtime"] = rt; r["ollama_version"] = m.get("ollama_version"); rows.append(r)
    runtimes = sorted({r["runtime"] for r in rows}); models = sorted({r["model"] for r in rows})
    L = ["# Runtime experiment — same models, same items, different daemon settings", "",
         f"Runs: {', '.join(d.name + ' (' + m['label'] + ', ollama ' + str(m.get('ollama_version')) + ', env ' + json.dumps(m.get('ollama_env')) + ')' for d, m in runs)}.",
         f"Rows: {len(rows)}; runtimes: {', '.join(runtimes)}. Items: VinDr-100 seed 0, first 50 packages; conditions raw and ctx; tasks left_edge, "
         "scale_available, ctr, heart_mm, flip_check; three replies per cell. Intervals Wilson 95 %; paired tests exact McNemar on repeat-0 items.", ""]
    by = defaultdict(dict)   # (model, runtime, condition, rep) -> task -> row
    for r in rows: by[(r["model"], r["runtime"], r["condition"], r.get("rep", 0))][r["task"]] = r
    reps = max((r.get("rep", 0) for r in rows), default=0) + 1
    for mdl in models:
        L += [f"## {mdl.split('/', 1)[-1]}", ""]
        # 1. accuracy per task x condition x runtime (repeat 0), paired contrast between the first two runtimes
        L += ["| condition | task | " + " | ".join(f"{rt} (rep 0)" for rt in runtimes) + " | " + " | ".join(f"{rt} (3 reps pooled)" for rt in runtimes)
              + (" | discordant a/b | p |" if len(runtimes) == 2 else " |"), "|---|---|" + "---|" * (2 * len(runtimes)) + ("---|---|" if len(runtimes) == 2 else "")]
        for c in ("raw", "ctx"):
            types = sorted({r["type"] for r in rows if r["condition"] == c and r["model"] == mdl})
            for t in types:
                cells = []
                for rt in runtimes:
                    x = [r for r in by.get((mdl, rt, c, 0), {}).values() if r["type"] == t]
                    cells.append(pct(sum(1 for r in x if r["score"].get("correct")), len(x)))
                for rt in runtimes:
                    x = [r for k in range(reps) for r in by.get((mdl, rt, c, k), {}).values() if r["type"] == t]
                    cells.append(pct(sum(1 for r in x if r["score"].get("correct")), len(x)))
                extra = ""
                if len(runtimes) == 2:
                    A = {i: r for i, r in by.get((mdl, runtimes[0], c, 0), {}).items() if r["type"] == t}; B = {i: r for i, r in by.get((mdl, runtimes[1], c, 0), {}).items() if r["type"] == t}
                    ids = sorted(set(A) & set(B))
                    b = sum(1 for i in ids if A[i]["score"].get("correct") and not B[i]["score"].get("correct")); cc = sum(1 for i in ids if not A[i]["score"].get("correct") and B[i]["score"].get("correct"))
                    extra = f" {b}/{cc} | {mcnemar_exact(b, cc):.3f} |"
                L.append(f"| {c} | {t} | " + " | ".join(cells) + " |" + extra)
        L.append("")
        # 2. stability and hygiene per runtime
        L += ["| runtime | items with 3 replies | identical score in all 3 | empty replies | cut off at cap | latency median s | ollama |", "|---|---|---|---|---|---|---|"]
        for rt in runtimes:
            allr = defaultdict(dict)
            for k in range(reps):
                for c in ("raw", "ctx"):
                    for i, r in by.get((mdl, rt, c, k), {}).items(): allr[(c, i)][k] = r
            full = {i: v for i, v in allr.items() if len(v) == reps}
            same = sum(1 for v in full.values() if len({bool(r["score"].get("correct")) for r in v.values()}) == 1)
            x = [r for v in allr.values() for r in v.values()]
            empty = sum(1 for r in x if not (r["reply"] or "").strip()); cut = sum(1 for r in x if (r.get("usage") or {}).get("done_reason") == "length")
            lat = statistics.median([(r.get("usage") or {}).get("latency_s") or 0 for r in x]) if x else 0
            ver = {r.get("ollama_version") for r in x}
            L.append(f"| {rt} | {len(full)} | {pct(same, len(full))} | {empty} | {cut} | {lat:.1f} | {', '.join(str(v) for v in ver)} |")
        L.append("")
    notes = ROOT / "docs/reports/runtime-readings.md"     # hand-written interpretation, appended so a regeneration keeps it
    if notes.exists(): L += ["", notes.read_text().rstrip()]
    out = "\n".join(L)
    if a.out: Path(a.out).write_text(out + "\n"); print("wrote", a.out)
    else: print(out)


if __name__ == "__main__":
    main()
