"""Re-apply bench/score.py to the stored replies of every run (scorer fixes must not require re-running models).

Usage: python bench/rescore.py [--dry-run] [--report PATH] [run_dir ...]

Each changed row keeps its previous score under `score_prev` (with `scorer_prev`, the version that produced it, "0.2" when
unknown) and records the new `scorer` version; unchanged rows only get `scorer`. A diff report (markdown) summarises, per
dataset, model, condition and task type, how many rows changed correctness in each direction and how the abstention flag
moved. With --dry-run nothing is written except the report.
"""
from __future__ import annotations
import argparse, collections, json, time
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "bench"))
from score import score, SCORER_VERSION

DATASETS = {"vindr": "pilot-vindr-20", "vindr-paper": "paper-vindr-100", "nih-paper": "paper-nih-50", "bonescan": "bonescan-40"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", default=str(ROOT / f"docs/reports/rescore-scorer-{SCORER_VERSION}.md"))
    ap.add_argument("runs", nargs="*")
    a = ap.parse_args()
    runs = [Path(p) for p in a.runs] or sorted(p for p in (ROOT / "bench/results").glob("*") if (p / "results.jsonl").exists())
    changes = collections.Counter(); abst = collections.Counter(); examples = collections.defaultdict(list); per_run = []
    total = 0; changed_total = 0
    for r in runs:
        tj = r / "tasks.json"
        if not tj.exists():
            continue
        tasks = {t["id"]: t for t in json.loads(tj.read_text())}
        ds = DATASETS.get(Path(next(iter(tasks.values()))["pkg"]).parent.name, "unknown") if tasks else "unknown"
        rows = [json.loads(l) for l in (r / "results.jsonl").read_text().splitlines() if l.strip()]
        changed = 0
        for x in rows:
            if x.get("error") or x["task"] not in tasks:
                continue
            total += 1
            old = x.get("score") or {}; new = score(tasks[x["task"]], x["reply"])
            if new != old:
                changed += 1
                key = (ds, x["model"].replace("ollama/", "").replace(":675b:cloud", ":675b-cloud"), x["condition"], x["type"])
                oc, nc = bool(old.get("correct")), bool(new.get("correct"))
                if oc != nc:
                    changes[key + ("wrong→correct" if nc else "correct→wrong",)] += 1
                oa, na = bool(old.get("abstained")), bool(new.get("abstained"))
                if oa != na:
                    abst[key + ("flag removed" if oa else "flag added",)] += 1
                if len(examples[key]) < 2:
                    examples[key].append((x["reply"] or "")[:140].replace("\n", " "))
                if not a.dry_run:
                    if "score_prev" not in x:
                        x["score_prev"] = old; x["scorer_prev"] = x.get("scorer", "0.2")
                    x["score"] = new
            if not a.dry_run:
                x["scorer"] = SCORER_VERSION
        changed_total += changed
        per_run.append((r.name, ds, len(rows), changed))
        if not a.dry_run:
            (r / "results.jsonl").write_text("\n".join(json.dumps(x) for x in rows) + "\n")
        print(f"{r.name[:60]}: {changed} scores changed")
    # report
    L = [f"# Rescore with scorer {SCORER_VERSION} ({time.strftime('%Y-%m-%d %H:%M')}; {'dry run' if a.dry_run else 'applied'})", "",
         f"Rows rescored: {total}; rows whose score dict changed: {changed_total} (any key, including value/abs_error; "
         f"correctness changes and abstention-flag changes are listed below). Previous scores are kept per row as `score_prev`.", "",
         "## Correctness changes per dataset, model, condition, task type", "", "| dataset | model | condition | task | direction | rows |", "|---|---|---|---|---|---|"]
    for (ds, m, c, t, d), n in sorted(changes.items()):
        L.append(f"| {ds} | {m} | {c} | {t} | {d} | {n} |")
    L += ["", "## Abstention-flag changes", "", "| dataset | model | condition | task | change | rows |", "|---|---|---|---|---|---|"]
    for (ds, m, c, t, d), n in sorted(abst.items()):
        L.append(f"| {ds} | {m} | {c} | {t} | {d} | {n} |")
    L += ["", "## Examples of changed replies (first 140 characters)", ""]
    for key, ex in sorted(examples.items()):
        for e in ex:
            L.append(f"- {' | '.join(key)}: `{e}`")
    L += ["", "## Per run", "", "| run | dataset | rows | changed |", "|---|---|---|---|"] + [f"| {n} | {d} | {r} | {c} |" for n, d, r, c in per_run]
    Path(a.report).write_text("\n".join(L) + "\n"); print("report:", a.report)


if __name__ == "__main__":
    main()
