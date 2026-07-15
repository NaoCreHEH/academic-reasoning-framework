"""Serialization helpers for Claude Code adapter evaluation reports."""

from typing import Any

from benchmark.adapters.claude_code.models import ClaudeAdapterEvaluationSummary


def evaluation_summary_to_dict(
    summary: ClaudeAdapterEvaluationSummary,
) -> dict[str, Any]:
    """Serialize a live evaluation summary without raw model responses."""

    return {
        "total_cases": summary.total_cases,
        "dispatch_passed": summary.dispatch_passed,
        "dispatch_failed": summary.dispatch_failed,
        "dispatch_skipped": summary.dispatch_skipped,
        "response_passed": summary.response_passed,
        "response_failed": summary.response_failed,
        "response_skipped": summary.response_skipped,
        "fully_successful_cases": summary.fully_successful_cases,
        "results": [
            {
                "case_identifier": result.case_identifier,
                "dispatch_status": result.dispatch_status.value,
                "response_contract_status": result.response_contract_status.value,
                "observed_skill": result.observed_skill,
                "failed_markers": list(result.failed_markers),
                "matched_forbidden_patterns": list(
                    result.matched_forbidden_patterns
                ),
                "diagnostic": result.diagnostic,
            }
            for result in summary.results
        ],
    }
