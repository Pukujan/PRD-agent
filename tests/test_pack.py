from __future__ import annotations

import json
from pathlib import Path
import pytest

from prd_agent.hype import DEFAULT_HYPE_LEVEL
from prd_agent.llm import LLM
from prd_agent.pack import (
    PackResult,
    assert_no_em_dashes,
    generate_copy_deck,
    generate_launch_thread,
    generate_pack,
    generate_pitch_deck,
    generate_show_hn,
    purge_em_dashes,
)
from prd_agent.persona import DEFAULT_PERSONA


class FakeLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict] = []

    def complete(self, *, system: str, prompt: str) -> str:
        self.calls.append({"system": system, "prompt": prompt})
        if not self.responses:
            raise RuntimeError("no more canned responses")
        return self.responses.pop(0)


def test_purge_em_dashes() -> None:
    text_with_dashes = "Autonomous systems — built for speed – and zero compromise -- forever."
    cleaned = purge_em_dashes(text_with_dashes)
    assert "—" not in cleaned
    assert "–" not in cleaned
    assert " -- " not in cleaned
    assert_no_em_dashes(cleaned)


def test_assert_no_em_dashes_fails_on_dashes() -> None:
    with pytest.raises(ValueError):
        assert_no_em_dashes("This has an em-dash — right here.")
    with pytest.raises(ValueError):
        assert_no_em_dashes("This has a double-hyphen -- right here.")


def test_generate_copy_deck() -> None:
    raw_copy = json.dumps({
        "headline": "Replace an 8-person dev team with one daemon",
        "subheadline": "The autonomous execution engine for solo builders.",
        "superpowers": [
            {
                "title": "Immortal Recall",
                "description": "Never lose context across agent restarts.",
                "nightmare_contrast": "Before: 2 hours rebuilding lost context. Now: 0 ms.",
            }
        ],
        "before_after_table": [
            {"legacy_way": "Manual test runs", "superpower_way": "Deterministic verification"}
        ],
        "social_proof_hooks": ["Shipped 4 features in one night without touching git."],
        "cta": {
            "primary": "Deploy Now",
            "secondary": "Read the Spec",
            "guarantee": "Zero telemetry, 100% open source.",
        },
    })
    llm = FakeLLM([raw_copy])
    deck = generate_copy_deck(
        claims={"claims": []},
        trends={},
        positioning={"vision": "Speed"},
        story="Story body",
        llm=llm,
        hype="1000",
        persona="solopreneur",
    )
    assert deck["headline"] == "Replace an 8-person dev team with one daemon"
    assert len(deck["superpowers"]) == 1
    assert deck["superpowers"][0]["title"] == "Immortal Recall"
    assert "1000" in llm.calls[0]["prompt"]
    assert "SOLOPRENEUR" in llm.calls[0]["prompt"]


def test_generate_launch_thread() -> None:
    raw_thread = """\
1/7 Most developer tools are lying to you about leverage.
2/7 It starts at 3:00 AM when your agents collide.
3/7 You spend 4 hours cleaning up hallucinated imports.
4/7 We spent 6 months building an architectural killswitch.
5/7 Here is how it works under the hood.
6/7 Benchmarks: 400 microseconds, zero network dependencies.
7/7 Try it today. Link below.
"""
    llm = FakeLLM([raw_thread])
    thread = generate_launch_thread(
        claims={"claims": []},
        trends={},
        positioning={"vision": "Speed"},
        story="Story body",
        llm=llm,
        hype="1000",
        persona="solopreneur",
    )
    assert "1/7" in thread
    assert "7/7" in thread
    assert_no_em_dashes(thread)


def test_generate_show_hn() -> None:
    raw_hn = """\
# Show HN: Daemon – Autonomous code verification that never sleeps

Hey HN, I got tired of agents hallucinating non-existent modules.

### Why I built this
Every time an agent ran overnight, I woke up to broken imports.

### What it actually does
Deterministic AST verification in pure Python with zero dependencies.
"""
    llm = FakeLLM([raw_hn])
    hn = generate_show_hn(
        claims={"claims": []},
        trends={},
        positioning={"vision": "Speed"},
        story="Story body",
        llm=llm,
        hype="1000",
        persona="solopreneur",
    )
    assert "Show HN:" in hn
    assert_no_em_dashes(hn)


def test_generate_pitch_deck() -> None:
    raw_deck = """\
# Slide 1: The Category Shift
The era of seat-based developer tooling is dead.

# Slide 2: The Bleeding Wound
$40,000 lost per month in API token incinerators.

# Slide 3: The Broken Alternatives
Incumbents wrap APIs with pretty UIs and charge 10x.

# Slide 4: The Breakthrough
A single compiled binary with local context isolation.

# Slide 5: The Superpowers
Immortal recall and instant killswitch.

# Slide 6: The Secret Weapon
Deterministic cache invalidation without network queries.

# Slide 7: Unfair Economics
Zero per-seat tax. Runs locally on existing machines.

# Slide 8: Traction & Validation
40 active teams shipping production code daily.

# Slide 9: The Impossible Future
The autonomous software studio where one engineer does the work of 100.

# Slide 10: The Ask
Join the private alpha or run the open source binary today.
"""
    llm = FakeLLM([raw_deck])
    deck = generate_pitch_deck(
        claims={"claims": []},
        trends={},
        positioning={"vision": "Speed"},
        story="Story body",
        llm=llm,
        hype="1000",
        persona="solopreneur",
    )
    assert "Slide 1:" in deck
    assert "Slide 10:" in deck
    assert_no_em_dashes(deck)


def test_generate_pack_writes_all_files(tmp_path: Path) -> None:
    canned_copy = json.dumps({
        "headline": "Replace an 8-person dev team with one daemon",
        "subheadline": "The autonomous execution engine for solo builders.",
        "superpowers": [
            {
                "title": "Immortal Recall",
                "description": "Never lose context across agent restarts.",
                "nightmare_contrast": "Before: 2 hours rebuilding lost context. Now: 0 ms.",
            }
        ],
        "before_after_table": [
            {"legacy_way": "Manual test runs", "superpower_way": "Deterministic verification"}
        ],
        "social_proof_hooks": ["Shipped 4 features in one night without touching git."],
        "cta": {
            "primary": "Deploy Now",
            "secondary": "Read the Spec",
            "guarantee": "Zero telemetry, 100% open source.",
        },
    })
    canned_thread = "1/2 Hook\n\n2/2 Link"
    canned_hn = "# Show HN: Daemon – Fast code\n\nOrigin story"
    canned_deck = "# Slide 1: Problem\n\n# Slide 2: Solution"

    llm = FakeLLM([canned_copy, canned_thread, canned_hn, canned_deck])

    run_dir = tmp_path / "runs" / "target"
    run_dir.mkdir(parents=True)

    result = generate_pack(
        run_dir=run_dir,
        claims={"claims": []},
        trends={},
        positioning={"vision": "Speed"},
        story="Story body",
        llm=llm,
        hype="1000",
        persona="solopreneur",
    )

    assert isinstance(result, PackResult)
    assert result.pack_dir == run_dir / "pack"
    assert result.copy_json_path.is_file()
    assert result.launch_thread_path.is_file()
    assert result.show_hn_path.is_file()
    assert result.pitch_deck_path.is_file()

    # Verify content
    loaded_copy = json.loads(result.copy_json_path.read_text(encoding="utf-8"))
    assert loaded_copy["headline"] == "Replace an 8-person dev team with one daemon"
    assert_no_em_dashes(result.launch_thread_path.read_text(encoding="utf-8"))
    assert_no_em_dashes(result.show_hn_path.read_text(encoding="utf-8"))
    assert_no_em_dashes(result.pitch_deck_path.read_text(encoding="utf-8"))
