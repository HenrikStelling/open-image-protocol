"""Second anatomy source: CXAS (159 structures incl. individual ribs), run in its own venv via subprocess.
Provides the INTERNAL thoracic width from the inner rib margins — the clinical CTR denominator — as an alternative to
the lung-mask union used by the PSPNet adapter."""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

CXAS_PY = Path.home() / "cxas-venv/bin/python"
WORKER = Path(__file__).resolve().parents[2] / "scripts/cxas_worker.py"


def run_cxas(pkg: Path) -> dict[str, np.ndarray]:
    out = pkg / "derived/masks_cxas"; out.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(CXAS_PY), str(WORKER), str(pkg / "renders/canonical.png"), str(out)], check=True, capture_output=True, text=True)
    return {k: np.asarray(Image.open(out / f"{k}.png")) > 127 for k in ("ribs", "heart", "lung_left", "lung_right")}


def internal_thoracic_width_px(ribs: np.ndarray, lungs: np.ndarray | None = None) -> dict:
    """Internal thoracic width = distance between the INNER margins of the lateral chest wall at the widest level.
    Per row: outermost rib pixel on each side, then walk inward to the end of that contiguous rib run (the inner cortex of the
    lateral rib segment). Rows are restricted to the lung-bearing region when lung masks are given. Width = max over rows."""
    H, W = ribs.shape
    rows = range(H)
    if lungs is not None and lungs.any():
        rr = np.where(lungs.any(axis=1))[0]; rows = range(int(rr.min()), int(rr.max()) + 1)
    best = (0, None, None, None)
    for r in rows:
        idx = np.where(ribs[r])[0]
        if idx.size < 2: continue
        l = int(idx.min()); li = l
        while li + 1 < W and ribs[r, li + 1]: li += 1          # end of the left rib run -> inner margin
        rt = int(idx.max()); ri = rt
        while ri - 1 >= 0 and ribs[r, ri - 1]: ri -= 1          # start of the right rib run -> inner margin
        if ri - li > best[0] and (rt - l) > 0.5 * W * 0.4:      # ignore rows where only one side is segmented
            best = (int(ri - li), r, li, ri)
    return {"width_px": best[0], "row": best[1], "left_inner_col": best[2], "right_inner_col": best[3]}
