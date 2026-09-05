# Q8 — Does Kaggle contain enough reference data for X-ray and scintigraphy?

## Verdict
- **X-ray: yes**, comfortably, including DICOM with pixel spacing and radiologist annotations.
- **Scintigraphy: no.** Searches (web + site:kaggle.com) found no planar
  scintigraphy / bone scan / thyroid / DaTscan image dataset on Kaggle. The
  Kaggle search page is JavaScript-rendered and could not be scraped here; this
  must be re-checked with the Kaggle CLI (`kaggle datasets list -s scintigraphy`)
  once credentials are configured (see Q9). Mitigation below.

## X-ray inventory (Kaggle)

| Dataset (Kaggle) | Size | Format | Metadata | Annotations | Use in OIP |
|---|---|---|---|---|---|
| RSNA Pneumonia Detection Challenge (`rsna-pneumonia-detection-challenge`) | 26,684 frontal CXR | **DICOM**, 1024×1024 (derived from NIH) | age, sex, ViewPosition, PixelSpacing (verify: images were resampled, so spacing may be recomputed) | pneumonia bounding boxes | converter tests, box-size in mm |
| VinDr-CXR (`vinbigdata-chest-xray-abnormalities-detection`) | 18,000 PA CXR (15k train / 3k test); **~142 GB total, ~13 MB per DICOM** → we download a stratified 1,000-image sample (~13 GB) via per-file kagglehub downloads | **original DICOM** from many vendors (Philips, GE, Fujifilm, Siemens, Toshiba, Canon, Samsung) | full headers | 14 findings, boxes by 3 radiologists each (up to 58 annotations/img) | primary validation set: vendor diversity, spacing, findings F1 |
| SIIM-ACR Pneumothorax (`siim-acr-pneumothorax-segmentation`) | ~12k | **DICOM** 1024×1024 | headers | pneumothorax masks (RLE) | mask-based measurement tests |
| NIH ChestX-ray14 (`nih-chest-xrays/data`) | 112,120 | PNG 1024×1024 | CSV: age, sex, ViewPosition, **OriginalImagePixelSpacing**, original size | 14 labels (NLP) | non-DICOM path: spacing from CSV, `external` |
| CheXpert (mirrors, e.g. `ashery/chexpert`) | 224k | JPG | frontal/lateral, AP/PA | 14 labels | label diversity; no spacing |
| RSNA Bone Age (`rsna-bone-age`) | 12,611 hand radiographs | PNG | sex | bone age | non-chest projection radiography |
| MURA (mirrors) | 40k musculoskeletal | PNG | body part | abnormal y/n | non-chest |
| Kermany pediatric pneumonia (`paultimothymooney/chest-xray-pneumonia`) | 5.8k | JPEG | none | 3 classes | **avoid** for validation (known quality/duplication issues); useful as "bad input" test |
| COVID-19 CXR collections | various | mixed | inconsistent | labels | avoid (documented pitfalls) |

Later phases (already on Kaggle, DICOM): RSNA Intracranial Hemorrhage (CT),
RSNA 2022 Cervical Spine (CT), RSNA 2023 Abdominal Trauma (CT), RSNA 2024 Lumbar
Spine Degenerative (MRI). These make Kaggle sufficient for CT/MRI too.

## Scintigraphy inventory (outside Kaggle)

| Dataset | Size | Format | License | Notes |
|---|---|---|---|---|
| Bone scan images, IICS-UNA Paraguay (Zenodo 10.5281/zenodo.13900966) | 582 images / 291 patients, anterior + posterior, 256×1024 | image files (format to verify on download; ~80 MB zip) | CC-BY-4.0 | metastases yes/no; Tc-99m MDP ~20 mCi; best immediate NM reference |
| BS-80K (West China Hospital) | 82,544 bone scan images / 3,247 patients | images (Google Drive) | not stated — **verify before use** | largest; region/lesion annotations per paper |
| Thyroid scintigraphy multicentre (2,954 pts, 9 centres; PMC10453808 / arXiv 2503.00366) | 3k | — | not public | code only |
| TCIA PET/CT collections (e.g. FDG-PET-CT-Lesions) | large | **DICOM NM/PT** with radiopharmaceutical module | TCIA licence | closest public source of real NM-family DICOM headers |
| Synthetic NM DICOM (ours, pydicom) | unlimited | DICOM NM IOD | Apache-2.0 | exact ground truth for converter/tools |

## Storage budget (measured 2026-09-05)
VinDr full = ~142 GB (too large for a laptop); RSNA ≈ 3.7 GB; SIIM-ACR ≈ 5 GB; NIH full ≈ 42 GB. Phase 2 plan uses ≈ 25 GB: VinDr 1,000-image stratified sample (500 with findings, 500 normal, seed 0, ids in `data/vindr-cxr/sample_ids.txt`), RSNA + SIIM full, NIH CSV + `images_001` only. `scripts/fetch_data.py --phase 2 --dry-run` prints the plan without downloading.

## What OIP does about it
1. Phase 2 validation on VinDr sample + RSNA (DICOM), NIH (PNG + CSV) for the non-DICOM path.
2. Scintigraphy: Zenodo Paraguay set + synthetic NM DICOM in Phase 4; request BS-80K terms; consider TCIA PET/CT to test the NM radiopharmaceutical module on real headers.
3. Action for the user: create Kaggle API token; re-run the Kaggle scintigraphy search via CLI (Q9 script).
