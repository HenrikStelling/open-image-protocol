"""Build the Zenodo release bundle: the frozen benchmark replies and the benchmark packages, with a sha256 manifest.

Usage: python scripts/export_release_bundle.py --tag v0.2.1 [--until 20260922] [--round3-until 20261016] [--bench-dir $OIP_BENCH_DIR] [--out dist]

Produces dist/oip-bench-<tag>/ with
  replies/<run>/results.jsonl, tasks.json[, run_meta.json]   every run directory dated <= --until (CONTAMINATED-* runs go to
                                                             replies-excluded/ so the no-leakage exclusion stays auditable)
  replies-round3/<run>/...                                   runs dated after --until and <= --round3-until (post-hoc experiments:
                                                             verification ablation, render probe, OEP-002, round 3a, runtime)
  meta/chexmask/*.json                                       CheXmask / CXAS per-image cross-check files (bench/results/_chexmask)
  packages/nih-paper/, packages/bonescan/                    full packages (CC-BY-4.0 sources)
  packages/vindr-paper-meta/, packages/vindr-pilot-meta/     oip.json, context.md, derived/measurements.json only (Kaggle terms:
                                                             no pixels, renders or masks); full-package hashes in the manifest
  meta/pilot_pkgs.txt, meta/cxas_vs_pspnet_20.json
  MANIFEST.json                                              sha256 and size of every bundled file; sha256 of every file of every
                                                             full package (including the VinDr files not bundled); run table
  README.md
and one zip per top-level group next to it. Nothing is uploaded; the author does that on Zenodo.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = {"vindr": "pilot-vindr-20", "vindr-paper": "paper-vindr-100", "nih-paper": "paper-nih-50", "bonescan": "bonescan-40"}
META_ONLY = ("oip.json", "context.md", "derived/measurements.json")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_info(d: Path) -> dict:
    tasks = json.loads((d / "tasks.json").read_text()) if (d / "tasks.json").exists() else []
    rows = [json.loads(l) for l in (d / "results.jsonl").read_text().splitlines() if l.strip()]
    meta = json.loads((d / "run_meta.json").read_text()) if (d / "run_meta.json").exists() else {}
    pkgdir = Path(tasks[0]["pkg"]).parent.name if tasks else None
    return {"run": d.name, "dataset": DATASETS.get(pkgdir, pkgdir), "rows": len(rows), "error_rows": sum(1 for x in rows if x.get("error")),
            "models": sorted({x["model"] for x in rows}), "conditions": sorted({x["condition"] for x in rows}),
            "scorer": sorted({str(x.get("scorer", "0.2")) for x in rows}), "harness_commit": meta.get("harness_commit"),
            "started": meta.get("started")}


def copy_tree(src: Path, dst: Path, only: tuple[str, ...] | None = None) -> None:
    for f in sorted(src.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(src)
        if only is not None and str(rel) not in only:
            continue
        (dst / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, dst / rel)


def package_hashes(setdir: Path) -> dict:
    out = {}
    for pkg in sorted(p for p in setdir.glob("*.oip") if (p / "oip.json").exists()):
        out[pkg.name] = {str(f.relative_to(pkg)): {"sha256": sha(f), "bytes": f.stat().st_size} for f in sorted(pkg.rglob("*")) if f.is_file() and not f.name.startswith("_")}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--until", default="20260922", help="last run date (YYYYMMDD) to include as paper runs")
    ap.add_argument("--round3-until", default="", help="last run date (YYYYMMDD) of post-hoc runs to include under replies-round3/ (empty: none)")
    ap.add_argument("--bench-dir", default=os.environ.get("OIP_BENCH_DIR", str(Path.home() / "oip-bench")))
    ap.add_argument("--out", default=str(ROOT / "dist"))
    ap.add_argument("--doi", default="", help="Zenodo DOI of this bundle, written into README.md and MANIFEST.json (reserve it on Zenodo first)")
    a = ap.parse_args()
    bench = Path(a.bench_dir); out = Path(a.out) / f"oip-bench-{a.tag}"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    # 1. replies
    runs = []
    for d in sorted((ROOT / "bench/results").glob("*")):
        if not (d / "results.jsonl").exists() or d.name.startswith("_"):
            continue
        contaminated = d.name.startswith("CONTAMINATED")
        date = d.name.split("-")[1 if contaminated else 0][:8]
        phase = "paper" if contaminated or date <= a.until else ("round3" if a.round3_until and date <= a.round3_until else None)
        if phase is None:
            continue
        dst = out / ("replies-excluded" if contaminated else ("replies" if phase == "paper" else "replies-round3")) / d.name
        dst.mkdir(parents=True)
        for name in ("results.jsonl", "tasks.json", "run_meta.json"):
            if (d / name).exists():
                shutil.copy2(d / name, dst / name)
        info = run_info(d); info["excluded"] = contaminated; info["phase"] = phase; runs.append(info)
    chex = ROOT / "bench/results/_chexmask"
    if a.round3_until and chex.exists():
        (out / "meta/chexmask").mkdir(parents=True, exist_ok=True)
        for f in sorted(chex.glob("*.json")):
            shutil.copy2(f, out / "meta/chexmask" / f.name)
    # 2. packages
    for setname, mode in (("nih-paper", "full"), ("bonescan", "full"), ("vindr-paper", "meta"), ("vindr", "meta")):
        src = bench / setname
        if not src.exists():
            print("missing package set:", src); continue
        dst = out / "packages" / (setname if mode == "full" else ("vindr-pilot-meta" if setname == "vindr" else f"{setname}-meta"))
        for pkg in sorted(p for p in src.glob("*.oip") if (p / "oip.json").exists()):
            copy_tree(pkg, dst / pkg.name, None if mode == "full" else META_ONLY)
    for name in ("pilot_pkgs.txt", "cxas_vs_pspnet_20.json"):
        if (bench / name).exists():
            (out / "meta").mkdir(exist_ok=True); shutil.copy2(bench / name, out / "meta" / name)
    # 3. manifest
    files = {str(f.relative_to(out)): {"sha256": sha(f), "bytes": f.stat().st_size} for f in sorted(out.rglob("*")) if f.is_file()}
    full_hashes = {DATASETS[s]: package_hashes(bench / s) for s in ("vindr-paper", "vindr", "nih-paper", "bonescan") if (bench / s).exists()}
    manifest = {"bundle": f"oip-bench-{a.tag}", "built": time.strftime("%Y-%m-%dT%H:%M:%S"), "repo": "https://github.com/HenrikStelling/open-image-protocol",
                "repo_commit": commit, "doi": a.doi or None, "paper_runs_until": a.until, "round3_runs_until": a.round3_until or None, "runs": runs, "bundled_files": files, "package_files_sha256": full_hashes,
                "notes": ["VinDr-CXR images, renders and masks are Kaggle competition data and are not bundled; their hashes are listed so a rebuild can be verified.",
                          "Rows carry `score` (scorer 0.3) and, where it differs, `score_prev` (scorer 0.2, commit 050769a) — see docs/reports/rescore-scorer-0.3.md.",
                          "Abstentions and empty replies are scored incorrect; error rows have `error` set and are excluded from denominators.",
                          "replies-round3/: post-hoc runs (2026-09-26 to 2026-10-16) with `rep` (repeat index), `prompt_sha256`, `reply_sha256`, `tasks_version` per row; rows with score.truncated = true were cut off at the output cap before closing their reasoning and count as no answer (bench/run.py score_row, from commit c8f8ece).",
                          "Packages are bundled in their current state: from 2026-10-17 the measurements carry validation_status cross_checked with a CheXmask cross_check record and context.md is rendered with template 0.2.1; the paper-era manifests are in the v0.2.0 bundle (10.5281/zenodo.23040047). CXAS masks (derived/masks_cxas/) exist in the vindr-paper packages and are listed in the hashes but not bundled (derived from Kaggle pixels).",
                          "glm-5.3-flash's first round-3a run (2,400-token cap) was set aside and lost in a reboot; the bundled run is the 8,000-token rerun (docs/reports/round3a-readings.md, item 6)."]}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    (out / "README.md").write_text(f"""# OIP-Bench release bundle {a.tag}

Frozen model replies and benchmark packages of the Open Image Protocol paper. Built {manifest['built']} from repository commit {commit}.
{('DOI: https://doi.org/' + a.doi) if a.doi else 'DOI: see the Zenodo record.'}
How to use them: `REPRODUCE.md` in the repository (level B). Contents and hashes: `MANIFEST.json`.

- `replies/`: {sum(1 for r in runs if not r['excluded'] and r['phase'] == 'paper')} run directories dated up to {a.until}, {sum(r['rows'] for r in runs if not r['excluded'] and r['phase'] == 'paper')} rows (the paper's runs); `replies-excluded/`: the run discarded under the no-leakage rule.
- `replies-round3/`: {sum(1 for r in runs if r['phase'] == 'round3')} post-hoc run directories dated {a.until} to {a.round3_until or '-'}, {sum(r['rows'] for r in runs if r['phase'] == 'round3')} rows (verification ablation, render probe, OEP-002, round 3a with three replies per cell, runtime experiment; `docs/reports/`).
- `meta/chexmask/`: CheXmask and CXAS per-image cross-check files (`bench/chexmask_validate.py`, `bench/itw_cxas_eval.py`).
- `packages/nih-paper`, `packages/bonescan`: full packages (sources CC-BY-4.0 / CC0). `packages/vindr-paper-meta`, `packages/vindr-pilot-meta`: manifests, reference files and measurements only.
- `meta/`: pilot package list and the CXAS cross-check file.

Licence: replies and manifests CC-BY-4.0; the NIH and bone-scan packages inherit their sources' licences.
""")
    # 4. zips
    for group in ("replies", "replies-round3", "replies-excluded", "packages", "meta"):
        g = out / group
        if not g.exists():
            continue
        z = out.parent / f"oip-bench-{a.tag}-{group}.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(g.rglob("*")):
                if f.is_file():
                    zf.write(f, f.relative_to(out))
        print(f"{z.name}: {z.stat().st_size/1e6:.1f} MB")
    for name in ("MANIFEST.json", "README.md"):
        shutil.copy2(out / name, out.parent / f"oip-bench-{a.tag}-{name}")
    print("bundle:", out, "| runs:", len(runs), "| files:", len(files))


if __name__ == "__main__":
    main()
