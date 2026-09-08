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


def build_prompt(task: dict, condition: str) -> tuple[str, list[tuple[str, bytes]]]:
    pkg = Path(task["pkg"]); images = []
    if condition == "raw":
        images.append(("image/png", (pkg / "renders/canonical.png").read_bytes())); text = task["question"]
    elif condition == "ctx":
        images.append(("image/png", (pkg / "renders/canonical.png").read_bytes()))
        text = "Reference file for the attached image (OIP context.md):\n\n" + (pkg / "context.md").read_text() + "\n\nQuestion: " + task["question"]
    elif condition == "annot":
        images.append(("image/png", (pkg / "renders/annotated.png").read_bytes()))
        text = "Reference file for the attached (annotated) image (OIP context.md):\n\n" + (pkg / "context.md").read_text() + "\n\nQuestion: " + task["question"]
    elif condition in ("misled_plain", "misled_oip"):
        # misleading text: plain = bare sentence (how reports are pasted today); oip = inside context.md's External section with the
        # 'external, verify against the pixels' label. The difference between the two adoption rates is the protocol's contribution.
        images.append(("image/png", (pkg / "renders/canonical.png").read_bytes())); wrong = task.get("misleading_label", "Cardiomegaly")
        if condition == "misled_plain":
            text = f"Prior report note: {wrong}.\n\nQuestion: " + task["question"]
        else:
            ctx = (pkg / "context.md").read_text().replace("## Unknowns and cautions", f"- Dataset labels [external — verify against the pixels]: {wrong}\n\n## Unknowns and cautions", 1)
            text = "Reference file for the attached image (OIP context.md):\n\n" + ctx + "\n\nQuestion: " + task["question"]
    else:
        raise KeyError(condition)
    return text, images


def _downscale(png: bytes, max_side: int = 1568) -> bytes:
    from PIL import Image; import io
    im = Image.open(io.BytesIO(png))
    if max(im.size) <= max_side: return png
    im.thumbnail((max_side, max_side)); b = io.BytesIO(); im.save(b, format="PNG"); return b.getvalue()


def call(provider: str, model: str, text: str, images: list[tuple[str, bytes]]) -> str:
    if provider == "ollama":
        # Local daemon (http://localhost:11434 by default); ':cloud' / '-cloud' tags are routed to Ollama Cloud through the
        # signed-in account, so no API key is needed. Native /api/chat with base64 images. OLLAMA_HOST overrides the base URL.
        import urllib.request
        base = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        if not base.startswith("http"): base = "http://" + base
        # reasoning models spend the output budget inside 'thinking'; keep it generous and let --ollama-think decide
        body = {"model": model, "stream": False, "think": OLLAMA_THINK, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text, "images": [base64.b64encode(_downscale(b)).decode() for _, b in images]}],
                "options": {"num_predict": 1200 if OLLAMA_THINK else 400}}
        req = urllib.request.Request(base + "/api/chat", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)["message"]["content"]
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
        return r.output_text
    if provider == "google":
        from google import genai
        from google.genai import types
        c = genai.Client(api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
        parts = [types.Part.from_bytes(data=_downscale(b), mime_type=mt) for mt, b in images] + [text]
        r = c.models.generate_content(model=model, contents=parts, config=types.GenerateContentConfig(system_instruction=SYSTEM, max_output_tokens=300))
        return r.text or ""
    raise KeyError(provider)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dataset", default="vindr"); ap.add_argument("--n", type=int, default=50); ap.add_argument("--models", default="claude,gpt,gemini")
    ap.add_argument("--conditions", default="raw,ctx,annot,misled_plain,misled_oip"); ap.add_argument("--ollama-think", action="store_true", help="let Ollama reasoning models think (slower; default off)"); ap.add_argument("--gpt-model"); ap.add_argument("--gemini-model"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--seed", type=int, default=0); a = ap.parse_args()
    if a.gpt_model: MODELS["gpt"] = ("openai", a.gpt_model)
    if a.gemini_model: MODELS["gemini"] = ("google", a.gemini_model)
    global OLLAMA_THINK; OLLAMA_THINK = a.ollama_think
    labels = vindr_labels() if a.dataset == "vindr" else None
    tasks = build(ROOT / "data/oip" / a.dataset, a.n, a.seed, labels)
    run = ROOT / "bench/results" / time.strftime("%Y%m%d-%H%M%S"); run.mkdir(parents=True, exist_ok=True)
    (run / "tasks.json").write_text(json.dumps(tasks, indent=1))
    conds = a.conditions.split(","); models = a.models.split(",")
    if a.dry_run:
        chars = {c: sum(len(build_prompt(t, c)[0]) for t in tasks if (c.startswith("misled")) == (t["type"] == "findings_misled")) for c in conds}
        applies = lambda t, c: (c.startswith("misled")) == (t["type"] == "findings_misled")
        n_calls = sum(1 for c in conds for t in tasks if applies(t, c))
        in_tok = sum(v // 4 for v in chars.values()) + IMAGE_TOKENS * n_calls; out_tok = 400 * n_calls   # ~400 output incl. thinking
        cost = {m: (round(in_tok / 1e6 * PRICES[m][0] + out_tok / 1e6 * PRICES[m][1], 2) if m in PRICES else "ollama plan allowance") for m in models}
        print(json.dumps({"tasks": len(tasks), "by_type": {t: sum(1 for x in tasks if x["type"] == t) for t in sorted({x["type"] for x in tasks})}, "calls_per_model": n_calls,
                          "approx_text_tokens_per_condition": {c: v // 4 for c, v in chars.items()}, "approx_input_tokens_per_model": in_tok, "approx_output_tokens_per_model": out_tok,
                          "approx_cost_usd_per_model": cost, "models": {m: (MODELS[m] if m in MODELS else ("ollama", m.split("/", 1)[1])) for m in models}, "run_dir": str(run)}, indent=1)); return
    rows = []
    for m in models:
        prov, mid = MODELS[m] if m in MODELS else (("ollama", m.split("/", 1)[1]) if m.startswith("ollama/") else (_ for _ in ()).throw(KeyError(f"unknown model {m}; use a key in MODELS or ollama/<tag>")))
        for c in conds:
            for i, t in enumerate(tasks, 1):
                if (c.startswith("misled")) != (t["type"] == "findings_misled"):
                    continue
                text, imgs = build_prompt(t, c)
                try:
                    reply = call(prov, mid, text, imgs); err = None
                except Exception as e:
                    reply, err = "", f"{type(e).__name__}: {str(e)[:200]}"
                rows.append({"model": m, "model_id": mid, "provider": prov, "condition": c, "task": t["id"], "type": t["type"], "gating": t["gating"], "reply": reply, "error": err, "score": score(t, reply) if not err else {}})
                if i % 20 == 0: print(f"  {m}/{c}: {i}/{len(tasks)}", flush=True)
            (run / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    print("done ->", run)


if __name__ == "__main__":
    main()
