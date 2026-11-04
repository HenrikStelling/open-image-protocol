"""Token-based cost estimate for the confirmatory round, from measured usage of the exploratory runs.

Per-call usage per (model, condition, task) is averaged over: repeat subset 2026-10-31/11-02 (raw, ctx, misled_*; 20 images
x 3 replies) and the round-3a repeats 2026-10-02/10-05 (conflict cells on the masked render, condition ctx3_mask).
Confirmatory mix per reply: 80 images x (raw: 4 fact tasks; ctx: 4 fact tasks + 4 conflict cells; misled_plain and
misled_oip: findings), heart_mm only on the 65 calibrated images = 1,090 items.
Prices per million tokens as read from the providers' pricing pages on 2026-11-04 (standard tier).
Anthropic usage: input_tokens excludes cache tokens; cache_creation and cache_read are billed separately.
OpenAI/Google: the harness stored only input/output totals; automatic caching (OpenAI) is not captured, so those are upper bounds.
"""
import json, os, re
from collections import defaultdict
R = "/Users/pal/oip-work/bench/results"
RUNS = ["20261002-065128-gemini-9124", "20261002-065128-gpt-9125", "20261005-143507-claude-95017",
        "20261031-033634-claude-30493", "20261102-063129-gpt-74275", "20261102-071221-gemini-89051",
        "20260930-154432-ollama_gemma4_31b-cloud-30452", "20261005-021730-ollama_minimax-m3_cloud-46588",
        "20260930-175734-ollama_kimi-k3_cloud-66601", "20261005-062527-ollama_glm-5.3-flash_cloud-55584",
        "20261005-033312-ollama_mistral-large-3_675b-cloud-53730",
        "20261024-080342-ollama_gemma4_31b-cloud+ollama_glm-5.3-flash_cloud+ollama_ki-46689"]
PK = re.compile(r"^[0-9a-f]{32}\.oip:")
agg = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))  # model -> (cond, task) -> sums
for d in RUNS:
    for line in open(os.path.join(R, d, "results.jsonl")):
        r = json.loads(line)
        u = r.get("usage") or {}
        if not u or r.get("error"):
            continue
        key = (r["condition"], PK.sub("", r["task"]))
        a = agg[r["model"]][key]
        a["n"] += 1
        a["in"] += u.get("input_tokens") or 0
        a["out"] += u.get("output_tokens") or 0
        a["cw"] += u.get("cache_creation_input_tokens") or 0
        a["cr"] += u.get("cache_read_input_tokens") or 0
for m in sorted(agg):
    print("==", m)
    for key in sorted(agg[m]):
        a = agg[m][key]; n = a["n"]
        print(f"  {key[0]:10s} {key[1]:36s} n={int(n):4d}  in={a['in']/n:6.0f}  cache_w={a['cw']/n:6.0f}  "
              f"cache_r={a['cr']/n:6.0f}  out={a['out']/n:5.0f}")

N, NCAL = 80, 65
MIX = {("raw", "left_edge"): N, ("raw", "scale_available"): N, ("raw", "ctr"): N, ("raw", "heart_mm"): NCAL,
       ("ctx", "left_edge"): N, ("ctx", "scale_available"): N, ("ctx", "ctr"): N, ("ctx", "heart_mm"): NCAL,
       ("ctx3_mask", "orient_conflict"): N, ("ctx3_mask", "orient_conflict:flipped"): N,
       ("ctx3_mask", "orient_conflict:textflipped"): N, ("ctx3_mask", "orient_conflict:textflipped:flipped"): N,
       ("misled_plain", "findings_misled"): N, ("misled_oip", "findings_misled"): N}
assert sum(MIX.values()) == 1090
# USD per MTok: input, cache write (5 min), cache read, output
PRICES = {"claude": (2.00, 2.50, 0.20, 10.00), "gpt": (2.00, None, 0.20, 12.00), "gemini": (0.75, None, 0.075, 3.75),
          "ollama/gemma4:31b-cloud": (0.14, None, 0.05, 0.40), "ollama/glm-5.3-flash:cloud": (0.15, None, 0.03, 0.50),
          "ollama/kimi-k3:cloud": (3.00, None, 0.30, 15.00), "ollama/minimax-m3:cloud": (0.60, None, 0.12, 2.40),
          "ollama/mistral-large-3:675b-cloud": (0.50, None, 0.50, 1.50)}
BATCH = {"claude": (1.00, 1.25, 0.10, 5.00), "gpt": (1.00, None, 0.10, 6.00), "gemini": (0.375, None, 0.0375, 1.875)}
print("\nitems per reply:", sum(MIX.values()))
TOTAL = [0.0, 0.0]
for m in PRICES:
    t = defaultdict(float)
    for key, k in MIX.items():
        a = agg[m][key]; n = a["n"]
        assert n > 0, (m, key)
        for f in ("in", "out", "cw", "cr"):
            t[f] += k * a[f] / n
    def cost(p):
        pi, pw, pr, po = p
        return (t["in"] * pi + t["cw"] * (pw or 0) + t["cr"] * pr + t["out"] * po) / 1e6
    c = cost(PRICES[m]); TOTAL[0] += c; TOTAL[1] += 3 * c
    b = f", ${cost(BATCH[m]):.2f} batch" if m in BATCH else ""
    print(f"{m:34s} per reply: input {t['in']/1e6:.2f} MTok, cache write {t['cw']/1e6:.2f}, cache read {t['cr']/1e6:.2f}, "
          f"output {t['out']/1e6:.3f} MTok -> ${c:.2f} standard{b}; three replies ${3*c:.2f}")
print(f"TOTAL eight priced lanes: rep 0 ${TOTAL[0]:.2f}, three replies ${TOTAL[1]:.2f}")
