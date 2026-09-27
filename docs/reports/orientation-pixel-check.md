# Pixel-side orientation check (`oip check` 0.1.0) on vindr-paper, n = 100

Generated 2026-09-26 12:26 by scripts/check_mirror_eval.py; packages not modified. The check compares the column centroid of the unsided heart (and aortic-arch) mask with the thoracic midline (lung-union bbox centre) and the edge labelled L; |offset| < 2% of thoracic width is indeterminate, ≥ 5% is confident. It does not use the segmentation model's left/right class labels.

| condition | consistent | inconsistent | indeterminate |
|---|---|---|---|
| stored masks, image as shipped | 98 | 0 | 2 |
| masks mirrored (geometry only) | 0 | 98 | 2 |
| canonical render mirrored, re-segmented | 5 | 71 | 24 |

Heart centroid offset toward the L edge, as shipped: min +0.015, median +0.079, max +0.146 of thoracic width (positive = toward L).
After mirroring and re-segmenting: min -0.145, median -0.053, max +0.061.

Packages where the single-pass check points the wrong way: 5: 0e5734a54830, 2271647c6cb5, 49d5b90070ca, a7c0ab62b8c6, d7163e05dad8
Indeterminate as shipped: ['061fa33f6ba0', '83bf2acb96d1']

Reading: a correct check reads consistent on the shipped image and inconsistent on the mirrored copy. The single pass under-reads the flip because the segmentation model has a positional prior: on a mirrored image the heart mask is pulled back toward the conventional side.

## Two-pass, prior-free check (default of `oip check` 0.1.0)

s = (offset on the image − offset on its mirror) / 2 cancels the model's prior p = their mean. On the shipped images: s min +0.0017, median +0.0628, max +0.1410; p min -0.0115, median +0.0078, max +0.0682.

| verdict on the shipped image (mirrored input: the same counts with consistent and inconsistent swapped) | n |
|---|---|
| consistent (correct) | 94 |
| inconsistent (wrong) | 0 |
| indeterminate (|s| < 2%) | 6 |

Weakest five (smallest s): 061fa33f6ba0, 0e5734a54830, a7c0ab62b8c6, d7163e05dad8, 2271647c6cb5.
