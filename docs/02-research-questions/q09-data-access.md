# Q9 — How do we access our reference data?

## Kaggle
- Token: kaggle.com → Settings → API → *Create New Token* → `~/.kaggle/kaggle.json`
  (or env `KAGGLE_USERNAME` / `KAGGLE_KEY`). Never commit it (`.gitignore` covers it).
- Library: `kagglehub` (official). Example:
  ```python
  import kagglehub
  path = kagglehub.competition_download("vinbigdata-chest-xray-abnormalities-detection")
  path = kagglehub.dataset_download("nih-chest-xrays/data")
  ```
  Competition data requires accepting the competition rules once in the browser.
- CLI search (to re-check scintigraphy): `kaggle datasets list -s scintigraphy`,
  `kaggle datasets list -s "bone scan"`, `kaggle datasets list -s "nuclear medicine"`.
- Cache: `~/.cache/kagglehub/`. Script: `scripts/fetch_data.py` (stub, reads a
  manifest of dataset ids and downloads only what a phase needs).

## Zenodo (Paraguay bone scans)
- Direct download of the record files (`https://zenodo.org/records/13900966`), CC-BY-4.0. `scripts/fetch_data.py --source zenodo:13900966`.

## PhysioNet (CheXmask, MIMIC-CXR)
- Requires a PhysioNet account, CITI training and a signed DUA (credentialed).
  User action; afterwards `wget -r -N -c -np --user … https://physionet.org/files/chexmask-cxr-segmentation-data/1.0.0/`.

## Stanford AIMI (CheXpert Plus), TCIA
- Registration + licence acceptance; download via their portals / `tcia_utils`.

## Storage and hygiene
- Raw data lives outside the repo (`data/` is git-ignored except `data/samples/`
  which holds only synthetic or explicitly redistributable samples).
- Every downloaded dataset gets a `data/<name>/SOURCE.md` with URL, licence,
  version, checksum, and the date.
- OIP packages derived from restricted datasets are **not** committed.

## What OIP does about it
`scripts/fetch_data.py` (stub written, needs credentials to run) + `.gitignore`
rules + the `SOURCE.md` convention.
