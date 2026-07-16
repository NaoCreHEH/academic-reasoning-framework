from pathlib import Path
import json
import unittest

from benchmark.adapters.claude_code.analytics import (
    analytics_summary_to_dict,
    analyze_live_runs,
    load_live_run_report,
    render_json_report,
    render_text_report,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "claude_adapter_analytics"


class ClaudeAdapterAnalyticsReportingTests(unittest.TestCase):
    def test_text_report_contains_run_and_case_sections(self):
        summary = _summary()
        report = render_text_report(summary)
        self.assertIn("Runs", report)
        self.assertIn("Infrastructure", report)
        self.assertIn("Case stability", report)
        self.assertIn("response-confidence-no-percentage", report)

    def test_text_report_uses_fractions_not_percentages(self):
        report = render_text_report(_summary())
        self.assertIn("eligible observations:", report)
        self.assertNotIn("%", report)

    def test_json_report_parses_and_uses_enum_values(self):
        payload = json.loads(render_json_report(_summary()))
        categories = payload["infrastructure_category_counts"]
        self.assertEqual(categories[0]["category"], "invocation_timeout")

    def test_json_report_contains_no_raw_diagnostics_or_responses(self):
        text = render_json_report(_summary())
        self.assertNotIn("diagnostic", text)
        self.assertNotIn("response_text", text)
        self.assertNotIn("Public final response", text)

    def test_summary_dict_contains_denominators(self):
        payload = analytics_summary_to_dict(_summary())
        case = payload["cases"][0]
        self.assertIn("eligible_observations", case)
        self.assertIn("unusable_runs_excluded", case)


def _summary():
    return analyze_live_runs(
        [
            load_live_run_report(FIXTURE_DIR / "usable-run.json"),
            load_live_run_report(FIXTURE_DIR / "degraded-run.json"),
        ]
    )


if __name__ == "__main__":
    unittest.main()
