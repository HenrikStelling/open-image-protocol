## Readings (2026-10-02, updated 2026-10-05 with kimi complete; minimax, mistral, glm pending behind the Ollama weekly limit that held 10-01 10:11 to 10-05 ~02:00)

1. **Two models compare the file with the image; four never look at the pixels for this question.** gemini-3.8-flash is right on
   94 % of the four cells and classified as "compares" on 64/82 images, gpt-5.6-terra on 91 % and 55/82. The decisive cell is
   WN (file labels swapped, image normal): both say "mirrored" on 100 %, which no pixel-only or text-only reader can do. gemma4:31b
   (76/82), gemma4:e4b (82/82), MedGemma (73/82) follow a single source: e4b and MedGemma always agree with the file, gemma4:31b
   calls "mirrored" whenever the FILE names the unconventional side, whatever the image shows — a policy that scored exactly like
   "always agree" on the paper's flip check (true-file cells only) and is only now separable. kimi is mixed (43/82 images fit no
   policy; 53 % overall).
2. **The burned-in side marker matters only for the partial readers.** Masking it moves gemini not at all (94 → 94 %, 8/8
   discordant) and gpt by 5 points (91 → 86 %, 38/22, p = 0.05, Holm 0.31): both read anatomy, gpt leans on the marker a little.
   kimi's detections of mirrored images under a true file fall from 23 to 12 % and its "always agree" images rise from 15 to 34,
   i.e. the partial pass the paper recorded for kimi (64 % flip check) rested on the marker. For the three single-source models
   the mask changes nothing, as expected.
3. **Reading the printed edge labels is solved for five of six models** (90–100 %, labels as shipped and swapped, truth balanced; kimi 100 / 80 %),
   so label size and placement (OEP-005, D-030) are not where the open models fail. MedGemma reads the label and answers the
   opposite side on 100 % of the shipped-label items and 2 % of the swapped ones: a consistent inversion, not noise.
4. **Mark side has no leak problem for the models that can do it.** Without the region list gemini 99 %, gpt 99 %, gemma4:31b 98 %,
   kimi 98 %; e4b stays at chance (49 %) and MedGemma significantly below it (22 %, p = 2e-8, the same inversion as in 3). The
   paper's annotated-render cells therefore did not depend on the region names for the capable models.
5. **Consequences.** (a) The paper's flip-check result for gemini (99 %) and gpt (88 %) is confirmed as a genuine comparison of
   file and pixels; the sentence that no model checks the file against the image must be restricted to the open models.
   (b) The conflict design (four cells) replaces the flip check in round 3: it is the only form in which "checks" is testable.
   (c) The masked render is the right default for anatomy-only orientation items; it costs the comparing models nothing.
   (d) The repeat pass (`--repeats 3`) is still to run; all numbers above are single replies.
