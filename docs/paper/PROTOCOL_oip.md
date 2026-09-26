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

## 5. Descriptive only (no inferential claims)

- Everything on `pilot-vindr-20` (incl. §4.4).
- Findings F1 (reported, not gating — D-015).
- Differences between model families (local vs cloud vs frontier): model size, provider and
  settings are uncontrolled.
- Cost and latency.
- The CXAS cross-check (§4.9).
- Converter facts and the sampling record (§4.10).

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

