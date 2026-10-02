# Addendum to the RA revision plan — round-3 results into the OIP paper (2026-10-02)

For the Claude session in `/Users/pal/Projects/Research_Automation`. Base: `main` at 0143284, where the revision plan A–F, amendment 11 (scorer-0.3 sensitivity) and the Zenodo DOIs are in and the claim audit reads PASS. Same rules as the plan: change only the sources (`ingest.py`, `analysis_oip.py`, `template_oip.md`, `PROTOCOL_oip.md`, `config_oip.yaml`), never the built manuscript; every number the manuscript quotes comes from `results.json`; rebuild → audit → peer review afterwards. No model is called to produce a number: the new runs below are frozen replies, ingested and scored like the paper's.

What changed on the OIP side since the revision plan (all in `~/oip-work`, release 0.2.0, software DOI 10.5281/zenodo.23052075, data DOI 10.5281/zenodo.23040047):

- **OEP-003/004 closed, not adopted** (decisions log, entries "OEP-003 / OEP-004" and its two measured addenda). Four-arm ablation on eleven models: cue-bearing reference file, a verify sentence in the system prompt, both, against a same-day control. Report: `docs/reports/pilot-ollama-report.md`, section "Verification ablation".
- **D-029, `oip check`**: a pixel-side orientation check in the tools, two-pass to cancel the segmentation model's positional prior. Evaluation on mirrored copies of the 100 VinDr paper packages: `docs/reports/orientation-pixel-check.md` and `.json`.
- **Round 3a** (conflict trials, marker-masked render, label reading, mark side without the region list): `docs/reports/round3a-2026-09-30.md` and `round3a-readings.md`. Six of nine models complete (gemini, gpt, gemma4 31B, gemma4 e4b, MedGemma; kimi at 914 of 1,056 rows); minimax, mistral and glm still queued behind the Ollama allowance.
- **OEP-002 closed, D-031**: the estimation caution is adopted as template 0.2.1; the low-confidence guard is not. Report `docs/reports/oep-002-2026-09-29.md`. The paper's own measurements used template 0.2; 0.2.1 postdates them.
- **OEP-005 / D-030**: an encoder-safe inspection sheet does not change whether models check the pixels; not adopted. `docs/reports/render-probe-2026-09-27.md`.
- `qwen3.5:cloud` was retired by Ollama on 2026-09-25 (HTTP 410), after the paper run and before round 3; a second retired tag after qwen3-vl.

## Kickoff prompt (paste into the RA session)

```
Apply /Users/pal/oip-work/docs/paper/RA-revision-addendum-2026-10-02.md to the OIP study on a new branch
claude/oip-round3 from main (0143284). Parts H to M in this order; change only ingest.py, analysis_oip.py,
template_oip.md, PROTOCOL_oip.md, config_oip.yaml; then ingest → analysis → citations → build → audit →
peer review. Every number in the new sections must come from results.json; the OIP reports are for
reconciliation only, never a source of a number. Register the new runs as amendment 13 (post-hoc, new data
collection after the paper's). Stop and report to me if a run directory listed in part H is missing or if a
reconciliation cell differs from the OIP report by more than rounding.
```

## H. Ingest the round-3 runs (new raw data, kept apart from the paper's)

Copy the directories below from `/Users/pal/oip-work/bench/results/` into `oipbench/data/raw/bench_results_round3/` (verbatim: `results.jsonl`, `tasks.json`, `run_meta.json`), extend `MANIFEST.json` with their sha256, row counts and harness commits, and add to `ingest.py` a second ingest path that produces `data/rows_round3.csv` with the same columns as `rows.csv` plus `experiment`, `arm`, `cell`, `rep`, `harness_commit`. Re-score every reply with the vendored scorer 0.3 and assert agreement with the stored score, as the paper's ingest does.

| experiment | run directory | model | rows | harness |
|---|---|---|---|---|
| ablation (4 arms) | 20260926-121533-claude-31463 | claude-sonnet-5 | 1,200 | da2c424-dirty (551 rows, 26 Sep) + c201602 (649 rows, resumed 2 Oct from a pinned worktree; prompts byte-identical, see note) |
| ablation | 20260926-121533-gemini-31465 | gemini-3.8-flash | 1,200 | da2c424-dirty |
| ablation | 20260926-121533-gpt-31464 | gpt-5.6-terra | 1,200 | da2c424-dirty |
| ablation | 20260927-053621-ollama_gemma4_31b-cloud-55206 | gemma4:31b-cloud | 1,200 | ed33473-dirty |
| ablation | 20260927-053625-ollama_gemma4_e4b-it-qat-55224 | gemma4:e4b-it-qat | 1,200 | ed33473-dirty |
| ablation | 20260927-062225-ollama_kimi-k3_cloud-74318 | kimi-k3:cloud | 1,200 | ed33473-dirty |
| ablation | 20260927-070107-ollama_medgemma1.5_4b-90804 | medgemma1.5:4b | 1,200 | ed33473-dirty |
| ablation | 20260928-160019-ollama_glm-5.3-flash_cloud-51311 | glm-5.3-flash:cloud | 1,200 | 705c155-dirty |
| ablation | 20260928-181318-ollama_mistral-large-3_675b-cloud-79927 | mistral-large-3:675b-cloud | 1,200 | 32fb8d9 |
| ablation | 20260928-191213-ollama_minimax-m3_cloud-92059 | minimax-m3:cloud | 1,200 | 32fb8d9 |
| round 3a | 20260930-152852-ollama_gemma4_e4b-it-qat-24798 | gemma4:e4b-it-qat | 1,056 | a116105 |
| round 3a | 20260930-154432-ollama_gemma4_31b-cloud-30452 | gemma4:31b-cloud | 1,056 | 5f83ab6 |
| round 3a | 20260930-174754-ollama_medgemma1.5_4b-62722 | medgemma1.5:4b | 1,056 | dd2ed4d |
| round 3a | 20260930-175734-ollama_kimi-k3_cloud-66601 | kimi-k3:cloud | 914 (partial) | dd2ed4d |
| round 3a | 20261002-065128-gemini-9124 | gemini-3.8-flash | 1,056 | 3b49f99 |
| round 3a | 20261002-065128-gpt-9125 | gpt-5.6-terra | 1,056 | 3b49f99 |
| OEP-002 | 20260929-12*/13*/15* (eight directories, one per model: gemma4 e4b, glm, MedGemma, gemma4 31B, kimi, minimax, mistral, gpt) | 7 Ollama + gpt | 600 each | dd5e7a2 … a7545f1 |
| pixel check | `docs/reports/orientation-pixel-check.json` (not a run: 100 packages × 3 conditions, offsets per package) | — | — | c201602 |

Notes for the ingest. The ablation's four conditions are `ctx_ctl`, `ctx_cue`, `ctx_instr`, `ctx_cue_instr`; identify these runs by `run_meta.conditions` containing all four, not by the latest-run rule, because the render-probe runs reused `ctx_ctl` on 40-image subsets. Tasks are `flip_check` (two items per image, `:flipped` suffix marks the mirrored one) and `left_edge`. Claude's directory holds two harness commits: the control and most of the cue arm from 26 September, the rest from the resume on 2 October, which ran from a detached worktree of c201602 because the working clone's template had moved to 0.2.1 in between; the dry-run text-token counts per arm were identical (392,915 and 521,576), so the prompts were the same. Round 3a's task types are `orient_conflict` (field `cell` in TN, TM, WN, WM), `badge_read` and `mark_side`; conditions `ctx3` and `ctx3_mask`; rows carry `rep` (only repeat 0 exists so far). Round 3a is incomplete: if minimax, mistral and glm have finished by the time you start, include them; otherwise report six models and name the three pending in the text and in a protocol note.

## I. `analysis_oip.py`: new result blocks

Add, with the same conventions as the existing blocks (Wilson 95 % CIs, exact McNemar on paired items, Holm within a family, n in every cell):

1. `ablation_round3`: per model × arm: flip-check accuracy, mirrored items caught of 100, normal items correct of 100, left-edge accuracy; per model the three contrasts arm vs `ctx_ctl` on paired items (discordant b/c, p, Holm over the three arms); the gate as stated in the decisions log (+20 pp for at least two of three frontier models without left-edge loss) evaluated as a boolean with the numbers behind it. Also the paper's own `ctx` flip-check cell per model for reference (from `rows.csv`), marked as a different day and run.
2. `pixel_check`: from the JSON report: single pass as shipped (98 consistent / 0 / 2 indeterminate), masks mirrored (0 / 98 / 2), mirrored and re-segmented (5 consistent / 71 inconsistent / 24 indeterminate), heart offsets (median +0.079 shipped, −0.053 mirrored), two-pass prior-free (94 / 0 / 6; s median +0.063, prior p median +0.008). Recompute the two-pass verdicts from the per-package offsets in the JSON rather than copying the summary.
3. `conflict_round3a`: per model × render: the four cells with CIs, the policy classification per image (compares / text only / pixels only / file vs convention / always mirrored / other) using the definitions in `docs/reports/round3a-2026-09-30.md` §1 (reimplement from the rows; reconcile with the report), and the canonical-vs-masked paired test (§2). Label reading and mark side without the region list per model (§3 and §4 of the report).
4. `oep002`: per model, CTR / cardiac width / left edge under `raw_ctl`, `ctx_l1_ctl`, `ctx_l1_oep2`, `ctx_l1_oep2e` with the paired tests against `ctx_l1_ctl`, the truncation counts, and the gpt repeat; the decision (D-031) as text in the template, not in results.
5. `template_versions`: paper measurements = template 0.2 (harness 050769a); OEP-002 arms = 0.2 + the two draft flags; shipped default since 2026-09-29 = 0.2.1; cue arms = 0.3 draft behind a flag. Scorer 0.3 for all round-3 rows.
6. `retired_tags`: qwen3-vl:235b-cloud (410, 2026-09-08, before the paper run) and qwen3.5:cloud (410, 2026-09-25, after it); the paper's qwen3.5 rows stand, round 3 has none.

## J. `template_oip.md`

Results, three new subsections after the existing last results section, numbered to follow it:

- **"Does the reference file make models check it against the image?"** The four-arm table for eleven models (flip check; mirrored caught; left edge), the gate outcome, and the left-edge cost for glm (99 → 48 → 87 → 40 %), MedGemma, mistral and gemma4 e4b. One paragraph: only gemma4 31B (+16) and minimax-m3 (+12) move, both only with cues and instruction together; the two frontier models that pass already did so with the shipped file; claude-sonnet-5 answers "agree" to every mirrored image in every arm.
- **"A pixel-side orientation check in the tools."** The design (unsided heart and aortic-arch centroid against the edge labelled L, two passes), the single-pass numbers and why they fall short (the segmentation model's positional prior), the two-pass numbers (94 of 100 decided, 0 wrong), and what the verdict looks like in the package and the reference file. This is the design-rule-R4 answer: the guarantee does not depend on the model.
- **"Conflict trials: which models compare file and image."** The four-cell table for the models available, the policy counts, the WN cell as the decisive one (both frontier models 100 %), the marker-mask result (gemini unmoved; gpt −5 pp, p = 0.05 uncorrected; kimi's partial pass rested on the marker), label reading solved for five of six, MedGemma's consistent inversion, mark side without the region list. State plainly that three open models are pending if they are.

Discussion. Replace the sentence that currently reads, in substance, "the result shows that the models use facts the pixels do not carry; it does not show that they checked those facts against the image, and on the tasks that required such a check they did not" with a version that (a) keeps the first half, (b) restricts the second half: gemini-3.8-flash and gpt-5.6-terra do compare the file with the image (WN cell 100 %), and the open models and claude-sonnet-5 follow a single source; (c) adds that three interventions in the file and the prompt do not change this and cost small models accuracy, so the protocol's answer is the tool-side check, now shipped; (d) notes that the paper's flip check could not separate "compares" from "calls mirrored whenever the file names the unconventional side" (gemma4 31B's policy), which the four-cell design can.

Methods. A paragraph "Post-hoc experiments (amendment 13)": the round-3 runs are new data collected after the paper's run, on the same 100 VinDr packages, one reply per cell, scorer 0.3, harness commits as in the manifest, templates as in `template_versions`; Ollama models through the Pro plan, frontier models at low effort as before; the cost rule (Ollama first) and the two exceptions (the cue ablation and the OEP-002 gpt repeat as like-for-like repeats).

Limitations. Add: cloud model tags are unpinned and two were retired during the study; the OEP-002 gpt repeat did not reproduce the paper's L0–L2 drop, consistent with snapshot drift; the round-3 interventions were measured on one dataset and one reply per cell; round 3a repeats are pending; the pixel check is defined for frontal chest radiographs only, with no equivalent yet for scintigraphy.

Data and code availability. Add the software DOI for release 0.2.0 next to the data DOI, and the sentence that the round-3 replies are included in the frozen-replies deposit's next version (or state the version if it exists).

## K. `PROTOCOL_oip.md`: amendment 13

Dated, post-hoc: lists the four experiments (ablation, pixel-check evaluation, round 3a, OEP-002), their run directories by name, their endpoints and tests as in part I, their gates as decided in the OIP decisions log before the runs, the selection rule for four-arm runs, the exclusions (render-probe runs; qwen3.5 absent), and the pinned-harness resume of Claude's arm with its justification. Note that the OIP-side decisions (OEP-002 adopt / OEP-003/004/005 not adopted) were taken against gates written before the respective runs, and name where.

## L. Citations

None new are required by the text above. If the discussion cites the positional-prior observation, it is this study's own report, not a reference.

## M. Then

Rebuild and verify that no cell of the paper's original tables changed (the reconciliation script against the previous `results.json`); run the audits; peer review; copy the new `PROTOCOL_oip.md` and `results.json` back to `/Users/pal/oip-work/docs/paper/`; record the branch and verdicts in `docs/state/oip-bench.md` and the CLAUDE.md "Current state" block of the RA repo.

Honesty points the claim audit should be told to check, in addition to the existing eleven: every round-3 percentage is quoted with its n and arm; "two models compare file and image" is tied to the WN cell numbers; the cue-arm left-edge losses are reported, not only the flip-check gains; the pixel check's single-pass failure is stated before its two-pass success; pending models are named as pending; the template version of every measurement is stated; no sentence claims an intervention "makes models check".
