# TASK-PRA-0007 — Hype Dial

<!-- continuity:task {"acceptance":["python -m pytest tests/test_hype.py passes all 4 tier calibration tests","python -m pytest passes all 167 unit and integration tests cleanly","--hype CLI parameter parses canonical values and aliases (1000, 750, 500, 250, electric, venture, balanced, truth)","interactive mode prompts operator with 4-tier calibration menu when --hype is omitted","selected hype directive is injected into positioning and story prompts"],"depends_on":[],"goal":"Add the 4-tier Hype-to-Honesty Dial with interactive pre-generation calibration","id":"PRA-0007","issue_url":"https://github.com/Pukujan/PRD-agent/issues/18","next_action":"Commit product code and documentation, run continuity checkpoint, and open pull request","owner":"Pukujan","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Builders need copy calibrated from Level 1000 electric solo-unicorn hype down to Level 250 pure technical truth"} -->

- Status: active
- Owner: Pukujan
- Priority: P1
- Depends on: none

## Goal

Add the 4-tier Hype-to-Honesty Dial with interactive pre-generation calibration

## Why

Builders need copy calibrated from Level 1000 electric solo-unicorn hype down to Level 250 pure technical truth

## Allowed files

- `src/prd_agent/hype.py`
- `src/prd_agent/cli.py`
- `src/prd_agent/pipeline.py`
- `src/prd_agent/positioning.py`
- `src/prd_agent/schemas.py`
- `src/prd_agent/story.py`
- `README.md`
- `skills/prd-agent/SKILL.md`
- `tests/test_hype.py`
- `tests/test_cli.py`
- `tests/test_positioning.py`
- `tests/test_story.py`
- `tests/test_pipeline.py`

## Human outcome

Builders can generate marketing copy tuned exactly to their target audience: loud, kinetic Level 1000 electric god-mode for public drops and solopreneur launches, down to Level 250 clinical technical truth for security and systems audits.

## Scope and boundaries

- In scope:
  - 4 calibration tiers: Level 1000 (Electric God-Mode), Level 750 (Venture Hype), Level 500 (Balanced Authority), Level 250 (Pure Technical Truth).
  - CLI argument `--hype` with aliases and canonical normalizer.
  - Interactive pre-generation prompt when running interactively without `--hype`.
  - Directive injection into positioning and story generation prompts.
- Out of scope:
  - Modifying external model providers or network protocols.
  - Changes to `.coord/` or `stack-official` pins.

## Acceptance criteria

- [x] `python -m pytest tests/test_hype.py` passes all 4 tier calibration tests.
- [x] `python -m pytest` passes all 167 unit and integration tests cleanly.
- [x] `--hype` CLI parameter parses canonical values and aliases (1000, 750, 500, 250, electric, venture, balanced, truth).
- [x] Interactive mode prompts operator with 4-tier calibration menu when `--hype` is omitted.
- [x] Selected hype directive is injected into positioning and story prompts.

## Evidence and sources

- `python -m pytest -q`: 167 passed in 9.09s.
- `continuity validate --root .`: VALID.
- Leaf GitHub issue: https://github.com/Pukujan/PRD-agent/issues/18.

## Related records

- Required leaf owning issue, parent ancestry and dependencies: leaf https://github.com/Pukujan/PRD-agent/issues/18, parent: none.
## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.

