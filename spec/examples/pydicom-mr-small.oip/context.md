# OIP image reference — MR slice
OIP 0.1.0 · profile `core` · layers L0, L1, L2 · de-identification: deidentified

## What this is
This package describes a tomographic slice: each pixel is a reconstructed value in a cross-sectional plane.
- Modality: [measured] MR · body part: [unknown] unknown · view: [unknown] unknown · laterality: [unknown] unknown
- Subject (de-identified): age band unknown, sex F

## How to read the renders
- `renders/canonical.png` (canonical): apply Modality LUT / RescaleSlope+Intercept; apply VOI (WindowCenterWidth); scaled to 8-bit; no rotation/flip/crop/resample.
- `renders/annotated.png` (annotated): canonical render pasted into a dark margin; image content unchanged and pixel-aligned at the stated offset. Annotations: margin_offset_px: 40 (subtract from annotated coords to get frame coords); edge labels: ; scale bar: 50 mm = 160 px, bottom-left.
- `renders/thumbnail.png` (thumbnail): canonical render downsampled to fit 256 px; for preview only, not for measurement.
- Polarity guarantee: in the canonical render, higher attenuation is BRIGHTER.
- Orientation [unknown]: do not assume which side is the patient's left or right.
- Scale [measured]: 0.3125 × 0.3125 mm per pixel (row × column), source `PixelSpacing`, valid in the patient plane, confidence high. Image extent ≈ 20 × 20 mm (height × width).
- Pixel values: 16-bit stored, units `relative`; window for the canonical render: WindowCenterWidth (center 600, width 1600).

## Measured facts
Facts read directly from the source metadata (assertion: measured).
- Image size: 64 rows × 64 columns.
- Pixel spacing: 0.3125 × 0.3125 mm (PixelSpacing).
- Device: TOSHIBA_MEC MRT50H1.
- DICOM ImageType: DERIVED / SECONDARY / OTHER.

## Computed measurements
None. (Measurements, when present, are computed by deterministic tools, not by a model.)

## Inferred
None.

## Unknowns and cautions
- source is a DERIVED image (already processed)

## External context
Not rendered by default (OEP-001). External labels or report text, if any, are in `oip.json` under `external`; they are unverified and must not be repeated unless the pixels support them.

## Self-check
Before answering questions about this image, confirm you can answer these from the package:
1. Which anatomical side is on the image's left edge? → unknown
2. What is the modality? → MR
3. Can sizes be given in mm? → yes, 0.3125 mm/px (column)
4. Is bright = high attenuation in the canonical render? → yes

## Machine-readable
- Manifest: `oip.json` (schema https://open-image-protocol.org/schemas/0.1/oip-manifest.schema.json). Lossless pixels: `pixels/frame-0000.png`.
- De-identified DICOM headers (DICOM JSON model): `source/dicom-headers.json`.
