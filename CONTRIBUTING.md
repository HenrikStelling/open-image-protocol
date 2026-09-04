# Contributing

1. Changes to the spec or schema go through an OIP Enhancement Proposal: add an entry to `docs/03-brainstorm/decisions-log.md` with problem, evidence, prototype, benchmark effect.
2. Code changes must keep `make test` and `make validate` green; regenerate `spec/examples` when the schema changes.
3. Never commit real patient data. `data/` is ignored except synthetic samples.
4. Commit messages: imperative subject, body explains *why*.
