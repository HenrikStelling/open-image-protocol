# Runbook — producing the OIP paper with Research_Automation

For a Claude Code session opened in `/Users/pal/Projects/Research_Automation`. Written 2026-09-23 from an analysis of both repos; the inventory it relies on is [handoff-inventory.md](handoff-inventory.md) (same folder, `~/oip-work/docs/paper/`). Everything below is phrased so the session can execute it in order; the parts marked **[user]** are decisions or actions only you can make.

## 0. Before opening the session [user]

1. Decide, or accept the defaults in brackets:
   - Funding statement [“This research received no external funding.”] and competing interests [“The author declares no competing interests.”].
   - Availability: will `HenrikStelling/open-image-protocol` be public at preprint time, and will the result files get a Zenodo DOI? [public repo at preprint time; Zenodo DOI for `bench/results` and the package manifests]
   - Author line and affiliation; venue [arXiv preprint, cs.CV + eess.IV, then NeurIPS Datasets & Benchmarks or a J Imaging Inform Med submission].
   - Paper id in the registry [`oip`]; package name [`oipbench`].
2. Confirm nothing is running in `~/oip-work/bench/results` (no benchmark process; last check 2026-09-22 showed none).
3. Open the session in `/Users/pal/Projects/Research_Automation` on `main` (clean at 2701a78) and paste the kickoff prompt from §1.

## 1. Kickoff prompt (paste verbatim, fill the brackets)

```
Set up and run a new study in this repo: the Open Image Protocol (OIP) benchmark paper.
Follow the runbook at /Users/pal/oip-work/docs/paper/RUNBOOK-research-automation.md and the
inventory at /Users/pal/oip-work/docs/paper/handoff-inventory.md. The OIP source repo is
/Users/pal/oip-work (use it, never /Users/pal/Desktop/OIP). Package name: oipbench. Paper id: oip.
Declarations: funding "[...]"; competing interests "[...]". Availability: repo URL
https://github.com/HenrikStelling/open-image-protocol, DOI [pending / 10.5281/zenodo.xxxx].
Author: Henrik Stelling, [affiliation]. Venue: arXiv preprint.
Work through the runbook phases A to I in order. Do not call any model to produce a number:
the frozen replies in bench/results are the dataset. Stop and ask me only at the points the
runbook marks [user].
```

## Phase A — orientation (read before touching anything)

Read, in this order: `CLAUDE.md` (hard invariants, maintenance protocol), `docs/state/INDEX.md`, `docs/state/shared-infra.md`, `docs/state/isaps-trends.md` (the pattern to copy), `docs/state/audit-chain.md` (headless caller rules), `openclaw-skills/dataset-pipeline/SKILL.md` (the onboarding recipe), then the inventory. Also read the ISAPS thin CLIs you will copy: `isaps/iconfig.py`, `isaps/orchestrate_isaps.py`, `isaps/build_paper_isaps.py`, `isaps/citations_isaps.py`, `isaps/audit_isaps.py`, and `src/audit_eval.py` (the eval-audit prompt you will adapt).

From the OIP side read: `docs/paper/outline.md`, `docs/reports/pilot-ollama-report.md`, `bench/report.py`, `bench/score.py`, `bench/tasks.py`, `bench/run.py`, `docs/03-brainstorm/decisions-log.md` (D-015, D-025 to D-028), `PLAN.md` §Phase 3.

Rules that apply to every step: always `.venv/bin/python` of this repo; never modify `src/`; never install a skill; write helper code to files (the machine-wide "Skill-Audit" hook rejects shell lines with `$(...)` and some inline one-liners); paths inside any headless `claude -p` prompt are `oipbench/`-prefixed.

## Phase B — bring the data in

Create `oipbench/` and `oipbench/data/raw/`. Then copy, without transformation:

```bash
rsync -a --exclude 'CONTAMINATED-*' /Users/pal/oip-work/bench/results/ /Users/pal/Projects/Research_Automation/oipbench/data/raw/bench_results/
```

```bash
cp /Users/pal/oip-bench/meta/vindr_train.csv /Users/pal/oip-bench/cxas_vs_pspnet_20.json /Users/pal/oip-bench/pilot_pkgs.txt /Users/pal/Projects/Research_Automation/oipbench/data/raw/
```

Write and run a script `oipbench/tools/copy_package_meta.py` that copies only `oip.json` and `context.md` from every `*.oip` under `~/oip-bench/vindr-paper`, `nih-paper`, `bonescan` and `vindr` into `oipbench/data/raw/packages_meta/<set>/<package>/`, and records the sha256 of every file in each full package (including renders and pixels) into `packages_manifest.json`. Expected: 190 paper-set packages plus the 20 pilot packages; 3.7 MB of metadata.

Vendor the harness at commit 050769a into `oipbench/vendor/`: `score.py`, `tasks.py`, `run.py`, `report.py`, `context.py` (from `src/oip/`), the manifest schema, and a `VENDOR.md` naming the commit. Only `score.py` is imported; the rest are read by the eval audit and cited in Methods.

Write `oipbench/data/raw/MANIFEST.json` from inventory §3.5: per run directory the sha256 of `results.jsonl` and `tasks.json`, row count, dataset (by the package dir named in `tasks.json`), models, conditions, first and last row timestamps if present, nearest preceding harness commit from `git -C /Users/pal/oip-work log --format='%h %ci %s' -- bench`; plus the model-id table, SDK versions, Ollama version, price table and the exclusion list.

Check `.gitignore` in this repo and commit the raw data and manifests (36 MB + 4 MB + 3.7 MB) as the study's dataset, the way `review/data/` is committed. **[user]** if you would rather keep `vindr_train.csv` out of git (Kaggle terms), say so; the ingest then reads it from `~/oip-bench/meta/` and the manifest records its hash.

## Phase C — the analysis plan, before any analysis code

Write `oipbench/PROTOCOL_oip.md`. Its first paragraph must state that the plan was written on the date of writing, after data collection and after the descriptive scoreboard in `pilot-ollama-report.md` had been seen, so it is a **post-hoc analysis plan** fixed before the inferential analysis code was written, not a pre-registration. Content:

1. **Design as run.** Datasets: VinDr-CXR 100 (stratified sample, seed 0), NIH ChestX-ray14 50, Paraguay bone scans 40 (20 anterior, 20 posterior). Conditions: raw, ctx_l1 (L0–L2 reference file), ctx (full), annot (annotated render + full), misled_plain, misled_oip; bone scans raw, ctx_l1, ctx only. Models: 8 via Ollama (6 cloud, 2 local) and 3 frontier, with effort and token settings from `run.py`. One reply per (model, condition, task); no repeats. Frozen replies are the data; re-scoring from reply text by the vendored scorer is the only scoring path.
2. **Selection rules** (from `report.py`): latest run directory per (dataset, model, condition); tag and condition normalisation; NIH `scale_available` excluded; `CONTAMINATED-*` excluded; error rows excluded from denominators and counted separately; abstentions and empty replies scored incorrect.
3. **Primary endpoint.** Gating accuracy on the four tasks common to all conditions (left_edge, scale_available, ctr ±0.05, heart_mm ±10 %), per model and dataset, contrast **full reference file vs raw**, paired by task item: exact McNemar per model, Wilson 95 % CIs per cell, Holm over the 11 models within a dataset, Cohen's g. Also ctx_l1 vs raw and ctx vs ctx_l1 (layer ablation), same test.
4. **Secondary endpoints.** annot vs ctx; mark_heart and mark_side accuracy (annot only); flip_check vs the 50 % chance level (exact binomial, two-sided, per model and condition); misled_oip vs misled_plain adoption rate (paired McNemar per model) and findings F1 under both; the OEP-001 before/after on the pilot-20 set (`misled_oip_v01` vs `misled_oip`), labelled pilot; bone-scan tasks (left_edge_nm, scale_available_nm, modality_nm, counts_semantics, hot_side, flip_check_nm) with the same tests; cross-model spread = population SD of model accuracies per condition with a bootstrap CI over task items; cost = mean input/output tokens, latency, and list-price dollars per call and per condition; abstention and error counts.
5. **What is descriptive only.** Everything on the pilot-20 set; findings F1 (reported, not gating, D-015); local vs cloud differences (uncontrolled model sizes).
6. **Pre-declared limitations.** Ground truth for CTR and widths is the package's own PSPNet-derived measurement (Tier 1, CXAS cross-check on 20 images), not CheXmask or expert reading; left-edge truth on stripped headers rests on the 1,000-image laterality check; single reply per cell so no run-to-run reliability; cloud model versions unpinned; the reference file was authored by the same project that built the benchmark; ceiling effects at 100 %.
7. **Amendments** section, empty, dated.

**[user]** approve or edit the protocol before Phase D.

## Phase D — scaffold the package (copy ISAPS, point it at OIP)

Files to create in `oipbench/`, each a thin adaptation of its `isaps/` counterpart:

| File | Copied from | What changes |
|---|---|---|
| `config_oip.yaml` | `isaps/config_isaps.yaml` | `study:` name, raw-data paths; `paths:` data/results/paper/literature under `oipbench/`; `declarations:`; `availability:` (repo URL, DOI); `prices:` table; `analysis:` alpha 0.05, correction holm. |
| `papers.yaml` | `isaps/papers.yaml` | One entry `oip`: title (outline §1 candidate 1), `analysis: oipbench.analysis_oip`, `template: template_oip.md`, `prepare: [oipbench.ingest]`, `relevance_keywords`, `pubmed_queries` (see Phase G). |
| `oconfig.py` | `isaps/iconfig.py` | Delegates to `src.paper_registry.Registry`. |
| `ingest.py` | new (the "extract" stage) | Reads `data/raw/bench_results/*/`, applies the selection rules, re-scores every reply with `vendor/score.py`, **asserts stored score == recomputed score for every row (stop on any mismatch and report it)**, writes tidy `data/rows.csv` (one row per reply, with dataset, model, family, condition, task type, item id, correct, abstained, error, f1, adopted_misleading, tokens, cost) and `data/coverage.json` (rows per cell, excluded rows with reasons, error rows). |
| `analysis_oip.py` | `isaps/analysis_*.py` pattern | `compute(cfg)` → `RESULTS/oip/results.json` + figures; `narrative(results)`; `tables(results)`. Uses `src.stats` where a function exists and `statsmodels.stats.contingency_tables.mcnemar(exact=True)`, `statsmodels.stats.multitest.multipletests(method="holm")`, `scipy.stats.binomtest`. Figures via `src.figures.save` and `legend_below`. |
| `template_oip.md` | `isaps/template_*.md` | Jinja template following the outline §3–§9 (see Phase F). |
| `build_paper_oip.py` | `isaps/build_paper_isaps.py` | `provenance_block()` renders: datasets with source, licence, sample sizes and sampling seed; the Ollama and frontier model table with ids, dates, settings; the raw-data manifest hashes; the vendored harness commit. |
| `citations_oip.py` | `isaps/citations_isaps.py` | `_CORE` terms for this domain (see Phase G); corpus seeded from `docs/04-sources.md`. |
| `audit_oip.py` | `isaps/audit_isaps.py` + `src/audit_eval.py` | Three layers: `eval` (adapted prompt: read `vendor/score.py`, `vendor/tasks.py`, `ingest.py`, `analysis_oip.py`, `data/rows.csv`, `RESULTS/oip/results.json`, `PROTOCOL_oip.md`; the same five failure modes as the EBNM eval audit, plus "does the re-scoring assertion exist and is the abstention rule applied as declared"), `claim` (prompt names `oipbench/RESULTS/oip/results.json` as the only number source and lists the honesty points below), `citation` (DOI re-check). |
| `orchestrate_oip.py` | `isaps/orchestrate_isaps.py` | Stages: ingest → analysis → citations → build → audit → peer review; `--paper oip`, `--no-audit`, `--no-peer-review`, `--no-notify`, `--assurance`. The peer-review prompt lists the frozen items (Phase H). |
| `__init__.py` | | empty |

Add the study to the repo record now, not at the end (Phase I lists the entries), because the Stop hook will flag the undocumented modules on every turn otherwise.

## Phase E — ingest and analysis

Run `.venv/bin/python -m oipbench.ingest`. Expected checks it prints: 41 run dirs read; the per-(dataset, model, condition) latest-run table; re-score agreement 100 % (if not, stop: either the vendored scorer differs from the one used, or a stored score was edited); total rows and error rows; the 11 model × 3 dataset coverage grid with no empty cell for the paper sets.

Run `.venv/bin/python -m oipbench.analysis_oip`. Before writing the paper, reconcile: every percentage in `RESULTS/oip/results.json` for the gating table must equal the corresponding cell of `pilot-ollama-report.md` (same rules, same data); write the reconciliation as `RESULTS/oip/reconciliation.md` (cell by cell, identical / differs with reason). A difference is a bug in one of the two, to be resolved before continuing.

`results.json` layout (keep flat and named, the claim auditor reads it cold): `design` (n per dataset, conditions, models with ids and family), `gating` [dataset][model][condition] {n, correct, acc, wilson_lo, wilson_hi}, `contrasts` [dataset][model][pair] {discordant b, c, p_exact, p_holm, cohens_g}, `layer_ablation`, `render_tasks`, `flip` {acc, n, p_vs_chance}, `misled` {adopt_plain, adopt_oip, f1_plain, f1_oip, p_paired}, `oep001_pilot`, `nm`, `spread` {per condition sd, ci}, `cost` {tokens, latency, usd per call and per condition, observed spend}, `abstentions`, `errors`, `coverage`, `provenance` {manifest hashes, harness commit, protocol version, build date}.

Figures (300 dpi, legend below): Fig. 1 gating accuracy raw → L0–L2 → full → annotated per model, two panels (VinDr, NIH), with CIs; Fig. 2 flip check and mark-side per model; Fig. 3 misleading-label adoption plain vs template per model, plus the pilot OEP-001 before/after panel; Fig. 4 tokens and cost per condition; Fig. 5 bone-scan tasks; Fig. 6 (schematic, static) the package tree and manifest excerpt from `spec/`.

## Phase F — template and build

The template follows `outline.md` §3–§9 with these fixed elements: a single-paragraph abstract without labelled sub-headings; Methods that cite `PROTOCOL_oip.md` as a post-hoc plan; a "Data sources and provenance" block from `provenance_block()`; grouped background citations from `src.provenance.cite_clusters` so no reference is orphaned; a Limitations section that contains, verbatim in substance, the six pre-declared limitations of Phase C plus "each cell is one reply; no run-to-run reliability was measured"; the Data and Code Availability text from `config_oip.yaml`; funding and competing interests from `declarations:`; Ethics: public de-identified datasets, no patient data in packages, no ethics approval required.

Honesty points the narrative generator must encode (the claim audit prompt lists the same ones): every gating percentage is quoted with its n; "100 %" cells are called a ceiling, not a difference; a McNemar result is quoted with b and c discordant counts; flip-check results near 50 % are described as chance, not "agreement"; the L0–L2 file's negative effect on NIH for glm and gpt is reported as an abstention effect and quoted with the abstention counts; measurement truth is described as tool-derived and Tier-1 validated; cost numbers are list price at the stated date; the OEP-001 wording result is labelled pilot (n = 20 images).

Build: `.venv/bin/python -m oipbench.build_paper_oip --paper oip` → `oipbench/PAPER/manuscript_oip.{md,docx,html}`. Check that every `{{ }}` rendered and every figure path resolves.

## Phase G — citations

Seed corpus: convert `docs/04-sources.md` into `oipbench/LITERATURE/citations_db.json` (title, DOI or PMID or arXiv id, year) with a script; entries without a resolvable DOI or PMID are kept for the Related-work prose only and flagged. `_CORE` terms for the relevance gate: vision-language, multimodal, radiograph, chest x-ray, chest radiograph, scintigraph, bone scan, dicom, medical image, cardiothoracic. `pubmed_queries` (keep the set small): "vision language model chest radiograph benchmark", "multimodal large language model medical imaging orientation laterality", "cardiothoracic ratio deep learning agreement", "large language model text context misleads image interpretation", "DICOM metadata loss image conversion machine learning". Run `.venv/bin/python -m oipbench.citations_oip --paper oip --top 20`; then rebuild.

## Phase H — audits, peer review, deliverable

1. `.venv/bin/python -m oipbench.audit_oip --paper oip` (eval, claim, citation; advisory at draft). Read the three reports. Fix eval and claim findings **at origin** (ingest, analysis, template), rebuild, re-audit; stop when the numeric layer is clean and the residue is wording only (the repo's known steady state). Do not edit the built manuscript by hand.
2. Peer review handoff via `orchestrate_oip.py` (uses `src.handoff.PEER_REVIEW_TOOLS`); the reviser prompt must freeze: every number to `results.json`, references to `selected_references.json`, the provenance block verbatim, the post-hoc-plan wording, the six limitations, the figure links. Output `oipbench/PAPER/manuscript_oip_revised.{md,docx,html}`.
3. Run `tools/check_humanize_safe.py` only if the `manuscript-humanizer` skill is used on a copy; then re-run the audits.
4. Deliverable: `manuscript_oip_revised.docx` + `peer_review_oip.md` + `RESULTS/oip/` + `PROTOCOL_oip.md`. **[user]** read it before anything is posted.

## Phase I — record the study (maintenance protocol)

- `docs/state/oip-bench.md`: Purpose, Status, Key files, Key decisions (frozen replies as dataset; re-scoring assertion; post-hoc plan; exclusions), Open items (CheXmask, experts, DOI), Last updated.
- `docs/state/INDEX.md`: new row. `CLAUDE.md`: new row in the area table and a dated entry at the top of "Current state".
- Optional, only if you want OpenClaw to run it: `openclaw-skills/oip-paper/SKILL.md` (copy the `isaps-trends` skill's shape), then `tools/sync_openclaw_skills.sh`.
- Commit on a branch, open a PR, merge to `main`; the drift check should be silent after the merge.
- Back in `~/oip-work`: add a PLAN.md entry pointing at the RA study and the deliverable; copy `PROTOCOL_oip.md` and the final `results.json` into `docs/paper/` so the public repo carries the plan and the numbers.

## Definition of done

- Re-scoring agreement 100 %; reconciliation with `pilot-ollama-report.md` cell-identical.
- `results.json` contains every number the manuscript quotes; claim audit numeric layer clean; citation audit PASS; eval audit PASS or WARN with reasons recorded.
- Manuscript states: post-hoc plan, one reply per cell, tool-derived measurement truth at Tier 1, unpinned cloud versions, pilot-only OEP-001 numbers, declarations, availability with URL and DOI.
- `docs/state` and `CLAUDE.md` updated; Stop hook silent; PR merged.

## Gotchas collected from both repos

- Headless auditors run `--safe-mode` and see no CLAUDE.md; the prompt is their whole world, so list the number sources in it.
- The `/peer-review` skill must be available to the reviser (`--allowedTools Skill` is set by `handoff.tool_flags`); if the handoff returns no revision, check `permission_denials` in the CLI output.
- A transient Anthropic outage shows up as audit timeout plus a false citation FAIL; re-run, do not debug.
- Telegram needs `~/.openclaw/openclaw.json`; pass `--no-notify` if it is not configured.
- Pandoc makes docx and html only; PDF needs `brew install basictex` (not installed, not needed for arXiv if the LaTeX route is chosen later).
- The RA venv does not contain the `oip` package and does not need it: `context.md` is pre-rendered in the copied metadata.
- Do not point the ingest at `/Users/pal/Desktop/OIP` (stale) or at `~/oip-bench/smoke` (deleted results, test packages).
