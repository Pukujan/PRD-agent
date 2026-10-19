# TASK-PRA-0012 — Universal Repo Pointing

<!-- continuity:task {"acceptance":["SDD: docs/superpowers/specs/2026-10-19-universal-repo-pointing.md defines remote intake and action spec","Remote URL Intake: src/prd_agent/remote.py shallow-clones remotes with automatic cleanup","CLI Remote Pointing: cli.py and pipeline.py accept remote Git URLs and output 5-line battle cry to stdout","Composite GitHub Action: action.yml validated and tested","TDD/BDD: All tests in tests/test_remote_repo.py pass cleanly; 207 total tests pass","Repository Health: 0 mypy errors, 0 ruff errors, continuity validate VALID"],"depends_on":[],"goal":"Enable pointing any repository directly to PRD-agent via remote URL intake and GitHub Action","id":"PRA-0012","issue_url":"https://github.com/Pukujan/PRD-agent/issues/28","next_action":"Commit product and docs, run continuity checkpoint, push branch, open PR, verify CI, auto-merge, and publish leaf receipt","owner":"Pukujan","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"External repos and blind agents need zero-setup intake without manual cloning"} -->

- Status: active
- Owner: Pukujan
- Priority: P1
- Depends on: none

## Goal

Enable pointing any repository directly to PRD-agent via remote URL intake and GitHub Action

## Why

External repos and blind agents need zero-setup intake without manual cloning

## Allowed files

- `src/prd_agent/`
- `tests/`
- `action.yml`
- `docs/superpowers/specs/2026-10-19-universal-repo-pointing.md`
- `skills/prd-agent/SKILL.md`
- `README.md`
- `checkpoints/CURRENT.md`
- `.continuity/`
- `docs/CONTINUITY_INDEX.md`

## Human outcome

Any external repository, developer, or blind agent can point directly to PRD-agent via remote GitHub URL intake (`prd-agent https://github.com/...`) or GitHub Action (`uses: Pukujan/PRD-agent@main`), generating marketing copy and READMEs with zero manual cloning or setup.

## Scope and boundaries

- In scope:
  - SDD spec in `docs/superpowers/specs/2026-10-19-universal-repo-pointing.md`.
  - Remote repository URL detection and shallow-cloning seam in `src/prd_agent/remote.py`.
  - CLI and pipeline integration supporting remote repository resolution, caller working directory outputs, and stdout streaming.
  - Root `action.yml` composite GitHub Action for CI/CD turnkey execution.
  - Unit and integration tests in `tests/test_remote_repo.py`.
  - Documentation in `README.md` and `skills/prd-agent/SKILL.md`.
- Out of scope:
  - Private Git credential storage or host management outside standard git credential helpers.

## Acceptance criteria

- [x] SDD: `docs/superpowers/specs/2026-10-19-universal-repo-pointing.md` defines remote intake and action spec.
- [x] Remote URL Intake: `src/prd_agent/remote.py` shallow-clones remotes with automatic cleanup.
- [x] CLI Remote Pointing: `cli.py` and `pipeline.py` accept remote Git URLs and output 5-line battle cry to stdout.
- [x] Composite GitHub Action: `action.yml` validated and tested.
- [x] TDD/BDD: All tests in `tests/test_remote_repo.py` pass cleanly; 207 total tests pass.
- [x] Repository Health: 0 mypy errors, 0 ruff errors, `continuity validate` VALID.

## Evidence and sources

Link repository state at a revision and cite external factual claims directly. Record commands and results for claims that need verification.

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
