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
