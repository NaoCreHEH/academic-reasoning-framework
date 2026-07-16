"""Aggregation for offline Claude adapter multi-run analytics."""

from collections import Counter
from collections.abc import Iterable

from benchmark.adapters.claude_code.analytics.enums import (
    BehavioralEligibility,
    CaseOutcomeCategory,
    RunUsabilityStatus,
)
from benchmark.adapters.claude_code.analytics.models import (
    CaseStabilitySummary,
    MultiRunAnalyticsSummary,
    ParsedCaseRunResult,
    ParsedLiveRun,
)


class CaseSetMismatchError(ValueError):
    """Raised when input reports do not contain the same case identifiers."""


def analyze_live_runs(
    runs: Iterable[ParsedLiveRun],
    include_unusable: bool = False,
    allow_case_set_differences: bool = False,
) -> MultiRunAnalyticsSummary:
    """Analyze parsed live runs without invoking a model."""

    parsed_runs = tuple(runs)
    if not parsed_runs:
        raise ValueError("at least one run is required")
    if not allow_case_set_differences:
        _validate_case_sets(parsed_runs)

    case_ids = sorted(
        {
            result.case_identifier
            for run in parsed_runs
            for result in run.results
        }
    )
    case_summaries = tuple(
        _summarize_case(case_id, parsed_runs, include_unusable)
        for case_id in case_ids
    )
    return MultiRunAnalyticsSummary(
        runs=parsed_runs,
        case_summaries=case_summaries,
    )


def _validate_case_sets(runs: tuple[ParsedLiveRun, ...]) -> None:
    expected = {result.case_identifier for result in runs[0].results}
    errors: list[str] = []
    for run in runs[1:]:
        current = {result.case_identifier for result in run.results}
        missing = sorted(expected - current)
        unexpected = sorted(current - expected)
        if missing or unexpected:
            parts = [str(run.source_path)]
            if missing:
                parts.append(f"missing cases: {', '.join(missing)}")
            if unexpected:
                parts.append(f"unexpected cases: {', '.join(unexpected)}")
            errors.append("; ".join(parts))
    if errors:
        raise CaseSetMismatchError("\n".join(errors))


def _summarize_case(
    case_identifier: str,
    runs: tuple[ParsedLiveRun, ...],
    include_unusable: bool,
) -> CaseStabilitySummary:
    results_by_run: list[tuple[ParsedLiveRun, ParsedCaseRunResult]] = []
    for run in runs:
        result = _find_result(run, case_identifier)
        if result is not None:
            results_by_run.append((run, result))

    included_pairs = [
        (run, result)
        for run, result in results_by_run
        if include_unusable or run.usability_status is not RunUsabilityStatus.UNUSABLE
    ]
    eligible_results = [
        result
        for _run, result in included_pairs
        if result.behavioral_eligibility is BehavioralEligibility.ELIGIBLE
    ]
    infrastructure_results = [
        result
        for _run, result in included_pairs
        if result.behavioral_eligibility
        is BehavioralEligibility.INELIGIBLE_INFRASTRUCTURE
    ]
    unavailable_results = [
        result
        for _run, result in included_pairs
        if result.behavioral_eligibility
        is BehavioralEligibility.INELIGIBLE_UNAVAILABLE
    ]
    observed_skill_counter: Counter[str] = Counter(
        result.observed_skill for result in eligible_results if result.observed_skill
    )
    failed_marker_counter: Counter[str] = Counter()
    forbidden_counter: Counter[str] = Counter()
    for result in eligible_results:
        failed_marker_counter.update(result.failed_markers)
        forbidden_counter.update(result.matched_forbidden_patterns)

    return CaseStabilitySummary(
        case_identifier=case_identifier,
        total_input_runs=len(runs),
        usable_or_degraded_runs=sum(
            1 for run, _result in included_pairs if run.usability_status is not RunUsabilityStatus.UNUSABLE
        ),
        unusable_runs_excluded=sum(
            1
            for run, result in results_by_run
            if run.usability_status is RunUsabilityStatus.UNUSABLE
            and not include_unusable
            and result is not None
        ),
        eligible_observations=len(eligible_results),
        dispatch_passed=_count_category(
            eligible_results,
            CaseOutcomeCategory.DISPATCH_PASSED,
        ),
        dispatch_wrong=_count_category(
            eligible_results,
            CaseOutcomeCategory.DISPATCH_WRONG,
        ),
        dispatch_skipped=_count_category(
            eligible_results,
            CaseOutcomeCategory.DISPATCH_SKIPPED,
        ),
        response_passed=_count_category(
            eligible_results,
            CaseOutcomeCategory.RESPONSE_PASSED,
        ),
        response_failed=_count_category(
            eligible_results,
            CaseOutcomeCategory.RESPONSE_FAILED,
        ),
        response_skipped=_count_category(
            eligible_results,
            CaseOutcomeCategory.RESPONSE_SKIPPED,
        ),
        infrastructure_failures=len(infrastructure_results),
        unavailable_observations=len(unavailable_results),
        observed_skill_counts=_sorted_counter(observed_skill_counter),
        failed_marker_counts=_sorted_counter(failed_marker_counter),
        forbidden_pattern_counts=_sorted_counter(forbidden_counter),
    )


def infrastructure_category_counts(
    summary: MultiRunAnalyticsSummary,
) -> tuple[tuple[CaseOutcomeCategory, int], ...]:
    counter: Counter[CaseOutcomeCategory] = Counter()
    for run in summary.runs:
        for result in run.results:
            for category in result.outcome_categories:
                if category.value.startswith("invocation_") or category in (
                    CaseOutcomeCategory.PLUGIN_LOAD_FAILURE,
                    CaseOutcomeCategory.OTHER_INVOCATION_FAILURE,
                ):
                    counter[category] += 1
    return tuple(sorted(counter.items(), key=lambda item: (-item[1], item[0].value)))


def _find_result(
    run: ParsedLiveRun,
    case_identifier: str,
) -> ParsedCaseRunResult | None:
    for result in run.results:
        if result.case_identifier == case_identifier:
            return result
    return None


def _count_category(
    results: list[ParsedCaseRunResult],
    category: CaseOutcomeCategory,
) -> int:
    return sum(1 for result in results if category in result.outcome_categories)


def _sorted_counter(counter: Counter[str]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(counter.items(), key=lambda item: (-item[1], item[0])))
