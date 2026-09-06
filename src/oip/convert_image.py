"""Non-DICOM adapter: PNG/JPEG + externally supplied metadata -> OIP package.
Everything that comes from a CSV or dataset documentation is marked assertion_level 'external';
what cannot be known is 'unknown' and flagged. Used for NIH ChestX-ray14 (Kaggle PNG + CSV)."""
from __future__ import annotations
import datetime as _dt, hashlib, json, uuid
from pathlib import Path
import numpy as np
from PIL import Image
from . import SCHEMA_URI, SPEC_VERSION, __version__
from .adapters import family
from .context import TEMPLATE_VERSION, build_context
from .deid import age_band
from .geometry import OPPOSITE
from .render import annotated
from .validate import validate_manifest

PLAUSIBLE_WIDTH_MM = {"CHEST": (250, 500), "HAND": (80, 300), "SKULL": (150, 300)}


def convert_image(src: str | Path, out_dir: str | Path, meta: dict, *, title: str | None = None) -> Path:
    """meta keys (all optional): modality, body_part, view, laterality, sex, age (e.g. '060Y'),
    original_size [w, h], original_spacing_mm [x, y], dataset, labels (list), notes (list), manufacturer.
    Spacing for the delivered image is derived from original spacing x (original size / delivered size), per axis."""
    src = Path(src); im = Image.open(src)
    if im.mode not in ("L", "I;16", "I"):
        im = im.convert("L")
    arr = np.asarray(im); rows, cols = arr.shape[:2]
    modality = str(meta.get("modality") or "OT"); fam = family(modality)
    body = meta.get("body_part"); view = meta.get("view")
    pkg = Path(out_dir); pkg = pkg if pkg.name.endswith(".oip") else pkg.with_name(pkg.name + ".oip")
    for sub in ("renders", "pixels", "derived"):
        (pkg / sub).mkdir(parents=True, exist_ok=True)
    flags, notes = ["non_dicom_source"], []
    # geometry: recompute spacing per axis if the image was resized
    spacing = None; source = "none"; cal = dict(plane="unknown", type=None, magnification_factor=None, confidence="none")
    osp, osz = meta.get("original_spacing_mm"), meta.get("original_size")
    if osp and osz:
        fx, fy = osz[0] / cols, osz[1] / rows            # original px per delivered px
        spacing = [round(float(osp[1]) * fy, 4), round(float(osp[0]) * fx, 4)]   # [row, col]
        source = "dataset_metadata"; cal = dict(plane="detector", type=None, magnification_factor=None, confidence="low")
        if abs(fx - fy) / max(fx, fy) > 0.02:
            notes.append(f"Image was resized anisotropically from {osz[0]}x{osz[1]} to {cols}x{rows}: horizontal and vertical scales differ ({spacing[1]} vs {spacing[0]} mm/px). Shapes are distorted; use per-axis spacing.")
    elif osp:
        spacing = [float(osp[1]), float(osp[0])]; source = "dataset_metadata"; cal = dict(plane="detector", type=None, magnification_factor=None, confidence="low")
    if spacing is None:
        flags.append("missing_pixel_spacing")
    else:
        flags.append("spacing_uncalibrated")
    extent = [rows * spacing[0], cols * spacing[1]] if spacing else None
    if extent and body and str(body).upper() in PLAUSIBLE_WIDTH_MM:
        lo, hi = PLAUSIBLE_WIDTH_MM[str(body).upper()]
        if not (lo <= extent[1] <= hi):
            flags.append("implausible_extent"); cal["confidence"] = "low"; notes.append(f"Expected {body} width {lo}-{hi} mm, computed {extent[1]:.0f} mm.")
    if view and str(view).upper() in ("PA", "AP", "ANTERIOR"):
        row, col, lvl, onote = "L", "F", "inferred", f"No orientation metadata; assumed conventional display for view {view} (patient's right on image left)."
    elif view and str(view).upper() == "POSTERIOR":
        row, col, lvl, onote = "R", "F", "inferred", "No orientation metadata; assumed conventional posterior display (mirrored: patient's left on image left)."
    else:
        row = col = None; lvl, onote = "unknown", "Orientation unknown; do not assume laterality."
    orient = dict(row_direction=row, column_direction=col, edge_labels=dict(left=OPPOSITE.get(row) if row else None, right=row, top=OPPOSITE.get(col) if col else None, bottom=col), assertion_level=lvl, note=onote)
    if lvl == "inferred": flags.append("orientation_inferred")
    # pixels + renders (8-bit sources: canonical == stored; assume already MONOCHROME2-like display)
    bits = 16 if arr.dtype == np.uint16 else 8
    Image.fromarray(arr).save(pkg / "pixels/frame-0000.png")
    units = "relative"; counts_note = None; count_step = None
    if fam == "scintigraphy":
        units = "counts"; flags.append("counts_not_comparable")
        nz = np.unique(arr[arr > 0])
        if nz.size > 1:
            k = np.round(nz / float(nz.min()))         # integer count for each distinct value if the image was linearly stretched
            step = float((nz * k).sum() / (k * k).sum())  # least-squares step (the smallest value is rounded, this is not)
            q = nz / step
            if step > 1.5 and np.abs(q - np.round(q)).max() < 0.15 and 20 < arr.max() / step < 65535:
                count_step = round(step, 3)
                counts_note = (f"Stored values are quantised in steps of {step:.1f} (image stretched to full 16-bit range); "
                               f"original photon counts ≈ stored value / {step:.1f} (max ≈ {arr.max()/step:.0f} counts). This recovery is inferred, not measured.")
    if fam == "scintigraphy":
        hi = float(np.percentile(arr[arr > 0], 99.5)) if (arr > 0).any() else float(arr.max())
        u8 = np.clip(np.sqrt(np.clip(arr.astype(np.float64), 0, hi)) / np.sqrt(hi) * 255, 0, 255).astype(np.uint8)
        voi = dict(source="sqrt", center=None, width=None, function=None, lower=0.0, upper=hi); tr = "square-root scaling of counts, clipped at the 99.5th percentile of non-zero pixels, to 8-bit (hot = bright)."
        Image.fromarray(255 - u8).save(pkg / "renders/inverted.png")
    elif bits == 8:
        u8 = arr.astype(np.uint8); voi = dict(source="full_range", center=None, width=None, function=None, lower=0.0, upper=255.0)
        tr = "source is already 8-bit; no window applied; assumed display polarity (bone bright) from the dataset."
    else:
        lo, hi = np.percentile(arr, [0.5, 99.5]); u8 = np.clip((arr - lo) / max(hi - lo, 1) * 255, 0, 255).astype(np.uint8)
        voi = dict(source="auto_percentile", center=None, width=None, function=None, lower=float(lo), upper=float(hi)); tr = "linear window 0.5-99.5 percentile to 8-bit."
    flags.append("no_voi_in_source")
    if counts_note: notes.append(counts_note)
    if rows < 1024 and cols < 1024: flags.append("low_resolution")
    Image.fromarray(u8).save(pkg / "renders/canonical.png")
    title = title or f"{ {'DX':'Radiograph','CR':'Radiograph'}.get(modality, modality)}" + (f", {str(body).lower()}" if body else "") + (f", {view}" if view else "") + " (from PNG)"
    ann, ann_notes = annotated(u8, orient["edge_labels"], spacing, f"{title} · OIP {SPEC_VERSION}")
    ann.save(pkg / "renders/annotated.png")
    th = Image.fromarray(u8); th.thumbnail((256, 256)); th.save(pkg / "renders/thumbnail.png")
    renders = [dict(path="renders/canonical.png", purpose="canonical", frame=0, width=cols, height=rows, transform=tr + " No rotation/flip/crop/resample."),
               *([dict(path="renders/inverted.png", purpose="inverted", frame=0, width=cols, height=rows, transform="canonical render inverted (hot = dark), the conventional nuclear-medicine display.")] if fam == "scintigraphy" else []),
               dict(path="renders/annotated.png", purpose="annotated", frame=None, width=ann.width, height=ann.height, transform="canonical render pasted into a dark margin; image content unchanged and pixel-aligned at the stated offset.", annotations=ann_notes),
               dict(path="renders/thumbnail.png", purpose="thumbnail", frame=None, width=th.width, height=th.height, transform="canonical render downsampled to fit 256 px; preview only.")]
    ext = {k: v for k, v in dict(dataset=meta.get("dataset"), labels=meta.get("labels"), notes=meta.get("notes")).items() if v}
    m = {
        "oip": {"version": SPEC_VERSION, "profile": "core", "layers": ["L0", "L1", "L2"] + (["L5"] if ext else []), "schema": SCHEMA_URI},
        "identity": {"package_id": str(uuid.uuid4()), "created": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"), "title": title,
                     "source_uids": {"study": None, "series": None, "instance": None}, "source_hash": hashlib.sha256(src.read_bytes()).hexdigest()},
        "provenance": {"producer": "oip-python", "producer_version": __version__, "source_format": "png" if src.suffix.lower() == ".png" else "jpeg", "source_filename": src.name,
                       "image_type": ["DERIVED", "SECONDARY"], "pipeline": ["read 8/16-bit image", "derive per-axis spacing from dataset metadata", "write lossless pixels", "write renders", "generate context.md", "validate"]},
        "subject": {"age_band": age_band(meta.get("age")), "sex": meta.get("sex") if meta.get("sex") in ("F", "M", "O") else None, "species": "human"},
        "acquisition": {"modality": {"value": modality, "assertion_level": "external" if meta.get("modality") else "unknown"}, "modality_family": fam,
                        "body_part": {"value": body, "assertion_level": "external" if body else "unknown"},
                        "view": {"value": view, "assertion_level": "external" if view else "unknown"},
                        "laterality": {"value": meta.get("laterality"), "assertion_level": "external" if meta.get("laterality") else "unknown"},
                        "patient_position": {"value": None, "assertion_level": "unknown"},
                        "device": ({"manufacturer": meta["manufacturer"]} if meta.get("manufacturer") else {}), "acquisition_datetime_relative": None},
        "geometry": {"rows": rows, "columns": cols, "number_of_frames": 1, "pixel_spacing_mm": spacing, "spacing_source": source, "calibration": cal, "physical_extent_mm": extent, "orientation": orient},
        "intensity": {"bits_allocated": bits, "bits_stored": bits, "signed": False, "photometric": "MONOCHROME2", "presentation_lut": None, "units": units,
                      "rescale": {"slope": 1.0, "intercept": 0.0}, "value_range": {"min": float(arr.min()), "max": float(arr.max()), "p0_5": float(np.percentile(arr, 0.5)), "p99_5": float(np.percentile(arr, 99.5))},
                      "voi": voi, "canonical_polarity": "high_is_bright", "source_inverted_for_render": False},
        "frames": [], "renders": renders,
        "pixels": {"format": "png16" if bits == 16 else "png8", "paths": ["pixels/frame-0000.png"], "lossless": True, "stored_dtype": str(arr.dtype)},
        "derived": {"regions": [], "measurements": [], "measurements_file": "derived/measurements.json"},
        "quality": {"flags": sorted(set(flags)), "notes": notes},
        "deid": {"status": "deidentified", "method": "source dataset is public and de-identified; no DICOM headers present", "removed_tag_count": 0, "burned_in_text_checked": False},
        "context": {"path": "context.md", "template_version": TEMPLATE_VERSION},
    }
    if fam == "scintigraphy":
        nm = meta.get("nm") or {}
        m["acquisition"]["nm"] = {"image_type": nm.get("image_type"), "radiopharmaceutical": nm.get("radiopharmaceutical"), "radionuclide": nm.get("radionuclide"),
                                  "administered_activity_MBq": {"value": nm.get("administered_activity_MBq"), "unit": "MBq", "assertion_level": "external" if nm.get("administered_activity_MBq") else "unknown"},
                                  "uptake_time_min": {"value": nm.get("uptake_time_min"), "unit": "min", "assertion_level": "external" if nm.get("uptake_time_min") else "unknown"},
                                  "route": nm.get("route"), "energy_windows": nm.get("energy_windows", []), "collimator": nm.get("collimator"), "number_of_detectors": None,
                                  "whole_body": {"technique": None, "scan_length_mm": None, "scan_velocity_mm_per_s": None}, "corrections": [], "termination_condition": None}
        if count_step: m["extensions"] = {"org.openimageprotocol.counts_recovery": {"quantisation_step": count_step, "estimated_max_counts": round(float(arr.max()) / count_step), "assertion_level": "inferred"}}
    if ext: m["external"] = ext
    errs = validate_manifest(m)
    if errs: raise ValueError("\n".join(errs))
    (pkg / "derived/measurements.json").write_text("[]\n"); (pkg / "oip.json").write_text(json.dumps(m, indent=2)); (pkg / "context.md").write_text(build_context(m))
    return pkg


def nih_meta(row: dict, dataset="NIH ChestX-ray14 (Kaggle sample)") -> dict:
    """Map a sample_labels.csv / Data_Entry_2017.csv row to convert_image meta."""
    g = lambda *ks: next((row[k] for k in ks if k in row and row[k] != ""), None)
    labels = [x for x in (g("Finding Labels") or "").split("|") if x]
    return dict(modality="DX", body_part="CHEST", view=g("View Position"), sex=g("Patient Gender"), age=g("Patient Age"),
                original_size=[int(float(g("OriginalImageWidth", "OriginalImage[Width"))), int(float(g("OriginalImageHeight", "Height]")))],
                original_spacing_mm=[float(g("OriginalImagePixelSpacing_x", "OriginalImagePixelSpacing[x")), float(g("OriginalImagePixelSpacing_y", "y]"))],
                dataset=dataset, labels=labels or ["No Finding"], notes=["Labels were extracted from reports by NLP (CheXpert/NegBio style) and are noisy.", "Images are 1024x1024 downsampled PNGs; original DICOM headers are not available."])
