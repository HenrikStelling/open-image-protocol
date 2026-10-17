"""Rib-based internal thoracic width vs the lung-union width, CTR variants against the VinDr cardiomegaly label, heart width
three ways (PSPNet, CXAS, CheXmask). Needs `derived/masks_cxas/` in the packages (scripts/cxas_worker.py) and the CheXmask per-image
file from bench/chexmask_validate.py. Report: docs/reports/itw-cxas-2026-10-17.md. Evaluation on the 100 VinDr paper packages with CXAS masks: internal thoracic width (rib inner margins, two conventions) vs the
lung-union width; CTR variants against the VinDr 'Cardiomegaly' label (AUC); heart width three ways (PSPNet, CXAS, CheXmask)."""
import json, pathlib, sys
import numpy as np
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "bench"))
from oip.anatomy_cxas import internal_thoracic_width_px
from tasks import vindr_labels


def extent(mask):
    c = np.flatnonzero(mask.any(axis=0)); return int(c.max() - c.min() + 1) if c.size else 0




def auc(pos, neg):
    return (sum(1 for p in pos for n in neg if p > n) + 0.5 * sum(1 for p in pos for n in neg if p == n)) / (len(pos) * len(neg))


labels = vindr_labels(); chex = {r["id"]: r for r in json.loads((pathlib.Path.home() / "oip-work/bench/results/_chexmask/vindr-paper.json").read_text())}
rows = []
for p in sorted((pathlib.Path.home() / "oip-bench/vindr-paper").glob("*.oip")):
    cx = p / "derived/masks_cxas"
    if not (cx / "ribs.png").exists(): continue
    ld = lambda f: np.asarray(Image.open(f).convert("L")) > 127
    ribs = ld(cx / "ribs.png"); lungs = ld(p / "derived/masks/lung_left.png") | ld(p / "derived/masks/lung_right.png")
    sid = p.name.split(".")[0]; lu = extent(lungs); hp = extent(ld(p / "derived/masks/heart.png")); hc = extent(ld(cx / "heart.png"))
    v2 = internal_thoracic_width_px(ribs, lungs, "v2")["width_px"]; q = internal_thoracic_width_px(ribs, lungs, "q25")["width_px"]
    rows.append({"id": sid, "lung_union": lu, "itw_v2": v2, "itw_q25": q, "heart_pspnet": hp, "heart_cxas": hc, "heart_chexmask": chex[sid]["heart_px_theirs"] if sid in chex else None,
                 "lung_union_chexmask": chex[sid]["thorax_px_theirs"] if sid in chex else None, "cardiomegaly": "Cardiomegaly" in labels.get(sid, [])})
out = ROOT / "bench/results/_chexmask/itw_cxas_100.json"; out.write_text(json.dumps(rows, indent=0))
n = len(rows); print("packages with CXAS masks:", n)
for k in ("itw_v2", "itw_q25"):
    rat = [r[k] / r["lung_union"] for r in rows if r[k]]
    print(f"{k} / lung-union: n={len(rat)} median {np.median(rat):.3f} IQR {np.percentile(rat, 25):.3f}–{np.percentile(rat, 75):.3f} min {min(rat):.3f} max {max(rat):.3f}")
hc = [r["heart_cxas"] / r["heart_pspnet"] for r in rows]; hx = [r["heart_chexmask"] / r["heart_pspnet"] for r in rows if r["heart_chexmask"]]; cc = [r["heart_chexmask"] / r["heart_cxas"] for r in rows if r["heart_chexmask"]]
print(f"heart width: CXAS/PSPNet median {np.median(hc):.3f}, CheXmask/PSPNet {np.median(hx):.3f}, CheXmask/CXAS {np.median(cc):.3f}")
pos = [r for r in rows if r["cardiomegaly"]]; neg = [r for r in rows if not r["cardiomegaly"]]
print(f"cardiomegaly label: {len(pos)} of {n}")
for name, f in (("CTR lung-union (package)", lambda r: r["heart_pspnet"] / r["lung_union"]), ("CTR rib v2", lambda r: r["heart_pspnet"] / r["itw_v2"] if r["itw_v2"] else None),
                ("CTR rib q25", lambda r: r["heart_pspnet"] / r["itw_q25"] if r["itw_q25"] else None), ("CTR CXAS heart / lung-union", lambda r: r["heart_cxas"] / r["lung_union"]),
                ("CTR CheXmask heart / CheXmask lungs", lambda r: r["heart_chexmask"] / r["lung_union_chexmask"] if r["heart_chexmask"] else None)):
    P = [f(r) for r in pos if f(r)]; N = [f(r) for r in neg if f(r)]
    best = max(((sum(1 for p in P if p > t) + sum(1 for x in N if x <= t)) / (len(P) + len(N)), t) for t in [x / 100 for x in range(35, 75)])
    print(f"{name:38s} AUC {auc(P, N):.3f} | mean {np.mean(P):.3f} vs {np.mean(N):.3f} | > 0.50 among unlabelled {sum(1 for x in N if x > 0.5)}/{len(N)} | best acc {best[0]:.2f} at {best[1]:.2f}")
