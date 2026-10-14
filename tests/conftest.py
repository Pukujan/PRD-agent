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
