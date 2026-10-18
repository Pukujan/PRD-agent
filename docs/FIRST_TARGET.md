# First target: the ACS hot-loader repository

Status: run. Owner verdict: not yet given.

## What was run

`python -m prd_agent <hot-loader-root> --autonomous --out stories/acs-hot-loader.md`, on
2026-10-18, at artifact commit `aea4f1b`.

The target artifact is the owner's `agent-custom-setup` (ACS) repository, registered in the
continuity per-device workspace registry.

## What the run produced

- `stories/acs-hot-loader.md`
- `runs/acs-hot-loader/claims.json`
- `runs/acs-hot-loader/trends.json`
- `runs/acs-hot-loader/positioning.json`

The mechanism leads prominently. The hero headline names the hot-load mechanism directly rather
than the category's abstraction:

> `# Any number of agents on your repo, one boss on a 30-minute lease`
>
> `The decision seat fills by live join order, lapses on a clock, and reopens through a FIFO queue. A boss that goes stale loses the crown and rejoins at the back of the line.`

The story follows the Human Action Model beats cleanly:
- Current discomfort: "Two agents, one file, and no rule for who decides" (Cursor writes the migration, Codex rewrites the same schema, uncoordinated sessions wake up).
- Better vision: "The seat has a name, a clock, and a queue" (join-order roles, 30-minute lease, FIFO claim queue, agent-less watchdog).
- Path to action: "Work moves as a proposal" and "Five steps to a repo with a boss on a clock".

The footer is built entirely in code:
- A proof table with 27 rows traced to specific repository files and lines (`modules/coordination/multi-agent-hotload/v0.1.0/README.md`, `.github/workflows/ci.yml`, `.github/scripts/oio_installer.py`, `.content-system/system-version.json`).
- Unknowns explicitly acknowledged rather than guessed (`benchmarks against rival hotloaders`, `exact CPU overhead of watchdog`).
- 8 machine-allocated `[NEED:]` flags carrying the exact evidence required to unlock harder claims.
- The self-check report passing with 0 hard bans in 6 sections and all structural beats present.

## What the run exposed

The live run on a production repository exposed three critical operational realities:

1. **Intake token exhaustion on real repositories (`src/prd_agent/intake.py` lines 23-46, `src/prd_agent/llm.py` line 24).**
   ACS contains 48 source and doc files (~400,000 bytes) within the artifact collector's limit. Because `_PROMPT_TEMPLATE` gave no target claim count or brevity constraint, Claude 3.5/4.5 attempted an exhaustive catalog of every detail. At output token 8,000 (`DEFAULT_MAX_TOKENS`), the output truncated mid-claim at `{"id": "C-028", "text": "The root README hero is a single narrative raster, 1280x`. `extract_json()` failed to parse the unclosed JSON string and raised `ModelOutputError: no JSON object could be parsed from the model response`, causing the CLI to exit with code 2. The first 27 claims were complete and valid once the unclosed array was closed.

2. **Web search tool output handling in non-native proxy environments (`src/prd_agent/trends.py` lines 63-65, `src/prd_agent/llm.py` line 161).**
   `trends.py` attaches `WEB_SEARCH_TOOL = {"type": "web_search_20250305", ...}`. When running through an OpenAI/LiteLLM proxy, the proxy executes DuckDuckGo and returns the raw tool result text (130,571 characters of snippets) inside a `text` block instead of streaming a synthesized completion. `extract_json()` found 130KB of prose search snippets and 0 JSON objects, failing the live trends pass. When decoupled or supplied with trends data, the downstream positioning and story generation succeeded immediately.

3. **Real artifact discrepancies caught by positioning (`stories/acs-hot-loader.md` lines 87-94).**
   Just as the PCM hand-run caught a version discrepancy, the automated run on ACS exposed real inconsistencies inside the artifact:
   - `HOTLOAD.md` asserts an 8-module required install including `human-output-naming`, while its table lists only 7 module rows (`[NEED: proof]` flag `N-006`).
   - `PROMPT_INJECT.md` pins CGM `0.5.12` at one commit while `.content-system/system-version.json` records a different commit for that version (`[NEED: differentiator]` flag `N-003`).
   - PCM CLI pin is `0.6.0` while `SPEC.md` references `0.7.0` (`N-003`).
   The pipeline refused to smooth over these contradictions and instead emitted named `[NEED:]` flags with exact unlock conditions.

## What this says about the design

1. **§6's acceptance criterion holds:** The core claim of the PRD-agent design — that an artifact repository can be turned into a mechanism-led marketing story without AI tells, with an auditable code-built proof footer, and with no invented facts — is validated on the owner's live ACS repository.
2. **Follow-up work required:** Two pipeline defects must be filed as follow-up issues per Step 7:
   - Intake prompt claim-count guideline to prevent exceeding `DEFAULT_MAX_TOKENS` on large artifacts.
   - Resilient trends web-search synthesis that handles tool-result text blocks from proxy providers.
