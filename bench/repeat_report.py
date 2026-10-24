"""Repeat-subset readout (OIP-Bench B7, 2026-10-24): run-to-run reliability of the main-result cells.

Usage: python bench/repeat_report.py [--label b7:repeat_subset] [--paper-until 20260922] [--out docs/reports/repeat-subset-<date>.md]

Reads every bench/results/* whose run_meta.json carries the label (default `b7:repeat_subset`): N replies per
(model, condition, item) on a fixed package subset. For each model x condition x task type it reports
  * accuracy per repeat, its range, and the share of items with the same verdict in every repeat;
  * Fleiss' kappa of the binary verdict (correct / adopted) across the repeats (1 = identical verdicts, 0 = chance);
  * for comparison, the paper run's single reply on the same items (latest paper-window run per cell, run dirs dated up to
    --paper-until, package dir `vindr-paper`), re-scored with the current scorer, with its accuracy and the share of
    items where it agrees with the majority verdict of today's repeats.
The paper run and the repeats differ in more than the day: the packages carry the CheXmask cross-check table and template
0.2.1 since 2026-10-17, so the full-file prompt is not byte-identical to the paper's (prompt hashes differ). Within the
repeat run every item received the same prompt in all repeats (asserted below).
"""
from __future__ import annotations
import argparse, json, re, sys, time
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "bench"))
from score import score  # noqa: E402

TYPES = ("left_edge", "scale_available", "ctr", "heart_mm", "flip_check", "findings_misled")
MODEL_ORDER = ("claude", "gemini", "gpt", "ollama/gemma4:31b-cloud", "ollama/glm-5.3-flash:cloud", "ollama/kimi-k3:cloud", "ollama/minimax-m3:cloud",
               "ollama/mistral-large-3:675b-cloud", "ollama/qwen3.5:cloud", "ollama/gemma4:e4b-it-qat", "ollama/medgemma1.5:4b")


def verdict(task: dict, reply: str | None, err) -> bool | None:
    """Binary verdict per reply: correct (adopted for findings_misled); None for an error row."""
    if err or reply is None:
        return None
    s = score(task, reply)
    return bool(s.get("adopted_misleading")) if task["type"] == "findings_misled" else bool(s.get("correct"))


def fleiss_kappa(items: list[list[bool]]) -> float | None:
    """Fleiss' kappa for binary ratings; items = per-item list of verdicts (same number of raters each)."""
    items = [v for v in items if v]
    if not items:
        return None
    n = len(items[0])
    if n < 2 or any(len(v) != n for v in items):
        return None
    p_true = sum(sum(v) for v in items) / (n * len(items)); p_false = 1 - p_true
    pe = p_true ** 2 + p_false ** 2
    pbar = sum((sum(v) ** 2 + (n - sum(v)) ** 2 - n) / (n * (n - 1)) for v in items) / len(items)
    return 1.0 if pe == 1 else (pbar - pe) / (1 - pe)


def load_repeat_runs(label: str) -> tuple[dict, dict, list[str]]:
    """rows[(model, cond, task_id)] -> {rep: (reply, err, prompt_sha)}, tasks[task_id] -> task, run dirs used."""
    rows: dict = defaultdict(dict); tasks: dict = {}; used = []
    for d in sorted((ROOT / "bench/results").glob("*")):
        meta = d / "run_meta.json"
        if not meta.exists() or json.loads(meta.read_text()).get("label") != label or not (d / "results.jsonl").exists():
            continue
        used.append(d.name)
        for t in json.loads((d / "tasks.json").read_text()):
            tasks[t["id"]] = t
        for line in (d / "results.jsonl").read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            rows[(r["model"], r["condition"], r["task"])][r.get("rep", 0)] = (r.get("reply"), r.get("error"), r.get("prompt_sha256"))
    return rows, tasks, used


def load_paper(until: str, task_ids: set[str]) -> dict:
    """paper[(model, cond, task_id)] -> (reply, err, task) from the latest paper-window run on the vindr-paper packages."""
    out: dict = {}
    for d in sorted((ROOT / "bench/results").glob("2026*")):
        if not re.match(r"\d{8}", d.name) or d.name[:8] > until or not (d / "tasks.json").exists() or not (d / "results.jsonl").exists():
            continue
        tj = {t["id"]: t for t in json.loads((d / "tasks.json").read_text())}
        if not tj or "vindr-paper" not in next(iter(tj.values()))["pkg"]:
            continue
        for line in (d / "results.jsonl").read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r["task"] in task_ids and r["type"] in TYPES and r.get("rep", 0) == 0:
                out[(r["model"], r["condition"], r["task"])] = (r.get("reply"), r.get("error"), tj.get(r["task"]))   # later dirs overwrite: latest run wins
    return out


def pct(k: int, n: int) -> str:
    return f"{100 * k / n:.0f} %" if n else "—"


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--label", default="b7:repeat_subset"); ap.add_argument("--paper-until", default="20260922")
    ap.add_argument("--out", default=f"docs/reports/repeat-subset-{time.strftime('%Y-%m-%d')}.md"); a = ap.parse_args()
    rows, tasks, used = load_repeat_runs(a.label)
    if not rows:
        sys.exit(f"no run dir with label {a.label!r}")
    paper = load_paper(a.paper_until, set(tasks))
    # same prompt in every repeat of an item
    multi = sum(1 for reps in rows.values() if len({p for (_, _, p) in reps.values() if p}) > 1)
    models = [m for m in MODEL_ORDER if any(k[0] == m for k in rows)] + sorted({k[0] for k in rows} - set(MODEL_ORDER))
    conds = sorted({k[1] for k in rows}, key=lambda c: ("raw", "ctx", "misled_plain", "misled_oip").index(c) if c in ("raw", "ctx", "misled_plain", "misled_oip") else 9)
    n_reps = max(len(v) for v in rows.values())
    pkgs = sorted({tid.split(":")[0] for tid in tasks})
    L = [f"# Repeat subset: run-to-run reliability of the main-result cells ({time.strftime('%Y-%m-%d')})", "",
         f"Runs: {', '.join('`' + u + '`' for u in used)}. {len(pkgs)} packages, {n_reps} replies per item, {len(rows)} (model, condition, item) cells, "
         f"{sum(len(v) for v in rows.values())} replies. Items with more than one prompt hash across repeats: {multi}. "
         f"Paper comparison: latest run per cell dated up to {a.paper_until} on the `vindr-paper` packages, re-scored with the current scorer "
         "(the repeat packages carry the CheXmask cross-check table and template 0.2.1, so the full-file prompt differs from the paper's).", "",
         "Columns: accuracy (adoption for findings_misled) per repeat; stable = items with the same verdict in every repeat; kappa = Fleiss' kappa "
         "of the verdict across repeats; paper = the paper run's single reply on the same items; agrees = share of items where the paper verdict "
         "equals the majority verdict of the repeats. Items with an error row in any repeat are dropped from stable/kappa. Kappa is near zero "
         "whenever almost every verdict has the same value (prevalence effect, e.g. 95 % wrong in every repeat), so read it together with stable.", ""]
    summary = defaultdict(list)
    for m in models:
        L += [f"## {m}", "", "| Condition | Task | n | " + " | ".join(f"rep {i}" for i in range(n_reps)) + " | range (pp) | stable | kappa | paper | agrees |",
              "|---|---|---|" + "---|" * n_reps + "---|---|---|---|---|"]
        complete = True
        for c in conds:
            for t in TYPES:
                keys = [k for k in rows if k[0] == m and k[1] == c and tasks[k[2]]["type"] == t]
                if not keys:
                    continue
                per_rep = [[] for _ in range(n_reps)]; items = []; agree = [0, 0]; paper_acc = [0, 0]
                for k in sorted(keys):
                    reps = rows[k]
                    if len(reps) < n_reps:
                        complete = False
                    vs = []
                    for i in range(n_reps):
                        v = verdict(tasks[k[2]], *reps[i][:2]) if i in reps else None
                        vs.append(v)
                        if v is not None:
                            per_rep[i].append(v)
                    if all(v is not None for v in vs) and len(vs) == n_reps:
                        items.append(vs)
                    p = paper.get(k)
                    if p and p[2] is not None:
                        pv = verdict(p[2], p[0], p[1])
                        if pv is not None:
                            paper_acc[1] += 1; paper_acc[0] += pv
                            good = [v for v in vs if v is not None]
                            if good:
                                agree[1] += 1; agree[0] += (pv == (sum(good) * 2 >= len(good)))
                accs = [100 * sum(r) / len(r) if r else None for r in per_rep]
                have = [x for x in accs if x is not None]
                rng = f"{max(have) - min(have):.0f}" if len(have) > 1 else "—"
                stable = sum(1 for v in items if len(set(v)) == 1)
                kap = fleiss_kappa(items)
                L.append(f"| {c} | {t} | {len(keys)} | " + " | ".join(f"{x:.0f} %" if x is not None else "—" for x in accs)
                         + f" | {rng} | {pct(stable, len(items))} ({stable}/{len(items)}) | {kap:.2f} | {pct(*paper_acc)} | {pct(*agree)} |" if kap is not None else
                         f"| {c} | {t} | {len(keys)} | " + " | ".join(f"{x:.0f} %" if x is not None else "—" for x in accs) + f" | {rng} | {pct(stable, len(items))} | — | {pct(*paper_acc)} | {pct(*agree)} |")
                if kap is not None:
                    summary[m].append((c, t, max(have) - min(have) if len(have) > 1 else 0.0, stable / len(items) if items else None, kap))
        if not complete:
            L.append(""); L.append(f"_Incomplete: not every item of {m} has {n_reps} replies yet._")
        L.append("")
    # overview
    L += ["## Overview per model", "", "| Model | cells | largest range (pp) | median stable | median kappa | cells with kappa < 0.6 |", "|---|---|---|---|---|---|"]
    for m in models:
        s = summary.get(m, [])
        if not s:
            continue
        st = sorted(x[3] for x in s if x[3] is not None); ka = sorted(x[4] for x in s)
        L.append(f"| {m} | {len(s)} | {max(x[2] for x in s):.0f} | {100 * st[len(st) // 2]:.0f} % | {ka[len(ka) // 2]:.2f} | {sum(1 for x in s if x[4] < 0.6)} |")
    L.append("")
    out = ROOT / a.out; out.parent.mkdir(parents=True, exist_ok=True); out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(models)} models, {len(rows)} cells)")


if __name__ == "__main__":
    main()
