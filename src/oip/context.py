"""Generate context.md, the natural-language reference file, from a manifest (fixed template, section 6 of the spec)."""
from __future__ import annotations

TEMPLATE_VERSION = "0.2.1"   # 0.2.1 (2026-09-29, OEP-002): the estimation caution in "How to read" is on by default (D-031)


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


def _verification_cues(m: dict, fam: str, el: dict, geo: dict, acq: dict) -> list[str]:
    """OEP-004 (template 0.3 draft): pixel cues for the inferred/external facts a reader can check in the image itself.
    The cues name landmarks whose side is fixed by anatomy, so a mirrored image contradicts the stated orientation in a way
    the reader can see; they never restate the answer. Returns markdown bullets for the 'How to read the renders' section."""
    out: list[str] = []
    left, right = el.get("left"), el.get("right")
    view = str((acq.get("view") or {}).get("value") or "").upper()
    body = str((acq.get("body_part") or {}).get("value") or "").upper()
    has_annot = any(r.get("purpose") == "annotated" for r in m.get("renders", []))
    if left not in ("L", "R"):
        return out
    if fam == "projection_radiography" and "CHEST" in body and view in ("PA", "AP"):
        l_edge = "RIGHT" if right == "L" else "LEFT"
        out.append("- Verify the stated orientation against the image before using it: on a frontal chest radiograph the cardiac apex "
                   "and the aortic knob lie on the patient's LEFT, i.e. toward the image edge labelled L (here the " + l_edge + " edge); "
                   "the gastric air bubble, when visible, lies on the same side, and the right hemidiaphragm (liver side) is usually the "
                   "higher one. If these landmarks lie toward the other edge, the image is mirrored relative to this file (or, rarely, "
                   "the patient has dextrocardia): report the disagreement instead of repeating the stated orientation.")
    elif fam == "scintigraphy":
        out.append("- Verify the stated view against the image: in a posterior whole-body view the spine, the scapulae and the kidneys are "
                   "the sharpest structures; in an anterior view the sternum, the anterior ribs and the facial skeleton are. Left and right "
                   "cannot be told reliably from a normal skeleton; an injection-site hot spot on a forearm or a printed marker may identify "
                   "a side. If the view looks different from the stated one, report it instead of repeating the stated orientation.")
    else:
        out.append("- Verify the stated orientation against the image where the anatomy allows it; if the image disagrees, report the "
                   "disagreement instead of repeating the stated orientation.")
    if geo.get("pixel_spacing_mm") and has_annot and fam == "projection_radiography" and "CHEST" in body:
        out.append("- Verify the stated scale: the scale bar on the annotated render represents 50 mm, and an adult thorax measures roughly "
                   "250–350 mm across at its widest, so the bar should fit about five to seven times across the thorax. If it does not, the "
                   "spacing may be wrong: say so rather than reporting sizes derived from it.")
    if has_annot:
        out.append(f"- Verify the printed edge labels on the annotated render against the stated orientation (left = {left}, right = {right}); "
                   "if they differ, report it.")
    return out


def build_context(m: dict, include_external: bool = False, verification_cues: bool = False, low_confidence_guard: bool = False,
                  estimation_caution: bool | None = None) -> str:
    """include_external=False (default, OEP-001): external labels/report text stay in oip.json and are not rendered.
    estimation_caution (OEP-002, adopted as template 0.2.1 on 2026-09-29, D-031; None = template default, i.e. on): one line in
    "How to read" saying that a quantity absent from the measurements table is judged from the picture as a ratio, not computed
    from self-estimated pixel coordinates. Measured on NIH-50 (`docs/reports/oep-002-2026-09-29.md`): it repairs the L0-L2 CTR
    drop on the three Ollama models that show it (glm 26 → 50 %, minimax 32 → 50 %, MedGemma 10 → 18 %) and moves nothing else;
    pass False to render the 0.2 wording (the benchmark's legacy conditions do).
    low_confidence_guard=True (OEP-002 variant a, NOT adopted, D-031): when the calibration confidence is `low`, the scale
    statement and self-check item 3 tell the model not to derive millimetres from the nominal spacing. Measured: three models
    comply fully and lose every correct answer, three comply partly and lose accuracy without abstaining, one ignores it.
    verification_cues=True (OEP-003/OEP-004, template 0.3 draft; off by default until the benchmark has measured it): every
    [inferred] or [external] statement about orientation, view and scale carries a pixel cue to check it against, a 'How to
    use this file' section asks for that check, and the self-check gains items that can be answered only from the image."""
    acq, geo, inten, q = m["acquisition"], m["geometry"], m["intensity"], m["quality"]
    mod = acq["modality"]["value"]; fam = acq.get("modality_family", "other")
    title = m["identity"].get("title", "medical image")
    has_annot = any(r.get("purpose") == "annotated" for r in m.get("renders", []))
    L = []
    L.append(f"# OIP image reference — {title}")
    L.append(f"OIP {m['oip']['version']} · profile `{m['oip']['profile']}` · layers {', '.join(m['oip']['layers'])} · de-identification: {m['deid']['status']}"
             + (" · template 0.3-draft (verification cues)" if verification_cues else "") + "\n")

    if verification_cues:
        L.append("## How to use this file")
        L.append("Statements marked [measured] or [computed] come from the source metadata or from a deterministic tool and can be used as "
                 "given, within their stated confidence. Statements marked [inferred] or [external] are hypotheses, not observations: verify "
                 "each against the image using the cue given with it, and if the image disagrees, say so instead of repeating the statement.")
        L.append("")

    L.append("## What this is")
    fam_txt = {"projection_radiography": "a projection radiograph (X-ray): pixel brightness relates to X-ray attenuation along the beam; the image is a 2D shadow, not a slice.",
               "scintigraphy": "a planar scintigraphy image (nuclear medicine): each pixel is a count of gamma photons emitted by a radiotracer inside the patient; brightness means tracer uptake, not anatomy density.",
               "tomography": "a tomographic slice: each pixel is a reconstructed value in a cross-sectional plane.",
               "other": "a medical image of unspecified physics."}[fam]
    L.append(f"This package describes {fam_txt}")
    VIEW_WORDS = {"PA": "frontal, posteroanterior (PA)", "AP": "frontal, anteroposterior (AP)", "LL": "lateral, left lateral (LL)", "RL": "lateral, right lateral (RL)",
                  "LATERAL": "lateral", "ANTERIOR": "anterior (frontal)", "POSTERIOR": "posterior (from the back, mirrored)"}
    v = acq["view"]; vtxt = f"[{v.get('assertion_level','unknown')}] {VIEW_WORDS.get(str(v.get('value')).upper(), v.get('value')) if v.get('value') else 'unknown'}"
    L.append(f"- Modality: {_a(acq['modality'])} · body part: {_a(acq['body_part'])} · view: {vtxt} · laterality: {_a(acq['laterality'])}")
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
        chk = next((c for c in (q.get("checks") or []) if c.get("id") == "orientation_pixel_check"), None)
        if chk:   # `oip check`: the tool's own pixel-side check of the stated orientation (design rule R4)
            st = (chk.get("evidence") or {}).get("structures") or {}
            named = " and ".join({"heart": "the heart", "aorta": "the aortic arch"}[k] for k in ("heart", "aorta") if k in st) or "the heart"
            off = (st.get("heart") or st.get("aorta") or {}).get("centroid_offset_frac")
            where = f" (centroid {abs(off):.0%} of the thoracic width from the midline; {chk['tool']} {chk['tool_version']})" if off is not None else f" ({chk['tool']} {chk['tool_version']})"
            if chk["result"] == "consistent":
                L.append(f"- Orientation cross-checked against the pixels [computed]: CONSISTENT, {named} lie{'s' if ' and ' not in named else ''} toward the edge labelled L{where}.")
            elif chk["result"] == "inconsistent":
                L.append(f"- Orientation cross-checked against the pixels [computed]: INCONSISTENT, {named} lie{'s' if ' and ' not in named else ''} toward the edge labelled R{where}. "
                         "The stated left/right or the image may be mirrored: do not rely on the stated orientation, and say so when asked about sides.")
            else:
                L.append(f"- Orientation cross-checked against the pixels [computed]: indeterminate ({chk.get('reason', 'no usable evidence')}; {chk['tool']} {chk['tool_version']}). The stated orientation stands unverified.")
    else:
        L.append("- Orientation [unknown]: do not assume which side is the patient's left or right.")
    if geo["pixel_spacing_mm"]:
        sp = geo["pixel_spacing_mm"]; cal = geo["calibration"]
        L.append(f"- Scale [{'measured' if geo['spacing_source']!='dataset_metadata' else 'external'}]: {sp[0]:g} × {sp[1]:g} mm per pixel (row × column), source `{geo['spacing_source']}`, valid in the {cal['plane']} plane, confidence {cal['confidence']}. Image extent ≈ {geo['physical_extent_mm'][0]:.0f} × {geo['physical_extent_mm'][1]:.0f} mm (height × width)."
                 + (" Anatomy is magnified relative to the detector; absolute sizes may be over-estimated by roughly 5–10 % unless corrected." if cal["plane"] == "detector" and fam == "projection_radiography" else "")
                 + (" Planar gamma-camera images have no geometric magnification, but resolution is coarse (several mm) and the pixel size here is not from the header." if fam == "scintigraphy" and geo["spacing_source"] in ("dataset_metadata",) else ""))
        if low_confidence_guard and cal.get("confidence") == "low":
            L.append("- LOW-CONFIDENCE SCALE: the spacing above is nominal (dataset documentation or an uncalibrated tag, not a calibrated header value) and may be wrong by a large factor. "
                     "Do NOT derive sizes in millimetres from it yourself. If a size in mm is listed under `Computed measurements`, report that value; otherwise give sizes in pixels or as ratios and say that no calibrated scale is available.")
    else:
        L.append("- Scale [unknown]: NO pixel spacing is available. Do not state sizes in mm or cm; use pixels or ratios only.")
    if estimation_caution is None or estimation_caution:
        L.append("- Estimating from the image: for a quantity that is not listed under `Computed measurements`, judge it directly from the picture (a ratio or a size relative to the thorax); "
                 "do not compute it from pixel coordinates you estimate yourself, because such coordinate estimates are unreliable.")
    L.append(f"- Pixel values: {inten['bits_stored']}-bit stored, units `{inten['units']}`; window for the canonical render: {inten['voi'].get('source')}"
             + (f" (center {inten['voi'].get('center'):g}, width {inten['voi'].get('width'):g})" if inten['voi'].get('center') is not None else "")
             + (f" (range {inten['voi'].get('lower'):.4g}–{inten['voi'].get('upper'):.4g})" if inten['voi'].get('lower') is not None else "") + ".")
    if verification_cues:
        L.extend(_verification_cues(m, fam, el, geo, acq))
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

    L.append("## Unknowns and cautions")
    caut = []
    flag_txt = {"missing_pixel_spacing": "no pixel spacing: never report sizes in mm",
                "spacing_uncalibrated": "spacing is at the detector plane; anatomy magnified ~5–10 %",
                "implausible_extent": "computed physical extent is outside the expected anatomical range; spacing may be wrong",
                "burned_in_annotation": "source declares burned-in annotation (possible text/PHI in pixels)",
                "lossy_compression": "source was lossy-compressed",
                "orientation_inferred": "left/right labels are inferred from the view, not read from the header",
                "orientation_pixel_inconsistent": "the pixel check contradicts the stated left/right (heart toward the edge labelled R): the image or the labels may be mirrored",
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

    L.append("## External context")
    ext = (m.get("external") or {}) if include_external else {}
    if ext:
        L.append("UNVERIFIED information from outside the image (dataset files, prior reports). Such labels are wrong in a substantial fraction of cases. Do not repeat any of it unless the pixels clearly show it; if the image does not support a statement below, say so explicitly.")
        if ext.get("dataset"):
            L.append(f"- Dataset: {ext['dataset']}")
        if ext.get("labels"):
            L.append(f"- Dataset labels [external, UNVERIFIED]: {', '.join(ext['labels'])}")
        if ext.get("report_text"):
            L.append(f"- Report text [external, UNVERIFIED]: {ext['report_text']}")
        for n in ext.get("notes", []):
            L.append(f"- Note [external]: {n}")
    else:
        L.append("Not rendered by default (OEP-001). External labels or report text, if any, are in `oip.json` under `external`; they are unverified and must not be repeated unless the pixels support them.")
    L.append("")

    L.append("## Self-check")
    L.append("Before answering questions about this image, confirm you can answer these from the package:")
    if verification_cues:
        L.append(f"1. Which anatomical side does this file state for the image's left edge? → {el.get('left') or 'unknown'}")
    else:
        L.append(f"1. Which anatomical side is on the image's left edge? → {el.get('left') or 'unknown'}")
    L.append(f"2. What is the modality? → {mod}")
    if low_confidence_guard and geo["pixel_spacing_mm"] and geo["calibration"].get("confidence") == "low":
        has_mm = any(x.get("unit") == "mm" for x in ((m.get("derived") or {}).get("measurements") or []))
        L.append("3. Can sizes be given in mm? → " + ("only the values listed under `Computed measurements` (spacing confidence low); do not compute mm yourself" if has_mm else "no (the spacing is nominal, confidence low); use pixels or ratios"))
    else:
        L.append(f"3. Can sizes be given in mm? → {'yes, ' + str(geo['pixel_spacing_mm'][1]) + ' mm/px (column)' if geo['pixel_spacing_mm'] else 'no'}")
    L.append(f"4. Is bright = high {'counts' if fam=='scintigraphy' else 'attenuation'} in the canonical render? → yes")
    if verification_cues and el.get("left") in ("L", "R"):
        # OEP-004: items 5 and 6 have no answer in this file; they are answered from the image and compared with item 1.
        if fam == "projection_radiography":
            L.append("5. Look at the image, not the file: on which image side is the cardiac apex? It should point toward the edge labelled L. "
                     "Does that agree with item 1? If not, the image is mirrored relative to this file: report it.")
        else:
            L.append("5. Look at the image, not the file: do the view (which structures are sharpest) and any side marker agree with item 1? "
                     "If not, report it.")
        if has_annot:
            L.append(f"6. On the annotated render, do the printed edge labels read left = {el.get('left')}, right = {el.get('right')}? If not, report it.")   # OEP-003
    L.append("")
    L.append("## Machine-readable")
    L.append(f"- Manifest: `oip.json` (schema {m['oip'].get('schema','')}). Lossless pixels: `{(m.get('pixels') or {}).get('paths', ['pixels/'])[0]}`.")
    if m.get("source", {}).get("dicom_headers"):
        L.append(f"- De-identified DICOM headers (DICOM JSON model): `{m['source']['dicom_headers']}`.")
    return "\n".join(L) + "\n"
