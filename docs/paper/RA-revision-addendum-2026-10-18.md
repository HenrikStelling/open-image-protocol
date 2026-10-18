# Addendum to the RA revision plan — rounds 3 and 3a, the CheXmask cross-check and the CTR denominator, final (2026-10-18)

For the Claude session in `/Users/pal/Projects/Research_Automation`. **Supersedes** `RA-revision-addendum-2026-10-02.md` (written
while round 3a was half done) and `round3a-for-paper.md`; §G of `RA-revision-plan.md` (amendment 12, glm truncation) stays valid
and is referenced here. Same rules as the plan: change only the sources (`ingest.py`, `analysis_oip.py`, `template_oip.md`,
`PROTOCOL_oip.md`, `config_oip.yaml`), never the built manuscript; every number the manuscript quotes comes from `results.json`;
the OIP reports named below are for reconciliation only; rebuild → audit → peer review afterwards. No model is called to produce
a number: all runs are frozen replies, ingested and scored like the paper's.

OIP side: release 0.2.0 (software DOI 10.5281/zenodo.23052075, data DOI 10.5281/zenodo.23040047), working clone `~/oip-work`,
`main` at 82f3e6a. Decisions D-029 … D-034 in `docs/03-brainstorm/decisions-log.md`.

## Kickoff prompt (paste into the RA session)

```
Apply /Users/pal/oip-work/docs/paper/RA-revision-addendum-2026-10-18.md to the OIP study on branch
claude/oip-round3 (create it from main if it does not exist; if it exists from the 10-02 addendum, continue on it
and treat 10-18 as the authoritative version of every section). Parts H to M in this order; change only
ingest.py, analysis_oip.py, template_oip.md, PROTOCOL_oip.md, config_oip.yaml; then ingest → analysis →
citations → build → audit → peer review. Every number in the new sections must come from results.json; the
OIP reports are for reconciliation only. Register the new runs as amendments 12 to 16 as written in part K.
Stop and report if a run directory in part H is missing, if a reconciliation cell differs from the OIP report
by more than rounding, or if the original tables of the paper change in any cell.
```

## What is final now (summary for the author)

1. **Round 3a is complete: ten models, three replies per cell** (seven Ollama models, claude-sonnet-5, gemini-3.8-flash,
   gpt-5.6-terra), 1,056 items per reply. Two models compare the reference file with the pixels (gemini 94 %, gpt 91 % on the
   four conflict cells; both 100 % on the decisive WN cell), glm partly and unstably (61–68 %), seven follow a single source.
2. **OEP-002 closed (D-031):** estimation caution adopted (template 0.2.1); low-confidence guard not adopted. The gpt repeat did
   not reproduce the paper's NIH L0–L2 drop (snapshot drift).
3. **Runtime experiment (D-033):** the Metal kernel workaround on the owner's Mac changes no benchmark cell; dropped.
4. **CheXmask cross-check (D-034 part 1):** thorax width agrees (CCC 0.99), the package heart is 4 % narrower than CheXmask's
   (CCC 0.90), CTR CCC 0.76 with the package 0.02 lower; applied to 1,150 packages as `validation_status: cross_checked`.
5. **CTR denominator settled (D-034 part 2):** on CXAS rib masks the inner rib margin is 1.5–3.4 % narrower than the lung
   union; the package CTR separates the VinDr cardiomegaly label with AUC 0.95; CXAS corroborates the package heart (+1 %).
   The "CTR biased high" remark in the paper's limitations is withdrawn.
6. **Harness provenance:** every round-3 row carries `prompt_sha256`, `reply_sha256`, `rep`, `harness_commit`, `tasks_version`;
   repeats received byte-identical prompts (0 of 10,560 items with more than one prompt hash across repeats, verified 2026-10-18).
   A reply cut off at the output cap before closing its reasoning is scored as no answer (flag `truncated`; glm needs an
   8,000-token cap and still loses 14 %). Cost calibration: token-based estimates under-counted gpt 2.5× (measured on the bill).

## H. Ingest (new raw data, kept apart from the paper's)

Copy the directories below from `/Users/pal/oip-work/bench/results/` into `oipbench/data/raw/bench_results_round3/` (verbatim:
`results.jsonl`, `tasks.json`, `run_meta.json`), extend `MANIFEST.json` with sha256, row counts and harness commits, and add to
`ingest.py` a second ingest path producing `data/rows_round3.csv` with the paper's columns plus `experiment`, `arm`, `cell`, `rep`,
`harness_commit`, `prompt_sha256`, `truncated`. Re-score every reply with the vendored scorer 0.3 and assert agreement with the
stored score, except rows with `score.truncated = true`, whose stored score is the rule "no answer" and must be kept as is.

| experiment | run directory | model | good rows | replies per cell | harness commits (rows) |
|---|---|---|---|---|---|
| ablation (4 arms) | 20260926-121533-claude-31463 | claude-sonnet-5 | 1,200 | 1 | da2c424-dirty, c201602 (resume from a pinned worktree, prompts identical) |
| ablation | 20260926-121533-gemini-31465 | gemini-3.8-flash | 1,197 | 1 | da2c424-dirty |
| ablation | 20260926-121533-gpt-31464 | gpt-5.6-terra | 1,198 | 1 | da2c424-dirty |
| ablation | 20260927-053621-ollama_gemma4_31b-cloud-55206 | gemma4:31b-cloud | 1,200 | 1 | ed33473-dirty |
| ablation | 20260927-053625-ollama_gemma4_e4b-it-qat-55224 | gemma4:e4b-it-qat | 1,200 | 1 | ed33473-dirty |
| ablation | 20260927-062225-ollama_kimi-k3_cloud-74318 | kimi-k3:cloud | 1,200 | 1 | ed33473-dirty, 3ef3013, c201602 (resumes) |
| ablation | 20260927-070107-ollama_medgemma1.5_4b-90804 | medgemma1.5:4b | 1,200 | 1 | ed33473-dirty |
| ablation | 20260928-160019-ollama_glm-5.3-flash_cloud-51311 | glm-5.3-flash:cloud | 1,200 | 1 | 705c155-dirty |
| ablation | 20260928-181318-ollama_mistral-large-3_675b-cloud-79927 | mistral-large-3:675b-cloud | 1,200 | 1 | 32fb8d9 |
| ablation | 20260928-191213-ollama_minimax-m3_cloud-92059 | minimax-m3:cloud | 1,200 | 1 | 32fb8d9 |
| OEP-002 | 20260929-120003-ollama_gemma4_e4b-it-qat-51772 | gemma4:e4b-it-qat | 600 | 1 | dd5e7a2-dirty |
| OEP-002 | 20260929-120003-ollama_glm-5.3-flash_cloud-51751 | glm-5.3-flash:cloud | 600 | 1 | dd5e7a2-dirty (800-token cap; truncation counts in the report) |
| OEP-002 | 20260929-121517-ollama_medgemma1.5_4b-55569 | medgemma1.5:4b | 600 | 1 | dd5e7a2-dirty |
| OEP-002 | 20260929-123925-ollama_gemma4_31b-cloud-65012 | gemma4:31b-cloud | 600 | 1 | dd5e7a2-dirty |
| OEP-002 | 20260929-125349-ollama_kimi-k3_cloud-71551 | kimi-k3:cloud | 600 | 1 | 59627fe-dirty, 2521e5d-dirty |
| OEP-002 | 20260929-132231-ollama_minimax-m3_cloud-81742 | minimax-m3:cloud | 600 | 1 | 2521e5d-dirty |
| OEP-002 | 20260929-134617-ollama_mistral-large-3_675b-cloud-86718 | mistral-large-3:675b-cloud | 600 | 1 | 36d7c20-dirty |
| OEP-002 | 20260929-151043-gpt-4650 | gpt-5.6-terra | 600 | 1 | a7545f1-dirty |
| round 3a | 20260930-152852-ollama_gemma4_e4b-it-qat-24798 | gemma4:e4b-it-qat | 3,168 | 3 | a116105, c8f8ece |
| round 3a | 20260930-154432-ollama_gemma4_31b-cloud-30452 | gemma4:31b-cloud | 3,168 | 3 | 5f83ab6, dd2ed4d, 594e3e7, c8f8ece |
| round 3a | 20260930-174754-ollama_medgemma1.5_4b-62722 | medgemma1.5:4b | 3,168 | 3 | dd2ed4d, c8f8ece |
| round 3a | 20260930-175734-ollama_kimi-k3_cloud-66601 | kimi-k3:cloud | 3,168 | 3 | dd2ed4d, 594e3e7, 6375ced, c590801, e011568, f601a15 |
| round 3a | 20261002-065128-gemini-9124 | gemini-3.8-flash | 3,168 | 3 | 3b49f99, b2c28a2, b52af8b |
| round 3a | 20261002-065128-gpt-9125 | gpt-5.6-terra | 3,168 | 3 | 3b49f99, b2c28a2, 18863ad-dirty, b52af8b |
| round 3a | 20261005-021730-ollama_minimax-m3_cloud-46588 | minimax-m3:cloud | 3,168 | 3 | e011568, d9cd617, 348a194 |
| round 3a | 20261005-033312-ollama_mistral-large-3_675b-cloud-53730 | mistral-large-3:675b-cloud | 3,168 | 3 | bd93d6d, 348a194 |
| round 3a | 20261005-062527-ollama_glm-5.3-flash_cloud-55584 | glm-5.3-flash:cloud | 3,168 | 3 | c8f8ece, c590801, d9cd617 (8,000-token cap; 150 of 1,056 rows per reply truncated) |
| round 3a | 20261005-143507-claude-95017 | claude-sonnet-5 | 3,168 | 3 | a753ba6(-dirty), a24c76f |
| runtime | 20261016-073501-ollama_gemma4_e4b-it-qat-88159 | gemma4:e4b-it-qat | 1,464 | 3 | 5739a5a-dirty; label `runtime:metal_tensor_disabled`, Ollama 0.40.1 |
| runtime | 20261016-081315-ollama_medgemma1.5_4b-89296 | medgemma1.5:4b | 1,464 | 3 | 5739a5a-dirty; same label |
| runtime | 20261016-090740-ollama_gemma4_e4b-it-qat-90972 | gemma4:e4b-it-qat | 1,464 | 3 | 5739a5a-dirty; label `runtime:metal_default` |
| runtime | 20261016-094436-ollama_medgemma1.5_4b-91947 | medgemma1.5:4b | 1,464 | 3 | 03475bb-dirty; same label |
| pixel check | `docs/reports/orientation-pixel-check.json` (100 packages × 3 conditions, offsets per package) | — | — | c201602 |
| CheXmask | `bench/results/_chexmask/vindr-paper.json`, `nih-paper.json`, `vindr-1000.json` (per-image widths, Dice, RCA) | — | 100 / 50 / 1,000 images | `bench/chexmask_validate.py` at 31165fd+ |
| CTR denominator | `bench/results/_chexmask/itw_cxas_100.json` (rib widths in two conventions, three heart widths, label) | — | 100 images | `bench/itw_cxas_eval.py` at 82f3e6a |

Notes. (1) Round-3a rows mix harness commits because repeats 1–2 were added by `--resume` days later; the prompt hashes show
that every item received the same prompt in all three repeats (0 of 10,560 items differ). What changed between those commits
is the scoring of cut-off replies (c8f8ece) and transport settings, not prompts. (2) glm's first round-3a run (2,400-token cap,
328 cut-off replies scored from their fragments) was set aside before the rerun and its rows were lost in a reboot of the owner's
Mac on 2026-10-08; the readings describe it, no number from it is quoted. (3) The ablation runs are identified by
`run_meta.conditions` containing the four arms, not by the latest-run rule. (4) Round-3a tasks: `orient_conflict` (field `cell`:
TN, TM, WN, WM), `badge_read` (field `label_swap`), `mark_side`; conditions `ctx3`, `ctx3_mask`, `labels3`, `annot3`, `annot3_l1`.
(5) `--ollama-think` was `off` for the paper, `auto` since round 3 (think stays false; glm's cap 8,000); the daemon version is in
`run_meta.ollama_version` from 2026-10-07 on (0.33.3 before, 0.35.1 then 0.40.1 after).

## I. `analysis_oip.py`: result blocks

Same conventions as the paper's blocks (Wilson 95 % CIs, exact McNemar on paired items, Holm within a family, n in every cell).

1. `ablation_round3` and 2. `pixel_check` — as specified in the 10-02 addendum (unchanged; the ablation is complete for all
   eleven models including claude's resumed arm).
3. `conflict_round3a` (replaces the 10-02 version). Per model × render (canonical, marker-masked): the four cells (repeat 0,
   with CIs), all-four-cells accuracy, the per-image policy on repeat 0 and **by majority of the three repeats** (compares /
   text only / pixels only / file vs convention / always mirrored / other — definitions in `docs/reports/round3a-2026-09-30.md`
   header; reimplement from rows), the canonical-vs-masked paired contrast (repeat 0; discordant b/c, p, Holm over ten models),
   stability (share of items with the same score in all three repeats; accuracy per repeat), label reading (as shipped /
   swapped), mark side with and without the region list, and reply hygiene (rows with `truncated`, think setting). Reconcile
   with tables 1–7 of the report. Expected headline numbers: gemini 94 % / gpt 91 % four cells, WN 100 % both; compares by
   majority 59 / 64 of 82; glm 61–68 % per repeat; stability claude 100, mistral 100, e4b 100, gemma4:31b 96, MedGemma 96,
   gemini 89, gpt 82, minimax 69, glm 56, kimi 47 %; mask effect gpt −5 pp in every repeat (p = 0.05 uncorrected), gemini none,
   glm −9 pp (p = 0.005, Holm 0.05), kimi 23 → 12 % and minimax 15 → 2 % mirrored detections.
4. `oep002` — as specified on 10-02, now closed: seven Ollama models plus the gpt repeat; truncation counts per cell
   (glm); the decision in the template, not in results. gpt: CTR 22 → 36 % with the caution (p = 0.09), guard neutral, 0
   abstentions; its image-only baseline 24 % against 34 % in the paper run under the same model id.
5. `runtime` (new). For e4b and MedGemma: accuracy per task × condition under the two daemon settings (repeat 0 and pooled),
   paired McNemar on repeat-0 items, stability per runtime, empty / cut-off replies, median latency. Expected: every file-bearing
   cell identical; largest image-only gap e4b left edge 51 vs 43 % pooled (overlapping CIs); 0 empty replies.
6. `chexmask` (new). From the three per-image files: n, mean package / CheXmask, bias, limits of agreement, share within 10 %,
   Lin's CCC and r for heart width, thorax width and CTR; the same restricted to RCA ≥ 0.7; Dice medians; CTR > 0.5 counts.
   Expected (VinDr-100 / NIH-50 / VinDr-1000): thorax CCC 0.993 / 0.967 / 0.990; heart CCC 0.903 / 0.789 / 0.881 with the
   package narrower by 4.0 / 5.5 / 3.7 %; CTR CCC 0.760 / 0.800 / 0.745, package lower by 0.023 / 0.021 / 0.021.
7. `ctr_denominator` (new). From `itw_cxas_100.json`: rib inner margin / lung-union width (two conventions: v2 n = 95 median
   0.985; q25 n = 100 median 0.966), heart width ratios (CXAS/PSPNet 1.010, CheXmask/PSPNet 1.031), AUC of five CTR variants
   against the VinDr "Cardiomegaly" label (22 of 100): package 0.949, rib q25 0.948, rib v2 0.911, CXAS heart 0.903, CheXmask
   0.908; share > 0.50 among the 78 unlabelled (package 12).
8. `template_versions`, 9. `retired_tags` — as on 10-02; add that template 0.2.1 is the shipped default from 2026-09-29 and that
   all 1,150 paper and store packages carry `cross_check` records from 2026-10-17 (so a rerun of the paper's `ctx` cells after
   that date sends a different measurements table).
10. `cost` (new): estimated vs billed where known — gemini round 3a $5.6 (estimate matched), gpt round 3a ≈ $22 per 1,000
    calls on the bill against $8.6 estimated (calibration 2.5), claude per the Anthropic bill (cache reads not captured).

## J. `template_oip.md`

**Results — three new subsections** after the last existing one:

- *Does the reference file make models check it against the image?* (ablation; as on 10-02, all eleven models).
- *A pixel-side orientation check in the tools* (as on 10-02).
- *Conflict trials: which models compare file and image.* The ten-model table (four cells, WN cell, policy by majority of three
  replies, mask effect, stability), then: label reading solved for eight of ten (claude and MedGemma the exceptions: claude
  answers the convention when labels are swapped, 47 %; MedGemma inverts, 0 / 98 %), mark side without the region list 91–99 %
  for every capable model (mistral the one model that needs the names, 91 → 80 %), and three replies per cell for all ten.

**Results §5.8 (measurement validation), replace the paragraph.** The measurements were cross-checked against CheXmask 1.0.0
(HybridGNet masks, PhysioNet, CC BY 4.0) on the 100 VinDr and 50 NIH paper images and on the 1,000-package VinDr store: thoracic
width agrees (CCC 0.99 / 0.97 / 0.99), the package cardiac width is 4–5 % narrower than CheXmask's (CCC 0.90 / 0.79 / 0.88), the
CTR is 0.02 lower (CCC 0.76 / 0.80 / 0.75), and a third segmentation (CXAS) sits 1 % from the package heart. The CTR denominator
was tested against the inner rib margins from CXAS rib masks: the lung-union width equals them within 2–3 %. The package CTR
separates the VinDr "Cardiomegaly" label with AUC 0.95 on the 100 paper images. Packages now carry `validation_status:
cross_checked` with the agreement record; `validated` remains reserved for reference or expert measurements.

**Discussion.** Replace the "no model checks the file against the image" sentence as specified on 10-02 (keep the first half;
restrict the second to the open models and claude; gemini and gpt compare, WN cell 100 %; the four-cell design separates
"compares" from gemma4:31b's "file vs convention" policy, which the flip check could not). Add one sentence each: the marker
mask shows that the partial passes of kimi and minimax rested on the burned-in side marker; repeats show the rule-followers are
deterministic and the two comparers stable with a drift (gemini 94 → 88 % across identical repeats eleven days apart).

**Limitations, replace the CTR sentence** ("lung-union thoracic width underestimates … CTR biased high") with: the thoracic width
is the lung-mask union, which equals the inner rib margin from a second segmentation within 2–3 %; cardiac width differs between
three automatic segmentations by up to 4 %, and no expert-read reference exists for these images. Add: unpinned cloud model tags
(two retired during the study; gemini's accuracy drifted 94 → 88 % across identical repeats); the output cap truncated glm's
reasoning (amendment 12; in round 3a 14 % of its conflict replies even at 8,000 tokens, scored as no answer); the marker-mask
review is an assistant's visual pass over contact sheets, not a radiologist's; the runtime experiment covers one machine and one
daemon.

**Methods.** Paragraph "Post-hoc experiments (amendments 13–16)" as on 10-02, updated: round 3a with three replies per cell for
all ten models (frontier repeats 2026-10-13/15/16, paid by the owner); the truncation rule; the cost calibration.

**Title / abstract.** "…but not the check against the pixels" → "…; only two of ten models check them against the pixels".

**Data and code availability.** Software DOI 10.5281/zenodo.23052075 (0.2.0) next to the data DOI; the round-3 replies and the
CheXmask per-image files go into the next version of the frozen-replies deposit (state the version when it exists).

## K. `PROTOCOL_oip.md`: amendments 12–16 (all post hoc, dated)

- **12** (already drafted in `RA-revision-plan.md` §G): glm output-cap truncation in the paper's L0–L2 numeric cells; limitation, no
  cell changed.
- **13**: the round-3 experiments (ablation, pixel-check evaluation, round 3a, OEP-002) with run directories, endpoints, tests,
  the gates decided before the runs (decisions log D-029–D-032), the four-arm selection rule, the exclusions, the pinned-harness
  resume of claude's arm, and — new — three replies per cell, the majority rule for per-image policies, the truncation rule.
- **14**: CheXmask cross-check (data source, DOI 10.13026/3705-zg36, definitions, agreement statistics, the RCA ≥ 0.7 filter,
  `validation_status: cross_checked` written into the packages on 2026-10-17; packages' reference files changed from that date).
- **15**: CTR denominator test (CXAS rib masks, two inner-margin conventions, the September rib-walk withdrawn, the label AUC as a
  plausibility check); the limitation sentence in the paper replaced accordingly.
- **16**: runtime experiment (Metal kernel switch, Ollama 0.40.1, no effect; the daemon version changed 0.33.3 → 0.35.1 →
  0.40.1 during the study and is recorded per run from 2026-10-07).

## L. Citations (verify each against the canonical source before use)

- CheXmask: Gaggion N. et al., "CheXmask: a large-scale dataset of anatomical segmentation masks for multi-center chest x-ray
  images", Scientific Data 2024; dataset on PhysioNet, "CheXmask Database" v1.0.0, DOI 10.13026/3705-zg36; HybridGNet (Gaggion
  et al., IEEE TMI 2022). CC BY 4.0.
- CXAS: Seibold C. et al., "Accurate fine-grained segmentation of human anatomy in radiographs via volumetric pseudo-labeling",
  2023 (arXiv; the `cxas` package, model UNet_ResNet50_default). Verify venue and year.
- VinDr-CXR labels as already cited.

## M. Then

Rebuild; the reconciliation script must show no change in any cell of the paper's original tables; audits (eval, claim,
citation); peer review; copy the new `PROTOCOL_oip.md` and `results.json` back to `/Users/pal/oip-work/docs/paper/`; record
branch and verdicts in the RA repo's state block.

Honesty points for the claim audit, in addition to the eleven existing and the eight of 10-02: every round-3a cell states
whether it is repeat 0 or the majority of three; "two of ten models compare" is tied to the WN cell; gemini's drift across repeats
is reported; the CheXmask numbers are called a cross-check, never a validation; the CTR limitation is replaced, not deleted
(the 4 % heart-width spread between segmentations stays); the cost figures name what was billed and what was estimated.
