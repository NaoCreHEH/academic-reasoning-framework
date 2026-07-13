import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_benchmarks.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class BenchmarkCliTests(unittest.TestCase):
    def test_default_cli_exits_zero(self) -> None:
        self.assertEqual(run_cli().returncode, 0)

    def test_suite_all_exits_zero(self) -> None:
        self.assertEqual(run_cli("--suite", "all").returncode, 0)

    def test_suite_routing_exits_zero(self) -> None:
        self.assertEqual(run_cli("--suite", "routing").returncode, 0)

    def test_suite_conformance_exits_zero(self) -> None:
        self.assertEqual(run_cli("--suite", "conformance").returncode, 0)

    def test_text_output_contains_suite_identifiers_and_overall(self) -> None:
        result = run_cli("--format", "text")
        self.assertIn("routing-regression", result.stdout)
        self.assertIn("structural-conformance", result.stdout)
        self.assertIn("Overall: PASSED", result.stdout)

    def test_json_output_parses_and_uses_enum_values(self) -> None:
        result = run_cli("--format", "json")
        payload = json.loads(result.stdout)
        self.assertTrue(payload["success"])
        self.assertEqual([suite["status"] for suite in payload["suites"]], ["passed", "passed"])

    def test_json_suite_order_is_stable(self) -> None:
        payload = json.loads(run_cli("--format", "json").stdout)
        self.assertEqual(
            [suite["identifier"] for suite in payload["suites"]],
            ["routing-regression", "structural-conformance"],
        )

    def test_routing_only_json_contains_one_suite(self) -> None:
        payload = json.loads(run_cli("--suite", "routing", "--format", "json").stdout)
        self.assertEqual([suite["identifier"] for suite in payload["suites"]], ["routing-regression"])

    def test_conformance_only_json_contains_one_suite(self) -> None:
        payload = json.loads(
            run_cli("--suite", "conformance", "--format", "json").stdout
        )
        self.assertEqual(
            [suite["identifier"] for suite in payload["suites"]],
            ["structural-conformance"],
        )

    def test_invalid_suite_exits_two(self) -> None:
        self.assertEqual(run_cli("--suite", "missing").returncode, 2)

    def test_invalid_format_exits_two(self) -> None:
        self.assertEqual(run_cli("--format", "xml").returncode, 2)


if __name__ == "__main__":
    unittest.main()
