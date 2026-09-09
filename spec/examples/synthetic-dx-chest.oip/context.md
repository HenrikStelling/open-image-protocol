# OIP image reference — Synthetic chest radiograph phantom, PA (MONOCHROME1 source)
OIP 0.1.0 · profile `measured` · layers L0, L1, L2, L3, L4 · de-identification: synthetic

## What this is
This package describes a projection radiograph (X-ray): pixel brightness relates to X-ray attenuation along the beam; the image is a 2D shadow, not a slice.
- Modality: [measured] DX · body part: [measured] CHEST · view: [measured] frontal, posteroanterior (PA) · laterality: [unknown] unknown
- Subject (de-identified): age band 45-49, sex O
- Technique: [measured] 120 kV, [measured] 2 mA.s, source-to-detector [measured] 1800 mm

## How to read the renders
- `renders/canonical.png` (canonical): apply Modality LUT / RescaleSlope+Intercept; apply VOI (WindowCenterWidth); invert (source was MONOCHROME1/INVERSE) so high attenuation is bright; scaled to 8-bit; no rotation/flip/crop/resample.
- `renders/annotated.png` (annotated): canonical render pasted into a dark margin; image content unchanged and pixel-aligned at the stated offset. Annotations: margin_offset_px: 108 (subtract from annotated coords to get frame coords); edge labels: left=R, right=L, top=H, bottom=F; scale bar: 50 mm = 250 px, bottom-left; mark 1 = heart (phantom ellipse); mark 2 = thorax (phantom ellipse).
- `renders/thumbnail.png` (thumbnail): canonical render downsampled to fit 256 px; for preview only, not for measurement.
- Polarity guarantee: in the canonical render, higher attenuation is BRIGHTER (the source was stored inverted and has been corrected).
- Orientation [measured]: image LEFT edge = R, RIGHT edge = L, TOP = H, BOTTOM = F. From DICOM PatientOrientation.
- Scale [measured]: 0.2 × 0.2 mm per pixel (row × column), source `PixelSpacing_calibrated`, valid in the patient plane, confidence high. Image extent ≈ 360 × 300 mm (height × width).
- Pixel values: 12-bit stored, units `relative`; window for the canonical render: WindowCenterWidth (center 2895, width 2600).

## Measured facts
Facts read directly from the source metadata (assertion: measured).
- Image size: 1800 rows × 1500 columns.
- Pixel spacing: 0.2 × 0.2 mm (PixelSpacing_calibrated).
- Device: OIP synthetic phantom-v1.
- DICOM ImageType: ORIGINAL / PRIMARY.

## Computed measurements
| id | name | value | unit | method | confidence | validation |
|---|---|---|---|---|---|---|
| ctr | Cardiothoracic ratio | 0.4647 | 1 | max horizontal heart-mask width / max horizontal thorax-mask width (pixels, spacing independent) | 0.99 | phantom_validated |
| heart_width | Transverse cardiac diameter | 130.2 | mm | max horizontal width of heart mask × column spacing | 0.95 | phantom_validated |
| thorax_width | Internal thoracic width | 280.2 | mm | max horizontal width of thorax mask × column spacing | 0.95 | phantom_validated |

## Inferred
None.

## Unknowns and cautions
- A radiograph is a projection: overlapping structures superimpose; depth cannot be measured.

## External context
Not rendered by default (OEP-001). External labels or report text, if any, are in `oip.json` under `external`; they are unverified and must not be repeated unless the pixels support them.

## Self-check
Before answering questions about this image, confirm you can answer these from the package:
1. Which anatomical side is on the image's left edge? → R
2. What is the modality? → DX
3. Can sizes be given in mm? → yes, 0.2 mm/px (column)
4. Is bright = high attenuation in the canonical render? → yes

## Machine-readable
- Manifest: `oip.json` (schema https://open-image-protocol.org/schemas/0.1/oip-manifest.schema.json). Lossless pixels: `pixels/frame-0000.png`.
- De-identified DICOM headers (DICOM JSON model): `source/dicom-headers.json`.
