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
_DIVIDER = re.compile(r"^\s*[-*_]{3,}\s*$")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_BOLD_QUESTION = re.compile(r"^\s*\*\*.+\?\*\*")
_EM_DASH = re.compile(r"[\u2014\u2013]")
AUDIT_JARGON = re.compile(r"(?i)\b(?:proof table|audit trail|compliance report|verification status|evidence:\s*|status:\s*(?:verified|claimed|unknown))\b")
INTERNAL_PATH = re.compile(r"\b(?:modules|src|tests|\.github)\/[A-Za-z0-9_\-\.\/]+")
FEATURE_BEFORE_STORY = re.compile(r"(?i)\b(?:features?:|key features|feature list|under the hood|technical architecture|implementation details)\b")
_HYPE = re.compile(r"!|\?!")
_EMOJI_LEAD = re.compile(r"^\s*(?:[-*+]\s+|\#{1,6}\s+)[\U0001F300-\U0001FAFF\u2600-\u27BF]")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[A-Za-z][A-Za-z'\-]*")
META_LABEL_PATTERN = re.compile(
    r"(?i)\b(?:level\s*(?:1000|750|500|250)|solopreneur\s*,\s*belief\s+inversion|belief\s+inversion\s*:|beat\s*[1-5]\s*:)\b"
)
TEMPLATE_OPENER_PATTERN = re.compile(
    r"(?i)\b(?:the\s+false\s+dogma\s+says|the\s+cultural\s+enemy\s+is|the\s+rebellion\s+belief\s+is)\b"
)

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

CAP_LIMITS = {"fragment": 1, "reflexive_three": 1, "cap_vocabulary": 1, "em_dash_long": 1}
CAP_WORDS = frozenset(
    {
        "seamless", "robust", "streamline", "empower", "elevate", "unlock", "unleash", "harness",
        "foster", "enhance", "optimize", "cutting-edge", "innovative", "revolutionary",
        "transformative", "holistic", "comprehensive", "pivotal", "crucial", "vital", "powerful",
        "next-level", "world-class", "best-in-class", "landscape", "navigate", "ecosystem",
        "journey", "supercharge", "turbocharge",
    }
)
INTENSIFIERS = frozenset(
    {"truly", "genuinely", "incredibly", "deeply", "fundamentally", "significantly", "simply",
     "actually", "literally", "quietly"}
)
REFLEXIVE_THREE = re.compile(r"(?i)\b(\w+),\s+(\w+),?\s+and\s+(\w+)[.!?\n]")
FALSE_RANGE = re.compile(r"(?i)\bfrom\s+[a-z]+\s+to\s+[a-z]+\b")
ORDERED_ITEM = re.compile(r"^\s*(?:#{1,6}\s+)?\d+[.)]\s+")


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
        """The cap findings past their limit, counted per rule per section."""
        counts: dict[tuple[str, str], list[Finding]] = {}
        for finding in self.caps:
            counts.setdefault((finding.rule, finding.section), []).append(finding)
        violations: list[Finding] = []
        for (rule, _section), items in counts.items():
            limit = CAP_LIMITS.get(rule, 0)
            if len(items) > limit:
                violations.extend(items[limit:])
        return tuple(violations)

    def summary(self) -> str:
        counts = {rule: 0 for rule in ("contrast_reveal", "negation_list", "trailing_pile_on",
                                       "self_answered_question", "colon_reveal", "stock_phrase",
                                       "banned_vocabulary", "hype_punctuation", "em_dash_short")}
        for finding in self.findings:
            counts[finding.rule] = counts.get(finding.rule, 0) + 1
        bans = len(self.bans)
        caps = {rule: 0 for rule in CAP_LIMITS}
        for finding in self.caps:
            caps[finding.rule] = caps.get(finding.rule, 0) + 1
        caps_text = ", ".join(f"{rule} {caps[rule]}/{CAP_LIMITS[rule]}" for rule in CAP_LIMITS)
        return (
            f"**Self-check.** Run by `prd_agent.checks` against the vendored `copywriting` skill's "
            f"`references/ai-tells.md`. {bans} hard bans in {len(self.sections)} sections "
            f"(contrast reveals {counts['contrast_reveal']}, negation lists {counts['negation_list']}, "
            f"trailing pile-ons {counts['trailing_pile_on']}, self-answered questions "
            f"{counts['self_answered_question']}, colon reveals {counts['colon_reveal']}, stock phrases "
            f"{counts['stock_phrase']}, banned words {counts['banned_vocabulary']}, hype punctuation "
            f"{counts['hype_punctuation']}, em dashes in short copy {counts['em_dash_short']}). "
            f"Frequency caps, counted per section: {caps_text}. Structural beats present: discomfort, "
            f"vision, path. {self.limitations()}"
        )

    def limitations(self) -> str:
        return (
            "What this check cannot decide: whether the story lands, whether a sentence that avoids "
            "every rule is still empty, and any tell written in a shape no rule here matches. That "
            "judgment is the owner's."
        )

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


def has_ascii_em_dash(text: str) -> bool:
    """Detect ASCII double-hyphen em dashes (--) in prose, ignoring inline code and CLI flags."""
    clean = re.sub(r"`[^`]*`", "", text)
    if _DIVIDER.match(clean):
        return False
    for m in re.finditer(r"(?<!-)--(?!-)", clean):
        start, end = m.start(), m.end()
        before = clean[:start]
        after = clean[end:]
        if (not before or before[-1].isspace() or before[-1] in "('\"") and after and after[0].isalpha():
            continue
        return True
    return False


def _prose_lines(section: Section) -> list[tuple[int, str]]:
    """The lines a tell can live on: no fences, no table rows, no fenced content."""
    out: list[tuple[int, str]] = []
    in_fence = False
    for offset, line in enumerate(section.text.splitlines()):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or _TABLE_ROW.match(line) or _DIVIDER.match(line):
            continue
        out.append((section.start_line + offset, line))
    return out


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_SPLIT.split(text.strip()) if part.strip()]


def _check_prose(section: Section, is_problem: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    for line, raw in _prose_lines(section):
        text = raw.strip()
        if not text:
            continue
        stripped = _HEADING.sub(r"\2", text).replace("**", "").strip()
        is_bold_question = bool(_BOLD_QUESTION.match(text))
        is_short = section.name == "hero" or bool(_HEADING.match(text))
        if is_short and (_EM_DASH.search(text) or has_ascii_em_dash(text)):
            findings.append(Finding("em_dash_short", BAN, section.name, line, text,
                                    "em dashes are banned in headings and the hero"))
        elif has_ascii_em_dash(text):
            findings.append(Finding("ascii_em_dash", BAN, section.name, line, text,
                                    "double-hyphen em dashes (--) are banned; use periods or commas"))
        if AUDIT_JARGON.search(text):
            findings.append(Finding("audit_jargon", BAN, section.name, line, text,
                                    "audit terminology is banned from marketing copy"))
        if META_LABEL_PATTERN.search(text):
            findings.append(Finding("meta_label_leakage", BAN, section.name, line, text,
                                    "meta-prompt labels are forbidden in customer-facing copy"))
        if TEMPLATE_OPENER_PATTERN.search(text):
            findings.append(Finding("template_opener", BAN, section.name, line, text,
                                    "formulaic template openers are forbidden; attack the status quo directly"))
        if INTERNAL_PATH.search(text):
            findings.append(Finding("code_path_in_prose", BAN, section.name, line, text,
                                    "internal file paths are banned from marketing copy"))
        if is_problem and FEATURE_BEFORE_STORY.search(text):
            findings.append(Finding("feature_before_story", BAN, section.name, line, text,
                                    "story and human nightmare must come before features and technical architecture"))
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


def _check_caps(section: Section) -> list[Finding]:
    """The frequency caps and the review-only findings for one section."""
    findings: list[Finding] = []

    for line, raw in _prose_lines(section):
        text = raw.strip()
        if not text or _HEADING.match(text):
            continue
        if section.name != "hero" and _EM_DASH.search(text):
            findings.append(Finding("em_dash_long", CAP, section.name, line, text, "one em dash per section"))
        if REFLEXIVE_THREE.search(text):
            findings.append(Finding("reflexive_three", CAP, section.name, line, text, "one three-item list per section"))
        if FALSE_RANGE.search(text):
            findings.append(Finding("false_range", REVIEW, section.name, line, text, "a range whose ends do not span"))

    paragraphs = [block.strip() for block in section.text.split("\n\n") if block.strip()]
    for paragraph in paragraphs:
        if _HEADING.match(paragraph):
            continue
        words = _WORD.findall(paragraph)
        if words and len(words) <= 2 and not any(w.lower() in COMMON_VERBS for w in words):
            findings.append(Finding("fragment", CAP, section.name, section.start_line, paragraph, "one fragment per section"))
        has_cap = any(word.lower() in CAP_WORDS for word in words)
        intensifiers = sum(1 for word in words if word.lower() in INTENSIFIERS)
        if has_cap or intensifiers >= 2:
            findings.append(Finding("cap_vocabulary", CAP, section.name, section.start_line, paragraph[:120],
                                    "cap vocabulary in paragraph"))

    for line, raw in _prose_lines(section):
        text = raw.strip()
        if not text:
            continue
        for sentence in _sentences(text):
            word_count = len(_WORD.findall(sentence))
            if word_count > 20:
                findings.append(Finding("long_sentence", REVIEW, section.name, line, sentence,
                                        f"{word_count} words, read it aloud"))
    return findings


def check_beats(body: str) -> list[Finding]:
    """The three structural beats of the Human Action Model, as far as they are mechanical.

    discomfort: the first `## ` section names the reader's situation in their own terms.
    vision: a second `## ` section says what the better state looks like.
    path: a later section carries the ordered steps that get there.
    """
    sections = split_sections(body)
    if not sections or sections[0].name != "hero" or not sections[0].text.startswith("# "):
        return []

    findings: list[Finding] = []
    body_sections = [section for section in sections if section.name != "hero"]
    first_line = sections[0].start_line if sections else 1

    if not body_sections:
        return [
            Finding("beat_discomfort", BAN, "hero", first_line, "", "no problem section at all"),
            Finding("beat_vision", BAN, "hero", first_line, "", "there is no second section to carry the vision"),
            Finding("beat_path", BAN, "hero", first_line, "", "found 0 ordered steps; the path to action needs at least 3"),
        ]

    discomfort = body_sections[0]
    discomfort_text = discomfort.text
    has_second_person = bool(re.search(r"(?i)\b(?:you|your|you're)\b", discomfort_text))
    enough_prose = len(_sentences(discomfort_text)) >= 2
    if not (has_second_person and enough_prose):
        findings.append(Finding("beat_discomfort", BAN, discomfort.name, discomfort.start_line, discomfort_text,
                                "the first section does not name the reader's situation"))
    if len(body_sections) < 2:
        findings.append(Finding("beat_vision", BAN, discomfort.name, discomfort.start_line, "",
                                "there is no second section to carry the vision"))
    else:
        vision = body_sections[1]
        if len(_sentences(vision.text)) < 2:
            findings.append(Finding("beat_vision", BAN, vision.name, vision.start_line, vision.text,
                                    "the second section does not describe the better state"))

    ordered = 0
    for section in body_sections[1:]:
        ordered += sum(1 for line in section.text.splitlines() if ORDERED_ITEM.match(line))
    if ordered < 3:
        findings.append(Finding("beat_path", BAN, body_sections[-1].name, body_sections[-1].start_line, "",
                                f"found {ordered} ordered steps; the path to action needs at least 3"))
    return findings


def check_story(body: str) -> CheckReport:
    """Run every rule over the pitch body and return the report."""
    body, _ = split_body_footer(body)
    sections = split_sections(body)
    findings: list[Finding] = []
    body_sections = [s for s in sections if s.name != "hero"]
    discomfort_name = body_sections[0].name if body_sections else None
    for section in sections:
        findings.extend(_check_prose(section, is_problem=(section.name == "hero" or section.name == discomfort_name)))
        findings.extend(_check_caps(section))
    findings.extend(check_beats(body))
    return CheckReport(findings=tuple(findings), sections=tuple(sections))
