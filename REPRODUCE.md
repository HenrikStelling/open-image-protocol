# Reproducing OIP: install, examples, the paper's tables, the packages, new runs

Four levels, from minutes without any data to days with Kaggle access. Each level states what it needs, what it produces and how to check the result.

| Level | What you reproduce | Needs | Time |
|---|---|---|---|
| A | install, tests, example packages, CLI | Python ≥ 3.10, `uv` | 5 min |
| B | every table of the paper from the frozen model replies | the Zenodo bundle (≈ 150 MB) | 10 min |
| C | the 2,100 converted packages and the 190 benchmark packages from the raw datasets | Kaggle account, ≈ 25 GB, CPU | hours |
| D | new benchmark runs on your own models | Ollama and/or API keys | hours to days, paid calls |

Paths and secrets are never hard-coded. Everything the scripts need to know about your machine comes from these variables (defaults in brackets):

| Variable | Meaning |
|---|---|
| `OIP_KAGGLE_CACHE` | kagglehub download cache [`~/.cache/kagglehub`] |
| `OIP_BENCH_DIR` | package store for the benchmark sets, outside the clone [`~/oip-bench`] |
| `OIP_VINDR_LABELS` | VinDr `train.csv` for the finding-level tasks [`$OIP_BENCH_DIR/meta/vindr_train.csv`, then the cache] |
| `OIP_CXAS_PYTHON` | python of the isolated CXAS venv, only for the cross-check [`~/cxas-venv/bin/python`] |
| `SOURCE_DATE_EPOCH` | if set, package ids and creation times are deterministic (uuid5 of the source hash + that time) |
| `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY` | frontier providers, level D only; keep them in a file outside the clone (e.g. `~/.config/oip/keys.env`, `chmod 600`) |

Keep the clone, the venv and the package store outside iCloud-synced folders (see CONTRIBUTING.md).

## A. Install, tests, examples (no data)

```bash
git clone https://github.com/HenrikStelling/open-image-protocol.git && cd open-image-protocol
make setup            # .venv with the core package and dev tools
make test             # phantom tests (tests/) + benchmark unit tests (bench/test_*.py)
make validate         # schema + package rules on the four example packages
make examples-check   # rebuilds spec/examples and data/samples; must leave git clean
.venv/bin/oip describe spec/examples/synthetic-dx-chest.oip
```

`make setup-all` adds the anatomy adapter (torch, torchxrayvision; CPU is enough) and the benchmark extras. Then:

```bash
.venv/bin/oip measure spec/examples/synthetic-dx-chest.oip     # regions + CTR from the PSPNet adapter
.venv/bin/oip check   spec/examples/synthetic-dx-chest.oip     # pixel-side orientation check
```

Expected: 56 tests pass; the synthetic DX phantom reports CTR 0.4647, heart 130.2 mm, thorax 280.2 mm (phantom truth 130 and 280 mm).

## B. The paper's tables from the frozen replies

The benchmark's dataset is the set of frozen model replies. They are published on Zenodo (DOI: see README, "Data and code availability") as `oip-bench-replies-<tag>.zip`, built by `scripts/export_release_bundle.py`; the RA study that produced the paper holds an identical, hashed copy.

```bash
unzip oip-bench-replies-v0.2.0.zip -d bench/results/        # one directory per run: results.jsonl + tasks.json (+ run_meta.json from 2026-09-26)
.venv/bin/python bench/report.py                             # -> docs/reports/pilot-ollama-report.md (the scoreboard)
.venv/bin/python bench/paper_stats.py scorer-0.3             # -> docs/paper/reference-sheet-scorer-0.3.md + paper-stats-scorer-0.3.json
```

Scorer versions matter. The paper (analysis in the Research_Automation study, `docs/paper/PROTOCOL_oip.md`) was scored with scorer 0.2, the `bench/score.py` of commit 050769a. The frozen rows now carry scorer 0.3 in `score` and the 0.2 result in `score_prev`; the differences are listed in `docs/reports/rescore-scorer-0.3.md` (only glm-5.3-flash moves by more than one point). To reproduce the 0.2 numbers exactly:

```bash
git show 050769a:bench/score.py > /tmp/score_0_2.py && cp bench/score.py /tmp/score_0_3.py
cp /tmp/score_0_2.py bench/score.py && .venv/bin/python bench/rescore.py && .venv/bin/python bench/report.py
cp /tmp/score_0_3.py bench/score.py     # restore
```

Checks: 41 run directories dated 2026-09-08 to 2026-09-22 belong to the paper; the three paper sets hold 60,483 non-error replies (frontier 16,476; Ollama cloud 32,939; local 11,068); `bench/rescore.py` reports 0 mismatches between the stored and the recomputed score when run twice. The gating table must match `docs/paper/reference-sheet-scorer-0.3.md` (or, under scorer 0.2, `reference-sheet.md`) cell for cell. Selection rules that the scoreboard applies: latest run per dataset × model × condition, NIH `scale_available` excluded, `CONTAMINATED-*` runs excluded, error rows out of every denominator, abstentions and empty replies scored incorrect.

## C. Packages from the raw datasets

Data (Kaggle token in `~/.kaggle/kaggle.json`; accept the competition rules once in the browser for VinDr-CXR, RSNA and SIIM):

```bash
.venv/bin/python scripts/fetch_data.py --phase 2                 # VinDr 1,000-image stratified sample (seed 0), RSNA, SIIM mirror, NIH sample; ≈ 25 GB
.venv/bin/python scripts/fetch_data.py --source zenodo:13900966  # Paraguay bone scans (CC-BY-4.0) -> data/bone-scans-paraguay/
```

Conversion and measurement (the Phase 2 reports in `docs/reports/`):

```bash
.venv/bin/python scripts/convert_batch.py            # 2,100 packages -> data/oip/<set>/, phase2-conversion-{stats.json,report.md}; expected 0 failures
.venv/bin/python scripts/measure_batch.py vindr 1000 # PSPNet regions + CTR on the VinDr packages
.venv/bin/python scripts/measure_report.py           # phase2-measurement-report.md (CTR median 0.478; 338 of 1,000 above 0.50)
```

The benchmark sets (no radiologist boxes or labels enter a package; a keyword leak check runs after generation):

```bash
export OIP_BENCH_DIR=~/oip-bench
.venv/bin/python scripts/make_bench_set.py --vindr 100 --nih 50 --seed 1    # seed 1 reproduces the paper's sets (verified 100/100 and 50/50)
.venv/bin/python scripts/bonescan_to_oip.py 40 $OIP_BENCH_DIR/bonescan       # 20 anterior + 20 posterior views, balanced by class, seed 0
```

The paper's packages were built without `SOURCE_DATE_EPOCH`, so `identity.package_id` and `identity.created` differ from yours; pixels, renders, masks, measurements and `context.md` must match the sha256 values in the bundle's `packages_manifest.json`. The VinDr images and labels are Kaggle competition data and are not in the bundle; the bundle carries the full NIH and bone-scan packages and, for VinDr, the manifests, `context.md` and measurement files only.

## D. New benchmark runs

```bash
. ~/.config/oip/keys.env                                     # only for claude / gpt / gemini
.venv/bin/python bench/run.py --dataset vindr-paper --pkg-dir $OIP_BENCH_DIR/vindr-paper --n 100 \
    --models ollama/gemma4:e4b-it-qat --conditions raw,ctx_l1,ctx,annot,misled_plain,misled_oip
.venv/bin/python bench/run.py --resume bench/results/<run dir>     # continue an interrupted run; error rows are retried
.venv/bin/python bench/report.py
```

Models: `claude`, `gpt`, `gemini` (ids pinned in `bench/run.py`), or any multimodal Ollama tag as `ollama/<tag>`. One Ollama cloud model runs at a time (a file lock enforces it). Every run directory records the harness commit, scorer version, system prompt and arguments in `run_meta.json`, and every row carries them too. Cost: a full pass over the three paper sets was about US$ 9 (Gemini 3.8 Flash), 37 (GPT-5.6 Terra) and 15 (Claude Sonnet 5, with prompt caching) at September 2026 list prices. Cloud model versions are not pinned by the providers; two tags used in the paper were retired within a month, so record the date of every run.

## What is deliberately not reproducible from this repository

Ground truth for CTR and cardiac width is the package's own tool measurement (validation Tier 1); the Tier 2 comparison against CheXmask needs PhysioNet credentialing and is pending. The VinDr images cannot be redistributed. Anything a model answered is frozen; nothing in the analysis calls a model.
