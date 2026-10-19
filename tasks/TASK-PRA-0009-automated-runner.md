# TASK-PRA-0009 — Automated Runner

<!-- continuity:task {"acceptance":["default_llm() normalizes ANTHROPIC_BASE_URL to append /v1/messages if missing","default_llm() falls back to HADES_LITELLM_API_KEY or OPENCODE_LITELLM_MASTER_KEY when ANTHROPIC_API_KEY is unset","default_llm() honors ANTHROPIC_MODEL when PRD_AGENT_MODEL is unset","clean_body() purges forbidden em-dashes and double-hyphens so drafts do not fail the gate for punctuation alone","--readme CLI flag writes the generated story directly to <artifact_path>/README.md","all unit and integration tests pass cleanly"],"depends_on":[],"goal":"Automate PRD-agent execution with proxy auto-discovery, em-dash auto-purge, and --readme target","id":"PRA-0009","issue_url":"https://github.com/Pukujan/PRD-agent/issues/22","next_action":"Commit, checkpoint, push, open PR, verify gates and auto-merge, and post receipt to issue #22","owner":"Pukujan","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Autonomous agents need zero-configuration execution against local proxies and direct README writing to complete repository marketing stories without failure"} -->

- Status: active
- Owner: Pukujan
- Priority: P1
- Depends on: none

## Goal

Automate PRD-agent execution with proxy auto-discovery, em-dash auto-purge, and --readme target

## Why

Autonomous agents need zero-configuration execution against local proxies and direct README writing to complete repository marketing stories without failure

## Allowed files

- `src/prd_agent/llm.py`
- `src/prd_agent/story.py`
- `src/prd_agent/cli.py`
- `src/prd_agent/pipeline.py`
- `README.md`
- `skills/prd-agent/SKILL.md`
- `tests/test_llm.py`
- `tests/test_story.py`
- `tests/test_cli.py`
- `tests/test_pipeline.py`

## Human outcome

Builders and autonomous agents can execute `python -m prd_agent <path> --readme` with zero configuration, auto-discovering local proxy endpoints and keys, automatically purging forbidden em-dashes without failing gates, and writing the final marketing story directly into the target repository's `README.md`.

## Scope and boundaries

- In scope:
  - LiteLLM and proxy `base_url` normalization in `llm.py` (ensuring `/v1/messages` is appended when `/v1` or raw port is given).
  - Proxy key fallback (`HADES_LITELLM_API_KEY`, `OPENCODE_LITELLM_MASTER_KEY`) when `ANTHROPIC_API_KEY` is not exported.
  - Model fallback: honoring `ANTHROPIC_MODEL` before falling back to `DEFAULT_MODEL`.
  - Em-dash auto-purging in `story.clean_body()` before self-check gating.
  - `--readme` CLI argument directing output to `<artifact_path>/README.md`.
- Out of scope:
  - Modifying external proxy server runtime configurations.
  - Modifying `.continuity/` protocol versions.

## Acceptance criteria

- [x] `default_llm()` normalizes `ANTHROPIC_BASE_URL` to append `/v1/messages` if missing.
- [x] `default_llm()` falls back to `HADES_LITELLM_API_KEY` or `OPENCODE_LITELLM_MASTER_KEY` when `ANTHROPIC_API_KEY` is unset.
- [x] `default_llm()` honors `ANTHROPIC_MODEL` when `PRD_AGENT_MODEL` is unset.
- [x] `clean_body()` purges forbidden em-dashes and double-hyphens so drafts do not fail the gate for punctuation alone.
- [x] `--readme` CLI flag writes the generated story directly to `<artifact_path>/README.md`.
- [x] All unit and integration tests pass cleanly.

## Evidence and sources


- GitHub Issue: https://github.com/Pukujan/PRD-agent/issues/22.

## Related records

- Required leaf owning issue, parent ancestry and dependencies: leaf https://github.com/Pukujan/PRD-agent/issues/22, parent: none.

## Checkpoint log

No checkpoints yet.

### 2026-10-19 10:52:30 UTC — Antigravity

<!-- continuity:checkpoint {"agent":"Antigravity","blocked":[],"changed":["src/prd_agent/llm.py, src/prd_agent/story.py, src/prd_agent/cli.py, src/prd_agent/pipeline.py, tests/, README.md, skills/prd-agent/SKILL.md"],"completed":["Automated runner discovery: default_llm() normalizes ANTHROPIC_BASE_URL to /v1/messages, falls back to HADES_LITELLM_API_KEY / OPENCODE_LITELLM_MASTER_KEY when ANTHROPIC_API_KEY is unset, and honors ANTHROPIC_MODEL","Added em-dash auto-sanitization in clean_body() before self-check gating and --readme CLI flag to write directly to <artifact_path>/README.md"],"decisions":["no new decisions"],"evidence":["python -m pytest -q: 192 passed cleanly in 11.09s","continuity validate --root .: VALID"],"next_action":"Open PR, verify gates, auto-merge, and publish receipt to issue #22","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PRA-0009","timestamp":"2026-10-19T10:52:30Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"588a0685e01e9f4e669b78fcbfe6d77e677a1f1e9b7b80522340cd2744f87a4a","request_id":"04193e0bc17d45049d8a53d11c99b344","schema":"project-continuity.checkpoint-operation.v1","task_id":"PRA-0009"} -->

Completed:
- Automated runner discovery: default_llm() normalizes ANTHROPIC_BASE_URL to /v1/messages, falls back to HADES_LITELLM_API_KEY / OPENCODE_LITELLM_MASTER_KEY when ANTHROPIC_API_KEY is unset, and honors ANTHROPIC_MODEL
- Added em-dash auto-sanitization in clean_body() before self-check gating and --readme CLI flag to write directly to <artifact_path>/README.md

Evidence:
- python -m pytest -q: 192 passed cleanly in 11.09s
- continuity validate --root .: VALID

Decisions:
- no new decisions

Changed:
- src/prd_agent/llm.py, src/prd_agent/story.py, src/prd_agent/cli.py, src/prd_agent/pipeline.py, tests/, README.md, skills/prd-agent/SKILL.md

Blocked/uncertain:
- none

Next:
- Open PR, verify gates, auto-merge, and publish receipt to issue #22

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
