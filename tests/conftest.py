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


@pytest.fixture(autouse=True)
def isolate_evals_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    temp_evals = tmp_path / "evals" / "story_evals.json"
    monkeypatch.setattr("prd_agent.evals.EVALS_PATH", temp_evals)

