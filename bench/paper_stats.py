"""Paper statistics for OIP-Bench, computed from the frozen replies in bench/results (no model is called).

Selection rules are those of bench/report.py: dataset = package directory named in the run's tasks.json; latest run directory
per (dataset, model, condition); legacy condition names renamed; NIH `scale_available` rows excluded (truth ill-defined for
low-confidence dataset-derived spacing); CONTAMINATED-* runs excluded; error rows excluded from every denominator and counted;
abstentions and empty replies scored incorrect. Where a task id has several non-error replies in the selected run (a resume
re-asked it), the last reply in file order is used and the repeat is counted.

Added here: Wilson 95 % CIs per cell; exact McNemar tests on paired items for the condition contrasts, Holm-corrected over the
models within a dataset and contrast, with Cohen's g; exact two-sided binomial tests against the 50 % chance level for the
flip-consistency, mark-side and hot-side tasks; a percentile bootstrap CI (2,000 replicates over task items, seed 0) for the
cross-model spread; list-price cost per call for the frontier models; the CXAS-vs-PSPNet cross-check on the 20 pilot images.

Usage: ~/oip-venv/bin/python bench/paper_stats.py  ->  docs/paper/reference-sheet.md + docs/paper/paper-stats.json
"""
from __future__ import annotations
import json, collections, math, random, statistics, time
from pathlib import Path
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "bench/results"
import sys as _sys
_SUFFIX = ("-" + _sys.argv[1]) if len(_sys.argv) > 1 else ""      # e.g. `paper_stats.py scorer-0.3` -> reference-sheet-scorer-0.3.md
OUT_MD = ROOT / f"docs/paper/reference-sheet{_SUFFIX}.md"
OUT_JSON = ROOT / f"docs/paper/paper-stats{_SUFFIX}.json"
DATASETS = {"vindr": "pilot-vindr-20", "vindr-paper": "paper-vindr-100", "nih-paper": "paper-nih-50", "bonescan": "bonescan-40"}
CONDS = ["raw", "ctx_l1", "ctx", "annot"]
COMMON_GATING = ("left_edge", "scale_available", "ctr", "heart_mm")
NM_GATING = ("left_edge_nm", "scale_available_nm", "hot_side")
NM_TYPES = ("modality_nm", "left_edge_nm", "scale_available_nm", "counts_semantics", "hot_side", "flip_check_nm")
FAMILY = {"claude": "frontier", "gpt": "frontier", "gemini": "frontier", "gemma4:e4b-it-qat": "local", "medgemma1.5:4b": "local"}
MODEL_ID = {"claude": "claude-sonnet-5", "gpt": "gpt-5.6-terra", "gemini": "gemini-3.8-flash"}
# $ per 1M tokens (input, output), Sep 2026 price pages; Anthropic cache read 10 % and cache write 125 % of the input price
PRICES = {"claude": (2.0, 10.0), "gpt": (2.0, 12.0), "gemini": (0.75, 3.75)}
ALPHA = 0.05


# ---------------------------------------------------------------- statistics helpers
def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p on the discordant pairs (binomial, p = 0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    return binomtest(min(b, c), n, 0.5, alternative="two-sided").pvalue


def binom_vs_chance(k: int, n: int) -> float:
    return binomtest(k, n, 0.5, alternative="two-sided").pvalue if n else 1.0


def holm(ps: list[float]) -> list[float]:
    m = len(ps); order = sorted(range(m), key=lambda i: ps[i]); adj = [0.0] * m; running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * ps[i]); adj[i] = min(1.0, running)
    return adj


def cell(k: int, n: int) -> dict:
    lo, hi = wilson(k, n)
    return {"n": n, "correct": k, "acc": k / n if n else None, "ci_lo": lo, "ci_hi": hi}


# ---------------------------------------------------------------- load and select
def load() -> tuple[list[dict], dict]:
    rows, taskmeta = [], {}
    for r in sorted(RESULTS.glob("2026*")):
        f = r / "results.jsonl"
        if not f.exists() or r.name.startswith("CONTAMINATED"):
            continue
        ts = json.loads((r / "tasks.json").read_text()) if (r / "tasks.json").exists() else []
        if not ts:
            continue
        ds = DATASETS.get(Path(ts[0]["pkg"]).parent.name, "unknown")
        for t in ts:
            taskmeta[(ds, t["id"])] = t
        for line in f.read_text().splitlines():
            if line.strip():
                x = json.loads(line); x["dataset"] = ds; x["_run"] = r.name
                x["model"] = x["model"].replace("ollama/", "").replace(":675b:cloud", ":675b-cloud")
                if x["condition"] in ("misled_oip", "misled_oip_strong") and "usage" not in x:
                    x["condition"] = {"misled_oip_strong": "misled_oip", "misled_oip": "misled_oip_v01"}[x["condition"]]
                rows.append(x)
    latest = {}
    for x in rows:
        key = (x["dataset"], x["model"], x["condition"]); latest[key] = max(latest.get(key, ""), x["_run"])
    rows = [x for x in rows if x["_run"] == latest[(x["dataset"], x["model"], x["condition"])]]
    rows = [x for x in rows if not (x["dataset"] == "paper-nih-50" and x["type"] == "scale_available")]
    return rows, taskmeta


def index(rows: list[dict]) -> tuple[dict, dict, dict]:
    """(dataset, model, condition) -> {task id: last non-error row}; error counts; repeat counts."""
    idx = collections.defaultdict(dict); errors = collections.Counter(); repeats = collections.Counter()
    for x in rows:
        key = (x["dataset"], x["model"], x["condition"])
        if x.get("error"):
            errors[key] += 1; continue
        if x["task"] in idx[key]:
            repeats[key] += 1
        idx[key][x["task"]] = x
    return idx, errors, repeats


def correct(x: dict) -> bool:
    return bool((x.get("score") or {}).get("correct"))


def is_gating(x: dict, nm: bool = False) -> bool:
    return bool(x.get("gating")) and x["type"] in (NM_GATING if nm else COMMON_GATING)


def paired(idx, ds, m, a, b, pred) -> dict:
    """Paired contrast of condition b against baseline a on items satisfying pred, present (non-error) in both."""
    A, B = idx.get((ds, m, a), {}), idx.get((ds, m, b), {})
    ids = [i for i in A if i in B and pred(A[i])]
    bb = sum(1 for i in ids if correct(A[i]) and not correct(B[i]))      # correct only in the baseline
    cc = sum(1 for i in ids if not correct(A[i]) and correct(B[i]))      # correct only in the new condition
    ka, kb = sum(correct(A[i]) for i in ids), sum(correct(B[i]) for i in ids)
    n = len(ids)
    return {"n_pairs": n, "acc_a": ka / n if n else None, "acc_b": kb / n if n else None, "delta_pp": 100 * (kb - ka) / n if n else None,
            "b": bb, "c": cc, "p": mcnemar_exact(bb, cc), "g": (cc / (bb + cc) - 0.5) if bb + cc else 0.0}


def with_holm(contrasts: dict) -> None:
    ps = [v["p"] for v in contrasts.values()]; adj = holm(ps)
    for (k, v), a in zip(contrasts.items(), adj):
        v["p_holm"] = a


def acc_cell(idx, ds, m, c, pred) -> dict:
    sel = [x for x in idx.get((ds, m, c), {}).values() if pred(x)]
    return cell(sum(correct(x) for x in sel), len(sel))


def mean_f1(idx, ds, m, c, t) -> tuple[float | None, int]:
    sel = [x for x in idx.get((ds, m, c), {}).values() if x["type"] == t]
    return (sum((x.get("score") or {}).get("f1", 0.0) for x in sel) / len(sel) if sel else None, len(sel))


# ---------------------------------------------------------------- main
def main() -> None:
    rows, taskmeta = load(); idx, errors, repeats = index(rows)
    models = sorted({x["model"] for x in rows if x["dataset"] in ("paper-vindr-100", "paper-nih-50")})
    R: dict = {"generated": time.strftime("%Y-%m-%d %H:%M"), "alpha": ALPHA, "models": {m: {"family": FAMILY.get(m, "ollama-cloud"), "id": MODEL_ID.get(m, m)} for m in models}}
    R["selected_rows"] = len(rows)
    R["errors"] = {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in sorted(errors.items())}
    R["repeats"] = {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in sorted(repeats.items())}

    # 1. gating accuracy per dataset, model, condition + paired contrasts
    R["gating"], R["contrasts"] = {}, {}
    for ds in ("paper-vindr-100", "paper-nih-50"):
        R["gating"][ds] = {m: {c: acc_cell(idx, ds, m, c, is_gating) for c in CONDS} for m in models}
        R["contrasts"][ds] = {}
        for name, (a, b) in {"ctx_vs_raw": ("raw", "ctx"), "ctx_l1_vs_raw": ("raw", "ctx_l1"), "ctx_vs_ctx_l1": ("ctx_l1", "ctx"), "annot_vs_ctx": ("ctx", "annot")}.items():
            con = {m: paired(idx, ds, m, a, b, is_gating) for m in models}; with_holm(con); R["contrasts"][ds][name] = con
    # 2. per task per condition per dataset
    R["per_task"] = {}
    for ds in ("paper-vindr-100", "paper-nih-50"):
        R["per_task"][ds] = {m: {t: {c: acc_cell(idx, ds, m, c, lambda x, t=t: x["type"] == t) for c in CONDS} for t in ("modality", "view") + COMMON_GATING} for m in models}
    # 3. render tasks and flip consistency
    R["render"], R["flip"] = {}, {}
    for ds in ("paper-vindr-100", "paper-nih-50"):
        R["render"][ds] = {}
        for m in models:
            mh = acc_cell(idx, ds, m, "annot", lambda x: x["type"] == "mark_heart"); ms = acc_cell(idx, ds, m, "annot", lambda x: x["type"] == "mark_side")
            ms["p_vs_chance"] = binom_vs_chance(ms["correct"], ms["n"]); R["render"][ds][m] = {"mark_heart": mh, "mark_side": ms}
        R["flip"][ds] = {}
        for c in ("ctx_l1", "ctx"):
            fl = {}
            for m in models:
                sel = [x for x in idx.get((ds, m, c), {}).values() if x["type"] == "flip_check"]
                ce = cell(sum(correct(x) for x in sel), len(sel)); ce["p_vs_chance"] = binom_vs_chance(ce["correct"], ce["n"])
                by_pkg = collections.defaultdict(list)
                for x in sel:
                    by_pkg[x["task"].split(":")[0]].append(correct(x))
                ce["images_both_correct"] = sum(1 for v in by_pkg.values() if len(v) == 2 and all(v)); ce["images"] = len(by_pkg)
                fl[m] = ce
            ps = holm([v["p_vs_chance"] for v in fl.values()])
            for (m, v), a in zip(fl.items(), ps):
                v["p_holm"] = a
            R["flip"][ds][c] = fl
    # 4. misleading label (paper-vindr-100) and findings F1
    ds = "paper-vindr-100"; R["misled"] = {}
    for m in models:
        P, O = idx.get((ds, m, "misled_plain"), {}), idx.get((ds, m, "misled_oip"), {})
        ids = [i for i in P if i in O and P[i]["type"] == "findings_misled"]
        ad = lambda x: bool((x.get("score") or {}).get("adopted_misleading"))
        kp, ko = sum(ad(P[i]) for i in ids), sum(ad(O[i]) for i in ids)
        b = sum(1 for i in ids if ad(P[i]) and not ad(O[i])); c = sum(1 for i in ids if not ad(P[i]) and ad(O[i]))
        R["misled"][m] = {"n_pairs": len(ids), "adopt_plain": cell(kp, len(ids)), "adopt_oip": cell(ko, len(ids)), "b_plain_only": b, "c_oip_only": c,
                          "p": mcnemar_exact(b, c), "f1_plain": mean_f1(idx, ds, m, "misled_plain", "findings_misled")[0], "f1_oip": mean_f1(idx, ds, m, "misled_oip", "findings_misled")[0]}
    with_holm(R["misled"])
    R["findings_f1"] = {m: {c: mean_f1(idx, ds, m, c, "findings")[0] for c in CONDS} for m in models}
    # 5. abstentions and empty replies
    R["abstentions"] = {}
    for (d, m, c), rs in sorted(idx.items()):
        ab = sum(1 for x in rs.values() if (x.get("score") or {}).get("abstained")); em = sum(1 for x in rs.values() if not (x.get("reply") or "").strip())
        if ab or em:
            R["abstentions"][f"{d}|{m}|{c}"] = {"abstained": ab, "empty": em, "gating_abstained": sum(1 for x in rs.values() if (x.get("score") or {}).get("abstained") and is_gating(x))}
    # 6. cross-model spread with bootstrap CI over task items
    R["spread"] = {}
    rng = random.Random(0)
    for ds in ("paper-vindr-100", "paper-nih-50"):
        R["spread"][ds] = {}
        for c in CONDS:
            per_model = {m: {i: correct(x) for i, x in idx.get((ds, m, c), {}).items() if is_gating(x)} for m in models}
            common = sorted(set.intersection(*[set(v) for v in per_model.values()]))
            accs = [sum(per_model[m][i] for i in common) / len(common) for m in models]
            sd = statistics.pstdev(accs); boots = []
            for _ in range(2000):
                smp = [common[rng.randrange(len(common))] for _ in common]
                boots.append(statistics.pstdev([sum(per_model[m][i] for i in smp) / len(smp) for m in models]))
            boots.sort(); R["spread"][ds][c] = {"sd_pp": 100 * sd, "ci_lo_pp": 100 * boots[49], "ci_hi_pp": 100 * boots[1949], "items": len(common), "models": len(models)}
    # 7. cost: tokens, latency, list price per call over the two radiograph paper sets (the bone scans have much smaller images and a
    # different task mix, so pooling them lowered the means; this matches the RA study's definition)
    R["cost"] = {}
    for m in models:
        R["cost"][m] = {}
        for c in CONDS:
            sel = [x for d in ("paper-vindr-100", "paper-nih-50") for x in idx.get((d, m, c), {}).values() if (x.get("usage") or {}).get("input_tokens")]
            if not sel:
                continue
            tot_in = [x["usage"]["input_tokens"] + (x["usage"].get("cache_read_input_tokens") or 0) + (x["usage"].get("cache_creation_input_tokens") or 0) for x in sel]
            out = [x["usage"].get("output_tokens") or 0 for x in sel]; lat = [x["usage"]["latency_s"] for x in sel if x["usage"].get("latency_s")]
            e = {"calls": len(sel), "input_tokens_mean": statistics.mean(tot_in), "output_tokens_mean": statistics.mean(out), "latency_mean_s": statistics.mean(lat) if lat else None, "latency_median_s": statistics.median(lat) if lat else None}
            if m in PRICES:
                pi, po = PRICES[m]
                usd = [(x["usage"]["input_tokens"] * pi + (x["usage"].get("cache_read_input_tokens") or 0) * pi * 0.1 + (x["usage"].get("cache_creation_input_tokens") or 0) * pi * 1.25 + (x["usage"].get("output_tokens") or 0) * po) / 1e6 for x in sel]
                e["usd_per_call_mean"] = statistics.mean(usd)
            R["cost"][m][c] = e
    R["cost_totals_usd"] = {}
    for m in PRICES:
        pi, po = PRICES[m]; tot = 0.0; n = 0
        for (d, mm, c), rs in idx.items():
            if mm != m or d == "pilot-vindr-20":
                continue
            for x in rs.values():
                u = x.get("usage") or {}; n += 1
                tot += (u.get("input_tokens", 0) * pi + (u.get("cache_read_input_tokens") or 0) * pi * 0.1 + (u.get("cache_creation_input_tokens") or 0) * pi * 1.25 + (u.get("output_tokens") or 0) * po) / 1e6
        R["cost_totals_usd"][m] = {"usd": tot, "calls": n}
    # 8. bone scans
    ds = "bonescan-40"; R["nm"] = {"per_task": {}, "left_edge_by_view": {}, "gating_contrasts": {}}
    nm_models = sorted({x["model"] for x in rows if x["dataset"] == ds})
    # the hotter-side question was asked on 22 images in the early local-model run and on 8 after the asymmetry threshold was raised;
    # all models are compared on the items every model received (RA protocol amendment 6)
    hot_sets = [{x["task"] for x in idx.get((ds, m, "raw"), {}).values() if x["type"] == "hot_side"} for m in nm_models]
    common_hot = set.intersection(*hot_sets) if hot_sets else set()
    R["nm"]["hot_side_items_common"] = len(common_hot)
    nm_item = lambda x: x["type"] != "hot_side" or x["task"] in common_hot
    for m in nm_models:
        R["nm"]["per_task"][m] = {}
        for t in NM_TYPES:
            cs = ("ctx_l1", "ctx") if t == "flip_check_nm" else ("raw", "ctx_l1", "ctx")
            R["nm"]["per_task"][m][t] = {}
            for c in cs:
                ce = acc_cell(idx, ds, m, c, lambda x, t=t: x["type"] == t and nm_item(x))
                if t in ("hot_side", "flip_check_nm"):
                    ce["p_vs_chance"] = binom_vs_chance(ce["correct"], ce["n"])
                R["nm"]["per_task"][m][t][c] = ce
        R["nm"]["left_edge_by_view"][m] = {}
        for view in ("anterior", "posterior"):
            R["nm"]["left_edge_by_view"][m][view] = {c: acc_cell(idx, ds, m, c, lambda x, view=view: x["type"] == "left_edge_nm" and view in taskmeta[(ds, x["task"])]["question"]) for c in ("raw", "ctx_l1", "ctx")}
    for name, (a, b) in {"ctx_vs_raw": ("raw", "ctx"), "ctx_l1_vs_raw": ("raw", "ctx_l1")}.items():
        con = {m: paired(idx, ds, m, a, b, lambda x: is_gating(x, nm=True) and nm_item(x)) for m in nm_models}; with_holm(con); R["nm"]["gating_contrasts"][name] = con
    R["nm"]["gating"] = {m: {c: acc_cell(idx, ds, m, c, lambda x: is_gating(x, nm=True) and nm_item(x)) for c in ("raw", "ctx_l1", "ctx")} for m in nm_models}
    # 9. pilot-20: OEP-001 wording ablation (descriptive)
    ds = "pilot-vindr-20"; R["pilot_oep001"] = {}
    for m in sorted({x["model"] for x in rows if x["dataset"] == ds}):
        e = {}
        for c in ("misled_plain", "misled_oip_v01", "misled_oip"):
            sel = [x for x in idx.get((ds, m, c), {}).values() if x["type"] == "findings_misled"]
            if sel:
                e[c] = cell(sum(1 for x in sel if (x.get("score") or {}).get("adopted_misleading")), len(sel))
        if e:
            R["pilot_oep001"][m] = e
    # 10. CXAS vs PSPNet cross-check (20 pilot images)
    import os
    cx = Path(os.environ.get("OIP_BENCH_DIR", Path.home() / "oip-bench")) / "cxas_vs_pspnet_20.json"
    if cx.exists():
        d = json.loads(cx.read_text())
        def agree(key_a, key_b, tol, relative):
            pairs = [(x[key_a], x[key_b]) for x in d if x.get(key_a) and x.get(key_b)]
            diff = [b - a for a, b in pairs]; mu = statistics.mean(diff); sd = statistics.pstdev(diff)
            within = sum(1 for a, b in pairs if (abs(b - a) / a if relative else abs(b - a)) <= tol)
            return {"n": len(pairs), "mean_a": statistics.mean(a for a, _ in pairs), "mean_b": statistics.mean(b for _, b in pairs), "mean_diff": mu, "sd_diff": sd, "loa_lo": mu - 1.96 * sd, "loa_hi": mu + 1.96 * sd, "within_tol": within}
        R["cxas"] = {"heart_width_mm": agree("heart_pspnet_mm", "heart_cxas_mm", 0.10, True), "thoracic_width_mm_lung_union_vs_cxas_itw": agree("lung_union_mm", "itw_mm", 0.10, True), "ctr": agree("ctr_pspnet", "ctr_cxas", 0.05, False)}
    OUT_JSON.write_text(json.dumps(R, indent=1))
    OUT_MD.write_text(render(R)); print(render(R))


# ---------------------------------------------------------------- reference sheet
def pct(c: dict, ci: bool = True) -> str:
    if not c or c.get("n", 0) == 0 or c.get("acc") is None:
        return "–"
    s = f"{100*c['acc']:.0f} %"
    return s + (f" ({100*c['ci_lo']:.0f}–{100*c['ci_hi']:.0f}; n={c['n']})" if ci else "")


def pfmt(p: float) -> str:
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def render(R: dict) -> str:
    L = [f"# Paper reference sheet — OIP-Bench (auto-generated by bench/paper_stats.py, {R['generated']})", "",
         "Single source of truth for every number in docs/paper/manuscript-draft.md. Cells: accuracy (Wilson 95 % CI; n). Contrasts: exact McNemar on paired items, Holm over the 11 models within dataset and contrast; g = Cohen's g (positive = new condition better). Selection rules as in bench/report.py. Abstentions and empty replies are scored incorrect.", "",
         f"Selected rows: {R['selected_rows']}. Error rows excluded (dataset|model|condition: n): " + (", ".join(f"{k}: {v}" for k, v in R['errors'].items()) or "none") + ".",
         "Repeated replies (last kept): " + (", ".join(f"{k}: {v}" for k, v in R['repeats'].items()) or "none") + ".", ""]
    L += ["## Entity registry", "", "| key | model id | family |", "|---|---|---|"] + [f"| {m} | {v['id']} | {v['family']} |" for m, v in R["models"].items()] + [""]
    for ds in ("paper-vindr-100", "paper-nih-50"):
        L += [f"## Gating accuracy — {ds} (left_edge, scale_available, ctr ±0.05, heart_mm ±10 %{'; scale_available excluded' if ds == 'paper-nih-50' else ''})", "",
              "| model | raw | L0–L2 file | full file | annotated | full − raw (pp) | b / c | p (Holm) | g |", "|---|---|---|---|---|---|---|---|---|"]
        for m, g in R["gating"][ds].items():
            k = R["contrasts"][ds]["ctx_vs_raw"][m]
            L.append(f"| {m} | {pct(g['raw'])} | {pct(g['ctx_l1'])} | {pct(g['ctx'])} | {pct(g['annot'])} | {k['delta_pp']:+.0f} | {k['b']} / {k['c']} | {pfmt(k['p_holm'])} | {k['g']:+.2f} |")
        L += ["", f"### Layer ablation and annotated render — {ds}", "", "| model | L0–L2 vs raw: Δpp, b/c, p(Holm) | full vs L0–L2: Δpp, b/c, p(Holm) | annotated vs full: Δpp, b/c, p(Holm) |", "|---|---|---|---|"]
        for m in R["gating"][ds]:
            cs = [R["contrasts"][ds][k][m] for k in ("ctx_l1_vs_raw", "ctx_vs_ctx_l1", "annot_vs_ctx")]
            L.append(f"| {m} | " + " | ".join(f"{k['delta_pp']:+.0f}, {k['b']}/{k['c']}, {pfmt(k['p_holm'])}" for k in cs) + " |")
        L += ["", f"### Per task — {ds} (raw → L0–L2 → full → annotated; n per cell in brackets for raw)", "", "| model | modality | view | left edge | scale available | CTR | heart mm |", "|---|---|---|---|---|---|---|"]
        for m, tt in R["per_task"][ds].items():
            L.append(f"| {m} | " + " | ".join(" → ".join(pct(tt[t][c], ci=False) for c in CONDS) + f" (n={tt[t]['raw']['n']})" for t in ("modality", "view") + COMMON_GATING) + " |")
        L += ["", f"### Render and consistency tasks — {ds}", "", "| model | heart mark (annot) | mark side (annot) | mark side p vs 50 % | flip check L0–L2 | p (Holm) | flip check full | p (Holm) | images both flip items correct (full) |", "|---|---|---|---|---|---|---|---|---|"]
        for m in R["gating"][ds]:
            r = R["render"][ds][m]; f1, f2 = R["flip"][ds]["ctx_l1"][m], R["flip"][ds]["ctx"][m]
            L.append(f"| {m} | {pct(r['mark_heart'])} | {pct(r['mark_side'])} | {pfmt(r['mark_side']['p_vs_chance'])} | {pct(f1)} | {pfmt(f1['p_holm'])} | {pct(f2)} | {pfmt(f2['p_holm'])} | {f2['images_both_correct']}/{f2['images']} |")
        L += ["", f"### Cross-model spread — {ds} (population SD of the 11 model accuracies, bootstrap 95 % CI over task items)", "",
              "| condition | SD (pp) | 95 % CI | items |", "|---|---|---|---|"] + [f"| {c} | {v['sd_pp']:.1f} | {v['ci_lo_pp']:.1f}–{v['ci_hi_pp']:.1f} | {v['items']} |" for c, v in R["spread"][ds].items()] + [""]
    L += ["## Misleading label — paper-vindr-100 (adoption of the injected wrong label; paired by image)", "",
          "| model | plain note | shipped template | plain-only / template-only | p (Holm) | F1 plain | F1 template |", "|---|---|---|---|---|---|---|"]
    for m, v in R["misled"].items():
        L.append(f"| {m} | {pct(v['adopt_plain'])} | {pct(v['adopt_oip'])} | {v['b_plain_only']} / {v['c_oip_only']} | {pfmt(v['p_holm'])} | {100*v['f1_plain']:.0f} % | {100*v['f1_oip']:.0f} % |")
    L += ["", "## Findings F1 — paper-vindr-100 (reported, not gating)", "", "| model | raw | L0–L2 | full | annotated |", "|---|---|---|---|---|"]
    for m, v in R["findings_f1"].items():
        L.append(f"| {m} | " + " | ".join("–" if v[c] is None else f"{100*v[c]:.0f} %" for c in CONDS) + " |")
    L += ["", "## Abstentions and empty replies (dataset|model|condition: abstained / of which gating / empty)", ""] + [f"- {k}: {v['abstained']} / {v['gating_abstained']} / {v['empty']}" for k, v in R["abstentions"].items()]
    L += ["", "## Cost per call (paper sets pooled; input tokens include cache reads and writes for claude)", "", "| model | condition | calls | input tokens | output tokens | latency mean / median (s) | US$ per call |", "|---|---|---|---|---|---|---|"]
    for m, cc in R["cost"].items():
        for c, e in cc.items():
            L.append(f"| {m} | {c} | {e['calls']} | {e['input_tokens_mean']:.0f} | {e['output_tokens_mean']:.0f} | {e['latency_mean_s']:.1f} / {e['latency_median_s']:.1f} | {('%.4f' % e['usd_per_call_mean']) if 'usd_per_call_mean' in e else '–'} |")
    L += ["", "Frontier list-price totals over the three paper sets: " + ", ".join(f"{m}: US$ {v['usd']:.2f} ({v['calls']} calls)" for m, v in R["cost_totals_usd"].items()), ""]
    L += ["## Bone scans — bonescan-40 (raw → L0–L2 → full)", "", "| model | modality | left edge (all) | left edge anterior | left edge posterior | scale available | counts comparable | hotter side (n=8) | p vs 50 % (full) | flip check (L0–L2 → full) | p vs 50 % (full) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, tt in R["nm"]["per_task"].items():
        lv = R["nm"]["left_edge_by_view"][m]
        row = [" → ".join(pct(tt[t][c], ci=False) for c in ("raw", "ctx_l1", "ctx")) for t in ("modality_nm", "left_edge_nm")]
        row += [" → ".join(pct(lv[v][c], ci=False) for c in ("raw", "ctx_l1", "ctx")) for v in ("anterior", "posterior")]
        row += [" → ".join(pct(tt[t][c], ci=False) for c in ("raw", "ctx_l1", "ctx")) for t in ("scale_available_nm", "counts_semantics", "hot_side")]
        row += [pfmt(tt["hot_side"]["ctx"]["p_vs_chance"]), " → ".join(pct(tt["flip_check_nm"][c], ci=False) for c in ("ctx_l1", "ctx")), pfmt(tt["flip_check_nm"]["ctx"]["p_vs_chance"])]
        L.append(f"| {m} | " + " | ".join(row) + " |")
    L += ["", "### Bone-scan gating aggregate (left_edge_nm, scale_available_nm, hot_side) and contrasts", "", "| model | raw | L0–L2 | full | full − raw (pp) | b / c | p (Holm) |", "|---|---|---|---|---|---|---|"]
    for m, g in R["nm"]["gating"].items():
        k = R["nm"]["gating_contrasts"]["ctx_vs_raw"][m]
        L.append(f"| {m} | {pct(g['raw'])} | {pct(g['ctx_l1'])} | {pct(g['ctx'])} | {k['delta_pp']:+.0f} | {k['b']} / {k['c']} | {pfmt(k['p_holm'])} |")
    L += ["", "## Pilot-vindr-20 — OEP-001 wording ablation (descriptive; adoption of the wrong label)", "", "| model | plain note | v0.1 External section | OEP-001 wording (shipped) |", "|---|---|---|---|"]
    for m, e in R["pilot_oep001"].items():
        L.append(f"| {m} | {pct(e.get('misled_plain'))} | {pct(e.get('misled_oip_v01'))} | {pct(e.get('misled_oip'))} |")
    if "cxas" in R:
        L += ["", "## CXAS vs PSPNet cross-check (20 pilot images; difference = CXAS − PSPNet)", "", "| quantity | n | mean PSPNet | mean CXAS | mean diff | SD | 95 % LoA | within benchmark tolerance |", "|---|---|---|---|---|---|---|---|"]
        for k, v in R["cxas"].items():
            L.append(f"| {k} | {v['n']} | {v['mean_a']:.3f} | {v['mean_b']:.3f} | {v['mean_diff']:+.3f} | {v['sd_diff']:.3f} | {v['loa_lo']:+.3f} to {v['loa_hi']:+.3f} | {v['within_tol']}/{v['n']} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
