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
