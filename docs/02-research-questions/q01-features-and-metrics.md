# Q1 — What features and performance metrics do we need?

## Features (what an OIP package must be able to do)

| Feature | Why (evidence) | Layer |
|---|---|---|
| F1 Identity + provenance (hashes, producer, converter version, source format) | Statelessness lesson from MCP 2026-07-28; reproducibility | L0 |
| F2 Physical geometry: pixel spacing in mm, *spacing source* and calibration type, magnification factor, physical extent | DICOM has three different spacing concepts (`PixelSpacing`, `ImagerPixelSpacing`, `PixelSpacingCalibrationType`); wrong choice → wrong mm | L1 |
| F3 Orientation and laterality: patient orientation, view (PA/AP/lateral, anterior/posterior for NM), explicit R/L labels in renders | VLMs fail at relative position in medical images and rely on priors ("Your other Left", MICCAI 2025) | L1 |
| F4 Intensity semantics: bit depth, photometric interpretation, rescale, units (`relative`, `counts`, `HU`, `Bq/ml`), VOI window used for the render | 8-bit conversion without VOI LUT loses diagnostic contrast; MONOCHROME1 inverts polarity; windowing improves classification (WindowNet) | L1 |
| F5 Model-ready renders: canonical 8-bit PNG (VOI applied, MONOCHROME2 polarity), annotated overlay (scale bar, orientation labels, optional set-of-mark regions) | Grid overlays: +0.145 IoU for GPT-5.2 grounding; SoM prompting improves grounding; models need visual, not only textual, cues | L2 |
| F6 Semantic layer: anatomy masks / landmarks / bounding boxes with codes (SNOMED, RadLex) and assertion level | Needed for measurements and for SoM overlays | L3 |
| F7 Measurements computed by tools, with method, tool version, confidence, validation status, units | VLMs "perform poorly" on size/angle/distance (MedVision) → measure outside the model | L4 |
| F8 Natural-language reference file `context.md` with fixed sections and assertion levels | MHS auto-generated reference file; MC-CXR: text can mislead (74.6 % adoption of wrong text label) → label provenance | L5 |
| F9 Quality/diagnostic flags (missing spacing, burned-in annotation, lossy compression, implausible extent) | LSP `publishDiagnostics` analogy | L1 |
| F10 De-identification status | Non-negotiable | L0 |
| F11 Conformance profile declaring which layers are present | LSP capabilities | L0 |
| F12 Access paths: package, CLI, Python SDK, MCP server | MHS three paths | — |

## Metrics (how we know OIP works)

### A. Format / protocol metrics
- **Schema validity rate** on converted datasets (target 100 %).
- **Completeness score**: fraction of required fields per layer that are filled (per dataset; tells us which sources are weak).
- **Round-trip losslessness**: `pixels/` decodes bit-identically to the source pixel array.
- **Overhead**: package bytes / source bytes; `context.md` tokens (target < 1.5 k tokens for the default profile).
- **Conversion latency** per image (target < 1 s for 2D).

### B. Measurement metrics (Q11 details)
- Phantom exactness: |measured − true| ≤ 1 px-equivalent on synthetic phantoms.
- Real data: MAE / RMSE in mm, ICC and Bland–Altman limits of agreement vs expert or reference masks (published CTR models reach ICC ≈ 0.96 vs radiologists — our floor for "acceptable").
- Mask agreement: Dice vs CheXmask / CXAS.
- **Refusal correctness**: tool returns "no calibrated spacing" exactly when it should.

### C. Model-understanding metrics — "OIP-Bench" (Q12, Phase 3)
Evaluated **with vs without** the OIP package, across ≥ 4 models (Claude, GPT, Gemini, one open model such as MedGemma/CXR-LLaVA), zero-shot:
1. Modality identification accuracy.
2. View / orientation / laterality accuracy.
3. Scale awareness: mm estimate of a marked structure within ±10 %.
4. CTR estimate error (when asked to *read* the OIP measurement vs *estimate* from pixels).
5. Finding-level F1 on VinDr-CXR labels (does context help or hurt?).
6. Misleading-context resistance (MC-CXR protocol): switch rate when `external` text contradicts the image.
7. Cross-model consistency: variance of answers across models (a protocol that works "for any model" must reduce variance).
8. Report quality when asked to write findings: RadGraph-F1, GREEN, RaTEScore (ReXrank metric suite).
9. Token cost and latency per query.

### D. Safety metrics
- PHI leak rate in packages (target 0; burned-in text detector recall).
- Guardrail coverage: % of unsafe requests (uncalibrated mm, cross-window count comparison) refused.

## What OIP does about it
- Features F1–F12 map one-to-one onto the layers in `spec/oip-v0.1-draft.md`.
- Metrics A and B are implemented first (deterministic, cheap); C requires the
  benchmark harness in Phase 3; D is part of the conformance suite.
