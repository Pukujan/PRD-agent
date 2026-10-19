# TASK-PRA-0005 — Intake Token Ceiling

<!-- continuity:task {"acceptance":["Add claim count ceiling and brevity guidelines to intake prompt (12-18 distinctive claims, concise text and notes)","Allow max_tokens configuration via PRD_AGENT_MAX_TOKENS environment variable in llm.py","Implement robust partial-JSON salvage in extract_json() when JSON is truncated mid-stream","Unit tests for claim ceiling instruction and truncated JSON salvage in tests/test_intake.py and tests/test_llm.py","All unit and integration tests passing"],"depends_on":[],"goal":"Bound intake claim extraction and add truncation resilience to extract_json","id":"PRA-0005","issue_url":"https://github.com/Pukujan/PRD-agent/issues/10","next_action":"Checkpoint and open pull request","owner":"Pukujan","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Large repository artifacts exhaust model output tokens during intake, causing truncated JSON to fail the run"} -->

- Status: active
- Owner: Pukujan
- Priority: P1
- Depends on: none

## Goal

Bound intake claim extraction and add truncation resilience to extract_json

## Why

Large repository artifacts exhaust model output tokens during intake, causing truncated JSON to fail the run

## Allowed files

- `src/prd_agent/intake.py`
- `src/prd_agent/llm.py`
- `tests/test_intake.py`
- `tests/test_llm.py`
- `checkpoints/CURRENT.md`
- `tasks/TASK-PRA-0005-intake-token-ceiling.md`

## Human outcome

PRD-agent will reliably ingest large repositories without blowing model output token limits or failing abruptly on truncated JSON replies.

## Scope and boundaries

- In scope: Intake prompt ceiling (12-18 claims), `PRD_AGENT_MAX_TOKENS` env var, `extract_json()` truncation salvage helper, unit tests.
- Out of scope: Redesigning repository file collection in `artifact.py`.

## Acceptance criteria

- [x] Add claim count ceiling and brevity guidelines to intake prompt (12-18 distinctive claims, concise text and notes).
- [x] Allow `max_tokens` configuration via `PRD_AGENT_MAX_TOKENS` environment variable in `llm.py`.
- [x] Implement robust partial-JSON salvage in `extract_json()` when JSON is truncated mid-stream.
- [x] Unit tests for claim ceiling instruction and truncated JSON salvage in `tests/test_intake.py` and `tests/test_llm.py`.
- [x] All unit and integration tests passing.

## Evidence and sources

- Leaf issue: https://github.com/Pukujan/PRD-agent/issues/10
- `PROJECT.md`

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): Leaf: https://github.com/Pukujan/PRD-agent/issues/10, Parent: none, Dependencies: none
- Primary writer / branch / source issue revision / as-of status: Antigravity / `task/PRA-0005-intake-token-ceiling` / issue #10 / active
- Related PR/CI evidence and push receipt (request ID / SHA): pending

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
