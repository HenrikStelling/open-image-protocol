"""Schema + package-rule validation."""
from __future__ import annotations
import json
from pathlib import Path
import jsonschema

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "spec" / "schemas" / "oip-manifest.schema.json"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def validate_manifest(manifest: dict) -> list[str]:
    v = jsonschema.Draft202012Validator(load_schema())
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in v.iter_errors(manifest)]


def validate_package(pkg: Path) -> list[str]:
    errs = []
    mp = pkg / "oip.json"
    if not mp.exists():
        return ["oip.json missing"]
    m = json.loads(mp.read_text())
    errs += validate_manifest(m)
    for req in ["context.md", "renders/canonical.png"]:
        if not (pkg / req).exists():
            errs.append(f"{req} missing")
    for r in m.get("renders", []):
        if not (pkg / r["path"]).exists():
            errs.append(f"render {r['path']} missing")
    for p in (m.get("pixels") or {}).get("paths", []):
        if not (pkg / p).exists():
            errs.append(f"pixels {p} missing")
    if m["geometry"]["pixel_spacing_mm"] is None and m["geometry"]["spacing_source"] != "none":
        errs.append("spacing_source must be 'none' when pixel_spacing_mm is null")
    if m["geometry"]["pixel_spacing_mm"] is None and "missing_pixel_spacing" not in m["quality"]["flags"]:
        errs.append("missing_pixel_spacing flag required when pixel_spacing_mm is null")
    for x in (m.get("derived") or {}).get("measurements", []):
        if x["unit"] in ("mm", "cm", "mm2") and m["geometry"]["pixel_spacing_mm"] is None:
            errs.append(f"measurement {x['id']} in {x['unit']} without pixel spacing")
    return errs
