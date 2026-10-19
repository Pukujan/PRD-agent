"""One entry point over the four stages, the two modes, and the runs/<name>/ writes.

Every stage document is written beside the story so any stage can be inspected or re-run in
isolation. The mode difference is a single boolean; see spec section 4.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from prd_agent import (
    evals as evals_stage,
)
from prd_agent import (
    flags as flags_module,
)
from prd_agent import (
    intake,
)
from prd_agent import (
    pack as pack_stage,
)
from prd_agent import (
    positioning as positioning_stage,
)
from prd_agent import (
    story as story_stage,
)
from prd_agent import (
    trends as trends_stage,
)
from prd_agent.artifact import Artifact, collect_artifact
from prd_agent.checks import CheckReport
from prd_agent.errors import StageError
from prd_agent.llm import LLM
from prd_agent.pack import PackResult
from prd_agent.schemas import TRENDS_SPEC, require_valid
from prd_agent.voice import build_five_lines_from_positioning

RUNS_DIR = "runs"
STORIES_DIR = "stories"

@dataclass
class RunResult:
    task_name: str
    run_dir: Path
    story_path: Path
    claims_path: Path
    trends_path: Path
    positioning_path: Path
    flags: list[dict] = field(default_factory=list)
    report: CheckReport | None = None
    awaiting_answers: bool = False
    pack: PackResult | None = None
    five_lines: str = ""

def run_dir(root: Path, name: str) -> Path:
    return Path(root) / RUNS_DIR / name

def default_out(root: Path, name: str) -> Path:
    return Path(root) / STORIES_DIR / f"{name}.md"

def load_trends(path: Path) -> dict:
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StageError(f"{path} is not readable JSON: {exc}") from exc
    require_valid(doc, TRENDS_SPEC, str(path))
    return doc

def answers_from_file(path: Path) -> dict[str, str]:
    """Read a `{flag id: answer}` map so a run can be driven without stdin."""
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StageError(f"{path} is not readable JSON: {exc}") from exc
    if not isinstance(doc, dict):
        raise StageError(f"{path} must be a JSON object of flag id to answer")
    return {str(key): str(value) for key, value in doc.items()}

def _write_json(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def run(
    artifact_path: Path,
    *,
    llm: LLM,
    trends: dict | None = None,
    trends_file: Path | None = None,
    out: Path | None = None,
    readme: bool = False,
    autonomous: bool = True,
    ask: Callable[[list[dict]], dict[str, str]] | None = None,
    answers: dict[str, str] | None = None,
    live: bool = True,
    evals_path: Path | None = None,
    hype: str | None = None,
    persona: str | None = None,
    pack: bool = False,
) -> RunResult:
    """Run intake, trends, positioning and story. Human mode stops at the flag loop."""
    artifact_path = Path(artifact_path)
    if not artifact_path.exists():
        raise StageError(f"artifact path does not exist: {artifact_path}")
    root = artifact_path.resolve().parent
    name = artifact_path.resolve().name

    if not live and trends is None and trends_file is None:
        raise StageError(
            "no trends source. Pass --trends-file <path>, or drop --no-web to run the live web pass."
        )

    # Intake runs first: the live trends pass reads `claims` to build its prompt.
    collected: Artifact = collect_artifact(artifact_path)
    claims = intake.intake(artifact_path, llm, artifact=collected)

    if trends is not None:
        trends_doc = trends
        require_valid(trends_doc, TRENDS_SPEC, "trends.json")
    elif trends_file is not None:
        trends_doc = load_trends(Path(trends_file))
    elif not live:
        raise StageError(
            "no trends source. Pass --trends-file <path>, or drop --no-web to run the live web pass."
        )
    else:
        trends_doc = trends_stage.analyze(claims, llm)

    positioned = positioning_stage.positioning(claims, trends_doc, llm, hype=hype, persona=persona)

    target_run_dir = run_dir(root, name)
    if out is not None:
        target_story = Path(out)
    elif readme:
        target_story = artifact_path / "README.md"
    else:
        target_story = default_out(root, name)
    _write_json(target_run_dir / "claims.json", claims)
    _write_json(target_run_dir / "trends.json", trends_doc)
    _write_json(target_run_dir / "positioning.json", positioned)

    five_lines_text = build_five_lines_from_positioning(positioned)
    (target_run_dir / "five_lines.txt").write_text(five_lines_text + "\n", encoding="utf-8")

    result = RunResult(
        task_name=name,
        run_dir=target_run_dir,
        story_path=target_story,
        claims_path=target_run_dir / "claims.json",
        trends_path=target_run_dir / "trends.json",
        positioning_path=target_run_dir / "positioning.json",
        flags=list(positioned.get("flags", [])),
        five_lines=five_lines_text,
    )

    if not autonomous and answers is None and ask is None:
        result.awaiting_answers = True
        return result

    if not autonomous:
        if answers is not None:
            supplied = answers
        else:
            assert ask is not None
            supplied = ask(list(positioned.get("flags", [])))

        if supplied or ask is not None:
            positioned = positioning_stage.positioning(
                claims,
                trends_doc,
                llm,
                answers=flags_module.answers_as_prompt(list(positioned.get("flags", [])), supplied),
                hype=hype,
                persona=persona,
            )
            _write_json(target_run_dir / "positioning.json", positioned)
            result.flags = list(positioned.get("flags", []))
            five_lines_text = build_five_lines_from_positioning(positioned)
            (target_run_dir / "five_lines.txt").write_text(five_lines_text + "\n", encoding="utf-8")
            result.five_lines = five_lines_text

    corpus = evals_stage.load_evals(evals_path or evals_stage.EVALS_PATH)
    exemplars = evals_stage.select_exemplars(corpus, positioning=positioned)
    page, report = story_stage.story(
        claims=claims,
        positioning=positioned,
        trends=trends_doc,
        llm=llm,
        exemplars=exemplars,
        hype=hype,
        persona=persona,
    )
    target_story.parent.mkdir(parents=True, exist_ok=True)
    target_story.write_text(page, encoding="utf-8")
    record = evals_stage.build_eval(
        task_name=name,
        artifact_name=collected.name,
        positioning=positioned,
        page=page,
        report=report,
    )
    evals_stage.append_eval(evals_path or evals_stage.EVALS_PATH, record)
    result.report = report
    result.awaiting_answers = False

    if pack:
        result.pack = pack_stage.generate_pack(
            run_dir=target_run_dir,
            claims=claims,
            trends=trends_doc,
            positioning=positioned,
            story=page,
            llm=llm,
            hype=hype,
            persona=persona,
        )

    return result

def close_flag_loop(
    result: RunResult,
    *,
    llm: LLM,
    answers: dict[str, str],
    hype: str | None = None,
    persona: str | None = None,
    pack: bool = False,
) -> RunResult:
    """Resume a stopped human-mode run with the owner's answers.

    Reads the documents already on disk, folds the answers back into positioning, regenerates
    the story and rewrites the affected files.
    """
    claims = json.loads(result.claims_path.read_text(encoding="utf-8"))
    trends_doc = json.loads(result.trends_path.read_text(encoding="utf-8"))
    positioned = json.loads(result.positioning_path.read_text(encoding="utf-8"))
    hype_choice = hype or positioned.get("hype_level")
    persona_choice = persona or positioned.get("persona")
    revised = positioning_stage.positioning(
        claims,
        trends_doc,
        llm,
        answers=flags_module.answers_as_prompt(list(positioned.get("flags", [])), answers),
        hype=hype_choice,
        persona=persona_choice,
    )
    _write_json(result.positioning_path, revised)
    five_lines_text = build_five_lines_from_positioning(revised)
    (result.run_dir / "five_lines.txt").write_text(five_lines_text + "\n", encoding="utf-8")
    result.five_lines = five_lines_text

    page, report = story_stage.story(
        claims=claims,
        positioning=revised,
        trends=trends_doc,
        llm=llm,
        hype=hype_choice,
        persona=persona_choice,
    )
    result.story_path.parent.mkdir(parents=True, exist_ok=True)
    result.story_path.write_text(page, encoding="utf-8")
    result.flags = list(revised.get("flags", []))
    result.report = report
    result.awaiting_answers = False
    if pack:
        result.pack = pack_stage.generate_pack(
            run_dir=result.run_dir,
            claims=claims,
            trends=trends_doc,
            positioning=revised,
            story=page,
            llm=llm,
            hype=hype_choice,
            persona=persona_choice,
        )
    return result
