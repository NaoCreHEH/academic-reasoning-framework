"""Dataclasses for offline Claude adapter multi-run analytics."""

from dataclasses import dataclass
from pathlib import Path

from benchmark.adapters.claude_code.enums import ClaudeEvaluationStatus
from benchmark.adapters.claude_code.analytics.enums import (
    BehavioralEligibility,
    CaseOutcomeCategory,
    RunUsabilityStatus,
)


class AnalyticsValidationError(ValueError):
    """Raised when analytics model data is structurally invalid."""


def _require_non_blank(value: str | None, field_name: str) -> None:
    if value is None or not isinstance(value, str) or not value.strip():
        raise AnalyticsValidationError(f"{field_name} cannot be blank")


def _validate_unique_strings(values: tuple[str, ...], field_name: str) -> None:
    seen: set[str] = set()
    for value in values:
        _require_non_blank(value, field_name)
        if value in seen:
            raise AnalyticsValidationError(f"{field_name} cannot contain duplicates")
        seen.add(value)


@dataclass(frozen=True)
class ParsedCaseRunResult:
    """One parsed live-evaluation case result without raw response text."""

    case_identifier: str
    dispatch_status: ClaudeEvaluationStatus
    response_contract_status: ClaudeEvaluationStatus
    observed_skill: str | None
    failed_markers: tuple[str, ...]
    matched_forbidden_patterns: tuple[str, ...]
    diagnostic: str
    outcome_categories: tuple[CaseOutcomeCategory, ...]
    behavioral_eligibility: BehavioralEligibility

    def __post_init__(self) -> None:
        _require_non_blank(self.case_identifier, "case_identifier")
        if not isinstance(self.dispatch_status, ClaudeEvaluationStatus):
            raise AnalyticsValidationError(
                "dispatch_status must be a ClaudeEvaluationStatus"
            )
        if not isinstance(self.response_contract_status, ClaudeEvaluationStatus):
            raise AnalyticsValidationError(
                "response_contract_status must be a ClaudeEvaluationStatus"
            )
        if self.observed_skill is not None:
            _require_non_blank(self.observed_skill, "observed_skill")
        _validate_unique_strings(self.failed_markers, "failed_markers")
        _validate_unique_strings(
            self.matched_forbidden_patterns,
            "matched_forbidden_patterns",
        )
        _require_non_blank(self.diagnostic, "diagnostic")
        seen_categories: set[CaseOutcomeCategory] = set()
        for category in self.outcome_categories:
            if not isinstance(category, CaseOutcomeCategory):
                raise AnalyticsValidationError(
                    "outcome_categories must contain CaseOutcomeCategory values"
                )
            if category in seen_categories:
                raise AnalyticsValidationError(
                    "outcome_categories cannot contain duplicates"
                )
            seen_categories.add(category)
        if not isinstance(self.behavioral_eligibility, BehavioralEligibility):
            raise AnalyticsValidationError(
                "behavioral_eligibility must be a BehavioralEligibility"
            )


@dataclass(frozen=True)
class ParsedLiveRun:
    """One parsed live run with source-count consistency metadata."""

    source_path: Path
    results: tuple[ParsedCaseRunResult, ...]
    usability_status: RunUsabilityStatus
    source_counts_consistent: bool
    source_count_mismatches: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source_path.exists():
            raise AnalyticsValidationError("source_path must exist at load time")
        if not self.results:
            raise AnalyticsValidationError("results must contain at least one case")
        identifiers = tuple(result.case_identifier for result in self.results)
        _validate_unique_strings(identifiers, "case identifiers")
        if not isinstance(self.usability_status, RunUsabilityStatus):
            raise AnalyticsValidationError(
                "usability_status must be a RunUsabilityStatus"
            )
        if not isinstance(self.source_counts_consistent, bool):
            raise AnalyticsValidationError("source_counts_consistent must be a bool")
        _validate_unique_strings(
            self.source_count_mismatches,
            "source_count_mismatches",
        )
        if self.source_counts_consistent and self.source_count_mismatches:
            raise AnalyticsValidationError(
                "consistent runs must not include source_count_mismatches"
            )

    @property
    def total_cases(self) -> int:
        return len(self.results)

    @property
    def infrastructure_failure_count(self) -> int:
        return sum(
            1
            for result in self.results
            if result.behavioral_eligibility
            is BehavioralEligibility.INELIGIBLE_INFRASTRUCTURE
        )

    @property
    def behaviorally_eligible_case_count(self) -> int:
        return sum(
            1
            for result in self.results
            if result.behavioral_eligibility is BehavioralEligibility.ELIGIBLE
        )

    @property
    def unavailable_case_count(self) -> int:
        return sum(
            1
            for result in self.results
            if result.behavioral_eligibility
            is BehavioralEligibility.INELIGIBLE_UNAVAILABLE
        )


@dataclass(frozen=True)
class CaseStabilitySummary:
    """Cross-run stability summary for one case identifier."""

    case_identifier: str
    total_input_runs: int
    usable_or_degraded_runs: int
    unusable_runs_excluded: int
    eligible_observations: int
    dispatch_passed: int
    dispatch_wrong: int
    dispatch_skipped: int
    response_passed: int
    response_failed: int
    response_skipped: int
    infrastructure_failures: int
    unavailable_observations: int
    observed_skill_counts: tuple[tuple[str, int], ...]
    failed_marker_counts: tuple[tuple[str, int], ...]
    forbidden_pattern_counts: tuple[tuple[str, int], ...]

    def __post_init__(self) -> None:
        _require_non_blank(self.case_identifier, "case_identifier")
        for field_name in (
            "total_input_runs",
            "usable_or_degraded_runs",
            "unusable_runs_excluded",
            "eligible_observations",
            "dispatch_passed",
            "dispatch_wrong",
            "dispatch_skipped",
            "response_passed",
            "response_failed",
            "response_skipped",
            "infrastructure_failures",
            "unavailable_observations",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise AnalyticsValidationError(f"{field_name} must be non-negative")
        _validate_count_tuple(self.observed_skill_counts, "observed_skill_counts")
        _validate_count_tuple(self.failed_marker_counts, "failed_marker_counts")
        _validate_count_tuple(
            self.forbidden_pattern_counts,
            "forbidden_pattern_counts",
        )

    @property
    def dispatch_observation_stability(self) -> str:
        return _qualitative_stability(
            self.dispatch_wrong,
            self.dispatch_skipped,
            self.eligible_observations,
            "no eligible observations",
        )

    @property
    def response_contract_stability(self) -> str:
        return _qualitative_stability(
            self.response_failed,
            self.response_skipped,
            self.eligible_observations,
            "no eligible observations",
        )

    @property
    def infrastructure_reliability(self) -> str:
        if self.infrastructure_failures == 0:
            return "no infrastructure failures in included runs"
        return (
            f"{self.infrastructure_failures} infrastructure failure records "
            f"in {self.usable_or_degraded_runs} included runs"
        )


@dataclass(frozen=True)
class MultiRunAnalyticsSummary:
    """Aggregate analytics result for multiple parsed live runs."""

    runs: tuple[ParsedLiveRun, ...]
    case_summaries: tuple[CaseStabilitySummary, ...]

    def __post_init__(self) -> None:
        if not self.runs:
            raise AnalyticsValidationError("runs must contain at least one run")
        identifiers = tuple(summary.case_identifier for summary in self.case_summaries)
        if len(identifiers) != len(set(identifiers)):
            raise AnalyticsValidationError("case_summaries cannot contain duplicates")

    @property
    def total_runs(self) -> int:
        return len(self.runs)

    @property
    def usable_runs(self) -> int:
        return self._count_runs(RunUsabilityStatus.USABLE)

    @property
    def degraded_runs(self) -> int:
        return self._count_runs(RunUsabilityStatus.DEGRADED)

    @property
    def unusable_runs(self) -> int:
        return self._count_runs(RunUsabilityStatus.UNUSABLE)

    @property
    def total_case_records(self) -> int:
        return sum(run.total_cases for run in self.runs)

    @property
    def eligible_behavioral_records(self) -> int:
        return sum(run.behaviorally_eligible_case_count for run in self.runs)

    @property
    def infrastructure_failure_records(self) -> int:
        return sum(run.infrastructure_failure_count for run in self.runs)

    @property
    def source_count_inconsistency_runs(self) -> int:
        return sum(1 for run in self.runs if not run.source_counts_consistent)

    def _count_runs(self, status: RunUsabilityStatus) -> int:
        return sum(1 for run in self.runs if run.usability_status is status)


def _validate_count_tuple(values: tuple[tuple[str, int], ...], field_name: str) -> None:
    seen: set[str] = set()
    for key, count in values:
        _require_non_blank(key, field_name)
        if key in seen:
            raise AnalyticsValidationError(f"{field_name} cannot contain duplicates")
        if not isinstance(count, int) or count <= 0:
            raise AnalyticsValidationError(f"{field_name} counts must be positive")
        seen.add(key)


def _qualitative_stability(
    adverse: int,
    skipped: int,
    denominator: int,
    empty_label: str,
) -> str:
    if denominator == 0:
        return empty_label
    if adverse == 0 and skipped == 0:
        return f"stable across {denominator}/{denominator} eligible observations"
    return f"varied across {denominator} eligible observations"
