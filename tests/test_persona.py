from __future__ import annotations

import pytest

from prd_agent.persona import (
    DEFAULT_PERSONA,
    PERSONAS,
    Persona,
    ask_persona,
    get_persona,
    normalize_persona,
)


def test_canonical_personas_defined() -> None:
    assert set(PERSONAS.keys()) == {"solopreneur", "enterprise", "normie"}
    for pid, persona in PERSONAS.items():
        assert isinstance(persona, Persona)
        assert persona.id == pid
        assert persona.name
        assert persona.summary
        assert persona.target_nightmare
        assert persona.target_dream
        assert persona.directive


def test_normalize_persona() -> None:
    assert normalize_persona(None) == DEFAULT_PERSONA
    assert normalize_persona("") == DEFAULT_PERSONA
    assert normalize_persona("solopreneur") == "solopreneur"
    assert normalize_persona("solo") == "solopreneur"
    assert normalize_persona("unicorn") == "solopreneur"
    assert normalize_persona("builder") == "solopreneur"
    assert normalize_persona("indie") == "solopreneur"
    assert normalize_persona("1") == "solopreneur"

    assert normalize_persona("enterprise") == "enterprise"
    assert normalize_persona("cto") == "enterprise"
    assert normalize_persona("vp") == "enterprise"
    assert normalize_persona("executive") == "enterprise"
    assert normalize_persona("b2b") == "enterprise"
    assert normalize_persona("2") == "enterprise"

    assert normalize_persona("normie") == "normie"
    assert normalize_persona("consumer") == "normie"
    assert normalize_persona("everyday") == "normie"
    assert normalize_persona("magic") == "normie"
    assert normalize_persona("lifestyle") == "normie"
    assert normalize_persona("3") == "normie"

    assert normalize_persona("unrecognized-random") == DEFAULT_PERSONA


def test_get_persona() -> None:
    solo = get_persona("unicorn")
    assert solo.id == "solopreneur"
    assert "Unicorn" in solo.name

    ent = get_persona("cto")
    assert ent.id == "enterprise"
    assert "Boardroom" in ent.target_nightmare or "liability" in ent.target_nightmare.lower()

    normie = get_persona("consumer")
    assert normie.id == "normie"
    assert "Magic" in normie.name or "magic" in normie.directive.lower()


def test_ask_persona_interactive() -> None:
    assert ask_persona(input_fn=lambda _: "2") == "enterprise"
    assert ask_persona(input_fn=lambda _: "normie") == "normie"
    assert ask_persona(input_fn=lambda _: "") == DEFAULT_PERSONA


def test_ask_persona_handles_eof() -> None:
    def raise_eof(_: str) -> str:
        raise EOFError()

    assert ask_persona(input_fn=raise_eof) == DEFAULT_PERSONA
