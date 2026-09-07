# Decisions log (ADR / OEP style)

Format: **D-nnn — title** · status · date · context · decision · consequences.
Anything marked *proposed* is awaiting the user's review.

## D-001 — Name: Open Image Protocol (OIP) · accepted · 2026-09-04
Web search found no existing "Open Image Protocol"; OpenImageIO (VFX) and OCI
image-spec (containers) are the nearest name neighbours and are unrelated. Keep
the name; use `oip` as CLI/package name and `.oip` as package extension.

## D-002 — Licences · proposed · 2026-09-04
Spec + docs: CC-BY-4.0. Code: Apache-2.0 (patent grant matters for a protocol).
LICENSE file added for code; spec licence noted in `spec/README.md`.

## D-003 — Package = directory with JSON sidecar (BIDS-style), zip optional · accepted
Rationale: inspectable with any tool, git-friendly, works offline, matches
OME-Zarr/BIDS practice. A single-file binary container was rejected for v0.

## D-004 — Manifest is JSON validated by JSON Schema (draft 2020-12) · accepted
Same choice as MCP tool schemas; every field carries a `description` written for
models as well as humans.

## D-005 — Do not resample, rotate or flip pixels in v0.1 · accepted
Keep source pixel coordinates valid; put orientation cues in the annotated
render and in `geometry.orientation`. Revisit when 3D arrives.

## D-006 — Canonical polarity: attenuation/counts high = bright · accepted
Rationale: MONOCHROME2 is the DICOM default; models see mostly bright-bone
CXRs. Bone scans are often shown inverted in practice → provide `inverted`
render variant for NM.

## D-007 — Assertion levels on every fact · accepted
`measured | computed | inferred | external | unknown`. Driven by MC-CXR evidence.

## D-008 — Measurements are computed by tools, never by the model · accepted
Tools refuse mm without calibrated spacing (MHS "limits in the driver").

## D-009 — Versioning: semver from 0.1.0; deprecation ≥ 2 minor versions · accepted

## D-010 — Verb set: describe, locate, measure, window, crop, overlay, validate · proposed
Small, read-only. `write`-type operations are out of scope.

## D-011 — Reference data strategy · accepted
X-ray on Kaggle (VinDr, RSNA, NIH); scintigraphy from Zenodo + synthetic NM
DICOM; request PhysioNet/AIMI access for masks/reports.

## D-012 — First MCP server is read-only and local (stdio) · proposed
Resources: `oip://<package>/manifest`, `/context`, `/renders/canonical`;
tools mirror the verb set. Remote (HTTP + OAuth) later.

## D-013 — 3D extension deferred; will align with NIfTI affine + OME-Zarr multiscale · proposed

---
## Decisions from the owner's review of the open questions (2026-09-06)

## D-014 — Target consumers, in order: general assistants (a) → clinical integrators (c) → research pipelines (b) · accepted
Consequence: MCP server and `context.md` quality come first; SR/FHIR export (clinical integration) is pulled forward ahead of research-pipeline conveniences (bulk conversion, dataset tooling).

## D-015 — OIP is an understanding protocol, not a diagnostic one · accepted
OIP lets a model understand and analyse an image. It never produces a diagnosis. The benchmark measures both understanding tasks and finding-level tasks, but **only understanding tasks gate releases**.

## D-016 — Scintigraphy priority: bone scans → thyroid → renal → cardiac · accepted

## D-017 — Human free-text notes allowed in `context.md`, marked `external` · accepted

## D-018 — Full-resolution lossless pixels are included in every package · accepted

## D-019 — Subject keeps 5-year age band and sex; finer detail opt-in · accepted

## D-020 — Layers inside the manifest, profiles as named layer sets · accepted (default confirmed)

## D-021 — Governance: first outside contributors are domain experts who validate · accepted
Open the OEP process to outside contributors after v0.2, or earlier if the first benchmark fails its gate. Expert readers are available (D-023).

## D-022 — Kaggle re-checked for scintigraphy (2026-09-06) · accepted
Small image-only sets exist (thyroid scan set under CDLA-Permissive-1.0; two DaTscan sets; one bone-scan set with unknown licence; one SPECT MPI set). None ship DICOM headers. Strategy unchanged: Zenodo Paraguay + synthetic NM DICOM for the converter; Kaggle sets added to Phase 4 for render/benchmark diversity.

## D-023 — Expert readers are available · accepted
Tier-3 validation (~200 CXR, ~50 bone scans, two readers) is scheduled in Phase 3 rather than deferred.

## D-024 — Model API keys are available · accepted
Phase 3 benchmark is unblocked; cost estimate to be confirmed before the first full run.

## D-025 — Diagnosis is emergent, not preconfigured; OIP carries observations, optionally reference ranges, never interpretations · accepted · 2026-09-06
Owner's question: does a format that lets a model understand an image (entity, anatomy, sizes, intensity values such as HU or uptake) need built-in diagnostic logic, or can diagnosis follow from better understanding? Decision: the latter, with a three-tier boundary.
1. **Observations (in scope, mandatory):** what the image is, geometry, intensity semantics, regions, and measurements with provenance and assertion level. This includes *value* measurements per region (mean/min/max HU, count density, relative attenuation) — added as `derived.regions[].stats`.
2. **Reference ranges (in scope, optional, `external`):** cited normal ranges next to a measurement (e.g. "adult CTR normal < 0.50", "liver 40–60 HU"). Knowledge, not judgement; lets a model compare without OIP deciding anything.
3. **Interpretation (out of scope):** findings, impressions, diagnoses. Produced by the consuming model or a downstream tool, never by the package. Detector outputs (boxes, "nodule") may be carried as `inferred` observations with the producing tool named, but OIP defines no diagnostic vocabulary and no rules.
Rationale: (a) frontier models already hold the clinical reasoning (CTR threshold, HU ranges, uptake patterns); what they lack is trustworthy inputs — MedVision, MC-CXR and our own runs show the failure is measurement and grounding, not reasoning. (b) Diagnostic logic inside a format freezes today's medicine into a spec and turns a data standard into a regulated device. (c) It keeps the benchmark honest: OIP-Bench measures whether findings-level accuracy rises *as a consequence* of understanding tasks improving, with zero diagnostic code in the package — that is the test of the hypothesis. Consistent with D-015.
