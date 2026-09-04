"""Render rules: canonical 8-bit (high_is_bright), annotated render with edge labels and scale bar."""
from __future__ import annotations
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pydicom.dataset import Dataset

try:
    from pydicom.pixels import apply_modality_lut, apply_voi_lut
except ImportError:  # pydicom < 3
    from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut


def rescaled(ds: Dataset, arr: np.ndarray) -> np.ndarray:
    """Apply Modality LUT / rescale so values are in the declared units."""
    return np.asarray(apply_modality_lut(arr, ds), dtype=np.float64)


def canonical_8bit(ds: Dataset, frame: np.ndarray) -> tuple[np.ndarray, dict, list[str]]:
    """Return (uint8 array, voi record, pipeline steps). Guarantees high_is_bright."""
    steps: list[str] = []
    values = rescaled(ds, frame)
    steps.append("apply Modality LUT / RescaleSlope+Intercept")
    voi: dict
    has_wc = ds.get("WindowCenter") is not None and ds.get("WindowWidth") is not None
    has_lut = ds.get("VOILUTSequence") is not None
    modality = str(ds.get("Modality", ""))
    if has_wc or has_lut:
        out = np.asarray(apply_voi_lut(frame, ds, prefer_lut=has_lut), dtype=np.float64)
        lo, hi = float(out.min()), float(out.max())
        img = (out - lo) / (hi - lo) if hi > lo else np.zeros_like(out)
        wc = ds.get("WindowCenter"); ww = ds.get("WindowWidth")
        wc = float(wc[0] if isinstance(wc, (list, tuple)) or hasattr(wc, "__len__") and not isinstance(wc, str) else wc) if has_wc else None
        ww = float(ww[0] if isinstance(ww, (list, tuple)) or hasattr(ww, "__len__") and not isinstance(ww, str) else ww) if has_wc else None
        voi = dict(source="VOILUTSequence" if has_lut else "WindowCenterWidth", center=wc, width=ww,
                   function=str(ds.get("VOILUTFunction")) if ds.get("VOILUTFunction") else None, lower=None, upper=None)
        steps.append(f"apply VOI ({voi['source']})")
    else:
        if modality == "NM":
            lo, hi = 0.0, float(np.percentile(values, 99.5))
            v = np.sqrt(np.clip(values, 0, hi)); img = v / (np.sqrt(hi) if hi > 0 else 1)
            voi = dict(source="sqrt", center=None, width=None, function=None, lower=lo, upper=hi)
            steps.append("no VOI in source; sqrt scaling, clipped at 99.5th percentile")
        else:
            lo, hi = float(np.percentile(values, 0.5)), float(np.percentile(values, 99.5))
            img = (np.clip(values, lo, hi) - lo) / (hi - lo) if hi > lo else np.zeros_like(values)
            voi = dict(source="auto_percentile", center=None, width=None, function=None, lower=lo, upper=hi)
            steps.append("no VOI in source; linear window between 0.5th and 99.5th percentile")
    inverted = False
    if str(ds.get("PhotometricInterpretation", "")) == "MONOCHROME1" or str(ds.get("PresentationLUTShape", "")) == "INVERSE":
        img = 1.0 - img; inverted = True
        steps.append("invert (source was MONOCHROME1/INVERSE) so high attenuation is bright")
    u8 = np.clip(np.round(img * 255), 0, 255).astype(np.uint8)
    voi["_inverted"] = inverted
    return u8, voi, steps


def save_png16(arr: np.ndarray, path) -> None:
    a = np.asarray(arr)
    if a.dtype.kind == "i":  # signed -> store as int32 PNG not supported; shift to uint16 with note in manifest
        a = (a.astype(np.int64) - int(a.min())).astype(np.uint16)
    Image.fromarray(a.astype(np.uint16)).save(path)


def _font(size: int):
    for name in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def annotated(canon: np.ndarray, edge_labels: dict, spacing_mm, title: str, marks: list[dict] | None = None,
              scale_bar_mm: float = 50.0, frame_labels: list[dict] | None = None) -> tuple[Image.Image, list[str]]:
    """Letterbox the canonical render with a margin carrying edge labels, a scale bar and region marks.
    Returns (image, annotation notes including margin offsets)."""
    h, w = canon.shape
    m = max(40, int(0.06 * max(h, w)))
    canvas = Image.new("L", (w + 2 * m, h + 2 * m), 32)
    canvas.paste(Image.fromarray(canon), (m, m))
    d = ImageDraw.Draw(canvas)
    f = _font(max(14, m // 2)); fs = _font(max(11, m // 3))
    notes = [f"margin_offset_px: {m} (subtract from annotated coords to get frame coords)"]
    fsize = max(14, m // 2)
    labels = {"left": (4, h // 2 + m), "right": (w + m + 4, h // 2 + m), "top": (w // 2 + m, m - fsize - 2), "bottom": (w // 2 + m, h + m + 4)}
    for side, (x, y) in labels.items():
        lab = edge_labels.get(side)
        if lab:
            d.text((x, y), lab, fill=255, font=f)
    notes.append("edge labels: " + ", ".join(f"{k}={v}" for k, v in edge_labels.items() if v))
    # per-frame labels for composites: view name above each frame, side labels at each frame's edges
    for fl in frame_labels or []:
        x0, fw = fl["x_offset"] + m, fl["width"]
        if fl.get("view"):
            d.text((x0 + 2, m - fsize - 2), str(fl["view"]), fill=255, font=fs)
        if fl.get("left"):
            d.text((x0 + 2, h // 2 + m), str(fl["left"]), fill=255, font=f)
        if fl.get("right"):
            d.text((x0 + fw - fsize, h // 2 + m), str(fl["right"]), fill=255, font=f)
        notes.append(f"frame {fl.get('index')} ({fl.get('view') or '?'}): x-offset {fl['x_offset']} px, left edge={fl.get('left')}, right edge={fl.get('right')}")
    # title: shrink to fit the canvas width
    tsize = max(11, m // 3)
    while tsize > 9 and d.textlength(title, font=_font(tsize)) > canvas.width - 2 * m:
        tsize -= 1
    d.text((m, 2), title, fill=255, font=_font(tsize))
    if spacing_mm:
        px = int(round(scale_bar_mm / float(spacing_mm[1])))
        y = h + m + m // 2
        d.line([(m, y), (m + px, y)], fill=255, width=max(2, m // 12))
        d.text((m + px + 6, y - m // 6), f"{scale_bar_mm:g} mm", fill=255, font=fs)
        notes.append(f"scale bar: {scale_bar_mm:g} mm = {px} px, bottom-left")
    else:
        d.text((m, h + m + m // 3), "NO CALIBRATED SCALE - do not estimate sizes in mm", fill=255, font=fs)
        notes.append("scale bar: none (pixel spacing unknown)")
    for r in marks or []:
        if r.get("bbox_px") and r.get("mark"):
            r0, c0, r1, c1 = r["bbox_px"]
            d.rectangle([c0 + m, r0 + m, c1 + m, r1 + m], outline=255, width=2)
            d.text((c0 + m + 3, r0 + m + 3), str(r["mark"]), fill=255, font=f)
            notes.append(f"mark {r['mark']} = {r.get('label')}")
    return canvas, notes
