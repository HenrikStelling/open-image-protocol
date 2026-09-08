"""Re-apply bench/score.py to stored replies (scorer fixes must not require re-running models). Usage: python bench/rescore.py [run_dir ...]"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "bench"))
from score import score
runs = [Path(p) for p in sys.argv[1:]] or sorted(p for p in (ROOT / "bench/results").glob("*") if (p / "results.jsonl").exists())
for r in runs:
    tasks = {t["id"]: t for t in json.loads((r / "tasks.json").read_text())}
    rows = [json.loads(l) for l in (r / "results.jsonl").read_text().splitlines() if l.strip()]
    changed = 0
    for x in rows:
        if x.get("error") or x["task"] not in tasks: continue
        new = score(tasks[x["task"]], x["reply"])
        if new != x["score"]: changed += 1; x["score"] = new
    (r / "results.jsonl").write_text("\n".join(json.dumps(x) for x in rows) + "\n"); print(f"{r.name[:60]}: {changed} scores changed")
