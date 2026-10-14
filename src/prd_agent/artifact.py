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
