"""Evaluate `oip check` (pixel-side orientation check) on a package set, normal and mirrored, WITHOUT writing into the packages.

For every package: (a) the check on the stored masks; (b) the check on horizontally mirrored masks (pure geometry);
(c) the check on the mirrored canonical render, re-segmented by the anatomy model (the realistic case: a mirrored image
arriving at the converter). A correct check says 'consistent' for (a) and 'inconsistent' for (b) and (c).

Usage: python scripts/check_mirror_eval.py <pkg_dir> [limit] -> docs/reports/orientation-pixel-check.md (+ .json)
"""
from __future__ import annotations
import collections, json, statistics, sys, time
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from oip.check import orientation_evidence, check_image, MIN_OFFSET, STRONG_OFFSET, TOOL_VERSION  # noqa: E402

pkg_dir = Path(sys.argv[1]); limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9
pkgs = sorted(p for p in pkg_dir.glob("*.oip") if (p / "oip.json").exists())[:limit]
rows = []; t0 = time.time()
for p in pkgs:
    m = json.loads((p / "oip.json").read_text()); el = m["geometry"]["orientation"]["edge_labels"]; W = m["geometry"]["columns"]
    masks = {}
    for rid in ("heart", "aorta", "lung_left", "lung_right"):
        f = p / f"derived/masks/{rid}.png"
        masks[rid] = (np.asarray(Image.open(f).convert("L")) > 127) if f.exists() else None
    a = orientation_evidence(masks, W, el)
    b = orientation_evidence({k: (v[:, ::-1] if v is not None else None) for k, v in masks.items()}, W, el)
    canon = np.asarray(Image.open(p / "renders/canonical.png").convert("L"))
    c = check_image(canon[:, ::-1].copy(), el)
    off = lambda r: ((r.get("evidence") or {}).get("structures") or {}).get("heart", {}).get("centroid_offset_frac")
    rows.append({"pkg": p.name, "normal": a["result"], "mirrored_masks": b["result"], "mirrored_resegmented": c["result"],
                 "offset_normal": off(a), "offset_mirrored_resegmented": off(c), "reason_normal": a.get("reason"), "reason_mirrored": c.get("reason")})
    print(f"{p.name[:12]} normal={a['result']:13s} mirrored(masks)={b['result']:13s} mirrored(reseg)={c['result']:13s} off={off(a)} / {off(c)}", flush=True)

def dist(key): return dict(collections.Counter(r[key] for r in rows))
offs = [r["offset_normal"] for r in rows if r["offset_normal"] is not None]
offs_m = [r["offset_mirrored_resegmented"] for r in rows if r["offset_mirrored_resegmented"] is not None]
summary = {"n": len(rows), "tool_version": TOOL_VERSION, "min_offset": MIN_OFFSET, "strong_offset": STRONG_OFFSET,
           "normal": dist("normal"), "mirrored_masks": dist("mirrored_masks"), "mirrored_resegmented": dist("mirrored_resegmented"),
           "heart_offset_normal": {"min": min(offs), "median": statistics.median(offs), "max": max(offs)} if offs else None,
           "heart_offset_mirrored_resegmented": {"min": min(offs_m), "median": statistics.median(offs_m), "max": max(offs_m)} if offs_m else None,
           "seconds": round(time.time() - t0, 1), "generated": time.strftime("%Y-%m-%d %H:%M")}
out = ROOT / "docs/reports/orientation-pixel-check"
out.with_suffix(".json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1))
md = [f"# Pixel-side orientation check (`oip check` {TOOL_VERSION}) on {pkg_dir.name}, n = {len(rows)}", "",
      f"Generated {summary['generated']} by scripts/check_mirror_eval.py; packages not modified. The check compares the column centroid of the unsided heart (and aortic-arch) mask with the thoracic midline (lung-union bbox centre) and the edge labelled L; |offset| < {MIN_OFFSET:.0%} of thoracic width is indeterminate, ≥ {STRONG_OFFSET:.0%} is confident. It does not use the segmentation model's left/right class labels.", "",
      "| condition | consistent | inconsistent | indeterminate |", "|---|---|---|---|"]
for k, lab in (("normal", "stored masks, image as shipped"), ("mirrored_masks", "masks mirrored (geometry only)"), ("mirrored_resegmented", "canonical render mirrored, re-segmented")):
    d = summary[k]; md.append(f"| {lab} | {d.get('consistent', 0)} | {d.get('inconsistent', 0)} | {d.get('indeterminate', 0)} |")
if offs:
    md += ["", f"Heart centroid offset toward the L edge, as shipped: min {min(offs):+.3f}, median {statistics.median(offs):+.3f}, max {max(offs):+.3f} of thoracic width (positive = toward L).",
           f"After mirroring and re-segmenting: min {min(offs_m):+.3f}, median {statistics.median(offs_m):+.3f}, max {max(offs_m):+.3f}." if offs_m else ""]
wrong = [r for r in rows if r["normal"] == "inconsistent" or r["mirrored_resegmented"] == "consistent"]
md += ["", f"Packages where the single-pass check points the wrong way: {len(wrong)}" + (": " + ", ".join(r["pkg"][:12] for r in wrong) if wrong else "."),
       f"Indeterminate as shipped: {[r['pkg'][:12] for r in rows if r['normal'] == 'indeterminate']}", "",
       "Reading: a correct check reads consistent on the shipped image and inconsistent on the mirrored copy. The single pass under-reads the flip because the segmentation model has a positional prior: on a mirrored image the heart mask is pulled back toward the conventional side.", ""]
# two-pass, prior-free statistic (oip.check.combine_two_pass): s = (offset on the image − offset on its mirror) / 2; the prior p = their mean.
# Pass 1 here = the stored masks (model on the shipped image), pass 2 = the model on the mirrored render, so s is available per package.
# A mirrored input gives exactly −s (the two passes swap), so the counts below hold for both orientations.
pairs = [(r["offset_normal"], r["offset_mirrored_resegmented"], r["pkg"]) for r in rows if r["offset_normal"] is not None and r["offset_mirrored_resegmented"] is not None]
if pairs:
    from oip.check import combine_two_pass
    two = [(combine_two_pass(a, b), pk) for a, b, pk in pairs]
    dd = collections.Counter(c["result"] for c, _ in two); ss = [c["prior_free_offset_frac"] for c, _ in two]; pp = [c["model_prior_frac"] for c, _ in two]
    summary["two_pass"] = {"n": len(two), "consistent": dd.get("consistent", 0), "inconsistent": dd.get("inconsistent", 0), "indeterminate": dd.get("indeterminate", 0),
                           "s_min": min(ss), "s_median": statistics.median(ss), "s_max": max(ss), "prior_min": min(pp), "prior_median": statistics.median(pp), "prior_max": max(pp),
                           "weakest": [pk[:12] for c, pk in sorted(two, key=lambda t: t[0]["prior_free_offset_frac"])[:5]]}
    md += [f"## Two-pass, prior-free check (default of `oip check` {TOOL_VERSION})", "",
           f"s = (offset on the image − offset on its mirror) / 2 cancels the model's prior p = their mean. On the shipped images: s min {min(ss):+.4f}, median {statistics.median(ss):+.4f}, max {max(ss):+.4f}; p min {min(pp):+.4f}, median {statistics.median(pp):+.4f}, max {max(pp):+.4f}.",
           "", "| verdict on the shipped image (mirrored input: the same counts with consistent and inconsistent swapped) | n |", "|---|---|",
           f"| consistent (correct) | {dd.get('consistent', 0)} |", f"| inconsistent (wrong) | {dd.get('inconsistent', 0)} |", f"| indeterminate (|s| < {MIN_OFFSET:.0%}) | {dd.get('indeterminate', 0)} |", "",
           f"Weakest five (smallest s): {', '.join(summary['two_pass']['weakest'])}.", ""]
    out.with_suffix(".json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1))
out.with_suffix(".md").write_text("\n".join(md)); print("\n".join(md))
