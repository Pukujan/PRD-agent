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
        pipeline.run(tmp_path, llm=FakeLLM("{}"), autonomous=True, live=False)
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
        artifact, llm=FakeLLM(scripted), autonomous=True,
        evals_path=corpus_path,
    )
    assert corpus_path.is_file()
    assert load(corpus_path)["evals"][0]["task"] == "mini"

    second_llm = FakeLLM(scripted)
    pipeline.run(
        artifact, llm=second_llm, autonomous=True,
        evals_path=corpus_path,
    )
    assert "worked example" in str(second_llm.calls[3]["prompt"]).lower()
    assert load(corpus_path)["evals"][1]["id"] == 2
    assert first.story_path.is_file()


def repo_root_fixture() -> Path:
    return Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "trends_pcm.json"



