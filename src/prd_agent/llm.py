"""The one place the pipeline talks to a model.

Every stage takes an `LLM`, so the whole pipeline runs in tests with no network and no
credentials. The only shipped provider is stdlib `urllib`, which keeps runtime dependencies
at zero.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Protocol

from prd_agent.errors import LLMUnavailable, ModelOutputError, StageError

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_MAX_TOKENS = int(os.environ.get("PRD_AGENT_MAX_TOKENS", "8000"))
RETRY_DELAY_SECONDS = 2.0
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504, 529})
WEB_SEARCH_TOOL: dict[str, object] = {"type": "web_search_20250305", "name": "web_search", "max_uses": 8}


class LLM(Protocol):
    def complete(
        self,
        *,
        system: str,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        tools: list[dict] | None = None,
    ) -> str: ...


class FakeLLM:
    """A scripted model for tests: returns queued responses and records every call."""

    def __init__(self, responses: list[str] | str) -> None:
        self._responses = [responses] if isinstance(responses, str) else list(responses)
        self.calls: list[dict[str, object]] = []

    def complete(
        self,
        *,
        system: str,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        tools: list[dict] | None = None,
    ) -> str:
        self.calls.append({"system": system, "prompt": prompt, "max_tokens": max_tokens, "tools": tools})
        if not self._responses:
            raise StageError("FakeLLM ran out of scripted responses")
        return self._responses.pop(0)


class CannedLLM:
    """Replays numbered text files in order, so a keyless smoke run can drive the pipeline."""

    def __init__(self, directory: Path) -> None:
        self._files = sorted(Path(directory).glob("*.txt"))
        if not self._files:
            raise StageError(f"no canned responses in {directory}")
        self._index = 0
        self.calls: list[dict[str, object]] = []

    def complete(
        self,
        *,
        system: str,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        tools: list[dict] | None = None,
    ) -> str:
        self.calls.append({"system": system, "prompt": prompt, "max_tokens": max_tokens, "tools": tools})
        if self._index >= len(self._files):
            raise StageError("CannedLLM ran out of canned responses")
        text = self._files[self._index].read_text(encoding="utf-8")
        self._index += 1
        return text


class AnthropicHTTPLLM:
    """The Anthropic Messages API over stdlib urllib."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        api_key: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        base_url: str = ANTHROPIC_URL,
        timeout: float = 300.0,
        attempts: int = 2,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.base_url = base_url
        self.timeout = timeout
        self.attempts = max(1, attempts)

    def build_request(
        self,
        *,
        system: str,
        prompt: str,
        max_tokens: int | None = None,
        tools: list[dict] | None = None,
    ) -> tuple[str, dict[str, str], bytes]:
        headers = {
            "content-type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
        }
        payload: dict[str, object] = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }
        if tools:
            payload["tools"] = tools
        return self.base_url, headers, json.dumps(payload).encode("utf-8")

    def complete(
        self,
        *,
        system: str,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        tools: list[dict] | None = None,
    ) -> str:
        url, headers, body = self.build_request(system=system, prompt=prompt, max_tokens=max_tokens, tools=tools)
        last_error: Exception | None = None
        for attempt in range(1, self.attempts + 1):
            request = urllib.request.Request(url, data=body, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                return extract_text(payload)
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code not in RETRYABLE_STATUS or attempt == self.attempts:
                    detail = (exc.read() or b"").decode("utf-8", "replace")[:500]
                    raise StageError(f"model call failed with HTTP {exc.code}: {detail}") from exc
                time.sleep(RETRY_DELAY_SECONDS * attempt)
            except (urllib.error.URLError, OSError) as exc:
                last_error = exc
                if attempt == self.attempts:
                    raise StageError(f"model call failed: {exc}") from exc
                time.sleep(RETRY_DELAY_SECONDS * attempt)
        raise StageError(f"model call failed: {last_error}")


def extract_text(payload: dict) -> str:
    """Join the text blocks of a Messages API response."""
    blocks = payload.get("content") or []
    parts = [
        str(block.get("text", ""))
        for block in blocks
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    text = "\n".join(part for part in parts if part).strip()
    if not text:
        raise ModelOutputError("the model response contained no text blocks")
    return text


def salvage_json(text: str) -> dict | None:
    """Salvage completed objects from a truncated JSON stream.

    Walks forward scanning structural delimiters outside string literals,
    then evaluates candidate closing prefixes from latest to earliest.
    """
    start = text.find("{")
    if start == -1:
        return None
    raw = text[start:]

    stack: list[str] = []
    in_string = False
    escape = False
    candidates: list[tuple[int, str]] = []

    for i, char in enumerate(raw):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
                if stack and stack[-1] == "]":
                    candidates.append((i + 1, "".join(reversed(stack))))
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            stack.append("}")
        elif char == "[":
            stack.append("]")
        elif char == "}":
            if stack and stack[-1] == "}":
                stack.pop()
                candidates.append((i + 1, "".join(reversed(stack))))
        elif char == "]":
            if stack and stack[-1] == "]":
                stack.pop()
                candidates.append((i + 1, "".join(reversed(stack))))

    for end_pos, closing in reversed(candidates):
        prefix = raw[:end_pos].rstrip().rstrip(",")
        attempt = prefix + closing
        try:
            parsed = json.loads(attempt)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and parsed:
            return parsed
    return None


def extract_json(text: str) -> dict:
    """Pull one JSON object out of a model reply, fenced or wrapped in prose."""
    candidates: list[str] = [block.strip() for block in re.findall(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])
    candidates.append(text.strip())
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    salvaged = salvage_json(text)
    if salvaged is not None:
        return salvaged
    raise ModelOutputError("no JSON object could be parsed from the model response")


def normalize_anthropic_url(url: str) -> str:
    """Normalize custom Anthropic base URLs (e.g. LiteLLM proxies) to the /v1/messages endpoint."""
    cleaned = url.strip().rstrip("/")
    if not cleaned:
        return ANTHROPIC_URL
    if cleaned.endswith("/messages"):
        return cleaned
    if cleaned.endswith("/v1"):
        return f"{cleaned}/messages"
    return f"{cleaned}/v1/messages"


def default_llm() -> LLM:
    """The provider a real run uses: canned replay when asked, else the API."""
    if os.environ.get("PRD_AGENT_LLM", "").strip().lower() == "fake":
        directory = os.environ.get("PRD_AGENT_CANNED_DIR", "").strip()
        if not directory:
            raise LLMUnavailable("PRD_AGENT_LLM=fake needs PRD_AGENT_CANNED_DIR set to a directory of .txt files")
        return CannedLLM(Path(directory))
    api_key = (
        os.environ.get("ANTHROPIC_API_KEY", "").strip()
        or os.environ.get("HADES_LITELLM_API_KEY", "").strip()
        or os.environ.get("OPENCODE_LITELLM_MASTER_KEY", "").strip()
    )
    if not api_key:
        raise LLMUnavailable(
            "ANTHROPIC_API_KEY is not set, so no model call can be made. Export it, set "
            "PRD_AGENT_LLM=fake with PRD_AGENT_CANNED_DIR for an offline run, or inject an LLM."
        )
    max_tokens = int(os.environ.get("PRD_AGENT_MAX_TOKENS", str(DEFAULT_MAX_TOKENS)))
    model = (
        os.environ.get("PRD_AGENT_MODEL", "").strip()
        or os.environ.get("ANTHROPIC_MODEL", "").strip()
        or DEFAULT_MODEL
    )
    raw_base_url = os.environ.get("ANTHROPIC_BASE_URL", "").strip()
    base_url = normalize_anthropic_url(raw_base_url) if raw_base_url else ANTHROPIC_URL
    return AnthropicHTTPLLM(
        model=model,
        api_key=api_key,
        max_tokens=max_tokens,
        base_url=base_url,
    )

