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
