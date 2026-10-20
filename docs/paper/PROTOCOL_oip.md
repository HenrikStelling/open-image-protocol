# OIP-Bench — Analysis Plan (post hoc, fixed before the inferential code)

> **Status of this plan.** Written on **2026-09-23**, *after* all benchmark replies had been
> collected (8–22 September 2026) and *after* the descriptive scoreboard
> `docs/reports/pilot-ollama-report.md` of the OIP repository (regenerated 2026-09-22 19:29) had
> been seen. It is therefore a **post-hoc analysis plan**. It was fixed before any inferential
> analysis code of this study (`oipbench/analysis_oip.py`) was written, and every later change is
> logged, dated, under §7 *Amendments*. It is **not** a pre-registration and must never be described
> as one. The Methods section of the manuscript cites this file by path.

## 1. Design as run

**Object of study.** Whether an Open Image Protocol (OIP) package — a canonical render plus a
fixed-template natural-language reference file (`context.md`, template 0.2) generated from a
schema-validated manifest — changes how well vision-language models answer *understanding*
questions about a medical image (orientation, scale, calibrated measurement, localisation,
render-consistency), compared with the image alone.

**Datasets** (packages built by the OIP converter; no radiologist boxes or finding labels inside
any package — the no-leakage rule):

| Set | Source | Images | Sampling |
|---|---|---|---|
| `paper-vindr-100` | VinDr-CXR (training split, DICOM path) | 100 | stratified by findings / cardiomegaly / spacing, seed 1 (corrected from "seed 0", amendment 10) |
| `paper-nih-50` | NIH ChestX-ray14 (PNG, non-DICOM path, dataset-derived spacing) | 50 | half with / half without a finding label, seed 1 (corrected from "seed 0", amendment 10) |
| `bonescan-40` | Paraguay whole-body bone scans (planar scintigraphy) | 40 (20 anterior, 20 posterior) | balanced by view |
| `pilot-vindr-20` | VinDr-CXR | 20 | pilot set (seed 0); descriptive only (§5) |

**Conditions** (text of `CONDITIONS` in the vendored `run.py`):

| Condition | Input |
|---|---|
| `raw` | canonical PNG only |
| `ctx_l1` | canonical PNG + reference file restricted to layers L0–L2 (identity, geometry, units, orientation, cautions; no computed regions or measurements) |
| `ctx` | canonical PNG + full reference file (adds L3 regions and L4 measurements) |
| `annot` | annotated PNG (edge labels, scale bar, numbered region marks) + full reference file |
| `misled_plain` | canonical PNG + one wrong finding label as a bare "Prior report note" |
| `misled_oip` | canonical PNG + the same wrong label rendered through the shipped template (cautions first, unverified-label wording; = `oip describe --with-external`) |
| `misled_oip_v01` | pilot only: the same label in the v0.1 "External" section wording (superseded by OEP-001 / D-027) |

Bone scans ran `raw`, `ctx_l1`, `ctx` only.

**Tasks** (vendored `tasks.py`, `tasks_nm.py`). CXR: `modality`, `view` (reported, not gating);
gating `left_edge`, `scale_available`, `ctr` (tolerance ±0.05 absolute), `heart_mm` (±10 %
relative), `mark_heart` and `mark_side` (annotated render only), `flip_check` (reference-file
conditions only; two items per image, one mirrored, one not, so a constant answer scores 50 %);
reported-only `findings` (F1 over 14 VinDr labels, VinDr only) and `findings_misled` (answer = true
labels; also records whether the injected wrong label was adopted). Bone scans: `modality_nm`,
`counts_semantics` (reported), gating `left_edge_nm`, `scale_available_nm`, `hot_side` (only where
the image-half count asymmetry exceeds 8 %), `flip_check_nm`.

**Models** (11): three frontier APIs — `claude` = claude-sonnet-5 (effort low, max_tokens 4000,
prompt caching on image and reference-file blocks), `gpt` = gpt-5.6-terra (reasoning effort low,
max_output_tokens 600), `gemini` = gemini-3.8-flash (thinking level low, max_output_tokens 600);
six Ollama cloud tags (gemma4:31b-cloud, glm-5.3-flash:cloud, kimi-k3:cloud, minimax-m3:cloud,
mistral-large-3:675b-cloud, qwen3.5:cloud) and two local tags (gemma4:e4b-it-qat, medgemma1.5:4b),
Ollama 0.33.3, thinking off, output budget 800 tokens. Same system prompt for all. Family labels:
`frontier`, `ollama-cloud`, `ollama-local`.

**Replication.** One reply per (model, condition, task item). No repeats; no run-to-run
reliability can be computed.

**Data.** The frozen replies in `oipbench/data/raw/bench_results/` (41 run directories, hashed in
`MANIFEST.json`) are the dataset. **No model is called to produce any number in this study.**
Re-scoring each reply's text with the vendored scorer `oipbench/vendor/score.py` (commit 050769a)
is the only scoring path; the ingest asserts that the recomputed score equals the stored score for
every non-error row and stops on any mismatch.

## 2. Selection rules (from `report.py` at 050769a, re-implemented in `oipbench/ingest.py`)

1. Dataset of a run = the package directory named in its `tasks.json`
   (`vindr-paper` → paper-vindr-100, `nih-paper` → paper-nih-50, `bonescan` → bonescan-40,
   `vindr` → pilot-vindr-20).
2. Model tag normalisation `:675b:cloud` → `:675b-cloud` (a resume script once wrote the former).
   **Declared deviation from `report.py`:** the tag is normalised *before* the latest-run
   selection (rule 4); `report.py` normalises after it. Only pilot rows are affected (see rule 9
   and amendment 2 for the pooling this caused there).
3. Legacy condition names in rows without a `usage` field (written before 2026-09-09):
   `misled_oip` → `misled_oip_v01`, `misled_oip_strong` → `misled_oip`. **Declared deviation from
   `report.py`:** renamed *before* the latest-run selection (amendment 4); pilot rows only.
4. For each (dataset, model, condition) keep only the rows of the **latest** run directory that
   has rows for that combination (repeated pilot runs are not pooled).
5. `paper-nih-50` `scale_available` rows are excluded (truth ill-defined for low-confidence
   dataset-derived spacing; task builder fixed in commit 2259a54).
6. `CONTAMINATED-*` run directories are excluded (leaked box labels) — not copied into this study.
7. Error rows (`error` set) are excluded from every denominator and counted separately per
   (dataset, model, condition).
8. Abstentions (reply matches the scorer's abstention pattern on an answerable task, or no number
   can be extracted for `ctr`/`heart_mm`) and empty replies are scored **incorrect**; they are
   counted separately.
9. After selection, (dataset, model, condition, task id) must be unique; the ingest asserts it.
   The one known exception is handled by keeping the first reply in file order (amendment 2).

## 3. Primary endpoint

**Gating accuracy** on the four tasks asked in every CXR condition (`left_edge`,
`scale_available`, `ctr` ±0.05, `heart_mm` ±10 %), per model and dataset (paper-vindr-100,
paper-nih-50; on NIH only three, rule 5).

**Primary contrast: full reference file (`ctx`) vs image only (`raw`)**, paired by task item.

- Per cell: n, correct, accuracy, Wilson 95 % CI.
- Per (dataset, model): exact McNemar test on the discordant pairs b (raw correct, ctx wrong) and
  c (raw wrong, ctx correct); items missing in either condition (error rows) are dropped from the
  pair set and counted.
- Holm correction over the 11 models within a dataset (one family per dataset and contrast).
- Effect size Cohen's g = max(b, c)/(b + c) − 0.5, with the direction stated; the accuracy
  difference in percentage points is reported alongside.

**Layer ablation** (same test, same correction, separate families): `ctx_l1` vs `raw` (what the
L0–L2 layers alone contribute) and `ctx` vs `ctx_l1` (what regions and computed measurements add).

## 4. Secondary endpoints

1. **Annotated render:** `annot` vs `ctx` on the four common tasks (McNemar, Holm over models);
   `mark_heart` and `mark_side` accuracy in `annot` with Wilson CIs; `mark_side` vs 50 % (exact
   binomial, two-sided).
2. **Flip consistency:** `flip_check` accuracy per model × condition (`ctx_l1`, `ctx`) × dataset vs
   the 50 % chance level (exact binomial, two-sided, Holm over the 11 models within dataset ×
   condition). Also reported: the share of images whose mirrored *and* unmirrored item are both
   correct.
3. **Misleading text** (paper-vindr-100): adoption rate of the injected wrong label under
   `misled_plain` and `misled_oip`, paired by image, exact McNemar per model, Holm over 11; mean
   findings F1 under both conditions (descriptive, D-015).
4. **OEP-001 before/after** (pilot-vindr-20, labelled *pilot*): adoption under `misled_oip_v01` vs
   `misled_oip` per model where both exist; paired counts, descriptive (n = 20 images).
5. **Bone scans** (bonescan-40): per task accuracy by condition with Wilson CIs; NM gating
   aggregate on the tasks asked in all three conditions (`left_edge_nm`, `scale_available_nm`,
   `hot_side`) with `ctx` vs `raw` and `ctx_l1` vs `raw` McNemar (Holm over 11);
   `left_edge_nm` split by view (posterior views are displayed mirrored); `flip_check_nm` and
   `hot_side` vs 50 % (exact binomial).
6. **Cross-model spread** per dataset and condition: population SD of the 11 model gating
   accuracies, with a percentile bootstrap 95 % CI resampling task items (2,000 replicates, seed 0,
   the same resampled items for every model).
7. **Cost:** per model and condition, mean and median total input tokens, output tokens and
   wall-clock latency per call; list-price US$ per call and per condition for the three frontier
   models. For `claude`, total input = `input_tokens` + `cache_read_input_tokens` +
   `cache_creation_input_tokens` (the provider reports `input_tokens` net of cache), priced at
   input, 10 % and 125 % of the input price respectively. Latency is wall-clock per call and
   includes client-side retry back-off. Ollama calls are billed by plan allowance, so they get
   token counts, no dollars. The observed spend (≈ US$61) is quoted as reported in the run log.
8. **Abstentions and errors** per (dataset, model, condition).
9. **Measurement-truth cross-check** (descriptive): on the 20 pilot images, agreement between the
   package's PSPNet-derived cardiac width / CTR and an independent CXAS segmentation
   (`cxas_vs_pspnet_20.json`): mean difference, SD, 95 % limits of agreement, and the share of
   images within ±10 % (cardiac width) and ±0.05 (CTR) — the benchmark's own tolerances.
10. **Converter facts and sampling record** (descriptive, amendment 10): per source (VinDr-CXR,
   RSNA Pneumonia, SIIM-ACR, NIH ChestX-ray14), the counts the OIP converter reported in
   `reference/phase2-conversion-stats.json` (spacing source, spacing confidence, photometric
   interpretation, bit depth, display window, orientation, transfer syntax, image width from the
   header spacing, quality flags, reference-file length, package/source size ratio); the VinDr-CXR
   anatomy-adapter summary of `reference/phase2-measurement-report.md` (CTR distribution, regions
   per image, millimetre widths reported vs refused); the number of bone-scan packages whose
   manifest carries the inferred count-recovery extension; and, per benchmark set, the sampling
   rule with the seed that reproduces the set (`tools/verify_sampling.py` →
   `data/raw/sampling_check.json`). Copied reports and manifests only; no benchmark reply is read.
11. **Scorer-0.3 sensitivity** (amendment 11): every selected paper-set reply re-scored with the OIP
   project's revised scorer 0.3; primary contrast, layer ablation, full-file flip check, bone-scan
   aggregate and abstention counts recomputed with the same selection, tests and corrections, and
   label adoption re-derived with word-boundary matching. Reported alongside; never replaces the
   primary scorer-0.2 results.

## 5. Descriptive only (no inferential claims)

- Everything on `pilot-vindr-20` (incl. §4.4).
- Findings F1 (reported, not gating — D-015).
- Differences between model families (local vs cloud vs frontier): model size, provider and
  settings are uncontrolled.
- Cost and latency.
- The CXAS cross-check (§4.9).
- Converter facts and the sampling record (§4.10).
- The scorer-0.3 sensitivity analysis (§4.11, amendment 11).
- The round-3 experiments, the CheXmask cross-check, the CTR-denominator test and the runtime test (amendments
  12–16): post hoc; their tests are exploratory and are reported apart from the paper's primary and secondary endpoints.

## 6. Pre-declared limitations

1. Ground truth for `ctr` and `heart_mm` is the package's own PSPNet-derived measurement
   (validation Tier 1) with a 20-image CXAS cross-check (§4.9); not CheXmask (Tier 2) or expert
   reading (Tier 3), both pending. The benchmark therefore measures whether models *use* the
   package's measurements, not whether those measurements are correct.
2. Left-edge truth on VinDr (headers stripped of orientation) rests on the converter's inferred
   orientation, supported by a 1,000-image laterality sanity check (0 flags).
3. One reply per cell; no run-to-run reliability was measured.
4. Cloud model versions (Ollama cloud tags, provider endpoints) are not pinned by the providers.
5. The reference file and its template were authored by the same project that built the
   benchmark and its tasks.
6. Ceiling effects: many `ctx`/`annot` cells are at or near 100 %; such cells are reported as a
   ceiling, not as a difference between models.
7. The two `flip_check` items per image are not independent; the binomial tests treat them as
   independent.
8. This plan is post hoc (see the status note above).

## 7. Amendments

*(each entry: date, change, reason, whether it was made before or after seeing the affected
result)*

1. **2026-09-23 — re-score assertion, abstention flag.** The first ingest run stopped on 15
   re-score mismatches. All 15 are in two `pilot-vindr-20` `raw` runs of 2026-09-08
   (glm-5.3-flash 14, kimi-k3 1, all `scale_available`). They agree with the vendored scorer on
   `correct` and differ only in the `abstained` key, which the scorer began to emit at bench commit
   4a29137 (2026-09-09 10:07), after those rows were stored. Change: the assertion now requires
   every key to agree, except that a row stored before that commit may lack `abstained`; any other
   difference still stops the ingest. The recomputed score (with the flag) is used throughout, in
   line with §1 (re-scoring is the only scoring path). Made after seeing the mismatch and before any
   inferential analysis; it changes only abstention counts on the pilot set, which is descriptive
   (§5).
2. **2026-09-23 — repeated pilot replies (rule 9).** The uniqueness check found 245 duplicate keys,
   all in one pilot run (`20260908-170632-…mistral-large-3…`): after a resume that wrote the other
   tag spelling, the runner did not recognise rows already done and asked `raw` (138) and `ctx`
   (107) a second time in the same directory. `report.py` pooled both replies (its pilot mistral
   n = 156 = 2 × 78). Of the 245 repeats, 211 have the identical reply and score, 34 differ. Change:
   keep the first reply in file order (the original ask) and count the repeat as excluded; any
   other duplicate still stops the ingest. Made after seeing the duplicates, before any inferential
   analysis; pilot rows only (descriptive, §5).
3. **2026-09-23 — CXAS cross-check units (§4.9).** Two of the 20 cross-check images have no pixel
   spacing and one is in pixel units (spacing 1.0), so cardiac width is compared as the relative
   difference (CXAS − package)/package in %, on the 18 images with both widths; CTR is compared on
   all 20. Also reported: how often CXAS's own thoracic width falls more than 20 % below the
   lung-field width, since that drives the CTR disagreement. Made after first opening the file;
   descriptive only.
4. **2026-09-23 — legacy condition rename before the latest-run selection (rule 3).** The
   reconciliation (`RESULTS/oip/reconciliation.md`) found four pilot cells for the two local models
   that differ from `report.py`. Cause: `report.py` renames legacy conditions *after* choosing the
   latest run per raw condition name. For gemma4:e4b-it-qat and medgemma1.5:4b, the v0.1-wording rows
   (run 20260908-161636, raw name `misled_oip`) were therefore dropped in favour of a later run that
   reused the raw name for the shipped template, and the 2026-09-08 `misled_oip_strong` rows were
   pooled with that later run (report n = 140 = 100 + 2 × 20). This study renames first, then
   selects the latest run per *resolved* condition: 20 shipped-template rows (the latest run) and 20
   v0.1 rows per local model on the pilot set. Made after seeing the reconciliation; pilot rows only
   (descriptive, §5); it adds the two local models to the OEP-001 before/after table.
5. **2026-09-23 — added descriptive analysis: which answers the reference file states
   (`oipbench/answer_in_file.py`).** While drafting the Results it became clear that the full
   reference file states the scored answer in text for the orientation, scale, CTR and
   cardiac-width items and, through the region list, for the two mark tasks; only the flip-check
   and hotter-side items require comparing pixels with text. The primary contrast (§3) therefore
   measures whether a model *uses* facts the package states, not whether it perceives them in the
   image. Change: a deterministic per-item check of the copied `context.md` files (rules in the
   module docstring) is reported as a descriptive analysis, and the manuscript interprets the
   primary contrast accordingly. No test, endpoint or correction changes. Made after seeing the
   results.
6. **2026-09-23 — bone-scan hotter-side items restricted to the common set.** While checking the
   figures it became clear that the two local models (run 20260910-061756) were asked the
   hotter-side question on 22 images, all other models on 8: the local run predates bench commit
   2bf9080 (2026-09-10 07:16), which raised the asymmetry threshold to 8 %. Change: `hot_side` and
   the bone-scan gating aggregate use only the items asked of every model; the manuscript states the
   difference. The other bone-scan tasks are identical across models. Made after seeing the results.
7. **2026-09-23 — changes after the independent eval and claim audits
   (`RESULTS/oip/eval_audit.md`, `claim_audit.md`).** (a) Holm correction over models was applied to
   the mark-side binomial tests although §4.1 did not declare it; declared here (conservative).
   (b) Added sensitivity analyses (`oipbench/sensitivity.py`): a second, stricter parser that
   scores only each reply's final answer for the orientation, flip-check and measurement tasks
   (agreement with the vendored scorer reported; the vendored scorer stays primary), and an
   image-level cluster bootstrap for the primary contrast. (c) §4.7 corrected: latency includes
   client retries only for the frontier APIs; for Ollama it is the successful call. (d) Noted: the
   vendored scorer's abstention flag misses some explicit abstentions on questions whose answer is
   "no" (correctness unaffected). (e) The hotter-side truth (pixel-count heuristic) is added to the
   tool-derived truths of §6. (f) `dropped_unpaired` now counts items missing on either side.
   Made after seeing all results; no primary test or endpoint changed.
8. **2026-09-23 — disclosures after the round-2 eval audit.** (a) The `misled_oip` arm embeds the
   label in the full reference file, so the misleading-text contrast does not separate wording from
   the surrounding facts and cautions; the manuscript says so, and the wording-only comparison is the
   pilot OEP-001 result. (b) The 40 bone scans are 20 patients in two views; the tests treat views as
   independent. (c) The re-score assertion establishes deterministic scoring from the frozen text
   (stored scores were re-applied with `bench/rescore.py` after scorer fixes). (d) Units are not
   normalised by the scorer. (e) The excluded CONTAMINATED run is now recorded (rows, sha256) in
   `MANIFEST.json`. (f) The sensitivity parser treats "do not agree" as mirrored. No analysis changed.
9. **2026-09-23 — disclosures after the round-4 eval audit.** The abstention flag is unreliable in
   both directions (limitation reworded); centimetre-like cardiac-width answers are counted per
   condition (`results.json` `cm_like_heart_answers`); `rows.csv` gains `reply_sha256` so each
   scored reply can be matched to the frozen text; Methods names the selection-order deviations.
   No analysis changed. The audit loop stops here: the numeric layer has been declared clean by
   the claim audit in three consecutive rounds, and the remaining eval findings are minor.
10. **2026-09-23/24 — descriptive converter fields added (§4.10); sampling seed corrected.** Made
   after the peer review, to give the new protocol-motivation section (manuscript §3.8) numbers
   that trace to `results.json`: per-source conversion statistics, measurement-report summaries and
   the bone-scan count-recovery count, read from the copied OIP reports and package manifests, and
   the sampling rule of each benchmark set. Descriptive only; no test, selection rule or reply
   changed, and the scoreboard reconciliation is unaffected. **Correction:** this plan (§1) and the
   manuscript said the two paper sets were drawn with seed 0. Re-running each selection rule
   against the raw sources (`tools/verify_sampling.py`, recorded in `data/raw/sampling_check.json`)
   reproduces `paper-vindr-100` (100/100) and `paper-nih-50` (50/50) only with **seed 1**, the
   default of the OIP sampling script (`scripts/make_bench_set.py`); seed 0 reproduces 12/100 and
   0/50. The pilot set is reproduced by seed 0 (20/20). The bootstrap seed (0) is unrelated.
   **Also disclosed:** the misleading-label draw (`vendor/tasks.py` seeds it with Python's per-process
   string hash, so labels are identical across the two arms within a model but differ between models;
   `results.json` `misled_summary.label_draw`). **After the round-5 eval audit (same day):** the
   per-item truth balance of `left_edge` and `scale_available` (`results.json` `truth_balance`) is
   reported, and the ingest asserts that each (dataset, task id) has one ground truth across runs
   (holds for all 2,132; `rows.csv` byte-identical). Not changed, and listed as known: substring
   matching of finding labels ("ILD" in "mild") and the order-dependent abstention flag in the vendored
   scorer, the uncovered yes/no branch of the strict parser, the hot-side restriction also applying
   to the bone-scan abstention table, and the observed spend quoted from the run log.
11. **2026-09-28 — sensitivity analysis: revised scorer 0.3 (§4.11).** Added after the paper's eval
   audit and peer review, once the OIP project had released scorer 0.3 (OIP commit da2c424, copied
   unchanged to `vendor/score_v03.py`; the harness analysed here is tagged `paper-v1` = 050769a).
   `scorer_sensitivity.py` re-scores every selected paper-set reply with it (after asserting that the
   vendored scorer 0.2 reproduces `rows.csv` on the same reply–task pairs) and recomputes, with the
   same selection, tests and corrections: the primary contrast, the layer ablation, the flip check
   with the full file, the bone-scan gating aggregate and the abstention counts. Scorer 0.3 still
   matches finding labels as substrings, so label adoption is also re-derived with word-boundary
   matching. Results in `results.json` `sensitivity.scorer_v03`. **The primary scoring path stays
   scorer 0.2**; this is a sensitivity analysis, made after the results were seen. Outcome, reported
   in §5.9 of the manuscript: 245 correctness changes (222 from glm-5.3-flash, whose replies carry a
   visible reasoning block); primary contrast unchanged (11/11 on both radiograph sets); flip-check
   models above chance unchanged; word-boundary matching changes no adoption; the NIH L0–L2 drop stays
   significant for gpt only (glm-5.3-flash no longer), and the bone-scan aggregate improves
   significantly for 6 rather than 7 of 11 models. **Added the same day after the round-6 eval audit:**
   both scorers accept a side (left edge, hotter side, mark side) only in the literal form "patient
   right/left", so possessive answers ("the patient's right side") are scored wrong. A third variant
   applies scorer 0.3 to the reply with "patient's" normalised to "patient" (side tasks only;
   `results.json` `sensitivity.scorer_v03.possessive_side_rule`): 256 side answers change (177
   medgemma1.5:4b); the primary contrast stays 11/11 on both sets; the manuscript's "below chance"
   mark-side result for medgemma1.5:4b (28 %, VinDr) becomes 49 % (Holm-adjusted p = 1.0), so §5.4 now
   reports it as an answer-formatting artefact instead of a mark–region confusion.

The following amendments (12–16) were written on **2026-10-18**, after all runs they describe, from the OIP
addendum `docs/paper/RA-revision-addendum-2026-10-18.md`. All are **post hoc**. The round-3 data are new frozen
replies collected after the paper's run; they are ingested on a separate path (`ingest.ingest_round3` →
`data/rows_round3.csv`), analysed in `results.json` `round3`, and **never change a cell of the paper's original
analyses** (verified: `results.json` differs from the pre-round-3 build only by the added `round3` block and the
build date; scoreboard reconciliation unchanged).

12. **2026-09-29 (written 2026-10-18) — glm-5.3-flash output-cap truncation in the paper run; limitation, no cell
   changed.** glm-5.3-flash is the only paper model that reasons visibly inside the reply and closes with `</think>`.
   The harness capped Ollama replies at 800 tokens; a reply at the cap with no closing `</think>` was cut off inside
   its reasoning and the scorer read a number from the fragment. Counted from the frozen replies (`results.json`
   `round3.truncation_paper`): L0–L2 arm VinDr-CXR CTR 33/100, cardiac width 57/82; NIH CTR 20/50, cardiac width 13/50;
   image-only 4–7 per cell; full-file and annotated cells 0; categorical tasks 0. On complete replies the L0–L2 drop
   remains but is smaller (VinDr CTR 52 → 39 %, NIH 59 → 40 %, vendored scorer). Also counted, not described in the OIP
   readout: 18 replies of two other models reached the cap on the numeric tasks (kimi-k3 5, medgemma1.5:4b 13, 17 of
   them in L0–L2 cells); those models write no reasoning markup, so whether they were cut off before answering cannot
   be told from the text. No re-scoring, no re-run for the paper.
13. **Round-3 experiments (ablation, pixel-check evaluation, round 3a, OEP-002).** Runs (32 directories with the
   runtime runs of amendment 16; listed in `config_oip.yaml` `round3.runs`, copied verbatim with sha256 in
   `data/raw/bench_results_round3/MANIFEST.json`):
   (a) *Verification ablation* (OEP-003/004), 10 models (qwen3.5:cloud retired 2026-09-25, before round 3), 100 VinDr-CXR
   images, arms `ctx_ctl` (shipped file, same-day control), `ctx_cue`, `ctx_instr`, `ctx_cue_instr`; tasks flip check
   (two items per image) and left edge; one reply per cell. Runs selected by `run_meta.conditions` containing the four
   arms, not by the latest-run rule (the render-probe runs reused `ctx_ctl` on 40-image subsets and are excluded).
   Endpoints: per model × arm flip-check accuracy, mirrored items detected, left-edge accuracy; contrasts arm vs
   control on paired items (exact McNemar, Holm over the three arms per model). Gate written in the OIP decisions log
   before the runs (OEP-003/004 entry): +20 pp on the flip check for at least two of three frontier models without a
   left-edge loss. Claude's arm was resumed on 2026-10-02 from a pinned worktree of c201602 because the working clone's
   template had moved to 0.2.1; the dry-run text-token counts per arm were identical, so the prompts were the same.
   (b) *Pixel-check evaluation* (D-029): `oip check` on the 100 VinDr paper packages, shipped / masks mirrored /
   mirrored and re-segmented; the two-pass verdict recomputed here from the per-package offsets.
   (c) *Round 3a* (D-032): conflict trials (file labels true/swapped × image normal/mirrored, cells TN TM WN WM) on the
   canonical and on a marker-masked render (82 images with a reviewed mask), printed-label reading (labels as shipped
   or swapped, truth balanced), mark side with and without the region list; 10 models, **three replies per cell**
   (repeats 1–2 added by `--resume`; 0 of 10,560 round-3a items received more than one prompt across repeats). Tests:
   Wilson CIs; canonical vs masked exact McNemar on paired items, Holm over models; stability = share of items with
   the same score in all repeats. Per-image policy (compares / file only / pixels only / file vs convention / always
   mirrored / other) on repeat 0 and **by majority** (a verdict needs at least two of three replies; items with all
   three repeats only). Gate for "compares": the WN cell. **Truncation rule** (OIP c8f8ece): a reply cut off at the
   output cap before it closes its reasoning is scored as no answer (`score.truncated`); glm's cap was raised to 8,000
   tokens, its first round-3a run (2,400-token cap) was set aside and its rows were lost; no number from it is used.
   (d) *OEP-002* (D-031): NIH-50, seven Ollama models plus a pre-specified gpt repeat; arms `raw_ctl`, `ctx_l1_ctl`,
   `ctx_l1_oep2` (low-confidence guard), `ctx_l1_oep2e` (guard + estimation caution); tasks CTR, cardiac width, left
   edge; contrasts against `ctx_l1_ctl` (exact McNemar; Holm over models for the CTR caution contrast). The OIP-side
   decisions (estimation caution adopted as template 0.2.1; guard, cues, instruction and the render probe not adopted)
   were taken against gates written before the respective runs (decisions log D-029–D-032).
   Scoring: the vendored scorer 0.3 (da2c424) with the two round-3 type mappings of OIP a116105 (`orient_conflict` →
   flip rule, `badge_read` → left-edge rule); the ingest asserts recomputed = stored for every non-error, non-truncated
   reply (53,803 of 53,803); truncated replies (528) keep their stored score, and the ingest asserts that each of them is a
   length cut-off without a closing reasoning tag, scored wrong. Harness state: rows produced by a harness with
   uncommitted changes (commit suffix `-dirty`, recorded per run in the round-3 MANIFEST and counted in
   `coverage_round3.json`): ablation 8,146 of 12,000, OEP-002 4,800 of 4,800, round 3a 1,123 of 31,680, runtime
   5,856 of 5,856. Their prompts cannot be rebuilt from a commit alone; for round 3a the stored `prompt_sha256`
   shows one prompt per item across repeats, for the claude ablation arm the dry-run token counts above. Cost: token-based list-price estimates, with
   the owner-reported bills quoted from the OIP PLAN (gpt about 2.6 times the estimate: US$22 billed per 1,000 calls
   against US$8.42 estimated). Reconciliation with the OIP reports was a **manual comparison** on 2026-10-18 (scripts
   outside the pipeline; no artefact in this tree) against the OIP reports in `~/oip-work/docs/reports/`
   (`round3a-2026-09-30.md`, `pilot-ollama-report.md`, `oep-002-2026-09-29.md`, `runtime-2026-10-16.md`) and the
   copied OIP files in `data/raw/round3_files/`: round3a tables 1–7, 130 rows identical; ablation, pixel check, OEP-002, runtime,
   CheXmask, CTR denominator identical; the ablation's paper-run column agrees when both sides use scorer 0.3.
14. **CheXmask cross-check (D-034 part 1).** CheXmask 1.0.0 (HybridGNet masks; PhysioNet, DOI 10.13026/3705-zg36,
   CC BY 4.0) on the 100 VinDr and 50 NIH paper images and the 1,000-package VinDr store; per-image files from OIP
   `bench/chexmask_validate.py` (copied to `data/raw/round3_files/`). Definitions on both sides: width = maximum
   horizontal extent of the mask, thorax = union of both lungs, CTR = heart / thorax. Statistics: bias (package −
   CheXmask) and Bland–Altman limits, relative bias = mean of per-image relative differences, share within 10 %, Lin's
   CCC, Pearson r, Dice medians, CTR > 0.5 counts; the same restricted to CheXmask Dice RCA (mean) ≥ 0.7. Since
   2026-10-17 all paper and store packages carry `validation_status: cross_checked` with the agreement record, so the
   packages' reference files changed from that date (a rerun of the paper's `ctx` cells would send a different
   measurements table). Reported as a cross-check, never as a validation.
15. **CTR denominator test (D-034 part 2).** CXAS rib masks on the 100 VinDr paper images; two inner-margin
   conventions (v2: end of the lateral-most rib run, fails on 5 images; q25: outer edge minus the 25th-percentile run
   length); the September rib-walk (`internal_thoracic_width_px`, followed oblique ribs into the lung field) withdrawn.
   The AUC of five CTR variants against the VinDr "Cardiomegaly" label is a plausibility check, not a reference. The
   paper's limitation that the lung-union thoracic width makes the CTR "probably biased high" is **replaced** (not
   deleted): the lung union equals the inner rib margin within 1.5–3.4 %, and the cardiac width differs between three
   automatic segmentations by up to 5.5 % on average.
16. **Runtime experiment (D-033).** gemma4:e4b-it-qat and medgemma1.5:4b under Ollama 0.40.1 with the Metal tensor
   kernels disabled (`GGML_METAL_TENSOR_DISABLE=1`, the workaround used since 2026-09-08) and enabled; 50 VinDr items,
   conditions raw and ctx, three replies per cell. No effect: every file-bearing repeat-0 cell identical except
   MedGemma's left edge (76 vs 72 %, p = 0.82); image-only differences within noise once pooled. The daemon version
   changed 0.33.3 → 0.35.1 → 0.40.1 during the study and is recorded per run (`run_meta.ollama_version`) from
   2026-10-07.

