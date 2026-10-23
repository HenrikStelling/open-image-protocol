# Open Image Protocol (OIP) — vision and scope

## The one-sentence goal

Convert any medical image (starting with X-ray and scintigraphy, later CT and
MRI) into a **self-describing, schema-validated package** that any capable
vision-language model can use *without prior training*: what the image
is, how it was acquired, what a pixel means physically, which way is left, how
big things are, and which statements are measured facts versus guesses.

The benchmark (OIP-Bench, 2026-09/10) settled what the package is for: every
model tested used the facts the package states, and almost none checked them
against the pixels; wrong text in the file was adopted. So the facts handed to
a model must be checked *before* they reach it and must say how certain they
are. OIP is a checking and translation layer with that job; the package is how
the result travels.

## Why this does not exist yet

- **DICOM** is the universal *storage/transport* standard, but it was designed
  for scanners, PACS and radiologists, not for models: 16-bit pixels, thousands
  of optional tags, vendor private tags, modality-specific pixel semantics,
  inverted polarity (MONOCHROME1), and no natural-language layer. Models are fed
  JPEG/PNG exports that silently drop units, spacing, orientation and polarity.
- Foundation VLMs perform poorly on **quantitative** tasks (size, distance, angle)
  and on **spatial relations** (patient left vs image left) in medical images,
  and adopt misleading textual context at very high rates.
- Existing "AI results" standards (DICOM SR TID 1500, IHE AIR, FHIR
  ImagingStudy, RSNA CDEs) describe *outputs* of AI for clinical systems; none
  packages an *input* for a model.

## Position relative to DICOM

- **OIP does not replace DICOM.** DICOM stays the original record; an OIP package
  is *derived* from it by a converter that checks plausibility, labels every fact
  with an assertion level (`measured | computed | inferred | external | unknown`)
  and its source, computes measurements with deterministic tools and writes the
  reference file for the model.
- **Why not hand the raw tags to the model:** (a) the frontier model interfaces
  accept images and text, not DICOM objects; (b) the tags are often missing or
  wrong (of 2,100 converted chest radiographs none carried an edge-orientation
  tag, and two of four public sources ship a pixel spacing that implies an
  implausible image width for every image); (c) raw tags are not a reading guide
  (which edge is the patient's left must be derived from orientation, view and
  display convention); (d) models do not check text against the pixels, so
  whatever they are told must have been checked first and must carry its
  certainty. (d) is the strongest reason and the one the benchmark established.
- **Input side, not output side.** DICOM SR (TID 1500), IHE AI Results and FHIR
  ImagingStudy describe *findings* for clinical systems. OIP describes the *input*
  to a model and deliberately carries no findings; detector outputs may appear
  only as `inferred` observations with the producing tool named (D-025).
- **A protocol and schema, not a new file format.** The core is the checking and
  translation, specified as a schema with a change process (OEPs). The `.oip`
  directory or zip is one transport. Other transports are planned, none built:
  the manifest and reference file attached to the study as a DICOM object
  (an SR-like container, so it travels through any PACS); the checked package as
  the *response* of an MCP or DICOMweb service that an agent queries (today the
  MCP server in `src/oip/mcp_server.py` is a stub); an "export as OIP" action in
  open viewers and archives (Orthanc, Weasis, 3D Slicer) in place of the PNG or
  screenshot export that researchers use to show a medical image to a model.
- **Honest limits.** One package describes one image: a posteroanterior and a
  lateral radiograph are two packages, a CT or MR series is reduced to single
  slices (a study-level container is future work). For screenshots or JPEGs
  without a header, as in teaching collections, there is nothing to recover and
  the benefit is small. When models come to read DICOM natively the translation
  becomes unnecessary; the plausibility checks, certainty levels and
  tool-computed measurements do not, because the tags stay faulty and the models
  still do not verify text. Most likely models will read DICOM through tools, and
  OIP is then the tool's response format.

## Scope

**In scope (v0.x):**
1. Projection radiography (CR/DX) and planar scintigraphy (NM static/whole-body).
2. A package format (`*.oip/` directory or zip) with manifest, model-ready
   renders, lossless pixels, derived measurements, and a natural-language
   reference file.
3. A converter from DICOM (and, with reduced fidelity, from PNG/JPG + CSV
   metadata as found on Kaggle).
4. Deterministic measurement tools (pixel→mm, CTR, ROI counts) with validation.
5. A CLI and Python SDK exposing the same small verb set; an MCP server with
   the same verbs (stub only, Phase 5).
6. A benchmark that measures whether a model *uses* the package's facts, whether
   it *checks* them against the pixels, and whether it adopts wrong text in the
   file (OIP-Bench; `bench/README.md`).

**Out of scope, by design (D-025):** diagnosis and interpretation — OIP carries observations and optional cited reference ranges; conclusions are the consuming model's. Also out of scope for now: clinical decision support, regulatory
clearance, PACS integration, DICOM write-back, 3D volumes (CT/MRI arrive in a
later phase with an explicit 3D extension, aligned with NIfTI/OME-Zarr).

## Who it is for

- Developers building agents/apps that must look at medical images.
- Researchers benchmarking VLMs on imaging.
- Dataset curators who want a model-ready, lossless, provenance-carrying export.

## Non-negotiables

- **No PHI in packages by default** (de-identification is a first-class step).
- **No measurement without calibration**: tools refuse to return millimetres if
  pixel spacing is unknown, and say so in `context.md`.
- **Lossless** originals are always retrievable from the package (or referenced by hash).
- **Open**: spec under CC-BY-4.0, code under Apache-2.0 (decision D-002).
