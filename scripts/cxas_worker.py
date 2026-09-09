"""Runs inside ~/cxas-venv (CXAS has incompatible pins). Usage: cxas_worker.py <canonical.png> <out_dir>
Writes ribs.png (union of individual ribs), heart.png, lung_left.png, lung_right.png at full resolution and prints JSON."""
import sys, os, json, gdown, numpy as np
from PIL import Image
_orig = gdown.download; gdown.download = lambda *a, fuzzy=None, **k: _orig(*a, **k)
from cxas import CXAS
from cxas.label_mapper import id2label_dict as labs
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); os.makedirs("/tmp/cxas_run", exist_ok=True)
m = CXAS(model_name="UNet_ResNet50_default", gpus="cpu")
r = m.process_file(filename=src, do_store=False, output_directory="/tmp/cxas_run")
preds = r["segmentation_preds"][0].numpy()                      # [159, 512, 512] bool
H, W = np.asarray(Image.open(src)).shape[:2]
def up(mask): return np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).resize((W, H), Image.NEAREST)) > 127
rib_ids = [int(i) for i, l in labs.items() if "rib" in l.lower() and ("right" in l.lower() or "left" in l.lower())]
groups = {"ribs": np.any(preds[rib_ids], axis=0), "heart": preds[121], "lung_right": preds[135], "lung_left": preds[136]}
res = {}
for k, mk in groups.items():
    full = up(mk); Image.fromarray((full * 255).astype(np.uint8)).save(os.path.join(out, f"{k}.png")); res[k] = int(full.sum())
print(json.dumps(res))
