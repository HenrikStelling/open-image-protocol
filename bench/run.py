"""Run OIP-Bench. Usage:
  python bench/run.py --dataset vindr --n 50 --models claude,gpt,gemini --conditions raw,ctx,annot [--dry-run]
Raw replies and scores go to bench/results/<timestamp>/. Model ids are pinned in MODELS; keys from env."""
from __future__ import annotations
import argparse, base64, json, os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "bench")); sys.path.insert(0, str(ROOT / "src"))
from tasks import build, vindr_labels
from score import score

# Anthropic id verified against current docs (2026-09). OpenAI/Google ids are placeholders: confirm against each provider's
# model list before a paid run (override with --gpt-model / --gemini-model).
MODELS = {"claude": ("anthropic", "claude-opus-5"), "gpt": ("openai", "gpt-5.2"), "gemini": ("google", "gemini-3.1-flash")}
# $ per 1M tokens (input, output) for the cost estimate; Anthropic from the current price table, others approximate.
PRICES = {"claude": (5.0, 25.0), "gpt": (2.5, 10.0), "gemini": (0.5, 3.0)}
IMAGE_TOKENS = 1600   # ~1568 px long side image on Claude; comparable order on other providers
OLLAMA_THINK = False
SYSTEM = "You are assisting with medical image understanding for a benchmark. Answer the question only, briefly, with no disclaimers. This is not clinical use."


def _ctx(pkg: Path, strip_measurements: bool = False, external_text: str | None = None) -> str:
    """Render the reference file from the manifest. strip_measurements -> layers L0-L2 only (no computed measurements, no regions);
    external_text -> rendered through the shipped template (cautions first, unverified wording), i.e. what `--with-external` shows."""
    import json as _json
    sys.path.insert(0, str(ROOT / "src"))
    from oip.context import build_context
    m = _json.loads((pkg / "oip.json").read_text())
    if strip_measurements:
        m["derived"] = {"regions": [], "measurements": [], "measurements_file": "derived/measurements.json"}
    if external_text is not None:
        m["external"] = {"dataset": "prior report note", "report_text": external_text}
    return build_context(m, include_external=external_text is not None)


CONDITIONS = {
    "raw":          "canonical PNG only",
    "ctx_l1":       "canonical PNG + context.md WITHOUT computed measurements/regions (layers L0-L2: identity, geometry, units, orientation, cautions)",
    "ctx":          "canonical PNG + full context.md (adds L3 regions and L4 measurements)",
    "annot":        "annotated PNG (edge labels, scale bar, region marks) + full context.md",
    "misled_plain": "canonical PNG + a wrong finding as a bare 'Prior report note' (how reports are pasted today)",
    "misled_oip":   "canonical PNG + the same wrong finding delivered through the shipped template (external section after cautions, unverified wording; = `oip describe --with-external`)",
}
DEFAULT_CONDITIONS = "raw,ctx_l1,ctx,annot,misled_plain,misled_oip"


def applies(task: dict, condition: str) -> bool:
    """Which conditions a task runs in: misled_* only for findings_misled; tasks with an explicit 'conditions' list only there."""
    if condition.startswith("misled") or task["type"] == "findings_misled":
        return condition.startswith("misled") and task["type"] == "findings_misled"
    return condition in task["conditions"] if task.get("conditions") else True


def _flipped(pkg: Path) -> bytes:
    """Horizontally mirrored canonical render (bench artefact, cached next to the package as renders/_flipped.png)."""
    f = pkg / "renders/_flipped.png"
    if not f.exists():
        from PIL import Image, ImageOps
        ImageOps.mirror(Image.open(pkg / "renders/canonical.png")).save(f)
    return f.read_bytes()


def build_prompt(task: dict, condition: str) -> tuple[str, list[tuple[str, bytes]]]:
    pkg = Path(task["pkg"]); canon = ("image/png", _flipped(pkg) if task.get("flipped") else (pkg / "renders/canonical.png").read_bytes())
    q = task["question"]; wrong = task.get("misleading_label", "Cardiomegaly")
    if condition == "raw":
        return q, [canon]
    if condition == "ctx_l1":
        return "Reference file for the attached image (OIP context.md):\n\n" + _ctx(pkg, strip_measurements=True) + "\n\nQuestion: " + q, [canon]
    if condition == "ctx":
        return "Reference file for the attached image (OIP context.md):\n\n" + _ctx(pkg) + "\n\nQuestion: " + q, [canon]   # rendered from the manifest with the current template
    if condition == "annot":
        return "Reference file for the attached (annotated) image (OIP context.md):\n\n" + _ctx(pkg) + "\n\nQuestion: " + q, [("image/png", (pkg / "renders/annotated.png").read_bytes())]
    if condition == "misled_plain":
        return f"Prior report note: {wrong}.\n\nQuestion: " + q, [canon]
    if condition == "misled_oip":
        return "Reference file for the attached image (OIP context.md):\n\n" + _ctx(pkg, external_text=wrong) + "\n\nQuestion: " + q, [canon]
    raise KeyError(f"unknown condition {condition}; known: {', '.join(CONDITIONS)}")


def _downscale(png: bytes, max_side: int = 1568) -> bytes:
    from PIL import Image; import io
    im = Image.open(io.BytesIO(png))
    if max(im.size) <= max_side: return png
    im.thumbnail((max_side, max_side)); b = io.BytesIO(); im.save(b, format="PNG"); return b.getvalue()


def call(provider: str, model: str, text: str, images: list[tuple[str, bytes]]) -> tuple[str, dict]:
    """Returns (reply_text, usage) with usage = {input_tokens, output_tokens, latency_s} where the provider reports them."""
    if provider == "ollama":
        # Local daemon (http://localhost:11434 by default); ':cloud' / '-cloud' tags are routed to Ollama Cloud through the
        # signed-in account, so no API key is needed. Native /api/chat with base64 images. OLLAMA_HOST overrides the base URL.
        import urllib.request
        base = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        if not base.startswith("http"): base = "http://" + base
        # reasoning models spend the output budget inside 'thinking'; keep it generous and let --ollama-think decide
        body = {"model": model, "stream": False, "think": OLLAMA_THINK, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text, "images": [base64.b64encode(_downscale(b)).decode() for _, b in images]}],
                "options": {"num_predict": 1600 if OLLAMA_THINK else 800}}
        req = urllib.request.Request(base + "/api/chat", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        last = None
        for attempt in range(5):                       # cloud 502s/timeouts are transient; back off 5/15/45/135 s
            try:
                t0 = time.time()
                with urllib.request.urlopen(req, timeout=180) as r:
                    d = json.load(r)
                    return d["message"]["content"], {"input_tokens": d.get("prompt_eval_count"), "output_tokens": d.get("eval_count"), "latency_s": round(time.time() - t0, 2)}
            except Exception as e:                     # noqa: BLE001
                last = e
                msg = str(e)
                if not ("timed out" in msg or "502" in msg or "503" in msg or "504" in msg or "429" in msg):
                    raise
                time.sleep([5, 15, 45, 135, 300][min(attempt, 4)])   # sporadic failures cost seconds; sustained ones escalate
        raise last
    if provider == "anthropic":
        import anthropic
        c = anthropic.Anthropic()   # credentials: ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile
        content = [{"type": "image", "source": {"type": "base64", "media_type": mt, "data": base64.standard_b64encode(_downscale(b)).decode("utf-8")}} for mt, b in images] + [{"type": "text", "text": text}]
        # Adaptive thinking is on by default on claude-opus-5; low effort suits short factual answers. max_tokens must leave
        # room for thinking tokens. No server-side fallbacks on purpose: a benchmark must not silently swap models.
        r = c.messages.create(model=model, max_tokens=4000, system=SYSTEM, output_config={"effort": "low"},
                              messages=[{"role": "user", "content": content}])
        if r.stop_reason == "refusal":
            cat = r.stop_details.category if r.stop_details else None
            return f"[refusal:{cat}]"
        return "".join(x.text for x in r.content if x.type == "text")
    if provider == "openai":
        from openai import OpenAI
        c = OpenAI()
        content = [{"type": "input_image", "image_url": f"data:{mt};base64,{base64.b64encode(_downscale(b)).decode()}"} for mt, b in images] + [{"type": "input_text", "text": text}]
        r = c.responses.create(model=model, instructions=SYSTEM, input=[{"role": "user", "content": content}], max_output_tokens=300)
        return r.output_text, {"input_tokens": getattr(getattr(r, "usage", None), "input_tokens", None), "output_tokens": getattr(getattr(r, "usage", None), "output_tokens", None), "latency_s": None}
    if provider == "google":
        from google import genai
        from google.genai import types
        c = genai.Client(api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
        parts = [types.Part.from_bytes(data=_downscale(b), mime_type=mt) for mt, b in images] + [text]
        r = c.models.generate_content(model=model, contents=parts, config=types.GenerateContentConfig(system_instruction=SYSTEM, max_output_tokens=300))
        um = getattr(r, "usage_metadata", None)
        return (r.text or ""), {"input_tokens": getattr(um, "prompt_token_count", None), "output_tokens": getattr(um, "candidates_token_count", None), "latency_s": None}
    raise KeyError(provider)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dataset", default="vindr"); ap.add_argument("--n", type=int, default=50); ap.add_argument("--models", default="claude,gpt,gemini")
    ap.add_argument("--resume", help="existing run dir: reuse tasks.json, skip rows already done"); ap.add_argument("--pkg-dir", help="directory of .oip packages (default data/oip/<dataset>); use a copy outside iCloud-synced folders"); ap.add_argument("--conditions", default=DEFAULT_CONDITIONS, help="; ".join(f"{k} = {v}" for k, v in CONDITIONS.items())); ap.add_argument("--ollama-think", action="store_true", help="let Ollama reasoning models think (slower; default off)"); ap.add_argument("--gpt-model"); ap.add_argument("--gemini-model"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--seed", type=int, default=0); a = ap.parse_args()
    if a.gpt_model: MODELS["gpt"] = ("openai", a.gpt_model)
    if a.gemini_model: MODELS["gemini"] = ("google", a.gemini_model)
    global OLLAMA_THINK; OLLAMA_THINK = a.ollama_think
    labels = vindr_labels() if a.dataset == "vindr" else None
    if a.resume:
        run = Path(a.resume); tasks = json.loads((run / "tasks.json").read_text())
        if a.pkg_dir:
            for t in tasks: t["pkg"] = str(Path(a.pkg_dir) / Path(t["pkg"]).name)
    else:
        if a.dataset == "bonescan":
            from tasks_nm import build_nm; tasks = build_nm(Path(a.pkg_dir) if a.pkg_dir else ROOT / "data/oip" / a.dataset, a.n, a.seed)
        else:
            tasks = build(Path(a.pkg_dir) if a.pkg_dir else ROOT / "data/oip" / a.dataset, a.n, a.seed, labels)
        tag = "+".join(m.replace("/", "_").replace(":", "_") for m in a.models.split(","))[:60]
        run = ROOT / "bench/results" / f"{time.strftime('%Y%m%d-%H%M%S')}-{tag}-{os.getpid()}"; run.mkdir(parents=True, exist_ok=True)   # unique per process
        (run / "tasks.json").write_text(json.dumps(tasks, indent=1))
    conds = a.conditions.split(","); models = a.models.split(",")
    if a.dry_run:
        chars = {c: sum(len(build_prompt(t, c)[0]) for t in tasks if applies(t, c)) for c in conds}
        n_calls = sum(1 for c in conds for t in tasks if applies(t, c))
        in_tok = sum(v // 4 for v in chars.values()) + IMAGE_TOKENS * n_calls; out_tok = 400 * n_calls   # ~400 output incl. thinking
        cost = {m: (round(in_tok / 1e6 * PRICES[m][0] + out_tok / 1e6 * PRICES[m][1], 2) if m in PRICES else "ollama plan allowance") for m in models}
        print(json.dumps({"tasks": len(tasks), "by_type": {t: sum(1 for x in tasks if x["type"] == t) for t in sorted({x["type"] for x in tasks})}, "calls_per_model": n_calls,
                          "approx_text_tokens_per_condition": {c: v // 4 for c, v in chars.items()}, "approx_input_tokens_per_model": in_tok, "approx_output_tokens_per_model": out_tok,
                          "approx_cost_usd_per_model": cost, "models": {m: (MODELS[m] if m in MODELS else ("ollama", m.split("/", 1)[1])) for m in models}, "run_dir": str(run)}, indent=1)); return
    rows = [json.loads(l) for l in (run / "results.jsonl").read_text().splitlines() if l.strip()] if (run / "results.jsonl").exists() else []
    rows = [r for r in rows if not r.get("error")]          # failed rows are retried
    done = {(r["model"], r["condition"], r["task"]) for r in rows if not r.get("error")}   # error rows are retried on resume
    if done: print(f"resuming {run.name}: {len(done)} rows already done", flush=True)
    for m in models:
        prov, mid = MODELS[m] if m in MODELS else (("ollama", m.split("/", 1)[1]) if m.startswith("ollama/") else (_ for _ in ()).throw(KeyError(f"unknown model {m}; use a key in MODELS or ollama/<tag>")))
        for c in conds:
            for i, t in enumerate(tasks, 1):
                if not applies(t, c) or (m, c, t["id"]) in done:
                    continue
                try:
                    text, imgs = build_prompt(t, c)
                    t_call = time.time(); reply, usage = call(prov, mid, text, imgs); err = None
                    usage = dict(usage or {}); usage["latency_s"] = usage.get("latency_s") or round(time.time() - t_call, 2)
                except Exception as e:
                    reply, err, usage = "", f"{type(e).__name__}: {str(e)[:200]}", {}
                rows.append({"model": m, "model_id": mid, "provider": prov, "condition": c, "task": t["id"], "type": t["type"], "gating": t["gating"], "reply": reply, "error": err, "usage": usage, "score": score(t, reply) if not err else {}})
                # abort policy: deterministic client errors (404/410/401/400) after 5 identical in a row;
                # transient server errors / timeouts (5xx, timed out, 429) only after 20 in a row (degraded cloud periods)
                recent = [r["error"] for r in rows[-20:] if r["model"] == m]; last5 = recent[-5:]
                transient = lambda e: any(k in (e or "") for k in ("502", "503", "504", "timed out", "429"))
                if (len(last5) == 5 and all(last5) and len({e[:60] for e in last5}) == 1 and not transient(last5[-1])) or \
                   (len(recent) == 20 and all(recent) and all(transient(e) for e in recent)):
                    (run / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
                    sys.exit(f"ABORT {m}: consecutive errors -> {recent[-1][:160]} (retired tag? auth? degraded cloud? see bench/README.md)")
                if i % 20 == 0: print(f"  {m}/{c}: {i}/{len(tasks)}", flush=True)
                if len(rows) % 10 == 0: (run / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
            (run / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    print("done ->", run)


if __name__ == "__main__":
    main()
