"""Text and JSON reporting for Claude adapter multi-run analytics."""

import json
from typing import Any

from benchmark.adapters.claude_code.analytics.aggregation import (
    infrastructure_category_counts,
)
from benchmark.adapters.claude_code.analytics.models import MultiRunAnalyticsSummary


def analytics_summary_to_dict(summary: MultiRunAnalyticsSummary) -> dict[str, Any]:
    """Serialize analytics without raw diagnostics or model responses."""

    return {
        "runs": {
            "total": summary.total_runs,
            "usable": summary.usable_runs,
            "degraded": summary.degraded_runs,
            "unusable": summary.unusable_runs,
        },
        "records": {
            "total_case_records": summary.total_case_records,
            "eligible_behavioral_records": summary.eligible_behavioral_records,
            "infrastructure_failure_records": summary.infrastructure_failure_records,
            "source_count_inconsistency_runs": (
                summary.source_count_inconsistency_runs
            ),
        },
        "infrastructure_category_counts": [
            {"category": category.value, "count": count}
            for category, count in infrastructure_category_counts(summary)
        ],
        "cases": [
            {
                "case_identifier": case.case_identifier,
                "total_input_runs": case.total_input_runs,
                "usable_or_degraded_runs": case.usable_or_degraded_runs,
                "unusable_runs_excluded": case.unusable_runs_excluded,
                "eligible_observations": case.eligible_observations,
                "dispatch": {
                    "passed": case.dispatch_passed,
                    "wrong": case.dispatch_wrong,
                    "skipped": case.dispatch_skipped,
                },
                "response": {
                    "passed": case.response_passed,
                    "failed": case.response_failed,
                    "skipped": case.response_skipped,
                },
                "infrastructure_failures": case.infrastructure_failures,
                "unavailable_observations": case.unavailable_observations,
                "observed_skill_counts": _count_entries(case.observed_skill_counts),
                "failed_marker_counts": _count_entries(case.failed_marker_counts),
                "forbidden_pattern_counts": _count_entries(
                    case.forbidden_pattern_counts
                ),
                "dispatch_observation_stability": (
                    case.dispatch_observation_stability
                ),
                "response_contract_stability": case.response_contract_stability,
                "infrastructure_reliability": case.infrastructure_reliability,
            }
            for case in summary.case_summaries
        ],
    }


def render_json_report(summary: MultiRunAnalyticsSummary) -> str:
    return json.dumps(analytics_summary_to_dict(summary), indent=2)


def render_text_report(summary: MultiRunAnalyticsSummary) -> str:
    lines = [
        "Runs",
        f"  usable: {summary.usable_runs}",
        f"  degraded: {summary.degraded_runs}",
        f"  unusable: {summary.unusable_runs}",
        "",
        "Infrastructure",
    ]
    category_counts = infrastructure_category_counts(summary)
    if category_counts:
        for category, count in category_counts:
            lines.append(f"  {category.value} records: {count}")
    else:
        lines.append("  infrastructure failure records: 0")
    lines.extend(
        [
            "",
            "Records",
            f"  total case records: {summary.total_case_records}",
            (
                "  eligible behavioral records: "
                f"{summary.eligible_behavioral_records}"
            ),
            (
                "  source count inconsistency runs: "
                f"{summary.source_count_inconsistency_runs}"
            ),
            "",
            "Case stability",
        ]
    )
    for case in summary.case_summaries:
        lines.extend(
            [
                "",
                case.case_identifier,
                (
                    "  eligible observations: "
                    f"{case.eligible_observations}/"
                    f"{case.usable_or_degraded_runs} included runs"
                ),
                (
                    "  unusable runs excluded: "
                    f"{case.unusable_runs_excluded}"
                ),
                (
                    "  dispatch: "
                    f"passed {case.dispatch_passed}, "
                    f"skipped {case.dispatch_skipped}, "
                    f"wrong {case.dispatch_wrong}"
                ),
                (
                    "  response: "
                    f"passed {case.response_passed}, "
                    f"failed {case.response_failed}, "
                    f"skipped {case.response_skipped}"
                ),
                f"  infrastructure failures: {case.infrastructure_failures}",
                f"  unavailable observations: {case.unavailable_observations}",
            ]
        )
        _append_counts(lines, "  observed skills", case.observed_skill_counts)
        _append_counts(lines, "  failed markers", case.failed_marker_counts)
        _append_counts(
            lines,
            "  forbidden patterns",
            case.forbidden_pattern_counts,
        )
    return "\n".join(lines)


def _count_entries(values: tuple[tuple[str, int], ...]) -> list[dict[str, Any]]:
    return [{"value": key, "count": count} for key, count in values]


def _append_counts(
    lines: list[str],
    heading: str,
    values: tuple[tuple[str, int], ...],
) -> None:
    if not values:
        return
    lines.append(f"{heading}:")
    for key, count in values:
        lines.append(f"    {key}: {count}")
