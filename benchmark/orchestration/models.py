"""Models for unified benchmark orchestration."""

from dataclasses import dataclass
from enum import Enum


class BenchmarkSelectionError(ValueError):
    """Raised when an unknown benchmark suite selection is requested."""


class UnknownBenchmarkSuiteError(KeyError):
    """Raised when a suite identifier is absent from a run summary."""


class BenchmarkOrchestrationValidationError(ValueError):
    """Raised when orchestration result objects are structurally invalid."""


class BenchmarkSuiteStatus(str, Enum):
    """Overall benchmark suite status."""

    PASSED = "passed"
    FAILED = "failed"


def _require_non_empty(value: str | None, field_name: str) -> None:
    if value is None or not value.strip():
        raise BenchmarkOrchestrationValidationError(f"{field_name} cannot be blank")


def _validate_diagnostics(diagnostics: tuple[str, ...]) -> None:
    seen: set[str] = set()
    for diagnostic in diagnostics:
        _require_non_empty(diagnostic, "diagnostics")
        if diagnostic in seen:
            raise BenchmarkOrchestrationValidationError(
                f"diagnostics contains duplicate value: {diagnostic}"
            )
        seen.add(diagnostic)


@dataclass(frozen=True)
class BenchmarkSuiteResult:
    """Unified result for one benchmark suite."""

    identifier: str
    status: BenchmarkSuiteStatus
    total: int
    passed: int
    failed: int
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty(self.identifier, "identifier")
        for field_name in ("total", "passed", "failed"):
            if getattr(self, field_name) < 0:
                raise BenchmarkOrchestrationValidationError(
                    f"{field_name} cannot be negative"
                )
        if self.passed + self.failed != self.total:
            raise BenchmarkOrchestrationValidationError(
                "passed + failed must equal total"
            )
        if self.status is BenchmarkSuiteStatus.PASSED and self.failed != 0:
            raise BenchmarkOrchestrationValidationError(
                "PASSED suites cannot have failures"
            )
        if self.status is BenchmarkSuiteStatus.FAILED and self.failed == 0:
            raise BenchmarkOrchestrationValidationError(
                "FAILED suites require at least one failure"
            )
        _validate_diagnostics(self.diagnostics)


@dataclass(frozen=True)
class BenchmarkRunSummary:
    """Unified result for a benchmark run containing one or more suites."""

    suites: tuple[BenchmarkSuiteResult, ...]

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for suite in self.suites:
            if suite.identifier in seen:
                raise BenchmarkOrchestrationValidationError(
                    f"duplicate suite identifier: {suite.identifier}"
                )
            seen.add(suite.identifier)

    @property
    def total_suites(self) -> int:
        return len(self.suites)

    @property
    def passed_suites(self) -> int:
        return sum(
            1 for suite in self.suites if suite.status is BenchmarkSuiteStatus.PASSED
        )

    @property
    def failed_suites(self) -> int:
        return self.total_suites - self.passed_suites

    @property
    def success(self) -> bool:
        return self.failed_suites == 0

    @property
    def total_cases(self) -> int:
        return sum(suite.total for suite in self.suites)

    @property
    def passed_cases(self) -> int:
        return sum(suite.passed for suite in self.suites)

    @property
    def failed_cases(self) -> int:
        return sum(suite.failed for suite in self.suites)

    def get_suite(self, identifier: str) -> BenchmarkSuiteResult:
        for suite in self.suites:
            if suite.identifier == identifier:
                return suite
        raise UnknownBenchmarkSuiteError(f"unknown benchmark suite: {identifier}")
