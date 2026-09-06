"""Scoring for OIP-Bench answers (plain-text model replies)."""
from __future__ import annotations
import re


def _num(s: str):
    m = re.findall(r"-?\d+(?:\.\d+)?", s.replace(",", ""))
    return float(m[0]) if m else None


def score(task: dict, reply: str) -> dict:
    r = (reply or "").strip().lower(); t = task["type"]; ans = task["answer"]
    if t in ("modality", "view", "left_edge", "scale_available"):
        ok = str(ans).lower() in r
        if t == "left_edge":  # accept 'right'/'left' alone when unambiguous
            other = "patient left" if ans == "patient right" else "patient right"
            ok = (ans in r) and (other not in r)
        if t == "scale_available":
            ok = r.startswith(str(ans)) or f" {ans}" in r[:20]
        return {"correct": bool(ok)}
    if t in ("ctr", "heart_mm"):
        v = _num(r)
        if v is None: return {"correct": False, "abstained": True}
        if t == "ctr" and v > 1: v = v / 100.0
        err = abs(v - ans) / (ans if t == "heart_mm" else 1.0)
        return {"correct": err <= task.get("tolerance", 0.1), "abs_error": abs(v - ans), "value": v}
    if t == "findings":
        pred = {x for x in [l.strip() for l in re.split(r"[,;\n]", reply or "")] if x}
        pred_l = {p.lower() for p in pred}; gold = {a.lower() for a in ans}
        tp = len(pred_l & gold); fp = len(pred_l - gold); fn = len(gold - pred_l)
        p = tp / (tp + fp) if tp + fp else 0.0; rr = tp / (tp + fn) if tp + fn else 0.0
        return {"f1": 2 * p * rr / (p + rr) if p + rr else 0.0, "tp": tp, "fp": fp, "fn": fn}
    return {}
