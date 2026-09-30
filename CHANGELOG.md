# Changelog

All notable changes to the specification, the reference implementation and the benchmark. Versions of the parts are tracked separately because they move at different speeds:

| Part | Version | Where |
|---|---|---|
| specification | 0.1 draft | `spec/oip-v0.1-draft.md`, `oip.version` in every manifest |
| manifest schema | 0.1 | `spec/schemas/oip-manifest.schema.json` |
| reference-file template | 0.2.1 (0.2 + the estimation caution of OEP-002; verification cues of the 0.3 draft remain behind a flag) | `src/oip/context.py` `TEMPLATE_VERSION` |
| Python package | 0.2.0 | `pyproject.toml`, `provenance.producer_version` in every manifest |
| benchmark scorer | 0.3 | `bench/score.py` `SCORER_VERSION`, recorded per row |
| harness commit used for the paper runs | 050769a | `run_meta.json` (runs from 2026-09-26), otherwise by run date |

## 0.2.0 (2026-09-29): the state of the paper, its audits and the first benchmark-driven revisions

Source code of this release: https://doi.org/10.5281/zenodo.23052075 · frozen benchmark replies and packages: https://doi.org/10.5281/zenodo.23040047

### Specification and reference file
- OEP-001 / D-027: external labels and report text are omitted from `context.md` by default; when requested, cautions precede them and they carry unverified-label wording (template 0.2). Evidence: the benchmark's misleading-text test.
- OEP-002 / D-031: the estimation caution ("judge it directly from the picture, do not compute it from pixel coordinates you estimate yourself") is on by default (template 0.2.1); it repairs the L0–L2 CTR drop on low-confidence spacing for the three of seven Ollama models that showed it and changes nothing for the others. The low-confidence-scale guard was not adopted (it cost cardiac-width answers).
- D-029: pixel-side orientation check `oip check` (`quality.checks[]`, flag `orientation_pixel_inconsistent`), two-pass and prior-free; schema extended. 94 of 100 mirrored packages decided, 0 wrong.
- OEP-003/004 (verification cues, a "how to use this file" instruction, a self-check mirror item; template 0.3 draft behind a flag): no effect on the frontier models, a net cost for the two small local models, one open model moved +16 points; not adopted as default. Round 3 closed on eleven models.
- OEP-005 / D-030: an encoder-safe inspection sheet (1536 px, large R/L badges, heart inset, ruler) does not change whether models check the pixels; not adopted, the render stays optional and non-normative.
- Deterministic package identity under `SOURCE_DATE_EPOCH` (`src/oip/identity.py`); example packages are byte-reproducible.

### Reference implementation
- Non-DICOM adapter (PNG plus dataset metadata) for NIH ChestX-ray14; planar scintigraphy adapter for stretched 16-bit PNG bone scans with count recovery.
- Chest anatomy adapter (TorchXRayVision PSPNet): regions, marks, CTR, cardiac and thoracic width; CXAS bridge in an isolated venv as a second source.
- CLI verbs `describe`, `validate`, `convert`, `window`, `crop`, `overlay`, `measure`, `check`; the MCP server remains a stub.
- All machine-specific paths moved to environment variables (`OIP_KAGGLE_CACHE`, `OIP_BENCH_DIR`, `OIP_VINDR_LABELS`, `OIP_CXAS_PYTHON`); optional dependency groups `measure`, `bench`, `all`; CI on GitHub Actions.

### Benchmark (OIP-Bench)
- Harness v2: layer ablation (`ctx_l1`), annotated-render tasks (heart mark, mark side), balanced flip check, misleading test through the shipped template, abstention and cost capture; NM task set; no-leakage rule and leak check.
- Paper run: 11 models × 3 sets (VinDr-100, NIH-50, 40 bone scans), 60,483 replies, frozen; scoreboard `bench/report.py`; statistics `bench/paper_stats.py`.
- Scorer 0.3 after the independent audits: abstention flag independent of correctness, centimetre answers normalised, flip parser reads the final line and more negations, reasoning before `</think>` not scored, abstention pattern narrowed. `bench/rescore.py` keeps the previous score per row and writes a diff report.
- Run provenance: `run_meta.json` and per-row harness commit and scorer version; Ollama thinking text separated from the answer and `done_reason` recorded per row; one-cloud-model-at-a-time lock.
- Ablation conditions for OEP-002 to OEP-005 (`raw_ctl`, `ctx_l1_ctl`, `ctx_l1_oep2`, `ctx_l1_oep2e`, `ctx_ctl`, `ctx_cue`, `ctx_instr`, `ctx_cue_instr`, render-probe conditions) with their own names, so the paper's cells are never overwritten by the latest-run rule; reports under `docs/reports/`.

### Documentation and release
- `REPRODUCE.md` (four levels), `docs/README.md` (documentation map), `CITATION.cff`, `LICENSE-docs.md`, release bundle script for Zenodo (`scripts/export_release_bundle.py`).

## 0.1.0 (2026-09-08)
- First public structure: specification draft, JSON Schema, converter for DX/CR, NM multi-frame and single-frame CT/MR, renders, reference file (template 0.1), synthetic phantoms with exact truth, example packages, Tier-0 tests.
