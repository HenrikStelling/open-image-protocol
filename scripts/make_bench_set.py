"""Build the paper benchmark set (E4): stratified VinDr packages + NIH packages, generated from the raw sources into
~/oip-bench/<dataset>-paper (outside iCloud). No radiologist boxes (no-leakage rule). Anatomy measurements attached.
Usage: python scripts/make_bench_set.py --vindr 100 --nih 50"""
from __future__ import annotations
import argparse, csv, collections, json, random, sys, time, glob
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from oip.convert import convert
from oip.convert_image import convert_image, nih_meta
from oip.anatomy import measure_chest
import os
C = Path(os.environ.get("OIP_KAGGLE_CACHE", Path.home() / ".cache/kagglehub"))   # kagglehub download cache
OUT = Path(os.environ.get("OIP_BENCH_DIR", Path.home() / "oip-bench"))            # package store, outside the clone (REPRODUCE.md)
LEAK = ["aortic enlargement", "atelectasis", "calcification", "cardiomegaly", "consolidation", "ild", "infiltration", "lung opacity", "nodule", "other lesion", "pleural effusion", "pleural thickening", "pneumothorax", "pulmonary fibrosis"]


def leak_check(pkg: Path) -> list[str]:
    txt = (pkg / "context.md").read_text().lower() + json.dumps(json.loads((pkg / "oip.json").read_text())).lower()
    return [k for k in LEAK if k in txt]


def vindr(n: int, seed: int):
    """Stratify by (finding present, cardiomegaly label) × spacing availability, from the 1,000-sample ids."""
    ids = (ROOT / "data/vindr-cxr/sample_ids.txt").read_text().split() if (ROOT / "data/vindr-cxr/sample_ids.txt").exists() else Path("/Users/pal/Desktop/OIP/data/vindr-cxr/sample_ids.txt").read_text().split()
    labels = collections.defaultdict(set)
    for r in csv.DictReader(open(C / "competitions/vinbigdata-chest-xray-abnormalities-detection/train.csv")):
        if r["class_name"] != "No finding": labels[r["image_id"]].add(r["class_name"])
    import pydicom
    cells = collections.defaultdict(list)
    for i in ids:
        f = C / f"competitions/vinbigdata-chest-xray-abnormalities-detection/train/{i}.dicom"
        if not f.exists(): continue
        ds = pydicom.dcmread(f, stop_before_pixels=True); has_sp = ds.get("PixelSpacing") is not None
        cells[(bool(labels.get(i)), "Cardiomegaly" in labels.get(i, set()), has_sp)].append(i)
    rng = random.Random(seed); chosen = []
    # target: half with findings; within findings a third cardiomegaly; ~85 % with spacing (matches the source)
    plan = {(False, False, True): 0.40, (False, False, False): 0.08, (True, False, True): 0.25, (True, True, True): 0.17, (True, False, False): 0.05, (True, True, False): 0.05}
    for cell, frac in plan.items():
        pool = cells.get(cell, []); k = min(len(pool), round(n * frac)); chosen += rng.sample(pool, k)
    while len(chosen) < n:
        extra = [i for pool in cells.values() for i in pool if i not in chosen]; chosen.append(rng.choice(extra))
    out = OUT / "vindr-paper"; out.mkdir(parents=True, exist_ok=True); t0 = time.time(); leaks = 0
    for k, i in enumerate(chosen[:n], 1):
        pkg = out / f"{i}.oip"
        if not (pkg / "oip.json").exists():
            convert(C / f"competitions/vinbigdata-chest-xray-abnormalities-detection/train/{i}.dicom", out / i, hints={"modality": "DX", "body_part": "CHEST", "view": "PA"})
            measure_chest(pkg)
        if leak_check(pkg): leaks += 1
        if k % 10 == 0: print(f"  vindr {k}/{n} ({(time.time()-t0)/k:.1f} s/img)", flush=True)
    print(f"vindr-paper: {n} packages, leaks: {leaks}; cells used: { {str(c): len(v) for c, v in cells.items()} }")


def nih(n: int, seed: int):
    base = sorted(glob.glob(str(C / "datasets/nih-chest-xrays/sample/versions/*")))[-1]
    rows = list(csv.DictReader(open(Path(base) / "sample_labels.csv"))); rng = random.Random(seed)
    with_f = [r for r in rows if r["Finding Labels"] != "No Finding"]; no_f = [r for r in rows if r["Finding Labels"] == "No Finding"]
    chosen = rng.sample(with_f, n // 2) + rng.sample(no_f, n - n // 2)
    out = OUT / "nih-paper"; out.mkdir(parents=True, exist_ok=True); t0 = time.time(); leaks = 0
    for k, r in enumerate(chosen, 1):
        meta = nih_meta(r); meta["labels"] = None; meta["notes"] = ["Images are 1024x1024 downsampled PNGs; original DICOM headers are not available."]  # no labels in the package
        pkg = out / r["Image Index"].replace(".png", ".oip")
        if not (pkg / "oip.json").exists():
            convert_image(Path(base) / "sample/images" / r["Image Index"], out / r["Image Index"].replace(".png", ""), meta)
            measure_chest(pkg)
        if leak_check(pkg): leaks += 1
        if k % 10 == 0: print(f"  nih {k}/{n} ({(time.time()-t0)/k:.1f} s/img)", flush=True)
    print(f"nih-paper: {n} packages, leaks: {leaks}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--vindr", type=int, default=100); ap.add_argument("--nih", type=int, default=50); ap.add_argument("--seed", type=int, default=1); a = ap.parse_args()
    if a.vindr: vindr(a.vindr, a.seed)
    if a.nih: nih(a.nih, a.seed)
