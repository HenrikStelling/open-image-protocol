"""Round 3a readout (OIP-Bench, 2026-09-30): orientation conflict trials on canonical and marker-masked renders, the printed-label
reading control, and mark_side with and without the region list.

Usage: python bench/round3_report.py [--out docs/reports/round3a.md] [RUN_DIR ...]
Without run dirs: every bench/results/* whose run_meta.json lists condition ctx3_mask with n = 100.

Conflict cells per image (file labels True/Wrong x image Normal/Mirrored): TN, TM, WN, WM. 'agree' is right in TN and WM.
  comparing policy  (file against pixels):        agree, mirrored, mirrored, agree   -> 100 %
  text-only policy  (trust the file, never look):  agree, agree,    agree,    agree   ->  50 %
  pixel-only policy (judge the image by the display convention, ignore the file): agree, mirrored, agree, mirrored -> 50 %
  file-vs-convention policy (call 'mirrored' when the FILE states the unconventional side, never look at the pixels):
                                                   agree, agree,    mirrored, mirrored -> 50 %
so the four are separable per image from the four verdicts. On the paper's flip check (true-file cells only) the last policy
is indistinguishable from 'always agree', and the pixel-only policy from comparing."""
from __future__ import annotations
import argparse, json, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "bench"))
from paper_stats import wilson, mcnemar_exact, binom_vs_chance, holm   # noqa: E402
from score import score                                                # noqa: E402

CELLS = ("TN", "TM", "WN", "WM")
POLICY = {("agree", "mirrored", "mirrored", "agree"): "compares file and image", ("agree", "agree", "agree", "agree"): "text only (always agree)",
          ("agree", "mirrored", "agree", "mirrored"): "pixels only (ignores the file)", ("agree", "agree", "mirrored", "mirrored"): "file vs convention (ignores the pixels)",
          ("mirrored", "mirrored", "mirrored", "mirrored"): "always mirrored"}
POLICIES = ("compares file and image", "text only (always agree)", "pixels only (ignores the file)", "file vs convention (ignores the pixels)", "always mirrored", "other")


def verdict(row: dict) -> str | None:
    """'agree' / 'mirrored' as the scorer reads the reply; None when it reads neither or the reply was cut off (score.truncated)."""
    if row.get("score", {}).get("truncated"):
        return None
    for v in ("agree", "mirrored"):
        if score({"type": "flip_check", "answer": v}, row["reply"]).get("correct"):
            return v
    return None


def pct(k: int, n: int) -> str:
    if not n: return "–"
    lo, hi = wilson(k, n); return f"{100 * k / n:.0f} % [{100 * lo:.0f}–{100 * hi:.0f}]"


def load(dirs: list[Path]) -> tuple[list[dict], dict]:
    rows, tasks = [], {}
    for d in dirs:
        for t in json.loads((d / "tasks.json").read_text()): tasks[t["id"]] = t
        rows += [r for r in (json.loads(l) for l in (d / "results.jsonl").read_text().splitlines() if l.strip()) if not r.get("error")]
    return rows, tasks


def default_dirs() -> list[Path]:
    out = []
    for d in sorted((ROOT / "bench/results").glob("2026*")):
        mf = d / "run_meta.json"
        if mf.exists() and (d / "results.jsonl").exists():
            m = json.loads(mf.read_text())
            if "ctx3_mask" in (m.get("conditions") or []) and m.get("n") == 100: out.append(d)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("dirs", nargs="*"); ap.add_argument("--out"); a = ap.parse_args()
    dirs = [Path(d) for d in a.dirs] or default_dirs(); rows, tasks = load(dirs)
    models = sorted({r["model"] for r in rows}); L: list[str] = []
    reps = max((r.get("rep", 0) for r in rows), default=0) + 1
    L += ["# OIP-Bench round 3a — conflict trials, marker mask, label reading, mark side", "",
          f"Runs: {', '.join(d.name for d in dirs)}. Rows: {len(rows)} (errors excluded). Replies per cell: up to {reps}. "
          "Tables use repeat 0 unless stated; intervals are Wilson 95 %; paired tests are exact McNemar on items present in both arms, Holm over models.", ""]
    r0 = [r for r in rows if r.get("rep", 0) == 0]
    by = defaultdict(dict)                                   # (model, condition) -> task id -> row (repeat 0)
    for r in r0: by[(r["model"], r["condition"])][r["task"]] = r

    # ---- 1. conflict cells
    L += ["## 1. Orientation conflict trials (file labels true/wrong × image normal/mirrored)", "",
          "| model | render | TN | TM | WN | WM | all four cells | images: compares / text only / pixels only / file vs convention / always mirrored / other |", "|---|---|---|---|---|---|---|---|"]
    pol_rows = {}
    for m in models:
        for c, name in (("ctx3", "canonical"), ("ctx3_mask", "marker-masked")):
            cell = by.get((m, c), {}); conf = {tid: r for tid, r in cell.items() if r["type"] == "orient_conflict"}
            if not conf: continue
            k = {x: 0 for x in CELLS}; n = {x: 0 for x in CELLS}; per_img = defaultdict(dict)
            for tid, r in conf.items():
                t = tasks[tid]; n[t["cell"]] += 1; k[t["cell"]] += bool(r["score"].get("correct")); per_img[t["pkg"]][t["cell"]] = verdict(r)
            pol = Counter(POLICY.get(tuple(v.get(x) for x in CELLS), "other") for v in per_img.values() if len(v) == 4)
            pol_rows[(m, c)] = pol; K, N = sum(k.values()), sum(n.values())
            L.append(f"| {m.split('/', 1)[-1]} | {name} | " + " | ".join(pct(k[x], n[x]) for x in CELLS) + f" | {pct(K, N)} | "
                     + " / ".join(str(pol.get(p, 0)) for p in POLICIES) + f" (of {sum(pol.values())}) |")
    L += ["", "Cells: T/W = the file's edge labels are true / swapped; N/M = the image is normal / mirrored; 'agree' is right in TN and WM. "
          "Every single-source policy scores 50 % on the four cells; only comparing file and image is right on all of them.", ""]

    # ---- 2. mask effect (paired)
    L += ["## 2. Does removing the burned-in side marker change the verdicts? (canonical vs marker-masked, paired items)", "",
          "| model | mirrored images called 'mirrored', true file (TM): canonical → masked | correct overall: canonical → masked | discordant (canonical right only / masked right only) | p | Holm |", "|---|---|---|---|---|---|"]
    ps, lines = [], []
    for m in models:
        A, B = by.get((m, "ctx3"), {}), by.get((m, "ctx3_mask"), {}); ids = sorted(i for i in set(A) & set(B) if A[i]["type"] == "orient_conflict")
        if not ids: continue
        tm = [i for i in ids if tasks[i]["cell"] == "TM"]
        b = sum(1 for i in ids if A[i]["score"].get("correct") and not B[i]["score"].get("correct")); c = sum(1 for i in ids if not A[i]["score"].get("correct") and B[i]["score"].get("correct"))
        p = mcnemar_exact(b, c); ps.append(p)
        lines.append((m, f"{pct(sum(1 for i in tm if A[i]['score'].get('correct')), len(tm))} → {pct(sum(1 for i in tm if B[i]['score'].get('correct')), len(tm))}",
                      f"{pct(sum(1 for i in ids if A[i]['score'].get('correct')), len(ids))} → {pct(sum(1 for i in ids if B[i]['score'].get('correct')), len(ids))}", f"{b} / {c}", p))
    for (m, tmtxt, alltxt, bc, p), ph in zip(lines, holm(ps) if ps else []):
        L.append(f"| {m.split('/', 1)[-1]} | {tmtxt} | {alltxt} | {bc} | {p:.3f} | {ph:.3f} |")
    L.append("")

    # ---- 3. badge reading
    L += ["## 3. Reading the printed edge labels (annotated render, no file; labels as shipped or swapped, truth balanced)", "",
          "| model | labels as shipped | labels swapped | both | p vs 50 % |", "|---|---|---|---|---|"]
    for m in models:
        cell = {i: r for i, r in by.get((m, "labels3"), {}).items() if r["type"] == "badge_read"}
        if not cell: continue
        sw = [r for i, r in cell.items() if tasks[i].get("label_swap")]; no = [r for i, r in cell.items() if not tasks[i].get("label_swap")]
        ok = lambda x: sum(1 for r in x if r["score"].get("correct"))
        L.append(f"| {m.split('/', 1)[-1]} | {pct(ok(no), len(no))} | {pct(ok(sw), len(sw))} | {pct(ok(no) + ok(sw), len(cell))} | {binom_vs_chance(ok(no) + ok(sw), len(cell)):.3g} |")
    L += ["", "A reader of the printed labels scores 100 % on both columns; a display-convention prior scores 100 % / 0 %; the burned-in source marker contradicts the swapped labels.", ""]

    # ---- 4. mark side
    L += ["## 4. Mark side with and without the region list", "",
          "| model | annotated + full file (region list names the side) | annotated + L0–L2 file (no region list) | discordant (full only / L0–L2 only) | p | L0–L2 vs 50 % |", "|---|---|---|---|---|---|"]
    for m in models:
        A = {i: r for i, r in by.get((m, "annot3"), {}).items() if r["type"] == "mark_side"}; B = {i: r for i, r in by.get((m, "annot3_l1"), {}).items() if r["type"] == "mark_side"}
        ids = sorted(set(A) & set(B))
        if not ids: continue
        ka = sum(1 for i in ids if A[i]["score"].get("correct")); kb = sum(1 for i in ids if B[i]["score"].get("correct"))
        b = sum(1 for i in ids if A[i]["score"].get("correct") and not B[i]["score"].get("correct")); c = sum(1 for i in ids if not A[i]["score"].get("correct") and B[i]["score"].get("correct"))
        L.append(f"| {m.split('/', 1)[-1]} | {pct(ka, len(ids))} | {pct(kb, len(ids))} | {b} / {c} | {mcnemar_exact(b, c):.3f} | {binom_vs_chance(kb, len(ids)):.3g} |")
    L.append("")

    # ---- 5. hygiene: truncation, unparsed verdicts, repeats
    L += ["## 5. Reply hygiene", "", "| model | rows | cut off at the output cap (done_reason = length; scored wrong, flagged truncated) | conflict replies with no verdict | think |", "|---|---|---|---|---|"]
    for m in models:
        x = [r for r in r0 if r["model"] == m]; cut = sum(1 for r in x if (r.get("usage") or {}).get("done_reason") == "length")
        nov = sum(1 for r in x if r["type"] == "orient_conflict" and verdict(r) is None); th = {(r.get("usage") or {}).get("think") for r in x}
        L.append(f"| {m.split('/', 1)[-1]} | {len(x)} | {cut} | {nov} | {', '.join(str(t) for t in sorted(th, key=str))} |")
    L.append("")
    if reps > 1:
        L += ["## 6. Stability across repeated replies", "", "| model | condition | items with every repeat | identical score in all repeats | accuracy per repeat |", "|---|---|---|---|---|"]
        allr = defaultdict(lambda: defaultdict(dict))
        for r in rows: allr[(r["model"], r["condition"])][r["task"]][r.get("rep", 0)] = bool(r["score"].get("correct"))
        for (m, c), items in sorted(allr.items()):
            full = {i: v for i, v in items.items() if len(v) == reps}
            if not full: continue
            same = sum(1 for v in full.values() if len(set(v.values())) == 1)
            L.append(f"| {m.split('/', 1)[-1]} | {c} | {len(full)} | {pct(same, len(full))} | " + " / ".join(f"{100 * sum(v[k] for v in full.values()) / len(full):.0f}" for k in range(reps)) + " |")
        L.append("")
    notes = ROOT / "docs/reports/round3a-readings.md"     # hand-written interpretation, appended so a regeneration keeps it
    if notes.exists(): L += ["", notes.read_text().rstrip()]
    out = "\n".join(L)
    if a.out: Path(a.out).write_text(out + "\n"); print("wrote", a.out)
    else: print(out)


if __name__ == "__main__":
    main()
