"""Anatomy adapter for chest radiographs: TorchXRayVision PSPNet (ChestX-Det, 14 structures) -> derived.regions + CTR.
All outputs are assertion_level 'inferred' (model) or 'computed' (geometry on inferred masks) and validation_status
'unvalidated' until Tier-2 (CheXmask) agreement is measured."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from PIL import Image

_MODEL = None
KEEP = {"Heart": "heart", "Left Lung": "lung_left", "Right Lung": "lung_right", "Spine": "spine", "Aorta": "aorta", "Mediastinum": "mediastinum",
        "Left Clavicle": "clavicle_left", "Right Clavicle": "clavicle_right", "Facies Diaphragmatica": "diaphragm"}
CODES = {"heart": ("SCT", "80891009", "Heart"), "lung_left": ("SCT", "44029006", "Left lung"), "lung_right": ("SCT", "3341006", "Right lung"),
         "spine": ("SCT", "421060004", "Vertebral column"), "aorta": ("SCT", "15825003", "Aorta"), "mediastinum": ("SCT", "72410000", "Mediastinum"),
         "clavicle_left": ("SCT", "51299004", "Clavicle"), "clavicle_right": ("SCT", "51299004", "Clavicle"), "diaphragm": ("SCT", "5798000", "Diaphragm")}


def _model():
    global _MODEL
    if _MODEL is None:
        import torch, torchxrayvision as xrv
        _MODEL = xrv.baseline_models.chestx_det.PSPNet().eval()
    return _MODEL


def segment(canon_u8: np.ndarray) -> dict[str, np.ndarray]:
    """canon_u8: canonical render (8-bit, high attenuation bright). Returns {region_id: bool mask at full resolution}."""
    import torch, torchxrayvision as xrv
    m = _model()
    img = xrv.datasets.normalize(canon_u8.astype(np.float32), 255)[None, ...]      # [-1024, 1024]
    img = xrv.datasets.XRayResizer(512)(img)
    with torch.no_grad():
        out = m(torch.from_numpy(img)[None, ...])[0].numpy()                           # [14, 512, 512] logits
    H, W = canon_u8.shape; masks = {}
    for k, name in enumerate(m.targets):
        if name in KEEP:
            small = (out[k] > 0).astype(np.uint8) * 255
            masks[KEEP[name]] = np.asarray(Image.fromarray(small).resize((W, H), Image.NEAREST)) > 127
    return masks


def _bbox(mask):
    r = np.where(mask.any(axis=1))[0]; c = np.where(mask.any(axis=0))[0]
    return None if r.size == 0 else [int(r.min()), int(c.min()), int(r.max()), int(c.max())]


def measure_chest(pkg: Path, model_version: str = "torchxrayvision-pspnet-chestx-det") -> dict:
    """Segment, write masks, compute CTR (+ mm widths when calibrated) and attach everything to the package."""
    from .convert import add_measurements
    from .measure import cardiothoracic_ratio, width_mm, CalibrationError
    pkg = Path(pkg); m = json.loads((pkg / "oip.json").read_text())
    canon = np.asarray(Image.open(pkg / "renders/canonical.png").convert("L"))
    masks = segment(canon)
    (pkg / "derived/masks").mkdir(parents=True, exist_ok=True)
    regions, mark = [], 1
    edge = m["geometry"]["orientation"]["edge_labels"]
    notes = []
    for rid, mk in masks.items():
        if not mk.any():
            continue
        Image.fromarray((mk * 255).astype(np.uint8)).save(pkg / f"derived/masks/{rid}.png")
        sys_, val, disp = CODES[rid]
        reg = {"id": rid, "label": disp.lower(), "code": {"system": sys_, "value": val, "display": disp}, "mask": f"derived/masks/{rid}.png",
               "bbox_px": _bbox(mk), "mark": str(mark), "assertion_level": "inferred", "tool": model_version, "confidence": 0.7}
        # laterality sanity check: patient's left structures should sit on the image side labelled 'L'
        if rid.endswith("_left") or rid.endswith("_right"):
            cx = np.where(mk.any(axis=0))[0].mean(); side = "right" if cx > canon.shape[1] / 2 else "left"
            expect = "L" if rid.endswith("_left") else "R"
            if edge.get(side) and edge[side] != expect:
                notes.append(f"{rid}: model placed it on image {side} (labelled {edge[side]}); check orientation.")
                reg["confidence"] = 0.4
        regions.append(reg); mark += 1
    meas = []
    if "heart" in masks and ("lung_left" in masks or "lung_right" in masks):
        thorax = np.zeros_like(canon, dtype=bool)
        for k in ("lung_left", "lung_right"):
            if k in masks: thorax |= masks[k]
        ctr = cardiothoracic_ratio(masks["heart"], thorax)
        ctr.update({"code": {"system": "RadElement", "value": "RDE1", "display": "Cardiothoracic ratio"}, "method": "max horizontal heart-mask width / max horizontal width of the union of both lung masks (PSPNet, inferred masks); spacing independent",
                    "tool": model_version, "tool_version": "0.1.0", "confidence": 0.6, "validation_status": "unvalidated", "inputs": ["derived/masks/heart.png", "derived/masks/lung_left.png", "derived/masks/lung_right.png"]})
        meas.append(ctr)
        try:
            hw = width_mm(masks["heart"], m); tw = width_mm(thorax, m)
            for mid, name, w, inp in (("heart_width", "Transverse cardiac diameter", hw, "heart"), ("thorax_width", "Internal thoracic width (lung-mask extent)", tw, "lungs")):
                meas.append({"id": mid, "name": name, "value": round(w["value"], 1), "unit": "mm", "method": f"max horizontal width of inferred {inp} mask × column spacing ({m['geometry']['spacing_source']}, {m['geometry']['calibration']['plane']} plane)",
                             "tool": model_version, "tool_version": "0.1.0", "assertion_level": "computed", "confidence": round(min(w["confidence"], 0.7), 2), "validation_status": "unvalidated", "inputs": [f"derived/masks/{inp}.png"]})
        except CalibrationError:
            notes.append("No calibrated spacing: mm widths not reported (ratio only).")
    m2 = add_measurements(pkg, meas, regions)
    if notes:
        m2["quality"]["notes"] = sorted(set(m2["quality"].get("notes", []) + notes))
        (pkg / "oip.json").write_text(json.dumps(m2, indent=2))
        from .context import build_context
        (pkg / "context.md").write_text(build_context(m2))
    return {"regions": [r["id"] for r in regions], "ctr": next((x["value"] for x in meas if x["id"] == "ctr"), None), "notes": notes}
