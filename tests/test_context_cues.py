"""Template 0.3 draft (OEP-003/004): verification cues are off by default and, when on, add pixel cues, a 'How to use this
file' section and self-check items that the file itself does not answer. Uses the synthetic chest example (PA, labels R/L,
calibrated spacing, annotated render) and a modified copy without spacing."""
import copy, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from oip.context import build_context  # noqa: E402

M = json.loads((ROOT / "spec/examples/synthetic-dx-chest.oip/oip.json").read_text())


def test_default_has_no_cues():
    txt = build_context(M)
    assert "Verify the stated orientation" not in txt
    assert "How to use this file" not in txt
    assert "template 0.3-draft" not in txt
    assert "5. Look at the image" not in txt


def test_cues_name_landmarks_and_the_labelled_edge():
    txt = build_context(M, verification_cues=True)
    assert "template 0.3-draft (verification cues)" in txt
    assert "## How to use this file" in txt
    assert "cardiac apex" in txt and "aortic knob" in txt
    # edge labels are left=R, right=L, so the L edge is the RIGHT edge
    assert "toward the image edge labelled L (here the RIGHT edge)" in txt
    assert "dextrocardia" in txt


def test_self_check_gains_pixel_items_without_answers():
    txt = build_context(M, verification_cues=True)
    assert "1. Which anatomical side does this file state" in txt
    assert "5. Look at the image, not the file: on which image side is the cardiac apex?" in txt
    assert "6. On the annotated render, do the printed edge labels read left = R, right = L?" in txt
    # items 5 and 6 carry no arrow answer
    item5 = [l for l in txt.splitlines() if l.startswith("5. ")][0]
    assert "→" not in item5


def test_scale_cue_only_when_spacing_and_annotated_render():
    with_sp = build_context(M, verification_cues=True)
    assert "scale bar on the annotated render represents 50 mm" in with_sp
    m2 = copy.deepcopy(M); m2["geometry"]["pixel_spacing_mm"] = None
    without = build_context(m2, verification_cues=True)
    assert "scale bar on the annotated render represents 50 mm" not in without
    assert "cardiac apex" in without   # orientation cue does not depend on spacing


def test_no_orientation_cue_when_orientation_unknown():
    m2 = copy.deepcopy(M); m2["geometry"]["orientation"] = {"assertion_level": "unknown", "edge_labels": {}}
    txt = build_context(m2, verification_cues=True)
    assert "Verify the stated orientation" not in txt
    assert "5. Look at the image" not in txt


def test_scintigraphy_cue_is_about_the_view_not_a_side():
    m2 = copy.deepcopy(M); m2["acquisition"]["modality_family"] = "scintigraphy"; m2["acquisition"]["modality"]["value"] = "NM"
    txt = build_context(m2, verification_cues=True)
    assert "Verify the stated view against the image" in txt
    assert "cardiac apex" not in txt
    assert "Left and right cannot be told reliably from a normal skeleton" in txt
