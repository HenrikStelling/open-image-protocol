"""Run OIP-Bench. Usage:
  python bench/run.py --dataset vindr --n 50 --models claude,gpt,gemini --conditions raw,ctx,annot [--dry-run]
Raw replies and scores go to bench/results/<timestamp>/. Model ids are pinned in MODELS; keys from env."""
from __future__ import annotations
import argparse, base64, json, os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "bench")); sys.path.insert(0, str(ROOT / "src"))
from tasks import build, vindr_labels
from score import score

MODELS = {"claude": ("anthropic", "claude-sonnet-5"), "gpt": ("openai", "gpt-5.2"), "gemini": ("google", "gemini-3.1-flash")}
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
    else:
        raise KeyError(condition)
    return text, images


def _downscale(png: bytes, max_side: int = 1568) -> bytes:
    from PIL import Image; import io
    im = Image.open(io.BytesIO(png))
    if max(im.size) <= max_side: return png
    im.thumbnail((max_side, max_side)); b = io.BytesIO(); im.save(b, format="PNG"); return b.getvalue()


def call(provider: str, model: str, text: str, images: list[tuple[str, bytes]]) -> str:
    if provider == "anthropic":
        import anthropic
        c = anthropic.Anthropic()
        content = [{"type": "image", "source": {"type": "base64", "media_type": mt, "data": base64.b64encode(_downscale(b)).decode()}} for mt, b in images] + [{"type": "text", "text": text}]
        r = c.messages.create(model=model, max_tokens=300, system=SYSTEM, messages=[{"role": "user", "content": content}])
        return "".join(x.text for x in r.content if getattr(x, "type", "") == "text")
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
    ap.add_argument("--conditions", default="raw,ctx,annot"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--seed", type=int, default=0); a = ap.parse_args()
    labels = vindr_labels() if a.dataset == "vindr" else None
    tasks = build(ROOT / "data/oip" / a.dataset, a.n, a.seed, labels)
    run = ROOT / "bench/results" / time.strftime("%Y%m%d-%H%M%S"); run.mkdir(parents=True, exist_ok=True)
    (run / "tasks.json").write_text(json.dumps(tasks, indent=1))
    conds = a.conditions.split(","); models = a.models.split(",")
    if a.dry_run:
        chars = {c: sum(len(build_prompt(t, c)[0]) for t in tasks) for c in conds}
        print(json.dumps({"tasks": len(tasks), "by_type": {t: sum(1 for x in tasks if x["type"] == t) for t in sorted({x["type"] for x in tasks})}, "calls_per_model": len(tasks) * len(conds),
                          "approx_text_tokens_per_condition": {c: v // 4 for c, v in chars.items()}, "models": {m: MODELS[m] for m in models}, "run_dir": str(run)}, indent=1)); return
    rows = []
    for m in models:
        prov, mid = MODELS[m]
        for c in conds:
            for i, t in enumerate(tasks, 1):
                text, imgs = build_prompt(t, c)
                try:
                    reply = call(prov, mid, text, imgs); err = None
                except Exception as e:
                    reply, err = "", f"{type(e).__name__}: {str(e)[:200]}"
                rows.append({"model": m, "model_id": mid, "condition": c, "task": t["id"], "type": t["type"], "gating": t["gating"], "reply": reply, "error": err, "score": score(t, reply) if not err else {}})
                if i % 20 == 0: print(f"  {m}/{c}: {i}/{len(tasks)}", flush=True)
            (run / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    print("done ->", run)


if __name__ == "__main__":
    main()
