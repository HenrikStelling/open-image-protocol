# Pre-registration: confirmatory replication of the OIP-Bench findings on fresh VinDr-CXR images

Version 1.0, 2026-11-03. Text, image hash list and analysis code frozen at git tag `prereg-confirm-2026-11` (https://github.com/HenrikStelling/open-image-protocol/tree/prereg-confirm-2026-11); image list and code at commit `abcad9f`. Thresholds and sample size approved by the owner on 2026-11-02 before the image draw; no model of this round has been called. Attachments: `confirm_set.json` (sha256 list of the 80 + 10 images). Source of this text in the repository: `docs/paper/preregistration-draft-2026-11-02.md` (identical in content; this copy omits the owner's German working note at the top and sets table column widths for the PDF).

## 1. Study information

**Title.** Use and verification of supplied image metadata by vision-language models in chest radiography: a pre-registered
confirmatory replication on fresh images (part of the study "Use and verification of supplied image metadata by vision-language
models in chest radiography and bone scintigraphy: a cross-sectional benchmarking study").

**Authors.** As on the manuscript; corresponding author Dr Ibrahim Güler (Otto von Guericke University Magdeburg); design,
code and runs Henrik Stelling (developer of the Open Image Protocol, a non-financial interest declared in the manuscript).

**Registration.** OSF Preregistration (generic template), registered before any model call of this round. Public, or
embargoed with a visible registration timestamp, as the authors decide. This document is attached verbatim, together with the
image hash list (`bench/confirm/confirm_set.json`) and the frozen commit hash of the analysis code.

**Relation to prior work.** All results reported so far by this study are exploratory and post hoc: the paper runs
(replies 2026-09-08 to 2026-09-22, 11 models, 100 VinDr-CXR and 50 NIH images), the orientation conflict trials of round 3a
(2026-09-30 to 2026-10-16, 10 models, 82 VinDr images, three replies per cell) and the repeat subset (2026-10-24 to 2026-11-02,
10 models, 20 VinDr images, three replies). The thresholds below were chosen from those data and are tested here on images none
of the models has seen in this study. Only this round will be called "pre-registered" or "prespecified" in the manuscript.

## 2. Background and the exploratory findings to be confirmed

The Open Image Protocol (OIP) packages a medical image with a machine-readable reference file (manifest and `context.md`) that
states what the pixels cannot show: patient side at each image edge, pixel spacing, tool-computed measurements with their
assertion levels. OIP-Bench asks a vision-language model questions about an image under several conditions: image only
(`raw`), image with the full reference file (`ctx`), and two conditions in which a wrong finding label is supplied, either as a
plain note (`misled_plain`) or inside the OIP file with its provenance and assertion level (`misled_oip`). Three exploratory
findings carry the manuscript:

1. **Facts from the file.** With the reference file, eight of ten models answer the four fact tasks (patient side at the left
   edge, availability of a physical scale, cardiothoracic ratio class, cardiac width in mm) on 99–100 % of images; image only,
   scale availability is answered on 16–36 % (medgemma1.5 82 %), cardiac width on 9–61 %.
2. **Only two of ten models check the file against the pixels.** In the four-cell conflict design (file edge labels true or
   swapped × image normal or mirrored, 82 images), gemini-3.8-flash and gpt-5.6-terra answered "mirrored" on 100 % of the
   decisive WN items (file wrong, image normal), an answer no reader of a single source can give; claude-sonnet-5,
   mistral-large-3, gemma4:e4b and medgemma1.5 answered from the file on 98–100 % of those items (WN accuracy 0–2 %),
   minimax-m3 26 %, kimi-k3 48 % (noise), glm-5.3-flash 82 %, gemma4:31b 96 % (a "file versus convention" policy that never
   looks at the image).
3. **A wrong label is adopted, less so from the OIP file.** The wrong label of the plain note was adopted on 74–100 % of
   images by every model; from the OIP file on 69–100 % by seven models (claude 83, gemini 78, gemma4:31b 69, gemma4:e4b 75,
   glm 71, kimi 69, mistral 100 %) and on 1–48 % by three (medgemma 1, minimax 42, gpt 48 %). Within model, adoption from the
   OIP file was lower than from the plain note for seven of ten models (exact McNemar, Holm-corrected).

The repeat subset showed the fact cells to be identical across three replies for eight of ten models, while wrong-label adoption
of the mid-sized models and the image-only size cells move by 3–4 items in 20 between runs. The thresholds below leave room for
that spread and for provider-side model drift (gemini's four-cell accuracy moved 94 → 90 → 88 % across identical repeats).

## 3. Hypotheses (directional, with the registered criteria)

Each statement is evaluated per model with a one-sided exact test, Holm-corrected within the statement, alpha 0.05, and is
**confirmed** when at least the registered number of models meets its criterion. Models that cannot be run (retired tag, see
6.4) count as not meeting any criterion. Chance for the WN cell is 50 % under every single-source policy.

| | statement | per-model criterion | registered minimum | exploratory values that motivate the threshold |
|--|------|------|---|------|
| **H1a** | Most models do not check the file against the image: in the WN cell (file edge labels swapped, image normal) the accuracy is below 50 % | one-sided exact binomial test of H0 p ≥ 0·5 against H1 p < 0·5, Holm over the ten models | **5 of 10** | 0, 0, 0, 2, 26 % for claude, mistral, gemma4:e4b, medgemma, minimax; kimi 48 % is excluded by design (noise), glm 82 and gemma4:31b 96 % answer "mirrored" for another reason |
| **H1b** | gemini-3.8-flash and gpt-5.6-terra check the file against the image: WN accuracy at least 90 % | point estimate ≥ 90 % and one-sided test of H0 p ≤ 0·75 against H1 p > 0·75, Holm over the two named models | **2 of 2** | 100 % and 100 % (canonical render), 99 % and 94 % (marker-masked), repeats 100 / 100 / 100 and 100 / 98 / 100 |
| **H2a** | A wrong finding label inside the OIP file is adopted by at least half of the models on at least half of the images | adoption point estimate ≥ 50 % and one-sided test of H0 p ≤ 0·35 against H1 p > 0·35, Holm over ten | **5 of 10** | 69–100 % for seven models in the paper run; in the repeat subset claude 65–70, gemini 75–85, glm 80–90, mistral 100, gemma4:31b 55–65 %, the others 0–75 % |
| **H2b** | The OIP file is adopted less often than the plain note | paired exact McNemar within model, one-sided (plain-only discordant pairs more frequent than OIP-only), Holm over ten | **5 of 10** | 7 of 10 after Holm in the paper run (claude, gemma4:e4b, glm, gpt, medgemma, minimax, gemma4:31b); gemini and mistral show no difference, kimi p = 0·07 |
| **H3a** | With the reference file the facts are read: each of the four fact tasks is answered correctly on at least 95 % of images | per model × task, point estimate ≥ 95 % and one-sided test of H0 p ≤ 0·80 against H1 p > 0·80, Holm over the 40 model × task tests; a model meets the criterion when all four tasks meet it | **8 of 10** | 99–100 % on every task for eight models; glm 79–100 %, medgemma 60–100 % |
| **H3b** | Image only, scale availability cannot be read: accuracy below 50 % | one-sided exact binomial test of H0 p ≥ 0·5 against H1 p < 0·5, Holm over ten | **8 of 10** | 16–36 % for nine models; medgemma 82 % (answers "yes" by default) |

No omnibus test combines the six statements; each is reported as confirmed or not confirmed, with every per-model estimate,
its Wilson 95 % CI and both p values. A statement that is not confirmed is reported as such in the manuscript and the framing
of the corresponding exploratory result is weakened accordingly.

## 4. Design

### 4.1 Images
Fresh images from the 1,000-package VinDr-CXR store (the seed-0 stratified sample of the Kaggle training set of
VinBigData Chest X-ray Abnormalities Detection, converted to OIP on 2026-09-06 and cross-checked against CheXmask on 2026-10-17).
Eligible is every package that

- was never shown to a model in any run of this study (every `bench/results/*/tasks.json`), never in the reader study
  (`bench/reader/set_key.json`) and never in the marker review of round 3a — the excluded names are written into
  `confirm_set.json` (`excluded_used`), 122 packages as of 2026-11-02 (100 paper packages, 19 pilot and smoke packages, 3 practice packages of the reader study);
- carries inferred L/R edge labels (`geometry.orientation.edge_labels`);
- has the stored anatomy masks and passes the pixel-side orientation check with a clear cardiac cue (`bench/tasks.py`
  `clear_cue`: `oip check` consistent, confidence ≥ 0·9, heart offset ≥ 5 % of thoracic width — the same gate as round 3a, so
  "could not tell" is not confounded with "did not look");
- has a canonical render and a source hash.

From the eligible packages, `bench/confirm/draw_set.py` draws **90 with `random.Random(20261105).sample` over the sorted
names**: the first **80 are the set**, the remaining 10 the reserve, used in order and only for the technical replacements of
6.3. The set is copied to `~/oip-bench/vindr-confirm/`, and `bench/confirm/confirm_set.json` records for every package the
VinDr image id, the sha256 of the source DICOM (`identity.source_hash`), and the sha256 of `oip.json`, `renders/canonical.png`
and the three masks that decide eligibility. That file is part of the registration. `draw_set.py --verify` recomputes the hashes
before the first model call. Pixel spacing is not an eligibility criterion: the cardiac-width task is built only for packages
with a header spacing (expected about 80 % of the set), as in the paper.

The images are not inspected by anyone before the run. No marker-masked render is used (its review requires looking at the
images); the conflict items use the canonical render, the paper's and round 3a's primary render.

### 4.2 Conditions and tasks
`bench/run.py` with conditions `raw, ctx, misled_plain, misled_oip` and tasks `left_edge, scale_available, ctr, heart_mm,
orient_conflict, findings_misled` (`bench/tasks.py`, `TASKS_VERSION` 3.0). Per image and reply: four fact tasks image only,
four with the full reference file, the four conflict cells TN, TM, WN, WM with the full file (the file's edge labels true or
swapped, the image normal or mirrored; "agree" is right in TN and WM), and the finding-list task with the wrong label in a plain
note and in the OIP file (the wrong label is drawn per image from the labels the image does not carry, seeded with the sha256 of
the package name, identical across arms and models). Up to 14 items per image and reply, 1,088 per model and reply on 80 images
with about 80 % calibrated.

### 4.3 Reference file and renders
The reference file is rendered at run time by the frozen code from the package manifest: template 0.2.1 with the CheXmask
cross-check table (`validation_status: cross_checked`), the form every package has carried since 2026-10-17. The `prompt_sha256`
of every row records the exact bytes sent (system prompt, user text, image). Conflict items with swapped labels remove the stale
pixel-check verdict from the manifest, as in round 3a.

### 4.4 Models
The ten models of round 3a and the repeat subset, by the identifiers the harness records (`model_id`, `provider`, `started`):

| lane | model id | access |
|---|---|---|
| claude | claude-sonnet-5 | Anthropic API (max_tokens 4,000, effort low, prompt caching of the shared prefix) |
| gpt | gpt-5.6-terra | OpenAI API |
| gemini | gemini-3.8-flash | Google API |
| ollama cloud | gemma4:31b-cloud, glm-5.3-flash:cloud, kimi-k3:cloud, minimax-m3:cloud, mistral-large-3:675b-cloud | Ollama Pro, one cloud model at a time (`bench/cloudlock.py`) |
| ollama local | gemma4:e4b-it-qat, medgemma1.5:4b | Ollama on the owner's Mac (version recorded in `run_meta.ollama_version`) |

Sampling parameters are the providers' defaults (no temperature or seed is set); Ollama models run with `think=false`
(`--ollama-think auto`: output cap 800 tokens, 8,000 for glm-5.3-flash, whose visible reasoning otherwise exceeds the cap). The
system prompt is the harness's: "You are assisting with medical image understanding for a benchmark. Answer the question only,
briefly, with no disclaimers. This is not clinical use." None of the models is pinned by its provider; drift is handled in 6.4.

### 4.5 Replies
Three replies per item (`--repeats 3`), collected repeat by repeat. **The first reply (rep 0) of every item is the primary
datum** for every statement in section 3; repeats 1 and 2 enter only the secondary analyses of 6.5 and may remain incomplete
(6.6) without affecting the primary analysis.

### 4.6 Scoring
Scorer 0.3 (`bench/score.py`), thresholds as recorded in every `run_meta.json`: CTR class tolerance 0·05 absolute, cardiac
width 10 % relative, clear-cue confidence 0·9 and offset 0·05. A reply cut off at the output cap before an answer
(`score.truncated`) is scored as wrong (conflict) or as not adopted and wrong (finding list), as in round 3a. Adoption means the
injected wrong label appears in the model's finding list (`score.adopted_misleading`).

### 4.7 Frozen code
The run and the analysis use one commit of https://github.com/HenrikStelling/open-image-protocol, named here at registration
(step F3) and recorded in every row (`harness_commit`) and in `run_meta.json`. **Frozen commit: `abcad9f`**
(the commit that contains `bench/confirm/confirm_set.json` and the scripts; tag `prereg-confirm-2026-11` marks the follow-up
commit that writes this hash into the text). Before the first model call, `git diff prereg-confirm-2026-11 -- bench/ src/`
must be empty for `bench/confirm/`, `bench/run.py`, `bench/tasks.py`, `bench/score.py`, `bench/cloudlock.py` and `src/oip/`;
documentation commits after the tag do not touch them. The analysis is `bench/confirm/analyze.py` at
that commit; it reads the run directories and prints the tables of section 3 with the confirmed / not confirmed verdicts. It was
dry-run on the exploratory data before registration (round 3a: H1a 5 of 10, H1b 2 of 2; repeat subset: H2a 5 of 10 on 20 images)
and is not changed afterwards. Exact commands:

```
python bench/confirm/draw_set.py --store "/Volumes/Video Storage/oip/oip-packages/vindr"
python bench/confirm/draw_set.py --verify
python bench/run.py --dataset vindr --pkg-dir ~/oip-bench/vindr-confirm --n 80 --seed 0 --conditions raw,ctx,misled_plain,misled_oip --tasks left_edge,scale_available,ctr,heart_mm,orient_conflict,findings_misled --repeats 3 --ollama-think auto --label "confirm:2026-11" --models <lane>
python bench/confirm/analyze.py --label confirm:
```

## 5. Sample size

n = 80 images. Table 5.1 gives, for each statement, the per-model rejection boundary at the worst-case Holm level and the power
at plausible true values (exact binomial; `bench/confirm/` power script in the session notes, reproducible from the formulae
in `analyze.py`). The minimum counts in section 3 are reached when the models that showed the effect in the exploratory data show
it again; at n = 80 every clear exploratory effect has power ≥ 0·95, the marginal ones (minimax 26 % in H1a, gpt 90 % in H1b
under drift, a model at 60 % adoption in H2a) 0·95–0·97.

| statement | test (worst-case Holm alpha) | reject when | power at true value |
|--|-----|-------|-------|
| H1a | p < 0·5 (0·005) | ≤ 28 of 80 correct | 1·00 at 2 %, 0·97 at 26 %, 0·55 at 35 % |
| H1b | p > 0·75 (0·025) | ≥ 68 of 80 correct | 1·00 at 97 %, 0·95 at 90 %, 0·58 at 85 % |
| H2a | p > 0·35 (0·005) | ≥ 40 of 80 adopted | 1·00 at 70 %, 0·97 at 60 %, 0·54 at 50 % |
| H2b | McNemar, one-sided (0·005) | depends on the discordant pairs: with 10 all must be plain-only, with 20 at least 17, with 30 at least 23 | — |
| H3a | p > 0·80 (0·00125) | ≥ 75 of 80 correct (≥ 61 of 64 when only the calibrated images carry the task) | 1·00 at 100 %, 0·99 at 98 %, 0·79 at 95 % (n = 64: 0·96 at 98 %) |
| H3b | p < 0·5 (0·005) | ≤ 28 of 80 correct | 1·00 at 20 %, 0·97 at 26 %, 0·55 at 35 % |

With n = 60 the powers at the marginal values fall to 0·87 (H1a at 26 %), 0·86 (H1b at 90 %) and 0·88 (H2a at 60 %); with
n = 100 they rise to 0·99, 0·98 and 0·99. n = 80 is the smallest size at which every marginal case stays above 0·95 at a cost
the project can carry (section 8).

## 6. Analysis plan

6.1 **Primary.** `bench/confirm/analyze.py`, rep 0 only, as specified in sections 3 and 4.6: per-model one-sided exact binomial
tests at the registered p0, Holm within each statement over the tests it names (10, 2, 10, 10, 40, 10), point-estimate
conditions where stated, count of models meeting the criterion against the registered minimum. Wilson 95 % CIs on every
estimate. No covariates, no pooling across models, no model-level weighting.

6.2 **Error rows.** Transport errors (`error` set, no reply) are not data: before the analysis they are refilled with
`bench/run.py --resume`, which re-sends the identical prompt (same `prompt_sha256`). The analysis asserts that no primary item
is missing or in error and otherwise reports the count as a deviation.

6.3 **Image replacements.** A package of the set that fails `oip validate` or lacks a render or a mask when staged is replaced,
before any model call, by the next reserve package; the replacement is logged in `confirm_set.json` and reported. No image is
replaced after the first model call for any reason; an image on which a model returns errors that cannot be refilled is kept and
its missing items reported.

6.4 **Model availability and drift.** A model whose tag is retired (HTTP 410) or whose API rejects every call for more than
seven consecutive days before its rep-0 replies are complete is reported as not run; it counts as not meeting any criterion. No
substitute model is added. Drift cannot be prevented (no provider pins these models); the run dates (`started`) and the
exploratory run dates are reported side by side, and a confirmed or non-confirmed statement is read with that caveat.

6.5 **Secondary, descriptive, not confirmatory.** Four-cell accuracy and per-image policy (compares / text only / pixels only /
file versus convention / always mirrored / other, by the majority of three replies, definitions as in
`docs/reports/round3a-2026-09-30.md`), accuracy per repeat and the share of conflict items with identical verdicts across the
three replies, adoption from the plain note, image-only CTR and cardiac-width accuracy, and the comparison of every estimate
with its exploratory value. These are reported in the supplement without hypothesis tests.

6.6 **Stopping.** No interim analysis. The primary data set is complete when every model has a rep-0 reply for every item
(or is recorded under 6.4). Repeats 1 and 2 are collected until 2026-11-21 as capacity allows (Ollama Pro imposes daily and weekly
caps); incomplete repeats are reported as such and do not touch the primary analysis.

6.7 **Deviations.** Any departure from this document is listed in a "Deviations" section of the report and in the manuscript's
Methods, with the reason and its effect.

## 7. Procedure and timeline

| step | what | who | by |
|--|------------|----|----|
| F1 | approve or amend the statements, thresholds and n in sections 3 and 5 — **approved as written on 2026-11-02** (statements H1a–H3b, thresholds and minimum counts of section 3, n = 80 + 10 reserve) | Henrik | done 2026-11-02 |
| F2 | mount the external SSD, run `draw_set.py` and `draw_set.py --verify`; `confirm_set.json` is written — **done 2026-11-02**: store 1,000, 122 excluded as used, 150 without a clear cardiac cue, 728 eligible; 80 + 10 drawn with seed 20261105, 65 of 80 with a header pixel spacing; verify OK; the draw was recomputed once after the reader-study practice block was added to the exclusion list and reproduced the same 90 packages | Henrik (OIP session runs it) | done 2026-11-02 |
| F3 | commit the final text, `confirm_set.json` and the scripts; write the commit hash into 4.7; tag `prereg-confirm-2026-11` — **done 2026-11-02**, frozen commit `abcad9f` | OIP session | done 2026-11-02 |
| F4 | upload this document and `confirm_set.json` to OSF; record the registration DOI and timestamp here and in the manuscript | Henrik | 2026-11-09 |
| F5 | release the API cost (section 8) | Henrik | before F6 |
| F6 | run rep 0 for all ten lanes, then repeats 1 and 2 until 2026-11-21; refill error rows with `--resume` | OIP session | 2026-11-21 |
| F7 | `analyze.py` → `docs/reports/confirmatory-<date>.md`; addendum to the RA session with the per-statement verdicts | OIP session | 2026-11-23 |

No model call of this round happens before F4. The registration is not edited after F4; corrections are deviations (6.7).

## 8. Cost estimate (needs the owner's release)

Per model about 1,088 calls per reply, 3,264 for three. At the rates measured on the bills of round 3a and the repeat subset:
gpt-5.6-terra about US$22 per 1,000 calls with the full file → about $24 for rep 0, $72 for all three; gemini-3.8-flash
about $1·8 per 1,000 → $2 / $6; claude-sonnet-5 with prompt caching about $1 per 1,000 → $1 / $3·5. **About $27 for the
primary data, about $80 for all three replies**, plus the Ollama Pro subscription already in place (22,800 cloud and local calls,
one cloud model at a time). The real spend is read from the three consoles after the run and reported in the supplement next to
the estimate.

## 9. Data and code sharing

The run directories (`results.jsonl` with every reply and its hashes, `tasks.json`, `run_meta.json`) are frozen after F7 and
shipped in the next version of the study's Zenodo bundle (concept DOI 10.5281/zenodo.23052074 for the software; the data bundle
10.5281/zenodo.23040047 gets a new version), together with `confirm_set.json`, this document and the OSF registration link.
VinDr-CXR pixels are not redistributed; the hashes identify the images, the Kaggle competition supplies them.

## 10. Deviations

None at registration.
