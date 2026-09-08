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

Failure notes: a retired Ollama cloud tag answers `HTTP Error 410: Gone` on every call (seen with `qwen3-vl:235b-cloud`, 2026-09-08); the runner now aborts a model after 5 consecutive identical errors. Reasoning models need a large `num_predict` or `--ollama-think off`, otherwise the answer is consumed by thinking and `content` comes back empty.
