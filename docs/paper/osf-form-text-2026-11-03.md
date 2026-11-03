# OSF form text: confirmatory round (template "OSF Preregistration")

Copy-paste blocks for the registration form of project https://osf.io/ntgrb/. Every block is taken from
`preregistration-confirmatory-2026-11-03-osf.md` (frozen at tag `prereg-confirm-2026-11`); the full text is attached as PDF.
Where the form asks for something the document does not spell out (study type, randomization), the answer states the fact and
points to the section. German notes in brackets are for Henrik, not for the form.

---

## Study Information

### Title
Use and verification of supplied image metadata by vision-language models in chest radiography: a pre-registered confirmatory replication on fresh images

### Authors
As on the manuscript. Corresponding author: Dr Ibrahim Güler (Otto von Guericke University Magdeburg). Design, code and runs: Henrik Stelling (developer of the Open Image Protocol; non-financial interest declared in the manuscript).

### Description
The Open Image Protocol (OIP) packages a medical image with a machine-readable reference file (manifest and context.md) that states what the pixels cannot show: patient side at each image edge, pixel spacing, tool-computed measurements with their assertion levels. OIP-Bench asks a vision-language model questions about an image under several conditions: image only (raw), image with the full reference file (ctx), and two conditions in which a wrong finding label is supplied, either as a plain note (misled_plain) or inside the OIP file with its provenance and assertion level (misled_oip).

All results reported so far by this study are exploratory and post hoc (paper runs 2026-09-08 to 2026-09-22, 11 models, 100 VinDr-CXR and 50 NIH images; orientation conflict trials 2026-09-30 to 2026-10-16, 10 models, 82 VinDr images; repeat subset 2026-10-24 to 2026-11-02, 20 images, three replies). Three exploratory findings carry the manuscript: (1) with the reference file, models read the four facts (patient side, scale availability, cardiothoracic ratio class, cardiac width) on 99–100 % of images; (2) only two of ten models check the file against the pixels when the two disagree; (3) a wrong label is adopted on most images, less often from the OIP file than from a plain note. This registration tests six directional statements derived from those findings on 80 fresh VinDr-CXR images that no model has seen in this study, with thresholds fixed from the exploratory data before the image draw. Only this round will be called "pre-registered" in the manuscript. The full registration text, the image hash list (confirm_set.json) and the frozen analysis code (GitHub tag prereg-confirm-2026-11, commit abcad9f) are attached.

### Hypotheses
Each statement is evaluated per model with a one-sided exact test, Holm-corrected within the statement, alpha 0.05, and is confirmed when at least the registered number of models meets its criterion. Ten models: claude-sonnet-5, gpt-5.6-terra, gemini-3.8-flash, gemma4:31b, gemma4:e4b, glm-5.3-flash, kimi-k3, medgemma1.5:4b, minimax-m3, mistral-large-3. Models that cannot be run count as not meeting any criterion. "WN cell": the file's edge labels are swapped and the image is normal, so the file and the pixels disagree; chance is 50 % under every single-source policy.

H1a. Most models do not check the file against the image: in the WN cell the accuracy is below 50 %. Per model: one-sided exact binomial test of H0 p ≥ 0.5 against H1 p < 0.5, Holm over ten models. Confirmed if at least 5 of 10 models meet it. (Exploratory: 0, 0, 0, 2, 26 % for claude, mistral, gemma4:e4b, medgemma, minimax; kimi 48 % is excluded by design.)

H1b. gemini-3.8-flash and gpt-5.6-terra check the file against the image: WN accuracy at least 90 %. Per model: point estimate ≥ 90 % and one-sided test of H0 p ≤ 0.75 against H1 p > 0.75, Holm over the two named models. Confirmed if 2 of 2. (Exploratory: 100 % and 100 % on the canonical render; repeats 100/100/100 and 100/98/100.)

H2a. A wrong finding label inside the OIP file is adopted by at least half of the models on at least half of the images. Per model: adoption point estimate ≥ 50 % and one-sided test of H0 p ≤ 0.35 against H1 p > 0.35, Holm over ten. Confirmed if at least 5 of 10. (Exploratory: 69–100 % for seven models in the paper run.)

H2b. The OIP file is adopted less often than the plain note. Per model: paired exact McNemar within model, one-sided (plain-only discordant pairs more frequent than OIP-only), Holm over ten. Confirmed if at least 5 of 10. (Exploratory: 7 of 10 after Holm.)

H3a. With the reference file the facts are read: each of the four fact tasks (patient side at the left edge, scale availability, cardiothoracic ratio class, cardiac width in mm) is answered correctly on at least 95 % of images. Per model × task: point estimate ≥ 95 % and one-sided test of H0 p ≤ 0.80 against H1 p > 0.80, Holm over the 40 model × task tests; a model meets the criterion when all four tasks meet it. Confirmed if at least 8 of 10. (Exploratory: 99–100 % on every task for eight models.)

H3b. Image only, scale availability cannot be read: accuracy below 50 %. Per model: one-sided exact binomial test of H0 p ≥ 0.5 against H1 p < 0.5, Holm over ten. Confirmed if at least 8 of 10. (Exploratory: 16–36 % for nine models; medgemma 82 %.)

No omnibus test combines the six statements; each is reported as confirmed or not confirmed with every per-model estimate, its Wilson 95 % CI and both p values. A statement that is not confirmed is reported as such in the manuscript and the framing of the corresponding exploratory result is weakened accordingly.

---

## Design Plan

### Study type
Other. A benchmark of ten vision-language models on a fixed set of 80 de-identified public chest radiographs (VinDr-CXR). No human participants in this round; the models are queried through their APIs with and without a machine-readable reference file, under conditions the investigator assigns.

### Blinding
No blinding is involved in this study.
[Begründung, falls gefragt: the units are model API calls; nobody who could be blinded interacts with them. The images are not inspected by anyone before the run, see section 4.1 of the attached document.]

### Is there any additional blinding in this study?
The 80 images are drawn by a deterministic script (seed 20261105) from the eligible pool and are not inspected by anyone before the run. The analysis code was frozen before the draw and runs without manual steps.

### Study design
Within-image, within-model factorial design. Every image is presented to every model under four conditions (image only; image with the full OIP reference file; wrong finding label in a plain note; wrong finding label inside the OIP file) and, with the full file, in the four orientation-conflict cells (file edge labels true or swapped × image normal or mirrored). Tasks: patient side at the left edge, scale availability, cardiothoracic ratio class, cardiac width in mm, orientation conflict, finding list. Up to 14 items per image and reply, about 1,088 items per model and reply. Three replies per item are collected; the first reply of every item is the primary datum. Details: sections 4.2–4.6 of the attached document.

### Randomization
Image selection: random.Random(20261105).sample over the sorted names of the eligible pool (728 of 1,000 packages); the first 80 are the set, the next 10 the reserve. The wrong finding label of the misleading conditions is drawn per image from the labels the image does not carry, seeded with the sha256 of the package name, identical across conditions and models. No other randomization; the harness presents the items in a fixed order per model.

---

## Sampling Plan

### Existing data
Registration prior to creation of data.

### Explanation of existing data
No model has been called on the 80 images of this round. The images themselves exist (public VinDr-CXR training set, converted to OIP packages on 2026-09-06) but were never shown to a model, a reader or a reviewer in this study; the exclusion list (122 packages used anywhere before) is part of the attached confirm_set.json. The exploratory results on other images (sections 2 and 3 of the attached document) exist and motivated the thresholds.

### Data collection procedures
Fresh images from the 1,000-package VinDr-CXR store. Eligible is every package that (a) was never shown to a model in any benchmark run, never in the reader study and never in the marker review, (b) carries inferred L/R edge labels, (c) has stored anatomy masks and passes the pixel-side orientation check with a clear cardiac cue (confidence ≥ 0.9, heart offset ≥ 5 % of thoracic width, the gate of the exploratory conflict trials), (d) has a canonical render and a source hash. 728 packages were eligible; 80 + 10 reserve were drawn with seed 20261105. confirm_set.json records for every package the VinDr image id, the sha256 of the source DICOM and of oip.json, the canonical render and the masks. The models are called through their providers' APIs (Anthropic, OpenAI, Google) and through Ollama (cloud and local) with the harness bench/run.py at the frozen commit, providers' default sampling, system prompt "You are assisting with medical image understanding for a benchmark. Answer the question only, briefly, with no disclaimers. This is not clinical use." Scoring by scorer 0.3 with the thresholds recorded in run_meta.json. Run window: after this registration, until 2026-11-21.

### Sample size
80 images (plus 10 reserve packages, used in order only for technical replacements before any model call). Ten models. Up to 14 items per image and reply, about 1,088 items per model and reply; three replies per item, the first being primary.

### Sample size rationale
Exact binomial power at the worst-case Holm level per statement (section 5 of the attached document): H1a rejects at ≤ 28 of 80 correct, power 0.97 at a true 26 % (the marginal exploratory value); H1b rejects at ≥ 68 of 80, power 0.95 at 90 %; H2a rejects at ≥ 40 of 80 adopted, power 0.97 at 60 %; H3a rejects at ≥ 75 of 80 (≥ 61 of 64 where only calibrated images carry the task), power 0.99 at 98 %; H3b rejects at ≤ 28 of 80, power 0.97 at 26 %. With n = 60 the marginal powers fall to 0.86–0.88; with n = 100 they rise to 0.98–0.99. n = 80 is the smallest size at which every marginal case stays above 0.95 at a cost the project can carry.

### Stopping rule
No interim analysis. The primary data set is complete when every model has a first reply for every item, or is recorded as not run (API retired or rejecting every call for more than seven consecutive days). Repeats 1 and 2 are collected until 2026-11-21 as capacity allows; incomplete repeats are reported as such and do not touch the primary analysis.

---

## Variables

### Manipulated variables
Condition (within image and model): raw (image only); ctx (image with the full OIP reference file); misled_plain (image, a plain note with a wrong finding label); misled_oip (image, the OIP file carrying the wrong label with its provenance and assertion level). Orientation-conflict cell (within image and model, with the full file): TN (file labels true, image normal), TM (true, mirrored), WN (swapped, normal), WM (swapped, mirrored). Model (ten levels, between "subjects").

### Measured variables
Per item and reply, from scorer 0.3: correct (binary) for the fact tasks and the conflict items; adopted_misleading (binary: the injected wrong label appears in the model's finding list) for the finding-list task; truncated (binary: reply cut off at the output cap before an answer; scored as wrong, or as not adopted and wrong). Every row also records model_id, provider, start time, the sha256 of the prompt bytes and of the reply.

### Indices
Per model: WN-cell accuracy (H1a, H1b); adoption rate from the OIP file (H2a); discordant-pair counts plain-only vs OIP-only (H2b); accuracy per fact task under ctx (H3a); scale-availability accuracy under raw (H3b). All from the first reply of each item.

---

## Analysis Plan

### Statistical models
Per-model one-sided exact binomial tests at the registered p0 (H1a 0.5, H1b 0.75, H2a 0.35, H3a 0.80, H3b 0.5), Holm within each statement over the tests it names (10, 2, 10, 10, 40, 10); paired exact one-sided McNemar within model for H2b; point-estimate conditions where stated; count of models meeting the criterion against the registered minimum. Wilson 95 % CIs on every estimate. No covariates, no pooling across models, no model-level weighting. Implemented in bench/confirm/analyze.py at the frozen commit; the script was dry-run on the exploratory data before registration and is not changed afterwards.

### Transformations
None. Binary verdicts are counted; cardiac width is scored as correct within 10 % relative tolerance and the cardiothoracic ratio class within 0.05 absolute, as recorded in run_meta.json.

### Inference criteria
One-sided tests, alpha 0.05 after Holm within each statement. A statement is confirmed when at least the registered number of models meets its criterion (5, 2, 5, 5, 8, 8 of 10 for H1a, H1b, H2a, H2b, H3a, H3b).

### Data exclusion
No image is excluded after the first model call. Before any model call, a package that fails validation or lacks a render or a mask is replaced by the next reserve package; the replacement is logged in confirm_set.json and reported. Transport errors (no reply) are not data: they are refilled by re-sending the identical prompt before the analysis. A model whose API is retired or rejects every call for more than seven consecutive days before its first replies are complete is reported as not run and counts as not meeting any criterion; no substitute model is added.

### Missing data
The analysis asserts that no primary item is missing or in error and otherwise reports the count as a deviation. Items missing on an image that cannot be refilled are reported; the image is kept.

### Exploratory analysis (optional)
Descriptive, without hypothesis tests, in the supplement: four-cell accuracy and per-image policy (compares / text only / pixels only / file versus convention / always mirrored / other, by the majority of three replies), accuracy per repeat and the share of conflict items with identical verdicts across the three replies, adoption from the plain note, image-only cardiothoracic ratio and cardiac-width accuracy, and the comparison of every estimate with its exploratory value.

---

## Other

### Other
Full registration text attached as PDF (preregistration-confirmatory-2026-11-03-osf.pdf); image hash list attached (confirm_set.json). Code and text frozen at https://github.com/HenrikStelling/open-image-protocol/tree/prereg-confirm-2026-11 (image list and analysis code at commit abcad9f). Model drift cannot be prevented (no provider pins these models); run dates and exploratory run dates are reported side by side. The run directories (every reply with its hashes) are shipped in the next version of the study's Zenodo bundle (software concept DOI 10.5281/zenodo.23052074; data bundle 10.5281/zenodo.23040047). VinDr-CXR pixels are not redistributed; the hashes identify the images. Any departure from this registration is listed in a "Deviations" section of the report and in the manuscript's Methods.
