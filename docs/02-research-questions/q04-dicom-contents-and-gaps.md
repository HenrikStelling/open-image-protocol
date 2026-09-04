# Q4 — What DICOM contains (for X-ray and scintigraphy) and what is missing

## 4.1 Projection radiography: CR / DX Image IODs

Tags that OIP must read (tag, keyword, meaning, OIP field):

| Tag | Keyword | Meaning | OIP |
|---|---|---|---|
| (0008,0060) | Modality | CR, DX (also RG legacy) | `acquisition.modality` |
| (0008,0008) | ImageType | ORIGINAL/DERIVED, PRIMARY/SECONDARY | `provenance.image_type` |
| (0018,0015) | BodyPartExamined | CHEST, HAND… | `acquisition.body_part` |
| (0018,5101) | ViewPosition | PA, AP, LL, RL, LATERAL… | `acquisition.view` |
| (0020,0020) | PatientOrientation | e.g. `L\F` (row→left, column→foot) | `geometry.orientation` |
| (0020,0062) | ImageLaterality | L / R / B / U | `acquisition.laterality` |
| (0018,5100) | PatientPosition | e.g. standing not encoded; mostly for CT | `acquisition.patient_position` |
| (0028,0030) | PixelSpacing | mm between pixel centres **in the patient** (only if calibrated) | `geometry.pixel_spacing_mm` (spacing_source=`PixelSpacing`) |
| (0018,1164) | ImagerPixelSpacing | mm at the **detector** plane | `geometry.pixel_spacing_mm` (spacing_source=`ImagerPixelSpacing`) |
| (0028,0A02)/(0028,0A04) | PixelSpacingCalibrationType/Description | GEOMETRY or FIDUCIAL calibration | `geometry.calibration` |
| (0018,1114) | EstimatedRadiographicMagnificationFactor | SID/SOD ratio | `geometry.calibration.magnification_factor` |
| (0018,1110)/(0018,1111) | DistanceSourceToDetector / ToPatient | mm | `acquisition.technique` |
| (0018,0060) | KVP | tube voltage | `acquisition.technique.kvp` |
| (0018,1152)/(0018,1153)/(0018,1150) | Exposure (mAs) / ExposureInuAs / ExposureTime | dose-related | `acquisition.technique` |
| (0018,1411) | ExposureIndex | detector exposure index | `acquisition.technique` |
| (0028,0004) | PhotometricInterpretation | MONOCHROME1 (0 = white!) or MONOCHROME2 | `intensity.photometric` |
| (0028,0100)/(0028,0101)/(0028,0103) | BitsAllocated / BitsStored / PixelRepresentation | 12–16-bit | `intensity.bits_stored` |
| (0028,1052)/(0028,1053) | RescaleIntercept / Slope | linear map to units | `intensity.rescale` |
| (0028,1050)/(0028,1051)/(0028,1056) | WindowCenter / Width / VOILUTFunction | display window | `intensity.voi` |
| (0028,3010) | VOILUTSequence | explicit LUT | `intensity.voi.lut = true` |
| (2050,0020) | PresentationLUTShape | IDENTITY / INVERSE | `intensity.presentation_lut` |
| (0028,0301) | BurnedInAnnotation | YES → PHI risk | `quality.flags` |
| (0028,2110)/(0028,2112) | LossyImageCompression / Ratio | | `quality.flags` |
| (0008,0070)/(0008,1090) | Manufacturer / ModelName | | `acquisition.device` |
| (0010,1010)/(0010,0040) | PatientAge / PatientSex | keep as age band + sex only | `subject` |
| (0020,000D)/(0020,000E)/(0008,0018) | Study/Series/SOP Instance UID | hashed | `identity` |

## 4.2 Planar scintigraphy: NM Image IOD (multi-frame)

| Tag | Keyword | Meaning | OIP |
|---|---|---|---|
| (0008,0008) value 3 | ImageType | STATIC / DYNAMIC / GATED / WHOLE BODY / TOMO / RECON TOMO | `acquisition.nm.image_type` |
| (0028,0008) | NumberOfFrames | frames (e.g. anterior + posterior) | `frames[]` |
| (0054,0020)/(0054,0021) | DetectorVector / NumberOfDetectors | which detector produced each frame | `frames[].detector` |
| (0054,0022) | DetectorInformationSequence → CollimatorType (0018,1181), CollimatorGridName, ImageOrientationPatient, ViewCodeSequence, ZoomFactor, FieldOfViewShape/Dimensions | per-detector geometry and view (anterior/posterior) | `frames[].view`, `geometry` |
| (0054,0012) | EnergyWindowInformationSequence → EnergyWindowRangeSequence lower/upper limit (0054,0014/0015) keV | which photopeak was counted (e.g. 126–154 keV for Tc-99m) | `acquisition.nm.energy_windows[]` |
| (0054,0016) | RadiopharmaceuticalInformationSequence → Radiopharmaceutical (0018,0031), RadionuclideCodeSequence, RadionuclideTotalDose (0018,1074) MBq, RadiopharmaceuticalStartTime (0018,1072), RouteOfAdministration | tracer, dose, injection time (→ uptake time) | `acquisition.nm.radiopharmaceutical` |
| (0018,1242) | ActualFrameDuration | ms | `frames[].duration_ms` |
| (0018,0070) | CountsAccumulated | total counts | `frames[].counts` |
| (0018,0071) | AcquisitionTerminationCondition | TIME / CNTS | |
| (0018,1301)/(0018,1302)/(0018,1300) | WholeBodyTechnique / ScanLength / ScanVelocity | whole-body sweep parameters | `acquisition.nm` |
| (0054,1001) | Units | CNTS, CPS, BQML… | `intensity.units` |
| (0028,0051) | CorrectedImage | UNIF, DECY, ATTN, SCAT… corrections applied | `intensity.corrections` |
| (0028,0030) | PixelSpacing | mm at detector plane (zoom-dependent) | `geometry` (spacing_source=`PixelSpacing`, calibration=`detector`) |
| (0028,0009) | FrameIncrementPointer | how frames are indexed | internal |
| (0018,1020) / (0008,0070) | SoftwareVersions / Manufacturer | | `acquisition.device` |

## 4.3 What DICOM does **not** give us (gaps OIP must fill)

| Gap | Why it matters | OIP fill |
|---|---|---|
| Natural-language description of what the image is and how to read it | Models read prose; DICOM has none | `context.md` (auto-generated + optional human notes) |
| Explicit statement of *which* spacing applies and its trust level | Three spacing concepts, frequently absent (Kaggle PNG datasets) | `geometry.spacing_source`, `geometry.calibration.confidence` |
| Canonical model-ready render + record of the transform | Conversion is silent today | `renders[]` with `transform` description |
| Anatomy / regions / landmarks | Not in image IODs (only in SEG/SR objects) | `derived/masks`, `derived/landmarks` with assertion level |
| Measurements with method and validation status | SR TID 1500 exists but is rarely produced | `derived/measurements.json` |
| Assertion levels / provenance per statement | MC-CXR shows text without provenance misleads | `assertion_level` everywhere |
| Quality diagnostics | Nothing tells a model "spacing missing" or "burned-in text" | `quality.flags[]` |
| Semantics of NM counts for reasoning (counts are relative; comparisons need same window, duration, dose, decay) | Models treat greyscale as intensity | `intensity.units = counts` + `context.md` cautions + tool guardrails |
| De-identification status | | `deid` |
| Cross-modality neutral core | DICOM IODs differ per modality | Layer L1 identical for all modalities |

## What OIP does about it
The manifest schema (`spec/schemas/oip-manifest.schema.json`) has fields for
every row above; the converter (`src/oip/convert.py`) maps the tags; unmapped
tags remain available in `source/dicom-headers.json` (DICOM JSON model, PHI removed).
