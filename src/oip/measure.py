"""Deterministic measurement tools with guardrails (no mm without calibrated spacing)."""
from __future__ import annotations
import numpy as np


class CalibrationError(ValueError):
    """Raised when a physical (mm) measurement is requested but the package has no pixel spacing."""


def px_to_mm(px: float, manifest: dict, axis: int = 1) -> float:
    sp = manifest["geometry"]["pixel_spacing_mm"]
    if not sp:
        raise CalibrationError("pixel_spacing_mm is null: only pixel/ratio measurements are allowed")
    return float(px) * float(sp[axis])


def mask_extent(mask: np.ndarray) -> dict:
    """Bounding extent of a binary mask: width/height in px and bbox [r0,c0,r1,c1]."""
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if rows.size == 0:
        return {"width_px": 0, "height_px": 0, "bbox_px": None}
    return {"width_px": int(cols.max() - cols.min() + 1), "height_px": int(rows.max() - rows.min() + 1),
            "bbox_px": [int(rows.min()), int(cols.min()), int(rows.max()), int(cols.max())]}


def width_mm(mask: np.ndarray, manifest: dict) -> dict:
    ext = mask_extent(mask)
    return {"value": px_to_mm(ext["width_px"], manifest, axis=1), "unit": "mm", "width_px": ext["width_px"],
            "assertion_level": "computed",
            "confidence": {"high": 0.95, "medium": 0.8, "low": 0.5, "none": 0.0}[manifest["geometry"]["calibration"]["confidence"]]}


def cardiothoracic_ratio(heart_mask: np.ndarray, thorax_mask: np.ndarray) -> dict:
    """CTR = max horizontal cardiac width / max horizontal internal thoracic width. Dimensionless, spacing-free."""
    h = mask_extent(heart_mask); t = mask_extent(thorax_mask)
    if not t["width_px"]:
        return {"value": None, "unit": "1", "assertion_level": "unknown"}
    return {"id": "ctr", "name": "Cardiothoracic ratio", "value": round(h["width_px"] / t["width_px"], 4), "unit": "1",
            "method": "max horizontal heart-mask width / max horizontal thorax-mask width (pixels, spacing independent)",
            "tool": "oip-measure", "assertion_level": "computed",
            "geometry": {"heart_bbox_px": h["bbox_px"], "thorax_bbox_px": t["bbox_px"]}}


def region_counts(frame: np.ndarray, mask: np.ndarray, duration_ms: float | None) -> dict:
    """Counts inside a region; counts per second if duration is known. Only comparable within one package/window."""
    c = float(frame[mask.astype(bool)].astype(np.float64).sum())
    out = {"counts": c, "pixels": int(mask.astype(bool).sum()), "unit": "counts", "assertion_level": "computed",
           "caution": "counts are only comparable within the same acquisition and energy window"}
    if duration_ms:
        out["cps"] = c / (duration_ms / 1000.0)
    return out
