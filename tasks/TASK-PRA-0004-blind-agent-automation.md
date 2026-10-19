# TASK-PRA-0004 — Blind Agent Automation

<!-- continuity:task {"acceptance":["Default CLI execution to autonomous mode so python -m prd_agent runs end-to-end without hanging on stdin","Add --interactive flag to opt into human flag answering loop","Package skills/prd-agent/SKILL.md as an agent skill defining how any blind agent can invoke PRD-agent","Update README.md to reflect default autonomous mode and remove obsolete mentions of proof-table footers","All unit and integration tests passing"],"depends_on":[],"goal":"Default to autonomous execution, package the prd-agent skill, and update documentation","id":"PRA-0004","issue_url":"https://github.com/Pukujan/PRD-agent/issues/14","next_action":"Run continuity checkpoint, open PR on GitHub, verify CI gates, and merge","owner":"Pukujan","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Blind agents without prior context must run PRD-agent without hanging on interactive prompts"} -->

- Status: active
- Owner: Pukujan
- Priority: P1
- Depends on: none

## Goal

Default to autonomous execution, package the prd-agent skill, and update documentation

## Why

Blind agents without prior context must run PRD-agent without hanging on interactive prompts

## Allowed files

- `src/prd_agent/cli.py`
- `src/prd_agent/pipeline.py`
- `skills/prd-agent/SKILL.md`
- `README.md`
- `checkpoints/CURRENT.md`
- `tasks/TASK-PRA-0004-blind-agent-automation.md`
- `tests/test_cli.py`
- `tests/test_pipeline.py`

## Human outcome

Any newly spawned coding agent or tool can run `python -m prd_agent <path>` without any flags and have it run cleanly to completion without hanging on stdin, and can discover how to run it via `skills/prd-agent/SKILL.md`.

## Scope and boundaries

- In scope: Change CLI default to autonomous (add `--interactive`), create `skills/prd-agent/SKILL.md`, sync `README.md`, update CLI tests.
- Out of scope: Modifying stage JSON schemas or checks logic.

## Acceptance criteria

- [x] Default CLI execution to autonomous mode so `python -m prd_agent` runs end-to-end without hanging on stdin.
- [x] Add `--interactive` flag to opt into human flag answering loop.
- [x] Package `skills/prd-agent/SKILL.md` as an agent skill defining how any blind agent can invoke PRD-agent.
- [x] Update `README.md` to reflect default autonomous mode and remove obsolete mentions of proof-table footers.
- [x] All unit and integration tests passing.

## Evidence and sources

- Leaf issue: https://github.com/Pukujan/PRD-agent/issues/14
- `PROJECT.md`
- `docs/OWNER_VISION.md`

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): Leaf: https://github.com/Pukujan/PRD-agent/issues/14, Parent: none, Dependencies: none
- Primary writer / branch / source issue revision / as-of status: Antigravity / `task/PRA-0004-blind-agent-automation` / issue #14 / active
- Related PR/CI evidence and push receipt (request ID / SHA): pending

## Checkpoint log

No checkpoints yet.

### 2026-10-19 03:55:45 UTC — Antigravity

<!-- continuity:checkpoint {"agent":"Antigravity","blocked":[],"changed":["src/prd_agent/cli.py, src/prd_agent/pipeline.py, skills/prd-agent/SKILL.md, README.md, tests/test_cli.py"],"completed":["Made autonomous mode the default in cli.py and pipeline.py, adding --interactive for human flag prompting","Packaged skills/prd-agent/SKILL.md as a standardized agent skill for blind agent discovery","Updated README.md to document autonomous default and remove legacy proof table footer mentions"],"decisions":["no new decisions"],"evidence":["python -m pytest -q: 150 passed with 0 failures","continuity validate --root .: VALID"],"next_action":"Open pull request on GitHub, verify CI gates, and merge","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PRA-0004","timestamp":"2026-10-19T03:55:45Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"4f5bd94faec01c332e23e1f6b9e94ed133a0a5dc17f7d4b4a3207f57ef6a8948","request_id":"d2cf8c3946064900af9d199682539609","schema":"project-continuity.checkpoint-operation.v1","task_id":"PRA-0004"} -->

Completed:
- Made autonomous mode the default in cli.py and pipeline.py, adding --interactive for human flag prompting
- Packaged skills/prd-agent/SKILL.md as a standardized agent skill for blind agent discovery
- Updated README.md to document autonomous default and remove legacy proof table footer mentions

Evidence:
- python -m pytest -q: 150 passed with 0 failures
- continuity validate --root .: VALID

Decisions:
- no new decisions

Changed:
- src/prd_agent/cli.py, src/prd_agent/pipeline.py, skills/prd-agent/SKILL.md, README.md, tests/test_cli.py

Blocked/uncertain:
- none

Next:
- Open pull request on GitHub, verify CI gates, and merge

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
