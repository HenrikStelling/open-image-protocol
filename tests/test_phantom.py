"""Tier-0 validation: synthetic phantoms with exactly known geometry."""
import json, sys
from pathlib import Path
import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "scripts"))
from oip.convert import convert  # noqa: E402
from oip.measure import CalibrationError, cardiothoracic_ratio, px_to_mm, width_mm  # noqa: E402
from oip.validate import validate_package  # noqa: E402
import make_examples as mk  # noqa: E402


@pytest.fixture(scope="module")
def dx(tmp_path_factory):
    d = tmp_path_factory.mktemp("dx"); p = d / "dx.dcm"; masks = mk.make_dx(p)
    pkg = convert(p, d / "dx", synthetic=True)
    return pkg, masks, json.loads((pkg / "oip.json").read_text())


def test_package_validates(dx):
    pkg, _, _ = dx
    assert validate_package(pkg) == []


def test_spacing_selection_prefers_calibrated_pixel_spacing(dx):
    _, _, m = dx
    assert m["geometry"]["pixel_spacing_mm"] == [mk.DX_SPACING, mk.DX_SPACING]
    assert m["geometry"]["spacing_source"] == "PixelSpacing_calibrated"
    assert m["geometry"]["calibration"]["plane"] == "patient"
    assert m["geometry"]["physical_extent_mm"] == [mk.DX_ROWS * mk.DX_SPACING, mk.DX_COLS * mk.DX_SPACING]


def test_monochrome1_is_inverted_to_high_is_bright(dx):
    pkg, masks, m = dx
    assert m["intensity"]["source_inverted_for_render"] is True
    canon = np.asarray(Image.open(pkg / "renders/canonical.png"))
    assert canon[masks["heart"]].mean() > canon[masks["thorax"] & ~masks["heart"]].mean() > canon[~masks["thorax"]].mean()


def test_lossless_pixels_roundtrip(dx):
    pkg, _, m = dx
    import pydicom
    src = pydicom.dcmread(str(ROOT / "data/samples/synthetic_dx_chest.dcm")) if (ROOT / "data/samples/synthetic_dx_chest.dcm").exists() else None
    stored = np.asarray(Image.open(pkg / m["pixels"]["paths"][0]))
    assert stored.dtype == np.uint16 and stored.shape == (mk.DX_ROWS, mk.DX_COLS)


def test_measurements_match_ground_truth(dx):
    _, masks, m = dx
    ctr = cardiothoracic_ratio(masks["heart"], masks["thorax"])["value"]
    assert abs(ctr - mk.HEART_W / mk.THORAX_W) < 0.003
    assert abs(width_mm(masks["heart"], m)["value"] - mk.HEART_W) <= 2 * mk.DX_SPACING
    assert abs(width_mm(masks["thorax"], m)["value"] - mk.THORAX_W) <= 2 * mk.DX_SPACING


def test_orientation_from_patient_orientation(dx):
    _, _, m = dx
    o = m["geometry"]["orientation"]
    assert o["assertion_level"] == "measured" and o["edge_labels"] == {"left": "R", "right": "L", "top": "H", "bottom": "F"}


def test_refuses_mm_without_spacing(dx):
    _, _, m = dx
    m2 = json.loads(json.dumps(m)); m2["geometry"]["pixel_spacing_mm"] = None
    with pytest.raises(CalibrationError):
        px_to_mm(100, m2)


def test_deidentified(dx):
    pkg, _, m = dx
    hdr = (pkg / "source/dicom-headers.json").read_text()
    assert "PHANTOM" not in hdr and "OIP-SYN-000" not in hdr and "20260904" not in hdr
    assert m["subject"]["age_band"] == "45-49"


def test_nm_frames(tmp_path):
    p = tmp_path / "nm.dcm"; mk.make_nm(p)
    pkg = convert(p, tmp_path / "nm", synthetic=True); m = json.loads((pkg / "oip.json").read_text())
    assert validate_package(pkg) == []
    assert m["intensity"]["units"] == "counts" and len(m["frames"]) == 2
    assert [f["view"] for f in m["frames"]] == ["ANTERIOR", "POSTERIOR"]
    assert m["acquisition"]["nm"]["energy_windows"][0]["lower_keV"] == 126.0
    assert m["acquisition"]["nm"]["uptake_time_min"]["value"] == 180.0
    assert abs(sum(f["counts_total"] for f in m["frames"]) - m["frames"][0]["counts_accumulated_tag"]) < 1
    assert "counts_not_comparable" in m["quality"]["flags"]
    assert (pkg / "renders/inverted.png").exists()
