"""Download reference datasets listed in scripts/datasets.json (needs Kaggle credentials for kaggle sources).
Usage: python scripts/fetch_data.py --phase 2   |   python scripts/fetch_data.py --source zenodo:13900966"""
from __future__ import annotations
import argparse, json, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; DATA = ROOT / "data"
DATASETS = json.loads((ROOT / "scripts" / "datasets.json").read_text())


def fetch(entry):
    kind, ident = entry["source"].split(":", 1)
    dest = DATA / entry["name"]; dest.mkdir(parents=True, exist_ok=True)
    (dest / "SOURCE.md").write_text(f"# {entry['name']}\n\n- source: {entry['source']}\n- url: {entry['url']}\n- licence: {entry['licence']}\n- use: {entry['use']}\n")
    if kind in ("kaggle-competition", "kaggle-dataset"):
        try:
            import kagglehub
        except ImportError:
            print("pip install kagglehub, then create ~/.kaggle/kaggle.json (see docs/02-research-questions/q09-data-access.md)"); return
        fn = kagglehub.competition_download if kind == "kaggle-competition" else kagglehub.dataset_download
        print(entry["name"], "->", fn(ident))
    elif kind == "zenodo":
        rec = json.load(urllib.request.urlopen(f"https://zenodo.org/api/records/{ident}"))
        for f in rec["files"]:
            out = dest / f["key"]
            if not out.exists():
                print("downloading", f["key"], f["size"], "bytes"); urllib.request.urlretrieve(f["links"]["self"], out)
        print(entry["name"], "->", dest)
    else:
        print("manual download required:", entry["url"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--phase", type=int); ap.add_argument("--source"); a = ap.parse_args()
    for e in DATASETS:
        if (a.source and e["source"] == a.source) or (a.phase and a.phase in e["phases"]):
            fetch(e)
