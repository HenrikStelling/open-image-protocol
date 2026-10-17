"""Write a CheXmask cross-check record into the measurements of a package store (PLAN Phase 3b, CTR truth Tier 2; owner's
decision 2026-10-17). The record goes next to `validation_status`, which becomes `cross_checked`; `validated` is reserved for a
reference or expert measurement, which an automatic second segmentation is not.

Usage: python scripts/apply_crosscheck.py --store ~/oip-bench/vindr-paper --per-image bench/results/_chexmask/vindr-paper.json \
           --report docs/reports/chexmask-vindr-2026-10-17.md [--backup ~/oip-bench/_backup] [--dry-run]

Aggregates (n, Lin's CCC, bias, limits of agreement, share within 10 %) are computed from the per-image file that
bench/chexmask_validate.py wrote, per metric: ctr ↔ ctr, heart_width ↔ heart px, thorax_width ↔ thorax px (relative figures, so
they hold for the millimetre values too). Every package is re-validated against the schema, its context.md is re-rendered with
the current template, and the manifest's context entry records the template version."""
from __future__ import annotations
import argparse, json, shutil, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "bench"))
from oip.validate import validate_package          # noqa: E402
from oip.context import build_context, TEMPLATE_VERSION   # noqa: E402
from chexmask_validate import agreement            # noqa: E402

SOURCE = {"source": "CheXmask", "source_version": "1.0.0", "doi": "10.13026/3705-zg36", "method": "HybridGNet masks at original resolution; same width definition (max horizontal extent, thorax = union of both lung masks)"}
METRICS = {"ctr": ("ctr_ours", "ctr_theirs", 3), "heart_width": ("heart_px_ours", "heart_px_theirs", 1), "thorax_width": ("thorax_px_ours", "thorax_px_theirs", 1)}


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--store", required=True); ap.add_argument("--per-image", required=True); ap.add_argument("--report", required=True)
    ap.add_argument("--backup", default=str(Path.home() / "oip-bench/_backup")); ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    store = Path(a.store).expanduser(); per = json.loads(Path(a.per_image).read_text()); by_id = {r["id"]: r for r in per}
    agg = {}
    for mid, (ko, kt, dec) in METRICS.items():
        pairs = [(r[ko], r[kt]) for r in per if r.get(ko) and r.get(kt)]
        s = agreement(pairs)
        agg[mid] = {"n": s["n"], "ccc": round(s["ccc"], 3), "bias": round(s["bias"], dec), "unit": "1" if mid == "ctr" else "px", "bias_rel_pct": round(s["rel_bias_pct"], 1),
                    "loa": [round(s["loa"][0], dec), round(s["loa"][1], dec)], "within_10pct": round(s["within_tol"] / s["n"], 2)}
    print("aggregates:", json.dumps(agg))
    changed = 0; skipped = []
    for p in sorted(store.glob("*.oip")):
        if not (p / "oip.json").exists(): continue
        m = json.loads((p / "oip.json").read_text()); sid = Path(m["provenance"].get("source_filename") or p.name).stem
        r = by_id.get(sid)
        if not r: skipped.append(p.name); continue
        for x in m["derived"]["measurements"]:
            if x["id"] not in METRICS: continue
            ko, kt, dec = METRICS[x["id"]]
            x["validation_status"] = "cross_checked"
            x["cross_check"] = dict(SOURCE, date=time.strftime("%Y-%m-%d"), report=str(Path(a.report).name), aggregate=agg[x["id"]],
                                    this_image={"source_value": round(r[kt], dec) if x["id"] == "ctr" else int(r[kt]), "unit": x["unit"] if x["id"] == "ctr" else "px",
                                                "dice_heart": round(r["dice_heart"], 3), "dice_lungs": round(r["dice_lungs"], 3), "source_quality_dice_rca_mean": round(r["dice_rca_mean"], 3)})
        m["context"] = {"path": "context.md", "template_version": TEMPLATE_VERSION}
        if a.dry_run:
            changed += 1; continue
        bdir = Path(a.backup).expanduser() / store.name / p.name; bdir.mkdir(parents=True, exist_ok=True)
        for f in ("oip.json", "context.md"):
            if (p / f).exists() and not (bdir / f).exists(): shutil.copy2(p / f, bdir / f)
        (p / "oip.json").write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n")
        (p / "context.md").write_text(build_context(m))
        errs = validate_package(p)
        if errs: sys.exit(f"{p.name}: validation failed after the change: {errs}")
        changed += 1
    print(f"{'would change' if a.dry_run else 'changed'} {changed} packages; no CheXmask row for {len(skipped)}: {skipped[:5]}")


if __name__ == "__main__":
    main()
