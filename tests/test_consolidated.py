from __future__ import annotations

from pathlib import Path

import pytest

from prd_agent.checks import check_story
from prd_agent.pack import assert_no_em_dashes
from prd_agent.voice import (
    ManifestoVoice,
    build_five_lines_from_positioning,
    format_five_lines,
    get_voice,
)


def test_voice_mapping_backwards_compatible() -> None:
    assert get_voice("1000") == ManifestoVoice.ELECTRIC
    assert get_voice("electric") == ManifestoVoice.ELECTRIC
    assert get_voice("solopreneur") == ManifestoVoice.ELECTRIC

    assert get_voice("750") == ManifestoVoice.VENTURE
    assert get_voice("venture") == ManifestoVoice.VENTURE
    assert get_voice("enterprise") == ManifestoVoice.VENTURE

    assert get_voice("500") == ManifestoVoice.TECHNICAL
    assert get_voice("250") == ManifestoVoice.TECHNICAL
    assert get_voice("technical") == ManifestoVoice.TECHNICAL
    assert get_voice("truth") == ManifestoVoice.TECHNICAL

    # Default fallback
    assert get_voice(None) == ManifestoVoice.ELECTRIC


def test_format_five_lines_produces_clean_battle_cry() -> None:
    lines = [
        "Stop renting your brain from a cloud monopoly at three cents a query.",
        "The computer on your desk is not a consumer toy, it is a private supersonic inference engine.",
        "TurboFit scans your silicon down to the byte, loads the heaviest model your hardware can carry, and hot-swaps memory so you never crash.",
        "Zero cloud surveillance, zero monthly API bills, and 200 tokens per second streaming offline while you sleep.",
        "Set provider to TurboFit, select model auto, and take back the wheel.",
    ]
    formatted = format_five_lines(lines)
    assert len(formatted.strip().split("\n\n")) == 5
    assert_no_em_dashes(formatted)
    assert "Level 1000" not in formatted
    assert "belief inversion" not in formatted
    assert "The false dogma says" not in formatted


def test_checks_flag_meta_prompt_leakage_and_template_openers() -> None:
    leaked_draft = """# A New Era

**Stop renting cloud compute.**

Level 1000, solopreneur, belief inversion:

The false dogma says local AI is a toy. TurboFit buries that dogma.

## 1. The Nightmare
Staying up at 2:00 AM fighting broken configurations and rate limits.

## 2. The Solution
Run models locally with deterministic speed.

## 3. How to Start
1. Install
2. Run
3. Enjoy
"""
    report = check_story(leaked_draft)
    assert report.passed() is False
    banned_rules = [b.rule for b in report.bans]
    assert any("meta_label" in rule or "template_opener" in rule for rule in banned_rules)


def test_build_five_lines_from_positioning() -> None:
    pos = {
        "cultural_enemy": "The false dogma says local AI is a toy for people with a 4090.",
        "rebellion_belief": "The truth is your workstation is a private supersonic engine.",
        "differentiator": "TurboFit hot-swaps memory so your agents never crash.",
    }
    result = build_five_lines_from_positioning(pos)
    assert len(result.strip().split("\n\n")) == 5
    assert not result.startswith("The false dogma says")
    assert "local AI is a toy" in result
    assert "supersonic engine" in result
    assert "TurboFit" in result


def test_pipeline_writes_five_lines_file_and_result(
    tmp_path: Path, repo_root: Path, pcm_run: Path
) -> None:
    from prd_agent import pipeline
    from prd_agent.llm import FakeLLM

    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    good_body = (
        (Path(__file__).parent / "test_story.py")
        .read_text(encoding="utf-8")
        .split('GOOD_BODY = """\\\n')[1]
        .split('"""')[0]
    )
    fake = FakeLLM(
        responses=[
            (pcm_run / "claims.json").read_text(encoding="utf-8"),
            (pcm_run / "positioning.json").read_text(encoding="utf-8"),
            good_body,
        ]
    )
    result = pipeline.run(
        artifact,
        llm=fake,
        trends_file=repo_root / "tests" / "fixtures" / "trends_pcm.json",
        autonomous=True,
    )
    assert result.five_lines != ""
    assert len(result.five_lines.split("\n\n")) == 5
    five_lines_path = result.run_dir / "five_lines.txt"
    assert five_lines_path.is_file()
    assert five_lines_path.read_text(encoding="utf-8").strip() == result.five_lines.strip()


def test_cli_prints_five_lines_battle_cry_to_stdout(
    tmp_path: Path, repo_root: Path, pcm_run: Path, monkeypatch, capsys
) -> None:
    from prd_agent import cli

    artifact = tmp_path / "mini"
    artifact.mkdir()
    (artifact / "README.md").write_text("# mini\n", encoding="utf-8")
    canned = tmp_path / "canned"
    canned.mkdir()
    for index, source in enumerate(
        [pcm_run / "claims.json", pcm_run / "positioning.json"],
        start=1,
    ):
        (canned / f"{index:02d}.txt").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (canned / "03.txt").write_text(
        (Path(__file__).parent / "test_story.py")
        .read_text(encoding="utf-8")
        .split('GOOD_BODY = """\\\n')[1]
        .split('"""')[0],
        encoding="utf-8",
    )
    monkeypatch.setenv("PRD_AGENT_LLM", "fake")
    monkeypatch.setenv("PRD_AGENT_CANNED_DIR", str(canned))
    monkeypatch.chdir(tmp_path)
    code = cli.main([
        str(artifact),
        "--autonomous",
        "--trends-file", str(repo_root / "tests" / "fixtures" / "trends_pcm.json"),
    ])
    assert code == 0
    captured = capsys.readouterr()
    assert "5-LINE EXECUTIVE BATTLE CRY" in captured.out
    assert "prd-agent: wrote" in captured.out


def test_hidden_holdout_turbofit() -> None:
    turbofit_path = Path("D:/development/turbofit")
    if not turbofit_path.exists():
        pytest.skip("Turbofit holdout repository not present on this machine")

    from prd_agent.artifact import collect_artifact
    artifact = collect_artifact(turbofit_path)
    assert artifact.name == "turbofit"
    assert len(artifact.files) > 0
    assert any("README.md" in f.path for f in artifact.files)

    pos = {
        "cultural_enemy": "The false dogma says local AI is a toy for hobbyists while cloud vendors rent out compute at three cents a query.",
        "rebellion_belief": "The truth is your workstation silicon is a private supersonic engine.",
        "differentiator": "TurboFit inventories compute down to the byte and loads the heaviest model your hardware can safely sustain.",
        "dream_scene": "Zero monthly API bills and continuous local inference running 24/7 without a single crash.",
        "weaponized_mechanisms": [
            "TurboFit checks physical memory and maps optimal quants (Qwen 3.8 27B or Maple Preview) without crashing."
        ],
    }

    five_lines = build_five_lines_from_positioning(pos)
    assert len(five_lines.strip().split("\n\n")) == 5
    assert_no_em_dashes(five_lines)
    assert "The false dogma says" not in five_lines
    assert "The truth is" not in five_lines
    assert "Level 1000" not in five_lines
    assert "belief inversion" not in five_lines
    assert "three cents a query" in five_lines
    assert "supersonic engine" in five_lines

    turbofit_story = """# Stop Renting Your Brain from the Cloud

**TurboFit scans your silicon and loads the heaviest local model your hardware can safely sustain.**

## 1. The Token Tollbooth
Every month the invoice arrives. You pay three cents a query for the privilege of renting intelligence on someone else's terms. Your proprietary code streams across public fiber. When their rate limit triggers, your entire autonomous stack grinds to a halt.

## 2. The 2:00 AM Nightmare
It is 2:00 AM and your automated test runner is dead. A cloud provider dropped your connection mid-evaluation. You find yourself frantically alt-tabbing between crashing terminal windows while your sprint deadline slips away.

## 3. The Sovereign Reality
You close your laptop at 6:00 PM with total confidence. Your workstation runs models through the night on private silicon. Every weight resides in local memory. Every token streams directly to your terminal.

## 4. The Machine Under the Hood
TurboFit turns local silicon into an impenetrable private fortress.
The adaptive runtime calculates exact usable memory. It selects optimized quants like Maple Preview and Qwen 3.8 27B so your agents never run out of memory.

## 5. Take the Wheel
Set provider to custom turbofit, select model auto, and execute right now:
```text
provider: custom:turbofit
model: auto
```
"""
    report = check_story(turbofit_story)
    assert report.passed() is True
    assert_no_em_dashes(turbofit_story)
    assert "Level 1000" not in turbofit_story
    assert "belief inversion" not in turbofit_story
    assert "The false dogma says" not in turbofit_story
