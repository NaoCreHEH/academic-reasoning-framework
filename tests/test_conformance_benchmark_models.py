import unittest

from benchmark.conformance import (
    ConformanceCase,
    ConformanceDomain,
    ConformanceExpectation,
    ConformanceFailureKind,
    ConformanceResult,
    ConformanceSummary,
)
from benchmark.conformance.models import ConformanceBenchmarkValidationError


def noop():
    return None


class ConformanceEnumTests(unittest.TestCase):
    def test_exact_conformance_domain_members(self) -> None:
        self.assertEqual(
            {member.name: member.value for member in ConformanceDomain},
            {
                "EVIDENCE": "evidence",
                "CLAIM": "claim",
                "CONFIDENCE": "confidence",
                "FEEDBACK": "feedback",
                "INTERPRETATION": "interpretation",
            },
        )

    def test_exact_conformance_expectation_members(self) -> None:
        self.assertEqual(
            {member.name: member.value for member in ConformanceExpectation},
            {"ACCEPT": "accept", "REJECT": "reject"},
        )

    def test_exact_conformance_failure_kind_members(self) -> None:
        self.assertEqual(
            {member.name: member.value for member in ConformanceFailureKind},
            {
                "CONSTRUCTION_ERROR": "construction_error",
                "VALIDATION_ERROR": "validation_error",
                "UNEXPECTED_ACCEPTANCE": "unexpected_acceptance",
                "UNEXPECTED_REJECTION": "unexpected_rejection",
                "WRONG_ERROR_TYPE": "wrong_error_type",
            },
        )


class ConformanceCaseModelTests(unittest.TestCase):
    def test_valid_accept_case(self) -> None:
        case = ConformanceCase(
            identifier="case",
            description="description",
            domain=ConformanceDomain.EVIDENCE,
            expectation=ConformanceExpectation.ACCEPT,
            operation=noop,
            tags=("positive",),
            rfc_references=("RFC-0002",),
        )
        self.assertIs(case.expectation, ConformanceExpectation.ACCEPT)

    def test_valid_reject_case(self) -> None:
        case = ConformanceCase(
            identifier="case",
            description="description",
            domain=ConformanceDomain.EVIDENCE,
            expectation=ConformanceExpectation.REJECT,
            operation=noop,
            expected_error=ValueError,
            tags=("negative",),
            rfc_references=("RFC-0002",),
        )
        self.assertIs(case.expected_error, ValueError)

    def test_blank_identifier_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceCase(
                identifier=" ",
                description="description",
                domain=ConformanceDomain.EVIDENCE,
                expectation=ConformanceExpectation.ACCEPT,
                operation=noop,
            )

    def test_blank_description_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceCase(
                identifier="case",
                description=" ",
                domain=ConformanceDomain.EVIDENCE,
                expectation=ConformanceExpectation.ACCEPT,
                operation=noop,
            )

    def test_non_callable_operation_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceCase(
                identifier="case",
                description="description",
                domain=ConformanceDomain.EVIDENCE,
                expectation=ConformanceExpectation.ACCEPT,
                operation="not callable",
            )

    def test_duplicate_tags_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceCase(
                identifier="case",
                description="description",
                domain=ConformanceDomain.EVIDENCE,
                expectation=ConformanceExpectation.ACCEPT,
                operation=noop,
                tags=("tag", "tag"),
            )

    def test_blank_tag_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceCase(
                identifier="case",
                description="description",
                domain=ConformanceDomain.EVIDENCE,
                expectation=ConformanceExpectation.ACCEPT,
                operation=noop,
                tags=(" ",),
            )

    def test_duplicate_rfc_references_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceCase(
                identifier="case",
                description="description",
                domain=ConformanceDomain.EVIDENCE,
                expectation=ConformanceExpectation.ACCEPT,
                operation=noop,
                rfc_references=("RFC-0002", "RFC-0002"),
            )

    def test_invalid_rfc_reference_format_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceCase(
                identifier="case",
                description="description",
                domain=ConformanceDomain.EVIDENCE,
                expectation=ConformanceExpectation.ACCEPT,
                operation=noop,
                rfc_references=("RFC-2",),
            )

    def test_accept_with_expected_error_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceCase(
                identifier="case",
                description="description",
                domain=ConformanceDomain.EVIDENCE,
                expectation=ConformanceExpectation.ACCEPT,
                operation=noop,
                expected_error=ValueError,
            )

    def test_reject_without_expected_error_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceCase(
                identifier="case",
                description="description",
                domain=ConformanceDomain.EVIDENCE,
                expectation=ConformanceExpectation.REJECT,
                operation=noop,
            )

    def test_reject_with_non_exception_expected_error_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceCase(
                identifier="case",
                description="description",
                domain=ConformanceDomain.EVIDENCE,
                expectation=ConformanceExpectation.REJECT,
                operation=noop,
                expected_error=str,
            )


class ConformanceResultSummaryTests(unittest.TestCase):
    def result(
        self,
        identifier: str,
        domain: ConformanceDomain,
        passed: bool,
    ) -> ConformanceResult:
        return ConformanceResult(
            case_identifier=identifier,
            domain=domain,
            passed=passed,
            expected=ConformanceExpectation.ACCEPT,
            observed_accepted=True,
            failure_kind=None if passed else ConformanceFailureKind.UNEXPECTED_REJECTION,
            observed_error_type=None,
            diagnostic="diagnostic",
        )

    def test_passed_result_with_failure_kind_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceResult(
                case_identifier="case",
                domain=ConformanceDomain.EVIDENCE,
                passed=True,
                expected=ConformanceExpectation.ACCEPT,
                observed_accepted=True,
                failure_kind=ConformanceFailureKind.UNEXPECTED_REJECTION,
                observed_error_type=None,
                diagnostic="diagnostic",
            )

    def test_failed_result_without_failure_kind_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceResult(
                case_identifier="case",
                domain=ConformanceDomain.EVIDENCE,
                passed=False,
                expected=ConformanceExpectation.ACCEPT,
                observed_accepted=False,
                failure_kind=None,
                observed_error_type="ValueError",
                diagnostic="diagnostic",
            )

    def test_blank_diagnostic_rejected(self) -> None:
        with self.assertRaises(ConformanceBenchmarkValidationError):
            ConformanceResult(
                case_identifier="case",
                domain=ConformanceDomain.EVIDENCE,
                passed=True,
                expected=ConformanceExpectation.ACCEPT,
                observed_accepted=True,
                failure_kind=None,
                observed_error_type=None,
                diagnostic=" ",
            )

    def test_summary_totals(self) -> None:
        summary = ConformanceSummary(
            results=(
                self.result("a", ConformanceDomain.EVIDENCE, True),
                self.result("b", ConformanceDomain.EVIDENCE, False),
            )
        )
        self.assertEqual(summary.total, 2)
        self.assertEqual(summary.passed, 1)
        self.assertEqual(summary.failed, 1)
        self.assertFalse(summary.success)

    def test_summary_by_domain(self) -> None:
        summary = ConformanceSummary(
            results=(
                self.result("a", ConformanceDomain.EVIDENCE, True),
                self.result("b", ConformanceDomain.FEEDBACK, True),
            )
        )
        self.assertEqual(len(summary.by_domain(ConformanceDomain.EVIDENCE)), 1)
        self.assertEqual(summary.by_domain(ConformanceDomain.EVIDENCE)[0].case_identifier, "a")

    def test_domain_totals_returns_correct_values(self) -> None:
        summary = ConformanceSummary(
            results=(
                self.result("a", ConformanceDomain.EVIDENCE, True),
                self.result("b", ConformanceDomain.EVIDENCE, False),
                self.result("c", ConformanceDomain.FEEDBACK, True),
            )
        )
        totals = summary.domain_totals()
        self.assertEqual(totals[ConformanceDomain.EVIDENCE], (1, 2))
        self.assertEqual(totals[ConformanceDomain.FEEDBACK], (1, 1))
        totals[ConformanceDomain.EVIDENCE] = (0, 0)
        self.assertEqual(summary.domain_totals()[ConformanceDomain.EVIDENCE], (1, 2))


if __name__ == "__main__":
    unittest.main()
