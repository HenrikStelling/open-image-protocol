"""Run OIP-Bench. Usage:
  python bench/run.py --dataset vindr --n 50 --models claude,gpt,gemini --conditions raw,ctx,annot [--dry-run]
Raw replies and scores go to bench/results/<timestamp>/. Model ids are pinned in MODELS; keys from env."""
from __future__ import annotations
import argparse, base64, json, os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "bench")); sys.path.insert(0, str(ROOT / "src"))
from tasks import build, vindr_labels
from score import score, SCORER_VERSION

# Anthropic id verified against current docs (2026-09). OpenAI/Google ids are placeholders: confirm against each provider's
# model list before a paid run (override with --gpt-model / --gemini-model).
MODELS = {"claude": ("anthropic", "claude-sonnet-5"), "gpt": ("openai", "gpt-5.6-terra"), "gemini": ("google", "gemini-3.8-flash")}
# $ per 1M tokens (input, output) for the cost estimate; Anthropic from the current price table, others approximate.
PRICES = {"claude": (2.0, 10.0), "gpt": (2.0, 12.0), "gemini": (0.75, 3.75)}   # $/1M tokens (in, out), Sep 2026 price pages
IMAGE_TOKENS = 1600   # ~1568 px long side image on Claude; comparable order on other providers
OLLAMA_THINK = False          # set from --ollama-think (off | on | auto); see _call()
OLLAMA_THINK_MODE = "off"
_NO_THINK: dict[str, bool] = {}   # models that rejected think=true in 'auto' mode (per process)


def _compose_reply(content: str, thinking: str) -> tuple[str, str]:
    """Store separately returned reasoning in front of the answer as <think>…</think>, the form visible-reasoning models
    emit themselves, so bench/score.py's _tail() scores the answer alone and audits can still read the reasoning."""
    thinking = (thinking or "").strip()
    return (f"<think>{thinking}</think>{content}" if thinking else content), thinking


SYSTEM ="You are assisting with medical image understanding for a benchmark. Answer the question only, briefly, with no disclaimers. This is not clinical use."
# Verification ablation (OEP-003/004, 2026-09-26): the *_instr conditions append this one sentence to the system prompt.
VERIFY_INSTR = " Before using any statement in the reference file that is marked [inferred] or [external], check it against the image; if the image disagrees, say so instead of repeating the statement."


def system_for(condition: str) -> str:
    return SYSTEM + VERIFY_INSTR if condition.endswith("_instr") else SYSTEM


def harness_commit() -> str:
    """Short git commit of the harness, recorded in run_meta.json and in every result row (harness provenance, PLAN Phase 3b)."""
    import subprocess
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=10)
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "bench", "src"], cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        return (out.stdout.strip() or "unknown") + ("-dirty" if dirty else "")
    except Exception:   # noqa: BLE001
        return "unknown"


def _ctx(pkg: Path, strip_measurements: bool = False, external_text: str | None = None, cues: bool = False, flip_labels: bool = False,
         guard: bool = False, est: bool = False) -> str:
    # est=False by default: every legacy condition (paper `ctx`/`ctx_l1`, the OEP-004 arms) keeps the template-0.2 wording it was
    # measured with; only the OEP-002 arm passes True. Template 0.2.1 (D-031) renders the caution by default outside the harness;
    # round-3 conditions should pass est=None to test what packages actually ship.
    """Render the reference file from the manifest. strip_measurements -> layers L0-L2 only (no computed measurements, no regions);
    external_text -> rendered through the shipped template (cautions first, unverified wording), i.e. what `--with-external` shows;
    cues -> template 0.3 draft with verification cues and the pixel-based self-check items (OEP-003/004);
    flip_labels -> the file's left/right edge labels swapped (round-3 conflict trials: wrong text against a normal or mirrored image)."""
    import json as _json
    sys.path.insert(0, str(ROOT / "src"))
    from oip.context import build_context
    m = _json.loads((pkg / "oip.json").read_text())
    if strip_measurements:
        m["derived"] = {"regions": [], "measurements": [], "measurements_file": "derived/measurements.json"}
    if external_text is not None:
        m["external"] = {"dataset": "prior report note", "report_text": external_text}
    if flip_labels:
        el = m["geometry"]["orientation"].get("edge_labels") or {}
        el["left"], el["right"] = el.get("right"), el.get("left")
        for fr in m.get("frames") or []:
            fe = fr.get("edge_labels") or {}
            if fe: fe["left"], fe["right"] = fe.get("right"), fe.get("left")
        m["quality"]["checks"] = [c for c in m["quality"].get("checks", []) if c.get("id") != "orientation_pixel_check"]   # a stale tool verdict would give the swap away
    return build_context(m, include_external=external_text is not None, verification_cues=cues, low_confidence_guard=guard, estimation_caution=est)


CONDITIONS = {
    "raw":          "canonical PNG only",
    "ctx_l1":       "canonical PNG + context.md WITHOUT computed measurements/regions (layers L0-L2: identity, geometry, units, orientation, cautions)",
    "ctx":          "canonical PNG + full context.md (adds L3 regions and L4 measurements)",
    "annot":        "annotated PNG (edge labels, scale bar, region marks) + full context.md",
    "misled_plain": "canonical PNG + a wrong finding as a bare 'Prior report note' (how reports are pasted today)",
    "misled_oip":   "canonical PNG + the same wrong finding delivered through the shipped template (external section after cautions, unverified wording; = `oip describe --with-external`)",
    # verification ablation (OEP-003/004): same tasks as ctx; separate names so the latest-run rule in report.py / paper_stats.py never
    # lets a partial ablation run replace the paper's ctx cells
    "ctx_ctl":      "identical to ctx; same-day within-run control for the verification ablation",
    "ctx_cue":      "canonical PNG + full context.md rendered with verification cues and pixel-based self-check items (template 0.3 draft)",
    "ctx_instr":    "canonical PNG + full context.md (template 0.2) + a one-sentence system instruction to verify [inferred]/[external] statements against the image",
    "ctx_cue_instr": "canonical PNG + cue-bearing context.md + the verify instruction (both)",
    # render probe (2026-09-27, Codex proposal 1 / OEP-005 draft): does a render that survives provider downscaling move the flip check?
    # Flip items show the render built from the MIRRORED canonical while printed labels (and the file) keep the true orientation.
    "annot_ctx":    "annotated render (re-rendered; mirrored pixels for flip items, labels unchanged) + full context.md",
    "annot_only":   "annotated render only, question refers to the printed edge labels (no file)",
    "insp_ctx":     "inspection sheet (1536 px, 96 px R/L badges, heart inset, mm ruler) + full context.md",
    "insp_only":    "inspection sheet only, question refers to the printed edge labels (no file)",
    # OEP-002 ablation (2026-09-29): low-confidence spacing. Same-day controls plus the L0-L2 file with the guard wording (a) and with
    # the guard plus the estimation caution (b); NIH-50, tasks ctr / heart_mm / left_edge
    "raw_ctl":      "identical to raw; same-day control for the OEP-002 ablation",
    "ctx_l1_ctl":   "identical to ctx_l1; same-day control for the OEP-002 ablation",
    "ctx_l1_oep2":  "canonical PNG + L0-L2 file with the OEP-002 low-confidence-scale guard (do not derive mm from a low-confidence spacing)",
    "ctx_l1_oep2e": "canonical PNG + L0-L2 file with the OEP-002 guard and the estimation caution (judge unlisted quantities visually, not from self-estimated pixel coordinates)",
}
RENDER_CACHE = ROOT / "bench/results/_render_cache"   # bench artefacts live outside the packages (git-ignored with results/)


def _variant(pkg: Path, kind: str, flipped: bool) -> bytes:
    """Annotated render or inspection sheet re-rendered from the canonical pixels (mirrored for flip items) with the manifest's
    edge labels; region marks / the heart inset follow the mirroring. Cached under bench/results/_render_cache/<pkg>/."""
    f = RENDER_CACHE / pkg.name / f"{kind}{'_flipped' if flipped else ''}.png"
    if f.exists():
        return f.read_bytes()
    import numpy as np
    from PIL import Image
    from oip.render import annotated, inspection_sheet
    m = json.loads((pkg / "oip.json").read_text()); g = m["geometry"]; el = g["orientation"].get("edge_labels") or {}
    canon = np.asarray(Image.open(pkg / "renders/canonical.png").convert("L"))
    if flipped:
        canon = canon[:, ::-1]
    w = canon.shape[1]; regs = (m.get("derived") or {}).get("regions") or []
    mb = (lambda b: [b[0], w - 1 - b[3], b[2], w - 1 - b[1]]) if flipped else (lambda b: b)
    if kind == "annot":
        marks = [dict(r, bbox_px=mb(r["bbox_px"])) for r in regs if r.get("bbox_px") and r.get("mark")]
        im, _ = annotated(canon, el, g["pixel_spacing_mm"], f"{m['identity']['title']} · OIP {m['oip']['version']}", marks=marks)
    else:
        heart = next((r for r in regs if r["id"] == "heart" and r.get("bbox_px")), None)
        im, _ = inspection_sheet(canon, el, g["pixel_spacing_mm"], mb(heart["bbox_px"]) if heart else None)
    f.parent.mkdir(parents=True, exist_ok=True); im.save(f)
    return f.read_bytes()
DEFAULT_CONDITIONS = "raw,ctx_l1,ctx,annot,misled_plain,misled_oip"
BASE_CONDITION = {"ctx_ctl": "ctx", "ctx_cue": "ctx", "ctx_instr": "ctx", "ctx_cue_instr": "ctx",
                  "raw_ctl": "raw", "ctx_l1_ctl": "ctx_l1", "ctx_l1_oep2": "ctx_l1", "ctx_l1_oep2e": "ctx_l1"}   # task applicability follows the base


def applies(task: dict, condition: str) -> bool:
    """Which conditions a task runs in: misled_* only for findings_misled; tasks with an explicit 'conditions' list only there.
    Ablation conditions apply wherever their base condition applies."""
    condition = BASE_CONDITION.get(condition, condition)
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
    if condition in ("raw", "raw_ctl"):
        return q, [canon]
    fl = bool(task.get("text_flipped"))   # round-3 conflict trials: the file's edge labels swapped
    if condition in ("ctx_l1", "ctx_l1_ctl"):
        return "Reference file for the attached image (OIP context.md):\n\n" + _ctx(pkg, strip_measurements=True, flip_labels=fl) + "\n\nQuestion: " + q, [canon]
    if condition in ("ctx_l1_oep2", "ctx_l1_oep2e"):
        return "Reference file for the attached image (OIP context.md):\n\n" + _ctx(pkg, strip_measurements=True, flip_labels=fl, guard=True, est=condition.endswith("e")) + "\n\nQuestion: " + q, [canon]
    if condition in ("ctx", "ctx_ctl", "ctx_instr"):
        return "Reference file for the attached image (OIP context.md):\n\n" + _ctx(pkg, flip_labels=fl) + "\n\nQuestion: " + q, [canon]   # rendered from the manifest with the current template
    if condition in ("ctx_cue", "ctx_cue_instr"):
        return "Reference file for the attached image (OIP context.md):\n\n" + _ctx(pkg, cues=True, flip_labels=fl) + "\n\nQuestion: " + q, [canon]
    if condition == "annot":
        return "Reference file for the attached (annotated) image (OIP context.md):\n\n" + _ctx(pkg, flip_labels=fl) + "\n\nQuestion: " + q, [("image/png", (pkg / "renders/annotated.png").read_bytes())]
    if condition in ("annot_ctx", "annot_only", "insp_ctx", "insp_only"):
        kind = "annot" if condition.startswith("annot") else "insp"
        img = ("image/png", _variant(pkg, kind, bool(task.get("flipped"))))
        if condition.endswith("_only"):
            return "Question: " + task.get("question_labels", q), [img]
        return "Reference file for the attached image (OIP context.md):\n\n" + _ctx(pkg, flip_labels=fl) + "\n\nQuestion: " + q, [img]
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


def call(provider: str, model: str, text: str, images: list[tuple[str, bytes]], system: str = SYSTEM) -> tuple[str, dict]:
    """Returns (reply_text, usage); transient transport/server failures on the API providers are retried with back-off."""
    if provider == "ollama":
        return _call(provider, model, text, images, system)
    last = None
    for attempt in range(5):
        try:
            return _call(provider, model, text, images, system)
        except Exception as e:                     # noqa: BLE001
            msg = f"{type(e).__name__}: {e}"
            if not any(k in msg for k in ("503", "502", "504", "429", "500", "overloaded", "Broken pipe", "disconnected", "timed out", "Timeout", "ReadError", "ConnectError", "Connection error", "APIConnectionError")):
                raise
            last = e; time.sleep([5, 15, 45, 135, 300][min(attempt, 4)])
    raise last


def _call(provider: str, model: str, text: str, images: list[tuple[str, bytes]], system: str = SYSTEM) -> tuple[str, dict]:
    """Single provider call. usage = {input_tokens, output_tokens, latency_s} where the provider reports them."""
    if provider == "ollama":
        # Local daemon (http://localhost:11434 by default); ':cloud' / '-cloud' tags are routed to Ollama Cloud through the
        # signed-in account, so no API key is needed. Native /api/chat with base64 images. OLLAMA_HOST overrides the base URL.
        import urllib.request
        base = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        if not base.startswith("http"): base = "http://" + base
        # Thinking (2026-09-29, OEP-002 readout): with think=false, glm-5.3-flash still reasons inside `content` and closes it
        # with </think>; at num_predict 800 that reasoning is cut off before the answer in up to 57/82 replies of a cell
        # (paper runs, L0-L2 heart width). With think=true the daemon returns the reasoning in message.thinking and the
        # answer alone in content. --ollama-think on|auto turns that on ('auto' falls back to think=false for models that
        # reject the field); the reply is then stored as "<think>…</think>" + answer so the scorer's _tail() rule applies
        # unchanged, and usage records done_reason ("length" = output cap reached), num_predict and thinking_chars.
        think = OLLAMA_THINK and not _NO_THINK.get(model, False)
        body = {"model": model, "stream": False, "think": think, "messages": [{"role": "system", "content": system}, {"role": "user", "content": text, "images": [base64.b64encode(_downscale(b)).decode() for _, b in images]}],
                "options": {"num_predict": 1600 if think else 800}}
        req = urllib.request.Request(base + "/api/chat", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        last = None
        for attempt in range(5):                       # cloud 502s/timeouts are transient; back off 5/15/45/135 s
            try:
                t0 = time.time()
                with urllib.request.urlopen(req, timeout=180) as r:
                    d = json.load(r)
                    reply, thinking = _compose_reply(d["message"].get("content") or "", d["message"].get("thinking") or "")
                    return reply, {"input_tokens": d.get("prompt_eval_count"), "output_tokens": d.get("eval_count"), "latency_s": round(time.time() - t0, 2),
                                   "done_reason": d.get("done_reason"), "think": think, "num_predict": body["options"]["num_predict"], "thinking_chars": len(thinking)}
            except Exception as e:                     # noqa: BLE001
                last = e
                msg = str(e)
                if think and OLLAMA_THINK_MODE == "auto" and "400" in msg:
                    # the daemon answers HTTP 400 for models without the thinking capability: remember it and retry without
                    _NO_THINK[model] = True
                    return _call(provider, model, text, images, system)
                if not ("timed out" in msg or "502" in msg or "503" in msg or "504" in msg or "429" in msg):
                    raise
                time.sleep([5, 15, 45, 135, 300][min(attempt, 4)])   # sporadic failures cost seconds; sustained ones escalate
        raise last
    if provider == "anthropic":
        import anthropic
        c = anthropic.Anthropic()   # credentials: ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile
        # Prompt caching: the image and the reference file are identical across the ~12 questions per package, so they are
        # marked as cache breakpoints and only the question is billed at full price after the first call (5-min TTL).
        content = [{"type": "image", "source": {"type": "base64", "media_type": mt, "data": base64.standard_b64encode(_downscale(b)).decode("utf-8")}, "cache_control": {"type": "ephemeral"}} for mt, b in images]
        head, sep, q = text.rpartition("\n\nQuestion: ")
        if sep:
            content += [{"type": "text", "text": head + sep, "cache_control": {"type": "ephemeral"}}, {"type": "text", "text": q}]
        else:
            content.append({"type": "text", "text": text})
        # Adaptive thinking is on by default on claude-opus-5; low effort suits short factual answers. max_tokens must leave
        # room for thinking tokens. No server-side fallbacks on purpose: a benchmark must not silently swap models.
        r = c.messages.create(model=model, max_tokens=4000, system=system, output_config={"effort": "low"},
                              messages=[{"role": "user", "content": content}])
        if r.stop_reason == "refusal":
            cat = r.stop_details.category if r.stop_details else None
            return f"[refusal:{cat}]", {}
        u = r.usage
        return "".join(x.text for x in r.content if x.type == "text"), {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None), "latency_s": None,
                                                                        "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", None), "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", None)}
    if provider == "openai":
        from openai import OpenAI
        c = OpenAI()
        content = [{"type": "input_image", "image_url": f"data:{mt};base64,{base64.b64encode(_downscale(b)).decode()}"} for mt, b in images] + [{"type": "input_text", "text": text}]
        r = c.responses.create(model=model, instructions=system, input=[{"role": "user", "content": content}], max_output_tokens=600,
                               reasoning={"effort": "low"})   # reasoning tokens bill as output and eat the budget; low suits short factual answers
        return r.output_text, {"input_tokens": getattr(getattr(r, "usage", None), "input_tokens", None), "output_tokens": getattr(getattr(r, "usage", None), "output_tokens", None), "latency_s": None}
    if provider == "google":
        from google import genai
        from google.genai import types
        c = genai.Client(api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
        parts = [types.Part.from_bytes(data=_downscale(b), mime_type=mt) for mt, b in images] + [text]
        r = c.models.generate_content(model=model, contents=parts, config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=600,
                                                                                            thinking_config=types.ThinkingConfig(thinking_level="low")))   # Gemini 3.x thinks by default; low keeps the answer inside the output budget
        um = getattr(r, "usage_metadata", None)
        return (r.text or ""), {"input_tokens": getattr(um, "prompt_token_count", None), "output_tokens": getattr(um, "candidates_token_count", None), "latency_s": None}
    raise KeyError(provider)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dataset", default="vindr"); ap.add_argument("--n", type=int, default=50); ap.add_argument("--models", default="claude,gpt,gemini")
    ap.add_argument("--resume", help="existing run dir: reuse tasks.json, skip rows already done"); ap.add_argument("--pkg-dir", help="directory of .oip packages (default data/oip/<dataset>); use a copy outside iCloud-synced folders"); ap.add_argument("--conditions", default=DEFAULT_CONDITIONS, help="; ".join(f"{k} = {v}" for k, v in CONDITIONS.items())); ap.add_argument("--ollama-think", nargs="?", const="on", default="off", choices=["off", "on", "auto"], help="Ollama think field: off (default; glm then reasons inside content and can hit the 800-token cap), on (think=true, num_predict 1600, reasoning stored as <think>…</think>), auto (on, per-model fallback when the daemon rejects it)"); ap.add_argument("--gpt-model"); ap.add_argument("--gemini-model"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tasks", help="comma-separated task types to keep (e.g. flip_check,left_edge); default: all built tasks")
    ap.add_argument("--no-cloud-lock", action="store_true", help="skip the shared one-cloud-model-at-a-time lock (bench/cloudlock.py); only for diagnostics"); a = ap.parse_args()
    if a.gpt_model: MODELS["gpt"] = ("openai", a.gpt_model)
    if a.gemini_model: MODELS["gemini"] = ("google", a.gemini_model)
    global OLLAMA_THINK, OLLAMA_THINK_MODE; OLLAMA_THINK_MODE = a.ollama_think; OLLAMA_THINK = a.ollama_think != "off"
    labels = vindr_labels() if a.dataset == "vindr" else None
    conds = a.conditions.split(","); models = a.models.split(",")
    commit = harness_commit()
    if a.resume:
        run = Path(a.resume); tasks = json.loads((run / "tasks.json").read_text())
        if a.pkg_dir:
            for t in tasks: t["pkg"] = str(Path(a.pkg_dir) / Path(t["pkg"]).name)
    else:
        if a.dataset == "bonescan":
            from tasks_nm import build_nm; tasks = build_nm(Path(a.pkg_dir) if a.pkg_dir else ROOT / "data/oip" / a.dataset, a.n, a.seed)
        else:
            tasks = build(Path(a.pkg_dir) if a.pkg_dir else ROOT / "data/oip" / a.dataset, a.n, a.seed, labels)
        if a.tasks:
            keep = set(a.tasks.split(",")); tasks = [t for t in tasks if t["type"] in keep]
        tag = "+".join(m.replace("/", "_").replace(":", "_") for m in a.models.split(","))[:60]
        run = ROOT / "bench/results" / f"{time.strftime('%Y%m%d-%H%M%S')}-{tag}-{os.getpid()}"   # unique per process
        if not a.dry_run:   # a dry run must not leave a results directory behind (report.py would read it)
            run.mkdir(parents=True, exist_ok=True)
            (run / "tasks.json").write_text(json.dumps(tasks, indent=1))
            (run / "run_meta.json").write_text(json.dumps({"harness_commit": commit, "scorer": SCORER_VERSION, "dataset": a.dataset, "pkg_dir": a.pkg_dir,
                                                           "n": a.n, "seed": a.seed, "models": models, "model_ids": {m: MODELS.get(m) for m in models}, "conditions": conds,
                                                           "tasks_filter": a.tasks, "system_prompt": SYSTEM, "verify_instruction": VERIFY_INSTR if any(c.endswith("_instr") for c in conds) else None,
                                                           "ollama_think": OLLAMA_THINK_MODE, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "argv": sys.argv[1:]}, indent=1))
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
    from cloudlock import acquire as _lock_acquire, release as _lock_release, is_cloud as _is_cloud
    for m in models:
        prov, mid = MODELS[m] if m in MODELS else (("ollama", m.split("/", 1)[1]) if m.startswith("ollama/") else (_ for _ in ()).throw(KeyError(f"unknown model {m}; use a key in MODELS or ollama/<tag>")))
        # one Ollama cloud model at a time across all lanes and sessions: block here until the shared lock is free (bench/cloudlock.py)
        lock = _lock_acquire(m, log=lambda s: print(f"  {m}: {s}", flush=True)) if _is_cloud(m) and not a.no_cloud_lock else None
        for c in conds:
            for i, t in enumerate(tasks, 1):
                if not applies(t, c) or (m, c, t["id"]) in done:
                    continue
                try:
                    text, imgs = build_prompt(t, c)
                    t_call = time.time(); reply, usage = call(prov, mid, text, imgs, system=system_for(c)); err = None
                    usage = dict(usage or {}); usage["latency_s"] = usage.get("latency_s") or round(time.time() - t_call, 2)
                except Exception as e:
                    reply, err, usage = "", f"{type(e).__name__}: {str(e)[:200]}", {}
                rows.append({"model": m, "model_id": mid, "provider": prov, "condition": c, "task": t["id"], "type": t["type"], "gating": t["gating"], "reply": reply, "error": err, "usage": usage,
                             "score": score(t, reply) if not err else {}, "harness_commit": commit, "scorer": SCORER_VERSION})
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
        if lock: _lock_release(lock)
    print("done ->", run)


if __name__ == "__main__":
    main()
