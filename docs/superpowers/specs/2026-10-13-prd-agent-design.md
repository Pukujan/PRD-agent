# PRD-agent — design

**Date:** 2026-10-13
**Status:** approved by owner, pending implementation plan

## 1. The problem

A builder makes things — repositories, tools, protocols, demos — and can explain how
each one works. He cannot easily explain, to a stranger, why it should exist. Turning
his own artifacts into a product story is the missing step.

Generated marketing copy already fails at this in a specific, nameable way. It comes
out reading like an **audit**: an inventory of what the product does, what exists, and
what does not. The owner's words: *"marketing pages contents and stories are coming out
like audits instead of what they are. They need marketing and upsells."*

Two things are settled and are not open questions in this design:

- **Hype is uncapped.** Asked whether the pipeline should refuse anything, the owner
  chose maximum hype: invented-sounding numbers are allowed unless they contradict what
  the artifact actually is. There are no hedging rules, no "don't sell too much"
  guardrails, and no evidence-gating on the output register.
- **The market analysis is input, never output.** What exists and what does not is
  material the agent reads in order to know what to say. It must not appear in the
  reader-facing story.

## 2. What already exists, and what does not

**Adopted, not rebuilt.** `coreyhaines31/marketingskills` (MIT, ~50 skills) is vendored
as a dependency. Its `copywriting` skill already contains:

- The **Human Action Model** spine — current discomfort → better vision → path to
  action. This is the upsell structure.
- The **"Now you can…" test** and the **swap test** ("if the line would work unchanged
  on a competitor's site, rewrite it").
- A structural theory of slop: *"A draft can avoid every banned word and still read as
  AI because of its shape."* Slop is old rhetoric used **by default, stacked, and with
  nothing specific behind them**.
- The **`[NEED: proof]` / `[NEED: differentiator]` flag mechanism**: when a claim cannot
  be supported the skill neither invents it nor drops it silently — it emits a named flag
  and the exact evidence that would unlock it.
- An eval format (`prompt` → `expected_output` → `assertions`) that is the reusability
  substrate.

**The library is not anti-hype; it is anti-*weak*-hype.** Its banned words
("revolutionary", "seamless", "game-changer") are banned for being empty, not for being
strong. Its headline formulas — *"Never {unpleasant event} again"*, *"What if you could
{outcome}?"* — are hype formulas. Strong hype is specific, dramatic, and about the
reader's future; weak hype is adjectives.

**The genuine gap.** The library writes the page once you *tell it* the positioning. It
expects a `.agents/product-marketing.md` context file to already exist. This project is
the **upstream derivation**: read a builder's real artifacts, establish what is true,
produce the positioning the copywriting skill consumes.

## 3. Architecture

Four stages, plain JSON between them, one file per stage.

```
artifact repo → claims.json → trends.json → positioning.json → story.md
                    ↑_______________ [NEED:] _______________↓
```

### 3.1 Intake — `intake.py`

Reads the artifact: README, code entry points, tests, commit subjects, docs, demo output.
Emits `claims.json`. Refuses to guess mechanism — an unread fact becomes an `unknown`,
never a plausible invention.

```json
{
  "schema": "prd-agent.claims.v1",
  "artifact": { "name": "", "path": "", "commit": "", "read_at": "" },
  "claims": [
    { "id": "C-001", "text": "", "status": "verified|claimed|unknown",
      "evidence": "path:line or commit sha", "note": "" }
  ],
  "unknowns": []
}
```

`verified` = pointed at in the artifact. `claimed` = asserted by the artifact's own
prose. `unknown` = not established.

### 3.2 Trends — `trends.py`

A live web pass. No scraped corpus in version one; that is a documented later seam.
Extracts all three trend kinds the owner asked for:

- **Category** — what competing and adjacent products claim right now, with the language
  they use. This is what makes the swap test runnable.
- **Style** — what register of copy is currently landing, so the story reads current
  rather than dated.
- **Cultural** — the conversation worth attaching to.

Also picks the **market sophistication stage** (Schwartz): a virgin market gets a claim,
a crowded one a bigger claim, a jaded one a new mechanism, an exhausted one
identification instead of promise. This decides how loud the story goes.

```json
{
  "schema": "prd-agent.trends.v1",
  "category": { "competitors": [ { "name": "", "url": "", "claim": "", "language": [] } ],
                "sophistication_stage": "" },
  "style": { "register": "", "notes": [] },
  "cultural": [ { "moment": "", "url": "", "relevance": "" } ],
  "searched_at": ""
}
```

### 3.3 Positioning — `positioning.py`

Derives the spine and the differentiator. If no differentiator survives the swap test,
it emits a flag rather than writing mush.

```json
{
  "schema": "prd-agent.positioning.v1",
  "audience": { "who": "", "situation": "", "trigger": "" },
  "discomfort": "", "vision": "", "path": "",
  "alternative": "", "differentiator": "",
  "swap_test": { "passed": false, "note": "" },
  "flags": [ { "id": "N-001", "need": "", "claim": "", "unlock": "" } ]
}
```

### 3.4 Story — `story.py`

Hands positioning to the vendored `copywriting` skill. Emits `story.md`, a
GitHub-flavored markdown marketing document: hero, problem, benefits, how it works,
proof, objections, CTA. Hype uncapped. Factual footnotes and open flags live behind the
marketing, not inside it.

### 3.5 Interface

One entry point, run from the repository root:

```
python -m prd_agent <artifact-path> [--autonomous] [--out stories/<name>.md]
```

Without `--autonomous` the run stops at the flag loop and asks. With it, the run
completes and writes the flag footer. Intermediate JSON is written beside the story
under `runs/<name>/` so any stage can be inspected or re-run in isolation.

## 4. The storyboard loop

The `[NEED:]` flags **are** the storyboard. There is no separate question-generation
step. When a stage cannot derive something it emits a flag carrying the claim, the kind
of need, and the evidence that would resolve it.

- **Human mode** — flags are put to the owner before the story is finalized; answers are
  folded back into positioning and the story is regenerated.
- **Autonomous mode** — the same codepath with one boolean. The story ships, with a
  machine-readable flag footer recording what stayed unresolved.

One pipeline, two modes, one difference: whether the loop is interrupted for a human.

## 5. Reusability

Every finished story is appended as a worked example in the marketingskills eval format
(`prompt` → `expected_output` → `assertions`), and becomes an exemplar the next run can
retrieve. Run one uses a template; run fifty uses fifty real stories. This is how the
process repeats both with and without a human.

## 6. Testing

**Machine-checkable:** swap test, banned shapes and the self-check pass, the three
structural beats (discomfort → vision → path), flag resolution, schema validity.

**Not machine-checkable:** whether the story actually hits. Model judges cannot reliably
detect slop, so this is recorded as the owner's acceptance criterion rather than faked
with an automated score.

**Fixture:** the first run operates on the owner's own ACS hot-loader repository — a real
artifact with a known shape.

## 7. Failure modes

| Condition | Behaviour |
|---|---|
| Artifact with no evidence | Emit flags; produce no invented mechanism |
| Artifact too large to read | Read entry points, README, tests, commit subjects; declare what was skipped |
| No differentiator survives the swap test | Flag `[NEED: differentiator]`; never write generic copy |
| Storyboarding with no human available | Autonomous mode; ship with flag footer |
| Contradicting the artifact | The one refusal that survives — do not sell a CLI as a GUI |

## 8. Build order

The swap test needs competitors, and the sophistication stage needs category trends, so
`positioning.py` depends on `trends.json`. Steps 3–5 therefore run against a hand-written
fixture `trends.json` until step 6 wires the live web pass. This keeps each stage
independently testable without the network.

1. Vendor the `copywriting` skill and its references into the repo.
2. `intake.py` + `claims.json` schema + a test against the ACS hot-loader artifact.
3. `positioning.py` + schema + swap-test check, against a fixture `trends.json`.
4. `story.py` + the copywriting handoff + structural-beat checks.
5. The flag loop and the two modes.
6. `trends.py` + the live web pass and sophistication staging, replacing the fixture.
7. Eval append and exemplar retrieval.

Each step is independently verifiable. The corpus/retrieval seam is documented, not built.

## 9. Resolved decisions

- **Output form:** markdown story doc.
- **Hype ceiling:** none — hype overrides verification.
- **First target:** the owner's ACS hot-loader repository.
- **Trends:** all three kinds, live web search, no corpus in version one.
