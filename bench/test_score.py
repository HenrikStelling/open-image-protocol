"""Unit tests for bench/score.py 0.3 (run: ~/oip-venv/bin/python -m pytest bench/test_score.py -q)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import score, SCORER_VERSION


def T(type_, answer, **kw):
    return dict(type=type_, answer=answer, **kw)


def test_version():
    assert SCORER_VERSION == "0.3"


# 1. abstention flag independent of correctness
def test_decisive_wrong_no_is_not_abstention():
    s = score(T("scale_available", "yes"), "No pixel spacing is visible, so distances cannot be reliably stated. So the answer is 'no'. No.")
    assert s["correct"] is False and "abstained" not in s


def test_cannot_on_no_item_is_abstention():
    s = score(T("scale_available", "no"), "I cannot determine this from the image alone.")
    assert s["correct"] is False and s["abstained"] is True


def test_abstain_wording_with_decisive_side_is_not_abstention():
    s = score(T("left_edge", "patient right"), "I cannot be certain, but by convention the patient right is at the left edge.")
    assert s["correct"] is True and "abstained" not in s


def test_pure_abstention_left_edge():
    s = score(T("left_edge", "patient right"), "It is not possible to determine the orientation from this image.")
    assert s["correct"] is False and s["abstained"] is True


def test_no_number_is_abstention():
    s = score(T("heart_mm", 130.0, tolerance=0.1), "Without calibration this cannot be estimated.")
    assert s["abstained"] is True


# 2. unit normalisation
def test_cm_with_unit_word():
    s = score(T("heart_mm", 130.0, tolerance=0.1), "Approximately 13 cm.")
    assert s["value"] == 130.0 and s["correct"] is True


def test_cm_mentioned_small_value():
    s = score(T("heart_mm", 130.0, tolerance=0.1), "Estimated transverse cardiac diameter: about 12.5 (in cm).")
    assert s["value"] == 125.0 and s["correct"] is True


def test_mm_unchanged():
    s = score(T("heart_mm", 130.0, tolerance=0.1), "Answer: 128 mm")
    assert s["value"] == 128.0 and s["correct"] is True


def test_small_value_without_cm_stays():
    s = score(T("heart_mm", 130.0, tolerance=0.1), "Answer: 13")
    assert s["value"] == 13.0 and s["correct"] is False


# 3. flip check
def test_flip_do_not_agree():
    assert score(T("flip_check", "mirrored"), "The labels do not agree with the image.")["correct"] is True


def test_flip_doesnt_agree():
    assert score(T("flip_check", "mirrored"), "It doesn't agree; the image is reversed.")["correct"] is True


def test_flip_final_line_wins():
    reply = "The stated orientation says patient right on the left edge. The heart appears on the image right, which would agree with... let me check.\n\nAnswer: mirrored"
    assert score(T("flip_check", "mirrored"), reply)["correct"] is True


def test_flip_agree_plain():
    assert score(T("flip_check", "agree"), "Agree.")["correct"] is True


def test_flip_disagree_not_agree():
    assert score(T("flip_check", "agree"), "I disagree, it is mirrored.")["correct"] is False


def test_nm_aliases():
    assert score(T("flip_check_nm", "agree"), "agree")["correct"] is True
    s = score(T("counts_semantics", "no"), "No, counts depend on dose and time.")
    assert s["correct"] is True and "abstained" not in s


# 4./5. reasoning stripped for every task; abstention pattern narrowed; "cannot be compared" is a decisive no
def test_think_tail_only():
    reply = "Could be patient left or patient right... convention says right.</think>Patient right"
    s = score(T("left_edge", "patient right"), reply)
    assert s["correct"] is True


def test_agreed_counts_as_agree():
    assert score(T("flip_check", "agree"), "agreed")["correct"] is True


def test_cannot_be_compared_is_no():
    s = score(T("counts_semantics", "no"), "The brightness cannot be directly compared with another patient's scan.")
    assert s["correct"] is True and "abstained" not in s


def test_cannot_determine_is_abstention_not_no():
    s = score(T("counts_semantics", "no"), "I cannot determine that from a single image.")
    assert s["correct"] is False and s["abstained"] is True


def test_yes_before_no_phrase():
    s = score(T("scale_available", "yes"), "Yes, 0.14 mm per pixel; fine detail cannot be measured though.")
    assert s["correct"] is True
