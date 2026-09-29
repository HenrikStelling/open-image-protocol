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


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "scripts/make_examples.py")], check=True, stdout=subprocess.DEVNULL)
    files = tracked(); same = pixel_same = 0; bad = []
    for rel in files:
        new = (ROOT / rel).read_bytes(); old = committed(rel)
        if new == old:
            same += 1; continue
        if rel.endswith(".png"):
            a = np.asarray(Image.open(io.BytesIO(old))); b = np.asarray(Image.open(io.BytesIO(new)))
            if a.shape == b.shape and a.dtype == b.dtype and np.array_equal(a, b):
                pixel_same += 1; continue
        bad.append(rel)
    print(f"{len(files)} files: {same} byte-identical, {pixel_same} PNGs with identical pixels but different encoding, {len(bad)} differ")
    for rel in bad:
        print("  DIFFERS:", rel)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
