# Confirmatory round: token-priced cost estimate (2026-11-04)

Companion to section 8 of the pre-registration (registered 2026-11-03, https://osf.io/9rxbk). Section 8 gives a bill-based
estimate (about US$27 for the primary data, about $80 for three replies, read from the round-3a and repeat-subset bills).
This note re-derives the figure from the providers' published token prices and the token counts the harness recorded in the
exploratory runs, so the supplement can show the price basis next to the real spend. Nothing here changes the registration.

## 1. Price sources (read 2026-11-04, standard tier, USD per million tokens)

| Provider | Pricing page | Model | Input | Cache write | Cache read | Output |
|---|---|---|---|---|---|---|
| Anthropic | https://platform.claude.com/docs/en/about-claude/pricing (summary at https://claude.com/pricing) | Claude Sonnet 5 | 2.00 | 2.50 (5 min) | 0.20 | 10.00 |
| OpenAI | https://developers.openai.com/api/docs/pricing (redirect target of platform.openai.com/docs/pricing) | gpt-5.6-terra, short context ≤ 272K | 2.00 | — | 0.20 | 12.00 |
| Google | https://aistudio.google.com/docs/pricing (redirect target of ai.google.dev/gemini-api/docs/pricing) | Gemini 3.8 Flash, paid tier | 0.75 | — | 0.075 | 3.75 |
| Ollama cloud | https://ollama.com/pricing | gemma4 (31b not listed separately) | 0.14 | — | 0.05 | 0.40 |
| | | glm-5.3-flash | 0.15 | — | 0.03 | 0.50 |
| | | kimi-k3 | 3.00 | — | 0.30 | 15.00 |
| | | minimax-m3 | 0.60 | — | 0.12 | 2.40 |
| | | mistral-large-3 | 0.50 | — | — | 1.50 |

Notes from the pages: Anthropic's Sonnet 5 price of $2/$10 is the standard price (the announced rise to $3/$15 was
withdrawn); batch API halves input and output for all three API providers (not used: the harness is sequential).
Google's Gemini 3.8 Flash prices double on 2027-01-01 (1.50 / 7.50), after the run window. OpenAI charges 2× for prompts over
272K tokens (never reached; a call here is 2.5–4.1K tokens). Ollama Pro ($20/month) includes $60 of usage credits per month,
consumed at the per-token rates of the table; running models on own hardware (gemma4:e4b, medgemma1.5:4b) is free.

## 2. Measured tokens per call (harness `usage` field, exploratory runs)

Source runs: repeat subset 2026-10-24 to 2026-11-02 (raw, ctx, misled_plain, misled_oip; 20 images × 3 replies) and the
round-3a repeats 2026-09-30 to 2026-10-05 (the four conflict cells on the masked render, condition `ctx3_mask`, 82 images × 3).
Anthropic reports cache writes and reads separately from `input_tokens`; OpenAI, Google and Ollama report input and output
totals only, so automatic caching on those providers is not captured and their figures are upper bounds.

| Model | Image only (raw), input per call | Full file (ctx), input per call | Output per call |
|---|---|---|---|
| claude-sonnet-5 | about 2.7K, almost all cache reads | about 5.0K; first cell of an image a cache write, the rest reads | 4–14 |
| gpt-5.6-terra | 2.5K | 4.0–4.1K | 5–230 (reasoning tokens included; up to 170 on conflict cells) |
| gemini-3.8-flash | 1.1K | 2.7K | 1–6 |
| gemma4:31b (Ollama) | — | 1.4K average over the mix | 3–4 |
| glm-5.3-flash (Ollama) | 2.7K | 3.7–4.2K | up to 1,400 (reasons inside the reply; 8,000-token cap) |
| kimi-k3, minimax-m3, mistral-large-3 (Ollama) | 2.6–2.8K | 3.8–4.2K | 3–9 |

## 3. Estimate for the registered mix

Per reply and model 1,090 items: 80 images × (raw: four fact tasks; ctx: four fact tasks + four conflict cells; misled_plain
and misled_oip: finding list), cardiac width only on the 65 calibrated images. Tokens = items × measured mean per (condition,
task); cost = tokens × price. Script: `scripts/token_cost.py` (the numbers below are its output; it reads the exploratory run directories and does not touch the frozen files).

| Model | Input MTok per reply | Output MTok per reply | Rep 0 (USD) | Three replies (USD) |
|---|---|---|---|---|
| claude-sonnet-5 (0.07 uncached + 1.60 cache write + 2.98 cache read) | 4.65 | 0.007 | 4.81 | 14.43 |
| gpt-5.6-terra | 3.84 | 0.101 | 8.90 | 26.70 |
| gemini-3.8-flash | 2.35 | 0.003 | 1.78 | 5.33 |
| **API lanes** | | | **15.49** | **46.46** |
| gemma4:31b | 1.48 | 0.004 | 0.21 | 0.63 |
| glm-5.3-flash | 4.08 | 1.540 | 1.38 | 4.14 |
| kimi-k3 | 4.15 | 0.018 | 12.71 | 38.14 |
| minimax-m3 | 4.21 | 0.009 | 2.55 | 7.64 |
| mistral-large-3 | 4.08 | 0.005 | 2.05 | 6.14 |
| **Ollama cloud lanes (Pro credits)** | | | **18.90** | **56.69** |
| gemma4:e4b, medgemma1.5:4b (local) | | | 0 | 0 |
| **All ten models** | | | **34.39** | **103.16** |

## 4. Reading

- API lanes: the token-priced estimate (about $15 for rep 0, about $46 for three replies) is below the registered
  bill-based estimate ($27 / $80). The registered figure stays the ceiling for the owner's release; the real spend is read
  from the three consoles after the run and reported next to both.
- The gpt figure is dominated by input tokens (3.8 MTok per reply at $2); its reasoning output adds about $1.20 per reply.
  Claude's cost is the cache writes on the conflict cells (one write per image and render, $2.50 per MTok), not the reads.
- Ollama cloud is not free at the margin: the five cloud models consume about $19 of Pro credits per reply and about
  $57 for three, against $60 of monthly credits. kimi-k3 alone is $12.71 per reply at $3/$15. Three replies of all five
  cloud models in one calendar month will exhaust the Pro allowance unless the run straddles the monthly reset or credits
  are bought; the "one cloud model at a time" rule stays.
- Not in the estimate: refills of transport errors (identical prompt re-sent; a few per cent in the exploratory runs),
  the reserve packages, and provider price changes during the run window (2026-11-04 to 2026-11-21).
