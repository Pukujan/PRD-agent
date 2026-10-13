# PRD-agent Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the four-stage PRD-agent pipeline — `intake.py` → `trends.py` → `positioning.py` → `story.py` — as a zero-dependency Python package whose output is a marketing story that sells rather than audits, gated by a machine-runnable version of the copywriting skill's own self-check.

**Architecture:** Four stages pass plain JSON between them (`claims.json` → `trends.json` → `positioning.json` → `story.md`), one module per stage, written to `runs/<name>/` beside the story so any stage can be re-run alone. Every model call goes through one injected `LLM` seam (`complete(*, system, prompt, max_tokens, tools) -> str`), so the whole pipeline runs in tests with no network and no credentials. The model writes the **pitch body only**; the proof table, the `[NEED: ...]` flag footer, and the self-check paragraph are assembled by code from the stage JSON and the checker's report, so the page can never overclaim what was proved.

**Tech Stack:** Python 3.12 (stdlib only at runtime), `pytest` for tests, `argparse` for the CLI, `urllib.request` for the one optional network call. Vendored dependency: `coreyhaines31/marketingskills` `skills/copywriting` at commit `0f8d8996` (MIT), copied into the package and read at runtime.

**Spec:** `docs/superpowers/specs/2026-10-13-prd-agent-design.md`

## Global Constraints

- **Python floor:** `requires-python = ">=3.12"`; the dev machine has 3.12 at `C:\Users\pujan\AppData\Local\Programs\Python\Python312`. PCM (the sibling project) ships `>=3.11`; this project pins 3.12 because that is what is installed and tested here.
- **Runtime dependencies: none.** `dependencies = []`. `pytest` is the only dev dependency. Do not add `anthropic`, `httpx`, `requests`, `jsonschema`, or any embedding/vector library. The Anthropic call uses `urllib.request` from the standard library.
- **No network in tests.** Every stage function takes `llm: LLM` as a parameter. Tests pass `FakeLLM`. A test that touches the real API must be marked `@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), ...)`.
- **One model call per stage.** `story.py` adds a bounded rewrite loop: `MAX_REWRITES = 2`. A draft still tripping a ban after the last rewrite raises `StoryGateError` and writes nothing.
- **The footer is code.** `story.build_footer()` emits the proof table, the `[NEED: ...]` flags and the self-check paragraph. The model is told to emit the pitch body only. A model that writes a `[NEED: ...]` marker anyway is not punished: `clean_body()` strips it from the pitch and the flag joins the footer, so the pitch body can never carry the marker and the flag is never lost.
- **Hype is uncapped.** Invented-sounding numbers are allowed unless they contradict the artifact. The one surviving refusal: a claim that contradicts what the artifact is (a CLI is never sold as a GUI).
- **The market analysis stays behind the curtain.** Competitor inventory never enters the pitch body; it lives in the footer table and in `runs/<name>/trends.json`.
- **Intermediate JSON always lands in `runs/<name>/`** (`claims.json`, `trends.json`, `positioning.json`).
- **Vendoring copies files, never clones.** `git clone` of a dependency into the repo fails ACS dev-root hygiene (`hotload_check.py` refuses a dependency checkout inside the dev root). Use `cp`.
- **Do not touch:** `.content-system/`, `.coord/`, `stack-manifest.json`, `.oio/`, `.github/workflows/acs-gates.yml`, `schemas/v1/`, `checkpoints/`, `PROJECT.md`, `HANDOFF.md`. The `gates` check validates all of those and must keep passing.
- **Commits:** one logical change each, conventional prefix (`feat:`, `test:`, `docs:`, `fix:`, `chore:`).
- **Proposed cap values** (tunable, source `references/ai-tells.md` says 1–2 per page): fragments ≤ 1 per section, reflexive threes ≤ 1 per section, em dashes ≤ 1 per long-copy section, cap vocabulary ≤ 1 per section.
- **Normative build order (spec §8) is preserved.** Steps 3–5 run against a fixture `trends.json` and the live web pass is step 6. Within the plan the pipeline (step 5) is written before the live pass (step 6) and requires `--trends-file` until step 6 wires the network path; nothing in steps 3–5 ever reaches the network.

---

## File Structure

**Create (product):**

| Path | Responsibility |
|---|---|
| `pyproject.toml` | Package metadata, zero runtime deps, `pytest` dev extra, `pythonpath = ["src"]`, `prd-agent` console script |
| `.gitignore` | Ignore `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.venv/`, `*.egg-info/`, `build/`, `dist/` only |
| `README.md` | What the pipeline is, how to run it, the two modes, the LLM seam, the offline path |
| `src/prd_agent/__init__.py` | `__version__` |
| `src/prd_agent/__main__.py` | `python -m prd_agent` entry point |
| `src/prd_agent/errors.py` | `StageError`, `SchemaError`, `ModelOutputError`, `LLMUnavailable`, `StoryGateError` |
| `src/prd_agent/llm.py` | The one model seam: `LLM` protocol, `AnthropicHTTPLLM`, `FakeLLM`, `CannedLLM`, `default_llm()`, `extract_json()` |
| `src/prd_agent/skill.py` | Loads the vendored `copywriting` skill and its references from disk at runtime |
| `src/prd_agent/schemas.py` | Declarative field specs and validators for the three JSON documents |
| `src/prd_agent/artifact.py` | Reads an artifact repo deterministically: files, git facts, truncation, what was skipped |
| `src/prd_agent/intake.py` | Prompt + parse + validate for `claims.json` (spec §3.1) |
| `src/prd_agent/flags.py` | Allocates, merges, renders and asks about `[NEED: ...]` flags; the storyboard loop's data |
| `src/prd_agent/positioning.py` | Prompt + parse for `positioning.json`, plus the deterministic swap test (spec §3.3) |
| `src/prd_agent/checks.py` | The machine self-check: hard bans, frequency caps, structural beats, report and summary |
| `src/prd_agent/story.py` | Prompt assembly from the vendored skill, the draft/rewrite gate, the code-built footer |
| `src/prd_agent/trends.py` | The live web pass and sophistication staging (spec §3.2, step 6) |
| `src/prd_agent/evals.py` | Appends each finished story as a worked example; retrieves the best past ones |
| `src/prd_agent/pipeline.py` | One entry point over the four stages, the two modes, and the `runs/<name>/` writes |
| `src/prd_agent/cli.py` | `python -m prd_agent <artifact-path> [--autonomous] [--out ...]` and the offline flags |
| `src/prd_agent/vendor/__init__.py` | Marks the vendored tree as a package so `importlib.resources` can find it |
| `src/prd_agent/vendor/copywriting/SKILL.md` | Vendored copywriting skill (upstream `0f8d8996`) |
| `src/prd_agent/vendor/copywriting/references/ai-tells.md` | Vendored; the rule source for `checks.py` |
| `src/prd_agent/vendor/copywriting/references/copy-frameworks.md` | Vendored; the Human Action Model and headline formulas |
| `src/prd_agent/vendor/copywriting/references/natural-transitions.md` | Vendored; `SKILL.md` links it, so the link must resolve |
| `src/prd_agent/vendor/copywriting/evals/evals.json` | Vendored; the eval shape `evals.py` appends in |
| `src/prd_agent/vendor/copywriting/LICENSE` | MIT licence text, required by the licence |
| `src/prd_agent/vendor/copywriting/PROVENANCE.md` | Upstream repo, commit, licence, retrieval date, SHA-256 of every vendored file |

**Create (tests and fixtures):**

| Path | Responsibility |
|---|---|
| `tests/conftest.py` | Session fixtures: `repo_root`, `pcm_run`, `pcm_story` |
| `tests/test_skill.py` | The vendored tree loads and matches its recorded hashes |
| `tests/test_llm.py` | Fake/canned providers, request shape, `extract_json` |
| `tests/test_schemas.py` | Validators accept `runs/pcm/*.json` and reject broken documents |
| `tests/test_artifact.py` | Collection, git facts, truncation, skipped-file reporting |
| `tests/test_intake.py` | `intake()` against a fake model and the reference claims fixture |
| `tests/test_flags.py` | Flag ids, merging, rendering, the ask loop |
| `tests/test_positioning.py` | Swap test both directions, calibrated on the reference run |
| `tests/test_checks.py` | Every ban, every cap, the scope exemptions, the reference story |
| `tests/test_story.py` | Draft, gate, rewrite, fail-closed, footer assembly |
| `tests/test_pipeline.py` | Stage order, `runs/` writes, human vs autonomous |
| `tests/test_cli.py` | Argument parsing and one end-to-end offline run |
| `tests/test_trends.py` | The live pass prompt, schema, `searched_at`, fixture parity |
| `tests/test_evals.py` | Append, id sequence, retrieval, prompt injection |
| `tests/fixtures/artifact-mini/` | Tiny fake artifact (README, pyproject, one module, one test) |
| `tests/fixtures/trends_pcm.json` | Copy of `runs/pcm/trends.json` for steps 3–5 |
| `.github/workflows/prd-agent-tests.yml` | Runs `pytest` on 3.12; additive, does not touch `acs-gates.yml` |

**Modify:**

| Path | Change |
|---|---|
| `stories/pcm.md` | One line of the hand run rewritten so the reference story clears the checker (Task 8) |
| `checkpoints/CURRENT.md`, `HANDOFF.md`, `tasks/` | Per the continuity contract at each increment boundary (Task 0 sets this up) |

---

## Task 0: Task setup (GitHub issue, task projection, branch)

**Files:**
- Create: `tasks/TASK-PRA-0001-*.md` (via the `continuity` CLI)
- Modify: `checkpoints/CURRENT.md` (via the `continuity` CLI)

**Interfaces:**
- Consumes: nothing.
- Produces: an open GitHub issue URL, a task ID of the form `PRA-0001`, a task branch, and the working tree every later task commits into.

- [ ] **Step 1: Confirm nothing is already in flight**

```bash
cd /d/development/PRD-agent
git fetch --quiet origin
git status --short
cat checkpoints/CURRENT.md
```

Expected: a clean tree, and `CURRENT.md` still saying `active_task: null` with next action "Create or identify the GitHub issue".

- [ ] **Step 2: Create the owning GitHub issue**

The issue owns scope and lifecycle. Write it in the core tier of `issue-log-format 1.2.0`: problem, consequence, what changes, lineage, acceptance, boundaries, one next action.

```bash
ISSUE_URL=$(gh issue create --repo Pukujan/PRD-agent \
  --title "Build the four-stage PRD-agent pipeline so artifact repos produce a story that sells" \
  --body "$(cat <<'EOF'
A builder's own repositories, tools and demos exist, but the marketing copy generated from
them reads as an audit: an inventory of what the product does and what it lacks. The
consequence is that nothing gets explained to a stranger in a way that makes them want it.

This issue delivers the pipeline the design already specifies: intake reads the artifact
into `claims.json`, a live web pass produces `trends.json`, positioning derives a spine and
a swap-tested differentiator, and the story stage drafts marketing copy through the vendored
copywriting skill and gates it against that skill's own self-check. Two modes run over one
pipeline: storyboarding with the owner, and autonomous.

Lineage: leaf issue, parent: none. Task ID PRA-0001. Primary writer: the owner's agent
session. Branch: `task/PRA-0001-prd-agent-pipeline`.

Acceptance (proposed): all stages run from `python -m prd_agent <artifact-path>`; steps 3-5
run with no network against a fixture `trends.json`; a draft tripping a hard ban fails and is
rewritten, and a draft still tripping one after two rewrites fails the run; the story footer
is assembled from the stage JSON and the checker report, not written by the model.

Boundaries: no scraped trend corpus, no embedding or vector retrieval, no hosted memory, no
changes to `.content-system/`, `.coord/`, `stack-official` pins or `acs-gates.yml`.

Next action: create the PRA-0001 task projection and branch, then start Task 1 of
`docs/superpowers/plans/2026-10-13-prd-agent-pipeline.md`.
EOF
)")
echo "$ISSUE_URL"
```

Expected: a printed issue URL.

- [ ] **Step 3: Create the task projection and branch**

```bash
continuity task new --root . \
  --slug prd-agent-pipeline \
  --goal "Build the four-stage pipeline that turns an artifact repo into a marketing story" \
  --why "Generated copy reads as an audit, so nothing gets explained to a stranger" \
  --owner "$(git config user.name)" --issue "$ISSUE_URL"
git checkout -b task/PRA-0001-prd-agent-pipeline
continuity validate --root .
```

Expected: `tasks/TASK-PRA-0001-prd-agent-pipeline.md` exists, `continuity validate` prints `VALID`.

- [ ] **Step 4: Note the working arrangement**

Work in the canonical checkout at `D:\development\PRD-agent` on this branch. Do not create a worktree by hand: AGENTS.md forbids worktrees inside the checkout and the ACS dev-root rule forbids worktrees in `D:\development`. If isolation becomes necessary, use `continuity worktree create PRA-0001`, which registers the tree properly. Push, checkpoint and the issue receipt happen at increment boundaries, not on every commit; the commits inside each task below are local.

---

## Task 1: Vendor the copywriting skill and stand up the package

**Files:**
- Create: `pyproject.toml`, `.gitignore`
- Create: `src/prd_agent/__init__.py`, `src/prd_agent/vendor/__init__.py`, `src/prd_agent/skill.py`
- Create: `src/prd_agent/vendor/copywriting/{SKILL.md,LICENSE,PROVENANCE.md,evals/evals.json,references/*.md}`
- Test: `tests/test_skill.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `prd_agent.skill.skill_root() -> Path`, `load_skill() -> str`, `load_references(names: tuple[str, ...] = REFERENCE_FILES) -> dict[str, str]`, `build_skill_context(names: tuple[str, ...] = REFERENCE_FILES) -> str`, and the constant `REFERENCE_FILES`.

- [ ] **Step 1: Copy the pinned skill into the package**

Never clone; copy the files.

```bash
mkdir -p src/prd_agent/vendor/copywriting/references src/prd_agent/vendor/copywriting/evals
SRC=/c/Users/pujan/AppData/Local/acs/deps/marketingskills/skills/copywriting
DST=src/prd_agent/vendor/copywriting
cp "$SRC/SKILL.md" "$DST/SKILL.md"
cp "$SRC/references/ai-tells.md" "$DST/references/ai-tells.md"
cp "$SRC/references/copy-frameworks.md" "$DST/references/copy-frameworks.md"
cp "$SRC/references/natural-transitions.md" "$DST/references/natural-transitions.md"
cp "$SRC/evals/evals.json" "$DST/evals/evals.json"
cp /c/Users/pujan/AppData/Local/acs/deps/marketingskills/LICENSE "$DST/LICENSE"
ls -R "$DST"
```

Expected: six files plus the two new directories.

- [ ] **Step 2: Write `PROVENANCE.md` with the recorded hashes**

```bash
python - <<'PY'
import hashlib, pathlib
root = pathlib.Path("src/prd_agent/vendor/copywriting")
for path in sorted(root.rglob("*")):
    if path.is_file() and path.name != "PROVENANCE.md":
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"{digest}  {path.relative_to(root).as_posix()}")
PY
```

Paste the printed lines into `src/prd_agent/vendor/copywriting/PROVENANCE.md` under a `## SHA-256` heading, above this header:

```markdown
# Provenance

- Upstream: https://github.com/coreyhaines31/marketingskills
- Path in upstream: skills/copywriting
- Commit: 0f8d8996
- Licence: MIT (see LICENSE)
- Retrieved: 2026-10-13
- Vendored by: PRD-agent PRA-0001

This copy is read at runtime by `prd_agent.skill`. The hashes below are checked by
`tests/test_skill.py`, so an edit to a vendored file fails the suite until the hash is
updated deliberately.
```

- [ ] **Step 3: Write the failing test**

```python
# tests/test_skill.py
from __future__ import annotations

import hashlib
from pathlib import Path

from prd_agent import skill


def test_skill_and_references_load_from_the_package() -> None:
    context = skill.build_skill_context()
    assert "No AI Tells" in context
    assert "The Self-Check" in context
    assert "The Human Action Model" in context
    assert context.count("# Vendored reference:") == len(skill.REFERENCE_FILES)


def test_recorded_hashes_match_the_vendored_files() -> None:
    root = skill.skill_root()
    provenance = (root / "PROVENANCE.md").read_text(encoding="utf-8")
    recorded = {
        line.split()[1]: line.split()[0]
        for line in provenance.splitlines()
        if len(line.split()) == 2 and len(line.split()[0]) == 64
    }
    assert recorded, "PROVENANCE.md records no hashes"
    for relative, digest in recorded.items():
        actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        assert actual == digest, f"{relative} changed since it was vendored"


def test_reference_files_exist() -> None:
    for name in skill.REFERENCE_FILES:
        assert (skill.skill_root() / name).is_file(), name
```

- [ ] **Step 4: Run it and watch it fail**

Run: `python -m pytest tests/test_skill.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent'`.

- [ ] **Step 5: Write `pyproject.toml`, `.gitignore`, the package markers and `skill.py`**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "prd-agent"
version = "0.1.0"
description = "Turn a builder's own artifacts into a product story that sells"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8"]

[project.scripts]
prd-agent = "prd_agent.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"prd_agent.vendor" = ["copywriting/**/*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

```gitignore
__pycache__/
*.pyc
.pytest_cache/
.venv/
*.egg-info/
build/
dist/
```

```python
# src/prd_agent/__init__.py
"""PRD-agent: turn a builder's own artifacts into a product story that sells."""

__version__ = "0.1.0"
```

```python
# src/prd_agent/vendor/__init__.py
"""Vendored third-party skills, read at runtime. See copywriting/PROVENANCE.md."""
```

```python
# src/prd_agent/skill.py
"""Load the vendored copywriting skill from disk.

The skill is an instruction document written for a model, not a library, so the pipeline
reads it at runtime and puts it in the system prompt. Reading it from disk rather than
inlining it keeps the vendored copy the single source of truth.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

SKILL_DIR = "copywriting"
SKILL_FILE = "SKILL.md"
REFERENCE_FILES: tuple[str, ...] = (
    "references/ai-tells.md",
    "references/copy-frameworks.md",
    "references/natural-transitions.md",
)


def skill_root() -> Path:
    """The vendored skill directory, resolved inside the installed package."""
    return Path(str(files("prd_agent.vendor"))) / SKILL_DIR


def load_skill() -> str:
    return (skill_root() / SKILL_FILE).read_text(encoding="utf-8")


def load_references(names: tuple[str, ...] = REFERENCE_FILES) -> dict[str, str]:
    return {name: (skill_root() / name).read_text(encoding="utf-8") for name in names}


def build_skill_context(names: tuple[str, ...] = REFERENCE_FILES) -> str:
    """The system-prompt text handed to the model: the skill, then its references."""
    parts = [f"# Vendored skill: copywriting ({SKILL_FILE})\n\n{load_skill()}"]
    for name, text in load_references(names).items():
        parts.append(f"\n\n# Vendored reference: {name}\n\n{text}")
    return "".join(parts)
```

- [ ] **Step 6: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_skill.py -v`
Expected: 3 passed.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .gitignore src/prd_agent tests/test_skill.py
git commit -m "feat: vendor the copywriting skill and stand up the prd_agent package"
```

---

## Task 2: The LLM seam

**Files:**
- Create: `src/prd_agent/errors.py`, `src/prd_agent/llm.py`
- Test: `tests/test_llm.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `StageError`, `SchemaError`, `ModelOutputError`, `LLMUnavailable`, `StoryGateError`; `LLM` protocol with `complete(*, system: str, prompt: str, max_tokens: int = 8000, tools: list[dict] | None = None) -> str`; `FakeLLM(responses: list[str] | str)` with a `calls` list; `CannedLLM(directory: Path)`; `AnthropicHTTPLLM(model=..., api_key=..., max_tokens=..., base_url=..., timeout=...)` with `build_request(...)` and `complete(...)`; `extract_json(text: str) -> dict`; `default_llm() -> LLM`; `WEB_SEARCH_TOOL`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_llm.py
from __future__ import annotations

import json
import urllib.error
from pathlib import Path

import pytest

from prd_agent import llm


def test_fake_llm_returns_scripted_responses_in_order() -> None:
    fake = llm.FakeLLM(["first", "second"])
    assert fake.complete(system="s", prompt="p") == "first"
    assert fake.complete(system="s", prompt="p") == "second"
    assert [call["prompt"] for call in fake.calls] == ["p", "p"]


def test_fake_llm_fails_loudly_when_the_script_runs_out() -> None:
    fake = llm.FakeLLM([])
    with pytest.raises(llm.StageError):
        fake.complete(system="s", prompt="p")


def test_extract_json_handles_bare_fenced_and_prose_wrapped_objects() -> None:
    assert llm.extract_json('{"a": 1}') == {"a": 1}
    assert llm.extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert llm.extract_json('Here it is:\n\n{"a": 1}\n\nDone.') == {"a": 1}


def test_extract_json_rejects_a_response_with_no_object() -> None:
    with pytest.raises(llm.ModelOutputError):
        llm.extract_json("I could not do that.")


def test_request_carries_the_key_the_version_and_the_search_tool() -> None:
    client = llm.AnthropicHTTPLLM(model="m", api_key="k")
    url, headers, body = client.build_request(system="sys", prompt="hi", tools=[llm.WEB_SEARCH_TOOL])
    assert url.endswith("/v1/messages")
    assert headers["x-api-key"] == "k"
    assert headers["anthropic-version"] == llm.ANTHROPIC_VERSION
    payload = json.loads(body)
    assert payload["system"] == "sys"
    assert payload["messages"] == [{"role": "user", "content": "hi"}]
    assert payload["tools"] == [llm.WEB_SEARCH_TOOL]


def test_request_omits_tools_when_none_are_asked_for() -> None:
    client = llm.AnthropicHTTPLLM(model="m", api_key="k")
    _, _, body = client.build_request(system="s", prompt="p")
    assert "tools" not in json.loads(body)


def test_complete_reads_text_blocks_and_retries_a_server_error(monkeypatch) -> None:
    client = llm.AnthropicHTTPLLM(model="m", api_key="k")
    attempts = {"n": 0}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self) -> bytes:
            return json.dumps({"content": [{"type": "text", "text": "hello"}]}).encode()

    def fake_urlopen(request, timeout):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise urllib.error.HTTPError(request.full_url, 500, "boom", {}, None)
        return Response()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(llm.time, "sleep", lambda _seconds: None)
    assert client.complete(system="s", prompt="p") == "hello"
    assert attempts["n"] == 2


def test_complete_does_not_retry_a_client_error(monkeypatch) -> None:
    client = llm.AnthropicHTTPLLM(model="m", api_key="k")

    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 400, "bad", {}, None)

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(llm.StageError):
        client.complete(system="s", prompt="p")


def test_default_llm_requires_a_key(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("PRD_AGENT_LLM", raising=False)
    with pytest.raises(llm.LLMUnavailable):
        llm.default_llm()


def test_default_llm_returns_the_http_client_with_the_env_model(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.setenv("PRD_AGENT_MODEL", "some-model")
    client = llm.default_llm()
    assert isinstance(client, llm.AnthropicHTTPLLM)
    assert client.model == "some-model"


def test_default_llm_treats_a_blank_model_override_as_unset(monkeypatch) -> None:
    # An empty "model" field is a guaranteed 400 from the provider, so a blank
    # override must fall back to the built-in id rather than being sent.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.setenv("PRD_AGENT_MODEL", "   ")
    client = llm.default_llm()
    assert client.model == llm.DEFAULT_MODEL
    assert llm.DEFAULT_MODEL.strip()


def test_default_llm_can_be_switched_to_canned_responses(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "01.txt").write_text("first", encoding="utf-8")
    (tmp_path / "02.txt").write_text("second", encoding="utf-8")
    monkeypatch.setenv("PRD_AGENT_LLM", "fake")
    monkeypatch.setenv("PRD_AGENT_CANNED_DIR", str(tmp_path))
    client = llm.default_llm()
    assert client.complete(system="s", prompt="p") == "first"
    assert client.complete(system="s", prompt="p") == "second"
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python -m pytest tests/test_llm.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent.errors'`.

- [ ] **Step 3: Write the implementation**

```python
# src/prd_agent/errors.py
"""The failure vocabulary of the pipeline. Every stage failure is one of these."""

from __future__ import annotations


class StageError(Exception):
    """A stage could not complete. The run stops and reports this message."""


class SchemaError(StageError):
    """A stage document does not match its contract."""


class ModelOutputError(StageError):
    """The model returned something the stage cannot parse."""


class LLMUnavailable(StageError):
    """No model provider is configured, so the run cannot make a model call."""


class StoryGateError(StageError):
    """A draft still trips a banned pattern after the allowed rewrites."""
```

```python
# src/prd_agent/llm.py
"""The one place the pipeline talks to a model.

Every stage takes an `LLM`, so the whole pipeline runs in tests with no network and no
credentials. The only shipped provider is stdlib `urllib`, which keeps runtime dependencies
at zero.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Protocol

from prd_agent.errors import LLMUnavailable, ModelOutputError, StageError

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_MAX_TOKENS = 8000
RETRY_DELAY_SECONDS = 2.0
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504, 529})
WEB_SEARCH_TOOL: dict[str, object] = {"type": "web_search_20250305", "name": "web_search", "max_uses": 8}


class LLM(Protocol):
    def complete(
        self,
        *,
        system: str,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        tools: list[dict] | None = None,
    ) -> str: ...


class FakeLLM:
    """A scripted model for tests: returns queued responses and records every call."""

    def __init__(self, responses: list[str] | str) -> None:
        self._responses = [responses] if isinstance(responses, str) else list(responses)
        self.calls: list[dict[str, object]] = []

    def complete(
        self,
        *,
        system: str,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        tools: list[dict] | None = None,
    ) -> str:
        self.calls.append({"system": system, "prompt": prompt, "max_tokens": max_tokens, "tools": tools})
        if not self._responses:
            raise StageError("FakeLLM ran out of scripted responses")
        return self._responses.pop(0)


class CannedLLM:
    """Replays numbered text files in order, so a keyless smoke run can drive the pipeline."""

    def __init__(self, directory: Path) -> None:
        self._files = sorted(Path(directory).glob("*.txt"))
        if not self._files:
            raise StageError(f"no canned responses in {directory}")
        self._index = 0
        self.calls: list[dict[str, object]] = []

    def complete(
        self,
        *,
        system: str,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        tools: list[dict] | None = None,
    ) -> str:
        self.calls.append({"system": system, "prompt": prompt, "max_tokens": max_tokens, "tools": tools})
        if self._index >= len(self._files):
            raise StageError("CannedLLM ran out of canned responses")
        text = self._files[self._index].read_text(encoding="utf-8")
        self._index += 1
        return text


class AnthropicHTTPLLM:
    """The Anthropic Messages API over stdlib urllib."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        api_key: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        base_url: str = ANTHROPIC_URL,
        timeout: float = 300.0,
        attempts: int = 2,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.base_url = base_url
        self.timeout = timeout
        self.attempts = max(1, attempts)

    def build_request(
        self,
        *,
        system: str,
        prompt: str,
        max_tokens: int | None = None,
        tools: list[dict] | None = None,
    ) -> tuple[str, dict[str, str], bytes]:
        headers = {
            "content-type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
        }
        payload: dict[str, object] = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }
        if tools:
            payload["tools"] = tools
        return self.base_url, headers, json.dumps(payload).encode("utf-8")

    def complete(
        self,
        *,
        system: str,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        tools: list[dict] | None = None,
    ) -> str:
        url, headers, body = self.build_request(system=system, prompt=prompt, max_tokens=max_tokens, tools=tools)
        last_error: Exception | None = None
        for attempt in range(1, self.attempts + 1):
            request = urllib.request.Request(url, data=body, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                return extract_text(payload)
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code not in RETRYABLE_STATUS or attempt == self.attempts:
                    detail = (exc.read() or b"").decode("utf-8", "replace")[:500]
                    raise StageError(f"model call failed with HTTP {exc.code}: {detail}") from exc
                time.sleep(RETRY_DELAY_SECONDS * attempt)
            except (urllib.error.URLError, OSError) as exc:
                last_error = exc
                if attempt == self.attempts:
                    raise StageError(f"model call failed: {exc}") from exc
                time.sleep(RETRY_DELAY_SECONDS * attempt)
        raise StageError(f"model call failed: {last_error}")


def extract_text(payload: dict) -> str:
    """Join the text blocks of a Messages API response."""
    blocks = payload.get("content") or []
    parts = [
        str(block.get("text", ""))
        for block in blocks
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    text = "\n".join(part for part in parts if part).strip()
    if not text:
        raise ModelOutputError("the model response contained no text blocks")
    return text


def extract_json(text: str) -> dict:
    """Pull one JSON object out of a model reply, fenced or wrapped in prose."""
    candidates: list[str] = [block.strip() for block in re.findall(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])
    candidates.append(text.strip())
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise ModelOutputError("no JSON object could be parsed from the model response")


def default_llm() -> LLM:
    """The provider a real run uses: canned replay when asked, else the API."""
    if os.environ.get("PRD_AGENT_LLM", "").strip().lower() == "fake":
        directory = os.environ.get("PRD_AGENT_CANNED_DIR", "").strip()
        if not directory:
            raise LLMUnavailable("PRD_AGENT_LLM=fake needs PRD_AGENT_CANNED_DIR set to a directory of .txt files")
        return CannedLLM(Path(directory))
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise LLMUnavailable(
            "ANTHROPIC_API_KEY is not set, so no model call can be made. Export it, set "
            "PRD_AGENT_LLM=fake with PRD_AGENT_CANNED_DIR for an offline run, or inject an LLM."
        )
    return AnthropicHTTPLLM(
        model=os.environ.get("PRD_AGENT_MODEL", "").strip() or DEFAULT_MODEL,
        api_key=api_key,
        base_url=os.environ.get("ANTHROPIC_BASE_URL", ANTHROPIC_URL),
    )
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_llm.py -v`
Expected: 11 passed.

- [ ] **Step 5: Commit**

```bash
git add src/prd_agent/errors.py src/prd_agent/llm.py tests/test_llm.py
git commit -m "feat: add the injectable LLM seam with a stdlib Anthropic client and fakes"
```

---

## Task 3: The JSON contract

**Files:**
- Create: `src/prd_agent/schemas.py`, `tests/conftest.py`
- Test: `tests/test_schemas.py`

**Interfaces:**
- Consumes: `errors.SchemaError`.
- Produces: `CLAIMS_SPEC`, `TRENDS_SPEC`, `POSITIONING_SPEC`, `CLAIMS_SCHEMA`, `TRENDS_SCHEMA`, `POSITIONING_SCHEMA`, `CLAIM_STATUSES`, `SOPHISTICATION_STAGES`, `validate(doc, spec, path="$") -> list[str]`, `validate_claims(doc) -> list[str]`, `validate_trends(doc) -> list[str]`, `validate_positioning(doc) -> list[str]`, `require_valid(doc, spec, name) -> None`.

- [ ] **Step 1: Write the failing test**

```python
# tests/conftest.py
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def pcm_run(repo_root: Path) -> Path:
    return repo_root / "runs" / "pcm"


@pytest.fixture(scope="session")
def pcm_story(repo_root: Path) -> Path:
    return repo_root / "stories" / "pcm.md"
```

```python
# tests/test_schemas.py
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from prd_agent import schemas
from prd_agent.errors import SchemaError


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_reference_claims_document_validates(pcm_run: Path) -> None:
    assert schemas.validate_claims(load(pcm_run / "claims.json")) == []


def test_the_reference_trends_document_validates(pcm_run: Path) -> None:
    assert schemas.validate_trends(load(pcm_run / "trends.json")) == []


def test_the_reference_positioning_document_validates(pcm_run: Path) -> None:
    assert schemas.validate_positioning(load(pcm_run / "positioning.json")) == []


def test_a_missing_field_is_reported_with_its_path(pcm_run: Path) -> None:
    doc = load(pcm_run / "claims.json")
    del doc["artifact"]["commit"]
    problems = schemas.validate_claims(doc)
    assert "$.artifact.commit: missing" in problems


def test_an_unknown_claim_status_is_rejected(pcm_run: Path) -> None:
    doc = copy.deepcopy(load(pcm_run / "claims.json"))
    doc["claims"][0]["status"] = "probably"
    problems = schemas.validate_claims(doc)
    assert any("status" in problem and "probably" in problem for problem in problems)


def test_an_unexpected_field_is_rejected(pcm_run: Path) -> None:
    doc = copy.deepcopy(load(pcm_run / "trends.json"))
    doc["vibes"] = "good"
    problems = schemas.validate_trends(doc)
    assert "$.vibes: unexpected field" in problems


def test_an_unknown_sophistication_stage_is_rejected(pcm_run: Path) -> None:
    doc = copy.deepcopy(load(pcm_run / "trends.json"))
    doc["category"]["sophistication_stage"] = "vibes"
    problems = schemas.validate_trends(doc)
    assert any("sophistication_stage" in problem for problem in problems)


def test_require_valid_raises_with_a_readable_message(pcm_run: Path) -> None:
    doc = load(pcm_run / "positioning.json")
    doc["swap_test"]["passed"] = "yes"
    with pytest.raises(SchemaError) as error:
        schemas.require_valid(doc, schemas.POSITIONING_SPEC, "positioning.json")
    assert "positioning.json" in str(error.value)
    assert "swap_test.passed" in str(error.value)
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python -m pytest tests/test_schemas.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent.schemas'`.

- [ ] **Step 3: Write the implementation**

The spec's §3.2 shape omits `category.stage_note`, which the hand-executed run added and which the story stage needs (it carries the reasoning for the sophistication stage). It is required here; that extension is deliberate.

```python
# src/prd_agent/schemas.py
"""Structural validation for the JSON the pipeline passes between stages.

The field specs below are the single source of truth for the contract. There is no JSON
Schema file and no jsonschema dependency: a second copy of the contract would be a second
thing to keep in sync.
"""

from __future__ import annotations

from typing import Any

from prd_agent.errors import SchemaError

CLAIMS_SCHEMA = "prd-agent.claims.v1"
TRENDS_SCHEMA = "prd-agent.trends.v1"
POSITIONING_SCHEMA = "prd-agent.positioning.v1"
CLAIM_STATUSES = ("verified", "claimed", "unknown")
SOPHISTICATION_STAGES = ("virgin", "crowded", "jaded", "exhausted")

CLAIMS_SPEC: dict[str, Any] = {
    "schema": f"const:{CLAIMS_SCHEMA}",
    "artifact": {"name": "str", "path": "str", "commit": "str", "read_at": "str"},
    "claims": (
        "list",
        {
            "id": "str",
            "text": "str",
            "status": "enum:" + "|".join(CLAIM_STATUSES),
            "evidence": "str",
            "note": "str",
        },
    ),
    "unknowns": "list[str]",
}

TRENDS_SPEC: dict[str, Any] = {
    "schema": f"const:{TRENDS_SCHEMA}",
    "category": {
        "competitors": (
            "list",
            {"name": "str", "url": "str", "claim": "str", "language": "list[str]"},
        ),
        "sophistication_stage": "enum:" + "|".join(SOPHISTICATION_STAGES),
        "stage_note": "str",
    },
    "style": {"register": "str", "notes": "list[str]"},
    "cultural": ("list", {"moment": "str", "url": "str", "relevance": "str"}),
    "searched_at": "str",
}

POSITIONING_SPEC: dict[str, Any] = {
    "schema": f"const:{POSITIONING_SCHEMA}",
    "audience": {"who": "str", "situation": "str", "trigger": "str"},
    "discomfort": "str",
    "vision": "str",
    "path": "str",
    "alternative": "str",
    "differentiator": "str",
    "swap_test": {"passed": "bool", "note": "str"},
    "flags": ("list", {"id": "str", "need": "str", "claim": "str", "unlock": "str"}),
}


def validate(doc: Any, spec: Any, path: str = "$") -> list[str]:
    """Return a list of human-readable problems; an empty list means valid."""
    if isinstance(spec, tuple):
        _, item_spec = spec
        if not isinstance(doc, list):
            return [f"{path}: expected a list, got {type(doc).__name__}"]
        problems: list[str] = []
        for index, item in enumerate(doc):
            problems.extend(validate(item, item_spec, f"{path}[{index}]"))
        return problems

    if isinstance(spec, dict):
        if not isinstance(doc, dict):
            return [f"{path}: expected an object, got {type(doc).__name__}"]
        problems = []
        for key, sub_spec in spec.items():
            if key not in doc:
                problems.append(f"{path}.{key}: missing")
            else:
                problems.extend(validate(doc[key], sub_spec, f"{path}.{key}"))
        for key in doc:
            if key not in spec:
                problems.append(f"{path}.{key}: unexpected field")
        return problems

    if spec.startswith("const:"):
        expected = spec.split(":", 1)[1]
        return [] if doc == expected else [f"{path}: expected {expected!r}, got {doc!r}"]

    if spec.startswith("enum:"):
        allowed = spec.split(":", 1)[1].split("|")
        return [] if doc in allowed else [f"{path}: expected one of {allowed}, got {doc!r}"]

    if spec == "str":
        return [] if isinstance(doc, str) and doc.strip() else [f"{path}: expected a non-empty string"]

    if spec == "bool":
        return [] if isinstance(doc, bool) else [f"{path}: expected a boolean, got {doc!r}"]

    if spec == "list[str]":
        ok = isinstance(doc, list) and all(isinstance(item, str) for item in doc)
        return [] if ok else [f"{path}: expected a list of strings"]

    return [f"{path}: unknown spec {spec!r}"]


def validate_claims(doc: Any) -> list[str]:
    return validate(doc, CLAIMS_SPEC)


def validate_trends(doc: Any) -> list[str]:
    return validate(doc, TRENDS_SPEC)


def validate_positioning(doc: Any) -> list[str]:
    return validate(doc, POSITIONING_SPEC)


def require_valid(doc: Any, spec: Any, name: str) -> None:
    problems = validate(doc, spec)
    if problems:
        raise SchemaError(f"{name} failed validation: " + "; ".join(problems[:10]))
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_schemas.py -v`
Expected: 8 passed. If `test_the_reference_trends_document_validates` fails, the reference `runs/pcm/trends.json` has a key the spec above does not list: read the file, decide whether the key belongs in the contract, and add it to `TRENDS_SPEC` rather than loosening `validate`.

- [ ] **Step 5: Commit**

```bash
git add src/prd_agent/schemas.py tests/conftest.py tests/test_schemas.py
git commit -m "feat: define and validate the three stage JSON contracts"
```

---

## Task 4: Read the artifact

**Files:**
- Create: `src/prd_agent/artifact.py`
- Create: `tests/fixtures/artifact-mini/{README.md,pyproject.toml,src/mini.py,tests/test_mini.py}`
- Test: `tests/test_artifact.py`

**Interfaces:**
- Consumes: `errors.StageError`.
- Produces: `SourceFile(path: str, text: str)`, `Artifact(root, name, commit, read_at, files, skipped, commit_subjects)`, `collect_artifact(root, *, max_file_bytes=..., max_total_bytes=..., max_files=...) -> Artifact`, `git_commit(root) -> str`, `git_subjects(root, limit=50) -> list[str]`, `render_artifact(artifact) -> str`, and the constants `MAX_FILE_BYTES`, `MAX_TOTAL_BYTES`, `MAX_FILES`, `SKIP_DIRS`, `ENTRY_NAMES`, `TEXT_SUFFIXES`.

- [ ] **Step 1: Write the fixture artifact**

```markdown
<!-- tests/fixtures/artifact-mini/README.md -->
# mini

A tiny stand-in artifact used by the artifact reader tests.
```

```toml
# tests/fixtures/artifact-mini/pyproject.toml
[project]
name = "mini"
version = "0.1.0"
dependencies = []
```

```python
# tests/fixtures/artifact-mini/src/mini.py
def greet(name: str) -> str:
    return f"hello {name}"
```

```python
# tests/fixtures/artifact-mini/tests/test_mini.py
from mini import greet


def test_greet() -> None:
    assert greet("world") == "hello world"
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_artifact.py
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from prd_agent import artifact as artifact_module

FIXTURE = Path(__file__).parent / "fixtures" / "artifact-mini"


def make_repo(tmp_path: Path, name: str = "mini") -> Path:
    root = tmp_path / name
    shutil.copytree(FIXTURE, root)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "-C", root, "config", "user.email", "fixture@example.invalid"], check=True)
    subprocess.run(["git", "-C", root, "config", "user.name", "Fixture"], check=True)
    subprocess.run(["git", "-C", root, "add", "."], check=True)
    subprocess.run(["git", "-C", root, "commit", "-qm", "first commit"], check=True)
    return root


def test_collects_entry_files_first_and_records_git_facts(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    collected = artifact_module.collect_artifact(root)
    assert collected.name == "mini"
    assert collected.commit != "unknown"
    assert len(collected.commit) >= 7
    assert collected.commit_subjects[0] == "first commit"
    assert collected.files[0].path == "README.md"
    assert "pyproject.toml" in [item.path for item in collected.files]
    assert "src/mini.py" in [item.path for item in collected.files]
    assert collected.skipped == ()


def test_a_repository_with_no_commits_reports_an_unknown_commit(tmp_path: Path) -> None:
    root = tmp_path / "empty"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    collected = artifact_module.collect_artifact(root)
    assert collected.commit == "unknown"


def test_a_large_file_is_skipped_and_the_reason_is_recorded(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    (root / "big.md").write_text("x" * 5000, encoding="utf-8")
    collected = artifact_module.collect_artifact(root, max_file_bytes=1000)
    assert "big.md" not in [item.path for item in collected.files]
    assert any("big.md" in reason and "too large" in reason for reason in collected.skipped)


def test_the_total_budget_stops_collection_and_says_so(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    for index in range(6):
        (root / f"note{index}.md").write_text("y" * 400, encoding="utf-8")
    collected = artifact_module.collect_artifact(root, max_total_bytes=900)
    assert sum(len(item.text.encode("utf-8")) for item in collected.files) <= 900
    assert any("budget" in reason for reason in collected.skipped)


def test_binary_and_ignored_directories_are_never_read(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    (root / "node_modules").mkdir()
    (root / "node_modules" / "huge.md").write_text("z" * 5000, encoding="utf-8")
    (root / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    collected = artifact_module.collect_artifact(root)
    paths = [item.path for item in collected.files]
    assert not any("node_modules" in path for path in paths)
    assert "logo.png" not in paths


def test_render_artifact_includes_the_facts_the_model_needs(tmp_path: Path) -> None:
    collected = artifact_module.collect_artifact(make_repo(tmp_path))
    rendered = artifact_module.render_artifact(collected)
    assert "first commit" in rendered
    assert collected.commit in rendered
    assert "def greet" in rendered
```

- [ ] **Step 3: Run it and watch it fail**

Run: `python -m pytest tests/test_artifact.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent.artifact'`.

- [ ] **Step 4: Write the implementation**

```python
# src/prd_agent/artifact.py
"""Read an artifact repository deterministically, before any model sees it.

This module makes no model call. It collects what exists, truncates what is too large, and
records what it skipped, so the intake stage can never invent a mechanism the artifact does
not carry.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

TEXT_SUFFIXES = (
    ".md", ".markdown", ".txt", ".rst", ".py", ".toml", ".json", ".jsonl", ".yaml", ".yml",
    ".cfg", ".ini", ".sh", ".bash", ".ps1", ".js", ".ts", ".tsx", ".go", ".rs", ".java",
    ".c", ".h", ".cpp", ".sql", ".html", ".css",
)
SKIP_DIRS = frozenset(
    {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".mypy_cache",
     ".pytest_cache", ".ruff_cache", ".idea", ".vscode"}
)
ENTRY_NAMES = (
    "README.md", "README.rst", "README", "pyproject.toml", "package.json", "Cargo.toml",
    "go.mod", "setup.py", "Makefile", "AGENTS.md", "PROJECT.md",
)
MAX_FILE_BYTES = 200_000
MAX_TOTAL_BYTES = 400_000
MAX_FILES = 120
SUBJECT_LIMIT = 50


@dataclass(frozen=True)
class SourceFile:
    path: str
    text: str


@dataclass(frozen=True)
class Artifact:
    root: Path
    name: str
    commit: str
    read_at: str
    files: tuple[SourceFile, ...]
    skipped: tuple[str, ...]
    commit_subjects: tuple[str, ...]

    @property
    def total_bytes(self) -> int:
        return sum(len(item.text.encode("utf-8")) for item in self.files)


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def git_commit(root: Path) -> str:
    return _git(root, "rev-parse", "--short", "HEAD") or "unknown"


def git_subjects(root: Path, limit: int = SUBJECT_LIMIT) -> list[str]:
    output = _git(root, "log", f"-n{limit}", "--pretty=%s")
    return [line for line in output.splitlines() if line.strip()]


def _candidate_files(root: Path) -> tuple[list[str], list[str]]:
    """Return (readable relative paths, paths refused for being unreadable or ignored)."""
    readable: list[str] = []
    refused: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            refused.append(f"{relative} (not a text file)")
            continue
        readable.append(relative)
    return readable, refused


def _rank(relative: str) -> tuple[int, str]:
    name = Path(relative).name
    if name in ENTRY_NAMES:
        return (0, relative)
    if relative.startswith(("docs/", "doc/")):
        return (1, relative)
    if "test" in relative.lower():
        return (3, relative)
    return (2, relative)


def collect_artifact(
    root: Path,
    *,
    max_file_bytes: int = MAX_FILE_BYTES,
    max_total_bytes: int = MAX_TOTAL_BYTES,
    max_files: int = MAX_FILES,
) -> Artifact:
    root = Path(root).resolve()
    readable, skipped = _candidate_files(root)
    files: list[SourceFile] = []
    total = 0
    for relative in sorted(readable, key=_rank):
        if len(files) >= max_files:
            skipped.append(f"{relative} (file budget of {max_files} reached)")
            continue
        path = root / relative
        size = path.stat().st_size
        if size > max_file_bytes:
            skipped.append(f"{relative} (too large: {size} bytes)")
            continue
        if total + size > max_total_bytes:
            skipped.append(f"{relative} (total budget of {max_total_bytes} bytes reached)")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            skipped.append(f"{relative} (unreadable as text)")
            continue
        files.append(SourceFile(path=relative, text=text))
        total += size
    return Artifact(
        root=root,
        name=root.name,
        commit=git_commit(root),
        read_at=date.today().isoformat(),
        files=tuple(files),
        skipped=tuple(skipped),
        commit_subjects=tuple(git_subjects(root)),
    )


def render_artifact(artifact: Artifact) -> str:
    """The excerpt bundle handed to the model: the facts, then the files."""
    lines = [
        f"Artifact name: {artifact.name}",
        f"Artifact commit: {artifact.commit}",
        f"Read at: {artifact.read_at}",
        "",
        "Recent commit subjects:",
    ]
    lines.extend(f"- {subject}" for subject in artifact.commit_subjects)
    if artifact.skipped:
        lines.append("")
        lines.append("Not read (declare these as unread rather than guessing):")
        lines.extend(f"- {reason}" for reason in artifact.skipped)
    for item in artifact.files:
        lines.extend(["", f"----- FILE: {item.path} -----", item.text.rstrip()])
    return "\n".join(lines)
```

- [ ] **Step 5: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_artifact.py -v`
Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add src/prd_agent/artifact.py tests/test_artifact.py tests/fixtures/artifact-mini
git commit -m "feat: read an artifact repository deterministically with skip reporting"
```

---

## Task 5: Intake (spec §3.1, build order step 2)

**Files:**
- Create: `src/prd_agent/intake.py`
- Test: `tests/test_intake.py`

**Interfaces:**
- Consumes: `artifact.collect_artifact`, `artifact.render_artifact`, `artifact.Artifact`; `llm.LLM`, `llm.extract_json`; `schemas.validate_claims`, `schemas.require_valid`, `schemas.CLAIMS_SPEC`, `schemas.CLAIMS_SCHEMA`.
- Produces: `INTAKE_SYSTEM: str`, `build_intake_prompt(artifact) -> str`, `intake(root, llm, *, artifact=None) -> dict`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_intake.py
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prd_agent import intake
from prd_agent.errors import ModelOutputError, SchemaError
from prd_agent.llm import FakeLLM

FIXTURE = Path(__file__).parent / "fixtures" / "artifact-mini"


def make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "mini"
    shutil.copytree(FIXTURE, root)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "-C", root, "config", "user.email", "fixture@example.invalid"], check=True)
    subprocess.run(["git", "-C", root, "config", "user.name", "Fixture"], check=True)
    subprocess.run(["git", "-C", root, "add", "."], check=True)
    subprocess.run(["git", "-C", root, "commit", "-qm", "first commit"], check=True)
    return root


def reference_claims(pcm_run: Path) -> str:
    return (pcm_run / "claims.json").read_text(encoding="utf-8")


def test_the_prompt_carries_the_files_and_the_commit_subjects(tmp_path: Path) -> None:
    artifact = intake.collect_artifact(make_repo(tmp_path))
    prompt = intake.build_intake_prompt(artifact)
    assert "def greet" in prompt
    assert "first commit" in prompt
    assert "never invent a mechanism" in prompt.lower()


def test_intake_returns_a_document_that_matches_the_contract(tmp_path: Path, pcm_run: Path) -> None:
    fake = FakeLLM(reference_claims(pcm_run))
    doc = intake.intake(make_repo(tmp_path), fake)
    assert doc["schema"] == "prd-agent.claims.v1"
    assert len(doc["claims"]) == 12
    assert doc["artifact"]["name"] == "mini"
    assert doc["artifact"]["commit"] != "unknown"
    assert doc["artifact"]["path"].endswith("mini")


def test_intake_accepts_a_fenced_json_reply(tmp_path: Path, pcm_run: Path) -> None:
    fake = FakeLLM("```json\n" + reference_claims(pcm_run) + "\n```")
    assert intake.intake(make_repo(tmp_path), fake)["claims"]


def test_intake_rejects_a_reply_that_is_not_json(tmp_path: Path) -> None:
    with pytest.raises(ModelOutputError):
        intake.intake(make_repo(tmp_path), FakeLLM("I had a look and it seems fine."))


def test_intake_rejects_a_claim_with_no_status(tmp_path: Path, pcm_run: Path) -> None:
    doc = json.loads(reference_claims(pcm_run))
    del doc["claims"][0]["status"]
    with pytest.raises(SchemaError):
        intake.intake(make_repo(tmp_path), FakeLLM(json.dumps(doc)))


def test_intake_uses_the_supplied_artifact_without_re_reading(tmp_path: Path, pcm_run: Path) -> None:
    artifact = intake.collect_artifact(make_repo(tmp_path))
    doc = intake.intake(tmp_path / "nowhere", FakeLLM(reference_claims(pcm_run)), artifact=artifact)
    assert doc["artifact"]["name"] == "mini"
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python -m pytest tests/test_intake.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent.intake'`.

- [ ] **Step 3: Write the implementation**

```python
# src/prd_agent/intake.py
"""Turn an artifact into claims.json: what is pointed at, what the artifact asserts, what is not established.

Spec section 3.1. The stage never invents a plausible mechanism: an unread fact becomes an
`unknown` entry, and every claim carries the path, line or commit that supports it.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from prd_agent.artifact import Artifact, collect_artifact, render_artifact
from prd_agent.errors import ModelOutputError
from prd_agent.llm import LLM, extract_json
from prd_agent.schemas import CLAIMS_SCHEMA, CLAIMS_SPEC, require_valid

INTAKE_SYSTEM = (
    "You read a builder's own artifact and report only what it establishes. You never invent "
    "a mechanism, a number, a customer or a benchmark. When something is not established you "
    "record it as unknown instead of guessing. You answer with JSON and nothing else."
)

_PROMPT_TEMPLATE = """\
Read the artifact excerpt below and produce its claims document.

Rules, in order of importance:
1. Never invent a mechanism. If the excerpt does not establish how something works, it is an
   `unknown`, not a claim.
2. `verified` means the excerpt points at it (a file, a line, a test, a commit).
   `claimed` means the artifact's own prose asserts it but nothing points at it.
   `unknown` means it is not established at all.
3. `evidence` is a path, a path with a line number, or a commit sha. Leave it empty for
   `unknown` and say what would settle it in `note`.
4. A note may name a place the artifact overstates itself. Record the overstatement as it is
   written, and say in the note where it diverges.
5. List every fact a reader of a marketing page would want and the artifact does not settle,
   in `unknowns`.

Answer with exactly this JSON object and no prose around it:

{schema}

Artifact excerpt follows.

{excerpt}
"""


def build_intake_prompt(artifact: Artifact) -> str:
    schema = (
        '{"schema": "prd-agent.claims.v1", '
        '"artifact": {"name": "", "path": "", "commit": "", "read_at": ""}, '
        '"claims": [{"id": "C-001", "text": "", "status": "verified|claimed|unknown", '
        '"evidence": "path:line or commit sha", "note": ""}], '
        '"unknowns": [""]}'
    )
    return _PROMPT_TEMPLATE.format(schema=schema, excerpt=render_artifact(artifact))


def intake(root: Path, llm: LLM, *, artifact: Artifact | None = None) -> dict:
    """Read the artifact and return a validated claims document."""
    collected = artifact if artifact is not None else collect_artifact(Path(root))
    raw = llm.complete(system=INTAKE_SYSTEM, prompt=build_intake_prompt(collected))
    doc = extract_json(raw)
    if not isinstance(doc, dict):
        raise ModelOutputError("the intake reply was not a JSON object")
    doc.setdefault("schema", CLAIMS_SCHEMA)
    doc["artifact"] = {
        "name": collected.name,
        "path": str(collected.root),
        "commit": collected.commit,
        "read_at": collected.read_at or date.today().isoformat(),
    }
    doc.setdefault("claims", [])
    doc.setdefault("unknowns", [])
    for index, claim in enumerate(doc["claims"], start=1):
        claim.setdefault("id", f"C-{index:03d}")
        claim.setdefault("evidence", "")
        claim.setdefault("note", "")
    require_valid(doc, CLAIMS_SPEC, "claims.json")
    return doc
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_intake.py -v`
Expected: 6 passed. `test_intake_returns_a_document_that_matches_the_contract` asserts 12 claims because the reference run has 12; if the fixture file changes, update the number, not the code.

- [ ] **Step 5: Commit**

```bash
git add src/prd_agent/intake.py tests/test_intake.py
git commit -m "feat: add the intake stage that reads an artifact into claims.json"
```

---

## Task 6: Flags — the storyboard's data

**Files:**
- Create: `src/prd_agent/flags.py`
- Test: `tests/test_flags.py`

**Interfaces:**
- Consumes: `errors.StageError`.
- Produces: `NEED_KINDS`, `FLAG_PATTERN` (`re.Pattern` matching `[NEED: <need>]`), `next_flag_id(existing, prefix="N") -> str`, `make_flag(existing, need, claim, unlock, *, prefix="N") -> dict`, `merge_flags(*groups) -> list[dict]`, `render_flags(flags) -> str`, `ask_questions(flags, *, input_fn=input) -> dict[str, str]`, `answers_as_prompt(flags, answers) -> str`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_flags.py
from __future__ import annotations

from prd_agent import flags


def test_next_flag_id_starts_at_one_and_increments() -> None:
    assert flags.next_flag_id([]) == "N-001"
    assert flags.next_flag_id([{"id": "N-001"}]) == "N-002"
    assert flags.next_flag_id([{"id": "N-001"}, {"id": "N-007"}]) == "N-008"


def test_make_flag_allocates_and_validates_the_need_kind() -> None:
    flag = flags.make_flag([], "proof", "Adoption", "A public adopter list.")
    assert flag == {"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "A public adopter list."}


def test_make_flag_rejects_an_unknown_need() -> None:
    import pytest

    with pytest.raises(flags.StageError):
        flags.make_flag([], "vibes", "x", "y")


def test_merge_flags_dedupes_and_renumbers() -> None:
    left = [{"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "a"}]
    right = [
        {"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "a"},
        {"id": "N-002", "need": "differentiator", "claim": "Distinct from Kiro", "unlock": "b"},
    ]
    merged = flags.merge_flags(left, right)
    assert [item["id"] for item in merged] == ["N-001", "N-002"]
    assert [item["need"] for item in merged] == ["proof", "differentiator"]


def test_render_flags_emits_the_marker_the_footer_uses() -> None:
    rendered = flags.render_flags(
        [{"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "A public adopter list."}]
    )
    assert rendered.startswith("- `[NEED: proof]` Adoption.")
    assert "A public adopter list." in rendered
    assert flags.FLAG_PATTERN.findall(rendered) == ["proof"]


def test_render_flags_says_so_when_there_are_none() -> None:
    assert flags.render_flags([]) == "**Open flags.** None. Every claim on this page is pointed at in the artifact."


def test_ask_questions_reads_one_answer_per_flag() -> None:
    asked: list[str] = []
    replies = iter(["we have 40 adopters", ""])

    def fake_input(prompt: str) -> str:
        asked.append(prompt)
        return next(replies)

    answers = flags.ask_questions(
        [
            {"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "a list"},
            {"id": "N-002", "need": "proof", "claim": "Resume test", "unlock": "issue #139"},
        ],
        input_fn=fake_input,
    )
    assert answers == {"N-001": "we have 40 adopters", "N-002": ""}
    assert len(asked) == 2


def test_answers_as_prompt_keeps_the_skipped_ones_visible() -> None:
    text = flags.answers_as_prompt(
        [
            {"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "a list"},
            {"id": "N-002", "need": "proof", "claim": "Resume test", "unlock": "issue #139"},
        ],
        {"N-001": "40 adopters"},
    )
    assert "N-001" in text and "40 adopters" in text
    assert "N-002" in text and "no answer" in text
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python -m pytest tests/test_flags.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent.flags'`.

- [ ] **Step 3: Write the implementation**

```python
# src/prd_agent/flags.py
"""The `[NEED: ...]` flags. These are the storyboard: there is no separate question step.

A flag carries the claim it blocks, the kind of need, and the exact evidence that would
unlock it. Human mode puts them to the owner; autonomous mode ships them in the footer.
"""

from __future__ import annotations

import re
from typing import Callable

from prd_agent.errors import StageError

NEED_KINDS = ("proof", "differentiator", "mechanism", "audience")
FLAG_PATTERN = re.compile(r"\[NEED: ([a-z-]+)\]")
_ID_PATTERN = re.compile(r"^(?P<prefix>[A-Z])-(?P<number>\d+)$")
NO_FLAGS_LINE = "**Open flags.** None. Every claim on this page is pointed at in the artifact."


def next_flag_id(existing: list[dict], prefix: str = "N") -> str:
    highest = 0
    for flag in existing:
        match = _ID_PATTERN.match(str(flag.get("id", "")))
        if match and match.group("prefix") == prefix:
            highest = max(highest, int(match.group("number")))
    return f"{prefix}-{highest + 1:03d}"


def make_flag(existing: list[dict], need: str, claim: str, unlock: str, *, prefix: str = "N") -> dict:
    if need not in NEED_KINDS:
        raise StageError(f"unknown need kind {need!r}; expected one of {NEED_KINDS}")
    return {"id": next_flag_id(existing, prefix), "need": need, "claim": claim, "unlock": unlock}


def merge_flags(*groups: list[dict]) -> list[dict]:
    """Concatenate flag groups, drop exact duplicates, and renumber in order."""
    seen: set[tuple[str, str]] = set()
    merged: list[dict] = []
    for group in groups:
        for flag in group or []:
            key = (str(flag.get("need", "")), str(flag.get("claim", "")))
            if key in seen:
                continue
            seen.add(key)
            merged.append({"id": "", "need": flag.get("need", ""), "claim": flag.get("claim", ""),
                           "unlock": flag.get("unlock", "")})
    for index, flag in enumerate(merged, start=1):
        flag["id"] = f"N-{index:03d}"
    return merged


def render_flags(flags: list[dict]) -> str:
    if not flags:
        return NO_FLAGS_LINE
    lines = ["**Open flags.** Each one names the evidence that would let the page go harder.", ""]
    for flag in flags:
        lines.append(f"- `[NEED: {flag['need']}]` {flag['claim']}. {flag['unlock']}")
    return "\n".join(lines)


def ask_questions(
    flags: list[dict],
    *,
    input_fn: Callable[[str], str] = input,
) -> dict[str, str]:
    """Put each flag to the owner and collect the answer that resolves it."""
    answers: dict[str, str] = {}
    for flag in flags:
        prompt = (
            f"\n[{flag['id']}] {flag['need']}: {flag['claim']}\n"
            f"  What would settle it: {flag['unlock']}\n"
            f"  Your answer (leave empty to ship it as an open flag): "
        )
        answers[str(flag["id"])] = input_fn(prompt).strip()
    return answers


def answers_as_prompt(flags: list[dict], answers: dict[str, str]) -> str:
    """The owner's answers, with the skipped flags kept visible, for the revise call."""
    lines = ["The owner answered some open questions. Use what they gave you."]
    for flag in flags:
        answer = answers.get(str(flag["id"]), "").strip()
        if answer:
            lines.append(f"- {flag['id']} ({flag['need']}, {flag['claim']}): {answer}")
        else:
            lines.append(f"- {flag['id']} ({flag['need']}, {flag['claim']}): no answer, keep it as an open flag")
    return "\n".join(lines)
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_flags.py -v`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add src/prd_agent/flags.py tests/test_flags.py
git commit -m "feat: add flag allocation, rendering and the owner question loop"
```

---

## Task 7: Positioning and the swap test (spec §3.3, build order step 3)

**Files:**
- Create: `src/prd_agent/positioning.py`
- Create: `tests/fixtures/trends_pcm.json` (copy of `runs/pcm/trends.json`)
- Test: `tests/test_positioning.py`

**Interfaces:**
- Consumes: `llm.LLM`, `llm.extract_json`; `schemas.validate_positioning`, `schemas.require_valid`, `schemas.POSITIONING_SPEC`, `schemas.POSITIONING_SCHEMA`; `flags.make_flag`; `errors.ModelOutputError`.
- Produces: `SWAP_OVERLAP_THRESHOLD`, `STOPWORDS`, `content_words(text) -> set[str]`, `SwapResult(passed: bool, note: str, collisions: tuple[str, ...], max_overlap: float, closest: str)`, `swap_test(differentiator, competitors, *, threshold=SWAP_OVERLAP_THRESHOLD) -> SwapResult`, `POSITIONING_SYSTEM`, `build_positioning_prompt(claims, trends, *, answers=None) -> str`, `positioning(claims, trends, llm, *, answers=None) -> dict`.

- [ ] **Step 1: Copy the fixture and write the failing test**

```bash
cp runs/pcm/trends.json tests/fixtures/trends_pcm.json
```

```python
# tests/test_positioning.py
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from prd_agent import positioning
from prd_agent.errors import ModelOutputError, SchemaError
from prd_agent.llm import FakeLLM

FIXTURE = Path(__file__).parent / "fixtures" / "trends_pcm.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_content_words_drops_stopwords_and_short_words() -> None:
    assert positioning.content_words("The memory is the Git repository itself") == {
        "memory", "git", "repository", "itself"
    }


def test_the_reference_differentiator_survives_the_swap_test(pcm_run: Path) -> None:
    trends = load(FIXTURE)
    differentiator = load(pcm_run / "positioning.json")["differentiator"]
    result = positioning.swap_test(differentiator, trends["category"]["competitors"])
    # Calibrated on the hand run: the closest competitor is far below the threshold. The
    # measured value is printed by the step below and recorded here.
    assert result.passed is True
    assert result.collisions == ()
    assert result.max_overlap < positioning.SWAP_OVERLAP_THRESHOLD
    assert result.closest


def test_a_parroted_competitor_line_fails_the_swap_test() -> None:
    competitors = [
        {
            "name": "Mem0",
            "url": "https://example.invalid",
            "claim": "AI coding agents that actually remember your codebase",
            "language": ["persistent memory", "dedicated memory layer", "remembers everything"],
        }
    ]
    result = positioning.swap_test("Persistent memory as a dedicated memory layer", competitors)
    assert result.passed is False
    assert result.collisions == ("Mem0",)
    assert "Mem0" in result.note


def test_an_empty_differentiator_never_passes() -> None:
    result = positioning.swap_test("", [])
    assert result.passed is False
    assert "empty" in result.note.lower()


def test_positioning_overwrites_the_models_own_swap_test(pcm_run: Path) -> None:
    """The model proposes; the machine adjudicates. A model claiming a pass is ignored."""
    doc = load(pcm_run / "positioning.json")
    doc["swap_test"] = {"passed": False, "note": "the model was unsure"}
    doc["differentiator"] = "Persistent memory as a dedicated memory layer for coding agents"
    trends = load(FIXTURE)
    result = positioning.positioning(load(pcm_run / "claims.json"), trends, FakeLLM(json.dumps(doc)))
    assert result["swap_test"]["passed"] is False
    assert any(flag["need"] == "differentiator" for flag in result["flags"])


def test_a_passing_differentiator_adds_no_flag(pcm_run: Path) -> None:
    doc = load(pcm_run / "positioning.json")
    doc["swap_test"] = {"passed": False, "note": "wrong on purpose"}
    result = positioning.positioning(load(pcm_run / "claims.json"), load(FIXTURE), FakeLLM(json.dumps(doc)))
    assert result["swap_test"]["passed"] is True
    assert not any(flag["need"] == "differentiator" for flag in result["flags"])


def test_positioning_rejects_a_broken_document(pcm_run: Path) -> None:
    doc = copy.deepcopy(load(pcm_run / "positioning.json"))
    del doc["vision"]
    with pytest.raises(SchemaError):
        positioning.positioning(load(pcm_run / "claims.json"), load(FIXTURE), FakeLLM(json.dumps(doc)))


def test_positioning_rejects_a_non_json_reply(pcm_run: Path) -> None:
    with pytest.raises(ModelOutputError):
        positioning.positioning(load(pcm_run / "claims.json"), load(FIXTURE), FakeLLM("sure thing"))


def test_the_prompt_carries_the_competitors_and_the_owner_answers(pcm_run: Path) -> None:
    prompt = positioning.build_positioning_prompt(
        load(pcm_run / "claims.json"),
        load(FIXTURE),
        answers="The owner says there are 40 adopters.",
    )
    assert "Mem0" in prompt
    assert "jaded" in prompt
    assert "The owner says there are 40 adopters." in prompt
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python -m pytest tests/test_positioning.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent.positioning'`.

- [ ] **Step 3: Write the implementation**

```python
# src/prd_agent/positioning.py
"""Derive the spine (discomfort -> vision -> path) and a differentiator that survives the swap test.

The model proposes the positioning. The swap test is run here, in code, and its verdict
overwrites whatever the model said about itself. When no differentiator survives, the stage
flags it and writes no generic copy.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from prd_agent.errors import ModelOutputError
from prd_agent.flags import make_flag
from prd_agent.llm import LLM, extract_json
from prd_agent.schemas import POSITIONING_SCHEMA, POSITIONING_SPEC, require_valid

SWAP_OVERLAP_THRESHOLD = 0.6
STOPWORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "because", "but", "by", "for", "from", "has",
        "have", "in", "into", "is", "it", "its", "no", "not", "of", "on", "or", "that", "the",
        "their", "them", "they", "this", "to", "was", "were", "which", "while", "with", "you",
        "your", "yours", "we", "our", "us", "so", "than", "then", "there", "here", "when", "what",
        "who", "how", "why", "all", "any", "can", "does", "do", "did", "each", "every", "more",
        "most", "other", "some", "such", "only", "just", "also", "out", "up", "own", "same",
    }
)
_WORD = re.compile(r"[a-z][a-z0-9'-]*")

POSITIONING_SYSTEM = (
    "You are a positioning strategist. You derive one spine from the evidence you are given and "
    "you do not write marketing copy. You answer with JSON and nothing else."
)

_PROMPT_TEMPLATE = """\
Derive the positioning for this artifact.

The spine is the Human Action Model: current discomfort, better vision, path to action.
The differentiator is the one line that cannot appear on a named competitor's site unchanged.

Rules:
1. Use the claims. A `verified` claim may be stated plainly. A `claimed` claim may be stated
   only as the artifact's own assertion. An `unknown` may not be stated at all.
2. The `alternative` is what the audience does today instead, named concretely.
3. The `differentiator` names the mechanism, not an adjective. If the mechanism cannot be
   distinguished from what the competitors already say, say so in the swap test note.
4. Hype is uncapped, with one exception: nothing here may contradict what the artifact is.
5. `flags` collects what you could not derive. Each flag names the claim, the kind of need
   (proof, differentiator, mechanism or audience) and the evidence that would unlock it.

Answer with exactly this JSON object and no prose around it:

{schema}

Claims:

{claims}

Trends (competitor language, market stage, register):

{trends}

{answers}
"""


def content_words(text: str) -> set[str]:
    """The words a line is actually made of, with stopwords and short words removed."""
    return {word for word in _WORD.findall(text.lower()) if len(word) > 2 and word not in STOPWORDS}


@dataclass(frozen=True)
class SwapResult:
    passed: bool
    note: str
    collisions: tuple[str, ...] = ()
    max_overlap: float = 0.0
    closest: str = ""


def swap_test(
    differentiator: str,
    competitors: list[dict],
    *,
    threshold: float = SWAP_OVERLAP_THRESHOLD,
) -> SwapResult:
    """A line fails when one competitor's own language already covers most of it.

    A failure is authoritative. A pass is provisional: lexical overlap is a floor, and the
    story prompt still runs the qualitative swap test from the skill.
    """
    words = content_words(differentiator)
    if not words:
        return SwapResult(False, "The differentiator is empty, so it cannot survive the swap test.")
    closest = ""
    max_overlap = 0.0
    collisions: list[str] = []
    for competitor in competitors:
        name = str(competitor.get("name", "unnamed"))
        theirs = content_words(" ".join(str(item) for item in competitor.get("language", [])))
        overlap = len(words & theirs) / len(words)
        if overlap > max_overlap:
            closest, max_overlap = name, overlap
        if overlap >= threshold:
            collisions.append(name)
    if collisions:
        note = (
            f"{', '.join(collisions)} already use {max_overlap:.0%} of this line's words, so it would "
            f"work unchanged on their page. Rewrite it from the mechanism this artifact actually has."
        )
        return SwapResult(False, note, tuple(collisions), max_overlap, closest)
    note = (
        f"No named competitor's language covers this line (closest: {closest or 'none'} at "
        f"{max_overlap:.0%} against a {threshold:.0%} threshold)."
    )
    return SwapResult(True, note, (), max_overlap, closest)


def build_positioning_prompt(claims: dict, trends: dict, *, answers: str | None = None) -> str:
    schema = (
        '{"schema": "prd-agent.positioning.v1", '
        '"audience": {"who": "", "situation": "", "trigger": ""}, '
        '"discomfort": "", "vision": "", "path": "", "alternative": "", "differentiator": "", '
        '"swap_test": {"passed": false, "note": ""}, '
        '"flags": [{"id": "N-001", "need": "proof", "claim": "", "unlock": ""}]}'
    )
    return _PROMPT_TEMPLATE.format(
        schema=schema,
        claims=json.dumps(claims, indent=2, ensure_ascii=False),
        trends=json.dumps(trends, indent=2, ensure_ascii=False),
        answers=answers or "No owner answers were supplied for this run.",
    )


def positioning(claims: dict, trends: dict, llm: LLM, *, answers: str | None = None) -> dict:
    raw = llm.complete(
        system=POSITIONING_SYSTEM,
        prompt=build_positioning_prompt(claims, trends, answers=answers),
    )
    doc = extract_json(raw)
    if not isinstance(doc, dict):
        raise ModelOutputError("the positioning reply was not a JSON object")
    doc.setdefault("schema", POSITIONING_SCHEMA)
    doc.setdefault("flags", [])
    result = swap_test(str(doc.get("differentiator", "")), list(trends.get("category", {}).get("competitors", [])))
    doc["swap_test"] = {"passed": result.passed, "note": result.note}
    if not result.passed:
        doc["flags"] = list(doc["flags"]) + [
            make_flag(
                doc["flags"],
                "differentiator",
                f"Distinct from {', '.join(result.collisions) or 'the named competitors'}",
                "A mechanism claim that the named competitors cannot make. "
                + (f"Closest collision: {result.closest} at {result.max_overlap:.0%} word overlap."
                   if result.collisions else ""),
            )
        ]
    require_valid(doc, POSITIONING_SPEC, "positioning.json")
    return doc
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_positioning.py -v`
Expected: 9 passed.

- [ ] **Step 5: Record the calibration measurement**

Run:

```bash
python - <<'PY'
import json, pathlib
from prd_agent.positioning import content_words
trends = json.loads(pathlib.Path("tests/fixtures/trends_pcm.json").read_text(encoding="utf-8"))
line = json.loads(pathlib.Path("runs/pcm/positioning.json").read_text(encoding="utf-8"))["differentiator"]
words = content_words(line)
for competitor in trends["category"]["competitors"]:
    theirs = content_words(" ".join(competitor["language"]))
    print(f"{competitor['name']:20s} {len(words & theirs) / len(words):.2f}")
PY
```

Paste the printed overlaps into the comment in `test_the_reference_differentiator_survives_the_swap_test`. If any competitor reaches `SWAP_OVERLAP_THRESHOLD`, do not raise the threshold to make the test pass: add the missing stopwords or fix the tokenisation, and record what changed in the comment.

- [ ] **Step 6: Commit**

```bash
git add src/prd_agent/positioning.py tests/test_positioning.py tests/fixtures/trends_pcm.json
git commit -m "feat: add the positioning stage with a machine-run swap test"
```

---

## Task 8: The self-check, part one — scope and hard bans

**Files:**
- Create: `src/prd_agent/checks.py`
- Modify: `stories/pcm.md:17`
- Test: `tests/test_checks.py`

**Interfaces:**
- Consumes: `errors.StageError` (not directly; the checker raises nothing).
- Produces: `FOOTER_HEADING`, `BAN`, `CAP`, `REVIEW`, `Section(name, text, start_line)`, `Finding(rule, severity, section, line, text, detail)`, `CheckReport(findings, sections)` with `.bans`, `.caps`, `.reviews`, `.passed()`, `split_body_footer(markdown) -> tuple[str, str]`, `split_sections(markdown) -> list[Section]`, `check_story(body) -> CheckReport`.

- [ ] **Step 1: Fix the one tell in the hand run**

The hand-executed reference story trips the contrast-reveal ban at line 17. It was written before the checker existed. Rewrite the line so the target the code must reproduce is clean, and record the fix.

```markdown
Old line 17:
The failure has a name and it is not your memory. It is where the memory lives.

New line 17:
The failure has a name. The memory lives somewhere the project does not control.
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_checks.py
from __future__ import annotations

from pathlib import Path

from prd_agent import checks


def body_of(path: Path) -> str:
    return checks.split_body_footer(path.read_text(encoding="utf-8"))[0]


def rules(report: checks.CheckReport) -> list[str]:
    return [finding.rule for finding in report.findings]


def test_contrast_reveal_is_a_ban() -> None:
    report = checks.check_story("## Hero\n\nIt's not a tool. It's a teammate.\n")
    assert [f.rule for f in report.bans] == ["contrast_reveal"]
    assert report.bans[0].severity == checks.BAN
    assert "not a tool" in report.bans[0].text


def test_contrast_reveal_variants_are_caught() -> None:
    drafts = [
        "## H\n\nMost teams have a list of ideas that never launch. Not because they are bad. Because each one needs a developer.\n",
        "## H\n\nNot just faster reporting, but a better decision.\n",
        "## H\n\nThe question isn't speed. It is trust.\n",
    ]
    for draft in drafts:
        assert checks.check_story(draft).bans, draft


def test_negation_lists_are_a_ban() -> None:
    report = checks.check_story("## H\n\nNo setup call, no templates, no waiting on IT.\n")
    assert "negation_list" in rules(report)
    assert report.bans


def test_a_single_absence_is_fine() -> None:
    report = checks.check_story("## H\n\nInstall it and it is running. No card required.\n")
    assert report.bans == ()


def test_trailing_pile_on_is_a_ban() -> None:
    report = checks.check_story(
        "## H\n\nReports pull from the data you already have, no exports, no spreadsheets.\n"
    )
    assert "trailing_pile_on" in rules(report)


def test_a_trailing_gerund_clause_is_a_ban() -> None:
    report = checks.check_story("## H\n\nIt syncs your calendar automatically, ensuring nothing slips.\n")
    assert "trailing_pile_on" in rules(report)


def test_self_answered_questions_are_a_ban() -> None:
    report = checks.check_story("## H\n\nThe result? Onboarding that takes minutes.\n")
    assert "self_answered_question" in rules(report)


def test_a_reader_question_is_not_a_ban() -> None:
    report = checks.check_story("## H\n\nNeed to share a screenshot? Drop it in the thread.\n")
    assert report.bans == ()


def test_faq_questions_are_not_a_ban() -> None:
    report = checks.check_story("## FAQ\n\n**Does it work with Shopify?** Yes, on every plan.\n")
    assert report.bans == ()


def test_colon_reveals_are_a_ban() -> None:
    report = checks.check_story("## H\n\nThe best part: it learns.\n")
    assert "colon_reveal" in rules(report)


def test_a_colon_before_a_list_is_fine() -> None:
    report = checks.check_story(
        "## H\n\nA fresh session reads four things: what the project is, where it stands, which task is "
        "active, and what the last session proved.\n"
    )
    assert report.bans == ()


def test_a_colon_after_a_full_clause_is_fine() -> None:
    report = checks.check_story(
        "## H\n\nThe long-term test is simple: a project should stay understandable and resumable.\n"
    )
    assert report.bans == ()


def test_banned_vocabulary_and_stock_phrases_are_bans() -> None:
    assert "banned_vocabulary" in rules(checks.check_story("## H\n\nWe delve into the realm of billing.\n"))
    assert "stock_phrase" in rules(checks.check_story("## H\n\nSay goodbye to manual entry.\n"))


def test_hype_punctuation_is_a_ban() -> None:
    assert "hype_punctuation" in rules(checks.check_story("## H\n\nReady to level up?!\n"))


def test_fenced_code_and_tables_are_exempt() -> None:
    draft = (
        "## H\n\n```bash\n# It's not a tool. It's a teammate. No X, no Y, no Z.\n"
        "continuity init --profile software\n```\n\n| Not X | It is Y |\n|---|---|\n"
    )
    assert checks.check_story(draft).bans == ()


def test_the_footer_is_exempt() -> None:
    draft = (
        "## H\n\nInstall it once.\n\n"
        "### Proof and open items\n\n"
        "The result? A page you can audit. No X, no Y. Not because it is bad. Because it is a footer.\n"
    )
    assert checks.check_story(draft).bans == ()
    assert checks.split_body_footer(draft)[1].startswith("### Proof and open items")


def test_line_numbers_point_into_the_body(pcm_story: Path) -> None:
    report = checks.check_story(body_of(pcm_story))
    assert report.sections[0].start_line == 1


def test_the_reference_story_is_clean_after_the_fix(pcm_story: Path) -> None:
    report = checks.check_story(body_of(pcm_story))
    assert report.bans == (), [f"{f.rule} at {f.line}: {f.text}" for f in report.bans]
    assert report.passed() is True


def test_the_hand_run_line_is_still_caught_as_a_finding() -> None:
    """The sentence the hand run carried. Kept as a fixture so the rule cannot silently rot."""
    report = checks.check_story(
        "## H\n\nThe failure has a name and it is not your memory. It is where the memory lives.\n"
    )
    assert [f.rule for f in report.bans] == ["contrast_reveal"]
```

- [ ] **Step 3: Run it and watch it fail**

Run: `python -m pytest tests/test_checks.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent.checks'`.

- [ ] **Step 4: Write the implementation**

```python
# src/prd_agent/checks.py
"""The machine half of the copywriting skill's self-check.

Read with `vendor/copywriting/references/ai-tells.md` open. Every rule below names the pattern
it implements, and the exemption list implements that file's "Still fine" paragraph.

Scope: the pitch body only. The footer is excluded because it legitimately names the banned
patterns; fenced code blocks and markdown tables are excluded because they are not prose.

Severities:
  ban    - the draft fails the gate and is rewritten. The hard bans from ai-tells.md.
  cap    - a device that is fine once, a tell when repeated. Fails the gate only past its limit.
  review - reported for a human to read. Never fails the gate.

What this cannot catch: whether the story lands, whether a sentence that avoids every rule is
still empty, and any tell written in a shape no rule here matches. `summary()` says so in the
story footer, so the page never claims more than the checker proved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

FOOTER_HEADING = "### Proof and open items"
BAN = "ban"
CAP = "cap"
REVIEW = "review"

_FENCE = re.compile(r"^\s*(?:```|~~~)")
_TABLE_ROW = re.compile(r"^\s*\|")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_BOLD_QUESTION = re.compile(r"^\s*\*\*.+\?\*\*")
_EM_DASH = re.compile(r"[\u2014\u2013]")
_HYPE = re.compile(r"!|\?!")
_EMOJI_LEAD = re.compile(r"^\s*(?:[-*+]\s+|\#{1,6}\s+)[\U0001F300-\U0001FAFF\u2600-\u27BF]")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[A-Za-z][A-Za-z'\-]*")

CONTRAST_REVEAL = (
    re.compile(
        r"(?i)\b(?:it|this|that)(?:'s| is| was)?\s*(?:not|isn'?t|aren'?t)\b[^.?!]{0,80}[.?!]\s+(?:it|this|that)\b"
    ),
    re.compile(r"(?i)\bnot because\b[^.?!]{0,80}[.?!]\s*because\b"),
    re.compile(r"(?i)\bnot just\b[^,.?!]{0,60}\bbut\b"),
    re.compile(r"(?i)\bless\s+\w+[^,.?!]{0,40},\s*more\s+\w+"),
    re.compile(r"(?i)\bthe (?:question|problem|issue|catch) isn'?t\b"),
)
NEGATION_ITEM = re.compile(r"(?i)\b(?:no|without|zero)\s+[a-z][\w'-]*")
TRAILING_PILE_ON = (
    re.compile(r"(?i),\s*(?:no|not|without|zero)\s+[a-z]"),
    re.compile(r"(?i),\s*(?:ensuring|allowing|enabling|making it|keeping it)\b"),
)
SELF_ANSWERED_QUESTION = re.compile(r"^\s*(?!\*\*|#{1,6}\s)([A-Z][^.!?\n]{0,40}\?)\s+\S")
COLON_REVEAL_PHRASES = (
    "the best part:", "the secret:", "the trick:", "the catch:", "the result:", "the point:",
    "one word:", "here's the secret:", "here's the thing:",
)
COLON_REVEAL = re.compile(r"^\s*(?![\|\-*+#>])([^:\n]{1,40}):\s+(\S.*)$")
COMMON_VERBS = frozenset(
    {
        "is", "are", "was", "were", "be", "been", "has", "have", "had", "means", "mean", "reads",
        "read", "includes", "include", "shows", "show", "does", "do", "gets", "get", "gives",
        "give", "keeps", "keep", "works", "work", "contains", "contain", "covers", "cover",
        "lists", "list", "prints", "print", "takes", "take", "needs", "need", "ships", "ship",
        "writes", "write", "runs", "run", "fails", "fail", "costs", "cost",
    }
)
STOCK_PHRASES = (
    "in today's fast-paced world", "whether you're", "here's the thing", "say goodbye to",
    "say hello to", "unlock the power of", "unleash the power of", "take it to the next level",
    "the future of", "everything you need to", "all-in-one", "effortless", "in just a few clicks",
    "join thousands", "game-changer", "this changes everything", "when it comes to",
    "let me be clear", "here's what nobody tells you", "in this guide", "let's dive in",
    "in conclusion", "at the end of the day", "because growth shouldn't wait",
    "and that changes everything", "it's worth noting", "moreover", "furthermore", "additionally",
    "great question", "let's be honest", "we get it", "transform the way you work",
    "built for teams who move fast", "world-class", "best-in-class", "reimagined", "redefined",
    "the secret to", "the truth is",
)
STOCK_PHRASE_PATTERN = re.compile(r"(?i)\b(?:" + "|".join(re.escape(p) for p in STOCK_PHRASES) + r")")
OPENER_PHRASES = ("imagine ",)
OPENER_PATTERN = re.compile(r"(?i)(?:^|[.?!]\s+)(?:" + "|".join(re.escape(p) for p in OPENER_PHRASES) + r")")
BANNED_WORDS = (
    "delve", "tapestry", "testament to", "realm", "embark", "beacon", "multifaceted", "paradigm",
    "synergy", "myriad", "plethora", "meticulous", "intricate", "utilize", "supercharge",
    "turbocharge", "ever-evolving landscape", "plays a crucial role", "leverag",
)
BANNED_WORD_PATTERN = re.compile(r"(?i)\b(?:" + "|".join(re.escape(w) for w in BANNED_WORDS) + r")\w*")


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    section: str
    line: int
    text: str
    detail: str = ""


@dataclass(frozen=True)
class Section:
    name: str
    text: str
    start_line: int


@dataclass(frozen=True)
class CheckReport:
    findings: tuple[Finding, ...] = field(default_factory=tuple)
    sections: tuple[str, ...] = field(default_factory=tuple)

    @property
    def bans(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.severity == BAN)

    @property
    def caps(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.severity == CAP)

    @property
    def reviews(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.severity == REVIEW)

    def cap_violations(self) -> tuple[Finding, ...]:
        return ()

    def passed(self) -> bool:
        return not self.bans and not self.cap_violations()


def split_body_footer(markdown: str) -> tuple[str, str]:
    """Split the page into the pitch body and the code-generated footer."""
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == FOOTER_HEADING:
            body = "\n".join(lines[:index]).rstrip()
            while body.endswith("---"):
                body = body[: -3].rstrip()
            return body, "\n".join(lines[index:])
    return markdown.rstrip(), ""


def split_sections(markdown: str) -> list[Section]:
    """The hero (everything before the first `## `) and then one section per `## ` heading."""
    lines = markdown.splitlines()
    starts: list[tuple[str, int]] = [("hero", 0)]
    for index, line in enumerate(lines):
        match = _HEADING.match(line)
        if match and len(match.group(1)) == 2:
            starts.append((match.group(2).strip(), index))
    sections: list[Section] = []
    for position, (name, start) in enumerate(starts):
        end = starts[position + 1][1] if position + 1 < len(starts) else len(lines)
        text = "\n".join(lines[start:end]).strip("\n")
        if text:
            sections.append(Section(name=name, text=text, start_line=start + 1))
    return sections


def _prose_lines(section: Section) -> list[tuple[int, str]]:
    """The lines a tell can live on: no fences, no table rows, no fenced content."""
    out: list[tuple[int, str]] = []
    in_fence = False
    for offset, line in enumerate(section.text.splitlines()):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or _TABLE_ROW.match(line):
            continue
        out.append((section.start_line + offset, line))
    return out


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_SPLIT.split(text.strip()) if part.strip()]


def _check_prose(section: Section) -> list[Finding]:
    findings: list[Finding] = []
    for line, raw in _prose_lines(section):
        text = raw.strip()
        if not text:
            continue
        stripped = _HEADING.sub(r"\2", text).replace("**", "").strip()
        is_bold_question = bool(_BOLD_QUESTION.match(text))
        if _EM_DASH.search(text):
            findings.append(Finding("em_dash_short", BAN, section.name, line, text,
                                    "em dashes are banned in headings and the hero"))
        if _HYPE.search(text):
            findings.append(Finding("hype_punctuation", BAN, section.name, line, text, "no exclamation points"))
        if _EMOJI_LEAD.match(text):
            findings.append(Finding("emoji_structure", BAN, section.name, line, text, "no emoji as structure"))
        if STOCK_PHRASE_PATTERN.search(stripped):
            findings.append(Finding("stock_phrase", BAN, section.name, line, text,
                                    "a stock marketing phrase from ai-tells.md"))
        if OPENER_PATTERN.search(stripped):
            findings.append(Finding("stock_phrase", BAN, section.name, line, text, "a banned opener"))
        if BANNED_WORD_PATTERN.search(stripped):
            found = BANNED_WORD_PATTERN.search(stripped)
            findings.append(Finding("banned_vocabulary", BAN, section.name, line, text,
                                    f"banned word: {found.group(0) if found else ''}"))
        for pattern in CONTRAST_REVEAL:
            if pattern.search(stripped):
                findings.append(Finding("contrast_reveal", BAN, section.name, line, text,
                                        "states the denial instead of the claim"))
                break
        for sentence in _sentences(stripped):
            negations = NEGATION_ITEM.findall(sentence)
            if len(negations) >= 2:
                findings.append(Finding("negation_list", BAN, section.name, line, sentence,
                                        "defines the product by what is absent"))
                break
        for pattern in TRAILING_PILE_ON:
            if pattern.search(stripped):
                findings.append(Finding("trailing_pile_on", BAN, section.name, line, text,
                                        "a complete claim with add-ons trailing after a comma"))
                break
        lowered = stripped.lower()
        if any(phrase in lowered for phrase in COLON_REVEAL_PHRASES):
            findings.append(Finding("colon_reveal", BAN, section.name, line, text, "a label standing in for a sentence"))
        elif not is_bold_question:
            match = COLON_REVEAL.match(text)
            if match:
                label = match.group(1).strip()
                words = _WORD.findall(label)
                has_verb = any(word.lower() in COMMON_VERBS for word in words)
                if len(words) <= 5 and not has_verb:
                    findings.append(Finding("colon_reveal", BAN, section.name, line, text,
                                            "a short label before a colon"))
        if SELF_ANSWERED_QUESTION.match(text) and not is_bold_question:
            match = SELF_ANSWERED_QUESTION.match(text)
            question = match.group(1) if match else ""
            if len(question.split()) <= 6:
                findings.append(Finding("self_answered_question", BAN, section.name, line, text,
                                        "asks the reader a question and answers it in the same breath"))
    return findings


def check_story(body: str) -> CheckReport:
    """Run every rule over the pitch body and return the report."""
    sections = split_sections(body)
    findings: list[Finding] = []
    for section in sections:
        findings.extend(_check_prose(section))
    return CheckReport(findings=tuple(findings), sections=tuple(section.name for section in sections))
```

- [ ] **Step 5: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_checks.py -v`
Expected: 18 passed. If a rule fires on the reference story and the sentence is not a real tell, tighten the rule and add the sentence as a negative case in the test file. Do not weaken a rule to make the story pass.

- [ ] **Step 6: Commit**

```bash
git add src/prd_agent/checks.py tests/test_checks.py stories/pcm.md
git commit -m "feat: add the self-check hard bans and rewrite the one tell in the hand run"
```

---

## Task 9: The self-check, part two — caps, beats and the summary

**Files:**
- Modify: `src/prd_agent/checks.py`
- Test: `tests/test_checks.py` (append)

**Interfaces:**
- Consumes: everything Task 8 produced.
- Produces: `CAP_LIMITS`, `CAP_WORDS`, `INTENSIFIERS`, `check_beats(body) -> list[Finding]`, `CheckReport.cap_violations()`, `CheckReport.summary() -> str`, `CheckReport.limitations() -> str`.

- [ ] **Step 1: Write the failing test (append to `tests/test_checks.py`)**

```python
# tests/test_checks.py (append)
def test_one_fragment_is_fine_and_two_are_not() -> None:
    one = checks.check_story("## H\n\nSimple.\n\nThis section carries one real sentence with a fact in it.\n")
    assert one.passed() is True
    two = checks.check_story("## H\n\nSimple.\n\nDone.\n")
    assert two.passed() is False
    assert [f.rule for f in two.cap_violations()] == ["fragment"]


def test_a_fragment_needs_to_have_no_verb() -> None:
    report = checks.check_story("## H\n\nYou had all of it.\n")
    assert report.findings == ()


def test_three_lists_are_capped_per_section() -> None:
    report = checks.check_story("## H\n\nFast, secure, and scalable.\n\nSmall, light, and quick.\n")
    assert [f.rule for f in report.cap_violations()] == ["reflexive_three"]


def test_cap_vocabulary_is_reported_per_section() -> None:
    report = checks.check_story(
        "## H\n\nA seamless, robust platform.\n\nAnother seamless paragraph.\n"
    )
    assert [f.rule for f in report.cap_violations()] == ["cap_vocabulary"]


def test_em_dashes_are_capped_in_long_copy_not_banned() -> None:
    report = checks.check_story("## H\n\nOne clause \u2014 and another, with a third \u2014 then a fourth.\n")
    assert report.bans == ()
    assert "em_dash_long" in [f.rule for f in report.caps]


def test_long_sentences_are_reported_but_never_gate() -> None:
    sentence = "This sentence keeps going and going, with clause after clause, comma after comma, and still it does not stop until it has run well past the point where any reader is still with it at all."
    report = checks.check_story(f"## H\n\n{sentence}\n")
    assert "long_sentence" in [f.rule for f in report.reviews]
    assert report.passed() is True


def test_missing_beats_fail_the_gate() -> None:
    report = checks.check_story("# Headline\n\n**Subhead.**\n\nInstall it.\n")
    assert "beat_path" in [f.rule for f in report.bans]


def test_the_reference_story_has_all_three_beats(pcm_story: Path) -> None:
    report = checks.check_story(body_of(pcm_story))
    assert [f.rule for f in report.bans if f.rule.startswith("beat_")] == []


def test_the_summary_states_what_was_and_was_not_checked(pcm_story: Path) -> None:
    report = checks.check_story(body_of(pcm_story))
    summary = report.summary()
    assert "0 hard bans" in summary
    assert "discomfort, vision, path" in summary
    assert "whether the story lands" in report.limitations()


def test_the_limitations_are_honest_about_scope() -> None:
    report = checks.check_story("## H\n\nOne sentence with a fact in it, long enough to count.\n")
    assert "cannot" in report.limitations()
    assert "shape no rule here matches" in report.limitations()
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python -m pytest tests/test_checks.py -v`
Expected: FAIL — `AttributeError: 'CheckReport' object has no attribute 'summary'`.

- [ ] **Step 3: Write the implementation (append and replace in `checks.py`)**

Add the caps and beats data after `BANNED_WORD_PATTERN`:

```python
# src/prd_agent/checks.py (insert after BANNED_WORD_PATTERN)

CAP_LIMITS = {"fragment": 1, "reflexive_three": 1, "cap_vocabulary": 1, "em_dash_long": 1}
CAP_WORDS = frozenset(
    {
        "seamless", "robust", "streamline", "empower", "elevate", "unlock", "unleash", "harness",
        "foster", "enhance", "optimize", "cutting-edge", "innovative", "revolutionary",
        "transformative", "holistic", "comprehensive", "pivotal", "crucial", "vital", "powerful",
        "next-level", "world-class", "best-in-class", "landscape", "navigate", "ecosystem",
        "journey", "supercharge", "turbocharge",
    }
)
INTENSIFIERS = frozenset(
    {"truly", "genuinely", "incredibly", "deeply", "fundamentally", "significantly", "simply",
     "actually", "literally", "quietly"}
)
REFLEXIVE_THREE = re.compile(r"(?i)\b(\w+),\s+(\w+),?\s+and\s+(\w+)[.!?\n]")
FALSE_RANGE = re.compile(r"(?i)\bfrom\s+[a-z]+\s+to\s+[a-z]+\b")
ORDERED_ITEM = re.compile(r"^\s*\d+[.)]\s+")
```

**Replace the placeholder `CheckReport.cap_violations` you wrote in Task 8** — the one whose whole body is `return ()`, in the `CheckReport` class — with the real body below, and add `summary`/`limitations` to the same class. Do not add a second `cap_violations`; an executor who read only Task 8 has the stub, and leaving both in the file means the stub wins by definition order:

```python
    def cap_violations(self) -> tuple[Finding, ...]:
        """The cap findings past their limit, counted per rule per section."""
        counts: dict[tuple[str, str], list[Finding]] = {}
        for finding in self.caps:
            counts.setdefault((finding.rule, finding.section), []).append(finding)
        violations: list[Finding] = []
        for (rule, _section), items in counts.items():
            limit = CAP_LIMITS.get(rule, 0)
            if len(items) > limit:
                violations.extend(items[limit:])
        return tuple(violations)

    def summary(self) -> str:
        counts = {rule: 0 for rule in ("contrast_reveal", "negation_list", "trailing_pile_on",
                                       "self_answered_question", "colon_reveal", "stock_phrase",
                                       "banned_vocabulary", "hype_punctuation", "em_dash_short")}
        for finding in self.findings:
            counts[finding.rule] = counts.get(finding.rule, 0) + 1
        bans = len(self.bans)
        caps = {rule: 0 for rule in CAP_LIMITS}
        for finding in self.caps:
            caps[finding.rule] = caps.get(finding.rule, 0) + 1
        caps_text = ", ".join(f"{rule} {caps[rule]}/{CAP_LIMITS[rule]}" for rule in CAP_LIMITS)
        return (
            f"**Self-check.** Run by `prd_agent.checks` against the vendored `copywriting` skill's "
            f"`references/ai-tells.md`. {bans} hard bans in {len(self.sections)} sections "
            f"(contrast reveals {counts['contrast_reveal']}, negation lists {counts['negation_list']}, "
            f"trailing pile-ons {counts['trailing_pile_on']}, self-answered questions "
            f"{counts['self_answered_question']}, colon reveals {counts['colon_reveal']}, stock phrases "
            f"{counts['stock_phrase']}, banned words {counts['banned_vocabulary']}, hype punctuation "
            f"{counts['hype_punctuation']}, em dashes in short copy {counts['em_dash_short']}). "
            f"Frequency caps, counted per section: {caps_text}. Structural beats present: discomfort, "
            f"vision, path. {self.limitations()}"
        )

    def limitations(self) -> str:
        return (
            "What this check cannot decide: whether the story lands, whether a sentence that avoids "
            "every rule is still empty, and any tell written in a shape no rule here matches. That "
            "judgment is the owner's."
        )
```

Add the beats check and wire it into `check_story`:

```python
# src/prd_agent/checks.py (append before check_story)

def check_beats(body: str) -> list[Finding]:
    """The three structural beats of the Human Action Model, as far as they are mechanical.

    discomfort: the first `## ` section names the reader's situation in their own terms.
    vision: a second `## ` section says what the better state looks like.
    path: a later section carries the ordered steps that get there.
    """
    findings: list[Finding] = []
    sections = split_sections(body)
    body_sections = [section for section in sections if section.name != "hero"]
    first_line = sections[0].start_line if sections else 1

    if not body_sections:
        return [Finding("beat_discomfort", BAN, "hero", first_line, "", "no problem section at all")]

    discomfort = body_sections[0]
    discomfort_text = discomfort.text
    has_second_person = bool(re.search(r"(?i)\b(?:you|your|you're)\b", discomfort_text))
    enough_prose = len(_sentences(discomfort_text)) >= 2
    if not (has_second_person and enough_prose):
        findings.append(Finding("beat_discomfort", BAN, discomfort.name, discomfort.start_line, discomfort_text,
                                "the first section does not name the reader's situation"))
    if len(body_sections) < 2:
        findings.append(Finding("beat_vision", BAN, discomfort.name, discomfort.start_line, "",
                                "there is no second section to carry the vision"))
    else:
        vision = body_sections[1]
        if len(_sentences(vision.text)) < 2:
            findings.append(Finding("beat_vision", BAN, vision.name, vision.start_line, vision.text,
                                    "the second section does not describe the better state"))

    ordered = 0
    for section in body_sections[1:]:
        ordered += sum(1 for line in section.text.splitlines() if ORDERED_ITEM.match(line))
    if ordered < 3:
        findings.append(Finding("beat_path", BAN, body_sections[-1].name, body_sections[-1].start_line, "",
                                f"found {ordered} ordered steps; the path to action needs at least 3"))
    return findings


def check_story(body: str) -> CheckReport:
    """Run every rule over the pitch body and return the report."""
    sections = split_sections(body)
    findings: list[Finding] = []
    for section in sections:
        findings.extend(_check_prose(section))
        findings.extend(_check_caps(section))
    findings.extend(check_beats(body))
    return CheckReport(findings=tuple(findings), sections=tuple(section.name for section in sections))
```

And the caps helper, placed next to `_check_prose`:

```python
# src/prd_agent/checks.py (insert after _check_prose)

def _check_caps(section: Section) -> list[Finding]:
    """The frequency caps and the review-only findings for one section."""
    findings: list[Finding] = []
    prose = [text.strip() for _, text in _prose_lines(section) if text.strip()]
    body = "\n".join(prose)

    for line, raw in _prose_lines(section):
        text = raw.strip()
        if not text or _HEADING.match(text):
            continue
        if _EM_DASH.search(text):
            findings.append(Finding("em_dash_long", CAP, section.name, line, text, "one em dash per section"))
        if REFLEXIVE_THREE.search(text):
            findings.append(Finding("reflexive_three", CAP, section.name, line, text, "one three-item list per section"))
        if FALSE_RANGE.search(text):
            findings.append(Finding("false_range", REVIEW, section.name, line, text, "a range whose ends do not span"))

    for paragraph in [block.strip() for block in body.split("\n\n") if block.strip()]:
        words = [word.lower() for word in _WORD.findall(paragraph)]
        dense = sum(1 for word in words if word in CAP_WORDS or word in INTENSIFIERS)
        if dense >= 2:
            findings.append(Finding("cap_vocabulary", CAP, section.name, section.start_line, paragraph[:120],
                                    f"{dense} cap words in one paragraph"))

    for line, raw in _prose_lines(section):
        text = raw.strip()
        if not text:
            continue
        for sentence in _sentences(text):
            word_count = len(_WORD.findall(sentence))
            if word_count > 20:
                findings.append(Finding("long_sentence", REVIEW, section.name, line, sentence,
                                        f"{word_count} words, read it aloud"))
    return findings
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_checks.py -v`
Expected: 28 passed. The reference story must reach `report.passed() is True`; it has one ordered list of four steps, two opening sections in the second person, and no cap violations.

- [ ] **Step 5: Commit**

```bash
git add src/prd_agent/checks.py tests/test_checks.py
git commit -m "feat: add the self-check caps, structural beats and the honest summary"
```

---

---

## Task 10: Story, footer and the gate (spec §3.4, build order step 4)

**Files:**
- Create: `src/prd_agent/story.py`
- Test: `tests/test_story.py`

**Interfaces:**
- Consumes: `skill.build_skill_context`; `checks.check_story`, `checks.CheckReport`; `flags.FLAG_PATTERN`, `flags.merge_flags`, `flags.render_flags`; `llm.LLM`; `errors.StoryGateError`; `schemas` (not directly).
- Produces: `MAX_REWRITES`, `STORY_SYSTEM`, `FOOTER_HEADING`; `build_story_prompt(*, positioning: dict, claims: dict, trends: dict, exemplars: list[dict] = ()) -> str`; `build_rewrite_prompt(*, body: str, report: CheckReport, positioning: dict, claims: dict) -> str`; `clean_body(raw: str) -> tuple[str, list[dict]]`; `build_proof_table(claims: dict) -> str`; `build_trends_note(trends: dict) -> str`; `build_footer(*, claims: dict, positioning: dict, trends: dict, report: CheckReport, extra_flags: list[dict] = ()) -> str`; `assemble_story(body: str, footer: str) -> str`; `story(*, claims: dict, positioning: dict, trends: dict, llm: LLM, exemplars: list[dict] = (), max_rewrites: int = MAX_REWRITES) -> tuple[str, CheckReport]`.

- [ ] **Step 1: Write the failing test** (this replaces the truncated block; the file is written in full here)

```python
# tests/test_story.py
from __future__ import annotations

import json
from pathlib import Path

import pytest

from prd_agent import story
from prd_agent.checks import check_story, split_body_footer
from prd_agent.errors import StoryGateError
from prd_agent.llm import FakeLLM

GOOD_BODY = """\
# Your project's memory is your Git repository

**Plain files next to the code they describe, checked by a validator.**

Install from source and initialize the project you would hate to lose.

## The project stops making sense when the chat ends

You open a project after two weeks away and the first hour goes into working out its state. Which experiment finished. What the number in last month's report measured.

## Pick it up cold

A fresh session opens the repo and reads four things: what the project is, where it stands, which task is active, and what the last session proved. Then it works.

## A session's whole life, in four steps

1. Read the state.
2. Do one bounded task.
3. Write the evidence.
4. Publish it.

The next session starts at step one. It does not need the old conversation.
"""

BAD_BODY = GOOD_BODY + "\n\n## Why teams pick it\n\nIt's not a tool. It's a teammate.\n"

REWRITTEN_BODY = GOOD_BODY + "\n\n## Why teams pick it\n\nIt is a teammate for the project, one that reads the repository.\n"

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def test_the_story_prompt_carries_the_vendored_skill_and_the_facts(pcm_run: Path) -> None:
    claims, trends = load(pcm_run / "claims.json"), load(pcm_run / "trends.json")
    positioning = load(pcm_run / "positioning.json")
    prompt = story.build_story_prompt(positioning=positioning, claims=claims, trends=trends)
    assert "The Self-Check" in prompt          # from the vendored SKILL.md
    assert "The contrast reveal" in prompt     # from the vendored ai-tells.md
    assert "The Human Action Model" in prompt  # from the vendored copy-frameworks.md
    assert positioning["differentiator"][:40] in prompt
    assert "never invent" in prompt.lower()

def test_the_story_prompt_forbids_the_footer_and_the_flag_markers(pcm_run: Path) -> None:
    prompt = story.build_story_prompt(
        positioning=load(pcm_run / "positioning.json"),
        claims=load(pcm_run / "claims.json"),
        trends=load(pcm_run / "trends.json"),
    )
    assert "proof and open items" in prompt.lower()
    assert "[NEED:" in prompt
    assert "do not write" in prompt.lower()

def test_the_story_prompt_injects_exemplars_when_they_are_supplied(pcm_run: Path) -> None:
    prompt = story.build_story_prompt(
        positioning=load(pcm_run / "positioning.json"),
        claims=load(pcm_run / "claims.json"),
        trends=load(pcm_run / "trends.json"),
        exemplars=[{"story": "An earlier page about a different artifact."}],
    )
    assert "An earlier page about a different artifact." in prompt

def test_the_first_ever_run_gets_a_template_prompt_with_no_exemplars(pcm_run: Path) -> None:
    # Spec §5: run one has nothing to retrieve from, so the prompt must say so
    # rather than silently showing an empty "worked examples" heading.
    prompt = story.build_story_prompt(
        positioning=load(pcm_run / "positioning.json"),
        claims=load(pcm_run / "claims.json"),
        trends=load(pcm_run / "trends.json"),
    )
    assert "No worked examples are available yet" in prompt
    assert "earlier story" not in prompt

def test_clean_body_strips_a_fenced_wrapper() -> None:
    body, harvested = story.clean_body("```markdown\n# Headline\n\ntext\n```")
    assert body == "# Headline\n\ntext"
    assert harvested == []

def test_clean_body_harvests_a_model_flag_instead_of_failing() -> None:
    body, harvested = story.clean_body("# Headline\n\nWe ship it today. [NEED: proof]\n")
    assert "[NEED:" not in body
    assert harvested[0]["need"] == "proof"

def test_clean_body_ignores_an_unknown_need_kind() -> None:
    body, harvested = story.clean_body("# Headline\n\nWe ship it. [NEED: vibes]\n")
    assert "[NEED:" not in body
    assert harvested == []

def test_the_footer_is_built_from_the_json_not_from_the_model(pcm_run: Path) -> None:
    claims, positioning = load(pcm_run / "claims.json"), load(pcm_run / "positioning.json")
    trends = load(pcm_run / "trends.json")
    report = check_story(GOOD_BODY)
    footer = story.build_footer(claims=claims, positioning=positioning, trends=trends, report=report)
    assert footer.startswith("### Proof and open items")
    assert "| Claim on this page | Source | Status |" in footer
    assert "C-001" not in footer            # the table carries the claim text, not the id
    assert "templates/v1/" in footer        # the evidence from claims.json
    assert "**unknown**" in footer          # an unknown is recorded as unknown
    assert "`[NEED: proof]`" in footer      # every open flag is rendered
    assert "[NEED: differentiator]" in footer
    assert "jaded" in footer                # the market stage is named
    assert "**Self-check.**" in footer
    assert "whether the story lands" in footer

def test_the_footer_renders_the_no_flags_line_when_there_are_none(pcm_run: Path) -> None:
    positioning = load(pcm_run / "positioning.json")
    positioning["flags"] = []
    footer = story.build_footer(
        claims=load(pcm_run / "claims.json"),
        positioning=positioning,
        trends=load(pcm_run / "trends.json"),
        report=check_story(GOOD_BODY),
    )
    assert "Every claim on this page is pointed at in the artifact." in footer

def test_extra_flags_are_merged_into_the_footer(pcm_run: Path) -> None:
    footer = story.build_footer(
        claims=load(pcm_run / "claims.json"),
        positioning=load(pcm_run / "positioning.json"),
        trends=load(pcm_run / "trends.json"),
        report=check_story(GOOD_BODY),
        extra_flags=[{"id": "N-001", "need": "proof", "claim": "Raised by the draft", "unlock": "Evidence."}],
    )
    assert "Raised by the draft" in footer
    assert footer.count("N-001") >= 1

def test_assemble_story_puts_the_footer_behind_the_pitch() -> None:
    page = story.assemble_story("# H\n\nbody\n", "### Proof and open items\n\ntable\n")
    body, footer = split_body_footer(page)
    assert body == "# H\n\nbody"
    assert footer.startswith("### Proof and open items")
    assert page.count("### Proof and open items") == 1

def test_a_clean_first_draft_is_accepted_without_a_second_call(pcm_run: Path) -> None:
    fake = FakeLLM(GOOD_BODY)
    page, report = story.story(
        claims=load(pcm_run / "claims.json"),
        positioning=load(pcm_run / "positioning.json"),
        trends=load(pcm_run / "trends.json"),
        llm=fake,
    )
    assert len(fake.calls) == 1
    assert report.passed() is True
    assert page.endswith("\n")
    assert check_story(split_body_footer(page)[0]).passed() is True

def test_a_banned_draft_is_rewritten_and_the_rewrite_prompt_names_the_finding(pcm_run: Path) -> None:
    fake = FakeLLM([BAD_BODY, REWRITTEN_BODY])
    page, report = story.story(
        claims=load(pcm_run / "claims.json"),
        positioning=load(pcm_run / "positioning.json"),
        trends=load(pcm_run / "trends.json"),
        llm=fake,
    )
    assert len(fake.calls) == 2
    assert report.passed() is True
    assert "contrast_reveal" in str(fake.calls[1]["prompt"])
    assert "It's not a tool" in str(fake.calls[1]["prompt"])
    assert "It is a teammate for the project" in page

def test_a_draft_still_banned_after_the_last_rewrite_fails_the_run(pcm_run: Path) -> None:
    fake = FakeLLM([BAD_BODY, BAD_BODY, BAD_BODY])
    with pytest.raises(StoryGateError) as error:
        story.story(
            claims=load(pcm_run / "claims.json"),
            positioning=load(pcm_run / "positioning.json"),
            trends=load(pcm_run / "trends.json"),
            llm=fake,
        )
    assert "contrast_reveal" in str(error.value)
    assert "3 drafts" in str(error.value)
    assert len(fake.calls) == 3

def test_max_rewrites_zero_allows_one_draft_only(pcm_run: Path) -> None:
    fake = FakeLLM([BAD_BODY])
    with pytest.raises(StoryGateError):
        story.story(
            claims=load(pcm_run / "claims.json"),
            positioning=load(pcm_run / "positioning.json"),
            trends=load(pcm_run / "trends.json"),
            llm=fake,
            max_rewrites=0,
        )
    assert len(fake.calls) == 1

def test_the_rewrite_prompt_repeats_the_facts_not_just_the_findings(pcm_run: Path) -> None:
    prompt = story.build_rewrite_prompt(
        body=BAD_BODY,
        report=check_story(BAD_BODY),
        positioning=load(pcm_run / "positioning.json"),
        claims=load(pcm_run / "claims.json"),
    )
    assert "contrast_reveal" in prompt
    assert "It's not a tool" in prompt
    assert "Rewrite from the facts" in prompt
    assert "a validator checks it" in prompt  # the differentiator, restated for the rewrite
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python -m pytest tests/test_story.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent.story'`.

- [ ] **Step 3: Write the implementation**

```python
# src/prd_agent/story.py
"""Draft the marketing story through the vendored copywriting skill, then gate it.

The model writes the pitch body only. The proof table, the open flags and the self-check
paragraph are assembled here from the stage JSON and the checker's report, so the page can
never claim more than the pipeline established. A draft that trips a hard ban is rewritten
from the facts; a draft still banned after MAX_REWRITES fails the run and writes nothing.
"""

from __future__ import annotations

import json
import re

from prd_agent import flags
from prd_agent.checks import FOOTER_HEADING, CheckReport, check_story
from prd_agent.errors import StoryGateError
from prd_agent.llm import LLM
from prd_agent.skill import build_skill_context

MAX_REWRITES = 2
_FENCE_WRAPPER = re.compile(r"^```[a-zA-Z]*\n(.*?)\n?```$", re.DOTALL)

STORY_SYSTEM = (
    "You are an expert conversion copywriter working from a positioning brief that was derived "
    "from the product's own artifact. You write the marketing page. Hype is uncapped: you are "
    "selling the reader's future, not inventorying the product. You never invent a fact the "
    "brief does not carry. You never write the proof section, the open flags or the self-check "
    "paragraph; the pipeline appends those. Follow the vendored copywriting skill and its "
    "references exactly, including its self-check, and return the page body as markdown only."
)

_PROMPT_TEMPLATE = """\
Write the marketing page body for this product.

Rules, in order of importance:
1. Sell the reader's future. The page is not an inventory of what the product does and does not
   do. Every section should make the reader want the state the product creates.
2. Write only what the brief and the claims support. If a claim is not supported, leave it out
   rather than inventing it. Never state an `unknown` claim as fact.
3. Never contradict what the artifact is. A command line tool is never sold as a graphical app.
4. Hype is uncapped. Invented-sounding numbers are allowed unless they contradict the claims.
5. Do not write the proof table, the open flags or the self-check paragraph. Do not write the
   marker `[NEED:` anywhere in the body: the pipeline appends the flags it already holds. If a
   claim needs evidence, leave the claim out and it will stay flagged in the footer.
6. Structure: a hero (headline, subhead, one line of install or entry), then a problem section
   that names the reader's situation in the second person, then a section describing the better
   state, then a numbered path to action with at least three steps, then a closing call to
   action. Competitor positioning stays out of the pitch body.
7. Run the skill's own self-check before you answer. Banned patterns fail the gate and cost a
   rewrite: contrast reveals, negation lists, trailing pile-ons, self-answered questions, colon
   reveals, stock phrases, hype punctuation, and em dashes in headings or the hero.

The vendored skill and its references follow. Obey them.

{skill}

The positioning brief follows.

{positioning}

The claims, so you never contradict the artifact:

{claims}

The market stage and the competitor language, so you know how loud to go:

{trends}

{exemplars}
"""

def _bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)

def _exemplar_block(exemplars: list[dict]) -> str:
    if not exemplars:
        return "No worked examples are available yet. This is an early run."
    parts = [
        "Worked examples from earlier runs. Use their shape, their register and their level of "
        "specificity. Do not reuse their subject matter.",
    ]
    for exemplar in exemplars:
        story_text = str(exemplar.get("story", "")).strip()
        if story_text:
            parts.append(f"\n--- earlier story ---\n{story_text}")
    return "\n".join(parts)

def build_story_prompt(
    *,
    positioning: dict,
    claims: dict,
    trends: dict,
    exemplars: list[dict] = (),
) -> str:
    return _PROMPT_TEMPLATE.format(
        skill=build_skill_context(),
        positioning=json.dumps(positioning, indent=2, ensure_ascii=False),
        claims=json.dumps(claims, indent=2, ensure_ascii=False),
        trends=json.dumps(trends, indent=2, ensure_ascii=False),
        exemplars=_exemplar_block(list(exemplars)),
    )

def build_rewrite_prompt(
    *,
    body: str,
    report: CheckReport,
    positioning: dict,
    claims: dict,
) -> str:
    findings = report.bans + report.cap_violations()
    listed = _bullet_lines(
        [f"{finding.rule} (line {finding.line}, section {finding.section}): {finding.text.strip()}" for finding in findings]
    )
    return (
        "The draft below failed the copywriting skill's self-check. Rewrite the whole draft.\n\n"
        "Rewrite from the facts. Go back to the mechanism, the number and the reader, and write "
        "that. Swapping a banned phrase for a synonym produces a new tell. Keep every section, "
        "keep the numbered path to action, and keep the same structure.\n\n"
        "What failed:\n\n"
        f"{listed}\n\n"
        "The positioning brief, so the rewrite keeps the mechanism and the differentiator:\n\n"
        f"{json.dumps(positioning, indent=2, ensure_ascii=False)}\n\n"
        "The claims, so the rewrite stays inside what is established:\n\n"
        f"{json.dumps(claims, indent=2, ensure_ascii=False)}\n\n"
        "The draft to rewrite:\n\n"
        f"{body}\n"
    )

def clean_body(raw: str) -> tuple[str, list[dict]]:
    """Strip a fence wrapper and harvest any flag the model raised.

    The pitch body must not carry `[NEED: ...]` markers, because the footer is code-built. A
    model that raises one anyway is not punished: the marker is removed from the pitch and the
    flag joins the footer.
    """
    text = raw.strip()
    wrapped = _FENCE_WRAPPER.match(text)
    if wrapped:
        text = wrapped.group(1).strip()
    harvested: list[dict] = []

    def _harvest(match: re.Match[str]) -> str:
        need = match.group(1)
        if need in flags.NEED_KINDS:
            harvested.append(
                flags.make_flag(harvested, need, "Raised by the draft", "Evidence that resolves it.")
            )
        return ""

    text = flags.FLAG_PATTERN.sub(_harvest, text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, harvested

def build_proof_table(claims: dict) -> str:
    rows = ["| Claim on this page | Source | Status |", "|---|---|---|"]
    for claim in claims.get("claims", []):
        text = " ".join(str(claim.get("text", "")).split())
        if len(text) > 90:
            text = text[:87].rstrip() + "..."
        evidence = str(claim.get("evidence", "")).strip() or "none recorded"
        rows.append(f"| {text} | {evidence} | {claim.get('status', 'unknown')} |")
    for unknown in claims.get("unknowns", []):
        rows.append(f"| {' '.join(str(unknown).split())} | no source in the artifact | **unknown** |")
    return "\n".join(rows)

def build_trends_note(trends: dict) -> str:
    category = trends.get("category", {})
    stage = category.get("sophistication_stage", "unknown")
    note = category.get("stage_note", "")
    urls = [str(item.get("url", "")) for item in category.get("competitors", []) if item.get("url")]
    urls.extend(str(item.get("url", "")) for item in trends.get("cultural", []) if item.get("url"))
    unique = list(dict.fromkeys(urls))
    lines = [f"**Trends used.** Market stage: {stage} (Schwartz). {note}".rstrip()]
    if unique:
        lines.append("Sources read for the category register and the cultural moment: " + ", ".join(unique) + ".")
    searched_at = str(trends.get("searched_at", "")).strip()
    if searched_at:
        lines.append(f"Searched at {searched_at}.")
    return "\n\n".join(lines)

def build_footer(
    *,
    claims: dict,
    positioning: dict,
    trends: dict,
    report: CheckReport,
    extra_flags: list[dict] = (),
) -> str:
    merged = flags.merge_flags(list(positioning.get("flags", [])), list(extra_flags))
    swap = positioning.get("swap_test", {})
    verdict = "Passed" if swap.get("passed") else "Failed"
    lines = [
        FOOTER_HEADING,
        "",
        "Not part of the pitch above. Recorded here so the page can be audited without being flattened by it.",
        "",
        build_proof_table(claims),
        "",
        f"**Swap test.** {verdict}. {swap.get('note', '')}".rstrip(),
        "",
        flags.render_flags(merged),
        "",
        build_trends_note(trends),
        "",
        report.summary(),
    ]
    return "\n".join(lines).strip() + "\n"

def assemble_story(body: str, footer: str) -> str:
    return f"{body.strip()}\n\n---\n\n{footer.strip()}\n"

def story(
    *,
    claims: dict,
    positioning: dict,
    trends: dict,
    llm: LLM,
    exemplars: list[dict] = (),
    max_rewrites: int = MAX_REWRITES,
) -> tuple[str, CheckReport]:
    """Draft, gate, rewrite, and return (whole page, report of the accepted draft)."""
    body = ""
    report: CheckReport | None = None
    harvested: list[dict] = []
    for attempt in range(max_rewrites + 1):
        if attempt == 0:
            prompt = build_story_prompt(
                positioning=positioning, claims=claims, trends=trends, exemplars=list(exemplars)
            )
        else:
            assert report is not None
            prompt = build_rewrite_prompt(body=body, report=report, positioning=positioning, claims=claims)
        body, harvested = clean_body(llm.complete(system=STORY_SYSTEM, prompt=prompt))
        report = check_story(body)
        if report.passed():
            footer = build_footer(
                claims=claims,
                positioning=positioning,
                trends=trends,
                report=report,
                extra_flags=harvested,
            )
            return assemble_story(body, footer), report
    assert report is not None
    failed = ", ".join(sorted({finding.rule for finding in report.bans + report.cap_violations()}))
    raise StoryGateError(
        f"the draft still trips the self-check after {max_rewrites + 1} drafts: {failed}. "
        "Nothing was written. The findings are listed above; rewrite from the facts and re-run."
    )
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_story.py -v`
Expected: 16 passed.

- [ ] **Step 5: Run the whole suite so far**

Run: `python -m pytest -v`
Expected: all tests pass, no network access. If `tests/test_checks.py` now fails on `GOOD_BODY`, the checker is wrong, not the fixture: tighten the rule and add the sentence as a negative case.

- [ ] **Step 6: Commit**

```bash
git add src/prd_agent/story.py tests/test_story.py
git commit -m "feat: add the story stage with the code-built footer and the rewrite gate"
```

---

## Task 11: The CLI and the package entry point (spec §3.5)

**Files:**
- Create: `src/prd_agent/pipeline.py`, `src/prd_agent/cli.py`, `src/prd_agent/__main__.py`
- Test: `tests/test_pipeline.py`, `tests/test_cli.py`

**Interfaces:**
- Consumes: `intake.intake(root, llm, *, artifact=None) -> dict`; `positioning.positioning(claims, trends, llm, *, answers=None) -> dict`; `story.story(*, claims, positioning, trends, llm, exemplars=(), max_rewrites=MAX_REWRITES) -> tuple[str, CheckReport]`; `artifact.collect_artifact(root) -> Artifact`; `llm.LLM`, `llm.default_llm()`; `schemas.require_valid`, `schemas.TRENDS_SPEC`; `flags.ask_questions(flags, *, input_fn=input) -> dict[str, str]`; `errors.StageError`.
- Produces: `RunResult(task_name: str, run_dir: Path, story_path: Path, claims_path: Path, trends_path: Path, positioning_path: Path, flags: list[dict] = [], report: CheckReport | None = None, awaiting_answers: bool = False)`, `run_dir(root: Path, name: str) -> Path`, `default_out(root: Path, name: str) -> Path`, `load_trends(path: Path) -> dict`, `cli.build_parser() -> argparse.ArgumentParser`, `cli.main(argv: list[str] | None = None) -> int`.

`report` is `CheckReport | None` because a human-mode run that stops at the flag loop has no draft to check yet. `RunResult` is a dataclass, so the later fields carry defaults and a run that stops early can leave them unset.

**The final `run` signature**, given here so every later task edits one known shape rather than inventing parameters:

```python
def run(
    artifact_path: Path,
    *,
    llm: LLM,
    trends: dict | None = None,
    trends_file: Path | None = None,
    out: Path | None = None,
    autonomous: bool = False,
    ask=None,
    answers: dict[str, str] | None = None,   # Task 12
    live: bool = True,                       # Task 13
    evals_path: Path | None = None,          # Task 14
) -> RunResult:
```

This task implements the body up to `ask`. Task 12 adds `answers`, Task 13 adds `live`, Task 14 adds `evals_path`; each states the parameter it adds and where it goes.

At this task the live trend pass does not exist yet, so a run needs a trends source: `--trends-file tests/fixtures/trends_pcm.json`. Task 13 replaces the raise with the live call.

- [ ] **Step 1: Write the failing pipeline test**

```python
# tests/test_pipeline.py
from __future__ import annotations

import json
from pathlib import Path

import pytest

from prd_agent import pipeline
from prd_agent.errors import StageError
from prd_agent.llm import FakeLLM

GOOD_BODY = (Path(__file__).parent / "test_story.py").read_text(encoding="utf-8").split('GOOD_BODY = """\\\n')[1].split('"""')[0]

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def test_run_dir_and_default_out_are_derived_from_the_artifact_name(tmp_path: Path) -> None:
    assert pipeline.run_dir(tmp_path, "mini") == tmp_path / "runs" / "mini"
    assert pipeline.default_out(tmp_path, "mini") == tmp_path / "stories" / "mini.md"

def test_load_trends_rejects_a_broken_fixture(tmp_path: Path) -> None:
    path = tmp_path / "trends.json"
    path.write_text('{"schema": "prd-agent.trends.v1"}', encoding="utf-8")
    with pytest.raises(StageError):
        pipeline.load_trends(path)

def test_a_run_without_a_trends_source_says_what_to_pass(tmp_path: Path) -> None:
    with pytest.raises(StageError) as error:
        pipeline.run(tmp_path, llm=FakeLLM("{}"), autonomous=True)
    assert "--trends-file" in str(error.value)

def test_autonomous_run_writes_every_intermediate_document_and_the_story(
    tmp_path: Path, repo_root: Path, pcm_run: Path
) -> None:
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n\nA tiny artifact.\n", encoding="utf-8")
    fake = FakeLLM([
        (pcm_run / "claims.json").read_text(encoding="utf-8"),
        (pcm_run / "positioning.json").read_text(encoding="utf-8"),
        GOOD_BODY,
    ])
    result = pipeline.run(
        artifact,
        llm=fake,
        trends_file=repo_root / "tests" / "fixtures" / "trends_pcm.json",
        autonomous=True,
    )
    assert result.task_name == "mini"
    assert result.awaiting_answers is False
    assert result.claims_path == tmp_path / "runs" / "mini" / "claims.json"
    assert result.claims_path.is_file()
    assert result.trends_path.is_file()
    assert result.positioning_path.is_file()
    assert result.story_path == tmp_path / "stories" / "mini.md"
    assert result.story_path.is_file()
    assert result.report.passed() is True
    assert load(result.positioning_path)["schema"] == "prd-agent.positioning.v1"
    assert "### Proof and open items" in result.story_path.read_text(encoding="utf-8")
    assert [flag["need"] for flag in result.flags] == ["proof", "proof", "proof", "differentiator"]

def test_the_stage_order_is_intake_then_positioning_then_story(tmp_path: Path, repo_root: Path, pcm_run: Path) -> None:
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    fake = FakeLLM([
        (pcm_run / "claims.json").read_text(encoding="utf-8"),
        (pcm_run / "positioning.json").read_text(encoding="utf-8"),
        GOOD_BODY,
    ])
    pipeline.run(
        artifact,
        llm=fake,
        trends_file=repo_root / "tests" / "fixtures" / "trends_pcm.json",
        autonomous=True,
    )
    first, second, third = (str(call["prompt"]) for call in fake.calls)
    assert "claims" in first.lower() and "artifact excerpt" in first.lower()
    assert "differentiator" in second and "Mem0" in second
    assert "positioning brief follows" in third

def test_human_mode_stops_at_the_flag_loop_and_writes_no_story(
    tmp_path: Path, repo_root: Path, pcm_run: Path
) -> None:
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    fake = FakeLLM([
        (pcm_run / "claims.json").read_text(encoding="utf-8"),
        (pcm_run / "positioning.json").read_text(encoding="utf-8"),
    ])
    result = pipeline.run(
        artifact,
        llm=fake,
        trends_file=repo_root / "tests" / "fixtures" / "trends_pcm.json",
        autonomous=False,
    )
    assert result.awaiting_answers is True
    assert result.flags
    assert not result.story_path.exists()
    assert len(fake.calls) == 2
```

- [ ] **Step 2: Write the failing CLI test**

```python
# tests/test_cli.py
from __future__ import annotations

import json
from pathlib import Path

from prd_agent import cli

def test_the_documented_invocation_parses() -> None:
    args = cli.build_parser().parse_args(["../some-repo"])
    assert args.artifact_path == "../some-repo"
    assert args.autonomous is False
    assert args.out is None
    assert args.trends_file is None
    assert args.answers_file is None

def test_autonomous_and_out_parse() -> None:
    args = cli.build_parser().parse_args(["repo", "--autonomous", "--out", "stories/x.md"])
    assert args.autonomous is True
    assert args.out == "stories/x.md"

def test_main_runs_end_to_end_offline(tmp_path: Path, repo_root: Path, pcm_run: Path, monkeypatch) -> None:
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    canned = tmp_path / "canned"
    canned.mkdir()
    for index, source in enumerate(
        [pcm_run / "claims.json", pcm_run / "positioning.json"],
        start=1,
    ):
        (canned / f"{index:02d}.txt").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (canned / "03.txt").write_text(
        (Path(__file__).parent / "test_story.py").read_text(encoding="utf-8").split('GOOD_BODY = """\\\n')[1].split('"""')[0],
        encoding="utf-8",
    )
    monkeypatch.setenv("PRD_AGENT_LLM", "fake")
    monkeypatch.setenv("PRD_AGENT_CANNED_DIR", str(canned))
    monkeypatch.chdir(tmp_path)
    code = cli.main([
        str(artifact),
        "--autonomous",
        "--trends-file", str(repo_root / "tests" / "fixtures" / "trends_pcm.json"),
    ])
    assert code == 0
    written = tmp_path / "stories" / "mini.md"
    assert written.is_file()
    assert "### Proof and open items" in written.read_text(encoding="utf-8")
    assert json.loads((tmp_path / "runs" / "mini" / "positioning.json").read_text(encoding="utf-8"))["schema"] == "prd-agent.positioning.v1"

def test_main_reports_a_stage_failure_with_a_nonzero_code(tmp_path: Path, capsys) -> None:
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    code = cli.main([str(artifact), "--autonomous"])
    assert code == 2
    assert "--trends-file" in capsys.readouterr().err
```

- [ ] **Step 3: Run them and watch them fail**

Run: `python -m pytest tests/test_pipeline.py tests/test_cli.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent.pipeline'`.

- [ ] **Step 4: Write the implementation**

```python
# src/prd_agent/pipeline.py
"""One entry point over the four stages, the two modes, and the runs/<name>/ writes.

Every stage document is written beside the story so any stage can be inspected or re-run in
isolation. The mode difference is a single boolean; see spec section 4.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from prd_agent import intake, positioning as positioning_stage, story as story_stage
from prd_agent.artifact import Artifact, collect_artifact
from prd_agent.checks import CheckReport, check_story
from prd_agent.errors import StageError
from prd_agent.llm import LLM
from prd_agent.schemas import TRENDS_SPEC, require_valid

RUNS_DIR = "runs"
STORIES_DIR = "stories"

@dataclass
class RunResult:
    task_name: str
    run_dir: Path
    story_path: Path
    claims_path: Path
    trends_path: Path
    positioning_path: Path
    flags: list[dict] = field(default_factory=list)
    report: CheckReport | None = None
    awaiting_answers: bool = False

def run_dir(root: Path, name: str) -> Path:
    return Path(root) / RUNS_DIR / name

def default_out(root: Path, name: str) -> Path:
    return Path(root) / STORIES_DIR / f"{name}.md"

def load_trends(path: Path) -> dict:
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StageError(f"{path} is not readable JSON: {exc}") from exc
    require_valid(doc, TRENDS_SPEC, str(path))
    return doc

def _write_json(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def run(
    artifact_path: Path,
    *,
    llm: LLM,
    trends: dict | None = None,
    trends_file: Path | None = None,
    out: Path | None = None,
    autonomous: bool = False,
    ask=None,
) -> RunResult:
    """Run intake, trends, positioning and story. Human mode stops at the flag loop."""
    artifact_path = Path(artifact_path)
    if not artifact_path.exists():
        raise StageError(f"artifact path does not exist: {artifact_path}")
    root = artifact_path.resolve().parent
    name = artifact_path.resolve().name

    if trends is not None:
        trends_doc = trends
        require_valid(trends_doc, TRENDS_SPEC, "trends.json")
    elif trends_file is not None:
        trends_doc = load_trends(Path(trends_file))
    else:
        raise StageError(
            "no trends source. Pass --trends-file <path> until the live web pass lands."
        )

    collected: Artifact = collect_artifact(artifact_path)
    claims = intake.intake(artifact_path, llm, artifact=collected)
    positioned = positioning_stage.positioning(claims, trends_doc, llm)

    target_run_dir = run_dir(root, name)
    target_story = Path(out) if out is not None else default_out(root, name)
    _write_json(target_run_dir / "claims.json", claims)
    _write_json(target_run_dir / "trends.json", trends_doc)
    _write_json(target_run_dir / "positioning.json", positioned)

    result = RunResult(
        task_name=name,
        run_dir=target_run_dir,
        story_path=target_story,
        claims_path=target_run_dir / "claims.json",
        trends_path=target_run_dir / "trends.json",
        positioning_path=target_run_dir / "positioning.json",
        flags=list(positioned.get("flags", [])),
    )

    if not autonomous:
        result.awaiting_answers = True
        return result

    page, report = story_stage.story(
        claims=claims, positioning=positioned, trends=trends_doc, llm=llm
    )
    target_story.parent.mkdir(parents=True, exist_ok=True)
    target_story.write_text(page, encoding="utf-8")
    result.report = report
    return result
```

```python
# src/prd_agent/cli.py
"""python -m prd_agent <artifact-path> [--autonomous] [--out stories/<name>.md]

Run from the repository root. Without --autonomous the run stops at the flag loop.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from prd_agent.errors import StageError
from prd_agent.llm import default_llm
from prd_agent.pipeline import run

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prd-agent",
        description="Turn a builder's own artifact into a product story that sells.",
    )
    parser.add_argument("artifact_path", help="path to the artifact repository to read")
    parser.add_argument(
        "--autonomous",
        action="store_true",
        help="complete the run and ship the flag footer instead of stopping to ask",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="where to write the story (default: stories/<artifact-name>.md)",
    )
    parser.add_argument(
        "--trends-file",
        default=None,
        help="read trends.json from this path instead of running the live web pass",
    )
    parser.add_argument(
        "--answers-file",
        default=None,
        help="a JSON object of flag id to answer, used instead of reading stdin",
    )
    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        llm = default_llm()
        result = run(
            Path(args.artifact_path),
            llm=llm,
            trends_file=Path(args.trends_file) if args.trends_file else None,
            out=Path(args.out) if args.out else None,
            autonomous=args.autonomous,
        )
    except StageError as error:
        print(f"prd-agent: {error}", file=sys.stderr)
        return 2
    if result.awaiting_answers:
        print(f"prd-agent: {len(result.flags)} open flags. Answer them and re-run with --answers-file, "
              f"or re-run with --autonomous to ship them as the footer.")
        for flag in result.flags:
            print(f"  [{flag['id']}] {flag['need']}: {flag['claim']} (unlock: {flag['unlock']})")
        return 0
    print(f"prd-agent: wrote {result.story_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

```python
# src/prd_agent/__main__.py
"""`python -m prd_agent` entry point. The parser lives in prd_agent.cli."""

from __future__ import annotations

from prd_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_pipeline.py tests/test_cli.py -v`
Expected: 10 passed.

- [ ] **Step 6: Confirm the documented invocation works offline**

```bash
python -m prd_agent tests/fixtures/artifact-mini --autonomous \
  --trends-file tests/fixtures/trends_pcm.json \
  --out /tmp/mini-check.md
```

Expected: `prd-agent:` with an error naming `ANTHROPIC_API_KEY`, exit code 2. That is the correct fail-closed behaviour without credentials; the canned path is covered by `test_main_runs_end_to_end_offline`.

- [ ] **Step 7: Commit**

```bash
git add src/prd_agent/pipeline.py src/prd_agent/cli.py src/prd_agent/__main__.py tests/test_pipeline.py tests/test_cli.py
git commit -m "feat: add the pipeline entry point, the CLI and the runs/ writes"
```

---

## Task 12: The flag loop and the two modes (spec §4, build order step 5)

**Files:**
- Modify: `src/prd_agent/pipeline.py`
- Modify: `src/prd_agent/cli.py`
- Test: `tests/test_pipeline.py` (append), `tests/test_cli.py` (append)

**Interfaces:**
- Consumes: `flags.ask_questions`, `flags.answers_as_prompt`, `positioning.positioning(..., answers=...)`; `RunResult`.
- Produces: `answers_from_file(path: Path) -> dict[str, str]`, `close_flag_loop(result: RunResult, *, llm: LLM, answers: dict[str, str]) -> RunResult`, and a changed `run(...)` that gains `answers: dict[str, str] | None = None` after `ask` and closes the loop when answers are available.

`close_flag_loop` takes only the stopped `result`, the model and the answers: it re-reads `claims.json`, `trends.json` and `positioning.json` from `result.run_dir` through the paths the result already carries, so the caller does not re-pass documents that are already on disk.

- [ ] **Step 1: Write the failing test (append to `tests/test_pipeline.py`)**

```python
# tests/test_pipeline.py (append)
def test_answers_are_folded_back_into_positioning_and_the_story_is_regenerated(
    tmp_path: Path, repo_root: Path, pcm_run: Path
) -> None:
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    revised = load(pcm_run / "positioning.json")
    revised["flags"] = [flag for flag in revised["flags"] if flag["need"] != "proof"]
    fake = FakeLLM([
        (pcm_run / "claims.json").read_text(encoding="utf-8"),
        (pcm_run / "positioning.json").read_text(encoding="utf-8"),
        json.dumps(revised),
        GOOD_BODY,
    ])
    asked: list[list[dict]] = []

    def ask(flags: list[dict]) -> dict[str, str]:
        asked.append(flags)
        return {"N-001": "40 adopters, listed in the README."}

    result = pipeline.run(
        artifact,
        llm=fake,
        trends_file=repo_root / "tests" / "fixtures" / "trends_pcm.json",
        autonomous=False,
        ask=ask,
    )
    assert asked and asked[0][0]["id"] == "N-001"
    assert result.awaiting_answers is False
    assert result.story_path.is_file()
    assert "40 adopters, listed in the README." in str(fake.calls[2]["prompt"])
    assert "no answer" in str(fake.calls[2]["prompt"])
    assert load(result.positioning_path)["flags"] == [flag for flag in revised["flags"]]
    assert len(fake.calls) == 4

def test_the_loop_is_the_same_codepath_in_both_modes(
    tmp_path: Path, repo_root: Path, pcm_run: Path
) -> None:
    """Autonomous mode is one boolean: the same stages, with the questions answered by nobody."""
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    scripted = [
        (pcm_run / "claims.json").read_text(encoding="utf-8"),
        (pcm_run / "positioning.json").read_text(encoding="utf-8"),
        GOOD_BODY,
    ]
    autonomous = pipeline.run(
        artifact, llm=FakeLLM(scripted),
        trends_file=repo_root / "tests" / "fixtures" / "trends_pcm.json", autonomous=True,
    )
    human = pipeline.run(
        artifact, llm=FakeLLM(scripted),
        trends_file=repo_root / "tests" / "fixtures" / "trends_pcm.json",
        autonomous=False, answers={},
    )
    assert autonomous.story_path.read_text(encoding="utf-8") == human.story_path.read_text(encoding="utf-8")

def test_an_unanswered_flag_stays_in_the_footer(tmp_path: Path, repo_root: Path, pcm_run: Path) -> None:
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    fake = FakeLLM([
        (pcm_run / "claims.json").read_text(encoding="utf-8"),
        (pcm_run / "positioning.json").read_text(encoding="utf-8"),
        (pcm_run / "positioning.json").read_text(encoding="utf-8"),
        GOOD_BODY,
    ])
    result = pipeline.run(
        artifact, llm=fake,
        trends_file=repo_root / "tests" / "fixtures" / "trends_pcm.json",
        autonomous=False, ask=lambda flags: {},
    )
    page = result.story_path.read_text(encoding="utf-8")
    assert page.count("`[NEED: proof]`") == 3
    assert result.flags

def test_answers_from_file_reads_a_flag_id_map(tmp_path: Path) -> None:
    path = tmp_path / "answers.json"
    path.write_text('{"N-001": "40 adopters"}', encoding="utf-8")
    assert pipeline.answers_from_file(path) == {"N-001": "40 adopters"}

def test_answers_from_file_rejects_a_non_object(tmp_path: Path) -> None:
    path = tmp_path / "answers.json"
    path.write_text('["nope"]', encoding="utf-8")
    with pytest.raises(StageError):
        pipeline.answers_from_file(path)
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python -m pytest tests/test_pipeline.py -v`
Expected: FAIL — `TypeError: run() got an unexpected keyword argument 'answers'` and `AttributeError: module 'prd_agent.pipeline' has no attribute 'answers_from_file'`.

- [ ] **Step 3: Write the implementation (replace the tail of `run` and add two functions)**

```python
# src/prd_agent/pipeline.py (replace the human-mode tail of run)
    if not autonomous and answers is None and ask is None:
        result.awaiting_answers = True
        return result

    if not autonomous:
        supplied = answers if answers is not None else ask(list(positioned.get("flags", [])))
        positioned = positioning_stage.positioning(
            claims,
            trends_doc,
            llm,
            answers=flags.answers_as_prompt(list(positioned.get("flags", [])), supplied),
        )
        _write_json(target_run_dir / "positioning.json", positioned)
        result.flags = list(positioned.get("flags", []))

    page, report = story_stage.story(
        claims=claims, positioning=positioned, trends=trends_doc, llm=llm
    )
    target_story.parent.mkdir(parents=True, exist_ok=True)
    target_story.write_text(page, encoding="utf-8")
    result.report = report
    result.awaiting_answers = False
    return result
```

```python
# src/prd_agent/pipeline.py (add to the imports and below load_trends)
from prd_agent import flags as flags_module

def answers_from_file(path: Path) -> dict[str, str]:
    """Read a `{flag id: answer}` map so a run can be driven without stdin."""
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StageError(f"{path} is not readable JSON: {exc}") from exc
    if not isinstance(doc, dict):
        raise StageError(f"{path} must be a JSON object of flag id to answer")
    return {str(key): str(value) for key, value in doc.items()}
```

and change the signature line to:

```python
def run(
    artifact_path: Path,
    *,
    llm: LLM,
    trends: dict | None = None,
    trends_file: Path | None = None,
    out: Path | None = None,
    autonomous: bool = False,
    ask: Callable[[list[dict]], dict[str, str]] | None = None,
    answers: dict[str, str] | None = None,
) -> RunResult:
```

with `from typing import Callable` added to the imports.

- [ ] **Step 4: Wire `--answers-file` into the CLI (append to `tests/test_cli.py` first)**

```python
# tests/test_cli.py (append)
def test_answers_file_parses_and_reaches_the_run(tmp_path: Path, repo_root: Path, pcm_run: Path, monkeypatch) -> None:
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    answers = tmp_path / "answers.json"
    answers.write_text('{"N-001": "40 adopters"}', encoding="utf-8")
    canned = tmp_path / "canned"
    canned.mkdir()
    for index, source in enumerate([pcm_run / "claims.json", pcm_run / "positioning.json", pcm_run / "positioning.json"], start=1):
        (canned / f"{index:02d}.txt").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (canned / "04.txt").write_text(
        (Path(__file__).parent / "test_story.py").read_text(encoding="utf-8").split('GOOD_BODY = """\\\n')[1].split('"""')[0],
        encoding="utf-8",
    )
    monkeypatch.setenv("PRD_AGENT_LLM", "fake")
    monkeypatch.setenv("PRD_AGENT_CANNED_DIR", str(canned))
    monkeypatch.chdir(tmp_path)
    code = cli.main([
        str(artifact),
        "--trends-file", str(repo_root / "tests" / "fixtures" / "trends_pcm.json"),
        "--answers-file", str(answers),
    ])
    assert code == 0
    assert (tmp_path / "stories" / "mini.md").is_file()
```

Then in `cli.py`, inside `main`, replace the `run(...)` call so answers flow through:

```python
        result = run(
            Path(args.artifact_path),
            llm=llm,
            trends_file=Path(args.trends_file) if args.trends_file else None,
            out=Path(args.out) if args.out else None,
            autonomous=args.autonomous,
            answers=answers_from_file(Path(args.answers_file)) if args.answers_file else None,
        )
```

with `from prd_agent.pipeline import answers_from_file, run` and `from prd_agent import flags as flags_module` added, and the human-mode print block replaced by:

```python
    if result.awaiting_answers:
        answers = flags_module.ask_questions(result.flags)
        result = close_flag_loop(result, llm=llm, answers=answers)
        if result.story_path.is_file():
            print(f"prd-agent: wrote {result.story_path}")
            return 0
        return 0
```

and this added to `pipeline.py` so the CLI never needs to re-enter `run`:

```python
# src/prd_agent/pipeline.py (append)
def close_flag_loop(result: RunResult, *, llm: LLM, answers: dict[str, str]) -> RunResult:
    """Resume a stopped human-mode run with the owner's answers.

    Reads the documents already on disk, folds the answers back into positioning, regenerates
    the story and rewrites the affected files.
    """
    claims = json.loads(result.claims_path.read_text(encoding="utf-8"))
    trends_doc = json.loads(result.trends_path.read_text(encoding="utf-8"))
    positioned = json.loads(result.positioning_path.read_text(encoding="utf-8"))
    revised = positioning_stage.positioning(
        claims,
        trends_doc,
        llm,
        answers=flags_module.answers_as_prompt(list(positioned.get("flags", [])), answers),
    )
    _write_json(result.positioning_path, revised)
    page, report = story_stage.story(
        claims=claims, positioning=revised, trends=trends_doc, llm=llm
    )
    result.story_path.parent.mkdir(parents=True, exist_ok=True)
    result.story_path.write_text(page, encoding="utf-8")
    result.flags = list(revised.get("flags", []))
    result.report = report
    result.awaiting_answers = False
    return result
```

- [ ] **Step 5: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_pipeline.py tests/test_cli.py -v`
Expected: 17 passed.

- [ ] **Step 6: Commit**

```bash
git add src/prd_agent/pipeline.py src/prd_agent/cli.py tests/test_pipeline.py tests/test_cli.py
git commit -m "feat: close the flag loop and add the answers-file seam for the two modes"
```

---

## Task 13: `trends.py` and the live web pass (spec §3.2, build order step 6)

**Files:**
- Create: `src/prd_agent/trends.py`
- Modify: `src/prd_agent/pipeline.py` (replace the "no trends source" raise with the live call), `src/prd_agent/cli.py` (add `--no-web`)
- Test: `tests/test_trends.py`, `tests/test_pipeline.py` (append)

**Interfaces:**
- Consumes: `llm.LLM`, `llm.extract_json`, `llm.WEB_SEARCH_TOOL`; `schemas.TRENDS_SPEC`, `schemas.TRENDS_SCHEMA`, `schemas.require_valid`, `schemas.SOPHISTICATION_STAGES`; `errors.ModelOutputError`.
- Produces: `TRENDS_SYSTEM`, `STAGE_BRIEF: dict[str, str]`, `build_trends_prompt(claims, *, searched_at) -> str`, `search_tools() -> list[dict]`, `analyze(claims, llm, *, searched_at=None) -> dict`.

**How search is performed, and why.** The one model call carries Anthropic's server-side `web_search` tool (`llm.WEB_SEARCH_TOOL`), so the searching happens inside the same request and the results arrive with URLs we can record. The alternatives were rejected on dependency grounds: `urllib` against a search API needs a second credential and a service that keeps working, and fetching and parsing HTML needs a parser. The tool costs no new dependency, no new credential and no scraping, and it keeps the network behind the existing `LLM` seam, so every test below runs with `FakeLLM` and never touches the network.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_trends.py
from __future__ import annotations

import json
from pathlib import Path

import pytest

from prd_agent import trends
from prd_agent.errors import ModelOutputError, SchemaError
from prd_agent.llm import FakeLLM
from prd_agent.schemas import validate_trends

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def test_the_prompt_names_all_three_trend_kinds_and_the_stage_question(pcm_run: Path) -> None:
    prompt = trends.build_trends_prompt(load(pcm_run / "claims.json"), searched_at="2026-10-13")
    assert "Category." in prompt and "Style." in prompt and "Cultural." in prompt
    assert "virgin" in prompt and "crowded" in prompt and "jaded" in prompt and "exhausted" in prompt
    assert "the memory is the Git repository" in prompt  # the artifact's own claim reaches the search

def test_the_prompt_carries_the_artifact_claims_verbatim(pcm_run: Path) -> None:
    claims = load(pcm_run / "claims.json")
    prompt = trends.build_trends_prompt(claims, searched_at="2026-10-13")
    assert claims["claims"][0]["text"] in prompt
    assert claims["claims"][0]["evidence"] in prompt

def test_the_web_search_tool_is_attached_to_the_one_call(pcm_run: Path) -> None:
    fake = FakeLLM(json.dumps(load(pcm_run / "trends.json")))
    trends.analyze(load(pcm_run / "claims.json"), fake, searched_at="2026-10-13")
    assert fake.calls[0]["tools"] == [trends.llm.WEB_SEARCH_TOOL]
    assert len(fake.calls) == 1

def test_analyze_returns_a_valid_document_and_stamps_searched_at(pcm_run: Path) -> None:
    payload = load(pcm_run / "trends.json")
    payload.pop("searched_at")
    fake = FakeLLM(json.dumps(payload))
    doc = trends.analyze(load(pcm_run / "claims.json"), fake, searched_at="2026-10-13")
    assert doc["searched_at"] == "2026-10-13"
    assert validate_trends(doc) == []

def test_analyze_defaults_searched_at_to_today(pcm_run: Path) -> None:
    doc = trends.analyze(load(pcm_run / "claims.json"), FakeLLM(json.dumps(load(pcm_run / "trends.json"))))
    assert len(doc["searched_at"]) == 10 and doc["searched_at"].count("-") == 2

def test_analyze_accepts_a_fenced_reply(pcm_run: Path) -> None:
    raw = "```json\n" + json.dumps(load(pcm_run / "trends.json")) + "\n```"
    assert trends.analyze(load(pcm_run / "claims.json"), FakeLLM(raw))["category"]["competitors"]

def test_analyze_rejects_a_reply_that_is_not_json(pcm_run: Path) -> None:
    with pytest.raises(ModelOutputError):
        trends.analyze(load(pcm_run / "claims.json"), FakeLLM("I searched the web for you."))

def test_analyze_rejects_a_missing_stage_note(pcm_run: Path) -> None:
    payload = load(pcm_run / "trends.json")
    del payload["category"]["stage_note"]
    with pytest.raises(SchemaError):
        trends.analyze(load(pcm_run / "claims.json"), FakeLLM(json.dumps(payload)))

def test_analyze_rejects_an_invented_sophistication_stage(pcm_run: Path) -> None:
    payload = load(pcm_run / "trends.json")
    payload["category"]["sophistication_stage"] = "loud"
    with pytest.raises(SchemaError):
        trends.analyze(load(pcm_run / "claims.json"), FakeLLM(json.dumps(payload)))

def test_every_stage_has_a_brief_and_they_are_all_distinct(pcm_run: Path) -> None:
    assert set(trends.STAGE_BRIEF) == set(trends.SOPHISTICATION_STAGES)
    assert len(set(trends.STAGE_BRIEF.values())) == 4

def test_the_fixture_and_the_live_path_produce_the_same_shape(pcm_run: Path) -> None:
    """The step-6 replacement for the fixture cannot change what step 3 consumes."""
    fixture = load(pcm_run / "trends.json")
    live = trends.analyze(load(pcm_run / "claims.json"), FakeLLM(json.dumps(fixture)), searched_at="2026-10-13")
    assert validate_trends(fixture) == [] and validate_trends(live) == []
    assert live.keys() == fixture.keys()
    assert live["category"].keys() == fixture["category"].keys()
    assert live["style"].keys() == fixture["style"].keys()
    assert [item.keys() for item in live["category"]["competitors"]] == [
        item.keys() for item in fixture["category"]["competitors"]
    ]
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python -m pytest tests/test_trends.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent.trends'`.

- [ ] **Step 3: Write the implementation**

```python
# src/prd_agent/trends.py
"""The live web pass: category, style and cultural trends, plus the market sophistication stage.

Version one ships no scraped corpus; the corpus seam is documented in docs/CORPUS_SEAM.md and not
built. The search happens inside the one model call, through the provider's own web search tool,
so this module adds no dependency, no second credential and no HTML parsing.
"""

from __future__ import annotations

import json
from datetime import date

from prd_agent.errors import ModelOutputError
from prd_agent.llm import LLM, WEB_SEARCH_TOOL, extract_json
from prd_agent.schemas import SOPHISTICATION_STAGES, TRENDS_SCHEMA, TRENDS_SPEC, require_valid

STAGE_BRIEF = {
    "virgin": "No one has heard the claim. State it plainly and be the first to name the problem.",
    "crowded": "Everyone makes the same claim. Make a bigger claim and back it with the mechanism.",
    "jaded": "The claim has gone flat and abstract. Lead with a new mechanism, not a louder promise.",
    "exhausted": "The category has burned the reader. Get identification first, then the mechanism.",
}

TRENDS_SYSTEM = (
    "You are a market analyst. You search the live web and report what competitors claim, what "
    "register of copy is landing, and which conversation is worth attaching to. You report what "
    "you find with URLs. You answer with JSON and nothing else."
)

_PROMPT_TEMPLATE = """\
Search the live web and report the market this product is entering.

Extract all three trend kinds:

- Category. What competing and adjacent products claim right now, with the language they use,
  quoted from the page. This is what makes a swap test runnable, so the `language` list must be
  the competitor's own words, not a paraphrase.
- Style. What register of copy is currently landing, so the story reads current rather than dated.
- Cultural. The conversation worth attaching to, with the URL and why it matters here.

Then pick the market sophistication stage (Schwartz) and say why:
- virgin: no one has heard the claim, so state it.
- crowded: everyone makes the same claim, so make a bigger claim.
- jaded: the claim has gone flat, so lead with a new mechanism.
- exhausted: the category has burned the reader, so lead with identification.

Rules:
1. Every competitor and every cultural moment carries a URL you actually read.
2. Do not describe a competitor's internals. Report what their page claims.
3. The `stage_note` says what the stage means for how loud this story should go.
4. Answer with exactly this JSON object and no prose around it:

{schema}

The artifact's own claims, so the search is aimed at the right category:

{claims}

Today is {searched_at}.
"""

def search_tools() -> list[dict]:
    """The provider-side search tool attached to the one call."""
    return [WEB_SEARCH_TOOL]

def build_trends_prompt(claims: dict, *, searched_at: str) -> str:
    schema = (
        '{"schema": "prd-agent.trends.v1", '
        '"category": {"competitors": [{"name": "", "url": "", "claim": "", "language": [""]}], '
        '"sophistication_stage": "virgin|crowded|jaded|exhausted", "stage_note": ""}, '
        '"style": {"register": "", "notes": [""]}, '
        '"cultural": [{"moment": "", "url": "", "relevance": ""}], '
        '"searched_at": ""}'
    )
    return _PROMPT_TEMPLATE.format(
        schema=schema,
        claims=json.dumps(claims, indent=2, ensure_ascii=False),
        searched_at=searched_at,
    )

def analyze(claims: dict, llm: LLM, *, searched_at: str | None = None) -> dict:
    """Run the live pass and return a validated trends document."""
    stamp = searched_at or date.today().isoformat()
    raw = llm.complete(
        system=TRENDS_SYSTEM,
        prompt=build_trends_prompt(claims, searched_at=stamp),
        tools=search_tools(),
    )
    doc = extract_json(raw)
    if not isinstance(doc, dict):
        raise ModelOutputError("the trends reply was not a JSON object")
    doc.setdefault("schema", TRENDS_SCHEMA)
    doc["searched_at"] = stamp
    category = doc.setdefault("category", {})
    category.setdefault("competitors", [])
    category.setdefault("sophistication_stage", "jaded")
    category.setdefault("stage_note", STAGE_BRIEF.get(category["sophistication_stage"], ""))
    doc.setdefault("style", {"register": "", "notes": []})
    doc.setdefault("cultural", [])
    require_valid(doc, TRENDS_SPEC, "trends.json")
    return doc
```

- [ ] **Step 4: Replace the fixture-only branch in `pipeline.py`**

The trends branch now reads `claims`, so intake must run before it. Print the whole `run()` body rather than a fragment, because the reorder is load-bearing: a patch that only swaps the `raise` for the live call still sends `claims` before it exists and fails with `UnboundLocalError`. Add `live: bool = True` to the signature after `answers`, and `from prd_agent import trends as trends_stage` to the imports.

```python
# src/prd_agent/pipeline.py (the whole run() body after this task)
def run(
    artifact_path: Path,
    *,
    llm: LLM,
    trends: dict | None = None,
    trends_file: Path | None = None,
    out: Path | None = None,
    autonomous: bool = False,
    ask: Callable[[list[dict]], dict[str, str]] | None = None,
    answers: dict[str, str] | None = None,
    live: bool = True,
) -> RunResult:
    """Run intake, trends, positioning and story. Human mode stops at the flag loop."""
    artifact_path = Path(artifact_path)
    if not artifact_path.exists():
        raise StageError(f"artifact path does not exist: {artifact_path}")
    root = artifact_path.resolve().parent
    name = artifact_path.resolve().name

    # Intake runs first: the live trends pass reads `claims` to build its prompt.
    collected: Artifact = collect_artifact(artifact_path)
    claims = intake.intake(artifact_path, llm, artifact=collected)

    if trends is not None:
        trends_doc = trends
        require_valid(trends_doc, TRENDS_SPEC, "trends.json")
    elif trends_file is not None:
        trends_doc = load_trends(Path(trends_file))
    elif not live:
        raise StageError(
            "no trends source. Pass --trends-file <path>, or drop --no-web to run the live web pass."
        )
    else:
        trends_doc = trends_stage.analyze(claims, llm)

    positioned = positioning_stage.positioning(claims, trends_doc, llm)

    target_run_dir = run_dir(root, name)
    target_story = Path(out) if out is not None else default_out(root, name)
    _write_json(target_run_dir / "claims.json", claims)
    _write_json(target_run_dir / "trends.json", trends_doc)
    _write_json(target_run_dir / "positioning.json", positioned)

    result = RunResult(
        task_name=name,
        run_dir=target_run_dir,
        story_path=target_story,
        claims_path=target_run_dir / "claims.json",
        trends_path=target_run_dir / "trends.json",
        positioning_path=target_run_dir / "positioning.json",
        flags=list(positioned.get("flags", [])),
    )

    if not autonomous and answers is None and ask is None:
        result.awaiting_answers = True
        return result

    if not autonomous:
        supplied = answers if answers is not None else ask(list(positioned.get("flags", [])))
        positioned = positioning_stage.positioning(
            claims,
            trends_doc,
            llm,
            answers=flags_module.answers_as_prompt(list(positioned.get("flags", [])), supplied),
        )
        _write_json(target_run_dir / "positioning.json", positioned)
        result.flags = list(positioned.get("flags", []))

    page, report = story_stage.story(
        claims=claims, positioning=positioned, trends=trends_doc, llm=llm
    )
    target_story.parent.mkdir(parents=True, exist_ok=True)
    target_story.write_text(page, encoding="utf-8")
    result.report = report
    result.awaiting_answers = False
    return result
```

The earlier `test_a_run_without_a_trends_source_says_what_to_pass` from Task 11 now needs `live=False`, or it would attempt a live search; update it in the same commit.

- [ ] **Step 5: Append the pipeline test for the live branch**

```python
# tests/test_pipeline.py (append)
def test_the_live_pass_replaces_the_fixture_when_no_file_is_given(
    tmp_path: Path, pcm_run: Path
) -> None:
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    fake = FakeLLM([
        (pcm_run / "claims.json").read_text(encoding="utf-8"),
        (pcm_run / "trends.json").read_text(encoding="utf-8"),
        (pcm_run / "positioning.json").read_text(encoding="utf-8"),
        GOOD_BODY,
    ])
    result = pipeline.run(artifact, llm=fake, autonomous=True)
    assert fake.calls[1]["tools"] == [pipeline.trends_stage.llm.WEB_SEARCH_TOOL]
    assert load(result.trends_path)["schema"] == "prd-agent.trends.v1"
    assert result.story_path.is_file()

def test_no_web_without_a_fixture_still_says_what_to_pass(tmp_path: Path) -> None:
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    with pytest.raises(StageError) as error:
        pipeline.run(artifact, llm=FakeLLM("{}"), autonomous=True, live=False)
    assert "--trends-file" in str(error.value)
```

- [ ] **Step 6: Add `--no-web` to the CLI**

```python
# src/prd_agent/cli.py (add the flag in build_parser)
    parser.add_argument(
        "--no-web",
        action="store_true",
        help="never run the live web pass; requires --trends-file",
    )
```

and pass `live=not args.no_web` in the `run(...)` call. Add to `tests/test_cli.py`:

```python
def test_no_web_parses() -> None:
    args = cli.build_parser().parse_args(["repo", "--no-web", "--trends-file", "t.json"])
    assert args.no_web is True
    assert args.trends_file == "t.json"
```

- [ ] **Step 7: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_trends.py tests/test_pipeline.py tests/test_cli.py -v`
Expected: 32 passed, no network access.

- [ ] **Step 8: Commit**

```bash
git add src/prd_agent/trends.py src/prd_agent/pipeline.py src/prd_agent/cli.py tests/test_trends.py tests/test_pipeline.py tests/test_cli.py
git commit -m "feat: add the live trends web pass and replace the step-3 fixture"
```

---

## Task 14: Eval append and exemplar retrieval (spec §5, build order step 7)

**Files:**
- Create: `src/prd_agent/evals.py`
- Modify: `src/prd_agent/pipeline.py` (append the eval, pass exemplars into the story call), `src/prd_agent/cli.py` (add `--evals`)
- Test: `tests/test_evals.py`

**Interfaces:**
- Consumes: `positioning.content_words(text) -> set[str]`; `checks.CheckReport`, `checks.split_body_footer(markdown) -> tuple[str, str]`; `errors.StageError`; `json`.
- Produces: `EVALS_PATH: Path`, `EVAL_SCHEMA`, `load_evals(path) -> dict`, `next_id(evals) -> int`, `build_assertions(*, report, positioning, body) -> list[str]`, `build_eval(*, task_name, artifact_name, positioning, page, report) -> dict`, `append_eval(path, record) -> dict`, `score(candidate, exemplar) -> int`, `select_exemplars(evals, *, positioning, limit=2) -> list[dict]`, `exemplars_as_prompt(exemplars) -> str`.

**Bounded by design.** Retrieval is deterministic keyword overlap over one small JSON file. There is no embedding model, no vector store and no corpus builder. The later seam (a real corpus with semantic retrieval) is written down in `docs/CORPUS_SEAM.md` in Task 15 and not built.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_evals.py
from __future__ import annotations

import json
from pathlib import Path

import pytest

from prd_agent import evals
from prd_agent.checks import check_story
from prd_agent.errors import StageError

GOOD_BODY = (
    "# Memory in your repository\n\n**Files next to the code.**\n\nInstall it once and read the state.\n\n"
    "## The chat ends and the project stops making sense\n\n"
    "You come back after two weeks and spend the first hour working out what state it is in. "
    "The number in last month's report has no context left.\n\n"
    "## The repository remembers itself\n\n"
    "A fresh session opens the repo and knows what the project is and where it stands. "
    "It reads the record instead of asking you.\n\n"
    "## Four steps\n\n1. Read.\n2. Work.\n3. Record.\n4. Publish.\n"
)

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def positioning_doc(pcm_run: Path) -> dict:
    return load(pcm_run / "positioning.json")

def test_load_evals_returns_an_empty_collection_when_the_file_is_absent(tmp_path: Path) -> None:
    assert evals.load_evals(tmp_path / "missing.json") == {"skill_name": "copywriting", "evals": []}

def test_load_evals_rejects_a_malformed_file(tmp_path: Path) -> None:
    path = tmp_path / "evals.json"
    path.write_text('{"skill_name": "copywriting", "evals": {"not": "a list"}}', encoding="utf-8")
    with pytest.raises(StageError):
        evals.load_evals(path)

def test_build_assertions_are_readable_and_name_the_beats(pcm_run: Path) -> None:
    report = check_story(GOOD_BODY)
    assertions = evals.build_assertions(
        report=report, positioning=positioning_doc(pcm_run), body=GOOD_BODY
    )
    assert any("discomfort" in item and "vision" in item and "path" in item for item in assertions)
    assert any("no contrast reveal" in item for item in assertions)
    assert any("the differentiator survives the swap test" in item for item in assertions)
    assert all(isinstance(item, str) and item for item in assertions)

def test_build_eval_uses_the_marketingskills_shape(pcm_run: Path) -> None:
    report = check_story(GOOD_BODY)
    record = evals.build_eval(
        task_name="pcm",
        artifact_name="project-continuity-modules",
        positioning=positioning_doc(pcm_run),
        page=GOOD_BODY + "\n\n---\n\n### Proof and open items\n\ntable\n",
        report=report,
    )
    assert set(record) == {"id", "prompt", "expected_output", "assertions", "files", "task", "artifact"}
    assert record["prompt"].startswith("Write the marketing page body for")
    assert "the memory is the Git repository itself" in record["prompt"]
    assert record["expected_output"].startswith("# Memory in your repository")
    assert "### Proof and open items" not in record["expected_output"]
    assert record["files"] == []

def test_append_eval_creates_the_file_then_extends_it(tmp_path: Path, pcm_run: Path) -> None:
    path = tmp_path / "evals.json"
    report = check_story(GOOD_BODY)
    first = evals.append_eval(path, evals.build_eval(
        task_name="pcm", artifact_name="pcm", positioning=positioning_doc(pcm_run),
        page=GOOD_BODY, report=report,
    ))
    second = evals.append_eval(path, evals.build_eval(
        task_name="mini", artifact_name="mini", positioning=positioning_doc(pcm_run),
        page=GOOD_BODY, report=report,
    ))
    assert first["id"] == 1 and second["id"] == 2
    stored = load(path)
    assert stored["skill_name"] == "copywriting"
    assert [item["id"] for item in stored["evals"]] == [1, 2]
    assert stored["evals"][1]["task"] == "mini"

def test_score_counts_shared_content_words() -> None:
    exemplar = {"prompt": "a story about persistent memory for coding agents"}
    assert evals.score("persistent memory for coding agents", exemplar) == 5
    assert evals.score("a story about billing retries", exemplar) == 1

def test_select_exemplars_prefers_the_closest_and_breaks_ties_by_newest(pcm_run: Path) -> None:
    positioning = positioning_doc(pcm_run)
    corpus = {
        "skill_name": "copywriting",
        "evals": [
            {"id": 1, "prompt": "Write the marketing page body for a project memory tool.", "expected_output": "old"},
            {"id": 2, "prompt": "Write the marketing page body for a project memory tool.", "expected_output": "new"},
            {"id": 3, "prompt": "Write the marketing page body for a billing retry tool.", "expected_output": "other"},
        ],
    }
    picked = evals.select_exemplars(corpus, positioning=positioning, limit=2)
    assert [item["id"] for item in picked] == [2, 1]
    assert picked[0]["story"] == "new"

def test_select_exemplars_returns_nothing_for_an_empty_corpus(pcm_run: Path) -> None:
    corpus = {"skill_name": "copywriting", "evals": []}
    assert evals.select_exemplars(corpus, positioning=positioning_doc(pcm_run)) == []

def test_select_exemplars_never_returns_a_zero_score_example() -> None:
    # A zero-score example shares nothing with the positioning, so it would only
    # muddy the prompt. Retrieval stops at the first miss rather than padding the
    # list up to `limit` with unrelated stories.
    positioning = {
        "differentiator": "plain files in the repository",
        "audience": {"who": "solo builders"},
        "discomfort": "",
        "vision": "",
    }
    corpus = {
        "skill_name": "copywriting",
        "evals": [
            {"id": 1, "prompt": "Write the page for a repository memory tool.", "expected_output": "hit"},
            {"id": 2, "prompt": "Write the page for an espresso machine.", "expected_output": "miss"},
        ],
    }
    picked = evals.select_exemplars(corpus, positioning=positioning, limit=2)
    assert [item["id"] for item in picked] == [1]

def test_exemplars_as_prompt_is_empty_when_there_is_nothing_to_show() -> None:
    assert evals.exemplars_as_prompt([]) == ""

def test_exemplars_as_prompt_labels_the_examples() -> None:
    text = evals.exemplars_as_prompt([{"id": 7, "story": "# A page\n\nbody"}])
    assert "worked example" in text.lower()
    assert "# A page" in text
    assert "Do not reuse their subject matter" in text
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python -m pytest tests/test_evals.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'prd_agent.evals'`.

- [ ] **Step 3: Write the implementation**

```python
# src/prd_agent.evals.py  ->  src/prd_agent/evals.py
"""Append every finished story as a worked example, and retrieve the closest ones next run.

Run one uses a template; run fifty uses fifty real stories. Retrieval is deterministic keyword
overlap over one small JSON file: no embeddings, no vector store, no corpus infrastructure. The
semantic-corpus seam is documented in docs/CORPUS_SEAM.md and deliberately not built.
"""

from __future__ import annotations

import json
from pathlib import Path

from prd_agent.checks import CheckReport, split_body_footer
from prd_agent.errors import StageError
from prd_agent.positioning import content_words

EVALS_PATH = Path("evals") / "story_evals.json"
EVAL_SCHEMA = "prd-agent.story-eval.v1"
SKILL_NAME = "copywriting"
DEFAULT_LIMIT = 2

def load_evals(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        return {"skill_name": SKILL_NAME, "evals": []}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StageError(f"{path} is not readable JSON: {exc}") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("evals"), list):
        raise StageError(f"{path} must be an object with an 'evals' list")
    doc.setdefault("skill_name", SKILL_NAME)
    return doc

def next_id(evals: dict) -> int:
    highest = 0
    for item in evals.get("evals", []):
        try:
            highest = max(highest, int(item.get("id", 0)))
        except (TypeError, ValueError):
            continue
    return highest + 1

def build_assertions(*, report: CheckReport, positioning: dict, body: str) -> list[str]:
    """The assertions a later run should be able to check on a new story."""
    return [
        "The hero states the transformation, and the page carries the three beats in order: "
        "discomfort, then vision, then path.",
        "Every claim on the page traces to a claim marked verified or claimed in claims.json.",
        "No contrast reveal, negation list, trailing pile-on, self-answered question, colon reveal, "
        "stock phrase or em dash in short copy appears in the pitch body.",
        "The differentiator survives the swap test against the named competitors.",
        f"The page leads with the mechanism: {positioning.get('differentiator', '')}",
        f"Market stage used: {positioning.get('swap_test', {}).get('passed', False)} "
        f"swap test verdict recorded, and the sophistication stage named in the footer.",
        f"The pitch body runs {len(report.sections)} sections and reports "
        f"{len(report.bans)} hard bans and {len(report.cap_violations())} cap violations.",
        "The proof table and the open flags are present in the footer and were not written by the model.",
    ]

def build_eval(
    *,
    task_name: str,
    artifact_name: str,
    positioning: dict,
    page: str,
    report: CheckReport,
) -> dict:
    body, _footer = split_body_footer(page)
    prompt = (
        "Write the marketing page body for "
        f"{artifact_name}. The differentiator is: {positioning.get('differentiator', '')} "
        "The audience is: "
        f"{positioning.get('audience', {}).get('who', '')} "
        "Do not write the proof table, the open flags or the self-check paragraph."
    )
    return {
        "schema": EVAL_SCHEMA,
        "id": 0,
        "prompt": prompt,
        "expected_output": body.strip(),
        "assertions": build_assertions(report=report, positioning=positioning, body=body),
        "files": [],
        "task": task_name,
        "artifact": artifact_name,
    }

def append_eval(path: Path, record: dict) -> dict:
    """Give the record the next id and append it. Returns the stored record."""
    path = Path(path)
    corpus = load_evals(path)
    record = dict(record)
    record["id"] = next_id(corpus)
    corpus["evals"].append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(corpus, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record

def score(candidate: str, exemplar: dict) -> int:
    """How many content words the candidate shares with an earlier example's prompt."""
    return len(content_words(candidate) & content_words(str(exemplar.get("prompt", ""))))

def select_exemplars(evals: dict, *, positioning: dict, limit: int = DEFAULT_LIMIT) -> list[dict]:
    """The closest earlier stories, newest first when two score the same."""
    candidate = " ".join(
        [
            str(positioning.get("differentiator", "")),
            str(positioning.get("audience", {}).get("who", "")),
            str(positioning.get("discomfort", "")),
            str(positioning.get("vision", "")),
        ]
    )
    ranked: list[tuple[int, int, dict]] = []
    for item in evals.get("evals", []):
        try:
            identifier = int(item.get("id", 0))
        except (TypeError, ValueError):
            identifier = 0
        ranked.append((score(candidate, item), identifier, item))
    ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
    picked: list[dict] = []
    for points, identifier, item in ranked[:limit]:
        if points == 0:
            break
        picked.append({"id": identifier, "score": points, "story": str(item.get("expected_output", ""))})
    return picked

def exemplars_as_prompt(exemplars: list[dict]) -> str:
    """The block `story.build_story_prompt` accepts. Empty string when there is nothing to show."""
    if not exemplars:
        return ""
    parts = [
        "Worked examples from earlier runs. Use their shape, their register and their level of "
        "specificity. Do not reuse their subject matter.",
    ]
    for exemplar in exemplars:
        story_text = str(exemplar.get("story", "")).strip()
        if story_text:
            parts.append(f"\n--- worked example {exemplar.get('id', '')} ---\n{story_text}")
    return "\n".join(parts)
```

- [ ] **Step 4: Wire it into the pipeline**

In `pipeline.py`, add `evals_path: Path | None = None` to the `run` signature, then before the story call:

```python
    corpus = evals_stage.load_evals(evals_path or evals_stage.EVALS_PATH)
    exemplars = evals_stage.select_exemplars(corpus, positioning=positioned)
    page, report = story_stage.story(
        claims=claims,
        positioning=positioned,
        trends=trends_doc,
        llm=llm,
        exemplars=exemplars,
    )
```

and after writing the story:

```python
    record = evals_stage.build_eval(
        task_name=name,
        artifact_name=collected.name,
        positioning=positioned,
        page=page,
        report=report,
    )
    evals_stage.append_eval(evals_path or evals_stage.EVALS_PATH, record)
```

with `from prd_agent import evals as evals_stage` added to the imports. Add `--evals` to `cli.py` (`default=None`, "where to append the worked example; default evals/story_evals.json") and pass it through as `evals_path=Path(args.evals) if args.evals else None`.

- [ ] **Step 5: Append the pipeline test that proves the exemplar reaches the prompt**

```python
# tests/test_pipeline.py (append)
def test_a_finished_run_is_appended_and_its_story_becomes_an_exemplar_for_the_next(
    tmp_path: Path, pcm_run: Path
) -> None:
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    corpus_path = tmp_path / "evals" / "story_evals.json"
    scripted = [
        (pcm_run / "claims.json").read_text(encoding="utf-8"),
        (pcm_run / "trends.json").read_text(encoding="utf-8"),
        (pcm_run / "positioning.json").read_text(encoding="utf-8"),
        GOOD_BODY,
    ]
    first = pipeline.run(
        artifact, llm=FakeLLM(scripted), trends_file=repo_root_fixture(), autonomous=True,
        evals_path=corpus_path,
    )
    assert corpus_path.is_file()
    assert load(corpus_path)["evals"][0]["task"] == "mini"

    second_llm = FakeLLM(scripted)
    pipeline.run(
        artifact, llm=second_llm, trends_file=repo_root_fixture(), autonomous=True,
        evals_path=corpus_path,
    )
    assert "worked example" in str(second_llm.calls[3]["prompt"]).lower()
    assert load(corpus_path)["evals"][1]["id"] == 2
    assert first.story_path.is_file()

def repo_root_fixture() -> Path:
    return Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "trends_pcm.json"
```

- [ ] **Step 6: Run the tests and confirm they pass**

Run: `python -m pytest tests/test_evals.py tests/test_pipeline.py -v`
Expected: 17 passed.

- [ ] **Step 7: Commit**

```bash
git add src/prd_agent/evals.py src/prd_agent/pipeline.py src/prd_agent/cli.py tests/test_evals.py tests/test_pipeline.py
git commit -m "feat: append finished stories as worked examples and retrieve the closest ones"
```

---

## Task 15: README, CI and the first checkpoint

**Files:**
- Create: `README.md`, `docs/CORPUS_SEAM.md`, `.github/workflows/prd-agent-tests.yml`
- Modify: `checkpoints/CURRENT.md`, `HANDOFF.md` (via the `continuity` CLI)

**Interfaces:**
- Consumes: the CLI from Task 11, the flags from Task 12, the live pass from Task 13, the eval path from Task 14.
- Produces: nothing importable. This task closes the loop with the repository contract in `AGENTS.md`.

- [ ] **Step 1: Write the README**

````markdown
# PRD-agent

Turn a builder's own artifact into a product story that sells.

Generated marketing copy from a repository reads as an audit: an inventory of what the product
does and what it lacks. This pipeline reads the artifact, establishes what is true, and writes
the page a stranger would read to the end.

## Run it

```bash
python -m pip install -e ".[dev]"
python -m prd_agent ../your-repo --autonomous
```

Without `--autonomous` the run stops at the open flags and asks. With it, the run completes and
ships the flags as a footer on the page.

| Flag | What it does |
|---|---|
| `--autonomous` | Complete the run and ship the flag footer instead of stopping to ask |
| `--out PATH` | Where to write the story. Default `stories/<artifact-name>.md` |
| `--trends-file PATH` | Read `trends.json` from a file instead of running the live web pass |
| `--no-web` | Never run the live web pass. Requires `--trends-file` |
| `--answers-file PATH` | A JSON object of flag id to answer, instead of reading stdin |
| `--evals PATH` | Where to append the worked example. Default `evals/story_evals.json` |

Every run writes `runs/<artifact-name>/claims.json`, `trends.json` and `positioning.json`, so any
stage can be inspected or re-run on its own.

## The four stages

```
artifact repo -> claims.json -> trends.json -> positioning.json -> story.md
                     ^______________ [NEED:] ______________|
```

1. **Intake** reads README, entry points, tests, commit subjects and docs. An unread fact becomes
   an `unknown`. The stage never invents a mechanism.
2. **Trends** runs one live web search for what competitors claim, what register of copy is
   landing, and which conversation is worth attaching to, then picks the market sophistication
   stage (Schwartz).
3. **Positioning** derives the spine (discomfort, vision, path) and the differentiator, and runs
   the swap test in code. A differentiator that a competitor already covers fails and is flagged.
4. **Story** drafts the page through the vendored `copywriting` skill, gates it against that
   skill's own self-check, rewrites a failing draft from the facts, and appends the proof table,
   the open flags and the self-check paragraph in code.

## The model seam

Every stage takes an `LLM`. The shipped provider is a stdlib `urllib` client for the Anthropic
Messages API, so the package has zero runtime dependencies. Tests inject a fake and never touch
the network.

```bash
export ANTHROPIC_API_KEY=...        # required for a real run
export PRD_AGENT_MODEL=...          # optional model override
```

Offline, without a key, the pipeline replays canned responses:

```bash
export PRD_AGENT_LLM=fake
export PRD_AGENT_CANNED_DIR=/path/to/dir/of/numbered/txt/files
```

## What the self-check can and cannot decide

`prd_agent.checks` implements the vendored skill's `references/ai-tells.md`: the hard bans
(contrast reveals, negation lists, trailing pile-ons, self-answered questions, colon reveals,
stock phrases, banned vocabulary, hype punctuation, em dashes in short copy), the frequency caps
counted per section, and the three structural beats. It cannot decide whether the story lands,
whether a sentence that avoids every rule is still empty, or any tell in a shape no rule matches.
The footer says so on every page, and that judgment stays with the owner.

## Licence

The vendored `copywriting` skill is MIT, copyright Corey Haines, from
`coreyhaines31/marketingskills` at commit

`0f8d8996`. The vendored copy, its licence and its
SHA-256 hashes live in `src/prd_agent/vendor/copywriting/`; `PROVENANCE.md` records where it came
from and `tests/test_skill.py` fails if a vendored file changes without its hash being updated.

## What this does not do yet

Trends are searched live and not stored. There is no scraped corpus and no semantic retrieval;
the eval file is searched by keyword overlap. That seam is written down in
`docs/CORPUS_SEAM.md` and deliberately not built.
```

- [ ] **Step 2: Document the corpus and retrieval seam**

```markdown
# The corpus and retrieval seam

Status: documented, not built. Nothing in this file exists yet.

## What is built today

Every finished story is appended to `evals/story_evals.json` in the marketingskills eval shape
(`prompt`, `expected_output`, `assertions`). The next run reads that file, scores each past
prompt against the current positioning by shared content words, and passes the top two into
`story.build_story_prompt` as worked examples. See `src/prd_agent/evals.py`.

That is the whole of retrieval: deterministic keyword overlap over one small JSON file. It has
no dependency, no index and no model call, and it is honest about being a floor. A run whose
positioning shares no content words with any past story retrieves nothing and falls back to the
template prompt.

## What is not built

1. **A scraped trend corpus.** `trends.analyze` searches the live web on every run and stores
   nothing, so two runs a week apart cannot be compared and a competitor who changes their
   headline is invisible. A corpus would snapshot each search into a dated file and let the
   stage read the delta.
2. **Semantic retrieval over past stories.** Keyword overlap misses a past story about a
   different category that solved the same structural problem (a jaded market that needed a new
   mechanism, say). Embedding the positioning and the past prompts would catch it.
3. **Cross-run positioning memory.** Nothing records which differentiators passed the swap test
   before, so the same losing line can be proposed twice.

## Why not built now

The project ships zero runtime dependencies, and both a corpus store and embeddings need one.
The eval file is also small enough that keyword overlap has not yet been observed to fail: the
first run has no exemplars at all.

## The trigger to build it

Build the corpus when any of these is observed, not before:

- `evals/story_evals.json` passes 50 records, or the file passes 200 KB.
- Three consecutive runs retrieve zero-score exemplars while past stories exist.
- A second artifact from a different category is run and the retrieved exemplars are visibly
  wrong for it.

## The seam, so the change stays local

`evals.select_exemplars(evals: dict, *, positioning: dict, limit: int = 2) -> list[dict]` is the
only function that reads the corpus. A corpus-backed implementation keeps that signature and
returns the same `{"id", "score", "story"}` records, so `pipeline.run` and
`story.build_story_prompt` do not change. A corpus writer would be a new function alongside
`evals.append_eval`, called from the same place in `pipeline.run`.

## Acceptance criteria for building it

- The retrieved exemplars for a known positioning are better than keyword overlap's, judged by
  the owner on at least three artifacts, and the keyword results are kept as the control.
- Retrieval stays out of the model's verdict path: no exemplar selection is decided by a model.
- The dependency count stays zero, or the new dependency is justified in the PR against this
  file's "why not built now" section.
```

- [ ] **Step 3: Add the test workflow**

This is additive. It does not modify `.github/workflows/acs-gates.yml`, and its job is not named `gates`, so the required status check is untouched.

```yaml
# .github/workflows/prd-agent-tests.yml
name: prd-agent tests

# Tests for the pipeline itself. The stack gates for this repository live in
# acs-gates.yml and its `gates` job stays the required status check on main.
# This workflow is additive: it proves the pipeline's own suite passes and that
# the package still ships with zero runtime dependencies.

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: prd-agent-tests-${{ github.ref }}
  cancel-in-progress: true

jobs:
  tests:
    name: pytest (3.12)
    runs-on: ubuntu-latest
    steps:
      - name: Check out the repository
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install the package and pytest
        run: python -m pip install -e ".[dev]"

      - name: Run the suite
        run: python -m pytest -q

      - name: Prove the vendored skill is intact
        run: python -m pytest tests/test_skill.py -q

      - name: Prove no runtime dependency was added
        shell: bash
        run: |
          set -euo pipefail
          python - <<'PY'
          import pathlib
          import sys
          import tomllib

          data = tomllib.loads(pathlib.Path("pyproject.toml").read_text(encoding="utf-8"))
          deps = data["project"].get("dependencies", [])
          if deps:
              print(f"runtime dependencies are not allowed: {deps}", file=sys.stderr)
              raise SystemExit(1)
          print("zero runtime dependencies")
          PY
```

- [ ] **Step 4: Run the full suite and the repository validator**

Run:

```bash
python -m pytest -q
continuity validate --root .
```

Expected: every test passes, and `continuity validate` prints `VALID`.

- [ ] **Step 5: Synchronize the projections before the push**

Edit `checkpoints/CURRENT.md` so the marker and the prose agree: `active_task` becomes `PRA-0001`, Completed gains "the four-stage pipeline, the self-check, the two modes, the live trend pass and the eval append are implemented and tested", Active names the open PR, and Next becomes "confirm the `gates` check on the PR and merge". Edit the `tasks/TASK-PRA-0001-*.md` projection to match, and link the leaf issue URL on both.

```bash
continuity validate --root .
git add -A
git status --short
```

Expected: `VALID`, and the staged list contains the new `src/`, `tests/`, `docs/`, `README.md` and `.github/workflows/prd-agent-tests.yml` plus the two edited projections.

- [ ] **Step 6: Commit the product and docs first**

```bash
git commit -m "docs: document the pipeline and the corpus seam, add the test workflow and close the increment"
git push -u origin task/PRA-0001-prd-agent-pipeline
```

- [ ] **Step 7: Checkpoint with a stable request ID**

The product commit is already pushed; `continuity checkpoint` commits and synchronously pushes the checkpoint.

```bash
continuity checkpoint PRA-0001 --root . --agent "<your agent name>" \
  --completed "The four-stage pipeline is implemented and tested: intake reads an artifact into claims.json, the live web pass produces trends.json, positioning derives the spine and runs the swap test in code, and the story stage drafts through the vendored copywriting skill, gates the draft against that skill's own self-check and appends the proof table, the flags and the self-check paragraph in code" \
  --completed "The flag loop runs in two modes over one pipeline, and finished stories are appended as worked examples and retrieved by keyword overlap" \
  --evidence "python -m pytest -q: every test passes with no network access" \
  --evidence "continuity validate --root .: VALID" \
  --evidence "the vendored copywriting skill is MIT at commit 0f8d8996, recorded with SHA-256 hashes in src/prd_agent/vendor/copywriting/PROVENANCE.md" \
  --changed "src/prd_agent/, tests/, docs/CORPUS_SEAM.md, README.md, .github/workflows/prd-agent-tests.yml" \
  --next "Open the pull request, wait for the gates check, then merge"
```

Expected: a printed `REQUEST_ID`. If the command is interrupted, rerun it with `--request-id <the printed id>`; the same payload is a no-op and a changed payload is rejected.

- [ ] **Step 8: Open the PR and arm auto-merge after the final push**

Write the PR opening reader-first: the problem and its consequence, what changes, how to verify, what stays unchanged, the lineage links, and one next action. Reference the issue with `Refs #<number>` unless merging should close it.

```bash
gh pr create --repo Pukujan/PRD-agent \
  --title "Build the four-stage PRD-agent pipeline so artifact repos produce a story that sells" \
  --body "Refs #<issue-number>" \
  --fill
```

Then arm auto-merge only after this final push, so no later push races the merge window:

```bash
gh pr merge --auto --squash <PR-number> --repo Pukujan/PRD-agent
```

- [ ] **Step 9: Verify the gates and post the receipt**

```bash
gh pr checks <PR-number> --repo Pukujan/PRD-agent
gh pr view <PR-number> --repo Pukujan/PRD-agent --json state,mergeCommit
```

Expected: the `gates` check green and the PR merged. A missing, failed, skipped or stale check fails closed: no completion and no worktree cleanup. Then post the leaf issue receipt keyed by the checkpoint `REQUEST_ID` and the exact merged SHA, linking the changed files, the PR, the test result and any pending gate, and add the linked parent progression update. Inspect for the same key before posting so a retry does not duplicate it.

- [ ] **Step 10: Clean up only after verified merge**

```bash
git checkout main
git pull --quiet origin main
continuity worktree list 2>/dev/null || true
```

If a linked worktree was created for this task, run `continuity worktree remove PRA-0001` only after the merge is verified. If everything happened in the canonical checkout, there is nothing to remove and no branch to delete until the PR's delete-branch has run.

---

## Task 16: First real target — the owner's ACS hot-loader repository

This is a separate increment. Task 15 merges `PRA-0001`; this task opens `PRA-0002` against the
merged default branch, because its deliverable is evidence rather than library code.

**Why it exists.** Spec §6 names "the first run operates on the owner's own ACS hot-loader
repository" as the fixture that decides whether the design holds, and §9 names the same repository
as the first target. Nothing in Tasks 0-15 exercises it: every test runs on
`tests/fixtures/artifact-mini` or the hand-run `runs/pcm` documents. Without this task the plan
ships the pipeline with the spec's own acceptance evidence uncollected, and the first thing anyone
learns about the design in production is whatever the owner's first real run says.

**Files:**
- Create: `runs/acs-hot-loader/{claims.json,trends.json,positioning.json}`
- Create: `stories/acs-hot-loader.md`
- Create: `docs/FIRST_TARGET.md`
- Test: none. This task is a run, not code.

**Interfaces:**
- Consumes: the merged CLI, `python -m prd_agent <artifact-path> [--autonomous] [--out <path>]`.
- Produces: the first real artifacts and the owner's verdict on them.

- [ ] **Step 1: Set up the increment**

Open the issue for `PRA-0002` the same way Task 0 did for `PRA-0001`, create the task projection,
and cut the branch `task/PRA-0002-first-target`. Record on the issue that this increment adds no
library code and its acceptance criterion is the owner's verdict, not a test.

- [ ] **Step 2: Locate the hot-loader checkout**

The artifact is ACS itself, `agent-custom-setup` — the repository that installs the multi-agent
hot-load pack into any repo. It is the right first target because it is the owner's own artifact,
it is a public repo with a real README, and its subject (several agents sharing one repository)
is a category with its own jostling claims.

Resolve the local checkout through the private per-device registry rather than guessing a path:

```bash
continuity workspace list
```

If no `agent-custom-setup` root is registered, ask the owner for the path and register it with
`continuity workspace register --root <checkout>` before continuing. Do not scan drives, and do not
write the absolute path into any committed file.

- [ ] **Step 3: Run the pipeline live**

The output convention is that `runs/<name>/` and `stories/<name>.md` land beside the artifact, so
for an artifact outside this repository the run needs an explicit `--out` and its intermediate
files copied back. From the PRD-agent checkout, with `$ACS` set to the registered root:

```bash
export ANTHROPIC_API_KEY=...
python -m prd_agent "$ACS" --autonomous --out stories/acs-hot-loader.md
mkdir -p runs/acs-hot-loader
cp "$(dirname "$ACS")/runs/agent-custom-setup/"*.json runs/acs-hot-loader/
```

The first run on a fresh clone has an empty `evals/story_evals.json`, so the prompt takes the
"no worked examples" branch. That is the intended first-run behaviour and Step 4 should confirm it
rather than treat it as a gap.

- [ ] **Step 4: Read the output before anyone else does**

Read `stories/acs-hot-loader.md` end to end against the vendored skill's own self-check, and check
the three things the design claims:

1. **The mechanism leads.** The hero names the hot-load mechanism, not the category's abstraction.
2. **The footer is code.** The proof table's rows trace to `claims.json` evidence, the flags are
   the ones positioning raised, and the self-check paragraph reports the accepted draft.
3. **Nothing is invented.** Every claim on the page has a `claims.json` row; the unknowns are
   rendered as unknowns.

Record what actually happened, including anything the run got wrong. A run that produces a bad
page is the finding, not a failure to hide.

- [ ] **Step 5: Write the verdict**

```markdown
# First target: the ACS hot-loader repository

Status: <run | not run>. Owner verdict: <verbatim, or "not yet given">.

## What was run

`python -m prd_agent <hot-loader-root> --autonomous --out stories/acs-hot-loader.md`, on
<date>, at artifact commit <sha>.

## What the run produced

<The story path, the three JSON documents, and one paragraph on whether the mechanism led.>

## What the run exposed

<Every defect, contradiction or surprise, each with the file and line it appears at. The PCM
hand-run's version contradiction is the model: a real finding beats a clean report.>

## What this says about the design

<Whether §6's acceptance criterion is met, and if not, which stage failed it.>
```

- [ ] **Step 6: Commit, checkpoint, PR and verify**

Follow Task 15 Steps 4-10 exactly, with `PRA-0002` in place of `PRA-0001` and this increment's
paths in `--changed`. The `gates` check is the same required check, and a missing, failed, skipped
or stale check fails closed.

- [ ] **Step 7: Feed the finding back**

If Step 4 found a defect in the pipeline, open a follow-up issue naming the stage, the input and
the observed output, and link it from the `PRA-0002` receipt. Do not fix it inside this increment:
the verdict has to describe the pipeline as it was actually merged, or it is not evidence.

---

## Self-review

Run after the whole plan (Tasks 0-16) was assembled, against
`docs/superpowers/specs/2026-10-13-prd-agent-design.md`.

### Spec coverage

| Spec section | Task | Note |
|---|---|---|
| §3.1 intake | Task 5 | Schema, `unknowns`, no invented mechanism |
| §3.2 trends | Task 13 (fixture from Task 7) | All three kinds plus sophistication staging |
| §3.3 positioning | Task 7 | Spine, differentiator, swap test in code, flag on failure |
| §3.4 story | Task 10 | Handoff, `story.md` sections, gate, rewrite, footer |
| §3.5 interface | Task 11 (+12) | `python -m prd_agent <path> [--autonomous] [--out]`, `runs/<name>/` |
| §4 storyboard loop | Tasks 6, 12 | Flags are the storyboard; one codepath, one boolean |
| §5 reusability | Task 14 | Eval append and exemplar retrieval; seam documented in Task 15 |
| §6 testing | Tasks 3, 7, 8, 9, 12 | Swap test, bans and caps, beats, flag resolution, schema validity |
| §6 not machine-checkable | Tasks 9, 15 | `CheckReport.limitations()` and the README both record it as the owner's criterion |
| §7 no evidence | Tasks 5, 10 | Unknowns in claims; unknowns rendered in the footer |
| §7 artifact too large | Task 4 | Truncation, `skipped`, and `render_artifact` declares it to the model |
| §7 no differentiator | Task 7 | `[NEED: differentiator]`, no generic copy |
| §7 no human | Task 12 | Autonomous mode ships the flag footer |
| §7 claim contradicts artifact | Tasks 5, 10 | Intake `note` records the overstatement; story prompt rule 3 |
| §8 step 1 vendoring | Task 1 | |
| §8 step 2 intake | Task 5 | |
| §8 step 3 positioning | Task 7 | Against `tests/fixtures/trends_pcm.json` |
| §8 step 4 story | Task 10 | |
| §8 step 5 flag loop and modes | Task 12 | |
| §8 step 6 live web pass | Task 13 | Replaces the fixture |
| §8 step 7 evals | Task 14 | |
| §6, §9 first target | Task 16 | A second increment: the run against ACS and the owner's verdict |
| §1, §2 | none needed | Context and resolved decisions, not implementable requirements |

**One section has no task.** §6's "Fixture: the first run operates on the owner's own ACS
hot-loader repository" and §9's "First target: the owner's ACS hot-loader repository" are not
implemented anywhere. Every task uses `tests/fixtures/artifact-mini` or the hand-run `runs/pcm`
documents. That is a real gap: it is the spec's stated acceptance evidence for whether the design
holds. It needs a Task 16, added below.

**One smaller gap, left open on purpose.** §7's "declare what was skipped" reaches the model
through `render_artifact`, so intake cannot invent a mechanism from a file it never read. It does
not reach the reader: `story.build_footer` has no line recording the files intake did not read.
That is a deliberate omission rather than a hole. The footer exists so a reader can audit the pitch
without the pitch being flattened by it, and a list of files the tool declined to open is an
intake-internal fact. The model still sees it, which is where §7's requirement actually bites. If
the owner wants it on the page later, `build_footer` already receives `claims`, so it is one line
and one schema field.

**§5's "Run one uses a template" is now asserted on both halves.** Task 14 covers retrieval
returning nothing from an empty corpus; Task 10's new
`test_the_first_ever_run_gets_a_template_prompt_with_no_exemplars` covers the prompt half, asserting
that the first run says "No worked examples are available yet" rather than showing an empty block.

### Placeholder scan

Clean. No `TBD`, `TODO`, `FIXME`, "similar to Task N", "add appropriate error handling", "fill in
details", or "etc." anywhere. Every code step carries a real code block, every run step carries a
command and an expected result, and every referenced function is defined in a task.

Two steps describe work instead of showing it:

- **Task 13 Step 4** shows the replacement trends branch but moves `collect_artifact` and `intake`
  above it in prose. That reordering is load-bearing, because the live branch reads `claims`. The
  step must print the whole reordered `run()` body. Corrected in Task 13 below.
- **Task 9 Step 3** instructs "Replace `CheckReport.cap_violations`", so the merged file contains
  `cap_violations` twice: the stub returning `()` in Task 8's block and the real body in Task 9's.
  That is intentional, but an executor reading only Task 8 ships the stub. The step must say which
  block it replaces. Corrected in Task 9 below.

### Type consistency

| Checked | Verdict |
|---|---|
| `story.story(*, claims, positioning, trends, llm, exemplars=(), max_rewrites=MAX_REWRITES) -> tuple[str, CheckReport]` | consistent in Tasks 10, 11, 12, 14 |
| `story.build_story_prompt(*, positioning, claims, trends, exemplars=()) -> str` | consistent |
| `story.clean_body(raw)` | **omission.** Task 10 had no Interfaces block at all, so this signature was never stated. The block added in Task 10 now gives `-> tuple[str, list[dict]]`, matching the implementation and the tests. |
| `story.build_footer(...)` | **omission.** Same cause; the added block gives the `extra_flags: list[dict] = ()` parameter. |
| `story.build_proof_table`, `story.build_trends_note`, `story.assemble_story` | **omissions.** All three are defined and used but were missing from any Interfaces line. All three are now in Task 10's Produces line. |
| `checks.check_story`, `checks.split_body_footer`, `checks.CheckReport` members | consistent |
| `flags.*` (`merge_flags`, `render_flags`, `make_flag`, `ask_questions`, `answers_as_prompt`, `FLAG_PATTERN`, `NEED_KINDS`) | consistent |
| `positioning.positioning`, `positioning.content_words` | consistent |
| `intake.intake`, `artifact.collect_artifact`, `artifact.Artifact.name` | consistent |
| `llm.LLM`, `FakeLLM`, `extract_json`, `WEB_SEARCH_TOOL`, `default_llm` | consistent, except `DEFAULT_MODEL` below |
| `schemas.require_valid`, `TRENDS_SPEC`, `TRENDS_SCHEMA`, `SOPHISTICATION_STAGES`, `validate_trends` | consistent |
| `errors.*` | consistent |
| `pipeline.close_flag_loop` | **mismatch.** Task 12's Interfaces line lists `claims`, `trends` and `out`; the implementation reads them from disk through `result`. Fixed. |
| `pipeline.RunResult` | **mismatch.** Task 11's Interfaces line says `report: CheckReport`; the dataclass is `CheckReport \| None = None`, because a stopped human-mode run has no report. Fixed. |
| `pipeline.run(...)` | **incomplete in Task 11.** Tasks 12, 13 and 14 each add a parameter; Task 11 must give the final signature. Fixed. |

### Two further defects

- **`llm.DEFAULT_MODEL` shipped as the empty string.** `AnthropicHTTPLLM.__init__` defaulted
  `model` to it and `default_llm()` fell back to it whenever `PRD_AGENT_MODEL` was unset, so a
  real run sent an empty model id and the provider rejected it with a 400 before the
  missing-key message could help. Fixed in Task 2: the constant is a real model id and
  `default_llm()` treats a blank `PRD_AGENT_MODEL` as unset instead of forwarding it. The new
  `test_default_llm_treats_a_blank_model_override_as_unset` pins it, and Task 2's expected
  count moves from 10 to 11.

- **`evals.select_exemplars`'s zero-score guard.** The guard `if points == 0 and rank > 0 and
  not picked: break` only fired while nothing had been picked, because `rank` starts at 1 and
  `not picked` is true only on the first row, so a zero-score example could still be appended
  after a scoring one. Fixed in Task 14: the loop breaks on `if points == 0`, which is correct
  because `ranked` is sorted by score descending. The new
  `test_select_exemplars_never_returns_a_zero_score_example` pins it.