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
