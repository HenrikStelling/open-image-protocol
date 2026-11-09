# OSF form text: reader study protocol 1.0 (OSF "Preregistration" template, 2025 form)

Draft 2026-11-09 for a second registration in project https://osf.io/ntgrb/. It supersedes the German reader protocol 0.1
(`PROTOKOLL.md`) attached to registration https://osf.io/9rxbk (2026-11-03). Every block is taken from
`bench/reader/PROTOCOL.md` version 1.0; attach that file and `bench/reader/items.json` to the draft. Items in square brackets
are filled in at the freeze (tag `reader-protocol-1.0`) or are German notes for Henrik, not for the form. Register before the
first reading; the waiver letter is added later to the protocol's section 7 and to Methods, not to this registration.

Order on the day: kimi-k3 complete (optional, Henrik's decision) → PROTOCOL.md section 7 (date and form of the committee's
answer) and section 10 filled in → commit, tag `reader-protocol-1.0`, push → this registration submitted → first reading.

---

## Page "Metadata"

### Title
Human reference reading for OIP-Bench: inter-reader agreement, agreement with segmentation-derived values, and re-scoring of vision-language model replies (reader protocol 1.0)

### Description
OIP-Bench scored vision-language model replies about chest radiographs and bone scintigrams against values taken from the image packages: patient side from the DICOM header or the conventional display, cardiothoracic ratio (CTR) and cardiac width from a segmentation (PSPNet/CheXmask, control CXAS). No human had read the images. This registration fixes the protocol of a blind reading by two board-certified radiologists and one nuclear medicine physician (adjudication of disputed radiograph items by a third radiologist) on the exploratory image sets of the study: 433 items in seven blocks (practice 3; side orientation 150 radiographs; CTR and cardiac width 100 VinDr-CXR; side marker visibility on 82 marker-masked renders; optional CTR on 50 NIH images; view and side on 40 bone scintigrams; activity side on 8 scintigrams). Three questions: inter-reader agreement; agreement of the segmentation-derived CTR and cardiac width with the human reference; whether the study's main statements change when every model reply is re-scored against the human reference. The protocol (PROTOCOL.md 1.0, English) and the item list with the sha256 of every image shown (items.json) are attached. This registration supersedes the German version 0.1 of the same protocol attached to registration https://osf.io/9rxbk; the changes since 0.1 are listed in section 9 of the protocol (blinding stated as procedural with reader attestation; ethics route and answer; readers' role; language). The measurement definitions, blocks, adjudication rule and analysis plan are unchanged since 0.1. Code and text frozen at GitHub tag reader-protocol-1.0 (commit [HASH]).

### Contributors
[Henrik Stelling und Ibrahim Güler wie bei 9rxbk. Die Leser kommen nicht in die Registrierung; sie sind Mitautoren des Manuskripts, nicht der Registrierung.]

### Affiliated Institutions
[Wie bei 9rxbk.]

### License
[Wie bei 9rxbk: CC0 1.0 oder CC-BY 4.0; gilt nur für die angehängten Dateien.]

### Subjects
Medicine and Health Sciences → Radiology

### Tags
reader study; inter-reader agreement; cardiothoracic ratio; chest radiography; bone scintigraphy; orientation; vision-language models; benchmark; preregistration; Open Image Protocol; VinDr-CXR

---

## Page "Overview"

### Research questions or hypotheses
This registration fixes measurement definitions and an analysis plan; it does not test directional hypotheses and is not part of the six confirmatory statements of registration https://osf.io/9rxbk. Three questions, answered descriptively with the registered estimators:

Q1. Inter-reader agreement of two radiologists: ICC(2,1) with 95 % CI for CTR and cardiac width; Cohen's kappa for side orientation, marker visibility and (one reader) scintigram view against the file convention.

Q2. Agreement of the segmentation-derived package values with the human reference (mean of the two radiologists after adjudication): Lin's concordance correlation coefficient and Bland–Altman mean difference with 95 % limits of agreement for CTR and cardiac width, against the shipped PSPNet/CheXmask value and, as a second column, CXAS.

Q3. Re-scoring: every model reply to the tasks patient side at the left edge, CTR class and cardiac width in mm from the study's exploratory runs is re-scored with the human reference as truth, same tolerances as the original scoring (CTR ± 0.05 absolute, cardiac width ± 10 % relative). Model accuracies against package truth and against the human reference are reported side by side; a main statement that flips is reported as such.

Also registered: the share of the 82 marker-masked images on which a reader sees a side marker (sensitivity analysis removing those images from the orientation conflict trials), and the agreement of scintigram view, orientation and activity side with the file convention and the pixel-based count.

### Foreknowledge of data or evidence
[Radio-Button:] **Data does not yet exist.**
[Die Lesedaten entstehen erst nach dieser Registrierung. Die Bilder und die Paketwerte existieren und sind öffentlich; das erklärt das nächste Feld.]

### Explanation of foreknowledge and managing unintended influences
No reading has taken place; the readings are the data of this registration. The images exist (public, de-identified datasets) and the package values they are compared with are public as part of the study's open data (repository and Zenodo bundle), so the blinding of the readers is procedural: readers see only the canonical render without annotations, package values, model replies or the other reader's values; they are not pointed to the repository, the key file or the item-id mapping; the sheet shows a running number instead of the item id; readers have no role in the project beyond the reading; and each reader attests by e-mail after the reading that no value was looked up (the attestations are stored with the reading files). The first author opens the key file only after the reading is complete. The model replies to be re-scored exist (exploratory runs 2026-09 to 2026-11) and have been analysed against the package values; the re-scoring rule and tolerances are those already used, fixed here before any reading.

---

## Page "Research Design"

### Study Type
[Radio-Button:] **Observational Study** [falls angeboten; sonst **Other** mit dem Text:]
A blind reader study: three physicians read 433 items from public, de-identified image sets on a local reading sheet; their readings are compared with each other, with segmentation-derived values, and used as reference truth to re-score existing model replies. No intervention, no patients.

### Intention For Causal Interpretation (optional)
[Radio-Button:] **No causal relationship inferred.**

### Blinding Of Experimental Treatments
[Checkbox:] **Personnel who interact directly with the study subjects (either human or non-human subjects) will not be aware of the assigned treatments.** [falls das Formular nur diese Kategorien anbietet; sonst "No blinding is involved" NICHT ankreuzen, stattdessen das nächste Feld füllen.]

### Additional Blinding During Research Or Analysis (optional)
Readers see only the canonical render (the same file the models received, at the source pixel grid), without annotations, package values, segmentation, model replies or the other reader's values. The sheet shows a running number, not the item id. The third reader reads the disputed items blinded to both first readings. The key file is opened by the first author only after the reading is complete. Readers attest after the reading that no value was looked up. Section 2 of the attached PROTOCOL.md.

### Study Design
Fully crossed reading design: every item of a block is read by every reader assigned to that block (blocks A–D both radiologists, blocks E–F the nuclear medicine physician), in a fixed random order (seed 20261102, drawn by build_set.py) that is the same for every reader. Every answer is stored append-only with timestamp and revision number; the analysis takes the latest revision per reader, item and task. Practice block (3 images outside the study set) read jointly by both radiologists before block B for calibration; not analysed. Adjudication by a third radiologist on disputed items (different categorical answers in blocks A and C; CTR difference > 0.05 or cardiac-width difference > 10 % of the mean in block B); reference = median (continuous) or majority (categorical), no majority = not assessable. Sections 3 to 5 of the attached PROTOCOL.md.

### Study Design - file upload
[PROTOCOL.md 1.0 und items.json anhängen.]

### Randomization (optional)
Item order within each block: random.Random(20261102) in build_set.py, identical for all readers. No other randomization; every assigned reader reads every item.

---

## Page "Sampling"

### Data Collection Procedures
Readers: two board-certified radiologists (R1, R2), one board-certified nuclear medicine physician (NM1), a third radiologist (R3) for adjudication only; pseudonyms in all files. Reading on a computer of the first author with a local browser sheet (no cloud service); readers get read access to the images, no copies; VinDr-CXR is not redistributed. Images: the exploratory image sets of the study (VinDr-CXR 100 paper images and 82 conflict-trial images as marker-masked renders, NIH ChestX-ray14 50, IICS-UNA bone scintigrams 40 plus 8), all public and de-identified; sha256 of every image shown in items.json. Measurements in image pixels; cardiac width in mm computed afterwards by collect.py from the header pixel spacing of the 82 VinDr images that carry one. Reader attestation by e-mail after the reading. Collection window: after this registration, [planned start DATE], until all blocks are read or [END DATE].

### Sample Size
433 items: practice 3 (not analysed); A 150 radiographs (100 VinDr, 50 NIH), side orientation; B 100 VinDr, CTR and cardiac width; C 82 VinDr marker-masked renders, marker visibility; D (optional) 50 NIH, CTR ratio; E 40 bone scintigrams, view and side; F 8 scintigrams, activity side. Two radiologists on A–D, one nuclear medicine physician on E–F, a third radiologist on disputed A–C items.

### Sample Size Rationale (optional)
The item counts are the complete exploratory image sets of the study (every image whose package values were used as truth), not a power-based sample: the purpose is to replace the package truth of exactly those images. For ICC(2,1) with two raters, n = 100 gives a 95 % CI half-width of about 0.05 at ICC 0.9.

### Starting And Stopping Rules
Start: first reading after this registration is submitted and the protocol is tagged (reader-protocol-1.0). Stop: when every assigned reader has a final revision for every item of their blocks, or at [END DATE]; blocks left incomplete are reported as such. No interim analysis; the key file is opened only after the stop.

---

## Page "Variables"

### Manipulated Variables
None. Reader (R1, R2, R3, NM1) and block are design factors, not manipulations.

### Measured Variables
Per reader, item, task and revision: side orientation (image_left / image_right / not assessable) with basis (anatomy / marker / both); cardiac-border and inner-rib-margin points in image pixels, heart_px, thorax_px, CTR, AP-projection flag; marker visibility (yes / no / unsure) with clicked position; scintigram view (anterior / posterior / unsure), side, activity half (image_left / image_right / none / not assessable); not-assessable and unsure flags, free-text comment, seconds open, image sha256, timestamp, revision. Derived by collect.py: heart_mm (heart_px × column spacing, header spacing only), spacing_source. CSV schema in README.md of the reader tooling.

### Indices
Human reference per image: mean of R1 and R2 (after adjudication) for CTR and cardiac width; majority for categorical tasks. Agreement indices as in the Overview (ICC(2,1), kappa, Lin's CCC, Bland–Altman). Re-scoring: per model and task, accuracy against package truth and against the human reference; images whose reference is "not assessable" are excluded and counted.

---

## Page "Analysis Plan"

### Statistical Models
Descriptive agreement statistics with 95 % CIs: ICC(2,1) two-way random, single measurement, absolute agreement; Cohen's kappa; Lin's concordance correlation coefficient; Bland–Altman mean difference with 95 % limits of agreement. Re-scoring with the existing scorer tolerances. No hypothesis tests, no modelling of covariates. Software and versions named in the report.

### Transformations
Cardiac width in mm = heart_px × header column spacing (no magnification correction, as for the package values). Activity side in image coordinates converted to the patient side with the reader's own orientation answer.

### Inference Criteria
None (descriptive registration). A main statement of the manuscript is reported as changed when its re-scored verdict differs from the verdict against package truth.

### Data Inclusion And Exclusion
Practice items and non-final revisions excluded. Items with reference "not assessable" excluded from the re-scoring and counted. AP-flagged images reported separately in block B. No other exclusions; missing values stay missing. Corrections are made only by the reader as a new revision; nothing is overwritten.

### Missing Data
Reported per block and reader; no imputation. An item without a final revision from a reader is missing for that reader; agreement statistics use complete pairs.

### Other Planned Analysis (optional)
Sensitivity analysis of the orientation conflict trials without the images on which a reader sees a side marker in the masked render. Scintigram view, orientation and activity side against the file convention and the pixel-based count.

---

## Page "Other"

### Context And Additional Information (optional)
Protocol attached (PROTOCOL.md version 1.0, English); item list attached (items.json, sha256 [HASH], unchanged since the version attached to https://osf.io/9rxbk). Frozen at https://github.com/HenrikStelling/open-image-protocol/tree/reader-protocol-1.0 (commit [HASH]). This registration supersedes the German protocol version 0.1 attached to https://osf.io/9rxbk; changes since 0.1 are listed in section 9 of the protocol. Ethics: the Ethics Committee of the Otto-von-Guericke-Universität Magdeburg, consulted through the co-author at Otto von Guericke University Magdeburg, stated on [DATE] that no ethics vote is required for a reader study on public, de-identified data; a written waiver was requested on [DATE] and is pending; its reference number and date will be recorded in the protocol's section 7 and in the manuscript's Methods, not by editing this registration. The reader CSV files and attestations are published with the pseudonyms in the study's Zenodo data bundle (10.5281/zenodo.23040047). Any departure from this protocol is listed in a "Deviations" section of the report and in Methods.
