"""Draw the image set of the pre-registered confirmatory round (docs/paper/preregistration-draft-2026-11-02.md, section 4).

Rule, fixed before the draw: from the 1,000-package VinDr-CXR store (the seed-0 sample of the Kaggle training set converted on
2026-09-06), take every package that (a) was never shown to a model in any benchmark run, never in the reader study and never in
the marker review, (b) carries inferred L/R edge labels, (c) has the stored anatomy masks and passes the pixel-side orientation
check with a clear cardiac cue (bench/tasks.py clear_cue, confidence >= 0.9, offset >= 5 % of thoracic width: the same gate as
round 3a), and (d) has a canonical render. Shuffle-sample 90 of them with random.Random(SEED); the first N_SET are the set,
the remaining ones are the reserve, used in order only for the technical replacements named in the pre-registration.

Usage:
  python bench/confirm/draw_set.py --store /Volumes/Video\\ Storage/oip/oip/vindr [--out ~/oip-bench/vindr-confirm]
      draws, stages (copies) the set into --out, writes bench/confirm/confirm_set.json with sha256 of every staged file that
      enters a prompt (oip.json, renders/canonical.png, the masks that decide eligibility) and the source DICOM hash.
  python bench/confirm/draw_set.py --verify [--out ~/oip-bench/vindr-confirm]
      recomputes the hashes of the staged store and compares them with confirm_set.json (run before the first model call).
The exclusion list (a) is computed from the repository (bench/results/*/tasks.json, the paper stores, bench/reader/set_key.json,
bench/marker_review.json) and written into confirm_set.json so that the draw is reproducible from the frozen commit alone.
"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, random, shutil, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "bench"))

SEED = 20261105          # fixed in the pre-registration; never change after registration
N_SET = 80               # images in the confirmatory set
N_RESERVE = 10           # replacements, used in order
STORE_DEFAULT = "/Volumes/Video Storage/oip/oip-packages/vindr"   # the external SSD; data/oip in the repo links to oip-packages


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def used_packages() -> dict[str, list[str]]:
    """Package names that appeared anywhere before the confirmatory round, by source."""
    used: dict[str, set] = {}
    def mark(name: str, src: str) -> None:
        used.setdefault(name, set()).add(src)
    for tj in glob.glob(str(ROOT / "bench/results/*/tasks.json")):
        try:
            T = json.load(open(tj))
        except Exception:
            continue
        for t in (T if isinstance(T, list) else T.get("tasks", [])):
            p = t.get("pkg") or ""
            if p:
                mark(Path(p).name, "benchmark run")
    bench = Path(os.environ.get("OIP_BENCH_DIR", Path.home() / "oip-bench"))
    for store in ("vindr-paper", "nih-paper", "bonescan", "smoke"):
        for p in (bench / store).glob("*.oip"):
            mark(p.name, f"store {store}")
    key = ROOT / "bench/reader/set_key.json"
    if key.exists():
        for v in json.loads(key.read_text()).values():
            mark(Path(v["pkg"]).name, "reader study")
    mr = ROOT / "bench/marker_review.json"
    if mr.exists():
        for n in json.loads(mr.read_text()).get("excluded", {}):
            mark(n, "marker review")
    return {k: sorted(v) for k, v in sorted(used.items())}


def eligible(pkg: Path) -> tuple[bool, str]:
    from tasks import clear_cue, THRESHOLDS
    if not (pkg / "oip.json").exists():
        return False, "no manifest"
    m = json.loads((pkg / "oip.json").read_text())
    el = m["geometry"]["orientation"].get("edge_labels") or {}
    if el.get("left") not in ("L", "R"):
        return False, "no L/R edge labels"
    if not (pkg / "derived/masks/heart.png").exists():
        return False, "no heart mask"
    if not (pkg / "renders/canonical.png").exists():
        return False, "no canonical render"
    if not m.get("identity", {}).get("source_hash"):
        return False, "no source hash"
    if not clear_cue(pkg, m, THRESHOLDS["clear_cue_min_confidence"]):
        return False, "no clear cardiac cue"
    return True, "ok"


def stage(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=False)


def record(pkg: Path) -> dict:
    m = json.loads((pkg / "oip.json").read_text()); g = m["geometry"]
    files = ["oip.json", "renders/canonical.png", "derived/masks/heart.png", "derived/masks/lung_left.png", "derived/masks/lung_right.png"]
    return dict(package=pkg.name, image_id=pkg.name.replace(".oip", ""), source_dicom_sha256=m["identity"]["source_hash"],
                rows=g["rows"], columns=g["columns"], pixel_spacing_mm=g.get("pixel_spacing_mm"), spacing_source=g.get("spacing_source"),
                edge_labels=g["orientation"].get("edge_labels"), validation_status=(m.get("derived") or {}).get("validation_status"),
                files={f: sha256(pkg / f) for f in files if (pkg / f).exists()})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", default=STORE_DEFAULT, help="the 1,000-package VinDr store (external drive)")
    ap.add_argument("--out", default=str(Path(os.environ.get("OIP_BENCH_DIR", Path.home() / "oip-bench")) / "vindr-confirm"))
    ap.add_argument("--verify", action="store_true", help="recompute the staged store's hashes against confirm_set.json")
    a = ap.parse_args()
    out = Path(os.path.expanduser(a.out)); setfile = HERE / "confirm_set.json"

    if a.verify:
        S = json.loads(setfile.read_text()); bad = 0; reserve_dir = out.parent / (out.name + "-reserve")
        extra = sorted(p.name for p in out.glob("*.oip") if p.name not in {i["package"] for i in S["set"]})
        if extra:
            print("NOT IN THE REGISTERED SET but staged:", ", ".join(extra)); bad += len(extra)
        for item in S["set"] + S["reserve"]:
            pkg = (out if item in S["set"] else reserve_dir) / item["package"]
            if not pkg.exists():
                if item in S["set"]:
                    print("MISSING", item["package"]); bad += 1
                continue
            for f, h in item["files"].items():
                if sha256(pkg / f) != h:
                    print("HASH MISMATCH", item["package"], f); bad += 1
        print("verified", len(S["set"]), "set packages (+ staged reserve) against", setfile.name, "->", "OK" if bad == 0 else f"{bad} problem(s)")
        sys.exit(1 if bad else 0)

    store = Path(os.path.expanduser(a.store))
    pkgs = sorted(p for p in store.glob("*.oip") if (p / "oip.json").exists())
    if not pkgs:
        sys.exit(f"no packages under {store}; mount the drive or pass --store")
    used = used_packages()
    reasons: dict[str, int] = {}; pool = []
    for p in pkgs:
        if p.name in used:
            reasons["used before"] = reasons.get("used before", 0) + 1; continue
        ok, why = eligible(p)
        reasons[why] = reasons.get(why, 0) + 1
        if ok:
            pool.append(p.name)
    pool.sort()
    if len(pool) < N_SET + N_RESERVE:
        sys.exit(f"only {len(pool)} eligible packages, need {N_SET + N_RESERVE}")
    drawn = random.Random(SEED).sample(pool, N_SET + N_RESERVE)
    reserve_dir = out.parent / (out.name + "-reserve")   # kept apart: bench/run.py --n 80 must see exactly the 80 set packages
    out.mkdir(parents=True, exist_ok=True); reserve_dir.mkdir(parents=True, exist_ok=True)
    for name in drawn[:N_SET]:
        stage(store / name, out / name)
    for name in drawn[N_SET:]:
        stage(store / name, reserve_dir / name)
    items = [record(out / n) for n in drawn[:N_SET]] + [record(reserve_dir / n) for n in drawn[N_SET:]]
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    S = dict(seed=SEED, n_set=N_SET, n_reserve=N_RESERVE, drawn_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"), harness_commit=commit,
             store=str(store), staged_to=str(out), rule=(__doc__ or "").split("\n\n")[1].replace("\n", " "),
             counts=dict(store=len(pkgs), eligible=len(pool), by_reason=reasons),
             excluded_used={k: v for k, v in used.items() if k in {p.name for p in pkgs}},
             set=items[:N_SET], reserve=items[N_SET:])
    setfile.write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding="utf-8")
    cal = sum(1 for i in items[:N_SET] if i["spacing_source"] not in (None, "none"))
    print(f"store {len(pkgs)}, eligible {len(pool)} ({reasons}); drew {N_SET} + {N_RESERVE} reserve with seed {SEED}; "
          f"{cal} of {N_SET} with a header pixel spacing; staged under {out}; wrote {setfile}")


if __name__ == "__main__":
    main()
