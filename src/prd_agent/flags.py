"""The `[NEED: ...]` flags. These are the storyboard: there is no separate question step.

A flag carries the claim it blocks, the kind of need, and the exact evidence that would
unlock it. Human mode puts them to the owner; autonomous mode ships them in the footer.
"""

from __future__ import annotations

import re
from typing import Callable

from prd_agent.errors import StageError

NEED_KINDS = ("proof", "differentiator", "mechanism", "audience")
FLAG_PATTERN = re.compile(r"\[NEED: ([a-z-]+)\]")
_ID_PATTERN = re.compile(r"^(?P<prefix>[A-Z])-(?P<number>\d+)$")
NO_FLAGS_LINE = "**Open flags.** None. Every claim on this page is pointed at in the artifact."


def next_flag_id(existing: list[dict], prefix: str = "N") -> str:
    highest = 0
    for flag in existing:
        match = _ID_PATTERN.match(str(flag.get("id", "")))
        if match and match.group("prefix") == prefix:
            highest = max(highest, int(match.group("number")))
    return f"{prefix}-{highest + 1:03d}"


def make_flag(existing: list[dict], need: str, claim: str, unlock: str, *, prefix: str = "N") -> dict:
    if need not in NEED_KINDS:
        raise StageError(f"unknown need kind {need!r}; expected one of {NEED_KINDS}")
    return {"id": next_flag_id(existing, prefix), "need": need, "claim": claim, "unlock": unlock}


def merge_flags(*groups: list[dict]) -> list[dict]:
    """Concatenate flag groups, drop exact duplicates, and renumber in order."""
    seen: set[tuple[str, str]] = set()
    merged: list[dict] = []
    for group in groups:
        for flag in group or []:
            key = (str(flag.get("need", "")), str(flag.get("claim", "")))
            if key in seen:
                continue
            seen.add(key)
            merged.append(
                {
                    "id": "",
                    "need": flag.get("need", ""),
                    "claim": flag.get("claim", ""),
                    "unlock": flag.get("unlock", ""),
                }
            )
    for index, flag in enumerate(merged, start=1):
        flag["id"] = f"N-{index:03d}"
    return merged


def render_flags(flags: list[dict]) -> str:
    if not flags:
        return NO_FLAGS_LINE
    lines = ["**Open flags.** Each one names the evidence that would let the page go harder.", ""]
    for flag in flags:
        lines.append(f"- `[NEED: {flag['need']}]` {flag['claim']}. {flag['unlock']}")
    return "\n".join(lines)


def ask_questions(
    flags: list[dict],
    *,
    input_fn: Callable[[str], str] = input,
) -> dict[str, str]:
    """Put each flag to the owner and collect the answer that resolves it."""
    answers: dict[str, str] = {}
    for flag in flags:
        prompt = (
            f"\n[{flag['id']}] {flag['need']}: {flag['claim']}\n"
            f"  What would settle it: {flag['unlock']}\n"
            f"  Your answer (leave empty to ship it as an open flag): "
        )
        answers[str(flag["id"])] = input_fn(prompt).strip()
    return answers


def answers_as_prompt(flags: list[dict], answers: dict[str, str]) -> str:
    """The owner's answers, with the skipped flags kept visible, for the revise call."""
    lines = ["The owner answered some open questions. Use what they gave you."]
    for flag in flags:
        answer = answers.get(str(flag["id"]), "").strip()
        if answer:
            lines.append(f"- {flag['id']} ({flag['need']}, {flag['claim']}): {answer}")
        else:
            lines.append(f"- {flag['id']} ({flag['need']}, {flag['claim']}): no answer, keep it as an open flag")
    return "\n".join(lines)
