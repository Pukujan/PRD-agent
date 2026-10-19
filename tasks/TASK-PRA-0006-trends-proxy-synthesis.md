# TASK-PRA-0006 — Trends Proxy Synthesis

<!-- continuity:task {"acceptance":["Detect when trends search returns raw search snippets rather than JSON and run secondary synthesis call with search context","Secondary synthesis call passes tools=None to prevent recursive search loops","Allow disabling web search tool definition via PRD_AGENT_NO_SEARCH_TOOL environment variable for proxy decoupling","Unit tests verifying snippet detection, secondary synthesis call, and search tool disablement in tests/test_trends.py","All unit and integration tests passing"],"depends_on":[],"goal":"Handle raw text search snippets from proxy providers during trends analysis","id":"PRA-0006","issue_url":"https://github.com/Pukujan/PRD-agent/issues/11","next_action":"Checkpoint and open pull request","owner":"Pukujan","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Proxy providers return search text blocks rather than JSON, failing extract_json"} -->

- Status: active
- Owner: Pukujan
- Priority: P1
- Depends on: none

## Goal

Handle raw text search snippets from proxy providers during trends analysis

## Why

Proxy providers return search text blocks rather than JSON, failing extract_json

## Allowed files

- `src/prd_agent/trends.py`
- `tests/test_trends.py`
- `tasks/TASK-PRA-0006-trends-proxy-synthesis.md`
- `checkpoints/CURRENT.md`

## Human outcome

When PRD-agent runs through LLM proxies (e.g. OpenAI/LiteLLM with DuckDuckGo search), search snippet dumps are automatically recognized and synthesized into the required trends JSON schema without manual intervention or crashes.

## Scope and boundaries

- In scope: Detecting search result text in `trends.py`, automated second synthesis call without tools, `PRD_AGENT_NO_SEARCH_TOOL` environment toggle, unit tests.
- Out of scope: Writing custom scrapers or modifying external proxy providers.

## Acceptance criteria

- [x] Detect when trends search returns raw search snippets rather than JSON and run secondary synthesis call with search context.
- [x] Secondary synthesis call passes tools=None to prevent recursive search loops.
- [x] Allow disabling web search tool definition via PRD_AGENT_NO_SEARCH_TOOL environment variable for proxy decoupling.
- [x] Unit tests verifying snippet detection, secondary synthesis call, and search tool disablement in tests/test_trends.py.
- [x] All unit and integration tests passing.

## Evidence and sources

- Leaf issue: https://github.com/Pukujan/PRD-agent/issues/11
- `PROJECT.md`

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): Leaf: https://github.com/Pukujan/PRD-agent/issues/11, Parent: none, Dependencies: none
- Primary writer / branch / source issue revision / as-of status: Antigravity / `task/PRA-0006-trends-proxy-synthesis` / issue #11 / active
- Related PR/CI evidence and push receipt (request ID / SHA): pending

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
