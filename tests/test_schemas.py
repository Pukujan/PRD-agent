from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from prd_agent import schemas
from prd_agent.errors import SchemaError


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_reference_claims_document_validates(pcm_run: Path) -> None:
    assert schemas.validate_claims(load(pcm_run / "claims.json")) == []


def test_the_reference_trends_document_validates(pcm_run: Path) -> None:
    assert schemas.validate_trends(load(pcm_run / "trends.json")) == []


def test_the_reference_positioning_document_validates(pcm_run: Path) -> None:
    assert schemas.validate_positioning(load(pcm_run / "positioning.json")) == []


def test_a_missing_field_is_reported_with_its_path(pcm_run: Path) -> None:
    doc = load(pcm_run / "claims.json")
    del doc["artifact"]["commit"]
    problems = schemas.validate_claims(doc)
    assert "$.artifact.commit: missing" in problems


def test_an_unknown_claim_status_is_rejected(pcm_run: Path) -> None:
    doc = copy.deepcopy(load(pcm_run / "claims.json"))
    doc["claims"][0]["status"] = "probably"
    problems = schemas.validate_claims(doc)
    assert any("status" in problem and "probably" in problem for problem in problems)


def test_an_unexpected_field_is_rejected(pcm_run: Path) -> None:
    doc = copy.deepcopy(load(pcm_run / "trends.json"))
    doc["vibes"] = "good"
    problems = schemas.validate_trends(doc)
    assert "$.vibes: unexpected field" in problems


def test_an_unknown_sophistication_stage_is_rejected(pcm_run: Path) -> None:
    doc = copy.deepcopy(load(pcm_run / "trends.json"))
    doc["category"]["sophistication_stage"] = "vibes"
    problems = schemas.validate_trends(doc)
    assert any("sophistication_stage" in problem for problem in problems)


def test_require_valid_raises_with_a_readable_message(pcm_run: Path) -> None:
    doc = load(pcm_run / "positioning.json")
    doc["swap_test"]["passed"] = "yes"
    with pytest.raises(SchemaError) as error:
        schemas.require_valid(doc, schemas.POSITIONING_SPEC, "positioning.json")
    assert "positioning.json" in str(error.value)
    assert "swap_test.passed" in str(error.value)
