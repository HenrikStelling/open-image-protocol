# Cross-protocol comparison and the design rules we derive for OIP

## 1. Side-by-side

| Dimension | LSP (2016) | MCP (2024) | MHS (2026) | **OIP (proposed)** |
|---|---|---|---|---|
| Problem shape | M editors × N languages | N assistants × M tools/data | N agents × M devices | N models × M modalities/vendors/formats |
| Neutral abstraction | Text document + position | Tool/resource + JSON Schema | read/write + state/procedures | **Image + physical frame (mm) + intensity semantics (units) + typed observations** |
| Self-description | Server capabilities | `tools/list` schemas + descriptions | Auto-generated reference file + NL tags | `oip.json` (schema) + `context.md` (prose reference file) |
| Discovery | `initialize` | `server/discover` | Network discovery of devices | Conformance profile + layer flags in manifest; MCP server for online discovery |
| Wire format | JSON-RPC 2.0 | JSON-RPC 2.0 | (MCP/CLI/code) | Files (JSON + PNG + Markdown); JSON-RPC via MCP when served |
| Who holds domain knowledge | Language server | MCP server | Driver | **Converter + tool layer**, never the model |
| Safety | n/a | Host approval dialogs | Limits enforced in driver | Guardrails in tools (no uncalibrated mm, no cross-window count comparison), PHI checks |
| Versioning | 3.x, additive | Date-based → moving to semver | preview | **Semver from v0.1, deprecation policy** |
| Governance | Microsoft, open spec | Linux Foundation, SEP process | Anthropic + partners | Open repo, SEP-style proposals (`docs/03-brainstorm/decisions-log.md`) |
| Launch bundle | VS Code + TS server | Spec + SDKs + servers + Claude Desktop | Partners + vendors | Spec + Python SDK + CLI + MCP server + example packages + benchmark |

## 2. How each one makes "unstandardised language" accessible to a model

All three do the same thing in different clothes:

1. **They do not translate the foreign language into the model's language at runtime.**
   They force the foreign side to *pre-describe itself* in a fixed, schema-validated
   vocabulary the model already reads (JSON Schema, capability lists, NL tags).
2. **They shrink the operation set** to a handful of verbs (hover/definition;
   tools/resources/prompts; read/write). Small verb sets are learnable zero-shot.
3. **They keep domain complexity behind the interface** (parsers, drivers, auth).
4. **They ship a reference implementation on both sides** so the standard is
   testable on day one.

## 3. Where OIP differs and must add something new

- LSP/MCP/MHS are **domain-agnostic transports of meaning**; the meaning of a
  tool is whatever its description says. For medical images that is not enough:
  a millimetre, Hounsfield unit, count, or "left" must mean the same thing for
  every producer. **OIP therefore needs a controlled vocabulary and unit model**
  (reuse DICOM, SNOMED CT, RadLex, RSNA/ACR CDEs — see Q2/Q4).
- Vision models are unreliable at *quantitative* perception (MedVision, "Your
  other Left"), and are *easily misled by text context* (MC-CXR). OIP must
  therefore (a) compute measurements outside the model and (b) label every
  statement with an **assertion level** (measured / computed / inferred / external)
  so the model can weight it.
- Images are large. OIP must define **model-ready renders** (8-bit, correct
  polarity, orientation markers, scale bar, optional set-of-mark overlays), not
  just metadata, because that is what actually enters the vision encoder.

## 4. Design rules (carry into `spec/`)

R1. **Neutral core**: every OIP package has geometry (mm), orientation, intensity units, and provenance, regardless of modality.
R2. **Self-describing twice**: machine (`oip.json`, JSON Schema) and model (`context.md`, fixed template).
R3. **Small verb set**: `describe`, `locate`, `measure`, `window`, `crop`, `overlay`, `validate`.
R4. **Physics and safety live in the tool layer**, not the model.
R5. **Assertion levels on every fact**.
R6. **Conformance profiles** so partial producers are still useful (like LSP capabilities).
R7. **Semver + deprecation policy + SEP-style change process**.
R8. **Stateless packages**: everything needed to interpret the image is in the package.
R9. **Ship the bundle**: spec, SDK, CLI, MCP server, examples, benchmark, together.
R10. **Measure uplift, not vibes**: every protocol change is evaluated on the OIP benchmark (Q1, Q13).
