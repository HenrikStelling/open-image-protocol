# Reader study: human reference reading (Lancet revision, 2026-11)

Blind reading of the benchmark images by specialists, replacing the package-derived truths for side, CTR and cardiac width
with a human reference and the assistant's visual check of the marker-masked renders with a specialist read. Protocol and
measurement definitions (German, for the readers and the OSF pre-registration): `PROTOKOLL.md`. No model calls.

## Files

| File | Role |
|---|---|
| `build_set.py` | draws the reading set from the package stores, writes `items.json`, `set_key.json`, `reader.html`, links the renders under `set/` |
| `reader_template.html` | the sheet (German UI); `build_set.py` inlines the item list into `reader.html` |
| `serve.py` | local server (127.0.0.1): serves the sheet and appends every answer to `readings/<reader_id>.csv` |
| `collect.py` | merges the readers' files (latest revision per reader, item, task), adds `heart_mm` from the header spacing, prints counts |
| `items.json` | the blinded item list: block, image file, size, sha256 of the image (committed: the sha256 list for the pre-registration) |
| `set_key.json` | the key: pixel spacing, edge labels, view, hot side, package measurements, package path (committed and public, like the package values in the Zenodo bundle; the blinding is procedural, `PROTOKOLL.md` section 2: readers are not pointed to it, the sheet shows no item id, readers attest after the reading) |
| `set/` | the renders, symlinks into `~/oip-bench` (git-ignored: VinDr-CXR is not redistributed) |
| `readings/` | the readers' CSV files (git-ignored until the study is frozen; then published with the data bundle) |

## Run

```
python bench/reader/build_set.py          # once; --copy makes a portable folder instead of symlinks
python bench/reader/serve.py              # then open http://127.0.0.1:8765/reader.html
python bench/reader/collect.py            # after the reading: docs/reports/reader-readings-<date>.csv
```

Set composition (seed 20261102, same order for every reader): practice 3 VinDr packages outside the paper set
(`~/oip-bench/vindr-practice`: staged 2026-11-02 from the 1,000-package store, never used in a run, not in the confirmatory set
or its reserve, taken from the packages without a clear cardiac cue so that the confirmatory draw's pool is unchanged); A side 150 (vindr-paper 100 + nih-paper 50); B ctr 100 VinDr; C marker 82 VinDr
(the conflict-trial set: clear cardiac cue and not excluded by `bench/marker_review.json`), shown as the marker-masked render
from `run._masked`; D ctr_nih 50; E scint 40 bone scans; F hot the 8 bone scans with a clear left/right count asymmetry
(`tasks_nm.build_nm`). The 82 conflict-trial packages and the 82 packages with a header pixel spacing are different sets
(overlap 68).

## Blinding

The sheet shows the canonical render only, the same file the models received, at the source pixel grid (the canonical render
is never resampled; `collect.py` asserts it). It holds no truth, no spacing, no segmentation, no model reply. Measurements
are recorded in image pixels; mm are computed afterwards in `collect.py` from the header spacing of the 82 VinDr packages
that have one. The bone-scan view is not shown: the reader names it (anterior/posterior) before the side question.

## CSV schema (`readings/<reader_id>.csv`, append-only, one row per saved revision)

| Column | Meaning |
|---|---|
| `ts_utc` | save time (ISO 8601) |
| `reader_id`, `role` | reader pseudonym (R1, R2, R3, NM1); radiology or nuclear |
| `block`, `item_id`, `dataset` | block key (practice, side, ctr, marker, ctr_nih, scint, hot); package id; vindr, nih, bonescan, vindr-extra |
| `task` | side, ctr, marker, scint_view, scint_side, scint_hot |
| `revision` | 1, 2, … per (reader, item, task); the analysis takes the highest |
| `answer` | side/scint_side: `image_left` or `image_right` = the image edge that shows the patient's right; marker: yes/no/unsure; scint_view: anterior/posterior/unsure; scint_hot: image_left/image_right/none; `na` when not assessable |
| `basis` | side tasks: anatomy, marker, both |
| `heart_x1..y2`, `heart_px` | the two cardiac-border points (image pixels) and their horizontal distance |
| `thorax_x1..y2`, `thorax_px` | the two inner rib-margin points and their horizontal distance |
| `ctr` | heart_px / thorax_px |
| `ap_projection` | 1 when the reader flagged an AP view (ctr task only) |
| `marker_x`, `marker_y`, `marker_quadrant` | clicked marker position and its quadrant |
| `not_assessable`, `unsure`, `comment` | flags and free text |
| `secs` | seconds the item had been open when this revision was saved |
| `image_w`, `image_h`, `image_sha256` | the shown image, for the audit trail |
| `tool_version` | `reader-0.1` |

`collect.py` adds `heart_mm` (heart_px × column spacing, header spacing only) and `spacing_source`.

## What the readers never see

`set_key.json`, `bench/results/`, the packages, the other reader's file. The practice block is not analysed. Corrections are
made only by the reader, in the sheet, as a new revision (the append-only file keeps the history).
