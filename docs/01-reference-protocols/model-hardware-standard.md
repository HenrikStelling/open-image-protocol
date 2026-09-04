# Reference protocol 3: Model Hardware Standard (MHS)

Status at time of writing (Sept 2026): **research preview**, announced by
Anthropic on 27 Aug 2026; not yet open-sourced; access by application at
modelhardwarestandard.com. Details below come from the announcement, the
launch video, and press coverage (heise, TNW, Truescho). The full spec is not
public, so some structure is inferred and flagged as such.

## 1. What problem it solves

- Labs and factories take "weeks, if not months" to integrate hardware; each
  device speaks a proprietary language; nothing talks to anything else.
- MHS = "the physical counterpart to MCP": a **standardised driver layer between
  the OS and the device, designed for control by AI agents**. Integration drops to
  "hours or minutes".

## 2. How it was developed

- Origin: collaboration between Anthropic and **HHMI Janelia Research Campus**;
  the initial concept came from Arco Bast's *shared memory dictionary* used to
  coordinate incompatible microscopy instruments.
- Research-preview partners provided real workloads: Genentech (protein assays),
  UW Baker/Pinglay labs (protein design screening), CMU (dose-response), Janelia
  (microscopy), QuEra (quantum laser stabilisation), Tetsuwan Scientific.
- Vendor partners adding support: AWS (Strands Robots), Automata, Danaher,
  Doosan Robotics, MBF Bioscience, QIAGEN, Tecan, Universal Robots, Hugging Face
  (LeRobot), Raspberry Pi.
- Process: **build with domain partners first, run safety evaluations, then open
  source**. Video framing: "a living standard", iterate, expect the model to make
  mistakes, keep a human in the loop.

## 3. How it makes unstandardised machines accessible to LLMs

Four mechanisms (this is the part that matters most for OIP):

1. **A tiny primitive set.** Everything reduces to `read` (get temperature) and
   `write` (set temperature). Devices report **state** (position, temperature) and
   **procedures** (allowed operations).
2. **Auto-generated reference file.** The driver "automatically produces a
   reference file with information about a device's general characteristics":
   measurements it can take, settings it can change, enforced safety limits.
   Authors add **natural-language tags** for physical properties (mass and reach
   of an arm, max laser power). The agent reads this file before acting.
3. **Discovery in a standard format**, so devices and agents find each other
   without a bespoke translator.
4. **Safety limits enforced in the driver, not in the model.** The "safety range
   visualiser" in the video: a command outside the safe envelope is refused by the
   protocol layer. Violations become programmable exceptions rather than things
   the model has to reason about.

Access paths: **MCP, a CLI, or code/APIs** — "any agent harness that speaks
standard protocols" can use it; model-agnostic.

## 4. Limitations Anthropic itself reports

- Models' understanding is "programmatic rather than physical": they struggle
  with physical/chemical/biological constraints and with troubleshooting hardware.
- Only devices with a programmable interface.
- Agents often ask for human confirmation near risky actions.

## 5. Transfer to OIP — the strongest analogy of the three

| MHS | OIP |
|---|---|
| Proprietary device language | Modality-specific pixel physics + 4,000-tag DICOM headers |
| Driver layer producing a reference file | Converter producing `oip.json` + `context.md` |
| `read` / `write` primitives | `describe` / `measure` / `window` / `crop` / `overlay` (read-only; there is no `write` to a patient) |
| State + procedures | Geometry/intensity state + allowed operations declared per profile |
| Natural-language tags by the device author | Natural-language `notes` by the converter/clinician ("magnification not corrected", "counts are decay-corrected") |
| Safety limits enforced in the driver | **Measurement guardrails enforced in the tool layer**: refuse to return mm when no calibrated spacing exists; refuse to compare counts across different energy windows; flag burned-in PHI |
| Three access paths (MCP / CLI / code) | Same three, plus the file package itself as a fourth (offline) path |

Key insight to carry forward: **the model should never be the component that
"knows" the physics.** MHS moved physics and safety into the driver; OIP moves
geometry, units and measurement into the converter and tool layer, and hands
the model a reference file it can trust.

Sources: `docs/04-sources.md` §MHS.
