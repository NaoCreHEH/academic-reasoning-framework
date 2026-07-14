"""Dataclasses for Claude Code adapter evaluation."""

from dataclasses import dataclass
import re

from benchmark.adapters.claude_code.enums import (
    ClaudeEvaluationStatus,
    ResponseMarkerMatchMode,
)


class ClaudeAdapterEvaluationValidationError(ValueError):
    """Raised when Claude adapter evaluation definitions are invalid."""


def _require_non_empty(value: str | None, field_name: str) -> None:
    if value is None or not value.strip():
        raise ClaudeAdapterEvaluationValidationError(f"{field_name} cannot be blank")


def _validate_unique_strings(values: tuple[str, ...], field_name: str) -> None:
    seen: set[str] = set()
    for value in values:
        _require_non_empty(value, field_name)
        if value in seen:
            raise ClaudeAdapterEvaluationValidationError(
                f"{field_name} cannot contain duplicates"
            )
        seen.add(value)


@dataclass(frozen=True)
class ResponseMarker:
    """Observable response marker matched mechanically against stdout."""

    identifier: str
    patterns: tuple[str, ...]
    match_mode: ResponseMarkerMatchMode

    def __post_init__(self) -> None:
        _require_non_empty(self.identifier, "identifier")
        if not self.patterns:
            raise ClaudeAdapterEvaluationValidationError(
                "patterns must contain at least one value"
            )
        _validate_unique_strings(self.patterns, "patterns")
        if not isinstance(self.match_mode, ResponseMarkerMatchMode):
            raise ClaudeAdapterEvaluationValidationError(
                "match_mode must be a ResponseMarkerMatchMode"
            )


@dataclass(frozen=True)
class ClaudeAdapterCase:
    """One live Claude Code adapter evaluation case."""

    identifier: str
    prompt: str
    expected_skill: str
    forbidden_skills: tuple[str, ...] = ()
    response_markers: tuple[ResponseMarker, ...] = ()
    response_forbidden_patterns: tuple[str, ...] = ()
    response_forbidden_regexes: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    notes: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.identifier, "identifier")
        _require_non_empty(self.prompt, "prompt")
        _require_non_empty(self.expected_skill, "expected_skill")
        _validate_unique_strings(self.forbidden_skills, "forbidden_skills")
        if self.expected_skill in self.forbidden_skills:
            raise ClaudeAdapterEvaluationValidationError(
                "expected_skill cannot appear in forbidden_skills"
            )
        _validate_unique_strings(
            tuple(marker.identifier for marker in self.response_markers),
            "response marker identifiers",
        )
        _validate_unique_strings(
            self.response_forbidden_patterns,
            "response_forbidden_patterns",
        )
        _validate_unique_strings(
            self.response_forbidden_regexes,
            "response_forbidden_regexes",
        )
        for pattern in self.response_forbidden_regexes:
            try:
                re.compile(pattern)
            except re.error as error:
                raise ClaudeAdapterEvaluationValidationError(
                    f"invalid forbidden regex: {pattern}"
                ) from error
        _validate_unique_strings(self.tags, "tags")
        if self.notes is not None:
            _require_non_empty(self.notes, "notes")


@dataclass(frozen=True)
class ClaudeInvocationResult:
    """Raw process result from a Claude Code invocation."""

    returncode: int
    stdout: str
    stderr: str

    def __post_init__(self) -> None:
        if not isinstance(self.returncode, int):
            raise ClaudeAdapterEvaluationValidationError("returncode must be an int")
        if not isinstance(self.stdout, str):
            raise ClaudeAdapterEvaluationValidationError("stdout must be a string")
        if not isinstance(self.stderr, str):
            raise ClaudeAdapterEvaluationValidationError("stderr must be a string")


@dataclass(frozen=True)
class ClaudeInvocationObservation:
    """Typed observable result from a Claude adapter invocation."""

    available: bool
    response_text: str | None = None
    observed_skill: str | None = None
    observed_skills: tuple[str, ...] = ()
    process_result: ClaudeInvocationResult | None = None
    unavailable_reason: str | None = None
    dispatch_observation_reason: str | None = None
    invocation_error: str | None = None
    plugin_loaded: bool | None = None
    plugin_load_error: str | None = None
    duration_seconds: float | None = None
    raw_response_available: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.available, bool):
            raise ClaudeAdapterEvaluationValidationError("available must be a bool")
        if not isinstance(self.raw_response_available, bool):
            raise ClaudeAdapterEvaluationValidationError(
                "raw_response_available must be a bool"
            )
        if self.plugin_loaded is not None and not isinstance(self.plugin_loaded, bool):
            raise ClaudeAdapterEvaluationValidationError(
                "plugin_loaded must be a bool or None"
            )
        if self.response_text is not None and not isinstance(self.response_text, str):
            raise ClaudeAdapterEvaluationValidationError(
                "response_text must be a string when set"
            )
        if self.observed_skill is not None:
            _require_non_empty(self.observed_skill, "observed_skill")
        for observed in self.observed_skills:
            _require_non_empty(observed, "observed_skills")
        if self.observed_skill is not None and self.observed_skills:
            if self.observed_skills != (self.observed_skill,):
                raise ClaudeAdapterEvaluationValidationError(
                    "observed_skill must match observed_skills when both are set"
                )
        if self.available:
            if self.unavailable_reason is not None:
                raise ClaudeAdapterEvaluationValidationError(
                    "available observations must not include unavailable_reason"
                )
        else:
            _require_non_empty(self.unavailable_reason, "unavailable_reason")
            if self.invocation_error is not None:
                raise ClaudeAdapterEvaluationValidationError(
                    "unavailable observations must not include invocation_error"
                )
        if self.dispatch_observation_reason is not None:
            _require_non_empty(
                self.dispatch_observation_reason,
                "dispatch_observation_reason",
            )
        if self.invocation_error is not None:
            _require_non_empty(self.invocation_error, "invocation_error")
        if self.plugin_load_error is not None:
            _require_non_empty(self.plugin_load_error, "plugin_load_error")
            if self.plugin_loaded is not False:
                raise ClaudeAdapterEvaluationValidationError(
                    "plugin_load_error requires plugin_loaded=False"
                )
        if self.duration_seconds is not None:
            if not isinstance(self.duration_seconds, int | float):
                raise ClaudeAdapterEvaluationValidationError(
                    "duration_seconds must be numeric"
                )
            if self.duration_seconds < 0:
                raise ClaudeAdapterEvaluationValidationError(
                    "duration_seconds cannot be negative"
                )


@dataclass(frozen=True)
class ClaudeAdapterCaseResult:
    """Per-case result with dispatch and response-contract kept separate."""

    case_identifier: str
    dispatch_status: ClaudeEvaluationStatus
    response_contract_status: ClaudeEvaluationStatus
    observed_skill: str | None
    failed_markers: tuple[str, ...] = ()
    matched_forbidden_patterns: tuple[str, ...] = ()
    diagnostic: str = "evaluated"

    def __post_init__(self) -> None:
        _require_non_empty(self.case_identifier, "case_identifier")
        if not isinstance(self.dispatch_status, ClaudeEvaluationStatus):
            raise ClaudeAdapterEvaluationValidationError(
                "dispatch_status must be a ClaudeEvaluationStatus"
            )
        if not isinstance(self.response_contract_status, ClaudeEvaluationStatus):
            raise ClaudeAdapterEvaluationValidationError(
                "response_contract_status must be a ClaudeEvaluationStatus"
            )
        if self.observed_skill is not None:
            _require_non_empty(self.observed_skill, "observed_skill")
        _validate_unique_strings(self.failed_markers, "failed_markers")
        _validate_unique_strings(
            self.matched_forbidden_patterns,
            "matched_forbidden_patterns",
        )
        _require_non_empty(self.diagnostic, "diagnostic")

    @property
    def success(self) -> bool:
        statuses = (self.dispatch_status, self.response_contract_status)
        evaluated = [status for status in statuses if status is not ClaudeEvaluationStatus.SKIPPED]
        return bool(evaluated) and all(
            status is ClaudeEvaluationStatus.PASSED for status in evaluated
        )


@dataclass(frozen=True)
class ClaudeAdapterEvaluationSummary:
    """Aggregate live Claude Code adapter evaluation results."""

    results: tuple[ClaudeAdapterCaseResult, ...]

    @property
    def total_cases(self) -> int:
        return len(self.results)

    @property
    def dispatch_passed(self) -> int:
        return self._count("dispatch_status", ClaudeEvaluationStatus.PASSED)

    @property
    def dispatch_failed(self) -> int:
        return self._count("dispatch_status", ClaudeEvaluationStatus.FAILED)

    @property
    def dispatch_skipped(self) -> int:
        return self._count("dispatch_status", ClaudeEvaluationStatus.SKIPPED)

    @property
    def response_passed(self) -> int:
        return self._count("response_contract_status", ClaudeEvaluationStatus.PASSED)

    @property
    def response_failed(self) -> int:
        return self._count("response_contract_status", ClaudeEvaluationStatus.FAILED)

    @property
    def response_skipped(self) -> int:
        return self._count("response_contract_status", ClaudeEvaluationStatus.SKIPPED)

    @property
    def fully_successful_cases(self) -> int:
        return sum(1 for result in self.results if result.success)

    @property
    def any_failed(self) -> bool:
        return any(
            result.dispatch_status is ClaudeEvaluationStatus.FAILED
            or result.response_contract_status is ClaudeEvaluationStatus.FAILED
            for result in self.results
        )

    @property
    def all_skipped(self) -> bool:
        return bool(self.results) and all(
            result.dispatch_status is ClaudeEvaluationStatus.SKIPPED
            and result.response_contract_status is ClaudeEvaluationStatus.SKIPPED
            for result in self.results
        )

    def _count(self, field_name: str, status: ClaudeEvaluationStatus) -> int:
        return sum(1 for result in self.results if getattr(result, field_name) is status)
