# Open Image Protocol — v0.1 draft specification

Status: draft, 2026-09-04. Normative words: MUST, SHOULD, MAY.

## 1. Purpose
OIP defines a self-describing package for one medical image (or one multi-frame
acquisition) so that a vision-language model can determine, without prior
training or external documentation: what the image is, how it was acquired,
what a pixel value means physically, how the image is oriented, what physical
scale applies, which derived facts exist and how much each can be trusted.

Relation to DICOM: OIP does not replace DICOM. DICOM remains the original
record; a package is derived from it (or, with reduced fidelity, from an image
file plus dataset metadata) by a converter that checks plausibility, labels
every fact with an assertion level and its source, computes measurements with
deterministic tools and writes the reference file. OIP is the *input* side for
a model; findings belong to the output side (DICOM SR, IHE AI Results) and are
not part of a package. The normative core of OIP is this schema and its rules,
not the directory layout: the `.oip` directory or zip of section 2 is one
transport, and the same manifest and reference file MAY travel attached to a
DICOM study or as the response of a service (section 10). A package describes
one image (or one multi-frame acquisition); a study of several images is
several packages.

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
8. Layers L3 and L4 carry no detection of their own. Every region in
   `derived.regions` and every measurement in `derived.measurements` MUST name
   the producing tool and its version (`tool`, `tool_version`), and its
   `assertion_level` follows from that tool: `computed` for a deterministic
   algorithm on the pixels or metadata, `inferred` for a machine-learning or
   heuristic source (for example a segmentation network), `external` for
   values taken from outside the image. What a package states in these layers
   comes from the source header, the converter's plausibility rules and the
   named tools; a consumer MUST NOT read it as a reference reading of the image.

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

Validation status of a measurement: `unvalidated` (default from the converter), `cross_checked` (an independent automatic source agreed within stated limits; the `cross_check` record carries source, n, Lin's concordance, bias and limits of agreement, and the reference file spells it out), `phantom_validated`, `reference_validated`, `expert_validated` (reserved for phantom, reference or expert measurements). A cross-check is not a validation: two automatic segmentations can share a definition error (added 2026-10-17 after the CheXmask comparison, `docs/reports/chexmask-*.md`).

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

Other transports of the same manifest and reference file, none implemented
(co-author review 2026-10-23): (a) **OIP in DICOM** — manifest and reference
file attached to the study as a DICOM object (an SR-like container), so the
checked facts travel through any PACS; (b) **OIP as a service response** — an
MCP or DICOMweb service that returns the checked package when an agent asks
for an image (`src/oip/mcp_server.py` is a stub; the verb set of section 7 is
the intended interface); (c) **"export as OIP"** in open viewers and archives
(Orthanc, Weasis, 3D Slicer) in place of a PNG or screenshot export. A
study-level container (several projections, CT stacks) and a findings layer
with several, possibly disagreeing sources (each with tool or person, time and
place; in `oip.json` only, never in `context.md` by default) are candidate
extensions for a later version.
