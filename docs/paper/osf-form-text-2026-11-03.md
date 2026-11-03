# OSF form text: confirmatory round (OSF "Preregistration" template, 2025 form)

Copy-paste blocks for the registration of project https://osf.io/ntgrb/. Registered 2026-11-03 17:15 CET as https://osf.io/9rxbk (public, no embargo); the registration carries these answers verbatim.
The blocks follow the pages and field order of the form (Metadata, Overview, Research Design, Sampling, Variables,
Analysis Plan, Other). Every block is taken from `preregistration-confirmatory-2026-11-03-osf.md` (frozen at tag
`prereg-confirm-2026-11`); that file, `confirm_set.json`, `PROTOKOLL.md` and `items.json` are attached to the draft.
Where the form asks for something the document does not spell out (study type, foreknowledge, causal intention), the answer
states the fact and points to the section. German notes in brackets are for Henrik, not for the form.

---

## Page "Metadata"

### Title
Use and verification of supplied image metadata by vision-language models in chest radiography: a pre-registered confirmatory replication on fresh images

### Description
The Open Image Protocol (OIP) packages a medical image with a machine-readable reference file (manifest and context.md) that states what the pixels cannot show: patient side at each image edge, pixel spacing, tool-computed measurements with their assertion levels. OIP-Bench asks a vision-language model questions about an image under several conditions: image only (raw), image with the full reference file (ctx), and two conditions in which a wrong finding label is supplied, either as a plain note (misled_plain) or inside the OIP file with its provenance and assertion level (misled_oip).

All results reported so far by this study are exploratory and post hoc (paper runs 2026-09-08 to 2026-09-22, 11 models, 100 VinDr-CXR and 50 NIH images; orientation conflict trials 2026-09-30 to 2026-10-16, 10 models, 82 VinDr images; repeat subset 2026-10-24 to 2026-11-02, 20 images, three replies). Three exploratory findings carry the manuscript: (1) with the reference file, models read the four facts (patient side, scale availability, cardiothoracic ratio class, cardiac width) on 99–100 % of images; (2) only two of ten models check the file against the pixels when the two disagree; (3) a wrong label is adopted on most images, less often from the OIP file than from a plain note. This registration tests six directional statements derived from those findings on 80 fresh VinDr-CXR images that no model has seen in this study, with thresholds fixed from the exploratory data before the image draw. Only this round will be called "pre-registered" in the manuscript. The full registration text (preregistration-confirmatory-2026-11-03-osf.md), the image hash list (confirm_set.json), the reader-study protocol (PROTOKOLL.md) and its item list (items.json) are attached; the frozen analysis code is at GitHub tag prereg-confirm-2026-11 (commit abcad9f).

### Contributors
[Schon erledigt: Henrik Stelling und Ibrahim Güler, beide Administrator und bibliographic.]

### Affiliated Institutions
[Leer lassen, falls die OVGU nicht in der Liste ist.]

### License
[CC0 1.0 Universal ist vorausgewählt. Sie gilt nur für Text und Dateien der Registrierung (Hash-Listen, Protokoll, Registrierungstext), nicht für das Repository. Das ist in Ordnung. Wer eine Namensnennung will, wählt CC-BY 4.0; beides ist für eine Pre-Registration üblich.]

### Subjects
Medicine and Health Sciences → Radiology (wenn der Unterpunkt angeboten wird; sonst Medicine and Health Sciences allein).

### Tags
vision-language models; chest radiography; bone scintigraphy; image metadata; cardiothoracic ratio; orientation; benchmark; preregistration; Open Image Protocol; VinDr-CXR

---

## Page "Overview"

### Research questions or hypotheses
Each statement is evaluated per model with a one-sided exact test, Holm-corrected within the statement, alpha 0.05, and is confirmed when at least the registered number of models meets its criterion. Ten models: claude-sonnet-5, gpt-5.6-terra, gemini-3.8-flash, gemma4:31b, gemma4:e4b, glm-5.3-flash, kimi-k3, medgemma1.5:4b, minimax-m3, mistral-large-3. Models that cannot be run count as not meeting any criterion. "WN cell": the file's edge labels are swapped and the image is normal, so the file and the pixels disagree; chance is 50 % under every single-source policy.

H1a. Most models do not check the file against the image: in the WN cell the accuracy is below 50 %. Per model: one-sided exact binomial test of H0 p ≥ 0.5 against H1 p < 0.5, Holm over ten models. Confirmed if at least 5 of 10 models meet it. (Exploratory: 0, 0, 0, 2, 26 % for claude, mistral, gemma4:e4b, medgemma, minimax; kimi 48 % is excluded by design.)

H1b. gemini-3.8-flash and gpt-5.6-terra check the file against the image: WN accuracy at least 90 %. Per model: point estimate ≥ 90 % and one-sided test of H0 p ≤ 0.75 against H1 p > 0.75, Holm over the two named models. Confirmed if 2 of 2. (Exploratory: 100 % and 100 % on the canonical render; repeats 100/100/100 and 100/98/100.)

H2a. A wrong finding label inside the OIP file is adopted by at least half of the models on at least half of the images. Per model: adoption point estimate ≥ 50 % and one-sided test of H0 p ≤ 0.35 against H1 p > 0.35, Holm over ten. Confirmed if at least 5 of 10. (Exploratory: 69–100 % for seven models in the paper run.)

H2b. The OIP file is adopted less often than the plain note. Per model: paired exact McNemar within model, one-sided (plain-only discordant pairs more frequent than OIP-only), Holm over ten. Confirmed if at least 5 of 10. (Exploratory: 7 of 10 after Holm.)

H3a. With the reference file the facts are read: each of the four fact tasks (patient side at the left edge, scale availability, cardiothoracic ratio class, cardiac width in mm) is answered correctly on at least 95 % of images. Per model × task: point estimate ≥ 95 % and one-sided test of H0 p ≤ 0.80 against H1 p > 0.80, Holm over the 40 model × task tests; a model meets the criterion when all four tasks meet it. Confirmed if at least 8 of 10. (Exploratory: 99–100 % on every task for eight models.)

H3b. Image only, scale availability cannot be read: accuracy below 50 %. Per model: one-sided exact binomial test of H0 p ≥ 0.5 against H1 p < 0.5, Holm over ten. Confirmed if at least 8 of 10. (Exploratory: 16–36 % for nine models; medgemma 82 %.)

No omnibus test combines the six statements; each is reported as confirmed or not confirmed with every per-model estimate, its Wilson 95 % CI and both p values. A statement that is not confirmed is reported as such in the manuscript and the framing of the corresponding exploratory result is weakened accordingly.

### Foreknowledge of data or evidence
[Radio-Button:] **Data does not yet exist.**
[Begründung: die analysierten Daten sind die Modellantworten, und kein Modell wurde auf diesen 80 Bildern aufgerufen. Die Bilder selbst existieren; das erklärt das nächste Feld. Wer konservativer sein will, wählt stattdessen "Data exists but the authors have not observed it yet" mit derselben Erklärung; beides ist vertretbar, die Erklärung macht es eindeutig.]

### Explanation of foreknowledge and managing unintended influences
The data analysed in this registration are the models' replies, and no model has been called on the 80 images of this round. The images themselves exist (public VinDr-CXR training set, converted to OIP packages on 2026-09-06) but were never shown to a model, a reader or a reviewer in this study and were not inspected by anyone before the draw; the exclusion list (122 packages used anywhere before) is part of the attached confirm_set.json. The 80 images were drawn by a deterministic script (seed 20261105) from the 728 eligible packages after the thresholds and the sample size had been fixed. Exploratory results on other images (sections 2 and 3 of the attached document) exist and motivated the thresholds; every threshold is stated with the exploratory value it was derived from. The analysis code was frozen before the draw and runs without manual steps.

---

## Page "Research Design"

### Study Type
[Radio-Button:] **Other**
[Falls ein Textfeld aufgeht:] A benchmark of ten vision-language models on a fixed set of 80 de-identified public chest radiographs (VinDr-CXR). No human participants in this round; the models are queried through their APIs with and without a machine-readable reference file, under conditions the investigator assigns to every image and model (within-image, within-model factorial design).

### Intention For Causal Interpretation (optional)
[Radio-Button:] **No causal relationship inferred.**
[Die sechs Aussagen sind Genauigkeits- und Übernahmeraten unter festgelegten Bedingungen, keine Kausalschätzung zwischen Variablen. Feld kann auch leer bleiben.]

### Blinding Of Experimental Treatments
[Checkbox:] **No blinding is involved.**

### Additional Blinding During Research Or Analysis (optional)
The units are model API calls; nobody who could be blinded interacts with them. The 80 images are drawn by a deterministic script (seed 20261105) from the eligible pool and are not inspected by anyone before the run. The analysis code (bench/confirm/analyze.py) was frozen before the draw, was dry-run on the exploratory data only, and runs without manual steps. The companion reader study (attached PROTOKOLL.md) is blinded: readers see only the canonical render without annotations, package values or model replies, and the item key is not opened before the readings are complete.

### Study Design
Within-image, within-model factorial design. Every image is presented to every model under four conditions (image only; image with the full OIP reference file; wrong finding label in a plain note; wrong finding label inside the OIP file) and, with the full file, in the four orientation-conflict cells (file edge labels true or swapped × image normal or mirrored). Tasks: patient side at the left edge, scale availability, cardiothoracic ratio class, cardiac width in mm, orientation conflict, finding list. Up to 14 items per image and reply, about 1,088 items per model and reply. Three replies per item are collected; the first reply of every item is the primary datum. All factors are within image and within model (paired); model is the only between factor. No counterbalancing: the harness presents the items in a fixed order per model. Full description: sections 4.2–4.6 of the attached preregistration-confirmatory-2026-11-03-osf.md.

### Study Design - file upload
[Die vier Dateien sind schon angehängt; nichts weiter hochladen.]

### Randomization (optional)
Image selection: random.Random(20261105).sample over the sorted names of the eligible pool (728 of 1,000 packages); the first 80 are the set, the next 10 the reserve. The wrong finding label of the misleading conditions is drawn per image from the labels the image does not carry, seeded with the sha256 of the package name, identical across conditions and models. No other randomization; conditions are not assigned at random because every image receives every condition.

---

## Page "Sampling"

### Data Collection Procedures
Fresh images from the 1,000-package VinDr-CXR store (public training set, de-identified by the dataset authors). Eligible is every package that (a) was never shown to a model in any benchmark run, never in the reader study and never in the marker review, (b) carries inferred L/R edge labels, (c) has stored anatomy masks and passes the pixel-side orientation check with a clear cardiac cue (confidence ≥ 0.9, heart offset ≥ 5 % of thoracic width, the gate of the exploratory conflict trials), (d) has a canonical render and a source hash. 728 packages were eligible; 80 + 10 reserve were drawn with seed 20261105. confirm_set.json records for every package the VinDr image id, the sha256 of the source DICOM and of oip.json, the canonical render and the masks. The models are called through their providers' APIs (Anthropic, OpenAI, Google) and through Ollama (cloud and local) with the harness bench/run.py at the frozen commit, providers' default sampling, system prompt "You are assisting with medical image understanding for a benchmark. Answer the question only, briefly, with no disclaimers. This is not clinical use." Scoring by scorer 0.3 with the thresholds recorded in run_meta.json. Run window: after this registration, until 2026-11-21. VinDr-CXR pixels are not redistributed; the hashes identify the images.

### Sample Size
80 images (plus 10 reserve packages, used in order only for technical replacements before any model call). Ten models. Every image is presented to every model under every condition, so the sample size is the same across conditions: 80 images per model and condition. Up to 14 items per image and reply, about 1,088 items per model and reply; three replies per item, the first being primary. Cardiac width in mm is scored on the 65 of 80 images that carry a header pixel spacing (section 4.1 of the attached document).

### Sample Size Rationale (optional)
Exact binomial power at the worst-case Holm level per statement (section 5 of the attached document): H1a rejects at ≤ 28 of 80 correct, power 0.97 at a true 26 % (the marginal exploratory value); H1b rejects at ≥ 68 of 80, power 0.95 at 90 %; H2a rejects at ≥ 40 of 80 adopted, power 0.97 at 60 %; H3a rejects at ≥ 75 of 80 (≥ 61 of 64 where only calibrated images carry the task), power 0.99 at 98 %; H3b rejects at ≤ 28 of 80, power 0.97 at 26 %. With n = 60 the marginal powers fall to 0.86–0.88; with n = 100 they rise to 0.98–0.99. n = 80 is the smallest size at which every marginal case stays above 0.95 at a cost the project can carry.

### Starting And Stopping Rules
Start: there is no pilot phase in this round; data collection begins with the first model call after this registration is submitted, and before that call the frozen code is checked against the tag (git diff prereg-confirm-2026-11 must be empty for the harness, the scorer and the analysis script). Stopping: no interim analysis. The primary data set is complete when every model has a first reply for every item, or is recorded as not run (API retired or rejecting every call for more than seven consecutive days). Repeats 1 and 2 are collected until 2026-11-21 as capacity allows; incomplete repeats are reported as such and do not touch the primary analysis.

---

## Page "Variables"

### Manipulated Variables
Condition (within image and model): raw (image only); ctx (image with the full OIP reference file); misled_plain (image, a plain note with a wrong finding label); misled_oip (image, the OIP file carrying the wrong label with its provenance and assertion level). Orientation-conflict cell (within image and model, with the full file): TN (file labels true, image normal), TM (true, mirrored), WN (swapped, normal), WM (swapped, mirrored). Model (ten levels, between "subjects"). Conditions are assigned to every image, not randomized.

### Measured Variables
Per item and reply, from scorer 0.3: correct (binary) for the fact tasks and the conflict items; adopted_misleading (binary: the injected wrong label appears in the model's finding list) for the finding-list task; truncated (binary: reply cut off at the output cap before an answer; scored as wrong, or as not adopted and wrong). Every row also records model_id, provider, start time, the sha256 of the prompt bytes and of the reply. Image-level variable used for subsetting: presence of a header pixel spacing (cardiac width in mm is scored only on those images).

### Indices
Per model: WN-cell accuracy (H1a, H1b) = correct conflict items in the WN cell / 80; adoption rate from the OIP file (H2a) = items with adopted_misleading under misled_oip / 80; discordant-pair counts plain-only vs OIP-only (H2b) = images adopted under misled_plain but not misled_oip, and the reverse; accuracy per fact task under ctx (H3a) = correct / images carrying the task; scale-availability accuracy under raw (H3b) = correct / 80. All from the first reply of each item.

---

## Page "Analysis Plan"

### Statistical Models
Per-model one-sided exact binomial tests at the registered p0 (H1a 0.5, H1b 0.75, H2a 0.35, H3a 0.80, H3b 0.5), Holm within each statement over the tests it names (10, 2, 10, 10, 40, 10); paired exact one-sided McNemar within model for H2b; point-estimate conditions where stated; count of models meeting the criterion against the registered minimum. Wilson 95 % CIs on every estimate. No covariates, no pooling across models, no model-level weighting, no omnibus test. Implemented in bench/confirm/analyze.py at the frozen commit (GitHub tag prereg-confirm-2026-11); the script was dry-run on the exploratory data before registration and is not changed afterwards.

### Transformations
None. Binary verdicts are counted; cardiac width is scored as correct within 10 % relative tolerance and the cardiothoracic ratio class within 0.05 absolute, as recorded in run_meta.json.

### Inference Criteria
One-sided tests, alpha 0.05 after Holm within each statement. A statement is confirmed when at least the registered number of models meets its criterion (5, 2, 5, 5, 8, 8 of 10 for H1a, H1b, H2a, H2b, H3a, H3b). Every per-model estimate is reported with its Wilson 95 % CI and both the raw and the Holm-adjusted p value, whether or not the statement is confirmed.

### Data Inclusion And Exclusion
No image is excluded after the first model call; there is no outlier rule. Before any model call, a package that fails validation or lacks a render or a mask is replaced by the next reserve package; the replacement is logged in confirm_set.json and reported. Transport errors (no reply) are not data: they are refilled by re-sending the identical prompt before the analysis. Truncated replies are kept and scored as wrong (or as not adopted and wrong). A model whose API is retired or rejects every call for more than seven consecutive days before its first replies are complete is reported as not run and counts as not meeting any criterion; no substitute model is added.

### Missing Data
The analysis asserts that no primary item is missing or in error and otherwise reports the count as a deviation. Items missing on an image that cannot be refilled are reported; the image is kept and the missing item counts as wrong.

### Other Planned Analysis (optional)
Descriptive, without hypothesis tests, in the supplement: four-cell accuracy and per-image policy (compares / text only / pixels only / file versus convention / always mirrored / other, by the majority of three replies), accuracy per repeat and the share of conflict items with identical verdicts across the three replies, adoption from the plain note, image-only cardiothoracic ratio and cardiac-width accuracy, and the comparison of every estimate with its exploratory value.

---

## Page "Other"

### Context And Additional Information (optional)
Full registration text attached (preregistration-confirmatory-2026-11-03-osf.md, version 1.0); image hash list attached (confirm_set.json). Code and text frozen at https://github.com/HenrikStelling/open-image-protocol/tree/prereg-confirm-2026-11 (image list and analysis code at commit abcad9f). Model drift cannot be prevented (no provider pins these models); run dates and exploratory run dates are reported side by side. The run directories (every reply with its hashes) are shipped in the next version of the study's Zenodo bundle (software concept DOI 10.5281/zenodo.23052074; data bundle 10.5281/zenodo.23040047). Any departure from this registration is listed in a "Deviations" section of the report and in the manuscript's Methods.

The attached PROTOKOLL.md and items.json document the companion human reference reading (two radiologists and one nuclear medicine physician read 433 items from the exploratory image sets on a local sheet; adjudication by a third radiologist; agreement by ICC(2,1), Cohen's kappa, Lin's CCC and Bland–Altman; model replies re-scored against the human reference). The reader study uses the exploratory images, not the 80 images of this round, and is registered here for transparency of its protocol; its hypotheses are not part of the six confirmatory statements.

---

## Page "Review"
[Alles noch einmal durchlesen, dann "Register". Danach: public oder Embargo wählen, Zustimmung des zweiten Administrators innerhalb von 48 h, dann DOI und Zeitstempel an mich für §7 (F4).]
