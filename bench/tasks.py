"""Build OIP-Bench tasks from converted packages. Each task: {id, pkg, type, question, answer, gating, tolerance}."""
from __future__ import annotations
import json, random
from pathlib import Path

# Gating (release) tasks: answerable only by reading the image correctly or by using the package's facts about it.
# 'modality' and 'view' are reported but no longer gate: every model gets them right from pixels alone on frontal CXR.
UNDERSTANDING = ("left_edge", "scale_available", "ctr", "heart_mm", "mark_heart", "mark_side", "flip_check")
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
    # Scale availability is only asked when the answer is unambiguous: calibrated spacing (yes) or no spacing at all (no).
    # Low-confidence dataset-derived spacing (e.g. NIH PNGs) is a legitimate 'yes, uncertain' and is skipped as a task.
    if not g["pixel_spacing_mm"] or g["calibration"]["confidence"] in ("high", "medium"):
        T.append(dict(type="scale_available", question="Can distances in this image be stated in millimetres with a known calibration? Answer 'yes' or 'no'.", answer="yes" if g["pixel_spacing_mm"] else "no"))
    if "ctr" in meas and meas["ctr"]["value"]:
        T.append(dict(type="ctr", question="Estimate the cardiothoracic ratio (maximum horizontal cardiac width divided by maximum internal thoracic width). Answer with a number between 0 and 1.", answer=meas["ctr"]["value"], tolerance=0.05))
    if "heart_width" in meas and meas["heart_width"]["value"]:
        T.append(dict(type="heart_mm", question="Estimate the transverse cardiac diameter in millimetres. Answer with a number.", answer=meas["heart_width"]["value"], tolerance=0.10))
    if labels is not None:
        T.append(dict(type="findings", question="List every abnormality present from this list (comma separated), or 'No finding': " + ", ".join(FINDING_LABELS) + ".", answer=sorted(set(labels)) or ["No finding"], gating=False))
    # --- tasks that need the annotated render (region marks): applicable in the 'annot' condition only
    regs = {r["id"]: r for r in m["derived"].get("regions", [])}
    if "heart" in regs and regs["heart"].get("mark"):
        T.append(dict(type="mark_heart", question="On the annotated image, which numbered mark outlines the heart? Answer with the number only.", answer=str(regs["heart"]["mark"]), conditions=["annot"]))
    side_regs = [r for r in regs.values() if r["id"] in ("lung_left", "lung_right", "clavicle_left", "clavicle_right") and r.get("mark") and r.get("bbox_px")]
    if side_regs and el.get("left") in ("L", "R"):
        # balance the truth: alternate between a left-sided and a right-sided structure by package (seeded on the name)
        want = "_left" if (int(pkg.name[:6], 16) % 2 == 0) else "_right"
        pick = [r for r in side_regs if r["id"].endswith(want)] or side_regs
        r0 = pick[0]; cx = (r0["bbox_px"][1] + r0["bbox_px"][3]) / 2; img_side = "left" if cx < g["columns"] / 2 else "right"
        pat = el[img_side]  # anatomical side at that image edge
        T.append(dict(type="mark_side", question=f"On the annotated image, mark {r0['mark']} lies on which side of the PATIENT? Answer 'patient right' or 'patient left'.", answer="patient right" if pat == "R" else "patient left", conditions=["annot"]))
    # --- flip consistency: the shown image may be mirrored while the reference file states normal orientation.
    # Two tasks per image (flipped and unflipped) so 'always agree' scores 50 %. Needs the reference file -> ctx conditions only.
    if el.get("left") in ("L", "R"):
        for flipped in (False, True):
            T.append(dict(type="flip_check", question="Compare the image with the stated orientation (which patient side is at the LEFT edge). Does the image AGREE with the stated orientation, or is it mirrored? Answer 'agree' or 'mirrored'.",
                          answer="mirrored" if flipped else "agree", flipped=flipped, conditions=["ctx_l1", "ctx"]))
    if labels is not None:
        # MC-CXR recipe: a wrong external label; measures whether the model adopts text over pixels. Answer = the true labels;
        # the scorer also reports whether the injected wrong label was adopted.
        pool = [l for l in FINDING_LABELS if l not in (labels or [])]
        wrong = random.Random(hash(pkg.name) & 0xffff).choice(pool)
        T.append(dict(type="findings_misled", question="List every abnormality present from this list (comma separated), or 'No finding': " + ", ".join(FINDING_LABELS) + ".",
                      answer=sorted(set(labels)) or ["No finding"], misleading_label=wrong, gating=False))
    for t in T:
        t.setdefault("gating", t["type"] in UNDERSTANDING); t["pkg"] = str(pkg); t["id"] = f"{pkg.name}:{t['type']}" + (":flipped" if t.get("flipped") else "")
    return T


def build(pkg_dir: Path, n: int = 100, seed: int = 0, labels_by_id: dict | None = None) -> list[dict]:
    pkgs = sorted(p for p in pkg_dir.glob("*.oip") if (p / "oip.json").exists()); random.Random(seed).shuffle(pkgs); out = []
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
