from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from prd_agent.errors import StageError
from prd_agent.remote import (
    is_remote_url,
    normalize_remote_url,
    resolve_artifact_source,
)


def test_is_remote_url(tmp_path: Path) -> None:
    assert is_remote_url("https://github.com/SouthpawIN/turbofit") is True
    assert is_remote_url("http://github.com/SouthpawIN/turbofit") is True
    assert is_remote_url("git@github.com:SouthpawIN/turbofit.git") is True
    assert is_remote_url("github.com/SouthpawIN/turbofit") is True
    assert is_remote_url("SouthpawIN/turbofit") is True

    # Local path that exists
    local_dir = tmp_path / "my_project"
    local_dir.mkdir()
    assert is_remote_url(str(local_dir)) is False
    assert is_remote_url(".") is False
    assert is_remote_url("not_a_repo") is False


def test_normalize_remote_url() -> None:
    assert (
        normalize_remote_url("SouthpawIN/turbofit")
        == "https://github.com/SouthpawIN/turbofit.git"
    )
    assert (
        normalize_remote_url("github.com/SouthpawIN/turbofit")
        == "https://github.com/SouthpawIN/turbofit.git"
    )
    assert (
        normalize_remote_url("https://github.com/SouthpawIN/turbofit")
        == "https://github.com/SouthpawIN/turbofit"
    )
    assert (
        normalize_remote_url("git@github.com:SouthpawIN/turbofit.git")
        == "git@github.com:SouthpawIN/turbofit.git"
    )


def test_resolve_artifact_source_local(tmp_path: Path) -> None:
    local_dir = tmp_path / "local_repo"
    local_dir.mkdir()
    with resolve_artifact_source(str(local_dir)) as resolved_path:
        assert resolved_path.resolve() == local_dir.resolve()


def test_resolve_artifact_source_clones_remote(tmp_path: Path) -> None:
    def fake_run(cmd, *args, **kwargs):
        # cmd: ['git', 'clone', '--depth', '1', url, dest]
        target = Path(cmd[5])
        target.mkdir(parents=True, exist_ok=True)
        (target / "README.md").write_text("# Cloned Repo\n", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")

    with patch("subprocess.run", side_effect=fake_run):
        with resolve_artifact_source("SouthpawIN/turbofit") as resolved_path:
            assert resolved_path.is_dir()
            assert (resolved_path / "README.md").is_file()


def test_resolve_artifact_source_clone_failure() -> None:
    def failing_run(cmd, *args, **kwargs):
        return subprocess.CompletedProcess(
            cmd, returncode=128, stdout="", stderr="Repository not found"
        )

    with patch("subprocess.run", side_effect=failing_run):
        with pytest.raises(StageError, match="failed to clone remote repository"):
            with resolve_artifact_source("Pukujan/nonexistent-404"):
                pass


def test_action_yml_is_valid(repo_root: Path) -> None:
    action_path = repo_root / "action.yml"
    assert action_path.is_file(), "action.yml must exist at repository root"
    content = action_path.read_text(encoding="utf-8")
    assert "name:" in content
    assert "runs:" in content
    assert "using: 'composite'" in content or "using: \"composite\"" in content
    assert "anthropic_api_key" in content


def test_cli_main_with_remote_repo_url(
    tmp_path: Path, repo_root: Path, pcm_run: Path, monkeypatch, capsys
) -> None:
    from prd_agent import cli

    canned = tmp_path / "canned"
    canned.mkdir()
    for index, source in enumerate(
        [pcm_run / "claims.json", pcm_run / "positioning.json"],
        start=1,
    ):
        (canned / f"{index:02d}.txt").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (canned / "03.txt").write_text(
        (repo_root / "tests" / "test_story.py")
        .read_text(encoding="utf-8")
        .split('GOOD_BODY = """\\\n')[1]
        .split('"""')[0],
        encoding="utf-8",
    )

    def fake_clone(cmd, *args, **kwargs):
        dest = Path(cmd[5])
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "README.md").write_text("# Remote Turbofit\n", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setenv("PRD_AGENT_LLM", "fake")
    monkeypatch.setenv("PRD_AGENT_CANNED_DIR", str(canned))
    monkeypatch.chdir(tmp_path)

    with patch("subprocess.run", side_effect=fake_clone):
        code = cli.main([
            "https://github.com/SouthpawIN/turbofit",
            "--autonomous",
            "--trends-file", str(repo_root / "tests" / "fixtures" / "trends_pcm.json"),
        ])
        assert code == 0
        captured = capsys.readouterr()
        assert "5-LINE EXECUTIVE BATTLE CRY" in captured.out
        assert "prd-agent: wrote" in captured.out
        assert (tmp_path / "stories" / "turbofit.md").is_file()
        assert (tmp_path / "runs" / "turbofit" / "five_lines.txt").is_file()
