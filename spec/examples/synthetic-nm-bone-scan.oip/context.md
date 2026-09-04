# OIP image reference — Synthetic whole-body bone scintigraphy phantom (anterior + posterior)
OIP 0.1.0 · profile `core` · layers L0, L1, L2 · de-identification: synthetic

## What this is
This package describes a planar scintigraphy image (nuclear medicine): each pixel is a count of gamma photons emitted by a radiotracer inside the patient; brightness means tracer uptake, not anatomy density.
- Modality: [measured] NM · body part: [measured] WHOLEBODY · view: [unknown] unknown · laterality: [unknown] unknown
- Subject (de-identified): age band 45-49, sex O
- Tracer: Tc-99m MDP (Technetium Tc-99m), administered activity [measured] 740 MBq, uptake time [computed] 180 min
- Energy windows: Tc-99m photopeak 126–154 keV
- Acquisition type: WHOLE BODY; collimator: PARA; corrections applied: UNIF, DECY
- Frames: 2 — frame 0: view ANTERIOR, 9e+05 ms, 6.262e+05 counts; frame 1: view POSTERIOR, 9e+05 ms, 5.633e+05 counts
  - frame 0 orientation [measured]: image LEFT edge = R, RIGHT edge = L, TOP = H, BOTTOM = F.
  - frame 1 orientation [measured]: image LEFT edge = L, RIGHT edge = R, TOP = H, BOTTOM = F. Posterior view: patient's LEFT appears on the image LEFT (mirrored relative to anterior).

## How to read the renders
- `renders/frame-0000.png` (frame): apply Modality LUT / RescaleSlope+Intercept; no VOI in source; sqrt scaling, clipped at 99.5th percentile; scaled to 8-bit; no rotation/flip/crop/resample.
- `renders/frame-0001.png` (frame): apply Modality LUT / RescaleSlope+Intercept; no VOI in source; sqrt scaling, clipped at 99.5th percentile; scaled to 8-bit; no rotation/flip/crop/resample.
- `renders/canonical.png` (composite): 2 frame renders placed side by side left-to-right in frame order (frame 0 leftmost); each frame keeps its own geometry.
- `renders/inverted.png` (inverted): canonical render inverted (hot = dark), the conventional nuclear-medicine display.
- `renders/annotated.png` (annotated): canonical render pasted into a dark margin; image content unchanged and pixel-aligned at the stated offset. Annotations: margin_offset_px: 61 (subtract from annotated coords to get frame coords); edge labels: top=H, bottom=F; frame 0 (ANTERIOR): x-offset 0 px, left edge=R, right edge=L; frame 1 (POSTERIOR): x-offset 256 px, left edge=L, right edge=R; scale bar: 50 mm = 22 px, bottom-left; frames left-to-right: 0=ANTERIOR, 1=POSTERIOR.
- `renders/thumbnail.png` (thumbnail): canonical render downsampled to fit 256 px; for preview only, not for measurement.
- Polarity guarantee: in the canonical render, higher counts is BRIGHTER.
- Orientation [unknown]: do not assume which side is the patient's left or right.
- Scale [measured]: 2.26 × 2.26 mm per pixel (row × column), source `PixelSpacing`, valid in the detector plane, confidence medium. Image extent ≈ 2314 × 579 mm (height × width). Anatomy is magnified relative to the detector; absolute sizes may be over-estimated by roughly 5–10 % unless corrected.
- Pixel values: 16-bit stored, units `counts`; window for the canonical render: sqrt (range 0–22).

## Measured facts
Facts read directly from the source metadata (assertion: measured).
- Image size: 1024 rows × 256 columns, 2 frames.
- Pixel spacing: 2.26 × 2.26 mm (PixelSpacing).
- Device: OIP synthetic phantom-v1.
- DICOM ImageType: ORIGINAL / PRIMARY / WHOLE BODY / EMISSION.

## Computed measurements
None. (Measurements, when present, are computed by deterministic tools, not by a model.)
Counts caution: pixel values are photon counts; compare them only within this package and the same energy window; normalise by frame duration (counts/s) before any ratio.

## Inferred
None.

## External context
None. Statements in this section, when present, come from outside the image and must be verified against the pixels.

## Unknowns and cautions
- counts depend on dose, uptake time, duration and window
- multiple frames; read frames[] before comparing views
- no display window in the source; the render window is automatic
- spacing is at the detector plane; anatomy magnified ~5–10 %

## Self-check
Before answering questions about this image, confirm you can answer these from the package:
1. Which anatomical side is on the image's left edge? → unknown
2. What is the modality? → NM
3. Can sizes be given in mm? → yes, 2.26 mm/px (column)
4. Is bright = high counts in the canonical render? → yes

## Machine-readable
- Manifest: `oip.json` (schema https://open-image-protocol.org/schemas/0.1/oip-manifest.schema.json). Lossless pixels: `pixels/frame-0000.png`.
- De-identified DICOM headers (DICOM JSON model): `source/dicom-headers.json`.
