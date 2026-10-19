"""Derive the spine (discomfort -> vision -> path) and a differentiator that survives the swap test.

The model proposes the positioning. The swap test is run here, in code, and its verdict
overwrites whatever the model said about itself. When no differentiator survives, the stage
flags it and writes no generic copy.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from prd_agent.errors import ModelOutputError
from prd_agent.flags import make_flag
from prd_agent.hype import get_hype_tier
from prd_agent.llm import LLM, extract_json
from prd_agent.schemas import POSITIONING_SCHEMA, POSITIONING_SPEC, require_valid

SWAP_OVERLAP_THRESHOLD = 0.6
STOPWORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "because", "but", "by", "for", "from", "has",
        "have", "in", "into", "is", "it", "its", "no", "not", "of", "on", "or", "that", "the",
        "their", "them", "they", "this", "to", "was", "were", "which", "while", "with", "you",
        "your", "yours", "we", "our", "us", "so", "than", "then", "there", "here", "when", "what",
        "who", "how", "why", "all", "any", "can", "does", "do", "did", "each", "every", "more",
        "most", "other", "some", "such", "only", "just", "also", "out", "up", "own", "same",
    }
)
_WORD = re.compile(r"[a-z][a-z0-9'-]*")

POSITIONING_SYSTEM = (
    "You are a positioning strategist. You derive one spine from the evidence you are given and "
    "you do not write marketing copy. You answer with JSON and nothing else."
)

_PROMPT_TEMPLATE = """\
Derive the positioning for this artifact.

The spine is the Human Action Model: current discomfort, better vision, path to action.
The differentiator is the one line that cannot appear on a named competitor's site unchanged.

Rules:
1. Use the claims. A `verified` claim may be stated plainly. A `claimed` claim may be stated
   only as the artifact's own assertion. An `unknown` may not be stated at all.
2. The `alternative` is what the audience does today instead, named concretely.
3. The `differentiator` names the mechanism, not an adjective. If the mechanism cannot be
   distinguished from what the competitors already say, say so in the swap test note.
4. Hype is uncapped, with one exception: nothing here may contradict what the artifact is.
5. `flags` collects what you could not derive. Each flag names the claim, the kind of need
   (proof, differentiator, mechanism or audience) and the evidence that would unlock it.
6. Story first, feature later. Ground the discomfort in a concrete, relatable human nightmare scene
   (e.g. 2:00 AM panic, frantic alt-tabbing between crashing agent terminals). Ground the vision in
   an unlocked dream scene (e.g. laptop closed at 6 PM, sleeping 8 hours uninterrupted while features
   ship). Provide a sharp, relatable human metaphor. Features and mechanisms are introduced only as
   the heroes that resolve the nightmare.

Answer with exactly this JSON object and no prose around it:

{schema}

Claims:

{claims}

Trends (competitor language, market stage, register):

{trends}

Narrative calibration:

{hype_directive}

{answers}
"""


def content_words(text: str) -> set[str]:
    """The words a line is actually made of, with stopwords and short words removed."""
    return {word for word in _WORD.findall(text.lower()) if len(word) > 2 and word not in STOPWORDS}


@dataclass(frozen=True)
class SwapResult:
    passed: bool
    note: str
    collisions: tuple[str, ...] = ()
    max_overlap: float = 0.0
    closest: str = ""


def swap_test(
    differentiator: str,
    competitors: list[dict],
    *,
    threshold: float = SWAP_OVERLAP_THRESHOLD,
) -> SwapResult:
    """A line fails when one competitor's own language already covers most of it.

    A failure is authoritative. A pass is provisional: lexical overlap is a floor, and the
    story prompt still runs the qualitative swap test from the skill.
    """
    words = content_words(differentiator)
    if not words:
        return SwapResult(False, "The differentiator is empty, so it cannot survive the swap test.")
    closest = ""
    max_overlap = 0.0
    collisions: list[str] = []
    for competitor in competitors:
        name = str(competitor.get("name", "unnamed"))
        theirs = content_words(" ".join(str(item) for item in competitor.get("language", [])))
        overlap = len(words & theirs) / len(words)
        if overlap > max_overlap:
            closest, max_overlap = name, overlap
        if overlap >= threshold:
            collisions.append(name)
    if collisions:
        note = (
            f"{', '.join(collisions)} already use {max_overlap:.0%} of this line's words, so it would "
            f"work unchanged on their page. Rewrite it from the mechanism this artifact actually has."
        )
        return SwapResult(False, note, tuple(collisions), max_overlap, closest)
    note = (
        f"No named competitor's language covers this line (closest: {closest or 'none'} at "
        f"{max_overlap:.0%} against a {threshold:.0%} threshold)."
    )
    return SwapResult(True, note, (), max_overlap, closest)


def build_positioning_prompt(
    claims: dict,
    trends: dict,
    *,
    answers: str | None = None,
    hype: str | None = None,
) -> str:
    tier = get_hype_tier(hype)
    schema = (
        '{"schema": "prd-agent.positioning.v1", '
        '"audience": {"who": "", "situation": "", "trigger": ""}, '
        '"discomfort": "", "vision": "", "path": "", "alternative": "", "differentiator": "", '
        '"nightmare_scene": "", "dream_scene": "", "metaphor": "", '
        '"swap_test": {"passed": false, "note": ""}, '
        '"flags": [{"id": "N-001", "need": "proof", "claim": "", "unlock": ""}]}'
    )
    return _PROMPT_TEMPLATE.format(
        schema=schema,
        claims=json.dumps(claims, indent=2, ensure_ascii=False),
        trends=json.dumps(trends, indent=2, ensure_ascii=False),
        answers=answers or "No owner answers were supplied for this run.",
        hype_directive=tier.directive,
    )


def positioning(
    claims: dict,
    trends: dict,
    llm: LLM,
    *,
    answers: str | None = None,
    hype: str | None = None,
) -> dict:
    tier = get_hype_tier(hype)
    raw = llm.complete(
        system=POSITIONING_SYSTEM,
        prompt=build_positioning_prompt(claims, trends, answers=answers, hype=tier.level),
    )
    doc = extract_json(raw)
    if not isinstance(doc, dict):
        raise ModelOutputError("the positioning reply was not a JSON object")
    doc.setdefault("schema", POSITIONING_SCHEMA)
    doc.setdefault("flags", [])
    doc["hype_level"] = tier.level
    result = swap_test(str(doc.get("differentiator", "")), list(trends.get("category", {}).get("competitors", [])))
    doc["swap_test"] = {"passed": result.passed, "note": result.note}
    if not result.passed:
        doc["flags"] = list(doc["flags"]) + [
            make_flag(
                doc["flags"],
                "differentiator",
                f"Distinct from {', '.join(result.collisions) or 'the named competitors'}",
                "A mechanism claim that the named competitors cannot make. "
                + (f"Closest collision: {result.closest} at {result.max_overlap:.0%} word overlap."
                   if result.collisions else ""),
            )
        ]
    require_valid(doc, POSITIONING_SPEC, "positioning.json")
    return doc
