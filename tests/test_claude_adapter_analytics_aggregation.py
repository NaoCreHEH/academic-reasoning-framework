from pathlib import Path
import unittest

from benchmark.adapters.claude_code.analytics import (
    CaseSetMismatchError,
    analyze_live_runs,
    load_live_run_report,
)
from benchmark.adapters.claude_code.analytics.enums import RunUsabilityStatus


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "claude_adapter_analytics"


class ClaudeAdapterAnalyticsAggregationTests(unittest.TestCase):
    def test_unusable_run_excluded_from_behavioral_denominator_by_default(self):
        unusable = load_live_run_report(FIXTURE_DIR / "unusable-return-code-run.json")
        summary = analyze_live_runs([unusable])
        case = summary.case_summaries[0]
        self.assertEqual(summary.unusable_runs, 1)
        self.assertEqual(case.eligible_observations, 0)
        self.assertEqual(case.dispatch_wrong, 0)
        self.assertEqual(case.response_failed, 0)
        self.assertEqual(case.unusable_runs_excluded, 1)

    def test_unusable_run_still_counted_at_run_and_infrastructure_level(self):
        unusable = load_live_run_report(FIXTURE_DIR / "unusable-return-code-run.json")
        summary = analyze_live_runs([unusable])
        self.assertEqual(summary.total_runs, 1)
        self.assertEqual(summary.infrastructure_failure_records, 16)

    def test_include_unusable_counts_case_infrastructure_not_behavior(self):
        unusable = load_live_run_report(FIXTURE_DIR / "unusable-return-code-run.json")
        summary = analyze_live_runs([unusable], include_unusable=True)
        case = summary.case_summaries[0]
        self.assertEqual(case.infrastructure_failures, 1)
        self.assertEqual(case.dispatch_wrong, 0)

    def test_degraded_run_contributes_eligible_cases(self):
        run = load_live_run_report(FIXTURE_DIR / "degraded-run.json")
        summary = analyze_live_runs([run])
        confidence = _case(summary, "response-confidence-no-percentage")
        timeout = _case(summary, "dispatch-python-mcq")
        self.assertEqual(run.usability_status, RunUsabilityStatus.DEGRADED)
        self.assertEqual(confidence.eligible_observations, 1)
        self.assertEqual(confidence.response_failed, 1)
        self.assertEqual(timeout.eligible_observations, 0)
        self.assertEqual(timeout.infrastructure_failures, 1)

    def test_observed_skill_markers_and_forbidden_patterns_aggregate(self):
        runs = [
            load_live_run_report(FIXTURE_DIR / "usable-run.json"),
            load_live_run_report(FIXTURE_DIR / "degraded-run.json"),
        ]
        summary = analyze_live_runs(runs)
        confidence = _case(summary, "response-confidence-no-percentage")
        self.assertEqual(
            confidence.observed_skill_counts,
            (("arf-academic:pfe-review", 2),),
        )
        self.assertEqual(
            confidence.forbidden_pattern_counts,
            (("confidence percentage pattern", 2),),
        )
        self.assertEqual(
            confidence.failed_marker_counts,
            (("insufficient-review-scope", 1),),
        )

    def test_case_summaries_sorted_deterministically(self):
        summary = analyze_live_runs(
            [
                load_live_run_report(FIXTURE_DIR / "usable-run.json"),
                load_live_run_report(FIXTURE_DIR / "degraded-run.json"),
            ]
        )
        identifiers = [case.case_identifier for case in summary.case_summaries]
        self.assertEqual(identifiers, sorted(identifiers))

    def test_differing_case_sets_rejected_by_default(self):
        with self.assertRaises(CaseSetMismatchError):
            analyze_live_runs(
                [
                    load_live_run_report(FIXTURE_DIR / "usable-run.json"),
                    load_live_run_report(FIXTURE_DIR / "different-case-set-run.json"),
                ]
            )

    def test_union_mode_works_when_enabled(self):
        summary = analyze_live_runs(
            [
                load_live_run_report(FIXTURE_DIR / "usable-run.json"),
                load_live_run_report(FIXTURE_DIR / "different-case-set-run.json"),
            ],
            allow_case_set_differences=True,
        )
        identifiers = {case.case_identifier for case in summary.case_summaries}
        self.assertIn("unexpected-new-case", identifiers)

    def test_critical_unusable_sixteen_return_code_regression(self):
        run = load_live_run_report(FIXTURE_DIR / "unusable-return-code-run.json")
        summary = analyze_live_runs([run])
        self.assertEqual(run.usability_status, RunUsabilityStatus.UNUSABLE)
        self.assertEqual(summary.infrastructure_failure_records, 16)
        self.assertEqual(sum(case.dispatch_wrong for case in summary.case_summaries), 0)
        self.assertEqual(sum(case.response_failed for case in summary.case_summaries), 0)


def _case(summary, identifier):
    for case in summary.case_summaries:
        if case.case_identifier == identifier:
            return case
    raise AssertionError(f"missing case: {identifier}")


if __name__ == "__main__":
    unittest.main()
