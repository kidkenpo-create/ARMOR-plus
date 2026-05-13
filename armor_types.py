from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


QuestionType = Literal[
    "clause_applicability",
    "clause_content",
    "definition",
    "procedure",
    "deadline",
    "exception",
    "deviation",
    "role_responsibility",
    "threshold",
    "domestic_preference",
    "subcontracting_plan",
    "other",
]

SourceFamily = Literal[
    "rfo_far",
    "rfo_far_saad",
    "dfars_rfo",
    "dfars_rfo_saad",
    "class_deviation",
    "dfars_pgi",
    "rfo_conventions",
    "legacy",
    "unknown",
]

ValidationStatus = Literal["accepted", "rejected", "conditional"]


@dataclass(frozen=True)
class Classification:
    question_type: QuestionType
    named_citations: list[str] = field(default_factory=list)
    likely_parts: list[str] = field(default_factory=list)
    dollar_amounts: list[float] = field(default_factory=list)
    requires_dfars_check: bool = False
    requires_deviation_check: bool = False
    requires_clause_text: bool = False
    requires_prescription: bool = False
    requires_conventions_check: bool = False
    is_dod: bool = True


@dataclass(frozen=True)
class SourceRequest:
    source_family: SourceFamily
    reason: str
    part: str | None = None
    citation: str | None = None
    required: bool = True


@dataclass(frozen=True)
class RetrievedSource:
    source_family: SourceFamily
    citation: str
    title: str
    text: str
    url: str | None = None
    part: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CitationCandidate:
    source: RetrievedSource
    excerpt: str
    section_title: str | None = None
    rfo_equivalent_exists: bool = False
    has_applicability_language: bool = False
    has_shall_must_language: bool = False
    has_exception_language: bool = False
    is_definition: bool = False
    is_class_deviation: bool = False


@dataclass(frozen=True)
class ValidationResult:
    status: ValidationStatus
    candidate: CitationCandidate | None
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ThresholdDecision:
    amount: float
    threshold: float
    operator: str
    result: bool
    convention_c_applies: bool = True


@dataclass(frozen=True)
class CaseFile:
    question: str
    classification: Classification
    source_requests: list[SourceRequest]
    retrieved_sources: list[RetrievedSource]
    controlling_citation: CitationCandidate | None
    citation_validation: ValidationResult
    threshold_decisions: list[ThresholdDecision] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class IssueProfile:
    issue_family: str
    confidence: float
    matched_triggers: list[str] = field(default_factory=list)
    route_first: list[str] = field(default_factory=list)
    classroom_reference: str | None = None
    current_reference: str | None = None
    scope_gate: str | None = None
    reject_as_controlling: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
