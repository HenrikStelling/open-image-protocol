# Q5 — How do we extract information from an X-ray or a scintigraphy image so that AI actually understands it?

## Principle
Split "understanding" into four sub-problems and solve each with the right tool.
The model is only responsible for the last one.

| Sub-problem | Who solves it | How |
|---|---|---|
| A. What is this? (modality, body part, view, tracer) | Converter (deterministic) | DICOM tags (Q4); fallback: dataset CSV; last resort: a classifier with `assertion_level = inferred` |
| B. What does a pixel mean? (units, polarity, window, mm) | Converter | Modality LUT → units; VOI LUT → 8-bit render; MONOCHROME1 inversion; spacing selection with trust level |
| C. Where are things? (anatomy, regions) | Segmentation/landmark tools | CXR: CheXmask-style HybridGNet (heart, lungs), CXAS (157 anatomical classes), MedSAM/SAM-Med2D for interactive masks. NM: body-region templates (skeleton regions on whole-body bone scans), ROI templates for organ studies |
| D. What does it mean? (findings, interpretation) | The model, reading the package | Canonical render + annotated render + `context.md` + measurements; benchmark tells us how well |

## X-ray (CR/DX) extraction pipeline
1. **Parse** with pydicom; keep a DICOM JSON dump (de-identified).
2. **Pixels → units**: `apply_modality_lut` (rescale). For DX the unit is
   "relative attenuation" (no absolute unit); record `intensity.units = relative`.
3. **Polarity**: if `PhotometricInterpretation == MONOCHROME1` or
   `PresentationLUTShape == INVERSE`, invert so that bone is bright (MONOCHROME2
   convention). Record this in `renders[].transform`.
4. **Window**: apply VOI LUT (`WindowCenter/Width` or `VOILUTSequence`); if none,
   use robust percentiles (0.5–99.5 %) and say so (`voi.source = auto_percentile`).
5. **Geometry**: choose spacing (Q6), compute physical extent, plausibility check
   (a chest should be ~300–450 mm wide).
6. **Orientation**: from `PatientOrientation` when present; otherwise from view +
   convention (PA/AP frontal: image left = patient right), with
   `assertion_level = inferred` and a caution in `context.md`.
7. **Anatomy**: run lung/heart segmentation (CheXmask-type model) → masks +
   bounding boxes; compute CTR, lung areas, mediastinal width (Q6).
8. **Renders**: canonical PNG; annotated PNG with scale bar (e.g. 50 mm),
   R/L labels at the correct image sides, optional numbered region marks.
9. **Context**: generate `context.md` from the manifest.

## Scintigraphy (planar NM) extraction pipeline
1. **Parse frames** using `DetectorVector`, `ViewCodeSequence` (anterior /
   posterior), `ActualFrameDuration`, `CountsAccumulated`.
2. **Units are counts** (`Units = CNTS`), not attenuation. Intensity is relative
   to dose, uptake time, frame duration, collimator and energy window. The
   converter records all of them and `context.md` states explicitly:
   "brightness = counts; only compare within the same study/window".
3. **Render**: counts are heavy-tailed; canonical render uses a percentile window
   (e.g. 0–99.5 %) or a log/sqrt transform, recorded in `transform`. Bone scans
   are conventionally shown *inverted* (hot = black); OIP canonical render keeps
   hot = bright and offers an `inverted` render because models see many inverted
   bone scans in training data.
4. **Layout**: whole-body scans are tall (e.g. 256×1024). The annotated render
   places anterior and posterior side by side with labels, since whole-body
   posterior views are mirrored relative to anterior.
5. **Regions**: skeletal region template (skull, spine segments, ribs, pelvis,
   femora…) via atlas registration or a segmentation model trained on BS-80K-like
   data; per-region counts, count densities, and anterior/posterior geometric mean.
6. **Metrics**: Q6.
7. **Context**: tracer, dose (MBq) decay-corrected to acquisition, uptake time,
   energy window, cautions.

## Making sure the AI *actually* understands
- Test, don't assume: OIP-Bench (Q12) asks the model to answer questions whose
  ground truth is in the package (modality, side, scale, CTR) and questions that
  require the pixels (findings), with vs without the package.
- Keep the render honest: never upscale, never crop silently, always show
  orientation labels, and keep aspect ratio (whole-body scans letterboxed).

## What OIP does about it
`src/oip/convert.py` implements steps 1–6, 8, 9 for X-ray and 1–4, 7 for NM in
v0 (anatomy models are Phase 2). The pipeline order and each decision are
recorded in the manifest so the model can see how the image was prepared.
