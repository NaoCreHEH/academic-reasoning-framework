from io import StringIO
from pathlib import Path
import contextlib
import json
import tempfile
import unittest

import scripts.analyze_claude_adapter_runs as cli


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "claude_adapter_analytics"


class ClaudeAdapterAnalyticsCliTests(unittest.TestCase):
    def test_directory_input_discovery(self):
        output, error, code = _run_cli([str(FIXTURE_DIR), "--allow-case-set-differences"])
        self.assertEqual(code, 1)
        self.assertIn("Loading 5 live run reports...", output)
        self.assertEqual(error, "")

    def test_multiple_files_text_output(self):
        output, _error, code = _run_cli(
            [
                str(FIXTURE_DIR / "usable-run.json"),
                str(FIXTURE_DIR / "degraded-run.json"),
            ]
        )
        self.assertEqual(code, 0)
        self.assertIn("Runs", output)
        self.assertIn("degraded: 1", output)

    def test_json_output_parses_and_has_no_progress_prefix(self):
        output, _error, code = _run_cli(
            [
                "--format",
                "json",
                str(FIXTURE_DIR / "usable-run.json"),
                str(FIXTURE_DIR / "degraded-run.json"),
            ]
        )
        self.assertEqual(code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["runs"]["total"], 2)

    def test_output_file_utf8_and_console_still_prints(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "analysis.txt"
            output, _error, code = _run_cli(
                [
                    str(FIXTURE_DIR / "usable-run.json"),
                    "--output",
                    str(output_path),
                ]
            )
            written = output_path.read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn("Runs", output)
        self.assertEqual(written, output.split("\n", 1)[1].rstrip("\n"))

    def test_nonexistent_path_error(self):
        _output, error, code = _run_cli(["missing.json"])
        self.assertEqual(code, 2)
        self.assertIn("input path does not exist", error)

    def test_empty_directory_error(self):
        with tempfile.TemporaryDirectory() as directory:
            _output, error, code = _run_cli([directory])
        self.assertEqual(code, 2)
        self.assertIn("no JSON reports found", error)

    def test_case_set_mismatch_exit_two(self):
        _output, error, code = _run_cli(
            [
                str(FIXTURE_DIR / "usable-run.json"),
                str(FIXTURE_DIR / "different-case-set-run.json"),
            ]
        )
        self.assertEqual(code, 2)
        self.assertIn("unexpected cases", error)

    def test_allow_differences_succeeds(self):
        _output, _error, code = _run_cli(
            [
                str(FIXTURE_DIR / "usable-run.json"),
                str(FIXTURE_DIR / "different-case-set-run.json"),
                "--allow-case-set-differences",
            ]
        )
        self.assertEqual(code, 0)

    def test_count_inconsistency_exit_one(self):
        _output, _error, code = _run_cli(
            [
                str(FIXTURE_DIR / "usable-run.json"),
                str(FIXTURE_DIR / "count-mismatch-run.json"),
            ]
        )
        self.assertEqual(code, 1)

    def test_infrastructure_failures_do_not_change_exit_code_from_zero(self):
        _output, _error, code = _run_cli([str(FIXTURE_DIR / "degraded-run.json")])
        self.assertEqual(code, 0)

    def test_output_parent_must_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing" / "analysis.txt"
            _output, error, code = _run_cli(
                [str(FIXTURE_DIR / "usable-run.json"), "--output", str(path)]
            )
        self.assertEqual(code, 2)
        self.assertIn("output parent directory does not exist", error)


def _run_cli(argv):
    stdout = StringIO()
    stderr = StringIO()
    with contextlib.redirect_stdout(stdout):
        with contextlib.redirect_stderr(stderr):
            code = cli.main(argv)
    return stdout.getvalue(), stderr.getvalue(), code


if __name__ == "__main__":
    unittest.main()
