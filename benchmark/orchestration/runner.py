"""Unified orchestration for ARF benchmark suites."""

from benchmark.conformance import CONFORMANCE_CASES, run_conformance_benchmark
from benchmark.routing import ROUTING_REGRESSION_CASES, run_routing_benchmark
from core.routing import StructuredRoutingEngine, build_default_academic_registry

from benchmark.orchestration.models import (
    BenchmarkRunSummary,
    BenchmarkSelectionError,
    BenchmarkSuiteResult,
    BenchmarkSuiteStatus,
)


ROUTING_SUITE_ID = "routing-regression"
CONFORMANCE_SUITE_ID = "structural-conformance"


def run_all_benchmarks() -> BenchmarkRunSummary:
    """Run all benchmark suites in stable order."""

    return BenchmarkRunSummary(
        suites=(
            _run_routing_suite(),
            _run_conformance_suite(),
        )
    )


def run_benchmarks(suite: str = "all") -> BenchmarkRunSummary:
    """Run selected benchmark suites."""

    if suite == "all":
        return run_all_benchmarks()
    if suite == "routing":
        return BenchmarkRunSummary(suites=(_run_routing_suite(),))
    if suite == "conformance":
        return BenchmarkRunSummary(suites=(_run_conformance_suite(),))
    raise BenchmarkSelectionError(f"unknown benchmark suite selection: {suite}")


def _run_routing_suite() -> BenchmarkSuiteResult:
    engine = StructuredRoutingEngine(build_default_academic_registry())
    summary = run_routing_benchmark(ROUTING_REGRESSION_CASES, engine)
    diagnostics = tuple(
        f"{result.case_identifier}: {result.diagnostic}"
        for result in summary.results
        if not result.passed
    )
    return BenchmarkSuiteResult(
        identifier=ROUTING_SUITE_ID,
        status=_status_from_failed(summary.failed),
        total=summary.total,
        passed=summary.passed,
        failed=summary.failed,
        diagnostics=diagnostics,
    )


def _run_conformance_suite() -> BenchmarkSuiteResult:
    summary = run_conformance_benchmark(CONFORMANCE_CASES)
    diagnostics = tuple(
        f"{result.case_identifier}: {result.diagnostic}"
        for result in summary.results
        if not result.passed
    )
    return BenchmarkSuiteResult(
        identifier=CONFORMANCE_SUITE_ID,
        status=_status_from_failed(summary.failed),
        total=summary.total,
        passed=summary.passed,
        failed=summary.failed,
        diagnostics=diagnostics,
    )


def _status_from_failed(failed: int) -> BenchmarkSuiteStatus:
    if failed == 0:
        return BenchmarkSuiteStatus.PASSED
    return BenchmarkSuiteStatus.FAILED
