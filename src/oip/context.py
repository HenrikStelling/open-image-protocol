"""Generate context.md, the natural-language reference file, from a manifest (fixed template, section 6 of the spec)."""
from __future__ import annotations

TEMPLATE_VERSION = "0.1"


def _fmt(v, unit=""):
    if v is None:
        return "unknown"
    if isinstance(v, float):
        v = f"{v:.4g}"
    return f"{v} {unit}".strip()


def _a(x: dict, unit_key="unit"):
    """asserted value -> '[level] value unit'"""
    if not isinstance(x, dict):
        return _fmt(x)
    return f"[{x.get('assertion_level','unknown')}] {_fmt(x.get('value'), x.get(unit_key, ''))}"


def build_context(m: dict) -> str:
    acq, geo, inten, q = m["acquisition"], m["geometry"], m["intensity"], m["quality"]
    mod = acq["modality"]["value"]; fam = acq.get("modality_family", "other")
    title = m["identity"].get("title", "medical image")
    L = []
    L.append(f"# OIP image reference — {title}")
    L.append(f"OIP {m['oip']['version']} · profile `{m['oip']['profile']}` · layers {', '.join(m['oip']['layers'])} · de-identification: {m['deid']['status']}\n")

    L.append("## What this is")
    fam_txt = {"projection_radiography": "a projection radiograph (X-ray): pixel brightness relates to X-ray attenuation along the beam; the image is a 2D shadow, not a slice.",
               "scintigraphy": "a planar scintigraphy image (nuclear medicine): each pixel is a count of gamma photons emitted by a radiotracer inside the patient; brightness means tracer uptake, not anatomy density.",
               "tomography": "a tomographic slice: each pixel is a reconstructed value in a cross-sectional plane.",
               "other": "a medical image of unspecified physics."}[fam]
    L.append(f"This package describes {fam_txt}")
    L.append(f"- Modality: {_a(acq['modality'])} · body part: {_a(acq['body_part'])} · view: {_a(acq['view'])} · laterality: {_a(acq['laterality'])}")
    if m.get("subject"):
        L.append(f"- Subject (de-identified): age band {m['subject'].get('age_band') or 'unknown'}, sex {m['subject'].get('sex') or 'unknown'}")
    if fam == "scintigraphy" and acq.get("nm"):
        nm = acq["nm"]
        L.append(f"- Tracer: {nm.get('radiopharmaceutical') or 'unknown'} ({nm.get('radionuclide') or 'radionuclide unknown'}), administered activity {_a(nm['administered_activity_MBq'])}, uptake time {_a(nm['uptake_time_min'])}")
        if nm.get("energy_windows"):
            L.append("- Energy windows: " + "; ".join(f"{w['name']} {w['lower_keV']:g}–{w['upper_keV']:g} keV" for w in nm["energy_windows"]))
        L.append(f"- Acquisition type: {nm.get('image_type') or 'unknown'}; collimator: {nm.get('collimator') or 'unknown'}; corrections applied: {', '.join(nm.get('corrections') or []) or 'none recorded'}")
    if fam == "projection_radiography" and acq.get("dx"):
        dx = acq["dx"]
        L.append(f"- Technique: {_a(dx['kvp'])}, {_a(dx['exposure_mAs'])}, source-to-detector {_a(dx['distance_source_to_detector_mm'])}")
    if m.get("frames"):
        L.append(f"- Frames: {len(m['frames'])} — " + "; ".join(f"frame {f['index']}: view {f.get('view') or 'unknown'}, {_fmt(f.get('duration_ms'),'ms')}, {_fmt(f.get('counts_total'))} counts" for f in m["frames"]))
        for f in m["frames"]:
            e = f.get("edge_labels") or {}
            if e.get("left"):
                L.append(f"  - frame {f['index']} orientation [{f.get('edge_labels_assertion','unknown')}]: image LEFT edge = {e['left']}, RIGHT edge = {e['right']}, TOP = {e.get('top')}, BOTTOM = {e.get('bottom')}." + (f" {f['orientation_note']}" if f.get('orientation_note') else ""))
    L.append("")

    L.append("## How to read the renders")
    for r in m["renders"]:
        L.append(f"- `{r['path']}` ({r['purpose']}): {r['transform']}" + (f" Annotations: {'; '.join(r.get('annotations', []))}." if r.get("annotations") else ""))
    L.append(f"- Polarity guarantee: in the canonical render, higher {'counts' if fam=='scintigraphy' else 'attenuation'} is BRIGHTER" + (" (the source was stored inverted and has been corrected)." if inten.get("source_inverted_for_render") else "."))
    o = geo["orientation"]; el = o.get("edge_labels", {})
    if o["assertion_level"] != "unknown":
        L.append(f"- Orientation [{o['assertion_level']}]: image LEFT edge = {el.get('left')}, RIGHT edge = {el.get('right')}, TOP = {el.get('top')}, BOTTOM = {el.get('bottom')}. {o.get('note','')}")
    else:
        L.append("- Orientation [unknown]: do not assume which side is the patient's left or right.")
    if geo["pixel_spacing_mm"]:
        sp = geo["pixel_spacing_mm"]; cal = geo["calibration"]
        L.append(f"- Scale [{'measured' if geo['spacing_source']!='dataset_metadata' else 'external'}]: {sp[0]:g} × {sp[1]:g} mm per pixel (row × column), source `{geo['spacing_source']}`, valid in the {cal['plane']} plane, confidence {cal['confidence']}. Image extent ≈ {geo['physical_extent_mm'][0]:.0f} × {geo['physical_extent_mm'][1]:.0f} mm (height × width)."
                 + (" Anatomy is magnified relative to the detector; absolute sizes may be over-estimated by roughly 5–10 % unless corrected." if cal["plane"] == "detector" and fam == "projection_radiography" else "")
                 + (" Planar gamma-camera images have no geometric magnification, but resolution is coarse (several mm) and the pixel size here is not from the header." if fam == "scintigraphy" and geo["spacing_source"] in ("dataset_metadata",) else ""))
    else:
        L.append("- Scale [unknown]: NO pixel spacing is available. Do not state sizes in mm or cm; use pixels or ratios only.")
    L.append(f"- Pixel values: {inten['bits_stored']}-bit stored, units `{inten['units']}`; window for the canonical render: {inten['voi'].get('source')}"
             + (f" (center {inten['voi'].get('center'):g}, width {inten['voi'].get('width'):g})" if inten['voi'].get('center') is not None else "")
             + (f" (range {inten['voi'].get('lower'):.4g}–{inten['voi'].get('upper'):.4g})" if inten['voi'].get('lower') is not None else "") + ".")
    L.append("")

    L.append("## Measured facts")
    L.append("Facts read directly from the source metadata (assertion: measured).")
    L.append(f"- Image size: {geo['rows']} rows × {geo['columns']} columns" + (f", {geo.get('number_of_frames',1)} frames" if geo.get('number_of_frames',1) > 1 else "") + ".")
    if geo["pixel_spacing_mm"] and geo["spacing_source"] != "dataset_metadata":
        L.append(f"- Pixel spacing: {geo['pixel_spacing_mm'][0]:g} × {geo['pixel_spacing_mm'][1]:g} mm ({geo['spacing_source']}).")
    dev = acq.get("device") or {}
    if dev.get("manufacturer"):
        L.append(f"- Device: {dev.get('manufacturer')} {dev.get('model') or ''}".rstrip() + ".")
    if m["provenance"].get("image_type"):
        L.append(f"- DICOM ImageType: {' / '.join(m['provenance']['image_type'])}.")
    L.append("")

    L.append("## Computed measurements")
    meas = (m.get("derived") or {}).get("measurements") or []
    if meas:
        L.append("| id | name | value | unit | method | confidence | validation |")
        L.append("|---|---|---|---|---|---|---|")
        for x in meas:
            L.append(f"| {x['id']} | {x['name']} | {_fmt(x['value'])} | {x['unit']} | {x['method']} | {x.get('confidence','–')} | {x['validation_status']} |")
    else:
        L.append("None. (Measurements, when present, are computed by deterministic tools, not by a model.)")
    if fam == "scintigraphy":
        L.append("Counts caution: pixel values are photon counts; compare them only within this package and the same energy window; normalise by frame duration (counts/s) before any ratio.")
    L.append("")

    L.append("## Inferred")
    regs = (m.get("derived") or {}).get("regions") or []
    inf = [r for r in regs if r.get("assertion_level") == "inferred"]
    if o["assertion_level"] == "inferred":
        L.append(f"- Orientation was inferred: {o.get('note')}")
    for r in inf:
        L.append(f"- Region `{r['id']}` = {r['label']} (mark {r.get('mark','–')}, tool {r.get('tool','?')}, confidence {r.get('confidence','?')})")
    if not inf and o["assertion_level"] != "inferred":
        L.append("None.")
    L.append("")

    L.append("## External context")
    ext = m.get("external") or {}
    if ext:
        if ext.get("dataset"):
            L.append(f"- Dataset: {ext['dataset']}")
        if ext.get("labels"):
            L.append(f"- Dataset labels [external — verify against the pixels]: {', '.join(ext['labels'])}")
        if ext.get("report_text"):
            L.append(f"- Report text [external — verify against the pixels]: {ext['report_text']}")
        for n in ext.get("notes", []):
            L.append(f"- Note [external]: {n}")
    else:
        L.append("None. Statements in this section, when present, come from outside the image and must be verified against the pixels.")
    L.append("")

    L.append("## Unknowns and cautions")
    caut = []
    flag_txt = {"missing_pixel_spacing": "no pixel spacing: never report sizes in mm",
                "spacing_uncalibrated": "spacing is at the detector plane; anatomy magnified ~5–10 %",
                "implausible_extent": "computed physical extent is outside the expected anatomical range; spacing may be wrong",
                "burned_in_annotation": "source declares burned-in annotation (possible text/PHI in pixels)",
                "lossy_compression": "source was lossy-compressed",
                "orientation_inferred": "left/right labels are inferred from the view, not read from the header",
                "no_voi_in_source": "no display window in the source; the render window is automatic",
                "derived_image": "source is a DERIVED image (already processed)",
                "multi_frame": "multiple frames; read frames[] before comparing views",
                "low_resolution": "image resolution is low for fine detail",
                "non_dicom_source": "source was not DICOM; metadata is from dataset documentation",
                "counts_not_comparable": "counts depend on dose, uptake time, duration and window",
                "unknown_modality": "modality could not be determined"}
    for fl in q.get("flags", []):
        caut.append(f"- {flag_txt.get(fl, fl)}")
    for n in q.get("notes", []):
        caut.append(f"- {n}")
    if fam == "projection_radiography":
        caut.append("- A radiograph is a projection: overlapping structures superimpose; depth cannot be measured.")
    L.extend(caut or ["- None recorded."])
    L.append("")

    L.append("## Self-check")
    L.append("Before answering questions about this image, confirm you can answer these from the package:")
    L.append(f"1. Which anatomical side is on the image's left edge? → {el.get('left') or 'unknown'}")
    L.append(f"2. What is the modality? → {mod}")
    L.append(f"3. Can sizes be given in mm? → {'yes, ' + str(geo['pixel_spacing_mm'][1]) + ' mm/px (column)' if geo['pixel_spacing_mm'] else 'no'}")
    L.append(f"4. Is bright = high {'counts' if fam=='scintigraphy' else 'attenuation'} in the canonical render? → yes")
    L.append("")
    L.append("## Machine-readable")
    L.append(f"- Manifest: `oip.json` (schema {m['oip'].get('schema','')}). Lossless pixels: `{(m.get('pixels') or {}).get('paths', ['pixels/'])[0]}`.")
    if m.get("source", {}).get("dicom_headers"):
        L.append(f"- De-identified DICOM headers (DICOM JSON model): `{m['source']['dicom_headers']}`.")
    return "\n".join(L) + "\n"
