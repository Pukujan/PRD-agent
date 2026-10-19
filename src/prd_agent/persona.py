"""Audience Persona Calibrator: Tailor the narrative hook and vocabulary to the buyer.

Personas:
- solopreneur: The One-Person Unicorn / solo builder (100x leverage, velocity, zero headcount)
- enterprise:   The Pragmatic CTO / VP of Eng (boardroom liability, cloud burn, vendor cartels)
- normie:       The Everyday Consumer / Non-technical operator (pure magic, flying cars, zero jargon)
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Persona:
    id: str
    name: str
    summary: str
    target_nightmare: str
    target_dream: str
    directive: str


PERSONAS: dict[str, Persona] = {
    "solopreneur": Persona(
        id="solopreneur",
        name="The One-Person Unicorn / Solopreneur",
        summary="Autonomous leverage, 1-person scale, shipping speed, zero headcount",
        target_nightmare=(
            "Being trapped babysitting brittle tools, drowning in maintenance sludge, "
            "and getting out-marketed while doing all the heavy lifting alone."
        ),
        target_dream=(
            "Infinite autonomous leverage: a single operator commanding an entire software empire, "
            "shipping at electric speed while sleeping, out-building 50-person legacy teams."
        ),
        directive=(
            "AUDIENCE PERSONA (SOLOPRENEUR / UNICORN): Address the hungry solo builder and indie hacker. "
            "Emphasize infinite leverage, electric shipping velocity, killing administrative drag, and the "
            "reality of the One-Person Unicorn out-maneuvering bloated legacy teams. Focus on cashflow, "
            "autonomy, and shipping without human babysitters."
        ),
    ),
    "enterprise": Persona(
        id="enterprise",
        name="The Pragmatic CTO / Enterprise Leader",
        summary="Boardroom liability, cloud incinerator bills, vendor cartels, SOC2 compliance",
        target_nightmare=(
            "Boardroom humiliation following a zero-day data leak, catastrophic cloud API incinerator bills, "
            "failing SOC2 compliance, and getting squeezed by SaaS vendor lock-in cartels."
        ),
        target_dream=(
            "Sovereign, air-tight systems that guarantee zero data leakage, provable audit compliance "
            "without security theater, and crushing cloud infrastructure waste."
        ),
        directive=(
            "AUDIENCE PERSONA (ENTERPRISE / CTO): Address technical leadership, VP of Engineering, and CTOs. "
            "Attack boardroom liability, security theater, runaway cloud API costs, and vendor lock-in cartels. "
            "Lead with sovereign isolation, predictable unit economics, zero-risk compliance, and engineering "
            "efficiency without legal exposure."
        ),
    ),
    "normie": Persona(
        id="normie",
        name="The Everyday Consumer (Pure Magic)",
        summary="Zero setup friction, plain human language, flying cars, instant superpower",
        target_nightmare=(
            "Cryptic error messages, intimidating terminal jargon, and feeling helpless and left behind "
            "while tech insiders boast about futuristic superpowers."
        ),
        target_dream=(
            "Effortless everyday magic: pressing one button and having hours of painful chores disappear "
            "instantly, lifestyle elevation, and pure simplicity without learning curves."
        ),
        directive=(
            "AUDIENCE PERSONA (NORMIE / CONSUMER): Address normal human beings and non-technical operators. "
            "Banish all developer jargon, command-line syntax, and abstract architecture. Lead with pure, "
            "effortless everyday magic and 'flying car' delight. The technology disappears: they press a button "
            "and their life gets immediately better."
        ),
    ),
}

DEFAULT_PERSONA = "solopreneur"

_ALIASES: dict[str, str] = {
    "1": "solopreneur",
    "solo": "solopreneur",
    "solopreneur": "solopreneur",
    "unicorn": "solopreneur",
    "indie": "solopreneur",
    "hacker": "solopreneur",
    "builder": "solopreneur",
    "developer": "solopreneur",
    "2": "enterprise",
    "enterprise": "enterprise",
    "cto": "enterprise",
    "vp": "enterprise",
    "executive": "enterprise",
    "corporate": "enterprise",
    "b2b": "enterprise",
    "leader": "enterprise",
    "3": "normie",
    "normie": "normie",
    "consumer": "normie",
    "everyday": "normie",
    "user": "normie",
    "magic": "normie",
    "lifestyle": "normie",
}


def normalize_persona(raw: str | int | None) -> str:
    """Normalize user input or CLI argument into one of the canonical 3 personas."""
    if raw is None:
        return DEFAULT_PERSONA
    val = str(raw).strip().lower()
    if not val:
        return DEFAULT_PERSONA
    return _ALIASES.get(val, DEFAULT_PERSONA)


def get_persona(raw: str | int | None) -> Persona:
    """Retrieve the full Persona descriptor."""
    canonical = normalize_persona(raw)
    return PERSONAS[canonical]


def ask_persona(input_fn: Callable[[str], str] = input) -> str:
    """Interactive CLI menu prompting the operator to choose their target audience persona."""
    banner = (
        "\n========================================================================\n"
        "[PRD-AGENT] Calibrate Your Target Audience Persona\n"
        "========================================================================\n\n"
        "Who is this story being written for?\n\n"
        "[1] Solopreneur / One-Person Unicorn (Default)\n"
        "    - Autonomous leverage, 1-person scale, shipping speed, zero headcount\n"
        "[2] Enterprise Leader / Pragmatic CTO\n"
        "    - Boardroom liability, cloud incinerator bills, vendor cartels, SOC2\n"
        "[3] Everyday Consumer / Non-Technical (Pure Magic)\n"
        "    - Zero setup friction, plain human language, flying cars, instant relief\n\n"
    )
    print(banner, file=sys.stderr)
    try:
        choice = input_fn("Select [1-3] (Press Enter for Solopreneur): ")
    except (EOFError, KeyboardInterrupt):
        return DEFAULT_PERSONA
    return normalize_persona(choice)
