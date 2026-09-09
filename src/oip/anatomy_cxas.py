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


def internal_thoracic_width_px(ribs: np.ndarray, spine_col: int | None = None) -> dict:
    """At each row, the inner margins are the innermost rib pixel on each side of the midline; width = max over rows of the
    distance between them. Midline = column of the rib mask's centroid unless given."""
    H, W = ribs.shape; mid = spine_col if spine_col is not None else int(np.round(np.where(ribs.any(axis=0))[0].mean())) if ribs.any() else W // 2
    best = (0, None)
    for r in range(H):
        row = ribs[r]
        left = np.where(row[:mid])[0]; right = np.where(row[mid:])[0]
        if left.size and right.size:
            li, ri = left.max(), mid + right.min()      # innermost rib pixel left of midline, innermost right of midline
            if ri - li > best[0]: best = (int(ri - li), r)
    return {"width_px": best[0], "row": best[1], "midline_col": mid}
