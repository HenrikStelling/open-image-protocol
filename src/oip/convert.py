"""DICOM -> OIP package converter (v0: single-frame CR/DX/CT/MR and multi-frame NM)."""
from __future__ import annotations
import datetime as _dt
import hashlib
import json
import uuid
from pathlib import Path

import numpy as np
import pydicom
from PIL import Image

from . import SCHEMA_URI, SPEC_VERSION, __version__
from .adapters import dx_block, family, nm_block, nm_frames
from .context import TEMPLATE_VERSION, build_context
from .deid import age_band, deidentify, hash_uid
from .geometry import derive_orientation, select_spacing
from .render import annotated, canonical_8bit, save_png16
from .validate import validate_manifest

PLAUSIBLE_WIDTH_MM = {"CHEST": (250, 500), "HAND": (80, 300), "SKULL": (150, 300)}


def _str(ds, kw, level="measured"):
    v = ds.get(kw)
    if v in (None, ""):
        return {"value": None, "assertion_level": "unknown"}
    return {"value": str(v), "assertion_level": level}


def _dicom_json(ds: pydicom.Dataset) -> dict:
    d = ds.copy()
    for kw in ("PixelData", "FloatPixelData", "DoubleFloatPixelData"):
        if kw in d:
            del d[kw]
    return d.to_json_dict(bulk_data_threshold=1024, bulk_data_element_handler=lambda e: "<bulk omitted>")


def convert(src: str | Path, out_dir: str | Path, *, external: dict | None = None, title: str | None = None,
            include_original: bool = False, synthetic: bool = False, hints: dict | None = None) -> Path:
    """hints: dataset-level facts used ONLY when the header lacks them (e.g. {"modality": "DX", "body_part": "CHEST",
    "view": "PA"}); they are recorded with assertion_level 'external', never 'measured'."""
    src = Path(src)
    ds = pydicom.dcmread(str(src), force=True)
    hints = hints or {}
    hinted: set[str] = set()
    for kw, hk in (("Modality", "modality"), ("BodyPartExamined", "body_part"), ("ViewPosition", "view"), ("ImageLaterality", "laterality")):
        if hk in hints and not ds.get(kw):
            ds.add_new(pydicom.datadict.tag_for_keyword(kw), pydicom.datadict.dictionary_VR(pydicom.datadict.tag_for_keyword(kw)), hints[hk]); hinted.add(hk)
    arr = ds.pixel_array
    if arr.ndim == 2:
        arr = arr[None, ...]
    elif arr.ndim == 3 and arr.shape[-1] in (3, 4):  # colour single frame -> grey
        arr = np.asarray(Image.fromarray(arr).convert("L"))[None, ...]
    n_frames = arr.shape[0]
    modality = str(ds.get("Modality", "OT"))
    fam = family(modality)
    pkg = Path(out_dir)
    pkg = pkg if pkg.name.endswith(".oip") else pkg.with_name(pkg.name + ".oip")
    for sub in ("renders", "pixels", "derived", "source"):
        (pkg / sub).mkdir(parents=True, exist_ok=True)
    pipeline: list[str] = ["read DICOM with pydicom", "de-identify (PHI tags removed, UIDs hashed, private tags dropped)"]

    # --- L0 identity / provenance / deid
    deid_ds, removed = deidentify(ds)
    sha = hashlib.sha256(src.read_bytes()).hexdigest()
    view = ds.get("ViewPosition")
    view = str(view) if view else None
    if view is None and modality == "NM" and n_frames == 1:
        det = ds.get("DetectorInformationSequence")
        if det and det[0].get("ViewCodeSequence"):
            view = str(det[0].ViewCodeSequence[0].CodeMeaning).upper()
    body = str(ds.get("BodyPartExamined", "")) or None
    title = title or f"{ {'DX':'Radiograph','CR':'Radiograph','NM':'Scintigraphy','CT':'CT slice','MR':'MR slice'}.get(modality, modality)}" + (f", {body.lower()}" if body else "") + (f", {view}" if view else "")

    # --- L1 geometry
    sp = select_spacing(ds)
    rows, cols = int(ds.Rows), int(ds.Columns)
    extent = [rows * sp["spacing"][0], cols * sp["spacing"][1]] if sp["spacing"] else None
    orient = derive_orientation(ds, view)
    if "view" in hinted and orient["assertion_level"] == "inferred":
        orient["note"] += " The view itself came from dataset metadata (external), not from the header."
    flags: list[str] = []
    notes: list[str] = []
    if sp["spacing"] is None:
        flags.append("missing_pixel_spacing")
    elif sp["calibration"]["plane"] == "detector":
        flags.append("spacing_uncalibrated")
    if extent and body and body.upper() in PLAUSIBLE_WIDTH_MM:
        lo, hi = PLAUSIBLE_WIDTH_MM[body.upper()]
        if not (lo <= extent[1] <= hi):
            flags.append("implausible_extent")
            notes.append(f"Expected {body} width {lo}-{hi} mm, computed {extent[1]:.0f} mm from the header spacing; the image was probably resampled after acquisition. Treat mm values as unreliable.")
            sp["calibration"]["confidence"] = "low"
    if orient["assertion_level"] == "inferred":
        flags.append("orientation_inferred")
    if str(ds.get("BurnedInAnnotation", "")).upper() == "YES":
        flags.append("burned_in_annotation")
    if str(ds.get("LossyImageCompression", "")) == "01":
        flags.append("lossy_compression")
    it = [str(x) for x in (ds.get("ImageType") or [])]
    if "DERIVED" in it:
        flags.append("derived_image")
    if n_frames > 1:
        flags.append("multi_frame")
    if modality == "NM":
        flags.append("counts_not_comparable")
    if fam == "other":
        flags.append("unknown_modality")

    # --- L2 renders + pixels
    renders, pix_paths = [], []
    voi_rec, inverted = None, False
    canon0 = None
    for i in range(n_frames):
        u8, voi, steps = canonical_8bit(ds, arr[i])
        if i == 0:
            voi_rec, inverted = {k: v for k, v in voi.items() if not k.startswith("_")}, voi["_inverted"]
            pipeline += steps
            if voi["source"] in ("auto_percentile", "sqrt", "log", "full_range"):
                flags.append("no_voi_in_source")
        ppath = f"pixels/frame-{i:04d}.png"; pix_fmt = save_png16(arr[i], pkg / ppath, int(ds.get("BitsStored", 16))); pix_paths.append(ppath)
        if n_frames == 1:
            rpath = "renders/canonical.png"; canon0 = u8
        else:
            rpath = f"renders/frame-{i:04d}.png"
            if i == 0:
                canon0 = u8
        Image.fromarray(u8).save(pkg / rpath)
        renders.append({"path": rpath, "purpose": "canonical" if n_frames == 1 else "frame", "frame": i,
                        "width": cols, "height": rows, "transform": "; ".join(steps) + "; scaled to 8-bit; no rotation/flip/crop/resample."})
    if n_frames > 1:  # composite canonical: frames side by side
        comp = np.concatenate([np.asarray(Image.open(pkg / r["path"])) for r in renders], axis=1)
        Image.fromarray(comp).save(pkg / "renders/canonical.png")
        renders.append({"path": "renders/canonical.png", "purpose": "composite", "frame": None, "width": comp.shape[1], "height": comp.shape[0],
                        "transform": f"{n_frames} frame renders placed side by side left-to-right in frame order (frame 0 leftmost); each frame keeps its own geometry."})
        canon_for_annot = comp
    else:
        canon_for_annot = canon0
    if modality == "NM":
        inv = 255 - canon_for_annot
        Image.fromarray(inv).save(pkg / "renders/inverted.png")
        renders.append({"path": "renders/inverted.png", "purpose": "inverted", "frame": None, "width": inv.shape[1], "height": inv.shape[0],
                        "transform": "canonical render inverted (hot = dark), the conventional nuclear-medicine display."})
    frames = nm_frames(ds, arr) if modality == "NM" else []
    edge = dict(orient["edge_labels"])
    if n_frames > 1:
        f0 = (frames[0].get("edge_labels") if frames else None) or {}
        edge = {"left": None, "right": None, "top": f0.get("top") or edge.get("top"), "bottom": f0.get("bottom") or edge.get("bottom")}
    frame_labels = None
    if n_frames > 1:
        frame_labels = [{"index": f["index"], "x_offset": f["index"] * cols, "width": cols, "view": f.get("view"),
                         "left": (f.get("edge_labels") or {}).get("left"), "right": (f.get("edge_labels") or {}).get("right")} for f in frames] if frames else \
                       [{"index": i, "x_offset": i * cols, "width": cols, "view": f"frame {i}"} for i in range(n_frames)]
    ann_img, ann_notes = annotated(canon_for_annot, edge, sp["spacing"], f"{title} · OIP {SPEC_VERSION}", frame_labels=frame_labels)
    if n_frames > 1:
        ann_notes.append("frames left-to-right: " + ", ".join(f"{f['index']}={f.get('view') or '?'}" for f in frames))
    ann_img.save(pkg / "renders/annotated.png")
    renders.append({"path": "renders/annotated.png", "purpose": "annotated", "frame": None, "width": ann_img.width, "height": ann_img.height,
                    "transform": "canonical render pasted into a dark margin; image content unchanged and pixel-aligned at the stated offset.",
                    "annotations": ann_notes})
    thumb = Image.fromarray(canon_for_annot); thumb.thumbnail((256, 256)); thumb.save(pkg / "renders/thumbnail.png")
    renders.append({"path": "renders/thumbnail.png", "purpose": "thumbnail", "frame": None, "width": thumb.width, "height": thumb.height,
                    "transform": "canonical render downsampled to fit 256 px; for preview only, not for measurement."})
    pipeline += [f"write lossless {pix_fmt} PNG per frame", "write canonical/annotated/thumbnail renders", "generate context.md", "validate against JSON Schema"]

    # --- intensity
    vals = arr.astype(np.float64)
    units = {"NM": "counts", "CT": "HU", "PT": "Bq/ml"}.get(modality, "relative")
    if modality == "CT" and ds.get("RescaleIntercept") is None:
        units = "unknown"
    intensity = {
        "bits_allocated": int(ds.get("BitsAllocated", 16)), "bits_stored": int(ds.get("BitsStored", ds.get("BitsAllocated", 16))),
        "signed": int(ds.get("PixelRepresentation", 0)) == 1,
        "photometric": str(ds.get("PhotometricInterpretation", "MONOCHROME2")),
        "presentation_lut": str(ds.get("PresentationLUTShape")) if ds.get("PresentationLUTShape") else None,
        "units": units,
        "rescale": {"slope": float(ds.get("RescaleSlope", 1)), "intercept": float(ds.get("RescaleIntercept", 0))},
        "value_range": {"min": float(vals.min()), "max": float(vals.max()), "p0_5": float(np.percentile(vals, 0.5)), "p99_5": float(np.percentile(vals, 99.5))},
        "voi": voi_rec, "canonical_polarity": "high_is_bright", "source_inverted_for_render": inverted,
    }

    lvl = lambda k: "external" if k in hinted else "measured"
    acquisition = {
        "modality": {"value": modality, "assertion_level": lvl("modality")}, "modality_family": fam,
        "body_part": _str(ds, "BodyPartExamined", lvl("body_part")),
        "view": {"value": view, "assertion_level": (lvl("view") if view else "unknown")},
        "laterality": _str(ds, "ImageLaterality", lvl("laterality")) if ds.get("ImageLaterality") else _str(ds, "Laterality"),
        "patient_position": _str(ds, "PatientPosition"),
        "device": {k: v for k, v in {"manufacturer": str(ds.get("Manufacturer", "")) or None, "model": str(ds.get("ManufacturerModelName", "")) or None,
                                     "software": str(ds.get("SoftwareVersions", "")) or None}.items() if v},
        "acquisition_datetime_relative": None,
    }
    if fam == "projection_radiography":
        acquisition["dx"] = dx_block(ds)
    if modality == "NM":
        acquisition["nm"] = nm_block(ds)

    manifest = {
        "oip": {"version": SPEC_VERSION, "profile": "core", "layers": ["L0", "L1", "L2"], "schema": SCHEMA_URI},
        "identity": {"package_id": str(uuid.uuid4()), "created": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"), "title": title,
                     "source_uids": {"study": hash_uid(ds.get("StudyInstanceUID")), "series": hash_uid(ds.get("SeriesInstanceUID")), "instance": hash_uid(ds.get("SOPInstanceUID"))},
                     "source_hash": sha},
        "provenance": {"producer": "oip-python", "producer_version": __version__, "source_format": "dicom", "source_filename": src.name,
                       "image_type": it, "sop_class": str(getattr(ds.get("SOPClassUID"), "name", ds.get("SOPClassUID", ""))), "pipeline": pipeline},
        "subject": {"age_band": age_band(ds.get("PatientAge")), "sex": (str(ds.get("PatientSex")) if str(ds.get("PatientSex", "")) in ("F", "M", "O") else None), "species": "human"},
        "acquisition": acquisition,
        "geometry": {"rows": rows, "columns": cols, "number_of_frames": n_frames, "pixel_spacing_mm": sp["spacing"], "spacing_source": sp["source"],
                     "calibration": sp["calibration"], "physical_extent_mm": extent, "orientation": orient},
        "intensity": intensity,
        "frames": frames,
        "renders": renders,
        "pixels": {"format": pix_fmt, "paths": pix_paths, "lossless": True, "stored_dtype": str(arr.dtype)},
        "derived": {"regions": [], "measurements": [], "measurements_file": "derived/measurements.json"},
        "quality": {"flags": sorted(set(flags)), "notes": notes},
        "deid": {"status": "synthetic" if synthetic else "deidentified", "method": "oip.deid basic profile: PHI keywords removed, UIDs sha256-hashed, private tags dropped, age banded, dates removed",
                 "removed_tag_count": removed, "burned_in_text_checked": False},
        "context": {"path": "context.md", "template_version": TEMPLATE_VERSION},
        "source": {"dicom_headers": "source/dicom-headers.json", "original": "source/original.dcm" if include_original else None},
    }
    if external:
        manifest["external"] = external
        manifest["oip"]["layers"].append("L5")
    errs = validate_manifest(manifest)
    if errs:
        raise ValueError("manifest failed schema validation:\n" + "\n".join(errs))
    (pkg / "source/dicom-headers.json").write_text(json.dumps(_dicom_json(deid_ds), indent=1))
    if include_original:
        (pkg / "source/original.dcm").write_bytes(src.read_bytes())
    (pkg / "derived/measurements.json").write_text("[]\n")
    (pkg / "oip.json").write_text(json.dumps(manifest, indent=2))
    (pkg / "context.md").write_text(build_context(manifest))
    return pkg


def add_measurements(pkg: Path, measurements: list[dict], regions: list[dict] | None = None) -> dict:
    """Attach tool-computed measurements/regions, re-validate, regenerate context.md and annotated render marks."""
    pkg = Path(pkg)
    m = json.loads((pkg / "oip.json").read_text())
    m["derived"]["measurements"] = measurements
    if regions:
        m["derived"]["regions"] = regions
        for L in ("L3",):
            if L not in m["oip"]["layers"]:
                m["oip"]["layers"].append(L)
    if measurements and "L4" not in m["oip"]["layers"]:
        m["oip"]["layers"].append("L4")
    m["oip"]["profile"] = "measured" if "L4" in m["oip"]["layers"] else m["oip"]["profile"]
    m["oip"]["layers"] = sorted(set(m["oip"]["layers"]))
    errs = validate_manifest(m)
    if errs:
        raise ValueError("\n".join(errs))
    if regions:
        canon = np.asarray(Image.open(pkg / "renders/canonical.png"))
        edge = m["geometry"]["orientation"]["edge_labels"] if m["geometry"]["number_of_frames"] == 1 else {"top": m["geometry"]["orientation"]["edge_labels"].get("top"), "bottom": m["geometry"]["orientation"]["edge_labels"].get("bottom")}
        img, notes = annotated(canon, edge, m["geometry"]["pixel_spacing_mm"], f"{m['identity']['title']} · OIP {SPEC_VERSION}", marks=regions)
        img.save(pkg / "renders/annotated.png")
        for r in m["renders"]:
            if r["purpose"] == "annotated":
                r["annotations"] = notes; r["width"], r["height"] = img.width, img.height
    (pkg / "derived/measurements.json").write_text(json.dumps(measurements, indent=2))
    (pkg / "oip.json").write_text(json.dumps(m, indent=2))
    (pkg / "context.md").write_text(build_context(m))
    return m
