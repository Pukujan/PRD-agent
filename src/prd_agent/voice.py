"""Consolidated Manifesto Voice and Executive 5-Line Formatter.

Fuses the historical hype levels (1000, 750, 500, 250) and personas (solopreneur,
enterprise, normie) into a single unified Tension Spine + Manifesto Voice architecture.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Sequence


class ManifestoVoice(str, Enum):
    ELECTRIC = "electric"
    VENTURE = "venture"
    TECHNICAL = "technical"


VOICE_ALIASES: dict[str, ManifestoVoice] = {
    # Electric / Solo Unicorn / 1000
    "1000": ManifestoVoice.ELECTRIC,
    "electric": ManifestoVoice.ELECTRIC,
    "solopreneur": ManifestoVoice.ELECTRIC,
    "god-mode": ManifestoVoice.ELECTRIC,
    "godmode": ManifestoVoice.ELECTRIC,
    "solo": ManifestoVoice.ELECTRIC,
    "unicorn": ManifestoVoice.ELECTRIC,
    "normie": ManifestoVoice.ELECTRIC,

    # Venture / Category Shift / 750
    "750": ManifestoVoice.VENTURE,
    "venture": ManifestoVoice.VENTURE,
    "enterprise": ManifestoVoice.VENTURE,
    "category": ManifestoVoice.VENTURE,

    # Technical / Empirical Truth / 500 / 250
    "500": ManifestoVoice.TECHNICAL,
    "250": ManifestoVoice.TECHNICAL,
    "technical": ManifestoVoice.TECHNICAL,
    "truth": ManifestoVoice.TECHNICAL,
    "balanced": ManifestoVoice.TECHNICAL,
    "empirical": ManifestoVoice.TECHNICAL,
}

VOICE_DIRECTIVES: dict[ManifestoVoice, str] = {
    ManifestoVoice.ELECTRIC: (
        "VOICE: ELECTRIC GOD-MODE (100x Solo Leverage & Radical Sovereignty)\n"
        "- Attack the cynical status quo and false dogma with visceral emotion.\n"
        "- Frame the user as a sovereign creator/builder commanding supersonic leverage.\n"
        "- Sell the 'flying car' dream: 100x velocity, total ownership, zero permission needed.\n"
        "- Transform technical mechanisms into impenetrable shields and superpowers.\n"
        "- High-voltage, kinetic rhythm, short punchy paragraphs, and unapologetic conviction."
    ),
    ManifestoVoice.VENTURE: (
        "VOICE: CATEGORY CREATION & HIGH-STAKES LEVERAGE\n"
        "- Call out the architectural obsolescence and operational liabilities of legacy tools.\n"
        "- Quantify the human pain: burnout, lost hours, runaway cloud bills, security theater.\n"
        "- Position the product as the fundamental category shift that rewrites unit economics.\n"
        "- Frame code mechanisms as an unassailable technical moat and architectural isolation."
    ),
    ManifestoVoice.TECHNICAL: (
        "VOICE: EMPIRICAL TRUTH & ZERO-FLUFF RIGOR\n"
        "- Attack vendor hype, vanity benchmarks, and unverified promises.\n"
        "- Ground every single claim in inspectable, mathematical, and deterministic receipts.\n"
        "- Understated, confident engineering authority. Zero empty buzzwords.\n"
        "- Let the mechanism and verifiable facts carry the load."
    ),
}


def get_voice(value: str | None) -> ManifestoVoice:
    """Resolve any hype level, persona, or voice string to a canonical ManifestoVoice."""
    if not value:
        return ManifestoVoice.ELECTRIC
    normalized = str(value).strip().lower()
    return VOICE_ALIASES.get(normalized, ManifestoVoice.ELECTRIC)


def get_voice_directive(value: str | None) -> str:
    """Return the directive prompt string for a voice/hype/persona value."""
    voice = get_voice(value)
    return VOICE_DIRECTIVES[voice]


def format_five_lines(lines: Sequence[str]) -> str:
    """Format and validate the 5-line executive battle cry."""
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Remove any leading bullet or number
        stripped = re.sub(r"^[-*•\d.]+\s*", "", stripped)
        if stripped:
            cleaned.append(stripped)
    return "\n\n".join(cleaned[:5])


def build_five_lines_from_positioning(positioning: dict) -> str:
    """Build the 5-line executive hook deterministically from positioning facts."""
    enemy = (
        positioning.get("cultural_enemy")
        or positioning.get("discomfort")
        or "The status quo compromises your sovereignty."
    )
    truth = (
        positioning.get("rebellion_belief")
        or positioning.get("vision")
        or "The machine on your desk is a private supersonic engine."
    )
    mechanisms = positioning.get("weaponized_mechanisms") or []
    weapon = (
        positioning.get("differentiator")
        or (mechanisms[0] if mechanisms else "It guards your execution with mathematical guarantees.")
    )
    dream = (
        positioning.get("dream_scene")
        or (mechanisms[1] if len(mechanisms) > 1 else None)
        or positioning.get("path")
        or "Zero cloud surveillance, zero monthly API bills, and private supersonic execution while you sleep."
    )

    clean_enemy = re.sub(
        r"^(?:The false dogma says|The cultural enemy is)\s*", "", str(enemy), flags=re.IGNORECASE
    ).strip()
    clean_truth = re.sub(
        r"^(?:The rebellion belief is|The truth is)\s*", "", str(truth), flags=re.IGNORECASE
    ).strip()
    clean_weapon = re.sub(
        r"^(?:The code shield is|The mechanism is)\s*", "", str(weapon), flags=re.IGNORECASE
    ).strip()
    clean_dream = re.sub(
        r"^(?:The dream scene is|The unlocked dream is)\s*", "", str(dream), flags=re.IGNORECASE
    ).strip()

    lines = [
        clean_enemy,
        clean_truth,
        clean_weapon,
        clean_dream,
        "Take back the wheel.",
    ]
    return format_five_lines(lines)

