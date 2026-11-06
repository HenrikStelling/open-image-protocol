# Confirmatory round — run report (draft, 2026-11-06)

Companion to the frozen analysis output `confirmatory-2026-11-06.md` (written by `bench/confirm/analyze.py --label confirm:`
on 2026-11-06 14:13 CET, exit status 0: no primary item missing, no error row at rep 0). Registration: https://osf.io/9rxbk
(project https://osf.io/ntgrb), frozen commit `abcad9f`, tag `prereg-confirm-2026-11`; registered text in
`docs/paper/preregistration-confirmatory-2026-11-03-osf.md`. This report covers what the registration asks to be reported
next to the verdicts: run dates, deviations (6.7), error-row refills (6.2), incomplete repeats (6.6), the comparison with the
exploratory values (6.5) and the spend (8). **Draft**: the kimi-k3 repeats are still being collected (section 5) and the real
spend has not yet been read from the three consoles; the primary analysis is complete and will not change.

## 1. Verdicts (rep 0, ten models, 80 fresh VinDr-CXR images)

| statement | criterion (per model) | met | registered minimum | result |
|---|---|---|---|---|
| H1a | WN cell accuracy < 50 % | 4 of 10 | 5 | **not confirmed** |
| H1b | gemini and gpt: WN cell ≥ 90 % (test against 75 %) | 2 of 2 | 2 | **confirmed** |
| H2a | wrong label in the OIP file adopted on ≥ 50 % of images (test against 35 %) | 3 of 10 | 5 | **not confirmed** |
| H2b | OIP file adopted less often than the plain note (exact McNemar) | 10 of 10 | 5 | **confirmed** |
| H3a | with the file, each of the four fact tasks ≥ 95 % (test against 80 %) | 7 of 10 | 8 | **not confirmed** |
| H3b | image only, scale availability < 50 % | 9 of 10 | 8 | **confirmed** |

Per-model estimates, Wilson CIs and both p values: `confirmatory-2026-11-06.md`.

## 2. What the data say per statement (against the exploratory values of the registration, section 3)

**H1a, not confirmed by one model.** Four models answer the WN cell (file edge labels swapped, image normal) from the file on
every image: claude 0 %, gemma4:e4b 0 %, mistral 0 %, medgemma 1 % (exploratory 0, 0, 0, 2 %). The fifth model the threshold
was built on, minimax-m3, moved from 26 % in the exploratory run to 59 % [48–69] here and no longer meets the criterion.
The others as expected: kimi-k3 51 % (48 % exploratory, noise), gemma4:31b 74 % (96 %), glm 76 % (82 %), gemini and gpt 100 %.

**H1b, confirmed.** gemini-3.8-flash and gpt-5.6-terra 80 of 80 each on the decisive WN cell (exploratory 100 % and 100 %).

**H2a, not confirmed.** Adoption of the wrong finding label from the OIP file reached the 50 % point criterion with a
significant test for three models (mistral 76 %, glm 68 %, kimi-k3 51 %). Four models sit just below the point criterion
(gemini 46 %, claude 45 %, gemma4:31b 44 %, gemma4:e4b 41 %); gpt 28 %, minimax 31 %, medgemma 0 %. Against the paper run,
adoption from the OIP file fell for every one of the seven models it was 69–100 % for (claude 83 → 45, gemini 78 → 46,
gemma4:31b 69 → 44, gemma4:e4b 75 → 41, glm 71 → 68, kimi 69 → 51, mistral 100 → 76), and against the repeat subset of
2026-10-24 (same cross-checked file form, 20 paper images) as well (claude 65–70 → 45, gemini 75–85 → 46, glm 80–90 → 68,
gemma4:31b 55–65 → 44, mistral 100 → 76). Adoption from the plain note stayed where it was: 74–100 % for every model
(gpt 74, gemini 79, gemma4:31b 78, gemma4:e4b 84, kimi 88, minimax 89, medgemma 96, glm 98, claude 100, mistral 100).

**H2b, confirmed by every model.** Within model, the OIP file is adopted less often than the plain note for 10 of 10
(exploratory 7 of 10); the discordant pairs are almost all plain-only (b = 19–77, c = 0–5).

**H3a, not confirmed by one model.** Seven models read all four facts from the file at ≥ 95 % (gpt, gemini, gemma4:31b,
gemma4:e4b, kimi-k3, minimax, mistral, every task 98–100 %). Three do not:
- claude, `left_edge` 94 % (75/80): on five images claude answers "patient left" with the file although the file states R at the
  left edge and claude answers "patient right" on the same five images image-only; the other three tasks 100 %. The behaviour
  is per image, not noise: repeats 1 and 2 miss 7 and 5 items, nine of them on the same five images.
- glm-5.3-flash, `ctr` 84 % (67/80) and `heart_mm` 88 % (57/65): the misses are long visible-reasoning replies that quote
  the file's values correctly and end without a clean final number; the frozen scorer's number parser then picks another number
  from the text (e.g. 1.24 parsed where the reply states CTR 0.4967, 0.48 parsed where it states 97.5 mm). The registered
  criterion counts these as wrong (4.6, scorer 0.3 frozen); the exploratory run showed the same cells at 79 % for the same reason.
  Not rescored.
- medgemma1.5, `left_edge` 69 % (55/80) with the file (the other three tasks 99–100 %).

**H3b, confirmed.** Image only, scale availability is answered on 15–21 % of images by nine models (exploratory 16–36 %);
medgemma 81 % (exploratory 82 %, answers "yes" by default).

## 3. Run dates and events (CET)

| when | event |
|---|---|
| 2026-11-03 17:15 | registration on OSF (F4); no model call before it |
| 2026-11-04 15:14 | F6 start: claude, gpt, gemini with `--repeats 3` in three processes; gemma4:31b-cloud and gemma4:e4b-it-qat rep 0; harness at commit 855ad12 (frozen paths identical to the tag, launcher check) |
| 2026-11-04 16:19 | medgemma1.5 rep 0 (after gemma4:e4b); 16:32 glm rep 0 (after gemma4:31b); 20:14 minimax rep 0; 20:58 mistral rep 0; 21:43 kimi-k3 rep 0 |
| 2026-11-04 16:19, 17:44 | gpt stopped twice on exhausted OpenAI credits (HTTP 429 "no credits"); topped up and resumed; rep 0 complete at the second stop |
| 2026-11-04 ~16:30 | one transport error row each for claude, gpt and gemini (connection error / timeout), refilled with `--resume` |
| 2026-11-04 17:46, 19:12, 20:50, 20:54 | three replies complete: claude, gemma4:e4b, gemini, medgemma |
| 2026-11-04 21:50, 22:24 | kimi-k3 stopped twice on the Ollama Pro session usage limit (251 and 775 rows); limit lifted 03:04 |
| 2026-11-05 03:13 | kimi-k3 rep 0 complete: **primary data complete for all ten models** |
| 2026-11-05 03:14 | repeats 1–2 for the cloud lanes, one model at a time: gemma4:31b complete 04:22; glm from 04:22 |
| 2026-11-05 06:57 | glm stopped on the session limit (2,198 rows); resumed 08:17 |
| 2026-11-05 ~08:50 | the session running the harness ended; the glm and gpt processes were killed mid-reply (glm 2,200 rows, gpt 2,579 rows); relaunched 09:17 with `--resume` from a persistent launcher; the glm log of 08:17–08:42 was lost with the session scratch directory |
| 2026-11-05 09:55, 12:2x | gpt stopped twice more on credits with 12 and 3 rows left; complete 12:29 |
| 2026-11-05 12:56, 14:50, 16:58 | three replies complete: glm, minimax, mistral |
| 2026-11-05 17:02, 18:10 | kimi-k3 repeats stopped twice on the session limit (1,285 and 1,551 rows) |
| 2026-11-06 14:01 | the Ollama probe answers "weekly usage limit"; kimi-k3 repeats paused until the weekly reset (section 5) |
| 2026-11-06 14:13 | `analyze.py` run (this report) |

Started timestamps per run directory are in the first table of `confirmatory-2026-11-06.md`; exploratory run dates:
round 3a 2026-09-26 to 10-16, repeat subset 2026-10-24 (6.4, drift caveat).

## 4. Error rows refilled (6.2)

Every refill re-sent the identical prompt (`prompt_sha256` unchanged) with `bench/run.py --resume`, which drops the error row
and writes the new reply. Counts from the launcher logs: claude 1 and gemini 1 (transport, 11-04); gpt 1 transport plus
21, 5, 12 and 3 rows of HTTP 429 "no credits" (11-04 17:44, 11-05 08:50, 09:55, 12:2x); glm 1 and 3 (session limit, 11-05);
kimi-k3 1, 1 and 2 (session limit). No image was replaced (6.3); no error row remains at rep 0 for any model.

## 5. Repeats (6.6)

Nine models have three replies per item (3,270 rows, no error rows). kimi-k3 has rep 0 complete and rep 1 for 459 of 1,090
items (1,551 rows, 2 error rows to be refilled) at the time of the analysis; the Ollama Pro weekly usage limit stops the lane
since 2026-11-05 18:10. The collection continues automatically when the limit lifts, until 2026-11-21 as registered; the
secondary table of `confirmatory-2026-11-06.md` marks kimi-k3 with two replies and will be regenerated. The primary analysis
does not use repeats and is final.

## 6. Deviations (6.7)

1. **Ollama lanes collected rep 0 first, repeats by `--resume`.** The registered command carries `--repeats 3`; the seven
   Ollama lanes were started with `--repeats 1` and the repeats added with `--resume --repeats 3` into the same run directory
   (same `tasks.json`, same prompts, every row carries `rep`). Reason: one cloud model at a time and the Ollama Pro caps; the
   primary data had to be complete before any repeat. Effect on the analysis: none (rep 0 is the first reply of every item in
   either order). `run_meta.json` of these directories records the first invocation (`repeats 1`).
2. **`harness_commit` carries `-dirty`.** At launch (855ad12) and at the resumes (394350e) the working tree held uncommitted
   documentation (the registration cover note, the reader-study protocol 0.2). The launcher refused to start unless
   `git diff prereg-confirm-2026-11 --stat` was empty for `bench/confirm/`, `bench/run.py`, `bench/tasks.py`, `bench/score.py`,
   `bench/cloudlock.py` and `src/oip/`; it was empty at every start and still is. The flag is cosmetic.
3. **Process interruption on 2026-11-05 ~08:50** (the session running the harness ended): glm and gpt rows in flight became error
   rows and were refilled; the glm launcher log of 08:17–08:42 was lost. No reply was altered; the run directories were untouched.
4. **kimi-k3 repeats incomplete at the time of the analysis** (section 5), as foreseen in 6.6. The analysis was run on
   2026-11-06, before the repeat collection closes on 2026-11-21, because the primary data were complete; it will be re-run
   when kimi-k3 completes or on 2026-11-21, which changes the secondary table only.
5. **Scoring observation, not a deviation:** glm-5.3-flash's `ctr` and `heart_mm` misses with the file are parser picks from
   verbose replies (section 2). The scorer is frozen (4.6); the numbers stand as scored and the observation goes to the
   supplement.
6. Outside the confirmatory round: the reader-study protocol attached to the registration is at 0.1; 0.2 of 2026-11-04 states the
   blinding as procedural (recorded in the registration cover note and the RA handover).

## 7. Spend (8)

List price from the recorded token usage (`usage` per row; prices of 2026-11-04, `docs/paper/cost-estimate-2026-11-04.md`),
three replies per model unless stated:

| lane | input / cache write / cache read / output tokens | list price |
|---|---|---|
| claude-sonnet-5 | 0.21 M / 6.32 M / 9.52 M / 0.022 M | $18.35 |
| gemini-3.8-flash | 8.39 M / – / – / 0.010 M | $6.33 |
| gpt-5.6-terra | 12.91 M / – / (cache reads not recorded) / 0.261 M | $28.95 |
| **API lanes, three replies** | | **$53.63** (registered ceiling about $80; token-priced estimate $46.46; rep 0 about one third, against the $27 ceiling) |
| gemma4:31b-cloud | 5.77 M / 0.013 M | $0.81 |
| glm-5.3-flash:cloud | 13.64 M / 3.84 M | $3.97 |
| minimax-m3:cloud | 14.03 M / 0.011 M | $8.45 |
| mistral-large-3:675b-cloud | 13.66 M / 0.017 M | $6.86 |
| kimi-k3:cloud (1,549 rows) | 6.24 M / 0.024 M | $19.08 |
| **Ollama cloud, Pro credits** | | **$39.17 so far**; kimi-k3's remaining ~1,720 rows about $21 more at list price, which would reach the $60 monthly credit of the subscription |

The local lanes (gemma4:e4b-it-qat, medgemma1.5:4b) cost nothing beyond electricity. The real spend is read from the
Anthropic, OpenAI and Google consoles and from the Ollama account after the run and reported next to these figures.

## 8. Reproduction

```
python bench/confirm/analyze.py --label confirm:
```

reads every run directory under `bench/results/` whose `run_meta.label` starts with `confirm:` (latest per model) and rewrites
`docs/reports/confirmatory-<date>.md`. The run directories (`results.jsonl`, `tasks.json`, `run_meta.json`) are frozen after F7
and go into the next version of the Zenodo data bundle (9).
