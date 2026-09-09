"""OIP-Bench task set for planar scintigraphy (bone scans). Ground truth from the manifest of the NM image adapter:
view (anterior/posterior from folder), orientation per view, units = counts, no calibrated scale, count recovery when present.
Tasks the file cannot answer verbatim: posterior mirroring (left edge side on a posterior view), flip consistency, hottest-region
side (computed from pixels by the task builder), and a counts-semantics question (are brightness values comparable to another scan?)."""
from __future__ import annotations
import json, random
from pathlib import Path
import numpy as np
from PIL import Image

UNDERSTANDING_NM = ("modality_nm", "left_edge_nm", "scale_available_nm", "counts_semantics", "hot_side", "flip_check_nm")


def tasks_for_nm_package(pkg: Path) -> list[dict]:
    m = json.loads((pkg / "oip.json").read_text()); g, a, i = m["geometry"], m["acquisition"], m["intensity"]
    el = g["orientation"]["edge_labels"]; view = (a["view"]["value"] or "").upper()
    T = [dict(type="modality_nm", question="What kind of image is this? Answer with one of: radiograph, CT, MRI, scintigraphy (nuclear medicine), ultrasound.", answer="scintigraphy", gating=False)]
    if el.get("left") in ("L", "R"):
        T.append(dict(type="left_edge_nm", question=f"This is a {view.lower()} whole-body view. Which side of the patient is at the LEFT edge of the image? Answer 'patient right' or 'patient left'.", answer="patient right" if el["left"] == "R" else "patient left"))
        for flipped in (False, True):
            T.append(dict(type="flip_check_nm", question="Compare the image with the stated orientation (which patient side is at the LEFT edge). Does the image AGREE with the stated orientation, or is it mirrored? Answer 'agree' or 'mirrored'.", answer="mirrored" if flipped else "agree", flipped=flipped, conditions=["ctx_l1", "ctx"]))
    T.append(dict(type="scale_available_nm", question="Can distances in this image be stated in millimetres with a known calibration? Answer 'yes' or 'no'.", answer="yes" if g["pixel_spacing_mm"] and g["calibration"]["confidence"] in ("high", "medium") else "no"))
    T.append(dict(type="counts_semantics", question="Can the brightness of a region in this image be compared directly with the brightness of the same region in a scan of another patient to say which has higher tracer uptake? Answer 'yes' or 'no'.", answer="no"))
    # hottest side computed from the pixels (image-left vs image-right half, excluding the midline), then mapped to the patient side
    arr = np.asarray(Image.open(pkg / m["pixels"]["paths"][0])).astype(np.float64); w = arr.shape[1]; mid = int(w * 0.08)
    left, right = arr[:, : w // 2 - mid].sum(), arr[:, w // 2 + mid:].sum()
    if el.get("left") in ("L", "R") and abs(left - right) / max(left + right, 1) > 0.04:      # only when the asymmetry is clear
        img_side = "left" if left > right else "right"; pat = el[img_side]
        T.append(dict(type="hot_side", question="Ignoring the spine and bladder, which side of the PATIENT shows more total tracer uptake (more counts) in this image? Answer 'patient right' or 'patient left'.", answer="patient right" if pat == "R" else "patient left"))
    for t in T:
        t.setdefault("gating", t["type"] in UNDERSTANDING_NM); t["pkg"] = str(pkg); t["id"] = f"{pkg.name}:{t['type']}" + (":flipped" if t.get("flipped") else "")
    return T


def build_nm(pkg_dir: Path, n: int = 40, seed: int = 0) -> list[dict]:
    pkgs = sorted(p for p in pkg_dir.glob("*.oip") if (p / "oip.json").exists()); random.Random(seed).shuffle(pkgs); out = []
    for p in pkgs[:n]: out += tasks_for_nm_package(p)
    return out
