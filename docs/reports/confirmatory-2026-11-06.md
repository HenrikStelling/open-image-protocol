# Confirmatory round — pre-registered analysis (2026-11-06)

Primary data: the first reply (rep 0) of every item. Per-model one-sided exact binomial tests (exact McNemar for H2b), Holm within each statement, alpha 0.05; a statement is confirmed when at least the registered number of models meets its criterion. Registration: docs/paper/preregistration-draft-2026-11-02.md (final text on OSF).

| model | model id | run dir | started | harness commit(s) | tasks / scorer | rep-0 items missing | rep-0 error rows |
|---|---|---|---|---|---|---|---|
| claude | claude-sonnet-5 | 20261104-151438-claude-20403 | 2026-11-04T15:14:38 | 394350e-dirty, 855ad12-dirty | 3.0 / 0.3 | 0 | 0 |
| gemini | gemini-3.8-flash | 20261104-151438-gemini-20419 | 2026-11-04T15:14:38 | 394350e-dirty, 855ad12-dirty | 3.0 / 0.3 | 0 | 0 |
| gpt | gpt-5.6-terra | 20261104-151438-gpt-20411 | 2026-11-04T15:14:38 | 394350e-dirty, 855ad12-dirty | 3.0 / 0.3 | 0 | 0 |
| ollama/gemma4:31b-cloud | gemma4:31b-cloud | 20261104-151438-ollama_gemma4_31b-cloud-20427 | 2026-11-04T15:14:38 | 394350e-dirty, 855ad12-dirty | 3.0 / 0.3 | 0 | 0 |
| ollama/gemma4:e4b-it-qat | gemma4:e4b-it-qat | 20261104-151438-ollama_gemma4_e4b-it-qat-20435 | 2026-11-04T15:14:38 | 394350e-dirty, 855ad12-dirty | 3.0 / 0.3 | 0 | 0 |
| ollama/medgemma1.5:4b | medgemma1.5:4b | 20261104-161935-ollama_medgemma1.5_4b-40411 | 2026-11-04T16:19:36 | 394350e-dirty | 3.0 / 0.3 | 0 | 0 |
| ollama/glm-5.3-flash:cloud | glm-5.3-flash:cloud | 20261104-163208-ollama_glm-5.3-flash_cloud-44219 | 2026-11-04T16:32:08 | 394350e-dirty | 3.0 / 0.3 | 0 | 0 |
| ollama/minimax-m3:cloud | minimax-m3:cloud | 20261104-201405-ollama_minimax-m3_cloud-8124 | 2026-11-04T20:14:05 | 394350e-dirty | 3.0 / 0.3 | 0 | 0 |
| ollama/mistral-large-3:675b-cloud | mistral-large-3:675b-cloud | 20261104-205831-ollama_mistral-large-3_675b-cloud-20793 | 2026-11-04T20:58:31 | 394350e-dirty | 3.0 / 0.3 | 0 | 0 |
| ollama/kimi-k3:cloud | kimi-k3:cloud | 20261104-214356-ollama_kimi-k3_cloud-33439 | 2026-11-04T21:43:56 | 394350e-dirty | 3.0 / 0.3 | 0 | 0 |

## Primary statements

| statement | criteria met | registered minimum | result |
|---|---|---|---|
| H1a | 4 | 5 | not confirmed |
| H1b | 2 | 2 | confirmed |
| H2a | 3 | 5 | not confirmed |
| H2b | 10 | 5 | confirmed |
| H3a | 7 | 8 | not confirmed |
| H3b | 9 | 8 | confirmed |

### H1a: WN cell (file labels swapped, image normal): accuracy below 50 %

| model | estimate [95 % CI] | p (one-sided) | p Holm | criterion met |
|---|---|---|---|---|
| claude | 0 % [0–5] (0/80) | < 0.001 | < 0.001 | yes |
| gpt | 100 % [95–100] (80/80) | 1.000 | 1.000 | no |
| gemini | 100 % [95–100] (80/80) | 1.000 | 1.000 | no |
| ollama/gemma4:31b-cloud | 74 % [63–82] (59/80) | 1.000 | 1.000 | no |
| ollama/gemma4:e4b-it-qat | 0 % [0–5] (0/80) | < 0.001 | < 0.001 | yes |
| ollama/glm-5.3-flash:cloud | 76 % [66–84] (61/80) | 1.000 | 1.000 | no |
| ollama/kimi-k3:cloud | 51 % [40–62] (41/80) | 0.631 | 1.000 | no |
| ollama/medgemma1.5:4b | 1 % [0–7] (1/80) | < 0.001 | < 0.001 | yes |
| ollama/minimax-m3:cloud | 59 % [48–69] (47/80) | 0.954 | 1.000 | no |
| ollama/mistral-large-3:675b-cloud | 0 % [0–5] (0/80) | < 0.001 | < 0.001 | yes |

**H1a: 4 of 10 criteria met; registered minimum 5; NOT confirmed.**

### H1b: WN cell accuracy of gemini-3.8-flash and gpt-5.6-terra at least 90 % (test against 75 %)

| model | estimate [95 % CI] | p (one-sided) | p Holm | criterion met |
|---|---|---|---|---|
| gemini | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| gpt | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |

**H1b: 2 of 2 criteria met; registered minimum 2; CONFIRMED.**

### H2a: wrong label in the OIP file adopted on at least 50 % of images (test against 35 %)

| model | estimate [95 % CI] | p (one-sided) | p Holm | criterion met |
|---|---|---|---|---|
| claude | 45 % [35–56] (36/80) | 0.041 | 0.246 | no |
| gpt | 28 % [19–38] (22/80) | 0.939 | 1.000 | no |
| gemini | 46 % [36–57] (37/80) | 0.025 | 0.173 | no |
| ollama/gemma4:31b-cloud | 44 % [33–55] (35/80) | 0.065 | 0.327 | no |
| ollama/gemma4:e4b-it-qat | 41 % [31–52] (33/80) | 0.146 | 0.584 | no |
| ollama/glm-5.3-flash:cloud | 68 % [57–77] (54/80) | < 0.001 | < 0.001 | yes |
| ollama/kimi-k3:cloud | 51 % [40–62] (41/80) | 0.002 | 0.017 | yes |
| ollama/medgemma1.5:4b | 0 % [0–5] (0/80) | 1.000 | 1.000 | no |
| ollama/minimax-m3:cloud | 31 % [22–42] (25/80) | 0.793 | 1.000 | no |
| ollama/mistral-large-3:675b-cloud | 76 % [66–84] (61/80) | < 0.001 | < 0.001 | yes |

**H2a: 3 of 10 criteria met; registered minimum 5; NOT confirmed.**

### H2b: the OIP file is adopted less often than the plain note (exact McNemar, one-sided)

| model | adopted plain | adopted OIP | b (plain only) | c (OIP only) | p (one-sided) | p Holm | criterion met |
|---|---|---|---|---|---|---|---|
| claude | 100 % [95–100] (80/80) | 45 % [35–56] (36/80) | 44 | 0 | < 0.001 | < 0.001 | yes |
| gpt | 74 % [63–82] (59/80) | 28 % [19–38] (22/80) | 37 | 0 | < 0.001 | < 0.001 | yes |
| gemini | 79 % [69–86] (63/80) | 46 % [36–57] (37/80) | 29 | 3 | < 0.001 | < 0.001 | yes |
| ollama/gemma4:31b-cloud | 78 % [67–85] (62/80) | 44 % [33–55] (35/80) | 30 | 3 | < 0.001 | < 0.001 | yes |
| ollama/gemma4:e4b-it-qat | 84 % [74–90] (67/80) | 41 % [31–52] (33/80) | 36 | 2 | < 0.001 | < 0.001 | yes |
| ollama/glm-5.3-flash:cloud | 98 % [91–99] (78/80) | 68 % [57–77] (54/80) | 25 | 1 | < 0.001 | < 0.001 | yes |
| ollama/kimi-k3:cloud | 88 % [78–93] (70/80) | 51 % [40–62] (41/80) | 34 | 5 | < 0.001 | < 0.001 | yes |
| ollama/medgemma1.5:4b | 96 % [90–99] (77/80) | 0 % [0–5] (0/80) | 77 | 0 | < 0.001 | < 0.001 | yes |
| ollama/minimax-m3:cloud | 89 % [80–94] (71/80) | 31 % [22–42] (25/80) | 46 | 0 | < 0.001 | < 0.001 | yes |
| ollama/mistral-large-3:675b-cloud | 100 % [95–100] (80/80) | 76 % [66–84] (61/80) | 19 | 0 | < 0.001 | < 0.001 | yes |

**H2b: 10 of 10 criteria met; registered minimum 5; CONFIRMED.**

### H3a: with the full file, each of the four fact tasks at least 95 % correct (test against 80 %)

| model | task | estimate [95 % CI] | p (one-sided) | p Holm | met |
|---|---|---|---|---|---|
| claude | left_edge | 94 % [86–97] (75/80) | < 0.001 | 0.002 | no |
| claude | scale_available | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| claude | ctr | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| claude | heart_mm | 100 % [94–100] (65/65) | < 0.001 | < 0.001 | yes |
| gpt | left_edge | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| gpt | scale_available | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| gpt | ctr | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| gpt | heart_mm | 100 % [94–100] (65/65) | < 0.001 | < 0.001 | yes |
| gemini | left_edge | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| gemini | scale_available | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| gemini | ctr | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| gemini | heart_mm | 100 % [94–100] (65/65) | < 0.001 | < 0.001 | yes |
| ollama/gemma4:31b-cloud | left_edge | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/gemma4:31b-cloud | scale_available | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/gemma4:31b-cloud | ctr | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/gemma4:31b-cloud | heart_mm | 100 % [94–100] (65/65) | < 0.001 | < 0.001 | yes |
| ollama/gemma4:e4b-it-qat | left_edge | 98 % [91–99] (78/80) | < 0.001 | < 0.001 | yes |
| ollama/gemma4:e4b-it-qat | scale_available | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/gemma4:e4b-it-qat | ctr | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/gemma4:e4b-it-qat | heart_mm | 100 % [94–100] (65/65) | < 0.001 | < 0.001 | yes |
| ollama/glm-5.3-flash:cloud | left_edge | 96 % [90–99] (77/80) | < 0.001 | < 0.001 | yes |
| ollama/glm-5.3-flash:cloud | scale_available | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/glm-5.3-flash:cloud | ctr | 84 % [74–90] (67/80) | 0.247 | 0.494 | no |
| ollama/glm-5.3-flash:cloud | heart_mm | 88 % [78–94] (57/65) | 0.076 | 0.228 | no |
| ollama/kimi-k3:cloud | left_edge | 99 % [93–100] (79/80) | < 0.001 | < 0.001 | yes |
| ollama/kimi-k3:cloud | scale_available | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/kimi-k3:cloud | ctr | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/kimi-k3:cloud | heart_mm | 100 % [94–100] (65/65) | < 0.001 | < 0.001 | yes |
| ollama/medgemma1.5:4b | left_edge | 69 % [58–78] (55/80) | 0.994 | 0.994 | no |
| ollama/medgemma1.5:4b | scale_available | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/medgemma1.5:4b | ctr | 99 % [93–100] (79/80) | < 0.001 | < 0.001 | yes |
| ollama/medgemma1.5:4b | heart_mm | 100 % [94–100] (65/65) | < 0.001 | < 0.001 | yes |
| ollama/minimax-m3:cloud | left_edge | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/minimax-m3:cloud | scale_available | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/minimax-m3:cloud | ctr | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/minimax-m3:cloud | heart_mm | 100 % [94–100] (65/65) | < 0.001 | < 0.001 | yes |
| ollama/mistral-large-3:675b-cloud | left_edge | 99 % [93–100] (79/80) | < 0.001 | < 0.001 | yes |
| ollama/mistral-large-3:675b-cloud | scale_available | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/mistral-large-3:675b-cloud | ctr | 100 % [95–100] (80/80) | < 0.001 | < 0.001 | yes |
| ollama/mistral-large-3:675b-cloud | heart_mm | 100 % [94–100] (65/65) | < 0.001 | < 0.001 | yes |

**H3a: 7 of 10 models meet the criterion on all four tasks; registered minimum 8; NOT confirmed.**

### H3b: image only, scale availability below 50 %

| model | estimate [95 % CI] | p (one-sided) | p Holm | criterion met |
|---|---|---|---|---|
| claude | 19 % [12–29] (15/80) | < 0.001 | < 0.001 | yes |
| gpt | 19 % [12–29] (15/80) | < 0.001 | < 0.001 | yes |
| gemini | 15 % [9–24] (12/80) | < 0.001 | < 0.001 | yes |
| ollama/gemma4:31b-cloud | 19 % [12–29] (15/80) | < 0.001 | < 0.001 | yes |
| ollama/gemma4:e4b-it-qat | 20 % [13–30] (16/80) | < 0.001 | < 0.001 | yes |
| ollama/glm-5.3-flash:cloud | 19 % [12–29] (15/80) | < 0.001 | < 0.001 | yes |
| ollama/kimi-k3:cloud | 20 % [13–30] (16/80) | < 0.001 | < 0.001 | yes |
| ollama/medgemma1.5:4b | 81 % [71–88] (65/80) | 1.000 | 1.000 | no |
| ollama/minimax-m3:cloud | 19 % [12–29] (15/80) | < 0.001 | < 0.001 | yes |
| ollama/mistral-large-3:675b-cloud | 21 % [14–31] (17/80) | < 0.001 | < 0.001 | yes |

**H3b: 9 of 10 criteria met; registered minimum 8; CONFIRMED.**

## Secondary (descriptive, not registered as confirmatory)

| model | replies per item | four cells, rep 0/1/2 | WN rep 0/1/2 | OIP-file adoption rep 0/1/2 | conflict items identical in all repeats |
|---|---|---|---|---|---|
| claude | 3 | 50 / 50 / 50 | 0 / 0 / 0 | 45 / 44 / 48 | 100 % [99–100] (320/320) |
| gemini | 3 | 94 / 93 / 92 | 100 / 100 / 100 | 46 / 46 / 45 | 91 % [87–94] (291/320) |
| gpt | 3 | 90 / 89 / 90 | 100 / 99 / 98 | 28 / 30 / 28 | 81 % [76–85] (258/320) |
| ollama/gemma4:31b-cloud | 3 | 50 / 51 / 49 | 74 / 78 / 74 | 44 / 41 / 41 | 93 % [90–96] (299/320) |
| ollama/gemma4:e4b-it-qat | 3 | 50 / 50 / 50 | 0 / 0 / 0 | 41 / 39 / 36 | 100 % [98–100] (319/320) |
| ollama/medgemma1.5:4b | 3 | 50 / 49 / 50 | 1 / 1 / 0 | 0 / 1 / 0 | 97 % [94–98] (309/320) |
| ollama/glm-5.3-flash:cloud | 3 | 62 / 58 / 66 | 76 / 71 / 81 | 68 / 59 / 69 | 50 % [44–55] (159/320) |
| ollama/minimax-m3:cloud | 3 | 60 / 58 / 58 | 59 / 49 / 52 | 31 / 34 / 39 | 84 % [80–88] (270/320) |
| ollama/mistral-large-3:675b-cloud | 3 | 50 / 50 / 50 | 0 / 0 / 0 | 76 / 78 / 76 | 100 % [99–100] (320/320) |
| ollama/kimi-k3:cloud | 2 | 56 / 50 | 51 / 65 | 51 / – | 73 % [62–82] (57/78) |
