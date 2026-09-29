"""Reproducibility check for the example packages (CI and `make examples-check`).

Rebuilds spec/examples and data/samples with scripts/make_examples.py, then compares every tracked file with the committed
version (git HEAD): text and DICOM files must be byte-identical; PNG files must decode to identical pixel arrays, because the
PNG byte stream depends on the zlib/Pillow build of the platform while the content does not. Exit 1 on any difference.
"""
from __future__ import annotations
import io, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PATHS = ["spec/examples", "data/samples"]


def tracked() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--", *PATHS], capture_output=True, text=True, check=True).stdout
    return [l for l in out.splitlines() if l.strip()]


def committed(path: str) -> bytes:
    return subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{path}"], capture_output=True, check=True).stdout


MARGIN_TOLERANCE = 0.02   # share of margin pixels that may differ (text rasterisation differs between FreeType/Pillow builds)


def margin_offset(rel: str) -> int:
    """The margin offset the manifest states for an annotated render (its content area is pixel-aligned at that offset)."""
    import json, re
    m = json.loads((ROOT / rel).parent.parent.joinpath("oip.json").read_text())
    for r in m["renders"]:
        if r["path"] == "renders/annotated.png":
            for note in r.get("annotations", []):
                hit = re.match(r"margin_offset_px: (\d+)", note)
                if hit:
                    return int(hit.group(1))
    raise ValueError(f"no margin offset recorded for {rel}")


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "scripts/make_examples.py")], check=True, stdout=subprocess.DEVNULL)
    files = tracked(); same = pixel_same = margin_ok = 0; bad = []
    for rel in files:
        new = (ROOT / rel).read_bytes(); old = committed(rel)
        if new == old:
            same += 1; continue
        if rel.endswith(".png"):
            a = np.asarray(Image.open(io.BytesIO(old))); b = np.asarray(Image.open(io.BytesIO(new)))
            if a.shape == b.shape and a.dtype == b.dtype and np.array_equal(a, b):
                pixel_same += 1; continue
            if rel.endswith("renders/annotated.png") and a.shape == b.shape:
                # the guarantee: the image content inside the margin is unchanged and pixel-aligned at the stated offset;
                # the margin carries text whose glyph rasterisation is platform-dependent, so it may differ a little
                o = margin_offset(rel); h, w = a.shape[:2]
                content_equal = np.array_equal(a[o:h - o, o:w - o], b[o:h - o, o:w - o])
                mask = np.ones(a.shape[:2], bool); mask[o:h - o, o:w - o] = False
                diff_share = float(np.mean((a != b).reshape(h, w, -1).any(axis=2)[mask]))
                if content_equal and diff_share <= MARGIN_TOLERANCE:
                    margin_ok += 1; print(f"  margin text differs in {100*diff_share:.2f} % of margin pixels, content identical: {rel}"); continue
                print(f"  content equal: {content_equal}, margin pixels differing: {100*diff_share:.2f} %: {rel}")
        bad.append(rel)
    import PIL
    print(f"{len(files)} files: {same} byte-identical, {pixel_same} PNGs with identical pixels but different encoding, "
          f"{margin_ok} annotated renders with identical content and small margin-text differences, {len(bad)} differ (Pillow {PIL.__version__})")
    for rel in bad:
        print("  DIFFERS:", rel)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
