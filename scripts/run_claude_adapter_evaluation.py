from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.adapters.claude_code import (  # noqa: E402
    CLAUDE_ADAPTER_CASES,
    ClaudeAdapterCase,
    ClaudeAdapterEvaluationSummary,
    ClaudeCliInvoker,
    run_claude_adapter_evaluation,
)


PLUGIN_DIR = ROOT / "implementations" / "claude-code" / "arf-academic"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run live Claude Code adapter evaluation cases."
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--show-responses",
        action="store_true",
        help="Print public model responses in text output for local diagnostics.",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_int,
        default=180,
        help="Per-case Claude invocation timeout in seconds.",
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--case", help="Run one built-in case identifier.")
    selection.add_argument("--tag", help="Run built-in cases containing a tag.")
    args = parser.parse_args(argv)
    if args.show_responses and args.format == "json":
        parser.error("--show-responses is only supported with --format text")

    try:
        cases = _select_cases(args.case, args.tag)
    except ValueError as error:
        parser.error(str(error))

    response_texts: dict[str, str] = {}

    def remember_response(case, observation) -> None:
        if observation.raw_response_available and observation.response_text is not None:
            response_texts[case.identifier] = observation.response_text

    summary = run_claude_adapter_evaluation(
        cases=cases,
        invoker=ClaudeCliInvoker(timeout_seconds=args.timeout),
        plugin_dir=PLUGIN_DIR,
        on_observation=remember_response if args.show_responses else None,
    )

    if args.format == "json":
        print(_to_json(summary))
    else:
        print(_to_text(summary, response_texts if args.show_responses else None))

    if summary.any_failed:
        return 1
    if summary.all_skipped:
        return 3
    return 0


def _select_cases(
    case_identifier: str | None,
    tag: str | None,
) -> tuple[ClaudeAdapterCase, ...]:
    if case_identifier is not None:
        matches = tuple(
            case for case in CLAUDE_ADAPTER_CASES if case.identifier == case_identifier
        )
        if not matches:
            raise ValueError(f"unknown case: {case_identifier}")
        return matches
    if tag is not None:
        matches = tuple(case for case in CLAUDE_ADAPTER_CASES if tag in case.tags)
        if not matches:
            raise ValueError(f"unknown tag: {tag}")
        return matches
    return CLAUDE_ADAPTER_CASES


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be a positive integer") from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError("timeout must be a positive integer")
    return parsed


def _to_text(
    summary: ClaudeAdapterEvaluationSummary,
    response_texts: dict[str, str] | None = None,
) -> str:
    lines: list[str] = []
    for result in summary.results:
        lines.append(result.case_identifier)
        if result.observed_skill is not None:
            dispatch_detail = f" - {result.observed_skill}"
        elif result.dispatch_status.name == "SKIPPED":
            dispatch_detail = f" - {result.diagnostic}"
        else:
            dispatch_detail = ""
        lines.append(
            f"  dispatch: {result.dispatch_status.name}{dispatch_detail}"
        )
        lines.append(
            f"  response_contract: {result.response_contract_status.name}"
        )
        lines.append(f"  diagnostic: {result.diagnostic}")
        if response_texts is not None and result.case_identifier in response_texts:
            lines.append("  response:")
            lines.extend(
                f"    {line}" for line in response_texts[result.case_identifier].splitlines()
            )
    lines.append(
        "Totals: "
        f"cases={summary.total_cases}; "
        f"dispatch passed/failed/skipped="
        f"{summary.dispatch_passed}/{summary.dispatch_failed}/"
        f"{summary.dispatch_skipped}; "
        f"response passed/failed/skipped="
        f"{summary.response_passed}/{summary.response_failed}/"
        f"{summary.response_skipped}; "
        f"fully successful cases={summary.fully_successful_cases}"
    )
    return "\n".join(lines)


def _to_json(summary: ClaudeAdapterEvaluationSummary) -> str:
    payload = {
        "total_cases": summary.total_cases,
        "dispatch_passed": summary.dispatch_passed,
        "dispatch_failed": summary.dispatch_failed,
        "dispatch_skipped": summary.dispatch_skipped,
        "response_passed": summary.response_passed,
        "response_failed": summary.response_failed,
        "response_skipped": summary.response_skipped,
        "fully_successful_cases": summary.fully_successful_cases,
        "results": [
            {
                "case_identifier": result.case_identifier,
                "dispatch_status": result.dispatch_status.value,
                "response_contract_status": result.response_contract_status.value,
                "observed_skill": result.observed_skill,
                "failed_markers": list(result.failed_markers),
                "matched_forbidden_patterns": list(
                    result.matched_forbidden_patterns
                ),
                "diagnostic": result.diagnostic,
            }
            for result in summary.results
        ],
    }
    return json.dumps(payload, indent=2)


if __name__ == "__main__":
    raise SystemExit(main())
