"""Structural conformance benchmark public API."""

from benchmark.conformance.cases import CONFORMANCE_CASES
from benchmark.conformance.enums import (
    ConformanceDomain,
    ConformanceExpectation,
    ConformanceFailureKind,
)
from benchmark.conformance.models import (
    ConformanceCase,
    ConformanceResult,
    ConformanceSummary,
)
from benchmark.conformance.runner import run_conformance_benchmark

__all__ = [
    "CONFORMANCE_CASES",
    "ConformanceCase",
    "ConformanceDomain",
    "ConformanceExpectation",
    "ConformanceFailureKind",
    "ConformanceResult",
    "ConformanceSummary",
    "run_conformance_benchmark",
]
