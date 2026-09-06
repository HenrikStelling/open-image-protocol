# Q10 — How do we transfer data into one standardized format (X-ray or scintigraphy alike)?

## Design: one neutral core, modality adapters underneath (the LSP move)

```
input (DICOM | PNG/JPG + CSV | NIfTI later)
   └─► adapter (dx.py | nm.py | generic.py)     ← modality knowledge lives here
          └─► neutral core manifest (oip.json)  ← identical schema for all modalities
                 ├─► renders/ (canonical, annotated)
                 ├─► pixels/  (lossless)
                 ├─► derived/ (masks, measurements)
                 ├─► source/  (de-identified DICOM JSON)
                 └─► context.md (prose reference file)
```

### Package layout (v0.1)
```
<study>.oip/
  oip.json                 manifest (schema-validated)
  context.md               natural-language reference file
  renders/canonical.png    8-bit, VOI applied, bone/hot bright, original geometry
  renders/annotated.png    canonical + scale bar + orientation labels (+ SoM marks)
  renders/thumbnail.png
  pixels/frame-0000.png    16-bit lossless (one per frame)
  derived/measurements.json
  derived/masks/*.png
  source/dicom-headers.json  DICOM JSON model (PS3.18 F), PHI removed
```
A zipped package uses the `.oip` extension with the same internal layout.

### Neutral core fields (identical for DX and NM)
`identity`, `provenance`, `subject`, `acquisition` (with modality-specific
sub-object `dx` or `nm`), `geometry`, `intensity`, `frames`, `renders`,
`derived`, `quality`, `deid`, `context`.

### Conversion rules
1. Never modify pixels in `pixels/`; renders are derived and their transforms recorded.
2. Canonical render polarity: high attenuation / high counts = bright.
3. Canonical render window: VOI LUT from the file if present; otherwise robust
   percentiles; for NM optionally sqrt/log; always recorded.
4. Orientation: no rotation/flip applied in v0.1 (record what the file says);
   labels are drawn in the annotated render. (Decision D-005 keeps geometry
   untouched so pixel coordinates stay valid.)
5. Multi-frame NM: one `frames[]` entry per frame with detector, view, duration,
   counts; renders per frame plus a composite.
6. De-identification: drop all PHI tags (names, IDs, dates → age band only,
   institution, private tags), hash UIDs, flag `BurnedInAnnotation`.
7. Non-DICOM inputs: fill what is known from the dataset CSV with
   `assertion_level = external`; everything else `unknown`; `quality.flags`
   list what is missing.
8. Validate against the JSON Schema before writing; a package that fails is not written.

## Learnings from the first 2,100 real conversions (2026-09-06)
- Headers lie in predictable ways: stale spacing after resampling (RSNA, SIIM), stripped identity/orientation (VinDr), anisotropic resizing (NIH). The converter now (a) checks physical extent against body-part ranges and downgrades confidence, (b) accepts dataset-level `hints` recorded as `external`, (c) recomputes per-axis spacing for resized PNGs.
- Lossless storage should match the source bit depth: 8-bit sources go to 8-bit PNG (`pixels.format = png8`). Packages of JPEG-compressed 8-bit DICOMs are still ~9× the source because PNG is lossless while the source was lossy; an OEP could allow keeping the original JPEG bitstream as the pixel layer.
- `context.md` costs ~850–900 tokens for the `core` profile, under the 1,500 target.
- Throughput: 0.85 s/image for 12–16-bit JPEG-2000 DICOMs, <0.1 s for 8-bit sources, single core.

## What OIP does about it
Implemented in v0: `src/oip/convert.py` (DICOM path for DX/CR/CT-single-frame and
NM multi-frame), `render.py`, `context.py`, `validate.py`, CLI `oip convert`.
Non-DICOM adapter and anatomy models are Phase 2.
