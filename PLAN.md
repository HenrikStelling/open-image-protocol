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

### Phase 3 — OIP-Bench: does it help models? (weeks 5–9)
- [x] Benchmark harness v0 (`bench/`): conditions {raw, ctx, annot}; tasks modality, view, left-edge side, scale availability, CTR, heart mm, findings F1 (VinDr); dry-run mode; results in `bench/results/` (ignored)
- [x] Misleading-context conditions (`misled_plain` vs `misled_oip`, adoption rate of a wrong label)
- [ ] Cross-model-variance aggregation in the report
- Cost estimate (dry run, 30 images): ≈ $11 Opus 5 + $5 GPT + $1 Gemini per full pass; 100 images ≈ $55 total. Anthropic id verified (`claude-opus-5`); GPT/Gemini ids must be confirmed before a paid run.
- [x] Ollama provider in the harness (D-026): pilot on Ollama cloud/local multimodal models, no keys needed
- [ ] Pilot runs on Ollama: fix harness/prompt issues, first protocol-effect numbers
  - Model roster (Ollama directory checked 2026-09-08). Cloud runs on Ollama's servers, so size is not limited by the Mac. Cloud vision-capable: kimi-k3 (most capable), mistral-large-3 (675b), qwen3.5 (cloud build), minimax-m3, gemma4 (12b/26b/31b), glm-5.3-flash (18b), kimi-k2.6. Retired: qwen3-vl:235b-cloud (410). Local medical (limited by 16 GB RAM / 14 GB disk): medgemma:4b only; the Gemma-3-based domain model and the privacy-preserving clinical arm.
  - Wave 1 (running): minimax-m3, glm-5.3-flash, gemma4:31b. Wave 2 (queued): kimi-k3, mistral-large-3:675b, qwen3.5. Wave 3: medgemma:4b local. Cloud concurrency limit: 3 models at a time.
- [ ] Later: export `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY` in the shell (not in the repo) and confirm GPT/Gemini model ids before paid runs
- [ ] API keys available (D-024); decide open-model hosting (MedGemma or CXR-LLaVA) **[needs you]**
- [ ] Self-check block failures fed back as protocol bugs
- [ ] Ablation: which `context.md` sections carry the uplift → trim default profile
- [ ] Tier-3 expert subset (~200 CXR): readers available (D-023); I prepare the reading set + instructions, you schedule the readers
Exit criteria (understanding tasks gate the release, D-015): statistically significant uplift on understanding tasks for every model; finding-level F1 reported but not gating; lower switch rate with labelled `external` text. Publish benchmark report → v0.2.

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
| v0.2.0 | real-data measurements + first benchmark report | end of Phase 3 |
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
