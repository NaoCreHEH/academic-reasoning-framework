"""Offline analytics for multiple Claude adapter live evaluation reports."""

from benchmark.adapters.claude_code.analytics.aggregation import (
    CaseSetMismatchError,
    analyze_live_runs,
)
from benchmark.adapters.claude_code.analytics.enums import (
    BehavioralEligibility,
    CaseOutcomeCategory,
    RunUsabilityStatus,
)
from benchmark.adapters.claude_code.analytics.loading import (
    LiveRunLoadError,
    load_live_run_report,
)
from benchmark.adapters.claude_code.analytics.models import (
    CaseStabilitySummary,
    MultiRunAnalyticsSummary,
    ParsedCaseRunResult,
    ParsedLiveRun,
)
from benchmark.adapters.claude_code.analytics.reporting import (
    analytics_summary_to_dict,
    render_json_report,
    render_text_report,
)

__all__ = [
    "BehavioralEligibility",
    "CaseOutcomeCategory",
    "CaseSetMismatchError",
    "CaseStabilitySummary",
    "LiveRunLoadError",
    "MultiRunAnalyticsSummary",
    "ParsedCaseRunResult",
    "ParsedLiveRun",
    "RunUsabilityStatus",
    "analytics_summary_to_dict",
    "analyze_live_runs",
    "load_live_run_report",
    "render_json_report",
    "render_text_report",
]
