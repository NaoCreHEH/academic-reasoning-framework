"""Runner for interpretation-to-routing regression benchmark cases."""

from collections.abc import Iterable

from core.interpretation import InterpretationConversionError, to_routing_request
from core.routing import RoutingStatus, StructuredRoutingEngine

from benchmark.routing.models import (
    RoutingBenchmarkCase,
    RoutingBenchmarkResult,
    RoutingBenchmarkSummary,
)


def run_routing_benchmark(
    cases: Iterable[RoutingBenchmarkCase],
    engine: StructuredRoutingEngine,
) -> RoutingBenchmarkSummary:
    """Run benchmark cases through conversion and structured routing."""

    return RoutingBenchmarkSummary(
        results=tuple(_run_case(case, engine) for case in cases)
    )


def _run_case(
    case: RoutingBenchmarkCase,
    engine: StructuredRoutingEngine,
) -> RoutingBenchmarkResult:
    try:
        request = to_routing_request(case.subtask)
    except InterpretationConversionError as error:
        signal_kind = error.signal_kind
        passed = (
            not case.expected_conversion
            and signal_kind == case.expected_conversion_error_signal
        )
        return RoutingBenchmarkResult(
            case_identifier=case.identifier,
            passed=passed,
            actual_conversion=False,
            actual_status=None,
            actual_capability=None,
            actual_candidates=(),
            conversion_error_signal=signal_kind,
            diagnostic=(
                "conversion failed as expected"
                if passed
                else f"conversion failed for unexpected signal: {signal_kind}"
            ),
        )

    decision = engine.route(request)
    status = decision.status
    capability = decision.trace.primary_capability
    candidates = decision.candidate_capabilities
    passed = (
        case.expected_conversion
        and status == case.expected_status
        and capability == case.expected_capability
        and candidates == case.expected_candidates
    )
    return RoutingBenchmarkResult(
        case_identifier=case.identifier,
        passed=passed,
        actual_conversion=True,
        actual_status=status,
        actual_capability=capability,
        actual_candidates=candidates,
        conversion_error_signal=None,
        diagnostic="passed" if passed else _diagnostic(case, status, capability, candidates),
    )


def _diagnostic(
    case: RoutingBenchmarkCase,
    status: RoutingStatus,
    capability: str | None,
    candidates: tuple[str, ...],
) -> str:
    return (
        f"expected status={case.expected_status}, capability={case.expected_capability}, "
        f"candidates={case.expected_candidates}; actual status={status}, "
        f"capability={capability}, candidates={candidates}"
    )
