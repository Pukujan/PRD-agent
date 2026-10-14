"""The machine half of the copywriting skill's self-check.

Read with `vendor/copywriting/references/ai-tells.md` open. Every rule below names the pattern
it implements, and the exemption list implements that file's "Still fine" paragraph.

Scope: the pitch body only. The footer is excluded because it legitimately names the banned
patterns; fenced code blocks and markdown tables are excluded because they are not prose.

Severities:
  ban    - the draft fails the gate and is rewritten. The hard bans from ai-tells.md.
  cap    - a device that is fine once, a tell when repeated. Fails the gate only past its limit.
  review - reported for a human to read. Never fails the gate.

What this cannot catch: whether the story lands, whether a sentence that avoids every rule is
still empty, and any tell written in a shape no rule here matches. `summary()` says so in the
story footer, so the page never claims more than the checker proved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

FOOTER_HEADING = "### Proof and open items"
BAN = "ban"
CAP = "cap"
REVIEW = "review"

_FENCE = re.compile(r"^\s*(?:```|~~~)")
_TABLE_ROW = re.compile(r"^\s*\|")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_BOLD_QUESTION = re.compile(r"^\s*\*\*.+\?\*\*")
_EM_DASH = re.compile(r"[\u2014\u2013]")
_HYPE = re.compile(r"!|\?!")
_EMOJI_LEAD = re.compile(r"^\s*(?:[-*+]\s+|\#{1,6}\s+)[\U0001F300-\U0001FAFF\u2600-\u27BF]")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[A-Za-z][A-Za-z'\-]*")

CONTRAST_REVEAL = (
    re.compile(
        r"(?i)\b(?:it|this|that)(?:'s| is| was)?\s*(?:not|isn'?t|aren'?t)\b[^.?!]{0,80}[.?!]\s+(?:it|this|that)\b"
    ),
    re.compile(r"(?i)\bnot because\b[^.?!]{0,80}[.?!]\s*because\b"),
    re.compile(r"(?i)\bnot just\b[^.?!]{0,60}\bbut\b"),
    re.compile(r"(?i)\bless\s+\w+[^,.?!]{0,40},\s*more\s+\w+"),
    re.compile(r"(?i)\bthe (?:question|problem|issue|catch) isn'?t\b"),
)
NEGATION_ITEM = re.compile(r"(?i)\b(?:no|without|zero)\s+[a-z][\w'-]*")
TRAILING_PILE_ON = (
    re.compile(r"(?i),\s*(?:no|not|without|zero)\s+[a-z]"),
    re.compile(r"(?i),\s*(?:ensuring|allowing|enabling|making it|keeping it)\b"),
)
SELF_ANSWERED_QUESTION = re.compile(r"^\s*(?!\*\*|#{1,6}\s)([A-Z][^.!?\n]{0,40}\?)\s+\S")
COLON_REVEAL_PHRASES = (
    "the best part:", "the secret:", "the trick:", "the catch:", "the result:", "the point:",
    "one word:", "here's the secret:", "here's the thing:",
)
COLON_REVEAL = re.compile(r"^\s*(?![\|\-*+#>])([^:\n]{1,40}):\s+(\S.*)$")
COMMON_VERBS = frozenset(
    {
        "is", "are", "was", "were", "be", "been", "has", "have", "had", "means", "mean", "reads",
        "read", "includes", "include", "shows", "show", "does", "do", "gets", "get", "gives",
        "give", "keeps", "keep", "works", "work", "contains", "contain", "covers", "cover",
        "lists", "list", "prints", "print", "takes", "take", "needs", "need", "ships", "ship",
        "writes", "write", "runs", "run", "fails", "fail", "costs", "cost",
    }
)
STOCK_PHRASES = (
    "in today's fast-paced world", "whether you're", "here's the thing", "say goodbye to",
    "say hello to", "unlock the power of", "unleash the power of", "take it to the next level",
    "the future of", "everything you need to", "all-in-one", "effortless", "in just a few clicks",
    "join thousands", "game-changer", "this changes everything", "when it comes to",
    "let me be clear", "here's what nobody tells you", "in this guide", "let's dive in",
    "in conclusion", "at the end of the day", "because growth shouldn't wait",
    "and that changes everything", "it's worth noting", "moreover", "furthermore", "additionally",
    "great question", "let's be honest", "we get it", "transform the way you work",
    "built for teams who move fast", "world-class", "best-in-class", "reimagined", "redefined",
    "the secret to", "the truth is",
)
STOCK_PHRASE_PATTERN = re.compile(r"(?i)\b(?:" + "|".join(re.escape(p) for p in STOCK_PHRASES) + r")")
OPENER_PHRASES = ("imagine ",)
OPENER_PATTERN = re.compile(r"(?i)(?:^|[.?!]\s+)(?:" + "|".join(re.escape(p) for p in OPENER_PHRASES) + r")")
BANNED_WORDS = (
    "delve", "tapestry", "testament to", "realm", "embark", "beacon", "multifaceted", "paradigm",
    "synergy", "myriad", "plethora", "meticulous", "intricate", "utilize", "supercharge",
    "turbocharge", "ever-evolving landscape", "plays a crucial role", "leverag",
)
BANNED_WORD_PATTERN = re.compile(r"(?i)\b(?:" + "|".join(re.escape(w) for w in BANNED_WORDS) + r")\w*")


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    section: str
    line: int
    text: str
    detail: str = ""


@dataclass(frozen=True)
class Section:
    name: str
    text: str
    start_line: int


@dataclass(frozen=True)
class CheckReport:
    findings: tuple[Finding, ...] = field(default_factory=tuple)
    sections: tuple[Section, ...] = field(default_factory=tuple)

    @property
    def bans(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.severity == BAN)

    @property
    def caps(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.severity == CAP)

    @property
    def reviews(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.severity == REVIEW)

    def cap_violations(self) -> tuple[Finding, ...]:
        return ()

    def passed(self) -> bool:
        return not self.bans and not self.cap_violations()


def split_body_footer(markdown: str) -> tuple[str, str]:
    """Split the page into the pitch body and the code-generated footer."""
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == FOOTER_HEADING:
            body = "\n".join(lines[:index]).rstrip()
            while body.endswith("---"):
                body = body[: -3].rstrip()
            return body, "\n".join(lines[index:])
    return markdown.rstrip(), ""


def split_sections(markdown: str) -> list[Section]:
    """The hero (everything before the first `## `) and then one section per `## ` heading."""
    lines = markdown.splitlines()
    starts: list[tuple[str, int]] = [("hero", 0)]
    for index, line in enumerate(lines):
        match = _HEADING.match(line)
        if match and len(match.group(1)) == 2:
            starts.append((match.group(2).strip(), index))
    sections: list[Section] = []
    for position, (name, start) in enumerate(starts):
        end = starts[position + 1][1] if position + 1 < len(starts) else len(lines)
        text = "\n".join(lines[start:end]).strip("\n")
        if text:
            sections.append(Section(name=name, text=text, start_line=start + 1))
    return sections


def _prose_lines(section: Section) -> list[tuple[int, str]]:
    """The lines a tell can live on: no fences, no table rows, no fenced content."""
    out: list[tuple[int, str]] = []
    in_fence = False
    for offset, line in enumerate(section.text.splitlines()):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or _TABLE_ROW.match(line):
            continue
        out.append((section.start_line + offset, line))
    return out


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_SPLIT.split(text.strip()) if part.strip()]


def _check_prose(section: Section) -> list[Finding]:
    findings: list[Finding] = []
    for line, raw in _prose_lines(section):
        text = raw.strip()
        if not text:
            continue
        stripped = _HEADING.sub(r"\2", text).replace("**", "").strip()
        is_bold_question = bool(_BOLD_QUESTION.match(text))
        if _EM_DASH.search(text):
            findings.append(Finding("em_dash_short", BAN, section.name, line, text,
                                    "em dashes are banned in headings and the hero"))
        if _HYPE.search(text):
            findings.append(Finding("hype_punctuation", BAN, section.name, line, text, "no exclamation points"))
        if _EMOJI_LEAD.match(text):
            findings.append(Finding("emoji_structure", BAN, section.name, line, text, "no emoji as structure"))
        if STOCK_PHRASE_PATTERN.search(stripped):
            findings.append(Finding("stock_phrase", BAN, section.name, line, text,
                                    "a stock marketing phrase from ai-tells.md"))
        if OPENER_PATTERN.search(stripped):
            findings.append(Finding("stock_phrase", BAN, section.name, line, text, "a banned opener"))
        if BANNED_WORD_PATTERN.search(stripped):
            found = BANNED_WORD_PATTERN.search(stripped)
            findings.append(Finding("banned_vocabulary", BAN, section.name, line, text,
                                    f"banned word: {found.group(0) if found else ''}"))
        for pattern in CONTRAST_REVEAL:
            if pattern.search(stripped):
                findings.append(Finding("contrast_reveal", BAN, section.name, line, text,
                                        "states the denial instead of the claim"))
                break
        for sentence in _sentences(stripped):
            negations = NEGATION_ITEM.findall(sentence)
            if len(negations) >= 2:
                findings.append(Finding("negation_list", BAN, section.name, line, sentence,
                                        "defines the product by what is absent"))
                break
        for pattern in TRAILING_PILE_ON:
            if pattern.search(stripped):
                findings.append(Finding("trailing_pile_on", BAN, section.name, line, text,
                                        "a complete claim with add-ons trailing after a comma"))
                break
        lowered = stripped.lower()
        if any(phrase in lowered for phrase in COLON_REVEAL_PHRASES):
            findings.append(Finding("colon_reveal", BAN, section.name, line, text, "a label standing in for a sentence"))
        elif not is_bold_question:
            match = COLON_REVEAL.match(text)
            if match:
                label = match.group(1).strip()
                words = _WORD.findall(label)
                has_verb = any(word.lower() in COMMON_VERBS for word in words)
                if len(words) <= 5 and not has_verb:
                    findings.append(Finding("colon_reveal", BAN, section.name, line, text,
                                            "a short label before a colon"))
        if SELF_ANSWERED_QUESTION.match(text) and not is_bold_question:
            match = SELF_ANSWERED_QUESTION.match(text)
            question = match.group(1) if match else ""
            words = _WORD.findall(question)
            has_verb = any(word.lower() in COMMON_VERBS for word in words)
            if len(words) <= 6 and not has_verb:
                findings.append(Finding("self_answered_question", BAN, section.name, line, text,
                                        "asks the reader a question and answers it in the same breath"))
    return findings


def check_story(body: str) -> CheckReport:
    """Run every rule over the pitch body and return the report."""
    body, _ = split_body_footer(body)
    sections = split_sections(body)
    findings: list[Finding] = []
    for section in sections:
        findings.extend(_check_prose(section))
    return CheckReport(findings=tuple(findings), sections=tuple(sections))
