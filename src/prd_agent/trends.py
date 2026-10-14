"""The live web pass: category, style and cultural trends, plus the market sophistication stage.

Version one ships no scraped corpus; the corpus seam is documented in docs/CORPUS_SEAM.md and not
built. The search happens inside the one model call, through the provider's own web search tool,
so this module adds no dependency, no second credential and no HTML parsing.
"""

from __future__ import annotations

import json
from datetime import date

from prd_agent import llm
from prd_agent.errors import ModelOutputError
from prd_agent.llm import LLM, WEB_SEARCH_TOOL, extract_json
from prd_agent.schemas import SOPHISTICATION_STAGES, TRENDS_SCHEMA, TRENDS_SPEC, require_valid

STAGE_BRIEF = {
    "virgin": "No one has heard the claim. State it plainly and be the first to name the problem.",
    "crowded": "Everyone makes the same claim. Make a bigger claim and back it with the mechanism.",
    "jaded": "The claim has gone flat and abstract. Lead with a new mechanism, not a louder promise.",
    "exhausted": "The category has burned the reader. Get identification first, then the mechanism.",
}

TRENDS_SYSTEM = (
    "You are a market analyst. You search the live web and report what competitors claim, what "
    "register of copy is landing, and which conversation is worth attaching to. You report what "
    "you find with URLs. You answer with JSON and nothing else."
)

_PROMPT_TEMPLATE = """\
Search the live web and report the market this product is entering.

Extract all three trend kinds:

- Category. What competing and adjacent products claim right now, with the language they use,
  quoted from the page. This is what makes a swap test runnable, so the `language` list must be
  the competitor's own words, not a paraphrase.
- Style. What register of copy is currently landing, so the story reads current rather than dated.
- Cultural. The conversation worth attaching to, with the URL and why it matters here.

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

def search_tools() -> list[dict]:
    """The provider-side search tool attached to the one call."""
    return [WEB_SEARCH_TOOL]

def build_trends_prompt(claims: dict, *, searched_at: str) -> str:
    schema = (
        '{"schema": "prd-agent.trends.v1", '
        '"category": {"competitors": [{"name": "", "url": "", "claim": "", "language": [""]}], '
        '"sophistication_stage": "virgin|crowded|jaded|exhausted", "stage_note": ""}, '
        '"style": {"register": "", "notes": [""]}, '
        '"cultural": [{"moment": "", "url": "", "relevance": ""}], '
        '"searched_at": ""}'
    )
    return _PROMPT_TEMPLATE.format(
        schema=schema,
        claims=json.dumps(claims, indent=2, ensure_ascii=False),
        searched_at=searched_at,
    )

def analyze(claims: dict, llm: LLM, *, searched_at: str | None = None) -> dict:
    """Run the live pass and return a validated trends document."""
    stamp = searched_at or date.today().isoformat()
    raw = llm.complete(
        system=TRENDS_SYSTEM,
        prompt=build_trends_prompt(claims, searched_at=stamp),
        tools=search_tools(),
    )
    doc = extract_json(raw)
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
