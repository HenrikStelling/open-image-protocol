"""`oip check`: pixel-side consistency checks that a consumer gets from the tools, whether or not the model would have made
them (design rule R4: safety in the driver, not in the model).

check_orientation — is the stated left/right orientation consistent with where the heart and the aortic arch sit in the
pixels? On a frontal chest radiograph both lie on the patient's LEFT, so their column centroid should fall on the side of the
thoracic midline that carries the edge label L. The check uses only the unsided `heart` and `aorta` masks and their geometry;
it does not use the segmentation model's left/right class labels, so it is independent of the display convention the
converter assumed (PLAN Phase 3b, "laterality check independence"). Mirroring the image flips the sign of the evidence.

Result: consistent | inconsistent | indeterminate, with the evidence, written to `quality.checks[]` (and the flag
`orientation_pixel_inconsistent` when it fails); context.md then reports the check next to the stated orientation.
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
from PIL import Image

TOOL = "oip-check"
TOOL_VERSION = "0.1.0"
CHECK_ID = "orientation_pixel_check"
FLAG = "orientation_pixel_inconsistent"
MIN_OFFSET = 0.02      # |centroid offset| / thoracic width below which the evidence is called indeterminate
STRONG_OFFSET = 0.05   # above this the check is confident (heart centroid on adults: ~0.05–0.15 toward the patient's left)


def _mask(pkg: Path, rid: str):
    p = pkg / f"derived/masks/{rid}.png"
    return (np.asarray(Image.open(p).convert("L")) > 127) if p.exists() else None


def _centroid_col(mask: np.ndarray) -> float:
    return float(np.nonzero(mask)[1].mean())


def orientation_evidence(masks: dict, width: int, edge_labels: dict) -> dict:
    """Pure geometry. masks: {id: bool array}; width: image columns; edge_labels: {'left': 'R', 'right': 'L', ...}.
    Returns {result, confidence, evidence{...}, reason?}."""
    lungs = [masks[k] for k in ("lung_left", "lung_right") if masks.get(k) is not None and masks[k].any()]
    if lungs:
        union = np.zeros_like(lungs[0], dtype=bool)
        for l in lungs:
            union |= l
        cols = np.nonzero(union.any(axis=0))[0]
        mid, tw = (cols.min() + cols.max()) / 2.0, int(cols.max() - cols.min() + 1)
        mid_src = "lung-union bbox centre"
    else:
        mid, tw, mid_src = width / 2.0, int(width), "image centre"
    ev = {"midline_col": round(float(mid), 1), "midline_source": mid_src, "thorax_width_px": tw, "structures": {}}
    if edge_labels.get("right") == "L":
        l_side = "right"
    elif edge_labels.get("left") == "L":
        l_side = "left"
    else:
        return {"result": "indeterminate", "confidence": 0.0, "evidence": ev, "reason": "no edge is labelled L"}
    sign = 1.0 if l_side == "right" else -1.0     # +: the patient's left structures should have centroid col > midline
    ev["l_edge"] = l_side
    for name in ("heart", "aorta"):
        mk = masks.get(name)
        if mk is None or not mk.any():
            continue
        off = (_centroid_col(mk) - mid) / tw
        ev["structures"][name] = {"centroid_offset_frac": round(float(off), 4),
                                  "toward": "L edge" if off * sign > 0 else "R edge",
                                  "mask_px": int(mk.sum())}
    if not ev["structures"]:
        return {"result": "indeterminate", "confidence": 0.0, "evidence": ev, "reason": "no heart or aorta mask"}
    primary = ev["structures"].get("heart") or ev["structures"]["aorta"]
    signed = primary["centroid_offset_frac"] * sign
    other = ev["structures"].get("aorta") if "heart" in ev["structures"] else None
    if other is not None and (other["centroid_offset_frac"] * sign) * signed < 0 and abs(other["centroid_offset_frac"]) >= MIN_OFFSET and abs(signed) < STRONG_OFFSET:
        return {"result": "indeterminate", "confidence": 0.3, "evidence": ev, "reason": "heart and aorta point to different edges"}
    if abs(signed) < MIN_OFFSET:
        return {"result": "indeterminate", "confidence": 0.3, "evidence": ev, "reason": "structures sit on the midline"}
    conf = 0.9 if abs(signed) >= STRONG_OFFSET else 0.7
    return {"result": "consistent" if signed > 0 else "inconsistent", "confidence": conf, "evidence": ev}


def check_image(canon_u8: np.ndarray, edge_labels: dict) -> dict:
    """Segment a canonical 8-bit frontal chest render (TorchXRayVision PSPNet, via oip.anatomy) and run the geometry check.
    Used for the mirrored pass and for evaluation; `check_orientation` prefers the stored masks for the first pass."""
    from .anatomy import segment
    return orientation_evidence(segment(canon_u8), canon_u8.shape[1], edge_labels)


def signed_offset(r: dict):
    """Heart (else aorta) centroid offset as a signed fraction of thoracic width, positive toward the edge labelled L; None if absent."""
    ev = r.get("evidence") or {}
    st = (ev.get("structures") or {}).get("heart") or (ev.get("structures") or {}).get("aorta")
    if not st or "l_edge" not in ev:
        return None
    return st["centroid_offset_frac"] * (1.0 if ev["l_edge"] == "right" else -1.0)


def combine_two_pass(o_image: float, o_mirror: float) -> dict:
    """Prior-free orientation evidence from two segmentations, of the image and of its mirror.
    The segmentation model carries a positional prior (it expects a heart where hearts usually are): on a mirrored image the
    mask is pulled back toward the conventional side, so a single pass under-reads the flip (VinDr-100, 2026-09-26: 71 of 100
    mirrored images detected, 24 indeterminate, 5 wrong). If o = s + p on the image and −s + p on its mirror (s the anatomical
    side signal, p the prior in image coordinates), then (o_image − o_mirror) / 2 = s cancels the prior. On VinDr-100 s was
    positive for 100 of 100 shipped images (min 0.002, median 0.063), 94 of 100 above 0.02, with no wrong sign at any threshold;
    by symmetry a mirrored input gives −s."""
    s = (o_image - o_mirror) / 2.0
    p = (o_image + o_mirror) / 2.0
    if abs(s) < MIN_OFFSET:
        return {"result": "indeterminate", "confidence": 0.3, "prior_free_offset_frac": round(s, 4), "model_prior_frac": round(p, 4), "reason": "prior-free offset below threshold"}
    return {"result": "consistent" if s > 0 else "inconsistent", "confidence": 0.9 if abs(s) >= STRONG_OFFSET else 0.7,
            "prior_free_offset_frac": round(s, 4), "model_prior_frac": round(p, 4)}


def check_orientation(pkg: Path, write: bool = True, two_pass: bool = True) -> dict:
    """Run the check on a package. Pass 1 uses derived/masks/*.png when present (no model call), otherwise segments the
    canonical render. With two_pass=True (default) pass 2 segments the mirrored canonical render and the verdict comes from
    the prior-free difference (see combine_two_pass); if the model is unavailable the single-pass geometry is used and said
    so. With write=True the record goes to quality.checks (replacing an earlier record of the same id), the flag is set or
    cleared, and context.md is re-rendered."""
    pkg = Path(pkg)
    m = json.loads((pkg / "oip.json").read_text())
    fam = m["acquisition"].get("modality_family")
    el = m["geometry"]["orientation"].get("edge_labels", {}) or {}
    method = "column centroid of the unsided heart (and aortic-arch) mask relative to the thoracic midline, compared with the edge labelled L"
    if fam != "projection_radiography":
        res = {"result": "indeterminate", "confidence": 0.0, "evidence": {}, "reason": f"no pixel check defined for {fam}"}
        inputs = []
    else:
        masks = {rid: _mask(pkg, rid) for rid in ("heart", "aorta", "lung_left", "lung_right")}
        canon = None
        if all(v is None for v in masks.values()):
            canon = np.asarray(Image.open(pkg / "renders/canonical.png").convert("L"))
            res = check_image(canon, el); inputs = ["renders/canonical.png"]
        else:
            res = orientation_evidence(masks, m["geometry"]["columns"], el)
            inputs = [f"derived/masks/{rid}.png" for rid, v in masks.items() if v is not None]
        res["evidence"] = {"pass1_image": res.get("evidence", {}), "single_pass": True}
        o1 = signed_offset({"evidence": res["evidence"]["pass1_image"]})
        if two_pass and o1 is not None:
            try:
                if canon is None:
                    canon = np.asarray(Image.open(pkg / "renders/canonical.png").convert("L"))
                r2 = check_image(canon[:, ::-1].copy(), el)
                o2 = signed_offset(r2)
                if o2 is not None:
                    c = combine_two_pass(o1, o2)
                    res = {"result": c["result"], "confidence": c["confidence"],
                           "evidence": {"pass1_image": res["evidence"]["pass1_image"], "pass2_mirrored_image": r2.get("evidence", {}),
                                        "prior_free_offset_frac": c["prior_free_offset_frac"], "model_prior_frac": c["model_prior_frac"], "single_pass": False}}
                    if c.get("reason"):
                        res["reason"] = c["reason"]
                    inputs = sorted(set(inputs) | {"renders/canonical.png"})
                    method = ("prior-free two-pass: signed heart-centroid offset toward the edge labelled L on the image minus the same on its mirror, "
                              "halved; the segmentation model's positional prior cancels")
            except Exception as e:   # noqa: BLE001 — no torch, no model weights: fall back to the single pass and say so
                res["reason"] = (res.get("reason", "") + f"; single pass only ({type(e).__name__})").strip("; ")
    rec = {"id": CHECK_ID, "result": res["result"], "confidence": res["confidence"], "assertion_level": "computed",
           "tool": TOOL, "tool_version": TOOL_VERSION, "method": method, "evidence": res.get("evidence", {}), "inputs": inputs}
    if res.get("reason"):
        rec["reason"] = res["reason"]
    if write:
        q = m["quality"]
        q["checks"] = [c for c in q.get("checks", []) if c.get("id") != CHECK_ID] + [rec]
        flags = [f for f in q.get("flags", []) if f != FLAG]
        if rec["result"] == "inconsistent":
            flags.append(FLAG)
        q["flags"] = flags
        (pkg / "oip.json").write_text(json.dumps(m, indent=2))
        from .context import build_context
        (pkg / "context.md").write_text(build_context(m))
    return rec
