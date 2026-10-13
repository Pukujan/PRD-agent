# PRD-agent: design

**Date:** 2026-10-13
**Status:** approved by owner, pending implementation plan

## 1. The problem

A builder makes repositories, tools, protocols and demos. He can explain how each one
works. What he cannot easily do is explain, to a stranger, why it should exist. Turning
his own artifacts into a product story is the missing step.

Generated marketing copy fails at this in a nameable way. It reads like an **audit**, an
inventory of what the product does and what it lacks. The owner's words: *"marketing
pages contents and stories are coming out like audits instead of what they are. They need
marketing and upsells."*

Two things are settled and are not open questions in this design:

- **Hype is uncapped.** Asked whether the pipeline should refuse anything, the owner chose
  maximum hype. Invented-sounding numbers are allowed unless they contradict what the
  artifact actually is. Every rule the pipeline carries serves the pitch.
- **The market analysis stays behind the curtain.** The agent reads what exists and what
  does not so it knows what to say. None of that inventory reaches the reader.

## 2. What already exists, and what does not

**Vendored as a dependency.** `coreyhaines31/marketingskills` (MIT, ~50 skills) ships the
pieces this project needs:

- The **Human Action Model** spine: current discomfort → better vision → path to action.
  This is the upsell structure.
- The **"Now you can…" test** and the **swap test**: if a line would work unchanged on a
  competitor's site, rewrite it.
- A structural theory of slop: *"A draft can avoid every banned word and still read as AI
  because of its shape."* Slop is old rhetoric used **by default, stacked, and with
  nothing specific behind them**.
- The **`[NEED: proof]` / `[NEED: differentiator]` flag mechanism**. When a claim cannot be
  supported, the skill emits a named flag carrying the exact evidence that would unlock it.
- An eval format (`prompt` → `expected_output` → `assertions`) that is the reusability
  substrate.

**The library pushes weak hype out and lets strong hype through.** Its banned words
("revolutionary", "seamless", "game-changer") are banned for being empty. Its headline
formulas, *"Never {unpleasant event} again"* and *"What if you could {outcome}?"*, are
hype formulas. Strong hype is specific, dramatic, and about the reader's future. Weak
hype is adjectives.

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

### 3.1 Intake (`intake.py`)

Reads the artifact: README, code entry points, tests, commit subjects, docs, demo output.
Emits `claims.json`. An unread fact becomes an `unknown`. The stage never invents a
plausible mechanism.

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

`verified` means the claim is pointed at in the artifact. `claimed` means the artifact's
own prose asserts it. `unknown` means it is not established.

### 3.2 Trends (`trends.py`)

A live web pass. Version one ships no scraped corpus; that is a documented later seam.
The stage extracts all three trend kinds the owner asked for:

- **Category.** What competing and adjacent products claim right now, with the language
  they use. This is what makes the swap test runnable.
- **Style.** What register of copy is currently landing, so the story reads current rather
  than dated.
- **Cultural.** The conversation worth attaching to.

The stage also picks the **market sophistication stage** (Schwartz). A virgin market gets
a claim, a crowded one a bigger claim, a jaded one a new mechanism, an exhausted one gets
identification. This decides how loud the story goes.

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

### 3.3 Positioning (`positioning.py`)

Derives the spine and the differentiator. When no differentiator survives the swap test,
the stage emits a flag and writes no generic copy.

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

### 3.4 Story (`story.py`)

Hands positioning to the vendored `copywriting` skill. Emits `story.md`, a GitHub-flavored
markdown marketing document: hero, problem, benefits, how it works, proof, objections,
CTA. Hype uncapped.

The stage then runs the skill's own self-check as a gate. A draft that trips a banned
pattern fails the gate and gets rewritten from the facts before it can ship. Factual
footnotes and open flags live behind the marketing.

### 3.5 Interface

One entry point, run from the repository root:

```
python -m prd_agent <artifact-path> [--autonomous] [--out stories/<name>.md]
```

Without `--autonomous` the run stops at the flag loop and asks. With it, the run completes
and writes the flag footer. Intermediate JSON is written beside the story under
`runs/<name>/` so any stage can be inspected or re-run in isolation.

## 4. The storyboard loop

The `[NEED:]` flags **are** the storyboard. There is no separate question-generation step.
When a stage cannot derive something it emits a flag carrying the claim, the kind of need,
and the evidence that would resolve it.

- **Human mode.** Flags are put to the owner before the story is finalized. Answers are
  folded back into positioning and the story is regenerated.
- **Autonomous mode.** The same codepath with one boolean. The story ships with a
  machine-readable flag footer recording what stayed unresolved.

One pipeline and two modes. The only difference is whether the loop stops for a human.

## 5. Reusability

Every finished story is appended as a worked example in the marketingskills eval format
(`prompt` → `expected_output` → `assertions`), and becomes an exemplar the next run can
retrieve. Run one uses a template; run fifty uses fifty real stories. This is how the
process repeats both with and without a human.

## 6. Testing

**Machine-checkable:** the swap test, the banned shapes and self-check gate, the three
structural beats (discomfort → vision → path), flag resolution, schema validity.

**Not machine-checkable:** whether the story actually hits. Model judges cannot reliably
detect slop, so this is recorded as the owner's acceptance criterion.

**Fixture:** the first run operates on the owner's own ACS hot-loader repository, a real
artifact with a known shape.

## 7. Failure modes

| Condition | Behaviour |
|---|---|
| Artifact with no evidence | Emit flags; produce no invented mechanism |
| Artifact too large to read | Read entry points, README, tests, commit subjects; declare what was skipped |
| No differentiator survives the swap test | Flag `[NEED: differentiator]`; never write generic copy |
| Storyboarding with no human available | Autonomous mode; ship with flag footer |
| A claim contradicts the artifact | The one refusal that survives. A CLI is never sold as a GUI |

## 8. Build order

The swap test needs competitors, and the sophistication stage needs category trends, so
`positioning.py` depends on `trends.json`. Steps 3 through 5 therefore run against a
hand-written fixture `trends.json` until step 6 wires the live web pass. This keeps each
stage independently testable without the network.

1. Vendor the `copywriting` skill and its references into the repo.
2. `intake.py`, the `claims.json` schema, and a test against the ACS hot-loader artifact.
3. `positioning.py`, its schema, and the swap-test check, against a fixture `trends.json`.
4. `story.py`, the copywriting handoff, and the self-check gate.
5. The flag loop and the two modes.
6. `trends.py`, the live web pass, and sophistication staging, replacing the fixture.
7. Eval append and exemplar retrieval.

Each step is independently verifiable. The corpus/retrieval seam is documented, not built.

## 9. Resolved decisions

- **Output form:** markdown story doc.
- **Hype ceiling:** none. Hype overrides verification.
- **First target:** the owner's ACS hot-loader repository.
- **Trends:** all three kinds, live web search, no corpus in version one.
