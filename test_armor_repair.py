from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from answer_builder import OutputValidationError, build_answer_casefile
from armor_pipeline import build_case_file
from armor_types import CitationCandidate, RetrievedSource
from citation_validator import validate_citation
from issue_router import is_rejected_for_issue, route_issue
from output_validator import validate_output_text
from question_classifier import classify_question
from source_router import route_sources
from threshold_resolver import MICRO_PURCHASE_THRESHOLD, evaluate_threshold
from source_policy import is_allowed_source_url, reject_unapproved_urls


class ArmorRepairTests(unittest.TestCase):
    def test_15000_does_not_exceed_micro_purchase_threshold(self) -> None:
        decision = evaluate_threshold(15_000, MICRO_PURCHASE_THRESHOLD, "exceeds")
        self.assertFalse(decision.result)
        self.assertTrue(decision.convention_c_applies)


    def test_classifier_triggers_threshold_convention(self) -> None:
        result = classify_question("Does a $15,000 buy exceed the micro-purchase threshold?")
        self.assertEqual(result.question_type, "threshold")
        self.assertEqual(result.dollar_amounts, [15_000])
        self.assertTrue(result.requires_conventions_check)


    def test_dod_question_routes_to_dfars_and_deviation_check(self) -> None:
        classification = classify_question("For DoD, does DFARS 252.225-7040 apply?")
        routes = route_sources(classification)
        families = {route.source_family for route in routes}
        self.assertIn("dfars_rfo", families)
        self.assertIn("class_deviation", families)


    def test_definition_rejected_for_non_definition_question(self) -> None:
        classification = classify_question("Does this requirement apply to the acquisition?")
        source = RetrievedSource("rfo_far", "RFO FAR 25.003", "Definitions", "Definition text")
        candidate = CitationCandidate(
            source=source,
            excerpt="Domestic construction material means...",
            section_title="Definitions",
            is_definition=True,
        )
        result = validate_citation(candidate, classification)
        self.assertEqual(result.status, "rejected")


    def test_scope_applies_sentence_allowed_for_applicability(self) -> None:
        classification = classify_question("Does this requirement apply to construction?")
        source = RetrievedSource("rfo_far", "RFO FAR 25.200(b)", "Scope", "It applies to construction.")
        candidate = CitationCandidate(
            source=source,
            excerpt="It applies to construction contracts.",
            section_title="Scope",
            has_applicability_language=True,
        )
        result = validate_citation(candidate, classification)
        self.assertEqual(result.status, "accepted")


    def test_class_deviation_wins_precedence(self) -> None:
        question = "Does DFARS 252.225-7040 apply when a class deviation replaces it?"
        deviation_source = RetrievedSource("class_deviation", "Class Deviation 2025-O0001", "Deviation", "Use attached clause.")
        dfars_source = RetrievedSource("dfars_rfo", "DFARS RFO 225.7040", "Prescription", "Use the clause.")
        candidates = [
            CitationCandidate(dfars_source, "Use the clause.", has_shall_must_language=True),
            CitationCandidate(
                deviation_source,
                "Use the attached clause in lieu of the clause.",
                is_class_deviation=True,
                has_shall_must_language=True,
            ),
        ]
        case = build_case_file(question, [deviation_source, dfars_source], candidates)
        self.assertIsNotNone(case.controlling_citation)
        self.assertEqual(case.controlling_citation.source.source_family, "class_deviation")


    def test_answer_builder_requires_step_6(self) -> None:
        source = RetrievedSource("rfo_far", "RFO FAR 1.000", "Applicability", "This applies.")
        candidate = CitationCandidate(source, "This applies.", has_applicability_language=True)
        case = build_case_file("Does this clause apply?", [source], [candidate])
        with self.assertRaises(OutputValidationError):
            build_answer_casefile(case, "Synthesis.", "")


    def test_output_validator_detects_missing_step_6(self) -> None:
        answer = "0) BLUF -- Definitive\nSTEP 6 -- Final Determination\nSTEP 7 -- User Validation Required"
        errors = validate_output_text(answer)
        self.assertIn("STEP 6 Final Determination is empty.", errors)

    def test_issue_router_motor_vehicle_certification_routes_to_far_811(self) -> None:
        question = (
            "You are a contracting officer stationed in Naples, Italy. You received a request "
            "to lease motor vehicles for 60 days. Are you required to obtain written certification "
            "from the requiring activity regarding fuel efficiency and size before preparing the solicitation?"
        )
        profile = route_issue(question)
        self.assertEqual(profile.issue_family, "motor_vehicle_lease_certification")
        self.assertEqual(profile.scope_gate, "FAR 8.1100")
        self.assertEqual(profile.classroom_reference, "FAR 8.1100")
        self.assertTrue(is_rejected_for_issue("DFARS 207.401", profile))

    def test_issue_router_buy_american_threshold_routes_to_far_25100(self) -> None:
        question = (
            "A contracting officer has a requirement for supplies for public use in Oregon valued "
            "at $15,000. None of the exceptions at FAR 25.103 and DFARS 225.103 apply. "
            "Is the contracting officer required to acquire only domestic end products?"
        )
        profile = route_issue(question)
        self.assertEqual(profile.issue_family, "buy_american_supplies_threshold")
        self.assertEqual(profile.classroom_reference, "FAR 25.100(b)(1)")
        self.assertTrue(is_rejected_for_issue("FAR 25.102", profile))

    def test_issue_router_multiyear_keeps_exact_classroom_reference(self) -> None:
        question = (
            "You are a member of an acquisition team contemplating the award of a multiyear "
            "contract with a cancellation ceiling of $20 million. Would congressional "
            "notification be required before award?"
        )
        profile = route_issue(question)
        self.assertEqual(profile.issue_family, "multiyear_congressional_notification")
        self.assertEqual(profile.classroom_reference, "FAR 17.108(b) or DFARS 217.170(d)(1)(iv)")
        self.assertIn("DFARS 217.170(d)(1)(iv)", profile.route_first)

    def test_source_policy_rejects_open_web_sources(self) -> None:
        urls = [
            "https://www.acquisition.gov/far/8.1100",
            "https://acq.osd.mil/dpap/dars/",
            "https://raw.githubusercontent.com/kidkenpo-create/ARMOR-plus/main/file.txt",
            "https://www.youtube.com/watch?v=bad",
            "https://example.com/far",
            "https://wikipedia.org/wiki/Federal_Acquisition_Regulation",
        ]
        rejected = reject_unapproved_urls(urls)
        self.assertIn("https://www.youtube.com/watch?v=bad", rejected)
        self.assertIn("https://example.com/far", rejected)
        self.assertIn("https://wikipedia.org/wiki/Federal_Acquisition_Regulation", rejected)
        self.assertTrue(is_allowed_source_url("https://www.acquisition.gov/far/8.1100"))

    def test_issue_router_remaining_day4_profiles(self) -> None:
        cases = [
            (
                "unclassified construction contract in Nebraska Government estimate of construction costs handled",
                "construction_estimate_handling",
                "DFARS PGI 236.203(1)",
            ),
            (
                "Can the HCA authority at FAR 17.106-3(g) be delegated to chief of contracting office",
                "delegation_of_authority",
                "FAR 1.108(b)",
            ),
            (
                "FAR part 12 supply procurement $800,000 first time purchased by DoD not nontraditional written determination commercial product definition",
                "commercial_product_written_determination",
                "DFARS 212.102(a)(i)(A) or DFARS 212.102(a)(iii)(A)",
            ),
            (
                "Can an enemy prisoner of war be interrogated by contractor personnel Secretary of Defense waiver 60 days",
                "detainee_interrogation_contractor_personnel",
                "DFARS 237.173-4",
            ),
            (
                "competitive solicitation for supplies technical data acquired FAR 52.227-14 none FAR 27.409 exceptions",
                "technical_data_clause_dod_exception",
                "FAR 27.400 or DFARS 227.400",
            ),
            (
                "undefinitized contract action UCA for initial spares limit obligated before definitization",
                "uca_initial_spares_obligation_limit",
                "DFARS 217.7404-5(a)",
            ),
            (
                "FAR 52.246-21 Warranty of Construction fixed-price construction contract performed in Germany",
                "warranty_construction_germany",
                "DFARS 246.710(2)",
            ),
            (
                "maintenance contract performance in Qatar CENTCOM contingency operation include DFARS 252.225-7040 contractor personnel supporting",
                "contingency_contractor_personnel_clause_deviation",
                "CD 2017-O0004",
            ),
            (
                "DoD activity service contract for military flight simulator without waiver from Secretary of Defense",
                "military_flight_simulator_waiver",
                "DFARS 237.102-71(b)",
            ),
            (
                "prime contractor accept subcontractor written representations size small disadvantaged business current accurate complete",
                "subcontractor_sdb_representation",
                "FAR 19.703(a)(2)(i)",
            ),
            (
                "assignment of claims for a nonpersonal services contract may be prohibited Government's interest",
                "assignment_of_claims_nonpersonal_services",
                "DFARS 232.803(b)",
            ),
            (
                "AbilityOne participating nonprofit agency affirmative determination of responsibility before award",
                "abilityone_responsibility_determination",
                "FAR 9.102(b)(3)",
            ),
        ]
        for question, issue_family, reference in cases:
            with self.subTest(issue_family=issue_family):
                profile = route_issue(question)
                self.assertEqual(profile.issue_family, issue_family)
                self.assertEqual(profile.classroom_reference, reference)

    def test_part_27_profile_rejects_far_27409_for_dod_classroom(self) -> None:
        question = (
            "Scenario: You are a contract specialist preparing a competitive solicitation for supplies. "
            "The associated technical data will be acquired under the contract. None of the exceptions "
            "at FAR 27.409(b)(1) apply. Will you be required to include FAR 52.227-14?"
        )
        profile = route_issue(question, classroom_mode=True)
        self.assertEqual(profile.issue_family, "technical_data_clause_dod_exception")
        self.assertEqual(profile.scope_gate, "FAR 27.400")
        self.assertTrue(is_rejected_for_issue("FAR 27.409(b)(1)", profile))
        self.assertIn("DoD is assumed", " ".join(profile.notes))


if __name__ == "__main__":
    unittest.main()
