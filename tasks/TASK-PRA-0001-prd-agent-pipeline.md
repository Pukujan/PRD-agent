# TASK-PRA-0001 — Prd Agent Pipeline

<!-- continuity:task {"acceptance":["The four-stage pipeline runs over an artifact and produces story.md","Self-check runs against ai-tells rules and gates draft","Two execution modes (interactive and autonomous) run over one pipeline","Live trend pass analyzes competitors and market sophistication","Finished stories append to evals/story_evals.json and are retrieved by keyword overlap","Python test suite passes with zero network access and continuity validate is VALID"],"depends_on":[],"goal":"Build the four-stage pipeline that turns an artifact repo into a marketing story","id":"PRA-0001","issue_url":"https://github.com/Pukujan/PRD-agent/issues/5","next_action":"Execute Task 16 (PRA-0002) for the first real target run","owner":"Pukujan","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"completed","why":"Generated copy reads as an audit, so nothing gets explained to a stranger"} -->

- Status: completed
- Owner: Pukujan
- Priority: P1
- Depends on: none

## Goal

Build the four-stage pipeline that turns an artifact repo into a marketing story

## Why

Generated copy reads as an audit, so nothing gets explained to a stranger

## Allowed files

- `pyproject.toml`
- `README.md`
- `src/prd_agent/**`
- `tests/**`
- `docs/**`
- `.github/workflows/**`
- `checkpoints/**`
- `tasks/**`
- `evals/**`

## Human outcome

A builder can turn a repository artifact into marketing copy that reads like a stranger-facing product story with proof points and self-checks instead of a feature audit.

## Scope and boundaries

- In scope: 4-stage pipeline (intake -> trends -> positioning -> story), self-check against AI tells, interactive and autonomous modes, live web trend pass, and eval append/retrieval.
- Out of scope: Scraped trend corpus, semantic retrieval/embeddings, cross-run positioning memory (documented in `docs/CORPUS_SEAM.md`).
- Dependencies/uncertainty: Zero runtime dependencies. Live web search requires network or canned responses.

## Acceptance criteria

- [x] The four-stage pipeline runs over an artifact and produces story.md
- [x] Self-check runs against ai-tells rules and gates draft
- [x] Two execution modes (interactive and autonomous) run over one pipeline
- [x] Live trend pass analyzes competitors and market sophistication
- [x] Finished stories append to evals/story_evals.json and are retrieved by keyword overlap
- [x] Python test suite passes with zero network access and continuity validate is VALID

## Evidence and sources

- `python -m pytest -q`: 139 passed in ~9.5s with zero network access
- `continuity validate --root .`: VALID

## Reproduction details (only when needed)

Run `python -m pytest -q` from repository root.

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): Leaf issue https://github.com/Pukujan/PRD-agent/issues/5, parent: none, dependencies: none.
- Primary writer / branch / source issue revision / as-of status: Primary writer: Antigravity, branch: `task/PRA-0001-prd-agent-pipeline`, status: active.
- Related PR/CI evidence and push receipt (request ID / SHA): Pending PR creation and CI run.

## Checkpoint log

No checkpoints yet.

### 2026-10-14 05:01:35 UTC — Antigravity

<!-- continuity:checkpoint {"agent":"Antigravity","blocked":[],"changed":["src/prd_agent/, tests/, docs/CORPUS_SEAM.md, README.md, .github/workflows/prd-agent-tests.yml"],"completed":["The four-stage pipeline is implemented and tested: intake reads an artifact into claims.json, the live web pass produces trends.json, positioning derives the spine and runs the swap test in code, and the story stage drafts through the vendored copywriting skill, gates the draft against that skill's own self-check and appends the proof table, the flags and the self-check paragraph in code","The flag loop runs in two modes over one pipeline, and finished stories are appended as worked examples and retrieved by keyword overlap"],"decisions":["no new decisions"],"evidence":["python -m pytest -q: every test passes with no network access","continuity validate --root .: VALID","the vendored copywriting skill is MIT at commit 0f8d8996, recorded with SHA-256 hashes in src/prd_agent/vendor/copywriting/PROVENANCE.md"],"next_action":"Open the pull request, wait for the gates check, then merge","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PRA-0001","timestamp":"2026-10-14T05:01:35Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"d84ce308e7dfde1adaec481927ac440d074ea8eef1dd09fe09b19029bfe4abda","request_id":"2a8bd6d62722463f8fa2a901da9cb5ca","schema":"project-continuity.checkpoint-operation.v1","task_id":"PRA-0001"} -->

Completed:
- The four-stage pipeline is implemented and tested: intake reads an artifact into claims.json, the live web pass produces trends.json, positioning derives the spine and runs the swap test in code, and the story stage drafts through the vendored copywriting skill, gates the draft against that skill's own self-check and appends the proof table, the flags and the self-check paragraph in code
- The flag loop runs in two modes over one pipeline, and finished stories are appended as worked examples and retrieved by keyword overlap

Evidence:
- python -m pytest -q: every test passes with no network access
- continuity validate --root .: VALID
- the vendored copywriting skill is MIT at commit 0f8d8996, recorded with SHA-256 hashes in src/prd_agent/vendor/copywriting/PROVENANCE.md

Decisions:
- no new decisions

Changed:
- src/prd_agent/, tests/, docs/CORPUS_SEAM.md, README.md, .github/workflows/prd-agent-tests.yml

Blocked/uncertain:
- none

Next:
- Open the pull request, wait for the gates check, then merge

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
