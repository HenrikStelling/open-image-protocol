# Korrekturplan für die RA-Fassung des OIP-Papers

Geschrieben 2026-09-23 in der OIP-Session, zum Einarbeiten in der Claude-Session im Repo `/Users/pal/Projects/Research_Automation`, Branch `claude/oip-paper`. Basis ist `oipbench/PAPER/manuscript_oip_revised.md` (Commit 629c9bd). Regel des Repos: **jede Änderung an der Quelle** (`template_oip.md`, `analysis_oip.py`, `citations_oip.py`, `config_oip.yaml`, `papers.yaml`), nie in der gebauten Datei; danach `build → audit → peer review` erneut. Kein Modell erzeugt eine Zahl.

Ergebnis des Vergleichs (OIP-Session, `docs/paper/manuscript-draft.md` gegen die Revision): alle gemeinsamen Zellen sind identisch; wo sich beide unterscheiden, ist die RA-Fassung richtig (Bone-Scan-Aggregat auf 88 gemeinsame Items, Kosten nur über die Röntgen-Sets, CXAS-CTR-Abweichung berichtet statt beiseitegelegt, Abstentions-Flag als unzuverlässig deklariert, Primärendpunkt als „Nutzung genannter Fakten" gefasst). Die Revision bleibt deshalb die Basis. Was ihr fehlt, ist die Motivation des Protokolls: die Design-Regeln, das Paketformat im Detail und der Befund, was vier öffentliche Quellen einem Konverter tatsächlich liefern. Das kommt aus dem OIP-Entwurf, Abschnitte 3 und 4, und wird unten so eingebaut, dass jede Zahl weiter aus `results.json` kommt.

## Kickoff-Prompt (in der RA-Session einfügen)

```
Arbeite den Korrekturplan /Users/pal/oip-work/docs/paper/RA-revision-plan.md in die OIP-Studie ein
(Branch claude/oip-paper, Basis manuscript_oip_revised.md). Teile A bis F in dieser Reihenfolge; nur an
der Quelle ändern (template_oip.md, analysis_oip.py, citations_oip.py, config_oip.yaml, papers.yaml);
danach ingest → analysis → citations → build → audit → peer review neu laufen lassen. Keine Zahl darf
im Template stehen, die nicht aus results.json kommt. Amendment 10 in PROTOCOL_oip.md anlegen, das die
neuen deskriptiven Konverter-Felder beschreibt. Halte an, wenn eine Zahl im eingefügten Text nicht aus
results.json belegbar ist, und melde sie mir, statt sie zu schätzen.
```

## A. `analysis_oip.py`: Konverter- und Messbericht-Felder erweitern (Voraussetzung für Teil C)

Der Block `R["converter"]` (Zeilen ~199–215) liest bereits `data/raw/reference/phase2-conversion-stats.json` und den Messbericht. Er soll zusätzlich, pro Quelle (`vindr`, `rsna`, `siim`, `nih`), diese Felder aus `phase2-conversion-stats.json` übernehmen, jeweils als Zähler wie in der Datei:

- `spacing_source` (VinDr: PixelSpacing 815, none 185; RSNA/SIIM: PixelSpacing 500/300; NIH: dataset_metadata 300)
- `confidence` (VinDr: medium 809, low 6, none 185; RSNA 500 low; SIIM 300 low; NIH 300 low)
- `photometric` (VinDr: MONOCHROME1 216, MONOCHROME2 784)
- `bits` (VinDr: 12 → 702, 14 → 253, 16 → 44, 10 → 1; RSNA/SIIM/NIH 8)
- `voi` (VinDr: WindowCenterWidth 964, auto_percentile 36; RSNA/SIIM auto_percentile; NIH full_range)
- `orientation` (inferred: 1000/500/300/300)
- `ts` (VinDr: Implicit VR LE 550, JPEG 2000 lossless 378, Explicit VR LE 72; RSNA/SIIM JPEG Baseline; NIH png)
- `computed image width mm` min/median/max (VinDr 180/348/2688 bei n = 815; RSNA und SIIM 142/146/199; NIH 316/420/428)
- `flags` (VinDr: orientation_inferred 1000, spacing_uncalibrated 815, missing_pixel_spacing 185, no_voi_in_source 36, implausible_extent 6; RSNA/SIIM: implausible_extent, lossy_compression, no_voi_in_source, orientation_inferred, spacing_uncalibrated je 100 %; NIH: no_voi_in_source, non_dicom_source, orientation_inferred, spacing_uncalibrated je 100 %)
- `context_md_mean_chars` (3331 / 3568 / 3569 / 3512) und `package_source_size_ratio` (1.23 / 9.41 / 9.40 / 3.39)

Aus `phase2-measurement-report.md` (per Regex, wie bereits für 338/34 %): CTR median 0.478, p10 0.415, p90 0.553; Regionen pro Bild 13.0; mm-Breiten berichtet für 815, verweigert für 185; Herzbreite median 128 mm (p10 109, p90 149); Thoraxbreite median 270 mm.

Count-Recovery der Bone Scans: die Zahl „71 %" steht nur in PLAN.md. Belegbar wird sie aus den kopierten Manifesten: in `data/raw/packages_meta/bonescan/*/oip.json` das Feld `extensions["org.openimageprotocol.counts_recovery"]` zählen (vorhanden/erfolgreich vs. nicht) und als `converter.bonescan_counts_recovery` ablegen. Wenn das Feld dort nicht auswertbar ist, den Satz im Text weglassen.

Stratifizierung des VinDr-100-Sets (Review-Frage Q1): Regel in `/Users/pal/oip-work/scripts/make_bench_set.py:22`: Strata = (Befund vorhanden, Kardiomegalie-Label) × Spacing verfügbar, Seed 0, aus den 1.000 Sample-IDs; NIH 50 mit Seed 0 ohne Strata; Pilot 20 Seed 0. In `design.datasets` als `sampling` eintragen.

Tabellen in `tables()` umnummerieren: die neue Quellentabelle wird **Tabelle 1** (steht in §3), die bisherigen Tabellen 1–10 werden 2–11; Captions und alle Verweise im Template mitziehen. Die Abbildungsnummern bleiben. (Alternative, falls die Audits Verweise auf die alten Nummern erwarten: die Quellentabelle als „Tabelle S1" in einen Anhang setzen. Ich empfehle die Umnummerierung, weil die Tabelle die Motivation trägt.)

## B. `citations_oip.py`: Korpus erweitern

Neue Einträge, damit die eingefügten Abschnitte zitierbar sind (DOI/PMID/arXiv wo vorhanden; Standards-Seiten als flagged Einträge nach Runbook Phase G):

| Schlüssel im Text | Werk |
|---|---|
| [LSP] | Microsoft, Language Server Protocol, Overview (Webseite) |
| [MCP] | Anthropic, Model Context Protocol, Ankündigung 2024 und Spezifikation 2026-07-28 (Webseite) |
| [MHS] | Anthropic, Model Hardware Standard, Research Preview 2026 (Webseite) |
| [DICOM] | NEMA PS3.18 §F (DICOM JSON model) und PS3.3 §10.7 (Basic Pixel Spacing Calibration Macro) |
| [FHIR] | HL7 FHIR ImagingStudy (Webseite) |
| [BIDS] | Gorgolewski KJ et al., The brain imaging data structure, Sci Data 2016, doi:10.1038/sdata.2016.44 |
| [OME] | OME-NGFF specification / RFC-4 (Webseite) |
| [LLMSTXT] | llms.txt proposal (Webseite) |
| [CXAS] | Seibold C et al., Accurate fine-grained segmentation of human anatomy in radiographs via volumetric pseudo-labeling, 2023 (arXiv:2306.03934, prüfen) |
| [IHE] | IHE Radiology, AI Results (AIR) profile (Webseite) |

Bereits vorhanden und im Text wiederverwendet: [9] highdicom, [10] CDEs, [11] Set-of-Mark, [12] WindowNet, [14] TorchXRayVision, [15] VinDr-CXR, [16] ChestX-ray14, [17] Paraguay-Bone-Scans, [18] CheXmask, [1] MedVision, [2] Your other Left, [4] MC-CXR.

## C. `template_oip.md`: §3 ersetzen und §3.8 anfügen

§3 der Revision (Zeilen 24–37: „Design rules", „Package", Figure 1, „Reference file", „Measurements and scope", „Reference implementation") wird durch den folgenden Text ersetzt. Zahlen sind als Jinja-Ausdrücke markiert; die Feldnamen entsprechen Teil A. Die Abschnittsnummer 3 und alle folgenden Nummern bleiben, §4 „Methods" bleibt unverändert. Zitatschlüssel in eckigen Klammern gemäß Teil B.

---

# 3. The Open Image Protocol

## 3.1 Design rules

The protocol follows ten rules derived from the comparison of the Language Server Protocol [LSP], the Model Context Protocol [MCP] and the Model Hardware Standard [MHS]. R1, a neutral core: every package has geometry in millimetres, orientation, intensity units and provenance, whatever the modality. R2, self-describing twice: machine-readable (`oip.json`, JSON Schema) and model-readable (`context.md`, fixed template). R3, a small verb set. R4, physics and safety live in the tool layer, not in the model. R5, an assertion level on every fact. R6, conformance profiles so partial producers remain useful. R7, semantic versioning, a deprecation policy and a change process with proposals (OEPs). R8, stateless packages: everything needed to interpret the image is inside. R9, ship the bundle: specification, SDK, CLI, MCP server, examples and benchmark together. R10, measure uplift: every protocol change is evaluated on the benchmark before it enters the specification.

## 3.2 Package layout, layers and profiles

A package is a directory `<name>.oip/` (or a zip of it) with a manifest `oip.json`, the reference file `context.md`, a canonical 8-bit render, an annotated render, lossless 16-bit PNG pixels per frame, optional derived measurements and masks, and the de-identified DICOM headers as a DICOM JSON model [DICOM] (Figure 1). The manifest is organised in six layers: L0 identity, provenance and de-identification; L1 acquisition, geometry, intensity semantics and quality flags; L2 renders and pixels; L3 semantic regions; L4 measurements; L5 narrative and external context. Profiles are named layer sets (`core` = L0–L2, `measured` = L0–L4, `full` = L0–L5); a producer must declare its profile and must not claim a layer it did not fill. Manifest rules make the guardrails explicit: pixel spacing must be null unless a spacing with a stated source exists, and a consumer must not infer physical size when it is null; the calibration plane distinguishes detector-plane from patient-plane spacing [DICOM]; counts are comparable only within one package and energy window; identifiers, names, dates and free text are removed or hashed, and age is reduced to a five-year band.

![Figure 1. Package layout and layers (schematic).](oipbench/RESULTS/oip/fig6_package.png)

## 3.3 The reference file

`context.md` is generated from the manifest by a fixed template (version 0.2 in this paper) with nine sections in fixed order: what this is; how to read the renders; measured facts; computed measurements; inferred; unknowns and cautions; external context; self-check; machine-readable. Each statement in the factual sections is prefixed with its assertion level in brackets (`measured`, `computed`, `inferred`, `external`, `unknown`). The "how to read the renders" section states the polarity guarantee (higher attenuation or higher counts is brighter in the canonical render), the anatomical side at each image edge, the pixel spacing with its source, plane and confidence, or the sentence "NO pixel spacing is available. Do not state sizes in mm or cm", and the window used. The self-check section lists four question-and-answer pairs whose answers are in the package (which side is at the left edge, the modality, whether sizes can be given in millimetres, and the polarity), so that a model can calibrate before answering. External content, such as dataset labels or prior-report text, is not rendered by default; when a consumer requests it, the cautions precede it and it is introduced as unverified (Section 5.5). The pattern of a prose file generated for a model from structured data follows llms.txt [LLMSTXT] and the reference files of the Model Hardware Standard [MHS]. The file is about {{ converter.vindr.context_md_mean_chars }}–{{ converter.siim.context_md_mean_chars }} characters, roughly 830–890 tokens, for a chest radiograph.

## 3.4 Renders

The canonical render is an 8-bit greyscale image with the frame's rows and columns, no rotation, flip, crop or resampling, polarity high-is-bright, and the source display window when present or robust percentiles otherwise; the exact transform is recorded. The annotated render adds a letterbox margin with edge labels giving the anatomical side of each edge, a scale bar with its length in millimetres or the text "no calibrated scale", optional numbered region marks listed in the manifest (a constrained form of set-of-mark prompting [11]), and a modality-and-view title; the image area stays pixel-aligned with the canonical render so that coordinates in the manifest remain valid after subtracting the stated margins. Scintigraphy packages should also carry an inverted render, because hot-is-dark is the conventional display.

## 3.5 Measurements as tool outputs

Measurements live in `derived/measurements.json` with an identifier, name, value, unit, method, confidence and validation status, and are computed by deterministic tools, never by the model. The `measure` verb refuses to return millimetres when spacing is null and refuses to compare counts across energy windows. For chest radiographs the reference implementation derives anatomical regions from a segmentation model in a published chest-radiograph library [14] and computes the transverse cardiac diameter, the thoracic width and the cardiothoracic ratio (CTR). The validation status of every value is `unvalidated` until a tiered validation has been run: Tier 0 on synthetic phantoms with exact truth, Tier 1 plausibility rules and cross-tool checks, Tier 2 against reference masks [18], Tier 3 against expert readings.

## 3.6 Modality adapters

The reference converter handles DICOM projection radiography (CR, DX), single-frame CT and MR, and multi-frame nuclear-medicine objects, and has a non-DICOM path for PNG or JPEG images accompanied by dataset metadata, which are marked with the `external` assertion level and a low spacing confidence. For planar scintigraphy the adapter records tracer, activity, uptake time, energy windows and per-frame counts when available, renders with a square-root window and, for sources that ship stretched 8-bit PNGs, recovers the count quantisation lattice where possible (Section 3.8).

## 3.7 Access paths and scope

The same verbs (`describe`, `locate`, `measure`, `window`, `crop`, `overlay`, `validate`) are exposed by a Python SDK, a command-line tool and an MCP server [MCP]. None of them is required: to hand an image to a model, one sends a render and `context.md`. By design the protocol carries observations and optional cited reference ranges and never interpretations; findings, impressions and diagnoses are produced by the consuming model or a downstream tool, and detector outputs may be carried only as `inferred` observations with the producing tool named. Standards that describe AI outputs for clinical systems, DICOM SR TID 1500 [9], the IHE AI Results profile [IHE], FHIR ImagingStudy [FHIR] and common data elements [10], are export targets, not inputs; sidecar conventions such as BIDS [BIDS] and OME-Zarr [OME] are the closest analogues for the geometry layer.

## 3.8 Reference implementation and what public sources deliver

We converted {{ converter.n_images }} images from four public sources with the reference converter: {{ converter.datasets.vindr.n }} VinDr-CXR DICOM files [15], {{ converter.datasets.rsna.n }} RSNA Pneumonia and {{ converter.datasets.siim.n }} SIIM-ACR Pneumothorax DICOM files, and {{ converter.datasets.nih.n }} NIH ChestX-ray14 PNG files [16], with {{ converter.n_failures }} failures. Table 1 summarises what the sources contained. Both the conversion statistics and the measurement statistics below come from the converter's own reports, not from the benchmark replies analysed in Section 5.

*(Tabelle 1 wird von `tables()` erzeugt; Spalten: Source, n, Format/transfer syntax, Pixel spacing, Spacing confidence, Polarity / bit depth, Window in source, Orientation in header; Zeilen VinDr-CXR, RSNA Pneumonia, SIIM-ACR, NIH ChestX-ray14; Zellinhalte aus `converter.<set>.*` wie in Teil A.)*

Only VinDr-CXR retains a trustworthy absolute scale, for {{ converter.vindr.spacing_source.PixelSpacing }} of {{ converter.datasets.vindr.n }} images ({{ pct }} %); {{ converter.vindr.photometric.MONOCHROME1 }} of its images are stored inverted (MONOCHROME1) and would be rendered with the wrong polarity by a naive export. The RSNA and SIIM files carry a pixel-spacing tag that no longer matches the resampled 8-bit pixels, so a converter that trusts the tag produces an image width of {{ converter.rsna.width_mm.min }}–{{ converter.rsna.width_mm.max }} mm for an adult thorax; the converter's plausibility rule flagged every one of them. The orientation was inferred from the view in every image of every source, which is why the left-edge truth of the benchmark rests on a laterality check rather than on a header (Section 4.4). The converted package is {{ converter.vindr.package_source_size_ratio }} times the size of the DICOM source for VinDr-CXR.

On the {{ converter.vindr_measured }} VinDr-CXR images the anatomy adapter produced on average {{ converter.regions_per_image }} regions per image and a CTR for every image (median {{ converter.ctr_median }}, 10th–90th percentile {{ converter.ctr_p10 }}–{{ converter.ctr_p90 }}), with a transverse cardiac diameter for the {{ converter.mm_reported }} images with calibrated spacing (median {{ converter.heart_width_median_mm }} mm) and a refusal for the {{ converter.mm_refused }} without. The CTR exceeded 0.50 in {{ converter.vindr_ctr_above_0_5_pct }} % of images, about twice the dataset's cardiomegaly label prevalence, because the union of the lung fields underestimates the internal thoracic width; the measurement is therefore biased high and its validation status remains `unvalidated` pending Tier 2 (Section 5.8). A laterality sanity check flagged {{ converter.laterality_flags }} of {{ converter.vindr_measured }} images; it compares the segmentation model's left- and right-sided structures with the image side that the converter's inferred edge labels call left, so it tests the two against each other and shares their common assumption of the standard display convention (Section 6, Limitations).

For scintigraphy we used a public whole-body bone-scan collection [17] of 16-bit PNG images in anterior and posterior pairs. *(Satz zur Count-Recovery nur, wenn `converter.bonescan_counts_recovery` belegt ist.)*

---

## D. Weitere Änderungen an `template_oip.md`

1. **§1 Introduction, Absatz 2:** nach „…are no longer in its input." den Satz ergänzen: „Section 3.8 quantifies this for four public chest-radiograph sources: one retains a trustworthy absolute scale for 82 % of its images, two carry a pixel spacing that is stale after resampling for all of theirs, and one has no header at all." (die 82 % aus `converter`; sonst als Jinja-Ausdruck).
2. **§2 Related work:** den Satz zu Standards um [IHE], [FHIR], [BIDS], [OME], [LLMSTXT] ergänzen (Text wie in §3.7, ohne Doppelung).
3. **§4.2 Data:** die Stratifizierungsregel aus Teil A einsetzen (Q1 des Reviews): „stratified by finding present, cardiomegaly label and spacing availability, seed 0, from the converter's 1,000-image sample; 82 of the 100 images have calibrated spacing".
4. **§4.4 Tasks:** Regel für das falsche Label (Q2): „drawn per image, with a seed derived from the package name, from the labels the image does not carry" (`vendor/tasks.py`, `findings_misled`).
5. **§4.4, Modality/View/Counts (Review M1, Q5):** die drei Reported-only-Tasks als Spalten in Tabelle 3 (Modality, View) und Tabelle 8 (Counts comparable) **an der Quelle** ergänzen; die Zellen liegen in `per_task` und `nm.per_task` bereits vor. Dann den Satz „released with the result file rather than tabulated here" streichen.
6. **§5.3 NIH-Absatz:** „(n = 50 per task)" einfügen (Claim-Audit-Nit 1).
7. **§5.8:** ersten Satz schärfen (Review M9): „…are the package's own segmentation-derived values, produced by the same pipeline that built the packages, not an independent reference…".
8. **§6 Discussion, Q3-Antwort und Q4-Antwort** als je einen Satz: Lateralitäts-Check wie in §3.8 beschrieben; NIH unterscheidet sich von VinDr in drei Paketfeldern zugleich (dataset-derived low-confidence spacing, 8-bit non-DICOM source, kein Scale-Task), so dass die Zuordnung des L0–L2-Effekts zum Spacing plausibel, aber nicht isoliert ist.
9. **§6, Prior-Work-Schleife (Review Minor 18):** einen Satz, der das Flip-Ergebnis auf [2] und [4] zurückbezieht, falls in der Revision noch nicht vorhanden.
10. **Titel** (`papers.yaml`): kürzen auf „Self-describing medical image packages supply the facts vision-language models cannot see, but not the check against the pixels" (Review Minor 16). Abstract auf ≤ 300 Wörter straffen, ohne Zahl zu streichen.
11. **Abbildungsdateien** bei Submission umbenennen (`fig6_package.png` → `fig1_package.png` usw.; Review Minor 17): erst am Ende, in `analysis_oip.py figures()` und den Captions gemeinsam.
12. **Declarations:** DOI eintragen, sobald Zenodo-Record existiert (`config_oip.yaml availability`).

## E. `PROTOCOL_oip.md`: Amendment 10

„2026-09-23/24 — descriptive converter fields added (§4.10): per-source conversion statistics, measurement-report summaries, bone-scan count-recovery count and the sampling rule, read from the copied OIP reports and package manifests; descriptive only, no test changed; made after the peer review to supply the protocol-motivation section (§3.8) with traceable numbers."

## F. Danach

`ingest` (unverändert) → `analysis_oip` → `reconcile` (die neuen Felder sind nicht Teil des Scoreboard-Abgleichs, Abgleich muss weiter 0 unexplained zeigen) → `citations_oip --top 30` (neue Einträge prüfen; Standards-Seiten bleiben flagged) → `build` → `audit_oip` (eval, claim, citation) → Peer-Review-Handoff mit denselben eingefrorenen Items plus Tabelle 1. Deliverable erneut `manuscript_oip_revised.{md,docx,html}`; anschließend `PROTOCOL_oip.md` und `results.json` nach `~/oip-work/docs/paper/` kopieren (Runbook Phase I) und dort `manuscript-draft.md` als „superseded by the RA revision" markieren.

Nicht Teil dieses Plans, sondern der Benchmark-Todos in `PLAN.md` (Phase 3b): Scorer-Korrekturen, neue Wahrnehmungs-Tasks, entkonfundierter Misleading-Test, Bone-Scan-Sampling, Mehrfachantworten. Diese verändern Zahlen und gehören in eine zweite Benchmark-Runde, nicht in die Revision dieses Papers.

## G. Nachtrag 2026-09-29: Amendment 12 — Output-Cap-Abschneidung bei glm-5.3-flash (Limitation, keine Zahl ändert sich)

Befund (OIP-Session, `docs/reports/oep-002-2026-09-29.md`, Abschnitt „Paper-run truncation"): glm-5.3-flash ist das einzige Modell, das sein Reasoning sichtbar im Antworttext führt und mit `</think>` abschließt, auch bei `think=false`. Der Harness begrenzt Ollama-Antworten auf 800 Tokens (`num_predict`). In den L0–L2-Zellen wird das Reasoning vor der Antwort abgeschnitten, und der Scorer liest dann eine Zahl aus dem abgeschnittenen Text:

| Set | Task | Bedingung | n | korrekt (alle Zeilen) | abgeschnitten | korrekt (vollständige Zeilen) |
|---|---|---|---|---|---|---|
| VinDr-100 | CTR | raw | 100 | 50 % | 4 | 52 % (n = 96) |
| VinDr-100 | CTR | L0–L2 | 100 | 28 % | 33 | 39 % (n = 67) |
| VinDr-100 | Herzbreite | raw | 82 | 40 % | 7 | 44 % (n = 75) |
| VinDr-100 | Herzbreite | L0–L2 | 82 | 26 % | 57 | 40 % (n = 25) |
| NIH-50 | CTR | raw | 50 | 54 % | 4 | 59 % (n = 46) |
| NIH-50 | CTR | L0–L2 | 50 | 26 % | 20 | 40 % (n = 30) |
| NIH-50 | Herzbreite | raw | 50 | 42 % | 4 | 46 % (n = 46) |
| NIH-50 | Herzbreite | L0–L2 | 50 | 40 % | 13 | 43 % (n = 37) |

Volle-Datei- und Annotations-Zellen: 0 abgeschnitten. Kategoriale Tasks: 0 abgeschnitten. Kein anderes Modell betroffen (keine `</think>`-Tags, kurze Ausgaben). Die Zahlen oben sind Scorer 0.3 (RA-Paper führt 0.2; die Richtung ist dieselbe).

Umsetzung in der RA-Fassung:
1. **PROTOCOL_oip.md, Amendment 12:** „2026-09-29 — post-hoc limitation, no cell changed: glm-5.3-flash replies in the L0–L2 arm were cut off by the harness output cap (800 tokens) inside visible reasoning in 33/100 (VinDr CTR), 57/82 (VinDr cardiac width), 20/50 and 13/50 (NIH) rows; the scorer read a number from the truncated text. On complete rows the L0–L2 drop remains (VinDr CTR 52 → 39 %, NIH 59 → 40 %) but is smaller. Detected in the OEP-002 readout; the harness now records `done_reason` per row and can route reasoning to a separate field."
2. **§5.3 / §6 (L0–L2-Absatz):** den Satz „glm computed widths from its own pixel estimates" ergänzen um: „…and in a third to two thirds of its L0–L2 replies was cut off by the harness's output cap before answering, so its L0–L2 cells combine a real drop with a truncation artefact (Amendment 12)". gpt ist nicht betroffen (kein sichtbares Reasoning); der gpt-Befund (57 → 42) bleibt wie er ist.
3. **§7 Limitations:** ein Satz zur Output-Cap-Abschneidung als Harness-Limitation, nur glm, nur numerische Tasks unter L0–L2.
4. Kein Re-Scoring, kein Re-Run für die Revision (Korrektheitsregel unverändert; ein glm-Wiederholungslauf mit `think=true` gehört in Runde 3).
