from __future__ import annotations

from pathlib import Path

from prd_agent import checks


def body_of(path: Path) -> str:
    return checks.split_body_footer(path.read_text(encoding="utf-8"))[0]


def rules(report: checks.CheckReport) -> list[str]:
    return [finding.rule for finding in report.findings]


def test_contrast_reveal_is_a_ban() -> None:
    report = checks.check_story("## Hero\n\nIt's not a tool. It's a teammate.\n")
    assert [f.rule for f in report.bans] == ["contrast_reveal"]
    assert report.bans[0].severity == checks.BAN
    assert "not a tool" in report.bans[0].text


def test_contrast_reveal_variants_are_caught() -> None:
    drafts = [
        "## H\n\nMost teams have a list of ideas that never launch. Not because they are bad. Because each one needs a developer.\n",
        "## H\n\nNot just faster reporting, but a better decision.\n",
        "## H\n\nThe question isn't speed. It is trust.\n",
    ]
    for draft in drafts:
        assert checks.check_story(draft).bans, draft


def test_negation_lists_are_a_ban() -> None:
    report = checks.check_story("## H\n\nNo setup call, no templates, no waiting on IT.\n")
    assert "negation_list" in rules(report)
    assert report.bans


def test_a_single_absence_is_fine() -> None:
    report = checks.check_story("## H\n\nInstall it and it is running. No card required.\n")
    assert report.bans == ()


def test_trailing_pile_on_is_a_ban() -> None:
    report = checks.check_story(
        "## H\n\nReports pull from the data you already have, no exports, no spreadsheets.\n"
    )
    assert "trailing_pile_on" in rules(report)


def test_a_trailing_gerund_clause_is_a_ban() -> None:
    report = checks.check_story("## H\n\nIt syncs your calendar automatically, ensuring nothing slips.\n")
    assert "trailing_pile_on" in rules(report)


def test_self_answered_questions_are_a_ban() -> None:
    report = checks.check_story("## H\n\nThe result? Onboarding that takes minutes.\n")
    assert "self_answered_question" in rules(report)


def test_a_reader_question_is_not_a_ban() -> None:
    report = checks.check_story("## H\n\nNeed to share a screenshot? Drop it in the thread.\n")
    assert report.bans == ()


def test_faq_questions_are_not_a_ban() -> None:
    report = checks.check_story("## FAQ\n\n**Does it work with Shopify?** Yes, on every plan.\n")
    assert report.bans == ()


def test_colon_reveals_are_a_ban() -> None:
    report = checks.check_story("## H\n\nThe best part: it learns.\n")
    assert "colon_reveal" in rules(report)


def test_a_colon_before_a_list_is_fine() -> None:
    report = checks.check_story(
        "## H\n\nA fresh session reads four things: what the project is, where it stands, which task is "
        "active, and what the last session proved.\n"
    )
    assert report.bans == ()


def test_a_colon_after_a_full_clause_is_fine() -> None:
    report = checks.check_story(
        "## H\n\nThe long-term test is simple: a project should stay understandable and resumable.\n"
    )
    assert report.bans == ()


def test_banned_vocabulary_and_stock_phrases_are_bans() -> None:
    assert "banned_vocabulary" in rules(checks.check_story("## H\n\nWe delve into the realm of billing.\n"))
    assert "stock_phrase" in rules(checks.check_story("## H\n\nSay goodbye to manual entry.\n"))


def test_hype_punctuation_is_a_ban() -> None:
    assert "hype_punctuation" in rules(checks.check_story("## H\n\nReady to level up?!\n"))


def test_fenced_code_and_tables_are_exempt() -> None:
    draft = (
        "## H\n\n```bash\n# It's not a tool. It's a teammate. No X, no Y, no Z.\n"
        "continuity init --profile software\n```\n\n| Not X | It is Y |\n|---|---|\n"
    )
    assert checks.check_story(draft).bans == ()


def test_the_footer_is_exempt() -> None:
    draft = (
        "## H\n\nInstall it once.\n\n"
        "### Proof and open items\n\n"
        "The result? A page you can audit. No X, no Y. Not because it is bad. Because it is a footer.\n"
    )
    assert checks.check_story(draft).bans == ()
    assert checks.split_body_footer(draft)[1].startswith("### Proof and open items")


def test_line_numbers_point_into_the_body(pcm_story: Path) -> None:
    report = checks.check_story(body_of(pcm_story))
    assert report.sections[0].start_line == 1


def test_the_reference_story_is_clean_after_the_fix(pcm_story: Path) -> None:
    report = checks.check_story(body_of(pcm_story))
    assert report.bans == (), [f"{f.rule} at {f.line}: {f.text}" for f in report.bans]
    assert report.passed() is True


def test_the_hand_run_line_is_still_caught_as_a_finding() -> None:
    """The sentence the hand run carried. Kept as a fixture so the rule cannot silently rot."""
    report = checks.check_story(
        "## H\n\nThe failure has a name and it is not your memory. It is where the memory lives.\n"
    )
    assert [f.rule for f in report.bans] == ["contrast_reveal"]


def test_one_fragment_is_fine_and_two_are_not() -> None:
    one = checks.check_story("## H\n\nSimple.\n\nThis section carries one real sentence with a fact in it.\n")
    assert one.passed() is True
    two = checks.check_story("## H\n\nSimple.\n\nDone.\n")
    assert two.passed() is False
    assert [f.rule for f in two.cap_violations()] == ["fragment"]


def test_a_fragment_needs_to_have_no_verb() -> None:
    report = checks.check_story("## H\n\nYou had all of it.\n")
    assert report.findings == ()


def test_three_lists_are_capped_per_section() -> None:
    report = checks.check_story("## H\n\nFast, secure, and scalable.\n\nSmall, light, and quick.\n")
    assert [f.rule for f in report.cap_violations()] == ["reflexive_three"]


def test_cap_vocabulary_is_reported_per_section() -> None:
    report = checks.check_story(
        "## H\n\nA seamless, robust platform.\n\nAnother seamless paragraph.\n"
    )
    assert [f.rule for f in report.cap_violations()] == ["cap_vocabulary"]


def test_em_dashes_are_capped_in_long_copy_not_banned() -> None:
    report = checks.check_story("## H\n\nOne clause \u2014 and another, with a third \u2014 then a fourth.\n")
    assert report.bans == ()
    assert "em_dash_long" in [f.rule for f in report.caps]


def test_long_sentences_are_reported_but_never_gate() -> None:
    sentence = "This sentence keeps going and going, with clause after clause, comma after comma, and still it does not stop until it has run well past the point where any reader is still with it at all."
    report = checks.check_story(f"## H\n\n{sentence}\n")
    assert "long_sentence" in [f.rule for f in report.reviews]
    assert report.passed() is True


def test_missing_beats_fail_the_gate() -> None:
    report = checks.check_story("# Headline\n\n**Subhead.**\n\nInstall it.\n")
    assert "beat_path" in [f.rule for f in report.bans]


def test_the_reference_story_has_all_three_beats(pcm_story: Path) -> None:
    report = checks.check_story(body_of(pcm_story))
    assert [f.rule for f in report.bans if f.rule.startswith("beat_")] == []


def test_the_summary_states_what_was_and_was_not_checked(pcm_story: Path) -> None:
    report = checks.check_story(body_of(pcm_story))
    summary = report.summary()
    assert "0 hard bans" in summary
    assert "discomfort, vision, path" in summary
    assert "whether the story lands" in report.limitations()


def test_the_limitations_are_honest_about_scope() -> None:
    report = checks.check_story("## H\n\nOne sentence with a fact in it, long enough to count.\n")
    assert "cannot" in report.limitations()
    assert "shape no rule here matches" in report.limitations()

