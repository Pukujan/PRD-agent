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

### 2026-10-19 16:59:57 UTC — Antigravity

<!-- continuity:checkpoint {"agent":"Antigravity","blocked":[],"changed":["src/prd_agent/, tests/, PROMPT.md, docs/superpowers/specs/, tasks/TASK-PRA-0011-consolidate-narrative-engine.md, checkpoints/CURRENT.md"],"completed":["Consolidated the narrative engine by fusing the hype dial and belief inversion into a unified Tension Spine + Manifesto Voice architecture (src/prd_agent/voice.py)","Wired turnkey 5-Line Executive Battle Cry directly to stdout in cli.py and five_lines.txt in pipeline.py","Added root PROMPT.md for blind chat agents and passed hidden holdout verification on turbofit repository"],"decisions":["no new decisions"],"evidence":["python -m pytest -q: 200 passed in 11.52s","python -m ruff check src/ tests/: 0 errors","python -m mypy src/: 0 errors in 21 source files","continuity validate --root .: VALID"],"next_action":"Open the pull request, wait for the gates check, auto-merge, and publish leaf receipt","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PRA-0011","timestamp":"2026-10-19T16:59:57Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"b358131da3bbfed1c05e763a85c07a60ca4d6b2df3af79f79d91a1a71964c9a8","request_id":"a4ea7d3793634b738740366df2778ba0","schema":"project-continuity.checkpoint-operation.v1","task_id":"PRA-0011"} -->

Completed:
- Consolidated the narrative engine by fusing the hype dial and belief inversion into a unified Tension Spine + Manifesto Voice architecture (src/prd_agent/voice.py)
- Wired turnkey 5-Line Executive Battle Cry directly to stdout in cli.py and five_lines.txt in pipeline.py
- Added root PROMPT.md for blind chat agents and passed hidden holdout verification on turbofit repository

Evidence:
- python -m pytest -q: 200 passed in 11.52s
- python -m ruff check src/ tests/: 0 errors
- python -m mypy src/: 0 errors in 21 source files
- continuity validate --root .: VALID

Decisions:
- no new decisions

Changed:
- src/prd_agent/, tests/, PROMPT.md, docs/superpowers/specs/, tasks/TASK-PRA-0011-consolidate-narrative-engine.md, checkpoints/CURRENT.md

Blocked/uncertain:
- none

Next:
- Open the pull request, wait for the gates check, auto-merge, and publish leaf receipt

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
