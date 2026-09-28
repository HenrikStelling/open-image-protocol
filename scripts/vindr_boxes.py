"""VinDr-CXR: attach radiologist finding boxes (external) as regions and measure lesion long axis (px, and mm when
spacing is calibrated). Boxes are in original pixel coordinates (train.csv: class_name, rad_id, x_min, y_min, x_max, y_max).
Usage: python scripts/vindr_boxes.py [limit]"""
import csv, json, os, sys, time, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from oip.convert import add_measurements
from oip.measure import px_to_mm, CalibrationError
C = Path(os.environ.get("OIP_KAGGLE_CACHE", Path.home() / ".cache/kagglehub"))
csv_path = C / "competitions/vinbigdata-chest-xray-abnormalities-detection/train.csv"
boxes = collections.defaultdict(list)
for r in csv.DictReader(open(csv_path)):
    if r["class_name"] != "No finding" and r["x_min"]:
        boxes[r["image_id"]].append(r)
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
pkgs = sorted((ROOT / "data/oip/vindr").glob("*.oip"))[:limit]; stats = collections.Counter(); mm_vals = []; t0 = time.time()
for i, pkg in enumerate(pkgs, 1):
    m = json.loads((pkg / "oip.json").read_text()); iid = m["provenance"]["source_filename"].replace(".dicom", "")
    regs = [r for r in m["derived"]["regions"] if r.get("assertion_level") != "external"]   # keep model regions, replace external ones
    meas = [x for x in m["derived"]["measurements"] if not x["id"].startswith("lesion_")]
    for k, b in enumerate(boxes.get(iid, []), 1):
        x0, y0, x1, y1 = (float(b[c]) for c in ("x_min", "y_min", "x_max", "y_max"))
        rid = f"finding_{k}"; long_px = max(x1 - x0, y1 - y0)
        regs.append({"id": rid, "label": f"{b['class_name']} (radiologist {b['rad_id']})", "bbox_px": [int(y0), int(x0), int(y1), int(x1)], "mark": f"F{k}",
                     "assertion_level": "external", "tool": "VinDr-CXR train.csv", "confidence": 0.8})
        rec = {"id": f"lesion_{k}_long_axis", "name": f"Long axis of box F{k} ({b['class_name']})", "value": round(long_px, 1), "unit": "px",
               "method": "longer side of the radiologist bounding box in source pixels; a box bound, not a lesion measurement", "tool": "oip-measure", "tool_version": "0.1.0",
               "assertion_level": "computed", "confidence": 0.8, "validation_status": "reference_validated", "inputs": ["external: VinDr-CXR train.csv"], "geometry": {"type": "bbox", "bbox_px": [int(y0), int(x0), int(y1), int(x1)]}}
        try:
            axis = 1 if (x1 - x0) >= (y1 - y0) else 0
            rec_mm = dict(rec, id=f"lesion_{k}_long_axis_mm", value=round(px_to_mm(long_px, m, axis), 1), unit="mm",
                          method=rec["method"] + f" × pixel spacing ({m['geometry']['spacing_source']}, {m['geometry']['calibration']['plane']} plane, confidence {m['geometry']['calibration']['confidence']})",
                          confidence=round(min(0.8, {"high": 0.95, "medium": 0.8, "low": 0.5}.get(m["geometry"]["calibration"]["confidence"], 0)), 2))
            meas += [rec, rec_mm]; mm_vals.append(rec_mm["value"]); stats["mm"] += 1
        except CalibrationError:
            meas.append(rec); stats["px_only"] += 1
    if boxes.get(iid):
        add_measurements(pkg, meas, regs); stats["images_with_boxes"] += 1
    stats["images"] += 1
    if i % 100 == 0: print(f"  {i}/{len(pkgs)}", flush=True)
mm_vals.sort()
summary = dict(stats) | {"lesion_mm_median": mm_vals[len(mm_vals)//2] if mm_vals else None, "lesion_mm_p10": mm_vals[len(mm_vals)//10] if mm_vals else None, "lesion_mm_p90": mm_vals[9*len(mm_vals)//10] if mm_vals else None, "seconds": round(time.time() - t0)}
(ROOT / "data/oip/vindr/_boxes.json").write_text(json.dumps(summary, indent=1)); print(json.dumps(summary, indent=1))
