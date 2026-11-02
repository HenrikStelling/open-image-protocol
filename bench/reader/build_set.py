"""Build the human reading set for the reader study (Lancet revision, protocol in bench/reader/PROTOKOLL.md).

Usage: python bench/reader/build_set.py [--vindr ~/oip-bench/vindr-paper] [--nih ~/oip-bench/nih-paper]
                                        [--bone ~/oip-bench/bonescan] [--practice ~/oip-bench/vindr-practice] [--copy]

Writes, next to this file:
  set/<block>/<id>.png   the canonical render of each package exactly as the models saw it (symlink; --copy copies), plus the
                         marker-masked render (run._masked) for the 82 conflict-trial packages; git-ignored (VinDr is not redistributed)
  items.json             the blinded item list the sheet shows: id, block, file, size, sha256 of the image; no truth, no spacing
  set_key.json           the key for the analysis: pixel spacing, edge labels, view, hot side, package path. Readers do not open it.
  reader.html            the sheet (reader_template.html with ITEMS inlined); open via serve.py (autosave) or by double-click (export)
Blocks and order are deterministic (seed 20261102): every reader sees the same order.
"""
from __future__ import annotations
import argparse, hashlib, json, os, random, shutil, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "bench"))
from tasks import clear_cue, _marker_excluded   # noqa: E402
from run import _masked                          # noqa: E402

SEED = 20261102
TOOL_VERSION = "reader-0.1"
BLOCKS = {   # block -> (role, label shown in the sheet, task types)
    "practice": ("radiology", "Übung (3 Bilder, nicht ausgewertet)", ["side", "ctr"]),
    "side":     ("radiology", "A Seitenorientierung, 150 Röntgenbilder", ["side"]),
    "ctr":      ("radiology", "B CTR und Herzbreite, 100 VinDr", ["ctr"]),
    "marker":   ("radiology", "C Seitenmarker im maskierten Bild, 82 VinDr", ["marker"]),
    "ctr_nih":  ("radiology", "D CTR NIH (optional), 50 Bilder", ["ctr"]),
    "scint":    ("nuclear",   "E Szintigramme: Ansicht und Seite, 40 Bilder", ["scint_view", "scint_side"]),
    "hot":      ("nuclear",   "F Szintigramme: Aktivität je Bildhälfte, 8 Bilder", ["scint_hot"]),
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def place(src: Path, dst: Path, copy: bool) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if copy:
        shutil.copyfile(src, dst)
    else:
        dst.symlink_to(src.resolve())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vindr", default="~/oip-bench/vindr-paper"); ap.add_argument("--nih", default="~/oip-bench/nih-paper")
    ap.add_argument("--bone", default="~/oip-bench/bonescan"); ap.add_argument("--practice", default="~/oip-bench/vindr-practice")
    ap.add_argument("--copy", action="store_true", help="copy renders instead of symlinking (portable folder; VinDr stays on this machine)")
    a = ap.parse_args()
    vindr = sorted(Path(os.path.expanduser(a.vindr)).glob("*.oip")); nih = sorted(Path(os.path.expanduser(a.nih)).glob("*.oip"))
    bone = sorted(Path(os.path.expanduser(a.bone)).glob("*.oip"))
    if not (vindr and nih and bone):
        sys.exit("package stores not found (expected vindr-paper, nih-paper, bonescan)")
    out = HERE / "set"; items = []; key = {}
    rng = random.Random(SEED)

    def add(block: str, pkg: Path, src: Path, dataset: str, extra_key: dict) -> None:
        # opaque item id: package names would leak the bone-scan view (A/P) and diagnosis; the mapping lives in set_key.json
        iid = hashlib.sha256(f"{SEED}:{block}:{pkg.name}".encode()).hexdigest()[:12]
        dst = out / block / f"{iid}.png"
        if src.resolve() != dst.resolve():
            place(src, dst, a.copy)
        m = json.loads((pkg / "oip.json").read_text()); g = m["geometry"]
        from PIL import Image
        w, h = Image.open(src).size
        items.append(dict(item=f"{block}:{iid}", block=block, id=iid, dataset=dataset, file=f"set/{block}/{iid}.png", w=w, h=h,
                          tasks=BLOCKS[block][2], sha256=sha256(src)))
        key[f"{block}:{iid}"] = dict(pkg=str(pkg), render=str(src), dataset=dataset, rows=g["rows"], columns=g["columns"],
                                     pixel_spacing_mm=g.get("pixel_spacing_mm"), spacing_source=g.get("spacing_source"),
                                     edge_labels=g["orientation"].get("edge_labels"), orientation_level=g["orientation"].get("assertion_level"),
                                     view=(m.get("acquisition") or {}).get("view", {}).get("value"), **extra_key)

    # practice: 3 VinDr packages outside the paper set
    paper_ids = {p.name for p in vindr}
    pr_dir = Path(os.path.expanduser(a.practice))
    pool = [p for p in sorted(pr_dir.glob("*.oip")) if p.name not in paper_ids and (p / "renders/canonical.png").exists()] if pr_dir.exists() else []
    if pool:
        for p in rng.sample(pool, 3):
            add("practice", p, p / "renders/canonical.png", "vindr-extra", {})
    else:
        print("warning: no practice pool found, block 'practice' skipped", file=sys.stderr)
    # A side: 150 CXR, one shuffle over both datasets
    cxr = [(p, "vindr") for p in vindr] + [(p, "nih") for p in nih]; rng.shuffle(cxr)
    for p, ds in cxr:
        add("side", p, p / "renders/canonical.png", ds, {})
    # B ctr: 100 VinDr; D ctr_nih: 50 NIH
    vs = list(vindr); rng.shuffle(vs)
    for p in vs:
        m = json.loads((p / "oip.json").read_text())
        meas = json.loads((p / "derived/measurements.json").read_text()) if (p / "derived/measurements.json").exists() else {}
        add("ctr", p, p / "renders/canonical.png", "vindr", dict(package_measurements=meas))
    ns = list(nih); rng.shuffle(ns)
    for p in ns:
        meas = json.loads((p / "derived/measurements.json").read_text()) if (p / "derived/measurements.json").exists() else {}
        add("ctr_nih", p, p / "renders/canonical.png", "nih", dict(package_measurements=meas))
    # C marker: the 82 conflict-trial packages (clear cardiac cue, not excluded by the 2026-09-30 review), masked render
    excluded = _marker_excluded(); conflict = []
    for p in vindr:
        m = json.loads((p / "oip.json").read_text())
        if m["geometry"]["orientation"]["edge_labels"].get("left") in ("L", "R") and p.name not in excluded and clear_cue(p, m):
            conflict.append(p)
    rng.shuffle(conflict)
    for p in conflict:
        png = _masked(p, False)   # cached under bench/results/_render_cache/<pkg>/masked.png
        oid = hashlib.sha256(f"{SEED}:marker:{p.name}".encode()).hexdigest()[:12]
        dst = out / "marker" / f"{oid}.png"; dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(png)
        add("marker", p, dst, "vindr", dict(masked=True, excluded_by_review=False))
    # E scint: 40 bone scans; F hot: the 8 with a clear left/right count asymmetry (same rule as bench/tasks_nm.py)
    from tasks_nm import build_nm
    T = build_nm(Path(os.path.expanduser(a.bone)), 40, 0)
    hot = {Path(t["pkg"]).name: t["answer"] for t in T if t["type"] == "hot_side"}
    bs = list(bone); rng.shuffle(bs)
    for p in bs:
        add("scint", p, p / "renders/canonical.png", "bonescan", {})
    for p in [p for p in bs if p.name in hot]:
        add("hot", p, p / "renders/canonical.png", "bonescan", dict(hot_side_patient=hot[p.name]))

    (HERE / "items.json").write_text(json.dumps(dict(seed=SEED, tool_version=TOOL_VERSION, blocks={k: dict(role=v[0], label=v[1]) for k, v in BLOCKS.items()},
                                                     items=items), ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "set_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
    tpl = (HERE / "reader_template.html").read_text(encoding="utf-8")
    (HERE / "reader.html").write_text(tpl.replace("/*ITEMS*/[]", json.dumps(dict(seed=SEED, tool_version=TOOL_VERSION,
                                       blocks={k: dict(role=v[0], label=v[1]) for k, v in BLOCKS.items()}, items=items), ensure_ascii=False)), encoding="utf-8")
    counts = {b: sum(1 for i in items if i["block"] == b) for b in BLOCKS}
    print("items per block:", counts, "total", len(items)); print("wrote items.json, set_key.json, reader.html; renders under", out)


if __name__ == "__main__":
    main()
