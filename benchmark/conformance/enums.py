"""Enums for the structural conformance benchmark."""

from enum import Enum


class ConformanceDomain(str, Enum):
    """Implemented structural RFC contract area."""

    EVIDENCE = "evidence"
    CLAIM = "claim"
    CONFIDENCE = "confidence"
    FEEDBACK = "feedback"
    INTERPRETATION = "interpretation"


class ConformanceExpectation(str, Enum):
    """Expected construction or validation outcome."""

    ACCEPT = "accept"
    REJECT = "reject"


class ConformanceFailureKind(str, Enum):
    """Benchmark harness failure categories."""

    CONSTRUCTION_ERROR = "construction_error"
    VALIDATION_ERROR = "validation_error"
    UNEXPECTED_ACCEPTANCE = "unexpected_acceptance"
    UNEXPECTED_REJECTION = "unexpected_rejection"
    WRONG_ERROR_TYPE = "wrong_error_type"
