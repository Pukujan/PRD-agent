# TASK-PRA-0008 — Persona Launch Pack

<!-- continuity:task {"acceptance":["python -m pytest tests/test_persona.py passes all persona calibration and normalization tests","python -m pytest tests/test_pack.py passes multi-asset generation tests across all formats","python -m pytest passes all unit and integration tests cleanly","--persona parses canonical personas (solopreneur, enterprise, normie) and aliases","interactive mode prompts for persona selection when --persona is omitted in interactive mode","--pack generates copy.json, launch_thread.md, show_hn.md, and pitch_deck.md under runs/<target>/pack/","all generated launch pack assets strictly ban em-dashes and enforce active hype calibration"],"depends_on":[],"goal":"Add audience persona calibration and full multi-asset launch pack generation","id":"PRA-0008","issue_url":"https://github.com/Pukujan/PRD-agent/issues/20","next_action":"None","owner":"Pukujan","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"completed","why":"Builders need to target specific buyer personas (solopreneur, enterprise, normie) and generate the entire launch arsenal (landing page copy, viral threads, Show HN, pitch decks) in one run"} -->

- Status: completed
- Owner: Pukujan
- Priority: P1
- Depends on: none

## Goal

Add audience persona calibration and full multi-asset launch pack generation

## Why

Builders need to target specific buyer personas (solopreneur, enterprise, normie) and generate the entire launch arsenal (landing page copy, viral threads, Show HN, pitch decks) in one run

## Allowed files

- `src/prd_agent/persona.py`
- `src/prd_agent/pack.py`
- `src/prd_agent/hype.py`
- `src/prd_agent/cli.py`
- `src/prd_agent/pipeline.py`
- `src/prd_agent/positioning.py`
- `src/prd_agent/schemas.py`
- `src/prd_agent/story.py`
- `README.md`
- `skills/prd-agent/SKILL.md`
- `tests/test_persona.py`
- `tests/test_pack.py`
- `tests/test_cli.py`
- `tests/test_pipeline.py`

## Human outcome

Builders can target specific buyer personas (solopreneur, enterprise, normie) and generate an entire launch arsenal in one run: landing page copy deck, viral launch thread, Show HN / Product Hunt pitch, and 10-slide pitch deck narrative, fully calibrated to the chosen hype level with zero em-dashes.

## Scope and boundaries

- In scope:
  - Audience persona module `persona.py` defining 3 core personas (`solopreneur`, `enterprise`, `normie`) with aliases, descriptors, target anxieties, dream states, and prompt directives.
  - Interactive persona calibration prompt `ask_persona()` in interactive CLI mode when `--persona` is omitted.
  - Multi-asset launch pack module `pack.py` generating `copy.json`, `launch_thread.md`, `show_hn.md`, and `pitch_deck.md` under `runs/<target>/pack/`.
  - Integration into `pipeline.py` and `cli.py` with `--persona` and `--pack`.
  - Machine validation guaranteeing zero em-dashes (`—` / `--`) and adherence to the active hype tier across all generated assets.
- Out of scope:
  - Visual rendering engines (HTML/CSS templates, Marp compiler, PDF generators).
  - Social media API posting or automated account publishing.
  - Modifications to `.continuity/` protocol versions.

## Acceptance criteria

- [x] `python -m pytest tests/test_persona.py` passes all persona calibration and normalization tests.
- [x] `python -m pytest tests/test_pack.py` passes multi-asset generation tests across all formats.
- [x] `python -m pytest` passes all unit and integration tests cleanly.
- [x] `--persona` parses canonical personas (`solopreneur`, `enterprise`, `normie`) and aliases (`unicorn`, `cto`, `consumer`).
- [x] Interactive mode prompts for persona selection when `--persona` is omitted and interactive mode is active.
- [x] `--pack` generates `copy.json`, `launch_thread.md`, `show_hn.md`, and `pitch_deck.md` under `runs/<target>/pack/`.
- [x] All generated launch pack assets strictly ban em-dashes (`—` and `--`) and enforce the active hype calibration tier.

## Evidence and sources

- `python -m pytest -q`: 184 passed in 10.34s across all unit and integration test suites.
- `continuity validate --root .`: VALID.
- GitHub Issue: https://github.com/Pukujan/PRD-agent/issues/20.

## Related records

- Required leaf owning issue, parent ancestry and dependencies: leaf https://github.com/Pukujan/PRD-agent/issues/20, parent: none.

## Checkpoint log

No checkpoints yet.

### 2026-10-19 10:25:01 UTC — Antigravity

<!-- continuity:checkpoint {"agent":"Antigravity","blocked":[],"changed":["src/prd_agent/persona.py, src/prd_agent/pack.py, src/prd_agent/cli.py, src/prd_agent/pipeline.py, src/prd_agent/positioning.py, src/prd_agent/schemas.py, src/prd_agent/story.py, tests/, README.md, skills/prd-agent/SKILL.md"],"completed":["Added audience persona targeting module (src/prd_agent/persona.py) with solopreneur, enterprise, and normie presets, normalization, aliases, and interactive pre-generation calibration","Added multi-asset launch pack generator (src/prd_agent/pack.py) producing copy.json landing page copy deck, launch_thread.md viral X thread, show_hn.md launch narrative, and pitch_deck.md 10-slide narrative","Enforced strict zero em-dash policy and active hype tier calibration across all launch pack assets","Added --persona and --pack CLI arguments with interactive fallback"],"decisions":["no new decisions"],"evidence":["python -m pytest -q: 184 passed cleanly across all test suites","continuity validate --root .: VALID"],"next_action":"Open PR, verify CI checks, auto-merge to main, and publish leaf receipt","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PRA-0008","timestamp":"2026-10-19T10:25:01Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"f13f3d5439dd7c6421645aa0b1ad919dcff99cd14fb8d5644abec3bf91d47340","request_id":"5b91882a62674239891feb743a60cdc8","schema":"project-continuity.checkpoint-operation.v1","task_id":"PRA-0008"} -->

Completed:
- Added audience persona targeting module (src/prd_agent/persona.py) with solopreneur, enterprise, and normie presets, normalization, aliases, and interactive pre-generation calibration
- Added multi-asset launch pack generator (src/prd_agent/pack.py) producing copy.json landing page copy deck, launch_thread.md viral X thread, show_hn.md launch narrative, and pitch_deck.md 10-slide narrative
- Enforced strict zero em-dash policy and active hype tier calibration across all launch pack assets
- Added --persona and --pack CLI arguments with interactive fallback

Evidence:
- python -m pytest -q: 184 passed cleanly across all test suites
- continuity validate --root .: VALID

Decisions:
- no new decisions

Changed:
- src/prd_agent/persona.py, src/prd_agent/pack.py, src/prd_agent/cli.py, src/prd_agent/pipeline.py, src/prd_agent/positioning.py, src/prd_agent/schemas.py, src/prd_agent/story.py, tests/, README.md, skills/prd-agent/SKILL.md

Blocked/uncertain:
- none

Next:
- Open PR, verify CI checks, auto-merge to main, and publish leaf receipt

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
