# OIP project rules

## Story file (comprehension debt)

`docs/STORY.md` is the owner's plain-language account of the project: pipeline, tiers, benchmark, scars, status.
It exists so the owner can explain the project to colleagues without re-reading the repository.

Before ending a session that did any of the following, append one story delta to section 7 of `docs/STORY.md`:

- changed what the pipeline does (any module in `src/oip/`, the template, the spec, the schema);
- moved a responsibility between tiers (protocol / implementation / evidence / paper);
- hit a new pitfall, or decided an OEP.

A delta is three sentences, no code: what changed, why, which section of the story it touches. Date it. If the delta
makes a section above it wrong, correct that section in the same session. A new pitfall also gets a bullet in
section 5 under the lesson it belongs to (or a new lesson).

Sessions that only run benchmarks, write reports or edit the paper do not append a delta unless they hit a pitfall.

On request ("teach-back"), the owner explains one section in their own words; compare it with the code and the file,
name what drifted, and fix the file where it was unclear.

## Working copy

Work in `~/oip-work` with `~/oip-venv`. `~/Desktop/OIP` is a stale iCloud clone of the same repository; do not edit it.
