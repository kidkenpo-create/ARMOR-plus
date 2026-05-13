from __future__ import annotations

from armor_types import Classification, IssueProfile, SourceRequest
from issue_router import source_requests_for_issue


DFARS_PARTS = {str(part) for part in range(201, 253)}


def route_sources(classification: Classification, issue_profile: IssueProfile | None = None) -> list[SourceRequest]:
    requests: list[SourceRequest] = []
    if issue_profile and issue_profile.issue_family != "generic":
        requests.extend(source_requests_for_issue(issue_profile))
    parts = classification.likely_parts or ["unknown"]

    for part in parts:
        if _needs_rfo_far(classification, part):
            requests.append(
                SourceRequest("rfo_far", "RFO FAR must be checked for the base rule.", part=part)
            )
            requests.append(
                SourceRequest("rfo_far_saad", "SAAD must be checked for the same RFO FAR part.", part=part)
            )

        if classification.is_dod or part in DFARS_PARTS:
            dfars_part = _to_dfars_part(part)
            requests.append(
                SourceRequest("dfars_rfo", "DoD default requires DFARS RFO overlay check.", part=dfars_part)
            )
            requests.append(
                SourceRequest(
                    "dfars_rfo_saad",
                    "DFARS RFO SAAD must be checked before finalizing a DFARS answer.",
                    part=dfars_part,
                )
            )

        if classification.requires_deviation_check:
            requests.append(
                SourceRequest(
                    "class_deviation",
                    "Class deviations can displace RFO FAR/DFARS text.",
                    part=_to_dfars_part(part),
                    required=True,
                )
            )

        if classification.requires_conventions_check:
            requests.append(
                SourceRequest(
                    "rfo_conventions",
                    "RFO FAR conventions may control threshold, delegation, or actor questions.",
                    part="1",
                    required=True,
                )
            )

        if classification.question_type in {"procedure", "deadline"}:
            requests.append(
                SourceRequest("dfars_pgi", "Procedural questions require PGI check when DoD applies.", part=_to_dfars_part(part))
            )

    return _dedupe(requests)


def _needs_rfo_far(classification: Classification, part: str) -> bool:
    return part != "unknown" and not part.startswith("2") or bool(classification.named_citations)


def _to_dfars_part(part: str) -> str:
    if part == "unknown":
        return part
    if part.startswith("2"):
        return part
    return f"2{int(part):02d}"


def _dedupe(requests: list[SourceRequest]) -> list[SourceRequest]:
    seen: set[tuple[str, str | None, str | None]] = set()
    deduped: list[SourceRequest] = []
    for request in requests:
        key = (request.source_family, request.part, request.citation)
        if key not in seen:
            seen.add(key)
            deduped.append(request)
    return deduped
