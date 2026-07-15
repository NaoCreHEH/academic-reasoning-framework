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


class ClaudeCaseArtifactRequirement(Enum):
    """Whether a live case requires an external artifact to execute fully."""

    NONE = "none"
    OPTIONAL = "optional"
    REQUIRED = "required"


class ResponseMarkerMatchMode(Enum):
    """How a response marker matches its patterns."""

    ANY = "any"
    ALL = "all"
