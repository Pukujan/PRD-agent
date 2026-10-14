from __future__ import annotations

import hashlib
from pathlib import Path

from prd_agent import skill


def test_skill_and_references_load_from_the_package() -> None:
    context = skill.build_skill_context()
    assert "No AI Tells" in context
    assert "The Self-Check" in context
    assert "The Human Action Model" in context
    assert context.count("# Vendored reference:") == len(skill.REFERENCE_FILES)


def test_recorded_hashes_match_the_vendored_files() -> None:
    root = skill.skill_root()
    provenance = (root / "PROVENANCE.md").read_text(encoding="utf-8")
    recorded = {
        line.split()[1]: line.split()[0]
        for line in provenance.splitlines()
        if len(line.split()) == 2 and len(line.split()[0]) == 64
    }
    assert recorded, "PROVENANCE.md records no hashes"
    for relative, digest in recorded.items():
        data = (root / relative).read_bytes().replace(b"\r\n", b"\n")
        actual = hashlib.sha256(data).hexdigest()
        assert actual == digest, f"{relative} changed since it was vendored"



def test_reference_files_exist() -> None:
    for name in skill.REFERENCE_FILES:
        assert (skill.skill_root() / name).is_file(), name
