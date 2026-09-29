"""Render rules: canonical 8-bit (high_is_bright), annotated render with edge labels and scale bar."""
from __future__ import annotations
import numpy as np
from pathlib import Path
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


def save_png16(arr: np.ndarray, path, bits_stored: int = 16) -> str:
    """Lossless PNG of stored pixel values. 8-bit PNG when the source has <= 8 bits stored (keeps packages small);
    16-bit otherwise. Signed data is shifted to unsigned (offset recorded by the caller). Returns the format name."""
    a = np.asarray(arr)
    if a.dtype.kind == "i":
        a = (a.astype(np.int64) - int(a.min())).astype(np.uint16)
    if bits_stored <= 8 and a.max() <= 255:
        Image.fromarray(a.astype(np.uint8)).save(path); return "png8"
    Image.fromarray(a.astype(np.uint16)).save(path); return "png16"


_VENDORED_FONT = Path(__file__).resolve().parent / "fonts" / "DejaVuSans.ttf"   # shipped with the package (Bitstream Vera licence, see fonts/LICENSE_DEJAVU)


def _font(size: int):
    """The vendored DejaVu Sans, so that annotated renders are identical on every platform; system fonts only as a fallback."""
    for name in (str(_VENDORED_FONT), "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def inspection_sheet(canon: np.ndarray, edge_labels: dict, spacing_mm, heart_bbox: list[int] | None = None,
                     side: int = 1536, badge_px: int = 96, inset_px: int = 384) -> tuple[Image.Image, list[str]]:
    """Encoder-safe inspection sheet (OEP-005 draft, 2026-09-27; Codex proposal 1). A fixed side×side canvas so that nothing
    is lost to provider downscaling: the whole image fills ~70 % of the height, large R/L edge badges (badge_px tall after the
    final resize), an enlarged heart-region inset with a locator, and a calibrated ruler with 10 mm ticks and 50 mm labels,
    or a crossed-out ruler when no spacing is known. No region marks, no region names, no numeric measurement: the sheet
    carries visual anchors only. The canonical pixels are resampled (Lanczos) for display; coordinates are recorded in notes."""
    S = side; bg = 32; bw = badge_px + 40
    canvas = Image.new("L", (S, S), bg); d = ImageDraw.Draw(canvas)
    h, w = canon.shape; box_w, box_h = S - 2 * bw, int(0.70 * S)
    sc = min(box_w / w, box_h / h); dw, dh = max(1, int(round(w * sc))), max(1, int(round(h * sc)))
    im = Image.fromarray(canon).resize((dw, dh), Image.LANCZOS)
    x0, y0 = bw + (box_w - dw) // 2, 8 + (box_h - dh) // 2
    canvas.paste(im, (x0, y0))
    notes = [f"sheet {S}x{S}; whole image at ({x0},{y0}) size {dw}x{dh}, scale {sc:.4f} (frame_coord = (sheet_coord - offset) / scale)"]
    fb = _font(badge_px); yc = y0 + dh // 2
    for key, xb in (("left", 12), ("right", S - bw + 12)):
        lab = edge_labels.get(key)
        if not lab:
            continue
        tw = d.textlength(lab, font=fb)
        d.rounded_rectangle([xb, yc - badge_px * 0.75, xb + bw - 24, yc + badge_px * 0.75], radius=12, fill=0, outline=255, width=4)
        d.text((xb + (bw - 24 - tw) / 2, yc - badge_px * 0.62), lab, fill=255, font=fb)
        notes.append(f"badge {key} edge = {lab}, {badge_px} px letters")
    fc = _font(26); ft = _font(28)
    ys = box_h + 28; d.line([(bw, ys - 8), (S - bw, ys - 8)], fill=96, width=2)
    # heart-region inset with a locator thumbnail
    if heart_bbox:
        r0, c0, r1, c1 = [int(v) for v in heart_bbox]; ph, pw = int(0.2 * (r1 - r0)), int(0.2 * (c1 - c0))
        R0, C0, R1, C1 = max(0, r0 - ph), max(0, c0 - pw), min(h - 1, r1 + ph), min(w - 1, c1 + pw)
        crop = Image.fromarray(canon[R0:R1 + 1, C0:C1 + 1]); csc = min(inset_px / crop.width, inset_px / crop.height)
        crop = crop.resize((max(1, int(crop.width * csc)), max(1, int(crop.height * csc))), Image.LANCZOS)
        ix, iy = bw, ys + 34; canvas.paste(crop, (ix, iy)); d.rectangle([ix - 2, iy - 2, ix + crop.width + 1, iy + crop.height + 1], outline=255, width=2)
        d.text((ix, ys), "heart region, enlarged (inset)", fill=255, font=fc)
        # locator: a small copy of the whole image with the inset rectangle
        lsc = 120 / max(w, h); loc = Image.fromarray(canon).resize((max(1, int(w * lsc)), max(1, int(h * lsc))), Image.LANCZOS)
        lx, ly = ix + inset_px + 24, iy; canvas.paste(loc, (lx, ly))
        d.rectangle([lx + C0 * lsc, ly + R0 * lsc, lx + C1 * lsc, ly + R1 * lsc], outline=255, width=2)
        d.text((lx, ly + loc.height + 6), "location", fill=200, font=fc)
        notes.append(f"inset: frame rows {R0}-{R1}, cols {C0}-{C1}, scale {csc:.3f}, at ({ix},{iy})")
        rx = lx + 120 + 48
    else:
        rx = bw
    # ruler
    ry = ys + 34 + inset_px // 2; rlen = S - bw - rx
    if spacing_mm:
        px_per_mm = sc / float(spacing_mm[1]); mm_total = int(rlen / px_per_mm // 50 * 50)
        if mm_total >= 50:
            d.text((rx, ys), "scale in mm (calibrated to the whole image)", fill=255, font=fc)
            d.line([(rx, ry), (rx + mm_total * px_per_mm, ry)], fill=255, width=4)
            for mm in range(0, mm_total + 1, 10):
                x = rx + mm * px_per_mm; major = mm % 50 == 0
                d.line([(x, ry), (x, ry - (36 if major else 16))], fill=255, width=4 if major else 2)
                if major:
                    d.text((x - d.textlength(str(mm), font=ft) / 2, ry + 10), str(mm), fill=255, font=ft)
            notes.append(f"ruler: 0-{mm_total} mm at {px_per_mm:.3f} sheet px per mm, ticks every 10 mm, labels every 50 mm")
        else:
            spacing_mm = None
    if not spacing_mm:
        d.text((rx, ys), "NO CALIBRATED SCALE", fill=255, font=ft)
        d.rectangle([rx, ry - 24, rx + min(rlen, 600), ry + 24], outline=255, width=4)
        for k in range(0, min(rlen, 600), 60):
            d.line([(rx + k, ry - 24), (rx + k, ry)], fill=255, width=2)
        d.line([(rx, ry - 60), (rx + min(rlen, 600), ry + 60)], fill=255, width=10)
        d.line([(rx, ry + 60), (rx + min(rlen, 600), ry - 60)], fill=255, width=10)
        notes.append("ruler: none (no calibrated spacing), crossed-out ruler symbol")
    return canvas, notes


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
