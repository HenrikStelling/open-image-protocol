"""`oip check` (pixel-side orientation check): pure geometry on synthetic masks, the mirror flips the verdict, the
manifest write validates against the schema, and context.md reports the result next to the orientation line."""
import copy, json, shutil, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from oip.check import CHECK_ID, FLAG, orientation_evidence, check_orientation, combine_two_pass, signed_offset  # noqa: E402
from oip.validate import validate_package  # noqa: E402


def test_two_pass_cancels_the_model_prior():
    # true side signal s = +0.06, model prior p = +0.03 (pulls toward the conventional side in image coordinates)
    c = combine_two_pass(0.06 + 0.03, -0.06 + 0.03)
    assert c["result"] == "consistent" and abs(c["prior_free_offset_frac"] - 0.06) < 1e-9 and abs(c["model_prior_frac"] - 0.03) < 1e-9 and c["confidence"] == 0.9
    # the same image mirrored: the two passes swap -> exactly the opposite verdict, same prior
    c2 = combine_two_pass(-0.06 + 0.03, 0.06 + 0.03)
    assert c2["result"] == "inconsistent" and abs(c2["prior_free_offset_frac"] + 0.06) < 1e-9
    # a single pass on that mirrored image would have read -0.03: below the 5 % strong threshold, and with a larger prior it would flip sign
    assert combine_two_pass(0.01, -0.005)["result"] == "indeterminate"


def test_signed_offset_follows_the_l_edge():
    r = {"evidence": {"l_edge": "right", "structures": {"heart": {"centroid_offset_frac": 0.07}}}}
    assert signed_offset(r) == 0.07
    r["evidence"]["l_edge"] = "left"
    assert signed_offset(r) == -0.07
    assert signed_offset({"evidence": {}}) is None

W, H = 1000, 1000
EL = {"left": "R", "right": "L", "top": "H", "bottom": "F"}


def _masks(heart_center_col: int, aorta_center_col: int | None = None):
    m = {k: np.zeros((H, W), bool) for k in ("heart", "aorta", "lung_left", "lung_right")}
    m["lung_right"][200:800, 150:450] = True     # image left  = patient right
    m["lung_left"][200:800, 550:850] = True      # image right = patient left
    m["heart"][450:750, heart_center_col - 150: heart_center_col + 150] = True
    if aorta_center_col is not None:
        m["aorta"][300:420, aorta_center_col - 40: aorta_center_col + 40] = True
    else:
        m["aorta"] = None
    return m


def test_heart_toward_l_edge_is_consistent():
    r = orientation_evidence(_masks(560, 540), W, EL)
    assert r["result"] == "consistent" and r["confidence"] >= 0.7
    assert r["evidence"]["structures"]["heart"]["toward"] == "L edge"
    assert r["evidence"]["midline_source"] == "lung-union bbox centre"


def test_mirrored_masks_flip_to_inconsistent():
    m = _masks(560, 540)
    mirrored = {k: (v[:, ::-1] if v is not None else None) for k, v in m.items()}
    r = orientation_evidence(mirrored, W, EL)
    assert r["result"] == "inconsistent"
    assert r["evidence"]["structures"]["heart"]["toward"] == "R edge"


def test_same_masks_with_flipped_labels_are_inconsistent():
    r = orientation_evidence(_masks(560, 540), W, {"left": "L", "right": "R"})
    assert r["result"] == "inconsistent"


def test_midline_heart_is_indeterminate():
    r = orientation_evidence(_masks(500), W, EL)
    assert r["result"] == "indeterminate" and "midline" in r["reason"]


def test_no_l_label_is_indeterminate():
    r = orientation_evidence(_masks(560), W, {"left": None, "right": None})
    assert r["result"] == "indeterminate"


def test_write_validates_and_renders(tmp_path):
    src = ROOT / "spec/examples/synthetic-dx-chest.oip"
    pkg = tmp_path / "dx.oip"; shutil.copytree(src, pkg)
    (pkg / "derived/masks").mkdir(parents=True, exist_ok=True)
    from PIL import Image
    m = json.loads((pkg / "oip.json").read_text()); cols = m["geometry"]["columns"]; rows = m["geometry"]["rows"]
    heart = np.zeros((rows, cols), bool); heart[rows // 2: rows // 2 + rows // 5, int(cols * 0.52): int(cols * 0.72)] = True
    Image.fromarray((heart * 255).astype(np.uint8)).save(pkg / "derived/masks/heart.png")
    rec = check_orientation(pkg, write=True, two_pass=False)
    assert rec["result"] == "consistent" and rec["id"] == CHECK_ID and rec["evidence"]["single_pass"] is True
    m2 = json.loads((pkg / "oip.json").read_text())
    assert m2["quality"]["checks"][0]["result"] == "consistent" and FLAG not in m2["quality"]["flags"]
    assert validate_package(pkg) == []
    txt = (pkg / "context.md").read_text()
    assert "cross-checked against the pixels [computed]: CONSISTENT" in txt
    # a failing check sets the flag, the caution and the warning line; running again replaces the record
    m2["geometry"]["orientation"]["edge_labels"] = {"left": "L", "right": "R", "top": "H", "bottom": "F"}
    (pkg / "oip.json").write_text(json.dumps(m2))
    rec2 = check_orientation(pkg, write=True, two_pass=False)
    m3 = json.loads((pkg / "oip.json").read_text())
    assert rec2["result"] == "inconsistent" and FLAG in m3["quality"]["flags"] and len(m3["quality"]["checks"]) == 1
    assert validate_package(pkg) == []
    txt = (pkg / "context.md").read_text()
    assert "INCONSISTENT" in txt and "pixel check contradicts the stated left/right" in txt


def test_no_write_leaves_package_untouched(tmp_path):
    src = ROOT / "spec/examples/synthetic-dx-chest.oip"
    pkg = tmp_path / "dx.oip"; shutil.copytree(src, pkg)
    before = (pkg / "oip.json").read_text()
    rec = check_orientation(pkg, write=False, two_pass=False)   # no masks in the example -> segments the render (torch) or indeterminate
    assert rec["result"] in ("consistent", "inconsistent", "indeterminate")
    assert (pkg / "oip.json").read_text() == before
