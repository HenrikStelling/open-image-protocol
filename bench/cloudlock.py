"""One Ollama cloud model at a time, across every lane and every session (Ollama Pro policy, PLAN Phase 3).

`acquire()` takes an exclusive flock on ~/.config/oip/ollama-cloud.lock and blocks, polling every `poll` seconds, while
another process holds it; the holder's pid, model and start time are written into the file so a waiting runner can say who
it waits for. The lock is released when the holding process exits, including on kill. Local models never take it.
"""
from __future__ import annotations
import fcntl, json, os, time
from pathlib import Path

LOCK = Path(os.environ.get("OIP_CLOUD_LOCK", str(Path.home() / ".config/oip/ollama-cloud.lock")))


def is_cloud(model: str) -> bool:
    return model.startswith("ollama/") and ("cloud" in model.split("/", 1)[1])


def acquire(model: str, poll: int = 60, log=print):
    """Return an open file object holding the exclusive lock; keep it referenced for the lifetime of the run."""
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    f = open(LOCK, "a+")
    waited = 0
    while True:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except OSError:
            f.seek(0); holder = f.read().strip()
            if waited % (poll * 10) == 0:
                log(f"cloud lock held by {holder or 'another process'}; waiting ({waited // 60} min)")
            time.sleep(poll); waited += poll
    f.seek(0); f.truncate()
    f.write(json.dumps({"pid": os.getpid(), "model": model, "started": time.strftime("%Y-%m-%dT%H:%M:%S")})); f.flush()
    return f


def release(f) -> None:
    try:
        f.seek(0); f.truncate(); f.flush()
        fcntl.flock(f, fcntl.LOCK_UN); f.close()
    except Exception:   # noqa: BLE001
        pass
