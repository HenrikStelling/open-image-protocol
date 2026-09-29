# Open Image Protocol — v0.1 draft specification

Status: draft, 2026-09-04. Normative words: MUST, SHOULD, MAY.

## 1. Purpose
OIP defines a self-describing package for one medical image (or one multi-frame
acquisition) so that a vision-language model can determine, without prior
training or external documentation: what the image is, how it was acquired,
what a pixel value means physically, how the image is oriented, what physical
scale applies, which derived facts exist and how much each can be trusted.

## 2. Package layout
```
<name>.oip/
  oip.json                  MUST   manifest, validates against schemas/oip-manifest.schema.json
  context.md                MUST   natural-language reference file (section 6)
  renders/canonical.png     MUST   8-bit greyscale, canonical polarity, source geometry
  renders/annotated.png     SHOULD canonical + edge labels + scale bar (+ region marks)
  renders/thumbnail.png     MAY
  renders/frame-XXXX.png    MUST for multi-frame (one canonical render per frame)
  pixels/frame-XXXX.png     MUST   lossless 16-bit PNG of stored pixel values (one per frame)
  derived/measurements.json MAY    array of measurement objects (schema $defs/measurement)
  derived/masks/*.png       MAY    binary masks, same geometry as the frame
  source/dicom-headers.json SHOULD DICOM JSON model (PS3.18 F) after de-identification
  source/original.*         MAY    original file (omit when it may contain PHI)
```
A package MAY be distributed as a zip archive with extension `.oip` containing
exactly this tree at its root.

## 3. Layers and profiles
| Layer | Content | Manifest sections |
|---|---|---|
| L0 | identity, provenance, de-identification | `identity`, `provenance`, `deid`, `subject` |
| L1 | geometry and intensity semantics, quality flags | `acquisition`, `geometry`, `intensity`, `frames`, `quality` |
| L2 | renders and lossless pixels | `renders`, `pixels` |
| L3 | semantic regions (masks, boxes, landmarks) | `derived.regions` |
| L4 | measurements | `derived.measurements` |
| L5 | narrative and external context | `context`, `external` |

Profiles: `core` = L0–L2, `measured` = L0–L4, `full` = L0–L5. A producer MUST
declare `oip.profile` and `oip.layers` and MUST NOT claim a layer it did not fill.

## 4. Manifest rules
1. `oip.json` MUST validate against the schema for its `oip.version`.
2. Every fact that could be wrong carries an `assertion_level`
   (`measured | computed | inferred | external | unknown`).
3. `geometry.pixel_spacing_mm` MUST be `null` unless a spacing with a stated
   `spacing_source` exists. Consumers MUST NOT infer physical size when it is null.
4. `geometry.calibration.plane` distinguishes detector-plane spacing from
   patient-plane spacing; consumers SHOULD mention magnification uncertainty when
   `plane = detector`.
5. `intensity.units` states what a rescaled pixel value means. For `counts`,
   values are only comparable within the same package and energy window.
6. UIDs, names, dates and free text from the source MUST be removed or hashed
   (`deid.status`). Age is reduced to a 5-year band.
7. Absolute timestamps MUST NOT appear; relative timings (uptake time) MAY.

## 5. Render rules
1. `renders/canonical.png`: 8-bit greyscale; same rows/columns as the frame; no
   rotation, flip, crop or resampling; polarity `high_is_bright`; window from the
   source VOI when present, else robust percentiles; the exact transform is
   recorded in `renders[].transform`.
2. `renders/annotated.png`: canonical image plus a letterbox margin containing
   (a) edge labels giving the anatomical side of each image edge,
   (b) a scale bar with its length in mm when spacing is known, or the text
   "no calibrated scale" otherwise, (c) optional region marks (numbers/letters)
   listed in `derived.regions[].mark`, (d) the modality/view title.
   The image content area MUST remain pixel-aligned with the canonical render
   (margins only), so pixel coordinates in `derived` remain valid after subtracting the margin offsets stated in `renders[].annotations`.
3. For scintigraphy an `inverted` variant SHOULD be provided (hot = dark), because
   that is the conventional display.

## 6. `context.md` (reference file)
Fixed section order (template 0.2.1); every section present even if it only says "none":
`What this is` · `How to read the renders` · `Measured facts` ·
`Computed measurements` · `Inferred` · `Unknowns and cautions` · `External context`
· `Self-check` · `Machine-readable`.
External content (dataset labels, prior report text) is NOT rendered by default (D-027): it stays in `oip.json.external`.
When a consumer requests it, it is rendered after the cautions with the wording "UNVERIFIED … do not repeat unless the pixels clearly show it".
Template 0.2.1 (2026-09-29, D-031, OEP-002): `How to read the renders` carries one estimation caution — a quantity that is not listed under `Computed measurements` is judged from the picture as a ratio or relative size, not computed from pixel coordinates the reader estimates itself. Measured on NIH-50 with seven open models: it repairs the drop in cardiothoracic-ratio accuracy that the L0–L2 file causes on the models that compute from self-estimated coordinates, and changes nothing else. A stronger "do not derive millimetres from a low-confidence spacing" guard was measured in the same ablation and NOT adopted (`docs/reports/oep-002-2026-09-29.md`).
The file SHOULD stay below ~1,500 tokens for the `core` profile. Each statement
in sections 3–6 is prefixed with its assertion level in brackets.

## 7. Verb set (tool interface; MCP, CLI and SDK expose the same)
Implementation status (v0.1 reference): `describe`, `measure`, `validate`, `window`, `crop`, `overlay`, `check` available in the Python SDK and CLI; `locate` is served through `derived.regions` and the MCP stub only.
| Verb | Input | Output | Guardrails |
|---|---|---|---|
| `describe` | package [, region] | manifest summary / context.md | — |
| `locate` | structure label | region(s) with bbox and mark | only from `derived.regions`; otherwise "unknown" |
| `measure` | geometry in px, or named measurement | value + unit + assertion + validation status | refuses mm when spacing is null; refuses count comparison across windows |
| `check` | package | `quality.checks[]` record (consistent / inconsistent / indeterminate, with evidence); sets `orientation_pixel_inconsistent` on failure | pixel-side only: the unsided heart and aortic-arch masks against the edge labelled L; never rewrites the stated orientation, only reports on it, and context.md shows the result next to the orientation line (added 2026-09-26, draft) |
| `window` | center/width or preset | new render + transform record | never overwrites canonical |
| `crop` | bbox px, optional upscale | render + coordinate offset | records offset so coordinates map back |
| `overlay` | regions / grid / scale | annotated render | — |
| `validate` | package | schema + package-rule report | — |

## 8. Conformance
A conformant producer: validates every package before writing; fills all MUST
items; passes the phantom test-suite (`tests/`). A conformant consumer: never
estimates physical size when spacing is null; treats `external` statements as
unverified; preserves `assertion_level` when re-emitting facts.

## 9. Versioning and change process
Semantic versioning. Additive changes = minor; breaking = major with ≥ 2 minor
releases of deprecation. Changes are proposed as OEPs with a prototype and a
benchmark result (see `docs/02-research-questions/q13-protocol-improvement-loop.md`).

## 10. Future extensions (non-normative)
3D volumes (affine to patient space, multiscale chunks, NIfTI/OME-Zarr alignment);
DICOM SR TID 1500 / FHIR export; remote OIP servers over Streamable HTTP with OAuth;
region vocabularies per modality (CXR anatomy, skeletal regions for bone scans).
