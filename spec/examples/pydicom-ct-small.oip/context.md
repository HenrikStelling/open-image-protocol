# OIP image reference — CT slice
OIP 0.1.0 · profile `core` · layers L0, L1, L2 · de-identification: deidentified

## What this is
This package describes a tomographic slice: each pixel is a reconstructed value in a cross-sectional plane.
- Modality: [measured] CT · body part: [unknown] unknown · view: [unknown] unknown · laterality: [unknown] unknown
- Subject (de-identified): age band 0-4, sex O

## How to read the renders
- `renders/canonical.png` (canonical): apply Modality LUT / RescaleSlope+Intercept; no VOI in source; linear window between 0.5th and 99.5th percentile; scaled to 8-bit; no rotation/flip/crop/resample.
- `renders/annotated.png` (annotated): canonical render pasted into a dark margin; image content unchanged and pixel-aligned at the stated offset. Annotations: margin_offset_px: 40 (subtract from annotated coords to get frame coords); edge labels: ; scale bar: 50 mm = 76 px, bottom-left.
- `renders/thumbnail.png` (thumbnail): canonical render downsampled to fit 256 px; for preview only, not for measurement.
- Polarity guarantee: in the canonical render, higher attenuation is BRIGHTER.
- Orientation [unknown]: do not assume which side is the patient's left or right.
- Scale [measured]: 0.661468 × 0.661468 mm per pixel (row × column), source `PixelSpacing`, valid in the patient plane, confidence high. Image extent ≈ 85 × 85 mm (height × width).
- Pixel values: 16-bit stored, units `HU`; window for the canonical render: auto_percentile (range -861–785).

## Measured facts
Facts read directly from the source metadata (assertion: measured).
- Image size: 128 rows × 128 columns.
- Pixel spacing: 0.661468 × 0.661468 mm (PixelSpacing).
- Device: GE MEDICAL SYSTEMS RHAPSODE.
- DICOM ImageType: ORIGINAL / PRIMARY / AXIAL.

## Computed measurements
None. (Measurements, when present, are computed by deterministic tools, not by a model.)

## Inferred
None.

## Unknowns and cautions
- no display window in the source; the render window is automatic

## External context
Not rendered by default (OEP-001). External labels or report text, if any, are in `oip.json` under `external`; they are unverified and must not be repeated unless the pixels support them.

## Self-check
Before answering questions about this image, confirm you can answer these from the package:
1. Which anatomical side is on the image's left edge? → unknown
2. What is the modality? → CT
3. Can sizes be given in mm? → yes, 0.661468 mm/px (column)
4. Is bright = high attenuation in the canonical render? → yes

## Machine-readable
- Manifest: `oip.json` (schema https://open-image-protocol.org/schemas/0.1/oip-manifest.schema.json). Lossless pixels: `pixels/frame-0000.png`.
- De-identified DICOM headers (DICOM JSON model): `source/dicom-headers.json`.
