import unittest

from benchmark.adapters.claude_code.enums import (
    ClaudeCaseArtifactRequirement,
    ClaudeEvaluationDimension,
    ClaudeEvaluationStatus,
    ResponseMarkerMatchMode,
)
from benchmark.adapters.claude_code.models import (
    ClaudeAdapterCase,
    ClaudeAdapterCaseResult,
    ClaudeAdapterEvaluationSummary,
    ClaudeAdapterEvaluationValidationError,
    ClaudeInvocationObservation,
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
        self.assertEqual(
            {member.name: member.value for member in ClaudeCaseArtifactRequirement},
            {"NONE": "none", "OPTIONAL": "optional", "REQUIRED": "required"},
        )

    def test_case_artifact_requirement_defaults_to_none(self):
        case = ClaudeAdapterCase(
            identifier="case",
            prompt="Prompt",
            expected_skill="skill",
        )
        self.assertIs(
            case.artifact_requirement,
            ClaudeCaseArtifactRequirement.NONE,
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

    def test_available_observation_may_carry_invocation_error(self):
        observation = ClaudeInvocationObservation(
            available=True,
            invocation_error="Claude live invocation timed out",
        )
        self.assertEqual(
            observation.invocation_error,
            "Claude live invocation timed out",
        )

    def test_unavailable_observation_rejects_invocation_error(self):
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ClaudeInvocationObservation(
                available=False,
                unavailable_reason="Claude CLI not found",
                invocation_error="timeout",
            )

    def test_blank_invocation_error_rejected(self):
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ClaudeInvocationObservation(
                available=True,
                invocation_error=" ",
            )

    def test_valid_plugin_loaded_true(self):
        observation = ClaudeInvocationObservation(
            available=True,
            plugin_loaded=True,
        )
        self.assertTrue(observation.plugin_loaded)

    def test_valid_plugin_loaded_false_with_load_error(self):
        observation = ClaudeInvocationObservation(
            available=True,
            plugin_loaded=False,
            plugin_load_error="failed to load",
        )
        self.assertFalse(observation.plugin_loaded)
        self.assertEqual(observation.plugin_load_error, "failed to load")

    def test_plugin_load_error_requires_plugin_loaded_false(self):
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ClaudeInvocationObservation(
                available=True,
                plugin_loaded=True,
                plugin_load_error="failed to load",
            )

    def test_non_negative_duration_accepted(self):
        observation = ClaudeInvocationObservation(
            available=True,
            duration_seconds=0.5,
        )
        self.assertEqual(observation.duration_seconds, 0.5)

    def test_negative_duration_rejected(self):
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ClaudeInvocationObservation(
                available=True,
                duration_seconds=-0.1,
            )

    def test_observed_skill_collection_preserves_repeated_invocations(self):
        observation = ClaudeInvocationObservation(
            available=True,
            observed_skills=("arf-academic:exam-generation", "arf-academic:exam-generation"),
        )
        self.assertEqual(
            observation.observed_skills,
            ("arf-academic:exam-generation", "arf-academic:exam-generation"),
        )

    def test_observed_skill_and_collection_must_match_when_both_set(self):
        with self.assertRaises(ClaudeAdapterEvaluationValidationError):
            ClaudeInvocationObservation(
                available=True,
                observed_skill="arf-academic:exam-generation",
                observed_skills=("arf-academic:python-teaching",),
            )

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
