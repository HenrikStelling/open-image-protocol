# Q3 — How do LLMs understand DICOM today?

## Short answer
They don't read DICOM. Every pipeline first converts DICOM to an 8-bit RGB/grey
PNG/JPEG, discarding most metadata, and then feeds pixels to a vision encoder.
Metadata, if used at all, is pasted as text into the prompt. Both steps are lossy
and unstandardised.

## Evidence

1. **Preprocessing practice.** Papers on CXR VLMs (CXR-LLaVA, LiteGPT, ChestGPT,
   MAIRA-2, LLaVA-Rad) normalise raw 10–16-bit data to 8 bits "using stored
   windowing parameters or the full range if missing", i.e. VOI LUT
   (WindowCenter/Width) → 8-bit. Anything not in the window is gone.
   MONOCHROME1 images must be inverted first or the model sees a negative.
2. **Information loss is measurable.** WindowNet (PMC10743662): applying a
   window before classification *improves* performance, and bit depth matters —
   the choice of window is a modelling decision that is currently made silently.
3. **General VLMs on raw exports.** GPT-4o on mixed chest/abdominal X-rays:
   69 % of pathologies identified (PMC12113413). Specialised 7B models
   (LLaVA-Rad, CXR-LLaVA) outperform GPT-4V/Gemini-Pro-Vision on CXR findings.
4. **Quantitative and spatial blind spots.** MedVision (2025): off-the-shelf VLMs
   "perform poorly" on size, angle and distance tasks. "Your other Left!"
   (MICCAI 2025): GPT-4o, Llama-3.2, Pixtral, JanusPro *all fail* at relative
   position in medical images; visual markers give only moderate gains; models
   lean on anatomical priors rather than the pixels.
5. **Text context dominates pixels.** MC-CXR (2026): with misleading text
   context, models switch answers 45.6–78.1 % of the time and adopt the wrong
   text label 74.6 % of the time (vs 17.6 % for misleading visual context).
   Any protocol that adds text to an image must therefore carry provenance and
   confidence, or it will make things worse.
6. **Agentic access to DICOM exists but stops at transport.** dicom-mcp lets
   Claude/ChatGPT query and move studies on a PACS via MCP; it does not make
   pixels or units understandable.

## Implications
- The conversion step *is* the protocol: whoever decides windowing, polarity,
  orientation and scale decides what the model sees. OIP standardises it and
  records it.
- Feed the model **facts computed by tools**, labelled as such; keep external
  narrative (prior reports) clearly separated and marked `external`.
- Visual cues (orientation labels, scale bar, region marks) belong in the render,
  because models process them differently from text.

## What OIP does about it
- Canonical render rules (Q10) and explicit `intensity.voi` record.
- `assertion_level` on every fact; `context.md` template separates measured /
  computed / inferred / external.
- Annotated render with R/L, A/P labels and scale bar; optional set-of-mark overlay.
- OIP-Bench (Q12) measures whether this actually helps, per model.
