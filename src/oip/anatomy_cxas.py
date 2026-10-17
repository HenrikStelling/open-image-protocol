"""Second anatomy source: CXAS (159 structures incl. individual ribs), run in its own venv via subprocess.
Provides the INTERNAL thoracic width from the inner rib margins — the clinical CTR denominator — as an alternative to
the lung-mask union used by the PSPNet adapter."""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

CXAS_PY = Path(os.environ.get("OIP_CXAS_PYTHON", Path.home() / "cxas-venv/bin/python"))   # python of the isolated CXAS venv (REPRODUCE.md)
WORKER = Path(__file__).resolve().parents[2] / "scripts/cxas_worker.py"


def run_cxas(pkg: Path) -> dict[str, np.ndarray]:
    out = pkg / "derived/masks_cxas"; out.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(CXAS_PY), str(WORKER), str(pkg / "renders/canonical.png"), str(out)], check=True, capture_output=True, text=True)
    return {k: np.asarray(Image.open(out / f"{k}.png")) > 127 for k in ("ribs", "heart", "lung_left", "lung_right")}


def _lateral_runs(ribs: np.ndarray, lungs: np.ndarray | None):
    """Per lung-bearing row: (row, left outer col, left run length, right outer col, right run length) of the lateral-most rib
    run on each side of the midline. Rows with ribs on one side only are skipped."""
    H, W = ribs.shape; mid = W // 2
    rows = range(H)
    if lungs is not None and lungs.any():
        rr = np.flatnonzero(lungs.any(axis=1)); rows = range(int(rr.min()), int(rr.max()) + 1)
    out = []
    for r in rows:
        row = ribs[r]
        idx = np.flatnonzero(np.diff(np.concatenate([[0], row.astype(np.int8), [0]])))
        runs = list(zip(idx[::2], idx[1::2] - 1))
        left = [x for x in runs if x[1] < mid]; right = [x for x in runs if x[0] > mid]
        if left and right:
            lo, ro = left[0], right[-1]
            out.append((r, int(lo[0]), int(lo[1] - lo[0] + 1), int(ro[1]), int(ro[1] - ro[0] + 1)))
    return out


def internal_thoracic_width_px(ribs: np.ndarray, lungs: np.ndarray | None = None, convention: str = "q25") -> dict:
    """Internal thoracic width = distance between the inner margins of the lateral chest wall at the widest level, from the
    union of the CXAS rib masks. The lateral-most rib run on each row marks the outer chest wall; its inner margin is
    - convention "q25": the outer edge minus the 25th percentile of the lateral run lengths over all rows (the tangential rib
      cortex; robust to oblique posterior ribs merging with the lateral segment in some rows; always defined), or
    - convention "v2": the inner end of the run itself, with rows whose lateral run exceeds 3 % of the image width skipped
      (fails when every row is skipped).
    Width = maximum over the lung-bearing rows. On 100 VinDr paper images (2026-10-17, `docs/reports/itw-cxas-2026-10-17.md`) the
    q25 width is 3.4 % and the v2 width 1.5 % narrower than the lung-union width the converter uses, i.e. within the resolution
    of a 512-px rib mask; the September version of this function walked along the contiguous run into oblique ribs and gave
    widths down to 74 % of the lung union — it is withdrawn."""
    lat = _lateral_runs(ribs, lungs)
    W = ribs.shape[1]
    if convention == "v2":
        cand = [(ro - lo_len_end, r, lo_len_end, ro) for (r, lo, ll, ro_out, rl) in lat for lo_len_end, ro in [(lo + ll - 1, ro_out - rl + 1)]
                if ll <= 0.03 * W and rl <= 0.03 * W and ro - lo_len_end > 0]
        if not cand: return {"width_px": 0, "rows_used": 0, "convention": "v2"}
        best = max(cand); return {"width_px": int(best[0]), "row": int(best[1]), "left_inner_col": int(best[2]), "right_inner_col": int(best[3]), "rows_used": len(cand), "convention": "v2"}
    if len(lat) < 10: return {"width_px": 0, "rows_used": len(lat), "convention": "q25"}
    tl = float(np.percentile([x[2] for x in lat], 25)); tr = float(np.percentile([x[4] for x in lat], 25))
    best = max(((x[3] - tr) - (x[1] + tl), x[0], x[1] + tl, x[3] - tr) for x in lat)
    return {"width_px": int(round(best[0])), "row": int(best[1]), "left_inner_col": int(round(best[2])), "right_inner_col": int(round(best[3])),
            "rows_used": len(lat), "thickness_px": [round(tl, 1), round(tr, 1)], "convention": "q25"}
