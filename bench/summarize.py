"""Aggregate bench/results/*/results.jsonl into a table: model × condition × task type -> accuracy / F1 / adoption rate.
Usage: python bench/summarize.py [run_dir ...]   (default: all runs)"""
import json, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
runs = [Path(p) for p in sys.argv[1:]] or sorted((ROOT / "bench/results").glob("*"))
rows = []
for r in runs:
    f = r / "results.jsonl"
    if f.exists(): rows += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
agg = collections.defaultdict(lambda: {"n": 0, "correct": 0, "f1": 0.0, "adopted": 0, "errors": 0, "abstain": 0})
for x in rows:
    k = (x["model"], x["condition"], x["type"]); a = agg[k]; a["n"] += 1
    if x.get("error"): a["errors"] += 1; continue
    s = x.get("score") or {}
    a["correct"] += int(bool(s.get("correct"))); a["f1"] += s.get("f1", 0.0); a["adopted"] += int(bool(s.get("adopted_misleading"))); a["abstain"] += int(bool(s.get("abstained")))
print(f"{'model':28s} {'condition':13s} {'task':17s} {'n':>4s} {'acc/F1':>7s} {'adopt':>6s} {'err':>4s}")
for (m, c, t), a in sorted(agg.items()):
    n_ok = a["n"] - a["errors"]
    val = (a["f1"] / n_ok) if t.startswith("findings") and n_ok else (a["correct"] / n_ok if n_ok else 0)
    print(f"{m:28s} {c:13s} {t:17s} {a['n']:4d} {val:7.2f} {(a['adopted']/n_ok if t=='findings_misled' and n_ok else 0):6.2f} {a['errors']:4d}")
# headline: gating tasks, raw vs ctx vs annot per model
print("\nGating (understanding) accuracy per model and condition:")
g = collections.defaultdict(lambda: [0, 0])
for x in rows:
    if x.get("gating") and not x.get("error"):
        k = (x["model"], x["condition"]); g[k][0] += int(bool((x.get("score") or {}).get("correct"))); g[k][1] += 1
for (m, c), (ok, n) in sorted(g.items()): print(f"  {m:28s} {c:13s} {ok:4d}/{n:<4d} {ok/n:.2f}")
