# Decisions log (ADR / OEP style)

Format: **D-nnn — title** · status · date · context · decision · consequences.
Anything marked *proposed* is awaiting the user's review.

## D-001 — Name: Open Image Protocol (OIP) · accepted · 2026-09-04
Web search found no existing "Open Image Protocol"; OpenImageIO (VFX) and OCI
image-spec (containers) are the nearest name neighbours and are unrelated. Keep
the name; use `oip` as CLI/package name and `.oip` as package extension.

## D-002 — Licences · proposed · 2026-09-04
Spec + docs: CC-BY-4.0. Code: Apache-2.0 (patent grant matters for a protocol).
LICENSE file added for code; spec licence noted in `spec/README.md`.

## D-003 — Package = directory with JSON sidecar (BIDS-style), zip optional · accepted
Rationale: inspectable with any tool, git-friendly, works offline, matches
OME-Zarr/BIDS practice. A single-file binary container was rejected for v0.

## D-004 — Manifest is JSON validated by JSON Schema (draft 2020-12) · accepted
Same choice as MCP tool schemas; every field carries a `description` written for
models as well as humans.

## D-005 — Do not resample, rotate or flip pixels in v0.1 · accepted
Keep source pixel coordinates valid; put orientation cues in the annotated
render and in `geometry.orientation`. Revisit when 3D arrives.

## D-006 — Canonical polarity: attenuation/counts high = bright · accepted
Rationale: MONOCHROME2 is the DICOM default; models see mostly bright-bone
CXRs. Bone scans are often shown inverted in practice → provide `inverted`
render variant for NM.

## D-007 — Assertion levels on every fact · accepted
`measured | computed | inferred | external | unknown`. Driven by MC-CXR evidence.

## D-008 — Measurements are computed by tools, never by the model · accepted
Tools refuse mm without calibrated spacing (MHS "limits in the driver").

## D-009 — Versioning: semver from 0.1.0; deprecation ≥ 2 minor versions · accepted

## D-010 — Verb set: describe, locate, measure, window, crop, overlay, validate · proposed
Small, read-only. `write`-type operations are out of scope.

## D-011 — Reference data strategy · accepted
X-ray on Kaggle (VinDr, RSNA, NIH); scintigraphy from Zenodo + synthetic NM
DICOM; request PhysioNet/AIMI access for masks/reports.

## D-012 — First MCP server is read-only and local (stdio) · proposed
Resources: `oip://<package>/manifest`, `/context`, `/renders/canonical`;
tools mirror the verb set. Remote (HTTP + OAuth) later.

## D-013 — 3D extension deferred; will align with NIfTI affine + OME-Zarr multiscale · proposed

---
## Decisions from the owner's review of the open questions (2026-09-06)

## D-014 — Target consumers, in order: general assistants (a) → clinical integrators (c) → research pipelines (b) · accepted
Consequence: MCP server and `context.md` quality come first; SR/FHIR export (clinical integration) is pulled forward ahead of research-pipeline conveniences (bulk conversion, dataset tooling).

## D-015 — OIP is an understanding protocol, not a diagnostic one · accepted
OIP lets a model understand and analyse an image. It never produces a diagnosis. The benchmark measures both understanding tasks and finding-level tasks, but **only understanding tasks gate releases**.

## D-016 — Scintigraphy priority: bone scans → thyroid → renal → cardiac · accepted

## D-017 — Human free-text notes allowed in `context.md`, marked `external` · accepted

## D-018 — Full-resolution lossless pixels are included in every package · accepted

## D-019 — Subject keeps 5-year age band and sex; finer detail opt-in · accepted

## D-020 — Layers inside the manifest, profiles as named layer sets · accepted (default confirmed)

## D-021 — Governance: first outside contributors are domain experts who validate · accepted
Open the OEP process to outside contributors after v0.2, or earlier if the first benchmark fails its gate. Expert readers are available (D-023).

## D-022 — Kaggle re-checked for scintigraphy (2026-09-06) · accepted
Small image-only sets exist (thyroid scan set under CDLA-Permissive-1.0; two DaTscan sets; one bone-scan set with unknown licence; one SPECT MPI set). None ship DICOM headers. Strategy unchanged: Zenodo Paraguay + synthetic NM DICOM for the converter; Kaggle sets added to Phase 4 for render/benchmark diversity.

## D-023 — Expert readers are available · accepted
Tier-3 validation (~200 CXR, ~50 bone scans, two readers) is scheduled in Phase 3 rather than deferred.

## D-024 — Model API keys are available · accepted
Phase 3 benchmark is unblocked; cost estimate to be confirmed before the first full run.

## D-025 — Diagnosis is emergent, not preconfigured; OIP carries observations, optionally reference ranges, never interpretations · accepted · 2026-09-06
Owner's question: does a format that lets a model understand an image (entity, anatomy, sizes, intensity values such as HU or uptake) need built-in diagnostic logic, or can diagnosis follow from better understanding? Decision: the latter, with a three-tier boundary.
1. **Observations (in scope, mandatory):** what the image is, geometry, intensity semantics, regions, and measurements with provenance and assertion level. This includes *value* measurements per region (mean/min/max HU, count density, relative attenuation) — added as `derived.regions[].stats`.
2. **Reference ranges (in scope, optional, `external`):** cited normal ranges next to a measurement (e.g. "adult CTR normal < 0.50", "liver 40–60 HU"). Knowledge, not judgement; lets a model compare without OIP deciding anything.
3. **Interpretation (out of scope):** findings, impressions, diagnoses. Produced by the consuming model or a downstream tool, never by the package. Detector outputs (boxes, "nodule") may be carried as `inferred` observations with the producing tool named, but OIP defines no diagnostic vocabulary and no rules.
Rationale: (a) frontier models already hold the clinical reasoning (CTR threshold, HU ranges, uptake patterns); what they lack is trustworthy inputs — MedVision, MC-CXR and our own runs show the failure is measurement and grounding, not reasoning. (b) Diagnostic logic inside a format freezes today's medicine into a spec and turns a data standard into a regulated device. (c) It keeps the benchmark honest: OIP-Bench measures whether findings-level accuracy rises *as a consequence* of understanding tasks improving, with zero diagnostic code in the package — that is the test of the hypothesis. Consistent with D-015.

## D-026 — Benchmark pilot on Ollama (cloud + local open models); frontier APIs after the harness is stable · accepted · 2026-09-08
While the harness, prompts and packages are still changing, run OIP-Bench against Ollama models: cloud multimodal tags
(glm-5.3-flash, gemma4 12b/26b/31b, minimax-m3, kimi-k2.6, kimi-k3, mistral-large-3) through the signed-in local daemon
(plan allowance instead of per-token billing; no API keys), and local models (gemma4 e4b) for the privacy-preserving clinical
deployment story (D-014: clinical integrators are consumer #2). Claude, GPT and Gemini are added once the harness is stable
and the pilot has shown the protocol effect, so that paid runs measure the protocol, not harness bugs. Consequence: the
benchmark's success criterion "uplift for every model" now spans open and frontier models, which is the stronger claim anyway.

## OEP-001 / D-027 — The External-context section makes misleading labels *more* credible; wording must change · proposed · 2026-09-08
Evidence (OIP-Bench pilot, 20 VinDr images, clean packages): gemma4 31B adopted a wrong finding label 75 % of the time when given
as a bare "prior report note" but **100 %** when placed in context.md's External section with the tag "[external — verify against
the pixels]". gemma4 e4b: 95 % vs 90 %. MedGemma 1.5: 90 % vs 0 %, but only because it answered "No finding" to everything
(degenerate, not resistance). Conclusion: a labelled section inside an authoritative reference file lends credibility to
whatever it contains; the assertion tag alone is not a safeguard (consistent with MC-CXR, where text context was adopted
74.6 % of the time). Proposal, to be measured by adoption rate before adoption into the spec:
1. Default profile omits external labels/report text from context.md entirely; they live in `oip.json.external` and are
   surfaced only on explicit request (`describe --with-external`).
2. When included, the wording states base rates and forbids echoing: "UNVERIFIED label from a dataset file; such labels are
   wrong in a substantial fraction of cases; report only what the pixels show and state explicitly if the label is not
   supported." (`misled_oip_strong` condition in bench/run.py).
3. Section order: cautions before external content, not after.
Gate: accept whichever variant yields the lowest adoption rate without lowering understanding accuracy, across ≥ 3 models.

First ablation (2026-09-08, local models): the strong wording cut gemma4 e4b's adoption from 90 % to 10 % and raised F1 under misleading text from 0.10 to 0.67 — but the model now answers "No finding" in 15/20 cases (over-suppression risk to be checked against findings F1 in the non-misled conditions). MedGemma 1.5 stays degenerate ("No finding" always). Cloud models queued for the same condition.

## D-027 — OEP-001 accepted: external content is omitted from context.md by default; when rendered, cautions precede it and it carries unverified-label wording · accepted · 2026-09-09
Cloud ablation (6 models, 20 images, wrong label injected): adoption under v0.1 wording → OEP-001 wording: gemma4 31B 100→10 %,
minimax-m3 90→0 %, qwen3.5 60→0 %, gemma4 e4b 90→10 %, kimi-k3 90→40 %, glm-5.3-flash 95→60 %, mistral-large-3 100→80 %
(MedGemma degenerate both ways). Findings F1 under misleading text rose for 6/8 models; the "No finding" rate stayed near
the true rate (12/20), so no general over-suppression. Because two capable models still adopt ≥ 60 %, wording alone is not a
sufficient safeguard: the default reference file now renders no external labels or report text at all (they remain in
`oip.json.external`; `oip describe --with-external` renders them with the strong wording, cautions first). Template 0.2.
Consumers that need prior-report text must request it explicitly and inherit the wording.

## D-028 — The Phase 3 deliverable is a paper (arXiv preprint, then a benchmark/resource venue) · accepted · 2026-09-09
The pilot is preprint-grade evidence for a protocol but not paper-grade evaluation (n = 20, one dataset, open models only,
partly self-referential ground truth). Remaining Phase 3 work is organised around the paper's figures: layer ablation,
localisation/flip tasks, misleading-text before/after, measurement validation (CheXmask + experts), cost and cross-model
spread, frontier models, 150 images across two sources and two modalities. Outline: docs/paper/outline.md.

## OEP-003 / OEP-004 — Verification cues and a pixel-based self-check: does the reference file make models look? · proposed · 2026-09-26
Evidence (paper run, 11 models, VinDr-100 and NIH-50): with the full reference file every capable model answers the gating
questions at 99–100 %, but the file states those answers, so the result shows use of facts the pixels do not carry, not a
check of those facts against the image. On the one task that requires the check, the flip check (image mirrored while the
file states normal orientation; two items per image so "always agree" scores 50 %), 8 of 11 models sit at chance; Gemini
99 %, GPT 88–97 %, glm-5.3-flash 80–86 %. The shipped template gives no pixel cue a reader could check the orientation
against, and nothing in the file or the prompt asks for a check.
Proposal, measured before adoption (template 0.3 draft, `build_context(..., verification_cues=True)`):
1. **OEP-004, cues.** Every [inferred] or [external] statement about orientation, view and scale carries a pixel cue with a
   side fixed by anatomy (frontal chest: cardiac apex and aortic knob toward the edge labelled L, gastric bubble on the same
   side, right hemidiaphragm higher; scintigraphy: which structures are sharp in a posterior vs anterior view, and the honest
   note that a normal skeleton does not give left from right), followed by "if the image disagrees, report it instead of
   repeating the stated orientation". A new "How to use this file" section says that [inferred]/[external] statements are
   hypotheses to verify. The self-check gains item 5, answerable only from the image (which image side is the cardiac apex;
   does it agree with item 1), with no arrow answer.
2. **OEP-003, mirror item.** Self-check item 6 asks whether the printed edge labels on the annotated render agree with the
   stated orientation.
3. **Instruction arm.** The same check requested by one added sentence in the system prompt instead of in the file, to
   locate where the remedy belongs.
Measurement (2026-09-26, `bench/run.py`, conditions `ctx_ctl`, `ctx_cue`, `ctx_instr`, `ctx_cue_instr`; flip_check + left_edge;
VinDr-100; claude-sonnet-5, gpt-5.6-terra, gemini-3.8-flash; the control has its own condition name so the latest-run rule
never lets it replace the paper's `ctx` cells; every row now carries the harness commit and scorer version). Gate: adopt the
cues into template 0.3 if the flip check rises by ≥ 20 pp against the same-day control for at least two of the three
models without lowering left-edge accuracy; if only the instruction arm moves, the remedy is the sentence, which the file
can carry in "How to use this file"; if nothing moves, the models cannot do the check on these images, and the tool-side
check (`oip check`, planned) is the only guarantee. Cost estimate ≈ $22 list price (Claude cached).

## D-029 — `oip check`: a pixel-side orientation check in the tools, two-pass to cancel the segmentation model's prior · accepted (tool), draft in spec · 2026-09-26
Why: the only way to guarantee that a stated orientation was checked against the pixels is to have the tools do it (R4); a model
may or may not. Design: the unsided heart (and aortic-arch) mask's column centroid relative to the thoracic midline, compared with
the edge labelled L; no use of the model's left/right class labels (which inherit the display convention, review Q3).
Evidence on 100 VinDr packages, normal and mirrored (`docs/reports/orientation-pixel-check.md`): pure geometry flips 98/98; a
single re-segmentation of the mirrored render catches only 71/100 (24 indeterminate, 5 wrong) because TorchXRayVision's PSPNet
places the heart partly where hearts usually are (offset median +0.079 as shipped, −0.053 mirrored). Segmenting the image and
its mirror and halving the difference cancels that prior: 94/100 decided, 0 wrong at every threshold, 6 indeterminate (|s| < 2 %).
Decision: two-pass is the default; verdicts go to `quality.checks[]` with the evidence and to context.md next to the orientation
line; a failure sets `orientation_pixel_inconsistent` and a caution. The check reports, it never rewrites the stated orientation.
Spec: verb table (§7) and schema extended, marked draft until v0.2. Open: no pixel check is defined for scintigraphy yet.

**Measured 2026-09-26 (Gemini and GPT complete, 1,200 rows each; Claude control and cue arms, then paused on a billing stop, to be resumed).** Flip check / mirrored items / left-edge side on VinDr-100:
gemini-3.8-flash: control 99 % (98/100) · cues 98 % (96/100) · instruction 98 % (95/99) · both 99 % (98/100); left edge 100 % in every arm.
gpt-5.6-terra: control 92 % (84/100) · cues 92 % (84/100) · instruction 93 % (86/99) · both 90 % (81/100); left edge 100 % in every arm.
claude-sonnet-5: control 50 % (1/100) · cues 49 % (0/83); left edge 95 → 100 %.
Outcome: **no arm moves any model beyond noise.** The two models that check the image against the file do so with the shipped
file already; the one that does not check keeps answering "agree" to every mirrored image with the cardiac cue named in the
file, a "how to use this file" section, a pixel-only self-check item, and (for the other two) a system-prompt sentence asking
for the check. OEP-004's gate (+20 pp for ≥ 2 of 3 models) is failed on the frontier models; OEP-003's mirror item cannot be
assessed here (the annotated render was not part of the flip check). Consequences: (1) the cue-bearing template stays behind
its flag; (2) the same four arms run on the eight Ollama models before either OEP is closed (cost rule: Ollama first);
(3) the guarantee is the tool-side check, D-029, not the prose; (4) the paper's discussion can now say that neither a named
cue, a usage instruction nor a self-check item changes whether a frontier model verifies text against pixels. Cost: Gemini
$2.55, GPT $11.12, Claude $5.06 so far (list prices from the usage fields).
