# Render probe: flip check and left edge on the annotated render and the inspection sheet

Runs: 20260927-113720-ollama_gemma4_e4b-it-qat-69876, 20260927-121150-ollama_medgemma1.5_4b-82048, 20260928-092803-ollama_glm-5.3-flash_cloud-64258, 20260928-093240-ollama_kimi-k3_cloud-65456, 20260928-201856-ollama_minimax-m3_cloud-6470, 20260928-204720-ollama_mistral-large-3_675b-cloud-12318, 20260928-213925-ollama_gemma4_31b-cloud-23021

## Flip check (mirrored render vs printed/stated orientation)

| model | ctx_ctl | annot_ctx | annot_only | insp_ctx | insp_only | both items right per image, by condition |
|---|---|---|---|---|---|---|
| gemma4:31b-cloud | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 0/40 / 0/40 / 0/40 / 0/40 / 0/40 |
| gemma4:e4b-it-qat | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 49 % (38–60; n=80) | 0/40 / 0/40 / 0/40 / 0/40 / 4/40 |
| glm-5.3-flash:cloud | 81 % (71–88; n=80) | 68 % (57–77; n=80) | 85 % (76–91; n=80) | 74 % (63–82; n=80) | 60 % (49–70; n=80) | 26/40 / 16/40 / 28/40 / 21/40 / 12/40 |
| kimi-k3:cloud | 55 % (44–65; n=80) | 49 % (38–60; n=80) | 59 % (48–69; n=80) | 58 % (47–68; n=80) | 60 % (49–70; n=80) | 7/40 / 3/40 / 11/40 / 6/40 / 14/40 |
| medgemma1.5:4b | 50 % (39–61; n=80) | 51 % (40–62; n=80) | 50 % (39–61; n=80) | 51 % (40–62; n=80) | 50 % (39–61; n=80) | 1/40 / 1/40 / 0/40 / 2/40 / 0/40 |
| minimax-m3:cloud | 51 % (40–62; n=80) | 51 % (40–62; n=80) | 58 % (47–68; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 4/40 / 1/40 / 8/40 / 0/40 / 0/40 |
| mistral-large-3:675b-cloud | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 0/40 / 0/40 / 0/40 / 0/40 / 0/40 |

### flip_check: each condition against ctx_ctl (paired items; b = right only in control, c = right only in the condition; exact McNemar, Holm over models)

| model | annot_ctx: Δpp, b/c, p | annot_only: Δpp, b/c, p | insp_ctx: Δpp, b/c, p | insp_only: Δpp, b/c, p |
|---|---|---|---|---|
| gemma4:31b-cloud | +0, 1/1, 1.000 | +0, 1/1, 1.000 | +0, 1/1, 1.000 | +0, 1/1, 1.000 |
| gemma4:e4b-it-qat | +0, 0/0, 1.000 | +0, 0/0, 1.000 | +0, 0/0, 1.000 | -1, 6/5, 1.000 |
| glm-5.3-flash:cloud | -14, 19/8, 0.366 | +4, 9/12, 1.000 | -8, 15/9, 1.000 | -21, 22/5, 0.011 |
| kimi-k3:cloud | -6, 11/6, 1.000 | +4, 13/16, 1.000 | +2, 7/9, 1.000 | +5, 16/20, 1.000 |
| medgemma1.5:4b | +1, 1/2, 1.000 | +0, 1/1, 1.000 | +1, 2/3, 1.000 | +0, 1/1, 1.000 |
| minimax-m3:cloud | +0, 5/5, 1.000 | +6, 6/11, 1.000 | -1, 5/4, 1.000 | -1, 5/4, 1.000 |
| mistral-large-3:675b-cloud | +0, 0/0, 1.000 | +0, 0/0, 1.000 | +0, 0/0, 1.000 | +0, 0/0, 1.000 |

## Left edge (which patient side is at the image's left edge)

| model | ctx_ctl | annot_ctx | annot_only | insp_ctx | insp_only |
|---|---|---|---|---|---|
| gemma4:31b-cloud | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 100 % (91–100; n=40) |
| gemma4:e4b-it-qat | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 72 % (57–84; n=40) | 100 % (91–100; n=40) | 70 % (55–82; n=40) |
| glm-5.3-flash:cloud | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 98 % (87–100; n=40) | 95 % (83–99; n=40) |
| kimi-k3:cloud | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 98 % (87–100; n=40) | 100 % (91–100; n=40) | 100 % (91–100; n=40) |
| medgemma1.5:4b | 72 % (57–84; n=40) | 82 % (68–91; n=40) | 5 % (1–17; n=40) | 58 % (42–71; n=40) | 2 % (0–13; n=40) |
| minimax-m3:cloud | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 100 % (91–100; n=40) |
| mistral-large-3:675b-cloud | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 98 % (87–100; n=40) | 100 % (91–100; n=40) | 15 % (7–29; n=40) |

### left_edge: each condition against ctx_ctl (paired items; b = right only in control, c = right only in the condition; exact McNemar, Holm over models)

| model | annot_ctx: Δpp, b/c, p | annot_only: Δpp, b/c, p | insp_ctx: Δpp, b/c, p | insp_only: Δpp, b/c, p |
|---|---|---|---|---|
| gemma4:31b-cloud | +0, 0/0, 1.000 | +0, 0/0, 1.000 | +0, 0/0, 1.000 | +0, 0/0, 1.000 |
| gemma4:e4b-it-qat | +0, 0/0, 1.000 | -28, 11/0, 0.006 | +0, 0/0, 1.000 | -30, 12/0, 0.002 |
| glm-5.3-flash:cloud | +0, 0/0, 1.000 | +0, 0/0, 1.000 | -2, 1/0, 1.000 | -5, 2/0, 1.000 |
| kimi-k3:cloud | +0, 0/0, 1.000 | -2, 1/0, 1.000 | +0, 0/0, 1.000 | +0, 0/0, 1.000 |
| medgemma1.5:4b | +10, 5/9, 1.000 | -68, 27/0, <0.001 | -15, 12/6, 1.000 | -70, 28/0, <0.001 |
| minimax-m3:cloud | +0, 0/0, 1.000 | +0, 0/0, 1.000 | +0, 0/0, 1.000 | +0, 0/0, 1.000 |
| mistral-large-3:675b-cloud | +0, 0/0, 1.000 | -2, 1/0, 1.000 | +0, 0/0, 1.000 | -85, 34/0, <0.001 |


## Reading (all seven Ollama models, 2026-09-28 22:00; 4,200 rows, 0 errors)

**Flip check.** Four models answer "agree" to every item in every condition (gemma4:31b, mistral-large-3, gemma4:e4b, MedGemma: 50 %, 0–4 images both right). minimax detects 8/40 mirrored images with the annotated render alone (58 %, n.s.) and none with the sheet. kimi-k3 goes from 55 % to 60 % with the sheet alone (n.s.), but only by shifting its bias: it detects 22/40 mirrored images instead of 7 while its correct answers on unmirrored images fall from 37 to 26. glm, the one model with real discrimination, loses 21 points with the sheet alone (Holm p = 0.011 over seven models) through false alarms on unmirrored images. No model improves significantly in any condition; the annotated render alone is never worse than the control.

**Left edge (badge reading, no file).** gemma4:31b, kimi-k3, minimax, glm read the badges correctly on both renders (95–100 %). gemma4:e4b reads them at 70–72 %. MedGemma inverts them on both renders (2–5 %). **mistral-large-3 reads the annotated render's letters correctly (98 %) but inverts the sheet's badges (15 %, 34 items wrong only with the sheet, Holm p < 0.001):** the boxed 96 px badges are mapped to the wrong side by a model that maps the plain margin letters correctly. Caveat as before: the truth is constant (all PA), so a fixed "patient right" also scores 100 %.

**Conclusion.** The resolution hypothesis is rejected for every Ollama model: larger, encoder-safe anchors and a heart inset neither create mirror detection where there was none (six of seven models) nor sharpen it where it exists (glm), and the composite has two harmful side effects (glm false alarms, mistral badge inversion). The shipped annotated render is not the problem. What the models that partly pass use is anatomy and the burned-in source marker, both of which the package cannot supply and one of which (the marker, mirrored into a reversed glyph) is a cue the benchmark should mask for anatomy-only items. OEP-005 in this form is not adopted; `inspection_sheet()` stays in the code as an optional render for the vision-only track, not as a conformance claim. The tool-side orientation check (`oip check`, two-pass, 94/100 decided, 0 wrong) remains the guarantee that does not depend on the model.
