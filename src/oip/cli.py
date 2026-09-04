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
    d = sub.add_parser("describe", help="print context.md"); d.add_argument("pkg"); d.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    if a.cmd == "convert":
        out = convert(a.src, a.out, title=a.title, include_original=a.include_original); print(out)
    elif a.cmd == "validate":
        errs = validate_package(Path(a.pkg)); print("\n".join(errs) if errs else "OK"); sys.exit(1 if errs else 0)
    elif a.cmd == "describe":
        pkg = Path(a.pkg); print((pkg / "oip.json").read_text() if a.json else (pkg / "context.md").read_text())


if __name__ == "__main__":
    main()
