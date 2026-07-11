import unittest

from benchmark.routing.models import (
    RoutingBenchmarkCase,
    RoutingBenchmarkResult,
    RoutingBenchmarkSummary,
    RoutingBenchmarkValidationError,
)
from core.interpretation import SignalKind
from core.routing import RoutingStatus
from tests.test_interpretation_validation import subtask


class RoutingBenchmarkCaseModelTests(unittest.TestCase):
    def test_valid_selected_case(self) -> None:
        case = RoutingBenchmarkCase(
            identifier="selected",
            description="selected case",
            subtask=subtask(),
            expected_conversion=True,
            expected_status=RoutingStatus.SELECTED,
            expected_capability="exam-generation",
            tags=("tag",),
        )
        self.assertEqual(case.expected_capability, "exam-generation")

    def test_valid_ambiguous_case(self) -> None:
        case = RoutingBenchmarkCase(
            identifier="ambiguous",
            description="ambiguous case",
            subtask=subtask(),
            expected_conversion=True,
            expected_status=RoutingStatus.AMBIGUOUS,
            expected_candidates=("a", "b"),
            tags=("tag",),
        )
        self.assertEqual(case.expected_candidates, ("a", "b"))

    def test_valid_no_match_case(self) -> None:
        case = RoutingBenchmarkCase(
            identifier="no-match",
            description="no match case",
            subtask=subtask(),
            expected_conversion=True,
            expected_status=RoutingStatus.NO_MATCH,
            tags=("tag",),
        )
        self.assertIsNone(case.expected_capability)

    def test_valid_conversion_failure_case(self) -> None:
        case = RoutingBenchmarkCase(
            identifier="conversion-failure",
            description="conversion failure case",
            subtask=subtask(),
            expected_conversion=False,
            expected_conversion_error_signal=SignalKind.PRIMARY_ARTIFACT,
            tags=("tag",),
        )
        self.assertFalse(case.expected_conversion)

    def test_blank_identifier_rejected(self) -> None:
        with self.assertRaises(RoutingBenchmarkValidationError):
            RoutingBenchmarkCase(
                identifier=" ",
                description="description",
                subtask=subtask(),
                expected_conversion=True,
                expected_status=RoutingStatus.NO_MATCH,
            )

    def test_blank_description_rejected(self) -> None:
        with self.assertRaises(RoutingBenchmarkValidationError):
            RoutingBenchmarkCase(
                identifier="case",
                description=" ",
                subtask=subtask(),
                expected_conversion=True,
                expected_status=RoutingStatus.NO_MATCH,
            )

    def test_duplicate_tags_rejected(self) -> None:
        with self.assertRaises(RoutingBenchmarkValidationError):
            RoutingBenchmarkCase(
                identifier="case",
                description="description",
                subtask=subtask(),
                expected_conversion=True,
                expected_status=RoutingStatus.NO_MATCH,
                tags=("tag", "tag"),
            )

    def test_blank_tag_rejected(self) -> None:
        with self.assertRaises(RoutingBenchmarkValidationError):
            RoutingBenchmarkCase(
                identifier="case",
                description="description",
                subtask=subtask(),
                expected_conversion=True,
                expected_status=RoutingStatus.NO_MATCH,
                tags=(" ",),
            )

    def test_invalid_selected_expectation_rejected(self) -> None:
        with self.assertRaises(RoutingBenchmarkValidationError):
            RoutingBenchmarkCase(
                identifier="case",
                description="description",
                subtask=subtask(),
                expected_conversion=True,
                expected_status=RoutingStatus.SELECTED,
            )

    def test_invalid_ambiguous_expectation_rejected(self) -> None:
        with self.assertRaises(RoutingBenchmarkValidationError):
            RoutingBenchmarkCase(
                identifier="case",
                description="description",
                subtask=subtask(),
                expected_conversion=True,
                expected_status=RoutingStatus.AMBIGUOUS,
                expected_candidates=("only-one",),
            )

    def test_invalid_no_match_expectation_rejected(self) -> None:
        with self.assertRaises(RoutingBenchmarkValidationError):
            RoutingBenchmarkCase(
                identifier="case",
                description="description",
                subtask=subtask(),
                expected_conversion=True,
                expected_status=RoutingStatus.NO_MATCH,
                expected_candidates=("candidate",),
            )

    def test_conversion_failure_with_routing_expectation_rejected(self) -> None:
        with self.assertRaises(RoutingBenchmarkValidationError):
            RoutingBenchmarkCase(
                identifier="case",
                description="description",
                subtask=subtask(),
                expected_conversion=False,
                expected_status=RoutingStatus.NO_MATCH,
                expected_conversion_error_signal=SignalKind.PRIMARY_ARTIFACT,
            )

    def test_conversion_success_with_error_signal_rejected(self) -> None:
        with self.assertRaises(RoutingBenchmarkValidationError):
            RoutingBenchmarkCase(
                identifier="case",
                description="description",
                subtask=subtask(),
                expected_conversion=True,
                expected_status=RoutingStatus.NO_MATCH,
                expected_conversion_error_signal=SignalKind.PRIMARY_ARTIFACT,
            )


class RoutingBenchmarkResultSummaryTests(unittest.TestCase):
    def test_result_requires_diagnostic(self) -> None:
        with self.assertRaises(RoutingBenchmarkValidationError):
            RoutingBenchmarkResult(
                case_identifier="case",
                passed=False,
                actual_conversion=True,
                actual_status=RoutingStatus.NO_MATCH,
                actual_capability=None,
                actual_candidates=(),
                conversion_error_signal=None,
                diagnostic=" ",
            )

    def test_summary_properties(self) -> None:
        summary = RoutingBenchmarkSummary(
            results=(
                RoutingBenchmarkResult(
                    case_identifier="pass",
                    passed=True,
                    actual_conversion=True,
                    actual_status=RoutingStatus.NO_MATCH,
                    actual_capability=None,
                    actual_candidates=(),
                    conversion_error_signal=None,
                    diagnostic="passed",
                ),
                RoutingBenchmarkResult(
                    case_identifier="fail",
                    passed=False,
                    actual_conversion=True,
                    actual_status=RoutingStatus.NO_MATCH,
                    actual_capability=None,
                    actual_candidates=(),
                    conversion_error_signal=None,
                    diagnostic="failed",
                ),
            )
        )
        self.assertEqual(summary.total, 2)
        self.assertEqual(summary.passed, 1)
        self.assertEqual(summary.failed, 1)
        self.assertFalse(summary.success)


if __name__ == "__main__":
    unittest.main()
