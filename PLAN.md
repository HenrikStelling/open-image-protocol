# OIP — living plan

Last updated: 2026-09-06 (owner answered all open questions; Phase 2 data downloading). Owner: Henrik.
Everything marked **[needs you]** is blocked on a decision or credential; see
also `docs/03-brainstorm/open-questions.md`.

## 0. Where we are

| Item | State |
|---|---|
| Reference protocols dissected (MCP, LSP, MHS) | done — `docs/01-reference-protocols/` |
| 13 research questions answered | done — `docs/02-research-questions/` |
| Vision, scope, design rules R1–R10 | done |
| Spec v0.1 draft + JSON Schema | done (draft) — `spec/` |
| Reference converter (DICOM → .oip) for DX/CR/CT/MR single-frame and NM multi-frame | v0 working |
| context.md generator, annotated renders, measurement guardrails | v0 working |
| Synthetic phantoms (DX MONOCHROME1, NM whole-body) + Tier-0 tests | working |
| Example packages | generated in `spec/examples/` |
| GitHub remote | done — https://github.com/HenrikStelling/open-image-protocol (private) |
| Kaggle credentials | done (2026-09-05) |
| PhysioNet | CITI training done 2026-09-08; credentialing application pending |
| Open questions | all 12 answered (D-014 to D-024) |
| Phase 2 data | VinDr 1,000-sample, RSNA, SIIM mirror (train + masks), NIH sample: all downloaded (~26 GB) |
| Phase 2 conversion | 2,100 real images converted, 0 failures; report in `docs/reports/` |
| Phase 2 measurements | 1,000 VinDr (regions, CTR, mm), 299 SIIM (pneumothorax ratios); CTR bias identified, Tier-2 pending CheXmask |

## 1. Principles (do not re-litigate without an OEP)
R1 neutral core (mm, orientation, units, provenance for every modality) · R2 self-describing twice (schema + prose) ·
R3 small verb set · R4 physics/safety in tools, not in the model · R5 assertion levels · R6 conformance profiles ·
R7 semver + deprecation + OEP process · R8 stateless packages · R9 ship the bundle · R10 measure uplift on a benchmark.

## 2. Phases

### Phase 1 — Spec v0.1 and reference implementation (now → 2 weeks)
Goal: a package any developer can generate and any model can read.
- [x] Package layout, manifest schema, context template, verb set (draft)
- [x] Converter: DX/CR (MONOCHROME1/2, VOI LUT, spacing selection, orientation), NM (frames, energy windows, tracer, counts)
- [x] Renders: canonical, annotated (edge labels, scale bar, marks), inverted (NM), thumbnail
- [x] Guardrails: no mm without spacing; schema validation before write
- [x] Non-DICOM adapter (PNG/JPG + CSV → `external` metadata) for NIH ChestX-ray14 (`src/oip/convert_image.py`)
- [ ] Burned-in text detector (OCR pass) to set `burned_in_text_checked = true`
- [x] `oip window/crop/overlay/measure` verbs in CLI + SDK (`src/oip/tools.py`, `anatomy.py`)
- [ ] Spec review pass with you; freeze v0.1.0 tag
Exit criteria: `make test` + `make validate` green; five example packages; spec text reviewed.

### Phase 2 — Real X-ray data and measurements (weeks 3–6)
- [ ] **[needs you]** accept competition rules on Kaggle for VinDr-CXR, RSNA Pneumonia, SIIM-ACR (one click each) → download VinDr-CXR, RSNA Pneumonia, SIIM-ACR, NIH (`scripts/fetch_data.py --phase 2`)
- [x] Convert 1,000 VinDr + 500 RSNA + 300 SIIM + 300 NIH; completeness/flag report (`docs/reports/phase2-conversion-report.md`). Finding: only VinDr has trustworthy absolute scale (82 %); RSNA/SIIM spacing is stale after resampling.
- [ ] Anatomy adapter: TorchXRayVision PSPNet (heart, lungs, 14 structures) first, CheXmask/CXAS for cross-checking → `derived/regions` (in progress)
- [x] Measurements: CTR, transverse cardiac diameter, thoracic width (VinDr, 1,000 images running); SIIM pneumothorax area / lung fraction from radiologist masks (`scripts/siim_measure.py`)
- [ ] VinDr lesion long axis (mm) from radiologist boxes
- [ ] Tier-1 plausibility rules in `quality.flags`; Tier-2 validation vs CheXmask (**[needs you]** PhysioNet access): ICC ≥ 0.95, Bland–Altman
- [x] Re-checked Kaggle for scintigraphy (D-022): small image-only sets only
Exit criteria: measurement report with ICC/LoA per spacing source; converter handles ≥ 5 vendors without manual fixes.

### Phase 3 — OIP-Bench: does it help models? (weeks 5–9) — deliverable: the paper (D-028, `docs/paper/outline.md`)
- [x] Benchmark harness v0 (`bench/`): conditions {raw, ctx, annot}; tasks modality, view, left-edge side, scale availability, CTR, heart mm, findings F1 (VinDr); dry-run mode; results in `bench/results/` (ignored)
- [x] Misleading-context conditions (`misled_plain` vs `misled_oip`, adoption rate of a wrong label)
- [x] Cross-model-variance aggregation in the report (std of gating accuracy across models per condition)
- [x] Harness v2 (2026-09-09, before the frontier run): layer ablation condition `ctx_l1` (L0–L2 only, no measurements) vs full `ctx`; misleading test routed through the shipped template; token/latency capture and cost table; abstention detection; new gating tasks that the file cannot answer verbatim — heart-mark and mark-side localisation (annotated render only) and a balanced flip-consistency test (mirrored render vs stated orientation); modality/view demoted from the gate. Validated on the two local models before any paid call.
- **Harness v2 validated on local models (2026-09-09):** layer ablation gemma4 e4b raw 61 % → L0–L2 only 78 % → full 100 %; MedGemma 57 → 67 → 87 %. About half of the uplift comes from geometry/orientation/units, the rest from computed measurements. Misleading test via the shipped template: gemma4 e4b 30 % adoption (vs 95 % plain note); MedGemma 0 % (degenerate). Cross-model spread raw 9 → ctx 5 pp. Localisation/flip tasks running (v3).
- [x] Storage: Kaggle cache (22 GB) and package store (15 GB) moved to /Volumes/Video Storage/oip with checksum verification; symlinks in place; 121 GB free internally
- [x] Paper benchmark set built (2026-09-09): 100 VinDr stratified (findings / cardiomegaly / spacing) + 50 NIH (non-DICOM path), no labels in packages, leak check 0/150; at ~/oip-bench/{vindr,nih}-paper. Sample cardiomegaly label prevalence 27 % (consistent with 34 % CTR > 0.5). Local-model baseline run queued; frontier run needs keys.
- **v3 complete (2026-09-09, 20 images, both local models):** heart-mark localisation gemma4 e4b 100 %, MedGemma 90 % (marks are readable); mark-side 0 % and 5 % (image side mapped to patient side despite printed R/L labels — a "Your other Left" failure; truth was unbalanced in this run, fixed for the paper set); flip consistency 50 % for both = chance ("agree" always: models do not verify text against pixels). Gating with the new tasks: gemma4 e4b raw 40 → L0–L2 59 → full 82 → annotated 82 %; MedGemma 37 → 51 → 78 → 75 %. The new tasks separate models that the old set put at the ceiling. Runs paused on request (battery); queue to resume: scintigraphy (40 pkgs) → paper-set baseline (150) → frontier.
- [x] Second thoracic-width source (CXAS) done — cross-tool agreement; left-edge truth footnoted with the 1,000-image laterality check (0 mismatches)
- [ ] **OEP-001**: External-section wording ablation (`misled_oip` vs `misled_oip_strong` vs omit-by-default), decide by adoption rate across ≥3 models (finding: gemma4 31B adopts a wrong label 100 % inside the External section vs 75 % as a plain note)
- Cost estimate (dry run, 30 images): ≈ $11 Opus 5 + $5 GPT + $1 Gemini per full pass; 100 images ≈ $55 total. Anthropic id verified (`claude-opus-5`); GPT/Gemini ids must be confirmed before a paid run.
- [x] Ollama provider in the harness (D-026): pilot on Ollama cloud/local multimodal models, no keys needed
- [ ] Pilot runs on Ollama: fix harness/prompt issues, first protocol-effect numbers
  - **PILOT COMPLETE (2026-09-09): 8 Ollama models (6 cloud, 2 local), 20 VinDr images, ~4,000 answers.** Understanding accuracy raw → +context.md: gemma4 31B 75→99, gemma4 e4b 63→99, glm-5.3-flash 58→88 (400-token budget run; 97 with annotated), kimi-k3 74→99, minimax-m3 74→100, mistral-large-3 55→100, qwen3.5 78→99, MedGemma 1.5 56→81 %. Findings F1 unchanged by the package (no label leakage). OEP-001 ablation decided D-027: external content omitted from context.md by default; strong wording when rendered. Report: `docs/reports/pilot-ollama-report.md`. Gate for v0.2 ("uplift on understanding tasks for every model, no F1 regression") is **met** on open models; frontier APIs (Claude/GPT/Gemini) remain to be run with the same harness.
  - **Wave 2 partial (2026-09-08, stopped by Pro rate limiting, HTTP 429, resuming one model at a time):** kimi-k3 74→99→99 %, mistral-large-3 675B 54→100 % (annot pending), qwen3.5 raw 81 % (rest pending). Eight models so far, every one lifts to 97–100 % with the reference file except MedGemma (81 %). glm-5.3-flash's context run was limited to a 400-token output budget (answers sometimes cut off inside its visible reasoning), so its 88 % ctx is a lower bound; later runs use 800.
  - **Wave 1 complete (2026-09-08, 5 models, 20 images, ~2,300 rows, 0 errors):** understanding accuracy raw → +context.md → +annotated: gemma4 31B 75→99→99 %, gemma4 e4b 63→99→99 %, glm-5.3-flash 51→97→99 %, minimax-m3 74→100→98 %, MedGemma 1.5 56→81→78 %. The protocol effect is +22 to +48 points and holds across sizes (4B–31B+), providers and local/cloud. Annotated render adds nothing measurable over context.md alone on these tasks (both near ceiling); its value must be tested on tasks that need localisation. Findings F1 unchanged by the package (0.55–0.65 everywhere) — correct, since packages carry no label information.
  - **Clean local results (2026-09-08, 20 images, no-leakage packages, 908 rows, 0 errors):** gemma4 e4b understanding 63 % raw → 99 % ctx → 99 % annot (left/right 50→100, scale 45→95, CTR 55→100, heart-mm 22→100; findings F1 flat ≈0.6 as expected). MedGemma 1.5 4B: 56 % → 81 % → 78 %; it misreads "view: PA" as lateral (80→15→0 %) and answers "No finding" to everything under misleading text — a degenerate behaviour, not resistance. Misleading label adopted by gemma4 e4b: 95 % plain vs 90 % in OIP external section (small model; protocol labelling barely helps at this size). Cloud wave 1 in progress shows the same shape (gemma4 31b 75→99 %, minimax-m3 74→100 %). Report: `docs/reports/pilot-ollama-report.md` (auto-generated by `bench/report.py`).
  - **First result (2026-09-08, gemma4 e4b local, contaminated run, kept for history):** understanding accuracy raw 61 % → +context.md 99 % → +annotated 99 %; left/right 70→100 %, scale awareness 35→95 %, CTR-within-5 % 45→100 %, heart mm-within-10 % 11→100 %. Findings row invalid in that run (label leak via box names, fixed; see bench/README). Misleading label adopted 100 % (plain note) vs 95 % (OIP external section) — small model, to be re-measured cleanly.
  - Model roster (Ollama directory checked 2026-09-08). Cloud runs on Ollama's servers, so size is not limited by the Mac. Cloud vision-capable: kimi-k3 (most capable), mistral-large-3 (675b), qwen3.5 (cloud build), minimax-m3, gemma4 (12b/26b/31b), glm-5.3-flash (18b), kimi-k2.6. Retired: qwen3-vl:235b-cloud (410). Local medical (limited by 16 GB RAM / 14 GB disk): medgemma:4b only; the Gemma-3-based domain model and the privacy-preserving clinical arm.
  - Wave 1: minimax-m3, glm-5.3-flash, gemma4:31b; wave 2: kimi-k3, mistral-large-3:675b, qwen3.5; wave 3: medgemma:4b + gemma4:e4b local (Metal workaround, see CONTRIBUTING).
  - 2026-09-08 status: first cloud attempts hit the Free tier's 1-request concurrency and (probably) exhausted the starter credits → every cloud call 502/timeout. **[needs you]** decide: Ollama Pro ($20/mo, 3 concurrent, $60 credits) or run one model at a time on Free once credits reset. Pilot packages live at ~/oip-bench/vindr (outside iCloud); run from ~/oip-work with ~/oip-venv.
- [ ] Later: export `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY` in the shell (not in the repo) and confirm GPT/Gemini model ids before paid runs
- [ ] API keys available (D-024); decide open-model hosting (MedGemma or CXR-LLaVA) **[needs you]**
- [ ] Self-check block failures fed back as protocol bugs
- [ ] Ablation: which `context.md` sections carry the uplift → trim default profile
- [ ] Tier-3 expert subset (~200 CXR): readers available (D-023); I prepare the reading set + instructions, you schedule the readers
Exit criteria (understanding tasks gate the release, D-015; paper experiments E1–E8 in `docs/paper/outline.md` §11): statistically significant uplift on understanding tasks for every model; finding-level F1 reported but not gating; lower switch rate with labelled `external` text. Publish benchmark report → v0.2.

### Phase 4 — Scintigraphy (weeks 8–12)
- [x] Download Zenodo Paraguay bone scans (582 × 16-bit PNG, 256×1024, ant/post pairs)
- [x] Non-DICOM NM adapter (PNG + hints; counts units; sqrt window; inverted render; count recovery from quantisation, 71 % success) — `scripts/bonescan_to_oip.py`
- [ ] Count-recovery robustness for the remaining 29 % (multi-start lattice fit)
- [ ] Skeletal region template (atlas or model trained on BS-80K if licence allows **[needs you]** to confirm terms)
- [ ] NM metrics: region counts, cps, anterior/posterior geometric mean, lesion/normal ratio, hot-spot count; BSI later
- [ ] NM rendering study: sqrt vs log vs percentile windows, inverted vs canonical — which do models read best (extend OIP-Bench with NM tasks)
- [ ] Try real NM-family DICOM headers via TCIA PET/CT to validate the radiopharmaceutical module mapping
Exit criteria: NM packages from real data validate; NM benchmark tasks added; counts guardrails tested.

### Phase 5 — Access paths (weeks 10–13)
- [ ] MCP server on the official Python SDK (replace `src/oip/mcp_server.py` stub): resources `oip://…`, tools = verb set, image + text + structuredContent results
- [ ] Python SDK polish, `pip install oip`
- [ ] CLI `oip serve`, `oip bench`
- [ ] Try it from Claude Desktop / Claude Code and one non-Anthropic host
Exit criteria: a model in an MCP host answers the self-check questions correctly on all examples.

### Phase 6 — Governance, interop, release (weeks 12–16)
Order per D-014: clinical-integration exports (SR/FHIR) before research-pipeline tooling; first outside contributors are validating experts (D-021).
- [ ] OEP process opened to outside contributors; CHANGELOG; deprecation policy text
- [ ] Conformance suite published; `oip validate --conformance`
- [ ] Exports: DICOM SR TID 1500 (via highdicom), FHIR ImagingStudy/Observation stub
- [ ] Opt-in aggregate telemetry from converters (missing-tag statistics)
- [ ] v1.0 candidate

### Phase 7 — 3D (CT, MRI) (after v1.0)
- Affine to patient space (NIfTI qform/sform semantics), multiscale chunked pixels (OME-Zarr), multi-planar canonical renders with slice position and window presets (HU), TotalSegmentator-derived regions; Kaggle RSNA CT/MRI competitions as data.

## 3. Milestones
| Tag | Content | Target |
|---|---|---|
| v0.1.0 | spec draft frozen, converter, phantoms, examples | end of Phase 1 |
| v0.2.0 | real-data measurements + first benchmark report (open-model pilot done 2026-09-09; frontier run pending) | end of Phase 3 |
| v0.3.0 | scintigraphy + MCP server | end of Phase 5 |
| v1.0.0 | governance, conformance, exports | end of Phase 6 |

## 4. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Context text misleads models more than it helps (MC-CXR effect) | assertion levels; benchmark switch-rate metric gates every release; keep `external` separate |
| No public NM DICOM | synthetic NM DICOM now; Zenodo/BS-80K images; TCIA PET/CT headers; seek a partner site later |
| Spacing wrong or absent in Kaggle data | explicit `spacing_source` + confidence; refusal rule; plausibility flags |
| Token cost of `context.md` | measured per profile; ablation trims defaults |
| Scope creep into diagnosis | out of scope in v0.x by decision; benchmark "understanding" tasks gate releases |
| Licence traps (BS-80K unclear, Kaggle competition rules) | `SOURCE.md` per dataset; never commit restricted data or packages derived from it |
| PHI leakage via burned-in text | OCR check in Phase 1; `burned_in_text_checked` flag; synthetic examples only in repo |

## 5. Immediate next actions
1. **[needs you]** PhysioNet credentialing for CheXmask: CITI course done (2026-09-08); upload the certificate in the credentialing application and sign the CheXmask DUA once approved.
2. **[needs you]** Accept the competition rules once on Kaggle (VinDr-CXR, RSNA Pneumonia, SIIM-ACR) so `scripts/fetch_data.py --phase 2` can download.
3. Me: non-DICOM adapter, OCR burned-in check, remaining verbs, then Phase 2 conversions as soon as data is available.
