"""Tier-2 validation of the package measurements against CheXmask (PhysioNet, CC BY 4.0; HybridGNet masks with RCA quality
scores). PLAN Phase 3b "CTR truth (Tier 1 → Tier 2)".

Usage: python bench/chexmask_validate.py --dataset vindr --store ~/oip-bench/vindr-paper \
           --csv ~/oip-bench/chexmask/OriginalResolution/VinDr-CXR.csv --out docs/reports/chexmask-vindr-<date>.md

For every package whose source image has a CheXmask row: decode the heart / left-lung / right-lung masks (RLE, 1-based starts,
row-major, at the original image size), apply the SAME width definition the converter uses (max horizontal extent of the mask;
thorax = union of both lung masks; CTR = heart width / thorax width), and compare with the package's own PSPNet masks and
`derived/measurements.json`. Reports Dice overlap per structure, bias / limits of agreement and Lin's concordance for heart width,
thorax width and CTR, the share of images within 10 % relative difference, CTR > 0.5 prevalence from both sources, and the same
restricted to CheXmask rows with Dice RCA (Mean) >= 0.7 (the authors' recommended quality threshold). The package store is read
only; nothing is written into packages."""
from __future__ import annotations
import argparse, csv, json, math, statistics, sys, time
from pathlib import Path
import numpy as np
from PIL import Image

csv.field_size_limit(sys.maxsize)
ROOT = Path(__file__).resolve().parents[1]


def rle_to_mask(rle: str, height: int, width: int) -> np.ndarray:
    """CheXmask RLE: space-separated (start, length) pairs, starts 1-based over the row-major flattened mask."""
    runs = np.array([int(x) for x in rle.split()], dtype=np.int64)
    mask = np.zeros(height * width, dtype=bool)
    for start, length in zip(runs[::2], runs[1::2]):
        mask[start - 1:start - 1 + length] = True
    return mask.reshape((height, width))


def extent_px(mask: np.ndarray) -> int:
    cols = np.where(mask.any(axis=0))[0]
    return int(cols.max() - cols.min() + 1) if cols.size else 0


def dice(a: np.ndarray, b: np.ndarray) -> float:
    s = a.sum() + b.sum()
    return float(2 * np.logical_and(a, b).sum() / s) if s else float("nan")


def lin_ccc(x: list[float], y: list[float]) -> float:
    if len(x) < 3: return float("nan")
    mx, my = statistics.mean(x), statistics.mean(y); vx, vy = statistics.pvariance(x), statistics.pvariance(y)
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y)) / len(x)
    d = vx + vy + (mx - my) ** 2
    return 2 * cov / d if d else float("nan")


def pearson(x, y):
    if len(x) < 3: return float("nan")
    mx, my = statistics.mean(x), statistics.mean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else float("nan")


def agreement(pairs: list[tuple[float, float]], rel_tol: float = 0.10) -> dict:
    """pairs of (ours, theirs). Bias = ours − theirs; limits of agreement = bias ± 1.96 SD; relative bias as % of theirs."""
    if not pairs: return {"n": 0}
    o = [p[0] for p in pairs]; t = [p[1] for p in pairs]; d = [a - b for a, b in pairs]
    rel = [(a - b) / b for a, b in pairs if b]
    sd = statistics.pstdev(d) if len(d) > 1 else 0.0
    return {"n": len(pairs), "mean_ours": statistics.mean(o), "mean_theirs": statistics.mean(t), "bias": statistics.mean(d), "sd": sd,
            "loa": (statistics.mean(d) - 1.96 * sd, statistics.mean(d) + 1.96 * sd), "rel_bias_pct": 100 * statistics.mean(rel) if rel else float("nan"),
            "within_tol": sum(1 for r in rel if abs(r) <= rel_tol), "ccc": lin_ccc(o, t), "r": pearson(o, t)}


def fmt(a: dict, unit: str = "", dec: int = 1) -> str:
    if not a.get("n"): return "| – | – | – | – | – | – | – |"
    return (f"| {a['n']} | {a['mean_ours']:.{dec}f} / {a['mean_theirs']:.{dec}f}{unit} | {a['bias']:+.{dec}f}{unit} ({a['rel_bias_pct']:+.1f} %) | "
            f"{a['loa'][0]:+.{dec}f} … {a['loa'][1]:+.{dec}f}{unit} | {100 * a['within_tol'] / a['n']:.0f} % | {a['ccc']:.3f} | {a['r']:.3f} |")


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--dataset", required=True, choices=["vindr", "nih"]); ap.add_argument("--store", required=True)
    ap.add_argument("--csv", required=True); ap.add_argument("--out"); ap.add_argument("--min-dice", type=float, default=0.7); ap.add_argument("--per-image", help="JSON file for the per-image table")
    a = ap.parse_args(); store = Path(a.store).expanduser()
    pkgs = {}
    for p in sorted(store.glob("*.oip")):
        if not (p / "oip.json").exists(): continue
        m = json.loads((p / "oip.json").read_text()); sid = Path(m["provenance"].get("source_filename") or p.name).stem
        pkgs[sid] = (p, m)
    t0 = time.time(); found = {}
    with open(Path(a.csv).expanduser(), newline="") as f:
        for row in csv.DictReader(f):
            sid = Path(row.get("image_id") or row.get("Image Index") or row.get("Image ID") or "").stem   # VinDr: image_id; ChestX-Ray8: Image Index
            if sid in pkgs: found[sid] = row
            if len(found) == len(pkgs): break
    per = []
    for sid, row in found.items():
        p, m = pkgs[sid]; H, W = int(row["Height"]), int(row["Width"])
        ours = {k: np.asarray(Image.open(p / f"derived/masks/{k}.png").convert("L")) > 127 for k in ("heart", "lung_left", "lung_right") if (p / f"derived/masks/{k}.png").exists()}
        if len(ours) < 3: continue
        theirs = {"heart": rle_to_mask(row["Heart"], H, W), "lung_left": rle_to_mask(row["Left Lung"], H, W), "lung_right": rle_to_mask(row["Right Lung"], H, W)}
        if ours["heart"].shape != theirs["heart"].shape:   # CheXmask masks are restored to the original image size; ours are at the package's canonical size
            scale = ours["heart"].shape[1] / W
            theirs = {k: np.asarray(Image.fromarray(v.astype(np.uint8) * 255).resize(ours["heart"].shape[::-1], Image.Resampling.NEAREST)) > 127 for k, v in theirs.items()}
        else:
            scale = 1.0
        lo = ours["lung_left"] | ours["lung_right"]; lt = theirs["lung_left"] | theirs["lung_right"]
        meas = {x["id"]: x.get("value") for x in m["derived"]["measurements"]}
        rec = {"id": sid, "dice_rca_mean": float(row["Dice RCA (Mean)"]), "scale": scale, "rows": m["geometry"]["rows"], "cols": m["geometry"]["columns"],
               "dice_heart": dice(ours["heart"], theirs["heart"]), "dice_lungs": dice(lo, lt),
               "heart_px_ours": extent_px(ours["heart"]), "heart_px_theirs": extent_px(theirs["heart"]),
               "thorax_px_ours": extent_px(lo), "thorax_px_theirs": extent_px(lt), "ctr_pkg": meas.get("ctr")}
        rec["ctr_ours"] = rec["heart_px_ours"] / rec["thorax_px_ours"] if rec["thorax_px_ours"] else None
        rec["ctr_theirs"] = rec["heart_px_theirs"] / rec["thorax_px_theirs"] if rec["thorax_px_theirs"] else None
        per.append(rec)
    L = [f"# CheXmask validation — {a.dataset} ({store.name}), {time.strftime('%Y-%m-%d')}", "",
         f"Packages: {len(pkgs)}; CheXmask rows found: {len(found)}; compared (all three masks present): {len(per)}; CSV `{Path(a.csv).name}` (CheXmask 1.0.0, HybridGNet, "
         f"PhysioNet DOI 10.13026/3705-zg36). Definition on both sides: width = max horizontal extent of the mask, thorax = union of both lung masks, "
         f"CTR = heart / thorax (the converter's Tier-1 definition; CheXmask provides no rib-cage width, so the thoracic-width *definition* is not tested here, only the segmentation). "
         f"Bias = package − CheXmask; LoA = bias ± 1.96 SD; CCC = Lin's concordance. Scan {time.time() - t0:.0f} s.", ""]
    consistent = [r for r in per if r["ctr_pkg"] is not None and r["ctr_ours"] is not None and abs(r["ctr_pkg"] - r["ctr_ours"]) > 0.005]
    L.append(f"Consistency check: the CTR recomputed from the package masks differs from `measurements.json` by > 0.005 on {len(consistent)} of {len(per)} packages.")
    L.append("")
    for label, sub in (("all compared images", per), (f"CheXmask Dice RCA (Mean) ≥ {a.min_dice}", [r for r in per if r["dice_rca_mean"] >= a.min_dice])):
        L += [f"## {label} (n = {len(sub)})", "",
              "| metric | n | mean package / CheXmask | bias (rel.) | limits of agreement | within 10 % | CCC | r |", "|---|---|---|---|---|---|---|---|"]
        L.append("| heart width (px) " + fmt(agreement([(r["heart_px_ours"], r["heart_px_theirs"]) for r in sub if r["heart_px_theirs"]]), " px", 0))
        L.append("| thorax width (px) " + fmt(agreement([(r["thorax_px_ours"], r["thorax_px_theirs"]) for r in sub if r["thorax_px_theirs"]]), " px", 0))
        L.append("| CTR " + fmt(agreement([(r["ctr_ours"], r["ctr_theirs"]) for r in sub if r["ctr_ours"] and r["ctr_theirs"]], rel_tol=0.10), "", 3))
        dh = [r["dice_heart"] for r in sub]; dl = [r["dice_lungs"] for r in sub]
        if sub:
            L += ["", f"Dice overlap package vs CheXmask: heart median {statistics.median(dh):.3f} (min {min(dh):.3f}), lungs median {statistics.median(dl):.3f} (min {min(dl):.3f}). "
                  f"CTR > 0.5: package {sum(1 for r in sub if (r['ctr_ours'] or 0) > 0.5)}, CheXmask {sum(1 for r in sub if (r['ctr_theirs'] or 0) > 0.5)} of {len(sub)}."]
        L.append("")
    worst = sorted(per, key=lambda r: abs((r["ctr_ours"] or 0) - (r["ctr_theirs"] or 0)), reverse=True)[:8]
    L += ["## Largest CTR disagreements", "", "| image | CTR package | CTR CheXmask | heart px pkg / CheX | thorax px pkg / CheX | Dice heart | Dice lungs | RCA mean |", "|---|---|---|---|---|---|---|---|"]
    for r in worst:
        L.append(f"| {r['id'][:12]} | {r['ctr_ours']:.3f} | {r['ctr_theirs']:.3f} | {r['heart_px_ours']} / {r['heart_px_theirs']} | {r['thorax_px_ours']} / {r['thorax_px_theirs']} | {r['dice_heart']:.2f} | {r['dice_lungs']:.2f} | {r['dice_rca_mean']:.2f} |")
    out = "\n".join(L) + "\n"
    if a.per_image: Path(a.per_image).write_text(json.dumps(per, indent=1))
    if a.out: Path(a.out).write_text(out); print("wrote", a.out)
    else: print(out)


if __name__ == "__main__":
    main()
