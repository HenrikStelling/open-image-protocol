# Repeat subset: run-to-run reliability of the main-result cells (2026-10-24)

Runs: `20261024-080342-ollama_gemma4_31b-cloud+ollama_glm-5.3-flash_cloud+ollama_ki-46689`, `20261024-080342-ollama_gemma4_e4b-it-qat+ollama_medgemma1.5_4b-46693`. 20 packages, 3 replies per item, 1624 (model, condition, item) cells, 4872 replies. Items with more than one prompt hash across repeats: 0. Paper comparison: latest run per cell dated up to 20260922 on the `vindr-paper` packages, re-scored with the current scorer (the repeat packages carry the CheXmask cross-check table and template 0.2.1, so the full-file prompt differs from the paper's).

Columns: accuracy (adoption for findings_misled) per repeat; stable = items with the same verdict in every repeat; kappa = Fleiss' kappa of the verdict across repeats; paper = the paper run's single reply on the same items; agrees = share of items where the paper verdict equals the majority verdict of the repeats. Items with an error row in any repeat are dropped from stable/kappa. Kappa is near zero whenever almost every verdict has the same value (prevalence effect, e.g. 95 % wrong in every repeat), so read it together with stable.

## ollama/gemma4:31b-cloud

| Condition | Task | n | rep 0 | rep 1 | rep 2 | range (pp) | stable | kappa | paper | agrees |
|---|---|---|---|---|---|---|---|---|---|---|
| raw | left_edge | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| raw | scale_available | 20 | 20 % | 20 % | 20 % | 0 | 100 % (20/20) | 1.00 | 20 % | 100 % |
| raw | ctr | 20 | 80 % | 90 % | 75 % | 15 | 75 % (15/20) | 0.44 | 70 % | 90 % |
| raw | heart_mm | 16 | 50 % | 44 % | 50 % | 6 | 62 % (10/16) | 0.50 | 50 % | 81 % |
| ctx | left_edge | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | scale_available | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | ctr | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | heart_mm | 16 | 100 % | 100 % | 100 % | 0 | 100 % (16/16) | 1.00 | 100 % | 100 % |
| ctx | flip_check | 40 | 50 % | 50 % | 50 % | 0 | 100 % (40/40) | 1.00 | 50 % | 100 % |
| misled_plain | findings_misled | 20 | 80 % | 75 % | 70 % | 10 | 90 % (18/20) | 0.82 | 75 % | 70 % |
| misled_oip | findings_misled | 20 | 60 % | 60 % | 65 % | 5 | 95 % (19/20) | 0.93 | 55 % | 75 % |

## ollama/glm-5.3-flash:cloud

| Condition | Task | n | rep 0 | rep 1 | rep 2 | range (pp) | stable | kappa | paper | agrees |
|---|---|---|---|---|---|---|---|---|---|---|
| raw | left_edge | 20 | 100 % | 95 % | 85 % | 15 | 80 % (16/20) | -0.07 | 90 % | 90 % |
| raw | scale_available | 20 | 20 % | 20 % | 20 % | 0 | 100 % (20/20) | 1.00 | 20 % | 100 % |
| raw | ctr | 20 | 55 % | 50 % | 65 % | 15 | 45 % (9/20) | 0.25 | 50 % | 65 % |
| raw | heart_mm | 16 | 38 % | 50 % | 44 % | 12 | 25 % (4/16) | -0.02 | 19 % | 62 % |
| ctx | left_edge | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | scale_available | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | ctr | 20 | 70 % | 90 % | 95 % | 25 | 60 % (12/20) | -0.05 | 75 % | 80 % |
| ctx | heart_mm | 16 | 94 % | 88 % | 75 % | 19 | 69 % (11/16) | 0.16 | 88 % | 75 % |
| ctx | flip_check | 40 | 85 % | 72 % | 85 % | 12 | 62 % (25/40) | 0.19 | 88 % | 82 % |
| misled_plain | findings_misled | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| misled_oip | findings_misled | 20 | 80 % | 80 % | 90 % | 10 | 60 % (12/20) | 0.04 | 80 % | 90 % |

## ollama/kimi-k3:cloud

| Condition | Task | n | rep 0 | rep 1 | rep 2 | range (pp) | stable | kappa | paper | agrees |
|---|---|---|---|---|---|---|---|---|---|---|
| raw | left_edge | 20 | 100 % | 95 % | 95 % | 5 | 95 % (19/20) | 0.48 | 100 % | 95 % |
| raw | scale_available | 20 | 20 % | 25 % | 20 % | 5 | 95 % (19/20) | 0.90 | 20 % | 100 % |
| raw | ctr | 20 | 60 % | 80 % | 75 % | 20 | 70 % (14/20) | 0.51 | 90 % | 75 % |
| raw | heart_mm | 16 | 44 % | 62 % | 44 % | 19 | 38 % (6/16) | 0.17 | 69 % | 69 % |
| ctx | left_edge | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | scale_available | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | ctr | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | heart_mm | 16 | 100 % | 100 % | 100 % | 0 | 100 % (16/16) | 1.00 | 100 % | 100 % |
| ctx | flip_check | 40 | 48 % | 62 % | 60 % | 15 | 65 % (26/40) | 0.52 | 52 % | 82 % |
| misled_plain | findings_misled | 20 | 75 % | 85 % | 85 % | 10 | 50 % (10/20) | -0.11 | 75 % | 70 % |
| misled_oip | findings_misled | 20 | 75 % | 60 % | 40 % | 35 | 45 % (9/20) | 0.25 | 60 % | 50 % |

## ollama/minimax-m3:cloud

| Condition | Task | n | rep 0 | rep 1 | rep 2 | range (pp) | stable | kappa | paper | agrees |
|---|---|---|---|---|---|---|---|---|---|---|
| raw | left_edge | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| raw | scale_available | 20 | 20 % | 20 % | 20 % | 0 | 100 % (20/20) | 1.00 | 20 % | 100 % |
| raw | ctr | 20 | 55 % | 40 % | 50 % | 15 | 60 % (12/20) | 0.47 | 65 % | 70 % |
| raw | heart_mm | 16 | 44 % | 69 % | 62 % | 25 | 38 % (6/16) | 0.14 | 44 % | 69 % |
| ctx | left_edge | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | scale_available | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | ctr | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | heart_mm | 16 | 100 % | 100 % | 100 % | 0 | 100 % (16/16) | 1.00 | 100 % | 100 % |
| ctx | flip_check | 40 | 50 % | 50 % | 50 % | 0 | 100 % (40/40) | 1.00 | 52 % | 92 % |
| misled_plain | findings_misled | 20 | 90 % | 85 % | 80 % | 10 | 65 % (13/20) | 0.08 | 80 % | 80 % |
| misled_oip | findings_misled | 20 | 40 % | 50 % | 40 % | 10 | 55 % (11/20) | 0.39 | 50 % | 55 % |

## ollama/mistral-large-3:675b-cloud

| Condition | Task | n | rep 0 | rep 1 | rep 2 | range (pp) | stable | kappa | paper | agrees |
|---|---|---|---|---|---|---|---|---|---|---|
| raw | left_edge | 20 | 65 % | 65 % | 75 % | 10 | 85 % (17/20) | 0.77 | 60 % | 90 % |
| raw | scale_available | 20 | 20 % | 20 % | 20 % | 0 | 100 % (20/20) | 1.00 | 20 % | 100 % |
| raw | ctr | 20 | 15 % | 15 % | 15 % | 0 | 100 % (20/20) | 1.00 | 20 % | 95 % |
| raw | heart_mm | 16 | 56 % | 56 % | 56 % | 0 | 100 % (16/16) | 1.00 | 50 % | 94 % |
| ctx | left_edge | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | scale_available | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | ctr | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | heart_mm | 16 | 100 % | 100 % | 100 % | 0 | 100 % (16/16) | 1.00 | 100 % | 100 % |
| ctx | flip_check | 40 | 50 % | 50 % | 50 % | 0 | 100 % (40/40) | 1.00 | 50 % | 100 % |
| misled_plain | findings_misled | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| misled_oip | findings_misled | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |

## ollama/gemma4:e4b-it-qat

| Condition | Task | n | rep 0 | rep 1 | rep 2 | range (pp) | stable | kappa | paper | agrees |
|---|---|---|---|---|---|---|---|---|---|---|
| raw | left_edge | 20 | 50 % | 35 % | 40 % | 15 | 50 % (10/20) | 0.31 | 40 % | 65 % |
| raw | scale_available | 20 | 20 % | 20 % | 20 % | 0 | 100 % (20/20) | 1.00 | 50 % | 70 % |
| raw | ctr | 20 | 35 % | 25 % | 45 % | 20 | 75 % (15/20) | 0.63 | 30 % | 80 % |
| raw | heart_mm | 16 | 19 % | 44 % | 19 % | 25 | 31 % (5/16) | -0.16 | 12 % | 88 % |
| ctx | left_edge | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | scale_available | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | ctr | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | heart_mm | 16 | 100 % | 100 % | 100 % | 0 | 100 % (16/16) | 1.00 | 100 % | 100 % |
| ctx | flip_check | 40 | 48 % | 50 % | 50 % | 2 | 98 % (39/40) | 0.97 | 50 % | 100 % |
| misled_plain | findings_misled | 20 | 90 % | 80 % | 85 % | 10 | 85 % (17/20) | 0.61 | 100 % | 90 % |
| misled_oip | findings_misled | 20 | 45 % | 50 % | 35 % | 15 | 60 % (12/20) | 0.46 | 80 % | 40 % |

## ollama/medgemma1.5:4b

| Condition | Task | n | rep 0 | rep 1 | rep 2 | range (pp) | stable | kappa | paper | agrees |
|---|---|---|---|---|---|---|---|---|---|---|
| raw | left_edge | 20 | 5 % | 10 % | 5 % | 5 | 80 % (16/20) | -0.07 | 5 % | 95 % |
| raw | scale_available | 20 | 80 % | 80 % | 80 % | 0 | 100 % (20/20) | 1.00 | 80 % | 100 % |
| raw | ctr | 20 | 40 % | 50 % | 40 % | 10 | 90 % (18/20) | 0.86 | 40 % | 90 % |
| raw | heart_mm | 16 | 0 % | 6 % | 6 % | 6 | 88 % (14/16) | -0.04 | 6 % | 94 % |
| ctx | left_edge | 20 | 80 % | 85 % | 65 % | 20 | 45 % (9/20) | -0.02 | 65 % | 50 % |
| ctx | scale_available | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | ctr | 20 | 100 % | 100 % | 100 % | 0 | 100 % (20/20) | 1.00 | 100 % | 100 % |
| ctx | heart_mm | 16 | 100 % | 100 % | 100 % | 0 | 100 % (16/16) | 1.00 | 100 % | 100 % |
| ctx | flip_check | 40 | 52 % | 52 % | 50 % | 2 | 90 % (36/40) | 0.87 | 48 % | 98 % |
| misled_plain | findings_misled | 20 | 95 % | 95 % | 85 % | 10 | 90 % (18/20) | 0.56 | 85 % | 90 % |
| misled_oip | findings_misled | 20 | 0 % | 0 % | 10 % | 10 | 90 % (18/20) | -0.03 | 0 % | 100 % |

## Overview per model

| Model | cells | largest range (pp) | median stable | median kappa | cells with kappa < 0.6 |
|---|---|---|---|---|---|
| ollama/gemma4:31b-cloud | 11 | 15 | 100 % | 1.00 | 2 |
| ollama/glm-5.3-flash:cloud | 11 | 25 | 69 % | 0.19 | 7 |
| ollama/kimi-k3:cloud | 11 | 35 | 95 % | 0.52 | 6 |
| ollama/minimax-m3:cloud | 11 | 25 | 100 % | 1.00 | 4 |
| ollama/mistral-large-3:675b-cloud | 11 | 10 | 100 % | 1.00 | 0 |
| ollama/gemma4:e4b-it-qat | 11 | 25 | 98 % | 0.97 | 3 |
| ollama/medgemma1.5:4b | 11 | 20 | 90 % | 0.86 | 5 |

