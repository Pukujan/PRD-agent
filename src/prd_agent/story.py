"""Draft the marketing story through the vendored copywriting skill, then gate it.

The model writes the pitch body only. The proof table, the open flags and the self-check
paragraph are assembled here from the stage JSON and the checker's report, so the page can
never claim more than the pipeline established. A draft that trips a hard ban is rewritten
from the facts; a draft still banned after MAX_REWRITES fails the run and writes nothing.
"""

from __future__ import annotations

import json
import re

from prd_agent import flags
from prd_agent.checks import FOOTER_HEADING, CheckReport, check_story
from prd_agent.errors import StoryGateError
from prd_agent.llm import LLM
from prd_agent.skill import build_skill_context

MAX_REWRITES = 2
_FENCE_WRAPPER = re.compile(r"^```[a-zA-Z]*\n(.*?)\n?```$", re.DOTALL)

STORY_SYSTEM = (
    "You are an expert conversion copywriter working from a positioning brief that was derived "
    "from the product's own artifact. You write the marketing page. Hype is uncapped: you are "
    "selling the reader's future, not inventorying the product. You never invent a fact the "
    "brief does not carry. You never write the proof section, the open flags or the self-check "
    "paragraph; the pipeline appends those. Follow the vendored copywriting skill and its "
    "references exactly, including its self-check, and return the page body as markdown only."
)

_PROMPT_TEMPLATE = """\
Write the marketing page body for this product.

Rules, in order of importance:
1. Sell the reader's future. The page is not an inventory of what the product does and does not
   do. Every section should make the reader want the state the product creates.
2. Write only what the brief and the claims support. Never invent a fact the brief does not carry:
   if a claim is not supported, leave it out rather than inventing it. Never state an `unknown`
   claim as fact.
3. Never contradict what the artifact is. A command line tool is never sold as a graphical app.
4. Hype is uncapped. Invented-sounding numbers are allowed unless they contradict the claims.
5. Do not write the footer ("### Proof and open items"), the proof table, the open flags or the
   self-check paragraph. Do not write the marker `[NEED:` anywhere in the body: the pipeline
   appends the flags it already holds. If a claim needs evidence, leave the claim out and it will
   stay flagged in the footer.
6. Structure: a hero (headline, subhead, one line of install or entry), then a problem section
   that names the reader's situation in the second person, then a section describing the better
   state, then a numbered path to action with at least three steps, then a closing call to
   action. Competitor positioning stays out of the pitch body.
7. Run the skill's own self-check before you answer. Banned patterns fail the gate and cost a
   rewrite: contrast reveals, negation lists, trailing pile-ons, self-answered questions, colon
   reveals, stock phrases, hype punctuation, and em dashes in headings or the hero.

The vendored skill and its references follow. Obey them.

{skill}

The positioning brief follows.

{positioning}

The claims, so you never contradict the artifact:

{claims}

The market stage and the competitor language, so you know how loud to go:

{trends}

{exemplars}
"""

def _bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)

def _exemplar_block(exemplars: list[dict]) -> str:
    if not exemplars:
        return "No worked examples are available yet. This is an early run."
    parts = [
        "Worked examples from earlier runs. Use their shape, their register and their level of "
        "specificity. Do not reuse their subject matter.",
    ]
    for exemplar in exemplars:
        story_text = str(exemplar.get("story", "")).strip()
        if story_text:
            parts.append(f"\n--- earlier story ---\n{story_text}")
    return "\n".join(parts)

def build_story_prompt(
    *,
    positioning: dict,
    claims: dict,
    trends: dict,
    exemplars: list[dict] = (),
) -> str:
    return _PROMPT_TEMPLATE.format(
        skill=build_skill_context(),
        positioning=json.dumps(positioning, indent=2, ensure_ascii=False),
        claims=json.dumps(claims, indent=2, ensure_ascii=False),
        trends=json.dumps(trends, indent=2, ensure_ascii=False),
        exemplars=_exemplar_block(list(exemplars)),
    )

def build_rewrite_prompt(
    *,
    body: str,
    report: CheckReport,
    positioning: dict,
    claims: dict,
) -> str:
    findings = report.bans + report.cap_violations()
    listed = _bullet_lines(
        [f"{finding.rule} (line {finding.line}, section {finding.section}): {finding.text.strip()}" for finding in findings]
    )
    return (
        "The draft below failed the copywriting skill's self-check. Rewrite the whole draft.\n\n"
        "Rewrite from the facts. Go back to the mechanism, the number and the reader, and write "
        "that. Swapping a banned phrase for a synonym produces a new tell. Keep every section, "
        "keep the numbered path to action, and keep the same structure.\n\n"
        "What failed:\n\n"
        f"{listed}\n\n"
        "The positioning brief, so the rewrite keeps the mechanism and the differentiator:\n\n"
        f"{json.dumps(positioning, indent=2, ensure_ascii=False)}\n\n"
        "The claims, so the rewrite stays inside what is established:\n\n"
        f"{json.dumps(claims, indent=2, ensure_ascii=False)}\n\n"
        "The draft to rewrite:\n\n"
        f"{body}\n"
    )

def clean_body(raw: str) -> tuple[str, list[dict]]:
    """Strip a fence wrapper and harvest any flag the model raised.

    The pitch body must not carry `[NEED: ...]` markers, because the footer is code-built. A
    model that raises one anyway is not punished: the marker is removed from the pitch and the
    flag joins the footer.
    """
    text = raw.strip()
    wrapped = _FENCE_WRAPPER.match(text)
    if wrapped:
        text = wrapped.group(1).strip()
    harvested: list[dict] = []

    def _harvest(match: re.Match[str]) -> str:
        need = match.group(1)
        if need in flags.NEED_KINDS:
            harvested.append(
                flags.make_flag(harvested, need, "Raised by the draft", "Evidence that resolves it.")
            )
        return ""

    text = flags.FLAG_PATTERN.sub(_harvest, text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, harvested

def build_proof_table(claims: dict) -> str:
    rows = ["| Claim on this page | Source | Status |", "|---|---|---|"]
    for claim in claims.get("claims", []):
        text = " ".join(str(claim.get("text", "")).split())
        if len(text) > 90:
            text = text[:87].rstrip() + "..."
        evidence = str(claim.get("evidence", "")).strip() or "none recorded"
        rows.append(f"| {text} | {evidence} | {claim.get('status', 'unknown')} |")
    for unknown in claims.get("unknowns", []):
        rows.append(f"| {' '.join(str(unknown).split())} | no source in the artifact | **unknown** |")
    return "\n".join(rows)

def build_trends_note(trends: dict) -> str:
    category = trends.get("category", {})
    stage = category.get("sophistication_stage", "unknown")
    note = category.get("stage_note", "")
    urls = [str(item.get("url", "")) for item in category.get("competitors", []) if item.get("url")]
    urls.extend(str(item.get("url", "")) for item in trends.get("cultural", []) if item.get("url"))
    unique = list(dict.fromkeys(urls))
    lines = [f"**Trends used.** Market stage: {stage} (Schwartz). {note}".rstrip()]
    if unique:
        lines.append("Sources read for the category register and the cultural moment: " + ", ".join(unique) + ".")
    searched_at = str(trends.get("searched_at", "")).strip()
    if searched_at:
        lines.append(f"Searched at {searched_at}.")
    return "\n\n".join(lines)

def _render_flags_in_footer(merged: list[dict]) -> str:
    rendered = flags.render_flags(merged)
    if not merged or rendered == flags.NO_FLAGS_LINE:
        return rendered
    lines = rendered.splitlines()
    flag_lines = []
    flag_idx = 0
    for line in lines:
        if line.startswith("- `[NEED:") and flag_idx < len(merged):
            flag_id = merged[flag_idx].get("id")
            if flag_id and flag_id not in line:
                line = f"{line} [{flag_id}]"
            flag_idx += 1
        flag_lines.append(line)
    return "\n".join(flag_lines)

def build_footer(
    *,
    claims: dict,
    positioning: dict,
    trends: dict,
    report: CheckReport,
    extra_flags: list[dict] = (),
) -> str:
    merged = flags.merge_flags(list(positioning.get("flags", [])), list(extra_flags))
    swap = positioning.get("swap_test", {})
    verdict = "Passed" if swap.get("passed") else "Failed"
    lines = [
        FOOTER_HEADING,
        "",
        "Not part of the pitch above. Recorded here so the page can be audited without being flattened by it.",
        "",
        build_proof_table(claims),
        "",
        f"**Swap test.** {verdict}. {swap.get('note', '')}".rstrip(),
        "",
        _render_flags_in_footer(merged),
        "",
        build_trends_note(trends),
        "",
        report.summary(),
    ]
    return "\n".join(lines).strip() + "\n"

def assemble_story(body: str, footer: str) -> str:
    return f"{body.strip()}\n\n---\n\n{footer.strip()}\n"

def story(
    *,
    claims: dict,
    positioning: dict,
    trends: dict,
    llm: LLM,
    exemplars: list[dict] = (),
    max_rewrites: int = MAX_REWRITES,
) -> tuple[str, CheckReport]:
    """Draft, gate, rewrite, and return (whole page, report of the accepted draft)."""
    body = ""
    report: CheckReport | None = None
    harvested: list[dict] = []
    for attempt in range(max_rewrites + 1):
        if attempt == 0:
            prompt = build_story_prompt(
                positioning=positioning, claims=claims, trends=trends, exemplars=list(exemplars)
            )
        else:
            assert report is not None
            prompt = build_rewrite_prompt(body=body, report=report, positioning=positioning, claims=claims)
        body, harvested = clean_body(llm.complete(system=STORY_SYSTEM, prompt=prompt))
        report = check_story(body)
        if report.passed():
            footer = build_footer(
                claims=claims,
                positioning=positioning,
                trends=trends,
                report=report,
                extra_flags=harvested,
            )
            return assemble_story(body, footer), report
    assert report is not None
    failed = ", ".join(sorted({finding.rule for finding in report.bans + report.cap_violations()}))
    raise StoryGateError(
        f"the draft still trips the self-check after {max_rewrites + 1} drafts: {failed}. "
        "Nothing was written. The findings are listed above; rewrite from the facts and re-run."
    )
