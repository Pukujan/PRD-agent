"""Load the vendored copywriting skill from disk.

The skill is an instruction document written for a model, not a library, so the pipeline
reads it at runtime and puts it in the system prompt. Reading it from disk rather than
inlining it keeps the vendored copy the single source of truth.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

SKILL_DIR = "copywriting"
SKILL_FILE = "SKILL.md"
REFERENCE_FILES: tuple[str, ...] = (
    "references/ai-tells.md",
    "references/copy-frameworks.md",
    "references/natural-transitions.md",
)


def skill_root() -> Path:
    """The vendored skill directory, resolved inside the installed package."""
    return Path(str(files("prd_agent.vendor"))) / SKILL_DIR


def load_skill() -> str:
    return (skill_root() / SKILL_FILE).read_text(encoding="utf-8")


def load_references(names: tuple[str, ...] = REFERENCE_FILES) -> dict[str, str]:
    return {name: (skill_root() / name).read_text(encoding="utf-8") for name in names}


def build_skill_context(names: tuple[str, ...] = REFERENCE_FILES) -> str:
    """The system-prompt text handed to the model: the skill, then its references."""
    parts = [f"# Vendored skill: copywriting ({SKILL_FILE})\n\n{load_skill()}"]
    for name, text in load_references(names).items():
        parts.append(f"\n\n# Vendored reference: {name}\n\n{text}")
    return "".join(parts)
