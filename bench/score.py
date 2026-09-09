"""Scoring for OIP-Bench answers (plain-text model replies)."""
from __future__ import annotations
import re
FINDING_LABELS = ["Aortic enlargement", "Atelectasis", "Calcification", "Cardiomegaly", "Consolidation", "ILD", "Infiltration", "Lung Opacity", "Nodule/Mass", "Other lesion", "Pleural effusion", "Pleural thickening", "Pneumothorax", "Pulmonary fibrosis"]


NUM = r"-?\d+(?:\.\d+)?"


def _num(s: str):
    """Answer extraction for free-text replies, in order of reliability: a number after an explicit answer marker
    ('Answer:', '**≈116 mm**'), then the first number on the final non-empty line, then the last number anywhere."""
    s = (s or "").replace(",", "")
    tail = s.split("</think>")[-1]                      # visible reasoning models close their thinking with this tag
    m = re.search(r"(?:answer|estimate|ctr|ratio|diameter)\s*(?:is|:|=|≈|~)?\s*\**\s*[~≈]?\s*(" + NUM + ")", tail, re.I)
    if m: return float(m.group(1))
    m = re.search(r"\*\*\s*[~≈]?\s*(" + NUM + ")", tail)
    if m: return float(m.group(1))
    lines = [l for l in tail.splitlines() if l.strip()]
    if lines:
        m = re.search(NUM, lines[-1])
        if m: return float(m.group(0))
    m = re.findall(NUM, tail)
    return float(m[-1]) if m else None


def score(task: dict, reply: str) -> dict:
    r = (reply or "").strip().lower(); t = task["type"]; ans = task["answer"]
    ABSTAIN = re.compile(r"\b(cannot|can't|unable|not possible|insufficient|no way to|impossible to|not determin|indetermin|unknown from the image)\b")
    if t in ("modality", "view", "left_edge", "scale_available"):
        ok = str(ans).lower() in r
        if ABSTAIN.search(r) and not ok:
            return {"correct": False, "abstained": True}
        if t == "modality" and ans == "radiograph": ok = ok or "x-ray" in r or "xray" in r or "radiography" in r
        if t == "view":
            frontal = bool(re.search(r"\b(frontal|pa|ap|posteroanterior|anteroposterior|postero-anterior|antero-posterior)\b", r))
            lateral = bool(re.search(r"\b(lateral|ll|rl)\b", r))
            ok = (ans == "frontal" and frontal and not lateral) or (ans == "lateral" and lateral and not frontal)
        if t == "left_edge":  # accept 'right'/'left' alone when unambiguous
            other = "patient left" if ans == "patient right" else "patient right"
            ok = (ans in r) and (other not in r)
        if t == "scale_available":
            # first standalone yes/no token in the reply decides ('no,' 'yes.' etc.)
            m = re.search(r"\b(yes|no)\b", r)
            ok = bool(m) and m.group(1) == str(ans)
        return {"correct": bool(ok)}
    if t == "mark_heart":
        m = re.search(r"\b(\d{1,2})\b", r); return {"correct": bool(m) and m.group(1) == str(ans), "value": m.group(1) if m else None}
    if t == "mark_side":
        other = "patient left" if ans == "patient right" else "patient right"
        return {"correct": (ans in r) and (other not in r)}
    if t == "flip_check":
        mir = bool(re.search(r"\b(mirror|mirrored|flipped|disagree|does not agree|reversed)\b", r)); agr = bool(re.search(r"\bagree", r)) and not mir
        return {"correct": (ans == "mirrored" and mir) or (ans == "agree" and agr)}
    if t in ("ctr", "heart_mm"):
        v = _num(r)
        if v is None: return {"correct": False, "abstained": True}
        if t == "ctr" and v > 1: v = v / 100.0
        err = abs(v - ans) / (ans if t == "heart_mm" else 1.0)
        return {"correct": err <= task.get("tolerance", 0.1), "abs_error": abs(v - ans), "value": v}
    if t in ("findings", "findings_misled"):
        # chain-of-thought replies: the label list is the last non-empty line; match only known labels (no free-text tokens)
        lines = [l.strip() for l in (reply or "").splitlines() if l.strip()]
        tail = lines[-1] if lines else ""
        known = [l.lower() for l in FINDING_LABELS] + ["no finding"]
        pred_l = {k for k in known if k in tail.lower()}
        if not pred_l and len(lines) > 1: pred_l = {k for k in known if k in (reply or "").lower()}   # fallback: anywhere
        gold = {a.lower() for a in ans}
        tp = len(pred_l & gold); fp = len(pred_l - gold); fn = len(gold - pred_l)
        p = tp / (tp + fp) if tp + fp else 0.0; rr = tp / (tp + fn) if tp + fn else 0.0
        out = {"f1": 2 * p * rr / (p + rr) if p + rr else 0.0, "tp": tp, "fp": fp, "fn": fn}
        if t == "findings_misled": out["adopted_misleading"] = task["misleading_label"].lower() in pred_l
        return out
    return {}
