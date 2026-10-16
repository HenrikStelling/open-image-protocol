## Readings (2026-10-16)

1. **No runtime effect.** Under Ollama 0.40.1 the two daemon settings (Metal tensor kernels disabled by `GGML_METAL_TENSOR_DISABLE=1`,
   the workaround set on 2026-09-08 for a kernel bug on this M5, vs. the default) give the same results on every cell for both
   local models: all file-bearing cells identical (100 % / 100 % / 100 % / 50 % flip check), and the image-only cells within
   noise once the three repeats are pooled (e4b left edge 51 vs 43 %, CTR 49 vs 49 %; MedGemma left edge 12 vs 12 %, CTR 53 vs
   52 %). The one repeat-0 contrast that looked like an effect (e4b raw left edge 64 vs 38 %, p = 0.015) is sampling noise:
   e4b's image-only left-edge answers are the least stable cell of the set (identical score on 82–84 % of items only), and the
   pooled figures sit 8 pp apart with overlapping intervals.
2. **The workaround is no longer needed.** No empty, garbled or cut-off replies under either setting (0 of 2,928 per model);
   the bug the variable worked around (garbage output from the tensor kernels on 0.33) is gone in 0.40.1. The default setting
   is slightly faster (e4b median 0.3 vs 0.4 s per call).
3. **Stability is a property of the model, not the runtime:** identical score on all three replies for 84 / 82 % of items
   (e4b) and 86 / 85 % (MedGemma) under the two settings.
4. **Consequences.** The Metal variable is dropped (`launchctl unsetenv`, bench README updated); future local runs use the
   daemon default and record `ollama_env` and `ollama_version` in `run_meta.json`. The optional second runtime (oMLX,
   MLX-format weights) stays an open PLAN item: it would test a different quantisation, not a kernel switch, and is only
   worth running if a local model is to be reported on two runtimes in the paper.
