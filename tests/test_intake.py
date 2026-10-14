from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prd_agent import intake
from prd_agent.errors import ModelOutputError, SchemaError
from prd_agent.llm import FakeLLM

FIXTURE = Path(__file__).parent / "fixtures" / "artifact-mini"


def make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "mini"
    shutil.copytree(FIXTURE, root)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "-C", root, "config", "user.email", "fixture@example.invalid"], check=True)
    subprocess.run(["git", "-C", root, "config", "user.name", "Fixture"], check=True)
    subprocess.run(["git", "-C", root, "add", "."], check=True)
    subprocess.run(["git", "-C", root, "commit", "-qm", "first commit"], check=True)
    return root


def reference_claims(pcm_run: Path) -> str:
    return (pcm_run / "claims.json").read_text(encoding="utf-8")


def test_the_prompt_carries_the_files_and_the_commit_subjects(tmp_path: Path) -> None:
    artifact = intake.collect_artifact(make_repo(tmp_path))
    prompt = intake.build_intake_prompt(artifact)
    assert "def greet" in prompt
    assert "first commit" in prompt
    assert "never invent a mechanism" in prompt.lower()


def test_intake_returns_a_document_that_matches_the_contract(tmp_path: Path, pcm_run: Path) -> None:
    fake = FakeLLM(reference_claims(pcm_run))
    doc = intake.intake(make_repo(tmp_path), fake)
    assert doc["schema"] == "prd-agent.claims.v1"
    assert len(doc["claims"]) == 12
    assert doc["artifact"]["name"] == "mini"
    assert doc["artifact"]["commit"] != "unknown"
    assert doc["artifact"]["path"].endswith("mini")


def test_intake_accepts_a_fenced_json_reply(tmp_path: Path, pcm_run: Path) -> None:
    fake = FakeLLM("```json\n" + reference_claims(pcm_run) + "\n```")
    assert intake.intake(make_repo(tmp_path), fake)["claims"]


def test_intake_rejects_a_reply_that_is_not_json(tmp_path: Path) -> None:
    with pytest.raises(ModelOutputError):
        intake.intake(make_repo(tmp_path), FakeLLM("I had a look and it seems fine."))


def test_intake_rejects_a_claim_with_no_status(tmp_path: Path, pcm_run: Path) -> None:
    doc = json.loads(reference_claims(pcm_run))
    del doc["claims"][0]["status"]
    with pytest.raises(SchemaError):
        intake.intake(make_repo(tmp_path), FakeLLM(json.dumps(doc)))


def test_intake_uses_the_supplied_artifact_without_re_reading(tmp_path: Path, pcm_run: Path) -> None:
    artifact = intake.collect_artifact(make_repo(tmp_path))
    doc = intake.intake(tmp_path / "nowhere", FakeLLM(reference_claims(pcm_run)), artifact=artifact)
    assert doc["artifact"]["name"] == "mini"
