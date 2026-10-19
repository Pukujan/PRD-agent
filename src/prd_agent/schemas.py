"""Structural validation for the JSON the pipeline passes between stages.

The field specs below are the single source of truth for the contract. There is no JSON
Schema file and no jsonschema dependency: a second copy of the contract would be a second
thing to keep in sync.
"""

from __future__ import annotations

from typing import Any

from prd_agent.errors import SchemaError

CLAIMS_SCHEMA = "prd-agent.claims.v1"
TRENDS_SCHEMA = "prd-agent.trends.v1"
POSITIONING_SCHEMA = "prd-agent.positioning.v1"
CLAIM_STATUSES = ("verified", "claimed", "unknown")
SOPHISTICATION_STAGES = ("virgin", "crowded", "jaded", "exhausted")

CLAIMS_SPEC: dict[str, Any] = {
    "schema": f"const:{CLAIMS_SCHEMA}",
    "artifact": {"name": "str", "path": "str", "commit": "str", "read_at": "str"},
    "claims": (
        "list",
        {
            "id": "str",
            "text": "str",
            "status": "enum:" + "|".join(CLAIM_STATUSES),
            "evidence": "str",
            "note": "str",
        },
    ),
    "unknowns": "list[str]",
}

TRENDS_SPEC: dict[str, Any] = {
    "schema": f"const:{TRENDS_SCHEMA}",
    "category": {
        "competitors": (
            "list",
            {"name": "str", "url": "str", "claim": "str", "language": "list[str]"},
        ),
        "sophistication_stage": "enum:" + "|".join(SOPHISTICATION_STAGES),
        "stage_note": "str",
    },
    "style": {"register": "str", "notes": "list[str]"},
    "cultural": ("list", {"moment": "str", "url": "str", "relevance": "str"}),
    "human_nightmare": "opt:str",
    "trending_hype_words": "opt:list[str]",
    "unlocked_dream": "opt:str",
    "searched_at": "str",
}

POSITIONING_SPEC: dict[str, Any] = {
    "schema": f"const:{POSITIONING_SCHEMA}",
    "audience": {"who": "str", "situation": "str", "trigger": "str"},
    "discomfort": "str",
    "vision": "str",
    "path": "str",
    "alternative": "str",
    "differentiator": "str",
    "nightmare_scene": "opt:str",
    "dream_scene": "opt:str",
    "metaphor": "opt:str",
    "swap_test": {"passed": "bool", "note": "str"},
    "flags": ("list", {"id": "str", "need": "str", "claim": "str", "unlock": "str"}),
}


def validate(doc: Any, spec: Any, path: str = "$") -> list[str]:
    """Return a list of human-readable problems; an empty list means valid."""
    if isinstance(spec, tuple):
        _, item_spec = spec
        if not isinstance(doc, list):
            return [f"{path}: expected a list, got {type(doc).__name__}"]
        problems: list[str] = []
        for index, item in enumerate(doc):
            problems.extend(validate(item, item_spec, f"{path}[{index}]"))
        return problems

    if isinstance(spec, dict):
        if not isinstance(doc, dict):
            return [f"{path}: expected an object, got {type(doc).__name__}"]
        problems = []
        for key, sub_spec in spec.items():
            is_optional = isinstance(sub_spec, str) and sub_spec.startswith("opt:")
            actual_spec = sub_spec[4:] if is_optional else sub_spec
            if key not in doc:
                if not is_optional:
                    problems.append(f"{path}.{key}: missing")
            else:
                problems.extend(validate(doc[key], actual_spec, f"{path}.{key}"))
        for key in doc:
            if key not in spec:
                problems.append(f"{path}.{key}: unexpected field")
        return problems

    if spec.startswith("const:"):
        expected = spec.split(":", 1)[1]
        return [] if doc == expected else [f"{path}: expected {expected!r}, got {doc!r}"]

    if spec.startswith("enum:"):
        allowed = spec.split(":", 1)[1].split("|")
        return [] if doc in allowed else [f"{path}: expected one of {allowed}, got {doc!r}"]

    if spec == "str":
        return [] if isinstance(doc, str) else [f"{path}: expected a string"]

    if spec == "bool":
        return [] if isinstance(doc, bool) else [f"{path}: expected a boolean, got {doc!r}"]

    if spec == "list[str]":
        ok = isinstance(doc, list) and all(isinstance(item, str) for item in doc)
        return [] if ok else [f"{path}: expected a list of strings"]

    return [f"{path}: unknown spec {spec!r}"]


def validate_claims(doc: Any) -> list[str]:
    return validate(doc, CLAIMS_SPEC)


def validate_trends(doc: Any) -> list[str]:
    return validate(doc, TRENDS_SPEC)


def validate_positioning(doc: Any) -> list[str]:
    return validate(doc, POSITIONING_SPEC)


def require_valid(doc: Any, spec: Any, name: str) -> None:
    problems = validate(doc, spec)
    if problems:
        raise SchemaError(f"{name} failed validation: " + "; ".join(problems[:10]))
