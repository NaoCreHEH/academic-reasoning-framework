import contextlib
from io import StringIO
import json
from pathlib import Path
import tempfile
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

    timeout_seconds = None

    def __init__(self, timeout_seconds=180):
        FakeInvoker.timeout_seconds = timeout_seconds
        pass

    def invoke(self, prompt, plugin_dir):
        return self.observation


class ClaudeAdapterEvaluationCliTests(unittest.TestCase):
    def test_default_timeout_is_180(self):
        _output, _code = _run_cli(
            ["--case", "dispatch-python-mcq"],
            ClaudeInvocationObservation(
                available=False,
                unavailable_reason="Claude CLI not found",
            ),
        )
        self.assertEqual(FakeInvoker.timeout_seconds, 180)

    def test_positive_custom_timeout_accepted(self):
        _output, _code = _run_cli(
            ["--case", "dispatch-python-mcq", "--timeout", "12"],
            ClaudeInvocationObservation(
                available=False,
                unavailable_reason="Claude CLI not found",
            ),
        )
        self.assertEqual(FakeInvoker.timeout_seconds, 12)

    def test_zero_timeout_rejected(self):
        with self.assertRaises(SystemExit) as context:
            cli.main(["--timeout", "0"])
        self.assertEqual(context.exception.code, 2)

    def test_negative_timeout_rejected(self):
        with self.assertRaises(SystemExit) as context:
            cli.main(["--timeout", "-1"])
        self.assertEqual(context.exception.code, 2)

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

    def test_show_responses_prints_public_response_text(self):
        output, _code = _run_cli(
            ["--case", "response-architecture-files-not-names", "--show-responses"],
            ClaudeInvocationObservation(
                available=True,
                response_text="Public final response",
                observed_skill="arf-academic:architecture-review",
                process_result=ClaudeInvocationResult(0, "", ""),
                raw_response_available=True,
            ),
        )
        self.assertIn("  response:", output)
        self.assertIn("    Public final response", output)

    def test_responses_hidden_by_default(self):
        output, _code = _run_cli(
            ["--case", "response-architecture-files-not-names"],
            ClaudeInvocationObservation(
                available=True,
                response_text="Public final response",
                observed_skill="arf-academic:architecture-review",
                process_result=ClaudeInvocationResult(0, "", ""),
                raw_response_available=True,
            ),
        )
        self.assertNotIn("Public final response", output)

    def test_show_responses_with_json_rejected(self):
        with self.assertRaises(SystemExit) as context:
            cli.main(["--format", "json", "--show-responses"])
        self.assertEqual(context.exception.code, 2)

    def test_text_output_file_is_written_utf8_and_console_still_prints(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.txt"
            output, code = _run_cli(
                ["--case", "response-architecture-files-not-names", "--output", str(output_path)],
                ClaudeInvocationObservation(
                    available=True,
                    response_text="Cela ne prouve pas la qualite; il faut inspecter.",
                    observed_skill="arf-academic:architecture-review",
                    process_result=ClaudeInvocationResult(0, "", ""),
                ),
            )
            written = output_path.read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn("response-architecture-files-not-names", output)
        self.assertEqual(written, output.rstrip("\n"))

    def test_json_output_file_is_written_utf8_and_parses(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.json"
            output, code = _run_cli(
                [
                    "--format",
                    "json",
                    "--case",
                    "dispatch-python-mcq",
                    "--output",
                    str(output_path),
                ],
                ClaudeInvocationObservation(
                    available=False,
                    unavailable_reason="Claude CLI not found",
                ),
            )
            payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(code, 3)
        self.assertEqual(payload["total_cases"], 1)
        self.assertEqual(json.loads(output), payload)

    def test_output_parent_directory_must_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing" / "report.txt"
            with self.assertRaises(SystemExit) as context:
                cli.main(["--output", str(missing)])
        self.assertEqual(context.exception.code, 2)

    def test_json_output_file_never_contains_response_text(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.json"
            _output, code = _run_cli(
                [
                    "--format",
                    "json",
                    "--case",
                    "response-architecture-files-not-names",
                    "--output",
                    str(output_path),
                ],
                ClaudeInvocationObservation(
                    available=True,
                    response_text="Public final response",
                    observed_skill="arf-academic:architecture-review",
                    process_result=ClaudeInvocationResult(0, "", ""),
                    raw_response_available=True,
                ),
            )
            written = output_path.read_text(encoding="utf-8")
        self.assertEqual(code, 1)
        self.assertNotIn("Public final response", written)

    def test_show_responses_text_output_file_may_contain_public_response(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.txt"
            _output, code = _run_cli(
                [
                    "--case",
                    "response-architecture-files-not-names",
                    "--show-responses",
                    "--output",
                    str(output_path),
                ],
                ClaudeInvocationObservation(
                    available=True,
                    response_text="Public final response",
                    observed_skill="arf-academic:architecture-review",
                    process_result=ClaudeInvocationResult(0, "", ""),
                    raw_response_available=True,
                ),
            )
            written = output_path.read_text(encoding="utf-8")
        self.assertEqual(code, 1)
        self.assertIn("Public final response", written)

    def test_configure_utf8_diagnostics_reconfigures_stdout_and_stderr(self):
        stdout = mock.Mock()
        stderr = mock.Mock()
        with mock.patch.object(cli.sys, "stdout", stdout):
            with mock.patch.object(cli.sys, "stderr", stderr):
                cli._configure_utf8_diagnostics()
        stdout.reconfigure.assert_called_once_with(encoding="utf-8")
        stderr.reconfigure.assert_called_once_with(encoding="utf-8")

    def test_configure_utf8_diagnostics_ignores_streams_without_reconfigure(self):
        class MinimalStream:
            pass

        with mock.patch.object(cli.sys, "stdout", MinimalStream()):
            with mock.patch.object(cli.sys, "stderr", MinimalStream()):
                cli._configure_utf8_diagnostics()


def _run_cli(argv, observation):
    FakeInvoker.observation = observation
    stdout = StringIO()
    with mock.patch.object(cli, "ClaudeCliInvoker", FakeInvoker):
        with contextlib.redirect_stdout(stdout):
            code = cli.main(argv)
    return stdout.getvalue(), code


if __name__ == "__main__":
    unittest.main()
