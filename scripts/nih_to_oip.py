"""Convert N images of the NIH ChestX-ray14 Kaggle sample to OIP packages (non-DICOM path)."""
import csv, os, sys, glob, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from oip.convert_image import convert_image, nih_meta
C = Path(os.environ.get("OIP_KAGGLE_CACHE", Path.home() / ".cache/kagglehub"))
base = sorted(glob.glob(str(C / "datasets/nih-chest-xrays/sample/versions/*")))[-1]
n = int(sys.argv[1]) if len(sys.argv) > 1 else 5; out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/oip/nih")
rows = list(csv.DictReader(open(Path(base) / "sample_labels.csv")))[:n]
for r in rows:
    pkg = convert_image(Path(base) / "sample/images" / r["Image Index"], out / r["Image Index"].replace(".png", ""), nih_meta(r))
    m = json.loads((pkg / "oip.json").read_text()); print(pkg.name, m["geometry"]["pixel_spacing_mm"], m["quality"]["flags"])
