"""Merge the readers' CSV files into one table: latest revision per (reader, item, task), mm from the header spacing, overview.

Usage: python bench/reader/collect.py [readings/*.csv] [--out docs/reports/reader-readings-<date>.csv]
Reads bench/reader/set_key.json for the spacing (readers never see it). Heart width in mm = heart_px x column spacing of the
source, only for packages whose spacing comes from the DICOM header (spacing_source PixelSpacing or ImagerPixelSpacing: the
82 VinDr packages; NIH's dataset_metadata spacing is not used); the canonical render has the source's pixel
grid for every package in the set (no resample), which this script asserts. Agreement statistics live in a later script
once two readers' files exist; this one only merges and counts.
"""
from __future__ import annotations
import argparse, csv, glob, json, time
from collections import Counter, defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("files", nargs="*"); ap.add_argument("--out", default=f"docs/reports/reader-readings-{time.strftime('%Y-%m-%d')}.csv")
    a = ap.parse_args()
    files = a.files or sorted(glob.glob(str(HERE / "readings" / "*.csv")))
    if not files:
        raise SystemExit("no readings/*.csv yet")
    key = json.loads((HERE / "set_key.json").read_text(encoding="utf-8"))
    latest: dict = {}
    for f in files:
        for r in csv.DictReader(open(f, encoding="utf-8")):
            k = (r["reader_id"], r["block"], r["item_id"], r["task"])
            if k not in latest or int(r["revision"] or 0) >= int(latest[k]["revision"] or 0):
                latest[k] = r
    rows = []
    for (reader, block, iid, task), r in sorted(latest.items()):
        kk = key.get(f"{block}:{iid}", {}); sp = kk.get("pixel_spacing_mm"); src = kk.get("spacing_source")
        r = dict(r); r["heart_mm"] = ""; r["spacing_source"] = src or ""
        if r.get("heart_px") and sp and src not in (None, "", "none", "dataset_metadata"):   # header-derived spacing (PixelSpacing, ImagerPixelSpacing)
            assert int(r["image_w"]) == kk["columns"], f"{iid}: render width {r['image_w']} != source columns {kk['columns']}"
            r["heart_mm"] = f"{float(r['heart_px']) * float(sp[1]):.1f}"   # [row spacing, column spacing]; width is along columns
        rows.append(r)
    out = ROOT / a.out; out.parent.mkdir(parents=True, exist_ok=True)
    cols = list(rows[0].keys())
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
    c = Counter((r["reader_id"], r["block"], r["task"]) for r in rows); na = Counter((r["reader_id"], r["block"], r["task"]) for r in rows if r["not_assessable"] == "1")
    uns = Counter((r["reader_id"], r["block"], r["task"]) for r in rows if r["unsure"] == "1")
    print(f"wrote {out}: {len(rows)} latest-revision rows from {len(files)} file(s)")
    print("| reader | block | task | n | not assessable | unsure |"); print("|---|---|---|---|---|---|")
    for k in sorted(c):
        print(f"| {k[0]} | {k[1]} | {k[2]} | {c[k]} | {na[k]} | {uns[k]} |")
    revs = defaultdict(int)
    for f in files:
        for r in csv.DictReader(open(f, encoding="utf-8")):
            revs[r["reader_id"]] += 1
    print("rows in the append-only files (all revisions):", dict(revs))


if __name__ == "__main__":
    main()
