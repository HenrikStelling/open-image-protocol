# Q11 — How can we validate that our measurements are correct?

## Four tiers, cheapest first

### Tier 0 — Synthetic phantoms (exact ground truth, runs in CI)
- Generate DX and NM DICOMs with pydicom containing shapes of known physical
  size (e.g. an ellipse 120 mm wide at 0.2 mm/px = 600 px), known windows,
  known polarity (MONOCHROME1 and 2), known frame counts.
- Assert: spacing selection, mm conversion, polarity handling, count sums,
  CTR on synthetic "heart"/"thorax" ellipses, refusal when spacing removed.
- Implemented: `scripts/make_examples.py` + `tests/test_phantom.py`.

### Tier 1 — Physics and plausibility checks on real data
- `columns × spacing` within anatomical range; spacing symmetric; NM counts
  consistent with `CountsAccumulated`; decay-corrected dose positive; frame
  durations match `AcquisitionTerminationCondition`.
- Cross-tag consistency: `PixelSpacing` vs `ImagerPixelSpacing / magnification`.

### Tier 2 — Agreement with reference annotations
- Masks: Dice / Hausdorff vs CheXmask (HybridGNet) and CXAS on the same images;
  disagreement between two independent tools flags cases for review.
- Boxes: VinDr radiologist boxes → lesion long axis in mm; compare with tool output.
- CTR: compute from CheXmask masks as reference; report MAE, ICC, Bland–Altman.
  Acceptance: ICC ≥ 0.95 (published DL-CTR systems reach ~0.96 vs radiologists;
  radiologist–radiologist agreement is similar).
- NM: region counts vs manual ROIs on the Paraguay set (small expert subset).

### Tier 3 — Expert reading (small, decisive)
- ~200 CXR + ~50 bone scans measured independently by two readers; compute
  inter-reader agreement first; the tool must fall inside the inter-reader
  limits of agreement. This is the only tier that costs money/time; schedule in Phase 3.

## Status (2026-09-06)
- Tier 0: passing (phantom tests in CI).
- Tier 1: extent/spacing plausibility live; caught RSNA/SIIM stale spacing (100 %) and 6 VinDr outliers.
- Tier 2: **blocked on CheXmask (PhysioNet)**. The Phase 2 run already shows the need: CTR from lung-mask union is biased high (see Q6 §6.4b); the CheXmask comparison will quantify the bias and calibrate the thoracic-width definition.
- Tier 3: readers available (D-023); reading set to be prepared after Tier 2.

## Statistical protocol (fixed in advance)
- Primary: ICC(2,1) and Bland–Altman 95 % LoA per metric.
- Secondary: MAE in mm and in %, error stratified by vendor, view (PA/AP),
  spacing source, and image size.
- Report per `spacing_source` level so users see how confidence maps to error.

## Validation status vocabulary (in `measurements.json`)
`unvalidated` → `phantom_validated` → `reference_validated` → `expert_validated`.
`context.md` states the status next to each measurement.

## What OIP does about it
Tier 0 exists now; Tier 1 rules go into `quality.flags`; Tier 2/3 are Phase 2–3 milestones with acceptance thresholds recorded in PLAN.md.
