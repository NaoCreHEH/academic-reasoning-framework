import unittest

from benchmark.orchestration import (
    BenchmarkRunSummary,
    BenchmarkSuiteResult,
    BenchmarkSuiteStatus,
    UnknownBenchmarkSuiteError,
)
from benchmark.orchestration.models import BenchmarkOrchestrationValidationError


class BenchmarkOrchestrationModelTests(unittest.TestCase):
    def test_exact_benchmark_suite_status_members(self) -> None:
        self.assertEqual(
            {member.name: member.value for member in BenchmarkSuiteStatus},
            {"PASSED": "passed", "FAILED": "failed"},
        )

    def test_valid_passed_suite(self) -> None:
        suite = BenchmarkSuiteResult(
            identifier="suite",
            status=BenchmarkSuiteStatus.PASSED,
            total=2,
            passed=2,
            failed=0,
        )
        self.assertEqual(suite.passed, 2)

    def test_valid_failed_suite(self) -> None:
        suite = BenchmarkSuiteResult(
            identifier="suite",
            status=BenchmarkSuiteStatus.FAILED,
            total=2,
            passed=1,
            failed=1,
            diagnostics=("case: failed",),
        )
        self.assertEqual(suite.failed, 1)

    def test_blank_identifier_rejected(self) -> None:
        with self.assertRaises(BenchmarkOrchestrationValidationError):
            BenchmarkSuiteResult(
                identifier=" ",
                status=BenchmarkSuiteStatus.PASSED,
                total=0,
                passed=0,
                failed=0,
            )

    def test_negative_total_rejected(self) -> None:
        with self.assertRaises(BenchmarkOrchestrationValidationError):
            BenchmarkSuiteResult("suite", BenchmarkSuiteStatus.PASSED, -1, 0, 0)

    def test_negative_passed_rejected(self) -> None:
        with self.assertRaises(BenchmarkOrchestrationValidationError):
            BenchmarkSuiteResult("suite", BenchmarkSuiteStatus.FAILED, 1, -1, 2)

    def test_negative_failed_rejected(self) -> None:
        with self.assertRaises(BenchmarkOrchestrationValidationError):
            BenchmarkSuiteResult("suite", BenchmarkSuiteStatus.PASSED, 1, 2, -1)

    def test_inconsistent_counts_rejected(self) -> None:
        with self.assertRaises(BenchmarkOrchestrationValidationError):
            BenchmarkSuiteResult("suite", BenchmarkSuiteStatus.PASSED, 3, 1, 1)

    def test_passed_with_failures_rejected(self) -> None:
        with self.assertRaises(BenchmarkOrchestrationValidationError):
            BenchmarkSuiteResult("suite", BenchmarkSuiteStatus.PASSED, 2, 1, 1)

    def test_failed_without_failures_rejected(self) -> None:
        with self.assertRaises(BenchmarkOrchestrationValidationError):
            BenchmarkSuiteResult("suite", BenchmarkSuiteStatus.FAILED, 2, 2, 0)

    def test_blank_diagnostic_rejected(self) -> None:
        with self.assertRaises(BenchmarkOrchestrationValidationError):
            BenchmarkSuiteResult(
                "suite",
                BenchmarkSuiteStatus.FAILED,
                1,
                0,
                1,
                diagnostics=(" ",),
            )

    def test_duplicate_diagnostics_rejected(self) -> None:
        with self.assertRaises(BenchmarkOrchestrationValidationError):
            BenchmarkSuiteResult(
                "suite",
                BenchmarkSuiteStatus.FAILED,
                2,
                0,
                2,
                diagnostics=("case: failed", "case: failed"),
            )

    def test_valid_run_summary_and_properties(self) -> None:
        summary = BenchmarkRunSummary(
            suites=(
                BenchmarkSuiteResult("a", BenchmarkSuiteStatus.PASSED, 2, 2, 0),
                BenchmarkSuiteResult(
                    "b",
                    BenchmarkSuiteStatus.FAILED,
                    3,
                    1,
                    2,
                    diagnostics=("b1: failed", "b2: failed"),
                ),
            )
        )
        self.assertEqual(summary.total_suites, 2)
        self.assertEqual(summary.passed_suites, 1)
        self.assertEqual(summary.failed_suites, 1)
        self.assertFalse(summary.success)
        self.assertEqual(summary.total_cases, 5)
        self.assertEqual(summary.passed_cases, 3)
        self.assertEqual(summary.failed_cases, 2)
        self.assertEqual(summary.get_suite("a").identifier, "a")

    def test_duplicate_suite_identifiers_rejected(self) -> None:
        with self.assertRaises(BenchmarkOrchestrationValidationError):
            BenchmarkRunSummary(
                suites=(
                    BenchmarkSuiteResult("a", BenchmarkSuiteStatus.PASSED, 1, 1, 0),
                    BenchmarkSuiteResult("a", BenchmarkSuiteStatus.PASSED, 1, 1, 0),
                )
            )

    def test_unknown_suite_raises_specific_error(self) -> None:
        summary = BenchmarkRunSummary(
            suites=(BenchmarkSuiteResult("a", BenchmarkSuiteStatus.PASSED, 1, 1, 0),)
        )
        with self.assertRaises(UnknownBenchmarkSuiteError):
            summary.get_suite("missing")


if __name__ == "__main__":
    unittest.main()
