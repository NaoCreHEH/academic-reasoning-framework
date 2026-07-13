"""Dataclasses for structural conformance benchmark cases and results."""

from collections.abc import Callable
from dataclasses import dataclass
import re

from benchmark.conformance.enums import (
    ConformanceDomain,
    ConformanceExpectation,
    ConformanceFailureKind,
)


class ConformanceBenchmarkValidationError(ValueError):
    """Raised when benchmark definitions are structurally invalid."""


RFC_REFERENCE_RE = re.compile(r"^RFC-\d{4}$")


def _require_non_empty(value: str | None, field_name: str) -> None:
    if value is None or not value.strip():
        raise ConformanceBenchmarkValidationError(f"{field_name} cannot be blank")


def _validate_unique_strings(values: tuple[str, ...], field_name: str) -> None:
    seen: set[str] = set()
    for value in values:
        _require_non_empty(value, field_name)
        if value in seen:
            raise ConformanceBenchmarkValidationError(
                f"{field_name} contains duplicate value: {value}"
            )
        seen.add(value)


@dataclass(frozen=True)
class ConformanceCase:
    """One structural conformance expectation."""

    identifier: str
    description: str
    domain: ConformanceDomain
    expectation: ConformanceExpectation
    operation: Callable[[], object | None]
    expected_error: type[Exception] | None = None
    tags: tuple[str, ...] = ()
    rfc_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty(self.identifier, "identifier")
        _require_non_empty(self.description, "description")
        if not callable(self.operation):
            raise ConformanceBenchmarkValidationError("operation must be callable")
        _validate_unique_strings(self.tags, "tags")
        _validate_unique_strings(self.rfc_references, "rfc_references")
        for reference in self.rfc_references:
            if RFC_REFERENCE_RE.fullmatch(reference) is None:
                raise ConformanceBenchmarkValidationError(
                    f"invalid RFC reference format: {reference}"
                )

        if self.expectation is ConformanceExpectation.ACCEPT:
            if self.expected_error is not None:
                raise ConformanceBenchmarkValidationError(
                    "ACCEPT cases must not specify expected_error"
                )
        elif self.expectation is ConformanceExpectation.REJECT:
            if self.expected_error is None:
                raise ConformanceBenchmarkValidationError(
                    "REJECT cases require expected_error"
                )
            if not isinstance(self.expected_error, type) or not issubclass(
                self.expected_error,
                Exception,
            ):
                raise ConformanceBenchmarkValidationError(
                    "expected_error must be an Exception subclass"
                )
        else:
            raise ConformanceBenchmarkValidationError(
                f"unknown expectation: {self.expectation}"
            )


@dataclass(frozen=True)
class ConformanceResult:
    """One structural conformance benchmark result."""

    case_identifier: str
    domain: ConformanceDomain
    passed: bool
    expected: ConformanceExpectation
    observed_accepted: bool
    failure_kind: ConformanceFailureKind | None
    observed_error_type: str | None
    diagnostic: str

    def __post_init__(self) -> None:
        _require_non_empty(self.case_identifier, "case_identifier")
        _require_non_empty(self.diagnostic, "diagnostic")
        if self.observed_error_type is not None:
            _require_non_empty(self.observed_error_type, "observed_error_type")
        if self.passed and self.failure_kind is not None:
            raise ConformanceBenchmarkValidationError(
                "passed results must not have failure_kind"
            )
        if not self.passed and self.failure_kind is None:
            raise ConformanceBenchmarkValidationError(
                "failed results require failure_kind"
            )


@dataclass(frozen=True)
class ConformanceSummary:
    """Aggregate structural conformance benchmark results."""

    results: tuple[ConformanceResult, ...]

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

    def by_domain(self, domain: ConformanceDomain) -> tuple[ConformanceResult, ...]:
        return tuple(result for result in self.results if result.domain is domain)

    def domain_totals(self) -> dict[ConformanceDomain, tuple[int, int]]:
        totals: dict[ConformanceDomain, tuple[int, int]] = {}
        for domain in ConformanceDomain:
            results = self.by_domain(domain)
            totals[domain] = (
                sum(1 for result in results if result.passed),
                len(results),
            )
        return totals
