# Co-author review (2026-10-23): action list

Source: co-author's written review of the OIP manuscript and repository (German, kept privately).
This file splits the review into (A) changes to the manuscript, owned by the Research_Automation
session, and (B) changes to OIP itself, owned by this repository. (C) lists ideas the reviewer
explicitly parked for a later paper. Items marked **[verified]** were checked against the repo
on 2026-10-23; items marked **[open]** need a decision.

Reviewer's summary verdict: craft is strong (deterministic scoring, frozen replies, open data,
hashes, no hallucinated sources, honest claims). Main problems: no single thesis, DICOM
positioning missing, use case not described, ground-truth circularity stated too late, and the
manuscript is ~3× over the Scientific Reports length limit.

---

## A. Manuscript (Research_Automation session)

### A1. One thesis, one structure
- Proposed thesis (adopt verbatim as the backbone): *given the physical facts of an image, every
  VLM uses them, but almost none checks them against the pixels; metadata must therefore be
  checked tool-side and delivered with a stated certainty level, and OIP is a layer for that.*
- Demote the primary endpoint (full file vs. image only). It is trivial because the answer is in
  the text. Frame it as a manipulation check ("the information arrives"), not as the main result.
- Promote to the main results: (a) the flip check and the round-3 conflict trials (only Gemini and
  GPT compare text with the image, the rest follow the text), (b) adoption of injected wrong
  labels. State openly that these analyses are post hoc relative to the pre-registered plan.
- New order: export gap → OIP in one figure → results in three blocks: (1) facts are used,
  (2) facts are not checked against the pixels, (3) wrong labels are adopted → discussion:
  tool-side checks and the integration point.
- Fewer numbers in prose, more interpretation.

### A2. DICOM positioning (new paragraph in intro, one in discussion)
- OIP does not replace DICOM; it is derived from DICOM. DICOM is the original, OIP the layer for
  models.
- Why not raw DICOM tags: (a) frontier APIs do not accept DICOM; (b) tags are often wrong or
  missing (0 of 2,100 images carried an orientation tag; ~800 RSNA/SIIM images had implausible
  spacing); (c) raw tags are not reading instructions; (d) models do not check text, so metadata
  must be checked beforehand and carry a certainty level. The reviewer flags (d) as the strongest
  argument and currently under-used. **[verified]** the certainty vocabulary already exists in the
  schema (`assertion_level`: measured / computed / inferred / external / unknown; calibration
  `confidence`: high / medium / low / none; orientation cross-check result) and in `context.md`
  wording; the manuscript should present it as the core mechanism, not as a detail.
- Delimit from DICOM SR and IHE AIR: those carry findings (output side); OIP is the input side for
  models and excludes findings by design.
- Cite dicom-mcp in the manuscript body (currently only reference 22, not discussed) and position
  OIP as the checked layer above servers that hand raw DICOM to LLMs.

### A3. Use case paragraph (methods or a short "How a package is used" box)
- Concretely: one package per image as a directory or zip; it replaces the JPEG export; the images
  are inside; no viewer is needed (PNG, Markdown and JSON open anywhere).
- Practical catch: a directory cannot be uploaded to chat interfaces; the real path is an API or
  agent, or PNG plus `context.md` as two files.
- State the limits: one package = one image, no study level (PA + lateral = two packages), CT/MR
  only as a single slice.
- Honest boundary: for screenshots or JPEGs without a header (e.g. Radiopaedia) OIP recovers
  nothing; the benefit is small.
- Position against the adoption risk of new file formats in medicine: OIP is a protocol and schema
  (the checking and translation layer is the core, the zip is one transport); it can live inside
  DICOM (manifest as an SR-like object attached to the study); it can be the response format of an
  MCP or DICOMweb service; today concretely "export as OIP" instead of PNG in Orthanc, Weasis,
  3D Slicer, audience VLM researchers. **[verified]** the MCP server is a planned stub
  (PLAN Phase 5, `src/oip/mcp_server.py`), so the manuscript must not present it as available.
- Answer the future question: when models read DICOM natively, translation disappears but
  plausibility checks, certainty levels and tool-computed measurements remain, because tags are
  faulty and models do not verify text. Realistically models will read DICOM through tools, and
  OIP is then the tool's response format.
- Add the clinical hook: left/right confusion is a patient-safety issue (cite wrong-site literature).

### A4. Ground truth and circularity (move from Limitations to Methods, first mention)
- Truth for CTR and cardiac width is the project's own segmentation, and the same numbers appear
  in the text handed to the model. Say this early and plainly.
- Left-edge truth is "patient right" for 100/100 VinDr and 50/50 NIH and rests on the display
  convention only.
- No human image review was performed ("assistant's visual pass" is not a human read).
- The findings layer has no detection of its own: everything in it comes from the header,
  plausibility rules and a pre-trained segmentation network. State this explicitly.

### A5. Scientific Reports format
- Main text ≤ 4,500 words (Methods excluded); abstract ≤ 200 words, unstructured; title ≤ 20
  words (current title has 21); order Introduction → Results → Discussion → Methods.
- ≤ 8 display items in total (currently 13 tables + 6 figures). Keep roughly: the OIP figure, one
  main-results figure (three blocks), one conflict-trial figure or table, one wrong-label table,
  one model roster table; everything else to Supplementary.
- Move to Supplementary: scorer-bug paragraphs, the 16 amendments, cost/token/latency tables, bone
  scan details, the pilot table.
- Hotter-side task (n = 8): delete or reduce to one sentence.
- Scorer 0.3 becomes the main analysis; the old scorer is a sensitivity analysis. Everything is
  post hoc, which replaces half of the bug confession with one sentence.

### A6. Pre-empt the expected reviewer attacks (one paragraph each, Discussion or Methods)
1. "The answer is in the prompt, so the uplift is trivial": agree and reframe (A1).
2. Post-hoc analysis plan: list which analyses were pre-registered and which were added, with the
   amendment number.
3. One reply per cell in the paper run, repeats only for the conflict trials (3): report this,
   and if a repeat subset is run (B7), cite its run-to-run agreement.
4. Cloud models not pinned, two tags retired, drift (Gemini 94 → 90 → 88 %): report the model
   identifiers and dates per run and treat drift as a finding, not as noise.
5. "Wrong labels drawn with Python's string hash, not reproducible": **[verified]** the paper run
   (2026-09-06 harness) seeded the draw with the per-process `hash()`, so the draw itself is not
   re-derivable, but the drawn label is recorded for every frozen row (`misleading_label` in the
   row, `misled_summary.label_draw` in `results.json`), and the harness has used a sha256 seed of
   the package name since round 3 (commit a116105, 2026-09-30). Say exactly that.
6. No human validation: state it, and point to the planned expert-read subset (B8) if it exists
   by submission.
7. Automated Claude pipeline for the manuscript: keep the disclosure, add that all numbers derive
   from the frozen replies and deterministic scorer, and that the authors reviewed every claim.
8. Related work: add CXReasonBench (NeurIPS 2025; VLMs including CTR measurement).

### A7. README and manuscript must say the same thing
- The repo README still sells "models understand images, 99–100 %". Align with the thesis in A1
  (owned by B1 on the repo side).

---

## B. OIP itself (this repository)

### B1. README rewrite **[verified: lines 4, 143, 178–189 carry the old claim]**
- Replace "understand" wording and the 99–100 % headline with the A1 thesis: the package makes
  facts usable; the checks and certainty levels are the point; models do not verify text.
- Add the DICOM positioning (A2) and the use-case paragraph (A3) in short form.
- State the one-package-one-image limit and the screenshot/JPEG boundary.

### B2. Positioning in `docs/00-vision-and-scope.md` and `spec/oip-v0.1-draft.md`
- "Derived from DICOM, not a replacement"; "protocol and schema, the zip is one transport".
- Name the three integration points as roadmap: OIP-in-DICOM (manifest as attached object),
  MCP/DICOMweb response format, viewer/PACS export. Mark all three as not implemented.

### B3. Tool-side checks and certainty as the visible core of the manifest **[open]**
- Today the checks are spread over fields (orientation cross-check, calibration confidence,
  assertion levels, quality flags). Consider a top-level `verification` summary in `oip.json`
  (which checks ran, tool and version, result, what remains unverified) and a matching first
  block in `context.md`, so a consumer sees the certainty status before any fact. Requires an
  OEP and a schema minor version; do not change the frozen v0.2.1 packages.

### B4. Findings layer provenance
- Document in the spec that the regions and measurements layers contain no detection of their
  own: the sources are the header, plausibility rules and the named segmentation network
  (version recorded). Already true in the data; make it a stated rule.

### B5. Misleading-label draw
- Done in the harness (sha256 seed since a116105). Add one line to `bench/README` or the
  harness docstring that the paper run used the per-process hash and that the labels are
  recorded per row, so the bundle readme and the manuscript agree.

### B6. Model pinning in run metadata
- Record the exact model identifier, provider version string and run date per run in `run_meta`
  (check what is already there) so drift can be reported from the data.

### B7. Repeat subset (cheap defence for A6.3) **[open, cost]**
- At least 3 runs on a fixed subset (e.g. 20 packages × the main tasks) for the models that
  carry the main result. Ollama first; paid models only with explicit OK and a cost estimate.

### B8. Expert-read subset (defence for A6.6) **[open, already in PLAN as Tier 3]**
- A radiologist reads a fixed subset for the left-edge and CTR truths; report agreement.

### B9. MCP server
- Leave as planned work (Phase 5). Do not claim it in README or manuscript until it exists.

---

## C. Parked for a later paper (reviewer's list, not for this manuscript)
- Findings layer with several, possibly contradictory sources (CNN A, CNN B, MLLM, radiologist)
  with time, place and person stamps; only in `oip.json`, never by default in `context.md`
  (models adopt text blindly, which is the paper's own finding). Follow-up experiment: whom does
  the model follow when sources disagree (radiologist vs. majority vs. latest entry)?
- Study-level container (several projections, CT stacks) instead of single images.
- OIP-in-DICOM variant as a proof of concept.
- Export plugin for one viewer or PACS as a proof of concept.
- MSK adapter (hand/wrist): tool-computed angles (radial inclination, palmar tilt, ulnar variance).
- Repeats (≥ 3 runs) on a subset for run-to-run reliability (listed here by the reviewer, but see
  B7: it is cheap enough to help this paper).

## Suggested order
1. B1 + B2 (repo wording, half a day) so README and manuscript stop contradicting each other.
2. A1–A6 in the RA session (the rewrite is mostly cutting and reordering; the new text is A2, A3,
   A4 and the eight defence paragraphs).
3. B5, B6 (small harness/doc edits).
4. Decide B3 (schema change) and B7/B8 (cost, external person) with the co-author.
