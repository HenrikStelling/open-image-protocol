## Readings (final, 2026-10-13: seven Ollama models with three replies per cell, gemini / gpt / claude-sonnet-5 with one; 10 models × 1,056 items; Ollama weekly limits held 10-01→10-05 and 10-07→10-12, the Mac rebooted 10-08)

1. **Two models compare the file with the image; four never look at the pixels for this question.** gemini-3.8-flash is right on
   94 % of the four cells and classified as "compares" on 64/82 images, gpt-5.6-terra on 91 % and 55/82. The decisive cell is
   WN (file labels swapped, image normal): both say "mirrored" on 100 %, which no pixel-only or text-only reader can do. gemma4:31b
   (76/82), gemma4:e4b (82/82), MedGemma (73/82) follow a single source: e4b and MedGemma always agree with the file, gemma4:31b
   calls "mirrored" whenever the FILE names the unconventional side, whatever the image shows — a policy that scored exactly like
   "always agree" on the paper's flip check (true-file cells only) and is only now separable. kimi is mixed (43/82 images fit no
   policy; 53 % overall), minimax mostly 'always agree' (43/82, 54 %), mistral-large-3 'always agree' on 82/82.
2. **The burned-in side marker matters only for the partial readers.** Masking it moves gemini not at all (94 → 94 %, 8/8
   discordant) and gpt by 5 points (91 → 86 %, 38/22, p = 0.05, Holm 0.31): both read anatomy, gpt leans on the marker a little.
   kimi's detections of mirrored images under a true file fall from 23 to 12 % and its "always agree" images rise from 15 to 34,
   i.e. the partial pass the paper recorded for kimi (64 % flip check) rested on the marker. minimax-m3 the same, more sharply:
   mirrored detections under a true file 15 → 2 %, 'always agree' images 43 → 62 of 82, overall 54 → 48 % (42/22 discordant,
   p = 0.017, Holm 0.12). For the three single-source models the mask changes nothing, as expected.
3. **Reading the printed edge labels is solved for five of six models** (88–100 %, labels as shipped and swapped, truth balanced; kimi 100 / 80 %, minimax 93 / 84 %; glm 100 / 90 %). mistral answers 'patient left' for the left edge almost regardless of the labels (27 % as shipped, 100 % swapped), the lexical echo of the question rather than a reading,
   so label size and placement (OEP-005, D-030) are not where the open models fail. MedGemma reads the label and answers the
   opposite side on 100 % of the shipped-label items and 2 % of the swapped ones: a consistent inversion, not noise.
4. **Mark side has no leak problem for the models that can do it.** Without the region list gemini 99 %, gpt 99 %, gemma4:31b 98 %,
   kimi 98 %, minimax 84 % (87 % with it), glm 97 % (91 % with it); mistral is the one model that needs the names: 91 % with the region list, 80 % without (13/2, p = 0.007); e4b stays at chance (49 %) and MedGemma significantly below it (22 %, p = 2e-8, the same inversion as in 3). The
   paper's annotated-render cells therefore did not depend on the region names for the capable models.
5. **Consequences.** (a) The paper's flip-check result for gemini (99 %) and gpt (88 %) is confirmed as a genuine comparison of
   file and pixels; the sentence that no model checks the file against the image must be restricted to the open models.
   (b) The conflict design (four cells) replaces the flip check in round 3: it is the only form in which "checks" is testable.
   (c) The masked render is the right default for anatomy-only orientation items; it costs the comparing models nothing.
   (d) The repeat pass (`--repeats 3`) is still to run; all numbers above are single replies.
6. **glm-5.3-flash, rerun with an 8,000-token cap (repeat 0 complete 2026-10-05 14:10): the one open model that partly
   compares, and the one that uses the marker most.** With the 2,400-token cap of the first run 328/1,056 replies were cut off
   inside the visible reasoning and the scorer read 'mirrored' out of 95 % of the fragments (an apparent 'always mirrored'
   pattern); that run is set aside, and a reply cut off before it closes its reasoning now counts as no answer
   (`run.score_row`, flag `truncated`). At 8,000 tokens 149/1,052 replies are still cut off, 88 of them in the WM cell (wrong
   file and mirrored image, the only cell where both sources are off): glm deliberates for up to 34,000 characters about the
   burned-in marker, the file and the display convention and never concludes. Complete replies: TN 79 %, TM 99 %, WN 96 %, WM
   51 % (canonical); all four cells 68 % canonical, 59 % masked. Per image: 12 'compares', 66 mixed. The mask costs 9 points
   (76/45 discordant, p = 0.006, Holm 0.055), i.e. glm's partial comparison leans on the marker more than gpt's does. Reading
   labels 100 / 92 %, mark side 95 / 93 %.
7. **Stability across three replies (Ollama models; table 6) separates rule-followers from coin-flippers.** Identical verdict
   on all three replies, conflict items canonical / masked: mistral 100 / 100 %, e4b 100 / 100 %, gemma4:31b 96 / 96 %,
   MedGemma 96 / 96 %, minimax 69 / 85 %, glm 56 / 43 %, kimi 47 / 56 %. The four single-source models apply their rule
   every time; kimi's 53 % and minimax's 54 % are sampling noise around 50 % (accuracy per repeat 48–55 %), and glm's
   partial comparison is real but unstable (68 → 64 → 61 % per repeat on the canonical render, the mask cost in every
   repeat). Label reading and mark side are stable for every model that can do them (84–100 % identical).
8. **Policy per image from the majority of three replies (table 7)** removes the spurious 'other' category for the rule
   followers (gemma4:31b 76/82 'file vs convention', e4b / MedGemma / mistral 82/82 'always agree', minimax 55 → 76/82
   'always agree' on the masked render) and leaves kimi (43/82 'other') and glm (70/82) where single replies had them: for
   those two the four cells do not combine into any stable policy on most images. gemini and gpt have single replies.
9. **Claude-sonnet-5 (run by the other session, 2026-10-05):** text-only policy on 82/82 images, like mistral and the small
   models; and it reads the printed labels as shipped (100 %) but answers the convention when they are swapped (47 %), i.e. it
   does not read labels at all. mark side 93 / 91 %.

**Verdict of round 3a.** Of ten models, two compare the reference file with the pixels (gemini 94 %, gpt 91 % on the four
conflict cells; WN cell 100 % for both), one does so partly and unstably (glm 61–68 %, leaning on the burned-in marker),
and seven follow a single source on every image — the file (claude, mistral, e4b, MedGemma, minimax), the file against the
display convention (gemma4:31b) or noise (kimi). The paper's flip check (true-file cells only) could not separate the
single-source policies from comparison; the four-cell design can, and it replaces the flip check from round 3 on. The
burned-in side marker carried kimi's and minimax's apparent partial passes and part of glm's; the marker-masked render is
the default for anatomy-only orientation items (it costs the comparing models nothing). Printed-label reading is solved
for eight of ten models (the mark_side leak was irrelevant for every capable model but mistral), so the open models' failure
is the check itself, not the rendering (D-030 confirmed with balanced truth). Three replies per cell are needed before any
per-image policy is reported for a model whose cell accuracies sit near 50 %.

