"""Modality adapters: fill acquisition.dx / acquisition.nm and frames[] from a DICOM dataset."""
from __future__ import annotations
import numpy as np
from pydicom.dataset import Dataset


def _num(ds, kw, unit, level="measured"):
    v = ds.get(kw)
    if v in (None, ""):
        return {"value": None, "unit": unit, "assertion_level": "unknown"}
    try:
        return {"value": float(v), "unit": unit, "assertion_level": level}
    except Exception:
        return {"value": None, "unit": unit, "assertion_level": "unknown"}


def family(modality: str) -> str:
    return {"DX": "projection_radiography", "CR": "projection_radiography", "RG": "projection_radiography",
            "MG": "projection_radiography", "NM": "scintigraphy", "CT": "tomography", "MR": "tomography",
            "PT": "tomography"}.get(modality, "other")


def dx_block(ds: Dataset) -> dict:
    return {
        "kvp": _num(ds, "KVP", "kV"),
        "exposure_mAs": _num(ds, "Exposure", "mA.s"),
        "exposure_time_ms": _num(ds, "ExposureTime", "ms"),
        "exposure_index": _num(ds, "ExposureIndex", "1"),
        "distance_source_to_detector_mm": _num(ds, "DistanceSourceToDetector", "mm"),
        "distance_source_to_patient_mm": _num(ds, "DistanceSourceToPatient", "mm"),
        "grid": str(ds.get("Grid")) if ds.get("Grid") else None,
        "detector_type": str(ds.get("DetectorType")) if ds.get("DetectorType") else None,
    }


def _uptake_minutes(ds: Dataset, rp: Dataset | None):
    """Minutes from RadiopharmaceuticalStartTime to AcquisitionTime; absolute times are NOT kept."""
    try:
        start = rp.get("RadiopharmaceuticalStartTime") if rp is not None else None
        acq = ds.get("AcquisitionTime")
        if not start or not acq:
            return None
        def secs(t):
            t = str(t).split(".")[0].ljust(6, "0")
            return int(t[:2]) * 3600 + int(t[2:4]) * 60 + int(t[4:6])
        d = (secs(acq) - secs(start)) % 86400
        return round(d / 60.0, 1)
    except Exception:
        return None


def nm_block(ds: Dataset) -> dict:
    it = list(ds.get("ImageType", []))
    rp_seq = ds.get("RadiopharmaceuticalInformationSequence")
    rp = rp_seq[0] if rp_seq else None
    radionuclide = None
    if rp is not None and rp.get("RadionuclideCodeSequence"):
        radionuclide = str(rp.RadionuclideCodeSequence[0].get("CodeMeaning", "")) or None
    windows = []
    for i, ew in enumerate(ds.get("EnergyWindowInformationSequence", []) or []):
        rng = ew.get("EnergyWindowRangeSequence")
        if rng:
            windows.append({"name": str(ew.get("EnergyWindowName", f"window {i}")),
                            "lower_keV": float(rng[0].get("EnergyWindowLowerLimit", 0)),
                            "upper_keV": float(rng[0].get("EnergyWindowUpperLimit", 0))})
    det = ds.get("DetectorInformationSequence")
    collimator = str(det[0].get("CollimatorType")) if det and det[0].get("CollimatorType") else None
    uptake = _uptake_minutes(ds, rp)
    return {
        "image_type": it[2] if len(it) > 2 else None,
        "radiopharmaceutical": str(rp.get("Radiopharmaceutical")) if rp is not None and rp.get("Radiopharmaceutical") else None,
        "radionuclide": radionuclide,
        "administered_activity_MBq": _num(rp, "RadionuclideTotalDose", "MBq") if rp is not None else {"value": None, "unit": "MBq", "assertion_level": "unknown"},
        "uptake_time_min": {"value": uptake, "unit": "min", "assertion_level": "computed" if uptake is not None else "unknown"},
        "route": str(rp.get("RadiopharmaceuticalRoute")) if rp is not None and rp.get("RadiopharmaceuticalRoute") else None,
        "energy_windows": windows,
        "collimator": collimator,
        "number_of_detectors": int(ds.get("NumberOfDetectors")) if ds.get("NumberOfDetectors") else None,
        "whole_body": {"technique": str(ds.get("WholeBodyTechnique")) if ds.get("WholeBodyTechnique") else None,
                        "scan_length_mm": float(ds.ScanLength) if ds.get("ScanLength") else None,
                        "scan_velocity_mm_per_s": float(ds.ScanVelocity) if ds.get("ScanVelocity") else None},
        "corrections": [str(x) for x in (ds.get("CorrectedImage") or [])],
        "termination_condition": str(ds.get("AcquisitionTerminationCondition")) if ds.get("AcquisitionTerminationCondition") else None,
    }


def nm_frames(ds: Dataset, arr: np.ndarray) -> list[dict]:
    """One entry per frame with detector/view, duration and counts."""
    n = arr.shape[0]
    det_vec = list(ds.get("DetectorVector", []) or [])
    ew_vec = list(ds.get("EnergyWindowVector", []) or [])
    det_info = ds.get("DetectorInformationSequence") or []
    dur = ds.get("ActualFrameDuration")
    frames = []
    for i in range(n):
        det = int(det_vec[i]) if i < len(det_vec) else None
        view = None
        if det is not None and det - 1 < len(det_info):
            vcs = det_info[det - 1].get("ViewCodeSequence")
            if vcs:
                view = str(vcs[0].get("CodeMeaning", "")).upper() or None
        note = ""
        if view == "POSTERIOR":
            note = "Posterior view: patient's LEFT appears on the image LEFT (mirrored relative to anterior)."
        po = det_info[det - 1].get("PatientOrientation") if det is not None and det - 1 < len(det_info) else None
        if po and len(po) == 2:
            row, col = str(po[0])[0], str(po[1])[0]; lvl = "measured"
        elif view in ("ANTERIOR", "POSTERIOR"):
            row, col = ("R", "F") if view == "POSTERIOR" else ("L", "F"); lvl = "inferred"
        else:
            row = col = None; lvl = "unknown"
        opp = {"L": "R", "R": "L", "A": "P", "P": "A", "H": "F", "F": "H"}
        edge = {"left": opp.get(row), "right": row, "top": opp.get(col), "bottom": col}
        frames.append({"index": i, "view": view, "detector": det, "edge_labels": edge, "edge_labels_assertion": lvl,
                       "duration_ms": float(dur) if dur else None,
                       "counts_total": float(arr[i].astype(np.float64).sum()),
                       "counts_accumulated_tag": float(ds.CountsAccumulated) if ds.get("CountsAccumulated") else None,
                       "energy_window": int(ew_vec[i]) if i < len(ew_vec) else None,
                       "orientation_note": note,
                       "pixels": f"pixels/frame-{i:04d}.png", "render": f"renders/frame-{i:04d}.png"})
    return frames
