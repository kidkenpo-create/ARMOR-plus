from __future__ import annotations

from armor_types import CitationCandidate, Classification, IssueProfile, ValidationResult
from issue_router import is_rejected_for_issue


TITLE_TRAP_TITLES = {"general", "scope", "purpose", "definitions", "policy"}


def validate_citation(
    candidate: CitationCandidate,
    classification: Classification,
    issue_profile: IssueProfile | None = None,
) -> ValidationResult:
    reasons: list[str] = []
    qtype = classification.question_type
    source_family = candidate.source.source_family
    citation = candidate.source.citation
    title = (candidate.section_title or "").strip().lower()

    if source_family == "legacy" and candidate.rfo_equivalent_exists:
        reasons.append("Legacy citation used even though an RFO equivalent exists.")

    if issue_profile and is_rejected_for_issue(citation, issue_profile):
        reasons.append(f"{citation} is a known wrong-nearby source for {issue_profile.issue_family}.")

    if issue_profile and issue_profile.scope_gate:
        if candidate.has_exception_language and citation != issue_profile.scope_gate:
            reasons.append(f"Scope-gate issue requires checking {issue_profile.scope_gate} before {citation}.")

    if candidate.is_definition and qtype != "definition":
        reasons.append("Definition cannot be the controlling citation for a non-definition question.")

    if title in TITLE_TRAP_TITLES and qtype != "definition":
        if not (qtype == "clause_applicability" and candidate.has_applicability_language):
            reasons.append("General/scope/purpose/policy cite failed the title-trap exception.")

    if qtype in {"clause_applicability", "threshold", "exception", "domestic_preference"}:
        if not (
            candidate.has_applicability_language
            or candidate.has_exception_language
            or candidate.has_shall_must_language
            or candidate.is_class_deviation
        ):
            reasons.append("Applicability answer lacks operative applicability, exception, or mandate language.")

    if qtype in {"procedure", "deadline", "role_responsibility"} and not candidate.has_shall_must_language:
        reasons.append("Procedural/responsibility answer lacks shall/must operative language.")

    if classification.requires_deviation_check and source_family not in {"class_deviation", "dfars_rfo", "rfo_far"}:
        reasons.append("Required deviation-aware question was answered from a non-controlling source family.")

    if reasons:
        return ValidationResult("rejected", candidate, reasons)

    return ValidationResult("accepted", candidate, ["Candidate directly supports the answer type."])


def choose_controlling_citation(
    candidates: list[CitationCandidate],
    classification: Classification,
    issue_profile: IssueProfile | None = None,
) -> ValidationResult:
    accepted: list[ValidationResult] = []
    rejected_reasons: list[str] = []

    for candidate in sorted(candidates, key=_precedence_key):
        result = validate_citation(candidate, classification, issue_profile)
        if result.status == "accepted":
            accepted.append(result)
        else:
            rejected_reasons.extend(result.reasons)

    if accepted:
        return accepted[0]

    return ValidationResult(
        "rejected",
        None,
        rejected_reasons or ["No candidate citation was available for validation."],
    )


def _precedence_key(candidate: CitationCandidate) -> int:
    if candidate.is_class_deviation or candidate.source.source_family == "class_deviation":
        return 0
    if candidate.source.source_family == "dfars_rfo":
        return 1
    if candidate.source.source_family == "dfars_pgi":
        return 2
    if candidate.source.source_family == "rfo_far":
        return 3
    if candidate.source.source_family == "rfo_far_saad":
        return 4
    return 9
