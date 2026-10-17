"""Internal thoracic width from a synthetic rib cage: an elliptical ring of rib "cortex" plus oblique bands crossing the lung
field; both conventions must find the inner margin of the ring, not the oblique bands, within one cortex thickness."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from oip.anatomy_cxas import internal_thoracic_width_px


def _cage(H=600, W=800, thick=12):
    yy, xx = np.mgrid[0:H, 0:W]; cy, cx = H / 2, W / 2; a, b = 300, 250        # outer semi-axes (cols, rows)
    outer = ((xx - cx) / a) ** 2 + ((yy - cy) / b) ** 2 <= 1
    inner = ((xx - cx) / (a - thick)) ** 2 + ((yy - cy) / (b - thick)) ** 2 <= 1
    ribs = outer & ~inner
    for k in range(-4, 5):                     # oblique posterior ribs crossing the lung field
        band = np.abs((yy - cy) - 0.35 * (xx - cx) - 60 * k) < 5
        ribs |= band & inner
    lungs = inner.copy()
    return ribs, lungs, int(2 * (a - thick))   # true inner width at the widest row


def test_inner_margin_found_by_both_conventions():
    ribs, lungs, truth = _cage()
    for conv, tol in (("q25", 0.04), ("v2", 0.02)):
        w = internal_thoracic_width_px(ribs, lungs, convention=conv)["width_px"]
        assert abs(w - truth) <= tol * truth, (conv, w, truth)


def test_q25_defined_where_v2_is_not():
    ribs, lungs, _ = _cage(thick=40)                  # a thick cortex exceeds v2's 3 % cap on every row
    assert internal_thoracic_width_px(ribs, lungs, convention="v2")["width_px"] == 0
    assert internal_thoracic_width_px(ribs, lungs, convention="q25")["width_px"] > 0
