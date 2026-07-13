"""Runner for explicit structural conformance benchmark cases."""

from collections.abc import Iterable

from benchmark.conformance.enums import (
    ConformanceExpectation,
    ConformanceFailureKind,
)
from benchmark.conformance.models import (
    ConformanceCase,
    ConformanceResult,
    ConformanceSummary,
)


def run_conformance_benchmark(
    cases: Iterable[ConformanceCase],
) -> ConformanceSummary:
    """Execute explicit benchmark operations and compare structural outcomes."""

    return ConformanceSummary(results=tuple(_run_case(case) for case in cases))


def _run_case(case: ConformanceCase) -> ConformanceResult:
    try:
        case.operation()
    except Exception as error:
        return _result_for_exception(case, error)
    return _result_for_acceptance(case)


def _result_for_acceptance(case: ConformanceCase) -> ConformanceResult:
    passed = case.expectation is ConformanceExpectation.ACCEPT
    return ConformanceResult(
        case_identifier=case.identifier,
        domain=case.domain,
        passed=passed,
        expected=case.expectation,
        observed_accepted=True,
        failure_kind=None if passed else ConformanceFailureKind.UNEXPECTED_ACCEPTANCE,
        observed_error_type=None,
        diagnostic="accepted as expected" if passed else "operation unexpectedly accepted",
    )


def _result_for_exception(
    case: ConformanceCase,
    error: Exception,
) -> ConformanceResult:
    error_type = type(error).__name__
    if case.expectation is ConformanceExpectation.ACCEPT:
        return ConformanceResult(
            case_identifier=case.identifier,
            domain=case.domain,
            passed=False,
            expected=case.expectation,
            observed_accepted=False,
            failure_kind=ConformanceFailureKind.UNEXPECTED_REJECTION,
            observed_error_type=error_type,
            diagnostic=f"operation unexpectedly raised {error_type}",
        )

    expected_error = case.expected_error
    passed = expected_error is not None and isinstance(error, expected_error)
    return ConformanceResult(
        case_identifier=case.identifier,
        domain=case.domain,
        passed=passed,
        expected=case.expectation,
        observed_accepted=False,
        failure_kind=None if passed else ConformanceFailureKind.WRONG_ERROR_TYPE,
        observed_error_type=error_type,
        diagnostic=(
            f"rejected with expected error {error_type}"
            if passed
            else f"operation raised wrong error type {error_type}"
        ),
    )
