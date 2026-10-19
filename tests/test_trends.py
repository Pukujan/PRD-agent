from __future__ import annotations

import json
from pathlib import Path

import pytest

from prd_agent import trends
from prd_agent.errors import ModelOutputError, SchemaError
from prd_agent.llm import FakeLLM
from prd_agent.schemas import validate_trends


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def test_the_prompt_names_all_three_trend_kinds_and_the_stage_question(pcm_run: Path) -> None:
    prompt = trends.build_trends_prompt(load(pcm_run / "claims.json"), searched_at="2026-10-13")
    assert "Category." in prompt and "Style." in prompt and "Cultural." in prompt
    assert "Human Nightmare." in prompt and "Trending Hype Words." in prompt and "Unlocked Dream." in prompt
    assert "False Dogma." in prompt and "Rebellion Belief." in prompt
    assert "virgin" in prompt and "crowded" in prompt and "jaded" in prompt and "exhausted" in prompt
    assert "Stores a project's working memory as ordinary Markdown and JSON files in Git" in prompt  # the artifact's own claim reaches the search

def test_the_prompt_carries_the_artifact_claims_verbatim(pcm_run: Path) -> None:
    claims = load(pcm_run / "claims.json")
    prompt = trends.build_trends_prompt(claims, searched_at="2026-10-13")
    assert claims["claims"][0]["text"] in prompt
    assert claims["claims"][0]["evidence"] in prompt

def test_the_web_search_tool_is_attached_to_the_one_call(pcm_run: Path) -> None:
    fake = FakeLLM(json.dumps(load(pcm_run / "trends.json")))
    trends.analyze(load(pcm_run / "claims.json"), fake, searched_at="2026-10-13")
    assert fake.calls[0]["tools"] == [trends.llm.WEB_SEARCH_TOOL]
    assert len(fake.calls) == 1

def test_analyze_returns_a_valid_document_and_stamps_searched_at(pcm_run: Path) -> None:
    payload = load(pcm_run / "trends.json")
    payload.pop("searched_at")
    fake = FakeLLM(json.dumps(payload))
    doc = trends.analyze(load(pcm_run / "claims.json"), fake, searched_at="2026-10-13")
    assert doc["searched_at"] == "2026-10-13"
    assert validate_trends(doc) == []

def test_analyze_defaults_searched_at_to_today(pcm_run: Path) -> None:
    doc = trends.analyze(load(pcm_run / "claims.json"), FakeLLM(json.dumps(load(pcm_run / "trends.json"))))
    assert len(doc["searched_at"]) == 10 and doc["searched_at"].count("-") == 2

def test_analyze_accepts_a_fenced_reply(pcm_run: Path) -> None:
    raw = "```json\n" + json.dumps(load(pcm_run / "trends.json")) + "\n```"
    assert trends.analyze(load(pcm_run / "claims.json"), FakeLLM(raw))["category"]["competitors"]

def test_analyze_rejects_a_reply_that_is_not_json(pcm_run: Path) -> None:
    with pytest.raises(ModelOutputError):
        trends.analyze(load(pcm_run / "claims.json"), FakeLLM("I searched the web for you."))

def test_analyze_rejects_a_missing_stage_note(pcm_run: Path) -> None:
    payload = load(pcm_run / "trends.json")
    del payload["category"]["stage_note"]
    with pytest.raises(SchemaError):
        trends.analyze(load(pcm_run / "claims.json"), FakeLLM(json.dumps(payload)))

def test_analyze_rejects_an_invented_sophistication_stage(pcm_run: Path) -> None:
    payload = load(pcm_run / "trends.json")
    payload["category"]["sophistication_stage"] = "loud"
    with pytest.raises(SchemaError):
        trends.analyze(load(pcm_run / "claims.json"), FakeLLM(json.dumps(payload)))

def test_every_stage_has_a_brief_and_they_are_all_distinct(pcm_run: Path) -> None:
    assert set(trends.STAGE_BRIEF) == set(trends.SOPHISTICATION_STAGES)
    assert len(set(trends.STAGE_BRIEF.values())) == 4

def test_the_fixture_and_the_live_path_produce_the_same_shape(pcm_run: Path) -> None:
    """The step-6 replacement for the fixture cannot change what step 3 consumes."""
    fixture = load(pcm_run / "trends.json")
    live = trends.analyze(load(pcm_run / "claims.json"), FakeLLM(json.dumps(fixture)), searched_at="2026-10-13")
    assert validate_trends(fixture) == [] and validate_trends(live) == []
    assert live.keys() == fixture.keys()
    assert live["category"].keys() == fixture["category"].keys()
    assert live["style"].keys() == fixture["style"].keys()
    assert [item.keys() for item in live["category"]["competitors"]] == [
        item.keys() for item in fixture["category"]["competitors"]
    ]


def test_search_tools_can_be_disabled_via_env_var(monkeypatch) -> None:
    monkeypatch.setenv("PRD_AGENT_NO_SEARCH_TOOL", "1")
    assert trends.search_tools() == []
    monkeypatch.setenv("PRD_AGENT_NO_SEARCH_TOOL", "0")
    assert trends.search_tools() == [trends.llm.WEB_SEARCH_TOOL]


def test_is_search_context_detects_raw_snippets() -> None:
    assert not trends.is_search_context("Short error message")
    assert not trends.is_search_context("I searched the web for you and found nothing.")
    snippet_text = (
        "Search Results for prompt engineering tools:\n"
        "1. Title: Tool Alpha\n"
        "   URL: https://example.com/alpha\n"
        "   Snippet: The best prompt tool.\n"
        "2. Title: Tool Beta\n"
        "   URL: https://example.com/beta\n"
        "   Snippet: Automate your prompts."
    )
    assert trends.is_search_context(snippet_text)


def test_analyze_performs_secondary_synthesis_when_search_snippets_returned(pcm_run: Path) -> None:
    fixture = load(pcm_run / "trends.json")
    raw_snippets = (
        "DuckDuckGo search results for software continuity git tools:\n"
        "[1] URL: https://example.com/cm-tool Title: Continuous Memory Tools\n"
        "    Snippet: Git-based memory tools for multi-agent workflows.\n"
        "[2] URL: https://example.com/git-assist Title: Git Assistant\n"
        "    Snippet: Never lose context across agents."
    )
    fake = FakeLLM([raw_snippets, json.dumps(fixture)])
    doc = trends.analyze(load(pcm_run / "claims.json"), fake, searched_at="2026-10-13")
    assert len(fake.calls) == 2
    assert fake.calls[0]["tools"] == [trends.llm.WEB_SEARCH_TOOL]
    assert fake.calls[1]["tools"] is None
    assert "raw search results and market snippets" in str(fake.calls[1]["prompt"])
    assert doc["category"]["competitors"] == fixture["category"]["competitors"]
    assert validate_trends(doc) == []
