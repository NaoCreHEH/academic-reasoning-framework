"""Loading and schema validation for offline Claude adapter JSON reports."""

from json import JSONDecodeError
import json
from pathlib import Path
from typing import Any

from benchmark.adapters.claude_code.enums import ClaudeEvaluationStatus
from benchmark.adapters.claude_code.analytics.classification import (
    classify_case_result,
    classify_run_usability,
)
from benchmark.adapters.claude_code.analytics.models import (
    ParsedCaseRunResult,
    ParsedLiveRun,
)


class LiveRunLoadError(ValueError):
    """Raised when a live-run report cannot be loaded."""

    def __init__(self, source_path: Path, cause: str) -> None:
        self.source_path = source_path
        self.cause = cause
        super().__init__(f"{source_path}: {cause}")


def load_live_run_report(path: Path | str) -> ParsedLiveRun:
    """Load one JSON report produced by the live Claude adapter evaluator."""

    source_path = Path(path)
    if not source_path.exists():
        raise LiveRunLoadError(source_path, "file does not exist")
    try:
        text = source_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise LiveRunLoadError(source_path, f"file is not valid UTF-8: {error}") from error
    try:
        payload = json.loads(text)
    except JSONDecodeError as error:
        raise LiveRunLoadError(source_path, f"invalid JSON: {error.msg}") from error
    if not isinstance(payload, dict):
        raise LiveRunLoadError(source_path, "top-level JSON value must be an object")

    results_payload = payload.get("results")
    if not isinstance(results_payload, list) or not results_payload:
        raise LiveRunLoadError(source_path, "results must be a non-empty list")

    results = tuple(
        _parse_result(source_path, index, item)
        for index, item in enumerate(results_payload)
    )
    identifiers = [result.case_identifier for result in results]
    if len(identifiers) != len(set(identifiers)):
        raise LiveRunLoadError(source_path, "case identifiers must be unique")

    mismatches = _source_count_mismatches(payload, results)
    return ParsedLiveRun(
        source_path=source_path,
        results=results,
        usability_status=classify_run_usability(results),
        source_counts_consistent=not mismatches,
        source_count_mismatches=tuple(mismatches),
    )


def _parse_result(
    source_path: Path,
    index: int,
    payload: Any,
) -> ParsedCaseRunResult:
    if not isinstance(payload, dict):
        raise LiveRunLoadError(source_path, f"results[{index}] must be an object")
    required = (
        "case_identifier",
        "dispatch_status",
        "response_contract_status",
        "observed_skill",
        "failed_markers",
        "matched_forbidden_patterns",
        "diagnostic",
    )
    for field_name in required:
        if field_name not in payload:
            raise LiveRunLoadError(
                source_path,
                f"results[{index}] missing required field: {field_name}",
            )

    case_identifier = _required_string(source_path, index, payload, "case_identifier")
    dispatch_status = _status_value(source_path, index, payload, "dispatch_status")
    response_status = _status_value(
        source_path,
        index,
        payload,
        "response_contract_status",
    )
    observed_skill = payload["observed_skill"]
    if observed_skill is not None and (
        not isinstance(observed_skill, str) or not observed_skill.strip()
    ):
        raise LiveRunLoadError(
            source_path,
            f"results[{index}].observed_skill must be string or null",
        )
    failed_markers = _string_list(source_path, index, payload, "failed_markers")
    forbidden_patterns = _string_list(
        source_path,
        index,
        payload,
        "matched_forbidden_patterns",
    )
    diagnostic = _required_string(source_path, index, payload, "diagnostic")
    categories, eligibility = classify_case_result(
        dispatch_status,
        response_status,
        diagnostic,
    )
    return ParsedCaseRunResult(
        case_identifier=case_identifier,
        dispatch_status=dispatch_status,
        response_contract_status=response_status,
        observed_skill=observed_skill,
        failed_markers=failed_markers,
        matched_forbidden_patterns=forbidden_patterns,
        diagnostic=diagnostic,
        outcome_categories=categories,
        behavioral_eligibility=eligibility,
    )


def _required_string(
    source_path: Path,
    index: int,
    payload: dict[str, Any],
    field_name: str,
) -> str:
    value = payload[field_name]
    if not isinstance(value, str) or not value.strip():
        raise LiveRunLoadError(
            source_path,
            f"results[{index}].{field_name} must be a non-blank string",
        )
    return value


def _status_value(
    source_path: Path,
    index: int,
    payload: dict[str, Any],
    field_name: str,
) -> ClaudeEvaluationStatus:
    value = payload[field_name]
    if not isinstance(value, str):
        raise LiveRunLoadError(
            source_path,
            f"results[{index}].{field_name} must be a string",
        )
    try:
        return ClaudeEvaluationStatus(value)
    except ValueError as error:
        raise LiveRunLoadError(
            source_path,
            f"results[{index}].{field_name} has invalid value: {value}",
        ) from error


def _string_list(
    source_path: Path,
    index: int,
    payload: dict[str, Any],
    field_name: str,
) -> tuple[str, ...]:
    value = payload[field_name]
    if not isinstance(value, list):
        raise LiveRunLoadError(
            source_path,
            f"results[{index}].{field_name} must be a list",
        )
    parsed: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise LiveRunLoadError(
                source_path,
                f"results[{index}].{field_name} entries must be non-blank strings",
            )
        parsed.append(item)
    if len(parsed) != len(set(parsed)):
        raise LiveRunLoadError(
            source_path,
            f"results[{index}].{field_name} entries must be unique",
        )
    return tuple(parsed)


def _source_count_mismatches(
    payload: dict[str, Any],
    results: tuple[ParsedCaseRunResult, ...],
) -> list[str]:
    calculated = {
        "total_cases": len(results),
        "dispatch_passed": _count_status(results, "dispatch_status", "passed"),
        "dispatch_failed": _count_status(results, "dispatch_status", "failed"),
        "dispatch_skipped": _count_status(results, "dispatch_status", "skipped"),
        "response_passed": _count_status(
            results,
            "response_contract_status",
            "passed",
        ),
        "response_failed": _count_status(
            results,
            "response_contract_status",
            "failed",
        ),
        "response_skipped": _count_status(
            results,
            "response_contract_status",
            "skipped",
        ),
        "fully_successful_cases": sum(
            1
            for result in results
            if (
                result.dispatch_status is ClaudeEvaluationStatus.PASSED
                and result.response_contract_status
                is ClaudeEvaluationStatus.PASSED
            )
            or (
                result.dispatch_status is ClaudeEvaluationStatus.PASSED
                and result.response_contract_status
                is ClaudeEvaluationStatus.SKIPPED
            )
            or (
                result.dispatch_status is ClaudeEvaluationStatus.SKIPPED
                and result.response_contract_status
                is ClaudeEvaluationStatus.PASSED
            )
        ),
    }
    mismatches: list[str] = []
    for field_name, calculated_value in calculated.items():
        if field_name in payload and payload[field_name] != calculated_value:
            mismatches.append(
                f"{field_name}: source={payload[field_name]} calculated={calculated_value}"
            )
    return mismatches


def _count_status(
    results: tuple[ParsedCaseRunResult, ...],
    field_name: str,
    status_value: str,
) -> int:
    return sum(
        1 for result in results if getattr(result, field_name).value == status_value
    )
