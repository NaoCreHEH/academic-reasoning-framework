import contextlib
from io import StringIO
import json
from unittest import mock
import unittest

import scripts.run_claude_adapter_evaluation as cli
from benchmark.adapters.claude_code.models import (
    ClaudeInvocationObservation,
    ClaudeInvocationResult,
)


class FakeInvoker:
    observation = ClaudeInvocationObservation(
        available=False,
        unavailable_reason="not configured",
    )

    def __init__(self):
        pass

    def invoke(self, prompt, plugin_dir):
        return self.observation


class ClaudeAdapterEvaluationCliTests(unittest.TestCase):
    def test_json_parses(self):
        output, code = _run_cli(
            ["--format", "json", "--case", "dispatch-python-mcq"],
            ClaudeInvocationObservation(
                available=False,
                unavailable_reason="Claude CLI not found",
            ),
        )
        self.assertEqual(code, 3)
        payload = json.loads(output)
        self.assertEqual(payload["total_cases"], 1)

    def test_all_skipped_exit_code_is_three(self):
        _output, code = _run_cli(
            ["--case", "dispatch-python-mcq"],
            ClaudeInvocationObservation(
                available=False,
                unavailable_reason="Claude CLI not found",
            ),
        )
        self.assertEqual(code, 3)

    def test_failed_dimension_exit_code_is_one(self):
        _output, code = _run_cli(
            ["--case", "dispatch-python-mcq"],
            ClaudeInvocationObservation(
                available=True,
                response_text="",
                observed_skill="wrong",
                process_result=ClaudeInvocationResult(0, "", ""),
            ),
        )
        self.assertEqual(code, 1)

    def test_successful_evaluated_dimensions_exit_code_is_zero(self):
        _output, code = _run_cli(
            ["--case", "response-architecture-files-not-names"],
            ClaudeInvocationObservation(
                available=True,
                response_text="Cela ne prouve pas la qualite; il faut inspecter.",
                observed_skill="arf-academic:architecture-review",
                process_result=ClaudeInvocationResult(0, "ok", ""),
            ),
        )
        self.assertEqual(code, 0)

    def test_invalid_case_exits_two(self):
        with self.assertRaises(SystemExit) as context:
            cli.main(["--case", "missing"])
        self.assertEqual(context.exception.code, 2)

    def test_invalid_tag_exits_two(self):
        with self.assertRaises(SystemExit) as context:
            cli.main(["--tag", "missing"])
        self.assertEqual(context.exception.code, 2)

    def test_case_filtering(self):
        output, _code = _run_cli(
            ["--case", "dispatch-python-mcq"],
            ClaudeInvocationObservation(
                available=False,
                unavailable_reason="Claude CLI not found",
            ),
        )
        self.assertIn("dispatch-python-mcq", output)
        self.assertNotIn("dispatch-python-submission", output)

    def test_tag_filtering(self):
        output, _code = _run_cli(
            ["--tag", "misspelling"],
            ClaudeInvocationObservation(
                available=False,
                unavailable_reason="Claude CLI not found",
            ),
        )
        self.assertIn("dispatch-misspelled-qcm", output)
        self.assertNotIn("dispatch-python-mcq", output)

    def test_text_output_uses_skipped_honestly(self):
        output, _code = _run_cli(
            ["--case", "dispatch-python-mcq"],
            ClaudeInvocationObservation(
                available=True,
                response_text="response",
                observed_skill=None,
                process_result=ClaudeInvocationResult(0, "response", ""),
                dispatch_observation_reason="skill identity not observable",
            ),
        )
        self.assertIn("dispatch: SKIPPED", output)
        self.assertIn("skill identity not observable", output)

    def test_unavailable_text_reports_unavailable_reason(self):
        output, _code = _run_cli(
            ["--case", "dispatch-python-mcq"],
            ClaudeInvocationObservation(
                available=False,
                unavailable_reason="Claude CLI not found",
            ),
        )
        self.assertIn("dispatch: SKIPPED", output)
        self.assertIn("Claude CLI not found", output)


def _run_cli(argv, observation):
    FakeInvoker.observation = observation
    stdout = StringIO()
    with mock.patch.object(cli, "ClaudeCliInvoker", FakeInvoker):
        with contextlib.redirect_stdout(stdout):
            code = cli.main(argv)
    return stdout.getvalue(), code


if __name__ == "__main__":
    unittest.main()
