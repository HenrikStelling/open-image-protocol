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
