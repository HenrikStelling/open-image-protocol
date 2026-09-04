# Q2 — Comparable file formats / protocols we can reuse

| Standard | What it is | Reuse in OIP | Do not copy |
|---|---|---|---|
| **DICOM (PS3.x)** | Universal medical image storage + network standard; IODs per modality (DX, CR, NM…); tags with VR | Source of truth for acquisition metadata; we keep a de-identified **DICOM JSON model (PS3.18 Annex F)** dump in `source/dicom-headers.json` (`{"00280030": {"vr": "DS", "Value": [0.139, 0.139]}}`) | Its size, optionality and vendor private tags; its lack of prose |
| **DICOM SR TID 1500 (Measurement Report)** + **highdicom** | Standard container for AI measurements/qualitative results; profiled by IHE AI Results (AIR) | Our `derived/measurements.json` mirrors TID 1500 concepts (finding, measurement, units via UCUM, method, tracking id) so an OIP package can be *exported* to SR later | Its XML/SR tree complexity as the primary model-facing format |
| **IHE AI Results (AIR)** | Workflow profile for exchanging AI results via DICOM / DICOMweb | Interop target for Phase 6 | Not an input format |
| **FHIR ImagingStudy / DiagnosticReport** | Clinical-record pointers to DICOM studies (no pixels) | Optional `references.fhir` link; CDE mapping | Not an image format |
| **RSNA/ACR Common Data Elements (RadElement)** | Machine-readable definitions of findings (size, location, composition) with allowed values; web service | Use CDE ids for measurement/finding names where they exist (e.g. cardiothoracic ratio) | — |
| **NIfTI-1/2** | Neuroimaging volume format with affine (qform/sform) | Model for our 3D extension (affine to patient space) | 2D use |
| **OME-Zarr / OME-NGFF (v0.5)** | Chunked, multiscale, cloud-native images with JSON metadata; RFC-4 adds anatomical orientation | Model for multiscale renders and for CT/MRI phase; JSON-in-attrs pattern | Microscopy-specific metadata |
| **BIDS** | Directory + JSON sidecar convention for neuroimaging datasets | **Directly copied**: OIP is a directory convention with JSON sidecars and a validator | — |
| **OpenAPI / JSON Schema** | Machine-readable API and data schemas | JSON Schema for `oip.json` (as MCP uses for tools) | — |
| **MCP / LSP / MHS** | See `docs/01-reference-protocols` | Verb set, self-description, capability profiles, semver, SEP process | — |
| **llms.txt** | Convention: a Markdown file that tells LLMs what a site is and how to read it | **Directly copied** as `context.md` (a fixed-template "llms.txt for one image") | — |
| **Model cards / Policy cards** | Structured prose + fields describing a model's intended use and limits | Template style for `context.md` "Cautions" section | — |
| **DICOMweb (WADO-RS metadata)** | JSON/XML representation of DICOM over HTTP | Future transport for an OIP server that sits in front of a PACS | — |
| **dicom-mcp (ChristianHinge)** | MCP server for querying/moving DICOM on PACS (Orthanc) | Shows demand; complements OIP (they fetch, we make understandable) | Not clinical-grade, no image semantics |

**Conclusion.** Nothing packages an image *for a model*. The closest relatives are
BIDS (directory + sidecar), llms.txt (prose for models), OME-Zarr (JSON metadata,
multiscale) and TID 1500 (typed measurements). OIP composes these.

## What OIP does about it
- Directory + JSON sidecar layout (BIDS), JSON Schema validation (MCP), a prose
  reference file (llms.txt/MHS), measurements modelled on TID 1500 with UCUM units
  and CDE/RadLex/SNOMED codes, DICOM JSON headers kept verbatim (de-identified).
- Interop exports (SR, FHIR) are a later phase, not the core.
