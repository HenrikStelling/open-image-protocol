# Contributing

1. Changes to the spec or schema go through an OIP Enhancement Proposal: add an entry to `docs/03-brainstorm/decisions-log.md` with problem, evidence, prototype, benchmark effect.
2. Code changes must keep `make test` and `make validate` green; regenerate `spec/examples` when the schema changes.
3. Never commit real patient data. `data/` is ignored except synthetic samples.
4. Commit messages: imperative subject, body explains *why*.

## macOS note
Recent CPython security releases ignore `.pth` files carrying the macOS `hidden` flag, which files created inside `.venv` inherit. `make setup` runs `chflags nohidden` on them; if `import oip` fails after a reinstall, run that again.

## Do not keep the working set inside an iCloud-synced folder
Lesson from 2026-09-08: with "Desktop & Documents" iCloud sync and "Optimize Mac Storage" on, macOS evicted files under
`~/Desktop/OIP` once free disk dropped to ~11 GB. Reads of package files and even `import torch` from the `.venv` then blocked
for minutes and failed with `[Errno 60] Operation timed out`; renaming the 15 GB store made iCloud re-process the whole tree.
Keep the clone, the virtual environment and `data/` outside iCloud (e.g. `~/oip-work`, `~/oip-venv`, `~/oip-bench`), or
exclude the folders with a `.nosync` suffix before they grow. `bench/run.py --pkg-dir` exists for running from such a copy.
