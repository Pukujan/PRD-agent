"""Universal remote Git repository resolution and cloning seam.

Allows external developers and blind agents to pass a GitHub URL, SSH URI, or
shorthand `owner/repo` directly to PRD-agent without manual local cloning.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from prd_agent.errors import StageError

REMOTE_PREFIXES = ("http://", "https://", "git@", "ssh://", "github.com/")
SHORTHAND_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$")


def is_remote_url(source: str | Path) -> bool:
    """Return True if source looks like a remote repository URL or shorthand."""
    src = str(source).strip()
    if not src:
        return False
    # If it exists on the local filesystem, treat it as a local path first
    try:
        if Path(src).exists():
            return False
    except OSError:
        pass

    for prefix in REMOTE_PREFIXES:
        if src.startswith(prefix):
            return True

    return bool(SHORTHAND_PATTERN.match(src))


def normalize_remote_url(source: str) -> str:
    """Convert any supported remote string into a cloneable Git URL."""
    src = str(source).strip()
    if src.startswith("github.com/"):
        return f"https://{src}.git" if not src.endswith(".git") else f"https://{src}"
    if src.startswith(("http://", "https://", "git@", "ssh://")):
        return src
    if SHORTHAND_PATTERN.match(src):
        return f"https://github.com/{src}.git"
    return src


@contextmanager
def resolve_artifact_source(source: str | Path) -> Generator[Path, None, None]:
    """Resolve an artifact path or remote Git URL into a local directory Path.

    If given a remote URL or `owner/repo` shorthand, shallow-clones the repository
    into a temporary directory that is cleaned up when the context manager exits.
    """
    src_str = str(source).strip()
    if not is_remote_url(src_str):
        local_path = Path(src_str)
        if not local_path.exists():
            raise StageError(f"artifact path does not exist: {local_path}")
        yield local_path
        return

    url = normalize_remote_url(src_str)
    with tempfile.TemporaryDirectory(prefix="prd_agent_remote_") as temp_dir:
        dest = Path(temp_dir) / "repo"
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, str(dest)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            err = result.stderr.strip() or result.stdout.strip() or "unknown git error"
            raise StageError(f"failed to clone remote repository '{url}': {err}")
        yield dest
