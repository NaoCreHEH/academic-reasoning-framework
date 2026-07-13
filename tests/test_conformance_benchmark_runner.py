import unittest

from benchmark.conformance import (
    CONFORMANCE_CASES,
    ConformanceCase,
    ConformanceDomain,
    ConformanceExpectation,
    ConformanceFailureKind,
    ConformanceResult,
    ConformanceSummary,
    run_conformance_benchmark,
)


class CustomError(ValueError):
    pass


class CustomSubError(CustomError):
    pass


def accepts():
    return None


def raises_custom(message: str = "first"):
    raise CustomError(message)


def raises_subclass():
    raise CustomSubError("subclass")


def raises_type_error():
    raise TypeError("wrong")


def raises_keyboard_interrupt():
    raise KeyboardInterrupt()


def case(
    *,
    identifier: str = "case",
    expectation: ConformanceExpectation = ConformanceExpectation.ACCEPT,
    operation=accepts,
    expected_error: type[Exception] | None = None,
) -> ConformanceCase:
    return ConformanceCase(
        identifier=identifier,
        description="runner test case",
        domain=ConformanceDomain.EVIDENCE,
        expectation=expectation,
        operation=operation,
        expected_error=expected_error,
        tags=("test",),
        rfc_references=("RFC-0002",),
    )


class ConformanceBenchmarkRunnerTests(unittest.TestCase):
    def test_all_builtin_conformance_cases_pass(self) -> None:
        summary = run_conformance_benchmark(CONFORMANCE_CASES)
        self.assertTrue(summary.success)
        self.assertEqual(summary.passed, summary.total)

    def test_accept_operation_returning_normally_passes(self) -> None:
        result = run_conformance_benchmark((case(),)).results[0]
        self.assertTrue(result.passed)
        self.assertTrue(result.observed_accepted)

    def test_accept_operation_raising_fails_with_unexpected_rejection(self) -> None:
        result = run_conformance_benchmark(
            (case(operation=raises_custom),)
        ).results[0]
        self.assertFalse(result.passed)
        self.assertIs(result.failure_kind, ConformanceFailureKind.UNEXPECTED_REJECTION)

    def test_reject_operation_raising_expected_type_passes(self) -> None:
        result = run_conformance_benchmark(
            (
                case(
                    expectation=ConformanceExpectation.REJECT,
                    operation=raises_custom,
                    expected_error=CustomError,
                ),
            )
        ).results[0]
        self.assertTrue(result.passed)
        self.assertEqual(result.observed_error_type, "CustomError")

    def test_reject_operation_returning_normally_fails_with_unexpected_acceptance(self) -> None:
        result = run_conformance_benchmark(
            (
                case(
                    expectation=ConformanceExpectation.REJECT,
                    operation=accepts,
                    expected_error=CustomError,
                ),
            )
        ).results[0]
        self.assertFalse(result.passed)
        self.assertIs(result.failure_kind, ConformanceFailureKind.UNEXPECTED_ACCEPTANCE)

    def test_reject_operation_raising_wrong_type_fails_with_wrong_error_type(self) -> None:
        result = run_conformance_benchmark(
            (
                case(
                    expectation=ConformanceExpectation.REJECT,
                    operation=raises_type_error,
                    expected_error=CustomError,
                ),
            )
        ).results[0]
        self.assertFalse(result.passed)
        self.assertIs(result.failure_kind, ConformanceFailureKind.WRONG_ERROR_TYPE)

    def test_subclass_of_expected_error_is_accepted(self) -> None:
        result = run_conformance_benchmark(
            (
                case(
                    expectation=ConformanceExpectation.REJECT,
                    operation=raises_subclass,
                    expected_error=CustomError,
                ),
            )
        ).results[0]
        self.assertTrue(result.passed)

    def test_exception_messages_are_not_benchmark_truth(self) -> None:
        first = case(
            identifier="first",
            expectation=ConformanceExpectation.REJECT,
            operation=lambda: raises_custom("first message"),
            expected_error=CustomError,
        )
        second = case(
            identifier="second",
            expectation=ConformanceExpectation.REJECT,
            operation=lambda: raises_custom("second message"),
            expected_error=CustomError,
        )
        results = run_conformance_benchmark((first, second)).results
        self.assertEqual(
            [(result.passed, result.failure_kind, result.observed_error_type) for result in results],
            [(True, None, "CustomError"), (True, None, "CustomError")],
        )

    def test_keyboard_interrupt_is_not_swallowed(self) -> None:
        with self.assertRaises(KeyboardInterrupt):
            run_conformance_benchmark((case(operation=raises_keyboard_interrupt),))

    def test_summary_contains_one_result_per_case(self) -> None:
        summary = run_conformance_benchmark(CONFORMANCE_CASES)
        self.assertEqual(summary.total, len(CONFORMANCE_CASES))

    def test_domain_summaries_are_correct(self) -> None:
        summary = run_conformance_benchmark(CONFORMANCE_CASES)
        totals = summary.domain_totals()
        self.assertEqual(sum(total for _, total in totals.values()), summary.total)
        for domain in ConformanceDomain:
            passed, total = totals[domain]
            domain_results = summary.by_domain(domain)
            self.assertEqual(passed, sum(1 for result in domain_results if result.passed))
            self.assertEqual(total, len(domain_results))
            self.assertGreater(total, 0)

    def test_domain_summaries_count_failed_results_independently(self) -> None:
        summary = ConformanceSummary(
            results=(
                ConformanceResult(
                    case_identifier="pass",
                    domain=ConformanceDomain.EVIDENCE,
                    passed=True,
                    expected=ConformanceExpectation.ACCEPT,
                    observed_accepted=True,
                    failure_kind=None,
                    observed_error_type=None,
                    diagnostic="passed",
                ),
                ConformanceResult(
                    case_identifier="fail",
                    domain=ConformanceDomain.EVIDENCE,
                    passed=False,
                    expected=ConformanceExpectation.ACCEPT,
                    observed_accepted=False,
                    failure_kind=ConformanceFailureKind.UNEXPECTED_REJECTION,
                    observed_error_type="CustomError",
                    diagnostic="failed",
                ),
            )
        )
        self.assertEqual(summary.domain_totals()[ConformanceDomain.EVIDENCE], (1, 2))

    def test_diagnostic_exists_for_every_result(self) -> None:
        summary = run_conformance_benchmark(CONFORMANCE_CASES)
        for result in summary.results:
            with self.subTest(case=result.case_identifier):
                self.assertTrue(result.diagnostic.strip())


if __name__ == "__main__":
    unittest.main()
