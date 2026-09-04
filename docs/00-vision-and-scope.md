# Open Image Protocol (OIP) — vision and scope

## The one-sentence goal

Convert any medical image (starting with X-ray and scintigraphy, later CT and
MRI) into a **self-describing, schema-validated package** that any capable
vision-language model can understand *without prior training*: what the image
is, how it was acquired, what a pixel means physically, which way is left, how
big things are, and which statements are measured facts versus guesses.

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

## Scope

**In scope (v0.x):**
1. Projection radiography (CR/DX) and planar scintigraphy (NM static/whole-body).
2. A package format (`*.oip/` directory or zip) with manifest, model-ready
   renders, lossless pixels, derived measurements, and a natural-language
   reference file.
3. A converter from DICOM (and, with reduced fidelity, from PNG/JPG + CSV
   metadata as found on Kaggle).
4. Deterministic measurement tools (pixel→mm, CTR, ROI counts) with validation.
5. An MCP server, CLI and Python SDK exposing the same small verb set.
6. A benchmark that measures model understanding *with vs without* OIP.

**Out of scope for now:** diagnosis, clinical decision support, regulatory
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
