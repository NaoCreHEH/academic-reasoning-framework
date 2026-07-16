import json
from pathlib import Path
import tempfile
import unittest

from benchmark.adapters.claude_code.analytics.enums import RunUsabilityStatus
from benchmark.adapters.claude_code.analytics.loading import (
    LiveRunLoadError,
    load_live_run_report,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "claude_adapter_analytics"


class ClaudeAdapterAnalyticsLoadingTests(unittest.TestCase):
    def test_valid_report_loads(self):
        run = load_live_run_report(FIXTURE_DIR / "usable-run.json")
        self.assertEqual(run.total_cases, 4)
        self.assertEqual(run.usability_status, RunUsabilityStatus.USABLE)

    def test_invalid_json_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(LiveRunLoadError):
                load_live_run_report(path)

    def test_invalid_utf8_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_bytes(b"\xff")
            with self.assertRaises(LiveRunLoadError):
                load_live_run_report(path)

    def test_missing_results_rejected(self):
        with self.assertRaises(LiveRunLoadError):
            _load_payload({"total_cases": 0})

    def test_duplicate_case_ids_rejected(self):
        payload = _minimal_payload()
        payload["results"].append(dict(payload["results"][0]))
        with self.assertRaises(LiveRunLoadError):
            _load_payload(payload)

    def test_invalid_enum_rejected(self):
        payload = _minimal_payload()
        payload["results"][0]["dispatch_status"] = "unknown"
        with self.assertRaises(LiveRunLoadError):
            _load_payload(payload)

    def test_unknown_fields_ignored(self):
        payload = _minimal_payload()
        payload["unknown"] = "ignored"
        payload["results"][0]["extra"] = "ignored"
        run = _load_payload(payload)
        self.assertEqual(run.total_cases, 1)

    def test_source_aggregate_mismatches_detected_but_loaded(self):
        run = load_live_run_report(FIXTURE_DIR / "count-mismatch-run.json")
        self.assertFalse(run.source_counts_consistent)
        self.assertIn("total_cases", run.source_count_mismatches[0])

    def test_marker_fields_must_be_lists(self):
        payload = _minimal_payload()
        payload["results"][0]["failed_markers"] = "marker"
        with self.assertRaises(LiveRunLoadError):
            _load_payload(payload)

    def test_observed_skill_must_be_string_or_null(self):
        payload = _minimal_payload()
        payload["results"][0]["observed_skill"] = 3
        with self.assertRaises(LiveRunLoadError):
            _load_payload(payload)


def _load_payload(payload):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "run.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return load_live_run_report(path)


def _minimal_payload():
    return {
        "total_cases": 1,
        "dispatch_passed": 1,
        "dispatch_failed": 0,
        "dispatch_skipped": 0,
        "response_passed": 0,
        "response_failed": 0,
        "response_skipped": 1,
        "fully_successful_cases": 1,
        "results": [
            {
                "case_identifier": "case",
                "dispatch_status": "passed",
                "response_contract_status": "skipped",
                "observed_skill": "skill",
                "failed_markers": [],
                "matched_forbidden_patterns": [],
                "diagnostic": "observed skill",
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()
