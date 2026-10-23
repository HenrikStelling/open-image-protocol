# Open Image Protocol (OIP)

**A protocol, package format and tool set that gives a vision-language model the
physical facts of one medical image (pixel spacing, orientation, polarity, units,
tool-computed measurements), checked by tools and labelled with their certainty.**
OIP is derived from DICOM and does not replace it: DICOM stays the record, an OIP
package is the reading of it prepared for a model. Starting with projection
radiography (X-ray) and planar scintigraphy; CT and MRI follow.

> Status: specification v0.1 draft; reference converter, measurement tools and
> benchmark harness working. 2,100 real radiographs converted with zero failures;
> OIP-Bench run on 190 packages across three datasets and eleven models (eight open,
> three frontier). A paper is in preparation ([docs/paper/](docs/paper/)). Plan and
> milestones: [PLAN.md](PLAN.md).
>
> New here? [docs/README.md](docs/README.md) sorts the documentation into normative,
> implementation, evidence and history. [REPRODUCE.md](REPRODUCE.md) takes you from
> `make setup` to the paper's tables. Versions of the parts (spec, template, package,
> scorer) are listed in [CHANGELOG.md](CHANGELOG.md); cite via [CITATION.cff](CITATION.cff).

## The problem

Vision-language models are usually fed 8-bit screenshots of medical images. That
export silently drops what a radiologist takes for granted: the pixel size, which
side is the patient's left, whether bright means dense or the reverse, what the
intensity units are, how the display window was chosen. The model then guesses,
measures badly, and tends to trust any text it is given over the pixels it sees.

## The idea

OIP turns one image into a small self-describing directory, a `.oip` package, that
any model can read zero-shot. The core is the checking and translation layer
(plausibility rules, assertion levels, measurements computed by tools); the
directory or zip archive is one way to transport it. Findings stay out of the
package on purpose; they belong on the output side (DICOM SR, IHE AI Results). The design borrows from three protocols that made
foreign systems readable to models: **LSP** (a neutral abstraction: text and
positions become image, millimetres and units), **MCP** (self-description through a
JSON Schema plus prose, discovery, semantic versioning, a proposal process) and the
**Model Hardware Standard** (an auto-generated reference file, natural-language
tags, safety enforced in the driver rather than in the model). The full analysis is
in [docs/01-reference-protocols](docs/01-reference-protocols/).

**What a package is and is not.** One package describes one image: a posteroanterior
and a lateral radiograph are two packages, and a CT or MR series is reduced to single
slices (a study-level container is future work). For screenshots or JPEGs without a
header, as found in teaching collections, there is nothing to recover and the benefit
is small. Chat interfaces do not accept folders, so the realistic routes are an API
or an agent that reads the package, or the render and `context.md` sent as two files.

```
DICOM / PNG+CSV  ──►  oip convert  ──►  study.oip/
                                          ├── oip.json        machine-readable manifest (JSON Schema)
                                          ├── context.md      "llms.txt for one image": what it is, how to read it,
                                          │                   measured / computed / inferred / external facts, cautions
                                          ├── renders/        canonical 8-bit (bone/hot = bright), annotated (R/L labels,
                                          │                   scale bar, region marks), inverted (NM), thumbnail
                                          ├── pixels/         lossless 16-bit frames
                                          ├── derived/        masks + measurements (computed by tools, never by the model)
                                          └── source/         de-identified DICOM JSON headers
        any VLM  ◄──  image(s) + context.md  ◄──  file | CLI | Python SDK | MCP server
```

To hand an image to a model today: send `renders/annotated.png` (or
`canonical.png`) plus `context.md`. Nothing else is required.

## What is in a package

The content is organised in layers, and a producer declares which layers it filled:

| Layer | Content | Manifest sections |
|---|---|---|
| L0 | identity, provenance, de-identification | `identity`, `provenance`, `deid`, `subject` |
| L1 | geometry and intensity semantics, quality flags | `acquisition`, `geometry`, `intensity`, `frames`, `quality` |
| L2 | renders and lossless pixels | `renders`, `pixels` |
| L3 | semantic regions (masks, boxes, landmarks) | `derived.regions` |
| L4 | measurements | `derived.measurements` |
| L5 | narrative and external context | `context`, `external` |

Profiles: `core` = L0–L2, `measured` = L0–L4, `full` = L0–L5.

Every fact that could be wrong carries an **assertion level**, one of `measured`,
`computed`, `inferred`, `external` or `unknown`, and the reference file prefixes
each statement with it. Two rules do most of the work:

- **No size in millimetres is ever stated unless a calibrated spacing exists.** Without
  one, the package says so and the tools refuse to answer in mm; ratios and pixels remain.
- **Measurements are computed by tools, never by the model.** Each measurement records
  its method, tool, inputs, confidence and validation status.

Diagnosis is out of scope by design: the package carries observations and optional
reference ranges, never interpretation.

An excerpt of a real reference file, generated from a VinDr-CXR radiograph:

```
# OIP image reference — Radiograph, chest, PA
OIP 0.1.0 · profile `measured` · layers L0, L1, L2, L3, L4 · de-identification: deidentified

## How to read the renders
- Polarity guarantee: in the canonical render, higher attenuation is BRIGHTER.
- Orientation [inferred]: image LEFT edge = R, RIGHT edge = L, TOP = H, BOTTOM = F. No PatientOrientation
  tag; assumed conventional display for view PA.
- Scale [unknown]: NO pixel spacing is available. Do not state sizes in mm or cm; use pixels or ratios only.
- `renders/annotated.png`: edge labels: left=R, right=L, top=H, bottom=F; mark 3 = left lung;
  mark 4 = right lung; mark 5 = heart; ...

## Computed measurements
| id  | name                 | value  | method                                          | confidence | validation  |
| ctr | Cardiothoracic ratio | 0.4824 | max heart-mask width / max lung-union width ... | 0.6        | unvalidated |

## Unknowns and cautions
- no pixel spacing: never report sizes in mm
- left/right labels are inferred from the view, not read from the header
- A radiograph is a projection: overlapping structures superimpose; depth cannot be measured.

## Self-check
1. Which anatomical side is on the image's left edge? → R
2. Can sizes be given in mm? → no
```

## How it is built

- **Converter** ([src/oip/convert.py](src/oip/convert.py), [convert_image.py](src/oip/convert_image.py)):
  reads DICOM (DX/CR, NM multi-frame, CT/MR single-frame), or PNG plus a metadata
  table for datasets that ship no headers, and writes the package. Handles
  MONOCHROME1/2, VOI LUTs, spacing selection with a stated source and confidence,
  orientation, energy windows and tracer data for NM, and de-identification of headers.
- **Renders** ([render.py](src/oip/render.py)): a canonical 8-bit image with a
  guaranteed polarity, an inverted render for scintigraphy, a thumbnail, and an
  **annotated render**: the canonical image pasted into a dark margin with edge
  labels (R, L, H, F), a scale bar when spacing is known, and numbered region marks;
  the image content is unchanged and pixel-aligned at a stated offset.
- **Anatomy and measurements** ([anatomy.py](src/oip/anatomy.py), [measure.py](src/oip/measure.py)):
  a chest adapter runs TorchXRayVision's PSPNet to segment heart, lungs, clavicles,
  spine, aorta, mediastinum and diaphragm, writes masks, numbers each region as a
  mark, and computes the cardiothoracic ratio from the mask widths, plus cardiac and
  thoracic width in mm when the spacing is calibrated. All outputs are marked
  `inferred` or `computed` and stay `unvalidated` until validated (see below).
- **Scintigraphy adapter** ([scripts/bonescan_to_oip.py](scripts/bonescan_to_oip.py)):
  planar whole-body bone scans from stretched PNGs, with count units recovered from
  the quantisation where possible, a square-root window and an inverted render.
- **Reference file** ([context.py](src/oip/context.py)): a fixed template that
  renders the manifest into prose, cautions first, with a self-check block. External
  labels or report text are omitted by default (OEP-001, see below) and, when
  requested, rendered after the cautions with unverified-label wording.
- **Access paths**: the same verbs (`describe`, `measure`, `validate`, `window`,
  `crop`, `overlay`, `locate`) through the CLI and the Python SDK; the MCP server is a
  stub until Phase 5 (nothing in the benchmark depends on it). `oip check` runs the
  pixel-side orientation check and writes its verdict into the manifest.
  Guardrails live in the tools: HU presets refuse non-HU images, mm refuses
  uncalibrated images.

## OIP-Bench: do models use the facts, and do they check them?

The benchmark asks three things: whether models use the facts a package states,
whether they check those facts against the pixels, and whether they adopt a wrong
label placed in the package. The reference file states the answer to every main
question, so the uplift with the file measures uptake of stated facts, not better
image understanding.

**Data.** Three sets, 190 packages: 100 VinDr-CXR chest radiographs (DICOM, with
radiologist finding labels), 50 NIH ChestX-ray14 images (PNG, headers stripped) and
40 whole-body bone scans from the IICS-UNA Paraguay set (20 anterior, 20
posterior). Packages are generated without any label-derived text; a leak check
enforces this after a first pilot showed that box names leaked the finding class.

**Conditions.** Raw image only · image + reference file limited to L0–L2 (identity,
geometry, units, orientation, cautions; no measurements) · image + full reference
file · annotated render + full reference file · a deliberately wrong finding label
injected as a bare "prior report note" · the same wrong label delivered through the
package's external-context template.

**Tasks.** The gating tasks are answerable by reading the image correctly or by
using the package's facts: which patient side is at the left edge; whether sizes can
be stated in mm; the cardiothoracic ratio within ±0.05; the cardiac width within
±10 %. The annotated render adds localisation: which numbered mark outlines the
heart, and on which patient side a given mark lies. The **flip check** shows the
image either normal or mirrored while the reference file states the orientation and
asks whether they agree; two tasks per image, so "always agree" scores 50 %, and the
file states nothing that answers it. The misleading-label test measures how often the
injected wrong label is adopted. Bone scans get the equivalent tasks, including the
mirrored posterior view and which side is hotter. Modality, view and finding-level
F1 are reported but do not gate. The truths come from the package itself (see the
next section); no person reviewed the images.

**Models.** Eleven, one reply per model, condition and question: eight open models
through Ollama (gemma4 31B and e4b, MedGemma 1.5 4B, glm-5.3-flash, kimi-k3,
minimax-m3, mistral-large-3, qwen3.5) and three frontier models (Claude Sonnet 5,
GPT-5.6 Terra, Gemini 3.8 Flash). Later conflict trials ran with three replies per
cell on the ten models still available (qwen3.5 was retired by its provider).

**Results** (scorer 0.3; the paper's analysis: [docs/paper/](docs/paper/)):

| Gating accuracy | raw | + L0–L2 file | + full file | + annotated |
|---|---|---|---|---|
| VinDr-100, range over 11 models | 36–65 % | 53–87 % | 90–100 % | 92–100 % |
| NIH-50, range over 11 models | 18–74 % | 26–77 % | 86–100 % | 83–100 % |

- **The facts reach every model.** With the full file every model improves
  significantly (Holm) on both sets; 9 of 11 reach at least 99.5 % on VinDr-100 and
  7 of 11 on NIH-50. That ceiling is expected, because the file states the answers:
  models use the facts, which says nothing about whether they see them. A partial
  file can hurt: on NIH-50 the L0–L2 file (a low-confidence spacing without the
  measurements) lowered GPT's accuracy significantly.
- **The facts are not checked against the pixels.** With the full file the flip check
  is passed above chance by Gemini (99 %), GPT (88 %), glm-5.3-flash (86 %), qwen3.5
  (63 %) and kimi-k3 (60 %) on VinDr-100; the others, Claude Sonnet 5 included, sit at
  chance and mostly confirm the stated orientation whatever the image shows. In
  conflict trials that cross a true or swapped file with a normal or mirrored image,
  only Gemini and GPT compare file and image (94 % and 91 % over the four cells,
  100 % when the file is swapped and the image normal); the others follow the file,
  the display convention or no consistent rule. Pixel cues in the file and an
  instruction to verify did not change this and cost small models left-edge
  accuracy. A check in the tools does: `oip check` compares the segmented heart
  with each image and its mirror and decided 94 of 100 VinDr images correctly,
  0 wrongly, 6 indeterminate.
- **Bone scans:** the package raises side identification on the mirrored posterior
  views from 0–100 % to 60–100 % across models and improves the gating tasks for 6
  of 11 models; the hotter-side and flip tasks stay at chance for every model.
- A reference file costs about 1,400–2,100 extra input tokens per image (median
  about 1,460 across models).

**Wrong labels in the file are adopted; a benchmark-driven spec change (OEP-001).**
In the pilot, placing a wrong label inside a labelled "external" section of an
authoritative reference file made it *more* credible than the same label pasted as
a bare note (gemma4 31B adopted it 75 % of the time as a note and 100 % inside the
file). Revised wording, cautions first and an explicit unverified-label statement,
lowers adoption for nine of the eleven models on the paper sets (significantly for
eight), in some cases sharply (qwen3.5 45 → 14 %, minimax 87 → 42 %, GPT 74 → 48 %),
but seven models still adopt the wrong label in at least half of the cases and
Gemini is unaffected (75 → 78 %). Wording alone is not a safeguard, so the reference
file renders no external labels or report text by default; they stay in `oip.json`
and are shown only on explicit request. Details in
[docs/03-brainstorm/decisions-log.md](docs/03-brainstorm/decisions-log.md).

**What follows.** Models do not correct what they are told, so metadata for a model
has to be checked before it arrives and has to say how certain it is. That is the
job of the tool layer, not of the prompt.

## What validates the ground truth

The benchmark answers come from the package itself, so the question is how good the
package's facts are.

| Fact | Validation |
|---|---|
| Orientation on stripped headers | No source carries an orientation tag; edge sides are inferred from the view and the display convention. The 1,000-image laterality check on VinDr shares that convention; the pixel-side check (`oip check`, two-pass) is independent of it (94 / 0 / 6 of 100) |
| CTR, cardiac and thoracic width | Tier 1: plausibility rules on the PSPNet-derived values. Cross-check against CheXmask on the 100 VinDr and 50 NIH paper images and 1,000 VinDr packages: thoracic width agrees (Lin's CCC 0.99 / 0.97 / 0.99); the package cardiac width is 4.0 / 5.5 / 3.7 % narrower and the CTR 0.023 / 0.021 / 0.021 lower. The lung-union thoracic width equals the inner rib margin (CXAS rib masks) within 1.5–3.4 %, so the earlier "CTR probably biased high" is withdrawn |
| Lesion sizes, finding labels | VinDr radiologist boxes and labels |
| Pneumothorax area | SIIM-ACR radiologist masks |
| Converter geometry, polarity, units | Synthetic phantoms with exact ground truth ([tests/](tests/)) |
| Tier 2, cross-check done | CheXmask agreement above; every paper and store package carries `validation_status: cross_checked` with the agreement record. This is agreement between automatic segmentations, not a validation |
| Tier 3, pending | Expert reading of about 100 radiographs and 50 bone scans |

Nothing in the benchmark uses a model's own output as ground truth. The benchmark's
truths for side, scale and size are the package's own facts, so OIP-Bench tests
whether models use what the package states, not whether the package is right;
`validated` stays reserved for an expert or reference measurement (Tier 3).

## Repository map

| Path | What |
|---|---|
| [PLAN.md](PLAN.md) | Living plan: phases, milestones, risks, next actions |
| [docs/00-vision-and-scope.md](docs/00-vision-and-scope.md) | Problem, scope, non-negotiables |
| [docs/01-reference-protocols/](docs/01-reference-protocols/) | MCP, LSP, MHS dissected; comparison and the derived design rules R1–R10 |
| [docs/02-research-questions/](docs/02-research-questions/) | The 13 research questions, each answered with evidence and "what OIP does about it" |
| [docs/03-brainstorm/](docs/03-brainstorm/) | Decisions log (OEP style), open questions, naming |
| [docs/04-sources.md](docs/04-sources.md) | Bibliography |
| [docs/reports/](docs/reports/) | Conversion, measurement and benchmark reports on real data |
| [docs/paper/](docs/paper/) | Paper outline and analysis plan |
| [spec/oip-v0.1-draft.md](spec/oip-v0.1-draft.md) | Draft specification |
| [spec/schemas/oip-manifest.schema.json](spec/schemas/oip-manifest.schema.json) | JSON Schema for `oip.json` |
| [spec/examples/](spec/examples/) | Generated example packages (synthetic DX and NM phantoms, pydicom CT/MR samples) |
| [src/oip/](src/oip/) | Reference implementation: converter, renders, context generator, anatomy and measurements, validator, CLI, MCP stub |
| [bench/](bench/) | OIP-Bench: task builder, runner, scorer, report |
| [scripts/](scripts/) | Phantoms, dataset fetching, batch conversion and measurement, the non-DICOM adapters |
| [tests/](tests/) | Tier-0 phantom tests (exact ground truth) |

## Quickstart

```bash
make setup          # creates .venv with uv and installs the package
make examples       # builds spec/examples/*.oip from synthetic phantoms + pydicom samples
make test           # phantom tests
.venv/bin/python -m oip.cli convert path/to/image.dcm out/study   # -> out/study.oip/
.venv/bin/python -m oip.cli describe spec/examples/synthetic-dx-chest.oip
.venv/bin/python -m oip.cli validate spec/examples/synthetic-dx-chest.oip
.venv/bin/oip measure  path/to/study.oip                       # chest anatomy regions + CTR (TorchXRayVision)
.venv/bin/oip crop     path/to/study.oip 700 400 1200 1100 --upscale 2
.venv/bin/oip overlay  path/to/study.oip --regions 1 2 --grid-mm 50
.venv/bin/oip window   path/to/ct.oip --preset lung             # HU presets refuse non-HU images
```

Benchmark: `python bench/run.py --pkg-dir path/to/packages --models ollama/<tag>,claude,gpt,gemini --conditions raw,ctx_l1,ctx,annot`
(frontier providers read their keys from the environment; see [bench/README.md](bench/README.md)).
`make setup-all` adds the anatomy adapter and the benchmark extras. Machine-specific
locations are environment variables (`OIP_KAGGLE_CACHE`, `OIP_BENCH_DIR`, `OIP_VINDR_LABELS`,
`OIP_CXAS_PYTHON`), listed with their defaults in [REPRODUCE.md](REPRODUCE.md).

## Data and code availability

The benchmark's dataset is the set of frozen model replies (41 run directories,
64,809 rows, with their task files) together with the benchmark packages. They are
archived on Zenodo as the release bundle built by
[scripts/export_release_bundle.py](scripts/export_release_bundle.py): full NIH and
bone-scan packages, manifests and reference files of the VinDr packages (whose images
are Kaggle competition data and are not redistributed), and a sha256 manifest of every
file including the ones not bundled, so a rebuild can be verified. Zenodo:
https://doi.org/10.5281/zenodo.23500611 (v0.2.1 bundle: the paper run and the later
experiments, the packages, the CheXmask/CXAS files and the paper's analysis code with
its results file); https://doi.org/10.5281/zenodo.23040047 keeps the v0.2.0 bundle with
the packages as analysed in the paper run. The source code of the same
release is archived at https://doi.org/10.5281/zenodo.23052075; release 0.2.1 (round 3a, the CheXmask cross-check and the settled CTR
denominator) at https://doi.org/10.5281/zenodo.23490342, concept DOI https://doi.org/10.5281/zenodo.23052074 for the latest version. The analysis plan and the results file of the paper are in
[docs/paper/](docs/paper/); the scoring is deterministic and re-runnable
([REPRODUCE.md](REPRODUCE.md), level B).

The source datasets are not redistributed here. `scripts/fetch_data.py` with
`scripts/datasets.json` downloads VinDr-CXR, RSNA Pneumonia, SIIM-ACR and NIH
ChestX-ray14 (Kaggle; the competition sets require accepting their rules) and the
Paraguay bone scans (Zenodo, CC-BY-4.0). Each dataset carries a `SOURCE.md` with its
licence. The repository contains only synthetic example packages; packages derived
from restricted datasets are never committed, and no package carries patient
identifiers.

## Contributing

Changes to the specification or schema go through an OIP Enhancement Proposal,
recorded in the decisions log with problem, evidence, prototype and benchmark
effect. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

Code: Apache-2.0 (see [LICENSE](LICENSE)). Specification and documentation:
CC-BY-4.0 (see [LICENSE-docs.md](LICENSE-docs.md)).
