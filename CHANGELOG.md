# Changelog

All notable changes to the specification, the reference implementation and the benchmark. Versions of the parts are tracked separately because they move at different speeds:

| Part | Version | Where |
|---|---|---|
| specification | 0.1 draft | `spec/oip-v0.1-draft.md`, `oip.version` in every manifest |
| manifest schema | 0.1 | `spec/schemas/oip-manifest.schema.json` |
| reference-file template | 0.2 (0.3 draft behind `verification_cues=True`, not default) | `src/oip/context.py` `TEMPLATE_VERSION` |
| Python package | 0.1.0 | `pyproject.toml`, `provenance.producer_version` in every manifest |
| benchmark scorer | 0.3 | `bench/score.py` `SCORER_VERSION`, recorded per row |
| harness commit used for the paper runs | 050769a | `run_meta.json` (runs from 2026-09-26), otherwise by run date |

## Unreleased (towards v0.2.0, the state of the paper)

### Specification and reference file
- OEP-001 / D-027: external labels and report text are omitted from `context.md` by default; when requested, cautions precede them and they carry unverified-label wording (template 0.2). Evidence: the benchmark's misleading-text test.
- Pixel-side orientation check `oip check` (`quality.checks[]`, flag `orientation_pixel_inconsistent`), two-pass and prior-free; schema extended. 94 of 100 mirrored packages decided, 0 wrong.
- Template 0.3 draft with verification cues, behind a flag; the ablation on eleven models showed no effect on frontier models and a cost for small models, so it is not the default (OEP-003/004, decisions log).
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
- Run provenance: `run_meta.json` and per-row harness commit and scorer version; one-cloud-model-at-a-time lock.

### Documentation and release
- `REPRODUCE.md` (four levels), `docs/README.md` (documentation map), `CITATION.cff`, `LICENSE-docs.md`, release bundle script for Zenodo (`scripts/export_release_bundle.py`).

## 0.1.0 (2026-09-08)
- First public structure: specification draft, JSON Schema, converter for DX/CR, NM multi-frame and single-frame CT/MR, renders, reference file (template 0.1), synthetic phantoms with exact truth, example packages, Tier-0 tests.
