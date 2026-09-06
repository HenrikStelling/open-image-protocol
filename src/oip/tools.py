"""Read-only verbs beyond describe/measure/validate: window, crop, overlay. Each returns a new render file and a
transform record; the canonical render and pixels are never modified (spec section 7)."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from PIL import Image
from .render import annotated

PRESETS = {"bone": (2000, 1500), "lung": (-600, 1500), "soft_tissue": (40, 400), "brain": (40, 80), "liver": (60, 160)}  # HU presets (CT only)


def _load(pkg: Path):
    pkg = Path(pkg); m = json.loads((pkg / "oip.json").read_text()); return pkg, m


def _stored_values(pkg: Path, m: dict, frame: int = 0) -> np.ndarray:
    arr = np.asarray(Image.open(pkg / m["pixels"]["paths"][frame])).astype(np.float64)
    r = m["intensity"].get("rescale") or {}
    return arr * r.get("slope", 1.0) + r.get("intercept", 0.0)


def window(pkg: Path, center: float | None = None, width: float | None = None, preset: str | None = None, frame: int = 0, name: str | None = None) -> dict:
    """Re-window the lossless pixels. Returns {path, transform}. Polarity follows the canonical guarantee (high = bright)."""
    pkg, m = _load(pkg)
    if preset:
        if m["intensity"]["units"] != "HU": raise ValueError(f"preset '{preset}' is defined in Hounsfield units; this image has units '{m['intensity']['units']}'")
        center, width = PRESETS[preset]
    if center is None or width is None: raise ValueError("center and width (or a preset) are required")
    v = _stored_values(pkg, m, frame); lo, hi = center - width / 2, center + width / 2
    img = np.clip((v - lo) / (hi - lo), 0, 1)
    if m["intensity"].get("source_inverted_for_render"): img = 1 - img
    u8 = (img * 255).round().astype(np.uint8)
    name = name or f"window_c{center:g}_w{width:g}"; out = pkg / "renders" / f"{name}.png"; Image.fromarray(u8).save(out)
    rec = {"path": f"renders/{name}.png", "purpose": "overlay", "frame": frame, "width": u8.shape[1], "height": u8.shape[0],
           "transform": f"linear window center {center:g} width {width:g} in units '{m['intensity']['units']}' applied to rescaled stored pixels; high = bright; no resample."}
    _append_render(pkg, m, rec); return rec


def crop(pkg: Path, bbox_px: list[int], upscale: int = 1, frame: int = 0, name: str | None = None) -> dict:
    """Crop the canonical render to [r0, c0, r1, c1] (inclusive) and optionally upscale (nearest). Records the offset so
    coordinates map back: frame_coord = crop_coord / upscale + (r0, c0)."""
    pkg, m = _load(pkg)
    src = pkg / ("renders/canonical.png" if m["geometry"].get("number_of_frames", 1) == 1 else f"renders/frame-{frame:04d}.png")
    im = Image.open(src); r0, c0, r1, c1 = [int(x) for x in bbox_px]
    r0, c0 = max(r0, 0), max(c0, 0); r1, c1 = min(r1, im.height - 1), min(c1, im.width - 1)
    cr = im.crop((c0, r0, c1 + 1, r1 + 1))
    if upscale > 1: cr = cr.resize((cr.width * upscale, cr.height * upscale), Image.NEAREST)
    name = name or f"crop_{r0}_{c0}_{r1}_{c1}" + (f"_x{upscale}" if upscale > 1 else ""); out = pkg / "renders" / f"{name}.png"; cr.save(out)
    sp = m["geometry"]["pixel_spacing_mm"]
    rec = {"path": f"renders/{name}.png", "purpose": "overlay", "frame": frame, "width": cr.width, "height": cr.height,
           "transform": f"crop of canonical render rows {r0}-{r1}, cols {c0}-{c1}" + (f", nearest-neighbour upscale x{upscale}" if upscale > 1 else "") + f". frame_coord = crop_coord/{upscale} + ({r0}, {c0})." + (f" Effective spacing {sp[0]/upscale:.4g} x {sp[1]/upscale:.4g} mm/px." if sp else " No calibrated spacing.")}
    _append_render(pkg, m, rec); return rec


def overlay(pkg: Path, regions: list[str] | None = None, grid_mm: float | None = None, name: str = "overlay") -> dict:
    """Annotated render with a chosen subset of regions and/or a metric grid (needs spacing)."""
    pkg, m = _load(pkg)
    canon = np.asarray(Image.open(pkg / "renders/canonical.png").convert("L")); regs = m.get("derived", {}).get("regions", [])
    if regions: regs = [r for r in regs if r["id"] in regions or r.get("mark") in regions]
    sp = m["geometry"]["pixel_spacing_mm"]
    img, notes = annotated(canon, m["geometry"]["orientation"]["edge_labels"] if m["geometry"].get("number_of_frames", 1) == 1 else {}, sp, f"{m['identity']['title']} · overlay", marks=regs)
    if grid_mm:
        if not sp: raise ValueError("grid_mm needs calibrated pixel spacing")
        from PIL import ImageDraw
        d = ImageDraw.Draw(img); mrg = int(notes[0].split(":")[1].split()[0]); H, W = canon.shape
        step_r, step_c = grid_mm / sp[0], grid_mm / sp[1]
        y = 0.0
        while y < H: d.line([(mrg, mrg + y), (mrg + W, mrg + y)], fill=110); y += step_r
        x = 0.0
        while x < W: d.line([(mrg + x, mrg), (mrg + x, mrg + H)], fill=110); x += step_c
        notes.append(f"grid: {grid_mm:g} mm spacing ({step_c:.1f} px horizontally, {step_r:.1f} px vertically)")
    out = pkg / "renders" / f"{name}.png"; img.save(out)
    rec = {"path": f"renders/{name}.png", "purpose": "overlay", "frame": None, "width": img.width, "height": img.height,
           "transform": "canonical render in a dark margin with selected region marks" + (f" and a {grid_mm:g} mm grid" if grid_mm else "") + "; content pixel-aligned at the stated offset.", "annotations": notes}
    _append_render(pkg, m, rec); return rec


def _append_render(pkg: Path, m: dict, rec: dict):
    m["renders"] = [r for r in m["renders"] if r["path"] != rec["path"]] + [rec]
    (pkg / "oip.json").write_text(json.dumps(m, indent=2))
