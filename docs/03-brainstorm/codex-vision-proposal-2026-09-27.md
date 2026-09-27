# Codex proposal — improving the vision side of OIP and a vision-only benchmark track (2026-09-27)

Consult output of the OpenAI Codex CLI (codex-cli 0.146.0, reasoning medium, read-only, session 01a0e18e-2b0c-76e1-a4f7-1830581191b7), prompted from the OIP session with the benchmark findings of 2026-09-23 and the file map. Verbatim, tool calls removed. Claude's assessment follows in the chat transcript and in PLAN.md Phase 3b.

---

I’ll inspect only the repository paths you named (and repository metadata/instructions if present), then tie every proposal to the actual APIs and benchmark schema. I’ll use web search only for primary papers needed to support the literature claims.
The code confirms the core confound: `annot` always includes the full `context.md`, and region marks are bounding boxes whose numbers are explicitly decoded in that file. The runner also downsizes every image to a 1568-pixel long side, which can make the current margin labels and scale bar too small for the vision encoder even though they remain legible to a human.
I’m separating two claims that are easy to blur: “a technique helped general VLM grounding in a paper” versus “it should help OIP’s frozen medical-image models.” The latter will be labeled as a hypothesis until this benchmark demonstrates it; most published visual-prompting work does not establish medical laterality or quantitative calibration.
# Solution proposal

The first correction is methodological: the current benchmark has not tested whether `annotated.png` improves flip detection.

`flip_check` is restricted to `ctx_l1` and `ctx` in [bench/tasks.py](/Users/pal/oip-work/bench/tasks.py:65), and [bench/run.py](/Users/pal/oip-work/bench/run.py:105) shows those conditions use the canonical image. The mirrored artifact is also made from `canonical.png`, without edge labels. Therefore:

- The benchmark shows that most models do not infer mirroring from anatomy when text states an orientation.
- It does not show that printed R/L labels fail to help flip detection.
- The annotated-render comparison is invalid for the primary gating tasks because the full file already states their answers.
- `mark_side` is text-leaked, as stated.

That gap should be fixed before changing the normative render.

## 1. Diagnosis

### Why the current render is unlikely to help much

The current annotated render has four structural problems.

1. **Annotations are below effective encoder resolution.**

   [render.py](/Users/pal/oip-work/src/oip/render.py:78) chooses a margin of only 6% of the source long side and a main font roughly half that size. Then [run.py](/Users/pal/oip-work/bench/run.py:128) downsizes every input to a maximum side of 1568 pixels.

   A 3000-pixel radiograph can therefore end up with edge letters roughly 10–20 effective pixels high. They are far smaller than they look when the original PNG is opened locally.

2. **The useful material is placed in the margin.**

   Vision encoders allocate most tokens to the image as a whole. Small peripheral text competes with a large, visually complex radiograph. The labels are not anchored to a large local cue such as an enlarged source marker or the cardiac apex.

3. **The marks are bounding boxes, not perceptual regions.**

   `annotated()` draws the full `bbox_px` and puts a number in its corner. Large overlapping anatomy boxes are a weak form of set-of-mark prompting: they obscure pixels, do not follow the structure, and may put the number far from the visually diagnostic part of the region.

4. **The benchmark encourages text-first behavior.**

   `annot` supplies the full reference file. Since that file contains the scored value, the rational shortcut is to read it. The render has no opportunity to demonstrate incremental value.

There are also task-specific problems:

- A naked chest radiograph contains no metric calibration. “Scale available?” is not a vision question unless the image visibly contains a calibrated ruler.
- Patient laterality is not identical to image-left/image-right. Small models often learn the wrong mapping.
- Mirroring cannot always be established from anatomy. Dextrocardia, rotation, obscured cardiac borders, lateral views, and symmetric bone scans must be excluded or marked indeterminate.
- The existing PSPNet masks have a positional prior. `PLAN.md` already reports that re-segmenting mirrors produced only 71/100 detections until the two-pass correction was introduced.
- CTR and cardiac-width “truth” are pipeline outputs from unvalidated inferred masks. A vision-only CTR task can test whether a model reads the overlay, but not whether the clinical measurement is correct.

### Mechanisms worth testing

**Set-of-mark prompting.** Yang et al., *Set-of-Mark Prompting Unleashes Extraordinary Visual Grounding in GPT-4V*, found that numbered masks and marks improved referring and grounding tasks. That supports contour-following marks and external label disks, but not the claim that marks fix medical laterality or measurement. [Paper](https://arxiv.org/abs/2310.11441)

**Coordinate scaffolds and grids.** Lei et al., *Scaffolding Coordinates to Promote Vision-Language Coordination*, report improvements from dot-matrix coordinates over textual chain of thought. This supports a sparse labeled grid for localization, not a dense metric grid over the entire radiograph. [Paper](https://arxiv.org/abs/2402.12058)

**Cropping and zooming.** Wu and Xie’s *V\** shows that guided visual search and selected high-resolution crops help models recover details lost in global encodings. OIP can approximate this with deterministic inset crops even without an agent loop. [Paper](https://arxiv.org/abs/2312.14135)

**Visual chain of thought.** *Visual Sketchpad* improved spatial and visual reasoning by letting models draw, crop, and use specialist tools. Its important mechanism is an iterative tool loop, not the phrase “look carefully.” A static OIP sheet can imitate one or two steps, but should not be described as equivalent. [Paper](https://arxiv.org/abs/2406.09403)

**Higher resolution and visual token allocation.** MM1’s ablations found that image resolution and image-token count materially affect multimodal performance. OIP currently hands resolution control to provider-specific resizing. [Paper](https://arxiv.org/abs/2403.09611)

**Multi-image comparison.** It may help with reference examples and mirror pairs, but it is not reliably beneficial. MIBench found substantial multi-image weaknesses in current models. A single labeled contact sheet should therefore be tested against separate image attachments. [Paper](https://arxiv.org/abs/2407.15272)

### Mechanisms not supported by current evidence

- More textual reminders, anatomical prose, and self-check questions: the OEP-004 result in `PLAN.md` is already negative.
- Textual chain of thought without changing visual input: it cannot restore pixels discarded by the encoder.
- Nearest-neighbor enlargement by itself: it makes existing pixels bigger but adds no detail.
- Dense grids over anatomy: they can occlude edges and introduce false line structure.
- Set-of-mark alone: it improves reference selection in some settings, but does not teach patient-coordinate conventions.
- Arbitrarily adding more images: multi-image reasoning can regress.
- Treating a polarity-inverted image as intrinsically “wrong”: for scintigraphy both hot-bright and conventional hot-dark displays can be legitimate if explicitly identified.

## 2. Ranked render and overlay proposals

Do not replace `canonical.png`. Add optional derived renders, benchmark them, and promote only successful variants.

### 1. Encoder-safe inspection sheet

**What the model sees**

A fixed 1536×1536 sheet:

- Large whole image occupying about 70% of the pixels.
- High-contrast R and L badges at least 64 pixels high after final resizing.
- A 256–384 pixel inset of any detected burned-in side marker.
- A 256–384 pixel cardiac-apex/aortic-knob inset for frontal CXR.
- A calibrated ruler with 10 mm minor ticks and 50 mm major ticks.
- For missing spacing, a large crossed ruler symbol rather than a sentence in tiny type.
- No region-name legend.

**Code**

- Add `inspection_sheet()` and reusable `draw_edge_badges()`, `draw_metric_ruler()`, and `make_inset()` functions to [render.py](/Users/pal/oip-work/src/oip/render.py).
- Add `inspection(pkg, features=..., name=...)` to [tools.py](/Users/pal/oip-work/src/oip/tools.py).
- Do not use the existing margin-size formula. Render to a target presentation canvas with minimum post-resize sizes.
- Prefer bilinear/Lanczos for visual crops; retain nearest-neighbor only for masks.

**Spec/schema**

Add optional purpose `inspection` and structured panel metadata:

```json
{
  "purpose": "inspection",
  "panels": [
    {
      "id": "whole",
      "source": "renders/canonical.png",
      "source_bbox_px": [0, 0, 2999, 2999],
      "canvas_bbox_px": [0, 0, 1099, 1099]
    }
  ],
  "minimum_annotation_px": 48
}
```

The current render schema has `additionalProperties: false`, so [the schema](/Users/pal/oip-work/spec/schemas/oip-manifest.schema.json:268) must change with the spec.

**Hypothesis**

Current failure partly results from visual-token allocation and unreadably small anchors. A fixed-size sheet should improve marker OCR, scale reading, and mark localization.

### 2. Orientation self-check sheet

**What the model sees**

A single labeled composite:

- Panel A: the complete target.
- Panel B: enlarged left/right source-marker areas when present.
- Panel C: an enlarged cardiac-apex/aortic-knob crop with a vertical image-midline.
- Panel D: a generic reference tile showing a normal frontal thorax, with the cardiac apex toward the patient-L edge.

No textual verdict such as “orientation consistent” appears. The model must compare the target cue with the reference tile.

A second experimental variant shows the target and its horizontal mirror side by side as A/B and asks which matches the reference tile. This is easier than unconstrained “is it mirrored?” and directly tests visual comparison.

**Code**

- Add `orientation_sheet(canon, cue_bbox, edge_labels, include_mirror_pair=False)`.
- Use masks only to choose the crop and midline, not to draw the answer.
- If the two-pass orientation check is indeterminate, do not generate the anatomy-cue task.

**Spec**

Add optional purpose `orientation_check`; record whether the reference tile is generic, the crop source coordinates, and whether a mirror was included.

**Hypothesis**

The reference tile acts as a visual in-context example. It may overcome a language-dominant response policy by placing both the rule and the evidence in the vision stream.

This is the required visual self-check. It is deliberately different from the failed textual self-check.

### 3. Contour SoM plus caliper overlay

**What the model sees**

- Thin heart and thorax contours in distinct high-contrast colors.
- Numbered disks outside the anatomy with leader lines.
- A horizontal cardiac-width caliper and thoracic-width caliper.
- No numeric CTR or width.
- Optional metric ruler below the image.

Do not draw region-name text. Do not use bounding rectangles as the default.

**Code**

- Replace or supplement the `bbox_px` loop in `annotated()` with mask-contour drawing.
- Add an overlay mode:

```python
overlay(
    pkg,
    regions=["heart", "lung_left", "lung_right"],
    style="contour",
    calipers=["heart_width", "thorax_width"],
    reveal_labels=False,
)
```

- Compute caliper endpoints from masks and store them as pixel coordinates.
- Use neutral marks such as A, B, C. The association to `lung_left` must remain out of the image-only prompt.

**Hypothesis**

SoM should improve mark-to-region grounding. Calipers should convert CTR from an unconstrained anatomy-estimation problem into a visual ratio-reading problem.

### 4. True metric ruler and sparse coordinate scaffold

The current scale bar is a single line labeled “50 mm.” That tests OCR more than calibrated spatial reasoning.

**What the model sees**

- A ruler spanning a substantial fraction of the image width.
- Alternating 10 mm ticks, 50 mm labels, and a zero origin.
- A sparse 4×4 or 6×6 alphanumeric grid when localization is requested.
- Grid and ruler outside the anatomy where possible.

**Code**

Extend `overlay()` with:

```python
ruler_mm=True
grid={"rows": 4, "cols": 4, "labels": True}
```

Keep `grid_mm` for geometric overlays, but do not use it as the primary VLM scaffold.

**Hypothesis**

Large repeated ticks let the model compare a target length against visible units. The sparse grid supplies stable visual anchors for crop registration.

### 5. Crop pyramid / focus tiles

**What the model sees**

A whole image plus 2–4 labeled high-resolution tiles:

- Source marker or burned-in text.
- Cardiac silhouette.
- Selected numbered region.
- Asymmetric NM uptake region.

Each tile includes a miniature locator map showing its location in the whole image.

**Code**

- Reuse `crop()`, but add an antialiased presentation upscale.
- Add `crop_sheet(pkg, crops, include_locator=True)`.
- Record the exact `source_bbox_px` and scale for each tile.

**Hypothesis**

Fine detail currently lost during provider resizing becomes a meaningful share of the vision tokens. The locator map prevents the crop from losing side and whole-image context.

### 6. Window and polarity contact sheet

**What the model sees**

For radiographs:

- Canonical.
- CLAHE or local-contrast variant.
- Soft-tissue-oriented window where meaningful.

For NM:

- Hot-bright square-root.
- Hot-dark square-root.
- Log-scaled hot-bright.
- Optional perceptually uniform false-color variant as an experimental arm only.

Every panel is visibly labeled A/B/C; labels describe the transform, not the answer.

**Code**

- Generalize `window()` beyond HU-only presets for named, recorded transforms.
- Add `contact_sheet()` to `render.py`.
- Store percentile/window parameters, polarity and panel ordering.
- Never describe CLAHE or false color as quantitative; count comparisons must use lossless pixels.

**Hypothesis**

NM hot-side failures may be caused by poor dynamic-range allocation. Multiple monotonic views could expose subtle asymmetry. False color is speculative and should not become normative without clear gains.

## 3. Vision-only benchmark track

The system prompt should contain no package facts:

> Answer using only the attached image or images. Return exactly one of the allowed answers.

No `context.md`, manifest excerpt, title, filenames, package path, metadata, or region list is shown.

| Task | Prompt and images | Truth | Target n and balance | Scoring | Supply |
|---|---|---|---|---|---|
| **Anatomical mirror detection** | “Is this frontal chest image normally displayed or horizontally mirrored? Answer `normal` or `mirrored`.” Canonical or mirrored render. | Applied transform; include only frontal cases where the two-pass orientation check is decisive. | 400 unique CXR, both transforms; 50/50. Chance 50%. | Exact token. Cluster by source image. | Expand VinDr packages beyond the current 100; NIH supplemental. |
| **Visual-reference orientation** | Same question, but show the orientation self-check sheet. | Applied transform. | Same 400 paired items. | Exact token; paired against canonical. | Same. |
| **Printed-marker reading** | “What letter is printed in the highlighted inset? `L`, `R`, or `none`.” Show whole image plus marker inset. | OCR/manual audit of actual burned-in marker, not manifest orientation. | At least 200 marker-positive plus 100 marker-negative; balance L/R. Chance 33%. | Exact `L/R/none`. | VinDr if source markers are present; otherwise do not pretend generated badges test source-marker perception. |
| **Generated edge-anchor reading** | “Which patient side is marked at the image’s left edge?” Inspection sheet only. | Generated badge. | 200, balanced L/R by controlled badge swap. Chance 50%. | Exact patient side. | Any package. This is an overlay legibility control, not anatomical perception. |
| **Ruler decoding** | “How many millimetres does the red segment span? Choose `30`, `50`, `70`, or `90`.” Inspection sheet with ruler and synthetic segment. | Render geometry × pixel spacing. | 320 items, four values balanced. Chance 25%. | Exact option. | Calibrated VinDr packages. |
| **Relative physical size** | “Which segment is longer in millimetres, A or B?” Same apparent pixel length under different displayed scales, or differing pixel lengths under the same ruler. | Generator parameters. | 320, 50/50, include anti-shortcut counterbalancing. | Exact A/B. | Calibrated VinDr; synthetic overlay geometry. |
| **CTR without overlay** | Numeric CTR from canonical only. | PSPNet-derived value, explicitly labeled pipeline-readout truth. | 400 CXR. | Absolute error ≤0.05 plus MAE. | VinDr/NIH. |
| **CTR with contours** | Same prompt, contour-only sheet. | Same tool output. | Same images, paired. | Same. | Existing masks. |
| **CTR with calipers** | Same prompt, heart and thorax calipers but no numeric result. | Same tool output. | Same images, paired. | Same. | Existing masks. |
| **Cardiac width with ruler** | “Estimate cardiac width in mm.” Contour/caliper plus visual ruler. | Mask width × calibrated column spacing. | At least 300 medium/high-confidence calibrated images. | ±10% and MAE in mm. | VinDr only; exclude NIH low-confidence spacing. |
| **Polarity relation** | Show A and B. “Are these the same intensity polarity or opposite polarity?” | Known inversion transform. | 200 CXR + 200 NM, 50/50 same/opposite. | Exact same/opposite. | All packages. |
| **Hot-side, natural** | “Ignoring the spine and bladder, which patient side has more total counts?” Show NM render only. | Pixel sums from lossless counts in preregistered lateral masks. | 200 unique patients with adequate asymmetry; 50/50 through mirrored copies. | Exact side. | Expand the 582-image Paraguay set; cluster anterior/posterior by patient. |
| **Hot-side, controlled** | Same question; apply 5%, 10%, or 20% multiplicative count asymmetry to one lateral skeletal region before rendering. | Generator parameters and recomputed counts. | 200 unique patients × magnitude, balanced side. | Exact side; psychometric curve by magnitude. | Existing bone scans. |
| **Mark-to-anatomy** | “Which marked region is the heart? Answer A–D.” Contour SoM; no region list. | Derived mask identity. | 400 CXR, balanced mark assignment. Chance 25%. | Exact letter. | Existing PSPNet masks. |
| **Mark-to-patient-side** | “Does mark A lie on patient left or patient right?” Neutral, non-side-named target region; visible edge badges only. | Mask centroid plus generated edge badges. | 400, 50/50. | Exact side. | CXR masks. Do not expose `lung_left` or `clavicle_left`. |
| **Crop-to-whole registration** | Whole image with sparse grid plus a separate crop. “Which grid cell contains this crop?” | Crop transform. | 400 crops; cells balanced. Chance 1/16 for 4×4. | Exact cell. | Any package. |
| **Render consistency** | Ask the same laterality, mark or hot-side question on two independently presented renders of one image. | Task truth plus shared source ID. | At least 300 sources per task. | Accuracy and pairwise consistency. Report “consistently wrong” separately. | All datasets. |

For consistency tasks, never report consistency alone. An always-wrong model is perfectly consistent.

## 4. Experimental design

### Paired conditions

For each source image, generate all applicable conditions:

1. Canonical baseline.
2. Current annotated render, image only.
3. Inspection sheet.
4. Inspection sheet without insets.
5. Inspection sheet without visual reference.
6. Contour SoM.
7. Bounding-box SoM.
8. Calipers without ruler.
9. Calipers with ruler.
10. Separate images versus one contact sheet.

The same task, truth and source image must be used across conditions. Randomize condition order. Do not regenerate masks between conditions.

### Attribution

Each visual proposal needs a component ablation:

- Large badges versus current small labels.
- Whole image versus whole image plus crop.
- Generic orientation reference versus no reference.
- Contours versus boxes.
- Ruler versus scale bar.
- Multiple windows versus the best single window.
- Separate attachments versus a single composite.

Include visual controls that identify the failure layer:

1. Can the model read a large generated R/L badge?
2. Can it map that badge to patient side?
3. Can it use anatomical asymmetry without the badge?
4. Can it reconcile anatomy and the badge when they conflict?

If step 1 fails, the input pipeline or encoder resolution is the problem. If step 1 passes but step 2 fails, the coordinate convention is the problem. If both pass but step 3 fails, the frozen model lacks the medical visual cue.

### Sample size

With Holm over 11 models, a per-model two-sided familywise threshold is roughly 0.0045 for the smallest p-value. Under a paired binary design and a discordant-pair rate around 0.25:

- About 400 independent source images are needed for 80% power to detect a 10-point gain.
- About 180 are needed for a 15-point gain.
- About 90 are needed for a 20-point gain.

These are planning approximations; the final preregistration should use simulation from pilot discordance rates.

The current VinDr-100 and NIH-50 sets are not adequately powered for modest render improvements after multiplicity correction. Mirrored and unmirrored variants do not create additional independent patients.

Recommended primary sizes:

- 400 unique CXR for orientation, localization and CTR tasks.
- At least 300 calibrated CXR for metric tasks.
- 200 unique bone-scan patients for hot-side tasks.
- NIH-50 only as an external-source sensitivity set.

### Replication

Use three replies per model × condition × source, at temperature zero where available.

Treat image or patient as the independent unit:

- Primary: majority vote across the three replies, paired by source.
- Secondary: all replies in a mixed-effects or cluster-bootstrap analysis.
- Report instability rate: proportion of cells with disagreement across repeats.
- For bone scans, cluster anterior/posterior views and synthetic variants by patient.

Three replies do not triple the sample size.

### Small local models

Do not relax their task or pool them with cloud models.

Do:

- Use the same images and exact-answer prompts.
- Record the actual image dimensions after provider preprocessing.
- Report invalid-format responses separately.
- Include a large-anchor legibility control.
- Report local models in their own stratum.
- Cap the contact sheet at the model’s supported resolution rather than silently allowing Ollama to resize it unpredictably.

### Execution policy

1. Smoke test 40 sources on the two local models and currently available Ollama-cloud models.
2. Drop variants that fail basic legibility or cause more than a five-point regression.
3. Run the full powered track on Ollama.
4. Freeze render definitions, prompts, task IDs, scorer and analysis.
5. Repeat only the surviving baseline-versus-best contrasts on the paid frontier APIs.

Do not silently replace retired Ollama tags. Record the resolved model ID and date.

## 5. Harness changes

### 1. Define a task and artifact schema — 1–2 engineer-days

Add a versioned task format:

```json
{
  "task_version": "vision-1.0",
  "source_id": "...",
  "patient_cluster": "...",
  "type": "mirror_detection",
  "images": [
    {
      "role": "target",
      "variant": "orientation_sheet",
      "path": "...",
      "sha256": "...",
      "width": 1536,
      "height": 1536
    }
  ],
  "answer": "mirrored",
  "choices": ["normal", "mirrored"],
  "generator": {
    "name": "mirror",
    "version": "1",
    "parameters": {"horizontal": true}
  }
}
```

Replace uses of Python’s randomized `hash(pkg.name)` in task selection with SHA-256-derived seeds. The misleading-label selection in [tasks.py](/Users/pal/oip-work/bench/tasks.py:87) is currently not reproducible across Python processes.

### 2. Add deterministic render generators — 4–6 days

Implement the proposed functions in `render.py` and `tools.py`, with tests for:

- Panel transforms.
- Minimum final font size.
- Ruler geometry.
- Crop coordinate recovery.
- Mirror transforms.
- No alteration of canonical pixels.
- Manifest/schema validation.

Generate benchmark artifacts in the run directory or a content-addressed cache. Do not write `_flipped.png` into the source package as [run.py](/Users/pal/oip-work/bench/run.py:93) currently does.

### 3. Generalize conditions into variant matrices — 2 days

Replace hard-coded condition branches with declarative condition records:

```python
Condition(
    name="vision_orientation_sheet",
    text_mode="question_only",
    image_variants=["orientation_sheet"],
)
```

`_call()` already accepts multiple images for all providers. The missing work is task-level image specification, stable labeling and provenance—not basic transport.

For A/B comparisons, test:

- Two separately attached images.
- One rendered A/B contact sheet.

Record attachment order.

### 4. Add vision-only task builders — 4–5 days

Create `bench/tasks_vision.py` rather than extending the current mixed text/file builder indefinitely.

It should:

- Produce controlled mirror, inversion, marker-swap and hot-side variants.
- Enforce balance.
- Group by patient.
- Reject indeterminate anatomy.
- Separate natural truth from synthetic-transform truth.
- Record every eligibility threshold in `tasks.json`.
- Label segmentation-derived values as pipeline truth.

### 5. Replace permissive parsing with task-specific exact scoring — 2 days

Bump the scorer version.

Use:

- Exact categorical tokens.
- Explicit invalid-answer state.
- Numeric parser with units for widths.
- CTR tolerance and continuous error.
- Pair-consistency records.
- No substring scoring for `left`/`right`.
- No reuse of `left_edge` scoring for semantically different NM tasks.

Keep raw replies.

### 6. Add repeats and immutable provenance — 2 days

`run.py` needs:

- `--repeats`.
- Repeat ID and provider seed where supported.
- Temperature and decoding parameters.
- Source-image SHA-256.
- Generated-image SHA-256.
- Pre- and post-downscale dimensions.
- Task-builder version.
- Render-generator version.
- All thresholds and transform parameters.
- `reply_sha256`.
- Resumption key including repeat ID.

The current completion key `(model, condition, task)` cannot support replication.

### 7. Analysis and power reporting — 3–4 days

Add:

- Paired accuracy differences and exact McNemar.
- Holm families declared per task and contrast.
- Patient-cluster bootstrap.
- Repeat instability.
- Psychometric hot-side curves.
- Accuracy-conditioned consistency.
- Per-model and model-family results.
- No pooling of natural and synthetic tasks.

Total: roughly 3 engineer-weeks including tests and report integration.

## 6. Risks and falsification

### Main risks

- **The overlay encodes the answer instead of improving perception.** Separate “read the generated badge” from “infer side from anatomy.”
- **Segmentation errors contaminate tasks.** For overlay-reading tasks this is acceptable only if described as reading the OIP pipeline output. It is not clinical ground truth.
- **Resolution differs by provider.** Store post-resize artifacts and dimensions.
- **The ruler becomes an OCR task.** Include relative-size tasks where labels alone do not determine the answer.
- **Reference tiles create a learned shortcut.** Counterbalance target placement, mirror status, label positions and panel order.
- **Synthetic hot-side manipulation looks artificial.** Apply changes in lossless count space, pass them through the normal renderer, and report natural and controlled tracks separately.
- **Visual clutter hurts small models.** Use component ablations and a strict maximum panel count.
- **Multiple views consume more visual tokens without improving integration.** Compare a single contact sheet with separate images and with the best single render.
- **Mirroring changes burned-in source text.** Either mask source text for anatomy-only tasks or treat it as a separate marker-reading task.

### Falsification rule

The render-improvement hypothesis should be considered falsified for the tested frozen VLMs if all of the following hold:

1. Models pass the large-label and ruler legibility controls.
2. At least 400 independent CXR and 200 bone-scan patients are tested.
3. Three replies per cell are collected.
4. The best preregistered visual variant improves no primary perception task by at least 10 percentage points after Holm correction.
5. Confidence intervals exclude a 10-point gain for the capable Ollama models.
6. The result replicates on at least two frontier models after the design is frozen.

If that happens, the correct OIP scope is narrower:

- OIP reliably supplies facts, provenance, calibrated geometry and deterministic tool outputs.
- It can make those facts visually accessible.
- It cannot make a frozen general-purpose VLM perform medical pixel verification.
- Orientation checking, measurement and count comparison must remain tool-side guarantees.
- `context.md` should say what the tool found; the protocol should stop implying that self-description causes pixel inspection.
- Enhanced renders remain optional human/agent affordances, not a conformance claim.

That outcome would not invalidate OIP. It would invalidate the stronger claim that packaging alone can repair the visual perception of frozen VLMs.

tokens used: 886607
