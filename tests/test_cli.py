from __future__ import annotations

import json
from pathlib import Path

from prd_agent import cli

def test_the_documented_invocation_parses() -> None:
    args = cli.build_parser().parse_args(["../some-repo"])
    assert args.artifact_path == "../some-repo"
    assert args.autonomous is True
    assert args.interactive is False
    assert args.out is None
    assert args.trends_file is None
    assert args.answers_file is None

def test_autonomous_and_out_parse() -> None:
    args = cli.build_parser().parse_args(["repo", "--autonomous", "--out", "stories/x.md"])
    assert args.autonomous is True
    assert args.out == "stories/x.md"

def test_interactive_flag_parses() -> None:
    args = cli.build_parser().parse_args(["repo", "--interactive"])
    assert args.interactive is True

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
    assert "### Proof and open items" not in written.read_text(encoding="utf-8")
    assert json.loads((tmp_path / "runs" / "mini" / "positioning.json").read_text(encoding="utf-8"))["schema"] == "prd-agent.positioning.v1"

def test_main_reports_a_stage_failure_with_a_nonzero_code(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    code = cli.main([str(artifact), "--autonomous", "--no-web"])
    assert code == 2
    assert "--trends-file" in capsys.readouterr().err


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


def test_no_web_parses() -> None:
    args = cli.build_parser().parse_args(["repo", "--no-web", "--trends-file", "t.json"])
    assert args.no_web is True
    assert args.trends_file == "t.json"


