from __future__ import annotations

import re
from dataclasses import dataclass

from armor_types import IssueProfile, SourceRequest


@dataclass(frozen=True)
class IssueRule:
    issue_family: str
    required_any: tuple[str, ...]
    weighted_triggers: tuple[str, ...]
    route_first: tuple[str, ...]
    classroom_reference: str | None
    current_reference: str | None
    scope_gate: str | None = None
    reject_as_controlling: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


ISSUE_RULES: tuple[IssueRule, ...] = (
    IssueRule(
        issue_family="motor_vehicle_lease_certification",
        required_any=("motor vehicle", "motor vehicles", "vehicle"),
        weighted_triggers=(
            "lease",
            "leased",
            "fuel efficiency",
            "size",
            "equipment",
            "written certification",
            "requiring activity",
            "before",
            "solicitation",
        ),
        route_first=("RFO FAR 8.1100", "RFO FAR 8.1102"),
        classroom_reference="FAR 8.1100",
        current_reference="RFO FAR 8.1100",
        scope_gate="RFO FAR 8.1100",
        reject_as_controlling=("DFARS RFO 207.401",),
        notes=(
            "This is a motor-vehicle certification issue, not a lease-or-purchase justification issue.",
            "Check the RFO FAR 8.11 scope gate before the certification rule.",
        ),
    ),
    IssueRule(
        issue_family="buy_american_supplies_threshold",
        required_any=("domestic end product", "domestic end products", "buy american"),
        weighted_triggers=(
            "supplies",
            "supply",
            "public use",
            "united states",
            "oregon",
            "$",
            "15,000",
            "25.103",
            "exceptions",
        ),
        route_first=("RFO FAR 25.100(b)(1)", "RFO FAR 25.102", "RFO FAR 25.103", "RFO FAR 2.101"),
        classroom_reference="FAR 25.100(b)(1)",
        current_reference="RFO FAR 25.100(b)(1)",
        scope_gate="RFO FAR 25.100(b)(1)",
        reject_as_controlling=("RFO FAR 25.102", "RFO FAR 25.003"),
        notes=(
            "The applicability threshold controls before the domestic-only policy.",
            "Exactly the micro-purchase threshold does not exceed the threshold.",
        ),
    ),
    IssueRule(
        issue_family="multiyear_congressional_notification",
        required_any=("multiyear", "multi-year"),
        weighted_triggers=(
            "cancellation ceiling",
            "congressional notification",
            "before award",
            "$20 million",
            "20 million",
            "award",
            "contract",
        ),
        route_first=("RFO FAR 17.108(b)", "DFARS RFO 217.170(d)(1)(iv)", "RFO FAR 17.104-3"),
        classroom_reference="FAR 17.108(b) or DFARS 217.170(d)(1)(iv)",
        current_reference="DFARS RFO 217.104-370(b)(1)(iv)",
        scope_gate=None,
        reject_as_controlling=("RFO FAR 17.104-3(a)-(c)",),
        notes=(
            "Preserve exact paragraph level for the class reference.",
            "A cancellation ceiling exactly equal to $20 million does not exceed $20 million.",
        ),
    ),
    IssueRule(
        issue_family="micro_purchase_threshold",
        required_any=("micro-purchase", "micro purchase"),
        weighted_triggers=("threshold", "$", "15,000", "exceed", "exceeds"),
        route_first=("RFO FAR 2.101", "RFO FAR 1.107(c)"),
        classroom_reference="FAR 2.101",
        current_reference="RFO FAR 2.101",
        scope_gate=None,
        reject_as_controlling=(),
        notes=("Exactly $15,000 equals the threshold; it does not exceed it.",),
    ),
    IssueRule(
        issue_family="construction_estimate_handling",
        required_any=("government estimate", "estimate of construction", "construction costs"),
        weighted_triggers=("construction", "unclassified", "nebraska", "for official use only", "bids", "estimate"),
        route_first=("DFARS PGI 236.203(1)", "RFO FAR 36.203", "DFARS RFO 236.203"),
        classroom_reference="DFARS PGI 236.203(1)",
        current_reference="DFARS PGI 236.203(1)",
        notes=("Handling/marking of DoD construction estimates routes to PGI, not only RFO FAR 36.203.",),
    ),
    IssueRule(
        issue_family="delegation_of_authority",
        required_any=("delegated", "delegate", "delegation"),
        weighted_triggers=("hca", "head of the contracting activity", "chief of the contracting office", "17.106-3", "variable unit prices"),
        route_first=("RFO FAR 1.108(b)", "RFO FAR 17.106-3(g)"),
        classroom_reference="FAR 1.108(b)",
        current_reference="RFO FAR 1.108(b)",
        notes=("Delegation questions are controlled by the FAR convention unless the authority says nondelegable.",),
    ),
    IssueRule(
        issue_family="commercial_product_written_determination",
        required_any=("commercial product", "commercial service", "far part 12"),
        weighted_triggers=("800,000", "first time", "not solicit from nontraditional", "12.102", "written determination", "simplified acquisition threshold"),
        route_first=("DFARS RFO 212.102(a)(iii)(A)", "DFARS RFO 212.102(a)(i)(A)"),
        classroom_reference="DFARS 212.102(a)(i)(A) or DFARS 212.102(a)(iii)(A)",
        current_reference="DFARS RFO 212.102(a)(iii)(A)",
        notes=("If RFO FAR part 12 use is under the commerciality path and exceeds SAT, written determination is required.",),
    ),
    IssueRule(
        issue_family="detainee_interrogation_contractor_personnel",
        required_any=("enemy prisoner of war", "detainee"),
        weighted_triggers=("interrogated", "interrogate", "contractor personnel", "secretary of defense", "waiver", "60 days"),
        route_first=("DFARS RFO 237.173-4", "DFARS RFO 237.173-3(a)", "DFARS RFO 237.173-2"),
        classroom_reference="DFARS 237.173-4",
        current_reference="DFARS RFO 237.173-4",
        notes=("Answer includes the general prohibition and the 60-day Secretary of Defense waiver.",),
    ),
    IssueRule(
        issue_family="technical_data_clause_dod_exception",
        required_any=("52.227-14", "technical data", "data will be acquired"),
        weighted_triggers=("competitive solicitation", "supplies", "27.409", "none of the exceptions", "include the clause"),
        route_first=("RFO FAR 27.400", "DFARS RFO 227.400", "RFO FAR 27.409(b)(1)"),
        classroom_reference="FAR 27.400 or DFARS 227.400",
        current_reference="RFO FAR 27.400 or DFARS RFO 227.400",
        scope_gate="RFO FAR 27.400",
        reject_as_controlling=("RFO FAR 27.409(b)(1)",),
        notes=(
            "In classroom mode, DoD is assumed; do not treat DoD status as unknown.",
            "For DoD, RFO FAR 27.400/DFARS RFO 227.400 controls before the RFO FAR 52.227-14 prescription.",
            "Expected classroom answer is No when the question asks whether RFO FAR 52.227-14 is required for DoD technical data.",
        ),
    ),
    IssueRule(
        issue_family="uca_initial_spares_obligation_limit",
        required_any=("undefinitized contract action", "uca"),
        weighted_triggers=("initial spares", "obligated", "before definitization", "limit", "limitations"),
        route_first=("DFARS RFO 217.7404-5(a)", "DFARS RFO 217.7404-4"),
        classroom_reference="DFARS 217.7404-5(a)",
        current_reference="DFARS RFO 217.7404-5(a)",
        reject_as_controlling=("DFARS RFO 217.7404-4",),
        notes=("The initial-spares exception controls over the normal UCA obligation limits.",),
    ),
    IssueRule(
        issue_family="warranty_construction_germany",
        required_any=("52.246-21", "warranty of construction", "germany"),
        weighted_triggers=("fixed-price", "construction", "performed in germany", "use the clause", "246.710"),
        route_first=("DFARS RFO 246.710(2)", "RFO FAR 46.710(e)(1)"),
        classroom_reference="DFARS 246.710(2)",
        current_reference="DFARS RFO 246.710(2)",
        reject_as_controlling=("RFO FAR 46.710(e)(1)", "RFO FAR 52.246-21"),
        notes=("Germany-specific DFARS prescription controls over the general FAR warranty clause.",),
    ),
    IssueRule(
        issue_family="contingency_contractor_personnel_clause_deviation",
        required_any=("252.225-7040", "contractor personnel supporting"),
        weighted_triggers=("qatar", "centcom", "contingency operation", "maintenance contract", "8,500,000", "outside the united states"),
        route_first=("CD 2017-O0004", "DFARS RFO 225.371-5(a)"),
        classroom_reference="CD 2017-O0004",
        current_reference="CD 2017-O0004",
        reject_as_controlling=("DFARS RFO 225.371-5(a)",),
        notes=("Class deviation is the expected controlling authority for this classroom question.",),
    ),
    IssueRule(
        issue_family="military_flight_simulator_waiver",
        required_any=("military flight simulator",),
        weighted_triggers=("service contract", "secretary of defense", "waiver", "without getting a waiver"),
        route_first=("DFARS RFO 237.102-71(b)", "PGI 237.102-71"),
        classroom_reference="DFARS 237.102-71(b)",
        current_reference="DFARS RFO 237.102-71(b)",
        notes=("The prohibition/waiver rule controls; PGI is supporting waiver process.",),
    ),
    IssueRule(
        issue_family="subcontractor_sdb_representation",
        required_any=("subcontractor", "small disadvantaged business"),
        weighted_triggers=("written representations", "size", "socioeconomic status", "current", "accurate", "complete", "prime contractor"),
        route_first=("RFO FAR 19.703(a)(2)(i)",),
        classroom_reference="FAR 19.703(a)(2)(i)",
        current_reference="RFO FAR 19.703(a)(2)(i)",
        notes=("Prime may accept written representation unless it has reason to question it.",),
    ),
    IssueRule(
        issue_family="assignment_of_claims_nonpersonal_services",
        required_any=("assignment of claims",),
        weighted_triggers=("nonpersonal services", "prohibited", "government's interest", "may not be prohibited"),
        route_first=("DFARS RFO 232.803(b)", "RFO FAR 32.803(b)"),
        classroom_reference="DFARS 232.803(b)",
        current_reference="DFARS RFO 232.803(b)",
        reject_as_controlling=("RFO FAR 32.803(b)",),
        notes=("For DoD, DFARS RFO 232.803(b) is the expected controlling authority, not the broader RFO FAR cite.",),
    ),
    IssueRule(
        issue_family="abilityone_responsibility_determination",
        required_any=("abilityone", "participating nonprofit"),
        weighted_triggers=("affirmative determination", "responsibility", "before making the award", "nonprofit agency"),
        route_first=("RFO FAR 9.102(b)(3)", "RFO FAR 9.103(b)"),
        classroom_reference="FAR 9.102(b)(3)",
        current_reference="RFO FAR 9.102(b)(3)",
        reject_as_controlling=("RFO FAR 9.103(b)",),
        notes=("Applicability exclusion controls before the general affirmative-responsibility rule.",),
    ),
)


def route_issue(question: str, classroom_mode: bool = True) -> IssueProfile:
    text = _normalize(question)
    best_rule: IssueRule | None = None
    best_score = 0.0
    best_matches: list[str] = []

    for rule in ISSUE_RULES:
        if not any(trigger in text for trigger in rule.required_any):
            continue
        matches = [trigger for trigger in rule.weighted_triggers if trigger in text]
        score = _score(rule, matches, text)
        if score > best_score:
            best_rule = rule
            best_score = score
            best_matches = matches

    if best_rule is None or best_score < 0.35:
        return IssueProfile("generic", 0.0, notes=["No issue-family profile matched with confidence."])

    reference = best_rule.classroom_reference if classroom_mode else best_rule.current_reference
    return IssueProfile(
        issue_family=best_rule.issue_family,
        confidence=round(best_score, 3),
        matched_triggers=best_matches,
        route_first=list(best_rule.route_first),
        classroom_reference=best_rule.classroom_reference,
        current_reference=best_rule.current_reference,
        scope_gate=best_rule.scope_gate,
        reject_as_controlling=list(best_rule.reject_as_controlling),
        notes=[f"Preferred reference: {reference}.", *best_rule.notes],
    )


def source_requests_for_issue(profile: IssueProfile) -> list[SourceRequest]:
    requests: list[SourceRequest] = []
    for citation in profile.route_first:
        source_family = _source_family_for_citation(citation)
        requests.append(
            SourceRequest(
                source_family=source_family,
                reason=f"Issue-family route: {profile.issue_family} requires {citation}.",
                part=_part_for_citation(citation),
                citation=citation,
                required=True,
            )
        )
    return requests


def is_rejected_for_issue(citation: str, profile: IssueProfile) -> bool:
    normalized = _citation_key(citation)
    return any(normalized == _citation_key(rejected) for rejected in profile.reject_as_controlling)


def _score(rule: IssueRule, matches: list[str], text: str) -> float:
    if not rule.weighted_triggers:
        return 0.0
    score = 0.25 + (len(matches) / len(rule.weighted_triggers)) * 0.75
    if "$" in text or re.search(r"\b\d+\s*million\b", text):
        score += 0.05
    return min(score, 1.0)


def _normalize(question: str) -> str:
    return re.sub(r"\s+", " ", question.lower()).strip()


def _source_family_for_citation(citation: str) -> str:
    if citation.startswith("DFARS"):
        return "dfars_rfo"
    if citation.startswith("RFO FAR") or citation.startswith("FAR"):
        return "rfo_far"
    return "unknown"


def _part_for_citation(citation: str) -> str | None:
    match = re.search(r"(\d{1,3})\.", citation)
    return match.group(1) if match else None


def _citation_key(citation: str) -> str:
    return re.sub(r"\s+", "", citation.lower())
