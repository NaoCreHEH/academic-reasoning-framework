"""Enums for Claude Code adapter evaluation."""

from enum import Enum


class ClaudeEvaluationDimension(Enum):
    """Separately evaluated live adapter dimensions."""

    DISPATCH = "dispatch"
    RESPONSE_CONTRACT = "response_contract"


class ClaudeEvaluationStatus(Enum):
    """Per-dimension evaluation status."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ResponseMarkerMatchMode(Enum):
    """How a response marker matches its patterns."""

    ANY = "any"
    ALL = "all"
