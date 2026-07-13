from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.orchestration import BenchmarkRunSummary, run_benchmarks  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run ARF benchmark suites.")
    parser.add_argument(
        "--suite",
        choices=("all", "routing", "conformance"),
        default="all",
        help="Benchmark suite to run.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    args = parser.parse_args(argv)

    summary = run_benchmarks(args.suite)
    if args.format == "json":
        print(_to_json(summary))
    else:
        print(_to_text(summary))
    return 0 if summary.success else 1


def _to_text(summary: BenchmarkRunSummary) -> str:
    lines: list[str] = []
    for suite in summary.suites:
        lines.append(
            f"{suite.identifier}: {suite.status.name} ({suite.passed}/{suite.total})"
        )
        for diagnostic in suite.diagnostics:
            lines.append(f"  {diagnostic}")
    lines.append(f"Overall: {'PASSED' if summary.success else 'FAILED'}")
    return "\n".join(lines)


def _to_json(summary: BenchmarkRunSummary) -> str:
    payload = {
        "success": summary.success,
        "total_suites": summary.total_suites,
        "passed_suites": summary.passed_suites,
        "failed_suites": summary.failed_suites,
        "total_cases": summary.total_cases,
        "passed_cases": summary.passed_cases,
        "failed_cases": summary.failed_cases,
        "suites": [
            {
                "identifier": suite.identifier,
                "status": suite.status.value,
                "total": suite.total,
                "passed": suite.passed,
                "failed": suite.failed,
                "diagnostics": list(suite.diagnostics),
            }
            for suite in summary.suites
        ],
    }
    return json.dumps(payload, indent=2)


if __name__ == "__main__":
    raise SystemExit(main())
