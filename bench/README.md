# OIP-Bench (Phase 3)

Measures whether an OIP package helps a vision-language model understand an image, zero-shot, versus the raw image.

- `tasks.py` — builds the task set from converted packages: ground truth comes from the manifest (modality, view, edge labels,
  scale availability, CTR, mm widths) and from dataset labels (findings, `external`). Understanding tasks gate releases (D-015);
  finding-level tasks are reported only.
- `run.py` — runs conditions × models × tasks, stores raw responses in `bench/results/<run>/`, scores them.
  Conditions: `raw` (canonical PNG only), `ctx` (canonical PNG + context.md), `annot` (annotated PNG + context.md),
  `misled_plain` / `misled_oip` (a wrong finding label given as a bare 'prior report note' vs inside context.md's External
  section; the gap in adoption rate is the protocol's contribution against misleading text — MC-CXR recipe).
  Models: `claude` / `gpt` / `gemini` via env keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`), or any Ollama model as
  `ollama/<tag>` through the local daemon (e.g. `ollama/minimax-m3:cloud`, `ollama/gemma4:26b-cloud`, `ollama/glm-5.3-flash:cloud`);
  cloud tags need `ollama signin`, no key. Pilot phase runs on Ollama (D-026); frontier providers afterwards. `--dry-run` builds prompts and estimates tokens only.
- `score.py` — per task type: exact match (modality, view, side), tolerance (scale/CTR within ±10 %), F1 (findings), switch rate (misleading context).

Failure notes: a retired Ollama cloud tag answers `HTTP Error 410: Gone` on every call (seen with `qwen3-vl:235b-cloud`, 2026-09-08); the runner now aborts a model after 5 consecutive identical errors. Reasoning models need a large `num_predict` or `--ollama-think off`, otherwise the answer is consumed by thinking and `content` comes back empty. Since round 3 (2026-09-30) `--ollama-think auto` is the default: think=false for every model (the paper setting) and a 2,400-token output cap for models that reason inside `content` regardless (glm-5.3-flash), whose reasoning was cut off at 800 tokens in up to 57/82 replies of a paper cell; `on` sends think=true with a 4,000-token cap (on glm a different, much longer operating mode), `off` reproduces the paper runs. Every row records `usage.done_reason` (`length` = cut off), `num_predict` and `think`.

## No-leakage rule (learned 2026-09-08)
Benchmark packages must not contain any information derived from the evaluation labels. The first pilot attached VinDr
radiologist boxes whose measurement names carried the finding class ("Long axis of box F1 (Aortic enlargement)") into
`context.md`, inflating findings F1 from 0.62 to 0.93. Pilot packages are now generated with `convert` + `measure_chest`
only (anatomy regions, CTR, mm widths), and a keyword leak check runs after generation. Understanding-task results from
that first run stand (they do not depend on boxes): gemma4 e4b raw 61 % → ctx 99 % → annot 99 % (n = 118 gating items).

## One cloud model at a time (2026-09-28)
`bench/run.py` takes an exclusive file lock (`~/.config/oip/ollama-cloud.lock`, `bench/cloudlock.py`) before it starts an
Ollama cloud model and holds it until that model's rows are done; a second runner, from any lane or any Claude session, waits
at the lock and prints who holds it. Local models and the API providers do not take the lock. `--no-cloud-lock` skips it
(diagnostics only). Reason: on Ollama Pro two concurrent cloud lanes reach the daily usage limit faster and the runs abort
into each other's back-off (2026-09-27).

## Round 3 (2026-09-30): conditions, repeats, provenance
- `ctx3` / `ctx3_mask`: full file as shipped (template 0.2.1) with the canonical render or the **marker-masked** render (`run.mask_box`, `run._masked`; cache in `bench/results/_render_cache`). Used by `orient_conflict` (four cells per image). Packages whose masked render still shows a side marker are listed in `bench/marker_review.json` and get no round-3 conflict items.
- `labels3`: annotated render only, printed edge labels as shipped or swapped (`badge_read`, truth follows the printed labels, 50/50).
- `annot3` / `annot3_l1`: annotated render with the full file or the L0–L2 file (`mark_side` with and without the region list that names the side).
- `--repeats N`: N replies per (model, condition, task); rows carry `rep`; `--resume <dir> --repeats N` adds missing replies. Replies are collected repeat by repeat.
- Every row: `tasks_version`, `prompt_sha256` (system prompt, user text, image bytes), `reply_sha256`, `harness_commit`, `scorer`. `run_meta.json`: `tasks_version`, `thresholds`, `repeats`, `ollama_think`.
- Readout: `python bench/round3_report.py --out docs/reports/round3a-<date>.md`.

## Local daemon settings (2026-10-16)
The Metal workaround `launchctl setenv GGML_METAL_TENSOR_DISABLE 1` (set 2026-09-08 for garbled local output on Ollama 0.33) is no
longer used: a controlled comparison under Ollama 0.40.1 (`bench/runtime_report.py`, `docs/reports/runtime-2026-10-16.md`) found no
difference in any benchmark cell and no garbled replies without it. Every run records the daemon's value of that variable
(`run_meta.json` → `ollama_env`) and the daemon version (`ollama_version`), so a future kernel change is traceable. Note for anyone
relaunching the menubar app from a shell: `open -a Ollama` hands the shell's environment to the app, so launch it from
Launchpad/Spotlight (or log in afresh) to get a clean daemon environment.

## Repeat subset: run-to-run reliability (B7, 2026-10-24)
Answer to the reviewer point "one reply per cell in the paper run": the main-result cells were re-run with three replies per
item on a fixed subset. Design: 20 VinDr paper packages (`--pkg-dir ~/oip-bench/vindr-paper --n 20 --seed 0`, the subset of
the runtime experiment), conditions `raw, ctx, misled_plain, misled_oip`, tasks `left_edge, scale_available, ctr, heart_mm,
flip_check, findings_misled`, `--repeats 3 --ollama-think auto --label b7:repeat_subset`; 136 items per repeat (76 in `raw`,
which has no flip check), 696 replies per model. Seven Ollama models (five cloud, two local) ran on 2026-10-24 in two lanes
(cloud models one at a time under the cloud lock; one HTTP 500 row refilled with `--resume`); claude (claude-sonnet-5) ran on
2026-10-31 (696 replies in 18 min, 0 errors; 43k uncached + 2.19M cached input tokens, 4.5k output tokens, about US$0.60 at list
price thanks to prompt caching of the shared prefix); gpt and gemini follow when released. Readout: `python bench/repeat_report.py` → `docs/reports/repeat-subset-<date>.md` (accuracy
per repeat, range, share of items with the same verdict in every repeat, Fleiss' kappa, and the paper run's single reply on
the same items re-scored with the current scorer). Caveat for the paper comparison: the packages carry the CheXmask
cross-check table and template 0.2.1 since 2026-10-17, so the full-file prompt is not byte-identical to the paper's.

Reading of the 2026-10-24 run (`docs/reports/repeat-subset-2026-10-24.md`, 77 cells, 4,872 replies, 0 errors; claude added
2026-10-31, 88 cells, 5,568 replies):
- The full-file fact cells behind the paper's first result (left edge, scale, CTR, cardiac width) gave the same verdict on
  every item in every repeat for six of eight models (claude included: every full-file cell, the flip check at 48 % and the
  plain-note adoption at 100 % identical across repeats; its largest spread is image-only cardiac width, 44–56 %). Exceptions: glm-5.3-flash, whose visible reasoning is cut off, varied
  on CTR (70–95 %) and cardiac width (75–94 %); medgemma1.5 varied on the left edge (65–85 %).
- The flip check was stable for the six models that always agree (same verdict on 90–100 % of items, 50 % accuracy in every
  repeat); glm (72–85 %) and kimi-k3 (48–62 %) varied.
- The image-only CTR and cardiac-width cells varied by 10–25 pp between repeats for five of eight models (mistral-large-3
  0 pp, medgemma 6–10 pp, claude 5–12 pp), with only 25–75 % of items keeping their verdict: 3–4 of 16–20 items move from one run to the next.
- Wrong-label adoption was stable (≥ 85 % of items) for gemma4:31b, mistral-large-3 and medgemma; it varied for kimi-k3
  (misled_oip 75 → 60 → 40 %), gemma4:e4b (35–50 %) and minimax-m3 (40–55 % of items stable).
- The paper run's single reply lay outside the range of the three repeats in 16 of 77 Ollama cells (claude: 1 of 11, image-only
  CTR 65 % vs 70–75 %), by more than 10 pp in six, all
  image-only size or scale cells (glm cardiac width, kimi CTR, minimax CTR, gemma4:e4b scale) or gemma4:e4b's wrong-label
  cells (misled_oip 80 % in the paper against 35–50 % now; the cell most exposed to the changed full-file prompt).
Consequence for the manuscript: a single reply is enough for the full-file fact cells and for the flip check of the models
at chance; image-only size cells and wrong-label adoption of the mid-sized models carry a run-to-run spread of 3–4 items in
20, which the Limitations should state with these numbers.

## Misleading-label draw (B5, 2026-10-23)
The wrong label of `misled_plain` / `misled_oip` is drawn per image from the labels the image does not carry. In the paper
run (harness 050769a, replies 2026-09-08 to 2026-09-22) `tasks.py` seeded that draw with Python's per-process string
`hash()`, which is salted per interpreter: the labels are identical across the two arms within one run (one model), differ
between models, and cannot be regenerated from the seed. They are not lost: every run directory stores its task set in
`tasks.json` with the drawn `misleading_label` per item, and the frozen bundle ships those files. Since round 3 (commit
a116105, 2026-09-30) the draw is seeded with sha256 of the package name (`tasks.py`), so new runs are reproducible across
processes and models. Adoption is therefore compared within a model only (both arms share the label), never between
models.

## Model identity and drift (B6, 2026-10-23)
Cloud and API models are not pinned by their providers. What the harness records so that drift can be read from the data:
every row carries `model_id` (the exact tag or API model name) and `provider`; `run_meta.json` carries `started` (run start),
`harness_commit`, `ollama_version`, `ollama_env`, `tasks_version`, `thresholds`, `repeats` and `argv`. Two Ollama cloud tags
were retired (HTTP 410) during the project: `qwen3-vl:235b-cloud` on 2026-09-08, before the paper run, so it is not in the
roster; `qwen3.5:cloud` on 2026-09-25, after the paper run and before round 3, so its paper rows stand and round 3 has
none (10 models). Observed drift under identical prompts: gemini's four-cell conflict accuracy 94 → 90 → 88 % across three
repeats; gpt's NIH-50 image-only CTR 24 % in a same-protocol repeat against 34 % in the paper run. Report model tags with
their run dates (`started`) rather than as fixed versions.

## Package stores changed on 2026-10-17 (CheXmask cross-check)
All 150 paper packages (`vindr-paper`, `nih-paper`) carry `validation_status: cross_checked` with a `cross_check` record on `ctr`,
`heart_width`, `thorax_width`, and their `context.md` was re-rendered with template 0.2.1. Any run with a full reference file made
after this date sends a measurements table that names CheXmask, n, CCC and bias — a different prompt from the paper runs
(prompt hashes differ). The paper-era manifests and reference files are in `~/oip-bench/_backup/<store>/<package>/`.
