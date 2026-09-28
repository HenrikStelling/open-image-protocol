# Render probe: flip check and left edge on the annotated render and the inspection sheet

Runs: 20260927-113720-ollama_gemma4_e4b-it-qat-69876, 20260927-121150-ollama_medgemma1.5_4b-82048, 20260928-092803-ollama_glm-5.3-flash_cloud-64258

## Flip check (mirrored render vs printed/stated orientation)

| model | ctx_ctl | annot_ctx | annot_only | insp_ctx | insp_only | both items right per image, by condition |
|---|---|---|---|---|---|---|
| gemma4:e4b-it-qat | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 50 % (39–61; n=80) | 49 % (38–60; n=80) | 0/40 / 0/40 / 0/40 / 0/40 / 4/40 |
| glm-5.3-flash:cloud | 81 % (71–88; n=80) | 68 % (57–77; n=80) | 85 % (76–91; n=80) | 74 % (63–82; n=80) | 60 % (49–70; n=80) | 26/40 / 16/40 / 28/40 / 21/40 / 12/40 |
| medgemma1.5:4b | 50 % (39–61; n=80) | 51 % (40–62; n=80) | 50 % (39–61; n=80) | 51 % (40–62; n=80) | 50 % (39–61; n=80) | 1/40 / 1/40 / 0/40 / 2/40 / 0/40 |

### flip_check: each condition against ctx_ctl (paired items; b = right only in control, c = right only in the condition; exact McNemar, Holm over models)

| model | annot_ctx: Δpp, b/c, p | annot_only: Δpp, b/c, p | insp_ctx: Δpp, b/c, p | insp_only: Δpp, b/c, p |
|---|---|---|---|---|
| gemma4:e4b-it-qat | +0, 0/0, 1.000 | +0, 0/0, 1.000 | +0, 0/0, 1.000 | -1, 6/5, 1.000 |
| glm-5.3-flash:cloud | -14, 19/8, 0.157 | +4, 9/12, 1.000 | -8, 15/9, 0.922 | -21, 22/5, 0.005 |
| medgemma1.5:4b | +1, 1/2, 1.000 | +0, 1/1, 1.000 | +1, 2/3, 1.000 | +0, 1/1, 1.000 |

## Left edge (which patient side is at the image's left edge)

| model | ctx_ctl | annot_ctx | annot_only | insp_ctx | insp_only |
|---|---|---|---|---|---|
| gemma4:e4b-it-qat | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 72 % (57–84; n=40) | 100 % (91–100; n=40) | 70 % (55–82; n=40) |
| glm-5.3-flash:cloud | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 100 % (91–100; n=40) | 98 % (87–100; n=40) | 95 % (83–99; n=40) |
| medgemma1.5:4b | 72 % (57–84; n=40) | 82 % (68–91; n=40) | 5 % (1–17; n=40) | 58 % (42–71; n=40) | 2 % (0–13; n=40) |

### left_edge: each condition against ctx_ctl (paired items; b = right only in control, c = right only in the condition; exact McNemar, Holm over models)

| model | annot_ctx: Δpp, b/c, p | annot_only: Δpp, b/c, p | insp_ctx: Δpp, b/c, p | insp_only: Δpp, b/c, p |
|---|---|---|---|---|
| gemma4:e4b-it-qat | +0, 0/0, 1.000 | -28, 11/0, 0.002 | +0, 0/0, 1.000 | -30, 12/0, <0.001 |
| glm-5.3-flash:cloud | +0, 0/0, 1.000 | +0, 0/0, 1.000 | -2, 1/0, 1.000 | -5, 2/0, 0.500 |
| medgemma1.5:4b | +10, 5/9, 1.000 | -68, 27/0, <0.001 | -15, 12/6, 0.714 | -70, 28/0, <0.001 |


## Reading (glm-5.3-flash, 2026-09-28 11:20; 600 rows, 0 errors)

- **Flip check:** ctx_ctl 81 % (26/40 images both right), annot_ctx 68 %, annot_only 85 %, insp_ctx 74 %, **insp_only 60 %** (−21 pp vs control, 22 items right only in control against 5, Holm p = 0.005). The annotated render without the file is on par with the control (+4 pp, n.s.); the inspection sheet is worse, with the file and without.
- **The sheet does not change mirror detection, it adds false alarms.** Mirrored items are detected in every condition (39, 36, 39, 38, 35 of 40); the losses are on the unmirrored items: 26/40 right in the control, 18/40 with the annotated render + file, 21/40 with the sheet + file and 13/40 with the sheet alone, i.e. glm answers "mirrored" for normal images more often when it gets the sheet. Its replies cite anatomy (apex, aortic knob, gastric bubble) in 38–39 of 40 mirrored items and the burned-in source marker in 31–35, in all conditions alike, so the cue it uses is not the badge and the sheet's enlarged heart inset seems to mislead its side judgement on normal images rather than help it.
- **Left edge:** 100 / 100 / 100 / 98 / 95 %. glm reads the badges and maps them correctly; the two small models do not (see above).
- **Net for the resolution hypothesis:** for the one Ollama model that partly passes the flip check, larger anchors do not help and a composite hurts; for the two small models nothing moves. The remaining cloud models (kimi-k3, minimax, mistral, gemma4:31b; all at chance on the paper's flip check) are running to complete the table.
