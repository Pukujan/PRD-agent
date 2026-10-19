# TASK-PRA-0003 — Story First Hype Engine

<!-- continuity:task {"acceptance":["_EM_DASH catches both Unicode and ASCII double hyphens with hard ban in short copy","Add audit_jargon and code_path_in_prose hard bans in checks.py","Add feature_before_story hard ban in checks.py ensuring Hero and Problem are 100% human nightmare and dream","Remove build_footer() from story.py assembly so story output is pure pitch with zero audit clutter","Update trends.py and schemas to hunt cultural zeitgeist, human nightmare, and hype language","Update positioning.py to require concrete cinematic nightmare and dream scenes","Clean stories/acs-hot-loader.md to match the gold standard with zero dashes and zero audit clutter","All unit and integration tests passing"],"depends_on":[],"goal":"Enforce story-first dream creation, cultural zeitgeist hunting, and anti-audit gates","id":"PRA-0003","issue_url":"https://github.com/Pukujan/PRD-agent/issues/12","next_action":"None. Task completed and merged into main via PR #13","owner":"Pukujan","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"completed","why":"AI writing defaults to dry audits; PRD-agent exists to build pure human relatable hype and aspiration"} -->

- Status: completed
- Owner: Pukujan
- Priority: P1
- Depends on: none

## Goal

Enforce story-first dream creation, cultural zeitgeist hunting, and anti-audit gates

## Why

AI writing defaults to dry audits; PRD-agent exists to build pure human relatable hype and aspiration

## Allowed files

- `src/prd_agent/checks.py`
- `src/prd_agent/story.py`
- `src/prd_agent/trends.py`
- `src/prd_agent/positioning.py`
- `src/prd_agent/schemas.py`
- `stories/acs-hot-loader.md`
- `docs/GOLD_STANDARD.md`
- `PROJECT.md`
- `tests/*`
- `checkpoints/CURRENT.md`
- `tasks/TASK-PRA-0003-story-first-hype-engine.md`

## Human outcome

Any repository processed by PRD-agent will receive a compelling, human-relatable marketing story that sells the dream and outcome, with hard machine gates ensuring zero audit tables, zero code-path citations, zero em-dash crutches, and pure story-first narrative flow.

## Scope and boundaries

- In scope: Anti-audit checks in `checks.py`, em-dash `--` and `—` bans, removal of footer from `story.py`, cultural zeitgeist hunting in `trends.py`, scene requirement in `positioning.py`, clean gold-standard `stories/acs-hot-loader.md`.
- Out of scope: Modifying `.coord/` or `.github/workflows/acs-gates.yml`.
- Dependencies/uncertainty: None. Offline test suite must remain 100% green.

## Acceptance criteria

- [x] `_EM_DASH` catches both Unicode and ASCII double hyphens (`--` and `—`) with hard ban in short copy.
- [x] Add `audit_jargon` and `code_path_in_prose` hard bans in `checks.py`.
- [x] Add `feature_before_story` hard ban in `checks.py` ensuring Hero and Problem are 100% human nightmare and dream.
- [x] Remove `build_footer()` from `story.py` assembly so story output is pure pitch with zero audit clutter.
- [x] Update `trends.py` and schemas to hunt cultural zeitgeist, human nightmare, and hype language.
- [x] Update `positioning.py` to require concrete cinematic nightmare and dream scenes.
- [x] Clean `stories/acs-hot-loader.md` to match the gold standard with zero dashes and zero audit clutter.
- [x] All unit and integration tests passing.

## Evidence and sources

- Leaf issue: https://github.com/Pukujan/PRD-agent/issues/12
- `docs/OWNER_VISION.md`
- `PROJECT.md`

## Reproduction details (only when needed)

`python -m pytest -q`

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): Leaf: https://github.com/Pukujan/PRD-agent/issues/12, Parent: none, Dependencies: none
- Primary writer / branch / source issue revision / as-of status: Antigravity / `task/PRA-0003-story-first-hype-engine` / issue #12 / active
- Related PR/CI evidence and push receipt (request ID / SHA): pending

## Checkpoint log

No checkpoints yet.

### 2026-10-19 03:36:27 UTC — Antigravity

<!-- continuity:checkpoint {"agent":"Antigravity","blocked":[],"changed":["src/prd_agent/checks.py, src/prd_agent/story.py, src/prd_agent/trends.py, src/prd_agent/positioning.py, src/prd_agent/schemas.py, stories/acs-hot-loader.md, docs/GOLD_STANDARD.md, tests/"],"completed":["Enforced story-first dream creation and anti-audit machine gates across checks, story, positioning, trends, and schemas","Hard bans added in checks.py for ascii_em_dash, audit_jargon, code_path_in_prose, and feature_before_story","Removed build_footer() from story assembly so marketing stories are pure pitch with zero audit clutter","Cleaned stories/acs-hot-loader.md to match the reference gold standard with 0 bans and 0 cap violations"],"decisions":["no new decisions"],"evidence":["python -m pytest -q: 149 passed with 0 failures","continuity validate --root .: VALID"],"next_action":"Open pull request on GitHub, verify CI gates, and merge","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PRA-0003","timestamp":"2026-10-19T03:36:27Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"b40334ad8c58606f58a9fc04cea7c101a0eb0ccd81ca1d578ae8984fcbf5244a","request_id":"13f88baeadf54948bf5a5e409474d7a4","schema":"project-continuity.checkpoint-operation.v1","task_id":"PRA-0003"} -->

Completed:
- Enforced story-first dream creation and anti-audit machine gates across checks, story, positioning, trends, and schemas
- Hard bans added in checks.py for ascii_em_dash, audit_jargon, code_path_in_prose, and feature_before_story
- Removed build_footer() from story assembly so marketing stories are pure pitch with zero audit clutter
- Cleaned stories/acs-hot-loader.md to match the reference gold standard with 0 bans and 0 cap violations

Evidence:
- python -m pytest -q: 149 passed with 0 failures
- continuity validate --root .: VALID

Decisions:
- no new decisions

Changed:
- src/prd_agent/checks.py, src/prd_agent/story.py, src/prd_agent/trends.py, src/prd_agent/positioning.py, src/prd_agent/schemas.py, stories/acs-hot-loader.md, docs/GOLD_STANDARD.md, tests/

Blocked/uncertain:
- none

Next:
- Open pull request on GitHub, verify CI gates, and merge

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
