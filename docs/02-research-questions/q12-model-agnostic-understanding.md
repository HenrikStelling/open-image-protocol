# Q12 — How can any capable vision model understand the image, its nature, measurements and metrics **without prior training**?

## The contract
An OIP package is designed to be dropped into *any* multimodal prompt as
(1) one or two PNGs and (2) one Markdown file, and be sufficient. No fine-tuning,
no special tokenizer, no SDK required on the model side. (SDK/MCP are conveniences.)

## Five mechanisms, each backed by evidence

| # | Mechanism | Evidence it helps | Where in OIP |
|---|---|---|---|
| 1 | **Canonical render** with correct polarity, VOI window, original aspect ratio | 8-bit/windowing choices change model performance (WindowNet; CXR VLM pipelines) | `renders/canonical.png` |
| 2 | **Annotated render**: R/L and A/P labels at the image edges, a scale bar in mm, optional numbered region marks (set-of-mark) | SoM prompting improves grounding in GPT-4V; grid/ruler overlays +0.145 IoU (GPT-5.2); visual markers give moderate gains on medical relative-position tasks | `renders/annotated.png` |
| 3 | **Measurements computed outside the model**, presented as a table with units, method, confidence | VLMs are poor at size/angle/distance (MedVision); MHS keeps physics in the driver | `derived/measurements.json`, `context.md` §Measured facts |
| 4 | **Fixed-template `context.md`** with assertion levels (measured / computed / inferred / external / unknown) and explicit cautions | Models adopt misleading text 74.6 % of the time (MC-CXR) → text must carry trust labels; llms.txt/MHS reference-file pattern; Markdown is token-cheap (up to 10× vs HTML) | `context.md` |
| 5 | **Self-check block**: 3–5 Q&A pairs whose answers are in the package ("Which side of the image is the patient's right?") | Lets the model calibrate before answering; makes failures detectable in the benchmark | `context.md` §Self-check |

## `context.md` template (v0.1)
```
# OIP image reference — <short title>
## What this is            (modality, body part, view, tracer; one paragraph)
## How to read the renders (polarity, window, orientation labels, scale bar, what is NOT corrected)
## Measured facts          (from source metadata; assertion: measured)
## Computed measurements   (table: name, value, unit, method, confidence, validation status)
## Inferred                (model/heuristic outputs; assertion: inferred)
## External context        (prior report text, dataset labels; assertion: external — verify against pixels)
## Unknowns and cautions   (missing spacing, magnification not corrected, counts not comparable across studies…)
## Self-check              (Q/A pairs)
## Machine-readable        (path to oip.json, schema version)
```

## How we prove it (OIP-Bench, Phase 3)
For each model (Claude, GPT, Gemini, one open model), for each image, three
conditions: **raw PNG**, **PNG + context.md**, **annotated PNG + context.md**.
Tasks 1–9 from Q1 §C. Success criterion for v0.1: statistically significant
uplift on modality/orientation/scale/CTR tasks for *every* model, no degradation
on finding-level F1, and a lower switch rate under misleading `external` text
than under unlabeled text.

## What OIP does about it
`src/oip/context.py` renders the template from the manifest; `render.py`
produces the annotated PNG; the benchmark harness is a Phase 3 deliverable.
