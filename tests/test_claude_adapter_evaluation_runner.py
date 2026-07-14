from pathlib import Path
import subprocess
from unittest import mock
import unittest

from benchmark.adapters.claude_code.enums import (
    ClaudeEvaluationStatus,
    ResponseMarkerMatchMode,
)
from benchmark.adapters.claude_code.models import (
    ClaudeAdapterCase,
    ClaudeInvocationObservation,
    ClaudeInvocationResult,
    ResponseMarker,
)
from benchmark.adapters.claude_code.runner import run_claude_adapter_evaluation
from benchmark.adapters.claude_code.runner import ClaudeCliInvoker


PLUGIN_DIR = Path("implementations/claude-code/arf-academic")


class FakeInvoker:
    def __init__(self, observation):
        self.observation = observation

    def invoke(self, prompt, plugin_dir):
        return self.observation


class RaisingInvoker:
    def __init__(self, error):
        self.error = error

    def invoke(self, prompt, plugin_dir):
        raise self.error


class ClaudeAdapterEvaluationRunnerTests(unittest.TestCase):
    def test_expected_observed_skill_passes(self):
        result = _run(
            _case(),
            _observation(observed_skill="expected", response_text="ok"),
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.PASSED)

    def test_expected_sole_observed_skill_from_collection_passes(self):
        result = _run(
            _case(expected_skill="arf-academic:exam-generation"),
            _observation(
                observed_skills=("arf-academic:exam-generation",),
                response_text="ok",
            ),
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.PASSED)
        self.assertEqual(result.observed_skill, "arf-academic:exam-generation")

    def test_wrong_observed_skill_fails(self):
        result = _run(
            _case(),
            _observation(observed_skill="other", response_text="ok"),
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.FAILED)

    def test_forbidden_observed_skill_fails(self):
        result = _run(
            _case(forbidden_skills=("forbidden",)),
            _observation(observed_skill="forbidden", response_text="ok"),
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.FAILED)

    def test_expected_plus_another_arf_skill_fails_exclusivity(self):
        result = _run(
            _case(expected_skill="arf-academic:exam-generation"),
            _observation(
                observed_skills=(
                    "arf-academic:exam-generation",
                    "arf-academic:python-teaching",
                ),
                response_text="ok",
            ),
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.FAILED)
        self.assertIn("exclusive dispatch", result.diagnostic)

    def test_unobservable_skill_identity_is_skipped_not_passed(self):
        result = _run(_case(), _observation(response_text="ok"))
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.SKIPPED)
        self.assertIn("not observable", result.diagnostic)

    def test_explicit_plugin_load_failure_fails_both_dimensions(self):
        result = _run(
            _case(),
            _observation(
                plugin_loaded=False,
                plugin_load_error="failed to load",
            ),
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.FAILED)
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.FAILED,
        )
        self.assertIn("ARF plugin failed to load", result.diagnostic)

    def test_unknown_plugin_state_does_not_become_plugin_success(self):
        result = _run(
            _case(expected_skill="arf-academic:exam-generation"),
            _observation(
                observed_skills=("arf-academic:exam-generation",),
                plugin_loaded=None,
            ),
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.PASSED)
        self.assertNotIn("plugin loaded", result.diagnostic)

    def test_unavailable_invocation_skips_both_dimensions(self):
        result = _run(
            _case(),
            ClaudeInvocationObservation(
                available=False,
                unavailable_reason="Claude CLI not found",
            ),
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.SKIPPED)
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.SKIPPED,
        )
        self.assertIn("Claude CLI not found", result.diagnostic)

    def test_type_error_from_invoker_propagates(self):
        with self.assertRaises(TypeError):
            run_claude_adapter_evaluation(
                cases=(_case(),),
                invoker=RaisingInvoker(TypeError("bug")),
                plugin_dir=PLUGIN_DIR,
            )

    def test_value_error_from_invoker_propagates(self):
        with self.assertRaises(ValueError):
            run_claude_adapter_evaluation(
                cases=(_case(),),
                invoker=RaisingInvoker(ValueError("bug")),
                plugin_dir=PLUGIN_DIR,
            )

    def test_unexpected_exceptions_are_not_converted_to_skipped(self):
        with self.assertRaises(RuntimeError):
            run_claude_adapter_evaluation(
                cases=(_case(),),
                invoker=RaisingInvoker(RuntimeError("unexpected")),
                plugin_dir=PLUGIN_DIR,
            )

    def test_failed_process_does_not_become_skipped(self):
        result = _run(
            _case(),
            _observation(
                response_text="",
                process_result=ClaudeInvocationResult(1, "", "error"),
            ),
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.FAILED)
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.FAILED,
        )

    def test_invocation_error_fails_both_dimensions(self):
        result = _run(
            _case(),
            ClaudeInvocationObservation(
                available=True,
                invocation_error="Claude live invocation timed out",
            ),
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.FAILED)
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.FAILED,
        )
        self.assertIn("timed out", result.diagnostic)

    def test_any_marker_passes_on_one_pattern(self):
        case = _case(
            response_markers=(
                ResponseMarker("marker", ("missing", "present"), ResponseMarkerMatchMode.ANY),
            )
        )
        result = _run(case, _observation(response_text="this is present"))
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.PASSED,
        )

    def test_public_response_markers_operate_on_reconstructed_answer(self):
        case = _case(
            response_markers=(
                ResponseMarker("marker", ("final answer",), ResponseMarkerMatchMode.ANY),
            )
        )
        result = _run(case, _observation(response_text="final answer"))
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.PASSED,
        )

    def test_tool_input_marker_text_cannot_create_false_response_pass(self):
        case = _case(
            response_markers=(
                ResponseMarker("marker", ("tool-only",), ResponseMarkerMatchMode.ANY),
            )
        )
        result = _run(case, _observation(response_text="final answer"))
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.FAILED,
        )
        self.assertEqual(result.failed_markers, ("marker",))

    def test_malformed_stream_parse_failure_becomes_failed(self):
        result = _run(
            _case(),
            _observation(invocation_error="Claude stream parsing failed: line 2"),
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.FAILED)
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.FAILED,
        )

    def test_any_marker_fails_with_no_patterns(self):
        case = _case(
            response_markers=(
                ResponseMarker("marker", ("missing",), ResponseMarkerMatchMode.ANY),
            )
        )
        result = _run(case, _observation(response_text="other text"))
        self.assertEqual(result.failed_markers, ("marker",))

    def test_all_marker_requires_all_patterns(self):
        case = _case(
            response_markers=(
                ResponseMarker("marker", ("one", "two"), ResponseMarkerMatchMode.ALL),
            )
        )
        result = _run(case, _observation(response_text="one only"))
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.FAILED,
        )

    def test_matching_is_case_insensitive(self):
        case = _case(
            response_markers=(
                ResponseMarker("marker", ("present",), ResponseMarkerMatchMode.ANY),
            )
        )
        result = _run(case, _observation(response_text="PRESENT"))
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.PASSED,
        )

    def test_literal_forbidden_pattern_fails(self):
        result = _run(
            _case(response_forbidden_patterns=("bad idea",)),
            _observation(response_text="This is a BAD idea."),
        )
        self.assertEqual(result.matched_forbidden_patterns, ("bad idea",))

    def test_regex_forbidden_pattern_fails(self):
        result = _run(
            _case(response_forbidden_regexes=(r"\b\d{2}% confiance\b",)),
            _observation(response_text="Je donne 80% confiance."),
        )
        self.assertEqual(result.matched_forbidden_patterns, (r"\b\d{2}% confiance\b",))

    def test_stderr_is_not_evaluated_as_response_text(self):
        case = _case(
            response_markers=(
                ResponseMarker("marker", ("only stderr",), ResponseMarkerMatchMode.ANY),
            )
        )
        result = _run(
            case,
            _observation(
                response_text="stdout",
                process_result=ClaudeInvocationResult(0, "stdout", "only stderr"),
            ),
        )
        self.assertEqual(result.failed_markers, ("marker",))

    def test_full_response_is_not_stored_in_result(self):
        text = "long private output marker"
        result = _run(_case(), _observation(response_text=text))
        self.assertNotIn(text, result.diagnostic)

    def test_marker_diagnostics_identify_failed_marker_ids(self):
        case = _case(
            response_markers=(
                ResponseMarker("marker", ("missing",), ResponseMarkerMatchMode.ANY),
            )
        )
        result = _run(case, _observation(response_text="text"))
        self.assertIn("marker", result.diagnostic)

    def test_response_contract_without_checks_is_skipped(self):
        result = _run(_case(), _observation(response_text="text"))
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.SKIPPED,
        )

    def test_cli_help_timeout_produces_unavailable_observation(self):
        with mock.patch(
            "benchmark.adapters.claude_code.runner.shutil.which",
            return_value="claude",
        ):
            with mock.patch(
                "benchmark.adapters.claude_code.runner.subprocess.run",
                side_effect=subprocess.TimeoutExpired(["claude", "--help"], 1),
            ):
                observation = ClaudeCliInvoker(timeout_seconds=1).invoke(
                    "Prompt",
                    PLUGIN_DIR,
                )
        self.assertFalse(observation.available)
        self.assertEqual(
            observation.unavailable_reason,
            "Claude CLI help inspection timed out",
        )

    def test_actual_invocation_timeout_becomes_failed_observation(self):
        help_result = subprocess.CompletedProcess(
            ["claude", "--help"],
            0,
            stdout="--plugin-dir --print",
            stderr="",
        )
        with mock.patch(
            "benchmark.adapters.claude_code.runner.shutil.which",
            return_value="claude",
        ):
            with mock.patch(
                "benchmark.adapters.claude_code.runner.subprocess.run",
                side_effect=[
                    help_result,
                    subprocess.TimeoutExpired(["claude", "--print"], 1),
                ],
            ):
                observation = ClaudeCliInvoker(timeout_seconds=1).invoke(
                    "Prompt",
                    PLUGIN_DIR,
                )
        result = _run(_case(), observation)
        self.assertTrue(observation.available)
        self.assertTrue(
            observation.invocation_error.startswith("Claude live invocation timed out")
        )
        self.assertIs(result.dispatch_status, ClaudeEvaluationStatus.FAILED)
        self.assertIs(
            result.response_contract_status,
            ClaudeEvaluationStatus.FAILED,
        )


def _case(**overrides):
    values = {
        "identifier": "case",
        "prompt": "Prompt",
        "expected_skill": "expected",
    }
    values.update(overrides)
    return ClaudeAdapterCase(**values)


def _observation(
    response_text="",
    observed_skill=None,
    observed_skills=(),
    process_result=None,
    plugin_loaded=None,
    plugin_load_error=None,
    invocation_error=None,
):
    return ClaudeInvocationObservation(
        available=True,
        response_text=response_text,
        observed_skill=observed_skill,
        observed_skills=observed_skills,
        process_result=process_result or ClaudeInvocationResult(0, response_text, ""),
        dispatch_observation_reason="skill identity not observable",
        plugin_loaded=plugin_loaded,
        plugin_load_error=plugin_load_error,
        invocation_error=invocation_error,
        raw_response_available=response_text is not None,
    )


def _run(case, observation):
    summary = run_claude_adapter_evaluation(
        cases=(case,),
        invoker=FakeInvoker(observation),
        plugin_dir=PLUGIN_DIR,
    )
    return summary.results[0]


if __name__ == "__main__":
    unittest.main()
