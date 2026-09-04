# Naming and vocabulary

- **OIP** — Open Image Protocol (the whole thing: package format + verb set + tools).
- **Package** — a `<name>.oip/` directory (or `.oip` zip) for one image or one multi-frame acquisition.
- **Manifest** — `oip.json`.
- **Reference file** — `context.md` (term borrowed from MHS).
- **Adapter** — modality-specific converter module (`dx`, `nm`, …), analogous to a language server.
- **Layer** — L0 identity/provenance, L1 geometry/intensity, L2 renders, L3 semantic, L4 measurements, L5 narrative.
- **Profile** — named set of layers a producer guarantees: `core` (L0–L2), `measured` (L0–L4), `full` (L0–L5).
- **Assertion level** — measured / computed / inferred / external / unknown.
- **Verb set** — describe, locate, measure, window, crop, overlay, validate.
- **OEP** — OIP Enhancement Proposal (see decisions log).
- **OIP-Bench** — the with/without-OIP model benchmark.
