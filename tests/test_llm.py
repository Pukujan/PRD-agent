from __future__ import annotations

import json
import urllib.error
from pathlib import Path

import pytest

from prd_agent import llm


def test_fake_llm_returns_scripted_responses_in_order() -> None:
    fake = llm.FakeLLM(["first", "second"])
    assert fake.complete(system="s", prompt="p") == "first"
    assert fake.complete(system="s", prompt="p") == "second"
    assert [call["prompt"] for call in fake.calls] == ["p", "p"]


def test_fake_llm_fails_loudly_when_the_script_runs_out() -> None:
    fake = llm.FakeLLM([])
    with pytest.raises(llm.StageError):
        fake.complete(system="s", prompt="p")


def test_extract_json_handles_bare_fenced_and_prose_wrapped_objects() -> None:
    assert llm.extract_json('{"a": 1}') == {"a": 1}
    assert llm.extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert llm.extract_json('Here it is:\n\n{"a": 1}\n\nDone.') == {"a": 1}


def test_extract_json_rejects_a_response_with_no_object() -> None:
    with pytest.raises(llm.ModelOutputError):
        llm.extract_json("I could not do that.")


def test_request_carries_the_key_the_version_and_the_search_tool() -> None:
    client = llm.AnthropicHTTPLLM(model="m", api_key="k")
    url, headers, body = client.build_request(system="sys", prompt="hi", tools=[llm.WEB_SEARCH_TOOL])
    assert url.endswith("/v1/messages")
    assert headers["x-api-key"] == "k"
    assert headers["anthropic-version"] == llm.ANTHROPIC_VERSION
    payload = json.loads(body)
    assert payload["system"] == "sys"
    assert payload["messages"] == [{"role": "user", "content": "hi"}]
    assert payload["tools"] == [llm.WEB_SEARCH_TOOL]


def test_request_omits_tools_when_none_are_asked_for() -> None:
    client = llm.AnthropicHTTPLLM(model="m", api_key="k")
    _, _, body = client.build_request(system="s", prompt="p")
    assert "tools" not in json.loads(body)


def test_complete_reads_text_blocks_and_retries_a_server_error(monkeypatch) -> None:
    client = llm.AnthropicHTTPLLM(model="m", api_key="k")
    attempts = {"n": 0}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self) -> bytes:
            return json.dumps({"content": [{"type": "text", "text": "hello"}]}).encode()

    def fake_urlopen(request, timeout):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise urllib.error.HTTPError(request.full_url, 500, "boom", {}, None)
        return Response()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(llm.time, "sleep", lambda _seconds: None)
    assert client.complete(system="s", prompt="p") == "hello"
    assert attempts["n"] == 2


def test_complete_does_not_retry_a_client_error(monkeypatch) -> None:
    client = llm.AnthropicHTTPLLM(model="m", api_key="k")

    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 400, "bad", {}, None)

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(llm.StageError):
        client.complete(system="s", prompt="p")


def test_default_llm_requires_a_key(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("PRD_AGENT_LLM", raising=False)
    with pytest.raises(llm.LLMUnavailable):
        llm.default_llm()


def test_default_llm_returns_the_http_client_with_the_env_model(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.setenv("PRD_AGENT_MODEL", "some-model")
    client = llm.default_llm()
    assert isinstance(client, llm.AnthropicHTTPLLM)
    assert client.model == "some-model"


def test_default_llm_treats_a_blank_model_override_as_unset(monkeypatch) -> None:
    # An empty "model" field is a guaranteed 400 from the provider, so a blank
    # override must fall back to the built-in id rather than being sent.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.setenv("PRD_AGENT_MODEL", "   ")
    client = llm.default_llm()
    assert client.model == llm.DEFAULT_MODEL
    assert llm.DEFAULT_MODEL.strip()


def test_default_llm_can_be_switched_to_canned_responses(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "01.txt").write_text("first", encoding="utf-8")
    (tmp_path / "02.txt").write_text("second", encoding="utf-8")
    monkeypatch.setenv("PRD_AGENT_LLM", "fake")
    monkeypatch.setenv("PRD_AGENT_CANNED_DIR", str(tmp_path))
    client = llm.default_llm()
    assert client.complete(system="s", prompt="p") == "first"
    assert client.complete(system="s", prompt="p") == "second"


def test_default_llm_respects_max_tokens_env_var(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("PRD_AGENT_MAX_TOKENS", "4096")
    client = llm.default_llm()
    assert isinstance(client, llm.AnthropicHTTPLLM)
    assert client.max_tokens == 4096


def test_extract_json_salvages_truncated_stream() -> None:
    truncated = """```json
{
  "schema": "prd-agent.claims.v1",
  "artifact": {"name": "repo", "path": "/test", "commit": "abc", "read_at": "2026-10-18"},
  "claims": [
    {"id": "C-001", "text": "Claim 1", "status": "verified", "evidence": "f.py:1", "note": "ok"},
    {"id": "C-002", "text": "Claim 2", "status": "claimed", "evidence": "", "note": ""},
    {"id": "C-003", "text": "Claim 3 truncated mid-stream", "status": "ver
"""
    result = llm.extract_json(truncated)
    assert result["schema"] == "prd-agent.claims.v1"
    assert len(result["claims"]) == 2
    assert [c["id"] for c in result["claims"]] == ["C-001", "C-002"]


def test_extract_json_salvages_truncated_array_of_strings() -> None:
    truncated = """
{
  "schema": "prd-agent.trends.v1",
  "queries": ["query one", "query two", "query three trunca
"""
    result = llm.extract_json(truncated)
    assert result["schema"] == "prd-agent.trends.v1"
    assert result["queries"] == ["query one", "query two"]


def test_salvage_json_returns_none_when_no_json_present() -> None:
    assert llm.salvage_json("There is no json in this text.") is None

