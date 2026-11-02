"""Local server for the reading sheet: serves bench/reader/ and appends every saved answer to readings/<reader_id>.csv.

Usage: python bench/reader/serve.py [--port 8765]     then open http://127.0.0.1:8765/reader.html
Binds to 127.0.0.1 only. No cloud, no upload: the renders never leave this machine (VinDr is not redistributed).
  POST /save            JSON row -> appended to readings/<reader_id>.csv (header written once); append-only, every revision kept
  GET  /readings/ping   {"ok": true}  (the sheet uses it to detect autosave mode)
  GET  /readings/<reader_id>.csv   the file, for resuming in another browser
"""
from __future__ import annotations
import argparse, csv, json, re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
HERE = Path(__file__).resolve().parent
COLS = ["ts_utc", "reader_id", "role", "block", "item_id", "dataset", "task", "revision", "answer", "basis",
        "heart_x1", "heart_y1", "heart_x2", "heart_y2", "heart_px", "thorax_x1", "thorax_y1", "thorax_x2", "thorax_y2", "thorax_px", "ctr",
        "ap_projection", "marker_x", "marker_y", "marker_quadrant", "not_assessable", "unsure", "comment", "secs",
        "image_w", "image_h", "image_sha256", "tool_version"]
SAFE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE), **k)

    def log_message(self, format, *args):   # quiet except errors
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(format, *args)

    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        if self.path == "/readings/ping":
            return self._json(200, {"ok": True, "cols": COLS})
        if self.path.startswith("/readings/"):
            name = self.path.split("/")[-1]
            if not (name.endswith(".csv") and SAFE.match(name[:-4])):
                return self._json(400, {"error": "bad name"})
            f = HERE / "readings" / name
            if not f.exists():
                return self._json(404, {"error": "no such file"})
        return super().do_GET()

    def do_POST(self):
        if self.path != "/save":
            return self._json(404, {"error": "unknown endpoint"})
        try:
            row = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))).decode())
        except Exception as e:
            return self._json(400, {"error": f"bad json: {e}"})
        rid = str(row.get("reader_id", ""))
        if not SAFE.match(rid):
            return self._json(400, {"error": "reader_id must be 1-32 letters, digits, _ or -"})
        d = HERE / "readings"; d.mkdir(exist_ok=True); f = d / f"{rid}.csv"; new = not f.exists()
        with open(f, "a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
            if new:
                w.writeheader()
            w.writerow({c: ("" if row.get(c) is None else row.get(c)) for c in COLS})
        return self._json(200, {"ok": True, "file": f.name})

    def end_headers(self):
        self.send_header("Cache-Control", "no-store"); super().end_headers()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8765); a = ap.parse_args()
    if not (HERE / "reader.html").exists():
        raise SystemExit("reader.html missing: run python bench/reader/build_set.py first")
    print(f"reading sheet: http://127.0.0.1:{a.port}/reader.html   (answers -> {HERE / 'readings'}/<reader_id>.csv; Ctrl-C to stop)")
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
