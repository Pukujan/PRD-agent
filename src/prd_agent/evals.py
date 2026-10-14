"""Append every finished story as a worked example, and retrieve the closest ones next run.

Run one uses a template; run fifty uses fifty real stories. Retrieval is deterministic keyword
overlap over one small JSON file: no embeddings, no vector store, no corpus infrastructure. The
semantic-corpus seam is documented in docs/CORPUS_SEAM.md and deliberately not built.
"""

from __future__ import annotations

import json
from pathlib import Path

from prd_agent.checks import CheckReport, split_body_footer
from prd_agent.errors import StageError
from prd_agent.positioning import content_words

EVALS_PATH = Path("evals") / "story_evals.json"
EVAL_SCHEMA = "prd-agent.story-eval.v1"
SKILL_NAME = "copywriting"
DEFAULT_LIMIT = 2

def load_evals(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        return {"skill_name": SKILL_NAME, "evals": []}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StageError(f"{path} is not readable JSON: {exc}") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("evals"), list):
        raise StageError(f"{path} must be an object with an 'evals' list")
    doc.setdefault("skill_name", SKILL_NAME)
    return doc

def next_id(evals: dict) -> int:
    highest = 0
    for item in evals.get("evals", []):
        try:
            highest = max(highest, int(item.get("id", 0)))
        except (TypeError, ValueError):
            continue
    return highest + 1

def build_assertions(*, report: CheckReport, positioning: dict, body: str) -> list[str]:
    """The assertions a later run should be able to check on a new story."""
    return [
        "The hero states the transformation, and the page carries the three beats in order: "
        "discomfort, then vision, then path.",
        "Every claim on the page traces to a claim marked verified or claimed in claims.json.",
        "no contrast reveal, negation list, trailing pile-on, self-answered question, colon reveal, "
        "stock phrase or em dash in short copy appears in the pitch body.",
        "the differentiator survives the swap test against the named competitors.",
        f"The page leads with the mechanism: {positioning.get('differentiator', '')}",
        f"Market stage used: {positioning.get('swap_test', {}).get('passed', False)} "
        f"swap test verdict recorded, and the sophistication stage named in the footer.",
        f"The pitch body runs {len(report.sections)} sections and reports "
        f"{len(report.bans)} hard bans and {len(report.cap_violations())} cap violations.",
        "The proof table and the open flags are present in the footer and were not written by the model.",
    ]

def build_eval(
    *,
    task_name: str,
    artifact_name: str,
    positioning: dict,
    page: str,
    report: CheckReport,
) -> dict:
    body, _footer = split_body_footer(page)
    prompt = (
        "Write the marketing page body for "
        f"{artifact_name}. The differentiator is: {positioning.get('differentiator', '')} "
        "The audience is: "
        f"{positioning.get('audience', {}).get('who', '')} "
        "Do not write the proof table, the open flags or the self-check paragraph."
    )
    return {
        "id": 0,
        "prompt": prompt,
        "expected_output": body.strip(),
        "assertions": build_assertions(report=report, positioning=positioning, body=body),
        "files": [],
        "task": task_name,
        "artifact": artifact_name,
    }

def append_eval(path: Path, record: dict) -> dict:
    """Give the record the next id and append it. Returns the stored record."""
    path = Path(path)
    corpus = load_evals(path)
    record = dict(record)
    record["id"] = next_id(corpus)
    corpus["evals"].append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(corpus, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record

def score(candidate: str, exemplar: dict) -> int:
    """How many content words the candidate shares with an earlier example's prompt."""
    return len(content_words(candidate) & content_words(str(exemplar.get("prompt", ""))))

def select_exemplars(evals: dict, *, positioning: dict, limit: int = DEFAULT_LIMIT) -> list[dict]:
    """The closest earlier stories, newest first when two score the same."""
    candidate = " ".join(
        [
            str(positioning.get("differentiator", "")),
            str(positioning.get("audience", {}).get("who", "")),
            str(positioning.get("discomfort", "")),
            str(positioning.get("vision", "")),
        ]
    )
    ranked: list[tuple[int, int, dict]] = []
    for item in evals.get("evals", []):
        try:
            identifier = int(item.get("id", 0))
        except (TypeError, ValueError):
            identifier = 0
        ranked.append((score(candidate, item), identifier, item))
    ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
    picked: list[dict] = []
    for points, identifier, item in ranked[:limit]:
        if points == 0:
            break
        picked.append({"id": identifier, "score": points, "story": str(item.get("expected_output", ""))})
    return picked

def exemplars_as_prompt(exemplars: list[dict]) -> str:
    """The block `story.build_story_prompt` accepts. Empty string when there is nothing to show."""
    if not exemplars:
        return ""
    parts = [
        "Worked examples from earlier runs. Use their shape, their register and their level of "
        "specificity. Do not reuse their subject matter.",
    ]
    for exemplar in exemplars:
        story_text = str(exemplar.get("story", "")).strip()
        if story_text:
            parts.append(f"\n--- worked example {exemplar.get('id', '')} ---\n{story_text}")
    return "\n".join(parts)
