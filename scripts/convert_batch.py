"""Phase 2 batch conversion: convert real datasets to OIP packages and write a completeness/flag report.
Usage: python scripts/convert_batch.py [--limit-vindr 1000 --limit-rsna 500 --limit-siim 300 --limit-nih 300]
Outputs: data/oip/<dataset>/*.oip (git-ignored), docs/reports/phase2-conversion-stats.json, docs/reports/phase2-conversion-report.md"""
from __future__ import annotations
import argparse, collections, csv, glob, json, random, sys, time, traceback
from pathlib import Path
import pydicom
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from oip.convert import convert
from oip.convert_image import convert_image, nih_meta
import os
C = Path(os.environ.get("OIP_KAGGLE_CACHE", Path.home() / ".cache/kagglehub"))   # kagglehub download cache (REPRODUCE.md)


def dataset_files(name, limit, seed=0):
    rng = random.Random(seed)
    if name == "vindr":
        ids = (ROOT / "data/vindr-cxr/sample_ids.txt").read_text().split()
        return [C / f"competitions/vinbigdata-chest-xray-abnormalities-detection/train/{i}.dicom" for i in ids][:limit]
    if name == "rsna":
        fs = sorted((C / "competitions/rsna-pneumonia-detection-challenge/stage_2_train_images").glob("*.dcm")); rng.shuffle(fs); return fs[:limit]
    if name == "siim":
        base = sorted(glob.glob(str(C / "datasets/jesperdramsch/siim-acr-pneumothorax-segmentation-data/versions/*")))[-1]
        fs = sorted(Path(base).glob("dicom-images-train/*/*/*.dcm")); rng.shuffle(fs); return fs[:limit]
    if name == "nih":
        base = sorted(glob.glob(str(C / "datasets/nih-chest-xrays/sample/versions/*")))[-1]
        rows = list(csv.DictReader(open(Path(base) / "sample_labels.csv"))); rng.shuffle(rows)
        return [(Path(base) / "sample/images" / r["Image Index"], r) for r in rows[:limit]]
    raise KeyError(name)


HINTS = {"vindr": {"modality": "DX", "body_part": "CHEST", "view": "PA"}, "rsna": {"body_part": "CHEST"}, "siim": {"body_part": "CHEST"}}


def run(name, files):
    st = collections.Counter(); per = []; fails = []; t0 = time.time()
    out = ROOT / "data/oip" / name; out.mkdir(parents=True, exist_ok=True)
    for k, item in enumerate(files, 1):
        f, row = (item if isinstance(item, tuple) else (item, None))
        try:
            if name == "nih":
                pkg = convert_image(f, out / f.stem, nih_meta(row))
            else:
                pkg = convert(f, out / f.stem.replace(".", "_")[-40:], hints=HINTS.get(name))
            m = json.loads((pkg / "oip.json").read_text()); g, i, a, q = m["geometry"], m["intensity"], m["acquisition"], m["quality"]
            rec = dict(file=f.name, spacing_source=g["spacing_source"], spacing=g["pixel_spacing_mm"], confidence=g["calibration"]["confidence"],
                       extent_w=round(g["physical_extent_mm"][1]) if g["physical_extent_mm"] else None, photometric=i["photometric"], bits=i["bits_stored"],
                       voi=i["voi"]["source"], orientation=g["orientation"]["assertion_level"], modality=a["modality"]["value"], modality_level=a["modality"]["assertion_level"],
                       view=a["view"]["value"], vendor=(a.get("device") or {}).get("manufacturer"), rows=g["rows"], cols=g["columns"], flags=q["flags"],
                       ts=(pydicom.dcmread(f, stop_before_pixels=True).file_meta.TransferSyntaxUID.name if row is None else "png"),
                       context_chars=len((pkg / "context.md").read_text()), pkg_bytes=sum(p.stat().st_size for p in pkg.rglob("*") if p.is_file()), src_bytes=f.stat().st_size)
            per.append(rec); st["ok"] += 1
        except Exception as e:
            fails.append(dict(file=f.name, error=f"{type(e).__name__}: {str(e)[:200]}")); st["fail"] += 1
        if k % 100 == 0: print(f"  {name}: {k}/{len(files)} ({st['ok']} ok, {st['fail']} fail)", flush=True)
    return dict(n=len(files), ok=st["ok"], fail=st["fail"], seconds=round(time.time() - t0, 1), per_image=per, failures=fails)


def summarize(name, r):
    per = r["per_image"]; n = max(len(per), 1)
    cnt = lambda key: collections.Counter(str(x.get(key)) for x in per).most_common()
    flags = collections.Counter(f for x in per for f in x["flags"]).most_common()
    L = [f"### {name}", f"- converted {r['ok']}/{r['n']} ({r['fail']} failures) in {r['seconds']} s ({r['seconds']/max(r['n'],1):.2f} s/image)"]
    if per:
        L.append(f"- package/source size ratio: {sum(x['pkg_bytes'] for x in per)/max(sum(x['src_bytes'] for x in per),1):.2f}; context.md mean {sum(x['context_chars'] for x in per)/n:.0f} chars (~{sum(x['context_chars'] for x in per)/n/4:.0f} tokens)")
        for key in ("spacing_source", "confidence", "photometric", "bits", "voi", "orientation", "modality_level", "view", "vendor", "ts"):
            L.append(f"- {key}: " + ", ".join(f"{v} ({c})" for v, c in cnt(key)))
        ext = [x["extent_w"] for x in per if x["extent_w"]]
        if ext: L.append(f"- computed image width from header spacing: min {min(ext)} / median {sorted(ext)[len(ext)//2]} / max {max(ext)} mm (n={len(ext)})")
        L.append("- flags: " + ", ".join(f"{f} ({c}, {100*c/n:.0f}%)" for f, c in flags))
    for x in r["failures"][:5]: L.append(f"- FAIL {x['file']}: {x['error']}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for d, dflt in (("vindr", 1000), ("rsna", 500), ("siim", 300), ("nih", 300)): ap.add_argument(f"--limit-{d}", type=int, default=dflt)
    a = ap.parse_args(); results = {}
    for name in ("vindr", "rsna", "siim", "nih"):
        lim = getattr(a, f"limit_{name}")
        if lim <= 0: continue
        print(f"== {name} (limit {lim})", flush=True); results[name] = run(name, dataset_files(name, lim))
    # merge with previous runs so re-running one dataset does not erase the others; per-image stats stay out of git
    stats_path = ROOT / "docs/reports/phase2-conversion-stats.json"
    merged = json.loads(stats_path.read_text()) if stats_path.exists() else {}
    for k, v in results.items():
        (ROOT / "data/oip" / k / "_per_image.json").write_text(json.dumps(v["per_image"], indent=1))
        merged[k] = {kk: vv for kk, vv in v.items() if kk != "per_image"} | {"summary_md": summarize(k, v), "generated": time.strftime("%Y-%m-%d %H:%M")}
    stats_path.write_text(json.dumps(merged, indent=1))
    md = ["# Phase 2 conversion report (auto-generated by scripts/convert_batch.py)", "", f"Updated {time.strftime('%Y-%m-%d %H:%M')}. Packages under `data/oip/` (not committed); per-image stats in `data/oip/<dataset>/_per_image.json`.", ""]
    md += [merged[k]["summary_md"] + f"\n(generated {merged[k]['generated']})\n" for k in ("vindr", "rsna", "siim", "nih") if k in merged]
    (ROOT / "docs/reports/phase2-conversion-report.md").write_text("\n".join(md)); print("\n".join(md))
