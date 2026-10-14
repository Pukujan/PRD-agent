"""One entry point over the four stages, the two modes, and the runs/<name>/ writes.

Every stage document is written beside the story so any stage can be inspected or re-run in
isolation. The mode difference is a single boolean; see spec section 4.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from prd_agent import intake, positioning as positioning_stage, story as story_stage
from prd_agent.artifact import Artifact, collect_artifact
from prd_agent.checks import CheckReport, check_story
from prd_agent.errors import StageError
from prd_agent.llm import LLM
from prd_agent.schemas import TRENDS_SPEC, require_valid

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
    autonomous: bool = False,
    ask=None,
) -> RunResult:
    """Run intake, trends, positioning and story. Human mode stops at the flag loop."""
    artifact_path = Path(artifact_path)
    if not artifact_path.exists():
        raise StageError(f"artifact path does not exist: {artifact_path}")
    root = artifact_path.resolve().parent
    name = artifact_path.resolve().name

    if trends is not None:
        trends_doc = trends
        require_valid(trends_doc, TRENDS_SPEC, "trends.json")
    elif trends_file is not None:
        trends_doc = load_trends(Path(trends_file))
    else:
        raise StageError(
            "no trends source. Pass --trends-file <path> until the live web pass lands."
        )

    collected: Artifact = collect_artifact(artifact_path)
    claims = intake.intake(artifact_path, llm, artifact=collected)
    positioned = positioning_stage.positioning(claims, trends_doc, llm)

    target_run_dir = run_dir(root, name)
    target_story = Path(out) if out is not None else default_out(root, name)
    _write_json(target_run_dir / "claims.json", claims)
    _write_json(target_run_dir / "trends.json", trends_doc)
    _write_json(target_run_dir / "positioning.json", positioned)

    result = RunResult(
        task_name=name,
        run_dir=target_run_dir,
        story_path=target_story,
        claims_path=target_run_dir / "claims.json",
        trends_path=target_run_dir / "trends.json",
        positioning_path=target_run_dir / "positioning.json",
        flags=list(positioned.get("flags", [])),
    )

    if not autonomous:
        result.awaiting_answers = True
        return result

    page, report = story_stage.story(
        claims=claims, positioning=positioned, trends=trends_doc, llm=llm
    )
    target_story.parent.mkdir(parents=True, exist_ok=True)
    target_story.write_text(page, encoding="utf-8")
    result.report = report
    return result
