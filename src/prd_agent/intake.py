"""Turn an artifact into claims.json: what is pointed at, what the artifact asserts, what is not established.

Spec section 3.1. The stage never invents a plausible mechanism: an unread fact becomes an
`unknown` entry, and every claim carries the path, line or commit that supports it.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from prd_agent.artifact import Artifact, collect_artifact, render_artifact
from prd_agent.errors import ModelOutputError
from prd_agent.llm import LLM, extract_json
from prd_agent.schemas import CLAIMS_SCHEMA, CLAIMS_SPEC, require_valid

INTAKE_SYSTEM = (
    "You read a builder's own artifact and report only what it establishes. You never invent "
    "a mechanism, a number, a customer or a benchmark. When something is not established you "
    "record it as unknown instead of guessing. You answer with JSON and nothing else."
)

_PROMPT_TEMPLATE = """\
Read the artifact excerpt below and produce its claims document.

Rules, in order of importance:
1. Never invent a mechanism. If the excerpt does not establish how something works, it is an
   `unknown`, not a claim.
2. `verified` means the excerpt points at it (a file, a line, a test, a commit).
   `claimed` means the artifact's own prose asserts it but nothing points at it.
   `unknown` means it is not established at all.
3. `evidence` is a path, a path with a line number, or a commit sha. Leave it empty for
   `unknown` and say what would settle it in `note`.
4. A note may name a place the artifact overstates itself. Record the overstatement as it is
   written, and say in the note where it diverges.
5. List every fact a reader of a marketing page would want and the artifact does not settle,
   in `unknowns`.

Answer with exactly this JSON object and no prose around it:

{schema}

Artifact excerpt follows.

{excerpt}
"""


def build_intake_prompt(artifact: Artifact) -> str:
    schema = (
        '{"schema": "prd-agent.claims.v1", '
        '"artifact": {"name": "", "path": "", "commit": "", "read_at": ""}, '
        '"claims": [{"id": "C-001", "text": "", "status": "verified|claimed|unknown", '
        '"evidence": "path:line or commit sha", "note": ""}], '
        '"unknowns": [""]}'
    )
    return _PROMPT_TEMPLATE.format(schema=schema, excerpt=render_artifact(artifact))


def intake(root: Path, llm: LLM, *, artifact: Artifact | None = None) -> dict:
    """Read the artifact and return a validated claims document."""
    collected = artifact if artifact is not None else collect_artifact(Path(root))
    raw = llm.complete(system=INTAKE_SYSTEM, prompt=build_intake_prompt(collected))
    doc = extract_json(raw)
    if not isinstance(doc, dict):
        raise ModelOutputError("the intake reply was not a JSON object")
    doc.setdefault("schema", CLAIMS_SCHEMA)
    doc["artifact"] = {
        "name": collected.name,
        "path": str(collected.root),
        "commit": collected.commit,
        "read_at": collected.read_at or date.today().isoformat(),
    }
    doc.setdefault("claims", [])
    doc.setdefault("unknowns", [])
    for index, claim in enumerate(doc["claims"], start=1):
        claim.setdefault("id", f"C-{index:03d}")
        claim.setdefault("evidence", "")
        claim.setdefault("note", "")
    require_valid(doc, CLAIMS_SPEC, "claims.json")
    return doc
