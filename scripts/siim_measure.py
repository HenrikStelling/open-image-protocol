"""SIIM-ACR: attach radiologist pneumothorax masks (external) to converted packages and compute the pneumothorax /
lung area ratio (spacing-free) plus, where present, areas in px. Usage: python scripts/siim_measure.py [limit]"""
import csv, glob, json, sys, time
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from oip.convert import add_measurements
from oip.anatomy import segment
from oip.measure import mask_extent
base = sorted(glob.glob(str(Path.home() / ".cache/kagglehub/datasets/jesperdramsch/siim-acr-pneumothorax-segmentation-data/versions/*")))[-1]
rle = {}
for r in csv.DictReader(open(Path(base) / "train-rle.csv")):
    k = r["ImageId"].strip(); v = r[" EncodedPixels"].strip() if " EncodedPixels" in r else r["EncodedPixels"].strip()
    rle.setdefault(k, []).append(v)


def rle2mask(s, w=1024, h=1024):
    """SIIM relative RLE (start offsets are relative), column-major."""
    m = np.zeros(w * h, np.uint8)
    if s == "-1": return m.reshape(w, h).T
    a = np.array(s.split(), int); pos = 0
    for i in range(0, len(a), 2):
        pos += a[i]; m[pos:pos + a[i + 1]] = 1; pos += a[i + 1]
    return m.reshape(w, h).T


limit = int(sys.argv[1]) if len(sys.argv) > 1 else 300
pkgs = sorted((ROOT / "data/oip/siim").glob("*.oip"))[:limit]; out = []; t0 = time.time()
for i, pkg in enumerate(pkgs, 1):
    m = json.loads((pkg / "oip.json").read_text()); sid = m["provenance"]["source_filename"].replace(".dcm", "")
    if sid not in rle: continue
    ptx = np.zeros((1024, 1024), bool)
    for s in rle[sid]: ptx |= rle2mask(s).astype(bool)
    canon = np.asarray(Image.open(pkg / "renders/canonical.png").convert("L")); masks = segment(canon)
    lungs = masks.get("lung_left", np.zeros_like(ptx)) | masks.get("lung_right", np.zeros_like(ptx))
    (pkg / "derived/masks").mkdir(exist_ok=True, parents=True)
    regions = []
    for rid, mk, lvl, tool, conf in (("lung_left", masks.get("lung_left"), "inferred", "torchxrayvision-pspnet-chestx-det", 0.7), ("lung_right", masks.get("lung_right"), "inferred", "torchxrayvision-pspnet-chestx-det", 0.7)):
        if mk is not None and mk.any():
            Image.fromarray((mk * 255).astype(np.uint8)).save(pkg / f"derived/masks/{rid}.png")
            regions.append({"id": rid, "label": rid.replace("_", " "), "mask": f"derived/masks/{rid}.png", "bbox_px": mask_extent(mk)["bbox_px"], "mark": str(len(regions) + 1), "assertion_level": lvl, "tool": tool, "confidence": conf})
    has = bool(ptx.any())
    if has:
        Image.fromarray((ptx * 255).astype(np.uint8)).save(pkg / "derived/masks/pneumothorax.png")
        regions.append({"id": "pneumothorax", "label": "pneumothorax (radiologist annotation)", "code": {"system": "SCT", "value": "36118008", "display": "Pneumothorax"}, "mask": "derived/masks/pneumothorax.png", "bbox_px": mask_extent(ptx)["bbox_px"], "mark": str(len(regions) + 1), "assertion_level": "external", "tool": "SIIM-ACR train-rle.csv", "confidence": 0.9})
    meas = [{"id": "ptx_area_px", "name": "Pneumothorax area", "value": float(ptx.sum()), "unit": "px", "method": "pixel count of the radiologist mask (SIIM-ACR); no calibrated spacing, so no mm2", "tool": "oip-measure", "tool_version": "0.1.0", "assertion_level": "computed", "confidence": 0.9, "validation_status": "reference_validated", "inputs": ["derived/masks/pneumothorax.png"]}]
    if has and lungs.any():
        side = "lung_right" if (ptx & masks.get("lung_right", ptx & False)).sum() >= (ptx & masks.get("lung_left", ptx & False)).sum() else "lung_left"
        lung = masks[side]
        meas.append({"id": "ptx_lung_fraction", "name": f"Pneumothorax area / ipsilateral lung-field area ({side.replace('_', ' ')})", "value": round(float(ptx.sum()) / float(lung.sum() | 1), 4), "unit": "1",
                     "method": "radiologist pneumothorax mask pixels / inferred ipsilateral lung-field mask pixels (PSPNet); spacing independent", "tool": "oip-measure", "tool_version": "0.1.0", "assertion_level": "computed", "confidence": 0.6, "validation_status": "unvalidated", "inputs": ["derived/masks/pneumothorax.png", f"derived/masks/{side}.png"]})
    add_measurements(pkg, meas, regions)
    out.append({"pkg": pkg.name, "ptx": has, "area_px": int(ptx.sum()), "fraction": next((x["value"] for x in meas if x["id"] == "ptx_lung_fraction"), None)})
    if i % 25 == 0: print(f"  {i}/{len(pkgs)} ({(time.time()-t0)/i:.1f} s/img)", flush=True)
pos = [o for o in out if o["ptx"]]; fr = sorted(o["fraction"] for o in pos if o["fraction"] is not None)
summary = {"n": len(out), "with_pneumothorax": len(pos), "fraction_median": fr[len(fr)//2] if fr else None, "fraction_p90": fr[9*len(fr)//10] if fr else None, "area_px_median": sorted(o["area_px"] for o in pos)[len(pos)//2] if pos else None, "results": out}
(ROOT / "data/oip/siim/_measure.json").write_text(json.dumps(summary, indent=1)); print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=1))
