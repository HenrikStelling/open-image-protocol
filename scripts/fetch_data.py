"""Download reference datasets listed in scripts/datasets.json.

Modes per entry:
  - full            : whole competition/dataset archive (only for small sets)
  - files: [...]    : explicit file list, downloaded one by one (kagglehub path=)
  - sample: {n, ...}: stratified sample of VinDr-CXR train images (avoids the 142 GB full download)
Usage: python scripts/fetch_data.py --phase 2 [--dry-run]   |   --source zenodo:13900966
Storage: ~/.cache/kagglehub (kaggle) and data/<name>/ (zenodo). Each dataset gets data/<name>/SOURCE.md."""
from __future__ import annotations
import argparse, csv, json, random, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; DATA = ROOT / "data"
DATASETS = json.loads((ROOT / "scripts" / "datasets.json").read_text())


def _retry(fn, *args, attempts=6, **kwargs):
    """Kaggle downloads over flaky links drop with BrokenPipe/ChunkedEncoding; retry with exponential backoff.
    kagglehub keeps completed files, so a retry resumes rather than restarts."""
    import time
    for i in range(attempts):
        try:
            return fn(*args, **kwargs)
        except Exception as e:  # noqa: BLE001
            if i == attempts - 1:
                raise
            wait = min(300, 10 * 2 ** i)
            print(f"  retry {i + 1}/{attempts - 1} after error: {type(e).__name__}: {str(e)[:120]} (waiting {wait}s)")
            time.sleep(wait)


def _kagglehub():
    try:
        import kagglehub
        return kagglehub
    except ImportError:
        sys.exit("pip install kagglehub, then create a Kaggle token (docs/02-research-questions/q09-data-access.md)")


def _source_md(entry, dest, extra=""):
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "SOURCE.md").write_text(f"# {entry['name']}\n\n- source: {entry['source']}\n- url: {entry['url']}\n- licence: {entry['licence']}\n- use: {entry['use']}\n{extra}")


def vindr_sample(entry, kind, ident, dry):
    """Stratified sample: half images with at least one finding box, half 'No finding'; spread across the id space."""
    kh = _kagglehub(); n = entry["sample"]["n"]; seed = entry["sample"].get("seed", 0)
    csv_path = Path(kh.competition_download(ident, path="train.csv"))
    by_id: dict[str, set] = {}
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            by_id.setdefault(r["image_id"], set()).add(r["class_name"])
    with_finding = sorted(i for i, c in by_id.items() if c - {"No finding"})
    normal = sorted(i for i, c in by_id.items() if not (c - {"No finding"}))
    rng = random.Random(seed)
    chosen = rng.sample(with_finding, n // 2) + rng.sample(normal, n - n // 2)
    (DATA / entry["name"]).mkdir(parents=True, exist_ok=True)
    (DATA / entry["name"] / "sample_ids.txt").write_text("\n".join(chosen) + "\n")
    print(f"{entry['name']}: {len(with_finding)} images with findings, {len(normal)} normal; sampling {n} (seed {seed}) ≈ {n*13/1000:.1f} GB on disk")
    if dry:
        return
    for k, iid in enumerate(chosen, 1):
        p = _retry(kh.competition_download, ident, path=f"train/{iid}.dicom")
        if k % 50 == 0 or k == len(chosen):
            print(f"  {k}/{len(chosen)} -> {Path(p).parent}")
    _source_md(entry, DATA / entry["name"], f"- subset: {n} train images listed in sample_ids.txt (seed {seed}); files live in ~/.cache/kagglehub/competitions/{ident}/train/\n")


def fetch(entry, dry=False):
    kind, ident = entry["source"].split(":", 1)
    dest = DATA / entry["name"]
    if kind in ("kaggle-competition", "kaggle-dataset"):
        kh = _kagglehub()
        fn = kh.competition_download if kind == "kaggle-competition" else kh.dataset_download
        if entry.get("sample"):
            return vindr_sample(entry, kind, ident, dry)
        if entry.get("files"):
            print(f"{entry['name']}: {len(entry['files'])} file(s) ≈ {entry.get('approx_gb','?')} GB")
            if dry: return
            for fpath in entry["files"]:
                print("  ", fpath, "->", _retry(fn, ident, path=fpath))
        else:
            print(f"{entry['name']}: full download ≈ {entry.get('approx_gb','?')} GB")
            if dry: return
            print("  ->", _retry(fn, ident))
        _source_md(entry, dest, f"- files cached under ~/.cache/kagglehub/\n")
    elif kind == "zenodo":
        rec = json.load(urllib.request.urlopen(f"https://zenodo.org/api/records/{ident}"))
        tot = sum(f["size"] for f in rec["files"]) / 1e9
        print(f"{entry['name']}: {len(rec['files'])} file(s), {tot:.2f} GB")
        if dry: return
        _source_md(entry, dest)
        for f in rec["files"]:
            out = dest / f["key"]
            if not out.exists():
                print("  downloading", f["key"]); _retry(urllib.request.urlretrieve, f["links"]["self"], out)
    else:
        print(f"{entry['name']}: manual download required: {entry['url']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--phase", type=int); ap.add_argument("--source"); ap.add_argument("--name")
    ap.add_argument("--dry-run", action="store_true", help="print sizes and plan, download nothing"); a = ap.parse_args()
    for e in DATASETS:
        if (a.source and e["source"] == a.source) or (a.phase and a.phase in e["phases"]) or (a.name and e["name"] == a.name):
            fetch(e, a.dry_run)
