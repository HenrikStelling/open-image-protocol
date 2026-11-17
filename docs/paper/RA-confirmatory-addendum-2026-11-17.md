# Addendum for the RA session: confirmatory round, per-statement verdicts (final, 2026-11-17)

Step F7 of the registration (https://osf.io/9rxbk; `docs/paper/preregistration-confirmatory-2026-11-03-osf.md`). Sources:
the frozen analysis output `docs/reports/confirmatory-2026-11-17.md` and the run report
`docs/reports/confirmatory-2026-11-17-run.md`. **Final** for the data and the analysis: the kimi-k3 repeats closed on
2026-11-16 01:08, all ten models have three replies, and the analysis was re-run on 2026-11-17. Against the interim output
of 2026-11-06 (which RA reproduced line by line) three lines changed: the title date, kimi-k3's `harness_commit` list and
kimi-k3's row of the secondary table. Every verdict and every primary number is unchanged. Still open: the real spend from
the consoles and the Zenodo version DOI (section 5).

## 1. Verdicts

| statement (registration section 3) | met | minimum | verdict |
|---|---|---|---|
| H1a — most models do not check the file against the image (WN cell < 50 %) | 4 of 10 | 5 | not confirmed |
| H1b — gemini-3.8-flash and gpt-5.6-terra check the file against the image (WN ≥ 90 %) | 2 of 2 | 2 | confirmed |
| H2a — a wrong label inside the OIP file is adopted by half the models on half the images | 3 of 10 | 5 | not confirmed |
| H2b — the OIP file is adopted less often than the plain note | 10 of 10 | 5 | confirmed |
| H3a — with the file, every fact task is read at ≥ 95 % | 7 of 10 | 8 | not confirmed |
| H3b — image only, scale availability cannot be read (< 50 %) | 9 of 10 | 8 | confirmed |

Design as registered: 80 fresh VinDr-CXR images never shown to a model before (drawn 2026-11-02, seed 20261105, hashes in
`bench/confirm/confirm_set.json`), ten models, first reply per item as the primary datum, one-sided exact tests per model with
Holm within each statement, alpha 0.05. No primary item missing, no error row at rep 0, no image replaced.

## 2. Reading for Results and Discussion

- **The two confirmed mechanisms carry the paper's claim.** gemini and gpt answer "mirrored" on 80 of 80 decisive items each
  (H1b), and every one of the ten models adopts a wrong label less often from the OIP file than from a plain note (H2b, 10 of 10;
  the exploratory data had 7 of 10). Image-only, scale availability stays unreadable for nine models (H3b).
- **H1a missed its minimum by one model.** Four models still answer from the file on every WN item (claude, mistral,
  gemma4:e4b, medgemma, 0–1 %); minimax-m3 moved from 26 % to 59 % and no longer counts. The exploratory wording "only two of
  ten models check the file against the pixels" should become: two models check (H1b confirmed); four answer from the file alone;
  the remaining four are in between (51–76 %) and are not single-source readers either. State H1a as not confirmed.
- **H2a missed because adoption from the OIP file fell across the board.** Against the paper run it fell for all seven models
  it had been 69–100 % for (e.g. claude 83 → 45 %, gemini 78 → 46 %, mistral 100 → 76 %), while plain-note adoption stayed at
  74–100 %. Three models meet the criterion (mistral 76, glm 68, kimi-k3 51 %); four sit at 41–46 %. The registered point
  criterion (≥ 50 %) is what fails, not the direction. Weaken the exploratory framing "adopted from the OIP file on 69–100 % by
  seven models" to the confirmatory range (28–76 %; 0 % for medgemma) and keep H2b as the result that replicated in full.
  Candidate reasons to name, not to adjudicate: fresh images with their own drawn wrong labels; provider-side drift between
  September/October and November (6.4); the cross-checked file form. The repeat subset of 2026-10-24 already used the
  cross-checked form and still showed 65–100 % for five models, so the form alone does not explain it.
- **H3a missed by one model, for three different reasons** (run report section 2): claude misreads the left-edge label from
  the file on five fixed images (94 %), glm's verbose replies defeat the frozen number parser on CTR and cardiac width (84 and
  88 %; a scoring artefact the registration anticipated and the scorer is frozen, so it stands), medgemma reads the left edge
  from the file on 69 %. Seven models read every fact at 98–100 %. For Methods: the registered criterion is per model on all four
  tasks; for Discussion: the fact-reading claim holds for seven of ten models on all four tasks. Per task: scale availability
  is read at ≥ 95 % by all ten models, CTR class and cardiac width by nine (glm misses both), the left-edge side by eight
  (claude and medgemma miss). [Corrected 2026-11-09 after RA's check; the earlier text said "three of four tasks for all ten",
  which the data do not support.]
- **Drift caveat (6.4).** Exploratory runs 2026-09-26 to 10-24, confirmatory 2026-11-04 to 11-06; no provider pins these models.

## 2a. Secondary table, now with three replies for every model

kimi-k3: four cells 56 / 52 / 53 %, WN cell 51 / 54 / 48 %, OIP-file adoption 51 / 55 / 58 %, conflict items identical in
all three replies 49 % [44–55] (157/320). The interim row read "2 replies, 73 % (57/78)"; that figure covered only the 78
items rep 1 had reached and should not be quoted. With glm (50 %) kimi-k3 is the least repeatable model; claude, mistral
and gemma4:e4b are at 100 %, the other five at 81–97 %. The other nine rows are unchanged. For RA: re-copy the ten run
directories and rebuild; only this row and the run facts move.

## 3. Deviations to list in Methods (registration 6.7; details in the run report, section 6)

1. Ollama lanes: rep 0 collected first (`--repeats 1`), repeats 1–2 added by `--resume` into the same run directory; no effect on
   the primary analysis.
2. `harness_commit` recorded with `-dirty` because of uncommitted documentation in the working tree; the frozen code paths were
   identical to the tag at every start (launcher check), still identical on 2026-11-06.
3. One process interruption (2026-11-05 ~08:50) and repeated provider stops (OpenAI credits four times; Ollama Pro session
   and weekly usage limits between 2026-11-04 and 11-16; three transport errors); every affected row refilled with the
   identical prompt (`--resume`). No error row remains in any run directory.
4. The analysis was first run on 2026-11-06 on the complete primary data with kimi-k3 at two replies (allowed by 6.6); the
   verdicts went to the manuscript from that interim run. The final run of 2026-11-17 changed kimi-k3's secondary row only.
5. kimi-k3's repeats closed on 2026-11-16, inside the registered window (until 2026-11-21); its rows carry four
   `harness_commit` ids because documentation was committed between resumes (frozen paths identical under each).

## 4. Spend (registration 8)

List price from recorded tokens: API lanes $53.63 for three replies (claude $18.35, gemini $6.33, gpt $28.95; registered
ceiling about $80, token-priced estimate $46.46). Ollama cloud lanes $62.49 at list price for three replies (kimi-k3 $42.40,
minimax $8.45, mistral $6.86, glm $3.97, gemma4:31b $0.81), against the $60 monthly credit the estimate assumed; billed as
the flat Pro subscription, no usage credits bought. Total at list price $116.12. Real spend from the consoles follows;
report both in the supplement.

## 5. Open on the OIP side

- Real spend from the Anthropic, OpenAI, Google consoles and the Ollama account.
- Freeze the ten run directories and ship them in the next Zenodo data-bundle version with `confirm_set.json` and the
  registration link (registration 9); add the Zenodo version DOI here.
- OSF: DOI of the registration once approved; "Deviations" are not entered on OSF (the registration is not edited), they live
  in the report and in Methods.

## 6. Pointers

- `docs/reports/confirmatory-2026-11-17.md` — tables per statement and model (frozen analysis output, final).
- `docs/reports/confirmatory-2026-11-06.md` — the interim output (kimi-k3 with two replies), kept for the record.
- `docs/reports/confirmatory-2026-11-17-run.md` — timeline, refills, deviations, spend, reproduction.
- `docs/paper/cost-estimate-2026-11-04.md` — prices and the pre-run estimate.
- `bench/confirm/` — `draw_set.py`, `confirm_set.json`, `analyze.py` (frozen at `abcad9f`).
