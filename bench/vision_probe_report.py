"""Report for the render probe (2026-09-27): flip check and left-edge accuracy per model and condition on the 40-image VinDr subset.

Conditions: ctx_ctl (canonical + full file, same-day control), annot_ctx / annot_only (annotated render with / without the file),
insp_ctx / insp_only (inspection sheet with / without the file). Flip items: the shown render is built from the mirrored canonical
while the printed edge labels (and the file, where present) keep the true orientation. Wilson 95 % CIs; exact McNemar of every
condition against ctx_ctl on the paired items; images with both flip items correct.

Usage: ~/oip-venv/bin/python bench/vision_probe_report.py [run_dir ...]   (default: all runs whose run_meta.json lists insp_only)
"""
from __future__ import annotations
import json, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from paper_stats import wilson, mcnemar_exact, holm   # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONDS = ["ctx_ctl", "annot_ctx", "annot_only", "insp_ctx", "insp_only"]


def load(runs):
    idx = collections.defaultdict(dict)
    for r in runs:
        for line in (r / "results.jsonl").read_text().splitlines():
            if not line.strip():
                continue
            x = json.loads(line)
            if x.get("error"):
                continue
            idx[(x["model"].replace("ollama/", ""), x["condition"])][x["task"]] = x
    return idx


def main():
    runs = [Path(p) for p in sys.argv[1:]] or [p for p in sorted((ROOT / "bench/results").glob("2026*")) if (p / "run_meta.json").exists()
                                                  and "insp_only" in json.loads((p / "run_meta.json").read_text()).get("conditions", [])]
    idx = load(runs); models = sorted({m for m, _ in idx})
    fmt = lambda k, n: f"{100*k/n:.0f} % ({100*wilson(k, n)[0]:.0f}–{100*wilson(k, n)[1]:.0f}; n={n})" if n else "–"
    L = ["# Render probe: flip check and left edge on the annotated render and the inspection sheet", "", f"Runs: {', '.join(r.name for r in runs)}", ""]
    for typ, title in (("flip_check", "Flip check (mirrored render vs printed/stated orientation)"), ("left_edge", "Left edge (which patient side is at the image's left edge)")):
        L += [f"## {title}", "", "| model | " + " | ".join(CONDS) + " | both flip items right (ctx_ctl → insp_only) |" if typ == "flip_check" else f"## {title}", ""]
        if typ == "flip_check":
            L[-2] = "| model | " + " | ".join(CONDS) + " | both items right per image, by condition |"; L += ["|---|" + "---|" * (len(CONDS) + 1)]
        else:
            L += ["| model | " + " | ".join(CONDS) + " |", "|---|" + "---|" * len(CONDS)]
        for m in models:
            cells = []; both = []
            for c in CONDS:
                rows = [x for x in idx.get((m, c), {}).values() if x["type"] == typ]
                k = sum(1 for x in rows if x["score"].get("correct")); cells.append(fmt(k, len(rows)))
                if typ == "flip_check":
                    by = collections.defaultdict(list)
                    for x in rows:
                        by[x["task"].split(":")[0]].append(bool(x["score"].get("correct")))
                    both.append(f"{sum(1 for v in by.values() if len(v) == 2 and all(v))}/{len(by)}" if by else "–")
            L.append(f"| {m} | " + " | ".join(cells) + (" | " + " / ".join(both) + " |" if typ == "flip_check" else " |"))
        L += [""]
        # paired contrasts vs control
        L += [f"### {typ}: each condition against ctx_ctl (paired items; b = right only in control, c = right only in the condition; exact McNemar, Holm over models)", "",
              "| model | " + " | ".join(f"{c}: Δpp, b/c, p" for c in CONDS[1:]) + " |", "|---|" + "---|" * (len(CONDS) - 1)]
        table = {}
        for c in CONDS[1:]:
            ps = {}
            for m in models:
                A, B = idx.get((m, "ctx_ctl"), {}), idx.get((m, c), {})
                ids = [i for i in A if i in B and A[i]["type"] == typ]
                b = sum(1 for i in ids if A[i]["score"].get("correct") and not B[i]["score"].get("correct"))
                cc = sum(1 for i in ids if not A[i]["score"].get("correct") and B[i]["score"].get("correct"))
                d = 100 * (cc - b) / len(ids) if ids else 0.0
                table[(m, c)] = [d, b, cc]; ps[m] = mcnemar_exact(b, cc)
            adj = dict(zip(ps, holm(list(ps.values()))))
            for m in models:
                table[(m, c)].append(adj[m])
        for m in models:
            L.append(f"| {m} | " + " | ".join(f"{table[(m, c)][0]:+.0f}, {table[(m, c)][1]}/{table[(m, c)][2]}, {'<0.001' if table[(m, c)][3] < 0.001 else f'{table[(m, c)][3]:.3f}'}" for c in CONDS[1:]) + " |")
        L += [""]
    out = ROOT / "docs/reports/render-probe-2026-09-27.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
