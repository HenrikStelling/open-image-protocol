"""Minimal MCP server (stdio, JSON-RPC 2.0) exposing OIP packages. Phase 5 will replace this with the official SDK;
this stub documents the intended resource/tool surface and is runnable for local experiments.

Resources: oip://<pkg>/manifest, oip://<pkg>/context, oip://<pkg>/renders/canonical, oip://<pkg>/renders/annotated
Tools:     oip_describe(pkg), oip_measure_px_to_mm(pkg, px), oip_validate(pkg)
"""
from __future__ import annotations
import base64, json, sys
from pathlib import Path
from .measure import CalibrationError, px_to_mm
from .validate import validate_package

TOOLS = [
    {"name": "oip_describe", "description": "Return the natural-language reference file (context.md) and manifest for an OIP package.",
     "inputSchema": {"type": "object", "properties": {"package": {"type": "string", "description": "Path to a .oip directory"}}, "required": ["package"]}},
    {"name": "oip_measure_px_to_mm", "description": "Convert a pixel distance to millimetres using the package's calibrated spacing. Refuses if no spacing exists.",
     "inputSchema": {"type": "object", "properties": {"package": {"type": "string"}, "px": {"type": "number"}, "axis": {"type": "integer", "enum": [0, 1], "default": 1}}, "required": ["package", "px"]}},
    {"name": "oip_validate", "description": "Validate an OIP package against the schema and package rules.",
     "inputSchema": {"type": "object", "properties": {"package": {"type": "string"}}, "required": ["package"]}},
]


def _call(name, args):
    pkg = Path(args["package"])
    if name == "oip_describe":
        m = json.loads((pkg / "oip.json").read_text())
        img = base64.b64encode((pkg / "renders/annotated.png").read_bytes()).decode()
        return {"content": [{"type": "text", "text": (pkg / "context.md").read_text()}, {"type": "image", "data": img, "mimeType": "image/png"}],
                "structuredContent": {"manifest": m}}
    if name == "oip_measure_px_to_mm":
        m = json.loads((pkg / "oip.json").read_text())
        try:
            mm = px_to_mm(args["px"], m, args.get("axis", 1))
            cal = m["geometry"]["calibration"]
            return {"content": [{"type": "text", "text": f"{mm:.2f} mm (spacing source {m['geometry']['spacing_source']}, plane {cal['plane']}, confidence {cal['confidence']})"}]}
        except CalibrationError as e:
            return {"content": [{"type": "text", "text": f"REFUSED: {e}"}], "isError": True}
    if name == "oip_validate":
        errs = validate_package(pkg)
        return {"content": [{"type": "text", "text": "OK" if not errs else "\n".join(errs)}], "isError": bool(errs)}
    raise KeyError(name)


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line); mid = req.get("id"); meth = req.get("method")
        if meth in ("initialize", "server/discover"):
            res = {"protocolVersion": "2025-06-18", "supportedVersions": ["2025-06-18"], "capabilities": {"tools": {}, "resources": {}},
                   "serverInfo": {"name": "oip", "version": "0.1.0"}}
        elif meth == "tools/list":
            res = {"tools": TOOLS}
        elif meth == "tools/call":
            res = _call(req["params"]["name"], req["params"].get("arguments", {}))
        elif meth == "notifications/initialized":
            continue
        else:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"unknown method {meth}"}}) + "\n"); sys.stdout.flush(); continue
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": res}) + "\n"); sys.stdout.flush()


if __name__ == "__main__":
    main()
