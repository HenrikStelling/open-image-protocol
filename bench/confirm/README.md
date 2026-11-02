# Confirmatory round (pre-registered)

Tooling for the pre-registered confirmatory replication of the Lancet revision. The registration text is
`docs/paper/preregistration-draft-2026-11-02.md`; everything here is frozen at the commit named in its section 4.7 and must not
change after the OSF registration.

| file | role |
|---|---|
| `draw_set.py` | draws the fresh image set (rule and seed in the registration, section 4.1), stages it to `~/oip-bench/vindr-confirm/` (reserve to `vindr-confirm-reserve/`), writes `confirm_set.json` with the sha256 list; `--verify` recomputes the hashes before the run |
| `confirm_set.json` | the registered image list: VinDr image ids, source DICOM hash, hashes of manifest, canonical render and masks, the exclusion list, the draw counts (written by `draw_set.py`; attached to the OSF registration) |
| `analyze.py` | the frozen primary analysis (rep 0, per-model exact tests, Holm, registered minimum counts) and the descriptive secondary table; writes `docs/reports/confirmatory-<date>.md` |

Order of operations (registration section 7): approve the text → mount the external SSD and draw → commit and tag → register on OSF
→ owner releases the API cost → run rep 0 for all ten lanes, then repeats 1–2 → analyze. No model call before the registration.

```
python bench/confirm/draw_set.py --store "/Volumes/Video Storage/oip/oip-packages/vindr"
python bench/confirm/draw_set.py --verify
python bench/run.py --dataset vindr --pkg-dir ~/oip-bench/vindr-confirm --n 80 --seed 0 --conditions raw,ctx,misled_plain,misled_oip --tasks left_edge,scale_available,ctr,heart_mm,orient_conflict,findings_misled --repeats 3 --ollama-think auto --label "confirm:2026-11" --models <lane>
python bench/confirm/analyze.py --label confirm:
```

Draw of 2026-11-02: store 1,000; 122 excluded as used before (100 paper, 19 pilot and smoke, 3 reader-study practice); 150 without
a clear cardiac cue; 728 eligible; 80 + 10 reserve drawn with seed 20261105; 65 of 80 carry a header pixel spacing; `--verify` OK.

`analyze.py` was dry-run on the exploratory data before registration (round 3a directories with `--conflict-condition ctx3`:
H1a 5 of 10, H1b 2 of 2, matching table 1 of `docs/reports/round3a-2026-09-30.md`; repeat-subset directories: all ten models
load, H2a 5 of 10 on 20 images). Its thresholds are constants at the top of the file and mirror the registration.
