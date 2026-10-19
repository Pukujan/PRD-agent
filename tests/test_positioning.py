# tests/test_positioning.py
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from prd_agent import positioning
from prd_agent.errors import ModelOutputError, SchemaError
from prd_agent.llm import FakeLLM

FIXTURE = Path(__file__).parent / "fixtures" / "trends_pcm.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_content_words_drops_stopwords_and_short_words() -> None:
    assert positioning.content_words("The memory is the Git repository itself") == {
        "memory", "git", "repository", "itself"
    }


def test_the_reference_differentiator_survives_the_swap_test(pcm_run: Path) -> None:
    trends = load(FIXTURE)
    differentiator = load(pcm_run / "positioning.json")["differentiator"]
    result = positioning.swap_test(differentiator, trends["category"]["competitors"])
    # Calibrated on the hand run: the closest competitor is far below the threshold.
    # Measured overlaps: Mem0: 0.03, Zep: 0.03, Letta: 0.06, agentmemory: 0.00, GitHub Spec Kit: 0.00, Kiro: 0.00.
    assert result.passed is True
    assert result.collisions == ()
    assert result.max_overlap < positioning.SWAP_OVERLAP_THRESHOLD
    assert result.closest


def test_a_parroted_competitor_line_fails_the_swap_test() -> None:
    competitors = [
        {
            "name": "Mem0",
            "url": "https://example.invalid",
            "claim": "AI coding agents that actually remember your codebase",
            "language": ["persistent memory", "dedicated memory layer", "remembers everything"],
        }
    ]
    result = positioning.swap_test("Persistent memory as a dedicated memory layer", competitors)
    assert result.passed is False
    assert result.collisions == ("Mem0",)
    assert "Mem0" in result.note


def test_an_empty_differentiator_never_passes() -> None:
    result = positioning.swap_test("", [])
    assert result.passed is False
    assert "empty" in result.note.lower()


def test_positioning_overwrites_the_models_own_swap_test(pcm_run: Path) -> None:
    """The model proposes; the machine adjudicates. A model claiming a pass is ignored."""
    doc = load(pcm_run / "positioning.json")
    doc["flags"] = [flag for flag in doc["flags"] if flag["need"] != "differentiator"]
    doc["swap_test"] = {"passed": False, "note": "the model was unsure"}
    doc["differentiator"] = "Persistent memory as a dedicated memory layer for coding agents"
    trends = load(FIXTURE)
    result = positioning.positioning(load(pcm_run / "claims.json"), trends, FakeLLM(json.dumps(doc)))
    assert result["swap_test"]["passed"] is False
    assert any(flag["need"] == "differentiator" for flag in result["flags"])


def test_a_passing_differentiator_adds_no_flag(pcm_run: Path) -> None:
    doc = load(pcm_run / "positioning.json")
    doc["flags"] = [flag for flag in doc["flags"] if flag["need"] != "differentiator"]
    doc["swap_test"] = {"passed": False, "note": "wrong on purpose"}
    result = positioning.positioning(load(pcm_run / "claims.json"), load(FIXTURE), FakeLLM(json.dumps(doc)))
    assert result["swap_test"]["passed"] is True
    assert not any(flag["need"] == "differentiator" for flag in result["flags"])


def test_positioning_rejects_a_broken_document(pcm_run: Path) -> None:
    doc = copy.deepcopy(load(pcm_run / "positioning.json"))
    del doc["vision"]
    with pytest.raises(SchemaError):
        positioning.positioning(load(pcm_run / "claims.json"), load(FIXTURE), FakeLLM(json.dumps(doc)))


def test_positioning_rejects_a_non_json_reply(pcm_run: Path) -> None:
    with pytest.raises(ModelOutputError):
        positioning.positioning(load(pcm_run / "claims.json"), load(FIXTURE), FakeLLM("sure thing"))


def test_the_prompt_carries_the_competitors_and_the_owner_answers(pcm_run: Path) -> None:
    prompt = positioning.build_positioning_prompt(
        load(pcm_run / "claims.json"),
        load(FIXTURE),
        answers="The owner says there are 40 adopters.",
    )
    assert "Mem0" in prompt
    assert "jaded" in prompt
    assert "The owner says there are 40 adopters." in prompt


def test_the_positioning_prompt_requires_nightmare_and_dream_scenes(pcm_run: Path) -> None:
    prompt = positioning.build_positioning_prompt(load(pcm_run / "claims.json"), load(FIXTURE))
    assert "Story first, feature later" in prompt
    assert "nightmare scene" in prompt
    assert "dream scene" in prompt
    assert "metaphor" in prompt


def test_the_positioning_prompt_carries_hype_directive(pcm_run: Path) -> None:
    prompt_1000 = positioning.build_positioning_prompt(
        load(pcm_run / "claims.json"), load(FIXTURE), hype="1000"
    )
    assert "ELECTRIC GOD-MODE" in prompt_1000
    assert "One-Person Unicorn" in prompt_1000

    prompt_250 = positioning.build_positioning_prompt(
        load(pcm_run / "claims.json"), load(FIXTURE), hype="truth"
    )
    assert "PURE TECHNICAL TRUTH" in prompt_250

    doc = load(pcm_run / "positioning.json")
    result = positioning.positioning(
        load(pcm_run / "claims.json"), load(FIXTURE), FakeLLM(json.dumps(doc)), hype="750"
    )
    assert result["hype_level"] == "750"


def test_the_positioning_prompt_carries_persona_directive(pcm_run: Path) -> None:
    prompt_ent = positioning.build_positioning_prompt(
        load(pcm_run / "claims.json"), load(FIXTURE), persona="enterprise"
    )
    assert "ENTERPRISE" in prompt_ent
    assert "boardroom liability" in prompt_ent.lower()

    doc = load(pcm_run / "positioning.json")
    result = positioning.positioning(
        load(pcm_run / "claims.json"), load(FIXTURE), FakeLLM(json.dumps(doc)), persona="normie"
    )
    assert result["persona"] == "normie"



