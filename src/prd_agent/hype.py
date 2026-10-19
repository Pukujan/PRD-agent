"""The Hype-to-Honesty Dial: 4-tier calibration between electric god-mode and pure truth.

Level 1000: Electric God-Mode (Flagship / Kinetic, loud, solo unicorn, 100x leverage)
Level 750:  High-Converting Venture Hype (2:00 AM founder nightmare, unlocked dream)
Level 500:  Balanced Authority (Dignified strength, concrete proof, zero buzzwords)
Level 250:  Pure Technical Truth (Clinical, understated, empirical rigor, data first)
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class HypeTier:
    level: str
    name: str
    summary: str
    directive: str


TIERS: dict[str, HypeTier] = {
    "1000": HypeTier(
        level="1000",
        name="Electric God-Mode",
        summary="Kinetic, loud, solo unicorn, 100x leverage, unstoppable future",
        directive=(
            "HYPE LEVEL 1000 (ELECTRIC GOD-MODE): Maximum kinetic energy, loud optimism, and "
            "unstoppable forward momentum. Sell the dream of the One-Person Unicorn, 100x leverage, "
            "and solo operators out-shipping 50-person legacy teams. Attack corporate sludge and "
            "administrative drag with relentless velocity. Paint the flying-car-level future as already "
            "here. Zero timid qualifiers. Zero apology. Pure kinetic power grounded in the artifact's "
            "true capability."
        ),
    ),
    "750": HypeTier(
        level="750",
        name="High-Converting Venture Hype",
        summary="2:00 AM founder nightmare, unlocked dream, aggressive contrast",
        directive=(
            "HYPE LEVEL 750 (VENTURE HYPE): Story-first, sharp emotional contrast. Attack the visceral "
            "founder nightmare (e.g. 2:00 AM panic, chaotic tools, feeling like an unpaid babysitter). "
            "Contrast against the unlocked dream. Name the competitor category flaws directly. High "
            "persuasion and punchy conversion prose without hyperbole."
        ),
    ),
    "500": HypeTier(
        level="500",
        name="Balanced Authority",
        summary="Dignified strength, concrete proof, zero buzzwords",
        directive=(
            "HYPE LEVEL 500 (BALANCED AUTHORITY): Confident, dignified engineering reality. Direct "
            "problem and solution. Grounded in concrete evidence, verified claims, and architectural "
            "clarity. Zero buzzwords, zero marketing fluff, but absolute structural confidence."
        ),
    ),
    "250": HypeTier(
        level="250",
        name="Pure Technical Truth",
        summary="Clinical, understated, empirical rigor, data first",
        directive=(
            "HYPE LEVEL 250 (PURE TECHNICAL TRUTH): Clinical, understated, empirical rigor. Zero "
            "marketing adjectives. Let the code, benchmarks, system boundaries, and numbers speak for "
            "themselves. Written for security reviewers, systems programmers, and technical auditors "
            "who distrust all hype."
        ),
    ),
}

DEFAULT_HYPE_LEVEL = "1000"

_ALIASES: dict[str, str] = {
    "1": "1000",
    "1000": "1000",
    "electric": "1000",
    "god-mode": "1000",
    "2": "750",
    "750": "750",
    "venture": "750",
    "3": "500",
    "500": "500",
    "balanced": "500",
    "4": "250",
    "250": "250",
    "truth": "250",
    "pure": "250",
    "technical": "250",
}


def normalize_hype_level(raw: str | int | None) -> str:
    """Normalize user input or CLI argument into one of the canonical 4 levels."""
    if raw is None:
        return DEFAULT_HYPE_LEVEL
    val = str(raw).strip().lower()
    if not val:
        return DEFAULT_HYPE_LEVEL
    return _ALIASES.get(val, DEFAULT_HYPE_LEVEL)


def get_hype_tier(raw: str | int | None) -> HypeTier:
    """Retrieve the full HypeTier descriptor."""
    canonical = normalize_hype_level(raw)
    return TIERS[canonical]


def ask_hype_level(input_fn: Callable[[str], str] = input) -> str:
    """Interactive CLI menu prompting the operator to choose their narrative energy level."""
    banner = (
        "\n========================================================================\n"
        "[PRD-AGENT] Calibrate Your Narrative Dial\n"
        "========================================================================\n\n"
        "How loud do you want this story to go?\n\n"
        "[1] Level 1000: Electric God-Mode (Default)\n"
        "    - Kinetic, loud, solo unicorn, 100x leverage, unstoppable future\n"
        "[2] Level 750:  High-Converting Venture Hype\n"
        "    - 2:00 AM founder nightmare, unlocked dream, aggressive contrast\n"
        "[3] Level 500:  Balanced Authority\n"
        "    - Dignified strength, concrete proof, zero buzzwords\n"
        "[4] Level 250:  Pure Technical Truth\n"
        "    - Clinical, understated, empirical rigor, code and data first\n\n"
    )
    print(banner, file=sys.stderr)
    try:
        choice = input_fn("Select [1-4] (Press Enter for Level 1000): ")
    except (EOFError, KeyboardInterrupt):
        return DEFAULT_HYPE_LEVEL
    return normalize_hype_level(choice)
