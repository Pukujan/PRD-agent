# TASK-PRA-0010 — Repo Integrity And Belief Inversion

<!-- continuity:task {"acceptance":["python -m mypy src/ passes with 0 errors","python -m ruff check src/ tests/ passes with 0 errors",".continuity/documents.json is rendered and continuity validate --root . passes with zero warnings","prd-agent-tests.yml CI workflow enforces ruff and mypy","trends.py extracts false_dogma and rebellion_belief","positioning.py maps code features to weaponized_mechanisms","story.py and pack.py generate cultural sovereignty manifestos","all unit and integration tests pass cleanly"],"depends_on":[],"goal":"Arm repository maintenance gates (mypy, ruff, documents inventory) and build the dynamic belief inversion engine","id":"PRA-0010","issue_url":"https://github.com/Pukujan/PRD-agent/issues/24","next_action":"Commit product and docs, create pull request, verify CI checks, and merge.","owner":"Pukujan","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Ensure PRD-agent is a strictly maintained, type-safe, lint-clean codebase that produces cultural sovereignty manifestos"} -->

- Status: active
- Owner: Pukujan
- Priority: P1
- Depends on: none

## Goal

Arm repository maintenance gates (mypy, ruff, documents inventory) and build the dynamic belief inversion engine

## Why

Ensure PRD-agent is a strictly maintained, type-safe, lint-clean codebase that produces cultural sovereignty manifestos

## Allowed files

- `src/prd_agent/`
- `tests/`
- `pyproject.toml`
- `.github/workflows/prd-agent-tests.yml`
- `.continuity/`
- `.gitignore`
- `README.md`
- `skills/prd-agent/SKILL.md`

## Human outcome

Builders and maintainers have strict mechanical guarantees that the repository remains type-safe, lint-clean, and inventory-tracked in CI, while autonomous runs dynamically invert category dogmas to produce high-stakes, cultural sovereignty manifestos.

## Scope and boundaries

- In scope:
  - Fix all mypy type errors in `src/prd_agent/`.
  - Fix all ruff lint and import issues in `src/` and `tests/`.
  - Configure `pyproject.toml` with `dev` dependencies (`mypy`, `ruff`) and tool configs.
  - Initialize and render `.continuity/documents.json` inventory.
  - Update `.github/workflows/prd-agent-tests.yml` to run `ruff`, `mypy`, and `continuity validate`.
  - Upgrade `schemas.py`, `trends.py`, `positioning.py`, `story.py`, and `pack.py` with `false_dogma`, `rebellion_belief`, and `weaponized_mechanisms`.
- Out of scope:
  - Modifying `.content-system/`, `.coord/`, `stack-official` pins or `acs-gates.yml`.

## Acceptance criteria

- [x] `python -m mypy src/` passes with 0 errors.
- [x] `python -m ruff check src/ tests/` passes with 0 errors.
- [x] `.continuity/documents.json` is rendered and `continuity validate --root .` passes with zero warnings.
- [x] `prd-agent-tests.yml` CI workflow enforces ruff and mypy.
- [x] `trends.py` extracts `false_dogma` and `rebellion_belief`.
- [x] `positioning.py` maps code features to `weaponized_mechanisms`.
- [x] `story.py` and `pack.py` generate cultural sovereignty manifestos.
- [x] All unit and integration tests pass cleanly.

## Evidence and sources

- GitHub Issue: https://github.com/Pukujan/PRD-agent/issues/24.

## Related records

- Required leaf owning issue, parent ancestry and dependencies: leaf https://github.com/Pukujan/PRD-agent/issues/24, parent: none.


## Checkpoint log

No checkpoints yet.

### 2026-10-19 16:26:46 UTC — Antigravity

<!-- continuity:checkpoint {"agent":"Antigravity","blocked":[],"changed":["src/prd_agent/, tests/, pyproject.toml, .github/workflows/prd-agent-tests.yml, .continuity/documents.json, docs/CONTINUITY_INDEX.md, checkpoints/CURRENT.md, tasks/TASK-PRA-0010-repo-integrity-and-belief-inversion.md"],"completed":["Arm repository maintenance gates with mypy (0 errors), ruff lint/import enforcement (0 errors), and .continuity/documents.json inventory tracking (VALID)","Implement dynamic belief inversion engine extracting false_dogma and rebellion_belief in trends, weaponizing mechanisms in positioning, and enforcing 5-Beat Manifesto structure across story and launch pack"],"decisions":["no new decisions"],"evidence":["python -m mypy src/: Success (0 issues in 20 source files)","python -m ruff check src/ tests/: All checks passed (0 errors)","python -m pytest -q: 193 passed in 9.3s","continuity validate --root .: VALID"],"next_action":"Open pull request, verify CI checks, and merge to main","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PRA-0010","timestamp":"2026-10-19T16:26:46Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"fda2ae71a18e515967bb20ea837d05008961fd1ed378548b3def211c1bf60787","request_id":"e6508bdb92274b7d80abb91578c7b8db","schema":"project-continuity.checkpoint-operation.v1","task_id":"PRA-0010"} -->

Completed:
- Arm repository maintenance gates with mypy (0 errors), ruff lint/import enforcement (0 errors), and .continuity/documents.json inventory tracking (VALID)
- Implement dynamic belief inversion engine extracting false_dogma and rebellion_belief in trends, weaponizing mechanisms in positioning, and enforcing 5-Beat Manifesto structure across story and launch pack

Evidence:
- python -m mypy src/: Success (0 issues in 20 source files)
- python -m ruff check src/ tests/: All checks passed (0 errors)
- python -m pytest -q: 193 passed in 9.3s
- continuity validate --root .: VALID

Decisions:
- no new decisions

Changed:
- src/prd_agent/, tests/, pyproject.toml, .github/workflows/prd-agent-tests.yml, .continuity/documents.json, docs/CONTINUITY_INDEX.md, checkpoints/CURRENT.md, tasks/TASK-PRA-0010-repo-integrity-and-belief-inversion.md

Blocked/uncertain:
- none

Next:
- Open pull request, verify CI checks, and merge to main

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
