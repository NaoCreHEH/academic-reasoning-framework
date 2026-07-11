import unittest

from core.ontology import (
    Claim,
    ConfidenceAssessment,
    ConfidenceLabel,
    ConfidenceState,
    EvidenceCategory,
    EvidenceItem,
    EvidenceReference,
    FeedbackItem,
    FindingKind,
    OntologyValidationError,
    RoutingTrace,
    Severity,
    validate_feedback_item,
)


class EnumTests(unittest.TestCase):
    def test_exact_evidence_categories(self) -> None:
        self.assertEqual(
            [member.name for member in EvidenceCategory],
            [
                "DIRECT_OBSERVATION",
                "EXECUTION_RESULT",
                "MEASUREMENT",
                "DERIVED_EVIDENCE",
            ],
        )

    def test_no_corroborated_evidence_category(self) -> None:
        self.assertNotIn("CORROBORATED", [member.name for member in EvidenceCategory])

    def test_exact_five_confidence_labels(self) -> None:
        self.assertEqual(
            [member.name for member in ConfidenceLabel],
            [
                "CONFIRMED",
                "STRONGLY_SUPPORTED",
                "SUPPORTED",
                "PLAUSIBLE",
                "SPECULATIVE",
            ],
        )

    def test_confidence_state_separate_from_label(self) -> None:
        self.assertNotIsInstance(ConfidenceState.UNKNOWN, ConfidenceLabel)
        self.assertEqual([member.name for member in ConfidenceState], ["UNKNOWN", "NOT_ASSESSED"])

    def test_exact_severity_members(self) -> None:
        self.assertEqual(
            [member.name for member in Severity],
            ["BLOCKING", "MAJOR", "MODERATE", "MINOR", "INFORMATIONAL"],
        )


class EvidenceModelTests(unittest.TestCase):
    def test_valid_direct_evidence(self) -> None:
        item = EvidenceItem(
            identifier="e1",
            category=EvidenceCategory.DIRECT_OBSERVATION,
            reference=EvidenceReference(source="settings.py", locator="line 4"),
            scope="settings.py",
            provenance="static inspection",
        )
        self.assertEqual(item.identifier, "e1")

    def test_direct_observation_with_derived_from_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            EvidenceItem(
                identifier="e1",
                category=EvidenceCategory.DIRECT_OBSERVATION,
                reference=EvidenceReference(source="settings.py", locator="line 4"),
                scope="settings.py",
                provenance="static inspection",
                derived_from=("e0",),
            )

    def test_execution_result_with_transformation_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            EvidenceItem(
                identifier="e1",
                category=EvidenceCategory.EXECUTION_RESULT,
                reference=EvidenceReference(source="unit test output"),
                scope="tests",
                provenance="test execution",
                transformation="summarized failing test output",
            )

    def test_measurement_with_derivation_lineage_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            EvidenceItem(
                identifier="e1",
                category=EvidenceCategory.MEASUREMENT,
                reference=EvidenceReference(source="coverage report"),
                scope="coverage",
                provenance="measurement",
                derived_from=("e0",),
                transformation="calculated branch coverage",
            )

    def test_valid_non_derived_evidence_accepted(self) -> None:
        item = EvidenceItem(
            identifier="e1",
            category=EvidenceCategory.MEASUREMENT,
            reference=EvidenceReference(source="coverage report"),
            scope="coverage",
            provenance="measurement",
        )
        self.assertEqual(item.derived_from, ())
        self.assertIsNone(item.transformation)

    def test_valid_derived_evidence_accepted(self) -> None:
        item = EvidenceItem(
            identifier="d1",
            category=EvidenceCategory.DERIVED_EVIDENCE,
            reference=EvidenceReference(source="analysis summary"),
            scope="module",
            provenance="derived analysis",
            derived_from=("e1",),
            transformation="summarized repeated import cycles",
        )
        self.assertEqual(item.derived_from, ("e1",))
        self.assertEqual(item.transformation, "summarized repeated import cycles")

    def test_blank_source_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            EvidenceReference(source=" ")

    def test_blank_identifier_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            EvidenceItem(
                identifier="",
                category=EvidenceCategory.DIRECT_OBSERVATION,
                reference=EvidenceReference(source="file.py"),
                scope="file.py",
                provenance="static inspection",
            )

    def test_derived_evidence_without_source_ids_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            EvidenceItem(
                identifier="d1",
                category=EvidenceCategory.DERIVED_EVIDENCE,
                reference=EvidenceReference(source="tool output"),
                scope="module",
                provenance="measurement",
                transformation="count imports",
            )

    def test_derived_evidence_without_transformation_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            EvidenceItem(
                identifier="d1",
                category=EvidenceCategory.DERIVED_EVIDENCE,
                reference=EvidenceReference(source="tool output"),
                scope="module",
                provenance="measurement",
                derived_from=("e1",),
            )


class ClaimAndConfidenceModelTests(unittest.TestCase):
    def test_claim_may_exist_without_evidence(self) -> None:
        claim = Claim(identifier="c1", text="The function is complex.")
        self.assertEqual(claim.evidence_ids, ())

    def test_label_assessment_accepted(self) -> None:
        assessment = ConfidenceAssessment(
            target_id="c1",
            label=ConfidenceLabel.SUPPORTED,
            basis="Evidence e1 supports the claim.",
        )
        self.assertEqual(assessment.label, ConfidenceLabel.SUPPORTED)

    def test_state_assessment_accepted(self) -> None:
        assessment = ConfidenceAssessment(
            target_id="c1",
            state=ConfidenceState.UNKNOWN,
            basis="Only partial files were provided.",
        )
        self.assertEqual(assessment.state, ConfidenceState.UNKNOWN)

    def test_label_plus_state_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            ConfidenceAssessment(
                target_id="c1",
                label=ConfidenceLabel.PLAUSIBLE,
                state=ConfidenceState.UNKNOWN,
                basis="Conflicting inputs.",
            )

    def test_neither_label_nor_state_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            ConfidenceAssessment(target_id="c1")

    def test_confidence_label_without_basis_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            ConfidenceAssessment(target_id="c1", label=ConfidenceLabel.CONFIRMED)

    def test_unknown_remains_state(self) -> None:
        self.assertIs(ConfidenceState.UNKNOWN, ConfidenceState.UNKNOWN)
        self.assertNotIn("UNKNOWN", [member.name for member in ConfidenceLabel])

    def test_not_assessed_remains_state(self) -> None:
        self.assertIs(ConfidenceState.NOT_ASSESSED, ConfidenceState.NOT_ASSESSED)
        self.assertNotIn("NOT_ASSESSED", [member.name for member in ConfidenceLabel])

    def test_obvious_uncalibrated_percentage_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            ConfidenceAssessment(
                target_id="c1",
                label=ConfidenceLabel.SUPPORTED,
                basis="73% confident this is correct.",
            )


class FeedbackModelTests(unittest.TestCase):
    def test_demonstrated_error_with_evidence_accepted(self) -> None:
        item = FeedbackItem(
            identifier="f1",
            target="total_price",
            finding="Discount is not applied.",
            finding_kind=FindingKind.DEMONSTRATED_ERROR,
            evidence_summary="Test output shows expected 90 and actual 100.",
            impact=None,
            recommendation=None,
        )
        self.assertEqual(item.finding_kind, FindingKind.DEMONSTRATED_ERROR)

    def test_demonstrated_error_without_evidence_summary_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            FeedbackItem(
                identifier="f1",
                target="total_price",
                finding="Discount is not applied.",
                finding_kind=FindingKind.DEMONSTRATED_ERROR,
                evidence_summary=None,
                impact=None,
                recommendation=None,
            )

    def test_debatable_choice_is_not_automatically_error(self) -> None:
        item = FeedbackItem(
            identifier="f1",
            target="UML association",
            finding="Composition may overstate lifecycle ownership.",
            finding_kind=FindingKind.DEBATABLE_CHOICE,
            evidence_summary=None,
            impact=None,
            recommendation=None,
        )
        self.assertEqual(item.finding_kind, FindingKind.DEBATABLE_CHOICE)

    def test_positive_finding_requires_evidence_summary(self) -> None:
        with self.assertRaises(OntologyValidationError):
            FeedbackItem(
                identifier="f1",
                target="diagram",
                finding="Uses domain vocabulary.",
                finding_kind=FindingKind.POSITIVE_FINDING,
                evidence_summary=None,
                impact=None,
                recommendation=None,
            )

    def test_severity_independent_from_confidence(self) -> None:
        item = FeedbackItem(
            identifier="f1",
            target="typo",
            finding="A typo exists.",
            finding_kind=FindingKind.DEMONSTRATED_ERROR,
            evidence_summary="The word is misspelled.",
            impact=None,
            recommendation=None,
            severity=Severity.MINOR,
            confidence=ConfidenceAssessment(
                target_id="f1",
                label=ConfidenceLabel.CONFIRMED,
                basis="The typo is directly visible.",
            ),
        )
        self.assertEqual(item.severity, Severity.MINOR)
        self.assertEqual(item.confidence.label, ConfidenceLabel.CONFIRMED)

    def test_require_impact_rejects_missing_impact(self) -> None:
        item = FeedbackItem(
            identifier="f1",
            target="endpoint",
            finding="Authorization is not demonstrated.",
            finding_kind=FindingKind.HYPOTHESIS,
            evidence_summary=None,
            impact=None,
            recommendation=None,
        )
        with self.assertRaises(OntologyValidationError):
            validate_feedback_item(item, require_impact=True)

    def test_require_recommendation_rejects_missing_recommendation(self) -> None:
        item = FeedbackItem(
            identifier="f1",
            target="endpoint",
            finding="Authorization is not demonstrated.",
            finding_kind=FindingKind.HYPOTHESIS,
            evidence_summary=None,
            impact="Security verification is blocked.",
            recommendation=None,
        )
        with self.assertRaises(OntologyValidationError):
            validate_feedback_item(item, require_recommendation=True)


class RoutingTraceModelTests(unittest.TestCase):
    def test_valid_trace(self) -> None:
        trace = RoutingTrace(
            user_objective="Create questions",
            primary_artifact="Python code",
            requested_output="MCQs",
            primary_capability="exam generation",
            supporting_capabilities=("python teaching",),
        )
        self.assertEqual(trace.primary_capability, "exam generation")

    def test_ambiguous_trace_without_primary_capability_accepted(self) -> None:
        trace = RoutingTrace(
            user_objective="Review this project",
            primary_artifact=None,
            requested_output=None,
            primary_capability=None,
            material_ambiguity="Artifact type is unknown.",
        )
        self.assertIsNone(trace.primary_capability)

    def test_no_primary_capability_and_no_ambiguity_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            RoutingTrace(
                user_objective="Review this project",
                primary_artifact=None,
                requested_output=None,
                primary_capability=None,
            )

    def test_primary_capability_duplicated_in_supporting_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            RoutingTrace(
                user_objective="Create questions",
                primary_artifact="Python code",
                requested_output="MCQs",
                primary_capability="exam generation",
                supporting_capabilities=("exam generation",),
            )

    def test_duplicate_supporting_capabilities_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            RoutingTrace(
                user_objective="Review code",
                primary_artifact="repository",
                requested_output="feedback",
                primary_capability="architecture review",
                supporting_capabilities=("python teaching", "python teaching"),
            )

    def test_blank_capability_names_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            RoutingTrace(
                user_objective="Review code",
                primary_artifact="repository",
                requested_output="feedback",
                primary_capability="architecture review",
                supporting_capabilities=(" ",),
            )


if __name__ == "__main__":
    unittest.main()
