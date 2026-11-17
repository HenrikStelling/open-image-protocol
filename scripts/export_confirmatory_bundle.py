"""Build the confirmatory-round supplement of the Zenodo data bundle (registration https://osf.io/9rxbk, section 9).

Usage: python scripts/export_confirmatory_bundle.py [--label confirm:] [--bench-dir $OIP_BENCH_DIR] [--out dist] [--doi DOI]

Produces dist/oip-bench-confirmatory-2026-11/ with
  replies-confirmatory/<run>/results.jsonl, tasks.json, run_meta.json   every run directory whose run_meta.label starts with --label
  registration/                                                          the registered text (md, pdf) and confirm_set.json
  reports/                                                               the frozen analysis output (final and interim) and the run report
  packages/vindr-confirm-meta/                                           oip.json, context.md, derived/measurements.json of the 80 packages
                                                                         (Kaggle terms: no pixels, renders or masks; full hashes in the manifest)
  MANIFEST.json, README.md
and one zip next to it. Nothing is uploaded; the author adds the zip to a new version of the data bundle on Zenodo.
"""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_release_bundle import META_ONLY, ROOT, copy_tree, package_hashes, run_info, sha  # noqa: E402

NAME = "oip-bench-confirmatory-2026-11"
REGISTRATION = "https://osf.io/9rxbk"
DOCS = {
    "registration": ["docs/paper/preregistration-confirmatory-2026-11-03-osf.md", "docs/paper/preregistration-confirmatory-2026-11-03-osf.pdf",
                     "bench/confirm/confirm_set.json"],
    "reports": ["docs/reports/confirmatory-2026-11-17.md", "docs/reports/confirmatory-2026-11-06.md", "docs/reports/confirmatory-2026-11-17-run.md"],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="confirm:")
    ap.add_argument("--bench-dir", default=os.environ.get("OIP_BENCH_DIR", str(Path.home() / "oip-bench")))
    ap.add_argument("--out", default=str(ROOT / "dist"))
    ap.add_argument("--doi", default="", help="Zenodo DOI of the bundle version, written into README.md and MANIFEST.json")
    a = ap.parse_args()
    bench = Path(a.bench_dir); out = Path(a.out) / NAME
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    git = lambda *args: subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True).stdout.strip()
    commit = git("rev-parse", "--short", "HEAD"); tag_commit = git("rev-parse", "--short", "prereg-confirm-2026-11^{commit}")
    frozen = git("diff", "prereg-confirm-2026-11", "--stat", "--", "bench/confirm/", "bench/run.py", "bench/tasks.py", "bench/score.py",
                 "bench/cloudlock.py", "src/oip/")
    if frozen:
        raise SystemExit("frozen code differs from tag prereg-confirm-2026-11:\n" + frozen)
    # 1. replies
    runs = []
    for d in sorted((ROOT / "bench/results").glob("*")):
        meta_f = d / "run_meta.json"
        if not (d / "results.jsonl").exists() or not meta_f.exists():
            continue
        meta = json.loads(meta_f.read_text())
        if not str(meta.get("label", "")).startswith(a.label):
            continue
        dst = out / "replies-confirmatory" / d.name; dst.mkdir(parents=True)
        for name in ("results.jsonl", "tasks.json", "run_meta.json"):
            shutil.copy2(d / name, dst / name)
        info = run_info(d); info["label"] = meta.get("label")
        rows = [json.loads(l) for l in (d / "results.jsonl").read_text().splitlines() if l.strip()]
        info["rows_per_rep"] = {str(r): sum(1 for x in rows if x.get("rep") == r) for r in sorted({x.get("rep") for x in rows})}
        info["harness_commits"] = sorted({x.get("harness_commit") for x in rows})
        runs.append(info)
    bad = [r["run"] for r in runs if r["error_rows"] or r["rows"] != 3270]
    if len(runs) != 10 or bad:
        raise SystemExit(f"expected ten complete run directories (3,270 rows, no error rows); found {len(runs)}, incomplete: {bad}")
    # 2. registration, reports
    for group, files in DOCS.items():
        (out / group).mkdir()
        for rel in files:
            shutil.copy2(ROOT / rel, out / group / Path(rel).name)
    # 3. package manifests (no pixels)
    src = bench / "vindr-confirm"; pkgs = sorted(p for p in src.glob("*.oip") if (p / "oip.json").exists())
    for pkg in pkgs:
        copy_tree(pkg, out / "packages/vindr-confirm-meta" / pkg.name, META_ONLY)
    # 4. manifest, readme
    files = {str(f.relative_to(out)): {"sha256": sha(f), "bytes": f.stat().st_size} for f in sorted(out.rglob("*")) if f.is_file()}
    manifest = {"bundle": NAME, "built": time.strftime("%Y-%m-%dT%H:%M:%S"), "repo": "https://github.com/HenrikStelling/open-image-protocol",
                "repo_commit": commit, "frozen_tag": "prereg-confirm-2026-11", "frozen_commit": tag_commit, "registration": REGISTRATION,
                "doi": a.doi or None, "runs": runs, "bundled_files": files, "package_files_sha256": {"confirm-vindr-80": package_hashes(src)},
                "notes": ["VinDr-CXR images, renders and masks are Kaggle competition data and are not bundled; their hashes are listed so a rebuild can be verified.",
                          "Three replies per item for every model (rep 0, 1, 2); rep 0 is the primary datum of the registered analysis.",
                          "Rows carry `harness_commit` with a `-dirty` suffix (uncommitted documentation in the working tree); the frozen code paths were identical to the tag at every start (run report, section 6).",
                          "No error row remains; refilled rows were re-sent with the identical prompt (`prompt_sha256`).",
                          "reports/confirmatory-2026-11-06.md is the interim output (kimi-k3 with two replies); the final output of 2026-11-17 differs in three lines."]}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    (out / "README.md").write_text(f"""# OIP-Bench confirmatory round, 2026-11 (supplement to the data bundle)

Frozen model replies of the pre-registered confirmatory round of the Open Image Protocol study. Registration: {REGISTRATION}
(2026-11-03). Analysis code frozen at tag `prereg-confirm-2026-11` (commit {tag_commit}). Built {manifest['built']} from repository
commit {commit}. {('DOI: https://doi.org/' + a.doi) if a.doi else 'DOI: see the Zenodo record.'}

- `replies-confirmatory/`: {len(runs)} run directories (one per model), {sum(r['rows'] for r in runs)} rows, three replies per item, run
  2026-11-04 to 2026-11-16. Each directory holds `results.jsonl` (every reply with prompt and reply hashes), `tasks.json`, `run_meta.json`.
- `registration/`: the registered text (Markdown and PDF) and `confirm_set.json` (the 80 images and 10 reserve packages with their hashes).
- `reports/`: `confirmatory-2026-11-17.md` (output of the frozen `bench/confirm/analyze.py`), `confirmatory-2026-11-06.md` (interim
  output before the last model's repeats closed), `confirmatory-2026-11-17-run.md` (timeline, refills, deviations, spend).
- `packages/vindr-confirm-meta/`: manifests, reference files and measurements of the {len(pkgs)} packages. VinDr-CXR pixels are not
  redistributed; the Kaggle competition supplies them and `MANIFEST.json` lists the hash of every package file.

Reproduce the report: check out the tag, place the run directories under `bench/results/`, run
`python bench/confirm/analyze.py --label confirm:`.

Licence: replies, reports and manifests CC-BY-4.0.
""")
    z = out.parent / f"{NAME}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(out.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(out.parent))
    print(f"{z.name}: {z.stat().st_size/1e6:.1f} MB | runs: {len(runs)} | files: {len(files)}")


if __name__ == "__main__":
    main()
