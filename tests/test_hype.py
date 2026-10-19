"""Tests for the Hype-to-Honesty Dial and calibration tiers."""

from prd_agent.hype import (
    DEFAULT_HYPE_LEVEL,
    TIERS,
    ask_hype_level,
    get_hype_tier,
    normalize_hype_level,
)


def test_default_hype_level_is_1000():
    assert DEFAULT_HYPE_LEVEL == "1000"
    tier = get_hype_tier(None)
    assert tier.level == "1000"
    assert "ELECTRIC GOD-MODE" in tier.directive
    assert "One-Person Unicorn" in tier.directive

def test_normalization_handles_aliases_and_numbers():
    assert normalize_hype_level("1000") == "1000"
    assert normalize_hype_level(1000) == "1000"
    assert normalize_hype_level("electric") == "1000"
    assert normalize_hype_level("1") == "1000"

    assert normalize_hype_level("750") == "750"
    assert normalize_hype_level(750) == "750"
    assert normalize_hype_level("venture") == "750"
    assert normalize_hype_level("2") == "750"

    assert normalize_hype_level("500") == "500"
    assert normalize_hype_level(500) == "500"
    assert normalize_hype_level("balanced") == "500"
    assert normalize_hype_level("3") == "500"

    assert normalize_hype_level("250") == "250"
    assert normalize_hype_level(250) == "250"
    assert normalize_hype_level("truth") == "250"
    assert normalize_hype_level("pure") == "250"
    assert normalize_hype_level("4") == "250"

def test_all_four_tiers_have_distinct_directives():
    assert len(TIERS) == 4
    directives = [tier.directive for tier in TIERS.values()]
    assert len(set(directives)) == 4

    assert "PURE TECHNICAL TRUTH" in TIERS["250"].directive
    assert "BALANCED AUTHORITY" in TIERS["500"].directive
    assert "VENTURE HYPE" in TIERS["750"].directive
    assert "ELECTRIC GOD-MODE" in TIERS["1000"].directive

def test_ask_hype_level_uses_input_and_falls_back_to_default():
    # Empty string input defaults to Level 1000
    assert ask_hype_level(input_fn=lambda _: "") == "1000"

    # Selecting option 2 yields Level 750
    assert ask_hype_level(input_fn=lambda _: "2") == "750"

    # Direct name input works
    assert ask_hype_level(input_fn=lambda _: "truth") == "250"
