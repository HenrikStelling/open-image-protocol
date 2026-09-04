# Q13 — How do we improve the protocol based on our findings?

## The loop (borrowed from MCP's SEP process + LSP's capability model)

1. **Every proposed change is an OIP Enhancement Proposal (OEP)** in
   `docs/03-brainstorm/decisions-log.md`: problem, evidence, proposed schema/
   context change, prototype, benchmark result, migration note.
2. **Prototype before acceptance** (MCP rule): the converter/SDK implements it
   behind a profile flag.
3. **Benchmark gate**: OIP-Bench (Q1 §C) is re-run; a change is accepted only if
   it improves at least one metric without regressing others, across models.
   Field-level ablations tell us which context fields carry the uplift, so the
   default profile stays small (token cost is a metric).
4. **Conformance suite**: schema tests + phantom tests + example packages must pass.
5. **Versioning**: semver. Additive fields → minor; renamed/removed → major with a
   deprecation window of ≥ 2 minor releases (MCP 2026-07-28 lifecycle policy).
6. **Telemetry from converters** (opt-in, aggregate only): which tags were
   missing, which flags fired, per dataset/vendor → drives the next adapters.
7. **Release bundle** each minor: spec, schema, SDK, CLI, MCP server, examples,
   benchmark report, changelog.

## Feedback sources ranked by value
1. Benchmark deltas per model (objective).
2. Failure cases from the self-check block (model answered a self-check wrong → protocol or render bug).
3. Converter completeness stats per dataset.
4. Users/clinicians reviewing `context.md` wording.
5. Interop feedback (SR/FHIR export round-trips).

## What OIP does about it
Decision log and open-questions files exist; benchmark harness and telemetry are Phase 3/6 deliverables.
