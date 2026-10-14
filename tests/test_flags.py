from __future__ import annotations

from prd_agent import flags


def test_next_flag_id_starts_at_one_and_increments() -> None:
    assert flags.next_flag_id([]) == "N-001"
    assert flags.next_flag_id([{"id": "N-001"}]) == "N-002"
    assert flags.next_flag_id([{"id": "N-001"}, {"id": "N-007"}]) == "N-008"


def test_make_flag_allocates_and_validates_the_need_kind() -> None:
    flag = flags.make_flag([], "proof", "Adoption", "A public adopter list.")
    assert flag == {"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "A public adopter list."}


def test_make_flag_rejects_an_unknown_need() -> None:
    import pytest

    with pytest.raises(flags.StageError):
        flags.make_flag([], "vibes", "x", "y")


def test_merge_flags_dedupes_and_renumbers() -> None:
    left = [{"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "a"}]
    right = [
        {"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "a"},
        {"id": "N-002", "need": "differentiator", "claim": "Distinct from Kiro", "unlock": "b"},
    ]
    merged = flags.merge_flags(left, right)
    assert [item["id"] for item in merged] == ["N-001", "N-002"]
    assert [item["need"] for item in merged] == ["proof", "differentiator"]


def test_render_flags_emits_the_marker_the_footer_uses() -> None:
    rendered = flags.render_flags(
        [{"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "A public adopter list."}]
    )
    assert "- `[NEED: proof]` Adoption." in rendered
    assert "A public adopter list." in rendered
    assert flags.FLAG_PATTERN.findall(rendered) == ["proof"]


def test_render_flags_says_so_when_there_are_none() -> None:
    assert flags.render_flags([]) == "**Open flags.** None. Every claim on this page is pointed at in the artifact."


def test_ask_questions_reads_one_answer_per_flag() -> None:
    asked: list[str] = []
    replies = iter(["we have 40 adopters", ""])

    def fake_input(prompt: str) -> str:
        asked.append(prompt)
        return next(replies)

    answers = flags.ask_questions(
        [
            {"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "a list"},
            {"id": "N-002", "need": "proof", "claim": "Resume test", "unlock": "issue #139"},
        ],
        input_fn=fake_input,
    )
    assert answers == {"N-001": "we have 40 adopters", "N-002": ""}
    assert len(asked) == 2


def test_answers_as_prompt_keeps_the_skipped_ones_visible() -> None:
    text = flags.answers_as_prompt(
        [
            {"id": "N-001", "need": "proof", "claim": "Adoption", "unlock": "a list"},
            {"id": "N-002", "need": "proof", "claim": "Resume test", "unlock": "issue #139"},
        ],
        {"N-001": "40 adopters"},
    )
    assert "N-001" in text and "40 adopters" in text
    assert "N-002" in text and "no answer" in text
