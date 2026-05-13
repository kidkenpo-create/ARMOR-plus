from __future__ import annotations

import re

from armor_types import Classification, QuestionType


CITATION_RE = re.compile(
    r"\b(?:FAR|DFARS|RFO FAR|DFARS RFO)?\s*(?:\d{1,3}\.\d{3}(?:-\d+)?(?:\([a-z0-9ivx]+\))*|\d{3}\.\d{3}(?:-\d+)?(?:\([a-z0-9ivx]+\))*|(?:52|252)\.\d{3}-\d+)\b",
    re.IGNORECASE,
)
PART_RE = re.compile(r"\b(?:part|subpart)\s+(\d{1,3})(?:\b|\.)", re.IGNORECASE)
DOLLAR_RE = re.compile(r"\$\s*([0-9][0-9,]*(?:\.\d+)?)")


def classify_question(question: str, default_dod: bool = True) -> Classification:
    text = question.strip()
    lower = text.lower()

    named_citations = _named_citations(text)
    likely_parts = _likely_parts(text, named_citations)
    dollar_amounts = _dollar_amounts(text)
    qtype = _question_type(lower, named_citations, dollar_amounts)

    names_clause = any(c.startswith("52.") or c.startswith("252.") for c in named_citations)
    requires_clause_text = qtype == "clause_content"
    requires_prescription = qtype == "clause_applicability" or (
        names_clause and qtype != "clause_content"
    )
    requires_dfars_check = default_dod or "dfars" in lower or any(p.startswith("2") for p in likely_parts)
    requires_deviation_check = (
        requires_dfars_check
        or names_clause
        or "deviation" in lower
        or "class deviation" in lower
        or "in lieu of" in lower
    )
    requires_conventions_check = bool(dollar_amounts) or any(
        token in lower
        for token in (
            "threshold",
            "delegate",
            "delegation",
            "existing solicitation",
            "who is responsible",
            "responsible",
        )
    )

    return Classification(
        question_type=qtype,
        named_citations=named_citations,
        likely_parts=likely_parts,
        dollar_amounts=dollar_amounts,
        requires_dfars_check=requires_dfars_check,
        requires_deviation_check=requires_deviation_check,
        requires_clause_text=requires_clause_text,
        requires_prescription=requires_prescription,
        requires_conventions_check=requires_conventions_check,
        is_dod=default_dod,
    )


def _question_type(lower: str, citations: list[str], dollar_amounts: list[float]) -> QuestionType:
    if "class deviation" in lower or "deviation" in lower or "in lieu of" in lower:
        return "deviation"
    if dollar_amounts or "threshold" in lower or "micro-purchase" in lower:
        return "threshold"
    if any(word in lower for word in ("define", "definition", "what is", "what does")):
        return "definition"
    if any(word in lower for word in ("deadline", "days", "date", "when must", "by when")):
        return "deadline"
    if any(word in lower for word in ("exception", "excluded", "does not apply", "exempt")):
        return "exception"
    if any(word in lower for word in ("who is responsible", "responsible", "authority", "delegate")):
        return "role_responsibility"
    if any(word in lower for word in ("buy american", "domestic", "country of origin", "foreign")):
        return "domestic_preference"
    if "subcontracting plan" in lower:
        return "subcontracting_plan"
    if any(c.startswith("52.") or c.startswith("252.") for c in citations):
        if any(word in lower for word in ("say", "text", "content", "what does", "meaning")):
            return "clause_content"
        return "clause_applicability"
    if any(word in lower for word in ("apply", "applicable", "covered", "required", "include")):
        return "clause_applicability"
    if any(word in lower for word in ("shall", "must", "steps", "process", "how do")):
        return "procedure"
    return "other"


def _named_citations(text: str) -> list[str]:
    citations: list[str] = []
    for match in CITATION_RE.findall(text):
        normalized = re.sub(r"^(?:FAR|DFARS|RFO FAR|DFARS RFO)\s+", "", match.strip(), flags=re.I)
        normalized = re.sub(r"\s+", "", normalized)
        if normalized not in citations:
            citations.append(normalized)
    return citations


def _likely_parts(text: str, citations: list[str]) -> list[str]:
    parts: list[str] = []
    for match in PART_RE.findall(text):
        if match not in parts:
            parts.append(match)
    for citation in citations:
        part = citation.split(".", 1)[0]
        if part in {"52", "252"}:
            continue
        if part not in parts:
            parts.append(part)
    return parts


def _dollar_amounts(text: str) -> list[float]:
    return [float(value.replace(",", "")) for value in DOLLAR_RE.findall(text)]

