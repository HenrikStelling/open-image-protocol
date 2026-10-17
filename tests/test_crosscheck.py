"""A measurement with validation_status cross_checked and a cross_check record validates against the schema and is spelled out in
the reference file; the default stays unvalidated."""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from oip.validate import validate_manifest
from oip.context import build_context

M = json.loads((Path(__file__).resolve().parents[1] / "spec/examples/synthetic-dx-chest.oip/oip.json").read_text())
CC = {"source": "CheXmask", "source_version": "1.0.0", "doi": "10.13026/3705-zg36", "date": "2026-10-17", "report": "chexmask-vindr-2026-10-17.md",
      "aggregate": {"n": 100, "ccc": 0.76, "bias": -0.023, "unit": "1", "bias_rel_pct": -4.5, "loa": [-0.08, 0.034], "within_10pct": 0.87},
      "this_image": {"source_value": 0.5, "unit": "1", "dice_heart": 0.93, "dice_lungs": 0.85, "source_quality_dice_rca_mean": 0.86}}


def _with_ctr(status, cc=None):
    m = copy.deepcopy(M)
    x = {"id": "ctr", "name": "Cardiothoracic ratio", "value": 0.48, "unit": "1", "method": "m", "assertion_level": "computed", "validation_status": status}
    if cc: x["cross_check"] = cc
    m["derived"]["measurements"] = [x]
    return m


def test_cross_checked_validates_and_is_spelled_out():
    m = _with_ctr("cross_checked", CC)
    assert validate_manifest(m) == []
    t = build_context(m)
    assert "cross-checked against CheXmask 1.0.0 (n = 100, CCC 0.76, bias -0.023); not a reference measurement" in t


def test_unvalidated_unchanged_and_unknown_status_rejected():
    assert validate_manifest(_with_ctr("unvalidated")) == [] and "| unvalidated |" in build_context(_with_ctr("unvalidated"))
    assert validate_manifest(_with_ctr("validated")) != []          # not a status: validated is a family of reserved values
    bad = _with_ctr("cross_checked", {"source": "x"})                 # record without version / date / aggregate
    assert validate_manifest(bad) != []
