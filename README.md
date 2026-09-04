# Open Image Protocol (OIP)

**A self-describing package format, tool set and protocol that turns any medical
image into something a vision-language model can understand without prior
training.** Starting with projection radiography (X-ray) and planar
scintigraphy; CT and MRI follow.

> Status: v0.1 draft. Research complete, spec drafted, reference converter and
> phantom tests working. See [PLAN.md](PLAN.md) for phases and
> [docs/03-brainstorm/open-questions.md](docs/03-brainstorm/open-questions.md)
> for the decisions that need your input.

## The idea in one diagram

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

Design borrowed from three protocols that made "foreign languages" readable to
models: **LSP** (neutral abstraction: text + positions → image + mm + units),
**MCP** (self-description via JSON Schema + prose, discovery, semver, SEP
process) and the **Model Hardware Standard** (auto-generated reference file,
natural-language tags, safety limits enforced in the driver rather than the model).
Full analysis: [docs/01-reference-protocols](docs/01-reference-protocols/).

## Repository map

| Path | What |
|---|---|
| [PLAN.md](PLAN.md) | Living plan: phases, milestones, risks, next actions |
| [docs/00-vision-and-scope.md](docs/00-vision-and-scope.md) | Problem, scope, non-negotiables |
| [docs/01-reference-protocols/](docs/01-reference-protocols/) | MCP, LSP, MHS dissected + comparison and derived design rules |
| [docs/02-research-questions/](docs/02-research-questions/) | The 13 research questions, each answered with evidence and "what OIP does about it" |
| [docs/03-brainstorm/](docs/03-brainstorm/) | Decisions log (OEP style), open questions for you, naming |
| [docs/04-sources.md](docs/04-sources.md) | Bibliography |
| [spec/oip-v0.1-draft.md](spec/oip-v0.1-draft.md) | Draft specification |
| [spec/schemas/oip-manifest.schema.json](spec/schemas/oip-manifest.schema.json) | JSON Schema for `oip.json` |
| [spec/examples/](spec/examples/) | Generated example packages (synthetic DX and NM phantoms, pydicom CT/MR samples) |
| [src/oip/](src/oip/) | Reference implementation: converter, renders, context generator, measurements, validator, CLI, MCP stub |
| [scripts/](scripts/) | `make_examples.py` (phantoms), `fetch_data.py` + `datasets.json` (reference data) |
| [tests/](tests/) | Tier-0 phantom tests (exact ground truth) |

## Quickstart

```bash
make setup          # creates .venv with uv and installs the package
make examples       # builds spec/examples/*.oip from synthetic phantoms + pydicom samples
make test           # phantom tests
.venv/bin/python -m oip.cli convert path/to/image.dcm out/study   # -> out/study.oip/
.venv/bin/python -m oip.cli describe spec/examples/synthetic-dx-chest.oip
.venv/bin/python -m oip.cli validate spec/examples/synthetic-dx-chest.oip
```

To hand an image to a model today: send `renders/annotated.png` (or
`canonical.png`) plus `context.md`. Nothing else is required.

## Publishing to GitHub

`gh` is not authenticated on this machine, so the remote was not created. Run:

```bash
gh auth login
```

then, from the repo root:

```bash
gh repo create open-image-protocol --private --source=. --remote=origin --push
```

## Licence
Code: Apache-2.0 (see LICENSE). Specification and docs: CC-BY-4.0 (proposed, decision D-002).
