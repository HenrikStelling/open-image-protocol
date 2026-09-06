"""Build OIP-Bench tasks from converted packages. Each task: {id, pkg, type, question, answer, gating, tolerance}."""
from __future__ import annotations
import json, random
from pathlib import Path

UNDERSTANDING = ("modality", "view", "left_edge", "scale_available", "ctr", "heart_mm")
FINDING_LABELS = ["Aortic enlargement", "Atelectasis", "Calcification", "Cardiomegaly", "Consolidation", "ILD", "Infiltration", "Lung Opacity", "Nodule/Mass", "Other lesion", "Pleural effusion", "Pleural thickening", "Pneumothorax", "Pulmonary fibrosis"]


def tasks_for_package(pkg: Path, labels: list[str] | None = None) -> list[dict]:
    m = json.loads((pkg / "oip.json").read_text()); g, a = m["geometry"], m["acquisition"]; meas = {x["id"]: x for x in m["derived"]["measurements"]}
    T = []
    T.append(dict(type="modality", question="What imaging modality produced this image? Answer with one of: radiograph, CT, MRI, scintigraphy, ultrasound.", answer={"DX": "radiograph", "CR": "radiograph", "NM": "scintigraphy", "CT": "CT", "MR": "MRI", "US": "ultrasound"}.get(a["modality"]["value"], "other")))
    if a["view"]["value"]:
        T.append(dict(type="view", question="Is this a frontal or a lateral projection? Answer 'frontal' or 'lateral'.", answer="lateral" if "LAT" in str(a["view"]["value"]).upper() or a["view"]["value"] in ("LL", "RL") else "frontal"))
    el = g["orientation"]["edge_labels"]
    if el.get("left") in ("L", "R"):
        T.append(dict(type="left_edge", question="Which side of the patient is at the LEFT edge of the image? Answer 'patient right' or 'patient left'.", answer="patient right" if el["left"] == "R" else "patient left"))
    T.append(dict(type="scale_available", question="Can distances in this image be stated in millimetres with a known calibration? Answer 'yes' or 'no'.", answer="yes" if g["pixel_spacing_mm"] and g["calibration"]["confidence"] in ("high", "medium") else "no"))
    if "ctr" in meas and meas["ctr"]["value"]:
        T.append(dict(type="ctr", question="Estimate the cardiothoracic ratio (maximum horizontal cardiac width divided by maximum internal thoracic width). Answer with a number between 0 and 1.", answer=meas["ctr"]["value"], tolerance=0.05))
    if "heart_width" in meas and meas["heart_width"]["value"]:
        T.append(dict(type="heart_mm", question="Estimate the transverse cardiac diameter in millimetres. Answer with a number.", answer=meas["heart_width"]["value"], tolerance=0.10))
    if labels is not None:
        T.append(dict(type="findings", question="List every abnormality present from this list (comma separated), or 'No finding': " + ", ".join(FINDING_LABELS) + ".", answer=sorted(set(labels)) or ["No finding"], gating=False))
    for t in T:
        t.setdefault("gating", t["type"] in UNDERSTANDING); t["pkg"] = str(pkg); t["id"] = f"{pkg.name}:{t['type']}"
    return T


def build(pkg_dir: Path, n: int = 100, seed: int = 0, labels_by_id: dict | None = None) -> list[dict]:
    pkgs = sorted(pkg_dir.glob("*.oip")); random.Random(seed).shuffle(pkgs); out = []
    for p in pkgs[:n]:
        m = json.loads((p / "oip.json").read_text()); iid = m["provenance"]["source_filename"].split(".")[0]
        out += tasks_for_package(p, (labels_by_id or {}).get(iid))
    return out


def vindr_labels() -> dict:
    import csv, collections
    d = collections.defaultdict(set)
    for r in csv.DictReader(open(Path.home() / ".cache/kagglehub/competitions/vinbigdata-chest-xray-abnormalities-detection/train.csv")):
        if r["class_name"] != "No finding": d[r["image_id"]].add(r["class_name"])
        else: d.setdefault(r["image_id"], set())
    return {k: sorted(v) for k, v in d.items()}
