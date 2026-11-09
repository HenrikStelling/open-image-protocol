# Reading protocol: human reference reading for OIP-Bench

Version 1.0, DRAFT of 2026-11-06. Supersedes `PROTOKOLL.md` (German, version 0.2 of 2026-11-04). Version 0.1 of 2026-11-02 is
the version attached to the OSF registration of the confirmatory round (https://osf.io/9rxbk, registered 2026-11-03); that
registration is not edited. Every change of substance since 0.1 is listed in section 9. Sections 1 to 7 are the measurement
definitions and the analysis plan; they are frozen before the first reading. Section 8 is the operating guide for the sheet and
is not part of the frozen definitions. Section 10 records the freeze.

Status at this draft (2026-11-09): no reading has taken place (no reader file exists under `bench/reader/readings/`). The
ethics committee has answered that no vote is required; the written waiver is requested and outstanding (section 7). The
protocol is frozen before the first reading, after the first author has approved the text.

## 1. Aim

So far the model replies in OIP-Bench have been scored against values taken from the packages: the side orientation from the
DICOM header or from the conventional display, CTR and cardiac width from a segmentation (PSPNet/CheXmask, control CXAS). No
human has read the images. This study provides a human reference by specialists and answers three questions:

1. How well do two radiologists agree with each other (inter-reader agreement)?
2. How well does the segmentation agree with the human reference (human versus model)?
3. Do the paper's main statements change when every model reply is re-scored against the human reference (sensitivity
   analysis)?

The reading also replaces the earlier model-assisted visual screen of the masked renders (side marker removed?), recorded in
`bench/marker_review.json`, with a specialist read.

## 2. Readers and blinding

- Two board-certified radiologists (R1, R2) and one board-certified nuclear medicine physician (NM1). Where the radiologists
  disagree, a third reader (R3) adjudicates the disputed images only. The readers are co-authors of the manuscript (decision of
  the authors, 2026-11-09); their contributions are stated in the paper, the readings are published under the pseudonym.
- The readers see only the canonical render of the image without annotations, that is, exactly the image the models received.
  They see no package values (pixel spacing, orientation, segmentation), no model replies and no values of the other reader.
- The package values are public as part of the open data (repository: `bench/reader/set_key.json`; Zenodo bundle:
  `derived/measurements.json` and `context.md` of each package). The blinding is therefore procedural: the readers are not
  pointed to the repository, to the key file or to the mapping of item ids, have no role in the project, and are asked before
  the reading not to look up any value for the images shown. The sheet shows a running number, not an item id. After finishing,
  each reader confirms in one sentence by e-mail that no value was looked up; the confirmations are stored with the reading
  files. The first author opens `set_key.json` only after the reading is complete. The point is stated in the limitations of the
  manuscript.
- The reading takes place on a computer of the first author (local sheet in the browser, no cloud service). VinDr-CXR is not
  passed on; the readers get read access to the images, no copies.
- Every answer is stored with a timestamp and a revision number. Corrections are made only by the reader; they create a new
  revision, nothing is overwritten or cleaned up afterwards. Missing values stay missing.

## 3. Images and blocks

All images come from public, de-identified datasets (VinDr-CXR, NIH ChestX-ray14, bone scintigrams IICS-UNA Paraguay,
CC BY 4.0). The order within each block is random (seed 20261102, drawn by `build_set.py`) and the same for every reader. The
sha256 checksum of every image shown is listed in `items.json`.

| Block | Readers | Images | Task | Guide time |
|---|---|---|---|---|
| Practice | R1, R2 | 3 VinDr images outside the study set | side and CTR, joint calibration beforehand | 15 min |
| A | R1, R2 | 150 radiographs (100 VinDr, 50 NIH) | side orientation | 30 min |
| B | R1, R2 | 100 VinDr | CTR and cardiac width, AP flag | 3 h |
| C | R1, R2 | 82 VinDr (conflict-trial images), masked render | side marker visible? | 15 min |
| D (optional) | R1, R2 | 50 NIH | CTR, ratio only | 1.5 h |
| E | NM1 | 40 whole-body scintigrams (20 patients, anterior and posterior) | view, side orientation | 15 min |
| F | NM1 | 8 scintigrams with a clear left/right count asymmetry | image half with more activity | 5 min |

Note: the 82 images of block C (clear cardiac side cue, not excluded by the marker review of 2026-09-30) are not the same 82
images that carry a pixel spacing in the header; the two sets overlap in 68 images.

## 4. Measurement definitions

### 4.1 Side orientation (blocks A and E)

Question: which image edge shows the patient's right side? Answers: left image edge, right image edge, not assessable. In
addition the basis: anatomy, marker/label, both.

- Anatomical criteria on the chest radiograph: aortic knob and cardiac apex on the patient's left, gastric bubble on the left,
  liver shadow and the higher hemidiaphragm on the right. The decision follows the anatomy as it appears in the image; a situs
  inversus or dextrocardia is answered from the image and noted in the comment.
- A burnt-in side marker (R, L, text) may be used. The basis is then "marker/label" or "both", so that the analysis can separate
  anatomically based from label-based answers.
- Not assessable: neither anatomy nor marker allows a decision, or the two contradict each other without resolution.

### 4.2 CTR and cardiac width (blocks B and D)

Transverse cardiac diameter: the horizontal distance between the most lateral point of the right heart border and the most
lateral point of the left heart border of the cardiac silhouette. The two points may lie at different heights; the tool uses
the horizontal component (which equals the sum of the greatest distances of the two heart borders from the midline).
Pericardial and epicardial fat does not count towards the silhouette where it can be delineated; hilar vessels do not count.

Internal thoracic diameter: the greatest horizontal internal distance of the thorax between the inner rib margins (pleural
line), usually at the level of the right hemidiaphragm. Here too the horizontal component is used.

CTR = transverse cardiac diameter / internal thoracic diameter. Both lengths are recorded in image pixels of the source grid.
The cardiac width in millimetres is computed afterwards by `collect.py` from the pixels and the header pixel spacing, only for
the 82 VinDr images that carry a header pixel spacing; the readers do not see the pixel spacing. No magnification correction is
applied (detector plane), as for the package values.

- AP projection: tick when the image was recognisably taken a.p. (scapulae over the lung fields, clavicle projection, supine
  patient, corresponding label). The measurement is made anyway; the analysis reports the AP images separately.
- Not assessable: heart borders or thoracic borders cannot be delineated (effusion, opacification, cut-off, gross rotation). A
  partial measurement (thorax only or heart only) is stored but does not enter the CTR.
- Before block B both radiologists read the three practice images together and align their point placement (calibration).
  The practice images are not part of the study set and are not analysed.

### 4.3 Side marker in the masked image (block C)

In the conflict trials the models saw a masked render: everything outside a lung box is blacked out so that burnt-in side
markers disappear. Question: is a side marker or side label visible in this masked image? Answers: yes, no, unsure. For yes or
unsure, the position is clicked.

- A side marker is any burnt-in sign that names a body side: R, L, D, S, "rechts", "links", "re", "li", arrows with a side
  reference. Projection labels (PA, AP), date, device text or numbers without a side reference do not count; if it is unclear
  whether a sign names a side, "unsure" with a comment.
- Symmetrical foreign bodies (ECG electrodes, clips, buttons) are not side cues.

### 4.4 Scintigrams (blocks E and F)

The canonical render is shown (hot = bright), invertible. The view is not displayed.

- View: anterior, posterior, unsure. Criteria: anterior shows the sternum, facial skeleton, anterior ribs, patellae; posterior
  shows the spine, scapulae, sacroiliac joints, kidneys, posterior ribs.
- Side orientation: which image edge shows the patient's right side? Answers as in 4.1. In conventional display the patient's
  right lies at the left image edge in the anterior view and at the right image edge in the posterior view; the decision,
  however, follows the image, not the convention.
- Activity (block F): which image half (left or right in the image) shows more activity overall, spine and bladder excluded?
  Answers: left image half, right image half, no clear difference, not assessable. The answer is deliberately recorded in image
  coordinates; the analysis converts it to the patient side using the reader's own orientation answer.

## 5. Adjudication (third reader)

Disputed are: different categorical answers (including "not assessable" against an answer) in blocks A and C; in block B a CTR
difference above 0.05 or a cardiac-width difference above 10 percent of the mean. The third reader reads only the disputed
images, blinded to both first readings. The reference is then the median of the three values (continuous) or the majority
(categorical); if there is no majority, the image counts as "not assessable". The scintigrams have one reader; deviations from
the package convention are reported, not adjudicated.

## 6. Analysis plan

All analyses run on the frozen CSV files (`bench/reader/readings/`), merged by `bench/reader/collect.py` (latest revision per
reader, image and task).

1. Inter-reader agreement: CTR and cardiac width ICC(2,1) (two-way random, single measurement, absolute agreement) with 95
   percent confidence interval; side orientation, marker and view Cohen's kappa.
2. Human versus segmentation: the reference is the mean of the two radiologists (after adjudication). Lin's concordance
   correlation coefficient and Bland-Altman (mean difference, 95 percent limits of agreement) for CTR and cardiac width against
   the value shipped in the package (PSPNet/CheXmask); CXAS as a second column.
3. Re-scoring: every model reply to `left_edge`, `ctr` and `heart_mm` is re-scored with the human reference as truth, with the
   same tolerances as before (CTR plus/minus 0.05 absolute, cardiac width plus/minus 10 percent relative, `bench/tasks.py`).
   Images that the reference lists as "not assessable" are excluded and counted. Model accuracies against package truth and
   against the human reference are reported side by side; if a main statement flips, this is reported and the framing is
   adjusted.
4. Marker: the share of the 82 masked images on which a reader sees a side marker; these images are removed from the conflict
   trials in a sensitivity analysis.
5. Scintigrams: agreement of view and orientation with the file convention; activity side against the pixel-based count
   (`bench/tasks_nm.py`).
6. The practice images and all non-final revisions do not enter the statistics. Software and versions are named in the report.

## 7. Ethics and data

Public, de-identified datasets; no patient contact; no data from a clinic. The readers are specialists who read public images;
no reader data beyond the readings and the pseudonym (R1, R2, R3, NM1) are collected.

The question whether a reader study on public data requires an ethics vote was put to the Ethics Committee of the
Otto-von-Guericke-Universität Magdeburg through the co-author at Otto von Guericke University Magdeburg (inquiry of [DATE]). The inquiry also asked whether the answer
covers the external co-authors and the readers who are not affiliated with that university.

Answer: the committee stated that no ethics vote is required for a reader study on public, de-identified data; a written
waiver was requested on [DATE] and is on file as [REFERENCE, DATE OF THE WAIVER LETTER]. Scope (question 3, external co-authors
and readers): [TO FILL FROM THE WAIVER]. [Bracketed items are filled in when the waiver letter arrives; if the first reading
takes place before that, the date of the committee's preliminary answer and the date of the first reading are both recorded
here.]

The reader CSV files are published with the reader pseudonym.

## 8. Operating the sheet

1. The first author starts the sheet: `python bench/reader/serve.py`, then `http://127.0.0.1:8765/reader.html` in the browser.
   "Autosave in CSV aktiv" appears at the top right. Without the server (double-click on `reader.html`) the sheet saves in the
   browser only; then export the CSV regularly ("CSV exportieren").
2. Enter the reader id (R1, R2, R3 or NM1) and the role, choose the block. On first start the short rules unfold.
3. Image: mouse wheel scrolls, Cmd/Ctrl plus mouse wheel zooms, holding the space bar and dragging pans. Brightness and
   contrast affect the display only. "invertiert" inverts the grey values.
4. Side orientation, marker, view, activity: click the answer or press keys 1 to 4. "Not assessable" (n) and "unsure" (u) at
   any time. Comment optional.
5. CTR: "Herz messen" (h), then two clicks on the most lateral points of the cardiac silhouette; "Thorax messen" (t), then two
   clicks on the inner rib margins. The pixel values and the CTR appear immediately. Clicking "Herz messen" again discards the
   heart points and allows a new measurement. Tick AP projection where it applies.
6. Marker: for "yes" or "unsure" click once on the spot in the image; the circle shows the stored position.
7. Continue with the right arrow key; "Nächstes offenes" jumps to the next incomplete image. The progress bar counts complete
   images. Breaks are possible at any time; the state is kept.
8. At the end of each block export the CSV once as an additional backup; the first author stores the file next to the server
   files in `bench/reader/readings/`.

The sheet's user interface is in German, the readers' working language; the answer values stored in the CSV are the English
codes listed in `README.md`.

## 9. Changes from version 0.1

Version 0.1 (German, 2026-11-02, commit `abcad9f`, file `PROTOKOLL.md`) is the version attached to registration
https://osf.io/9rxbk. Changes of substance since then, with date and reason:

1. **2026-11-04 (version 0.2), section 2, blinding.** Version 0.1 stated that the key file `set_key.json` "is not opened before
   the reading is complete". Added: the package values are public as part of the open data (repository and Zenodo bundle), so
   the blinding is procedural, not technical; the readers are not pointed to the repository or the key file, the sheet shows a
   running number instead of the item id, and each reader attests after the reading that no value was looked up. The point is
   named in the limitations. Reason: the earlier sentence described a safeguard that the public data do not provide.
2. **2026-11-06 (version 1.0), section 7, ethics.** Version 0.1 said that whether the first author's institution requires a
   confirmation for reader studies on public data "is clarified beforehand and stated in the paper". Replaced by: the question
   was put to the Ethics Committee of the Otto-von-Guericke-Universität Magdeburg through the co-author at Otto von Guericke University Magdeburg, including the question
   whether the answer covers the external co-authors and readers; the committee's answer (name, reference number, date, scope)
   is recorded in section 7. Reason: the inquiry was routed through that co-author's institution, not the first author's. [Pending the first author's
   confirmation, to be added: the first author works in a private practice without an ethics committee of its own; the
   co-author is a member of the OVGU Faculty of Medicine, whose committee advises its members.]
   Status 2026-11-09: the committee answered that no vote is required; a waiver was requested, the letter is outstanding.
3. **2026-11-06 (version 1.0), language and wording.** The protocol is now in English (`PROTOCOL.md`); `PROTOKOLL.md` stays in
   the repository as the historical version with a note at the top. Project-internal process terms were removed; persons are
   named by author role or affiliation, work done by scripts is attributed to the script (`build_set.py`, `collect.py`). Editorial, no change
   to the measurement definitions or the analysis plan.
4. **2026-11-09 (version 1.0), section 2, role of the readers.** Version 0.1 left the readers' role open. Added: the readers
   are co-authors of the manuscript (decision of the authors). No effect on the measurements or the analysis.
5. **2026-11-06 (version 1.0), structure.** Section 8 (operating the sheet) is stated as not belonging to the frozen
   definitions; sections 9 (this list) and 10 (freeze record) added. No change to sections 1 to 7 beyond items 1 and 2.

Items not changed since 0.1: the reading set (`items.json`, sha256
`2349a71e6e278e536bc293f170b7550572341cb37b1b0e1b997c0b53fb5281d2`, unchanged since commit `abcad9f`), the blocks, the
measurement definitions in section 4, the adjudication rule in section 5 and the analysis plan in section 6. A one-page
German information sheet for the readers (`leserinformation.html`, `leserinformation.pdf`) summarises sections 1 to 7 and
contains no pointer to the repository or the key file.

## 10. Freeze record

To be filled in at the freeze, after the ethics answer is on file and the first author has approved the text:

- No reading had taken place at the freeze: [confirmed on DATE; `bench/reader/readings/` empty].
- Commit: [HASH]; tag: `reader-protocol-1.0`.
- sha256 of `PROTOCOL.md`: [HASH]; of `items.json`: `2349a71e6e278e536bc293f170b7550572341cb37b1b0e1b997c0b53fb5281d2`
  (the item list with the per-image sha256 values is `items.json` itself).
- OSF registration in project https://osf.io/ntgrb, referring to https://osf.io/9rxbk and stating that it supersedes the
  version 0.1 attached there: [URL / DOI, TIMESTAMP].
