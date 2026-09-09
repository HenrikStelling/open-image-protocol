# Paper outline — Open Image Protocol (working draft, 2026-09-09)

Status: outline. Target: arXiv preprint first, then a benchmark/resource track or an imaging-informatics journal (see §10).
Deliverable of Phase 3 (D-028). Everything marked **[pending]** is an experiment still to run; each maps to a PLAN.md item.

## 1. Title candidates
- *Open Image Protocol: self-describing medical image packages that let any vision-language model understand radiographs and scintigrams*
- *What a model needs to know about a medical image: a protocol and benchmark for zero-shot image understanding*
- *From DICOM to model-readable: a package format and benchmark for vision-language models in medical imaging*

## 2. Abstract (skeleton, ~200 words)
Problem: VLMs are fed 8-bit exports that silently drop units, scale, orientation and polarity; they measure poorly and follow text over pixels.
Method: OIP — a directory package with a schema-validated manifest, model-ready renders, deterministic measurements with provenance, and a fixed-template natural-language reference file; every fact carries an assertion level; measurements are computed by tools, never by the model; no diagnostic logic.
Evaluation: OIP-Bench — understanding tasks (orientation, scale, calibrated measurement, localisation, flip consistency), layer ablation, misleading-text test; N images from K datasets and two modalities; M open and frontier models.
Results: raw → package uplift of +X to +Y points on every model **[pending final N]**; the L0–L2 layer alone explains Z % of the effect **[pending]**; the v0.1 external-context wording increased adoption of wrong labels, the revised template reduces it from A % to B % **[pending frontier]**; measurement agreement with reference masks ICC = … **[pending CheXmask]**.
Conclusion: understanding is a data-format problem before it is a model problem; the protocol, converter, benchmark and packages are released.

## 3. Introduction
1. VLMs in medical imaging: strong reasoning, weak perception of quantity and side (MedVision; "Your other Left"); text dominates pixels (MC-CXR).
2. The silent conversion step: what today's pipelines discard between DICOM and the model (windowing, polarity, spacing, orientation) — with the Phase 2 numbers (RSNA/SIIM stale spacing, NIH anisotropic resize, VinDr stripped headers).
3. Lessons from protocols that made foreign systems model-readable: LSP (neutral abstraction), MCP (self-description via schema + prose, discovery), Model Hardware Standard (auto-generated reference file, safety in the driver).
4. Contributions: (a) the protocol and its design rules; (b) a reference implementation for DX/CR, NM, CT/MR single-frame; (c) OIP-Bench and the layer-ablation methodology; (d) empirical findings incl. a benchmark-driven spec revision; (e) open release.

## 4. Related work
DICOM SR TID 1500 / highdicom, IHE AIR, FHIR ImagingStudy, RSNA CDEs (outputs for clinical systems, not inputs for models) · NIfTI, OME-Zarr, BIDS (sidecar conventions) · llms.txt / model cards (prose for models) · MC-CXR, MedVision, MIRP, Set-of-Mark, grid-overlay results · medical VLMs (CXR-LLaVA, LLaVA-Rad, MAIRA-2, MedGemma) · dicom-mcp.

## 5. The Open Image Protocol
5.1 Design rules R1–R10 (from docs/01-reference-protocols/comparison-and-lessons.md).
5.2 Package layout, layers L0–L5, profiles, manifest schema (figure: package tree + manifest excerpt).
5.3 The reference file: fixed template, assertion levels, cautions before external content (template 0.2).
5.4 Renders: canonical polarity/window rules, annotated render (edge labels, scale bar, marks).
5.5 Measurements as tool outputs with guardrails (no mm without calibration; counts not comparable across windows).
5.6 Modality adapters: projection radiography, planar scintigraphy (count recovery from stretched PNGs), non-DICOM path.
5.7 Access paths: package, CLI, SDK, MCP server. Scope statement: observations and reference ranges, never interpretation (D-025).

## 6. Reference implementation and real-data conversion
Converter on 2,100 images from four sources, 0 failures; what the headers really contained (table from docs/reports/phase2-conversion-report.md); package overhead and reference-file token cost; anatomy adapter and measurement outputs; validation tiers.
**[pending]** CheXmask Tier-2 agreement (ICC, Bland–Altman) for CTR, cardiac and thoracic width; CXAS thoracic width as second source; expert-read subset (Tier 3).

## 7. OIP-Bench
7.1 Conditions: raw · L0–L2 reference file · full reference file · annotated render · misleading text (plain vs template).
7.2 Tasks: gating (left-edge side, scale availability, CTR, calibrated width, heart mark, mark side, flip consistency) and reported-only (modality, view, findings F1). No-leakage rule.
7.3 Scoring (answer extraction for chain-of-thought replies, abstentions), cost capture, cross-model spread.
7.4 Data: **[pending]** 100 VinDr (stratified) + 50 NIH + 60 bone-scan pairs; models: 8 open (Ollama) + Claude, GPT, Gemini **[pending]**.

## 8. Results
Table 1: understanding accuracy per model × condition (pilot: 8 models, +22…+45 pp; final **[pending]**).
Figure 2: layer ablation — L0–L2 vs full vs annotated, per task (which layer carries the effect) **[pending v2 runs]**.
Table 2: localisation and flip consistency (does the annotated render earn its place; do models check pixels against text) **[pending]**.
Figure 3: misleading text — adoption rate under plain note / v0.1 wording / revised template, per model (pilot numbers exist; the spec change is the story).
Table 3: measurement validation vs CheXmask and experts **[pending]**.
Figure 4: cost — tokens and latency per condition; cross-model spread shrinking with the package.
Modality generalisation: bone-scan tasks (counts semantics, orientation of posterior views) **[pending]**.

## 9. Discussion and limitations
- Why the effect is large: the failures were input failures. What the package does not fix (MedGemma's degenerate behaviours; models that adopt wrong labels regardless of wording → hence omit-by-default).
- Ground-truth caveats: CTR from lung masks (bias quantified in §6), left-edge truth on stripped headers backed by the 1,000-image laterality check.
- Ceiling effects at n = 20 → final N; single-centre datasets; 2D only; no diagnosis by design.
- Benchmark-driven protocol evolution (OEP process) as the maintenance model.

## 10. Venue and timeline
arXiv preprint when frontier numbers and the ablation exist (target: +2 weeks). Then: NeurIPS Datasets & Benchmarks / MIDL / MICCAI foundation-model workshop (benchmark framing) or Radiology: AI / J Imaging Inform Med (protocol framing). Authors: Henrik Stelling (lead), expert readers as clinical co-authors; AI assistance disclosed per venue policy.

## 11. Experiments checklist (maps to PLAN.md)
| # | Experiment | Data | Status |
|---|---|---|---|
| E1 | 8 open models, 20 images, 3 conditions | VinDr | done (pilot) |
| E2 | Harness v2 validation (ablation, localisation, flip) | VinDr 20, local models | running |
| E3 | Frontier models (Claude, GPT, Gemini) | VinDr 20 → 100 | needs keys |
| E4 | Scale to 100 VinDr + 50 NIH, stratified | on disk | after storage move |
| E5 | Bone-scan benchmark tasks | Zenodo 60 pairs | needs NM task set |
| E6 | CheXmask agreement | PhysioNet | needs approval |
| E7 | Expert reading (100 CXR, 50 bone scans) | readers available | needs reading set |
| E8 | CXAS thoracic width | local | to do |
