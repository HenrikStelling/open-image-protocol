# Q6 — How do we extract measurements, modality and metrics from an image?

## 6.1 Modality
Deterministic from `(0008,0060) Modality` + `ImageType` + SOP Class UID. For
non-DICOM sources (Kaggle PNG/JPG), from dataset documentation, with
`assertion_level = external`; optionally confirmed by a small classifier
(`inferred`). OIP never lets a model guess the modality if metadata exists.

## 6.2 Scale: the one decision everything depends on
Order of preference for `geometry.pixel_spacing_mm` (each recorded as `spacing_source`):
1. `PixelSpacing` **with** `PixelSpacingCalibrationType` present → calibrated in patient plane (`calibration.confidence = high`).
2. `PixelSpacing` without calibration type → treat as detector-plane spacing (`medium`), note possible magnification (~5–10 % for chest at 180 cm SID).
3. `ImagerPixelSpacing` (+ `EstimatedRadiographicMagnificationFactor` if present → divide) (`medium`).
4. Dataset-level spacing (e.g. NIH `OriginalImagePixelSpacing` CSV column) rescaled by the resize factor if the image was resampled (`low`, `external`).
5. **None** → `geometry.pixel_spacing_mm = null`; measurement tools return relative values only (pixels, ratios) and refuse mm. This is the MHS "safety limit in the driver" rule.

Plausibility check: `columns × spacing` for a chest PA should be 300–450 mm; violations raise `quality.flags: implausible_extent`.

## 6.3 X-ray metrics (Phase 2 targets)
| Metric | Definition | Inputs | Validation reference |
|---|---|---|---|
| Cardiothoracic ratio (CTR) | max horizontal cardiac width / max internal thoracic width (same row basis as clinical practice) | heart + lung masks | CheXmask masks; published DL-CTR ICC ≈ 0.96 vs radiologists |
| Transverse cardiac diameter (mm) | width of heart mask | mask + spacing | same |
| Lung areas / asymmetry | pixel area × spacing² per lung | masks | CheXmask |
| Mediastinal width | at level of aortic knob | landmarks | expert subset |
| Lesion size (mm) | bounding box long axis | VinDr boxes or detector | VinDr annotations |
| Rotation / inspiration proxies | clavicle symmetry; posterior rib count | landmarks | expert subset |
| Bone age (hand) | model-based | RSNA Bone Age | labels |

Ratios (CTR) are spacing-independent → available even at level 5 above; absolute
mm require levels 1–4 and carry the corresponding confidence.

## 6.4 Scintigraphy metrics
| Study | Metric | Definition |
|---|---|---|
| Whole-body bone scan | Region counts, count density (counts/mm²/s), anterior–posterior geometric mean, lesion/normal-bone uptake ratio, hot-spot count, **Bone Scan Index (BSI)** (fraction of skeletal mass involved) | region template + frame duration + counts |
| Thyroid | % uptake = (thyroid counts − background) / (standard counts) × 100 corrected for decay; nodule/gland ratio | ROI + standard source |
| DAT-SPECT (later, 3D) | Striatal binding ratio (SBR), putamen/caudate ratio, asymmetry index | VOI templates |
| MIBG | heart/mediastinum ratio early/delayed, washout rate | ROIs |
| Renal (DMSA/MAG3) | split function %, T½ | ROIs + dynamic frames |
| MUGA | LVEF | gated frames |

NM guardrails (enforced in tools, explained in `context.md`):
- Compare counts only within one study and one energy window.
- Normalise by `ActualFrameDuration` (→ cps) and, for cross-patient comparison,
  by decay-corrected administered dose and uptake time.
- Whole-body posterior view is mirrored; ROI templates must be flipped.

## 6.5 How measurements are represented
`derived/measurements.json` — one record per measurement:
```json
{"id": "ctr", "name": "Cardiothoracic ratio", "code": {"system": "RadElement", "value": "RDE…"},
 "value": 0.48, "unit": "1", "method": "max heart width / max thoracic width on heart+lung masks",
 "tool": "oip-measure", "tool_version": "0.1.0", "inputs": ["derived/masks/heart.png", "derived/masks/lungs.png"],
 "assertion_level": "computed", "confidence": 0.9, "validation_status": "phantom_validated",
 "geometry": {"type": "line_pair", "points_px": [[…],[…]]}}
```
Modelled on DICOM SR TID 1500 (finding + measurement + method + tracking id) so it
can be exported to SR/FHIR later.

## What OIP does about it
- `geometry.spacing_source` + `calibration` in the schema; measurement tools in
  `src/oip/measure.py` implement the refusal rule; phantom tests in `tests/`.
