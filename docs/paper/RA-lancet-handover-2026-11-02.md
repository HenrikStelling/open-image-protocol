# RA handover 2026-11-02: the Lancet package and who does what

For the Research_Automation session. Henrik received a submission package from the corresponding author (folder
`OIP_Lancet_Uebergabe/`: `00_LIES_MICH_ZUERST.md`, `01_AUFTRAG_FUER_CLAUDE.md`, `02_Mail_an_Leser.md`,
`03_Journal_Originaldokumente/`). Target: "Article" at The Lancet Medical Imaging & Theranostics, submission by 2026-12-15.
The package is written for one assistant; the work is split between the RA session (manuscript, figures, forms, package) and
the OIP session (data, tools, runs). This note says which side owns which section of `01_AUFTRAG_FUER_CLAUDE.md`, what the
OIP side delivers and in which form, and where the package needs a correction. Read the package first, then this.

## 1. Split by section of the package

| Package section | Owner | Notes |
|---|---|---|
| 0 Roles, dates | both | dates in §4 below |
| 1 Primary sources, compliance matrix | RA | `09_Compliance_Matrix.xlsx` from the journal documents |
| 2 AI use: rules, `ai_use_log.md`, prompt archive, AI declaration | RA, with Henrik | the OIP session logs its own runs in `bench/README.md` and run_meta; the sample of 50 raw replies for Ibrahim (2.3) comes from OIP |
| 3.1–3.2 Framing, title | RA | |
| 3.3 A human reference reading | **OIP builds, readers read, OIP analyses** | tool and protocol are in the repo now (§2) |
| 3.3 B pre-registered confirmatory round | **OIP** selects images, freezes code, runs; Henrik registers on OSF | needs Henrik's release for the API costs (§3) |
| 3.4–3.6 rewrite, cuts, Lancet style | RA | |
| 4 reading protocol | OIP (done, `bench/reader/PROTOKOLL.md`) | RA turns it into the appendix section and the OSF document |
| 5 pre-registration | OIP drafts hypotheses and image list; Henrik approves and uploads | |
| 6 references | RA | the OIP docs cite nothing the RA side does not already have |
| 7 reporting checklists | RA, facts from OIP on request | |
| 8 figures | RA (`make_figures.py` from `results.json`) | image examples: NIH or Paraguay renders only, taken from the packages (OIP can export unannotated renders with licence strings) |
| 8.3 tagged release, Zenodo version | OIP, on Henrik's word | |
| 9 supplement | RA; OIP supplies tables: package structure L0–L5, scorer details, model ids and run dates, repeat subset (S17) | |
| 10–13 forms, cover letter, EM list, package | RA | |
| 14 gates | RA; G4 (numbers) against `results.json`; G9 is a fresh session | |
| 15 pitfalls | both | "validated/validation" wording: only for the human reference, and cautiously |

## 2. What the OIP side delivers (paths in the public repo)

- `bench/reader/PROTOKOLL.md`: reading protocol with the measurement definitions (German, reader-facing; the
  pre-registration text for the reader study), including the adjudication rule and the analysis plan (ICC(2,1), Cohen's
  kappa, Lin's CCC, Bland–Altman, re-scoring with the thresholds of `bench/tasks.py`).
- `bench/reader/README.md`: the tool, the set composition, the CSV schema.
- `bench/reader/items.json`: the item list with the sha256 of every shown image (the hash list for the pre-registration).
- After the reading: `docs/reports/reader-readings-<date>.csv` (merged, latest revision per reader and item, `heart_mm`
  added) and `docs/reports/reader-study-<date>.md` (agreement tables, Bland–Altman numbers, the re-scored model
  accuracies against both truths), plus an RA addendum with the sentences to change.
- Confirmatory round: `docs/paper/preregistration-draft-2026-11-02.md` (draft 0.1: six directional statements with the X and Y
  taken from the exploratory data, image selection rule and seed, models, frozen code; thresholds and n = 80 approved by Henrik on 2026-11-02; the sha256
  list `bench/confirm/confirm_set.json` is drawn and verified (80 + 10 reserve of 728 eligible); analysis `bench/confirm/analyze.py`;
  frozen at tag `prereg-confirm-2026-11`; registered on OSF 2026-11-03, https://osf.io/9rxbk, public, DOI after approval;
  OSF copy of the text `preregistration-confirmatory-2026-11-03-osf.md`), then the run directories and
  `docs/reports/confirmatory-<date>.md`.
- Already there: `docs/reports/repeat-subset-2026-10-24.md` and `docs/paper/RA-addendum-2026-10-25-repeats.md` (all ten
  models, S17), `bench/README.md` sections on model identity and the misleading-label draw.

## 3. Corrections and clarifications to the package

1. **Two different sets of 82 images.** The package equates "82 VinDr with header pixel spacing" (cardiac width in mm)
   with "82 conflict-trial images" (marker check). They overlap in 68 images only. Block B measures all 100 VinDr images;
   mm are computed for the 82 with a header spacing. Block C shows the 82 conflict-trial images.
2. **The marker check is done on the masked render**, the image the models saw in the conflict trials, not on the full
   radiograph. That is what the assistant's visual pass checked and what the human read replaces.
3. **The sheet records pixels, not mm.** Readers never see the pixel spacing; `collect.py` converts afterwards. This keeps
   the blinding and matches how the package values were produced (detector plane, no magnification correction).
4. **The bone-scan view is not shown.** The reader names anterior/posterior first, then the side. The models were told the
   view; the human read therefore also tests whether the view is recognisable from the image.
5. **Costs.** The confirmatory round re-runs claude, gpt and gemini on fresh images. Under the project's cost rule this
   needs Henrik's explicit release once the pre-registration fixes the size — released 2026-11-04, run started the same day; token-priced estimate in `docs/paper/cost-estimate-2026-11-04.md`; the OIP side will give the token-based estimate
   and the measured bills of the repeat subset (claude about US$0.60 list price for 696 replies with prompt caching; gpt
   2.38M input tokens, gemini 1.45M input tokens, bills pending).
6. **Legacy wording in `docs/paper/`.** `RA-revision-addendum-2026-10-18.md`, `round3a-for-paper.md` and
   `coauthor-review-2026-10-23-actions.md` describe the marker review as an assistant's visual pass. After the human read
   those sentences are superseded; do not carry them into the Lancet text.
7. **VinDr renders stay on Henrik's machine.** The reading runs locally (`serve.py` binds to 127.0.0.1). No VinDr pixels in
   figures, supplement, OSF or Zenodo; `items.json` carries hashes, not images.
8. **One assistant, two sessions.** The AI declaration and `ai_use_log.md` should name both uses: the RA pipeline for the
   manuscript and the OIP session for harness, tools and runs (model versions from `bench/README.md` and the run_meta files).

## 4. Dates (from the package) and the OIP side's part

| By | Package | OIP side |
|---|---|---|
| 2026-11-07 | readers confirmed | — |
| 2026-11-09 | protocol and pre-registration public on OSF | done 2026-11-03: registration https://osf.io/9rxbk (public) with the text, `confirm_set.json`, `PROTOKOLL.md` and `items.json` attached; `PROTOKOLL.md` 1.0 still to be confirmed by Henrik |
| 2026-11-23 | readings and replication run done | reading sessions on Henrik's machine; confirmatory run after Henrik's release; merged CSV, agreement report, re-scoring, addendum to RA |
| 2026-12-06 | manuscript, figures, supplement, forms | tables for the supplement on request; tagged release and Zenodo version when Henrik says so |
| 2026-12-12 | all gates passed, package to Ibrahim | — |
| 2026-12-15 | submission | — |

## 5. Pointers

- `bench/reader/` — tool, protocol, schema (this delivery).
- `bench/README.md` — harness, conditions, model identity, repeat subset.
- `docs/paper/coauthor-review-2026-10-23-actions.md` — the earlier action list; B8 (expert-read subset) is now this reader
  study, B3 (verification block) stays after submission.
