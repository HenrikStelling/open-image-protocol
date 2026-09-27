# Render probe: flip check and left edge on the annotated render and the inspection sheet

Runs: 20260927-113720-ollama_gemma4_e4b-it-qat-69876, 20260927-121150-ollama_medgemma1.5_4b-82048

## Flip check (mirrored render vs printed/stated orientation)

| model | ctx_ctl | annot_ctx | annot_only | insp_ctx | insp_only | both items right per image, by condition |
|---|---|---|---|---|---|---|
| gemma4:e4b-it-qat | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 49 % (38–60; n=80) | 0/40 / 0/40 / 0/40 / 0/40 / 4/40 |
| medgemma1.5:4b | 50 % (39–61; n=80) | 51 % (40–62; n=80) | 50 % (39–61; n=80) | 51 % (40–62; n=80) | 50 % (39–61; n=80) | 1/40 / 1/40 / 0/40 / 2/40 / 0/40 |

### flip_check: each condition against ctx_ctl (paired items; b = right only in control, c = right only in the condition; exact McNemar, Holm over models)

| model | annot_ctx: Δpp, b/c, p | annot_only: Δpp, b/c, p | insp_ctx: Δpp, b/c, p | insp_only: Δpp, b/c, p |
|---|---|---|---|---|
| gemma4:e4b-it-qat | +0, 0/0, 1.000 | +0, 0/0, 1.000 | +0, 0/0, 1.000 | -1, 6/5, 1.000 |
| medgemma1.5:4b | +1, 1/2, 1.000 | +0, 1/1, 1.000 | +1, 2/3, 1.000 | +0, 1/1, 1.000 |

## Left edge (which patient side is at the image's left edge)

| model | ctx_ctl | annot_ctx | annot_only | insp_ctx | insp_only |
|---|---|---|---|---|---|
| gemma4:e4b-it-qat | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 72 % (57–84; n=40) | 100 % (91–100; n=40) | 70 % (55–82; n=40) |
| medgemma1.5:4b | 72 % (57–84; n=40) | 82 % (68–91; n=40) | 5 % (1–17; n=40) | 58 % (42–71; n=40) | 2 % (0–13; n=40) |

### left_edge: each condition against ctx_ctl (paired items; b = right only in control, c = right only in the condition; exact McNemar, Holm over models)

| model | annot_ctx: Δpp, b/c, p | annot_only: Δpp, b/c, p | insp_ctx: Δpp, b/c, p | insp_only: Δpp, b/c, p |
|---|---|---|---|---|
| gemma4:e4b-it-qat | +0, 0/0, 1.000 | -28, 11/0, <0.001 | +0, 0/0, 1.000 | -30, 12/0, <0.001 |
| medgemma1.5:4b | +10, 5/9, 0.848 | -68, 27/0, <0.001 | -15, 12/6, 0.476 | -70, 28/0, <0.001 |


## Reading (local models, 2026-09-27 13:30)

- **Flip check: unchanged at 50 % in every condition.** Both small models answer "agree" to every item: gemma4:e4b 80/80 in ctx_ctl, annot_ctx, annot_only and insp_ctx (on insp_only 11 random "mirrored" answers, 4/40 images both right by chance); MedGemma the same with a few off-format replies. Neither the re-rendered annotated image nor the inspection sheet with 96 px badges, the enlarged heart inset and the ruler moves the check. For these two models the failure is not the size of the labels.
- **Left edge without the file (badge-reading control): the badge is read but mapped wrongly.** gemma4:e4b answers "patient right" (correct) 29/40 and 28/40 with the annotated render and the sheet, "patient left" otherwise; MedGemma answers "patient left" 38/40 and 39/40, i.e. it reads the R badge at the left edge and inverts it systematically. With the file both are back to 100 % / 72 % (MedGemma's ctx_ctl errors are off-format replies, not the wrong side). In Codex's staged reading this is stage 2 (convention), not stage 1 (legibility).
- **Caveat on the control:** all 40 packages are PA radiographs with patient right at the left edge, so the left-edge truth is constant; a "patient right always" policy scores 100 %. The badge-swap variant of the vision-only track (generated labels swapped on half the items) is needed before this control can separate reading from prior.
- Cloud models pending (lane queued behind the OEP-004 ablation lane and the Ollama cloud outage).
