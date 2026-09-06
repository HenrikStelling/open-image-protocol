"""Convert the Zenodo IICS-UNA Paraguay bone scans (16-bit PNG, ant/post) to OIP packages. Usage: python scripts/bonescan_to_oip.py [limit] [out]"""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from oip.convert_image import convert_image
SRC = ROOT / "data/bone-scans-paraguay/images"
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 4; out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "data/oip/bonescan"
files = sorted(SRC.glob("*/*/*.png"))[:limit]
for f in files:
    cls, view = f.parts[-3], f.parts[-2]
    meta = dict(modality="NM", body_part="WHOLEBODY", view=view.upper(), original_spacing_mm=[2.3, 2.3], original_size=[256, 1024],
                dataset="Bone scan images, IICS-UNA Paraguay (Zenodo 10.5281/zenodo.13900966, CC-BY-4.0)",
                labels=[cls], notes=["Label is the patient-level final diagnosis by a nuclear physician (bone metastases vs none), not a per-lesion annotation.",
                                     "Pixel size is NOT in the data; 2.3 mm/px is the typical whole-body planar pixel size for a 256x1024 matrix (paper reports ~20 mCi Tc-99m MDP, planar whole-body).",
                                     "Whole-body scans: the anterior and posterior views of the same patient share the file number (A<n>/P<n>)."],
                nm=dict(image_type="WHOLE BODY", radiopharmaceutical="Tc-99m MDP", radionuclide="Technetium Tc-99m", administered_activity_MBq=740.0, route="IV"))
    pkg = convert_image(f, out / f"{cls.replace(' ', '_').lower()}-{f.stem}", meta, title=f"Whole-body bone scintigraphy, {view.lower()} view (from PNG)")
    m = json.loads((pkg / "oip.json").read_text())
    print(pkg.name, m["intensity"]["units"], m["geometry"]["orientation"]["edge_labels"], m["quality"]["flags"], (m.get("extensions") or {}).get("org.openimageprotocol.counts_recovery"))
