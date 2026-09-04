# Q7 — What reference data do we need / have to train (and test) AI understanding?

Important framing: OIP's promise is *zero-shot understanding by any capable
model*. We therefore need reference data primarily to **validate the converter,
the measurement tools and the benchmark**, and only secondarily to train
auxiliary models (segmentation, region templates). We do not plan to train a
foundation VLM.

## Needs by purpose

| Purpose | Data requirement | Have (see Q8) | Gap |
|---|---|---|---|
| Converter correctness (tags → manifest) | Real DICOM from many vendors, both CR and DX, MONOCHROME1 and 2, with/without VOI LUT | RSNA Pneumonia, VinDr-CXR, SIIM-ACR (Kaggle, DICOM) | NM DICOM with full NM module: **not on Kaggle** |
| Scale/measurement validation | Images with known pixel spacing + expert measurements or masks | VinDr (spacing in DICOM), CheXmask (PhysioNet, masks for 657k CXRs from 5 datasets), NIH CSV spacing | Expert CTR labels (need a small expert-annotated subset, ~200 images) |
| Anatomy models | Masks for lungs/heart; NM skeletal regions | CheXmask, CXAS pseudo-labels; BS-80K (bone scans, 82k images, annotations) | NM region masks are sparse |
| OIP-Bench (model understanding) | Diverse images with ground-truth answers for modality, view, side, scale, CTR, findings | VinDr labels/boxes, RSNA boxes, CheXpert/NIH labels, Zenodo Paraguay bone scans (metastasis yes/no) | Scintigraphy question set must be built by us |
| Misleading-context tests | Pairs of image + wrong text | Build from VinDr labels (MC-CXR recipe) | — |
| Report-quality metrics | Image + report pairs | MIMIC-CXR (PhysioNet, credentialed), CheXpert Plus (Stanford AIMI) | Not on Kaggle; credentialed access |
| Later CT/MRI | Volumes with masks | RSNA 2022/2023/2024 (Kaggle, DICOM), TotalSegmentator data | Phase 7 |

## What OIP does about it
- Phase 2 uses RSNA + VinDr (DICOM) for converter and measurement validation.
- We create a **synthetic reference set**: phantom DX and NM DICOMs generated
  with pydicom, with exactly known geometry, counts and windows (already in
  `scripts/make_examples.py`). This is our unit-test ground truth and it fills
  the NM DICOM gap until real NM DICOM is sourced.
- We request access to PhysioNet (CheXmask, MIMIC-CXR) and Stanford AIMI
  (CheXpert Plus) in Phase 2 (user action needed, see PLAN).
