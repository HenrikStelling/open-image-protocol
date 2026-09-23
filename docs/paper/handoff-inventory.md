# OIP paper via Research_Automation — analysis and handoff inventory

Written 2026-09-23. Companion: [RUNBOOK-research-automation.md](RUNBOOK-research-automation.md) (what to do, step by step, in a Claude session inside the Research_Automation repo). This file says what the automation setup is, how the OIP paper fits it, and every file and data item the paper needs, with its location, size, git status and the action to take.

Repos and paths used below:

| Name | Path | Notes |
|---|---|---|
| RA | `/Users/pal/Projects/Research_Automation` | Research automation repo, GitHub `HenrikStelling/Research_Automation`, branch `main`, clean at 2701a78. `/Users/pal/Desktop/Research_Automation` is a symlink to it, so the Desktop paths hard-coded in its CLAUDE.md and skills still work. |
| OIP | `/Users/pal/oip-work` | The OIP working clone, `main` at 050769a, pushed. **Use this one.** `/Users/pal/Desktop/OIP` is a stale iCloud clone (ed010ed, 8 September) and must not be used as a source. |
| Packages | `/Users/pal/oip-bench` | The benchmark package store (not in git). |

## 1. What the Research_Automation setup is

One Python codebase (`src/`, Python 3.14 venv at `RA/.venv`) with a dataset-agnostic engine and thin per-study packages. Three studies already run through it: the EBNM benchmark (`src/`, an LLM-on-exam benchmark), ISAPS trends (`isaps/`, PDF extraction → six papers via a registry) and a systematic review (`review/`, literature as the dataset). The generic onboarding recipe is the `dataset-pipeline` skill (`openclaw-skills/dataset-pipeline/SKILL.md`); ISAPS is its reference instance and the pattern to copy.

The chain for one paper is: extract → analysis → citations → build → integrity audit → peer review, each stage a deterministic subprocess run by a thin orchestrator (`isaps/orchestrate_isaps.py`, 134 lines, is the template). The pieces to reuse by import, never fork:

- `src/paper_registry.py` `Registry`: loads `papers.yaml`, resolves `RESULTS/<id>` and `LITERATURE/<id>`.
- `src/stats.py`, `src/figures.py` (300 dpi, legend below the plot), `src/match.py`.
- `src/provenance.py`: `cite_clusters`, `render_provenance` (a "Data sources and provenance" block, no orphan references).
- `src/citations.py`: PubMed E-utilities, CrossRef enrichment, live DOI check, Vancouver and BibTeX.
- `src/build_paper.py`: `md_table`, `pct`, `convert` (pandoc → docx and html; PDF only if a LaTeX engine is installed, none is).
- `src/audit.py`: six-state verdicts, `gate()`, and `run_claude_audit`, a hermetic read-only headless auditor (`claude -p --safe-mode --tools Read,Glob,Grep --strict-mcp-config`).
- `src/handoff.py`: the reviser's tool allowlist for the peer-review handoff (`claude -p` with the `/peer-review` skill, `--permission-mode acceptEdits`, `--add-dir ROOT`).
- `src/notify.py`: Telegram, optional (`--no-notify`).

Hard invariants that bind the OIP paper too (RA `CLAUDE.md`): the LLM never computes a result, every number in the manuscript traces to `results.json` and every citation to `selected_references.json`; always the RA venv; a written analysis plan (`PROTOCOL`) that the Methods reference, with dated amendments; auditors are fresh, read-only, hermetic, and never the reviser; no skill installation from inside the repo; every structural change is recorded in `docs/state/<area>.md`, `docs/state/INDEX.md` and the CLAUDE.md "Current state" block (a Stop hook, `tools/check_state_drift.sh`, nags when this is skipped).

Operational facts that matter for a new study:

- Headless `claude -p` calls run with cwd = RA root, so every path inside an audit or reviser prompt must be package-prefixed (`oipbench/PAPER/...`), else the auditor reads another study's files and returns BLOCKED.
- The audit prompt is the auditor's only framing; it must name the sanctioned number sources explicitly.
- The claim audit reaches an "irreducible WARN steady state" on wording nits; the repo's rule is to fix findings at origin (template or analysis code), never by editing the built manuscript, so a rebuild cannot reintroduce them.
- The EBNM audit loop stopped on two things no audit can supply: a repository URL/DOI and the funding and competing-interest declarations (`declarations:` in the study config). The OIP paper will stop on the same two unless they are decided first.
- Tools present: pandoc 3.8.2.1, Claude Code CLI 2.1.267, venv with jinja2, pandas, statsmodels, scipy, matplotlib, pingouin, PyYAML, requests. No LaTeX engine (docx and html only).
- A machine-wide PreToolUse hook ("Skill-Audit") rejects shell lines containing `$(...)` substitutions, the word "skills" in path-like contexts, and some other forms; write helper logic to script files with the Write tool and run them, rather than inline one-liners.

## 2. How the OIP paper maps onto this setup

The benchmark data are already collected: 41 run directories of frozen model replies with their scores (5,000-plus rows per frontier model). That makes the OIP study the same shape as the systematic review's re-cast of invariant 1: **the LLM replies are the raw data, frozen; deterministic Python re-scores and analyses them; the LLM only writes and reviews prose.** No model is called again to produce a number.

Consequences for the design:

- A new study package `RA/oipbench/` mirroring `isaps/`, registry `papers.yaml` with one paper id `oip` (a second id for a scintigraphy-only paper can be added later without touching the first).
- An ingest stage copies the raw run directories into `oipbench/data/raw/` with a manifest (sha256 per file, harness commit per run, model ids, SDK and Ollama versions, prices, run dates) and applies the report's selection rules deterministically (latest run per dataset × model × condition, tag normalisation, condition renaming, NIH `scale_available` exclusion).
- The vendored scorer (`bench/score.py`) re-scores every reply from text; the ingest asserts 100 % agreement with the stored `score` field before anything else runs. That is the reproducibility guarantee a reviewer can check.
- The analysis plan is written **before** the analysis code, but **after** data collection, and the paper must say so (the EBNM protocol's §8 amendments are the model for honest post-hoc labelling).
- Ground truth for measurement tasks (CTR, cardiac width) comes from the package's own tool outputs, validated only at Tier 1 plus a 20-image CXAS cross-check; CheXmask (Tier 2) and expert reading (Tier 3) are pending. The paper states this; it is not a blocker for the preprint.

## 3. Inventory

Column "git": whether the item is version-controlled anywhere. Column "action": what the RA session does with it. Sizes measured 2026-09-23.

### 3.1 Raw benchmark data (the dataset)

| Item | Path | Size | git | Action |
|---|---|---|---|---|
| Run directories: `results.jsonl` (one row per model × condition × task: model, model_id, provider, condition, task, type, gating, reply, error, usage incl. cache tokens and latency, score) and `tasks.json` (the task set with question text, answer, tolerance, package path) | `OIP/bench/results/2026*/` (41 dirs; exclude `CONTAMINATED-20260908-160228-gemma4_e4b`) | 36 MB | **no** (`bench/results/` is git-ignored) | Copy all 41 dirs verbatim to `oipbench/data/raw/bench_results/`; commit them to RA (they are the dataset). |
| VinDr finding labels (findings F1 and the misleading-label task) | `~/oip-bench/meta/vindr_train.csv` | 4.4 MB | no | Copy to `oipbench/data/raw/vindr_train.csv`. Kaggle competition data: keep in the private repo, do not publish the CSV; the paper cites VinDr-CXR. |
| Slim package metadata: `oip.json` and `context.md` of every paper-set package (100 VinDr, 50 NIH, 40 bone scans = 190 packages) for reference-file token counts, spacing confidence, calibration source, ground-truth values | `~/oip-bench/{vindr-paper,nih-paper,bonescan}/*.oip/{oip.json,context.md}` | 3.7 MB | no | Copy with a small script preserving the directory names to `oipbench/data/raw/packages_meta/`. The full packages (1.7 GB + 87 MB + 19 MB, with renders, pixels, masks) stay where they are; record their sha256 manifest only. |
| Pilot-20 packages (the OEP-001 before/after ablation ran only on this set) | `~/oip-bench/vindr/` | 342 MB | no | Metadata copy as above (`oip.json`, `context.md`). |
| CXAS vs PSPNet thoracic-width agreement on 20 images | `~/oip-bench/cxas_vs_pspnet_20.json` | 8 KB | no | Copy. |
| Smoke and pilot lists | `~/oip-bench/pilot_pkgs.txt`, `~/oip-bench/smoke/` | small | no | Copy the txt; ignore `smoke/` (its result dirs were deleted, nothing in the paper depends on it). |

### 3.2 Harness code to vendor (scoring must be reproducible from the copy)

| Item | Path | Why | Action |
|---|---|---|---|
| Scorer | `OIP/bench/score.py` (80 lines) | Re-scores replies; abstention rule; answer extraction for chain-of-thought | Vendor as `oipbench/vendor/score.py` at commit 050769a, unchanged. |
| Task builder | `OIP/bench/tasks.py` | Task definitions, gating set, tolerances (CTR ±0.05, width ±10 %), the NIH `scale_available` skip rule, flip-check design (two tasks per image so "always agree" scores 50 %), misleading-label draw | Vendor (read-only, for the Methods and the eval audit). |
| Runner header | `OIP/bench/run.py` lines 1–60 | `MODELS`, `PRICES`, `IMAGE_TOKENS`, `SYSTEM` prompt, `CONDITIONS` text, `applies()` | Vendor the whole file (read-only). The provider-call code documents effort settings: Gemini `thinking_level="low"`, OpenAI `reasoning effort low`, `max_output_tokens=600`; Anthropic `effort low`, `max_tokens=4000`, prompt caching on image and reference-file blocks; retry policy for transient errors. |
| Existing aggregator | `OIP/bench/report.py` | The selection rules the paper must reproduce: latest run per (dataset, model, condition); dataset name map by package dir; NIH `scale_available` rows dropped; tag fix `:675b:cloud` → `:675b-cloud`; legacy condition renaming `misled_oip_strong` → `misled_oip`, old `misled_oip` → `misled_oip_v01`; gating aggregate = the four common tasks only | Vendor; the new ingest re-implements these rules and asserts equality with this script's tables. |
| Reference-file generator (template 0.2 text) | `OIP/src/oip/context.py` (168 lines) | Quoted in §5.3 of the paper; the L0–L2 ablation is "derived stripped" through `build_context` | Vendor as text for citation; not executed in RA. |
| Manifest schema | `OIP/spec/schemas/oip-manifest.schema.json` | Figure: manifest excerpt | Copy under `oipbench/data/raw/spec/`. |

### 3.3 Reports and prior numbers (inputs to prose, never a source of a number in the paper)

| Item | Path | Content |
|---|---|---|
| Benchmark scoreboard | `OIP/docs/reports/pilot-ollama-report.md` (regenerated 2026-09-22 19:29) | All tables for 11 models × 3 sets; the numbers the new analysis must reproduce exactly. |
| Conversion report and stats | `OIP/docs/reports/phase2-conversion-report.md`, `phase2-conversion-stats.json` | 2,100 images, 0 failures; spacing sources and confidence; what headers contained (§6 of the paper). |
| Measurement report | `OIP/docs/reports/phase2-measurement-report.md` | CTR distribution, PSPNet regions, "unvalidated until Tier 2". |
| Plan, decisions | `OIP/PLAN.md`; `OIP/docs/03-brainstorm/decisions-log.md` (D-015 gating tasks, D-025 no diagnosis, D-026 Ollama pilot, OEP-001/D-027 external-context wording, D-028 the paper) | Run chronology (throttles, weekly limit, retries), design decisions with their evidence. |

### 3.4 Documents the prose is written from

| Item | Path |
|---|---|
| Paper outline (sections, tables, figures, experiment checklist E1–E8) | `OIP/docs/paper/outline.md` |
| Spec draft, package layout, verb set, conformance | `OIP/spec/oip-v0.1-draft.md`, `OIP/spec/README.md` |
| Design rules R1–R10 and the three reference protocols | `OIP/docs/01-reference-protocols/comparison-and-lessons.md`, `lsp.md`, `mcp.md`, `model-hardware-standard.md` |
| Vision and scope; research questions (esp. q03 how LLMs read DICOM, q04 DICOM gaps, q05 X-ray and scintigraphy, q11 validation, q12 model-agnostic understanding) | `OIP/docs/00-vision-and-scope.md`, `OIP/docs/02-research-questions/` |
| Bibliography (URLs, arXiv ids, PMC ids: MC-CXR, MedVision, "Your other Left", Set-of-Mark, CXR-LLaVA, MAIRA-2, CheXmask, CXAS, VinDr-CXR, Paraguay bone scans, DICOM and FHIR standards, MCP, LSP, MHS) | `OIP/docs/04-sources.md` → seed for the citation corpus (DOIs to be resolved by `src.citations`). |
| README (diagram, quickstart) and bench README (no-leakage rule) | `OIP/README.md`, `OIP/bench/README.md` |

### 3.5 Provenance facts to record in `oipbench/data/raw/MANIFEST.json`

None of these are stored in the result rows; the ingest must write them down once, from these sources:

- Harness commit per run directory: map each run's timestamp to `git -C ~/oip-work log` (results are not tagged with a commit; the closest preceding bench commit is the best available record, say so).
- Model identities: `claude` = `claude-sonnet-5`, `gpt` = `gpt-5.6-terra`, `gemini` = `gemini-3.8-flash` (from `model_id` in rows); Ollama tags as in the row `model` field (`ollama/<tag>`), Ollama 0.33.3, cloud tags served by Ollama's cloud; local: `gemma4:e4b-it-qat`, `medgemma1.5:4b`.
- SDKs: anthropic 1.7.0, openai 3.16.2, google-genai 2.24.0 (in `~/oip-venv`).
- Prices used for cost figures: from `PRICES` in `run.py` (Sep 2026 price pages); Anthropic cache read at 10 % of input price; observed spend ≈ $61 (Gemini 9, GPT 37, Claude 15).
- Run dates: Ollama sets 8–21 September 2026 (daily and weekly usage throttles interrupted runs; resumed with checkpoints, no rows lost); frontier 21–22 September 2026.
- Selection rules (see 3.2) and the exclusions: `CONTAMINATED-*` dir (leaked box labels, no-leakage rule), NIH `scale_available` (truth ill-defined for low-confidence dataset-derived spacing), smoke dirs deleted before analysis.
- Abstentions are scored incorrect (a stated "cannot determine" on an answerable task); empty replies (three or four for gpt, hidden reasoning consumed the 600-token budget) are scored as abstentions.
- Pilot-vindr-20 rows: superseded for the main tables by the paper sets, but the only source of the `misled_oip_v01` (v0.1 wording) condition; the OEP-001 before/after figure uses them, labelled as the pilot.

### 3.6 Things that do not exist yet and need the user

| Item | Why it blocks | Where it goes |
|---|---|---|
| Funding and competing-interest statements | The manuscript prints an explicit "not declared" marker otherwise; the EBNM audit loop stalled on this | `oipbench/config_oip.yaml` `declarations:` |
| Repository URL and, if possible, a DOI (Zenodo) for code and result files; decision whether the OIP repo goes public with the preprint | "Data and Code Availability" and the reproducibility claim rest on it | `config_oip.yaml` `availability:` |
| Author list and affiliations; venue (outline §10: arXiv first) | Front matter | `papers.yaml` title block / template |
| Whether the 1.8 GB package sets are archived (Zenodo) or only their manifests published | VinDr packages derive from Kaggle competition data (redistribution restricted); NIH and Paraguay (CC-BY-4.0) can be shared | Availability statement |
| CheXmask Tier-2 and expert Tier-3 validation | Not needed for the preprint; the paper says measurement truth is Tier 1 + CXAS cross-check | Limitations; a later amendment |
| Ollama cloud model versions are not pinned by the provider | State as a limitation (same as EBNM) | Limitations |
