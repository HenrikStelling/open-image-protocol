# Round 3a → paper: the four-cell orientation check (notes for the RA session, 2026-10-13)

Source: `docs/reports/round3a-2026-09-30.md` (tables 1–7), decision D-032. Numbers are repeat 0 unless stated; the seven
Ollama models have three replies per cell (stability in table 6, majority policies in table 7), gemini / gpt / claude one.

## What changes in the manuscript
1. **§6 Discussion, the sentence that no model checks the file against the image.** Restrict it to the open models. In the
   four-cell design (file labels true / swapped × image normal / mirrored, 82 VinDr images) gemini-3.8-flash is right on 94 %
   and gpt-5.6-terra on 91 % of the cells, and both answer "mirrored" on 100 % of the items whose file is wrong while the image
   is normal — an answer no reader of a single source can give. So the paper's flip-check result for these two (99 % / 88 %)
   was a genuine comparison; the flip check could not prove it because its true-file cells are also solved by a pixel-only
   reader. claude-sonnet-5, mistral-large-3, gemma4 e4b, MedGemma and minimax-m3 answer from the file on every image;
   gemma4:31b calls "mirrored" whenever the file names the unconventional side and never looks (a policy that scored exactly
   like "always agree" on the flip check); kimi-k3 is noise around 50 % (identical verdicts on 47 % of items over three
   replies); glm-5.3-flash compares partly (61–68 % per reply) and leans on the burned-in marker.
2. **§5 Results, a new short subsection or a paragraph in §5.6 (flip check):** the design (four cells, three policies
   separable: compare / text-only / pixel-only, plus "file vs convention"), the ten-model table (all-four-cells accuracy,
   WN cell, policy counts per image), and two controls: (a) removing the burned-in side marker changes gemini not at all
   (94 → 94 %) and gpt by 5 pp (91 → 86 %, p = 0.05, n.s. after Holm) but removes kimi's and minimax's partial detections
   (23 → 12 %, 15 → 2 %); (b) printed-label reading with balanced truth is 88–100 % for eight models (MedGemma inverts, claude
   answers the convention when labels are swapped), so label size and placement are not why open models fail (confirms
   D-030 with balanced truth).
3. **§4 Methods:** the marker-masked render (lung-union box from 15 % below its top, sides +2 % of width, bottom +3 % of height;
   82 of 85 clear-cue packages marker-free by visual review, 3 excluded) and the majority-of-three rule for per-image policies.
4. **§7 Limitations:** three replies per cell were collected for the open models only (frontier single replies, cost); glm's
   visible reasoning exceeds an 8,000-token cap on 14 % of conflict items (counted as no answer); the mask review is an
   assistant's visual pass, not a radiologist's.
5. **Abstract / title:** "…but not the check against the pixels" needs the qualifier "in the open models"; two frontier models do
   perform the check. Suggested: "…supply the facts vision-language models cannot see; only two of ten models check them
   against the pixels".

## Table for §5 (all four cells, repeat 0; policy counts of 82 images)
| model | four cells | WN | compares / single source / other | mask effect |
|---|---|---|---|---|
| gemini-3.8-flash | 94 % | 100 % | 64 / 2 / 16 | 0 pp |
| gpt-5.6-terra | 91 % | 100 % | 55 / 4 / 23 | −5 pp (n.s.) |
| glm-5.3-flash | 68 % | 82 % | 13 / 2 / 67 | −9 pp (p = 0.005, Holm 0.05) |
| minimax-m3 | 54 % | 26 % | 2 / 48 / 28 | −6 pp (removes its detections) |
| kimi-k3 | 53 % | 48 % | 5 / 34 / 43 | −2 pp (removes its detections) |
| gemma4:31b | 50 % | 96 % | 0 / 76 / 6 | 0 |
| claude-sonnet-5 | 50 % | 0 % | 0 / 82 / 0 | 0 |
| mistral-large-3 | 50 % | 0 % | 0 / 82 / 0 | 0 |
| gemma4 e4b | 50 % | 0 % | 0 / 82 / 0 | 0 |
| MedGemma 1.5 4B | 51 % | 2 % | 0 / 73 / 9 | 0 |
"single source" = text only + pixels only + file vs convention + always mirrored. Chance for the four-cell total is 50 % under
every single-source policy.

## Repeats (added 2026-10-16)
All ten models now have three replies per cell. Majority-of-three policies (table 7): gemini 'compares' 59/82, gpt 64/82
(canonical) and 56/82 (masked), glm 9/82, every other model 0. Stability (identical verdict on all three replies, conflict
items): claude, mistral, e4b 100 %; gemma4:31b, MedGemma 96 %; gemini 89 %; gpt 82 %; minimax 69 %; glm 56 %; kimi 47 %.
gpt's marker effect is −5 pp in each of the three repeats (91/89/90 → 86/85/84 %); gemini's accuracy drifts 94 → 90 → 88 %
across identical repeats (unpinned snapshot caveat for §7).

## Not for this revision
The current paper keeps its numbers and its flip-check table; these results are a round-3 addition (v2 or the second paper,
PLAN Phase 3b "Paper"). What the current revision can take is the one-sentence qualifier in §6 and the title/abstract wording.
