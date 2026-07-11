"""Dataclasses for routing regression benchmark cases and results."""

from dataclasses import dataclass

from core.interpretation import InterpretedSubtask, SignalKind
from core.interpretation.validation import validate_string_tuple
from core.routing import RoutingStatus


class RoutingBenchmarkValidationError(ValueError):
    """Raised when benchmark definitions are structurally invalid."""


def _require_non_empty(value: str | None, field_name: str) -> None:
    if value is None or not value.strip():
        raise RoutingBenchmarkValidationError(f"{field_name} cannot be blank")


def _validate_unique_strings(values: tuple[str, ...], field_name: str) -> None:
    try:
        validate_string_tuple(values, field_name)
    except ValueError as error:
        raise RoutingBenchmarkValidationError(str(error)) from error


@dataclass(frozen=True)
class RoutingBenchmarkCase:
    """One interpretation-to-routing regression benchmark case."""

    identifier: str
    description: str
    subtask: InterpretedSubtask
    expected_conversion: bool
    expected_status: RoutingStatus | None = None
    expected_capability: str | None = None
    expected_candidates: tuple[str, ...] = ()
    expected_conversion_error_signal: SignalKind | None = None
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty(self.identifier, "identifier")
        _require_non_empty(self.description, "description")
        _validate_unique_strings(self.tags, "tags")
        _validate_unique_strings(self.expected_candidates, "expected_candidates")
        if self.expected_capability is not None:
            _require_non_empty(self.expected_capability, "expected_capability")

        if not self.expected_conversion:
            if self.expected_status is not None:
                raise RoutingBenchmarkValidationError(
                    "conversion-failure cases must not expect routing status"
                )
            if self.expected_capability is not None:
                raise RoutingBenchmarkValidationError(
                    "conversion-failure cases must not expect capability"
                )
            if self.expected_candidates:
                raise RoutingBenchmarkValidationError(
                    "conversion-failure cases must not expect candidates"
                )
            if self.expected_conversion_error_signal is None:
                raise RoutingBenchmarkValidationError(
                    "conversion-failure cases require expected conversion error signal"
                )
            return

        if self.expected_conversion_error_signal is not None:
            raise RoutingBenchmarkValidationError(
                "conversion-success cases must not expect conversion errors"
            )
        if self.expected_status is None:
            raise RoutingBenchmarkValidationError(
                "conversion-success cases require expected routing status"
            )
        if self.expected_status is RoutingStatus.SELECTED:
            if self.expected_capability is None:
                raise RoutingBenchmarkValidationError(
                    "selected cases require expected capability"
                )
            if self.expected_candidates:
                raise RoutingBenchmarkValidationError(
                    "selected cases must not expect candidates"
                )
        elif self.expected_status is RoutingStatus.AMBIGUOUS:
            if self.expected_capability is not None:
                raise RoutingBenchmarkValidationError(
                    "ambiguous cases must not expect capability"
                )
            if len(self.expected_candidates) < 2:
                raise RoutingBenchmarkValidationError(
                    "ambiguous cases require at least two expected candidates"
                )
        elif self.expected_status is RoutingStatus.NO_MATCH:
            if self.expected_capability is not None:
                raise RoutingBenchmarkValidationError(
                    "no-match cases must not expect capability"
                )
            if self.expected_candidates:
                raise RoutingBenchmarkValidationError(
                    "no-match cases must not expect candidates"
                )


@dataclass(frozen=True)
class RoutingBenchmarkResult:
    """One benchmark case result."""

    case_identifier: str
    passed: bool
    actual_conversion: bool
    actual_status: RoutingStatus | None
    actual_capability: str | None
    actual_candidates: tuple[str, ...]
    conversion_error_signal: SignalKind | None
    diagnostic: str

    def __post_init__(self) -> None:
        _require_non_empty(self.case_identifier, "case_identifier")
        _require_non_empty(self.diagnostic, "diagnostic")
        _validate_unique_strings(self.actual_candidates, "actual_candidates")


@dataclass(frozen=True)
class RoutingBenchmarkSummary:
    """Aggregate benchmark results."""

    results: tuple[RoutingBenchmarkResult, ...]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def success(self) -> bool:
        return self.failed == 0
