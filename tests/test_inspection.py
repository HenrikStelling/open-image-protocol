"""Tier-0 tests for the inspection sheet (render.inspection_sheet): fixed canvas, badges, inset, ruler, no pixel change."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from oip.render import inspection_sheet


def _phantom(h=1200, w=1000):
    a = np.zeros((h, w), np.uint8); a[300:900, 200:800] = 120; a[500:800, 350:650] = 200   # "thorax" + "heart"
    return a


def test_canvas_and_notes():
    im, notes = inspection_sheet(_phantom(), {"left": "R", "right": "L"}, [0.2, 0.2], heart_bbox=[500, 350, 800, 650])
    assert im.size == (1536, 1536) and im.mode == "L"
    assert any(n.startswith("badge left edge = R") for n in notes) and any(n.startswith("badge right edge = L") for n in notes)
    assert any(n.startswith("inset:") for n in notes) and any(n.startswith("ruler: 0-") for n in notes)


def test_badges_are_large_and_placed_at_the_edges():
    im, _ = inspection_sheet(_phantom(), {"left": "R", "right": "L"}, None)
    a = np.asarray(im)
    left, right = a[:, :136], a[:, -136:]
    assert (left == 255).sum() > 800 and (right == 255).sum() > 800       # white glyph pixels inside the badge columns


def test_no_spacing_gives_crossed_ruler():
    im, notes = inspection_sheet(_phantom(), {"left": "R", "right": "L"}, None)
    assert any("crossed-out" in n for n in notes)


def test_mirrored_input_keeps_labels():
    a = _phantom(); im1, n1 = inspection_sheet(a, {"left": "R", "right": "L"}, [0.2, 0.2], [500, 350, 800, 650])
    im2, n2 = inspection_sheet(a[:, ::-1], {"left": "R", "right": "L"}, [0.2, 0.2], [500, 1000 - 1 - 650, 800, 1000 - 1 - 350])
    assert n1[1] == n2[1] and n1[2] == n2[2]          # same badge notes
    assert np.asarray(im1)[:, :136].tolist() == np.asarray(im2)[:, :136].tolist()   # identical left badge column
