"""Spacing selection and orientation derivation (the decisions everything else depends on)."""
from __future__ import annotations
from pydicom.dataset import Dataset

DIRECTION_WORDS = {"L": "patient LEFT", "R": "patient RIGHT", "A": "ANTERIOR", "P": "POSTERIOR",
                   "H": "HEAD", "F": "FEET"}
OPPOSITE = {"L": "R", "R": "L", "A": "P", "P": "A", "H": "F", "F": "H"}


def _pair(v):
    try:
        return [float(v[0]), float(v[1])]
    except Exception:
        return None


def select_spacing(ds: Dataset) -> dict:
    """Return geometry.pixel_spacing_mm, spacing_source and calibration per Q6 ordering."""
    ps = _pair(ds.get("PixelSpacing"))
    ips = _pair(ds.get("ImagerPixelSpacing"))
    cal_type = ds.get("PixelSpacingCalibrationType")
    mag = ds.get("EstimatedRadiographicMagnificationFactor")
    mag = float(mag) if mag not in (None, "") else None
    modality = str(ds.get("Modality", ""))

    if ps and cal_type:
        return dict(spacing=ps, source="PixelSpacing_calibrated",
                    calibration=dict(plane="patient", type=str(cal_type), magnification_factor=mag, confidence="high"))
    if ps and modality in ("CT", "MR", "PT"):
        return dict(spacing=ps, source="PixelSpacing",
                    calibration=dict(plane="patient", type=None, magnification_factor=None, confidence="high"))
    if ps and modality == "NM":
        return dict(spacing=ps, source="PixelSpacing",
                    calibration=dict(plane="detector", type=None, magnification_factor=None, confidence="medium"))
    if ps:
        return dict(spacing=ps, source="PixelSpacing",
                    calibration=dict(plane="detector", type=None, magnification_factor=mag, confidence="medium"))
    if ips and mag:
        return dict(spacing=[ips[0] / mag, ips[1] / mag], source="ImagerPixelSpacing_magnification_corrected",
                    calibration=dict(plane="patient", type=None, magnification_factor=mag, confidence="medium"))
    if ips:
        return dict(spacing=ips, source="ImagerPixelSpacing",
                    calibration=dict(plane="detector", type=None, magnification_factor=None, confidence="medium"))
    return dict(spacing=None, source="none",
                calibration=dict(plane="unknown", type=None, magnification_factor=None, confidence="none"))


def derive_orientation(ds: Dataset, view: str | None) -> dict:
    """Edge labels from PatientOrientation, else inferred from view for frontal projections."""
    po = ds.get("PatientOrientation")
    if po and len(po) == 2:
        row, col = str(po[0])[0], str(po[1])[0]
        level, note = "measured", "From DICOM PatientOrientation."
    elif view and view.upper() in ("PA", "AP", "ANTERIOR", "POSTERIOR"):
        # Conventional display: frontal image, patient's right on image left, head up.
        row, col = ("R", "F") if view.upper() == "POSTERIOR" else ("L", "F")
        level, note = "inferred", f"No PatientOrientation tag; assumed conventional display for view {view}."
    else:
        return dict(row_direction=None, column_direction=None,
                    edge_labels=dict(left=None, right=None, top=None, bottom=None),
                    assertion_level="unknown", note="Orientation unknown; do not assume laterality.")
    return dict(row_direction=row, column_direction=col,
                edge_labels=dict(left=OPPOSITE.get(row), right=row, top=OPPOSITE.get(col), bottom=col),
                assertion_level=level, note=note)
