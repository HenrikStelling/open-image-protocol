"""Scoring for OIP-Bench answers (plain-text model replies).

Scorer 0.3 (2026-09-23), after the RA eval audit of the paper run (scorer 0.2 = harness commit 050769a):
  1. The abstention flag is computed independently of correctness. 0.2 tested `answer in reply` before the abstention
     regex, so a decisive wrong "no" on a "yes" item was flagged as an abstention (glm-5.3-flash, 63 VinDr raw rows) and
     "cannot determine" on a "no" item was never flagged ("no" is a substring of "cannot"). Now: abstained = the reply
     matches the abstention pattern AND contains no decisive answer token for the task.
  2. Units are normalised for cardiac width: a value given in centimetres (unit word next to the number, or a value
     <= 25 in a reply that mentions cm) is converted to millimetres. 0.2 scored such answers wrong; they occurred almost
     only in the image-only and L0-L2 arms.
  3. The flip check reads the final answer line first and recognises more negation forms ("do not agree", "doesn't
     agree", "not consistent", "does not match", "reversed"); 0.2 matched "does not agree" only and read the whole reply.
  4. Text before a closing </think> tag is not scored for any task (0.2 stripped it only for numeric extraction), so a
     visible-reasoning model is no longer scored on both sides it weighed before answering. Only glm-5.3-flash emits
     the tag; its categorical cells change.
  5. The abstention pattern is narrowed to statements about determinability ("cannot determine", "unable to tell",
     "insufficient information"), and on yes/no tasks the phrases "cannot be stated / compared / measured / given" count as
     a decisive "no", which is what they answer. 0.2 treated every "cannot" as an abstention.
Correctness rules for every other task are unchanged from 0.2.
"""
from __future__ import annotations
import re

SCORER_VERSION = "0.3"
FINDING_LABELS = ["Aortic enlargement", "Atelectasis", "Calcification", "Cardiomegaly", "Consolidation", "ILD", "Infiltration", "Lung Opacity", "Nodule/Mass", "Other lesion", "Pleural effusion", "Pleural thickening", "Pneumothorax", "Pulmonary fibrosis"]

NUM = r"-?\d+(?:\.\d+)?"
ABSTAIN = re.compile(r"\b(?:(?:cannot|can't|unable to|not possible to|impossible to|no way to|hard to|difficult to)\s+(?:reliably\s+|definitively\s+|confidently\s+)?(?:determine|tell|say|know|assess|establish|ascertain|judge|be (?:determined|certain|sure))|insufficient (?:information|data|detail)|indetermin\w*|not determinable|cannot be determined|can't be determined|unknown from the image)\b")
NO_PHRASE = re.compile(r"\b(?:cannot|can't|can not|not possible to|impossible to|unable to)\s+(?:be\s+)?(?:reliably\s+|directly\s+|accurately\s+|meaningfully\s+)?(?:stated|state|compared|compare|measured|measure|given|give|expressed|express|quantified|quantify|calibrated|converted|convert)\b")
MIRROR = re.compile(r"\b(mirror|mirrored|flipped|disagree|disagrees|disagreed|do(?:es)? not agree|doesn't agree|don't agree|not consistent|inconsistent|do(?:es)? not match|doesn't match|reversed)\b")
AGREE = re.compile(r"\b(agree|agrees|agreed|agreement|consistent|matches)\b")


def _tail(s: str) -> str:
    """Visible reasoning models close their thinking with </think>; score what follows."""
    return (s or "").split("</think>")[-1]


def _last_line(s: str) -> str:
    lines = [l for l in s.splitlines() if l.strip()]
    return lines[-1] if lines else ""


def _num(s: str):
    """Answer extraction for free-text replies, in order of reliability: a number after an explicit answer marker
    ('Answer:', '**≈116 mm**'), then the first number on the final non-empty line, then the last number anywhere."""
    s = (s or "").replace(",", "")
    tail = _tail(s)
    m = re.search(r"(?:answer|estimate|ctr|ratio|diameter)\s*(?:is|:|=|≈|~)?\s*\**\s*[~≈]?\s*(" + NUM + ")", tail, re.I)
    if m: return float(m.group(1))
    m = re.search(r"\*\*\s*[~≈]?\s*(" + NUM + ")", tail)
    if m: return float(m.group(1))
    last = _last_line(tail)
    if last:
        m = re.search(NUM, last)
        if m: return float(m.group(0))
    m = re.findall(NUM, tail)
    return float(m[-1]) if m else None


def _mm(s: str, v: float | None):
    """Unit normalisation for a length: the unit word next to the extracted number decides; a value <= 25 in a reply
    that mentions centimetres is a centimetre answer. Returns the value in mm."""
    if v is None:
        return None
    tail = _tail(s or "").replace(",", "")
    vs = ("%g" % v)
    m = re.search(re.escape(vs) + r"\s*(cm|centimet\w*|mm|millimet\w*)\b", tail, re.I)
    if m:
        return v * 10 if m.group(1).lower().startswith("c") else v
    if v <= 25 and re.search(r"\b(cm|centimet\w*)\b", tail, re.I):
        return v * 10
    return v


def _decisive(t: str, r: str) -> bool:
    """Does the reply contain an answer token for this task (right or wrong)? Used for the abstention flag."""
    if t == "scale_available":
        return bool(re.search(r"\b(yes|no)\b", r)) or bool(NO_PHRASE.search(r))
    if t == "left_edge":
        return bool(re.search(r"\b(left|right)\b", r))
    if t == "modality":
        return bool(re.search(r"\b(radiograph\w*|x-?ray|xray|ct|mri|mr|scintigraph\w*|nuclear|bone scan|spect|ultrasound|sonograph\w*)\b", r))
    if t == "view":
        return bool(re.search(r"\b(frontal|lateral|pa|ap|ll|rl|posteroanterior|anteroposterior|postero-anterior|antero-posterior)\b", r))
    return True


def score(task: dict, reply: str) -> dict:
    r = _tail((reply or "")).strip().lower(); t = task["type"]; ans = task["answer"]
    # orient_conflict (round 3, 2026-09-26) is scored by the flip_check rule and badge_read (2026-09-30) by the left_edge rule; no rule
    # for an existing type changed, so the version stays 0.3
    t = {"modality_nm": "modality", "left_edge_nm": "left_edge", "scale_available_nm": "scale_available", "counts_semantics": "scale_available", "hot_side": "left_edge", "flip_check_nm": "flip_check", "orient_conflict": "flip_check", "badge_read": "left_edge"}.get(t, t)
    if t in ("modality", "view", "left_edge", "scale_available"):
        ok = str(ans).lower() in r
        if t == "modality" and ans == "radiograph": ok = ok or "x-ray" in r or "xray" in r or "radiography" in r
        if t == "modality" and ans == "scintigraphy": ok = ok or "nuclear" in r or "bone scan" in r or "spect" in r
        if t == "view":
            frontal = bool(re.search(r"\b(frontal|pa|ap|posteroanterior|anteroposterior|postero-anterior|antero-posterior)\b", r))
            lateral = bool(re.search(r"\b(lateral|ll|rl)\b", r))
            ok = (ans == "frontal" and frontal and not lateral) or (ans == "lateral" and lateral and not frontal)
        if t == "left_edge":  # accept 'right'/'left' alone when unambiguous
            other = "patient left" if ans == "patient right" else "patient right"
            ok = (ans in r) and (other not in r)
        if t == "scale_available":
            # first standalone yes/no token in the reply decides ('no,' 'yes.' etc.); a "cannot be stated/compared"
            # phrase that comes first counts as "no" (it answers the question, it does not abstain from it)
            m = re.search(r"\b(yes|no)\b", r); n = NO_PHRASE.search(r)
            tok = None
            if m and (not n or m.start() <= n.start()): tok = m.group(1)
            elif n: tok = "no"
            ok = tok == str(ans)
        out = {"correct": bool(ok)}
        if ABSTAIN.search(r) and not _decisive(t, r):
            out["abstained"] = True
        return out
    if t == "mark_heart":
        m = re.search(r"\b(\d{1,2})\b", r); return {"correct": bool(m) and m.group(1) == str(ans), "value": m.group(1) if m else None}
    if t == "mark_side":
        other = "patient left" if ans == "patient right" else "patient right"
        return {"correct": (ans in r) and (other not in r)}
    if t == "flip_check":
        last = _last_line(r)
        for seg in (last, r):          # the final answer line decides when it carries a verdict; else the whole reply
            mir = bool(MIRROR.search(seg)); agr = bool(AGREE.search(seg)) and not mir
            if mir or agr:
                return {"correct": (ans == "mirrored" and mir) or (ans == "agree" and agr)}
        return {"correct": False}
    if t in ("ctr", "heart_mm"):
        v = _num(r)
        if v is None: return {"correct": False, "abstained": True}
        if t == "ctr" and v > 1: v = v / 100.0
        if t == "heart_mm": v = _mm(r, v)
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
