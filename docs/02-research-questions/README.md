# Research questions — index

Each file answers one of the 13 questions from the project brief, states the
evidence, and ends with **"What OIP does about it"** so the answer feeds the
spec and plan directly.

| # | Question | File | Status |
|---|---|---|---|
| 1 | What features and performance metrics do we need? | [q01](q01-features-and-metrics.md) | answered, metrics to be instrumented in Phase 3 |
| 2 | Comparable file formats / standards to use as reference? | [q02](q02-comparable-standards.md) | answered |
| 3 | How do LLMs understand DICOM today? | [q03](q03-how-llms-understand-dicom.md) | answered |
| 4 | What does DICOM contain, what is missing? | [q04](q04-dicom-contents-and-gaps.md) | answered (tag-level) |
| 5 | How to extract info from X-ray / scintigraphy so AI understands it? | [q05](q05-extracting-info-xray-scintigraphy.md) | answered, pipeline in `src/oip` |
| 6 | How to extract measurements, modality and metrics? | [q06](q06-measurements-modality-metrics.md) | answered |
| 7 | What reference data do we need / have? | [q07](q07-reference-data-needs.md) | answered |
| 8 | Is Kaggle enough for X-ray and scintigraphy? | [q08](q08-kaggle-data-inventory.md) | X-ray: yes. Scintigraphy: **no** (mitigation listed) |
| 9 | How do we access reference data? | [q09](q09-data-access.md) | answered, script stub |
| 10 | How to convert into one standardized format? | [q10](q10-conversion-pipeline.md) | answered, implemented v0 |
| 11 | How to validate measurements? | [q11](q11-validation.md) | answered, phantom test implemented |
| 12 | How does any vision model understand it without training? | [q12](q12-model-agnostic-understanding.md) | answered (design), to be measured |
| 13 | How do we improve the protocol from findings? | [q13](q13-protocol-improvement-loop.md) | answered (process) |
