import unittest

from benchmark.adapters.claude_code.enums import (
    ClaudeEvaluationDimension,
    ClaudeEvaluationStatus,
    ResponseMarkerMatchMode,
)
from benchmark.adapters.claude_code.models import (
    ClaudeAdapterCase,
    ClaudeAdapterCaseResult,
    ClaudeAdapterEvaluationSummary,
    ClaudeAdapterEvaluationValidationError,
    ClaudeInvocationResult,
    ResponseMarker,
)


class ClaudeAdapterEvaluationModelTests(unittest.TestCase):
    def test_exact_enum_members(self):
        self.assertEqual(
            {member.name: member.value for member in ClaudeEvaluationDimension},
            {"DISPATCH": "dispatch", "RESPONSE_CONTRACT": "response_contract"},
        )
        self.assertEqual(
            {member.name: member.value for member in ClaudeEvaluationStatus},
            {"PASSED": "passed", "FAILED": "failed", "SKIPPED": "skipped"},
        )
        self.assertEqual(
            {member.name: member.value for member in ResponseMarkerMatchMode},
            {"ANY": "any", "ALL": "all"},
        )

    def test_valid_marker_any(self):
        marker = ResponseMarker(
            identifier="valid",
            patterns=("one", "two"),
            match_mode=ResponseMarkerMatchMode.ANY,
        )
        self.assertEqual(marker.identifier, "valid")

    def test_valid_marker_all(self):
        marker = ResponseMarker(
            identifier="valid",
            patterns=("one", "two"),
            match_mode=ResponseMarkerMatchMode.ALL,
        )
        self.assertIs(marker.match_mode, ResponseMarkerMatchMode.ALL)

    def test_blank_marker_identifier_rejected(self):
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ResponseMarker("", ("one",), ResponseMarkerMatchMode.ANY)

    def test_no_marker_patterns_rejected(self):
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ResponseMarker("marker", (), ResponseMarkerMatchMode.ANY)

    def test_duplicate_marker_patterns_rejected(self):
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ResponseMarker("marker", ("one", "one"), ResponseMarkerMatchMode.ANY)

    def test_invalid_forbidden_regex_rejected(self):
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ClaudeAdapterCase(
                identifier="case",
                prompt="Prompt",
                expected_skill="skill",
                response_forbidden_regexes=("[",),
            )

    def test_expected_skill_in_forbidden_skill_list_rejected(self):
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ClaudeAdapterCase(
                identifier="case",
                prompt="Prompt",
                expected_skill="skill",
                forbidden_skills=("skill",),
            )

    def test_duplicate_marker_identifiers_rejected(self):
        marker = ResponseMarker("marker", ("one",), ResponseMarkerMatchMode.ANY)
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ClaudeAdapterCase(
                identifier="case",
                prompt="Prompt",
                expected_skill="skill",
                response_markers=(marker, marker),
            )

    def test_invocation_result_validates_types(self):
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ClaudeInvocationResult("0", "", "")  # type: ignore[arg-type]

    def test_result_success_semantics(self):
        result = ClaudeAdapterCaseResult(
            case_identifier="case",
            dispatch_status=ClaudeEvaluationStatus.SKIPPED,
            response_contract_status=ClaudeEvaluationStatus.PASSED,
            observed_skill=None,
            diagnostic="response evaluated",
        )
        self.assertTrue(result.success)

    def test_all_skipped_result_is_not_successful(self):
        result = ClaudeAdapterCaseResult(
            case_identifier="case",
            dispatch_status=ClaudeEvaluationStatus.SKIPPED,
            response_contract_status=ClaudeEvaluationStatus.SKIPPED,
            observed_skill=None,
            diagnostic="unavailable",
        )
        self.assertFalse(result.success)

    def test_summary_counts(self):
        summary = ClaudeAdapterEvaluationSummary(
            results=(
                ClaudeAdapterCaseResult(
                    "a",
                    ClaudeEvaluationStatus.PASSED,
                    ClaudeEvaluationStatus.FAILED,
                    "skill",
                    diagnostic="failed response",
                ),
                ClaudeAdapterCaseResult(
                    "b",
                    ClaudeEvaluationStatus.SKIPPED,
                    ClaudeEvaluationStatus.PASSED,
                    None,
                    diagnostic="dispatch skipped",
                ),
            )
        )
        self.assertEqual(summary.total_cases, 2)
        self.assertEqual(summary.dispatch_passed, 1)
        self.assertEqual(summary.dispatch_skipped, 1)
        self.assertEqual(summary.response_failed, 1)
        self.assertEqual(summary.fully_successful_cases, 1)


if __name__ == "__main__":
    unittest.main()
