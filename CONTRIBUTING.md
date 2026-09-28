# Contributing

1. Changes to the spec or schema go through an OIP Enhancement Proposal: add an entry to `docs/03-brainstorm/decisions-log.md` with problem, evidence, prototype, benchmark effect. A proposal enters the spec only with a measured benchmark result (design rule R10).
2. Code changes must keep `make test`, `make validate` and `make examples-check` green (CI runs all three); regenerate `spec/examples` when the schema or the template changes, and bump `TEMPLATE_VERSION` or the schema version accordingly.
3. Never commit real patient data, packages derived from restricted datasets, API keys or Kaggle tokens. `data/` is ignored except synthetic samples; keys live outside the clone (`~/.config/oip/keys.env`).
4. Commit messages: imperative subject, body explains *why*.
5. Scorer changes: bump `SCORER_VERSION`, add a unit test in `bench/test_score.py`, re-apply with `bench/rescore.py` (it keeps the previous score per row and writes `docs/reports/rescore-scorer-<version>.md`), and never edit a stored reply.
6. Benchmark runs: one Ollama cloud model at a time (the runner's lock enforces it); paid API models only for a like-for-like repeat of an earlier run or after a rebuild is complete (owner's cost rule, 2026-09-26). Record the run date; cloud tags are not pinned by their providers.
7. Releases: update `CHANGELOG.md` and `CITATION.cff`, tag `vX.Y.Z`, build the Zenodo bundle with `scripts/export_release_bundle.py --tag vX.Y.Z`, upload, and put the DOI into README, CITATION.cff and the paper's availability statement.

## macOS note
Recent CPython security releases ignore `.pth` files carrying the macOS `hidden` flag, which files created inside `.venv` inherit. `make setup` runs `chflags nohidden` on them; if `import oip` fails after a reinstall, run that again.

## Do not keep the working set inside an iCloud-synced folder
Lesson from 2026-09-08: with "Desktop & Documents" iCloud sync and "Optimize Mac Storage" on, macOS evicted files under
`~/Desktop/OIP` once free disk dropped to ~11 GB. Reads of package files and even `import torch` from the `.venv` then blocked
for minutes and failed with `[Errno 60] Operation timed out`; renaming the 15 GB store made iCloud re-process the whole tree.
Keep the clone, the virtual environment and `data/` outside iCloud (e.g. `~/oip-work`, `~/oip-venv`, `~/oip-bench`), or
exclude the folders with a `.nosync` suffix before they grow. `bench/run.py --pkg-dir` exists for running from such a copy.

## Ollama on Apple M5 / macOS 26 (2026-09-08)
- Local models fail to load with `ggml_metal_library_init_from_source: error compiling source` (Metal bfloat/half
  static_assert; ollama/ollama issues #15594, #15862, #15548). Workaround: `launchctl setenv GGML_METAL_TENSOR_DISABLE 1`
  and restart the Ollama app. `num_gpu: 0` (CPU only) also works but is ~10x slower.
- Ollama Cloud free tier: starter credits and **one concurrent request**; extra requests are queued (then time out /
  502 through the local daemon). Run one model at a time on Free; Pro ($20/mo, $60 credits, 3 concurrent) fits the
  benchmark's three-parallel-model layout. Retired cloud tags answer HTTP 410. Pro also rate-limits bursts: three parallel runs of ~5k-token image prompts hit sustained HTTP 429 after ~30 minutes (2026-09-08); the runner backs off 15/30/60 s and then aborts the model, and runs must be resumed (`--resume <run dir>`) one model at a time.
