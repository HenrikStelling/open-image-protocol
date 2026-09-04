"""Build example OIP packages: synthetic DX phantom, synthetic NM whole-body phantom, and pydicom sample CT/MR.
Synthetic phantoms have exactly known geometry so they double as measurement ground truth (Q11 Tier 0)."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.sequence import Sequence
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from oip.convert import add_measurements, convert  # noqa: E402
from oip.measure import cardiothoracic_ratio, width_mm  # noqa: E402

OUT = ROOT / "spec" / "examples"
SAMPLES = ROOT / "data" / "samples"

# Phantom ground truth (mm)
DX_SPACING = 0.2          # mm/px, patient plane (calibrated)
THORAX_W, THORAX_H = 280.0, 320.0
HEART_W, HEART_H = 130.0, 110.0
DX_ROWS, DX_COLS = 1800, 1500   # 360 x 300 mm


def _base(modality, sop_class, rows, cols):
    meta = FileMetaDataset(); meta.MediaStorageSOPClassUID = sop_class; meta.MediaStorageSOPInstanceUID = generate_uid()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    ds = FileDataset(None, {}, file_meta=meta, preamble=b"\0" * 128)
    ds.SOPClassUID = sop_class; ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
    ds.StudyInstanceUID = generate_uid(); ds.SeriesInstanceUID = generate_uid()
    ds.Modality = modality; ds.PatientName = "PHANTOM^SYNTHETIC"; ds.PatientID = "OIP-SYN-000"; ds.PatientSex = "O"; ds.PatientAge = "047Y"
    ds.StudyDate = "20260904"; ds.Manufacturer = "OIP synthetic"; ds.ManufacturerModelName = "phantom-v1"
    ds.Rows, ds.Columns = rows, cols; ds.SamplesPerPixel = 1; ds.PixelRepresentation = 0
    return ds


def _ellipse(rows, cols, cy, cx, ry, rx):
    yy, xx = np.mgrid[:rows, :cols]
    return ((yy - cy) / ry) ** 2 + ((xx - cx) / rx) ** 2 <= 1.0


def make_dx(path: Path):
    """MONOCHROME1 12-bit chest-like phantom: thorax ellipse (280 mm) + heart ellipse (130 mm) -> CTR 0.4643."""
    rows, cols = DX_ROWS, DX_COLS
    # attenuation image (high = bright in MONOCHROME2 sense), then stored inverted as MONOCHROME1
    att = np.full((rows, cols), 300.0)
    thorax = _ellipse(rows, cols, rows / 2, cols / 2, THORAX_H / 2 / DX_SPACING, THORAX_W / 2 / DX_SPACING)
    heart = _ellipse(rows, cols, rows * 0.55, cols * 0.52, HEART_H / 2 / DX_SPACING, HEART_W / 2 / DX_SPACING)
    att[thorax] = 900.0; att[heart] = 2200.0
    rng = np.random.default_rng(0); att += rng.normal(0, 25, att.shape)
    stored = np.clip(4095 - att, 0, 4095).astype(np.uint16)   # MONOCHROME1: low value = white
    ds = _base("DX", "1.2.840.10008.5.1.4.1.1.1.1", rows, cols)
    ds.ImageType = ["ORIGINAL", "PRIMARY"]; ds.BodyPartExamined = "CHEST"; ds.ViewPosition = "PA"; ds.PatientOrientation = ["L", "F"]
    ds.PhotometricInterpretation = "MONOCHROME1"; ds.BitsAllocated = 16; ds.BitsStored = 12; ds.HighBit = 11
    ds.PixelSpacing = [DX_SPACING, DX_SPACING]; ds.PixelSpacingCalibrationType = "GEOMETRY"; ds.PixelSpacingCalibrationDescription = "synthetic, patient plane"
    ds.ImagerPixelSpacing = [DX_SPACING * 1.1, DX_SPACING * 1.1]; ds.EstimatedRadiographicMagnificationFactor = 1.1
    ds.DistanceSourceToDetector = 1800; ds.DistanceSourceToPatient = 1636; ds.KVP = 120; ds.Exposure = 2; ds.ExposureTime = 10
    ds.WindowCenter = 4095 - 1200; ds.WindowWidth = 2600; ds.BurnedInAnnotation = "NO"; ds.PresentationLUTShape = "INVERSE"
    ds.PixelData = stored.tobytes()
    ds.save_as(path, enforce_file_format=True)
    return {"thorax": thorax, "heart": heart}


def make_nm(path: Path):
    """Whole-body bone-scan phantom, 2 frames (anterior/posterior), Tc-99m MDP, counts."""
    rows, cols, spacing = 1024, 256, 2.26
    body = _ellipse(rows, cols, rows / 2, cols / 2, rows * 0.47, cols * 0.33)
    spine = np.zeros((rows, cols), bool); spine[int(rows * 0.12):int(rows * 0.55), cols // 2 - 6: cols // 2 + 6] = True
    hot = _ellipse(rows, cols, rows * 0.62, cols * 0.42, 9, 9)          # a focal "lesion" in the pelvis region
    lam = np.where(body, 4.0, 0.2); lam[spine] = 18.0; lam[hot] = 60.0
    rng = np.random.default_rng(1)
    ant = rng.poisson(lam).astype(np.uint16)
    post = rng.poisson(lam[:, ::-1] * 0.9).astype(np.uint16)             # posterior is mirrored
    arr = np.stack([ant, post])
    ds = _base("NM", "1.2.840.10008.5.1.4.1.1.20", rows, cols)
    ds.ImageType = ["ORIGINAL", "PRIMARY", "WHOLE BODY", "EMISSION"]; ds.BodyPartExamined = "WHOLEBODY"
    ds.PhotometricInterpretation = "MONOCHROME2"; ds.BitsAllocated = 16; ds.BitsStored = 16; ds.HighBit = 15
    ds.NumberOfFrames = 2; ds.FrameIncrementPointer = (0x0054, 0x0020); ds.DetectorVector = [1, 2]; ds.NumberOfDetectors = 2
    ds.EnergyWindowVector = [1, 1]; ds.NumberOfEnergyWindows = 1
    ds.PixelSpacing = [spacing, spacing]; ds.Units = "CNTS"; ds.CountsAccumulated = int(arr.sum())
    ds.ActualFrameDuration = 900000; ds.AcquisitionTerminationCondition = "TIME"; ds.CorrectedImage = ["UNIF", "DECY"]
    ds.WholeBodyTechnique = "1PS"; ds.ScanLength = int(round(rows * spacing)); ds.ScanVelocity = 12.0
    ds.AcquisitionTime = "113000"
    ew = Dataset(); ew.EnergyWindowName = "Tc-99m photopeak"
    r = Dataset(); r.EnergyWindowLowerLimit = 126.0; r.EnergyWindowUpperLimit = 154.0; ew.EnergyWindowRangeSequence = Sequence([r])
    ds.EnergyWindowInformationSequence = Sequence([ew])
    rp = Dataset(); rp.Radiopharmaceutical = "Tc-99m MDP"; rp.RadionuclideTotalDose = 740.0; rp.RadiopharmaceuticalStartTime = "083000"; rp.RadiopharmaceuticalRoute = "IV"
    rc = Dataset(); rc.CodeValue = "C-163A8"; rc.CodingSchemeDesignator = "SRT"; rc.CodeMeaning = "Technetium Tc-99m"; rp.RadionuclideCodeSequence = Sequence([rc])
    ds.RadiopharmaceuticalInformationSequence = Sequence([rp])
    dets = []
    for i, (meaning, po) in enumerate([("Anterior", ["L", "F"]), ("Posterior", ["R", "F"])]):
        d = Dataset(); d.CollimatorType = "PARA"; d.CollimatorGridName = "LEHR"; d.ZoomFactor = [1.0, 1.0]
        v = Dataset(); v.CodeValue = "255549009" if i == 0 else "255551008"; v.CodingSchemeDesignator = "SCT"; v.CodeMeaning = meaning
        d.ViewCodeSequence = Sequence([v]); d.PatientOrientation = po; dets.append(d)
    ds.DetectorInformationSequence = Sequence(dets)
    ds.PixelData = arr.tobytes()
    ds.save_as(path, enforce_file_format=True)
    return {"hot": hot, "body": body}


def main():
    SAMPLES.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    # 1. DX phantom + measurements
    dxp = SAMPLES / "synthetic_dx_chest.dcm"; masks = make_dx(dxp)
    pkg = convert(dxp, OUT / "synthetic-dx-chest", synthetic=True, title="Synthetic chest radiograph phantom, PA (MONOCHROME1 source)")
    m = json.loads((pkg / "oip.json").read_text())
    ctr = cardiothoracic_ratio(masks["heart"], masks["thorax"]); ctr.update({"validation_status": "phantom_validated", "tool_version": "0.1.0", "confidence": 0.99, "inputs": ["derived/masks/heart.png", "derived/masks/thorax.png"]})
    hw = width_mm(masks["heart"], m); tw = width_mm(masks["thorax"], m)
    meas = [ctr,
            {"id": "heart_width", "name": "Transverse cardiac diameter", "value": round(hw["value"], 2), "unit": "mm", "method": "max horizontal width of heart mask × column spacing", "tool": "oip-measure", "tool_version": "0.1.0", "assertion_level": "computed", "confidence": hw["confidence"], "validation_status": "phantom_validated", "inputs": ["derived/masks/heart.png"]},
            {"id": "thorax_width", "name": "Internal thoracic width", "value": round(tw["value"], 2), "unit": "mm", "method": "max horizontal width of thorax mask × column spacing", "tool": "oip-measure", "tool_version": "0.1.0", "assertion_level": "computed", "confidence": tw["confidence"], "validation_status": "phantom_validated", "inputs": ["derived/masks/thorax.png"]}]
    from PIL import Image
    (pkg / "derived/masks").mkdir(exist_ok=True)
    for k in ("heart", "thorax"):
        Image.fromarray((masks[k] * 255).astype(np.uint8)).save(pkg / f"derived/masks/{k}.png")
    from oip.measure import mask_extent
    regions = [{"id": "heart", "label": "heart (phantom ellipse)", "mask": "derived/masks/heart.png", "bbox_px": mask_extent(masks["heart"])["bbox_px"], "mark": "1", "assertion_level": "computed", "tool": "phantom-generator", "confidence": 1.0},
               {"id": "thorax", "label": "thorax (phantom ellipse)", "mask": "derived/masks/thorax.png", "bbox_px": mask_extent(masks["thorax"])["bbox_px"], "mark": "2", "assertion_level": "computed", "tool": "phantom-generator", "confidence": 1.0}]
    add_measurements(pkg, meas, regions)
    print("DX:", pkg, "CTR", ctr["value"], "heart mm", meas[1]["value"], "thorax mm", meas[2]["value"])
    # 2. NM phantom
    nmp = SAMPLES / "synthetic_nm_wholebody.dcm"; make_nm(nmp)
    pkg = convert(nmp, OUT / "synthetic-nm-bone-scan", synthetic=True, title="Synthetic whole-body bone scintigraphy phantom (anterior + posterior)")
    print("NM:", pkg)
    # 3. pydicom samples (CT, MR) exercise the generic path
    from pydicom.data import get_testdata_file
    for name, out in [("CT_small.dcm", "pydicom-ct-small"), ("MR_small.dcm", "pydicom-mr-small")]:
        pkg = convert(get_testdata_file(name), OUT / out)
        print("sample:", pkg)


if __name__ == "__main__":
    main()
