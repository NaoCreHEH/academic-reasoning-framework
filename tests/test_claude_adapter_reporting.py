import unittest

from benchmark.adapters.claude_code.enums import ClaudeEvaluationStatus
from benchmark.adapters.claude_code.models import (
    ClaudeAdapterCaseResult,
    ClaudeAdapterEvaluationSummary,
)
from benchmark.adapters.claude_code.reporting import evaluation_summary_to_dict


class ClaudeAdapterReportingTests(unittest.TestCase):
    def test_summary_serializes_deterministically_with_enum_values(self):
        summary = ClaudeAdapterEvaluationSummary(
            results=(
                ClaudeAdapterCaseResult(
                    case_identifier="first",
                    dispatch_status=ClaudeEvaluationStatus.PASSED,
                    response_contract_status=ClaudeEvaluationStatus.SKIPPED,
                    observed_skill="arf-academic:exam-generation",
                    diagnostic="observed",
                ),
                ClaudeAdapterCaseResult(
                    case_identifier="second",
                    dispatch_status=ClaudeEvaluationStatus.SKIPPED,
                    response_contract_status=ClaudeEvaluationStatus.FAILED,
                    observed_skill=None,
                    failed_markers=("marker",),
                    matched_forbidden_patterns=("forbidden",),
                    diagnostic="failed",
                ),
            )
        )

        payload = evaluation_summary_to_dict(summary)

        self.assertEqual(
            list(payload),
            [
                "total_cases",
                "dispatch_passed",
                "dispatch_failed",
                "dispatch_skipped",
                "response_passed",
                "response_failed",
                "response_skipped",
                "fully_successful_cases",
                "results",
            ],
        )
        self.assertEqual(payload["total_cases"], 2)
        self.assertEqual(
            [result["case_identifier"] for result in payload["results"]],
            ["first", "second"],
        )
        self.assertEqual(payload["results"][0]["dispatch_status"], "passed")
        self.assertEqual(
            payload["results"][1]["response_contract_status"],
            "failed",
        )
        for result in payload["results"]:
            self.assertNotIn("response_text", result)
            self.assertNotIn("raw_stream", result)


if __name__ == "__main__":
    unittest.main()
