from __future__ import annotations

from armor_types import CaseFile, CitationCandidate, RetrievedSource
from citation_validator import choose_controlling_citation
from issue_router import route_issue
from question_classifier import classify_question
from source_router import route_sources
from threshold_resolver import resolve_thresholds


def build_case_file(
    question: str,
    retrieved_sources: list[RetrievedSource],
    candidates: list[CitationCandidate],
    classroom_mode: bool = True,
) -> CaseFile:
    classification = classify_question(question)
    issue_profile = route_issue(question, classroom_mode=classroom_mode)
    source_requests = route_sources(classification, issue_profile)
    threshold_decisions = resolve_thresholds(classification.dollar_amounts)
    validation = choose_controlling_citation(candidates, classification, issue_profile)

    return CaseFile(
        question=question,
        classification=classification,
        source_requests=source_requests,
        retrieved_sources=retrieved_sources,
        controlling_citation=validation.candidate,
        citation_validation=validation,
        threshold_decisions=threshold_decisions,
        unknowns=[],
    )
