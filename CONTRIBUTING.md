# Contributing

1. Changes to the spec or schema go through an OIP Enhancement Proposal: add an entry to `docs/03-brainstorm/decisions-log.md` with problem, evidence, prototype, benchmark effect.
2. Code changes must keep `make test` and `make validate` green; regenerate `spec/examples` when the schema changes.
3. Never commit real patient data. `data/` is ignored except synthetic samples.
4. Commit messages: imperative subject, body explains *why*.

## macOS note
Recent CPython security releases ignore `.pth` files carrying the macOS `hidden` flag, which files created inside `.venv` inherit. `make setup` runs `chflags nohidden` on them; if `import oip` fails after a reinstall, run that again.
