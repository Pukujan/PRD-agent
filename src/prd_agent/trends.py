"""The live web pass: category, style and cultural trends, plus the market sophistication stage.

Version one ships no scraped corpus; the corpus seam is documented in docs/CORPUS_SEAM.md and not
built. The search happens inside the one model call, through the provider's own web search tool,
so this module adds no dependency, no second credential and no HTML parsing.
"""

from __future__ import annotations

import json
import os
from datetime import date

from prd_agent import llm
from prd_agent.errors import ModelOutputError
from prd_agent.llm import LLM, WEB_SEARCH_TOOL, extract_json
from prd_agent.schemas import (
    SOPHISTICATION_STAGES,
    TRENDS_SCHEMA,
    TRENDS_SPEC,
    require_valid,
)

__all__ = [
    "STAGE_BRIEF",
    "TRENDS_SCHEMA",
    "TRENDS_SPEC",
    "TRENDS_SYSTEM",
    "analyze",
    "build_trends_prompt",
    "llm",
    "search_tools",
    "SOPHISTICATION_STAGES",
]

STAGE_BRIEF = {
    "virgin": "No one has heard the claim. State it plainly and be the first to name the problem.",
    "crowded": "Everyone makes the same claim. Make a bigger claim and back it with the mechanism.",
    "jaded": "The claim has gone flat and abstract. Lead with a new mechanism, not a louder promise.",
    "exhausted": "The category has burned the reader. Get identification first, then the mechanism.",
}

TRENDS_SYSTEM = (
    "You are a cultural zeitgeist and market trend researcher. You search the live web and report "
    "what competitors claim, viral hype words landing right now, the universal human nightmare "
    "developers/founders secretly live with, and the aspirational unlocked dream. You report what "
    "you find with URLs. You answer with JSON and nothing else."
)

_PROMPT_TEMPLATE = """\
Search the live web and report the market this product is entering.

Extract all trend kinds:

- Category. What competing and adjacent products claim right now, with the language they use,
  quoted from the page. This is what makes a swap test runnable, so the `language` list must be
  the competitor's own words, not a paraphrase.
- Style. What register of copy is currently landing, so the story reads current rather than dated.
- Cultural. The conversation worth attaching to, with the URL and why it matters here.
- Human Nightmare. The universal emotional pain, exhaustion, or anxiety developers and founders
  secretly live with in this category (e.g. babysitting toddlers with root access, 2:00 AM panic).
- Trending Hype Words. Viral, high-energy hype words and phrases currently landing in discussions on
  X, Reddit, and Hacker News.
- Unlocked Dream. The ultimate aspirational future beyond current limits that humans actually crave
  (e.g. solo founder out-shipping 50 engineers, uninterrupted 8 hours of sleep).
- False Dogma. The cynical lie, shallow shortcut, or toy belief the industry has settled for that
  users secretly hate or feel insulted by (e.g. "AI is only good for spitting out cheap slop",
  "just prompt it and accept whatever garbage comes out", "real work requires a 20-person committee").
- Rebellion Belief. The radical counter-truth that gives power and sovereignty back to the creator/engineer
  (e.g. "the human artist/engineer holds the steering wheel", "AI as a supersonic rocket booster for mastery,
  not a slot machine for slop").

Then pick the market sophistication stage (Schwartz) and say why:
- virgin: no one has heard the claim, so state it.
- crowded: everyone makes the same claim, so make a bigger claim.
- jaded: the claim has gone flat, so lead with a new mechanism.
- exhausted: the category has burned the reader, so lead with identification.

Rules:
1. Every competitor and every cultural moment carries a URL you actually read.
2. Do not describe a competitor's internals. Report what their page claims.
3. The `stage_note` says what the stage means for how loud this story should go.
4. Answer with exactly this JSON object and no prose around it:

{schema}

The artifact's own claims, so the search is aimed at the right category:

{claims}

Today is {searched_at}.
"""

def search_tools(client: LLM | None = None) -> list[dict]:
    """The provider-side search tool attached to the one call.

    Only the Anthropic Messages API accepts this server-side tool. [OI]-compatible
    chat endpoints have no equivalent, so they run the trends pass without live search
    unless the caller supplies --trends-file. Can be suppressed for every provider with
    PRD_AGENT_NO_SEARCH_TOOL=1.
    """
    if os.environ.get("PRD_AGENT_NO_SEARCH_TOOL", "").strip().lower() in ("1", "true", "yes"):
        return []
    if getattr(client, "supports_web_search", True) is False:
        return []
    return [WEB_SEARCH_TOOL]


def is_search_context(text: str) -> bool:
    """Detect whether text contains raw search snippets from a search tool or proxy."""
    if not text or len(text) < 80:
        return False
    lower = text.lower()
    has_url = "http://" in lower or "https://" in lower
    search_indicators = (
        "search result",
        "duckduckgo",
        "web search",
        "results for",
        "snippet",
        "source:",
        "url:",
    )
    if has_url and any(ind in lower for ind in search_indicators):
        return True
    if text.count("http://") + text.count("https://") >= 2:
        return True
    return False


def build_trends_prompt(claims: dict, *, searched_at: str) -> str:
    schema = (
        '{"schema": "prd-agent.trends.v1", '
        '"category": {"competitors": [{"name": "", "url": "", "claim": "", "language": [""]}], '
        '"sophistication_stage": "virgin|crowded|jaded|exhausted", "stage_note": ""}, '
        '"style": {"register": "", "notes": [""]}, '
        '"cultural": [{"moment": "", "url": "", "relevance": ""}], '
        '"human_nightmare": "", '
        '"trending_hype_words": [""], '
        '"unlocked_dream": "", '
        '"false_dogma": "", '
        '"rebellion_belief": "", '
        '"searched_at": ""}'
    )
    return _PROMPT_TEMPLATE.format(
        schema=schema,
        claims=json.dumps(claims, indent=2, ensure_ascii=False),
        searched_at=searched_at,
    )


def analyze(claims: dict, client: LLM, *, searched_at: str | None = None) -> dict:
    """Run the live pass and return a validated trends document."""
    stamp = searched_at or date.today().isoformat()
    trends_prompt = build_trends_prompt(claims, searched_at=stamp)
    raw = client.complete(
        system=TRENDS_SYSTEM,
        prompt=trends_prompt,
        tools=search_tools(client),
    )
    try:
        doc = extract_json(raw)
    except ModelOutputError:
        if is_search_context(raw):
            synthesis_prompt = (
                f"The web search pass returned the following raw search results and market snippets:\n\n"
                f"{raw[:80000]}\n\n"
                f"Using these search results and the artifact claims, generate the trends JSON document matching the required schema:\n\n"
                f"{trends_prompt}"
            )
            synthesized = client.complete(
                system=TRENDS_SYSTEM,
                prompt=synthesis_prompt,
                tools=None,
            )
            doc = extract_json(synthesized)
        else:
            raise
    if not isinstance(doc, dict):
        raise ModelOutputError("the trends reply was not a JSON object")
    doc.setdefault("schema", TRENDS_SCHEMA)
    doc["searched_at"] = stamp
    category = doc.setdefault("category", {})
    category.setdefault("competitors", [])
    category.setdefault("sophistication_stage", "jaded")
    doc.setdefault("style", {"register": "", "notes": []})
    doc.setdefault("cultural", [])
    require_valid(doc, TRENDS_SPEC, "trends.json")
    return doc
