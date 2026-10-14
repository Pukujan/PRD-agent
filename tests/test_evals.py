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
    assert "the memory is the git repository itself" in record["prompt"].lower()
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
    assert evals.score("persistent memory for coding agents", exemplar) == 4
    assert evals.score("a story about billing retries", exemplar) == 2

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
