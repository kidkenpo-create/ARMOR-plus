from __future__ import annotations

from armor_types import CaseFile


class OutputValidationError(ValueError):
    pass


def build_answer_casefile(case: CaseFile, synthesis: str, final_determination: str) -> str:
    validate_output_inputs(case, final_determination)

    status = _determination_status(case)
    citation = case.controlling_citation
    cite_text = citation.source.citation if citation else "UTR"
    excerpt = citation.excerpt if citation else ""

    return "\n".join(
        [
            f"0) BLUF -- {status} {final_determination} Citation: {cite_text}",
            "",
            "STEP 1 -- Acquisition Facts: " + _facts(case),
            "",
            "STEP 2 -- Regulatory Framework: " + _framework(case),
            "",
            "STEP 3A -- Zoom-Out: " + _zoom_out(case),
            "",
            "STEP 3B -- Rungs",
            _rungs(case),
            "",
            "STEP 4 -- Synthesis: " + synthesis,
            "",
            "STEP 5 -- Final Receipt",
            f'- Cite: {cite_text} | Excerpt: "{excerpt[:250]}" | Why: validated against question type and source precedence.',
            "- Self-Verification: code validator accepted controlling citation.",
            "",
            "STEP 6 -- Final Determination: " + final_determination,
            "",
            "STEP 7 -- User Validation Required",
            _unknowns(case),
        ]
    )


def validate_output_inputs(case: CaseFile, final_determination: str) -> None:
    if not final_determination.strip():
        raise OutputValidationError("STEP 6 Final Determination is required.")
    if case.citation_validation.status == "rejected":
        raise OutputValidationError(
            "Cannot produce final answer with rejected citation: "
            + "; ".join(case.citation_validation.reasons)
        )
    if case.controlling_citation is None:
        raise OutputValidationError("A controlling citation is required before answer generation.")


def _determination_status(case: CaseFile) -> str:
    if case.unknowns or case.citation_validation.status == "conditional":
        return "Conditional"
    return "Definitive"


def _facts(case: CaseFile) -> str:
    amounts = ", ".join(f"${amount:,.2f}" for amount in case.classification.dollar_amounts)
    return f"Question type: {case.classification.question_type}; dollar amounts: {amounts or 'N/A'}."


def _framework(case: CaseFile) -> str:
    families = [request.source_family for request in case.source_requests]
    return " -> ".join(dict.fromkeys(families)) or "N/A"


def _zoom_out(case: CaseFile) -> str:
    parts = ", ".join(case.classification.likely_parts or ["unknown"])
    deviation = "required" if case.classification.requires_deviation_check else "not triggered"
    conventions = "required" if case.classification.requires_conventions_check else "not triggered"
    return f"Parts checked: {parts}. Deviation check: {deviation}. Conventions check: {conventions}."


def _rungs(case: CaseFile) -> str:
    lines = []
    retrieved = {(source.source_family, source.part) for source in case.retrieved_sources}
    for request in case.source_requests:
        status = "R" if (request.source_family, request.part) in retrieved else "UTR"
        lines.append(f"- {request.source_family} [{status}]: {request.reason}")
    return "\n".join(lines) if lines else "- N/A"


def _unknowns(case: CaseFile) -> str:
    if not case.unknowns:
        return "None."
    return "\n".join(f"{index}. {unknown}" for index, unknown in enumerate(case.unknowns, 1))

