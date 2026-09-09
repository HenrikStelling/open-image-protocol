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

## 6.4b Recovering counts from exported scintigraphy images (finding, 2026-09-06)
Public bone-scan PNGs (Zenodo IICS-UNA set) are 16-bit images linearly stretched so that the per-image maximum is 65535. The stored values therefore sit on a lattice `value = floor(step × counts)`; fitting `step` (smallest value gap, then iterative least squares) recovers the original photon counts up to that per-image factor. On the Zenodo set this succeeds for 414/582 images (recovered maxima 72–1,110 counts). OIP records the result under `extensions["org.openimageprotocol.counts_recovery"]` with `assertion_level = inferred` and states it in `context.md`. Absolute cross-patient comparison still needs dose, time and duration, which such exports lack. To do: the 29 % of images where the lattice fit fails (likely a half-step local minimum).

## 6.4b First real-data results (VinDr 1,000 sample, 2026-09-06; `docs/reports/phase2-measurement-report.md`)
- Anatomy adapter (TorchXRayVision PSPNet, ChestX-Det): 9 regions on every image, 0 errors, ~1 s/image on CPU; laterality sanity check (left-labelled structures on the L-labelled side) passed on all 1,000.
- CTR median 0.478, p10 0.415, p90 0.553; 34 % above 0.50. First reading (2026-09-06): "lung-mask union underestimates the internal thoracic width, CTR biased high". **Revised 2026-09-09 with a second, independent tool:** CXAS (159 structures, individual ribs) run on the 20 pilot images gives an internal thoracic width from the inner rib margins of 271 mm (median) vs 275 mm from the lung union (ratio 0.994), and CTR 0.486 vs 0.483; the two tools' heart widths also agree (136 vs 131 mm). So the lung-union denominator is not systematically narrow on these images. The elevated >0.5 rate is consistent with the sample: the 1,000-image stratified sample is finding-enriched (half with findings; cardiomegaly is VinDr's most frequent finding), so its cardiomegaly prevalence is well above the dataset's 18 %. Per-image disagreement between the tools does occur (rib-margin/lung-union ratio 0.58–1.05; the low values are one-sided rib segmentation failures), which is why CTR stays `unvalidated` until CheXmask/expert Tier 2–3, and why the package now can carry both measurements with their methods named.
- mm widths refused on 185 images (no spacing); 6 images with implausible spacing produced absurd widths (median 1,712 mm) and were correctly marked confidence `low` — a reader following `context.md` would ignore them.
- SIIM (299 images): radiologist pneumothorax masks attached as `external` regions; pneumothorax/ipsilateral-lung-field area ratio median 0.041, p90 0.214 — a spacing-free measurement, usable even on data with stale spacing.

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
