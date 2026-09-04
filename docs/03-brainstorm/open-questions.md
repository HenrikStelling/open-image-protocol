# Open questions for the user (brainstorm backlog)

Each item: why it matters, my current default, what I need from you.

1. **Target consumer.** Are we optimising first for (a) general assistants
   (Claude/GPT/Gemini via MCP), (b) research pipelines, or (c) clinical
   integrators? Default: (a) then (b). It changes how much SR/FHIR export we do early.
2. **Clinical claims.** OIP v0 makes no diagnostic claims. Do you want the
   benchmark to include finding-level diagnosis at all, or only "understanding"
   tasks (modality, orientation, scale, measurements)? Default: both, but
   understanding tasks gate releases.
3. **Scintigraphy priority.** Bone scans (whole-body) vs thyroid vs renal vs
   cardiac? Default: whole-body bone scans (open data exists: Zenodo, BS-80K).
4. **Human notes in `context.md`.** Should clinicians be able to add free-text
   notes (like MHS natural-language tags)? Default: yes, marked `external`.
5. **Package size.** Include the full-resolution 16-bit pixels by default, or
   reference them by hash? Default: include (losslessness is a non-negotiable).
6. **De-identification depth.** Keep age band and sex? Default: yes (age in
   5-year bands). Anything finer is opt-in.
7. **Naming of the spec parts.** "layers L0–L5" vs "profiles". Default: layers
   inside the manifest, profiles = named sets of layers (`core`, `measured`, `full`).
8. **Governance.** Solo project for now; when do we open an SEP-style process
   to outside contributors? Default: at v0.2 after the first benchmark report.
9. **GitHub remote.** `gh` is not authenticated on this machine. Create the repo
   as private under your account? Command is in README §Publishing.
10. **Kaggle credentials.** Needed to re-check the scintigraphy inventory and to
    download VinDr/RSNA in Phase 2.
11. **Expert readers.** Do we have access to a radiologist / nuclear medicine
    physician for Tier-3 validation (~250 images)?
12. **Model access for the benchmark.** API keys for Claude, GPT, Gemini, and a
    GPU or hosted endpoint for MedGemma / CXR-LLaVA.
