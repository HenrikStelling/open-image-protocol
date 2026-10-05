## Readings (2026-10-02, updated 2026-10-05: all seven Ollama models and both frontier models at repeat 0; glm is being rerun — see 6; the Ollama weekly limit held 10-01 10:11 to 10-05 ~02:00)

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
6. **glm-5.3-flash needs a larger output cap than any other model.** With think=false and a 2,400-token cap, 328 of its 1,056
   round-3 replies were cut off inside the visible reasoning (142 on the canonical, 186 on the masked render, almost all in the
   three cells where something is off: TM, WN, WM), and the scorer read 'mirrored' out of 95 % of the fragments — the apparent
   'always mirrored' pattern (18 images) and the 70 % total were artefacts of truncation. Fix (commit of 2026-10-05): a reply the
   provider cut off before it closed its reasoning is scored wrong and flagged `truncated` (`run.score_row`), the cap for
   in-content reasoners is 8,000 tokens, the 2,400-cap run is set aside, and glm is rerun with three repeats. On its complete
   replies glm was right on 155/186 conflict items (83 %), with a clear selection effect (it finishes when the case is easy).

