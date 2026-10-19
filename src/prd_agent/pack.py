"""Multi-Asset Launch Pack: Generate the complete launch arsenal for any artifact.

Produces:
- copy.json: Landing page copy deck (headline, subhead, superpowers, before/after, CTA)
- launch_thread.md: Viral X / Twitter announcement thread (hook, drama, proof, link)
- show_hn.md: Show HN / Product Hunt launch narrative (founder origin, architecture, dogfooding)
- pitch_deck.md: 10-slide high-stakes pitch narrative (category shift, secret weapon, flywheel)

Enforces:
- Zero em-dashes (—, –, --) across all generated assets
- Narrative calibration according to active hype level and audience persona
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from prd_agent.hype import get_hype_tier
from prd_agent.llm import LLM, extract_json
from prd_agent.persona import get_persona

_EM_DASH_PATTERN = re.compile(r"[\u2014\u2013]|(?<=\S)\s*--\s*(?=\S)")


def purge_em_dashes(text: str) -> str:
    """Purge all em-dashes, en-dashes, and double hyphens from text without breaking words."""
    cleaned = re.sub(r"\s*[\u2014\u2013]\s*", ", ", text)
    cleaned = re.sub(r"\s+--\s+", ", ", cleaned)
    cleaned = re.sub(r"--", "-", cleaned)
    # Clean up double commas if created
    cleaned = re.sub(r",\s*,", ",", cleaned)
    return cleaned


def assert_no_em_dashes(text: str) -> None:
    """Raise ValueError if any forbidden em-dash or double-hyphen is present."""
    if "\u2014" in text or "\u2013" in text or " -- " in text or "--" in text:
        raise ValueError("forbidden em-dash or double-hyphen found in text")


def _purge_obj(obj: Any) -> Any:
    if isinstance(obj, str):
        return purge_em_dashes(obj)
    if isinstance(obj, list):
        return [_purge_obj(item) for item in obj]
    if isinstance(obj, dict):
        return {key: _purge_obj(val) for key, val in obj.items()}
    return obj


@dataclass(frozen=True)
class PackResult:
    pack_dir: Path
    copy_json_path: Path
    launch_thread_path: Path
    show_hn_path: Path
    pitch_deck_path: Path


COPY_DECK_SYSTEM = (
    "You are a master conversion copywriter. You write high-voltage landing page copy decks. "
    "Every section attacks a human pain and sells a transformative superpower. Answer with valid "
    "JSON and nothing else. Strictly ZERO em-dashes (—, –, --)."
)

COPY_DECK_PROMPT = """\
Create a complete landing page copy deck for this product.

Structure your answer with exactly this JSON schema:
{{
  "headline": "Magnetic, punchy hero headline (NO em-dashes)",
  "subheadline": "Compelling subheadline explaining the core value and superpower",
  "superpowers": [
    {{
      "title": "Superpower Name",
      "description": "2-3 sentences explaining the mechanism and benefit",
      "nightmare_contrast": "Before vs After contrast"
    }}
  ],
  "before_after_table": [
    {{"legacy_way": "The painful old way", "superpower_way": "The unlocked new way"}}
  ],
  "social_proof_hooks": [
    "Realistic, high-impact quotes or results from early users"
  ],
  "cta": {{
    "primary": "High-converting action button text",
    "secondary": "Alternative button text",
    "guarantee": "Trust or risk-reversal line"
  }}
}}

Narrative Calibration:
{hype_directive}

Audience Persona:
{persona_directive}

Positioning:
{positioning}

Claims & Verification:
{claims}

Story Context:
{story}
"""

LAUNCH_THREAD_SYSTEM = (
    "You are an elite viral tech launch strategist. You craft high-converting, pattern-interrupting "
    "X/Twitter launch threads that generate massive buzz and immediate signups. Strictly ZERO em-dashes (—, –, --)."
)

LAUNCH_THREAD_PROMPT = """\
Write a viral 6-8 tweet launch thread for this product.

Thread Structure:
- 1/7: The Pattern Interrupt / Controversial Hook (Attack the status quo)
- 2/7: The 3:00 AM Nightmare (The specific pain that forced this to be built)
- 3/7: The Lie (Why current market tools and incumbents fail)
- 4/7: The Architectural Shift (The secret weapon / core invention)
- 5/7: The 3 Core Superpowers (Concrete capabilities, not generic fluff)
- 6/7: The Proof / Benchmarks (Real speed, numbers, deterministic execution)
- 7/7: The Call to Action (Link, demo, invitation to test)

Format as numbered tweets separated by double newlines (1/7, 2/7, etc.).
Strictly NO em-dashes (—, –, --). Use commas or periods instead.

Narrative Calibration:
{hype_directive}

Audience Persona:
{persona_directive}

Positioning:
{positioning}

Claims:
{claims}

Story Context:
{story}
"""

SHOW_HN_SYSTEM = (
    "You are a deeply technical founder writing a Show HN / Product Hunt launch post. "
    "Lead with personal frustration and technical substance. No corporate fluff. Strictly ZERO em-dashes (—, –, --)."
)

SHOW_HN_PROMPT = """\
Write a high-authenticity Show HN launch drop in Markdown.

Format:
# Show HN: [Product Name] - [One-sentence punchy hook without buzzwords]

### Why I built this
[The founder origin story, the personal frustration, and why existing tools failed]

### What it actually does
[Concrete technical explanation of the architecture and superpowers]

### What surprised us
[Unexpected lessons or edge cases learned while dogfooding this internally]

### Try it / Feedback
[Direct link, install command, and open invitation for hard technical feedback]

Strictly NO em-dashes (—, –, --).

Narrative Calibration:
{hype_directive}

Audience Persona:
{persona_directive}

Positioning:
{positioning}

Claims:
{claims}

Story Context:
{story}
"""

PITCH_DECK_SYSTEM = (
    "You are a category-defining venture founder. You craft 10-slide high-stakes pitch deck "
    "narratives that command investor conviction. Strictly ZERO em-dashes (—, –, --)."
)

PITCH_DECK_PROMPT = """\
Write a 10-slide high-stakes pitch deck narrative in Markdown.

Format:
# Slide 1: The Category Shift
[The macroeconomic or technological shift that makes legacy tools obsolete]

# Slide 2: The Bleeding Wound
[Quantified pain, burnout, lost hours, and runaway costs]

# Slide 3: The Broken Alternatives
[Why incumbent vendors and band-aids cannot solve this fundamental flaw]

# Slide 4: The Breakthrough
[The core invention that changes the equation]

# Slide 5: The Superpowers
[The 3 unfair capabilities granted to users]

# Slide 6: The Secret Weapon
[The defensible technical moat and architectural isolation]

# Slide 7: Unfair Economics
[Massive leverage: doing with 1 person what legacy teams do with 50]

# Slide 8: Traction & Validation
[Real usage, benchmarks, and adoption momentum]

# Slide 9: The Impossible Future
[The multi-year category vision]

# Slide 10: The Ask
[Next step, pilot onboarding, or capital round]

Strictly NO em-dashes (—, –, --).

Narrative Calibration:
{hype_directive}

Audience Persona:
{persona_directive}

Positioning:
{positioning}

Claims:
{claims}

Story Context:
{story}
"""


def generate_copy_deck(
    *,
    claims: dict,
    trends: dict,
    positioning: dict,
    story: str,
    llm: LLM,
    hype: str | None = None,
    persona: str | None = None,
) -> dict:
    tier = get_hype_tier(hype)
    pers = get_persona(persona)
    prompt = COPY_DECK_PROMPT.format(
        hype_directive=tier.directive,
        persona_directive=pers.directive,
        positioning=json.dumps(positioning, indent=2, ensure_ascii=False),
        claims=json.dumps(claims, indent=2, ensure_ascii=False),
        story=story,
    )
    raw = llm.complete(system=COPY_DECK_SYSTEM, prompt=prompt)
    doc = extract_json(raw)
    if not isinstance(doc, dict):
        raise ValueError("model response was not a JSON object")
    return _purge_obj(doc)


def generate_launch_thread(
    *,
    claims: dict,
    trends: dict,
    positioning: dict,
    story: str,
    llm: LLM,
    hype: str | None = None,
    persona: str | None = None,
) -> str:
    tier = get_hype_tier(hype)
    pers = get_persona(persona)
    prompt = LAUNCH_THREAD_PROMPT.format(
        hype_directive=tier.directive,
        persona_directive=pers.directive,
        positioning=json.dumps(positioning, indent=2, ensure_ascii=False),
        claims=json.dumps(claims, indent=2, ensure_ascii=False),
        story=story,
    )
    raw = llm.complete(system=LAUNCH_THREAD_SYSTEM, prompt=prompt)
    return purge_em_dashes(raw.strip())


def generate_show_hn(
    *,
    claims: dict,
    trends: dict,
    positioning: dict,
    story: str,
    llm: LLM,
    hype: str | None = None,
    persona: str | None = None,
) -> str:
    tier = get_hype_tier(hype)
    pers = get_persona(persona)
    prompt = SHOW_HN_PROMPT.format(
        hype_directive=tier.directive,
        persona_directive=pers.directive,
        positioning=json.dumps(positioning, indent=2, ensure_ascii=False),
        claims=json.dumps(claims, indent=2, ensure_ascii=False),
        story=story,
    )
    raw = llm.complete(system=SHOW_HN_SYSTEM, prompt=prompt)
    return purge_em_dashes(raw.strip())


def generate_pitch_deck(
    *,
    claims: dict,
    trends: dict,
    positioning: dict,
    story: str,
    llm: LLM,
    hype: str | None = None,
    persona: str | None = None,
) -> str:
    tier = get_hype_tier(hype)
    pers = get_persona(persona)
    prompt = PITCH_DECK_PROMPT.format(
        hype_directive=tier.directive,
        persona_directive=pers.directive,
        positioning=json.dumps(positioning, indent=2, ensure_ascii=False),
        claims=json.dumps(claims, indent=2, ensure_ascii=False),
        story=story,
    )
    raw = llm.complete(system=PITCH_DECK_SYSTEM, prompt=prompt)
    return purge_em_dashes(raw.strip())


def generate_pack(
    *,
    run_dir: Path,
    claims: dict,
    trends: dict,
    positioning: dict,
    story: str,
    llm: LLM,
    hype: str | None = None,
    persona: str | None = None,
) -> PackResult:
    """Generate all 4 assets in the Launch Pack under run_dir/pack."""
    pack_dir = run_dir / "pack"
    pack_dir.mkdir(parents=True, exist_ok=True)

    # 1. Landing page copy deck
    copy_deck = generate_copy_deck(
        claims=claims,
        trends=trends,
        positioning=positioning,
        story=story,
        llm=llm,
        hype=hype,
        persona=persona,
    )
    copy_path = pack_dir / "copy.json"
    copy_path.write_text(json.dumps(copy_deck, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 2. Launch thread
    thread_text = generate_launch_thread(
        claims=claims,
        trends=trends,
        positioning=positioning,
        story=story,
        llm=llm,
        hype=hype,
        persona=persona,
    )
    thread_path = pack_dir / "launch_thread.md"
    thread_path.write_text(thread_text + "\n", encoding="utf-8")

    # 3. Show HN
    show_hn_text = generate_show_hn(
        claims=claims,
        trends=trends,
        positioning=positioning,
        story=story,
        llm=llm,
        hype=hype,
        persona=persona,
    )
    show_hn_path = pack_dir / "show_hn.md"
    show_hn_path.write_text(show_hn_text + "\n", encoding="utf-8")

    # 4. Pitch deck
    pitch_deck_text = generate_pitch_deck(
        claims=claims,
        trends=trends,
        positioning=positioning,
        story=story,
        llm=llm,
        hype=hype,
        persona=persona,
    )
    pitch_deck_path = pack_dir / "pitch_deck.md"
    pitch_deck_path.write_text(pitch_deck_text + "\n", encoding="utf-8")

    return PackResult(
        pack_dir=pack_dir,
        copy_json_path=copy_path,
        launch_thread_path=thread_path,
        show_hn_path=show_hn_path,
        pitch_deck_path=pitch_deck_path,
    )
