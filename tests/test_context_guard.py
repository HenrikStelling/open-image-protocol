"""OEP-002 draft: the low-confidence-scale guard and the estimation caution in context.md (off by default)."""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from oip.context import build_context

M = json.loads((Path(__file__).resolve().parents[1] / "spec/examples/synthetic-dx-chest.oip/oip.json").read_text())


def _low():
    m = copy.deepcopy(M); m["geometry"]["calibration"]["confidence"] = "low"; m["geometry"]["spacing_source"] = "dataset_metadata"
    return m


def test_defaults_after_d031():
    # template 0.2.1: the estimation caution is on by default (adopted), the guard stays off (not adopted); False renders 0.2
    t = build_context(_low())
    assert "LOW-CONFIDENCE SCALE" not in t and "Estimating from the image" in t
    assert "Estimating from the image" not in build_context(_low(), estimation_caution=False)


def test_guard_only_when_low():
    assert "LOW-CONFIDENCE SCALE" in build_context(_low(), low_confidence_guard=True)
    assert "LOW-CONFIDENCE SCALE" not in build_context(copy.deepcopy(M), low_confidence_guard=True)   # example package is not low


def test_self_check_item_3_follows_the_measurements():
    m = _low(); m["derived"]["measurements"] = []
    assert "3. Can sizes be given in mm? → no (the spacing is nominal" in build_context(m, low_confidence_guard=True)
    m["derived"]["measurements"] = [{"id": "heart_width", "name": "x", "value": 120.0, "unit": "mm", "method": "m", "validation_status": "unvalidated"}]
    assert "only the values listed under `Computed measurements`" in build_context(m, low_confidence_guard=True)


def test_estimation_caution_flag():
    assert "Estimating from the image" in build_context(_low(), estimation_caution=True)
