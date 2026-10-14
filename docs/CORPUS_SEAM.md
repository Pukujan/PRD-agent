# The corpus and retrieval seam

Status: documented, not built. Nothing in this file exists yet.

## What is built today

Every finished story is appended to `evals/story_evals.json` in the marketingskills eval shape
(`prompt`, `expected_output`, `assertions`). The next run reads that file, scores each past
prompt against the current positioning by shared content words, and passes the top two into
`story.build_story_prompt` as worked examples. See `src/prd_agent/evals.py`.

That is the whole of retrieval: deterministic keyword overlap over one small JSON file. It has
no dependency, no index and no model call, and it is honest about being a floor. A run whose
positioning shares no content words with any past story retrieves nothing and falls back to the
template prompt.

## What is not built

1. **A scraped trend corpus.** `trends.analyze` searches the live web on every run and stores
   nothing, so two runs a week apart cannot be compared and a competitor who changes their
   headline is invisible. A corpus would snapshot each search into a dated file and let the
   stage read the delta.
2. **Semantic retrieval over past stories.** Keyword overlap misses a past story about a
   different category that solved the same structural problem (a jaded market that needed a new
   mechanism, say). Embedding the positioning and the past prompts would catch it.
3. **Cross-run positioning memory.** Nothing records which differentiators passed the swap test
   before, so the same losing line can be proposed twice.

## Why not built now

The project ships zero runtime dependencies, and both a corpus store and embeddings need one.
The eval file is also small enough that keyword overlap has not yet been observed to fail: the
first run has no exemplars at all.

## The trigger to build it

Build the corpus when any of these is observed, not before:

- `evals/story_evals.json` passes 50 records, or the file passes 200 KB.
- Three consecutive runs retrieve zero-score exemplars while past stories exist.
- A second artifact from a different category is run and the retrieved exemplars are visibly
  wrong for it.

## The seam, so the change stays local

`evals.select_exemplars(evals: dict, *, positioning: dict, limit: int = 2) -> list[dict]` is the
only function that reads the corpus. A corpus-backed implementation keeps that signature and
returns the same `{"id", "score", "story"}` records, so `pipeline.run` and
`story.build_story_prompt` do not change. A corpus writer would be a new function alongside
`evals.append_eval`, called from the same place in `pipeline.run`.

## Acceptance criteria for building it

- The retrieved exemplars for a known positioning are better than keyword overlap's, judged by
  the owner on at least three artifacts, and the keyword results are kept as the control.
- Retrieval stays out of the model's verdict path: no exemplar selection is decided by a model.
- The dependency count stays zero, or the new dependency is justified in the PR against this
  file's "why not built now" section.
