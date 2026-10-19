# TASK-PRA-0011 — Consolidate Narrative Engine

<!-- continuity:task {"acceptance":["SDD: docs/superpowers/specs/2026-10-19-consolidated-narrative-engine.md defines the consolidated contract","BDD/TDD: All tests in tests/test_consolidated.py pass cleanly","Unified Architecture: One unified engine replaces the split between hype level and 4-step dogma","Turnkey Output: Running on any repo outputs both the 5-line executive hook and 5-beat manifesto directly to stdout and target files","Blind Agent Zero-Leakage: Output is strictly free of meta-labels ('Level 1000', 'belief inversion'), template starters ('The false dogma says'), and alphabet-soup identifier dumps","Hidden Holdout: Automated run on TurboFit cleanly passes all anti-audit gates","Repository Integrity: mypy 0 errors, ruff 0 errors, pytest 100% green, and continuity validate VALID"],"depends_on":[],"goal":"Consolidate narrative engine: fuse hype dial and belief inversion into a single turnkey protocol for any repository","id":"PRA-0011","issue_url":"https://github.com/Pukujan/PRD-agent/issues/26","next_action":"Commit product and docs, run continuity checkpoint, push branch, create PR, verify CI, auto-merge, and publish leaf receipt","owner":"Pukujan","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Unify fragmented routes into one seamless engine that any repo can point to without meta-leakage or friction"} -->

- Status: active
- Owner: Pukujan
- Priority: P1
- Depends on: none

## Goal

Consolidate narrative engine: fuse hype dial and belief inversion into a single turnkey protocol for any repository

## Why

Unify fragmented routes into one seamless engine that any repo can point to without meta-leakage or friction

## Allowed files

- `src/prd_agent/`
- `tests/`
- `docs/superpowers/specs/`
- `skills/prd-agent/SKILL.md`
- `PROMPT.md`
- `README.md`
- `checkpoints/CURRENT.md`
- `.continuity/`
- `docs/CONTINUITY_INDEX.md`

## Human outcome

Any user or blind agent pointing to PRD-agent gets an immediate, automated, high-stakes manifesto (5-line hook + 5-beat full narrative) with zero meta-leakage, zero fragmented dials, and zero alphabet-soup code dumps.

## Scope and boundaries

- In scope:
  - Write SDD spec in `docs/superpowers/specs/2026-10-19-consolidated-narrative-engine.md`.
  - Write BDD/TDD tests in `tests/test_consolidated.py`.
  - Consolidate hype dial and 4-step belief inversion into unified Tension Spine + Manifesto Voice architecture.
  - Implement turnkey stdout output (5-line hook + 5-beat story) in CLI.
  - Add root `PROMPT.md` for blind agent chat ingestion.
  - Run hidden holdout verification on TurboFit.
  - Maintain 100% mypy, ruff, pytest, and continuity validation.
- Out of scope:
  - Modifying `.content-system/`, `.coord/`, `stack-official` pins or `acs-gates.yml`.

## Acceptance criteria

- [x] SDD: `docs/superpowers/specs/2026-10-19-consolidated-narrative-engine.md` defines the consolidated contract.
- [x] BDD/TDD: All tests in `tests/test_consolidated.py` pass cleanly.
- [x] Unified Architecture: One unified engine replaces the split between hype level and 4-step dogma.
- [x] Turnkey Output: Running on any repo outputs both the 5-line executive hook and 5-beat manifesto directly to stdout and target files.
- [x] Blind Agent Zero-Leakage: Output is strictly free of meta-labels (`Level 1000`, `belief inversion`), template starters (`The false dogma says`), and alphabet-soup identifier dumps.
- [x] Hidden Holdout: Automated run on TurboFit cleanly passes all anti-audit gates.
- [x] Repository Integrity: `mypy` 0 errors, `ruff` 0 errors, `pytest` 100% green, and `continuity validate` VALID.

## Evidence and sources

- GitHub Issue: https://github.com/Pukujan/PRD-agent/issues/26.


## Reproduction details (only when needed)

Starting revision, material inputs/configuration, runtime, exact command or prompt, observed result, and limitations.

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none):
- Primary writer / branch / source issue revision / as-of status:
- Related PR/CI evidence and push receipt (request ID / SHA):

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
