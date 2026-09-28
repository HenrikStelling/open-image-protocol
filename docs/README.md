# Documentation map

The repository grew as a research log. This page sorts it into four kinds of document so that a reader knows what is normative, what is code, what is evidence and what is history.

## 1. Normative: the protocol

| Document | Status |
|---|---|
| [spec/oip-v0.1-draft.md](../spec/oip-v0.1-draft.md) | the specification: package layout, layers and profiles, manifest rules, render rules, the reference-file template (0.2), verb set, conformance, versioning |
| [spec/schemas/oip-manifest.schema.json](../spec/schemas/oip-manifest.schema.json) | JSON Schema for `oip.json` |
| [spec/examples/](../spec/examples/) | four example packages (synthetic DX and NM phantoms, pydicom CT and MR samples), rebuilt deterministically by `make examples` |
| [01-reference-protocols/comparison-and-lessons.md](01-reference-protocols/comparison-and-lessons.md) | the design rules R1–R10 and where they come from (LSP, MCP, Model Hardware Standard) |
| [03-brainstorm/decisions-log.md](03-brainstorm/decisions-log.md) | every design decision and enhancement proposal (OEP) with its evidence; the change process |

Read in this order: comparison-and-lessons → spec → an example's `context.md` → the decisions log for the why.

## 2. Reference implementation

| Where | What |
|---|---|
| [src/oip/](../src/oip/) | converter (`convert.py`, `convert_image.py`), renders, reference-file generator (`context.py`), anatomy and measurements, pixel-side orientation check (`check.py`), validator, CLI, MCP server stub |
| [scripts/](../scripts/) | phantoms, dataset fetching, batch conversion and measurement, the benchmark-set builders, the release bundle |
| [tests/](../tests/), [bench/test_*.py](../bench/) | phantom tests with exact truth, scorer and runner tests |
| [../REPRODUCE.md](../REPRODUCE.md) | how to install, rebuild, re-score and re-run, with expected results |

## 3. Evidence: what was measured

| Document | Content |
|---|---|
| [reports/phase2-conversion-report.md](reports/phase2-conversion-report.md) | 2,100 real radiographs converted; what four public sources actually deliver (spacing, polarity, orientation) |
| [reports/phase2-measurement-report.md](reports/phase2-measurement-report.md) | PSPNet regions and CTR on 1,000 VinDr images; the known upward CTR bias |
| [reports/pilot-ollama-report.md](reports/pilot-ollama-report.md) | the OIP-Bench scoreboard, regenerated from the frozen replies by `bench/report.py` |
| [reports/rescore-scorer-0.3.md](reports/rescore-scorer-0.3.md) | which cells moved when the scorer was corrected after the audits |
| [reports/orientation-pixel-check.md](reports/orientation-pixel-check.md) | the `oip check` verb on 100 mirrored packages |
| [reports/render-probe-2026-09-27.md](reports/render-probe-2026-09-27.md) | inspection-sheet render probe (OEP-005 draft) |
| [paper/](paper/) | the paper: analysis plan (post hoc, with amendments), results file, reference sheets, the superseded first draft, and the runbook of the Research_Automation study that produced the revised manuscript |

## 4. History and working notes

| Document | Content |
|---|---|
| [../PLAN.md](../PLAN.md) | the living plan: phases, milestones, and a dated run log; long, and written while the work happened |
| [00-vision-and-scope.md](00-vision-and-scope.md) | the original problem statement, scope and non-negotiables |
| [02-research-questions/](02-research-questions/) | the thirteen research questions answered before the design |
| [03-brainstorm/](03-brainstorm/) | open questions, naming, and third-party proposals quoted verbatim (marked as such) |
| [04-sources.md](04-sources.md) | bibliography with identifiers |

Nothing under 4 is normative; where it disagrees with the spec or a report, the spec and the report win.
