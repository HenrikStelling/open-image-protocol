# Open Image Protocol (OIP)

**A self-describing package format, tool set and protocol that turns any medical
image into something a vision-language model can understand without prior
training.** Starting with projection radiography (X-ray) and planar
scintigraphy; CT and MRI follow.

> Status: specification v0.1 draft; reference converter, measurement tools and
> benchmark harness working. 2,100 real radiographs converted with zero failures;
> OIP-Bench run on 190 packages across three datasets and eleven models (eight open,
> three frontier). A paper is in preparation ([docs/paper/](docs/paper/)). Plan and
> milestones: [PLAN.md](PLAN.md).

## The problem

Vision-language models are usually fed 8-bit screenshots of medical images. That
export silently drops what a radiologist takes for granted: the pixel size, which
side is the patient's left, whether bright means dense or the reverse, what the
intensity units are, how the display window was chosen. The model then guesses,
measures badly, and tends to trust any text it is given over the pixels it sees.

## The idea

OIP turns one image into a small self-describing directory, a `.oip` package, that
any model can read zero-shot. The design borrows from three protocols that made
foreign systems readable to models: **LSP** (a neutral abstraction: text and
positions become image, millimetres and units), **MCP** (self-description through a
JSON Schema plus prose, discovery, semantic versioning, a proposal process) and the
**Model Hardware Standard** (an auto-generated reference file, natural-language
tags, safety enforced in the driver rather than in the model). The full analysis is
in [docs/01-reference-protocols](docs/01-reference-protocols/).

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
  `crop`, `overlay`, `locate`) through the CLI, the Python SDK and an MCP server stub.
  Guardrails live in the tools: HU presets refuse non-HU images, mm refuses
  uncalibrated images.

## OIP-Bench: does it help models?

The benchmark asks whether a model understands an image better with the package
than with the raw image, and whether it checks text against pixels.

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

**Tasks.** The gating tasks are answerable only by reading the image correctly or by
using the package's facts: which patient side is at the left edge; whether sizes can
be stated in mm; the cardiothoracic ratio within ±0.05; the cardiac width within
±10 %. The annotated render adds localisation: which numbered mark outlines the
heart, and on which patient side a given mark lies. The **flip check** shows the
image either normal or mirrored while the reference file states the orientation and
asks whether they agree; two tasks per image, so "always agree" scores 50 %. The
misleading-label test measures how often the injected wrong label is adopted. Bone
scans get the equivalent tasks, including the mirrored posterior view and which side
is hotter. Modality, view and finding-level F1 are reported but do not gate.

**Models.** Eleven, one reply per model, condition and question: eight open models
through Ollama (gemma4 31B and e4b, MedGemma 1.5 4B, glm-5.3-flash, kimi-k3,
minimax-m3, mistral-large-3, qwen3.5) and three frontier models (Claude Sonnet 5,
GPT-5.6 Terra, Gemini 3.8 Flash).

**Results** (full tables: [docs/reports/pilot-ollama-report.md](docs/reports/pilot-ollama-report.md)):

| Gating accuracy | raw | + L0–L2 file | + full file | + annotated |
|---|---|---|---|---|
| VinDr-100, range over 11 models | 36–65 % | 53–87 % | 90–100 % | 92–100 % |
| NIH-50, range over 11 models | 17–74 % | 26–77 % | 84–100 % | 83–100 % |
| Spread across models (SD) | 12 pp | 11 pp | 4 pp | 3 pp |

- Nine of eleven models reach 99–100 % with the full package; the two weakest reach
  84–90 %. Roughly half of the uplift comes from the L0–L2 file (geometry,
  orientation, units), the rest from the computed measurements.
- Where models still differ is telling. The flip check is passed by Gemini (99 %),
  GPT (88–97 %) and glm-5.3-flash (80–85 %); every other model, including Claude
  Sonnet 5, sits at or near chance (50–69 %): most models do not verify text against pixels.
- Bone scans: the package lifts side identification (chance on mirrored posterior
  views) from 40–78 % to 80–100 % and modality and scale questions to about 100 %;
  the hotter-side and flip tasks stay at chance for every model.
- A reference file costs on the order of 1,000–2,000 input tokens per image.

**A benchmark-driven spec change (OEP-001).** In the pilot, placing a wrong label
inside a labelled "external" section of an authoritative reference file made it
*more* credible than the same label pasted as a bare note (gemma4 31B adopted it
75 % of the time as a note and 100 % inside the file). Revised wording, cautions
first and an explicit unverified-label statement, lowers adoption for nine of the
eleven models on the paper sets, in some cases sharply (qwen3.5 42 → 12 %, minimax
88 → 35 %, GPT 74 → 48 %), but seven models still adopt the wrong label in more
than half of the cases and Gemini is unaffected. Wording alone is not a safeguard,
so the reference file renders no external labels or report text by default; they
stay in `oip.json` and are shown only on explicit request. Details in
[docs/03-brainstorm/decisions-log.md](docs/03-brainstorm/decisions-log.md).

## What validates the ground truth

The benchmark answers come from the package itself, so the question is how good the
package's facts are.

| Fact | Validation |
|---|---|
| Orientation on stripped headers | 1,000-image laterality check on VinDr |
| CTR, cardiac and thoracic width | Tier 1: plausibility rules on the PSPNet-derived values; thoracic width cross-checked against an independent tool (CXAS) on 20 images, agreement within 1 % |
| Lesion sizes, finding labels | VinDr radiologist boxes and labels |
| Pneumothorax area | SIIM-ACR radiologist masks |
| Converter geometry, polarity, units | Synthetic phantoms with exact ground truth ([tests/](tests/)) |
| Tier 2, pending | Agreement with CheXmask expert-curated lung and heart masks (ICC, Bland–Altman) |
| Tier 3, pending | Expert reading of about 100 radiographs and 50 bone scans |

Nothing in the benchmark uses a model's own output as ground truth, and every
measurement in a package stays marked `unvalidated` until Tier 2 agreement is measured.

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

## Data

The datasets are not redistributed here. `scripts/fetch_data.py` with
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
CC-BY-4.0.
