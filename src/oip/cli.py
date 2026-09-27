"""oip command line: convert | validate | describe."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .convert import convert
from .validate import validate_package


def main(argv=None):
    p = argparse.ArgumentParser(prog="oip", description="Open Image Protocol tools")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("convert", help="DICOM -> .oip package"); c.add_argument("src"); c.add_argument("out"); c.add_argument("--title"); c.add_argument("--include-original", action="store_true")
    v = sub.add_parser("validate", help="validate a package"); v.add_argument("pkg")
    d = sub.add_parser("describe", help="print context.md"); d.add_argument("pkg"); d.add_argument("--json", action="store_true"); d.add_argument("--with-external", action="store_true", help="render external labels/report text (OEP-001: off by default)")
    w = sub.add_parser("window", help="re-window pixels into a new render"); w.add_argument("pkg"); w.add_argument("--center", type=float); w.add_argument("--width", type=float); w.add_argument("--preset", choices=["bone", "lung", "soft_tissue", "brain", "liver"]); w.add_argument("--frame", type=int, default=0)
    cr = sub.add_parser("crop", help="crop canonical render: r0 c0 r1 c1"); cr.add_argument("pkg"); cr.add_argument("bbox", type=int, nargs=4); cr.add_argument("--upscale", type=int, default=1); cr.add_argument("--frame", type=int, default=0)
    ov = sub.add_parser("overlay", help="annotated render with selected regions and/or a mm grid"); ov.add_argument("pkg"); ov.add_argument("--regions", nargs="*"); ov.add_argument("--grid-mm", type=float); ov.add_argument("--name", default="overlay")
    me = sub.add_parser("measure", help="run the chest anatomy adapter (regions + CTR)"); me.add_argument("pkg")
    ck = sub.add_parser("check", help="pixel-side check of the stated orientation (heart/aortic-arch side vs the edge labelled L); writes quality.checks"); ck.add_argument("pkg"); ck.add_argument("--no-write", action="store_true", help="report only; do not modify the package")
    a = p.parse_args(argv)
    if a.cmd == "convert":
        out = convert(a.src, a.out, title=a.title, include_original=a.include_original); print(out)
    elif a.cmd == "validate":
        errs = validate_package(Path(a.pkg)); print("\n".join(errs) if errs else "OK"); sys.exit(1 if errs else 0)
    elif a.cmd == "window":
        from .tools import window; print(json.dumps(window(Path(a.pkg), a.center, a.width, a.preset, a.frame), indent=1))
    elif a.cmd == "crop":
        from .tools import crop; print(json.dumps(crop(Path(a.pkg), a.bbox, a.upscale, a.frame), indent=1))
    elif a.cmd == "overlay":
        from .tools import overlay; print(json.dumps(overlay(Path(a.pkg), a.regions, a.grid_mm, a.name), indent=1))
    elif a.cmd == "measure":
        from .anatomy import measure_chest; print(json.dumps(measure_chest(Path(a.pkg)), indent=1))
    elif a.cmd == "check":
        from .check import check_orientation; print(json.dumps(check_orientation(Path(a.pkg), write=not a.no_write), indent=1))
    elif a.cmd == "describe":
        pkg = Path(a.pkg)
        if a.json: print((pkg / "oip.json").read_text())
        elif a.with_external:
            from .context import build_context; print(build_context(json.loads((pkg / "oip.json").read_text()), include_external=True))
        else: print((pkg / "context.md").read_text())


if __name__ == "__main__":
    main()
