"""Deterministic classification for parsed Claude adapter results."""

from benchmark.adapters.claude_code.enums import ClaudeEvaluationStatus
from benchmark.adapters.claude_code.analytics.enums import (
    BehavioralEligibility,
    CaseOutcomeCategory,
    RunUsabilityStatus,
)
from benchmark.adapters.claude_code.analytics.models import ParsedCaseRunResult


INFRASTRUCTURE_CATEGORIES = {
    CaseOutcomeCategory.INVOCATION_TIMEOUT,
    CaseOutcomeCategory.INVOCATION_PROCESS_FAILURE,
    CaseOutcomeCategory.INVOCATION_ENCODING_FAILURE,
    CaseOutcomeCategory.INVOCATION_STREAM_PARSE_FAILURE,
    CaseOutcomeCategory.PLUGIN_LOAD_FAILURE,
    CaseOutcomeCategory.OTHER_INVOCATION_FAILURE,
}


def classify_case_result(
    dispatch_status: ClaudeEvaluationStatus,
    response_contract_status: ClaudeEvaluationStatus,
    diagnostic: str,
) -> tuple[tuple[CaseOutcomeCategory, ...], BehavioralEligibility]:
    """Classify one result without treating infrastructure as behavior."""

    diagnostic_lower = diagnostic.casefold()
    if (
        dispatch_status is ClaudeEvaluationStatus.FAILED
        and response_contract_status is ClaudeEvaluationStatus.FAILED
    ):
        infrastructure = _classify_infrastructure(diagnostic_lower)
        if infrastructure is not None:
            return (infrastructure,), BehavioralEligibility.INELIGIBLE_INFRASTRUCTURE

    if (
        dispatch_status is ClaudeEvaluationStatus.SKIPPED
        and response_contract_status is ClaudeEvaluationStatus.SKIPPED
        and "evaluation unavailable" in diagnostic_lower
    ):
        return (
            (CaseOutcomeCategory.EVALUATION_UNAVAILABLE,),
            BehavioralEligibility.INELIGIBLE_UNAVAILABLE,
        )

    categories: list[CaseOutcomeCategory] = []
    if dispatch_status is ClaudeEvaluationStatus.PASSED:
        categories.append(CaseOutcomeCategory.DISPATCH_PASSED)
    elif dispatch_status is ClaudeEvaluationStatus.SKIPPED:
        categories.append(CaseOutcomeCategory.DISPATCH_SKIPPED)
    else:
        categories.append(CaseOutcomeCategory.DISPATCH_WRONG)

    if response_contract_status is ClaudeEvaluationStatus.PASSED:
        categories.append(CaseOutcomeCategory.RESPONSE_PASSED)
    elif response_contract_status is ClaudeEvaluationStatus.SKIPPED:
        categories.append(CaseOutcomeCategory.RESPONSE_SKIPPED)
    else:
        categories.append(CaseOutcomeCategory.RESPONSE_FAILED)

    return tuple(categories), BehavioralEligibility.ELIGIBLE


def classify_run_usability(
    results: tuple[ParsedCaseRunResult, ...],
) -> RunUsabilityStatus:
    """Classify a run by infrastructure usability, not model quality."""

    eligible = sum(
        1
        for result in results
        if result.behavioral_eligibility is BehavioralEligibility.ELIGIBLE
    )
    infrastructure = sum(
        1
        for result in results
        if result.behavioral_eligibility
        is BehavioralEligibility.INELIGIBLE_INFRASTRUCTURE
    )
    if eligible == 0:
        return RunUsabilityStatus.UNUSABLE
    if infrastructure:
        return RunUsabilityStatus.DEGRADED
    return RunUsabilityStatus.USABLE


def is_infrastructure_result(result: ParsedCaseRunResult) -> bool:
    return any(category in INFRASTRUCTURE_CATEGORIES for category in result.outcome_categories)


def _classify_infrastructure(diagnostic_lower: str) -> CaseOutcomeCategory | None:
    if "timed out" in diagnostic_lower:
        return CaseOutcomeCategory.INVOCATION_TIMEOUT
    if "return code" in diagnostic_lower:
        return CaseOutcomeCategory.INVOCATION_PROCESS_FAILURE
    if "not valid utf-8" in diagnostic_lower:
        return CaseOutcomeCategory.INVOCATION_ENCODING_FAILURE
    if "stream parsing failed" in diagnostic_lower:
        return CaseOutcomeCategory.INVOCATION_STREAM_PARSE_FAILURE
    if "plugin failed to load" in diagnostic_lower:
        return CaseOutcomeCategory.PLUGIN_LOAD_FAILURE
    if "claude invocation failed" in diagnostic_lower:
        return CaseOutcomeCategory.OTHER_INVOCATION_FAILURE
    return None
