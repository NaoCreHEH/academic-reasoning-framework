import unittest
from unittest.mock import patch

from benchmark.conformance import CONFORMANCE_CASES
from benchmark.conformance.models import ConformanceResult, ConformanceSummary
from benchmark.conformance.enums import (
    ConformanceDomain,
    ConformanceExpectation,
    ConformanceFailureKind,
)
from benchmark.orchestration import (
    BenchmarkSelectionError,
    BenchmarkSuiteStatus,
    run_all_benchmarks,
    run_benchmarks,
)
from benchmark.orchestration.runner import (
    CONFORMANCE_SUITE_ID,
    ROUTING_SUITE_ID,
    _run_conformance_suite,
    _run_routing_suite,
)
from benchmark.routing import ROUTING_REGRESSION_CASES
from benchmark.routing.models import RoutingBenchmarkResult, RoutingBenchmarkSummary


class BenchmarkOrchestrationRunnerTests(unittest.TestCase):
    def test_run_all_benchmarks_returns_two_suites(self) -> None:
        summary = run_all_benchmarks()
        self.assertEqual(summary.total_suites, 2)

    def test_stable_suite_order(self) -> None:
        summary = run_all_benchmarks()
        self.assertEqual(
            [suite.identifier for suite in summary.suites],
            [ROUTING_SUITE_ID, CONFORMANCE_SUITE_ID],
        )

    def test_builtin_suites_pass(self) -> None:
        summary = run_all_benchmarks()
        self.assertIs(summary.get_suite(ROUTING_SUITE_ID).status, BenchmarkSuiteStatus.PASSED)
        self.assertIs(
            summary.get_suite(CONFORMANCE_SUITE_ID).status,
            BenchmarkSuiteStatus.PASSED,
        )

    def test_suite_counts_match_public_case_collections(self) -> None:
        summary = run_all_benchmarks()
        self.assertEqual(
            summary.get_suite(ROUTING_SUITE_ID).total,
            len(ROUTING_REGRESSION_CASES),
        )
        self.assertEqual(
            summary.get_suite(CONFORMANCE_SUITE_ID).total,
            len(CONFORMANCE_CASES),
        )

    def test_total_case_aggregation_correct(self) -> None:
        summary = run_all_benchmarks()
        self.assertEqual(
            summary.total_cases,
            len(ROUTING_REGRESSION_CASES) + len(CONFORMANCE_CASES),
        )

    def test_no_diagnostics_when_all_builtins_pass(self) -> None:
        summary = run_all_benchmarks()
        self.assertEqual(summary.get_suite(ROUTING_SUITE_ID).diagnostics, ())
        self.assertEqual(summary.get_suite(CONFORMANCE_SUITE_ID).diagnostics, ())

    def test_run_benchmarks_routing_returns_only_routing_suite(self) -> None:
        summary = run_benchmarks("routing")
        self.assertEqual([suite.identifier for suite in summary.suites], [ROUTING_SUITE_ID])

    def test_run_benchmarks_conformance_returns_only_conformance_suite(self) -> None:
        summary = run_benchmarks("conformance")
        self.assertEqual(
            [suite.identifier for suite in summary.suites],
            [CONFORMANCE_SUITE_ID],
        )

    def test_run_benchmarks_all_returns_both(self) -> None:
        summary = run_benchmarks("all")
        self.assertEqual(summary.total_suites, 2)

    def test_invalid_suite_raises_selection_error(self) -> None:
        with self.assertRaises(BenchmarkSelectionError):
            run_benchmarks("missing")

    def test_routing_failed_diagnostics_include_only_failed_cases(self) -> None:
        fake_summary = RoutingBenchmarkSummary(
            results=(
                RoutingBenchmarkResult(
                    case_identifier="pass",
                    passed=True,
                    actual_conversion=True,
                    actual_status=None,
                    actual_capability=None,
                    actual_candidates=(),
                    conversion_error_signal=None,
                    diagnostic="passed diagnostic",
                ),
                RoutingBenchmarkResult(
                    case_identifier="fail",
                    passed=False,
                    actual_conversion=True,
                    actual_status=None,
                    actual_capability=None,
                    actual_candidates=(),
                    conversion_error_signal=None,
                    diagnostic="failed diagnostic",
                ),
            )
        )
        with patch("benchmark.orchestration.runner.run_routing_benchmark", return_value=fake_summary):
            suite = _run_routing_suite()
        self.assertEqual(suite.diagnostics, ("fail: failed diagnostic",))

    def test_conformance_failed_diagnostics_include_only_failed_cases(self) -> None:
        fake_summary = ConformanceSummary(
            results=(
                ConformanceResult(
                    case_identifier="pass",
                    domain=ConformanceDomain.EVIDENCE,
                    passed=True,
                    expected=ConformanceExpectation.ACCEPT,
                    observed_accepted=True,
                    failure_kind=None,
                    observed_error_type=None,
                    diagnostic="passed diagnostic",
                ),
                ConformanceResult(
                    case_identifier="fail",
                    domain=ConformanceDomain.EVIDENCE,
                    passed=False,
                    expected=ConformanceExpectation.ACCEPT,
                    observed_accepted=False,
                    failure_kind=ConformanceFailureKind.UNEXPECTED_REJECTION,
                    observed_error_type="ValueError",
                    diagnostic="failed diagnostic",
                ),
            )
        )
        with patch(
            "benchmark.orchestration.runner.run_conformance_benchmark",
            return_value=fake_summary,
        ):
            suite = _run_conformance_suite()
        self.assertEqual(suite.diagnostics, ("fail: failed diagnostic",))


if __name__ == "__main__":
    unittest.main()
