# tests/test_story.py
from __future__ import annotations

import json
from pathlib import Path

import pytest

from prd_agent import story
from prd_agent.checks import check_story, split_body_footer
from prd_agent.errors import StoryGateError
from prd_agent.llm import FakeLLM

GOOD_BODY = """\
# Your project's memory is your Git repository

**Plain files next to the code they describe, checked by a validator.**

Install from source and initialize the project you would hate to lose.

## The project stops making sense when the chat ends

You open a project after two weeks away and the first hour goes into working out its state. Which experiment finished. What the number in last month's report measured.

## Pick it up cold

A fresh session opens the repo and reads four things: what the project is, where it stands, which task is active, and what the last session proved. Then it works.

## A session's whole life, in four steps

1. Read the state.
2. Do one bounded task.
3. Write the evidence.
4. Publish it.

The next session starts at step one. It does not need the old conversation.
"""

BAD_BODY = GOOD_BODY + "\n\n## Why teams pick it\n\nIt's not a tool. It's a teammate.\n"

REWRITTEN_BODY = GOOD_BODY + "\n\n## Why teams pick it\n\nIt is a teammate for the project, one that reads the repository.\n"

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def test_the_story_prompt_carries_the_vendored_skill_and_the_facts(pcm_run: Path) -> None:
    claims, trends = load(pcm_run / "claims.json"), load(pcm_run / "trends.json")
    positioning = load(pcm_run / "positioning.json")
    prompt = story.build_story_prompt(positioning=positioning, claims=claims, trends=trends)
    assert "The Self-Check" in prompt          # from the vendored SKILL.md
    assert "The contrast reveal" in prompt     # from the vendored ai-tells.md
    assert "The Human Action Model" in prompt  # from the vendored copy-frameworks.md
    assert positioning["differentiator"][:40] in prompt
    assert "never invent" in prompt.lower()

def test_the_story_prompt_forbids_the_footer_and_the_flag_markers(pcm_run: Path) -> None:
    prompt = story.build_story_prompt(
        positioning=load(pcm_run / "positioning.json"),
        claims=load(pcm_run / "claims.json"),
        trends=load(pcm_run / "trends.json"),
    )
    assert "proof and open items" in prompt.lower()
    assert "[NEED:" in prompt
    assert "do not write" in prompt.lower()

def test_the_story_prompt_injects_exemplars_when_they_are_supplied(pcm_run: Path) -> None:
    prompt = story.build_story_prompt(
        positioning=load(pcm_run / "positioning.json"),
        claims=load(pcm_run / "claims.json"),
        trends=load(pcm_run / "trends.json"),
        exemplars=[{"story": "An earlier page about a different artifact."}],
    )
    assert "An earlier page about a different artifact." in prompt

def test_the_first_ever_run_gets_a_template_prompt_with_no_exemplars(pcm_run: Path) -> None:
    # Spec §5: run one has nothing to retrieve from, so the prompt must say so
    # rather than silently showing an empty "worked examples" heading.
    prompt = story.build_story_prompt(
        positioning=load(pcm_run / "positioning.json"),
        claims=load(pcm_run / "claims.json"),
        trends=load(pcm_run / "trends.json"),
    )
    assert "No worked examples are available yet" in prompt
    assert "earlier story" not in prompt

def test_clean_body_strips_a_fenced_wrapper() -> None:
    body, harvested = story.clean_body("```markdown\n# Headline\n\ntext\n```")
    assert body == "# Headline\n\ntext"
    assert harvested == []

def test_clean_body_harvests_a_model_flag_instead_of_failing() -> None:
    body, harvested = story.clean_body("# Headline\n\nWe ship it today. [NEED: proof]\n")
    assert "[NEED:" not in body
    assert harvested[0]["need"] == "proof"

def test_clean_body_ignores_an_unknown_need_kind() -> None:
    body, harvested = story.clean_body("# Headline\n\nWe ship it. [NEED: vibes]\n")
    assert "[NEED:" not in body
    assert harvested == []

def test_the_footer_is_built_from_the_json_not_from_the_model(pcm_run: Path) -> None:
    claims, positioning = load(pcm_run / "claims.json"), load(pcm_run / "positioning.json")
    trends = load(pcm_run / "trends.json")
    report = check_story(GOOD_BODY)
    footer = story.build_footer(claims=claims, positioning=positioning, trends=trends, report=report)
    assert footer.startswith("### Proof and open items")
    assert "| Claim on this page | Source | Status |" in footer
    assert "C-001" not in footer            # the table carries the claim text, not the id
    assert "templates/v1/" in footer        # the evidence from claims.json
    assert "**unknown**" in footer          # an unknown is recorded as unknown
    assert "`[NEED: proof]`" in footer      # every open flag is rendered
    assert "[NEED: differentiator]" in footer
    assert "jaded" in footer                # the market stage is named
    assert "**Self-check.**" in footer
    assert "whether the story lands" in footer

def test_the_footer_renders_the_no_flags_line_when_there_are_none(pcm_run: Path) -> None:
    positioning = load(pcm_run / "positioning.json")
    positioning["flags"] = []
    footer = story.build_footer(
        claims=load(pcm_run / "claims.json"),
        positioning=positioning,
        trends=load(pcm_run / "trends.json"),
        report=check_story(GOOD_BODY),
    )
    assert "Every claim on this page is pointed at in the artifact." in footer

def test_extra_flags_are_merged_into_the_footer(pcm_run: Path) -> None:
    footer = story.build_footer(
        claims=load(pcm_run / "claims.json"),
        positioning=load(pcm_run / "positioning.json"),
        trends=load(pcm_run / "trends.json"),
        report=check_story(GOOD_BODY),
        extra_flags=[{"id": "N-001", "need": "proof", "claim": "Raised by the draft", "unlock": "Evidence."}],
    )
    assert "Raised by the draft" in footer
    assert footer.count("N-001") >= 1

def test_assemble_story_puts_the_footer_behind_the_pitch() -> None:
    page = story.assemble_story("# H\n\nbody\n", "### Proof and open items\n\ntable\n")
    body, footer = split_body_footer(page)
    assert body == "# H\n\nbody"
    assert footer.startswith("### Proof and open items")
    assert page.count("### Proof and open items") == 1

def test_a_clean_first_draft_is_accepted_without_a_second_call(pcm_run: Path) -> None:
    fake = FakeLLM(GOOD_BODY)
    page, report = story.story(
        claims=load(pcm_run / "claims.json"),
        positioning=load(pcm_run / "positioning.json"),
        trends=load(pcm_run / "trends.json"),
        llm=fake,
    )
    assert len(fake.calls) == 1
    assert report.passed() is True
    assert page.endswith("\n")
    assert check_story(split_body_footer(page)[0]).passed() is True

def test_a_banned_draft_is_rewritten_and_the_rewrite_prompt_names_the_finding(pcm_run: Path) -> None:
    fake = FakeLLM([BAD_BODY, REWRITTEN_BODY])
    page, report = story.story(
        claims=load(pcm_run / "claims.json"),
        positioning=load(pcm_run / "positioning.json"),
        trends=load(pcm_run / "trends.json"),
        llm=fake,
    )
    assert len(fake.calls) == 2
    assert report.passed() is True
    assert "contrast_reveal" in str(fake.calls[1]["prompt"])
    assert "It's not a tool" in str(fake.calls[1]["prompt"])
    assert "It is a teammate for the project" in page

def test_a_draft_still_banned_after_the_last_rewrite_fails_the_run(pcm_run: Path) -> None:
    fake = FakeLLM([BAD_BODY, BAD_BODY, BAD_BODY])
    with pytest.raises(StoryGateError) as error:
        story.story(
            claims=load(pcm_run / "claims.json"),
            positioning=load(pcm_run / "positioning.json"),
            trends=load(pcm_run / "trends.json"),
            llm=fake,
        )
    assert "contrast_reveal" in str(error.value)
    assert "3 drafts" in str(error.value)
    assert len(fake.calls) == 3

def test_max_rewrites_zero_allows_one_draft_only(pcm_run: Path) -> None:
    fake = FakeLLM([BAD_BODY])
    with pytest.raises(StoryGateError):
        story.story(
            claims=load(pcm_run / "claims.json"),
            positioning=load(pcm_run / "positioning.json"),
            trends=load(pcm_run / "trends.json"),
            llm=fake,
            max_rewrites=0,
        )
    assert len(fake.calls) == 1

def test_the_rewrite_prompt_repeats_the_facts_not_just_the_findings(pcm_run: Path) -> None:
    prompt = story.build_rewrite_prompt(
        body=BAD_BODY,
        report=check_story(BAD_BODY),
        positioning=load(pcm_run / "positioning.json"),
        claims=load(pcm_run / "claims.json"),
    )
    assert "contrast_reveal" in prompt
    assert "It's not a tool" in prompt
    assert "Rewrite from the facts" in prompt
    assert "a validator checks it" in prompt  # the differentiator, restated for the rewrite
